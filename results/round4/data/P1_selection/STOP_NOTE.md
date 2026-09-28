# P1 stop-and-report, 28 September 2026

`code/scripts/round4_data_select.py` exited non-zero before any download, under the decision boundary
in `docs/round4_data_plan.md` section 5: set V's count is outside its predicted range by more than a
factor of two. Nothing has been downloaded, and no other stage has started. The only job submitted
is P0's environment check, which downloads nothing.

| set | selected | predicted | within a factor of two |
|---|---|---|---|
| L, lung Xenium | 24 samples, 21 provisional donor keys | 24 samples, 21 keys | yes |
| V, donor-labelled Visium and Xenium | 39 samples, 28 provisional donor keys, 18.98 GB | 150 to 250 samples, under 150 GB | no (below 75) |

From `results/round4/data/P1_selection/selection_summary.json` and `selection.csv`.

How the 39 arise from the rule as written, applied to `results/round3/D0_inventory/hest_inventory.csv`:

| step | samples left |
|---|---|
| human | 689 |
| technology exactly Visium or Xenium | 494 |
| patient label usable (`labelled`) | 172 |
| not a duplicate | 172 |
| not in `bench_data/` (71 removed) | 101 |
| not in `hest_ext/` (42 removed) | 59 |
| not in set L (20 removed) | 39 |

The rule is applied as written, so this reads as a prediction that did not anticipate how much of
the archive's labelled Visium and Xenium is already on disk. It is not a selection bug. Two other
readings reach the predicted range:
- Dropping the technology restriction gives 143 samples not on disk and not in set L, of which 104
  are the older Spatial Transcriptomics platform.
- Dropping the label requirement gives 338, of which 185 have no label and 114 a whitespace-only
  label.

The rule excludes both explicitly, so neither is applied. Set V's 39 are 14 bowel, 14 brain,
6 bladder, 3 breast and 2 lymphoid samples, 34 Visium and 5 Xenium, from nine dataset titles, with
24 carrying an uncertain pixel size. The inventory holds no donor-labelled `Xenium 5k` sample, so
plan section 7 item 4 does not arise.

Set L is inside its prediction. Its selection also shows plan section 7 items 1 to 3:
- two benchmark LUNG samples;
- two samples without a patient label;
- four estimated pixel sizes (0.2125, 0.2517, 0.2736, 0.2739), all with the resolution flag clear;
- four dataset titles.

Decision needed from the oversight chat before P1 downloads anything:
1. Proceed with set V as selected (39 samples, 19 GB) and set L (24 samples, 9.4 GB).
2. Change set V's rule, for example to include Spatial Transcriptomics.
3. Download set L only.

## P0 environment check (job 2723647, `l40-gpu`, node g181009), completed after this note was first written

Round 3's `round3_d1_download.py` (md5 `4cbb8b9b3417b6e31daf80638915127e`) and `round3_d2_embed.py` (md5
`3b9e47a045993bc2bd38790466486178`) ran unchanged on one existing sample, NCBI692, in a scratch tree
that links to the real files (`results/round4/data/P0_setup/`).
- D1 found 5 of 5 files present at their listed sizes, with 0 size mismatches. HuggingFace `main` is
  still the pinned revision `7e8d5a0b0aace41d8c8ec0f6ecea80e4ad2a61ec`, so P1 has no newer release to
  handle.
- The script prints "FAILURES PRESENT" only because of its old patch-count-equals-spot-count test (357
  patches against 370 spots). Round 3 replaced that test with the subset relation.
- D2 loaded resnet50 at float32 on an NVIDIA L40S and read the sample as cached, with 357 rows.
- The three linked files were still links after the run, so no real file was written.
