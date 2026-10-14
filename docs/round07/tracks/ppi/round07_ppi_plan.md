# Round 7, the inference track, operating plan

Living document. Written 14 October 2026 by the execution session and approved by Nicolas the same day, from `docs/round07/i01/ppi/round07_ppi_track.md` at the starting commit. Section 9 is section 7 of the track document transcribed unchanged. Sections 1 to 8 say how I will carry it out. Nothing in this plan changes the track document. Where the two differ, the track document holds and the difference is a mistake in this plan.

## 0. Current state

| field | value |
|---|---|
| stage | S0 complete. S1.1 (theory sections 1 and 2.1) and S1.2 (synthetic test, run 2) done, Broska and Howes's checks pass. S1.3 runs being fanned out |
| starting commit | `c2af4630fe601c255c927d2a3f5a76b19a53d9f2` (13 October 2026, "Docs: open round 7's inference track after O2 was accepted") |
| `origin/main` when read | `690b999b99460e5d341edc6aeba3f1d01a99c93f` (merge of pull request #28, `round7-fedlearn`). The track document has no later revision there |
| track document revisions transcribed | the two lines dated 13 October 2026 (first version, and the revision before handover) |
| branch | `round7-ppi` from `c2af4630` |
| Longleaf code clone | `/work/users/w/e/weiyang/hest_code/round7-ppi/`, made by Slurm job 4816458 |
| last delivered commit | `ba3129e41d6557f29c56b7a020d73ef9d4c7edbd` (delivery 4, Slurm job 4824339) |
| open pull request | none |
| plan extensions | none |
| escalations recorded for the next report | none |
| next action | S1.3, seven sub-agent units (six tasks, one simulation) on snapshot `ba3129e` |

A restarted session resumes from this block, the job ledger `results/round7/ppi/r7ppi_slurm_jobs.csv` and `results/round7/ppi/code_deliveries.csv`.

## 1. Starting point and preconditions

The starting commit is the one that carries the first version of the track document. `git log` on `origin/main` shows a single commit touching the document, `c2af4630`, and both revision lines are already in it. `main` has since moved to `690b999b` with the federated learning track's F2 merge. I branch from `c2af4630`, as the document says, and not from the current tip.

Checked on 14 October 2026 in `~/hest-1k/HEST-1k-replication-PPI` before writing this plan.
- The clone is on `round5-ppi` and its working tree is clean. No `.git/index.lock` is present.
- `git fetch origin main` succeeded. Writes inside `.git` succeed. The sandbox printed a warning that git protection runs in a coarse mode because the granted folders hold several repositories. I record it here in case a later git write is refused.
- At the starting commit the five scripts of the section 3 table have the recorded md5s (`round5_ppi_estimator.py` `2de31569ffe72239062fbeb0c9a50fc5`, `round5_ppi_twolevel.py` `e13183a4ffdddf4f01ba5136844c606d`, `round5_ppi_balance.py` `d78b654d7fd8e6a824f73dd50ee2a0c1`, `round5_ppi_e4b_rejective.py` `059c18e1b4998b1ac9c9685ba324a872`, `round5_ppi_common.py` `122375c3acb103ed93e3e687644d7f6d`).
- The two anchor rows exist in `results/round5/ppi/E4b_rejective/e4b_rej_width_ratios.csv`. `CCRCC`, `uni_v2`, $\theta_3$, `own`, $p_a = 0.01$, $n_L = 8$ has `wr_D0cl` 0.7262961344734262. `ACS_STATES`, `package`, same cell, has 0.5512905600386501. To four decimals these are 0.7263 and 0.5513, the values the track document quotes.
- Longleaf answers. `hest_code/round7-ppi/` and `hest_code/round7-ppi_snapshots/` do not exist. The project tree `/work/users/w/e/weiyang/hest_replication` is on `main` at tag `round4-data-v2` (`9d7277dc8c4bfade08d5895051666ee134b8396a`), read with `git --no-optional-locks`. `squeue -u weiyang` listed no jobs.

Not yet in place.
Both were missing when the plan was written and are now in place. Nicolas granted read-only access to `~/hest-1k/ppi_conf_papers/`, which holds `cluster_ppi.pdf`, `kluger.pdf` and `balanced_active_inference.pdf`. The `longleaf-provenance` skill is loaded.

### 1.1 What the S0 reading found, and how I handle it

1. **Which code wrote the anchors.** Both anchor rows come from the E4b run of round 5, jobs 4382135 (`CCRCC`, `uni_v2`) and 4382108 (`ACS_STATES`, `package`), at snapshot `9185bc6be157ee9c62d8d1067e5ad9e14f53984e`, with `round5_ppi_e4b_rejective.py` of md5 `228972e745a16ad91b5a368600e6acda` (`results/round5/ppi/E4b_rejective/CCRCC/uni_v2/theta3_nL8/PROVENANCE.txt` and the `ACS_STATES` counterpart). The script at the starting commit has md5 `059c18e1b4998b1ac9c9685ba324a872`, from commit `b410529`, which computes the pool threshold in float64 instead of float32 and halves the column chunk of that computation, which does not change its result. Nothing else differs. E5 did not rerun these cells. So "round 5's E5 cells" are read as these E4b cells, and arm 1 runs the E4b script from this track's own snapshot of the starting commit with round 5's seeds, which are fixed inside the script. `wr_D0cl` is the median over genes of the `rej_t` width over the D0 classical width, from the gene rows with all 2,000 draws (`round5_ppi_e4b_merge.py`), and S0 computes it the same way.
2. **The fixed thresholds.** `results/round5/ppi/E4b_rejective/_threshold/` on Longleaf holds, per task and arm, only the median over genes of each threshold (`round5_ppi_e4b_threshold.py` at `0776327`). With own balance every gene has its own design and threshold, so the median cannot serve as the threshold. The per-gene thresholds are deterministic, since they are the $p_a$ quantiles over a pool of seeded candidates (`pool_thresholds` in `round5_ppi_e4b_rejective.py`). So the new code recomputes them with round 5's pool function and candidate seeds, writes them to a file per cell, and checks that their median equals `thr_E4b_median` in `_threshold/` up to the float32 rounding of the old code. Those per-gene values are D2's fixed thresholds for every later draw and for $\hat\pi_g$. This is a choice between equivalent implementations, recorded as an escalation in the S2 report.
3. **The tolerance for arm 2.** Arm 2 draws new accepted samples, so its width ratio differs from round 5's by Monte Carlo error in both. Each arm's standard error is a bootstrap over its 2,000 draws (500 replicates, resampling draws jointly for all genes, crc32 seeds), and arm 2 passes if the difference from round 5's value is within two standard errors of the difference, $\sqrt{se_1^2 + se_2^2}$, with $se_1$ taken from arm 1's rerun of round 5's draws.
4. **The runner.** Every job of this track runs through a new `code/scripts/round7_ppi_run.py`, adapted from `round5_ppi_run.py`, which executes a script from a snapshot and writes `PROVENANCE.txt` with every field of section 4 of the track document, including the config and its hash, the intended prefix `r7ppi_`, the stage and the owning frame id. The `_provenance.json` stamp is written by the job script on the node from the `longleaf-provenance` skill's payload.

## 2. Areas and files I write

Only these. Branch `round7-ppi`. Scripts `code/scripts/round7_ppi_*.py`. Results `results/round7/ppi/<STAGE>/` with `<STAGE>` one of `S0_anchors`, `S1_weighting`, `S2_comparators`, `S3_adaptive`, `S4_kcenter`. Track-level files `results/round7/ppi/r7ppi_slurm_jobs.csv`, `results/round7/ppi/code_deliveries.csv`, `results/round7/ppi/provenance_index.csv`. The exceptions file `.verify-exceptions-round7-ppi`. The documents of section 5 of the track document, at the names it gives. Decision memos Nicolas hands me, committed unchanged at the paths they name.

I do not edit `README.md`, `CLAUDE.md`, `docs/README.md`, `docs/progress-log.md`, `docs/WAYS_OF_WORKING.md`, any earlier round's files, or anything of the federated learning track. I run no git command in any other clone under `~/hest-1k`. On Longleaf I read the project tree only with `git --no-optional-locks` and never check out, fetch or pull there.

## 3. S0 step by step

1. **Reading.** The track document (done for this plan), `docs/WAYS_OF_WORKING.md`, `docs/round07/00_prep/round07_overlap_check.md`, `docs/round07/oversight/round07_ppi_positioning.md`, `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`, section 3 of `docs/round05/tracks/ppi/round5_ppi_theory.md`, and section 4 of `docs/round05/i02/ppi/round5_ppi_E2_decisions.md`. I also read the E4b scripts and the E5 memo far enough to know which script and which seeds produced the anchor rows.
2. **Branch.** In the PPI clone, `git switch -c round7-ppi c2af4630fe601c255c927d2a3f5a76b19a53d9f2`. `round5-ppi` is left as it is. The first commit adds this plan and the empty ledgers, with the message written through a file.
3. **Longleaf code clone.** One short Slurm job (about 10 minutes requested, 1 GB) clones `git@github.com:NicWYZ/HEST-1k-replication.git` over the SSH key on Longleaf into `/work/users/w/e/weiyang/hest_code/round7-ppi/`, creates the local branch `round7-ppi` at `c2af4630` and checks it out, and prints its HEAD. After this job the clone never contacts GitHub again. I first confirm that the target path does not exist, and stop to ask if it does.
4. **First delivery.** `git bundle create` from `c2af4630` to `round7-ppi`, copied to Longleaf with the job's inputs. A short Slurm job runs `git bundle verify`, `git fetch <bundle> round7-ppi` and `git merge --ff-only FETCH_HEAD` in the clone, writes `git archive <commit> code` to `/work/users/w/e/weiyang/hest_code/round7-ppi_snapshots/<full hash>/`, removes write permission from it, and prints the md5 of every script in the section 3 table as found in the snapshot. I check those against the table. The delivery becomes the first row of `code_deliveries.csv` (date, job id, HEAD before and after, bundle md5, commits carried, snapshot path).
5. **Anchor, arm 1 (round 5 code).** From the first snapshot, rerun with round 5's script and round 5's seeds the cells that produced the two anchor rows, which are written by the E4b run, and confirm `wr_D0cl` to four decimals: 0.7263 for `CCRCC` with `uni_v2` and 0.5513 for `ACS_STATES` with `package` ($\theta_3$, own balance, $p_a = 0.01$, $n_L = 8$). The track document calls these "round 5's E5 cells". If reading shows that E5 reran them with its own seeds, I use E5's script and seeds and say so. Memory and time come from the `sacct` of the round 5 job that produced each row.
6. **Anchor, arm 2 (new code).** A new script `code/scripts/round7_ppi_d2.py` that builds D2 as section 2.3 defines it (round 5's fixed thresholds, candidates drawn until one is accepted, never the fallback of `d2_select`), importing the round 5 modules unmodified. It reruns the same two cells. Match is judged within the Monte Carlo error of 2,000 draws, which I take as two Monte Carlo standard errors of the width ratio, the error estimated by a bootstrap over draws and written beside the ratio.
7. **Outputs.** `results/round7/ppi/S0_anchors/s0_anchors.csv` with, per anchor and arm, the task, arm, cell, target value, reproduced value, Monte Carlo error, tolerance and pass flag, plus `PROVENANCE.txt` and the stamp in every output directory.
8. **Stop rule.** If an anchor fails, I make one fix and rerun. If it still fails, I stop and write a report in the format of section 9 of the track document.

S0 is capped at one day. Expected Slurm use is four short jobs (clone, delivery, two anchor arms, the arms possibly as one job per task).

## 4. How every job runs

- Submitted by the Longleaf route of round 5, with an explicit `#SBATCH --mem` in every job script, since the route's default of 1 GB has caused out-of-memory failures before. Memory and time from a sibling's `sacct`, time limits at about three times the expected runtime.
- The project's Python by absolute path, `/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python`.
- Each job runs from its own output directory with the snapshot's `code/scripts` on `PYTHONPATH`. No script runs from the clone or is copied loose.
- `PROVENANCE.txt` with job id, partition actually used, node, date, snapshot commit, command line, config and its hash, `PYTHONHASHSEED`, the md5 of every script that ran, and the intended prefix `r7ppi_` with the stage. Every output directory is stamped with `stamp_dir()` on the node.
- Every job is a row of `r7ppi_slurm_jobs.csv` when it is submitted, and gets its `sacct` fields when it ends.
- Seeds from `zlib.crc32` of a string `r7ppi|<stage>|<task>|<cell>|<purpose>`, so that seeds for $\hat\pi_g$ are disjoint from every evaluation draw. E5's seeds are used for the first 2,000 draws wherever a cell repeats E5.
- Parquets with an explicit `pa.schema`. Summaries written before bulk tables.
- A job pending for four hours is reported to Nicolas in chat and keeps waiting. I may lower a pending job's limits with `scontrol` to a sibling's measured values or move it between `rc_htzhu_pi` and `rc_tengfei_pi`. I cancel only my own jobs, after checking `squeue -u weiyang` against the ledger.
- Nothing runs on the Mac apart from git, copying results back, and the numeric-claim sweep of my own documents before a handover.

## 5. Fan-out

| stage | units | who |
|---|---|---|
| S0 | none, the lead does it | lead |
| S1 | six task units (`CCRCC`, `CCRCC_merged`, `INDIANA_KIDNEY`, `LUNG_XENIUM`, `ACS_STATES`, `ACS_CA_PUMA`) and one simulation unit | sub-agents for the runs, the lead for the theory section and the synthetic test |
| S2 | the same six task units and one simulation unit | sub-agents for the runs, the lead for the theory section and both Broska and Howes checks |
| S3 (if the S2 memo keeps it) | six task units and one simulation unit | the lead implements and tests the cube method, sub-agents run |
| S4 (if kept) | four tissue task units | sub-agents |

Each brief carries the sub-agent's frame id in its first message and the sentence of section 4 of the track document on `stamp_dir()` and `whose()`. Sub-agents run no git command and never run `scancel`. Each writes its own fragment and its own job ledger fragment. I check the frame id in every returned stamp, merge, recompute every pooled number from the merged tables into `<stage>_report_numbers.csv`, check each hand-back against its primary tables, and commit. Mechanical runs may use a model one tier below mine. Derivations stay with me.

## 6. Order of work inside interval i01

S0, then S1.1 (theory section 1, with the expectation for the cells where `rej_t` failed written before any run), then S1.2 (synthetic test), then S1.3 (runs). Then S2.1 (theory section 2, with the overstatement factor of Broska and Howes's interval for the design target derived as a function of $n_L/G$ and the cluster-level $R^2$, and both checks run), then S2.2 (runs). Then the S2 report, the numeric-claim sweep, the provenance checks, the commit, the tag `round7-ppi-S2`, one push of branch and tag, one pull request, its number confirmed on GitHub, and stop. Inside the interval there are no interim reports. Anything that would have halted work is handled by the decision boundaries and goes into the "Escalations" section of the S2 report. The stop conditions are those of section 10 of the track document.

Nothing of S3, S4 or S5 is set up, staged or piloted before the corresponding decision memo.

## 7. Predictions

Copied from the track document before any run. Each is scored in its gate report as held, partly held, refuted or not tested.

| id | prediction | status |
|---|---|---|
| S1.1 | Simulation, $k = 2$, $n_L \le 6$. The classical mean's bias exceeds 0.1 of its standard deviation in at least a quarter of the cells, and the Hájek interval covers within 0.03 of nominal in at least three quarters of them | not tested |
| S1.2 | Real tasks, `pcF2` and `pcE2`, $n_L = 6$. The Hájek interval covers within 0.03 of the D0 classical interval in at most half of the cells where `rej_t` covered below 0.80 | not tested |
| S1.3 | $n_L = 8$, own balance. The Hájek interval is wider than `rej_t` in every supported cell, by a width ratio of 1.10 to 1.50 | not tested |
| S1.4 | $\theta_3$, own balance, $p_a = 0.01$, $n_L = 4$. The smallest $\hat\pi_g$ is below 0.5 times $n_L/G$ on both census tasks | not tested |
| S2.1 | D0, design target. Broska and Howes's interval covers below 0.85 at $n_L = 4$ on at least two of the four tissue tasks | not tested |
| S2.2 | Design target with $n_L/G \ge 0.5$ (lung at $n_L = 8$ and 12, `CCRCC` and `CCRCC_merged` at $n_L = 12$). It covers above 0.95 at nominal 0.90 | not tested |
| S2.3 | Superpopulation target. It covers below 0.85 at $n_L \le 6$ in every simulation cell with $G = 15$ | not tested |
| S2.4 | Superpopulation target. Kluger et al.'s cluster bootstrap covers below 0.85 at $n_L \le 8$ on every task | not tested |
| S3.1 | $n_L = 8$, own balance, first score, $\theta_3$, `CCRCC`, `uni_v2`. The adaptive design's Hájek interval has a width ratio of 0.95 to 1.15 against D2 with `rej_t` | not tested |
| S3.2 | It covers within 0.03 of nominal in every simulation cell with $n_L \ge 8$ | not tested |
| S4.1 | $n_L = 8$. The classical interval applied as if simple random covers below 0.80 for $\theta_3$ on at least two tissue tasks | not tested |
| S4.2 | $n_L = 8$. The exact standard deviation of $\hat\theta_{\mathrm{HT}}$ under k-center is at least 1.5 times that of the classical mean under D0 on every tissue task | not tested |

## 8. Plan extensions

None. A local run that Nicolas asks for in chat is written here as a numbered extension before it runs, and does not carry across a gate.

## 9. The plan, transcribed from section 7 of the track document

Six stages. Gates at S2, S4 and S5. Transcribe this section into the plan before running anything, and keep a current-state block at the plan's top so that a compacted or restarted session can resume from the plan alone.

#### Interval i01

**Entry gate.** This document is on `main`, Nicolas has brought the PPI clone up to date, and the session can reach Longleaf.

##### S0. Setup and anchors (half a day, capped at one day)

1. Read this document, `docs/WAYS_OF_WORKING.md`, the two documents of section 2.1, the estimator definition, section 3 of `docs/round05/tracks/ppi/round5_ppi_theory.md`, and section 4 of round 5's E2 memo.
2. Set up the branch, the Longleaf code clone and the first bundle delivery (section 5), and transcribe section 7 into the plan.
3. Anchor. Rerun round 5's E5 cells with round 5's code and seeds and reproduce, to four decimals, the `rej_t` width ratio in column `wr_D0cl` of `results/round5/ppi/E4b_rejective/e4b_rej_width_ratios.csv` for $\theta_3$, own balance, $p_a = 0.01$, $n_L = 8$, on `CCRCC` with arm `uni_v2` (0.7263) and on `ACS_STATES` with arm `package` (0.5513). Then rerun the same cells with the new code and match them within the Monte Carlo error of the draw count.

**Exit.** Both anchors pass, with the numbers in `results/round7/ppi/S0_anchors/s0_anchors.csv`.

##### S1. Weighting under rejective selection (three days, capped at four)

Time cap three days, with the runs fanned out by task (six units) plus one simulation unit.

1. **Theory first.** In `docs/round07/tracks/ppi/round07_ppi_theory.md` section 1, write the estimators and variances of section 2.3 for D2, the conditions under which $\hat\theta_{\mathrm{HT}}$ is unbiased for the design (every $\pi_g > 0$), the effect of estimating $\pi_g$ and $\pi_{gh}$ by simulation, the interval's reference distribution, and how the cross-fitted difference form interacts with the weights. Say what you expect the weighting to do in the cells where round 5's `rej_t` failed, before any run.
2. **Synthetic test.** Extend round 5's test 3 (`code/scripts/round5_ppi_e4b_tests.py`) to the weighted estimators. Check that $\hat\theta_{\mathrm{HT}}$ is unbiased within Monte Carlo error under D2 at $(G, n_L, k) \in \{(51, 8, 1), (51, 8, 2), (24, 8, 1), (15, 6, 2)\}$, and that the mean of the variance estimate is within 0.10 of the empirical variance where the support is at least 1,000.
3. **Runs.** The simulation and masking grids of section 6 under D2, with estimators the classical mean with `textbook_t|fpc|lin` and `rej_t`, $\hat\theta_{\mathrm{HT}}$, $\hat\theta_{\mathrm{H}}$ and $\hat\theta_{\mathrm{HT},\lambda}$ with their intervals, and Broska and Howes's interval applied as if the clusters had been drawn without balance, and D0 with the classical and tuned estimators as the reference.

**Outputs.** `results/round7/ppi/S1_weighting/` with `s1_pi_hat.parquet` (every cell's $\hat\pi_g$ with Monte Carlo errors), `s1_sim.csv`, `s1_masking_grid.csv`, `s1_report_numbers.csv`.

##### S2. The comparators from the literature (two days, capped at three; gate)

1. **Theory.** Section 2 of the theory document gives Broska and Howes's interval specialised to the cluster contributions, with the checks against their example 1 and a simulation under their assumptions, and Kluger et al.'s weighted estimator and cluster bootstrap.
2. **Runs.** On the shared grids, under D0 (simple random selection of $n_L$ clusters), Broska and Howes's interval for the design target and for the superpopulation target, beside `textbook_t|fpc|lin|xf` and round 5's superpopulation interval. Kluger et al.'s design with $\pi_k = n_L/G$, which gives a random number of labelled clusters whose mean is $n_L$, and with $\pi_k$ proportional to $\lvert\bar f_k - \bar F\rvert$ mixed half and half with uniform, each with their estimator and cluster bootstrap and with the inverse-probability-weighted mean and its Poisson-design variance under the same draws, for the design and the superpopulation targets. Fan out by task, six units, plus one simulation unit.

**Outputs.** `results/round7/ppi/S2_comparators/` with `tests/`, `s2_sim.csv`, `s2_masking_grid.csv`, `s2_report_numbers.csv`.
3. **The S2 report** in `docs/round07/i01/ppi/round07_ppi_S2_report.md`, covering S0 to S2, with predictions S1.1 to S2.4 scored. Run the sweep, commit, tag `round7-ppi-S2`, push, open the pull request, and stop.

**Exit items, each with its evidence.**
1. The anchors of S0 pass (`S0_anchors/`).
2. The synthetic test of S1 passes, or the report says which cells fail and why (`S1_weighting/tests/`).
3. Every cell of both grids has run under every design and estimator named, or the report lists the cells that did not and why.
4. Broska and Howes's interval passes both checks of section 2.3 (`S2_comparators/tests/`).
5. The provenance index passes both checks.

**Predictions for interval i01.**
- **S1.1** In the simulation with $k = 2$ and $n_L \le 6$, the classical mean's bias exceeds 0.1 of its standard deviation in at least a quarter of the cells, and the Hájek interval covers within 0.03 of nominal in at least three quarters of them.
- **S1.2** On the real tasks with `pcF2` and `pcE2` at $n_L = 6$, the Hájek interval covers within 0.03 of the D0 classical interval in at most half of the cells where `rej_t` covered below 0.80.
- **S1.3** At $n_L = 8$ with own balance, the Hájek interval is wider than `rej_t` in every supported cell, by a width ratio of 1.10 to 1.50.
- **S1.4** For $\theta_3$ with own balance at $p_a = 0.01$ and $n_L = 4$, the smallest $\hat\pi_g$ is below 0.5 times $n_L/G$ on both census tasks.
- **S2.1** Under D0 for the design target, Broska and Howes's interval covers below 0.85 at $n_L = 4$ on at least two of the four tissue tasks.
- **S2.2** For the design target with $n_L/G$ of 0.5 or more (lung at $n_L = 8$ and 12, `CCRCC` and `CCRCC_merged` at $n_L = 12$), it covers above 0.95 at nominal 0.90, since it counts the unlabelled clusters' predictions as random and has no finite-population factor.
- **S2.3** For the superpopulation target it covers below 0.85 at $n_L \le 6$ in every simulation cell with $G = 15$.
- **S2.4** For the superpopulation target, Kluger et al.'s cluster bootstrap covers below 0.85 at $n_L \le 8$ on every task, in line with the project's own donor bootstrap at 0.71 to 0.84, as round 5's deck-2 literature check recorded.

#### Interval i02, opened by the S2 decision memo

What follows is the default. The S2 memo fixes the design, and nothing of it is set up, staged or piloted before the memo.

##### S3. An adaptive, balanced design at the cluster level (two days)

The design of section 2.3 after Chen et al., with two scores, $u_g = \lvert\bar f_g - \bar F\rvert$ on every task and, on the tissue tasks only, the distance in the space of the first 10 embedding principal components from cluster $g$ to its nearest other cluster. Balance variables are $\pi_g$ and the estimand's own $\bar f_g$. A constant predictor makes the first score zero everywhere, which gives uniform probabilities, so the constant arm is that design. Implement the cube method's flight and landing phases in Python, with a time cap of one day, and test that its realised inclusion frequencies match the targets within Monte Carlo error. If the cap is reached, record the escalation and use conditional Poisson sampling with the same targets and rejection on the balance condition, which this instruction allows as the fallback. The estimator is $\hat\theta_{\mathrm{H}}$ with the interval derived in S1, beside Broska and Howes's interval, on the shared grids. With balance on the own $\bar f_g$ the difference form adds nothing, since the $\lambda$ term is balanced away, which is Chen et al.'s remark 1. Fan out by task, six units, plus one simulation unit. Outputs in `results/round7/ppi/S3_adaptive/` with `tests/`, `s3_sim.csv`, `s3_masking_grid.csv` and `s3_report_numbers.csv`. A version that labels in batches, after Kluger and Bates (arXiv:2602.16933), is not run this round. If S3 succeeds, propose it in the S4 report.

**Predictions.**
- **S3.1** At $n_L = 8$ with own balance and the first score, the adaptive design's Hájek interval has a width ratio of 0.95 to 1.15 against D2 with `rej_t`, for $\theta_3$ on `CCRCC` with `uni_v2`.
- **S3.2** It covers within 0.03 of nominal in every simulation cell with $n_L \ge 8$.

##### S4. A deterministic rule (one day; gate)

Greedy k-center on the tissue tasks of the shared masking grid, at $n_L \in \{4, 6, 8, 12\}$, computed exactly over the $G$ starts. For each cell, report the exact $\pi_g$, the share of pairs with $\pi_{gh} = 0$, the exact coverage of `textbook_t|fpc|lin` applied as if the sample were simple random, Broska and Howes's interval applied the same way, and the exact standard deviation of $\hat\theta_{\mathrm{HT}}$. Put each beside the same quantities under D0 and under D2 with own balance at the same $n_L$. Fan out by task, four units. Outputs in `results/round7/ppi/S4_kcenter/` with `s4_grid.csv` and `s4_report_numbers.csv`. Then write the S4 report in `docs/round07/i02/ppi/round07_ppi_S4_report.md` covering S3 and S4, with predictions scored, and stop at tag `round7-ppi-S4`.

**Predictions.**
- **S4.1** At $n_L = 8$, the classical interval applied as if the sample were simple random covers below 0.80 for $\theta_3$ on at least two tissue tasks.
- **S4.2** At $n_L = 8$, the exact standard deviation of $\hat\theta_{\mathrm{HT}}$ under k-center is at least 1.5 times that of the classical mean under D0, on every tissue task.

**Exit items.** S3's cube test passes or its fallback is recorded. Every cell has run or is listed. The predictions are scored. The provenance index passes both checks.

#### Interval i03, opened by the S4 decision memo

##### S5. The closing report (one day; gate, end of track)

`docs/round07/i03/ppi/round07_ppi_final_report.md`, ending with a closing page "What the inference track established in round 7". It states, for each design, whether the paper can recommend it, under which conditions, and against which comparator, and lists what is not established. The memo at S4 may add stages before S5.
