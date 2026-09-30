> **Reference document, dated 27 September 2026.** Written by the oversight chat for Nicolas; every method derived from scratch and every round-3 result read with its file. Not maintained; the round-4 changes are in `../decisions/round4_originality_check.md` and `concepts_explained_round4.md`.

# The methods, what we did with them, and what the data still holds

27 September 2026. Written by the oversight chat for Nicolas, as the reference for deciding how to move forward. Part I explains every method the project has used or has queued, with the derivations done slowly. Part II says what was tried, how, what came out, and what each result implies. Part III lists what has not been tried. Part IV answers the data question. Numbers are from the round-3 reports and their files, quoted at the precision the point needs.

---

# Part I. The methods

## 1. The setting and the notation

A tissue section is a slide. A slide comes from a donor, and some donors contribute several slides. On each slide there are spots, a few hundred to tens of thousands, each with a 224 by 224 pixel image patch and a vector of gene counts. A frozen encoder maps the patch to an embedding $z_i \in \mathbb{R}^d$, with $d$ from 512 to 2560. The target for gene $g$ at spot $i$ is $y_{ig} = \log(1 + \text{count}_{ig})$. The base predictor is a linear head on the first 256 principal components of the standardised embedding, $\hat y_{ig} = a_g + b_g^\top P z_i$, fit by ridge regression with a penalty so small it does nothing. So the whole project sits on a fixed, cheap, linear predictor. Its quality is about $r = 0.3$ to $0.4$ Pearson per gene on average.

The three-level structure, spots inside slides inside donors, is the single fact that everything else turns on. Spots on one slide share the section, the stain, the scanner session and the tissue state; slides from one donor share the donor's biology and, usually, the laboratory that made them.

## 2. Prediction intervals, and what "coverage" means

An interval $C(z)$ for a new spot has coverage $1 - \alpha$ if $\mathbb{P}(y \in C(z)) \ge 1 - \alpha$. The probability is over the draw of the new spot and of the data used to build $C$. This is marginal coverage. It says nothing about any particular slide, gene or region of feature space; an interval can be at 90% marginally while covering 60% on one slide and 99% on another. Conditional coverage, at 90% for every slide or for every value of $\hat y$, is what one would want and is impossible to guarantee without assumptions (Lei, G'Sell, Rinaldo, Tibshirani and Wasserman 2018; Barber, Candès, Ramdas and Tibshirani 2021), so the project measures marginal coverage and then checks it inside strata.

## 3. Split conformal prediction, derived

Take a score that says how badly a prediction missed, for example $s_i = |y_i - \hat y_i|$. Fit the predictor on a proper-training set $T$. On a separate calibration set $C$ of $n$ spots the predictor did not see, compute the scores $s_1, \dots, s_n$. For a new spot with score $s_{n+1}$, the interval is $\{ y : |y - \hat y| \le \hat q \}$ with $\hat q$ chosen from the calibration scores.

Why this works. Suppose the $n + 1$ scores are exchangeable, meaning any reordering of them is equally likely. Then the rank of $s_{n+1}$ among all $n+1$ is uniform on $\{1, \dots, n+1\}$. Let $s_{(k)}$ be the $k$-th smallest calibration score. The new score is at most $s_{(k)}$ exactly when its rank is at most $k$, which has probability $k/(n+1)$. To make that at least $1 - \alpha$, take

$$k = \lceil (n+1)(1-\alpha) \rceil, \qquad \hat q = s_{(k)}.$$

That is the whole guarantee. It is finite-sample, it needs no model to be right, and it needs exactly one thing, exchangeability of the calibration scores with the test score. If ties are absent, coverage is also at most $1 - \alpha + 1/(n+1)$, so the interval is not conservative either.

Two consequences follow. If $k > n$, that is if $(n+1)(1-\alpha) > n$, there is no finite $\hat q$ and the valid interval is the whole line. Rearranged, this happens when $n < (1-\alpha)/\alpha$, which is $n < 9$ at $\alpha = 0.1$. And the guarantee is only as good as the exchangeability. If calibration spots come from one population and test spots from another, the rank of the test score is not uniform and nothing is promised.

## 4. Scores, and what each one can adapt to

The score decides the shape of the interval.

**Absolute residual**, $s = |y - \hat y|$. The interval is $\hat y \pm \hat q$, the same width everywhere. It cannot adapt to a spot whose expression is harder to predict.

**Scaled residual**, $s = |y - \hat y| / \hat\sigma(z)$, with $\hat\sigma$ a second model fit on $T$ to predict the size of the residual from the features. The interval is $\hat y \pm \hat q \, \hat\sigma(z)$, wide where the residual model expects a large miss. This is locally weighted conformal (Lei et al. 2018). Its weakness is that $\hat\sigma$ is a regression that extrapolates. On shifted features it can predict huge or tiny dispersion, and a tiny $\hat\sigma$ on a calibration spot inflates $\hat q$ for everyone.

**Conformalised quantile regression, CQR** (Romano, Patterson and Candès 2019). Fit two quantile regressions on $T$, $\hat q_{\text{lo}}(z)$ at level $\alpha/2$ and $\hat q_{\text{hi}}(z)$ at $1 - \alpha/2$. The naive interval $[\hat q_{\text{lo}}, \hat q_{\text{hi}}]$ has no guarantee, so conformalise it with the score

$$s_i = \max\big( \hat q_{\text{lo}}(z_i) - y_i, \; y_i - \hat q_{\text{hi}}(z_i) \big),$$

which is how far outside the naive interval the truth fell (negative if inside). The calibrated interval is $[\hat q_{\text{lo}} - \hat q, \; \hat q_{\text{hi}} + \hat q]$. It adapts in width and in asymmetry, because the two quantile fits can sit at different distances from the centre.

**Model-based intervals.** A negative-binomial head models the count directly, $\text{count} \sim \text{NB}(\mu(z), \phi_g)$ with variance $\mu + \phi_g \mu^2$, and its central 90% band is an interval with no conformal guarantee. Whether it covers is a question about the model. The probability integral transform $F(y; \hat\mu, \hat\phi)$ is uniform on $[0, 1]$ when the model is right, so a histogram of PIT values on held-out data is the calibration check. Conformalising a model means using $s = |F(y) - 0.5|$ as the score, so the interval is the model's band widened or narrowed until it covers on the calibration set.

**Interval score.** Coverage alone rewards wide intervals. The Winkler or interval score at level $\alpha$ is width plus $\frac{2}{\alpha}$ times the distance by which the truth falls outside, so it penalises both. Width at matched coverage, comparing scores at the level where each actually covers 90%, is the other way to be fair to a narrow interval.

## 5. The anatomy of a coverage failure

When an interval on a slide covers less than nominal, it is either in the wrong place or too narrow. The project separates the two with three diagnostics that use the test labels, so they describe rather than repair. The slide offset $b_s = \bar y_s - \bar{\hat y}_s$, standardised by the target's spread $s_y$, says how far the predictions sit from the truth on average on that slide. The miss asymmetry $(\text{miss}_{\text{above}} - \text{miss}_{\text{below}}) / (\text{miss}_{\text{above}} + \text{miss}_{\text{below}})$ says whether misses are one-sided, which is the signature of a level error. The oracle width ratio $w^\star / \hat w$, where $w^\star$ is the half-width that would give exactly 90% on that slide, says whether the interval is too narrow (ratio above 1) or too wide.

The $R^2$ ladder from round 2 is the same decomposition for a point prediction. With $r$ the Pearson correlation, $\rho = s_{\hat y} / s_y$ the ratio of prediction to target spread and $b$ the offset,

$$R^2 = 2 r \rho - \rho^2 - b^2 / s_y^2,$$

which is maximised at $\rho = r$. The benchmark head has $\rho / r \approx 1.8$, so its predictions are spread almost twice as widely as they should be. High predictions overshoot. That matters for intervals because a symmetric band around an overshooting prediction misses on the high side.

## 6. Covariate shift and weighted conformal

Suppose the calibration and test features come from different distributions, $p_{\text{cal}}(z)$ and $p_{\text{test}}(z)$, but the conditional law of $y$ given $z$ is the same. Then scores are not exchangeable, but Tibshirani, Barber, Candès and Ramdas (2019) showed the guarantee survives if each calibration score is weighted by the density ratio $w(z) = p_{\text{test}}(z) / p_{\text{cal}}(z)$. The weighted quantile puts mass $\tilde w_i = w(z_i) / \big( \sum_j w(z_j) + w(z_{\text{test}}) \big)$ on each calibration score and the remainder on the test point, and $\hat q$ is the smallest $q$ whose cumulative weighted mass reaches $1 - \alpha$.

The ratio has to be estimated. The standard route is a classifier trained to tell calibration from test features; if it outputs $\hat p(\text{test} \mid z)$, then $w(z) \propto \hat p / (1 - \hat p)$. Here is the catch, and it is the one this project hit. Reweighting only works when the two distributions overlap. If the classifier can separate them almost perfectly, the weights concentrate on the handful of calibration spots that look like test spots. The effective calibration size,

$$n_{\text{eff}} = \frac{\big( \sum_i w_i \big)^2}{\sum_i w_i^2},$$

collapses, and the quantile is set by a few points. Weighted conformal is designed for mild shift, and it has no answer when the test population is identifiable from its features.

## 7. Hierarchical data and prediction for a new group

When data come in groups, spots inside slides inside donors, the right notion is hierarchical exchangeability (Dunn, Wasserman and Ramdas, JASA 2023; Lee, Barber and Willett, arXiv:2306.06342). The groups are exchangeable with each other, and within a group the observations are exchangeable, but an observation from one group is not exchangeable with one from another. The question is coverage for an observation from a new group.

The simplest valid method takes one score per group. With $K$ calibration groups that gives $K$ scores, exchangeable with the test group's score, and split conformal applies with $n = K$. The finite-interval condition becomes $K \ge (1-\alpha)/\alpha$, so nine groups at $\alpha = 0.1$ and four at $\alpha = 0.2$. Using one observation per group throws away almost all the data, so Dunn et al. repeat the draw and combine; Lee, Barber and Willett instead give every calibration group total weight $1/(K+1)$ spread evenly over its $N_k$ observations, put the remaining $1/(K+1)$ on the test point as an atom at $+\infty$, and take the weighted quantile. This is hierarchical conformal prediction, HCP. Its coverage is at least $1 - \alpha$ for any $K \ge 1$, and at most $1 - \alpha + 2/(K+1)$ when scores are distinct. The atom at $+\infty$ has mass $1/(K+1)$, so the interval is finite exactly when $1/(K+1) \le \alpha$, the same condition. And at $K = 10$ the upper bound is $0.9 + 2/11 > 1$, which is why HCP can over-cover badly at small $K$ and still be doing what it promises.

The pooled alternative, treating every calibration spot as its own unit and taking the ordinary quantile, has no guarantee for a new group at all. It behaves as if it had thousands of exchangeable scores when it has $K$ exchangeable groups.

## 8. The design effect, derived

This is the confidence-interval side of the same fact. Let $y_{ij}$ be a quantity for spot $j$ in donor $i$, with $n$ donors and $m$ spots each. Write $y_{ij} = \mu + u_i + e_{ij}$ with a donor effect of variance $\sigma_u^2$ and a spot effect of variance $\sigma_e^2$, independent. The between-donor share is $\rho = \sigma_u^2 / (\sigma_u^2 + \sigma_e^2)$, and $\sigma^2 = \sigma_u^2 + \sigma_e^2$ is the total variance of one spot.

The overall mean is $\bar y = \frac{1}{n} \sum_i \big( u_i + \frac{1}{m} \sum_j e_{ij} \big) + \mu$. Its variance is

$$\text{Var}(\bar y) = \frac{\sigma_u^2}{n} + \frac{\sigma_e^2}{nm} = \frac{\sigma^2}{nm} \big( m \rho + (1 - \rho) \big) = \frac{\sigma^2}{nm} \big( 1 + (m-1)\rho \big).$$

The formula that treats all $nm$ spots as independent gives $\sigma^2 / (nm)$, so it is too small by the factor $1 + (m-1)\rho$, the design effect. The effective sample size is

$$n_{\text{eff}} = \frac{nm}{1 + (m-1)\rho} \xrightarrow{m \to \infty} \frac{n}{\rho}.$$

With thousands of spots per donor and $\rho$ around 0.3, $n_{\text{eff}} \approx 3n$ regardless of $m$. Precision is set by the number of donors, and the spot-level standard error is off by a factor of $\sqrt{1 + (m-1)\rho}$, which for $m$ in the thousands is in the tens. Round 3 measured 29 to 68.

## 9. Prediction-powered inference, derived for a mean

The problem. We have a small labelled set $L$ of $n$ units with true $y$ and a large unlabelled set $U$ of $N$ units with only predictions $\hat y$, and we want a confidence interval for $\theta = \mathbb{E}[y]$ that is valid whatever the predictor's quality and narrower than the labelled-only interval when the predictor is good.

The classical estimator is $\hat\theta_{\text{cl}} = \frac{1}{n} \sum_{L} y_i$, with variance $\text{Var}(y)/n$. The naive estimator $\frac{1}{N} \sum_U \hat y_i$ is precise and biased by however much $\hat y$ misses on average. Prediction-powered inference (Angelopoulos, Bates, Fannjiang, Jordan and Zrnic, Science 2023) uses the labelled set to estimate that bias, the rectifier, and subtracts it:

$$\hat\theta_{\text{PP}} = \frac{1}{N} \sum_{U} \hat y_i + \frac{1}{n} \sum_{L} \big( y_i - \hat y_i \big).$$

Its expectation is $\mathbb{E}[\hat y] + \mathbb{E}[y - \hat y] = \mathbb{E}[y]$ whatever $\hat y$ is, so it is unbiased for any predictor. Its variance, with $U$ and $L$ independent, is $\text{Var}(\hat y)/N + \text{Var}(y - \hat y)/n$. When $N$ is large the first term vanishes, and the interval is narrower than classical exactly when $\text{Var}(y - \hat y) < \text{Var}(y)$, that is when the predictor explains some of $y$.

PPI++ (Angelopoulos, Duchi and Zrnic 2023) adds a tuning weight $\lambda$ on the prediction terms,

$$\hat\theta_{\text{PP}}(\lambda) = \frac{\lambda}{N} \sum_{U} \hat y_i + \frac{1}{n} \sum_{L} \big( y_i - \lambda \hat y_i \big),$$

still unbiased for every $\lambda$, with $\lambda = 0$ giving the classical estimator. The variance is $\lambda^2 \text{Var}(\hat y)/N + \text{Var}(y - \lambda \hat y)/n$, a quadratic in $\lambda$ minimised at

$$\lambda^\star = \frac{\text{Cov}(y, \hat y)}{\text{Var}(\hat y) \, (1 + n/N)},$$

so a useless predictor gets $\lambda \approx 0$ and PPI falls back to classical, and a perfect one gets $\lambda \approx 1$. The same construction works for any estimand defined by an estimating equation $\mathbb{E}[\psi(y, m; \theta)] = 0$, replacing $y$ by $\psi$. For a regression slope of $y$ on a morphology covariate $m$, $\psi$ is linear in $y$, so everything above carries over with $y$ replaced by $(m - \bar m) y$.

## 10. Why the PPI variance is wrong here, and the cluster-robust fix

The variances in section 9 treat the labelled spots as independent. They are not. Every spot in a donor shares $u_i$, and the labelled set is a handful of whole donors. The right variance sums the influence contributions within each donor first and then takes the variance across donors. Write $\phi_i$ for spot $i$'s contribution to the estimating equation (for the mean, $\phi_i = y_i - \lambda \hat y_i - \theta$). With $G$ labelled donors and $S_g = \sum_{i \in g} \phi_i$ the donor totals,

$$\widehat{\text{Var}}_{\text{cluster}} = \frac{G}{G - 1} \cdot \frac{1}{n^2} \sum_{g=1}^{G} S_g^2,$$

and the same for the unlabelled term over its own donors. The $G/(G-1)$ factor is the small-sample correction, and with few donors the reference distribution is $t_{G-1}$, not normal (Cameron and Miller 2015; MacKinnon, Nielsen and Webb 2023). This is the Liang and Zeger sandwich, applied to the PPI influence function. With $G = 2$ there is one degree of freedom and no useful interval exists; with $G = 6$ the $t$ reference matters a great deal.

The donor bootstrap resamples donors with replacement and takes percentile intervals. It needs $G$ large enough for the resampled sets to vary; at $G$ of 6 to 12 it under-covers, which round 3 measured.

Two subtleties that surfaced. The optimal $\lambda$ is estimated from a variance, and if that variance is the clustered one with $G = 2$ it can be driven to zero, so $\lambda$ is tuned on the spot-level variance and only the interval uses the clustered one. And for a covariance-type estimand a permuted predictor is not a useless predictor in the spot-weighted population, because the covariate weight $(m - \bar m)$ stays attached; the donor-weighted population, whose unit is the donor, behaves as the theory says.

## 11. Semi-synthetic validation

A coverage claim is a claim about repeated sampling, so it is checked by repeating the sampling. The full dataset defines a truth, $\theta_{\text{full}}$, the estimand computed on every spot of every donor. A partition draws $n_L$ donors as labelled and leaves the rest unlabelled; classical and PPI intervals are computed; whether each covers $\theta_{\text{full}}$ is recorded; 200 partitions give a coverage estimate with Monte Carlo error about 0.02. This is a design-based statement, coverage of this dataset's value over repeated labelling. It does not speak to a superpopulation of donors, which would need a different truth.

## 12. Split designs, size matching and difference lists

The evaluation designs are ways of choosing which spots are held out. Random spot, patient (the benchmark's), audited donor, slide-out, and spatial blocks with a buffer around held-out blocks so no training spot is adjacent to a test spot. Each design removes one more kind of shared information from training. Because the designs give different training-set sizes, proper-training sets are subsampled to the smallest within a fold, so a difference between designs is not a difference in data volume. Before any term from a comparison is named, every variable that differs between its arms is written down. That rule caught the "institution" term in round 1 and the "laboratory" terms in round 3.

## 13. Probes, and variance components

A probe is a linear classifier on the frozen embeddings, trained to predict a label (slide, session, population) under spatial-block cross-validation, reported as balanced accuracy against chance. It measures how much of that label the encoder carries. Regressing out morphology covariates before probing measures how much of the signal is tissue composition. The nested variance decomposition of expression, spot within slide within donor, uses a moment estimator (Henderson's method), and its between-donor share is the $\rho$ of section 8 measured on expression.

---

# Part II. What was tried, how, what came out, what it says

## 14. Round 1 and 2 in one paragraph

The benchmark was replicated exactly (mean absolute difference 0.0002 over 108 encoder-task cells), instrumented so every prediction sits in a table with its spot, slide and donor, and then taken apart. The results that carried forward are that split design matters 1.6 times more than encoder choice, that donor identity and not slide novelty drives the split penalty, that encoders carry a scanning-session signature decodable at 0.97 to 0.99 balanced accuracy, that the head has no intercept and over-disperses its predictions by 1.8, that counts are negative binomial without zero inflation, and that the between-donor share of expression variance is about 0.3 to 0.4 on the tasks that can measure it. These are the premises of both topics, measured rather than assumed.

## 15. A1. Coverage across designs

**How.** The harness (A0) builds, for each task, design and fold, three disjoint sets, proper-training, calibration and test, with the calibration set held out at the highest level the pool supports (donor if at least two donors, else slide, else buffered blocks) at about 25% of units. Absolute and scaled scores, twelve encoders, four designs. Checked against round 2 to $10^{-16}$ and at nominal on the no-shift control.

**What came out.** Random 0.894, slide-out 0.859, donor 0.802, patient 0.786, the ordering identical for all twelve encoders. Grouped by calibration unit instead of design, donor-level and slide-level calibration lose about five points and block-level calibration loses twenty-one. Encoder quality does not predict coverage under shift (range under 0.02 across encoders) but does predict width.

**What it says.** Coverage is a property of the calibration design, not of the predictor. The benchmark's own patient split, with the calibration set formed by any sensible rule, does not give valid intervals on new donors.

## 16. A2. Where and how the failure happens

**How.** Strata over the A1 outputs, plus one controlled intervention. On one shared proper-training set, the calibration scores come either from held-out donors or from spatial blocks carved out of the training slides, with everything else identical, three encoders, eight task files.

**What came out.** Unit calibration 0.856, block calibration 0.744, block lower in 138 of 138 cells, and block intervals a third narrower. The unit arm did this on 38% of the calibration spots and reproduced A1 within 0.0005. Coverage does not track $K$ or the between-unit variance share; a location-shift simulation predicts near-nominal coverage at every $K$. Failures are on scale, intervals too narrow, in every group; unit-calibrated intervals are the right width with a consistent tendency to miss above. Coverage collapses in the top decile of predicted values, 0.68 against 0.90 in the low deciles. Slides are heterogeneous even without shift, and the scaled score fixes that under the random design.

**What it says.** Where the calibration scores come from decides coverage, and how many there are barely matters. Calibration inside the training slides cannot see the between-slide spread a new donor produces. The small-$K$ reading I proposed at the A1 gate was tested and failed, which is a good thing to know. The upper-tail failure is the $R^2$ ladder's over-dispersion seen from the interval side.

## 17. A3. Reweighting and hierarchical calibration

**How.** Weighted conformal with a classifier on the embedding (W1), a classifier on eight morphology covariates only (W1b), coarse covariate cells (W2), and HCP (W3), at $\alpha$ of 0.1 and 0.2, three encoders.

**What came out.** Calibration and test slides separate at AUC 0.97 or better from the embedding and 0.90 from morphology alone; $n_{\text{eff}}$ collapses to a median 2% of the calibration set; W1 moves coverage a long way per fold in both directions with no mean movement, costing one task 0.15. W2 has no support on the folds that matter. HCP is infinite wherever $K + 1 < 1/\alpha$, in all 1,932 cells, which at $\alpha = 0.1$ is every unit-calibrated fold in the benchmark, and where finite at $\alpha = 0.2$ it over-covers by 10 to 19 points.

**What it says.** Feature-based reweighting is not a repair on this kind of data, because the test population is identifiable from its features. Tissue composition alone identifies the slide nearly as well, so the shift is not separable into a technical part to remove and a biological part to keep. The valid method needs nine donors at 90%, and the benchmark's calibration rule never reaches it.

## 18. A4. Scores, and HCP with enough donors

**How.** Six scores compared at matched coverage on a gene subset (CQR and NB were expensive). Then A4b, CCRCC with the calibration fraction raised so that ten donors calibrate, three encoders, three draws, pooled quantile against HCP against one-score-per-donor.

**What came out.** At 90%, CQR is 2.65 wide against 2.69 for the absolute score; the scaled score is 14.8. In the top decile CQR and conformalised NB lift coverage from 0.72 to 0.87. The NB model's own band under-covers (0.71 under donor shift) and conformalising it restores marginal coverage. With ten calibration donors HCP is finite in every cell, covers 0.969 at 1.95 times the pooled width; one-per-donor covers 0.911 at 1.43 times; the pooled quantile covers 0.864 whether six or ten donors calibrate it. On the Indiana set the same design gives HCP 0.988 at 1.91 times.

**What it says.** The interval shape is a second-order matter except in the upper tail, where a prediction-dependent score is needed. The valid method exists, works on real data once $K \ge 9$, and costs about a factor of two in width and seven to nine points of over-coverage. That over-coverage is the open problem.

## 19. B1 and B2. Inference with predicted expression

**How.** Estimands are the slope of expression on standardised mean nuclear area, the neoplastic-minus-stromal difference, and the round-2 correlation on IDC. Predictions come from a head that never saw the donor. Three variances (spot i.i.d., donor cluster-robust with $t_{G-1}$, donor bootstrap), two population definitions, three encoders plus a permuted predictor, CCRCC with 6, 8 and 12 labelled donors, LYMPH_IDC with 2, PRAD as the two-donor failure case. Then 200 relabellings per setting.

**What came out.** The clustered standard error is 29 to 68 times the spot-level one. Over relabellings the spot i.i.d. interval covers 0.044 at nominal 0.90, the cluster-robust one 0.913, the bootstrap 0.711. PPI intervals are 0.85 to 0.89 as wide as classical for the encoders in the donor-weighted population and 0.98 for the permuted predictor; $\lambda$ falls from about 0.7 at six labelled donors to about 0.2 at eight or more; better-predicted genes gain more. IDC's correlation, the paper's own biomarker example, is $-0.46$, $-0.70$, $+0.53$ and $+0.87$ on its four donors, each interval excluding zero, and its pooled donor-clustered interval spans zero at 59 times the spot-level width. PRAD with one donor degree of freedom covers 0.

**What it says.** This is the cleanest result of the round and the one with the widest audience. Any spot-level uncertainty statement about predicted expression, or for that matter about measured expression, is off by more than an order of magnitude. The fix is standard and works with as few as six donors if the $t$ reference is used. Predictions help, modestly, and mostly when labelled donors are few.

## 20. Track D. The expansion

**How.** Inventory of all 1,276 samples, three sets downloaded (105 samples, 70 GB), embedded with three encoders, audited against source records, and the benchmark's own patches compared with the release's.

**What came out.** The archive has no cell with three laboratories at three donors, and no two-laboratory cell with disease held fixed. Two round-2 labels were wrong in the direction that matters (IDC's pair is two donors; a "Washington University" set was generated at Indiana). The benchmark's patches are a different resampling of the same images, and no result moves with the layout. Indiana's 25 donors with every technical axis fixed show donor shift costing one point of coverage. The kidney tumour-to-non-tumour shift is asymmetric (0.91 one way, 0.70 the other). Instrument generation is a session-like axis (0.81 against 0.89 on breast Xenium).

**What it says.** The institution axis is not in HEST-1k. The donor axis is, twice over, and it behaves the same way on both tasks. Every label has to be read from a source record before it is grouped on.

---

# Part III. What has not been tried

Ordered by how much each would change the decision.

1. **A valid, less conservative interval for a new donor at $K$ of 10 to 25.** The gap between HCP's 0.97 and nominal, at double the width, is the methodological opening. Candidate routes, none yet run, are repeated one-per-donor subsampling with a proper aggregation of the draws; an adaptive score (CQR or NB) inside the hierarchical weighted quantile, since the upper-tail failure survives HCP; a model for the between-donor distribution of score quantiles with a finite-$K$ correction; and a randomised version of the $+\infty$ atom. All are simulation first.
2. **A small labelled sample on the test slide.** With $m$ labelled spots on the slide being predicted, calibration within the slide is exchangeable with the rest of that slide and needs no cross-donor assumption at all. Coverage as a function of $m$, and the PPI width when the same $m$ spots are the labelled set, have not been measured. Everything needed is in hand.
3. **The allocation result.** For a labelling budget $B = n_L \times m$, the variance of the clustered PPI estimator as a function of the split between donors and spots per donor, derived from section 8 and checked by masking. Not started.
4. **A cross-fitted $\lambda$, a studentised or BCa bootstrap, and the superpopulation version of B2.** Standard refinements, all cheap.
5. **Slide-level recentring predicted from features.** The offsets $b_s$ are about half a standard deviation and both signs; whether they can be predicted from the slide's mean embedding, which carries the slide signature, is untested. If they can, the small-$K$ case improves without labels.
6. **Session as a calibration level.** PRAD's two sessions and breast's two instrument generations are the only measured session contrasts; calibrating at session level has not been tried.
7. **The scaled score's residual model with a floor set by calibration quantiles rather than a constant, and CQR on the full gene set.** A4 ran CQR on 6 of 50 genes.
8. **Anything on the full transcriptome.** Every gene-level claim is conditional on 50 genes chosen with test spots. Visium samples carry the whole transcriptome and gene selection on training data only has been implemented but not used beyond Indiana.
9. **Topic B on a second task**, Indiana, once its morphology covariates are built.
10. **Any train-time method.** Fine-tuning the encoder, a spatial model (STFlow stays deferred), or a head with a donor random effect. The project has been deliberately post-hoc, and that choice has not been revisited.

---

# Part IV. Are we using the data?

## 21. What HEST-1k is

The release (v1.3.0) has 1,276 samples across 26 organs, mostly Visium, with per-sample image patches, expression, CellViT nuclear segmentation, and metadata, plus whole-slide images (1.14 TB) and, for Xenium, subcellular transcripts. About 292 samples carry a usable patient label, resolving to 158 donor keys. 1,074 of 1,276 carry an uncertain pixel size. Fifteen ids are duplicates of other ids. The benchmark is 72 of these samples with a fixed protocol.

## 22. What we have used

72 benchmark samples for everything through A4 and B; 76 expansion samples (kidney and breast Xenium) embedded and used in D4; 32 platform-pair samples downloaded and untouched. Components used are patches, expression, segmentation (for morphology covariates) and metadata. Not used are the whole-slide images (not needed once patches exist), the subcellular transcripts, and the eleven-hundred-odd remaining samples. In sample count that is about 12% of the archive. In donor count it is a larger fraction of what is usable, because most of the archive has no donor label.

## 23. What the rest of the archive holds for this project, and what it does not

The project's question has become "how many donors, and how is a labelling budget spent", so the archive's value is in donor-rich cells with technical axes fixed, in whole-transcriptome samples, and in tissue diversity for the population-shift result. Reading the inventory that way:

- **Lung Xenium, 24 samples, 21 donors, one laboratory, pixel size clean on all 24.** The best unused cell for the donor agenda. It would be a third $K = 10$ task and a third Topic B task, on a Xenium panel rather than Visium, which matters because the two platforms have different sparsity and dispersion.
- **Breast on the older Spatial Transcriptomics platform, 108 samples, 31 donors, two Stockholm groups.** The largest donor count anywhere, but 100 µm spots, about 400 spots per section and uncertain pixel size on every sample. Useful for the donor-count question if the pipeline tolerates the platform; not useful for anything spot-resolved.
- **Bowel Visium, 50 samples across five cohorts.** Donor labels mostly missing; would need the same audit as kidney before it is worth anything.
- **Whole-transcriptome Visium samples generally.** The gene axis is the one the project has ignored. Every Visium sample in the archive supports training-only gene selection over thousands of genes, which turns the 50-gene coverage tables into distributions over genes and removes the biggest conditional in every claim.
- **Mouse tissue and non-cancer tissue.** Out-of-population test sets for the coverage floor, of the kind D4.3 measured once.
- **The Xenium transcripts.** Sub-spot resolution; nothing in the current framing uses it.

What the archive cannot give, checked across all 46 organ-by-technology cells, is a laboratory contrast with disease held fixed. That was the original expansion goal and it is closed.

## 24. The honest answer

We are not restricting ourselves to the benchmark by choice any longer; we restricted ourselves to it in round 3 because the expansion was scoped for an institution axis that turned out not to exist, and the donor-rich cells were picked up on the way. For the reframed question the archive is far from exhausted. Lung Xenium and the whole-transcriptome Visium samples are the two things worth pulling next, and both cost a day of download and embedding on infrastructure that already works. What no amount of HEST-1k will supply is the multi-laboratory axis, and the decision to stop looking for it there should be explicit.

One thing HEST-1k offers that is easy to overlook. Every spot is labelled. That means any labelling design, a few spots per slide, a few slides per donor, a few donors per study, can be simulated by masking, with the full data as the truth. For a project about how to spend a labelling budget, that is the ideal dataset, and it is why the reframed question is not data-limited.

---

# Part V. The decision, framed

The methods that have been used are all standard and correctly applied; the project's value so far is in the measurements, and the measurements say the unit is the donor. The open methodological problem is a sharper valid interval for a new donor at small $K$. The paper that is ready to be written is on inference and design with the donor as the unit. The data for both are either in hand or one download away, with lung Xenium and whole-transcriptome Visium the next pulls. The thing to stop doing is looking for an institution axis in this archive.
