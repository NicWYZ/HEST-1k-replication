# H0 item 3: where COAD TENX111's 6,643 comes from, against the AnnData's 6,138

One hour, as the A1 decision memo allows. The hour settled it. The cause is the one the memo named
as likely, and it is now measured rather than guessed: **6,643 is the pseudo-Visium grid before the
under-tissue filter and 6,138 is the grid after it**, and `TENX111` is the only benchmark sample
where HEST published the pre-filter number.

## The two values, and where each is written

- **6,643** is HEST's own `spots_under_tissue` for `TENX111`. It is byte-identical in
  `results/round3/D0_inventory/release_tables/HEST_v1_1_0.csv` and `HEST_v1_3_0.csv`, so it has
  not been revised across releases. `results/tailored/integrity/sample_metadata.csv` carries 6,643
  in its own `spots_under_tissue` column because that column was copied from HEST's table.
- **6,138** is the row count of the AnnData the benchmark ships,
  `bench_data/COAD/adata/TENX111.h5ad`, read directly (Slurm job 2126477 on `spill`, node
  c151606). It is the value in `bench_data/hest_bench_sample_inventory.csv` and the value every
  task file, split and result in this repository uses.

## What settles it

The AnnData carries the pseudo-Visium grid indices, `array_col` and `array_row`, and an `in_tissue`
column. For `TENX111`, `in_tissue` is `True` on all 6,138 rows, no barcode is duplicated, and no
spot has zero counts, so the file is already the filtered set rather than a set with a filter
column to apply. Its grid indices run 0 to 72 in the column direction and 0 to 90 in the row
direction, a rectangle of 73 by 91 positions, and 73 times 91 is **6,643** exactly. 505 of those
positions are absent from the file.

That identity is not a coincidence of one sample. Job 2129588 (`spill`, node c151406) read the grid
indices of all 19 samples in six benchmark tasks (COAD, IDC, READ, PAAD, LUNG, SKCM) and compared
three numbers per sample: the AnnData row count, HEST's published `spots_under_tissue`, and the size
of the bounding rectangle of the grid indices.

| task | sample | AnnData rows | HEST `spots_under_tissue` | grid rectangle | rows = HEST | rectangle = HEST |
|---|---|---|---|---|---|---|
| COAD | TENX111 | 6,138 | 6,643 | 73 x 91 = 6,643 | no | **yes** |
| COAD | TENX147 | 3,997 | 3,997 | 62 x 69 = 4,278 | yes | no |
| COAD | TENX148 | 4,379 | 4,379 | 73 x 67 = 4,891 | yes | no |
| COAD | TENX149 | 4,009 | 4,009 | 73 x 67 = 4,891 | yes | no |
| READ | ZEN36 | 1,691 | 1,691 | 94 x 53 = 4,982 | yes | no |
| LUNG | TENX118 | 3,115 | 3,115 | 37 x 109 = 4,033 | yes | no |

The remaining thirteen samples read (IDC's four, PAAD's three, READ's other three, LUNG TENX141,
SKCM's two) all have rows equal to HEST's value; in eight of them the tissue fills the rectangle
so all three numbers coincide, which is why the test needs the sparse samples to be informative.
The full table is `grid_check.txt` in the job output.

So on every sample except this one, HEST's published figure is the count of grid positions kept
after the under-tissue filter. On `TENX111` it is the count before the filter. Read across all 72
benchmark samples rather than the 19 whose grids were read, the AnnData row count equals HEST's
`spots_under_tissue` for 71 of 72; `TENX111` is the single exception
(`bench_data/hest_bench_sample_inventory.csv` against
`results/round3/D0_inventory/release_tables/HEST_v1_3_0.csv`).

## Two readings that were tested and do not hold

- **A convention difference between HEST's pseudo-Visium gridding and its metadata.** If the
  published figure counted the grid and the AnnData counted retained spots as a matter of
  convention, every sparse sample would disagree. Ten of the samples read have a rectangle
  substantially larger than their row count, up to 4,517 positions larger on READ ZEN48, and all
  ten publish the row count. The difference is specific to `TENX111`, not systematic.
- **The pixel-size discrepancy.** `TENX111` is also the sample whose embedded pixel size, 0.2125,
  disagrees with its estimated 0.2738 by 22.4 per cent, and it is flagged `resolution_uncertain`
  (`results/tailored/integrity/sample_metadata.csv`). A grid pitched in pixels by the wrong scale
  would change the spot count by the square of that ratio, about 0.60, where the observed ratio of
  6,138 to 6,643 is 0.924. The pixel-size flag does not explain this gap, and the measured grid
  pitch in the file, about 365 px, is the one implied by the estimated pixel size at the 100 µm
  pseudo-Visium pitch.

## What this does not establish

The mechanism inside HEST's ingestion is not observed, only its output. What is established is that
the published figure for this sample is the pre-filter grid count and the shipped file is the
post-filter set. Why this one sample was recorded before the filter is not in any file reached here
and would need HEST's ingestion code or its issue tracker; the value being identical in v1.1.0 and
v1.3.0 says only that it was never refreshed. Nothing was reported upstream from this track.

No result in this repository is affected: every task file and every computed result uses the
AnnData's 6,138 rows. The stale figure sits in `sample_metadata.csv`'s `spots_under_tissue` column,
which is descriptive metadata copied from HEST, and README known limitation 13 now records both
values.
