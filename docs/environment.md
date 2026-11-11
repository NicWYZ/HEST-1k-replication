# Environment

Where the project's machines, clones, accounts and data are, and the quirks of each. Moved here from `CLAUDE.md` and `docs/WAYS_OF_WORKING.md` on 6 November 2026, when the record moved to the project-record skill. `CLAUDE.md` points here, and this file holds no status.

## People and accounts

- Nicolas Weiyang Zhang, Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`. He merges every pull request.
- Dr. Hongtu Zhu, the PI. Dr. Daiwei (David) Zhang, Nicolas's GRA supervisor.
- Nicolas's Claude accounts before the move he announced on 10 November 2026: a Max subscription, which held his API credits; a seat on David's Claude team account, which the Longleaf execution sessions used from 6 November; and an institutional claude.ai account with no Claude Code access. He would rather not change his local Claude Code settings when setting up runs (20 October). On 10 November he said the project is moving to another account (`docs/progress-log.md`, 10 November).
- GitHub repository `NicWYZ/HEST-1k-replication`, public. Round 9's Claude Science sessions committed as `NicWYZ <NicWYZ@users.noreply.github.com>`.

## What each kind of session can reach

- **The oversight chat** runs in the claude.ai project "Spatial Transcriptomics". In a cloud session it has only the clone it makes, no Longleaf and no data. When linked to Nicolas's Mac it reaches the clones under `~/hest-1k`. Claude Code cloud sessions cannot be linked. It pushes over HTTPS with the repository attached with push access. `gh pr create` is blocked there, but a pull request can be opened through the GitHub REST API, as #36 was on 6 November. On 8 November the cloud session's proxy still refused arXiv and OpenReview (HTTP 403 on CONNECT), the web fetch tool asked for an approval per domain that went unanswered while Nicolas was away, and a network test from the Mac's shell was refused by the session's safety check, so sources there are read through the fetch tool with Nicolas present or through the Mac's built-in browser. The built-in browser reached arXiv and JSTOR (abstract pages and search) without an approval prompt on 8 November, after Nicolas granted full internet access; JSTOR full texts still need his UNC library sign-in. Scanned PDFs are read in the cloud workspace, which has `tesseract` and `pdftoppm`; two-page spreads (Särndal et al.) are split before OCR, and every formula is checked against the page image.
- **Execution sessions** run in Claude Science or Claude Code, on Longleaf or on Nicolas's Mac with SSH to Longleaf (`Host longleaf` in `~/.ssh/config`, Nicolas, 24 October), or as Claude Code cloud sessions as in round 6. A cloud session can be reclaimed, so it pushes its branch after every batch, still with one pull request at its final gate, and Nicolas pulls the branch on Longleaf and runs its jobs from a `git archive` copy (round 6's track instruction, section 5, now in `NicWYZ/textual-st-histology`). Round 9's Claude Science sessions downloaded Longleaf outputs through the scratch root `/work/users/w/e/weiyang/.claude-science-scratch/` (other paths raise an approval card), needed Nicolas's approval for network domains outside the sandbox and for the stored OpenAlex credential once per session, and were pointed to their own clone and branch by the kickoff message, which overrides the folder the Claude Science project instructions name. `git clone` does not run inside the Claude Science sandbox on the Mac, so Nicolas created each round 9 clone there (round 9's branch `CLAUDE.md` files).
- **Round 10's final-runs sessions** ran in Claude Science on a Windows execution PC on David's team account, reaching Longleaf through the compute target `ssh:longleaf` (the track plan's state block on branch `round10-final-runs`, 11 November).
- **On the Mac.** A plain `git status` on a mounted folder can leave `.git/index.lock` behind and block the next commit there. The device shell cannot delete files without Nicolas's permission. The oversight chat commits and pushes from its cloud clone.

## Clones and trees

- **On Nicolas's Mac,** `~/hest-1k` holds `HEST-1k-replication-oversight` (the oversight clone, on `main`), `HEST-1k-replication-PPI` (rounds 4, 5 and 7, branch `round7-ppi` in round 7) and `HEST-1k-replication-conformal` (rounds 4 and 5), read only for any other session, `HEST-1k-replication-fedlearn` (round 7), `HEST-1k-Claude-Science` (branch `claude-science`), `HEST-1k-fewcluster` and `HEST-1k-newtopic` (round 9), the clone of `NicWYZ/textual-st-histology`, `acs_pums2018` (the raw census fetch, not in the repository), `r6ext_private/` (round 6's old token, the only one of the round 6 extension's folders left, checked 19 October), and the paper folders `ppi_conf_papers/` and `fedlearn_papers/`, never committed. Track fewcluster's supplied PDFs sit in a `refs` folder in its clone, which `.gitignore` keeps out.
- **Nicolas's Longleaf clone has GitHub access over SSH** (Nicolas, recorded on 8 November from his statement), so an execution session working in a clone on Longleaf can push its branch from there. Claude Science sessions create their own clones (Nicolas, 8 November).
- **On Longleaf,** the project tree `/work/users/w/e/weiyang/hest_replication` is on `main` at tag `round4-data-v2` and is the data root (`MANIFEST.md`, `bench_data/INVENTORY.md`). Read it with `git --no-optional-locks` and never check out, fetch or pull there. The project's Python is `/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python`. Tracks' code clones are under `/work/users/w/e/weiyang/hest_code/` (for example `round7-ppi/`, `round7-fedlearn/`). Round 9 wrote its outputs under `/work/users/w/e/weiyang/hest_replication/results/round9/`, in a folder per branch's work (`claude_science`, `fewcluster`, `newtopic`).
- **Elsewhere.** The HEST-1k benchmark data are gated (`MahmoodLab/hest-bench`) and never enter the repository. Round 6's record, scripts, results, data package and transcripts live in the private repository `NicWYZ/textual-st-histology` (called `NicWYZ/hest-r6-data` until 19 October). The private versions of round 7's overlap check and round 8's working notes are claude.ai project docs (`claude/round07_overlap_check_full.md`, `claude/round08_positioning_working_notes.md`).

## What a new account must recreate

- The claude.ai project "Spatial Transcriptomics" and the Claude Science project, each with the instructions in `docs/project_instructions.md`.
- The skill `project-record`, and the skill `longleaf-provenance` for execution sessions.
- Access to Longleaf under ONYEN `weiyang`, and GitHub push access to `NicWYZ/HEST-1k-replication`.
- The claude.ai project's 24 docs, which Nicolas re-adds to the new project from `~/hest-1k/claude_project_docs/` on his Mac. That folder is outside every clone, because some of the docs hold details of unpublished manuscripts (hard rule 8). It was filled on 10 and 11 November: 21 docs were typed out again by the oversight chat from what the Projects tool showed, so they are not checked byte for byte, and Nicolas copied the other 3 by hand.

## Longleaf scheduler notes (account `rc_htzhu_pi`)

**A small CPU job's priority here is effectively fixed. There is no lever; plan around the wait.**
`sprio` decomposes it: for a 4-core CPU job, 182 = age 0 + fairshare 4 + partition 177. The cluster
config explains why none of that moves:

```
PriorityWeightAge = 1000    PriorityMaxAge = 60-00:00:00
PriorityWeightFairShare = 2000    PriorityWeightPartition = 10000
```

Age is normalised by `PriorityMaxAge`, so **one hour of queue age is worth about 0.7 points and a
full day about 17**, against a baseline of 182 that the partition factor dominates. Fairshare
contributes 4 of 182 at this account's usage (0.0022 against RawUsage 4.8M), and it drifts *down*
as the account runs jobs.

Two consequences, the second of which corrected an earlier note in `docs/WAYS_OF_WORKING.md`:

- Shortening a wall to chase backfill does not work. Measured in round 2: identical jobs went from
  starting within a minute to pending for over 90 minutes with no wall change, and a 2 h → 50 min
  reduction did not help but did kill an encoder at the limit (`exit_code 143`). Ask for the wall
  the work needs. Both `general` and `spill` allow `MaxTime=11-00:00:00`, so a generous wall costs
  nothing.
- Cancelling and resubmitting does **not** meaningfully reset priority, because there was almost no
  age to lose. An earlier version of this note claimed it did, inferred from a single
  resubmit-then-long-wait sequence; the config shows that inference was wrong, and the long wait was
  cluster load rather than anything the resubmission caused. Resubmit freely when the code needs
  fixing — just do not expect resubmitting to *help*, and do not resubmit a job that is merely slow.

What still holds: if a stage is too long for one job, split it by unit and submit the pieces
together, because that is about wall-clock and failure isolation rather than priority.

**Correction, round 3: in the fairshare regime the group is now in, the time limit is the lever,
and a generous wall is not free.** The first bullet above says shortening a wall to chase backfill
does not work, and a generous wall costs nothing. That was measured in round 2 and it is wrong now.
With the group's fairshare on `rc_htzhu_pi` at about 0.007, a job starts early through backfill or
it does not start early at all, and a long limit is exactly what makes a job unschedulable in a
backfill window. In A3 the five A2 jobs still pending after 2 h 40 min had been submitted with 16 h
limits; lowering the limits in place to 3 h, bounded from a sibling job's measured runtime, started
all five within minutes, with nothing about the jobs' work, resources or seeds changed
(`docs/round03/i02/exec/round3_A3_stage_report.md` section 2, `docs/round03/i03/exec/round3_A3_decisions.md` section 3.5).
So: size the Slurm `--time` at about three times the expected runtime, take the expectation from a
sibling's `sacct` rather than from intuition, smoke-test first when there is no sibling to measure,
and never submit a blanket 16 h. The submission harness's own `run_timeout_s` is the opposite case
and is unchanged — it counts queue time, so it stays generous.

**The submission harness has its own clock, and it counts queue time.** `run_timeout_s` is
measured from submission, not from the job starting, and when it expires the harness cancels the
Slurm job. In round 2 a two-minute D3/D4 check was submitted with a 2 h ceiling, waited longer than
that in `PENDING`, and was killed before it ever ran (`error_kind: timeout_ceiling`, no outputs)
while its siblings with 10 h and 25 h ceilings survived the same wait. Set the ceiling from
**expected queue time plus runtime**, not from runtime; on this cluster that means hours even for
a job that computes for seconds. The Slurm `--time` wall is a separate limit and should still be
sized to the work.

**Record the partition the job actually ran on.** Jobs requesting `general` routinely land on
`spill`. `$SLURM_JOB_PARTITION`, not the request, belongs in provenance.

**`-p` is a request, not a destination, and the rerouting is driven by the memory ask.** Measured
in round 2: nine jobs submitted with `#SBATCH -p general_big` landed as five on `spill`, three on
`general` and only one on `general_big` — the one asking for 96 GB. The 48 GB and 64 GB jobs were
rerouted. So `general_big` is reachable only by asking for memory in the hundreds of GB.

**Do not inflate a memory request to reach an emptier partition.** It is available capacity on
1.5 TB nodes where memory, not cores, is the scarce resource, so an inflated ask displaces jobs that
genuinely need those nodes. When `general` is saturated (round 2 saw 18,294 pending against 4,569
running, with 5,320 cores idle but no schedulable memory), the honest options are to wait, to ask
the PI about an account with better fairshare, or to cut the work — not to misreport what the job
needs.

**Size memory from `sacct`, not from a guess.** `sacct -o MaxRSS --units=G` on the completed R1
encoder jobs gives a peak of **16.7 GB**, most between 11 and 13 GB, for the head-fitting stages
over this benchmark (largest task 74k spots x 1536-dim embeddings). Round 2's R1b and R3 were
requested at 48-64 GB, which is a 3-4x over-ask; 32 GB with the float64 arms would be honest. An
over-ask does not slow scheduling much here — priority dominates — but it does make the job fit
fewer backfill gaps, so right-size at submission rather than after.

**Do not compute on the login node.** Its system python has no pandas or pyarrow, and a monitoring
daemon kills work there. Send inspection through the scheduler like everything else.

**Longleaf is where work runs. Nothing runs locally unless Nicolas asks for that specific task.**
In round 4 both tracks moved simulation and post-processing work to Nicolas's laptop while the queue
was full, each time on his instruction in chat. The oversight memos then disagreed with the sessions
about whether that permission carried into the next interval, one sub-agent read a notice about it as
an order to stop, and partial local outputs had to be quarantined when units moved back. The rule
that came out of it has four parts. Every job runs on Longleaf through Slurm by default. A local run
needs Nicolas to ask for it in chat, and the request is written into the operating plan as a numbered
extension before the task runs. A permission covers the work it names and does not carry across a
gate unless he says so again. And a local run records the host, the library versions, the md5 of
every script and input, and the command line in its `PROVENANCE.txt`, in place of the Slurm fields.

**A job that has waited four hours is reported to Nicolas in chat, and it keeps waiting.** The
session says what the job needs (its inputs and their sizes, memory, expected runtime and the state
of the queue). It does not move the job to another site or copy its inputs elsewhere on its own.
Two things are allowed and are recorded in the job ledger. A pending job's time limit and memory may
be reduced with `scontrol` to a sibling's measured values, which is the round-3 backfill lesson
applied in place. And a pending job may be switched between the group's two approved accounts,
`rc_htzhu_pi` and `rc_tengfei_pi`.

**Run a job from its own working directory, never from inside the code clone.** Several round-4
job scripts changed directory into `code/scripts/` of the track's Longleaf clone and left dozens of
untracked output files there, which had to be moved out by a separate job before the clone was clean
again. The clone goes on `PYTHONPATH`. The job's working directory is its output directory.

## Watching a job on Longleaf

`sacct` `TotalCPU` reads `00:00:00` for running jobs on this cluster, so it cannot tell a working job from a hung one. Use `srun --jobid=<id> --overlap -n1 ps -eo pid,etime,time,pcpu,rss,args` and read the process's own `TIME` and `%CPU`. Never pipe a long job's output through `tail`, which hides all progress until the process exits. Let stdout go to the log and `tail` the file.

## A data quirk. HEST patient labels

**Audit a grouping variable against something outside the dataset before grouping by it.** Every
term in this project that separates "same X" from "different X" is only as good as the column that
says which X a sample belongs to, and HEST's `patient` field is wrong in both directions. In COAD
it collapses three distinct patients into one label and leaves a fourth sample unlabelled, so the
shipped patient split does not separate patients at all and the per-task term computed on it cannot
be read as a patient effect -- it was round 2's largest such term and was reported as a striking
same-patient result before the labels were checked. In IDC it does the mirror image: two samples
carry different patient labels and are sections of one specimen from one donor, which the
originating vendor's own page states. In READ the labels are right but understate themselves, since
each pair is a replicate of one specimen rather than merely one patient. Nothing in the files
reveals any of this; it took reading the upstream issue tracker, the GEO subseries strings and the
vendor dataset pages. The audit is now a stage of its own (`R5b_audit`), its verdicts carry a
`donor_label_status` column rather than being assumed, and nine of the 72 samples are recorded as
unverifiable rather than inferred. Budget for it: the audit found something in three of the ten
tasks, and two of the three findings invalidated a number already written down.

## Several sessions on one repository

**One working copy per session, locally and on Longleaf.** A git working copy has one checked-out
branch, so two sessions sharing one decide for each other what is checked out. Round 4 ran two
tracks at once. Each had its own local clone and its own code clone on Longleaf, on its own branch,
with disjoint result directories. The Longleaf project tree stayed on `main` at the round's starting
tag as the data root, and nobody checked out a branch there.

**Reading another session's clone can break it.** A plain `git status` in the PPI session's clone,
run by the oversight chat, left a stale `.git/index.lock` that would have blocked that session's next
commit. Read another clone's files directly, or read its branch from your own clone after a fetch
with `git show origin/<branch>:<path>`. If git must be run in a clone that is not yours, use
`git --no-optional-locks` and nothing that writes.

**A file too large for GitHub is committed compressed, with the md5 of the plain file recorded.**
The plain file stays at the same path in the Longleaf project tree, and the report says so.
