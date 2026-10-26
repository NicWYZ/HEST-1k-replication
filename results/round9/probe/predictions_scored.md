# Probe-then-label feasibility, predictions scored

Scored 26 October 2026 from `probe_medians.csv` (Longleaf job 74cc77e6, uni_v2, 400 donor draws per cell, medians over genes, nominal 0.90).

- R1 held. On CCRCC at n_L = 8 and o = 3, D2's width relative to D0 is 0.630.
- R2 refuted. D2's median coverage there is 0.811, below 0.85 and below D0's 0.851.
- R3 held. On LUNG_XENIUM at n_L = 8 and o = 3, D3's width ratio is 0.839, against 0.910 for D1 and 0.966 for D2.
- R4 held. On CCRCC at n_L = 8, D2's width gain over D0 is 0.286 at o = 1 and 0.370 at o = 3, a loss of 0.228 of the gain.

Reading. A probe of three spots per donor gives a donor-level auxiliary that narrows the CCRCC interval by a third, and on lung it lets the predictions help, but every regression interval under-covers at these numbers of labelled donors (0.739 to 0.892 over all cells), and so does the plain mean on the Visium tasks. Narrower intervals that cover less are not a result; the binding constraint for donor-level inference remains coverage with few labelled clusters.
