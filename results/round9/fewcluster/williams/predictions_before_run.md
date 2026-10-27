# Predictions before the run, step I3-4 (Williams' estimator against round 5's)

Written 27 October 2026 by the fewcluster session, before the comparison was run. Whole clusters labelled (regime A), even n from 4 to 16, alpha = 0.10, 20,000 draws of sample and split per population and n. Populations are the ACS state means (51) and the HEST donor means per gene (CCRCC, INDIANA_KIDNEY, LUNG_XENIUM, uni_v2). Forms are round 5's estimator R5 = T1 - T2 with round 5's coefficient rule (half-sample slope, clipped to [0, 1], zero below six clusters) and round 5's variance with the cross-fitting term, Williams' W = T1 - (1 - n/G) T2 with the plain finite-population variance and with round 5's variance, the fold-wise form, a global least-squares coefficient with t on n - 2 degrees of freedom, and the fixed coefficient lambda = 1.

- **W1 (sanity).** Williams' and the fold-wise estimators are unbiased to Monte Carlo error on every population (|bias| below 3 Monte Carlo SE in at least 0.97 of population-n cells).
- **W2.** Round 5's bias is small against its SD, |bias|/SD below 0.1 in at least 0.9 of cells at n <= 12, and largest at the largest n/G.
- **W3.** Williams' estimator with the plain variance covers at least 0.01 below Williams' with round 5's variance at n >= 8 on the median population, because the cross-fitted coefficient adds variance the plain form misses.
- **W4.** On CCRCC no form reaches 0.90 coverage at the median gene for n <= 12, in line with the frontier (the median gene is beyond it).
- **W5.** Williams' and the fold-wise forms have mean squared errors within 10% of each other at the median population.

## Addendum, 27 October 2026, after the ACS run and before the HEST run

On ACS, round 5's variance turned out to depend on the level of the predictions. It pools residuals z_g - lambda_(g) f_g across the two halves, which use different coefficients, so a difference in the half coefficients moves one half's residuals by (lambda_B - lambda_A) times the level of f. Round 4's `estimate_textbook` and `var_textbook` (`code/scripts/round4_ppi_estimator.py`), which round 5 calls, compute it that way. On ACS its mean width at n = 6 was 3.03 against 0.149 for the fold-wise form. The session added W_within, Williams' estimator with the residual variance pooled within halves, after seeing this.

- **W6.** On HEST at n >= 6, round 5's interval is at least 20% wider than W_within's at the median gene on each kidney task, and covers more.
