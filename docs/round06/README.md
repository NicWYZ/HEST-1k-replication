# Round 6, the cheatsheet experiment (11 to 12 October 2026, reopened 12 October)

David proposed an experiment by email. An agent predicts the expression of 50 genes from H&E patches. A second agent, which saw the measured expression, writes a text cheatsheet of limited size that the first may use. The question is how large the cheatsheet must be for the predictions to reach a given accuracy. Nicolas decided on 11 October to run it as round 6, with the purpose of learning whether few-shot prediction with a general-purpose language model can beat pathology foundation models. The PPI paper's next round becomes round 7.

**Track.** cheatsheet (branch `round6-cheatsheet` for C0 and C1, and `claude/beautiful-mccarthy-feog45` for C2 and C3, stages C0 to C3, run by a Claude Code cloud session, with one packaging job on Longleaf). **Starts from** `main` at the commit that carries the masterplan and the instruction.

**Reopened.** Nicolas reopened the round on 12 October, after its close, for an extension on held-out patients in intervals i04 and i05 of the same track. It keeps only arm C, uses 10 FFPE slides of HEST-bench `CCRCC` (7 for writers, 3 for testing), sizes from 256 to 65,536 bytes, and a rubric for biological, transferable cheatsheets that a checker agent enforces. It runs in a local Claude Code session on Nicolas's Mac that reaches Longleaf over SSH, on branch `round6-cheatsheet-ext`, stages C4 to C7. The plan is the masterplan's section "Extension" and the instruction is `i04/cheatsheet/round06_cheatsheet_ext_track.md`. The sections from "What the round established" on describe intervals i01 to i03 and are extended when the extension closes.

## Gates

| Date | Track | Gate | Report | Answered by | Tag | Pull request |
|---|---|---|---|---|---|---|
| 12 Oct | cheatsheet | C1 | `i01/cheatsheet/round06_cheatsheet_C1_report.md` | `i02/cheatsheet/round06_cheatsheet_C1_decisions.md` | `round6-cheatsheet-C1` | #23 |
| 12 Oct | cheatsheet | C3 | `i02/cheatsheet/round06_cheatsheet_final_report.md` | `i03/cheatsheet/round06_cheatsheet_final_decisions.md` | `round6-cheatsheet-final` | #24 |
| 12 Oct | cheatsheet | C5 (extension) | `i04/cheatsheet/round06_cheatsheet_C5_report.md` | `i05/cheatsheet/round06_cheatsheet_C5_decisions.md` | `round6-cheatsheet-C5` | #25 |

## Documents

| Document | Date | Role |
|---|---|---|
| `masterplan.md` | 11 Oct, amended to 12 Oct, frozen 12 Oct, reopened 12 Oct with a living section "Extension" | the round's plan, with the design, the trial count, the oversight chat's choices, the predictions, the open questions, three points explained for Nicolas, and dated amendments |
| `00_prep/round06_round5_results_explained.md` | 11 Oct | for Nicolas, the four main round-5 results explained with their theory (the level term in regime B, the cross-fitting term of the design-target interval, the full conformal set inside the target donor, balanced selection of the labelled clusters), the other results briefly, and what is not established |
| `i01/cheatsheet/round06_cheatsheet_track.md` | 11 Oct, living, frozen 12 Oct | instruction for the cheatsheet track, with the fixed prompts, the isolation properties and stages C0 to C3, revised in place with a dated list at its top |
| `i01/cheatsheet/round06_cheatsheet_C1_report.md` | 12 Oct | report at the C1 gate (C0 setup and the pilot of twelve slots at high effort) |
| `i02/cheatsheet/round06_cheatsheet_C1_decisions.md` | 12 Oct | decision at C1. Medium effort from here, exclusion only for leak signs, one sentence added to every prompt, then, at 02:10 the same night, the grid cut to Opus alone with one replicate, 20 sessions |
| `i02/cheatsheet/round06_cheatsheet_final_report.md` | 12 Oct | end-of-track report (C2 and C3), with its closing page "What the cheatsheet experiment established" |
| `i03/cheatsheet/round06_cheatsheet_final_decisions.md` | 12 Oct | acceptance and close of the track, with the readings for the record and one correction |
| `oversight/round06_cheatsheet_summary.md` | 12 Oct | the two-page summary of design, method, implementation, results and discussion, presented in place of slides |
| `tracks/cheatsheet/round06_cheatsheet_plan.md` | 11 to 12 Oct, living, frozen 12 Oct | the session's operating plan, with flags F1 to F20 |
| `i04/cheatsheet/round06_cheatsheet_ext_track.md` | 12 Oct, living | instruction for the extension, stages C4 to C7, with the slides, sampling, rubric, prompts, audit loop, isolation on the Mac, comparators and predictions X.1 to X.8 |
| `i04/cheatsheet/round06_cheatsheet_C5_report.md` | 13 Oct | report at the C5 gate (C4 setup on the Mac and the pilot of three sessions) |
| `i05/cheatsheet/round06_cheatsheet_C5_decisions.md` | 12 Oct | decision at C5. Harness accepted unchanged, the pilot counts, the grid runs as planned |
| `tracks/cheatsheet/round06_cheatsheet_ext_plan.md` | 12 Oct, living | the extension session's operating plan |

## What the round established

- Asked to reach $\bar r = 0.8$ on spots it had seen, a writer did so only at 262,144 bytes (0.903), by listing every spot with an image fingerprint and its 50 gene values, so the cheatsheet had to hold the measurements (`i03/cheatsheet/round06_cheatsheet_final_decisions.md`, section 2 item 1).
- On unseen spots, Opus 5.5 with a cheatsheet or with the labels in hand did not beat the benchmark head on `uni_v2` embeddings fitted on the same spots. It reached 0.621 against 0.757 on an unseen region and 0.672 against 0.683 on a second patient, the latter within one trial's noise (same memo, item 2).
- On the second patient, 4,096 bytes of class descriptions and per-class means carried most of the gain, from 0.345 to 0.647 (same memo, item 3).
- From 32,768 bytes up, cheatsheets carried feature-extraction code, and at 262,144 bytes training tables of every spot, so the predictor ran a hand-built image model (same memo, item 4).
- Medium effort cost 0.43 times high effort at four slots with no difference that one trial per slot can resolve, except at the baseline (same memo, item 5).
- A confined child Claude Code session in a cloud container, with its own process and network namespaces and a filtering proxy, can run blind trials that reach nothing but the API (`i01/cheatsheet/round06_cheatsheet_C1_report.md`, section 3).

## Corrections and withdrawn readings

- The instruction's revision line of 02:20 gives the pilot writers' sizes as 6,890 and 17,690 bytes. The manifest holds 6,892 and 17,688 (`i03/cheatsheet/round06_cheatsheet_final_decisions.md`, section 3).
- The instruction first routed files through Nicolas's Mac, which a Claude Code cloud session cannot reach. The route was replaced by the private repository `NicWYZ/hest-r6-data` before any data moved (the instruction's revision of 11 October, 22:50).
- Prediction C.1, that zero-shot Opus would score 0.05 to 0.35, was refuted at 0.502 (high effort) and 0.427 (medium) (`i02/cheatsheet/round06_cheatsheet_final_report.md`, section 5).
- Arm A's 0.903 is a copying check and is not reported as a result on its own (`i03/cheatsheet/round06_cheatsheet_final_decisions.md`, section 2).

## Carried forward

- Nothing from this track. Nicolas decided on 12 October that nothing further is pursued.
- Whether and when the summary goes to David is Nicolas's decision (open question R6-3 in `CLAUDE.md`).
- If a cloud execution track runs again, its instruction should not fix a branch name, and the confinement's scripts should be committed in the first interval (`i03/cheatsheet/round06_cheatsheet_final_decisions.md`, section 3).

## Read first next round

Round 7 returns to the PPI paper, so it builds on round 5, not on this round.
- `docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, section 3 for the inference readings and section 5 for the first methods question.
- `docs/round05/i03/conformal/round5_conformal_W5_decisions.md`, section 3.
- `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`, the paper's estimator.
- `docs/round06/00_prep/round06_round5_results_explained.md`, round 5's results explained.

