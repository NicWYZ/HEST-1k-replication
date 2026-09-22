> **Active instruction document for round 3, dated 22 September 2026.** This is the instruction this round executes against. Its transcription into the execution session's operating plan is `docs/round3_execution_plan.md`. Not bannered as a closed record, because it is not closed.

# Handoff to the Claude Science session: round 3 of the HEST-1k project

22 September 2026. Prepared by the oversight chat for the Claude Science session that will execute round 3 on `NicWYZ/HEST-1k-replication`, starting from tag `round2-docs-clean` (commit `4da6b86`). The companion document `round3_oversight_handoff.md` is context rather than instruction. Read this document fully, then transcribe § 6 into your operating plan before running anything.

---

## 0. How to use this document, and your role

You are the execution agent. A separate chat session (the oversight chat) reviews your reports, makes scope decisions and writes decision memos, which Nicolas hands to you in full. Nicolas Weiyang Zhang (Longleaf ONYEN `weiyang`, Slurm account `rc_htzhu_pi`) is the student whose project this is; he reads every command before it runs and will ask why.

Your responsibilities, as Nicolas stated them, are to run the planned analyses; SSH into Longleaf and submit Slurm jobs; extract and analyse results; debug and iterate; generate figures; write stage reports in the format of § 8; transcribe each instruction document into your operating plan before starting work on it; commit, push and maintain the GitHub repository, keeping only the most up-to-date results in it, moving anything superseded into a `superseded/` folder, and keeping every working document under `docs/`; and everything else you did for the past two rounds.

Sections 1 to 4 are context. Section 5 is what exists and what you build on. Section 6 is the plan. Section 7 is repository practice. Section 8 is the reporting format. Section 9 sets what you decide alone and what you escalate.

Working principles carried over from the two previous rounds, all of which earned their place by catching something:

- Silent failure is the main risk. Verify each stage's output against an expected value before moving on.
- Never assert a number you have not read back from a file. Cite the path.
- Before naming a term or a probe, list in writing every variable that differs between its arms.
- Audit a grouping variable against a source outside the dataset before grouping by it. That is done for donors (`donor_id`); use it, not `patient`.
- Write predictions down before running, and report them beside the outcomes.
- Every output directory gets `PROVENANCE.txt`. Every parquet is written with an explicit schema. Summaries are written before bulk tables. Seeds come from `zlib.crc32`, never `hash()`.
- In reports, quote numbers at the precision the comparison needs and say the relative scale (1.6 times, an order of magnitude smaller). Full precision stays in the files and in computations. Do not fill prose with four-decimal values.
- Do not reconstruct or revise a past working document that has served its purpose. If a memo was not saved, it is listed as absent, not rewritten.
- Put a time cap on anything that is not analysis. The last instruction had no cap and cost a day on the claim checker. Round 3's caps are in § 7.
- `docs/WAYS_OF_WORKING.md` is the accumulated procedure. Re-read it before the first job.

---

## 1. Project context

Nicolas is a first-year biostatistics PhD student in Dr. Hongtu Zhu's group at UNC, supervised for his GRA by Dr. Daiwei (David) Zhang (iStar, GLMP). The advisors set spatial transcriptomics as the year's focus, methodological rather than applied, aiming at a submittable paper by spring or summer 2027. The first assignment was to replicate the HEST-1k benchmark. That replication is done (rounds 1 and 2), and its byproducts are the motivation and the inputs for two topics.

**Topic A. Calibrated uncertainty for histology-to-expression prediction under cohort shift.** For each held-out spot and gene, an interval with guaranteed coverage; characterise coverage when the test slide, scan session or donor is new, and repair it.

**Topic B. Valid inference for population quantities using predicted expression.** Confidence intervals for a morphology-expression relationship that are valid regardless of predictor quality, with variance clustered at the donor, validated by masking measured donors.

Round 3 is Topic A's first experiment (stages A0 to A4), Topic B's first result (stages B1 and B2), and the start of the data expansion (stages D0 to D4). The constraints have not changed. Minimal biology; no GPU except for embedding the expansion set; the A and B stages run on the benchmark's ten tasks and the harness is built so that expansion sets plug in as further tasks. Nothing outside the project is contacted; the authors' draft issue in `docs/hest_bench_issue_draft.md` stays unsent.

Two things about the audience. Nicolas presented half of the round-2 deck on 21 September; the second half (the two topics and the three results) and round 3's results will be presented next. The project will expand beyond the benchmark subset in this round (track D, § 6.9 and § 6.10), because 72 samples cannot carry a methodological project; the selection is made by design criteria first, and nothing is downloaded until Nicolas approves the sets and the storage ask.

---

## 2. The benchmark in one paragraph

Ten tasks (Xenium: IDC, PAAD, SKCM, COAD, LUNG; Visium: PRAD, READ, CCRCC, LYMPH_IDC, HCC), 72 samples, 29 shipped patient-stratified folds, 50 target genes per task. Target is $\log(1 + \text{count})$ per spot per gene. The benchmark head is `StandardScaler` then `PCA(256, random_state=seed)` fit on training embeddings, then `Ridge(alpha = 100/(256 × 50), fit_intercept=False, solver='lsqr')`. Scored by Pearson per gene, averaged. Round 2 established that the penalty is inert and the head has no intercept; the Topic A base predictor is the same pipeline with an intercept solved exactly in float64 (`intercept_f64`, R1b).

---

## 3. What rounds 1 and 2 established

Each item names the file that establishes it. These numbers are given at file precision because several serve as acceptance references in § 6, where precision matters. In your reports, state numbers at the precision the comparison needs and give the relative scale.

1. **Faithful replication.** 12 encoders, four heads, 108 encoder-task cells against the live leaderboard with mean absolute difference 0.0002 and 0 of 108 over threshold; ResNet50 and H-Optimus-1 exact. `results/summary/discrepancy_table.csv`, `results_encoder.csv`.
2. **The patient split is wrong on two tasks.** COAD's labels merge three donors (fold trains on one donor, tests on three; gap 0.3172 against 0.0504 to 0.1931 elsewhere). IDC's TENX95/TENX99 are probably one donor (unresolved); holding test slide and training size fixed, the partner section is worth $+0.0652$ within-slide Pearson, 6 of 6 cells, 54% of IDC's gap; READ's same-specimen pairs give $+0.0901$, 12 of 12, counterfactual. `results/round2/R5c_leak/r5c_leak_summary.csv`, `R5b_audit/donor_audit.csv` (58 verified, 9 unverifiable, 5 contradicted), `R3_splits/r3_patient_label_audit.csv`.
3. **Split design outweighs encoder choice.** Random-minus-patient 0.1586 over ten tasks against a 0.0977 encoder spread; decomposed into training size 0.0126, adjacency 0.0327, residual adjacency removed by a 2.5-pitch buffer 0.0115, slide-and-patient identity 0.1018; on multi-slide tasks, novel slide 0.0148 against patient identity 0.1357. Pooled Pearson over a multi-patient test set is inflated by $+0.19$; the within-slide metric is the one used everywhere. `R3_splits/r3_decomposition_terms.csv`, `r3_per_task_terms.csv`, `r3_buffer_grid_sweep.csv`.
4. **A slide-and-session signature in the features, not in the expression.** Within PRAD patient 2 (15 slides, pixel size spread 1.02×), slide identity is decodable at 0.871 to 0.949 (chance 1/15) and session at 0.967 to 0.991; morphology adjustment removes 1.4% within patient against 17 to 27% across patients; within PRAD patient 1 a 20% resolution difference is at chance (0.489 to 0.511); between-session expression variance is 2.6% (28 of 50 genes at or below zero). `R4_probes/r4_probes_v2.csv`, `R6_variance/r6_prad_session_variance.csv`, `R0_resolution/resolution_by_task.csv`.
5. **The head has no intercept; the $R^2$ ladder.** Fold-median $R^2$ is $-0.953$ shipped, $-0.155$ with a training-mean intercept, $+0.030$ with the test fold's own mean (oracle), $+0.100$ with optimal scale, equal to $r^2$. $\rho / r = 1.840$ pooled (2.165 ResNet50 to 1.650 UNI2-h). The float64 intercept head passes the three-head identity to $10^{-13}$ and reproduces round 1's per-task Pearson to a mean of $1.5 \times 10^{-4}$. `R1b_heads/r1b_ladder_pooled.csv`, `r1b_ladder_by_encoder.csv`, `acceptance__*__f64.csv`, `faithful_check__*__f64.csv`.
6. **Table A13 ranks by width.** Spearman(width, score) $-0.950$ raw against $+0.727$ PCA; H-Optimus-1 rank 1 PCA, rank 7 raw; Gram condition number about $3.0 \times 10^{15}$ at raw width. `R8_raw_heads/r8_width_correlations.csv`, `results/tailored/regularization/alpha_sweep.csv`.
7. **Panels and selection.** PAAD's samples share 159 of 919 genes; training-only target selection changes the list by about half (mean 25.2 of 50 shared) and Pearson by a mean of $+0.0048$, up to $+0.0441$. `R2_fold_hvg/r2_panel_heterogeneity.csv`, `r2_leakage_summary.csv`.
8. **Negative binomial, no zero inflation.** NB beats Poisson 478 of 488; ZINB beats NB 28 of 488 with median $\Delta\text{AIC}$ $-2.002$; minimum Fano 1.638. `results/tailored/counts/count_diagnostics.csv`.
9. **Estimand and unit.** $\theta_1$ (nuclear area against GATA3, IDC) is 0.4209 on NCBI785 under the current morphology build (bootstrap 0.377 to 0.472), 0.15, 0.01, $-0.06$ on the other three slides. Between-donor variance fraction of expression 0.393 on CCRCC (24 donors), 0.335 on LYMPH_IDC, pooled 0.376. Per gene within task, split penalty tracks replicate gain ($+0.377$), between-slide variance tracks novel-slide cost ($+0.21$), between-donor variance does not track split penalty ($+0.04$, n.s.). `R6_theta/r6_theta_bootstrap_ci.csv`, `R6_variance/r6_variance_by_task.csv`, `r6_pooled_between_donor.csv`, `R7_pergene/r7_correlations_task_centred.csv`.
10. **Solver noise.** Per-gene Pearson under `lsqr` carries about $10^{-3}$ noise; the faithful head's predictions differ from the exact solution by up to 0.35. Topic A uses the float64 exact head. `R1b_heads/r1b_solver_sensitivity.csv`.

What these mean for round 3, in three lines. The base predictor is the float64 intercept head. The evaluation must run under three fold designs (random spot, shipped patient, audited donor), with COAD flagged `patient_labels_unreliable`, READ flagged `same_specimen_pairs`, IDC run under both label sets, and `donor_id` as the grouping variable. The shift to handle is slide and session novelty with donor novelty on top; the density-ratio estimator is a probe on the embeddings; the variance for Topic B is clustered by donor.

---

## 4. Flags that every round-3 table carries

| flag | applies to | effect |
|---|---|---|
| `patient_labels_unreliable` | COAD | excluded from any patient-level claim under shipped labels; included under `donor_id` (four donors; TENX111 is its own donor) |
| `same_specimen_pairs` | READ | its patient term is a same-specimen term |
| `idc_attribution_unresolved` | IDC | run under shipped labels (4 patients) and audited labels (3 donors, TENX95 and TENX99 merged); report both |
| `resolution_uncertain` | 31 of 72 samples | carried as a column from `sample_metadata.csv` |
| `donor_label_status` | every sample | `verified`, `unverifiable` or `contradicted`, from `donor_audit.csv` |
| `calibration_unit` | every fold in round 3 | `donor`, `slide` or `block`; see § 6.2 |

---

## 5. What exists and what you build on

### 5.1 On Longleaf (`/work/users/w/e/weiyang/hest_replication`; sizes and hashes in `MANIFEST.md`)

| asset | path | notes |
|---|---|---|
| benchmark data (gated) | `bench_data/<task>/` | AnnData with raw counts, patch HDF5, shipped splits, `var_50genes.json` |
| embeddings | `embeddings/<task>/<encoder>/<sample>.h5` | 12 encoders, barcodes and coordinates inside |
| float64 intercept-head predictions | `instrumentation/round2_intercept_f64/<task>/preds__<enc>__f64.parquet` | per spot per gene per shipped fold; the schema is in that directory's provenance and in `docs/round2_R3_stage_report.md`; read one file and confirm before use |
| round-1 joined tables | `instrumentation/<task>/preds.parquet`, `spots.parquet` | spot metadata incl. `array_row`, `array_col`, pixel coordinates |
| morphology, current build | `instrumentation/morphology_v2/` | per-spot nuclear count, mean and median area, five CellViT class fractions, per-sample geometry calibration |
| sample metadata | `results/tailored/integrity/sample_metadata.csv` (in repo) | `patient`, `pixel_size_um`, `resolution_group`, `resolution_uncertain`, `st_technology`, cohort source |
| donor labels | `results/round2/R5b_audit/donor_audit.csv` (in repo) | `donor_id`, `donor_label_status` |
| session labels | PRAD patient 2 sub-clusters MEND139 to MEND146 and MEND147 to MEND153 (`docs/round2_R5_stage_report.md`, `r4_probes_v2.csv`) | the only task with a session contrast inside one donor |
| per-gene split terms | `results/round2/R3_splits/pergene__<enc>.parquet`, `R7_pergene/r7_pergene_decomposition.csv` | per-gene `random − patient`, novel slide, patient identity |

### 5.2 Code you extend

| script | what it has that round 3 needs |
|---|---|
| `code/scripts/round2_split_v4.py` | the five split designs (`random`, `blocked`, `blocked_buffered`, `slide_out`, `patient`), size matching by subsampling, the within-slide metric, buffered blocks at 2.5 pitches, per-gene storage with explicit schema, crc32 seeding |
| `code/scripts/round2_r1b_heads.py` | the float64 Cholesky ridge with intercept, the three-head identity checks, the faithful-check anchor |
| `code/scripts/round2_r4_probes.py` | scaler, PCA-256 fit on train, logistic regression, balanced accuracy, block CV; the density-ratio estimator is this classifier with a different label |
| `code/scripts/round2_r5c_replicate_leak.py` | the equal-size two-pool design; the template for Topic B's masking |
| `code/scripts/round2_r6_theta.py`, `round2_r6_donor_variance.py` | $\theta$ per slide with spot bootstrap; Henderson nested variance components |
| `code/scripts/count_diagnostics.py` | NB and ZINB fits; the convergence guard |
| `code/scripts/verify_numeric_claims.py`, `build_deck_numbers.py`, `build_summary_tables.py` | document and table gates |

### 5.3 Conventions

New scripts go in `code/scripts/` with a `round3_` prefix. New results go under `results/round3/<STAGE>/`, one directory per stage, each with a directory-level `PROVENANCE.txt` and per-encoder provenance files where jobs are per encoder. Stage reports go in `docs/` as `round3_<gate>_stage_report.md`. Nothing under `results/round2/` or `results/faithful/` is modified.

---

## 6. Round 3 plan

### 6.0 Gates and sequencing

Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under § 9, recorded in an "Escalations" section of the next report, and work continues. If a defect invalidates a completed stage's numbers, fix it and rerun inside the interval and say so.

| interval | stages | report |
|---|---|---|
| 1 | S0, A0, A1, D0 | **A1 report, then wait** (D0's proposal is in it) |
| 2 | A2, A3, D1 to D3 | **A3 report, then wait** (A2 and the D status are in it) |
| 3 | A4, B1, B2, D4 | **B2 report, end of round** |

Idle capacity inside an interval may go to housekeeping and to supplements of stages already complete in that interval, never to a stage after the gate. D1 has a second condition besides the gate, Nicolas's approval of the selected sets and the storage ask; it does not start without it.

### 6.1 S0. Housekeeping (half a day, capped at one day)

1. Transcribe § 6 into your operating plan. Flag anything that looks wrong in the A1 report rather than changing it silently.
2. Commit the round-2 documents Nicolas supplies under `docs/decisions/` (`round2_R3_decisions.md`, `round2_R5_decisions.md`, `round2_closeout_decisions.md`, `deck_figures_and_repo_update.md`, `post_deck_repo_instructions.md`, and this document as `round3_execution_handoff.md`). `round2_R1_decisions.md` was not saved; list it in `docs/README.md` as not in the repository and do not reconstruct it. Banner each supplied memo as a closed record; run the sweep over them with the `historical` class.
3. Update `docs/README.md`. It is missing `docs_clean_report.md`, `literature_landscape.md` and `round2_results_synthesis.md`, lists `r5_idc_provenance.md` as absent when it is present, and lists the memos as pending.
4. Check the README headline table shows H-Optimus-1's `raw_ridge` average now that `results_encoder.csv` carries it.
5. Create `results/round3/` and the `round3_` script convention; add a `docs/round3_execution_plan.md` that is your operating-plan transcription.

### 6.2 A0. The conformal harness (one to two days)

**Why.** Every Topic A number comes out of this harness. Design errors here (a calibration set that is not exchangeable with the test set under the design's assumption, a PCA fit that saw calibration spots, an overlap between sets) would produce coverage numbers that mean nothing. So the harness is built and checked before any result is read.

**Script.** `round3_a0_harness.py <encoder> --task-def <file>`, extending `round2_split_v4.py`. For each task, each design and each fold it produces three disjoint spot sets, proper-training $T$, calibration $C$ and test $E$, fits the base predictor on $T$ only, and evaluates conformal intervals on $E$.

**Task definition.** A task is not hard-coded as one of the benchmark's ten. It is a file listing sample ids with `donor_id`, `lab`, `session`, `resolution_group`, the flags of § 4, the fold assignments per design, and the target-gene list with how it was chosen. The ten benchmark tasks are written as such files in S0 (`results/round3/task_defs/<task>.json`), and the expansion sets from track D become further files. Nothing in the harness may assume the benchmark's directory layout beyond what the task file points at.

**Base predictor.** On $T$ only, `StandardScaler`, then `PCA(256, random_state=1)`, then float64 Cholesky ridge with intercept at $\alpha = 100/(256 \times 50)$, exactly the R1b `intercept_f64` head. Predictions $\hat y$ for $C$ and $E$. Nothing is fit on $C$ or $E$ except the conformal quantile on $C$ and, in A3, weights that use features only.

**Designs.** Four, each yielding $(T, C, E)$ per fold. Proper-training sets are size-matched across designs within a fold by subsampling to the smallest, as R3 did; record the sizes.

| design | test $E$ | pool for $T \cup C$ | calibration unit |
|---|---|---|---|
| `random` | a random draw of the shipped fold's test size over all spots of the task, 5 repeats | the rest | spot; $C$ is a random 20% of the pool |
| `patient` | the shipped fold's test slides | the shipped fold's training slides | highest available level (rule below) using HEST `patient` |
| `donor` | leave-one-donor-out by `donor_id` (COAD 4 folds, IDC 3 folds under audited labels plus the shipped 4-fold version) | all other donors | highest available level using `donor_id` |
| `slide_out` | one slide (multi-slide tasks PRAD, COAD, READ, LYMPH_IDC, and IDC under audited labels) | all other slides, including the donor's other slides | slide; record `cal_shares_donor_with_test` |

**Calibration-unit rule.** Within the pool, hold out about 25% of the units at the highest level the pool supports, rounding up to at least one unit. Use the donor if the pool has at least two donors (patients, under `patient`); otherwise slide if it has at least two slides; otherwise buffered spatial blocks within the single slide (grid 6, 2.5-pitch buffer, about 20% of blocks). Record `calibration_unit`, `n_cal_units`, `n_cal_spots`, `cal_shares_session_with_test` (any calibration slide in the test slide's `resolution_group`, and for PRAD patient 2 the same session) and `cal_shares_donor_with_test`. Where the pool has at least three units, draw three calibration sets with crc32 seeds and report the dispersion. This rule is part of the design, because the table's structure, which folds could calibrate at the donor level and which could not, is itself a result.

**Scores and intervals**, per gene, at $\alpha = 0.10$ (also store the $\alpha = 0.20$ quantile; report 0.10).

- `abs`: $s_i = |y_i - \hat y_i|$; interval $\hat y \pm \hat q$, with $\hat q$ the $\lceil (n+1)(1-\alpha) \rceil / n$ empirical quantile of the calibration scores.
- `scaled`: $s_i = |y_i - \hat y_i| / \hat\sigma(x_i)$, with $\hat\sigma$ a ridge regression of $|y - \hat y|$ on the PCA-256 features fit on $T$'s in-sample residuals, floored at $10^{-3}$; interval $\hat y \pm \hat q\, \hat\sigma(x)$.

**Metrics** per (task, design, fold, repeat, encoder, score, gene, test slide) are `coverage` (fraction of test spots covered), `width_mean`, `interval_score` (Winkler score at $\alpha$), `miss_above`, `miss_below`, `n_test`. Aggregation follows the metric convention, per slide, then mean over slides, then over genes, then over folds with the standard deviation across folds.

**Outputs** under `results/round3/A1_coverage/` (A0 writes the harness; A1 runs it at scale) are `a1_calibration_units.csv`; `a1_by_task.csv` (task, design, encoder, score, calibration_unit, n_folds, coverage_mean, coverage_sd, width_mean, width_sd, interval_score_mean, n_train_matched); `a1_by_slide.csv`; `pergene__<enc>.parquet` with an explicit `pa.schema` (fold as string). Summaries before parquets.

**Acceptance checks for A0.**

- H1, anchor to the prior result. With the calibration fraction set to zero on the `patient` design, the harness's per-task Pearson equals R1b's `intercept_f64` per-task Pearson for every encoder-task cell to within $10^{-6}$ (`faithful_check__<enc>__f64.csv` and the R1b intercept summaries). If it does not, the pipeline differs from R1b; find out why before anything else.
- H2, harness correctness. On `random` with the `abs` score, marginal coverage pooled over folds is within 0.02 of 0.90 for every task-encoder cell. If it is not, the conformal implementation is wrong.
- H3, disjointness. Assert per fold that $T$, $C$ and $E$ are disjoint on (sample id, barcode) and that the scaler and PCA were fit on $T$ only.
- H4, engineering. Explicit parquet schema; summaries written first; crc32 seeds; provenance with config hash and `pythonhashseed`; a two-fold, one-task smoke run before any full job.

### 6.3 A1. Marginal coverage across designs (one to two days; gate)

**Why.** This is the first coverage table across designs and the core of Topic A. Its shape is the result, where coverage holds, where it fails, and by how much.

**Run.** The A0 harness on all ten tasks, all 12 encoders, four designs, two scores. Fan out one job per encoder. Size memory from `sacct` on R1b (peak 16.7 GB for head fitting); 24 GB and 4 CPUs is the honest ask, with a generous wall and a harness ceiling set from queue time plus runtime.

**Predictions, written before running.**

1. `random` at nominal for every task and encoder (this is H2).
2. `patient` and `donor` under-cover, worst where the shift is largest, on PRAD and SKCM patient folds (which are session folds) and COAD under shipped labels. COAD improves under `donor`.
3. Coverage at or near nominal under `donor` only in folds where `calibration_unit = donor`; folds calibrated at slide or block level under-cover.
4. `slide_out` sits between `random` and `donor`, and folds where the calibration slide shares the test slide's donor do better than folds where it does not.
5. Under-coverage is larger for weaker encoders in absolute terms, but the ordering across designs is the same for every encoder.
6. IDC under audited labels (three donors) under-covers more than IDC under shipped labels, because the shipped folds leak the partner section.

**Report** the table beside the benchmark's Pearson table (same encoders, same tasks), the calibration-unit table, and predictions against outcomes. Include the "what was not checked" section. Then stop.

### 6.4 A2. Conditional coverage and the anatomy of failure (one day; no gate)

**Why.** Marginal coverage says whether intervals fail; this says where and how. Two questions. Is the failure concentrated (some slides, sessions, genes) or diffuse? And is a failing interval centred wrong (level) or too narrow (scale)? The ladder in round 2 said the remaining $R^2$ deficit after an intercept is a slide-level mean shift ($+0.185$) and a scale error ($+0.070$); this stage asks whether the coverage failure has the same anatomy.

**Script.** `round3_a2_conditional.py`, reading A1's per-gene parquets and per-slide tables plus covariates. No refitting.

**Strata.** Test slide; `resolution_group` and session (PRAD patient 2); `cal_shares_session_with_test`; predicted-value decile within task; gene; neoplastic-fraction tertile of the test spot (from `morphology_v2`); `donor_label_status`.

**Level-versus-scale decomposition** per (test slide, gene) under `patient`, `donor`, `slide_out`:

- miss asymmetry $a = (\text{miss}_{\text{above}} - \text{miss}_{\text{below}}) / (\text{miss}_{\text{above}} + \text{miss}_{\text{below}})$; near $\pm 1$ means the interval is centred wrong;
- standardised slide offset $b_s / s_y$ with $b_s = \bar y_s - \bar{\hat y}_s$ on the test slide (a diagnostic using test labels; label it as such);
- oracle width ratio $w^\star / \hat w$, with $w^\star$ the half-width that would give exactly 90% coverage on the test slide and $\hat w$ the calibrated half-width; above 1 means too narrow;
- regress the coverage shortfall on $|b_s| / s_y$ and $\log(w^\star / \hat w)$ across slides and report the shares.

**Per-gene join.** Spearman, within task, between gene-level coverage shortfall under `donor` and R7's per-gene `random − patient`.

**Predictions.** Shortfall under `donor` is mostly level (asymmetric misses, large $|b_s|$), consistent with the ladder. Gene-level shortfall correlates positively with the per-gene split penalty. Coverage is worse for spots in the predicted-value tails. Session-unsupported folds (PRAD, SKCM) are the worst stratum.

**Outputs.** `results/round3/A2_conditional/a2_by_stratum.csv`, `a2_level_scale.csv`, `a2_pergene_join.csv`, one figure (`fig_a2_anatomy.png`).

### 6.5 A3. Weighted conformal under slide and session shift (two days; gate)

**Why.** Round 2 measured that the features move between slides and sessions while the expression does not. That is the covariate-shift case, and weighted conformal (Tibshirani, Barber, Candès, Ramdas 2019) is the method built for it. It reweights calibration scores by the density ratio $w(z) = p_{\text{test}}(z) / p_{\text{cal}}(z)$. It also has a known failure, no calibration support, which PRAD's and SKCM's patient folds create. This stage tests both.

**Script.** `round3_a3_weighted.py <encoder>`, on the A0 harness, designs `patient`, `donor`, `slide_out`, scores `abs` and `scaled`, three encoders (`hoptimus0`, `uni_v2`, `resnet50`). Run `random` too, as the control where weights should be near 1.

**Weight estimators.**

- W1, embedding classifier. Per fold, logistic regression on the PCA-256 features (the same PCA fit on $T$), class-balanced, L2 with a fixed $C$, trained to separate $C$ (label 0) from $E$ (label 1) using features only. $w(z) = \frac{\hat p(1 \mid z)}{\hat p(0 \mid z)} \cdot \frac{n_C}{n_E}$. Clip at the 99.5th percentile of the calibration weights and record the clipping rate and the classifier's AUC.
- W2, covariate weights. Ratio of test to calibration proportions within cells of (`resolution_group`, session where defined). A test cell absent from calibration has no finite weight; flag `no_support` and fall back to unweighted for that fold, reporting it.
- W3, hierarchical arm, only if the oversight chat's literature search (see the oversight handoff § 3) specifies one in a memo before this interval starts. Otherwise leave a placeholder column.

**Weighted quantile.** For each test point, $\hat q = \inf\{ q : \sum_{i \in C} \tilde w_i \mathbf{1}[s_i \le q] \ge 1 - \alpha \}$ with $\tilde w_i = w(z_i) / (\sum_{j \in C} w(z_j) + w(z_{\text{test}}))$, the test point's own weight in the normaliser. Sort the calibration scores once per fold and use cumulative sums.

**Calibration-support diagnostic.** Effective sample size of the weights per test slide, $n_{\text{eff}} = (\sum_i w_i)^2 / \sum_i w_i^2$ over calibration spots, reported as the median over the slide's test spots.

**Acceptance.** On `random`, weighted coverage equals unweighted within 0.005 and the classifier AUC is near 0.5. Weights are positive and finite after clipping. On a fold whose test session is absent from calibration, $n_{\text{eff}}$ collapses; report the value.

**Predictions.** Reweighting restores coverage towards nominal where $n_{\text{eff}}$ stays high (slide-out on PRAD patient 2; donor folds on CCRCC; IDC's TENX pair) and does not where it collapses (PRAD and SKCM patient folds). Coverage gain is monotone in $n_{\text{eff}}$. W1 beats W2 where the shift is within a covariate cell (slide-level) and the two agree where it is between cells. The scaled score narrows intervals at matched coverage.

**Outputs.** `results/round3/A3_weighted/a3_by_task.csv` (weighting in {none, W1, W2, W3}, coverage, width, interval score, `neff_median`, `clip_rate`, `auc`, `no_support` count), `a3_by_slide.csv`, `fig_a3_coverage_vs_neff.png`.

**Report** A2 and A3 together, predictions against outcomes, and stop.

### 6.6 A4. Adaptive scores and the model-based comparator (two to three days; no gate)

**Why.** Two comparisons the paper needs. First, width at matched coverage across scores, since a wide interval that covers is not useful. Second, whether a model-based predictive distribution (the negative-binomial head, the likelihood round 1 settled) is calibrated across designs, and what conformalising it does. This stage also measures the conditional dispersion the round-1 review asked for.

**Script.** `round3_a4_scores.py <encoder>`, three encoders, all tasks, the A0 designs.

**CQR.** `QuantileRegressor(quantile=q, alpha=0, solver='highs')` on PCA-256 for $q \in \{0.05, 0.95\}$, fit on $T$; conformalised with $s_i = \max(\hat q_{0.05}(x_i) - y_i,\; y_i - \hat q_{0.95}(x_i))$ (Romano, Patterson, Candès 2019). Time-box each task-encoder fit at 20 minutes; if exceeded, subsample $T$ to 20,000 spots and record it.

**Negative-binomial head.** Per gene on raw counts, fit a Poisson GLM with log link on PCA-256 (`PoissonRegressor`, small L2) for $\hat\mu(x)$, then an NB2 dispersion per gene by the moment estimator on $T$'s Pearson residuals, $\hat\alpha_g = \max\!\left(0, \frac{\sum (y - \hat\mu)^2 - \sum \hat\mu}{\sum \hat\mu^2}\right)$. Predictive distribution $\text{NB}(\hat\mu(x), \hat\alpha_g)$. Report the central 90% interval on the count scale mapped to $\log(1+y)$, its coverage, the PIT values $F(y; \hat\mu, \hat\alpha)$ (randomised for discreteness), the log score, and $\hat\alpha_g$ beside the marginal Fano factor from `count_diagnostics.csv`. Do not trust library convergence flags; check the fitted deviance and record failures, as round 1 did.

**Conformalised NB.** Score $s_i = |F(y_i; \hat\mu_i, \hat\alpha) - 0.5|$ on $C$; the calibrated interval is the NB quantile band at $0.5 \pm \hat q$.

**Acceptance.** On `random`, the NB PIT histogram is close to uniform (report the KS statistic) and CQR coverage is at nominal.

**Predictions.** NB intervals under-cover under `donor` in the same pattern as the conformal ones and conformalising restores marginal coverage. CQR and `scaled` are narrower than `abs` at matched coverage, most on Xenium tasks where variance depends strongly on the mean. Conditional dispersion $\hat\alpha_g$ is well below the marginal Fano factor but far from zero.

**Outputs.** `results/round3/A4_scores/a4_scores_by_task.csv` (score in {abs, scaled, cqr, nb, nb_conformal}), `a4_nb_dispersion.csv`, `a4_pit.csv`, `fig_a4_width_at_coverage.png`.

### 6.7 B1. Prediction-powered inference with donor-clustered variance (two days; no gate)

**Why.** Topic B's claim is that inference on predicted expression can be valid if the variance respects the dependence, and that the gain from predictions is real but bounded. Round 2 measured the between-donor variance share (0.39 on CCRCC) and derived the consequence. With $m$ spots per donor and between-donor share $\rho$, the variance of a mean is inflated by $1 + (m-1)\rho$ relative to the i.i.d. formula, and the effective sample size is about $n_{\text{donors}} / \rho$. This stage builds the estimator and the three variances and shows the difference on real data.

**Script.** `round3_b1_ppi.py`. Inputs are predictions from the A1 `donor` design (every spot predicted by a head that never saw its donor, so cross-fitting holds), measured $\log(1+y)$, and `morphology_v2` covariates.

**Estimands**, per task and gene $g$, with $m$ the standardised mean nuclear area of the spot:

- $\theta_3$ (primary): the slope of $\log(1+y_g)$ on $m$ over the population of spots, $\theta_3 = \text{Cov}(m, \log(1+y_g)) / \text{Var}(m)$.
- $\theta_2$: difference in mean $\log(1+y_g)$ between neoplastic-dominant spots (fraction above 0.7) and stromal-dominant spots (below 0.3).
- $\theta_1$ (the motivating example only): the correlation of mean nuclear area with raw GATA3 count on IDC, per slide and pooled.

Two population definitions, both reported. Spot-weighted (the mean over all spots of the task), and donor-weighted (the mean over donors of the donor-level value). The second is the one whose target population is donors.

**Data split.** Labelled set $L$ = a subset of donors with measured expression; unlabelled set $U$ = the remaining donors, for which only $\hat y$ is used.

**Estimators.** The classical estimator on $L$ alone. The prediction-powered estimator in the estimating-equation form (PPI++, Angelopoulos, Duchi, Zrnic 2023), solving

$$\frac{1}{N}\sum_{i \in U} \psi(\hat y_i, m_i; \theta) + \frac{1}{n}\sum_{i \in L}\big[\psi(y_i, m_i; \theta) - \psi(\hat y_i, m_i; \theta)\big] = 0,$$

with the power-tuning parameter $\lambda$ estimated as in PPI++ and reported. For $\theta_3$ and $\theta_2$, $\psi$ is linear in the outcome, so this reduces to the plug-in estimate on $U$ plus the rectifier on $L$.

**Variance estimators**, for both the classical and the PPI estimator:

- (a) spot i.i.d., the default in the PPI papers;
- (b) donor cluster-robust: sum the influence-function contributions within each donor, take the variance across donors with the $G/(G-1)$ correction, separately for the $U$ and $L$ terms (the donor sets are disjoint), and use a $t$ reference with $G - 1$ degrees of freedom;
- (c) donor bootstrap: resample donors with replacement within $U$ and within $L$, 500 draws, percentile interval.

**Tasks and settings.** CCRCC (24 donors) is the powered case; label 6, 8 and 12 donors. LYMPH_IDC (4 donors) label 2. PRAD (2 donors, 23 slides) is the expected failure case with one donor degree of freedom; run it and say so. IDC for $\theta_1$ as illustration. Three encoders (`hoptimus0`, `uni_v2`, `resnet50`) plus a permuted-predictions arm as the deliberately useless predictor.

**Acceptance.** With $U$ empty the PPI estimate equals the classical one exactly. With $\hat y = y$ the PPI estimate equals the full-data value exactly. With one spot per donor, (b) equals (a). The permuted predictor's PPI interval still covers (validity) and is at least as wide as the classical one.

**Outputs.** `results/round3/B1_ppi/b1_estimates.csv` (task, gene, estimand, population, encoder, n_L_donors, n_U_donors, theta_full, theta_classical, theta_pp, lambda, se_iid, se_cluster, se_boot, width ratios), `fig_b1_intervals.png` ($\theta_1$ per IDC slide with spot-level against donor-level intervals; $\theta_3$ on CCRCC by variance estimator).

### 6.8 B2. Semi-synthetic coverage (one to two days; end-of-round report)

**Why.** B1 is one partition. Validity is a statement about repeated sampling, so this stage repeats the partition many times, treating the full-data value as truth, which is the masking design from R5c applied to donors. This is what turns B1 into a claim.

**Script.** `round3_b2_semisynthetic.py`. For each task and $n_L$ in B1's settings, draw 200 random labelled-donor sets with crc32 seeds, compute classical and PPI intervals under the three variance estimators, and record whether each covers the full-data value. Also a slide-masking variant on PRAD (mask whole slides within the two donors) to show the $G = 2$ failure.

**Report** empirical coverage at nominal 0.90, mean width, and the PPI-to-classical width ratio as a function of encoder quality (its Pearson on the task) and $n_L$, for each estimand and population definition.

**Predictions.** Spot i.i.d. intervals cover far below 0.90 for both estimators. Donor cluster-robust intervals cover near 0.90 for $n_L \ge 8$ and below for $n_L = 4$ or 6 unless the $t$ reference is used; the donor bootstrap behaves similarly. The PPI width ratio is below 1 only for the better encoders and approaches 1 as the estimand's between-donor variance share grows, because predictions on unlabelled donors cannot reduce the donor-level variance in the labelled rectifier. The permuted predictor's ratio is at or above 1 everywhere.

**Outputs.** `results/round3/B2_semisynthetic/b2_coverage.csv`, `b2_width_ratio.csv`, `fig_b2_coverage.png`. The end-of-round report covers A4, B1 and B2, plus an "escalations" section and the full predictions-versus-outcomes table for the round.

### 6.9 D0. Inventory of full HEST-1k and the expansion proposal (one day, capped at one day; interval 1)

**Why.** The benchmark subset is 72 samples with at most 24 donors in a task, one lab per task, and 50 genes chosen with test spots. The project needs an institution contrast, donors in the tens to hundreds, and gene lists chosen without test data, none of which the subset has. Full HEST-1k (about 1,200 samples, 153 cohorts, 26 organs, mostly Visium) has them. The whole archive is over 2 TB, almost all of it whole-slide images the pipeline does not need once patches exist, so the plan is a designed subset. Selection comes before download.

**Inputs.** HEST's metadata table already on disk (`HEST_v1_1_0.csv`, read by R5b; check for a newer release on the HuggingFace page and record which version is used), and the HuggingFace file listing of `MahmoodLab/hest` for per-sample sizes of `patches/`, `st/`, `cellvit_seg/` and `metadata/` (listing only; no download).

**Script.** `round3_d0_inventory.py`. Writes `results/round3/D0_inventory/hest_inventory.csv` (one row per sample with organ, species, technology, oncotree, cohort or dataset title, HEST patient label, pixel size, spot count, and bytes per component) and `expansion_candidates.csv` (one row per candidate set with the samples it contains, the counts of samples, HEST-labelled patients, cohorts and labs, and the total bytes).

**Sets to propose**, each with a stated selection rule and its size.

- Institution set. One organ and one technology with at least three distinct labs (cohorts from different generating institutions, not merely different download sources; the IDC lesson in `docs/HEST_replication_review.md` § 5.4 applies) and at least three donors per lab. Human breast on Visium and brain on Visium are the review's candidates; propose whichever the table supports, with alternatives.
- Donor-power set. The organ and technology combination with the most distinct HEST-labelled donors, for Topic B.
- Platform-pair set. Tissues profiled on more than one technology, ideally the same block on Visium and Xenium, for a platform-shift axis.

Record for each set how many samples carry `resolution_uncertain`, how the HEST patient labels look (repeated labels across cohorts, missing labels), and any sample already in the benchmark. Report the storage ask against the current `/work` quota.

**Acceptance.** Every benchmark sample appears in the inventory with the same metadata the benchmark used. The three sets' sizes sum from the listing, not from an estimate. The proposal goes into the A1 report; nothing is downloaded.

### 6.10 D1 to D4. Download, embed, audit, and measure lab shift (intervals 2 and 3)

**D1, download (after Nicolas approves the sets; half a day of wall time plus transfer).** `snapshot_download` on `MahmoodLab/hest` with `allow_patterns` restricted to the approved sample ids under `patches/`, `st/`, `cellvit_seg/` and `metadata/`. No `wsis/`. Target `/work/users/w/e/weiyang/hest_replication/hest_ext/<set>/`, with a `PROVENANCE.txt` naming the HuggingFace revision and the sample list. Check `quota` before and after. Verify every expected file is present and that patch counts match the expression files' spot counts, as Stage 1 did for the benchmark.

**D2, embeddings (GPU; one job per encoder per set).** `hoptimus0`, `uni_v2`, `resnet50` only. Use the benchmark's own extraction path so embeddings are cached per sample under `embeddings_ext/<set>/<encoder>/`, and a killed job resumes. Check `sinfo` for the current GPU partitions; the queue was saturated in round 1, so submit early in interval 2 and size the wall from the round-1 actuals per sample. Record the TRIDENT commit; it must be the pinned one.

**D3, label audit (reading; capped at two days).** For every sample in the approved sets, record donor, generating lab, scanner or session where stated, and technology, from the source (GEO record, 10x page, or the publication's methods), not from HEST's fields, with `donor_label_status` and a new `lab_label_status`, in `results/round3/D3_audit/donor_lab_audit_ext.csv` with the same column conventions as `donor_audit.csv`. No grouping by donor or lab happens before this file exists. Expect the lab field to need it; the benchmark's patient field was wrong in two tasks.

**D4, lab-shift decomposition on the institution set (interval 3).** `round3_d4_lab_decomposition.py`, extending `round2_split_v4.py` with a `lab_out` arm (test on one lab, train on the others; size-matched), alongside `random`, `blocked_buffered`, `slide_out` and `donor_out`. Target genes for the set are chosen on training samples only, per fold, with the reproduction check of R2 as the template. Report the chain of terms per gene set and, before naming the lab term, the written list of everything that differs between labs (scanner, protocol, resolution, tissue preparation, donor population). Rerun the R4 probes with lab as a target. This is the first measurement of institution shift with donor and slide separated, and it is the input to round 4's Topic A under lab shift.

**Predictions.** The lab term is at least as large as the patient-identity term on the benchmark, and it is not explained by tissue composition (the morphology adjustment removes a minority of it). Lab is decodable from embeddings at well above chance under spatial-block CV, as GLMP found. Some of HEST's lab or donor labels in the sets are wrong.

### 6.11 Time and compute

| stage | days | jobs |
|---|---|---|
| S0 | 0.5 (cap 1) | none |
| A0 | 1 to 2 | smoke jobs only |
| A1 | 1 to 2 | 12, one per encoder |
| A2 | 1 | 1 |
| A3 | 2 | 3 |
| A4 | 2 to 3 | 3, CQR time-boxed |
| B1 | 2 | 1 to 3 |
| B2 | 1 to 2 | 1 to 3 |
| D0 | 1 (cap 1) | none |
| D1 | 0.5 plus transfer | none |
| D2 | queue-bound | 3 per set, GPU |
| D3 | 1 to 2 (cap 2) | none |
| D4 | 2 | 3 |

About two to three weeks of wall time with the gates. Head fitting is minutes per encoder per fold; the A1 volume is 12 encoders × 29 folds × 4 designs × repeats, well under R3's 47-hour actuals. Ask for the wall the work needs; do not chase backfill; set harness ceilings from queue time plus runtime; record the partition the job actually ran on.

---

## 7. Repository practice for round 3

- **Layout.** `code/scripts/round3_*.py`, `results/round3/<STAGE>/`, `docs/round3_*.md`, `docs/decisions/`. Figures for the next deck go under `figures/deck/` as `fig08_` onward, rendered by scripts under `code/figures/`, numbers read from files, and added to `results/summary/deck_numbers.csv` by `build_deck_numbers.py`.
- **Only current results in the repository.** When a result is superseded, move it to a `superseded/` subfolder beside its replacement (or the root `superseded/` for root-level files), never delete it, and say so in the commit message. Every file present is current.
- **Working documents live in `docs/`.** Stage reports are written once and frozen; corrections go in the next report and the README. `docs/README.md` is updated whenever a document is added.
- **Provenance.** `PROVENANCE.txt` per output directory with job ID, partition actually used, node, date, commit, command line, config hash with the config it hashes, and `pythonhashseed`.
- **Writes.** Explicit `pa.schema` on every parquet; summaries and acceptance tables before bulk tables; never pipe a long job through `tail`.
- **Parallel work.** One writer per file. If several workers must contribute, each writes its own fragment and a merge step with collision reporting produces the shared file.
- **Commits.** Messages through a file (`git commit -F`). A message that summarises a gate states the full table or points to the file that does. Tag `round3-A1`, `round3-A3`, `round3-final`.
- **Documents.** Run `verify_numeric_claims.py` over the README and `docs/round3_*.md` before each report. Scope for round 3 is round-3 documents plus the README; the round-2 documents are at zero and are not re-swept unless edited. Triage is capped at two hours per report; a false failure that blocks a handover is fixed in the checker with a fixture, time-boxed at half a day, and anything beyond that is reported as a limitation rather than fixed.
- **Caps.** S0 one day. Any checker or tooling work half a day per interval. Anything that is not analysis and is not in this plan: report it as a proposal, do not do it.

---

## 8. Reporting format

After each gate, in this order:

1. Stage and status.
2. What was run, meaning scripts, commits, job IDs, partitions, wall times, peak memory from `sacct`.
3. Acceptance checks with the actual numbers and file paths.
4. For every design and every weighting, the list of variables that differ between its arms, written out.
5. Predictions against outcomes, as a table.
6. Results, numbers from files with paths, dispersion beside every mean; paths rather than pasted tables for anything over 20 rows.
7. Discrepancies, open questions and escalations.
8. What was not checked.
9. Proposed next step.

Keep prose plain. No em-dashes; no colon-then-explanation constructions; math as LaTeX. Numbers in the report at the precision the comparison needs, with the relative scale stated; full precision stays in the files.

---

## 9. Decision boundaries

**You decide alone.** Script structure; seeds; the exact calibration fraction within 20 to 30%; block grid and buffer within the R3 ranges; clipping percentile within 99 to 99.9; bootstrap counts; which additional encoders to include beyond the named ones; job sizing.

**Report and wait (recorded as an escalation inside an interval, then continue).** Any H1 or H2 failure in A0 is the exception, where you stop and report, since nothing downstream is interpretable. Otherwise, any change to a design's arm definitions or to the calibration-unit rule; any fold where the harness cannot produce a calibration set; any new property of the benchmark found along the way; any per-task result that reverses a round-2 sign.

**Escalate to Nicolas.** The D0 proposal (which sets, how much storage) before any download; any download beyond the approved sets, including whole-slide images; anything that would be sent to the HEST authors; anything touching the scientific framing of the two topics; STFlow, which stays deferred.

---

## 10. References for the methods in § 6

- Tibshirani, Barber, Candès, Ramdas. Conformal prediction under covariate shift. NeurIPS 2019.
- Barber, Candès, Ramdas, Tibshirani. Conformal prediction beyond exchangeability. Annals of Statistics 2023.
- Romano, Patterson, Candès. Conformalized quantile regression. NeurIPS 2019.
- Lei, G'Sell, Rinaldo, Tibshirani, Wasserman. Distribution-free predictive inference for regression. JASA 2018 (locally weighted conformal).
- Angelopoulos, Bates, Fannjiang, Jordan, Zrnic. Prediction-powered inference. Science 2023. Angelopoulos, Duchi, Zrnic. PPI++. arXiv:2311.01453. Zrnic and Candès. Cross-prediction-powered inference. PNAS 2024.
- Hierarchical conformal and PPI under clustering: to be supplied by the oversight chat's memo before interval 2, if any.
