# `docs/`, a reading guide

This is the map of the project's documents. Since 9 October 2026 they are filed in time order, by round, then by interval, then by track, so reading the folders in order is reading the project in the order it happened. Each round folder has its own reading guide, and this file points to them. The current state of the project is not kept here. It is in `CLAUDE.md` at the repository root.

## Start here

1. `CLAUDE.md`, the oversight chat's operating file. Its `state` block is the one place that says where the project stands, and nothing here repeats it.
2. The reading guide of the round in hand, and of the last closed round, from the table below. For the PPI paper, the latest account is round 9's track fewcluster, read with round 8's positioning note for what was already in print.
3. `docs/progress-log.md`, what happened at each step and why the project moved, newest first.

For the methods themselves, derived from scratch, read `docs/reference/methods_and_state_of_play.md` and `docs/reference/concepts_explained_round4.md`.

## How the folders work

- Each `docs/round05`-style folder holds one round. `round00` holds what came before round 1.
- A round's `00_prep` folder holds what was written after the previous round closed and before this one started, such as a change of direction, an oversight handoff or advisor-deck preparation.
- `iKK/<track>/` is interval KK of one track. Interval 1 opens with the track's instruction, or from round 9 its brief. Each later interval opens with the decision that answered the previous gate report (an oversight memo through round 7, a decision file written by the session from round 9), and ends with the next gate report. A track's closing memo sits alone in its last interval folder. Intervals are numbered per track, so the gate table in each round's guide gives the order across tracks.
- `tracks/<track>/` holds the documents a track kept updating across intervals, such as its execution plan, theory and definitions. They are frozen once the round closes.
- A round's `oversight` folder holds oversight documents written during a round and not tied to one track.
- `masterplan.md` is the round's plan. Rounds 1 to 5 have none from the time, so each has a short note written at migration that points to the documents that served as its plan.
- **Names.** Tracks and stages are named per round (`round5_ppi_*`, stages E0 to E5; `round5_conf_*`, stages W0 to W5; `round06_cheatsheet_*` documents and `round6_cheatsheet_*.py` scripts, stages C0 to C7, now in `NicWYZ/textual-st-histology`; `round07_fedlearn_*` documents and `round7_fedlearn_*.py` scripts, stages F0 to F4; `round07_ppi_*` documents and `round7_ppi_*.py` scripts, stages S0 to S5 with S2b and S4b; `round08_positioning_*` documents, stages P0 to P3, results in `results/round8/positioning/`; `round09_fewcluster_*` and `round09_newtopic_*` documents and `round9_<track>_*.py` scripts, results in `results/round9/<track>/`, with the preparation's scripts `round9_*.py` and results in `results/round9/scan/`, `results/round9/diagnostics/`, `results/round9/between/`, `results/round9/stud/`, `results/round9/norm/` and `results/round9/probe/`). Tags mark each gate (`round5-ppi-E2`, `round6-cheatsheet-C1`, `round7-fedlearn-F2`).
- `[proposed]` marks what the oversight chat proposed and Nicolas has not accepted, and `[verify]` a statement written from memory.
- The numeric-claim sweep, `code/scripts/verify_numeric_claims.py`, runs as `docs/WAYS_OF_WORKING.md` shows, with each track's exceptions in its own `.verify-exceptions-<round>-<track>` file. The oversight chat sweeps `README.md`.
- New file names carry the full prefix (`round06_ppi_E2_report.md`). Every document kept its file name when it moved, and every name is unique, so a bare file name still finds its file. `docs/moved.md` lists each old path with its new one.

From round 2 to round 7 each stage of work produced the same chain. A coordinating chat (called the oversight chat in the record) wrote an instruction or a decision memo. The session that ran the work (an execution session) transcribed it into its operating plan before running anything, flagged what looked wrong rather than changing it, and wrote a gate report. The next memo answered that report. Reports are written once and not edited, and corrections go in the next memo or report. Tags mark the state of the repository at each gate.

## Standing documents

| Document | What it is |
|---|---|
| `docs/progress-log.md` | what happened and why, newest first, with an entry for every memo, gate review and decision |
| `docs/WAYS_OF_WORKING.md` | the oversight chat's sample audit, the literature and novelty check, the document rules, the numeric-claim sweep and the deck conventions. Cut to these on 6 November 2026, when its Longleaf notes and data quirks moved to `docs/environment.md` |
| `docs/EXECUTION_RULES.md` | the one standing document for execution sessions, from 13 October 2026, revised for the project-record round layout on 6 November. Briefs cite it instead of restating it |
| `docs/environment.md` | machines, clones, accounts, Longleaf scheduler notes, the HEST patient-label quirk, and what a new account must recreate (6 November 2026) |
| `docs/project_instructions.md` | the texts pasted into the claude.ai project and the Claude Science project, verbatim (6 November 2026) |
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
| 8 | 19 October to 6 November, closed after round 9 | `docs/round08/` | the PPI paper's positioning against the survey-sampling literature and newer PPI work, then its plan and the runs it needs. The positioning note (gate P3, its pull request merged on 22 October) finds every formula the paper would display classical or in print, and round 5's cross-fitted estimator a known estimator missing one factor. No track of its own followed. Round 9 carried out its recommendation in effect, and Nicolas closed the round on 6 November | `docs/round08/README.md`, "What the round established" |
| 9 | 24 October to 6 November | `docs/round09/` | preparation on branch `claude-science` found no methodological core that survives the literature check, and found that on Visium a shared technical factor dominates between-donor variation and one technical-outlier donor breaks few-cluster intervals. Two independent tracks followed on their own branches. Track `fewcluster` proved three frontier theorems for finite-sample valid inference with few labelled clusters (not found in print, provisionally), compared labelling whole clusters with a few units in every cluster under them, recommended `[proposed]` Williams' form in place of round 5's estimator and wrote a first paper draft. Track `newtopic` found no open direction outside clustered PPI and hierarchical conformal prediction. The three branches were merged into `main` at the close | `docs/round09/README.md`, "What the round established" |

## Superseded and withdrawn

Withdrawn readings that live inside frozen documents are listed in the round guides under "Corrections and withdrawn readings", in `docs/round04/oversight/round4_oversight_handoff.md` section 12 and `docs/round05/00_prep/round5_oversight_handoff.md` section 14 (dead ends), and in the root README's known limitations. The most important are the IDC one-donor reading (withdrawn by round 3's D3), the round-1 "institution shift" scalar, and the D4 probe's 31% to 34% morphology share (quarantined by the P7 decisions).
