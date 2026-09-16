# Handoff: HEST-1k Benchmark Replication and First-Year Spatial Transcriptomics Project

Prepared 12 September 2026 for a Claude Science session with SSH access to UNC Longleaf. Companion file: the HEST-1k paper (Jaume et al., NeurIPS 2024, arXiv:2406.16192v2). Read this document fully before running anything.

---

## 0. How to use this document

You are the execution agent. A separate chat session (the "oversight chat") audits your reports, makes scope decisions, and drafts instructions for the student. The student is Nicolas Weiyang Zhang, Longleaf ONYEN `weiyang`, first-year biostatistics PhD at UNC. He reads and understands every command before it runs and will push back on unexplained steps, so explain what each command does and why before executing it.

Sections 1 to 5 give context so that your judgment calls are informed. Section 6 is the plan you execute. Section 7 lists pitfalls found by reading the current HEST codebase. Section 8 sets what you may decide alone versus escalate. Section 9 is the reporting format.

Working principles from prior work in this group, which apply here:

- Silent failure is the main risk. Nearly every serious bug in the group's previous pipelines raised no error. Verify each stage's output explicitly against an expected value before moving on.
- Never assert a number or scope you have not confirmed from actual output. State what was checked and what was not.
- When a workflow gets messy, restart it cleanly rather than accumulating patches.
- Stamp every output directory you create and every batch job you submit with provenance (job ID, git commit, date, config hash), since other sessions write to the same filesystem.

---

## 1. Project context

### 1.1 Who and what

Nicolas is in Dr. Hongtu Zhu's group at UNC Gillings. His GRA is supervised by Dr. Daiwei (David) Zhang, first author of iStar (super-resolution ST from histology, *Nat Biotech* 2024) and corresponding author of GLMP (batch-effect-robust histology embeddings via an LLM text bottleneck). Dr. Zhu and David have set spatial transcriptomics as Nicolas's focus for the year, with an explicit instruction that the work be methodological (devising methods) rather than applied (running existing methods on data). Target: a submittable paper by spring or summer 2027.

The first concrete assignment from the advisors is to download HEST-1k and replicate the paper's results. That replication is what you will execute.

### 1.2 Framing

This is an exploratory first-year project. It may or may not become dissertation work. Two proposed topics (Section 5) are ordered so that Topic A is reachable from the replication outputs alone and Topic B builds on A. The replication is instrumented so that its byproducts become the motivation and inputs for both topics.

Nicolas's constraints, which shape all choices:

- Minimal biology. The topics treat expression as a signal to be predicted, calibrated, and used for inference; no gene-level biology is required.
- Transferable quantitative skill. His long-term goal is quantitative research in finance, so the project emphasizes probabilistic prediction, calibration, distribution shift, and semi-supervised inference.
- ML venues (NeurIPS, ICML, AISTATS) or top statistics journals are preferred over biology journals.

### 1.3 Environment

- HPC: UNC Longleaf, SLURM, accessed via OnDemand or SSH. GPU partitions exist (Volta and A100 class); check `sinfo -o "%P %G %D"` to confirm current partition names and GPU types before submitting.
- No `sudo`. System-level dependencies (libvips, openslide) must come from conda-forge, not `apt`.
- Confirm whether compute nodes have outbound internet; if not, do all HuggingFace downloads from a login or data-transfer node and set `HF_HOME` to a path on `/work` or the group's project space, not `$HOME`.
- Storage: check quotas with `quota -s` or the Longleaf-specific command before downloading. The benchmark subset is small (tens of GB); the full HEST-1k archive is over 2 TB and is not needed for this plan.

---

## 2. Scientific background in one page

Gene expression is a count of mRNA transcripts per gene. Spatial transcriptomics (ST) measures it at known positions on a tissue section. Sequencing-based platforms (Visium, spot diameter 55 µm, whole transcriptome of roughly 18k to 36k genes) and imaging-based platforms (Xenium, subcellular, panels of hundreds to a few thousand genes) are both present in HEST. HEST pools Xenium transcripts into 55 µm "pseudo-Visium" spots so both share one format.

An H&E whole-slide image (WSI) is a gigapixel scan of the stained section. HEST extracts a 224 × 224 pixel patch at 20× (0.5 µm/px, so 112 µm square) centered on each spot. A frozen pathology foundation model (UNI, Virchow, H-Optimus, CONCH, GigaPath, etc.) maps each patch to an embedding vector.

The benchmark task: for each of nine cancer tasks, predict the log1p counts of the 50 most variable genes from the patch embedding, evaluated by Pearson correlation per gene, averaged over genes, with patient-stratified cross-validation folds.

Statistical properties of the target that matter for the project: counts are sparse (most entries zero), overdispersed (variance exceeds mean; negative binomial is the standard model, sometimes with zero inflation), spatially autocorrelated (neighboring spots share cell types and, on Visium, physically leak transcripts into each other), and subject to batch effects across labs, platforms, and tissue preparation.

---

## 3. Literature landscape (as of September 2026)

The following is condensed from a broader review; citations are at the end.

**Data and benchmarks.** HEST-1k (1,229 samples in the paper; the current release lists 1,276 with Visium HD and Xenium 5K additions through February 2026) and STImage-1K4M (1,149 slides, 4.3M spots; Chen and Zou, NeurIPS 2024) are the paired image-expression atlases. HEST-Benchmark's current leaderboard (updated 3 April 2026 on GitHub) covers 25 encoders; the paper's Table 1 covers 11.

**Prediction has a low ceiling.** Best average Pearson on HEST is about 0.42 (H-Optimus-1 on the current leaderboard; 0.4146 for H-Optimus-0 in the paper). Task-level values range from 0.66 (melanoma) to 0.18 to 0.25 (rectum). STFlow (Huang et al., ICML 2025) adds spatial context via flow matching and reaches 0.415 with UNI features. HESCAPE (Gindra et al., 2025) found that contrastive image-expression pretraining degrades direct expression prediction and traced this to batch effects. A *Nature Methods* 2026 study of 400 pretrained single-cell foundation models found no clear data scaling laws. Pushing Pearson up is a crowded, low-yield direction.

**Embeddings are dominated by nuisance variation.** GLMP (Zhang, Wu, ..., Zhu, Wu, D. Zhang; this group), Kömen et al. (arXiv:2411.05489), and de Jong et al. (arXiv:2501.18055) show that a linear probe recovers tissue-source institution from UNI2/Virchow2 embeddings at near-100% accuracy, that stain normalization does not fix it, and that models collapse under label-site confounding. HEST spans 153 cohorts, so every patient-stratified fold is also a site or platform shift.

**Predicted expression is used as if measured.** Testa, Lei, Roeder (CMU; bioRxiv June 2026, "Accurate prediction in reconstructed spatial transcriptomes does not ensure valid biological discovery") show that DE tests on imputed expression lose FDR control and propose a calibration using measured genes. Boyeau, Bates, Jordan, Yosef (Berkeley/Broad; bioRxiv Jan 2026, CSDE) apply prediction-powered inference to correct segmentation bias. These are the only two applications of valid-inference machinery to ST as of this writing. The general theory is prediction-powered inference (Angelopoulos et al., *Science* 2023; PPI++; cross-PPI) and post-prediction inference (Wang, McCormick, Leek, *PNAS* 2020; POP-Inf, *JMLR* 2025). TISSUE (Sun et al., *Nat Methods* 2024) gives conformal intervals for scRNA-reference imputation, not for the histology-to-expression map.

---

## 4. The gap and our angle

The field has moderately accurate point predictors of expression from H&E whose errors depend on site and platform, and those predictions are fed into downstream analyses (super-resolution, biomarker discovery, "virtual ST" on H&E-only cohorts such as TCGA) with no accounting for error.

Two questions follow, and each is a topic:

1. How wrong is a given prediction, and does the answer hold when the cohort changes? No method gives per-spot, per-gene calibrated uncertainty for the histology-to-expression map, and nobody has characterized coverage under site shift.
2. If predictions are used to estimate a population quantity, how do we get valid confidence intervals? The PPI theory assumes exchangeable data; spots within a slide are spatially dependent and slides carry batch effects. The two existing ST applications are narrow and do not treat dependence.

Both are statistical questions. Both are answerable on HEST-1k because HEST provides the one ingredient valid-inference methods need: patches where the truth (measured expression) is known alongside the prediction.

---

## 5. The two topics

### Topic A. Calibrated uncertainty for histology-to-expression prediction under cohort shift

Goal: for each held-out spot $i$ and gene $g$, produce an interval $C_{ig}$ with $\mathbb{P}(y_{ig} \in C_{ig}) \ge 1 - \alpha$, and characterize coverage when the held-out patient comes from a different institution or technology than the training patients.

Method sketch. Keep the benchmark's PCA-256 + ridge head as the base predictor so the uncertainty layer is the only new component. Add a heteroscedastic negative-binomial head as a model-based comparator. Apply split conformal (absolute residual score, and CQR with quantile regression) with calibration spots drawn from training patients. Apply weighted conformal for covariate shift, where the weight $w(z) = p_{\text{test}}(z)/p_{\text{cal}}(z)$ is estimated by a site classifier on the embeddings (this reuses GLMP's site-prediction probe as a density-ratio estimator). Evaluate marginal and conditional coverage (by site, technology, tissue, predicted-expression decile), interval width, and proper scoring rules (CRPS; log score for the NB head) under three regimes: random spot split, patient split within site, leave-site-out.

Deliverable: a table like HEST Table 1 but with coverage and width per encoder per task, plus a finding on whether "best by Pearson" and "best calibrated" coincide.

### Topic B. Valid inference for population quantities using predicted expression

Goal: for a scalar estimand $\theta$ defined on the joint distribution of expression and a covariate available from H&E alone, deliver a confidence interval that is valid regardless of predictor quality and narrower than the labeled-only interval when the predictor is good.

Candidate estimands (all computable from HEST's shipped CellViT nuclear segmentation, no new biology):

- $\theta_1 = \mathrm{Corr}(\text{mean nuclear area}_i, \log(1+y_{ig}))$ for a fixed gene (HEST Figure 3 reports $r = 0.47$ for GATA3 on one IDC Xenium slide).
- $\theta_2 = \mathbb{E}[\log(1+y_{ig}) \mid \text{neoplastic-dominant spot}] - \mathbb{E}[\log(1+y_{ig}) \mid \text{stromal-dominant spot}]$.
- $\theta_3$ = slope of $\log(1+y_{ig})$ on a morphology feature.

Method sketch. Implement PPI++ with cross-fitting (the predictor is never trained on the labeled spots used for rectification). Replace the i.i.d. variance with a slide-level cluster estimator and a within-slide spatial block bootstrap. Validate by semi-synthesis: mask expression on a fraction of spots or entire slides to create the unlabeled set, and check empirical coverage against the full-data value. Report the PPI-to-classical interval-width ratio as a function of predictor quality.

### How A and B connect

A produces per-spot predictive distributions and site-shift weights; B needs a predictor, its error characterization, and a covariate-shift correction inside the rectifier. Site and platform shift is the evaluation axis for both.

---

## 6. Replication plan (staged)

### 6.0 Principles

Faithful first, tailored second. Every deviation from the paper's protocol is run alongside the faithful version, never instead of it, and logged. Each stage has an acceptance check; do not proceed past a failed check without reporting.

### 6.1 What the current codebase actually does (read before Stage 1)

The HEST GitHub repository has moved on from the paper in ways that matter:

- Encoders are loaded through TRIDENT (Mahmood Lab's patch-encoder library), not through HEST's own model zoo. Encoder names in `bench_config/bench_config.yaml` are TRIDENT names: `resnet50`, `ctranspath`, `phikon`, `phikon_v2`, `uni_v1`, `uni_v2`, `conch_v1`, `conch_v15`, `gigapath`, `virchow`, `virchow2`, `hoptimus0`, `hoptimus1`, `hibou_l`, `musk`, `midnight12k`, `h0-mini`, `openmidnight`, `gpfm`, and several Kaiko/Lunit models.
- Benchmark data (pre-extracted patches as HDF5, per-sample AnnData with counts, patient-stratified split CSVs, per-task gene lists) live in a separate, small HuggingFace dataset `MahmoodLab/hest-bench`, downloaded automatically by `benchmark.py` via `snapshot_download(repo_id="MahmoodLab/hest-bench", ...)`. You do not need the 2 TB HEST-1k archive for the benchmark.
- The benchmark script already saves, per task, per encoder, per split: `results.json`, `summary.json`, and `inference_dump.pkl` containing `preds_all` and `targets_all` (test-set predictions and targets, spots × 50 genes). This is most of the instrumentation Topic A and B need. Row order in the dump follows the concatenation of test-split samples in the split CSV order, with barcodes taken from each sample's embedding HDF5; you will need to reconstruct the barcode-to-row mapping (Stage 4).
- Normalization: `normalize_adata` applies `sc.pp.log1p` only. Despite its docstring, it does not do total-count normalization. It is applied to the 50-gene subset after subsetting. Match this exactly for the faithful run.
- Regression head: `StandardScaler` then `PCA(n_components=256, random_state=seed)` fit on train embeddings; `Ridge(solver='lsqr', alpha=100/(256 × 50), fit_intercept=False, max_iter=1000)`. Note `fit_intercept=False`. The alternative heads in the paper (plain ridge, XGBoost) are selected by the `method` argument.
- Task table in the current tutorial: IDC (TENX95, TENX99, NCBI783, NCBI785; Xenium), PRAD (MEND139 to MEND162; Visium, 23 samples), PAAD (TENX116, TENX126, TENX140; Xenium), SKCM (TENX115, TENX117; Xenium), COAD (TENX111, TENX147, TENX148, TENX149; **Xenium**), READ (ZEN36, ZEN40, ZEN48, ZEN49; Visium), ccRCC (INT1 to INT24; Visium), LUAD (TENX118, TENX141; Xenium), LYMPH_IDC (NCBI681 to NCBI684; Visium).
- COAD changed after the paper. The paper's appendix describes COAD as Visium; the benchmark was updated (30 August 2024) to four Xenium samples. Paper Table 1 COAD numbers will not match. Use the current GitHub leaderboard (3 April 2026) as the comparison target for COAD and as a secondary target for all tasks.
- Encoder name mapping from the paper's 11 to current names: ResNet50 (IN) → `resnet50`; CTransPath → `ctranspath`; Phikon → `phikon`; Remedis → not available in TRIDENT (weights require a separate Google request; drop and note); UNI → `uni_v1`; CONCH → `conch_v1`; GigaPath → `gigapath`; Virchow → `virchow`; Virchow 2 → `virchow2`; H-Optimus-0 → `hoptimus0`; UNIv1.5 → `uni_v2` (released publicly as UNI2-h; treat as the closest available, and note the substitution).
- Paper Table 1 versus current leaderboard, PCA + ridge averages: H-Optimus-0 0.4146 vs 0.4150; UNI 0.3862 vs 0.3873; GigaPath 0.3853 vs 0.3875; Virchow 0.3977 vs 0.4061; Virchow2 0.3984 vs 0.4034; CTransPath 0.3447 vs 0.3468; ResNet50 0.326 vs 0.3252; Phikon 0.3656 vs 0.3660; CONCH 0.3709 vs 0.3696. Differences of this size come from the COAD update and library versions. Your acceptance threshold in Stage 3 is relative to both.

### Stage 0. Access and environment (Day 1 to 3; blocked on HuggingFace approvals)

Nicolas is handling access requests in parallel (separate to-do list). You need, in the environment:

1. A HuggingFace token with read access, logged in via `huggingface-cli login` (or `HF_TOKEN` env var) on the node that will download. Store nothing in the repo.
2. Confirmed access to datasets `MahmoodLab/hest` and `MahmoodLab/hest-bench`, and to the gated model repos for the encoders you will run.

Environment:

```
git clone https://github.com/mahmoodlab/HEST.git
cd HEST
conda create -n hest python=3.11 -y
conda activate hest
pip install -e .
pip install -e ".[benchmark]"
conda install -c conda-forge libvips pyvips openslide openslide-python -y   # replaces apt install
```

Record `git rev-parse HEAD` for HEST and the installed version of TRIDENT, torch, timm, scanpy, scikit-learn, and xgboost into `env/versions.txt`. Test GPU visibility inside a short SLURM job (`srun --partition=<gpu> --gres=gpu:1 --pty python -c "import torch; print(torch.cuda.is_available())"`).

Directory layout (adapt the root to the group's project space; do not use `$HOME`):

```
<root>/hest_replication/
  env/                versions.txt, conda export, provenance notes
  code/               git clone of HEST (pinned) + our scripts
  bench_data/         MahmoodLab/hest-bench snapshot
  embeddings/         per-encoder, per-sample HDF5 (from benchmark.py)
  results/faithful/   benchmark.py outputs, one exp_code per head
  results/tailored/   our additional runs
  instrumentation/    joined tables (Stage 4)
  reports/            replication memo, discrepancy log
```

Every directory under `results/` and `instrumentation/` gets a `PROVENANCE.txt` with job ID, commit, date, config hash, and the command line.

Acceptance: `python -c "import hest, trident"` succeeds; GPU test passes; HF login verified with `huggingface-cli whoami`.

### Stage 1. Benchmark data (Day 3 to 4)

Trigger the automatic download by running `benchmark.py` once with `encoders: [resnet50]` and `datasets: [IDC]`, or call `snapshot_download` directly with the same arguments the script uses (`ignore_patterns=['fm_v1/*']` skips legacy weights). Then inspect:

- For each of the nine tasks: number of samples, patch HDF5 shape (expect `n_spots × 224 × 224 × 3`), AnnData `.X` dtype and whether values are raw integer counts (they should be), number of genes in the task gene list (expect 50), and the split CSVs (expect `k` train/test pairs, `k` = number of patients; ccRCC has 6 splits per STFlow's Table 7, not 24, so confirm what `hest-bench` ships).
- Verify barcodes in each patch HDF5 match `adata.obs_names` exactly.

Write `bench_data/INVENTORY.md` with these counts. Acceptance: all nine tasks present, counts are integers, barcodes match.

### Stage 2. Faithful runs (Day 4 to 10; GPU)

Run `benchmark.py --config <our copy of bench_config.yaml>` with:

- `datasets`: all nine.
- `encoders`: the ten available from the paper's list (`resnet50, ctranspath, phikon, uni_v1, conch_v1, gigapath, virchow, virchow2, hoptimus0, uni_v2`). Add `hoptimus1` and `conch_v15` if access is granted, since they head the current leaderboard.
- `dimreduce: PCA`, `latent_dim: 256`, `method: ridge`, `normalize: True`, default seed.

Embedding extraction is the only heavy step. One SLURM job per encoder. ViT-giant models (GigaPath, H-Optimus, UNI2-h) need an 80 GB A100 at batch 128 or a reduced batch size on smaller cards. Embeddings are cached per sample, so re-running heads is CPU-only afterwards.

Then rerun with `dimreduce` off and `method: ridge` (paper Table A13) and with `method: xgboost` (Table A14; check the trainer's XGBoost parameters against the paper's: 100 estimators, learning rate 0.1, max depth 3, subsample 0.8).

Use distinct `exp_code` values (`faithful_pca_ridge`, `faithful_ridge`, `faithful_xgb`).

Acceptance: `dataset_results.csv` exists with all encoders × tasks filled; no NaN; per-split `inference_dump.pkl` present.

### Stage 3. Verification (Day 10 to 12)

Build `reports/discrepancy_table.csv` with one row per encoder × task × head: paper value, current GitHub leaderboard value (PCA + ridge only), our value, absolute differences.

Thresholds: a task-level difference above 0.03 from the current leaderboard, or above 0.05 from the paper on non-COAD tasks, must be investigated before proceeding (candidate causes: wrong normalization flag, wrong `latent_dim`, `fit_intercept`, seed, a different `hest-bench` version, or a transform mismatch in TRIDENT). COAD is expected to differ from the paper.

Reproduce Figure 2a (average Pearson against parameter count, log scale) from Table A12 counts and confirm the fitted correlation is near $R = 0.81$ for the paper's encoder set.

Deliverable: `reports/replication_memo.md` with the discrepancy table, a short explanation of each discrepancy, and the environment record. Send this to the oversight chat before starting Stage 4.

### Stage 4. Instrumentation (Day 12 to 24; mostly CPU)

These runs turn the replication into the project's motivation section. All go under `results/tailored/` and `instrumentation/`.

**4a. Joined prediction table.** For each task × encoder × split, unpack `inference_dump.pkl`, reconstruct row identity (sample ID and barcode) from the test split CSV order and the embedding HDF5 barcodes, and write one long table: `task, encoder, split, sample_id, barcode, gene, y_true_log1p, y_pred, y_raw_count`. Join spot metadata from the AnnData (`array_row`, `array_col`, pixel coordinates) and sample metadata from HEST's metadata CSV (patient, cohort source such as TENX/MEND/NCBI/ZEN/INT, technology, organ, oncotree code, tissue preparation, species). Save as Parquet. This table is the input to Topic A's conformal calibration and Topic B's rectifier.

**4b. Split comparison.** For the top three encoders by Pearson, rerun PCA + ridge under three split designs on every task where feasible: (i) random spot-level split ignoring patient (deliberately leaky; five random repeats), (ii) the shipped patient split, (iii) leave-cohort-source-out where a task contains more than one source (IDC has TENX and NCBI; also run across-task, training on all Xenium tasks and testing on a held-out Xenium task). Report Pearson under each. The (i) minus (ii) gap is leakage; the (ii) minus (iii) gap is site shift. Produce one figure.

**4c. Count diagnostics.** For each task's 50 genes, from raw counts: zero fraction, mean, variance, variance-to-mean ratio, and per-gene maximum-likelihood fits of Poisson, NB, and ZINB with AIC. Tabulate how often ZINB is preferred over NB. One figure of zero fraction and dispersion by task and technology.

**4d. Site-predictability probe.** For each encoder, train a logistic-regression probe (with the same PCA-256 preprocessing) to predict cohort source and technology from embeddings; evaluate with sample-level cross-validation so no slide appears in both train and test. Report accuracy against a chance baseline. This replicates GLMP Table 2 on HEST and provides Topic A's density-ratio estimator.

**4e. Morphology features.** Download the CellViT segmentation for the benchmark samples only (from `MahmoodLab/hest`, `cellvit_seg/` pattern filtered by sample ID; these are zipped GeoJSON). For each spot, compute nuclear count, mean and median nuclear area, and fraction of nuclei in each of the five CellViT classes within the 112 µm patch. Join to the table from 4a. As a correctness check, recompute HEST Figure 3e (nuclear area versus GATA3 on the IDC Xenium sample) and confirm $r \approx 0.47$; a large deviation indicates a coordinate or scaling error, which must be resolved before this feature is used.

**4f. Held-out-gene sanity.** For one task, hold out 10 of the 50 genes from the ridge fit and confirm the remaining 40 give a comparable average; this guards against any per-gene leakage in the HVG selection step.

Acceptance for Stage 4: Parquet table loads with expected row count (sum over tasks of test spots × 50 genes × encoders); Figure 3e check within 0.05 of 0.47; split-comparison figure produced.

### Stage 5 (optional, only if Stages 0 to 4 are complete). One stronger baseline

Run STFlow from its public repository (github.com/Graph-and-Geometric-Learning/STFlow) with UNI features on the benchmark to confirm its reported 0.415 average. Save its predictions in the same joined-table format. This gives Topic B a spatial-context predictor and tests whether the calibration story changes.

### 6.2 Deliverables at end of replication

1. `reports/replication_memo.md` with discrepancy table and environment record.
2. `instrumentation/predictions.parquet` (joined predictions, metadata, morphology).
3. Three figures: split-comparison gap, count diagnostics, site-predictability by encoder.
4. `reports/motivation_draft.md`: one page written from the three figures, in the form of a paper introduction paragraph for Topic A.

### 6.3 Time and compute budget

Embedding extraction: roughly 100k benchmark patches × 10 to 12 encoders; a few GPU-hours each on an A100, more for ViT-giant models. Heads and diagnostics are CPU, minutes each. Six weeks total is realistic if approvals arrive in the first week.

---

## 7. Pitfalls and gotchas

- The tutorial notebook sets `LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libffi.so.7` before running `benchmark.py`. That is a workaround for a specific machine. On Longleaf, try without it first; if you hit a libffi symbol error, resolve it inside conda (`conda install libffi`) rather than by pointing at a system path.
- `normalize_adata` is log1p only. Do not add total-count normalization to the faithful run. For Topic A's NB head you will use raw counts, which are available in the AnnData `.X`.
- `Ridge(fit_intercept=False)` with standardized-then-PCA features. Keep as is for faithful runs.
- The shipped split files define the folds. Do not regenerate them. For Stage 4b, create new split CSVs in a separate directory and point the config there.
- Gated models: TRIDENT loads weights from HuggingFace at first use. If a job fails with a 401 or 403, the token is missing on that node or access has not been granted for that repo. Do not retry in a loop.
- `hest-bench` may be gated like `hest`; accept the terms on its page.
- Remedis is not reproducible here; note it as dropped.
- If `sinfo` shows GPU partitions with time limits shorter than an extraction job needs, chunk by sample (the script caches per-sample embeddings, so a restart resumes).
- Check HEST issue tracker if a TRIDENT encoder fails to build; the transforms for some encoders changed between TRIDENT versions.
- Do not download the full `MahmoodLab/hest` archive. Only the CellViT segmentation for benchmark samples (Stage 4e) comes from it.

---

## 8. Decision boundaries

You may decide alone: SLURM parameters, batch sizes, directory names, which encoder to run first, how to chunk jobs, which conda packages to pin.

Report and wait before proceeding: any Stage 3 discrepancy above threshold; any deviation from the faithful protocol; dropping an encoder or task; any storage or quota problem that would require deleting data; any change to the shipped splits.

Escalate to Nicolas for PI or David input: anything touching the scientific framing in Sections 4 and 5; requests to run models or data not listed here; anything requiring new data access agreements.

---

## 9. Reporting format

After each stage, send a report with these headings, in this order:

1. Stage and status (complete / blocked / failed, with the blocking item).
2. What was run (commands, config hash, job IDs).
3. What was checked and the result of each acceptance check, with the actual numbers.
4. Discrepancies and open questions.
5. What was not checked.
6. Proposed next step.

Keep it concise. Numbers only from actual output. Attach paths, not pasted tables, for anything over 20 rows.

---

## 10. References

- Jaume et al. HEST-1k. NeurIPS 2024. arXiv:2406.16192. Code and leaderboard: github.com/mahmoodlab/HEST. Data: huggingface.co/datasets/MahmoodLab/hest and MahmoodLab/hest-bench.
- Huang et al. STFlow. ICML 2025. github.com/Graph-and-Geometric-Learning/STFlow.
- Zhang, Wu, ..., Zhu, Wu, D. Zhang. GLMP. arXiv:2606.28697.
- Kömen et al. Do histopathological foundation models eliminate batch effects? arXiv:2411.05489. de Jong et al. arXiv:2501.18055.
- Gindra et al. HESCAPE. arXiv:2508.01490.
- Chen and Zou. STImage-1K4M. NeurIPS 2024. arXiv:2406.06393.
- Testa, Lei, Roeder. TIDEST. bioRxiv June 2026 (PMC13320745).
- Boyeau, Bates, Jordan, Yosef. CSDE. bioRxiv 2026.01.15.699786.
- Angelopoulos, Bates, Fannjiang, Jordan, Zrnic. Prediction-powered inference. Science 382:669, 2023. PPI++: arXiv:2311.01453. Zrnic and Candès, cross-PPI, PNAS 2024.
- Wang, McCormick, Leek. Post-prediction inference. PNAS 117:30266, 2020. Miao et al. POP-Inf. JMLR 26:179, 2025.
- Sun et al. TISSUE. Nature Methods 21:444, 2024.
- Tibshirani, Barber, Candès, Ramdas. Conformal prediction under covariate shift. NeurIPS 2019. Barber et al. Conformal prediction beyond exchangeability. Annals of Statistics 2023.
- Chernozhukov et al. Double/debiased machine learning. Econometrics Journal 2018.
- DenAdel et al. No scaling laws for single-cell foundation models. Nature Methods 23:1447, 2026.
