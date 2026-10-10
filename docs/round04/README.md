# Round 4, data pull and the two method tracks (28 September to 3 October 2026)

The round followed the literature check that reframed the paper as "Labelling budgets for prediction-powered inference with clustered data". A data pull built the tasks first, and then an inference track and a prediction-set track ran side by side on those tasks.

**Tracks.** data (no branch, stages P0 to P8), ppi (`round4-ppi`, stages Q0 to Q5 and the closing unit Q5a), conformal (`round4-conformal`, stages C0 to C4). **Started from** `main` for the data track, and from tag `round4-data-v2` for the ppi and conformal tracks.

## Gates

| Date | Track | Gate | Report | Answered by | Tag | Pull request |
|---|---|---|---|---|---|---|
| 28 Sep | data | P1 stop | stop note under `results/round4/data/P1_selection`, not in this folder | `i01/data/round4_data_P1_decision.md` | none | none |
| 28 Sep | data | P7 | `i01/data/round4_data_report.md` | `i02/data/round4_data_P7_decisions.md` | `round4-data` | none |
| 30 Sep | data | P8 | `i02/data/round4_data_P8_report.md` | none, the data track had no closing memo | `round4-data-v2` | none |
| 1 Oct | ppi | Q1 | `i01/ppi/round4_ppi_Q1_report.md` | `i02/ppi/round4_ppi_Q1_decisions.md` | `round4-ppi-Q1` | #2 |
| 2 Oct | conformal | C2 | `i01/conformal/round4_conf_C2_report.md` | `i02/conformal/round4_conformal_C2_decisions.md` | `round4-conf-C2` | #3 |
| 2 Oct | ppi | Q3 | `i02/ppi/round4_ppi_Q3_report.md` | `i03/ppi/round4_ppi_Q3_decisions.md` | `round4-ppi-Q3` | #4 |
| 2 Oct | conformal | C4 | `i02/conformal/round4_conf_final_report.md` | `i03/conformal/round4_conformal_C4_decisions.md` | `round4-conf-final` | #5 |
| 2 Oct | ppi | Q5 | `i03/ppi/round4_ppi_final_report.md` | `i04/ppi/round4_ppi_Q5_decisions.md` | `round4-ppi-final` | #8 |
| 3 Oct | ppi | Q5a | `i03/ppi/round4_ppi_final_report.md`, section 10 | `i05/ppi/round4_ppi_Q5a_closing.md` | none | #8 |

Pull request #7 (`round4-conformal`, 2 October) only added ignore rules for large C3 tables and is not a gate.

## Documents

| Document | Date | Role |
|---|---|---|
| `masterplan.md` | 9 Oct (at migration) | the round's plan note, pointing to the documents that served as its plan |
| `00_prep/round3_directions.md` | 24 Sep | the first change of direction, written after round 3 and committed on 30 Sep |
| `00_prep/round4_originality_check.md` | 28 Sep | the second change of direction, with PPI read as the survey-sampling difference estimator and GHCP as occupying the labelled-test-group setting |
| `i01/conformal/round4_conformal_track.md` | 30 Sep | instruction for the conformal track |
| `i01/conformal/round4_conformal_addendum1.md` | 30 Sep | answers to the five flagged points, the GHCP pool rule and the ACS source |
| `i01/conformal/round4_conf_lower_bound.md` | 30 Sep to 1 Oct | scoping of the lower bound with no test-group observations, each step marked derived, conjectured or failed |
| `i01/conformal/round4_conf_candidate_definitions.md` | 1 Oct | the four candidate methods as written before they ran |
| `i01/conformal/round4_conf_C2_report.md` | 1 to 2 Oct | report at the C2 gate (testbed, GHCP reproduction, candidates, go or no-go) |
| `i01/data/round4_data_pull.md` | 28 Sep | instruction for the data pull, stages P0 to P7 |
| `i01/data/round4_data_P1_decision.md` | 28 Sep | decision on the P1 stop, to proceed as selected |
| `i01/data/round4_data_report.md` | 28 Sep | report at P7, with nineteen escalations |
| `i01/ppi/round4_ppi_track.md` | 30 Sep | instruction for the ppi track |
| `i01/ppi/round4_ppi_addendum1.md` | 30 Sep | answers to the eight flagged points, the textbook form for the design target and the ACS source |
| `i01/ppi/round4_ppi_Q1_report.md` | 1 Oct | report at the Q1 gate |
| `i02/conformal/round4_conformal_C2_decisions.md` | 2 Oct | decision at C2, no candidate goes forward and `within_plain` is added |
| `i02/conformal/round4_conf_final_report.md` | 2 Oct | end-of-track report on the real-data map, with a closing page that summarises the track |
| `i02/data/round4_data_P7_decisions.md` | 30 Sep | acceptance of P7, a decision on each escalation, and the P8 addendum |
| `i02/data/round4_data_P8_report.md` | 30 Sep | report on P8, which ends the data track at tag `round4-data-v2` |
| `i02/ppi/round4_ppi_Q1_decisions.md` | 1 Oct | decision at Q1 |
| `i02/ppi/round4_ppi_Q3_report.md` | 2 Oct | report at the Q3 gate (Q2, Q3, the Q1 supplement and the theorem check) |
| `i03/conformal/round4_conformal_C4_decisions.md` | 2 Oct | acceptance and close of the conformal track |
| `i03/ppi/round4_ppi_Q3_decisions.md` | 2 Oct | decision at Q3, with the corrected tuning rule and the tuning-cost result |
| `i03/ppi/round4_ppi_addendum2.md` | 2 Oct | where the conformal outputs are and how Q5 builds the joint design table |
| `i03/ppi/round4_ppi_final_report.md` | 2 to 3 Oct | end-of-track report for Q1 to Q5, with Q5a as section 10 and a closing page that summarises the track |
| `i04/ppi/round4_ppi_Q5_decisions.md` | 2 Oct | decision at Q5, acceptance subject to the closing unit Q5a |
| `i05/ppi/round4_ppi_Q5a_closing.md` | 3 Oct | acceptance of Q5a and close of the ppi track, a record that was not handed to the session |
| `oversight/round4_oversight_handoff.md` | 30 Sep | oversight handoff covering rounds 1 to 4, the path to the current directions, and what was running then to round 4 |
| `tracks/conformal/round4_conf_plan.md` | 30 Sep onward | living plan of the conformal track, which transcribes the addendum and both memos |
| `tracks/data/round4_data_plan.md` | 28 Sep onward | living plan of the data track, with the P1 decision and the P7 decisions and P8 |
| `tracks/ppi/round4_ppi_plan.md` | 30 Sep onward | living plan of the ppi track, which transcribes every addendum and memo |
| `tracks/ppi/round4_ppi_estimator_definition.md` | 1 to 3 Oct | the estimator defined once, finalised at Q3 and given the linearised design-target variance on 3 Oct |
| `tracks/ppi/round4_ppi_theory.md` | 1 Oct onward | the gain theorem, the allocation result and the two labelling regimes, derived |

Two reference documents written in this period live in `docs/reference/`. They are `docs/reference/methods_and_state_of_play.md` (27 Sep) and `docs/reference/concepts_explained_round4.md` (28 to 29 Sep).

## What the round established
- The data track ended with a lung task of 20 samples and 15 donors, after `NCBI865` was reinstated by dropping its one patch barcode without an expression row (`i02/data/round4_data_P8_report.md`).
- The gain theorem holds. With $\lambda$ cross-fitted from half the labelled donors, the theorem check reproduces the predicted tuning cost to within 0.0426 in all 24 cells, and the break-even rule is $n_L > 4 + 2/R^2_{\text{cluster}}$ (closing page of `i03/ppi/round4_ppi_final_report.md`).
- The donor-weighted gain on the Visium tasks is small, with design-target ratios of 0.93 to 1.09 at $n_L \ge 8$ for every encoder except `uni_v2` on CCRCC and CCRCC merged. On lung Xenium the gain is 0.41 to 0.55 at $n_L = 6$ to 12 (closing page of `i03/ppi/round4_ppi_final_report.md`).
- Under the cost ratio $c_d/c_s = 10$, labelling a few spots on every donor gives a narrower interval than labelling whole donors in 216 of 232 cells (closing page of `i03/ppi/round4_ppi_final_report.md`).
- Every spot-weighted PPI row is driven by a nuisance effect, since a permuted predictor reaches 0.285 to 0.397 of the classical variance on CCRCC $\theta_3$ (closing page of `i03/ppi/round4_ppi_final_report.md` and `i05/ppi/round4_ppi_Q5a_closing.md`).
- GHCP was reproduced at 254 of 254 simulation values and 53 of 53 ACS values, and no candidate method for the case with no labelled test spots met the fixed criterion (`i02/conformal/round4_conformal_C2_decisions.md` and `i03/conformal/round4_conformal_C4_decisions.md`).
- On HEST at $K = 10$, GHCP is 1.23 to 1.49 times HCP's width at $o \le 10$, and `within_plain` covers 0.90 to 0.92 from $o = 10$ on every task (`i03/conformal/round4_conformal_C4_decisions.md`).
- For $K + 1 < 1/\alpha$ every valid method has infinite expected width, and the released GHCP code uses a pool one group larger than the paper's equation (8) (closing page of `i02/conformal/round4_conf_final_report.md`).

## Corrections and withdrawn readings
- The round-3 statement that morphology removes 31% to 34% of the above-chance probe signal was quarantined, because the D4 probe used the full extent where half the extent was meant (`i02/data/round4_data_P7_decisions.md`, item 3).
- Addendum 1 had said the tuning rules were unchanged for the textbook form, which was an error. The Q3 memo tunes $\lambda$ on the labelled donors alone and drops the pre-test rule (d) (`i03/ppi/round4_ppi_Q3_decisions.md`, sections 1 and 2).
- The Q5 memo leaned toward the diagnostic column being wrong for the ACS states $\theta_2$ rows. The Q5a closing memo shows the interval was wrong, because the variance left out the term $(\lambda_g - c_U)\bar F$ (`i05/ppi/round4_ppi_Q5a_closing.md`, section 2).
- The Q5 memo's allocation sentence was wrong and the report was right, so the theory document's statement with the `uni_v2` exception stands (`i04/ppi/round4_ppi_Q5_decisions.md`, section 4, item 7).
- The conformal final report's closing page says fewer than about 25 labelled spots buy nothing for the prediction set. The C4 memo, which adds `within_plain`, puts the figure at about ten (`i02/conformal/round4_conf_final_report.md` and `i03/conformal/round4_conformal_C4_decisions.md`, section 2).
- The closing page's Visium and lung ranges are for $\theta_3$, and $\theta_2$ shows smaller gains on the same tasks (`i05/ppi/round4_ppi_Q5a_closing.md`, section 3).
- A candidate rule in the lower-bound scoping was invalid as first stated, and the repaired rule does not dominate HCP (`i01/conformal/round4_conf_lower_bound.md`, and `docs/round05/00_prep/round5_oversight_handoff.md` section 13).
- The regime B correction in section 4 of `docs/reference/concepts_explained_round4.md` changed the PPI track's Q3.

## Carried forward
- Round 5 starts from `results/round4/ppi/Q5_joint/q5_cluster_table.csv` for active cluster selection, and from Q5 and C3 for the paper's joint design section (`i05/ppi/round4_ppi_Q5a_closing.md`, section 5).
- A regression-form spot-weighted estimand, under which donor-level weight sums cancel, is a round-5 candidate (`i05/ppi/round4_ppi_Q5a_closing.md`, section 5).
- One of the six candidates the handoff lists for round 5 is checking whether the final design-target rule and variance hold in simulation, since they were validated only on masking draws. The first it lists is active cluster selection (`docs/round05/00_prep/round5_oversight_handoff.md`, section 13).
- Whether HCP can be beaten when $K + 1 \ge 1/\alpha$ stays open (`i03/conformal/round4_conformal_C4_decisions.md`, section 5, and `i01/conformal/round4_conf_lower_bound.md`).
- Whether the GHCP authors are told about the pool rule and the tie convention is for Nicolas with David and Dr. Zhu (`i03/conformal/round4_conformal_C4_decisions.md`, section 5).
- The D4 probe rerun and the ten unresolved claims in two documents that predate round 3 are round-5 housekeeping (`i02/data/round4_data_P7_decisions.md`, items 3 and 19).

## Read first next round
- `docs/round04/i03/ppi/round4_ppi_final_report.md`, the closing page and section 10 for the state of the inference track.
- `docs/round04/i02/conformal/round4_conf_final_report.md`, the closing page for the prediction-set map.
- `docs/round04/i05/ppi/round4_ppi_Q5a_closing.md`, the closing decisions and what leaves the track.
- `docs/round04/i03/conformal/round4_conformal_C4_decisions.md`, the readings for the paper and the open decisions.
- `docs/round04/tracks/ppi/round4_ppi_estimator_definition.md`, the final estimator with the linearised variance.
