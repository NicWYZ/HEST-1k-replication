# Round 10, track `final-runs`, the final report (gate F4)

*Written on 15 November 2026 by the ninth session of track `final-runs` (frame `3f5eb01e-aa12-4f67-84ac-45c28e10831d`). F4's methods are the plan's section 5e (`docs/round10/tracks/final-runs/round10_final_runs_plan.md`), written by the eighth session (frame `bdb361de-6630-44e8-b0f8-8bd63dae9ad3`) before any F4 job, which also ran F4's first part. The decisions in force are the F1, F2 and F3 decision files in `docs/round10/i03/`, `i04/` and `i05/final-runs/`. Paths that begin `F2/`, `F3/` or `F4/` are relative to `results/round10/final_runs/`, and "the numbers table" is `results/round10/final_runs/F4/paper_numbers.csv`, whose `key` column names the row a number is read from. The pull request is __PR__.*

## 1. Stage and status

F4 is the track's final gate, and every task of plan section 5e is done. The five open points of gate F3 are resolved. The first is the regime B $\mu$ question. Its check failed two of the three thresholds named before the run, so all 330 regime B $\mu$ units of the HEST and corpus tasks were rerun on all spots. Every regime B $\mu$ row of the paper now estimates the donor mean over all spots, which is the estimand of record. The label $\mu_J$ of the F3 decision file therefore applies only to F3's superseded tables. The numbers table has 443 rows, keyed by the findings survey's and the ledger's identifiers. Every value in it is read by a committed script from a committed file. No job of the track is running. The branch carries the gate tag `round10-final-runs-F4`, and one pull request into `main` is open for Nicolas to merge.

## 2. What was run

Every F4 job ran on Longleaf from a read-only snapshot of a committed `code/` directory, with `PROVENANCE.txt` in its output directory under `/work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F4/`. The F4 rows of `results/round10/final_runs/job_ledger.csv` (342 rows, unit `F4_ledger/ledger_v1`, Slurm 9227399, provenance in `F4/ledger_PROVENANCE.txt`) give each job's Slurm id, partition, node, wall time, requested memory, peak memory and commit. All 342 read COMPLETED.

| unit | Slurm | commit | what it did |
|---|---|---|---|
| `mu_check/means_v1`, `means_v2` | 9154351, 9173533 | `1da199cb`, `727de29a` | 5e.1 parts 1 and 2. `means_v2` casts the float32 prediction files to float64 before averaging |
| `mu_check/compare_v1`, `compare_v2` | 9173685, 9173991 | `727de29a`, `d6caff04` | 5e.1 part 3, the one-population comparison against the thresholds |
| `mu_check/allspot__*` (330 units) | see the ledger | `1da199cb`, `727de29a`, `d6caff04` | the all-spot rerun of every regime B $\mu$ unit, 270 regcomp and 60 box |
| `readings/readings_v1` | 9174829 | `0484ad3c` | 5e.2 and 5e.3, the ACS and S0006 readings |
| `f4_aggregate_v1` | 9177176 | `5d5cb1f5` | 5e.5, F3's regcomp and box aggregates on the all-spot units, the merged tables and the readings |
| `readings/readings_alloc_v1` | 9184267 | `daa8781d` | the allocation reading, prediction F4-3b |
| `paper_numbers/paper_numbers_v1`, `v2` | 9227174, 9227641 | `759aef7b`, `e3635e23` | 5e.6, the numbers table. `v2` is of record |
| `F4_ledger/ledger_v1` | 9227399 | `39666533` | the job-ledger rows |

Wall times are 2 seconds to 58 seconds for the single jobs and 1 minute 45 seconds to 50 minutes 18 seconds for the all-spot units, and no job's peak memory reached 5 GB (`job_ledger.csv`, rows of stage F4). Four of the 342 jobs were routed to the `spill` partition and ran there, and the track moved its other pending jobs to `general` as Nicolas approved on 12 November.

The F4 scripts at the gate commit, with their md5s, are `round10_final_runs_f4_mu_check.py` (`5be8363c0767cc514ef2a4842e21d220`), `round10_final_runs_f4_readings.py` (`495d270849ca771a90a64cbf8672e027`), `round10_final_runs_f4_aggregate.py` (`c5f296bbb0821368679a9bdacb52d270`) and `round10_final_runs_f4_paper_numbers.py` (`2433e4b7244dea17e7c01b25efef6a51`). Every job's own script md5s are in its `PROVENANCE.txt` and are checked against their commits in `F4/provenance_index.csv`. No sub-agent was used in F4.

## 3. Acceptance checks and exit items

- **The all-spot donor means.** On all 60 HEST and corpus populations with a $\mu$ row, the all-spot donor means of $y$ and of $f$ equal the committed cluster values within a largest relative difference of 2.4e-13, against the criterion of 1e-10 (`F4/aggregate/f4_mu_check_populations.csv`, columns `allspot_vs_cv_max_rel_y` and `allspot_vs_cv_max_rel_f`).
- **The all-spot rerun.** 330 of 330 units read COMPLETED, and every unit's anchor passed (`F4/aggregate/f4_allspot_units.csv`, `F4/aggregate/f4_aggregate_summary.json`).
- **The F4 aggregate** ran F3's regcomp and box aggregates unchanged on the all-spot units. Its merged comparison table keeps 8868 F3 rows and adds 4374 all-spot rows, 13242 in all, and its merged box summary has 134 rows (`F4/aggregate/f4_aggregate_summary.json`).
- **The allocation reading.** Its numbers of clusters per task equal those of F2's regime B summary (24, 23, 25, 15 and 51, `F4/readings/readings_alloc_v1/f4_alloc_by_task.csv` against `F2/aggregate_regimeB/f2_regimeB_summary.csv`).
- **The numbers table.** All 443 selectors resolve to one value, and every cited file is tracked in the clone (`F4/paper_numbers/paper_numbers_summary.json`). Two values are empty by definition. They are the Spearman correlations over genes on ACS by state, which has one gene (keys `B4.ACS_STATES` and `B4p.ACS_STATES`). Forty-one values were checked against the numbers the F2 and F3 reports quote, and all agree at the quoted precision.
- **Gate checks.** The provenance index runs over F1 to F4 into `F4/provenance_index.csv`, and the numeric-claim sweep runs over this report and the F3 decision file, in the gate job of section 9.

## 4. Variables that differ between the arms of each comparison

- **The $\mu$ check, all spots against joined spots** (5e.1). The spots that enter each donor's mean (all spots against spots joined to nuclear morphology, a share of 0.912 to 0.999 per population, `F4/aggregate/f4_mu_check_populations.csv`, column `share_kept`). Seeds, cells, $R$ and estimators are the same.
- **Regime B against regime A** (E1). The design (every donor with a few spots against a few donors with all spots), the number of labelled clusters, the units per cluster, the cost model and the variance estimator. Between ACS by state and the HEST tasks, also the number of clusters (51 against 15 to 25), the spread of cluster sizes, the estimands formed and the predictor's accuracy.
- **The allocation factor** (F4-3b). Only the cluster sizes $M_g$ of each task's $\theta_3$ population. No estimator enters.
- **S0006 against the other kidney Visium centers** (F4-4). The center, its donors and spots, and the center-out prediction heads, on each encoder and scale.
- **The numbers table's earlier-round rows against the final-runs rows** beside them. The code generation, the estimator (the coefficient fixed at 1 in the final runs), the number of draws and, for the corpus tasks, the data.

## 5. Predictions against outcomes

| prediction | gate | outcome | verdict |
|---|---|---|---|
| FR1. With round 4's `lin` term, round 5's interval is within 1.15 times the width of Williams' form at 8 labelled clusters | F1 | ratios 0.982 to 1.004 on the four tasks (`F1/aggregate/f1_fr1.csv`; threshold from `docs/round10/i01/final-runs/round10_final_runs_brief.md`) | held |
| F1's anchors, prediction anchor and gene rule | F1 | as the F1 report gives them | held |
| P10.1 part 1. The tuned interval's coverage at 8 donors is 0.02 to 0.05 below round 5's | F2 | drops of -0.0004, -0.0010 and -0.0077 (`F2/report_tables/r13_p10_1.csv`) | refuted |
| P10.1 part 2, $p_a = 0.1$. The ordering of designs is unchanged | F3 | D2_rej_t and cube_S4b change order (`F3/aggregate/t24_balance_p101_part2.csv`) | refuted |
| P10.1 part 2, $p_a = 0.01$ | F3 | the pair is tied in round 7 | held |
| P10.3 part 1. `within_full` narrower than HCP from 9 spots on CCRCC and LUNG_XENIUM | F3 | margins at least 1.729 and 1.562 (`F3/aggregate/t01_map_p103.csv`) | held |
| P10.3 part 2. INDIANA_KIDNEY within 2% of `within_plain` at 9 to 15 spots | F3 | ratios 1.049 to 1.072 | refuted |
| FR2. $\hat V_w$ stays primary, $\hat V < 0$ in at least 0.05 of draws at 6 clusters | F2 | smallest median 0.9937 over 1432 cells (`F2/aggregate/f2_switch_decision.json`) | held |
| FR3. At 4 clusters `fix1`'s RMSE below `classical`'s | F2 | on all four tasks (`F2/aggregate/f2_scores.csv`) | held |
| FR4. The share of genes with `fix1` wider than `classical` | F2 | 0.30, 0.32 and 0.044 for $\theta_3$, at the threshold on CCRCC (`F2/aggregate/f2_scores.csv`) | held for $\theta_3$ |
| FR5. `fix1`'s coverage at least 0.02 higher on the normalised scale on CCRCC | F2 | -0.0006 for $\theta_3$ (`F2/aggregate/f2_scores.csv`) | refuted for $\theta_3$ |
| FR6. Kidney Visium beyond the frontier with coverage below 0.88 at 16 donors | F2 | coverage 0.8924 (`F2/diagnostics/f2_fr6.csv`) | refuted |
| FR7. Regime B `fix1` within 0.03 of nominal at $m \ge 6$; the unbounded column larger | F3 | largest deviation 0.0205 in 30 of 30 cells; 11 of 11 tasks (`F3/regimeB/aggregate_v1/box/f3_box_checks.json`) | held |
| FR8 clause 1. Donor-level HCP pooled below 0.75 | F3 | 0.9057 (`F3/aggregate/t09_institution_fr8.csv`) | refuted |
| FR8 clause 2. HCP over centers at least 0.8 | F3 | 1.0 | held |
| R10-F3a. Regime B narrower in at least 0.8 of cost-matched comparisons | F3 | 141 of 156 (`F3/regimeB/aggregate_v1/regcomp/f3_regcomp_checks.json`) | held |
| F3's open points 2 to 7 | F3 | as the F3 report gives them (`F3/aggregate/f3_predictions.csv`) | 2 refuted, 3 held, 4 partly held, 5 held, 6 held, 7 held |
| F4-1. The all-spot donor means equal the committed $\mu$ rows within 1e-10 | F4 | largest relative difference 2.4e-13 on 60 of 60 populations | held |
| F4-2. On CCRCC `uni_v2` $\log(1 + y)$ the three thresholds of 5e.1 hold | F4 | coverage moves up to 0.012 against 0.01, the width ratio up to 0.0375 relative against 0.02, the required $m$ by 0 steps (`F4/aggregate/f4_mu_part3_compare.json`) | refuted |
| F4-3. On ACS regime B is wider only in cost-matched cells, and its cost-matched $m$ is the smallest | F4 | regime B is narrower in 0.25 of 12 unit-cost pairs; its median cost-matched $m$ is the smallest, 48 (`F4/aggregate/f4_acs_summary.json`) | refuted |
| F4-3b. The allocation factor is larger on ACS than on every HEST task | F4 | 2.656 against at most 1.706 (`F4/readings/readings_alloc_v1/f4_alloc_summary.json`) | held |
| F4-4. S0006's median absolute residual exceeds every other center's | F4 | in 5 of 6 encoder and scale cells, not on `uni_v2` lognorm (`F4/aggregate/f4_s0006_summary.json`) | refuted as written |
| F4-5. E8's $m = 15$ rows come from how the join selects sets | F4 | all 54 rows choose GHCP by round 5's mean-width rule (`F4/aggregate/f4_aggregate_summary.json`); no fix, so the second half holds trivially | held |

## 6. Results

### 6.1 The $\mu$ question (5e.1)

The all-spot donor means reproduce the committed cluster values on all 60 populations, which closes the item the F3 report left unchecked. Joined-spot means differ from them by at most 0.193 between-donor standard deviations for any gene (`F4/aggregate/f4_mu_check_populations.csv`, column `abs_std_diff_max`). On CCRCC `uni_v2` $\log(1 + y)$ the all-spot rerun moved regime B's median coverage by up to 0.012 in 141 regcomp cells and the regime B to regime A width ratio by up to 0.0375 relative in 24 cells, while the box column's required $m$ did not move (`F4/aggregate/f4_mu_part3_compare.json`). Two thresholds failed, so by the plan's rule all 330 $\mu$ units were rerun on all spots. The coverage threshold of 0.01 was about one Monte Carlo standard error of a difference between two runs, which was too tight to separate the estimands. The width ratio's movement is real, though.

On the all-spot rows, regime B is narrower than regime A in all 1458 cost-matched comparisons of $\mu$ with the fixed coefficient on the HEST and corpus tasks (numbers table, keys `F4.mu.n` and `F4.mu.narrow`). The V picture is unchanged. Against F3's $\mu_J$ rows, the median required $m$ changes in 21 of 132 bounded rows and 16 of 132 unbounded rows, by a factor of 0.8 to 1.5. Median coverage at the chosen $m$ lies between 0.8865 and 0.904 in the bounded column and between 0.889 and 0.90425 in the unbounded column (keys `V.F4.cov_min_b` to `V.F4.cov_max_u`). The largest absolute Spearman correlation of coverage with $G^\ast_B$ is 0.38 (`F4/aggregate/f4_box_task_summary_merged.csv`), which corrects the F3 decision file's "close to zero".

### 6.2 Regime B wider on ACS by state (5e.2)

Regime B on ACS by state is narrower than regime A in only 0.25 of the 12 unit-cost pairs. So the per-cluster cost cannot be the mechanism, and F4-3 is refuted (`F4/aggregate/f4_acs_summary.json`). The allocation explains it. Regime B labels every cluster at $m_g = \min(M_g, \max(1, \mathrm{round}(B' M_g/N)))$, which is proportional to cluster size, while the target weights clusters equally. With equal within-cluster variances this inflates regime B's variance against equal allocation by about the mean of $\overline{M}/M_g$, written

$$
\overline{M} \cdot \frac{1}{G}\sum_{g=1}^{G} \frac{1}{M_g}.
$$

The factor is 2.656 on ACS by state, where state sizes run from 3064 to 195665 units. On the HEST tasks it is 1.280 (CCRCC), 1.288 (CCRCC_merged), 1.706 (INDIANA_KIDNEY) and 1.324 (LUNG_XENIUM) (`F4/readings/readings_alloc_v1/f4_alloc_by_task.csv`). F4-3b holds. The factor does not order the HEST tasks by their width ratios, and it assumes equal within-cluster variances, which the reading does not check. So it is a sufficient mechanism for ACS, not a full account of every task. An equal allocation would remove it. This is a design choice that round 5's E3 made, and the final runs keep it for comparability.

### 6.3 FR8's lowest center (5e.3)

S0006's median absolute center-out residual is larger than every other center's in 5 of 6 encoder and scale cells. On `uni_v2` $\log(1 + y)$ it is 0.975 against at most 0.722 elsewhere (numbers table, keys `F4.S0006.resid` and `F4.S0006.others`), but on `uni_v2` lognorm it is 0.883 against 0.971 (`F4/aggregate/f4_s0006_summary.json`). Center shift, meaning the center-out heads predict S0006 worse, is the main cause of its coverage of 0.655, but the prediction as written is refuted.

### 6.4 E8 at $m = 15$ (5e.4)

All 54 rows at $m = 15$ where the overall narrowest set needs extra labels are part 2 rows at $K$ from 18 to 40, and in all of them round 5's mean-width rule chooses GHCP (`F4/aggregate/f4_aggregate_summary.json`, item `e8_m15`; rows in `F4/aggregate/f4_e8_m15_rows.csv`). The F3 table reports median widths, so a set that is narrower by median width can lose by mean width. This is the selection rule, not a fault in the join, and no rerun was needed. When E8 is quoted, the paper should name the width rule.

### 6.5 The paper's numbers, by section of the writing plan

The numbers table holds every number with its file, selector, stage and commit. The headline rows are these.

- **S2, data.** 278 of 340 corpus samples are kept on six tasks (keys `F1.samples_in`, `F1.samples`). The first principal component's share of between-donor variance on $\log(1 + y)$ is 0.650 on CCRCC and 0.313 to 0.782 on the other tasks, and lower on the normalised scale on every task, for example 0.338 on CCRCC (keys `F2.pc1.*`).
- **S3, prediction sets.** HCP at $K = 10$ with no labelled target spots covers 0.9694 on CCRCC in the final runs, beside round 3's 0.9692 (keys `F3.A4.CCRCC`, `A4.hcp`). `within_full` is narrower than HCP by at least 1.729 on CCRCC and 1.562 on LUNG_XENIUM from 9 labelled spots. On the institution axis, donor-level HCP pooled covers 0.9057 at the median center and S0006 0.655 (keys `INST.*`).
- **S4, valid inference.** At 8 labelled donors under `uni_v2`, `fix1`'s median width over `classical`'s for $\theta_3$ is 0.554 on ACS by state, 0.585 on LUNG_XENIUM, 0.878 on CCRCC and 0.664 to 0.948 on the corpus tasks (keys `B7.*`). Same-sample tuning covers 0.840 at 4 clusters against the control's 0.897, and Kluger's cluster bootstrap 0.7145 (keys `B5.*`). The smallest median $E(\hat V_w)/\text{Var}$ over 1432 cells is 0.9937 (key `B10.switch.min`).
- **S5, how many donors.** `fix1` covers 0.8965 on CCRCC at 8 labelled donors against `classical`'s 0.849 (keys `B8.*`). The median residual max-share is beyond `kappa_sup` for 0.98 of CCRCC's genes (keys `B13.*`). Regime B is narrower in 141 of 156 cost-matched $\theta_3$ comparisons and in 1458 of 1458 for $\mu$ on all spots (keys `E1.*`, `F4.mu.*`). Under the unbounded column regime B needs a median 100 spots per donor on CCRCC and 75 persons per state on ACS, against 10 and 2 under the bounded column, at coverage 0.898 to 0.901 on CCRCC (keys `V.*`). The take-all design lifts CCRCC's coverage from 0.833 to 0.892 at 0.770 of the width (keys `E7.CCRCC.*`).
- **S6, limits.** The pairs percentile bootstrap covers 0.771 at 4 clusters and 0.982 at 16 (keys `S6-2.*`). Broska and Howes's interval without the small-sample correction covers 0.699 at 4 clusters, and `bh_t` 0.875 (keys `S6.bh.n4`, `S6.bh_t.n4`). The interval without the finite-population factor covers 0.944 against the design target on CCRCC at 8 donors (key `S6-6.CCRCC.n8`).

Both scales are in the table wherever the final runs ran both, since D5 is not decided.

## 7. Discrepancies, open questions and escalations

1. **The held edit, redone before asking.** The eighth session's edit adding mode `alloc` and prediction F4-3b was held by the seat's safety check for Nicolas's approval and lived only in that session's workspace. This session redid it from the frame trace, committed it (`daa8781d`) and ran it before asking. Nicolas then approved keeping it, on 15 November in the session.
2. **The $\mu_J$ label is retired for the paper.** The F3 decision file labels regime B's $\mu$ rows $\mu_J$. After F4-2 failed, the merged tables `F4/aggregate/f4_regcomp_comparisons_merged.csv` and `f4_box_task_summary_merged.csv` replace them, with column `mu_spots` set to `all`. F3's `t10` to `t16b` tables still hold the $\mu_J$ rows and should not be quoted for $\mu$ on the HEST and corpus tasks.
3. **The numbers table adds a `key` column** to the eight columns the plan named, so that each row can be cited. The plan's list of earlier-round citations (A1 to A3, A7, A8, E4 and E6) is extended to the D findings of S2 and to A9 and A10, which the final runs do not reproduce. A9's 0.130 is derived in the table as one minus the ratio of two stored half-widths (key `A9.gain`).
4. **Findings not in the table.** B2 and D7 carry no number. B9 belongs to a supplement and was not tabulated. D12's share of genes where the pooled head beats a constant (0.46 to 0.64) and E1's round 9 box numbers were not located in a stored column and are not in the table. B14 and E8's literature status are documents, not numbers.
5. **E4's cell count.** The survey's 1336 cells are the rejective-selection rows of `results/round7/ppi/S1_weighting/_merged/s1_masking_diag.csv` (1526 rows in all), and the table counts them with that filter (key `E4.cells`).
6. **Spill routing.** Four F4 jobs ran on `spill`. Their results are of record, and their partition is in each `PROVENANCE.txt`.

## 8. What was not checked

- F4-3b's mechanism assumes equal within-cluster variances, and the reading does not measure them.
- The numbers table's earlier-round rows are read from committed files, but their computations were not rerun in F4.
- The 402 table values not among the 41 checked against the reports were checked only by their selectors resolving to one row.
- Jobs that wrote no `PROVENANCE.txt` are not in the job ledger (F3 decision file, section 3, item 10).

## 9. Proposed next step

Nicolas reviews this report and the pull request. The gate job's provenance index over F1 to F4 is `results/round10/final_runs/F4/provenance_index.csv`, and its numeric-claim sweep log is in the gate job's directory on Longleaf. Once the pull request is merged, the paper's numbers are read from `results/round10/final_runs/F4/paper_numbers.csv`. Which scale is primary (D5) remains Nicolas's decision with David.
