#!/usr/bin/env python
"""Round 4 PPI, interval 3: merge the Q4a recomputation (Q3 decision memo section 3, plan section 14.3)
and score predictions Q4a.1, Q4.4 and Q3.3 (plan section 4).

Inputs
  --stage   directory holding the Q4a unit outputs, any layout; read recursively:
            nL*/q2_variance_grid__<vtag>__<arm>.csv and q2_variance_grid_genes__*.csv.gz (masking),
            q3_regime_comparison__<vtag>__<arm>__{q4aA,cd10,cd1000}.csv (regimes)
  --res     results/round4/ppi (reads the interval-2 Q3_regimes/q3_regime_comparison.csv for the
            unit-cost regime B and c_d/c_s = 100 rows, and Q2_theory/q2_fitted_components.csv.gz)
Outputs under --res/Q4a_recompute/
  q4a_variance_grid.csv, q4a_variance_grid_genes.csv.gz, q4a_regime_comparison.csv,
  q4a_table61.csv          the section 6.1 table at every n_L, both targets, m = all, rules none,
                           c_crossfit, c_crossfit_design side by side (theta3 and theta2, both populations)
  q4a_breakeven_cells.csv  per (task, arm, n_L) the Q4.4 inputs
  q4a_crossover.csv        Q3.3 empirical and predicted crossover cost ratios
  q4a_prediction_scores.csv one row per criterion, with a SUMMARY row per prediction
"""
import argparse
import glob
import os
import re

import numpy as np
import pandas as pd

HEST = ["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM"]
ENC = ["hoptimus0", "uni_v2", "resnet50"]
KEY2 = ["vtag", "arm", "n_L", "m", "estimand", "population", "target", "lambda_rule", "interval"]


def read_all(pattern):
    fs = sorted(glob.glob(pattern, recursive=True))
    parts = []
    for f in fs:
        try:
            parts.append(pd.read_csv(f).assign(source_file=os.path.basename(f)))
        except pd.errors.EmptyDataError:
            pass   # e.g. c_d/c_s = 1000, where regime B is unaffordable and the file is empty
    return (pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()), fs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stage", required=True)
    p.add_argument("--res", required=True)
    a = p.parse_args()
    out = f"{a.res}/Q4a_recompute"
    os.makedirs(out, exist_ok=True)
    g, gf = read_all(f"{a.stage}/**/nL*/q2_variance_grid__*.csv")
    g["m"] = g["m"].astype(str).replace({"0": "all"})
    g = g.drop_duplicates(KEY2, keep="first")
    g.to_csv(f"{out}/q4a_variance_grid.csv", index=False)
    gg, ggf = read_all(f"{a.stage}/**/nL*/q2_variance_grid_genes__*.csv.gz")
    gg["m"] = gg["m"].astype(str).replace({"0": "all"})
    gg = gg.drop_duplicates(KEY2 + ["gene"], keep="first")
    gg.to_csv(f"{out}/q4a_variance_grid_genes.csv.gz", index=False, compression="gzip")
    q, qf = read_all(f"{a.stage}/**/q3_regime_comparison__*.csv")
    q.to_csv(f"{out}/q4a_regime_comparison.csv", index=False)

    # ---------------------------------------------------------------- section 6.1 table
    s = g[(g.m == "all") & g.interval.isin(["textbook_t|fpc", "CR2_bm", "CR1_t"])]
    cols = ["emp_var_median", "emp_var_ratio_median", "coverage_median", "est_var_over_emp_var_median",
            "lambda_median", "lambda_se_median"]
    t61 = s[["vtag", "arm", "estimand", "population", "target", "interval", "lambda_rule", "n_L"] + cols].copy()
    t61["G"] = t61.vtag.map(g.groupby("vtag").G.first()) if "G" in g else np.nan
    t61["G_U"] = np.where(t61.target == "super", t61["G"] - t61["n_L"], np.nan)
    t61 = t61.sort_values(["vtag", "arm", "estimand", "population", "target", "interval", "n_L", "lambda_rule"])
    t61.to_csv(f"{out}/q4a_table61.csv", index=False)

    rows = []

    def add(pred, scope, stat, value, crit, holds):
        rows.append(dict(prediction=pred, scope=scope, statistic=stat, value=value, criterion=crit,
                         holds=None if holds is None else bool(holds)))

    d = t61[(t61.estimand == "theta3") & (t61.population == "donor") & (t61.target == "design")]

    def val(vt, arm, n, rule, col):
        x = d[(d.vtag == vt) & (d.arm == arm) & (d.n_L == n) & (d.lambda_rule == rule)][col]
        return float(x.iloc[0]) if len(x) else np.nan

    # ---------------------------------------------------------------- Q4a.1
    for arm in ENC:
        l8, l16 = val("CCRCC", arm, 8, "c_crossfit_design", "lambda_median"), val("CCRCC", arm, 16, "c_crossfit_design", "lambda_median")
        add("Q4a.1", f"CCRCC|{arm}", "lambda_median_nL16_minus_nL8", l16 - l8,
            "|median lambda at n_L 16 - at n_L 8| <= 0.1 (theta3 donor, design, m = all)", abs(l16 - l8) <= 0.1)
    for vt in HEST:
        for arm in ENC:
            r8 = val(vt, arm, 8, "c_crossfit_design", "emp_var_ratio_median")
            for n in (12, 16):
                rn = val(vt, arm, n, "c_crossfit_design", "emp_var_ratio_median")
                if np.isfinite(rn) and np.isfinite(r8):
                    add("Q4a.1", f"{vt}|{arm}|nL{n}", "ratio_minus_ratio_nL8", rn - r8,
                        "design ratio at n_L 12 and 16 no larger than at n_L 8", rn <= r8)
    for n in (6, 8, 12, 16):
        r = val("CCRCC", "uni_v2", n, "c_crossfit_design", "emp_var_ratio_median")
        add("Q4a.1", f"CCRCC|uni_v2|nL{n}", "design_ratio", r, "< 0.9 at every n_L >= 6", r < 0.9)
    for n in sorted(d[d.vtag == "LUNG_XENIUM"].n_L.unique()):
        r = val("LUNG_XENIUM", "hoptimus0", int(n), "c_crossfit_design", "emp_var_ratio_median")
        add("Q4a.1", f"LUNG_XENIUM|hoptimus0|nL{int(n)}", "design_ratio", r,
            "< 0.75 at every n_L (n_L = 4 is classical by the n_L < 6 rule, ratio 1)", r < 0.75)

    # ---------------------------------------------------------------- Q4.4
    ge = gg[(gg.estimand == "theta3") & (gg.population == "donor") & (gg.target == "design") & (gg.m == "all")
            & (gg.lambda_rule == "c_crossfit_design") & gg.n_L.isin([8, 16])].copy()
    ge["ratio_m1"] = ge.emp_var / ge.emp_var_classical - 1.0
    ge["be"] = ge.lambda_se_median ** 2 - ge.lambda_median ** 2
    be = ge.groupby(["vtag", "arm", "n_L"]).agg(n_genes=("gene", "size"), ratio_minus_1_median=("ratio_m1", "median"),
                                              se2_minus_lam2_median=("be", "median"),
                                              lambda_median=("lambda_median", "median"),
                                              lambda_se_median=("lambda_se_median", "median")).reset_index()
    be["agree"] = np.sign(be.ratio_minus_1_median) == np.sign(be.se2_minus_lam2_median)
    be.to_csv(f"{out}/q4a_breakeven_cells.csv", index=False)
    for sub, mask in (("all_arms", np.ones(len(be), bool)), ("encoders_only", be.arm.isin(ENC).to_numpy()),
                      ("HEST_encoders", (be.arm.isin(ENC) & be.vtag.isin(HEST)).to_numpy())):
        b = be[mask]
        add("Q4.4", sub, "n_agree_of_n_cells", f"{int(b.agree.sum())}/{len(b)}",
            "sign(ratio - 1) agrees with sign(se^2 - lambda^2) in at least 18 of 22 cells (scaled: >= 18/22 of cells)",
            (b.agree.mean() >= 18 / 22) if len(b) else None)

    # ---------------------------------------------------------------- Q3.3 crossover
    q2 = pd.read_csv(f"{a.res}/Q3_regimes/q3_regime_comparison.csv", low_memory=False)
    allq = pd.concat([q2, q], ignore_index=True).drop_duplicates(
        ["vtag", "arm", "regime", "budget", "cost", "n_L", "estimand", "population", "target", "lambda_rule", "interval"])
    allq = allq[(allq.estimand == "theta3") & (allq.population == "donor") & (allq.target == "super")
                & (allq.lambda_rule == "c_crossfit") & (allq.interval.isin(["CR1_t", "regB_t"]))]
    fit = pd.read_csv(f"{a.res}/Q2_theory/q2_fitted_components.csv.gz", low_memory=False)
    fit = fit[(fit.target == "super") & (fit.interval == "CR1_t") & (fit.estimand == "theta3") & (fit.population == "donor")]
    comp = fit.groupby(["vtag", "arm", "lambda_rule"])[["sigma2_cluster", "sigma2_unit"]].median()
    cx = []
    for (vt, arm), z in allq.groupby(["vtag", "arm"]):
        A = z[(z.regime == "A") & (z.cost == "unit")]
        G = int(z.G.iloc[0])
        for _, ra in A.iterrows():
            nl, B = int(ra.n_L), int(ra.budget)
            mA = B // nl
            pts = []
            Bu = z[(z.regime == "B") & (z.cost == "unit") & (z.budget == B)]
            if len(Bu):
                pts.append((0.0, float(Bu.emp_var_median.iloc[0])))
            for c in (10, 100, 1000):
                Bc = z[(z.regime == "B") & (z.cost == f"cd_cs_{c}_vs_A_nL{nl}_B{B}")]
                if len(Bc):
                    pts.append((float(c), float(Bc.emp_var_median.iloc[0])))
            vA = float(ra.emp_var_median)
            emp = np.nan
            for (c0, v0), (c1, v1) in zip(pts, pts[1:]):
                if (v0 - vA) * (v1 - vA) <= 0 and v1 != v0:
                    emp = c0 + (vA - v0) * (c1 - c0) / (v1 - v0)
                    break
            # regime B can touch all G clusters only while n_L (c + m_A) - c G > 0
            c_aff = nl * mA / (G - nl)
            kind = "interpolated"
            if np.isnan(emp) and pts and all(v < vA for _, v in pts):
                emp, kind = c_aff, "affordability_limit"   # B wins wherever it is affordable
            try:
                su, se = comp.loc[(vt, arm, "none")]
                sur, ser = comp.loc[(vt, arm, "c_crossfit")]
                den = sur / nl + ser / B - su / G
                BB = ser / den if den > 0 else np.nan
                pred = (nl * mA - BB) / (G - nl) if np.isfinite(BB) else np.nan
                pred = min(pred, c_aff) if np.isfinite(pred) else pred
            except KeyError:
                pred = np.nan
            cx.append(dict(vtag=vt, arm=arm, n_L=nl, budget=B, var_A=vA, n_cost_points=len(pts),
                           c_affordable_max=c_aff, crossover_emp=emp, crossover_emp_kind=kind,
                           crossover_pred=pred))
    cx = pd.DataFrame(cx)
    cx.to_csv(f"{out}/q4a_crossover.csv", index=False)
    ok = cx[np.isfinite(cx.crossover_emp) & np.isfinite(cx.crossover_pred) & (cx.crossover_pred > 0) & (cx.crossover_emp > 0)]
    for (vt, arm), z in ok.groupby(["vtag", "arm"]):
        r = (z.crossover_emp / z.crossover_pred)
        within = ((r >= 0.5) & (r <= 2)).mean()
        add("Q3.3", f"{vt}|{arm}", "frac_cells_pred_within_factor2", float(within),
            "predicted crossover within a factor of two of the empirical one in every cell", within == 1.0)
    add("Q3.3", "all", "n_cells_scored", len(ok), "context", None)

    sc = pd.DataFrame(rows)
    summ = []
    for pr, z in sc.groupby("prediction"):
        h = z.holds.dropna()
        summ.append(dict(prediction=pr, scope="SUMMARY", statistic="n_holds_of_n_scored",
                         value=f"{int(h.sum())}/{len(h)}", criterion="", holds=bool(h.all()) if len(h) else None))
    sc = pd.concat([sc, pd.DataFrame(summ)], ignore_index=True)
    sc.to_csv(f"{out}/q4a_prediction_scores.csv", index=False)
    print(dict(q2_files=len(gf), q2_rows=len(g), gene_rows=len(gg), q3_files=len(qf), q3_rows=len(q),
               tasks=sorted(g.vtag.unique()), table61=len(t61), breakeven_cells=len(be), crossover_rows=len(cx)))
    print(pd.DataFrame(summ).to_string(index=False))


if __name__ == "__main__":
    main()
