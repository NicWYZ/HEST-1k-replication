# Round 9, track fewcluster, Williams' estimator against round 5's (step I3-4)

*27 October 2026. Written by the fewcluster session. This is run 6.4.1 of the round 8 positioning note (`docs/round08/i01/positioning/round08_positioning_note.md`, section 3.2), the third piece of work the paper outline lists before drafting. Predictions were written before the run and scored after it (`results/round9/fewcluster/williams/predictions_before_run.md`, `predictions_scored.md`). Script `code/scripts/round9_fewcluster_williams.py`; outputs in `results/round9/fewcluster/williams/`. Recommendations are `[proposed]`.*

## 1. What was compared

Whole clusters are labelled. For each population of $G$ cluster values $z_g$ with mean predictions $f_g$, and each even $n$ from 4 to 16, 20,000 draws each take a simple random sample of $n$ clusters and a random split into halves $A$ and $B$. The populations are the 51 ACS state means of log income with the cross-fitted GBM predictions, the 50 genes of CCRCC and of INDIANA_KIDNEY, and 42 of LUNG_XENIUM's 343 genes (donor means, uni_v2). The forms are these, with the notation of the round 8 note.

1. Round 5's estimator, $\hat\theta_{\text{R5}} = T_1 - T_2$, with round 5's coefficient (each half's slope applied to the other half, clipped to $[0, 1]$, zero below six clusters) and round 5's variance with the cross-fitting term, $t_{n-1}$.
2. Williams' estimator, $\hat\theta_{\text{W}} = T_1 - (1 - n/G)\,T_2$, with the plain variance, with round 5's variance, and with the residual variance pooled within halves ($t_{n-2}$).
3. The fold-wise form, which splits the unlabelled clusters between the folds as well, with its fold-wise variance ($t_{n-2}$).
4. A global least-squares coefficient, unclipped ($t_{n-2}$), and the fixed coefficient $\lambda = 1$ ($t_{n-1}$).

## 2. Results

At $n = 8$ and $\alpha = 0.10$, medians over each task's populations (`i34_williams_summary_hest.csv`, `i34_williams_summary_acs.csv`).

| Task | Round 5, coverage and width | Williams within halves | Fold-wise | Fixed $\lambda = 1$ | Global slope |
|---|---|---|---|---|---|
| ACS by state | 0.942, 1.941 | 0.891, 0.116 | 0.890, 0.116 | 0.891, 0.106 | 0.849, 0.098 |
| CCRCC | 0.873, 0.504 | 0.837, 0.464 | 0.836, 0.464 | 0.855, 0.452 | 0.804, 0.461 |
| INDIANA_KIDNEY | 0.905, 0.225 | 0.863, 0.186 | 0.861, 0.186 | 0.871, 0.186 | 0.837, 0.180 |
| LUNG_XENIUM | 0.939, 0.646 | 0.891, 0.301 | 0.887, 0.302 | 0.892, 0.280 | 0.863, 0.283 |

1. **Williams' and the fold-wise estimators are exactly unbiased, and equally good.** Their bias was below three Monte Carlo standard errors in 0.999 of 3264 cells, and their root mean squared errors agree to the third decimal at the median population on every task.
2. **Round 5's bias is small but real.** It is below 0.1 of its standard deviation in 0.968 of the 715 cells with $n \le 12$, and it is detectable where $n/G$ is large. On LUNG_XENIUM, where $n/G$ reaches 0.8, it exceeds three Monte Carlo standard errors in most cells at $n \ge 6$, as the round 8 formula says it should.
3. **Round 5's variance depends on the level of the predictions.** It pools the residuals $z_g - \lambda_{(g)} f_g$ across the two halves, which use different coefficients. A difference $\lambda_B - \lambda_A$ therefore moves one half's residuals by $(\lambda_B - \lambda_A)\bar f$, and the variance grows with the level of $f$. That variance is not invariant under a shift of the predictions, which an equivariant procedure must be. Round 4's `estimate_textbook` and `var_textbook` (`code/scripts/round4_ppi_estimator.py`), which round 5's code calls, compute it this way. At $n \ge 6$ the median width ratio to Williams' form with the within-half variance is 1.09 on CCRCC, 1.12 to 1.14 on INDIANA_KIDNEY and 1.51 to 1.53 on LUNG_XENIUM. On ACS, where $f$ sits near 10.5 on the log scale, it is 9.3 to 20.3. Round 5's interval covers 0.025 to 0.046 more at the median population. Its coverage, close to nominal on tissue, comes partly from this inflation.
4. **The cross-fitting term does nothing measurable.** Adding it to Williams' estimator changes coverage by at most 0.003 (W3 refuted). The finite-population factor that round 5's term was meant to supply is Williams' $(1 - n/G)$ on $T_2$.
5. **With a variance that does not depend on the level of $f$, every exactly unbiased form under-covers on the kidney tasks.** At $n = 8$ the median coverage is 0.84 on CCRCC and 0.86 on INDIANA_KIDNEY. This is what Theorems 1 and 2 predict, since the median gene of both tasks lies beyond both frontiers at this size.
6. **The fixed coefficient is as good as any tuned form here.** Its root mean squared error is the smallest, or within 0.001 of the smallest, on every task at $n \le 10$. Its coverage is within 0.03 of the exactly unbiased tuned forms, and higher on the kidney tasks at $n \ge 6$. The global slope, fitted on the whole sample, is biased by 0.07 to 0.26 of its standard deviation (90th percentile over populations) and covers 0.02 to 0.06 below Williams' form.

## 3. What this changes

`[proposed]` The paper should use Williams' estimator with $k = 2$ and the residual variance pooled within halves, or the fold-wise form, whichever it finds simpler to state, and cite Williams (1961) and the fold-wise papers for it. It should not display round 5's variance. The fixed coefficient $\lambda = 1$ is the natural reference interval, since the frontiers of Theorems 1 and 3 are stated for it and it does about as well at these sizes. Below six labelled clusters round 5's rule sets the coefficient to zero, where all these forms reduce to the classical estimator.

Two things are left open. Whether the intervals reported in rounds 5 to 7 carry the inflation of item 3 depends on the level of $f$ in each task's coding, and this step did not check it. The within-half variance is a plug-in. A variance estimator for Williams' form that is exact under sampling without replacement and stable with two groups, which the round 8 note named, is still not written. Neither is needed for Theorems 1 to 3, which are about the fixed coefficient.

## 4. Literature

Nothing here is claimed as new. The estimators are Williams (1961), Sanguiao Sande and Zhang (2020) and the fold-wise papers of 2025 and 2026 (Lu et al.; An, Dagdoug, Haziza and Tillé; Kwon, Yang and Kim), as the round 8 note records. That a pooled residual variance with different coefficients in the two halves is not shift-equivariant is a defect of round 5's code, not a result, and is recorded as a correction.
