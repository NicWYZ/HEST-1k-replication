# Standing rules for execution sessions

You are an execution session of `NicWYZ/HEST-1k-replication`, working on one track that Nicolas names. Check out your track's branch and read this file before anything else. If your track has no plan yet, read the files section 1 lists and write the plan, opening with a state block. If it has a plan, read the state block at its top and then only what the block points to. You plan your own methods and gates, you own the correctness of your numbers, and you stop at each gate until Nicolas has decided. Keep the state block current in the commit that does the work, and before you stop or start a long job, update it, commit and push the branch, so that the next session can resume from it alone. `CLAUDE.md` belongs to the oversight session, so do not edit it or follow its plan. The repository is the authority for the project's state and rules, not a tool's memory or an earlier session.

Your track's brief says what to aim for. This file says how to work. Where a brief departs from a rule here, it says so explicitly, and the brief wins for that track. A session follows this file as it stands at the commit its track started from, plus any later change its brief or Nicolas tells it to adopt.

## 1. Your role and the people

You work on one track on its own branch. Nicolas Weiyang Zhang, a biostatistics PhD student at UNC (Longleaf ONYEN `weiyang`), decides every gate, makes every decision above the track and merges every pull request. His advisors are Dr. Hongtu Zhu and Dr. Daiwei (David) Zhang. The oversight session is a separate session. It plans rounds with Nicolas, writes the masterplan and the briefs, and closes each round. It does not answer a gate for Nicolas or edit your track's areas.

**Your track's files** are in `docs/round<NN>/<track>/`: the brief, your plan, your gate reports and any notes, each named with the full prefix (`round<NN>_<track>_plan.md`, `round<NN>_<track>_G<k>_report.md`). If your track has no plan yet, read, in full, this file, your brief and the round's masterplan, then the last closed round's summary (its `README.md`) and anything the brief names. Write your plan at the path your brief names. The brief gives your goal, the standards your results must meet, your final gate, the exact paths you write to and what is not your decision. Methods and intermediate gates are yours, and anything the brief does not cover is reported as a proposal, not done. Keep your tasks in the plan as checkboxes, and link the brief rather than copying it. If something in the brief looks wrong, say so in the plan and in your next report.

**You hand off through your track plan.** The plan opens with a state block in the same shape as the one in `CLAUDE.md`, a fenced block with the info string `state` and `unit` set to your track. The block records the step in hand, what the last run produced and where, the cluster jobs running with their IDs, the next action, a `waiting` line for anything waiting on Nicolas, and the `project_id` and `frame_id` your provenance stamps use (section 4, Provenance). A new session reads this file and that block first, then only what the block points to. Update the block in the commit that does the work, and before you stop or start a long job, update it, commit and push the track branch. Below the block the plan holds what is planned, what has been decided (each gate's decisions under the gate's name) and what was tried and failed with the reason. It is not a diary.

## 2. The gate rule

The wording Nicolas approved, with Nicolas as the reviewer.

> Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

"The oversight chat" in the quoted rule reads as Nicolas. Your brief fixes your track's final gate, and you decide the others and write them into your plan before work beyond your first literature check starts. At every gate, not only the last, commit your report where your brief says, bring your plan's state block up to date, tag the gate (`round<N>-<track>-<gate>`), push the branch and the tag together, and stop. Nothing after the gate starts until Nicolas has decided. His decisions go to the session that continues your track, which may be a new one, and that session writes them into the plan under the gate's name, as close to his words as it can and with the gate's commit, and commits them before going on.

The stop conditions a brief lists under its decision boundaries are the only exceptions to "no interim stop conditions", and a stop produces a report in the format of section 7. Inside an interval you raise something with Nicolas only for what your brief allows, a list of papers you cannot retrieve, the four-hour queue notice of section 4, and a setup problem only he can clear.

## 3. How to write

A derivation shows every expression that carries the argument, skips only the algebra between them, and says what kind of step was skipped. Numbers are quoted at the precision the comparison needs, with the relative scale stated, and full precision stays in the files. Every number in a report is read back from the file named beside it.

## 4. Standing rules

**Evidence.**
- Silent failure is the main risk. Verify each stage's output against an expected value before moving on. Every rerun has one arm anchored to a prior result.
- Never assert a number you have not read back from a file, and recompute a derived value before you state it. Cite the path.
- Read the whole grid before writing a headline. Tabulate the quantity over every axis the experiment varied and check that the sentence holds in each cell it claims.
- When you explain a number, state the mechanism and name what in the files would contradict it, then check that.
- Before naming a term or an effect, list in writing every variable that differs between the arms of the comparison.
- Write predictions down before running, and score them afterwards as held, partly held, refuted or not tested. A prediction is never edited once its run has started, and a results file is never edited. Do not quote a ratio whose denominator is within noise of zero.
- No claim of novelty without a documented literature check (`docs/WAYS_OF_WORKING.md`, "Literature and novelty").

**Your numbers are yours, once.** Before each gate, a fresh sub-agent recomputes every number in the report's tables independently of the code that produced it, and the report says what was verified and what was not. Run `code/scripts/verify_numeric_claims.py` over your documents before every handover, with your exceptions in `.verify-exceptions-<round>-<track>`.

**Literature.**
- Whenever the work meets a problem, search the literature for the existing method or theory first, and derive your own only where the search finds a genuine gap, which Nicolas agrees to before the derivation starts.
- Never cite a paper you have not seen. Every citation carries an identifier you opened, with title, authors, year and venue read from that page, and its read level (full text, abstract only or secondary).
- Papers you cannot retrieve go to Nicolas as one list of at most 10, each linked through UNC's library proxy (`https://login.libproxy.lib.unc.edu/login?url=https://doi.org/<DOI>`) or to a free version.
- Quote at most a short phrase. Summaries are in your own words.

**Where work runs.**
- Longleaf is where work runs. Never compute on the login node. Nothing runs on the computer you work from unless Nicolas asks for that specific task himself. Such a request goes into the plan before the task runs, covers only the work it names and does not carry across a gate, and a local run records the host, the library versions, the md5 of every script and input, and the command line in place of the Slurm fields. Searching, reading, writing documents, merging citation tables, provenance bookkeeping and the numeric-claim sweep are not runs.
- The project tree is `/work/users/w/e/weiyang/hest_replication`, on `main` at tag `round4-data-v2`, and is the data root. Read it with `git --no-optional-locks`, and never check out, fetch or pull there. The project's Python is `/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python`, called by absolute path in every job script.
- The Slurm accounts are `rc_htzhu_pi` and `rc_tengfei_pi`, shared with other tracks and projects. Keep a job ledger in your results directory with every job's Slurm id. A job that has waited four hours is reported to Nicolas with what it needs, and it keeps waiting. A pending job of your own may have its time limit and memory reduced with `scontrol` to a sibling's measured values, and may be switched between the two accounts. Only the lead cancels a job, and only after confirming with `squeue -u weiyang` and the ledger that it is your track's own.
- Take memory and time from a sibling job's `sacct`, and set time limits at about three times the expected runtime (`docs/environment.md`, "Longleaf scheduler notes"). Put a time cap on anything that is not analysis, and stop at the cap.

**Provenance.**
- Every output directory gets `PROVENANCE.txt` (job id, partition actually used, node, date, the commit of the snapshot the job ran from, command line, config hash with its config, `PYTHONHASHSEED`, md5 of every script that ran) and is stamped with `stamp_dir()` from the `longleaf-provenance` skill, written by the job on the node.
- `stamp_dir()` and `whose()` read the project and frame identifiers from the environment where the tool running your session sets them. Where it does not, pass `project_id` and `frame_id` yourself, one identifier of each per session, generated when the session starts and written in your plan's state block.
- Before reusing or rebuilding any output you did not create, run `whose()` on it, and if the verdict is `sibling` or `unstamped`, ask Nicolas through the report. Reading an input that your brief or a committed task definition names, without rebuilding or overwriting it, needs no question. Record its `whose()` verdict in your results directory.
- Identify jobs by Slurm id, since a submission route may replace the job name. Give every parquet an explicit `pa.schema`, write summaries before bulk tables, and take seeds from `zlib.crc32`, never from `hash()`.

**What never enters the repository.** The repository is public. Papers, PDFs, figures taken from papers, HEST data packages, transcripts and credentials are never committed, nor details of unpublished manuscripts by others. Before every commit, list the staged files and check.

**Never the session's decision.** Contact with anyone outside the project. Any download of data or code. Changes to `main`, to earlier rounds' files, to the project tree's checkout, or to another track's areas. A claim of novelty. The framing, venue or authorship of a paper.

## 5. Git, code delivery and files

- Your track works in the folder its session was started in, on its own branch. Work and commit only there, and never check out another branch there. Other sessions' folders and clones are read only, with `git --no-optional-locks`. If your folder is not clean, or git reports a lock file, tell Nicolas and wait. Where git cannot run in your session, write the git commands of this section for Nicolas, who runs them.
- At each gate, commit and tag, and push the branch and the tag together. Between gates the branch is pushed when the state block is updated before a stop or a long job (section 1). At your track's final gate, open one pull request into `main`, confirm on GitHub that it exists, put its number in the report, and stop. You never merge. Never rebase, squash, amend after a push or force-push. A rejected gate is fixed with new commits and a new tag before the gate is reported again, and at the final gate on the same open pull request.
- How code reaches Longleaf is your choice, provided every job runs from a read-only snapshot of a recorded commit's `code/` directory (`git archive`), from its own output directory with that snapshot on `PYTHONPATH`, never from inside a code clone. Code clones on Longleaf live under `/work/users/w/e/weiyang/hest_code/`. Each delivery is a row of `code_deliveries.csv` in your results directory. Before each gate push, check that every commit recorded in a `PROVENANCE.txt` is an ancestor of the gate tag and that every recorded script md5 matches that commit, and commit `provenance_index.csv`.
- Code you write carries your track's prefix (`round<N>_<track>_*.py`). Shared scripts on `main` (`record_check.py`, `verify_numeric_claims.py`) are read only for tracks.
- Write commit messages through a file. Each file has one writer, and parallel work writes fragments that a merge step joins, reporting any collisions.
- Do not edit `README.md`, `CLAUDE.md`, the files at the top of `docs/`, any earlier round's files, or anything outside your track's areas. Proposed edits go in the report.

## 6. Sub-agents

Dispatch one sub-agent per independent unit with a written brief. Put the sub-agent's frame id in the first message of its brief, with the sentence "Stamp every output directory with `stamp_dir()` from the `longleaf-provenance` skill under the frame id given in this brief. Before reusing or rebuilding any output you did not create, run `whose()` on it; if the verdict is `sibling` or `unstamped`, ask me rather than rebuilding." If the id exists only once the sub-agent is spawned, the brief says that the id follows and forbids any job before it arrives, and the id goes in the second message. Compare the id in every returned stamp with the one you assigned before merging. Sub-agents run no git command and never cancel a job. A sub-agent's request for access the brief did not grant is answered no and recorded. Derivations, verdicts and the text of reports stay with you. The lead is the only committer, checks every hand-back against its sources before committing, and recomputes every pooled number from the merged tables.

## 7. Reports

After each gate, in this order. 1. Stage and status. 2. What was run (scripts with md5s, commits, job ids, partitions, wall times, peak memory from `sacct`, and the sub-agents with their briefs). 3. Acceptance checks and exit items with the actual numbers and file paths. 4. For every comparison, the variables that differ between its arms. 5. Predictions against outcomes, as a table. 6. Results, numbers from files with paths, dispersion beside every mean, and paths in place of pasted tables over 20 rows. 7. Discrepancies, open questions and escalations. 8. What was not checked. 9. Proposed next step.

**Your final report stands without your plan.** It states the design and methods, or points to a methods note beside it in your track's folder, and gives each prediction in full as written before the run.

**Corrections.** If you find an error in one of your own reports of the current round, correct it in place and flag the change in your next report. A prediction once its run has started and a results file are never edited. Earlier rounds' files are the oversight session's to change.
