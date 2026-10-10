# Round 4, stage P: the data pull, report

Instruction: `docs/round04/i01/data/round4_data_pull.md`, transcribed in `docs/round04/tracks/data/round4_data_plan.md`, with the
oversight chat's P1 decision (`docs/round04/i01/data/round4_data_P1_decision.md`) recorded as the plan's
section 8. Format: the instruction's section 8. Date: 28 September 2026.

## 1. Stage and status

Stage P is complete, P0 to P6 and this report, and it stops here for the oversight chat. No track
session has started. Every stage's output was handed back by a sub-agent or built by the lead, and the
lead checked it against its primary tables before it was committed. The lead's checks are written
down in `results/round4/data/P1_download/p1_p2_lead_verification.md`,
`results/round4/data/P6_genes/p6_lead_verification.md` and the commit messages for P3 and P4.

Two samples change what the tracks start from. `NCBI865` fails P1's subset relation. On the lead's
ruling it stays on disk and in the embeddings, and it is left out of set L's task membership until the
oversight chat decides (escalation 1). The lung task is therefore **19 samples and 14 donors**, where
the P1 decision expected 19 to 21 donor units (escalation 4).

## 2. What was run

Commits on `main`, in order: `d431630` (instruction and transcription), `d08a693` (P1 selection and
stop), `c31e36e` (P0), `71451d7` (P1 decision), `15ca1f0` (P4), `3048f83` (P3), `60ab51d` (P5),
`028637a` (P6), `07f6280` (P1 download and P2). The Longleaf working copy was at `71451d7` for every
job after P0. P0 ran at `e00d9bd`, before the sync.

Scripts and the md5 of the file that ran. Every one was recomputed by the lead on the committed file.

| stage | script | md5 |
|---|---|---|
| P0, P1 | `code/scripts/round3_d1_download.py` (P0 only, unchanged) | `4cbb8b9b3417b6e31daf80638915127e` |
| P0, P2 | `code/scripts/round3_d2_embed.py` (unchanged) | `3b9e47a045993bc2bd38790466486178` |
| P1 | `code/scripts/round4_data_select.py` | `8d3822d60f2ce8407fee95b43d94bd71` |
| P1 | `code/scripts/round4_data_download.py` | `8420374d957de7cf9b3e3068c42d332a` |
| P2 | `code/scripts/round4_data_p2_accept.py` | `e0e32d959b90daeef7a4568141eb6246` |
| P3 | `code/scripts/round4_data_morphology.py` | `987d005ad66e9f8bdbd7544901298c4a` |
| P4 | `code/scripts/round4_data_build_audit_r4.py` | `4ec393a8a4a83574c5bbe51a35b969c5` |
| P5 | `code/scripts/round4_data_task_lung.py` | `f040b71ddf85fce7ac77050bea410f1e` |
| P5 | `results/round4/data/P5_task/panel_job/lung_panel.py` | `f72eb6aba473637cf06c5de4cede099d` |
| P6 | `code/scripts/round4_data_p6_genes.py` | `03ecb15ccdf71dd22d05f2802f28f0ce` |

Jobs. Account, partition, node, wall time and batch-step MaxRSS are from the lead's `sacct` query, `results/round4/data/P7_report/stageP_sacct.psv`, as CSV in
`results/round4/data/P7_report/stageP_sacct.csv`. The P6 jobs are in
`results/round4/data/P7_report/p6_sacct_lead.csv`. Every CPU job asked for `general` and ran on `spill`.
The submission route replaces `--job-name`, so every job is recorded as `operon-<id>` rather than
`r4data_` (escalation 15).

| stage | job | account | partition | node | elapsed | limit | ReqMem | MaxRSS |
|---|---|---|---|---|---|---|---|---|
| P0 check | `2723647` | rc_htzhu_pi | l40-gpu | g181009 | 00:01:08 | 00:45:00 | 16G | 1765772K |
| P1 set L | `2750881` | rc_htzhu_pi | spill | b1001 | 00:01:51 | 00:30:00 | 16G | 10382900K |
| P1 set V | `2751561` | rc_htzhu_pi | spill | c0825 | 00:02:43 | 00:45:00 | 16G | 16777920K |
| P2 hoptimus0 | `2751562` | rc_tengfei_pi | l40-gpu | g181009 | 00:11:11 | 01:00:00 | 32G | 14121700K |
| P2 uni_v2 | `2751563` | rc_tengfei_pi | l40-gpu | g181006 | 00:09:17 | 01:00:00 | 32G | 8989324K |
| P2 resnet50 | `2751564` | rc_tengfei_pi | l40-gpu | g181006 | 00:08:07 | 01:00:00 | 32G | 3139208K |
| P3 anchor | `2753400` | rc_htzhu_pi | spill | c0813 | 00:08:56 | 00:30:00 | 16G | 2953320K |
| P3 expansion | `2772935` | rc_htzhu_pi | spill | c0926 | 00:10:10 | 00:45:00 | 32G | 5612292K |
| P5 panel | `2774326` | rc_htzhu_pi | spill | c0304 | 00:00:03 | 00:15:00 | 4G | 79404K |

P6 ran eight jobs on rc_htzhu_pi, all on spill. The largest was CCRCC's list job `2774163`, which took
00:27:51 against a 02:00:00 limit, with MaxRSS 15822932K against 32G. Two first attempts failed and
were rerun: `2753541` (check) and `2776647` (verify). Source: `results/round4/data/P7_report/p6_sacct_lead.csv`.

The P2 jobs are the only ones on rc_tengfei_pi, and each P2 PROVENANCE file records that use. The
association read at report time lists both accounts with `gpu_access` and `gres/gpu=16`. Fairshare is
0.006797 on rc_htzhu_pi and 0.017973 on rc_tengfei_pi, which is now lower than before P2. Source:
`results/round4/data/P7_report/accounts_at_report.txt`. The three GPU jobs waited in the l40-gpu
queue from 13:50 to between 15:45 and 16:08, and that queue, not the transfer, set the stage's length.

## 3. Acceptance checks

**P0.** `round3_d1_download.py` and `round3_d2_embed.py` ran unchanged on `NCBI692` in a scratch tree of
links. D1 found 5 of 5 files at their listed sizes. D2 read the sample as cached, with 357 rows. D1's
patch-count test printed a failure (357 patches against 370 spots), which is the stale check the P1
decision rules on (proposed edit 1). Source: `results/round4/data/P0_setup/d1_verification.csv`,
`results/round4/data/P0_setup/d2_extraction__p0check__resnet50.csv`.

**P1, download.** Every selected sample arrived with every expected file:
- set L: 24 samples and 120 of 120 files;
- set V: 39 samples and 195 of 195 files;
- 0 size mismatches;
- 9,358,042,424 bytes for set L and 18,980,302,609 for set V, equal to the selection table on every row.

The subset relation holds on 23 of 24 set-L samples and 39 of 39 set-V samples. `NCBI865` fails it:
1 of its 2,143 patch barcodes, `051x019`, has no expression row. The HEST revision is `7e8d5a0b`,
unchanged from D1. Source: `results/round4/data/P1_download/p1_verification.csv`,
`results/round4/data/P1_download/p1_p2_lead_verification.md`.

**P2.** For each of the three encoders:
- 24 of 24 samples accepted;
- 55,104 embedding rows against 55,104 patches;
- rows equal patches on every sample;
- barcodes readable by the D4 readers and in patch order on 72 of 72 rows.

Source: `results/round4/data/P2_embeddings/p2_acceptance.csv`.

**P3.** The anchor reproduces `morphology_v2` exactly on `INT1` (CCRCC) and `NCBI783` (IDC), with a
maximum absolute difference of 0.0 on every column. Source:
`results/round4/data/P3_morphology/p3_anchor_comparison.csv`.

Join rate is at or above 0.90 on 30 of 30 Indiana, 24 of 24 lung and 17 of 18 breast samples. The
exception is `TENX197`, at 0.861937 (escalation 2). Source:
`results/round4/data/P3_morphology/p3_acceptance_join_and_quantiles.csv`.

Nuclear count per spot is inside the benchmark range. The pooled medians are 42.0 on Indiana, 45.0 on
lung and 39.0 on breast, against 33.0 on CCRCC and 49.0 on IDC. The means and standard deviations are
42.662539 (17.071913), 49.114422 (32.346114), 43.175080 (31.693555), 36.538521 (29.457330) and
51.171910 (33.416123). Source: `results/round4/data/P3_morphology/morphology_ext_pooled.csv`.

**P4.** `results/round4/data/P4_audit/donor_audit_r4.csv` carries the 148 round-3 rows unchanged, 24
lung rows with citations, and 39 set-V rows marked `unaudited`. The builder regenerated it
byte-identically in two independent lead rebuilds (commit `15ca1f0`). Source:
`results/round4/data/P4_audit/p4_audit_summary.csv`.

**P5.** `results/round4/data/P5_task/LUNG_XENIUM.json` passes relaxed v1. It fails v1 strict on the
extension fields, by design, as the D4 definitions do. It fails the committed extension schema only on
the row-origin enum, which has no `expansion_r4` value. It passes that schema once the one value is
added in memory. The schema file is not edited; proposed edit 3 covers it.

The folds cover every sample and are disjoint. The K = 10 lists are identical, on all 42 fold-by-draw
rows, to what round 3's own `round3_d4_sets.a4b_specs` produces on the definition. Source:
`results/round4/data/P5_task/p5_validation.csv`, `results/round4/data/P5_task/p5_a4b_crosscheck.txt`.

**P6.** The reproduction check passes:
- 5 of 5 benchmark tasks reproduce the shipped 50-gene list in set and order;
- 55 of 55 of D4's Indiana selections reproduce.

Presence was checked 974,818 times with 0 absent, and no list is empty at any size. Source:
`results/round4/data/P6_genes/p6_check_reproduction.csv`,
`results/round4/data/P6_genes/p6_check_indiana_folds.csv`, `results/round4/data/P6_genes/p6_acceptance.csv`.

## 4. What differs between arms

This stage has no experimental arms, except the P3 anchor. There the new builder and
`morphology_v2` differ only in the code path, so the inputs, samples and geometry source are the same.
The tracks' documents will list arms when they define terms.

## 5. Predictions against outcomes

The predictions are those in the instruction's section 7, written before anything ran.

| # | prediction | outcome | score |
|---|---|---|---|
| 1 | set L is 24 samples and 21 donor keys, one pixel size to three decimals, one laboratory | 24 samples; HEST's labels give 21 keys but the sources give 15 donor units; four HEST pixel sizes; two laboratories (P4 section 7) | refuted |
| 2 | set V is 150 to 250 samples and under 150 GB | 39 samples, 18.98 GB; written from the 172 labelled samples without subtracting those already on disk (the P1 decision) | refuted |
| 3 | the morphology builder reproduces `morphology_v2` to 1e-6 | maximum absolute difference 0.0 on both anchors | held |
| 4 | training-only selection changes the top-50 by about half on every Visium task; 500-gene lists complete on CCRCC and Indiana, short on at least one of PRAD, READ or HCC | CCRCC shares 42.71 of 50 on average; Indiana is the only task with a short list; PRAD, READ and HCC are complete | refuted in three of four claims |
| 5 | at least one lung source record contradicts a HEST field | patient labels contradicted on 8 samples, magnification on 20 | confirmed |

Sources, row by row:
- row 1: `results/round4/data/P1_selection/selection_summary.json` (24 samples, 21 keys; pixel sizes
  0.2125, 0.2517, 0.2736, 0.2739) and `results/round4/data/P4_audit/p4_notes.md`;
- row 2: `results/round4/data/P1_selection/selection_summary.json`;
- row 3: `results/round4/data/P3_morphology/p3_anchor_comparison.csv`;
- row 4: `results/round4/data/P6_genes/p6_gene_summary.csv`;
- row 5: `results/round4/data/P4_audit/donor_audit_r4.csv`.

Round 2's reference figure for prediction 4 is reproduced from round 2's own table: a mean of 24.69
shared (sd 11.13) over 16 folds of the five Visium tasks, from
`results/round2/R2_fold_hvg/fold_hvg__hoptimus0.csv`, computed in
`results/round4/data/P7_report/report_numbers.csv`. CCRCC's donor folds hold out 1 of 24 samples
where round 2's patient folds held out 4, which is why CCRCC's top-50 barely moves. So "about half" is
a property of round 2's splits, not of training-only selection.

## 6. Results

**Sets.** Set L has 24 samples, 55,104 patches and 86,408 expression spots. Its unpatched fraction per
sample has a median of 0.379772 (min 0.282733, max 0.757519, mean 0.414785, sd 0.119870). Set V has 39
samples, 93,814 patches and 111,623 spots, with a median unpatched fraction of 0.003063 (max 0.549540).
24 of the 39 carry the uncertain-pixel-size flag, which travels with their rows. Source:
`results/round4/data/P1_download/p1_verification.csv`; the statistics are in
`results/round4/data/P7_report/report_numbers.csv`.

**The lung task** (`results/round4/data/P5_task/LUNG_XENIUM.json`):
- 19 TGen fibrosis TMA cores from 14 donors, run by one laboratory on one instrument
  (`XETG00048`) with one software generation, at pixel size 0.2125 µm;
- nine donors with one sample each and five with two;
- donor labels verified on 11 samples and contradicted by HEST on 8, where HEST's patient label splits
  a donor.

The 541-feature var list is identical on all 19. 198 of the features are controls, which leaves 343
genes, and the 343 genes are the target list. Source: `results/round4/data/P5_task/p5_validation.csv`,
`results/round4/data/P5_task/panel_job/lung_panels.csv`.

Every one of the four capture slides carries 2 to 5 donors, so no slide-out design is possible and
`slide_out` is empty. The slide ids are recorded per sample under `expansion.source_slide_id`.

Folds:
- `donor`: leave one out, 14 folds;
- `patient`: 6 grouped folds, used only to size `random`;
- `random`: 5 repeats;
- `a4b_k10`: 14 folds by 3 draws. Each fold's pool of 13 donors gives 10 calibration and 3 training donors.

**Gene lists.** Training-only lists at 50, 200 and 500 cover 59 donor folds over six tasks. Top-50
overlap with the shipped list, as mean, sd, min and max over folds:
- CCRCC 42.71, 6.22, 21, 48;
- HCC 24.00, 1.41, 23, 25;
- LYMPH_IDC 21.00, 3.56, 16, 24;
- READ 16.50, 2.12, 15, 18;
- PRAD 11.00, 1.41, 10, 12;
- pooled over the 34 benchmark folds, 35.65 (sd 12.57).

One Indiana fold, `kidVis_atlas_IU-F59`, is short of k: 199 at 200 and 494 at 500. That is the
specified off-panel drop, and the list was not topped up. Source:
`results/round4/data/P6_genes/p6_gene_summary.csv`; the pooled figures are in
`results/round4/data/P7_report/report_numbers.csv`.

The parquets stay on Longleaf under `results/round4/data/P6_genes/` and are gitignored. The CSV copies
are committed.

**Morphology.** The parquets are `instrumentation/morphology_ext/{indiana_kidney, breast_xenium,
lung_xenium}/morphology.parquet` on Longleaf. All 72 samples take their geometry from the patch
`downsample` attribute. Pooled join rates are 0.998939 on Indiana, 0.969680 on breast and 0.983903 on
lung. Source: `results/round4/data/P3_morphology/morphology_ext_pooled.csv`.

## 7. Discrepancies, open questions and escalations

1. **`NCBI865` fails the subset relation.** Its patch barcode `051x019` is absent from the expression
   file after stripping and case folding, while its grid neighbours are present
   (`results/round4/data/P1_download/ncbi865_barcode_diagnostic.txt`). The fault is in the shipped
   data, not the transfer. Round 3's D4 loader asserts the relation, so it would raise on this sample.

   Following the decision boundary for samples the download cannot verify, the sample is out of set
   L's task membership (`set_L_member_for_task` False) and listed under `expansion.pending_oversight`
   in the lung definition. Its donor, `lungXen_VUILD110`, has no other sample. **The oversight chat to
   decide:** exclude it, or reinstate it by dropping the one patch.
2. **`TENX197` joins at 0.861937**, below the 0.90 acceptance line, the only one of the 72 samples to
   fall short. It stays in the breast set and nothing downstream was changed. Source:
   `results/round4/data/P3_morphology/p3_acceptance_join_and_quantiles.csv`.
3. **A round-3 defect in D4's morphology probe box.** The `patch_geometry` fallback in
   `round3_d4_probe.py` returns `112/pixel_size` as the half-width. That quantity is the full 112 µm
   extent, so on all 30 Indiana samples the half-width is exactly 2.0 times too large. The box
   therefore has 4 times the area, and nucleus-spot pairs are 3.642 to 3.972 times the correct count.
   Source: `results/round4/data/P3_morphology/p3_d4_geometry_discrepancy.csv`.

   D4 used the fallback on all 54 kidney samples. Round 3's statement that morphology removes 31% to
   34% of the above-chance probe signal (`docs/round03/i03/exec/round3_final_report.md`, H23 and item 10) was computed
   on that box. Round-3 files are not changed. **The oversight chat to decide** whether D4's
   population probe is rerun with the corrected box, and where the correction is recorded.
4. **Lung donor units: 14, not 19 to 21.** The P1 decision expected P5 to build on 19 to 21 donor
   units. The source records support 15, from 20 samples. HEST's 21 keys come from splitting four
   donors into eight labels and from counting samples that have no resolvable donor. Excluding
   `NCBI865` leaves 14. Source: `results/round4/data/P4_audit/p4_notes.md`, section 4.
5. **K = 10 on 14 donors leaves 3 training donors per fold.** Each donor fold's pool is 13 donors, so
   A4b's fixed K = 10 leaves 3 donors, about 4 samples, to train on. K is not a session choice. The
   tracks should know the design runs at that size. Source: `results/round4/data/P5_task/p5_validation.csv`.
6. **Multi-donor slides.** 22 of the 24 set-L samples sit on a slide carrying more than one donor.
   Each HEST image of the 20 fibrosis samples is one core, but some rectangles are larger than the
   core: `NCBI856` is 3.64 mm by 5.27 mm against a 3 mm core. Whether any edge patch holds a
   neighbouring donor's tissue has not been checked (section 8). Source:
   `results/round4/data/P4_audit/p4_notes.md`, sections 2 and 9.
7. **`NCBI885` and `NCBI886` are whole-capture-area TMAs.** Each is a 17-donor TMA, and the two are
   serial sections of one block. They are excluded from every donor unit, stay on disk and in the
   embeddings, and are not in the lung task. HEST records each as one sample with no multi-donor flag.
   Source: `results/round4/data/P4_audit/p4_notes.md`, section 2.
8. **`NCBI886` duplicates `NCBI887`.** They are the same physical section (slide `0069259`), and HEST
   flags neither as a duplicate. `NCBI887` is outside set L because its technology string is
   `Xenium 5k`. Source: `results/round4/data/P4_audit/donor_audit_r4.csv`.
9. **HEST fields contradicted by the sources.** HEST gives magnification 40x on the 20 fibrosis
   samples, where the primary publication states a x20 objective. HEST splits four donors into eight
   patient labels. `TENX118`'s HEST pixel size describes a different raster from the source's, which
   the audit records as two images rather than a contradicted number. Source:
   `results/round4/data/P4_audit/p4_notes.md`, sections 3, 5 and 6.
10. **Control features are counted as genes in the Xenium panels.** The intersection panels in
    `results/round4/data/P6_genes/p6_xenium_panels.csv` include negative controls:
    - 61 (NegControlCodeword and NegControlProbe) on each of BREAST_XENIUM, COAD, LUNG, PAAD and SKCM;
    - 220 on IDC, of which 159 are BLANK codewords.

    Round 2's recorded intersections include them too, and so does round 3's
    `BREAST_XENIUM.json` target list, which is 90 genes plus 61 controls.

    D4's breast heads are not affected: HEST's min-cells filter leaves 90 common genes, and no control
    appears in any breast selection. The lung definition excludes controls. Source:
    `results/round4/data/P6_genes/p6_lead_verification.md`. **Proposed** (edit 4): the tracks read
    Xenium panels without controls.
11. **Disease is not fixed across the lung task.** The 19 samples are IPF, control lung, sarcoidosis,
    IPAF, ILD not specified, cHP and CTD-ILD. A lung task holds organ, instrument and preservation
    fixed, and does not hold disease fixed. Source: `results/round4/data/P4_audit/p4_notes.md`,
    section 8.
12. **`TENX141` is unreadable.** The 10x page returns HTTP 429 behind a bot challenge, so its donor
    and laboratory are `unverifiable`. Source: `results/round4/data/P4_audit/p4_notes.md`, section 1.
13. **P2's time limit was not sized by the literal rule.** The instruction says three times the
    per-sample D2 actual times 24. On the three breast samples D2 encoded, that is 7,366 s from the
    mean and 9,338 s from the slowest. The track set 1 h from the measured rate instead. The slowest
    job ran 00:11:11. Both figures are recorded in `results/round4/data/P2_embeddings/PROVENANCE.txt`.
    Source for the D2 figures: `results/round3/D2_embeddings/d2_extraction__institution_breast_xenium__hoptimus0.csv`.
14. **Set V's download job reached its memory request.** `2751561` recorded MaxRSS 16777920K against
    16G and completed with exit 0, so its true peak is unknown. A rerun should ask for more. Source:
    `results/round4/data/P7_report/stageP_sacct.csv`.
15. **Job names.** The `r4data_` prefix could not be applied because the submission route replaces
    `--job-name`. Jobs are identified by Slurm id throughout.
16. **The P3 provenance carries the lead's frame id.** `frame_id` in the P3 provenance records is
    this session's, not the Morphology sub-agent's, so `whose()` attributes those directories to the
    lead session. Source: `results/round4/data/P3_morphology/PROVENANCE__p3_expand.txt`.
17. **A track's claim corrected.** The transfer track reported that P2's provenance recorded
    `e00d9bd`, disagreeing with `71451d7`. It does not. Every P2 record carries `71451d7`, and the
    working copy is at that commit. Source: `results/round4/data/P1_download/p1_p2_lead_verification.md`.
18. **`rc_tengfei_pi` is available** for GPU work, with the same limits as rc_htzhu_pi. Source:
    `results/round4/data/P7_report/accounts_at_report.txt`.
19. **The numeric-claim gate.** It was run in its `docs/WAYS_OF_WORKING.md` form, both invocations
    over README and every document, on the synced Longleaf working copy at `a6d5d44` (job `2812030`).
    - Every claim in this report and in `docs/round04/tracks/data/round4_data_plan.md` resolves.
    - The deck outline invocation resolves every claim.
    - The main invocation leaves 10 claims unresolved: 5 in `docs/round02/tracks/deck/deck_speaker_scripts.md` and 5 in
      `docs/round00/first_year_ST_project_proposal.md`.

    Both documents entered at `80f1ae5`, which precedes the round-3 tag. Stage P changed no file
    outside round-4 paths, so the 10 predate this stage. Round 3's gate covered README and the round-3
    documents only, which is why they were not seen. They are not fixed here, because those
    documents are outside stage P. **For the oversight chat.** Source:
    `results/round4/data/P7_report/gate_main.tsv`, `results/round4/data/P7_report/gate_deck.tsv`,
    `results/round4/data/P7_report/report_numbers.csv`.

**Proposed edits**, not applied:
1. `round3_d1_download.py`'s patch-count test is stale. Patch count need not equal spot count, and the
   test should be replaced by the subset relation that the round-4 scripts use (the P1 decision, item 6).
2. `round3_d4_probe.py`: the docstring and the `patch_geometry` fallback should use half the patch
   extent (escalation 3).
3. A v2 of `results/round3/D4_expansion/task_defs/task_def_ext.schema.json` that:
   - adds `expansion_r4` to `donor_label_status_row_origin`;
   - adds a per-sample `slide_id`;
   - adds an `a4b_k10` fold key, so that K = 10 lists need not sit in the free-form `expansion` block.
4. Xenium panel tables and target lists should drop the `NegControl`, `UnassignedCodeword` and `BLANK`
   features (escalation 10).
5. `code/scripts/morphology_features.py` has no functions and skips existing outputs, so it cannot
   be called as a library. P3 imported it for its constants and transcribed its per-sample body
   verbatim (commit `3048f83`). Moving that body into a function behind a guarded `main` would let
   later stages call it.

**Proposed index entries for `docs/README.md`:**
- `docs/round04/tracks/data/round4_data_plan.md`: round 4 stage P, the transcription of the data-pull instruction and the
  P1 decision.
- `docs/round04/i01/data/round4_data_report.md`: round 4 stage P, the data-pull report and gate (tag `round4-data`).
- `docs/round04/i01/data/round4_data_pull.md` and `docs/round04/i01/data/round4_data_P1_decision.md`: the
  instruction and the oversight chat's P1 decision.

## 8. What was not checked

- Whether any lung patch at a core's edge contains a neighbouring donor's tissue (escalation 6). This
  needs the patch coordinates set against the core geometry.
- Embedding values. Only rows, dimensions, dtypes and barcodes were checked. The two benchmark LUNG
  samples, downloaded again in the HEST-1k layout, were not compared with their benchmark copies.
- Set V's rows. Set V is neither audited nor embedded, and its 24 uncertain-pixel-size flags were not
  checked against anything.
- Gene measurability. Presence means membership in `var_names`, so a gene that is present but all
  zero on a sample is not told apart from one that is measured.
- Whether the `NCBI865` gap has any other consequence, or what causes it.
- `round3_d1_download.py` was not run on sets L and V. The equivalence of `round4_data_download.py`
  to it rests on reading the code.
- Presence in P6 was not recomputed by the lead, because the h5ad files are on Longleaf. The lead
  checked the lists themselves.

## 9. Proposed next step

None. The two track sessions, PPI and conformal, start from the tag `round4-data` once the oversight
chat accepts this report, and their documents follow.
