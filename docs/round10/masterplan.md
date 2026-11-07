# Round 10, masterplan

*Written on 6 November 2026 by the oversight chat through the `project-record` skill, after Nicolas's reframing and his answers of the same day. Living while the round runs. Amendments are appended at the end with their date, and the text above them is not rewritten. It is frozen at the round's close.*

## Why this round

On 6 November Nicolas reframed the project's objective (`00_prep/round10_reframing.md`, section 1). The aim is to answer the two questions of the September proposal, calibrated uncertainty for histology-predicted expression and valid inference with it, on the project's data, applying existing or classical methods where they exist and devising the project's own only where a documented literature search finds a genuine gap. The survey of nine rounds (`00_prep/round10_findings_survey.md`) found that the record already answers most of both questions with existing methods, that the one piece of theory which came from a problem met in practice is round 9's frontier, and that the inference numbers of rounds 5 to 7 were computed with an estimator and a variance that rounds 8 and 9 corrected and have not been rerun.

On 6 November, later, Nicolas settled how the round runs. He opened the round on the structure the oversight chat put to him in the chat that evening (an applied paper, three tracks, a literature search before any derivation), so that structure is taken as accepted and its details below remain the oversight chat's and are revised as the round goes. The methods ledger is built by the oversight chat with Opus subagents. The final runs are a Claude Science session on Longleaf. The estimator for the final runs is decided by the ledger after the sources are read. Prediction sets stay in the paper only if that makes sense, which the ledger assesses at L3 and he decides. The venue depends on what the paper ends up with. The decision of 6 November on paper reads applied only to closing round 9, so reads resume here. The advisor line in `CLAUDE.md` and the advisor meeting are not to be worried about now.

## Goal

An applied paper answering the two original questions on HEST-1k, with ACS PUMS 2018 as a second domain, every method cited to its source, the project's own method only where the ledger records a genuine gap. Draft v1 by January 2027, submission by spring 2027.

## Tracks

| Track | Who and where | Branch | Brief | Writes to | Gate |
|---|---|---|---|---|---|
| `ledger` | the oversight chat with Opus subagents, no compute | `round10-ledger` for the subagents' logs under `results/round10/ledger/`, one pull request at L3; documents as documentation commits to `main` | `i01/ledger/round10_ledger_brief.md` | `docs/round10/i01/ledger/`, `docs/round10/i02/ledger/` (Nicolas's answer at L3), `docs/round10/tracks/ledger/`, `docs/round10/i01/final-runs/` (the brief it writes), `results/round10/ledger/` | L3, Nicolas reviews the ledger, the two recommendations, the writing plan and the final-runs brief |
| `final-runs` | one Claude Science session on Longleaf, under `docs/EXECUTION_RULES.md` | `round10-final-runs` | `i01/final-runs/round10_final_runs_brief.md`, written by track `ledger` at L3 and checked by a fresh agent | `docs/round10/iKK/final-runs/`, `docs/round10/tracks/final-runs/`, `results/round10/final_runs/`, `code/scripts/round10_final_runs_*` | F1 anchors, F2 inference, F3 prediction sets and designs, F4 final report and pull request |
| `paper` | the oversight chat | none | written at F4 | `docs/round10/tracks/paper/` | draft v1 with a fresh-agent check |

The tracks run in order. `final-runs` does not start until L3 is accepted, and `paper` not until F4's pull request is merged.

**Track `ledger`** builds, for each section of the paper outline (`00_prep/round10_findings_survey.md`, section 4.2), a table of the existing method applied, its source with read level, where it is implemented in `code/scripts/`, what has been validated and what is missing; reads the sources not yet read, with papers it cannot retrieve going to Nicolas as one list of at most 10 through the UNC proxy; decides the estimator for the final runs (question E) and recommends on the coefficient rule (R7-6, Nicolas's) and on prediction sets (question P, Nicolas's); and writes the writing plan and the final-runs brief with predictions written first.

**Track `final-runs`** produces one clean set of analyses with the cited methods on CCRCC, INDIANA_KIDNEY, LUNG_XENIUM and ACS. It first reproduces one round 5 cell and one round 7 cell as anchors. It then runs inference in both regimes with the estimator the ledger chose, the fixed and cross-fitted coefficients and a level-free variance, including the check of whether rounds 5 to 7's intervals carried the inflation, and redoes the design comparison on that footing. If prediction sets stay, it reruns the prediction-set map with INT5 and the cross-gene set and the adaptive scores at full gene scope. It runs the probe and take-all design, and re-cites the frontier numbers per task. Its brief names its clone on Longleaf, since a Claude Science session there has no Mac clone. When it meets a problem the ledger does not cover, it searches the literature first with subagents, records the search, and reports at its next gate; a derivation starts only after Nicolas has seen the search and agreed the gap is genuine.

**Track `paper`** drafts v1 from the writing plan and the final report, and whatever Nicolas then wants for the advisors. The reframing's suggestion of a sensitivity run on both normalization scales is left to the ledger's brief for the final runs.

## Schedule

The tracks run in order, `ledger`, then `final-runs`, then `paper`. No durations are given (amendment of 7 November).

## Open questions

| # | Question | Default | Who decides |
|---|---|---|---|
| E | The estimator for the final runs (Williams with two groups, the fold-wise form, or round 5's) | round 5's as defined | the ledger, after reading Williams, Mickey if retrievable, Sanguiao Sande and Zhang, and the fold-wise papers (Lu et al. 2025, An et al. 2026); recorded at L3. R7-6, the coefficient rule, stays Nicolas's, with the ledger's recommendation |
| P | Whether prediction sets stay in the paper (R8-1) | the fewcluster draft defers them | Nicolas at L3, on the ledger's recommendation |
| D5 | Normalization of the estimands | both scales run and the effect quantified | decided 7 November: settled by testing; the final runs carry both scales and report the difference (F2) |
| Q1 | Whether regime B can be bought on a spatial platform, and the cost model | no cost claim for spatial platforms | deferred 7 November to the next advisor deck, time not set |
| V | Whether the variance-share bound is defensible | regime B stated under it beside the unbounded column | decided 7 November: settled by the literature and by testing, not by one person's knowledge; the ledger searches (L3), the final runs test (F3) |
| DATA | Whether round 10's tasks extend to the federated project's corpus on Longleaf | decided 7 November: use as much of the existing data as possible, read only, no new download; the L0 scope names the tasks | decided (Nicolas) |
| Q3 | Venue and lead result | open | Nicolas, once the paper's content is known, which the oversight chat reads as after F4 |
| R7-7, R7-5, O5 | Design recommended, positioning | their state-block defaults | Nicolas, when the time comes |
| O3 | The paper and the lab's manuscript | neither refers to the other | decided 7 November (Nicolas) |

## Predictions

Scored at F4 as held, partly held, refuted or not tested.

- P10.1 (scored at F2 and F3). On CCRCC, INDIANA_KIDNEY and LUNG_XENIUM at 8 labelled donors, the median over genes of the tuned interval's coverage under the level-free variance is 0.02 to 0.05 below the value rounds 5 to 7 reported for the same cell, and the ordering of designs by median width on round 7's matched supported cells at 8 labelled clusters is unchanged.
- P10.2 (scored at L3). The ledger finds a published variance estimator for the exactly unbiased split-sample form under simple random sampling without replacement, and finds no published interval with a finite-sample coverage guarantee for the design target at 4 to 16 labelled clusters without a restriction on the population.
- P10.3 (scored at F3, not tested if prediction sets are dropped). At 10 calibration donors and the nominal level of round 5's map, the target donor's own full conformal set becomes narrower in median width than HCP from 9 labelled spots on CCRCC and LUNG_XENIUM, and on INDIANA_KIDNEY its median width stays within 2% of the plain within-donor split's at 9 to 15 labelled spots.

## What closes the round

F4's pull request merged and track `paper`'s draft v1 checked, or Nicolas's decision to close earlier. The close runs through `/project-record`.

## Amendments

- 7 November, later. Nicolas answered: DATA, use as much of the existing data as possible; D5 by testing with the effect quantified; Q1 deferred to the next deck; V by the literature and testing; O3 neither refers to the other; the carried housekeeping to be decided by the oversight chat with good judgement (its decisions are in `CLAUDE.md`'s carried line); everything else revisited when the time comes. The ledger's L0 scope then started.
- 7 November. Nicolas asked that no time estimates be given for intervals, since the project runs much faster than such estimates; the schedule section and the ledger brief no longer carry them. He also asked, before round 10 starts, whether the project has reached a stopping point, whether the original questions are answered adequately, and whether all available data have been used, pointing to the federated project's pull of nearly all usable HEST data. The oversight chat's answer is in `docs/round10/00_prep/round10_stopping_point.md`, and the data question is open question DATA above. The ledger does not start L0 until DATA is answered.
