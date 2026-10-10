# Round 5, the inference track, the E4 decision memo

9 October 2026. Written by the oversight chat after reading `docs/round05/i02/ppi/round5_ppi_E4_report.md` at `bf9b869`, the head of `round5-ppi` and of pull request #17, together with `docs/round05/tracks/ppi/round5_ppi_theory.md` sections 2.0 to 2.6 and `docs/round05/tracks/ppi/round5_ppi_plan.md` section 7, and checking the report against `e3a_sim_prediction_cells.csv`, `e3a_masking_E3a3_table_nL8_12_16.csv`, `e3_prediction_cells.csv`, `e3_prediction_scores.csv`, `e3_components.csv`, `e3_components_fitted.csv`, `e3_masking_grid.csv`, `e3_superseded_round4_numbers.csv`, `e4_selection_grid.csv`, `e4_prediction_scores.csv`, `e4_perm_balance_diagnostic.csv`, `e4_inclusion_bias.csv`, `provenance_index.csv`, `provenance_index_summary.csv`, `code_deliveries.csv` and `E2_regimeB/diag/PROVENANCE__report_extra.txt`. The tag `round5-ppi-E4` marks `7e0a00e`, one commit earlier. The later commit rewords E4.4's verdict and escalation 1's conclusion, adds two exceptions to the sweep and reruns it, and this memo reviews that later version. Nicolas hands this to the inference session in full. Transcribe it into `docs/round05/tracks/ppi/round5_ppi_plan.md` as section 8, and commit this memo unchanged as `docs/round05/i03/ppi/round5_ppi_E4_decisions.md`, before anything in it runs. Interval 3 (E4b and E5, ending at the E5 gate) starts when both are committed locally.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

This track's gates are E2, E4 and E5. E5 is the last.

---

## 1. Acceptance

The E4 report is accepted. Every number I checked reads back as quoted, with the two corrections of section 2, and the predictions are scored as the report scores them except E3.3, which section 2 rescores.

- **E3a.** Section 2.0 of the theory document closes the derivation and corrects my reasoning. The current estimate carries about $\delta^2 s_f^2$, not $d^2 s_f^2$, and the finite-population factor then removes a fraction $n_L/G$ of the whole cross-fitting term. The conclusion and the corrected estimate stand, and the form with the mean squared deviation of each cluster's coefficient also covers odd $n_L$. The acceptance passes, E3a.1 and E3a.2 hold, and E3a.3 holds for $\theta_3$. `textbook_t|fpc|lin|xf` is the paper's design-target interval.
- **E3.** The four acceptance checks pass. Check 3 is the real test of form C, and check 4 is trivial for the constant arm, as escalation 6 says.
- **E4.** Check 1a passes. Check 1b differs only where the two rounds treat draws with fewer than two valid donors differently. Check 2 fails, and the band was my error. I set it as if the 50 genes gave independent replicates, but every gene of a task shares the same 200 draws, so the median over genes does not average the draw noise away. On a census task there is one outcome, and the band was much narrower than the Monte Carlo error of a single variance ratio from 200 draws. On lung the failure is a design with very few distinct samples, as the report says. Section 5, E4b, redoes the check.
- **The three records naming `8b879bb`.** My reading in the E2 memo was wrong. The file holds three appended records, one per job, and I took the first record's commit for all three. The index's treatment is right.

Nicolas merges pull request #17 after reading this memo. Nothing is pushed to `round5-ppi` until that merge has happened.

## 2. What I checked, two corrections and two findings

**E3.3 splits by estimand.** The report reads E3.3's band as holding in half the cells because form C narrows the classical estimator by "about 9%" on kidney cancer and "2 to 4%" on Indiana and lung. Those are medians over both estimands. For $\theta_3$ the form C classical estimator is 0.818 to 0.854 of form P's width on the two kidney cancer tasks, 0.928 to 0.962 on Indiana and 0.936 to 0.948 on lung. For $\theta_2$ under the stratified draw the two classical forms give the same width, 1.000 to 1.003 (`results/round5/ppi/E3_twolevel/e3_prediction_cells.csv`, prediction E3.3). So the 144 cells in the band are exactly the 144 $\theta_3$ cells, and the band could not apply to $\theta_2$. E3.3's first clause held for $\theta_3$ in every cell and is not applicable to $\theta_2$. With its second clause, which held, E3.3 is held for $\theta_3$.

**The regime B minimum of 0.500 is on census by state, not by area.** It is in `e3_superseded_round4_numbers.csv` at cost ratio 100, at the budget where round 4 labelled one unit per state (`m` equal to 1), where round 4 covered as little as 0.545. That is below the smallest number of labelled units either form needs, so it says nothing about the method.

**What balanced selection delivers as an interval.** At $n_L = 8$ for $\theta_3$, with balance on the estimand's own $\bar f_g$ at $p_a = 0.01$, the classical interval's width under D2 is 0.93 to 1.08 of its width under D0 on every task and encoder (`results/round5/ppi/E4_selection/e4_selection_grid.csv`, median over genes of `width_median`). Its ratio of estimated to empirical variance rises to 1.2 to 1.5 on the kidney cancer tasks, 3.2 to 4.0 on lung, and 3.3 and 7.4 on the two census tasks. So the variance falls as E4.2 says and the interval does not see it. The simple-random-sampling formula uses the spread of $\bar z_g$ among the labelled clusters, which balance on the mean of $\bar f_g$ does not change. The tuned estimator under D2 is 2 to 8% narrower than the tuned estimator under D0 on the three kidney tasks and 0 to 2% wider on lung and census. I read this as the tuning cost remaining, since balance does not touch the halves' difference $\Delta$ of theory section 2.0. This is a gap in my brief. Its reason for E4 was that the classical mean of balanced clusters has the reduced variance with nothing tuned, but it specified no interval that uses that. Section 5, E4b, adds it.

**E3.5's second clause and the fitted components.** For form C, $\theta_3$ and the three encoders on the four tissue tasks, the fitted within-cluster component's ratio of PPI to classical is 1.01 to 1.09 times $1 - R^2_w$, which is about what the within tuning cost should add. The fitted between-cluster component's ratio is 0.98 to 1.04, while $1 - R^2_c$ is 0.29 to 0.95 (medians over genes, `e3_components_fitted.csv` against `e3_components.csv`). The between gain is real. On lung with `hoptimus0`, the ratio of median variances at every unit labelled is 1.000 at $n_L = 4$, where $\lambda^c = 0$, and 0.395, 0.377 and 0.379 at $n_L = 6$, 8 and 12 (`e3_masking_grid.csv`). A curve $a/n_L + b/(n_L m) + c$ cannot carry a between gain that is zero below $n_L = 6$ and pays a tuning cost above it, so it put the gain elsewhere. E3.5's second clause compared the formula with a fit that cannot express it. The derivation of theory section 2.4 stands for coefficients fixed in advance, and section 5, E5 item 2, says how the paper states it.

## 3. Readings for the paper

1. **The design-target interval.** With the cross-fitting term restored, the ratio of estimated to empirical variance is 0.97 to 1.01 at $G = 15$ and $n_L = 12$, against 0.69 to 0.91 without it, and coverage is 0.888 to 0.903 against 0.840 to 0.886 (`E3a_crossfit/e3a_sim_prediction_cells.csv`). The correction costs width only where the term is real. On lung at $n_L = 12$ the corrected $\theta_3$ interval is 0.702 of the classical width against 0.649 uncorrected, and it covers 0.885, the same as the classical interval, against 0.870 uncorrected (`e3a_masking_E3a3_table_nL8_12_16.csv`).
2. **Form C is the paper's within-cluster form.** A predictor constant within each cluster changes nothing, exactly. The permuted predictor's width ratio against the form C classical estimator is 1.000 to 1.017 in regime B at $m \ge 10$. For $\theta_3$ the form C classical estimator is 4 to 18% narrower than form P's, and form C covers within 0.87 to 0.92 in all 864 cells from $m = 5$. Form P stays in the record as the pooled-intercept comparator.
3. **The group difference in regime B.** Under the stratified draw $\theta_2$ covers 0.885 to 0.913 at every $m \ge 6$ on every tissue task and arm, against a median over cells from 0.73 at $m = 2$ to 0.84 at $m = 100$ under simple random draws in E2.
4. **Regime B under the two-level estimator.** It stays narrower than regime A in 210 of 232 comparisons. On the kidney tasks the regime ratio is the same with and without the predictor. On lung and census by area the predictor helps regime A slightly more than regime B (median differences 0.056 and 0.146 in the regime B over regime A width ratio), so regime B's advantage is the design.
5. **Balanced selection.** The classical estimator's variance under D2 falls to about $1 - R^2$ of its D0 value at $G = 51$ (78 of 80 cells within 0.05) and less reliably at $G = 15$ and 24. On the real tasks the fall is 0.604 on kidney cancer for `uni_v2` and 0.264 on census by state at $n_L = 8$, against 0.844 and 0.434 for the tuned estimator under D0. No interval run so far delivers it. Whether one can is E4b.
6. **Lung's balance numbers.** At $G = 15$ and $n_L = 8$ there are 6,435 possible samples, and $p_a = 0.01$ keeps about 64. Lung's D2 rows describe a nearly fixed design, and the paper reports them with that number beside them.

## 4. What stays in force, and four additions

Plan section 7, including its section 7.3 on code delivery, pushes and shared files, stays in force. Plan section 7.4 on local runs stays in force. Four additions.

1. **Frame ids.** `docs/WAYS_OF_WORKING.md` already says it, and interval 2 missed it in 173 of 175 unit records. The lead writes each sub-agent's own frame id into its brief and compares the id in every returned stamp with the one it assigned before merging that unit. A stamp with the wrong id is fixed before the merge.
2. **Shared files.** Pull request #17 adds two entries to `.gitignore`. That is accepted. Any further change to a file outside the track's areas is an escalation in the next report.
3. **The tag.** At the E5 gate the tag goes on the last commit of the push, after every wording correction.
4. **Briefs.** The lead checks each sub-agent's brief against the unit it is meant for before dispatch, since interval 2 sent the E4 simulation sub-agent the E3 brief.

## 5. Interval 3

### E4b. An interval that uses the balance (one day, capped; first in the interval)

**Theory first.** Write section 3 of `docs/round05/tracks/ppi/round5_ppi_theory.md` before any E4b job. Take D2 with $k$ balance variables $x_g$ and the Mahalanobis acceptance of E4. Write

$$
\bar z_L - \bar Z = (\bar e_L - \bar E) + B^\top(\bar x_L - \bar X)
$$

with $\bar Z$ and $\bar X$ the means over the $G$ clusters, $B$ the population least-squares coefficient of $\bar z_g$ on $x_g$ over the $G$ clusters, and $e_g = \bar z_g - B^\top x_g$. Under simple random sampling the two terms are uncorrelated, because $B$ makes the population covariance of $e_g$ and $x_g$ zero. Rejective acceptance on the Mahalanobis distance of $\bar x_L - \bar X$ leaves the first term's distribution approximately unchanged and scales the covariance of the second by

$$
v_a = \frac{P(\chi^2_{k+2} \le q_a)}{P(\chi^2_k \le q_a)}
$$

with $q_a$ the $p_a$ quantile of $\chi^2_k$ (Morgan and Rubin 2012, Theorem 3.1, here in sampling form). Derive the resulting variance of the classical mean under D2 with the finite-population factor, and the estimate

$$
\widehat{\text{Var}}_{\text{rej}} = \Big(1 - \frac{n_L}{G}\Big)\frac{s^2_{\text{res}} + v_a\,\hat b^\top S_x\,\hat b}{n_L}
$$

where $\hat b$ and $s^2_{\text{res}}$ come from least squares of $\bar z_g$ on $x_g$ with an intercept over the labelled clusters, $s^2_{\text{res}}$ has divisor $n_L - k - 1$, and $S_x$ is the labelled clusters' sample covariance of $x_g$. The reference is $t_{n_L - k - 1}$. The point estimate is the classical mean $\bar z_L$, so no coefficient enters it and there is no tuning cost. State the conditions under which the approximation holds, including the number of distinct samples the design can accept, and confirm that Morgan and Rubin and Fuller (2009) are the right references before relying on them. If the derivation does not close, stop and report.

**Code.** Add the interval as `rej_t` to `round5_ppi_balance.py`, for D2 only. It needs $n_L - k - 1 \ge 2$. Cells below that are skipped and listed. Add a cluster-level null control `perm_cluster`, the `resnet50` arm's own $\bar f_g$ permuted across clusters with a crc32 seed per gene, so that its distribution over clusters is kept and any link to a cluster's own weights is broken. Keep the unit-level `perm` control beside it. In the simulation, a draw with no accepted candidate draws further candidates until one is accepted. No draw falls back to its last candidate, and the number of candidates per accepted draw is recorded.

**Runs.** Rerun E4's real-task masking on all six tasks with 2,000 accepted draws per cell, the first 200 with E4's seeds. Designs D0, D1 and D2 at $p_a \in \{0.1, 0.01\}$. Balance variables `own`, `pcF2`, `pcE2`, `perm` and `perm_cluster`. $\theta_3$ and $\theta_2$, donor-weighted, every unit labelled, design target, $n_L \in \{4, 6, 8, 12\}$, the three encoders and the permuted arm. Intervals `textbook_t|fpc|lin` for the classical mean, `textbook_t|fpc|lin|xf` for the tuned estimator, `rej_t` under D2 and `strat_t` under D1. Rerun E4's simulation with `rej_t` added. Report beside every D2 cell its support, $p_a \binom{G}{n_L}$, the standard deviation over clusters of the inclusion frequency, its Spearman correlation with $|\bar f_g - \bar F|$ for the balance variable, and the share of genes with standardised bias above 3. Fan out by task, six units on Longleaf, plus one local simulation unit under plan section 7.4.

**Acceptance.**

1. The first 200 draws of each D0 and D1 cell reproduce E4's rows at the E0 tolerances. D2's threshold is the $p_a$ quantile over a larger candidate pool, so its rows are set beside E4's without a tolerance, and the change in the threshold is reported.
2. `rej_t`'s point estimate equals the classical estimate on every draw.
3. Check 2, restated. For each cell, a bootstrap over draws, resampling the 2,000 draws of each design with replacement and jointly for all genes, 500 times, gives a standard error for the ratio of median variances under D2 and D0. With `perm_cluster` the ratio is within three standard errors of 1 in every cell whose support is at least 1,000.

**Predictions.**

1. E4b.1. In the simulation under the normal law with balance on $\bar f_g$ at $p_a = 0.01$, `rej_t` covers 0.88 to 0.92 in every cell with $n_L \ge 6$ and support of at least 1,000, and is narrower than the tuned estimator's interval under D0 in every such cell with $n_L \le 8$ and $R^2 \ge 0.4$.
2. E4b.2. On the real tasks at $n_L = 8$ for $\theta_3$ with own balance at $p_a = 0.01$, `rej_t`'s width relative to the D0 classical interval is 0.72 to 0.88 for `uni_v2` on kidney cancer, 0.45 to 0.62 on census by state and 0.50 to 0.65 on lung. On the two kidney cancer tasks it is narrower than the tuned estimator's D0 interval for every encoder, and it covers within 0.03 of the D0 classical interval.
3. E4b.3. On the kidney cancer tasks for $\theta_2$, the unit-level `perm` control falls outside three standard errors of 1 in more cells than `perm_cluster` does. The reason I expect is that a unit-level permuted predictor's $\bar f_g$ is most spread on donors with a rare group, whose $\bar z_g$ is also extreme, so it is not a null variable for a cluster-level design.
4. E4b.4. With 2,000 draws, lung's own-balance variance ratios at $n_L = 8$ and $p_a = 0.01$ stay within 0.05 of E4's 0.255 to 0.330, because they belong to the accepted set and not to the number of draws.

### E5. As the brief says, with these changes

1. **The definition document.** `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md` defines the paper's estimator with form C within clusters, the between coefficient under rule `c_crossfit_design`, the interval `textbook_t|fpc|lin|xf`, regime B's reference with $\sum_g (m_g - 2)$ degrees of freedom for $\theta_3$ and $\sum_{g,h}(m_{h,g} - 1)$ for $\theta_2$, and the stratified draw for $\theta_2$. For $\theta_2$ the clusters are the donors where both groups are present, and draws are taken from those. Where E4's code drew from all donors and dropped draws, the report gives the share dropped per cell rather than rerunning. D2 with `rej_t` enters the document as the design option if E4b's acceptance passes and E4b.1's coverage clause holds, with its support condition. Otherwise the document says that balance reduces the variance and that no interval run here captures it. The document also says where the superpopulation-target interval covers below 0.85 in E3's simulation, since the paper's real-data claims use the design target only.
2. **Allocation.** State theory section 2.4's result for coefficients fixed in advance. Then give `results/round5/ppi/E5_joint/e5_allocation.csv`, one row per task, encoder and $n_L$, for form C and $\theta_3$, computed locally from committed files. It carries $1 - R^2_w$ and $1 - R^2_c$ from `e3_components.csv`, the measured between ratio $\rho_c(n_L)$, which is the ratio of median variances of `C_ppi` to `C_classical` at every unit labelled in `e3_masking_grid.csv`, the classical $m^\star$ at $c_d/c_s = 100$ from the components, and

$$
m^\star_{\text{PP}}(n_L) = m^\star\sqrt{\frac{1 - R^2_w}{\rho_c(n_L)}}
$$

with the fitted values of `e3_components_fitted.csv` beside them as the check. This also gives census by state its form C value.
3. **The joint design table** uses form C. Read `results/round5/conformal/W3_real/merged/w3_map_by_task.csv` from `origin/main` after fetching, if pull request #18 has been merged, and record the commit, as the brief says.
4. **Regime B coverage statements** are made only at budgets where every cluster gets at least the form's smallest number of labelled units. Other cells are marked.
5. **The final report** covers E1 to E5 and E4b, scores E4b.1 to E4b.4, carries the corrections of section 2 of this memo, and lists every round-4 statement this round changes. The closing page is as the brief says.
6. **The sweep** runs with `.verify-exceptions-round5-ppi`. An exception that states a derived value, such as a sum, is checked by recomputing it before it is declared. The README is not swept.
7. **The push.** Tag `round5-ppi-final` on the last commit, push once after pull request #17 is merged, open one pull request, and stop.

## 6. Answers to the escalations

1. **Check 2.** Section 1 and E4b.
2. **Check 1b.** Accepted. Section 5, E5 item 1, fixes one convention for the paper.
3. **E4 code defects.** Accepted. The superseded outputs stay as the record.
4. **The E3 simulation.** Accepted. `r5e3sim_final` is the record. Section 4 item 4 covers the dispatch.
5. **Process.** Job 4338818 is recorded and its output was not used. Section 4 item 1 covers the stamps.
6. **E3 check 4.** Accepted as trivial for the constant arm. Check 3 is the test of form C.
7. **The records naming `8b879bb`.** My error, as section 1 says. The index stands as committed.

The discrepancies of the report's section 7 are accepted as recorded, with the census correction of section 2. Of its section 8, items 2 and 5 are E4b and item 4 comes out of E4b's runs. Item 3 is answered in section 2, item 7 by E5 item 2, and item 6 is the oversight chat's. Item 1 is not pursued.
