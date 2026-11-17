"""Round 11, track closeout, gate G2: the tables of the G2 report, from the A5 prediction runs and the A2 anchors.

1. g2_strength.csv, one row per (task, arm, design): spots, folds, features; the median over genes of the per-gene
   Pearson over all held-out spots on each scale (round 10's `median_pearson_<scale>`, the masterplan's measure), its gain
   over arm R10 on the same task and design; the spread over folds of the per-fold median Pearson (q25, median, q75);
   and the paired per-fold difference to R10 (per fold, the median over genes of the fold's Pearson, arm minus R10):
   median, q25, q75 over folds and the share of folds where the arm is higher.
2. g2_p111.json: P11.1 scored on arm P, as the masterplan writes it (a gain of at least 0.02 over the reference on at
   least two of kidney Visium, bowel Visium and LUNG_XENIUM; references 0.471, 0.511, 0.619), with the gain over this
   track's own R10 on the same inputs beside it.
3. g2_anchor_ccrcc.csv: A2.2 on CCRCC, theta3 and mu, log1p, n_L 8. For the anchor's regime A cells and for round 10's
   (F2/regimeA/CCRCC__uni_v2), computed the same way as round10_final_runs_f2_diagnostics.py's f2_buy: per gene the
   ratio of fix1 (variance fpc) to classical (fpc) median width, then the median over genes; the median over genes of
   fix1's coverage and of its Monte Carlo standard error; and R2_c, the squared correlation over donors of z_g with
   f_g from the cluster values, median over genes. Round 10's R2_c comes from its cluster values
   (F2/cluster_values_v1/cluster_values__CCRCC.parquet).
Writes g2_summary.json first, then the tables.
Usage: round11_closeout_g2_aggregate.py <closeout_root> <round10_final_runs_root>
"""
import glob, json, os, sys
import numpy as np, pandas as pd

REF = {'kidney__Visium': 0.471, 'bowel__Visium': 0.511, 'LUNG_XENIUM': 0.619}
WANT = {('fix1', 'fpc'): 'fix1', ('classical', 'fpc'): 'cl'}


def strength(root):
    rows, folds = [], {}
    for p in sorted(glob.glob(f'{root}/predict/*__*__*/pred_summary__*.json')):
        d = os.path.basename(os.path.dirname(p)); task, arm, design = d.rsplit('__', 2)
        s = json.load(open(p))
        fp = glob.glob(os.path.join(os.path.dirname(p), 'pred_folds__*.csv'))
        F = pd.read_csv(fp[0]) if fp else None
        if F is not None:
            folds[(task, arm, design)] = F.groupby(['scale', 'fold']).pearson.median()
        r = dict(task=task, arm=arm, design=design, spots=s['spots'], folds=s['folds'], n_features=s['n_features'],
                 seconds_per_fold=s['seconds_per_fold'])
        for k in ('log1p', 'lognorm'):
            r[f'median_pearson_{k}'] = s[f'median_pearson_{k}']
            fm = s[f'fold_median_pearson_{k}']
            r.update({f'fold_{q}_{k}': fm[q] for q in ('q25', 'median', 'q75')})
        rows.append(r)
    S = pd.DataFrame(rows)
    for i, r in S.iterrows():
        ref = S[(S.task == r.task) & (S.arm == 'R10') & (S.design == r.design)]
        for k in ('log1p', 'lognorm'):
            if len(ref):
                S.loc[i, f'gain_vs_R10_{k}'] = r[f'median_pearson_{k}'] - ref[f'median_pearson_{k}'].iloc[0]
            a, b = folds.get((r.task, r.arm, r.design)), folds.get((r.task, 'R10', r.design))
            if a is not None and b is not None:
                d = (a.loc[k] - b.loc[k]).dropna()
                S.loc[i, f'paired_fold_diff_median_{k}'] = d.median()
                S.loc[i, f'paired_fold_diff_q25_{k}'] = d.quantile(.25)
                S.loc[i, f'paired_fold_diff_q75_{k}'] = d.quantile(.75)
                S.loc[i, f'share_folds_higher_{k}'] = float((d > 0).mean())
    return S


def p111(S):
    out = dict(rule='arm P gains >= 0.02 over the reference on at least two of three tasks, log1p, donor design', tasks={})
    n = 0
    for t, ref in REF.items():
        p = S[(S.task == t) & (S.arm == 'P') & (S.design == 'donor')]
        r = S[(S.task == t) & (S.arm == 'R10') & (S.design == 'donor')]
        if not len(p):
            continue
        g = float(p.median_pearson_log1p.iloc[0] - ref)
        out['tasks'][t] = dict(reference=ref, P=float(p.median_pearson_log1p.iloc[0]), gain_vs_reference=g,
                               R10_this_track=float(r.median_pearson_log1p.iloc[0]) if len(r) else None,
                               gain_vs_R10=float(p.gain_vs_R10_log1p.iloc[0]) if len(r) else None, meets=g >= 0.02)
        n += g >= 0.02
    out['tasks_meeting'] = int(n); out['verdict'] = 'held' if n >= 2 else 'refuted'
    return out


def buy(cells, cv):
    x = pd.read_parquet(cells)
    x = x[(x.n == 8) & x.estimand.isin(['theta3', 'mu']) & (x.scale == 'log1p')]
    x = x[[(a, v) in WANT for a, v in zip(x.arm, x.variance)]].copy()
    x['lab'] = [WANT[(a, v)] for a, v in zip(x.arm, x.variance)]
    W = x.pivot_table(index=['task', 'encoder', 'scale', 'estimand', 'gene'], columns='lab',
                      values=['median_width', 'coverage', 'coverage_se']).reset_index()
    W.columns = ['_'.join([c for c in col if c]) if isinstance(col, tuple) else col for col in W.columns]
    W['wr_fix1'] = W.median_width_fix1 / W.median_width_cl
    C = pd.read_parquet(cv)
    C = C[(C.scale == 'log1p') & (C.encoder == 'uni_v2')]
    r2 = C.groupby(['estimand', 'gene']).apply(
        lambda g: float(np.corrcoef(g.z, g.f)[0, 1] ** 2) if g.z.std() > 0 and g.f.std() > 0 else np.nan).rename('R2c').reset_index()
    W = W.merge(r2, on=['estimand', 'gene'], how='left')
    return W.groupby(['task', 'encoder', 'scale', 'estimand']).agg(
        genes=('gene', 'size'), median_wr_fix1=('wr_fix1', 'median'), median_cov_fix1=('coverage_fix1', 'median'),
        median_cov_cl=('coverage_cl', 'median'), median_mcse_fix1=('coverage_se_fix1', 'median'),
        median_R2c=('R2c', 'median')).reset_index()


def main():
    root, r10 = sys.argv[1], sys.argv[2]
    S = strength(root); P = p111(S)
    an = f'{root}/anchor/CCRCC__R10_v2'
    A = buy(f'{an}/regimeA/regimeA_cells.parquet', f'{an}/cv/cluster_values__CCRCC.parquet'); A['source'] = 'round11 R10 (corpus, 73,813 spots)'
    B = buy(f'{r10}/F2/regimeA/CCRCC__uni_v2/regimeA_cells.parquet', f'{r10}/F2/cluster_values_v1/cluster_values__CCRCC.parquet')
    B = B[B.encoder == 'uni_v2']; B['source'] = 'round10 (round 3 file, 74,220 spots)'
    AN = pd.concat([A, B], ignore_index=True)
    t3 = AN[AN.estimand == 'theta3'].set_index('source')
    summ = dict(p111=P, anchor_ccrcc_theta3=t3[['median_wr_fix1', 'median_cov_fix1', 'median_mcse_fix1', 'median_R2c']].to_dict('index'))
    json.dump(summ, open('g2_summary.json', 'w'), indent=1, default=float)
    S.to_csv('g2_strength.csv', index=False); AN.to_csv('g2_anchor_ccrcc.csv', index=False)
    json.dump(P, open('g2_p111.json', 'w'), indent=1, default=float)
    print(json.dumps(summ, indent=1, default=float)); print(S.to_string()); print(AN.to_string())


if __name__ == '__main__':
    main()
