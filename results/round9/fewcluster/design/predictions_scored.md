# Track fewcluster, step I2-3, predictions scored

*26 October 2026, second session. Values from `i23_takeall_summary.csv` and `i23_takeall_kappa.csv` beside this file (Longleaf job 528136d8, script `code/scripts/round9_fewcluster_takeall_kappa.py`, CCRCC, uni_v2, 50 genes). The frontier for 7 random donors of the remaining 23 is 0.157.*

- **P10. Held.** With INT5 in a take-all stratum, the median residual max-share among the other 23 donors is 0.293 (it was 0.533 with all 24), above the frontier, and 0.06 of genes come inside it.
- **P11. Held.** Removing each gene's own largest-residual donor instead (an oracle) gives a median of 0.286, with 0.08 of genes inside the frontier.

One take-all donor does not bring CCRCC inside the frontier at 8 labelled donors. After the most atypical donor is removed, another donor still carries about 0.29 of the residual sum of squares for the median gene.
