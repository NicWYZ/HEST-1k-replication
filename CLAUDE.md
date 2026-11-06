# CLAUDE.md

**If you are an execution session** (Claude Science or Claude Code on a track branch), this file belongs to the oversight chat. Do not edit it and do not act on its plan. Your rules are `docs/EXECUTION_RULES.md`, and your work is your track's brief in `docs/roundNN/i01/<track>/`, the round's masterplan and your track's decision files. The copy of this file on your branch was frozen when the branch started and may be out of date. The hard rules below apply to you as well. **If you are the oversight chat,** this is your operating file, and keeping its state block true is part of every session.

The project is Nicolas Weiyang Zhang's first-year biostatistics PhD project at UNC, in Dr. Hongtu Zhu's lab and supervised by Dr. Daiwei (David) Zhang. The advisors want methods, not applied analysis, with a submittable paper by spring 2027. The paper in preparation is "Labelling budgets for prediction-powered inference with clustered data", methodology and theory first, applied to HEST-1k spatial transcriptomics and ACS PUMS 2018 income (`docs/round04/00_prep/round4_originality_check.md`). Two lines that started here now have their own repositories, the federated learning paper proposed by Dr. Zhu on 12 October (`NicWYZ/ST-Fed-Learn` since 26 October, after `docs/round07/00_prep/round07_advisor_directions.md`) and David's textual knowledge base (`NicWYZ/textual-st-histology` since 19 October).

```state
updated: 2026-11-06 (oversight chat, cloud session, Nicolas's account; record migrated to project-record)
unit: round10
status: waiting
next: Nicolas gives the new direction, then round 10 opens through /project-record with a literature survey first, starting from a problem met in practice (newtopic's lesson in docs/round09/README.md).
waiting: direction | since 2026-11-06 | the project's new direction, which opens round 10 (Nicolas)
waiting: instructions | since 2026-11-06 | paste the texts of docs/project_instructions.md into the claude.ai project and the Claude Science project (Nicolas)
waiting: Q3/D1 | since 2026-10-09 | venue and lead result; round 9's candidate is the three frontiers as theory, regime A against B as the design result (fewcluster closing report section 4); default open (Nicolas, likely with David and Dr. Zhu)
waiting: R8-1/D2 | since 2026-10-19 | whether prediction sets (HCP, GHCP, within_full) stay in the PPI paper; default the fewcluster draft defers them (Nicolas)
waiting: Williams | since 2026-10-27 | whether round 5's estimator is replaced by Williams' or the fold-wise form, [proposed] by round 9; default round 5's estimator as defined (Nicolas)
waiting: R7-6 | since 2026-10-14 | a global coefficient below six labelled clusters; round 9 found the fixed coefficient as good as any tuned form (docs/round09/i03/fewcluster/round09_fewcluster_williams.md); default round 5's rule (Nicolas)
waiting: D5 | since 2026-10-26 | whether earlier estimands on log1p of unnormalized counts are redefined; default keep them and say they partly measure depth (Nicolas, likely with David)
waiting: V | since 2026-10-27 | whether bounding each cluster's share of the design variance is defensible; default regime B's numbers stated under it beside the unbounded column (Nicolas, with David)
waiting: Q1 | since 2026-10-09 | can regime B be bought on a spatial platform, at what cost; not yet asked of David, and more pressing since regime B is round 9's main design result; default no cost claim (Nicolas, with David)
waiting: R7-5 | since 2026-10-14 | positioning against Broska and Howes's small-sample interval (docs/round07/i04/ppi/round07_ppi_final_decisions.md section 4), feeds O5; default round 7's positioning note keeps its banner (Nicolas, with David)
waiting: R7-7 | since 2026-10-15 | which balanced design the paper recommends (docs/round07/i04/ppi/round07_ppi_final_decisions.md section 4); default [proposed] rej_t where its support and one balance variable allow, the S4b cube design as the alternative (Nicolas, with David)
waiting: O5 | since 2026-10-13 | the paper's positioning (docs/round07/oversight/round07_ppi_positioning.md section 5 and round 8's note); default claim nothing marked prior art, classical or implied, nor the few-cluster regime in general (the banner of 15 October); round 9's theorems are candidates (Nicolas, with David)
waiting: O3 | since 2026-10-13 | how the PPI paper and the lab's manuscript refer to each other; default neither refers to the other (Nicolas, with David and Dr. Zhu)
waiting: tags | since 2026-10-09 | whether to tag round5-final (Q4) and the untagged gates of rounds 8 and 9; a cloud session cannot push tags; round6-close exists (Nicolas)
waiting: branches | since 2026-11-06 | whether to delete the 27 remote branches, all merged into main (Nicolas)
waiting: carried | since 2026-10-09 | when to schedule the carried tasks: delete the full texts round 9 saved to the Claude Science artifact store (decided 6 November), fix verify_numeric_claims.py for comma-grouped integers in CSV text cells (R7.6), the paper's writing plan (from the closing pages of rounds 4, 5, 7 and 9, the estimator definition and round 8's note, after Q3, R8-1 and the Williams decision), the next advisor presentation (see docs/round05/00_prep/deck2/), and housekeeping from rounds 3 to 5 (the D4 probe rerun, ten unresolved claims in two pre-round-3 documents, the r5c_leak_summary.csv reading in docs/round05/00_prep/round5_oversight_handoff.md section 12) (Nicolas)
```

**Where the PPI paper stands.** Round 8's positioning note (`docs/round08/i01/positioning/round08_positioning_note.md`) found every formula the paper would display classical or in print. Round 9's track fewcluster then proved three frontier theorems for finite-sample valid inference with few labelled clusters, not found in print, provisionally, and compared labelling whole clusters with a few units in every cluster under them. Its closing report (`docs/round09/i04/fewcluster/round09_fewcluster_closing_report.md`) and first draft (`docs/round09/tracks/fewcluster/paper_draft_v0.md`) are the latest account. Whether the tuned intervals of rounds 5 to 7 carry round 5's variance inflation is not checked. Round 9's track newtopic found no open direction outside clustered PPI and hierarchical conformal prediction. The round-7 documents `docs/round07/oversight/round07_ppi_results_explained.md` and `docs/round07/oversight/round07_ppi_positioning.md` are frozen and still call results the paper's own that round 8 withdrew. Round 5's estimator is `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`, and round 5's readings for the paper are section 3 of `docs/round05/i04/ppi/round5_ppi_E5_decisions.md` and `docs/round05/i03/conformal/round5_conformal_W5_decisions.md`.

**What the advisors have seen.** The second advisor meeting stopped at slide 8 (7 October), so they have seen the project up to the pivot and the originality check, not the results of rounds 4, 5, 7 or 9 (`docs/round05/i01/ppi/round5_ppi_track.md` section 2.1). The meeting of 12 October discussed round 6. Deck preparation is in `docs/round05/00_prep/deck2/`.

## Session start

1. `git fetch origin --prune --tags`, then `python3 code/scripts/record_check.py`. Read every commit and branch it lists, the open pull requests (`gh api repos/NicWYZ/HEST-1k-replication/pulls?state=open` where `gh pr list` is blocked), and the plan named on each live branch. Bring the state block up to date before any other work. Run the check again before every documentation commit.
2. Note where you run and on which account, and what that place can reach (`docs/environment.md`). A cloud session has only its own clone. A session linked to Nicolas's Mac reaches the clones under `~/hest-1k`. Longleaf is reached through execution sessions or Nicolas.
3. Read `docs/README.md` the first time you need the record, the current round's `README.md` and `masterplan.md`, then only what the work in hand needs. History is in `docs/progress-log.md`. Do not rely on memory or reconstruct history from summaries.

Before stopping, or before a long or risky step, update the state block and commit. That is the handoff. Bookkeeping goes in the commit that does the work. A decision, rule or preference Nicolas states goes into the repository in the same session, dated and in his terms. The oversight chat keeps each round's `README.md` (its gate table and, at the close, its summary), adding a track's gate rows when the track pushes a gate tag, since sessions do not edit outside their track's areas. Rounds are opened and closed through the `project-record` skill, whose close needs a fresh agent's check of the record (`docs/WAYS_OF_WORKING.md`, first section).

## Hard rules

These are not preferences. Breaking one invalidates the work.


1. **The gate rule** is in `docs/EXECUTION_RULES.md` section 2, its one copy.
2. **Every number is read back from its file before it is asserted,** and a derived value is recomputed before it is stated (`docs/WAYS_OF_WORKING.md`, "Quoting a number").
3. **Predictions are written before a run** and scored afterwards as held, partly held, refuted or not tested.
4. **Frozen documents are not edited.** Corrections go in the next document and the round's summary.
5. **No claim of novelty** without a literature check covering survey sampling as well as machine learning, run by subagents continually while the work goes on, since the model tends to rediscover results from its training data (24 October; `docs/round04/00_prep/round4_originality_check.md`, `docs/round05/00_prep/deck2/deck2_literature_check.md`, `docs/WAYS_OF_WORKING.md`).
6. **Longleaf is where work runs.** A local run needs Nicolas to ask for that task, and is recorded in the plan before it runs.
7. **Contact with anyone outside the project** is Nicolas's decision, never a session's. On 6 November he decided there is none for now.
8. **Gated data, papers, transcripts and credentials never enter the repository,** which is public. Details of unpublished manuscripts by others (title, authors, methods, results) stay out of it too. The repository records that a check was made and its verdict, and the full check goes to the claude.ai project docs (13 October).
9. **Git.** No rebase, squash, amend or force-push. Other sessions' clones are read only, with `git --no-optional-locks`.

## Working rules (Nicolas's)

- **Aims.** Minimal biology by design. Expression is a signal to predict, calibrate and use for inference. His career goal is quantitative research in finance, so directions are judged by how well their skills transfer. He prefers ML venues (NeurIPS, ICML, AISTATS) or top statistics journals, and wants the paper's scope broad and useful beyond spatial transcriptomics.
- **Compute.** Longleaf by default (hard rule 6). For agent experiments he prefers Claude Code to Claude Science unless Science has an obvious advantage, and a local session on his Mac, which can SSH into Longleaf, over a cloud session (11 and 12 October).
- **Autonomy and novelty** (24 October). A research session explores, derives and validates on its own, and reports to him only at significant results or roadblocks, which are where its plan puts its gates. The end goal is a statistics-forward methodological paper. Novelty checks run continually (hard rule 5).
- **Independent tracks** (26 October). Tracks run as independent sessions, each reporting only to him, neither overseen by nor reporting to another session.
- **Literature reviews** (13 October). A detailed review is done by a research session with sub-agents, and the oversight chat sets its scope. No new paper reads for now (6 November), so verdicts that rest on unread sources stay provisional. When reads resume, papers a session cannot retrieve go to him as one list of at most 10, each linked through UNC's library proxy (`https://login.libproxy.lib.unc.edu/login?url=https://doi.org/<DOI>`) or to a free version, and he supplies them in `~/hest-1k/ppi_conf_papers/`.
- **Agent experiments** (11 October). Every trial is a fresh agent with no context on the project, in its own sandbox, with trial counts small enough not to use up his tokens, run in parallel where that helps.

## Git route

The oversight chat pushes documentation-only commits straight to `main` (9 October), pulling first. Documentation is this file, `README.md` and everything under `docs/` except a running track's areas. Code, results, `.verify-*` files and anything in a track's areas go through a pull request that Nicolas merges with a merge commit. A track pushes its branch and gate tag at each gate and opens one pull request at its final gate (`docs/EXECUTION_RULES.md` section 5). Commit messages go through a file and end with the attribution lines the session is given.

## Where things are

```
CLAUDE.md                   this file
README.md                   the public entry point, with the benchmark work of rounds 1 and 2
docs/README.md              the record's index, how the folders work, one row per round
docs/progress-log.md        what happened and why, newest first
docs/EXECUTION_RULES.md     the one standing document for execution sessions
docs/WAYS_OF_WORKING.md     procedures, each tied to the failure behind it
docs/environment.md         machines, clones, accounts, Longleaf notes, data quirks
docs/project_instructions.md  the texts pasted into the two Claude projects
docs/roundNN/               one round, with README.md, masterplan.md, 00_prep/, iKK/<track>/, tracks/
code/scripts/               every script, including record_check.py and verify_numeric_claims.py
results/, figures/          outputs by round
```

`docs/environment.md` also says what a new account must recreate.
