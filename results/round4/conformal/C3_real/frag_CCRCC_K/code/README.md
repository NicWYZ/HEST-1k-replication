# CCRCC K sweep (o = 0): assumptions and guarantees

Written before the jobs run. Text below is copied from the docstring of round4_conf_c3.py
(md5 2d8418677cf8290eec89a14c315b92cd), which this unit uses unchanged.

Unit design. CCRCC, donor sets `CCRCC:24` and `CCRCC:23_merged`, encoders hoptimus0, uni_v2, resnet50,
K in 4,6,...,20, three calibration draws per fold, alphas 0.1 and 0.2, methods pooled, hcp, one_per
(o = 0 only). The training-donor count `n_T_donors` falls as K rises and is in every row.
Reference check: at K = 10, alpha 0.1 the rows are compared with results/round3/A4_scores/a4b_hcp_K10__<enc>.csv
(one_per against a4b `dwr`). Widths may differ at about 5e-10 on AMD nodes (core unit's anchor note);
the CPU vendor of every job is recorded in node_info.txt.

```
QUANTILE CONVENTION (memo 12.2 item 1). Q_beta(nu) = inf{t : nu((-inf, t]) >= beta} with the
relative tolerance 1e-12 of round4_conf_sim (QTOL), the same tolerance round 3's A3 uses. The
released GHCP code resolves an exact tie upward. Every row carries `finite_code`, the finiteness
the upward resolution would give (an exact tie at the last finite atom returns +inf), so the two
conventions are read side by side wherever they differ (alpha = 0.1, K = 10, o = 0 for GHCP).

DESIGN K. `K` in the output is the number of calibration donors of the design (the K axis of the
plan). `K_eff` in the full table is the number of exchangeable units the method's quantile rests on
(n_C for pooled, K for hcp and one_per, the pool size for ghcp, and so on). The training-donor
count (`n_T_donors`) falls as K rises and is recorded in every row.

o = 0 (no labelled spot in the test donor)

  pooled      Split conformal on all calibration spots with equal weights, quantile level
              ceil((n+1)(1-alpha)) of the n calibration scores. Assumes spot-level exchangeability
              of calibration and test spots, which hierarchical data violate. Guarantee: none for
              a new donor; round 3's A1 interval.
  hcp         Lee, Barber and Willett. Calibration donor k's spots carry 1/((K+1) N_k), the test
              donor's mass 1/(K+1) sits at +inf (A3's W3). Assumes hierarchical exchangeability of
              donors, within donor exchangeability. Guarantee: coverage >= 1 - alpha for any K when
              the assumption holds; infinite exactly when 1/(K+1) > alpha (K <= 8 at alpha 0.1).
              Real donors are not exchangeable in features or in prediction error; the guarantee
              is conditional on that assumption, which A4b tested on CCRCC.
  one_per     Dunn, Wasserman and Ramdas single subsampling as round 3's a4b `dwr` applies it: one
              calibration spot drawn per donor, ordinary conformal quantile of the K scores,
              repeated `dwr_reps` times (200, crc32 seeds) with the coverage and width averaged over
              repetitions. Each repetition is a valid single-subsampling interval (coverage >=
              1 - alpha under hierarchical exchangeability, nontrivial iff K >= 1/alpha - 1);
              the average is a summary of valid intervals, not itself a conformal set. It is NOT
              the repeated-subsampling set of the paper's section 4.3, which C3 does not run
              (memo 12.2 item 5). Output name `one_per`; a4b called it `dwr`.
```

No candidates, no scaled score, no repeated subsampling are used.
