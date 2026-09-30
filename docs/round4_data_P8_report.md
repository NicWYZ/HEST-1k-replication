# Round 4, stage P8: the addendum, report

Instruction: `docs/decisions/round4_data_P7_decisions.md` section 3, transcribed with its decisions
as section 9 of `docs/round4_data_plan.md`. Format: `docs/decisions/round4_data_pull.md` section 8.
Run on `main` from tag `round4-data`. Date: 30 September 2026.

## 1. Stage and status

P8 is complete: all six items are done and this report is the sixth. It stops here, at tag
`round4-data-v2`. Nothing under `results/round4/data/P1_*` to `P7_*` was changed except the two
files the memo names, `results/round4/data/P5_task/LUNG_XENIUM.json` and `p5_validation.csv`,
which were rewritten with their previous versions kept beside them. No download, embedding or GPU
job ran.

The lung task is now **20 samples and 15 donors**, with `NCBI865` reinstated by dropping its one
patch barcode that has no expression row. Source: `results/round4/data/P5_task/p5_validation.csv`.

One sequencing point is on the record. The Longleaf check for item 1 was submitted before Nicolas
had approved the P8 operating plan. It was read-only apart from its own directory, and none of its
output was used until the plan was approved.

## 2. What was run

Commits on `main`, in order:
- `331b8cc`: the memo and the plan's section 9;
- `7a12217`: items 1 and 2, the lung task and schema v2;
- `4b6ba8f`: item 3, the control-free panels;
- `06eb328`: item 4, the probe correction;
- `9da3ba1`: item 4, the D1 correction;
- then the commit carrying this report and the index.

Scripts and the md5 of the committed file:

| item | script | md5 |
|---|---|---|
| 1 | `code/scripts/round4_data_p8_task_lung.py` | `4c0162247f1f79193bc6126a8dfa7e20` |
| 1, 5 | `code/scripts/round4_data_p8_longleaf.py` | `a782962d84f0dadf44dccd8c3d006a58` |
| 2 | `code/scripts/round4_data_p8_schema_v2.py` | `3f79c411911f8a5f13ad026ff7ccdb71` |
| 3 | `code/scripts/round4_data_p8_panels.py` | `09f774f1943bcd3eff13c178ddda154e` |
| 4 | `code/scripts/round3_d4_probe.py` (corrected, not run) | `3cee345b360dd9d42f8c5038e9fc5802` |
| 4 | `code/scripts/round3_d1_download.py` (corrected, not run) | `c8c6db1efd77404fa4b89c307c46d72b` |
| 6 | `code/scripts/round4_data_p8_report_numbers.py` | `e171cb5ee1ce43c5d5cf14b24f807494` |

Jobs. Both ran on rc_htzhu_pi and landed on spill. Source: `results/round4/data/P8_addendum/p8_sacct.csv`.

| job | purpose | node | elapsed | limit | ReqMem | MaxRSS |
|---|---|---|---|---|---|---|
| `3041866` | subset check and edge diagnostic, first run | c151409 | 00:00:55 | 00:30:00 | 16G | 279872K |
| `3042053` | the same, adding each sample's source core size | c151415 | 00:00:52 | 00:30:00 | 16G | 292324K |

The second run's script (`a782962d…`) differs from the first (`5e31875e…`) only by the added
source-core columns. Its subset table is byte-identical to the first run's, and the memo's columns
of its edge table are identical to the first run's. The committed outputs are the second run's.
The first run's provenance is kept as `results/round4/data/P8_addendum/PROVENANCE__run1_3041866.txt`.
Both jobs recorded the Longleaf working copy at `2905525` (`round4-data`), because the P8 commits
had not yet been pushed. Their script and config were staged into the job directory, and the
committed copies have the md5s the jobs recorded. Source: `results/round4/data/P8_addendum/PROVENANCE.txt`.

## 3. Acceptance checks

**Item 1, the lung task.** The memo's acceptance values are 20 samples, 15 donor units, 15 donor
folds, 45 `a4b_k10` rows, a minimum of 4 training donors, and the subset relation holding on every
sample after the drop. The file gives exactly these:
- 20 samples and 15 donor units;
- 15 donor folds and 6 patient folds;
- 45 `a4b_k10` rows, with a pool of 14 donors and a minimum of 4 training donors;
- 343 target genes out of 541 features.

The folds cover every sample and are disjoint. Source: `results/round4/data/P5_task/p5_validation.csv`.

The subset relation holds on 20 of 20 samples after the drop. `NCBI865` had 1 patch barcode
without an expression row before the drop and 0 after, keeping 2,142 of its 2,143 patches. No
other sample had any. Source: `results/round4/data/P8_addendum/p8_subset_after_drop.csv`.

The lung file passes relaxed v1 and schema v2. As intended, it fails v1 strict (the extension
fields) and the committed extension schema v1 (the `expansion_r4` row origin and the v2 fields).
Source: `results/round4/data/P5_task/p5_validation.csv`.

Round 3's own `round3_d4_sets.a4b_specs`, run on the new file, gives calibration and training sets
identical to `folds.a4b_k10` on all 45 rows. The copy under `expansion.a4b_k10` is asserted
identical. Source: `results/round4/data/P8_addendum/p8_task_crosscheck.txt`.

**Item 2, schema v2.** `results/round3/D4_expansion/task_defs/task_def_ext.schema.v2.json` is v1
plus four optional additions:
- the `expansion_r4` row origin;
- a per-sample `slide_id`;
- `folds.a4b_k10`;
- a top-level `dropped_patch_barcodes`.

The v1 file is unchanged. Round 3's four D4 definitions validate against both v1 and v2 with no
errors. Source: `results/round4/data/P8_addendum/p8_task_crosscheck.txt`.

**Item 3, control features.** The memo expected 61 controls dropped on five sets and 220 on IDC,
and the table gives exactly that. On every set the controls are 41 NegControlCodeword and 20
NegControlProbe features; IDC's 220 add 159 BLANK codewords. No intersection contains an
UnassignedCodeword feature. Source: `results/round4/data/P8_addendum/xenium_panels_genes_only.csv`.

**Item 4, code corrections.** The probe's fallback now returns half the patch extent. On the 30
Indiana rows, the old formula reproduces D4's recorded half-width exactly, and the corrected one
reproduces P3's half-width, taken from the patch downsample attribute, exactly. The ratio between
them is 2.0 on every row. D1's acceptance test is now the subset relation.

D1 has no self-test, because it downloads on import. It compiles, and its verification functions,
run on synthetic files, accept a valid sample that the stale test rejects and reject a patch
barcode missing from the expression file. Source: `results/round4/data/P8_addendum/p8_code_corrections.txt`.

**Item 5.** `results/round4/data/P8_addendum/lung_edge_patches.csv` has one row for each of the 20
lung samples, with the columns the memo names (section 6).

## 4. What differs between arms

There are no experimental arms here. What differs between the lung definition at `round4-data` and
the one at `round4-data-v2`:
1. `NCBI865` is a member, with `dropped_patch_barcodes`, so there are 20 samples and 15 donors
   instead of 19 and 14.
2. The donor, patient and `a4b_k10` folds are regenerated over 15 donors. `random` keeps its
   parameters.
3. `a4b_k10` lives canonically under `folds`, with a copy under `expansion`.
4. Each sample row gains `slide_id`.
5. `expansion` gains the source core diameters, and core diameter joins the donor difference list.

Nothing else on the 19 samples that both files share changed: the only sample key that differs is
the added `slide_id`, and the target genes are identical. Source:
`results/round4/data/P8_addendum/p8_task_crosscheck.txt`.

## 5. Expected values against outcomes

P8 carries no new predictions. The memo's expected values are scored instead.

| item | expected | outcome | held |
|---|---|---|---|
| 1 | 20 samples, 15 donors, 15 donor folds, 45 `a4b_k10` rows, 4 training donors at minimum | 20, 15, 15, 45, 4 | yes |
| 1 | the subset relation on every sample after the drop | 20 of 20 | yes |
| 3 | 61 controls on five sets, 220 on IDC | 61 on PAAD, SKCM, COAD, LUNG and BREAST_XENIUM; 220 on IDC | yes |

Sources: `results/round4/data/P5_task/p5_validation.csv`,
`results/round4/data/P8_addendum/p8_subset_after_drop.csv`,
`results/round4/data/P8_addendum/xenium_panels_genes_only.csv`.

## 6. Results

**Control-free panels.** Genes left after dropping controls:

| set | genes |
|---|---|
| IDC | 280 |
| PAAD | 98 |
| SKCM | 282 |
| COAD | 351 |
| LUNG (benchmark) | 198 |
| BREAST_XENIUM | 90 |

The breast row is round 3's `BREAST_XENIUM.json` target list with its controls filtered out.
Source: `results/round4/data/P8_addendum/xenium_panels_genes_only.csv`. The lung task's own panel,
343 genes, was control-free from P5.

**Edge-patch diagnostic** (report only; nothing is excluded). The memo's measure is the fraction of
patch centres more than 1.6 mm from the mean patch centre. Over the 20 samples it has a median of
0.105743 (mean 0.200531, sd 0.231908, min 0.000000, max 0.679952), and 10 samples exceed 0.10.
Source: `results/round4/data/P8_addendum/p8_report_numbers.csv`.

That threshold assumes a 3 mm core, and 4 of the 20 are 5 mm cores (section 7, item 1). Beside
it, the table gives each sample's fraction beyond its own core radius plus 0.1 mm. That measure
has a median of 0.067286 (mean 0.096754, sd 0.089898, max 0.308901), and 8 samples exceed 0.10.
- The 16 samples with 3 mm cores have the same median, 0.062217, on both measures.
- For the 4 samples with 5 mm cores, the median falls from 0.619568 to 0.081103.

Source: `results/round4/data/P8_addendum/p8_report_numbers.csv`.

The largest fractions on 3 mm cores are:

| sample | fraction beyond 1.6 mm | furthest patch centre (mm) |
|---|---|---|
| `NCBI857` | 0.308901 | 1.9652 |
| `NCBI866` | 0.284698 | 2.0175 |
| `NCBI882` | 0.186992 | 1.8826 |
| `NCBI856` | 0.178458 | 1.9300 |

HEST's rectangles for these four are 3.641 to 4.243 mm wide. Source:
`results/round4/data/P8_addendum/lung_edge_patches.csv`.

## 7. Discrepancies, open questions and escalations

1. **Four lung samples are 5 mm cores, not 3 mm.** `NCBI864`, `NCBI865`, `NCBI867` and `NCBI884`
   carry `_5mm` in their GEO titles (TMA3), and the other 16 carry `_3mm`. The memo's 1.6 mm
   threshold and 3 mm core are right for the 16 and wrong for the 4. On the memo's measure those 4
   read 0.548698 to 0.679952 beyond 1.6 mm, which reflects the size of their cores and says
   nothing about neighbouring tissue.

   The memo's columns are reported unchanged, and the source-based columns sit beside them. The
   core size is now recorded per sample in the lung task, under `expansion.core_diameter_mm_source`,
   and core diameter is on the donor difference list. Source:
   `results/round4/data/P8_addendum/lung_edge_patches.csv`.
2. **The radial measure is coarse.** Even against the correct core size, 8 samples have more than
   0.10 of their patch centres beyond radius plus 0.1 mm. A centroid-and-radius test cannot tell
   a patch that reaches a neighbouring core from one on tissue that is not a centred disc, which is
   the case for a core that is torn, folded or off-centre in its rectangle. Settling it needs the
   TMA core geometry or the image. Report only, as the memo says, and nothing is excluded. Source:
   `results/round4/data/P8_addendum/p8_report_numbers.csv`.
3. **The dropped patch at read time.** The task file records the drop, and the embedding files are
   unchanged, so `NCBI865`'s embedding file still has 2,143 rows. A reader must exclude
   `051x019` by barcode, as `expansion.reinstated` states. Round 3's `round3_d4_sets.load_set`
   asserts the subset relation on the embedding file's barcodes, so a round-3 loader reading
   `NCBI865` without applying the drop list would still raise. The tracks need to apply the drop
   list before that check. Source: `code/scripts/round3_d4_sets.py`.
4. **Longleaf ran against `round4-data`.** The P8 jobs recorded commit `2905525` because the P8
   commits were pushed afterwards. Their inputs were the staged script and config, whose md5s match
   the committed copies (section 2), and the data files, which P8 did not change.
5. **Approval order** (section 1). The item 1 check was submitted before the plan was approved. It
   changed nothing outside its job directory.
6. **Proposed, not applied:** a note in `docs/WAYS_OF_WORKING.md` that a task file's
   `dropped_patch_barcodes` is applied before any subset assertion. The two tracks' documents are
   the oversight chat's to update.

## 8. What was not checked

- No reader was run against the new lung file, so exclusion of `051x019` at read time is recorded
  but not exercised (item 3 above).
- The D4 probe was not rerun, so the quarantined 31% to 34% statement is neither confirmed nor
  replaced.
- `round3_d1_download.py` was not run on data.
- The edge diagnostic uses patch centres only, not the image, the nuclei or the TMA layout.
- `UnassignedCodeword` features were not found in any intersection. The lung task's 541 features
  include 137 of them, which P5 already excluded along with its 41 NegControlCodeword and 20
  NegControlProbe features. Source: `results/round4/data/P8_addendum/p8_report_numbers.csv`.

## 9. Proposed next step

None. The two round-4 tracks start from tag `round4-data-v2`.
