> **Active instruction document for round 3 interval 3, dated 23 September 2026.** The oversight
> chat's decision memo at the A3 gate, handed over by Nicolas. It answers
> `docs/round3_A3_stage_report.md` revision 2 (tag `round3-A3-r2`) and opens interval 3, the last of
> the round. Its transcription into the execution session's operating plan is
> `docs/round3_execution_plan.md` section 13. Not bannered as a closed record, because it is not closed.

# Round 3, decision memo at the A3 gate

23 September 2026. From the oversight chat to the Claude Science session, handed over by Nicolas. Answers `docs/round3_A3_stage_report.md` revision 2 at tag `round3-A3-r2` (commit `5bc4bb3`). This document opens interval 3, the last of the round. Commit it as `docs/decisions/round3_A3_decisions.md` with the active-instruction banner, transcribe sections 3 to 7 into `docs/round3_execution_plan.md`, and flag anything in it that looks wrong in the end-of-round report rather than changing it silently.

---

## 1. The gate

A3 is accepted and interval 3 opens on receipt of this memo. The five decisions the report asks for are in section 2, each with its reason. Section 3 is what the oversight review adds to the report's reading. Sections 4 to 7 are the stages.

Checked against the repository. A2b's arm means, the 138 of 138 count and the anchor at $10^{-15}$ reproduce from `a2_unit_intervention.csv` directly; the five level-scale groups reproduce from `a2_level_scale.csv`; the W3 infinite-interval predicate holds on all 1,932 nominal cells of `a3_by_fold.csv`; the D2 anchor rows, the determinism diff and the D3 status counts read as reported. `A3_report_numbers.csv` agrees with the primary tables everywhere I compared. Nothing in the report is withdrawn.

The gate rule, in the wording Nicolas approved. Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Round 3's remaining gate is B2, the end-of-round report. Contact with anyone outside the project is never the session's decision.

Three errors in the A1 memo, which the report flagged rather than corrected, are acknowledged here so the record is straight. The W3 prediction at $\alpha = 0.1$ said "outside CCRCC's donor design" in the same paragraph that derived $K \ge 9$; CCRCC has $K = 6$ and the derivation was right. Section 2.1 said "two task files" and listed three. And the mechanism-(a) prediction, that the unit-calibrated shortfall would track the between-unit share and $K$, was tested in A2c and failed; section 3.1 says what stands in its place.

---

## 2. The five decisions

**2.1 IDC `audited` is superseded.** D3 establishes from the vendor's own run metadata that `TENX98` and `TENX99` are the replicate pair (the Avaden block) and that `TENX95` and `TENX97` are two sections of a separate BioIVT block, so the benchmark's IDC task is four distinct donors and HEST's shipped labels were right. Create `results/round3/D3_audit/donor_audit_r3.csv` as the round-3 audit file, with the 72 benchmark rows carried from `donor_audit.csv` unchanged except IDC, where `TENX95` and `TENX99` get distinct `donor_id` values and a `donor_label_status` of `verified` citing D3's rows, and with the 76 expansion rows from `donor_lab_audit_ext.csv` appended. `donor_audit.csv` stays frozen and its provenance says it is superseded. Every round-3 table that carries an IDC `audited` row keeps it, tagged `superseded_label_set`, and no further stage runs IDC `audited`. `docs/r5_idc_provenance.md` is frozen; it gets a one-line banner pointing at D3 and this memo, and its line 47 is not edited.

What this does to round 2's results, to be written into the README in H1 (section 4). Property 1 is withdrawn, not left unresolved. The 96% partner confusion between `TENX95` and `TENX99` is two donors from one laboratory, one production instrument, one panel and one pixel size, three weeks apart, which is the session signature of finding 3 seen in a second task, not a donor signature. The R5c figure of $+0.0652$ stands as a measurement and changes its name. It is the value of a same-laboratory, same-instrument slide in the training pool across donors, and `leak_realised_in_shipped_split` for IDC becomes `False`, because the shipped split separates the two donors correctly. READ's $+0.0901$ remains the same-specimen replicate figure and is now the only such measurement in the benchmark. `docs/hest_bench_issue_draft.md` is unsent and its IDC item is struck; the draft stays unsent. Nicolas presented the IDC pair as probably one donor on 21 September and will correct it at the next presentation; the deck's `issue1` slide is on the running list.

**2.2 The D2 layout finding is accepted as a property of the public data, and no re-embedding is needed.** The 28 anchor samples are already embedded from HEST-1k patches, so the expansion sets are internally consistent. What is not known is whether a benchmark result moves when the layout moves, and that is measured rather than assumed. D4 opens with a layout anchor (section 7.1): the A1 harness's `random` and `donor` designs on CCRCC with the HEST-1k-layout embeddings, three encoders, compared with A1's committed CCRCC rows on Pearson and coverage. Expansion results are set beside benchmark results only through that anchor. The README's property list gains property 11, that the benchmark's shipped patches are not the HEST-1k release's patches for the same spots (resampling differs by a few grey levels, correlation 0.96 to 0.99, the kept spot sets differ, and frozen-encoder embeddings differ by a median 6% to 15% relative L2 depending on the encoder, `anchor_check_consolidated.csv`), with the anchor experiment's outcome added when it exists.

**2.3 The D1 criterion is the subset relation.** Patch barcodes are a subset of expression barcodes on all 105 samples, which is the relation HEST's own benchmark code assumes. Expansion analyses use the patched spots only, and every expansion task definition records the unpatched fraction per sample (`TENX95` at 36% is the extreme). Why HEST drops a spot is not pursued this round.

**2.4 D4 is re-scoped, and no round-3 document carries a laboratory term.** D3 leaves the archive with no laboratory contrast at all. The 18 breast Xenium samples are one laboratory, 10x Genomics, in fifteen donor groups and two instrument generations. The 54 kidney samples are two laboratories, Cordeliers and Indiana, separated exactly by tumour status, and further by preservation, region, instrument and pixel size. The source axis this round is therefore a population-and-source shift on kidney, named as such with its list, and D4 is rebuilt around the two things the expansion can still deliver, which are more donors and a hard out-of-population test. Section 7 has the design. The statement at the top of the report, that HEST-1k has no three-laboratory cell, is now the weaker of two limitations; the stronger one is that it has no two-laboratory cell with disease held fixed, and both go in every document that reports a source term and in what Nicolas tells the advisors.

**2.5 A4 absorbs A3's consequences as follows.** W1 and W1b run in no further stage; their result is recorded. HCP at $\alpha = 0.2$ on CCRCC joins A4's width-at-matched-coverage table. The `scaled` against `scaled_clip` comparison is A4's first row. And A4 gains one experiment (A4b, section 4.2) that the benchmark can support and that tests the round's central claim directly, HCP at $\alpha = 0.1$ with $K = 10$ exchangeable donors on CCRCC.

---

## 3. How the oversight review reads interval 2

### 3.1 What A2 established, and what the A1 memo's mechanism (a) becomes

A2b is the result of the interval. On one proper-training set, held-out-donor calibration covers 0.856 and spatial-block calibration covers 0.744, block below unit in 138 of 138 cells, with the block intervals a third narrower (`a2_unit_intervention.csv`). The unit arm did that on 38% of A1's calibration spots and reproduced A1 within 0.0005. So the number of calibration spots is nearly irrelevant, and the level the calibration scores come from is what sets coverage. That is the cleanest single statement the project has, and it goes on the deck as a figure.

A2c refutes the A1 memo's reading that the unit-calibrated shortfall is a small-$K$ effect. Coverage does not track $K$ (Spearman $-0.03$) or the between-unit share ($-0.08$, wrong sign), and a location-shift model with the measured variances predicts 0.89 to 0.90 at every $K$. What the small-$K$ account still explains is the scatter, not the mean. Fold-level coverage is a unit-level random variable with a wide spread (CCRCC 0.25 to 0.98), and the $K \ge 9$ condition is a statement about guarantees, which A3 confirmed to the cell, not about how far below nominal a pooled quantile lands. The unit-calibrated mean shortfall of three to four points is not explained by anything measured so far. The report's own description, that intervals at unit level are about the right width ($w^\star/\hat w = 0.98$) and carry a positive miss asymmetry, is the best current account, and A4's per-decile results will say whether the asymmetry is the upper tail of the predictions (section 3.3).

One caution on the level-scale table (`a2_level_scale.csv`). The level and scale shares are shares of the variance of the shortfall across slides. A constant offset present on every slide contributes to the mean shortfall and not to that variance, so the regression cannot credit it. The mean standardised slide offset $|b_s|/s_y$ is about 0.5 on unit-calibrated slides, with both signs, which is large, and the width absorbs it. The right reading is that slide-level recentring would buy width at matched coverage rather than coverage, which is why it appears in A4 as an oracle width row and not as a coverage repair.

### 3.2 What A3 established

A3 is a clean negative result with its mechanism measured. Feature-based reweighting cannot work here because calibration and test slides are separable at AUC 0.97 or better from the embedding and at a median 0.90 from eight morphology covariates alone. That second figure is new and matters on its own. Tissue composition is slide-specific to nearly the same degree as the encoder's slide signature, so W1b, which was meant to see biology without the scanner, sees the slide anyway. Weights with an effective size of 2% of the calibration set move coverage a long way in whichever direction a handful of spots point, which is what LYMPH_IDC's loss of 0.15 and SKCM's gain of 0.28 both are. No weighting is a repair, and the report is right to say so despite the arithmetic on the two-sample tasks.

HCP behaves exactly as the arithmetic says. Infinite wherever $K + 1 < 1/\alpha$, in 1,932 of 1,932 cells; where finite at $\alpha = 0.2$, over-covering by 10 to 19 points because its upper bound $1 - \alpha + 2/(K+1)$ does not bind at these $K$. The benchmark cannot show HCP at $\alpha = 0.1$ with exchangeable units because no unit-calibrated fold has $K > 6$. That is a consequence of the calibration-unit rule's 25% fraction, not of the donor count. CCRCC has 23 donors in the pool once one is held out, and a calibration fraction near 45% gives $K = 10$. A4b runs it.

### 3.3 Two results the report under-weights

Coverage by predicted-value decile falls from 0.90 in the low deciles to 0.68 in the top decile, under every design (`a2_by_stratum.csv`). This is the $R^2$ ladder's scale error seen from the interval side. The head's predictions are spread 1.84 times too widely, so the highest predictions overshoot, and a symmetric absolute-residual interval centred on an overshooting prediction misses above. It is a conditional-coverage failure the `abs` score cannot fix and the scores in A4 should, since CQR, the scaled score and the NB head all let the interval depend on the prediction. A4 reports every score by predicted-value decile, and the prediction is that the top-decile shortfall closes under CQR and NB and not under `abs`.

`INT5` in CCRCC covers 0.26 under both shift designs and is the only slide below 0.50. It is an outlier of the kind that decides whether donor-level coverage claims hold in the mean or in the tail, and it is one of the 24 slides whose donor labels D3 records as unverifiable. H1 item 4 reads the source for it.

### 3.4 CCRCC's donor labels

D3 records all 24 Cordeliers samples as `donor_label_status = unverifiable`, where round 2 had them `verified` against a GEO series that states no donor identifier, and it flags `INT4` and `INT24` as a possible pair. CCRCC is the powered task for B1 and B2 and the only benchmark task with $K \ge 5$, so this is not a footnote. H1 item 4 spends one hour on the Immunity paper's patient table; if it gives the number of patients, the labels are corroborated at the count level and the file says so. Whatever the outcome, B1, B2 and A4b each run twice on CCRCC, once with 24 donors and once with `INT4` and `INT24` merged, and report both.

### 3.5 Procedure findings that go into `WAYS_OF_WORKING.md`

Three, each tied to the episode that produced it. The scheduler note that says shortening a wall does not help is wrong in the regime the group is now in. With fairshare at 0.007, jobs start through backfill or not at all, and a 16 h limit blocks backfill while a limit at three times the measured runtime started five jobs within minutes; the rule is a limit at about three times the expected runtime, sized from a sibling's `sacct`, never a blanket 16 h. Determinism across nodes holds to $3 \times 10^{-6}$ absolute in widths and exactly in every count, and bit for bit on the same node; provenance therefore records the node, and a byte-identical rerun is a same-node claim. And a provenance `commit` field records the working copy's HEAD, not the script that ran; the D2 first runs show why that is not enough, so every job's provenance also records the md5 of the script file it executed, which D2's rerun already does.

---

## 4. H1. Housekeeping from the A3 escalations (capped at one day in total)

1. The round-3 audit file of section 2.1, and the tagging of IDC `audited` rows.
2. README. Property 1 withdrawn and rewritten as section 2.1 says; property 11 added; known limitations updated for the D2 layout, the subset relation, the CCRCC labels and the determinism note; the `raw_ridge` sentence and everything else untouched.
3. `docs/hest_bench_issue_draft.md` IDC item struck with a dated note; the draft stays unsent.
4. Two reading items, one hour each. The Immunity paper's patient table for CCRCC's donor count and any per-sample donor mapping, and `INT5`'s source record. Record in `donor_audit_r3.csv`.
5. `WAYS_OF_WORKING.md`, the three notes of section 3.5.
6. `docs/round3_execution_plan.md` transcription, including the D4 re-scope.

---

## 5. A4. Scores, the model-based comparator, and the $K \ge 9$ experiment (three days; no gate)

### 5.1 A4a. As specified in the execution handoff section 6.6, with these changes

Scores in the table are `abs`, `scaled` (unclipped), `scaled_clip`, `cqr`, `nb` and `nb_conformal`, three encoders, the A0 designs, all task files except IDC `audited`. The first comparison is `scaled` against `scaled_clip` against `abs`, so the extrapolation defect of the $\hat\sigma$ model is measured once and set aside; report the fraction of folds where the lower clip binds. Every score is reported by predicted-value decile, per design, as the test of section 3.3. Width at matched coverage is the primary table, mean and median width beside each other. HCP at $\alpha = 0.2$ on CCRCC `donor` (from A3's tables, no rerun) is a row of that table. One oracle row is added, the `abs` interval recentred per test slide by $b_s$, with the width that then gives 90% on that slide; it uses test labels, is labelled as a diagnostic, and says what slide-level recentring would be worth in width.

The NB head as specified, with the convergence guard, PIT histogram and KS statistic on `random`, and $\hat\alpha_g$ beside the marginal Fano factor. CQR time-boxed at 20 minutes per task-encoder fit with the 20,000-spot fallback recorded.

### 5.2 A4b. HCP with $K = 10$ exchangeable donors on CCRCC

**Why.** The round's central claim is that valid intervals for a new donor need calibration at the donor level and at least nine donors in the calibration set. A1 to A3 showed the first half and showed that the benchmark's default calibration rule cannot reach the second. CCRCC can, if the calibration fraction rises. This is the one place the claim can be tested on real data this round, and it is the cell the paper's Table 1 needs.

**Design.** CCRCC, `donor` design, one held-out donor per fold, 24 folds (and 23 with `INT4` and `INT24` merged). From the 23-donor pool, hold out 10 donors as $C$ and train on the remaining 13, three calibration draws with crc32 seeds. Score `abs`, three encoders. Four intervals per fold, all at $\alpha = 0.1$: the pooled spot-level quantile (A1's method), HCP with group-equal weights (A3's W3), the one-score-per-group subsample of Dunn, Wasserman and Ramdas (one calibration spot per donor, so $K + 1 = 11$ exchangeable scores, repeated 200 times with the intervals averaged in width and coverage reported per repetition), and, as the control, the same four on `random` with $K$ equal to the spot count. Record the training-set size beside A1's (it falls from 18 to 13 donors) and, as the anchor, the pooled-quantile interval's coverage against A1's CCRCC `donor` row.

**Predictions.** HCP is finite in every fold. HCP's mean coverage over folds is at or above 0.90 and below $0.90 + 2/11$, most likely 0.92 to 0.95, with a width ratio to the pooled quantile between 1.2 and 1.6. The pooled quantile covers about 0.86 as in A1, unchanged by the larger $K$, because its shortfall is not a $K$ effect (section 3.1). The one-per-group subsample covers at nominal in the mean with wide dispersion across repetitions. Training on 13 donors instead of 18 costs Pearson under 0.02.

**Outputs.** `results/round3/A4_scores/a4b_hcp_K10.csv` (fold, draw, encoder, method, coverage, width_mean, width_median, K, n_T, n_C, finite), and `fig_a4b_hcp_K10.png`, coverage against width for the four methods with A1's point marked.

Outputs for A4a as specified, plus `a4_by_decile.csv` and `a4_oracle_recentred.csv`.

---

## 6. B1 and B2. As planned, with four changes

**Inputs.** B1 uses the calibration-fraction-zero `donor` predictions (the H1 mode), as the A1 memo said. IDC $\theta_1$ runs under the four-donor labels. CCRCC runs with 24 donors and with the `INT4` and `INT24` merge, both reported, per section 3.4; the same for B2's semi-synthetic partitions.

**References and positioning.** The four references in the A1 memo's section 3, and the positioning against Salerno, Wu and McCormick (arXiv:2603.11368) and Shirota (arXiv:2608.10356) in the B1 report's opening paragraph, as already transcribed.

**The parallel with A4b.** The B1 report carries a short paragraph setting the donor-limited effective sample size $n_{\text{eff}} \approx n_{\text{donors}} / \rho$ beside the $K \ge 9$ condition, with A4b's result quoted once it exists. One fact from two sides.

**No expansion task in B this round.** The Indiana kidney set is Topic B's second donor set for round 4; it needs a morphology build on the new samples, which is not in this round.

B2 as specified, 200 partitions per setting, the slide-masking variant on PRAD, and the end-of-round report as the gate.

---

## 7. D4. The expansion, re-scoped (two days; inside interval 3)

Every D4 arm runs on HEST-1k-layout embeddings only, on patched spots only, with `donor_audit_r3.csv` as the grouping source and the four contradicted papilla samples (`NCBI563` to `NCBI566`) excluded from any donor unit. Task definitions for the expansion sets are written first, in the A0 format, with `lab`, `source`, `population`, `instrument_generation`, `preservation`, `region` and the audit statuses as columns.

### 7.1 The layout anchor (first, and a condition for reading anything else in D4)

CCRCC, 24 samples, HEST-1k-layout embeddings, three encoders, the A1 harness on `random` and `donor` with A1's seeds and rule. Compare per-task Pearson and coverage with A1's committed CCRCC rows. The prediction is that Pearson moves by less than a tenth of the encoder spread (about 0.01) and coverage by less than its across-fold dispersion, so the layout difference in the embeddings does not reach the results. If either moves more, the end-of-round report says so before any expansion number, and property 11 is extended.

### 7.2 The Indiana donor set, the second multi-donor task

The 23 atlas samples (22 donors; `NCBI701` and `NCBI702` are one participant) plus the three single-donor papilla samples, 25 donor units, one laboratory, one instrument, one objective, fresh frozen throughout. Target genes chosen on training samples only per fold, with R2's reproduction check as the template, 50 genes. Run the A1 harness on `random`, `donor` (25% rule) and the A4b design ($K = 10$; 24 in the pool, 10 calibration, 14 training), `abs` score, three encoders, and the R7-style per-gene decomposition. The difference list for `donor` on this set is donor, disease (reference, diabetic, acute injury), region where stated, section and capture area, and not laboratory, instrument, preservation or pixel size, which are held fixed. This is the first task in the project where donor novelty can be measured with the technical axes fixed, and it is the second test of A4b's claim.

Predictions. `random` at nominal. `donor` at the 25% rule covers 0.85 to 0.88 with the same across-fold scatter as CCRCC. HCP at $K = 10$ is finite and covers 0.90 or above. The per-gene split penalty is smaller than CCRCC's, because the technical axes are fixed.

### 7.3 The kidney population-and-source shift

Two arms on the 54-sample analysis set with training-only gene selection on the intersection panel. The `population_out` arm trains on the 24 Cordeliers ccRCC samples and tests on the 30 Indiana non-tumour samples, and the reverse, with calibration at donor level within the training population. The difference list, written before the term is named, is tissue state (tumour against non-tumour), anatomical region (cortex and papilla against tumour), disease, preservation (partly), laboratory, instrument, objective, pixel size, and the pixel-size provenance flag. It is reported as a population-and-source shift, never as a laboratory term, and its point is to be the hardest shift the project can measure, a floor for coverage and a ceiling for the shift-decodability probe. The R4-style probe runs with population as the target and the same difference list, and with the morphology adjustment, so the fraction of the signature that composition explains is measured on the hardest contrast too.

Predictions. Coverage under `population_out` is below every benchmark design, at or under 0.70, and the failure is on scale and level together. The population probe is at ceiling (balanced accuracy above 0.99) and the morphology adjustment removes a majority of it, unlike within-patient PRAD, because here the tissue really does differ.

### 7.4 Breast Xenium, one laboratory, two instrument generations

Fifteen donor groups, one laboratory. The `donor` design at the 25% rule (pool of 14 groups, $K = 4$), `abs`, three encoders, target genes on the 280-gene common panel chosen on training samples. Two strata are reported, instrument generation (the three Janesick prototype samples against the twelve production-instrument samples) and disease (three IDC, seven DCIS, one CCH/DCIS, and the four vendor-page samples as IDC). The difference list for `donor` is donor, disease, block source, instrument generation for some pairs, run date and slide, and not laboratory, platform, panel or preservation. No source term is reported from this set.

Prediction. `donor` covers 0.82 to 0.87; coverage on the prototype-instrument test slides is lower than on production ones when calibration has no prototype slide, which is the session finding of round 2 in a fourth setting.

### 7.5 What D4 does not do this round

No `lab_out` anywhere. No platform-pair set. No Topic B on expansion data. No morphology build for the expansion samples beyond what the probe in 7.3 needs, which is the shipped CellViT counts and areas per spot computed with the per-sample geometry calibration of round 2.

---

## 8. The end-of-round report

The nine-item format, covering A4, B1, B2, D4 and H1, plus the full predictions-against-outcomes table for the round (every prediction from the execution handoff and the two memos, with its outcome), an "escalations" section, and a closing section titled "What round 3 established", at most one page, written for the deck and for the advisors, in which every sentence names its file. Run the numeric-claim sweep with the corrected command over the README and `docs/round3_*.md`. Tag `round3-final`. Then stop; the round-4 plan is the oversight chat's to write.

---

## 9. Decision boundaries

Unchanged, with two additions. A4b's calibration fraction is fixed at $K = 10$ and is not a session choice. Any D4 result that would be read against a benchmark result waits for 7.1's anchor and is reported beside it or not at all.

---

## 10. Predictions for interval 3, consolidated

| # | stage | prediction |
|---|---|---|
| 1 | A4a | `scaled_clip` narrows the mean width of `scaled` by more than half at equal coverage; the median barely moves |
| 2 | A4a | the top-decile shortfall (0.68 under `abs`) closes to within 0.05 of nominal under `cqr` and `nb_conformal` and stays under `abs` |
| 3 | A4a | NB intervals under-cover under `donor` in the same pattern as `abs`; conformalising restores marginal coverage; $\hat\alpha_g$ is well below the marginal Fano factor and above zero |
| 4 | A4a | the recentred oracle is 20 to 40% narrower than `abs` at 90% on unit-calibrated slides |
| 5 | A4b | HCP finite in every fold, mean coverage 0.92 to 0.95, width ratio 1.2 to 1.6 to the pooled quantile; the pooled quantile stays near 0.86; one-per-group covers at nominal with wide dispersion |
| 6 | B1 | spot i.i.d. standard errors are smaller than donor-clustered ones by a factor of five or more on CCRCC; PPI's $\lambda$ is between 0.3 and 0.9 for the three encoders and near 0 for the permuted predictor |
| 7 | B2 | spot i.i.d. intervals cover under 0.6; donor cluster-robust with the $t$ reference covers 0.85 to 0.92 at $n_L \ge 8$; PPI width ratio below 1 only for the better encoders and rising toward 1 as the between-donor share grows |
| 8 | D4.1 | the layout anchor moves Pearson by less than 0.01 and coverage by less than its across-fold dispersion |
| 9 | D4.2 | Indiana `donor` at 25% covers 0.85 to 0.88; HCP at $K = 10$ finite and at or above 0.90 |
| 10 | D4.3 | `population_out` covers at or under 0.70; the population probe is at ceiling and composition explains a majority of it |
| 11 | D4.4 | breast `donor` covers 0.82 to 0.87; prototype-instrument test slides cover lower when calibration has no prototype slide |
