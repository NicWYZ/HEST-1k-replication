# Round 10, track `final-runs`, gate F2 report

*Written on 11 November 2026 by the fifth session of track `final-runs` (frame `10b1be42-01a3-406b-b386-7580e28b98ad`), from the track plan `docs/round10/tracks/final-runs/round10_final_runs_plan.md` (sections 5 to 6) and the brief `docs/round10/i01/final-runs/round10_final_runs_brief.md` (F2 items 1 to 8). The F2 computation was run by the third and fourth sessions (frames `311f766a-9eaf-4808-9fe7-7f16ec282d07` and `e57d4a98-8078-4281-8c49-84c1df952f94`). Every number below is read from the file named beside it. The committed aggregates are under `results/round10/final_runs/F2/`, and the report's own selections and summaries of them are in `results/round10/final_runs/F2/report_tables/`, written by `code/scripts/round10_final_runs_f2_report_tables.py`, which re-estimates nothing. Paths below that begin `report_tables/`, `aggregate/`, `aggregate_limits/`, `aggregate_regimeB/`, `diagnostics/` or `refit_norm/` are relative to `results/round10/final_runs/F2/`. The bulk outputs stay on Longleaf under `/work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F2/`.*

## 1. Stage and status

Stage F2 (inference) is complete. Every item of brief F2 has an output on every task, encoder, scale and estimand it names, except the bootstrap arms, which ran under `uni_v2` only as the plan set out (section 8). The switch rule keeps $\hat V_w$ as the primary variance of the cross-fitted form. FR2 and FR3 hold, FR4 holds for $\theta_3$ at its threshold on CCRCC, FR5 and FR6 are refuted for $\theta_3$, and part 1 of P10.1 is refuted on all three tasks. Every anchor reproduced, every unit's `PROVENANCE.txt` reads `COMPLETED`, and no job is running. The gate asks Nicolas to review the scores and the points of section 7 before F3's methods are written. No stop condition of the brief was met.

## 2. What was run

All jobs ran on Longleaf through the submission route, which names jobs `claude-science-<uuid8>`, so they are identified by Slurm id. Every job is a row of `results/round10/final_runs/job_ledger.csv` with its partition, node, times, state, wall time, requested memory, peak memory and commit. The 159 rows of the fourth session and of this one were added in this commit, read from `sacct` by `code/scripts/round10_final_runs_ledger_rows.py` (`report_tables/f2_ledger_new_rows.csv`). Every F2 job landed on `spill`.

The units, in order (scripts with md5 as recorded in each unit's `PROVENANCE.txt`, commits abbreviated to 8 characters).

- **F2.0, the CellViT download** (`round10_final_runs_f2_cellvit_download.py`, commit `b934827e`, Slurm `8783097`, 65 s), approved by Nicolas on 10 November, 148 parquets from `MahmoodLab/hest` at revision `7e8d5a0b`.
- **F2.0, cluster values.** `round10_final_runs_f2_cluster_values.py` v1 (md5 `8f1fb04428949c082104bfd58eed53bc`, commit `99de9998`, Slurm `8783376`), v1b for ACS $\theta_3$ (md5 `202ccfe23862a60810d96e50955d8010`, commit `a1ab8ee3`), v2 for the corpus (md5 `f0ea6142ec150b5705347c54d970c5c3`, commit `b1f7e626`) and v3 on the refitted normalised scale (md5 `202ccfe23862a60810d96e50955d8010`, commit `09e2d402`, Slurm `8825178`, 13 s). Anchor 2 against round 5's donor values (`round10_final_runs_f2_anchor_r5.py`, md5 `f460c703b20155339bc8326d1ba0bc3f`, commit `3477e7a1`).
- **Option (b), spot morphology** (`round10_final_runs_f2_morphology.py`, md5 `b75ef531772bdcefdbd887c975850926`, with round 4's `round4_data_morphology.py`, md5 `987d005ad66e9f8bdbd7544901298c4a`, commit `e5dfd2f0`), six jobs, Slurm `8784343` to `8784410`, and its kidney diagnostic (`round10_final_runs_f2_morph_diag.py`, commit `ddf3fa96`).
- **Regime A** (`round10_final_runs_f2_regimeA.py`, md5 `774f14de3ed57d6eb110dec4128cec1c`, with `round10_final_runs_estimators.py`, md5 `9580a38223ad46f5e141626572254fea`). The smoke test and anchor (commit `dd25eb27`, Slurm `8784277`), 40 units on $\log(1 + y)$, $\log(1 + 10^4 y/n)$ and round 9's pairing (commits `51573c1d`, `75be395c` and `25619ba5`, listed in `F2/regimeA_units.csv`), and 15 units on the refitted normalised scale `norm_refit` (commit `09e2d402`, Slurm `8827356` to `8827473`, 2.4 to 54.7 minutes, MaxRSS at most 569120K).
- **Limits arms** (`round10_final_runs_f2_limits.py`, md5 `00f9df41de45d88bed984189c3639bde`, commit `52285e7a`, with round 4's and round 5's estimator modules, `round5_ppi_balance.py` and round 7's `round7_ppi_s2_comparators.py` at the md5s of round 5's snapshot `9185bc6b`). The smoke test and anchor (Slurm `8803183`) and 94 units (Slurm `8803183` to `8808214`, 27 s to 46 minutes, MaxRSS at most 818424K).
- **Regime B** (`round10_final_runs_f2_regimeB.py`, md5 `05f9c7a1a24a4bff1041ff5094dae011`, with round 5's `round5_ppi_e3_twolevel.py` and `round5_ppi_twolevel.py`). The smoke test and anchor (commit `6fa3cef5`) and 31 units (commit `a4c7065f`, Slurm `8814479` to `8823729`, 49 s to 12.6 minutes).
- **The HEST heads refitted on the normalised outcome** (`round10_final_runs_f2_refit_norm.py`, md5 `6f7a1973fbe10b3e215172d32ff6fbaf`, commit `a4c7065f`, with round 3's `round3_a0_harness.py` md5 `0ad7ae8efe554c1f285e5f384a9fb7f5` and `round3_b1_ppi.py` md5 `544721f07cb3d74dc5b92456d61fe450`, and round 4's INDIANA and LUNG drivers), 12 units, Slurm `8823487` to `8824275`, 3.8 to 22.8 minutes, MaxRSS at most 8905244K.
- **Aggregations.** Regime A v3 with scores v3 (`round10_final_runs_f2_aggregate.py` md5 `33ded614e47a8410bafb203d3528c51e`, `round10_final_runs_f2_scores.py` md5 `7299bd9e1cf75f660924fa4c98095b98`, commit `1bb97a65`, Slurm `8827807`, 41 s). Limits and regime B (`round10_final_runs_f2_limits_aggregate.py` md5 `7acdb64ccea02fb704a5e571dd5d62bb`, `round10_final_runs_f2_regimeB_aggregate.py` md5 `a80a68637dea25ce6c385a98cf47c365`, commit `6b7e0f66`, Slurm `8824760`, 38 s).
- **F2.5 to F2.8 diagnostics** (`round10_final_runs_f2_diagnostics.py`, md5 `f0c32b1017ca8832f3e4b4c9b1807d15`, with round 9's `round9_fewcluster_hest_kappa.py` md5 `8ea0be3f99cb3e640e29ecdcbfe54ffe` and `round9_c0_diagnostics.py` md5 `1b23b360fb05d825c13eae29b0a8fa26`). Version 1 (commit `44f252a9`, Slurm `8824693`) and version 2 with `norm_refit` (commit `1bb97a65`, Slurm `8827808`), 84 to 120 s, MaxRSS at most 4210524K. Version 2's tables are the committed ones.
- **This session.** The report tables and the ledger rows (`round10_final_runs_f2_report_tables.py` md5 `76aeb73c38ac9b1d2d54dcdec1eb04b2`, `round10_final_runs_ledger_rows.py` md5 `1623ac00e248c3afa655d8a81b57f494`, commit `10d00554`, Slurm `8869064`), then the numeric-claim sweep and the provenance index (section 3).

**Sub-agents.** The option (c) search used three sub-agents of the third session, `Pathology` (frame `0907eef7-a0c0-4d0c-9261-7d9f437cf409`), `Survey` (`d24387cf-ee0b-4127-a924-d18f82c9ed88`) and `Econometrics` (`4fdd907f-4a4f-44ab-89ad-fe7d61f81fbe`), under the written brief of plan section 5c. They ran no job and no git and downloaded no data. Their merged logs are in `option_c_search/` (section 6.9). This session used no sub-agents.

## 3. Acceptance checks and exit items

**Anchors, every one written before its run.** The first four were recorded in the plan's dated notes from files on Longleaf (`F2/cluster_values_v1/f2_anchor_c0.csv`, `F2/anchor_r5_CCRCC/f2_anchor_r5.csv` and `F2/morphology/<task>/morph_anchor.csv` under the bulk directory).

| anchor | rule | result | file |
|---|---|---|---|
| Cluster values, $\mu$ against round 9's `mean_y` and `mean_f` (four HEST variants, ACS) | $10^{-9}$ relative | largest 1.5e-14, spot counts equal | `docs/round10/tracks/final-runs/round10_final_runs_plan.md`, section 6 |
| Cluster values, $\theta_3$ against round 9's donor slopes | $10^{-9}$ relative | largest 4.3e-12; ACS v1b 1.2e-14 | `docs/round10/tracks/final-runs/round10_final_runs_plan.md`, section 6 |
| $\theta_3$ and $\theta_2$ against round 5's `donor_arrays` on CCRCC | $10^{-9}$ relative | 2.0e-13 and 1.7e-12 | `docs/round10/tracks/final-runs/round10_final_runs_plan.md`, section 6 |
| Option (b) spot features against round 4's tables | $10^{-6}$ | largest difference 0 on 31,425, 134,333 and 23,990 shared rows | `docs/round10/tracks/final-runs/round10_final_runs_plan.md`, section 6 |
| Regime A driver against round 9's `i34_williams_summary` | exact | 34 of 34 rows, largest differences 1.1e-16 in coverage and 2.2e-16 in width | `report_tables/r04_controls_and_anchor.json` |
| Limits arm on round 5's E4b reference cell | `coverage_median` 0.85775 | 0.85775 and width 0.113623215193696, equal on all 4 D0 rows | `limits_smoke/limits_anchor_r5.csv` |
| Regime B on round 5's E3 cell (CCRCC, $\theta_3$, $m = 10$, `C_ppi`) | within 3 Monte Carlo SE | exact; all 26 rows of CCRCC `uni_v2` within 2.2e-16 | `regimeB_smoke/regimeB_anchor_r5.csv` |
| Refit with the outcome unchanged against the committed prediction files | $10^{-5}$ absolute | 12 of 12 pass, largest 4.8e-7 | `refit_norm/refit_compare.csv` |
| Diagnostics against round 9's $\kappa$, $R^2_c$, skewness and `pc1_share` | exact up to rounding | 444, 1,480 and 12 rows, largest 1.4e-15, 1.1e-14 and 4.4e-16 | `diagnostics/f2_diag_summary.json` |

**Controls inside regime A** (`report_tables/r04_controls_and_anchor.json`). Over all 1,722 cells, the constant predictor's `fix1` equals `classical` with largest coverage difference 0 and largest relative width difference 1.4e-14, and the driver's per-draw identity check holds in all 55 units, largest deviation 1.1e-14. The permuted predictor's `fix1` has median coverage 0.900 over cells (0.858 to 0.940), and its median width is below `classical`'s in 0.23% of cells, the smallest ratio being 0.981.

**Completeness.** Regime A has 55 of 55 units completed and 1,722 cells. The limits aggregation found 94 of 94 units, 1,452 cells matching regime A's cells without `norm_refit` one for one, no duplicate rows, and the identities rule `none` = `classical` (7.1e-15) and `a_b1` = `b_cluster` (0) (`aggregate_limits/f2_limits_checks.json`). Regime B has 31 of 31 units, 147,603 rows and its cluster means equal this track's within 1.8e-10 relative (`aggregate_regimeB/f2_regimeB_checks.json`).

**Provenance.** The index `results/round10/final_runs/F2/provenance_index.csv` covers the 283 `PROVENANCE*.txt` files under `F1/` and `F2/` of the bulk directory, written by `round10_final_runs_provenance_index.py` with stages F1 and F2 (its printed counts in `results/round10/final_runs/F2/provenance_index_stdout.txt`). Of these, 259 record a snapshot commit, and every one is an ancestor of the gate commit. All 1162 recorded script md5s equal the md5 of the script at that commit. The other 24 are the `PROVENANCE__predict__*` files that round 3's and round 4's prediction code writes inside each refit unit's `as_is/` and `norm/` directories. They record no snapshot commit and no script md5, and the unit's own `PROVENANCE.txt` above them carries both.

## 4. Variables that differ between the arms of each comparison

- **`fix1` against `classical`.** The point estimate subtracts the predictions' labelled mean and adds their population mean, and the variance uses $s_{z - f}^2$ in place of $s_z^2$. The draws, $n_L$, finite-population factor, $t_{n_L - 1}$, population and nominal level are the same.
- **`xf2` against `fix1`.** The cross-fitted form estimates a coefficient on one half and applies it on the other, with Williams' arrangement and $t_{n_L - 2}$, and its four variances differ from `fix1`'s. Same draws and population. `xf2_r5` uses round 5's clipped coefficient, `xf2_fix1` the coefficient fixed at 1 and `xf2_ols` the unclipped one.
- **P10.1 part 1, round 10 against round 5** (plan section 5.8). The variance ($\hat V_w$ against round 5's linearised `textbook_t|fpc|lin|xf`), the placement of the coefficient, the reference distribution ($t_{n_L - 2}$ against $t_{n_L - 1}$), the draws and their number (20,000 against 2,000). The estimand, population, genes, encoder and scale are the same.
- **Limits arms against regime A.** The limits arms use the first 2,000 of regime A's draws, round 4's and round 5's code paths and round 5's interval labels. Kluger's bootstrap uses its own resampling at $B$ = 2,000. Same populations.
- **Bootstrap arms against `fix1`.** The interval construction, and the number of draws (2,000 against `fix1`'s 20,000). `uni_v2` only.
- **Regime B forms.** `C_fix1`, `C_ppi` and `C_classical` differ in the coefficient (1, cross-fitted, 0) on the same units and draws.
- **The two scales (D5).** The outcome, and on the HEST tasks the head (refitted, `norm_refit`, or round 9's pairing of the $\log(1 + y)$ head with the normalised outcome, `norm_r9pair`). The donors and genes are the same. The draws differ, since the seed of each population is taken from a tag that includes the scale. On the corpus tasks the head was fitted on each scale's outcome at F1.
- **Superpopulation interval.** `fix1_nofpc` against `fix1` differ only by the factor $1 - n_L/G$ on the variance.
- **Across tasks and encoders.** Platform, organ, $G$, genes, spots per donor and the encoder all differ, so no effect is named from a difference between tasks.

## 5. Predictions against outcomes

The defaults of brief section 5 apply: $\theta_3$, `uni_v2`, $\log(1 + y)$, nominal 0.90. Coverage at 20,000 draws has Monte Carlo standard error $\sqrt{0.9 \cdot 0.1/20{,}000} = 0.0021$ near nominal, and at 2,000 draws 0.0067.

| prediction | outcome | verdict |
|---|---|---|
| P10.1, part 1. The tuned interval's median coverage at 8 labelled donors under the level-free variance is 0.02 to 0.05 below round 5's | `xf2_r5` with $\hat V_w$ against round 5's row: CCRCC 0.8581 against 0.85775, INDIANA_KIDNEY 0.8960 against 0.8950, LUNG_XENIUM 0.8752 against 0.8675, so the drop is -0.0004, -0.0010 and -0.0077. Round 7's rows beside them are 0.8525 (CCRCC) and 0.893 (INDIANA_KIDNEY) at both $p_a$, and with $\max(\hat V, \hat V_w)$ round 10 gives 0.8836, 0.9201 and 0.8944 (`report_tables/r13_p10_1.csv`) | refuted on all three |
| P10.1, part 2 (design ordering) | scored at F3 | not tested |
| FR2. Median $E(\hat V_w)/\text{Var}$ at least 0.95 in every cell with $n_L \ge 6$; $\hat V < 0$ in at least 0.05 of draws at 6 clusters on CCRCC and INDIANA_KIDNEY | smallest median 0.9937 over 1,432 cells (ACS, $\theta_3$, $n_L = 8$); share of draws with $\hat V < 0$ 0.197 and 0.208 ($\theta_3$), 0.180 and 0.194 ($\mu$) (`aggregate/f2_switch_decision.json`, `aggregate/f2_scores.csv`) | held |
| FR3. At 4 clusters `fix1`'s median RMSE below `classical`'s on every HEST task and ACS | $\theta_3$: 0.0468 against 0.0552, 0.0185 against 0.0191, 0.0503 against 0.0952, 0.0128 against 0.0231; $\mu$ holds on all four too (`aggregate/f2_scores.csv`) | held |
| FR4. At 8 donors, share of genes with `fix1` wider than `classical` at least 0.3 on CCRCC and INDIANA_KIDNEY, at most 0.2 on LUNG_XENIUM; narrower on ACS | $\theta_3$: 0.30, 0.32, 0.044, ACS ratio 0.554. Under the mean-width reading CCRCC gives 0.20 (section 7, item 2). For $\mu$, LUNG_XENIUM gives 0.30 (`aggregate/f2_scores.csv`, `aggregate/f2_fix1_cost.csv`) | held for $\theta_3$, at the threshold on CCRCC |
| FR5. On CCRCC at 8 donors, `fix1`'s coverage at least 0.02 higher on $\log(1 + 10^4 y/n)$ | $\theta_3$: -0.0006 with the refitted head, -0.0014 in round 9's pairing; $\mu$: 0.027 and 0.036 (`aggregate/f2_scores.csv`) | refuted for $\theta_3$ |
| FR6. On kidney Visium at 16 donors the median gene's residual max-share lies beyond round 9's frontier, and `fix1`'s median coverage is below 0.88 | $\kappa(e)$ 0.157 against `kappa_sup` 0.180 (beyond for 0.32 of genes), against `kappa_star_v1` 0.147 beyond; coverage 0.8924 (`diagnostics/f2_fr6.csv`) | refuted |
| FR7 (F3). Regime B with the coefficient fixed at 1 within 0.03 of nominal at every $m \ge 6$ | preview only. `C_fix1` within 0.0055 on the four HEST variants and within 0.0205 on ACS (`report_tables/r08d_regimeB_fr7_preview.csv`) | not tested |
| P10.3, FR8 | F3 | not tested |

## 6. Results

### 6.1 Regime A, the design simulation (brief F2 item 1)

The table gives the headline cell, $\theta_3$ at 8 labelled clusters on the primary scale under `uni_v2` (ACS by state has one population). Coverage is the median over genes. The width ratio is the median over genes of `fix1`'s median width over `classical`'s. The last column is the median over genes of the share of draws in which $\hat V$ was negative and formed no interval (`report_tables/r01_regimeA_uni_v2_primary.csv`, `report_tables/r06_fix1_cost_n8.csv`).

| task | $G$ | genes | `classical` | `fix1` (10% to 90% over genes) | `xf2`, $\hat V_w$ | `xf2`, $\max(\hat V, \hat V_w)$ | `bh_t_fpc` | width ratio `fix1`/`classical` | no interval under $\hat V$ |
|---|---|---|---|---|---|---|---|---|---|
| CCRCC | 24 | 50 | 0.849 | 0.897 (0.859 to 0.905) | 0.858 | 0.884 | 0.844 | 0.878 | 0.165 |
| CCRCC_merged | 23 | 50 | 0.849 | 0.895 (0.870 to 0.903) | 0.856 | 0.882 | 0.838 | 0.897 | 0.160 |
| INDIANA_KIDNEY | 25 | 50 | 0.896 | 0.897 (0.874 to 0.906) | 0.896 | 0.920 | 0.872 | 0.957 | 0.176 |
| LUNG_XENIUM | 15 | 343 | 0.880 | 0.887 (0.800 to 0.907) | 0.875 | 0.894 | 0.904 | 0.585 | 0.134 |
| ACS_STATES | 51 | 1 | 0.894 | 0.899 | 0.893 | 0.918 | 0.933 | 0.554 | 0.203 |
| kidney Visium | 51 | 50 | 0.906 | 0.895 (0.875 to 0.906) | 0.897 | 0.923 | 0.868 | 0.937 | 0.198 |
| breast ST | 32 | 50 | 0.877 | 0.900 (0.883 to 0.907) | 0.872 | 0.899 | 0.863 | 0.925 | 0.180 |
| bowel Visium | 18 | 50 | 0.896 | 0.888 (0.836 to 0.901) | 0.891 | 0.913 | 0.944 | 0.669 | 0.145 |
| brain Visium | 18 | 50 | 0.865 | 0.885 (0.841 to 0.903) | 0.871 | 0.891 | 0.843 | 0.948 | 0.137 |
| breast Xenium | 17 | 50 | 0.905 | 0.899 (0.867 to 0.908) | 0.898 | 0.916 | 0.921 | 0.782 | 0.154 |
| lung Xenium | 17 | 50 | 0.891 | 0.890 (0.827 to 0.904) | 0.880 | 0.903 | 0.910 | 0.664 | 0.151 |

Over the whole grid (`report_tables/r02_regimeA_grid_ranges.csv`, every encoder, scale and estimand), `fix1`'s median coverage at $n_L = 8$ has median 0.896 over the 146 HEST and ACS cells and 0.899 over the 144 corpus cells, with minima 0.843 (CCRCC_merged, `uni_v2`, $\log(1 + y)$, $\mu$) and 0.854 (bowel Visium, `resnet50`, $\log(1 + y)$, $\mu$). `classical` has minima 0.833 and 0.859, and `xf2` with $\hat V_w$ has medians 0.883 and 0.893 with minima 0.831 and 0.856. At every $n_L$ the lowest HEST and ACS cell of each of these arms is on CCRCC or CCRCC_merged, except `fix1` at $n_L = 4$, whose lowest is ACS by state. At $n_L = 4$, `fix1`'s minimum is 0.854 (ACS by state, $\mu$) and its medians 0.904 and 0.905. At the headline cell `fix1`'s coverage is at or above `classical`'s on seven of the eleven tasks. On the other four (kidney Visium, bowel Visium, breast Xenium and lung Xenium) `classical` is within 0.01 of nominal and `fix1` is below it by 0.001 to 0.012. The lowest cells of `fix1` are $\mu$ on CCRCC and CCRCC_merged and on bowel Visium.

**The bootstrap arms** (`report_tables/r03b_bootstrap_ranges.csv`, 2,000 draws and 999 resamples, `uni_v2`, 74 cells at $n_L = 4$). The pairs percentile bootstrap under-covers at few clusters and over-covers at many, with median coverage 0.771 at $n_L = 4$, 0.888 at 8 and 0.982 at 16. The wild cluster bootstrap-$t$ with Webb's weights over-covers throughout (0.937 at 4, 0.946 at 8, 0.991 at 16), at 1.17 to 1.79 times `fix1`'s width. Rao and Wu's rescaled bootstrap-$t$ covers 0.927 at 4 at 2.41 times `fix1`'s width, and 0.884 to 0.891 at $n_L \ge 8$ at 1.04 to 1.20 times. The headline cell's rows are in `report_tables/r03_regimeA_bootstrap.csv`.

### 6.2 The switch rule (brief F2 item 2)

Over the 1,432 cells with $n_L \ge 6$, on every task, encoder, scale and estimand, the smallest median over genes of $E(\hat V_w)/\text{Var}(\hat\theta)$ is 0.9937 (ACS by state, $\theta_3$, $n_L = 8$). No cell is below 0.95 and none lies within two approximate standard errors of it (`aggregate/f2_switch_decision.json`). On the 1,210 cells of the primary scales the verdict is the same. Per task the smallest median ranges from 0.9937 to 1.0211, and at most 0.02 of genes in any cell fall below 0.95 (`report_tables/r05_switch_by_task.csv`). **Under the rule, $\hat V_w$ stays primary for the cross-fitted form.** $\hat V$ is negative in a median 0.201 of draws at $n_L = 6$ (0.129 to 0.240 over 290 cells), 0.159 at 8 and 0.059 at 16 (`report_tables/r05b_frac_V_neg_by_n.csv`), which is why `xf2` under $\hat V$ alone covers only 0.73 to 0.75 on the HEST tasks at the headline cell (`report_tables/r13_p10_1.csv`).

### 6.3 The fixed coefficient's cost (brief F2 item 3)

At $n_L = 8$ under `uni_v2` on the primary scale, the share of genes where `fix1` is wider than `classical` for $\theta_3$ is 0.30 on CCRCC and CCRCC_merged, 0.32 on INDIANA_KIDNEY, 0.044 on LUNG_XENIUM, 0 on ACS, and 0 to 0.28 on the corpus tasks (bowel Visium 0, kidney Visium 0.28). For $\mu$ it is 0.46, 0.50, 0.42 and 0.30 on the HEST variants and 0.02 to 0.32 on the corpus. Across encoders the share for $\theta_3$ on CCRCC ranges from 0.30 to 0.58. On the refitted normalised scale it is 0.48 on CCRCC and 0.46 on INDIANA_KIDNEY, and in round 9's pairing 0.80 and 0.58 (`report_tables/r06_fix1_cost_n8.csv`). Where the fixed coefficient costs width, it costs little in the median. Among the $\theta_3$ and $\mu$ rows of that table, the median width ratio is at most 1.02 except round 9's pairing for $\theta_3$ on CCRCC (1.21), CCRCC_merged (1.19) and INDIANA_KIDNEY (1.03).

### 6.4 The limits arms (brief F2 item 1, same-sample tuning and Kluger's bootstrap)

Over the 1,452 cells, median over cells of median coverage (`report_tables/r07_limits_ranges.csv`) and of the median width ratio to `classical` (`report_tables/r07b_limits_width_ratio_by_n.csv`):

| arm | interval | coverage at 4 | at 8 | at 16 | width ratio at 4 | at 8 | at 16 |
|---|---|---|---|---|---|---|---|
| round 4's rule none (control) | `textbook_t\|fpc\|lin` | 0.897 | 0.894 | 0.892 | 1.000 | 1.000 | 1.000 |
| rule (a) `a_b1` = rule (b) `b_cluster` | `textbook_t\|fpc\|lin` | 0.840 | 0.868 | 0.885 | 0.750 | 0.853 | 0.953 |
| rule (c) `c_crossfit_design` | `textbook_t\|fpc\|lin\|xf` | 0.897 | 0.887 | 0.890 | 1.000 | 0.956 | 0.986 |
| round 4's PPI++ form, rule (c) | `CR1_t\|fpc` | 0.897 | 0.908 | 0.887 | 1.177 | 1.112 | 1.258 |
| Kluger et al.'s cluster bootstrap | percentile | 0.715 | 0.874 | 0.954 | 0.576 | 0.965 | 1.626 |

Against the control, same-sample tuning covers 0.057 less at 4 clusters and 0.025 less at 8. Rule (c) at $n_L = 4$ sets the coefficient to 0 in every draw (`report_tables/r07d_limits_lambda_by_n.csv`, `median_frac_lam0` 1), so it equals the control there. Kluger's bootstrap moves from under-coverage at few clusters to over-coverage at many, with width to match. On the four tasks for $\theta_3$ at $n_L = 8$, `a_b1` covers 0.826 (CCRCC), 0.872, 0.856 and 0.874 against `fix1`'s 0.897, 0.897, 0.887 and 0.899 (`report_tables/r07c_limits_four_tasks_theta3.csv`). Round 4's PPI++ form forms no interval, and Kluger's bootstrap mostly falls below 0.6, in the 54 cells with one unlabelled cluster (section 7, item 3).

### 6.5 Regime B (brief F2 item 4)

Over the 736 cells of each form (the four HEST variants on $\log(1 + y)$ for $\theta_3$ and $\theta_2$, ACS by state for $\mu$ and $\theta_3$, and the six corpus tasks on both scales for $\theta_3$ and $\theta_2$, $m$ from 3 to 30), the median over genes of $E(\hat V)/\text{Var}$ has median 0.998 for every form, and its cell range is 0.942 to 1.057 for `C_fix1`, 0.940 to 1.058 for `C_ppi` and 0.927 to 1.040 for `C_classical`. Median coverage lies between 0.8795 and 0.9130 in every cell, and the median share of draws without an interval is 0 in every cell (`report_tables/r08_regimeB_ranges.csv`). By task and estimand the median ratio lies between 0.976 (breast Xenium, $\theta_3$, `C_classical`) and 1.006 (`report_tables/r08b_regimeB_ev_by_task.csv`). **The under-estimate of round 5's $\theta_3$ regime B variance that F1's toy enumeration found, 0.76 to 0.80 of the true variance, does not appear on the real tasks**, where $\theta_3$'s median ratio is 0.992 to 1.000 on the HEST variants over the three forms. The files hold no quantity that explains the toy result, so this report gives none (section 7, item 9). FR7's preview is in section 5.

### 6.6 The shortfall and its explanation (brief F2 item 5)

At $n_L = 8$ under `uni_v2` on the primary scale (`report_tables/r09_shortfall_uni_v2_primary_n8.csv`). $\kappa(e)$ is the largest cluster's share of $\sum_g (e_g - \bar e)^2$ with $e_g = z_g - f_g$, `kappa_sup` is round 9's corrected frontier for the fixed coefficient at that $(G, n_L)$, and $G^\ast = 1/\sum_g s_g^2$.

| task | estimand | median $\kappa(e)$ | `kappa_sup` | share of genes beyond | median $G^\ast$ | median skewness of $e$ | `fix1` coverage | coverage, genes within / beyond |
|---|---|---|---|---|---|---|---|---|
| CCRCC | $\mu$ | 0.525 | 0.158 | 1.00 | 3.3 | 1.97 | 0.858 | none within / 0.858 |
| CCRCC | $\theta_3$ | 0.282 | 0.158 | 0.98 | 6.3 | 0.55 | 0.897 | 0.901 / 0.896 |
| INDIANA_KIDNEY | $\mu$ | 0.336 | 0.160 | 0.98 | 5.5 | 1.35 | 0.870 | 0.906 / 0.868 |
| INDIANA_KIDNEY | $\theta_3$ | 0.253 | 0.160 | 0.94 | 7.4 | 0.20 | 0.897 | 0.902 / 0.897 |
| LUNG_XENIUM | $\mu$ | 0.329 | 0.433 | 0.25 | 5.2 | -0.24 | 0.898 | 0.901 / 0.871 |
| LUNG_XENIUM | $\theta_3$ | 0.410 | 0.433 | 0.44 | 4.1 | 0.71 | 0.887 | 0.899 / 0.843 |
| ACS_STATES | $\theta_3$ | 0.109 | 0.071 | 1 | 20.5 | -0.02 | 0.899 | none within / 0.899 |
| kidney Visium | $\theta_3$ | 0.157 | 0.071 | 1.00 | 11.6 | 0.48 | 0.895 | none within / 0.895 |
| bowel Visium | $\theta_3$ | 0.333 | 0.278 | 0.70 | 4.8 | 0.51 | 0.888 | 0.896 / 0.879 |
| brain Visium | $\theta_3$ | 0.357 | 0.278 | 0.80 | 4.8 | 0.64 | 0.885 | 0.901 / 0.878 |
| lung Xenium | $\theta_3$ | 0.418 | 0.275 | 0.88 | 4.0 | 0.78 | 0.890 | 0.903 / 0.885 |

The rows for CCRCC_merged, breast ST and breast Xenium and for $\mu$ on the corpus are in the same file. Across every cell of the grid (`report_tables/r09b_shortfall_correlations.csv`), the Spearman correlation over genes of `fix1`'s coverage with $\kappa(e)$ has median -0.556 over 810 HEST and ACS cells (negative in 0.81 of them) and -0.403 over 900 corpus cells (0.75). With $G^\ast$ it has median 0.627 and 0.454, and with the skewness of $e$ -0.257 and -0.159. In the cells that have genes on both sides of the frontier, the genes beyond it have the lower median coverage in 0.97 (HEST and ACS, 420 cells) and 0.93 (corpus, 451 cells) of cells, by a median of 0.015 and 0.009. So the shortfall follows the concentration of the residual in a few donors, measured by $\kappa(e)$ or $G^\ast$, more closely than it follows skewness. Crossing the frontier is not by itself a large loss: on kidney Visium every gene is beyond `kappa_sup` at $n_L = 8$ and coverage is 0.895. The mechanism this reading rests on is that a donor carrying most of the residual sum of squares makes the labelled sample's variance estimate depend on whether that donor was drawn. It would be contradicted by cells where coverage rises with $\kappa(e)$. The cells without a negative correlation are 0.19 and 0.25 of the two groups, counting cells where it is undefined, and they are not examined one by one here.

### 6.7 What predictions buy (brief F2 item 6)

At $n_L = 8$ under `uni_v2` (`report_tables/r10_buy_uni_v2_primary_n8.csv`), the median width ratio of `fix1` to `classical` for $\theta_3$ is 0.554 on ACS, 0.585 on LUNG_XENIUM, 0.664 to 0.948 on the corpus tasks and 0.878 to 0.957 on the other HEST tasks. `xf2`'s ratio is above `fix1`'s in every row, by 0.016 to 0.112. Within a task, the Spearman correlation over genes between `fix1`'s width ratio and the cluster-level $R^2_c$ (the squared correlation of donor values with donor predictions, round 9's `R2c_mean`) is between -0.63 and -0.99 in every row with more than one gene, while with the spot-level Pearson it is weaker and is positive on kidney Visium for $\theta_3$ (0.036). So the gain per gene follows how well the predictions track the donor-level values, not the spot-level accuracy of F1's tables.

**D9, the donor-clustered against the i.i.d. standard error of the spot mean** (`report_tables/r10b_d9_by_task.csv`, `uni_v2`, median over genes with 10% to 90%). On the corpus tasks on $\log(1 + y)$ it is 41.0 (32.8 to 49.1) on kidney Visium, 24.6 (20.7 to 30.6) on breast ST, 58.2 (46.8 to 67.2) on bowel Visium, 59.0 (51.4 to 70.5) on brain Visium, 51.8 (37.3 to 83.6) on breast Xenium and 18.6 (14.1 to 23.7) on lung Xenium. On the HEST tasks it is 32.6 (CCRCC), 16.4 (INDIANA_KIDNEY) and 14.8 (LUNG_XENIUM). So an interval that treated spots as independent would be narrower than the donor-clustered one by a factor whose median over genes is 14.8 to 59.0 on $\log(1 + y)$ under `uni_v2`.

### 6.8 The scale difference and the superpopulation interval (brief F2 items 7 and 8)

**Scale (D5)** (`report_tables/r11_scale_diff_uni_v2_n8.csv`, `fix1`, `uni_v2`, $n_L = 8$). For $\theta_3$ the normalised scale changes `fix1`'s median coverage by -0.0045 to 0.0053 on every task with its own head, and by -0.0014 to 0.0063 in round 9's pairing. For $\mu$ it raises coverage by 0.027 on CCRCC, 0.044 on CCRCC_merged, 0.013 on INDIANA_KIDNEY and 0.030 on bowel Visium, and changes it by less than 0.006 elsewhere. The shared factor's share (`pc1_share`, round 9's first principal component of the standardised donor by gene matrix) falls on the normalised scale on every task under `uni_v2`, from 0.650 to 0.338 on CCRCC, from 0.782 to 0.339 on bowel Visium and from 0.314 to 0.243 on INDIANA_KIDNEY (`report_tables/r11c_pc1_share.csv`). The three largest gains for $\mu$ are on the three tasks with the largest share on $\log(1 + y)$ above 0.64, but kidney Visium (0.564) and brain Visium (0.542) gain nothing, so the share alone does not order the tasks. Over the whole grid the median change in `fix1`'s coverage is near zero on every pairing (`report_tables/r11b_scale_diff_ranges.csv`, -0.00004 on the corpus, 0.0013 with the refitted head), with cell ranges of -0.032 to 0.059, and the normalised interval is narrower, median ratio 0.866 and 0.872.

**The refit itself.** The refitted heads' median spot-level Pearson on the normalised scale is 0.200 on CCRCC, 0.178 on INDIANA_KIDNEY and 0.497 on LUNG_XENIUM under `uni_v2` (`refit_norm/refit_compare.csv`).

**Superpopulation interval (S6-6)** (`report_tables/r12_superpop_four_tasks.csv`). `fix1_nofpc` drops the finite-population factor, so its width is $1/\sqrt{1 - n_L/G}$ times `fix1`'s, 1.225 on CCRCC at $n_L = 8$. Against the design target it over-covers, at $n_L = 8$ for $\theta_3$ 0.944 on CCRCC, 0.945 on INDIANA_KIDNEY, 0.969 on LUNG_XENIUM and 0.922 on ACS, and at $n_L = 12$ 0.971, 0.968, 0.996 and 0.938. Superpopulation coverage cannot be measured from one finite population. These design-target figures are the stated limit: the interval is conservative for the design target by an amount that grows with $n_L/G$.

### 6.9 Option (c), the search for a corpus covariate

The search of plan section 5c logged 107 queries and opened 93 sources, with 32 not retrieved (`option_c_search/optc_queries.csv`, `optc_evidence.csv`, `optc_not_retrieved.csv`, the sub-agents' summaries and declared deviations in `optc_summaries.md`). Most sources were read at abstract or excerpt level, and none end to end.

My reading of it is this. On the first question, the sub-agent found the label-free H&E transforms (colour deconvolution and stain separation, giving a haematoxylin amount per pixel) but no study that measures their agreement with deep nuclear segmentation per patch or per spot, and the evidence it did find points to site-dependent bias in intensity-based counts, which would matter on the center axis. On the second, both literatures define the estimand from fixed unit values, and a covariate that also feeds the predictor leaves the difference estimator design-unbiased provided the predictions are fixed or cross-fitted. A domain contrast needs the rectification done per domain. On the third, a covariate computed without labels for every unit defines a different but exactly specified finite-population parameter, so the inference is unchanged and only the reading changes, while recovering the parameter of a "true" covariate needs a validation subsample measured by the reference method. No source treats a generated covariate with few clusters. Since option (b) delivered CellViT's covariates on all six corpus tasks, nothing was built from option (c), and the search stands as evidence that no validated label-free substitute for CellViT's nuclear area was found.

## 7. Discrepancies, open questions and escalations

1. **FR6's frontier clause** is marked "not yet run" in `aggregate/f2_scores.csv`, because scores v3 ran before diagnostics v2. It is scored here from `diagnostics/f2_fr6.csv`, on $\kappa$ of the fixed-coefficient residual against `kappa_sup` as plan section 6 (note of 10 November on F2.5 to F2.8) named before the score. Under `kappa_star_v1` the clause holds. The coverage clause fails under every reading, so FR6 is refuted either way.
2. **The two readings of the fixed coefficient's cost do not agree.** Plan section 5.3 said that the share of genes where `fix1`'s median width exceeds `classical`'s equals the share where its mean width does, and that the aggregation would check this. The median and the mean of $s_{z - f}$ over draws are different functionals, so they need not agree, and they differ by more than 0.05 in 326 of 1,722 cells, by up to 0.36 (CCRCC_merged, $\mu$, $n_L = 12$) (`aggregate/f2_fix1_cost.csv`, log of `report_tables/`). The brief asks for the share of genes where "the fixed-coefficient interval is wider", which the plan reads by the median width, so FR4 is scored on it. Under the mean width CCRCC's $\theta_3$ share is 0.20 and FR4 would fail there.
3. **One unlabelled cluster.** In all 54 limits cells with $G - n_L = 1$ (breast Xenium and lung Xenium at $n_L = 16$, lung Xenium $\theta_2$ at 10, LUNG_XENIUM $\theta_2$ at 8), round 4's PPI++ form forms no interval under rules (a), (b) and (c) in any draw, and Kluger's bootstrap covers below 0.6 in 48 of them, lowest 0.227. Every such cell has no PPI++ interval and no other cell lacks one, and no other cell has Kluger coverage below 0.6. These cells enter the grid medians of section 6.4 as coverage 0. They are an edge of the grid, not a property of the estimators at ordinary $n_L$.
4. **Rule (a) is rule (b) on the donor target.** Round 4's `a_b1` codes the same donor-pairs formula as `b_cluster`, so the two arms agree draw for draw (largest difference 0). The brief's "rule (a)" as a spot-level tuning rule applies only to the spot-weighted population, which F2 does not run.
5. **Kluger et al.'s bootstrap was run under simple random sampling** of clusters with $\pi = n_L/G$, regime A's design, not under the Bernoulli designs round 7 used.
6. **F2.8's model term.** `round5_ppi_e5_superpop.py` computes no model term. The record's superpopulation interval on real tasks is round 7's `round5_superpop` row, which is `fix1_nofpc` here, so F2.8 is reported from those rows (plan section 6).
7. **`factor_rows`' input `frac_nonzero_y`** is not carried by the cluster values and was passed as missing. It changes no `pc1_share` value and leaves one column of round 9's table empty.
8. **The switch rule's Monte Carlo error** is the approximation $\text{ratio}\sqrt{2/(R - 1)}$, since the cell tables keep no per-draw values, in place of the bootstrap over draws that plan section 5.3 named. With the smallest median at 0.9937 against a threshold of 0.95, the verdict does not depend on it.
9. **Regime B's toy shortfall** (F1, plan section 4) is absent on the real tasks (section 6.5) and is not explained here. A comparison of the toy populations' within-cluster sizes and heterogeneity with the real tasks' would be needed, and it was not run.
10. **The harness and `sacct` states of some completed jobs read failed.** The first 21 regime A units (the job template's copy loop under `bash -e`) and the refit units of CCRCC `uni_v2` (Slurm `8823488`) and LUNG_XENIUM `uni_v2` (`8823487`), both submitted before the template's `tail` line was fixed. The plan's note named only the second. In every case `PROVENANCE.txt` reads `COMPLETED` and the outputs are complete.
11. **$R^2_c$ in F2.6** is the squared correlation of donor values with donor predictions, as round 9's `R2c_mean` defines it and as the diagnostics anchor reproduces. Plan section 5.6 named D12's leave-one-donor-out $R^2$ from F1, which is a different quantity. The report uses $R^2_c$ throughout F2.6.
12. **Queue waits over four hours** (`report_tables/f2_ledger_new_rows.csv`). The 15 `norm_refit` regime A units waited 4.0 to 6.0 hours, cluster values v3 4.3 hours, the limits and regime B aggregation 4.5 hours and aggregation v3 with diagnostics v2 6.4 hours, all on `spill` on the night of 10 November. The record of the fourth session does not show the four-hour notice of rules section 4. All finished before this session began, so the notice is recorded here as an escalation.
13. **The provenance index now covers F2.** `round10_final_runs_provenance_index.py` walked only `F1/`. It gained an optional stage argument, whose default keeps the F1 index as it was, and the F2 index is written to `results/round10/final_runs/F2/provenance_index.csv`. It found no mismatch (section 3).
14. **Bookkeeping left by the fourth session.** The plan's F2 checkboxes were not ticked, and regime A v3, aggregation v3 and diagnostics v2 had no dated note. Both are fixed in this commit.
15. **The option (c) sub-agent `Pathology`** ran 27 read-only web searches before its frame-id message arrived, against its brief. No job, git or data was touched (plan section 6).
16. **The F1 report's sentence that the corpus tasks carry $\theta_1$ without a covariate was wrong**, since $\theta_1$ needs nuclear area. Nicolas decided that the corpus tasks carry $\mu$, with $\theta_1$ to $\theta_3$ where option (b) delivers, and it delivered on all six (plan sections 5.0 and 5b).

## 8. What was not checked

- The bootstrap arms under `hoptimus0` and `resnet50`, which the plan left out for cost.
- The limits arms on `norm_refit`, which they were not run on, so they cover 1,452 of regime A's 1,722 cells (`aggregate_limits/f2_limits_checks.json`, `report_tables/r04_controls_and_anchor.json`).
- Regime B on the normalised scale of the HEST tasks, and $\theta_1$ in regime B, which its form does not cover.
- The LUNG_XENIUM comparison on round 9's 42-gene subset, which is flagged in the cluster values but not tabulated here.
- The cells of section 6.6 where coverage rises with $\kappa(e)$, one by one.
- The 18 matched cells of round 7 for P10.1 part 2, which F3 runs.
- Option (c)'s sources beyond the abstract or excerpt level at which the sub-agents read them, and the hosts and books they could not open.

## 9. Proposed next step

After Nicolas has reviewed the scores and the points of section 7, chiefly the reading of FR4 (item 2), the cells with one unlabelled cluster (item 3) and the unexplained toy shortfall of regime B (item 9), his reply goes into `docs/round10/i04/final-runs/` as the next interval's decision file. A new session then writes F3's methods into the plan (prediction sets, the institution axis, the designs, E8 with its literature search first, and the evidence for question V), on the decided estimator with $\hat V_w$ as the cross-fitted form's variance, and runs F3.
