# Round 2, stages R5b to R8: stage report

Prepared 19 September 2026 for the oversight chat. Covers R5b (donor provenance audit), R5c
(replicate leak generalised), R6 (donor-grouped variance components and theta), R7 (per-gene
decomposition), R8 (H-optimus-1 on the raw heads), and the document and idle-capacity work of
directives 2.6 and 2.7. Written under the R5 decisions memo, which closes the round in a single
interval with no interim reports and no interim stop-and-report conditions; everything that would
previously have halted work is recorded in § 9 instead.

Numbers come from files, with the path. Dispersion accompanies every mean.

---

## 1. Stage and status

| stage | status | deliverable |
|---|---|---|
| R5b donor audit | complete, with three of the audit's own verdicts corrected by me | `results/round2/R5b_audit/donor_audit.csv` |
| R5c replicate leak | complete | `results/round2/R5c_leak/r5c_replicate_leak.csv` |
| R6 variance components | complete | `results/round2/R6_variance/r6_donor_variance_components.csv` |
| R6 theta | complete; acceptance check diagnosed, not passed as written | `results/round2/R6_theta/`, `r6_theta_build_comparison.csv` |
| R7 per-gene | complete | `results/round2/R7_pergene/` |
| R8 raw heads | see § 8 | `results/faithful/raw_{ridge,xgb}__hoptimus1::*` |
| 2.6 rank supplement | complete, third pass | `results/round2/R2_fold_hvg/rank_supplement__hoptimus0.csv` |
| 2.7 IDC confusion | complete | `results/round2/R5c_leak/r5d_idc_partner_confusion.csv` |
| 1.1 authors' draft | written, **not sent** | `docs/hest_bench_issue_draft.md` |

---

## 2. R5b: the donor audit, and the three verdicts I had to correct

All 72 samples were audited against sources outside HEST's metadata: **58 verified,
9 unverifiable, 5 contradicted**.

**Three of the audit's verdicts were wrong, all from one root cause**, and I corrected them before
anything was built on them. The audit assumed which source page each sample came from instead of
reading HEST's own `download_page_link1`. Checking that column:

| task | audit said | what HEST's metadata says | corrected to |
|---|---|---|---|
| LUNG | contradicted — "the only 10x product cited for both has donorCount 1" | **two** distinct pages, one per sample | unverifiable |
| PAAD | "two named products for three samples", implying ≤2 donors | **three** distinct pages, one per sample | unverifiable; reasoning withdrawn |
| SKCM | verified from a `donorCount: 2` page | that page is **neither** of the two HEST cites | unverifiable |

COAD went the other way and was **upgraded**. HEST issue #133, read directly from the GitHub API:
a project collaborator states the patient information for this cohort was wrong in v1.1.0, was
corrected in v1.3.0 (TENX147 → patient 5, TENX148 → patient 2, TENX149 → patient 1), and that the
bench splits were **deliberately** not updated because no patient spans train and test of a fold.
The issue body and the collaborator's reply are saved verbatim at
`results/round2/R5b_audit/r5b_issue133_evidence.md`, and #126 — which that reply cites — at
`r5b_issue126_evidence.md`. The cross-reference needs one word of explanation: **#126 reports the
same study's *Visium HD* samples** (TENX153–156, TENX128, none of them in HEST-bench, corrected in
v1.2.1); our three are that study's **Xenium In Situ** arm, added in v1.3.0.

**And the mapping does not depend on the issue thread at all.** `HEST_v1_1_0.csv` labels all three
`Patient 1` while its own `subseries` field, in the same row, reads "Xenium In Situ, Sample **P5**
CRC", "Sample **P2** CRC" and "Sample **P1** CRC" — reproducing the v1.3.0 mapping exactly
(`r5b_coad_subseries_confirmation.csv`). The three-donor reading is therefore established from the
shipped metadata alone, with the issue as corroboration rather than as the source.
That is true. The consequence it leaves is ours to state: COAD's `test_0` holds out all three of
those samples — three donors — and trains on TENX111 alone. COAD's `random − patient` gap is
**0.3172**, the largest of the ten, where the other nine run
0.0504 to
0.1931
(`r3_per_task_terms.csv`). It is a three-donor holdout trained on one donor, not a fact about
colorectal tissue.

### 2.1 The IDC attribution is flagged, not asserted

The same check cast doubt on a claim already published in the R4–R5 report. The `donorCount: 1`
and Replicate 1 / Replicate 2 language belongs to the "FFPE Human Breast using the Entire Sample
Area" page, which HEST associates with **TENX99 only**; TENX95 is attributed to a different
product, "FFPE Human Breast with Pre-designed Panel". 10x returned HTTP 429 on every re-fetch.

Evidence now on both sides, none of it decisive:

- **For**: TENX95 and TENX99 carry byte-identical 541-entry panels, the only such pair in IDC.
- **For**: of the TENX slides' classification errors, **123 of 128
  (96.1%)** land on the partner TENX slide against 33.3%
  expected if spread over the other three (binomial p = 7.3e-52), in all three
  encoders — though slide identity is decodable at 0.987–0.997
  so this reads only the 0.49% of spots that are
  misclassified at all.
- **Against**: spot counts differ 2.1-fold (25,080 against 11,845), which two replicates of one
  imaged area should not show.
- **Neither**: Janesick et al. is not the source for either — its Xenium runs used the 280-gene
  breast panel **plus 33 add-on genes**, and both samples carry exactly 280 real genes.

**The R5c measurement does not depend on the label**: it measures what TENX95 in training is worth
for predicting TENX99, whatever the two are called. The *claim* that they are one donor does, and
the authors' draft now carries a blocking note saying so.

---

## 3. R5c: the replicate leak generalises, and one way I first reported it was wrong

![R5c: the replicate leak on IDC and READ]({{artifact:a339103d-f1b4-4a9c-90b2-0881642a7dd1}})

Three encoders, six held-out slides, test set and training size held fixed within every pair
(`r5c_replicate_leak.csv`, `r5c_leak_summary.csv`):

| task | leak, mean ± sd | range | positive | task's `random − patient` | realised in the shipped split? |
|---|---|---|---|---|---|
| IDC | **+0.0652** ± 0.0294 | +0.0302 to +0.1096 | 6/6 | 0.1210 | **yes** — 54% of the gap |
| READ | **+0.0901** ± 0.0383 | +0.0326 to +0.1503 | 12/12 | 0.1834 | **no** — see below |

**The correction.** My first summary expressed both as a share of each task's gap. That is right
for IDC, whose four folds are four single slides, so each TENX slide sits in the other's training
set. It is **wrong for READ**, whose folds group each pair — fold 0 is ZEN48+ZEN49, fold 1 is
ZEN36+ZEN40 — so no replicate is ever in its partner's training set and READ's gap contains none
of this. READ's +0.0901 is the **counterfactual** value of a replicate and a second
independent estimate of the quantity IDC's split does expose. It is not a defect in READ; READ is
what a correctly grouped split looks like. The summary now carries a
`leak_realised_in_shipped_split` flag and the share is NaN for READ.

Worth keeping: without its partner, ResNet50 on ZEN40 scores **−0.0174** — below predicting the
mean. And IDC reproduces the standalone R5 run ([`r5_idc_replicate_leak.csv`](r5_idc_replicate_leak.csv)) (0.0652 against 0.0651) under a different subsample
seed, an unplanned reproducibility check on the design.

---

## 4. R6: variance components on the audited donor labels

![R6: variance components on audited donor labels]({{artifact:fbb07f6e-bdc8-4200-b6a4-e25c5952e621}})

`r6_variance_by_task.csv`, `r6_donor_variance_components.csv`. Unbalanced nested ANOVA (Henderson
moments) of log1p expression, per gene, grouped by `donor_id` from R5b.

**The estimator was validated before use** ([`r6_estimator_validation.csv`](r6_estimator_validation.csv))**.** Against known components over 40 unbalanced
simulations at 24 donors it recovers 0.494 / 0.202 / 0.998 against true 0.500 / 0.200 / 1.000, all
z within ±2. The same check showed the donor component's sampling sd is 0.13 at 24 donors and
larger below — which is why `df_donor` is in every row and why five tasks are reported as
uninformative rather than as small effects.

| task | donors / slides | df donor | between donor | between slide, within donor | within slide | label status |
|---|---|---|---|---|---|---|
| CCRCC | 24 / 24 | 23 | 0.393 | — | 0.607 | verified |
| LYMPH_IDC | 4 / 4 | 3 | 0.335 | — | 0.665 | verified |
| IDC | 3 / 4 | 2 | 0.165 | 0.063 | 0.708 | contradicted;unverifiable |
| COAD | 4 / 4 | 3 | 0.116 | — | 0.884 | contradicted;verified |
| HCC | 2 / 2 | 1 | 0.090 | — | 0.910 | verified |
| READ | 2 / 4 | 1 | 0.080 | 0.039 | 0.878 | verified |
| LUNG | 2 / 2 | 1 | 0.062 | — | 0.938 | unverifiable |
| PAAD | 3 / 3 | 2 | 0.048 | — | 0.952 | unverifiable |
| SKCM | 2 / 2 | 1 | 0.015 | — | 0.985 | unverifiable |
| PRAD | 2 / 23 | 1 | 0.000 | 0.140 | 0.854 | verified |

Only **CCRCC (24 donors) and LYMPH_IDC (4)** have `df_donor ≥ 3` with verified labels, at
0.393 and 0.335. Five tasks rest on one degree of freedom. PRAD's between-donor
point estimate of 0.000 is truncation, not a small effect — its raw moment estimate is negative
for 68% of genes.

### 4.1 The pooled estimate: what the directive specified, and what I substituted

Directive 2.3 asks for "a pooled between-donor estimate that uses **CCRCC and PRAD** with the rest
as a sensitivity check." I substituted CCRCC and LYMPH_IDC on a power filter, which is a deviation
from a directive I was told to follow precisely. Both are reported here
(`r6_pooled_between_donor.csv`):

| definition | pooled between-donor fraction |
|---|---|
| **the estimate: CCRCC + LYMPH_IDC** (`df_donor ≥ 3`, verified labels) | **0.3761** |
| directive 2.3 as written: CCRCC + PRAD | 0.1217 |
| sensitivity, all ten tasks ([`r6_variance_by_task.csv`](r6_variance_by_task.csv)) | 0.0846 (range 0.0000–0.3932) |

The two differ threefold for one reason. PRAD has **two** donors, so `df_donor = 1`, and its
between-donor component of 0.000 is truncation — the raw moment estimate is negative for 68% of
its genes. The directive's pairing therefore averages one well-determined value with one
uninformative zero, and 0.1217 is an artefact of that pairing rather than an estimate of anything.
LYMPH_IDC has four donors and `df_donor = 3`.

I should have flagged this at the point of substitution instead of quietly choosing the better
pair; the directive's number is the one that was asked for and it is now stated.

**Settled by the
closeout memo § 1.2: the pooled between-donor estimate is 0.376**, the CCRCC + LYMPH_IDC pairing,
with 0.1217 reported beside it as an artefact of averaging one well-determined value with a
truncated zero. The memo records that the substitution was right *and* that flagging it was
right, so the flag stays.

### 4.2 The PRAD caveat directive 2.3 asked for reverses

The directive asked me to state that PRAD's between-slide-within-donor component contains the
scan-session effect R4 measured. Repeating the decomposition inside PRAD patient 2 with **scan
session** as the top level (`r6_prad_session_variance.csv`, sessions derived from the pixel-size
clustering rather than hard-coded — an 8/7 split at a 0.0066 µm/px gap):

| component | variance |
|---|---|
| between session | **0.00000** — raw estimate ≤ 0 for 28/50 genes |
| between slide, within session | 0.04660 — positive for 50/50 genes |
| within slide (spot) | 0.27606 |

R4 found these same two sessions separable at **0.977** balanced accuracy in the image features
([`r4_probes_v2.csv`](r4_probes_v2.csv)).
They contribute **no measurable variance to the expression**. The session signature lives in the
images and does not reach the targets, so PRAD's slide component is within-session slide-to-slide
variation — not what the directive expected it to contain. This sharpens rather than overturns the
earlier resolution findings: resolution is still aligned with patient identity in PRAD, SKCM and
PAAD, and still confounds those folds on the feature side.

### 4.3 The theta acceptance value, restated against morphology_v2

*Closed by the closeout memo § 1.3: restated, not recorded as a failure.* The plan required
IDC/GATA3/NCBI785 to reproduce round 1's 0.458 to 1e-3; it came out **0.4106** (log1p) /
**0.4209** (raw). The cause is not the computation.

Build statistics below are in [`r6_theta_build_stats.csv`](r6_theta_build_stats.csv).
Round 1's 0.458 is the **raw** correlation on `instrumentation/morphology`; R6 reads
`morphology_v2`, the later build, which assigns ~60% more neoplastic nuclei per spot (mean 17.8
against 11.1) and qualifies 2,195 spots where v1 qualified 1,980. Run against the build the check
was defined on, reproduction is **exact**: 0.457791 against `fig3e_gate.csv`'s 0.457791, six
decimal places.

The substantive round-1 finding survives the build change (`r6_theta_build_comparison.csv`):

| slide | v1 θ₁ | v2 θ₁ |
|---|---|---|
| NCBI785 | 0.4578 | 0.4209 |
| NCBI783 | 0.1333 | 0.1515 |
| TENX95 | 0.0121 | 0.0116 |
| TENX99 | −0.0480 | −0.0649 |

Rank order identical; between-slide spread 0.486 against 0.506. θ₁ remains a slide-level quantity
with large between-slide variance, which is the claim the review called Topic B's strongest single
motivation.

**Restated.** The acceptance value is now **0.410577 (log1p) / 0.420947 (raw) on
`morphology_v2`**, tolerance 1e-3, carried in [`round2_r6_theta.py`](code/scripts/round2_r6_theta.py) and
[`r6_theta_acceptance.csv`](r6_theta_acceptance.csv). Round 1's 0.457791 is retained as a historical value with one line
recording that the difference is the morphology build and not the computation. No failure is
recorded against this check.

---

## 5. R7: two of three pooled correlations reverse under task centring

![R7: pooled versus within-task correlations]({{artifact:9f5519b8-a7ad-45d5-befe-5feebbfdee96}})

`r7_pergene_decomposition.csv` (1,500 encoder–task–gene rows), `r7_correlations_task_centred.csv`.
Directive 2.4's join uses R6's **between-donor** variance.

Pooling per-gene correlations across ten tasks mixes a within-task with a between-task relation,
and they disagree:

| relation | pooled | within task | between task |
|---|---|---|---|
| split penalty vs between-donor variance | -0.2338 | **+0.0441** (p = 0.09) | -0.59 |
| novel slide vs between-slide variance | -0.2218 | **+0.2096** (p = 3e-04) | — |
| replicate leak vs split penalty | +0.3803 | **+0.3774** (p < 1e-10) | — |

Directive 2.4 asks a question about genes, so the within-task value is the answer:

1. **Between-donor variance does not explain which genes lose most from a patient-respecting
   split** (+0.044, not significant). The pooled −0.23 is a between-task effect.
2. **Between-slide-within-donor variance does predict which genes lose most from slide novelty**
   (+0.210, p = 3e-04) — the *opposite sign* to the pooled figure.
3. **The genes a patient split costs most are the genes a same-donor replicate recovers most**
   (+0.377), the one relation unaffected by centring.

The pooled negative is itself a task-level finding, reported as such on ten points: tasks with the
most between-donor variance have the **smallest** patient-split penalties (Spearman
-0.59) — CCRCC at 0.396 donor variance and a 0.050 penalty against PRAD's
0.006 and 0.136.

---

## 6. Directives 2.6 and 2.7

**Rank supplement (2.6).** `r2_rank_supplement.csv`. Holding the shipped 50 fixed and varying only
whether the ranking sees training spots or all spots: mean Spearman **0.510**
(sd 0.209, range -0.069 to 0.779), with 32 of 50 genes moving more
than five ranks. So the protocol genuinely moves the ranking; what it moves is *which genes get
picked*, which is why the R2 gap is not interpretable as leakage. It took three passes (§ 9). The
built-in check — how many of the shipped 50 the all-spot arm recovers, which must be 50 if the
statistic is the benchmark's — is now **50/50 on all ten tasks**, and the supplement's
set-overlap figure of 27.2/50 matches R2's independently computed 27.2 exactly.

**IDC confusion (2.7).** Reported in § 2.1.

**Documents.** `docs/hest_bench_issue_draft.md` written and **not sent**, with the IDC attribution
flagged as blocking. README updated: scan resolution reframed as a proxy for scan session, key
findings carrying the replicate leak in place of the withdrawn institution scalar, finding 5
rewritten from an open question to the answer R4 supplies.

---

## 7. Arms differing, for every term reported here

| term | what differs between its arms |
|---|---|
| replicate leak | **only** whether the same-donor partner slide is in the training pool. Test spots identical, training size identical to the spot, same pipeline, same metric, same seed. |
| between-donor variance | donor identity, and everything confounded with it in that task — tissue, scanner, panel, site. It is a variance decomposition, not a contrast, so nothing is held fixed. |
| between-slide-within-donor | slide identity within one donor: section, staining batch, scan session, position in the block. |
| between-session (PRAD patient 2) | scan session only. Donor, tissue, panel and platform constant; slides split 8/7. |
| θ₁ | nothing — it is a within-slide correlation, and the between-slide spread is the quantity of interest. |
| rank supplement | **only** whether the ranking statistic sees the held-out slide's spots. Gene set fixed at the shipped 50. |

---

## 8. R8: D2 is confirmed, cleanly

![R8: the raw-head ranking tracks embedding width]({{artifact:aafecd6b-dab3-42c5-aed4-7b1927259400}})

`r8_raw_head_leaderboard.csv`, `results/faithful/raw_ridge__hoptimus1::26-09-19-02-32-36/`.
H-optimus-1 had all ten `pca_ridge` cells and zero `raw_ridge`/`raw_xgb` cells, so this filled a
real gap rather than repeating work. All 72 embeddings were already cached; no GPU was used.

D2 claims Table A13's encoder ranking tracks prediction **width** rather than accuracy.
H-optimus-1 is the sharpest available test because it is the strongest encoder in the set:

- **pca_ridge: rank 1 of 12** at 0.3891 — the best encoder there is.
- **raw_ridge: rank 7 of 12** at 0.2590 — mid-table, exactly where 1536
  dimensions places it.

And the pattern is not confined to it ([`r8_width_correlations.csv`](r8_width_correlations.csv)).
Spearman(width, raw_ridge) = **-0.950**
(p < 1e-4, n = 12); equalising width at 256 with PCA reverses the sign to **+0.727**
(p = 0.007). Every encoder of ≥1536 dimensions occupies raw_ridge ranks 7–12, every encoder of
≤1024 dimensions occupies ranks 1–6, with no exceptions. The two orderings correlate
**-0.60**.

So the `pca_ridge` ranking reflects encoder quality and the `raw_ridge` ranking reflects
dimensionality. **D2's reading of Table A13 is confirmed, not falsified.** The plan asked me to
report where H-optimus-1 lands rather than whether it confirms, and it lands 7th.

**`raw_xgb` did not finish, and I cancelled it rather than resubmit.** It completed **2 of 29
splits in 2 h 25 min** — about 70 minutes per split, so roughly 34 hours for the full set against
the 8-hour wall I gave it. At that rate it would have reached one task of ten by the wall, which
cannot support a leaderboard comparison, and the D2 falsification hinges on `raw_ridge`, which is
complete across all ten tasks. Continuing would have spent the group's allocation on an output
this report already records as not obtained. What would finish it is in § 10.

---

## 9. Escalations and discrepancies

Per the memo these are recorded rather than halting work. None was acted on outside the project.

1. **Three audit verdicts corrected (§ 2).** LUNG and PAAD contradictions withdrawn, SKCM
   downgraded from verified. One root cause: assuming the source page instead of reading HEST's
   `download_page_link1`.
2. **The IDC same-donor attribution is not secure (§ 2.1)**, and it is already published in the
   R4–R5 report. The measurement is unaffected; the label claim is flagged and the authors' draft
   carries a blocking note. 10x rate-limiting prevented closure.
3. **COAD's fault is already known upstream and deliberately not fixed in the splits** (HEST
   #133). Our contribution is the consequence, not the report.
4. **A reviewer caught two COAD figures in the authors' draft that were not in the file they
   cited** — 0.2938 and a 0.026–0.163 range, both carried from round 1's v3 decomposition, whose
   per-task file is not in the artifact store. Replaced with
   0.3172 and 0.2578
   from `r3_per_task_terms.csv`; both documents then swept, nine quoted terms all verified. This is
   the second occurrence of the same failure mode — a number typed from memory into a sentence
   whose *citation* was accurate — and it is now the most recurrent defect in this project.
5. **The theta acceptance threshold is defined against a superseded morphology build** (§ 4.3).
   Not a failure of the computation; needs restating.
6. **R8's first submission never scheduled.** 8 CPUs / 64 GB / 24 h sat 5.5 hours at `(Priority)`
   while every other job ran. `sacct` shows my heaviest job ever peaked at 8.8 GB on 4 CPUs, so the
   ask was several-fold oversized. Resized from that record, it started within minutes.
7. **`raw_xgb` incomplete** (§ 8).

### Failures of mine in this interval, and what each cost

| what | cost | fix |
|---|---|---|
| Rank supplement used the wrong scanpy path, then omitted `min_cells_pct` | two wasted passes | the built-in recovery check caught both; `disp()` now reproduces `get_k_genes` step for step and recovers 50/50 on all ten tasks |
| Confusion script lifted a prelude above the line binding `enc` | one failed job, 3 min | an AST check for names used but never bound would have caught it; recorded |
| Piped job output through `tail`, blinding progress monitoring — **again**, having recorded this exact gotcha last interval | no data lost, monitoring lost | read the result directories instead |
| R8 harvest used `find \| head`, giving SIGPIPE and exit 141 on a job whose computation had fully succeeded | nearly discarded a complete result | checked the output directory before believing the exit code |
| Oversized R8 resource ask | 5.5 h of queue | size from `sacct`, not intuition |

---

## 10. What was not checked

- **`raw_xgb` for H-optimus-1** — 10 of 10 task cells still missing (2 IDC splits exist and are
  not enough for a task value). At the measured 70 min/split this needs ~34 CPU-hours; a fan-out
  of ten per-task jobs is the right shape, and would backfill far better than one long job.
- **The IDC attribution** — needs the "FFPE Human Breast with Pre-designed Panel" page read. Every
  fetch returned HTTP 429.
- **Donor identity for the 9 unverifiable samples** (LUNG 2, PAAD 3, SKCM 2, and 2 others). The
  sources reached do not state it. R6's components for those tasks carry the status.
- **Bootstrap intervals on the variance components.** Point estimates plus degrees of freedom are
  reported; with two donors no resampling makes the donor term informative, so this would be
  decoration on the tasks that matter.
- **Whether the between-session result generalises beyond PRAD patient 2.** It is one patient, two
  sessions, 15 slides — the only place in the benchmark where session varies with donor fixed.
- **Assumption diagnostics for the nested ANOVA** (normality, homoscedasticity per gene). Not
  assessed.

---

## 11. Proposed next step

1. **Settle the IDC attribution** before the authors' draft goes anywhere. One page fetch.
2. **Restate the theta acceptance value** against `morphology_v2` and record v1's as historical.
3. **Finish `raw_xgb`** as ten per-task jobs if the D2 result is wanted on both heads; otherwise
   close it, since `raw_ridge` settles the question.
4. **For Topic B**, the two cleanest results in this interval are the replicate leak generalising
   across two tasks (§ 3) and the finding that the scan session lives in the features but not the
   targets (§ 4.1). The second says something sharp about what a slide-level random effect is
   modelling: the technical signature an encoder reads need not be present in what it predicts.
5. **For Topic A**, R7's within-task result (§ 5) says between-donor biological variance does not
   explain which genes a patient split costs most — so a donor-level random effect alone will not
   absorb the penalty, and the replicate result points at what does.
