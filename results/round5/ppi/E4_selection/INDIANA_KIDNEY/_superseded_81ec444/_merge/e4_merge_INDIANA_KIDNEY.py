"""E4 INDIANA_KIDNEY merge: acceptance 1 and 2, per gene variance ratios. Run from anywhere."""
import os, numpy as np, pandas as pd
R = "/Users/nicolaszhang/hest-1k/HEST-1k-replication-PPI"
base = f"{R}/results/round5/ppi/E4_selection/INDIANA_KIDNEY"
arms = ["hoptimus0", "uni_v2", "resnet50", "permuted"]
LIN = "textbook_t|fpc|lin"
E = pd.concat([pd.read_csv(f"{base}/{a}/e4_selection__INDIANA_KIDNEY__{a}.csv") for a in arms], ignore_index=True)
Gn = pd.concat([pd.read_csv(f"{base}/{a}/e4_selection_genes__INDIANA_KIDNEY__{a}.csv.gz") for a in arms], ignore_index=True)
q = pd.read_csv(f"{R}/results/round4/ppi/Q4a_recompute/q4a_table61.csv")
key = ["arm", "estimand", "n_L", "rule", "interval"]
num = ["n_draws", "n_genes", "emp_var_median", "est_var_over_emp_var_median", "coverage_median", "coverage_mean", "width_median", "G"]
D0 = E[E.design == "D0"].set_index(key).sort_index(); DI = E[E.design == "D2_inf"].set_index(key).sort_index()
dd = (D0[num] - DI[num]).abs().reset_index()
qq = q[(q.vtag == "INDIANA_KIDNEY") & (q.population == "donor") & (q.target == "design") & (q.interval == LIN)
       & q.lambda_rule.isin(["none", "c_crossfit_design"])].rename(columns={"lambda_rule": "rule"}).set_index(key)
j = D0.reset_index(); j = j[j.interval == LIN].set_index(key).join(qq[["emp_var_median", "coverage_median", "est_var_over_emp_var_median"]], rsuffix="_q4a")
j["matched_q4a"] = j.emp_var_median_q4a.notna()
j["d_cov"] = (j.coverage_median - j.coverage_median_q4a).abs()
j["rel_emp"] = ((j.emp_var_median - j.emp_var_median_q4a) / j.emp_var_median_q4a).abs()
j["rel_ratio"] = ((j.est_var_over_emp_var_median - j.est_var_over_emp_var_median_q4a) / j.est_var_over_emp_var_median_q4a).abs()
j["pass"] = j.matched_q4a & (j.d_cov <= 0.005) & (j.rel_emp <= 1e-5) & (j.rel_ratio <= 1e-5)
G2 = Gn[Gn.interval.isin([LIN, "strat_t"])].copy()
ev0 = G2[(G2.design == "D0") & (G2.rule == "none")].set_index(["arm", "estimand", "n_L", "gene"]).emp_var.rename("ev0")
G2 = G2.join(ev0, on=["arm", "estimand", "n_L", "gene"]); G2["ratio"] = G2.emp_var / G2.ev0; G2["p_a"] = G2.p_a.fillna(-1)
gk = ["arm", "estimand", "n_L", "design", "balance", "p_a", "rule"]
rat = G2.groupby(gk).ratio.agg(ratio_median="median", p10=lambda s: s.quantile(.1), p90=lambda s: s.quantile(.9), n_genes="count").reset_index()
rat["p_a"] = rat.p_a.replace(-1, np.nan)
inv = E[(E.design == "D2") & (E.n_no_accept > 0)].groupby(["arm", "estimand", "n_L", "design", "balance", "p_a"]).n_no_accept.max().rename("nacc").reset_index()
rat = rat.merge(inv, how="left", on=["arm", "estimand", "n_L", "design", "balance", "p_a"])
rat["flag_no_accept"] = rat.nacc.fillna(0) > 0
rat["flag_pcE_is_not_embedding"] = rat.balance.str.startswith("pcE")   # see notes: numeric columns n_spots, n_joined were used
rat.drop(columns="nacc").to_csv(f"{base}/e4_ratios__INDIANA_KIDNEY.csv", index=False)
a2 = rat[(rat.design == "D2") & (rat.balance == "perm") & (rat.rule == "none")]
rows = []
for (est, nl), g in dd.groupby(["estimand", "n_L"]):
    mx = g[num].max().max()
    rows.append(dict(check="acc1_D2inf_equals_D0", arm="all", estimand=est, n_L=nl, p_a=np.nan, value=mx, passed=bool(mx == 0),
                     note="max abs diff over summary columns" + ("; fails: candidate 0 has <2 valid labelled, NaN distance, D2 takes candidate 1999 while D0 skips the draw" if mx else "")))
for (arm, est, nl, rule), g in j.reset_index().groupby(["arm", "estimand", "n_L", "rule"]):
    r = g.iloc[0]
    rows.append(dict(check="acc1_D0_vs_q4a", arm=arm, estimand=est, n_L=nl, p_a=np.nan, value=r.d_cov, passed=bool(r["pass"]),
                     note=f"rule={rule} matched={r.matched_q4a} dcov={r.d_cov:.4g} rel_emp_var={r.rel_emp:.3g} rel_ratio={r.rel_ratio:.3g}; n_draws={r.n_draws}"))
for _, r in a2.iterrows():
    ok = bool(0.93 <= r.ratio_median <= 1.07 and not r.flag_no_accept)
    rows.append(dict(check="acc2_perm_balance_classical_ratio", arm=r.arm, estimand=r.estimand, n_L=r.n_L, p_a=r.p_a, value=r.ratio_median, passed=ok,
                     note="band 0.93-1.07" + ("; INVALID cell: NaN threshold, no draw had an accepted candidate" if r.flag_no_accept else "")))
pd.DataFrame(rows).to_csv(f"{base}/e4_unit_acceptance__INDIANA_KIDNEY.csv", index=False)
print(pd.DataFrame(rows).groupby("check").passed.agg(["sum", "count"]))
