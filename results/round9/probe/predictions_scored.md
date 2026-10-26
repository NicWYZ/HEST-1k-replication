# Probe-then-label feasibility, predictions scored

Scored 26 October 2026 from `probe_medians.csv` (Longleaf job 74cc77e6, uni_v2, 400 donor draws per cell, medians over genes, nominal 0.90).

- R1 held. On CCRCC at n_L = 8 and o = 3, D2's width relative to D0 is 0.630.
- R2 refuted. D2's median coverage there is 0.811, below 0.85 and below D0's 0.851.
- R3 held. On LUNG_XENIUM at n_L = 8 and o = 3, D3's width ratio is 0.839, against 0.910 for D1 and 0.966 for D2.
- R4 held. On CCRCC at n_L = 8, D2's width gain over D0 is 0.286 at o = 1 and 0.370 at o = 3, a loss of 0.228 of the gain.

Reading. A probe of three spots per donor gives a donor-level auxiliary that narrows the CCRCC interval by a third, and on lung it lets the predictions help, but every regression interval under-covers at these numbers of labelled donors (0.739 to 0.892 over all cells), and so does the plain mean on the Visium tasks. Narrower intervals that cover less are not a result; the binding constraint for donor-level inference remains coverage with few labelled clusters.


## Second run, take-all stratum, predictions scored

Scored 26 October 2026 from `takeall_medians.csv` (Longleaf job 8f4d6844, 400 draws per cell, medians over genes, nominal 0.90).

- R5 partly held. On CCRCC at n_L = 8 and k = 1, T2's width ratio to D0 is 0.666 (held) but its median coverage is 0.848 (below 0.87). The simpler T0 covers 0.885 against D0's 0.825, at width ratio 0.779, and its 10th-percentile gene covers 0.827 against 0.675.
- R6 held. At n_L = 8 and k = 1, T0's median coverage minus D0's is -0.010 on INDIANA_KIDNEY and -0.010 on LUNG_XENIUM.

Reading. Labelling the one probe-atypical donor with certainty repairs coverage on CCRCC and narrows the interval at the same time, and is neutral where no such donor exists. This is two-phase sampling for stratification with a take-all stratum, a classical design; what the data add is that in spatial transcriptomics the atypical donor is a technical outlier that histology cannot reveal and that three labelled spots can.
