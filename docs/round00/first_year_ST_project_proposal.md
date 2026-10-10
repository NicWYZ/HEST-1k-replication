# First-Year Spatial Transcriptomics Project: Framing, Two Topics, and HEST-1k Replication Plan

Prepared September 2026. Exploratory first-year scope; not a dissertation commitment.

---

## 1. Framing

The project has three constraints that should shape every choice below.

1. It is exploratory. The goal is to learn the data, the field, and one or two method families well enough to know whether they deserve a dissertation, not to stake a dissertation on them now.
2. It should build transferable quantitative skill rather than domain knowledge. The two topics are chosen so that the biology is a wrapper around a statistical problem that exists in any field with cheap noisy predictors and expensive clean labels.
3. It should produce a submittable paper by spring or summer 2027, which means the first paper has to be reachable from the HEST replication with one clear methodological addition, not three.

The two topics are ordered. Topic A is the entry point and is achievable on the replication outputs alone. Topic B is the stretch and uses Topic A's outputs as an ingredient. Either could become the paper; doing A first is what makes B tractable.

---

## 2. The problem, stated carefully

### 2.1 What the field is doing

The task is to predict spatial gene expression from an H&E image. Concretely, for a Visium or Xenium sample, each measurement spot $i$ has a $112\,\mu\text{m}$ image patch $I_i$ and a count vector $y_i \in \mathbb{Z}_{\ge 0}^{G}$. A frozen pathology foundation model gives an embedding $z_i = f(I_i) \in \mathbb{R}^d$, and a head $h$ predicts $\hat{y}_i = h(z_i)$ (or, for slide-level models like STFlow and TRIPLEX, $\hat{y}_i = h(z_i, \{z_j\}_{j \in \mathcal{N}(i)})$). Evaluation is Pearson correlation between $\log(1+y)$ and $\hat{y}$ on the 50 most variable genes, under patient-stratified folds.

The reason people care is that H&E is free and universal while ST costs thousands of dollars per slide. If the map $I \to y$ were reliable, every archival H&E cohort (TCGA has over 11,000 cases) would become a spatial transcriptomics cohort. That is the actual value proposition, and it is why predicted expression is already being used downstream: iStar for super-resolution, HEST's biomarker section for morphology-expression correlations, STFlow for biomarker gene maps, and many 2025-2026 papers for "virtual ST" on H&E-only cohorts.

### 2.2 Where the literature stands (September 2026)

Three findings from the last eighteen months change the problem.

**Accuracy has a ceiling and it is low.** The best encoder on HEST reaches average Pearson $\approx 0.41$; individual tasks range from $0.64$ (melanoma) to $0.23$ (rectum). STFlow adds spatial context and gets to $0.415$ with UNI features. The HESCAPE benchmark (Gindra et al., 2025) found that contrastive image-expression pretraining, which was supposed to be the next step, actually degrades direct expression prediction, and traced this to batch effects. Data-quality ablations show sparsity and noise cap performance and that imputation-based "rescue" does not generalize. The scaling-law study in *Nature Methods* (July 2026) found no clear data scaling for single-cell foundation models across 400 pretrained models. Pushing Pearson up is a crowded, low-yield direction.

**Embeddings are dominated by nuisance variation.** GLMP (our group), Kömen et al., and de Jong et al. show that a linear probe recovers tissue-source institution from UNI2/Virchow2 embeddings at near-100% accuracy, that stain normalization does not fix it, and that under label-site confounding the models collapse. Since HEST spans 153 cohorts, two species, and three technologies, every patient-stratified fold is also a site or platform shift, and nobody has characterized what that does to the reliability of a prediction.

**Predictions are used as if measured, and this is now documented as a failure.** The June 2026 preprint from Roeder's group is titled "Accurate prediction in reconstructed spatial transcriptomes does not ensure valid biological discovery" and shows that downstream differential-expression tests on imputed expression lose FDR control. A Berkeley preprint (CSDE) applies prediction-powered inference to correct segmentation bias in ST pipelines. These are the only two papers applying valid-inference machinery to ST as of this writing.

### 2.3 The gap, and why it is the right gap for us

Put together: the field has moderately accurate point predictors whose errors depend on site and platform, and those predictions feed downstream analyses with no accounting for error. Two questions follow, and each is a topic.

- **How wrong is a given prediction, and does the answer hold when the cohort changes?** No method gives per-spot, per-gene calibrated uncertainty for the histology-to-expression map. TISSUE (Sun et al., 2024) gives conformal intervals for scRNA-reference imputation, not for image prediction, and not under cohort shift.
- **If predictions are used to estimate something about a population, how do we get valid confidence intervals?** The general theory exists (prediction-powered inference, post-prediction inference, DML-style debiasing). It assumes exchangeable or i.i.d. data. Spatial data violate that within a slide, and cohorts violate it across slides. The two existing ST applications are narrow (DE; segmentation) and do not treat the dependence problem.

Both gaps are statistical, not biological. Both are answerable on HEST-1k because HEST provides the one thing valid-inference methods need: a set of patches where the truth (measured expression) is known alongside the prediction. And both connect to the semi-supervised inference literature (SynSurr, PPI, DML) that has already appeared in the group's journal club, which lowers the learning cost and raises the odds of useful supervision.

---

## 3. Topic A: Calibrated uncertainty for histology-to-expression prediction under cohort shift

### 3.1 Problem statement

Given a frozen encoder and a regression head trained on HEST tasks, produce for each held-out spot $i$ and gene $g$ a prediction interval $C_{ig}$ such that

$$\mathbb{P}\big(y_{ig} \in C_{ig}\big) \ge 1-\alpha$$

and characterize how coverage behaves when the held-out patient comes from a different institution or technology than the training patients.

### 3.2 Why this is open

The HEST benchmark reports Pearson only. Per-fold standard deviations in Table 1 are large (often $\pm 0.08$ on a mean of $0.5$), and folds are patients, so the variance is largely cohort shift, not sampling noise. Nobody has asked whether the uncertainty implied by a model is honest, whether it degrades across sites, or whether the encoder ranking by Pearson matches the ranking by calibration. Conformal methods that handle covariate shift (Tibshirani et al. 2019 weighted conformal; Barber et al. 2023 beyond exchangeability) exist but have not been applied here, and the multi-output structure (50 correlated genes per spot) is a real complication.

### 3.3 Method sketch

Base predictor. Reuse the replication's PCA-256 + ridge head so that the uncertainty layer is the only new thing. A second base predictor, a heteroscedastic negative-binomial head $y_{ig} \mid z_i \sim \mathrm{NB}(\mu_g(z_i), \phi_g)$, gives a model-based predictive distribution to compare against.

Split conformal. Hold out calibration spots (from training patients, not test patients), compute nonconformity scores $s_{ig} = |y_{ig} - \hat{y}_{ig}|$ or the CQR score using quantile regression, and set $C_{ig} = \hat{y}_{ig} \pm \hat{q}_{g,1-\alpha}$. Report marginal coverage on test patients.

Shift-aware conformal. Estimate a density ratio $w(z) = p_{\text{test}}(z)/p_{\text{cal}}(z)$ with a site classifier on the embeddings (this is exactly the GLMP TSI-prediction probe reused as a weight estimator), and use the weighted conformal quantile. Compare coverage under three regimes: random spot split (i.i.d., should be fine), patient split within site, and leave-site-out.

Evaluation. Marginal and conditional coverage (by site, technology, tissue, and by predicted-expression decile), interval width, and proper scoring rules (CRPS, log score for the NB head). The key deliverable is a table like HEST's Table 1 but with coverage and width per encoder per task.

### 3.4 Contribution

A benchmark of uncertainty for the standard task, a demonstration of how far naive intervals miss under site shift, a shift-aware fix, and an empirical answer to whether "best by Pearson" and "best calibrated" coincide. This is a self-contained AISTATS or ICML-workshop paper reachable from the replication.

### 3.5 Quant transfer

Conformal prediction, coverage under covariate shift, density-ratio reweighting, proper scoring rules, and the discipline of separating calibration from test data are core skills for probabilistic forecasting and risk modeling.

---

## 4. Topic B: Valid inference for population quantities using predicted expression

### 4.1 Problem statement

Let $\theta$ be a scalar quantity defined on the joint distribution of expression and a covariate available from H&E alone. Examples that need no biology beyond what HEST already computed:

- $\theta_1 = \mathrm{Corr}(\text{nuclear area}_i,\; \log(1+y_{ig}))$ for a fixed gene, using CellViT nuclear features shipped with HEST (HEST Figure 3 reports $r = 0.47$ for GATA3 on one slide).
- $\theta_2 = \mathbb{E}[\log(1+y_{ig}) \mid \text{neoplastic}] - \mathbb{E}[\log(1+y_{ig}) \mid \text{stromal}]$, a difference in mean expression between nuclear classes.
- $\theta_3 = $ the slope in $\log(1+y_{ig}) = \beta_0 + \beta_1 \cdot m_i + \varepsilon$ for a morphology feature $m_i$.

We have a small labeled set $\{(x_i, y_i)\}_{i=1}^{n}$ of spots with measured expression and a large unlabeled set $\{x_j\}_{j=1}^{N}$ of patches with only H&E (from H&E-only slides, or from held-out ST slides with expression masked), plus a predictor $\hat{y} = h(z)$. The goal is a confidence interval for $\theta$ that is valid regardless of how good $h$ is, and narrower than the labeled-only interval when $h$ is good.

### 4.2 Why this is open

Prediction-powered inference (Angelopoulos et al., *Science* 2023; PPI++; cross-PPI) gives exactly this for i.i.d. data:

$$\hat{\theta}^{\mathrm{PP}} = \underbrace{\frac{1}{N}\sum_{j=1}^{N} \hat{y}_j\text{-based estimate}}_{\text{plug-in on unlabeled}} \;-\; \underbrace{\frac{1}{n}\sum_{i=1}^{n}\big(\hat{y}_i\text{-based} - y_i\text{-based}\big)}_{\text{rectifier on labeled}}$$

with a tuning parameter $\lambda$ that interpolates between classical and plug-in. The variance formula assumes independent observations. In ST, spots within a slide are spatially correlated and share a slide-level batch effect, so the labeled set is far from $n$ independent draws, and the effective sample size is closer to the number of slides than the number of spots. Naive PPI will undercover. TIDEST addresses DE specifically with a latent-confounder adjustment; CSDE addresses segmentation bias. Neither handles general estimands with a dependence-aware variance.

### 4.3 Method sketch

Estimator. Implement PPI++ for $\theta_1, \theta_2, \theta_3$ with cross-fitting so that $h$ is never trained on the labeled spots used for rectification (this mirrors DML's cross-fitting and is what makes the theory clean).

Variance under dependence. Replace the i.i.d. variance with a slide-level cluster estimator, and separately a spatial block bootstrap within slide (blocks of adjacent spots). Compare against a naive spot-level variance to show how much it undercovers.

Validation by semi-synthesis. Use HEST slides with measured expression, mask expression on a fraction of spots or entire slides to create the "unlabeled" set, and check empirical coverage of the interval for $\theta$ against the value computed from the full data. This gives ground truth without simulation from a model.

Power. Report the interval-width ratio (PPI vs classical) as a function of predictor quality, which is a direct diagnostic of when virtual ST is worth anything for a given estimand.

### 4.4 Contribution

An empirical demonstration that plug-in inference on predicted expression is biased and that naive PPI undercovers on ST due to spatial and slide-level dependence; a dependence-aware PPI variance with cluster and block-bootstrap options; and a practical answer to "how many measured slides do you need to make H&E-only inference trustworthy." If time allows, a coverage argument under a spatial mixing condition, which is the piece that would move this from applied to methodological. This is a NeurIPS/ICML paper if the theory lands, or a *Genome Biology* / AoAS paper if it stays empirical.

### 4.5 Quant transfer

This is semi-supervised inference with a learned surrogate under dependence: the exact structure of using a fast model-derived signal alongside a small set of realized outcomes, with cluster-robust and block-bootstrap variance. It builds directly on the SynSurr/PPI/DML material from the journal club.

---

## 5. How A and B fit together, and what to tell the advisors

A produces per-spot predictive distributions; B needs a predictor and a way to characterize its error. The shift-aware weights from A are also the natural covariate-shift correction inside B's rectifier when the unlabeled slides come from a different site. Batch and site shift is the evaluation axis for both, which connects to GLMP without competing with it.

The sentence for Dr. Zhu and David: *We are asking how much to trust histology-predicted expression, first by giving it calibrated uncertainty that survives cohort shift, then by showing how to use it for valid population-level inference when only a few slides have measured expression.*

A fallback if both stall: calibrated multiple testing for spatially variable genes (report direction #4), which needs only simulation and Visium DLPFC and is the cleanest pure-statistics paper.

---

## 6. HEST-1k replication plan

### 6.1 Principles

Faithful first, tailored second. Every deviation from the paper's protocol is logged and run alongside the faithful version, never instead of it. The replication is instrumented so that its byproducts are the inputs to Topics A and B.

### 6.2 Scope and storage

Do not download the full 1 TB. HEST-Library supports metadata-filtered download; pull the benchmark subset first (tasks 1 to 9 per Table A11, about 70 samples, tens of GB including WSIs), then the remaining Visium/Xenium samples later if needed. Note that the benchmark COAD task was updated after the paper (STFlow's footnote), so Task 5 numbers will not match Table 1 exactly; record the dataset version.

Longleaf layout: raw HEST data on `/work` or the group's project space, embeddings and results on `/work` with a manifest, code in a git repo. Stamp output directories with a provenance file (job ID, commit, date) so results are attributable when other sessions write to the same tree.

### 6.3 Faithful reproduction (target: 3 to 4 weeks)

**Week 1. Environment and data.**
Install `hest` and its benchmark dependencies in a conda env on Longleaf. Request HuggingFace gated access for UNI, UNIv1.5, CONCH, Virchow, Virchow2, H-Optimus-0, GigaPath (some approvals take days; start immediately). Download the benchmark subset. Verify each sample loads: WSI as pyramidal TIFF, AnnData with raw counts, spot coordinates, CellViT nuclei geojson. Confirm patch extraction gives $224 \times 224$ at $20\times$, $112\,\mu\text{m}$, centered on spots.

**Week 2. Embeddings.**
Run the HEST benchmark script to extract patch embeddings for the 11 encoders on all benchmark spots. One GPU job per encoder; ViT-giant models need an 80 GB card or reduced batch size. Save embeddings as HDF5 keyed by sample and spot barcode, with per-spot metadata columns: patient, sample, cohort source, technology (Visium/Xenium), organ, tissue preparation. This metadata is what Topics A and B need and is the main tailoring at this stage.

**Week 3. Heads and Table 1.**
For each task: select the 50 HVGs per the paper (exclude genes with non-zero counts in fewer than 10% of spots, then top 50 by normalized variance), log1p-normalize, patient-stratified folds ($k$ = number of patients; $k/2$ for ccRCC). Run three heads: PCA-256 + ridge with $\lambda = 100/(M \cdot C)$; plain ridge; XGBoost with 100 estimators, depth 3, learning rate 0.1. Compute per-gene Pearson on each fold, average over genes, report mean $\pm$ SD across folds. Reproduce Tables 1, A13, A14. Expect small discrepancies from library versions and the COAD update; anything above roughly $0.03$ on a task average deserves investigation.

**Week 4. Sanity and write-up.**
Reproduce the scaling-law scatter (Figure 2) from Table A12 parameter counts. Write a short replication memo with a discrepancy table. This memo is what you show David before touching the topics.

### 6.4 Tailored additions (run alongside, weeks 3 to 6)

These are the instrumentation that turn the replication into the project's motivation section.

**Per-gene, per-spot residuals.** Save $\hat{y}_{ig}$ and $y_{ig}$ for every fold, not just the Pearson summary. This is the raw material for conformal calibration (A) and for the PPI rectifier (B).

**Split comparison.** Rerun PCA + ridge for the best encoder under three splits: (i) random spot-level split ignoring patient, (ii) the paper's patient split, (iii) leave-site-out where sites are the cohort sources in the metadata (this is possible for ccRCC with 24 patients from one study versus Xenium tasks from 10x; also across the whole HEST-1k collection beyond the benchmark). The gap between (i) and (ii) quantifies leakage; the gap between (ii) and (iii) quantifies site shift. Both are the first figure of Topic A.

**Count diagnostics.** For each benchmark task, tabulate per-gene zero fraction, mean, and variance-to-mean ratio for the 50 HVGs, and fit NB and ZINB per gene by maximum likelihood to see whether zero inflation is needed beyond NB. This grounds the NB head in A and the noise argument in the introduction.

**Site-predictability probe.** Train a linear probe to predict cohort source and technology from each encoder's embeddings, replicating GLMP's Table 2 on HEST. This links the replication to the group's own paper and provides the density-ratio estimator for weighted conformal in A.

**Morphology features for B.** From the shipped CellViT geojson, compute per-spot summaries: nuclear count, mean nuclear area, fraction of neoplastic/stromal/inflammatory nuclei. Join to the spot table. Recompute HEST's Figure 3 correlation (nuclear area versus GATA3 on the IDC Xenium sample) as a first estimand and as a check that the geometry alignment is correct.

**One stronger baseline (optional, week 6).** Run STFlow from its public code with UNI features on the benchmark to confirm its $0.415$ average. This tells you whether a spatial-context predictor changes the calibration story, and it is a natural base predictor for B.

### 6.5 Deliverables at the end of replication

1. A replication memo with reproduced tables and a discrepancy log.
2. An HDF5 store of embeddings, predictions, residuals, and metadata for all benchmark spots and encoders.
3. Three figures: leakage/shift gap, count diagnostics, site-predictability by encoder.
4. A one-page draft of the motivation section for Topic A written from those figures.

### 6.6 Compute and time budget

Embedding extraction is the only heavy step: roughly 100k benchmark patches $\times$ 11 encoders, a few GPU-hours each on an A100, more for the ViT-giant models. Heads and diagnostics run on CPU in minutes. Six weeks total is realistic if HuggingFace approvals arrive on time; request them today.

---

## 7. Reading list to pair with the replication

Ordered by when you will need each.

1. HEST-1k, Sections 3 and 5 and Appendix C (already read). Reread C.3 before writing the heads.
2. Angelopoulos, Bates, Fannjiang, Jordan, Zrnic. Prediction-powered inference. *Science* 2023. Then PPI++ (arXiv:2311.01453). These are short and give the estimator and variance for Topic B.
3. Angelopoulos and Bates, "A gentle introduction to conformal prediction" (arXiv:2107.07511), Sections 1 to 3, then Tibshirani et al. 2019 on covariate shift. Topic A.
4. Gindra et al., HESCAPE (arXiv:2508.01490). The batch-effect finding that motivates the shift axis.
5. GLMP (our group). Reread Section 4.7 for the site-predictability protocol.
6. Testa, Lei, Roeder, TIDEST (bioRxiv, June 2026), and CSDE (bioRxiv, Jan 2026). The two competitors; read to see exactly what they do not cover.
7. Chernozhukov et al., Double/debiased machine learning (2018), Section 1 to 3, for the cross-fitting logic shared by B.
