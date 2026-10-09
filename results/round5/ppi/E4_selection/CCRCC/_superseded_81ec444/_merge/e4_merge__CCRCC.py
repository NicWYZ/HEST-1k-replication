"""E4 CCRCC unit: acceptance checks and ratio tables. Run from anywhere; paths absolute."""
import os, numpy as np, pandas as pd
R = "/Users/nicolaszhang/hest-1k/HEST-1k-replication-PPI"
D = f"{R}/results/round5/ppi/E4_selection/CCRCC"
ARMS = ("hoptimus0", "uni_v2", "resnet50", "permuted")
s = pd.concat([pd.read_csv(f"{D}/{a}/e4_selection__CCRCC__{a}.csv") for a in ARMS], ignore_index=True)
g = pd.concat([pd.read_csv(f"{D}/{a}/e4_selection_genes__CCRCC__{a}.csv.gz") for a in ARMS], ignore_index=True)
KEY = ["vtag", "arm", "estimand", "n_L", "rule", "interval"]
VAL = ["n_draws", "n_genes", "emp_var_median", "est_var_over_emp_var_median", "coverage_median", "coverage_mean", "width_median"]
acc = []
# ---- acceptance 1a: D2_inf == D0, all columns
d0 = s[s.design == "D0"].set_index(KEY)[VAL].sort_index()
di = s[s.design == "D2_inf"].set_index(KEY)[VAL].sort_index()
assert d0.index.equals(di.index)
exact = bool(((d0 == di) | (d0.isna() & di.isna())).all().all())
maxdiff = float((d0 - di).abs().max().max())
acc.append(dict(check="1a_D2inf_equals_D0_summary", n_rows=len(d0), passed=exact, max_abs_diff=maxdiff))
gk = KEY + ["gene"]
gd0 = g[(g.design == "D0")] if "design" in g else None
# genes file has cell dict columns incl. design
gd0 = g[g.design == "D0"].set_index(gk)[["emp_var", "est_var", "coverage", "width"]].sort_index()
gdi = g[g.design == "D2_inf"].set_index(gk)[["emp_var", "est_var", "coverage", "width"]].sort_index()
gexact = bool(gd0.index.equals(gdi.index) and ((gd0 == gdi) | (gd0.isna() & gdi.isna())).all().all())
acc.append(dict(check="1a_D2inf_equals_D0_genes", n_rows=len(gd0), passed=gexact, max_abs_diff=float((gd0 - gdi).abs().max().max())))
# ---- acceptance 1b: D0 vs q4a_table61
q = pd.read_csv(f"{R}/results/round4/ppi/Q4a_recompute/q4a_table61.csv")
q = q[(q.vtag == "CCRCC") & (q.population == "donor") & (q.target == "design")
      & q.interval.isin(["textbook_t|fpc", "textbook_t|fpc|lin"]) & q.lambda_rule.isin(["none", "c_crossfit_design"])]
q = q.rename(columns={"lambda_rule": "rule", "emp_var_median": "q_emp", "coverage_median": "q_cov", "est_var_over_emp_var_median": "q_ratio"})
m = s[s.design == "D0"].merge(q[KEY + ["q_emp", "q_cov", "q_ratio"]], on=KEY, how="left", indicator=True)
m["matched"] = m._merge == "both"
mm = m[m.matched].copy()
mm["d_cov"] = (mm.coverage_median - mm.q_cov).abs()
mm["rel_emp"] = (mm.emp_var_median / mm.q_emp - 1).abs()
mm["rel_ratio"] = (mm.est_var_over_emp_var_median / mm.q_ratio - 1).abs()
mm["pass"] = (mm.d_cov <= 0.005) & (mm.rel_emp <= 1e-5) & (mm.rel_ratio <= 1e-5)
m[~m.matched][KEY].to_csv(f"{D}/_merge/e4_acc1_unmatched__CCRCC.csv", index=False)
mm.to_csv(f"{D}/_merge/e4_acc1_vs_q4a__CCRCC.csv", index=False)
acc.append(dict(check="1b_D0_vs_q4a_table61", n_rows=len(m), n_matched=len(mm), n_unmatched=int((~m.matched).sum()),
                passed=bool(mm["pass"].all()), n_fail=int((~mm["pass"]).sum()), max_abs_dcov=float(mm.d_cov.max()),
                max_rel_emp=float(mm.rel_emp.max()), max_rel_ratio=float(mm.rel_ratio.max()),
                unmatched_desc="; ".join(sorted({f"{a}/{e}/nL{n}/{r}|{i}" for a, e, n, r, i in m[~m.matched][["arm","estimand","n_L","rule","interval"]].itertuples(index=False)}))[:600]))
# ---- per-gene ratio to D0 classical (rule none, same interval) ----
cell = ["vtag", "arm", "estimand", "n_L", "design", "balance", "p_a", "rule", "interval"]
g["p_a"] = g["p_a"].astype(float)
base = g[(g.design == "D0") & (g.rule == "none")][["arm", "estimand", "n_L", "interval", "gene", "emp_var"]].rename(columns={"emp_var": "emp_var_D0none"})
gg = g.merge(base, on=["arm", "estimand", "n_L", "interval", "gene"], how="left")
gg["ratio"] = gg.emp_var / gg.emp_var_D0none
rat = (gg.groupby(cell, dropna=False).ratio
       .agg(ratio_median="median", ratio_p10=lambda x: x.quantile(.1), ratio_p90=lambda x: x.quantile(.9), n_genes="count").reset_index())
rat.to_csv(f"{D}/e4_ratios__CCRCC.csv", index=False)
# ---- acceptance 2: perm balance, classical (none, |lin), D2, both p_a
p = rat[(rat.design == "D2") & (rat.balance == "perm") & (rat.rule == "none") & (rat.interval == "textbook_t|fpc|lin")].copy()
p["in_band"] = p.ratio_median.between(0.93, 1.07)
p.to_csv(f"{D}/_merge/e4_acc2_perm_balance__CCRCC.csv", index=False)
acc.append(dict(check="2_perm_balance_D2_classical_ratio", n_rows=len(p), passed=bool(p.in_band.all()), n_fail=int((~p.in_band).sum()),
                min_ratio=float(p.ratio_median.min()), max_ratio=float(p.ratio_median.max())))
pd.DataFrame(acc).to_csv(f"{D}/e4_unit_acceptance__CCRCC.csv", index=False)
print(pd.DataFrame(acc).T.to_string())
