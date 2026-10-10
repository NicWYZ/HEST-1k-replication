# Spatial Transcriptomics & Spatial Omics: A 2026 Methodology Landscape and Ranked Dissertation Shortlist

## TL;DR
- **Best fit for the student:** the strongest, most defensible, most quant-transferable direction is **statistically valid inference on ML-predicted / imputed spatial expression** (post-prediction / prediction-powered inference with calibration, conformal guarantees, and FDR control) — it is methodologically rich, biology-light, runs on HEST-1k, and maps almost one-to-one onto quant-finance skills (calibration, semi-supervised inference, distribution shift).
- **The field's central open problem is not accuracy but trust:** 2024–2026 benchmarks show histology→expression models barely beat cell-abundance baselines, contrastive pretraining can *degrade* expression prediction, single-cell/pathology foundation-model embeddings are dominated by batch/site effects, and single-cell foundation models show no clean scaling laws — so methods that quantify, calibrate, and correct these failures are where the gaps (and the ML/stats venues) are.
- **Avoid the crowded niche** of "yet another histology→expression architecture" (dozens of 2025–2026 papers: TRIPLEX, STFlow, GenAR, FLAG, HistoPrism, etc.); instead occupy the thinner, higher-rigor niches of uncertainty quantification, distribution-shift/batch-robust evaluation, spatial multiple-testing calibration, and optimal-transport alignment theory.

## Key Findings

**1. The technology shift has changed the modeling problem from "resolution" to "reconciliation."** Visium HD (2 µm bins) and Xenium Prime 5K now deliver near-single-cell or subcellular resolution, and head-to-head studies on identical lung/colorectal slides (Long et al., *J Exp Clin Cancer Res* 44:219, 2025) show the two platforms disagree in pathology-dependent ways: segmentation of irregular tumor nuclei favors Xenium, while transcriptome breadth favors Visium HD. This turns cell segmentation, spot→cell deconvolution/aggregation (e.g., STARS, *Nat Commun* 2026), and cross-platform harmonization into the dominant statistical problems, not spatial resolution per se. Large paired image–expression atlases now exist and make methods work feasible on public data: **HEST-1k** — 1,229 spatial transcriptomic profiles each linked to a whole-slide image, assembled from 153 cohorts across 26 organs and two species, with 367 cancer samples from 25 cancer types, yielding 2.1 million expression–morphology pairs and over 76 million nuclei (Jaume et al., NeurIPS 2024; the current GitHub release lists 1,276 paired samples and, as of v1.3.0 in Feb 2026, added Xenium 5K samples); **STImage-1K4M** — 1,149 ST slides encompassing 4,293,195 spots with paired gene expression, spanning 50 tissues (brain largest at 21.8%/251 slides) across Spatial Transcriptomics, Visium and Visium HD (Chen & Zou, NeurIPS 2024); and **SpatialCorpus-110M** (57M dissociated + 53M spatial cells) behind Nicheformer (https://github.com/mahmoodlab/hest; https://arxiv.org/abs/2406.06393; https://www.nature.com/articles/s41592-025-02814-z).

**2. Foundation models for ST/single-cell have well-documented, citable failure modes.** (a) *No scaling laws:* DenAdel, Hughes, Thoutam et al. (*Nature Methods* 23:1447–1457, Jul 2026; last author Lorin Crawford) pretrained 400 models on a corpus of 22.2 million cells via 6,400 experiments and concluded, "Unlike large language models, single-cell foundation models show no clear data scaling laws," with performance plateauing far below current corpus sizes (https://www.nature.com/articles/s41592-026-03120-y). (b) *Zero-shot weakness:* Kedzierska, Crawford, Amini & Lu ("Zero-shot evaluation reveals limitations of single-cell foundation models," *Genome Biology* 26:101, 18 Apr 2025) found Geneformer and scGPT "may face reliability challenges and could be outperformed by simpler methods," and for batch integration "Geneformer in particular consistently ranks lowest… often retaining or even amplifying batch-specific variation," lagging scVI and Harmony (https://link.springer.com/article/10.1186/s13059-025-03574-x). (c) *Perturbation:* Ahlmann-Eltze, Huber & Anders (*Nature Methods* 22:1657–1661, 2025) found deep models don't beat linear baselines for perturbation prediction. (d) *Batch dominance:* multiple 2025–2026 papers show pathology foundation-model embeddings (e.g., UNI2-h, ~122k HuggingFace downloads) cluster by tissue-source institution rather than biology (GLMP, arXiv:2606.28697; "Do Histopathological Foundation Models Eliminate Batch Effects?", arXiv:2411.05489; "Current Pathology Foundation Models are unrobust to Medical Center Differences," arXiv:2501.18055).

**3. Histology→expression prediction may be near a ceiling, and evaluation is fragile.** The HEST benchmark uses ridge/random-forest regression on frozen patch embeddings to predict top-50 highly variable genes by Pearson correlation (run on a single NVIDIA 3090 in the original paper). The HESCAPE benchmark (Gindra, …, Crawford, Peng, ICCV 2025 Workshops; https://arxiv.org/abs/2508.01490) found the striking result that contrastive cross-modal pretraining *improves* mutation classification but *degrades* direct expression prediction, and identified batch effects as the culprit. Data-quality ablations (bioRxiv, Sep 2025, PMID 40964396) show sparsity/noise cap performance and imputation "rescue" fails to generalize beyond the test set. This is strong evidence that the open problem is calibrated, distribution-shift-aware, uncertainty-carrying prediction — not higher Pearson r.

**4. Statistical inference on predicted expression is a small, fast-moving, high-rigor niche — the sweet spot.** Two 2026 preprints define it: **TIDEST** (Testa, Lei, Roeder — CMU Statistics & Data Science; bioRxiv, June 2026; PMC13320745) provides post-imputation differential-expression testing that calibrates reconstructed expression using measured genes and adjusts for latent spatial confounding, controlling FDR where SpaGCN/DESpace/SpatialGEE fail; and **CSDE** (Boyeau, Bates, Jordan, Yosef — UC Berkeley/Broad; bioRxiv 2026.01.15.699786) applies Prediction-Powered Inference to correct ST preprocessing (segmentation/annotation) bias using a small expert-validated set. Both descend from the canonical PPI literature (Angelopoulos, Bates, Fannjiang, Jordan, Zrnic, *Science* 382:669–674, 2023; PPI++, arXiv:2311.01453; cross-PPI, Zrnic & Candès, *PNAS* 2024) and post-prediction inference (Wang, McCormick, Leek, *PNAS* 117:30266, 2020; POP-Inf, Miao et al., *JMLR* 26:179, 2025). **TISSUE** (Sun, Ma, …, Zou, *Nature Methods* 21:444–454, 2024) is the conformal-inference precursor for imputed ST.

**5. Spatial multiple-testing and calibration are chronically broken.** Benchmarks of spatially-variable-gene (SVG) detection (*Genome Biology* 2023 and 2025; *Bioinformatics* btaf131, 2025) repeatedly find most methods produce poorly calibrated p-values and fail FDR control; SPARK-X and Moran's I are the robust baselines. Cell-cell communication / ligand-receptor inference has the same disease: spatial autocorrelation, count-depth variation, and measurement error induce spurious co-expression and inflated false positives (CONCISE, PMC13320749, 2026; SOAAR, PMC13370955, 2025). There is no gold standard for true LR interactions, so validation relies on simulation.

**6. Genetics integration is real but data-limited.** gsMap (Song, Chen, Hou, Guo & Yang, "Spatially resolved mapping of cells associated with human complex traits," *Nature* 641:932–941, 2025; https://www.nature.com/articles/s41586-025-08757-x) integrates ST with GWAS summary statistics via a spatially-aware S-LDSC framework on per-spot SNP annotations plus "the Cauchy combination test to aggregate P values of spots," benchmarked on embryonic ST covering 25 organs. A Spatial GWAS Atlas (NAR, 2025) now hosts 635 ST datasets × 3,854 GWAS. Critically, the authors state (Nature Reviews Genetics, 2025) that "As human ST data are limited, gsMap has been primarily applied to ST data from model organisms," and note sparsity/noise "can mask associations." Population-scale human ST for spatial-eQTL/TWAS is not yet broadly public — a feasibility risk for genetics-heavy directions.

**7. 3D/OT alignment is mature but has theoretical gaps.** PASTE (Gromov-Wasserstein OT, *Nature Methods* 2022), PASTE2 (partial OT), STalign (LDDMM diffeomorphisms, *Nat Commun* 2023), STAligner, SANTO, and DeST-OT (semi-relaxed OT for spatiotemporal growth/death) form a crowded applied space, but principled uncertainty on alignments, statistically valid downstream inference *after* alignment, and non-rigid deformation with guarantees remain open.

## Details: Ranked Dissertation Shortlist

Each direction lists: problem statement · why it's open · method sketch · data · risks · **quant-transfer score (1–10)** with justification · likely venue.

---

### #1 — Post-prediction / prediction-powered inference for spatial expression (calibrated, FDR-controlled downstream inference)
**Problem.** ML-predicted or imputed spatial expression (from histology via iStar/STFlow, or from scRNA reference via Tangram/CellPLM) is increasingly treated as if it were measured, biasing every downstream test (DE, SVG detection, gene-set enrichment, co-expression). We need estimators and tests that are *statistically valid* when a large machine-predicted dataset is combined with a small measured/gold-standard set.
**Why open.** Only two preprints (TIDEST, CSDE) exist as of mid-2026; the general PPI theory (Angelopoulos/Zrnic; POP-Inf) has barely been specialized to the spatial setting, where the "gold" set is itself noisy, spatially autocorrelated, and non-exchangeable — violating standard PPI/conformal exchangeability assumptions.
**Method sketch.** Extend PPI++/cross-PPI to a spatial regime: build a rectifier that models the joint law of (measured, predicted) expression as a function of spatial covariates; use spatially-blocked or diffusion-aware conformal calibration to restore coverage under autocorrelation; deliver valid confidence intervals and FDR-controlled SVG/DE tests. Prove coverage under a spatial-mixing (β-mixing) relaxation of exchangeability.
**Data.** HEST-1k (paired image + measured expression gives a natural gold set), plus Visium HD / Xenium held-out genes as ground truth for imputation calibration.
**Risks.** The two existing preprints could crowd the DE-specific slice quickly; mitigate by owning the *theory* (coverage under spatial dependence) and expanding to SVG/enrichment/co-expression, which they don't cover.
**Quant-transfer: 10.** This *is* semi-supervised inference / calibration / distribution-shift correction — the exact toolkit for combining a cheap noisy predictor with a small clean label set, which is the daily bread of quant signal research.
**Venue.** NeurIPS/ICML/AISTATS (methods), Annals of Applied Statistics / JASA (theory), Genome Biology (applied).

### #2 — Batch/site-robust representation learning and evaluation for multimodal ST (disentangling technical from biological variation)
**Problem.** Pathology and single-cell foundation-model embeddings are dominated by tissue-source-institution / platform / gene-panel batch effects; cross-modal contrastive pretraining can *degrade* expression prediction because of them (HESCAPE). We need methods that provably remove nuisance variation while preserving biological signal, and evaluation protocols that detect when they don't.
**Why open.** Existing fixes (stain normalization, Harmony, GLMP's LLM-mediated text bottleneck) are heuristic; there is no widely accepted, guarantee-bearing objective for invariance in this multimodal setting, and no standardized batch-adversarial benchmark for ST.
**Method sketch.** Cast as invariant-risk / domain-generalization with an explicit generative nuisance model of platform + panel + site; use OT- or HSIC-based independence penalties, or a causal front-door correction; evaluate with a battery quantifying "biology-retained vs. batch-removed" (kBET/iLISI-style but for prediction).
**Data.** HEST-1k (153 cohorts = natural site labels), HESCAPE (6 gene panels, 54 donors), STImage-1K4M.
**Risks.** Crowded on the *diagnosis* side; differentiate by focusing on ST-specific cross-panel generalization (gene-set mismatch across Xenium panels) which is under-studied.
**Quant-transfer: 9.** Distribution shift, domain generalization, invariant prediction, and nuisance/confounder removal are core to robust alpha across regimes and venues.
**Venue.** ICLR/NeurIPS, ICCV/CVPR workshops, Nature Communications.

### #3 — Cross-panel / cross-platform generalization of gene models under gene-set shift
**Problem.** Every imaging-based ST platform measures a different gene panel (Xenium 300 → 5K; CosMx 1K; MERFISH custom). Models trained on one panel cannot transfer to another, and whole-transcriptome (Visium HD) vs. targeted (Xenium) have different noise regimes. This is a covariate/label-space shift problem with rich structure (genes have ontology/pathway relationships).
**Why open.** Foundation models use fixed gene vocabularies; Nicheformer itself notes short panels hurt it. Principled transfer across variable gene supports — using gene embeddings/ontology priors as a shared latent space — is unsolved.
**Method sketch.** Represent genes in a shared ontology-informed embedding (GenePT/GeneCompass-style), model expression as a function over this space so panels become subsampled measurements of one latent field; use Gaussian-process / low-rank completion with a negative-binomial likelihood for principled cross-panel imputation and transfer.
**Data.** HEST-1k Xenium (multiple panels incl. 5K), Visium HD, CosMx subsets.
**Risks.** Requires modest biology (gene-set priors); ceiling may be low for rare genes.
**Quant-transfer: 8.** High-dimensional regression with structured/hierarchical priors, matrix completion, and transfer across shifting feature sets — directly analogous to cross-market factor transfer.
**Venue.** ICML/NeurIPS, AISTATS, Bioinformatics.

### #4 — Calibrated multiple testing for spatially dependent hypotheses (SVG detection & spatial DE with honest FDR)
**Problem.** SVG detection and spatial DE are pervasively miscalibrated (poor p-values, uncontrolled FDR under spatial autocorrelation and cell-type confounding). This is a pure spatial-statistics + multiple-testing problem.
**Why open.** Benchmarks (2023, 2025) show most tools fail; SPACE, spCorr, CONCISE are recent partial fixes but each addresses one confounder. A unified framework handling autocorrelation + count-depth + cell-type composition + dependency-aware FDR (Benjamini–Yekutieli / knockoffs on spatial fields) is missing.
**Method sketch.** Model counts with Poisson-lognormal / NB GLMM with a spatial random field; derive a calibrated score test; control FDR with spatial knockoffs or a dependency-aware step-up procedure; validate on scDesign3/SRTsim simulations with known ground truth.
**Data.** Simulation (scDesign3, SRTsim) for calibration truth + HEST-1k / Visium DLPFC for realism.
**Risks.** The most "classical biostatistics" of the list — risk of landing in a stats/bio journal rather than an ML venue; but methodologically clean and low-biology.
**Quant-transfer: 8.** Spatial covariance modeling, GLMMs, and dependency-aware multiple testing map to spatial/temporal covariance estimation and false-discovery control in backtesting.
**Venue.** Annals of Applied Statistics, Biometrika, JASA; Genome Biology.

### #5 — Uncertainty quantification for histology→expression via conformal prediction under distribution shift
**Problem.** Image-to-expression predictions (iStar, STFlow, TRIPLEX) are point estimates with no calibrated uncertainty; yet they're used for super-resolution and biomarker discovery. We need prediction sets/intervals with coverage guarantees that hold across organs/cohorts (distribution shift), not just i.i.d. splits.
**Why open.** TISSUE (2024) did conformal intervals for scRNA-reference imputation but not for the histology→expression map, and not under cross-cohort shift. HEST's patient-stratified splits are ideal for testing shift-robust conformal methods.
**Method sketch.** Split/CQR conformal on top of a frozen foundation-model regressor, extended with weighted/robust conformal (Barber et al. beyond-exchangeability; Tibshirani covariate-shift weighting) to handle organ/cohort shift; report per-gene, spatially-resolved coverage.
**Data.** HEST-1k (nine benchmark tasks, patient splits) — directly the student's first assignment.
**Risks.** Conformal-on-images is increasingly done; novelty must come from the spatial + cross-cohort-shift twist and multi-output (multi-gene) coverage.
**Quant-transfer: 9.** Conformal prediction, coverage under covariate shift, and probabilistic forecasting are increasingly standard in quant risk; extremely portable.
**Venue.** NeurIPS/ICML/AISTATS.

### #6 — Optimal-transport 3D alignment with valid post-alignment inference
**Problem.** OT/diffeomorphic alignment of serial sections (PASTE, STalign, DeST-OT) is mature for point estimates but gives no uncertainty on the alignment and no valid inference for tests run on aligned/integrated data.
**Why open.** No method propagates alignment uncertainty into downstream DE/domain-detection error rates; non-rigid deformation with statistical guarantees is unsolved; entropic-OT calibration is untouched here.
**Method sketch.** Bayesian or bootstrap OT to get a posterior over transport plans; propagate into downstream estimands; connect to entropic-OT / Sinkhorn statistical theory and Gromov-Wasserstein stability bounds.
**Data.** DLPFC 12-slice, mouse embryo Stereo-seq serial sections, HEST 3D-capable cohorts.
**Risks.** OT theory is hard; competition from strong OT groups. High reward if the inference-after-alignment angle is nailed.
**Quant-transfer: 9.** Optimal transport is now core quant tooling (distributional robustness, portfolio/coupling problems); GW/Sinkhorn expertise is highly marketable.
**Venue.** NeurIPS/ICML/AISTATS; Nature Methods (applied).

### #7 — Noise-model-aware generative modeling of counts with spillover/diffusion (probabilistic forecasting of spatial counts)
**Problem.** Spot/cell counts have overdispersion, dropout, and physical spillover/diffusion between neighbors; most deep ST models ignore the measurement model and use Gaussian losses on log1p data. A principled generative count model with a spatial diffusion/spillover kernel is missing at scale.
**Why open.** Debate persists on ZINB vs. NB vs. Poisson-lognormal ("zero-inflation not necessary" — Svensson-type findings vs. platform-dependent overdispersion); spillover is modeled ad hoc; flow/diffusion ST generators (STFlow, SpaDiT, GenAR) don't embed an explicit physical noise model.
**Method sketch.** Hierarchical Poisson-lognormal / NB latent field + convolution (spillover) kernel; fit with amortized variational inference; benchmark calibration of predictive count distributions, not just means.
**Data.** Xenium (subcellular, spillover visible), Visium HD, HEST-1k.
**Risks.** Some biology needed to argue the physical model; identifiability of spillover vs. true expression is subtle.
**Quant-transfer: 7.** Probabilistic forecasting, latent-variable count models, and calibration of predictive distributions transfer to volume/intensity modeling; slightly more domain-specific.
**Venue.** ICML/NeurIPS (probabilistic ML), AoAS, Genome Biology.

### #8 (stretch) — Spatially-resolved GWAS/heritability inference beyond gsMap
**Problem.** gsMap maps trait-associated cells but relies on S-LDSC point enrichment; uncertainty, cross-species transfer error, and the effect of ST sparsity on inferred associations are not rigorously handled.
**Why open.** Human ST is scarce; the statistical properties of spot-level heritability enrichment under noisy embeddings are unexamined; TWAS-with-spatial-context is nascent.
**Method sketch.** Reframe spot-trait association as a hierarchical model with propagated ST-embedding uncertainty; calibrate via null simulations; possibly semi-supervised using predicted expression (links to #1).
**Data.** gsMap public mouse/human ST + open GWAS summary stats; Spatial GWAS Atlas.
**Risks.** **Highest-biology, highest-data-risk** of the list; feasibility in 9 months is doubtful without a genetics collaborator. Flagged as biology-heavy; gsMap's own authors confirm human ST scarcity limits the approach.
**Quant-transfer: 6.** Hierarchical modeling and error propagation transfer, but the genetics overhead dilutes the quant payoff.
**Venue.** ASHG-adjacent (AJHG, Nature Genetics), or a stats journal if kept methodological.

## Competitor Map (avoid head-on collisions)
- **PPI-in-spatial (small, Berkeley-centric):** Yosef/Bates/Jordan (CSDE); the core PPI authors (Angelopoulos, Zrnic, Candès). **CMU:** Roeder/Lei/Testa (TIDEST) — the most formal DE-specific entrant (June 2026). → Own the *theory under spatial dependence* and non-DE estimands.
- **Imputation-calibration:** Zou/Sun (TISSUE, Stanford); Qiao/Huang (Univ. of Hong Kong, *Patterns* 2024). 
- **Valid spatial DE:** Irizarry (C-SIDE, Dana-Farber/Harvard); Nancy Zhang (Niche-DE, CellANOVA, UPenn/Wharton); smiDE (*Genome Biology* 2026); TESSERA (Berkeley).
- **Histology→expression architectures (very crowded — avoid):** dozens incl. TRIPLEX, STFlow, GenAR, FLAG, HistoPrism, GC-MoE, M2OST, mclSTExp, PH2ST, plus the student's own lab (iStar).
- **Foundation-model critique:** Kedzierska/Crawford/Lu (zero-shot limits); Ahlmann-Eltze/Huber (perturbation); DenAdel/…/Crawford (scaling-law study, *Nat Methods* 2026); Berlin/BIFOLD & TU-adjacent groups (pathology batch effects); the student's lab (GLMP).
- **Benchmarks:** Mahmood Lab (HEST); Peng/Crawford (HESCAPE); STImage-1K4M (Chen/Zou, UNC — note this is in-house/adjacent to the student's environment).

## Recommendations
1. **First 6–8 weeks (do this now):** replicate the HEST-1k benchmark as instructed, but instrument it for the *inference* agenda — log per-gene residuals, add patient-stratified vs. random splits to demonstrate leakage/shift, and reproduce the HESCAPE "contrastive degrades regression" finding. This single reproduction seeds Directions #1, #2, and #5 simultaneously and is low-risk on the group's existing SLURM/GPU footprint (HEST's own benchmark runs on a single 3090).
2. **Commit primarily to Direction #1 (post-prediction inference), with #5 (conformal under shift) as the concrete first paper.** Rationale: highest quant-transfer, lowest biology, runs entirely on HEST-1k + a GPU SLURM cluster, and the niche is small but validated (TIDEST/CSDE prove the field cares, yet leave the spatial-dependence theory and non-DE estimands open). Target a spring/summer 2027 AISTATS/ICML submission on shift-robust, spatially-valid conformal prediction for histology→expression, then a follow-on theory paper on PPI coverage under spatial mixing.
3. **Keep #4 (calibrated spatial multiple testing) as a parallel, simulation-driven track** — it's the cleanest pure-statistics paper and de-risks against #1 getting scooped.
4. **Treat #6 (OT alignment inference) as the "high-ceiling optional"** if the student wants a stronger optimization/OT portfolio for quant; only pursue if a math-heavy angle excites them.
5. **Deprioritize #8 (spatial GWAS)** unless a genetics collaborator materializes — it fails the 9-month/public-data test.
6. **Benchmarks/thresholds that should change the plan:** if a preprint appears extending PPI to spatial dependence with coverage proofs before ~Q1 2027, pivot #1 toward non-DE estimands (enrichment, co-expression, SVG) and the multi-output conformal angle. If HEST-1k Pearson ceilings prove too low to make UQ interesting (predictions near-random for most genes), shift weight to #2/#4 where the signal is in the nuisance structure, not the mean.

## Caveats
- **Publication-venue realism:** the purest statistics directions (#4, parts of #1) may land more naturally in AoAS/JASA/Biometrika/Genome Biology than in NeurIPS/ICML; the student should decide early whether "top ML venue" or "top stats venue" is the harder constraint, as it changes framing.
- **Biology-light flags:** Directions #1, #4, #5, #6 are genuinely biology-light (they treat expression as a signal to be calibrated/tested/aligned). #3 and #7 need modest gene-set/measurement biology. #8 is biology-heavy — flagged.
- **Crowdedness is real and fast-moving:** the histology→expression architecture space is saturated (multiple 2026 papers cited above); the inference/UQ space is thin *today* but attracting strong groups (Berkeley PPI, CMU Roeder, Stanford Zou), so speed and theoretical depth matter.
- **Source-quality notes:** several key items are 2026 preprints (TIDEST, CSDE, CONCISE, STARS, STORM) not yet peer-reviewed; treat their quantitative claims as provisional. The "no scaling laws" (*Nat Methods* 2026) and "foundation models underperform baselines" findings are now corroborated across multiple independent groups and are safe to build on. gsMap's own authors caution that human ST scarcity and sparsity can mask associations — a real limit on genetics directions.
- **One factual correction worth flagging:** CSDE is from the Yosef/Bates/Jordan group (Berkeley/Broad), not a Berlin/Ishaque group as sometimes assumed; the segmentation-error concern it shares is echoed by the separate smiDE method (*Genome Biology* 2026).
- **Feasibility assumption:** all recommended directions assume single-GPU-to-small-multi-GPU SLURM jobs suffice, matching HEST's own single-3090 benchmark footprint; none require foundation-model-scale pretraining, which is the right call given the documented absence of scaling returns.

### Key URLs
- HEST-1k: https://github.com/mahmoodlab/hest · https://proceedings.neurips.cc/paper_files/paper/2024/file/60a899cc31f763be0bde781a75e04458-Paper-Datasets_and_Benchmarks_Track.pdf
- STImage-1K4M: https://arxiv.org/abs/2406.06393
- HESCAPE: https://arxiv.org/abs/2508.01490 · https://github.com/peng-lab/hescape
- Nicheformer: https://www.nature.com/articles/s41592-025-02814-z
- Scaling-law study (Nat Methods 2026): https://www.nature.com/articles/s41592-026-03120-y
- Zero-shot limits (Genome Biology 2025): https://link.springer.com/article/10.1186/s13059-025-03574-x
- GLMP: https://arxiv.org/abs/2606.28697 · Pathology batch effects: https://arxiv.org/abs/2411.05489 · https://arxiv.org/pdf/2501.18055
- TIDEST: https://pmc.ncbi.nlm.nih.gov/articles/PMC13320745/ · CSDE: https://www.biorxiv.org/content/10.64898/2026.01.15.699786v1
- PPI (Science 2023): https://www.science.org/doi/10.1126/science.adi6000 · cross-PPI: https://www.pnas.org/doi/10.1073/pnas.2322083121 · PostPI: https://pubmed.ncbi.nlm.nih.gov/33208538/
- TISSUE: https://www.nature.com/articles/s41592-024-02184-y
- SVG calibration benchmarks: https://link.springer.com/article/10.1186/s13059-025-03731-2 · https://academic.oup.com/bioinformatics/article/41/4/btaf131/8096371
- CONCISE (spatial CCC): https://pmc.ncbi.nlm.nih.gov/articles/PMC13320749/
- gsMap (Nature 2025): https://www.nature.com/articles/s41586-025-08757-x · Spatial GWAS Atlas: https://academic.oup.com/nar/advance-article/doi/10.1093/nar/gkaf1103/8324959
- PASTE: https://www.nature.com/articles/s41592-022-01459-6 · STalign: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10709594/
- STFlow (ICML 2025): https://openreview.net/forum?id=Ossg1IbHDT · TRIPLEX: https://arxiv.org/html/2403.07592
- Visium HD vs Xenium 5K: https://link.springer.com/article/10.1186/s13046-025-03479-4