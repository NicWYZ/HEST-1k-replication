"""Round 5 PPI, stage E0 item 3: compare an anchor rerun with the committed round-4 rows.

Tolerances (brief section 6, E0): 0.005 absolute on coverage columns, which is one draw of 200,
and 1e-5 relative on variance columns. Lambda columns are reported beside them without a
tolerance of their own. Rows are matched on every key column; an unmatched reference row is a
failure. Writes one row per compared column with the largest difference and the verdict.
"""
import argparse
import json

import numpy as np
import pandas as pd

COV = ["coverage_median"]
VAR = ["emp_var_median", "emp_var_ratio_median", "est_var_over_emp_var_median"]
OTHER = ["width_ratio_median", "lambda_median", "lambda_se_median", "lambda_raw_mean_median", "lambda_raw_mean_se_median"]


def compare(new, ref, keys, label):
    new = new.copy(); ref = ref.copy()
    for k in keys:
        new[k] = new[k].astype(str); ref[k] = ref[k].astype(str)
    dup_n, dup_r = new.duplicated(keys).sum(), ref.duplicated(keys).sum()
    m = ref.merge(new, on=keys, how="left", suffixes=("_ref", "_new"), indicator=True)
    unmatched = int((m["_merge"] != "both").sum())
    rows = []
    for col in COV + VAR + OTHER:
        if f"{col}_ref" not in m or f"{col}_new" not in m:
            continue
        a, b = m[f"{col}_ref"].astype(float).to_numpy(), m[f"{col}_new"].astype(float).to_numpy()
        both = np.isfinite(a) & np.isfinite(b)
        nan_mismatch = int((np.isfinite(a) != np.isfinite(b)).sum())
        absd = np.abs(a - b)[both]
        reld = (np.abs(a - b) / np.maximum(np.abs(a), 1e-300))[both]
        if col in COV:
            tol, kind, stat = 0.005, "abs", (absd.max() if absd.size else 0.0)
        elif col in VAR:
            tol, kind, stat = 1e-5, "rel", (reld.max() if reld.size else 0.0)
        else:
            tol, kind, stat = np.nan, "abs", (absd.max() if absd.size else 0.0)
        ok = (np.isnan(tol) or stat <= tol) and nan_mismatch == 0 and unmatched == 0
        rows.append(dict(anchor=label, column=col, n_ref_rows=len(ref), n_matched=int(both.sum()),
                         unmatched_ref_rows=unmatched, duplicate_keys_new=int(dup_n), duplicate_keys_ref=int(dup_r),
                         nan_mismatch=nan_mismatch, max_diff=float(stat), diff_kind=kind, tolerance=tol,
                         max_abs_diff=float(absd.max()) if absd.size else 0.0,
                         passes=bool(ok) if not np.isnan(tol) else None))
    return pd.DataFrame(rows), m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["masking", "regimeB"], required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--vtag", required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--rules", required=True)
    ap.add_argument("--nl", type=int, default=8)
    ap.add_argument("--budget", type=float, default=2400)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rules = a.rules.split(",")
    new = pd.read_csv(a.new)
    ref = pd.read_csv(a.ref, low_memory=False)
    ref = ref[(ref.vtag == a.vtag) & (ref.arm == a.arm) & ref.lambda_rule.isin(rules)]
    if a.kind == "masking":
        ref = ref[ref.n_L == a.nl]
        new = new[new.n_L == a.nl]
        keys = ["vtag", "arm", "estimand", "population", "target", "interval", "lambda_rule", "n_L"]
    else:
        ref = ref[(ref.regime == "B") & (ref.cost == "unit") & (pd.to_numeric(ref.budget, errors="coerce") == a.budget)]
        new = new[(new.regime == "B") & (new.cost == "unit")]
        keys = ["vtag", "arm", "estimand", "population", "target", "interval", "lambda_rule"]
    res, merged = compare(new, ref, keys, f"{a.kind}|{a.vtag}|{a.arm}")
    res.to_csv(a.out, index=False)
    merged.to_csv(a.out.replace(".csv", "_rows.csv"), index=False)
    print(json.dumps(dict(rows_ref=len(ref), rows_new=len(new), all_pass=bool(res.passes.dropna().all()))))


if __name__ == "__main__":
    main()
