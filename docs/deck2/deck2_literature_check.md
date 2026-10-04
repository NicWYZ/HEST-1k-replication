# Literature check before the second presentation

4 October 2026. Written by the oversight chat for Nicolas. It answers three questions about the work. Is it original, is it relevant, and is it important. Three searches ran in parallel, about 280 web queries and page reads in total, covering 2023 to October 2026. I then opened the four papers that matter most myself.

**How far to trust this.** Every page was read through a fetch tool that returns a summary of the page, not the page. Titles, authors and dates below are confirmed. Theorem numbers and quoted formulas are as the tool reported them and need checking against the PDFs before they go into a paper. Section 6 lists what I confirmed myself and what I did not.

---

## 1. The short version

- **Nobody has done PPI with clustered data the way we do.** No paper found combines few labelled clusters, cluster-level accuracy, and a comparison of labelling whole clusters against a few units in every cluster.
- **Two of our headline statements are translations of known results, and we did not know that.** The break-even rule is published for independent data. The gain theorem's limit is a standard formula in the design of cluster-randomised trials.
- **The design comparison is our most defensible contribution.** It was not found anywhere.
- **The need is easy to document.** Predicted expression is used as data at scale, accuracy has stopped improving, and the PPI literature assumes independent units.
- **The conformal side is narrower than the PPI side,** and one paper from five weeks ago changes how our open question must be worded.

---

## 2. Originality, claim by claim

### The break-even rule, $n_L > 4 + 2/R^2_{\text{cluster}}$

**Already published for independent data.** Mani, Xu, Lipton and Oberst, "No Free Lunch: Non-Asymptotic Analysis of Prediction-Powered Inference" (arXiv:2505.20178, May 2025, revised June 2026). Their abstract states that for Gaussian data the correlation must be at least $1/\sqrt{n - 2}$ for PPI++ to improve on the classical estimator. The search reports that their Corollary 4.1 gives $\rho^2 > 1/(n/2 - 2)$ for two-fold cross-fitting. Rearranged, that is

$$
n > 4 + \frac{2}{\rho^2},
$$

which is our rule with units in place of clusters. Their Theorem 4.1 also has the same structure as our tuning-cost formula, a floor plus a term in the error of the estimated coefficient. They trace it to Lavenberg and Welch (1981) on control variates with estimated coefficients. A second paper, Eyre and Madras (arXiv:2411.12665), makes the qualitative point that PPI++ can lose with few labels because of the variance of $\hat\lambda$.

**What is left for us.** The count that matters is labelled clusters and the $R^2$ that matters is the cluster-level one. That is a real difference in practice, since a study can have tens of thousands of labelled units and eight labelled clusters. But the formula is theirs and they must be cited beside it.

### The gain theorem, ratio tends to $1 - R^2_{\text{cluster}}$

**Not found for PPI. Standard for covariates in cluster-randomised trials.** The design literature in education has had this since Raudenbush (1997) and Bloom, Richburg-Hayes and Black (2007). Their precision formula has a between-cluster term multiplied by $1 - R^2$ at the cluster level and a within-cluster term multiplied by $1 - R^2$ at the individual level. As units per cluster grow, only the cluster-level term is left. On the survey side, Hagesæther and Zhang (2009) give the corresponding result for the regression estimator under cluster sampling in terms of the intraclass correlation of residuals.

**What is left for us.** The statement for a black-box predictor used through PPI, the measurement of both $R^2$ values for real foundation models, and the fact that they differ a great deal in practice. It should be presented as a known result carried over to PPI, not as a new phenomenon.

### Labelling a few clusters fully against a few units in every cluster

**Not found.** The ingredients exist separately. Optimal two-level designs with a covariate are in Raudenbush and in Moerbeek (2006), which I could not open. Label allocation for PPI without clusters is active, with at least six papers in 2025 and 2026. Shirota (arXiv:2608.10356, August 2026) gives an optimal spatial allocation of labels for design-based PPI on maps. None compares the two regimes with a predictor and a cost per cluster and per unit. This is the contribution to lead with.

### Valid intervals with 4 to 16 labelled clusters

**The combination was not found. Each ingredient is known.** Kluger, Lu, Zrnic, Wang and Bates (arXiv:2501.18577) give a cluster bootstrap for PPI and state that its theory is out of scope. Kennel and Valliant (2019) give leverage-adjusted cluster variance estimators for the regression estimator in surveys. Few-cluster inference is a mature topic in econometrics (Cameron and Miller 2015; MacKinnon, Nielsen and Webb 2023). No one found connects it to PPI. Our contribution is the assembled recipe and its validation. Our own experiments show the donor bootstrap covering 0.71 to 0.84 with few clusters, which is worth saying next to the Kluger citation.

### The uninformative predictor that appears to help

**Not found in any PPI paper.** The classical mechanism is known in survey sampling, where auxiliary information absorbs variation in cluster sizes or weights. It is new as a warning for PPI users and as a diagnostic.

### The map of prediction-set width over calibration clusters and labelled test units

**Not pre-empted, and the margin over GHCP is narrow.** The GHCP paper fixes 20 reference groups, never varies that number, and reports that its method improves steadily with more test-group observations. Its within-group baseline spends half the test-group observations on training, so that baseline is infinite until 20 observations. Our two findings sit exactly in what they did not vary. With 10 groups a few labelled units make GHCP wider than the hierarchical method with none, and a plain split that calibrates on all the labelled units is valid from about 10. The paper has to state both differences, and show that at 20 groups our numbers agree with theirs.

### The lower bound when $K + 1 < 1/\alpha$

**The first half is close to a known fact. The second half looks new.** Tibshirani, Barber and Ramdas, "Conformal Prediction Through the Lens of Hypothesis Testing: Universality, Impossibility, and Optimality" (arXiv:2608.27310, 27 August 2026) show that any distribution-free valid prediction set is of conformal type, building on earlier results of Vovk and of Angelopoulos, Barber and Bates. From that, the statement that an infinite set is forced with probability at least $1 - \alpha(K+1)$ follows in a few lines, and a referee who knows the paper will call it a corollary. It was not found written down anywhere, for groups or for ordinary data. The coverage floor for finite methods was not found in any form.

### The open question at $K + 1 \ge 1/\alpha$

**Must be reworded.** The same paper proves that for ordinary exchangeable data the best valid method is a randomised conformal predictor with an oracle score. So "can anything beat the hierarchical method" is settled in the ordinary case. For grouped data the invariance is larger and the within-group data carry extra information, and no paper addresses that. The question stands only if it is posed for the hierarchical class and cites this paper.

---

## 3. Relevance and importance

**Predicted expression is used as data, at scale, from few patients.** One model was trained on 14 breast cancer patients and then applied to 1,096 TCGA samples to derive prognostic and treatment-response signatures (Path2Space, bioRxiv 2024, reported as published in Cell in 2026). A 2026 preprint from Roeder's group (Testa, Lei and Roeder) says in its abstract that downstream analyses "typically treat reconstructed expression as experimentally observed, overlooking prediction error".

**Accuracy is not improving.** The best average correlation on the HEST benchmark was 0.41 in the 2024 paper and is 0.42 on the April 2026 leaderboard, after 25 models. An independent benchmark of eleven methods (Wang and colleagues, Nature Communications 2025) reports a best overall correlation of 0.28.

**Embeddings carry the site.** Kömen and colleagues (Nature Communications, June 2026) recover the medical centre of a patch with 88 to 98% accuracy from 20 pathology foundation models. That is cluster-level error, the kind our results say limits the gain.

**The PPI literature assumes independent units, and applied authors say so.** The main paper on LLM annotations states the assumption directly. Kluger and colleagues, applying PPI to remote-sensing maps, write that their work "does not explore these common settings" of clustered sampling. The genomics application avoids dependence by restricting to unrelated subjects.

**Label budgeting is named as open.** A December 2025 overview lists power and sample-size planning with predicted quantities as an open direction. The March 2026 power-analysis paper solves it for independent data only.

**Clustering matters in neighbouring fields.** For language-model evaluations, clustered standard errors were up to three times the naive ones (Miller, arXiv:2411.00640). In single-cell biology, treating cells as replicates is the standard example of false discoveries (Squair and colleagues 2021).

**What weakens the case.**

- Strong groups are bringing PPI into spatial transcriptomics now (Roeder; Jordan, Bates and Yosef). Neither preprint is about histology-predicted expression or about donors as the unit, but the area will not stay empty.
- A reviewer can say that clustered PPI is two-stage survey sampling under a new name. Mozer's paper makes that argument easy. Our answer is the design comparison, the few-cluster behaviour and the measurement on real predictors.
- The claim that applied users ignore clustering rests on stated assumptions in methods papers, not on an audit of applied papers.
- Shirota's paper is the nearest neighbour in spirit, PPI under dependence with a design answer. It uses spatial balance and has no clusters, no few-cluster correction and no within-against-between comparison. It needs a full read.

---

## 4. What changes in the presentation

1. The originality slide gains two lines. The break-even rule is known for independent data (Mani and colleagues). The gain formula is the cluster-randomised-trial formula (Raudenbush; Bloom and colleagues).
2. The slides for the gain theorem and the tuning cost say "carried over to clusters" and carry the citations.
3. The design comparison is presented as the main new result.
4. The lower-bound remark is described as a short proposition that follows from recent universality results, with the coverage floor as the part we have not found elsewhere.
5. The motivation slide can use three facts. The 14 patients and 1,096 samples, the benchmark's 0.41 to 0.42 over two years, and the 88 to 98% site recovery.

## 5. What changes in the paper plan

- Lead with design. Position the gain and tuning results as the two facts the design result rests on, each with its source.
- Cite Mani and colleagues, Lavenberg and Welch, Raudenbush, Bloom and colleagues, Hagesæther and Zhang, Kennel and Valliant, Kluger and colleagues, and Shirota in the first two pages.
- Add a comparison at 20 groups with the GHCP paper's own setting.
- Reword the open conformal question against Tibshirani, Barber and Ramdas.

## 6. What I confirmed myself, and what I did not

**Confirmed by opening the page.**

- Mani and colleagues exists with the title, authors and dates above, and its abstract gives the $1/\sqrt{n-2}$ threshold. I did not see the cross-fit corollary text. Our rule is its direct analogue with $n/2$ in place of $n$, which is what the search reported.
- Shirota exists, is dated 11 August 2026, analyses simple random, stratified and spatially balanced designs, and has no cluster or two-stage design and no small-sample correction.
- Tibshirani, Barber and Ramdas exists, dated 27 August 2026. The abstract states the optimality result. It does not treat grouped data or the case $n + 1 < 1/\alpha$.
- The GHCP paper exists with the authors and date we have used.

**Known to me independently.** The cluster-randomised-trial formula with separate cluster-level and individual-level $R^2$ is standard in that literature.

**Reported by the searches and not confirmed by me.**

- The exact statement and numbering of the theorems in Mani and colleagues and in Tibshirani, Barber and Ramdas.
- The content of Hagesæther and Zhang, Kennel and Valliant, Eyre and Madras, and the applied papers in section 3, including every quoted sentence.
- That the GHCP paper never varies the number of groups. Our own reproduction of its tables is consistent with that.

**Not read by anyone.** Moerbeek (2006), Raudenbush (1997) itself, Rivera-Rodriguez and colleagues on two-phase designs for cluster-correlated data, and the discussion sections of two PPI surveys. These are the reading list.

**Could not be found.** The GLMP paper. Ask David for the reference.

---

## Sources

- Mani, Xu, Lipton, Oberst. No Free Lunch: Non-Asymptotic Analysis of Prediction-Powered Inference. [arXiv:2505.20178](https://arxiv.org/abs/2505.20178)
- Eyre, Madras. Regression for the Mean. [arXiv:2411.12665](https://arxiv.org/abs/2411.12665)
- Shirota. Design-Based Prediction-Powered Inference for Spatial Data. [arXiv:2608.10356](https://arxiv.org/html/2608.10356)
- Kluger, Lu, Zrnic, Wang, Bates. Prediction-Powered Inference with Imputed Covariates and Nonuniform Sampling. [arXiv:2501.18577](https://arxiv.org/abs/2501.18577)
- Mozer. PPI is the Difference Estimator. [arXiv:2603.19160](https://arxiv.org/abs/2603.19160)
- Chen, Guo, Li. Power Analysis for Prediction-Powered Inference. [arXiv:2603.16041](https://arxiv.org/abs/2603.16041)
- Bloom, Richburg-Hayes, Black. Using Covariates to Improve Precision. [MDRC](https://www.mdrc.org/work/publications/using-covariates-improve-precision/file-full)
- Hagesæther, Zhang. A Note on the Effect of Auxiliary Information on the Variance of Cluster Sampling. [Journal of Official Statistics 2009](https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/a-note-on-the-effect-of-auxiliary-information-on-the-variance-of-cluster-sampling.pdf)
- Kennel, Valliant. Robust variance estimators for generalized regression estimators in cluster samples. [Survey Methodology 2019](https://www150.statcan.gc.ca/n1/pub/12-001-x/2019003/article/00001/01-eng.htm)
- Mallick, Tchetgen Tchetgen, Dobriban, Lee. Generalized Hierarchical Conformal Prediction. [arXiv:2608.15500](https://arxiv.org/html/2608.15500)
- Tibshirani, Barber, Ramdas. Conformal Prediction Through the Lens of Hypothesis Testing. [arXiv:2608.27310](https://arxiv.org/html/2608.27310)
- Lee, Barber, Willett. Distribution-free inference with hierarchical data. [arXiv:2306.06342](https://arxiv.org/abs/2306.06342)
- Wang, Li, Yu. Conformal causal inference for cluster randomized trials. [arXiv:2401.01977](https://arxiv.org/abs/2401.01977)
- Testa, Lei, Roeder. Accurate prediction in reconstructed spatial transcriptomes does not ensure valid biological discovery. [bioRxiv 2026](https://www.biorxiv.org/content/10.64898/2026.06.19.733432v2)
- Boyeau, Bates, Ergen, Jordan, Yosef. Mitigating Bias in Spatial Transcriptomic Pipelines via Human Feedback. [bioRxiv 2026](https://www.biorxiv.org/content/10.64898/2026.01.15.699786v1)
- Path2Space. [bioRxiv 2024.10.16.618609](https://www.biorxiv.org/content/10.1101/2024.10.16.618609v2)
- HEST leaderboard. [GitHub](https://github.com/mahmoodlab/hest)
- Wang and colleagues. Benchmarking the translational potential of spatial gene expression prediction from histology. [Nature Communications 2025](https://www.nature.com/articles/s41467-025-56618-y)
- Kömen and colleagues. Towards robust foundation models for digital pathology. [Nature Communications 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13260997/)
- Gligorić, Zrnic, Lee, Candès, Jurafsky. Can Unconfident LLM Annotations Be Used for Confident Conclusions? [arXiv:2408.15204](https://arxiv.org/html/2408.15204v2)
- Kluger, Lobell and coauthors. Regression coefficient estimation from remote sensing maps. [arXiv:2407.13659](https://arxiv.org/html/2407.13659v5)
- Do We Really Even Need Data? A Modern Look at Drawing Inference with Predicted Data. [arXiv:2512.05456](https://arxiv.org/html/2512.05456)
- Miller. Adding Error Bars to Evals. [arXiv:2411.00640](https://arxiv.org/abs/2411.00640)
- Cameron, Miller. A Practitioner's Guide to Cluster-Robust Inference. [Journal of Human Resources 2015](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
- MacKinnon, Nielsen, Webb. Cluster-robust inference: A guide to empirical practice. [arXiv:2205.03285](https://arxiv.org/abs/2205.03285)
