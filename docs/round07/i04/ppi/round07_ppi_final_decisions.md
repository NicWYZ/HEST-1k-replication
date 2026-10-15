# Round 7, the inference track, decisions at the closing gate

15 October 2026. Written by the oversight chat after reviewing the final report (`docs/round07/i03/ppi/round07_ppi_final_report.md`, pull request #32, tag `round7-ppi-final`). The track ends at this gate, so this memo opens no interval. It lives on `main` only. Nothing further is committed or pushed on branch `round7-ppi`.

**What was read and checked.** The whole report, and the S5 tables behind its closing page, `results/round7/ppi/S5_numbers/run1/s5_matched.csv` and `s5_bh_vs_tuned.csv`. The rows the closing page quotes were read back from those files, among them these, at $n_L = 8$, $p_a = 0.01$, coverage over all draws and width against D0 classical.
- Tissue, 18 matched cells. `rej_t` covers 0.861 at width 0.888. The S3 cube design covers 0.885 at 0.891, the S4b cube design 0.885 at 0.883, and the mixture 0.886 at 1.004.
- Census, 4 cells. `rej_t` covers 0.889 at 0.456. The S4b cube design covers 0.885 at 0.568, and the D0 tuned interval 0.894 at 0.531.

**The gate rule** is section 2 of `docs/EXECUTION_RULES.md`. The track has no later stage.

## 1. Acceptance

The closing gate is accepted, and the inference track is complete. S4b ran as the S4 memo fixed it, its three predictions are scored (two held, one refuted), the S5 tables match cells exactly, keep only supported D2 cells and count a draw without an interval as a miss, and the closing page states what the evidence supports and leaves the recommendation to Nicolas, as the memo asked. The dry run that reproduces the S4 memo's table cell for cell is a good anchor. Nicolas can merge pull request #32.

## 2. What the track established, for the record

These are the readings carried into the round's close and into the paper's planning. Whether the paper recommends any design is Nicolas's decision (section 4).

1. **Weighting under rejective selection fails, with a known mechanism.** Rejective balance at a small acceptance probability leaves some clusters with inclusion probability near zero and many pairs never sampled together. The Horvitz-Thompson and Hájek means are then biased or unstable, and the Sen-Yates-Grundy variance loses terms. `rej_t` stays D2's interval.
2. **Rejective selection with `rej_t` is the narrowest valid interval on census, and not on tissue.** On census at $n_L \ge 6$ its width is 0.449 to 0.467 of D0 classical at coverage 0.888 to 0.897. On tissue it is 0.876 to 0.921 wide but covers 0.852 to 0.866, below D0's 0.875 to 0.878, and 0.798 at $n_L = 4$ where only $p_a = 0.1$ has the support.
3. **A cube design with bounded inclusion probabilities is a valid, design-based alternative.** Balancing on $\pi_g$, the constant and $\bar f_g$ (S4b), with the Hájek mean and the Sen-Yates-Grundy form, it covers like D0 classical on both domains at $n_L \ge 6$. On tissue it is as narrow as `rej_t` at $n_L = 8$ (0.883) and narrower at 12 (0.801 against 0.921). On census it is 0.568 at $n_L = 8$, wider than `rej_t` and about as wide as the D0 tuned interval (0.531). Balancing on the constant was what made it work on census, as the S4 memo's reading predicted for the Hájek mean. The Horvitz-Thompson mean stays unusable on census, because the landing leaves $\hat N/G$ a few percent from 1 and that carries the level of income.
4. **The mixture of D2 and D0 is the control.** It gives the most reliable design-based coverage, at a width near D0's on tissue. Bounding every inclusion probability below makes a design-based interval valid after balance, and the mixture shows that done crudely it costs most of the gain.
5. **Greedy k-center is a negative result.** Exact enumeration shows the classical interval covering 0.326 to 0.458 on the kidney cancer tasks with the foundation-model encoders, and no design-based variance exists.
6. **Broska and Howes's interval as published under-covers at few clusters** (0.704 on tissue and 0.717 on census at $n_L = 4$, design target). **With this project's small-sample correction (`bh_t`) it covers at $n_L = 4$** (0.884 and 0.882) and is narrower there than the paper's tuned interval, which falls back to the classical interval below six labelled clusters. From $n_L = 8$ it over-covers the design target and is wider, because it has no finite-population factor.
7. **Kluger et al.'s cluster bootstrap under Bernoulli designs under-covers** at these cluster counts (0.618 at $n_L = 4$ on tissue for the design target, 0.565 to 0.808 for the superpopulation target).
8. **The gains come from the predictor.** With the constant or the permuted predictor no design narrows the interval, so the width gains above are information in $\bar f_g$, not artefacts of the designs.
9. **Round 5's $\theta_2$ failures** were draws in which `rej_t` forms no interval, which round 5 counted as misses and round 7 at first did not. Outside lung the two rounds agree once the counting is the same.

What is not established is section 10 of the report, items 1 to 7, and stands as written. The superpopulation target for the cube designs, every result that took one value of the score, $\tau$, $\epsilon$ or the skewed law, and the reason $\hat N$ misses $G$ under S4b are the main gaps.

## 3. Answers to the escalations

1. **$\hat N = G$ never holds exactly under S4b.** Accepted. The landing always ends on the size equation and drops the constant. Recorded as not established.
2. **S4b.3 refuted, and its reading.** Accepted as a reading. The direct test, a landing that keeps the constant to the end, is listed for any later round and not run now.
3. **The S4 memo's D0 figure at $n_L = 4$.** Accepted, and the correction is the oversight chat's. The memo gave D0 classical 0.903 on the 12 supported tissue cells at $p_a = 0.1$. Counting draws without an interval as misses, as the memo itself required of every row, it is 0.874. The 0.903 was D0's coverage over formed draws. The contrast with `rej_t` (0.798) stands, smaller. The round's README records the correction.
4. **The cube designs at $n_L = 4$.** Accepted. With three balance variables the primary reference leaves one degree of freedom, so no interval is formed, and the coverage of 0 says nothing about the design. The paper's design-based balanced interval is therefore stated for $n_L \ge 6$.
5. **The tissue gain from the constant.** Accepted as not examined.
6. **The skewed simulation law.** Accepted. With the variance accurate (estimated over empirical 0.992), the shortfall to 0.820 is the reference distribution at these sample sizes under that law. Only one skewed law was run.

## 4. For Nicolas

The track hands three decisions to Nicolas, recorded in `CLAUDE.md`.
1. **R7-5, positioning against Broska and Howes** (with David). The paper cannot claim the few-cluster regime in general, since a corrected version of their interval covers at four labelled clusters. What remains its own is the finite-population factor for the design target at moderate and large $n_L/G$, the design results of items 2 and 3, and the negative results of items 1 and 5.
2. **R7-6, the tuned estimator below six labelled clusters.** A global coefficient with a $t$ reference does better at $n_L = 4$ than round 5's cross-fitted rule, which sets the coefficient to zero there.
3. **R7-7, which balanced design the paper recommends.** The evidence supports `rej_t` on census and the S4b cube design on tissue, with the cube design as the design-based option on both at $n_L \ge 6$. `[proposed]` The oversight chat's view is that the paper presents rejective selection with `rej_t` as the narrowest option where its support and one balance variable allow, and the S4b cube design as the design-based alternative with a guarantee that does not rest on the regression behind `rej_t`.

## 5. What happens now

The session's work is finished. Nicolas merges pull request #32. The oversight chat then closes round 7 through `/project-state-keeping`, since both tracks have ended.
