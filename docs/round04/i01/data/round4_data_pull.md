# Round 4, stage P: the data pull

28 September 2026. Prepared by the oversight chat for a fresh Claude Science session. This document is self-contained. It is the first thing that happens in round 4, it runs alone, and the two round-4 tracks (the PPI track and the conformal track, each with its own instruction document) start only after its report has been accepted and the repository tagged `round4-data`. Read this document fully, then transcribe section 6 into `docs/round04/tracks/data/round4_data_plan.md` before running anything.

---

## 1. Your role and the people

You are the execution agent. A separate chat session, the oversight chat, reviews your report, makes scope decisions and writes decision memos, which Nicolas hands to you in full. Nicolas Weiyang Zhang (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and, since 23 September, `rc_tengfei_pi`) is the first-year biostatistics PhD student whose project this is. He reads every command before it runs and will ask why. His advisors are Dr. Hongtu Zhu and Dr. Daiwei (David) Zhang at UNC.

Your responsibilities are to run what this document specifies, on UNC Longleaf through Slurm, to verify every output against an expected value before moving on, to write the stage report in the format of section 8, to commit and push to the repository, and to stop at the gate. You do not make scope decisions. Anything this document does not cover is reported as a proposal, not done.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the report, and work continues. This stage has one gate, at its end. Contact with anyone outside the project is never the session's decision.

**How Nicolas wants things written.** Plain, natural prose. No em-dashes. No colon-then-explanation constructions. Math as LaTeX. Numbers quoted at the precision the comparison needs, with the relative scale stated; full precision stays in the files. Every number in a report is read back from the file named beside it. Do not inflate length.

---

## 2. The project in one page

Spatial transcriptomics measures gene expression at known spots on a tissue section. A frozen pathology foundation model maps each spot's H&E image patch to an embedding, and a linear head predicts $\log(1+\text{count})$ per gene from it. The data are nested, spots inside slides inside donors, and that structure is what the project is about.

Rounds 1 to 3 (September 2026) replicated the HEST-1k benchmark exactly, instrumented it, and then measured the premises of two topics, calibrated prediction intervals and valid inference with predicted expression. What round 3 established, in the order it matters:

1. The donor is the unit of every uncertainty statement. A donor-clustered standard error is 29 to 68 times the spot-level one on CCRCC; a spot i.i.d. interval covers 4% of the time at nominal 90% and a donor cluster-robust one with a $t_{G-1}$ reference covers 91%. Conformal intervals calibrated on held-out donors cover 0.856 and on spatial blocks inside the training slides 0.744, in 138 of 138 cells.
2. A valid prediction interval for a new donor exists once $K + 1 \ge 1/\alpha$ calibration donors are available, and the known method (hierarchical conformal, HCP) is conservative. At $K = 10$ on CCRCC it covers 0.969 at 1.95 times the pooled width.
3. Feature-based reweighting cannot repair donor shift here, because slides are separable at AUC 0.97 from the embedding and 0.90 from morphology alone.
4. Adaptive scores buy little width at matched coverage except in the upper tail of predicted values.
5. Prediction-powered inference under donor clustering works and gains modestly (widths 0.85 to 0.89 of classical for good encoders).
6. The expansion delivered a second donor task (Indiana kidney, 25 donor units, all technical axes fixed) and not an institution axis. HEST-1k has no two-laboratory cell with disease held fixed.

Round 4 has two tracks. The PPI track builds the estimator, the allocation result and the labelling-design comparison for a paper on inference and design with the donor as the unit. The conformal track runs a scoping study on sharper valid prediction sets for a new donor. Both need the data this stage pulls. The full account is in `docs/round03/i03/exec/round3_final_report.md` (read its closing page, "What round 3 established") and `docs/round03/i02/exec/round3_A3_stage_report.md`.

---

## 3. The repository, the data and the assets you build on

**Repository.** `NicWYZ/HEST-1k-replication`, public, at tag `round3-final-r2` (commit `e00d9bd`). Layout: `results/round3/<STAGE>/` per stage with `PROVENANCE.txt` per directory; `code/scripts/round3_*.py`; `docs/` for every report and working document, indexed in `docs/README.md`; `docs/decisions/` for memos; `docs/WAYS_OF_WORKING.md`, the accumulated procedure, which you read before your first job.

**Longleaf.** Project tree `/work/users/w/e/weiyang/hest_replication`. Benchmark data under `bench_data/` (gated, 72 samples). Benchmark embeddings under `embeddings/<task>/<encoder>/<sample>.h5`. Expansion downloads under `hest_ext/<set>/` (105 samples at HEST revision `7e8d5a0b0aace41d8c8ec0f6ecea80e4ad2a61ec`, four components each, `patches/`, `st/`, `cellvit_seg/`, `metadata/`, no whole-slide images). Expansion embeddings under `embeddings_ext/<set>/<encoder>/` for the 76 samples of the kidney and breast sets, three encoders (`hoptimus0`, `uni_v2`, `resnet50`), on NVIDIA L40S, float16, bfloat16 and float32 respectively as HEST's loader sets them. Morphology covariates for the benchmark under `instrumentation/morphology_v2/`. Never compute on the login node.

**Files you will use.**

| asset | path | notes |
|---|---|---|
| the HEST-1k inventory | `results/round3/D0_inventory/hest_inventory.csv` | 1,276 rows, one per sample, with organ, species, technology, oncotree, disease state, `patient_label`, `patient_label_status`, `donor_key_provisional`, `lab_provisional`, pixel size and its flag, `in_benchmark`, `is_duplicate_of_other_id`, bytes per component |
| the release tables | `results/round3/D0_inventory/release_tables/` | `HEST_v1_1_0.csv` to `HEST_v1_3_0.csv` |
| the round-3 audit file | `results/round3/D3_audit/donor_audit_r3.csv` | the grouping source for every donor and source label; `donor_audit.csv` in `results/round2/R5b_audit/` is frozen and superseded |
| the download scripts | `code/scripts/round3_d1_*.py` | `snapshot_download` with `allow_patterns` per sample, verification file by file, patch-subset check |
| the embedding script | `code/scripts/round3_d2_embed.py` | the benchmark's own extraction path, per-sample cache, the barcode fix already in |
| the audit builder | `code/scripts/round3_d3_build_audit.py` | joins hand verdicts to the inventory; no network, no inference |
| task definitions | `results/round3/task_defs/<task>.json`, `results/round3/D4_expansion/task_defs/*.json` and `task_def_ext.schema.json` | the A0 format, with the extension schema D4 added |
| the morphology builder | `code/scripts/morphology_features.py`, `results/tailored/morphology/patch_scale_sources.csv` | per-spot nuclear count, mean and median area, five CellViT class fractions, with the per-sample patch-geometry calibration of round 2 |
| training-only gene selection | `code/scripts/round2_r2_fold_hvg.py`, `round3_d4_r2_gene_check.py` | reproduces the shipped selection exactly, then selects on training samples only per fold |
| the harness | `code/scripts/round3_a0_harness.py`, md5 `0ad7ae8efe554c1f285e5f384a9fb7f5` | frozen; import unmodified |
| the numeric-claim gate | `code/scripts/sweep_table.py` | the corrected invocation; run before handover |

**What you already know about the archive**, from `results/round3/D0_inventory/` and D3's audit (`results/round3/D3_audit/d3_notes.md`). 292 samples carry a usable patient label, 870 have none and 114 carry a whitespace string that passes a naive null check. Patient label strings are reused across cohorts, so a donor is keyed on (dataset title, patient label). Fifteen ids are duplicates of other ids and are excluded from every set. 1,074 samples carry an uncertain pixel size. HEST's laboratory field is a senior-author affiliation and was wrong for 23 of 54 kidney samples; nothing is grouped by laboratory in round 4. The benchmark's shipped patches are a different resampling of the same images as the HEST-1k release; no result moves with the layout (`results/round3/D4_expansion/d4_layout_anchor.csv`), and everything in round 4 runs on the HEST-1k layout.

---

## 4. What this stage pulls, and why

The round-4 tracks need three things the archive still holds and the project has not used.

**A third multi-donor task with the technical axes fixed.** Lung Xenium, 24 samples, 21 HEST-labelled donors, one laboratory, pixel size clean on all 24 (`hest_inventory.csv`, organ Lung, technology Xenium). It joins CCRCC (24 donors, Visium, tumour) and Indiana kidney (25 donor units, Visium, non-tumour) as the third task on which $K = 10$ hierarchical calibration and donor-clustered PPI are tested, and it is the only one on a Xenium panel, whose sparsity and dispersion differ from Visium's.

**Every other human sample with a usable donor label.** Storage is not a constraint on Longleaf (Nicolas's decision, 22 September), so the archive's donor-labelled Visium and Xenium samples come down now, in one transfer, so that no later stage waits on a download. They are not embedded and not audited in this stage. They are on disk for the tracks to draw on, and the count and the GB are reported.

**The gene axis.** Every gene-level claim so far is conditional on 50 genes per task chosen with test spots. Visium samples carry the whole transcriptome, and training-only gene selection per fold was implemented in round 2 and used once in round 3 (Indiana). This stage writes the per-fold training-only gene lists at three sizes for every Visium task on disk, so the tracks can report gene-level results as distributions over hundreds of genes.

Two things are built alongside because the tracks need them and they belong with the data. Morphology covariates for the expansion samples (the PPI track's estimands need them), and task definitions in the A0 format for lung Xenium.

---

## 5. Standing rules and conventions

These are the rules that produced most of rounds 2 and 3's findings, each tied to a failure it prevents. `docs/WAYS_OF_WORKING.md` has the full list with the episodes.

- Silent failure is the main risk. Verify each stage's output against an expected value before moving on.
- Never assert a number you have not read back from a file. Cite the path.
- Audit a grouping variable against a source outside the dataset before grouping by it. HEST's patient field was wrong in two benchmark tasks and its laboratory field in 23 of 54 kidney samples.
- Before naming a term, list in writing every variable that differs between its arms.
- Write predictions down before running, and report them beside the outcomes.
- Every output directory gets `PROVENANCE.txt` with job id, partition actually used (jobs requesting `general` land on `spill`), node, date, commit, command line, config hash with the config it hashes, `PYTHONHASHSEED`, and the md5 of the script file that ran (not the repository HEAD; D2's first runs showed the two can differ).
- Every output directory is also stamped with `stamp_dir()` from the `longleaf-provenance` skill, written by the job on the node. Before reusing or rebuilding any output you did not create, run `whose()` on it; if the verdict is `sibling` or `unstamped`, ask the oversight chat rather than rebuilding.
- Explicit `pa.schema` on every parquet; summaries written before bulk tables; seeds from `zlib.crc32`, never `hash()`.
- Size memory from `sacct` (head fitting peaks at 12 GB; 16 GB on 4 CPUs is the honest ask). Set Slurm time limits at about three times the expected runtime from a sibling job's `sacct`, never a blanket 16 h, because with the group's fairshare jobs start through backfill or not at all. Set the harness ceiling from queue time plus runtime. Record the partition the job ran on.
- `$SLURM_SUBMIT_DIR` is the home directory under the submission route in use; set the working directory explicitly in every job script.
- Put a time cap on anything that is not analysis, and stop at the cap.
- Commit messages through a file (`git commit -F`). A message that summarises a gate states the full table or points to the file that does.
- Sub-agents run no git command. The lead is the only committer and checks every sub-agent result against its primary tables before commit. One writer per file; where several workers contribute, each writes a fragment and a merge step with collision reporting produces the shared file.
- Do not edit `README.md`, `docs/WAYS_OF_WORKING.md`, `docs/README.md` or any round-3 file. Proposed edits go in the report; the oversight chat merges them.
- Run `code/scripts/sweep_table.py` over the report before handing over.

**Round 4 conventions.** This stage runs on `main`, which nothing else touches while it runs. Scripts are `code/scripts/round4_data_*.py`. Results go under `results/round4/data/<STAGE>/`. Longleaf outputs go under `hest_ext/`, `embeddings_ext/`, `instrumentation/morphology_ext/` and `results/round4/data/` as named below. The report is `docs/round04/i01/data/round4_data_report.md`. The tag at acceptance is `round4-data`. Job names are prefixed `r4data_`.

---

## 6. The plan

Stages P0 to P6, one interval, one gate at the end. P1 and P2 are the long poles (transfer, then GPU queue). Fan out where marked; the lead verifies every hand-back.

### P0. Setup (half a day, capped at one day)

1. Read this document, `docs/WAYS_OF_WORKING.md`, the closing page of `docs/round03/i03/exec/round3_final_report.md`, and `docs/round03/i01/exec/round3_d0_expansion_proposal.md`. Transcribe section 6 into `docs/round04/tracks/data/round4_data_plan.md`. Flag anything that looks wrong in the report rather than changing it.
2. Confirm the environment. Run the D1 verification script on one existing expansion sample and the D2 embedding script's cache check on one existing embedding; both must pass without change.
3. Check `sinfo` for the GPU partitions and `sacct` for the D2 jobs' actual runtimes per sample, and record them; they size P2.
4. Check the Slurm association for `rc_tengfei_pi`. If it is usable for GPU jobs, record its partitions and fairshare; do not use it without recording that you did.

### P1. Selection and download (one day plus transfer)

**Selection rule, applied to `hest_inventory.csv` by `round4_data_select.py`**, which writes `results/round4/data/P1_selection/selection.csv` with one row per selected sample and the reason it was selected, before anything is downloaded.

- Set L, lung Xenium. Species human, organ Lung, technology Xenium, not a duplicate. Expected 24 samples and 21 donor keys; the script asserts the count it finds and the report states it.
- Set V, donor-labelled Visium and Xenium. Species human; technology Visium or Xenium (not Visium HD, not the older Spatial Transcriptomics platform); `patient_label_status` usable (non-null, non-whitespace); not a duplicate; not already on disk under `bench_data/` or `hest_ext/`; not in set L. Report the count, the number of donor keys, the organs and the GB. No cap.

**Download** with the D1 machinery, four components only, no `wsis/`, to `hest_ext/lung_xenium/` and `hest_ext/donor_labelled_v/`, at the same HEST revision as D1 unless the HuggingFace page shows a newer release, in which case record both and use the newer one for the new sets only (the existing sets are not re-downloaded). Check `quota` and `df` before and after. Verify every expected file arrived at its listed size and that patch barcodes are a subset of expression barcodes (the D1 criterion), recording the unpatched fraction per sample. `PROVENANCE.txt` with the revision and the sample list, and `stamp_dir()` on each set directory.

**Acceptance.** Every selected sample present with every expected file; zero size mismatches; the subset relation holds on every sample.

### P2. Embeddings for set L (GPU; queue-bound)

`round3_d2_embed.py` unchanged, three jobs, one per encoder, on set L only. Set V is not embedded in this stage. Per-sample cache so a killed job resumes. Time limit at three times the per-sample actual from D2 times 24, not a blanket value. Record node, GPU, precision and script md5 in `PROVENANCE__lung_xenium__<encoder>.txt`.

**Acceptance.** 24 samples per encoder, no sample missing patches, embedding row count equal to patch count per sample, barcode column readable by the D4 readers. A layout anchor is not needed here (set L has no benchmark counterpart); the CCRCC anchor of round 3 stands for the layout.

### P3. Morphology covariates for the expansion samples (one day; fan out by set)

Build per-spot nuclear count, mean and median nuclear area, and the five CellViT class fractions from the shipped `cellvit_seg/` for the 30 Indiana kidney samples, the 24 lung Xenium samples and the 18 breast Xenium samples, with the per-sample patch-geometry calibration of round 2 (`patch_scale_sources.csv` is the template; the calibration is re-derived per sample from the patch extents, not copied). Output `instrumentation/morphology_ext/<set>/morphology.parquet` with an explicit schema, and `results/round4/data/P3_morphology/morphology_ext_summary.csv` with per-sample spot counts, join rates and the geometry calibration used.

**Anchor.** Rerun the same builder on two benchmark samples (one CCRCC, one IDC) and reproduce `instrumentation/morphology_v2/` to within $10^{-6}$ on every column. If it does not reproduce, stop this sub-stage and report; do not adjust the builder to match.

**Acceptance.** Join rate at or above 90% of patched spots per sample (round 3 saw 96% on the benchmark); the distribution of nuclear count per spot on Indiana and lung inside the range the benchmark tasks show, reported as quantiles beside CCRCC's and IDC's.

### P4. Audit of set L against source records (reading; capped at one day)

For the 24 lung Xenium samples, from the publication, GEO record or 10x page and not from HEST's fields, record donor id, generating laboratory, instrument and instrument generation where stated, pixel size and objective where stated, disease per sample, preservation, and whether any capture area holds more than one donor's tissue (the kidney papilla lesson). One row per sample with a citation per row, `donor_label_status` and `lab_label_status` as `verified`, `unverifiable` or `contradicted`, appended to a new `results/round4/data/P4_audit/donor_audit_r4.csv` that carries every row of `donor_audit_r3.csv` unchanged plus the 24 new rows. Set V gets no reading in this stage; its rows are added with `donor_label_status = unaudited` so that no track groups by them without noticing.

**Acceptance.** 24 rows with citations; the builder regenerates the file byte-identically from the verdicts and the inventory.

### P5. Task definitions (half a day)

`LUNG_XENIUM.json` in the A0 format with the D4 extension schema, from `donor_audit_r4.csv`, with the per-sample unpatched fraction, the intersection panel and its size, and the fold assignments for `random`, `donor` (leave one donor out) and the $K = 10$ design of round 3's A4b (10 calibration donors from the pool, three draws, crc32 seeds). Validate against both schemas. The existing `INDIANA_KIDNEY` and `CCRCC` definitions are not modified; if the lung definition needs a field they lack, propose a v2 schema in the report and do not apply it.

### P6. Training-only gene lists for the Visium tasks (one day; fan out by task)

For CCRCC, PRAD, READ, LYMPH_IDC, HCC and Indiana kidney, under the `donor` design folds of each task definition, select the top 50, 200 and 500 genes by the benchmark's own variance ranking on the training samples of each fold only, with `round3_d4_r2_gene_check.py`'s reproduction check as the template (it must reproduce the shipped 50-gene list exactly when run on all samples before the per-fold selection is trusted). Output `results/round4/data/P6_genes/genes__<task>__<size>.parquet` (fold, rank, gene) with explicit schema, and `p6_gene_summary.csv` with panel sizes, the number of genes present on every sample, and the overlap of each fold's top-50 with the shipped list. For the Xenium tasks (IDC, lung, breast), record the intersection panel and note that gene selection is the panel.

**Acceptance.** The reproduction check passes on every task; every selected gene is present on every sample of its fold's training and test sets; no fold's list is empty at any size.

### P7. The report and the gate

`docs/round04/i01/data/round4_data_report.md` in the format of section 8. Tag `round4-data` with the report. Then stop. The two track sessions start from that tag and never touch `main`.

**Time.** About four working days, bounded by transfer and the GPU queue. Set P1's transfer going first, then P3, P4, P5 and P6 in parallel on CPU while P1 and P2 run.

---

## 7. Predictions, written before running

1. Set L is 24 samples and 21 donor keys, all with the same pixel size to three decimals and a single laboratory in the source records.
2. Set V is between 150 and 250 samples and under 150 GB.
3. The morphology builder reproduces `morphology_v2` on the two anchor samples to $10^{-6}$.
4. Training-only selection changes the top-50 list by about half its members on every Visium task, as R2 found (mean 25 of 50 shared), and the 500-gene lists are present on every sample in every fold on CCRCC and Indiana but drop below 500 present genes on at least one of PRAD, READ or HCC.
5. At least one lung Xenium source record contradicts a HEST field (pixel size, magnification or a patient label), as every audit so far has found.

---

## 8. Reporting format

In this order. 1. Stage and status. 2. What was run (scripts with md5s, commits, job ids, partitions, wall times, peak memory from `sacct`). 3. Acceptance checks with the actual numbers and file paths. 4. What differs between arms (not applicable here except the morphology anchor; say so). 5. Predictions against outcomes, as a table. 6. Results, numbers from files with paths, dispersion beside every mean; paths rather than pasted tables over 20 rows. 7. Discrepancies, open questions and escalations. 8. What was not checked. 9. Proposed next step, which here is none, since the tracks' documents follow.

Keep prose plain, per section 1.

---

## 9. Decision boundaries

**You decide alone.** Job sizing; the order of P3 to P6; sub-agent structure; the merge mechanics.

**Record as an escalation and continue.** Any sample in set L or set V that the download cannot verify (drop it from the set, list it); any morphology anchor mismatch (stop P3 only, report); any schema field the lung definition needs; any source record for set L that contradicts a HEST field.

**Stop and report.** P1's selection producing counts outside the predicted ranges by more than a factor of two, before downloading (a selection bug is cheaper to fix than a transfer). A `whose()` verdict of `foreign_session` or `other_project` on any directory this stage would write into.

**Never yours.** Contact with anyone outside the project; any download beyond sets L and V; whole-slide images; any change to round-3 files.
