
"""Local merge and acceptance for E4 LUNG_XENIUM (reads the four arm outputs from the 3f037cc snapshot)."""
import numpy as np, pandas as pd, os, sys
R = sys.argv[1]; Q4A = sys.argv[2]; V = "LUNG_XENIUM"
ARMS = ["hoptimus0", "uni_v2", "resnet50", "permuted"]
S = pd.concat([pd.read_csv(f"{R}/{a}/e4_selection__{V}__{a}.csv") for a in ARMS], ignore_index=True)
Gn = pd.concat([pd.read_csv(f"{R}/{a}/e4_selection_genes__{V}__{a}.csv.gz") for a in ARMS], ignore_index=True)
Gn["p_a"] = Gn["p_a"].astype(float)
key = ["arm", "estimand", "n_L", "rule", "interval"]
IV = "textbook_t|fpc|lin"
out = []
# ---- acceptance 1a: D2_inf == D0, all columns (summary rows and gene rows)
a = S[S.design == "D0"].set_index(key).sort_index()
b = S[S.design == "D2_inf"].set_index(key).sort_index()
assert a.index.equals(b.index), "index mismatch D0/D2_inf"
mc = ["n_draws", "n_genes", "emp_var_median", "est_var_over_emp_var_median", "coverage_median", "coverage_mean", "width_median", "G", "n_no_accept"]
diff = {c: float(np.nanmax(np.abs(a[c].to_numpy(float) - b[c].to_numpy(float)))) for c in mc}
ga = Gn[Gn.design == "D0"].set_index(key + ["gene"]).sort_index()
gb = Gn[Gn.design == "D2_inf"].set_index(key + ["gene"]).sort_index()
assert ga.index.equals(gb.index)
gdiff = {c: float(np.nanmax(np.abs(ga[c].to_numpy(float) - gb[c].to_numpy(float)))) for c in ["emp_var", "est_var", "coverage", "width"]}
out.append(dict(check="acc1a_D2inf_equals_D0", arm="all", estimand="all", n_L="all", n_compared=len(a), n_gene_rows=len(ga),
                max_abs_diff=max(list(diff.values()) + list(gdiff.values())), passed=max(list(diff.values()) + list(gdiff.values())) == 0.0,
                detail=str({**diff, **{"gene_" + k: v for k, v in gdiff.items()}})))
# ---- acceptance 1b: D0 vs q4a_table61
q = pd.read_csv(Q4A)
q = q[(q.vtag == V) & (q.population == "donor") & (q.target == "design") & (q.interval == IV) & q.lambda_rule.isin(["none", "c_crossfit_design"])]
d0 = S[(S.design == "D0") & (S.interval == IV)].rename(columns={"rule": "lambda_rule"})
m = d0.merge(q, on=["arm", "estimand", "lambda_rule", "n_L"], suffixes=("", "_q"), how="left", indicator=True)
unm = m[m._merge == "left_only"]
mm = m[m._merge == "both"].copy()
mm["d_cov"] = (mm.coverage_median - mm.coverage_median_q).abs()
mm["r_emp"] = (mm.emp_var_median / mm.emp_var_median_q - 1).abs()
mm["r_est"] = (mm.est_var_over_emp_var_median / mm.est_var_over_emp_var_median_q - 1).abs()
mm["ok"] = (mm.d_cov <= 0.005) & (mm.r_emp <= 1e-5) & (mm.r_est <= 1e-5)
mm.loc[:, ["arm", "estimand", "lambda_rule", "n_L", "emp_var_median", "emp_var_median_q", "coverage_median", "coverage_median_q",
           "est_var_over_emp_var_median", "est_var_over_emp_var_median_q", "d_cov", "r_emp", "r_est", "ok"]].to_csv(f"{R}/_merge/acc1b_q4a_comparison.csv", index=False)
unm[["arm", "estimand", "lambda_rule", "n_L"]].to_csv(f"{R}/_merge/acc1b_unmatched.csv", index=False)
out.append(dict(check="acc1b_D0_vs_q4a", arm="all", estimand="all", n_L="all", n_compared=len(mm), n_unmatched=len(unm),
                max_abs_diff=float(mm.d_cov.max()), passed=bool(mm.ok.all()),
                detail=f"max |d coverage_median|={mm.d_cov.max():.2e}; max rel emp_var={mm.r_emp.max():.2e}; max rel est/emp={mm.r_est.max():.2e}; n_fail={int((~mm.ok).sum())}; unmatched cells (no q4a row) = {sorted(set(zip(unm.estimand, unm.n_L, unm.lambda_rule)))}"))
# ---- per-gene ratios to D0 classical
base = Gn[(Gn.design == "D0") & (Gn.rule == "none") & (Gn.interval == IV)][["arm", "estimand", "n_L", "gene", "emp_var"]].rename(columns={"emp_var": "ev0"})
X = Gn.merge(base, on=["arm", "estimand", "n_L", "gene"], how="inner")
X = X[(X.ev0 > 0) & np.isfinite(X.emp_var)]
X["ratio"] = X.emp_var / X.ev0
# emp_var does not depend on the interval (same estimates); keep one interval per cell
first_iv = X.groupby(["design", "rule"]).interval.first().to_dict()
X = X[[first_iv[(d, r)] == i for d, r, i in zip(X.design, X.rule, X.interval)]]
gk = ["arm", "estimand", "n_L", "design", "balance", "p_a", "rule"]
X["p_a"] = X["p_a"].fillna(-1)
rt = X.groupby(gk).ratio.agg(ratio_median="median", ratio_p10=lambda s: s.quantile(.1), ratio_p90=lambda s: s.quantile(.9), n_genes="size").reset_index()
rt["p_a"] = rt["p_a"].replace(-1, np.nan)
rt.insert(0, "vtag", V)
rt.to_csv(f"{R}/e4_ratios__{V}.csv", index=False)
# ---- acceptance 2: perm balance, D2, classical
P = X[(X.design == "D2") & (X.balance == "perm") & (X.rule == "none")]
p2 = P.groupby(["arm", "estimand", "n_L", "p_a"]).ratio.median().reset_index()
for _, r in p2.iterrows():
    out.append(dict(check="acc2_perm_D2_classical_ratio_to_D0", arm=r.arm, estimand=r.estimand, n_L=int(r.n_L), p_a=r.p_a,
                    ratio_median=r.ratio, band="0.93-1.07", passed=bool(0.93 <= r.ratio <= 1.07)))
pd.DataFrame(out).to_csv(f"{R}/e4_unit_acceptance__{V}.csv", index=False)
print(pd.DataFrame(out).drop(columns=["detail"]).to_string())
print(open(f"{R}/_merge/acc1b_unmatched.csv").read()[:800])
print(out[0]["detail"]); print(out[1]["detail"])
