# Round 2 stage report: R4 and R5

Prepared 18 September 2026 for the oversight chat. This is the single report for the interval that
decision memo `round2_R3_decisions.md` opened, covering stages **R4** and **R5** and nothing after
them. Repository `NicWYZ/HEST-1k-replication`; every number cites the file it came from.

Written in the order set by the execution plan's § 13. Escalations are in § 7 rather than having
halted work, per the memo's § 0.

---

## 1. Stage and status

| stage | status | what it produced |
|---|---|---|
| R4, probes v2 | **complete**, after two defect reruns | `r4_probes_v2.csv`, `r4_probe1_confusion.csv`, `fig_r4_probes.png` |
| R5, IDC provenance | **complete** | `r5_idc_provenance.md`, `r5_idc_panels_observed.csv`, `r5_idc_panel_pairs.csv` |
| R3 defect fix (authorised by memo § 0) | see § 6 | `donor_out__*.csv` |

R6, R7 and R8 have not been started, set up, staged or piloted.

The headline is that the two stages answer the same question from opposite directions and agree.
R4 asked what the encoder reads when the patient is held fixed, and found a per-slide and
per-scan-session signature that survives morphology adjustment. R5 asked what actually differs
between the four IDC samples, and found that two of them are not different patients at all.

---

## 2. What was run

| item | script | commit | job |
|---|---|---|---|
| R4 probes, run 1 | `code/scripts/round2_r4_probes.py` | `cc188ff`, corrected `8b037c1` | `259f5185` — failed, exit 1 |
| R4 probes, run 2 | same, fixed | `4062fec` | `3d68e239` — succeeded |
| R4 probes, run 3 (probe 2 rescored) | same, rescored | `f3bf4c9` | `860e9f1e` — succeeded, **the reported run** |
| R5 provenance | reading task, no compute | — | delegated track |
| IDC panel extraction | ad-hoc, from each sample's own `var_names` | — | `call_command` |
| IDC donor_out fix | `code/scripts/round2_r5_donor_out.py` | see § 6 | `29e5ac35`, `95d8f80f`, `bfca7784` |

All SLURM scripts in this interval set `PYTHONHASHSEED=0` (memo § 2.6). The full sweep of that
change across older scripts is idle-capacity work under memo § 3 item 3 and is **not** done yet.

---

## 3. R4 — what the encoder reads when the patient is held fixed

Three encoders (`hoptimus0`, `uni_v2`, `resnet50`). Source: `r4_probes_v2.csv`.

### 3.1 The headline

| probe | unit | chance | accuracy (min–max over encoders) | verdict |
|---|---|---|---|---|
| slide identity | PRAD patient 2, 15 slides | 0.067 | **0.871 – 0.949** | far above chance |
| scan sub-cluster | PRAD patient 2, 2 sessions | 0.500 | **0.967 – 0.991** | far above chance |
| resolution class | PRAD patient 1, 7 slides | 0.500 | **0.489 – 0.511** | **at chance** |

Probe 1 was given its interpretation rule before it ran: blocked accuracy above 0.8 means the slide
signature is technical, near chance means round 1's 0.98 was biology and resolution. All three
encoders clear 0.8. Within a single patient, at a pixel-size spread of 0.3412 to 0.3492 µm/px —
1.02× — slides remain individually identifiable at 0.92 on average. **Round 1's slide-identity
probe was not reading tissue.**

### 3.2 Where the signature lives

The confusion matrix locates it. Off-diagonal mass falling inside a scan sub-cluster is **0.933,
0.964, 0.945** for the three encoders, against **0.467** expected if the sub-clusters were
interchangeable. Sub-cluster membership is itself decodable at **0.977** on average, with **15 of
15** slides assigned to the correct session by majority vote, for every encoder.

The two sub-clusters were verified from the metadata rather than taken from the memo: eight slides
at 0.3413–0.3418 µm/px (MEND139–MEND146) and seven at 0.3484–0.3492 (MEND147–MEND153), separated by
0.0066 µm/px, with contiguous ID blocks — consistent with two scan sessions.

**A note on the decision rule.** Memo § 2.1 framed this as a choice: confusion mostly within
sub-cluster means the signature is per-slide, confusion between sub-clusters means a scan-session
effect. The data does not choose. Slides are individually identifiable *and* sessions are almost
perfectly separable, and high within-session confusion means the session axis is the *easier* one —
errors concentrate where the session is shared. Both components are present, with the session
component the stronger. The either/or phrasing should be retired rather than answered.

### 3.3 Scan resolution is not what is encoded, and probe 2's first numbers are withdrawn

This is the result that changes an earlier reading, so the withdrawal comes first.

**Withdrawn:** probe 2's run-2 values of 0.712, 0.683 and 0.669. They are not evidence of anything.
Each leave-one-slide-out fold holds out one slide, whose spots all carry one resolution class, so a
per-fold balanced accuracy is recall on a single class. With 5 slides at 0.573 and 2 at 0.688, a
classifier that always predicts the majority class scores **5/7 = 0.714** — and the three values sit
at or *below* it. The statistic could not distinguish a resolution signal from a constant
prediction. This is the same defect as probe 1b's, which had been fixed; leaving it in probe 2 was
an inconsistency on my part.

**Replacement:** pool the leave-one-slide-out predictions and score once on the pooled pair, which
contains both classes, and report the per-slide majority vote beside it.

| encoder | pooled balanced accuracy | majority vote | withdrawn per-fold value | trivial baseline |
|---|---|---|---|---|
| hoptimus0 | 0.5112 | 5/7 | 0.7118 | 0.7143 |
| uni_v2 | 0.4888 | 5/7 | 0.6825 | 0.7143 |
| resnet50 | 0.4905 | 5/7 | 0.6686 | 0.7143 |

**Nominal scan resolution is not decodable within one patient.** Every encoder sits at chance, and
the majority vote is 5/7 for all three — exactly the constant predictor, the 5 majority slides right
and the 2 minority slides wrong.

Set beside probe 1b this is informative rather than merely negative. Patient 2's two sessions differ
by **0.0066 µm/px** and are separable at 0.98; patient 1's classes differ by **20%** (0.573 against
0.688) and are not separable at all. So what the embeddings carry is the *session and the slide*,
not the pixel size. The round-0 finding stands unchanged as a statement about the benchmark's
design — resolution is aligned with patient identity in PRAD, SKCM and PAAD — but the mechanism is
not "the encoder sees resolution."

**Power.** Probe 2 has 7 slides in a 5:2 split. It is consistent with no effect and cannot exclude
a small one; it is not evidence that resolution is undetectable in general.

### 3.4 Composition adjustment

Regressing the PCA-256 features on the morphology covariates, with the regression fit on training
spots only so the adjustment cannot itself move slide information between arms. Mean accuracy lost
over the three encoders:

| task | unit | blocked accuracy | lost to adjustment | under the plan-exact covariates | verdict |
|---|---|---|---|---|---|
| PRAD | patient 2, 15 slides | 0.877 | **0.014** | 0.011 | composition explains almost none |
| IDC | 4 samples | 0.998 | 0.030 | 0.023 | little |
| LUNG | 2 samples | 0.996 | 0.169 | 0.161 | partial to most |
| PAAD | 3 samples | 0.990 | 0.212 | 0.214 | most |
| SKCM | 2 samples | 0.996 | 0.274 | 0.279 | most |

Both covariate sets are reported because the plan names "mean nuclear area" and the parquet carries
both a generic `area_mean` and a neoplastic-only `neo_area_mean`; the earlier draft used the latter
by mistake. The verdicts are identical under either set, so no conclusion depends on that choice.

The contrast that matters is PRAD against the rest. On tasks whose slides come from *different*
patients, 13–27% of the slide signature is tissue composition — as expected, since different
patients have different tissue. Within **one** patient it is 1.4%. What remains there is not
composition, and by § 3.3 it is not resolution either.

### 3.5 The resolution_uncertain subset

Directive D4 asked for this subset separately. For the PRAD probes the answer is degenerate and
worth stating plainly rather than tabulating: **all 15 patient-2 slides and all 8 patient-1 slides
carry `resolution_uncertain = True`**, because PRAD has no embedded pixel size anywhere in the
benchmark. So probes 1, 1b, 2 and the PRAD arm of probe 3 lie entirely inside the flagged subset and
there is no unflagged comparison to make. Of the probe-3 tasks, only IDC contains flagged samples
(2 of 4); PAAD, LUNG and SKCM contain none.

This is a caveat on the *labels*, not on the probes. PRAD is Visium, so its pixel size is derived
from the known 100 µm spot pitch, which memo § 1.1 accepts as the more reliable of the two sources.
Probe 1 and probe 1b do not depend on the pixel values being right in absolute terms — only on the
two sub-clusters being distinct, which holds under any monotone rescaling.

### 3.6 Figure

![R4 probes](art_6472025f-bec2-4fc4-966d-924f8f07e109)

What the embeddings encode with the patient held fixed; the confusion structure; and how
much of the signature morphology composition accounts for.

---

## 4. R5 — IDC provenance

Reading task, run as a parallel track. Full write-up with every citation:
`r5_idc_provenance.md`. Observed panel data, computed from the four samples' own gene lists:
`r5_idc_panels_observed.csv` and `r5_idc_panel_pairs.csv`.

### 4.1 TENX95 and TENX99 are one donor, not two patients

This is the stage's main finding and it is an escalation (§ 7).

HEST's metadata assigns the four IDC samples four distinct patient labels — TENX99 "patient 1",
TENX95 "patient 2", NCBI785 "patient 4", NCBI783 "patient 5"
(`results/tailored/integrity/sample_metadata.csv`). But the 10x Genomics dataset page that is the
source of both TENX samples, *"FFPE Human Breast using the Entire Sample Area"*, states in its own
embedded metadata `"donorCount":1`, and its description reads "5µm sections from a formalin-fixed
paraffin-embedded (FFPE) human breast resected tumor mass **sample**" — plural sections, singular
sample — from Avaden Biosciences. The page presents the two as "Replicate 1"
(`Xenium_V1_FFPE_Human_Breast_IDC_Big_1`) and "Replicate 2" (`..._Big_2`) side by side, whose
purpose is stated as demonstrating "the high reproducibility of data generated by the platform",
with per-replicate metrics (892,966 against 885,523 cells detected).

I verified these strings myself in the fetched page rather than taking them from the track's
summary. One word from that summary is **not** supported and I have dropped it: the page nowhere
says "serial". What is sourced is *two 5 µm sections of one resected tumour mass from one donor*.

**So IDC has three donors, not four.** The NCBI pair, by contrast, is a genuine two-patient
contrast: they map to different GEO records in the Janesick et al. 2023 deposit
(doi:10.1038/s41467-023-43458-x) with different collection dates (2009 against 2021) and different
receptor and stage profiles.

### 4.2 The gene panels differ, and the difference is real

Computed from each sample's own `var_names`, not from any metadata table. All four files carry
exactly **541 entries**, but entries are not genes — they include Xenium control probes (`BLANK_`,
`NEGCONTROLCODEWORD_`, `NEGCONTROLPROBE_`):

| sample | entries | control probes | real genes | extras over the 500-entry intersection |
|---|---|---|---|---|
| NCBI783 | 541 | 253 | 288 | 33 control probes + 8 `antisense_*` probes |
| NCBI785 | 541 | 220 | **321** | 0 control + **41 real add-on genes** |
| TENX95 | 541 | 261 | 280 | 41 control probes + 0 real |
| TENX99 | 541 | 261 | 280 | 41 control probes + 0 real |

The four-way intersection is 500 entries = **280 real genes** + 220 control probes. Only TENX95 and
TENX99 have identical panels; pairwise overlaps are 533 (NCBI783 against each TENX), 508 (the NCBI
pair) and 500 (NCBI785 against each TENX).

The provenance track resolved this against primary sources, and it is a **real panel difference,
not a control-probe bookkeeping artefact**. The raw GEO-deposited `gene_panel.json` files show
TENX95/TENX99 on the commercial pre-designed Xenium Human Breast panel v1 (280 targets, no add-on),
NCBI783 on that base plus an 8-probe `antisense_*` add-on, and NCBI785 on a different custom design
carrying real target genes the other three do not measure.

One discrepancy is left open rather than reconciled: the raw panel-designer file gives NCBI785's
design 313 real targets (a 33-gene add-on), while HEST's ingested file carries 321 (41 extra). The
direction and the gene identities agree across both sources; the count does not. Resolving it needs
the processed per-sample feature list rather than the panel-designer JSON.

**This does not affect the benchmark's own targets.** The shipped 50 IDC genes all lie inside the
500-entry intersection, which R2 verified independently via its `shipped_all_on_panel` check.

### 4.3 The scan-resolution difference has no stated cause

Directive 2.2 asked what the sources say about the H&E scan. The answer is that they say nothing:
no 10x dataset page, no part of the Janesick Methods, and no GEO record reached in this task gives
an H&E scanner model or a nominal objective magnification for any of the four samples. GEO's
`Sample_scan_protocol` field reads only "Xenium In Situ Analyzer", which is the fluorescence
instrument, not the brightfield scan.

**The cause of the 0.2125 against 0.2740 against 0.3639 µm/px difference is therefore not
established.** It is not inferred from the pixel-size ratios, which would have been easy and
unjustified.

### 4.4 The IDC contrast, fully enumerated

Listing every variable that differs, which is what this project requires before a contrast is
named:

| pair | donor | block | panel | pixel size | instrument generation |
|---|---|---|---|---|---|
| TENX95 / TENX99 | **same** | **same** | **same** | same | same |
| NCBI783 / NCBI785 | different | different | different | different | same (both prototype) |
| TENX* / NCBI783 | different | different | different (533/541) | different | production vs stated prototype |
| TENX* / NCBI785 | different | different | different (500/541) | different, largest gap | production vs stated prototype |

The Janesick Methods state that study's Xenium runs used "a prototype instrument" with
in-development chemistry, which is a further difference from the production-line TENX dataset that
round 1 did not know about.

Round 1's withdrawal of the "institution shift" label is confirmed and, if anything, understated:
both halves were produced by 10x Genomics staff, and the remaining contrast differs in donor,
block, panel, pixel size and instrument generation simultaneously.

---

## 5. For every probe and term: what differs between its arms

The project's rule is that no term is named before every variable that moves between its arms is
written out. Doing that here is what exposed probe 2's baseline problem and the IDC donor fault.

| probe / term | arm A | arm B | what differs | what does NOT |
|---|---|---|---|---|
| probe 1, slide identity | one slide | another slide | slide, scan session, section, position on the block | patient, tissue type, assay, gene panel, resolution bin |
| probe 1b, scan sub-cluster | session A, 8 slides | session B, 7 slides | scan session, pixel size by 0.0066 µm/px, slide ids | patient, tissue, assay, panel |
| probe 2, resolution class | 5 slides at 0.573 | 2 slides at 0.688 | nominal pixel size, slide identity, and **class size, 5 against 2** | patient, tissue, assay, panel |
| probe 3, adjusted | unadjusted features | features with morphology regressed out | 8 morphology covariates | everything else, since the regression is fit on training spots only |
| IDC `patient` (shipped) | 3 samples train | 1 sample held out | sample; **and on 2 of 4 folds, nothing else — the held-out sample's own donor is still represented** | — |
| IDC `donor_out` | 2 donors train | 1 donor held out | donor, block, panel, pixel size, **and training-set size, 7,015 against ~32,000** | tissue type, assay |
| IDC `replicate_leak` | replicate available | replicate withheld | **only whether the same-donor replicate is in training** | test set, training-set size, everything else |

The class-size asymmetry in probe 2 is the entry that mattered: writing it down is what prompted
the check that found the majority-class baseline sitting exactly where the reported number was.

---

## 6. A defect this interval found in a completed stage, and its fix

Memo § 0 authorises fixing a defect that invalidates a completed stage's numbers, inside the
interval, and saying so. This is one.

**The defect.** R3 reported IDC's `random − patient` total as 0.1210, with the `patient` arm
standing for generalisation to an unseen patient. R5 established that two of IDC's four samples are
one donor. On 2 of the 4 patient folds the held-out sample's own donor is therefore still in
training, so the arm does not measure what its name says, and the reported IDC total is optimistic
by whatever that replicate is worth.

**The fix.** `code/scripts/round2_r5_donor_out.py`, three encoders, IDC only. It reuses R3's
loading, fitting, scoring and within-slide metric unchanged, so the comparison is like-for-like,
and it re-runs the shipped arm as `patient_recheck` to prove equivalence before changing anything.

**Reproduction check first.** `patient_recheck` reproduces R3's IDC patient arm exactly —
0.597598, 0.473880, 0.589765 for `hoptimus0`, `resnet50`, `uni_v2`, against R3's 0.597598, 0.473880,
0.589765; maximum absolute difference **0.000000**. The new script is R3's pipeline.

**Result.** From `donor_out__*.csv`:

| encoder | shipped `patient` (4 folds) | `donor_out` (3 donors) | difference |
|---|---|---|---|
| hoptimus0 | 0.5976 | 0.5789 | −0.0187 |
| uni_v2 | 0.5898 | 0.5784 | −0.0114 |
| resnet50 | 0.4739 | 0.4587 | −0.0152 |
| **pooled** | **0.5538** | **0.5387** | **−0.0151** |

Correcting the donor labels lowers IDC's held-out accuracy by 0.0151, which raises IDC's
`random − patient` total from 0.1210 to about 0.1361.

**But that number is confounded, and I am not reporting it as the leak.** Holding out both TENX
samples removes 28,521 of 35,536 spots, so the corrected fold trains on 7,015 spots against roughly
32,000 for the single-sample folds. Less training data lowers accuracy on its own. The
`donor_out_matched` arm in the same file does not fix this either: it matches downward to the
patient arm's mean training size, which only applies to the two NCBI folds and silently drops the
TENX fold entirely — so its higher value, 0.5815 pooled, is an average over an easier subset and
should not be read as a corrected estimate. That is a design error in my matching, caught on
reading the per-fold training sizes rather than the means.

**The controlled version** holds the test set and the training size fixed and varies only whether
the same-donor replicate is available — see § 6.1.

### 6.1 The replicate leak, measured cleanly

`code/scripts/round2_r5_replicate_leak.py`, results in `r5_idc_replicate_leak.csv`. For each TENX
sample as the held-out test set, two training arms drawn at **the same size, 7,015 spots** — the
size of the NCBI-only pool, which is the binding constraint:

- **with_replicate** — drawn from the other TENX sample plus NCBI783 and NCBI785;
- **without_replicate** — drawn from NCBI783 and NCBI785 only.

Everything else is identical: same test spots, same training size, same pipeline, same metric. The
difference is the value of the same-donor replicate.

| encoder | held out | with replicate | without | leak |
|---|---|---|---|---|
| H-optimus-0 | TENX95 | 0.6342 | 0.5758 | **+0.0583** |
| H-optimus-0 | TENX99 | 0.4700 | 0.3607 | **+0.1093** |
| UNI v2 | TENX95 | 0.6264 | 0.5984 | **+0.0281** |
| UNI v2 | TENX99 | 0.4673 | 0.3750 | **+0.0923** |
| ResNet50 | TENX95 | 0.5036 | 0.4551 | **+0.0485** |
| ResNet50 | TENX99 | 0.4039 | 0.3500 | **+0.0539** |
| | | | **pooled** | **+0.0651** |

Positive in **6 of 6** encoder-slide cells, range +0.028 to +0.109.

**The size of this against what IDC reports.** IDC's entire `random − patient` gap is **0.1210**.
The replicate is worth **0.0651**, or **54%** of it. So on IDC, more than half of what the
benchmark's patient split scores as generalisation to a new patient is recoverable from having
another section of the same tumour in training.

One property of the design to note: the `without_replicate` arm has zero variance across repeats,
because the NCBI-only pool is exactly 7,015 spots and drawing 7,015 from it returns the same set
every time. That is expected, not a bug, and it means the dispersion in the table comes from the
`with_replicate` arm alone.

### 6.2 Figure

![IDC replicate leak](art_5d580e1c-1647-4142-ac6f-d43c112f7ddb)

The controlled comparison, and the leak against IDC's whole reported gap.

---

## 7. Escalations

Under memo § 0 these are recorded rather than halting work.

**7.1 TENX95 and TENX99 are not two patients, and the IDC patient split leaks.** This is a
benchmark issue of the same kind as COAD's labels, and it is the one I would raise with the HEST
authors first, because unlike COAD it comes with a measured cost. HEST's metadata gives the two
samples distinct patient labels; 10x's own dataset page states `donorCount: 1` and describes them
as 5 µm sections of one resected tumour mass. The measured consequence is +0.0651 within-slide
Pearson, 54% of IDC's reported patient gap (§ 6.1). Evidence: `r5_idc_provenance.md` § 1–2,
`r5_idc_replicate_leak.csv`, and the page's own metadata, which I re-verified in the fetched copy.

Note what this does **not** affect: the IDC *task* remains a valid prediction task, and the shipped
50 genes are unaffected. What is affected is the interpretation of IDC's patient-split score as
cross-patient generalisation, and any use of TENX95/TENX99 as two independent samples.

**7.2 IDC's four samples do not share a gene panel.** NCBI785 measures 41 real genes that none of
the other three measure; NCBI783 adds 8 `antisense_*` probes; only TENX95 and TENX99 match. Real
difference, confirmed against the raw GEO panel-designer files, not a control-probe artefact
(§ 4.2). This is the IDC instance of the panel-heterogeneity issue R2 found across tasks.

**7.3 The scan-resolution difference within IDC has no stated cause** in any source consulted
(§ 4.3). Worth raising with the authors as a documentation gap, since resolution is aligned with
patient identity in three tasks and the benchmark gives no provenance for it.

**7.4 A number in the R3 report changes.** IDC's `random − patient` total moves from 0.1210 to
about 0.1361 under corrected donor labels — though as § 6 says, that particular figure is
confounded by training-set size and the clean statement is the 0.0651 of § 6.1. The R3 report is a
delivered document; I have not edited it, and this report supersedes it on that number.

---

## 8. Discrepancies and open questions

1. **The 33-against-41 panel-count gap** (§ 4.2). The raw panel-designer file gives NCBI785 a
   33-gene add-on; HEST's ingested file carries 41. Direction and gene identities agree across
   both sources; the count does not. Unresolved.
2. **Which GEO record NCBI785 is** — GSM7780153 or GSM7780154, the two Sample #1 replicates. Not
   determinable from the sources reached, and it affects no conclusion, since both carry the same
   panel.
3. **HEST-1k's Table A4 reports n = 4 Xenium samples for the Janesick publication** while GEO's
   subseries lists 3 and HEST's own `atlas.py` names 3 (NCBI783/784/785). Noted, unresolved.
4. **NCBI784 exists in HEST-1k but is excluded from the 4-sample IDC task.** If it is the other
   Sample #1 replicate, then the benchmark already excludes one same-donor replicate pair while
   including another — worth asking the authors about, since it suggests the issue was partly
   recognised.
5. **The memo's either/or rule for probe 1's confusion structure does not fit the data** (§ 3.2).
   Both a per-slide and a per-session component are present. I report both rather than forcing the
   choice.
6. **Probe 2 is underpowered**: 7 slides, 5:2 split. Consistent with no resolution signal, but it
   cannot exclude a small one.

---

## 9. What was not checked

- **The `PYTHONHASHSEED=0` sweep across older scripts** (memo § 2.6). New scripts in this interval
  set it; the sweep is idle-capacity work under § 3 item 3 and is not done.
- **The § 1.3 rank supplement, and the § 1.5 and § 2.5 README work.** All three are idle-capacity
  items permitted only once R4 and R5 are complete. They are complete as of this report, so these
  are the next things I can legitimately do — but the report is due now, so they are not done yet.
- **Whether the replicate leak generalises beyond IDC.** LYMPH_IDC, PRAD, COAD and READ all have
  same-patient multi-slide structure, and READ's pairs are same-*specimen* replicates, which is the
  closest analogue. I did not extend the measurement to them.
- **Whether other tasks contain undeclared same-donor pairs.** I checked IDC because R5 pointed at
  it. A systematic provenance audit of all 72 samples has not been done, and given two label faults
  in two tasks examined, the prior that others exist is not low.
- **Probe 3 on the remaining tasks.** Run on the five the plan and memo name, not on CCRCC, HCC,
  LYMPH_IDC or READ.
- **Assumption diagnostics of any kind** on the probe classifiers.

---

## 10. Proposed next step

For the oversight chat to rule on. My proposal, in order:

1. **Report 7.1 to the HEST authors.** It is concrete, sourced to their data's own provenance, and
   quantified. I would send 7.1 and 7.2 together, with the panel table.
2. **Audit the remaining tasks for undeclared same-donor structure** before R6 builds variance
   components on patient labels. R6's whole design rests on the patient being the unit; two of the
   tasks examined so far have patient labels that do not mean what they say. This is a reading task
   like R5, and it is the cheapest insurance available against R6 producing a well-estimated
   decomposition of the wrong quantity.
3. Then the idle-capacity items in § 9, which are already authorised.
4. Then R6, with whatever the audit changes.

I flag one thing in the R6 specification now, while it can still be changed, as memo § 2 invites.
Decision 2.3 says COAD is included carrying `patient_labels_unreliable` and excluded from the
between-patient estimate. On the evidence of § 6.1, IDC needs the same treatment for the opposite
reason — its labels split one donor rather than merging several — so its between-patient component
would be estimated across 3 donors, not 4 samples, and its within-patient component becomes
estimable for the first time using the TENX pair.
