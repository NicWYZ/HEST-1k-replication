# `docs/`, a reading guide

This is the map of the project's documents. Since 9 October 2026 they are filed in time order, by round, then by interval, then by track, so reading the folders in order is reading the project in the order it happened. Each round folder has its own reading guide, and this file points to them. The current state of the project is not kept here. It is in `CLAUDE.md` at the repository root.

## Start here

1. `CLAUDE.md`, the operating file. It holds the current state, the next action, Nicolas's preferences and the hard rules.
2. The reading guide of the latest round, `docs/round05/README.md`. Its last four sections say what the round established, what was corrected, what was carried forward and what to read first for the next round.
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

Each stage of work produces the same chain. The oversight chat writes an instruction or a decision memo. The execution session transcribes it into its operating plan before running anything, flags what looks wrong rather than changing it, and writes a gate report. The next memo answers that report. Reports are written once and not edited, and corrections go in the next memo or report. Tags mark the state of the repository at each gate.

## Standing documents

| Document | What it is |
|---|---|
| `docs/progress-log.md` | what happened and why, newest first, with an entry for every memo, gate review and decision |
| `docs/WAYS_OF_WORKING.md` | procedures, each tied to the failure it prevents, and the guardrails register |
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

## Superseded and withdrawn

Withdrawn readings that live inside frozen documents are listed in the round guides under "Corrections and withdrawn readings", in `docs/round04/oversight/round4_oversight_handoff.md` section 12 and `docs/round05/00_prep/round5_oversight_handoff.md` section 14 (dead ends), and in the root README's known limitations. The most important are the IDC one-donor reading (withdrawn by round 3's D3), the round-1 "institution shift" scalar, and the D4 probe's 31% to 34% morphology share (quarantined by the P7 decisions).
