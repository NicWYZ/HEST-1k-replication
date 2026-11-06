# Predictions before the run, step I3-1 and I3-2 (Theorem 3, stratified designs)

Written 27 October 2026 by the fewcluster session, before any computation of the stratified frontier. alpha = 0.10 throughout. The frontier kappa*_st is in units of the largest share of one cluster (or unit) in the design variance of the stratified estimator.

- **R1 (sanity).** With one stratum the stratified frontier equals Theorem 1's kappa2(k* - 1) in every cell of the interval 1 grid.
- **R2 (two equal strata).** G = 24 split into two strata of 12, 4 sampled in each: the frontier is within 10% of the unstratified 0.158 at 8 of 24 (session's hand estimate 0.156, set by one stratum at k = 2 and the other at k = 3).
- **R3 (regime B, synthetic).** 24 clusters of 2000 units, independent standard normal units, m units sampled in each cluster, target the average of cluster means. The smallest m at which the median population lies strictly inside the frontier is 3, below the iid threshold log2(2/alpha) = 4.32, because no one cluster can carry the whole design variance.
- **R4 (regime B, ACS by state).** Person-level log income residuals by state, 51 states: the smallest m per state at which the population lies inside the frontier is at most 10. Regime A at the same task needs more clusters than the 8 of 51 used (the cluster-level residual max-share 0.147 lies beyond the 0.071 frontier).
- **R5 (regime B, HEST, when Longleaf is reachable).** For at least 0.9 of genes on each kidney task, m of at most 10 spots per donor puts the population inside the frontier.

## Addendum, 27 October 2026, after R1 to R4 were run and before any HEST computation

R1 to R4 are scored in `predictions_scored.md`. R4 as written (pooled class) was refuted, and the session then defined the box class (no residual beyond Lambda0 within-stratum SDs, no stratum above v0 of the design variance). On ACS that class put regime B inside at m = 5 with predictions. That finding is post hoc. The HEST predictions under the box class, written now, are these.

- **R5b (regime B, HEST, box class).** At each population's own (Lambda0, v0), with lambda = 1, the median over genes of the smallest m per donor that is certified inside lies between 10 and 40 spots on CCRCC and INDIANA_KIDNEY. Fewer than 0.1 of genes need more than 100.
- **R6 (regime A, HEST).** At lambda = 1, regime A needs more than the 8 labelled donors used, for at least 0.9 of genes on each kidney task (Theorem 1 on donor means).
