> **Reference document, dated 29 September 2026.** Written by the oversight chat in answer to Nicolas's list of nineteen concepts. Section 4's proposed correction to the PPI track was applied to the track document on 30 September.

# The round-4 concepts, explained

29 September 2026. Written by the oversight chat for Nicolas, answering the list in `ST_confused.pdf`, in its order. Derivations are done step by step. Where my earlier wording was loose or wrong, this document says so and corrects it.

---

# Part 1. Prediction-powered inference and where it comes from

## 1a. The survey-sampling difference estimator

Survey sampling starts from a different picture than most of statistics. There is a fixed, finite population of $N$ units, say every household in a state. Each unit $i$ has a value $y_i$ we care about (income) that is expensive to measure, and we want the population mean $\bar Y = \frac{1}{N}\sum_{i=1}^N y_i$. Nothing about $y$ is random. The only randomness is which units we choose to measure. We draw a sample $s$ of $n$ units by a known random design (simple random sampling, say), measure $y$ on them, and estimate $\bar Y$. Statements like "unbiased" and "variance" refer to averaging over all the samples the design could have drawn. This is called design-based inference.

Now suppose we also have, for every unit in the population, a cheap auxiliary number $\hat y_i$ that is related to $y_i$. In a 1970s survey that might be last census's income for the household; today it could be a machine-learning prediction. The difference estimator is

$$\hat{\bar Y}_{\text{diff}} = \frac{1}{N}\sum_{i=1}^{N}\hat y_i + \frac{1}{n}\sum_{i \in s}\big(y_i - \hat y_i\big).$$

Read it in two parts. The first term is the average of the cheap numbers over everyone, which is precise but biased by however much $\hat y$ misses on average. The second term estimates that average miss from the sample and corrects for it.

It is unbiased whatever $\hat y$ is. Under simple random sampling each unit is in the sample with probability $n/N$, so the sample mean of any quantity is unbiased for its population mean. Apply that to $y_i - \hat y_i$:

$$\mathbb{E}_{\text{design}}\Big[\frac{1}{n}\sum_{i\in s}(y_i - \hat y_i)\Big] = \frac{1}{N}\sum_{i=1}^N (y_i - \hat y_i).$$

Add the first term, which is not random, and the $\hat y$ parts cancel, leaving $\bar Y$. Its variance is the sampling variance of the correction term alone,

$$\text{Var}\big(\hat{\bar Y}_{\text{diff}}\big) = \Big(1 - \frac{n}{N}\Big)\frac{S^2_{y - \hat y}}{n},$$

where $S^2_{y-\hat y}$ is the population variance of the differences and $1 - n/N$ is the finite-population correction. Compare the plain sample mean, whose variance is $(1 - n/N)\,S^2_y/n$. The difference estimator wins exactly when $S^2_{y - \hat y} < S^2_y$, that is when $\hat y$ tracks $y$. This is Cassel, Särndal and Wretman (1976).

Now look at prediction-powered inference. PPI has a labelled set $L$ of $n$ units with $y$ and a large unlabelled set $U$ of $N$ units with only $\hat y$, and its mean estimator is

$$\hat\theta_{\text{PP}} = \frac{1}{N}\sum_{i\in U}\hat y_i + \frac{1}{n}\sum_{i \in L}\big(y_i - \hat y_i\big).$$

It is the same formula. The only difference is the philosophy. PPI imagines $L$ and $U$ as independent random draws from an infinite population (a superpopulation) and uses ordinary i.i.d. asymptotics; the survey version fixes the population and randomises the sample. Both give the same estimator and, for large $N$, the same variance.

## 1b. Mozer, March 2026

Reagan Mozer's note (arXiv:2603.19160, "PPI is the Difference Estimator") makes exactly the observation in 1a and 1c formally, and argues the two communities should read each other. For us the consequence is concrete. Everything survey sampling knows about the difference estimator applies to PPI, and survey sampling has known for decades how that estimator behaves under cluster sampling, two-stage sampling and stratification, including optimal allocation of a sample between clusters and units within clusters. So the estimator we are using, and even the form of its variance under clustering, is not something we can claim. What survey sampling did not have is a machine-learned auxiliary whose errors have a particular structure, and the design questions that structure raises. That is where our results live.

## 1c. PPI++ and the generalised regression estimator

The difference estimator trusts $\hat y$ at full strength. If $\hat y$ is on the wrong scale (say it is systematically twice the truth), subtracting it at full strength adds noise. The fix is to use a scaled version $\lambda\hat y$ and choose $\lambda$ from the data:

$$\hat\theta(\lambda) = \frac{\lambda}{N}\sum_{i\in U}\hat y_i + \frac{1}{n}\sum_{i \in L}\big(y_i - \lambda\hat y_i\big).$$

This is still unbiased for every fixed $\lambda$, by the same cancellation as in 1a. In survey sampling, choosing $\lambda$ by regressing $y$ on $\hat y$ in the sample gives the regression estimator, and its general form with several auxiliaries is the generalised regression (GREG) estimator (Särndal, Swensson and Wretman 1992). PPI++ (Angelopoulos, Duchi and Zrnic 2023) chooses $\lambda$ to minimise the estimator's variance, which gives a slightly shrunken regression coefficient (derived in 3c). Mozer's point is that PPI++ is, in substance, the regression or GREG estimator.

## 1d. Model-assisted estimation, and a machine-learned auxiliary variable

There are two ways to use a model in survey estimation.

**Model-based.** Assume the model is true and estimate from it. If the model is wrong, the estimate is biased and the interval is wrong.

**Model-assisted.** Use the model only to build a more efficient estimator, while validity comes from the random design. The difference and GREG estimators are model-assisted. If the model is good, the variance drops. If the model is bad, the estimator is still unbiased and its interval still valid; it is just no more precise than ignoring the model.

"Auxiliary variable" is survey language for a quantity known for every unit in the population, as opposed to $y$, known only on the sample. Classically these were census counts or administrative records. A "machine-learned auxiliary variable" is simply a prediction $\hat y_i$ from a trained model, available for every unit. Breidt and Opsomer (Statistical Science 2017) review model-assisted estimation with modern predictors such as random forests. PPI is model-assisted estimation where the auxiliary is a machine-learning prediction. In our setting the auxiliary is the gene-expression prediction from the H&E image, known for every spot.

## 1e. Chen, Guo and Li, March 2026

Their paper (arXiv:2603.16041) answers a planning question. How many labelled units do I need for a PPI test to reach a given power? The core of it is a variance ratio. With $N$ large and $\lambda$ at its optimum, the PPI variance is $\text{Var}(y - \lambda^\star\hat y)/n$, and

$$\text{Var}(y - \lambda^\star\hat y) = \text{Var}(y)\big(1 - \text{Corr}^2(y, \hat y)\big) = \text{Var}(y)\,(1 - R^2).$$

(Derivation in 3c.) So PPI needs about $(1 - R^2)$ times as many labelled units as the classical estimator for the same precision. A predictor with $R^2 = 0.5$ halves the labelling cost. Their setting is i.i.d. units. Our contribution is what replaces this $R^2$ when units come in clusters, which is the gain theorem.

## 1f. Our topic, piece by piece

"PPI under cluster sampling" means the labelled units are not a random sample of individual units but whole clusters (donors) with all or many of their units (spots). The labelled donors are random; the spots inside a labelled donor are not independent draws, because they share the donor.

"The split of a labelling budget between clusters and units per cluster when predictions are available" is the design question. Suppose measuring expression has a fixed cost per donor (tissue acquisition, a slide run) and a smaller cost per spot. With a budget, you can label a few donors deeply or many donors shallowly. Survey sampling answers this without predictions. We answer it with predictions, and the answer changes (section 3).

"The behaviour of the estimator with few labelled clusters" refers to the fact that with 4 to 12 labelled donors, the usual large-sample normal approximation is poor. The variance estimate rests on a handful of donor totals, the reference distribution has to be $t$ with few degrees of freedom, and the choice of $\lambda$ becomes noisy. Q1 of the PPI track measures all of that.

## 1g. The motivation from round 3, stated more carefully than I did

I wrote that round 3 showed "modest gains despite decent unit-level Pearson, and slide offsets of half a standard deviation". The second half is strong evidence. The first half is weak, and I should not have leaned on it.

**The slide offsets are the real evidence.** For each test slide, A2 computed $b_s = \bar y_s - \bar{\hat y}_s$, the average miss of the predictor over that slide, and standardised it by the spread of expression. On unit-calibrated slides the mean of $|b_s|/s_y$ was about 0.52, with both signs. So on a typical slide, the predictor's average is half a standard deviation away from the truth's average, in a direction that varies from slide to slide. That is a cluster-level error, meaning an error shared by every spot on the slide. Averaging over thousands of spots does nothing to it, because every spot carries the same offset.

**The "modest gains" part is not a clean test.** PPI widths were 0.85 to 0.89 of classical, a variance ratio of about 0.72 to 0.79. Unit-level Pearson per gene is about 0.3 to 0.4, so unit-level $R^2$ is about 0.09 to 0.16, which would predict a variance ratio of 0.84 to 0.91. The observed gain was, if anything, larger than unit-level $R^2$ predicts. But the estimand was a slope with morphology weighting, the unlabelled term was included, and $\lambda$ was tuned on the spot-level variance, so the comparison is not like for like. The honest statement is that round 3 did not test the gain theorem. Q2's prediction 1 does, by measuring unit-level and cluster-level $R^2$ directly and setting them beside the observed variance ratio.

## 1h. The gain theorem and the regime comparison

**The setting.** $G$ clusters, each with $m$ units. Write the outcome as a cluster mean plus a within-cluster deviation, $y_{gi} = \mu + u_g + e_{gi}$, with between-cluster variance $\sigma_u^2$ and within-cluster variance $\sigma_e^2$. Write the prediction the same way, $\hat y_{gi} = \nu + p_g + d_{gi}$, with its own cluster part $p_g$ and within part $d_{gi}$. Let $Y_g = \mu + u_g$ and $P_g = \nu + p_g$ be the true and predicted cluster means.

**Regime A, a few clusters fully labelled.** Label $n_L$ clusters with $m$ units each. The PPI estimator's labelled term is an average of rectifiers $r_{gi} = y_{gi} - \lambda\hat y_{gi}$. Split the rectifier the same way:

$$r_{gi} = \underbrace{(u_g - \lambda p_g)}_{\text{cluster part}} + \underbrace{(e_{gi} - \lambda d_{gi})}_{\text{within part}} + \text{constant}.$$

Averaging over $m$ units in each of $n_L$ independent clusters, the variance of the labelled term is

$$\text{Var}_L = \frac{\text{Var}(u_g - \lambda p_g)}{n_L} + \frac{\text{Var}(e_{gi} - \lambda d_{gi})}{n_L\, m}.$$

This is the two-stage sampling formula. The first piece comes from which clusters happened to be labelled; the second from which units inside them.

The classical estimator is the same thing with $\lambda = 0$:

$$\text{Var}_{\text{cl}} = \frac{\sigma_u^2}{n_L} + \frac{\sigma_e^2}{n_L\,m}.$$

Now let $m$ grow. The second pieces are divided by $m$ and vanish, so

$$\frac{\text{Var}_L}{\text{Var}_{\text{cl}}} \;\longrightarrow\; \frac{\text{Var}(u_g - \lambda p_g)}{\sigma_u^2}.$$

The numerator is the variance of "true cluster mean minus $\lambda$ times predicted cluster mean". It is smallest at $\lambda = \text{Cov}(u_g, p_g)/\text{Var}(p_g)$, and at that value (the same algebra as 3c),

$$\text{Var}(u_g - \lambda p_g) = \sigma_u^2\,\big(1 - \text{Corr}^2(Y_g, P_g)\big) = \sigma_u^2\,(1 - R^2_{\text{cluster}}).$$

So the variance ratio tends to $1 - R^2_{\text{cluster}}$, where $R^2_{\text{cluster}}$ is the squared correlation between the true and predicted cluster means across clusters.

**Why, in words.** With many units per cluster, each labelled cluster's own mean is known essentially exactly. What remains uncertain is which clusters you happened to label, because the clusters differ from each other. The rectifier can remove that uncertainty only to the extent that the predictions already know how the clusters differ. A predictor that ranks spots perfectly within each slide but gets every slide's average wrong knows nothing about how the slides differ, so it buys nothing.

**The whole curve, not just the limit.** At $m = 1$ every cluster contributes one unit and cluster sampling is ordinary i.i.d. sampling. Then the ratio is $1 - R^2_{\text{unit}}$, the Chen, Guo and Li result. As $m$ grows the ratio moves from $1 - R^2_{\text{unit}}$ toward $1 - R^2_{\text{cluster}}$. How fast depends on the between-cluster share. The theorem is the statement that it is the cluster-level quantity that matters for any realistic $m$.

**Two cautions the paper must state.** First, the unlabelled term has its own variance, roughly $\lambda^2\,\text{Var}(p_g)/G_U$, which vanishes only if the number of unlabelled clusters is large, not merely the number of unlabelled units. With 12 to 18 unlabelled donors it does not vanish. Second, $R^2_{\text{cluster}}$ is about the true cluster means. Correlating observed cluster means with a finite $m$ attenuates it, which is the small-cluster correction in Q2.

**Regime B, a few units in every cluster.** Label $m$ units in each of all $G$ clusters. What the variance is now depends on what you want to estimate, and I was not precise about this in the track document.

- *If the target is the mean over these $G$ clusters* (the design-based view of B2, where the truth is the full-data value of this donor set), then every cluster is observed, so there is no "which clusters" uncertainty at all. The clusters behave like strata. The variance is only the within-cluster part, $\text{Var}(e_{gi} - \lambda d_{gi})/(Gm)$, and the gain from prediction is governed by how well $\hat y$ ranks units within clusters, the within-cluster $R^2$. Cluster-level errors in the predictor are harmless, because the labelled units on each cluster measure that cluster's offset directly.
- *If the target is a superpopulation of donors*, then the $G$ donors are themselves a sample, and the between-donor variance $\sigma_u^2/G$ stays in the variance whatever you do, and predictions cannot reduce it (they are about the same $G$ donors). Regime B still wins on the within part and on degrees of freedom.

So the regime comparison has a clean statement. Regime A's gain is governed by the predictor's cluster-level accuracy, regime B's by its within-cluster accuracy. A pathology foundation model with large slide offsets is exactly the predictor for which regime B is much better. The PPI track's Q3 should state the target for each result; section 4 of this document proposes that edit.

## 1i. What a rectifier is

In the PPI paper, the rectifier is the correction term, the labelled-set average of $y_i - \hat y_i$ (or $y_i - \lambda\hat y_i$). "Rectify" means correct. The first term of the estimator is the prediction-based answer, and the rectifier measures how wrong that answer is on average and removes it. For a general estimand defined by an estimating equation $\psi$, the rectifier is the labelled-set average of $\psi(y_i) - \lambda\psi(\hat y_i)$. When I write "the rectifier's between-cluster variance", I mean the variance across clusters of the cluster-average rectifier, which is $\text{Var}(u_g - \lambda p_g)$ above.

---

# Part 2. Conformal

## 2a. GHCP

Mallick, Tchetgen Tchetgen, Dobriban and Lee (arXiv:2608.15500, August 2026). My summary is from their abstract and introduction; the conformal track implements it from the full paper, and the details below may need correcting when it does.

**The setting.** Grouped data, $K$ reference groups with many observations each, and a new test group from which you already have $o \ge 1$ observations with known $y$. You want intervals for the test group's remaining observations.

**Why HCP cannot just use the $o$ observations.** HCP's guarantee rests on the test group being exchangeable with the reference groups, which requires the test group to be treated exactly like one of them. The reference groups contribute full score distributions; the test group contributes an atom at $+\infty$. If you add the $o$ test observations as calibration data, the test group is now half-observed while every reference group is fully observed, the symmetry breaks, and the guarantee no longer follows.

**Donation.** GHCP restores the symmetry. It picks a reference group at random (among those with more than $o$ observations) and gives the test group that group's size, and handles the reference groups in the matching way, so that from the procedure's point of view the test group and a reference group are again interchangeable. The $o$ observed test points then enter the calibration legitimately.

**Adaptation.** Part of the $o$ observations can be used to fit a test-group-specific adjustment to the score (for example its offset or its scale), and the rest calibrate. This is where the width gain comes from. The between-group variation HCP had to hedge against is precisely the test group's unknown offset and scale, and a few observations reveal them.

**The guarantee.** Finite-sample coverage at least $1 - \alpha$ under a generalised hierarchical exchangeability. The price is conditional on having some test-group data.

## 2b. The webinar

That is an unlucky coincidence and also a useful one. A strong group arriving independently at the same problem is evidence the problem matters, and it tells you the people whose work the paper will be read against. Two practical notes. Dr. Zhu's connection to that series is a channel, and whether to write to Dobriban or Lee (to say you are building on GHCP for spatial data, or to ask about the $o = 0$ question) is a decision for you with David and Dr. Zhu, not for the sessions. And for your finance interest, Dobriban's line of work (conformal, distributed learning, uncertainty quantification) is a close fit, and following it closely is worth the time whatever the project does.

## 2c. What our "small labelled sample on the test slide" idea was

The deployment picture is a pathology lab that has an H&E slide and wants predicted expression for every spot on it. Suppose it can afford to measure expression at a few spots on that same slide, for example with a cheap targeted assay or a small region profiled. Those $o$ measured spots come from the same slide as the spots you want intervals for, so they are exchangeable with them. Calibrating on them needs no assumption about other donors at all, and the interval for the rest of the slide is valid by ordinary split conformal. With $o$ small that interval is noisy, and it ignores everything the other donors could tell you. GHCP is the principled way to combine the two sources, the $K$ reference donors and the $o$ test spots, and it is what the conformal track now uses.

## 2d. The case with no test-group observations

$o = 0$. You have only the H&E of the new donor, no measured expression on it. This is the case of "virtual spatial transcriptomics" on an H&E-only cohort, which is how these predictors are meant to be used in practice. The only information about the new donor's error comes from the $K$ reference donors, and HCP is the known valid method, at twice the width at $K = 10$.

## 2e. A lower bound on the price of validity at small $K$

**The price of validity** of a method is its interval width divided by the width an oracle would use, where the oracle knows the new donor's actual error distribution and uses its exact $(1-\alpha)$ quantile. HCP's price at $K = 10$ is about 2 in our data.

**What a lower bound would say.** "Any method whose coverage is at least $1 - \alpha$ for every hierarchically exchangeable distribution must have expected price at least $B(K, \alpha)$ on some such distribution." If $B$ is close to HCP's price, HCP is essentially optimal and the over-coverage is not a flaw of the method but a law. The practical conclusion would be that nothing done after data collection can fix it, and the only remedies are more donors or test-group labels, which connects directly to the design half of the paper.

**Why it is plausible.** Split conformal with $n$ exchangeable points is already tight in this sense. Its coverage is at least $1 - \alpha$ and at most $1 - \alpha + 1/(n+1)$, and no valid method can do uniformly better. At the group level the same argument suggests that, with $K$ groups and no test data, any valid method has to protect against the test group being worse than every group seen so far with probability about $1/(K+1)$, which is what HCP's atom at $+\infty$ does.

**Why it is hard.** A lower bound has to hold against every method, including ones nobody has thought of, so it is proved by constructing distributions that no method can tell apart from the data but that need different intervals. At the group level the objects are whole within-group distributions, not single numbers, which makes the construction harder than the classical case. The related known results are the impossibility of distribution-free conditional coverage (Vovk 2012; Lei and Wasserman 2014; Foygel Barber, Candès, Ramdas and Tibshirani 2021). The conformal track gives this three days and a stop rule, because it could take three days or three months.

## 2f. The small-$G$ reference

$G$ is the number of clusters (donors). When a confidence interval is built as estimate plus or minus a critical value times a standard error, the critical value depends on how well the standard error is known.

The cluster-robust standard error is computed from $G$ donor totals $S_1, \dots, S_G$ (the derivation from the earlier note on cluster-robust variance). With $G$ large it is known precisely and the critical value is the normal one, 1.645 for 90%. With $G$ small the variance estimate is itself noisy, and the ratio (estimate minus truth) over (estimated standard error) has heavier tails than a normal. In the simplest case, the mean with equal donor sizes, the cluster-robust interval is exactly a one-sample $t$ interval on the $G$ donor means, so the ratio follows $t_{G-1}$. That is the small-$G$ reference, using $t$ with $G - 1$ degrees of freedom instead of the normal. Its critical values at 90% are 2.13 at $G = 5$, 1.83 at $G = 10$, 6.31 at $G = 2$. The $G/(G-1)$ factor in the variance is the matching bias correction, for the same reason a sample variance divides by $n-1$.

Two refinements appear in Q1. CR2 (Bell and McCaffrey 2002) adjusts each donor's contribution for its leverage, which matters when donor sizes are unequal. Satterthwaite degrees of freedom replace $G - 1$ with an estimated effective count that accounts for unequal sizes and, in PPI, for the labelled and unlabelled terms having different numbers of donors.

The same small-number issue appears in conformal as $K$, which is why the two halves of the paper are one story. Few donors limit both how well a confidence interval knows its own width and how much a prediction interval must hedge.

---

# Part 3. The paper

## 3a and 3b. The gain theorem, and a correction to my wording

Both sentences state the theorem of 1h. One word in 3b was wrong. I wrote that "the variance reduction from predictions tends to $1 - R^2_{\text{cluster}}$". The variance *ratio*, PPI over classical, tends to $1 - R^2_{\text{cluster}}$; the *reduction* is $R^2_{\text{cluster}}$. Sentence 3a is the correct form.

A worked example to make it concrete. Suppose between-donor variance is $\sigma_u^2 = 0.4$ and within-donor variance is $\sigma_e^2 = 0.6$ (a between-donor share of 0.4, about what round 2 measured on CCRCC). Suppose the predictor gets donor means only weakly, $R^2_{\text{cluster}} = 0.1$, and ranks spots within a donor reasonably, within-donor $R^2 = 0.4$. Its unit-level $R^2$, pooling the two parts, is then $1 - (0.36 + 0.36)/1.0 = 0.28$. With $n_L = 8$ labelled donors:

| spots per donor $m$ | classical variance | PPI variance | ratio |
|---|---|---|---|
| 1 | $(0.4 + 0.6)/8 = 0.125$ | $(0.36 + 0.36)/8 = 0.090$ | 0.72 |
| 10 | $0.4/8 + 0.6/80 = 0.0575$ | $0.36/8 + 0.36/80 = 0.0495$ | 0.86 |
| 100 | $0.05 + 0.00075 = 0.0508$ | $0.045 + 0.00045 = 0.0455$ | 0.90 |
| large | $0.05$ | $0.045$ | 0.90 |

The PPI rows use $\text{Var}(u - \lambda p) = 0.4 \times (1 - 0.1) = 0.36$ and $\text{Var}(e - \lambda d) = 0.6 \times (1 - 0.4) = 0.36$, taking one $\lambda$ that is near-optimal for both parts for simplicity. At one spot per donor the predictor looks good (a 28% saving, its unit-level $R^2$). At the realistic hundreds of spots per donor it saves 10%, because it barely knows how donors differ. This is the pattern the paper wants to explain.

## 3c. The power-tuning weight $\lambda$

Start from $\hat\theta(\lambda) = \frac{\lambda}{N}\sum_U \hat y_i + \frac{1}{n}\sum_L (y_i - \lambda\hat y_i)$ with $U$ and $L$ independent i.i.d. samples. Its variance is

$$V(\lambda) = \frac{\lambda^2\,\text{Var}(\hat y)}{N} + \frac{\text{Var}(y) - 2\lambda\,\text{Cov}(y,\hat y) + \lambda^2\,\text{Var}(\hat y)}{n}.$$

This is a quadratic in $\lambda$. Set its derivative to zero:

$$\frac{2\lambda\,\text{Var}(\hat y)}{N} + \frac{-2\,\text{Cov}(y,\hat y) + 2\lambda\,\text{Var}(\hat y)}{n} = 0 \;\Longrightarrow\; \lambda^\star = \frac{\text{Cov}(y, \hat y)}{\text{Var}(\hat y)\,(1 + n/N)}.$$

With $N$ much larger than $n$, $\lambda^\star$ is the regression slope of $y$ on $\hat y$. Plugging it back, the labelled term's variance becomes $\text{Var}(y)\big(1 - \text{Corr}^2(y, \hat y)\big)/n$, which is the $1 - R^2$ of 1e.

What $\lambda$ does, in words. It decides how much to trust the predictions. If $\hat y$ is useless, $\text{Cov}(y, \hat y) \approx 0$ and $\lambda^\star \approx 0$, and PPI falls back to the classical estimator, so it can never be much worse than ignoring the predictor. If $\hat y$ is on the wrong scale, $\lambda$ rescales it. In practice $\lambda$ is estimated from the data, which introduces a small optimism that cross-fitting removes.

**Under clustering, which $\lambda$?** The derivation above used the i.i.d. variance. Under cluster sampling with many units per cluster the variance that matters is the cluster part, and minimising $\text{Var}(u_g - \lambda p_g)$ gives $\lambda^\star_{\text{cluster}} = \text{Cov}(u_g, p_g)/\text{Var}(p_g)$, the regression slope of true cluster means on predicted cluster means. That can be very different from the unit-level slope. A predictor that is good within slides and uninformative about slide means has a sizeable unit-level $\lambda$ and a near-zero cluster-level one. Round 3 tuned $\lambda$ on the spot-level variance, which is one of the four soft spots Q1 fixes. Estimating the cluster-level slope from 4 to 12 labelled donors is itself noisy, which is why Q1 compares the rules, including cross-fitting over donors.

## 3d. The $(K, o)$ map

A two-dimensional grid. One axis is $K$, the number of reference donors available for calibration. The other is $o$, the number of labelled spots on the test slide. Each cell records, for the best valid method there (HCP when $o = 0$, GHCP when $o > 0$), its coverage and its price of validity. It is a menu of options for a lab. Moving along $K$ means profiling more donors; moving along $o$ means measuring a few spots on each slide you want to predict. The map says which buys a sharper valid interval for the money, and, set beside the PPI allocation result, what one labelling design buys for confidence intervals and prediction intervals at once.

Its expected shape, from the round-3 results and the GHCP paper, written as predictions and not as results:

| | $K = 5$ | $K = 10$ | $K = 20$ |
|---|---|---|---|
| $o = 0$ | infinite at 90% | about 2.0 | about 1.4 |
| $o = 10$ | moderate | about 1.5 | about 1.3 |
| $o = 50$ | near 1.2 | about 1.15 | about 1.1 |

The row $o = 0$ is where the lower-bound question lives, and the jump from $o = 0$ to a handful of labelled spots is likely the largest step in the map.

---

# 4. One correction to the PPI track document, proposed

Section 1h shows that regime B's variance depends on the target, and that for the design-based target regime B turns clusters into strata and its gain is governed by the within-cluster $R^2$. The PPI track's Q3 derivation should state the target for every result, derive both versions, and add a prediction that regime B's gain tracks within-cluster $R^2$ while regime A's tracks cluster-level $R^2$. That is a sharper and more useful statement than the one currently in the document. I will make the edit if you want it before the tracks start.
