# Round 9, track fewcluster, the closing report

*27 October 2026. Written by the fewcluster session at Nicolas's request ("record the track's state in the repo and close this track now"). Frozen once committed. It closes track `fewcluster` (option B, valid inference with few labelled clusters) of round 9. The round itself closes through `/project-state-keeping` once both tracks have closed and Nicolas has decided how the branches are merged (masterplan, D4).*

## 1. The decision

Nicolas asked for the track to be closed on 27 October, after interval 3. The decisions the track handed him (section 4) were not answered before the close and are carried forward unanswered. The track ran three working intervals, `i01` to `i03`, on 26 and 27 October. Its record is the documents listed in `docs/round09/README.md` under `i01/fewcluster/` to `i03/fewcluster/` and `tracks/fewcluster/`, with results in `results/round9/fewcluster/` and scripts named `code/scripts/round9_fewcluster_*`.

## 2. What the track established

All statements are for intervals that move with the data (location and scale equivariant), at $\alpha = 0.10$, with a class bounded by residual concentration, the largest share of one cluster in the residual sum of squares. Each theorem was proved by the session and again by a fresh agent from the statements alone, with exact enumeration at small sizes.

1. **Theorem 1, the fixed-coefficient frontier** (`i01/fewcluster/round09_fewcluster_frontier.md`). A valid finite interval exists below $\kappa_2(k^\ast - 1)$, and above it every valid interval is unbounded with positive probability under every population. Two-point populations are extremal, and simple random sampling is minimax among fixed-size designs. The frontier is 0.158 at 8 of 24 and 0.071 at 8 of 51. A guarantee against residuals of 3 or 4 SD needs 13 or 17 of 24 clusters labelled.
2. **Theorem 2, the tuned-coefficient frontier, and an exact algorithm for it** (`i02/fewcluster/round09_fewcluster_tuned.md`, `round09_fewcluster_position.md`). The defeating samples are those on which residuals are affine in the predictions. The frontier is about half the fixed one (0.085 at 8 of 24 with normal predictions). The algorithm matched an independent computation in 15 of 15 cases.
3. **Theorem 3, the stratified frontier** (`i03/fewcluster/round09_fewcluster_stratified.md`). It is a product over strata, a knapsack for a pooled cap and a count of $\lceil 1/v_0 \rceil$ simultaneously degenerate strata for the box class. It covers take-all clusters and regime B, and pooling escapes the per-stratum iid threshold.
4. **Where the real tasks sit.** The median residual max-share is 0.533 (CCRCC), 0.336 (INDIANA_KIDNEY) and 0.312 (LUNG_XENIUM), and practically every gene lies beyond both frontiers at the sizes used. Under the box class, with predictions, regime B needs 5 persons per state on ACS and a median of 6 to 8 spots per donor on HEST. Regime A needs 11 of 51 states and 8 to 17 donors. Regime B's advantage rests on no cluster carrying a large share of the design variance. Without that bound it needs 22 to 143 units per cluster.
5. **Critical values below the frontier, claim K, partly** (`i03/fewcluster/round09_fewcluster_critical_value.md`, `round09_fewcluster_nov12.md`). Certified values exist only at up to half the frontier (3.78 at 8 of 24, at 0.4 of it). Lower bounds from explicit populations are 1.9 to 3.0 up to three quarters of the frontier and 4.4 to 5.0 near it, against the normal 1.645. No certified value exists for the box class at the real settings.
6. **The estimator** (`i03/fewcluster/round09_fewcluster_williams.md`). Williams' (1961) estimator and the fold-wise form are exactly unbiased and equally good. Round 5's variance pools residuals fitted with different coefficients and grows with the level of the predictions, widening its interval by 1.09 to 1.53 times on HEST and 9 to 20 times on ACS.
7. **A side result** (`i02/fewcluster/round09_fewcluster_sources_and_median.md`). The two-block construction proves Paul and Kuchibhotla's conjecture (arXiv:2403.06357) that no shift-invariant, locally bounded interval for the median exists below $\log_2(2/\alpha)$ observations.
8. **The paper** (`i02/fewcluster/round09_fewcluster_paper_outline.md`, `tracks/fewcluster/paper_draft_v0.md`). An outline, and a first draft in it without prediction sets.

**Novelty, on the evidence.** Thirteen checkers searched, NOV1 to NOV12 with NOV10b. They logged over 500 queries, screened about 2000 forward citations, and read the closest papers in full where an open version existed. Not found in print are Theorem 1 in its finite-population graded form with its possibility half and design minimaxity, Theorem 2 and its algorithm, Theorem 3 and the regime comparison, the median result, and the finite-population application of the critical-value certificate. Known, and cited rather than claimed, are the proof technique (Bahadur and Savage; Gleser and Hwang; Dufour), the unrestricted impossibility, the iid limit (Lanke 1974; Székely 2006), pooling across groups under symmetry or Gaussianity (Ibragimov and Müller; Canay, Romano and Shaikh; Hagemann), the certificate's moment-duality method (Pinelis), and the band lemma (Jonsson 2011). Every "not found" verdict is provisional, since several classical sources were read only from abstracts.

## 3. Corrections and withdrawn readings

1. The fixed frontier is $\kappa_2(k^\ast - 1)$, not $\kappa_2(k^\ast)$ (interval 1 verifier).
2. A spike at a high-leverage cluster is cheaper in max-share down to a floor of about 0.21 to 0.25 at 24 clusters, not invisible (`i02/fewcluster/round09_fewcluster_tuned.md`, section 4).
3. Claim B (a bounded-residual interval) is in print in the PPI paper's appendices, claim D (what the design buys) mostly so, and Lemma 0 is folklore (`i01/fewcluster/round09_fewcluster_decision.md`).
4. A single pooled cap on every unit's share is the wrong class when strata differ in size, which refuted R4 and led to the box class. That class was defined after R4 failed, and HEST tested it.
5. Of the 13 predictions written in interval 3, 7 held, 5 were refuted (R3, R4, R5b, W3, W6) and 1 was not tested (R5, superseded by R5b). The session's chat report of 27 October said six were refuted, which was wrong.
6. Pötscher and Preinerstorfer's Theorem 5.1 gives sufficient conditions, not an equivalence. A loose band certificate exists at 12 of 24 near the frontier ($c = 196.1$). Further slips in checker files are listed in `i03/fewcluster/round09_fewcluster_i03_corrections.md`.
7. Round 5's variance defect may affect the tuned intervals reported in rounds 5 to 7. That depends on how each task coded the level of the predictions, and it is not checked.

## 4. Carried forward

**Decisions for Nicolas,** none answered at the close.

| # | Decision | Default |
|---|---|---|
| D1 | Whether the three frontiers become the paper's theory section, with regime A against regime B as its main design result | open; likely with David and Dr. Zhu |
| D2 / R8-1 | Whether prediction sets stay in this paper | the draft defers them to separate work |
| V | Whether bounding each cluster's share of the design variance is defensible for the applications | regime B's numbers are stated under it, beside the unbounded column |
| D3 | Writing to Paul and Kuchibhotla about the median result | no contact |
| S | Obtaining nine paywalled sources (list with library links in `i03/fewcluster/round09_fewcluster_nov12.md`) | verdicts stay provisional |
| X | Deleting about 28 paper full texts that checkers saved to the project's private artifact store against instructions in interval 3, beside the files NOV8 saved in interval 2. None is in this repository | kept |

**Open technical items,** none needed for D1.

1. A sharp, computable critical value in the classes real tasks satisfy.
2. A tuned-coefficient version of Theorem 3.
3. The exact tuned frontier for ACS (51 states, where enumeration is infeasible).
4. Whether rounds 5 to 7's tuned intervals carry the variance inflation.
5. A variance estimator for Williams' form that is exact under sampling without replacement.
6. Draft v1, folding in the corrections of section 3 and the credits of NOV12.

## 5. Read first next round

The paper draft (`docs/round09/tracks/fewcluster/paper_draft_v0.md`), then Theorem 3 (`i03/fewcluster/round09_fewcluster_stratified.md`), then the interval 2 position note (`i02/fewcluster/round09_fewcluster_position.md`). Then read the critical-value note with NOV12's verdicts and the interval 3 corrections, before any claim from them is written into a draft.
