# F3 SCALE, predictions for the data check, written before the run (26 Oct 2026)

Design of the run. Tasks CCRCC, INDIANA_KIDNEY, LUNG_XENIUM, encoder uni_v2. Counts are expm1 of the y__ columns, predictions are expm1 of f__ clipped at zero. Pool = spot plus its 6 nearest neighbours (k-NN on spot coordinates). Per slide and gene: V = variance of counts, ybar = mean count, c_nn = mean covariance of counts over k-NN pairs. Ceiling upper bound (Poisson plug-in) U = 1 - ybar/V. Ceiling lower bound (shape-free, valid when the latent covariance is non-negative and at most its unit variance at neighbour distance) L = c_nn/V. Thinning cross-check T = Spearman-Brown of the correlation between two binomial half-thinned copies. Skill interval = Cov(P,y)/sqrt(Var(P) * sigma2) with sigma2 = L*V or U*V. Donor is the unit: slide values are averaged within donor, then mean and standard error across donors.

Predictions.
1. The interval [L,U] is non-empty (L <= U) for at least 95 percent of gene-by-donor cells in each task.
2. The median width U - L is at least 0.15 in each of the three tasks, because real counts are overdispersed relative to Poisson, so the Poisson plug-in overstates the ceiling.
3. T and U agree within 0.02 for the median gene (they coincide in expectation for any counts with conditionally independent thinning, by construction).
4. LUNG_XENIUM, the 20 genes with the largest donor-mean Cov(P,y): donor-level standard error of Cov(P,y) is below half the estimate for at least 15 of the 20 (this is the plan's prediction F3).
5. The skill computed with the lower-bound variance (the upper end of the skill interval) is at most 1 in at least 90 percent of gene-by-donor cells.
