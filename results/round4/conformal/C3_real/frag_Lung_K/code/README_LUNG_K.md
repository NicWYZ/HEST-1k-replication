# Lung K sweep at o = 0 (C3, track Lung K)

Frame id of the writing session: 37664027-917b-4af5-b46c-c441036d6333.

Task: LUNG_XENIUM, three encoders (hoptimus0, uni_v2, resnet50), K in (6, 8, 10) calibration donors,
3 calibration draws per fold, alpha in (0.1, 0.2), o = 0, methods pooled, hcp, one_per.
All code is the shared module round4_conf_c3.py (md5 2d8418677cf8290eec89a14c315b92cd), unedited.
The number of training donors (n_T_donors) is in every row of c3_full and c3_K_sweep.

## Assumptions and guarantees (copied from the module docstring)

pooled. Split conformal on all calibration spots with equal weights, level ceil((n+1)(1-alpha)) of the
n calibration scores. Assumes spot-level exchangeability of calibration and test spots, which
hierarchical data violate. Guarantee: none for a new donor.

hcp. Lee, Barber and Willett. Calibration donor k's spots carry mass 1/((K+1) N_k); the test donor's
mass 1/(K+1) sits at +inf. Assumes hierarchical exchangeability of donors and within-donor
exchangeability. Guarantee: coverage >= 1 - alpha for any K when the assumption holds. The interval
is infinite exactly when 1/(K+1) > alpha, so at alpha 0.1 for K <= 8 and at alpha 0.2 for K <= 3.
Hence at K = 6 and 8 the interval is infinite at alpha 0.1 and finite at alpha 0.2. Real donors are
not exchangeable in features or prediction error.

one_per. Single subsampling of Dunn, Wasserman and Ramdas as round 3's a4b `dwr`: one calibration spot
per donor, ordinary conformal quantile of the K scores, repeated 200 times (crc32 seeds); coverage and
width are averaged over repetitions. Each repetition is a valid single-subsampling interval
(coverage >= 1 - alpha under hierarchical exchangeability, nontrivial iff K >= 1/alpha - 1, so K >= 9
at alpha 0.1 and K >= 4 at alpha 0.2). The average is a summary of valid intervals, not itself a conformal set.
It is not the repeated-subsampling set of the paper's section 4.3, which is not run.

Tie convention: this track's QTOL convention (relative tolerance 1e-12); `finite_code` in c3_full and
c3_K_sweep records the finiteness the released code's upward tie resolution would give.
Design counts: rows per encoder = specs(K) x 3 methods x 2 alphas, summed over K; specs(K) is
folds x 3 calibration draws, minus folds that have <= K eligible pool donors.
