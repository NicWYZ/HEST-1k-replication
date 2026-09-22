# Round 2: decisions on the R3 report and directives for R4 through R7

18 September 2026. Response from the oversight chat to the round-2 stage report covering R0 through R3 (`NicWYZ/HEST-1k-replication`). This memo resolves every item the report asked a decision on, corrects two ambiguities in the execution plan, and sets the next report.

---

## 0. The gate rule, stated so it cannot be misread again

Report-and-wait means that **no stage after the gated stage starts until the oversight chat has reviewed the report and replied.** Not the dependent stages only, and not the expensive ones only. Every stage. The parallelism in the plan's § 11 applies only among stages that sit between two gates. Both readings in report § 8.6 were reasonable given the plan as written; this paragraph replaces the plan's § 0 and § 11 on that point.

R5 is the next gate, so the interval that starts now contains exactly two stages, **R4 and R5**. R6, R7 and R8 do not start, and no part of them is set up, staged or piloted, until the R5 report has been reviewed and answered. Their directives appear in § 2 below so the session knows what is coming and can flag anything in them that looks wrong while R4 and R5 run, not so they can be started early.

**The report is due when R4 and R5 are both complete, and not before.** There are no interim reports and no interim stop-and-report conditions inside the interval. Anything that would previously have halted work (a failed identity check, a threshold exceeded, a label found wrong, a benchmark issue) is handled by the session under the decision boundaries, recorded in an "Escalations" section of the R5 report, and work continues to the end of R5. If a defect invalidates a completed stage's numbers, fix it and rerun inside the interval, and say so in the report.

If R4 and R5 both finish and there is idle capacity before the report is answered, the acceptable work is listed in § 3 item 3. It is housekeeping and supplements to stages already complete, never a downstream stage.

---

## 1. Decisions on the report's open items

### 1.1 Probe 2 classes and chance (report § 8.5)

Use the nominal pixel-size groups, not R0's coarse bins. PRAD patient 1's evaluable classes are the five slides at 0.573 µm/px and the two at 0.688. Exclude the single 0.172 slide from both training and evaluation; it cannot be held out with its class present, and left in training as a third class it only adds a class that is never tested. Two classes, leave-one-slide-out over seven slides, chance 0.5 balanced. The script's two-class variant is primary; drop the binned variant from the report.

Note in the R4 write-up that PRAD carries no embedded pixel size (report § 4.4), so the class labels rest on the spot-spacing estimate alone. For Visium that estimate is the more reliable of the two sources, since it is derived from the known 100 µm pitch, so the probe is well defined. The flag is a caveat, not a blocker.

### 1.2 R4 and R6 (report § 8.6)

**R4 is authorised now. R6 is not**, and neither is R7, because both sit after the R5 gate. Cancelling them was the right call, and under § 0 it was also the correct reading of the intent even though the plan's wording did not force it. The ambiguity is now removed in the direction the cancellation assumed.

### 1.3 The clean gene-selection design (report § 4.5)

Approved as a descriptive supplement, and the framing changes. The report's argument that the shipped-minus-fold-selected gap is a mixture of leakage and gene-set composition is correct, and the Spearman 0.758 against the gene-set effect makes the point quantitatively. But leakage in gene selection acts *through* which genes are chosen, so gene-set composition is not a confound to be removed from the leakage term; it is the mechanism. The two cannot be separated by any design that compares two different gene lists, and the fixed-list rank design does not try to. It measures how much the *ranking* depends on test spots, which is a different and cleaner question.

So run it, with these outputs per task and fold. First, the Spearman rank correlation between the all-spot and training-only normalised-dispersion rankings of the shipped 50. Second, the top-$k$ overlap for $k \in \{10, 25, 50\}$ between the all-spot ranking and the training-only ranking over the full common panel; the $k = 50$ value is close to the report's existing "shared genes /50" column and should be reported beside it. Third, the report's existing gap number, relabelled.

The label for the whole R2 result is **selection-protocol sensitivity**, not leakage. The statement for the README and the eventual paper is that selecting targets on all spots versus training spots changes the target list by roughly half its members, changes measured Pearson by +0.009 on average and by up to +0.044 on individual tasks, and on four Xenium tasks a training-only selection can name genes the held-out slide does not measure. The panel-heterogeneity finding is the benchmark issue; the gap is context for it. The 0.02 escalation threshold in the plan is retired, since the quantity it applied to is not the one being measured.

### 1.4 COAD's patient labels (report § 5.1, § 6.4)

Confirmed as a benchmark issue. For every analysis from here on, COAD is flagged `patient_labels_unreliable` and excluded from any claim about patient-level effects. Its rows stay in every table with the flag visible. READ is flagged `same_specimen_pairs`, and its patient-identity term is labelled a same-specimen term. PRAD is the only task on which a patient-versus-slide claim is made.

The review's COAD exhibit for Topic B is withdrawn, as the report says. The replacement is PRAD, and the framing is corrected: the unit of inference is the patient, with slides nested inside patients. That is what Topic B's cluster-level variance must be built on, and R6 is adjusted accordingly (§ 2.3 below).

### 1.5 Solver sensitivity (report § 4.3)

Footnote, per Decision 1 of the previous memo. Add one sentence to the README's known-limitations section saying that per-gene Pearson under the faithful `lsqr` head carries about $10^{-3}$ of solver noise for most encoders and up to $3 \times 10^{-3}$ for `conch_v1`, `conch_v15`, `ctranspath` and `virchow`, and that task-level means are unaffected. The A2b value of 0.35 (report § 8.7) goes in the same sentence: the faithful head's predictions are not the ridge solution to any tight tolerance, which is why Topic A builds on `intercept_f64`.

### 1.6 The ladder (report § 4.1, § 4.2)

Accepted as the opening figure of the Topic A motivation. One caveat to attach in the text. The scale rung uses the test fold's own optimal $\rho$, so +0.070 is an upper bound on what any calibration layer can recover; the achievable gain is what a calibration fitted on training or calibration data actually delivers. The $\rho / r = 1.84$ over-dispersion result and its ordering with encoder quality are kept as stated and are the concrete target for Topic A.

---

## 2. Directives for R4 through R7

R4 and R5 are authorised and run now. **R6 and R7 are specified here but do not start until the R5 report is answered**, per § 0. They are written down now for two reasons: so the R4 and R5 work is aimed at what comes after it, and so the session can raise any objection to these specifications in the R5 report rather than after R6 has already run on the wrong design.

### 2.1 R4, probes

Run as specified in the plan with the § 1.1 change, and two additions.

Probe 1 (slide identity within PRAD patient 2, fifteen slides at 0.341 to 0.349 µm/px). The metadata shows two sub-clusters inside that range, eight slides at 0.3413 to 0.3418 (MEND139 to MEND146) and seven at 0.3484 to 0.3492 (MEND147 to MEND153). Report the slide-identity confusion matrix and state whether it is block-structured by sub-cluster. Add a two-class sub-cluster probe (leave-one-slide-out, chance 0.5) as a secondary target. If slide identity is decodable but the confusion is mostly within sub-cluster, the signature is per-slide; if the confusion is between sub-clusters, part of it is a scan-session effect.

Probe 3 (composition-adjusted). Run on IDC, PAAD, LUNG, SKCM as planned, and add PRAD patient 2 so that Probe 1 has an adjusted counterpart.

All probes report the `resolution_uncertain` subset separately per Directive D4.

### 2.2 R5, IDC provenance

Reading task, as specified. One addition following the panel-heterogeneity finding. Record each IDC sample's gene panel size and identity (the 541-gene panel versus any add-on), since if TENX95 and TENX99 differ in panel from NCBI783 and NCBI785 that is a fifth variable in the IDC contrast. Also record what the 10x pages and the Janesick methods say about the H&E scan (instrument and nominal magnification), because the 0.2125 versus 0.274 and 0.364 µm/px difference should have a stated cause.

### 2.3 R6, slide-level estimands (does not start until the R5 report is answered)

Run as specified, with the unit corrected. For PRAD, where patients have multiple slides, compute three variance components for each gene's $\hat r$. These are the within-slide sampling variance (spot bootstrap, as planned), the between-slide-within-patient variance, and the between-patient variance. Method of moments on the nested design is fine; report the three and their ratios. For single-slide-per-patient tasks the between-slide component is the between-patient component and should be labelled as such. COAD is included with the `patient_labels_unreliable` flag and excluded from the between-patient estimate.

The nuclear-area-by-resolution table in the plan is now more important than when it was written, since 31 of 72 samples carry `resolution_uncertain`. Report it with the flag as a column.

### 2.4 R7, per-gene decomposition (does not start until the R5 report is answered)

Inputs exist. Use the v4 terms per gene. For all tasks, `random − patient` (total) and the adjacency term; on PRAD only, the novel-slide and patient-identity terms. Do not compute the slide and patient split per gene on COAD or READ. Join to count diagnostics and to R6's between-patient variance, and report the Spearman correlations the plan lists. Relabel the stage "per-gene decomposition"; it inherits § 1.3's terminology.

### 2.5 Consolidated benchmark-properties section

Add a section to the README titled "Properties of HEST-bench found in this replication," with one entry per finding and the file path that establishes it. The current list is the inert ridge penalty and the width-ranked Table A13; the missing intercept and its $R^2$ consequence; per-gene solver noise under `lsqr`; the scan-resolution spread and its alignment with patient identity in PRAD, SKCM and PAAD; gene panels that differ between samples within a task; COAD's patient labels; READ's same-specimen pairs; the selection-protocol sensitivity of the target list. This is the list that will go to David, and eventually to the HEST authors, and it should be maintained from here on rather than assembled later.

### 2.6 Process items

The `zlib.crc32` fix, the explicit parquet schema rule, and the cheapest-outputs-first rule are all correct and are kept. One addition to `docs/WAYS_OF_WORKING.md`: set `PYTHONHASHSEED=0` in every SLURM script's environment as a belt-and-braces measure, since the `hash()` sweep found two instances and a third could exist in code not yet written.

Wall-time estimates for any future R3-scale job should be taken from the 47-hour actuals in this report, not from the R1 timing the previous memo suggested.

---

## 3. Order of operations

1. **R4**, with the § 1.1 and § 2.1 changes.
2. **R5.** It is a reading task and needs no compute, so it can run alongside R4 rather than after it. Both must be complete before the report.
3. If there is idle capacity once R4 and R5 are done, the following may be run, because none of them is a stage after the gate. The § 1.3 rank supplement, which is a supplement to R2. The README work in § 1.5 and § 2.5. The `PYTHONHASHSEED` change in § 2.6. Nothing else.

**One report, when R4 and R5 are both complete, and then stop.** R6 and R7 are not part of it and are not started. No interim reports; escalations go in the report.

---

## 4. On the report itself

Two things worth carrying forward. The determinism check in § 6.6 was unplanned and caught a bug that had already been reported as a result; the practice of re-running and diffing whenever a regeneration is free belongs in `WAYS_OF_WORKING`. And the withdrawal of the 199× ratio, with the reason stated (a ratio against a denominator indistinguishable from zero), is the right way to retract a number. Say what it was, why it was wrong, and what replaces it. The same discipline applies to the review's own withdrawn COAD exhibit, and the report handled that correctly too.
