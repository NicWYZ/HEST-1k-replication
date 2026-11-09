"""Round 10, track final-runs, stage F1.4c: held-out prediction files for a corpus task.

Every spot of the task is predicted once, by a head fitted on the other units only: leave-one-donor-out over the
audited donor labels (design `donor`), or leave-one-center-out (design `center`). The head is round 3's
`fit_base` (code/scripts/round3_a0_harness.py, round 2 R1b's intercept_f64: StandardScaler -> PCA(256,
random_state=1) -> Cholesky ridge with intercept at alpha = 100/(256 n_genes), float64 from the raw embeddings),
imported and called unchanged. The scaler and PCA do not see the outcome, so one pipeline per fold serves both scales,
and one ridge is fitted per scale:
  log1p   log(1 + y), y the raw count;
  lognorm log(1 + 1e4 y / n), n the spot's total count over its full measured panel (the corpus's `lognorm`).
Inputs follow the corpus layout (NicWYZ/ST-Fed-Learn, docs/round01/tracks/data/data_card.md): the task JSON's
samples with their expr_path (.h5ad, raw counts, var['ensembl_id']) and emb_paths[encoder] (.h5, `embeddings`,
`barcodes`). The donor map is a CSV (sample_id, donor_id) of audited labels; every task sample must be in it.
Output: <out>/pred__<task>__<encoder>__<design>.parquet with an explicit schema (sample_id, barcode, donor_id,
center_id, fold, lib_size, n_detected, then y_log1p__<g>, f_log1p__<g>, y_lognorm__<g>, f_lognorm__<g> per gene),
written after the summary <out>/pred_summary__<task>__<encoder>__<design>.json (spots, folds, per-gene spot-level
Pearson over all held-out spots per scale, seconds per fold).
Usage: round10_final_runs_f1_predict.py <task.json> <encoder> <donor|center> <donor_map.csv> <outdir> [--max-folds k]
       [--samples id,id,... --tag NAME]   (the CCRCC anchor runs on the kidney task's INT1 to INT24)
n_detected is the number of stored nonzero entries of the spot's row over its full panel.
"""
import argparse, json, os, sys, time
import anndata as ad, h5py, numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq, scipy.sparse as sp
import round3_a0_harness as H
from sklearn.linear_model import Ridge


def load_sample(s, encoder, genes):
    A = ad.read_h5ad(s['expr_path'])
    X = A.X.tocsr() if sp.issparse(A.X) else sp.csr_matrix(A.X)
    lib = np.asarray(X.sum(1)).ravel(); ndet = np.diff(X.indptr) if sp.issparse(X) else (X > 0).sum(1)
    idx = pd.Index(A.var['ensembl_id'].astype(str))
    gi = idx.get_indexer(genes)
    assert (gi >= 0).all(), f"{s['sample_id']}: {(gi < 0).sum()} task genes not measured"
    with h5py.File(s['emb_paths'][encoder], 'r') as f:
        E = f['embeddings'][:]
        b = [x.decode() if isinstance(x, bytes) else str(x) for x in np.asarray(f['barcodes'][:]).ravel()]
    pos = A.obs_names.get_indexer(b); keep = pos >= 0
    Y = np.asarray(X[pos[keep]][:, gi].todense(), dtype=np.float64)
    return E[keep], Y, np.array(b)[keep], lib[pos[keep]], np.asarray(ndet)[pos[keep]]


def pearson(a, b):
    a = a - a.mean(); b = b - b.mean(); d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else float('nan')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('task'); ap.add_argument('encoder'); ap.add_argument('design', choices=['donor', 'center'])
    ap.add_argument('donor_map'); ap.add_argument('out'); ap.add_argument('--max-folds', type=int, default=0)
    ap.add_argument('--samples', default='', help='comma-separated sample ids to keep (the anchor subset)')
    ap.add_argument('--map-task', default='', help='keep only rows of the donor map whose task column equals this')
    ap.add_argument('--genes-from-parquet', default='', help='use the genes of this file (columns y__<symbol>), mapped to Ensembl ids through the first sample')
    ap.add_argument('--chunk', default='', help='i/k: run only the i-th of k contiguous slices of the sorted held-out units (0-based)')
    ap.add_argument('--tag', default='', help='name used in the output files instead of the task name')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    T = json.load(open(a.task)); genes = [str(g) for g in T['genes_top50']]
    if a.samples:
        ks = set(a.samples.split(',')); T['samples'] = [s for s in T['samples'] if s['sample_id'] in ks]
        assert len(T['samples']) == len(ks), 'unknown sample ids in --samples'
    name = a.tag or T['name']
    gene_symbols = None
    if a.genes_from_parquet:
        syms = [n[3:] for n in pq.read_schema(a.genes_from_parquet).names if n.startswith('y__')]
        A0 = ad.read_h5ad(T['samples'][0]['expr_path'], backed='r')
        cands = [('var_names', pd.Index(A0.var_names.astype(str)))]
        cands += [(k, pd.Index(A0.var[k].astype(str))) for k in A0.var.columns if A0.var[k].dtype == object or str(A0.var[k].dtype) == 'category']
        best = max(cands, key=lambda kv: kv[1].isin(syms).sum())
        ens = pd.Index(A0.var['ensembl_id'].astype(str))
        m = {s_: ens[best[1].get_loc(s_)] for s_ in syms if s_ in best[1] and best[1].get_loc(s_) is not None and isinstance(best[1].get_loc(s_), (int, np.integer))}
        print(f'genes from {a.genes_from_parquet}: {len(syms)} symbols, {len(m)} mapped through var column {best[0]}', flush=True)
        gene_symbols = [s_ for s_ in syms if s_ in m]; genes = [m[s_] for s_ in gene_symbols]
    dmf = pd.read_csv(a.donor_map, dtype=str)
    if a.map_task:
        dmf = dmf[dmf['task'] == a.map_task]
    dm = dmf.drop_duplicates('sample_id').set_index('sample_id')['donor_id']
    miss = [s['sample_id'] for s in T['samples'] if s['sample_id'] not in dm.index]
    assert not miss, f'samples without an audited donor label: {miss}'
    parts = []
    for s in T['samples']:
        E, Y, b, lib, nd = load_sample(s, a.encoder, genes)
        parts.append((s['sample_id'], s['center_id'], dm[s['sample_id']], E, Y, b, lib, nd))
    E = np.concatenate([p[3] for p in parts]); Y = np.concatenate([p[4] for p in parts])
    lib = np.concatenate([p[6] for p in parts]).astype(np.float64); nd = np.concatenate([p[7] for p in parts]).astype(np.int64)
    sid = np.concatenate([[p[0]] * len(p[5]) for p in parts]); cen = np.concatenate([[p[1]] * len(p[5]) for p in parts])
    don = np.concatenate([[p[2]] * len(p[5]) for p in parts]); bc = np.concatenate([p[5] for p in parts])
    targets = {'log1p': np.log1p(Y), 'lognorm': np.log1p(1e4 * Y / np.maximum(lib, 1)[:, None])}
    unit = don if a.design == 'donor' else cen
    units = sorted(set(unit))
    if a.max_folds:
        units = units[:a.max_folds]
    part = ''
    if a.chunk:
        i, k = (int(x) for x in a.chunk.split('/'))
        units = [list(x) for x in np.array_split(np.array(units, dtype=object), k)][i]
        part = f'__part{i}of{k}'
    F = {k: np.full_like(v, np.nan) for k, v in targets.items()}
    fold = np.full(len(unit), '', dtype=object); secs = []
    for u in units:
        t0 = time.time(); te = unit == u; tr = ~te
        assert not (set(don[te]) & set(don[tr])), f'donor {u} on both sides'
        pipe, A_tr, reg, alpha = H.fit_base(E[tr], targets['log1p'][tr])
        A_te = pipe.transform(E[te].astype(np.float64, copy=False))
        F['log1p'][te] = reg.predict(A_te)
        reg2 = Ridge(alpha=alpha, random_state=0, fit_intercept=True, solver='cholesky').fit(A_tr, targets['lognorm'][tr])
        F['lognorm'][te] = reg2.predict(A_te)
        fold[te] = str(u); secs.append(time.time() - t0)
        print(f'fold {u}: train {tr.sum()} test {te.sum()} {secs[-1]:.1f}s', flush=True)
    done = fold != ''
    summ = dict(task=name, samples_filter=a.samples, chunk=a.chunk, units=[str(u) for u in units], encoder=a.encoder, design=a.design, spots=int(len(unit)), spots_predicted=int(done.sum()),
                samples=len(parts), donors=len(set(don)), centers=len(set(cen)), folds=len(units),
                alpha=float(alpha), n_genes=len(genes), seconds_per_fold=float(np.mean(secs)),
                gene_symbols=gene_symbols, pearson={k: {g: pearson(targets[k][done, j], F[k][done, j]) for j, g in enumerate(genes)} for k in targets})
    for k in targets:
        summ[f'median_pearson_{k}'] = float(np.nanmedian(list(summ['pearson'][k].values())))
    tag = f"{name}__{a.encoder}__{a.design}{part}"
    json.dump(summ, open(os.path.join(a.out, f'pred_summary__{tag}.json'), 'w'), indent=1)
    fields = [pa.field(n, pa.string()) for n in ('sample_id', 'barcode', 'donor_id', 'center_id', 'fold')]
    fields += [pa.field('lib_size', pa.float64()), pa.field('n_detected', pa.int64())]
    cols = dict(sample_id=sid[done].astype(str), barcode=bc[done].astype(str), donor_id=don[done].astype(str),
                center_id=cen[done].astype(str), fold=fold[done].astype(str), lib_size=lib[done], n_detected=nd[done])
    for k in targets:
        for j, g in enumerate(genes):
            for pre, M in (('y', targets[k]), ('f', F[k])):
                n = f'{pre}_{k}__{g}'; fields.append(pa.field(n, pa.float64())); cols[n] = M[done, j]
    schema = pa.schema(fields)
    pq.write_table(pa.Table.from_pydict(cols, schema=schema), os.path.join(a.out, f'pred__{tag}.parquet'))
    print(json.dumps({k: v for k, v in summ.items() if k != 'pearson'}, indent=1))


if __name__ == '__main__':
    main()
