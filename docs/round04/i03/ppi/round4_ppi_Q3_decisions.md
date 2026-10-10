# Round 4, the PPI track, the Q3 decision memo

2 October 2026. Written by the oversight chat after reading `docs/round04/i02/ppi/round4_ppi_Q3_report.md` at tag `round4-ppi-Q3` (`93e0ae3`, pull request #4), `docs/round04/tracks/ppi/round4_ppi_theory.md` and the estimator definition, and checking the report's numbers against `q2_report_numbers.csv`, `q3_report_numbers.csv`, `q3_prediction_scores.csv`, `q1b_report_numbers.csv`, `q2_sim_theorem.csv` and the merged grid `q2_variance_grid.csv`. Nicolas hands this to the PPI session in full. Transcribe it into `docs/round04/tracks/ppi/round4_ppi_plan.md` as section 14 before anything in it runs. Interval 3 (Q4 and Q5, ending at the Q5 gate) starts when the transcription is committed and Nicolas has merged the Q3 pull request.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. This track's gates are Q1, Q3 and Q5. Contact with anyone outside the project is never the session's decision.

---

## 1. Acceptance, and a different reading of the headline

The Q3 report is accepted. Every number I checked reads back as quoted. The predictions are scored as the report scores them, and most of mine failed on magnitude; section 5 of the report says why in each case and I agree with each.

Escalation 1 says the donor-weighted PPI estimator loses to the classical one on every HEST task. The table that supports it (section 6.1) is taken at the largest $n_L$ and the superpopulation target, and that is the one corner of the grid where the loss is general. I read `q2_variance_grid.csv` across $n_L$ and both targets for $\theta_3$ donor-weighted at $m = $ all, rule (c). Three things come out of it.

- **At $n_L \le 8$ the encoders gain on CCRCC and lung.** Superpopulation target, empirical variance ratio: CCRCC `uni_v2` 0.84, 0.75, 0.82 at $n_L = 4, 6, 8$; `hoptimus0` 0.93, 0.86, 1.02; lung `hoptimus0` 0.55, 0.52, 0.56 and `uni_v2` 0.54, 0.51, 0.55. Indiana is at 1.0 throughout. The loss appears at $n_L = 12$ and 16.
- **The loss at large $n_L$ is the complement form's unlabelled term.** With $n_L = 16$ of 24 donors, $U$ has 8 donors, and on lung with $n_L = 12$ of 15 it has 3, where the superpopulation ratio is 1.4 to 1.6 against 0.87 to 0.91 on the design target. $V_U = \lambda^2 \text{Var}(p_g)/G_U$ is as large as the labelled term there. That is a fact about the superpopulation form with a small complement, not about the predictors, and the design-based target, which every real-data coverage check uses, does not have it.
- **The design-target ratios drift to 1 as $n_L$ grows because $\lambda$ is tuned for the wrong objective.** The tuned $\lambda$ is identical on both targets in every cell, and it falls from about 0.45 at $n_L = 4$ to 0.29 at $n_L = 16$ on CCRCC as $G_U$ shrinks, because the tuning rule minimises the complement form's variance, whose $U$ term penalises $\lambda$ by $\lambda^2 \text{Var}(p_g)/G_U$. The textbook form has no such term, so for the design target $\lambda$ should minimise the between-donor variance of the rectifier over the labelled donors alone. Addendum 1 section 2 said the rules were unchanged for the textbook form, and that was my error. Section 3 corrects it and section 4 recomputes.

So the honest statement is narrower than escalation 1. On the real HEST tasks the achievable gain is small, because the predictors' donor-level squared correlation on the contrast scale is at most 0.44, and at $n_L \le 16$ the cost of estimating $\lambda$ takes much of what remains; where $G_U$ is small the complement form adds a loss of its own. On ACS, with donor-level $R^2$ of 0.57 and 0.95, the gain is large under either target. The gain theorem itself holds, since the oracle-$\lambda$ arm of the theorem check sits 0.03 to 0.08 above $1 - R^2_{\text{cluster}}$ at $G_U = 100$ and the estimated-$\lambda$ arm is what moves away from it. Section 5 makes the tuning cost a stated result.

Escalation 2 is a clarification I accept in full. For the donor-weighted estimands the donor-level contribution is a within-donor contrast, so a donor-constant shift in the predictions cancels, and the $R^2_{\text{cluster}}$ in the theorem is the squared correlation across donors of the predicted and true contrasts. The theory document states the setting for a general linear estimand with donor contributions $z_g$ and $f_g$, and reads $u_g$ and $p_g$ on that scale; `q2_cluster_r2.csv`'s `z`-scale column is the one every table uses. Recalibration by a donor offset cannot move these estimands and is dropped from the paper apart from one sentence.

## 2. The estimator, finalised

- **$\lambda$.** Rule (c), cross-fitted over halves of the labelled donors, with $\lambda = 0$ when $n_L < 6$ (kept from rule (d)). Rule (d) is dropped. In the simulation (d2) protects the null case, but on the real HEST tasks it is worse than (c) where it matters: on CCRCC `uni_v2` at $n_L = 16$, design target, (d2) has an empirical variance ratio of 1.17 against 1.03 for (c), with a median $\lambda$ of 0. The draws in which the pre-test passes are the draws in which the half-sample slope is large, so the pre-test selects a biased $\lambda$ and applies it to the other half. That is the known behaviour of pre-test estimators in the intermediate regime, and the intermediate regime is where these predictors live. The paper reports $\hat\lambda$ with its standard error and uses the break-even rule of section 5 to say when a gain is expected, rather than pre-testing.
- **The design-based target.** The textbook form with the finite-population correction and $t_{n_L - 1}$. $\lambda$ for this target is tuned, cross-fitted as in rule (c), by minimising the between-donor sample variance of the rectifier $r_g = z_g - \lambda f_g$ over the tuning half, with no unlabelled term, clipped to $[0, 1]$. This is the GREG coefficient of survey sampling. Name it `c_crossfit_design` in every table and keep the old rows labelled `c_crossfit` so the two can be compared.
- **The superpopulation target.** The complement form, rule (c) as it stands, CR2 with Bell and McCaffrey degrees of freedom (equal to CR1 under equal sizes), no Welch-Satterthwaite combination. Every superpopulation row states $G_U$, and the paper's HEST tables lead with the design target.
- **No bootstrap.** The wild cluster bootstrap-$t$ is dropped; Mammen weights cover less than CR1 at every $G_L$ and Rademacher within 0.03 of it.
- **The spot-weighted slope** is reported with CR2 and the Q1 finding stated beside it, as proposed. Check CR2 on the spot-weighted $\theta_3$ in the Q4 simulation rows before the table is built, as the report proposes.

Update `docs/round04/tracks/ppi/round4_ppi_estimator_definition.md` to this, with the design-target $\lambda$ objective written out, and the simulation and real-data behaviour quoted beside each choice. Put each `$$` on its own line.

## 3. Recomputation before the Q4 tables (unit Q4a)

Recompute every design-target row of Q2 (the masking grid, all tasks, all $n_L$ and $m$) and of Q3 regime A under `c_crossfit_design`, with the same draws and seeds, before any Q4 table is built. If the per-draw sufficient statistics of the masking runs are saved, recompute from them; otherwise rerun the HEST and ACS masking units with the new rule added, keeping every existing row. Regime B and the superpopulation rows are unchanged. The permuted arms run too. Report the recomputed section 6.1 table at every $n_L$, both targets, with `c_crossfit` and `c_crossfit_design` side by side, in the Q5 report.

**Prediction Q4a.1**, written now. Under `c_crossfit_design` the tuned $\lambda$ no longer falls with $n_L$ (median at $n_L = 16$ within 0.1 of the median at $n_L = 8$ on CCRCC for every encoder), and the design-target variance ratio at $n_L = 12$ and 16 is no larger than at $n_L = 8$ for every HEST encoder, with CCRCC `uni_v2` below 0.9 at every $n_L \ge 6$ and lung `hoptimus0` below 0.75 at every $n_L$.

## 4. Theory additions, written before Q4's tables and checked in Q4

Add to `docs/round04/tracks/ppi/round4_ppi_theory.md`, each derived step by step, and stop-and-report if a derivation does not close.

1. **The general setting.** State the gain theorem for a linear estimand with donor contributions $z_g$ (outcome) and $f_g$ (prediction), with $u_g$ and $p_g$ their centred between-donor parts, so that the mean, the group difference and the within-donor slope are cases of one statement. Carry the $G_U$ term, with the limit $1 - R^2_{\text{cluster}}$ reached only as $G_U/n_L \to \infty$, and say that for the design-based target with the textbook form there is no $G_U$ term and the ratio is exactly $S^2_r/S^2_z$.
2. **The tuning cost.** For a cross-fitted $\lambda$ applied to a half of $n_h = n_L/2$ donors whose contributions are independent of $\hat\lambda$, with $p_g$ centred,
   $$\text{Var}\big(\bar r_{\text{half}}\big) = \frac{\text{Var}(u_g - \bar\lambda\,p_g) + \text{Var}(\hat\lambda)\,\text{Var}(p_g)}{n_h}, \qquad \bar\lambda = E[\hat\lambda],$$
   so the variance ratio is $1 - R^2_{\text{cluster}} + \big[\text{Var}(\hat\lambda) + (\bar\lambda - \lambda^\star)^2\big]\text{Var}(p_g)/\sigma_u^2$. Derive it (conditioning on $\hat\lambda$, then the law of total variance), state what the average of the two halves adds, and give the corollary. With $\lambda^\star = \text{Cov}(u, p)/\text{Var}(p)$ one has $R^2_{\text{cluster}} = \lambda^{\star 2}\text{Var}(p_g)/\sigma_u^2$, so predictions reduce the variance if and only if $\lambda^{\star 2} > \text{Var}(\hat\lambda) + (\bar\lambda - \lambda^\star)^2$, which is the statement that $\hat\lambda$ has mean squared error below the square of what it estimates. For an unclipped least-squares $\hat\lambda$ from $n_h$ donors, $\text{Var}(\hat\lambda)\,\text{Var}(p_g)/\sigma_u^2 \approx (1 - R^2)/(n_h - 3)$, which gives the break-even $n_h > 2 + 1/R^2_{\text{cluster}}$, that is $n_L > 4 + 2/R^2_{\text{cluster}}$; say that clipping to $[0, 1]$ lowers $\text{Var}(\hat\lambda)$ so this is a conservative count. This is the paper's answer to "how many labelled clusters before a predictor pays for its own tuning", and it is the reason the HEST encoders gain at $n_L \le 8$ on some tasks and not reliably at 16.
3. **The allocation condition.** State the allocation result as the report's escalation 3 found it: $m^\star_{\text{PP}} \le m^\star$ if and only if $\sigma^2_{e,r}/\sigma^2_e \le \sigma^2_{u,r}/\sigma^2_u$, which at the optimal $\lambda$ is $R^2_{\text{within}} \ge R^2_{\text{cluster}}$. A predictor moves the optimum toward more clusters exactly when it ranks units within clusters better than it ranks clusters, which Q3.4 found for every HEST encoder.

**Prediction Q4.3**, written now, checked on the theorem-check replicates (`theorem_v2`, which has per-replicate $\hat\lambda$, or a rerun of it if they were not kept). In every cell the estimated-$\lambda$ ratio minus the oracle ratio equals $[\text{Var}(\hat\lambda) + (\bar\lambda - \lambda^\star)^2]\text{Var}(p_g)/\sigma_u^2$ within 0.03, with $\text{Var}(\hat\lambda)$ and $\bar\lambda$ measured across replicates. **Prediction Q4.4.** On the real tasks, under `c_crossfit_design`, the sign of (variance ratio minus 1) agrees with the sign of $\text{se}(\hat\lambda)^2 - \hat\lambda^2$ (the break-even rule evaluated from the data's own $\hat\lambda$ and its standard error, median over genes) in at least 18 of the 22 task, predictor and $n_L \in \{8, 16\}$ cells.

## 5. Q4, as instructed with these changes

- **The real-data tables** lead with the design target under `c_crossfit_design`, show every $n_L$ rather than the largest, and carry $\theta_2$ as well as $\theta_3$ in both populations. Superpopulation rows follow with $G_U$ stated. The permuted predictor is on every row. Three encoders. Each row carries $\hat\lambda$ and its standard error.
- **The crossover cost ratio**, Q3.3: run Q3's budget-matched comparison at $c_d/c_s \in \{10, 1000\}$ on every task, with the code as it stands, and score Q3.3 and the reversal clause of Q3.1 in the Q5 report.
- **The ACS application** runs as instructed, states and California PUMAs, with the package predictor's cross-fitted gradient boosting as built in Q0, and reads as the case where the predictor's cluster-level $R^2$ and the cluster count both clear the break-even.
- **The gene axis** and **the two-way supplement** as instructed. Under the gene axis, report the per-gene $\hat\lambda^2 - \text{se}(\hat\lambda)^2$ beside the width ratio, so Q4.1 and the break-even rule are scored on the same table.
- **Recalibration** is closed. One sentence in the paper, the negative leave-one-donor-out $R^2$ and the invariance.
- **The IDC illustration** as instructed.

## 6. Answers to the other escalations

- 3 (allocation) is in section 4. 4 (Q2.7) is in section 4. 5 (ANOVA-corrected $R^2$ undefined on permuted and ACS arms): accepted; report the uncorrected squared correlation beside it as done, and say so in the table notes.
- 6 (Indiana and lung morphology from `morphology_ext`): accepted; it is the round-4 data product for those tasks.
- 7 (prediction drivers for Indiana and lung): accepted; record the md5s in the final report as here.
- 9 (resizing pending jobs with `scontrol`): resizing a pending job's time or memory from a sibling's measurement is allowed and is not moving it; record each resize in the job ledger as done.
- 10 (strays in the clone): accepted; the brief rule stands.
- 11 (the Q1 pull request): the token has been replaced, and the Q3 pull request is open as #4 at `93e0ae3`. Nicolas merges it; nothing for the session to do.
- 12 (50 genes): accepted; the all-genes rerun is not needed.
- 13 (Indiana's 50-gene list): the rule is accepted and is recorded as the task's list; no rerun.
- 14 (local concurrency): recorded.

## 7. Where interval 3 runs

Every Q4 and Q5 job runs on Longleaf through Slurm, with walls sized from a sibling's `sacct`. Nicolas's plan sections 12.2 and 12.3 were his instructions for interval 2 and do not carry forward on their own; if he gives the same instruction for interval 3 in chat, record it as section 12.4 before acting on it. A pending job may be resized from a sibling's measurement; it is not moved to another site by the session. If a job has not started four hours after submission, tell Nicolas in chat what it needs and keep waiting.

## 8. What the Q5 report decides

The Q5 report carries Q4a, the recomputed section 6.1 table, the theory additions with Q4.3 and Q4.4 scored, Q3.3 at the two new cost ratios, the Q4 tables, the joint-design table from the conformal track's C3 outputs once committed (with `within_plain` as a method, per that track's C2 memo), the round-5 cluster table, and the closing page "What the PPI track established". Report and wait.
