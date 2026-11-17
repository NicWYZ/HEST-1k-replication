# Independent recomputation of Part B numbers (B3, B4, B5, B6, B7) and B1 table rows read from stored files.
import numpy as np, pandas as pd
R = '/work/users/w/e/weiyang/hest_replication/results/'
C = R + 'round11/closeout/'
I = C + 'g2check/inputs/results/'   # repository copies of files not present on Longleaf
inputs = []
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.precision', 17)


def rd(p):
    inputs.append(p)
    return pd.read_csv(p)


print('=== B3')
g = rd(C + 'b3/s0006_v1/b3_by_gene.csv')
print('rows', len(g), g.groupby(['encoder', 'scale', 'center']).size().describe().to_dict())
g['abs_bias_over_q'] = g.bias.abs() / g.q
agg = g.groupby(['encoder', 'scale', 'center']).agg(cov=('cov', 'median'), q=('q', 'median'), q_own=('q_own', 'median'),
                                                    med_abs=('med_abs', 'median'), abs_bias_over_q=('abs_bias_over_q', 'median'),
                                                    cov_centered=('cov_centered', 'median'), genes=('gene', 'nunique'))
print(agg.to_string())
u = agg.loc[('uni_v2', 'lognorm')]
print('uni_v2 lognorm S0006 q', u.loc['S0006', 'q'], '; others min', u.drop('S0006').q.min(), 'max', u.drop('S0006').q.max(),
      '; S0006 smallest:', u.q.idxmin())
print('S0006 cov', u.loc['S0006', 'cov'], 'cov_centered', u.loc['S0006', 'cov_centered'], 'diff', u.loc['S0006', 'cov_centered'] - u.loc['S0006', 'cov'])
print('S0006 q_own', u.loc['S0006', 'q_own'], 'abs_bias_over_q', u.loc['S0006', 'abs_bias_over_q'])
print('S0249 med_abs', u.loc['S0249', 'med_abs'], 'cov', u.loc['S0249', 'cov'], '; med_abs rank (desc):', u.med_abs.sort_values(ascending=False).index.tolist())
# check (a): reproduce round 10 inst_by_center hcp_donor alpha 0.2 coverage_median_gene from by-gene cov
ib = rd(R + 'round10/final_runs/F3/institution/production/inst_by_center.csv')
ib = ib[(ib.arm == 'hcp_donor') & (np.isclose(ib.alpha, 0.2))].set_index(['encoder', 'scale', 'center_unit']).coverage_median_gene
j = agg['cov'].rename_axis(['encoder', 'scale', 'center_unit'])
common = ib.index.intersection(j.index)
print('B3(a) rows compared', len(common), 'of inst rows', len(ib), 'max abs diff', float((ib.loc[common] - j.loc[common]).abs().max()))

print('=== B4')
b = rd(C + 'b4/equal_v2/b4_comparisons.csv')
for (al, est), d in b.groupby(['alloc', 'estimand']):
    print(al, est, 'n', len(d), 'B narrower', int((d.ratio_mean_width < 1).sum()), 'median ratio', d.ratio_mean_width.median(),
          'cov_B min', d.coverage_B.min(), 'max', d.coverage_B.max(), 'recomputed ratio maxdiff', float((d.mean_width_B / d.mean_width_A - d.ratio_mean_width).abs().max()))
an = rd(C + 'b4/equal_v2/b4_anchor.csv')
print('B4 anchor rows', len(an), 'merge', an._merge.value_counts().to_dict(), 'max abs diff', an.max_abs_diff.max())

print('=== B5')
bg = rd(C + 'b5/withinvar_v1/b5_by_gene.csv')
t = bg.groupby(['task', 'estimand']).agg(genes=('gene', 'nunique'), factor_equal=('factor_equal_var', 'median'), factor_meas=('factor_measured', 'median'),
                                         ratio=('ratio_measured_over_equal', 'median'), cv=('cv_V', 'median'), maxmin=('max_over_min_V', 'median'))
print(t.to_string())
hest = t.drop('ACS_STATES', level=0)
print('HEST theta3 maxmin range', hest.xs('theta3', level=1).maxmin.min(), hest.xs('theta3', level=1).maxmin.max())
print('HEST theta3 ratio range', hest.xs('theta3', level=1).ratio.min(), hest.xs('theta3', level=1).ratio.max(),
      '; both estimands', hest.ratio.min(), hest.ratio.max())
print('HEST max factor_meas (theta3)', hest.xs('theta3', level=1).factor_meas.max(), '; all estimands', hest.factor_meas.max())
print('all tasks maxmin > 3?', (t.maxmin > 3).to_dict())
cl = rd(C + 'b5/withinvar_v1/b5_clusters.csv')
rows = []
for (task, est, gene), d in cl.groupby(['task', 'estimand', 'gene']):
    M = d.M.to_numpy(float); V = d.V.to_numpy(float); Mb = M.mean(); G = len(M)
    rows.append(dict(task=task, estimand=est, gene=gene, G=G, f_eq=Mb * (1 / M).sum() / G, f_meas=Mb * (V / M).sum() / V.sum(),
                     maxmin=V.max() / V.min(), cv_ddof0=V.std(ddof=0) / V.mean(), cv_ddof1=V.std(ddof=1) / V.mean()))
cr = pd.DataFrame(rows).merge(bg, on=['task', 'estimand', 'gene'], how='left')
cr['d_eq'] = (cr.f_eq - cr.factor_equal_var).abs(); cr['d_meas'] = (cr.f_meas - cr.factor_measured).abs(); cr['d_mm'] = (cr.maxmin - cr.max_over_min_V).abs()
print(cr[['task', 'estimand', 'gene', 'G', 'f_eq', 'factor_equal_var', 'f_meas', 'factor_measured', 'maxmin', 'max_over_min_V', 'cv_ddof0', 'cv_ddof1', 'cv_V']].to_string())
print('max diffs: eq', cr.d_eq.max(), 'meas', cr.d_meas.max(), 'maxmin', cr.d_mm.max())

print('=== B6')
bh = rd(I + 'round9/between/between_head_by_gene.csv')
bh = bh[bh.design == 'lodo']
s = bh.groupby(['task', 'encoder']).apply(lambda d: pd.Series(dict(genes=d.gene.nunique(), rows=len(d), share=(d.R2_pooled > d.R2_constant).mean())))
print(s.to_string())
print('range over encoders/tasks', s.share.min(), s.share.max())
ab = rd(I + 'round9/fewcluster/strat/i32_acs_box.csv'); hb = rd(I + 'round9/fewcluster/strat/i32_hest_box_summary.csv'); rm = rd(I + 'round9/fewcluster/strat/i32_required_m_B.csv')
a1 = ab[ab['lambda'] == 1.0]
vals = [a1.m_min_B.iloc[0], a1.n_min_A.iloc[0]]
for tk in ['CCRCC', 'INDIANA_KIDNEY', 'LUNG_XENIUM']:
    h = hb[(hb.task == tk) & (hb['lambda'] == 1.0)]; assert len(h) == 1
    vals += [h.m_min_B_median.iloc[0], h.n_min_A_median.iloc[0]]
for L0 in [3, 8]:
    r = rm[(rm.N == 2000) & (rm.v0 == 1.0) & (rm.Lambda0 == L0)]; assert len(r) == 1, len(r)
    vals.append(r.m_min_B.iloc[0])
print('E1 values', vals)

print('=== B7')
j7 = rd(C + 'b7/ledger_v2/b7_round10_jobs.csv')
print('rows', len(j7), 'unique ids', j7.job_id.nunique())
nl = j7[~j7.in_ledger.astype(str).str.lower().eq('true')]
print('not in ledger', len(nl), 'states', nl.state.str.split().str[0].value_counts().to_dict(), 'with any provenance', int((nl.out_dirs_with_provenance > 0).sum()))

print('=== B1 rows from stored files')
d9 = rd(I + 'round10/final_runs/F2/report_tables/r10b_d9_by_task.csv'); d9 = d9[d9.scale == 'log1p']
pt = d9.groupby('task')['median'].agg(['min', 'max'])
print('H1(a) per-task medians (min/max over encoders):'); print(pt.to_string())
print('H1(a) min', d9.loc[d9['median'].idxmin(), ['task', 'encoder', 'median']].tolist(), 'max', d9.loc[d9['median'].idxmax(), ['task', 'encoder', 'median']].tolist())
bt = rd(C + 'b1/h1b_h4/b1_h1b_by_task.csv'); bt = bt[bt.score == 'abs']
for ls_idc in ['audited', 'shipped']:
    sel = bt[(bt.task != 'IDC') | (bt.label_set == ls_idc)]
    for des, d in sel.groupby('design'):
        print('H1(b) IDC', ls_idc, des, 'tasks', d.task.nunique(), 'cells', int(d.encoders.sum()), 'cell-weighted mean', float((d.coverage_mean * d.encoders).sum() / d.encoders.sum()))
cc = bt[(bt.task == 'CCRCC')]
print('H1(b) CCRCC', cc[['design', 'coverage_mean']].to_dict('records'))
fr = rd(R + 'round10/final_runs/F3/institution/production/inst_fr8.csv'); print(fr[['clause', 'arm', 'value', 'per_center']].to_string())
ib2 = rd(R + 'round10/final_runs/F3/institution/production/inst_by_center.csv')
for arm in ['hcp_donor', 'hcp_center']:
    x = ib2[(ib2.arm == arm) & np.isclose(ib2.alpha, 0.2) & (ib2.encoder == 'uni_v2') & (ib2.scale == 'log1p')].set_index('center_unit').coverage_median_gene
    print('H2', arm, x.to_dict(), 'median over centers', x.median())
a1b = rd(R + 'round3/A1_coverage/a1_vs_benchmark_pearson.csv')
col = 'benchmark_pca_ridge_avg_paper9'
print('H4 encoders', len(a1b), 'max', a1b[col].max(), a1b.loc[a1b[col].idxmax(), 'encoder'], 'min', a1b[col].min(), a1b.loc[a1b[col].idxmin(), 'encoder'], 'spread', a1b[col].max() - a1b[col].min())
dt = rd(R + 'round2/R3_splits/r3_decomposition_terms.csv')
tot = dt[dt.term.str.startswith('TOTAL')]['mean'].iloc[0]
print('H4 total random-patient', tot, 'ratio', tot / (a1b[col].max() - a1b[col].min()))
lim = rd(I + 'round10/final_runs/F2/report_tables/r07_limits_ranges.csv')
print('H5 kluger', lim[(lim.arm == 'kluger_ptd|cluster_boot') & (lim.n == 4)][['cells', 'median']].to_dict('records'))
gr = rd(I + 'round10/final_runs/F2/report_tables/r02_regimeA_grid_ranges.csv')
print('H5 bh', gr[(gr.arm.isin(['bh|own', 'bh_t|own'])) & (gr.n == 4)][['arm', 'group', 'cells', 'median']].to_dict('records'))
fp = rd(I + 'round10/final_runs/F1/aggregate/f1_predictions.csv')
print('H2 f1_predictions kidney', fp[fp.task == 'kidney__Visium'][['encoder', 'design', 'pearson_log1p_median']].to_dict('records'))
fd = rd(I + 'round10/final_runs/F1/aggregate/f1_d12.csv')
print('H3 f1_d12 kidney uni_v2', fd[(fd.name == 'kidney__Visium__uni_v2') & (fd.scale == 'log1p')][['R2_loo_const_median']].to_dict('records'))
buy = rd(I + 'round10/final_runs/F2/report_tables/r10_buy_uni_v2_primary_n8.csv')
print('round10 r10_buy theta3', buy[buy.estimand == 'theta3'][['task', 'median_wr_fix1', 'median_R2c', 'median_pearson_spot']].to_string())
open('inputs.txt', 'w').write('\n'.join(inputs) + '\n')
