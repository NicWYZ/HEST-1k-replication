# Lung o sweep (fragment frag_Lung_o): assumptions and guarantees, written before the run

Frame id of the producing session: 37664027-917b-4af5-b46c-c441036d6333.

Design. Task LUNG_XENIUM (15 donor folds, one held-out donor per fold), K = 10 calibration donors,
three encoders (hoptimus0, uni_v2, resnet50), absolute score only, alpha in (0.1, 0.2), 3 calibration
draws per fold (module default), o in (5, 10, 25, 50, 100, 200) with 20 label draws, plus o = 0.
The module is round4_conf_c3.py (md5 2d8418677cf8290eec89a14c315b92cd), used unedited. This fragment
adds only run_lung_o.py and merge_lung_o.py.

Source of labelled spots. The labelled spots of fold f are drawn (module label_stream) from the
evaluation spots E of the fold, and E is every spot of the held-out donor's own cores (the samples
listed under that fold's `test` in LUNG_XENIUM.json). run_lung_o.py asserts for every fit that all
evaluation spots belong to those cores and that their donor is the held-out donor. Other donors'
cores on the same capture slide are never in E; the number of such cores is recorded in the design
sidecar of each fit. The capture slide is therefore not used as a source of labelled spots.
An o that leaves fewer than 10 evaluation spots is skipped and listed in the sidecar.

Tie convention. This track's QTOL convention (Q = inf{q : F(q) >= beta}, relative tolerance 1e-12)
is primary. The column finite_code in the full table carries the released code's upward-tie
finiteness (differs at alpha 0.1, K = 10, o = 0 for the GHCP-type quantile).

Methods reported: o = 0 pooled, hcp, one_per; o > 0 ghcp, ghcp_noad, ghcp_r05 (primary, eq. 8 pool
rule), ghcp_r05_noad, ghcp_r05code (secondary, alpha 0.1 only), within, within_plain, recentred.
No candidates, no scaled score, no repeated subsampling.

Module text, verbatim:

```
METHODS (assumption and guarantee, written before anything runs)

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

o > 0 (o labelled spots, uniform without replacement from the test donor's own spots; nested
across o by taking the first o of one seeded permutation per label draw; evaluation on the
donor's other spots)

  ghcp, ghcp_noad, ghcp_r05, ghcp_r05_noad, ghcp_r05code
              Mallick, Tchetgen Tchetgen, Dobriban and Lee, Algorithm 1, as round4_conf_sim.ghcp_q
              implements it (this module is a gene-vectorised copy, checked equal to ghcp_q in
              `selftest`). Selection S = {k : N_k > o}, restricted to the m_eta smallest when
              eta > 0 (eq. 8: ceil((1-eta)K) groups; `r05code` uses the released code's pool, one
              group larger); a donor J0 is drawn uniformly from the pool, the test donor is given
              size N_J0 and the other pool donors calibrate. Within-group adaptation: the first
              m = floor(o/2) residuals of each group recentre it with shrinkage
              lambda = m/(n_glob + m), n_glob = n_T_donors (the donors the base head was trained
              on); `_noad` sets m = 0. Held-out scores |r - c_j| carry 1/((|S_cal|+1) L_j); the
              test donor's o - m scores carry 1/((|S_cal|+1) L_{K+1}) and the rest, (N_J0 - o)/
              ((|S_cal|+1) L_{K+1}), sits at +inf. Assumes A1 group exchangeability, A2 sizes
              exchangeable with and independent of the group laws, A3 within-group exchangeable.
              On real donors A1 and A2 are not established (donor size is tied to the slide
              count, not drawn from the group law). Guarantee: coverage >= 1 - alpha under A1-A3
              (Thm 2.1; Cor 2.6 for eta > 0, whose pool rule is eq. 8, hence `ghcp_r05` is the
              primary variant per memo 12.2 item 2 and `ghcp_r05code` the secondary at alpha 0.1
              only). The calibration spots' order inside a donor, which fixes the adaptation
              block, is a seeded permutation (crc32 of task, fold, donor).
  within      Split conformal inside the test donor alone, the GHCP paper's Std-CP form: the mean
              of the first floor(o/2) labelled residuals recentres, the other o - floor(o/2)
              calibrate |r - c|. Assumes the labelled spots and the evaluation spots are exchangeable
              within the donor (true here by construction: the labelled spots are a uniform random
              subset of the donor's spots, so the guarantee is marginal over that draw). Guarantee:
              coverage >= 1 - alpha; infinite when 1/(o - floor(o/2) + 1) > alpha.
  within_plain
              (memo 12.3 item 1.) Split conformal inside the test donor with all o labelled
              spots calibrating the absolute score and no recentring: q = the ceil((o+1)(1-alpha))-th
              smallest of the o scores |r|, interval yhat +- q. Same assumption and guarantee as
              `within`: coverage >= 1 - alpha marginally over the labelled draw and the evaluation
              spot, from the exchangeability of the o labelled and the evaluation spots. Finite from
              o = 9 at alpha = 0.1 and o = 4 at alpha = 0.2. The coverage statement is for a
              random evaluation spot; the fold coverage reported here is the average over the
              donor's remaining spots for one labelled draw, so single-draw coverages scatter around
              the guarantee and only the mean over the 20 draws should be compared to it.
  recentred   The cheapest practitioner rule (plan C3, memo 12.3 item 4). The pooled cross-donor
              quantile q of the calibration scores |r| (the K-donor design's calibration set,
              round 3's `donor` design, uncentred) with the interval shifted by c, the mean of the
              labelled spots' residuals, per gene: yhat + c +- q. Assumes the calibration donors'
              scores are a fair proxy for the test donor's centred scores, which they are not:
              q still contains the between-donor bias that c removes from the test donor only, so
              the interval is expected to be conservative where the failure is bias and not where it
              is scale. Guarantee: none.
```
