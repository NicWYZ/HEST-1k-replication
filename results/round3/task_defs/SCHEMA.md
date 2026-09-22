# Round-3 task-definition schema, version 1

Fixed by the lead session on 2026-09-22, before the A0 harness and the task-definition files were
written, so that the two could be built in parallel against the same contract. Machine-readable
version: `task_def.schema.json` in this directory.

A task is a file, not a name. `code/scripts/round3_a0_harness.py` takes `--task-def <file>` and may
assume nothing about the benchmark's directory layout beyond what the file states. The ten benchmark
tasks are written here in S0; track D's expansion sets become further files of the same shape, which
is the whole point of the indirection.

## One file per (task, label set)

IDC is run under both the shipped four-patient labels and the audited three-donor labels, per the
round-3 handoff § 4, so it gets two files: `IDC.json` with `label_set: "shipped"` and
`IDC_audited.json` with `label_set: "audited"`. Every other benchmark task gets one file whose
`label_set` is `"shipped"`, with `donor_id` carried from the audit regardless. This is the execution
session's choice of file layout, not an instruction.

## Fields

| field | type | meaning |
|---|---|---|
| `task_def_version` | int | `1` for this schema |
| `task` | string | task name, e.g. `PRAD`; matches the results directory naming |
| `label_set` | string | `shipped` or `audited` |
| `source` | string | `hest_bench` for the ten benchmark tasks, `hest_ext` for expansion sets |
| `st_technology` | string | `Visium` or `Xenium` |
| `repo_root_relative` | bool | `true`; every path below is relative to the project root on Longleaf, `/work/users/w/e/weiyang/hest_replication` |
| `paths` | object | templates with `{sample_id}` and `{encoder}` placeholders: `adata`, `patches`, `embeddings`, `target_genes` |
| `target_genes` | object | `list` (the gene symbols, in file order), `n`, `selection` (prose describing how the list was chosen), `selection_used_test_spots` (bool) |
| `samples` | array | one object per sample, fields below |
| `flags` | object | the § 4 task-level flags: `patient_labels_unreliable`, `same_specimen_pairs`, `idc_attribution_unresolved`, each a bool |
| `folds` | object | one key per design, contents below |
| `provenance` | object | `generated_by`, `generated_at`, `commit`, `inputs` (list of source file paths), `pythonhashseed` |

### `samples[]`

| field | type | meaning |
|---|---|---|
| `sample_id` | string | e.g. `MEND139` |
| `donor_id` | string | from `results/round2/R5b_audit/donor_audit.csv`, never from HEST's `patient` |
| `hest_patient` | string or null | HEST's own label, carried for traceability only, never grouped on |
| `donor_label_status` | string | `verified`, `unverifiable` or `contradicted`, from the audit |
| `lab` | string | generating laboratory or cohort source |
| `lab_label_status` | string | `unverified` for every benchmark sample: the benchmark's lab field has never been audited, and D3 is the stage that audits it. Do not write `verified` here |
| `session` | string or null | non-null only where a session contrast exists inside one donor, which in the benchmark is PRAD patient 2 alone |
| `resolution_group` | string | from `sample_metadata.csv` |
| `pixel_size_um` | float | from `sample_metadata.csv` |
| `resolution_uncertain` | bool | from `sample_metadata.csv` |
| `n_spots` | int | spots under tissue, read from the AnnData rather than copied from metadata |

### `folds`

- `patient`: array of `{fold, train: [sample_id], test: [sample_id]}`, transcribed from
  `bench_data/<task>/splits/train_<k>.csv` and `test_<k>.csv`. `fold` is a **string**, because the
  `slide_out` design's fold ids are slide names and the per-gene parquet holds one column for both.
  This is the R3 defect that killed three completed jobs at the final write.
- `donor`: array of the same shape, leave-one-donor-out by `donor_id`. `fold` is the held-out
  `donor_id`.
- `slide_out`: array of the same shape, one fold per slide, present only on the multi-slide tasks.
  Empty array where the task has one slide per donor and the design is not defined.
- `random`: object `{n_repeats, test_size_from_fold, seed_source}`. The test set is drawn at runtime
  by the harness, not enumerated here, since it is a random draw of the shipped fold's test size over
  all spots of the task.

`calibration_unit` is deliberately **not** in this file. It is decided per fold by the harness's
calibration-unit rule from the pool composition, and recorded in the harness output, because which
folds could calibrate at donor level is itself a result.

## Rules

1. Every value is read from a file and the file is named in `provenance.inputs`. Nothing is typed
   from memory, including gene lists and fold membership.
2. `donor_id` is the grouping variable. `hest_patient` is carried but never grouped on.
3. A sample missing from the audit is written with `donor_label_status: "unverifiable"` and a null
   `donor_id`, and the generator fails loudly rather than inventing one.
4. Gene lists are written in the order the source file gives them, so a downstream index is stable.
5. The generator is deterministic and reruns byte-identically, seeds from `zlib.crc32`.
