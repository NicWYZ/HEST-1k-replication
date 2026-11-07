# CLAUDE.md

**If you are an execution session** (Claude Science or Claude Code on a track branch), this file belongs to the oversight chat. Do not edit it and do not act on its plan. Your rules are `docs/EXECUTION_RULES.md`, and your work is your track's brief in `docs/roundNN/i01/<track>/`, the round's masterplan and your track's decision files. The copy of this file on your branch was frozen when the branch started and may be out of date. The hard rules below apply to you as well. **If you are the oversight chat,** this is your operating file, and keeping its state block true is part of every session.

The project is Nicolas Weiyang Zhang's first-year biostatistics PhD project at UNC, in Dr. Hongtu Zhu's lab and supervised by Dr. Daiwei (David) Zhang, with a submittable paper by spring 2027. Through round 9 the paper in preparation was "Labelling budgets for prediction-powered inference with clustered data", methodology and theory first, applied to HEST-1k spatial transcriptomics and ACS PUMS 2018 income (`docs/round04/00_prep/round4_originality_check.md`), on the record that the advisors want methods, not applied analysis. On 6 November Nicolas reframed the objective (`docs/round10/00_prep/round10_reframing.md`, section 1, quoted verbatim there). The aim is to answer the proposal's two questions, calibrated uncertainty for histology-predicted expression and valid inference with it, applying existing or classical methods is acceptable for a first paper, and new theory arises only where a problem met in practice has no existing solution after a literature search. That document's reading of this as an applied statistics paper is `[proposed]`. On 6 November, later, Nicolas said the advisor line and his meeting with the advisors are not to be worried about now, so the line stands as a record and is not a pending decision. Two lines that started here now have their own repositories, the federated learning paper proposed by Dr. Zhu on 12 October (`NicWYZ/ST-Fed-Learn` since 26 October, after `docs/round07/00_prep/round07_advisor_directions.md`) and David's textual knowledge base (`NicWYZ/textual-st-histology` since 19 October).

```state
updated: 2026-11-07 (oversight chat, cloud session linked to the Mac, Nicolas's account; ledger L1 rows pushed, L2 reads next)
unit: round10
status: running
next: track ledger, stages L0 to L3 of docs/round10/i01/ledger/round10_ledger_brief.md, gate L3 at Nicolas's review in the oversight chat; then the final-runs brief goes to a Claude Science session on Longleaf.
live: ledger | oversight chat; branch round10-ledger for its logs only | docs/round10/masterplan.md | L1 rows written and pushed (results/round10/ledger/ on branch round10-ledger, commit b8bf9286, with the R7.6 checker fix); L2 reads next, open sources through the Mac's built-in browser or WebFetch, gated ones through Nicolas
waiting: Q3/D1 | since 2026-10-09 | venue and lead result; Nicolas said on 6 November the venue depends on what the paper ends up with; default open (Nicolas, after F4)
waiting: R8-1/D2 | since 2026-10-19 | whether prediction sets (HCP, GHCP, within_full) stay in the paper; Nicolas said on 6 November only if it makes sense; the ledger recommends at L3 (masterplan question P); default the fewcluster draft defers them (Nicolas)
waiting: Williams | since 2026-10-27 | whether round 5's estimator is replaced by Williams' or the fold-wise form; Nicolas said on 6 November the ledger decides after reading the sources (masterplan question E); default round 5's estimator as defined (the ledger)
waiting: R7-6 | since 2026-10-14 | a global coefficient below six labelled clusters; round 9 found the fixed coefficient as good as any tuned form (docs/round09/i03/fewcluster/round09_fewcluster_williams.md); default round 5's rule (Nicolas)
waiting: D5 | since 2026-10-26 | normalization of the estimands; Nicolas decided on 7 November that this is settled by testing, with the effect quantified, so the final runs carry both scales and the paper reports the difference (the final-runs track, at F2)
waiting: V | since 2026-10-27 | whether bounding each cluster's share of the design variance is defensible; Nicolas decided on 7 November that this is settled by the literature and by testing, not by one person's knowledge, so the ledger searches for it and the final runs test it (the ledger at L3, the final-runs track at F3)
waiting: Q1 | since 2026-10-09 | can regime B be bought on a spatial platform, at what cost; deferred by Nicolas on 7 November to the next advisor slide deck, at a time not yet set; default no cost claim (Nicolas, with the advisors)
waiting: R7-5 | since 2026-10-14 | positioning against Broska and Howes's small-sample interval (docs/round07/i04/ppi/round07_ppi_final_decisions.md section 4), feeds O5; default round 7's positioning note keeps its banner (Nicolas, with David)
waiting: R7-7 | since 2026-10-15 | which balanced design the paper recommends (docs/round07/i04/ppi/round07_ppi_final_decisions.md section 4); default [proposed] rej_t where its support and one balance variable allow, the S4b cube design as the alternative (Nicolas, with David)
waiting: O5 | since 2026-10-13 | the paper's positioning (docs/round07/oversight/round07_ppi_positioning.md section 5 and round 8's note); default claim nothing marked prior art, classical or implied, nor the few-cluster regime in general (the banner of 15 October); round 9's theorems are candidates (Nicolas, with David)
waiting: carried | since 2026-10-09 | scheduled by the oversight chat on 7 November at Nicolas's request: the full texts round 9 saved to the Claude Science artifact store are deleted by the final-runs session at its start (in its brief); the verify_numeric_claims.py fix for comma-grouped integers (R7.6) goes on branch round10-ledger with the ledger's pull request; the next advisor presentation and Q1 go to track paper after F4; the D4 probe rerun, the ten unresolved claims in two pre-round-3 documents and the r5c_leak_summary.csv reading are closed without action, superseded by round 10's rerun and the frozen status of those documents (recorded in docs/round10/masterplan.md, amendments)
```

**Where the paper stands after the reframing.** `docs/round10/00_prep/round10_findings_survey.md` lists what nine rounds established, by the question each finding answers and with a status label, the seventeen claims held as the project's own and later found in print, and the applied paper the findings support (its section 4.2). `docs/round10/00_prep/round10_reframing.md` says what the paper still lacks (a final rerun with the corrected estimator, D5, Q1, a methods ledger, the cited sources read) and proposed round 10 as tracks `ledger`, `final-runs` and `paper`, which Nicolas opened on 6 November on that structure (`docs/round10/masterplan.md`). The paragraph below is the methods-first account through round 9 and stays as its record.

**Where the PPI paper stood through round 9.** Round 8's positioning note (`docs/round08/i01/positioning/round08_positioning_note.md`) found every formula the paper would display classical or in print. Round 9's track fewcluster then proved three frontier theorems for finite-sample valid inference with few labelled clusters, not found in print, provisionally, and compared labelling whole clusters with a few units in every cluster under them. Its closing report (`docs/round09/i04/fewcluster/round09_fewcluster_closing_report.md`) and first draft (`docs/round09/tracks/fewcluster/paper_draft_v0.md`) are the latest account. Whether the tuned intervals of rounds 5 to 7 carry round 5's variance inflation was not checked by a run; the ledger's code reading of 7 November (section 0 of the S4 rows on branch round10-ledger, confirmed by the oversight chat against the scripts) finds that they do not, because round 9's `R5` arm omits the linearisation term those intervals carry, and the final runs confirm it by rerunning round 9's comparison with that term. Round 9's track newtopic found no open direction outside clustered PPI and hierarchical conformal prediction. The round-7 documents `docs/round07/oversight/round07_ppi_results_explained.md` and `docs/round07/oversight/round07_ppi_positioning.md` are frozen and still call results the paper's own that round 8 withdrew. Round 5's estimator is `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`, and round 5's readings for the paper are section 3 of `docs/round05/i04/ppi/round5_ppi_E5_decisions.md` and `docs/round05/i03/conformal/round5_conformal_W5_decisions.md`.

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

- **Aims.** Minimal biology by design. Expression is a signal to predict, calibrate and use for inference. His career goal is quantitative research in finance, so directions are judged by how well their skills transfer. He prefers ML venues (NeurIPS, ICML, AISTATS) or top statistics journals, and wants the paper's scope broad and useful beyond spatial transcriptomics. The venue depends on what the paper ends up with (6 November).
- **Data** (7 November). Use as much of the existing data as possible. Round 10 reads the federated project's corpus on Longleaf, read only, with no new download.
- **Compute.** Longleaf by default (hard rule 6). From 6 November, Longleaf sessions run on Nicolas's seat on David's team account, which he says changes nothing in how the project is set up. Which kind of session runs a track (Claude Science, local or cloud Claude Code) he decides case by case; his earlier preference for Claude Code and local sessions (11 and 12 October) is withdrawn from the record at his request (6 November). Round 10's final runs are a Claude Science session on Longleaf.
- **Autonomy and novelty** (24 October). A research session explores, derives and validates on its own, and reports to him only at significant results or roadblocks, which are where its plan puts its gates. Novelty checks run continually (hard rule 5). The sentence of 24 October that the end goal is a statistics-forward methodological paper is superseded by the reframing of 6 November, and in round 10 a derivation starts only after Nicolas has seen the literature search and agreed the gap is genuine, as the structure he opened the round on says.
- **Literature first** (6 November, `docs/round10/00_prep/round10_reframing.md`, section 1). The aim is to answer the proposal's questions on the project's data, and applying existing or classical methods and theory is acceptable for a first paper. Whenever the work meets a problem, the literature is searched first for the existing method or theory to apply, before any analysis, and the project devises its own method or derives its own theory only where that search finds a genuine gap. New method and theory arise from problems met in practice and are never the main goal.
- **Independent tracks** (26 October). Tracks run as independent sessions, each reporting only to him, neither overseen by nor reporting to another session. Round 10's ledger track runs inside the oversight chat by his decision of 6 November.
- **Literature reviews** (13 October). A detailed review is done by a research session with sub-agents, and the oversight chat sets its scope. The decision of 6 November that there were no new paper reads applied only to closing round 9, before the reframing (Nicolas, 6 November, later); reads resume with round 10, and verdicts that rest on unread sources stay provisional until then. Round 10's methods ledger is built by the oversight chat with Opus subagents (6 November), a departure from this rule that he decided. Papers a session cannot retrieve go to him as one list of at most 10, each linked through UNC's library proxy (`https://login.libproxy.lib.unc.edu/login?url=https://doi.org/<DOI>`) or to a free version, and he supplies them in `~/hest-1k/ppi_conf_papers/`.
- **Delegation** (6 November). Delegating parallel tasks to Opus subagents is not a standing rule; Nicolas asks for it for particular tasks, as he did for the survey of 6 November.
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
