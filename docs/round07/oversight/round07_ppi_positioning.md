# The PPI paper's positioning against cluster-robust PPI, the cluster bootstrap and balanced active inference

*Revised by later results, 15 October 2026. Round 7 found that Broska and Howes's interval with a small-sample correction ($t_{n_L-1}$ and the divisor $n_L - 1$) covers at four labelled clusters and is narrower there than the paper's tuned interval. So the rows and sentences below that claim the few-cluster regime as the paper's own are too broad. What the paper keeps is the finite-population factor and cross-fitting term for the design target and the design results (`docs/round07/i04/ppi/round07_ppi_final_decisions.md`, section 2 item 6, and `docs/round07/oversight/round07_ppi_results_explained.md`, Part C). This note is revised once Nicolas decides R7-5.*

13 October 2026. Written by the oversight chat for Nicolas, as step R7.1 of round 7, after the overlap check (`docs/round07/00_prep/round07_overlap_check.md`). It settles what the paper "Labelling budgets for prediction-powered inference with clustered data" can claim as its own, and what that means for round 7's PPI question (open question O2). Recommendations are `[proposed]` until Nicolas decides. Positioning against published work is his decision with David (open question O5). An independent agent checked this note against the three papers and the repository before commit. It re-derived section 2.2 and found it correct, and its other findings are worked in.

## 1. What was read

Nicolas uploaded the three papers on 13 October to `~/hest-1k/ppi_conf_papers/` on his Mac. They are not in the repository.

- **Broska and Howes, "Cluster-Robust Prediction-Powered Inference", arXiv:2610.09601v1, 7 October 2026.** All 26 pages, including appendices A to E. This replaces the question-answering pass of the overlap check.
- **Chen, Zhou, Peng and Wang, "Balanced Active Inference", NeurIPS 2025.** The main text and appendix A, the proof of its theorem 1. The supplementary material, which holds the cube method's details and the variance estimators, was not in the file.
- **Kluger, Lu, Zrnic, Wang and Bates, "Prediction-Powered Inference with Imputed Covariates and Nonuniform Sampling", arXiv:2501.18577v3.** Sections 1 and 3.4, appendix B and the clustered experiment of the appendix. The general theory of sections 2 and 3 was skimmed, not checked.

Our side is the round-4 theory (`docs/round04/tracks/ppi/round4_ppi_theory.md`, sections 2 and 4.3), the estimator definition (`docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`), and the round-5 inference memos (`docs/round05/i02/ppi/round5_ppi_E2_decisions.md`, section 2, and `docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, sections 2, 3 and 5).

The round-4 theory itself says that none of its results is new. They are the difference estimator's variance in the one-way random-effects model (Särndal, Swensson and Wretman 1992, chapter 8; Cochran 1977, chapter 10), written in the notation of prediction-powered inference. What follows is about what the PPI literature now holds beside that classical background.

## 2. Broska and Howes

### 2.1 Their setting

Clusters $g = 1, \dots, G$ are independent draws from a cluster distribution, with random size $m_g$. Each cluster gets a labelling probability $p_g$, drawn independently of the data, and given $p_g$ each unit is labelled by an independent Bernoulli draw with probability $p_g$. So the number of labelled clusters is random. The design is described by the mean labelling probability $\mu_p = E[p_g]$ and the correlation of two units' label indicators in the same cluster,

$$
\eta_p = \frac{\text{Var}(p_g)}{\mu_p(1 - \mu_p)} .
$$

$\eta_p = 0$ labels units independently in every cluster, and $\eta_p = 1$ labels whole clusters or nothing. The estimand is the unit-level mean of a superpopulation, and appendix A allows cluster-level weights. The estimator is PPI++ with one global coefficient $\lambda$, the interval uses normal quantiles, and the predictor is fixed in advance, so there is no cross-fitting.

### 2.2 Their design formula contains the gain theorem's endpoint

Write $S_{Y,g} = \sum_i (Y_{g,i} - \theta^\star)$ and $S_{f,g} = \sum_i (f(X_{g,i}) - \theta_f)$ for a cluster's centred sums of outcomes and predictions, $\kappa = E[m_g]$, and $r = \mu_p/(1 - \mu_p)$. Their equation (8) gives the asymptotic variance at a fixed $\lambda$ as

$$
\sigma^2_\lambda = \frac{1 + r}{r\kappa}\Big(\text{Var}(\varepsilon_g) - 2\lambda\,\text{Cov}(\varepsilon_g, Z_g) + \lambda^2\,\text{Var}(Z_g)\Big),
$$

and their equation (11) gives the optimal coefficient $\lambda^\star = \text{Cov}(\varepsilon_g, Z_g)/\text{Var}(Z_g)$. Their appendix C writes the tuned variance in design terms as

$$
V^{PP} = \frac{1}{\kappa^2 G \mu_p}\left(V_\varepsilon - \frac{V_{\varepsilon,Z}^2}{V_Z}\right), \qquad V_\varepsilon = V_{Y,s} + \big(\eta_p(1 - \mu_p) + \mu_p\big)V_{Y,d},
$$

$$
V_Z = \frac{V_{f,s} + \eta_p V_{f,d}}{1 - \mu_p}, \qquad V_{\varepsilon,Z} = V_{Y,f,s} + \eta_p V_{Y,f,d},
$$

where the subscript $s$ marks sums over the same unit and $d$ sums over pairs of different units in a cluster. With whole clusters labelled, $\eta_p = 1$, the two parts add up to the variance and covariance of the cluster sums,

$$
V_\varepsilon = \text{Var}(S_Y), \qquad V_Z = \frac{\text{Var}(S_f)}{1 - \mu_p}, \qquad V_{\varepsilon,Z} = \text{Cov}(S_Y, S_f).
$$

The labels-only estimator is the case $\lambda = 0$ of equation (8). Since $(1 + r)/(r\kappa) = 1/(\kappa\mu_p)$ and $\text{Var}(\varepsilon_g) = \mu_p \text{Var}(S_Y)$ at $\eta_p = 1$, its variance in the same scaling is

$$
V^{\text{labels only}} = \frac{\text{Var}(S_Y)}{\kappa^2 G \mu_p}.
$$

Dividing the two, with the common factor cancelled,

$$
\frac{V^{PP}}{V^{\text{labels only}}} = 1 - (1 - \mu_p)\,\text{corr}^2(S_Y, S_f), \qquad \lambda^\star = (1 - \mu_p)\frac{\text{Cov}(S_Y, S_f)}{\text{Var}(S_f)} .
$$

Round 4's gain theorem (theory section 2, step 3) says that with $n_L$ labelled clusters, $G_U$ unlabelled ones and many units per cluster, the tuned ratio for the donor-weighted mean is

$$
\rho_A(\lambda_A) = 1 - R^2_{\text{cluster}}\,\frac{G_U}{G_U + n_L}, \qquad \lambda_A = \lambda_c\,\frac{G_U}{G_U + n_L},
$$

with $\lambda_c$ the cluster-level regression coefficient. Set $\mu_p = n_L/G$, so that $1 - \mu_p = G_U/(G_U + n_L)$, take equal cluster sizes, so that the unit-level and donor-weighted means coincide, and label every unit of a labelled cluster ($m = M$). Then the two formulas agree, at any cluster size and not only in round 4's large-$m$ limit, since round 4's variance before step 1 already carries the within-cluster terms. Their formula is a large-$G$ variance under Bernoulli selection with a random number of labelled clusters, and round 4's is a finite-$n_L$ variance at a fixed $\lambda$, so the agreement is between the formulas, not between the two procedures. What their formula cannot express is round 4's case $m < M$, a subsample of units labelled inside each labelled donor. That needs $0 < \eta_p < 1$, and their estimator would then also use those donors' unlabelled units.

They do not state this reading. They report the intraclass correlation of the prediction error and say the correlation $\rho(\varepsilon_g, Z_g)$ is "harder to interpret" in the clustered setting. But the endpoint and the shrunken coefficient follow from their published formula, as they follow from the classical survey-sampling variance the round-4 theory cites. So the paper cannot present them as new. It can present them as the cluster-level reading of a known variance, with the interpretation that at large cluster size a predictor gains nothing unless it tracks the cluster effects, and with the version for the design target. In the design target the finite-population factor $1 - n_L/G$ multiplies both variances, so the tuned ratio is $1 - R^2_{\text{cluster}}$ with the unshrunk coefficient $\lambda_c$.

### 2.3 Their design comparison and our regimes

They find that for a fixed share of labelled frames, spreading labels over all clusters ($\eta_p = 0$) gives the smallest error, and concentrating them in whole clusters nearly doubles it when labels are scarce. Their target is a superpopulation, so the error that remains when every cluster is partly labelled is mostly which clusters were sampled, and the predictions gain little there.

Round 4's regime comparison (theory section 4.3) answers the same superpopulation question. Its condition that regime B wins on the between-cluster term when $R^2_{\text{cluster}} < 1 - n_L/G$ leaves out the term $V_U$ for the unlabelled clusters. With $V_U$ included at $\lambda_A$, as their formula includes it, regime A's between-cluster term is

$$
\frac{\sigma_u^2\big(1 - R^2_{\text{cluster}}(1 - \mu_p)\big)}{n_L} \;\ge\; \frac{\sigma_u^2}{G}
$$

for every $R^2_{\text{cluster}} \le 1$, so regime B never loses on that term. Their formula supersedes round 4's condition, and the paper should not state that condition. What stays the paper's own is the comparison for the design target, where regime B has no between-cluster term at all (theory section 4.3), the costs per cluster and per unit with the crossover cost ratio, and round 5's level term.

One point is a reading to check, not a result. Round 5's E2 gate found that against round 4's classical estimator, which does not remove each cluster's level, a predictor that is constant within each cluster narrows the interval, by a width ratio of 0.81 to 0.82 on kidney cancer and 0.12 to 0.13 on census income (`docs/round05/i02/ppi/round5_ppi_E2_decisions.md`, section 2 item 2). Broska and Howes's labels-only comparator in the partly labelled design is the pooled mean of the labelled units, which also does not remove the cluster levels. Part of their small gain there may be of that kind. The paper should not claim this without a check.

### 2.4 What they leave out, confirmed by the full reading

- **Few clusters.** "Our variance estimator has no small-sample correction", which they name as future work. Every simulation draws 2,266 broadcasts. In the whole-cluster design at $\mu_p = 0.05$, about 113 labelled clusters in expectation, their interval covers 0.88 for the mean against nominal 0.95. For the regression, it covers 0.81 for the era coefficient, of which about 15 broadcasts in that era are labelled, and 0.95 for the program coefficient.
- **A design-based target.** Clusters are draws from a superpopulation, with no finite-population factor and no cross-fitting term.
- **Costs.** They give precision formulas and say that combining them with a cost model is future work. The paper's allocation result is that combination.
- **Choosing the labelled clusters.** Labelling probabilities may not depend on the data, which rules out balanced or rejective selection on predictions. Active labelling of clusters is future work.
- **One level of clustering,** and no prediction sets.

## 3. Kluger et al.

Whole clusters are labelled by independent Bernoulli draws with known, possibly unequal probabilities $\pi_k$, the estimator uses inverse-probability weights, and intervals come from a cluster bootstrap. The theory of the cluster bootstrap is stated to be out of scope. Their clustered experiment labels about 50 clusters, and they note slight under-coverage of the classical interval, which they suspect comes from the small number of labelled clusters.

This matters for O2. Weighting labelled clusters by known inclusion probabilities is already in print for independent Bernoulli selection of whole clusters. What is not is fixed-size, balanced selection, where the clusters' inclusions are dependent and the probabilities have to be computed by simulating the design, with an analytic interval at 4 to 16 labelled clusters. Round 5's deck-2 check also recorded that our own donor bootstrap covered 0.71 to 0.84 with few clusters (`docs/round05/00_prep/deck2/deck2_literature_check.md`).

## 4. Chen et al.

Units, not clusters, are labelled with probabilities proportional to an estimated uncertainty, mixed with uniform probabilities through a weight $\tau$ that their experiments set to 0.5. The labelled set is drawn by the cube method so that the inverse-probability-weighted total of the uncertainty equals its population total, and the estimator is the difference estimator with inverse-probability weights. The theory is asymptotic in the number of units and assumes that the dependence between inclusion indicators vanishes (their assumption 4).

Their remark 1 bears on the paper. It says that balancing on the predictions themselves makes the estimator collapse to the inverse-probability-weighted mean of the labelled outcomes, "forfeiting any benefits from active sampling", so they balance on uncertainty instead. Round 5's E4b design is a cluster-level analogue of that collapsed case, though not the same thing. It selects clusters by rejective sampling, which balances approximately on the estimand's own $\bar f_g$, and then uses the unweighted classical mean of the labelled clusters, with no prediction in the point estimate. Balancing on an auxiliary variable and then using the simple mean, as an approximation to the regression estimator, is classical (the E5 memo cites Morgan and Rubin and Fuller, section 4 item 11). What round 5 added is the comparison at few clusters. At 8 labelled clusters, selecting clusters by their predictions and then using the classical mean gave 0.726 of the simple-random classical width on kidney cancer with `uni_v2` and 0.551 on census by state, narrower than the tuned estimator under simple random selection at 0.852 and 0.618 (`docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, section 3 item 3). That holds under the conditions round 5 found (one balance variable, 8 or more labelled clusters, enough distinct acceptable samples), and the E5 memo records that inclusion under this design is uneven across clusters (section 2).

## 5. What the paper can claim

| Claim | Status after this reading | Cite |
|---|---|---|
| A cluster-robust PPI++ interval, valid as the number of clusters grows, with fully, partly or un-labelled clusters | prior art | Broska and Howes |
| PPI under weighted, stratified or whole-cluster labelling designs, with a bootstrap interval | prior art, without theory for the cluster bootstrap | Kluger et al. |
| The gain at large cluster size is $1 - R^2_{\text{cluster}}\,G_U/(G_U + n_L)$, and the optimal $\lambda$ is the cluster-level coefficient shrunk by $G_U/(G_U + n_L)$ | classical survey-sampling variance, and implied by Broska and Howes's equations (8), (11) and appendix C at $\eta_p = 1$. The paper states it as their formula read at the cluster level, and gives the interpretation, the no-gain corollary and the design-target version as its own | Särndal, Swensson and Wretman; Cochran; Broska and Howes |
| Spreading labels over clusters beats labelling whole clusters, for a superpopulation target | shown by Broska and Howes, whose formula also supersedes round 4's condition | Broska and Howes, section 3.3 |
| The regime comparison for the design target, with costs per cluster and per unit and the level term | the paper's own | |
| Intervals designed for the design target with 4 to 16 labelled clusters (finite-population factor, cross-fitting term, $t$ reference), with their coverage as measured | the paper's own. Broska and Howes name small-sample corrections as future work and under-cover at about 113 labelled clusters. The paper's own intervals cover 0.888 to 0.903 in the cross-fitting simulation and 0.855 to 0.950 over the regime-B rows, so it reports coverage, not a guarantee | `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`; `docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, section 3 item 2 |
| The split of a budget between clusters and units per cluster, with a predictor and costs | the paper's own. Broska and Howes name it as future work | |
| Label-free balanced selection of clusters | the principle is classical, and unit-level balanced active inference is Chen et al. The few-cluster comparison with tuned PPI under its conditions is the paper's own | Morgan and Rubin; Fuller; Chen et al., remark 1 |
| Inclusion-probability weighting of labelled clusters | prior art for independent Bernoulli selection of whole clusters. For fixed-size balanced selection with dependent inclusions and few clusters it is open | Kluger et al., appendix B.1 |
| Adaptive selection in batches | prior art at the unit level. A cluster-level, few-cluster version is open | Kluger and Bates, arXiv:2602.16933; Zrnic and Candès |
| The prediction-set map and the joint design | untouched | GHCP as before |

This corrects the overlap check of the same day, which listed the gain theorem among what remains the paper's own (`docs/round07/00_prep/round07_overlap_check.md`, section 3). The overlap check is frozen, so the correction is recorded here and in round 7's reading guide.

So the part of the paper that is clearly its own is the few-cluster, design-target regime and the design questions, which are how many clusters and units to buy, which clusters to label, and what that costs. The asymptotic interval and the gain formula are known, and the paper builds on them.

## 6. What this means for O2 and the PPI track

**Recommendation on O2** `[proposed]`. Accept the reframing, valid inference after histology-guided allocation, with three changes from the overlap check's version.

1. **The core question is narrower and still open.** Horvitz-Thompson and Hájek weighting for fixed-size rejective selection of 4 to 16 clusters with dependent inclusions, with probabilities from simulation and an analytic interval, compared with Kluger et al.'s independent Bernoulli selection with inverse-probability weights and their cluster bootstrap.
2. **Add Broska and Howes's interval as a comparator** in every design of the track. It is closed-form, so it costs little. Showing where it under-covers at 4 to 16 labelled clusters, beside `textbook_t|fpc|lin|xf`, makes the paper's few-cluster contribution concrete.
3. **Add a cluster-level version of Chen et al.'s design** as the adaptive arm (overlap check, adjustment 2). Clusters are drawn with probabilities that mix a label-free score with uniform probabilities, balanced by the cube method. Kluger and Bates's multiwave design is the unit-level reference for doing this in batches. This replaces the overlap check's less specific "probabilities that rise with a diversity score".

The k-center coverage check (overlap check, adjustment 3) stays as written.

**Positioning in the paper** `[proposed]`, for O5. The introduction cites Broska and Howes and Kluger et al. for PPI under cluster sampling with many clusters. It presents the gain formula as the classical variance, in the form of Broska and Howes's appendix C, read at the cluster level. It presents the paper as the few-cluster, design-based and design-choice counterpart, with the balanced-selection comparison set against Chen et al.'s remark 1.

**What happens next.** If Nicolas accepts O2 with these changes, the oversight chat writes the PPI instruction into `docs/round07/i01/ppi/` as a masterplan amendment, and the track runs on Longleaf as round 5's did.

## 7. Decisions, and who makes them

| # | Decision | Who decides | Default until decided |
|---|---|---|---|
| O2 | Round 7's PPI question, as in section 6 | Nicolas | the E5 memo's question as written |
| O5 | The paper's positioning, as in section 5 | Nicolas, with David | the paper claims nothing that section 5 marks as prior art, classical or implied |
