# CLAUDE.md

**Read this paragraph first, whoever you are.** This repository is worked on by two kinds of session. If you are an **execution session** (a Claude Science session on a track branch such as `round5-ppi`), your instructions are your track's instruction document in `docs/roundNN/i01/<track>/`, the operating plan you transcribed from it, and every decision memo since. This file belongs to the oversight chat. Do not edit it and do not act on its plan. The copy on your branch was frozen when the branch started and may be out of date. Section 7's rules apply to you as well. If you are the **oversight chat**, this is your operating file. It replaces the oversight handoff documents, and keeping it current is part of your job.

**Last updated:** 2026-10-09 (oversight, cloud session; `docs/` moved to the layout by round, interval and track on branch `docs-migration`, this file restructured to match)

The project is Nicolas Weiyang Zhang's first-year biostatistics PhD project at UNC, in Dr. Hongtu Zhu's lab and supervised by Dr. Daiwei (David) Zhang. The advisors want methods, not applied analysis, with a submittable paper by spring 2027. The paper is "Labelling budgets for prediction-powered inference with clustered data", methodology and theory first, applied to HEST-1k spatial transcriptomics and ACS PUMS 2018 income (`docs/round04/00_prep/round4_originality_check.md`).

## 1. Session protocol (oversight)

**At the start of a session**

1. Clone or fetch `NicWYZ/HEST-1k-replication` and read this file in full.
2. Check for staleness before trusting section 2. Run `git fetch origin --tags`, then `python3 code/scripts/state_check.py --standing-dirs reference superseded`, and list the open pull requests (`gh api repos/NicWYZ/HEST-1k-replication/pulls?state=open`). If the script is not on `main` yet, run `git log --oneline --first-parent $(git log -1 --format=%h origin/main -- CLAUDE.md)..origin/main` instead. Read every commit, tag or report after the last change to this file, and correct section 2 first.
3. Note where you are running. A **cloud session** has the repository clone you make, no Longleaf and no data. When the session is **linked to Nicolas's Mac**, the clones under `~/hest-1k` are reachable (section 10). Longleaf is reached only through execution sessions.
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

## 2. Current state (9 October 2026)

- **Between rounds.** Round 5 is closed (`docs/round05/README.md`). Both tracks finished and everything is on `main` (pull requests #14 to #20). No execution session is running and nothing is running on Longleaf for this project. What goes into the paper is in section 3 of the two closing memos, `docs/round05/i04/ppi/round5_ppi_E5_decisions.md` and `docs/round05/i03/conformal/round5_conformal_W5_decisions.md`, and on the closing pages of the final reports of rounds 4 and 5. The paper's estimator is `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`, with its allocation sentence settled by the E5 memo's section 2.
- **Waiting on Nicolas's merge.** Branch `docs-migration` moves `docs/` into the layout by round, interval and track, rewrites the paths inside every document to match, adds a reading guide and a plan note to each round, and installs `code/scripts/state_check.py`. It needs a pull request that Nicolas opens and merges. Until it merges, `main` still has the flat layout.
- **Next action.** Ask Nicolas what comes next. The candidates are the next advisor presentation, a writing plan for the paper, and a next round (section 5). The first methods question for a next round is weighting the labelled clusters by their inclusion probabilities under rejective selection (`docs/round05/i04/ppi/round5_ppi_E5_decisions.md` section 5). Whether a next round runs, and with what scope, is Nicolas's. Anything written before round 6 opens goes in `docs/round06/00_prep/`.
- **What the advisors have seen.** Nicolas reported on 7 October that the second advisor meeting stopped at slide 8, so the advisors have seen the project up to the pivot and the originality check and not the round-4 or round-5 results (`docs/round05/i01/ppi/round5_ppi_track.md` section 2.1). The deck preparation is in `docs/round05/00_prep/deck2/`.
- **Carried housekeeping from earlier rounds,** not urgent. The D4 probe rerun, the ten unresolved claims in two pre-round-3 documents, and the `r5c_leak_summary.csv` reading (`docs/round05/00_prep/round5_oversight_handoff.md` section 12).

**Open questions.** Each waits on the person named. The default holds until it is decided.

| # | Question | Who decides | Default |
|---|---|---|---|
| Q1 | Can regime B (a few labelled spots on every donor) be bought on a spatial platform, and at what cost? Not yet asked of David | Nicolas, with David | the paper treats regime B as a design comparison, with no cost claim |
| Q2 | Should the GHCP authors be contacted? | Nicolas, with his advisors, never a session | no contact |
| Q3 | Which venue, and which result does the paper lead with? Not yet raised | Nicolas, with his advisors | open |
| Q4 | Tag `round5-final` on `main` at the round's close `[proposed]` | Nicolas | no tag |

## 3. Where the record is

`docs/` is filed in time order by round, interval and track, and `docs/README.md` explains the layout and lists every round. Each round's `README.md` lists its gates and documents and, once closed, what it established. `docs/moved.md` maps every pre-migration path to its new one. Files under `results/` and comments in older scripts still carry the old paths.

## 4. Done

- **Rounds 1 to 4** (12 September to 4 October). Replication, instrumentation, the two pivots, round 4's tracks and the second deck's preparation. Summaries in `docs/round01/README.md` to `docs/round04/README.md`. The handoffs `docs/round03/00_prep/round3_oversight_handoff.md`, `docs/round04/oversight/round4_oversight_handoff.md` and `docs/round05/00_prep/round5_oversight_handoff.md` are the full history up to 4 October.
- **Round 5** (7 to 9 October). Instructions for two tracks, five gate memos, the move from handoffs to this file, and the round's close. Summary in `docs/round05/README.md`, and each step has an entry in `docs/progress-log.md`.

## 5. Oversight steps (between rounds)

- [x] **M1. Move `docs/` to the layout by round, interval and track.** Done on 9 October in a cloud session, on branch `docs-migration`. It moved 85 entries by the map in `docs/moved.md`, rewrote paths inside every document including frozen ones by Nicolas's decision, wrote six round reading guides and five plan notes, and installed the state check. The numeric-claim sweep gives the same counts before and after on all 92 documents, with 8,665 of 8,956 claims verified, 290 not found and 1 derived-value error, all of which predate the move. The deck outline verifies 162 of 162. Nicolas still has to open and merge the pull request.
- [ ] **The next advisor presentation,** from the literature landscape and the two original topics through the roadblocks, the pivot, the originality check, the revised directions and the results of rounds 4 and 5. Read `docs/round05/00_prep/deck2/` and the advisor-presentation preferences in section 6 first.
- [ ] **The paper,** a writing plan from the closing pages of rounds 4 and 5, the two round-5 closing memos' readings and the estimator definition.
- [ ] **A next round, if Nicolas wants one,** starting from inclusion-probability weighting under rejective selection.

## 6. Working preferences (Nicolas's)

- **Writing.** Plain, natural prose. No em-dashes. No sentence that states something, then a colon, then the explanation. No compressed or clever phrasing. Do not inflate length (by 4 October).
- **Math.** Rendered LaTeX, each `$$` on its own line. In a derivation, show every expression that carries the argument and skip only the algebra between displayed lines, with a sentence saying what kind of step was skipped. Never describe a derivation in words in place of its formulas (by 4 October). When he asks how something works, derive it slowly and step by step.
- **Numbers.** At the precision the comparison needs, with the relative scale stated. Full precision stays in files.
- **Documents for execution sessions.** Memos and instructions are complete standalone documents, never diffs. Execution sessions do not reconstruct or revise past working documents that have served their purpose.
- **Deliveries.** One file per deliverable, with a fixed name. Overwrite it in place and say what changed (by 4 October).
- **Decisions.** He makes the decisions at his level and wants to be told which need David or Dr. Zhu. He reads every command before it runs and asks why.
- **Slides.** Speaker notes cover only what is on the slide. For advisor decks, no workflow or round language, formulas on the slide when theory is discussed, and every slide says why the step was taken (by 4 October).
- **Aims.** Minimal biology by design. Expression is a signal to predict, calibrate and use for inference. Career goal is quantitative research in finance, so directions are judged by how well their skills transfer. Prefers ML venues (NeurIPS, ICML, AISTATS) or top statistics journals. Wants the paper's scope broad and useful beyond spatial transcriptomics.
- **Project state.** No more oversight handoff documents. State lives in this file, which points to `docs/README.md` for history (9 October). `docs/` is filed chronologically by round, interval and track, with the round's masterplan at the round level. Within a round, memos, gate reports and the reading guides are added as the work goes, and this file is updated at every gate. At each round's close a consistency and currency check between this file and `docs/` is mandatory (9 October).
- **Compute.** Longleaf by default. In round 5 he allowed the tracks' simulations to run on his Mac where that is genuinely faster, until he says stop (8 October, `docs/round05/tracks/ppi/round5_ppi_plan.md` extension 4).
- **Delegation.** For tedious mechanical work he asked for subagents on a smaller model at medium effort (9 October, the path rewrite of the migration).

## 7. Hard rules

These are not preferences. Breaking one invalidates the work. The procedures behind them, each tied to the failure that produced it, are in `docs/WAYS_OF_WORKING.md`.

1. **The gate rule, verbatim in every memo to an execution session.** "Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision."
2. **Every number is read back from its file before it is asserted,** and a derived value (a sum, a ratio) is recomputed before it is declared.
3. **Predictions are written before the run** and scored afterwards as held, partly held, refuted or not tested.
4. **Frozen reports are not edited.** Corrections go in the next memo or report. The one exception so far is the path rewrite of 9 October, which changed only paths, by Nicolas's decision.
5. **Git.** Execution tracks push once per gate, the branch and the tag together, with one pull request that Nicolas merges with a merge commit after review. No rebase, squash, amend or force-push. Commits reach Longleaf as bundles and jobs run from read-only snapshots (`docs/round05/i02/ppi/round5_ppi_E2_decisions.md` section 4).
6. **Other sessions' clones are read only,** with `git --no-optional-locks`. Never write there.
7. **Longleaf is where work runs.** A local run needs Nicolas to ask for that task in chat and is recorded in the plan before it runs.
8. **No claim of novelty** without a literature check (`docs/round04/00_prep/round4_originality_check.md`, `docs/round05/00_prep/deck2/deck2_literature_check.md`).
9. **Contact with anyone outside the project** is Nicolas's decision, never a session's.

## 8. Delegation

Independent, checkable jobs go to subagents, several at once when they do not depend on each other, such as searches, extracting numbers from reports, recomputing a headline, numeric-claim sweeps and mechanical rewrites. Mechanical jobs run one model tier below the oversight chat's model, at medium effort unless Nicolas says otherwise. Independent checks of high-stakes memos and the round-close consistency check run at the oversight chat's own tier, by a fresh agent that has not seen the drafting. Decisions, memos, instructions, edits to this file and commits stay with the oversight chat. Workers never commit or push, and their output is read against the files before it is used.

## 9. Conventions

- **Filing.** Every document has one place by round, interval and track (`docs/README.md`, "How the folders work"). A gate memo goes in the interval it opens. New file names carry the full prefix (`round06_ppi_E2_report.md`), so every name is unique.
- **The document chain.** The oversight chat writes an instruction or a decision memo. The execution session transcribes it into its operating plan in `tracks/<track>/`, flags what looks wrong without changing it, and writes a gate report into its interval folder. The next memo answers the report.
- **Memos.** Each memo opens with what was read and checked, restates the gate rule, then gives acceptance, what was checked, readings for the paper, the next interval with predictions, and answers to every escalation. The oversight chat writes each memo to `main` when Nicolas hands it over, and the track commits the same file unchanged, which merges cleanly. Copies in the claude.ai project docs are for convenience only.
- **Naming.** Tracks and stages are named per round (`round5_ppi_*`, stages E0 to E5; `round5_conf_*`, stages W0 to W5). Tags mark each gate (`round5-ppi-E2`).
- **Numeric-claim sweep.** `code/scripts/verify_numeric_claims.py`, run as `docs/WAYS_OF_WORKING.md` shows, with each track's exceptions in its own `.verify-exceptions-<track>` file. The oversight chat sweeps `README.md`.
- **Tags.** `[proposed]` marks what the oversight chat proposed and Nicolas has not accepted. `[verify]` marks a statement written from memory.
- **Before every documentation commit,** run the state check (section 1).

## 10. Where things are

```
CLAUDE.md                 this file, with protocol, state, preferences and rules
README.md                 the repository's public entry point, status through round 5
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

On Nicolas's Mac, `~/hest-1k` holds `HEST-1k-replication-oversight` (the oversight clone, on `main`), `HEST-1k-replication-PPI` and `HEST-1k-replication-conformal` (the tracks' clones, read only), and `acs_pums2018` (the raw census fetch, not in the repository). On Longleaf, the project tree `/work/users/w/e/weiyang/hest_replication` is on `main` at tag `round4-data-v2`, and the tracks' code clones are under `/work/users/w/e/weiyang/hest_code/`.

## 11. Environment and git

- **People.** Nicolas (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`). Dr. Hongtu Zhu, the PI. Dr. Daiwei (David) Zhang, his GRA supervisor.
- **Sessions.** Execution sessions run on Longleaf, take no scope decisions and report at gates. The oversight chat writes instructions and memos, reviews reports against the files, explains, researches and steers.
- **Git from the cloud.** Clone over HTTPS, with the repository attached with push access. Pushing to `main` needs only the documentation rule of section 1. Pull requests cannot be opened from here with `gh pr create`, so tell Nicolas when one is needed.
- **On the Mac.** A plain `git status` on the mounted folder can leave `.git/index.lock` behind and block the next commit there. The device shell cannot delete files without Nicolas's permission. Commit and push from the cloud clone.
- **Commit messages** go through a file, and end with the attribution lines the session is given.
