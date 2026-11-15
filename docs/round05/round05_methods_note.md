# Round 5, methods note

This note holds, word for word, the parts of round 5's working papers that kept documents, scripts or results cite for a definition, a reading or a dead end, and that no kept document states. The round's summary is `docs/round05/README.md`. Each section names the file it was taken from (all present at the tag `record-full-2026-11`) and what it describes. Text quoted here keeps the voice of its source, so "you" is the execution session the instruction was written for and "I" is the author of the memo or handoff.

## 1. The inference track's methods, stated once

From `round5_ppi_track.md` (at tag `record-full-2026-11`), section 2.3, the instruction of 7 October 2026. It describes the estimators, targets, regimes, masking and controls that `docs/round05/tracks/ppi/round5_ppi_plan.md` (sections 2 to 5), the E2, E4 and final reports, `docs/round05/tracks/ppi/round5_ppi_theory.md` and the `code/scripts/round5_ppi_*.py` scripts use. The paper's estimator after the round is `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`.

**Notation.** Cluster $g = 1, \dots, G$ has $M_g$ units, and $N = \sum_g M_g$. Unit $i$ of cluster $g$ has outcome $y_{gi}$ and prediction $\hat y_{gi}$. Every estimand is the mean of a per-unit scalar $z_{gi} = w_{gi}\,y_{gi}$ with label-free weights $w_{gi}$ computed from all units, and its prediction counterpart is $f_{gi} = w_{gi}\,\hat y_{gi}$. For the mean, $w = 1$. For the within-cluster slope $\theta_3$ on a covariate $x$, $w_{gi} = (x_{gi} - \bar x_g)/v_g$ with $\bar x_g$ and $v_g$ the cluster's own mean and variance of $x$. For the group difference $\theta_2$, $w_{gi} = 1/\pi_{g,\text{neo}}$ on neoplastic-dominant spots and $-1/\pi_{g,\text{str}}$ on stromal-dominant spots. On the tissue tasks $x$ is standardised mean nuclear area. On ACS, $\theta_3$ is the slope of log income on standardised age and $\theta_2$ is the mean of log income. Cluster means are $\bar z_g$ and $\bar f_g$, and cluster totals are $Z_g$ and $F_g$.

**Two populations.** Donor-weighted, the average over clusters of the cluster's own value, which is the primary estimand. Spot-weighted, the pooled value over all units. For $\theta_2$ and $\theta_3$ donor-weighted, $\sum_i w_{gi} = 0$ within every cluster.

**Two targets, named on every row.** The design-based target is the value on the fixed set of $G$ clusters in hand, and real-data coverage is always of this target. The superpopulation target is the value in the population the clusters were drawn from, and it can only be checked in simulation.

**Regime A** labels $m$ units on each of $n_L$ clusters and none on the others. **Regime B** labels $m$ units, drawn uniformly without replacement, on every one of the $G$ clusters. Predictions exist on every unit of every cluster in both.

**The final design-target estimator of round 4**, regime A with every unit of a labelled cluster labelled, donor-weighted.

$$
\hat\theta = \frac{c_U}{G}\sum_{g=1}^{G}\bar f_g + \frac{1}{n_L}\sum_{g \in L}\big(\bar z_g - \lambda_g \bar f_g\big), \qquad \widehat{\text{Var}} = \Big(1 - \frac{n_L}{G}\Big)\frac{s_e^2}{n_L}
$$

Here $\lambda_g$ is the cross-fitted coefficient of cluster $g$ under rule `c_crossfit_design`. The labelled clusters are split in two halves, each half's coefficient is the least-squares slope of $\bar z_g$ on $\bar f_g$ over that half, clipped to $[0, 1]$, and it is applied to the other half. $\lambda = 0$ when $n_L < 6$. $c_U$ is the average of $\lambda_g$ over the labelled clusters. $s_e^2$ is the sample variance over labelled clusters of

$$
e_g = \bar z_g - \lambda_g \bar f_g + (\lambda_g - c_U)\,\bar F, \qquad \bar F = \frac{1}{G}\sum_{g=1}^{G}\bar f_g
$$

and the reference is $t_{n_L - 1}$. The last term of $e_g$ is the linearised term added in Q5a. In the tables this interval is `textbook_t|fpc|lin` and the interval without the last term is `textbook_t|fpc`. The full definition, the spot-weighted form and the superpopulation form are in `docs/round04/tracks/ppi/round4_ppi_estimator_definition.md`.

**Regime B as round 4 ran it.** For cluster $g$ the estimate is the mean of $f$ over all its units times $\lambda_g$ plus the labelled units' mean of $z - \lambda_g f$. The coefficient is cross-fitted over two halves of the clusters as the pooled within-cluster slope of $z$ on $f$, clipped to $[0, 1]$. The design variance is $\frac{1}{G^2}\sum_g (1 - m_g/M_g)\,s^2_{r,g}/m_g$ with $s^2_{r,g}$ the labelled units' sample variance of $z - \lambda_g f$, and the reference is $t$ on $\sum_g (m_g - 1)$ degrees of freedom. The code is `regime_b` in `code/scripts/round4_ppi_q3_regimes.py`.

**Validation by masking.** The full data define the truth. Labelled clusters and labelled units are drawn 200 times with crc32 seeds, the interval is computed on each draw, and coverage of the full-data value is recorded. Variance ratios are empirical variances across the draws.

**The controls.** The permuted predictor is the `resnet50` prediction with rows permuted across the whole task, so it carries no information about any unit. This round adds two more. The constant predictor gives every unit the task-wide mean of the `resnet50` prediction for that gene. The donor-constant predictor gives every unit its own cluster's mean of the `resnet50` prediction. All three are label-free. On ACS they are built from the package predictor.

The tasks, from section 3 of the same instruction.

**The tasks.** Kidney cancer (`CCRCC`, 24 donors, Visium, 50 genes) and the same with donors `INT4` and `INT24` merged (`CCRCC_merged`, 23 donors), because the two may be one donor. Indiana kidney (`INDIANA_KIDNEY`, 25 donor units, Visium, 50 genes). Lung (`LUNG_XENIUM`, 15 donors, 343 genes), where disease is not fixed, so donor effects carry disease as well as person. Census income by state (`ACS_STATES`, 51 clusters) and by California PUMA (`ACS_CA_PUMA`, 265 clusters), one outcome. Three encoders on the tissue tasks, `hoptimus0`, `uni_v2` and `resnet50`. The package predictor on ACS.

## 2. The level term, the reading that stage E2 tested

From `round5_ppi_track.md` (at tag `record-full-2026-11`), section 2.4. It is the oversight's reading of the round-4 files that E2 tested (`docs/round05/i01/ppi/round5_ppi_E2_report.md`, section 6.4). It held for the slope $\theta_3$ and not for the group difference $\theta_2$ (summary, finding 2).

This is a reading of the round-4 files, not an established result. E2 tests it before E3 builds on it.

In regime B the classical estimate of a cluster's slope is the labelled units' mean of $z_{gi} = w_{gi}\,y_{gi}$. The outcome is not centred. Write $y_{gi} = \mu_g + \beta_g \tilde x_{gi} + \epsilon_{gi}$ with $\tilde x = x - \bar x_g$, so that $w = \tilde x / v_g$. If $\tilde x$ is symmetric within the cluster and $\epsilon$ is independent of it with variance $\sigma_g^2$, then

$$
\text{Var}(z_{gi}) = \frac{\mu_g^2 + \sigma_g^2}{v_g} + \beta_g^2\Big(\frac{\kappa_{4,g}}{v_g^2} - 1\Big)
$$

with $\kappa_{4,g}$ the fourth central moment of $x$ in the cluster. The term $\mu_g^2 / v_g$ comes from the level of the outcome and has nothing to do with the slope. A constant predictor $\hat y = c$ has $f = c\,w$, and regressing $z$ on $f$ removes exactly that term. So in regime B any predictor with a non-zero mean buys variance, and the round-4 comparator is a classical estimator that a statistician would not use, since the ordinary regression slope centres the outcome.

Four facts in the files agree with this.

- On ACS the permuted predictor has a within-cluster $R^2$ of 0.98 for the slope and 0.00 for the mean, where $w = 1$ and there is no weight to multiply a level (`results/round4/ppi/Q2_theory/q2_cluster_r2.csv`, scale `z`).
- For $\theta_2$ on kidney cancer the permuted predictor's within-cluster $R^2$ is 0.37, the same as `hoptimus0`'s 0.37, and on Indiana it is 0.32 against 0.18 (`q2_cluster_r2.csv`).
- For $\theta_3$ the permuted predictor's regime B width ratio is 0.87 on kidney cancer, 0.88 on Indiana, 0.66 on lung and 0.15 on ACS, against 0.80 to 0.84, 0.83 to 0.84, 0.42 to 0.49 and 0.08 for the real predictors (`q4_main_table.csv`, design target, donor-weighted, unit cost).
- The fitted optimal number of units per cluster at a cost ratio of 100 moves as far with the permuted predictor as with a real one. On kidney cancer it is 121 for the classical estimator, 108 with `hoptimus0` and 111 with the permuted predictor. On lung it is 172, 121 and 96. On census by state it is 379, 89 and 97 (`results/round4/ppi/Q2_theory/q2_report_numbers.csv`, $\theta_3$, donor-weighted).

If the reading holds, three round-4 statements change. Regime B's width against classical overstates what the encoders buy. The optimal number of units per cluster, which rests on the within-cluster variance, is too large for the classical estimator. And the spot-weighted rows that round 4 marked as nuisance rows are the same problem one level up, where the level multiplies the cluster's weight sum. The results with whole clusters labelled, donor-weighted, are not touched, because there the weights sum to zero exactly.

## 3. The prediction-set track's methods, stated once

From `round5_conformal_track.md` (at tag `record-full-2026-11`), section 2.3, the instruction of 7 October 2026. It defines the methods (`hcp`, `ghcp`, `ghcp_noad`, `within_plain`, `within`, `within_full`), the price of validity and "narrowest valid method" used by `docs/round05/tracks/conformal/round5_conf_plan.md`, the W2 and closing reports, and `code/scripts/round5_conf_w2_census.py` and `code/scripts/round5_conf_w2_wrapper.py`, whose docstrings cite this section. The plan's section 4 items 1, 5 and 10 correct or confirm parts of it (the released Std-CP is reported as `released_stdcp`, and the working on `within_full` checks out).

**Split conformal.** Scores $s_1, \dots, s_n$ on a calibration set. The set for a new unit is $\{y : s(y) \le \hat q\}$ with $\hat q$ the $\lceil (n + 1)(1 - \alpha) \rceil$-th smallest calibration score. If the $n + 1$ scores are exchangeable and distinct, coverage is exactly $\lceil (n + 1)(1 - \alpha) \rceil / (n + 1)$ on average, which is at least $1 - \alpha$. A finite $\hat q$ exists only if $n \ge (1 - \alpha)/\alpha$, which is $n \ge 9$ at 90%. The score here is the absolute residual $|y - \hat y|$.

**Hierarchical exchangeability.** Clusters are exchangeable with each other and units are exchangeable within a cluster. The question is coverage for a unit of a new cluster.

**HCP** (Lee, Barber and Willett, arXiv:2306.06342). Each of the $K$ calibration clusters gets total mass $1/(K + 1)$ spread equally over its units, and the test cluster's $1/(K + 1)$ is an atom at $+\infty$. The threshold is the $(1 - \alpha)$ quantile of that distribution. It is valid for any $K$ and finite only when $1/(K + 1) \le \alpha$. It ignores labelled test units, so it is available at every $o$.

**GHCP** (Mallick, Tchetgen Tchetgen, Dobriban and Lee, arXiv:2608.15500). With $o$ observations from the test group, the test group is assigned a size donated at random by a reference group with more than $o$ observations, part of the $o$ observations recentres the score, and the rest calibrate. The primary form here, `ghcp`, has $\eta = 0$ and adaptation on. `ghcp_noad` has adaptation off. Two conventions from round 4 stand. This track's tie convention is the standard one, under which the threshold is the $\lceil (n + 1)(1 - \alpha) \rceil$-th smallest score, and the released code's finiteness is reported beside it. And the paper's pool rule, its equation (8), is primary, with the released code's rule, one group larger, as a secondary variant.

**Inside the test cluster.** Three methods use only the $o$ labelled units, so they do not depend on $K$.

- `within_plain` is split conformal on the $o$ absolute residuals, uncentred. It is finite from $o = 9$ at 90%.
- `within` recentres on the first $\lfloor o/2 \rfloor$ residuals and calibrates on the rest. This is the GHCP paper's Std-CP with the absolute score. It is finite from $o = 17$ at 90%.
- `within_full` is added in this round. It is full conformal prediction with the mean as the fitted model. For a candidate residual $r$ of the test unit, let $c(r)$ be the mean of the $o$ labelled residuals and $r$, let $s_i(r) = |r_i - c(r)|$ and $s(r) = |r - c(r)|$, and keep $r$ when $1 + \#\{i : s_i(r) \ge s(r)\} > \alpha\,(o + 1)$. The oversight chat's working is that each condition $s_i(r) \ge s(r)$ holds on a closed interval with end points $r_i$ and $(2S - (o + 1)\,r_i)/(o - 1)$, where $S$ is the sum of the labelled residuals, so the set is found exactly from $2o$ end points, that it is finite from $o = 9$ at 90%, and that its coverage is $\lceil (o + 1)(1 - \alpha) \rceil/(o + 1)$, the same as the plain split's. A brute-force check of the end points on random draws found no mismatch. Check all three before you use them. Report the length of the set's convex hull, and record whenever the set is not an interval.

**No guarantee.** The pooled quantile of all calibration units, and `recentred`, which shifts the pooled interval by the labelled units' mean residual. They are reported as what a practitioner would try and are never called valid.

**The oracle and the price of validity.** In simulation the half-width $q^\star$ at which a new cluster's unit is covered with probability exactly $1 - \alpha$ is computable, and a method's price of validity is its mean threshold over $q^\star$. Simulation tables carry half-widths and real-data tables carry full widths.

**A valid method, in this document,** is one of `hcp`, `ghcp`, `ghcp_noad`, `within_plain`, `within` and `within_full`. The narrowest valid method in a cell is the one with the smallest mean width among those that are finite in every replicate or draw of that cell.

The tasks, from section 3 of the same instruction.

**The tasks.** Kidney cancer with 24 donors (`CCRCC:24`, written `CCRCC` in the round-4 tables) and with donors `INT4` and `INT24` merged (`CCRCC:23_merged`, written `CCRCC_23merged`), because the two may be one donor. Indiana kidney (25 donor units). Lung (15 donors), where disease is not fixed and each fold of the 10-donor design trains on 4 donors. Three encoders, `hoptimus0`, `uni_v2` and `resnet50`. The 50-gene lists on the kidney tasks and the 343-gene panel on lung, as round 4.

## 4. The checks behind the inference track's closing readings

From `docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, section 2, the closing memo of 9 October 2026 on `docs/round05/i03/ppi/round5_ppi_final_report.md`. It describes why acceptance check 3 failed, where `rej_t` failed, and how flat the allocation optimum is. Round 7 later found that the worst `rej_t` cells for $\theta_2$ counted draws with no interval as misses (summary, finding 6).

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

## 5. The question the inference track left

From `docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, section 5. Round 7 ran it and found that weighting fails under rejective selection (summary, open threads).

Rejective selection uses only label-free quantities, so each cluster's inclusion probability under D2 can be computed by simulating the design before any label is bought. A Horvitz-Thompson or Hájek mean of the labelled clusters, weighted by those probabilities, would then be unbiased for the design, and the residual variance of section 3 of the theory document would apply to it. Whether that removes the bias at small $n_L$ and with several balance variables, whether a floor on the residual degrees of freedom is still needed, and what it costs in width, is the first question for the next round. It is not part of this track and nothing is run for it now.

## 6. Dead ends recorded at the start of the round

From `round5_oversight_handoff.md` (at tag `record-full-2026-11`), section 14, written on 4 October 2026 at the close of round 4. "The previous handoff" is `docs/round04/round04_methods_note.md` (formerly `round4_oversight_handoff.md`, at tag `record-full-2026-11`), and "section 13" is the handoff's list of what to pursue, which round 5's prediction-set track took up as stage W4 (summary, findings 10 and 11).

The previous handoff's section 12 stands. Round 4 added these.

- **A pre-test for $\lambda$.** The draws that pass are the ones with a large estimated slope, so it selects a biased $\lambda$. Ratio 1.17 against 1.03 for plain cross-fitting on kidney cancer `uni_v2` with 16 donors.
- **Bootstrap intervals with few clusters.** The percentile cluster bootstrap under-covers and the wild cluster bootstrap did not beat the plain interval.
- **Tuning $\lambda$ on the clusters it is applied to.** Under-covers with few clusters while looking narrowest.
- **Recalibrating donor offsets.** No out-of-sample skill, and the donor-weighted estimands are invariant to it.
- **Two-way clustering.** No HEST task has a second grouping that crosses the donor.
- **Spot-weighted PPI rows as evidence of a gain.** A permuted predictor produces the same gain.
- **Four candidate prediction-set methods with no labelled test units.** A smoothed HCP, a model-based donor quantile, an adaptive score, and a rule switching between pooled and HCP. None met the criterion. The switch rule is invalid, with a counterexample. These four methods are closed. The question of whether anything valid can beat HCP is not closed and is to be pursued (section 13).
- **GHCP with a few labelled units at about 10 calibration clusters.** Wider than HCP with none.
- **The `ppi_py` census file for anything clustered.** It has no cluster identifiers.
- **Claiming the break-even rule or the gain limit as new.** Both exist for simpler settings.
- **Background slides on the field or the tools.** The advisors know them.
