> **Closed record, dated 2026-09-16.** This plan is not maintained; numbers in it may have been superseded by later execution and results.

# Round 2 execution plan: from replication to project motivation

Prepared 16 September 2026 for the Claude Science session that produced `NicWYZ/HEST-1k-replication` (commit `eb670fa`). Companion document: the review of that repository dated the same day. Read the review first; this plan implements its Sections 6 and 7 and adds the specifications needed to run them without guessing.

Everything in this round runs on cached embeddings, the joined prediction tables, the metadata table and the morphology parquets already on Longleaf under `/work/users/w/e/weiyang/hest_replication`. No GPU time is required. Nothing in this round touches the faithful results.

---

## 0. Ground rules carried over

- Verify each stage's output against an expected value before moving on. Silent failure is still the main risk.
- Every new output directory gets `PROVENANCE.txt` with job ID, commit, date, config hash and command line.
- Report-and-wait at the end of stages R1, R3 and R5. The other stages report on completion but do not block.
- Before any term in a decomposition or any probe is given a name, list every variable that differs between its arms. This is the procedural fix for the labelling errors identified in the review (Sections 5.3 to 5.5).
- Numbers in reports come from files, with the file path. Dispersion accompanies every mean.

---

## 1. What exists and is reused

| asset | location | used by |
|---|---|---|
| per-encoder, per-sample embeddings with barcodes and coords | `embeddings/<task>/<encoder>/<sid>.h5` | R1, R2, R3, R4 |
| benchmark AnnData with raw counts | `bench_data/<task>/adata/<sid>.h5ad` | R1, R2, R6 |
| shipped folds | `bench_data/<task>/splits/` | R1, R2, R3 |
| sample metadata incl. patient and pixel size | `results/tailored/integrity/sample_metadata.csv` | all |
| patch geometry per sample | `results/tailored/morphology/patch_scale_sources.csv` | R0, R4 |
| joined prediction tables (130M rows) | `instrumentation/` parquets | R6, R7 |
| per-spot morphology parquets | `instrumentation/` | R4, R6 |
| split decomposition v3 script | `code/scripts/split_decomposition.py` | R3 (extend) |
| probe scripts | `code/scripts/site_probe.py`, `spatial_block_probe.py` | R4 (extend) |

Two conventions for this round. New scripts go in `code/scripts/` with a `round2_` prefix so provenance is obvious. New results go under `results/round2/<stage>/` rather than into the existing `results/tailored/` tree, so the repository state at `eb670fa` remains an intact record of round 1.

---

## 2. Stage R0. Housekeeping and relabelling (half a day)

Edits, no computation.

1. README: remove "Private repository"; change "99 encoder-task cells" to 108; add a "Scan resolution" subsection under known limitations reproducing the table in review Section 5.3.
2. Add a column `pixel_size_um` to every joined prediction parquet and to `sample_metadata.csv` if not already present under that name (it is present as `pixel_size_um_estimated`; standardise the name and keep both). Add a derived column `resolution_group` with bins {≤0.15, 0.15 to 0.23, 0.23 to 0.30, 0.30 to 0.40, 0.40 to 0.50, >0.50} µm/px. These bins separate the observed clusters (0.137, 0.2125, 0.25 to 0.274, 0.34 to 0.36, 0.45 to 0.46, 0.57 to 0.69).
3. In the stage report and any table headers: rename "within-patient Pearson" to "within-slide Pearson" wherever the metric is the per-slide computation in `split_decomposition.py`.
4. In the stage report: move the technology and cohort-source probes to an appendix; mark the IDC institution probe as inconclusive; replace the "institution shift 0.0419" row with the four per-slide gaps and the relabel from review Section 5.4.

Acceptance: a diff of the report showing each edit; `sample_metadata.csv` has the two new columns and every sample has a non-null resolution group.

---

## 3. Stage R1. Intercept refit (one day; report-and-wait)

**Why.** The benchmark head has no intercept and its predictions are offset from the target mean by construction. Pearson hides this; every Topic A quantity does not. Review Section 5.6.

**Script.** `round2_head_intercept.py <encoder>`. For every task and every shipped fold, fit three heads on identical PCA-256 features from the identical pipeline (`StandardScaler` then `PCA(256, random_state=1)` fit on train only):

- `nointercept`: `Ridge(alpha=100/(256×50), fit_intercept=False, solver='lsqr', max_iter=1000)`, the faithful head, as a control.
- `intercept`: same with `fit_intercept=True`.
- `ycentered`: `fit_intercept=False` on $y - \bar{y}_{\text{train}}$ per gene, then add $\bar{y}_{\text{train}}$ back to predictions.

For each head save per fold, per gene: Pearson on the test slide(s) computed the faithful way (pooled over the test fold, matching Table 1), $R^2$, MSE, mean of predictions, mean of targets. Save the full prediction arrays for the `intercept` head into a new prediction parquet per task, same schema as round 1 plus a `head` column, so it can be joined to round 1 rows on (task, encoder, fold, sample, barcode, gene).

Run for all 12 encoders. It is head fitting only and takes minutes per encoder.

**Acceptance.**

- Pearson difference between `nointercept` and `intercept` per (task, fold, gene) has max absolute value below $10^{-6}$. If it does not, the pipeline differs from the faithful one; stop and find out why.
- `intercept` and `ycentered` predictions agree to solver tolerance ($\max|\Delta| < 10^{-4}$).
- Median per-gene $R^2$ for the `intercept` head is positive in the large majority of folds, and mean prediction equals mean target on the training fold to within $10^{-6}$.
- Report the fold-median $R^2$ for `nointercept` and `intercept` side by side, for `hoptimus0` and `resnet50`, all tasks.

**Deliverable.** `results/round2/R1_intercept/head_intercept_summary.csv` plus the new parquets. One paragraph stating that the faithful protocol's Pearson is unchanged and its $R^2$ was negative because of the missing intercept.

---

## 4. Stage R2. Within-fold gene selection (one to two days)

**Why.** The 50 target genes were selected on all spots including the test fold. The size of that leakage is unknown. Review Section 5.9.

**Script.** `round2_fold_hvg.py <encoder>`. For each task and shipped fold:

1. Reimplement HEST's `get_k_genes` exactly, but on training samples only: for each *training* sample, keep genes detected in at least $\lceil 0.1 \, n_i \rceil$ spots; intersect across training samples; drop names containing `BLANK` or `Control`; pool training spots' raw counts; `sc.pp.log1p`; `sc.pp.highly_variable_genes(n_top_genes=50)` with default flavour; take the 50 flagged genes in `var_names` order.
2. Verify the reimplementation first: running it on *all* samples of a task must reproduce the shipped `var_50genes.json` exactly (set equality and order). If it does not, the reimplementation is wrong; do not proceed.
3. Fit the `intercept` head on the fold with the fold-selected genes and evaluate on the test slide(s) with those genes. Fit again with the shipped genes on the same fold. Both use identical features.
4. Record per fold: shipped-gene Pearson (matches R1), fold-gene Pearson, the number of genes in common between the two lists, and the mean within-slide Pearson of the genes that are in the shipped list but not the fold list, if any.

Run for `hoptimus0`, `uni_v2`, `virchow`, `resnet50`.

**Acceptance.** Step 2 passes on all ten tasks. The paired difference (shipped minus fold-selected) is reported per task with its dispersion across folds and encoders, and the sign consistency count.

**Deliverable.** `results/round2/R2_fold_hvg/fold_hvg.csv` and one paragraph. Whatever the number is, it replaces the disclaimer in Section 5 item 1 of the round 1 report.

---

## 5. Stage R3. Split decomposition v4 (three to four days; report-and-wait)

**Why.** The v3 terms are correct as computed but mislabelled and pooled across tasks with different structure. Review Section 5.2.

**Script.** `round2_split_v4.py <encoder>`, extending v3. Keep the within-slide metric and the training-size matching exactly as in v3. Changes:

**Designs.** Five plus one optional, in a nested chain:

| design | same slide in train | same patient in train | adjacency broken | n_train |
|---|---|---|---|---|
| `random` | yes | yes | no | matched to shipped fold |
| `blocked` | yes | yes | partly (block edges) | matched |
| `blocked_buffered` | yes | yes | yes | see note |
| `slide_out` | no | yes | yes | see note |
| `patient` (shipped) | no | no | yes | shipped |

`blocked_buffered`: after choosing test blocks as in v3, remove from training every spot within a buffer distance of any test spot on the same slide. Buffer = 2.5 spot pitches, where pitch is read per sample from `spot_pitch_px` in `fig3e_gate.csv` or recomputed from coordinates (Visium: 100 µm; Xenium pseudo-spots: 55 µm, no gap). Record the buffered training size. To keep `n_train` matched to the other arms, subsample the *other* arms' training sets down to the buffered size in a separate matched comparison, and report both.

`slide_out`: only for tasks where some patient has more than one slide (PRAD, COAD, READ, LYMPH_IDC). For each slide $s$ of patient $p$: test on $s$; train on every other slide, including the other slides of $p$. This is "slide unseen, patient seen." Match `n_train` to the patient design by subsampling.

**Grid sweep.** Run `blocked` and `blocked_buffered` at grid sizes 4, 6 and 10. Report the adjacency term at each.

**Per-gene storage.** `score()` must now save the per-gene within-slide Pearson vector for every arm, not just its mean. Write one parquet per encoder with columns (task, design, fold, repeat, grid, slide, gene, pearson). This is what R7 reads.

**Resolution stratification.** For every row, join `resolution_group` of the test slide and, for `slide_out` and `patient`, whether the training set contains any slide in the same resolution group. In PRAD the patient design never does; the `slide_out` design always does. Report the PRAD patient term separately as "patient and resolution both novel."

**Terms to report per task**, all in within-slide Pearson with fold and repeat dispersion:

- adjacency: `random` − `blocked_buffered`
- block-edge residual: `blocked` − `blocked_buffered` (diagnostic; should be small and positive)
- same-slide identity: `blocked_buffered` − `slide_out` (multi-slide tasks) or `blocked_buffered` − `patient` (single-slide tasks, where the two coincide)
- same-patient-other-slide: `slide_out` − `patient` (multi-slide tasks only)

Do not report a cross-task pooled term for anything that contains the same-patient component. A pooled adjacency term across tasks is fine.

**Acceptance.**

- On the `random`, `blocked` and `patient` designs at grid 6, the new script reproduces the v3 per-task means to within $10^{-3}$. This confirms nothing else moved.
- `blocked_buffered` at grid 6 has a larger median nearest-training-spot distance than `blocked` (report the ratio).
- COAD's same-patient-other-slide term is large and its same-slide term is not (this is the prediction from the review; if it fails, the arm construction is wrong).
- Every reported term has a fold count and a standard deviation next to it.

**Deliverable.** `results/round2/R3_splits/terms_per_task.csv`, the per-gene parquet, and a staircase figure per task with the metric held fixed. One paragraph per term stating what varies between its arms.

---

## 6. Stage R4. Probes v2 (two days)

**Why.** Round 1 showed slides are separable in embedding space but could not say whether the signal is technical, biological or resolution. Review Sections 5.3 and 5.5.

**Scripts.** `round2_probe_within_patient.py <encoder>` and `round2_probe_resolution.py <encoder>`. Same probe machinery as round 1 (scaler, PCA-256 fit on train, logistic regression, balanced accuracy, 800 spots per slide subsample with the same seed).

**Probe 1: slide identity within one patient at one resolution.** PRAD patient 2, fifteen slides, pixel sizes 0.341 to 0.349. Target: slide ID. Evaluation: spatial block CV within slide (test blocks held out, as in round 1's `spatial_block_probe.py`), plus the random within-slide split as the upper bound. Chance is 1/15. Compare to the across-patient slide probe on PRAD from round 1. Interpretation rule, fixed before running: if blocked accuracy exceeds 0.8, slide signatures are technical in origin (section, stain, scanner) since biology and resolution are nearly constant; if it is near chance, round 1's 0.98 was mostly biology and resolution.

**Probe 2: resolution within one patient.** PRAD patient 1, eight slides in three resolution groups (five at 0.573, two at 0.688, one at 0.172). Target: resolution group. Evaluation: leave-one-slide-out, so the held-out slide's resolution group is always present in training from other slides (the 0.172 slide cannot be evaluated this way; report it as excluded). Chance is 1/3 balanced. If accuracy is high, resolution is decodable from embeddings independently of patient.

**Probe 3: composition-adjusted slide probe.** For the round 1 slide probe on IDC, PAAD, LUNG and SKCM (single-slide patients, Xenium), regress the PCA-256 features on per-spot morphology covariates (nuclear count, mean nuclear area, the five CellViT class fractions) fit on training spots, and run the probe on residuals. Report accuracy before and after adjustment. A large drop means composition explains the separability; no drop means it does not.

**Probe 4 (relabel, no new compute).** The round 1 IDC "institution" probe is reported as "TENX versus NCBI: same generating lab, different scan resolution; inconclusive at four slides."

**Acceptance.** Each probe reports fold count, chance, balanced accuracy with dispersion, and the interpretation rule stated before the run. Probe 1 and Probe 2 each run for `hoptimus0`, `uni_v2`, `resnet50` at minimum.

**Deliverable.** `results/round2/R4_probes/*.csv` and a one-figure summary.

---

## 7. Stage R5. IDC provenance check (half a day; report-and-wait)

**Why.** If any two of TENX95, TENX99, NCBI783, NCBI785 are serial sections of one FFPE block, the IDC task's own folds contain patient leakage and its Pearson of 0.59 is inflated. Review Section 5.4.

**Task.** This is reading, not computation. Establish, with sources quoted:

1. The 10x dataset pages for "Xenium FFPE Human Breast with Pre-designed Panel" and "Xenium FFPE Human Breast using the Entire Sample Area": tissue source, block or donor description, release date.
2. Janesick et al. 2023, methods and data availability: how many breast cancer blocks were profiled with Xenium, and whether the 10x demo data are the same sections.
3. HEST's metadata `subseries` and `patient` fields for the four samples (already in `sample_metadata.csv`) and, if available, HEST's own provenance notes for those IDs.

Output a table: sample ID, source page, block or donor identity as best determinable, confidence, and a one-line conclusion per pair. If the conclusion is "same block" for any pair, that is a finding about the public benchmark and must be reported to the oversight chat before the IDC task is used in any headline.

---

## 8. Stage R6. Topic B motivation: slide-level estimands (two days)

**Why.** Figure 3e reproduced on one slide and vanished on three others. The estimand is slide-specific, which is the case for cluster-level inference. Review Section 5.8.

**Script.** `round2_theta_by_slide.py`. Inputs: the per-spot morphology parquet (mean neoplastic nuclear area, neoplastic nuclear count, class fractions per spot) and raw counts from the AnnData for the 50 target genes.

For each task, each of its 50 genes, and each slide with at least 500 spots that have at least one neoplastic nucleus:

- $\hat r_{s,g}$: Pearson between mean neoplastic nuclear area and $\log(1+y_g)$ over spots of slide $s$.
- Within-slide sampling variance: spot bootstrap, 200 resamples, standard error $\hat\sigma_{s,g}$.
- Also the raw-count version, since round 1 found raw matches the paper's figure better.

Then per (task, gene): the between-slide variance estimate by method of moments,

$$\hat\tau^2_g = \max\left(0,\; \operatorname{Var}_s(\hat r_{s,g}) - \frac{1}{S}\sum_s \hat\sigma^2_{s,g}\right)$$

and the ratio $\hat\tau^2_g / \overline{\hat\sigma^2_{s,g}}$. A ratio well above 1 means slide heterogeneity dominates spot-level noise, which is the Topic B premise.

Add a second estimand for tasks where it is defined: $\theta_2$, the difference in mean $\log(1+y_g)$ between spots with neoplastic fraction above 0.7 and below 0.3, per slide, with the same bootstrap and variance components.

**Nuclear area by resolution.** Separately, tabulate the distribution of neoplastic nuclear area (median, IQR) per slide, joined to pixel size. If area shifts systematically with resolution across slides of the same task, CellViT's segmentation is resolution-dependent and the morphology covariates need a correction before use in Topic B. Report the correlation between slide-level median area and pixel size within each task.

**Acceptance.** For IDC and GATA3, $\hat r$ for NCBI785 reproduces round 1's 0.458 to within $10^{-3}$. The variance-components table exists for every task with at least three qualifying slides.

**Deliverable.** `results/round2/R6_theta/theta_by_slide.parquet`, `variance_components.csv`, and one figure: per-slide $\hat r$ with bootstrap intervals for the top five genes by $\hat\tau^2$ in each of three tasks.

---

## 9. Stage R7. Per-gene leakage (half a day; depends on R3)

**Script.** `round2_gene_leakage.py`. From the R3 per-gene parquet, compute per (task, gene) the mean over folds, repeats and encoders of `random` − `patient` and of `blocked_buffered` − `patient`. Rank genes within task. Report whether leakage is concentrated (top 10 genes carry more than half of the task's total) or diffuse. Join to the count diagnostics (mean, zero fraction, Fano) and to $\hat\tau^2_g$ from R6, and report Spearman correlations. This is the first look at whether the genes that leak are the genes with the most slide-level heterogeneity.

**Deliverable.** `results/round2/R7_gene_leakage/gene_leakage.csv` and one paragraph.

---

## 10. Stage R8. Optional, only after R1 to R7

- `hoptimus1` on `raw_ridge` and `raw_xgb`. Head fitting on cached embeddings. Falsification test of D2 (width-ranked Table A13): it should rank poorly on `raw_ridge`.
- STFlow remains deferred.

---

## 11. Sequence and time

| stage | depends on | days | blocks |
|---|---|---|---|
| R0 | none | 0.5 | nothing |
| R1 | none | 1 | Topic A |
| R2 | R1 (intercept head) | 1 to 2 | nothing |
| R3 | none | 3 to 4 | R7 |
| R4 | R0 (resolution groups) | 2 | nothing |
| R5 | none | 0.5 | use of IDC as a headline |
| R6 | none | 2 | Topic B |
| R7 | R3 | 0.5 | nothing |

R1, R3, R4 and R6 can run in parallel. Total about two weeks of wall time with the report-and-wait pauses.

---

## 12. Decision boundaries

You may decide alone: script structure, subsampling seeds, buffer distance within the 2 to 3 pitch range, block grid sizes beyond the three listed, bootstrap counts, which additional encoders to include.

Report and wait: any R1 acceptance failure; any R2 step-2 failure; any change to the arm definitions in R3; any conclusion in R5 that two IDC slides share a block; any case where a per-task term in R3 changes sign from v3.

Escalate to Nicolas: anything requiring new data (full HEST-1k samples beyond the benchmark), and any finding that would be reported to the HEST authors as a benchmark issue (the resolution alignment in PRAD, SKCM, PAAD; a same-block result in R5; the size of the gene-selection leakage if it exceeds 0.02).

---

## 13. Reporting format

After each stage, in this order:

1. Stage and status.
2. What was run: scripts, commits, job IDs.
3. Acceptance checks with the actual numbers.
4. For every term or probe: the list of variables that differ between its arms, written out.
5. Discrepancies and open questions.
6. What was not checked.
7. Proposed next step.

Numbers only from files, with the path. Dispersion next to every mean. Attach paths, not tables, for anything over 20 rows.
