> **Closed record, dated 22 September 2026.** The oversight chat's decision memo at the A1 gate,
> handed over by Nicolas. It governed round 3 interval 2, which closed at the A3 gate with
> `docs/round3_A3_stage_report.md` (tags `round3-A3` and `round3-A3-r2`). Its transcription is
> `docs/round3_execution_plan.md` section 12; its interval-3 amendments are carried forward, and
> revised where the A3 memo says so, in section 13. Not edited below this banner.

# Round 3, decision memo at the A1 gate

22 September 2026. From the oversight chat to the Claude Science session, handed over by Nicolas. Answers `docs/round3_A1_stage_report.md` and `docs/round3_d0_expansion_proposal.md` at commit `5598204`. This document opens interval 2. Commit it as `docs/decisions/round3_A1_decisions.md` with the active-instruction banner, transcribe sections 4 to 8 into `docs/round3_execution_plan.md`, and flag anything in it that looks wrong in the A3 report rather than changing it silently.

---

## 1. The gate

A1 is accepted and interval 2 opens on receipt of this memo. D1's second condition is met. Nicolas approved the expansion on 22 September, with the sets in section 6.1, and said that storage is not a constraint on Longleaf, so the size of the ask is no longer a reason to narrow it. D1 runs on those sets without waiting for anything further.

Every number in the report that I compared with the connected repository matched its file. That covers the acceptance rollup (`a1_acceptance_summary.csv`), the design table (`a1_coverage_by_design.csv`), the calibration-unit table, all eleven rows of the per-task table (`a1_coverage_by_task_design.csv`), the encoder correlations, the donor-sharing and IDC label tables, and the job accounting. Nothing in the report is withdrawn. Section 2 says where I read the same files differently, and those readings change what A2 and A3 do.

The gate rule, in the wording Nicolas approved, restated because it has been misread twice before. Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Round 3's remaining gates are A3 and B2. D1's own condition is now met, so it runs inside interval 2 like the other stages. Contact with anyone outside the project is never the session's decision.

---

## 2. How the oversight review reads A1

### 2.1 The calibration-unit table mixes two mechanisms, and the number of units is the missing column

The report's central table groups cells by the level of the calibration unit and finds about five points of shortfall at donor and slide level against twenty-one at block level. The number of calibration units per fold, $K$, is in `a1_calibration_unit_table.csv` and in the per-fold `a1_calibration_units__*` files, and it reorganises that table.

| task and design | calibration unit | $K$ | coverage, mean over folds | across-fold sd | fold range |
|---|---|---|---|---|---|
| COAD donor, IDC (all designs), LYMPH_IDC, PAAD, READ | donor, patient or slide | 1 | 0.80 to 0.89 | 0.03 to 0.12 | 0.62 to 0.94 |
| PRAD patient and donor | slide | 2 (one fold), 4 (the other) | 0.93 to 0.95 at $K=2$; 0.80 to 0.82 at $K=4$ | | |
| PRAD slide_out | slide | 6 | 0.897 | 0.086 | 0.57 to 0.98 |
| CCRCC donor | donor | 6 | 0.864 | 0.140 | 0.25 to 0.98 |
| CCRCC patient | patient | 5 | 0.856 | 0.087 | 0.70 to 0.96 |
| HCC, LUNG, SKCM, and COAD's fold that trains on TENX111 | block | 5 to 9 | 0.55 to 0.76 | 0.02 to 0.05 | |

Fold-level values are from the `a1_by_fold__*__main.csv` and `__slideout.csv` files, `abs` score, all twelve encoders pooled.

Two different things are happening.

**Mechanism (a), too few units at the right level.** In every task except CCRCC and PRAD, calibrating "at donor level" means calibrating on one donor. With $K$ calibration units, the realised coverage on a new unit is a unit-level random variable, and the table shows exactly that. It is not systematically low; it scatters. CCRCC's 24 folds range from 0.25 to 0.98, and the $K=1$ tasks have across-fold standard deviations of 0.03 to 0.12 against 0.002 to 0.003 under `random`. The mean shortfall of about five points is the average of that scatter.

**Mechanism (b), calibration below the level of the test unit.** In the two-sample tasks, and in COAD's fold that trains on TENX111 alone, the calibration set is carved out of the one training slide as spatial blocks, so the calibration scores are within-slide residuals and the test scores are new-slide residuals. This failure is systematic. Across-fold standard deviations are 0.02 to 0.05 and the shortfall is 0.14 (HCC) to 0.28 (LUNG). Nothing done inside those tasks can repair it, because a second slide would be needed to put slide-level variation into the calibration set.

Why mechanism (a) is expected, and bounded by $K$. Take one score per calibration unit, so that the $K$ calibration scores and the test unit's score are exchangeable at the unit level. Split conformal at level $1-\alpha$ uses the $\lceil (K+1)(1-\alpha) \rceil$-th smallest of the $K$ calibration scores, and that index exceeds $K$ when

$$(K+1)(1-\alpha) > K \quad\Longleftrightarrow\quad K < \frac{1-\alpha}{\alpha},$$

in which case the only valid interval is the whole line. At $\alpha = 0.1$ that is $K < 9$; at $\alpha = 0.2$ it is $K < 4$. So with the benchmark's donor counts, no distribution-free 90% interval for a new donor exists in nine of the eleven task files, and the pooled spot-level quantile A1 uses is not a valid substitute; it treats thousands of correlated spots as thousands of units, and pays with the scatter in the table. The two task files that clear the bar are none at $\alpha = 0.1$ and CCRCC, PRAD's $K=4$ fold, and PRAD `slide_out` at $\alpha = 0.2$. This is the same arithmetic as Topic B's effective sample size. The unit that carries the guarantee is the donor, and the benchmark has too few of them. It makes track D a Topic A need, not only a Topic B need.

What this changes in the report's framing. "The calibration unit predicts coverage" is right, but the unit table pools $K=1$ folds with $K=6$ folds and pools mechanism (a) with mechanism (b). "Donor-level and slide-level calibration are indistinguishable" should be read as "both are small-$K$", not as a property of the level. And the COAD recovery of 0.145 is not from the grouping variable alone. Under shipped labels COAD's two folds are one $K=1$ slide-calibrated fold at about 0.85 and one block-calibrated fold at about 0.55 (`a1_by_fold` COAD `patient` rows, range 0.548 to 0.868); under `donor_id` every fold trains on three donors and calibrates on one. Both the labels and the fold structure changed. Section 4.1 adds the experiments that separate the two mechanisms.

### 2.2 The `scaled` score under `random` is a finding, not nothing

Section 6.4 of the report says `scaled` buys nothing at this stage. Under `random` it does something specific. With the `abs` score, slide-mean coverage on CCRCC is 0.881 and on IDC 0.877, while pooled coverage is 0.900 (`a1_coverage_by_task_design.csv`, `a1_aggregation_note.csv`); the gap means coverage varies across slides even without any shift, with the larger slides over-covered and the smaller ones under-covered. With `scaled`, every task's slide-mean coverage under `random` is 0.898 to 0.902 with across-encoder sd under 0.001. So the scaled score delivers slide-conditional coverage in distribution where the absolute score does not. That is a conditional-coverage result and belongs in A2.

The width explosion under shift is a separate defect. Mean `scaled` width is 11.6 under `patient` and 16.5 under `donor` with across-cell standard deviations of 22.7 and 49.0, so the means are set by a few cells (IDC audited `donor` at 75.0, PAAD `patient` at 39.3). The $\hat\sigma$ model extrapolates on shifted features. A3 and A4 carry a clipped variant (section 4.2) and report medians beside means.

### 2.3 Encoder quality, reported as ranges

The correlation of $+0.74$ under `random` is computed over a coverage range of 0.0018 (0.8926 to 0.8944, `a1_encoder_quality_correlation.csv`), which is noise. Report the coverage range across encoders per design, which is under 0.02 everywhere, and state the conclusion as it stands in the file. Coverage is a property of the calibration design; encoder quality changes width, which the next reports should show by encoder.

### 2.4 The `slide_out` donor-sharing contrast is available within PRAD

The 216 sharing folds against 36 non-sharing folds is a between-task comparison, as the report says. But the 120 folds excluded because the flag varied across the three calibration draws are the folds that hold the within-slide contrast. For one PRAD test slide, one draw's calibration set contains a same-donor slide and another's does not, with the training set fixed. Section 4.1 uses them and adds a deliberate arm.

### 2.5 PRAD's two folds are not alike

PRAD's mean of 0.875 under `patient` is the average of a fold at 0.93 to 0.95 and a fold at 0.79 to 0.82. The fold that holds out patient 1 (eight slides at 0.57 to 0.69 µm/px), trained on patient 2's fifteen slides and calibrated on four of them, covers 0.79 to 0.81 at a width of 1.8 to 1.9; the reverse fold, calibrated on two of patient 1's slides, covers 0.93 to 0.95 at a width of 2.6 to 2.7 (`a1_by_fold__hoptimus0__main.csv`, `a1_calibration_units__hoptimus0__main.csv`). The fold with more calibration slides is the one that under-covers, so $K$ is not the explanation there. What sets the quantile is the calibration set's own between-slide spread, and patient 2's slides, one scanning session apart, are more alike than patient 1's. That is mechanism (a) seen from the other side, and it is an A2 stratum with the session structure and resolution class of each side written out.

### 2.6 The D0 institution set is not a laboratory contrast, and the archive has one that is closer

The proposal's difference list for the kidney set names the pixel-size provenance flag. It omits the differences that the dataset titles state. From `expansion_set_members.csv` and `hest_inventory.csv`, the three kidney arms are ccRCC tumour (Sorbonne, 24 samples, 0.457 µm/px, the existing CCRCC task), healthy and injured kidney cortex from an atlas study (Washington University, 23 samples, fresh frozen, 0.758 µm/px estimated), and kidney papilla from stone-disease patients (Indiana, 7 samples, fresh frozen, 0.758 µm/px estimated, no donor labels). A `lab_out` term on that set would be tumour against non-tumour before it was anything about a laboratory, and cortex against papilla after that. This is the naming failure of round 1 again, caught before the term was named rather than after.

Holding organ, technology, oncotree code and disease state fixed, no cell in HEST-1k has three laboratories with three donors each; that part of the proposal stands. The cell that comes closest on the criteria that matter is breast Xenium IDC. 18 samples, 22.9 GB, all FFPE, all IDC, all 541-gene panels, from two generating sources with four donors each (10x Genomics, seven samples across the Janesick paper and the vendor pages; an unresolved 2025 study, eleven samples, four patients, `TENX191` to `TENX202`), four of them already the benchmark's IDC task. Pixel sizes are 0.21 to 0.36 µm/px and the provenance flag is set on three of 18. It is two arms, not three, and the second arm's laboratory is unresolved until D3 reads it. But disease, platform and preservation are held fixed, which the kidney set cannot offer.

The same inventory changes the IDC attribution question. In HEST v1.3.0, `TENX95` (11,845 spots, pre-designed panel) has a sibling `TENX97` (11,845 spots, custom add-on panel, same patient label), and `TENX99` (25,080 spots, entire sample area) has a sibling `TENX98` (26,070 spots, same title, same patient label). The vendor's "Replicate 1 / Replicate 2" language that round 2 read as tying `TENX95` to `TENX99` most plausibly describes `TENX98` and `TENX99`, and the 2.1-fold spot-count gap that argued against the one-donor reading is a section-area difference. HEST v1.3.0 gives `TENX95` and `TENX99` different patient labels, which is what the benchmark shipped. This is a reading for D3 (section 6.2), not a conclusion, and the `idc_attribution_unresolved` flag stays until D3 reports. What A1 already shows is that merging the pair does not move coverage (section 6.6 of the report), which is consistent with either reading.

---

## 3. Literature, and what it settles

**Hierarchical conformal.** Lee, Barber and Willett, "Distribution-free inference with hierarchical data", arXiv:2306.06342 (2023, revised August 2025; ACM Journal of Data Science, DOI 10.1145/3786352). The oversight handoff named Tibshirani as the third author; that was wrong. Their hierarchical conformal prediction (HCP) for a test point from a new group gives every calibration group total weight $1/(K+1)$, spread equally over that group's $N_k$ observations, and gives the test group the remaining $1/(K+1)$ as an atom at $+\infty$. The interval is the $(1-\alpha)$ weighted quantile. Theorem 1 gives finite-sample marginal coverage at least $1-\alpha$ for any $K \ge 1$ under hierarchical exchangeability, with an upper bound of $1 - \alpha + 2/(K+1)$ when scores are distinct. The atom at $+\infty$ has mass $1/(K+1)$, so the interval is finite only when $1/(K+1) \le \alpha$, which is the $K \ge 9$ condition of section 2.1 again. The predecessor is Dunn, Wasserman and Ramdas, "Distribution-free prediction sets for two-layer hierarchical models", JASA 118(544), 2023, arXiv:1809.07441, whose repeated-subsampling method is the one they recommend when a guarantee is required. HCP is a one-line weight choice in A3's existing weighted-quantile machinery, so A3 gets a W3 arm (section 4.2).

**Prediction-powered inference under dependence.** Two papers have appeared since June 2026, which the landscape document flagged as the pivot trigger. Salerno, Wu and McCormick, "Spatially robust inference with predicted and missing at random labels", arXiv:2603.11368 (March 2026), a doubly robust estimator with a Conley-style spatial HAC variance and a correction for cross-fitting, asymptotic, with a two-way clustering extension in an appendix. Shirota, "Design-based prediction-powered inference for spatial data", arXiv:2608.10356 (August 2026), a finite-population difference estimator with design-based variance. Neither treats units nested in groups, neither has a donor-level unit of inference, and neither mentions spatial transcriptomics or histology. No pivot. Topic B's claim is the hierarchical one, that the effective sample size is set by donors and that spatial dependence within a slide is the smaller part of the problem, and B1 and B2 must position against both papers by name. The donor cluster-robust variance in B1 is the standard sandwich estimator applied to the PPI influence function; cite Cameron and Miller, "A practitioner's guide to cluster-robust inference", Journal of Human Resources 50(2), 2015, and MacKinnon, Nielsen and Webb, "Cluster-robust inference: a guide to empirical practice", Journal of Econometrics 232(2), 2023, for the small-$G$ behaviour and the $t_{G-1}$ reference. Fisch et al., "Stratified prediction-powered inference for hybrid language model evaluation", arXiv:2406.04291 (2024), is the published stratified variant and the nearest relative of a donor-stratified estimator; read it before B1 and say in the B1 report how the donor-clustered estimator differs.

---

## 4. Interval 2 stages

Interval 2 is H0, A2, A3 and D3, with D1 and D2 once Nicolas approves the sets. Order is H0, then A2 and A3 in that order (A3 needs A2's per-fold tables), D3 alongside from the start since it is reading. Memory ask for every job is 16 GB on 4 CPUs (A1 peaked at 12.0 GB on `virchow`, `a1_job_accounting.csv`); wall as the work needs; harness ceiling from queue time plus runtime; record the partition actually used.

### 4.0 H0. Housekeeping from the A1 escalations (capped at one day in total)

1. Fix the sweep command printed in `docs/WAYS_OF_WORKING.md` so that it is the one `code/scripts/sweep_table.py` runs, with `--derived .verify-derived` and `--always results/summary/deck_numbers.csv`. Fifteen minutes.
2. `docs/r5_idc_provenance.md`. Two hours of triage, then stop. What is fixable in that time is fixed; what remains is left, the document is bannered as a closed record of a reading task and swept under the `historical` class, and the per-document table for the whole docs tree goes into the A3 report so that the remaining five unresolved claims are located.
3. README known limitations gain two lines. One for the derived-claim formula in `round2_R3_stage_report.md` that cites a gitignored parquet and cannot resolve in a clone. One for COAD `TENX111`'s spot count, after a one-hour check of where `sample_metadata.csv`'s 6,643 came from (HEST's own metadata table before or after tissue filtering is the likely source) against the AnnData's 6,138; if the hour does not settle it, record both values and the likely cause.
4. README properties. Property 2 (COAD) gains one sentence, that HEST v1.3.0 corrects the labels upstream (`TENX147` to Patient 5, `TENX148` to Patient 2, `benchmark_crosscheck.csv`), which corroborates the audit. Property 1 (IDC) gains the sibling observation from section 2.6 marked as pending D3.
5. Determinism. Rerun the `resnet50` A1 job unchanged (40 minutes) and diff every summary CSV and the per-gene parquet against the committed run. Report byte-identical or not, and if not, which columns moved. This closes H4.
6. `docs/round3_execution_plan.md`. Record that `slide_out` is defined only on PRAD, READ and IDC-audited, that the handoff's multi-slide list was wrong, and transcribe this memo.

### 4.1 A2. Conditional coverage and the anatomy of failure (two days; no gate)

Everything in the handoff's A2 stands (strata, the level-versus-scale decomposition, the per-gene join with R7, `fig_a2_anatomy.png`). Six items are added. Items A2b and A2c are the important ones; they are the experiments that decide whether section 2.1's two mechanisms are real.

**A2a. Strata, as planned, plus three.** Test slide; `resolution_group` and session; `cal_shares_session_with_test`; predicted-value decile; gene; neoplastic-fraction tertile; `donor_label_status`. Three are added. The `random` design by test slide for `abs` against `scaled` (section 2.2), reported as the across-slide standard deviation of coverage per task and score. PRAD by fold, with the held-out patient, its session structure and its resolution class written out (section 2.5). And $K$, the number of calibration units, as a stratum for every fold.

**A2b. The calibration-unit intervention.** On every task file with at least two units in the training pool (CCRCC, LYMPH_IDC, PAAD, COAD under `donor_id`, IDC under both label sets, PRAD, READ), for each `donor` fold and three encoders (`hoptimus0`, `uni_v2`, `resnet50`), hold the test set $E$ fixed and build one proper-training set $T$ and two calibration sets from the same pool. $C_{\text{unit}}$ is the A1 calibration set (held-out units). $C_{\text{block}}$ is a set of buffered spatial blocks (grid 6, 2.5-pitch buffer, about 20% of blocks) carved out of the slides that form $T$. $T$ is the A1 proper-training set minus $C_{\text{block}}$, and it is the same $T$ for both calibration sets, so the head, the scaler and the PCA are fit once per fold. The only thing that differs between the two arms is where the calibration scores come from. Size-match $C_{\text{block}}$ to $C_{\text{unit}}$ in spot count by subsampling the larger. Report coverage and width under both, per fold, and the difference with its across-fold dispersion.

Prediction. $C_{\text{block}}$ under-covers the held-out donor by an amount of the same order as the two-sample tasks' shortfall (0.10 to 0.20), while $C_{\text{unit}}$ reproduces A1. If the two arms cover alike, mechanism (b) is wrong and the two-sample tasks fail for another reason (training diversity, training size), which the report should then say.

**A2c. Coverage against $K$ and the between-unit share of the score.** Add a harness flag that writes, per (fold, calibration draw, unit, gene), the count, mean, variance and 0.5 and 0.9 quantiles of the calibration scores, and the same for the test unit, to `a2_score_moments__<enc>.parquet` with an explicit schema. From it compute per (fold, gene) the between-unit share of the calibration-score variance (variance of unit means over total, with the usual finite-sample correction) and tabulate observed coverage against $K$ and that share, for `abs`, over all folds of the `patient`, `donor` and `slide_out` designs. Then a small simulation. For each fold, draw $K$ unit means and one test-unit mean from a normal with the fold's estimated between-unit variance, within-unit residuals from a normal with the fold's within-unit variance, pool the $K$ units' scores, take the $0.9$ quantile, and record coverage on the test unit; 1,000 replicates per fold. Report the simulated expected coverage beside the observed one, per fold and pooled by $K$. No refitting is needed if the moments are written from the A1 harness rerun in moments-only mode for the three encoders.

Prediction. Observed shortfall grows with the between-unit share and shrinks with $K$; the simulation reproduces the fold-level means to within their across-fold dispersion; and the block-calibrated folds sit below the simulated value, because their calibration scores do not contain the between-slide component at all.

**A2d. Donor sharing within PRAD.** From the A1 per-draw files, for each PRAD `slide_out` test slide, compare coverage between calibration draws that include a same-donor slide and draws that do not, with the test slide fixed; report the paired difference over test slides. Then add one arm, `slide_out_cal_other_donor`, in which the calibration slides are drawn only from the other donor's slides, three draws, on PRAD, three encoders. Write the difference list before naming the term. The arms differ in whether calibration shares the test slide's donor, and, in PRAD, in resolution class and session, since each patient's slides come from one scanning configuration; say so.

Prediction. Same-donor calibration covers higher, by a few points, and the effect is smaller than the between-task figure in the report.

**A2e. Width by encoder.** Mean and median `abs` width per encoder per design, joined to benchmark Pearson, as the counterpart of section 2.3. Prediction. Width orders with encoder quality under every design while coverage does not.

**A2f. The level-versus-scale decomposition, as planned**, run separately for the block-calibrated folds and the unit-calibrated folds. Prediction. Block folds fail on level (asymmetric misses, large $|b_s|/s_y$); unit-calibrated folds fail on both with no consistent sign, since each fold's miss is a unit-level draw.

Outputs under `results/round3/A2_conditional/`, with `a2_by_stratum.csv`, `a2_level_scale.csv`, `a2_pergene_join.csv`, `a2_unit_intervention.csv`, `a2_coverage_vs_K.csv`, `a2_simulated_coverage.csv`, `a2_prad_donor_sharing.csv`, `a2_width_by_encoder.csv`, `fig_a2_anatomy.png` and `fig_a2_coverage_vs_K.png`. Summaries before parquets.

### 4.2 A3. Weighted and hierarchical conformal under slide, session and donor shift (two days; gate)

The handoff's A3 stands in structure. Designs `patient`, `donor`, `slide_out` with `random` as the control; three encoders; the weighted quantile with the test point's own weight in the normaliser; the $n_{\text{eff}}$ diagnostic per test slide; the acceptance checks. Four changes.

**Scores.** `abs` is primary. `scaled` runs with $\hat\sigma$ clipped to the 1st and 99th percentiles of the calibration set's $\hat\sigma$ values, named `scaled_clip`; the unclipped `scaled` is not run in A3 (A4 compares them). Report median width beside mean width everywhere.

**Weight estimators.** W1 as specified (logistic regression on PCA-256, class-balanced, fixed $C$, clipped at the 99.5th percentile, with AUC and clipping rate). W1b, new, the same classifier on the eight `morphology_v2` covariates only (nuclear count, mean and median area, five class fractions), which sees tissue composition and not the slide signature. W2 as specified. W3 is HCP. For calibration spot $i$ in calibration unit $k$ with $N_k$ spots, $w_i = 1/N_k$, and the test point's own weight is $1$, so that each unit and the test point carry $1/(K+1)$ of the normalised mass; the unit is the fold's recorded `calibration_unit`. Run W3 at $\alpha = 0.10$ and $\alpha = 0.20$. Where the weighted quantile is infinite, which it is whenever $K + 1 < 1/\alpha$, record the interval as infinite, count it, and also report the interval at the largest feasible level for that fold, $1 - 1/(K+1)$, which is the maximum calibration score, with its realised coverage against its guaranteed level. Do not silently substitute a finite interval for an infinite one.

**Difference lists.** For each weighting, write what the weights can see. W1 sees everything the encoder represents, including the slide signature; W1b sees composition only; W2 sees resolution group and session; W3 sees the unit structure and no features.

**Acceptance**, as specified, plus one. On `random`, W3 at $\alpha = 0.1$ has $K$ equal to the spot count and reproduces the unweighted interval to $10^{-6}$ in coverage and width.

Predictions, written here so that the report can quote them.

1. W1's classifier separates calibration from test at AUC above 0.9 on every fold whose calibration and test sets are different slides (round 2's slide probes at 0.87 to 0.95 predict this), $n_{\text{eff}}$ collapses to under 5% of the calibration size, and W1 coverage moves little from unweighted. Where W1 does help is CCRCC and PRAD `slide_out`, where several calibration units exist and some resemble the test unit.
2. W1b keeps $n_{\text{eff}}$ above 30% of the calibration size and moves coverage by a small amount, in the direction of nominal, most on IDC and CCRCC where composition varies across donors.
3. W2 has no support on the PRAD and SKCM `patient` folds and falls back, as the handoff predicted.
4. W3 is infinite at $\alpha = 0.1$ on every fold with $K \le 8$, which is every fold outside CCRCC's donor design; at $\alpha = 0.2$ it is finite on CCRCC, PRAD's $K=4$ fold and PRAD `slide_out`, and its coverage there is at or above 0.80 with an upper bound near $0.80 + 2/(K+1)$. The feasible-level fallback covers at or above its guaranteed level $K/(K+1)$ in the mean over folds. On block-calibrated folds W3 does nothing, because its guarantee is for a new block of the training slide.
5. No weighting repairs the two-sample tasks.

Outputs under `results/round3/A3_weighted/`, `a3_by_task.csv` with weighting in {none, W1, W1b, W2, W3}, score, $\alpha$, coverage, mean and median width, interval score, `neff_median`, `clip_rate`, `auc`, `no_support` count, `n_infinite`, `feasible_level`; `a3_by_slide.csv`; `fig_a3_coverage_vs_neff.png`; and `fig_a3_hcp_by_K.png`, coverage against $K$ for W3 and unweighted at both $\alpha$.

Report A2 and A3 together, predictions against outcomes, and stop.

---

## 5. Changes to the interval 3 stages, recorded now, specified in full at the A3 gate

**A4.** Add `scaled` unclipped against `scaled_clip` as the first comparison, so the extrapolation defect is measured. Include W3 at $\alpha = 0.2$ on CCRCC in the width-at-matched-coverage table. Otherwise as planned.

**B1.** Use the harness's calibration-fraction-zero `donor` predictions (the H1 mode), so that every spot's prediction comes from a head trained on all other donors, rather than the A1 predictions whose training pool lost the calibration units. Cite the four references in section 3 and position against Salerno et al. and Shirota in the report's opening paragraph. Add a paragraph deriving the parallel between B1's donor-limited effective sample size and section 2.1's $K \ge 9$ condition; it is one result seen from two sides and belongs in the paper's framing. Otherwise as planned.

**B2.** As planned.

**D4.** The `lab_out` arm is renamed `source_out` (test on one generating source, train on the others), and no report calls it a laboratory term unless D3 has established that the sources differ in laboratory and agree in disease, tissue, preservation and platform. On the kidney set, add a `population_out` arm (train on Sorbonne's tumour slides, test on Washington University's non-tumour slides, and the reverse) and name it as a population-shift term with its difference list written out. On the breast Xenium set, `source_out` is a two-arm contrast and is described as such. The platform-pair set is not embedded this round, so no D4 arm runs on it.

---

## 6. Track D

### 6.1 The sets, approved

Nicolas approved the expansion and stated that storage is not a constraint on Longleaf. That removes the only reason the platform-pair set was going to be deferred, so all three sets are downloaded. What has not changed is that GPU time and reading attention are still scarce, so section 6.3 embeds only what round 3 analyses, and section 6.2 audits only what round 3 groups by.

Two of the sets are also widened, because the reason each exclusion was made was a judgement D3 is better placed to make, and keeping the excluded samples on disk costs nothing now.

| set | samples | GB | already in benchmark | round 3 use |
|---|---|---|---|---|
| kidney Visium, the whole human cell | 58 | 23.3 | 24 | Topic B's second donor set (Washington University, 22 labelled donors, one source, one protocol) beside CCRCC's 24; Topic A's population-shift arm; the Washington University against Indiana pair as the only kidney contrast that holds disease class and preservation fixed |
| breast Xenium IDC | 18 | 22.9 | 4 | the two-source contrast that holds disease, platform and preservation fixed; extends IDC from 4 to 18 samples; carries the `TENX` siblings that D3 needs |
| platform-pair | 32 | 25.8 | 5 | none. Downloaded and left on disk for round 4 |
| all three | 105 | 70.3 | 31 | |

Sizes and counts are from `hest_inventory.csv` (`bytes_four_components`), after removing the ids the inventory flags as duplicates. The three sets overlap, so the union is smaller than the sum.

The kidney set is the whole human kidney Visium cell, 58 samples, rather than D0's 54. The four extra are three KTH samples the proposal excluded as fixed organoid material on the strength of a `Treated` disease-state string, and one 10x vendor-page sample excluded because a product page is not a generating laboratory. Both exclusions may well be right, and neither is a reading D0 could make from the metadata alone. Download them, leave them out of every set definition, and let D3 say whether they belong.

Sample ids for breast Xenium IDC are the 18 human samples with organ Breast, technology Xenium and oncotree IDC in the v1_3_0 inventory. Write them into `expansion_set_members.csv` under `institution_breast_xenium` with the selection rule stated, and write the four kidney additions in as `kidney_visium_cell_extras` with the reason each was excluded from the analysis set, before D1.

### 6.2 D3 starts now (reading; capped at two days, and it may run into interval 3)

D3 does not need the download. It reads source records for the candidate sets from the inventory, and its output decides how D4 is framed. In priority order.

1. Breast Xenium IDC. For the eleven `TENX191` to `TENX202` samples, resolve the generating laboratory, scanner, section provenance and donor labels from the study (the inventory's `study_link` is a bioRxiv URL with a non-standard prefix; try the DOI, the title and the 10x dataset page it may point at). For the seven 10x samples, establish from the vendor pages and Janesick et al. 2023 which sections come from which block, and specifically what "Replicate 1" and "Replicate 2" name. Two hours on the `TENX95`/`TENX97`/`TENX98`/`TENX99` question, then record the answer or the impasse in `donor_lab_audit_ext.csv` with a citation per row.
2. Kidney Visium. For the Washington University and Indiana samples, donor ids, disease per sample (healthy, AKI, CKD, stone), anatomical region, preservation, scanner and pixel size from the source records (the atlas study's supplement and the GEO or HuBMAP records), not from HEST's fields. Record `lab_label_status` and `donor_label_status` per sample as `donor_audit.csv` does.
3. For every sample in the two analysis sets, `resolution_uncertain` re-derived from what the source states about the scanner and objective, where it states anything.
4. The four kidney samples held out of the analysis set, if time remains inside the cap. Whether KTH's three are tissue or fixed organoid material, and whether the 10x vendor-page kidney sample has a resolvable generating laboratory. If the cap is reached first, they stay out and the report says the question was not reached.

No grouping by donor, source or laboratory happens on the expansion data before this file exists.

### 6.3 D1 and D2

D1 downloads all 105 samples, in HEST-1k's own layout, including the 31 already in the benchmark; do not try to reuse the benchmark copies. Order is kidney, then breast Xenium, then platform-pair, so that a transfer problem stops the set round 3 does not need rather than one it does. Four components only, `patches/`, `st/`, `cellvit_seg/` and `metadata/`, and no `wsis/`. Record the HuggingFace revision and the sample list in `PROVENANCE.txt`, check the filesystem before and after, and verify that every expected file arrived and that patch counts match the expression files' spot counts.

D2 embeds the kidney and breast Xenium sets only, 76 samples, with `hoptimus0`, `uni_v2` and `resnet50`. The platform-pair set stays on disk unembedded until round 4; downloading it was free, and a GPU queue is not. One anchor check is added. For the 24 CCRCC and 4 IDC samples that exist in both layouts, the new embeddings from the HEST-1k patches must equal the cached benchmark embeddings for the same encoder to the float32 floor, about $10^{-5}$ relative. If they do not, the two layouts' patches differ, and that has to be understood before any expansion result is read.

### 6.4 What the advisors are told

Nicolas reports the selection to the advisors; the session does not contact anyone. For the record, the statement that goes with it is that HEST-1k contains no organ-by-technology cell with three laboratories at three or more donors each once disease state is held fixed, which was checked across all 46 cells (`organ_technology_ranking.csv`). The institution axis this round is therefore a two-source contrast, and a genuine multi-laboratory test of the same tissue and platform would need data from outside HEST-1k. That limitation is stated in every round-3 document that reports a source term, and it is a finding about the public archive rather than about this project.

---

## 7. The A3 report

The nine-item format of the handoff's section 8, with A2's results in full and D3's status. Add, as item 4, the difference list for every weighting in section 4.2 and for the A2b and A2d arms. Add the per-document table from H0 item 2. Numbers at the precision the comparison needs, relative scale stated, full precision in the files. Run the numeric-claim sweep with the corrected command over the README and `docs/round3_*.md` before handing over. Tag `round3-A3`.

---

## 8. Decision boundaries

Unchanged from the handoff's section 9, with two additions. Any fold in A2b where $T$ cannot be formed with at least 1,000 spots after the blocks are carved out is dropped and listed, not shrunk further. Any D3 finding that changes a benchmark donor label is an escalation recorded in the A3 report and does not change `donor_audit.csv` inside the interval; the round 2 file is frozen and a round 3 audit file supersedes it explicitly if the decision goes that way.

---

## 9. Predictions for interval 2, consolidated

| # | stage | prediction |
|---|---|---|
| 1 | A2b | block calibration on the same $T$ under-covers the held-out donor by 0.10 to 0.20; unit calibration reproduces A1 |
| 2 | A2c | shortfall grows with the between-unit score share and shrinks with $K$; the location-shift simulation reproduces fold means within their dispersion; block folds sit below it |
| 3 | A2a | `scaled` has across-slide coverage sd under `random` below `abs` on every task; PRAD's under-covering fold is the one calibrated on patient 2's slides, and its between-unit score share is the smaller of the two folds |
| 4 | A2d | same-donor calibration covers a few points higher within PRAD, less than the 0.14 between-task figure |
| 5 | A2e | width orders with encoder Pearson under every design; coverage range stays under 0.02 |
| 6 | A2f | block folds fail on level; unit folds fail without a consistent sign |
| 7 | A3 | W1 collapses $n_{\text{eff}}$ on every different-slide fold; W1b does not; W2 has no support on PRAD and SKCM `patient`; W3 is infinite at $\alpha = 0.1$ outside CCRCC, finite and near nominal at $\alpha = 0.2$ where $K \ge 4$, and inert on block folds; nothing repairs the two-sample tasks |
| 8 | D3 | the eleven-sample breast source resolves to one laboratory; `TENX98`/`TENX99` are the vendor's replicate pair; the Washington University samples split into healthy and diseased donors with one scanner |
