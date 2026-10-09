"""Merge of the E3a masking result files (no estimation): concatenates the 20 per-(task, arm) CSVs,
checks them against round 4's q4a_table61.csv and writes acceptance and score tables.
Run: python merge_e3a_masking.py <E3a_crossfit dir> <q4a_table61.csv>"""
import glob, os, sys
import numpy as np, pandas as pd

B, Q = sys.argv[1], sys.argv[2]
KEY = ["vtag", "arm", "estimand", "population", "target", "interval", "lambda_rule", "n_L"]
COLS = ["emp_var_median", "coverage_median", "est_var_over_emp_var_median", "lambda_median", "emp_var_ratio_median"]
LIN, XF, CL = "textbook_t|fpc|lin", "textbook_t|fpc|lin|xf", "textbook_t|fpc"
d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(B + "masking/*/e3a_masking__*.csv"))], ignore_index=True)
d.to_csv(B + "e3a_masking.csv", index=False)
q = pd.read_csv(Q)
acc = []
# (a)
for itv in (LIN, CL):
    a = d[(d.interval == itv) & (d.population == "donor") & (d.target == "design")]
    m = a.merge(q, on=KEY, how="left", suffixes=("", "_q4a"), indicator=True)
    un = (m["_merge"] != "both").sum()
    mm = m[m["_merge"] == "both"]
    for c in COLS:
        x, y = mm[c].to_numpy(float), mm[c + "_q4a"].to_numpy(float)
        both_nan = np.isnan(x) & np.isnan(y)
        ad = np.where(both_nan, 0, np.abs(x - y)); ad = np.where(np.isnan(ad), np.inf, ad)
        rel = np.where(both_nan, 0, ad / np.maximum(np.abs(y), 1e-300)); rel = np.where(np.isnan(rel), np.inf, rel)
        tol_ok = (ad.max() <= 0.005) if c == "coverage_median" else (rel.max() <= 1e-5)
        if c in ("lambda_median",): tol_ok = rel.max() <= 1e-5 or ad.max() <= 1e-9
        acc.append(dict(check="a_reproduce_q4a", interval=itv, column=c, rows=len(a), matched=len(mm), unmatched=int(un),
                        max_abs_diff=float(ad.max()), max_rel_diff=float(rel.max()),
                        tolerance="0.005 abs" if c == "coverage_median" else "1e-5 rel", passed=bool(tol_ok and un == 0)))
# (b)
k2 = [k for k in KEY if k != "interval"]
l = d[(d.interval == LIN) & (d.lambda_rule == "none")].set_index(k2)
x = d[(d.interval == XF) & (d.lambda_rule == "none")].set_index(k2).loc[l.index]
cols = [c for c in d.columns if c not in KEY and c != "xf_extra_over_lin_var_median"]
for c in cols:
    u, v = l[c].to_numpy(float) if l[c].dtype != object else l[c].to_numpy(), x[c].to_numpy(float) if x[c].dtype != object else x[c].to_numpy()
    same = np.all((u == v) | (pd.isna(u) & pd.isna(v)))
    acc.append(dict(check="b_none_xf_equals_lin", interval=XF, column=c, rows=len(l), matched=len(l), unmatched=0,
                    max_abs_diff=float(np.nanmax(np.abs(u.astype(float) - v.astype(float)))) if l[c].dtype != object else 0.0,
                    max_rel_diff=np.nan, tolerance="identical", passed=bool(same)))
ex = x["xf_extra_over_lin_var_median"]
acc.append(dict(check="b_none_xf_equals_lin", interval=XF, column="xf_extra_over_lin_var_median", rows=len(x), matched=len(x), unmatched=0,
                max_abs_diff=float(np.nanmax(np.abs(ex))) if ex.notna().any() else 0.0, max_rel_diff=np.nan, tolerance="== 0 (extra term)",
                passed=bool((ex.fillna(0) == 0).all())))
# (c) skipped cells
sk = []
for (v, g), _ in d.groupby(["vtag", "G"]):
    for n in (6, 8, 12, 16):
        if n not in set(d[d.vtag == v].n_L): sk.append(f"{v}: n_L={n} skipped (n_L > G-2 = {int(g) - 2}; G={int(g)})")
acc.append(dict(check="c_skipped_cells", interval="", column="; ".join(sk), rows=len(d), matched=np.nan, unmatched=np.nan,
                max_abs_diff=np.nan, max_rel_diff=np.nan, tolerance="", passed=True))
pd.DataFrame(acc).to_csv(B + "e3a_masking_acceptance.csv", index=False)
# scores
rows = []
cl = d[(d.lambda_rule == "none") & (d.interval == LIN)].set_index(k2)
sel = d[d.lambda_rule == "c_crossfit_design"]
key3 = ["vtag", "arm", "estimand", "n_L"]
M = lambda df, s: df.set_index(key3)[["coverage_median", "est_var_over_emp_var_median", "width_ratio_median"]].add_suffix(s)
t = M(cl.reset_index(), "__classical_none_lin")
for itv, nm in ((LIN, "cf_lin"), (XF, "cf_lin_xf"), (CL, "cf_nolin")):
    t = t.join(M(sel[sel.interval == itv], "__" + nm))
t = t.reset_index()
t["cov_diff_xf_minus_classical"] = t["coverage_median__cf_lin_xf"] - t["coverage_median__classical_none_lin"]
t["within_0.015"] = t["cov_diff_xf_minus_classical"].abs() <= 0.015
t.to_csv(B + "e3a_masking_scores.csv", index=False)
print("done", len(d), len(acc))
