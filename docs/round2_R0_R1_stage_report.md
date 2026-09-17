# Round 2, stages R0 and R1 — stage report

*17 September 2026. Execution session for `NicWYZ/HEST-1k-replication`. Reporting format follows
section 13 of the round-2 execution plan. R1 is a report-and-wait boundary, so this report covers
everything done since the plan was approved.*

**Repository:** `NicWYZ/HEST-1k-replication`, branch `main`, commit **`145ba91`** ("Round 2 R0:
scan-resolution columns, README relabelling"), parent `eb670fa`.

---

## 1. Stage and status

| stage | status |
|---|---|
| R0 · housekeeping and relabelling | **complete**, committed and pushed |
| R1 · intercept refit | **complete on 11 of 12 encoders**; `conch_v15` still queued |
| R1 acceptance | **three of four checks FAIL as written.** The cause is established and is numerical, not a pipeline difference. Details in § 3. Report-and-wait triggered. |

Two things need a decision from the oversight chat before R2 starts. Both are in § 5.

`conch_v15` is not a failure: its job hit a 50-minute wall while sharing the job with `conch_v1`,
and the rerun has been sitting in `PENDING (Priority)` for about 100 minutes. Diagnosis in § 5.4.
Every number below is over the 11 encoders that completed, and every per-encoder table shows a
spread small enough that the twelfth cannot move a conclusion: the median-$R^2$ result holds in
11/11 encoders and the across-encoder standard deviation is 0.055.

---

## 2. What was run

**Scripts** (both new, both committed):

| script | stage |
|---|---|
| `code/scripts/round2_r0_resolution_columns.py` | R0 item 2 |
| `code/scripts/round2_head_intercept.py` | R1 |

**Jobs** (all CPU-only, partition `spill`, no GPU time):

| stage | Slurm job | encoders | wall |
|---|---|---|---|
| R0 | `1381177` (node c0312) | — | 7 min |
| R1 | `1387525` | hoptimus0, resnet50 | < 50 min |
| R1 | `1387530` | hoptimus1, uni_v2 | < 50 min |
| R1 | `1387548` | virchow, virchow2 | < 50 min |
| R1 | `1387549` | gigapath, uni_v1 | < 50 min |
| R1 | `1387550` | conch_v1 (+ conch_v15 killed at wall) | 50 min, exit 143 |
| R1 | `1387551` | phikon, ctranspath | < 50 min |
| R1 | `1408698` | conch_v15 | **still PENDING** |

Three earlier R1 submissions (`1381730`, `1381735`, `1381736`) ran to completion but were
discarded: they predate the fix described in § 3.1, and their outputs were deleted before the
rerun so a partial set could not be mistaken for a complete one.

**Outputs.** `results/round2/R0_resolution/` and `results/round2/R1_intercept/`, each with
`PROVENANCE.txt` carrying job ID, partition, node, commit, date, bin definitions and command line.
Prediction shards in `instrumentation/round2_intercept/<task>/preds__<encoder>.parquet`, 1.6 GB,
11 encoders × 236,495 spots × 50 genes × 2 heads = 260,144,500 rows.

Sharding per encoder rather than appending to one per-task file is a deviation from the plan's
wording ("a new prediction parquet per task") and was made so that concurrent encoder jobs cannot
corrupt a shared file. The shards form one per-task dataset and carry the round-1 join keys
`(task, encoder, fold, sample_id, barcode, gene)` plus `head`, so they join to round 1 as specified.

---

## 3. Acceptance checks, with the actual numbers

### 3.1 One code defect, found and fixed

The first R1 run wrote every per-encoder CSV and then died with `KeyError: False` in the
faithful-comparison block. `d.head` resolves to the pandas `DataFrame.head` *method*, not the
`head` column, so `d[d.head == "nointercept"]` reduced to `d[False]`. It raised, so it was not
silent, and no output was affected — but the same expression appeared three times and would have
been silent had it been used in a mask that happened to be valid. All occurrences are now
`d["head"]`. The run was repeated from scratch.

### 3.2 The acceptance thresholds as written

Source: `results/round2/R1_intercept/acceptance__<encoder>.csv`, worst case over the 11 encoders.

| check | threshold | `lsqr` (faithful head) | `cholesky` (exact solve) |
|---|---|---|---|
| A1 max abs ΔPearson (intercept − nointercept) | 1e-6 | 3.15e-02 **FAIL** | 5.54e-05 **FAIL** |
| A2 max abs pred(intercept) − pred(ycentered) | 1e-4 | 6.19e-02 **FAIL** | 9.54e-06 **PASS** |
| A2b max abs (intercept − nointercept) − ȳ_train | 1e-4 | 4.61e-01 **FAIL** | 2.69e-03 **FAIL** |
| A3 max abs (train mean pred − train mean target) | 1e-6 | 3.690e-04 **FAIL** | 3.690e-04 **FAIL** |
| A4 fold-median R² positive in a large majority of folds | — | 95 of 319 encoder-folds (29.8%) **FAIL** | 95 of 319 **FAIL** |
| A5 nointercept reproduces round-1 faithful `pca_ridge` | < 1e-3 | **PASS**, max abs diff 3.73e-04 over 110 cells | — |

A2b and A5 are additions, not in the plan. A5 is the check that actually establishes pipeline
identity and is described in § 3.5; A2b tests the algebraic prediction in § 3.3.

### 3.3 Why A1, A2, A2b and A3 fail, and why it is not a pipeline difference

The three heads are **algebraically identical up to a constant per gene**, which the plan's
thresholds implicitly assume. Proof: PCA centres the training features, so `X'1 = 0`. With
`fit_intercept=True` the ridge coefficient solves the y-centred problem,

    w_int = w_noint − (X'X + αI)⁻¹ X' ȳ 1,

and `X'1 = 0` annihilates the second term. So `w_int = w_noint` exactly and `b = ȳ_train`. Hence
`pred(intercept) = pred(nointercept) + ȳ_train`, a per-gene shift; Pearson is invariant to it; and
`ycentered` is that same expression written a third way. Nothing in the three heads should differ
beyond the shift.

Three pieces of evidence establish that the observed deviations are floating-point, and specifically
the **float32 dtype of the faithful pipeline**, not solver choice and not a pipeline difference:

1. **A3 is identical to four significant figures across the two solvers** — 3.690e-04 under `lsqr`
   and 3.690e-04 under `cholesky`. A quantity that does not move when the solver is replaced by an
   exact one is not a solver-tolerance quantity.
2. **The worst A3 cell is the same (fold, gene) for every encoder.** IDC fold 2, gene `AQP3`,
   n_train = 31,526: 3.66e-04 to 3.68e-04 across all of hoptimus0, hoptimus1, uni_v2, virchow and
   gigapath. The error is set by the target vector and the fold size, not by the features — which
   is what an accumulation floor looks like and is not what a model property looks like.
   The error also grows with fold size, Spearman(A3, n_train) = 0.648.
3. **A matched synthetic float32/float64 comparison** (n = 36,819, d = 256, 50 targets, the shape of
   PRAD fold 0, exact solver) gives A3 = 7.9e-06 in float32 against 1.6e-14 in float64, and
   ΔPearson 1.8e-07 against 3.3e-16. Repeating it with column-scale ratios of 1, 60, 600 and 6,000
   moves float32 A3 only between 6.4e-06 and 7.0e-06, so conditioning is not the driver; dtype is.

The residual gap between the synthetic 7.9e-06 and the observed 3.69e-04 is target magnitude: the
per-gene means span 0.075 to 5.891, and A3 is an absolute error. Median A3 relative to the gene
mean is **1.27e-05**, about 10× float32 epsilon — the expected size for single-precision summation
over 10⁴–10⁵ terms.

Under the exact solver the median cell does satisfy A1: median abs ΔPearson is **5.96e-07**, below
the 1e-6 threshold, with p99 1.22e-05 and max 5.54e-05. It is the high-magnitude tail that fails.

**Reading.** The substantive content of A1, A2 and A3 is confirmed to the precision the faithful
pipeline supports: Pearson does not move, `ycentered` and `intercept` agree, and the intercept head
matches the training mean. The thresholds as written are below the numerical floor of a float32
pipeline and cannot be met by it at any solver setting. The recommendation in § 5.1 is to restate
them as relative tolerances.

### 3.4 A4 fails on substance, and this is the stage's main result

A4 is not a numerical matter. The plan expected the intercept head's fold-median R² to be positive
in a large majority of folds. It is positive in **95 of 319 encoder-folds (29.8%)**.

Adding the intercept does what it was predicted to do, and it is a large effect. Pooled over all
15,950 (encoder, fold, gene) cells, from
`results/round2/R1_intercept/head_intercept__<encoder>.csv`:

| head | median Pearson | median R² | mean R² | fraction of cells with R² < 0 | median mean(prediction) | median mean(target) |
|---|---|---|---|---|---|---|
| nointercept (faithful) | 0.3153 | **−0.9545** | −1.7545 | 94.2% | **0.0085** | 0.6315 |
| intercept | 0.3151 | **−0.1556** | −0.7888 | 66.3% | 0.6446 | 0.6315 |
| ycentered | 0.3151 | −0.1557 | −0.7888 | 66.3% | 0.6446 | 0.6315 |

The faithful head's predictions have median mean 0.0085 against a target median mean of 0.6315 —
it predicts approximately zero for a quantity whose average is 0.63, exactly as the review
predicted. Restoring the intercept recovers **0.799 of median R²** and leaves it negative.

**Pearson is unchanged, so no benchmark-table value moves.** Median 0.3153 → 0.3151; per-gene
median abs ΔPearson 1.94e-04 under the faithful solver and 5.96e-07 under the exact one. Every
Table 1 comparison in the round-1 report stands. What changes is every quantity that is not
shift-invariant: R², absolute residuals, interval width, CRPS — that is, everything Topic A is
about.

**Where the remaining negative R² comes from.** An oracle arm, computed from the stored columns
without refitting (shifting each gene's predictions by the test fold's own mean, which reduces
SS_res by n·δ²), isolates the train-to-test shift in the gene mean:

| head | median R² |
|---|---|
| nointercept | −0.9545 |
| intercept (training-mean intercept) | −0.1556 |
| oracle (test-fold gene mean as intercept) | **+0.0306** |

So of the total 0.985 deficit, 0.799 was the missing intercept and a further 0.186 is the
train-to-test shift in the per-gene mean, which a training-mean intercept cannot track by
construction. Median abs shift is 0.252 in log1p units. Even the oracle is barely positive
(median +0.0306, positive in 178 of 319 encoder-folds), so beyond the mean the head explains
little variance.

![R1: the R² ladder]({{artifact:art_623f6353-7994-4f52-b4d1-3fd8af02fa63}})

**The intercept is not uniformly an improvement.** Per-gene R² improves in **82.5%** of the 15,950
cells (median improvement +0.654, IQR [+0.195, +1.538]) and degrades in 17.5%, worst case
−102.59. The mechanism is visible in the worst cells: `ANKRD30A` in IDC fold 0 has training mean
4.494 and test mean 0.265, a 17-fold slide-level swing, so the head that predicts approximately
zero is accidentally closer to the truth than the one anchored at the training mean, and R² falls
from −9.70 to −112.29. The fraction of cells where the intercept hurts is 4.9% in PRAD and 36.6%
in LYMPH_IDC. This is a Topic A and Topic B result at once: the dominant error term is a
slide-level mean offset, and anchoring it to the training mean is an assumption that fails
whenever the test slide's expression level differs.

Plan-requested side-by-side, fold-median R² for `hoptimus0` and `resnet50`, all tasks, from
`r1_hoptimus0_resnet50.csv`:

| task | hoptimus0 nointercept | hoptimus0 intercept | resnet50 nointercept | resnet50 intercept |
|---|---|---|---|---|
| CCRCC | −0.745 | −0.069 | −0.937 | −0.134 |
| COAD | −1.536 | −0.422 | −1.830 | −0.612 |
| HCC | −0.871 | −0.442 | −0.800 | −0.506 |
| IDC | −2.121 | 0.076 | −1.765 | −0.210 |
| LUNG | −2.126 | 0.024 | −2.066 | −0.196 |
| LYMPH_IDC | −1.030 | −0.731 | −0.927 | −0.700 |
| PAAD | −1.248 | 0.041 | −1.209 | −0.250 |
| PRAD | −0.656 | 0.078 | −0.702 | −0.013 |
| READ | −0.705 | −0.409 | −0.541 | −0.569 |
| SKCM | −0.092 | 0.324 | −0.925 | −0.235 |

Across-encoder spread of median R²: nointercept −1.045 to −0.855 (sd 0.058), intercept −0.262 to
−0.087 (sd 0.055). The direction is the same in 11 of 11 encoders.

### 3.5 A5, the check that establishes pipeline identity

The plan's A1 was meant to certify that the R1 pipeline is the faithful one. Because A1 compares two
R1 heads to each other, it cannot do that — both could be wrong together. A5 was added: the
`nointercept` control must reproduce round 1's stored faithful `pca_ridge` per-task Pearson from
`results/summary/results_task.csv`.

**110 of 110 (encoder, task) cells agree, max abs difference 3.73e-04, mean 6.45e-05, none above
1e-3.** Round 1's table is rounded to four decimals, so this is agreement at the limit of what the
stored file can express. The R1 pipeline is the faithful pipeline. Per-cell values:
`results/round2/R1_intercept/faithful_check__<encoder>.csv`.

### 3.6 R0 acceptance

Required: `sample_metadata.csv` carries both new columns and every sample has a non-null resolution
group. Result, from `results/round2/R0_resolution/r0_verification.csv`:

- 20 of 20 parquets updated (10 tasks × `preds` and `spots`), each **independently re-read after
  writing** and checked for null pixel size, unbinned rows, and constancy of both columns within
  each sample.
- **130,072,250** prediction rows and **11,824,750** spot rows verified, matching round 1's
  reported totals exactly.
- 72 of 72 samples binned, no nulls. `pixel_size_um_estimated` retained alongside the new
  standardised `pixel_size_um`.

One byproduct worth recording: 130,072,250 ÷ 11,824,750 = **11 exactly**, so the round-1
instrumentation layer covers 11 encoders, not the 12 the faithful runs cover. `hoptimus1` has no
rows in `instrumentation/<task>/preds.parquet`. This does not affect any round-1 conclusion but it
does mean that anything reading the instrumentation layer is an 11-encoder result.

---

## 4. For every term and probe: what differs between the arms

The plan requires this list before any term is named. R0 and R1 introduce no split designs and no
probes, so the terms below are the ones R0 renamed or withdrew, plus R1's three heads.

**R1, the three heads.** Between `nointercept` and `intercept`: one thing, the presence of a fitted
per-gene constant. The features are the same object, the fold is the same, the penalty is the same,
the solver is the same. Between `intercept` and `ycentered`: nothing but the order of operations
(centre the target and add the mean back, versus fit the constant). Between `lsqr` and `cholesky`:
the solver only. Between the `intercept` head and the `oracle` arm: which fold supplies the gene
mean, training or test — and nothing else.

**R0, `blocked − patient`, formerly "slide-level signature".** Between the blocked arm and the
patient arm, in a single-slide task: slide identity, stain batch, section, scanner, and — newly
recognised — scan resolution. In a multi-slide task the same list *plus* same-patient-other-slide
information, because the blocked arm trains on other slides of the test patient. That second list
is why the pooled 0.1241 is withheld and the term is reported per task.

**R0, the withdrawn "institution shift".** Between the source-seen and source-unseen arms in IDC:
which slide is held out; whether the *other slide from the same portal* is in training; and scan
resolution, 0.2125 µm/px for the TENX pair against 0.274 and 0.364 for the NCBI pair. What does
*not* differ is the generating laboratory — both halves are 10x Genomics, the NCBI pair being the
GEO deposit of Janesick et al. 2023. The arms therefore never differed by institution and the
0.0419 scalar is withdrawn.

**R0, the slide-identity probe.** Between its classes: patient, tumour biology, stain batch,
section, scanner, and scan resolution. Round 1 attributed 0.9805 to "stain, scanner, section"; that
list was incomplete.

**R0, the technology and cohort-source probes.** Between their classes: the technology or source
label, and also the task, the organ and the tissue, because each task is a single technology and
most sources occur in one task only. The confound is structural and no amount of data removes it;
both probes moved to Appendix A.

---

## 5. Discrepancies and open questions

### 5.1 Decision needed: the R1 acceptance thresholds

A1, A2b and A3 are absolute tolerances of 1e-6 and 1e-4 on a float32 pipeline whose measured floor
is ~1e-5 relative, and ~3.7e-04 absolute on the largest-mean genes. They cannot be met as written.
Proposed restatement, for the oversight chat to accept or amend:

- A1: median abs ΔPearson < 1e-5 and max < 1e-3 under the faithful solver. Observed 1.94e-04 and
  3.15e-02 — so **this would still fail on the max** under `lsqr`, and pass under `cholesky`
  (5.96e-07 median, 5.54e-05 max).
- A3: max abs (train mean pred − train mean target) / mean target < 1e-4. Observed 3.60e-04 worst,
  1.27e-05 median — **would still fail on the worst cell**.

Because the honest restatement still fails on the tail under the faithful solver, the alternative
worth considering is to re-run R1 in float64. That is a one-line dtype change, costs another pass
over cached embeddings, and would make every identity hold to ~1e-14, turning these checks into
real tests rather than measurements of a precision floor. It would also mean the intercept head
shipped to Topic A is no longer bit-identical to round 1's float32 arithmetic. **Recommendation:
keep the float32 `intercept` head as the round-1-comparable artifact, and additionally ship a
float64 head.** Both already coexist in the `head` column; adding a third is cheap. I have not done
this, because it changes an arm definition.

### 5.2 Decision needed: A4, and what the intercept head is for

A4's expectation is not met, and the reason is substantive rather than fixable: with a training-mean
intercept the head's R² is negative in 66.3% of cells and its fold-median is positive in 29.8% of
folds. Restoring the intercept was still correct and necessary — it recovers 0.799 of median R² and
is a precondition for any calibration work — but it does not produce a head with positive R², and
the plan's paragraph ("the faithful protocol's Pearson is unchanged and its R² was negative because
of the missing intercept") is only half the story. The other half is that R² stays negative because
the per-gene mean shifts between slides, which is the Topic A premise stated as a measurement rather
than an assumption. I have written § 3.4 to say both. Confirm that framing before it propagates into
the motivation draft.

### 5.3 Correction to an error inherited from the review

The review's § 5.2 lists LYMPH_IDC among the tasks with two slides per patient. It has **four
samples from four distinct patients**, one slide each: NCBI681/Patient 8, NCBI682/Patient 7,
NCBI683/Patient 6, NCBI684/Patient 3, verified in
`results/tailored/integrity/sample_metadata.csv`. The tasks where any patient contributes more than
one slide are **PRAD, COAD and READ only**:

| task | patients | slides | max slides per patient | multi-slide patients |
|---|---|---|---|---|
| PRAD | 2 | 23 | 15 | patient 1 (8 slides), patient 2 (15) |
| COAD | 2 | 4 | 3 | Patient 1 (TENX147/148/149) |
| READ | 2 | 4 | 2 | Patient 1 (ZEN48/49), Patient 7 (ZEN36/40) |

This propagates into the plan. R3's `slide_out` arm is specified "only for tasks where some patient
has more than one slide (PRAD, COAD, READ, LYMPH_IDC)". The parenthetical is wrong; the criterion
is right. **I intend to run `slide_out` on PRAD, COAD and READ**, which follows the plan's stated
criterion rather than changing it. Flagging it because the plan makes changes to R3 arm definitions
report-and-wait, and because R3's `same-slide identity` term is defined differently for
multi-slide and single-slide tasks — LYMPH_IDC moves into the single-slide branch, where
`blocked_buffered − patient` is the term.

### 5.4 The queue, and what it costs this round

Every R1 job landed on partition `spill` rather than the requested `general`. Priority for these
jobs is 182, decomposing as age 0 + fairshare 4 + partition 177: the account's fairshare is
0.002216 against RawUsage 4,800,141, and it already had 369 CPUs running. **Age is the only
component the submitter influences, and cancelling and resubmitting resets it to zero.** I did
resubmit twice — once to fix the § 3.1 defect and add the exact-solver arm, which was necessary,
and once to shorten walls from 2 h to 50 min in the belief that backfill was the constraint, which
was a mistake: it cost the accumulated age and it is what caused `conch_v15` to hit a wall. The
50-minute wall was also simply too short at ~25 min per encoder under this contention.

Consequence for the rest of the round: R3 is the expensive stage (five designs × three grid sizes ×
repeats), and it should be submitted **once**, with a generous wall, and left alone.

### 5.5 Two edits beyond the letter of R0

R0 items 4 and 5 name the stage report. I applied the same relabelling to the README as well, and
also withdrew there the stale claims the review invalidated. Leaving the README asserting what the
report retracts would reproduce the exact failure the review identified. Both files were then swept
case-insensitively for `confound-free`, `within-patient`, `0.0419`, `institution` and `LYMPH_IDC`;
that sweep caught three further stale statements the targeted edits had missed — the Q1 answer
section, a "not checked" item, and a figure caption — which are now corrected or explicitly marked
stale.

### 5.6 COAD's dispersion

Recomputing round 1's per-task terms to write § 3.4 of the stage report surfaced the anomaly the
review flagged: COAD's patient design has mean 0.3073 with sd **0.0017** across two folds and three
encoders. That is far tighter than any other task (next tightest HCC, 0.0127; typical 0.03–0.09).
Not investigated. It is a candidate symptom of the same-patient structure described in § 5.3, since
COAD's two folds are one slide against three slides of the same patient.

---

## 6. What was not checked

1. **`conch_v15`** — queued, not run. 11 of 12 encoders.
2. **float64 R1** — not run; see § 5.1. The float32 floor is measured, not removed.
3. **The `xgb` and `raw_ridge` heads** — R1 refits `pca_ridge` only, as specified. Whether the
   missing intercept has the same consequence for the other three heads is untested; `xgb` has no
   intercept term in the same sense, and `raw_ridge` was not refitted.
4. **The oracle arm as a model** — it is a diagnostic computed from stored columns. It was not
   refitted, and it is not usable: it reads the test fold's own mean.
5. **Why LYMPH_IDC and READ are worst for the intercept** (36.6% and 35.6% of cells degraded) — the
   association with slide-level mean shift is reported pooled, not modelled per task.
6. **Whether `AQP3` and `ANKRD30A` behave this way for biological or technical reasons** — R6's
   variance-components measurement is the right instrument and has not run.
7. **R0's resolution table against the source images** — `pixel_size_um` is HEST's own estimate,
   carried over from `pixel_size_um_estimated`. It was not re-derived from the WSI metadata, so a
   systematic error in HEST's estimation would propagate into every round-2 resolution result.
8. **Nothing in the faithful stage was touched.** No file under `results/faithful/` was read or
   written by either stage.

---

## 7. Proposed next step

Waiting on § 5.1, § 5.2 and § 5.3. Assuming those are resolved as proposed:

1. `conch_v15` completes on its own and its row is appended to the R1 tables. No action.
2. **R2** next, as the plan orders it. One note from reading HEST's actual `get_k_genes`
   (`code/HEST/src/hest/utils.py:671`) rather than the plan's paraphrase: the common-gene
   intersection uses `np.intersect1d`, which **sorts** the gene order, so the shipped
   `var_50genes.json` order is alphabetical-after-intersection and not AnnData order. More
   importantly, the shipped lists were produced by `get_k_genes_from_df`, which reads
   `aligned_adata.h5ad` from the HEST-1k processed tree — a fuller spot set than the benchmark's
   per-task `adata/*.h5ad`, which round 1's OD1 found to be a strict subset (92.4% of spots
   overall, 57.8% for SKCM). If step 2's exact-reproduction gate fails, that difference is the
   first thing to check, and it would mean the gate cannot be met from `bench_data` alone. I will
   run the gate on the full `adata` spot set, which is the closest available analogue, and report
   before proceeding.
3. **R3** after R2, submitted once with a generous wall per § 5.4.

---

## Appendix. R0 in full

R0 changed one thing in the data and relabelled the rest.

**The data change.** `pixel_size_um` (a standardised copy of `pixel_size_um_estimated`) and
`resolution_group` are now columns of `sample_metadata.csv` and of all 20 joined parquets. Bins are
the plan's: `<=0.15`, `0.15-0.23`, `0.23-0.30`, `0.30-0.40`, `0.40-0.50`, `>0.50` µm/px, which
separate the observed clusters at 0.137, 0.2125, 0.25–0.274, 0.34–0.36, 0.45–0.46 and 0.57–0.69.
Group counts: 2, 3, 14, 16, 30, 7.

**The resolution picture, recomputed from the repository's own metadata rather than transcribed
from the review.** Source: `results/round2/R0_resolution/resolution_by_task.csv`.

| task | slides | patients | distinct µm/px (count) | within-task spread | resolution predicts patient? |
|---|---|---|---|---|---|
| PRAD | 23 | 2 | 0.172 (1), 0.341–0.349 (15), 0.573–0.574 (5), 0.688 (2) | **4.00×** | **yes, exactly** |
| PAAD | 3 | 3 | 0.137 (1), 0.274 (2) | 2.00× | partly — one patient of three is isolated |
| SKCM | 2 | 2 | 0.137 (1), 0.274 (1) | 2.00× | **yes, exactly** |
| IDC | 4 | 4 | 0.2125 (2), 0.274 (1), 0.364 (1) | 1.71× | partly — aligned with cohort source |
| COAD | 4 | 2 | 0.250 (1), 0.274 (3) | 1.10× | no, and hidden inside one bin |
| CCRCC, HCC, LUNG, LYMPH_IDC, READ | 24, 2, 2, 4, 4 | — | uniform within task | ≤ 1.01× | no variation |

Global range 0.1369 to 0.6876 µm/px, **spread 5.02×** across the 72 slides. The minimum is a tie
between TENX116 (PAAD) and TENX117 (SKCM); the maximum is MEND161 and MEND162 (PRAD).

Two refinements on the review's § 5.3, both from this recomputation. The strict statement "no
resolution group contains more than one patient" holds for **PRAD and SKCM**, not for PAAD or IDC,
where one group does contain two patients. And the global spread across all benchmark samples,
5.02×, is larger than the 4× within-task figure the review quoted.

![R0: scan resolution by task]({{artifact:art_fa8b7e85-e07d-4271-898f-c5e21086e494}})

**The relabelling.** README and `final_stage_report.md` (now revision 3):

| change | where |
|---|---|
| "Private repository" line removed | README |
| 99 → **108** encoder-task cells (12 encoders × 9 paper tasks) | README |
| split metric renamed **within-slide** Pearson, with the three multi-slide tasks named | both |
| pooled `blocked − patient` withheld; replaced by a per-task table | report § 3.4 |
| "institution shift 0.0419" **withdrawn**; replaced by the four per-slide gaps | both |
| IDC probe reported **inconclusive** and mislabelled | both |
| technology and cohort-source probes moved to **Appendix A** as confounded by construction | report |
| Q1 rewritten from "UNRESOLVED" to **"NOT TESTABLE ON THIS BENCHMARK"** | report |
| new **Scan resolution** subsection under known limitations | both |
| LYMPH_IDC multi-slide claim corrected (§ 5.3) | both |
| stale `discrepancy_table_v2.csv` path fixed | README |

The four per-slide IDC gaps that replace the withdrawn scalar, recomputed from
`results/tailored/splits/split_decomposition.csv` (mean over 3 encoders × 5 repeats):

| held-out slide | µm/px | gap (source seen − unseen) |
|---|---|---|
| NCBI783 | 0.274 | 0.0022 |
| NCBI785 | 0.364 | 0.0143 |
| TENX95 | 0.2125 | 0.0518 |
| TENX99 | 0.2125 | 0.0992 |

Adding the other slide at the *same* resolution helps by 0.05–0.10; adding the other slide at a
*different* resolution helps by almost nothing. The mean of the four, 0.0419, is the number round 1
reported as institution shift. My recomputation reproduces the review's figures for all ten
per-task terms and all four gaps exactly, which is what licensed the relabelling.
