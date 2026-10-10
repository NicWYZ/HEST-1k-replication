# Round 5, two tracks on intervals and prediction sets (7 to 9 October 2026)

Round 5 went ahead on the plan from the round-4 closing memos, because the second advisor meeting stopped at slide 8 and the advisors had not yet seen round 4's results. The inference track validated the final interval in simulation, completed regime B, put the estimators in regression form and chose which clusters to label. The prediction-set track completed the simulation map, ran GHCP in its own settings, extended the real-data map above 10 calibration donors and took up two theory questions.

**Tracks.** ppi (branch `round5-ppi`, stages E0 to E5 and E4b), conformal (branch `round5-conformal`, stages W0 to W5). **Started from** `main` at `d82c3f3`, the merge of pull request #14, which carried the two instructions.

## Gates

| Date | Track | Gate | Report | Answered by | Tag | Pull request |
|---|---|---|---|---|---|---|
| 8 Oct | ppi | E2 | `i01/ppi/round5_ppi_E2_report.md` | `i02/ppi/round5_ppi_E2_decisions.md` | `round5-ppi-E2` | #15 |
| 8 Oct | conformal | W2 | `i01/conformal/round5_conf_W2_report.md` | `i02/conformal/round5_conformal_W2_decisions.md` | `round5-conf-W2` | #16 |
| 9 Oct | ppi | E4 | `i02/ppi/round5_ppi_E4_report.md` | `i03/ppi/round5_ppi_E4_decisions.md` | `round5-ppi-E4` | #17 |
| 9 Oct | conformal | W5 | `i02/conformal/round5_conf_final_report.md` | `i03/conformal/round5_conformal_W5_decisions.md` | `round5-conf-final` | #18 (the memo's transcription in #19, no tag) |
| 9 Oct | ppi | E5 | `i03/ppi/round5_ppi_final_report.md` | `i04/ppi/round5_ppi_E5_decisions.md` | `round5-ppi-final` | #20 (the memo's transcription is in the same pull request, no further tag) |

## Documents

| Document | Date | Role |
|---|---|---|
| `masterplan.md` | 9 Oct (at migration) | the round's plan note, pointing to the documents that served as its plan |
| `00_prep/deck2/deck2_literature_check.md` | 4 Oct | originality, relevance and importance of round 4's results, with what was confirmed and what the searches only reported |
| `00_prep/deck2/deck2_new_results_explained.md` | 4 Oct | for Nicolas, the six round-4 results explained with their theory, and what is not established |
| `00_prep/deck2/deck2_outline.md` | 4 Oct | the outline of the second advisor presentation, revision 3, 16 slides |
| `00_prep/round5_oversight_handoff.md` | 4 Oct, revised that evening | the oversight handoff at the close of round 4; its section 8.3 lists what the slide build needs |
| `i01/conformal/round5_conformal_track.md` | 7 Oct | instruction for the prediction-set track |
| `i01/conformal/round5_conf_W2_report.md` | 8 Oct | report at the W2 gate (W1 and W2) |
| `i01/ppi/round5_ppi_track.md` | 7 Oct | instruction for the inference track; its section 2.4 states the reading that E2 tested |
| `i01/ppi/round5_ppi_E2_report.md` | 8 Oct | report at the E2 gate (E0 to E2) |
| `i02/conformal/round5_conformal_W2_decisions.md` | 8 Oct | decision at W2; its section 4 sets the code-delivery rules both tracks follow |
| `i02/conformal/round5_conf_final_report.md` | 9 Oct | end-of-track report (W3 to W5); its closing page is the track's summary |
| `i02/ppi/round5_ppi_E2_decisions.md` | 8 Oct | decision at E2; it leads to E3, the stratified draw and E3a |
| `i02/ppi/round5_ppi_E4_report.md` | 9 Oct | report at the E4 gate (E3a, E3 and E4) |
| `i03/conformal/round5_conformal_W5_decisions.md` | 9 Oct | acceptance and close of the prediction-set track, with four corrections for the record |
| `i03/ppi/round5_ppi_E4_decisions.md` | 9 Oct | decision at E4; form C becomes the within-cluster estimator and stage E4b is added before E5 |
| `i03/ppi/round5_ppi_final_report.md` | 9 Oct | end-of-track report (E4b and E5, with E1 to E4 in brief); its closing page is the track's summary |
| `i04/ppi/round5_ppi_E5_decisions.md` | 9 Oct | acceptance and close of the inference track, with the question for the next round |
| `tracks/conformal/round5_conf_plan.md` | 7 Oct onward | operating plan; section 6 transcribes the W2 memo and section 7 the W5 memo |
| `tracks/conformal/round5_conf_theory.md` | 7 Oct onward | the two W4 theory questions, part A on the small-$K$ propositions and part B on whether HCP can be beaten |
| `tracks/ppi/round5_ppi_estimator_definition.md` | 9 Oct | the paper's estimator, defined once; the E5 memo settles its allocation sentence |
| `tracks/ppi/round5_ppi_plan.md` | 7 Oct onward | operating plan; sections 7, 8 and 9 transcribe the E2, E4 and E5 memos |
| `tracks/ppi/round5_ppi_theory.md` | 7 Oct onward | the level term, the cross-fitting term and two-level estimator, and the interval for balanced selection |

## What the round established

- The design-target interval `textbook_t|fpc|lin|xf` covers 0.888 to 0.903 where the uncorrected interval covered 0.840 to 0.886 (`i03/ppi/round5_ppi_final_report.md`, closing page).
- Form C, which gives each cluster its own intercept, is the paper's within-cluster estimator, and a predictor constant within a cluster leaves it unchanged (`i03/ppi/round5_ppi_E4_decisions.md`, `tracks/ppi/round5_ppi_estimator_definition.md`).
- In regime B the predictors narrow the slope's interval to 0.706 to 0.847 of the classical width on lung and 0.594 to 0.625 on census, and not on the kidney tasks, at 0.982 to 1.009 (`i04/ppi/round5_ppi_E5_decisions.md`, section 3).
- Balanced selection of the labelled clusters, `rej_t`, enters the paper as a design result with conditions and not as the default (`i04/ppi/round5_ppi_E5_decisions.md`, section 3 item 3).
- The allocation uses the formula with the measured between ratio, and the fitted value is given beside it (`i04/ppi/round5_ppi_E5_decisions.md`, section 2).
- On real data at 10 calibration donors and 90%, HCP is the narrowest valid method up to 5 labelled spots, and from 9 labelled spots the full conformal set inside the target donor is 0.416 to 0.677 of HCP's width (`i03/conformal/round5_conformal_W5_decisions.md`, section 3 item 1).
- GHCP becomes narrower than HCP on kidney cancer once there are enough calibration donors, and in GHCP's own designs the full conformal set is 2 to 4 times narrower from 9 labelled units (`i03/conformal/round5_conformal_W5_decisions.md`, section 3 items 3 and 4).
- Two parts of the small-$K$ proposition are direct corollaries of published results, and HCP is not pointwise dominated in the revealed-law model (`tracks/conformal/round5_conf_theory.md`, B.5).

## Corrections and withdrawn readings

- The reading that regime B's classical comparator had no intercept, so a constant predictor appeared to help, was tested at E2, and the constant predictor became the primary control (`i02/ppi/round5_ppi_E2_decisions.md`, `i01/ppi/round5_ppi_track.md` section 2.4).
- The oversight chat's E2 memo misread three provenance records naming `8b879bb`, and its band for the permuted-balance check assumed independent genes. Both are corrected in `i03/ppi/round5_ppi_E4_decisions.md`.
- The W2 memo's "3 to 4 times narrower" than GHCP reads 2 to 4 times (`i03/conformal/round5_conformal_W5_decisions.md`, section 2 item 4). The final report's matched row count of 1,693,662, also declared in `.verify-exceptions-round5-conformal`, reads 1,694,142 (same file, section 2 item 1). The report and the exceptions file were left as committed.
- The W5 memo also corrects the count of Slurm jobs in the provenance index and the closing page's statement that the simulation's map holds on every task at $K = 10$. On Indiana the plain split is narrower by at most 2% at $o$ from 9 to 15 (same file, section 2, items 2 and 3).
- The E5 memo corrects the report's reading of `pcF2` on census, which repeats the `own` rows with $k = 1$ and not 2 (`i04/ppi/round5_ppi_E5_decisions.md`, section 4 item 12).
- Each closing report lists the round-4 statements it changes (`i03/ppi/round5_ppi_final_report.md` section 9, `i02/conformal/round5_conf_final_report.md` section 11).

## Carried forward

- The first question for the next round is weighting the labelled clusters by their inclusion probabilities under rejective selection (`i04/ppi/round5_ppi_E5_decisions.md`, section 5).
- Why the null control fails in two census designs at $n_L = 4$ is not established (`i04/ppi/round5_ppi_E5_decisions.md`, section 2).
- The conditions for `rej_t` were read from the same runs and are not a validated rule (`i04/ppi/round5_ppi_E5_decisions.md`, section 3 item 3).
- The superpopulation-target interval covers below 0.85 in 916 of 8,820 simulation cells, so real-data claims use the design target (`i04/ppi/round5_ppi_E5_decisions.md`, section 3 item 5).
- Dominance of HCP in expected width is open, and the paper says so (`i03/conformal/round5_conformal_W5_decisions.md`, section 4).
- Two round-4 rows were not reproduced, and they were not rerun (`i03/conformal/round5_conformal_W5_decisions.md`, section 4).
- In the next round's briefs the frame id goes in the first message to each sub-agent (`i04/ppi/round5_ppi_E5_decisions.md`, section 4 item 5).

## Read first next round

- `docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, section 3 for the inference readings and section 5 for the first methods question.
- `docs/round05/i03/conformal/round5_conformal_W5_decisions.md`, section 3 for the prediction-set readings.
- `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`, the paper's estimator.
- `docs/progress-log.md`, the round's oversight steps and the move from handoffs to `CLAUDE.md`.
