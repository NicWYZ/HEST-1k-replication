"""Round 5 PPI, the E2 gate report: extra numbers by subset, from the merged tables.

Run on Longleaf from results/round5/ppi/E2_regimeB/diag/. Reads ../e2_prediction_cells.csv,
../e2_decomposition.csv and ../../E1_interval/e1_sim_grid.csv; writes e2_report_numbers_extra.csv
(name,value). Every subset count the report quotes beside a prediction is here.
"""
import numpy as np
import pandas as pd

rows = []
add = lambda n, v: rows.append(dict(name=n, value=v))
c = pd.read_csv("../e2_prediction_cells.csv")
for p in ("E2.1a", "E2.1b"):
    for est in ("theta3", "theta2"):
        s = c[c.prediction.str.startswith(p) & (c.estimand == est)]
        for grp, lab in ((s.vtag.str.startswith("ACS"), "ACS"), (~s.vtag.str.startswith("ACS"), "tissue")):
            ss = s[grp]
            add(f"{p}|{est}|{lab}|n_cells", len(ss)); add(f"{p}|{est}|{lab}|n_in_band", int(ss.in_band.sum()))
            add(f"{p}|{est}|{lab}|min", float(ss.value.min())); add(f"{p}|{est}|{lab}|max", float(ss.value.max()))
        for vt, ss in s.groupby("vtag"):
            add(f"{p}|{est}|{vt}|min", float(ss.value.min())); add(f"{p}|{est}|{vt}|max", float(ss.value.max()))
for p in ("E2.2a|tissue", "E2.2b", "E2.3", "E2.5"):
    s = c[c.prediction.str.startswith(p)]
    for (vt, est), ss in s.groupby(["vtag", "estimand"]):
        add(f"{p}|{vt}|{est}|n_cells", len(ss)); add(f"{p}|{vt}|{est}|n_in_band", int(ss.in_band.sum()))
        add(f"{p}|{vt}|{est}|min", float(ss.value.min())); add(f"{p}|{vt}|{est}|max", float(ss.value.max()))
s = c[c.prediction.str.startswith("E2.5") & (c.estimand == "theta3")]
add("E2.5|theta3|n_cells", len(s)); add("E2.5|theta3|n_in_band", int(s.in_band.sum())); add("E2.5|theta3|max", float(s.value.max()))
d = pd.read_csv("../e2_decomposition.csv")
d = d[(d.target == "design") & (d.population == "donor")]
for (vt, est, arm), ss in d.groupby(["vtag", "estimand", "arm"]):
    add(f"width_ratio|{vt}|{est}|{arm}|min_over_m", float(ss.width_ratio_median.min()))
    add(f"width_ratio|{vt}|{est}|{arm}|max_over_m", float(ss.width_ratio_median.max()))
    if ss.width_over_constant_median.notna().any():
        add(f"over_constant|{vt}|{est}|{arm}|min_over_m", float(ss.width_over_constant_median.min()))
        add(f"over_constant|{vt}|{est}|{arm}|max_over_m", float(ss.width_over_constant_median.max()))
    add(f"sqrt_1m_R2_within|{vt}|{est}|{arm}", float(ss.sqrt_1m_R2_within_median.iloc[0]))
g = pd.read_csv("../../E1_interval/e1_sim_grid.csv")
f = g[(g.rule == "c_crossfit_design") & (g.interval == "textbook_t|fpc|lin") & (g.n_L >= 6)]
for (ln, ls), ss in f.groupby(["law_name", "lambda_star"]):
    add(f"E1|final_coverage|{ln}|lambda_star{ls}|nL>=6|min", float(ss.coverage_mean.min()))
    add(f"E1|final_coverage|{ln}|lambda_star{ls}|nL>=6|median", float(ss.coverage_mean.median()))
    add(f"E1|final_est_over_emp|{ln}|lambda_star{ls}|nL>=6|median", float(ss.est_over_emp_median.median()))
    add(f"E1|lambda_clipped_median|{ln}|lambda_star{ls}|nL>=6|median", float(ss.lambda_clipped_median.median()))
    add(f"E1|lambda_unclipped_median|{ln}|lambda_star{ls}|nL>=6|median", float(ss.lambda_unclipped_median.median()))
i = f.var_ratio_to_classical_mean.idxmax()
r = f.loc[i]
add("E1|max_var_ratio_to_classical|value", float(r.var_ratio_to_classical_mean))
add(f"E1|max_var_ratio_to_classical|cell|G{r.G}|nL{r.n_L}|R2{r.R2}|lam{r.lambda_star}|kap{r.kappa}|{r.law_name}", 1)
pd.DataFrame(rows).to_csv("e2_report_numbers_extra.csv", index=False)
print(len(rows))
