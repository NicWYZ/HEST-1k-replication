# Round 4, stage P, operating plan (the data pull)

Transcribed on 28 September 2026 from `docs/round04/i01/data/round4_data_pull.md` (the oversight chat's
instruction document of the same date) before anything in it was run, as that document and
Nicolas's standing rule both require. The source is committed beside this plan so the transcription
can be checked against it. Where this plan and the source differ, the source governs; the points
below where the source looks wrong are flagged in section 7 and not changed.

The repository starts at tag `round3-final-r2` (commit `e00d9bd`). Stage P runs on `main`, which
nothing else touches while it runs.

---

## 1. The gate

Stage P has one gate, at its end: the report `docs/round04/i01/data/round4_data_report.md`, then stop. The gate rule,
in the wording Nicolas approved, is that report-and-wait means no stage after the gated stage starts
until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not
the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside the
interval there are no interim reports and no interim stop conditions; anything that would have
halted work is handled under the decision boundaries (section 5), recorded in the report's
Escalations section, and work continues. The two round-4 tracks (PPI and conformal) start only after
the report is accepted and the repository is tagged `round4-data`. Contact with anyone outside the
project is never this session's decision.

## 2. Conventions for this stage

- Scripts are `code/scripts/round4_data_*.py`. Results go under `results/round4/data/<STAGE>/`.
  Longleaf outputs go under `hest_ext/`, `embeddings_ext/`, `instrumentation/morphology_ext/` and
  `results/round4/data/` as named below. Job names are prefixed `r4data_`.
- Every output directory gets `PROVENANCE.txt` (job id, partition actually used, node, date, commit,
  command line, config hash with the config it hashes, `PYTHONHASHSEED`, and the md5 of the script
  file that ran) and is stamped with `stamp_dir()` from the `longleaf-provenance` skill, written by
  the job on the node. Before reusing or rebuilding any output this session did not create, run
  `whose()` on it; a verdict of `sibling` or `unstamped` goes to the oversight chat rather than being
  rebuilt, and `foreign_session` or `other_project` on a directory this stage would write into is a
  stop-and-report.
- Explicit `pa.schema` on every parquet; summaries written before bulk tables; seeds from
  `zlib.crc32`, never `hash()`.
- Memory sized from `sacct` (16 GB on 4 CPUs for head fitting). Time limits at about three times the
  expected runtime from a sibling job's `sacct`, never a blanket 16 h. The working directory is set
  explicitly in every job script, because `$SLURM_SUBMIT_DIR` is the home directory under the
  submission route in use. Never compute on the login node.
- Time caps on anything that is not analysis, and a stop at the cap.
- Commit messages through a file. Sub-agents run no git command; the lead is the only committer and
  checks every sub-agent result against its primary tables before commit. One writer per file, with
  fragments and a merge step with collision reporting where several workers contribute.
- `README.md`, `docs/WAYS_OF_WORKING.md`, `docs/README.md` and every round-3 file are not edited.
  Proposed edits go in the report.
- The frozen harness `code/scripts/round3_a0_harness.py` (md5 `0ad7ae8efe554c1f285e5f384a9fb7f5`) is
  imported unmodified.
- The numeric-claim gate (`code/scripts/sweep_table.py`, the corrected invocation) runs over the
  report before handover.
- Jobs are charged to `rc_htzhu_pi`. `rc_tengfei_pi` is checked in P0 item 4 and used only if that
  use is recorded.

## 3. The stages (source section 6)

Stages P0 to P6, one interval, one gate at the end. P1 and P2 are the long poles (transfer, then GPU
queue). Fan out where marked; the lead verifies every hand-back. Order: set P1's transfer going first,
then P3, P4, P5 and P6 in parallel on CPU while P1 and P2 run. About four working days, bounded by
transfer and the GPU queue.

### P0. Setup (half a day, capped at one day)

1. Read the source document, `docs/WAYS_OF_WORKING.md`, the closing page of
   `docs/round03/i03/exec/round3_final_report.md`, and `docs/round03/i01/exec/round3_d0_expansion_proposal.md`. Transcribe section 6
   into this file. Flag anything that looks wrong in the report rather than changing it.
2. Confirm the environment. Run the D1 verification script on one existing expansion sample and the
   D2 embedding script's cache check on one existing embedding; both must pass without change.
3. Check `sinfo` for the GPU partitions and `sacct` for the D2 jobs' actual runtimes per sample, and
   record them; they size P2.
4. Check the Slurm association for `rc_tengfei_pi`. If it is usable for GPU jobs, record its
   partitions and fairshare; do not use it without recording that it was used.

### P1. Selection and download (one day plus transfer)

**Selection**, applied to `results/round3/D0_inventory/hest_inventory.csv` by
`code/scripts/round4_data_select.py`, which writes `results/round4/data/P1_selection/selection.csv`
with one row per selected sample and the reason it was selected, before anything is downloaded.

- **Set L, lung Xenium.** Species human, organ Lung, technology Xenium, not a duplicate. Expected 24
  samples and 21 donor keys; the script asserts the count it finds and the report states it.
- **Set V, donor-labelled Visium and Xenium.** Species human; technology Visium or Xenium (not
  Visium HD, not the older Spatial Transcriptomics platform); `patient_label_status` usable
  (non-null, non-whitespace); not a duplicate; not already on disk under `bench_data/` or
  `hest_ext/`; not in set L. Report the count, the number of donor keys, the organs and the GB. No
  cap.

**Download** with the D1 machinery (`code/scripts/round3_d1_*.py`), four components only (`patches/`,
`st/`, `cellvit_seg/`, `metadata/`), no `wsis/`, to `hest_ext/lung_xenium/` and
`hest_ext/donor_labelled_v/`, at the D1 revision `7e8d5a0b0aace41d8c8ec0f6ecea80e4ad2a61ec` unless the
HuggingFace page shows a newer release, in which case both are recorded and the newer one is used for
the new sets only (the existing sets are not re-downloaded). `quota` and `df` before and after.
Verify every expected file arrived at its listed size and that patch barcodes are a subset of
expression barcodes, recording the unpatched fraction per sample. `PROVENANCE.txt` with the revision
and the sample list, and `stamp_dir()` on each set directory.

**Acceptance.** Every selected sample present with every expected file; zero size mismatches; the
subset relation holds on every sample.

### P2. Embeddings for set L (GPU; queue-bound)

`code/scripts/round3_d2_embed.py` unchanged, three jobs, one per encoder (`hoptimus0`, `uni_v2`,
`resnet50`), on set L only. Set V is not embedded in this stage. Per-sample cache so a killed job
resumes. Time limit at three times the per-sample actual from D2 times 24, not a blanket value.
Node, GPU, precision and script md5 recorded in `PROVENANCE__lung_xenium__<encoder>.txt`.

**Acceptance.** 24 samples per encoder, no sample missing patches, embedding row count equal to patch
count per sample, barcode column readable by the D4 readers. No layout anchor is needed (set L has no
benchmark counterpart); the CCRCC anchor of round 3 stands for the layout.

### P3. Morphology covariates for the expansion samples (one day; fan out by set)

Per-spot nuclear count, mean and median nuclear area, and the five CellViT class fractions, from the
shipped `cellvit_seg/`, for the 30 Indiana kidney samples, the 24 lung Xenium samples and the 18
breast Xenium samples, with the per-sample patch-geometry calibration of round 2
(`results/tailored/morphology/patch_scale_sources.csv` is the template; the calibration is re-derived
per sample from the patch extents, not copied), using `code/scripts/morphology_features.py`. Output
`instrumentation/morphology_ext/<set>/morphology.parquet` with an explicit schema, and
`results/round4/data/P3_morphology/morphology_ext_summary.csv` with per-sample spot counts, join
rates and the geometry calibration used.

**Anchor, first.** Rerun the same builder on two benchmark samples (one CCRCC, one IDC) and reproduce
`instrumentation/morphology_v2/` to within $10^{-6}$ on every column. If it does not reproduce, stop
P3 only and report; do not adjust the builder to match.

**Acceptance.** Join rate at or above 90% of patched spots per sample; the distribution of nuclear
count per spot on Indiana and lung inside the range the benchmark tasks show, reported as quantiles
beside CCRCC's and IDC's.

### P4. Audit of set L against source records (reading; capped at one day)

For the 24 lung Xenium samples, from the publication, GEO record or 10x page and not from HEST's
fields: donor id, generating laboratory, instrument and instrument generation where stated, pixel
size and objective where stated, disease per sample, preservation, and whether any capture area holds
more than one donor's tissue. One row per sample with a citation per row, `donor_label_status` and
`lab_label_status` as `verified`, `unverifiable` or `contradicted`, in a new
`results/round4/data/P4_audit/donor_audit_r4.csv` that carries every row of
`results/round3/D3_audit/donor_audit_r3.csv` unchanged plus the 24 new rows. Set V gets no reading;
its rows are added with `donor_label_status = unaudited`.

**Acceptance.** 24 rows with citations; the builder regenerates the file byte-identically from the
verdicts and the inventory.

### P5. Task definitions (half a day)

`LUNG_XENIUM.json` in the A0 format with the D4 extension schema
(`results/round3/D4_expansion/task_defs/task_def_ext.schema.json`), built from `donor_audit_r4.csv`,
with the per-sample unpatched fraction, the intersection panel and its size, and fold assignments for
`random`, `donor` (leave one donor out) and the $K = 10$ design of round 3's A4b (10 calibration
donors from the pool, three draws, crc32 seeds). Validated against both schemas. The existing
`INDIANA_KIDNEY` and `CCRCC` definitions are not modified; a field the lung definition needs and they
lack becomes a v2 schema proposal in the report, not applied.

### P6. Training-only gene lists for the Visium tasks (one day; fan out by task)

For CCRCC, PRAD, READ, LYMPH_IDC, HCC and Indiana kidney, under the `donor` design folds of each task
definition, the top 50, 200 and 500 genes by the benchmark's own variance ranking on the training
samples of each fold only, with `code/scripts/round3_d4_r2_gene_check.py`'s reproduction check as the
template (it must reproduce the shipped 50-gene list exactly when run on all samples before the
per-fold selection is trusted). Output `results/round4/data/P6_genes/genes__<task>__<size>.parquet`
(fold, rank, gene) with explicit schema, and `p6_gene_summary.csv` with panel sizes, the number of
genes present on every sample, and the overlap of each fold's top-50 with the shipped list. For the
Xenium tasks (IDC, lung, breast), the intersection panel is recorded, with a note that gene
selection is the panel.

**Acceptance.** The reproduction check passes on every task; every selected gene is present on every
sample of its fold's training and test sets; no fold's list is empty at any size.

### P7. The report and the gate

`docs/round04/i01/data/round4_data_report.md` in the source's section 8 format: stage and status; what was run
(scripts with md5s, commits, job ids, partitions, wall times, peak memory from `sacct`); acceptance
checks with the actual numbers and file paths; what differs between arms (only the morphology anchor
applies); predictions against outcomes as a table; results with paths and dispersion beside every
mean; discrepancies, open questions and escalations; what was not checked; proposed next step (none).
Tag `round4-data` with the report, then stop.

## 4. Predictions (source section 7)

The five predictions are the source's section 7, written before anything ran. They are not restated
here, so they cannot drift from the source's wording; the report sets outcomes beside them.

## 5. Decision boundaries (source section 9)

- **Decided alone:** job sizing; the order of P3 to P6; sub-agent structure; merge mechanics.
- **Recorded as an escalation, and work continues:** a sample in set L or V the download cannot
  verify (dropped and listed); a morphology anchor mismatch (P3 stops, the rest continues); a schema
  field the lung definition needs; a set L source record that contradicts a HEST field.
- **Stop and report:** P1's selection producing counts outside the predicted ranges by more than a
  factor of two, before downloading (set L predicted at 24; set V at 150 to 250, so a stop below 75
  or above 500); a `whose()` verdict of `foreign_session` or `other_project` on any directory this
  stage would write into.
- **Never this session's:** contact outside the project; any download beyond sets L and V; whole-slide
  images; any change to round-3 files.

## 6. Parallel tracks

Per Nicolas's standing rule, parallel work goes to sub-agents. P0 is the lead's. P1's selection is
the lead's, because the stop-and-report check on its counts gates the download. After that the
download (P1) and then the embeddings (P2) form one queue-bound track, and P3, P4, P5 and P6 run
beside it on CPU. P5 needs `donor_audit_r4.csv` from P4 and the lung download from P1, and so runs
after both. The lead merges, verifies and commits; sub-agents run no git command.

## 7. Points in the source flagged for the report rather than changed

Checked against `results/round3/D0_inventory/hest_inventory.csv` before anything ran.

1. **Set L contains two benchmark samples.** The rule (human, Lung, Xenium, not a duplicate) selects
   24 samples, and two of them, `TENX118` and `TENX141`, are the benchmark LUNG task. Unlike set V,
   set L's rule does not exclude samples already on disk under `bench_data/`, and both already carry
   `benchmark_r2` rows in `donor_audit_r3.csv`. Read as written: set L is all 24, downloaded in the
   HEST-1k layout like everything else in round 4. P4's 24 new rows will then duplicate two
   benchmark rows, which `donor_audit_r4.csv` handles as round 3 did, with both rows kept and a
   `row_origin` column.
2. **Two of the 24 carry no patient label** (`patient_label_status = missing` on 2, `labelled` on
   22), while the inventory's provisional donor key still gives 21 keys. Where those two keys come
   from is P4's to read; the lung task definition groups by the audit, not by the provisional key.
3. **Set L's pixel sizes are not a single value.** The inventory's estimated pixel size takes four
   values over the 24 (0.2125, 0.2517, 0.2736 and 0.2739 µm), and the samples come from four dataset
   titles. Section 4's "pixel size clean on all 24" is read as the resolution flag being clear, and
   prediction 1 (one pixel size to three decimals, one laboratory) is left to be scored.
4. **Set V's technology rule and "Xenium 5k".** The inventory labels seven samples `Xenium 5k`, and
   Visium HD appears as both `Visium HD` and `Visium HD 3'`. The rule names Visium and Xenium and
   excludes Visium HD and Spatial Transcriptomics; it does not name Xenium 5k. Applied literally,
   exact labels `Visium` and `Xenium` only. Any donor-labelled Xenium 5k samples are counted in the
   report as a proposal, because a download beyond sets L and V is not this session's.
5. **P6's reproduction check cannot apply to Indiana kidney.** There is no shipped 50-gene list for a
   non-benchmark task. For Indiana, P6 uses round 3 D4's training-only per-fold selection
   (`results/round3/D4_expansion/d4_indiana_fold_genes.csv`) as the check that the per-fold code path
   reproduces, and reports the difference.
6. **P6's Xenium note names IDC, lung and breast only.** The benchmark's other Xenium tasks (PAAD,
   SKCM, COAD, LUNG) are neither in P6's Visium list nor in its Xenium note. Their intersection panels
   are recorded alongside, since that costs nothing, and the report says so.
7. **P2's time-limit rule.** "Three times the per-sample actual from D2 times 24" is sized from the
   D2 breast Xenium jobs, the only Xenium sibling, rather than from the kidney Visium ones, since
   Xenium samples are several times larger.
8. **The tag.** Section 5 says the tag `round4-data` is made "at acceptance"; P7 says "Tag
   `round4-data` with the report." Followed as P7 says, which is how the round-3 gates were tagged.
   If the oversight chat asks for changes, the revision gets a new tag rather than moving a pushed
   one, as `round3-A3-r2` and `round3-final-r2` did.
9. **The index.** This plan and the report are new documents under `docs/`, and `docs/README.md` is
   not edited this stage. Their index entries are proposed in the report.

## 8. The P1 decision, transcribed before P1's download starts

From `docs/round04/i01/data/round4_data_P1_decision.md` (28 September 2026, the oversight chat's answer to
`results/round4/data/P1_selection/STOP_NOTE.md` at `c31e36e`). Where it and the sections above differ,
it governs.

1. **Option 1.** Sets V and L proceed as selected: V is 39 samples and 19.0 GB, L is 24 samples and
   9.4 GB (`results/round4/data/P1_selection/selection.csv`). The selection rule stands as written and
   nothing is added to it. The Spatial Transcriptomics platform and unlabelled samples stay excluded;
   a later use for either comes back as a proposal.
2. **Prediction 2 is scored as refuted** in the P7 report. The stated reason is that it was written
   from the 172 labelled Visium and Xenium samples without subtracting the 113 already on disk.
3. **Set L's two unlabelled samples** stay in the download and the embedding. P4 tries to resolve
   their donors from the source record. If it cannot, they are recorded `unverifiable` and excluded
   from every donor unit. P5 builds the lung task definition on the donor units that remain (19 to
   21), and the P7 report states the count P5 used.
4. **Set L's two benchmark LUNG samples** (`TENX118`, `TENX141`) are downloaded again in the HEST-1k
   layout, like every other expansion sample, because the two layouts are not mixed. P5 uses the
   HEST-1k-layout copies, and the benchmark LUNG task is untouched. This settles section 7 item 1.
5. **Set V's 24 samples with an uncertain pixel size** are downloaded as they are. Set V is neither
   embedded nor audited in this stage, and the flag travels with its rows.
6. **The P0 finding.** `round3_d1_download.py`'s patch-count test is stale and is not edited.
   `round4_data_*` scripts use the subset relation, and the P7 report lists the stale check under
   proposed edits.
7. **What continues.** P1's download starts on receipt of the memo, set L first and then set V. P2 to
   P6 follow as planned. The one gate is P7, and the gate rule is unchanged.

On the same day Nicolas said that `rc_tengfei_pi` should now be on his association. P0 item 4's check
is therefore repeated before P2's GPU jobs, and any use of that account is recorded.

## 9. The P7 decisions and stage P8, transcribed before P8 starts

From `docs/round04/i02/data/round4_data_P7_decisions.md` (30 September 2026, the oversight chat's
acceptance of `docs/round04/i01/data/round4_data_report.md` at tag `round4-data`, `2905525`). Where it and the
sections above differ, it governs.

**Accepted.** The report is accepted and the predictions are scored as the report scored them.

**Decisions that change files in P8.**
1. `NCBI865` is reinstated by dropping its one patch barcode, `051x019`. The drop is recorded as
   `dropped_patch_barcodes` in the task definition. The subset relation is asserted after the drop,
   not relaxed. The embedding row for that patch is excluded by barcode at read time, and the
   embedding files are not rewritten.
2. D4's probe box: the `patch_geometry` fallback in `round3_d4_probe.py` is corrected to half the
   extent and its docstring fixed. Nothing is rerun. Round 3's 31% to 34% statement is quarantined.
3. Control features: a control-free Xenium panel table is written, and both tracks also filter at
   read time.
4. `round3_d1_download.py`: the stale patch-count test is replaced by the subset relation.
5. Schema v2 is written as a new file. The v1 file is untouched.
6. The `docs/README.md` index entries are added, with the P7 decisions memo among them.

**Recorded without file changes in P8:** `TENX197` stays (item 2). The lung donor count is read from
the task file (item 4). K = 10 stays, and the conformal track adds K = 6 and K = 8 on lung (item 5).
`NCBI885`, `NCBI886`, `NCBI887` and `TENX141` stay excluded (items 7, 8 and 12). The audit file is
the record of HEST's contradicted fields (item 9). Disease goes into the lung difference list
(item 11). Future set-V jobs ask for 32 GB (item 14). Jobs are identified by Slurm id, with the
intended prefix recorded in `PROVENANCE.txt` (item 15). Sub-agents call `stamp_dir()` from their own
process (item 16). Both tracks may use `rc_tengfei_pi` (item 18). The ten older unresolved claims
stay as a round-5 item (item 19). Proposed edit 5 is deferred.

**Stage P8** (one day, capped; report and wait). It runs on `main` from `round4-data`, writes under
`results/round4/data/P8_addendum/`, and rewrites only the files named. No downloads, no embeddings,
no GPU.
1. Rewrite `results/round4/data/P5_task/LUNG_XENIUM.json` with `NCBI865` as a member,
   `dropped_patch_barcodes` `{"NCBI865": ["051x019"]}`, and the donor, `random` and `a4b_k10`
   folds regenerated. Keep the previous file as `LUNG_XENIUM__19_pre_P8.json` and the previous
   validation as `p5_validation__pre_P8.csv`. Acceptance: 20 samples, 15 donor units, 15 donor
   folds, 45 `a4b_k10` rows, a minimum of 4 training donors, and the subset relation on every sample
   after the drop.
2. Write `results/round3/D4_expansion/task_defs/task_def_ext.schema.v2.json`. It adds row origin
   `expansion_r4`, a per-sample `slide_id`, an `a4b_k10` fold key and `dropped_patch_barcodes`.
   Validate the new lung file against it and record the result.
3. Write `results/round4/data/P8_addendum/xenium_panels_genes_only.csv` with the controls removed
   and a per-task count of controls dropped. Expected: 61 on five tasks, 220 on IDC.
4. Correct `round3_d4_probe.py` (not run) and `round3_d1_download.py` (self-test if it has one; no
   download). These are ordinary commits with the reason in the message.
5. Write `results/round4/data/P8_addendum/lung_edge_patches.csv`. For each of the 20 lung samples,
   it gives the fraction of patches whose centre is more than 1.6 mm from the tissue centroid, with
   the HEST rectangle and the 3 mm core diameter beside it. Report only.
6. Add the index entries, write `docs/round04/i02/data/round4_data_P8_report.md` in the report format, run the
   numeric-claim gate over it, commit, tag `round4-data-v2`, and stop.

**How the memo is read where it leaves a choice.** Flagged here rather than decided silently.
1. *Where `dropped_patch_barcodes` lives.* The memo writes it as a mapping from sample to list, so
   it is a top-level key of the task definition in exactly that form, and schema v2 defines it there.
2. *Where the `a4b_k10` lists live.* Schema v2 adds `folds.a4b_k10`, which becomes the canonical
   place. `expansion.a4b_k10` keeps its parameters and an identical copy of the lists, asserted
   equal, so that code written against the 19-sample file still reads them. `slide_id` is added per
   sample, and `expansion.source_slide_id` is kept.
3. *"`random` regenerated at the same sizes."* `random` is parametric: 5 repeats, with the test size
   taken from the `patient` folds. The parameters stay the same. The `patient` folds are regenerated
   over the 15 donors with the same 6 groups, so the test size follows the new donor set.
4. *The subset check after the drop, and the edge diagnostic,* need the patch and expression files,
   which are on Longleaf only. They run as one CPU job that reads the files and writes nothing
   outside its working directory. This is not a download, embedding or GPU job.
5. *Tissue centroid* is the mean of the sample's patch centres. The patch `coords` are box centres
   (this is how `round3_d4_probe.py` and P3 use them). NCBI865 is measured without its dropped
   patch. The threshold is converted with the sample's pixel size. The HEST rectangle comes from
   the inventory's `fullres_px_width` and `fullres_px_height`.
6. *`round3_d1_download.py` has no self-test.* It is a module-level script with no test entry. The
   change is checked by compiling it, and it is recorded that no download was run.
7. *Editing `docs/README.md` and the two round-3 scripts, and adding one file under a round-3
   directory,* is authorised by this memo for these items only. The standing rule otherwise holds.
8. *The gate* runs over README, `docs/README.md`, this plan and the P8 report. The ten older
   unresolved claims are out of scope, per item 19.
