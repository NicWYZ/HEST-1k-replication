# Round 5, the inference track, the E5 decision memo (end of track)

9 October 2026. Written by the oversight chat after reading `docs/round05/i03/ppi/round5_ppi_final_report.md` at tag `round5-ppi-final` (`e5fd30f`, pull request #20), `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`, `docs/round05/tracks/ppi/round5_ppi_theory.md` section 3 and `docs/round05/tracks/ppi/round5_ppi_plan.md` section 8, and checking the report against `e4b_acceptance.csv`, `e4b_bootstrap.csv`, `e4b_prediction_scores.csv`, `e4b_rej_width_ratios.csv`, `e4b_d2_diagnostics.csv`, `e4b_stamp_check.csv`, `e5_allocation.csv`, `e5_joint_design.csv`, `e5_superpop_undercoverage.csv`, `e5_theta2_dropped_draws.csv`, `provenance_index_summary.csv` and `code_deliveries.csv`. Nicolas hands this to the inference session in full. It closes the track. The session transcribes it into `docs/round05/tracks/ppi/round5_ppi_plan.md` as section 9, commits this memo unchanged as `docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, and then does only what section 6 lists.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

---

## 1. Acceptance

The final report is accepted and the track is complete. Every number I checked reads back as quoted, and the predictions are scored as the report scores them. E4b ran as instructed on all six tasks and in simulation. Acceptance checks 1 and 2 pass, and all four E4b predictions held. Check 3 fails in 4 of 208 cells, and section 2 says what can and cannot be said about why. The definition document applied the memo's rule strictly and left balanced selection out, which was the right reading of the rule as written.

The process held. Every sub-agent stamp carries its own frame id (191 of 191 in `E4b/e4b_stamp_check.csv`), code reached Longleaf as 11 bundles with a read-only snapshot each (`code_deliveries.csv`), and the provenance index fails only in the same 5 rows as at the E4 gate. The tag marks the report's last commit, and the corrections of the E4 memo's section 2 are carried in the report's section 6.3.

## 2. What I checked, and what the files add

**Why check 3 fails is not established.** The four failing cells are two designs, census by state, $\theta_3$, $n_L = 4$, at both values of $p_a$, with $|z|$ of 3.15 and 3.81. Uneven inclusion at small $n_L$ does not single them out. Under `perm_cluster` at $n_L = 4$, the Spearman correlation between a cluster's inclusion frequency and $|\bar f_g - \bar F|$ is $-0.57$ and $-0.60$ in the failing cells, and about as strong in cells that pass, $-0.57$ on CCRCC, $-0.68$ on Indiana and $-0.59$ to $-0.62$ on census by area (`E4b/e4b_d2_diagnostics.csv`). Census by area also has a single outcome and passes 32 of 32. What the check leaves out is the spread over permutations, since its bootstrap standard error covers only the noise of the draws, and on a census task one permutation decides each cell. Two failing designs among cells that share draws and repeat across arms may be within what a correct null gives, but that was not worked out, as the report's escalation 1 says. The decision below does not depend on it, because the design result is stated only for $n_L$ of 8 or more.

**Where `rej_t` fails.** With balance on the estimand's own $\bar f_g$, one balance variable, `rej_t` covers within 0.03 of the D0 classical interval in every supported cell at $n_L$ of 8 and 12, and in 92% and 75% of supported cells at $n_L$ of 4 and 6, never below 0.803 (`E4b/e4b_rej_width_ratios.csv`, support of at least 1,000). The 17 supported cells below 0.80 all have two balance variables on a tissue task, `pcF2` or `pcE2`. The eight worst, 0.641 to 0.684, are all Indiana $\theta_2$ at $n_L = 6$ and $p_a = 0.1$, where the residual regression has three degrees of freedom. The other nine, 0.781 to just under 0.80, are `pcF2` cells at $n_L$ of 6 and 8, eight of them on the kidney cancer tasks, where the share of genes with standardised bias above 3 is 0.48 to 0.94. Bias alone does not predict failure, since 46 of the 208 supported own-balance cells have a share of 0.5 or more and still cover at least 0.804. So the session's reading in escalation 7, too few residual degrees of freedom, fits the worst cells better than uneven inclusion does. Both point to the same region where the design behaves, which is one balance variable and $n_L$ of 8 or more.

**Escalation 9.** On lung the fitted $m^\star_{\text{PP}}$ is close to the formula evaluated at $n_L = 4$, where the between coefficient is zero, 52.9 against 53.2 with `hoptimus0` (`E5/e5_allocation.csv`). That fits the E4 memo's reading that the fitted curve cannot carry a between gain that changes with $n_L$. On the other tasks the fitted curve is off in the classical value as well, 157.8 against 125.0 from the components on Indiana and 136.4 against 102.9 on census by area, so the fitted values are not a reliable check there. The paper leads with

$$
m^\star_{\text{PP}}(n_L) = m^\star\sqrt{\frac{1 - R^2_w}{\rho_c(n_L)}}
$$

with the measured $\rho_c(n_L)$, and gives the fitted value beside it. This settles the last sentence of the definition document's allocation section, which gives both values with a caveat. The optimum is also flat. With cost proportional to $c_d + c_s m$ and variance to $A + B/m$, labelling $m = x\,m^\star_{\text{PP}}$ units instead of the optimum multiplies the variance at a fixed budget by

$$
\frac{(1 + q/x)(1 + q\,x)}{(1 + q)^2}, \qquad q = \frac{c_s\,m^\star_{\text{PP}}}{c_d}
$$

where the expression follows by substituting $B = A\,c_s\,(m^\star_{\text{PP}})^2/c_d$ and skipping the algebra. On lung with `hoptimus0` at $c_d/c_s = 100$ and $n_L = 8$, $m^\star_{\text{PP}} = 86.7$, so $q = 0.867$, and using the fitted 52.9 gives $x = 0.61$ and a factor of 1.06. The two values differ by a factor of 1.6 and cost 6% in variance. The factor holds the two variance components at their values for $n_L = 8$ and leaves out the finite-population factor, which matters at $G = 15$, so it shows how flat the optimum is rather than an exact cost.

## 3. Readings for the paper

1. **The estimator.** `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md` stands as written, with the allocation choice of section 2. Form C within clusters, the between coefficient under `c_crossfit_design`, the interval `textbook_t|fpc|lin|xf`, the stratified draw for $\theta_2$ over donors where both groups are present, and regime B's reference degrees of freedom.
2. **What the predictions buy in regime B.** Against the classical estimator of form C, the $\theta_3$ width ratio is 0.982 to 1.009 on the three kidney tasks, 0.706 to 0.847 on lung and 0.594 to 0.625 on the two census tasks, and the interval covers 0.855 to 0.950 over all 196 rows (`E5/e5_joint_design.csv`). On the Visium kidney tasks the encoders buy nothing once the level is removed. On lung and census they buy 15 to 41% of the width.
3. **Choosing the labelled clusters.** At $n_L = 8$, rejective selection on the estimand's own $\bar f_g$ with `rej_t` gives 0.726 of the D0 classical width on kidney cancer with `uni_v2` and 0.551 on census by state, against 0.852 and 0.618 for the tuned estimator under simple random selection (`E4b/e4b_rej_width_ratios.csv`). In these cells balanced selection is narrower than tuning, as theory section 3 leads one to expect, since no coefficient enters the point estimate. The paper presents this as a design result with its conditions. These are one balance variable, the estimand's own $\bar f_g$, a support $p_a\binom{G}{n_L}$ of at least 1,000, and $n_L$ of 8 or more. It also states where the design failed, which is two balance variables at few residual degrees of freedom. These conditions were read from the same runs and are not a validated rule. The definition document's default stays simple random selection.
4. **Allocation.** Section 2. The classical $m^\star$ at $c_d/c_s = 100$ is 77.9 on CCRCC, 125.0 on Indiana, 74.5 on lung and 268.7 on census by state, against round 4's 121, 236, 172 and 379. With a predictor and the between coefficient in use, the optimum on lung at $n_L = 8$ rises to 80 to 88 across the three encoders (`E5/e5_allocation.csv`).
5. **The superpopulation target.** Its interval covers below 0.85 in 916 of 8,820 simulation cells, all in regime A with a predictor at $G$ of 15 and 24, with minimum 0.705 (`E5/e5_superpop_undercoverage.csv`). The paper's real-data claims use the design target, and the superpopulation interval is stated with this limit.

## 4. Answers to the escalations

1. **Check 3 and balanced selection.** Section 2 and section 3 item 3. Why the two designs fail is not established. The definition document stands, and balanced selection enters the paper as a design result with its conditions and where it failed.
2. **The float32 threshold.** Accepted. The 8 reruns at `b410529` differ from the others only in the threshold code.
3. **E4's thresholds recomputed with the float32 code.** Accepted without a rerun.
4. **Permuted-arm parquet paths.** Accepted.
5. **Premature submissions.** Recorded. The report's section 2 says each brief carried the frame id, and this escalation says it arrived in a later message. Every stamp matches, so the record is sound. In the next round's briefs the frame id goes in the first message to each sub-agent.
6. **Lung has no acceptance-3 cell.** Accepted. Lung's balance results are reported with their support beside them.
7. **`rej_t` at three residual degrees of freedom.** Section 2. The session's reading fits the worst cells, and the paper's design result is stated for one balance variable and $n_L$ of 8 or more.
8. **Pilot outputs.** Accepted.
9. **The allocation value.** Section 2. The paper uses the formula with the measured $\rho_c(n_L)$.
10. **Delivery 8's size.** Accepted.
11. **Fuller (2009) in abstract only.** Accepted. The paper cites Morgan and Rubin for the scaling, says the sampling form is derived here, and cites Fuller for the regression estimator under rejective sampling only as far as its abstract supports.
12. **`pcF2` equals `own` on census.** Accepted, with one correction. `E4b/e4b_d2_diagnostics.csv` records $k = 1$ for census `pcF2`, and its `rej_t` rows equal the own rows, so they repeat own with $k = 1$, not 2. They are not reported separately.
13. **E4's dropped $\theta_2$ draws.** Accepted, with the shares in `E5/e5_theta2_dropped_draws.csv`.

## 5. The question the track leaves

Rejective selection uses only label-free quantities, so each cluster's inclusion probability under D2 can be computed by simulating the design before any label is bought. A Horvitz-Thompson or Hájek mean of the labelled clusters, weighted by those probabilities, would then be unbiased for the design, and the residual variance of section 3 of the theory document would apply to it. Whether that removes the bias at small $n_L$ and with several balance variables, whether a floor on the residual degrees of freedom is still needed, and what it costs in width, is the first question for the next round. It is not part of this track and nothing is run for it now.

## 6. What the session does before stopping

1. Transcribe this memo as plan section 9 and commit it, with this memo unchanged as `docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, in one commit. Nothing else is edited.
2. After Nicolas has merged pull request #20, push `round5-ppi` once and open one pull request into `main` carrying that commit. No tag. Nothing is delivered to Longleaf, since the commit changes documents only.
3. Stop. The track is closed.
