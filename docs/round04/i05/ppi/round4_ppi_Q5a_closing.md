# Round 4, the PPI track, the Q5a closing memo (end of track)

3 October 2026. Written by the oversight chat after reading section 10 and the closing page of `docs/round04/i03/ppi/round4_ppi_final_report.md` at `8cca44f` on `round4-ppi` (pull request #8), and checking them against `results/round4/ppi/Q5a/q5a_escalation2_reconciliation.csv`, `q5a_design_variance_before_after.csv`, `q5a_spot_weighted_permuted.csv`, `results/round4/ppi/Q4a_recompute/q4a_table61.csv`, `results/round4/ppi/Q4_tables/q4_main_table.csv`, `q4_gene_axis_summary.csv`, `q4_prediction_scores.csv`, `q4_report_numbers.csv` and `results/round4/ppi/Q5_joint/q5_report_numbers.csv`. This memo closes the track. It is a record. It is not handed to the PPI session, and no session does anything under it.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

---

## 1. Acceptance

Q5a is accepted and the PPI track is complete. Every number I checked in section 10 and on the closing page reads back from the files as quoted. The numeric-claim sweep file `results/round4/ppi/Q5a/q5a_sweep.tsv` has no unresolved rows. The five items of the Q5 decision memo's section 3 were done as asked.

## 2. Escalation 2 was a defect in the interval, and my memo guessed the wrong column

The Q5 memo said either the diagnostic column or the interval was wrong and leaned towards the diagnostic. The per-draw reconciliation shows it was the interval. With a cross-fitted $\lambda$ the labelled donors in the two halves carry different values $\lambda_g$, and the coefficient on the population prediction term is their average over the labelled donors, $c_U = \frac{1}{n_L}\sum_{g \in L}\lambda_g$. Writing $\bar F$ for the population mean of the prediction term, the donor-weighted estimator is

$$
\hat\theta = c_U\,\bar F + \frac{1}{n_L}\sum_{g \in L}\big(\bar z_g - \lambda_g \bar f_g\big) = \frac{1}{n_L}\sum_{g \in L}\big(\bar z_g - \lambda_g(\bar f_g - \bar F)\big).
$$

So each labelled donor's contribution carries $\lambda_g \bar F$. The old variance left that term out. When the two halves have different $\lambda$ and $\bar F$ is large against the spread of $\bar f_g$ between donors, the omitted term makes the donor contributions look far more variable than the estimator is. Adding $(\lambda_g - c_U)\bar F$ to each contribution is exact given the two values of $\lambda$. It is zero when every donor has the same $\lambda$, so the classical rows do not move. The corrected interval is written as `textbook_t|fpc|lin` beside the unchanged rows, and the final design-target role in `q4_main_table.csv` sits on the corrected rows.

The fix matters on ACS and hardly at all on the HEST tasks, where the $\theta_3$ weights are centred and $\bar F$ is small against the spread between donors. The before and after values are in section 10.1 of the final report. Point estimates, empirical variances, variance ratios and $\hat\lambda$ are unchanged.

## 3. One qualification for the paper

The closing page's ranges for the Visium tasks and for lung Xenium are for the estimand $\theta_3$ on the donor-weighted population. The $\theta_2$ rows in `q4a_table61.csv` show smaller gains on the same tasks. The paper quotes the closing page's ranges as $\theta_3$ numbers and reports $\theta_2$ beside them.

## 4. Decisions on the Q5a escalations

- 1 (the estimator definition): accepted. The oversight chat adds the linearised term to `docs/round04/tracks/ppi/round4_ppi_estimator_definition.md` in a separate commit after pull request #8 is merged.
- 2 (same-seed reruns under "no new masking draws"): accepted. The items needed per-draw outputs that had not been kept, Nicolas approved the reading, and every old column reproduced.
- 3 (the pause and restart on finding the defect): accepted. Fixing the code before the reruns finished was the right order.
- 4 (process limit) and 5 (one floating-point difference): recorded.

## 5. What leaves the track

- The spot-weighted PPI rows are nuisance rows and the paper treats them as a finding about the estimand. A regression-form spot-weighted estimand, under which donor-level weight sums cancel, is a round-5 candidate.
- Round 5 starts from `results/round4/ppi/Q5_joint/q5_cluster_table.csv` for active cluster selection, and from Q5 and C3 for the paper's joint design section.
- The decisions above the sessions are unchanged from the conformal track's C4 memo, section 5.
