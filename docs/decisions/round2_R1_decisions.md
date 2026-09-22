# Round 2: decisions on the R0/R1 report and directives for R2/R3

17 September 2026, revision 2. Response from the oversight chat to the R0/R1 stage report at commit `145ba91`. Everything the report asked for a decision on is decided here; a few additional directives follow.

Revision 2 corrects a gating error in revision 1. The round-2 plan sets report-and-wait at R1, R3 and R5. Revision 1 told the session to report at an "R2 gate," which does not exist in the plan. R2 reports on completion and proceeds to R3 without waiting. The next report-and-wait is R3.

---

## Decision 1. Acceptance thresholds (report § 5.1)

**A5 is adopted as the pipeline-identity check.** The report is right that A1 compares two round-2 heads to each other and cannot certify identity with round 1. A5 does, and it passed (110 of 110 cells within 3.7e-4 of round 1's four-decimal table). Record A5 as the check that matters and treat A1 to A3 as identity tests on the head, not on the pipeline.

**Run the float64 exact-solver head, and ship that one to Topic A.** Authorised as a fourth head, `intercept_f64`, using the cholesky solver in float64 on the same PCA-256 features. Under exact arithmetic the three-head identity holds to machine precision, so the thresholds become real tests:

- A1: max abs ΔPearson (intercept − nointercept), both in float64 exact, below 1e-9.
- A2: max abs pred(intercept) − pred(ycentered), float64 exact, below 1e-9.
- A3: max relative error of (train mean pred − train mean target)/mean target, float64 exact, below 1e-10.

If any of these fail in float64, that is a bug, not a floor, and the run stops and reports.

Keep the float32 `lsqr` `intercept` head as the round-1-comparable artifact. Topic A's base predictor is `intercept_f64`. Bit-identity with round 1's float32 arithmetic is not a property Topic A needs; A5 already establishes that the pipeline is the same.

**One new table, because the report surfaced a benchmark property worth recording.** Under `lsqr` the max per-cell ΔPearson between the `intercept` and `nointercept` heads is 3.15e-2. Since the exact solutions are identical, that entire difference is solver non-convergence in one or both fits. That means individual per-gene Pearson values in the faithful protocol carry solver noise of up to a few hundredths. Report, for the `nointercept` head in float32, the per-task mean and max of |Pearson(lsqr) − Pearson(cholesky)|. If task means are around 1e-3 or below, the benchmark's task-level numbers are stable and this is a footnote; if any task mean exceeds 5e-3, it goes in the known-limitations section alongside the inert penalty.

---

## Decision 2. The A4 result and what the intercept head is for (report § 5.2)

**The two-part framing is confirmed.** The intercept was necessary and recovers 0.80 of median $R^2$; $R^2$ stays negative because per-gene means shift between slides and a training-mean intercept cannot track that. Both halves go into the motivation draft.

**Add the scale term so the decomposition is complete.** From the oracle-level result the report already has, one more step closes it. For each (encoder, fold, gene) cell, using the stored columns and no refitting, compute on the test fold

$$\rho = \frac{s_{\hat y}}{s_y}, \qquad r = \text{Pearson}$$

and report the four-rung ladder of fold-median $R^2$:

| rung | what it fixes | value |
|---|---|---|
| faithful | nothing | as observed, −0.95 |
| training-mean intercept | level, from training | as observed, −0.16 |
| oracle level | level, from the test fold | as observed, +0.03 |
| oracle level and optimal scale | level and spread | $r^2$ |

The last rung is the identity $R^2 = -b^2/s_y^2 - \rho^2 + 2r\rho$ maximised over $b$ and $\rho$; the maximum is $r^2$ at $b = 0$ and $\rho = r$. With median Pearson 0.315 that ceiling is about 0.10. Also report the observed median $\rho$: if it sits well above $r$, the head is over-dispersed relative to its own signal, which is the scale miscalibration Topic A's calibration layer is meant to fix.

This turns the R1 result into one figure that assigns the whole $R^2$ deficit to four named causes: level (fixed by an intercept), slide-level mean shift (needs slide information; Topics A and B), scale (needs calibration; Topic A), and the pattern ceiling $r^2$ (the encoder's limit). That figure is the opening of the motivation draft.

**The `ANKRD30A` observation is kept as stated.** A 17-fold swing in a gene's mean between training and test slides is the clearest single illustration in the repository that the slide, not the spot, is the unit of variation. It is a Topic B exhibit as much as a Topic A one.

---

## Decision 3. The `slide_out` task list (report § 5.3)

**Approved: PRAD, COAD, READ.** The review's inclusion of LYMPH_IDC was my error; the metadata is unambiguous that it has four patients with one slide each. The plan's criterion ("any patient with more than one slide") stands and the parenthetical is corrected. LYMPH_IDC uses the single-slide branch, where the same-slide term is `blocked_buffered − patient`.

---

## Directives

**D1. `conch_v15` runs in the R2 batch.** Agreed. Do not resubmit it alone.

**D2. The R2 reproduction check.** The report's reading of `get_k_genes_from_df` is correct and important: the shipped gene lists were computed on `aligned_adata.h5ad` from the processed HEST-1k tree, not on the benchmark `adata/*.h5ad`, and OD1 established the latter is a strict subset of spots.

Proceed as follows, all inside R2 and without waiting on me. First run the reproduction check on the full benchmark `adata` spot set (all barcodes, not the patch subset) and report per task whether the shipped list is reproduced exactly. If any task fails, download `aligned_adata.h5ad` for the benchmark samples only from the `MahmoodLab/hest` repository, filtered by sample ID as was done for the CellViT files, and rerun the check on those. Once the check passes on whichever spot set the shipped lists were built from, the within-fold selection runs on the benchmark `adata` training spots as planned. Record which spot set was needed.

This is a self-check inside R2, not a gate that waits on the oversight chat. The within-fold comparison is uninterpretable if the reimplementation cannot reproduce the shipped lists, so do not run it until the check passes somewhere. The one case that escalates immediately is failure on **both** spot sets, since that means the reimplementation is wrong in a way nobody has identified.

**D3. COAD's dispersion (report § 5.6).** Before R3, print the six values behind sd 0.0017: two folds × three encoders, within-slide Pearson for the `patient` design. If the two folds agree to four decimals for each encoder, that is not a coincidence and something in the fold construction or the scoring is being repeated. Report the six numbers.

**D4. Pixel size cross-check (report § 6 item 7).** HEST's metadata CSV carries `pixel_size_um_embedded` (read from the TIFF header) alongside `pixel_size_um_estimated` (from spot spacing). Add the embedded column to `sample_metadata.csv` if it is present in the HEST metadata for the benchmark samples, and report the per-sample ratio. Agreement within a few percent means the resolution table rests on two independent sources. Disagreement on any sample flags that sample's resolution group as uncertain before R3 and R4 stratify on it.

**D5. R3 submission.** Once, with a wall long enough that the full design set (five arms, three grids, five repeats, three encoders, plus per-gene storage) cannot hit it. Estimate from the R1 timing (about 25 minutes per encoder for a single head) and add a factor of three. If the estimate exceeds the partition limit, split by encoder into three jobs submitted together, never resubmitted individually.

**D6. The `docs/` directory and the report target (report § 2.1 item 5, § 5.5).** Both decisions are correct and stand: round 1's report is frozen at revision 2 as a historical record, round 2's relabelling lives in the round 2 reports and the README, and the plan and review are version-controlled beside the results. The case-insensitive sweep that caught three stale statements the targeted edits missed is the procedure to keep; note it in `ways-of-working` or the README's contributing section.

---

## Order of operations from here

1. `intercept_f64` head and the four-rung ladder (Decisions 1 and 2). Head fitting only; hours, not days.
2. Solver-sensitivity table (Decision 1, last paragraph). Same job.
3. D3 and D4 checks. Minutes.
4. R2 in full, with `conch_v15` in the same batch, including the reproduction check per D2.
5. R3 per D5, with the approved `slide_out` list.

**Report-and-wait after R3.** Items 1 to 4 report on completion and continue without waiting. Two exceptions that stop work and report immediately: a float64 identity failure in item 1, and a D2 reproduction failure on both spot sets.

After R3 is reviewed, R4 through R7 follow as planned, with the next report-and-wait at R5.

---

## On the report itself

The diagnosis in § 3.3 is the right kind of work: three independent lines of evidence, a matched synthetic comparison, and a quantitative match to $\sqrt{n}\,\varepsilon$ growth rather than an appeal to "floating point." The self-audit in § 3.6 caught a check that could not fail, which is the failure mode audits exist for. Two things to carry forward: state acceptance thresholds in the units the arithmetic actually supports, and when a check fails, distinguish "the threshold was wrong" from "the claim was wrong" before proposing a restatement, as § 5.1 does.
