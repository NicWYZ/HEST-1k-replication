#!/usr/bin/env python
"""Round 4, conformal track, stage C1: compare the GHCP reproduction with the paper and the shipped files.

docs/round4_conf_plan.md section 4 (C1 known method 5) and section 10 item 2. Inputs are the merged
reproduction tree (--ours, holding paper-results/ and results/ as the released launchers and plot
scripts write them), the released repository's shipped paper-results/ (--shipped, commit
d1a69f4), and the transcription of the paper's simulation tables (--reference,
c1_ghcp_paper_reference.csv: table, page, design, alpha, method, metric, o, value, se).

Two outputs.

  c1_ghcp_files.csv          every shipped summary CSV and table file that the reproduction also
                             wrote, with shape, column and value agreement (numeric maximum
                             absolute difference; text files compared byte for byte).
  c1_ghcp_reproduction.csv   one row per transcribed paper value, with the reproduced value and
                             its standard error, the shipped value where a shipped file holds it,
                             and agreement within Monte Carlo error. A value agrees when
                             |ours - paper| <= r + 2 sqrt(se_paper^2 + se_ours^2), where r is half
                             a unit in the last digit the paper prints (rounding), because the two
                             estimates come from the same seeds only if the code path and library
                             versions are identical; when they are, the difference is zero.

Mapping of tables to files (lambda in the paper is the local weight w_local of the merger):
  T1-T4  paper-results/dgp/summaries/<design>_summary_by_alpha_o_method.csv; HCP rows (o = -1 in
         the transcription, HCP does not use o) are read at o = 0.
  T6     results/dgp/true_marg_latent_bayes_c1_gamma5p0_fixedN21_alpha10/..._raw_results_complete.csv,
         mean of finite width_bayes by o, SE = sd / sqrt(n).
  T7-T8  results/dgp/true_marg_latent_rf_gamma5p0_<design>_alpha10/..._raw_results_complete.csv,
         coverage_<key> and width_<key> at o = 0 for key pool, sub, rep, with the same estimators as
         code/marginal/export_paper_tables_baselines.py (_stats).
  T9     paper-results/size_shift/summary_by_xi_o.csv.
  T10    paper-results/effect_of_weights/gamma5p0/summary_by_weight_o.csv.
  T11    paper-results/effect_of_weights/ud_narrow_gamma0/summary_by_predictor_weight.csv.
"""
import argparse
import glob
import math
import os
import re
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_io as IO  # noqa: E402

FILES = [
    "dgp/summaries/fixedN21_summary_by_alpha_o_method.csv",
    "dgp/summaries/fixedN21_coverage_table.csv",
    "dgp/summaries/fixedN21_width_table.csv",
    "dgp/summaries/poissonNmean25_summary_by_alpha_o_method.csv",
    "dgp/summaries/poissonNmean25_coverage_table.csv",
    "dgp/summaries/poissonNmean25_width_table.csv",
    "size_shift/summary_by_xi_o.csv",
    "size_shift/summary_by_xi_o_panels.csv",
    "effect_of_weights/gamma5p0/summary_by_weight_o.csv",
    "effect_of_weights/gamma5p0/width_monotonicity.csv",
    "effect_of_weights/ud_narrow_gamma0/summary_by_predictor_weight.csv",
]
TEXT_GLOBS = ["dgp/tables/*.tex"]
KEY = {"Pooling CDF": "pool", "Subsampling Once": "sub", "Repeated Subsampling": "rep"}


def compare_csv(a, b):
    A, B = pd.read_csv(a), pd.read_csv(b)
    out = dict(rows_ours=len(A), rows_shipped=len(B), same_columns=list(A.columns) == list(B.columns))
    if not out["same_columns"] or len(A) != len(B):
        out.update(max_abs_diff=float("nan"), text_equal=False, agree=False)
        return out
    num = [c for c in A.columns if pd.api.types.is_numeric_dtype(A[c]) and pd.api.types.is_numeric_dtype(B[c])]
    txt = [c for c in A.columns if c not in num]
    d = 0.0
    for c in num:
        x, y = A[c].to_numpy(float), B[c].to_numpy(float)
        both_nan = np.isnan(x) & np.isnan(y)
        same_inf = np.isinf(x) & np.isinf(y) & (np.sign(x) == np.sign(y))
        m = ~(both_nan | same_inf)
        if (np.isnan(x[m]) | np.isnan(y[m]) | np.isinf(x[m]) | np.isinf(y[m])).any():
            d = math.inf
        elif m.any():
            d = max(d, float(np.max(np.abs(x[m] - y[m]))))
    te = all((A[c].astype(str).to_numpy() == B[c].astype(str).to_numpy()).all() for c in txt)
    out.update(max_abs_diff=d, text_equal=bool(te), agree=bool(te and d <= 1e-9))
    return out


def half_unit(s):
    s = str(s)
    if "." not in s:
        return 0.5
    return 0.5 * 10 ** (-len(s.split(".")[1]))


def raw_path(root, prefix, design):
    pat = os.path.join(root, "results", "dgp", f"{prefix}_{design}_alpha10", "*raw_results_complete.csv")
    hits = sorted(glob.glob(pat))
    return hits[0] if hits else None


def mean_se_width(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return math.inf, 0.0
    return float(x.mean()), float(x.std(ddof=1) / math.sqrt(len(x))) if len(x) > 1 else 0.0


def mean_se_cov(x):
    x = np.asarray(x, float)
    p = float(x.mean())
    return p, math.sqrt(p * (1 - p) / len(x))


def lookup(root, row, cache):
    """(value, se) for one transcribed row from the tree at root; (nan, nan) if absent."""
    t, des, mth, met = row.table, row.design, row.method, row.metric
    o = 0 if int(row.o) < 0 else int(row.o)
    alpha = float(row.alpha)

    def rd(rel):
        p = os.path.join(root, "paper-results", rel)
        if p not in cache:
            cache[p] = pd.read_csv(p) if os.path.exists(p) else None
        return cache[p]

    def rraw(prefix, design):
        p = raw_path(root, prefix, design)
        if p is None:
            return None
        if p not in cache:
            cache[p] = pd.read_csv(p)
        return cache[p]

    nan = (float("nan"), float("nan"))
    if t in ("T1", "T2", "T3", "T4"):
        d = rd(f"dgp/summaries/{des}_summary_by_alpha_o_method.csv")
        if d is None:
            return nan
        s = d[(d.dataset == des) & np.isclose(d.alpha, alpha) & (d.method == mth) & (d.o == o)]
        if len(s) != 1:
            return nan
        s = s.iloc[0]
        if met == "coverage":
            return float(s.coverage_mean), float(s.coverage_se)
        if s.width_infinite_rate == 1.0:
            return math.inf, 0.0
        return float(s.width_mean), float(s.width_se)
    if t == "T6":
        d = rraw("true_marg_latent_bayes_c1_gamma5p0", "fixedN21")
        if d is None:
            # the shipped tree has no raw file; its comparison table holds the mean width (no SE)
            c = rd("dgp/summaries/bayes_vs_rf_c1_alpha0p1_comparison.csv")
            if c is None or met != "width":
                return nan
            s = c[c.o == o]
            return (float(s["Bayes mean"].iloc[0]), float("nan")) if len(s) == 1 else nan
        s = d[d.o_observed == o]
        return mean_se_width(s.width_bayes) if met == "width" else mean_se_cov(s.coverage_bayes)
    if t in ("T7", "T8"):
        d = rraw("true_marg_latent_rf_gamma5p0", des)
        if d is None:
            return nan
        s = d[d.o_observed == 0]
        k = KEY[mth]
        if met == "coverage":
            return mean_se_cov(s[f"coverage_{k}"])
        return mean_se_width(s[f"width_{k}"].replace([np.inf, -np.inf], np.nan).dropna())
    if t == "T9":
        d = rd("size_shift/summary_by_xi_o.csv")
        if d is None:
            return nan
        xi = float(des.replace("sizeshift_xi", ""))
        s = d[np.isclose(d.xi, xi) & (d.o == o)]
    elif t == "T10":
        d = rd("effect_of_weights/gamma5p0/summary_by_weight_o.csv")
        if d is None:
            return nan
        k = int(re.search(r"lambda(\d)of7", des).group(1))
        s = d[np.isclose(d.w_local, k / 7) & (d.o == o)]
    elif t == "T11":
        d = rd("effect_of_weights/ud_narrow_gamma0/summary_by_predictor_weight.csv")
        if d is None:
            return nan
        pred = "bayes" if "_Bayes_" in des else "rf"
        k = int(re.search(r"lambda(\d)of7", des).group(1))
        s = d[(d.predictor.str.lower() == pred) & np.isclose(d.w_local, k / 7) & (d.o == o)]
    else:
        return nan
    if len(s) != 1:
        return nan
    s = s.iloc[0]
    if met == "coverage":
        return float(s.coverage_mean), float(s.coverage_se)
    return float(s.width_mean), float(s.width_se)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--ours", required=True)
    p.add_argument("--shipped", required=True, help="the released repository root")
    p.add_argument("--reference", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    rows = []
    for rel in FILES:
        o_, s_ = os.path.join(a.ours, "paper-results", rel), os.path.join(a.shipped, "paper-results", rel)
        r = dict(file=rel, ours_exists=os.path.exists(o_), shipped_exists=os.path.exists(s_))
        if r["ours_exists"] and r["shipped_exists"]:
            r.update(compare_csv(o_, s_))
        rows.append(r)
    for g in TEXT_GLOBS:
        for s_ in sorted(glob.glob(os.path.join(a.shipped, "paper-results", g))):
            rel = os.path.relpath(s_, os.path.join(a.shipped, "paper-results"))
            o_ = os.path.join(a.ours, "paper-results", rel)
            r = dict(file=rel, ours_exists=os.path.exists(o_), shipped_exists=True)
            if r["ours_exists"]:
                r.update(text_equal=open(o_, "rb").read() == open(s_, "rb").read())
                r["agree"] = r["text_equal"]
            rows.append(r)
    F = pd.DataFrame(rows)
    F.to_csv(f"{a.out}/c1_ghcp_files.csv", index=False)

    ref = pd.read_csv(a.reference, dtype={"value": str, "se": str})
    co, cs, out = {}, {}, []
    for r in ref.itertuples(index=False):
        v, se = lookup(a.ours, r, co)
        sv, _ = lookup(a.shipped, r, cs)
        pv = math.inf if str(r.value).strip().lower() in ("inf", "+inf") else float(r.value)
        pse = float(r.se) if str(r.se) not in ("nan", "", "None") else 0.0
        if math.isinf(pv) or math.isinf(v):
            diff = 0.0 if (math.isinf(pv) and math.isinf(v)) else math.inf
            tol = 0.0
        else:
            diff = abs(v - pv)
            tol = half_unit(r.value) + 2 * math.sqrt(pse ** 2 + (se if np.isfinite(se) else 0.0) ** 2)
        out.append(dict(table=r.table, page=r.page, design=r.design, alpha=r.alpha, method=r.method,
                        metric=r.metric, o=r.o, paper=r.value, paper_se=r.se, ours=v, ours_se=se,
                        shipped=sv, ours_minus_shipped=(v - sv) if np.isfinite(v) and np.isfinite(sv) else
                        (0.0 if (math.isinf(v) and math.isinf(sv)) else float("nan")),
                        abs_diff_paper=diff, tol=tol,
                        agree=bool(np.isfinite(diff) and diff <= tol + 1e-12) if not math.isnan(v) else False,
                        found=not math.isnan(v)))
    O = pd.DataFrame(out)
    O.to_csv(f"{a.out}/c1_ghcp_reproduction.csv", index=False)
    summ = O.groupby("table").agg(n=("agree", "size"), found=("found", "sum"), agree=("agree", "sum"),
                                  max_abs_ours_minus_shipped=("ours_minus_shipped",
                                                              lambda x: float(np.nanmax(np.abs(x))) if np.isfinite(x).any() else float("nan")))
    summ.to_csv(f"{a.out}/c1_ghcp_reproduction_by_table.csv")
    print(F[["file", "ours_exists", "agree"]].to_string(index=False))
    print(summ.to_string())
    IO.write_provenance(a.out, "C1", __file__, dict(stage="C1 GHCP reproduction comparison",
                                                    ours=a.ours, shipped=a.shipped, reference=a.reference))
    return 0


if __name__ == "__main__":
    sys.exit(main())
