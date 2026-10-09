# Round 5 PPI track, the operating plan

This is the session's transcription of `docs/decisions/round5_ppi_track.md` (md5 `65976a7f8e3b18e0bab5ebd459fd467f`), written before any job runs, as section 6 item E0.1 of that brief requires. The brief governs where this plan and the brief differ, except where a numbered extension in section 6 below records a decision Nicolas made in chat.

## 1. Starting point and working copies

The starting commit is `d82c3f33ce37fe2d7dbf5b527bfee9a9fb9ee935` on `main` of `NicWYZ/HEST-1k-replication`, the merge of pull request #14, which carries the brief. Branch `round5-ppi` was created from `origin/main` at that commit on 7 October 2026 in the local clone `~/hest-1k/HEST-1k-replication-PPI` and pushed. That is the only time `main` enters this branch. Nothing is merged into it afterwards.

Before the branch was made the clone's working tree was clean, no `.git/index.lock` was present, and it was on `round4-ppi` at `8cca44f`, which is an ancestor of the starting commit. `round4-ppi` is left as it was. No git command is run in the other two clones under `~/hest-1k`.

On Longleaf the track's code clone is `/work/users/w/e/weiyang/hest_code/round5-ppi/`, a fresh clone of `round5-ppi` made by a Slurm job over the SSH key on Longleaf, and moved only by `git merge --ff-only` from the pushed branch in a Slurm job. The project tree `/work/users/w/e/weiyang/hest_replication` is read only, through `git --no-optional-locks`, and is never checked out, fetched or pulled. The round-4 code clones are not used.

Jobs run from their own output directory under `results/round5/ppi/<STAGE>/` in the project tree, with the code clone on `PYTHONPATH`. Every output directory carries `PROVENANCE.txt` and a `_provenance.json` stamp written by the job on the node. Slurm job names are replaced by the submission route, so jobs are identified by Slurm id, and `PROVENANCE.txt` records the intended prefix `r5ppi_` and the stage.

## 2. The plan

### 2.1 Section 6 of the brief, verbatim

Five stages of analysis and one closing stage. Gates at E2, E4 and E5.

#### E0. Setup and anchors (half a day, capped at one day)

1. Read this document, `docs/WAYS_OF_WORKING.md`, `docs/round4_ppi_estimator_definition.md`, `docs/round4_ppi_theory.md`, the closing page and section 10 of `docs/round4_ppi_final_report.md`, `docs/decisions/round4_ppi_Q5a_closing.md` and part A4 of `docs/deck2/deck2_new_results_explained.md`. Transcribe section 6 into `docs/round5_ppi_plan.md` with the predictions of section 7. List anything in this document that looks wrong in a numbered section of the plan and in the E2 report. Do not change it.
2. Create the branch in the reused local clone as section 5 says, and make the Longleaf clone. Confirm the four md5s of section 3 in the Longleaf clone. Read the project tree's HEAD with `git --no-optional-locks rev-parse HEAD` and record it. If it is not `9d7277d`, record that as an escalation and change nothing. Run `whose()` on `results/round4/`. Confirm that every prediction parquet of section 3 exists on Longleaf and that the tissue files match `q5_input_md5.json`. Record the md5s of the two ACS parquets.
3. **Anchors, all on Longleaf.** Round 4's last runs were local, so this is also the first run of the final code there.
   - `round4_ppi_q4a_tests.py` passes 13 of 13 and `round4_ppi_q1b_tests.py` passes 135 of 135.
   - `round4_ppi_q2_masking.py` on `CCRCC` with `hoptimus0`, `--nl-grid 8 --m-grid 0 --draws 200 --rules none,c_crossfit,c_crossfit_design`, reproduces the matching rows of `q4a_table61.csv`. The tolerance is 0.005 on `coverage_median`, which is one draw of 200, and $10^{-5}$ relative on the variance columns, which is above the cross-node drift recorded in `docs/WAYS_OF_WORKING.md`. Report the largest difference in each column.
   - `round4_ppi_q3_regimes.py` on `CCRCC` with `hoptimus0`, `--budgets 2400 --parts B --rules none,c_crossfit`, reproduces the matching regime B rows of `q4_main_table.csv` at the same tolerances.

Nothing in E1 starts until all three pass.

#### E1. The final design-target interval in simulation (two days; no gate, reported with E2)

**Why.** The paper's design-target interval has been checked only on masking draws of the real tasks. On kidney cancer with 24 donors, Indiana and lung it covers 0.84 to 0.91. In the same cells the classical interval covers 0.85 to 0.92, and the two differ by at most 0.025 in any cell (`q4a_table61.csv`, $\theta_3$, donor-weighted, encoders, $n_L \ge 6$). So most of the shortfall looks like the classical interval's own, and a smaller part looks like the tuning. At $n_L \ge 8$ the final interval's estimated variance is 0.87 to 1.01 of the empirical variance on kidney cancer and 0.83 to 0.90 on lung, against 0.98 to 1.10 and 0.94 to 0.96 for the classical interval (`q4a_table61.csv`). E1 separates the two parts and checks the linearised term where it matters.

**The simulation runs at the level the theory lives at.** With every unit of a labelled cluster labelled, the estimator, the tuning rule and the variance depend on the data only through the $G$ pairs $(\bar z_g, \bar f_g)$. So E1 draws those pairs directly. For each cell, draw 60 finite populations of $G$ pairs

$$
\bar f_g = \kappa + p_g, \qquad \bar z_g = \lambda^\star p_g + \xi_g
$$

with $p_g$ and $\xi_g$ independent, $\text{Var}(p_g) = 1$, and $\text{Var}(\xi_g)$ set so that the squared correlation of $\bar z_g$ and $\bar f_g$ is $R^2$. At $R^2 = 0$ set $\bar z_g = \xi_g$ with unit variance. For each population draw 1,000 simple random samples of $n_L$ clusters with crc32 seeds, and compute the classical and tuned estimates and their intervals against that population's own mean of $\bar z_g$.

**The grid.** $G \in \{15, 24, 51\}$. $n_L \in \{4, 6, 8, 12, 16, 20\}$ with $n_L \le G - 3$. $R^2 \in \{0, 0.2, 0.4, 0.7, 0.9\}$. $\lambda^\star \in \{0.6, 1.2\}$, the second because the real unclipped coefficients reach 1.2 on ACS. The level $\kappa \in \{0, 2, 10\}$ in units of the between-cluster standard deviation of $\bar f_g$, because the linearised term is $(\lambda_g - c_U)\bar F$ and vanishes when the level is zero. Three laws for $p_g$ and $\xi_g$, which are normal, skewed and heavy. The skewed and heavy laws are standardised log-normals whose shape is set from the real tasks, as the next paragraph says.

**The real-task diagnostic, run first.** For each task, predictor, estimand ($\theta_3$ and $\theta_2$, donor-weighted) and gene, compute from the full data the sample skewness and excess kurtosis of the $G$ contributions $\bar z_g$, the same for $\bar z_g - \lambda \bar f_g$ at the finite-population coefficient, the finite-population $R^2$, and the level $\bar F$ over the standard deviation of $\bar f_g$. Write `e1_contribution_moments.csv`. Set the skewed law's shape so that the median absolute skewness of simulated populations of 24 equals the median over genes on `CCRCC`, and the heavy law's shape to the 90th percentile. Then rerun the masking with `--rules none --nl-grid 8 --m-grid 0` on each task, keep the per-gene coverage, and report the Spearman correlation between a gene's classical coverage and the absolute skewness of its contributions.

**Rules and intervals.** Rules `none`, `c_crossfit_design`, and an oracle arm with $\lambda$ fixed at the population's own least-squares coefficient. Intervals `textbook_t|fpc` and `textbook_t|fpc|lin`. One further interval as a diagnostic, capped at half a day, which is Johnson's skewness-adjusted $t$ applied to $e_g$. If it does not restore coverage, report that and drop it.

**Scripts.** `code/scripts/round5_ppi_estimator.py` holds what this round adds to the estimator and imports the round-4 modules unmodified. Its first function is the linearised design variance for whole labelled clusters. `code/scripts/round5_ppi_e1_sim.py` runs the grid. Build the sufficient-statistic arrays the way `synth()` in `round4_ppi_q4a_tests.py` does, so that `lambda_rule` is called unmodified. Fan out by $G$, three units, plus one unit for the diagnostic.

**Acceptance.**

1. The new variance function equals `textbook_two_stage(..., lin=True)` of `round4_ppi_q2_masking.py` on identical inputs with every unit labelled, to $10^{-12}$ relative, on one synthetic array and on one `CCRCC` masking draw.
2. Under rule `none` the two intervals are identical, because the added term is zero when every cluster has the same coefficient.
3. In the oracle arm the empirical variance over draws, divided by $(1 - n_L/G)\,S_r^2/n_L$ computed on the population, is 1 within three Monte Carlo standard errors in every cell. This checks the simulator, since that formula is exact for a fixed coefficient.
4. Under the normal law at $G = 24$, the classical interval's median coverage over cells is within 0.01 of 0.90 at every $n_L$. The round-4 design arm has medians of 0.896 to 0.900 across $n_L$ from 4 to 20 (`results/round4/ppi/Q1_estimator/q1_coverage_by_G.csv`, target `design`, form `textbook`, rule `none`, with the finite-population factor).

**Predictions.**

1. E1.1. Under the normal law the final interval covers 0.88 to 0.91 on average over populations in every cell with $n_L \ge 6$, and within 0.02 of the classical interval in the same cell.
2. E1.2. At $\kappa = 10$ and $R^2 \ge 0.4$ the interval without the linearised term has an estimated variance more than twice the empirical one in at least half the cells, and the interval with it has 0.85 to 1.10 in every cell. At $\kappa = 0$ the two intervals' coverages differ by less than 0.01 in every cell.
3. E1.3. The tuned interval's ratio of estimated to empirical variance is below the classical interval's in the same cell by 0.03 to 0.15 when $n_L/G \ge 1/3$ and $R^2 \ge 0.4$, and by less than 0.05 at $G = 51$ with $n_L \le 12$. That is, the tuning costs a little coverage, and less when the population is large against the sample.
4. E1.4. Coverage varies from one finite population to the next. Under the normal law at $G = 24$ and $n_L = 8$ the 5th to 95th percentile range of the classical interval's per-population coverage is at least 0.03 wide and lies above 0.87. Under the skewed law the classical interval covers 0.85 to 0.89 on average, so the kidney cancer shortfall is reproduced by skewness of the cluster contributions and not by the tuning.
5. E1.5. In every cell above the break-even count $n_L > 4 + 2/R^2$ the empirical variance ratio of the tuned estimator to the classical one is below 1. Below the count it is above 1 in at least half the cells.

**Outputs.** `results/round5/ppi/E1_interval/e1_sim_grid.csv` (one row per cell, rule and interval with coverage, its standard deviation and percentiles across populations, the ratio of estimated to empirical variance, the variance ratio to classical, the median clipped and unclipped coefficient and the Monte Carlo standard error), `e1_contribution_moments.csv`, `e1_real_coverage_vs_skewness.csv`, `e1_acceptance.csv`, `e1_report_numbers.csv`, `fig_e1_coverage.png`.

#### E2. Regime B, completed (three days; gate)

**Why.** Regime B is the result the paper leads with. It has not been run below 6 labelled units per cluster on a tissue task, and section 2.4 says its comparator may be the wrong one.

**Derivation first.** Before any E2 job runs, write section 1 of `docs/round5_ppi_theory.md`. Derive the within-cluster variance of $z_{gi}$ for $\theta_3$ and for $\theta_2$ without the two simplifying assumptions of section 2.4, the variance that a constant predictor removes, and the share $L$ of the within-cluster variance that it removes. Check section 2.4's expression as the special case. If the derivation contradicts section 2.4, stop and report.

**Part 1, equal labelled units per cluster.** Script `code/scripts/round5_ppi_e2_regimeB.py`. It imports `regime_b` unmodified and calls it with $m_g = \min(m, M_g)$ for $m \in \{2, 3, 4, 5, 6, 8, 10, 15, 20, 25, 50, 100\}$. Tasks are all six of section 3. Arms are the three encoders, the permuted predictor, the constant predictor and the donor-constant predictor on the tissue tasks, and the package predictor with the same three controls on ACS. Rules `none` and `c_crossfit`. Both estimands, both populations, both targets. 200 draws with crc32 seeds under a new tag. Skip a control wherever it has no within-cluster variance, which is the case for both constant controls when $w = 1$. Write the unclipped half-sample coefficients beside the clipped ones, since the constant predictor's coefficient is the ratio of the outcome's level to the constant and can exceed 1. Round 4's small ACS settings spread a total budget in proportion to state size, so its "4 units per state" was a median with many states at one unit, where the variance formula has nothing to estimate from. Equal $m$ removes that.

**Part 2, the same question in simulation.** `code/scripts/round5_ppi_e2_sim.py`, built on the generator of `round4_ppi_q3_regimeB_sim.py` with an outcome level added. $G = 24$, $M = 1000$, $m \in \{2, 5, 20, 100\}$, between-cluster share 0.3, outcome level $\mu \in \{0, 1, 3, 10\}$ in units of the outcome's standard deviation, predictors with unit-level correlation $r \in \{0.5, 0.8\}$, an uninformative predictor with the same level as the outcome, and the constant predictor. Estimands $\theta_3$ and the mean. 2,000 replicates per cell.

**Part 3, the decomposition.** For every task, estimand and $m$, the width ratio against the round-4 classical estimator for the constant, donor-constant and permuted predictors and for each real predictor, and the width of each real predictor over the width of the constant and of the donor-constant predictor. Beside them, $\sqrt{1 - R^2_{\text{within}}}$ for each arm, computed on the full data.

Fan out by task, six units, plus one for the simulation.

**Acceptance.**

1. With $m_g = M_g$ regime B returns the full-data value exactly.
2. With the round-4 proportional allocation and the round-4 seed strings, the new script reproduces the E0 regime B anchor rows exactly.
3. In the simulation at $\mu = 0$, the constant predictor's variance ratio is 1.00 within 0.02 and the round-4 simulation's coverage at $m = 5$ and $m = 20$ is reproduced within 0.01 (`results/round4/ppi/Q3_regimes/sim_regimeB/regimeB_sim__G24.csv`).

**Predictions.**

1. E2.1. With equal $m$, the design-target coverage of regime B is 0.87 to 0.92 for every $m \ge 5$ on every task and arm, and 0.78 to 0.90 at $m = 2$ and $m = 3$.
2. E2.2. The constant predictor's width ratio is at or below the permuted predictor's for $\theta_3$ and $\theta_2$ on every tissue task and for $\theta_3$ on ACS, and on the tissue tasks the gap is no more than 0.06. For the mean on ACS the permuted predictor's ratio is 1.00 within 0.01.
3. E2.3. The real predictors' width over the constant predictor's width is 0.93 to 1.00 for $\theta_3$ on kidney cancer and Indiana, at least 0.97 for $\theta_2$ on both, 0.60 to 0.85 for $\theta_3$ on lung, and 0.4 to 0.8 for the package predictor's $\theta_3$ on ACS. So on the Visium tasks nearly all of regime B's gain over the round-4 classical estimator is the level term.
4. E2.4. In the simulation the constant predictor's variance ratio equals $1 - L$ from the derivation within 0.03 at $m \ge 20$, for every $\mu$.
5. E2.5. The ratio of a real predictor's width to the constant predictor's width is flat in $m$ within 0.03 for $m \ge 5$ on every task.

**Outputs.** `results/round5/ppi/E2_regimeB/e2_regimeB_grid.csv`, `e2_level_share.csv`, `e2_decomposition.csv`, `e2_sim.csv`, `e2_acceptance.csv`, `e2_report_numbers.csv`, `fig_e2_coverage_by_m.png`, `fig_e2_decomposition.png`, and section 1 of the theory document. Report E1 and E2 together as `docs/round5_ppi_E2_report.md`, tag `round5-ppi-E2`, and stop.

#### E3. The regression form and the two-level estimator (four days; no gate, reported with E4)

This stage is written on the expectation that E2 confirms section 2.4. The decision memo at the E2 gate will say whether it runs as written.

**Why.** A gain from predictions is real only against a classical estimator that already uses everything known without a predictor. A cluster's slope is defined with the cluster's own intercept, and the ordinary regression slope estimates it that way. The round-4 comparator did not. And round 4 used one coefficient for both levels of a two-stage sample, which is why its allocation condition carried a penalty term (`docs/round4_ppi_theory.md` section 5.3). A coefficient for each level removes it.

**The estimator, as the oversight chat has worked it out.** Check every step in the theory document before any code. If a step does not close, stop and report. It has two stages with a coefficient for each, and the within-cluster stage has two candidate forms. E3 runs both.

*Within a labelled cluster, form C, the cluster's own intercept.* Let $L_g$ be the $m_g$ labelled units. For $\theta_3$,

$$
\hat z_g = \frac{M_g - 1}{M_g}\Big(\lambda^{w}_g\,S_{w\hat y,g} + s_{w,\,y - \lambda^{w}_g \hat y,\,g}\Big)
$$

where $S_{w\hat y,g}$ is the covariance of $w$ and $\hat y$ over all units of the cluster, with divisor $M_g - 1$, and $s_{w,\,y - \lambda \hat y,\,g}$ is the sample covariance of $w$ and $y - \lambda \hat y$ over the labelled units, with divisor $m_g - 1$. A sample covariance is design-unbiased for the cluster's covariance under simple random sampling without replacement, and $\bar z_g = \frac{M_g - 1}{M_g}\,S_{wy,g}$ because $\sum_i w_{gi} = 0$. So $\hat z_g$ is design-unbiased for $\bar z_g$ at any coefficient that does not depend on cluster $g$'s labels. For $\theta_2$, $\hat z_g$ is the difference between the two groups of the labelled units' mean of $y - \lambda^{w}_g \hat y$, plus $\lambda^{w}_g$ times the difference between the two groups of the all-unit mean of $\hat y$. At $\lambda^{w} = 0$ these are the ordinary regression slope and the ordinary difference of group means. A predictor that is constant within the cluster changes neither estimate at all.

*Within a labelled cluster, form P, one pooled intercept.* Write $a_{gi} = w_{gi}$ for the constant predictor's contribution, with cluster mean $\bar a_g$ over all units, which is zero for donor-weighted $\theta_2$ and $\theta_3$.

$$
\hat z_g = \gamma_g\,\bar a_g + \lambda^{w}_g\,\bar f_g + \frac{1}{m_g}\sum_{i \in L_g}\big(z_{gi} - \gamma_g\,a_{gi} - \lambda^{w}_g\,f_{gi}\big)
$$

This stays inside the linear machinery of round 4, is design-unbiased for any coefficients that do not depend on cluster $g$'s labels, and has the simple variance $(1 - m_g/M_g)\,s^2_{r,g}/m_g$ with $s^2_{r,g}$ the labelled units' sample variance of $z - \gamma_g a - \lambda^{w}_g f$. It removes the level common to all clusters and leaves the differences between the clusters' levels.

*Between clusters*, donor-weighted,

$$
\hat\theta = c_U\,\bar F + \frac{1}{n_L}\sum_{g \in L}\big(\hat z_g - \lambda^{c}_g\,\bar f_g\big)
$$

and the variance estimate is the two-stage one,

$$
\widehat{\text{Var}} = \Big(1 - \frac{n_L}{G}\Big)\frac{s_e^2}{n_L} + \frac{1}{G\,n_L}\sum_{g \in L}\hat V_g
$$

with $e_g = \hat z_g - \lambda^{c}_g \bar f_g + (\lambda^{c}_g - c_U)\bar F$ and $\hat V_g$ the estimated within-cluster variance of $\hat z_g$. Under form P, $\hat V_g$ is the simple variance above. Under form C it is the variance of a sample covariance, which the theory document derives by linearisation.

The within coefficients are cross-fitted over two halves of the labelled clusters, as the pooled within-cluster least-squares coefficients, with $\lambda^{w}$ clipped to $[0, 1]$ and $\gamma$ not clipped. The between coefficient $\lambda^{c}_g$ is rule `c_crossfit_design` applied to $(\hat z_g, \bar f_g)$. With every unit labelled the within stage vanishes and both forms are the round-4 final estimator. With $n_L = G$ the between stage vanishes and this is regime B with an intercept. The classical estimator of each form is the same with $\lambda^{w} = \lambda^{c} = 0$.

**What the theory document derives, as its section 2, before any E3 job.**

1. Design-unbiasedness of $\hat z_g$ in both forms and of $\hat\theta$, the two-stage variance and its estimator, and the linearised variance of form C, step by step. State the reference distribution in each corner, and the smallest $m_g$ each form needs.
2. That under form C a predictor constant within clusters changes the estimate by exactly zero, and that under form P a predictor constant over the whole task has zero partial within-cluster $R^2$ given $a$.
3. The allocation result with two coefficients. With $c_d$ per cluster and $c_s$ per unit, show that the optimal units per cluster is $m^\star_{\text{PP}} = m^\star \sqrt{(1 - R^2_{w})/(1 - R^2_{c})}$, where $R^2_w$ is the within-cluster $R^2$ and $R^2_c$ the cluster-level one, both against the classical estimator of the same form, and that $m^\star_{\text{PP}} \le m^\star$ exactly when $R^2_w \ge R^2_c$, with no penalty term.
4. The unit-weighted target. There the cluster-level auxiliary is the cluster's weight sum $A_g = \sum_i w_{gi}$, which is $M_g$ for the mean. Write the estimator with $(A_g, F_g)$ as auxiliaries and with the linearised variance for both coefficients, and the ratio form for the mean beside it as the textbook comparator.
5. The cost of tuning $p$ coefficients. The oversight chat's working is that with $p$ least-squares coefficients estimated on a half of $n_h$ clusters, Gaussian regressors and known population means, the variance ratio against the classical estimator is $(1 - R^2_p)\,(n_h - 2)/(n_h - p - 2)$, so predictions pay for their tuning when $n_L > 4 + 2p/R^2_p$. At $p = 1$ this is round 4's rule. Derive it or correct it.

**Experiments.** Script `code/scripts/round5_ppi_e3_twolevel.py` for the real data and `round5_ppi_e3_sim.py` for the simulation.

- **Simulation.** A two-level generator with an outcome level and cluster-specific levels. $G \in \{15, 24\}$, $n_L \in \{6, 8, 12, G\}$, $m \in \{3, 5, 20, 100, \text{all}\}$, $M = 1000$, between-cluster share 0.3, level $\mu \in \{0, 3, 10\}$, predictors as in E2. Both targets. 2,000 replicates per cell.
- **The regime comparison, rerun.** The round-4 budgets 2,400, 4,800 and 9,600 and cost ratios 10, 100 and 1,000 on all six tasks. Six estimators on every draw, which are the classical and the PPI estimator in the round-4 form, in form P and in form C. Arms as in E2.
- **The masking grid, rerun.** $n_L \in \{4, 6, 8, 12, 16\}$ and $m \in \{25, 50, 100, 200, 500, \text{all}\}$ with the same six estimators, and the variance components on the scale of each form, with $m^\star$ and $m^\star_{\text{PP}}$ at cost ratios 10, 100 and 1,000.
- **Regime B at small $m$, rerun.** The $m$ grid of E2 with forms P and C, to say from how many labelled units per cluster each form's interval covers.
- **The unit-weighted rows.** The spot-weighted estimands at every unit labelled, with the estimator of item 4.

Fan out by task, six units, plus one for the simulation.

**Acceptance.**

1. With $\gamma = 0$ and $\lambda^{w} = \lambda^{c}$ equal to round 4's coefficient, form P reproduces the round-4 regime A rows of `q4_main_table.csv` at $m <$ all, and with $n_L = G$ and $\gamma = 0$ the regime B rows, at the E0 tolerances.
2. With every unit labelled, donor-weighted, both forms reproduce the `final_design` rows of `q4_main_table.csv` at the E0 tolerances.
3. Under form C the constant and the donor-constant predictor leave every estimate unchanged to $10^{-10}$ on every draw. This is an identity, and it is the check that form C is coded as written.
4. Under form P the constant predictor's width ratio against the form P classical estimator is 0.97 to 1.05 at $m \ge 20$ in regime B on every task. The expected value is 1 plus a small tuning cost. The donor-constant predictor has no band under form P, since with a pooled intercept it can remove real differences between clusters' levels, and its ratio is reported as a measure of them.

**Predictions.**

1. E3.1. The permuted predictor's width ratio against the form C classical estimator is 0.97 to 1.05 in regime B at $m \ge 10$ on every task and both estimands. On the unit-weighted rows its variance ratio is 0.95 to 1.15 at $n_L \ge 8$, where round 4 had 0.09 to 0.48 on the tissue tasks (`results/round4/ppi/Q5a/q5a_spot_weighted_permuted.csv`).
2. E3.2. The real predictors' width ratio against the form C classical estimator in regime B agrees with E2's ratio to the donor-constant predictor within 0.05 on every task.
3. E3.3. The form C classical estimator is narrower than the form P classical estimator at every $m \ge 10$ on the tissue tasks, by 3 to 20%, and its interval covers 0.87 to 0.92 from $m = 5$.
4. E3.4. Regime B stays narrower than regime A in at least 200 of the 232 comparisons at a cost ratio of 10 under the two-level estimator in either form.
5. E3.5. The classical optimal units per cluster at a cost ratio of 100 falls on every task from round 4's 121 on kidney cancer, 236 on Indiana, 172 on lung and 379 on census by state (`results/round4/ppi/Q2_theory/q2_report_numbers.csv`). The fall is by about $\sqrt{1 - L}$, with $L$ the level share of E2 at the median gene, and on census by state the new value is below 100. $m^\star_{\text{PP}}/m^\star$ equals $\sqrt{(1 - R^2_w)/(1 - R^2_c)}$ within 15% on every task and predictor where both are defined.

**Outputs.** `results/round5/ppi/E3_twolevel/e3_sim.csv`, `e3_regime_comparison.csv`, `e3_masking_grid.csv`, `e3_regimeB_small_m.csv`, `e3_components.csv`, `e3_unit_weighted.csv`, `e3_superseded_round4_numbers.csv` (every round-4 number that the regression form changes, old and new side by side, with both paths), `e3_acceptance.csv`, `e3_report_numbers.csv`, figures, and section 2 of the theory document.

#### E4. Which clusters to label (three days; gate)

**Why.** The break-even counts of round 4 run from 6 to 43 labelled clusters across tasks and predictors, so with 4 to 12 clusters the tuning cost eats much of the gain. If the labelled clusters are balanced on $\bar f_g$, so that their mean of $\bar f_g$ equals $\bar F$, the term $\lambda(\bar F - \bar f_L)$ is zero for every $\lambda$ and the classical mean of the labelled clusters already has the reduced variance. Nothing is tuned.

**Designs.** All are randomised, since a design-based interval needs a known random design. Nothing computed from a label enters any of them.

- D0. Simple random sampling, as round 4.
- D1. Two per stratum. Sort the clusters by the first balance variable, cut them into $n_L/2$ strata of nearly equal size, and draw two per stratum.
- D2. Rejective sampling. Draw simple random samples and keep the first whose Mahalanobis distance between the labelled mean and the population mean of the balance variables is below a threshold set so that a fraction $p_a$ of samples is accepted, $p_a \in \{0.1, 0.01\}$.

**Balance variables.** (i) The estimand's own $\bar f_g$, which is one variable per gene and is the case of a study with one outcome. (ii) The first $k \in \{1, 2, 3\}$ principal components of the $G$ by genes matrix of $\bar f_g$, which gives one design for all genes. (iii) The first $k$ principal components of the clusters' mean embeddings from the cluster table, which uses no head at all. (iv) The permuted predictor's $\bar f_g$, as the control.

**Estimators and intervals.** The classical mean and the round-4 final design estimator. For D0 and D2 the interval is `textbook_t|fpc|lin`. Fuller (2009) is the reference for using the regression estimator's ordinary variance after rejective sampling. For D1 the stratified variance with two per stratum and $n_L/2$ degrees of freedom.

**Experiments.** `code/scripts/round5_ppi_e4_sim.py` reuses E1's generator at $G \in \{15, 24, 51\}$, $n_L \in \{4, 6, 8, 12\}$, the $R^2$ grid, $\kappa = 0$ and the normal and skewed laws. `round5_ppi_e4_selection.py` runs the masking on all six tasks for $\theta_3$ and $\theta_2$, donor-weighted, every unit labelled, design target, $n_L \in \{4, 6, 8, 12\}$, 200 accepted draws, the three encoders and the permuted control. Fan out by task, six units, plus one for the simulation.

**Acceptance.**

1. D2 with the threshold at infinity is D0 and reproduces the matching rows of `q4a_table61.csv` at the E0 tolerances.
2. Balancing on the permuted predictor leaves the classical estimator's empirical variance at 0.93 to 1.07 of its value under D0, taking the median over genes. The expected value is 1, and the band is the Monte Carlo error of a variance ratio from 200 draws after the median over 50 genes.

**Predictions.**

1. E4.1. In the simulation, the classical estimator under D2 with $p_a = 0.01$ on $\bar f_g$ has a variance within 0.05 of $1 - R^2$ times its variance under D0, at every $n_L$ from 4 to 12.
2. E4.2. On the real tasks at $n_L = 8$ with balance on the estimand's own $\bar f_g$, the same ratio is 0.25 to 0.40 on lung, 0.55 to 0.70 for `uni_v2` on kidney cancer and 0.28 to 0.40 on census by state, against 0.43 to 0.54, 0.84 and 0.43 for the tuned estimator under D0 (`q4a_table61.csv`).
3. E4.3. With balance on two principal components of the predictions, the median-gene ratio recovers at least half of that gain on lung and less than a third on kidney cancer.
4. E4.4. Under D2 the classical estimator's interval from the simple-random-sampling formula over-covers, at 0.93 or above, and the final design estimator's interval covers within 0.02 of its coverage under D0. Under D1 the stratified interval covers 0.88 to 0.92.
5. E4.5. Balance on the mean embeddings leaves the ratio at 0.9 or above on the kidney tasks.

**Outputs.** `results/round5/ppi/E4_selection/e4_sim.csv`, `e4_selection_grid.csv`, `e4_acceptance.csv`, `e4_report_numbers.csv`, `fig_e4_variance_by_design.png`. Report E3 and E4 together as `docs/round5_ppi_E4_report.md`, tag `round5-ppi-E4`, and stop.

#### E5. The closing report (two days; gate, end of track)

**The estimator, defined once.** `docs/round5_ppi_estimator_definition.md`, the paper's estimator as it stands after E3 and the decision memo at the E4 gate, which says which within-cluster form is the paper's, in the paper's notation, with its simulated behaviour quoted beside each choice. The round-4 definition stays as it is.

**The joint design table, rebuilt.** `results/round5/ppi/E5_joint/e5_joint_design.csv`, one row per task and $m \in \{5, 10, 15, 20, 25, 50, 100\}$ with regime B's width against the classical estimator of the chosen form and its coverage. If the prediction-set track's `results/round5/conformal/W3_real/w3_map_by_task.csv` is on `main` when E5 starts, read it there, record the commit, and add the narrowest valid prediction set at $o = m$ with its coverage and width for each number of calibration clusters that file carries. If it is not, write the inference columns only and mark the others pending.

`docs/round5_ppi_final_report.md` in the format of section 8, covering E1 to E5, the full predictions-against-outcomes table, an "Escalations" section, a section listing every round-4 statement that this round changes with the old and new values, and a closing page titled "What the round-5 inference track established", at most one page, every sentence naming its file. Run the numeric-claim sweep. Tag `round5-ppi-final`. Then stop.

**Time.** About fifteen working days with the gates.

## 3. Predictions, to be scored at each gate

The twenty predictions are the oversight chat's and are copied from section 2.1 above without change. Each is scored in the report of its gate as held, partly held, refuted or not tested.

| prediction | stage | gate | score |
|---|---|---|---|
| E1.1 | E1 | E2 | partly held, see `docs/round5_ppi_E2_report.md` section 5 |
| E1.2 | E1 | E2 | partly held, see `docs/round5_ppi_E2_report.md` section 5 |
| E1.3 | E1 | E2 | partly held, see `docs/round5_ppi_E2_report.md` section 5 |
| E1.4 | E1 | E2 | partly held, see `docs/round5_ppi_E2_report.md` section 5 |
| E1.5 | E1 | E2 | refuted in its second half, see `docs/round5_ppi_E2_report.md` section 5 |
| E2.1 | E2 | E2 | held for $\theta_3$, refuted for $\theta_2$, see `docs/round5_ppi_E2_report.md` section 5 |
| E2.2 | E2 | E2 | partly held, see `docs/round5_ppi_E2_report.md` section 5 |
| E2.3 | E2 | E2 | held in substance, see `docs/round5_ppi_E2_report.md` section 5 |
| E2.4 | E2 | E2 | partly held, see `docs/round5_ppi_E2_report.md` section 5 |
| E2.5 | E2 | E2 | held for $\theta_3$, refuted for $\theta_2$, see `docs/round5_ppi_E2_report.md` section 5 |
| E3.1 | E3 | E4 | held (`docs/round5_ppi_E4_report.md` section 5) |
| E3.2 | E3 | E4 | partly held (`docs/round5_ppi_E4_report.md` section 5) |
| E3.3 | E3 | E4 | held for theta3, not applicable to theta2 (rescored by `docs/decisions/round5_ppi_E4_decisions.md` section 2; the report had partly held) |
| E3.4 | E3 | E4 | held (`docs/round5_ppi_E4_report.md` section 5) |
| E3.5 | E3 | E4 | refuted (`docs/round5_ppi_E4_report.md` section 5) |
| E4.1 | E4 | E4 | partly held (`docs/round5_ppi_E4_report.md` section 5) |
| E4.2 | E4 | E4 | partly held (`docs/round5_ppi_E4_report.md` section 5) |
| E4.3 | E4 | E4 | partly held (`docs/round5_ppi_E4_report.md` section 5) |
| E4.4 | E4 | E4 | D2 over-coverage refuted, other parts partly held (`docs/round5_ppi_E4_report.md` section 5) |
| E4.5 | E4 | E4 | partly held (`docs/round5_ppi_E4_report.md` section 5) |

## 4. Parametrisations fixed before the runs that use them

1. The skewed and heavy laws of E1 are standardised log-normals, $(e^{\sigma Z} - e^{\sigma^2/2})/\sqrt{(e^{\sigma^2} - 1)e^{\sigma^2}}$ with $Z$ standard normal, and both $p_g$ and $\xi_g$ are drawn from the same law. The shapes were set on 7 October 2026, before any log-normal simulation job was submitted, by the diagnostic unit (`round5_ppi_e1_diag.py --moments`, Slurm job 4199035, `results/round5/ppi/unit_job_ledgers/e1_diag_jobs.csv`). The target is the median over the 50 CCRCC genes of $|\text{skewness}|$ of the 24 donor contributions $\bar z_g$ for $\theta_3$, donor-weighted, which is 1.758, and its 90th percentile, 2.929. $\sigma$ is the value at which the median over simulated populations of 24 (their number is in the `rule` field of the JSON file) of the sample $|\text{skewness}|$ of $e^{\sigma Z}$ equals the target, found by bisection. The skewed law has $\sigma = 0.94096$ and the heavy law $\sigma = 1.93948$ (`results/round5/ppi/E1_interval/e1_law_shapes.json`). The heavy law's population skewness is about 292, because the sample skewness of 24 values cannot exceed $(n-2)/\sqrt{n-1}$ with $n = 24$ and a sample median of 2.9 needs a very long tail. At intermediate $R^2$ the contributions $\bar z_g = \lambda^\star p_g + \sigma_\xi \xi_g$ are sums of two independent skewed variables and are less skewed than the target. The normal-law grid was run before the shapes were known, which the plan allowed because it does not use them.
2. Seeds are `zlib.crc32` of a string naming the stage, the cell and the draw. Round-4 seed strings are kept wherever a round-4 row is reproduced.

## 5. Points in the brief that look wrong or need a reading

These are listed and not acted on. Each is repeated in the E2 report.

1. Section 2.3 says that for $\theta_2$ and $\theta_3$ donor-weighted the weights sum to zero within every cluster. On ACS $\theta_2$ is the mean of log income, with $w = 1$, so the statement holds on the tissue tasks only. The same applies to E3 form P, where $\bar a_g$ is zero on the tissue tasks and one for ACS $\theta_2$. E2 part 1 already skips the constant controls where $w = 1$, so nothing in E1 or E2 changes.
2. In the E2 simulation at outcome level $\mu = 0$ the constant predictor gives every unit the task-wide mean of the predictor, which is close to zero. Its contribution $f = c\,w$ is then close to zero and the regime B coefficient is a ratio of two small numbers, clipped to $[0, 1]$. Acceptance check 3 and prediction E2.4 at $\mu = 0$ will be read with the coefficient's unclipped values reported beside them.
3. The fan-out paragraph of section 4 asks the lead to write each sub-agent's own frame id into its brief. A sub-agent's frame id exists only once it has been started. The lead therefore starts each sub-agent with a brief that tells it to write nothing until it receives its frame id, sends the id in a message immediately after the start, and checks every returned stamp against that id before merging.
4. Section 5 says the local clone had been brought up to date with `main`. It was on `round4-ppi` at `8cca44f`, which is 48 commits behind `origin/main` and contained in it. This has no effect, because `round5-ppi` was created from `origin/main`.
5. In E1 at $R^2 = 0$ the outcome contributions are $\bar z_g = \xi_g$ and do not involve $\lambda^\star$, so the two $\lambda^\star$ cells at $R^2 = 0$ are the same experiment. Both are run and reported, and their agreement is a check.
6. The brief requires the Longleaf code clone to move only by fast-forward from the pushed branch, and Nicolas's standing instruction of 1 October is not to push between gates. Nicolas resolved this on 7 October (extension 1 below).
7. The numeric statements in sections 2.1, 2.4 and E1 (for example the permuted predictor's within-cluster $R^2$ of 0.98 for the ACS slope, and the round-4 design-arm coverage medians of 0.896 to 0.900) are checked against their files in E0 and the result is reported in the E2 report.

## 6. Extensions agreed with Nicolas in chat

1. (7 October 2026) No pushes between gates. New `round5_ppi_*.py` scripts reach Longleaf by upload into the job's own directory. Each job's `PROVENANCE.txt` records the md5 of every uploaded script, the local commit that holds it, and the Longleaf clone's HEAD, which stays at its last fast-forward until the gate push. Round-3 and round-4 modules are imported from the Longleaf clone unmodified. The branch, the tag and the pull request are pushed together at each gate.

2. (7 October 2026) One pull request per gate, from `round5-ppi` into `main`, opened when the branch and the gate's tag are pushed. Nicolas merges it after he and the oversight chat have reviewed the gate report. The session never merges. A rejected gate is fixed with new commits on the same open pull request.

3. (8 October 2026) The numeric-claim sweep runs locally in the clone on Nicolas's Mac, at his request, because it measures the documents in place. It is the only local run. It used `code/scripts/verify_numeric_claims.py` unmodified, Python 3.11.15 and pandas 2.3.3, over `README.md` and `docs/round5_ppi_*.md`.

Extension 1 is replaced by section 4 of the E2 decision memo, transcribed in section 7.3 below. Extensions 2 and 3 stand, with the change in section 7.3 that the track sweeps only its own documents.

4. (8 October 2026) Nicolas said local compute is preferred where it is genuinely faster, until he says stop. He chose on the same day that the real-task units stay on Longleaf, because their prediction parquets exist only there and no data is copied to the Mac. So the simulations of interval 2 run locally and every unit that reads task data runs on Longleaf. Section 7.4 gives the rules for local runs.

## 7. Interval 2, from the E2 decision memo

The memo is `docs/decisions/round5_ppi_E2_decisions.md` (md5 `8a2117e26a5d69877855240ba06501d2`), committed unchanged. Where this section and the memo differ, the memo holds. Interval 2 runs E3a, E3 and E4 and ends at the E4 gate.

### 7.1 The gate rule and the people

No stage after a gate starts, is set up, staged or piloted until the oversight chat has reviewed the gate report and replied. Inside the interval there are no interim reports and no interim stops. Anything that would have halted work is handled under the decision boundaries of brief section 9, recorded in the "Escalations" section of the E4 report, and work continues. The exceptions are the stop-and-report cases of brief section 9 and of the memo (a derivation of E3a or E3 that does not close, E3 acceptance check 3 or 4 failing). Contact with anyone outside the project is never the session's decision. Every sub-agent brief of interval 2 carries the sentence "Sub-agents report to the lead and to no one else, Nicolas included."

### 7.2 What the memo accepts and answers

The E2 report is accepted. Escalations 1 and 2 are accepted as recorded, escalation 3 is answered by section 7.3, escalation 4 by the stratified draw of section 7.6, escalation 5 by the provenance index of section 7.3 item 6. The heavy-law outlier of report section 6.1 is not pursued. Nicolas merges pull request #15. Nothing is pushed to `round5-ppi` until that merge has happened.

The readings of memo section 3 stand as the paper's readings. The constant predictor is the primary control from now on, and the permuted predictor is reported beside it.

### 7.3 Code delivery, pushes and shared files (memo section 4)

1. GitHub sees one push per gate, the branch and the tag together, with one pull request into `main`. No push before pull request #15 is merged. If it is not merged when the E4 report is ready, the session commits and tags locally and waits.
2. Commits reach Longleaf as a git bundle, `git bundle create <file> <last delivered commit>..round5-ppi`, copied as job input. A short Slurm job in `/work/users/w/e/weiyang/hest_code/round5-ppi/` runs `git bundle verify`, `git fetch <file> round5-ppi` and `git merge --ff-only FETCH_HEAD`, and prints the new HEAD. A failed fast-forward changes nothing and is recorded. The clone never fetches from GitHub, is never rebased or reset, and never has another branch checked out.
3. The same job writes `git -C <clone> archive <commit> code | tar -x -C /work/users/w/e/weiyang/hest_code/round5-ppi_snapshots/<full hash>/` and removes write permission from it. Every job puts that snapshot's `code/scripts` on `PYTHONPATH`, runs its scripts from there and runs from its own output directory. No script is copied loose into a job directory. Committed data files are read from the clone. Nothing is edited on Longleaf.
4. Each delivery is one row of `results/round5/ppi/code_deliveries.csv`: date, Slurm job id, HEAD before and after, bundle md5, commits carried, snapshot path.
5. Every job records its snapshot's commit and the md5 of each script it executed. Commits of documents or results only need not be delivered.
6. Before the E4 gate push, `results/round5/ppi/provenance_index.csv` gets one row per job and script (job id, unit, script path, md5, recorded commit, and the two checks: the commit is an ancestor of the gate tag, and the md5 equals the script's md5 at that commit). It includes rows for every E0 to E2 job, read from the Longleaf `PROVENANCE.txt` files, and the three records naming `8b879bb` listed as failing the second check, with `4f52b0c` and `f75950f` beside them. The report lists every failing row.
7. Results computed on Longleaf come back by the route in use and are committed locally.
8. Only the lead cancels a Slurm job, after checking `squeue -u weiyang` and the ledger. A sub-agent never runs `scancel`.
9. The track's sweep exceptions go in `.verify-exceptions-round5-ppi`, and the sweep runs with `--exceptions` pointing at it, over `docs/round5_ppi_*.md` only. The README is swept by the oversight chat.

The first delivery carries `d82c3f3..` the commit that adds this section and the memo, and makes the first snapshot. No job of interval 2 runs an uploaded script.

### 7.4 Local runs (extension 4)

Local runs are the simulations: E3a's reruns of the E1 normal and skewed grids, `round5_ppi_e3_sim.py` and `round5_ppi_e4_sim.py`. They follow the same discipline as Longleaf jobs. Each runs from a read-only snapshot of a committed commit made with `git archive <commit> code`, outside the clone's tracked tree, in its own output directory, and writes a `PROVENANCE.txt` with the host, the Python, numpy, scipy and pandas versions, the snapshot commit, the md5 of every script and input, and the command line. Each local run is one row of `results/round5/ppi/r5ppi_local_runs.csv`. Any table holds rows of one platform only. Where an acceptance check compares a local rerun with a Longleaf row (E3a's reproduction of the E1 grid), the comparison is made at the E0 tolerances and the largest difference is reported. If it fails because of the platform, that part reruns on Longleaf and the report says so. Sub-agents may run local simulations in parallel, at most eight worker processes at a time across the session.

### 7.5 E3a, the cross-fitting term (first in the interval)

1. Theory section 2.0 before any E3a job. Derive the design variance of $\hat\theta = \bar z_L - c(\bar f_L - \bar F) - \tfrac{d}{2}(\bar f_A - \bar f_B)$, keeping the dependence between the halves' coefficients and means, say how much of the last term the current estimate misses, and derive or correct the candidate $\widehat{\text{Var}}_{\text{xf}} = (1 - n_L/G)\,s_e^2/n_L + (n_L/G)\,d^2 s_f^2/n_L$. If the derivation does not close, stop and report.
2. Add `textbook_t|fpc|lin|xf` to `round5_ppi_estimator.py`.
3. Locally, rerun E1's normal and skewed grids at $G \in \{15, 24, 51\}$ with both intervals on the same seeds.
4. On Longleaf, rerun the masking with every unit labelled, $n_L \in \{6, 8, 12, 16\}$, $\theta_3$ and $\theta_2$, donor-weighted, design target, rules `none` and `c_crossfit_design`, both intervals, on all six tasks, one unit per task in parallel. A cell with $n_L$ above the task's valid donors is skipped and recorded (lung $\theta_2$ has 9).
5. Acceptance: with $d = 0$ and under rule `none` the two intervals are identical; the `textbook_t|fpc|lin` rows reproduce E1 and `q4a_table61.csv`.
6. Predictions E3a.1 to E3a.3, scored at the E4 gate. If the acceptance passes, E3 and E4 report the corrected interval as primary and the uncorrected beside it. Otherwise they use `textbook_t|fpc|lin` and the failure is an escalation.

### 7.6 E3, as the brief says with the memo's changes

1. Theory section 2, items 1 to 5 of brief E3, plus the stratified form C for $\theta_2$ in item 1, before any E3 job.
2. Stratified draws for $\theta_2$. Every $\theta_2$ row with $m <$ all, in regime B and regime A, draws inside each cluster by group (neoplastic-dominant and stromal-dominant spots), $\lfloor m/2 \rfloor$ and $\lceil m/2 \rceil$ with the larger share to the rarer group, each capped at the group's size and any shortfall given to the other group. A group smaller than its share is labelled completely and has no sampling variance. The smallest $m$ for $\theta_2$ is 4. Units in neither group are not labelled for $\theta_2$. The estimate is the difference of the two groups' labelled means of $y - \lambda^w_g \hat y$ plus $\lambda^w_g$ times the difference of their all-unit means of $\hat y$, with variance $\sum_h (1 - m_h/M_h)\,s_h^2/m_h$. The $\theta_2$ rows of E2 are rerun under this draw. The simple random rows of E2 stay as the record.
3. The constant predictor is the primary control, the permuted predictor beside it.
4. `e3_regime_comparison.csv` adds the ratio of regime B to regime A width with the form C classical estimator in both, beside the same ratio with the two-level estimator.
5. The masking grid carries the interval chosen by E3a.
6. Fan-out: six task units on Longleaf in parallel, one local simulation unit. Acceptance as in the brief, with check 3 covering the stratified $\theta_2$ form.
7. Predictions E3.1 to E3.5 of the brief and E3.6, E3.7 of the memo.

### 7.7 E4, as the brief says

E4 uses the interval chosen by E3a. Six task units on Longleaf in parallel and one local simulation unit. Its code can be written while E3's units run, and its units are submitted once E3's results are merged. As run, the E4 task units were submitted after five of the six E3 task units had been merged and while lung's E3 unit was still running, since no E4 input depends on E3's lung rows. The E3 and E4 merges ran locally on committed result files. The E4 report `docs/round5_ppi_E4_report.md` covers E3a, E3 and E4 in the format of brief section 8, and adds the delivery ledger, the two checks of section 7.3 item 6, the E3a derivation and results, the stratified $\theta_2$ results, and `e3_superseded_round4_numbers.csv` including round 4's regime B and regime A $\theta_2$ rows with $m <$ all. Then the sweep of section 7.3 item 9, tag `round5-ppi-E4`, push and pull request once #15 is merged, and stop.

### 7.8 New predictions

| prediction | stage | gate | score |
|---|---|---|---|
| E3a.1 | E3a | E4 | held (`docs/round5_ppi_E4_report.md` section 5) |
| E3a.2 | E3a | E4 | held (`docs/round5_ppi_E4_report.md` section 5) |
| E3a.3 | E3a | E4 | held for theta3 (`docs/round5_ppi_E4_report.md` section 5) |
| E3.6 | E3 | E4 | held (`docs/round5_ppi_E4_report.md` section 5) |
| E3.7 | E3 | E4 | partly held (`docs/round5_ppi_E4_report.md` section 5) |

## 8. Interval 3, from the E4 decision memo

The memo is `docs/decisions/round5_ppi_E4_decisions.md` (md5 `a5f008f6d107c323b5089da5e6ebba55`), committed unchanged together with this section. Where this section and the memo differ, the memo holds. Interval 3 runs E4b and E5 and ends at the E5 gate, which is the track's last.

### 8.1 The gate rule

As in section 7.1. Inside the interval there are no interim reports and no interim stops. Anything that would have halted work is handled under the decision boundaries of brief section 9 and recorded in the "Escalations" section of the final report, and work continues. The exception is the stop-and-report case of the memo, a derivation of E4b that does not close. Contact with anyone outside the project is never the session's decision. Every sub-agent brief carries the sentence "Sub-agents report to the lead and to no one else, Nicolas included."

### 8.2 What the memo accepts and corrects

The E4 report is accepted. E3.3 is rescored as held for $\theta_3$ and not applicable to $\theta_2$, because the 144 cells in the band are exactly the $\theta_3$ cells and the two classical forms give the same width for the stratified $\theta_2$. The regime B minimum of 0.500 is on census by state at one labelled unit per state, not on census by area. E4 acceptance check 2's band was the oversight chat's error and is redone in E4b. The three records naming `8b879bb` were the oversight chat's misreading, and the provenance index stands. The memo adds two findings that the final report carries. The classical interval under D2 does not see the variance reduction, because the simple-random-sampling formula uses the spread of $\bar z_g$, which balance does not change. E3.5's second clause compared the allocation formula with a fitted curve that cannot express a between-cluster gain that is zero below $n_L = 6$. Pull requests #17 and #18 are merged (checked on 9 October), so the push at the E5 gate is allowed.

### 8.3 What stays in force, and four additions

Sections 7.3 (code delivery by bundle and snapshot, pushes, shared files, provenance) and 7.4 (local runs) stay in force. The additions are these.

1. **Frame ids.** The lead sends each sub-agent its own frame id as soon as it has started and before it writes anything, writes it into the unit's record, and compares the id in every returned stamp with the assigned one before merging that unit. A stamp with the wrong id is fixed before the merge. `code/scripts/round5_ppi_e4_stamp_check.py` is extended to the E4b units and reports zero mismatches before the merge.
2. **Shared files.** The two `.gitignore` entries of pull request #17 are accepted. Any further change outside the track's areas is an escalation in the final report.
3. **The tag.** `round5-ppi-final` goes on the last commit of the push, after every wording correction.
4. **Briefs.** Before dispatch the lead checks each brief against the unit it is for (stage, task, script, output directory) and records the check in the unit ledger.

### 8.4 E4b, an interval that uses the balance (first in the interval)

1. **Theory section 3** of `docs/round5_ppi_theory.md`, before any E4b job. D2 with $k$ balance variables and Mahalanobis acceptance. Decompose $\bar z_L - \bar Z = (\bar e_L - \bar E) + B^\top(\bar x_L - \bar X)$ with $B$ the population least-squares coefficient over the $G$ clusters. Derive the variance of the classical mean under rejective acceptance with the finite-population factor, using the scaling $v_a = P(\chi^2_{k+2} \le q_a)/P(\chi^2_k \le q_a)$, and the estimate $\widehat{\text{Var}}_{\text{rej}} = (1 - n_L/G)(s^2_{\text{res}} + v_a\,\hat b^\top S_x \hat b)/n_L$ with $s^2_{\text{res}}$ on divisor $n_L - k - 1$ and reference $t_{n_L - k - 1}$. State the conditions, including the number of distinct samples the design can accept. Confirm Morgan and Rubin (2012) Theorem 3.1 and Fuller (2009) as references before relying on them, from the papers themselves where they can be fetched, and say which parts were confirmed and how. If the derivation does not close, stop and report.
2. **Code**, committed and delivered by bundle before any job. `rej_t` in `round5_ppi_balance.py`, D2 only, needing $n_L - k - 1 \ge 2$, with skipped cells listed. A cluster-level null control `perm_cluster`, the `resnet50` arm's own $\bar f_g$ permuted across clusters with a crc32 seed per gene, beside the unit-level `perm`. In the simulation and the real-task runs, a draw with no accepted candidate draws further candidates until one is accepted, never falls back to its last candidate, and records the number of candidates used. Unit tests: the point estimate of `rej_t` equals the classical mean; $v_a$ against a Monte Carlo of the $\chi^2_k$ truncation; `rej_t` on a synthetic population against the empirical variance under D2.
3. **Runs.** E4's real-task masking on all six tasks with 2,000 accepted draws per cell, the first 200 on E4's seeds. Designs D0, D1 and D2 at $p_a \in \{0.1, 0.01\}$. Balance variables `own`, `pcF2`, `pcE2`, `perm`, `perm_cluster`. $\theta_3$ and $\theta_2$, donor-weighted, every unit labelled, design target, $n_L \in \{4, 6, 8, 12\}$, arms `hoptimus0`, `uni_v2`, `resnet50` and `permuted` (on census, `package` and `permuted`, and `pcE2` is not formed, as in E4). Intervals `textbook_t|fpc|lin` for the classical mean, `textbook_t|fpc|lin|xf` for the tuned estimator, `rej_t` under D2 and `strat_t` under D1. Beside every D2 cell, its support $p_a\binom{G}{n_L}$ (with $G$ the valid clusters of the estimand), the standard deviation over clusters of the inclusion frequency, its Spearman correlation with $|\bar f_g - \bar F|$ for the balance variable, and the share of genes with standardised bias above 3. E4's simulation is rerun with `rej_t` added. The real-task units keep per-draw, per-gene variance and estimate arrays (or per-draw per-gene summaries sufficient for the bootstrap) so that acceptance 3 can be computed.
4. **Fan-out.** Six task units on Longleaf in parallel, one local simulation unit under section 7.4, at most eight local worker processes. Each sub-agent is given its own frame id (8.3 item 1) and its brief is checked (8.3 item 4).
5. **Acceptance.** (1) The first 200 draws of every D0 and D1 cell reproduce E4's rows at the E0 tolerances; D2's rows are set beside E4's without a tolerance, with the change in threshold reported. (2) `rej_t`'s point estimate equals the classical estimate on every draw. (3) Check 2 restated. A bootstrap over draws, resampling the 2,000 draws of each design with replacement jointly for all genes, 500 times, gives a standard error for the ratio of median variances under D2 and D0, and with `perm_cluster` the ratio is within three standard errors of 1 in every cell with support at least 1,000. A failure is an escalation, and work continues.
6. **Predictions** E4b.1 to E4b.4 as the memo states them, scored in the final report.

### 8.5 E5, as the brief says with the memo's changes

1. **`docs/round5_ppi_estimator_definition.md`.** Form C within clusters, the between coefficient under `c_crossfit_design`, the interval `textbook_t|fpc|lin|xf`, regime B's reference with $\sum_g (m_g - 2)$ degrees of freedom for $\theta_3$ and $\sum_{g,h}(m_{h,g} - 1)$ for $\theta_2$, and the stratified draw for $\theta_2$ over the donors where both groups are present. Where E4's code drew from all donors and dropped draws, the share dropped per cell is reported, without a rerun. D2 with `rej_t` enters as the design option, with its support condition, only if E4b's acceptance passes and E4b.1's coverage clause holds; otherwise the document says that balance reduces the variance and that no interval run here captures it. The document also says where the superpopulation-target interval covers below 0.85 in E3's simulation. Simulated behaviour is quoted beside each choice.
2. **Allocation.** Theory section 2.4's result is stated for coefficients fixed in advance. `results/round5/ppi/E5_joint/e5_allocation.csv`, computed locally from committed files, one row per task, encoder and $n_L$, for form C and $\theta_3$, with $1 - R^2_w$ and $1 - R^2_c$ from `e3_components.csv`, the measured between ratio $\rho_c(n_L)$ (median variance of `C_ppi` over `C_classical` at every unit labelled, `e3_masking_grid.csv`), the classical $m^\star$ at $c_d/c_s = 100$ from the components, $m^\star_{\text{PP}}(n_L) = m^\star\sqrt{(1 - R^2_w)/\rho_c(n_L)}$, and the fitted values of `e3_components_fitted.csv` beside them. This gives census by state its form C value.
3. **The joint design table** `results/round5/ppi/E5_joint/e5_joint_design.csv` uses form C, one row per task and $m \in \{5, 10, 15, 20, 25, 50, 100\}$, with regime B's width against the form C classical estimator and its coverage. Pull request #18 is merged, so `results/round5/conformal/W3_real/merged/w3_map_by_task.csv` is read from `origin/main` after `git fetch`, by `git show`, without checking anything out, and the commit is recorded. The narrowest valid prediction set at $o = m$ is added with its coverage and width for each number of calibration clusters that file carries.
4. **Regime B coverage statements** only at budgets where every cluster gets at least the form's smallest number of labelled units (3 for $\theta_3$ intervals, 4 for the stratified $\theta_2$). Other cells are marked.
5. **`docs/round5_ppi_final_report.md`** in the format of brief section 8, covering E1 to E5 and E4b, the full predictions-against-outcomes table with E4b.1 to E4b.4 scored, an "Escalations" section, the corrections of memo section 2, a section listing every round-4 statement this round changes with old and new values, and the closing page "What the round-5 inference track established", at most one page, every sentence naming its file.
6. **The sweep** over `docs/round5_ppi_*.md` with `.verify-exceptions-round5-ppi`. An exception stating a derived value is recomputed by a committed script before it is declared. The README is not swept.
7. **The push.** Tag `round5-ppi-final` on the last commit, push the branch and tag once, open one pull request into `main`, and stop.

### 8.6 New predictions

| prediction | stage | gate | score |
|---|---|---|---|
| E4b.1 | E4b | E5 | held (`e4b_prediction_scores.csv`) |
| E4b.2 | E4b | E5 | held (`e4b_prediction_scores.csv`) |
| E4b.3 | E4b | E5 | held (`e4b_prediction_scores.csv`) |
| E4b.4 | E4b | E5 | held (`e4b_prediction_scores.csv`) |

