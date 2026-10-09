"""E4 ACS_STATES unit merge: acceptance 1 and 2 and per-gene variance ratios. Run: python merge_e4_acs.py"""
import glob, os, numpy as np, pandas as pd
R = "/Users/nicolaszhang/hest-1k/HEST-1k-replication-PPI"
LOC = f"{R}/results/round5/ppi/E4_selection/ACS_STATES"
V = "ACS_STATES"
KEY = ["vtag", "arm", "estimand", "n_L", "rule", "interval"]
sel = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"{LOC}/*__nl*/e4_selection__{V}__*.csv"))], ignore_index=True)
gen = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"{LOC}/*__nl*/e4_selection_genes__{V}__*.csv.gz"))], ignore_index=True)
sel.to_csv(f"{LOC}/e4_selection__{V}.csv", index=False)
gen.to_csv(f"{LOC}/e4_selection_genes__{V}.csv.gz", index=False)
NUM = ["n_no_accept", "n_draws", "n_genes", "emp_var_median", "est_var_over_emp_var_median", "coverage_median", "coverage_mean", "width_median"]
acc = []
# Acceptance 1a: D2_inf == D0, all numeric columns
d0 = sel[sel.design == "D0"].set_index(KEY)[NUM + ["G"]]
di = sel[sel.design == "D2_inf"].set_index(KEY)[NUM + ["G"]]
j = d0.join(di, lsuffix="_D0", rsuffix="_inf", how="outer")
diffs = [(j[c + "_D0"] - j[c + "_inf"]).abs() for c in NUM + ["G"]]
mx = max(float(np.nanmax(d.values)) for d in diffs)
nmiss = int(j.isna().any(axis=1).sum())
acc.append(dict(check="A1a_D2inf_equals_D0", arm="all", estimand="all", n_L="all", n_compared=len(j), n_unmatched=nmiss, max_abs_diff=mx, tol=0.0, passed=bool(mx == 0 and nmiss == 0)))
for (arm, est, nl), g in j.groupby(level=["arm", "estimand", "n_L"]):
    m = max(float(np.nanmax((g[c + "_D0"] - g[c + "_inf"]).abs().values)) for c in NUM + ["G"])
    acc.append(dict(check="A1a_D2inf_equals_D0", arm=arm, estimand=est, n_L=nl, n_compared=len(g), n_unmatched=int(g.isna().any(axis=1).sum()), max_abs_diff=m, tol=0.0, passed=bool(m == 0)))
# genes file too
gk = KEY + ["gene"]
g0 = gen[gen.design == "D0"].set_index(gk)[["emp_var", "est_var", "coverage", "width"]]
gi = gen[gen.design == "D2_inf"].set_index(gk)[["emp_var", "est_var", "coverage", "width"]]
gj = g0.join(gi, lsuffix="_D0", rsuffix="_inf", how="outer")
gm = max(float(np.nanmax((gj[c + "_D0"] - gj[c + "_inf"]).abs().values)) for c in ["emp_var", "est_var", "coverage", "width"])
acc.append(dict(check="A1a_D2inf_equals_D0_genes_file", arm="all", estimand="all", n_L="all", n_compared=len(gj), n_unmatched=int(gj.isna().any(axis=1).sum()), max_abs_diff=gm, tol=0.0, passed=bool(gm == 0 and not gj.isna().any().any())))
# Acceptance 1b: D0 vs q4a
q = pd.read_csv(f"{R}/results/round4/ppi/Q4a_recompute/q4a_table61.csv")
q = q[(q.vtag == V) & (q.population == "donor") & (q.target == "design") & (q.interval == "textbook_t|fpc|lin") & q.lambda_rule.isin(["none", "c_crossfit_design"])]
q = q.rename(columns={"lambda_rule": "rule"})
q["interval"] = "textbook_t|fpc|lin"
qk = q.set_index(KEY)[["emp_var_median", "coverage_median", "est_var_over_emp_var_median"]]
dd = sel[(sel.design == "D0") & (sel.interval == "textbook_t|fpc|lin")].set_index(KEY)[["emp_var_median", "coverage_median", "est_var_over_emp_var_median"]]
m = dd.join(qk, lsuffix="_e4", rsuffix="_q4a", how="left")
rows = []
for c, tol, rel in [("emp_var_median", 1e-5, True), ("coverage_median", 0.005, False), ("est_var_over_emp_var_median", 1e-5, True)]:
    a, b = m[c + "_e4"], m[c + "_q4a"]
    dif = ((a - b).abs() / b.abs()) if rel else (a - b).abs()
    m[c + "_diff"] = dif
    m[c + "_ok"] = dif <= tol
m["matched"] = m["emp_var_median_q4a"].notna()
m["all_ok"] = m["matched"] & m[[c + "_ok" for c in ["emp_var_median", "coverage_median", "est_var_over_emp_var_median"]]].all(axis=1)
m.reset_index().to_csv(f"{LOC}/_merge/acceptance1_D0_vs_q4a__{V}.csv", index=False)
mm = m.reset_index()
for (arm, est, rule), g in mm.groupby(["arm", "estimand", "rule"]):
    gg = g[g.matched]
    acc.append(dict(check="A1b_D0_vs_q4a", arm=arm, estimand=est, n_L=",".join(map(str, g.n_L)) + f" (matched {','.join(map(str, gg.n_L))})", rule=rule,
                    n_compared=len(gg), n_unmatched=int((~g.matched).sum()),
                    max_abs_diff=float(gg[["emp_var_median_diff", "est_var_over_emp_var_median_diff"]].max().max()) if len(gg) else np.nan,
                    max_cov_diff=float(gg.coverage_median_diff.max()) if len(gg) else np.nan, tol="rel 1e-5 var; 0.005 cov", passed=bool(gg.all_ok.all()) if len(gg) else False))
# per-gene ratios to D0 classical
base = gen[(gen.design == "D0") & (gen.rule == "none") & (gen.interval == "textbook_t|fpc|lin")][["arm", "estimand", "n_L", "gene", "emp_var"]].rename(columns={"emp_var": "emp_var_D0cl"})
# emp_var is interval independent; use one interval per cell
chk = gen.groupby(["arm", "estimand", "n_L", "design", "balance", "p_a", "rule", "gene"], dropna=False).emp_var.agg(lambda s: s.max() - s.min()).max()
g1 = gen[((gen.design != "D1") & (gen.interval == "textbook_t|fpc|lin")) | ((gen.design == "D1") & (gen.interval == "strat_t"))].copy()
g1 = g1.merge(base, on=["arm", "estimand", "n_L", "gene"], how="left")
g1["ratio"] = g1.emp_var / g1.emp_var_D0cl
cell = ["arm", "estimand", "G", "n_L", "design", "balance", "p_a", "rule"]
rat = g1.groupby(cell, dropna=False).ratio.agg(n_genes="count", ratio_median="median", ratio_p10=lambda s: s.quantile(.1), ratio_p90=lambda s: s.quantile(.9)).reset_index()
rat.insert(0, "vtag", V)
rat.to_csv(f"{LOC}/e4_ratios__{V}.csv", index=False)
# Acceptance 2: perm balance, D2, classical (rule none, |lin) vs D0
a2 = rat[(rat.design == "D2") & (rat.balance == "perm") & (rat.rule == "none")]
for _, r in a2.iterrows():
    acc.append(dict(check="A2_perm_balance_classical_ratio", arm=r.arm, estimand=r.estimand, n_L=r.n_L, p_a=r.p_a, n_compared=r.n_genes, max_abs_diff=r.ratio_median, tol="0.93-1.07", passed=bool(0.93 <= r.ratio_median <= 1.07)))
A = pd.DataFrame(acc)
A.insert(0, "vtag", V)
A.to_csv(f"{LOC}/e4_unit_acceptance__{V}.csv", index=False)
print("emp_var max spread across intervals within cell:", chk)
