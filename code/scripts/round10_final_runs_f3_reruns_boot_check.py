"""Round 10, track final-runs, F3 open point 3: the check of a bootstrap rerun of a regime A unit or part.

usage: round10_final_runs_f3_reruns_boot_check.py <new regimeA_cells.parquet> <F2 regimeA_cells.parquet> <out_dir> [<uni_v2 sibling regimeA_cells.parquet>]
Every row of the new file whose variance is not `boot` must equal the F2 row of the same population, n_L, arm and
variance, in every column (NaN equal to NaN), and every F2 row of the populations the new file covers must be
present. The bootstrap rows are counted (three arms for each population of theta3, theta2 or mu and each n_L).
With a uni_v2 sibling, a preview table puts each bootstrap arm's median coverage over genes beside uni_v2's, per
(scale, estimand, n_L, arm). Writes boot_check.json and boot_preview.csv.
"""
import json, os, sys
import numpy as np, pandas as pd

newp, f2p, out = sys.argv[1:4]; sib = sys.argv[4] if len(sys.argv) > 4 else None
os.makedirs(out, exist_ok=True)
KEYS = ['task', 'encoder', 'scale', 'estimand', 'gene', 'n', 'arm', 'variance']
N = pd.read_parquet(newp); F = pd.read_parquet(f2p)
pops = N[['task', 'encoder', 'scale', 'estimand', 'gene']].drop_duplicates()
F = F.merge(pops, on=['task', 'encoder', 'scale', 'estimand', 'gene'])
A = N[N.variance != 'boot']; Bt = N[N.variance == 'boot']
chk = dict(new_rows=len(N), new_analytic_rows=len(A), new_boot_rows=len(Bt), f2_rows_same_populations=len(F),
           f2_boot_rows=int((F.variance == 'boot').sum()))
a = A.sort_values(KEYS).reset_index(drop=True); f = F.sort_values(KEYS).reset_index(drop=True)
chk['same_row_count'] = len(a) == len(f)
if chk['same_row_count']:
    keys_eq = bool((a[KEYS].astype(str).to_numpy() == f[KEYS].astype(str).to_numpy()).all())
    num = [c for c in a.columns if c not in KEYS and pd.api.types.is_numeric_dtype(a[c])]
    x, y = a[num].to_numpy(float), f[num].to_numpy(float)
    same = (x == y) | (np.isnan(x) & np.isnan(y))
    chk.update(keys_equal=keys_eq, columns_compared=num, cells_differing=int((~same).sum()),
               max_abs_diff=float(np.nanmax(np.where(same, 0, np.abs(x - y)))) if (~same).any() else 0.0)
    chk['analytic_identical'] = bool(keys_eq and (~same).sum() == 0)
else:
    chk['analytic_identical'] = False
bp = Bt[['task', 'encoder', 'scale', 'estimand', 'gene', 'n']].drop_duplicates()
exp = A[A.estimand.isin(['theta3', 'theta2', 'mu'])][['task', 'encoder', 'scale', 'estimand', 'gene', 'n']].drop_duplicates()
chk.update(boot_cells=len(bp), boot_cells_expected=len(exp), boot_arms=sorted(Bt.arm.unique().tolist()),
           boot_rows_expected=3 * len(exp), boot_complete=bool(len(Bt) == 3 * len(exp) and len(bp) == len(exp)))
chk['pass'] = bool(chk['analytic_identical'] and chk['boot_complete'])
if sib:
    U = pd.read_parquet(sib); U = U[U.variance == 'boot']
    k = ['scale', 'estimand', 'n', 'arm']
    p1 = Bt.groupby(k).agg(genes=('gene', 'size'), median_coverage=('coverage', 'median'), median_width=('median_width', 'median')).reset_index()
    p2 = U.groupby(k).agg(genes_uni_v2=('gene', 'size'), median_coverage_uni_v2=('coverage', 'median'), median_width_uni_v2=('median_width', 'median')).reset_index()
    P = p1.merge(p2, on=k, how='left'); P['d_cov_vs_uni_v2'] = P.median_coverage - P.median_coverage_uni_v2
    P.to_csv(os.path.join(out, 'boot_preview.csv'), index=False)
    chk['preview_cells'] = len(P); chk['preview_share_within_002'] = float((P.d_cov_vs_uni_v2.abs() <= 0.02).mean())
json.dump(chk, open(os.path.join(out, 'boot_check.json'), 'w'), indent=1, default=str)
print(json.dumps(chk, indent=1, default=str))
sys.exit(0 if chk['pass'] else 2)
