"""Round 10, track final-runs, stage F1.4: donor-level diagnostics of a prediction file (ledger D12 and D13, INT5).

1. D12. Per gene and scale, the leave-one-donor-out R^2 of the donor mean y_d regressed on the donor mean prediction f_d
   (round 9's loo_r2, code/scripts/round9_depth_probe_diagnostics.py), reported against two baselines:
     R2_loo_const = 1 - sum_h res_h^2 / sum_h (y_h - mean_{-h} y)^2   (the leave-one-out constant; ledger D12)
     R2_full_mean = 1 - sum_h res_h^2 / sum_h (y_h - mean y)^2        (round 9's, kept as the anchor)
   and, beside them, the same with the raw prediction f_d as the forecast (no regression), against the LOO constant.
2. D13. Per donor, four diagnostics with z-scores across donors and ranks (1 = largest):
     avg_y        mean over genes of the donor mean of y;
     resid_scale  c_g of round 9's cross-gene set (round9_stud_feasibility.py, D xgene) on the donor's full data:
                  the median over genes of (RMS of the donor's residuals y - f for gene j) / (RMS over all spots of gene j);
     pred_out     root mean square over genes of the donor mean prediction, standardised per gene across donors;
     emb_out      the same on the donor mean embedding (per dimension), when --task and --encoder are given.
   Round 9's diagnostics file has no committed writer (ledger D13); these definitions are this script's.
3. INT5. Per donor, the median and mean raw library size and the median number of detected genes per spot, with z and
   rank, when the file carries lib_size and n_detected.
Column formats: this track's files (y_<scale>__<gene>, f_<scale>__<gene>) or round 3's (y__<gene>, f__<gene>, log1p).
Usage: round10_final_runs_f1_donor_diag.py <pred.parquet> <name> <outdir> [--task task.json --encoder enc]
"""
import argparse, json, os
import h5py, numpy as np, pandas as pd


def loo_fit(x, y):
    G = len(y); X = np.column_stack([np.ones(G), x]); res = np.empty(G)
    for h in range(G):
        tr = np.arange(G) != h
        b = np.linalg.lstsq(X[tr], y[tr], rcond=None)[0]; res[h] = y[h] - X[h] @ b
    return res


def zr(v):
    v = np.asarray(v, float); sd = v.std(ddof=1)
    z = (v - v.mean()) / sd if sd > 0 else np.zeros_like(v)
    rank = pd.Series(-v).rank(method='min').to_numpy().astype(int)
    return z, rank


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('pred'); ap.add_argument('name'); ap.add_argument('out')
    ap.add_argument('--task', default=''); ap.add_argument('--encoder', default='')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    df = pd.read_parquet(a.pred); df['donor_id'] = df['donor_id'].astype(str)
    if any(c.startswith('y_log1p__') for c in df.columns):
        scales = {sc: sorted(c.split('__', 1)[1] for c in df.columns if c.startswith(f'y_{sc}__')) for sc in ('log1p', 'lognorm')}
        col = lambda pre, sc, g: f'{pre}_{sc}__{g}'
    else:
        scales = {'log1p': sorted(c[3:] for c in df.columns if c.startswith('y__'))}
        col = lambda pre, sc, g: f'{pre}__{g}'
    donors = sorted(df.donor_id.unique()); G = len(donors)
    rows = []
    for sc, genes in scales.items():
        Y = df.groupby('donor_id')[[col('y', sc, g) for g in genes]].mean().loc[donors].to_numpy()
        Fm = df.groupby('donor_id')[[col('f', sc, g) for g in genes]].mean().loc[donors].to_numpy()
        for j, g in enumerate(genes):
            y, f = Y[:, j], Fm[:, j]
            res = loo_fit(f[:, None], y)
            loo_c = y - (y.sum() - y) / (G - 1)
            rows.append(dict(name=a.name, scale=sc, gene=g, G=G,
                             R2_loo_const=1 - (res ** 2).sum() / (loo_c ** 2).sum(),
                             R2_full_mean=1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum(),
                             R2_rawpred_loo_const=1 - ((y - f) ** 2).sum() / (loo_c ** 2).sum()))
    r2 = pd.DataFrame(rows); r2.to_csv(os.path.join(a.out, f'd12_lodo_r2__{a.name}.csv'), index=False)
    med = r2.groupby('scale')[['R2_loo_const', 'R2_full_mean', 'R2_rawpred_loo_const']].median().reset_index()
    med.insert(0, 'name', a.name); med['genes'] = r2.groupby('scale').size().values
    med.to_csv(os.path.join(a.out, f'd12_lodo_r2_medians__{a.name}.csv'), index=False)
    # D13 on log1p
    genes = scales['log1p']
    Yc = df[[col('y', 'log1p', g) for g in genes]].to_numpy(); Fc = df[[col('f', 'log1p', g) for g in genes]].to_numpy()
    Rc = Yc - Fc; sig = np.sqrt((Rc ** 2).mean(0)); d = df.donor_id.to_numpy()
    diag = pd.DataFrame(dict(donor_id=donors))
    diag['spots'] = [int((d == u).sum()) for u in donors]
    diag['avg_y'] = [Yc[d == u].mean(0).mean() for u in donors]
    diag['resid_scale'] = [np.median(np.sqrt((Rc[d == u] ** 2).mean(0)) / np.where(sig > 0, sig, 1)) for u in donors]
    Fd = np.array([Fc[d == u].mean(0) for u in donors]); sdF = Fd.std(0, ddof=1)
    diag['pred_out'] = np.sqrt((((Fd - Fd.mean(0)) / np.where(sdF > 0, sdF, 1)) ** 2).mean(1))
    if a.task and a.encoder:
        T = json.load(open(a.task)); emb = {}
        keep = set(df.sample_id.astype(str))
        for s in T['samples']:
            if s['sample_id'] not in keep:
                continue
            with h5py.File(s['emb_paths'][a.encoder], 'r') as f:
                E = f['embeddings'][:]; b = [x.decode() if isinstance(x, bytes) else str(x) for x in np.asarray(f['barcodes'][:]).ravel()]
            sel = df[df.sample_id.astype(str) == s['sample_id']]
            m = pd.Index(b).get_indexer(sel.barcode.astype(str)); ok = m >= 0
            for u, grp in pd.DataFrame(dict(u=sel.donor_id.to_numpy()[ok], i=m[ok])).groupby('u'):
                emb.setdefault(u, []).append(E[grp.i.to_numpy()])
        Ed = np.array([np.concatenate(emb[u]).mean(0) for u in donors]); sdE = Ed.std(0, ddof=1)
        diag['emb_out'] = np.sqrt((((Ed - Ed.mean(0)) / np.where(sdE > 0, sdE, 1)) ** 2).mean(1))
    if 'lib_size' in df.columns:
        g = df.groupby('donor_id')
        diag['lib_median'] = g.lib_size.median().loc[donors].to_numpy(); diag['lib_mean'] = g.lib_size.mean().loc[donors].to_numpy()
        diag['detected_median'] = g.n_detected.median().loc[donors].to_numpy()
    for k in [c for c in diag.columns if c not in ('donor_id', 'spots')]:
        diag[f'z_{k}'], diag[f'rank_{k}'] = zr(diag[k])
    diag.insert(0, 'name', a.name)
    diag.to_csv(os.path.join(a.out, f'd13_donor_diagnostics__{a.name}.csv'), index=False)
    print(med.to_string()); print(diag.sort_values('rank_avg_y').head(5).to_string())


if __name__ == '__main__':
    main()
