# Round 4, the new results explained

4 October 2026, revised the same evening after Nicolas's questions on the first version. Written by the oversight chat for Nicolas, as the companion to `deck2_outline.md`. Part A explains the six results on slides 10 to 15. For each one it says what we obtained, why we looked for it, how we obtained it, and the theory behind it. A short section after A6 sorts out the different things the word "cost" has meant. Part B goes briefly over the results that are not on the slides. Part C lists what is not established.

**What changed in this revision.** The numbers in brackets are the items of your question list.

- Every theory section is now written with its expressions. In the first version I described derivations in words, which was a misreading of what you asked for. A step is skipped only when it is algebra between two displayed lines, and I say so each time (3b, 4b).
- The estimands in "The setting, once" are written out as formulas, with what each one is in plain terms (4c).
- A1 has a new paragraph on which $\lambda$ is being fitted and why each donor gives one data point, and the paragraph on $\lambda = 0$ below six clusters is rewritten (1a, 1b).
- A2 explains the permuted predictor on the donor-weighted and on the spot-weighted estimand, what was step 7 and is now step 8, and the nuisance rows, each with formulas (2a, 2b, 2c).
- A3 is redone from the start. It says where "mean zero" comes from and what the best and the estimated $\lambda$ are (3a, 3b, 3c).
- A4 defines the two $R^2$ values and is redone from the start (4a, 4b).
- A5 restates the small-$K$ result as two propositions with their arguments (5a).
- The section on cost is new (6a).
- Part C marks the two open questions you asked to pursue.

**Added after the literature check of 4 October** (`deck2_literature_check.md`). Two of the results below are versions of results that already exist for simpler settings, and the text should be read with that in mind. The gain theorem (A2) is the cluster-randomised-trial formula for a covariate (Raudenbush 1997; Bloom, Richburg-Hayes and Black 2007) carried over to a black-box predictor. The break-even rule (A3) is the rule of Mani, Xu, Lipton and Oberst (arXiv:2505.20178) for independent data, with labelled clusters in place of labelled units. The first lower-bound proposition (A5) follows closely from recent universality results for conformal prediction (Tibshirani, Barber and Ramdas, arXiv:2608.27310). The comparison of the two labelling regimes (A4) was not found anywhere.

The full algebra is in `docs/round4_ppi_theory.md` and `docs/round4_conf_lower_bound.md`.

Every number is read from the file named beside it. Paths are relative to the repository root on `main`.

---

## The setting, once

**The data.** There are $G$ clusters. In our data a cluster is a donor and a unit is a spot. Donor $g$ has $M_g$ spots, and $N = \sum_g M_g$ is the total. For spot $i$ of donor $g$ and one gene there are three things.

- $y_{gi}$, the measured expression (on the $\log(1 + \text{count})$ scale). It is known only if we pay to label the spot.
- $\hat y_{gi}$, the predicted expression, from a model trained on other donors. It is known for every spot.
- Covariates read from the image, known for every spot. The two we use are $x_{gi}$, the mean nuclear area in the patch, and the patch's tissue type.

**Why every estimand is written as an average.** PPI is defined for averages. A slope or a difference between two groups is not an average on its face. But each can be rewritten as an average of $w_{gi}\,y_{gi}$, where the weight $w_{gi}$ is computed from the covariates alone. That is all the weights are for. They never use a label, so they are known for every spot before anything is measured. I write

$$
z_{gi} = w_{gi}\,y_{gi}, \qquad f_{gi} = w_{gi}\,\hat y_{gi},
$$

for the per-spot value and its predicted counterpart.

**The donor-weighted estimands.** Each donor gets one number, its contribution

$$
z_g = \frac{1}{M_g}\sum_{i=1}^{M_g} w_{gi}\,y_{gi},
$$

and the estimand is the plain average over donors,

$$
\theta = \frac{1}{G}\sum_{g=1}^{G} z_g .
$$

The three choices of weight give three estimands.

- **The mean.** $w_{gi} = 1$, so $z_g = \bar y_g$, the donor's mean expression.
- **$\theta_2$, a difference between tissue types.** Let $\pi_{g,\text{neo}}$ and $\pi_{g,\text{str}}$ be the shares of donor $g$'s spots that are neoplastic and stromal. Take $w_{gi} = 1/\pi_{g,\text{neo}}$ on neoplastic spots, $-1/\pi_{g,\text{str}}$ on stromal spots, and 0 elsewhere. Then

$$
z_g = \bar y_{g,\text{neo}} - \bar y_{g,\text{str}},
$$

  the donor's own difference in mean expression between its tumour spots and its stroma spots. I skip the one line that shows the weights give this.
- **$\theta_3$, a slope. This is the main one.** Let $\bar x_g$ and $v_g$ be the mean and variance of nuclear area among donor $g$'s spots. Take $w_{gi} = (x_{gi} - \bar x_g)/v_g$. Then

$$
z_g = \frac{\frac{1}{M_g}\sum_i (x_{gi} - \bar x_g)\,y_{gi}}{v_g} = \frac{\text{Cov}_g(x, y)}{\text{Var}_g(x)} = \beta_g ,
$$

  the least-squares slope of expression on nuclear area fitted inside donor $g$.

So $\theta_3$ is the average over donors of each donor's own slope. In words, it answers "in a typical patient, how does this gene's expression change with nuclear size". $\theta_2$ is the average over donors of each donor's own tumour-against-stroma difference.

The predicted counterpart $f_g$ is the same formula with $\hat y$ in place of $y$. For $\theta_3$ it is the slope of the predicted expression on nuclear area inside donor $g$, which I will write $\hat\beta_g$.

One property matters later. For $\theta_2$ and $\theta_3$ the weights of a donor sum to zero,

$$
\sum_{i=1}^{M_g} w_{gi} = 0 ,
$$

because each donor is centred on its own mean. For the mean they sum to $M_g$.

On the census data there are no tissue types, and what the tables call $\theta_2$ there is the plain mean of log income.

**The spot-weighted estimands.** Here the constants are computed once for the whole task and not donor by donor. For the slope, $w_{gi} = (x_{gi} - \bar x)/v$ with $\bar x$ and $v$ the mean and variance of nuclear area over all $N$ spots, and

$$
\theta^{\text{spot}} = \frac{1}{N}\sum_{g=1}^{G}\sum_{i=1}^{M_g} w_{gi}\,y_{gi},
$$

which is the slope of one regression fitted to all spots pooled, ignoring donors. A donor enters through its total $Z_g = \sum_i w_{gi}\,y_{gi}$. Its weights no longer sum to zero. Their sum is

$$
W_g = \sum_{i=1}^{M_g} w_{gi} = \frac{M_g\,(\bar x_g - \bar x)}{v},
$$

which is large for a donor with many spots or with unusually large or small nuclei. All headline results use the donor-weighted version. The spot-weighted version is where the nuisance rows of A2 come from.

**The estimator.** Write $L$ for the set of $n_L$ labelled donors. In regime A with every spot of a labelled donor measured, $z_g$ is known exactly for $g \in L$, and $f_g$ is known for every donor. The estimator with weight $\lambda$ is

$$
\hat\theta = \lambda\,\bar F + \frac{1}{n_L}\sum_{g \in L}\big(z_g - \lambda f_g\big), \qquad \bar F = \frac{1}{G}\sum_{g=1}^{G} f_g .
$$

The first piece uses the predictions on everyone. The second piece, the average of $r_g = z_g - \lambda f_g$ over the labelled donors, is called the rectifier. It corrects the first piece with the labelled data. For any fixed $\lambda$ the estimator is unbiased when the labelled donors are a random sample, since the average of $f_g$ over a random sample has expectation $\bar F$, so the two $\lambda$ terms cancel in expectation and what is left is the expectation of $z_g$, which is $\theta$. Setting $\lambda = 0$ gives the classical estimator, the plain average of $z_g$ over labelled donors. This is the difference estimator of survey sampling, and with $\lambda$ tuned it is the generalised regression estimator. Nothing about the estimator is new.

**Two targets.** Under the design-based target the $G$ donors at hand are the whole population, and the truth is the value we would get by labelling everything. The form above is the one used for it, and I call it the textbook form. Under the superpopulation target the donors are a sample from a wider population of donors, and the truth is that population's value. There the first piece averages $f_g$ over the $G_U$ unlabelled donors only, $\hat\theta = \lambda\,\bar f_U + \frac{1}{n_L}\sum_{g \in L}(z_g - \lambda f_g)$, so that the two pieces use different donors. Every coverage check on real data uses the design-based target, because the full-data value is the only truth we can compute.

**Two labelling regimes.** Regime A labels spots on $n_L$ donors and nothing on the others. Regime B labels $m$ spots on every donor.

**The masking experiment.** Most real-data numbers come from one procedure. Take a task where every spot is in fact measured. Pretend only $n_L$ of the $G$ donors are labelled, chosen at random. Compute the classical and the PPI estimates and their intervals from that subset. Repeat for 200 random choices and for every gene. The spread of the estimates across the 200 draws is the empirical variance. The share of intervals that contain the full-data value is the coverage. A ratio below 1 means PPI has the smaller variance.

**The tasks.** CCRCC (kidney cancer, Visium, 24 donors), Indiana kidney (Visium, 25 donor units), lung Xenium (15 donors), and ACS PUMS 2018 income with states or California PUMAs as clusters. Three image encoders are used as predictors on the HEST tasks (`hoptimus0`, `uni_v2`, `resnet50`).

**The permuted predictor.** A control run beside the encoders. It takes one encoder's predictions and shuffles them across all spots of the task. Each spot then carries a prediction that has nothing to do with it. The shuffled predictions keep the same overall distribution, and in particular the same average level $\nu$, which is not zero because expression on the log scale is positive.

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

Throughout, $r_g(\lambda) = z_g - \lambda f_g$ is a labelled donor's rectifier, and the interval is

$$
\hat\theta \pm t_{n_L - 1}\sqrt{\Big(1 - \frac{n_L}{G}\Big)\frac{s_r^2}{n_L}}, \qquad s_r^2 = \frac{1}{n_L - 1}\sum_{g \in L}\big(r_g - \bar r_L\big)^2 .
$$

**Which $\lambda$ is being fitted, and why each donor gives one data point.** The estimator is a constant plus the average of $r_g(\lambda)$ over a random sample of $n_L$ of the $G$ donors. For a fixed $\lambda$ its variance is the textbook variance of a sample mean drawn without replacement,

$$
\text{Var}(\hat\theta) = \Big(1 - \frac{n_L}{G}\Big)\frac{S_r^2(\lambda)}{n_L}, \qquad S_r^2(\lambda) = S_z^2 - 2\lambda\,S_{zf} + \lambda^2 S_f^2 ,
$$

where $S_z^2$, $S_f^2$ and $S_{zf}$ are the variance of $z_g$, the variance of $f_g$ and their covariance across donors. The second expression is the variance of a difference, expanded. It is a quadratic in $\lambda$, and it is smallest at

$$
\lambda = \frac{S_{zf}}{S_f^2},
$$

which is the slope of the regression of $z_g$ on $f_g$ across donors. From the labelled donors it is estimated by

$$
\hat\lambda = \frac{\sum_{g \in L}(z_g - \bar z_L)(f_g - \bar f_L)}{\sum_{g \in L}(f_g - \bar f_L)^2}.
$$

The data points of this regression are the pairs $(f_g, z_g)$, one pair per donor. A donor's thousands of spot-level pairs $(\hat y_{gi}, y_{gi})$ are all used, but they are used up in computing that donor's two numbers $z_g$ and $f_g$ very precisely. They say nothing about how $z_g$ and $f_g$ move together from one donor to the next, and that co-movement is the only thing the variance above depends on.

One could instead fit a slope to the spot-level pairs inside donors. That slope would be estimated very precisely, and it would be the right one for a different variance. With $m$ labelled spots per donor the variance has two parts, a between-donor part and a within-donor part,

$$
\text{Var}(\hat\theta) \approx \frac{\sigma_{u,r}^2(\lambda)}{n_L} + \frac{\sigma_{e,r}^2(\lambda)}{n_L\,m},
$$

in the notation of A2. The spot-level slope minimises the second part. That part is divided by $m$, which is in the hundreds or thousands, so it is already negligible. The first part is what is left, and only the donor-level slope minimises it. The two slopes can be far apart. This is the same fact as the gain theorem, seen from the side of $\lambda$.

**Why tuning on the same clusters under-covers.** Suppose $\hat\lambda$ is chosen to minimise $s_r^2(\lambda)$ on the labelled donors and the interval then uses $s_r^2(\hat\lambda)$ from the same donors. By construction

$$
s_r^2(\hat\lambda) = \min_\lambda s_r^2(\lambda) \le s_r^2(\lambda^\star)
$$

for the true best value $\lambda^\star$, and $s_r^2(\lambda^\star)$ is an unbiased estimate of the smallest variance any fixed $\lambda$ can reach. So the variance the interval uses is biased downward. The size of the bias is the usual one for a fitted line. A line with a slope and an intercept fitted to $n$ points leaves residuals whose sum of squares has expectation $(n - 2)$ times the error variance, and $s_r^2$ divides by $n - 1$. With four donors the estimated variance is therefore about $2/3$ of what it should be, before counting the extra noise that $\hat\lambda$ itself adds to the estimator (A3). The interval is too narrow and under-covers. This is also why the rules that under-cover look best on width.

**Why cross-fitting repairs it.** Split the labelled donors into halves $A$ and $B$. Fit $\hat\lambda_B$ on half $B$ only and $\hat\lambda_A$ on half $A$ only, and use each on the other half,

$$
\hat\theta = c_U\,\bar F + \frac{1}{n_L}\Big[\sum_{g \in A}\big(z_g - \hat\lambda_B f_g\big) + \sum_{g \in B}\big(z_g - \hat\lambda_A f_g\big)\Big], \qquad c_U = \frac{\hat\lambda_A + \hat\lambda_B}{2}
$$

for halves of equal size. The donors in $A$ played no part in choosing $\hat\lambda_B$. So once $\hat\lambda_B$ is given, the rectifiers $z_g - \hat\lambda_B f_g$ for $g \in A$ are a random sample with a fixed coefficient. Their average is unbiased and their sample variance is honest, with no minimisation over the same data.

**Why the finite-population correction.** When the population is the $G$ donors at hand and we label $n_L$ of them without replacement, the estimate becomes exact as $n_L$ approaches $G$. That is the factor $(1 - n_L/G)$ in the variance above, a textbook result I do not derive here. Round 3's variance had no such factor, so with 12 of 24 donors labelled it was twice too large. That, and not anything about $\lambda$, was the over-coverage.

**Why $\lambda = 0$ below six clusters.** The rule is "fewer than 6", so it applies at 4 and at 5 labelled clusters. Four was only the example in my first version.

With four labelled clusters each half has two. The fitted slope from two donors, with points $(f_1, z_1)$ and $(f_2, z_2)$, is

$$
\hat\lambda = \frac{z_1 - z_2}{f_1 - f_2},
$$

the slope of the straight line through the two points. That is what I meant by a slope through two points. The line passes through both exactly, so there is nothing left over to show how noisy it is. When the predictor is useless, the numerator and the denominator are two unrelated differences, and their ratio can be anything. It is then clipped to $[0, 1]$ and applied to the other half, where it adds $\hat\lambda f_g$ of pure noise to each donor.

The simulation shows the consequence. At four clusters the cross-fitted interval still covers 0.90, because cross-fitting keeps the variance estimate honest. But it is 1.32 times as wide as the classical one when the predictor is uninformative, and 1.01 times as wide when the predictor is informative. So at four clusters tuning can only lose. The classical estimator is used there by rule.

Six is where the rule stops because it is the smallest number that gives each half three donors, and three points is the fewest for which a fitted line leaves a residual. Five would split into two and three, so it is treated like four.

**The extra variance term under cross-fitting.** This one is new to round 4's last unit, so I go through it step by step.

Step 1. With cross-fitting, each labelled donor $g$ has its own weight $\lambda_g$, which is $\hat\lambda_B$ if $g$ is in half $A$ and $\hat\lambda_A$ if it is in half $B$. The weight on the population prediction term is the average of these over the labelled donors,

$$
c_U = \frac{1}{n_L}\sum_{g \in L}\lambda_g .
$$

Step 2. The estimator is

$$
\hat\theta = c_U\,\bar F + \frac{1}{n_L}\sum_{g \in L}\big(z_g - \lambda_g f_g\big).
$$

Step 3. Substitute the definition of $c_U$ into the first term. It becomes a sum over the same labelled donors, so the two pieces combine into one average,

$$
\hat\theta = \frac{1}{n_L}\sum_{g \in L}\big(z_g - \lambda_g\,(f_g - \bar F)\big).
$$

This step is one line of rearrangement and nothing is skipped.

Step 4. So each labelled donor contributes $z_g - \lambda_g f_g + \lambda_g \bar F$. The variance formula we had used only $z_g - \lambda_g f_g$ and left out $\lambda_g \bar F$.

Step 5. When every donor has the same $\lambda$, the left-out piece is the same constant for everyone and does not affect a variance. When the two halves have different $\lambda$, the pieces $z_g - \lambda_g f_g$ differ between the halves by about $(\hat\lambda_A - \hat\lambda_B)\,\bar F$, even though the estimator itself does not vary that way. The old formula read that difference as genuine between-donor variance.

Step 6. The size of the error is governed by how large the level $\bar F$ is against the spread of $f_g$ between donors. For the slope $\theta_3$ on the HEST tasks the weights are centred and $\bar F$ is small, so the error was small. On ACS income for the mean the level is large and the error was enormous. The old interval's estimated variance was 204 to 1,069 times the empirical variance. With the term added it is 0.89 to 1.04 times (`results/round4/ppi/Q5a/q5a_design_variance_before_after.csv`). On the HEST tasks the fix moves coverage by at most 0.025.

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

**A control that changed how we read the tables.** The permuted predictor gives a ratio of 1.00 to 1.05 on the donor-weighted estimands on the HEST tasks and 0.96 to 1.07 on the census tasks, as it should. On the spot-weighted estimands it gives 0.29 to 0.40 on CCRCC, 0.09 to 0.13 on lung and essentially zero on ACS states $\theta_2$, which there is the mean (`results/round4/ppi/Q5a/q5a_spot_weighted_permuted.csv`). A predictor with no information cannot halve a variance. So every spot-weighted PPI row in our tables is marked as a nuisance row and none is counted as a gain.

### Why we looked for it

The originality check found that the estimator is textbook, so the paper needs a statement of its own. Round 3 had shown a symptom with no named cause. The encoders have a decent unit-level correlation with expression, and yet PPI's interval was only 0.85 to 0.89 as wide as the classical one. The theorem names the cause. It is also the statement any user of PPI with clustered data needs before spending a labelling budget, whatever the application.

### How we obtained it

Three ways. A derivation in the standard random-effects model. A simulation in which $R^2_{\text{cluster}}$ is set to 0.8, 0.5 and 0.2 and the empirical variance ratio is compared with the formula. And the masking experiment on the six task variants, with $R^2_{\text{cluster}}$ measured separately on all donors.

### The theory

**Step 1, the model.** Split each donor's contribution and its predicted counterpart into a population average and a donor-specific part,

$$
z_g = \theta + u_g, \qquad f_g = \bar F + p_g .
$$

Here $u_g$ is how far donor $g$'s true contribution sits from the average over donors, and $p_g$ is the same for its predicted contribution. Both have mean zero across donors by construction. Write

$$
\sigma_u^2 = \text{Var}(u_g), \qquad \sigma_p^2 = \text{Var}(p_g), \qquad C_u = \text{Cov}(u_g, p_g), \qquad R^2_{\text{cluster}} = \frac{C_u^2}{\sigma_u^2\,\sigma_p^2}.
$$

$R^2_{\text{cluster}}$ is the squared correlation, across donors, between the true and the predicted contributions.

When only $m$ spots of a labelled donor are measured, the donor's contribution is itself estimated, and a unit-level part appears,

$$
\hat z_g = \theta + u_g + \bar e_g, \qquad \hat f_g = \bar F + p_g + \bar d_g, \qquad \text{Var}(\bar e_g) = \frac{\sigma_e^2}{m}, \quad \text{Var}(\bar d_g) = \frac{\sigma_d^2}{m}, \quad \text{Cov}(\bar e_g, \bar d_g) = \frac{C_e}{m}.
$$

For the plain mean this is the familiar model $y_{gi} = \mu + u_g + e_{gi}$ and $\hat y_{gi} = \nu + p_g + d_{gi}$ on the slide.

**Step 2, the rectifier inherits the same split.**

$$
\hat z_g - \lambda \hat f_g = (\theta - \lambda\bar F) + (u_g - \lambda p_g) + (\bar e_g - \lambda \bar d_g).
$$

The first bracket is a constant. The second varies between donors. The third is within-donor sampling noise.

**Step 3, the variance for a fixed $\lambda$.** The estimator is a constant plus the average of the rectifier over $n_L$ independent labelled donors, so its variance is the rectifier's variance divided by $n_L$,

$$
\text{Var}(\hat\theta_\lambda) = \frac{\sigma_{u,r}^2(\lambda)}{n_L} + \frac{\sigma_{e,r}^2(\lambda)}{n_L\,m},
$$

$$
\sigma_{u,r}^2(\lambda) = \sigma_u^2 - 2\lambda C_u + \lambda^2\sigma_p^2, \qquad \sigma_{e,r}^2(\lambda) = \sigma_e^2 - 2\lambda C_e + \lambda^2\sigma_d^2 .
$$

Each of the two is the variance of a difference, expanded. The classical estimator is $\lambda = 0$, with variance $\sigma_u^2/n_L + \sigma_e^2/(n_L m)$. I leave the term for the unlabelled donors to step 6.

**Step 4, many spots per donor.** With $m$ in the hundreds or thousands the second term is negligible in both, and

$$
\frac{\text{Var}(\hat\theta_\lambda)}{\text{Var}(\hat\theta_0)} \longrightarrow \frac{\sigma_u^2 - 2\lambda C_u + \lambda^2\sigma_p^2}{\sigma_u^2}.
$$

This is the whole mechanism. Spots within a donor are plentiful, so anything the predictor gets right spot by spot was already averaged away for free. The only uncertainty left is which donors we happened to label, and predictions help only by explaining why one donor differs from another.

**Step 5, the best $\lambda$.** The numerator is a quadratic in $\lambda$. Its derivative is $-2C_u + 2\lambda\sigma_p^2$, which is zero at

$$
\lambda^\star = \frac{C_u}{\sigma_p^2},
$$

the slope of the regression of $u_g$ on $p_g$ across donors. Substituting back,

$$
\sigma_{u,r}^2(\lambda^\star) = \sigma_u^2 - \frac{C_u^2}{\sigma_p^2} = \sigma_u^2\big(1 - R^2_{\text{cluster}}\big),
$$

so the ratio at the best $\lambda$ is

$$
1 - R^2_{\text{cluster}} .
$$

**Step 6, the term for the unlabelled clusters, under the superpopulation target.** There the estimator's first piece is $\lambda \bar f_U$, an average over $G_U$ unlabelled donors that are themselves a sample. It has variance $\lambda^2\sigma_p^2/G_U$ at large $m$, and it is independent of the labelled donors, so it adds to step 3. The ratio becomes

$$
\frac{\sigma_u^2 - 2\lambda C_u + \lambda^2\sigma_p^2}{\sigma_u^2} + \frac{n_L}{G_U}\cdot\frac{\lambda^2\sigma_p^2}{\sigma_u^2}.
$$

At $\lambda^\star$ the last term is $(n_L/G_U)\,R^2_{\text{cluster}}$, since $\lambda^{\star 2}\sigma_p^2/\sigma_u^2 = R^2_{\text{cluster}}$. So the ratio is

$$
1 - R^2_{\text{cluster}} + \frac{n_L}{G_U}\,R^2_{\text{cluster}},
$$

and it reaches $1 - R^2_{\text{cluster}}$ only when there are many more unlabelled than labelled clusters. If one minimises the whole expression over $\lambda$ instead, the minimiser is $\lambda^\star\,G_U/(G_U + n_L)$. I skip that minimisation, which is the same kind as step 5.

**Step 7, the design-based target has no such term.** There $\bar F$ is a known number, not an estimate. By the variance formula at the start of A1's theory the ratio is exactly $S_r^2(\lambda)/S_z^2$, and its minimum is one minus the squared correlation of $z_g$ and $f_g$ over the $G$ donors, reached at $\lambda = S_{zf}/S_f^2$.

This distinction cost us a correction during the round. The first tuning rule chose $\lambda$ to minimise a variance that included the unlabelled-cluster term, which shrinks $\lambda$ by the factor $G_U/(G_U + n_L)$. On the design-based target that shrinkage is wrong. With 12 of 15 lung donors labelled it multiplies $\lambda$ by $3/15$, and the gain almost disappears. Under the first rule the lung ratio for `hoptimus0` was 0.63 with 8 labelled donors and 0.87 with 12. Under the corrected rule, which tunes on the labelled donors' rectifier variance alone, it is 0.43 and 0.41 (`q4a_table61.csv`).

**Step 8, what "cluster-level" means for a slope or a difference.** This was step 7 in the first version.

For $\theta_3$ the donor's contribution is its own slope, $z_g = \beta_g$, and its predicted contribution is the slope of the predictions, $f_g = \hat\beta_g$. So

$$
u_g = \beta_g - \theta, \qquad p_g = \hat\beta_g - \bar F, \qquad R^2_{\text{cluster}} = \text{Corr}_g\big(\beta_g, \hat\beta_g\big)^2 .
$$

The cluster-level accuracy that matters is whether the predictor knows which donors have a steeper slope than others. It is not whether the predictor gets each donor's overall expression level right.

The second point follows from the weights summing to zero. Add any constant $c_g$ to all of donor $g$'s predictions. Then

$$
f_g^{\text{new}} = \frac{1}{M_g}\sum_i w_{gi}\,(\hat y_{gi} + c_g) = f_g + \frac{c_g}{M_g}\sum_i w_{gi} = f_g + 0 .
$$

A donor-level offset in the predictions, which is the kind of error a slide or batch effect produces, does not change $f_g$ at all, so it cannot affect these estimators. One consequence is that recalibrating donor offsets cannot help, and when we tried it, it did not (Part B). For the plain mean the weights sum to $M_g$, the same line gives $f_g^{\text{new}} = f_g + c_g$, and offsets matter in full.

**The simulation check.** With $\lambda$ fixed at its best value, the empirical ratio matches the formula of step 6 to within 0.03 in every cell. With 100 unlabelled clusters and 5,000 units per cluster it sits 0.03 to 0.08 above $1 - R^2_{\text{cluster}}$, which is the size of the unlabelled-cluster term (`results/round4/ppi/Q2_theory/theorem_v3/q2_sim_theorem_v3.csv`).

**The permuted predictor on the donor-weighted estimands.** After shuffling, a spot's prediction is unrelated to its nuclear area. So the slope of the shuffled predictions on nuclear area inside a donor, $f_g = \hat\beta_g$, is zero apart from noise of order $1/\sqrt{M_g}$, and that noise is unrelated to the donor's true slope. Then $C_u \approx 0$, $R^2_{\text{cluster}} \approx 0$ and the best $\lambda$ is zero. The theorem says the ratio should be 1. The measured $R^2_{\text{cluster}}$ of the permuted predictor is 0.00 to 0.04 and its ratio is 1.00 to 1.05 on the HEST tasks. This is the control behaving as it should.

**The permuted predictor on the spot-weighted estimands, and why those rows are a nuisance.** In the spot-weighted design-based estimator a donor enters through its total $Z_g = \sum_i w_{gi}\,y_{gi}$, with weights that do not sum to zero. Split each outcome into the overall level $\mu$ and the rest, and do the same for the predictions with their level $\nu$,

$$
Z_g = \mu\,W_g + \sum_i w_{gi}\,(y_{gi} - \mu), \qquad F_g = \nu\,W_g + \sum_i w_{gi}\,(\hat y_{gi} - \nu), \qquad W_g = \sum_i w_{gi}.
$$

Both totals contain the same donor-level quantity $W_g$, multiplied by a level. For the slope, $W_g = M_g(\bar x_g - \bar x)/v$. For the mean, $W_g = M_g$, the donor's size.

Now shuffle the predictions. The second part of $F_g$ becomes pure noise. The first part, $\nu W_g$, is untouched, because shuffling does not change the average level $\nu$. So across donors

$$
\text{Cov}_g(Z_g, F_g) \approx \mu\,\nu\,\text{Var}_g(W_g) \ne 0,
$$

and the rectifier is

$$
Z_g - \lambda F_g = (\mu - \lambda\nu)\,W_g + \text{the rest}.
$$

Choosing $\lambda = \mu/\nu$ removes the $W_g$ term completely. The shuffled predictions have about the same average as the outcomes, so $\mu/\nu$ is near 1. This is what the data show. On the spot-weighted slope the permuted predictor's $\hat\lambda$ is 0.86 to 0.92 on CCRCC and 0.95 to 0.98 on lung, and its variance ratio is 0.29 to 0.40 and 0.09 to 0.13. On the census mean by state, where $W_g$ is the number of people sampled in the state and varies enormously, the ratio is 0.0003 (`results/round4/ppi/Q5a/q5a_spot_weighted_permuted.csv`).

The variance reduction is real for that estimator. What makes the rows a nuisance is where it comes from. It comes from $W_g$, which is known for every donor without any prediction, and a "predictor" that returned the same constant for every spot would deliver it just as well. So a small ratio on a spot-weighted row is no evidence that the encoder predicts expression, and it cannot be compared with the donor-weighted rows, where a useless predictor gains nothing. The classical estimator in those rows is also a weak baseline, since a classical estimator that used $W_g$ would remove the same variance. That last sentence is standard survey reasoning and my reading. We did not build that baseline. Coverage on these rows is also below nominal, 0.84 to 0.875 for the slope on CCRCC and lung.

The lesson for the paper is about the choice of estimand, and the practical rule is that a PPI gain should always be reported beside a permuted predictor's.

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

I work in the textbook form with every spot of a labelled donor measured, and use the split of A2, $z_g = \theta + u_g$ and $f_g = \bar F + p_g$, where $u_g$ and $p_g$ have mean zero across donors.

**Three different $\lambda$.** They are easy to mix up.

- $\lambda^\star = C_u/\sigma_p^2$ is the best $\lambda$. It is a property of the population of donors, the slope of the true regression of $u_g$ on $p_g$. Nobody knows it. In a simulation we do know it, because we chose $C_u$ and $\sigma_p^2$, and the simulation's "oracle" arm uses it.
- $\hat\lambda$ is the estimated $\lambda$, the same slope computed from the few labelled donors we have. It is a random quantity. It changes with which donors were labelled.
- $\bar\lambda = E[\hat\lambda]$ is the average value of the estimate over repeated samples. It can differ from $\lambda^\star$, for example because $\hat\lambda$ is clipped to $[0, 1]$.

The error of the estimate is summarised by

$$
\text{MSE}(\hat\lambda) = E\big[(\hat\lambda - \lambda^\star)^2\big] = \text{Var}(\hat\lambda) + (\bar\lambda - \lambda^\star)^2 .
$$

**Step 1, the estimator's error in terms of $u_g$ and $p_g$.** Take a fixed $\lambda$ first. Substitute $z_g = \theta + u_g$ and $f_g = \bar F + p_g$ into the estimator,

$$
\hat\theta - \theta = \lambda\bar F + \frac{1}{n_L}\sum_{g \in L}\big(\theta + u_g - \lambda\bar F - \lambda p_g\big) - \theta = \frac{1}{n_L}\sum_{g \in L}\big(u_g - \lambda p_g\big).
$$

The constants $\theta$ and $\lambda\bar F$ cancel. This is why the first piece of the estimator is there. What is left is the average of the centred rectifier $u_g - \lambda p_g$.

With cross-fitting the same substitution, using step 3 of A1's last derivation, gives

$$
\hat\theta - \theta = \frac{1}{n_L}\Big[\sum_{g \in A}\big(u_g - \hat\lambda_B\,p_g\big) + \sum_{g \in B}\big(u_g - \hat\lambda_A\,p_g\big)\Big] = \frac{\bar r_A + \bar r_B}{2},
$$

where $\bar r_A = \frac{1}{n_h}\sum_{g \in A}(u_g - \hat\lambda_B\,p_g)$ is half $A$'s average, $n_h = n_L/2$, and $\bar r_B$ is defined the same way.

**Step 2, why each term has mean zero given $\hat\lambda_B$.** This is the sentence that was unclear. Fix a donor $g$ in half $A$. The coefficient $\hat\lambda_B$ was computed from half $B$ only, so it is independent of $(u_g, p_g)$. Conditioning on it therefore leaves the distribution of $(u_g, p_g)$ unchanged, and $\hat\lambda_B$ can be treated as a constant,

$$
E\big[u_g - \hat\lambda_B\,p_g \,\big|\, \hat\lambda_B\big] = E[u_g] - \hat\lambda_B\,E[p_g] = 0 - \hat\lambda_B \cdot 0 = 0 .
$$

Both zeros are the definition of $u_g$ and $p_g$ as deviations from the donor average. The "rectifier of mean zero" in my first version was this centred quantity. The uncentred rectifier $z_g - \hat\lambda_B f_g$ has mean $\theta - \hat\lambda_B\bar F$, which is not zero, and step 1 is what removes it.

The independence is essential. If $\hat\lambda$ had been computed from donor $g$ itself, $E[\hat\lambda\,p_g]$ would not factor into $E[\hat\lambda]\,E[p_g]$, and the term would not have mean zero. That is the algebraic form of A1's argument for cross-fitting.

By the same reasoning the conditional variance of one term is the variance of a difference with a fixed coefficient,

$$
\text{Var}\big(u_g - \hat\lambda_B\,p_g \,\big|\, \hat\lambda_B\big) = \sigma_u^2 - 2\hat\lambda_B\,C_u + \hat\lambda_B^2\,\sigma_p^2 ,
$$

and since half $A$'s donors are independent of each other,

$$
E\big[\bar r_A \,\big|\, \hat\lambda_B\big] = 0, \qquad \text{Var}\big(\bar r_A \,\big|\, \hat\lambda_B\big) = \frac{\sigma_u^2 - 2\hat\lambda_B\,C_u + \hat\lambda_B^2\,\sigma_p^2}{n_h}.
$$

**Step 3, remove the conditioning.** The law of total variance says

$$
\text{Var}(\bar r_A) = E\big[\text{Var}(\bar r_A \mid \hat\lambda_B)\big] + \text{Var}\big(E[\bar r_A \mid \hat\lambda_B]\big).
$$

The second term is the variance of a constant, zero. For the first, take the expectation of the conditional variance over $\hat\lambda_B$, using $E[\hat\lambda_B] = \bar\lambda$ and $E[\hat\lambda_B^2] = \text{Var}(\hat\lambda) + \bar\lambda^2$,

$$
\text{Var}(\bar r_A) = \frac{\sigma_u^2 - 2\bar\lambda\,C_u + \bar\lambda^2\sigma_p^2 + \text{Var}(\hat\lambda)\,\sigma_p^2}{n_h}.
$$

The first three terms are the variance the rectifier would have with the coefficient fixed at $\bar\lambda$. The fourth is new. It is there because $E[\hat\lambda^2]$ exceeds $(E[\hat\lambda])^2$ by the variance of $\hat\lambda$.

**Step 4, measure from the minimum.** A quadratic can be rewritten around its minimum. Here

$$
\sigma_u^2 - 2\bar\lambda\,C_u + \bar\lambda^2\sigma_p^2 = \sigma_u^2\big(1 - R^2_{\text{cluster}}\big) + (\bar\lambda - \lambda^\star)^2\,\sigma_p^2 .
$$

I skip the check, which is expanding the right side with $C_u = \lambda^\star\sigma_p^2$. Putting this into step 3 and collecting the two terms that multiply $\sigma_p^2$,

$$
\text{Var}(\bar r_A) = \frac{\sigma_u^2\big(1 - R^2_{\text{cluster}}\big) + \text{MSE}(\hat\lambda)\,\sigma_p^2}{n_h}.
$$

**Step 5, the ratio.** The classical estimator on the same half is the average of $u_g$ over $n_h$ donors, with variance $\sigma_u^2/n_h$. Dividing,

$$
\frac{\text{Var}(\bar r_A)}{\sigma_u^2/n_h} = \underbrace{1 - R^2_{\text{cluster}}}_{\text{the floor of A2}} + \underbrace{\text{MSE}(\hat\lambda)\,\frac{\sigma_p^2}{\sigma_u^2}}_{\text{the cost of tuning}} .
$$

In words, a noisy $\lambda$ adds noise to the estimator in proportion to how much the predicted contributions vary between donors. Each donor's correction is $\hat\lambda\,p_g$, so an error in $\hat\lambda$ is multiplied by $p_g$.

**Step 6, both halves together.** The full error is $(\bar r_A + \bar r_B)/2$, so

$$
\text{Var}\Big(\frac{\bar r_A + \bar r_B}{2}\Big) = \frac{\text{Var}(\bar r_A) + \text{Var}(\bar r_B)}{4} + \frac{\text{Cov}(\bar r_A, \bar r_B)}{2}.
$$

The two halves are not independent, since each one's coefficient comes from the other. The theory document expands the covariance term by term and finds that it is of order $1/n_h^2$, against $1/n_h$ for the variances. I skip that expansion. Dropping it,

$$
\text{Var}(\hat\theta) \approx \frac{\text{Var}(\bar r_A)}{2} = \frac{\sigma_u^2\big(1 - R^2_{\text{cluster}}\big) + \text{MSE}(\hat\lambda)\,\sigma_p^2}{n_L},
$$

and the ratio to the classical $\sigma_u^2/n_L$ is the same as in step 5. Averaging the halves restores the full sample size $n_L$. It does not reduce the tuning cost, because each half is still corrected with a coefficient estimated from only $n_h$ donors.

**Step 7, when predictions pay for their own tuning.** The ratio is below 1 when the cost is smaller than the gain,

$$
\text{MSE}(\hat\lambda)\,\frac{\sigma_p^2}{\sigma_u^2} < R^2_{\text{cluster}} .
$$

Since $R^2_{\text{cluster}} = \lambda^{\star 2}\sigma_p^2/\sigma_u^2$, this is the same as

$$
\text{MSE}(\hat\lambda) < \lambda^{\star 2} .
$$

Predictions help exactly when $\lambda$ is estimated with an error smaller than its own size.

**Step 8, the break-even count.** To turn this into a number of clusters we need $\text{Var}(\hat\lambda)$. For an unclipped least-squares slope fitted to $n_h$ points with normally distributed $p_g$, the slope is unbiased, so the MSE is the variance, and the variance is a standard regression result that I take as given,

$$
\text{Var}(\hat\lambda) = \frac{\text{residual variance}}{(n_h - 3)\,\sigma_p^2} = \frac{\sigma_u^2\big(1 - R^2_{\text{cluster}}\big)}{(n_h - 3)\,\sigma_p^2}.
$$

The residual variance is $\sigma_u^2(1 - R^2_{\text{cluster}})$ by step 5 of A2. The $n_h - 3$ is what the expectation of one over the sum of squares of $p_g$ works out to. Multiplying by $\sigma_p^2/\sigma_u^2$, the tuning cost is

$$
\frac{1 - R^2_{\text{cluster}}}{n_h - 3}.
$$

The condition of step 7 becomes

$$
\frac{1 - R^2_{\text{cluster}}}{n_h - 3} < R^2_{\text{cluster}} \quad\Longleftrightarrow\quad n_h > 2 + \frac{1}{R^2_{\text{cluster}}} \quad\Longleftrightarrow\quad n_L > 4 + \frac{2}{R^2_{\text{cluster}}} .
$$

The middle step is two lines of rearrangement, and the last uses $n_L = 2n_h$. For example, $R^2_{\text{cluster}} = 0.44$ gives $n_L > 8.5$, and $R^2_{\text{cluster}} = 0.2$ gives $n_L > 14$.

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

**The two $R^2$ values.** Take all spots of all donors and look at the per-spot pairs $(z_{gi}, f_{gi})$. Their variation splits into two levels.

- Between donors. Each donor has one pair of averages $(z_g, f_g)$. $R^2_{\text{cluster}}$ is the squared correlation of these pairs across the $G$ donors,

$$
R^2_{\text{cluster}} = \text{Corr}_g\big(z_g, f_g\big)^2 = \frac{C_u^2}{\sigma_u^2\,\sigma_p^2}.
$$

  It asks whether the predictor knows which donors are high and which are low.

- Within donors. Subtract each donor's average from its spots, leaving $z_{gi} - z_g$ and $f_{gi} - f_g$. $R^2_{\text{within}}$ is the squared correlation of these deviations over all spots,

$$
R^2_{\text{within}} = \frac{\Big(\sum_g\sum_i (z_{gi} - z_g)(f_{gi} - f_g)\Big)^2}{\sum_g\sum_i (z_{gi} - z_g)^2\ \sum_g\sum_i (f_{gi} - f_g)^2} = \frac{C_e^2}{\sigma_e^2\,\sigma_d^2}.
$$

  It asks whether, inside one donor, the predictor knows which spots are high and which are low.

The two are separate properties. A predictor can rank spots well inside every donor and still be wrong about every donor's level, or the reverse. On our data, for `hoptimus0`, they are 0.29 and 0.37 on CCRCC, 0.19 and 0.28 on Indiana, and 0.73 and 0.83 on lung (`q2_cluster_r2.csv`). The ordinary correlation that benchmarks report mixes the two levels.

**The estimator in regime B.** Every donor has $m$ labelled spots, a random subset $S_g$ of its $M_g$. The donor's contribution is estimated by the same difference estimator, applied inside the donor,

$$
\hat z_g = \lambda\,f_g + \frac{1}{m}\sum_{i \in S_g}\big(z_{gi} - \lambda f_{gi}\big),
$$

where $f_g$ is known exactly because every spot is predicted. The estimand and its estimator are

$$
\theta = \frac{1}{G}\sum_{g=1}^{G} z_g, \qquad \hat\theta_B = \frac{1}{G}\sum_{g=1}^{G}\hat z_g .
$$

**Step 1, regime B's variance under the design-based target.** The $G$ donors are the population and all of them are in the sample. So the only thing that is random is which spots were drawn inside each donor. For one donor, $\hat z_g$ is a constant plus the mean of $m$ values of $r_{gi} = z_{gi} - \lambda f_{gi}$ drawn without replacement from $M_g$, so by the same textbook formula as in A1

$$
\text{Var}(\hat z_g) = \Big(1 - \frac{m}{M_g}\Big)\frac{S_{r,g}^2}{m}, \qquad S_{r,g}^2 = \text{the variance of } r_{gi} \text{ among donor } g\text{'s spots}.
$$

The draws in different donors are independent, so the variances add,

$$
\text{Var}(\hat\theta_B) = \frac{1}{G^2}\sum_{g=1}^{G}\Big(1 - \frac{m}{M_g}\Big)\frac{S_{r,g}^2}{m}.
$$

This is the variance of a stratified sample with donors as strata.

**Step 2, donor-level quantities vanish.** $S_{r,g}^2$ is a variance taken inside one donor. Anything that is the same for all of a donor's spots drops out of it, including the donor's true level $u_g$ and any donor-level error of the predictor $p_g$. Expanded,

$$
S_{r,g}^2(\lambda) = S_{z,g}^2 - 2\lambda\,S_{zf,g} + \lambda^2 S_{f,g}^2 ,
$$

with all three computed from within-donor deviations. So $R^2_{\text{cluster}}$, which was everything in regime A, does not appear at all.

**Step 3, the best $\lambda$ and the ratio.** Take the donors to be of similar size, so the factors $(1 - m/M_g)$ are about equal and come out of the sum. Then the variance is proportional to

$$
\sum_g S_{r,g}^2(\lambda) = \sigma_e^2 - 2\lambda\,C_e + \lambda^2\sigma_d^2
$$

up to a constant, where $\sigma_e^2$, $\sigma_d^2$ and $C_e$ are the pooled within-donor variances and covariance. This is the same quadratic as in A2 with the within-donor quantities in place of the between-donor ones. Its minimum is at

$$
\lambda_w = \frac{C_e}{\sigma_d^2}, \qquad \text{with value } \sigma_e^2\big(1 - R^2_{\text{within}}\big).
$$

The classical estimator is $\lambda = 0$ with value $\sigma_e^2$, so

$$
\frac{\text{Var}_B(\text{PPI})}{\text{Var}_B(\text{classical})} = 1 - R^2_{\text{within}} .
$$

A width ratio is the square root of a variance ratio, which gives the predictions $\sqrt{1 - R^2_{\text{within}}}$ quoted above.

**Step 4, regime B under the superpopulation target.** If the donors are a sample from a wider population, each donor's true contribution $z_g = \theta + u_g$ is itself one random draw, and averaging $G$ of them leaves

$$
\text{Var}_B^{\text{super}} = \frac{\sigma_u^2}{G} + \text{Var}(\hat\theta_B) .
$$

No predictor can reduce the first term. It is the spread of the true donor values.

**Step 5, the two regimes at an equal number of labelled spots.** Let $N_{\text{lab}}$ be the number of labelled spots, so regime A has $n_L$ donors with $N_{\text{lab}}/n_L$ spots each and regime B has $G$ donors with $N_{\text{lab}}/G$ each. From step 3 of A2 and step 4 here, at the best $\lambda$ of each and ignoring the finite-population factors,

$$
\text{Var}_A \approx \frac{\sigma_u^2\big(1 - R^2_{\text{cluster}}\big)}{n_L} + \frac{\sigma_{e,r}^2}{N_{\text{lab}}}, \qquad \text{Var}_B \approx \frac{\sigma_u^2}{G} + \frac{\sigma_e^2\big(1 - R^2_{\text{within}}\big)}{N_{\text{lab}}}.
$$

The second terms are both a unit-level variance over the same $N_{\text{lab}}$. The first terms are where the regimes differ. Regime B's is smaller when

$$
\frac{\sigma_u^2}{G} < \frac{\sigma_u^2\big(1 - R^2_{\text{cluster}}\big)}{n_L} \quad\Longleftrightarrow\quad R^2_{\text{cluster}} < 1 - \frac{n_L}{G}.
$$

With 8 of 24 donors this is $R^2_{\text{cluster}} < 0.67$, which every Visium encoder satisfies. That is the reason regime B wins there. It divides the donor-level variance by all $G$ donors. Regime A divides a reduced variance by only $n_L$, and the reduction $1 - R^2_{\text{cluster}}$ is not large enough to make up for it. Regime A also carries the unlabelled-cluster term of A2, which I left out and which only makes it worse. Under the design-based target the comparison is more one-sided still, because regime B's first term is absent.

**Step 6, the allocation formula.** Now let labels cost money. A donor costs $c_d$ to include and each labelled spot costs $c_s$. With $n$ donors and $m$ spots on each, the total cost is

$$
C_{\text{tot}} = n\,(c_d + c_s\,m).
$$

The classical variance with $n$ donors and $m$ spots each is $\sigma_u^2/n + \sigma_e^2/(n\,m)$. Fix $C_{\text{tot}}$, so $n = C_{\text{tot}}/(c_d + c_s m)$, and substitute,

$$
\text{Var}(m) = \frac{(c_d + c_s\,m)\Big(\sigma_u^2 + \dfrac{\sigma_e^2}{m}\Big)}{C_{\text{tot}}} = \frac{c_d\sigma_u^2 + c_s\sigma_e^2 + c_s\sigma_u^2\,m + c_d\sigma_e^2/m}{C_{\text{tot}}}.
$$

Two of the four terms depend on $m$. One rises with $m$, since more spots per donor means fewer donors. One falls with $m$. Setting the derivative to zero,

$$
c_s\sigma_u^2 - \frac{c_d\sigma_e^2}{m^2} = 0 \quad\Longrightarrow\quad m^\star = \sqrt{\frac{c_d}{c_s}\cdot\frac{\sigma_e^2}{\sigma_u^2}} .
$$

This is the classical two-stage sampling result. Spend more spots per donor when donors are expensive or when spots inside a donor vary a lot, and fewer when donors differ a lot from each other.

With a predictor, the variance has the same form with the rectifier's two variances from step 3 of A2 in place of the outcome's, so

$$
m^\star_{\text{PPI}} = \sqrt{\frac{c_d}{c_s}\cdot\frac{\sigma_{e,r}^2}{\sigma_{u,r}^2}} .
$$

**Step 7, which way a predictor moves the optimum.** Comparing the two formulas, $m^\star_{\text{PPI}} \le m^\star$ exactly when

$$
\frac{\sigma_{e,r}^2}{\sigma_e^2} \le \frac{\sigma_{u,r}^2}{\sigma_u^2},
$$

that is, when the predictor removes at least as large a share of the within-donor variance as of the between-donor variance. At $\lambda^\star$ the right side is $1 - R^2_{\text{cluster}}$. The left side is the within-donor quadratic of step 3 evaluated at $\lambda^\star$ and not at its own minimiser $\lambda_w$, so by the same rewriting as step 4 of A3 it equals

$$
1 - R^2_{\text{within}} + (\lambda^\star - \lambda_w)^2\,\frac{\sigma_d^2}{\sigma_e^2}.
$$

So the condition is

$$
R^2_{\text{within}} - (\lambda^\star - \lambda_w)^2\,\frac{\sigma_d^2}{\sigma_e^2} \ \ge\ R^2_{\text{cluster}} .
$$

A predictor moves the best design toward more donors with fewer spots each when it ranks spots inside donors better than it ranks donors, by a margin that covers the mismatch between the two levels' best $\lambda$. On our data the within-donor $R^2$ exceeds the cluster-level one for every HEST encoder except `uni_v2` on CCRCC. My Q3 memo stated this without the exception and the session corrected it.

### What to keep in mind

Two things, and the second matters for the slide.

Regime B was only run at the budget grid's values, so its smallest setting is 6 spots per donor on Indiana, 14 on CCRCC and 36 on lung.

The permuted predictor also narrows the regime B interval. Its width ratio is 0.87 on CCRCC against 0.80 to 0.84 for the encoders, 0.66 on lung against 0.42 to 0.49, and 0.15 on ACS states against 0.08 (`results/round4/ppi/Q4_tables/q4_main_table.csv`). The reason is the same kind as the nuisance rows of A2, one level down. Inside a donor the per-spot values are

$$
z_{gi} = w_{gi}\,y_{gi}, \qquad f_{gi} = w_{gi}\,\hat y_{gi} .
$$

Write $y_{gi} = \mu_g + (y_{gi} - \mu_g)$ with $\mu_g$ the donor's mean expression, and the same for the prediction with its mean $\nu_g$. Then

$$
z_{gi} = \mu_g\,w_{gi} + \dots, \qquad f_{gi} = \nu_g\,w_{gi} + \dots
$$

Both contain the weight $w_{gi}$ times a level, and $w_{gi}$ varies from spot to spot. So across the spots of one donor $z_{gi}$ and $f_{gi}$ are correlated through $w_{gi}$ even when the prediction carries no information, as long as its level $\nu_g$ is not zero. The weights summing to zero does not help here, because this is a correlation across spots and not a sum over them. The measured within-donor $R^2$ of the permuted predictor on this scale is 0.24 on CCRCC and 0.57 on lung, and step 3 then predicts width ratios of 0.87 and 0.65, which is what it gets.

So on the Visium tasks most of regime B's gain over the classical estimator comes from knowing the weights, and only the step from 0.87 to about 0.83 comes from the encoder. On lung the encoder's share is large. I am reading this from the tables. No unit of the round was set up to test it, so treat it as a reading and not as an established result. It does not affect the comparison of regime B against regime A.


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

**A result of our own for very few donors.** By "our own" I mean that it is not in the HCP paper or the GHCP paper. The conformal session derived it during the scoping, and I checked the algebra. The literature check says the first half follows closely from known results, so it is a short proposition and not a headline.

It concerns the case $K + 1 < 1/\alpha$, which at 90% means 8 or fewer calibration donors. There HCP always returns an infinite set, which is useless. The question was whether that is HCP's fault or whether any valid method must do something like it. The answer has two parts, stated precisely in the theory below.

- Every valid method must sometimes return an infinite set. The probability of that cannot be pushed below $1 - \alpha(K+1)$, and a randomised version of HCP reaches exactly that value.
- A valid method that always returns a finite set must cover more than $1 - \alpha$, by a computable amount.

At 90% the first number is 0.5, 0.4, 0.3, 0.2 and 0.1 for $K$ = 4 to 8. The second, the smallest coverage a finite method can have, is 0.951, 0.923, 0.910, 0.903 and 0.901 for the same $K$ (`results/round4/conformal/C2_candidates/lower_bound/c2_lb_beta_star.csv`). So with very few donors a study cannot have a set that is both always finite and exactly at the nominal level. It has to give up one or the other.

### Why we looked for it

The originality check found that GHCP had taken the labelled-test-spots setting six weeks before us. Two things were left. One was practical. A reader of our paper needs to know what a valid prediction set costs at the numbers of donors and labelled spots a real study has, and GHCP's paper does not map that. The other was theoretical. With no labelled test spots, is HCP's conservatism forced or could a cleverer method do better? That question got a three-day scoping with a stop rule, not a track.

### How we obtained it

First a simulation testbed with a known oracle, on which the released GHCP code was reproduced and four candidate methods of our own were tested against a criterion fixed in advance. None passed (Part B). Then the real-data map on CCRCC, Indiana, lung and ACS, where every comparison is made within the same task, encoder, fold, calibration draw and label draw, so that only the method differs. The lower-bound work is pen and paper with a small numerical table.

### The theory

**Why a few labelled spots do not help at $K = 10$.** GHCP's construction sets one calibration donor aside to restore exchangeability between the test donor, which has $o$ labelled spots, and the calibration donors, which have many. With 10 calibration donors that leaves 9, which is exactly the edge $K + 1 = 1/\alpha$ where the hierarchical quantile is at its most conservative. And five labelled spots carry too little information about the test donor to buy that back. With more donors, or with 25 or more labelled spots, GHCP improves, as its paper shows. This is how our reports describe the mechanism. I have not rederived GHCP's guarantee.

**Why the within-donor split needs about 10 spots.** It is ordinary split conformal with $n = o$ calibration points, all from the test donor, so they are exchangeable with that donor's other spots and the guarantee is the standard one. The half-width is the $k$-th smallest of the $o$ errors with

$$
k = \lceil (1 - \alpha)(o + 1) \rceil ,
$$

and it exists only when $k \le o$. At $\alpha = 0.1$, $o = 8$ gives $k = \lceil 8.1 \rceil = 9 > 8$, and $o = 9$ gives $k = 9$. So it is finite from $o = 9$. The recentred variant spends half the labelled spots on estimating the donor's offset and calibrates on the rest, so it needs about twice as many, and on our grid it is finite from 25.

**The setting for the lower bound.** A method takes the calibration data $D$ from $K$ donors, possibly with some extra randomness, and returns a half-width $\hat q$, which may be $+\infty$. The test spot has error $S$ and is covered when $S \le \hat q$. Each donor has its own distribution of errors, and the donors' distributions are independent draws from some law $\Pi$ over distributions. The method is valid if

$$
P_\Pi\big(S \le \hat q\big) \ge 1 - \alpha \qquad \text{for every } \Pi .
$$

The words "for every $\Pi$" are what the argument uses. A valid method has to cover under any law we care to construct, including very artificial ones.

HCP gives each calibration donor weight $1/(K+1)$ and keeps $1/(K+1)$ at infinity for the unseen donor. Its quantile is finite only if the finite weight $K/(K+1)$ reaches $1 - \alpha$, that is if $K + 1 \ge 1/\alpha$.

**The forced infinite set** (Proposition 2 in the lower-bound document)**.** If $K + 1 < 1/\alpha$, then for every valid method there is a law $\Pi$ under which

$$
P\big(\hat q = \infty\big) \ge 1 - \alpha\,(K + 1) .
$$

Step 1. Choose a very simple family of laws. Every donor's errors are all equal to a single number $X_j$, and the numbers $X_1, \dots, X_{K+1}$ are independent draws from a continuous distribution. The problem is then to give an upper bound for $X_{K+1}$ after seeing $X_1, \dots, X_K$.

Step 2. By symmetry each of the $K + 1$ numbers is equally likely to be the largest, so

$$
P\big(X_{K+1} > \max(X_1, \dots, X_K)\big) = \frac{1}{K + 1}.
$$

Step 3. A finite $\hat q$ cannot reliably cover a new maximum. Whatever rule produces a finite $\hat q$ from the $K$ numbers, one can choose the continuous distribution so that a value exceeding all $K$ of them almost always exceeds $\hat q$ too. The idea is to stretch the scale above each observed value, since the rule cannot know how far above the largest value the next one may fall. The construction is written out in `docs/round4_conf_lower_bound.md`, section 8.1, and I skip it. Its conclusion is that, for any small $\eta$, there is such a distribution with

$$
P\big(X_{K+1} \le \hat q \,\big|\, \hat q < \infty\big) \le \frac{K}{K+1} + \eta .
$$

Step 4. Let $\pi = P(\hat q = \infty)$. An infinite set always covers. A finite one covers with probability at most $K/(K+1)$, letting $\eta$ go to zero. So

$$
\text{coverage} \le \pi + (1 - \pi)\,\frac{K}{K+1} .
$$

Validity requires the left side to be at least $1 - \alpha$. Solving $\pi + (1 - \pi)\frac{K}{K+1} \ge 1 - \alpha$ for $\pi$, which is two lines, gives

$$
\pi \ge 1 - \alpha\,(K+1) .
$$

When $K + 1 \ge 1/\alpha$ the right side is zero or negative and the statement says nothing.

Step 5, the bound is reached. Take HCP at the level it can afford, $K/(K+1)$, which is finite. Return $+\infty$ with probability $\pi = 1 - \alpha(K+1)$ and that finite half-width otherwise. Its coverage is at least

$$
\pi + (1 - \pi)\,\frac{K}{K+1} = 1 - \alpha(K+1) + \alpha K = 1 - \alpha ,
$$

so it is valid, and it is infinite exactly as often as the bound requires. HCP as usually run is infinite with probability 1 here, so it does more than is forced.

**The coverage floor for finite methods** (Proposition 1 in the lower-bound document)**.** Let a method be valid, and let $\Pi_0$ be any law under which it always returns a finite set. Write its coverage under $\Pi_0$ as $1 - \beta$. Then, when $K + 1 < 1/\alpha$,

$$
\beta \le \beta^\star = 1 - \frac{K}{K+1}\,\big(\alpha\,(K+1)\big)^{-1/K},
$$

and $\beta^\star$ is smaller than $\alpha$. The method must over-cover.

Step 1, contaminate. Build a new law from $\Pi_0$ by mixing in, with small probability $\varepsilon$, a donor whose errors are all larger than some huge number $M$.

Step 2. With probability $(1 - \varepsilon)^K$ none of the $K$ calibration donors is of the huge kind. Then the calibration data look exactly as under $\Pi_0$, and so does $\hat q$, which is finite.

Step 3. In that case the test donor is ordinary with probability $1 - \varepsilon$, and is missed with probability $\beta$. It is of the huge kind with probability $\varepsilon$, and is then missed almost surely once $M$ is large enough, because $\hat q$ is finite. So the probability of a miss under the mixed law is at least

$$
h_\beta(\varepsilon) = (1 - \varepsilon)^K\,\big[(1 - \varepsilon)\,\beta + \varepsilon\big] .
$$

Step 4. The method is valid under the mixed law as well, so $h_\beta(\varepsilon) \le \alpha$ for every $\varepsilon$ between 0 and 1.

Step 5. Take the $\varepsilon$ that makes $h_\beta$ largest. This is a calculus exercise that I skip. The largest value is

$$
\max_\varepsilon h_\beta(\varepsilon) = \frac{1}{K+1}\left(\frac{K}{(1 - \beta)(K+1)}\right)^{K} .
$$

Setting this equal to $\alpha$ and solving for $\beta$ gives $\beta^\star$ above.

In words, a method that is always finite on ordinary data is exposed to the rare donor it has never seen. To stay valid when such donors are mixed in, it must have had coverage to spare on the ordinary data.

**What stays open.** For $K + 1 \ge 1/\alpha$, which includes $K = 10$, neither argument forces anything. The scoping found a rule that is valid and narrower than HCP when the donors look alike, but it is wider than HCP when they differ, so it does not dominate. Whether anything valid beats HCP by a real margin there is open. For ordinary data without groups, Tibshirani, Barber and Ramdas (August 2026) have settled the matching question. For grouped data nobody has. You asked for this to be pursued, and for the two propositions to be checked properly against the literature. Both are in the handoff.

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

## The word "cost", in its four uses

I used "cost" and "price" for four different things. Two are about money and two are about statistical precision. They should not be confused, and on the slides each should be named in full.

| name | what is paid | measured in | where |
|---|---|---|---|
| labelling cost | money or effort to obtain labels | $c_d$ per donor, $c_s$ per spot | A4 |
| tuning cost | precision lost by estimating $\lambda$ | added to the variance ratio | A3 |
| unlabelled-cluster term | precision lost by estimating the mean prediction | added to the variance ratio | A2 |
| price of validity | width paid for a guarantee | a ratio of widths | A5 |

**1. Labelling cost.** This is the only one that is a cost in the everyday sense. Including a donor costs $c_d$, which stands for everything that is paid once per donor (consent, tissue, preparing and running a slide). Labelling one more spot on a donor already included costs $c_s$. A design with $n$ donors and $m$ labelled spots on each costs

$$
C_{\text{tot}} = n\,(c_d + c_s\,m).
$$

Only the ratio $c_d/c_s$ matters for which design is best, as the formula for $m^\star$ shows. Related phrases I used.

- "Equal budget" or "equal number of labelled spots" means $c_d = 0$. Only spots are counted.
- "A donor charged at 10 spots" means $c_d/c_s = 10$. We ran 10, 100 and 1,000.
- "Crossover cost ratio" is the value of $c_d/c_s$ above which regime A becomes the better choice, because regime B has to pay $c_d$ for all $G$ donors.
- "Affordable" means the budget covers the donor costs at all. Regime B needs $G\,c_d \le C_{\text{tot}}$ before it can label a single spot.

These cost ratios are hypothetical. Nobody gave us prices. And there is a practical point I should have raised earlier. On Visium a whole capture area is measured in one run, so I do not think a laboratory can buy "14 spots on this donor" at a per-spot price. Regime B fits naturally where units really are bought one at a time, such as survey respondents, or platforms that profile chosen regions. Whether and how it maps onto spatial transcriptomics in practice is a question for David. It affects how the design result is presented, so it is worth asking before the talk.

**2. Tuning cost.** This is statistical. It is the term

$$
\text{MSE}(\hat\lambda)\,\frac{\sigma_p^2}{\sigma_u^2}
$$

that estimating $\lambda$ adds to the variance ratio (A3, step 5). Nothing is paid in money. It is paid in precision, and it shrinks as more clusters are labelled. "Predictions pay for their own tuning" means the gain $R^2_{\text{cluster}}$ is larger than this term.

**3. The unlabelled-cluster term.** Also statistical. Under the superpopulation target the average prediction is itself estimated from $G_U$ unlabelled clusters, which adds $(n_L/G_U)\,R^2_{\text{cluster}}$ to the ratio (A2, step 6). The theory document calls it the cost of estimating the prediction mean. It is absent under the design-based target.

**4. Price of validity.** This belongs to the prediction sets. It is how much wider a set with a coverage guarantee is than a reference set without one,

$$
\text{price} = \frac{\text{width of the valid set}}{\text{width of the reference set}} .
$$

On real data the reference is the naive pooled interval, so HCP's price at $K = 10$ on CCRCC is 1.95. In the simulation the reference is the oracle interval that knows the true distribution. Related phrases.

- "The cheapest valid set" means the narrowest set that still has a guarantee. No money is involved.
- "GHCP's donation costs one reference group" means its construction sets aside one calibration donor, which leaves fewer to calibrate on.

**How the first and the others meet.** The paper's design question is the only place where money and precision are traded against each other. Given $c_d/c_s$ and a budget, choose $n$ and $m$ to get the smallest variance, where the variance includes the tuning cost. The joint table of A6 adds the fourth to the same choice, by asking how narrow a valid prediction set the same $m$ spots per donor can buy.

---

# Part B. Results not on the slides

Each is one paragraph. All are in the track reports with their files.

**PPI track.**

- **A pre-test for $\lambda$ was tried and dropped.** The rule set $\lambda$ to zero unless its estimate exceeded one or two standard errors. On real data it did worse than plain cross-fitting, for example a ratio of 1.17 against 1.03 on CCRCC `uni_v2` with 16 donors. The draws that pass a pre-test are the ones with a large estimated slope, so the pre-test selects a biased $\lambda$. The break-even rule replaced it. I had proposed the pre-test.
- **No bootstrap is used.** In the simulation the percentile cluster bootstrap covers 0.76 with four clusters and 0.84 with eight. The wild cluster bootstrap did not beat the plain cluster-robust interval either.
- **Unequal cluster sizes.** For the superpopulation target the Bell and McCaffrey CR2 variance removes the coverage loss that the simpler CR1 variance shows when cluster sizes differ, 0.88 against 0.85.
- **A coverage shortfall no interval removes.** For the spot-weighted slope the classical interval covers 0.84 in the hardest simulation cells even though its variance estimate is right on average. The donor contributions are skewed, so the $t$ reference is wrong. This is recorded as a limit of the definition.
- **The clipped $\hat\lambda$ often reads exactly 0.5.** The two halves frequently clip at 0 and at 1, and their average is 0.5. The tables now carry the unclipped value with its standard error, which is 0.47 to 0.67 with standard errors of 0.39 to 0.85 on CCRCC and Indiana.
- **Recalibrating donor offsets does not help.** A ridge model predicting each donor's offset from its mean embedding has no out-of-sample skill, and by step 8 of A2 it could not have changed the slope estimands anyway.
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

**To be pursued, at your request of 4 October.**

- Whether HCP can be beaten at $K + 1 \ge 1/\alpha$. This is open. For data without groups the matching question was settled in August 2026 by Tibshirani, Barber and Ramdas. For grouped data it has not been addressed, and that is the form in which we would pursue it.
- Whether the two small-$K$ propositions of A5 are new. This has not been checked beyond the papers named in the session's instruction. The literature check of 4 October suggests the forced-infinite-set statement is close to a corollary of known results and found the coverage floor nowhere, but it read summaries of pages and not the papers.

**Not established, and not yet planned.**

- The final design-based tuning rule and the corrected variance were never run in simulation. Their behaviour is known from 200 masking draws per cell on real data.
- On the real tasks the final design-based interval covers 0.85 to 0.89, a little under 0.90. We have not explained the remaining shortfall.
- Regime B below 6 spots per donor on HEST was not run.
- Whether regime B can be bought on a spatial transcriptomics platform at all, and at what cost per donor and per spot, is not known to us (see the section on cost).
- The break-even rule explains the pattern across tasks and does not predict individual cells.
- The reading in A4 that most of regime B's gain on Visium comes from the weights and not the encoder is my reading of the tables, with no dedicated check.
- A classical baseline that uses the weight sums $W_g$, against which the spot-weighted rows could be judged fairly, has not been built. Nor has a spot-weighted estimand under which PPI gains are real. Both are candidates for round 5.
