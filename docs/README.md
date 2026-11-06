# `docs/`, a reading guide

This is the map of the project's documents. Since 9 October 2026 they are filed in time order, by round, then by interval, then by track, so reading the folders in order is reading the project in the order it happened. Each round folder has its own reading guide, and this file points to them. The current state of the project is not kept here. It is in `CLAUDE.md` at the repository root.

## Start here

1. `CLAUDE.md`, the operating file. It holds the current state, the next action, Nicolas's preferences and the hard rules.
2. The reading guide of the last closed round, `docs/round09/README.md`, closed on 6 November, and of round 8, `docs/round08/README.md`, which is still formally open (decision D6 in `CLAUDE.md`). For the PPI paper, the latest account is round 9's track fewcluster, its closing report `docs/round09/i04/fewcluster/round09_fewcluster_closing_report.md` and its draft `docs/round09/tracks/fewcluster/paper_draft_v0.md`, read with round 8's positioning note for what was already in print. The older account, `docs/round07/oversight/round07_ppi_results_explained.md`, predates both, and round 5's guide, `docs/round05/README.md`, holds the estimator that round 9 replaced with Williams' form.
3. `docs/progress-log.md`, what happened at each step and why the project moved, newest first.

For the methods themselves, derived from scratch, read `docs/reference/methods_and_state_of_play.md` and `docs/reference/concepts_explained_round4.md`.

## How the folders work

- `docs/roundNN/` holds one round. `round00` holds what came before round 1.
- `00_prep/` inside a round holds what was written after the previous round closed and before this one started, such as a change of direction, an oversight handoff or advisor-deck preparation.
- `iKK/<track>/` is interval KK of one track. Interval 1 opens with the track's instruction. Each later interval opens with the decision memo that answered the previous gate report, and ends with the next gate report. A track's closing memo sits alone in its last interval folder. Intervals are numbered per track, so the gate table in each round's guide gives the order across tracks.
- `tracks/<track>/` holds the documents a track kept updating across intervals, such as its execution plan, theory and definitions. They are frozen once the round closes.
- `oversight/` holds oversight documents written during a round and not tied to one track.
- `masterplan.md` is the round's plan. Rounds 1 to 5 have none from the time, so each has a short note written at migration that points to the documents that served as its plan.
- Every document kept its file name when it moved, and every name is unique, so a bare file name still finds its file. `docs/moved.md` lists each old path with its new one.

Through round 8 each stage of work produced the same chain. A coordinating chat (called the oversight chat in the record) wrote an instruction or a decision memo. The session that ran the work (an execution session) transcribed it into its operating plan before running anything, flagged what looked wrong rather than changing it, and wrote a gate report. The next memo answered that report. Reports are written once and not edited, and corrections go in the next memo or report. Tags mark the state of the repository at each gate.

## Standing documents

| Document | What it is |
|---|---|
| `docs/progress-log.md` | what happened and why, newest first, with an entry for every memo, gate review and decision |
| `docs/WAYS_OF_WORKING.md` | procedures, each tied to the failure it prevents, and the guardrails register. Removed on the round 9 branches for their independent sessions and kept on `main` pending the workflow revamp of November 2026 |
| `docs/EXECUTION_RULES.md` | the standing rules every execution session follows, from 13 October 2026. Track instructions and memos cite it instead of restating it. Kept on `main` as above |
| `docs/moved.md` | each old path and its new path, from the move on 9 October 2026 |
| `docs/reference/methods_and_state_of_play.md` | every method derived from scratch, every round-3 result with how and why, what has not been tried, and what the rest of HEST-1k holds (27 September) |
| `docs/reference/concepts_explained_round4.md` | the nineteen concepts Nicolas asked about, with the regime B correction in its section 4 (28 to 29 September) |
| `docs/superseded/` | working documents a later document replaced, each bannered with what replaced it. It holds the round-3 park note (`round3_park_note.md`) and the flat index this guide replaced on 30 September (`README_index_2026-09-30.md`) |

## Rounds

| Round | Dates | Folder | In one line | Summary |
|---|---|---|---|---|
| 0 | early September | `docs/round00/` | the proposal and the literature landscape that produced Topics A and B | `docs/round00/README.md` |
| 1 | 12 to 16 September | `docs/round01/` | a faithful replication of the HEST-1k benchmark and its instrumentation | `docs/round01/README.md` |
| 2 | 16 to 21 September | `docs/round02/` | from replication to project motivation, stages R0 to R8, then the first advisor deck and its numeric-claim gate | `docs/round02/README.md` |
| 3 | 22 to 24 September | `docs/round03/` | the first experiments for both topics, after which Topics A and B as framed were retired | `docs/round03/README.md` |
| 4 | 28 September to 3 October | `docs/round04/` | after the change of direction to labelling budgets for prediction-powered inference with clustered data, a data pull and two tracks (inference and prediction sets) | `docs/round04/README.md` |
| 5 | 7 to 9 October | `docs/round05/` | the inference track's final interval, regime B, regression form and cluster selection, and the prediction-set map above 10 calibration donors | `docs/round05/README.md` |
| 6 | 11 to 13 October, reopened 12 October | `docs/round06/` | David's cheatsheet experiment. With a size-limited cheatsheet, Opus did not beat a pathology foundation model on unseen spots, and reached 0.8 on seen spots only by copying. Reopened for an extension on held-out CCRCC patients with rubric-bound cheatsheets, where any cheatsheet helped, size did not, and none reached the pathology model. Moved on 19 October to the private repository `NicWYZ/textual-st-histology` | `docs/round06/README.md`, a pointer |
| 7 | 13 to 15 October | `docs/round07/` | Two tracks. Federated learning: a literature review and scoping experiments found a one-round head exact and cheap, no clear gain across real sources, and measurable costs from privacy and from centers measuring different genes. The PPI paper: repositioned against Broska and Howes, weighting under rejective selection fails, rejective selection with `rej_t` is narrowest on census and a cube design with bounded probabilities matches it on tissue, k-center fails, and a corrected Broska and Howes interval is strong at four labelled clusters | `docs/round07/README.md`, "What the round established" |
| 8 | from 19 October, open | `docs/round08/` | the PPI paper's positioning against the survey-sampling literature and newer PPI work, then its plan and the runs it needs. The positioning note (gate P3, its pull request merged on 22 October) finds every formula the paper would display classical or in print, and round 5's cross-fitted estimator a known estimator missing one factor. No track of its own followed. Round 9 carried out its recommendation in effect, and the round stays formally open until Nicolas rules on the note (D6) | `docs/round08/README.md`, once the round closes |
| 9 | 24 October to 6 November | `docs/round09/` | preparation on branch `claude-science` found no methodological core that survives the literature check, and found that on Visium a shared technical factor dominates between-donor variation and one technical-outlier donor breaks few-cluster intervals. Two independent tracks followed on their own branches. Track `fewcluster` proved three frontier theorems for finite-sample valid inference with few labelled clusters (not found in print, provisionally), compared labelling whole clusters with a few units in every cluster under them, replaced round 5's estimator with Williams' form and wrote a first paper draft. Track `newtopic` found no open direction outside clustered PPI. The three branches were merged into `main` at the close | `docs/round09/README.md`, "What the round established" |

## Superseded and withdrawn

Withdrawn readings that live inside frozen documents are listed in the round guides under "Corrections and withdrawn readings", in `docs/round04/oversight/round4_oversight_handoff.md` section 12 and `docs/round05/00_prep/round5_oversight_handoff.md` section 14 (dead ends), and in the root README's known limitations. The most important are the IDC one-donor reading (withdrawn by round 3's D3), the round-1 "institution shift" scalar, and the D4 probe's 31% to 34% morphology share (quarantined by the P7 decisions).
