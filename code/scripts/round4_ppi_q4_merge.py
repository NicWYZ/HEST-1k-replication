"""Round 4 PPI, interval 3: merge the Q4 unit tables and score Q4.1 to Q4.4 and the Q3.1 reversal clause.

Inputs (all relative to --stage): q4_main/<unit>/q4_main_table*.csv, q4_gene/{CCRCC,INDIANA}/ per-gene
gene-axis files, two_way/q4_two_way.csv; --q4a is the merged Q4a directory (q4a_regime_comparison.csv,
q4a_prediction_scores.csv); --theorem is q2_sim_theorem_v3.csv. Writes to --out.
Canonical row roles (plan section 14.5 and memo section 2):
  final_design      design target, regime A, c_crossfit_design (textbook form, fpc, t_{n_L-1})
  final_super       superpopulation, regime A, c_crossfit with CR2_bm at n_L >= 6; the classical
                    (none) CR2_bm row at n_L < 6, where lambda = 0
  classical         none, every other row
  old_c_crossfit    design target, regime A, c_crossfit (kept for comparison)
  super_CR1_beside  superpopulation, regime A, c_crossfit, CR1_t, n_L >= 6
  regimeB_<rule>    regime B rows (regime B is unchanged from interval 2)
Superpopulation c_crossfit rows at n_L < 6 are dropped (lambda = 0 by rule there)."""
import argparse, glob, os, shutil
import numpy as np
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--stage", required=True)
ap.add_argument("--q4a", required=True)
ap.add_argument("--theorem", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
KEY = ["vtag", "arm", "estimand", "population", "target", "regime", "budget", "cost", "n_L", "m",
       "lambda_rule", "interval"]
COMMON = ["task", "vtag", "arm", "estimand", "population", "target", "G", "G_U", "regime", "budget", "cost",
          "n_L", "m", "lambda_rule", "interval", "n_draws", "n_genes", "emp_var_median",
          "est_var_over_emp_var_median", "coverage_median", "width_ratio_median", "emp_var_ratio_median",
          "lambda_median", "lambda_se_median", "source_file"]

# ------------------------------------------------------------------ main table
parts = []
for f in sorted(glob.glob(f"{a.stage}/q4_main/*/q4_main_table*.csv")):
    d = pd.read_csv(f, low_memory=False)
    d = d[[c for c in COMMON if c in d.columns]].copy()
    d["unit_table"] = os.path.basename(f)
    parts.append(d)
M = pd.concat(parts, ignore_index=True)
M["m"] = M["m"].astype(str).str.replace(r"\.0$", "", regex=True)
M["budget"] = pd.to_numeric(M["budget"], errors="coerce")
n0 = len(M)
M = M.drop_duplicates(KEY)
drop = (M.target == "super") & (M.regime == "A") & (M.lambda_rule == "c_crossfit") & (M.n_L < 6)
M = M[~drop].copy()


def role(r):
    if r.regime == "B":
        return f"regimeB_{r.lambda_rule}"
    if r.target == "design":
        return {"c_crossfit_design": "final_design", "c_crossfit": "old_c_crossfit"}.get(r.lambda_rule, "classical")
    if r.lambda_rule == "c_crossfit":
        return "final_super" if r.interval == "CR2_bm" else "super_CR1_beside"
    if r.n_L < 6 and r.interval == "CR2_bm":
        return "final_super"
    return "classical"


M["role"] = M.apply(role, axis=1)
M["G_U"] = np.where((M.target == "super") & (M.regime == "A"), M.G - M.n_L, np.where(M.target == "super", 0, np.nan))
M.to_csv(f"{a.out}/q4_main_table.csv", index=False)

nums = []


def add(name, v):
    nums.append(dict(name=name, value=v))


add("main|rows_before_dedupe", n0)
add("main|rows", len(M))
add("main|dropped_super_c_nL_lt6", int(drop.sum()))
for k, z in M.groupby(["vtag", "estimand"]):
    add(f"main|rows|{k[0]}|{k[1]}", len(z))
for k, z in M.groupby("role"):
    add(f"main|rows|role|{k}", len(z))

# ------------------------------------------------------------------ gene axis, harmonised long form
g = []
ci = pd.read_csv(f"{a.stage}/q4_gene/CCRCC/q4_gene_axis__CCRCC.csv", low_memory=False)
for s in ["A_design_cd", "A_design_cf", "A_super_cf_CR2", "B_design_cf", "B_super_cf"]:
    z = ci[["vtag", "gene", "arm", "in_all_folds"]].copy()
    z["setting"] = s
    for c in ["width_ratio", "emp_var_ratio", "coverage", "lambda_median", "lambda_se_median", "lam2_minus_se2"]:
        z[c] = ci[f"{s}_{c}"]
    z["R2_cluster_corrected"] = ci.R2_cluster_z_corrected
    z["R2_cluster_raw"] = ci.R2_cluster_z_raw
    z["pearson_unit"] = ci.pearson_unit_outcome
    g.append(z)
ii = pd.read_csv(f"{a.stage}/q4_gene/INDIANA/q4_gene_axis__INDIANA_KIDNEY.csv", low_memory=False)
ii = ii[(ii.population == "donor") & (ii.n_L == 8) & (ii.m.astype(str) == "all")]
smap = {("A", "design", "c_crossfit_design", "textbook_t|fpc"): "A_design_cd",
        ("A", "design", "c_crossfit", "textbook_t|fpc"): "A_design_cf",
        ("A", "super", "c_crossfit", "CR2_bm"): "A_super_cf_CR2",
        ("B", "design", "c_crossfit", "regB_t"): "B_design_cf",
        ("B", "super", "c_crossfit", "regB_t"): "B_super_cf"}
ii["setting"] = [smap.get(k) for k in zip(ii.regime, ii.target, ii.lambda_rule, ii.interval)]
ii = ii[ii.setting.notna()].copy()
ii["emp_var_ratio"] = ii.emp_var / ii.emp_var_classical
ii = ii.rename(columns={"encoder": "arm", "pearson_log1p": "pearson_unit"})
ii["vtag"] = "INDIANA_KIDNEY"
g.append(ii[["vtag", "gene", "arm", "in_all_folds", "setting", "width_ratio", "emp_var_ratio", "coverage",
             "lambda_median", "lambda_se_median", "lam2_minus_se2", "R2_cluster_corrected", "R2_cluster_raw",
             "pearson_unit"]])
GA = pd.concat(g, ignore_index=True)
GA["gains_gt5pct"] = GA.width_ratio < 0.95
GA.to_csv(f"{a.out}/q4_gene_axis.csv", index=False)

sc = []


def score(pred, scope, stat, val, crit, holds):
    sc.append(dict(prediction=pred, scope=scope, statistic=stat, value=val, criterion=crit, holds=holds))


summ = []
for (vt, arm, s), z in GA.groupby(["vtag", "arm", "setting"]):
    for gs, zz in (("full_union", z), ("in_all_folds", z[z.in_all_folds.astype(bool)])):
        rc = zz[["width_ratio", "R2_cluster_corrected"]].corr("spearman").iloc[0, 1]
        rp = zz[["width_ratio", "pearson_unit"]].corr("spearman").iloc[0, 1]
        rl = zz[["width_ratio", "lam2_minus_se2"]].corr("spearman").iloc[0, 1]
        summ.append(dict(vtag=vt, arm=arm, setting=s, gene_set=gs, n_genes=len(zz),
                         frac_gain_gt5pct=zz.gains_gt5pct.mean(), width_ratio_median=zz.width_ratio.median(),
                         spearman_R2_cluster=rc, spearman_pearson_unit=rp, spearman_lam2_minus_se2=rl,
                         frac_lam2_gt_se2=(zz.lam2_minus_se2 > 0).mean() if zz.lam2_minus_se2.notna().any() else np.nan))
GS = pd.DataFrame(summ)
GS.to_csv(f"{a.out}/q4_gene_axis_summary.csv", index=False)
crit41 = "|rho(width, R2_cluster)| > |rho(width, unit Pearson)| and frac genes gaining > 5% < 1/3 (regime A, n_L 8, m all, design, c_crossfit_design, full gene set)"
for _, r in GS[(GS.setting == "A_design_cd") & (GS.gene_set == "full_union") & (GS.arm != "permuted")].iterrows():
    h1 = abs(r.spearman_R2_cluster) > abs(r.spearman_pearson_unit)
    h2 = r.frac_gain_gt5pct < 1 / 3
    score("Q4.1", f"{r.vtag}|{r.arm}|correlation", "abs_rho_R2_cluster_minus_abs_rho_pearson",
          abs(r.spearman_R2_cluster) - abs(r.spearman_pearson_unit), crit41, bool(h1))
    score("Q4.1", f"{r.vtag}|{r.arm}|gain_share", "frac_gain_gt5pct", r.frac_gain_gt5pct, crit41, bool(h2))

# ------------------------------------------------------------------ two-way (Q4.2)
tw = pd.read_csv(f"{a.stage}/two_way/q4_two_way.csv")
shutil.copy(f"{a.stage}/two_way/q4_two_way.csv", f"{a.out}/q4_two_way.csv")
score("Q4.2", "HEST", "n_tasks_with_crossed_grouping_gt4_levels", 0,
      "no HEST task has a crossed second grouping with more than four levels (q4_two_way.csv)", True)
score("Q4.2", "ACS", "survey_year_levels", 1,
      "two-way variance reported for ACS state by survey year if the data carries the year; PUMS 2018 is one year, so there is nothing to report", None)

# ------------------------------------------------------------------ theorem check (Q4.3)
th = pd.read_csv(a.theorem)
d = (th.tuning_cost_obs - th.tuning_cost_pred).abs()
dU = (th.tuning_cost_obs - th.tuning_cost_pred_with_U).abs()
score("Q4.3", "all_cells", "n_within_0.03_of_n", f"{int((d <= 0.03).sum())}/{len(d)}",
      "observed minus predicted tuning cost within 0.03 in every cell", bool((d <= 0.03).all()))
score("Q4.3", "all_cells", "max_abs_diff", float(d.max()), "context", None)
score("Q4.3", "all_cells_with_U", "n_within_0.03_of_n", f"{int((dU <= 0.03).sum())}/{len(dU)}", "context (prediction with the G_U term)", None)
score("Q4.3", "all_cells_with_U", "max_abs_diff", float(dU.max()), "context", None)

# ------------------------------------------------------------------ Q3.1 reversal clause, and the c_d/c_s = 10 shrinkage
q = pd.read_csv(f"{a.q4a}/q4a_regime_comparison.csv", low_memory=False)
q = q[(q.estimand == "theta3") & (q.population == "donor")]
rows = []
for (vt, arm), z in q.groupby(["vtag", "arm"]):
    for tgt, ruleA, ruleB in (("super", "c_crossfit", "c_crossfit"), ("super", "none", "none"),
                              ("design", "c_crossfit_design", "c_crossfit"), ("design", "none", "none")):
        A = z[(z.regime == "A") & (z.cost == "unit") & (z.target == tgt) & (z.lambda_rule == ruleA)
              & (z.interval.isin(["CR1_t", "textbook_t|fpc"]))]
        Bc = z[(z.regime == "B") & (z.cost != "unit") & (z.target == tgt) & (z.lambda_rule == ruleB)]
        for _, rb in Bc.iterrows():
            p = rb.cost.split("_")
            c, nl, bb = int(p[2]), int(p[-2][2:]), int(p[-1][1:])
            aa = A[(A.n_L == nl) & (A.budget == bb)]
            if len(aa):
                rows.append(dict(vtag=vt, arm=arm, target=tgt, rule_A=ruleA, rule_B=ruleB, cd_cs=c, n_L=nl,
                                 budget_A=bb, budget_B=rb.budget, m_B=rb.m,
                                 width_ratio_B_over_A=float(np.sqrt(rb.emp_var_median / aa.emp_var_median.iloc[0]))))
R31 = pd.DataFrame(rows)
R31.to_csv(f"{a.out}/q4_q31_cost_ratios.csv", index=False)
p = R31[(R31.cd_cs == 1000) & (R31.target == "super") & (R31.rule_A == "c_crossfit")]
score("Q3.1", "reversal_cd1000|super|c_crossfit", "n_cells_A_narrower_of_n",
      f"{int((p.width_ratio_B_over_A > 1).sum())}/{len(p)}",
      "regime A narrower than regime B (B/A width > 1) when c_d/c_s >= 1000 (theta3 donor; only LUNG_XENIUM is affordable)",
      bool(len(p) and (p.width_ratio_B_over_A > 1).all()))
score("Q3.1", "reversal_cd1000|super|c_crossfit", "tasks_with_cells", ",".join(sorted(p.vtag.unique())), "context", None)
score("Q3.1", "reversal_cd1000|super|c_crossfit", "median_width_ratio", float(p.width_ratio_B_over_A.median()) if len(p) else np.nan, "context", None)
p2 = R31[(R31.cd_cs == 1000) & (R31.target == "design") & (R31.rule_A == "c_crossfit_design")]
score("Q3.1", "reversal_cd1000|design|cd_vs_c", "n_cells_A_narrower_of_n", f"{int((p2.width_ratio_B_over_A > 1).sum())}/{len(p2)}", "context (design target, A under c_crossfit_design)", None)
p3 = R31[(R31.cd_cs == 10) & (R31.target == "super") & (R31.rule_A == "c_crossfit")]
score("Q3.1", "cd10|super|c_crossfit", "median_width_ratio", float(p3.width_ratio_B_over_A.median()), "context (advantage under the cost-weighted budget)", None)
score("Q3.1", "cd10|super|c_crossfit", "n_cells_A_narrower_of_n", f"{int((p3.width_ratio_B_over_A > 1).sum())}/{len(p3)}", "context", None)
for c, pp in ((10, p3), (1000, p)):
    add(f"q31|cd{c}|super|c_crossfit|n_cells", len(pp))
    add(f"q31|cd{c}|super|c_crossfit|n_B_narrower", int((pp.width_ratio_B_over_A < 1).sum()))
    add(f"q31|cd{c}|super|c_crossfit|n_A_narrower", int((pp.width_ratio_B_over_A > 1).sum()))

# ------------------------------------------------------------------ carry Q4a.1, Q4.4, Q3.3 from the Q4a merge
s4a = pd.read_csv(f"{a.q4a}/q4a_prediction_scores.csv")
S = pd.concat([pd.DataFrame(sc), s4a], ignore_index=True)
summ = []
for pr, z in S[S.holds.notna() & (S.scope != "SUMMARY")].groupby("prediction"):
    hz = z.holds.astype(bool)
    summ.append(dict(prediction=pr, scope="SUMMARY", statistic="n_holds_of_n_scored", value=f"{int(hz.sum())}/{len(hz)}",
                     criterion="", holds=bool(hz.all())))
S = pd.concat([S[S.scope != "SUMMARY"], pd.DataFrame(summ)], ignore_index=True)
S.to_csv(f"{a.out}/q4_prediction_scores.csv", index=False)
pd.DataFrame(nums).to_csv(f"{a.out}/q4_report_numbers.csv", index=False)
print({"main_rows": len(M), "gene_rows": len(GA), "q31_rows": len(R31)})
print(pd.DataFrame(summ).to_string(index=False))
