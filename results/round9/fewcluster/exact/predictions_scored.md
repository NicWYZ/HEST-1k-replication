# Track fewcluster, step I2-6, predictions scored

*27 October 2026 (night of the 26th). Script `code/scripts/round9_fewcluster_exact_tuned.py`. Files beside this one: `i26_benchmark.csv`, `i26_synth_exact.csv`, `i26_exact_vs_twopiece_G24n8.csv`, `i26_real_exact.csv`, `i26_real_exact_summary.csv` (Longleaf jobs 1d3843d4, 65242783, 4590a8d6).*

- **E1. Held.** At $G = 10$, $n = 5$, for three kinds of prediction vector and lines of 5 to 9 clusters, the exact single-line algorithm equals the verifier's independent flat-lattice values in 15 of 15 cases, to $2 \times 10^{-16}$. Each extremal population returned is orthogonal to $(1, f)$ to $3 \times 10^{-15}$ and has exactly the stated affine count.
- **E2. Held.** At $G = 24$, $n = 8$ over 10 normal draws of $f$, the exact frontier averages 0.0853 against 0.0898 for the two-piece search on the same draws, 4.9% lower. Over the lognormal and outlier draws the gaps average 11.0% and 10.0%, and over all 30 draws 8.7% (largest 24.3%).
- **E3. Held.** The exact median frontier is 0.0907 on CCRCC and 0.0860 on INDIANA_KIDNEY at $n = 8$, and 0.1484 on LUNG_XENIUM at $n = 6$. The fractions of genes whose residual max-share lies beyond it are 1.00, 1.00 and 0.997. The exact value is below the search upper bound for every gene, by a median of 5.1%, 5.2% and 1.7%.

At every size used here, no arrangement of two or more lines can exceed the threshold (`multi_line_possible` is false throughout), so the single-line computation is the whole frontier. ACS by state ($G = 51$, $n = 8$) was not computed exactly. A defeating line there needs 40 of 51 states, and enumerating every such line is not feasible with this method.
