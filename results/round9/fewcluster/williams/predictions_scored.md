# Predictions scored, step I3-4

Scored 27 October 2026 against `i34_williams_acs.csv`, `i34_williams_hest.csv` and the two summaries (HEST on Longleaf, job 1afd6557). 20,000 draws per population and n; HEST populations are the 50 genes of each kidney task and 42 of LUNG_XENIUM's 343 (those with crc32(gene) divisible by 7).

| ID | Prediction | Result | Score |
|---|---|---|---|
| W1 | Williams' and the fold-wise forms unbiased to Monte Carlo error in at least 0.97 of cells | 0.999 of 3264 cells with the bias below 3 Monte Carlo SE | held |
| W2 | round 5's bias below 0.1 SD in at least 0.9 of cells at n <= 12, largest at the largest n/G | 0.968 of 715 cells (1.00 on ACS, CCRCC and INDIANA_KIDNEY, 0.89 on LUNG_XENIUM, where n/G reaches 0.8); its bias is detectable (below 3 Monte Carlo SE in only 0.07 to 0.46 of LUNG_XENIUM cells at n >= 6) | held |
| W3 | the cross-fitting term adds at least 0.01 to coverage at n >= 8 | at most 0.003 | refuted |
| W4 | no form reaches 0.90 on CCRCC at the median gene for n <= 12 | largest 0.878 (round 5's form at n = 6) | held |
| W5 | Williams' and fold-wise mean squared errors within 10% | equal to the third decimal at the median gene on every task | held |
| W6 | round 5's interval at least 20% wider than W_within on each kidney task at n >= 6, and covers more | median width ratio 1.085 to 1.099 (CCRCC) and 1.119 to 1.140 (INDIANA_KIDNEY); 1.51 to 1.53 on LUNG_XENIUM and 9.3 to 20.3 on ACS; covers 0.025 to 0.046 more (median over populations) | refuted (wider, but by less than 20% on the kidney tasks) |
