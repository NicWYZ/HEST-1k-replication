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
| E1.1 | E1 | E2 | not yet scored |
| E1.2 | E1 | E2 | not yet scored |
| E1.3 | E1 | E2 | not yet scored |
| E1.4 | E1 | E2 | not yet scored |
| E1.5 | E1 | E2 | not yet scored |
| E2.1 | E2 | E2 | not yet scored |
| E2.2 | E2 | E2 | not yet scored |
| E2.3 | E2 | E2 | not yet scored |
| E2.4 | E2 | E2 | not yet scored |
| E2.5 | E2 | E2 | not yet scored |
| E3.1 | E3 | E4 | not yet scored |
| E3.2 | E3 | E4 | not yet scored |
| E3.3 | E3 | E4 | not yet scored |
| E3.4 | E3 | E4 | not yet scored |
| E3.5 | E3 | E4 | not yet scored |
| E4.1 | E4 | E4 | not yet scored |
| E4.2 | E4 | E4 | not yet scored |
| E4.3 | E4 | E4 | not yet scored |
| E4.4 | E4 | E4 | not yet scored |
| E4.5 | E4 | E4 | not yet scored |

## 4. Parametrisations fixed before the runs that use them

1. The skewed and heavy laws of E1 are standardised log-normals. Their shape parameters are set from `e1_contribution_moments.csv` by the rule of section 2.1, E1, and are written here, with the commit that records them, before any E1 simulation job is submitted.
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

No local run has been requested. Nothing runs on Nicolas's Mac.
