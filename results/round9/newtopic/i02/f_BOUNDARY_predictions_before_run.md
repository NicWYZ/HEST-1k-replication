# F2 BOUNDARY, predictions written before the data run (27 Oct 2026)

Written after the simulation was launched but before its results were read, and before any project data were opened.
Data check planned: raw counts of a few CCRCC and INDIANA_KIDNEY slides, 5 to 10 genes each, boundary estimated on a binomial thinning (eps 0.5) of one gene's counts after Gaussian smoothing (sigma 2 spots) and two-means, then the three tests on the other part. Descriptive, no truth.

P1. Difference-in-means between the estimated domains rejects at 0.05 for at least 90 percent of gene-slide pairs with mean count above 1, and for fewer than 60 percent when the mean count is below 0.2.
P2. The local-linear (HC1) test at h=3 spacings rejects in 15 to 40 percent of gene-slide pairs, well above 0.05 but far below difference-in-means, because real tissue has true domain structure and a jump is expected for many genes (so the excess is not a size estimate).
P3. The robust-bias-corrected (local quadratic) test rejects less often than the local-linear test, in at least 70 percent of slide-gene cells.
P4. Cluster-robust (8x8 block) versions reject less often than their HC1 counterparts in at least 80 percent of cells.
P5. Rejection of the local-linear test falls as h increases from 2 to 5 spacings is NOT expected; I predict the rate rises with h.
Simulation-side prediction, for the record: selection on Y1 produces a systematic (not mean-zero) bias of order h^3 with the sign of the high-minus-low jump, absent at a boundary taken from an independent replicate.
