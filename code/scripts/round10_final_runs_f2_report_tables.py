"""Round 10, track final-runs, gate F2: the report's tables, read from the committed F2 aggregates.

Usage: round10_final_runs_f2_report_tables.py <clone> <base> <outdir>
  <clone>  the track's code clone (committed tables under results/round10/final_runs/F2/, round 7's S5 file)
  <base>   the bulk results directory (unit summaries of regime A, the regime A smoke anchor)
  <outdir> where the report tables are written

Every table is a selection or a summary over cells of a committed aggregate. Nothing is re-estimated.
A "cell" is one (task, encoder, scale, estimand, n) row of an aggregate, whose values are already medians
or quantiles over genes. The primary scale is log1p on the expression tasks and log_income on ACS by state.
"""
import glob, json, os, sys
import numpy as np
import pandas as pd

clone, base, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
F2c = os.path.join(clone, 'results/round10/final_runs/F2')
F2b = os.path.join(base, 'F2')
HEST = ['CCRCC', 'CCRCC_merged', 'INDIANA_KIDNEY', 'LUNG_XENIUM']
FOUR = ['CCRCC', 'INDIANA_KIDNEY', 'LUNG_XENIUM', 'ACS_STATES']
CORPUS = ['kidney__Visium', 'breast__Spatial_Transcriptomics', 'bowel__Visium', 'brain__Visium',
          'breast__Xenium', 'lung__Xenium']
TASKS = HEST + ['ACS_STATES'] + CORPUS
PRIMARY = {'log1p', 'log_income'}
log = []


def note(s):
    log.append(s); print(s, flush=True)


def wr(df, name):
    df.to_csv(os.path.join(out, name), index=False)
    note(f'wrote {name}: {len(df)} rows')


def enc_ok(df, enc='uni_v2'):
    return df[(df.encoder == enc) | (df.task == 'ACS_STATES')]


def prim(df):
    return df[df.scale.isin(PRIMARY)]


def order(df):
    df = df.copy(); df['_o'] = df.task.map({t: i for i, t in enumerate(TASKS)})
    return df.sort_values([c for c in ['_o', 'estimand', 'n', 'm'] if c in df.columns]).drop(columns='_o')


# ---------------------------------------------------------------- regime A
ra = pd.read_csv(os.path.join(F2c, 'aggregate/f2_regimeA_summary.csv.gz'))
ra['av'] = ra.arm + '|' + ra.variance
ra['group'] = np.where(ra.task.isin(CORPUS), 'corpus', 'HEST_ACS')
note(f'regime A summary: {len(ra)} rows, {ra[["task","encoder","scale","estimand","n"]].drop_duplicates().shape[0]} cells')

MAIN = ['classical|fpc', 'fix1|fpc', 'xf2_r5|V_w', 'xf2_r5|V', 'xf2_r5|V_max', 'xf2_r5|V_cons', 'xf2_fix1|V_w',
        'xf2_ols|V_w', 'bh|own', 'bh_t|own', 'bh_t_fpc|own', 'fix1_nofpc|nofpc']
sel = prim(enc_ok(ra))
rows = []
for (t, e, n), g in sel.groupby(['task', 'estimand', 'n']):
    r = {'task': t, 'estimand': e, 'n': n, 'G': g.G.iloc[0], 'genes': g.genes.iloc[0]}
    for av in MAIN:
        h = g[g.av == av]
        if len(h):
            h = h.iloc[0]
            r[f'cov__{av}'] = h.median_coverage; r[f'q10__{av}'] = h.q10_coverage; r[f'q90__{av}'] = h.q90_coverage
            r[f'width__{av}'] = h.median_width; r[f'rmse__{av}'] = h.median_rmse
            r[f'noint__{av}'] = h.median_frac_no_interval
    rows.append(r)
t01 = order(pd.DataFrame(rows))
wr(t01, 'r01_regimeA_uni_v2_primary.csv')

# grid ranges of median coverage over every cell, per arm and n, by group
gr = []
for (av, n, grp), g in ra.groupby(['av', 'n', 'group']):
    i = g.median_coverage.idxmin()
    gr.append({'arm': av, 'n': n, 'group': grp, 'cells': len(g), 'min': g.median_coverage.min(),
               'q10': g.median_coverage.quantile(.1), 'median': g.median_coverage.median(),
               'max': g.median_coverage.max(),
               'cell_of_min': '|'.join(str(ra.loc[i, k]) for k in ['task', 'encoder', 'scale', 'estimand'])})
wr(pd.DataFrame(gr), 'r02_regimeA_grid_ranges.csv')

# bootstrap arms beside fix1 (uni_v2, every scale the arms ran on)
B = ['fix1|fpc', 'boot_pairs_pct|boot', 'boot_wild_webb_t|boot', 'boot_raowu_t|boot']
bs = enc_ok(ra)
cells = bs[bs.av == 'boot_pairs_pct|boot'][['task', 'scale', 'estimand', 'n']].drop_duplicates()
rows = []
for _, c in cells.iterrows():
    g = bs[(bs.task == c.task) & (bs.scale == c.scale) & (bs.estimand == c.estimand) & (bs.n == c.n)]
    r = dict(c)
    for av in B:
        h = g[g.av == av]
        if len(h):
            r[f'cov__{av}'] = h.median_coverage.iloc[0]; r[f'width__{av}'] = h.median_width.iloc[0]
            r[f'R__{av}'] = h.R.iloc[0]
    rows.append(r)
t03 = order(pd.DataFrame(rows))
wr(t03, 'r03_regimeA_bootstrap.csv')
bsum = []
for av in B[1:]:
    for n, g in t03.groupby('n'):
        bsum.append({'arm': av, 'n': n, 'cells': g[f'cov__{av}'].notna().sum(), 'min': g[f'cov__{av}'].min(),
                     'median': g[f'cov__{av}'].median(), 'max': g[f'cov__{av}'].max(),
                     'median_width_ratio_to_fix1': (g[f'width__{av}'] / g['width__fix1|fpc']).median()})
wr(pd.DataFrame(bsum), 'r03b_bootstrap_ranges.csv')

# controls: constant predictor must equal classical; permuted predictor near nominal, not narrower than classical
key = ['task', 'encoder', 'scale', 'estimand', 'n']
piv_c = ra[ra.av.isin(['classical|fpc', 'ctrl_const_fix1|fpc', 'ctrl_perm_fix1|fpc', 'ctrl_perm_xf2_r5|V_w'])]
pc = piv_c.pivot_table(index=key, columns='av', values=['median_coverage', 'median_width']).reset_index()
pc.columns = ['__'.join([x for x in col if x]) for col in pc.columns]
ctrl = {
    'cells': len(pc),
    'max_abs_cov_const_minus_classical': float((pc['median_coverage__ctrl_const_fix1|fpc'] - pc['median_coverage__classical|fpc']).abs().max()),
    'max_rel_width_const_minus_classical': float(((pc['median_width__ctrl_const_fix1|fpc'] - pc['median_width__classical|fpc']).abs() / pc['median_width__classical|fpc']).max()),
    'perm_fix1_cov_min': float(pc['median_coverage__ctrl_perm_fix1|fpc'].min()),
    'perm_fix1_cov_median': float(pc['median_coverage__ctrl_perm_fix1|fpc'].median()),
    'perm_fix1_cov_max': float(pc['median_coverage__ctrl_perm_fix1|fpc'].max()),
    'perm_fix1_share_cells_narrower_than_classical': float((pc['median_width__ctrl_perm_fix1|fpc'] < pc['median_width__classical|fpc']).mean()),
    'perm_fix1_min_width_ratio_to_classical': float((pc['median_width__ctrl_perm_fix1|fpc'] / pc['median_width__classical|fpc']).min()),
    'perm_xf2_cov_min': float(pc['median_coverage__ctrl_perm_xf2_r5|V_w'].min()),
    'perm_xf2_cov_median': float(pc['median_coverage__ctrl_perm_xf2_r5|V_w'].median()),
}
# per-unit identity of the constant control (written by the driver, which stops if it fails)
ident = []
for p in sorted(glob.glob(os.path.join(F2b, 'regimeA', '*', 'regimeA_summary.json'))):
    d = json.load(open(p)); ident.append(d.get('max_const_identity_dev'))
prov = sorted(glob.glob(os.path.join(F2b, 'regimeA', '*', 'PROVENANCE.txt')))
st = [l.split(':', 1)[1].strip() for p in prov for l in open(p) if l.startswith('status:')]
ctrl.update({'regimeA_units': len(ident), 'regimeA_units_completed': int(sum(s == 'COMPLETED' for s in st)),
             'max_const_identity_dev_over_units': float(np.nanmax([x for x in ident if x is not None]))})
smoke = json.load(open(os.path.join(F2b, 'regimeA_smoke', 'regimeA_summary.json')))
ctrl['anchor_r9'] = smoke.get('anchor_r9')
json.dump(ctrl, open(os.path.join(out, 'r04_controls_and_anchor.json'), 'w'), indent=1, default=float)
note('controls ' + json.dumps(ctrl, default=float))

# ---------------------------------------------------------------- switch rule
sw = pd.read_csv(os.path.join(F2c, 'aggregate/f2_switch_rule.csv'))
rows = []
for t, g in sw.groupby('task'):
    i = g.median_ev_over_var.idxmin()
    r = {'task': t, 'cells': len(g), 'min_median_ev_over_var': g.median_ev_over_var.min(),
         'cell_of_min': '|'.join(str(sw.loc[i, k]) for k in ['encoder', 'scale', 'estimand', 'n']),
         'max_share_genes_below_095': g.share_genes_below_095.max(),
         'frac_V_neg_n6_min': g[g.n == 6].median_frac_V_neg.min(), 'frac_V_neg_n6_max': g[g.n == 6].median_frac_V_neg.max()}
    for e in ['theta3', 'mu']:
        h = prim(enc_ok(g)); h = h[(h.estimand == e) & (h.n == 6)]
        r[f'frac_V_neg_n6_uni_primary_{e}'] = h.median_frac_V_neg.iloc[0] if len(h) else np.nan
    rows.append(r)
wr(order(pd.DataFrame(rows)), 'r05_switch_by_task.csv')
fv = sw.groupby('n').median_frac_V_neg.agg(['count', 'min', 'median', 'max']).reset_index()
wr(fv, 'r05b_frac_V_neg_by_n.csv')

# ---------------------------------------------------------------- fixed coefficient's cost
fc = pd.read_csv(os.path.join(F2c, 'aggregate/f2_fix1_cost.csv'))
rows = []
for (t, s, e), g in fc[fc.n == 8].groupby(['task', 'scale', 'estimand']):
    u = g[(g.encoder == 'uni_v2') | (g.task == 'ACS_STATES')]
    rows.append({'task': t, 'scale': s, 'estimand': e, 'genes': u.genes.iloc[0] if len(u) else np.nan,
                 'share_uni_v2': u.share_fix1_wider_median.iloc[0] if len(u) else np.nan,
                 'share_min_enc': g.share_fix1_wider_median.min(), 'share_max_enc': g.share_fix1_wider_median.max(),
                 'median_width_ratio_uni_v2': u.median_width_ratio.iloc[0] if len(u) else np.nan})
wr(order(pd.DataFrame(rows)), 'r06_fix1_cost_n8.csv')
note(f'fix1 cost: max |share by median width - share by mean| over all rows = {(fc.share_fix1_wider_median - fc.share_fix1_wider_mean).abs().max():.6g}')

# ---------------------------------------------------------------- limits arms
lm = pd.read_csv(os.path.join(F2c, 'aggregate_limits/f2_limits_summary.csv'))
lm['av'] = lm.arm + '|' + lm.variance
rows = []
for (av, n), g in lm.groupby(['av', 'n']):
    rows.append({'arm': av, 'n': n, 'cells': len(g), 'min': g.median_coverage.min(), 'median': g.median_coverage.median(),
                 'max': g.median_coverage.max(), 'median_frac_no_interval': g.median_frac_no_interval.median()})
wr(pd.DataFrame(rows), 'r07_limits_ranges.csv')
lv = pd.read_csv(os.path.join(F2c, 'aggregate_limits/f2_limits_vs_regimeA.csv'))
wcols = [c for c in lv.columns if c.startswith('median_width_ratio_to_classical__')]
rows = []
for n, g in lv.groupby('n'):
    r = {'n': n, 'cells': len(g)}
    for c in wcols:
        r[c.replace('median_width_ratio_to_classical__', 'wr__')] = g[c].median()
    rows.append(r)
wr(pd.DataFrame(rows), 'r07b_limits_width_ratio_by_n.csv')
h = lv[(lv.task.isin(FOUR)) & ((lv.encoder == 'uni_v2') | (lv.task == 'ACS_STATES')) & (lv.scale.isin(PRIMARY))
       & (lv.estimand == 'theta3') & (lv.n.isin([4, 8, 16]))]
wr(order(h), 'r07c_limits_four_tasks_theta3.csv')
ld = pd.read_csv(os.path.join(F2c, 'aggregate_limits/f2_limits_diag.csv'))
wr(ld.groupby(['arm', 'n'])[['median_lam_mean', 'median_frac_lam0', 'median_frac_lam1', 'median_boot_drop']].median().reset_index(),
   'r07d_limits_lambda_by_n.csv')

# ---------------------------------------------------------------- regime B
rb = pd.read_csv(os.path.join(F2c, 'aggregate_regimeB/f2_regimeB_summary.csv'))
rows = []
for (grp, form), g in rb.assign(group=np.where(rb.task.isin(CORPUS), 'corpus', 'HEST_ACS')).groupby(['group', 'form']):
    rows.append({'group': grp, 'form': form, 'cells': len(g), 'ev_min': g.median_ev_over_var.min(),
                 'ev_median': g.median_ev_over_var.median(), 'ev_max': g.median_ev_over_var.max(),
                 'cov_min': g.median_coverage.min(), 'cov_median': g.median_coverage.median(), 'cov_max': g.median_coverage.max(),
                 'noint_max': g.median_frac_no_interval.max()})
for form, g in rb.groupby('form'):
    rows.append({'group': 'all', 'form': form, 'cells': len(g), 'ev_min': g.median_ev_over_var.min(),
                 'ev_median': g.median_ev_over_var.median(), 'ev_max': g.median_ev_over_var.max(),
                 'cov_min': g.median_coverage.min(), 'cov_median': g.median_coverage.median(), 'cov_max': g.median_coverage.max(),
                 'noint_max': g.median_frac_no_interval.max()})
wr(pd.DataFrame(rows), 'r08_regimeB_ranges.csv')
evt = rb.groupby(['task', 'estimand', 'form']).median_ev_over_var.agg(['count', 'min', 'median', 'max']).reset_index()
wr(order(evt), 'r08b_regimeB_ev_by_task.csv')
sel = rb[((rb.encoder == 'uni_v2') | (rb.task == 'ACS_STATES')) & rb.scale.isin(PRIMARY)]
p = sel.pivot_table(index=['task', 'estimand', 'm'], columns='form',
                    values=['median_coverage', 'median_width', 'median_ev_over_var']).reset_index()
p.columns = ['__'.join([x for x in col if x]) for col in p.columns]
wr(order(p), 'r08c_regimeB_uni_v2_primary.csv')
fr7 = []
for t, g in rb[(rb.form == 'C_fix1') & (rb.m >= 6)].groupby('task'):
    i = (g.median_coverage - 0.9).abs().idxmax()
    fr7.append({'task': t, 'cells': len(g), 'cov_min': g.median_coverage.min(), 'cov_max': g.median_coverage.max(),
                'max_abs_dev': (g.median_coverage - 0.9).abs().max(),
                'cell_of_max_dev': '|'.join(str(rb.loc[i, k]) for k in ['encoder', 'scale', 'estimand', 'm'])})
wr(order(pd.DataFrame(fr7)), 'r08d_regimeB_fr7_preview.csv')

# ---------------------------------------------------------------- F2.5 to F2.8
sf = pd.read_csv(os.path.join(F2c, 'diagnostics/f2_shortfall.csv'))
s8 = order(prim(enc_ok(sf))[lambda d: (d.n == 8) & d.estimand.isin(['theta3', 'mu'])])
wr(s8, 'r09_shortfall_uni_v2_primary_n8.csv')
rho = [c for c in sf.columns if c.startswith('rho_')]
rows = []
for grp, g in sf.assign(group=np.where(sf.task.isin(CORPUS), 'corpus', 'HEST_ACS')).groupby('group'):
    r = {'group': grp, 'cells': len(g)}
    for c in rho:
        r[f'{c}__median'] = g[c].median(); r[f'{c}__share_negative'] = (g[c] < 0).mean(); r[f'{c}__count'] = g[c].notna().sum()
    d = g.dropna(subset=['median_cov_fix1__beyond_sup_False', 'median_cov_fix1__beyond_sup_True'])
    r['cells_with_both_groups'] = len(d)
    r['median_cov_gap_not_beyond_minus_beyond'] = (d['median_cov_fix1__beyond_sup_False'] - d['median_cov_fix1__beyond_sup_True']).median()
    r['share_cells_beyond_lower'] = (d['median_cov_fix1__beyond_sup_True'] < d['median_cov_fix1__beyond_sup_False']).mean()
    rows.append(r)
wr(pd.DataFrame(rows), 'r09b_shortfall_correlations.csv')

by = pd.read_csv(os.path.join(F2c, 'diagnostics/f2_buy.csv'))
wr(order(prim(enc_ok(by))[lambda d: (d.n == 8) & d.estimand.isin(['theta3', 'mu'])]), 'r10_buy_uni_v2_primary_n8.csv')
d9 = pd.read_csv(os.path.join(F2c, 'diagnostics/f2_d9.csv'))
d9s = d9.groupby(['task', 'encoder', 'scale']).d9_ratio.agg(
    genes='count', median='median', q10=lambda x: x.quantile(.1), q90=lambda x: x.quantile(.9)).reset_index()
wr(order(d9s), 'r10b_d9_by_task.csv')

sd = pd.read_csv(os.path.join(F2c, 'diagnostics/f2_scale_diff.csv'))
s = sd[(sd.encoder == 'uni_v2') & (sd.n == 8) & sd.estimand.isin(['theta3', 'mu']) & sd.arm.isin(['fix1', 'classical', 'xf2'])]
wr(order(s), 'r11_scale_diff_uni_v2_n8.csv')
rows = []
for (o, a), g in sd.groupby(['other_scale', 'arm']):
    rows.append({'other_scale': o, 'arm': a, 'cells': len(g), 'd_cov_min': g.d_cov_other_minus_log1p.min(),
                 'd_cov_median': g.d_cov_other_minus_log1p.median(), 'd_cov_max': g.d_cov_other_minus_log1p.max(),
                 'median_width_ratio_other_to_log1p': (g.width_other / g.width_log1p).median()})
wr(pd.DataFrame(rows), 'r11b_scale_diff_ranges.csv')
pcs = pd.read_csv(os.path.join(F2c, 'diagnostics/f2_pc1_share.csv'))
wr(pcs, 'r11c_pc1_share.csv')

sp = pd.read_csv(os.path.join(F2c, 'diagnostics/f2_superpop.csv'))
wr(order(prim(enc_ok(sp))[lambda d: d.task.isin(FOUR) & d.estimand.isin(['theta3', 'mu'])]), 'r12_superpop_four_tasks.csv')

# ---------------------------------------------------------------- P10.1 part 1 with round 7's rows beside
sc = pd.read_csv(os.path.join(F2c, 'aggregate/f2_scores.csv'))
p10 = sc[sc.prediction == 'P10.1'][['task', 'coverage_r10', 'coverage_r5', 'drop']].copy()
r7 = pd.read_csv(os.path.join(clone, 'results/round7/ppi/S5_numbers/run1/s5_matched_cells.csv'))
r7 = r7[(r7.arm == 'uni_v2') & (r7.estimand == 'theta3') & (r7.n_L == 8) & (r7.design == 'D0_tuned') & (r7.domain == 'tissue')]
for pa in [0.01, 0.1]:
    m = r7[np.isclose(r7.p_a, pa)].set_index('vtag').coverage
    p10[f'coverage_r7_pa{pa}'] = p10.task.map(m)
h = ra[(ra.encoder == 'uni_v2') & (ra.scale == 'log1p') & (ra.estimand == 'theta3') & (ra.n == 8)]
for av in ['xf2_r5|V_max', 'xf2_r5|V', 'fix1|fpc', 'classical|fpc']:
    p10[f'cov_r10__{av}'] = p10.task.map(h[h.av == av].set_index('task').median_coverage)
wr(p10, 'r13_p10_1.csv')

json.dump({'log': log}, open(os.path.join(out, 'report_tables_log.json'), 'w'), indent=1)
print('done')
