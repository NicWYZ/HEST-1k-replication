# Round 7, the inference track, decisions at the S4 gate

14 October 2026. Written by the oversight chat for the execution session of the inference track, after reviewing the S4 report (`docs/round07/i02/ppi/round07_ppi_S4_report.md`, pull request #31, tag `round7-ppi-S4`). This memo opens interval i03, which holds S5 only. Commit it unchanged at this path on your branch as the first commit of i03, after Nicolas has merged pull request #31.

**What was read and checked.** The whole report, and the merged tables behind it. These were recomputed from the files on the branch.
- The S2b prediction scores and the Broska and Howes variants in `results/round7/ppi/S2b_diagnostics/numbers_items_2_3_r2/s2b3_masking_grid.csv`, set beside the D0 widths of `results/round7/ppi/S2_comparators/_merged/s2_masking_grid.csv`.
- The S3 grid `results/round7/ppi/S3_adaptive/_merged_r2/s3_masking_grid.csv` and its report numbers, set beside the D2 and D0 rows of `results/round7/ppi/S1_weighting/_merged/s1_masking_grid.csv`.
- The S4 report numbers in `results/round7/ppi/S4_kcenter/_merged_r2/s4_report_numbers.csv`.

The S3 and S4 headline figures of the report match the files. Section 2 adds comparisons the report did not make, restricted to the cells where balance can help.

**The gate rule** is section 2 of `docs/EXECUTION_RULES.md`. S5 has no gate after it, and nothing beyond S5 is set up, staged or piloted.

## 1. Acceptance

The S4 gate is accepted. Every exit item is met, with the two qualifications the report states. S2b confirms the S2 memo's reading of $\theta_2$ outside lung and gives a plausible partial account inside it. The cube sampler passes its test, and its primary variance does not. The report scores S3.2, S3.4 and S3.5 as refuted without softening them, raises the failure of `bh_t_fpc` against its own theory, and keeps S4.1 at the pre-registered definition while showing the other count. Nicolas can merge pull request #31.

## 2. What the interval establishes for the paper

**The comparison that matters is in the informative cells.** The report's pooled figures mix the informative arms with the constant and permuted controls, and the mixture's 0.912 share of cells within 0.03 of D0 classical is over all of them. Where a design is meant to help, the arms are the three encoders on tissue and the package predictor on census, and the balance is on the estimand's own $\bar f_g$. Over those cells, with the median over cells of the median over genes, the designs compare as follows. Coverage for the S3 designs counts a draw without an interval as a miss. Width is the ratio to D0 classical. The `rej_t` rows are S1's at $p_a = 0.01$.

| design and interval | $n_L = 4$ coverage | $n_L = 4$ width | $n_L = 8$ coverage | $n_L = 8$ width |
|---|---|---|---|---|
| D0, classical | 0.900 | 1 | 0.882 | 1 |
| D2, `rej_t` | 0.886 | 0.865 | 0.878 | 0.849 |
| cube, first score, Hájek, Sen-Yates-Grundy | 0.919 | 1.104 | 0.885 | 0.887 |
| mixture of D2 and D0, Hájek, Sen-Yates-Grundy | 0.799 | 1.038 | 0.886 | 0.982 |

The `rej_t` coverage at $n_L = 4$ is over the draws that formed an interval. Counting the others as misses it is 0.819, because $\theta_2$ cells at $n_L = 4$ often leave too few valid clusters.

1. **Rejective selection with `rej_t` remains the paper's balanced design.** At $n_L = 8$ it is the narrowest interval that covers like D0 classical. The cube design is 4% wider than `rej_t` at the median, and the mixture 16% wider. On census the gap is large. On `ACS_CA_PUMA` with the package predictor at $n_L = 8$, `rej_t` has a width of 0.361 of D0 classical for $\theta_3$, the cube design 0.865 and the mixture 0.817 to 0.833.
2. **So the mixture is not the paper's candidate.** The report proposes it because its coverage is the best of the design-based intervals. But it buys that coverage by giving up nearly all of what balance gains. Its width at $n_L = 8$ in the informative cells is 0.98 of D0 classical. A design that is as wide as simple random selection is not a reason to balance. In the paper the mixture is a control. It shows that the design-based route is valid once every inclusion probability is bounded below, and what that costs.
3. **The cube design is a real competitor on tissue and not on census.** In the paper's headline cell, `CCRCC` with `uni_v2`, $\theta_3$, $n_L = 8$, it has a width of 0.768 of D0 classical against 0.726 for `rej_t`, and covers 0.881 against 0.832. On census it loses most of the gain. The likely reason is structural. The cube method's landing phase cannot meet the balance more tightly than about one cluster's contribution to $\sum_{g \in L} x_g/\pi_g$, which is a relative error of order $1/n_L$. Rejective selection at $p_a = 0.01$ balances far more tightly, but leaves the inclusion probabilities uncontrolled. The median relative balance residual of 0.077 under the cube design fits this. At few labelled clusters, exact balance and known, bounded inclusion probabilities pull against each other, and that trade-off is a statement the paper can make. This reading is the oversight chat's and S5 states it as a reading, not a result.
4. **The cube design's variance.** The residual form is too small, by a few percent on the real tasks with the first score and by a fifth with the second, and it fails the synthetic test at $G \le 24$. The Sen-Yates-Grundy form with simulated $\hat\pi_{gh}$ is defined in every S3 cell (zero pairs at most 0.0014) and does better on every measure. In simulation both under-cover under the skewed law, and S3.2 stays refuted as scored.
5. **k-center is a negative result the paper can state exactly.** Its exact coverage of the classical interval falls to 0.326 to 0.458 on the two kidney cancer tasks with the foundation-model encoders, and $\hat\theta_{\mathrm{HT}}$, unbiased by construction, is 1.38 to 3.33 times as variable as the classical mean under D0. With most pairs never sampled together, no design-based variance exists, and `apx_size` intervals cover 0.58 to 0.72.
6. **Broska and Howes's interval with a small-sample correction is a strong comparator.** This changes the paper's positioning. Over the informative cells under D0 for the design target, compared with the paper's tuned interval `textbook_t|fpc|lin|xf`, the median coverage and width ratio to D0 classical are these (`s2b3_masking_grid.csv` against `s2_masking_grid.csv`).

   | $n_L$ | `bh_t` coverage | `bh_t` width | tuned coverage | tuned width |
   |---|---|---|---|---|
   | 4 | 0.884 | 0.834 | 0.900 | 1.000 |
   | 6 | 0.905 | 0.983 | 0.886 | 0.982 |
   | 8 | 0.922 | 1.103 | 0.876 | 0.975 |
   | 12 | 0.958 | 1.335 | 0.879 | 0.997 |

   At $n_L = 4$ the tuned interval cannot cross-fit its coefficient and falls back to the classical interval, while `bh_t` uses one global $\hat\lambda$ and is 17% narrower at a coverage 0.016 lower. From $n_L = 8$ `bh_t` is wider and over-covers, because it has no finite-population factor. So the paper's advantage over a corrected Broska and Howes interval is the finite-population factor at moderate and large $n_L/G$, and the design results. At the smallest $n_L$ the corrected interval is better on width. The positioning note's section 5 (open question O5) needs this added, and section 4 below puts it to Nicolas.

## 3. Answers to the escalations

1. **The failed recount job.** Accepted.
2. **Deliveries carried results.** Accepted. Snapshots copy only `code/`, so no job read them.
3. **Lung $\theta_2$ against round 5.** Accepted as recorded. The 8 lung cells that differ are those round 5 ran on its float32-threshold snapshot, and the explanation by ties at the threshold stays unchecked. S5 lists it under what is not established. No further run.
4. **`bh_t_fpc` under-covers.** Accepted. Theory 2.1's expectation was wrong.
5. **$\rho_{\mathrm{BH}}$ overstates the measured ratio.** Accepted as an open point. The derivation holds $\lambda$ fixed, while the empirical variance includes the noise of $\hat\lambda$ fitted on a handful of labelled clusters, which raises the denominator. In S5, add a short note to theory section 2.1 saying this, marked as an explanation that was not derived or checked.
6. **The cube design's primary variance.** In S5 the Sen-Yates-Grundy form with simulated $\hat\pi_{gh}$ is reported as the cube design's interval, with the residual form beside it and its failure stated. The scores of S3.2, S3.4 and S3.5 stay as made with the pre-registered primary.
7. **The inexact-draw count.** Accepted. The balance residual is the useful figure.
8. **The two resumed sub-agents.** Accepted. No job was submitted twice.
9. **The largest $\hat\pi_g$ differences.** Accepted. With up to several thousand comparisons per cell over 300 cells, a maximum near 5 is what Monte Carlo error alone would produce.
10. **Theory 4.3's first expectation.** Accepted as scored.
11. **S4.1 and the pooling of arms.** The pre-registered definition, the median over five arms, gives the score, partly held. The count over encoders is reported beside it, as the report does.

**Section 9, the proposed next step.** The batch version after Kluger and Bates is not run, as proposed. The mixture is not taken as the paper's candidate (section 2, item 2). The cube design's variance is not revisited this round.

## 4. For Nicolas, not for the session

Two questions follow from section 2. Neither changes S5.
1. **The paper's positioning against Broska and Howes** (O5, with David). The paper can no longer claim the few-cluster regime as its own ground in general. With a $t$ quantile and the divisor $n_L - 1$, their interval covers at four labelled clusters and is narrower than the paper's tuned interval there. What remains the paper's own is the finite-population factor for the design target, the design results with rejective balance, and the negative results on weighting and k-center. The positioning note should be revised after the round closes.
2. **The tuned estimator at the smallest $n_L$.** Round 5 closed the cross-fitted coefficient (`c_crossfit_design`), which cannot be formed at $n_L = 4$. A global coefficient with a $t$ reference, as `bh_t` uses, does better there. Whether the paper's estimator should switch to a global coefficient below some $n_L$ is a change to what round 5 closed, so it is Nicolas's decision, for after the round.

## 5. Interval i03, S5, the closing report (one day; gate, end of track)

No new draws. One numbers job from the existing merged tables, then the report.

1. **The numbers job.** Add to `round7_ppi_s3s4_numbers.py`, or a new `round7_ppi_s5_numbers.py`, the tables of section 2 of this memo.
   - The informative-cell table, at every $n_L$, for D0 classical, D0 tuned, D2 `rej_t` at both $p_a$, the cube design with both scores and the mixture with each of their variances, `bh` and `bh_t`. Report coverage over all draws and over formed draws, the share formed, and widths against D0 classical and against `rej_t`, with tissue and census separately.
   - The comparison of `bh_t` and `bh_t_n2` with the tuned interval by $n_L$, for both targets.
   - The control arms (constant, permuted, `perm_cluster`) in a separate table, so the pooled figures of the S4 report can be read against them.

   Outputs in `results/round7/ppi/S5_numbers/`.
2. **Theory.** The note on $\rho_{\mathrm{BH}}$ of section 3, item 5, in theory section 2.1. In theory section 3, the cube design's landing limit as section 2 item 3 describes it, as a reading marked unchecked.
3. **The report** in `docs/round07/i03/ppi/round07_ppi_final_report.md`, in the format of section 7 of `docs/EXECUTION_RULES.md`, ending with a closing page "What the inference track established in round 7". For each design (D0, D2 with `rej_t`, D2 with weighting, the cube design, the mixture, k-center) and each comparator (Broska and Howes as published and corrected, Kluger et al.), it says whether the paper can recommend it, under which conditions, against which comparator, and at what width, with $\theta_2$ coverages carrying their share formed. It lists what is not established, including the items of section 8 of the S4 report, escalations 3 and 5 above, the superpopulation target for the S3 designs, and every result that rests on one simulation law or one score.
4. Run the sweep, commit, tag `round7-ppi-final`, push the branch and the tag together, open one pull request, and stop.

There are no new predictions, since S5 runs nothing new.

## 6. What the session does next

1. Fetch `main`. Transcribe this memo into the plan as interval i03.
2. Commit this memo unchanged at `docs/round07/i03/ppi/round07_ppi_S4_decisions.md`, after Nicolas has merged pull request #31.
3. Run S5 and stop at the closing gate.
