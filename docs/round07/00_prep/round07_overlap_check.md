# Overlap check before round 7, a lab manuscript on slide selection and three newer PPI papers

13 October 2026. Written by the oversight chat for Nicolas, before round 7's PPI and conformal work builds on round 5. Nicolas asked whether a group member's manuscript overlaps the paper "Labelling budgets for prediction-powered inference with clustered data" closely enough to change its direction.

**What this public version leaves out.** The manuscript is unpublished. By Nicolas's decision of 13 October, this repository records only that it was checked, that it is about choosing which slides of a cohort receive a spatial transcriptomics assay under a budget, and the verdict. Its title, authors, methods, data and results, and a part-by-part comparison with the paper, are in the full check, which is kept in the private claude.ai project docs at `claude/round07_overlap_check_full.md`. The manuscript's PDF is in neither place. The literature in section 3 is public and is given in full here.

The recommendations in sections 2, 4 and 5 are `[proposed]` until Nicolas decides. On 13 October he decided that the PPI work of round 7 starts with a positioning note (section 4) before any execution track is opened.

## 1. What was read

- **The manuscript,** shared by Nicolas on 13 October and read in full, appendix included. Two searches on 13 October found no public version.
- **Our side.** The paper's estimator (`docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`), the readings for the paper and the open question in the two round-5 closing memos (`docs/round05/i04/ppi/round5_ppi_E5_decisions.md` sections 3 and 5, `docs/round05/i03/conformal/round5_conformal_W5_decisions.md` section 3), the originality check of 28 September (`docs/round04/00_prep/round4_originality_check.md`) and the deck-2 literature check of 4 October (`docs/round05/00_prep/deck2/deck2_literature_check.md`).
- **The literature since those checks.** Two search agents looked for papers on active or adaptive label selection with valid inference, PPI with clustered data, slide selection for spatial omics, and budget design for PPI. The oversight chat opened the abstract pages of the four closest papers itself. For the closest one, Broska and Howes, it put a list of questions to the full PDF through a question-answering pass. That is not a line-by-line reading, and section 4 says what still needs one.

## 2. Verdict on the manuscript

The direction does not need to change because of the manuscript. It chooses slides to profile for purposes other than inference, and it reports no estimand for a population quantity, no confidence interval and no prediction set. Nothing in it makes a claim our paper makes. Its question and ours meet at one decision, which clusters to label, and the two papers make that decision for different ends. Our paper chooses clusters so that an interval for a population quantity is valid and narrow.

The check did show a gap that round 7's planned question already addresses, and it applies to any selection rule chosen for training or coverage rather than for inference. Such rules are often deterministic given the slides already profiled, or depend on expression already measured. Under a deterministic rule every slide's inclusion probability is 0 or 1, and under an outcome-dependent rule the profiled set is selected on the outcome. In either case the labelled clusters are not a probability sample, and the interval `textbook_t|fpc|lin|xf` has no design to rest on. Round 5 closed with the question of weighting the labelled clusters by their inclusion probabilities under rejective selection (E5 memo, section 5). With $\pi_g$ the probability that cluster $g$ is labelled, computable by simulating the design before any label is bought, the Horvitz-Thompson form in the estimator definition's notation is

$$
\hat\theta_{\mathrm{HT}} = \frac{1}{G}\sum_{g \in L} \frac{\hat z_g}{\pi_g},
$$

which reduces to the classical mean of the labelled clusters under simple random selection, where $\pi_g = n_L/G$. That is the tool that lets a histology-guided selection policy coexist with valid inference, provided the policy is randomised and its $\pi_g$ are known.

Three adjustments are proposed, and none changes the paper's core.

1. **Reframe round 7's first methods question** as valid inference after histology-guided assay allocation. Keep the Horvitz-Thompson and Hájek weighting under rejective selection as the core, and widen the balance variables from the estimand's own $\bar f_g$ to the leading principal components of the slide-mean embeddings, the label-free information a histology-guided rule can use. Round 5 found that balance on two variables failed at few residual degrees of freedom (estimator definition, section on rejective selection), and whether the weighting repairs that is the open question either way.
2. **Add a randomised counterpart of an adaptive policy** as a second design. Clusters are labelled in batches with probabilities that rise with a label-free diversity score, so that each batch's probabilities are known when it is drawn. Section 3 shows that unit-level versions of this exist, so the cluster-level, few-cluster version is what would be the paper's own.
3. **Show what a deterministic rule does to coverage,** as a short cautionary result. Run the greedy k-center rule, which is standard in active learning (Sener and Savarese, ICLR 2018), on the paper's tasks, apply the paper's interval to the slides it picks, and report coverage against simple random and rejective selection. This needs nothing unpublished.

How the two papers refer to each other is for Nicolas to settle with David and Dr. Zhu. Contact with the manuscript's authors about code, data or citation is Nicolas's decision, never a session's.

## 3. The newer PPI papers, which matter more for the paper's originality

The search found one paper posted since the deck-2 literature check of 4 October, Broska and Howes, and two earlier papers that neither check recorded, Chen et al. (NeurIPS 2025) and Kluger and Bates (February 2026). With Kluger et al., which the deck-2 check did record, they change what the paper can claim as new more than the manuscript does.

**Broska and Howes, "Cluster-Robust Prediction-Powered Inference", arXiv:2610.09601, 7 October 2026.** They give closed-form cluster-robust standard errors for PPI++ under arbitrary within-cluster dependence, with clusters drawn independently and units labelled by a Bernoulli draw with a cluster-specific probability, so a cluster may be fully labelled, partly labelled or unlabelled. They derive a cluster-aware power-tuning rule, extend it to M-estimation, and analyse how precision depends on the labelling design. They conclude that when labels are scarce, spreading them over many clusters can be much more precise than labelling whole clusters. In their television-news application, ordinary PPI++ covers below 60% and theirs reaches 95%. This covers ground that the paper's section 3 and its regime comparison would have claimed. The question-answering pass found six things they do not do, and a line-by-line reading must confirm each before the paper relies on it.
- Few clusters. They use normal quantiles, state that the variance estimator has no small-sample correction, and run every simulation with 2,266 broadcasts as clusters.
- A design-based target. Clusters are draws from a superpopulation, with no finite-population factor and no cross-fitting term.
- A budget split with costs, which they name as future work.
- The predictor's cluster-level accuracy as the driver of the gain. They report the intraclass correlation of the prediction error but state no theorem in terms of it.
- Choosing which clusters to label. Their labelling probabilities may not depend on the data, and active labelling is future work.
- Prediction sets.

**Kluger, Lu, Zrnic, Wang and Bates, "Prediction-Powered Inference with Imputed Covariates and Nonuniform Sampling", arXiv:2501.18577, January 2025.** Bootstrap intervals for PPI when the labelled sample comes from a weighted, stratified or clustered design. The originality check of 28 September said that nobody had treated PPI under cluster sampling, and this paper had already done so. The deck-2 literature check of 4 October recorded it (`docs/round05/00_prep/deck2/deck2_literature_check.md`, section "Valid intervals with 4 to 16 labelled clusters"), and round 5's inference instruction cites it. With Broska and Howes the originality check's statement is now plainly out of date. The check is frozen, so this is recorded here and in round 7's reading guide.

**Chen, Zhou, Peng and Wang, "Balanced Active Inference", NeurIPS 2025.** Active statistical inference with balancing constraints built from model uncertainty, selecting labels with the cube method, with asymptotic theory and nominal coverage in experiments. The abstract speaks of individual examples, not clusters. It is the closest published relative of the paper's rejective-selection result and of adjustment 2 in section 2, and the paper has to position against it.

**Kluger and Bates, "M-estimation under Two-Phase Multiwave Sampling with Applications to Prediction-Powered Inference", arXiv:2602.16933, February 2026.** Valid inference when expensive labels are collected in waves chosen adaptively, with a near-greedy sampling rule. It is the closest relative of batchwise, adaptive selection, at the unit level.

Also relevant are Zrnic and Candès, "Active Statistical Inference" (ICML 2024), already cited in round 4's check, and a robust-sampling follow-up by Li, Zrnic and Candès (arXiv:2511.08991, November 2025).

**What remains the paper's own,** subject to the full reading of Broska and Howes. Inference with few labelled clusters for the design target, with the finite-population factor, the cross-fitting term and the $t$ reference. The gain theorem in terms of the predictor's cluster-level $R^2$, and the level term of regime B. The budget split between clusters and units with costs, using the measured between ratio. The selection of labelled clusters by a label-free design, with its conditions and failures, and the inclusion-probability weighting. The prediction-set map over calibration donors and labelled spots. And the joint design, where the same labelled spots serve the rectifier and GHCP. The paper's first page can no longer say that PPI under cluster sampling is untreated. It has to cite Broska and Howes and Kluger et al., say that they give the large-sample cluster-robust interval, and present the paper as the design and few-cluster counterpart.

## 4. What this means for round 7

- The conformal part is untouched by the manuscript and by the new papers. The nearest work remains GHCP (Mallick, Tchetgen Tchetgen, Dobriban and Lee, arXiv:2608.15500), which the paper already uses.
- Before an instruction for a PPI execution track is written, the oversight chat reads Broska and Howes and Chen et al. in full and writes a positioning note in `docs/round07/oversight/`. If either full text cannot be fetched from a cloud session, Nicolas uploads it. Nicolas chose this order on 13 October.
- The PPI track's first question then becomes adjustment 1 of section 2, with adjustments 2 and 3 as its later stages, if Nicolas accepts them.

## 5. Decisions, and who makes them

| # | Decision | Who decides | Default until decided |
|---|---|---|---|
| O1 | The paper's direction stands after the manuscript | Nicolas | stands |
| O2 | Round 7's PPI question is reframed as inference after histology-guided allocation, with the adjustments of section 2 | Nicolas, after the positioning note | the E5 memo's question as written, balance on $\bar f_g$ only |
| O3 | How our paper and the manuscript refer to each other | Nicolas, with David and Dr. Zhu | neither refers to the other |
| O4 | Any contact with the manuscript's authors about code, data or citation | Nicolas, never a session | no contact |
| O5 | The positioning against Broska and Howes, Kluger et al. and Chen et al. | Nicolas, with David | the paper claims nothing about large-sample cluster-robust PPI as new |

## 6. Sources

- Broska and Howes, "Cluster-Robust Prediction-Powered Inference", https://arxiv.org/abs/2610.09601
- Kluger, Lu, Zrnic, Wang and Bates, "Prediction-Powered Inference with Imputed Covariates and Nonuniform Sampling", https://arxiv.org/abs/2501.18577
- Chen, Zhou, Peng and Wang, "Balanced Active Inference", NeurIPS 2025, https://proceedings.neurips.cc/paper_files/paper/2025/hash/4a3dadd6fd404a113e190e07380f0761-Abstract-Conference.html
- Kluger and Bates, "M-estimation under Two-Phase Multiwave Sampling with Applications to Prediction-Powered Inference", https://arxiv.org/abs/2602.16933
- Zrnic and Candès, "Active Statistical Inference", ICML 2024, https://arxiv.org/abs/2403.03208
- Li, Zrnic and Candès, "Robust Sampling for Active Statistical Inference", https://arxiv.org/abs/2511.08991
- Mallick, Tchetgen Tchetgen, Dobriban and Lee, "Generalized Hierarchical Conformal Prediction", https://arxiv.org/abs/2608.15500
- Sener and Savarese, "Active Learning for Convolutional Neural Networks: A Core-Set Approach", ICLR 2018
- The deck-2 literature check, `docs/round05/00_prep/deck2/deck2_literature_check.md`
