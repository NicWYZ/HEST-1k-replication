# CLAUDE.md

**Read this paragraph first, whoever you are.** This repository is worked on by two kinds of session. If you are an **execution session** (a Claude Science or Claude Code session on a track branch such as `round7-fedlearn`), your instructions are your track's instruction document in `docs/roundNN/i01/<track>/`, the operating plan you transcribed from it, and every decision memo since. This file belongs to the oversight chat. Do not edit it and do not act on its plan. The copy on your branch was frozen when the branch started and may be out of date. Section 7's rules apply to you as well. If you are the **oversight chat**, this is your operating file. It replaces the oversight handoff documents, and keeping it current is part of your job.

**Last updated:** 2026-10-13, evening (oversight, cloud session linked to Nicolas's Mac; O2 accepted, the ppi track's instruction written, both round-7 tracks ready to start)

The project is Nicolas Weiyang Zhang's first-year biostatistics PhD project at UNC, in Dr. Hongtu Zhu's lab and supervised by Dr. Daiwei (David) Zhang. The advisors want methods, not applied analysis, with a submittable paper by spring 2027. The paper is "Labelling budgets for prediction-powered inference with clustered data", methodology and theory first, applied to HEST-1k spatial transcriptomics and ACS PUMS 2018 income (`docs/round04/00_prep/round4_originality_check.md`). Since the advisor meeting of 12 October there is a second line of work, a preliminary, proof-of-concept methods paper on federated learning for predicting expression from histology, proposed by Dr. Zhu (`docs/round07/00_prep/round07_advisor_directions.md`).

## 1. Session protocol (oversight)

**At the start of a session**

1. Clone or fetch `NicWYZ/HEST-1k-replication` and read this file in full.
2. Check for staleness before trusting section 2. Run `git fetch origin --tags`, then `python3 code/scripts/state_check.py --standing-dirs reference superseded`, and list the open pull requests (`gh api repos/NicWYZ/HEST-1k-replication/pulls?state=open`). If the script is not on `main` yet, run `git log --oneline --first-parent $(git log -1 --format=%h origin/main -- CLAUDE.md)..origin/main` instead. Read every commit, tag or report after the last change to this file, and correct section 2 first.
3. Note where you are running. A **cloud session** has the repository clone you make, no Longleaf and no data. When the session is **linked to Nicolas's Mac**, the clones under `~/hest-1k` are reachable (section 10). Only oversight sessions in the claude.ai project can be linked. Claude Code cloud sessions cannot. Longleaf is reached only through execution sessions or through Nicolas.
4. Read `docs/README.md`, the current round's `README.md` and `masterplan.md`, and the documents section 2 names for the work in hand. For history, read `docs/progress-log.md` and follow it to the files. Do not rely on memory or reconstruct history from summaries.

**At every gate**

1. Review the report against the files. Read the whole grid, recompute the key numbers, and use an independent checker agent for high-stakes memos. Read the session's flagged points first.
2. Write the memo to the track's next interval folder on `main` (`docs/roundNN/iKK/<track>/`), including after the track's last gate, when the closing memo sits there alone. The memo tells the track the exact paths for its next files.
3. When the gate's pull request merges, confirm the report and plan arrived where the instruction said.
4. In the same commit as the memo, or the first commit after the merge, add the rows to the round's `README.md` (gate table and documents table), add a dated entry to `docs/progress-log.md`, and update sections 2 and 5 here. A memo is not finished until this is done. The same holds for an instruction document.
5. Run the state check before committing.

**When the last gate of a round has merged,** invoke `/project-state-keeping` to close the round. The round is not closed, and the next one does not open, until its close check passes. Opening a round also goes through that skill, which writes the masterplan.

**During a session.** Write your steps into section 5 before starting them. After a context compaction, re-read sections 2 and 5. Before a long or risky step, or when the conversation is long, refresh section 2 so a fresh session could resume from it alone, and bump "Last updated". When Nicolas states a preference or a rule, record it in section 6 or 7 with the date, in his terms, in the same turn. When in doubt, update. A stale file costs more than an extra commit.

**How updates reach `main`.** The oversight chat pushes documentation-only commits straight to `main` (Nicolas, 9 October 2026). Documentation means this file, `README.md` and everything under `docs/` except a running track's own areas. Code, results, `.verify-*` files and anything in a running track's areas go through a pull request that Nicolas merges. Pull before committing, and never force-push.

## 2. Current state (13 October 2026)

- **Round 7 is open** (`docs/round07/README.md`, `docs/round07/masterplan.md`). One track is opened, `fedlearn`, a literature review of the viability of federated learning for predicting expression from histology, with quick scoping experiments, run by a Claude Science session with sub-agents on branch `round7-fedlearn`. Its instruction is `docs/round07/i01/fedlearn/round07_fedlearn_track.md`, living on `main`. No session is running yet. Gates are F2 (about Friday 16 October) and F4 (about Wednesday 21 October). During F1 the session sends Nicolas one list of at most 10 papers it cannot retrieve, with UNC proxy or free links, and he uploads them to `~/hest-1k/fedlearn_papers/`.
- **The PPI paper, track `ppi`.** The overlap check (`docs/round07/00_prep/round07_overlap_check.md`, public, and `claude/round07_overlap_check_full.md` in the private claude.ai project docs) and the positioning note (`docs/round07/oversight/round07_ppi_positioning.md`) moved the paper's own ground to the few-cluster, design-target regime and the design questions, since Broska and Howes (arXiv:2610.09601) hold the large-sample interval and their formula implies the gain theorem's endpoint. Nicolas accepted O2 with the note's three changes on 13 October. The track's instruction is `docs/round07/i01/ppi/round07_ppi_track.md`, living on `main`, branch `round7-ppi`, stages S0 to S5 with gates S2, S4 and S5. No session is running yet.
- **Next action.** Nicolas starts the two Claude Science sessions, fedlearn from a new clone (its instruction, section 12) and ppi from the reused PPI clone after a fetch (its instruction, section 11). The oversight chat waits for the F2 and S2 reports.
- **The PPI paper's record.** Round 5 closed on 9 October and everything is on `main` (pull requests #14 to #22). What goes into the paper is in section 3 of the two closing memos, `docs/round05/i04/ppi/round5_ppi_E5_decisions.md` and `docs/round05/i03/conformal/round5_conformal_W5_decisions.md`. The paper's estimator is `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`. The explainer of round 5's results is `docs/round06/00_prep/round06_round5_results_explained.md`.
- **Round 6** is closed, including its extension (`docs/round06/README.md`). Pull request #26 merged, and the extension's plan was marked frozen on 13 October.
- **What the advisors have seen.** Nicolas reported on 7 October that the second advisor meeting stopped at slide 8, so the advisors have seen the project up to the pivot and the originality check and not the round-4 or round-5 results (`docs/round05/i01/ppi/round5_ppi_track.md` section 2.1). The deck preparation is in `docs/round05/00_prep/deck2/`. The meeting of 12 October discussed round 6's experiments.
- **Carried housekeeping from earlier rounds,** not urgent. The D4 probe rerun, the ten unresolved claims in two pre-round-3 documents, and the `r5c_leak_summary.csv` reading (`docs/round05/00_prep/round5_oversight_handoff.md` section 12).

**Open questions.** Each waits on the person named. The default holds until it is decided.

| # | Question | Who decides | Default |
|---|---|---|---|
| Q1 | Can regime B (a few labelled spots on every donor) be bought on a spatial platform, and at what cost? Not yet asked of David | Nicolas, with David | the paper treats regime B as a design comparison, with no cost claim |
| Q2 | Should the GHCP authors be contacted? | Nicolas, with his advisors, never a session | no contact |
| Q3 | Which venue, and which result does the paper lead with? Not yet raised | Nicolas, with his advisors | open |
| Q4 | Tag `round5-final` on `main` at round 5's close `[proposed]`. `round6-close` exists | Nicolas | no tag |
| R6-3 | Whether and when round 6's two summaries go to David | Nicolas, never a session | nothing is sent |
| R7-1 | Any download of further HEST-1k slides or other public data for the fedlearn experiments | Nicolas, at the F2 gate | none, the experiments use what is on Longleaf |
| R7-2 | How the federated learning paper is framed relative to David's textual knowledge base | Nicolas, with David and Dr. Zhu | the review compares the routes on evidence and takes no side |
| R7-3 | Venue and authorship of the federated learning paper | Nicolas, with his advisors | open |
| O3 | How the PPI paper and the lab's manuscript refer to each other | Nicolas, with David and Dr. Zhu | neither refers to the other |
| O5 | The PPI paper's positioning, as in `docs/round07/oversight/round07_ppi_positioning.md`, section 5 | Nicolas, with David | the paper claims nothing that note marks as prior art, classical or implied |

## 3. Where the record is

`docs/` is filed in time order by round, interval and track, and `docs/README.md` explains the layout and lists every round. Each round's `README.md` lists its gates and documents and, once closed, what it established. `docs/moved.md` maps every pre-migration path to its new one. Files under `results/` and comments in older scripts still carry the old paths.

## 4. Done

- **Rounds 1 to 4** (12 September to 4 October). Replication, instrumentation, the two pivots, round 4's tracks and the second deck's preparation. Summaries in `docs/round01/README.md` to `docs/round04/README.md`. The handoffs `docs/round03/00_prep/round3_oversight_handoff.md`, `docs/round04/oversight/round4_oversight_handoff.md` and `docs/round05/00_prep/round5_oversight_handoff.md` are the full history up to 4 October.
- **Round 5** (7 to 9 October). Instructions for two tracks, five gate memos, the move from handoffs to this file, and the round's close. Summary in `docs/round05/README.md`, and each step has an entry in `docs/progress-log.md`.
- **Between rounds 5 and 6** (9 to 11 October). `docs/` moved to the layout by round, interval and track (pull request #22), and round 5's results were explained for Nicolas.
- **Round 6** (11 to 13 October). David's cheatsheet experiment, one track in a Claude Code cloud session with two gates, then an extension on held-out CCRCC patients in a local session on the Mac with two more gates, and the close. Summary in `docs/round06/README.md`, and each step has an entry in the progress log.

## 5. Oversight steps

- [x] **R7.0 Open round 7.** 13 October, cloud session linked to the Mac, commit `3c328ccc` on `main`. Three `.verify-exceptions` lines for the overlap check's external values merged as pull request #27. Recorded the advisor meeting, wrote the overlap check (public and private versions), the masterplan, the round's reading guide and the fedlearn instruction, and marked round 6's extension plan frozen. An independent agent checked the five round-7 files and found 15 problems, all fixed before commit. The largest were that the federated and pooled fits are equal only for an exact solver, that the inventory job needed delivered code, and that the public overlap check still described the unpublished manuscript.
- [x] **R7.1 PPI positioning note.** 13 October, cloud session linked to the Mac. Read Broska and Howes and Chen et al. in full and Kluger et al.'s cluster parts, from PDFs Nicolas put in `~/hest-1k/ppi_conf_papers/`, and wrote `docs/round07/oversight/round07_ppi_positioning.md`. An independent agent re-derived its section 2.2 and found 14 other problems, all fixed. Three values from Broska and Howes need `.verify-exceptions` lines on branch `oversight-round7-positioning-exceptions`, which waits for a pull request. O2 waits on Nicolas.
- [ ] **R7.2 F2 memo** for fedlearn, in `docs/round07/i02/fedlearn/round07_fedlearn_F2_decisions.md`, fixing interval 2's experiments and R7-1.
- [ ] **R7.3 F4 closing memo** for fedlearn, in `docs/round07/i03/fedlearn/`.
- [x] **R7.4 PPI instruction.** 13 October, cloud session linked to the Mac. Nicolas accepted O2 with the positioning note's changes. Wrote `docs/round07/i01/ppi/round07_ppi_track.md` with a masterplan amendment, checked by an independent agent (17 findings, all worked in, the largest that k-center gives every cluster a positive inclusion probability but most pairs none), and added the shared-queue rule to the fedlearn instruction.
- [ ] **R7.5 S2 memo** for ppi, in `docs/round07/i02/ppi/round07_ppi_S2_decisions.md`.
- [ ] **Carried. The paper,** a writing plan from the closing pages of rounds 4 and 5, the two round-5 closing memos, the estimator definition and the positioning note.
- [ ] **Carried. The next advisor presentation,** from the literature landscape and the two original topics through the pivot, the originality check and the results of rounds 4 and 5. Read `docs/round05/00_prep/deck2/` and the presentation preferences in section 6 first. Round 6's two summaries are ready as a short item.

## 6. Working preferences (Nicolas's)

- **Writing.** Plain, natural prose. No em-dashes. No sentence that states something, then a colon, then the explanation. No compressed or clever phrasing. Do not inflate length (by 4 October).
- **Math.** Rendered LaTeX, each `$$` on its own line. In a derivation, show every expression that carries the argument and skip only the algebra between displayed lines, with a sentence saying what kind of step was skipped. Never describe a derivation in words in place of its formulas (by 4 October). When he asks how something works, derive it slowly and step by step.
- **Numbers.** At the precision the comparison needs, with the relative scale stated. Full precision stays in files.
- **Documents for execution sessions.** Memos and instructions are complete standalone documents, never diffs. From round 6 an instruction and the masterplan stay living on `main` while the track runs. The oversight chat revises them in place with a dated line in their revision list, and Nicolas tells the session to check for updates instead of pasting text (11 October). Execution sessions do not reconstruct or revise past working documents that have served their purpose.
- **Deliveries.** One file per deliverable, with a fixed name. Overwrite it in place and say what changed (by 4 October).
- **Decisions.** He makes the decisions at his level and wants to be told which need David or Dr. Zhu. He reads every command before it runs and asks why.
- **Slides.** Speaker notes cover only what is on the slide. For advisor decks, no workflow or round language, formulas on the slide when theory is discussed, and every slide says why the step was taken (by 4 October).
- **Aims.** Minimal biology by design. Expression is a signal to predict, calibrate and use for inference. Career goal is quantitative research in finance, so directions are judged by how well their skills transfer. Prefers ML venues (NeurIPS, ICML, AISTATS) or top statistics journals. Wants the paper's scope broad and useful beyond spatial transcriptomics.
- **Project state.** No more oversight handoff documents. State lives in this file, which points to `docs/README.md` for history (9 October). `docs/` is filed chronologically by round, interval and track, with the round's masterplan at the round level. Within a round, memos, gate reports and the reading guides are added as the work goes, and this file is updated at every gate. At each round's close a consistency and currency check between this file and `docs/` is mandatory (9 October).
- **Compute.** Longleaf by default. In round 5 he allowed the tracks' simulations to run on his Mac where that is genuinely faster, until he says stop (8 October, `docs/round05/tracks/ppi/round5_ppi_plan.md` extension 4).
- **Delegation.** For tedious mechanical work he asked for subagents on a smaller model at medium effort (9 October, the path rewrite of the migration).
- **Unpublished work of others.** The details of an unpublished manuscript (its title, authors, methods and results) stay out of the public repository. The repository records that it was checked and the verdict, and the full check goes to the private claude.ai project docs (13 October).
- **Literature reviews by execution sessions.** For the federated learning line, the detailed review is done by a Claude Science session with sub-agents, and the oversight chat sets the scope and writes the instructions. Papers the session cannot retrieve go to Nicolas as one list of at most 10, each with a link through UNC Chapel Hill's library proxy, or to a free version where UNC's access is not available, and he uploads them (13 October).
- **Agent experiments.** Every trial is a fresh agent with no context on the project, in its own sandbox. Use Claude Code rather than Claude Science unless Science has an obvious advantage. Keep trial counts small enough not to use up his tokens, and run in parallel where it speeds things up (11 October). For round 6's extension he chose a local Claude Code session on his Mac, which can SSH into Longleaf and avoids a cloud session's constraints, over a cloud session or Claude Science (12 October).

## 7. Hard rules

These are not preferences. Breaking one invalidates the work. The procedures behind them, each tied to the failure that produced it, are in `docs/WAYS_OF_WORKING.md`.

1. **The gate rule, verbatim in every memo to an execution session.** "Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision."
2. **Every number is read back from its file before it is asserted,** and a derived value (a sum, a ratio) is recomputed before it is declared.
3. **Predictions are written before the run** and scored afterwards as held, partly held, refuted or not tested.
4. **Frozen reports are not edited.** Corrections go in the next memo or report. The one exception so far is the path rewrite of 9 October, which changed only paths, by Nicolas's decision.
5. **Git.** Execution tracks push once per gate, the branch and the tag together, with one pull request that Nicolas merges with a merge commit after review. No rebase, squash, amend or force-push. Commits reach Longleaf as bundles and jobs run from read-only snapshots (`docs/round05/i02/ppi/round5_ppi_E2_decisions.md` section 4). Round 6's track works in a cloud session that can be reclaimed, so it pushes its branch after every batch, with still one pull request per gate. Nicolas pulls its branch on Longleaf for its one job, which runs from a `git archive` copy (`docs/round06/i01/cheatsheet/round06_cheatsheet_track.md` section 5).
6. **Other sessions' clones are read only,** with `git --no-optional-locks`. Never write there.
7. **Longleaf is where work runs.** A local run needs Nicolas to ask for that task in chat and is recorded in the plan before it runs. Round 6's agent trials and analysis ran in a cloud session's container instead, by his decision of 11 October, and the extension's run on his Mac, including data preparation and comparators, by his decisions of 12 October.
8. **No claim of novelty** without a literature check (`docs/round04/00_prep/round4_originality_check.md`, `docs/round05/00_prep/deck2/deck2_literature_check.md`).
9. **Contact with anyone outside the project** is Nicolas's decision, never a session's.

## 8. Delegation

Independent, checkable jobs go to subagents, several at once when they do not depend on each other, such as searches, extracting numbers from reports, recomputing a headline, numeric-claim sweeps and mechanical rewrites. Mechanical jobs run one model tier below the oversight chat's model, at medium effort unless Nicolas says otherwise. Independent checks of high-stakes memos and the round-close consistency check run at the oversight chat's own tier, by a fresh agent that has not seen the drafting. Decisions, memos, instructions, edits to this file and commits stay with the oversight chat. Workers never commit or push, and their output is read against the files before it is used.

## 9. Conventions

- **Filing.** Every document has one place by round, interval and track (`docs/README.md`, "How the folders work"). A gate memo goes in the interval it opens. New file names carry the full prefix (`round06_ppi_E2_report.md`), so every name is unique.
- **The document chain.** The oversight chat writes an instruction or a decision memo. The execution session transcribes it into its operating plan in `tracks/<track>/`, flags what looks wrong without changing it, and writes a gate report into its interval folder. The next memo answers the report.
- **Memos.** Each memo opens with what was read and checked, restates the gate rule, then gives acceptance, what was checked, readings for the paper, the next interval with predictions, and answers to every escalation. The oversight chat writes each memo to `main` when Nicolas hands it over, and the track commits the same file unchanged, which merges cleanly. Copies in the claude.ai project docs are for convenience only.
- **Naming.** Tracks and stages are named per round (`round5_ppi_*`, stages E0 to E5; `round5_conf_*`, stages W0 to W5; `round06_cheatsheet_*` documents and `round6_cheatsheet_*.py` scripts, stages C0 to C7; `round07_fedlearn_*` documents and `round7_fedlearn_*.py` scripts, stages F0 to F4). Tags mark each gate (`round5-ppi-E2`, `round6-cheatsheet-C1`, `round7-fedlearn-F2`).
- **Numeric-claim sweep.** `code/scripts/verify_numeric_claims.py`, run as `docs/WAYS_OF_WORKING.md` shows, with each track's exceptions in its own `.verify-exceptions-<track>` file. The oversight chat sweeps `README.md`.
- **Tags.** `[proposed]` marks what the oversight chat proposed and Nicolas has not accepted. `[verify]` marks a statement written from memory.
- **Before every documentation commit,** run the state check (section 1).

## 10. Where things are

```
CLAUDE.md                 this file, with protocol, state, preferences and rules
README.md                 the repository's public entry point, status through round 6
docs/README.md            the reading guide, with the layout and one row per round
docs/progress-log.md      what happened and why, newest first
docs/WAYS_OF_WORKING.md   procedures, each tied to the failure that produced it, and the guardrails register
docs/moved.md             old path to new path, from the move of 9 October
docs/reference/           methods derived from scratch, concepts explained
docs/superseded/          two working documents a later one replaced, each bannered
docs/roundNN/             one round, with README.md, masterplan.md, 00_prep/, iKK/<track>/, tracks/, oversight/
code/scripts/             every script, including state_check.py; results/ the outputs by round; figures/ the figures
superseded/               a superseded manifest
```

On Nicolas's Mac, `~/hest-1k` holds `HEST-1k-replication-oversight` (the oversight clone, on `main`), `HEST-1k-replication-PPI` and `HEST-1k-replication-conformal` (the tracks' clones, read only), and `acs_pums2018` (the raw census fetch, not in the repository). Round 7's ppi track reuses `~/hest-1k/HEST-1k-replication-PPI` on branch `round7-ppi`, with its Longleaf code clone at `/work/users/w/e/weiyang/hest_code/round7-ppi/`. On Longleaf, the project tree `/work/users/w/e/weiyang/hest_replication` is on `main` at tag `round4-data-v2`, and the tracks' code clones are under `/work/users/w/e/weiyang/hest_code/`. Round 6's data package and transcripts live in the private repository `NicWYZ/hest-r6-data`, never in this public one. The extension's session clone is `~/hest-1k/HEST-1k-replication-cheatsheet`, its package and token sit in `~/hest-1k/r6ext_private/` and its trial folders in `~/hest-1k/r6ext_trials/`, all on the Mac. Its transcripts go to `NicWYZ/hest-r6-data` under `transcripts/ext/`. Round 7's fedlearn track uses a new clone, `~/hest-1k/HEST-1k-replication-fedlearn`, papers go to `~/hest-1k/fedlearn_papers/` and are never committed, and its Longleaf code clone is `/work/users/w/e/weiyang/hest_code/round7-fedlearn/`. The private version of round 7's overlap check is `claude/round07_overlap_check_full.md` in the claude.ai project docs.

## 11. Environment and git

- **People.** Nicolas (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`). Dr. Hongtu Zhu, the PI. Dr. Daiwei (David) Zhang, his GRA supervisor.
- **Sessions.** Execution sessions run on Longleaf, or as Claude Code cloud sessions as in round 6. They take no scope decisions and report at gates. The oversight chat writes instructions and memos, reviews reports against the files, explains, researches and steers.
- **Git from the cloud.** Clone over HTTPS, with the repository attached with push access. Pushing to `main` needs only the documentation rule of section 1. Pull requests cannot be opened from here with `gh pr create`, so tell Nicolas when one is needed.
- **On the Mac.** A plain `git status` on the mounted folder can leave `.git/index.lock` behind and block the next commit there. The device shell cannot delete files without Nicolas's permission. Commit and push from the cloud clone.
- **Commit messages** go through a file, and end with the attribution lines the session is given.
