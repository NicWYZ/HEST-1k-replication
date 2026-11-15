"""Round 10, track final-runs, F3 open point 7 (plan, section 5d.6 item 7): the cells where the fixed coefficient's
coverage does not fall with the residual max-share kappa(e).

usage: round10_final_runs_f3_reruns_kappa_rise.py <clone> <f2_gene_diag.parquet> <out_dir> [n_perm]
Inputs: the committed per-cell table <clone>/results/round10/final_runs/F2/diagnostics/f2_shortfall.csv, the committed
regime A summary (for R, the draws behind each gene's coverage) and F2's gene-level f2_gene_diag.parquet.
Anchors, before anything else: (a) the Spearman correlation of coverage_fix1 with kappa_e is recomputed in every cell
from the gene rows with the expression of round10_final_runs_f2_diagnostics.py and must equal the committed
rho_cov_fix1_kappa_e in all 1,722 cells (same NaN pattern, difference at most 1e-12, the CSV read being round-trip); (b) its median, share negative and count by
group must equal the committed r09b_shortfall_correlations.csv (to 1e-12).
Then for each cell whose correlation is not negative or is undefined: the gene count, the ranges of kappa(e) and of
coverage, the Monte Carlo standard error of coverage per gene, sqrt(c (1 - c) / R), summarised by its median and
maximum, a within-cell permutation test of the Spearman correlation over genes (n_perm permutations of the coverage
ranks against the kappa(e) ranks, seed zlib.crc32 of 'f3_kappa_rise|<cell>'), giving the two-sided p
(1 + #{|rho*| >= |rho|}) / (n_perm + 1) and the one-sided p for a rise, and the coverage fitted by least squares on
kappa(e) across its interquartile range, slope * (Q3 - Q1). A cell is a genuine rise if the two-sided p < 0.05 and the
fitted rise is at least 0.01 (plan). Writes f3_kappa_rise_summary.json first, then f3_kappa_rise_cells.csv,
f3_kappa_rise_counts.csv and f3_kappa_rise_genes.csv (the gene rows of every genuine-rise cell).
"""
import json, os, sys, zlib
import numpy as np, pandas as pd
from scipy import stats

clone, gdp, out = sys.argv[1:4]
NP = int(sys.argv[4]) if len(sys.argv) > 4 else 10000
os.makedirs(out, exist_ok=True)
F2c = os.path.join(clone, 'results/round10/final_runs/F2')
CORPUS = ['kidney__Visium', 'breast__Spatial_Transcriptomics', 'bowel__Visium', 'brain__Visium',
          'breast__Xenium', 'lung__Xenium']
C = ['task', 'encoder', 'scale', 'estimand', 'n']
summ = dict(script='round10_final_runs_f3_reruns_kappa_rise.py', n_perm=NP, criterion='two-sided permutation p < 0.05 and fitted rise over the IQR of kappa_e >= 0.01')
sp = os.path.join(out, 'f3_kappa_rise_summary.json'); json.dump(summ, open(sp, 'w'), indent=1)

sf = pd.read_csv(os.path.join(F2c, 'diagnostics/f2_shortfall.csv'), float_precision='round_trip')
J = pd.read_parquet(gdp)
summ['gene_rows'] = int(len(J)); summ['cells'] = int(len(sf))
# (a) rho per cell, the diagnostics' own expression
rho = lambda a_, b_: float(stats.spearmanr(a_, b_, nan_policy="omit")[0]) if np.isfinite(a_).sum() > 3 else np.nan
cc = J.groupby(C).apply(lambda g: pd.Series(dict(rho_re=rho(g.coverage_fix1, g.kappa_e)))).reset_index()
m = sf[C + ['rho_cov_fix1_kappa_e']].merge(cc, on=C, how='outer', indicator=True)
a = m.rho_cov_fix1_kappa_e.to_numpy(float); b = m.rho_re.to_numpy(float)
anc = dict(cells_committed=int(len(sf)), cells_recomputed=int(len(cc)), cells_unmatched=int((m._merge != 'both').sum()),
           nan_pattern_equal=bool((np.isnan(a) == np.isnan(b)).all()),
           max_abs_diff=float(np.nanmax(np.abs(a - b))))
# (b) the r09b row values
r9b = pd.read_csv(os.path.join(F2c, 'report_tables/r09b_shortfall_correlations.csv'), float_precision='round_trip')
sf['group'] = np.where(sf.task.isin(CORPUS), 'corpus', 'HEST_ACS')
rb = []
for grp, g in sf.groupby('group'):
    ref = r9b[r9b.group == grp].iloc[0]
    v = g.rho_cov_fix1_kappa_e
    rb.append(dict(group=grp, cells=len(g), cells_ref=int(ref.cells), median=float(v.median()), median_ref=float(ref['rho_cov_fix1_kappa_e__median']),
                   share_negative=float((v < 0).mean()), share_negative_ref=float(ref['rho_cov_fix1_kappa_e__share_negative']),
                   count=int(v.notna().sum()), count_ref=int(ref['rho_cov_fix1_kappa_e__count'])))
anc['r09b'] = rb
anc['pass'] = bool(anc['cells_unmatched'] == 0 and anc['nan_pattern_equal'] and anc['max_abs_diff'] <= 1e-12 and
                   all(r['cells'] == r['cells_ref'] and abs(r['median'] - r['median_ref']) <= 1e-12 and abs(r['share_negative'] - r['share_negative_ref']) <= 1e-12
                       and r['count'] == r['count_ref'] for r in rb))
summ['anchor'] = anc; json.dump(summ, open(sp, 'w'), indent=1); print(json.dumps(anc, indent=1), flush=True)
if not anc['pass']:
    print('ANCHOR FAILED'); sys.exit(2)

# R behind each coverage: regime A's fix1|fpc rows
ra = pd.read_csv(os.path.join(F2c, 'aggregate/f2_regimeA_summary.csv.gz'))
Rk = ra[(ra.arm == 'fix1') & (ra.variance == 'fpc')][C + ['R']].drop_duplicates()
assert not Rk.duplicated(C).any()
sel = sf[~(sf.rho_cov_fix1_kappa_e < 0)].merge(Rk, on=C, how='left')
summ['cells_not_negative_or_undefined'] = int(len(sel))
summ['cells_undefined'] = int(sel.rho_cov_fix1_kappa_e.isna().sum())
summ['R_values'] = sorted(int(x) for x in sel.R.dropna().unique())
Jg = {k: g for k, g in J.groupby(C)}
rows, gene_rows = [], []
for _, r in sel.iterrows():
    key = tuple(r[c] for c in C); tag = '|'.join(str(x) for x in key)
    g = Jg[key]
    x = g.kappa_e.to_numpy(float); y = g.coverage_fix1.to_numpy(float)
    ok = np.isfinite(x) & np.isfinite(y); x, y = x[ok], y[ok]; ng = len(x)
    R = float(r.R); se = np.sqrt(y * (1 - y) / R)
    d = dict(zip(C, key), group=r.group, G=int(r.G), genes=int(len(g)), genes_used=ng, R=int(R),
             rho_committed=r.rho_cov_fix1_kappa_e,
             kappa_e_min=float(x.min()) if ng else np.nan, kappa_e_q25=float(np.quantile(x, 0.25)) if ng else np.nan,
             kappa_e_q75=float(np.quantile(x, 0.75)) if ng else np.nan, kappa_e_max=float(x.max()) if ng else np.nan,
             cov_min=float(y.min()) if ng else np.nan, cov_median=float(np.median(y)) if ng else np.nan,
             cov_max=float(y.max()) if ng else np.nan,
             mcse_cov_median=float(np.median(se)) if ng else np.nan, mcse_cov_max=float(se.max()) if ng else np.nan)
    if ng > 3 and np.isfinite(r.rho_cov_fix1_kappa_e) and np.std(x) > 0 and np.std(y) > 0:
        rx = stats.rankdata(x); ry = stats.rankdata(y)
        rxc = rx - rx.mean(); ryc = ry - ry.mean()
        rho_obs = float(rxc @ ryc / np.sqrt((rxc @ rxc) * (ryc @ ryc)))
        rng = np.random.default_rng(zlib.crc32(f'f3_kappa_rise|{tag}'.encode()))
        P = ryc[np.argsort(rng.random((NP, ng)), axis=1)]
        rp = (P @ rxc) / np.sqrt((rxc @ rxc) * (ryc @ ryc))
        eps = 1e-12
        p2 = (1 + int((np.abs(rp) >= abs(rho_obs) - eps).sum())) / (NP + 1)
        p1 = (1 + int((rp >= rho_obs - eps).sum())) / (NP + 1)
        slope = float(np.polyfit(x, y, 1)[0])
        rise = slope * (d['kappa_e_q75'] - d['kappa_e_q25'])
        cls = ('genuine_rise' if (p2 < 0.05 and rise >= 0.01) else
               'significant_rise_below_0.01' if (p2 < 0.05 and rho_obs > 0) else 'not_significant' if p2 >= 0.05 else 'other')
        d.update(rho_ranks=rho_obs, rho_diff=abs(rho_obs - r.rho_cov_fix1_kappa_e), p_perm_two_sided=p2,
                 p_perm_one_sided_rise=p1, ols_slope=slope, fitted_rise_iqr=rise, classification=cls)
    else:
        d.update(rho_ranks=np.nan, rho_diff=np.nan, p_perm_two_sided=np.nan, p_perm_one_sided_rise=np.nan,
                 ols_slope=np.nan, fitted_rise_iqr=np.nan, classification='undefined')
    rows.append(d)
    if d['classification'] == 'genuine_rise':
        gene_rows.append(g.assign(cell=tag))
T = pd.DataFrame(rows)
summ['max_rho_rank_vs_committed'] = float(T.rho_diff.max())
cnt = T.groupby(['group', 'classification']).size().rename('cells').reset_index()
cnt2 = T.groupby(['group', 'task', 'estimand', 'classification']).size().rename('cells').reset_index()
pd.concat([cnt.assign(level='group'), cnt2.assign(level='group_task_estimand')], ignore_index=True).to_csv(
    os.path.join(out, 'f3_kappa_rise_counts.csv'), index=False)
gen = int((T.classification == 'genuine_rise').sum())
summ['classification'] = T.classification.value_counts().to_dict()
summ['prediction'] = dict(text='fewer than 0.1 of the 1,722 cells show a genuine rise', genuine=gen, cells=int(len(sf)),
                          share=gen / len(sf), verdict='held' if gen / len(sf) < 0.1 else 'refuted')
json.dump(summ, open(sp, 'w'), indent=1, default=str)
T.to_csv(os.path.join(out, 'f3_kappa_rise_cells.csv'), index=False)
cols = ['cell'] + C[:4] + ['gene', 'n', 'G', 'kappa_e', 'coverage_fix1', 'coverage_cl', 'coverage_xf2', 'median_width_fix1',
                           'median_width_cl', 'skew_e', 'skew_z', 'Gstar_e', 'kappa_ols', 'kappa_sup', 'beyond_sup', 'R2c']
GR = pd.concat(gene_rows, ignore_index=True)[cols] if gene_rows else pd.DataFrame(columns=cols)
GR.to_csv(os.path.join(out, 'f3_kappa_rise_genes.csv'), index=False)
summ['genes_rows_written'] = int(len(GR)); summ['finished'] = True
json.dump(summ, open(sp, 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in summ.items() if k != 'anchor'}, indent=1, default=str))
