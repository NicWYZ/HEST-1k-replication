# Environment

People, the cluster, the data, and what the project needs that the repository cannot hold. This file holds no status.

## People

- **Nicolas Weiyang Zhang,** Longleaf ONYEN `weiyang`, with Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`. He merges every pull request.
- **Dr. Hongtu Zhu,** the PI. **Dr. Daiwei (David) Zhang,** Nicolas's GRA supervisor.

## What a session needs

| Need | Required for |
|---|---|
| GitHub access with push to `NicWYZ/HEST-1k-replication` (public) | every session |
| Longleaf SSH access as `weiyang` | execution tracks |
| The `project-record` skill for the oversight session and the `longleaf-provenance` skill for execution sessions | keeping the record, opening and closing rounds, stamping outputs on Longleaf |
| Supplied papers in Nicolas's folder `~/hest-1k/ppi_conf_papers/` (and `fedlearn_papers/` for round 7), never committed | literature reads |
| The private folder for full checks on unpublished manuscripts, `~/hest-1k/claude_project_docs/` on Nicolas's machine, outside every clone `[proposed]` | hard rule 8 |

The full checks of round 7's overlap check and round 8's working notes are in that private folder, as are the other private documents the oversight session wrote.

## Clones and trees

- **On Longleaf,** the project tree `/work/users/w/e/weiyang/hest_replication` is on `main` at tag `round4-data-v2` and is the data root (`MANIFEST.md`, `bench_data/INVENTORY.md`). Read it with `git --no-optional-locks` and never check out, fetch or pull there. The project's Python is `/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python`. Tracks' code clones are under `/work/users/w/e/weiyang/hest_code/`, and their bulk outputs under `/work/users/w/e/weiyang/hest_replication/results/round<N>/<track>/`. The federated project's corpus, read only, is under `/work/users/w/e/weiyang/st_fed_learn/data/`.
- **Each session works in its own folder on its own branch.** A git working copy has one checked-out branch, so two sessions sharing one decide for each other what is checked out. Another session's folder is read directly or through `git show origin/<branch>:<path>` from your own clone, and if git must run there, with `git --no-optional-locks` and nothing that writes, since a plain `git status` once left a `.git/index.lock` that would have blocked that session's next commit.
- **Elsewhere.** The HEST-1k benchmark data are gated (`MahmoodLab/hest-bench`) and never enter the repository. The raw ACS PUMS 2018 fetch is kept outside the repository. Round 6's record, scripts, results and data live in the private repository `NicWYZ/textual-st-histology`, and the federated learning line of round 7 in `NicWYZ/ST-Fed-Learn`.
- **A file too large for GitHub is committed compressed, with the md5 of the plain file recorded.** The plain file stays at the same path in the Longleaf project tree, and the report says so.

## Longleaf scheduler notes (account `rc_htzhu_pi`)

**A small CPU job's priority is effectively fixed, and the time limit is the lever.** `sprio` for a 4-core CPU job reads about 182, almost all of it the partition factor (`PriorityWeightAge = 1000`, `PriorityMaxAge = 60-00:00:00`, `PriorityWeightFairShare = 2000`, `PriorityWeightPartition = 10000`), so one hour of queue age is worth about 0.7 points and a full day about 17. With the group's fairshare low, a job starts early through backfill or not at all, and a long limit is what makes it unschedulable in a backfill window. In round 3, five jobs pending after 2 h 40 min with 16 h limits all started within minutes once their limits were lowered in place to 3 h, bounded from a sibling's measured runtime (`docs/round03/i02/exec/round3_A3_stage_report.md`, section 2). So size `--time` at about three times the expected runtime, taken from a sibling's `sacct`, smoke-test first when there is no sibling, and never submit a blanket 16 h. Cancelling and resubmitting does not reset priority meaningfully, since there is almost no age to lose, so resubmit when the code needs fixing but not to help a slow job. A stage too long for one job is split by unit and the pieces submitted together.

**A submission harness may have its own clock that counts queue time.** Where it cancels the job when its timeout expires, set that ceiling from expected queue time plus runtime, which means hours even for a job that computes for seconds. In round 2 a two-minute check with a 2 h ceiling was killed in `PENDING` before it ran. The Slurm `--time` is a separate limit, sized to the work.

**Record the partition the job actually ran on.** Jobs requesting `general` routinely land on `spill`, so `$SLURM_JOB_PARTITION`, not the request, goes in provenance. `-p` is a request, rerouted by the memory ask: in round 2 nine jobs submitted to `general_big` landed as five on `spill`, three on `general` and one on `general_big`, the one asking for 96 GB.

**Do not inflate a memory request to reach an emptier partition,** since an inflated ask displaces jobs that need the large-memory nodes. When `general` is saturated, wait, ask the PI about an account with better fairshare, or cut the work. Size memory from `sacct -o MaxRSS --units=G` on a sibling: the head-fitting stages over the benchmark (largest task 74k spots by 1536-dimension embeddings) peak at 16.7 GB, most between 11 and 13 GB.

**Do not compute on the login node.** Its system Python has no pandas or pyarrow, and a monitoring daemon kills work there.

**Run a job from its own output directory, never from inside the code clone,** which otherwise fills with untracked outputs that a separate job has to move out.

**Watching a job.** `sacct` `TotalCPU` reads `00:00:00` for running jobs, so it cannot tell a working job from a hung one. Use `srun --jobid=<id> --overlap -n1 ps -eo pid,etime,time,pcpu,rss,args` and read the process's own `TIME` and `%CPU`. Never pipe a long job's output through `tail`, which hides all progress until the process exits. Let stdout go to the log and `tail` the file.

## A data quirk: HEST patient labels

**Audit a grouping variable against something outside the dataset before grouping by it.** HEST's `patient` field is wrong in both directions. In COAD it collapses three distinct patients into one label and leaves a fourth sample unlabelled, so the shipped patient split does not separate patients, and the per-task term computed on it, round 2's largest, was reported as a striking same-patient result before the labels were checked. In IDC two samples carry different patient labels and are sections of one specimen from one donor, as the vendor's page states. In READ the labels are right but each pair is a replicate of one specimen. Nothing in the files reveals this; it took the upstream issue tracker, the GEO subseries strings and the vendor pages. The audit is a stage of its own (`results/round2/R5b_audit/`), its verdicts carry a `donor_label_status` column, and unverifiable samples are recorded as such rather than inferred. The audit found something in three of the ten tasks, and two of the three findings invalidated a number already written down. Round 10's audit of the federated corpus found the same kind of error, where a blank `patient` gave a whole study one donor (`docs/round10/README.md`).
