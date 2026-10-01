
import sys, json, math
import pandas as pd, numpy as np
new_p, old_p, out_csv, out_json = sys.argv[1:5]
TOL = 1e-10
new = pd.read_csv(new_p); old = pd.read_csv(old_p)
old_all = old
old = old[old.variant == "CCRCC"].copy()
key = ["check", "variant", "estimand", "population", "arm"]
for d in (new, old):
    d["k"] = d.groupby(key).cumcount()
    d["n_L"] = d["detail"].str.extract(r"n_L=(\d+)")[0]
m = old.merge(new, on=key + ["k"], how="outer", suffixes=("_committed", "_rerun"), indicator=True)
def diff(r):
    a, b = r["value_committed"], r["value_rerun"]
    if pd.isna(a) and pd.isna(b): return 0.0
    if pd.isna(a) or pd.isna(b): return float("inf")
    return abs(a - b)
m["abs_diff"] = m.apply(diff, axis=1)
m["agree_1e-10"] = (m["_merge"] == "both") & (m["abs_diff"] <= TOL)
m["n_L_match"] = m["n_L_committed"].fillna("") == m["n_L_rerun"].fillna("")
m["passed_committed"] = m["passed_committed"]; 
cols = key + ["k", "n_L_committed", "n_L_rerun", "value_committed", "value_rerun", "abs_diff", "agree_1e-10",
              "tol_committed", "tol_rerun", "passed_committed", "passed_rerun", "evaluable_committed",
              "evaluable_rerun", "detail_committed", "detail_rerun", "_merge"]
m = m[cols].rename(columns={"_merge": "row_presence"})
m.to_csv(out_csv, index=False)
both = m[m.row_presence == "both"]
unc = old_all[old_all.variant != "CCRCC"]
summ = dict(
    n_committed_CCRCC_rows=int(len(old)), n_rerun_rows=int(len(new)),
    n_compared=int(len(both)), n_only_committed=int((m.row_presence == "left_only").sum()),
    n_only_rerun=int((m.row_presence == "right_only").sum()),
    n_agree=int(both["agree_1e-10"].sum()), n_disagree=int((~both["agree_1e-10"]).sum()),
    max_abs_diff=float(both["abs_diff"].max()) if len(both) else None,
    all_agree=bool(len(both) > 0 and both["agree_1e-10"].all() and (m.row_presence == "both").all()),
    n_L_all_match=bool(both["n_L_committed"].fillna("").eq(both["n_L_rerun"].fillna("")).all()),
    passed_flag_mismatch=int((both["passed_committed"] != both["passed_rerun"]).sum()),
    by_check_max_abs_diff={k: float(v) for k, v in both.groupby("check")["abs_diff"].max().items()},
    by_check_n={k: int(v) for k, v in both.groupby("check").size().items()},
    committed_rows_not_covered=int(len(unc)),
    not_covered_variants={k: int(v) for k, v in unc.groupby("variant").size().items()},
    tol=TOL)
json.dump(summ, open(out_json, "w"), indent=1)
print(json.dumps(summ, indent=1))
