# Round 3, the first experiments for both topics (22 to 24 September 2026)

Round 3 ran the first experiments for Topic A (conformal prediction for a new slide, session or donor) and Topic B (inference on predicted expression with donor-clustered variance), and the first expansion of the data beyond the benchmark's 72 samples. It ran as one track, `exec`, in stages S0, A0 to A4, B1, B2 and D0 to D4, started from tag `round2-docs-clean` (commit `4da6b86`). Its gates are tagged `round3-A1`, `round3-A3` with revision `round3-A3-r2`, and `round3-final` with revision `round3-final-r2`. No masterplan was written. The plan of record is `tracks/exec/round3_execution_plan.md`, which transcribes the execution instruction (sections 3 to 11) and the two gate memos (sections 12 and 13). `docs/round10/00_prep/round10_findings_survey.md` lists what the round established by question in its rows D6, D7, D9, A1 to A5, B1 and B3.

## What the round established, as it now stands

**The donor carries the variance.** On CCRCC $\theta_3$ the median ratio of the donor-clustered to the spot i.i.d. standard error is 29.0 to 35.8 spot-weighted and 44.9 to 67.6 donor-weighted at 6 to 12 labelled donors, on the `resnet50` arm (`results/round3/B1_ppi/b1b2_report_numbers.csv`). Over 200 labelled-donor draws per setting, pooled over the classical cells, a spot i.i.d. interval covers 0.044 at nominal 0.90, a donor cluster-robust interval with a $t_{G-1}$ reference 0.913, and a percentile donor bootstrap 0.711 (`results/round3/final_report/final_report_numbers.csv`). The coverage is design-based, of the full-data value of this donor set over repeated labelling, and with one labelled donor (PRAD) nothing covers (`i03/exec/round3_final_report.md`, section 6.4). Round 10 reran the standard-error ratio on the log scale with `uni_v2`: 32.58 on CCRCC and 14.81 to 58.98 on the other tasks it ran (`results/round10/final_runs/F4/paper_numbers.csv`, keys `D9.*`). The variance machinery is classical (Cameron and Miller 2015; MacKinnon, Nielsen and Webb 2023).

**Coverage under shift is set by the calibration design, not the encoder.** With the absolute score at nominal 0.90, coverage is 0.894 under `random`, 0.859 under `slide_out`, 0.802 under `donor` and 0.786 under `patient`, in that order for all twelve encoders (`results/round3/A1_coverage/a1_coverage_by_design.csv`, `i01/exec/round3_A1_stage_report.md`, section 6.1). Round 11 showed that the `donor` shortfall of this mean comes mostly from tasks with two to four donors, and is 0.006 to 0.029 on tasks with 15 to 51 (`docs/round11/README.md`, H1(b)); the 132 cells count IDC twice, and with IDC once `donor` is 0.800. These are means over cells of per-slide coverage; pooled over spots, `random` covers 0.8986 to 0.9018 on the 30 harness-check cells (`results/round3/A1_coverage/a1_aggregation_note.csv`, A1 report section 3). By calibration unit, donor-level calibration covers 0.851, slide-level 0.849 and block-level 0.686 (`results/round3/A1_coverage/a1_coverage_by_calibration_unit.csv`). The A1 report reads COAD's rise from 0.721 under `patient` to 0.866 under `donor` as the effect of correcting the grouping variable; the review at the A1 gate showed that both the labels and the fold structure changed (plan section 12.2 item 1).

**The calibration unit, not the calibration size, decides coverage.** On one shared proper-training set, held-out-donor calibration covers 0.8562 and spatial-block calibration 0.7442, block lower in 138 of 138 cells (`results/round3/A3_report_numbers.csv`), and block intervals fail by being too narrow rather than misplaced (`results/round3/A2_conditional/a2_level_scale.csv`, A3 report section 6.3). The account at the A1 gate, that the unit-calibrated shortfall is a small-$K$ effect, was refuted: coverage tracks neither $K$ (Spearman −0.0265) nor the between-unit share (−0.0825) (`i02/exec/round3_A3_stage_report.md`, section 5 row 2). Small $K$ explains the fold-to-fold scatter, not the mean shortfall of three to four points, which nothing measured in the round explains (`i03/exec/round3_A3_decisions.md`, section 3.1).

**Feature-based weighted conformal cannot repair donor or slide shift here.** Calibration and test slides are separable at held-out AUC 0.9747 or more, and the weights leave a median 2.13% of the calibration set effective; on morphology covariates alone, 9.34% (`results/round3/A3_report_numbers.csv`). The method is in print (Tibshirani, Barber, Candès and Ramdas 2019); the result is negative on these data.

**Hierarchical conformal prediction (HCP) is valid once $K + 1 \ge 1/\alpha$ and conservative.** It is infinite in exactly the cells where $K + 1 < 1/\alpha$, 1,932 of 1,932 (`results/round3/A3_report_numbers.csv`). With $K = 10$ calibration donors on CCRCC it covers 0.9692 at 1.947 times the pooled quantile's width, the one-per-donor subsample 0.9109, and the pooled quantile 0.8644, against 0.8642 at $K = 6$, so the pooled shortfall is not a $K$ effect (`results/round3/A4_scores/a4b_summary.csv`, final report section 6.3). On Indiana HCP covers 0.9882 at 1.907 times the width (`results/round3/D4_expansion/d4_pooled_numbers.csv`). Both methods are in print (Lee, Barber and Willett, arXiv:2306.06342; Dunn, Wasserman and Ramdas, JASA 2023). Round 10 reran HCP at $K = 10$ on CCRCC at 0.9694, and round 4 measured the width ratio at $K = 20$ as 1.3604 (`results/round10/final_runs/F4/paper_numbers.csv`, keys `F3.A4.CCRCC` and `A4.ratio20`).

**Adaptive scores buy little width at matched coverage except in the upper tail.** At the level whose realised coverage is 0.90, a diagnostic since the level is chosen with test labels, CQR is 2.6461 wide against 2.6930 for the absolute score; in the top predicted-value decile the absolute score covers 0.7224, CQR 0.8747 and conformalised negative binomial 0.8668 (`results/round3/A4_scores/a4_report_numbers.csv`). These hold only at A4a's reduced scope, CQR on 6 of 50 genes and the negative binomial head on 16, on the first calibration draw (final report section 7 item 10). The `scaled` score's width explodes under shift (14.83 at matched coverage, same file), and clipping its scale barely changes the mean width (ratio 0.9887, final report section 6.2).

**Prediction-powered inference under donor clustering is valid with a modest gain in the donor-weighted population.** On CCRCC $\theta_3$ the PPI-to-classical cluster width ratio is 0.845 (`uni_v2`), 0.874 (`hoptimus0`), 0.891 (`resnet50`) and 0.984 for a permuted predictor (`results/round3/final_report/final_report_numbers.csv`). The spot-weighted ratios, 0.717 to 0.760 including the permuted predictor (same file), are not a gain: for covariance-type spot-weighted estimands a permutation cannot make a useless predictor (final report section 7 item 4), and round 4 marked every spot-weighted PPI row as nuisance-driven (`docs/round04/i03/ppi/round4_ppi_final_report.md`, section 10.2). Later rounds changed the donor-weighted reading too: B1 tuned $\lambda$ on the spot-level variance of the labelled data, which round 4 replaced with a cross-fitted coefficient (survey row B5), and in regime B a comparator without a cluster-specific intercept credits the predictor with a level term (survey rows B6 and B7).

**The data.** IDC's four benchmark samples are four donors; `TENX98` and `TENX99` are the vendor's replicate pair and round 2 misassigned `TENX95` (`results/round3/D3_audit/donor_audit_r3.csv`, A3 memo section 2.1). The round 2 reading that IDC's replicate leak came from a shared donor is withdrawn, and READ's $+0.0901$ is the only same-specimen replicate figure. CCRCC's 24 donor labels are unverifiable at donor level, and `INT4` and `INT24` may be one donor, so B1, B2 and A4b ran both ways without changing the reading (final report sections 6.1 and 6.3). HEST-1k has no organ-by-technology cell with three laboratories at three or more donors (46 cells checked) and no two-laboratory cell with disease held fixed (`i01/exec/round3_d0_expansion_proposal.md`, section 4; root `README.md`, known limitation 14). The D0 proposal's attribution of 23 kidney samples to Washington University was overturned by D3, which found them generated at Indiana (A3 report section 5 row 8). The D0 proposal's section 7 records HEST-1k's label quality: 292 of 1,276 samples carry a usable patient label, 114 carry a whitespace-only label, label strings are reused across cohorts, and 15 groups of ids share their expression data. Moving CCRCC from the benchmark's patches to HEST-1k's moves coverage by at most 0.0019 and Pearson by at most 0.0064 (`results/round3/D4_expansion/d4_pooled_numbers.csv`).

**The expansion arms.** On Indiana kidney, 25 donor units with laboratory, instrument and preservation fixed, `random` covers 0.8883 and `donor` 0.8778, with about a third of CCRCC's fold scatter. The kidney population-and-source shift is asymmetric: trained on ccRCC and tested on non-tumour kidney it covers 0.9053, the reverse 0.7032, and the population is decodable at balanced accuracy 0.99997. On breast Xenium from one laboratory, prototype-instrument slides cover 0.8104 against 0.8948 for production instruments (all `results/round3/D4_expansion/d4_pooled_numbers.csv`). The statement that morphology removes 31% to 34% of the probe signal does not stand: the probe used the full patch extent where half was meant, round 4 quarantined it, and it was not rerun (`docs/round04/i02/data/round4_data_P7_decisions.md`, item 3).

## Expectations and their scores

The predictions were written before the runs in the plan's sections 4.3 to 4.10 (H1 to H25, from the execution instruction), in section 12.4 (M1.1 to M1.8, from the A1 memo's section 9) and in the A3 memo's section 10 (rows 1 to 11). The scores are the track's, in `i03/exec/round3_final_report.md` section 5, where each is quoted in full; the wording below is shortened.

| # | prediction (shortened) | score |
|---|---|---|
| H1 | `random` at nominal | held |
| H2 | `patient` and `donor` under-cover, worst on PRAD and SKCM | partly held (PRAD among the best) |
| H3 | near nominal under `donor` only with donor calibration | held |
| H4 | `slide_out` between `random` and `donor`; donor-sharing calibration better | held |
| H5 | weaker encoders under-cover more; same ordering by design | partly held |
| H6 | IDC audited labels under-cover more | refuted; the audited label set is superseded |
| H7 | `donor` shortfall mostly level | refuted |
| H8 | gene shortfall tracks the split penalty | refuted |
| H9 | worse in the predicted-value tails | partly held (upper tail only) |
| H10 | session-unsupported folds worst | not tested as stated |
| H11 | reweighting restores coverage where $n_{\text{eff}}$ stays high | refuted |
| H12 | gain monotone in $n_{\text{eff}}$ | not tested |
| H13 | W1 beats W2 within cells | not tested |
| H14 | `scaled` narrower at matched coverage | refuted |
| H15 | NB under-covers like conformal; conformalising restores it | held |
| H16 | CQR and `scaled` narrower than `abs` | partly held; `scaled` clause refuted |
| H17 | conditional dispersion well below marginal, above zero | partly held |
| H18 | spot i.i.d. intervals cover far below 0.90 | held |
| H19 | cluster-robust near 0.90 for $n_L \ge 8$, needs $t$ below | held, with over-coverage at $n_L = 12$ |
| H20 | donor bootstrap similar | refuted |
| H21 | PPI width ratio below 1 only for better encoders; permuted at or above 1 | partly held |
| H22 | lab term at least the patient term | not tested (no laboratory term exists) |
| H23 | lab term not explained by composition | track: held for a population term; now not tested, since the probe figure is quarantined |
| H24 | lab decodable from embeddings | held, for population rather than laboratory |
| H25 | some lab or donor labels wrong | held |
| M1.1 | block calibration under-covers by 0.10 to 0.20 | partly held |
| M1.2 | shortfall grows with between-unit share, shrinks with $K$ | partly held (first clause wrong in sign) |
| M1.3 | `scaled` lower across-slide sd on every task; PRAD fold | partly held |
| M1.4 | same-donor calibration a few points higher in PRAD | not settled |
| M1.5 | width orders with Pearson; coverage range under 0.02 | partly held |
| M1.6 | block folds fail on level | refuted |
| M1.7 | W1 collapses; W1b does not; W2 no support; W3 as stated | partly held |
| M1.8 | breast source one lab; replicate pair; WashU split | partly held |
| 1 | `scaled_clip` halves `scaled`'s mean width | refuted; median clause held |
| 2 | top-decile shortfall closes under CQR and conformalised NB | held pooled, two per-design exceptions |
| 3 | NB under-covers; conformalising restores; dispersion above zero | held, except dispersion zero in 10.58% of fits |
| 4 | recentred oracle 20 to 40% narrower | refuted in magnitude, right in direction |
| 5 | HCP finite, 0.92 to 0.95, width ratio 1.2 to 1.6 | partly held; width clause refuted |
| 6 | spot SEs smaller by five or more; $\lambda$ 0.3 to 0.9 | partly held |
| 7 | spot i.i.d. under 0.6; cluster 0.85 to 0.92; PPI ratio clauses | partly held |
| 8 | layout anchor moves Pearson under 0.01 | held |
| 9 | Indiana `donor` 0.85 to 0.88; HCP finite and at or above 0.90 | held |
| 10 | `population_out` at or under 0.70; composition explains a majority | track: partly held, composition clause refuted; the composition clause now rests on the quarantined probe |
| 11 | breast `donor` 0.82 to 0.87; prototype slides lower | half held |

## What was tried and did not work

- Feature-based weighting (W1 on embeddings, W1b on morphology, W2 on session and resolution): calibration and test slides are separable, so the weights either collapse or have no support (A3 report section 6.8).
- The `scaled` score under shift, and clipping its scale at the 1st and 99th percentiles, which binds on almost every fold and changes almost nothing (final report section 6.2).
- The percentile donor bootstrap with few donors (0.711 pooled; final report section 6.4).
- A laboratory term: HEST-1k has no cell that supports one, so no `lab_out` arm was run (A3 memo section 2.4).
- Tuning $\lambda$ on donor-clustered residuals, which drives the variance to zero at two labelled donors (final report section 7 item 5).
- A permuted predictor as the useless-predictor control for spot-weighted covariance estimands, which cannot work (final report section 7 item 4).

## Presented outside the project

The first advisor deck, presented on 21 September, called the IDC pair probably one donor (A3 memo section 2.1). The second deck's slide 4 carries the correction, and its slides 5 and 6 present round 3's coverage by design, the AUC and effective-size result, the absence of an institution axis, the 0.04 and 0.91 coverages and HCP at $K = 10$ (`deck2_outline.md` (at tag `record-full-2026-11`; summarised in `docs/round05/README.md`)). Those figures stand. The A1 memo asked that the advisors be told the expansion selection and the limitation of the archive; the record does not show whether that was done apart from the second deck. The round 2 benchmark issue draft for the HEST authors stays unsent, with its IDC item struck.

## Open threads

- Root `README.md` known limitation 8 still shows H-Optimus-1's `raw_ridge` cell as a dash (final report section 7 item 3).
- `results/round2/R5c_leak/r5c_leak_summary.csv` still records IDC's `leak_realised_in_shipped_split` as True; results files are not edited, and this summary gives the reading that stands.
- Checks left undone (final report section 8): whether HCP's over-coverage is level, scale or asymmetry; any studentised or bias-corrected bootstrap; a cross-fitted $\lambda$; whether `INT4` and `INT24` are one donor; the D4 probe with the corrected extent.

## Documents kept

- `tracks/exec/round3_execution_plan.md`, the plan of record, with every stage's design and the predictions as written before the runs; cited by the round's scripts and provenance files.
- `i01/exec/round3_A1_stage_report.md`, the A1 gate report: the harness checks and the coverage table across designs.
- `i01/exec/round3_d0_expansion_proposal.md`, the HEST-1k inventory, the institution criterion and the archive's label quality.
- `i02/exec/round3_A3_stage_report.md`, the A3 gate report: A2's anatomy of the failure, A3's weighting, D1 to D3.
- `i03/exec/round3_A3_decisions.md`, the A3 gate memo: the five decisions, the interval 3 designs and predictions, cited by the interval 3 scripts.
- `i03/exec/round3_final_report.md`, the end-of-round report, with every prediction scored and the escalations.
