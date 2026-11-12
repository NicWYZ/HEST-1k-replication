#!/usr/bin/env python
"""Round 10, track final-runs, F3.1 anchors (plan section 5d.1 items 1, 5 and 7; 5d.4 item 3). Each subcommand
compares a rerun of an earlier script, run unchanged from the snapshot, with the committed rows it must reproduce,
and writes anchor_<name>.json with both values, the criterion and the verdict. Nothing here is a result.

usage:
  round10_final_runs_f3_map_anchor.py w3 <w3_out_dir> <ref w3_by_fold.csv> <out_dir> [--driver <map_by_fold.csv>]
  round10_final_runs_f3_map_anchor.py stud <stud_reps__CCRCC.csv.gz> <ref stud_summary.csv> <ref per_donor.csv> <out_dir>
  round10_final_runs_f3_map_anchor.py a4 <new a4_scores_by_task csv> <ref a4_scores_by_task csv> <out_dir>
  round10_final_runs_f3_map_anchor.py acs <acs_o_sweep.csv> <ref c3_o_sweep__ACS.csv> <out_dir>
"""
import glob
import json
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
TOL = 1e-9


def _dump(out_dir, name, d):
    os.makedirs(out_dir, exist_ok=True)
    json.dump(d, open(os.path.join(out_dir, f"anchor_{name}.json"), "w"), indent=1, default=float)
    print(json.dumps(d, indent=1, default=float), flush=True)


def _maxdiff(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    both_inf = np.isinf(a) & np.isinf(b) & (np.sign(a) == np.sign(b))
    both_nan = np.isnan(a) & np.isnan(b)
    d = np.where(both_inf | both_nan, 0.0, np.abs(a - b))
    d = np.where(np.isnan(d), np.inf, d)
    return float(d.max()) if d.size else float("nan")


def w3(w3_dir, ref_path, out_dir, driver=None):
    import round4_conf_c3 as C
    full = pd.concat([pd.read_csv(p) for p in sorted(glob.glob(os.path.join(w3_dir, "w3_full__*.csv.gz")))])
    new = C.by_fold_table(full.to_dict("records"))
    new = new.rename(columns={"finite_frac": "finite_frac", "n_draws": "n_draws"})
    ref = pd.read_csv(ref_path)
    folds = sorted(new["fold"].unique().tolist())
    ref = ref[(ref.part == 1) & (ref.task == "CCRCC") & (ref.encoder == "uni_v2") & (ref.fold.isin(folds))]
    keys = ["method", "alpha", "o", "K", "fold"]
    m = ref.merge(new, on=keys, how="left", suffixes=("_ref", "_new"), indicator=True)
    out = dict(anchor="5d.1 item 1: round5_conf_w3.py --part 1 unchanged, CCRCC:24, uni_v2", folds=folds,
               reference=ref_path, n_ref_rows=int(len(ref)), n_matched=int((m["_merge"] == "both").sum()),
               criterion=f"every reference row matched and max abs difference <= {TOL} in coverage, width_mean, "
                         f"width_median and n_T_donors")
    for c in ("coverage", "width_mean", "width_median", "n_T_donors", "n_draws"):
        out[f"maxabs_{c}"] = _maxdiff(m[f"{c}_ref"], m[f"{c}_new"])
    named = []
    for meth, o, fold in (("hcp", 0, "INT1"), ("within_full", 9, "INT1"), ("within_full", 9, "INT5"),
                          ("hcp", 0, "INT5"), ("within_plain", 9, "INT1"), ("ghcp", 9, "INT5")):
        r = m[(m.method == meth) & (m.o == o) & (m.fold == fold) & (m.alpha == 0.1)]
        if len(r):
            r = r.iloc[0]
            named.append(dict(method=meth, o=o, fold=fold, alpha=0.1, coverage_ref=r["coverage_ref"],
                              coverage_new=r["coverage_new"], width_median_ref=r["width_median_ref"],
                              width_median_new=r["width_median_new"]))
    out["named_rows"] = named
    chk = sorted(glob.glob(os.path.join(w3_dir, "w3_checks__*.csv")))
    if chk:
        ck = pd.concat([pd.read_csv(p) for p in chk])
        out["w3_checks_all_passed"] = bool(ck["passed"].all()) if len(ck) else None
    out["passed"] = bool(out["n_matched"] == out["n_ref_rows"] and out["n_ref_rows"] > 0 and
                         max(out[f"maxabs_{c}"] for c in ("coverage", "width_mean", "width_median",
                                                          "n_T_donors")) <= TOL)
    if driver:
        dv = pd.read_csv(driver)
        dv = dv[(dv.scale == "log1p")]
        mm = new.merge(dv, on=keys, suffixes=("_w3", "_f3"))
        out["driver_vs_w3_rows"] = int(len(mm))
        out["driver_vs_w3_methods"] = sorted(mm["method"].unique().tolist())
        for c in ("coverage", "width_mean", "width_median"):
            out[f"driver_vs_w3_maxabs_{c}"] = _maxdiff(mm[f"{c}_w3"], mm[f"{c}_f3"])
        out["driver_passed"] = bool(len(mm) > 0 and max(out[f"driver_vs_w3_maxabs_{c}"] for c in
                                                         ("coverage", "width_mean", "width_median")) <= TOL)
    _dump(out_dir, "w3", out)


def stud(reps_path, ref_path, ref_pd_path, out_dir):
    d = pd.read_csv(reps_path)
    task = d["task"].iloc[0]
    rep_mean = d.groupby(["o", "method", "rep"])["coverage"].mean().reset_index()
    se = rep_mean.groupby(["o", "method"])["coverage"].agg(lambda x: x.std(ddof=1) / math.sqrt(len(x))).rename("mcse")
    summ = d.groupby(["o", "method"]).agg(coverage=("coverage", "mean"), hw=("mean_hw_finite", "mean"),
                                          frac_inf=("frac_inf", "mean")).join(se).reset_index()
    summ.insert(0, "task", task)
    summ.to_csv(os.path.join(out_dir, f"stud_summary_rerun__{task}.csv"), index=False)
    ref = pd.read_csv(ref_path)
    ref = ref[ref.task == task]
    m = ref.merge(summ, on=["task", "o", "method"], suffixes=("_ref", "_new"))
    m["z"] = (m["coverage_new"] - m["coverage_ref"]) / m["mcse"]
    m.to_csv(os.path.join(out_dir, f"stud_compare__{task}.csv"), index=False)
    r = m[(m.o == 3) & (m.method == "xgene")].iloc[0]
    pdr = pd.read_csv(ref_pd_path)
    new_pd = d.groupby(["o", "method", "target"])["coverage"].mean().reset_index()
    int5 = pdr[(pdr.task == task) & (pdr.o == 3) & (pdr.method == "xgene") & (pdr.target == "INT5")]
    n5 = new_pd[(new_pd.o == 3) & (new_pd.method == "xgene") & (new_pd.target == "INT5")]
    out = dict(anchor="5d.1 item 5: round9_stud_feasibility.py unchanged, CCRCC, PYTHONHASHSEED=0",
               reference=f"{ref_path} row CCRCC, o 3, xgene", reference_coverage=float(r["coverage_ref"]),
               reproduced_coverage=float(r["coverage_new"]), mcse=float(r["mcse"]), z=float(r["z"]),
               exact=bool(abs(r["coverage_new"] - r["coverage_ref"]) <= TOL),
               criterion="|reproduced - reference| <= 2 Monte Carlo standard errors (rep-level SE over 40 reps); "
                         "exact agreement not expected (the script seeds from hash(task))",
               all_rows_max_abs_z=float(m["z"].abs().max()), all_rows_n=int(len(m)),
               all_rows_share_within_2se=float((m["z"].abs() <= 2).mean()),
               int5_xgene_o3_ref=float(int5["coverage"].iloc[0]) if len(int5) else None,
               int5_xgene_o3_new=float(n5["coverage"].iloc[0]) if len(n5) else None)
    out["passed"] = bool(abs(out["z"]) <= 2)
    _dump(out_dir, "stud", out)


def a4(new_path, ref_path, out_dir):
    new, ref = pd.read_csv(new_path), pd.read_csv(ref_path)
    keys = ["task", "label_set", "encoder", "design", "score", "alpha", "subset", "gene_subset"]
    sel = lambda d: d[(d.task == "CCRCC") & (d.encoder == "uni_v2") & (d.design == "donor")]
    m = sel(ref).merge(sel(new), on=keys, suffixes=("_ref", "_new"))
    cols = [c for c in ("coverage", "coverage_sd", "width_mean", "width_median", "n_folds", "n_cells")
            if f"{c}_ref" in m and f"{c}_new" in m]
    out = dict(anchor="5d.1 item 7: round3_a4_scores.py unchanged (designs random,patient,donor; scores abs, scaled, "
                      "scaled_clip), CCRCC, uni_v2, donor design", reference=ref_path,
               n_matched=int(len(m)), scores=sorted(m["score"].unique().tolist()),
               criterion=f"max abs difference <= {TOL} over {cols} on every matched row")
    for c in cols:
        out[f"maxabs_{c}"] = _maxdiff(m[f"{c}_ref"], m[f"{c}_new"])
    r = m[(m.score == "scaled_clip") & (m.alpha.round(6) == 0.1) & (m.subset == "full")]
    if len(r):
        out["scaled_clip_coverage_ref"] = float(r["coverage_ref"].iloc[0])
        out["scaled_clip_coverage_new"] = float(r["coverage_new"].iloc[0])
    out["passed"] = bool(len(m) > 0 and max(out[f"maxabs_{c}"] for c in cols) <= TOL)
    _dump(out_dir, "a4", out)


def acs(new_path, ref_path, out_dir):
    new, ref = pd.read_csv(new_path), pd.read_csv(ref_path)
    keys = ["method", "alpha", "o", "fold", "draw"]
    ref = ref[ref.draw.isin(new.draw.unique())]
    m = ref.merge(new, on=keys, how="left", suffixes=("_ref", "_new"), indicator=True)
    out = dict(anchor="5d.4 item 3: round4_conf_c3_acs_o.py one_draw unchanged (o grid widened), rows at round 4's o",
               reference=ref_path, draws=sorted(int(x) for x in new.draw.unique()), n_ref_rows=int(len(ref)),
               n_matched=int((m["_merge"] == "both").sum()),
               criterion=f"every reference row of these draws matched, max abs difference <= {TOL}")
    for c in ("coverage", "width_mean", "width_median", "finite", "n_test", "K"):
        out[f"maxabs_{c}"] = _maxdiff(m[f"{c}_ref"], m[f"{c}_new"])
    out["passed"] = bool(out["n_matched"] == out["n_ref_rows"] > 0 and
                         max(out[f"maxabs_{c}"] for c in ("coverage", "width_mean", "width_median", "finite")) <= TOL)
    _dump(out_dir, "acs", out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "w3":
        drv = a[a.index("--driver") + 1] if "--driver" in a else None
        w3(a[1], a[2], a[3], drv)
    elif a[0] == "stud":
        stud(a[1], a[2], a[3], a[4])
    elif a[0] == "a4":
        a4(a[1], a[2], a[3])
    elif a[0] == "acs":
        acs(a[1], a[2], a[3])
    else:
        raise SystemExit(__doc__)
