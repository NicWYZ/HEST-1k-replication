# CLAUDE.md

**If you are an execution session** (a session working on a track branch), your rules are `docs/EXECUTION_RULES.md` and your goals are your track's brief and every gate decision recorded in your plan. This file is the oversight session's, so do not edit it or act on its plan. The hard rules below apply to you as well.

The project is Nicolas Weiyang Zhang's first-year biostatistics PhD project at UNC, in Dr. Hongtu Zhu's lab and supervised by Dr. Daiwei (David) Zhang, toward a submittable paper by spring 2027. The paper answers the proposal's two questions, calibrated uncertainty for histology-predicted gene expression and valid inference with it, on HEST-1k spatial transcriptomics with ACS PUMS 2018 income as a second domain. Existing or classical methods are applied wherever they serve, and the project's own method or theory arises only where a problem met in practice has no existing solution after a literature search (`docs/round10/00_prep/round10_reframing.md`, section 1). 

```state
updated: 2026-11-17 (oversight session; gate G2 of track closeout answered)
unit: round11
status: running
next: track closeout runs from docs/round11/closeout/round11_closeout_brief.md; the oversight session reviews its gates and relays summaries to Nicolas (docs/round11/masterplan.md, "Who decides the gates"); once G-final is merged, draft the advisor outline in docs/round11/oversight/ (docs/round11/masterplan.md).
branch round11-closeout: running | docs/round11/closeout/round11_closeout_plan.md
waiting: FRAMING | since 2026-11-16 | whether the paper is round 10's applied paper or one paper on the headline results of the closeout brief, section 3 (Nicolas with the advisors; default not decided, the outline presents both)
waiting: D5 | since 2026-10-26 | which scale the paper calls primary; both are in the numbers table (Nicolas with David; default report both)
waiting: O5 | since 2026-11-08 | which of round 9's three theorems the paper keeps (Nicolas; default candidates, not claimed)
waiting: Q1 | since 2026-10-09 | whether regime B can be bought on a spatial platform, and at what cost (Nicolas with the advisors; default no cost claim)
waiting: Q3 | since 2026-10-09 | venue and lead result, once the paper's content is known (Nicolas; default open)
waiting: PAPERS | since 2026-11-07 | paper full texts round 9's checkers saved outside the repository are not yet deleted (Nicolas; default left)
```

What the project has established is in `docs/round10/README.md`, with the paper's numbers in `results/round10/final_runs/F4/paper_numbers.csv` and a plan for a draft in `docs/round10/tracks/ledger/round10_writing_plan.md`. Round 11 tests the headline results against a stronger predictor, closes round 10's open threads and prepares the presentation to the advisors (`docs/round11/masterplan.md`).

## Session start

1. `git fetch origin --prune --tags`, then `python3 code/scripts/record_check.py`. Read every commit and branch it lists, the open pull requests, and the plan named on each live branch. Bring the state block up to date before any other work. Run the check again before every documentation commit.
2. A running track is read through its branch on `origin`, read only. Longleaf is reached through execution sessions or Nicolas.
3. Read `docs/README.md` the first time you need the record, then the last closed round's summary, the current round's `README.md` and `masterplan.md`, and only what the work in hand needs. For how something came to be, read `git log` on the file or the tag named in the round's index row.

Before stopping, or before a long or risky step, update the state block and commit. That is the handoff. There is no progress log: the commit that does the work updates the state block, and its message says what was found or decided and who decided it. A decision, rule or preference Nicolas states goes into the file it belongs in (a rule, the state block, a brief) in the same session.

## The oversight session's work

- **Rounds** are opened and closed through the `project-record` skill. A round's `README.md` is its summary once it closes, the authority on what the round established.
- **While a round runs,** Nicolas decides every gate, and the oversight session does not answer one for him or edit a running track's areas. A request to act on a track must come from him.
- **New rounds are filed by track,** `docs/round<NN>/<track>/` with the track's brief, plan, gate reports and notes. A brief names the plan's path there.

## Hard rules

These are not preferences. Breaking one invalidates the work.

1. **The gate rule** is in `docs/EXECUTION_RULES.md` section 2, its one copy.
2. **Every number is read back from its file before it is asserted,** and a derived value is recomputed before it is stated (`docs/WAYS_OF_WORKING.md`, "Quoting a number").
3. **Predictions are written before a run** and scored afterwards as held, partly held, refuted or not tested. A prediction is never edited once its run has started, and a results file is never edited.
4. **The tree holds what a session needs now, and git holds what happened.** Rules, state and summaries say what is true now. A report, survey or plan says what was found or intended on its date, and an error in one is corrected in place. A conclusion that later work overturned is settled in the round's summary. A document no later session would open is deleted once the summary carries what it held, and a tag keeps it. No list of corrections is kept.
5. **No claim of novelty** without a literature check covering survey sampling as well as machine learning, run by subagents continually while the work goes on, since the model tends to rediscover results from its training data (`docs/WAYS_OF_WORKING.md`, "Literature and novelty").
6. **Longleaf is where work runs.** A local run needs Nicolas to ask for that task, and is recorded in the plan before it runs.
7. **Contact with anyone outside the project** is Nicolas's decision, never a session's. There is none for now.
8. **Gated data, papers, transcripts and credentials never enter the repository,** which is public. Details of unpublished manuscripts by others (title, authors, methods, results) stay out of it too. The repository records that a check was made and its verdict, and the full check goes to the private folder named in `docs/environment.md`.
9. **Git.** No rebase, squash, amend or force-push. Other sessions' clones are read only, with `git --no-optional-locks`.

## Working rules (Nicolas's)

- **Aims.** Minimal biology by design. Expression is a signal to predict, calibrate and use for inference. His career goal is quantitative research in finance, so directions are judged by how well their skills transfer. He prefers ML venues (NeurIPS, ICML, AISTATS) or top statistics journals, wants the paper's scope broad and useful beyond spatial transcriptomics, and decides the venue once the paper's content is known. The project is also what he presents in his search for a summer 2027 internship, quantitative research first, then ML or AI roles, then data science or statistics.
- **Literature first.** Whenever the work meets a problem, the literature is searched first for the existing method or theory to apply, and the project devises its own only where that search finds a genuine gap, which Nicolas agrees to before a derivation starts. New method and theory arise from problems met in practice and are never the main goal.
- **Data.** Use as much of the existing data as possible, including the federated project's corpus on Longleaf, read only. Longleaf storage is not a constraint.
- **Autonomy.** A research session explores, derives and validates on its own, and reports to Nicolas only at significant results or roadblocks, which are where its plan puts its gates.
- **Literature reviews.** A detailed review is done by a research session with subagents, and the oversight session sets its scope. Papers a session cannot retrieve go to Nicolas as one list of at most 10, each linked through UNC's library proxy (`https://login.libproxy.lib.unc.edu/login?url=https://doi.org/<DOI>`) or to a free version, and he supplies them in `~/hest-1k/ppi_conf_papers/`.
- **Thoroughness** always comes first, over speed.
- **No time estimates.** Intervals, tracks and rounds carry no duration estimates.
- **Delegation.** Delegating parallel tasks to subagents is done when Nicolas asks for it for a particular task.

## Git route

The oversight session pushes documentation-only commits straight to `main`, pulling first. Documentation is this file, `README.md` and everything under `docs/` except a running track's areas. Code, results, `.verify-*` files and anything in a track's areas go through a pull request that Nicolas merges with a merge commit. A track tags and pushes at each gate and opens one pull request at its final gate (`docs/EXECUTION_RULES.md`, section 5). Commit messages go through a file and end with the attribution lines the session is given.

## Where things are

```
CLAUDE.md                   this file
README.md                   the public entry point, with the benchmark work of rounds 1 and 2
docs/README.md              the record's index, how the folders work, one row per closed round
docs/EXECUTION_RULES.md     the one standing document for execution sessions
docs/WAYS_OF_WORKING.md     procedures, each tied to the failure behind it
docs/environment.md         people, Longleaf trees and scheduler notes, data quirks, what a session needs
docs/reference/             material consulted across rounds
docs/roundNN/               one round: README.md (its summary), masterplan.md, 00_prep/, tracks
code/scripts/               every script, including record_check.py and verify_numeric_claims.py
results/, figures/          outputs by round
```
