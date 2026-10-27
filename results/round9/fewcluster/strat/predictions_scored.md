# Predictions scored, steps I3-1 and I3-2

Scored 27 October 2026 against `i31_checks.txt`, `i32_acs_regimes.csv` and `i32_acs_box.csv`.

| ID | Prediction | Result | Score |
|---|---|---|---|
| R1 | one stratum reproduces Theorem 1 | 22 of 22 grid cells inside the computed bracket | held |
| R2 | two strata of 12 with 4 each within 10% of 0.158 | 0.1562 against 0.1583 | held |
| R3 | regime B synthetic needs m = 3 | the median population is first inside at m = 4. Over 200 populations, 0.26 are inside at m = 3, 0.875 at m = 4 and all at m = 5 (the first run's 21 populations had put all of them inside at m = 4; the verifier's 20 draws reached 6.7e-4, beyond the m = 4 frontier of 4.73e-4). m = 4 is still below log2(2/alpha) = 4.32 | refuted |
| R4 | ACS regime B inside at m <= 10, pooled class | beyond the pooled frontier at every m up to 30 (kappa_st 3.1e-4 against 6.4e-5 at m = 30); regime A needs 11 of 51 states at lambda = 1 | refuted as written |

R4's failure has one cause. The pooled class caps every unit's share by one number, and the adversary then puts all the variance in California, whose two-point populations have shares near 1/N. Under the box class, defined after R4 failed, ACS regime B is inside at m = 5 with predictions and at m = 2 without (`i32_acs_box.csv`). That result is post hoc and is tested on HEST by R5b.

## HEST, scored 27 October 2026 against `i32_hest_box_summary.csv` and `i32_hest_box_genes.csv` (Longleaf job 161e6b2b)

| ID | Prediction | Result | Score |
|---|---|---|---|
| R5b | median m between 10 and 40 on the kidney tasks at lambda = 1, fewer than 0.1 of genes above 100 | median 6 (CCRCC) and 8 (INDIANA_KIDNEY), 90th percentiles 10 and 12; no gene above 100 on any task (LUNG_XENIUM median 8, 90th percentile 25) | refuted on the low side (the second half held) |
| R6 | regime A needs more than 8 donors for at least 0.9 of genes on each kidney task | 1.00 on CCRCC and 0.98 on INDIANA_KIDNEY (median 17 and 13 donors) | held |

The populations' own v0 is about 0.08 on the kidney tasks at m = 10 (median over genes), so about 13 donors must be degenerate at once, and the median largest within-donor residual is 5.3 (CCRCC) and 6.3 (INDIANA_KIDNEY) within-donor SDs.
