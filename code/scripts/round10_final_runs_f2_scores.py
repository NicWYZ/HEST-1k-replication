"""Round 10, track final-runs, F2: scores of P10.1 (part 1) and FR2 to FR6 from the aggregation tables (plan, section 5.8).

usage: round10_final_runs_f2_scores.py <aggregate_dir> <e4b_grid.csv> <out_dir>
Writes f2_scores.csv, one row per clause, with the cell keys, the values read, and the clause's verdict.
The brief's defaults: HEST tasks CCRCC, INDIANA_KIDNEY, LUNG_XENIUM; estimand theta3; encoder uni_v2; scale log1p;
level 0.90. Each clause is also given for mu where the brief's prediction came from round 9's mu runs.
"""
import os, sys, json
import numpy as np, pandas as pd
agg, e4b, out = sys.argv[1:4]; os.makedirs(out, exist_ok=True)
S = pd.read_csv(os.path.join(agg, "f2_regimeA_summary.csv"))
W = pd.read_csv(os.path.join(agg, "f2_switch_rule.csv"))
C = pd.read_csv(os.path.join(agg, "f2_fix1_cost.csv"))
HEST = ["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM"]
rows = []
def get(task, arm, var, n, est="theta3", enc="uni_v2", scale="log1p", col="median_coverage"):
    x = S[(S.task == task) & (S.arm == arm) & (S.variance == var) & (S.n == n) & (S.estimand == est) & (S.encoder == enc) & (S.scale == scale)]
    return float(x[col].iloc[0]) if len(x) == 1 else np.nan
def add(pred, clause, ok, **v):
    rows.append(dict(prediction=pred, clause=clause, holds=None if ok is None else bool(ok), **{k: (round(x, 6) if isinstance(x, float) else x) for k, x in v.items()}))
# FR2
sw_min = W.median_ev_over_var.min()
add("FR2", "median E(V_w)/Var >= 0.95 in every cell n>=6", bool(sw_min >= 0.95), cells=len(W), min_median=float(sw_min))
for t in ["CCRCC", "INDIANA_KIDNEY"]:
    for est in ["theta3", "mu"]:
        x = W[(W.task == t) & (W.n == 6) & (W.encoder == "uni_v2") & (W.scale == "log1p") & (W.estimand == est)]
        v = float(x.median_frac_V_neg.iloc[0]) if len(x) else np.nan
        add("FR2", f"V < 0 in >= 0.05 of draws at n=6, {t}, {est}", v >= 0.05, task=t, estimand=est, median_frac_V_neg=v)
# FR3
for est in ["theta3", "mu"]:
    for t in HEST + ["ACS_STATES"]:
        enc, scale = ("pkg", "log_income") if t == "ACS_STATES" else ("uni_v2", "log1p")
        a = get(t, "fix1", "fpc", 4, est, enc, scale, "median_rmse"); b = get(t, "classical", "fpc", 4, est, enc, scale, "median_rmse")
        add("FR3", f"fix1 median RMSE below classical at n=4, {t}, {est}", a < b if np.isfinite(a) and np.isfinite(b) else None, task=t, estimand=est, rmse_fix1=a, rmse_classical=b)
# FR4
for est in ["theta3", "mu"]:
    for t, lo, hi in [("CCRCC", 0.3, None), ("INDIANA_KIDNEY", 0.3, None), ("LUNG_XENIUM", None, 0.2)]:
        x = C[(C.task == t) & (C.n == 8) & (C.encoder == "uni_v2") & (C.scale == "log1p") & (C.estimand == est)]
        v = float(x.share_fix1_wider_median.iloc[0]) if len(x) else np.nan
        ok = (v >= lo) if lo is not None else (v <= hi)
        add("FR4", f"share of genes with fix1 wider than classical at n=8, {t}, {est}", ok, task=t, estimand=est, share=v)
    x = C[(C.task == "ACS_STATES") & (C.n == 8) & (C.estimand == est)]
    v = float(x.share_fix1_wider_median.iloc[0]) if len(x) else np.nan
    add("FR4", f"ACS fix1 narrower than classical at n=8, {est}", v == 0.0 if np.isfinite(v) else None, task="ACS_STATES", estimand=est, share=v)
# FR5 (normalised scale here is round 9's pairing until the refit)
for est in ["theta3", "mu"]:
    a = get("CCRCC", "fix1", "fpc", 8, est, "uni_v2", "norm_r9pair"); b = get("CCRCC", "fix1", "fpc", 8, est, "uni_v2", "log1p")
    add("FR5", f"CCRCC fix1 coverage at n=8 higher by >= 0.02 on the normalised scale (round 9 pairing), {est}", (a - b) >= 0.02, estimand=est, cov_norm=a, cov_log1p=b, diff=a - b)
# FR6, coverage clause only (the frontier clause needs F2.5)
for est in ["theta3", "mu"]:
    for scale in ["log1p", "lognorm"]:
        a = get("kidney__Visium", "fix1", "fpc", 16, est, "uni_v2", scale)
        add("FR6", f"kidney Visium fix1 median coverage at n=16 below 0.88, {est}, {scale} (frontier clause not yet run)", a < 0.88, estimand=est, scale=scale, coverage=a)
# P10.1 part 1
E = pd.read_csv(e4b)
for t in HEST:
    ref = E[(E.vtag == t) & (E.arm == "uni_v2") & (E.estimand == "theta3") & (E.n_L == 8) & (E.design == "D0") & (E.rule == "c_crossfit_design") &
            (E.interval == "textbook_t|fpc|lin|xf") & (E.n_sub == 2000)]
    r5 = float(ref.coverage_median.iloc[0]) if len(ref) == 1 else np.nan
    a = get(t, "xf2_r5", "V_w", 8)
    add("P10.1", f"xf2_r5 with V_w at n=8 is 0.02 to 0.05 below round 5's coverage_median, {t}", 0.02 <= (r5 - a) <= 0.05, task=t, coverage_r10=a, coverage_r5=r5, drop=r5 - a, ref_rows=len(ref))
d = pd.DataFrame(rows); d.to_csv(os.path.join(out, "f2_scores.csv"), index=False)
print(d.to_string())
