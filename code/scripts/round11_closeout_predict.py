"""Round 11, track closeout, Part A: held-out prediction files from frozen embeddings, for several predictors.

Every spot of the task is predicted once by a head fitted on the other units only: leave-one-donor-out over the
audited donor labels (design `donor`) or leave-one-center-out (design `center`), as round 10's
round10_final_runs_f1_predict.py does, with the same inputs (corpus task JSON, donor map, genes_top50 or the genes of a
HEST prediction file), the same scales and the same output columns, so round 10's downstream scripts read the files
unchanged. An arm is (encoders, context, head):

  encoders  one or more corpus encoders (uni_v2, hoptimus0, resnet50, virchow2, phikon_v2), concatenated per spot
            after aligning barcodes (spots present in every encoder's file).
  context   none   the spot's own embedding;
            ring1  the spot's embedding concatenated with the mean embedding of its neighbours in the same sample,
                   the patches whose centres lie within 1.5 times the sample's median nearest-neighbour distance (the
                   6 hexagonal neighbours on Visium, the 8 grid neighbours on Xenium pseudo-spots). All patches of the
                   sample's embedding file count as neighbours, whether or not they carry expression; a patch with no
                   neighbour uses its own embedding. No outcome enters.
  head      r10      round 10's head, round3_a0_harness.fit_base imported unchanged (StandardScaler, PCA 256 with
                     random_state 1, Cholesky ridge at alpha = 100/(256 n_genes), float64), one ridge per scale on the
                     same PCA features, exactly as round 10's predict script;
            ridgecv  ridge on the standardised features without PCA, with an intercept, the penalty chosen per gene and
                     scale by inner cross-validation inside the outer training fold. Inner folds group the training
                     units: for the donor design the training donors are dealt into 5 folds in order of
                     zlib.crc32(donor id); for the center design each training center is an inner fold. The standardisation
                     uses the moments of the data the fit sees (the inner training part, or the outer training fold).
                     Grid: alpha = n_fit * 10^k, k in {-6, -5.5, ..., 1} (15 values), n_fit the number of fitted spots;
                     the alpha with the smallest summed inner held-out squared error is refitted on the outer training
                     fold. Implemented from per-unit sufficient statistics (sum x, sum x x', sum x y', sum y, n) and an
                     eigendecomposition of each fitting set's standardised centred Gram matrix, which is exact ridge.
Output: <out>/pred__<tag>.parquet in round 10's layout (sample_id, barcode, donor_id, center_id, fold, lib_size,
n_detected, y_<scale>__<gene>, f_<scale>__<gene>), written after <out>/pred_summary__<tag>.json (per-gene pooled
Pearson per scale as round 10 computes it, per-fold medians over genes, chosen alphas, timings), and
<out>/pred_folds__<tag>.csv (per fold, scale and gene: Pearson over the fold's spots, n).
Usage: round11_closeout_predict.py <task.json> <donor_map.csv> <donor|center> <outdir> --arm ENC[+ENC..]:CONTEXT:HEAD
       [--samples ids] [--map-task T] [--genes-from-parquet p] [--only-mapped] [--group-centers-by-donor] [--tag NAME]
"""
import argparse, json, os, sys, time, zlib
import anndata as ad, h5py, numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq, scipy.sparse as sp
from scipy.spatial import cKDTree
from sklearn.linear_model import Ridge
import round3_a0_harness as H

KGRID = np.arange(-6.0, 1.01, 0.5)
NINNER_DONOR = 5


def pearson(a, b):
    a = a - a.mean(); b = b - b.mean(); d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else float('nan')


def read_emb(path):
    with h5py.File(path, 'r') as f:
        E = f['embeddings'][:]
        b = [x.decode() if isinstance(x, bytes) else str(x) for x in np.asarray(f['barcodes'][:]).ravel()]
        xy = np.asarray(f['coords'][:], dtype=np.float64) if 'coords' in f else None
    return np.asarray(E, dtype=np.float64), np.array(b, dtype=object), xy


def ring_mean(E, xy):
    """Mean embedding of each patch's neighbours within 1.5 x the median nearest-neighbour distance (self excluded)."""
    tree = cKDTree(xy)
    d, _ = tree.query(xy, k=2)
    r = 1.5 * float(np.median(d[:, 1]))
    nb = tree.query_ball_point(xy, r)
    M = np.empty_like(E); nn = np.zeros(len(E), dtype=np.int64)
    for i, lst in enumerate(nb):
        lst = [j for j in lst if j != i]
        nn[i] = len(lst)
        M[i] = E[lst].mean(0) if lst else E[i]
    return M, nn, r


def load_sample(s, encoders, context, genes):
    A = ad.read_h5ad(s['expr_path'])
    X = A.X.tocsr() if sp.issparse(A.X) else sp.csr_matrix(A.X)
    lib = np.asarray(X.sum(1)).ravel(); ndet = np.diff(X.indptr)
    gi = pd.Index(A.var['ensembl_id'].astype(str)).get_indexer(genes)
    assert (gi >= 0).all(), f"{s['sample_id']}: {(gi < 0).sum()} task genes not measured"
    feats, bc0, nn_stats = [], None, []
    embs = []
    for enc in encoders:
        E, b, xy = read_emb(s['emb_paths'][enc])
        embs.append((E, b, xy))
    common = set(embs[0][1].tolist())
    for _, b, _ in embs[1:]:
        common &= set(b.tolist())
    for E, b, xy in embs:
        keep = np.array([x in common for x in b])
        E, b2, xy2 = E[keep], b[keep], (xy[keep] if xy is not None else None)
        if len(embs) > 1:   # align encoders by barcode; one encoder keeps the file's order, as round 10's loader
            order = np.argsort(b2, kind='stable'); E, b2 = E[order], b2[order]; xy2 = xy2[order] if xy2 is not None else None
        if bc0 is None:
            bc0 = b2
        assert (b2 == bc0).all()
        if context == 'ring1':
            assert xy2 is not None, f"{s['sample_id']}: no coords for context"
            M, nn, r = ring_mean(E, xy2); nn_stats.append((float(np.median(nn)), float((nn == 0).mean()), r))
            feats.append(np.hstack([E, M]))
        else:
            feats.append(E)
    F = np.hstack(feats)
    pos = A.obs_names.get_indexer(bc0); keep = pos >= 0
    Y = np.asarray(X[pos[keep]][:, gi].todense(), dtype=np.float64)
    return F[keep], Y, bc0[keep], lib[pos[keep]], np.asarray(ndet)[pos[keep]], nn_stats


class Suff:
    """Per-unit sufficient statistics for ridge with intercept on standardised features."""
    def __init__(self, X, T, unit):
        self.units = sorted(set(unit.tolist()))
        self.S = {}
        for u in self.units:
            m = unit == u; Xu = X[m]
            self.S[u] = dict(n=int(m.sum()), sx=Xu.sum(0), sxx=Xu.T @ Xu,
                             sy={k: v[m].sum(0) for k, v in T.items()}, sxy={k: Xu.T @ v[m] for k, v in T.items()},
                             syy={k: (v[m] ** 2).sum(0) for k, v in T.items()})

    def pool(self, us):
        n = sum(self.S[u]['n'] for u in us)
        sx = sum(self.S[u]['sx'] for u in us); sxx = sum(self.S[u]['sxx'] for u in us)
        keys = self.S[us[0]]['sy'].keys()
        sy = {k: sum(self.S[u]['sy'][k] for u in us) for k in keys}
        sxy = {k: sum(self.S[u]['sxy'][k] for u in us) for k in keys}
        return n, sx, sxx, sy, sxy


def fit_eig(n, sx, sxx, sy, sxy):
    mu = sx / n
    C = sxx - n * np.outer(mu, mu)
    sd = np.sqrt(np.maximum(np.diag(C) / n, 0)); sd[sd == 0] = 1.0
    Cs = C / np.outer(sd, sd)
    w, V = np.linalg.eigh(Cs); w = np.maximum(w, 0)
    out = {}
    for k in sy:
        ym = sy[k] / n
        b = (sxy[k] - np.outer(sx, ym)) / sd[:, None]       # standardised centred X'y
        out[k] = dict(ym=ym, VTb=V.T @ b)
    return dict(mu=mu, sd=sd, w=w, V=V, n=n, t=out)


def coef(fit, k, alphas):
    """alphas: per-gene penalty (G,). Returns beta in standardised units (p, G)."""
    VTb = fit['t'][k]['VTb']
    return fit['V'] @ (VTb / (fit['w'][:, None] + alphas[None, :]))


def predict_fit(fit, k, alphas, X):
    B = coef(fit, k, alphas)
    return ((X - fit['mu']) / fit['sd']) @ B + fit['t'][k]['ym']


def ridgecv_fold(suff, X, T, unit, tr_units, te_mask, inner_groups):
    """Choose per-gene alpha by inner CV over inner_groups (list of lists of units), refit on tr_units, predict te."""
    outer = fit_eig(*suff.pool(tr_units))
    G = {k: v.shape[1] for k, v in T.items()}
    sse = {k: np.zeros((len(KGRID), G[k])) for k in T}
    for grp in inner_groups:
        fit_units = [u for u in tr_units if u not in grp]
        fi = fit_eig(*suff.pool(fit_units))
        hm = np.isin(unit, grp)
        Z = ((X[hm] - fi['mu']) / fi['sd']) @ fi['V']           # held-out block in the eigenbasis, once
        for k in T:
            Yc = T[k][hm] - fi['t'][k]['ym']
            VTb = fi['t'][k]['VTb']
            for a_i, kk in enumerate(KGRID):
                P = Z @ (VTb / (fi['w'][:, None] + fi['n'] * 10.0 ** kk))
                sse[k][a_i] += ((Yc - P) ** 2).sum(0)
    F, chosen = {}, {}
    for k in T:
        best = np.argmin(sse[k], axis=0)
        al = outer['n'] * 10.0 ** KGRID[best]
        F[k] = predict_fit(outer, k, al, X[te_mask]); chosen[k] = KGRID[best]
    return F, chosen


def inner_groups_for(tr_units, design):
    if design == 'center':
        return [[u] for u in tr_units]
    order = sorted(tr_units, key=lambda u: zlib.crc32(str(u).encode()))
    k = min(NINNER_DONOR, len(order))
    return [order[i::k] for i in range(k)]


def selftest():
    """The sufficient-statistics ridge, fitted on a subset of units and applied to the rest, equals sklearn's Ridge on
    StandardScaler features fitted on the same subset, at three penalties. Exits non-zero otherwise."""
    from sklearn.preprocessing import StandardScaler
    rng = np.random.default_rng(zlib.crc32(b'r11c_selftest'))
    n, p, g = 600, 40, 3
    X = rng.normal(size=(n, p)) * rng.uniform(0.5, 3, p) + rng.normal(size=p)
    Yv = X @ rng.normal(size=(p, g)) * 0.1 + rng.normal(size=(n, g))
    unit = np.array([f'd{i % 12}' for i in range(n)], dtype=object)
    T = {'log1p': Yv, 'lognorm': Yv * 2 + 1}
    S = Suff(X, T, unit)
    fit_units = [f'd{i}' for i in range(12) if i not in (0, 5)]
    fi = fit_eig(*S.pool(fit_units)); m = np.isin(unit, fit_units)
    worst = 0.0
    for kk in (-3.0, -1.0, 0.0):
        al = fi['n'] * 10.0 ** kk
        sc = StandardScaler().fit(X[m]); ref = Ridge(alpha=al, fit_intercept=True).fit(sc.transform(X[m]), T['lognorm'][m])
        mine = predict_fit(fi, 'lognorm', np.full(g, al), X[~m])
        worst = max(worst, float(np.abs(mine - ref.predict(sc.transform(X[~m]))).max()))
    print(f'selftest max abs diff to sklearn: {worst:.3e}')
    assert worst < 1e-8, worst
    print('selftest passed')


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        return selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument('task'); ap.add_argument('donor_map'); ap.add_argument('design', choices=['donor', 'center'])
    ap.add_argument('out'); ap.add_argument('--arm', required=True)
    ap.add_argument('--samples', default=''); ap.add_argument('--map-task', default='')
    ap.add_argument('--genes-from-parquet', default=''); ap.add_argument('--only-mapped', action='store_true')
    ap.add_argument('--group-centers-by-donor', action='store_true'); ap.add_argument('--tag', default='')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    encs, context, head = a.arm.split(':'); encoders = encs.split('+')
    assert context in ('none', 'ring1') and head in ('r10', 'ridgecv')
    T = json.load(open(a.task)); genes = [str(g) for g in T['genes_top50']]; gene_symbols = None
    if a.samples:
        ks = a.samples.split(','); T['samples'] = [s for s in T['samples'] if s['sample_id'] in set(ks)]
        assert len(T['samples']) == len(ks), 'unknown sample ids in --samples'
    if a.genes_from_parquet:   # round 10's mapping of symbols to Ensembl ids, transcribed
        syms = [n[3:] for n in pq.read_schema(a.genes_from_parquet).names if n.startswith('y__')]
        A0 = ad.read_h5ad(T['samples'][0]['expr_path'], backed='r')
        cands = [('var_names', pd.Index(A0.var_names.astype(str)))]
        cands += [(k, pd.Index(A0.var[k].astype(str))) for k in A0.var.columns if A0.var[k].dtype == object or str(A0.var[k].dtype) == 'category']
        best = max(cands, key=lambda kv: kv[1].isin(syms).sum())
        ens = pd.Index(A0.var['ensembl_id'].astype(str))
        m = {s_: ens[best[1].get_loc(s_)] for s_ in syms if s_ in best[1] and isinstance(best[1].get_loc(s_), (int, np.integer))}
        gene_symbols = [s_ for s_ in syms if s_ in m]; genes = [m[s_] for s_ in gene_symbols]
    dmf = pd.read_csv(a.donor_map, dtype=str)
    if a.map_task:
        dmf = dmf[dmf['task'] == a.map_task]
    dm = dmf.drop_duplicates('sample_id').set_index('sample_id')['donor_id']
    if a.only_mapped:
        T['samples'] = [s for s in T['samples'] if s['sample_id'] in dm.index]
    assert not [s['sample_id'] for s in T['samples'] if s['sample_id'] not in dm.index]
    name = a.tag or T['name']; t0 = time.time()
    parts, nnst = [], {}
    for s in T['samples']:
        Fx, Y, b, lib, nd, ns = load_sample(s, encoders, context, genes)
        parts.append((s['sample_id'], s['center_id'], dm[s['sample_id']], Fx, Y, b, lib, nd)); nnst[s['sample_id']] = ns
    X = np.concatenate([p[3] for p in parts]); Y = np.concatenate([p[4] for p in parts])
    lib = np.concatenate([p[6] for p in parts]).astype(np.float64); nd = np.concatenate([p[7] for p in parts]).astype(np.int64)
    sid = np.concatenate([[p[0]] * len(p[5]) for p in parts]); cen = np.concatenate([[p[1]] * len(p[5]) for p in parts])
    don = np.concatenate([[p[2]] * len(p[5]) for p in parts]); bc = np.concatenate([p[5] for p in parts])
    print(f'[load] {len(parts)} samples, {X.shape[0]} spots x {X.shape[1]} features, {time.time()-t0:.0f}s', flush=True)
    Tg = {'log1p': np.log1p(Y), 'lognorm': np.log1p(1e4 * Y / np.maximum(lib, 1)[:, None])}
    unit = don.astype(object) if a.design == 'donor' else cen.astype(object)
    if a.design == 'center' and a.group_centers_by_donor:
        par = {c_: c_ for c_ in sorted(set(cen))}
        def find(x):
            while par[x] != x:
                par[x] = par[par[x]]; x = par[x]
            return x
        for d_ in sorted(set(don)):
            cd = sorted(set(cen[don == d_]))
            for c_ in cd[1:]:
                par[find(c_)] = find(cd[0])
        comp = {}
        for c_ in sorted(par):
            comp.setdefault(find(c_), []).append(c_)
        lab = {c_: '+'.join(comp[find(c_)]) for c_ in par}
        unit = np.array([lab[c_] for c_ in cen], dtype=object)
    units = sorted(set(unit.tolist()))
    suff = Suff(X, Tg, unit) if head == 'ridgecv' else None
    F = {k: np.full_like(v, np.nan) for k, v in Tg.items()}
    fold = np.full(len(unit), '', dtype=object); secs, alph = [], {}
    for u in units:
        t1 = time.time(); te = unit == u; tr = ~te
        assert not (set(don[te]) & set(don[tr])), f'donor {u} on both sides'
        if head == 'r10':
            pipe, A_tr, reg, alpha = H.fit_base(X[tr], Tg['log1p'][tr])
            A_te = pipe.transform(X[te].astype(np.float64, copy=False))
            F['log1p'][te] = reg.predict(A_te)
            reg2 = Ridge(alpha=alpha, random_state=0, fit_intercept=True, solver='cholesky').fit(A_tr, Tg['lognorm'][tr])
            F['lognorm'][te] = reg2.predict(A_te)
        else:
            tr_units = [v for v in units if v != u]
            Fu, ch = ridgecv_fold(suff, X, Tg, unit, tr_units, te, inner_groups_for(tr_units, a.design))
            for k in Fu:
                F[k][te] = Fu[k]
            alph[str(u)] = {k: ch[k].tolist() for k in ch}
        fold[te] = str(u); secs.append(time.time() - t1)
        print(f'fold {u}: train {tr.sum()} test {te.sum()} {secs[-1]:.1f}s', flush=True)
    done = fold != ''
    frows = []
    for u in units:
        m = fold == u
        for k in Tg:
            for j, g in enumerate(genes):
                frows.append(dict(fold=str(u), scale=k, gene=g, n=int(m.sum()), pearson=pearson(Tg[k][m, j], F[k][m, j])))
    FR = pd.DataFrame(frows)
    summ = dict(task=name, arm=a.arm, encoders=encoders, context=context, head=head, design=a.design,
                spots=int(len(unit)), spots_predicted=int(done.sum()), samples=len(parts), donors=len(set(don)),
                centers=len(set(cen)), folds=len(units), n_features=int(X.shape[1]), n_genes=len(genes),
                seconds_per_fold=float(np.mean(secs)), gene_symbols=gene_symbols, kgrid=KGRID.tolist(),
                chosen_log10_alpha_over_n=alph, neighbours=nnst,
                pearson={k: {g: pearson(Tg[k][done, j], F[k][done, j]) for j, g in enumerate(genes)} for k in Tg})
    for k in Tg:
        summ[f'median_pearson_{k}'] = float(np.nanmedian(list(summ['pearson'][k].values())))
        fm = FR[FR.scale == k].groupby('fold').pearson.median()
        summ[f'fold_median_pearson_{k}'] = dict(median=float(fm.median()), q25=float(fm.quantile(.25)),
                                                 q75=float(fm.quantile(.75)), sd=float(fm.std(ddof=1)) if len(fm) > 1 else float('nan'))
    tag = f"{name}__{a.arm.replace(':', '__').replace('+', '-')}__{a.design}"
    json.dump(summ, open(os.path.join(a.out, f'pred_summary__{tag}.json'), 'w'), indent=1)
    FR.to_csv(os.path.join(a.out, f'pred_folds__{tag}.csv'), index=False)
    fields = [pa.field(n, pa.string()) for n in ('sample_id', 'barcode', 'donor_id', 'center_id', 'fold')]
    fields += [pa.field('lib_size', pa.float64()), pa.field('n_detected', pa.int64())]
    cols = dict(sample_id=sid[done].astype(str), barcode=bc[done].astype(str), donor_id=don[done].astype(str),
                center_id=cen[done].astype(str), fold=fold[done].astype(str), lib_size=lib[done], n_detected=nd[done])
    for k in Tg:
        for j, g in enumerate(genes):
            for pre, M in (('y', Tg[k]), ('f', F[k])):
                n = f'{pre}_{k}__{g}'; fields.append(pa.field(n, pa.float64())); cols[n] = M[done, j]
    pq.write_table(pa.Table.from_pydict(cols, schema=pa.schema(fields)), os.path.join(a.out, f'pred__{tag}.parquet'))
    print(json.dumps({k: v for k, v in summ.items() if k not in ('pearson', 'chosen_log10_alpha_over_n', 'neighbours')}, indent=1))


if __name__ == '__main__':
    main()
