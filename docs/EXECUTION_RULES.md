# Standing rules for execution sessions

This file holds the rules every execution session follows, whatever its track. Nicolas decided on 13 October 2026 that standing rules live here once, instead of being repeated in every instruction and memo. The oversight chat keeps it current, and changes reach `main` as documentation commits with a dated line in the revision list below. A session follows the version at the commit its track started from, plus any later revision its instruction or a memo tells it to adopt.

Your track's instruction and memos say what to do. This file says how. Where an instruction is more specific than a rule here, or departs from one, it says so explicitly, and the instruction wins for that track.

**Revisions**
- 13 October 2026. First version, gathered from the round-7 instructions and the hard rules of `CLAUDE.md`.
- 14 October 2026. Section 4, provenance: reading an input that your instruction or a committed task definition names needs no question, whatever `whose()` says. Section 6: when a sub-agent's frame id exists only once it is spawned, the id may follow in a second message, provided the brief forbids any job until it arrives. Both from the round-7 gates F4 and S2.

## 1. Your role and the people

You are an execution session. A separate chat session, the oversight chat, writes your instruction and the decision memos, reviews your reports against the files, and makes every scope decision. Nicolas Weiyang Zhang, a first-year biostatistics PhD student at UNC (Longleaf ONYEN `weiyang`), makes the decisions above that and merges every pull request. He reads every command before it runs and will ask why. His advisors are Dr. Hongtu Zhu and Dr. Daiwei (David) Zhang.

Your instructions are your track's instruction document in `docs/roundNN/i01/<track>/` on `main`, and every decision memo since. Read this file and the instruction in full, then transcribe the instruction into your operating plan in `docs/roundNN/tracks/<track>/` before running anything. Flag what looks wrong in the plan without changing the instruction. Keep a current-state block at the top of the plan, so that a compacted or restarted session can resume from the plan alone, and keep tasks as checkboxes with dated notes. Anything the instruction does not cover is reported as a proposal, not done.

The instruction and the round's masterplan stay living on `main` while your track runs. When Nicolas tells you to check for updates, fetch `main`, read the dated revisions, and transcribe any change into your plan.

The root `CLAUDE.md` belongs to the oversight chat. Do not edit it and do not act on its plan. Its hard rules agree with this file.

## 2. The gate rule

In the wording Nicolas approved.

> Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

The stop conditions an instruction lists under its decision boundaries are the only exceptions to "no interim stop conditions", and a stop produces a report in the format of section 7. Inside an interval you message Nicolas only for what your instruction allows, for the four-hour queue notice of section 4, and for a setup problem that only he can clear.

## 3. How to write

Plain, natural prose. No em-dashes. No sentence that states something and then gives the explanation after a colon. No compressed or clever phrasing. Math as LaTeX, with each `$$` on a line of its own. A derivation shows every expression that carries the argument, skips only the algebra between them, and says what kind of step was skipped. Numbers are quoted at the precision the comparison needs, with the relative scale stated, and full precision stays in the files. Every number in a report is read back from the file named beside it. Do not inflate length.

## 4. Standing rules

**Evidence.**
- Silent failure is the main risk. Verify each stage's output against an expected value before moving on. Every rerun has one arm anchored to a prior result.
- Never assert a number you have not read back from a file, and recompute a derived value before you state it. Cite the path.
- Read the whole grid before writing a headline. Tabulate the quantity over every axis the experiment varied and check that the sentence holds in each cell it claims.
- When you explain a number, state the mechanism and name what in the files would contradict it, then check that.
- Before naming a term or an effect, list in writing every variable that differs between the arms of the comparison.
- Write predictions down before running, and score them afterwards as held, partly held, refuted or not tested. Do not quote a ratio whose denominator is within noise of zero.
- No claim of novelty without a documented literature check.

**Literature.**
- Never cite a paper you have not seen. Every citation carries an identifier you opened, with title, authors, year and venue read from that page, and its read level (full text, abstract only or secondary).
- Quote at most a short phrase. Summaries are in your own words.

**Where work runs.**
- Longleaf is where work runs. Never compute on the login node. The project tree is `/work/users/w/e/weiyang/hest_replication`, on `main` at tag `round4-data-v2`. Read it with `git --no-optional-locks`, and never check out, fetch or pull there. The project's Python is `/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python`, called by absolute path in every job script.
- Nothing runs on Nicolas's Mac unless he asks for that specific task in chat. Such a request goes into the plan as a numbered extension before the task runs, covers only the work it names, and does not carry across a gate. A local run records the host, the library versions, the md5 of every script and input, and the command line in place of the Slurm fields. Searching, reading, writing documents, merging citation tables, provenance bookkeeping and the numeric-claim sweep are the session's own work, not local runs.
- The Slurm accounts are `rc_htzhu_pi` and `rc_tengfei_pi`, and several tracks may share them. Keep a job ledger in your results directory. A job that has waited four hours is reported to Nicolas in chat with what it needs, and it keeps waiting. A pending job of your own may have its time limit and memory reduced with `scontrol` to a sibling's measured values, and may be switched between the two accounts. Only the lead cancels a job, and only after confirming with `squeue -u weiyang` and the ledger that it is your track's own. A sub-agent never runs `scancel`.
- Take memory and time from a sibling job's `sacct`, and set time limits at about three times the expected runtime. Put a time cap on anything that is not analysis, and stop at the cap.

**Provenance.**
- Every output directory gets `PROVENANCE.txt` (job id, partition actually used, node, date, the commit of the snapshot the job ran from, command line, config hash with its config, `PYTHONHASHSEED`, md5 of every script that ran) and is stamped with `stamp_dir()` from the `longleaf-provenance` skill, written by the job on the node. Before reusing or rebuilding any output you did not create, run `whose()` on it, and if the verdict is `sibling` or `unstamped`, ask the oversight chat through the report. Reading an input that your instruction or a committed task definition names, without rebuilding or overwriting it, needs no question. Record its `whose()` verdict in your results directory.
- The submission route replaces `--job-name`, so jobs are identified by Slurm id. Record your track's job prefix and the stage in `PROVENANCE.txt`.
- Give every parquet an explicit `pa.schema`, write summaries before bulk tables, and take seeds from `zlib.crc32`, never from `hash()`.

**What never enters the repository.** The repository is public. Papers, PDFs, figures taken from papers, HEST data packages, transcripts and credentials are never committed. Before every commit, list the staged files and check.

**Never the session's decision.** Contact with anyone outside the project. Any download of data or code. Changes to `main`, to earlier rounds' files, to the project tree's checkout, or to another track's areas. A claim of novelty. The framing, venue or authorship of a paper.

## 5. Git, code delivery and files

- Your track has its own branch, its own clone on Nicolas's Mac under `~/hest-1k`, and its own code clone on Longleaf under `/work/users/w/e/weiyang/hest_code/`, as its instruction names. Other sessions' clones are read only, with `git --no-optional-locks`. If your Mac clone is not clean, or a `.git/index.lock` is present, tell Nicolas and wait.
- GitHub sees one push per gate. At each gate you commit, tag and push the branch and the tag together, open one pull request into `main`, confirm on GitHub that it exists, put its number in the report, and stop. You never merge. Do not push again while that pull request is open. Never rebase, squash, amend after a push or force-push. A rejected gate is fixed with new commits on the same open pull request.
- Commits reach Longleaf as a git bundle, applied by a short Slurm job with `git merge --ff-only` in your code clone, which never fetches from GitHub. The same job writes a read-only snapshot of the delivered commit's `code/` directory, and every job runs from its own output directory with that snapshot on `PYTHONPATH`. Each delivery is a row of `code_deliveries.csv` in your results directory. Before each gate push, check that every commit recorded in a `PROVENANCE.txt` is an ancestor of the gate tag and that every recorded script md5 matches that commit, and commit `provenance_index.csv`. The full procedure is section 4 of `docs/round05/i02/ppi/round5_ppi_E2_decisions.md`.
- Write commit messages through a file. Each file has one writer, and parallel work writes fragments that a merge step joins, reporting any collisions.
- Do not edit `README.md`, `CLAUDE.md`, `docs/README.md`, `docs/progress-log.md`, `docs/WAYS_OF_WORKING.md`, this file, any earlier round's files, or anything outside your track's areas. Proposed edits go in the report.
- When Nicolas hands you a decision memo, commit it unchanged at the path it names on your branch, so that it merges cleanly with the copy the oversight chat has put on `main`.
- Run `code/scripts/verify_numeric_claims.py` over your documents before every handover, with your exceptions in `.verify-exceptions-<round>-<track>`.

## 6. Sub-agents

Dispatch one sub-agent per independent unit with a written brief. Put the sub-agent's frame id in the first message of its brief, with the sentence "Stamp every output directory with `stamp_dir()` from the `longleaf-provenance` skill under the frame id given in this brief. Before reusing or rebuilding any output you did not create, run `whose()` on it; if the verdict is `sibling` or `unstamped`, ask me rather than rebuilding." If the id exists only once the sub-agent is spawned, the brief says that the id follows and forbids any job before it arrives, and the id goes in the second message. Compare the id in every returned stamp with the one you assigned before merging. Sub-agents run no git command and never cancel a job. A sub-agent's request for access the brief did not grant is answered no and recorded. Mechanical work may run one model tier below yours. Derivations, verdicts and the text of reports stay with you. The lead is the only committer, checks every hand-back against its sources before committing, and recomputes every pooled number from the merged tables.

## 7. Reports

After each gate, in this order. 1. Stage and status. 2. What was run (scripts with md5s, commits, job ids, partitions, wall times, peak memory from `sacct`, and the sub-agents with their briefs). 3. Acceptance checks and exit items with the actual numbers and file paths. 4. For every comparison, the variables that differ between its arms. 5. Predictions against outcomes, as a table. 6. Results, numbers from files with paths, dispersion beside every mean, and paths in place of pasted tables over 20 rows. 7. Discrepancies, open questions and escalations. 8. What was not checked. 9. Proposed next step. Reports are frozen once handed over. Corrections go in the next report.
