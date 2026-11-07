# Round 10, track `ledger`, brief

*6 November 2026. Written by the oversight chat for itself and its subagents, under `masterplan.md`. A fresh agent checked this brief before the work started and its findings were worked in.*

## Where it runs

In the oversight chat, with Opus subagents for the parallel parts, and no compute. Its documents reach `main` as documentation commits. Its subagents' query logs go to `results/round10/ledger/` on branch `round10-ledger`, with one pull request at L3. This track runs inside the oversight chat rather than as an independent session, which departs from the rules of 13 and 26 October by Nicolas's decision of 6 November.

## Goal

One document, the methods ledger, that lets the paper be written and the final runs be briefed without any further search. For each section of the paper outline in `00_prep/round10_findings_survey.md`, section 4.2, and for each result the section rests on, the ledger gives the existing method applied, its source (identifier opened, read level, which sections), where it is implemented in `code/scripts/`, what the record has validated about it and where, and what is missing. Where the search finds no existing method for a result the paper needs, the ledger records a genuine gap, with the search that established it, and does not fill it.

## Inputs

`00_prep/round10_findings_survey.md` (the findings with status labels), `00_prep/round10_reframing.md` (what the paper lacks), round 8's positioning note (`docs/round08/i01/positioning/round08_positioning_note.md`, the verdicts C0 to C12 and the sources list of its section 7), round 9's novelty checks under `results/round9/fewcluster/novelty/`, the asset inventory (`claude/round10_survey_F_assets_inventory.md` in the project docs, for the scripts), and `docs/EXECUTION_RULES.md` for the standards the final runs must meet.

## Stages

- **L0. Scope.** The paper's sections and the list of results each rests on, taken from the findings survey's section 4.2, with the open questions of the masterplan (E, P, D5, Q1, V) placed where they bite.
- **L1. Rows.** One Opus subagent per section, in parallel, each writing the ledger rows for its section with every source opened and its read level recorded, the implementing script named from the inventory, and gaps stated with the queries that failed to fill them. Subagents search survey sampling, econometrics and machine learning venues. They read abstracts and full texts where open, log every query, and never cite what they have not opened.
- **L2. Reads.** The sources an applied paper must cite and the record has not read in full. Cochran (1977) chapters 5, 7 and 9 to 11; Särndal, Swensson and Wretman (1992) chapter 8; Mickey (1959); Yang, Qu and Li (JASA 2023) as published; GHCP's full text (Mallick et al., arXiv:2608.15500), checked for a comparison with the target cluster's own full conformal set; Williams (1961) equation 13 and Sanguiao Sande and Zhang (2020) for a variance estimator of the exactly unbiased split form; and the fold-wise papers (Lu, Shi, Liu and Ding 2025; An, Dagdoug, Haziza and Tillé 2026) for question E. If Mickey (1959) cannot be retrieved, E is decided from the others and the gap is recorded. Sources the oversight chat cannot retrieve go to Nicolas as one list of at most 10 with UNC proxy links, and he supplies them in `~/hest-1k/ppi_conf_papers/`.
- **L3. The ledger, the decisions and the briefs.** The ledger document, the decision on the estimator (question E) with the reading behind it, the recommendations on the coefficient rule (R7-6) and on prediction sets (question P), which are Nicolas's to decide, the writing plan, and the final-runs brief with predictions written first. A fresh agent checks the ledger and the final-runs brief before the gate.

## Outputs

`docs/round10/i01/ledger/round10_ledger.md` (the ledger), `docs/round10/i01/ledger/round10_ledger_decisions.md` (E, and the recommendations on R7-6 and P, with their reading), `docs/round10/tracks/ledger/round10_writing_plan.md`, `docs/round10/i01/final-runs/round10_final_runs_brief.md`, and the subagents' query logs in `results/round10/ledger/` through a pull request.

## Standards

Every citation carries an identifier that was opened, with its read level. Every number quoted is read back from its file and cited. No result is called the project's own without the checks of rounds 8 and 9 behind it, and no gap is called genuine without a logged search covering survey sampling as well as machine learning. The numeric-claim sweep runs on every document before the gate.

## Gate

L3. Nicolas reviews the ledger, the two decisions, the writing plan and the final-runs brief in the oversight chat and answers there. His answer is recorded in `docs/round10/i02/ledger/` before the final-runs track starts.

## Not this track's decision

D5, Q1 and V, which Nicolas settles with David when he chooses. R7-6, P, R7-7, R7-5, O5 and O3, on which the ledger recommends. The paper's framing and venue. Which theorems of round 9 the paper keeps. Any claim of novelty. Any contact outside the project. Any download of data, and whether the tasks extend to the federated project's corpus (masterplan question DATA, Nicolas's). Changes to earlier rounds' files. Details of the lab's unpublished manuscript never enter the repository (hard rule 8).
