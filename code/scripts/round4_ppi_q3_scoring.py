#!/usr/bin/env python
"""Round 4 PPI, interval 2: score predictions Q2.1 to Q2.7 and Q3.1 to Q3.4 against the merged numbers.

Inputs under --res (results/round4/ppi):
  Q2_theory/q2_report_numbers.csv, Q2_theory/recalibration/q2_recalibration.csv,
  Q2_theory/theorem_v2/q2_sim_theorem.csv, Q3_regimes/q3_report_numbers.csv,
  Q3_regimes/q3_regime_comparison.csv
Output: Q3_regimes/q3_prediction_scores.csv with one row per prediction, scope and statistic
(columns prediction, scope, statistic, value, criterion, holds), and a summary row per prediction.

Criteria are the plan's section 4 wording, made operational as stated in each row's `criterion`.
"Flat in m" (Q2.2) is read as a variance ratio to m = all below 1.2: with 200 draws the relative
standard error of one empirical variance is about sqrt(2/199) = 0.10, so 1.2 is about 1.4 standard
errors of the ratio of two such variances.
"""
import argparse

import numpy as np
import pandas as pd

HEST = ["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM"]
VISIUM = ["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--res", required=True)
    a = p.parse_args()
    q2 = pd.read_csv(f"{a.res}/Q2_theory/q2_report_numbers.csv")
    q3 = pd.read_csv(f"{a.res}/Q3_regimes/q3_report_numbers.csv")
    N2 = dict(zip(q2.name, q2.value)); N3 = dict(zip(q3.name, q3.value))
    tasks = sorted({n.split("|")[1] for n in q2.name if n.startswith("Q2|")})
    arms = {t: sorted({n.split("|")[2] for n in q2.name if n.startswith(f"Q2|{t}|")}) for t in tasks}
    rows = []

    def add(pred, scope, stat, value, crit, holds):
        rows.append(dict(prediction=pred, scope=scope, statistic=stat, value=value, criterion=crit,
                         holds=(None if holds is None else bool(holds))))

    # Q2.1
    for t in tasks:
        for arm in arms[t]:
            tag = f"{t}|{arm}|theta3|donor"
            v = N2.get(f"Q2.1|{tag}|super|c_crossfit|var_ratio_mall_nLmax", np.nan)
            o = N2.get(f"Q2.1|{tag}|one_minus_R2_cluster_raw", np.nan)
            add("Q2.1", f"{t}|{arm}", "var_ratio_mall_nLmax_minus_one_minus_R2_cluster_raw", v - o,
                "|ratio - (1 - R2_cluster_raw)| <= 0.1, theta3 donor, rule c, superpopulation",
                abs(v - o) <= 0.1 if np.isfinite(v - o) else None)
            add("Q2.1", f"{t}|{arm}", "R2_unit", 1 - N2.get(f"Q2.1|{tag}|one_minus_R2_unit", np.nan), "context", None)
            add("Q2.1", f"{t}|{arm}", "R2_cluster_raw", N2.get(f"Q2.1|{tag}|R2_cluster_raw", np.nan), "context", None)
            add("Q2.1", f"{t}|{arm}", "frac_genes_R2_cluster_corrected_undefined",
                N2.get(f"Q2.1|{tag}|frac_genes_R2_cluster_corrected_undefined", np.nan), "context", None)
    # Q2.2
    for t in tasks:
        for arm in arms[t]:
            for rule in ("none", "c_crossfit"):
                for m in ("200", "500"):
                    v = N2.get(f"Q2.2|{t}|{arm}|theta3|donor|super|{rule}|emp_var_m{m}_over_mall", np.nan)
                    add("Q2.2", f"{t}|{arm}|{rule}", f"emp_var_m{m}_over_mall_nLmax", v,
                        "ratio < 1.2 at m = 200 and m = 500 (flat beyond 100 to 200)",
                        v < 1.2 if np.isfinite(v) else None)
    # Q2.3: m*_PP ordering hoptimus0 < resnet50 < permuted on every HEST task
    for t in [x for x in HEST if x in tasks]:
        ms = {e: N2.get(f"Q2.3|{t}|{e}|theta3|donor|c_crossfit|m_star_cd_cs_100_median", np.nan)
              for e in ("hoptimus0", "resnet50", "permuted")}
        for e, v in ms.items():
            add("Q2.3", f"{t}|{e}", "m_star_PP_cd_cs_100_median", v, "context", None)
        add("Q2.3", t, "order_hoptimus0_lt_resnet50_lt_permuted", np.nan,
            "m*_PP(hoptimus0) < m*_PP(resnet50) < m*_PP(permuted)",
            ms["hoptimus0"] < ms["resnet50"] < ms["permuted"])
        for e in ("hoptimus0", "resnet50", "permuted"):
            add("Q2.3", f"{t}|{e}", "sigma2_unit_rule_c_median",
                N2.get(f"Q2.3|{t}|{e}|theta3|donor|c_crossfit|sigma2_unit_median", np.nan), "context", None)
            add("Q2.3", f"{t}|{e}", "sigma2_cluster_rule_c_median",
                N2.get(f"Q2.3|{t}|{e}|theta3|donor|c_crossfit|sigma2_cluster_median", np.nan), "context", None)
    # Q2.4: classical m* at c_d/c_s = 100
    vis = []
    for t in [x for x in tasks if x in VISIUM] + [x for x in tasks if x not in VISIUM]:
        arm = "hoptimus0" if "hoptimus0" in arms[t] else "package"
        v = N2.get(f"Q2.3|{t}|{arm}|theta3|donor|none|m_star_cd_cs_100_median", np.nan)
        if t in VISIUM:
            vis.append(v)
            add("Q2.4", f"{t}|{arm}", "m_star_classical_cd_cs_100_median", v, "30 <= m* <= 150 (Visium)",
                (30 <= v <= 150) if np.isfinite(v) else None)
        else:
            add("Q2.4", f"{t}|{arm}", "m_star_classical_cd_cs_100_median", v,
                "larger than every Visium task's m*", (v > np.nanmax(vis)) if (np.isfinite(v) and vis) else None)
    # Q2.5: estimated over empirical variance within 15% at n_L >= 6
    for t in tasks:
        for tgt in ("design", "super"):
            sel = q2[q2.name.str.startswith(f"Q2.5|{t}|") & q2.name.str.endswith("est_over_emp_median")
                     & q2.name.str.contains(f"|{tgt}|", regex=False)]
            nl = sel.name.str.extract(r"\|nL(\d+)\|")[0].astype(float)
            s6 = sel[nl >= 6]; s4 = sel[nl == 4]
            frac = float((s6.value.sub(1).abs() <= 0.15).mean())
            add("Q2.5", f"{t}|{tgt}", "frac_cells_nL_ge6_within_15pct", frac,
                "estimated / empirical variance within 15% in every cell with n_L >= 6", frac == 1.0)
            add("Q2.5", f"{t}|{tgt}", "frac_cells_nL4_within_15pct", float((s4.value.sub(1).abs() <= 0.15).mean()),
                "context", None)
            add("Q2.5", f"{t}|{tgt}", "median_est_over_emp_nL_ge6", float(s6.value.median()), "context", None)
            add("Q2.5", f"{t}|{tgt}", "n_cells_nL_ge6", len(s6), "context", None)
    # Q2.6: recalibration
    try:
        rc = pd.read_csv(f"{a.res}/Q2_theory/recalibration/q2_recalibration.csv")
        for (t, e), r in rc.groupby(["task", "encoder"]):
            med = float(r.R2_offset_loo.median())
            add("Q2.6", f"{t}|{e}", "R2_offset_loo_median_gene", med, "0.1 <= median LOO R2 of offsets <= 0.4",
                0.1 <= med <= 0.4)
            dc = float((r.R2_cluster_raw_after - r.R2_cluster_raw_before).median())
            add("Q2.6", f"{t}|{e}", "delta_R2_cluster_raw_median", dc, "cluster-level R2 rises by >= 0.1", dc >= 0.1)
            dw = float((r.R2_within_after - r.R2_within_before).abs().max())
            add("Q2.6", f"{t}|{e}", "max_abs_delta_R2_within", dw, "within-cluster R2 unchanged to 1e-3", dw <= 1e-3)
            # The donor-weighted estimators centre within donor, so a donor-constant offset cancels in every
            # donor sum at m = all (max before/after difference is float rounding); scored on spot-weighted.
            dvd = float((r.vr_theta3_donor_c_crossfit_nL12_mall_after
                         - r.vr_theta3_donor_c_crossfit_nL12_mall_before).abs().max())
            add("Q2.6", f"{t}|{e}", "max_abs_delta_var_ratio_theta3_donor_nL12", dvd,
                "context (structurally zero for donor-weighted estimands)", None)
            dv = (r.vr_theta3_spot_c_crossfit_nL12_mall_after - r.vr_theta3_spot_c_crossfit_nL12_mall_before)
            d1 = -(r.R2_cluster_raw_after - r.R2_cluster_raw_before)
            add("Q2.6", f"{t}|{e}", "median_delta_var_ratio_theta3_spot_nL12", float(dv.median()), "context", None)
            dd = float((dv - d1).abs().median())
            add("Q2.6", f"{t}|{e}", "median_abs(delta_var_ratio - delta_one_minus_R2c)_theta3_spot_nL12", dd,
                "variance-ratio change within 0.1 of the change in 1 - R2_cluster (spot-weighted)", dd <= 0.1)
    except FileNotFoundError:
        add("Q2.6", "all", "missing", np.nan, "q2_recalibration.csv not found", None)
    # Q2.7: theorem check
    th = pd.read_csv(f"{a.res}/Q2_theory/theorem_v2/q2_sim_theorem.csv")
    for _, r in th.iterrows():
        sc = f"GL{int(r.G_L)}|GU{int(r.G_U)}|m{int(r.m)}|sa2su2_{r.sigma_a2_over_sigma_u2:g}"
        if r.m == 5000 and r.G_U == 100:
            d = r.emp_var_ratio - r.one_minus_R2_exact
            add("Q2.7", sc, "emp_ratio_minus_one_minus_R2_exact", d, "|diff| <= 0.05 at m = 5000, G_U = 100",
                abs(d) <= 0.05)
            d2 = r.oracle_emp_var_ratio - r.one_minus_R2_exact
            add("Q2.7", sc, "oracle_ratio_minus_one_minus_R2_exact", d2, "context (oracle lambda)", None)
        if r.G_U == 20:
            d = r.emp_var_ratio - r.full_ratio_lambda_A
            add("Q2.7", sc, "emp_ratio_minus_full_ratio", d, "|diff| <= 0.05 at G_U = 20", abs(d) <= 0.05)
            add("Q2.7", sc, "emp_ratio_minus_one_minus_R2_minus_GU_term",
                r.emp_var_ratio - r.one_minus_R2_exact - r.GU_term_lambda_A,
                ">= 0 (above 1 - R2 by at least the G_U term)",
                r.emp_var_ratio - r.one_minus_R2_exact >= r.GU_term_lambda_A)
    # Q3.1: width ratio B over A <= 0.8, theta3 donor, unit cost
    for t in sorted({n.split("|")[1] for n in q3.name if n.startswith("Q3.1|")}):
        for tgt in ("design", "super"):
            for rule in ("none", "c_crossfit"):
                s = q3[q3.name.str.match(rf"Q3\.1\|{t}\|[^|]+\|theta3\|donor\|{rule}\|{tgt}\|B\d+\|nL\d+\|width_ratio_B_over_A$")]
                if not len(s):
                    continue
                add("Q3.1", f"{t}|{tgt}|{rule}", "max_width_ratio_B_over_A_unit_cost", float(s.value.max()),
                    "regime B narrower by >= 20% at every budget and n_L (ratio <= 0.8); scored for rule c only",
                    (s.value.max() <= 0.8) if rule == "c_crossfit" else None)
                add("Q3.1", f"{t}|{tgt}|{rule}", "median_width_ratio_unit_cost", float(s.value.median()), "context", None)
                add("Q3.1", f"{t}|{tgt}|{rule}", "frac_cells_ratio_le_0.8", float((s.value <= 0.8).mean()), "context", None)
                c = q3[q3.name.str.match(rf"Q3\.1\|{t}\|[^|]+\|theta3\|donor\|{rule}\|{tgt}\|cost100\|B\d+\|nL\d+\|width_ratio_B_over_A$")]
                if len(c):
                    add("Q3.1", f"{t}|{tgt}|{rule}", "median_width_ratio_cost100", float(c.value.median()),
                        "advantage shrinks under c_d/c_s = 100 (median ratio above the unit-cost median); rule c only",
                        (float(c.value.median()) > float(s.value.median())) if rule == "c_crossfit" else None)
    add("Q3.1", "all", "reversal_at_cd_cs_ge_1000", np.nan, "not assessed (only c_d/c_s = 100 was run)", None)
    # Q3.2: regime B design coverage with design variance at m >= 25
    s = q3[q3.name.str.contains(r"\|theta3\|donor\|(?:none|c_crossfit)\|design\|regB\|B\d+\|coverage_median$")]
    for nm, v in zip(s.name, s.value):
        mm = N3.get(nm.replace("coverage_median", "m_median"), np.nan)
        if mm >= 25:
            add("Q3.2", "|".join(nm.split("|")[1:9]), "regB_design_coverage_median", v,
                "0.88 <= coverage <= 0.92 at m >= 25", 0.88 <= v <= 0.92)
    # second half: the cluster-robust (superpopulation) interval evaluated against theta_full, the
    # finite-population value the masking experiment can score, i.e. against the design target
    s = q3[q3.name.str.contains(r"\|theta3\|donor\|(?:none|c_crossfit)\|super\|regB\|B\d+\|coverage_median$")]
    for nm, v in zip(s.name, s.value):
        mm = N3.get(nm.replace("coverage_median", "m_median"), np.nan)
        if mm >= 25:
            add("Q3.2", "|".join(nm.split("|")[1:9]), "regB_CR_variance_coverage_of_theta_full", v,
                "> 0.97 (cluster-robust variance against the design target)", v > 0.97)
    # Q3.3
    add("Q3.3", "all", "crossover_cost_ratio", np.nan, "not assessed at this depth (only c_d/c_s = 100 was run)", None)
    # Q3.4
    for tgt in ("super", "design"):
        for reg, want_c, want_w in (("A", "> 0.8", "< 0.5"), ("B", "< 0.5", "> 0.8")):
            rc_ = N3.get(f"Q3.4|theta3|donor|{tgt}|regime{reg}|spearman_ratio_vs_one_minus_R2c_raw_pooled", np.nan)
            rw = N3.get(f"Q3.4|theta3|donor|{tgt}|regime{reg}|spearman_ratio_vs_one_minus_R2w_pooled", np.nan)
            hc = rc_ > 0.8 if want_c == "> 0.8" else rc_ < 0.5
            hw = rw < 0.5 if want_w == "< 0.5" else rw > 0.8
            add("Q3.4", f"pooled|{tgt}|regime{reg}", "spearman_vs_one_minus_R2_cluster_raw", rc_, f"{want_c}", hc)
            add("Q3.4", f"pooled|{tgt}|regime{reg}", "spearman_vs_one_minus_R2_within", rw, f"{want_w}", hw)
    df = pd.DataFrame(rows)
    summ = []
    for pr, d in df.groupby("prediction"):
        h = d.holds.dropna()
        summ.append(dict(prediction=pr, scope="SUMMARY", statistic="n_holds_of_n_scored",
                         value=f"{int(h.sum())}/{len(h)}", criterion="", holds=(bool(h.all()) if len(h) else None)))
    out = pd.concat([df, pd.DataFrame(summ)], ignore_index=True)
    out.to_csv(f"{a.res}/Q3_regimes/q3_prediction_scores.csv", index=False)
    print(pd.DataFrame(summ).to_string(index=False))


if __name__ == "__main__":
    main()
