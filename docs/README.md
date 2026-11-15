# `docs/`, the reading guide

The record of the project. The project's status lives only in `CLAUDE.md`'s state block, and a running track's in its plan's state block. Each closed round's `README.md` is its summary and the authority on what the round established. Git history and tags hold what happened, and the full record as it stood before it was reduced is at tag `record-full-2026-11`.

## Start here

1. `CLAUDE.md`, in full, for the state block, the session start, the working rules and the hard rules.
2. The summary of the last closed round (`round10/README.md`), then earlier summaries as the work needs them. `round10/00_prep/round10_findings_survey.md` lists what rounds 1 to 9 established, by the question each finding answers.

## How the folders work

**New rounds, by track (from round 11).**

- `round<NN>/README.md` is the round's summary once it closes, and `round<NN>/masterplan.md` its plan, with the oversight session's expectations.
- `round<NN>/00_prep/` holds what was written after the previous round closed and before the masterplan, such as the literature survey.
- `round<NN>/<track>/` holds one track: its brief, its plan (which opens with a state block and records each gate's decisions), its gate reports and its notes, such as a literature check, a theory note or a methods note. File names carry the full prefix (`round11_<track>_G1_report.md`).
- `round<NN>/oversight/` holds the oversight session's documents of the round that belong to no single track.

**Closed rounds 0 to 10, as they were filed.** `round<NN>/iKK/<track>/` holds one interval of one track, ending with its gate report. `round<NN>/tracks/<track>/` holds the track's plan, theory notes, definitions and other living documents. The prep and oversight folders are as above, and `round<NN>/round<NN>_methods_note.md`, where there is one, quotes the definitions and decisions of documents that were removed. Each kept report, survey and plan opens with a line naming its date, the tag that holds it as reviewed and the summary that says what stands. Gate tags are `round<N>-<track>-<gate>` (`git tag -l 'round5-*'`).

**Elsewhere.** `round00/` holds what came before round 1, and `reference/` holds material consulted across rounds. Results follow the rounds under `results/round<N>/`.

## Standing documents

| Document | Role |
|---|---|
| `EXECUTION_RULES.md` | how an execution session starts, works and hands over, with the gate rule |
| `WAYS_OF_WORKING.md` | procedures, each tied to the failure behind it: checks, literature, documents, the numeric-claim sweep, decks |
| `environment.md` | people, the Longleaf trees and scheduler notes, data quirks, and what a session needs |
| `reference/methods_and_state_of_play.md` | every method the project derived from scratch up to round 3, with its derivation (27 September 2026) |

## Rounds

| Round | Dates | What it found | Summary | Full record |
|---|---|---|---|---|
| 0 | September 2026 | the proposal and the literature landscape that produced Topics A and B | `round00/README.md` | `record-full-2026-11` |
| 1 | 12 to 16 Sep | a faithful replication of the HEST-1k benchmark on Longleaf and its instrumentation | `round01/README.md` | `record-full-2026-11` |
| 2 | 16 to 21 Sep | which of the benchmark's apparent problems are real (HEST's patient labels are wrong in both directions), the first advisor deck and the numeric-claim sweep | `round02/README.md` | `record-full-2026-11` |
| 3 | 22 to 24 Sep | the first experiments for both topics, after which Topics A and B as framed were retired | `round03/README.md` | `record-full-2026-11` |
| 4 | 28 Sep to 3 Oct | PPI read as the survey-sampling difference estimator; a data pull and two tracks, inference with few labelled donors and prediction sets for a new donor | `round04/README.md` | `record-full-2026-11` |
| 5 | 7 to 9 Oct | the inference track's regime B, regression form and cluster selection, round 5's estimator defined once, and the prediction-set map above 10 calibration donors | `round05/README.md` | `record-full-2026-11` |
| 6 | 11 to 13 Oct | David's cheatsheet experiment, now in `NicWYZ/textual-st-histology` | `round06/README.md` | `record-full-2026-11` |
| 7 | 13 to 15 Oct | federated learning scoped and moved to `NicWYZ/ST-Fed-Learn`; few-cluster selection designs for the PPI paper, some of whose claims round 8 withdrew | `round07/README.md` | `record-full-2026-11` |
| 8 | 19 Oct to 6 Nov | every formula the PPI paper would display is classical or in print, and round 5's estimator is a known one missing one factor | `round08/README.md` | `record-full-2026-11` |
| 9 | 24 Oct to 6 Nov | no methodological core survives the literature check; three provisional frontier theorems for few labelled clusters; a shared technical factor dominates between-donor variation on Visium | `round09/README.md` | `record-full-2026-11` |
| 10 | 6 to 15 Nov | the reframing to an applied paper with cited methods; the methods ledger, and final runs with a fixed coefficient of 1 on HEST, ACS and six corpus tasks, giving the paper's numbers table | `round10/README.md` | `record-full-2026-11` |
