# Round 11, track `closeout`, the plan

```state
updated: 2026-11-16, evening (first session of track closeout)
unit: closeout
project_id: proj_8450e231133d
frame_id: c9016697-c909-435e-82fc-ebfb9daaa857
step: A0 (inventory) and A1 (literature search) in hand; no Longleaf job submitted yet
last_run: none
jobs: none
next: finish the inventory of embeddings, prediction files and task definitions on Longleaf with whose() verdicts (results/round11/closeout/inventory/); log the literature search (results/round11/closeout/lit/); then the anchors (A2) and the designation of the primary predictor (A3) in this plan before any held-out result of a new predictor is read
waiting: none
```

*Written on 16 November 2026 by the first session of track `closeout` (frame above). The brief is `docs/round11/closeout/round11_closeout_brief.md` on `main`, read at `7ff4e2fc`, with `docs/round11/masterplan.md` at the same commit and `docs/EXECUTION_RULES.md` as it stands there. The branch starts from `7ff4e2fc`. This plan links the brief and does not copy it.*

## 1. What was read at the start

`docs/EXECUTION_RULES.md`, the brief, the masterplan, `docs/round11/README.md`, `docs/round10/README.md` (the last closed round's summary), `docs/round10/round10_methods_note.md`, `docs/round10/i05/final-runs/round10_final_runs_report.md`, `docs/environment.md`, `docs/WAYS_OF_WORKING.md`, and the head of `docs/round10/tracks/final-runs/round10_final_runs_plan.md` for how round 10 ran its jobs. Longleaf is reachable by SSH as `weiyang` (alias `longleaf`); on 16 November neither `/work/users/w/e/weiyang/hest_code/round11-closeout/` nor `/work/users/w/e/weiyang/hest_replication/results/round11/closeout/` existed, and no job of `weiyang` was in the queue.

**On the brief.** Nothing in it looks wrong so far. One reading is recorded: section 6 asks for coverage of HCP "as `inst_fr8.csv` was produced" at nominal 0.80, while the headline table's level is 0.90 elsewhere; the track follows the brief and runs the institution axis at 0.80 only.

## 2. How every job runs

As round 10's final runs did (`docs/round10/tracks/final-runs/round10_final_runs_plan.md`, section 3), with this track's paths.

- **Code.** Scripts `code/scripts/round11_closeout_*.py` are written in this worktree, committed on `round11-closeout`, pushed, and fetched into the clone `/work/users/w/e/weiyang/hest_code/round11-closeout/` (created by this track). Round 10's scripts are imported read only from the same snapshot.
- **Snapshot.** Each job runs from a read-only `git archive <commit> code` under `/work/users/w/e/weiyang/hest_replication/results/round11/closeout/_snapshots/<commit>/`, with that `code/` on `PYTHONPATH`, from its own output directory, with the project's Python by absolute path. Each delivery is a row of `results/round11/closeout/code_deliveries.csv`.
- **Provenance.** On the node each job writes `PROVENANCE.txt` (Slurm id, `$SLURM_JOB_PARTITION`, node, date, snapshot commit, command line, config with its sha256, `PYTHONHASHSEED=0`, md5 of every script and input) and the `_provenance.json` stamp from `provenance_shell_snippet()` with the project and frame ids of the state block, track `closeout`. Seeds from `zlib.crc32`, explicit `pa.schema`, summaries before bulk tables.
- **Inputs.** Every input not made by this track gets a `whose()` verdict in `results/round11/closeout/inputs_whose.csv`. Round 10's outputs carry project `proj_8450e231133d` under other frames, so they read `foreign_session`; reading them as inputs the brief names needs no question, and nothing of theirs is rebuilt or overwritten.
- **Job ledger.** `results/round11/closeout/job_ledger.csv`, one row per Slurm job, with `sacct` wall and MaxRSS. Time limits at about three times a sibling's measured runtime, memory from a sibling's `sacct`. Four hours pending is reported to Nicolas, and the job keeps waiting.
- **Repository.** Only aggregates under `results/round11/closeout/`. Staged files listed and checked before every commit; the two round 1 directories with `::` in their names are never staged.
- **Numbers.** `code/scripts/verify_numeric_claims.py` over every report, exceptions in `.verify-exceptions-round11-closeout`. Before each gate a fresh sub-agent recomputes the report's table numbers.

## 3. Gates

- **G1** only if the no-download rule stops Part A (brief, section 4).
- **G2, the stronger predictor.** After the inventory, the logged literature search, the anchors (A2), the designation of the primary predictor (A3) and its donor-held-out spot-level Pearson beside round 10's ridge on kidney Visium, bowel Visium and LUNG_XENIUM, which scores P11.1. Report `docs/round11/closeout/round11_closeout_G2_report.md`, tag `round11-closeout-G2`. Reason: whether the predictor is stronger decides whether the rest of Part A runs (brief, section 4, standard 5), and so is a significant result.
- **G-final.** As the brief's section 6 sets it, report `docs/round11/closeout/round11_closeout_report.md`, tag `round11-closeout-G-final`, one pull request into `main`.

Part B items that need no new predictor (1, 3, 5, 6, 7) may run before G2 and are reported at G2 if done; item 2 (H1(b) refits) and item 4 run when their turn comes and may straddle G2.

## 4. Part A, tasks

- [ ] **A0. Inventory.** Embeddings (encoder by task), prediction files, task definitions and gene lists on Longleaf, with `whose()` verdicts, in `results/round11/closeout/inventory/`. Includes the federated corpus's donors of the same organ and platform beyond each task's audited donors, and whether neighbour coordinates are available for spatial context.
- [ ] **A1. Literature.** Sub-agents search published benchmarks of histology-to-expression prediction for the strongest approaches, and any report of donor-level accuracy; the queries and verdicts logged in `results/round11/closeout/lit/`. Read levels and identifiers per `docs/EXECUTION_RULES.md`, section 4.
- [ ] **A2. Anchors.** Refit round 10's `uni_v2` ridge head and reproduce the brief's three anchor cells (section 4, standard 1) within the stated tolerances. Predictions for this stage written here before it runs.
- [ ] **A3. The primary predictor,** with its tuning rule, designated here before any held-out result of a new predictor is read.
- [ ] **A4. Stage predictions** with numbers, here, before the first run of each stage.
- [ ] **A5. Strength.** Donor-held-out median spot-level Pearson with fold spread for every predictor run, beside the ridge on the same inputs (standard 4). Scores P11.1. Gate G2.
- [ ] **A6. The same quantities** (standard 6) for each new predictor, after G2 if P11.1 holds.
- [ ] **A7. Pretraining overlap** statements for each encoder used.

## 5. Part B, tasks

- [ ] **B1.** Fresh sub-agent recomputes the headline table of brief section 3.
- [ ] **B2.** H1(b) refits under `random`, `slide_out`, `donor` and a center design.
- [ ] **B3.** S0006 on `uni_v2` lognorm, from existing prediction files.
- [ ] **B4.** Equal allocation for regime B on ACS by state.
- [ ] **B5.** Within-cluster variance equality on ACS by state and the HEST tasks.
- [ ] **B6.** D12's share and round 9's E1 box numbers stored, or declared unquotable.
- [ ] **B7.** Round 10 jobs without a provenance file, from `sacct`.

## 6. Decisions

None yet.

## 7. Tried and failed

None yet.
