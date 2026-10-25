# Cross-gene studentized prediction sets, feasibility run, predictions written before the run

Written 26 October 2026 by the claude-science session, before job outputs were read. Script `code/scripts/round9_stud_feasibility.py`.

Setting. For each task (CCRCC, INDIANA_KIDNEY, LUNG_XENIUM, encoder uni_v2), every donor in turn is the target. Residual r = y - f with f the existing leave-donor-out prediction. In each replicate, every donor (target and reference) gets a block of o random spots as its labelled block; each reference donor contributes one further random spot as its calibration point; the target's other spots are test points. Level alpha = 0.1. Methods: A HCP (score |r|), B the target's own split set on its block, C per-gene studentized score |r| / sigma_hat_gj from the donor's block, D cross-gene studentized score |r| / (sigma_j c_hat_g) with sigma_j pooled symmetrically over all donors' blocks and c_hat_g the donor's scale multiplier estimated from its block across all genes, E oracle (not valid) using the target's true per-gene scale.

Predictions.
- Q1. Methods A to D cover at least 0.89 on average on every task.
- Q2. At o = 2, D's mean finite half-width is at least 10% smaller than A's on CCRCC and on INDIANA_KIDNEY.
- Q3. At o <= 5, C is wider than A on every task (as round 4's K5 was inside GHCP).
- Q4. At o = 3 on CCRCC, the standard deviation over target donors of per-donor coverage is smaller for D than for A.
- Q5. The first principal component of the donor by gene matrix of log within-donor residual SD explains at least 0.50 of its between-donor variance on CCRCC.
