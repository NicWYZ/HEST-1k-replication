"""E4 unit ACS_CA_PUMA: acceptance 1 (D2_inf == D0; D0 reproduces q4a_table61), acceptance 2 (perm balance
band 0.93-1.07), per-gene ratios to D0 classical. Run from anywhere: python e4_unit_merge_ACS_CA_PUMA.py"""
import os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); L = os.path.dirname(HERE)
R = os.path.abspath(os.path.join(L, *[".."] * 5))
VT, ARMS = "ACS_CA_PUMA", ("package", "permuted")
S = pd.concat([pd.read_csv(f"{L}/{a}/e4_selection__{VT}__{a}.csv") for a in ARMS])
G = pd.concat([pd.read_csv(f"{L}/{a}/e4_selection_genes__{VT}__{a}.csv.gz") for a in ARMS])
key = ["vtag", "arm", "estimand", "n_L", "rule", "interval"]
acc = []
# Acceptance 1a: D2_inf == D0, all columns (summary rows and gene rows)
for name, T, extra in (("summary", S, ["n_draws", "n_genes", "emp_var_median", "est_var_over_emp_var_median", "coverage_median", "coverage_mean", "width_median"]),
                       ("genes", G, ["emp_var", "est_var", "coverage", "width"])):
    d0 = T[T.design == "D0"].set_index(key + (["gene"] if name == "genes" else []))[extra]
    di = T[T.design == "D2_inf"].set_index(key + (["gene"] if name == "genes" else []))[extra]
    j = d0.join(di, rsuffix="_inf", how="outer")
    mx = max(float((j[c] - j[c + "_inf"]).abs().max()) for c in extra)
    nmis = int(j.isna().any(axis=1).sum())
    acc.append(dict(check=f"A1a D2_inf rows == D0 rows ({name})", n_rows=len(j), n_unmatched=nmis, max_abs_diff=mx, passed=bool(nmis == 0 and mx == 0)))
# Acceptance 1b: D0 vs q4a_table61
q = pd.read_csv(f"{R}/results/round4/ppi/Q4a_recompute/q4a_table61.csv")
q = q[(q.vtag == VT) & (q.population == "donor") & (q.target == "design") & q.interval.isin(["textbook_t|fpc", "textbook_t|fpc|lin"]) & q.lambda_rule.isin(["none", "c_crossfit_design"])]
d0 = S[(S.design == "D0") & S.interval.isin(["textbook_t|fpc|lin"])]
for ivl in ("textbook_t|fpc|lin",):
    qq = q[q.interval == ivl]
    m = d0.merge(qq, left_on=["vtag", "arm", "estimand", "rule", "n_L"], right_on=["vtag", "arm", "estimand", "lambda_rule", "n_L"], how="left", suffixes=("", "_q4a"))
    m["has_q4a"] = m.emp_var_median_q4a.notna()
    mm = m[m.has_q4a].copy()
    mm["d_cov"] = (mm.coverage_median - mm.coverage_median_q4a).abs()
    mm["rel_var"] = (mm.emp_var_median / mm.emp_var_median_q4a - 1).abs()
    mm["rel_ratio"] = (mm.est_var_over_emp_var_median / mm.est_var_over_emp_var_median_q4a - 1).abs()
    mm["ok"] = (mm.d_cov <= 0.005) & (mm.rel_var <= 1e-5) & (mm.rel_ratio <= 1e-5)
    mm[["arm", "estimand", "rule", "n_L", "emp_var_median", "emp_var_median_q4a", "coverage_median", "coverage_median_q4a", "est_var_over_emp_var_median", "est_var_over_emp_var_median_q4a", "d_cov", "rel_var", "rel_ratio", "ok"]].to_csv(f"{HERE}/acceptance1_D0_vs_q4a.csv", index=False)
    nun = m[~m.has_q4a][["arm", "estimand", "rule", "n_L"]]
    acc.append(dict(check="A1b D0 vs q4a_table61 (lin; emp_var 1e-5 rel, coverage 0.005, est/emp 1e-5 rel)", n_rows=len(m), n_unmatched=len(nun),
                    max_abs_diff=float(max(mm.d_cov.max(), mm.rel_var.max(), mm.rel_ratio.max())) if len(mm) else np.nan, passed=bool(mm.ok.all() and len(mm) > 0),
                    note=f"matched {len(mm)}; max |dcov| {mm.d_cov.max():.2e}, max rel var {mm.rel_var.max():.2e}, max rel est/emp {mm.rel_ratio.max():.2e}; unmatched: " + "; ".join(f"{r.arm}/{r.estimand}/{r.rule}/nL{r.n_L}" for r in nun.itertuples())))
# Ratios to D0 classical (rule none, |lin), per gene
cl = "textbook_t|fpc|lin"
g0 = G[(G.design == "D0") & (G.rule == "none") & (G.interval == cl)].set_index(["arm", "estimand", "n_L", "gene"]).emp_var.rename("emp_var_D0_classical")
G2 = G.join(g0, on=["arm", "estimand", "n_L", "gene"])
G2["ratio"] = G2.emp_var / G2.emp_var_D0_classical
gk = ["vtag", "arm", "estimand", "n_L", "design", "balance", "p_a", "rule", "interval"]
Gf = G2.copy(); Gf["p_a"] = Gf.p_a.fillna(-1)
rt = Gf.groupby(gk).ratio.agg(ratio_median="median", ratio_p10=lambda x: x.quantile(.1), ratio_p90=lambda x: x.quantile(.9), n_genes="count").reset_index()
rt["p_a"] = rt.p_a.replace(-1, np.nan)
rt.to_csv(f"{L}/e4_ratios__{VT}.csv", index=False)
# Acceptance 2: perm balance (D2, both p_a), classical rule none, |lin
p = rt[(rt.design == "D2") & (rt.balance == "perm") & (rt.rule == "none") & (rt.interval == cl)].copy()
p["in_band"] = p.ratio_median.between(0.93, 1.07)
for r in p.itertuples():
    acc.append(dict(check=f"A2 perm balance {r.arm}/{r.estimand}/nL{r.n_L}/p_a{r.p_a}", n_rows=r.n_genes, n_unmatched=0, max_abs_diff=r.ratio_median, passed=bool(r.in_band), note="median-over-genes variance ratio to D0 classical"))
pd.DataFrame(acc).to_csv(f"{L}/e4_unit_acceptance__{VT}.csv", index=False)
p.to_csv(f"{HERE}/acceptance2_perm_balance.csv", index=False)
print(pd.DataFrame(acc)[["check", "n_rows", "n_unmatched", "max_abs_diff", "passed"]].to_string())
for r in acc[:3]:
    print(r.get("note", ""))
print(p[["arm", "estimand", "n_L", "p_a", "ratio_median", "in_band"]].to_string())
