"""Round 10, track final-runs, F3 open point 1 (plan, section 5d.6 item 1): the limits summaries of the F2 report's
section 6.4, with and without the cells where exactly one cluster is unlabelled (G - n_L = 1).

usage: round10_final_runs_f3_reruns_limits_g1.py <clone> <out_dir>
Reads the committed F2 limits aggregates under <clone>/results/round10/final_runs/F2/aggregate_limits/
(f2_limits_summary.csv, f2_limits_vs_regimeA.csv, f2_limits_diag.csv) and recomputes the tables r07, r07b, r07c and
r07d with the code of round10_final_runs_f2_report_tables.py (its lines 167 to 189, copied unchanged into `tables`).
Scope `all` keeps every cell and is the anchor: its four tables are compared with the committed report tables in
<clone>/results/round10/final_runs/F2/report_tables/, byte for byte and value by value.
Scope `noG1` drops every (task, encoder, scale, estimand, n) cell with G - n = 1 before the summaries, G being joined
from f2_limits_summary.csv on those five keys (G differs by estimand).
Writes f3_limits_g1_summary.json first, then r07*__all.csv, r07*__noG1.csv, f3_limits_g1_dropped_cells.csv and
f3_limits_g1_compare.csv (the two scopes side by side for r07 and r07b).
"""
import hashlib, json, os, sys
import numpy as np
import pandas as pd

clone, out = sys.argv[1:3]
os.makedirs(out, exist_ok=True)
F2c = os.path.join(clone, 'results/round10/final_runs/F2')
HEST = ['CCRCC', 'CCRCC_merged', 'INDIANA_KIDNEY', 'LUNG_XENIUM']
FOUR = ['CCRCC', 'INDIANA_KIDNEY', 'LUNG_XENIUM', 'ACS_STATES']
CORPUS = ['kidney__Visium', 'breast__Spatial_Transcriptomics', 'bowel__Visium', 'brain__Visium',
          'breast__Xenium', 'lung__Xenium']
TASKS = HEST + ['ACS_STATES'] + CORPUS
PRIMARY = {'log1p', 'log_income'}
K = ['task', 'encoder', 'scale', 'estimand', 'n']
summ = dict(script='round10_final_runs_f3_reruns_limits_g1.py', clone=clone)
sp = os.path.join(out, 'f3_limits_g1_summary.json')
json.dump(summ, open(sp, 'w'), indent=1)


def order(df):
    df = df.copy(); df['_o'] = df.task.map({t: i for i, t in enumerate(TASKS)})
    return df.sort_values([c for c in ['_o', 'estimand', 'n', 'm'] if c in df.columns]).drop(columns='_o')


def tables(lm, lv, ld):
    """Lines 167 to 189 of round10_final_runs_f2_report_tables.py, unchanged except that the tables are returned."""
    res = {}
    lm = lm.copy()
    lm['av'] = lm.arm + '|' + lm.variance
    rows = []
    for (av, n), g in lm.groupby(['av', 'n']):
        rows.append({'arm': av, 'n': n, 'cells': len(g), 'min': g.median_coverage.min(), 'median': g.median_coverage.median(),
                     'max': g.median_coverage.max(), 'median_frac_no_interval': g.median_frac_no_interval.median()})
    res['r07_limits_ranges'] = pd.DataFrame(rows)
    wcols = [c for c in lv.columns if c.startswith('median_width_ratio_to_classical__')]
    rows = []
    for n, g in lv.groupby('n'):
        r = {'n': n, 'cells': len(g)}
        for c in wcols:
            r[c.replace('median_width_ratio_to_classical__', 'wr__')] = g[c].median()
        rows.append(r)
    res['r07b_limits_width_ratio_by_n'] = pd.DataFrame(rows)
    h = lv[(lv.task.isin(FOUR)) & ((lv.encoder == 'uni_v2') | (lv.task == 'ACS_STATES')) & (lv.scale.isin(PRIMARY))
           & (lv.estimand == 'theta3') & (lv.n.isin([4, 8, 16]))]
    res['r07c_limits_four_tasks_theta3'] = order(h)
    res['r07d_limits_lambda_by_n'] = ld.groupby(['arm', 'n'])[['median_lam_mean', 'median_frac_lam0', 'median_frac_lam1',
                                                               'median_boot_drop']].median().reset_index()
    return res


md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
lm = pd.read_csv(os.path.join(F2c, 'aggregate_limits/f2_limits_summary.csv'))
lv = pd.read_csv(os.path.join(F2c, 'aggregate_limits/f2_limits_vs_regimeA.csv'))
ld = pd.read_csv(os.path.join(F2c, 'aggregate_limits/f2_limits_diag.csv'))
summ['inputs_md5'] = {n: md5(os.path.join(F2c, 'aggregate_limits', n)) for n in
                      ['f2_limits_summary.csv', 'f2_limits_vs_regimeA.csv', 'f2_limits_diag.csv']}
# G per cell, from the summary
Gk = lm[K + ['G']].drop_duplicates()
assert not Gk.duplicated(K).any(), 'G is not unique within a cell'
cells = Gk.assign(G_minus_n=Gk.G - Gk.n)
drop = cells[cells.G_minus_n == 1]
summ['cells'] = int(len(cells)); summ['cells_G_minus_n_eq_1'] = int(len(drop))
drop.sort_values(K).to_csv(os.path.join(out, 'f3_limits_g1_dropped_cells.csv'), index=False)


def keep(df):
    m = df.merge(Gk, on=K, how='left', suffixes=('', '_cell'))
    gcol = 'G_cell' if 'G_cell' in m.columns else 'G'
    assert m[gcol].notna().all(), 'a cell without G'
    assert len(m) == len(df)
    return df[(m[gcol] - m.n).to_numpy() != 1]


# the anchor: scope all against the committed report tables
anchor = {}
res_all = tables(lm, lv, ld)
for name, df in res_all.items():
    p = os.path.join(out, f'{name}__all.csv'); df.to_csv(p, index=False)
    ref = os.path.join(F2c, 'report_tables', f'{name}.csv')
    r = pd.read_csv(ref); x = pd.read_csv(p)
    same_shape = r.shape == x.shape and list(r.columns) == list(x.columns)
    maxd = np.nan
    if same_shape:
        num = [c for c in r.columns if pd.api.types.is_numeric_dtype(r[c])]
        oth = [c for c in r.columns if c not in num]
        eq_other = bool((r[oth].astype(str).to_numpy() == x[oth].astype(str).to_numpy()).all()) if oth else True
        a, b = r[num].to_numpy(float), x[num].to_numpy(float)
        nan_same = bool((np.isnan(a) == np.isnan(b)).all())
        maxd = float(np.nanmax(np.abs(a - b))) if np.isfinite(a).any() else 0.0
    else:
        eq_other = nan_same = False
    anchor[name] = dict(ref_md5=md5(ref), ours_md5=md5(p), bytes_identical=md5(ref) == md5(p), shape_ref=list(r.shape),
                        shape_ours=list(x.shape), same_columns=same_shape, non_numeric_equal=eq_other,
                        nan_pattern_equal=nan_same, max_abs_diff=maxd)
# the two named anchor rows of the plan
r07 = res_all['r07_limits_ranges']; rk = r07[(r07.arm == 'kluger_ptd|cluster_boot') & (r07.n == 16)]
r07b = res_all['r07b_limits_width_ratio_by_n']; rb = r07b[r07b.n == 4]
anchor['named_rows'] = dict(
    r07_kluger_n16=rk[['cells', 'min', 'median', 'max', 'median_frac_no_interval']].iloc[0].tolist() if len(rk) == 1 else None,
    r07_kluger_n16_expected=[212, 0.22725, 0.95425, 0.98875, 0.0],
    r07b_n4=[int(rb.cells.iloc[0]), float(rb['wr__kluger_ptd|cluster_boot'].iloc[0])] if len(rb) == 1 else None,
    r07b_n4_expected=[242, 0.5763047452681511])
ok = all(v['bytes_identical'] for k, v in anchor.items() if k != 'named_rows')
anchor['pass'] = bool(ok and anchor['named_rows']['r07_kluger_n16'] == anchor['named_rows']['r07_kluger_n16_expected']
                      and anchor['named_rows']['r07b_n4'] == anchor['named_rows']['r07b_n4_expected'])
summ['anchor'] = anchor
json.dump(summ, open(sp, 'w'), indent=1, default=str)
print(json.dumps(anchor, indent=1, default=str), flush=True)
if not anchor['pass']:
    print('ANCHOR FAILED: the filtered tables are not written'); sys.exit(2)

# scope noG1
lm_f, lv_f, ld_f = keep(lm), keep(lv), keep(ld)
summ['rows_dropped'] = dict(summary=int(len(lm) - len(lm_f)), vs_regimeA=int(len(lv) - len(lv_f)), diag=int(len(ld) - len(ld_f)))
res_f = tables(lm_f, lv_f, ld_f)
for name, df in res_f.items():
    df.to_csv(os.path.join(out, f'{name}__noG1.csv'), index=False)
# side by side
c = res_all['r07_limits_ranges'].merge(res_f['r07_limits_ranges'], on=['arm', 'n'], how='outer', suffixes=('__all', '__noG1'))
c.to_csv(os.path.join(out, 'f3_limits_g1_compare_r07.csv'), index=False)
cb = res_all['r07b_limits_width_ratio_by_n'].merge(res_f['r07b_limits_width_ratio_by_n'], on='n', how='outer', suffixes=('__all', '__noG1'))
cb.to_csv(os.path.join(out, 'f3_limits_g1_compare_r07b.csv'), index=False)
changed = c[(c['cells__all'] != c['cells__noG1'])]
summ['r07_rows_changed'] = int(len(changed))
summ['r07c_rows'] = dict(all=int(len(res_all['r07c_limits_four_tasks_theta3'])), noG1=int(len(res_f['r07c_limits_four_tasks_theta3'])))
summ['finished'] = True
json.dump(summ, open(sp, 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in summ.items() if k != 'anchor'}, indent=1, default=str))
