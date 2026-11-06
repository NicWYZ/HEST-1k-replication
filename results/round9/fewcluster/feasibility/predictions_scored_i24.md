# Track fewcluster, predictions P1 to P3 and P9 scored (step I2-4)

*26 October 2026. Values from `results/round9/fewcluster/hest/i24_task_summary.csv` and `i24_gene_kappa.csv` (Longleaf job 9f5ad9c3, script `code/scripts/round9_fewcluster_hest_kappa.py`, input the claude-science C0 donor summaries). Predictions are in `predictions_before_run.md` (P1 to P3 in the first section, P9 in addendum 2). uni_v2 predictions. LUNG_XENIUM has 343 genes in the summaries, not the 50 the predictions assumed, and all 343 are used.*

- **P1. Held.** On CCRCC the median residual max-share over 50 genes is 0.533, and INT5 carries the largest share for 0.80 of genes.
- **P2. Partly held.** On INDIANA_KIDNEY the median is 0.336, inside the predicted 0.15 to 0.35. On LUNG_XENIUM it is 0.312, above the predicted 0.25.
- **P3. Held.** Against $\kappa_2(k^\ast)$, the definition the prediction was written with, the median gene is beyond the boundary on every task. The fractions of genes beyond are 1.00 (CCRCC), 0.96 (INDIANA_KIDNEY) and 0.977 (LUNG_XENIUM). Against the corrected frontier $\kappa_2(k^\ast - 1)$ they are 1.00, 0.90 and 0.708. Against the tuned-coefficient frontier (upper bounds from a two-piece search on each gene's own prediction vector) they are 1.00, 1.00 and 0.997.
- **P9. Held.** For ACS by state with the GBM predictions the residual max-share is 0.147, between the corrected frontier at 8 of 51 (0.071) and the raw 0.209. The largest residual share moves from DC (raw) to state code 2, Alaska (2.69 residual standard deviations), so the predictions account for DC.
