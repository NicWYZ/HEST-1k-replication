# Round 4, the PPI track, final report (covering Q1 to Q5)

The instruction is `docs/decisions/round4_ppi_track.md`, with addendum 1, the Q1 decision memo, the Q3 decision memo (`docs/decisions/round4_ppi_Q3_decisions.md`) and addendum 2 (`docs/decisions/round4_ppi_addendum2.md`), all transcribed in `docs/round4_ppi_plan.md` (sections 1 to 14). The format is the instruction's section 8, as in the Q1 and Q3 reports. The branch is `round4-ppi`, and the report is dated 2 October 2026.

## 1. Stage and status

Interval 3 (Q4a, Q4 and Q5) is complete and this report is the final gate of the track. The work stops here. Q1 and Q2 with Q3 were reported at their gates in `docs/round4_ppi_Q1_report.md` and `docs/round4_ppi_Q3_report.md`. This report carries interval 3 in full and restates the earlier verdicts in the predictions table of section 5.

- Q4a recomputed every design-target row of Q2 and of Q3 regime A under the new rule `c_crossfit_design` on all six task variants, with the same draws and seeds. The rows under the old rules reproduce interval 2 exactly.
- The estimator definition is final (`docs/round4_ppi_estimator_definition.md`), and the theory document has its section 5 (`docs/round4_ppi_theory.md`).
- The theorem check was rerun with per-replicate $\hat\lambda$ kept, which scores Q4.3.
- CR2 was checked on the spot-weighted slope in simulation.
- Q4 built the real-data tables for CCRCC, CCRCC merged, Indiana kidney, lung Xenium and both ACS variants, the gene axis on CCRCC and Indiana, the two-way supplement and the IDC $\theta_1$ illustration.
- Q5 built the joint design table from the conformal track's C3 outputs on `main` and the round-5 cluster table.

One finding changes how the earlier reports should be read. On lung Xenium the design-target PPI estimator under `c_crossfit_design` has less than half the classical variance for every encoder (section 6.1). The Q3 report's statement that donor-weighted PPI loses on every HEST task holds for the old rule and for the Visium tasks, but not for lung under the final rule.

## 2. What was run

Commits on `round4-ppi` since the Q3 merge (`763e684`), oldest first:

- `cf1c7f9`, the Q3 decision memo, plan section 14 and section 12.4, and predictions Q4a.1, Q4.3 and Q4.4;
- `8b4e637`, `c_crossfit_design`, the $\hat\lambda$ standard-error outputs, the masking and regimes flags, the Q4a unit tests and the interval-2 reproduction check;
- `aa71028`, the theorem simulation with per-replicate half $\hat\lambda$;
- `fda9e6a`, theory section 5;
- `8e540d1`, addendum 2 as plan section 14.9;
- `89adc25`, the merged Q4a recompute and its merge script;
- `985c2bd`, the final estimator definition, the theorem check v3 and the spot-weighted CR2 check;
- `5ed0ca8`, the merged Q4 tables, gene axis, two-way supplement, IDC illustration, ACS application and the Q4 scores;
- `2104c25`, the joint design table;
- `4e0a3c7`, the round-5 cluster table;
- the commit carrying this report.

### Units

| Unit | Frame | Where it ran | Output in this tree |
|---|---|---|---|
| Q4a CCRCC | 30f92869-3c48-4ca7-aea4-4a59afc9e6e0 | local, 2 processes | `results/round4/ppi/Q4a_recompute/` |
| Q4a Indiana | 29d26232-3024-422c-8c8b-0dd27509ba09 | local | same |
| Q4a ACS | e2341968-ca72-46c3-a417-31beb69f6202 | local | same |
| Q4a lung | 040a77a6-04af-44f8-9fc3-a5a62d075ff8 | local, 1 process | same |
| Theorem Q4.3 | ab674f84-25c3-4e5f-9a25-e0dbd7583e34 | local | `results/round4/ppi/Q2_theory/theorem_v3/` |
| Spot CR2 | 95109aa8-7465-4c8e-bcf5-655491481b5e | local | `results/round4/ppi/Q4_tables/spot_cr2_check/` |
| Q4 CCRCC $\theta_3$ and gene axis | 8a3ad045-482e-4604-9184-5d7d08b4ba73 | Longleaf 3464054, 3464055, 3464056; local masking | `results/round4/ppi/Q4_tables/unit_tables/CCRCC_t3/`, `gene_axis_units/CCRCC/` |
| Q4 CCRCC $\theta_2$ and IDC | 6073c807-1027-4f5a-ac00-79f4ee34b59a | local assembly | `unit_tables/CCRCC_t2/`, `idc/` |
| Q4 Indiana $\theta_3$ and gene axis | 8c744e5a-ce3d-4fdb-98b9-29297bf7255d | Longleaf 3464104, 3464105, 3464108; local masking | `unit_tables/INDIANA_t3/`, `gene_axis_units/INDIANA/` |
| Q4 Indiana $\theta_2$ | e27ee32e-6544-407d-a691-f42069b38e46 | local assembly | `unit_tables/INDIANA_t2/` |
| Q4 lung $\theta_3$ | 97fc8009-f11d-47a5-8f76-4a9b683f3b44 | local assembly | `unit_tables/LUNG_t3/` |
| Q4 lung $\theta_2$ | 6120a7db-9618-4a93-82be-7004cc3c2d36 | local assembly | `unit_tables/LUNG_t2/` |
| Q4 ACS | cb1d3ea8-03e6-4479-a83c-bef0501bc732 | local | `unit_tables/ACS/`, `acs_phase1/` |
| Two-way | 3f23070f-dd2c-4000-83c1-b350e6efd8a2 | Longleaf 3463998 (file harvest); local diagnostic | `two_way/` |
| Cluster table | c9706800-a066-401a-8aa0-678d1e9e079d | Longleaf 3511943 | `results/round4/ppi/Q5_joint/` |

The Q4 directories above are under `results/round4/ppi/Q4_tables/`, and every Slurm job of the interval is listed in `results/round4/ppi/interval3_slurm_jobs.csv`. The code delivery to the Longleaf track clone ran as Slurm job 3463047 and fast-forwarded the clone from `de3b71f` to `aa71028` (`results/round4/ppi/interval3_slurm_jobs.csv`).

### Local runs

Nicolas allowed local compute in chat at the start of interval 3, recorded as plan section 12.4. Every local run carries a `PROVENANCE` file in the directory named in the unit table. The `exit_code 1` lines in those files come from the macOS `/usr/bin/time -l` wrapper failing in the sandbox after each script finished. Completion was judged from each run's summary JSON, final log line and row count (`results/round4/ppi/Q4a_recompute/PROVENANCE.md`).

The laptop slept twice and the local repo moved to `/Users/nicolaszhang/hest-1k/` during the interval. Four lung cost-ratio runs failed when the old path vanished and were rerun with the same seeds after their partial files were deleted (`results/round4/ppi/Q4a_recompute/PROVENANCE.md`). Two CCRCC regime B gene-axis runs were rerun after the move and a sleep (`results/round4/ppi/Q4_tables/gene_axis_units/CCRCC/PROVENANCE.txt`).

## 3. Acceptance checks

- The Q4a unit tests pass, 13 of 13, and the Q1b tests pass again, 135 of 135 (`results/round4/ppi/Q4a_recompute/tests/q4a_tests_stdout.txt`, `q1b_tests_rerun_stdout.txt`).
- In every Q4a unit the rows for rules none and `c_crossfit` match the interval-2 merged files with maximum absolute difference 0.0 and no unmatched rows (`results/round4/ppi/Q4a_recompute/unit_records/*_reproduction_check.csv`).
- The theorem check v3 reproduces the v2 ratios exactly (`results/round4/ppi/Q2_theory/theorem_v3/PROVENANCE__GL6.txt`).
- Every Q4 unit table matches its source rows exactly on every numeric column (the unit `PROVENANCE` files under `results/round4/ppi/Q4_tables/unit_tables/`).
- The numeric-claim sweep (`code/scripts/verify_numeric_claims.py` with `.verify-exceptions` and `.verify-derived`) over this report, the estimator definition, the theory document, the plan and the Q1 and Q3 reports leaves one unresolved claim. It is 0.32 in section 9 of `docs/round4_ppi_Q3_report.md`, a document not changed in interval 3, and it is left as found (`results/round4/ppi/final_gate_sweep.tsv`). Ten exceptions were added in this commit, each with its reason in `.verify-exceptions`. They are section references, prediction thresholds transcribed in the plan, two worked-example values and one range endpoint.
- The C3 file read for Q5 decompresses to md5 `2c3ceaa42528a1e3ad2979dc1161e542`, the value addendum 2 names (`results/round4/ppi/Q5_joint/PROVENANCE_joint.txt`).

## 4. What differs between the arms of each comparison

- `c_crossfit_design` against `c_crossfit` on the design target. Same halves and seeds. The two rules differ only in the objective minimised on the tuning half, which for the new rule is the between-donor variance of the textbook-form rectifier with no unlabelled term (`docs/round4_ppi_estimator_definition.md`).
- Regime A against regime B. Regime A labels every spot of $n_L$ donors and regime B labels $m$ spots on every donor, at equal unit budget or at a budget matched under the cost ratio $c_d/c_s$.
- CR2 against CR1. Same estimate, a different leverage adjustment and reference degrees of freedom.
- The gene axis. The CCRCC and Indiana encoders were run on the union of the per-fold training-only gene lists, 459 genes on CCRCC and 391 on Indiana, which differs from the 50-gene Q2 list. The intersection (49 and 62 genes) is the sensitivity check (`results/round4/ppi/Q4_tables/q4_gene_axis_summary.csv`).

## 5. Predictions against outcomes

Interval-3 predictions are scored in `results/round4/ppi/Q4_tables/q4_prediction_scores.csv`. Earlier verdicts are copied from the Q1 and Q3 reports.

| prediction | verdict | source |
|---|---|---|
| Q1.1 | partly held; CR2 not tested at Q1, tested in Q1b.3 | Q1 report section 5 |
| Q1.2 | partly held | Q1 report |
| Q1.3 | coverage held; width cost 3.2%, just over | Q1 report |
| Q1.4 | refuted (dropped by the Q1 memo) | Q1 report |
| Q1.5 | refuted, as plan section 8 item 3 expected | Q1 report |
| Q1b.1 | held in part | Q3 report section 5 |
| Q1b.2 | refuted | Q3 report |
| Q1b.3 | held except one margin | Q3 report |
| Q1b.4 | refuted | Q3 report |
| Q2.1 | refuted | Q3 report |
| Q2.2 | refuted | Q3 report |
| Q2.3 | refuted | Q3 report |
| Q2.4 | held on 3 of 5 scored tasks | Q3 report |
| Q2.5 | refuted as stated | Q3 report |
| Q2.6 | refuted | Q3 report |
| Q2.7 | refuted | Q3 report |
| Q3.1 | refuted at Q3; reversal clause refuted here | Q3 report; `q4_prediction_scores.csv` |
| Q3.2 | held for the design half on HEST | Q3 report |
| Q3.3 | partly held, 6 of 20 task and predictor pairs | `q4_prediction_scores.csv` |
| Q3.4 | held for regime B, refuted for regime A | Q3 report |
| Q4a.1 | partly held, 19 of 32 criteria | `q4_prediction_scores.csv` |
| Q4.1 | partly held, 7 of 12 criteria | `q4_prediction_scores.csv` |
| Q4.2 | held for HEST; the ACS clause has nothing to report | `q4_prediction_scores.csv` |
| Q4.3 | refuted as stated, 21 of 24 cells | `q4_prediction_scores.csv` |
| Q4.4 | refuted | `q4_prediction_scores.csv` |

Unless a sentence names another file, every number below is read from `results/round4/ppi/Q4_tables/q4_prediction_scores.csv`.

**Q4a.1, partly held.** The tuned $\lambda$ no longer falls with $n_L$ on CCRCC. The median at $n_L = 16$ minus the median at $n_L = 8$ is 0.0323 for `hoptimus0`, 0.0807 for `uni_v2` and 0.0284 for `resnet50`, all within 0.1. The second clause fails in part. The design-target ratio at $n_L = 12$ and 16 is no larger than at $n_L = 8$ in 9 of 21 HEST encoder cells, and at $n_L = 16$ it is larger on every CCRCC and CCRCC merged encoder, by 0.0250 to 0.0904. CCRCC `uni_v2` is below 0.9 at every $n_L \ge 6$ (0.7931, 0.8440, 0.8138 and 0.8690 at $n_L$ = 6, 8, 12 and 16). Lung `hoptimus0` is below 0.75 at $n_L$ = 6, 8 and 12 (0.4580, 0.4282, 0.4119) and equal to 1 at $n_L = 4$, where the estimator is classical by the $n_L < 6$ rule. The memo's clause "at every $n_L$" cannot hold at $n_L = 4$ under that rule.

**Q4.1, partly held.** The width ratio correlates more strongly with the cluster-level $R^2$ than with the unit-level Pearson correlation in 5 of 6 encoder cells. On CCRCC the Spearman correlations with the cluster-level $R^2$ are $-0.864$, $-0.898$ and $-0.803$ for `hoptimus0`, `uni_v2` and `resnet50`, against $-0.424$, $-0.445$ and $-0.244$ with the unit Pearson correlation (`q4_gene_axis_summary.csv`). On Indiana `uni_v2` the order is reversed. The share of genes gaining more than 5% is above a third on all three CCRCC encoders (0.477, 0.606, 0.407) and on Indiana `hoptimus0` (0.506), and below it on Indiana `resnet50` (0.064) and `uni_v2` (0.299).

**Q4.2, held for HEST.** No HEST task has a crossed second grouping. The lung slides contain the donors, with 4 slides holding 4, 5, 2 and 4 donors, and every other second grouping is nested in the donor (`results/round4/ppi/Q4_tables/two_way/q4_two_way.csv`). The ACS PUMS 2018 file is a single survey year, so the state-by-year two-way variance has nothing to report.

**Q4.3, refuted as stated.** The observed tuning cost is within 0.03 of the prediction in 21 of 24 cells, with a largest difference of 0.0426. With the $G_U$ term added the count is 22 of 24 and the largest difference 0.0413.

**Q4.4, refuted.** Under `c_crossfit_design` at $n_L \in \{8, 16\}$ the sign of the variance ratio minus 1 agrees with the sign of $\text{se}(\hat\lambda)^2 - \hat\lambda^2$ in 23 of 36 task and predictor cells, and in 9 of 21 encoder cells. The prediction asks for 18 of 22.

**Q3.3, partly held.** The predicted crossover cost ratio is within a factor of two of the empirical one in every cell for 6 of 20 task and predictor pairs, all four CCRCC arms and both ACS PUMA arms. In 181 of 240 cells regime B is narrower wherever it is affordable, so the empirical crossover is set at the affordability limit (`results/round4/ppi/Q4a_recompute/q4a_crossover.csv`).

**Q3.1, reversal clause refuted.** At $c_d/c_s = 1000$ only lung has affordable regime B cells, and regime A is narrower in 5 of 16 of them, with median width ratio regime B over regime A 0.7548 (superpopulation, $\theta_3$ donor-weighted, `c_crossfit`). Under $c_d/c_s = 10$ the median ratio is 0.5150 and regime A is narrower in 16 of 232 cells (`results/round4/ppi/Q4_tables/q4_report_numbers.csv`, names `q31|...`).

## 6. Results

### 6.1 The gain on real data, recomputed (the section 6.1 table)

The full table is `results/round4/ppi/Q4a_recompute/q4a_table61.csv`, at every $n_L$, both targets, $\theta_3$ and $\theta_2$, both populations, and rules none, `c_crossfit` and `c_crossfit_design` side by side. Figure `results/round4/ppi/Q4_tables/fig_q4_design_ratio_by_nL.png` shows the design-target $\theta_3$ donor-weighted rows.

| task | predictor | $n_L=6$ | $n_L=8$ | $n_L=12$ | $n_L=16$ | old rule, $n_L=8$ |
|---|---|---|---|---|---|---|
| CCRCC | `hoptimus0` | 0.8706 | 0.9634 | 0.9344 | 1.0537 | 1.0281 |
| CCRCC | `permuted` | 1.0009 | 1.0055 | 1.0130 | 1.0043 | 1.0039 |
| CCRCC | `resnet50` | 0.9151 | 1.0023 | 1.0130 | 1.0543 | 1.0108 |
| CCRCC | `uni_v2` | 0.7931 | 0.8440 | 0.8138 | 0.8690 | 0.8576 |
| CCRCC_merged | `hoptimus0` | 0.9473 | 1.0069 | 0.9724 | 1.0829 | 1.0114 |
| CCRCC_merged | `permuted` | 1.0287 | 1.0234 | 1.0162 | 1.0134 | 1.0180 |
| CCRCC_merged | `resnet50` | 0.9358 | 0.9867 | 0.9354 | 1.0681 | 0.9748 |
| CCRCC_merged | `uni_v2` | 0.8261 | 0.8313 | 0.8160 | 0.8966 | 0.8724 |
| INDIANA_KIDNEY | `hoptimus0` | 0.9566 | 0.9752 | 0.9857 | 0.9715 | 0.9572 |
| INDIANA_KIDNEY | `permuted` | 1.0236 | 1.0346 | 1.0364 | 1.0264 | 1.0312 |
| INDIANA_KIDNEY | `resnet50` | 1.0244 | 1.0352 | 1.0644 | 1.0525 | 1.0213 |
| INDIANA_KIDNEY | `uni_v2` | 0.9692 | 0.9835 | 1.0174 | 0.9879 | 0.9713 |
| LUNG_XENIUM | `hoptimus0` | 0.4580 | 0.4282 | 0.4119 | n.a. | 0.6268 |
| LUNG_XENIUM | `permuted` | 1.0328 | 1.0394 | 1.0545 | n.a. | 1.0341 |
| LUNG_XENIUM | `resnet50` | 0.5543 | 0.5396 | 0.5348 | n.a. | 0.6954 |
| LUNG_XENIUM | `uni_v2` | 0.4938 | 0.4703 | 0.4578 | n.a. | 0.6488 |
| ACS_STATES | `package` | 0.4510 | 0.4335 | 0.3358 | 0.3984 | 0.4440 |
| ACS_STATES | `permuted` | 0.9705 | 0.9920 | 0.9629 | 1.0208 | 0.9864 |
| ACS_CA_PUMA | `package` | 0.2271 | 0.1882 | 0.1695 | 0.1676 | 0.2090 |
| ACS_CA_PUMA | `permuted` | 1.0682 | 1.0405 | 1.0353 | 1.0188 | 1.0392 |

Empirical variance ratio, PPI over classical, design target, $\theta_3$ donor-weighted, $m$ = all, median over genes of 200 draws; `c_crossfit_design` except the last column (`results/round4/ppi/Q4a_recompute/q4a_table61.csv`). Lung has 15 donors, so it has no $n_L = 16$.

On the Visium tasks the new rule leaves the picture of the Q3 report in place. At $n_L \ge 8$ the design ratio lies between 0.93 and 1.09 for every encoder except `uni_v2` on CCRCC and CCRCC merged, which stays at 0.8138 to 0.8966. On lung the new rule turns a gain that shrank with $n_L$ under `c_crossfit` (0.6268 at $n_L = 8$, 0.8742 at 12 for `hoptimus0`) into a gain that holds, 0.4119 at $n_L = 12$, with median $\hat\lambda$ 0.8650. The permuted predictor stays at or slightly above 1 on every task (`q4a_table61.csv`).

The median $\hat\lambda$ under the new rule is exactly 0.5000 in most CCRCC cells (`q4a_table61.csv`). The two halves often clip at opposite ends of $[0, 1]$, so the median of their average sits at 0.5. CCRCC `uni_v2` is the exception, rising from 0.511 at $n_L = 6$ to 0.623 at 16.

### 6.2 Q4 tables

The merged main table is `results/round4/ppi/Q4_tables/q4_main_table.csv`, with 30,304 rows (`q4_report_numbers.csv`). Each row carries a `role` column that marks the final design-target estimator, the final superpopulation estimator, the classical row and the comparison rows. The 96 superpopulation `c_crossfit` rows at $n_L < 6$ that one unit kept are dropped, because $\lambda = 0$ there by rule. Every superpopulation row states $G_U$. Regime B has no `c_crossfit_design` rows, because the rule is design-only and regime B is unchanged from interval 2.

ACS, from `results/round4/ppi/Q4_tables/unit_tables/ACS/q4_acs_gain_vs_R2_breakeven.csv`. On ACS states $\theta_2$ the package predictor's corrected cluster-level $R^2$ is 0.367, so the break-even rule puts the gain above $n_L = 9.44$. The spot-weighted superpopulation `c_crossfit` ratio is 0.752 at $n_L = 6$ and 0.822 at 8, and 1.084 to 1.205 from $n_L = 12$. That is opposite to the rule's direction. The donor-weighted ratio is 0.511 to 0.577 at every $n_L \ge 6$. On ACS PUMAs the spot-weighted $\theta_2$ superpopulation ratio is 0.106 to 0.152 at $n_L \ge 6$.

The IDC illustration (`results/round4/ppi/Q4_tables/idc/q4_idc_theta1.csv`) pools the four IDC donors for $\theta_1$ of GATA3. With $n_L = 4$ the estimator is classical by rule. The pooled donor-weighted estimate is 0.5847 with 90% interval 0.3277 to 0.8416 on $t_3$.

The lung slide diagnostic (`results/round4/ppi/Q4_tables/two_way/q4_two_way_lung_slide_summary.csv`) gives a median slide-clustered to donor-clustered CR1 variance ratio of 0.910 for the donor-weighted classical $\theta_3$ estimate and 2.738 for the spot-weighted one, over 343 genes. It rests on 4 slides and is descriptive.

### 6.3 Gene axis

Figure `results/round4/ppi/Q4_tables/fig_q4_gene_axis.png` plots the per-gene width ratio against the corrected cluster-level $R^2$. On CCRCC the relation is close to monotone for every encoder. On Indiana it is weak, and a group of genes has a corrected cluster-level $R^2$ of 1.0 with width ratio near 1 (`q4_gene_axis.csv`). The per-gene file is `results/round4/ppi/Q4_tables/q4_gene_axis.csv`, with $\hat\lambda^2 - \text{se}(\hat\lambda)^2$ beside each width ratio. Its Spearman correlation with the width ratio is $-0.713$, $-0.698$ and $-0.565$ on CCRCC (`q4_gene_axis_summary.csv`).

### 6.4 Theory additions

`docs/round4_ppi_theory.md` section 5 derives the general linear-estimand setting, the design-target ratio $S^2_r/S^2_z$, the tuning cost and the break-even $n_L > 4 + 2/R^2_{\text{cluster}}$. The allocation condition was made exact. $R^2_{\text{within}} \ge R^2_{\text{cluster}}$ is necessary, and sufficient only when the within-donor $\lambda$ equals $\lambda^\star$. Otherwise the condition carries a penalty term.

### 6.5 The joint design table

`results/round4/ppi/Q5_joint/q5_joint_design.csv` has 154 rows, one per task and regime B setting. It reads the C3 o-sweep from `main` at `cbf091dad8e952e80479213c02087a68dfd3afe0`, the merge commit of pull request #5. The conformal columns are `ghcp`, `within_plain` and `within` at $K = 10$ and $\alpha = 0.1$, averaged over encoders, folds and draws, with the finite share beside each. Where $m$ is not on the o-grid the nearest $o$ at or below $m$ is used and named in `o_used`. ACS PUMAs have no C3 counterpart.

| task | regime B setting | $m$ | regime B width ratio, $\theta_3$ | regime B coverage, $\theta_3$ | $o$ used | cheapest valid set | its coverage | its mean width |
|---|---|---|---|---|---|---|---|---|
| CCRCC | cd_cs_100_vs_A_nL4_B2400 | 14 | 0.827 | 0.893 | 10 | `within_plain` | 0.910 | 2.321 |
| CCRCC | unit | 84 | 0.814 | 0.890 | 50 | `within` | 0.923 | 1.955 |
| CCRCC | unit | 168.5 | 0.827 | 0.905 | 100 | `within` | 0.902 | 1.754 |
| CCRCC | unit | 336.5 | 0.832 | 0.885 | 200 | `within` | 0.900 | 1.711 |
| CCRCC_merged | cd_cs_100_vs_A_nL4_B2400 | 18 | 0.827 | 0.905 | 10 | `within_plain` | 0.908 | 2.330 |
| CCRCC_merged | unit | 84 | 0.808 | 0.905 | 50 | `within` | 0.922 | 1.973 |
| CCRCC_merged | unit | 169 | 0.815 | 0.890 | 100 | `within` | 0.902 | 1.774 |
| CCRCC_merged | unit | 337 | 0.817 | 0.895 | 200 | `within` | 0.901 | 1.737 |
| INDIANA_KIDNEY | cd_cs_100_vs_A_nL4_B2400 | 6 | 0.844 | 0.897 | 5 | `ghcp` | 0.999 | 4.564 |
| INDIANA_KIDNEY | unit | 51 | 0.838 | 0.900 | 50 | `within` | 0.922 | 1.748 |
| INDIANA_KIDNEY | unit | 103 | 0.836 | 0.897 | 100 | `within` | 0.901 | 1.530 |
| INDIANA_KIDNEY | unit | 206 | 0.837 | 0.900 | 200 | `within` | 0.901 | 1.494 |
| LUNG_XENIUM | cd_cs_1000_vs_A_nL6_B9600 | 36 | 0.426 | 0.895 | 25 | `within` | 0.928 | 2.908 |
| LUNG_XENIUM | unit | 142 | 0.419 | 0.900 | 100 | `within` | 0.901 | 2.315 |
| LUNG_XENIUM | unit | 284 | 0.424 | 0.895 | 200 | `within` | 0.901 | 2.265 |
| LUNG_XENIUM | unit | 569 | 0.423 | 0.900 | 200 | `within` | 0.901 | 2.265 |
| ACS_STATES | cd_cs_100_vs_A_nL4_B4800 | 1 | 0.077 | 0.505 | 0 | `hcp` | n.a. | n.a. |
| ACS_STATES | unit | 32 | 0.077 | 0.870 | 25 | `within` | 0.928 | 3.341 |
| ACS_STATES | unit | 63 | 0.077 | 0.895 | 50 | `within` | 0.924 | 2.967 |
| ACS_STATES | unit | 127 | 0.078 | 0.890 | 100 | `within` | 0.902 | 2.434 |
| ACS_CA_PUMA | cd_cs_10_vs_A_nL12_B4800 | 8 | 0.079 | 0.900 | 5 | `ghcp` | n.a. | n.a. |
| ACS_CA_PUMA | unit | 9 | 0.079 | 0.920 | 5 | `ghcp` | n.a. | n.a. |
| ACS_CA_PUMA | unit | 17 | 0.079 | 0.895 | 10 | `within_plain` | n.a. | n.a. |
| ACS_CA_PUMA | unit | 35 | 0.079 | 0.890 | 25 | `within` | n.a. | n.a. |

Rows are the smallest-$m$ setting and the unit-cost settings per task (`results/round4/ppi/Q5_joint/q5_joint_design.csv`). Width ratios and coverages for HEST are medians over the three encoders, design target, donor-weighted, `c_crossfit`. The conformal coverage and width are means over encoders, folds and draws at $K = 10$, $\alpha = 0.1$, with widths over finite sets only. ACS PUMAs have no C3 counterpart, and at $o = 0$ the `hcp` row is not averaged here.

At $o = 5$ only `ghcp` is finite on the HEST tasks. Its coverage is 0.995 to 0.999 and its mean width 4.564 to 6.622 on CCRCC, Indiana and lung. `within_plain` is finite from $o = 10$ and covers 0.909 to 0.910 there (`results/round4/ppi/Q5_joint/q5_report_numbers.csv`, names `c3|...`, computed from the C3 file at `cbf091d`).

### 6.6 The round-5 cluster table

`results/round4/ppi/Q5_joint/q5_cluster_table.csv` has 261 rows, one per donor, task and encoder (72 CCRCC, 69 CCRCC merged, 75 Indiana and 45 lung, for `hoptimus0`, `uni_v2` and `resnet50`; counts in `results/round4/ppi/Q5_joint/q5_report_numbers.csv`). Each row carries the spot count, the path and row key of the donor's mean embedding in `results/round4/ppi/Q5_joint/embeddings/`, and the median over genes of the mean residual and of the within-donor residual variance. The per-gene values are in `q5_cluster_residuals_long.csv.gz`. The gene lists are the Q2 ones, 50 genes on CCRCC and Indiana and 343 on lung (`PROVENANCE_cluster.txt`).

The leave-one-out offset prediction is Q2's recalibration quantity, the other donors' offsets ridge-regressed on their mean embeddings with the donor left out. Q2 ran it only on CCRCC and Indiana with `hoptimus0`, so the column is filled on 49 rows and empty elsewhere (`q5_report_numbers.csv`). The unit's mean residual reproduces Q2's donor offset with largest difference $4.4 \times 10^{-16}$ (`cluster_unit/q5_q2_b_vs_residual_check.txt`). No analysis was done on the table, as the plan asks. The permuted arm is not included because no permuted prediction file exists. It is derived from `resnet50` at estimation time.

## 7. Discrepancies, open questions and escalations

### Escalations

1. **ACS states $\theta_2$, spot-weighted design coverage.** Under `c_crossfit_design` the design interval covers 0.720 to 0.790 at $n_L \ge 6$, against 0.780 to 0.855 for the classical interval (`q4a_table61.csv`). The estimated variance over the empirical one is near 1 for both (0.998 to 1.252 under the new rule). So the shortfall is shared with the classical estimator and looks like the skewed-contribution limit of the estimator definition, with very unequal state sizes. The Q4 ACS unit read it as a possible collapse of the variance estimate when $\hat\lambda$ is near 1, and the ratio column does not support that reading.
2. **ACS states $\theta_2$, donor-weighted variance diagnostic.** Under `c_crossfit` at every $n_L$ and `c_crossfit_design` at $n_L \ge 6$, the median of estimated over empirical variance is 204 to 1165, while coverage is 0.910 to 0.975 (`q4a_table61.csv`). Coverage that high is not consistent with intervals that much too wide. The column is a median of per-draw ratios and may be dominated by a few draws. These rows reproduce interval 2 exactly under `c_crossfit`, so the issue predates interval 3. It is not resolved.
3. **The Q4.1 gene set.** The gene axis uses the union of the per-fold lists (459 and 391 genes), predicted for every donor, with the intersection as the sensitivity check (`results/round4/ppi/Q4_tables/q4_gene_axis_summary.csv`). The Q2 tables use the 50-gene lists. This is a lead decision recorded in the unit briefs.
4. **Local runs without a fresh instruction.** The Q4 ACS unit ran its phase 1 locally, and the CCRCC $\theta_3$ unit ran CCRCC merged regime B locally (unit cost and $c_d/c_s = 100$, 4 arms, 824 to 834 s each, `results/round4/ppi/Q4_tables/unit_tables/CCRCC_t3/PROVENANCE_phase2.txt`) because interval 2 never ran it. Both are within section 12.4 but were not asked for in advance.
5. **Provenance stamps.** Several units could not see their own frame id and wrote an empty, null, placeholder or lead frame id. The lead set the true unit frame ids at commit and recorded the change in a `frame_id_note` field (spot CR2, IDC, ACS, the lung, Indiana $\theta_2$ and CCRCC $\theta_2$ tables).
6. **A stray write.** The two-way unit's kernel was left in the repo working tree and wrote one file and an empty directory there. It moved both to the Trash through the approved delete, and `git status` showed only the expected untracked file afterwards.
7. **The memo's allocation sentence.** Q3 memo section 4 item 3 says Q3.4 found the within-cluster $R^2$ above the cluster-level one for every HEST encoder. The Q3 report says every HEST encoder except `uni_v2` on CCRCC and CCRCC merged, which is what the data show (`results/round4/ppi/Q3_regimes/q3_report_numbers.csv`). Theory section 5 states the condition with that exception.
8. **Q4.3 at 21 of 24.** The three cells outside 0.03 are within 0.0426. The prediction is scored as refuted as stated.
9. **The joint design table and addendum 2 item 5.** The table does not support the "from the first spot" clause on every task. HEST regime B starts at $m = 6$ on Indiana, $m = 14$ on CCRCC and $m = 36$ on lung, because Q3 only ran the budget grid. On ACS states the regime B $\theta_3$ interval covers 0.505 at $m = 1$ and 0.640 at $m = 4$ (`q5_joint_design.csv`). The closing page quotes the addendum's paragraph with this qualification beside it.
10. **The Indiana corrected cluster-level $R^2$ of 1.0.** On Indiana, 10, 7 and 19 genes have a corrected cluster-level $R^2$ of 1.0 for `hoptimus0`, `uni_v2` and `resnet50` (`q4_gene_axis.csv`). This looks like the correction clipping on genes with almost no between-donor variance. It does not change Q4.1's verdict, but those genes should be dropped or flagged before the gene axis is used in the paper.
11. **Indiana prediction md5s for the cluster table.** The cluster unit could not find recorded md5s for the Indiana `uni_v2` and `resnet50` Q2 prediction files and reports the computed ones (`PROVENANCE_cluster.txt`). Every other input matched its Q2 record.
12. **Lung $n_L = 16$.** It is infeasible with 15 donors, so lung rows stop at $n_L = 12$ throughout.

### Discrepancies and records

- The per-gene Q4a grid `q4a_variance_grid_genes.csv.gz` (78 MB) is not committed, following the Q2 practice. It is kept as artifact version 5c67808d-e6c7-4bb1-9f19-8449ea0b3e35 (`results/round4/ppi/Q4a_recompute/PROVENANCE.md`).
- At $c_d/c_s = 1000$ the cost-matched regime B budget is not positive on CCRCC, CCRCC merged, Indiana and both ACS variants, so those tasks have no rows at that ratio.
- `origin/main` was fetched once to read the C3 file at the merge commit. Nothing from `main` was merged into `round4-ppi`.

## 8. What was not checked

- `c_crossfit_design` in simulation. Its behaviour is quoted from the real-data masking draws only.
- The regime B $\hat\lambda$ standard error, which the committed regime B code does not compute.
- Regime B at small $m$ on the HEST tasks, below the smallest budget-grid $m$ named in escalation 9.
- The ACS donor-weighted variance diagnostic of escalation 2.

## 9. Proposed next step

The track ends here. For round 5, the cluster table of section 6.6 is the input the instruction names. The three items above that affect the paper's tables are escalations 1, 2 and 10.

## What the PPI track established

On the Visium tasks the cluster-clustered PPI estimator gives little over the classical one under either target. Its design-target variance ratio lies between 0.93 and 1.09 at $n_L \ge 8$ for every encoder except `uni_v2` on CCRCC and CCRCC merged, at 0.81 to 0.90 (`results/round4/ppi/Q4a_recompute/q4a_table61.csv`). On lung Xenium the final design rule brings the variance to 0.41 to 0.55 of the classical one for every encoder at $n_L \ge 6$, where the old rule's gain shrank as $n_L$ grew (`q4a_table61.csv`). The permuted predictor sits at 0.96 to 1.07 on every task, so the gains are not an artefact of the tuning (`q4a_table61.csv`). Within a task the gain tracks the cluster-level $R^2$ of the within-donor contrast, strongly on CCRCC and weakly on Indiana (`results/round4/ppi/Q4_tables/q4_gene_axis_summary.csv`). The break-even rule $n_L > 4 + 2/R^2_{\text{cluster}}$ and the sign rule of Q4.4 do not predict the real-data gains cell by cell (`results/round4/ppi/Q4_tables/q4_prediction_scores.csv`). The estimator that remains is the textbook difference estimator with the finite-population correction and the GREG $\lambda$ for the design target, and the complement form with CR2 for the superpopulation, with no bootstrap (`docs/round4_ppi_estimator_definition.md`). At $n_L = 4$ and 6, labelling a few spots on every donor gives a narrower interval than spending the same unit budget on whole donors on every task, for the predictor shown in the Q3 report (`docs/round4_ppi_Q3_report.md` section 5). For the superpopulation $\theta_3$ donor-weighted interval under the cost ratio $c_d/c_s = 10$ it is narrower in 216 of 232 cells, and at 1000, where only lung can afford it, in 11 of 16 (`results/round4/ppi/Q4_tables/q4_report_numbers.csv`).

Addendum 2 item 5 asks this page to carry its statement of what the joint table supports, which reads "on these data the same few labelled spots per donor serve the confidence interval (regime B, Q3) from the first spot and the prediction set only from about ten spots, so a labelling design of tens of spots on every donor serves both targets, while a design of a few fully labelled donors serves neither as well." The table supports the second half (`results/round4/ppi/Q5_joint/q5_joint_design.csv`). From $o = 10$ the `within_plain` set is finite and covers about 0.91, while at $o = 5$ only `ghcp` is finite, with mean width 4.564 to 6.622 on CCRCC, Indiana and lung against 1.879 to 2.947 for `within_plain` at $o = 10$ (`results/round4/ppi/Q5_joint/q5_report_numbers.csv`). The table does not test the "from the first spot" clause on HEST, because the smallest regime B setting is 6 spots per donor on Indiana and 14 on CCRCC. On ACS states the regime B slope interval covers 0.505 at one spot per state (`q5_joint_design.csv`).
