"""Round 10, track final-runs, F3 open point 6: where the all-gene LUNG_XENIUM diagnostics of
round10_final_runs_f3_reruns_r9g42.py differ from the committed F2 diagnostics, column by column.

usage: round10_final_runs_f3_reruns_r9g42_diagcheck.py <clone> <r9g42_out_dir> <full_rerun_dir> <out_dir>
<full_rerun_dir> holds an unchanged rerun of round10_final_runs_f2_diagnostics.py on the committed f2_diagnostics_v2.json
(every task). For each diagnostics table and numeric column, on the LUNG_XENIUM rows, it gives the largest absolute and
relative difference between (a) the committed table and the LUNG-only scope `all`, (b) the committed table and the full
rerun, (c) the full rerun and scope `all`. If (b) is non-zero where (a) is, the differences come from the run itself
(node, library paths), not from restricting the inputs to LUNG_XENIUM; if (c) is zero, scope `all` reproduces a fresh
full run exactly. Writes r9g42_diagcheck.json and r9g42_diagcheck_columns.csv.
"""
import json, os, sys
import numpy as np, pandas as pd
clone, r9, full, out = sys.argv[1:5]; os.makedirs(out, exist_ok=True)
F2c = os.path.join(clone, 'results/round10/final_runs/F2/diagnostics')
T = 'LUNG_XENIUM'
TABLES = ['f2_shortfall.csv', 'f2_buy.csv', 'f2_superpop.csv', 'f2_scale_diff.csv', 'f2_pc1_share.csv', 'f2_d9.csv',
          'f2_anchor_r9_kappa.csv', 'f2_anchor_r9_c0.csv', 'f2_anchor_r9_pc1.csv']
KC = ['task', 'encoder', 'scale', 'estimand', 'n', 'gene', 'arm', 'other_scale', 'ref']
rd = lambda p: pd.read_csv(p, float_precision='round_trip')
def lung(d):
    return d[d.task == T] if 'task' in d.columns else d
def pair(a, b):
    keys = [k for k in KC if k in a.columns and k in b.columns]
    m = a.merge(b, on=keys, how='outer', suffixes=('_a', '_b'), indicator=True)
    res = {'unmatched': int((m._merge != 'both').sum())}
    for c in a.columns:
        if c in keys or c not in b.columns or not pd.api.types.is_numeric_dtype(a[c]):
            continue
        x, y = m[c + '_a'].to_numpy(float), m[c + '_b'].to_numpy(float)
        f = np.isfinite(x) & np.isfinite(y)
        d = np.abs(x - y)[f]
        res[c] = (float(d.max()) if d.size else 0.0,
                  float((d / np.maximum(np.abs(x[f]), 1e-300)).max()) if d.size else 0.0,
                  bool((np.isnan(x) == np.isnan(y)).all()))
    return res
rows, summ = [], {}
for t in TABLES:
    C = lung(rd(os.path.join(F2c, t))); A = lung(rd(os.path.join(r9, 'scope_all/diagnostics', t))); Fu = lung(rd(os.path.join(full, t)))
    s = {}
    for lab, (a, b) in {'committed_vs_scope_all': (C, A), 'committed_vs_full_rerun': (C, Fu), 'full_rerun_vs_scope_all': (Fu, A)}.items():
        p = pair(a, b); s[lab] = dict(unmatched=p.pop('unmatched'), max_abs=max([v[0] for v in p.values()] + [0.0]),
                                      max_rel=max([v[1] for v in p.values()] + [0.0]), nan_equal=all(v[2] for v in p.values()))
        for c, v in p.items():
            rows.append(dict(table=t, comparison=lab, column=c, max_abs_diff=v[0], max_rel_diff=v[1], nan_pattern_equal=v[2]))
    summ[t] = s
pd.DataFrame(rows).to_csv(os.path.join(out, 'r9g42_diagcheck_columns.csv'), index=False)
json.dump(summ, open(os.path.join(out, 'r9g42_diagcheck.json'), 'w'), indent=1)
print(json.dumps(summ, indent=1))
