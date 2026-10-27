# How few labelled clusters are enough? Limits and labelling budgets for prediction-powered inference with clustered data

*Draft v0, 27 October 2026, by the fewcluster session, following the outline `docs/round09/i02/fewcluster/round09_fewcluster_paper_outline.md`. The prediction-set half is deferred, as Nicolas asked on 27 October. Every number is taken from a file named beside it. Statements marked "provisional" rest on checks not yet closed. This draft is a working text, and later versions are new files (v1, v2, ...), not edits of this one.*

## Abstract

Prediction-powered inference uses predictions available for every unit to sharpen inference from a small labelled subset. When units come in clusters and only a few clusters can be labelled, its intervals rest on asymptotics that may not hold. We ask when any interval that rescales with the data can be valid in finite samples, under sampling of a few clusters from a finite population. For a fixed prediction coefficient, the answer is a sharp frontier on residual concentration, the largest share of one cluster in the residual sum of squares. Below the frontier a finite critical value exists, and above it every valid interval is unbounded with positive probability under every population. The frontier depends only on the number of clusters, the number labelled and the level, and simple random sampling is minimax among fixed-size designs. With a coefficient fitted on the sample, the defeating samples are those on which residuals are affine in the predictions, and the frontier depends on the prediction vector. We give an exact algorithm for it. For stratified designs, which include labelling a cluster with certainty and labelling a few units in every cluster, the frontier is a product over strata. On spatial transcriptomics tasks from HEST-1k and on income by state from the American Community Survey, every task lies beyond the frontier when whole clusters are labelled at the sizes used in practice. Labelling a few units in every cluster puts the same tasks inside it with 5 to 8 units per cluster, provided no cluster carries more than a small share of the design variance.

## 1. Introduction

Labels are expensive and predictions are free. In spatial transcriptomics a pathology foundation model predicts gene expression for every spot of every slide, while measured expression exists for only a few donors. In census data a model predicts income for every person, while a survey of income reaches only some states. Prediction-powered inference (PPI; Angelopoulos et al.) and its tuned form (PPI++) correct the prediction-based estimate with the labelled residuals, and the survey-sampling literature knows the same construction as the difference and regression estimators (Cochran; Mozer, arXiv:2603.19160).

The data come in clusters, and labelling is usually done a cluster at a time. Broska and Howes (arXiv:2610.09601) give cluster-robust PPI intervals and compare labelling designs through their asymptotic variance. Their intervals, like every cluster-robust interval, rest on the number of labelled clusters growing. With 4 to 16 labelled clusters, the question is not how fast the asymptotics take hold but whether any finite-sample guarantee is available at all.

The paper answers that question for intervals that move with the data, which covers every PPI, $t$, CR2, sign-change and wild-bootstrap interval. It makes four contributions.

1. A sharp frontier for a fixed coefficient (Theorem 1), with its matching possibility half, extremal populations and design minimaxity, and its practical form as the number of clusters to label for a stated bound on residuals.
2. The frontier with a coefficient fitted on the sample (Theorem 2), where the predictions enter the theory, with an exact algorithm.
3. The frontier for stratified designs (Theorem 3), which turns the choice between labelling whole clusters and labelling a few units in every cluster into a statement about which designs can carry a guarantee.
4. The real tasks, read against the frontiers, and the estimator the design-based reading requires (Williams 1961 rather than the cross-fitted form in common use).

The technique is classical. It is the limiting-sequence argument of Bahadur and Savage (1956), Gleser and Hwang (1987) and Dufour (1997). The large-cluster limit of Theorem 1 is the iid threshold $n < \log_2(2/\alpha)$ of Lanke (1974), as discussed by Paul and Kuchibhotla (arXiv:2403.06357). What is new is the finite-population, graded form with its possibility half, the tuned and stratified frontiers, and the design consequences. Pötscher and Preinerstorfer (arXiv:2412.17470) give a yes-or-no condition of the same shape for Gaussian regression with leverage, and Ibragimov and Müller (2010, 2016) show that a $t$-test on a few heterogeneous Gaussian group estimates can be valid. Neither treats sampling from a finite population or gives a frontier.

## 2. Setting

There are $G$ clusters with values $z_g$, here a cluster mean of the outcome, and predictions $f_g$ known for every cluster. The target is $\theta = G^{-1}\sum_g z_g$. For a fixed coefficient $\lambda$ the residual is $e = z - \lambda f$ and $\theta = \lambda \bar F + \bar e$. A sample $S$ of $n$ clusters is drawn by simple random sampling without replacement, and the fixed-coefficient PPI interval is

$$
\lambda \bar F + \bar e_S \;\pm\; c\,\sqrt{\Big(1 - \frac{n}{G}\Big)\frac{s^2_{e,S}}{n}} .
$$

A procedure is equivariant if shifting and rescaling the residuals shifts and rescales its output in the same way. Residual concentration is measured by the max-share

$$
\kappa(e) = \frac{\max_g (e_g - \bar e)^2}{\sum_h (e_h - \bar e)^2},
$$

and the class $\mathcal{K}(\kappa_0)$ collects the populations with $\kappa(e) \le \kappa_0$. Equivalently, no residual lies more than $\Lambda_0 = \sqrt{\kappa_0 (G - 1)}$ residual standard deviations from the mean. This is Hájek's (1960) condition for the asymptotic normality of the sample mean, in finite-sample form. An analyst who can defend $\Lambda_0$ can defend $\kappa_0$.

Two quantities carry the results. For $1 \le k \le G/2$,

$$
\kappa_2(k) = \frac{1 - k/G}{k}, \qquad \pi(k) = \frac{\binom{G-k}{n} + \binom{k}{n}}{\binom{G}{n}} .
$$

A two-point population with $k$ clusters at one value and $G - k$ at another has max-share $\kappa_2(k)$, and $\pi(k)$ is the probability that the sample falls inside one of its groups. Let $k^\ast$ be the smallest $k$ with $\pi(k) \le \alpha$.

## 3. What few labelled clusters can and cannot guarantee

**Lemma 0.** *A procedure valid at every population covers every shifted target $\theta + M/G$ with probability at least $(1 - \alpha - n/G)/(1 - n/G)$, for every population and every $M$.* At 8 of 24 and $\alpha = 0.10$ this is 0.85. Without a restriction on the class, valid intervals are useless. This is the total-variation form of Bahadur and Savage and is not claimed.

**Lemma 1.** *A population constant on $G - k$ clusters has $\kappa \ge \kappa_2(k)$, with equality for $k \le G/2$ exactly at the two-point population.*

**Theorem 1 (fixed coefficient).** *If $\kappa_2(k) < \kappa_0$ and $\pi(k) > \alpha$ for some $k \le G/2$, every equivariant procedure valid over $\mathcal{K}(\kappa_0)$ is unbounded with probability at least $\pi(k) - \alpha$ under every population. If the largest fraction of samples on which a population in the class is constant is at most $\alpha$, the interval above is valid over the class for some finite $c$. The two meet at*

$$
\kappa^\ast = \kappa_2(k^\ast - 1) = \frac{1 - (k^\ast - 1)/G}{k^\ast - 1}
$$

*whenever $k^\ast$ exists and $n \ge 6$ (on the grid of this paper), with the boundary point open. Every fixed-size design that may depend on the predictions but not on the outcomes is no better, so simple random sampling is minimax.*

The impossibility half takes the two-point population, perturbed toward any given population. On the samples that fall inside one group the data are a rescaled copy of the given population's data, and by equivariance the target moves off to infinity as the perturbation shrinks. The possibility half is a compactness argument over normalised populations, in which a sample missed at an ever larger critical value must be constant in the limit. Proposition 3 of the frontier note bounds the fraction of constant samples by the two-point value and a convexity term that is below 0.02 on every cell with $n \ge 6$.

At 8 of 24 the frontier is 0.158, every residual within 1.91 SD of the mean, and 0.167 of populations of independent normal residuals lie inside it. At 8 of 51 it is 0.071, within 1.89 SD, and 0.009 of normal populations lie inside (`results/round9/fewcluster/feasibility/s3_frontier_exact.csv`). As $G$ grows with $n$ fixed the frontier in SD units tends to

$$
\Lambda^\ast(n, \alpha) = \sqrt{\frac{\alpha^{1/n}}{1 - \alpha^{1/n}}},
$$

1.73 at $n = 8$ and $\alpha = 0.10$, and as $\Lambda_0 \to \infty$ the condition becomes Lanke's $n < 1 + \log_2(1/\alpha)$. The same two-block construction with a small central mass proves Paul and Kuchibhotla's conjecture for shift-invariant intervals for the median (`docs/round09/i02/fewcluster/round09_fewcluster_sources_and_median.md`, provisional).

**Corollary (how many clusters to label).** To guarantee coverage when residuals beyond $\Lambda_0$ SD cannot be ruled out, 24 clusters need 13 labelled at $\Lambda_0 = 3$ and 17 at $\Lambda_0 = 4$, and 51 clusters need 16 and 27 (`results/round9/fewcluster/strat/i32_required_n_A.csv`).

**Theorem 2 (tuned coefficient).** With the least-squares coefficient fitted on the sample and the class defined through the population least-squares residual $\hat e(z)$, the coverage depends on $z$ only through $\hat e(z)$. The defeating samples are those on which $\hat e(z)$ is affine in $f$, and impossibility and possibility meet at

$$
\kappa^\dagger(f, G, n, \alpha) = \inf\big\{\kappa(\hat e(z)) : \text{the fraction of samples on which } \hat e(z)_S \text{ is affine in } f_S \text{ exceeds } \alpha\big\},
$$

up to the boundary point. At the paper's sizes only a single line of $m_{\min}$ collinear clusters can defeat the interval, and the frontier is the minimum over such lines of the reciprocal of a convex maximisation, solved exactly by enumerating the vertices of a small polytope. That computation matched an independent one in 15 of 15 cases to $2 \times 10^{-16}$ (`results/round9/fewcluster/exact/i26_benchmark.csv`). At 8 of 24 with normal predictions the tuned frontier is 0.0853 on average (`i26_synth_exact.csv`), about half the fixed-coefficient one. A spike at cluster $g$ has $\kappa(\hat e) = \max\{(1 - h_{gg})^2, \max_{j \ne g} h_{gj}^2\}/(1 - h_{gg})$, with $h$ the hat matrix of $(1, f)$. So fitting the coefficient makes the guarantee harder, and outliers at high-leverage clusters are cheaper in max-share than outliers elsewhere.

**Theorem 3 (stratified designs).** Strata $h$ of $N_h$ units are sampled independently, $n_h$ from each, with target $\sum_h W_h \bar e_h$ and the stratified interval. Write $v_h$ for stratum $h$'s share of the design variance and $\kappa_h$ for its own max-share. For any closed class defined through the pairs $(v_h, \kappa_h)$ that stays in the class when a $\kappa_h$ is lowered, a degenerate sample must be constant in every stratum carrying variance. The defeating configurations are two-point populations in a set $S$ of strata, with value $\prod_{h \in S} \pi_h(k_h)$. Impossibility holds when a configuration in the class has value above $\alpha$, and possibility when no population in the class has more than $\alpha$ of its samples degenerate. That condition is bounded by the same product with Proposition 3's term added (`docs/round09/i03/fewcluster/round09_fewcluster_stratified.md`). Two classes follow.

1. A pooled cap on every unit's share gives a multiple-choice knapsack, with capacity $k N_h/(N_h - k)$ and cost $-\log \pi_h(k)$ per level.
2. A box class bounds residuals by $\Lambda_0$ SD of their own stratum and each stratum's variance share by $v_0$. Then $\lceil 1/v_0 \rceil$ strata must degenerate at once, and the worst value is the product of the $\lceil 1/v_0 \rceil$ largest $\pi_h(k_{\min,h})$.

A take-all stratum never enters. So labelling a cluster with certainty removes it from the class, and on CCRCC, labelling the most atypical donor INT5 with certainty leaves 0.94 of genes beyond the frontier for the remaining 7 of 23 (`results/round9/fewcluster/design/`). With many strata, the iid threshold no longer binds per stratum. For 24 clusters of 2000 units, 4 units per cluster, below $\log_2(2/\alpha) = 4.32$, put 0.875 of normal populations inside the pooled frontier, and 5 put all inside.

**Corollary (units per cluster).** Under the box class, regime B needs the following units per cluster, for clusters of 2000 units (`i32_required_m_B.csv`).

| $\Lambda_0$ | $v_0 = 0.025$ | $0.05$ | $0.1$ | $0.2$ | $0.5$ | $1$ |
|---|---|---|---|---|---|---|
| 3 | 2 | 2 | 3 | 5 | 11 | 22 |
| 4 | 2 | 2 | 4 | 8 | 19 | 38 |
| 6 | 3 | 5 | 9 | 17 | 41 | 81 |
| 8 | 4 | 8 | 15 | 30 | 73 | 143 |

The column $v_0 = 1$ makes no assumption across clusters, and there the requirement is tens to hundreds of units per cluster. The gain of regime B is bought with the assumption that no cluster dominates the design variance.

## 4. Inference below the frontier (novelty provisional)

The possibility halves give a finite critical value but not its size. Writing $x$ for residuals centred at the population mean, the interval misses on sample $S$ exactly when

$$
\frac{\big(\sum_{i \in S} x_i\big)^2}{n\sum_{i \in S} x_i^2} > \rho, \qquad \rho = \frac{c^2(1 - f)/(n - 1)}{1 + c^2(1 - f)/(n - 1)},
$$

so a miss means the sample lies in a narrow cone around the constant direction. A quadratic majorant of the miss indicator, with the exact moments of sampling without replacement, gives certified critical values in tight classes. At 0.4 of the frontier it gives 3.78 at 8 of 24 and 4.40 at 8 of 51, and at 0.25 of the frontier 2.89 at 12 of 24 and 3.23 at 16 of 51. The worst populations found by search give lower bounds of 2.09, 2.36, 1.91 and 1.98 at the same points, against the normal 1.645 (`results/round9/fewcluster/crit/crit_value_report.md`). Up to three quarters of the frontier the lower bounds stay between 1.9 and 3.0. Near the frontier they rise to between 4.4 and 5.0, and no certificate was found there. For the box class at the ACS and HEST settings no certified value was found, because the probability that every stratum degenerates at once lies within 14% of $\alpha$, and the lower bounds are 2.1 to 2.8. A fresh agent re-derived the certificate and recomputed the four certified values in exact arithmetic (`results/round9/fewcluster/verify_crit/`), and its novelty check (NOV12) is pending. A sharp computable critical value in the classes that real tasks satisfy is open.

## 5. Estimators and designs in practice

**The estimator.** The cross-fitted tuned estimator of the project's round 5 is Williams' (1961) exactly unbiased split-sample regression estimator without his finite-population factor (round 8 positioning note). In 20,000 draws per population at even $n$ from 4 to 16, Williams' estimator and the fold-wise form of the design-based cross-fitting papers were unbiased to Monte Carlo error in 0.999 of 3264 cells and had equal mean squared errors. The round 5 estimator's bias was below 0.1 SD in 0.968 of cells, but its variance pooled residuals fitted with different coefficients. That variance grows with the level of the predictions, and it widened the interval by 1.09 to 1.53 times on HEST and 9 to 20 times on ACS (`docs/round09/i03/fewcluster/round09_fewcluster_williams.md`). With a variance pooled within halves, the exactly unbiased forms covered 0.84 on CCRCC and 0.86 on INDIANA_KIDNEY at 8 labelled donors, below nominal as the frontiers predict. The fixed coefficient did about as well as any tuned form at these sizes. The paper uses Williams' form with $k = 2$ and the within-half variance, and the fixed coefficient as the reference interval.

**Designs that select clusters with the predictions.** Corollary 4 of Theorem 1 shows that no fixed-size design can move the frontier, so balanced and prediction-guided designs cannot buy a guarantee. They can still narrow intervals. In the project's round 7 comparison at 4 to 16 labelled clusters (`docs/round07/i04/ppi/round07_ppi_final_decisions.md`), rejective selection with the `rej_t` interval of Yang, Qu and Li was 0.449 to 0.467 of the classical width on census at coverage 0.888 to 0.897, but covered only 0.852 to 0.866 on tissue. A cube design with bounded inclusion probabilities covered like the classical interval at $n \ge 6$. Greedy k-center selection covered 0.326 to 0.458, and Broska and Howes's interval covered 0.704 on tissue at 4 labelled clusters, 0.884 with a small-sample correction. Those runs used round 5's machinery for the tuned interval, and whether their tuned-interval numbers carry the variance inflation above is not yet checked.

## 6. Applications

**Data.** HEST-1k (Jaume et al., NeurIPS 2024) supplies CCRCC (24 donors), INDIANA_KIDNEY (25 donors) and LUNG_XENIUM (15 donors, 343 genes), with predictions from the uni_v2 encoder. The ACS PUMS 2018 supplies log income for 1,659,616 persons in 51 states, with cross-fitted gradient-boosting predictions ($R^2 = 0.62$).

**Regime A.** The median residual max-share of donor means is 0.533 on CCRCC, 0.336 on INDIANA_KIDNEY and 0.312 on LUNG_XENIUM, against tuned frontiers of 0.091, 0.086 and 0.148 at the middle design size. Practically every gene lies beyond both frontiers, the tuned one for 1.00, 1.00 and 0.997 of genes (`results/round9/fewcluster/exact/i26_real_exact_summary.csv`). For ACS with predictions the state-level residual max-share is 0.094 against 0.071 at 8 of 51.

**Regime A against regime B.** The table judges each population under the box class at its own bounds, with $\lambda = 1$ (`results/round9/fewcluster/strat/`).

| Task | Regime A, clusters needed (median over genes) | Regime B, units per cluster (median, 90th percentile) |
|---|---|---|
| ACS by state | 11 of 51 | 5 |
| CCRCC | 17 of 24 | 6, 10 |
| INDIANA_KIDNEY | 13 of 25 | 8, 12 |
| LUNG_XENIUM | 8 of 15 | 8, 25 |

On ACS this is 54,539 to 931,765 labelled persons in regime A against 255 in regime B.

## 7. Discussion

The frontiers say what no interval can do, and the application says where real tasks sit. Labelling whole clusters at the sizes used in practice cannot carry a scale-free guarantee on any of the tasks here. Labelling a few units in every cluster can, under an assumption across clusters that is explicit and can be argued for. Prediction-guided selection of whole clusters cannot change that. The fixed and the tuned coefficient differ in how hard the guarantee is, with tuning making it harder. The paper does not offer a sharp critical value in the classes that real tasks satisfy, and it does not cover prediction sets for a new cluster, which are left for separate work.

**Open items before submission.** These are the fresh-agent and novelty checks of section 4, whether rounds 5 to 7's tuned intervals carry the variance inflation, the exact tuned frontier for ACS (51 states, where enumeration is infeasible), and a tuned version of Theorem 3.
