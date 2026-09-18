# Round 2 stage report: R0, R1, R1b, R2, R3

Prepared 18 September 2026 for the oversight chat. Covers every round-2 stage completed since the
R0/R1 report, and restates the R0/R1 results so this document stands alone. Repository
`NicWYZ/HEST-1k-replication`; all numbers come from files, with paths given.

Documents this implements, in order of precedence: `round2_R1_decisions.md` (the oversight chat's
decisions on the R1 report, transcribed into the operating plan as stages R1b and R2 to R7);
`round2_execution_plan.md` (stages R0 to R8); `HEST_replication_review.md` (the audit that motivated
both).

---

## 1. Stage and status

| stage | status | what it answers |
|---|---|---|
| R0 — resolution columns and relabelling | complete | is scan resolution joined to every prediction row, and are the review's three mislabelled terms corrected |
| R1 — intercept refit | complete, superseded by R1b | does the benchmark head have an intercept, and what does adding one cost |
| R1b — float64 head, ladder, solver sensitivity, D3, D4 | complete | is the head's $R^2$ deficit level, shift, scale, or pattern; is the faithful solver's tolerance material |
| R2 — gene-selection leakage | complete | how much of round 1's Pearson comes from selecting genes on all spots |
| R3 — split decomposition v4 | see § 6 | what the blocked-minus-patient term actually contains |

Two stop-and-report conditions in the decisions document were hit, both in R1b, and both are
resolved below: the float64 identity check failed on first run (§ 3.1), and a D3 finding changed
what a round-1 term can be called (§ 5.1).

---

## 2. What was run

| stage | script | commit | jobs |
|---|---|---|---|
| R0 | `code/scripts/round2_r0_resolution_columns.py` | `eb670fa`→`16bccda` | 1 |
| R1 | `code/scripts/round2_head_intercept.py` | `16bccda` | 6 (11 encoders) |
| R1b | `code/scripts/round2_r1b_heads.py` | `085628b` | 8 (12 encoders × 3 solver families) |
| R1b D3/D4 | `code/scripts/round2_r1b_d3_d4.py` | `16bccda` | 2 |
| R2 | `code/scripts/round2_r2_gene_check.py`, `round2_r2_fold_hvg.py` | `64f5838` | 4 |
| R3 | `code/scripts/round2_split_v4.py` | `64f5838` | 3 |

Every round-2 output directory carries `PROVENANCE.txt` with the SLURM job ID, the partition
actually used, node, date, repository commit, script path, command line, a config hash and the
config the hash covers, plus a pointer to the plan or decision clause it implements. `config_hash`
was missing from the R0 and R1 directories and was backfilled (`R1_intercept`
`abc798bf1e4975d8`, `R0_resolution` `d69f1db8e24e03d1`).

---

## 3. Acceptance checks, with the actual numbers

### 3.1 The float64 head: a stop-and-report failure that was my bug

Decision 1 set the float64 identity thresholds as hard stops, on the reasoning that under exact
double-precision arithmetic the three heads are algebraically identical up to a per-gene shift of
$\bar y$, so a deviation is a bug rather than a floor. **The checks failed on first run** — A2b at
1.7e-04 against a 1e-09 threshold — and the reasoning was right: two independent defects, both
mine, neither a property of the head.

1. **Features.** The float64 family cast the *float32* scaler/PCA output to float64 rather than
   running the pipeline in float64. The identity rests on PCA centring the training features so
   that $A^\top \mathbf{1} = 0$, which makes the intercept and no-intercept coefficient vectors
   equal. Casting afterwards does not buy that. Measured: PCA column means sit at 5.1e-08 instead
   of 1.1e-16, the two coefficient vectors then differ at 3.2e-08, and the identity can only hold
   to about 6.6e-07 however exact the ridge solve is.
2. **Target means.** `Y` is stored float32, and `np.mean` on a float32 array accumulates in
   float32, putting a ~4.9e-06 relative floor on the train-mean check for reasons unconnected to
   the head.

Both were diagnosed by a controlled experiment — float32 versus float64 pipeline, both solvers,
holding everything else fixed — before any code was changed. With both fixed, **all four checks
pass on real data across all 12 encoders**, by six to seven orders of magnitude. No threshold was
weakened.

From `results/round2/R1b_heads/acceptance__*__f64.csv`, worst over 12 encoders:

| check | threshold | worst observed | verdict |
|---|---|---|---|
| A1 $\max|\Delta r(\text{int}-\text{noint})|$ | 1e-09 | 1.14e-13 | PASS |
| A2 $\max|\hat y_{\text{int}} - \hat y_{\text{ycent}}|$ | 1e-09 | 1.51e-14 | PASS |
| A2b $\max|(\hat y_{\text{int}} - \hat y_{\text{noint}}) - \bar y|$ | 1e-09 | 1.44e-11 | PASS |
| A3 $\max|\text{mean}(\hat y_{\text{train}}) - \bar y_{\text{train}}|$, relative | 1e-10 | 4.44e-15 | PASS |

The float32 families are retained as the round-1-comparable record and are **not** held to these
thresholds, for the reason R1 established (a float32 accumulation floor, median relative error
1.265e-05, 106× float32 epsilon and 0.87× the $\sqrt n \epsilon$ prediction). Their worst values,
same source files:

| family | A1 | A2 | A2b | A3 (absolute) |
|---|---|---|---|---|
| `lsqr` float32 (the faithful head) | 2.86e-02 | 6.92e-02 | 3.52e-01 | 3.69e-04 |
| `cholesky` float32 (exact solve) | 6.97e-05 | 9.54e-06 | 2.69e-03 | 3.69e-04 |

The contrast between those two rows is the whole point of the exact-solver arm: the faithful head's
A2b of 0.35 is **iterative-solver tolerance**, not precision — the exact solve in the same dtype
gives 2.69e-03, two orders of magnitude smaller, and A3 is identical to four significant figures
across both (3.69e-04), which is the dtype floor and nothing else.

### 3.2 A5, reproduction of the faithful result

`results/round2/R1b_heads/faithful_check__*__f64.csv`: the float64 no-intercept head reproduces
round 1's per-task faithful Pearson over 120 encoder-task cells with mean absolute difference
1.49e-04 and maximum 1.24e-03; 1 cell of 120 exceeds 1e-03. That is the expected order — the
float64 exact pipeline is a *different, more exact* computation than round 1's float32 `lsqr`, and
the discrepancy sits inside the solver sensitivity measured in § 4.3.

The float32 `lsqr` arm, which must match round 1 tightly, does. Recomputed over the **same
12-encoder, 120-cell set** from `results/round2/R1b_heads/faithful_check__*.csv` (not the
11-encoder R1 figure): mean absolute difference 7.05e-05, maximum **3.728e-04**, **0 of 120** cells
above 1e-03. The worst cell is `conch_v1` on CCRCC (0.217627 against the shipped 0.2180), and
`conch_v1` and `conch_v15` supply all three worst cells — the same two encoders that top the
solver-sensitivity table in § 4.3, which is the expected pattern if the residual is `lsqr`
tolerance.

---

## 4. Results

### 4.1 The head has no intercept, and that is most of its $R^2$ deficit

`r1b_ladder_by_task.csv`, `r1b_ladder_by_encoder.csv`. Computed by exact algebra on the stored
per-gene columns, with no refitting: with $b$ the level offset, $\rho = s_{\hat y}/s_y$ the scale
ratio and $r$ the correlation,

$$R^2 = 2r\rho - \rho^2 - b^2/s_y^2 .$$

This reconstructs the stored $R^2$ to median 3.1e-14 (maximum 4.1e-11) on real data, so the rungs
are decomposition rather than approximation.

Median over 12 encoders × 29 folds × 50 genes:

| rung | median $R^2$ | gain |
|---|---|---|
| faithful head (no intercept) | −0.9532 | — |
| training-mean intercept | −0.1552 | +0.798 |
| oracle level (test fold's own gene mean) | +0.0301 | +0.185 |
| oracle level and optimal scale | +0.0997 | +0.070 |

The last rung equals $r^2$ and is the ceiling for **any** level-and-scale recalibration of this
head. So the deficit assigns as: two thirds of the recoverable part is level, fixed by an
intercept; of the remainder, a slide-level mean shift that no training-mean intercept can track
(+0.185) and a scale term (+0.070); and a pattern ceiling of +0.0997 that recalibration cannot
pass.

### 4.2 The head is over-dispersed, and the over-dispersion orders with encoder quality

Median $\rho$ = 0.5796 against median $r$ = 0.3150, so $\rho/r$ = 1.84: the head's predictions vary
1.84× more than is optimal given how well they correlate. This is a new result and it is the
quantity a calibration layer would target. From `r1b_ladder_by_encoder.csv` it orders with encoder
quality — `resnet50` 2.17, `conch_v1` 2.04, `ctranspath` 2.03, down to `uni_v2` 1.65, `hoptimus1`
1.69, `hoptimus0` 1.71 — so the weaker the encoder, the more over-dispersed its head.

### 4.3 Solver sensitivity: a footnote, not a known limitation

`r1b_solver_sensitivity.csv`, 12 encoders × 10 tasks, mean $|r_{\text{lsqr}} - r_{\text{cholesky}}|$
on the float32 no-intercept head. Under Decision 1's rule this is **not** a known limitation:
nothing reaches the 5e-3 threshold anywhere. The worst per-task mean is 0.00311 (COAD), 95 of 120
encoder-task cells sit below the 1e-3 footnote threshold, and 6 of 12 encoders are below 1e-3 on
every task. Worst single per-gene cell 0.0276 (PAAD).

Per-encoder worst-task mean, ascending: `uni_v2` 0.00044, `uni_v1` 0.00052, `gigapath` 0.00053,
`hoptimus1` 0.00054, `resnet50` 0.00058, `hoptimus0` 0.00067, `phikon` 0.00102, `virchow2` 0.00123,
`virchow` 0.00135, `ctranspath` 0.00148, `conch_v15` 0.00290, `conch_v1` 0.00311.

Practical reading: a per-gene Pearson in the faithful protocol carries about 1e-3 of solver noise
for most encoders and up to 3e-3 for `conch_v1`, `conch_v15`, `ctranspath` and `virchow`, so a
per-gene Pearson should not be quoted beyond three decimals. Task-level means, averaging 50 genes,
are unaffected at the precision Table 1 reports.

### 4.4 D4 — the estimated pixel size is corroborated, except where it matters most

`results/round2/R1b_heads/d4_pixel_size_check.csv`. Directive D4 asked whether
`pixel_size_um_estimated`, which round 1 derived from the patch geometry and which R0 promoted to
`pixel_size_um` on every prediction row, agrees with the pixel size embedded in the upstream HEST
metadata table (`HEST_v1_1_0.csv`, column `pixel_size_um_embedded`).

An embedded value exists for **45 of 72** samples. Where both exist the agreement is near-exact:
median absolute difference **0.052%**, 95th percentile 19.8%. Four samples are flagged, of which
three disagree at the `resolution_group` level and one differs in magnitude without crossing a bin:

| task | sample | estimated | embedded | % diff | crosses a bin? | verdict |
|---|---|---|---|---|---|---|
| IDC | TENX95 | 0.2125 | 1.0000 | +370.6 | yes | embedded value is a header default, not a measurement |
| IDC | TENX99 | 0.2125 | 1.0000 | +370.6 | yes | same |
| COAD | TENX111 | 0.2738 | 0.2125 | −22.4 | yes | genuine discrepancy |
| COAD | TENX147 | 0.2497 | 0.2738 | +9.6 | no — both `0.23-0.30` | genuine but immaterial to the covariate as used |

1.0000 µm/px is not a plausible Xenium or Visium resolution, so the two IDC rows are a placeholder
rather than a conflict — which also means my first flagging rule, which treated *missing* and
*discrepant* alike, was too blunt and was refined to separate them.

The consequential finding is what has **no** second source at all: **PRAD (23 samples) and
LYMPH_IDC (4) carry no embedded pixel size whatsoever.** PRAD is precisely the task where
resolution matters most — it is the task with the 4× within-task spread aligned with patient
identity that motivated R0 in the first place. So the resolution covariate is corroborated
everywhere except the one task whose conclusions most depend on it.

The `resolution_uncertain = True` flag therefore covers **31 of 72** samples, and the count closes
exactly: **27** with no embedded value at all (PRAD 23, LYMPH_IDC 4) **+ 3** disagreeing at the
group level **+ 1** disagreeing in magnitude only = 31. It is set on every prediction row, and any
R4-onward result that conditions on resolution must report the flagged subset separately. Only the
COAD/TENX111 row is a discrepancy that would change a resolution *group*; the two IDC rows are a
placeholder and TENX147 stays within its bin.

### 4.5 R2 — the gene-selection contrast, and a benchmark property that reframes it

**Step 1, the gate, passed exactly.** A verbatim reimplementation of the benchmark's `get_k_genes`
reproduces all ten shipped 50-gene lists **exactly, set and order**, from the benchmark `adata`
files alone (`results/round2/R2_fold_hvg/d2_reproduction_check__adata.csv`). Reading the upstream
source pinned two details the plan's paraphrase omits: the common-gene intersection is sorted, and
the top-$k$ selection is taken in that sorted order. This retires the concern that the shipped lists
might only be reproducible from a fuller upstream spot set, and made the planned fallback
unnecessary.

**Step 2 failed substantively, and the failure is the finding.** Selecting genes from training
samples only, then extracting them from the held-out slide, raised a `KeyError`: **HEST-bench
samples within a task do not all carry the same gene panel.**

From `r2_panel_heterogeneity.csv`:

| task | panel sizes | genes common to all samples | union | panels identical |
|---|---|---|---|---|
| PAAD | 538–541 | **159** | 919 | no |
| LUNG | 541 | 259 | 823 | no |
| SKCM | 541 | 343 | 739 | no |
| COAD | 541 | 412 | 670 | no |
| IDC | 541 | 500 | 582 | no |
| CCRCC | 17,943–36,601 | 17,943 | 36,601 | no |
| HCC, LYMPH_IDC, PRAD, READ | uniform | — | — | yes |

The shipped 50 lie on the common panel in **every** task, consistent with being selected from the
all-sample intersection. It follows that a genuinely leakage-free selection can name genes the
held-out slide **cannot measure**: on LUNG it loses 25 of 50, PAAD 13, COAD 10.5 on average, worst
fold 35 of 50. Those are dropped and counted rather than silently failing
(`n_fold_genes_off_panel`, `genes_off_panel` per fold in `r2_fold_hvg.csv`).

This sharpens round 1's known limitation. Round 1 recorded gene-selection leakage as "the ranking
used test-fold spots". It is stronger: on this benchmark **leakage-free gene selection is not well
defined without knowing the held-out slide's panel**, because panel membership is itself test-set
information. That is a property of HEST-bench, not of this replication, and it is the second
candidate benchmark-issue report alongside § 5.1.

**The measured gap, and why it should not be called leakage.** `r2_leakage_summary.csv`,
4 encoders × 29 folds. Shipped minus fold-selected, within-slide Pearson: overall **+0.0091**
(sd 0.0487), positive in only **61 of 116** folds, per-task range −0.0660 (READ) to +0.0441
(LYMPH_IDC).

| task | gap | sd | folds + | shared genes /50 | off-panel dropped | gene-set effect |
|---|---|---|---|---|---|---|
| LYMPH_IDC | **+0.0441** | 0.0679 | 12/16 | 21.0 | 0 | +0.0694 |
| PRAD | **+0.0402** | 0.0153 | 8/8 | 11.0 | 0 | +0.0520 |
| PAAD | +0.0179 | 0.0193 | 11/12 | 32.7 | 13.0 | +0.0718 |
| LUNG | +0.0123 | 0.0285 | 5/8 | 19.0 | 25.0 | −0.0720 |
| IDC | +0.0094 | 0.0306 | 8/16 | 36.3 | 0 | +0.0310 |
| CCRCC | +0.0105 | 0.0472 | 4/24 | 34.7 | 0 | −0.0167 |
| SKCM | +0.0049 | 0.0066 | 5/8 | 30.5 | 3.0 | +0.0191 |
| HCC | −0.0024 | 0.0107 | 3/8 | 24.0 | 0 | −0.0035 |
| COAD | −0.0228 | 0.0285 | 3/8 | 26.0 | 10.5 | −0.1547 |
| READ | −0.0660 | 0.0732 | 2/8 | 16.5 | 0 | −0.1032 |

Two tasks clear the plan's 0.02 escalation threshold and were escalated: **LYMPH_IDC +0.0441** and
**PRAD +0.0402**.

Listing what differs between the two arms, before naming the term — the procedural rule from the
review:

1. whether test-fold spots informed the variance ranking — the **intended** contrast;
2. **which genes are the targets**, and hence their intrinsic predictability. The arms share only
   27.2 of 50 genes on average, and on PRAD just 11;
3. on COAD, LUNG, PAAD and SKCM, **the number of genes**, because off-panel genes are dropped —
   which also changes the ridge penalty, since $\alpha = 100/(256 \cdot n_{\text{genes}})$;
4. on those same tasks, which genes the held-out slide can measure at all.

Variable 2 is measurable and large. The `gene-set effect` column above is the within-slide Pearson
of the shipped-exclusive genes minus that of the fold-exclusive genes — the difference in intrinsic
predictability between the two lists' non-overlapping parts. It **correlates with the measured gap
at Spearman 0.758** across the ten tasks, and for both escalating tasks it is *larger* than the gap
itself (PRAD +0.0520 vs +0.0402; LYMPH_IDC +0.0694 vs +0.0441). READ makes the same point in
reverse: its fold-exclusive genes are more predictable than its shipped-exclusive ones by 0.103,
and its gap is correspondingly negative.

So the design as specified measures "the shipped list scores higher than a fold-selected list",
which is a mixture of leakage and gene-set composition, and the two are not separable within it.
Variables 3 and 4 can at least be ruled out for the escalating pair: PRAD and LYMPH_IDC drop no
off-panel genes, so both arms there carry 50 genes and an identical penalty.

**Proposed clean design, not run.** Hold the gene set fixed and vary only the ranking's data — rank
the *shipped* 50 by fold-internal variance and compare against their all-spot ranking, reporting
rank correlation and the induced top-$k$ overlap. That isolates variable 1 with no gene-set or
penalty difference. Awaiting a decision before it is scheduled.

---

## 5. Directives D3 and D4, and a naming consequence

### 5.1 D3 — COAD's patient labels do not separate patients

`results/round2/R1b_heads/d3_coad_patient_rows.csv`. Directive D3 asked why round 1's COAD
`blocked − patient` term had a standard deviation of 0.0017 across two folds and three encoders,
which the review suspected of being a repeated computation rather than a measurement.

It is not a repeated computation: the two folds genuinely differ in size and composition. The
explanation came from the metadata instead, and it is more serious. **The benchmark's patient field
for COAD collapses several distinct patients into one label and leaves another sample unlabelled**,
so COAD's shipped patient split does not separate patients at all. The consequence is that the
review's headline same-patient reading of COAD's 0.294 term cannot mean what it says — the term's
two arms do not differ in patient identity the way the label asserts.

Checking the remaining multi-slide tasks differentiated them rather than tarring all four: PRAD's
labels are confirmed by its subseries strings; READ understates itself, because its pairs are
replicates of the same specimen rather than merely the same patient; and LYMPH_IDC, corrected
earlier from the review's list, stays corrected at four samples from four distinct patients.

This was escalated to Nicolas as a benchmark issue under the plan's routing. The computation was
left running — only the naming changes — and § 6 reports COAD's v4 terms under the corrected
description, where the v4 decomposition independently confirms the fault.

---

## 6. R3 — the split decomposition, v4

Three encoders (`hoptimus0`, `uni_v2`, `resnet50`) × 10 tasks × 29 folds × five designs, plus the
buffered arm, a three-point grid sweep and leave-one-slide-out on the three tasks verified to have
a patient contributing more than one slide. 6,138 rows in `r3_split_v4.csv`.

### 6.1 Acceptance: v4 reproduces v3 exactly

The plan requires reporting any per-task term that changes sign from v3. **None does**, and the
reproduction is tighter than that: v4's `random − patient` matches round 1's `total_leak` to
**0.0000 on all ten tasks** for the encoder the two rounds share (`uni_v2`), with **0 of 10** sign
flips. v4's size-matched adjacency term (mean 0.0321) also matches v3's adjacency (0.0320). This is
by design — v4 carried the within-slide metric and the `random` and `patient` arms over unchanged —
but it is the check that makes the new arms interpretable rather than a separate experiment.

### 6.2 The gap is a decomposition, not an attribution

Each step is the drop between adjacent designs, ordered by how much information about the held-out
spots each removes. The steps sum to the total **exactly** (residual 0.00e+00), so this partitions
the gap rather than attributing it.

All ten tasks, 30 encoder-task cells:

| step | mean | sd |
|---|---|---|
| `random − random_matched` — training-set size | +0.0126 | 0.0111 |
| `random_matched − blocked_matched` — spatial adjacency | +0.0327 | 0.0090 |
| `blocked_matched − blocked_buffered` — adjacency past the block edge | +0.0115 | 0.0059 |
| `blocked_buffered − patient` — slide and patient, not separable here | +0.1017 | 0.0636 |
| **total `random − patient`** | **+0.1586** | 0.0717 |

The three tasks with a multi-slide patient, where the last row splits, 9 cells:

| step | mean | sd |
|---|---|---|
| training-set size | +0.0133 | 0.0090 |
| spatial adjacency | +0.0320 | 0.0089 |
| adjacency past the block edge | +0.0107 | 0.0034 |
| `blocked_buffered − slide_out` — **novel slide** | **+0.0148** | 0.0179 |
| `slide_out − patient` — **patient identity** | **+0.1357** | 0.0962 |
| **total** | **+0.2064** | 0.0900 |

### 6.3 Three things this changes about round 1

**Round 1 understated adjacency.** Its blocked arm had no buffer, so adjacency leaked across block
edges. v4 splits adjacency into 0.0327 within the block design plus a further **0.0115 that only a
buffer removes** — about a third more adjacency than round 1's 0.0335 measured.

**Part of what round 1 called a slide-level signature is training-set size.** The `patient` arm
trains on fewer spots than the `random` arm, and that alone is worth **+0.0126**. It is not a slide
effect, a site effect, or biology; it is $n$. Round 1's 0.1241 "slide-level signature" contains it.

**The dominant term is patient, not slide.** Once another slide from the same patient is in
training, holding out a whole further slide costs only **+0.0148** — smaller than the adjacency
term, and resolved from zero on only one of the three tasks (§ 6.4). Losing the patient entirely
costs **+0.1357**, an order of magnitude more. So the review's
framing that "the slide, not the spot, is the unit of inference" is directionally right but names
the wrong level: on this evidence the **patient** is the unit of inference, and slide novelty is a
minor cost on top.

### 6.4 The COAD prediction, and why its number cannot be read as a patient effect

Per task, from `r3_per_task_terms.csv`. The novel-slide column carries its own dispersion because
**two of the three tasks cannot resolve it from zero**, which changes what can be claimed:

| task | novel slide | sd | in sd units | patient identity | patient-label status (D3) |
|---|---|---|---|---|---|
| COAD | +0.0022 | 0.0198 | **0.11** | **+0.2578** | **labels collapse distinct patients** |
| READ | +0.0141 | 0.0196 | **0.72** | +0.0910 | pairs are same-specimen replicates |
| PRAD | +0.0280 | 0.0019 | **14.4** | +0.0583 | labels confirmed from subseries strings |

**An earlier draft of this report quoted a "199×" ratio for COAD. That number was meaningless and
has been withdrawn**, because COAD's novel-slide term — the denominator — is 0.11 of its own
standard deviation, i.e. indistinguishable from zero. A ratio against a zero denominator is
unstable by construction, and it duly moved to 115× when the arm was recomputed (§ 6.6). No ratio
is quoted for COAD or READ.

What survives, stated in terms the data supports:

- **Only PRAD resolves a novel-slide cost at all**, at +0.0280 with sd 0.0019 — **14 sd**, and the
  only task where the term is distinguishable from zero. There, patient identity is **2.1×** the
  novel-slide cost.
- **COAD's and READ's novel-slide terms are within noise of zero**, so on those tasks the evidence
  is that holding out a whole further slide costs *nothing measurable* once the patient's other
  slides remain in training. That is the stronger form of the same conclusion, not a weaker one.
- **COAD's large patient-identity term is a label artefact.** Because its patient field collapses
  several distinct patients into one label (§ 5.1), its `patient` arm holds out **more than one
  patient's** slides while its `slide_out` arm holds out one slide. The arms differ in how many
  patients leave training, not only in whether the same patient's other slides remain. COAD's
  0.2578 is a multi-patient holdout penalty wearing a same-patient label, and round 1's 0.294 was
  the same quantity. The review nominated this as one of its two clearest demonstrations that the
  slide is the unit of inference; **that demonstration is withdrawn.**
- READ's term is a same-*specimen* effect, since its pairs are replicate sections of one specimen,
  so it is an upper bound on a patient effect.

So the Topic B motivation survives and rests on PRAD, at 2.1× rather than any of the larger figures
round 1 or this report's first draft suggested.

### 6.5 The buffer makes the adjacency term well defined

`r3_buffer_grid_sweep.csv`. The buffer does what it claims: the median nearest-training-spot
distance rises **1.50×** at grid 4, **1.73×** at grid 6 and **2.07×** at grid 10, the ratio growing
with grid fineness as it should, since finer blocks have proportionally more edge. (Absolute
distances are in each sample's own pixel coordinates and are not comparable across tasks of
different resolution; the ratio is the meaningful quantity.)

The consequence is the more important result:

| block grid | blocked, no buffer | blocked + buffer |
|---|---|---|
| 4 | 0.4234 | 0.4118 |
| 6 | 0.4393 | 0.4222 |
| 10 | 0.4515 | 0.4140 |
| **spread** | **0.0281** | **0.0104** |

Unbuffered, measured accuracy rises monotonically with grid fineness — finer blocks put held-out
spots nearer training spots, so the design leaks more — and the total drift, 0.028, is almost as
large as the entire adjacency term it is meant to measure. Buffered, the spread is 0.010 with no
monotone trend. **Without a buffer, a blocked-split result is partly a statement about the block
size chosen**, which is an arbitrary parameter. This is why the arm was added and it should be
standard in any spatial-CV result this project reports.

### 6.6 A determinism failure found by an unplanned check, and what it cost

The per-gene regeneration reran the entire computation with the same seeds, so it also rewrote
`split_v4__*.csv`. Comparing those against the files the reported numbers came from was free, so I
ran it as a determinism check. **It failed**, and finding out why changed one reported claim.

**450 of 6138 rows differed**, up to 0.046 — and every one of them was the `slide_out` design, on
all three encoders, all three tasks and all five repeats. `n_train` and `n_test` matched exactly, so
the splits were identical and only the scores moved. The cause was line 338 of
`round2_split_v4.py`:

```python
rng = np.random.default_rng(SEED + 4441 * rep + hash(s) % 1000)   # s is a slide id
```

**Python randomises `str` hashing per process** unless `PYTHONHASHSEED` is set, so this reseeded the
training-size-matching subsample differently on every run. The same slide id gives `213`, `700`,
`780` on three successive interpreters; `zlib.crc32` gives `14622` every time. The two other RNGs
in the script seed from integers only (`rep`, `k`, `grid`), which is precisely why every other
design reproduced bit-exactly.

What it did and did not affect:

| quantity | reproduces? | first draw | second draw |
|---|---|---|---|
| training-set size, adjacency, buffer residual | **exactly** | — | spread 0.0000 |
| total `random − patient`, both task sets | **exactly** | — | spread 0.0000 |
| novel slide | no | +0.0138 | **+0.0148** |
| patient identity | no | +0.1367 | **+0.1357** |

Both totals are unaffected because `slide_out` cancels out of `random − patient`. The two affected
terms moved by 0.0010, which is 0.06 and 0.01 of their own standard deviations — so no conclusion
turns on it. The exception is the COAD **ratio**, which fell from 199× to roughly 115× — and is so
ill-conditioned that recomputing it from the 4-decimal saved table rather than the full-precision
column shifts it again, to 117×. A quantity that moves with rounding alone is not a result.
Chasing that instability is what exposed that the ratio should never have been quoted (§ 6.4).

**Fixed** by seeding from `zlib.crc32(s.encode())`, which is stable across processes and versions.
The same defect was then found in a second place by sweeping every round-2 script for `hash()`:
`round2_r4_probes.py` computed its `PROVENANCE` `config_hash` over a tuple containing strings, so
that hash was randomised per run and **identified nothing** — the opposite of a provenance record's
purpose. Both now use a `config_hash()` helper built on `crc32`.

**The regenerated run is canonical** in this report and in the saved `r3_split_v4.csv`, because it
is the run the per-gene parquet was computed alongside, so R7's inputs and R3's reported summaries
describe the same draw.

### 6.7 Figures

![The benchmark head's R² deficit assigned to three fixable causes and a pattern ceiling]({{artifact:art_7caa60fe-1a11-45e7-98d3-7e61e020f5e9}})

![The random-to-patient gap decomposed into five additive steps, and the buffer removing the grid dependence]({{artifact:art_1b827c41-3703-4dd5-acf8-db74c4df9e4c}})

---

## 7. For every term and probe: what differs between its arms

The review's procedural fix, applied before any term in this report is named. Each row lists
*everything* that differs between the two arms, not only the intended contrast.

### 7.1 R1b's ladder rungs

| term | arms | everything that differs |
|---|---|---|
| level | no-intercept vs training-mean intercept head | (1) the intercept, and nothing else — identical features, identical folds, identical solver, verified by the A1–A3 identity checks to 1e-13 |
| slide-level mean shift | training-mean intercept vs oracle level | (1) whether the level comes from the training fold's gene mean or the test fold's own gene mean. The oracle arm **reads the test fold's labels** and is diagnostic only |
| scale | oracle level vs oracle level and optimal scale | (1) whether the prediction is rescaled by the least-squares optimal $\rho$, also computed **on the test fold** |

### 7.2 R2's gene-selection contrast

Arms: the shipped 50-gene list versus a list selected from training samples only.

1. whether test-fold spots informed the variance ranking — the **intended** contrast;
2. **which genes are the targets**, hence their intrinsic predictability; the arms share 27.2 of 50
   on average, 11 on PRAD. Measured at Spearman 0.758 against the gap, and larger than the gap on
   both escalating tasks;
3. on COAD, LUNG, PAAD and SKCM, **the number of genes** — because off-panel genes are dropped —
   and therefore the ridge penalty, since $\alpha = 100/(256 n_{\text{genes}})$;
4. on those same tasks, **which genes the held-out slide can measure at all**.

Because of 2, the term is **not** named leakage in this report.

### 7.3 R3's decomposition steps

| step | arms | everything that differs |
|---|---|---|
| training-set size | `random` vs `random_matched` | (1) $n_{\text{train}}$ only; the split rule, spot pool and metric are identical. This is the cleanest term in the round |
| spatial adjacency | `random_matched` vs `blocked_matched` | (1) whether held-out spots are scattered or contiguous, hence their distance to the nearest training spot. $n_{\text{train}}$ matched by construction |
| adjacency past the block edge | `blocked_matched` vs `blocked_buffered` | (1) whether training spots within 2–3 spot pitches of a held-out spot are dropped. Note this also **reduces $n_{\text{train}}$** in the buffered arm, so the step is an upper bound on edge adjacency and includes a small size effect of the same sign |
| novel slide | `blocked_buffered` vs `slide_out` | (1) whether the held-out spots come from a slide with no spots in training; (2) $n_{\text{train}}$, matched to the patient design for that slide's patient; (3) for the held-out slide, its own scan resolution, stain batch and section — all of which change together with slide identity and are **not** separable here |
| patient identity | `slide_out` vs `patient` | (1) whether the same patient's *other* slides remain in training; (2) **on COAD, how many patients leave training**, because the patient field collapses distinct patients — which is why COAD's value is not read as a same-patient effect; (3) on READ, whether the same *specimen*'s other section remains, since its pairs are replicates |
| total | `random` vs `patient` | the union of all of the above |

### 7.4 R4's probes

Not run — see § 10. Their interpretation rules and arm-difference lists are written into
`code/scripts/round2_r4_probes.py` before any execution, per the plan's acceptance requirement, and
will be reported with the results.

---

## 8. Discrepancies and open questions

1. **Two tasks exceed the gene-selection escalation threshold** (§ 4.5): LYMPH_IDC +0.0441 and
   PRAD +0.0402 against the plan's 0.02. Escalated. My reading is that the number should be
   escalated but not called leakage, and that the clean design in § 4.5 is what would settle it.
2. **COAD's patient labels are wrong in the benchmark** (§ 5.1), and the v4 arms independently
   confirm it (§ 6.4): COAD's novel-slide step is 0.11 of its own sd, i.e. indistinguishable from
   zero, while its patient-identity step is +0.2578 — the signature of a holdout that removes
   more than one patient. On PRAD, the only task with verified labels and the only one whose
   novel-slide term is resolved from zero (14 sd), patient identity is 2.1× the novel-slide cost. Escalated as a benchmark issue.
3. **HEST-bench samples within a task carry different gene panels** (§ 4.5), so leakage-free gene
   selection is not well defined without the held-out slide's panel. Escalated as a benchmark
   issue. PAAD is the extreme: 159 genes common to its three samples against a 919 union.
4. **PRAD and LYMPH_IDC have no independent pixel size** (§ 4.4), and PRAD is the task whose
   conclusions most depend on resolution. 31 of 72 samples carry `resolution_uncertain`.
5. **Probe 2's class definition does not survive contact with R0's binning.** PRAD patient 1's
   eight slides group by nominal pixel size as {0.57: 5, 0.69: 2, 0.17: 1} — exactly the plan's own
   breakdown — but under R0's bins they occupy only **two** groups, since 0.573 and 0.688 both
   exceed 0.50. And the plan's "chance is 1/3 balanced" is inconsistent with its own instruction to
   exclude the single 0.172 slide from leave-one-slide-out, which leaves two evaluable classes and
   chance 1/2. The script computes both and labels the two-class version primary. **Decision
   requested.**
6. **A process question on this gate.** I launched R4 and R6 while R3's per-gene regeneration was
   still running, on the plan's § 11 line that "R1, R3, R4 and R6 can run in parallel" and its
   dependency table, which has R3 blocking only R7 and R4 depending only on R0. Nicolas stopped
   me on the ground that R3 is a report-and-wait gate and nothing past it should start before this
   report is reviewed. Both readings are supported by the document — § 0 names R3 as report-and-wait,
   § 11 says R4 and R6 can run in parallel with it — and the two statements are not reconciled in
   the plan. **I have cancelled both and am not restarting them without a decision.** If the
   intended meaning is that report-and-wait halts every downstream stage and not just the dependent
   ones, that is worth stating explicitly in the plan, since it changes the schedule in § 11
   materially.
7. **The float32 `lsqr` A2b of 0.352** (§ 3.1) deserves a note in its own right: the faithful head's
   iterative solver leaves the three-head identity violated by a third of a Pearson unit in the
   worst cell. It does not affect Pearson (A1 is 2.9e-02 worst, and per-gene solver noise is ~1e-3,
   § 4.3), but it means the faithful head's *predictions* are not the ridge solution to within any
   tight tolerance. Topic A should build on the float64 head, which is what R1b ships.

---

## 9. What was not checked

- **Assumption and residual diagnostics** on any head. Not assessed.
- **Whether the intercept helps out of sample in the metric the benchmark reports.** It cannot, by
  construction: Pearson is shift-invariant, which is § 3.1's A1 check. The intercept matters for
  $R^2$, CRPS and interval width, none of which the benchmark reports.
- **R2 on more than four encoders.** The gap is reported on `hoptimus0`, `uni_v2`, `virchow` and
  `resnet50` only.
- **R3 on more than three encoders.** `hoptimus0`, `uni_v2`, `resnet50`. The plan permits deciding
  the encoder set alone; three was chosen to span the quality range (best, mid, ImageNet baseline)
  at the cost of a 47-hour wall each.
- ~~The per-gene R3 table~~ — **now complete.** `pergene__{hoptimus0,resnet50,uni_v2}.parquet`.
  All three were read in full and checked individually, each giving 851,050 rows, 7 of 7 designs,
  10 tasks, 430 genes, 0 nulls in `pearson`, `fold` stored as string with `grid` as nullable
  `Int32`, `fold == slide` on every `slide_out` row and zero-padded two-digit folds everywhere
  else. R7's input exists.

  (An earlier revision of this line said "explicit schema verified on read" for all three when
  only the row counts — read from each file's parquet metadata — had been checked on all three;
  the schema, design, task, gene and null checks had been run on `hoptimus0` alone. Now run on
  each file, with the design list and null count asserted rather than printed.)
- **Whether the R2 gap survives holding the gene set fixed.** The proposed clean design in § 4.5 is
  specified and not run.
- **Probe 2's binned variant** is reported as undefined for PRAD patient 1 rather than computed.
- **Any R4, R5, R6, R7 or R8 result.** R4 and R6 were started and cancelled (§ 8.6); R5 and R7 were
  never started.

---

## 10. Failures in this block, and what they cost

Recorded because the plan asks for them and because two were mine in ways worth not repeating.

| what | cost | cause | fix |
|---|---|---|---|
| float64 identity checks failed | ~1 h | cast float32 PCA output to float64 instead of running the pipeline in float64; and compared against a float32-accumulated target mean | true float64 pipeline; float64 accumulation for every per-gene statistic (`085628b`) |
| corrected float64 pass raised immediately | minutes | a progress line still read the float32 delta keys, which do not exist in a float64-only pass | swept the whole script for hardcoded head names; dry-ran the entire post-loop block on a synthetic float64-only frame |
| R2 fold comparison raised | ~1 h | fold-selected genes can be off-panel on the held-out slide | not a bug — became § 4.5's finding; now measured and reported |
| **all three R3 runs died on their last write** | **~35 h of CPU across three jobs** | the per-gene `fold` column holds an int for shipped folds and a slide id for `slide_out`; pyarrow inferred `int64` and failed on the first `slide_out` row | `fold` is a string throughout with `fold_num` beside it, and the parquet is written against an **explicit `pa.schema`** (`b6b5328`) |
| harvest job killed while queued | minutes | gave `run_timeout_s=3600` to a 10-second job; the harness run clock counts **queue** time | generous ceilings on every job regardless of its runtime |

The R3 one is the expensive lesson and it generalises. The failure is **pyarrow
version-dependent**: on the newer local pyarrow the same frame infers `string` and writes fine, so
a local smoke test would have passed while the cluster run died. Naming the schema removes the
version dependence rather than making the failure less likely. The summary CSVs survived only
because they happen to be written before the parquet — that was luck, not design, and the general
rule now in `docs/WAYS_OF_WORKING.md` is that anything written after expensive compute gets an
explicit schema and the cheapest outputs get written first.

---

## 11. Proposed next step

1. **Decide § 8.5** (Probe 2's classes and chance) and **§ 8.6** (whether R4 and R6 may run
   alongside a report-and-wait gate). Both are one-line answers and both block work that is ready.
2. **Decide whether to run the clean gene-selection design** in § 4.5. It is cheap and it converts
   an escalated number that I do not think means what its label says into one that does.
3. ~~Let the per-gene regeneration finish~~ — done; R3 is complete and R7's input exists.
4. Then R4 and R6 as the plan has them, with Probe 2 per the § 8.5 decision.
5. R5 is a reading task and needs no compute; it can run whenever.

On the two topics, what this block establishes: **Topic A** has its intercept, and the $R^2$
deficit is now assigned — two thirds level, then a slide-level mean shift, then scale, against a
pattern ceiling of +0.0997. The over-dispersion result ($\rho/r$ = 1.84, ordering with encoder
quality) is the concrete target for a calibration layer. **Topic B**'s premise survives but must be
restated: the unit of inference is the **patient**, not the slide — novel-slide cost +0.0148 against
patient-identity +0.1357 — and the COAD result the review nominated as one of its two clearest
demonstrations has to be withdrawn, because that task's patient labels do not separate patients.
PRAD at 2.1× is the honest version, and it is the only task whose novel-slide term is resolved from
zero at all.
