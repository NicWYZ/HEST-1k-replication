# Round 8, the positioning track, the positioning note (gate P3)

*19 October 2026. Revised after the second pass was completed, then checked the same day by an independent agent at the oversight chat's tier, which redid the algebra and enumeration of section 3.2 with its own script and checked every quotation against the sources. It reported 47 findings (5 errors, 10 weak, 32 minor), and all are addressed here. Recommendations are `[proposed]` until Nicolas decides.*

Written by the oversight chat as stage P3 of the positioning track, under the scope `docs/round08/i01/positioning/round08_positioning_scope.md`. It gives a verdict for each claim C0 to C12 of the PPI paper "Labelling budgets for prediction-powered inference with clustered data" against the survey-sampling literature and PPI work newer than round 7's check, scores the masterplan's predictions, and says what follows for the paper and for Nicolas's open decisions. It replaces section 5 of `docs/round07/oversight/round07_ppi_positioning.md` and Part C of `docs/round07/oversight/round07_ppi_results_explained.md` as the account of what the paper can claim, once Nicolas accepts it.

## 1. What was read

### 1.1 The searches

The first pass ran five themes in parallel, one subagent each, one model tier below the oversight chat's model at medium effort. Together they logged 205 queries and kept 129 candidate rows, 27 graded close, 58 related and 44 background (some papers appear under more than one theme). The logs and candidate lists go to `results/round8/positioning/P1_search/` in the gate's pull request. Citation services (Semantic Scholar, and OpenAlex for most calls) were unreachable from the cloud session, so no forward-citation lists were built in the first pass.

The second pass ran three themes at high effort (A, cross-fitting and design-based PPI; B, allocation and the regime comparison; C, balanced selection and conformal prediction), seeded with the references the earlier checks recorded and with the backward citations of the papers read in full. It screened every entry of those reference lists and logged 200 rows, 134 candidate rows and 77 seed lookups, but only 22 of its web searches ran before the session's limit stopped them. The blocked queries and the unfound seeds were then run as pass 2b, again one subagent per theme at high effort, each with its own cap so that together they stayed under the session's limit (A 48 searches, B 45, C 45, none refused). Pass 2b kept 126 candidate rows, 25 graded close, 49 related and 52 background, and looked up 33 seeds, of which 2 (Innocenti and co-authors, 2019 and 2021) could not be confirmed. The logs of the second pass go to `results/round8/positioning/P1_search/pass2/` and `pass2b/`.

### 1.2 Read in full by the oversight chat

The papers' text was read through the browser on Nicolas's Mac, because neither the cloud session nor the Mac's shell can download from arXiv. Papers with an arXiv HTML page were read there with each formula's LaTeX source kept. The others (Sanguiao Sande and Zhang, Snijders, Raudenbush, Legg and Yu, Williams, Hagesæther and Zhang, Chauvet) were read from their PDFs through a text extraction, with the formulas checked against the page where the extraction garbled them. Where a paper is long, the sections bearing on a claim were read in full and the rest skimmed, and this is said for each.

| Paper | What was read | Claims it bears on |
|---|---|---|
| An, Dagdoug, Haziza and Tillé, "Agnostic Model-Assisted Estimation with Machine Learning for Survey Data", arXiv:2609.10904v1, 9 September 2026 | sections 1 to 8, appendices B.1, H.3 and H.4 | C1 |
| María Eugenia Riaño, "Model-assisted estimation with a training subsample", arXiv:2609.04082v2, September 2026 | sections 1, 3.1, 3.3, 4.2, 4.3, 7, the start of 4.4 | C1 |
| Kwon, Yang and Kim, "Sample-split REGression (SREG)", arXiv:2604.07636v1, April 2026 | the main text, sections 1 to 7 | C1 |
| Lu, Shi, Liu and Ding, "Conditional cross-fitting for unbiased machine-learning-assisted covariate adjustment in randomized experiments", arXiv:2508.15664v1, August 2025 | sections 4 and 5.1, 5.3 | C1 |
| Lee and Kim, "Statistical Optimality of Prediction-Powered Inference", arXiv:2606.08730v1, June 2026 | sections 2.1 and 5 | C1 |
| Karim, "Cross-Fitted Survey-Weighted TMLE with Design-Based Variance", arXiv:2606.30918v1, June 2026 | sections 3.2, 3.3 and the assumptions of section 4 | C1 |
| Salerno, Wu and McCormick, "Spatially Robust Inference with Predicted and Missing at Random Labels", arXiv:2603.11368v1, March 2026 | section 3 and section 6 | C1 |
| Dharamshi, Gao and Wakefield, "Exact variance estimation for model-assisted survey estimators using U- and V-statistics", arXiv:2502.11032v1, February 2025 | section 1 | C1 |
| Zrnic and Candès, "Cross-Prediction-Powered Inference", arXiv:2309.16598v3 | sections 3, 4 and 6 | C1 |
| Mani, Xu, Lipton and Oberst, "No Free Lunch: Non-Asymptotic Analysis of Prediction-Powered Inference", arXiv:2505.20178v2 | sections 3, 4.2 and 4.3 | C1 |
| Zhang, Tam, Sanguiao-Sande, Yung and Holmberg, "On design-unbiased algorithmic Machine Learning", arXiv:2606.28795v1, June 2026 | abstract and appendix C | C1 |
| Dagdoug and Haziza, "Machine learning methods for finite population parameter estimation in survey sampling", arXiv:2604.01160v1 | sections 4.2 and 4.3 | none (the term it drops is the nonresponse variance, not a cross-fitting term) |
| Shirota, "Design-Based Prediction-Powered Inference for Spatial Data", arXiv:2608.10356v1, 11 August 2026, and its retitled second version, "Conditional validity of prediction-powered inference for spatially dependent finite populations", v2, October 2026 | v1 sections 1, 2.1, 2.2, 3.1 to 3.4, the opening of 4 and section 7; v2 abstract and introduction | C0, C7 |
| Datta and Polson, "Prediction-Powered Inference with Inverse Probability Weighting", arXiv:2508.10149v2 | abstract and section structure | C0 |
| Ma and Candès, "Optimized Labeling Resource Allocation for Prediction-Assisted Inference via OPAL", arXiv:2606.03211v1, 3 June 2026 | sections 1.1 to 1.3 | C0, C4 |
| Yang, Qu and Li, "Rejective Sampling, Rerandomization and Regression Adjustment in Survey Experiments", arXiv:2109.09930v1, published in JASA 118(542), 1207 to 1221, 2023 | sections 2.2, 3.1, 3.3, 5.2, appendices A1.3 and A5 | C5 |
| Snijders, "Sampling", a chapter in *Multilevel Modelling of Health Statistics*, 2001 | sections 7 and 8 | C4, C12 |
| Legg and Yu, "A comparison of sample set restriction procedures", Survey Methodology 36(1), 69 to 79, 2010 | sections 1 to 3 and section 4 through the simulation set-up | C5, C6, C7 |
| Raudenbush, "Statistical Analysis and Optimal Design for Cluster Randomized Trials", Psychological Methods 2(2), 1997 | the sections on optimal allocation without and with a covariate, and Table 3 (equation bodies garbled in the extracted text) | C4 |
| Williams, "Generating unbiased ratio and regression estimators", Biometrics 17(2), 267 to 274, 1961 | in full, from the open copy in CUNY Academic Works, with equations (1) and (2) checked against the page image | C1 |
| Sanguiao Sande and Zhang, "Design-unbiased statistical learning in survey sampling", arXiv:2003.11423v1, March 2020 (published in Sankhyā A in 2021, as Riaño and Kwon et al. cite it, `[verify]` volume) | in full | C1, C9 |
| Hagesæther and Zhang, "A note on the effect of auxiliary information on the variance of cluster sampling", Journal of Official Statistics 25(3), 397 to 404, 2009 | in full (open PDF from Statistics Sweden) | C12 |
| Chauvet, "On variance estimation for the French Master Sample", Journal of Official Statistics 27(4), 651 to 668, 2011 | sections 1, 2, 3 (design), 5 and 6 | C6, C7 |
| Bouhadra and Dagdoug, "High-dimensional variance estimation for the generalized regression estimator", arXiv:2607.05570, July 2026 | introduction, assumptions and main results, skimmed in the browser | C9, loosely (section 3.9) |

Fuller (2009, Biometrika 96(4)), Yang and Ding (2025, JRSS B, arXiv:2403.01477), Aronow and Samii (2013, Survey Methodology 39(1)) and Fattorini (2006, Biometrika 93(2)) were read from their abstracts only, and the pass 2b sources cited below without a row here were read from their abstracts by the subagents. The textbook results that C2, C3 and C12 rest on (Cochran 1977, Särndal, Swensson and Wretman 1992) were not read, and section 7 asks Nicolas for them.

### 1.3 Limits

- Pass 2b ran every blocked query and seed, but each theme stopped at its cap. The stopping rule (two rounds in a row with no new close paper) was reached for the allocation, regression-with-intercept and conformal (C10) lines, and the cross-fitting lines were reported saturated. The cube-of-clusters line had one round without a new close paper. C7, C8 and C11 were still turning up related items, though no close ones, when the caps were hit. Where each line stopped is recorded in `results/round8/positioning/P1_search/README.md`.
- Forward citations of the anchor papers were not retrieved, because citation services were unreachable. Crossref and PubMed were rate-limited or blocked during pass 2b, so several abstracts are known only from secondary pages, and those rows are marked in the logs.

## 2. Verdicts at a glance

The verdict scale is the scope's four labels. Where a claim needs a qualifier, it goes in the last column. One departure is recorded. C1's cross-fitting term is withdrawn as a defect of round 5's estimator, which none of the four labels describes, and its verdict "classical" applies to the finite-population factor and to the corrected estimator. "The paper's own" is bounded by the search logs.

| ID | Claim | Verdict | What remains the paper's |
|---|---|---|---|
| C0 | Valid inference after prediction-guided selection of the clusters to label | partly held | design-based PPI with unequal, known or estimated inclusion probabilities is in print for units (Kluger et al., Datta and Polson, Shirota v1), and prediction-guided selection of units with valid inference too (Zrnic and Candès, Chen et al., OPAL). Fixed-size, balanced, prediction-guided selection of a few whole clusters with design-based intervals was not found |
| C1 | The finite-population factor and the cross-fitting term of the design-target interval | classical, and the cross-fitting term withdrawn as a defect | no result. For even $n_L$, round 5's estimator is Williams' (1961) exactly unbiased split-sample regression estimator with two groups, except that the factor $1 - n/G$ on his correction term is missing, and the part of the estimator that escapes the finite-population factor is that omission (section 3.2). Which exactly unbiased form behaves best at 6 to 16 clusters is a small open question |
| C2 | Regime A against regime B for the design target with costs | classical `[verify]` against Cochran | the substance is textbook, and what remains is the reading with a machine-learned predictor and the measured numbers |
| C3 | The level term and form C | classical | the principle is classical, and what remains is the diagnosis of round 4's apparent regime-B gain and the constant predictor as the control |
| C4 | Optimal units per cluster with a predictor | classical | replacing $1 - R^2_c$ by the measured $\rho_c(n_L)$ |
| C5 | Rejective selection with `rej_t` | prior art for the interval | balancing on the clusters' mean predictions at 4 to 16 clusters, and the matched comparison with simple random selection, tuned PPI and the cube design |
| C6 | Cluster-level cube design with bounded probabilities and the constant balanced | partly held | the components are classical, and cube selection of primary units with simulated pair probabilities is in print (Breidt and Chauvet 2011, Chauvet 2011). What remains is the bounded mixture of a label-free score with uniform, and the comparison at 6 to 16 clusters |
| C7 | Weighting fails under rejective selection | partly held | the mechanism is classical and the unit-level case is in print (Legg and Yu 2010). What remains is the finding that Mahalanobis rejective selection at small acceptance probability makes some clusters and pairs almost never sampled, at 4 to 16 clusters |
| C8 | Greedy k-center has no design-based variance | classical | the principle goes back to Neyman (1934), and what remains is the measured coverage on the tasks |
| C9 | Comparator check for a small-sample cluster-robust PPI interval | the paper's own, as a check | the correction stays classical (the CR2 form's survey origin is Bell and McCaffrey 2002), and nobody was found to have published it for PPI |
| C10 | The prediction-set map | the paper's own | the map, as in round 5 |
| C11 | The joint design | the paper's own | the joint design, as in round 5 |
| C12 | The gain formula's cluster-level and design-target reading | classical | Cochran's regression estimator on cluster values, with Hagesæther and Zhang (2009) for the anticipated design effect. Only the interpretation remains |

## 3. The claims one by one

### 3.1 C5. `rej_t` is Yang, Qu and Li's variance

Round 5's design D2 draws simple random samples of $n_L$ clusters and accepts the first whose Mahalanobis distance between the labelled and population means of $k$ balance variables is at or below a threshold. Yang, Qu and Li's rejective sampling is the same rule. With $W$ the balance variables (their section 3.1),

$$
M_S = \big(\bar W_S - \bar W\big)^\top\Big\{\Big(\frac{1}{n} - \frac{1}{N}\Big)S^2_W\Big\}^{-1}\big(\bar W_S - \bar W\big) \le a_S .
$$

Their Corollary A5 gives the limiting law of the sample mean under that rule,

$$
\sqrt{n}\,\big(\bar y_S - \bar y\big) \,\big|\, M_S \le a_S \;\dot\sim\; \sqrt{(1 - f)\,S_y^2}\,\Big(\sqrt{1 - \rho^2_{y,W}}\;\varepsilon + \sqrt{\rho^2_{y,W}}\;L_{J,a_S}\Big),
$$

with $\varepsilon$ standard normal, $L_{J,a} \sim D_1 \mid D^\top D \le a$ for $D \sim N(0, I_J)$, and $\rho^2_{y,W}$ the squared multiple correlation of $y$ on $W$. Since $\text{Var}(L_{J,a}) = P(\chi^2_{J+2} \le a)/P(\chi^2_J \le a) = v_{J,a}$, the variance is

$$
\text{Var}\big(\bar y_S \mid M_S \le a_S\big) \approx \frac{1 - f}{n}\,S_y^2\,\Big\{\big(1 - \rho^2_{y,W}\big) + v_{J,a}\,\rho^2_{y,W}\Big\}.
$$

Round 5's target variance (explainer A4) is

$$
\text{Var}_{D2}\big(\bar z_L\big) = \frac{1 - f}{n}\Big(S_e^2 + v_a\,B^\top S_X B\Big), \qquad B = S_X^{-1}S_{Xz}.
$$

With $B^\top S_X B = S_{zX}S_X^{-1}S_{Xz} = \rho^2 S_z^2$ and $S_e^2 = S_z^2 - B^\top S_X B = (1 - \rho^2)S_z^2$, the two expressions are the same, with $y$ read as the cluster contributions $z_g$, $n$ as $n_L$, $N$ as $G$ and $J$ as $k$. The step is the definition of the squared multiple correlation, so no algebra is skipped. Their appendix A5 applies every result to sampling whole clusters, "viewing each cluster as an individual", with cluster totals standardised by the mean cluster size. Their section 5.2 is written for the treatment effect under rejective sampling and rerandomization together, and for the rejective-sampling mean, the special case, it estimates the pieces by sample analogues, as `rej_t` does, and forms the interval from the quantile of the non-normal limit, where `rej_t` uses $t_{n_L - k - 1}$.

So the interval is prior art. The project took $v_a$ from Morgan and Rubin's Theorem 3.1 and cited Fuller (2009) for the principle (round 5's E5 memo, section 4 item 11), and no round cited Yang, Qu and Li or Yang and Ding. The assignment-side counterpart at the cluster level, Mahalanobis rerandomization of clusters with the same truncated-normal limit, is Lu, Liu, Liu and Ding (arXiv:2207.02540, read from the logs and its abstract), which the paper should cite too. What stays the paper's own is the use of the clusters' mean predictions as the balance variable, the behaviour at 4 to 16 clusters, the matched comparison of round 7 (`rej_t` narrowest on census, a little below simple random selection's coverage on tissue), and the failure with two balance variables at few residual degrees of freedom.

What follows is a reading, not a result. The limiting law is a normal plus a truncated normal, which has lighter tails than a normal with the same variance, so a normal or $t$ quantile with the right variance should be conservative in the limit. Yang, Qu and Li's own quantile would then give a narrower interval. Whether that holds at 4 to 16 clusters is not known.

### 3.2 C1. The cross-fitting term is the omission of a classical factor

**The classical estimator.** Exactly unbiased split-sample regression estimators under simple random sampling without replacement date from Mickey (1959, JASA 54(287), not read, cited by Kwon et al. beside Williams) and Williams (1961, Biometrics 17(2)). Williams splits a simple random sample of $n$ from $N$ at random into $k$ equal groups, computes a coefficient $b^{i}$ in each group from that group's own data, and sets $\bar b = \sum_i b^{i}/k$. Since $E\{\bar y + \bar b(\mu_x - \bar x)\} = \mu_y - \text{Cov}(\bar b, \bar x)$ and, given the split, the $k$ groups are a simple random sample of the $s = Nk/n$ groups, he adds the unbiased estimator of that covariance (his equations 1 and 2),

$$
T_k = \bar y + \bar b\,(\mu_x - \bar x) + \Big(1 - \frac{n}{N}\Big)\frac{1}{k(k - 1)}\sum_{i=1}^{k}\big(b^{i} - \bar b\big)\big(\bar x^{i} - \bar x\big),
$$

which is exactly unbiased for any form of $b^{i}$. Averaging $T_k$ over all splits of the sample keeps it unbiased, and in his small example (Table 1) the averaged version had the lower variance, 1.886 against 2.281. For least-squares slopes under a linear model with normal $x$ he finds the best number of groups to be $\sqrt{n/3}$. His section 5 extends the estimator to two-stage sampling of equal-sized primary units. His variance estimator (equation 13) assumes a negligible $n/N$, and he warns that it "can be subject to high sampling error, particularly for small $k$". Sanguiao Sande and Zhang (2020, arXiv:2003.11423) give a general design-based form for any learner and any design. A model is fitted on a subsample $s_1$, the observed values are kept on $s_1$, the model predicts on $U \setminus s_1$, and the errors on $s_2 = s \setminus s_1$ are weighted by the inclusion probabilities conditional on $s_1$. This single split, one way round, is exactly design-unbiased, and they Rao-Blackwellise it by averaging over the splits, with the exact variance decomposition $V(\hat Y^\ast) = E_1 V_2(\hat Y_1 \mid s_1) - E_p V_q(\hat Y_1 \mid s)$ (their equation 3) and an unbiased variance estimator when $|s_2| \ge 2$. In their section 2.3 they note that the averaged coefficient adds a variance of its own, and that the usual term dominates "as long as the sampling fraction n/N is small". Their construction predicts the unsampled units with the training subsample's model, like the fold-wise form below, but uses one subsample at a time rather than two folds with swapped roles. Williams has no intervals or coverage and treats clusters only as primary units with equal subsamples, and Sanguiao Sande and Zhang treat neither clusters nor intervals.

**What is in print since.** Design-based cross-fitting for model-assisted and difference estimators now has a theory at the unit level. Lu, Shi, Liu and Ding (2025) build conditionally independent folds for randomized experiments and an exactly unbiased cross-fitted estimator. An, Dagdoug, Haziza and Tillé (2026) characterise the sampling designs for which a uniform split gives conditionally independent folds (the exponential designs, including simple random sampling without replacement), prove exact design-unbiasedness with conditional inclusion probabilities, and give a variance estimator from cross-fitted residuals. Kwon, Yang and Kim (2026) cross-fit a regression estimator, with ordinary least squares, the lasso or more general learners, under simple random, stratified, conditional Poisson and rejective sampling, and prove first-order equivalence to the estimator with the population coefficient, not exact unbiasedness. Karim (2026) cross-fits at the level of primary sampling units in complex surveys. Lee and Kim (2026) and Zrnic and Candès treat cross-fitted PPI for independent or simple random samples of units. In every one of these the effect of fitting the rule on part of the sample is shown to vanish at first order, so the variance targeted is that of an estimator with the rule fixed. For independent samples, Mani, Xu, Lipton and Oberst (arXiv:2505.20178v2) give the exact finite-sample variance of cross-fitted PPI++ for a mean (their Theorem 4.1),

$$
\text{Var}\big(\hat\theta_{\text{CF-PPI++}}\big) = \frac{\sigma_y^2}{n} - \frac{\sigma_{fy}^2}{n\,\sigma_f^2} + \frac{E\big[(\hat\sigma_{fy} - \sigma_{fy})^2\big]}{n\,\sigma_f^2} + \frac{2\,\big(\sigma_{yf^2} - 2\sigma_{fy}\mu_f\big)^2}{n^2\sigma_f^4},
$$

where the third term is the loss from estimating the coefficient on half the sample and the fourth a cross-term between the folds, both of order $1/n^2$, and for the single-sample PPI++ estimator they show that a plug-in variance treating the coefficient as fixed is optimistic (their Proposition 4.6). That is the independent-sample counterpart of round 5's concern. Zhang, Tam, Sanguiao-Sande, Yung and Holmberg (arXiv:2606.28795) give design-unbiased bias and mean squared error estimators for predictors trained on one simple random subsample and evaluated on the rest, with explicit finite-population factors. María Eugenia Riaño (2026) argues the opposite principle for a single split, that "whoever splits a sample and reports a number that depends on the split carries this second phase in the uncertainty of that number", and derives the exact decomposition $V(\hat Y_{TS}) = V_1 + E_p(V_2)$. Dharamshi, Gao and Wakefield (2025) give an exact variance for the regression estimator that includes the fitting uncertainty, and Salerno, Wu and McCormick (2026) correct a spatial variance for noise shared within folds.

**Round 5's term.** Round 5's estimator (`docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`), with every unit of a labelled cluster labelled, is in the form of round 5's theory, section 2.0,

$$
\hat\theta = c'\,\bar F + \frac{1}{n}\sum_{g \in L}\big(z_g - \lambda_{(g)}\,f_g\big), \qquad c' = \frac{n_B\lambda_A + n_A\lambda_B}{n},
$$

where $\lambda_{(g)}$ is the coefficient fitted on the half that does not contain $g$. Draw by draw it splits as

$$
\hat\theta = \underbrace{\bar z_L - c'\,(\bar f_L - \bar F)}_{T_1} \; - \; \underbrace{\kappa\,(\lambda_B - \lambda_A)(\bar f_A - \bar f_B)}_{T_2}, \qquad \kappa = \frac{n_A n_B}{n^2},
$$

after algebra that is skipped (round 5's theory, section 2.0). $T_1$'s variance carries $1 - n/G$, and $T_2$'s does not. At $n = G$, $T_1 = \theta$ exactly while $T_2 \ne 0$.

**For even $n_L$ it is Williams' estimator without his factor.** Take equal halves, $n_A = n_B = n/2$, which round 5's split gives whenever $n_L$ is even, so that $\kappa = 1/4$ and $c' = (\lambda_A + \lambda_B)/2$. Read Williams with $k = 2$, the halves as his groups, $b^{A} = \lambda_A$ and $b^{B} = \lambda_B$, and the cluster contributions $z_g$ and mean predictions $f_g$ as his $y$ and $x$. Then $\bar b = c'$, and $T_1 = \bar z_L + c'(\bar F - \bar f_L)$ is his uncorrected estimator. His correction term is
$$
\Big(1 - \frac{n}{G}\Big)\frac{1}{2}\Big\{\big(\lambda_A - c'\big)\big(\bar f_A - \bar f_L\big) + \big(\lambda_B - c'\big)\big(\bar f_B - \bar f_L\big)\Big\} = \Big(1 - \frac{n}{G}\Big)\frac{1}{4}\big(\lambda_A - \lambda_B\big)\big(\bar f_A - \bar f_B\big) = -\Big(1 - \frac{n}{G}\Big)T_2 ,
$$
because $\lambda_A - c' = (\lambda_A - \lambda_B)/2$ and $\bar f_A - \bar f_L = (\bar f_A - \bar f_B)/2$, and likewise for $B$. So
$$
\hat\theta_{\text{Williams}} = T_1 - \Big(1 - \frac{n}{G}\Big)T_2, \qquad \hat\theta_{\text{round 5}} = T_1 - T_2 .
$$
Round 5's cross-fitting adds Williams' covariance correction without the finite-population factor that his equation (1) carries, so $\hat\theta_{\text{round 5}} = \hat\theta_{\text{Williams}} - (n/G)\,T_2$, and that difference is the part of the estimator that escapes $1 - n/G$. Round 5's variance term for it, $(n/G)\,\overline{(\lambda_{(g)} - c')^2}_L\,s_f^2/n$, is an approximation to the price of that difference, not its exact variance. For $n < G$, Williams' equation (1) also gives $E(T_2) = -\text{Cov}(c', \bar f_L)/(1 - n/G)$, so round 5's estimator has design bias
$$
E\big(\hat\theta_{\text{round 5}}\big) - \theta = \frac{n/G}{1 - n/G}\,\text{Cov}\big(c', \bar f_L\big),
$$
for even $n < G$. It vanishes as $n/G \to 0$, and whenever $\text{Cov}(c', \bar f_L) = 0$, for instance with a fixed coefficient or with round 5's coefficient of zero below six clusters. At $n = G$ the formula does not apply, and the bias there is $-E(T_2)$. This agrees with round 5's theory (section 2.0), which found $\delta$ and $\Delta$ "independent up to finite-population terms, and $E[T_2] = 0$" under a normal population, not under skewness, and which already called the estimator only approximately unbiased (section 2.1). What Williams adds is the exact bias for any population and the one-factor fix. This is the oversight chat's derivation from the two definitions. It was checked by exact enumeration over every sample and every equal split of a toy population of 10 clusters with a nonlinear relation between $z$ and $f$ (`results/round8/positioning/checks/williams_vs_r5.py` and its output, in the gate's pull request), and again by the independent checker with its own script on two populations and three coefficient rules. The identities held to rounding error in every draw, Williams' estimator was unbiased to about $10^{-15}$, and round 5's bias equalled the formula at every $n < G$. How much it matters depends on the coefficient rule. With the unclipped slope of each half, round 5's bias was $-0.090$, $+0.058$, $+0.159$ and $+0.169$ at $n$ of 4, 6, 8 and 10, and the standard deviations, Williams' first, were 7.44 and 9.44, 0.91 and 1.42, 0.29 and 0.43, and 0 and 0.23. With round 5's own rule, the slope clipped to $[0, 1]$ and set to zero below six clusters, the two estimators coincide at $n = 4$, and at $n$ of 6, 8 and 10 round 5's bias was $+0.011$, $+0.012$ and $+0.009$, with standard deviations 0.547 and 0.555, 0.325 and 0.328, and 0 and 0.034. So under round 5's rule the defect is small against the sampling error except near a census, and the clipping is what keeps it small. One toy population shows the mechanism, not the size of the effect on the project's tasks. With unequal halves (odd $n_L$) Williams' groups are not equal and his construction does not apply directly, while the fold-wise form below does.

Riaño's intermediate term, for a linear rule $m_1(x) = \lambda_1 f(x)$ against a full-sample $\hat\lambda f(x)$, is

$$
T_1^{\text{Riaño}} = \sum_{k \in U}\Big(1 - \frac{I_k}{\pi_k}\Big)\big(\lambda_1 - \hat\lambda\big)f_k = \big(\lambda_1 - \hat\lambda\big)\Big(\sum_{k \in U}f_k - \sum_{k \in S}\frac{f_k}{\pi_k}\Big),
$$

a coefficient difference times the Horvitz-Thompson error of the prediction total, which is zero at a census. Round 5's $T_2$ is a coefficient difference times the gap between the two halves of the sample, which is not. They belong to the same family and are different terms.

**The fold-wise form.** The fold-wise form of Lu et al., An et al. and Kwon et al. splits the unlabelled clusters between the folds as well, $U_j = S_j \cup R_j$, and applies the same coefficient to both parts of a fold,

$$
\hat\theta_{\text{fold}} = \sum_{j \in \{A, B\}}\frac{N_j}{G}\Big\{\lambda_{(-j)}\,\bar F_{U_j} + \bar z_{S_j} - \lambda_{(-j)}\,\bar f_{S_j}\Big\},
$$

with $N_j = |U_j|$ and inclusion probabilities $n_j/N_j$ conditional on the split. At $n = G$ every $R_j$ is empty, $U_j = S_j$, and $\hat\theta_{\text{fold}} = \sum_j (n_j/G)\,\bar z_{S_j} = \theta$ exactly. So the term that escapes the finite-population factor belongs to round 5's form of cross-fitting, not to cross-fitting under sampling without replacement as such. Both Williams' estimator and the fold-wise form are exactly unbiased and exact at a census. How either behaves at 6 to 16 labelled clusters, where round 5's coefficient is not zero, is not known. Given the split, the fold-wise form's two folds are independent simple random samples, but each fold's coefficient depends on the other fold's sample, so the cross-covariance between folds, which the first-order theory drops, may matter at these sizes. For Williams' form the open piece is a variance estimator that does not assume a negligible $n/G$ and is stable with two groups.

**Verdict.** Classical for the finite-population factor and for the corrected estimator, with the cross-fitting term withdrawn as a defect (a departure from the scope's four labels, recorded in section 2). The finite-population factor is classical, the exactly unbiased split-sample regression estimator with its finite-population correction is Williams (1961), its general design-based form is Sanguiao Sande and Zhang (2020) and the fold-wise papers of 2025 and 2026, and the extra variance from a cross-fitted coefficient at small samples is in print for independent sampling (Mani et al.). Round 5's term is not a result the paper can claim. It is a defect of round 5's estimator, and the survey-sampling literature that a referee would know contains the fix. The paper should adopt an exactly unbiased form, Williams' with $k = 2$ when the halves are equal or the fold-wise form, and cite both. The cross-fitting term in the variance of round 5's estimator definition (the second term of its variance) is then expected to be unnecessary in that form, but the variance of $T_1 - (1 - n/G)\,T_2$ is not $1 - n/G$ times a fixed quantity, so this has to be checked, together with a variance estimator for the corrected form. Choosing between the forms at few clusters, and against Williams' version averaged over all splits, is a candidate run (section 6.4).

### 3.3 C4. The allocation formula is classical

Snijders (2001, section 7, eq. 12), citing Cochran (1977, section 10.6), gives the optimal number of units per level-two unit under the cost $c_1 N + c_2 N n \le k$ and the variance $\sigma_1^2/N + \sigma_2^2/(Nn)$,

$$
n_{\text{opt}} = \sqrt{\frac{c_1\,\sigma_2^2}{c_2\,\sigma_1^2}} .
$$

His section 8 (eq. 13) gives the reduction from controlling for a covariate $Z$ with residual within and between correlations $\rho_W$ and $\rho_B$,

$$
\tilde\sigma^2 = \big(1 - \rho_W^2\big)\,\sigma^2, \qquad \tilde\tau^2 = \big(1 - \rho_B^2\big)\,\tau^2,
$$

applied to the estimation variances in a large-sample approximation. Substituting the second display into the first, with the predictor as $Z$,

$$
n_{\text{opt},Z} = n_{\text{opt}}\sqrt{\frac{1 - \rho_W^2}{1 - \rho_B^2}},
$$

which is round 5's fixed-coefficient allocation $m^\star\sqrt{(1 - R^2_w)/(1 - R^2_c)}$. Snijders does not write this last line, but it is a substitution of one of his displays into the other. Raudenbush (1997, Psychological Methods 2(2), read from an open copy) states it to leading order. His covariate optimum (eq. 24, solved approximately) "is dominated by" the no-covariate form of his eq. (9) with the covariate-adjusted within and between variances, and his Table 3 applies it with a covariate explaining 73% of the between-cluster and 48% of the within-cluster variance. Recomputing all 15 rows of his table from the formula reproduces each to within one unit, for example at $\rho = 0.05$ and a cost ratio of 10,

$$
\sqrt{\frac{1 - \rho}{\rho}\cdot 10} = 13.8, \qquad 13.8 \times \sqrt{\frac{1 - 0.48}{1 - 0.73}} = 19.1,
$$

against 19 in his table, and likewise 43.7 against 43 at $\rho = 0.01$ with a cost ratio of 10. The replacement of $1 - R^2_c$ by the measured between ratio $\rho_c(n_L)$, which prices the cross-fitted coefficient and its zero value below six clusters, is the project's own. It is a small step. The PPI-side allocation papers of 2026 (OPAL, Ye and Yoganarasimhan arXiv:2604.17267, Ye, Lyu and Tao arXiv:2604.12497) allocate labels over units, tasks or strata, the two Ye papers with a cost per label across tasks, and none has a two-level cost model. Chen, Guo and Li (arXiv:2603.16041) give a power analysis for PPI rather than an allocation. Apart from OPAL's sections 1.1 to 1.3, these were read from their abstracts and the first-pass summaries.

### 3.4 C12. The design-target gain is the classical regression estimator

With whole clusters labelled by simple random sampling of $n$ of $G$, the difference estimator with a fixed coefficient $\lambda$ has

$$
\text{Var}\big(\bar z_L - \lambda(\bar f_L - \bar F)\big) = \Big(1 - \frac{n}{G}\Big)\frac{S^2_{z - \lambda f}}{n},
$$

minimised at $\lambda_c = S_{zf}/S_f^2$, where it equals $(1 - n/G)\,S_z^2\,(1 - R^2_{\text{cluster}})/n$. The ratio to the classical mean is $1 - R^2_{\text{cluster}}$, with the unshrunk coefficient. This is the variance of the regression estimator under simple random sampling (Cochran 1977, chapter 7 `[verify]` section) applied to cluster-level values, so the design-target version is classical. The no-gain corollary, that at large cluster size a predictor helps only through its between-cluster correlation, is Snijders' eq. (13) read for a level-two quantity. Round 7 had already found the superpopulation version implied by Broska and Howes. Hagesæther and Zhang (2009, read in full) give the anticipated-variance form under simple random sampling of clusters. A GREG estimator fitted at the cluster level has the design variance of the Horvitz-Thompson estimator with $y_k$ replaced by the residual $e_k$, and under a constant intra-cluster correlation model for the residuals its anticipated design effect against element sampling is $1 + \rho_e(N^\ast - 1)$, with $\rho_e$ the intra-cluster correlation conditional on the covariates and $N^\ast = \sum_k N_k^2/N$. Auxiliary information helps "to the extent it reduces the conditional intra-cluster correlation given the covariates". Their comparison is with element sampling, not with the classical cluster mean, so it is not the same formula. The two meet in what drives the gain. Under their model the cluster-level residual variance is $N_k\sigma_e^2\{1 + (N_k - 1)\rho_e\}$ against $N_k\sigma_y^2\{1 + (N_k - 1)\rho_y\}$ without covariates, and for large clusters the ratio of the two is close to $\sigma_e^2\rho_e/(\sigma_y^2\rho_y)$, the share of between-cluster variance that the covariates leave, which is $1 - R^2_{\text{cluster}}$ when $R^2_{\text{cluster}}$ is read at the cluster level. That is the oversight chat's reading of their model, not a statement they make. They use a classical estimator and no machine-learned predictor.

### 3.5 C2 and C3. Classical

Regime B with every cluster partly labelled is two-stage sampling with every cluster in the first stage, which is stratified sampling with the clusters as strata. Regime A is one-stage cluster sampling. That the between-cluster variance does not enter a stratified design, and the comparison of the two designs with a cost per cluster and per unit, are textbook (Cochran 1977, chapters 5 and 9 to 11 `[verify]`). With a predictor the residual variances replace the raw ones, as in section 3.3. Form C, a regression estimator with a cluster-specific intercept and a common prediction coefficient, belongs to the separate and combined regression estimators (Cochran 1977, section 7.10 `[verify]`), and the level term is the classical reason a regression estimator carries an intercept, as the round-7 explainer already says. These verdicts wait on reading the chapters (section 7).

Pass 2b found the pieces of C2 in separate places and nowhere together. The cost function with a cost per cluster and a cost per unit is in Cohen (1998, Journal of Official Statistics 14(3)) and in Moerbeek, van Breukelen, Ausems and Berger (2003, Understanding Statistics 2(3)), without a predictor. Allocation of units within a fixed set of primary units, which is regime B, is a routine in the PracTools package of Valliant, Dever and Kreuter (2018), whose theory is in chapter 9 of their book. The design effect with auxiliary information is Hagesæther and Zhang (2009), without costs. For C3, Shao and Wang (2014, Statistica Sinica 24(1)) compare regression estimators fitted within strata and across strata, and find that the ranking turns between few large strata and many small ones, which is regime B's situation. No source compared labelling whole clusters with labelling a few units in every cluster under a cost model and with a predictor. All of these were read from their abstracts or from secondary pages, and the subagent's transcriptions of the cost formulas came from garbled extractions.

### 3.6 C6 and C7. Partly held, with few-cluster findings

The cube method (Deville and Tillé 2004) balances chosen variables under prescribed inclusion probabilities. Estimating first- and second-order inclusion probabilities by simulating the design and plugging them into the Horvitz-Thompson and Sen-Yates-Grundy forms is Fattorini (2006), which round 7 did not cite. Mixing an informative score with uniform probabilities is Chen et al.'s $\tau$, and the robust sampling of Li, Zrnic and Candès (arXiv:2511.08991) mixes toward uniform as well. That zero pair probabilities make the design variance not unbiasedly estimable is classical (a design is measurable only if every $\pi_{gh} > 0$; Särndal, Swensson and Wretman 1992 `[verify]` section), Shirota v1 restates it for one-per-block designs, and Aronow and Samii (2013) give a weakly conservative correction for such designs, which round 7 did not try. Closest of all, Legg and Yu (2010, Survey Methodology 36(1), read from the open PDF through the simulation set-up of section 4) compare Fuller's rejective sampling with cube sampling by simulation, for units, with samples of 20 from 100 and of 80 from 400 (the population replicated four times, under Poisson initial sampling). They state that rejective sampling changes the first-order inclusion probabilities, units near the population mean becoming more likely, and that "very tight balancing can lead to a design with some extreme joint inclusion probabilities, including zero inclusion probabilities". To illustrate the first point they estimate first-order inclusion probabilities from 100,000 simulated samples (their Figure 1). They note that simulated probabilities can give nearly unbiased Horvitz-Thompson estimators but that this is impractical for large populations, and in their comparison they use the regression estimator with the initial probabilities, at 30,000 samples per simulation. They balance the cube design on $(p_i, x_i)$ to fix the sample size. They report no interval coverage. So the mechanism of C7 and the rejective-against-cube comparison are in print for units.

Cube selection of primary units, and simulated pair probabilities for it, are in print as well. Chauvet (2011, read in sections 1 to 3, 5 and 6) describes the French Master Sample, where interviewer action areas built from small municipalities are selected by the cube method with probabilities proportional to size and balanced on area totals. The Yates-Grundy estimator is used with pair probabilities estimated from 10,000 simulated replicates of the design through the martingale form of Breidt and Chauvet (2011, Journal of Statistical Planning and Inference 141, 479 to 487, not read). That estimator had relative bias under 6% in his simulation. Deville and Tillé's (2005) maximum-entropy approximation was "systematically negatively biased", because it "fails to track the variance due to the landing phase", which "may be appreciable even if the balancing variables have a small explanatory power". Thompson and Wu (2008, Survey Methodology 34(1) `[verify]` pages) estimate first- and second-order inclusion probabilities of clusters by simulation under randomized systematic sampling with substitution (abstract). Both treat many primary units. At few clusters the landing phase is most of the design. Dirdaitė and Krapavickaitė (2016, Lithuanian Journal of Statistics 55(1)) report from a simulation that cube balance was poor with 100 clusters because of the landing phase and good with 5,000 (abstract). That is a reason to expect the cube design at 15 to 50 clusters to balance only loosely on anything beyond the constant and $\pi$, and the paper should report the achieved balance. What the paper keeps is the finding at 4 to 16 whole clusters balanced on their mean predictions, measured by interval coverage on matched real cells. There, Mahalanobis rejective selection at small acceptance probability leaves some clusters almost never selected and some pairs never together, and a cluster-level cube design with bounded probabilities and the constant balanced is valid at 6 to 16 clusters and matches `rej_t` on tissue.

### 3.7 C8. Classical

That purposive selection gives no basis for design-based inference goes back to Neyman (1934, JRSS 97(4), 558 to 625), whose purposive districts were chosen to match control variables to their population values, which is what k-center does with the predictions. The pass 2b subagent read a copy and reports his point that without random selection there is no room for standard errors, and that with a few large districts most strata hold zero or one district. The oversight chat has not read it. Greedy k-center is a coreset rule from active learning (Sener and Savarese 2018) `[verify]`. The measured coverage of the classical interval under k-center on the kidney tasks, 0.326 to 0.458 (`docs/round07/i04/ppi/round07_ppi_final_decisions.md`, section 2 item 5), is an illustration the paper can report, not a method.

### 3.8 C0. The framing

Design-based PPI with known or estimated unequal inclusion probabilities is in print for units (Kluger et al., Datta and Polson, Shirota v1 section 4), and so is prediction-guided selection of units with valid inference (Zrnic and Candès's active inference, Chen et al., OPAL). Shirota's second version narrows to the conditional validity of calibrated residual-regression PPI and drops the design results of the first. What was not found is fixed-size, balanced selection of a few whole clusters driven by the predictions, with a design-based interval, which is the paper's setting.

### 3.9 C9. No published small-sample cluster-robust PPI interval

The second theme searched for a small-sample correction ($t$ reference, $n - 1$ divisor, CR2, wild cluster bootstrap) applied to a cluster-robust PPI interval and found none. The correction stays classical (Cameron and Miller; MacKinnon, Nielsen and Webb), round 3 had used it, and R7-5 stands as round 7 framed it. Pass 2b found its survey-sampling lineage, which the paper should cite beside the econometric one. Bell and McCaffrey (2002, Survey Methodology 28(2)) introduced bias-reduced linearization, the survey origin of the CR2 form, with a Satterthwaite degrees of freedom for multi-stage samples with few primary units. Kennel and Valliant (2019, Survey Methodology 45(3)) apply leverage adjustments to the sandwich variance of the GREG estimator in cluster samples. Jang and Eltinge (2009, Survey Methodology 35(2)) report that Satterthwaite-type degrees of freedom can be badly misjudged with few primary units per stratum. Imbens and Kolesár (2016) and Pustejovsky and Tipton (2018) are the general small-sample references. None of them treats PPI. These were read by the pass 2b subagent from abstracts, from Kennel and Valliant's introduction and from a fetched summary of Jang and Eltinge, not by the oversight chat. On the PPI side, Eyre and Madras (arXiv:2411.12665) show that PPI++ with few labels can do worse than the classical estimator, which bears on the regime but not on clusters.

### 3.10 C10 and C11. The paper's own

GHCP (Mallick et al., arXiv:2608.15500) still has only its first version. The fifth theme found no paper that compares the full conformal set built from the target cluster's own residuals with HCP or GHCP, and no paper that splits one labelling budget between PPI and prediction sets. The full conformal set itself is classical (Vovk, Gammerman and Shafer 2005), as round 5 said. Pass 2b found three neighbours, none close to the claims. Csillag, Dall'Antonia, Struchiner and Goedert (arXiv:2510.16166) impute with a conformal set predictor inside PPI, Ilyas and co-authors (ICML 2026) treat the number of calibration labels as a cost against set width with a stopping rule, and Dunn, Wasserman and Ramdas (arXiv:1809.07441) give conformal sets for two-level grouped data. None splits one labelling budget between inference and prediction sets, and none compares the target cluster's own full conformal set with hierarchical methods. GHCP's abstract names no baselines, so its full text should be checked for such a comparison before the paper claims the map. The map of which method is narrowest, and the joint design, stay the paper's own.

### 3.11 Regrade of the close rows

The scope asks the oversight chat to regrade every row the subagents graded close. The table merges the three passes, one row per paper (46 papers, with duplicates across themes merged), and gives how each was read and the oversight chat's grade. Papers read in full or in sections have their setting, estimator, variance, design and sample sizes in the sections above. For the rest, the grade rests on the subagents' abstracts and is provisional, as the scope says. That falls short of the scope's rule that every close paper is read in full, and the shortfall is the abstract-only rows below.

| Paper | Pass | Read by the oversight chat | Regrade | Claim and reason |
|---|---|---|---|---|
| Williams 1961, Biometrics | 2 | in full | close | C1, holds the corrected estimator (3.2) |
| Mickey 1959, JASA | 2 | no | close | C1, the companion paper, to obtain (section 7) |
| Sanguiao Sande and Zhang 2020 | 2b | in full | close | C1, design-unbiased split with any learner (3.2) |
| Sanguiao-Sande, Zhang and Lee, slides and ISI abstract | 2b | no | related | C1, the same construction extended to predictive inference |
| An, Dagdoug, Haziza and Tillé 2026 | 1 | sections | close | C1, the fold-wise form (3.2) |
| Lu, Shi, Liu and Ding 2025 | 1, 2 | sections | close | C1, the fold-wise form for experiments (3.2) |
| Mani, Xu, Lipton and Oberst 2025 | 2 | sections | close | C1, exact variance for independent samples (3.2) |
| María Eugenia Riaño 2026 | 1 | sections | related | C1, a different term of the same family (3.2) |
| Karim 2026 | 2 | sections | related | C1 and C0, cross-fitting of primary units, first order |
| Dagdoug and Haziza 2026, arXiv:2604.01160 | 1 | sections | background | the term it drops is the nonresponse variance |
| Dagdoug, Goga and Haziza 2023, JASA | 1 | no | related | C1, random forests in model-assisted estimation, units |
| Bouhadra and Dagdoug 2026 | 2b | skimmed | related | C9, variance estimators with many covariates (3.9) |
| You, Iowa State dissertation | 2b | no | related | C1 and C9, a cross-validated variance for regression estimators |
| Su and Ding 2021, JRSS B | 2b | no | related | C1 and C12, cluster-level regression adjustment in experiments, many clusters |
| Shirota 2026, v1 and v2 | 1, 2 | sections | close | C0 and C7 (3.6, 3.8) |
| Datta and Polson 2025 | 1 | abstract and structure | close | C0, design-based PPI with inverse probability weights (3.8) |
| Broska and Howes 2026 | 1, 2, 2b | in full in round 7 | close | C9 and R7-5, cluster-robust PPI, many clusters |
| Broska, Howes and van Loon 2025, SMR | 2b | no | related | C2, a cost-constrained design without clusters, to obtain |
| Yang, Qu and Li 2023 | 1 | sections | close | C5, prior art (3.1) |
| Fuller 2009 | 1 | no | close | C5, the principle, to obtain |
| Legg and Yu 2010 | 1 | sections | close | C7, the unit-level case (3.6) |
| Snijders 2001 | 1 | sections | close | C4, classical source (3.3) |
| Raudenbush 1997 | 2 | sections | close | C4, classical source (3.3) |
| Moerbeek 2006, Stat Med | 2b | no | related | C4 and C2, to obtain |
| Moerbeek, van Breukelen, Ausems and Berger 2003 | 2b | no | related | C2, cost model without a predictor (3.5) |
| Cohen 1998, JOS | 2b | no | related | C2, cost model without a predictor (3.5) |
| Shao and Wang 2014, Statistica Sinica | 2b | no | related | C3, separate and combined regression estimators (3.5) |
| Hagesæther and Zhang 2009 | 1, 2b | in full | close | C12, classical source (3.4) |
| Kennel and Valliant 2019 | 1, 2b | no | related | C9 (3.9) |
| Kennel 2013, Maryland dissertation | 2b | no | related | C9 |
| Bell and McCaffrey 2002 | 2b | no | related | C9, the survey origin of CR2 (3.9) |
| Jang and Eltinge 2009 | 2b | no | related | C9 (3.9) |
| Chauvet 2011, JOS | 2b | sections | close | C6 (3.6) |
| Thompson and Wu 2008 | 2b | no | related | C6 and C7 (3.6) |
| Fattorini 2009, Computational Statistics | 2b | no | related | C6 and C7, the follow-up to Fattorini 2006 |
| Dirdaitė and Krapavickaitė 2016 | 2b | no | related | C6 (3.6) |
| Neyman 1934, JRSS | 2b | no | close | C8, classical source (3.7) |
| Lu, Liu, Liu and Ding, arXiv:2207.02540 | 1, 2 | no | related | C5, rerandomization of clusters in experiments (3.1) |
| Mallick et al., GHCP, arXiv:2608.15500 | 1 | no | close | C10, a method the map compares, full text to check (3.10) |
| GHCP code repository | 1 | no | background | C10 |
| Lee, Barber and Willett, HCP, arXiv:2306.06342 | 1 | used in round 5 | close | C10, a method the map compares |
| Dunn, Wasserman and Ramdas 2023, JASA | 1, 2b | no | related | C10 (3.10) |
| Duchi, Gupta, Jia and others, arXiv:2403.16336 | 1 | no | related | C10, multi-environment prediction sets |
| Dobriban and Yu, SymmPI, arXiv:2312.16160 | 1 | no | background | C10 |
| Csillag, Dall'Antonia, Struchiner and Goedert, arXiv:2510.16166 | 2b | no | related | C11 (3.10) |
| Ilyas, Ko, Tang, Wu and Zhang, ICML 2026 | 2b | no | related | C11 (3.10) |

## 4. The predictions, scored

Scored as the masterplan's "How they are scored" paragraph fixed them.

- **P.1** (a) refuted. An et al. handle the dependence between folds by conditioning on the split (honest schemes, exact unbiasedness with conditional inclusion probabilities), not by adding a variance term, and their variance is the oracle's. (b) held, no clusters as sampling units. (c) held, normal intervals. The "So" part refuted as written, since the substance of round 5's term is not in their paper. Its conclusion, that the substance of the term is in print at the unit level, turned out true through Williams (1961), which the prediction did not anticipate. Overall partly held.
- **P.2** held for the part that counts. Shirota v1's inference after map-dependent selection uses estimated propensities under independent Bernoulli labelling with a sandwich variance, not fixed-size rejective or cube selection.
- **P.3** held. OPAL learns unit-level labelling probabilities under an expected budget and has no cost per cluster or per unit.
- **P.4** held. The $(1 - R^2_c)$ form follows from Snijders' eq. (12) and (13), and Raudenbush (1997) states and applies it to leading order (section 3.3).
- **P.5** held. Datta and Polson (arXiv:2508.10149, 2025) is graded close for C0 in the first pass and by the oversight chat (section 3.11), and was not in the repository at the opening commit. The logs also grade Lu, Shi, Liu and Ding (2025) and Karim (2026) close for C0 among other claims, and neither was in the repository. Yang and Ding (JRSS B 2025) is graded related in the logs, and OPAL was already in the repository at the opening commit, so neither counts. The closest paper found for C5, Yang, Qu and Li, is dated 2021 and 2023 and so falls outside the prediction's window, as do Fattorini (2006) and Aronow and Samii (2013) for C6 and C7.

## 5. Corrections to the record

Frozen documents are not edited, so these are recorded here and go into round 8's reading guide.

1. Round 5's `rej_t` is the cluster-level, plug-in form of Yang, Qu and Li's Corollary A5 with a $t$ reference (section 3.1). Round 7's positioning note (section 5, row "Label-free balanced selection") and explainer (Part C) call the principle classical and the few-cluster comparison the paper's own. The interval itself is prior art, and Yang, Qu and Li and Yang and Ding should be cited beside Fuller and Morgan and Rubin.
2. Round 7's explainer (Part B) and positioning note (section 5) call the allocation result the paper's own. Its fixed-coefficient form is classical (section 3.3).
3. Round 7's explainer (Part C) lists the design-target regime comparison, costs and the level term as the paper's own. Their substance is classical, pending the textbook check (section 3.5).
4. Round 7's simulated inclusion probabilities, its finding about zero pair probabilities, and its comparison of rejective and cube selection have antecedents that it did not cite, Fattorini (2006), Aronow and Samii (2013) and Legg and Yu (2010).
5. For even $n_L$, round 5's cross-fitted estimator (`docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`) is Williams' (1961) unbiased split-sample regression estimator with two groups, without the factor $1 - n/G$ on its covariance correction (section 3.2). For $n_L < G$ it therefore has a design bias of $\{(n/G)/(1 - n/G)\}\,\text{Cov}(c', \bar f_L)$, which round 5's theory had called zero up to finite-population terms under normality, and the part of the estimator that escapes the finite-population factor, which round 7 counted among the paper's own results, is that omission. Under round 5's clipped coefficient the bias was small in the toy check. Round 5's theory, its E3a unit and round 7's positioning note did not cite Mickey (1959) or Williams (1961), though Kwon et al. cite both.
6. The masterplan of round 8 first presented Shirota's paper as new. It was found in round 3 and checked from its abstract in the deck-2 check (corrected before the first commit, recorded in the progress log).

## 6. What this means

### 6.1 The paper's own ground, after this check

What survives as the paper's own is mostly empirical. It consists of the few-cluster comparison of prediction-guided cluster selection designs (rejective with `rej_t`, the cube design with the constant balanced, the mixture, k-center and weighting) on matched cells of real tasks, the prediction-set map with its switch from HCP to the target donor's own full conformal set at 9 labelled spots, and the joint design. No technical result survives. The cross-fitting term, the last candidate after the first pass, turned out to be the omission of a factor that Williams' 1961 estimator carries (section 3.2). Every formula the paper would display is classical or in print, and the paper's contribution would be the regime, the empirical comparison and the synthesis. For the ML venues and top statistics journals Nicolas prefers, that is a weak position for a methods paper, and the oversight chat's view is that the paper needs a methodological core of its own before it is written.

### 6.2 Options for that core `[proposed]`

These are directions for the paper plan, each to be checked against the literature before any work.

1. **Small-sample, design-based inference after prediction-guided selection of few clusters.** Every design-based interval and coverage guarantee found here is asymptotic in the number of units or clusters, though some point estimators are exactly unbiased. Exact or finite-sample guarantees at 4 to 16 clusters (randomization inference over the selection design, which Yang, Qu and Li's appendix A3 starts for tests, or a finite-sample bound for balanced designs) would be new and would carry the paper's empirical findings. The nearest literature to check first is constrained randomization in cluster randomized trials with few clusters, where pass 2b found Siddique, Li and O'Brien (2024, Trials 25), a factorial trial with 8 to 12 clusters, reporting that unadjusted inference after constrained randomization is conservative (abstract).
2. **The selection design as the object.** Choosing inclusion probabilities and balance variables for a few clusters to minimise the design variance of PPI, with the floor on probabilities that keeps the design measurable, as a design problem with a theory, rather than a comparison of existing designs.
3. **Prediction sets and inference under one budget.** C10 and C11 are untouched by every search, and a theory of the joint allocation would be the paper's own. R8-1 decides whether this stays in the paper.

### 6.3 The open decisions

- **Q3,** which result leads. The search removes the regime comparison, the allocation formula, `rej_t` and the cross-fitting term as leads. What can lead is one of section 6.2's directions, or the empirical few-cluster design comparison if the paper is pitched as an empirical and design study.
- **R7-5,** the positioning against Broska and Howes. This check does not change it. The correction is classical and unpublished for PPI, and its survey lineage (section 3.9) should be cited.
- **R7-6,** a global coefficient below six clusters. Section 3.2 bears on it, since Williams' form and the fold-wise form also define the coefficient at small $n_L$. The validation run should compare round 5's form, Williams' form, the fold-wise form and the global coefficient together.
- **R7-7,** which balanced design the paper recommends. Since `rej_t` is prior art, recommending it costs nothing in novelty and the paper should cite Yang, Qu and Li for it. Their quantile is a candidate improvement (section 3.1).
- **R8-1,** whether the prediction-set half stays. It is now among the few untouched parts, which argues for keeping it or for making it the centre (section 6.2, item 3).

### 6.4 Candidate runs for the execution track `[proposed]`

1. Round 5's cross-fitted estimator against Williams' estimator with $k = 2$ (a one-line change, the cross term multiplied by $1 - n_L/G$), Williams' estimator averaged over all splits (or Sanguiao Sande and Zhang's Rao-Blackwellised form), the fold-wise construction of Lu et al. and An et al. at the cluster level, and the global coefficient, at $n_L$ of 4 to 16, with bias, variance and coverage on the simulation grid and the real tasks (R7-6 and C1). For Williams' form this needs a variance estimator that does not assume a small $n_L/G$.
2. `rej_t` with Yang, Qu and Li's quantile in place of $t_{n_L - k - 1}$.
3. Aronow and Samii's conservative variance under rejective selection, against round 7's negative result.

### 6.5 Recommendation `[proposed]`

The oversight chat recommends three steps, in this order. First, fix the estimator. Run 6.4.1 is cheap, and the paper cannot use round 5's form once Williams is known, whatever else it claims. Second, before any new theory, the oversight chat runs a focused literature check of the three directions of section 6.2 under the same protocol as this track, starting with randomization inference after constrained randomization of few clusters. Third, Nicolas chooses the lead (Q3) from what that check leaves, with R8-1 decided at the same time, since the prediction-set half is one of the candidates. The textbook chapters of section 7 should be read before the regime comparison is described anywhere as classical in a paper draft.

## 7. For Nicolas, sources to obtain

The verdicts on C2, C3 and C12 rest on textbook sections that could not be read from here, and a few papers bear on C1, C4 and C6 and have no legitimate free copy. Each can be obtained through UNC Chapel Hill's library. The links were found by a subagent and checked where it could open the page, and the proxy links follow the library's pattern without having been tried. Williams (1961) and Yang, Qu and Li's arXiv version have already been read, and Deville and Tillé (2005) has an open copy in the Neuchâtel repository that the oversight chat can read itself.

1. Cochran, *Sampling Techniques*, 3rd ed., Wiley 1977, no DOI. Chapter 5 (stratified sampling, optimum allocation), chapter 7 (ratio and regression estimators, sections 7.9 and 7.10 on separate and combined estimators), chapters 9 to 11 (cluster and subsampling, section 10.6 on the optimum subsample size). Wiley page https://www.wiley.com/en-us/Sampling+Techniques,+3rd+Edition-p-9780471162407, and the UNC catalogue https://catalog.lib.unc.edu/?q=cochran+sampling+techniques. No free copy.
2. Särndal, Swensson and Wretman, *Model Assisted Survey Sampling*, Springer 1992. Chapter 2 on measurable designs, chapter 8 (two-stage and cluster sampling with the regression estimator), chapter 12 (optimal design). SpringerLink https://link.springer.com/book/9780387406206, through the proxy https://login.libproxy.lib.unc.edu/login?url=https://link.springer.com/book/9780387406206. No free copy.
3. Valliant, Dever and Kreuter, *Practical Tools for Designing and Weighting Survey Samples*, 2nd ed., Springer 2018, chapter 9 (sections 9.2 and 9.4, two-stage allocation with a fixed set of primary units), for C2. DOI 10.1007/978-3-319-93632-1 `[verify]`, through the proxy https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1007/978-3-319-93632-1. No free copy.
4. Mickey, "Some finite population unbiased ratio and regression estimators", JASA 54(287), 594 to 612, 1959, with a corrigendum in 1960. The companion of Williams (1961) for C1, which may give an exact variance for the split-sample regression estimator. JSTOR https://www.jstor.org/stable/2282540, through the proxy https://login.libproxy.lib.unc.edu/login?url=https://www.jstor.org/stable/2282540. The 1958 RAND paper P-1348 of the same title (https://www.rand.org/pubs/papers/P1348.html) may be a free earlier version, but no PDF link was visible.
5. Breidt and Chauvet, "Improved variance estimation for balanced samples drawn via the cube method", Journal of Statistical Planning and Inference 141, 479 to 487, 2011, for C6. ScienceDirect https://www.sciencedirect.com/science/article/abs/pii/S0378375810003150, through the proxy https://login.libproxy.lib.unc.edu/login?url=https://www.sciencedirect.com/science/article/abs/pii/S0378375810003150. No free copy found.
6. Fattorini, "Applying the Horvitz-Thompson criterion in complex designs", Biometrika 93(2), 269 to 278, 2006, for C6 and C7. DOI 10.1093/biomet/93.2.269, proxy https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1093/biomet/93.2.269. Two Siena repository records may hold it (https://usiena-air.unisi.it/handle/11365/8538, https://usiena-air.unisi.it/handle/11365/27124), unconfirmed.
7. Fuller, "Some design properties of a rejective sampling procedure", Biometrika 96(4), 933 to 944, 2009. DOI 10.1093/biomet/asp042, proxy https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1093/biomet/asp042. No free copy.
8. Yang, Qu and Li, "Rejective sampling, rerandomization, and regression adjustment in survey experiments", JASA 118(542), 1207 to 1221, 2023, to confirm the published statement of Corollary A5 and appendix A5. DOI 10.1080/01621459.2021.1984926, proxy https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1080/01621459.2021.1984926. Free version arXiv:2109.09930 (already read).
9. Broska, Howes and van Loon, "The mixed subjects design: treating large language models as potentially informative observations", Sociological Methods & Research 54(3), 1074 to 1109, 2025, to see whether the paper itself derives the cost-constrained design that its R package offers (C2). DOI 10.1177/00491241251326865, proxy https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1177/00491241251326865. No preprint found.
10. Moerbeek, "Power and money in cluster randomized trials: when is it worth measuring a covariate?", Statistics in Medicine 25(15), 2607 to 2617, 2006, for C4 and the cost side of C2. DOI 10.1002/sim.2297 (from the Wiley page's address in a search result), proxy https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1002/sim.2297. The Utrecht repository copy is embargoed.
