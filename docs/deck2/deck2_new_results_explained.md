# Round 4, the new results explained

4 October 2026. Written by the oversight chat for Nicolas, as the companion to `deck2_outline.md`. Part A explains the six results on slides 10 to 15. For each one it says what we obtained, why we looked for it, how we obtained it, and the theory behind it. Part B goes briefly over the results that are not on the slides. Part C lists what is not established.

**Added after the literature check of 4 October** (`deck2_literature_check.md`). Two of the results below are versions of results that already exist for simpler settings, and the text should be read with that in mind. The gain theorem (A2) is the cluster-randomised-trial formula for a covariate (Raudenbush 1997; Bloom, Richburg-Hayes and Black 2007) carried over to a black-box predictor. The break-even rule (A3) is the rule of Mani, Xu, Lipton and Oberst (arXiv:2505.20178) for independent data, with labelled clusters in place of labelled units. The first lower-bound proposition (A5) follows closely from recent universality results for conformal prediction (Tibshirani, Barber and Ramdas, arXiv:2608.27310). The comparison of the two labelling regimes (A4) was not found anywhere.

In the derivations I give the idea and the mechanism and leave out the algebra. Wherever I leave a step out I say so and say what kind of step it is. The full algebra is in `docs/round4_ppi_theory.md` and `docs/round4_conf_lower_bound.md`.

Every number is read from the file named beside it. Paths are relative to the repository root on `main` at `b1f1a7e`.

---

## The setting, once

There are $G$ clusters. In our data a cluster is a donor and a unit is a spot. Donor $g$ has $M_g$ spots. Every spot has a prediction $\hat y_{gi}$ from a model trained on other donors. A spot's measured value $y_{gi}$ is known only if we pay to label it.

**The estimands.** Each quantity we estimate is the average of a per-spot value $z_{gi} = w_{gi}\,y_{gi}$, where the weights $w_{gi}$ do not depend on the labels. Three are used.

- The mean. $w_{gi} = 1$.
- $\theta_2$, a difference between two tissue types within a donor (neoplastic against stromal spots).
- $\theta_3$, the within-donor slope of expression on a morphology covariate. This is the main one.

The same weights applied to the prediction give $f_{gi} = w_{gi}\,\hat y_{gi}$. Averaging over a donor's spots gives the donor's contribution $z_g$ and its predicted counterpart $f_g$. In the donor-weighted version the estimand is the plain average of $z_g$ over donors. All headline results use it.

**The estimator.** Prediction-powered inference (PPI) uses the predictions everywhere and corrects them with the labelled data. With a weight $\lambda$ it is

$$
\hat\theta = \lambda \times (\text{average of } f \text{ where only predictions exist}) + (\text{average over labelled clusters of } z_g - \lambda f_g).
$$

The second piece is called the rectifier. Setting $\lambda = 0$ gives the classical estimator that ignores the predictions. This is the difference estimator of survey sampling, and with $\lambda$ tuned it is the generalised regression estimator. Nothing about the estimator is new.

**Two labelling regimes.** Regime A labels every spot of $n_L$ donors and nothing on the others. Regime B labels $m$ spots on every donor.

**Two targets.** Under the design-based target the $G$ donors at hand are the whole population, and the truth is the value we would get by labelling everything. Under the superpopulation target the donors are a sample from a wider population of donors, and the truth is that population's value. Every coverage check on real data uses the design-based target, because the full-data value is the only truth we can compute.

**The masking experiment.** Most real-data numbers come from one procedure. Take a task where every spot is in fact measured. Pretend only $n_L$ of the $G$ donors are labelled, chosen at random. Compute the classical and the PPI estimates and their intervals from that subset. Repeat for 200 random choices and for every gene. The spread of the estimates across the 200 draws is the empirical variance. The share of intervals that contain the full-data value is the coverage. A ratio below 1 means PPI has the smaller variance.

**The tasks.** CCRCC (kidney cancer, Visium, 24 donors), Indiana kidney (Visium, 25 donor units), lung Xenium (15 donors), and ACS PUMS 2018 income with states or California PUMAs as clusters. Three image encoders are used as predictors on the HEST tasks (`hoptimus0`, `uni_v2`, `resnet50`). A permuted predictor, whose predictions carry no information about the outcome, is run beside them as a control.

---

# Part A. The results on the slides

## A1. A valid interval with few labelled clusters (slide 10)

### What we obtained

A definition of the estimator's interval that covers at close to the nominal 90% with as few as 4 to 16 labelled clusters, for both targets. It has four parts.

1. $\lambda$ is cross-fitted. The labelled clusters are split in two halves, and each half is corrected with a $\lambda$ estimated on the other half.
2. For the design-based target the variance carries a finite-population correction, the factor $(1 - n_L/G)$.
3. $\lambda$ is set to zero when fewer than 6 clusters are labelled.
4. With cross-fitting, the design-based variance needs one extra term, which we found in the last unit of the round.

The numbers, from the simulation (`results/round4/ppi/Q1_estimator/q1_report_numbers.csv`, 2,000 replicates per cell).

- With four labelled clusters, tuning $\lambda$ on the same clusters it is applied to covers 0.87 under one tuning rule and 0.86 under another. Cross-fitting covers 0.90.
- Those two under-covering rules also give the narrowest intervals. In the cells where the predictor is informative their median width is 0.74 and 0.61 of the classical width, against 1.01 for cross-fitting.
- For the design-based target, the form with the finite-population correction and cross-fitting covers 0.89 at every number of labelled clusters from 4 to 20. Round 3's form without the correction covers 0.98 when 12 of 24 clusters are labelled.

On the real tasks with 8 labelled donors, the final design-based interval covers 0.86 to 0.87 on CCRCC, 0.89 on Indiana and 0.85 to 0.865 on lung (`results/round4/ppi/Q4a_recompute/q4a_table61.csv`, median over genes). That is a little under nominal on two of the three.

### Why we looked for it

Round 3 had a working estimator and three things about its interval that we could not explain. It over-covered when half the donors were labelled (0.94 to 0.95). Its $\lambda$ fell as more donors were labelled. And $\lambda$ was tuned on the same handful of donors it was then applied to. Every later result is a statement about widths and variances, so the interval had to be right first.

### How we obtained it

A simulation with a known truth, then the masking experiment on real data. The simulation draws clustered data from a model with a cluster effect and a unit effect, with a predictor of adjustable quality, and varies the number of labelled clusters, the cluster size and the between-cluster share of variance. Each candidate interval's coverage is counted over 2,000 replicates per cell.

### The theory

**Why tuning on the same clusters under-covers.** $\lambda$ is chosen to make the rectifier's variance across the labelled clusters as small as possible. If the same clusters are then used to estimate that variance, the estimate is the minimum of a noisy function, and a minimum over noise is biased downward. It is the same reason a regression's in-sample fit is better than its out-of-sample fit. With four clusters the bias is large, so the interval is too narrow and under-covers. That is also why the rules that under-cover look best on width.

**Why cross-fitting repairs it.** Split the labelled clusters into halves $A$ and $B$. Estimate $\hat\lambda_B$ from half $B$ only and use it to form the rectifiers in half $A$. The clusters in $A$ played no part in choosing $\hat\lambda_B$. So, given $\hat\lambda_B$, the rectifiers in half $A$ are independent draws with a fixed $\lambda$, their average is unbiased, and their sample variance is an honest estimate. Do the reverse for half $B$ and average the two.

**Why the finite-population correction.** When the population is the $G$ donors at hand and we label $n_L$ of them without replacement, the estimate becomes exact as $n_L$ approaches $G$. The variance of a sample mean under sampling without replacement is

$$
\Big(1 - \frac{n_L}{G}\Big)\frac{S^2}{n_L},
$$

which is a textbook result I do not derive here. Round 3's variance had no such factor, so with 12 of 24 donors labelled it was about twice too large. That, and not anything about $\lambda$, was the over-coverage.

**Why $\lambda = 0$ below six clusters.** Cross-fitting with four clusters estimates each $\lambda$ from two clusters. When the predictor is useless, a slope fitted through two points is pure noise, and in the simulation it widens the interval to 1.32 times the classical one. Below six clusters the estimator is therefore the classical one by rule.

**The extra variance term under cross-fitting.** This one is new to round 4's last unit, so I go through it step by step.

Step 1. With cross-fitting, each labelled donor $g$ has its own weight $\lambda_g$, which is $\hat\lambda_B$ if $g$ is in half $A$ and $\hat\lambda_A$ if it is in half $B$. The weight on the population prediction term is the average of these over the labelled donors,

$$
c_U = \frac{1}{n_L}\sum_{g \in L}\lambda_g .
$$

Step 2. Write $\bar F$ for the average of $f_g$ over all $G$ donors, which is known because every spot is predicted. The estimator is

$$
\hat\theta = c_U\,\bar F + \frac{1}{n_L}\sum_{g \in L}\big(z_g - \lambda_g f_g\big).
$$

Step 3. Substitute the definition of $c_U$ into the first term. It becomes a sum over the same labelled donors, so the two pieces combine into one average,

$$
\hat\theta = \frac{1}{n_L}\sum_{g \in L}\big(z_g - \lambda_g\,(f_g - \bar F)\big).
$$

This step is one line of rearrangement and nothing is skipped.

Step 4. So each labelled donor contributes $z_g - \lambda_g f_g + \lambda_g \bar F$. The variance formula we had used only $z_g - \lambda_g f_g$ and left out $\lambda_g \bar F$.

Step 5. When every donor has the same $\lambda$, the left-out piece is the same constant for everyone and does not affect a variance. When the two halves have different $\lambda$, the pieces $z_g - \lambda_g f_g$ differ between the halves by $(\lambda_A - \lambda_B)$ times the typical level of $f$, even though the estimator itself does not vary that way. The old formula read that difference as genuine between-donor variance.

Step 6. The size of the error is governed by how large the level $\bar F$ is against the spread of $f_g$ between donors. For the slope $\theta_3$ on the HEST tasks the weights are centred and $\bar F$ is small, so the error was small. On ACS income for $\theta_2$ the level is large and the error was enormous. The old interval's estimated variance was 204 to 1,069 times the empirical variance. With the term added it is 0.89 to 1.04 times (`results/round4/ppi/Q5a/q5a_design_variance_before_after.csv`). On the HEST tasks the fix moves coverage by at most 0.025.

The estimates themselves never changed. Only the interval around them did.

### What to keep in mind

The simulation coverage numbers for the design-based form were computed before the extra term was added and were not rerun. The final tuning rule for the design-based target (A2 below) was never run in simulation. Its coverage is known from the real-data masking draws only.

---

## A2. What predictions buy under cluster sampling (slide 11)

### What we obtained

**The gain theorem.** Label $n_L$ clusters fully. As the number of units per cluster grows, the ratio of the PPI variance to the classical variance tends to

$$
1 - R^2_{\text{cluster}}
$$

at the best $\lambda$, where $R^2_{\text{cluster}}$ is the squared correlation between the clusters' true contributions and their predicted contributions. The predictor's accuracy on individual units does not appear.

**Evidence on data.** The table sets the theorem's floor beside the ratio observed with 8 labelled clusters.

| task, predictor | $R^2_{\text{cluster}}$ | floor $1 - R^2_{\text{cluster}}$ | observed ratio |
|---|---|---|---|
| CCRCC, `uni_v2` | 0.44 | 0.56 | 0.84 |
| CCRCC, `hoptimus0` | 0.29 | 0.71 | 0.96 |
| CCRCC, `resnet50` | 0.20 | 0.80 | 1.00 |
| Indiana, `hoptimus0` | 0.19 | 0.81 | 0.98 |
| lung, `hoptimus0` | 0.73 | 0.27 | 0.43 |
| lung, `uni_v2` | 0.71 | 0.29 | 0.47 |
| lung, `resnet50` | 0.65 | 0.35 | 0.54 |
| ACS states | 0.70 | 0.30 | 0.43 |
| ACS California PUMAs | 0.88 | 0.12 | 0.19 |

The floor is from `results/round4/ppi/Q2_theory/q2_cluster_r2.csv` and `q2_report_numbers.csv`, measured on all donors, median over genes, $\theta_3$ donor-weighted. The observed ratio is from `results/round4/ppi/Q4a_recompute/q4a_table61.csv`, design-based target.

Every observed ratio is above its floor and they are in the same order. The gap between the two columns is the subject of A3.

**Evidence across genes.** On CCRCC we computed the per-gene interval width ratio for 459 genes. Its Spearman correlation with the gene's cluster-level $R^2$ is $-0.86$ to $-0.90$ over the three encoders. With the gene's ordinary unit-level correlation it is $-0.36$ to $-0.51$ (`results/round4/ppi/Q4_tables/q4_gene_axis_summary.csv`). On Indiana the relation is weak for every measure, because almost no gene gains there.

**A control that changed how we read the tables.** The permuted predictor gives a ratio of 1.00 to 1.05 on the donor-weighted estimands on every task, as it should. On the spot-weighted estimands it gives 0.29 to 0.40 on CCRCC, 0.09 to 0.13 on lung and essentially zero on ACS states $\theta_2$ (`results/round4/ppi/Q5a/q5a_spot_weighted_permuted.csv`). A predictor with no information cannot halve a variance. So every spot-weighted PPI row in our tables is marked as a nuisance row and none is counted as a gain.

### Why we looked for it

The originality check found that the estimator is textbook, so the paper needs a statement of its own. Round 3 had shown a symptom with no named cause. The encoders have a decent unit-level correlation with expression, and yet PPI's interval was only 0.85 to 0.89 as wide as the classical one. The theorem names the cause. It is also the statement any user of PPI with clustered data needs before spending a labelling budget, whatever the application.

### How we obtained it

Three ways. A derivation in the standard random-effects model. A simulation in which $R^2_{\text{cluster}}$ is set to 0.8, 0.5 and 0.2 and the empirical variance ratio is compared with the formula. And the masking experiment on the six task variants, with $R^2_{\text{cluster}}$ measured separately on all donors.

### The theory

**Step 1, the model.** Split the outcome and the prediction into a cluster part and a unit part,

$$
y_{gi} = \mu + u_g + e_{gi}, \qquad \hat y_{gi} = \nu + p_g + d_{gi}.
$$

Here $u_g$ is the donor's true effect and $p_g$ is the donor-level part of the prediction. Write $\sigma_u^2$ and $\sigma_p^2$ for their variances and $C_u$ for their covariance.

**Step 2, the rectifier inherits the same split.** The rectifier $y - \lambda\hat y$ has cluster part $u_g - \lambda p_g$ and unit part $e_{gi} - \lambda d_{gi}$.

**Step 3, averaging within a cluster removes the unit part.** A labelled donor's mean rectifier over $m$ spots has variance equal to the variance of its cluster part plus the variance of its unit part divided by $m$. With hundreds or thousands of spots per donor the second piece is negligible. What is left is the variance of $u_g - \lambda p_g$ across donors, divided by the number of labelled donors.

This is the whole mechanism. Spots within a donor are plentiful, so anything the predictor gets right spot by spot was already averaged away for free. The only uncertainty left is which donors we happened to label, and predictions help only by explaining why one donor differs from another.

**Step 4, the best $\lambda$.** The variance of $u_g - \lambda p_g$ is a quadratic in $\lambda$. Minimising a quadratic is routine and I skip it. The minimum is at $\lambda^\star = C_u/\sigma_p^2$, the regression coefficient of the true donor effects on the predicted ones, and its value there is

$$
\sigma_u^2\,\big(1 - R^2_{\text{cluster}}\big).
$$

The classical estimator's variance is $\sigma_u^2/n_L$ in the same limit. The ratio is $1 - R^2_{\text{cluster}}$.

**Step 5, the term for the unlabelled clusters.** The estimator also needs the average prediction over the clusters that are not labelled. Under the superpopulation target those $G_U$ clusters are themselves a sample, so that average is noisy, and it adds a term. Carrying it through, which I skip, the ratio becomes

$$
1 - R^2_{\text{cluster}} + \frac{n_L}{G_U}\,R^2_{\text{cluster}}
$$

at $\lambda^\star$. It reaches $1 - R^2_{\text{cluster}}$ only when there are many more unlabelled than labelled clusters.

**Step 6, the design-based target has no such term.** There the average prediction over all $G$ donors is a known number, not an estimate. The ratio is exactly the rectifier's between-donor variance over the outcome's, and its minimum is one minus the squared correlation of $z_g$ and $f_g$ over the $G$ donors.

This distinction cost us a correction during the round. The first tuning rule chose $\lambda$ to minimise a variance that included the unlabelled-cluster term, which shrinks $\lambda$ by the factor $G_U/(G_U + n_L)$. On the design-based target that shrinkage is wrong. With 12 of 15 lung donors labelled it multiplies $\lambda$ by 3/15, and the gain almost disappears. Under the first rule the lung ratio for `hoptimus0` was 0.63 with 8 labelled donors and 0.87 with 12. Under the corrected rule, which tunes on the labelled donors' rectifier variance alone, it is 0.43 and 0.41 (`q4a_table61.csv`).

**Step 7, what "cluster-level" means for a slope.** For $\theta_2$ and $\theta_3$ the weights sum to zero within each donor, because each donor is centred on its own values. Adding any constant to all of a donor's predictions therefore changes $f_g$ by that constant times zero. So a donor-level offset in the predictions, which is the kind of error a slide or batch effect produces, cannot affect these estimators at all. $R^2_{\text{cluster}}$ for a slope is about whether the predictor gets each donor's within-donor contrast right. One consequence is that recalibrating donor offsets cannot help, and when we tried it, it did not (Part B).

**The simulation check.** With $\lambda$ fixed at its best value, the empirical ratio matches the formula to within 0.03 in every cell. With 100 unlabelled clusters and 5,000 units per cluster it sits 0.03 to 0.08 above $1 - R^2_{\text{cluster}}$, which is the size of the unlabelled-cluster term (`results/round4/ppi/Q2_theory/theorem_v3/q2_sim_theorem_v3.csv`).

**Why the spot-weighted rows are a nuisance.** In the spot-weighted version the weights are centred on one task-wide value, not within each donor. A donor's weights then do not sum to zero, and their sum $W_g = \sum_i w_{gi}$ differs from donor to donor. A donor's contribution is roughly $W_g$ times the level of expression plus a within-donor part. Its predicted contribution is $W_g$ times the level of the predictions plus a within-donor part. Both share the factor $W_g$. So $z_g$ and $f_g$ are strongly correlated across donors for any predictor whose predictions have a nonzero average level, including one that has been permuted. PPI then removes the between-donor variance of $W_g$, which is a property of the weights and has nothing to do with predicting expression. The permuted predictor gets a $\hat\lambda$ of 0.86 to 0.98 on those rows, which is the signature of this. The lesson for the paper is about the choice of estimand, and the practical rule is that a PPI gain should always be reported beside a permuted predictor's.

### What to keep in mind

The floor and the observed ratio in the table come from different computations, one on all donors and one from masking draws. The theorem is a statement about a limit and a fixed $\lambda$. It does not by itself predict the observed column, which is what A3 is for.

---

## A3. The price of tuning, and how many clusters it takes (slide 12)

### What we obtained

**The tuning-cost formula.** With $\lambda$ cross-fitted from half the labelled clusters, the variance ratio is

$$
1 - R^2_{\text{cluster}} + \text{MSE}(\hat\lambda)\,\frac{\sigma_p^2}{\sigma_u^2},
$$

where $\text{MSE}(\hat\lambda)$ is the variance of the estimated $\lambda$ plus its squared bias.

**The break-even rule.** Predictions lower the variance only when the number of labelled clusters satisfies

$$
n_L > 4 + \frac{2}{R^2_{\text{cluster}}}.
$$

**The check.** In the simulation the observed tuning cost and the formula's prediction differ by at most 0.043 over 24 cells (`results/round4/ppi/Q4_tables/q4_prediction_scores.csv`). We had predicted agreement within 0.03, which held in 21 of the 24, so by our own rule that prediction is scored as refuted. The formula is right to about 0.04.

**The reading on data.** Putting each task's $R^2_{\text{cluster}}$ into the rule gives a break-even of about 7 clusters on lung and on both ACS tasks, 9 for `uni_v2` on CCRCC, 11 for `hoptimus0` on CCRCC, 14 for `resnet50` on CCRCC, and 15 or more on Indiana (15, 18 and 43 for the three encoders). This is my arithmetic from the rule and the $R^2$ values in A2. It matches what the masking experiment shows. Lung and ACS gain from 6 clusters on. On the Visium tasks with 8 to 16 labelled donors only `uni_v2` on CCRCC gains clearly (0.81 to 0.87), and the rest sit between 0.93 and 1.09 (`q4a_table61.csv`).

### Why we looked for it

At the second gate the session's headline was that PPI loses on every HEST task. Reading the whole grid showed gains with few labelled donors that disappeared with more, which no version of the gain theorem predicts. In the simulation the ratio with the best $\lambda$ sat on the theorem, while the ratio with an estimated $\lambda$ sat 0.11 to 0.42 above it. So the gap between theory and practice was the estimation of $\lambda$, and it needed its own formula. The break-even rule is also the direct answer to a question a practitioner asks before labelling anything.

### How we obtained it

A derivation, then a rerun of the theorem simulation that kept every replicate's $\hat\lambda$, so that $\text{MSE}(\hat\lambda)$ could be measured and the formula's prediction compared with the observed excess cell by cell.

### The theory

**Step 1, condition on the estimated $\lambda$.** Take half $A$, corrected with $\hat\lambda_B$ from half $B$. The donors in $A$ are independent of $\hat\lambda_B$. Given $\hat\lambda_B$, each donor's rectifier $u_g - \hat\lambda_B\,p_g$ has mean zero and variance

$$
\sigma_u^2 - 2\hat\lambda_B C_u + \hat\lambda_B^2\,\sigma_p^2 .
$$

**Step 2, average over $\hat\lambda_B$.** The conditional mean is zero whatever $\hat\lambda_B$ is, so by the law of total variance the unconditional variance is the average of the conditional variance. The expression in step 1 is quadratic in $\hat\lambda_B$, and the average of a square is the squared mean plus the variance. So the average equals the same expression evaluated at the mean of $\hat\lambda$, plus $\text{Var}(\hat\lambda)\,\sigma_p^2$.

**Step 3, complete the square.** The expression at the mean of $\hat\lambda$ equals its minimum $\sigma_u^2(1 - R^2_{\text{cluster}})$ plus the squared distance of that mean from $\lambda^\star$, times $\sigma_p^2$. This is the usual identity for a quadratic around its minimum and I skip the line of algebra. Dividing by the classical variance $\sigma_u^2$ gives the formula.

In words, a noisy $\lambda$ adds noise to the estimator in proportion to how much the predictions vary between clusters. Each donor's correction is $\hat\lambda\,p_g$, so an error in $\hat\lambda$ is multiplied by $p_g$.

**Step 4, averaging the two halves does not remove the cost.** The two halves' averages are nearly uncorrelated. Showing that takes a term-by-term expansion, which I skip. The result is that averaging them restores the full sample size, but each half is still corrected with a $\lambda$ estimated from only half the clusters.

**Step 5, the break-even.** For a least-squares slope fitted on $n_h$ clusters with normal predictors, the variance of the slope is a standard result,

$$
\text{Var}(\hat\lambda) = \frac{\sigma_u^2\,(1 - R^2_{\text{cluster}})}{(n_h - 3)\,\sigma_p^2}.
$$

I take it as given. Substituting into the formula, the tuning cost is $(1 - R^2_{\text{cluster}})/(n_h - 3)$. The ratio is below 1 when this cost is smaller than the gain $R^2_{\text{cluster}}$. Rearranging, which I skip, gives $n_h > 2 + 1/R^2_{\text{cluster}}$ for each half, and so $n_L > 4 + 2/R^2_{\text{cluster}}$ in total.

### What to keep in mind

The rule is a structural statement. We also tried to use it cell by cell, predicting from each cell's own $\hat\lambda$ and its standard error whether that cell would gain. The sign was right in 23 of 36 cells, which is not good enough to call a predictor (`q4_prediction_scores.csv`). The paper should present the rule as the reason for the pattern and not as a per-dataset test. The derivation of the break-even assumes an unclipped slope. Our $\hat\lambda$ is clipped to $[0, 1]$, which makes the rule somewhat conservative.

---

## A4. Where to put the labels (slide 13)

### What we obtained

**Regime B beats regime A at an equal number of labelled spots.** On every HEST task, when regime A has 8 or fewer donors, spreading the same number of labelled spots over all donors gives the narrower interval. On CCRCC with 2,400 labelled spots, regime B's interval is 0.46 to 0.64 as wide as regime A's with 4 to 8 donors, and the advantage grows with the budget (`results/round4/ppi/Q3_regimes/q3_report_numbers.csv`, superpopulation target). When a donor is charged at 10 spots, regime B is narrower in 216 of 232 cells (`results/round4/ppi/Q4_tables/q4_report_numbers.csv`).

**It reverses when touching a donor is expensive.** At 100 spots per donor, regime B loses at the smallest budget on CCRCC (1.20) and Indiana (2.17). At 1,000 spots per donor only lung can afford regime B at all, and there it is still narrower in 11 of 16 cells.

**In regime B the gain from predictions follows within-cluster $R^2$.** The width of regime B's PPI interval over its classical interval is 0.81 to 0.84 on the Visium tasks, 0.42 on lung and 0.08 on ACS states (`results/round4/ppi/Q5_joint/q5_joint_design.csv`). The theory below predicts the square root of $1 - R^2_{\text{within}}$. With the measured within-donor $R^2$ of 0.37 on CCRCC, 0.83 on lung and 0.994 on ACS states, that prediction is 0.79, 0.42 and 0.08 (`q2_cluster_r2.csv`, my arithmetic).

**Regime B's design-based interval covers.** 0.885 to 0.905 on the HEST tasks (`q3_report_numbers.csv`).

**The allocation formula.** With a cost $c_d$ per donor and $c_s$ per spot, the best number of spots per labelled donor is

$$
m^\star = \sqrt{\frac{c_d}{c_s}\cdot\frac{\sigma_e^2}{\sigma_u^2}},
$$

and with a predictor the same formula holds with the rectifier's two variances in place of the outcome's. At a cost ratio of 100 the fitted optimum moves from 121 to 108 spots per donor on CCRCC, from 236 to 188 on Indiana, from 172 to 121 on lung and from 379 to 89 on ACS states (`results/round4/ppi/Q2_theory/q2_report_numbers.csv`).

### Why we looked for it

This is the design question in the paper's title. A practitioner with a fixed budget can sequence a few donors completely or sample a little from every donor, and the two regimes turn out to be governed by different properties of the predictor. A foundation model with large slide-level offsets is poor at the cluster level and may be good within a cluster, which is exactly the case where the choice matters.

### How we obtained it

The masking experiment run in both regimes on the same tasks, at three budgets (2,400, 4,800 and 9,600 labelled spots) and four cost ratios, with a simulation arm for regime B's coverage.

### The theory

**Step 1, regime B under the design-based target.** Every donor is observed, so there is no uncertainty about which donors we have. The donors act as strata. Inside donor $g$ we draw $m$ of its $M_g$ spots at random, and the only randomness is which spots. The variance of the donor-weighted estimator is the sum over donors of each donor's within-donor sampling variance,

$$
\frac{1}{G^2}\sum_{g=1}^{G}\Big(1 - \frac{m}{M_g}\Big)\frac{S_{r,g}^2}{m},
$$

where $S_{r,g}^2$ is the variance of the rectifier among donor $g$'s spots. This is the stratified-sampling variance and I take it as given.

**Step 2, donor-level terms vanish.** Anything constant within a donor, including the donor's true effect and any donor-level error of the predictor, drops out of a within-donor variance. So the predictor's cluster-level accuracy, which was everything in regime A, does not appear at all.

**Step 3, the ratio.** Minimising over $\lambda$ as in A2, the ratio to the classical variance is $1 - R^2_{\text{within}}$, the squared correlation between outcome and prediction among spots of the same donor. A width ratio is the square root of a variance ratio, which gives the predictions quoted above.

**Step 4, regime B under the superpopulation target.** If the donors are a sample, each donor's own mean is still one draw, so a term $\sigma_u^2/G$ stays in the variance and no predictor can reduce it. Regime A's corresponding term is $\sigma_u^2(1 - R^2_{\text{cluster}})/n_L$. Regime B wins on that term when

$$
R^2_{\text{cluster}} < 1 - \frac{n_L}{G}.
$$

With 8 of 24 donors this is $R^2_{\text{cluster}} < 0.67$, which every Visium encoder satisfies. That is the reason regime B wins there. It divides the donor-level variance by all $G$ donors, where regime A divides a reduced variance by only $n_L$.

**Step 5, the allocation formula.** Fix a total cost and write the number of donors affordable as a function of $m$. The variance becomes a function of $m$ alone, with one term that rises in $m$ and one that falls. Setting the derivative to zero, which I skip, gives $m^\star$. It is the classical two-stage sampling result.

**Step 6, which way a predictor moves the optimum.** A predictor moves the optimum toward fewer spots per donor and more donors when it removes a larger share of the unit-level variance than of the cluster-level variance. That holds when $R^2_{\text{within}}$ exceeds $R^2_{\text{cluster}}$ by enough to cover any mismatch between the two levels' best $\lambda$. On our data the within-donor $R^2$ exceeds the cluster-level one for every HEST encoder except `uni_v2` on CCRCC. My Q3 memo stated this without the exception and the session corrected it.

### What to keep in mind

Two things, and the second matters for the slide.

Regime B was only run at the budget grid's values, so its smallest setting is 6 spots per donor on Indiana, 14 on CCRCC and 36 on lung.

The permuted predictor also narrows the regime B interval. Its width ratio is 0.87 on CCRCC against 0.83 for the encoders, 0.66 on lung against 0.42, and 0.15 on ACS states against 0.08 (`q5_joint_design.csv`). The reason is the same kind as in A2. For a slope, a spot's value is its weight times its outcome, and its predicted value is the same weight times its prediction. Both contain the weight times an average level, so they are correlated within a donor even when the prediction is uninformative, and the measured within-donor $R^2$ of the permuted predictor on this scale is 0.24 on CCRCC. So on the Visium tasks most of regime B's gain over classical comes from this known-weights correction and only the step from 0.87 to 0.83 comes from the encoder. On lung the encoder's share is large. I am reading this from the joint table and the $R^2$ file. No unit of the round was set up to test it, so treat it as a reading and not as an established result. It does not affect the comparison of regime B against regime A.

---

## A5. Prediction sets for spots of a new donor (slide 14)

### Background in three paragraphs

A prediction set is an interval around a spot's predicted expression that should contain the measured value 90% of the time. Split conformal prediction builds it from calibration data. Compute the absolute error of the prediction on $n$ calibration points, take the $\lceil (n+1)(1-\alpha) \rceil$-th smallest error as the half-width, and the interval covers a new point with probability at least $1 - \alpha$, provided the new point is exchangeable with the calibration points.

A spot from a new donor is not exchangeable with spots from other donors, which is why the naive pooled interval covers 0.86 on CCRCC. Hierarchical conformal prediction (HCP) restores the guarantee by treating donors as the exchangeable objects. It gives each of the $K$ calibration donors a total weight of $1/(K+1)$, spread over that donor's errors, and keeps the last $1/(K+1)$ for the unseen test donor, placed at infinity. The half-width is the $1 - \alpha$ quantile of that weighted distribution. It is finite only if the calibration donors' total weight $K/(K+1)$ reaches $1 - \alpha$, that is, only if $K + 1 \ge 1/\alpha$. At 90% that needs at least 9 donors.

GHCP (Mallick, Tchetgen Tchetgen, Dobriban and Lee) assumes that $o$ spots of the test donor are labelled, and uses them to adapt the interval to that donor while keeping a guarantee.

### What we obtained

**A reproduction.** The released GHCP code reproduces the paper's simulation tables at 254 of 254 values and its ACS tables at 53 of 53 (`results/round4/conformal/C1_testbed/ghcp_repro_longleaf/compare/c1_ghcp_reproduction.csv`, `results/round4/conformal/C3_real/frag_ACS_o/acs_ghcp_reproduction.csv`).

**The price of a valid set as a map over $K$ and $o$, on real data.** Numbers for CCRCC, from `results/round4/conformal/C3_real/c3_report_numbers.csv` and `c3_o_sweep_by_task.csv`.

Along $K$, with no labelled test spots.

- HCP is infinite for 8 or fewer calibration donors.
- Its width over the pooled width falls from 1.95 at $K = 10$ to 1.36 at $K = 20$, and its coverage from 0.97 to 0.94.
- The pooled interval covers 0.86 to 0.87 at every $K$. More calibration donors do not repair it.

Along $o$, with $K = 10$.

| labelled test spots $o$ | method | coverage | mean width |
|---|---|---|---|
| 0 | pooled (no guarantee) | 0.86 | 2.11 |
| 0 | HCP | 0.97 | 4.11 |
| 5 | GHCP | 0.995 | 5.46 |
| 10 | GHCP | 0.996 | 5.06 |
| 10 | within-donor split | 0.91 | 2.32 |
| 25 | GHCP | 0.997 | 4.43 |
| 25 | within-donor split, recentred | 0.93 | 2.14 |
| 100 | within-donor split, recentred | 0.90 | 1.75 |

Three regions follow, and they repeat on Indiana, lung and ACS.

- With no labelled spots, HCP is the valid choice.
- With fewer than about 10 labelled spots, GHCP is the only finite method that uses them, and it is wider than HCP with none. Its width is 1.23 to 1.49 times HCP's at $o \le 10$ across the HEST tasks.
- From about 10 labelled spots, a plain split conformal interval calibrated on the test donor's own labelled spots is valid, covers 0.91, and is about half GHCP's width. From 25 spots a variant that first recentres on half of them is narrower still.

**A remark of our own for small $K$.** When $K + 1 < 1/\alpha$, every valid method must return an infinite set with probability at least $1 - \alpha(K+1)$ on some data-generating law, and a randomised version of HCP attains exactly that. Any method that is finite must over-cover, with a computable floor. At 90% the forced probability of an infinite set is 0.4 with 5 donors and 0.1 with 8, and the coverage floor for a finite method is 0.95 with 4 donors and 0.92 with 5 (`results/round4/conformal/C2_candidates/lower_bound/c2_lb_beta_star.csv`).

### Why we looked for it

The originality check found that GHCP had taken the labelled-test-spots setting six weeks before us. Two things were left. One was practical. A reader of our paper needs to know what a valid prediction set costs at the numbers of donors and labelled spots a real study has, and GHCP's paper does not map that. The other was theoretical. With no labelled test spots, is HCP's conservatism forced or could a cleverer method do better? That question got a three-day scoping with a stop rule, not a track.

### How we obtained it

First a simulation testbed with a known oracle, on which the released GHCP code was reproduced and four candidate methods of our own were tested against a criterion fixed in advance. None passed (Part B). Then the real-data map on CCRCC, Indiana, lung and ACS, where every comparison is made within the same task, encoder, fold, calibration draw and label draw, so that only the method differs. The lower-bound work is pen and paper with a small numerical table.

### The theory

**Why a few labelled spots do not help at $K = 10$.** GHCP's construction sets one calibration donor aside to restore exchangeability between the test donor, which has $o$ labelled spots, and the calibration donors, which have many. With 10 calibration donors that leaves 9, which is exactly the edge $K + 1 = 1/\alpha$ where the hierarchical quantile is at its most conservative. And five labelled spots carry too little information about the test donor to buy that back. With more donors, or with 25 or more labelled spots, GHCP improves, as its paper shows. This is how our reports describe the mechanism. I have not rederived GHCP's guarantee.

**Why the within-donor split needs about 10 spots.** It is ordinary split conformal with $n = o$ calibration points, all from the test donor, so they are exchangeable with that donor's other spots and the guarantee is the standard one. The half-width is the $\lceil 0.9\,(o+1) \rceil$-th smallest error, which exists only when that rank is at most $o$. That holds from $o = 9$. The recentred variant spends half the labelled spots on estimating the donor's offset and calibrates on the rest, so it needs about twice as many, and on our grid it is finite from 25.

**The lower bound, the idea of the forced infinite set.** I give the argument in four steps and skip one construction.

Step 1. Validity has to hold for every possible data-generating law. Take a very simple one, in which each donor's errors are all equal to a single number, and those numbers are independent draws from some continuous distribution. The problem is then to bound the next number given $K$ earlier ones.

Step 2. By symmetry, the new donor's number is the largest of the $K + 1$ with probability $1/(K+1)$.

Step 3. No finite rule can reliably cover a new maximum. Whatever finite threshold the rule computes from the $K$ numbers, one can choose the distribution so that a value exceeding all $K$ of them almost always exceeds the threshold as well, by stretching the scale above each observed value. The construction that does this is written out in `docs/round4_conf_lower_bound.md`, section 8.1, and I skip it here.

Step 4. So when the rule returns a finite set, it covers with probability at most $K/(K+1)$. If it returns an infinite set with probability $\pi$, its coverage is at most $\pi + (1 - \pi)\,K/(K+1)$. Requiring that to be at least $1 - \alpha$ and solving for $\pi$, which is one line, gives $\pi \ge 1 - \alpha(K+1)$. When $K + 1 \ge 1/\alpha$ the bound is zero or negative and says nothing.

**The coverage floor for finite methods.** The idea is contamination. Mix a small probability $\varepsilon$ of a donor whose errors are astronomically large into any law on which the method is finite. If no calibration donor is of that kind, the method behaves as before and cannot cover a test donor of that kind. Validity under the mixed law then forces the method to have over-covered on the original law, and optimising over $\varepsilon$ gives the floor. The optimisation is calculus and I skip it.

**What stays open.** For $K + 1 \ge 1/\alpha$, which includes $K = 10$, neither argument forces anything. The scoping found a rule that is valid and narrower than HCP when the donors look alike, but it is wider than HCP when they differ, so it does not dominate. Whether anything valid beats HCP by a real margin there is open.

### What to keep in mind

The ACS rows of our map use states as groups and the PPI track's predictor, which is not the GHCP paper's own ACS task. The reproduction of their tables used their task. The session did not check whether the two propositions are already in the literature beyond the papers the instruction named.

---

## A6. One labelling design for both targets (slide 15)

### What we obtained

A table that puts the two halves of the paper side by side. For each task and each number $m$ of labelled spots per donor, it shows regime B's confidence interval (width against classical, and coverage) and the cheapest valid prediction set at $o = m$ labelled spots with 10 calibration donors (`results/round4/ppi/Q5_joint/q5_joint_design.csv`).

| task | $m$ | CI width, PPI over classical | CI coverage | cheapest valid prediction set | its coverage | its width |
|---|---|---|---|---|---|---|
| CCRCC | 14 | 0.83 | 0.89 | within-donor split | 0.91 | 2.32 |
| CCRCC | 84 | 0.81 | 0.89 | within-donor split, recentred | 0.92 | 1.96 |
| Indiana | 6 | 0.84 | 0.90 | GHCP | 0.999 | 4.56 |
| Indiana | 51 | 0.84 | 0.90 | within-donor split, recentred | 0.92 | 1.75 |
| lung | 36 | 0.43 | 0.90 | within-donor split, recentred | 0.93 | 2.91 |

The statement it supports is that a design of tens of labelled spots on every donor serves both targets, and a design of a few fully labelled donors serves neither as well.

### Why we looked for it

The same labelled spots on a donor do two jobs. They feed the rectifier of the confidence interval and they calibrate the prediction set for that donor's remaining spots. If the two jobs needed very different numbers of spots there would be no single design to recommend, so the paper's design section needs this table.

### How we obtained it

No new computation. The PPI track read the conformal track's merged table from `main` at a recorded commit and joined it to its own regime B results, using the nearest $o$ at or below each $m$.

### The theory

There is none beyond A4 and A5. The table is where they meet. Regime B's interval is valid at every $m$ it was run at, and the prediction set becomes cheap from about 10 spots.

### What to keep in mind

The statement I originally asked the session to support said the confidence interval is served "from the first spot". The table does not show that. Regime B was not run below 6 spots per donor on HEST, and on ACS states with one spot per state the regime B slope interval covers 0.505. The honest version is that a handful of spots per cluster is needed for the interval too.

---

# Part B. Results not on the slides

Each is one paragraph. All are in the track reports with their files.

**PPI track.**

- **A pre-test for $\lambda$ was tried and dropped.** The rule set $\lambda$ to zero unless its estimate exceeded one or two standard errors. On real data it did worse than plain cross-fitting, for example a ratio of 1.17 against 1.03 on CCRCC `uni_v2` with 16 donors. The draws that pass a pre-test are the ones with a large estimated slope, so the pre-test selects a biased $\lambda$. The break-even rule replaced it. I had proposed the pre-test.
- **No bootstrap is used.** In the simulation the percentile cluster bootstrap covers 0.76 with four clusters and 0.84 with eight. The wild cluster bootstrap did not beat the plain cluster-robust interval either.
- **Unequal cluster sizes.** For the superpopulation target the Bell and McCaffrey CR2 variance removes the coverage loss that the simpler CR1 variance shows when cluster sizes differ, 0.88 against 0.85.
- **A coverage shortfall no interval removes.** For the spot-weighted slope the classical interval covers 0.84 in the hardest simulation cells even though its variance estimate is right on average. The donor contributions are skewed, so the $t$ reference is wrong. This is recorded as a limit of the definition.
- **The clipped $\hat\lambda$ often reads exactly 0.5.** The two halves frequently clip at 0 and at 1, and their average is 0.5. The tables now carry the unclipped value with its standard error, which is 0.47 to 0.67 with standard errors of 0.39 to 0.85 on CCRCC and Indiana.
- **Recalibrating donor offsets does not help.** A ridge model predicting each donor's offset from its mean embedding has no out-of-sample skill, and by step 7 of A2 it could not have changed the slope estimands anyway.
- **Two-way clustering has nothing to act on.** No HEST task has a second grouping that crosses the donor, and ACS 2018 is one survey year.
- **The ACS application.** On states the cluster-level $R^2$ for $\theta_2$ is 0.37 after correction, and the donor-weighted ratio is 0.51 to 0.58. On California PUMAs the gain is larger still. One spot-weighted row runs opposite to the break-even rule, and it is a nuisance row.
- **The IDC biomarker example.** Pooled over its four donors the estimate is 0.58 with a 90% interval of 0.33 to 0.84. With four donors the estimator is classical by rule.
- **The gene axis on Indiana.** Some genes have a corrected cluster-level $R^2$ of exactly 1, which is the correction clipping on genes with almost no between-donor variance. They are flagged and the summaries are given with and without them.
- **The crossover cost ratio.** The theory's predicted cost ratio at which regime A overtakes regime B was within a factor of two of the empirical one for 10 of 20 task and predictor pairs. In most cells regime B wins wherever it is affordable, so the empirical crossover is just the affordability limit.
- **Predictions scored.** We wrote predictions before each stage. A majority were refuted or only partly held, including several of mine. The ones that mattered are in Part A. The rest are in section 5 of each report.

**Conformal track.**

- **Four candidate methods at $o = 0$, none forward.** A smoothed HCP, a model-based donor-level quantile, an adaptive score, and a rule that switches between pooled and HCP. Against a criterion fixed in advance, the smoothed version was not narrower, the model-based one lost coverage because donor quantiles are skewed, the adaptive score's scale estimate was too noisy at small $o$, and the switch rule turned out not to be valid.
- **The switch rule's counterexample.** With ten normal donors and one donor that is a point mass just above the pooled threshold, its coverage is 0.899. A repaired version is valid but does not dominate HCP.
- **Two discrepancies in GHCP.** The released code keeps one more group in its restricted pool than the paper's equation, and the paper's tables were produced under the code's rule. And the released code resolves exact ties at the quantile level differently from the standard convention, which makes it infinite in a few cells where the standard rule is finite. Both go to you, David and Dr. Zhu as a decision on whether to tell the authors.
- **GHCP's restricted-pool variant.** It is infinite at every $o$ with 10 donors, because the restricted pool keeps about five.
- **A recentred cross-donor interval.** Shifting the pooled interval by the labelled spots' mean error keeps the pooled width and moves coverage to or past nominal. It has no guarantee and is recorded as a practitioner's shortcut.
- **The upper tail.** In the top decile of predicted values the pooled interval covers 0.73. GHCP with a quantile-regression score reaches 0.98 to 0.99 there, on six genes only.
- **How large the pooled shortfall is.** 0.036 below nominal on CCRCC at $K = 10$, 0.013 on Indiana, and under 0.002 on lung and ACS. The donor shift is real on CCRCC and small elsewhere, which was not what round 3 led us to expect.

**The data pull.** The lung Xenium task has 20 samples from 15 donors and 343 genes. The donor audit found that HEST's own 21 donor keys split four donors into eight labels.

---

# Part C. What is not established

- The final design-based tuning rule and the corrected variance were never run in simulation. Their behaviour is known from 200 masking draws per cell on real data.
- On the real tasks the final design-based interval covers 0.85 to 0.89, a little under 0.90. We have not explained the remaining shortfall.
- Regime B below 6 spots per donor on HEST was not run.
- The break-even rule explains the pattern across tasks and does not predict individual cells.
- The reading in A4 that most of regime B's gain on Visium comes from the weights and not the encoder is my reading of two files, with no dedicated check.
- Whether HCP can be beaten at $K + 1 \ge 1/\alpha$ is open.
- Whether the two lower-bound propositions are new has not been checked beyond the papers named in the instruction.
- A spot-weighted estimand under which PPI gains are real has not been built. It is a candidate for round 5.
