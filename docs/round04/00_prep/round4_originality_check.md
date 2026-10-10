> **Closed record, dated 28 September 2026.** The oversight chat's literature check before the round-4 tracks started, committed here on 30 September. It reframed the paper and led to the revision of both track documents.

# Originality check, and the revised paper plan

28 September 2026. Written by the oversight chat for Nicolas and David, before the round-4 tracks start. The question was whether the two tracks propose original methods or apply existing ones to spatial transcriptomics. The answer is different for the two tracks, and both instruction documents are revised as a result.

## 1. What the literature holds, as of this week

**Prediction-powered inference is the survey-sampling difference estimator.** Mozer (arXiv:2603.19160, March 2026) shows that PPI's mean estimator is the difference estimator of Cassel, Särndal and Wretman (1976) and PPI++ is the generalised regression estimator, so the whole PPI construction is model-assisted survey estimation with a machine-learned auxiliary variable. Model-assisted estimation under two-stage and cluster sampling, with cluster-level variance, is textbook (Särndal, Swensson and Wretman 1992, chapter 8; Breidt and Opsomer, Statistical Science 2017, for modern predictors). So "cluster-robust PPI" is not a new estimator. It is the model-assisted estimator under two-stage sampling, and the paper has to say so in its first page.

**PPI design questions are being worked on, without clusters.** Chen, Guo and Li (arXiv:2603.16041, March 2026) give power formulas and required labelled sample sizes for PPI, with the reduction scaling roughly with the predictor's $R^2$. A February 2026 paper (arXiv:2602.12992) derives Neyman-type stratified allocation for model-assisted estimation with LLM surrogate outcomes. Zrnic and Candès (2024) and a May 2026 follow-up treat active, unit-level label selection. Innocenti and colleagues (Statistics in Medicine 2019, 2021) give optimal two-stage allocation without predictions. Nobody I found treats PPI under cluster sampling, the split of a labelling budget between clusters and units per cluster when predictions are available, or the behaviour of the estimator with few labelled clusters.

**The conformal track's problem was taken up six weeks ago.** Mallick, Tchetgen Tchetgen, Dobriban and Lee (arXiv:2608.15500, 15 August 2026), "Generalized Hierarchical Conformal Prediction", start from exactly our observation, that HCP with $K$ calibration groups calibrates at level $(1-\alpha)(K+1)/K$ and is conservative at small $K$. Their method (GHCP) assumes $o$ initial observations from the test group are available, restores hierarchical exchangeability by a random "donation" of a reference group's size, uses part of the $o$ observations to adapt the score to the test group, and is provably valid and empirically narrower than HCP. Their real-data example is ACS PUMS income. Two things follow. Our "small labelled sample on the test slide" idea is their setting, and they got there first with a better construction than within-slide split conformal. And the case with no test-group observations, $o = 0$, is not treated by them beyond HCP, and no lower bound on the price of validity at small $K$ exists in the literature they cite (Dobriban and Yu 2025; Duchi et al. 2025 on multi-environment predictive inference).

**Conformal for grouped data otherwise.** Lee, Barber and Willett's HCP is now published (ACM Journal of Data Science, 2026). Dunn, Wasserman and Ramdas (JASA 2023) remain the predecessor. "Conformal prediction for hierarchical data" (Principato et al., 2024, revised May 2026) is hierarchical forecasting with aggregation constraints, unrelated. Longitudinal conformal (arXiv:2310.02863) is for subjects already in the training data.

## 2. The verdict

The methods in both tracks are existing methods. That was already true of round 3 and is not a problem in itself; the problem is a paper whose only contribution is a new application. Where the project has something of its own is narrower and more general than either track document said.

**On the PPI side**, the original content is a set of results about what predictions can and cannot buy under cluster sampling, and what that implies for design. They are corollaries of survey-sampling theory with a predictor substituted, which is exactly why they are general. Nobody has written them down, and every user of PPI with clustered data (LLM annotations of documents nested in sources, satellite predictions nested in regions, patients nested in hospitals, spots nested in donors) needs them. The central one is that the gain from predictions under cluster sampling is governed by the predictor's cluster-level accuracy, not its unit-level accuracy, because the rectifier's between-cluster variance is what the labelled clusters have to estimate and predictions reduce it only to the extent they get cluster means right. Round 3 measured the symptom (modest gains despite decent unit-level Pearson, and slide offsets of half a standard deviation) without naming the cause.

**On the conformal side**, the honest position is that GHCP is the method for the labelled-test-group regime and we should use it, cite it, and not compete with it. What remains open is the $o = 0$ case, where the question is whether any valid method can be sharper than HCP at small $K$, and that is a lower-bound question. It may have a clean answer, it may not, and it is the one place a theoretical contribution is possible; it gets a bounded scoping study with a stop rule, not a track.

## 3. The revised paper

One paper, methodology first, two application domains, spatial transcriptomics as the main case study and a general public dataset as the second so that the results are read as general.

**Working title.** Labelling budgets for prediction-powered inference with clustered data.

**Section 2, setting.** Units nested in clusters; a black-box predictor whose error has a cluster-level component; a labelling budget spent on clusters and units per cluster; two targets, confidence intervals for population quantities and prediction sets for units in new clusters.

**Section 3, inference.** The model-assisted (PPI++) estimator under two-stage sampling, positioned against Mozer and Särndal et al., with the cluster-robust variance, the small-$G$ reference, and the theorem on the gain, which says that as units per cluster grow, the PPI-to-classical variance ratio tends to the ratio of the rectifier's between-cluster variance to the outcome's, which is one minus the predictor's cluster-level $R^2$. Corollaries on the power-tuning weight $\lambda$ and on when PPI cannot help at all.

**Section 4, prediction sets.** HCP at $o = 0$ and GHCP at $o > 0$, with the price of validity as a function of $K$ and $o$ measured in simulation and on data, and, if the scoping study delivers it, a lower bound at $o = 0$.

**Section 5, design.** Optimal allocation of a budget between clusters and units with a predictor (the classical two-stage formula with residual components, and the result that a better predictor shifts the optimum toward more clusters); the comparison of labelling few clusters fully against labelling a few units in every cluster; and the joint design, since the same $o$ labelled units per cluster serve the rectifier and GHCP at once.

**Section 6, applications.** ACS PUMS income with states or PUMAs as clusters, which is the dataset both the PPI package and the GHCP paper use, so every number is comparable to two literatures. Then HEST-1k, three tasks with audited donors, where the cluster-level error is large and measured, and where the round-3 audit story shows what happens when the cluster labels are wrong.

**Venue.** ICML 2027 (January deadline) if round 4 finishes by mid-November, with Biometrics or JRSS-C as the fallback. The methodological content is moderate in novelty and high in usefulness, which is a better fit for a general venue than the earlier framing was.

## 4. What changes in the two track documents

**PPI track.** Section 2.2 rewritten around the paper above. Q1 unchanged. Q2 gains the gain theorem as its main statement, with the allocation result as its corollary, and its experiment measures the predictor's cluster-level $R^2$ on every task. Q3 loses the within-slide conformal arm, which moves to the conformal track as GHCP, and keeps the regime comparison. Q4 gains the ACS application as a parallel unit, fetched in Q0 from the PPI package's data, with an escalation path if Longleaf cannot reach it. Q5 gains the joint-design table, built from Q3's and the conformal track's C3 outputs once both are committed.

**Conformal track.** Section 2.2 rewritten around GHCP. C1 gains GHCP and an $o$ axis in the testbed. C2 drops double conformal and repeated subsampling, keeps smoothed HCP, the model-based group-level quantile and the adaptive score, adds GHCP as the reference at $o > 0$, and adds a bounded theoretical scoping of the $o = 0$ lower bound, capped at three days with a stop rule. The go or no-go criterion is restated against GHCP. C3 becomes the $(K, o)$ map on real data, including the labelled-spots-per-slide sweep that was in the PPI track, and the ACS application on the same footing.

The data-pull document does not change.

## 5. Sources

Mozer, "PPI is the Difference Estimator", arXiv:2603.19160. Särndal, Swensson and Wretman, *Model Assisted Survey Sampling*, 1992. Breidt and Opsomer, Statistical Science 32(2), 2017. Chen, Guo and Li, "Power Analysis for Prediction-Powered Inference", arXiv:2603.16041. "Stratified Sampling for Model-Assisted Estimation with Surrogate Outcomes", arXiv:2602.12992. Zrnic and Candès, "Active Statistical Inference", arXiv:2403.03208; "Active Multiple-Prediction-Powered Inference", arXiv:2605.08429. Innocenti et al., Statistics in Medicine 2019 and 2021. Mallick, Tchetgen Tchetgen, Dobriban and Lee, "Generalized Hierarchical Conformal Prediction", arXiv:2608.15500. Lee, Barber and Willett, ACM Journal of Data Science 2026, arXiv:2306.06342. Dunn, Wasserman and Ramdas, JASA 2023. Principato et al., arXiv:2411.13479. Song, Kluger, Parikh and Gu, "Demystifying Prediction Powered Inference", arXiv:2601.20819.
