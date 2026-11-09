# Round 10, track `final-runs`, the plan

```state
updated: 2026-11-09, 02:30 UTC (Claude Science session on the Windows execution PC, David's team account, reaching Longleaf through compute target ssh:longleaf; frame fc04d488-f9cc-4e63-99fc-f3a50dbc17ed)
unit: final-runs
status: running
step: F1, housekeeping done as far as this seat reaches (section 2); F1.1 the estimator module is next
last run: clone job only (no analysis yet); the clone is /work/users/w/e/weiyang/hest_code/round10-final-runs on branch round10-final-runs, started at 133384d1
jobs: none running
next: write code/scripts/round10_final_runs_estimators.py and its acceptance script (section 4, F1.1), deliver the commit as a snapshot (section 3), and run the acceptance job
waiting: Nicolas, the housekeeping deletion of round 9's saved papers (section 2), which needs the Claude Science store round 9 used; it does not block F1
```

*Written on 9 November 2026 by the first session of track `final-runs`. The brief is `docs/round10/i01/final-runs/round10_final_runs_brief.md` on `main` (read at 133384d1). It is read with `docs/EXECUTION_RULES.md` at that commit, `docs/round10/masterplan.md`, the ledger's decisions `docs/round10/i01/ledger/round10_ledger_decisions.md` and Nicolas's L3 answers `docs/round10/i02/ledger/round10_ledger_L3_answers.md`, which win where they differ. This plan does not copy the brief. It records how the session does each step, the checks it runs, and dated notes as the work goes.*

## 1. What was read at the start

- `docs/EXECUTION_RULES.md` (revision of 8 November), the brief, the kickoff, the masterplan with its amendments, the L3 answers, the ledger decisions, the L0 scope, `docs/environment.md`, section 0 of `results/round10/ledger/round10_ledger_L1_S4.md`, `results/round10/ledger/checks/l3_split_variance_check.py` and its output, `code/scripts/round9_fewcluster_williams.py`, and `CLAUDE.md` for the shape of the state block only.
- Where the L3 answers change the brief. The primary estimator is the difference estimator with the coefficient fixed at 1 at every number of labelled clusters (R7-6). The two-fold cross-fitted form is reported beside it from 6 labelled clusters, with $\hat V_w$ primary for that form under the switch rule. The classical estimator is the control. No coefficient fitted on the clusters it is applied to is used anywhere outside the limits arms the brief names. Prediction sets stay (P), so P10.3 and FR8 are scored. E8 runs at F3 with its literature search first, and V is decided by Nicolas after F3. The brief already carries these, and the plan follows the L3 answers where any wording differs.

## 2. Housekeeping (brief, section 1)

- [x] 2026-11-09. **Round 9's saved papers.** The brief asks for the full texts of papers that round 9's sessions saved to the Claude Science artifact store to be deleted. This session can see the store of the Claude Science installation it runs in (the Windows execution PC on David's team account). That store holds 537 artifacts, all created from 1 November 2026 on, in three projects of other repositories (`NicWYZ/ST-Fed-Learn`, `NicWYZ/textual-st-histology` and one more), and none from round 9 of this project. Its only two PDFs are `st-fed-learn/refs/qkag131.pdf` and `st-fed-learn/refs/2610.07048v1.pdf`, saved on 4 November by an ST-Fed-Learn session, which are not round 9's and are outside this track. Round 9's Claude Science sessions ran on Nicolas's Mac (`docs/environment.md`), so their store is not reachable from this seat. **Nothing was deleted.** The deletion needs a session in the Claude Science installation round 9 used, or Nicolas, and the request is in the state block's `waiting` line.

## 3. How every job runs

- **Code.** Scripts are written in this clone (`/work/users/w/e/weiyang/hest_code/round10-final-runs/`) under `code/scripts/round10_final_runs_*`, committed there as `NicWYZ <NicWYZ@users.noreply.github.com>`, with commit messages through a file. Commits are pushed over SSH only at gates and before a stop or a long job (rules, sections 1 and 5; brief, section 1, departure from section 5).
- **Snapshot.** Before a job uses a commit, a short delivery job runs `git archive <commit> code` from the clone into `/work/users/w/e/weiyang/hest_replication/results/round10/final_runs/_snapshots/<commit>/` and makes it read only. Each delivery is a row of `results/round10/final_runs/code_deliveries.csv` (commit, date, snapshot path, md5 of every script in it).
- **Output directories.** Bulk outputs go under `/work/users/w/e/weiyang/hest_replication/results/round10/final_runs/<stage>/<unit>/`, which did not exist on 9 November. Each job runs from its own output directory with the snapshot's `code/` on `PYTHONPATH` and the project's Python by absolute path (`/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python`). On the node it writes `PROVENANCE.txt` (Slurm job id, `$SLURM_JOB_PARTITION`, node, date, snapshot commit, command line, config with its sha256, `PYTHONHASHSEED=0`, md5 of every script that ran and every input) and the `_provenance.json` stamp of the `longleaf-provenance` skill under this session's frame id, with track `final-runs`. Seeds come from `zlib.crc32`. Parquets get an explicit `pa.schema`, and summaries are written before bulk tables.
- **Inputs not made by this track.** Reading an input the brief names needs no question. Its `whose()` verdict is recorded in `results/round10/final_runs/inputs_whose.csv`.
- **The job ledger.** `results/round10/final_runs/job_ledger.csv`, one row per Slurm job (stage, unit, harness job id, Slurm id, account, partition, submit and end times, state, wall, MaxRSS from `sacct`). Jobs are identified by Slurm id, since the harness sets the job name (`claude-science-<uuid8>`). CPU jobs go to `general` with `--mem` set and about three times the expected runtime, from a sibling's `sacct` where one exists and from a smoke test otherwise. A job pending four hours is reported to Nicolas and keeps waiting.
- **Repository contents.** Only aggregates enter `results/round10/final_runs/`. Before every commit the staged files are listed and checked for data, papers, transcripts or credentials.
- **Numeric claims.** `code/scripts/verify_numeric_claims.py` runs over every report before it is handed over, with exceptions in `.verify-exceptions-round10-final-runs`.

## 4. Stage F1, setup, anchors and data (gate F1)

Report to `docs/round10/i02/final-runs/round10_final_runs_F1_report.md`, tag `round10-final-runs-F1`.

### F1.1 The estimator module

- [ ] `code/scripts/round10_final_runs_estimators.py`. Plain numpy functions working on arrays of cluster values $z_g$ and mean predictions $f_g$ over the population $U$ of $G$ clusters, vectorised over draws, with these entries.
  - `classical`, the labelled mean with $(1 - n/G)s_z^2/n$ and $t_{n-1}$.
  - `difference_fixed(c)`, the difference estimator with a preassigned coefficient $c$ (1 for the paper), with $(1 - n/G)s_{z - cf}^2/n$ and $t_{n-1}$, and an argument to drop the finite-population factor (S6-3).
  - `crossfit(K, rule)`, the $K$-fold form of decisions section 1.1 with the coefficient rule as an argument (`r5_clipped`, `ols_unclipped`, `fixed`), returning $\hat\theta$, $\hat V_w$ with $t_{n-K}$, the exactly unbiased $\hat V$ (the $K$-fold form of the identity, $\frac{1}{K}\sum_k s_k^2 - \frac{1}{K}\sum_k (t_k - \hat\theta)^2$, as in `l3_split_variance_check.py`, which for $K = 2$ is the decisions' formula), $\max(\hat V, \hat V_w)$ and the conservative $\frac{1}{K}\sum_k s_k^2$, with an argument to drop the finite-population factor.
  - `fold_r9`, round 9's fold-wise form `FOLD`, for the anchor only.
  - `regime_b_formC`, form C for regime B with the coefficient fixed at 1 and cross-fitted, with the variance and degrees of freedom of `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`, section "Regime B". This entry is written in F1 and first used in F2.
  - `bh`, `bh_t`, `bh_t_fpc`, the Broska and Howes comparators as defined in `code/scripts/round7_ppi_s2_comparators.py`.
- [ ] **Acceptance, part 1.** `code/scripts/round10_final_runs_f1_module_check.py` imports the populations and the enumeration loop of `results/round10/ledger/checks/l3_split_variance_check.py` (read from the snapshot, not copied), replaces its estimator functions with the module's, and writes every row of the output in the same format. Pass means each of the 30 rows agrees with `l3_split_variance_check_output.txt` in every printed field at the printed six decimals. The comparison is written to `f1_module_check_diff.csv`.
- [ ] **Acceptance, part 2.** The same script runs `run_pop` of `round9_fewcluster_williams.py` on CCRCC from `results/round9/.../c0_cluster_summaries.csv.gz` (path confirmed on Longleaf before the job), and for every gene and $n$ recomputes `FIX1`, `W_within` and `FOLD` from the module on the same draws, by drawing the permutation matrix with the same generator calls in the same order. Pass means the point estimates and variances agree draw for draw to $10^{-12}$ relative, and the summary rows equal `results/round9/fewcluster/williams/i34_williams_summary_hest.csv` for CCRCC. Since round 9 ran the three HEST tasks through one generator, the check replays the generator through INDIANA_KIDNEY and LUNG_XENIUM in round 9's order as well, or it is restricted to the draws of CCRCC's genes, which come first in the `groupby` order. Which one holds is recorded when the code is read.
- [ ] Smoke test first on one gene and $n = 8$, then the full check as one CPU job.

### F1.2 The anchors

Each anchor is reproduced from the code path that made it before any new code touches it.

- [ ] **Round 5.** Find, from `results/round5/ppi/E4b_rejective/` and its `PROVENANCE.txt` and stamp, the commit, script (`round5_ppi_e4b_rejective.py` or `round5_ppi_e4b_sim.py`) and inputs that produced the `e4b_grid.csv` row (CCRCC, `uni_v2`, $\theta_3$, $G = 24$, 8 labelled donors, design D0, rule `c_crossfit_design`, interval `textbook_t|fpc|lin|xf`, `n_sub` 2000). Run that script at that commit from a snapshot, restricted to the cell if the script allows it, with its own seed. Expected `coverage_median` 0.85775 and `width_median` 0.113623.
- [ ] **Round 7.** The same for `results/round7/ppi/S5_numbers/run1/s5_matched_cells.csv` (ACS_STATES, $\theta_3$, 8 labelled clusters, $p_a = 0.01$, `D2_rej_t`). Its `PROVENANCE.txt` shows `round7_ppi_s5_numbers.py` merging earlier outputs at snapshot `61a60229`, so the reproduction goes back to the run that made the cell's draws. Expected `coverage` 0.87900 and `wr_D0cl` 0.551291.
- [ ] **Pass rule, written before the runs.** With the same seed and code the cell should agree exactly, and the report says whether it did. Otherwise the reproduction passes if each quantity is within 3 Monte Carlo standard errors of the file's value, where the standard error of a median over genes is taken from a bootstrap over draws of the gene-level coverages and widths, and that of a coverage from $\sqrt{p(1-p)/R}$ at the cell's draw count $R$. A failed anchor stops F2 and F3 arms that rest on it (brief, decision boundaries).

### F1.3 The inflation check

- [ ] `code/scripts/round10_final_runs_f1_inflation.py` reruns round 9's comparison on the observed `uni_v2` donor means and on ACS by state with an arm `R5_lin`, which adds round 4's `lin` term $(\lambda_{(g)} - c_U)\bar F$ to each contribution before pooling, as section 0 of `round10_ledger_L1_S4.md` describes, beside the arms `R5`, `W_within` and `FIX1` reproduced from round 9 at its seed. `R5`, `W_within` and `FIX1` must match round 9's summary files, which anchors the run.
- [ ] Score **FR1**. Report for each task the ratio of `R5_lin`'s median width to `W_within`'s at 8 labelled clusters, and coverage for both, and say whether the intervals of rounds 5 to 7 carried the level-dependent variance.

### F1.4 The data stage

- [ ] Read the corpus data card (`NicWYZ/ST-Fed-Learn`, `docs/round01/tracks/data/data_card.md`, through the federated project's clone on Longleaf with `git --no-optional-locks`) and the registry under `/work/users/w/e/weiyang/st_fed_learn/data/`, and record `whose()` for the corpus. Nothing is downloaded.
- [ ] For each candidate task of the L0 scope, section 3 (kidney Visium, lung Xenium, brain Visium, bowel Visium, breast Xenium, breast Visium, and breast ST, skin Visium and heart Visium if their donor counts pass), count samples, centers and donors from the registry, one CPU job. A task needs at least 10 donors.
- [ ] **Donor-label audit** of the kind of `results/round2/R5b_audit/`, one row per sample with the evidence used and a `donor_label_status` verdict, recording unverifiable samples as such. Reading upstream sources outside Longleaf needs network access, which is asked of Nicolas if it is needed, and is not assumed.
- [ ] **Licences** per sample, with the counts of samples with none and of those marked internal.
- [ ] **Kidney Visium against CCRCC and INDIANA_KIDNEY.** Match its samples and donors to the two HEST tasks' `sample_id` and `donor_id` so no donor is counted twice, and report any disagreement.
- [ ] The **proposed task list** with confirmed counts goes into the F1 report. Nicolas confirms it at the gate.
- [ ] **Held-out prediction files** for the proposed tasks. The method is fixed in this plan before the jobs run, after the corpus layout is read. The starting design is a ridge head on frozen embeddings for each gene of the task's gene set, fitted on standardised embeddings with the penalty chosen on the training donors only, with the target donor held out (and the target center held out for the institution axis), on both scales of D5, for the encoders the corpus holds among `uni_v2`, `hoptimus0` and `resnet50`. The columns follow the HEST tasks' files (`y__<gene>`, `f__<gene>`, `donor_id`, `sample_id`, `barcode`, `m_std`), and the raw count total per spot is kept for the second scale. These files are bulk outputs and stay on Longleaf.
- [ ] Leave-one-donor-out $R^2$ of donor means against the leave-one-out constant (D12), per task, encoder and scale.
- [ ] On kidney Visium, the atypical-donor diagnostics of `results/round9/stud/atypical_donor_diagnostics.csv`, regenerated from committed code (D13), and INT5's raw library size and detection rate.
- [ ] **Before F2** (P10.1). Name the round 5 to 7 file, row and interval label each P10.1 comparison uses, in a section of this plan.

## 5. Stages F2 to F4 (outline)

Each stage's methods are written into this plan after the previous gate's reply and before its first job. Predictions are the brief's section 5 and are scored at the gate each names.

- [ ] **F2, inference** (brief, F2 items 1 to 8). One design-simulation driver over each task's own cluster values, every arm on the same draws, with the switch rule of decisions section 1.1 evaluated first. Report to `docs/round10/i03/final-runs/`.
- [ ] **F3, prediction sets and designs** (brief, F3 items 1 to 5), with E8's literature search by subagents before any E8 analysis, its queries logged. Report to `docs/round10/i04/final-runs/`.
- [ ] **F4, final report and pull request** to `docs/round10/i05/final-runs/round10_final_runs_report.md`, with the table that maps each number the paper quotes to its file, and one pull request into `main`.

## 6. Escalations and open items

- 2026-11-09. Housekeeping deletion not possible from this seat (section 2).

## 7. Dated notes

- 2026-11-09. Clone created by a 2-CPU Slurm job on `general` (`git clone --reference-if-able` the round 7 clone `--dissociate`, then checkout), branch `round10-final-runs` at 133384d1, equal to `origin/main` at that time.
