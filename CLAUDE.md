# CLAUDE.md

**Read this paragraph first, whoever you are.** This repository is worked on by two kinds of session. If you are an **execution session** (a Claude Science session on a track branch such as `round5-ppi`), your instructions are your track's instruction document in `docs/decisions/`, the operating plan you transcribed from it, and every decision memo since. This file belongs to the oversight chat. Do not edit it and do not act on its plan. The copy on your branch was frozen when the branch started and may be out of date. Section 5's rules apply to you as well. If you are the **oversight chat**, this is your operating file. It replaces the oversight handoff documents, and keeping it current is part of your job.

**Last updated:** 2026-10-09 (oversight, cloud session; this file set up to replace the handoff documents, then the memo completion rule added)

The project is Nicolas Weiyang Zhang's first-year biostatistics PhD project at UNC, in Dr. Hongtu Zhu's lab and supervised by Dr. Daiwei (David) Zhang. The advisors want methods, not applied analysis, with a submittable paper by spring 2027. The paper is "Labelling budgets for prediction-powered inference with clustered data", methodology and theory first, applied to HEST-1k spatial transcriptomics and ACS PUMS 2018 income (`docs/decisions/round4_originality_check.md`).

## 1. Session protocol (oversight)

**At the start of a session**

1. Clone or fetch `NicWYZ/HEST-1k-replication` and read this file in full. Then read `docs/README.md`, the reading guide to every document in the project.
2. Check for staleness before trusting section 2. Run `git fetch origin --tags`, then `git log --oneline origin/main` and `git log --oneline --all --since=<Last updated>`. List the open pull requests (`gh api repos/NicWYZ/HEST-1k-replication/pulls?state=open`). Any gate tag, report or merge newer than "Last updated" is read before section 2 is relied on, and section 2 is corrected first.
3. Note where you are running. A **cloud session** has the repository clone you make, no Longleaf and no data. When the session is **linked to Nicolas's Mac**, the clones under `~/hest-1k` are reachable (section 7). Longleaf is reached only through execution sessions.
4. Read the documents that section 2 names for the work in hand.

**When you need to know what happened before,** read `docs/progress-log.md` first, which says what was found at each step and why the project moved. Then follow it to the files `docs/README.md` lists. Do not rely on memory or reconstruct history from summaries.

**Keep this file, the log and the reading guide current.** Update them in the same commit as the work, whenever:

- a memo or instruction is written, or a gate report is reviewed. Refresh section 2, check the step in section 3, add a dated entry to `docs/progress-log.md`, and add each new document to `docs/README.md`;
- Nicolas states a preference or a rule. Add it to section 4 or 5 with the date, in his terms;
- a decision is made or a question settled. Record it in the progress log and in section 2's open items;
- the session is about to stop, the conversation is long, or a long or risky step is next. Refresh section 2 so a fresh session can resume from it alone, and bump "Last updated".

When in doubt, update. A stale file costs more than an extra commit.

**How the updates reach `main`.** The oversight chat pushes documentation-only commits straight to `main` (Nicolas, 9 October 2026). Documentation means this file, `README.md`, `docs/README.md`, `docs/progress-log.md`, `docs/WAYS_OF_WORKING.md`, `docs/decisions/` and `docs/reference/`. Code, results, `.verify-*` files and anything in a running track's areas go through a pull request that Nicolas merges. Pull before committing, and never force-push.

**Progress log entries** are dated paragraphs, newest first. Each says what was found, what changed because of it, and which files show it. Numbers in them are read back from the file they cite.

**Archiving.** When a round closes, its steps in section 3 move to the progress log and one summary line stays here. Keep this file under about 250 lines.

## 2. Current state (9 October 2026)

- **Round 5** runs as two tracks on branches `round5-ppi` and `round5-conformal`, from the instructions `docs/decisions/round5_ppi_track.md` and `docs/decisions/round5_conformal_track.md` (7 October).
- **The prediction-set track is closed.** Its closing report is `docs/round5_conf_final_report.md` (tag `round5-conf-final`) and its closing memo `docs/decisions/round5_conformal_W5_decisions.md`. Both are on `main` (pull requests #18 and #19).
- **The inference track is in its last interval.** The E4 gate report `docs/round5_ppi_E4_report.md` is on `main` (pull request #17). The E4 memo `docs/decisions/round5_ppi_E4_decisions.md` sets interval 3, which is E4b (an interval that uses balanced cluster selection) and then E5 (the closing report, the paper's estimator definition, the joint design table), ending at the E5 gate. On 9 October the session's local clone had committed the memo and E4b's theory section 3. Nothing is pushed until the E5 gate.
- **Next action.** When Nicolas brings the E5 report, review it against the files and write the closing memo. Check that E4b's predictions and the corrections in section 2 of the E4 memo are carried. Then close round 5 (section 3).
- **What the advisors have seen.** Nicolas reported on 7 October that the second advisor meeting stopped at slide 8, so the advisors have seen the project up to the pivot and the originality check and not the round-4 or round-5 results (`docs/decisions/round5_ppi_track.md` section 2.1). The deck preparation is in `docs/deck2/`.
- **Waiting on Nicolas or his advisors.** Whether regime B (a few labelled spots on every donor) can be bought on a spatial platform, and at what cost, has not been asked of David. Whether to contact the GHCP authors is Nicolas's with his advisors, never a session's. The venue and which result the paper leads with are not yet raised.
- **Owed by the oversight chat.** The README sweep, which finds a value of 0.1018 it cannot match. The root `README.md` still describes the project at round 2 and needs rewriting at round 5's close. The numeric-claim checker's pandas-3 TypeError fix.

## 3. Operating plan (oversight)

### Done

- **Rounds 1 to 4** (12 September to 4 October). Replication, instrumentation, the two pivots, round 4's two tracks and the second deck's preparation. Summary and pointers in `docs/progress-log.md`. The handoffs `docs/decisions/round3_oversight_handoff.md`, `round4_oversight_handoff.md` and `round5_oversight_handoff.md` are the full history up to 4 October.

### Round 5 (current)

- [x] **Instructions for the two tracks** (7 October, pull request #14).
- [x] **E2 gate memo** (8 October, `docs/decisions/round5_ppi_E2_decisions.md`).
- [x] **W2 gate memo** (8 October, `docs/decisions/round5_conformal_W2_decisions.md`).
- [x] **E4 gate memo** (9 October, `docs/decisions/round5_ppi_E4_decisions.md`).
- [x] **W5 closing memo** (9 October, `docs/decisions/round5_conformal_W5_decisions.md`).
- [x] **State kept in this file in place of handoffs** (9 October, see the progress log).
- [ ] **E5 review and the inference track's closing memo.**
- [ ] **Close round 5.** Sweep the README and fix the 0.1018 entry, rewrite the root `README.md` status, update `docs/README.md` and the progress log, propose a tag on `main` for Nicolas, and archive this section.

### After round 5 (outline; expand when current)

- [ ] **The next advisor presentation,** from the literature landscape and the two original topics through the roadblocks, the pivot, the originality check, the revised directions and the results of rounds 4 and 5.
- [ ] **The paper,** a writing plan from the two tracks' closing pages and the E5 estimator definition.

## 4. Working preferences (Nicolas's)

- **Writing.** Plain, natural prose. No em-dashes. No sentence that states something, then a colon, then the explanation. No compressed or clever phrasing. Do not inflate length (by 4 October).
- **Math.** Rendered LaTeX, each `$$` on its own line. In a derivation, show every expression that carries the argument and skip only the algebra between displayed lines, with a sentence saying what kind of step was skipped. Never describe a derivation in words in place of its formulas (by 4 October). When he asks how something works, derive it slowly and step by step.
- **Numbers.** At the precision the comparison needs, with the relative scale stated. Full precision stays in files.
- **Documents for execution sessions.** Memos and instructions are complete standalone documents, never diffs. Execution sessions do not reconstruct or revise past working documents that have served their purpose.
- **Deliveries.** One file per deliverable, with a fixed name. Overwrite it in place and say what changed (by 4 October).
- **Decisions.** He makes the decisions at his level and wants to be told which need David or Dr. Zhu. He reads every command before it runs and asks why.
- **Slides.** Speaker notes cover only what is on the slide. For advisor decks, no workflow or round language, formulas on the slide when theory is discussed, and every slide says why the step was taken (by 4 October).
- **Aims.** Minimal biology by design. Expression is a signal to predict, calibrate and use for inference. Career goal is quantitative research in finance, so directions are judged by how well their skills transfer. Prefers ML venues (NeurIPS, ICML, AISTATS) or top statistics journals. Wants the paper's scope broad and useful beyond spatial transcriptomics.
- **Project state.** No more oversight handoff documents. State lives in this file, which points to `docs/README.md` for history (9 October).
- **Compute.** Longleaf by default. In round 5 he allowed the tracks' simulations to run on his Mac where that is genuinely faster, until he says stop (8 October, `docs/round5_ppi_plan.md` extension 4).

## 5. Hard rules

These are not preferences. Breaking one invalidates the work.

1. **The gate rule, verbatim in every memo to an execution session.** "Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision."
2. **Every number is read back from its file before it is asserted,** and a derived value (a sum, a ratio) is recomputed before it is declared.
3. **Predictions are written before the run** and scored afterwards as held, partly held, refuted or not tested.
4. **Frozen reports are not edited.** Corrections go in the next memo or report.
5. **Git.** Execution tracks push once per gate, the branch and the tag together, with one pull request that Nicolas merges with a merge commit after review. No rebase, squash, amend or force-push. Commits reach Longleaf as bundles and jobs run from read-only snapshots (`docs/decisions/round5_ppi_E2_decisions.md` section 4).
6. **Other sessions' clones are read only,** with `git --no-optional-locks`. Never write there.
7. **Longleaf is where work runs.** A local run needs Nicolas to ask for that task in chat and is recorded in the plan before it runs.
8. **No claim of novelty** without a literature check (`docs/decisions/round4_originality_check.md`, `docs/deck2/deck2_literature_check.md`).
9. **Contact with anyone outside the project** is Nicolas's decision, never a session's.

The procedures behind these, each tied to the failure that produced it, are in `docs/WAYS_OF_WORKING.md`.

## 6. Conventions

- **The document chain.** The oversight chat writes an instruction or a decision memo. The execution session transcribes it into its operating plan, flags what looks wrong without changing it, and writes a stage report at the gate. The next memo answers the report. Instructions and memos are in `docs/decisions/`, and plans, reports and theory documents in `docs/`.
- **Memos.** Each memo opens with what was read and checked, restates the gate rule, then gives acceptance, what was checked, readings for the paper, the next interval with predictions, and answers to every escalation. The oversight chat writes each memo to `docs/decisions/` on `main` when Nicolas hands it over, and the track commits the same file unchanged, which merges cleanly. A memo is not finished until the same commit also updates this file (section 2, and section 3's step), adds its entry to `docs/progress-log.md` and adds its row to `docs/README.md`. The same holds for an instruction document. Copies in the claude.ai project docs are for convenience only.
- **Reviewing a report.** Read the whole grid before accepting a headline. Recompute key numbers from the result files, and use an independent checker agent for high-stakes memos. Read the session's flagged points first.
- **Naming.** Tracks and stages are named per round (`round5_ppi_*`, stages E0 to E5; `round5_conf_*`, stages W0 to W5). Tags mark each gate (`round5-ppi-E2`).
- **Numeric-claim sweep.** `code/scripts/verify_numeric_claims.py`, with each track's exceptions in its own `.verify-exceptions-<track>` file. The oversight chat sweeps `README.md`.

## 7. Where things are

```
CLAUDE.md                 this file: protocol, state, plan, preferences, rules
README.md                 the repository's public entry point (status stale since round 2)
docs/README.md            the reading guide: every document, by round, with its role
docs/progress-log.md      what happened and why, newest first
docs/WAYS_OF_WORKING.md   procedures, each tied to the failure that produced it
docs/decisions/           instructions, decision memos, the old oversight handoffs
docs/reference/           methods derived from scratch, concepts explained
docs/deck2/               the second advisor deck's outline, explainer, literature check
docs/round*_*.md          plans, stage reports, theory documents
code/scripts/             every script; results/ the outputs by round; figures/ the figures
superseded/               documents a later one replaced, each bannered
```

On Nicolas's Mac under `~/hest-1k`: `HEST-1k-replication-oversight` (the oversight clone, on `main`), `HEST-1k-replication-PPI` and `HEST-1k-replication-conformal` (the tracks' clones, read only), and `acs_pums2018` (the raw census fetch, not in the repository). On Longleaf: the project tree `/work/users/w/e/weiyang/hest_replication` on `main` at tag `round4-data-v2`, and the tracks' code clones under `/work/users/w/e/weiyang/hest_code/`.

## 8. Environment and git

- **People.** Nicolas (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`). Dr. Hongtu Zhu, the PI. Dr. Daiwei (David) Zhang, his GRA supervisor.
- **Sessions.** Execution sessions run on Longleaf, take no scope decisions and report at gates. The oversight chat writes instructions and memos, reviews reports against the files, explains, researches and steers.
- **Git from the cloud.** Clone over HTTPS. Pushing to `main` needs only the documentation rule of section 1. Pull requests cannot be opened from here with `gh pr create`, so tell Nicolas when one is needed.
- **On the Mac.** A plain `git status` on the mounted folder can leave `.git/index.lock` behind and block the next commit there. The device shell cannot delete files without Nicolas's permission.
- **Commit messages** go through a file, and end with the attribution lines the session is given.
