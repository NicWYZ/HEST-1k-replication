"""Merge E4 CCRCC_merged jobs and compute acceptance 1, acceptance 2 and variance ratios (local)."""
import glob, os, numpy as np, pandas as pd
R = "/Users/nicolaszhang/hest-1k/HEST-1k-replication-PPI"
T = f"{R}/results/round5/ppi/E4_selection/CCRCC_merged"
V = "CCRCC_merged"
rows = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"{T}/*__nl*/e4_selection__*.csv"))], ignore_index=True)
genes = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"{T}/*__nl*/e4_selection_genes__*.csv.gz"))], ignore_index=True)
for d in (rows, genes):
    d["p_a"] = d["p_a"].fillna(-1.0)
key = ["vtag", "arm", "estimand", "n_L", "rule", "interval"]
CLS = "textbook_t|fpc|lin"
out = []
# ---- acceptance 1a: D2_inf == D0 exactly
d0 = rows[rows.design == "D0"].set_index(key)
di = rows[rows.design == "D2_inf"].set_index(key)
assert d0.index.equals(di.index) or set(d0.index) == set(di.index)
di = di.loc[d0.index]
cols = [c for c in rows.columns if c not in key + ["design", "balance", "p_a"]]
num = [c for c in cols if rows[c].dtype.kind in "fi"]
maxdiff = float(np.nanmax(np.abs(d0[num].to_numpy(float) - di[num].to_numpy(float))))
nneq = int((~((d0[num].to_numpy(float) == di[num].to_numpy(float)) | (d0[num].isna().to_numpy() & di[num].isna().to_numpy()))).sum())
out.append(dict(check="A1a_D2inf_equals_D0", scope="all arms, estimands, n_L, rules, intervals", n_compared=len(d0), max_abs_diff=maxdiff,
                n_fail=nneq, passed=nneq == 0, detail="all non-key columns"))
# genes-level too
kg = key + ["gene"]
g0 = genes[genes.design == "D0"].set_index(kg).sort_index()
gi = genes[genes.design == "D2_inf"].set_index(kg).sort_index()
gnum = ["emp_var", "est_var", "coverage", "width"]
gd = float(np.nanmax(np.abs(g0[gnum].to_numpy() - gi[gnum].reindex(g0.index).to_numpy())))
out.append(dict(check="A1a_D2inf_equals_D0_genes", scope="gene-level", n_compared=len(g0), max_abs_diff=gd, n_fail=int(gd != 0), passed=gd == 0, detail="emp_var, est_var, coverage, width"))
# ---- acceptance 1b: D0 vs q4a
q = pd.read_csv(f"{R}/results/round4/ppi/Q4a_recompute/q4a_table61.csv")
q = q[(q.vtag == V) & (q.population == "donor") & (q.target == "design") & (q.interval == "textbook_t|fpc|lin")].rename(columns={"lambda_rule": "rule"})
q["interval"] = CLS
m = d0.reset_index()
m = m[(m.interval == CLS) & m.rule.isin(["none", "c_crossfit_design"])]
mm = m.merge(q, on=key, how="left", suffixes=("", "_q4a"))
have = mm["emp_var_median_q4a"].notna()
cmp = mm[have].copy()
cmp["d_emp_rel"] = (cmp.emp_var_median - cmp.emp_var_median_q4a).abs() / cmp.emp_var_median_q4a.abs()
cmp["d_cov"] = (cmp.coverage_median - cmp.coverage_median_q4a).abs()
cmp["d_ratio_rel"] = (cmp.est_var_over_emp_var_median - cmp.est_var_over_emp_var_median_q4a).abs() / cmp.est_var_over_emp_var_median_q4a.abs()
cmp["ok"] = (cmp.d_emp_rel <= 1e-5) & (cmp.d_cov <= 0.005) & (cmp.d_ratio_rel <= 1e-5)
cmp[key + ["emp_var_median", "emp_var_median_q4a", "d_emp_rel", "coverage_median", "coverage_median_q4a", "d_cov",
           "est_var_over_emp_var_median", "est_var_over_emp_var_median_q4a", "d_ratio_rel", "ok"]].to_csv(f"{T}/_merge/acceptance1_q4a_comparison.csv", index=False)
nomatch = mm[~have][key]
nomatch.to_csv(f"{T}/_merge/acceptance1_unmatched_rows.csv", index=False)
out.append(dict(check="A1b_D0_vs_q4a_table61", scope=f"rules none, c_crossfit_design; interval {CLS}", n_compared=len(cmp), n_unmatched=len(nomatch),
                max_rel_emp_var=float(cmp.d_emp_rel.max()), max_abs_coverage=float(cmp.d_cov.max()), max_rel_est_over_emp=float(cmp.d_ratio_rel.max()),
                n_fail=int((~cmp.ok).sum()), passed=bool(cmp.ok.all()),
                detail="unmatched: " + "; ".join(sorted({f"{r.arm}/{r.estimand}/nL{r.n_L}/{r.rule}" for r in nomatch.itertuples()}))[:400]))
# ---- ratios to D0 classical, per gene
base = genes[(genes.design == "D0") & (genes.rule == "none") & (genes.interval == CLS)][["arm", "estimand", "n_L", "gene", "emp_var"]].rename(columns={"emp_var": "ev0"})
gg = genes[genes.interval == CLS].merge(base, on=["arm", "estimand", "n_L", "gene"], how="inner")
gg["ratio"] = gg.emp_var / gg.ev0
gk = ["vtag", "arm", "estimand", "G", "n_L", "design", "balance", "p_a", "rule"]
rat = gg.groupby(gk).ratio.agg(ratio_median="median", ratio_p10=lambda s: s.quantile(.1), ratio_p90=lambda s: s.quantile(.9), n_genes="count").reset_index()
nacc = rows[rows.interval == CLS][gk[:-1] + ["rule", "n_no_accept"]].drop_duplicates()
rat = rat.merge(nacc, on=gk, how="left")
rat.loc[rat.p_a < 0, "p_a"] = np.nan
rat.to_csv(f"{T}/e4_ratios__{V}.csv", index=False)
# ---- acceptance 2
pm = rat[(rat.design == "D2") & (rat.balance == "perm") & (rat.rule == "none")].copy()
pm["in_band"] = pm.ratio_median.between(0.93, 1.07)
pm.to_csv(f"{T}/_merge/acceptance2_perm_balance.csv", index=False)
out.append(dict(check="A2_perm_balance_classical_var_ratio", scope="D2 balance=perm, p_a 0.1 and 0.01, rule none, |lin; per arm, estimand, n_L",
                n_compared=len(pm), min_ratio=float(pm.ratio_median.min()), max_ratio=float(pm.ratio_median.max()),
                n_fail=int((~pm.in_band).sum()), passed=bool(pm.in_band.all()), detail="band 0.93-1.07, median over genes of per-gene ratio"))
# ---- no-accept
na = rows[rows.n_no_accept > 0][["arm", "estimand", "n_L", "design", "balance", "p_a", "n_no_accept"]].drop_duplicates()
na.to_csv(f"{T}/_merge/no_accept_draws.csv", index=False)
out.append(dict(check="no_accepted_candidate", scope="all D2 cells", n_compared=int((rows.design == "D2").sum()), n_fail=int(len(na)), passed=len(na) == 0,
                detail=f"max n_no_accept {int(rows.n_no_accept.max())}"))
res = pd.DataFrame(out)
res.to_csv(f"{T}/e4_unit_acceptance__{V}.csv", index=False)
rows.to_csv(f"{T}/_merge/e4_selection_rows_merged__{V}.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30); pd.set_option("display.max_colwidth", 120)
print(res.T.to_string())
print(pm.groupby(["arm", "estimand", "n_L"]).ratio_median.agg(["min", "max"]).round(3).to_string())
