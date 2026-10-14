# Federated learning for expression prediction: where round 7 leaves it, and what to decide

14 October 2026. Written by the oversight chat for Nicolas, to help decide how to proceed with the federated learning topic after the fedlearn track closed. It draws on the track's literature review (`docs/round07/tracks/fedlearn/round07_fedlearn_literature_review.md`), its two gate reports and the two decision memos (`docs/round07/i02/fedlearn/round07_fedlearn_F2_decisions.md`, `docs/round07/i03/fedlearn/round07_fedlearn_final_decisions.md`). Papers are cited by their row in the review's evidence table (P001 and so on). Every number from an experiment is read from the file named beside it, under `results/round7/fedlearn/`.

Section 1 explains the concepts. Section 2 says what the literature search established and what the track set out to do. Section 3 gives the results. Section 4 says what they imply for the approach. Section 5 lists the decisions.

## 1. The concepts, and how they apply here

### 1.1 Federated learning

Federated learning fits one model to data held at several sites without moving the data. Each site computes something from its own data, sends only that to a coordinator, and the coordinator combines what arrives. The standard algorithm, federated averaging, repeats this in rounds. The coordinator sends the current model to the sites, each site takes some gradient steps on its own data, sends back the updated parameters, and the coordinator averages them. A deep network typically needs tens to hundreds of such rounds.

Two settings are usually distinguished. In the cross-device setting there are millions of phones with a few records each. In the cross-silo setting there are a handful to a few hundred institutions, each with a large dataset and reliable compute. Hospitals and laboratories holding H&E slides with spatial transcriptomics are a cross-silo setting.

Three problems recur in the literature.
- **Heterogeneity.** Sites differ in who they sample and how they measure. In pathology that means different scanners, staining, tissue types and diseases, and frozen foundation-model embeddings are known to carry scanner and site signatures (P289, P355). A model averaged over unlike sites can be worse for a given site than its own local model (P235).
- **Communication and compute.** Iterative training needs a GPU at every site and many rounds of messages through hospital firewalls, which is the practical barrier deployments report (P047).
- **Privacy.** Not moving the raw data does not by itself make the messages safe. Gradients can sometimes be inverted into images (P344), and repeated covariance queries can reconstruct individual records exactly (P329).

### 1.2 Why our problem allows a one-round federation

The project's pipeline is HEST-bench's. A frozen pathology foundation model turns each spot's image patch into an embedding $x \in \mathbb{R}^p$. Principal components reduce it to 256 dimensions, and a ridge regression predicts the expression vector $y$ of the target genes. Round 1 replicated this head.

For this head, iterative training is unnecessary. Suppose center $k$ holds $n_k$ spots with embedding matrix $X_k$ and expression matrix $Y_k$. Each center computes and sends once

$$
n_k, \qquad X_k^\top \mathbf{1}, \qquad Y_k^\top \mathbf{1}, \qquad X_k^\top X_k, \qquad X_k^\top Y_k .
$$

With $N = \sum_k n_k$, these give the pooled means $\bar x$ and $\bar y$ and the pooled centred cross-products. The principal-component basis $V$ is the leading eigenvectors of $\sum_k X_k^\top X_k - N\bar x\bar x^\top$, and the ridge coefficients on the scores are

$$
\hat B = \Big(V^\top \big(\textstyle\sum_k X_k^\top X_k - N\bar x \bar x^\top\big) V + \lambda I\Big)^{-1} V^\top \Big(\textstyle\sum_k X_k^\top Y_k - N \bar x \bar y^\top\Big).
$$

Every quantity on the right is a sum over centers, so the fit from the sums equals the fit on the pooled spots, provided the eigendecomposition and the solve are computed exactly. A center needs no GPU, only one pass over its embeddings, and there is a single message. In the literature this algebra is established for linear and mixed models (P186, P188, P200, P205) and has been used for closed-form heads on frozen features in classification (P050, P222, P223).

Two refinements matter for us.
- **Center intercepts.** A center can be given its own intercept, $y = \alpha_k + B^\top V^\top(x - \bar x)$, still from the same sums. It absorbs a constant shift per center and gene.
- **The metric.** The project scores predictions by the within-slide Pearson correlation, computed per gene within each test slide and averaged. A constant shift per slide and gene cannot change a correlation within a slide, so center intercepts are invisible to this metric. A pooled Pearson over the spots of several centers does see them, which is why the experiments report both.

### 1.3 Differential privacy

Differential privacy is a guarantee about a randomised release $M$ of a dataset. Two datasets are neighbours if they differ in one record. $M$ is $(\varepsilon, \delta)$-differentially private if for every pair of neighbours $D$ and $D'$ and every set $S$ of outputs

$$
P\big(M(D) \in S\big) \le e^{\varepsilon}\, P\big(M(D') \in S\big) + \delta .
$$

So whatever an observer sees, it is almost as likely whether or not any one record was in the data. Smaller $\varepsilon$ is stronger protection. $\varepsilon$ of 1 or below is usually called strong, and 10 is weak.

The Gaussian mechanism achieves this for a numerical release $f(D)$. If changing one record moves $f(D)$ by at most $\Delta$ in Euclidean norm, the sensitivity, then releasing $f(D) + Z$ with $Z \sim N(0, \sigma^2 I)$ is private for a $\sigma$ proportional to $\Delta$ and growing as $\varepsilon$ falls. To make $\Delta$ finite, each record is first clipped to a fixed norm.

Here the release is a center's sums of section 1.2. The track took one spot as the record, clipped each spot's embedding and expression to norms chosen in advance, added Gaussian noise to every sum once, and refitted the head from the noisy sums (V3, after AdaSSP, P339). Two points shape how to read that.
- **The unit of protection is one spot, not one patient.** A patient contributes thousands of spots. A guarantee for one record extends to a group of $m$ records only with $\varepsilon$ multiplied by about $m$, so a spot-level guarantee says almost nothing about a patient. Protecting patients would mean clipping each patient's whole contribution, which needs far more noise.
- **Noise is not the only option.** Secure aggregation, a cryptographic protocol, lets the coordinator learn only the total over centers and not any one center's sums, at no cost in accuracy. It protects centers from each other and from the coordinator, but the total itself is released exactly.

### 1.4 How this maps onto the project

A center is a laboratory or hospital with paired H&E and spatial data. HEST-1k is assembled from many studies, so centers can be simulated from it, but it has no laboratory contrast with the disease held fixed (`docs/reference/methods_and_state_of_play.md`, section 23). Any two real sources differ in lab, study, disease and protocol at once. The track therefore used two kinds of federation. Pseudo-centers are random partitions of one cohort's donors, where only the donors differ. Real sources are two different studies of the same organ and technology.

## 2. What the literature search established, and what we set out to do

### 2.1 The search

A Claude Science session with seven theme sub-agents searched PubMed, Europe PMC, arXiv, a general web search and the main machine learning and medical imaging proceedings on 13 October, logged 695 queries, kept 406 papers and cited 91, of which 72 were read at full text. A separate audit checked every cited claim against its source and fixed the mismatches. Each answer carries a grade, from strong to none found, and every absence holds only within the queries in the log.

### 2.2 What it found

1. **Is accuracy limited by data? Not established (grade weak).** No study measures how within-slide accuracy changes with the number of training patients, slides or centers for a head on frozen embeddings. For bulk expression from whole slides there is a data effect (P130). For spatial prediction, Nguyen et al. (P134) find that much of the aggregate score is slide-level gene means and that a closed-form head already does best. That points to the representation and the weak within-slide signal as the limit, rather than the amount of data. Encoder scale matters little (P123, P157), and fine-tuning encoders gains about 0.01 in Pearson (P379, P385).
2. **Prior art. One federated study of this problem.** PPML-Omics (P001) trains ST-Net end to end across simulated hospitals with differential privacy. Without noise its federated model was slightly worse than central training. No paper fits a head on frozen pathology embeddings from per-center summary statistics, and none federates a reference database.
3. **The routes.** The one-round head from summary statistics (route 1) is exact in algebra and has close precedents outside expression. Iterative federation of a nonlinear head (route 2) is well evidenced for pathology classification, typically within a few points of pooled training (P046). Federated fine-tuning of encoders and federated pretraining are not supported for a first paper.
4. **Heterogeneity.** Scanner and site signatures in pathology embeddings are well documented, and generic methods exist (P266, P267, P268). Exact one-round mixed models with site random effects exist (P186, P188).
5. **Three open problems.** None of the following was found.
   - A method for centers that measure different gene panels. The closest is Ayme et al. (P287), for centers that record different input covariates, which is a different problem.
   - An analysis of the privacy cost of releasing high-dimensional embedding statistics.
   - Inference for a prediction head whose error has a center-level component.
6. **Privacy.** H&E slides can be matched to their patient (P063), expression can be linked to genotype (P321), and the number of summary statistics that can be released safely grows only with the number of individuals (P316). A center's release has about 1.26 million sums. By analogy only, that is far outside the safe regime for a single fixed release.
7. **The alternatives.** The textual knowledge base has no direct literature. The project's round 6 found that no cheatsheet beat the `uni_v2` head on held-out kidney cancer patients. Every alternative, federated learning included, has weak evidence for improving within-slide accuracy at scale.

**The novelty statement.** A claim of novelty for the one-round head can rest only on its application to expression from histology and on what is learned there, not on the estimator.

### 2.3 What we set out to do

The F2 memo turned the review into four scoping experiments on Longleaf, all with the exact head (float64 eigendecomposition and a Cholesky solve) on the data the project already held.
- **V1, the learning curve.** How within-slide accuracy grows with the number of training donors, on `CCRCC`, `INDIANA_KIDNEY` and `LUNG_XENIUM` with three encoders. This answers the review's first question with the project's own data.
- **V2, the simulated federation.** A local head against the federated head and the federated head with center intercepts, on pseudo-centers (three random partitions of donors) and on real sources (kidney Visium, Sorbonne ccRCC cohort against Indiana non-tumour atlas, and breast Xenium, 10x Genomics against a second study). Scored on held-out donors within each center and with a whole center left out.
- **V3, the cost of differential privacy.** Spot-level privacy at $\varepsilon$ from 0.5 to 10.
- **V4, partial gene overlap.** Each of three centers measures a random half of 50 genes, and each gene's head is fitted from the centers that measure it.

Before these, two anchors had to pass. The session's copy of the benchmark head had to match round 1, and the head fitted from sums had to match the pooled head.

## 3. The results

**The method is exact.** The head fitted from per-center sums equals the pooled head to a relative difference of $7.6 \times 10^{-15}$, and the benchmark head reproduces round 1's 0.264 for `uni_v2` on `CCRCC` (`F3_anchor_attempt2/f30_summary.json`).

**V1. More donors help, with diminishing returns.** Within-slide Pearson, mean over 20 draws of training donors, with the standard deviation over draws in brackets (`V1/<task>/v1_summary.csv`).

| task | encoder | 1 donor | 4 donors | 8 donors | full pool |
|---|---|---|---|---|---|
| `CCRCC` (pool 17) | `uni_v2` | 0.061 (0.024) | 0.119 (0.020) | 0.137 (0.010) | 0.147 |
| `INDIANA_KIDNEY` (pool 19) | `uni_v2` | 0.064 (0.028) | 0.114 (0.018) | 0.132 (0.009) | 0.139 |
| `LUNG_XENIUM` (pool 11) | `uni_v2` | 0.351 (0.064) | 0.482 (0.009) | 0.501 (0.004) | 0.505 |

In every task and encoder the rise from 1 to 4 donors (0.041 to 0.131) is larger than the rise from 4 donors to the full pool (0.021 to 0.029). Accuracy is still rising at the largest pools the project holds, but slowly. On `CCRCC` the step from 8 to 17 donors is 0.010. The curves cannot be extrapolated to hundreds of donors from these pools.

**V2. Federation helps when centers differ only in donors, and not clearly across real sources.** On pseudo-centers the federated head beats the local head on held-out donors within centers in all 9 task and encoder cells, by 0.026 to 0.038 on `CCRCC`, 0.016 to 0.020 on `INDIANA_KIDNEY` and 0.025 to 0.032 on `LUNG_XENIUM` (`V2_run2/<task>/v2_paired.csv`). That is the V1 effect, a third of the donors against all of them.

On real sources, with `uni_v2` (`V2_run2/<task>/v2_rows.csv`, held-out donors within each source, mean over 10 draws):

| task | source | local | federated minus local |
|---|---|---|---|
| breast Xenium | 10x Genomics | 0.669 | +0.018 |
| breast Xenium | second study | 0.684 | −0.001 |
| kidney Visium | Sorbonne ccRCC cohort | 0.191 | +0.003 |
| kidney Visium | Indiana non-tumour atlas | 0.112 | −0.021 |

Adding tumour data to the non-tumour atlas lowered its accuracy in every draw and every encoder, by 0.021 to 0.035. The breast gain rests on one held-out slide per draw from 7. A head trained on one source and applied to the other lost 0.05 to 0.17 against the within-source figure.

Center intercepts changed the within-slide metric by at most 0.0022, as section 1.2 predicts. Over the pooled spots of several centers they helped slightly across real kidney sources (0.0018 to 0.0026) and hurt on pseudo-centers (0.008 to 0.033), where there is no center effect for them to capture.

**V3. Spot-level privacy is costly** (`V3/v3_summary.csv`, `V3/v3_paired.csv`, `CCRCC` with `uni_v2`, pseudo-centers).

| release | within-slide | change against non-private |
|---|---|---|
| non-private | 0.219 | |
| clipped, no noise | 0.219 | −0.0004 |
| $\varepsilon = 10$ | 0.196 | −0.023 |
| $\varepsilon = 2$ | 0.152 | −0.067 |
| $\varepsilon = 1$ | 0.112 | −0.107 |
| $\varepsilon = 0.5$ | 0.079 | −0.140 |

Clipping costs nothing, so the loss comes from the noise and the larger ridge penalty that guards against it. Even the weak budget $\varepsilon = 10$ loses a tenth of the accuracy, and $\varepsilon = 1$ loses half. All of this is for spot-level protection, which section 1.3 explains is much weaker than protecting patients.

**V4. Partial gene overlap has a real cost** (`V4/<task>/v4_paired.csv`). When each center measures half of the genes, fitting each gene from the centers that measure it lowers within-slide accuracy by 0.018 to 0.023 on `CCRCC`, 0.010 to 0.013 on `INDIANA_KIDNEY` and 0.015 to 0.019 on `LUNG_XENIUM`, on held-out donors within centers, and is below full overlap in 97 to 100 of 100 partition and mask pairs. A gene measured by one center is fitted from one center's donors, which by V1 costs accuracy.

**Not tested.** Iterative federation, more than three centers, data outside HEST-1k, patient-level privacy, and any inference. The oversight chat's predictions that adding another lab changes accuracy by less than 0.02 (F.9), that $\varepsilon = 10$ costs less than 0.01 (F.11) and that partial overlap costs less than 0.01 (F.12) were all refuted or only partly held.

## 4. What the results say about how to approach the problem

1. **The pitch "more data through federation gives better accuracy" is not supported by what we can test.** Within one cohort more donors help, but by about 0.01 from 8 to 17 donors at a within-slide level near 0.14. Across real sources the gain was small or negative, and the one clear loss came from mixing diseases. This agrees with the review's reading that the limit lies more in the representation and the within-slide signal than in the amount of data. It does not rule out gains at the scale of hundreds of centers, which the project cannot simulate from HEST-1k. A paper whose main claim is improved accuracy would need data we do not have.
2. **What is shown is that a federation is cheap and exact.** One message per center, no GPU, and a fit identical to pooling. That is a solid, honest proof of concept, but the estimator is not new. On its own it is an application note, not a methods paper.
3. **Heterogeneity between centers is the central technical issue.** Pooling unlike sources can hurt, and intercepts do not help the metric that matters. A method would have to decide how much each center should borrow from the others, for example through center-specific slopes, random effects on the coefficients, or weighting in the style of transfer learning (P209). That is a statistical problem with known tools and no application to this setting.
4. **Privacy cannot be claimed cheaply.** Spot-level noise already costs a tenth to a half of the accuracy, and patient-level protection would cost more. Secure aggregation is the cheaper way to protect centers' individual sums, but it does not make the released total private. A paper should say plainly which of these it offers. A privacy-focused method would enter a large differential privacy literature as an application.
5. **Partial gene overlap is the open problem with a measured cost and the most statistical content.** Centers on different platforms or panels will measure different genes. Fitting each gene from fewer centers costs 0.010 to 0.023. Borrowing strength across genes, for example by constraining the coefficient matrix $B$ to low rank so that a gene measured by one center shares directions estimated from all centers, is a natural method. It is exact-from-sums friendly, and nothing in the literature does it for response genes.
6. **Inference with center-level error connects to the PPI work.** The review found no method for uncertainty in a federated head whose error has a center-level component. Rounds 4 and 5 showed that center-level (cluster-level) accuracy governs what predictions buy. This is where the project's own expertise lies, but it is a larger undertaking and would compete with the PPI paper for time.

## 5. The decisions

Each item says who decides. The defaults hold until a decision is made.

1. **Whether to continue the federated learning line now** (Nicolas, with Dr. Zhu and David, open question R7-4 in `CLAUDE.md`). The options are to open a track for a proof-of-concept methods paper now, to pause it until the PPI paper is drafted, or to report the review and results to the advisors and let them decide. The PPI paper has the spring 2027 deadline and is in active work. Default, no federated learning track opens.
2. **What the paper would claim.** This is the substantive choice, and it should go to Dr. Zhu, since his proposal was about improving accuracy with data gathered as summary statistics. The results do not support that claim at the scale we can test. The realistic options are these.
   - (a) A characterisation paper. The exact one-round head, the learning curve, real against pseudo-centers, and the measured costs of privacy and partial overlap, with the honest conclusion that heterogeneity, not data volume, is the obstacle. This is the fastest and the closest to "preliminary proof of concept", with little methodological novelty.
   - (b) A method for partial gene overlap, with (a) as its motivation and experimental setting. This is the oversight chat's recommendation, for the reasons in section 4, item 5.
   - (c) A method for private release of the sums. Most directly tied to the privacy motivation of federated learning, but it competes with an established literature, and spot-level privacy is not the protection that matters.
   - (d) Inference for a federated head with center-level error. The best fit to the project's skills, and the least developed.
   - (e) A method for heterogeneity across centers (how much each center borrows). Natural and needed, but the most crowded of these in the general federated learning literature.
3. **The framing against David's textual knowledge base** (Nicolas, with David and Dr. Zhu, R7-2). The review compared the routes on evidence and took no side. Round 6 found that small cheatsheets did not beat the embedding head, and round 7 found that more embedding data helps only slowly. Neither route has evidence of breaking the accuracy ceiling. Default, the paper compares on evidence and does not argue against the other route.
4. **More data** (Nicolas). Testing real federations needs more than two sources per organ and technology, and only 3 of 18 groups on disk have two or more. Downloading more of HEST-1k, or STimage-1K4M (P131), would allow more real sources. Any download is Nicolas's decision. Default, none.
5. **Venue and authorship** (Nicolas, with his advisors, R7-3). Open.
6. **If a track opens, its first interval** (the oversight chat writes it after decisions 1 and 2). It would start with the three checks the closing report left (the split of the privacy cost between noise and penalty, partial overlap gene by gene, intercepts against center size), add a metric that pools test centers or mean squared error, and then build the chosen method.

**What to bring to the advisors.** The two-line summary is that a one-round federated head is exact and practical on the project's data, but federation across real sources did not improve accuracy, and the measurable obstacles are center heterogeneity, the accuracy cost of privacy and centers that measure different genes. The question for them is decision 2.
