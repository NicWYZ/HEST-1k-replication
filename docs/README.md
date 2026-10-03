# `docs/`, a reading guide

Rewritten 30 September 2026 by the oversight chat, replacing the flat index that is kept at `superseded/README_index_2026-09-30.md`. This file is the map of the project's documents, ordered the way the project happened, so that someone new can follow what was planned, what was found, and what was decided because of it.

The files themselves are not moved. Every instruction document, plan and report cites other documents by their path under `docs/`, the two round-4 tracks are running against those paths on their branches, and frozen records are not edited. Moving files now would break hundreds of references in documents that cannot be corrected. A physical reorganisation into round folders is a between-rounds job, after round 4's branches are merged, with a script that rewrites the references and a numeric-claim sweep afterwards. Until then, this guide is the organisation.

---

## Start here

To get up to speed in about an hour, read these in order.

1. `../README.md`, the repository's entry point (status, key findings, the benchmark's properties, known limitations).
2. `decisions/round4_oversight_handoff.md`, the latest oversight handoff (30 September). It carries the whole path from the literature review to the current directions, with reasons, the key numbers with their files, what is running, and the open decisions.
3. `decisions/round3_oversight_handoff.md`, the previous handoff (22 September), for rounds 1 and 2 in detail. Its sections 0, 2, 6 and 10 still hold.
4. `round3_final_report.md`, its closing page "What round 3 established".
5. `decisions/round3_directions.md` and `decisions/round4_originality_check.md`, the two documents where the project changed direction.
6. `WAYS_OF_WORKING.md`, the procedures, each tied to the failure it prevents.

For the methods themselves, derived from scratch, read `reference/methods_and_state_of_play.md` and `reference/concepts_explained_round4.md`.

## How the documents relate

Each stage of work produces the same chain. The oversight chat writes an **instruction** (a handoff or a track document) or a **decision memo** at a gate. The execution session transcribes it into an **operating plan** before running anything, flags what looks wrong rather than changing it, then writes a **stage report** at the gate. The next decision memo answers that report. Instructions and decision memos live in `decisions/`; plans and reports live in `docs/` itself. Reports are written once and not edited; corrections go in the next report. Tags mark the state of the repository at each gate.

---

## Before round 1 (early September)

| document | date | what it is |
|---|---|---|
| `first_year_ST_project_proposal.md` | September | The framing. Three constraints on the first year; Topic A (calibrated uncertainty on predicted expression) and Topic B (inference on predicted expression); the plan to reach them through a HEST-1k replication. Superseded as a statement of scope by the round-3 and round-4 reframings below. |
| `literature_landscape.md` | undated, mid-2026 citations | The landscape and ranked shortlist that produced Topics A and B. Slide 7 of the round-2 deck. |

## Round 1, faithful replication and instrumentation (12 to 16 September)

| document | date | role |
|---|---|---|
| `HEST_replication_handoff.md` | 12 Sep | instruction, the original stage plan and ground rules |
| `round1_final_stage_report.md` | 16 Sep | report, frozen. Contains claims round 2 withdrew (the "institution shift" scalar, the COAD same-patient reading); do not cite those |
| `HEST_replication_review.md` | 16 Sep | the oversight audit of round 1 that produced round 2 |

## Round 2, from replication to project motivation (16 to 21 September)

| document | date | role |
|---|---|---|
| `round2_execution_plan.md` | 16 Sep | instruction and plan, stages R0 to R8; its section 13 is the report format every later report follows |
| `round2_R0_R1_stage_report.md` | 17 Sep | report, R0 and R1 (the intercept, the $R^2$ ladder); carries the relabelling note on round 1 |
| `decisions/round2_R1_decisions.md` | 17 Sep | decision at R1 |
| `round2_R3_stage_report.md` | 18 Sep | report, R0 to R3 (split decomposition) |
| `decisions/round2_R3_decisions.md` | 18 Sep | decision at R3 |
| `r5_idc_provenance.md` | 18 Sep | reading task on the IDC samples. Its `TENX95` mapping is contradicted by round 3's D3 |
| `round2_R5_stage_report.md` | 18 Sep | report, R4 and R5 (probes, provenance) |
| `decisions/round2_R5_decisions.md` | 19 Sep | decision at R5 |
| `round2_R8_stage_report.md` | 19 Sep | report, R5b to R8 (donor audit, replicate leak, variance components, per-gene, raw heads) |
| `decisions/round2_closeout_decisions.md` | 19 Sep | closeout instruction |
| `round2_closeout_report.md` | 19 Sep | closeout report; freeze at `round2-final` |
| `round2_results_synthesis.md` | 19 Sep | every result of rounds 1 and 2 ranked by significance; the basis of the deck |
| `decisions/deck_figures_and_repo_update.md` | 20 Sep | instruction for the deck figures and repository refresh |
| `deck_master_outline.md`, `deck_speaker_scripts.md` | 20 to 22 Sep | the deck's outline and full scripts |
| `closeout_gate_report.md` | 21 Sep | the numeric-claim gate's first correction |
| `decisions/post_deck_repo_instructions.md` | 21 Sep | instruction closing the claim gate |
| `docs_clean_report.md` | 21 Sep | how the claim gate was closed at zero; tag `round2-docs-clean` |
| `deck_round2/` | presented 21 Sep | the deck. `HEST-1k Replication Update.pptx` is the authoritative copy, kept current by Nicolas; `deck_round2_slides.md`, `deck.json` and `slides/` are a text export as of 22 September and may lag his edits. Presented through slide 6 of 14 |
| `hest_bench_issue_draft.md` | undated | draft issue to the HEST authors. **Unsent**, and its IDC item is contradicted; do not send as drafted |

## Round 3, the first experiments for both topics (22 to 24 September)

| document | date | role |
|---|---|---|
| `decisions/round3_oversight_handoff.md` | 22 Sep | context for the oversight chat, rounds 1 and 2 in detail |
| `decisions/round3_execution_handoff.md` | 22 Sep | instruction, stages S0 to D4 |
| `round3_execution_plan.md` | 22 Sep | plan, the transcription |
| `superseded/round3_park_note.md` | 22 Sep | mid-interval park note, superseded by the A1 report |
| `round3_d0_expansion_proposal.md` | 22 Sep | D0, the expansion proposal; the institution criterion is not satisfiable in HEST-1k |
| `round3_A1_stage_report.md` | 22 Sep | report at the A1 gate (coverage across four fold designs); tag `round3-A1` |
| `decisions/round3_A1_decisions.md` | 22 Sep | decision at A1 (interval 2; the expansion approved; HCP added as W3) |
| `round3_A3_stage_report.md` | 23 Sep | report at the A3 gate (A2 anatomy of failure, A3 reweighting and HCP, D1 to D3); tags `round3-A3`, `round3-A3-r2` |
| `decisions/round3_A3_decisions.md` | 23 Sep | decision at A3 (IDC is four donors; A4b with $K = 10$; B1 and B2; D4 re-scoped) |
| `round3_final_report.md` | 24 Sep | end-of-round report (A4, B1, B2, D4); tags `round3-final`, `round3-final-r2`. Its closing page is the best one-page summary of round 3 |
| `decisions/round3_directions.md` | 24 Sep | **the first change of direction.** What round 3 established, the three facts that constrain any direction, the four candidates D1 to D4, and why Topics A and B as framed were retired |

## Between rounds 3 and 4 (25 to 28 September)

| document | date | role |
|---|---|---|
| `reference/methods_and_state_of_play.md` | 27 Sep | every method derived from scratch, every round-3 result with how and why, what has not been tried, and what the rest of HEST-1k holds |
| `decisions/round4_originality_check.md` | 28 Sep | **the second change of direction.** PPI is the survey-sampling difference estimator (Mozer 2026); GHCP (Mallick et al., August 2026) occupies the labelled-test-group conformal setting; the paper reframed as "Labelling budgets for prediction-powered inference with clustered data" |
| `reference/concepts_explained_round4.md` | 28 to 29 Sep | the nineteen concepts Nicolas asked about, with the regime B correction (section 4) that changed the PPI track's Q3 |

## Round 4, stage P, the data pull (28 to 30 September)

| document | date | role |
|---|---|---|
| `decisions/round4_data_pull.md` | 28 Sep | instruction, stages P0 to P7 |
| `round4_data_plan.md` | 28 Sep | plan, with the P1 decision (section 8) and the P7 decisions and P8 (section 9) |
| `decisions/round4_data_P1_decision.md` | 28 Sep | decision on the P1 stop (proceed as selected) |
| `round4_data_report.md` | 28 Sep | report at P7; tag `round4-data`. Nineteen escalations |
| `decisions/round4_data_P7_decisions.md` | 30 Sep | acceptance, a decision on each escalation, and the P8 addendum |
| `round4_data_P8_report.md` | 30 Sep | report on P8 (lung task at 20 samples and 15 donors, schema v2, control-free panels, code corrections); tag `round4-data-v2`, the tag both tracks start from |

## Round 4, the two tracks (30 September to October)

Each gate's report arrived as a pull request into `main`, merged by Nicolas with a merge commit after the oversight chat accepted it. Everything below is on `main` unless marked.

**The PPI track** (branch `round4-ppi`, stages Q0 to Q5 and the closing unit Q5a, gates Q1, Q3, Q5; complete).

| document | date | role |
|---|---|---|
| `decisions/round4_ppi_track.md` | 30 Sep | instruction |
| `round4_ppi_plan.md` | 30 Sep onward | plan; section 8 lists eight points flagged in the instruction; later sections transcribe every addendum and memo, and Nicolas's decisions on where work runs |
| `decisions/round4_ppi_addendum1.md` | 30 Sep | addendum inside interval 1 (answers to the eight flags, the textbook form for the design-based target, the ACS source) |
| `round4_ppi_Q1_report.md` | 1 Oct | report at the Q1 gate; tag `round4-ppi-Q1` |
| `round4_ppi_estimator_definition.md` | 1 to 3 Oct | the estimator, defined once; proposed at Q1, finalised by the Q3 decision memo, and given the linearised design-target variance after Q5a |
| `decisions/round4_ppi_Q1_decisions.md` | 1 Oct | decision at Q1 |
| `round4_ppi_theory.md` | 1 Oct onward | the gain theorem, the allocation result and the two labelling regimes, derived |
| `round4_ppi_Q3_report.md` | 2 Oct | report at the Q3 gate (Q2, Q3, the Q1 supplement and the theorem check); tag `round4-ppi-Q3` |
| `decisions/round4_ppi_Q3_decisions.md` | 2 Oct | decision at Q3. It reads the Q3 headline against the whole grid, finalises the estimator, corrects the tuning rule for the design-based target, and adds the tuning-cost result |
| `decisions/round4_ppi_addendum2.md` | 2 Oct | where the conformal track's outputs are and how Q5 builds the joint design table |
| `round4_ppi_final_report.md` | 2 to 3 Oct | end-of-track report (Q1 to Q5, then Q5a as section 10); tag `round4-ppi-final` marks the report before Q5a. Its closing page, "What the PPI track established", is the summary |
| `decisions/round4_ppi_Q5_decisions.md` | 2 Oct | decision at Q5. Acceptance subject to the closing unit Q5a (the ACS design-interval defect, the spot-weighted rows marked as nuisance rows, the unclipped tuning coefficient) |
| `decisions/round4_ppi_Q5a_closing.md` | 3 Oct | acceptance of Q5a and close of the track; a record, not handed to the session |

**The conformal track** (branch `round4-conformal`, stages C0 to C4, gates C2, C4; complete).

| document | date | role |
|---|---|---|
| `decisions/round4_conformal_track.md` | 30 Sep | instruction |
| `round4_conf_plan.md` | 30 Sep onward | plan; section 8 lists five points flagged in the instruction; later sections transcribe the addendum and both memos |
| `decisions/round4_conformal_addendum1.md` | 30 Sep | addendum inside interval 1 (answers to the five flags, the GHCP pool rule, the rest of the lower-bound cap, the ACS source) |
| `round4_conf_candidate_definitions.md` | 1 Oct | the four candidate methods as written before they ran |
| `round4_conf_lower_bound.md` | 30 Sep to 1 Oct | the lower-bound scoping at no test-group observations, each step marked derived, conjectured or failed |
| `round4_conf_C2_report.md` | 2 Oct | report at the C2 gate (the simulation testbed, the GHCP reproduction, the candidates and the go or no-go); tag `round4-conf-C2` |
| `decisions/round4_conformal_C2_decisions.md` | 2 Oct | decision at C2 (no candidate goes forward; the plain within-donor split added; the scoping closed) |
| `round4_conf_final_report.md` | 2 Oct | end-of-track report (the real-data map over calibration donors and labelled spots); tag `round4-conf-final`. Its closing page, "What the conformal track established", is the summary |
| `decisions/round4_conformal_C4_decisions.md` | 2 Oct | acceptance and close of the track |

---

## Living documents

| document | what it is |
|---|---|
| `WAYS_OF_WORKING.md` | procedures, each tied to the failure it prevents; added to every round |
| `README.md` (this file) | the reading guide; update it when a document is added |

## Superseded and withdrawn

`superseded/` holds working documents that a later document replaced, each bannered with what replaced it. Withdrawn readings that live inside frozen documents are listed in `decisions/round4_oversight_handoff.md` section 12 (dead ends) and in the README's known limitations. The most important are the IDC one-donor reading (withdrawn by round 3's D3), the round-1 "institution shift" scalar, and the D4 probe's 31% to 34% morphology share (quarantined by the P7 decisions).
