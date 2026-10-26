# Probe-then-label feasibility, predictions written before the run

Written 26 October 2026 by the claude-science session, before any output of the run was read. Script `code/scripts/round9_probe_feasibility.py`.

Setting. Design target theta_j = mean over all G donors of the donor mean of log1p expression of gene j (uni_v2 predictions). Simple random selection of n_L whole donors (n_L in 4, 6, 8, 12); probe of o random spots (o in 1, 3) in every donor. Estimators with t intervals at 90%: D0 the labelled donors' mean (t, n_L - 1 df, finite-population factor); D1 regression estimator on the donor-mean prediction (n_L - 2 df); D2 regression estimator on the probe factor u_hat_g, the average over genes and probe spots of the probe's log1p expression (n_L - 2 df); D3 regression estimator on u_hat_g and the donor-mean prediction (n_L - 3 df). 400 donor draws per n_L, a fresh probe per draw.

Predictions.
- R1. On CCRCC at n_L = 8 and o = 3, the median over genes of D2's width relative to D0 is below 0.80.
- R2. On CCRCC at n_L = 8 and o = 3, the median over genes of D2's coverage is at least 0.85, and above D0's.
- R3. On LUNG_XENIUM at n_L = 8 and o = 3, D3 is narrower than both D1 and D2 (median over genes).
- R4. D2 at o = 1 loses less than a third of its width gain over D0 compared with o = 3 on CCRCC at n_L = 8.

## Second run, take-all stratum from the probe (written 26 October, before the second run's output was read)

Design. After the probe (o = 3), the k donors with the largest |u_hat_g - median(u_hat)| are always labelled (k = 1, 2) and n_L - k further donors are drawn at random from the rest. Estimators T0 (take-all plus mean of the rest) and T2 (take-all plus regression on u_hat within the rest), 90% t intervals with the rest's degrees of freedom. Script `code/scripts/round9_probe_takeall.py`.
- R5. On CCRCC at n_L = 8 and k = 1, T2's median coverage is at least 0.87 and its width ratio to D0 at most 0.70.
- R6. On INDIANA_KIDNEY and LUNG_XENIUM at n_L = 8, k = 1 changes T0's median coverage by less than 0.03 against D0.
