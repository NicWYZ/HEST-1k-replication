# Round 7, the inference track, decisions at the S4 gate

14 October 2026. Written by the oversight chat for the execution session of the inference track, after reviewing the S4 report (`docs/round07/i02/ppi/round07_ppi_S4_report.md`, pull request #31, tag `round7-ppi-S4`). This memo opens interval i03, which holds a short stage S4b and then S5. After Nicolas has merged pull request #31, commit this memo unchanged at this path on your branch as the first commit of i03.

**Revisions**
- 14 October 2026. First version.
- 14 October 2026, before handover. Revised after an independent check. The comparison of designs is now on matched, supported cells, which reverses the first version's reading on tissue. The explanation of the cube design's loss on census is replaced by one the data support, and S4b is added to test it. Statements about the paper are marked `[proposed]`.

**What was read and checked.** The whole report, and the merged tables behind it, recomputed from the files on the branch.
- The S3 grid `results/round7/ppi/S3_adaptive/_merged_r2/s3_masking_grid.csv` and its report numbers, set beside the D2 and D0 rows of `results/round7/ppi/S1_weighting/_merged/s1_masking_grid.csv` and the supports in `results/round7/ppi/S1_weighting/_merged/s1_masking_diag.csv`.
- The Broska and Howes variants in `results/round7/ppi/S2b_diagnostics/numbers_items_2_3_r2/s2b3_masking_grid.csv`, set beside the D0 widths of `results/round7/ppi/S2_comparators/_merged/s2_masking_grid.csv`.
- The S4 report numbers in `results/round7/ppi/S4_kcenter/_merged_r2/s4_report_numbers.csv`.

The report's S3 and S4 headline figures match the files. Section 2 adds comparisons on matched cells.

**The gate rule** is section 2 of `docs/EXECUTION_RULES.md`. The track's last gate is S5. Nothing beyond S4b and S5 is set up, staged or piloted.

## 1. Acceptance

The S4 gate is accepted. Every exit item is met, with the two qualifications the report states. S2b confirms the S2 memo's reading of $\theta_2$ outside lung and gives a plausible partial account inside it. The cube sampler passes its test, and its primary variance does not. The report scores S3.2, S3.4 and S3.5 as refuted without softening them, raises the failure of `bh_t_fpc` against its own theory, and keeps S4.1 at the pre-registered definition while showing the other count. Nicolas can merge pull request #31.

## 2. What the interval establishes

The report's pooled figures mix the informative arms with the constant and permuted controls. The comparisons below are restricted to the informative arms (the three encoders on tissue and the package predictor on census), with balance on the estimand's own $\bar f_g$. Each design is compared with D2 `rej_t` on exactly the same task, arm, estimand and $n_L$, only where D2's support is at least 1,000, at $p_a = 0.01$. Coverage counts a draw without an interval as a miss for every design. Width is the ratio to D0 classical. The figures are medians over cells of the median over genes. The cube design uses the Hájek mean with the Sen-Yates-Grundy form, and so does the mixture.

| domain, $n_L$, cells | D0 classical coverage | `rej_t` coverage | `rej_t` width | cube coverage | cube width | mixture coverage | mixture width |
|---|---|---|---|---|---|---|---|
| tissue, 8, 18 | 0.875 | 0.861 | 0.888 | 0.885 | 0.891 | 0.886 | 1.004 |
| tissue, 12, 18 | 0.879 | 0.866 | 0.921 | 0.876 | 0.820 | 0.881 | 0.982 |
| census, 8, 4 | 0.886 | 0.889 | 0.456 | 0.899 | 0.912 | 0.912 | 0.834 |

At $n_L = 4$ only 4 census cells and no tissue cell reach the support of 1,000 at $p_a = 0.01$. At $p_a = 0.1$ the 12 supported tissue cells at $n_L = 4$ give `rej_t` a coverage of 0.797 against 0.903 for D0 classical, counting draws without an interval as misses.

1. **On tissue, the cube design matches or beats rejective selection.** At $n_L = 8$ it is as narrow as `rej_t` and covers closer to D0 classical, and at $n_L = 12$ it is narrower. Its inclusion probabilities are known and bounded below, so its interval is design-based. `[proposed]` For tissue, the cube design with the first score is a candidate for the paper's balanced design beside `rej_t`.
2. **On census, rejective selection keeps a large advantage.** `rej_t` has a width of 0.456 of D0 classical at $n_L = 8$, against 0.912 for the cube design and 0.834 for the mixture.
3. **Why the cube design loses on census, a reading that S4b tests.** The cube design balances on $\pi_g$ and on the uncentred $\bar f_g$. That fixes the sample size and makes the Horvitz-Thompson estimate of $\bar F$ exact, but it does not fix $\hat N = \sum_{g \in L} 1/\pi_g$. The Hájek mean of the predictions is then
$$
\frac{\sum_{g \in L} \bar f_g/\pi_g}{\hat N} = \bar F\,\frac{G}{\hat N},
$$
which misses $\bar F$ by $\bar F\,(G/\hat N - 1)$. That error is large when the level of $\bar f_g$ is large against its spread, as for income. The Horvitz-Thompson mean suffers in the same way, since it carries the level of $\bar z_g$ itself. Its width under the cube design at $n_L = 8$ is 3.48 times D0 classical's on census and 0.84 times on tissue. The first version of this memo explained the gap by the landing phase. That does not fit, because the median balance residual is smaller on census than on tissue. Balancing also on the constant, $x_g = 1$, makes $\hat N = G$ exactly and should remove the error. S4b tests this.
4. **The mixture of D2 and D0.** It keeps none of balance's width gain on tissue (width 1.004 at $n_L = 8$) and about 30% of `rej_t`'s gain on census. Its coverage is the best of the design-based intervals on the real tasks, but in the skewed simulation its median is 0.844, and only $\epsilon = 0.5$ was run. `[proposed]` In the paper it is a control, showing that bounding every inclusion probability below makes a design-based interval valid, and what that costs. It is not the paper's candidate, which answers the report's proposal.
5. **The cube design's variance.** The residual form is too small, by a few percent on the real tasks with the first score and by a fifth with the second, and it fails the synthetic test at $G \le 24$. The Sen-Yates-Grundy form with simulated $\hat\pi_{gh}$ is defined in every S3 cell (zero pairs at most 0.0014) and does better on every measure. In simulation both under-cover under the skewed law. S3.2 stays refuted as scored.
6. **k-center is a negative result the paper can state exactly.** Its exact coverage of the classical interval falls to 0.326 to 0.458 on the two kidney cancer tasks with the foundation-model encoders. $\hat\theta_{\mathrm{HT}}$ is unbiased by construction but 1.38 to 3.33 times as variable as the classical mean under D0. Many pairs are never sampled together (median share 0.732 at $n_L = 4$, 0.431 at $n_L = 8$), so no design-based variance exists, and `apx_size` intervals cover 0.58 to 0.72.
7. **The project's correction of Broska and Howes's interval is a strong comparator at $n_L = 4$.** The published interval covers 0.706 there. With the $t_{n_L-1}$ quantile and the divisor $n_L - 1$ on the labelled term, which is this project's correction and not theirs (`bh_t`), it covers 0.885 on tissue at a width of 0.846 of D0 classical, and 0.883 on census at 0.444. The paper's tuned interval at $n_L = 4$ is the classical interval, because rule `c_crossfit_design` sets the coefficient to zero when $n_L < 6$ (`docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`). With $t_{n_L-2}$ in place of $t_{n_L-1}$ (`bh_t_n2`), the corrected interval covers 0.949 on tissue at a width of 1.110. From $n_L = 8$, `bh_t` is wider than the tuned interval and over-covers the design target, because it has no finite-population factor (width 1.103 against 0.975, coverage 0.922 against 0.876, informative cells, both domains). Section 4 puts the consequences to Nicolas.

## 3. Answers to the escalations

1. **The failed recount job.** Accepted.
2. **Deliveries carried results.** Accepted. Snapshots copy only `code/`, so no job read them.
3. **Lung $\theta_2$ against round 5.** Accepted as recorded. The explanation by ties at a float32 threshold stays unchecked, and S5 lists it under what is not established.
4. **`bh_t_fpc` under-covers.** Accepted. Theory 2.1's expectation was wrong.
5. **$\rho_{\mathrm{BH}}$ overstates the measured ratio.** Accepted as an open point. The derivation holds $\lambda$ fixed, while the empirical variance includes the noise of $\hat\lambda$ fitted on a handful of labelled clusters, which raises the denominator. In S5, add a note to theory section 2.1 saying this, marked as an explanation not derived or checked.
6. **The cube design's primary variance.** From S4b on, the Sen-Yates-Grundy form with simulated $\hat\pi_{gh}$ is the cube design's interval, with the residual form beside it and its failure stated. The scores of S3.2, S3.4 and S3.5 stay as made.
7. **The inexact-draw count.** Accepted.
8. **The two resumed sub-agents.** Accepted. No job was submitted twice.
9. **The largest $\hat\pi_g$ differences.** Accepted. With up to several thousand comparisons per cell over 300 cells, a maximum near 5 is consistent with Monte Carlo error.
10. **Theory 4.3's first expectation.** Accepted as scored.
11. **S4.1 and the pooling of arms.** The pre-registered median over five arms gives the score, partly held, with the count over encoders beside it.

**Section 9, the proposed next step.** The batch version after Kluger and Bates is not run. The mixture is not taken as the paper's candidate (section 2, item 4). The cube design's variance is settled by item 6 above.

## 4. For Nicolas, not for the session

Neither question changes S4b or S5.
1. **The paper's positioning against Broska and Howes** (O5, with David). With a correction any reader could make, their interval covers at four labelled clusters and is narrower there than the paper's tuned interval. What the paper can still claim as its own, on these results, is the finite-population factor for the design target at moderate and large $n_L/G$, the design results, and the negative results on weighting under rejective selection and on k-center. The positioning note should be revised after the round closes.
2. **The tuned estimator below $n_L = 6$.** Rule `c_crossfit_design`, which round 5 closed, sets the coefficient to zero below six labelled clusters. A global coefficient with a $t$ reference does better at four. Whether the paper's estimator changes there alters what round 5 closed, so it is Nicolas's decision, for after the round.

## 5. Interval i03

### S4b. The cube design with the constant balanced (capped at one day)

1. **Theory.** In theory section 3, write the cube design with balance variables $\pi_g$, $1$ and $\bar f_g$, say why the constant makes $\hat N = G$ and what that does to the Hájek and Horvitz-Thompson means, and check that the flight phase can meet three balance equations at every $n_L$ of the grid.
2. **Runs.** That design with the first score, on all six tasks of the masking grid and on the simulation cells with $n_L \ge 8$, with the Hájek and Horvitz-Thompson means, the Sen-Yates-Grundy form with simulated $\hat\pi_{gh}$ and the residual form. Repeat the sampler test of S3 first. Outputs in `results/round7/ppi/S4b_cube_constant/`, merged as in S3.
3. **Predictions, written before any run.**
   - **S4b.1** On census at $n_L = 8$, the Hájek interval under the new design has a width at most 0.70 of D0 classical, in the median over the informative cells.
   - **S4b.2** On the matched supported tissue cells at $n_L = 8$, its width is within 0.03 of the S3 cube design's, and its coverage within 0.03 of D0 classical.
   - **S4b.3** Its Horvitz-Thompson width on census at $n_L = 8$ is below 1.

### S5. The closing report (one day; gate, end of track)

1. **The numbers job,** from the merged tables of S1 to S4b, with no new draws. Outputs in `results/round7/ppi/S5_numbers/`.
   - Every table matches cells exactly across designs (task, arm, estimand, $n_L$), keeps D2 cells with support of at least 1,000, and drops degenerate cells. Each table states its cell count.
   - Coverage over all draws, with a draw without an interval counted as a miss, is the primary figure in every row, with the coverage over formed draws and the share formed beside it.
   - The informative-cell tables of section 2 at every $n_L$ and both $p_a$, for D0 classical and tuned, D2 `rej_t`, the cube designs of S3 and S4b, the mixture, `bh` and `bh_t`, with tissue and census separately and widths against D0 classical and against `rej_t`.
   - `bh_t` and `bh_t_n2` against the tuned interval by $n_L$, for the design target with `textbook_t|fpc|lin|xf` and for the superpopulation target with round 5's tuned superpopulation interval.
   - The control arms (constant, permuted, `perm_cluster`) in a separate table.
   - The Horvitz-Thompson and Hájek widths and the balance residuals of every cube design, by domain.
2. **Theory.** The note on $\rho_{\mathrm{BH}}$ of section 3, item 5.
3. **The report** in `docs/round07/i03/ppi/round07_ppi_final_report.md`, covering S4b and S5, in the format of section 7 of `docs/EXECUTION_RULES.md`, with S4b's predictions scored, ending with a closing page "What the inference track established in round 7". For each design (D0, D2 with `rej_t`, D2 with weighting, the cube designs, the mixture, k-center) and each comparator (Broska and Howes as published and with the project's correction, Kluger et al.), it says whether the results support recommending it, under which conditions, against which comparator and at what width, with $\theta_2$ coverages carrying their share formed. Whether the paper recommends a design is Nicolas's decision, so the page states what the evidence supports. It lists what is not established, including the items of section 8 of the S4 report, escalations 3 and 5 above, the superpopulation target for the S3 and S4b designs, and every result that rests on one simulation law, one score or one value of $\epsilon$.
4. Run the sweep, commit, tag `round7-ppi-final`, push the branch and the tag together, open one pull request, and stop.

## 6. What the session does next

1. Fetch `main`. After Nicolas has merged pull request #31, commit this memo unchanged at `docs/round07/i03/ppi/round07_ppi_S4_decisions.md`, then transcribe it into the plan as interval i03.
2. Run S4b, then S5, and stop at the closing gate.
