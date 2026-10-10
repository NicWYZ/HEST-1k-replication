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
| R1 · intercept refit | **complete on 11 of 12 encoders**; `conch_v15` deferred to the R2 submission |
| R1 acceptance | **three of four checks FAIL as written.** The cause is established and is numerical, not a pipeline difference. Details in § 3. Report-and-wait triggered. |

Three things need a decision from the oversight chat: the acceptance thresholds against the measured
float32 floor (§ 5.1), the framing of the A4 result (§ 5.2), and the `slide_out` task list for R3
(§ 5.3). The first two block R2; the third blocks R3.

`conch_v15` is not a failure: its job hit a 50-minute wall while sharing the job with `conch_v1`,
and the rerun then sat in `PENDING (Priority)` for about three hours without starting. Diagnosis in
§ 5.4. I cancelled it rather than leave a queued job nobody was waiting to harvest, and it will be
submitted once, with a generous wall, alongside the R2 jobs. Every number below is over the 11
encoders that completed, and every per-encoder table shows a spread small enough that the twelfth
cannot move a conclusion: the median-$R^2$ result holds in 11/11 encoders and the across-encoder
standard deviation is 0.055.

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
| R1 | `1408698` | conch_v15 | **never started; cancelled after ~3 h pending** |

Three earlier R1 submissions (`1381730`, `1381735`, `1381736`) ran to completion but were
discarded: they predate the fix described in § 3.1, and their outputs were deleted before the
rerun so a partial set could not be mistaken for a complete one.

**Outputs.** `results/round2/R0_resolution/` and `results/round2/R1_intercept/`, each with
`PROVENANCE.txt` carrying job ID, partition, node, commit, date, bin definitions and command line.
Prediction shards in `instrumentation/round2_intercept/<task>/preds__<encoder>.parquet`, 1.6 GB,
11 encoders × 236,495 spots × 50 genes × 2 heads = 260,144,500 rows.

### 2.1 Every deviation from the plan, declared

1. **Sharding per encoder** rather than appending to one per-task file ("a new prediction parquet
   per task"), so that concurrent encoder jobs cannot corrupt a shared file. The shards form one
   per-task dataset.
2. **A cholesky (exact) solver arm** added to R1's three heads. Without it the acceptance failures
   in § 3.3 could not have been attributed, and the plan makes arm definitions report-and-wait —
   this arm is additive and does not alter the three specified heads, but it is a deviation.
3. **Check A5 added** (§ 3.5), because the plan's A1 compares two R1 heads to each other and so
   cannot establish that the pipeline is the faithful one.
4. **An oracle arm** (§ 3.4), computed from stored columns without refitting, to decompose the
   residual negative R².
5. **A `docs/` directory** holding the plan, review, handoff and reports. This is **not in the
   round-2 plan** — it is my addition, so that the plan being executed is version-controlled beside
   the results it produces. Declaring it because the instruction was verbatim transcription.
6. **The plan's ground rule on `config_hash` was initially missed.** PROVENANCE.txt carried job ID,
   partition, node, commit, date and command line but not a config hash. Backfilled for both stages
   by `code/scripts/round2_r1_fix_schema.py`, which records the hash and the config it came from.
7. **Two shard columns were initially misnamed** relative to round 1 — `y_pred`/`y_true_log1p`
   against round 1's `pred`/`target`. The plan requires "the same schema as round 1 plus a head
   column"; the six join keys were correct so joins worked, but the requirement was not met and the
   script had loaded round 1's schema without ever comparing against it. Both the shards and the
   writer are corrected, and the writer now asserts the schema before writing. The shards carry
   round 1's ten columns plus `head` plus `y_raw_count`, the last being a declared addition.

Round-1 schema, read from `instrumentation/CCRCC/preds.parquet` and logged by the R1 job:
`task, encoder, fold, sample_id, barcode, gene, pred, target, pixel_size_um, resolution_group`.

Both fixes are verified, not asserted. `code/scripts/round2_r1_fix_schema.py` rewrote all **110
shards** and then re-read each one: **110 of 110 now match round 1's ten columns plus
`{head, y_raw_count}`**, with all six join keys present, and row counts asserted unchanged through
the rewrite. `config_hash` is now present in all 12 provenance files — `abc798bf1e4975d8` for R1
(covering the pipeline, alpha, solvers, heads, dtype, fold source and metric convention) and
`d69f1db8e24e03d1` for R0 (bin edges, labels, source column and bin closure).

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

Source: the eleven per-encoder files `results/round2/R1_intercept/acceptance__conch_v1.csv`,
`results/round2/R1_intercept/acceptance__ctranspath.csv`,
`results/round2/R1_intercept/acceptance__gigapath.csv`,
`results/round2/R1_intercept/acceptance__hoptimus0.csv`,
`results/round2/R1_intercept/acceptance__hoptimus1.csv`,
`results/round2/R1_intercept/acceptance__phikon.csv`,
`results/round2/R1_intercept/acceptance__resnet50.csv`,
`results/round2/R1_intercept/acceptance__uni_v1.csv`,
`results/round2/R1_intercept/acceptance__uni_v2.csv`,
`results/round2/R1_intercept/acceptance__virchow2.csv`, and
`results/round2/R1_intercept/acceptance__virchow.csv`, worst case over the 11 encoders.

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
mean is **1.265e-05**, which is **106× float32 epsilon** (1.1921e-07) — and that is the size
single-precision accumulation predicts. At the median fold size of 14,972 training spots,
random-walk accumulation gives √n·ε = **1.459e-05** and worst-case accumulation gives n·ε =
1.785e-03; the observed median is **0.87× the random-walk estimate**, i.e. a quantitative match to
√n growth rather than an order-of-magnitude hand-wave. The worst cell sits at 3095× epsilon
(corrected; see Changelog), which is the tail the largest-mean genes in the largest folds
produce.

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
15,950 (encoder, fold, gene) cells, from the eleven per-encoder files
`results/round2/R1_intercept/head_intercept__conch_v1.csv`,
`results/round2/R1_intercept/head_intercept__ctranspath.csv`,
`results/round2/R1_intercept/head_intercept__gigapath.csv`,
`results/round2/R1_intercept/head_intercept__hoptimus0.csv`,
`results/round2/R1_intercept/head_intercept__hoptimus1.csv`,
`results/round2/R1_intercept/head_intercept__phikon.csv`,
`results/round2/R1_intercept/head_intercept__resnet50.csv`,
`results/round2/R1_intercept/head_intercept__uni_v1.csv`,
`results/round2/R1_intercept/head_intercept__uni_v2.csv`,
`results/round2/R1_intercept/head_intercept__virchow2.csv`, and
`results/round2/R1_intercept/head_intercept__virchow.csv`:

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
stored file can express. The R1 pipeline is the faithful pipeline. Per-cell values in the
eleven per-encoder files `results/round2/R1_intercept/faithful_check__conch_v1.csv`,
`results/round2/R1_intercept/faithful_check__ctranspath.csv`,
`results/round2/R1_intercept/faithful_check__gigapath.csv`,
`results/round2/R1_intercept/faithful_check__hoptimus0.csv`,
`results/round2/R1_intercept/faithful_check__hoptimus1.csv`,
`results/round2/R1_intercept/faithful_check__phikon.csv`,
`results/round2/R1_intercept/faithful_check__resnet50.csv`,
`results/round2/R1_intercept/faithful_check__uni_v1.csv`,
`results/round2/R1_intercept/faithful_check__uni_v2.csv`,
`results/round2/R1_intercept/faithful_check__virchow2.csv`, and
`results/round2/R1_intercept/faithful_check__virchow.csv`.

### 3.6 Audit of this report's own numbers

Every substantive figure quoted in this report was re-derived from the per-encoder result CSVs and
checked against the text programmatically, not spot-checked: **40 of 40 numeric claims verified
present in the text and correct to the precision quoted.** The first version of this audit covered
37 claims and one of them was defective — the `ANKRD30A` training mean was compared against a
hard-coded constant rather than against the data, so that entry could not have failed. It is
corrected here, and the four `ANKRD30A` figures (training mean 4.4937, test mean 0.2648, a 16.97×
ratio, and resnet50's R² of −9.704 → −112.291) are now all derived from the result tables. The
audit covers the head table, the
Pearson and R² figures, the oracle decomposition, the improvement distribution, all four acceptance
values in both solver families, the A5 figures, the dispersion statistics, the cell and fold counts,
and the target-magnitude range. Two internal inconsistencies found by review before this audit ran
are corrected above: the A3 figure in § 5.1 is now labelled as the *relative* maximum
(3.603e-04) to distinguish it from the *absolute* maximum in the § 3.2 table (3.690e-04), and the
float32-epsilon multiple in § 3.3 is 106×, not the 10× first written.

### 3.7 R0 acceptance

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

- A1: median abs ΔPearson < 1e-5 and max < 1e-3 under the faithful solver. Observed median
  **1.94e-04** and max **3.15e-02** — so this **fails on both criteria** under `lsqr` (the median
  by 19×, the max by 32×), and passes both comfortably under `cholesky` (5.96e-07 median,
  5.54e-05 max).
- A3: max **relative** error, (train mean pred − train mean target) / mean target, < 1e-4. Observed
  worst **3.603e-04** relative (the corresponding absolute figure is the 3.690e-04 in the § 3.2
  table) against a median of 1.265e-05 — **would still fail on the worst cell**, by 3.6×.

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

The `conch_v15` rerun then never started at all — about three hours in `PENDING (Priority)` — so I
cancelled it rather than leave a queued job whose completion nobody was waiting to harvest, and
folded it into the R2 submission.

Consequence for the rest of the round: R3 is the expensive stage (five designs × three grid sizes ×
repeats), and it should be submitted **once**, with a generous wall, and left alone. The same
applies to R2, which now also carries `conch_v15`.

### 5.5 Which document R0's relabelling belongs in

R0 items 4 and 5 say "in the stage report", and at the time the plan was written the only stage
report was round 1's. I read it as that document and edited it to a revision 3. **That was the wrong
target.** Round 1's report exists only because round 1 had no report-and-wait gates and so produced
one comprehensive document at the end; it records what that round completed and is kept as history.
Turning it into a maintained running report destroys its value as a record and, worse, means the
round-2 relabelling would live in a document nobody reads per stage.

Corrected: round 1's `final_stage_report.md` is restored verbatim to revision 2, and round 2's
relabelling lives in **this report** and in the README, which is the repository's living entry
point. The appendix table records where each change now sits. Round 1's report consequently still
contains the withdrawn claims; that is what a historical record is, and the appendix says so
explicitly so no reader mistakes it for current.

The relabelling itself was applied by sweeping for `confound-free`, `within-patient`, `0.0419`,
`institution` and `LYMPH_IDC` case-insensitively rather than by targeted edits alone; that sweep
caught three stale statements the targeted edits had missed — the institution-question answer, a
"not checked" item, and a figure caption. The sweep, not the edits, is the procedure worth keeping.

### 5.6 COAD's dispersion

Recomputing round 1's per-task terms for this report's appendix surfaced the anomaly the
review flagged: COAD's patient design has mean 0.3073 with sd **0.0017** across two folds and three
encoders. That is far tighter than any other task (next tightest HCC, 0.0127; typical 0.03–0.09).
Not investigated. It is a candidate symptom of the same-patient structure described in § 5.3, since
COAD's two folds are one slide against three slides of the same patient.

---

## 6. What was not checked

1. **`conch_v15`** — not run. 11 of 12 encoders. Deferred to the R2 submission (§ 5.4).
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

1. `conch_v15` is resubmitted **in the same batch as the R2 jobs**, once, with a 3-hour wall, and
   its row appended to the R1 tables. Submitting it on its own again would only reset its queue age
   a third time.
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

**The relabelling, and where it lives.** Round 1's `final_stage_report.md` is a closed historical
record and is not edited; see § 5.5. Round 2's relabelling lives in **this report**, the maintained
document for this stage, and in the README, the repository's living entry point:

| change | where it now lives |
|---|---|
| "Private repository" line removed | README |
| 99 → **108** encoder-task cells (12 encoders × 9 paper tasks) | README |
| split metric renamed **within-slide** Pearson, with the three multi-slide tasks named | README; this report § 4 and appendix |
| pooled `blocked − patient` withheld; replaced by a per-task table | README; this report's appendix table above |
| "institution shift 0.0419" **withdrawn**; replaced by the four per-slide gaps | README; this report § 4 and appendix |
| IDC probe reported **inconclusive** and mislabelled | README; this report § 4 |
| technology and cohort-source probes reported as confounded by construction | README; this report § 4 |
| the institution question reframed from "unresolved" to **not testable on this benchmark** | README; this report § 4 |
| new **Scan resolution** subsection under known limitations | README; this report's appendix |
| LYMPH_IDC multi-slide claim corrected | README; this report § 5.3 |
| stale `discrepancy_table_v2.csv` path fixed | README |

One consequence to be explicit about: round 1's report still contains the claims this stage
withdrew — the pooled slide-signature term, the "institution shift 0.0419" row, the
"confound-free" description of the IDC contrast, and the within-patient metric label. That is what
a historical record is: it says what round 1 concluded. Anyone reading it should read this report
beside it, and the README reflects only the current state.

**The pooled `blocked − patient` term, replaced by a per-task table.** Round 1 reported a single
0.1241 for what it called the slide-level signature. That pooled figure averages over tasks whose
terms do not mean the same thing (§ 4), so R0 withdraws it in favour of the per task values.
Recomputed here from `results/tailored/splits/split_decomposition.csv`, in within-slide Pearson,
over 3 encoders × folds × 5 repeats:

| task | adjacency (random − blocked) | blocked − patient | total (random − patient) | patient-design mean | sd | n |
|---|---|---|---|---|---|---|
| COAD | 0.0343 | **0.2938** | 0.3281 | 0.3073 | 0.0017 | 6 |
| LUNG | 0.0204 | 0.1627 | 0.1831 | 0.5614 | 0.0280 | 6 |
| SKCM | 0.0300 | 0.1439 | 0.1739 | 0.6436 | 0.0575 | 6 |
| PAAD | 0.0227 | 0.1300 | 0.1527 | 0.5024 | 0.0544 | 9 |
| READ | 0.0514 | 0.1197 | 0.1710 | 0.2333 | 0.0305 | 6 |
| HCC | 0.0629 | 0.1075 | 0.1703 | 0.0790 | 0.0127 | 6 |
| IDC | 0.0267 | 0.0965 | 0.1232 | 0.5907 | 0.0912 | 12 |
| PRAD | 0.0244 | 0.0897 | 0.1141 | 0.3040 | 0.0547 | 6 |
| LYMPH_IDC | 0.0311 | 0.0711 | 0.1022 | 0.2643 | 0.0418 | 12 |
| CCRCC | 0.0310 | 0.0258 | 0.0568 | 0.2030 | 0.0572 | 18 |

COAD's `blocked − patient` is **0.2938** against 0.026–0.163 everywhere else, and COAD is one of
the three tasks where a patient contributes several slides — its two folds are one slide against
three slides of the same patient. That is the review's prediction, and it is why the term is
reported per task. The adjacency term, by contrast, means the same thing in every task
(0.0204–0.0629) and may legitimately be pooled.

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

## Changelog

- **21 September 2026.** This report was assessed by the numeric-claim sweep for the first
  time (its earlier run had been OOM-killed at 64 GB during the closeout and never
  measured it). The sweep found `228` of `275` claims unresolved. Almost all of § 3.2's
  acceptance table, § 3.4's head-intercept table and § 3.5's A5 check were flagged for one
  structural reason: the "Source:" lines cited a templated path
  (`acceptance__<encoder>.csv`-style) that could not parse as a real file at all, so those
  three blocks were checked only against `results/summary/deck_numbers.csv` (the sweep's
  always-consulted file) and never against the real per-encoder result files. Fixed by
  replacing each templated citation with the eleven real file names, explicitly. This
  brought the count from `228` to `121`.
- **21 September 2026.** Corrected an arithmetic error in § 3.3: "the worst cell sits at
  `3022`× epsilon" should read **3095×**. The worst A3 cell (virchow2, IDC, fold 2, gene
  AQP3) is `3.6895e-04`, and `3.6895e-04` / `1.1920929e-07` (float32 epsilon) =
  `3095.0` exactly, not `3022`. This does not change the surrounding conclusion (the
  largest-mean genes in the largest folds still produce the tail of the
  accumulation-error distribution); it is a digit-level correction, not a conclusion
  change.
- **21 September 2026.** Triaged the remaining unresolved values (`121` rows, `102`
  distinct values, after the citation fix above). `6` distinct values (§ 3.2's
  A1, A2 and A2b entries) needed no declaration at all -- they resolve as plain literal
  matches now that the citation fix names the real files. `72` distinct values -- the
  appendix's per-task split-decomposition table and per-slide IDC gaps, several pooled
  means and single-cell lookups in § 3.3, § 3.4, § 3.5 and § 3.6, and one arithmetic
  identity -- are genuinely derived quantities computed from cited cells; each now has a `derived:`
  entry in `.verify-derived` that the sweep evaluates rather than a declared exception.
  `15` more (fold-median counts and percentages, a Spearman correlation, a two-level
  standard deviation, an oracle-arm figure, cross-head per-row minimum/median/percentile
  quantities, a cross-format spot-count comparison) are computable by hand but not
  expressible in the derived-formula grammar (no distinct-group count, no rank
  correlation, no inequality filter, no two-level aggregate); each is a
  `derived: inexpressible` declared exception with the hand-verified value recorded in
  the reason. `6` values from the ad-hoc synthetic float32/float64 debugging experiment
  (§ 3.3 point 3) were never checkpointed to a file and are declared `diagnostic:`. `3`
  scheduler-priority figures (§ 5.4) are declared `cost:`. (`6+72+15+6+3=102`, matching
  the count of distinct values.) See `.verify-exceptions` and `.verify-derived` for
  every entry and its reason. Sweep result after this pass: `275` claims, `275`
  verified, `0` unresolved, `0` uncited.
