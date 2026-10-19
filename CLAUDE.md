# CLAUDE.md

**Read this paragraph first, whoever you are.** This repository is worked on by two kinds of session. If you are an **execution session** (a Claude Science or Claude Code session on a track branch such as `round7-fedlearn`), your standing rules are `docs/EXECUTION_RULES.md`, and your instructions are your track's instruction document in `docs/roundNN/i01/<track>/`, the operating plan you transcribed from it, and every decision memo since. This file belongs to the oversight chat. Do not edit it and do not act on its plan. The copy on your branch was frozen when the branch started and may be out of date. Section 7's rules apply to you as well. If you are the **oversight chat**, this is your operating file. It replaces the oversight handoff documents, and keeping it current is part of your job.

**Last updated:** 2026-10-19, morning (oversight, cloud session linked to the Mac; round 8 positioning, first search pass and reading done, note drafted, second pass pending)

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

## 2. Current state (19 October 2026)

- **Round 8 is open** (`docs/round08/masterplan.md`, `docs/round08/README.md`). One track, `positioning`, an oversight track done by the oversight chat on `main`, with no branch. It is in interval i01, stage P1 (the first search pass over themes T1 to T5 by subagents, then a second pass at high effort) with P2 reading begun, under the scope `docs/round08/i01/positioning/round08_positioning_scope.md`. Its gate P3 is Nicolas's review of `docs/round08/i01/positioning/round08_positioning_note.md`, not yet written, with one oversight pull request for the search logs, and the tag `round8-positioning-P3` `[proposed]`. No execution track is running. All pull requests through #33 are merged.
- **Why the round starts here.** Four papers from June to September 2026, from the survey-sampling and PPI sides, bear on the claims round 7 left as the paper's own (masterplan, "Why this round"). Three are new to the project, and Shirota's was checked only from its abstract in the deck-2 check. The paper plan, an execution track on Longleaf and the advisor deck are opened by amendment after the P3 review.
- **The PPI paper.** Its current account is `docs/round07/oversight/round07_ppi_results_explained.md`, its estimator `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`, and what it can claim `docs/round07/i04/ppi/round07_ppi_final_decisions.md` (section 2) with `docs/round07/oversight/round07_ppi_positioning.md`, until round 8's note replaces them. Round 5's readings are in section 3 of `docs/round05/i04/ppi/round5_ppi_E5_decisions.md` and `docs/round05/i03/conformal/round5_conformal_W5_decisions.md`.
- **Federated learning and the textual knowledge base** are outside round 8. Track fedlearn closed at F4 (`docs/round07/i03/fedlearn/round07_fedlearn_final_decisions.md`), and R7-4 waits on Nicolas with his advisors, with `docs/round07/oversight/round07_fedlearn_decision_report.md`. On 19 October he said his next advisor meeting will be about these lines.
- **Next action.** Finish the second search pass (cut short on 19 October by the per-turn search limit), read any new close papers, revise the draft note (section 5, R8.3), have a fresh agent check it, commit it with the round's records, and tell Nicolas to open the gate's pull request from branch `oversight-round8-positioning-search`. Nicolas may tag `round7-close` on `main` `[proposed]`.
- **What the advisors have seen.** Nicolas reported on 7 October that the second advisor meeting stopped at slide 8, so the advisors have seen the project up to the pivot and the originality check and not the results of rounds 4, 5 or 7 (`docs/round05/i01/ppi/round5_ppi_track.md` section 2.1). The deck preparation is in `docs/round05/00_prep/deck2/`. The meeting of 12 October discussed round 6's experiments.
- **Carried housekeeping,** not urgent. The D4 probe rerun, the ten unresolved claims in two pre-round-3 documents, the `r5c_leak_summary.csv` reading (`docs/round05/00_prep/round5_oversight_handoff.md` section 12), and the checker fix of step R7.6.

**Open questions.** Each waits on the person named. The default holds until it is decided.

| # | Question | Who decides | Default |
|---|---|---|---|
| Q1 | Can regime B (a few labelled spots on every donor) be bought on a spatial platform, and at what cost? Not yet asked of David | Nicolas, with David | the paper treats regime B as a design comparison, with no cost claim |
| Q2 | Should the GHCP authors be contacted? | Nicolas, with his advisors, never a session | no contact |
| Q3 | Which venue, and which result the paper leads with | Nicolas, with his advisors, after round 8's positioning note | open |
| Q4 | Tag `round5-final` on `main` at round 5's close `[proposed]`. `round6-close` exists | Nicolas | no tag |
| R6-3 | Whether and when round 6's two summaries go to David | Nicolas, never a session | nothing is sent |
| R7-2 | How the federated learning paper is framed relative to David's textual knowledge base | Nicolas, with David and Dr. Zhu | the review compares the routes on evidence and takes no side |
| R7-3 | Venue and authorship of the federated learning paper | Nicolas, with his advisors | open |
| R7-4 | Whether the closing recommendation of the fedlearn track becomes the federated learning paper, and whether its first method targets partial gene overlap or private release (`docs/round07/i03/fedlearn/round07_fedlearn_final_decisions.md`, section 4) | Nicolas, with Dr. Zhu and David | no federated learning track opens; the oversight chat's view is partial gene overlap |
| R7-5 | The PPI paper's positioning against Broska and Howes's interval with small-sample corrections, which covers at four labelled clusters and is narrower there than the paper's tuned interval (`docs/round07/i04/ppi/round07_ppi_final_decisions.md`, section 4). Feeds O5 | Nicolas, with David | the positioning note is revised once this is decided, and until then carries a banner saying its few-cluster claims are too broad |
| R7-6 | Whether the paper's tuned estimator uses a global coefficient below six labelled clusters, where rule `c_crossfit_design` sets the coefficient to zero. Changes what round 5 closed. Its evidence is `bh_t`, which has no finite-population factor, so a validation run comes first | Nicolas, after round 8's positioning note (said on 19 October) | round 5's estimator as defined |
| R7-7 | Which balanced design the PPI paper recommends (`docs/round07/i04/ppi/round07_ppi_final_decisions.md`, section 4) | Nicolas, with David | `[proposed]` `rej_t` where its support and one balance variable allow, the S4b cube design as the design-based alternative |
| R8-1 | Whether the prediction-set half (HCP, GHCP, `within_full`) stays in the PPI paper or becomes a separate paper | Nicolas, after round 8's positioning note (said on 19 October) | the decision waits |
| O3 | How the PPI paper and the lab's manuscript refer to each other | Nicolas, with David and Dr. Zhu | neither refers to the other |
| O5 | The PPI paper's positioning, as in `docs/round07/oversight/round07_ppi_positioning.md`, section 5 | Nicolas, with David | the paper claims nothing that note marks as prior art, classical or implied, nor the few-cluster regime in general (its banner of 15 October) |

## 3. Where the record is

`docs/` is filed in time order by round, interval and track, and `docs/README.md` explains the layout and lists every round. Each round's `README.md` lists its gates and documents and, once closed, what it established. `docs/moved.md` maps every pre-migration path to its new one. Files under `results/` and comments in older scripts still carry the old paths.

## 4. Done

- **Rounds 1 to 4** (12 September to 4 October). Replication, instrumentation, the two pivots, round 4's tracks and the second deck's preparation. Summaries in `docs/round01/README.md` to `docs/round04/README.md`. The handoffs `docs/round03/00_prep/round3_oversight_handoff.md`, `docs/round04/oversight/round4_oversight_handoff.md` and `docs/round05/00_prep/round5_oversight_handoff.md` are the full history up to 4 October.
- **Round 5** (7 to 9 October). Instructions for two tracks, five gate memos, the move from handoffs to this file, and the round's close. Summary in `docs/round05/README.md`, and each step has an entry in `docs/progress-log.md`.
- **Between rounds 5 and 6** (9 to 11 October). `docs/` moved to the layout by round, interval and track (pull request #22), and round 5's results were explained for Nicolas.
- **Round 6** (11 to 13 October). David's cheatsheet experiment, one track in a Claude Code cloud session with two gates, then an extension on held-out CCRCC patients in a local session on the Mac with two more gates, and the close. Summary in `docs/round06/README.md`, and each step has an entry in the progress log.
- **Round 7** (13 to 15 October). Two Claude Science tracks on Longleaf, federated learning (two gates) and the PPI paper's inference after histology-guided selection (three gates), the positioning against newer work, two reports for Nicolas, and the close. Summary in `docs/round07/README.md`.

## 5. Oversight steps

Round 7's steps R7.0 to R7.11 are in `docs/progress-log.md`, entry of 15 October, round close.

- [x] **R8.0 Open round 8,** through the `project-state-keeping` skill. 19 October, cloud session linked to the Mac. Staleness check found only pull request #33 after round 7's close. Nicolas chose the direction (positioning check first, R7-6 and R8-1 after it, thoroughness first). Wrote the masterplan with predictions P.1 to P.5, the positioning scope with claims C0 to C12, the round's reading guide, and updated `docs/README.md`, the progress log and this file. A fresh agent checked them before commit and found 14 errors and 12 suggestions, all worked in. The largest were that Shirota's paper was already in the repository, that C12 was missing, and that C1 and C9 restated ground round 7 had settled.
- [ ] **R8.1 P1 search.** On 19 October the first pass was done (205 queries, 129 candidate rows, 27 graded close), logs on branch `oversight-round8-positioning-search` under `results/round8/positioning/P1_search/pass1/`, which becomes the gate's pull request. Second pass started at high effort and was cut short by the session's per-turn limit on web searches. It resumes in the next turn and its outputs go to `pass2/`. The plan as written is a first pass of five subagents, one per theme T1 to T5, one tier below at medium effort, logs in the scratchpad. Second pass at high effort, seeded with the earlier checks' references and the backward citations of the papers read in full. The oversight chat merges both passes, regrades every close paper itself, and the merged logs go to `results/round8/positioning/P1_search/` in the gate's pull request.
- [ ] **R8.2 P2 full reading.** On 19 October fifteen sources were read in full or in the parts that bear on a claim (list in the draft note, section 1.2), with working notes in the claude.ai project doc `claude/round08_positioning_working_notes.md`. The largest findings are that `rej_t`'s variance is Yang, Qu and Li's Corollary A5 (JASA 2023, arXiv:2109.09930), the allocation formula follows from Snijders' eq. (12) and (13), and round 5's cross-fitting term comes from its averaged-coefficient form, which the fold-wise form in print (Lu et al. 2025, An et al. 2026) avoids at $n_L = G$. The plan as written is a full reading of every close paper and the classical sources, starting with arXiv:2608.10356, 2609.10904, 2609.04082 and 2606.03211. The papers' text is read from their arXiv HTML through the browser on the Mac, since neither the cloud session nor the Mac's shell can download from arXiv. Papers not readable go to Nicolas as one list of at most 10.
- [ ] **R8.3 P3 the note,** a verdict per claim C0 to C12, predictions scored. On 19 October it was drafted, and the draft is kept outside the repository in the claude.ai project doc `claude/round08_positioning_note_draft.md` until it is checked. It waits on the second pass and the independent check.
- [ ] **R8.4 Independent check** of the note by a fresh agent at the oversight chat's tier, findings worked in, numeric sweep, state check, commit with the round's records.
- [ ] **R7.6 Checker fix,** carried. `code/scripts/verify_numeric_claims.py` misses comma-grouped integers inside free-text CSV cells. Fix it through an oversight pull request.
- [ ] **Carried. The paper,** a writing plan from the closing pages of rounds 4, 5 and 7, the estimator definition, the positioning note and the round-7 explainer, after R7-5 to R7-7.
- [ ] **Carried. The next advisor presentation,** from the literature landscape through the pivot, the originality check and the results of rounds 4, 5 and 7, with the federated learning decision report as a separate item. Read `docs/round05/00_prep/deck2/` and the presentation preferences in section 6 first. Round 6's two summaries are ready as a short item.

## 6. Working preferences (Nicolas's)

- **Writing.** Plain, natural prose. No em-dashes. No sentence that states something, then a colon, then the explanation. No compressed or clever phrasing. Do not inflate length (by 4 October).
- **Math.** Rendered LaTeX, each `$$` on its own line. In a derivation, show every expression that carries the argument and skip only the algebra between displayed lines, with a sentence saying what kind of step was skipped. Never describe a derivation in words in place of its formulas (by 4 October). When he asks how something works, derive it slowly and step by step.
- **Numbers.** At the precision the comparison needs, with the relative scale stated. Full precision stays in files.
- **Documents for execution sessions.** Standing rules for execution sessions live once, in `docs/EXECUTION_RULES.md`, which the oversight chat keeps current with a dated revision list. Track instructions and memos cite it and carry only what is specific to the track, saying so explicitly where they depart from it. The Claude Science project instructions point sessions to it (13 October, replacing the rule that every instruction and memo restates the standing rules; the two round-7 instructions already handed over keep their full text). Memos and instructions are otherwise complete documents, never diffs. From round 6 an instruction and the masterplan stay living on `main` while the track runs. The oversight chat revises them in place with a dated line in their revision list, and Nicolas tells the session to check for updates instead of pasting text (11 October). Execution sessions do not reconstruct or revise past working documents that have served their purpose.
- **Deliveries.** One file per deliverable, with a fixed name. Overwrite it in place and say what changed (by 4 October).
- **Decisions.** He makes the decisions at his level and wants to be told which need David or Dr. Zhu. He reads every command before it runs and asks why.
- **Thoroughness.** "Thoroughness always comes first." Said on 19 October about round 8's positioning check, with no deadline pressing.
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

1. **The gate rule, kept verbatim in `docs/EXECUTION_RULES.md` section 2, which every memo cites (13 October, previously restated in every memo).** "Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision."
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
- **Memos.** Each memo opens with what was read and checked, cites the gate rule in `docs/EXECUTION_RULES.md` section 2, then gives acceptance, what was checked, readings for the paper, the next interval with predictions, and answers to every escalation. The oversight chat writes each memo to `main` when Nicolas hands it over, and the track commits the same file unchanged, which merges cleanly. Copies in the claude.ai project docs are for convenience only.
- **Naming.** Tracks and stages are named per round (`round5_ppi_*`, stages E0 to E5; `round5_conf_*`, stages W0 to W5; `round06_cheatsheet_*` documents and `round6_cheatsheet_*.py` scripts, stages C0 to C7; `round07_fedlearn_*` documents and `round7_fedlearn_*.py` scripts, stages F0 to F4; `round07_ppi_*` documents and `round7_ppi_*.py` scripts, stages S0 to S5 with S2b and S4b; `round08_positioning_*` documents, stages P0 to P3, results in `results/round8/positioning/`). Tags mark each gate (`round5-ppi-E2`, `round6-cheatsheet-C1`, `round7-fedlearn-F2`).
- **Numeric-claim sweep.** `code/scripts/verify_numeric_claims.py`, run as `docs/WAYS_OF_WORKING.md` shows, with each track's exceptions in its own `.verify-exceptions-<track>` file. The oversight chat sweeps `README.md`.
- **Tags.** `[proposed]` marks what the oversight chat proposed and Nicolas has not accepted. `[verify]` marks a statement written from memory.
- **Before every documentation commit,** run the state check (section 1).

## 10. Where things are

```
CLAUDE.md                 this file, with protocol, state, preferences and rules
README.md                 the repository's public entry point, status through round 7
docs/README.md            the reading guide, with the layout and one row per round
docs/progress-log.md      what happened and why, newest first
docs/WAYS_OF_WORKING.md   procedures, each tied to the failure that produced it, and the guardrails register
docs/EXECUTION_RULES.md   the standing rules every execution session follows, cited by instructions and memos
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
