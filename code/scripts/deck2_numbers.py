#!/usr/bin/env python
"""Build results/summary/deck2_numbers.csv, every number the second advisor deck quotes.

Each row is (id, value, shown_as, slide_topic, what, source_file, how). Nothing is typed in:
every value is computed here from the file named in source_file. Run from the repository root.
    python code/scripts/deck2_numbers.py
"""
import math
import pandas as pd

ROWS = []


def add(id_, value, shown, topic, what, src, how):
    ROWS.append(dict(id=id_, value=value, shown_as=shown, slide_topic=topic, what=what,
                     source_file=src, how=how))


def f2(x):
    return f"{x:.2f}"


# ---------------------------------------------------------------- data sets
src = "results/round4/ppi/Q5_joint/q5_cluster_table.csv"
c = pd.read_csv(src)
h = c[c.arm == "hoptimus0"]
for task in ["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM"]:
    s = h[h.task == task]
    add(f"data|{task}|donors", len(s), str(len(s)), "data", "donor units in the task", src, "rows for one encoder")
    add(f"data|{task}|spots", int(s.spot_count.sum()), f"{int(s.spot_count.sum()):,}", "data", "spots in the task", src, "sum of spot_count")
    add(f"data|{task}|spots_per_donor_median", float(s.spot_count.median()), f"{s.spot_count.median():.0f}", "data",
        "median spots per donor", src, "median of spot_count")
    add(f"data|{task}|genes", int(s.n_genes.iloc[0]), str(int(s.n_genes.iloc[0])), "data", "genes analysed", src, "n_genes")
src = "results/round4/ppi/Q4a_recompute/q4a_table61.csv"
T = pd.read_csv(src)
for v in ["ACS_STATES", "ACS_CA_PUMA"]:
    G = int(T[T.vtag == v].G.iloc[0])
    add(f"data|{v}|clusters", G, str(G), "data", "clusters in the task", src, "column G")

import json
src = "results/round4/ppi/Q0_setup/acs_pums2018/acs_pums_task_def.json"
nu = json.load(open(src))["n_units"]
add("data|ACS|people", nu, f"{nu:,}", "data", "people in the ACS 2018 income task", src, "n_units")

# ---------------------------------------------------------------- first experiments
src = "results/round3/A1_coverage/a1_coverage_by_design.csv"
a1 = pd.read_csv(src)
for d in a1[a1.score == "abs"].itertuples():
    add(f"coverage_by_design|{d.design}", d.coverage_mean, f2(d.coverage_mean), "roadblocks",
        "coverage at nominal 0.90, absolute score, mean over cells", src, f"design={d.design}, score=abs")
src = "results/round3/A2_conditional/a2_unit_intervention.csv"
a2 = pd.read_csv(src)
f = a2[(a2.scope == "fold") & (a2.score == "abs")]
add("unit_vs_block|donor_calibrated", f.coverage__C_unit.mean(), f2(f.coverage__C_unit.mean()), "roadblocks",
    "coverage when calibration scores come from held-out donors", src, "mean over fold rows")
add("unit_vs_block|block_calibrated", f.coverage__C_block.mean(), f2(f.coverage__C_block.mean()), "roadblocks",
    "coverage when calibration scores come from blocks inside training slides", src, "mean over fold rows")
src = "results/round3/B2_semisynthetic/b2_coverage.csv"
b2 = pd.read_csv(src)
cl = b2[b2.estimator == "classical"].groupby("variance").coverage.mean()
for k, name in [("iid", "spot_level"), ("cluster", "donor_clustered_t"), ("boot", "donor_bootstrap")]:
    add(f"interval_coverage|{name}", cl[k], f2(cl[k]), "first experiments",
        "coverage of a 90% interval for a population quantity, classical estimator", src, f"mean over cells, variance={k}")
src = "results/round4/conformal/C3_real/c3_report_numbers.csv"
c3 = pd.read_csv(src)


def c3v(q, scope):
    r = c3[(c3.quantity == q) & (c3.scope == scope)]
    assert len(r) == 1, (q, scope, len(r))
    return float(r.value.iloc[0])


for K in [10, 12, 14, 16, 18, 20]:
    sc = f"CCRCC alpha=0.1 K={K}"
    add(f"hcp|CCRCC|K{K}|coverage", c3v("hcp coverage, mean over encoders", sc), f2(c3v("hcp coverage, mean over encoders", sc)),
        "prediction sets", "HCP coverage", src, sc)
    add(f"hcp|CCRCC|K{K}|width_over_pooled", c3v("hcp/pooled mean width, mean over encoders", sc),
        f2(c3v("hcp/pooled mean width, mean over encoders", sc)), "prediction sets", "HCP width over pooled width", src, sc)
    add(f"pooled|CCRCC|K{K}|coverage", c3v("pooled coverage, mean over encoders", sc),
        f2(c3v("pooled coverage, mean over encoders", sc)), "prediction sets", "pooled interval coverage", src, sc)

# ---------------------------------------------------------------- result 1, the interval
src = "results/round4/ppi/Q1_estimator/q1_coverage_by_G.csv"
q = pd.read_csv(src)


def q1(target, form, rule, interval, fpc, G, col="cov_median"):
    r = q[(q.target == target) & (q.form == form) & (q.lambda_rule == rule) & (q.interval == interval)
          & (q.fpc == fpc) & (q.G_L == G)]
    assert len(r) == 1, (target, form, rule, interval, fpc, G, len(r))
    return float(r[col].iloc[0])


for rule, name in [("a_b1", "same_clusters_rule1"), ("b_cluster", "same_clusters_rule2"), ("c_crossfit", "cross_fitted")]:
    for G in [4, 6, 8, 12, 20]:
        v = q1("super", "complement", rule, "CR1_t", False, G)
        add(f"sim_coverage|super|{name}|G{G}", v, f2(v), "result 1", "simulated coverage, lambda tuning rule", src,
            f"super, complement, {rule}, CR1_t, G_L={G}, cov_median")
    qr = pd.read_csv("results/round4/ppi/Q1_estimator/q1_report_numbers.csv").set_index("name").value
    for tag, lab in [("r>0", "informative_predictor"), ("r0", "uninformative_predictor")]:
        k = f"S|super|{rule}|CR1_t|GL4|{tag}|width_ratio_median"
        add(f"sim_width|super|{name}|G4|{lab}", qr[k], f2(qr[k]), "result 1", "median PPI width over classical width, four clusters",
            "results/round4/ppi/Q1_estimator/q1_report_numbers.csv", k)
for G in [4, 6, 8, 12, 20]:
    v = q1("design", "complement", "a_b1", "CR1_t", False, G)
    add(f"sim_coverage|design|no_fpc|G{G}", v, f2(v), "result 1", "design target, no finite-population correction", src,
        f"design, complement, a_b1, CR1_t, fpc False, G_L={G}")
    v = q1("design", "textbook", "c_crossfit", "textbook_t", True, G)
    add(f"sim_coverage|design|fpc_crossfit|G{G}", v, f2(v), "result 1",
        "design target, finite-population correction and cross-fitting", src, f"design, textbook, c_crossfit, textbook_t, fpc True, G_L={G}")
src = "results/round4/ppi/Q5a/q5a_design_variance_before_after.csv"
ba = pd.read_csv(src)
s = ba[(ba.vtag == "ACS_STATES") & (ba.estimand == "theta2") & (ba.population == "donor") & (ba.target == "design")
       & (ba.lambda_rule != "none") & (ba.n_L >= 6)]
add("variance_fix|ACS_states|before_min", s.est_var_over_emp_var_median_before.min(), f"{s.est_var_over_emp_var_median_before.min():.0f}",
    "result 1", "estimated over empirical variance before the extra term", src, "min over PPI rules and n_L>=6")
add("variance_fix|ACS_states|before_max", s.est_var_over_emp_var_median_before.max(), f"{s.est_var_over_emp_var_median_before.max():.0f}",
    "result 1", "same, max", src, "max")
add("variance_fix|ACS_states|after_min", s.est_var_over_emp_var_median_after.min(), f2(s.est_var_over_emp_var_median_after.min()),
    "result 1", "estimated over empirical variance after", src, "min")
add("variance_fix|ACS_states|after_max", s.est_var_over_emp_var_median_after.max(), f2(s.est_var_over_emp_var_median_after.max()),
    "result 1", "same, max", src, "max")

# ---------------------------------------------------------------- result 2 and 3, gain and tuning
src_r = "results/round4/ppi/Q2_theory/q2_cluster_r2.csv"
r2 = pd.read_csv(src_r)
r2 = r2[(r2.scale == "z") & (r2.population == "donor") & (r2.estimand == "theta3")]
R = r2.groupby(["vtag", "arm"])[["R2_cluster_raw", "R2_within"]].median()
src_t = "results/round4/ppi/Q4a_recompute/q4a_table61.csv"
D = T[(T.estimand == "theta3") & (T.population == "donor") & (T.target == "design")
      & (T.lambda_rule == "c_crossfit_design") & (T.interval == "textbook_t|fpc|lin")]
for (v, arm), row in R.iterrows():
    if v == "CCRCC_merged":
        continue
    rc = float(row.R2_cluster_raw)
    add(f"R2_cluster|{v}|{arm}", rc, f2(rc), "result 2", "cluster-level R-squared, slope estimand, median over genes", src_r,
        "scale z, donor, theta3, R2_cluster_raw median")
    add(f"floor|{v}|{arm}", 1 - rc, f2(1 - rc), "result 2", "one minus cluster-level R-squared", src_r, "derived: 1 - R2_cluster")
    add(f"R2_within|{v}|{arm}", float(row.R2_within), f2(row.R2_within), "result 4", "within-cluster R-squared", src_r, "R2_within median")
    if arm != "permuted" and rc > 0:
        be = 4 + 2 / rc
        add(f"break_even|{v}|{arm}", be, f"{be:.1f}", "result 3", "break-even labelled clusters, 4 + 2/R2_cluster", src_r,
            "derived from the rule and R2_cluster")
    for n in sorted(D[(D.vtag == v) & (D.arm == arm)].n_L.unique()):
        x = D[(D.vtag == v) & (D.arm == arm) & (D.n_L == n)]
        assert len(x) == 1
        add(f"ratio|{v}|{arm}|nL{n}", float(x.emp_var_ratio_median.iloc[0]), f2(x.emp_var_ratio_median.iloc[0]), "result 2 and 3",
            "PPI over classical empirical variance, masking draws", src_t, "theta3 donor design c_crossfit_design lin")
src = "results/round4/ppi/Q4_tables/q4_gene_axis_summary.csv"
ga = pd.read_csv(src)
s = ga[(ga.vtag == "CCRCC") & (ga.setting == "A_design_cd_lin") & (ga.gene_set == "full_union") & (ga.arm != "permuted")]
for r in s.itertuples():
    add(f"gene_axis|CCRCC|{r.arm}|spearman_cluster", r.spearman_R2_cluster, f2(r.spearman_R2_cluster), "result 2",
        "Spearman of per-gene width ratio with cluster-level R-squared", src, "A_design_cd_lin, full_union")
    add(f"gene_axis|CCRCC|{r.arm}|spearman_unit", r.spearman_pearson_unit, f2(r.spearman_pearson_unit), "result 2",
        "Spearman with unit-level correlation", src, "A_design_cd_lin, full_union")
    add(f"gene_axis|CCRCC|{r.arm}|n_genes", int(r.n_genes), str(int(r.n_genes)), "result 2", "genes", src, "n_genes")
src = "results/round4/ppi/Q5a/q5a_spot_weighted_permuted.csv"
sw = pd.read_csv(src)
for v in ["CCRCC", "LUNG_XENIUM"]:
    x = sw[(sw.vtag == v) & (sw.estimand == "theta3") & (sw.n_L >= 6)]
    add(f"spot_weighted_permuted|{v}|min", x.emp_var_ratio_median.min(), f2(x.emp_var_ratio_median.min()), "result 2",
        "permuted predictor, unit-weighted slope, variance ratio", src, "theta3, n_L>=6, min")
    add(f"spot_weighted_permuted|{v}|max", x.emp_var_ratio_median.max(), f2(x.emp_var_ratio_median.max()), "result 2", "same, max", src, "max")
src = "results/round4/ppi/Q2_theory/theorem_v3/q2_sim_theorem_v3.csv"
th = pd.read_csv(src)
add("tuning_cost|sim|max_abs_diff", th.tuning_cost_obs_minus_pred.abs().max(), f"{th.tuning_cost_obs_minus_pred.abs().max():.3f}",
    "result 3", "largest gap between observed and predicted tuning cost", src, "max |tuning_cost_obs_minus_pred| over cells")
add("tuning_cost|sim|cells", len(th), str(len(th)), "result 3", "simulation cells", src, "rows")
big = th[(th.G_U == 100) & (th.m == 5000)]
add("theorem|sim|oracle_minus_floor_min", (big.oracle_emp_var_ratio - big.one_minus_R2_exact).min(),
    f2((big.oracle_emp_var_ratio - big.one_minus_R2_exact).min()), "result 2", "best-lambda ratio minus floor", src, "G_U=100, m=5000")
add("theorem|sim|oracle_minus_floor_max", (big.oracle_emp_var_ratio - big.one_minus_R2_exact).max(),
    f2((big.oracle_emp_var_ratio - big.one_minus_R2_exact).max()), "result 2", "same, max", src, "G_U=100, m=5000")

# ---------------------------------------------------------------- result 4, regimes
src = "results/round4/ppi/Q4_tables/q4_report_numbers.csv"
rn = pd.read_csv(src).set_index("name").value
add("regimes|cost10|cells", rn["q31|cd10|super|c_crossfit|n_cells"], f"{rn['q31|cd10|super|c_crossfit|n_cells']:.0f}", "result 4",
    "cells compared at a cluster cost of 10 units", src, "name q31|cd10|super|c_crossfit|n_cells")
add("regimes|cost10|B_narrower", rn["q31|cd10|super|c_crossfit|n_B_narrower"], f"{rn['q31|cd10|super|c_crossfit|n_B_narrower']:.0f}",
    "result 4", "cells where regime B is narrower", src, "name q31|cd10|super|c_crossfit|n_B_narrower")
src = "results/round4/ppi/Q4_tables/q4_main_table.csv"
M = pd.read_csv(src, low_memory=False)
B = M[(M.role == "regimeB_c_crossfit") & (M.estimand == "theta3") & (M.population == "donor") & (M.target == "design")
      & (M.cost.astype(str) == "unit")]
for (v, arm), x in B.groupby(["vtag", "arm"]):
    if v == "CCRCC_merged":
        continue
    w = float(x.width_ratio_median.median())
    add(f"regimeB_width|{v}|{arm}", w, f2(w), "result 4", "regime B, PPI width over classical width", src,
        "regimeB_c_crossfit, theta3 donor design, unit cost, median over budgets")
    rw = float(R.loc[(v, arm), "R2_within"])
    add(f"regimeB_predicted|{v}|{arm}", math.sqrt(max(0, 1 - rw)), f2(math.sqrt(max(0, 1 - rw))), "result 4",
        "square root of one minus within-cluster R-squared", src_r, "derived")
src = "results/round4/ppi/Q3_regimes/q3_report_numbers.csv"
q3 = pd.read_csv(src).set_index("name").value
for t in ["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM"]:
    for n in [4, 8]:
        k = f"Q3.1|{t}|hoptimus0|theta3|donor|c_crossfit|super|B2400|nL{n}|width_ratio_B_over_A"
        add(f"regimes|{t}|B2400|nL{n}|B_over_A", q3[k], f2(q3[k]), "result 4", "regime B width over regime A width, equal budget", src, k)
src = "results/round4/ppi/Q2_theory/q2_report_numbers.csv"
q2 = pd.read_csv(src).set_index("name").value
for t, arm in [("CCRCC", "hoptimus0"), ("INDIANA_KIDNEY", "hoptimus0"), ("LUNG_XENIUM", "hoptimus0"), ("ACS_STATES", "package")]:
    for rule, nm in [("none", "classical"), ("c_crossfit", "with_predictor")]:
        k = f"Q2.3|{t}|{arm}|theta3|donor|{rule}|m_star_cd_cs_100_median"
        add(f"allocation|{t}|{nm}", q2[k], f"{q2[k]:.0f}", "result 4", "optimal units per cluster at cost ratio 100", src, k)

# ---------------------------------------------------------------- result 5, prediction sets
src = "results/round4/conformal/C3_real/c3_o_sweep_by_task.csv"
o = pd.read_csv(src)
o = o[(o.alpha == 0.1) & (o.K == 10) & (o.score == "abs")]
g = o.groupby(["task", "method", "o"])[["coverage", "width_mean", "finite"]].mean()
for (task, method, oo), row in g.iterrows():
    if task == "CCRCC_23merged" or method not in ("pooled", "hcp", "ghcp", "within", "within_plain"):
        continue
    add(f"sets|{task}|{method}|o{oo}|coverage", row.coverage, f2(row.coverage) if row.coverage < 0.99 else f"{row.coverage:.3f}",
        "result 5", "coverage, 10 calibration clusters, mean over encoders", src, "alpha 0.1, K 10, abs score")
    if row.finite > 0.999:
        add(f"sets|{task}|{method}|o{oo}|width", row.width_mean, f2(row.width_mean), "result 5", "mean width", src, "same")
src = "results/round4/conformal/C2_candidates/lower_bound/c2_lb_beta_star.csv"
lb = pd.read_csv(src)
for r in lb[(lb.alpha == 0.1) & (lb.K.isin([4, 5, 6, 7, 8]))].itertuples():
    add(f"lower_bound|K{r.K}|coverage_floor", r.min_coverage_any_valid, f"{r.min_coverage_any_valid:.3f}", "result 5",
        "coverage floor for a finite valid method, alpha 0.1", src, "min_coverage_any_valid")
    add(f"lower_bound|K{r.K}|forced_infinite_prob", 1 - 0.1 * (r.K + 1), f2(1 - 0.1 * (r.K + 1)), "result 5",
        "forced probability of an infinite set, 1 - alpha(K+1)", src, "derived from K and alpha")
for fsrc, n in [("results/round4/conformal/C1_testbed/ghcp_repro_longleaf/compare/c1_ghcp_reproduction.csv", "simulation"),
                ("results/round4/conformal/C3_real/frag_ACS_o/acs_ghcp_reproduction.csv", "acs")]:
    d = pd.read_csv(fsrc)
    add(f"ghcp_reproduction|{n}|values", len(d), str(len(d)), "result 5", "published values compared", fsrc, "rows")

# ---------------------------------------------------------------- result 6, joint design
src = "results/round4/ppi/Q5_joint/q5_joint_design.csv"
J = pd.read_csv(src)
for v, m in [("CCRCC", 14), ("CCRCC", 84), ("INDIANA_KIDNEY", 6), ("INDIANA_KIDNEY", 51), ("LUNG_XENIUM", 36)]:
    x = J[(J.vtag == v) & (J.m.round() == m)]
    x = x.iloc[[0]]
    for col, nm in [("regB_width_ratio_theta3", "ci_width_ratio"), ("regB_coverage_theta3", "ci_coverage"),
                    ("cheapest_coverage", "set_coverage"), ("cheapest_width_mean_finite", "set_width")]:
        add(f"joint|{v}|m{m}|{nm}", float(x[col].iloc[0]), f2(float(x[col].iloc[0])), "result 6", nm, src, f"m={m}, {col}")
    add(f"joint|{v}|m{m}|cheapest_set", 0, str(x.cheapest_valid_set.iloc[0]), "result 6", "cheapest valid set (name in shown_as)", src,
        "cheapest_valid_set")

out = pd.DataFrame(ROWS)
assert out.id.is_unique, out[out.id.duplicated()].id.tolist()
out.to_csv("results/summary/deck2_numbers.csv", index=False)
print(len(out), "rows written to results/summary/deck2_numbers.csv")
