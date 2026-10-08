"""Round 5 PPI, stage E2: the level share against the constant predictor's regime B width ratio.

Run on Longleaf from results/round5/ppi/E2_regimeB/diag/. For each task, estimand and m, design target,
donor-weighted, rule c_crossfit: the constant predictor's width ratio against the round-4 classical
estimator (e2_decomposition.csv) beside sqrt(1 - L), with L the clipped pooled level share of
docs/round5_ppi_theory.md section 1.2, median over genes (e2_level_share.csv). Also the permuted and the
real predictors' width ratios, for the report's table. Writes e2_level_share_vs_constant.csv.
"""
import numpy as np
import pandas as pd

d = pd.read_csv("../e2_decomposition.csv")
ls = pd.read_csv("../e2_level_share.csv")
d = d[(d.target == "design") & (d.population == "donor")]
w = d.pivot_table(index=["vtag", "estimand", "m"], columns="arm", values="width_ratio_median").reset_index()
s = ls[(ls.arm == "constant") & (ls.population == "donor")][["vtag", "estimand", "m", "share_clipped_median"]]
out = w.merge(s, on=["vtag", "estimand", "m"], how="left")
out["sqrt_1_minus_L"] = np.sqrt(1 - out.share_clipped_median)
out["constant_minus_sqrt_1_minus_L"] = out.constant - out.sqrt_1_minus_L
out.to_csv("e2_level_share_vs_constant.csv", index=False)
print(out[out.m.isin([5, 20, 100])].round(3).to_string())
