# Round 7, the inference track, the S4 report (S2b, S3 and S4)

Written on 14 October 2026 by the execution session (frame `89b5f4ed-6180-409e-831d-0fecc6ce5f4e`) under `docs/round07/i02/ppi/round07_ppi_S2_decisions.md` and `docs/EXECUTION_RULES.md` (revision of 14 October). Paths are relative to the repository root unless they start with `/work`. On Longleaf every result directory named here sits under `/work/users/w/e/weiyang/hest_replication/` at the same relative path.

## 1. Stage and status

S2b, S3 and S4 of interval i02 are complete, and the track stops here until the oversight chat's S4 decision memo. Nothing of S5 has been set up, staged or piloted. This report is committed on branch `round7-ppi` and tagged `round7-ppi-S4`, and the branch and tag are pushed together once, with one pull request into `main`. The pull request is opened after the commit that holds this report, so its number is not written here. It is given in the chat handover and is the open pull request from `round7-ppi`, confirmed on GitHub.

Every exit item of the memo's section 5 is met, with two qualifications given in section 3. S2b item 1 confirms the memo's section 3 outside `LUNG_XENIUM` and gives a partial explanation inside it. The cube method passes its sampling test and its fallback was not needed, but the primary variance fails the test's 0.10 band at $G = 24$ and $G = 15$. Every cell ran or is listed. The predictions are scored in section 5. The provenance index passes both checks.

## 2. What was run

### 2.1 Jobs, partitions, wall times and memory

Every job ran under account `rc_htzhu_pi`, was submitted to `general` and ran on `spill`, and is a row of `results/round7/ppi/r7ppi_slurm_jobs.csv` (505 rows, 185 of them for i02, all `COMPLETED` but one). Wall times and peak memory below are the `sacct` values in that ledger. Sub-agents ran from read-only snapshots through `round7_ppi_run.py`, with the frame ids the lead assigned in `results/round7/ppi/S3_adaptive/s3_assigned_frame_ids.csv` and `results/round7/ppi/S4_kcenter/s4_assigned_frame_ids.csv`, each sent as a second message seconds after its brief. The briefs follow section 6 of the rules and are those of i01 with the stage, script, snapshot, outputs and resources changed.

| unit | runner | jobs | snapshot | wall time per job | peak memory (GB) | sub-agent wall time |
|---|---|---|---|---|---|---|
| S2b diagnostics | lead | 21 | `4644d70b`, `02217ca4`, `3258eb1f` | 00:00:05 to 00:07:02 | at most 1.83 | |
| S3 test and pilots | lead | 4 (4900059, 4900555, 4900557, 4900558) | `df344a76` | 00:05:29 to 00:37:42 | at most 1.81 | |
| S3 `CCRCC` | `df384ce0-59e2-4e4a-b958-7c74eb908718` | 20 | `df344a76` | 00:02:47 to 00:17:12 | at most 1.55 | 1311 s |
| S3 `CCRCC_merged` | `cd433da7-306d-4c40-ac36-fb367b34119e` | 20 | `df344a76` | 00:03:46 to 00:09:21 | at most 1.50 | 1236 s |
| S3 `INDIANA_KIDNEY` | `98571a34-f292-42b6-b065-4625ef0c26a0` | 20 | `df344a76` | 00:02:08 to 00:09:31 | at most 1.56 | 1270 s |
| S3 `LUNG_XENIUM` | `11e6fd80-e2ac-4635-aa4b-7b9f103651b1` | 20 | `df344a76` | 00:09:19 to 01:58:49 | at most 1.89 | 19104 s |
| S3 `ACS_STATES` | `1b3d0083-6297-4e21-bbb8-b0f295aa5ad0` | 10 | `df344a76` | 00:00:33 to 00:01:56 | at most 1.74 | 366 s |
| S3 `ACS_CA_PUMA` | `9aa7829b-3c22-4019-ba26-252ea86da7ba` | 10 | `df344a76` | 00:02:09 to 00:09:10 | at most 1.41 | 719 s |
| S3 simulation | `3896f774-c0e2-412f-9281-c4bd322e5b63` | 26 | `df344a76` | 00:11:13 to 00:57:32 | at most 2.12 | 22507 s |
| S4 pilot | lead | 1 (4902613) | `4102a38c` | 00:00:25 | 1.02 | |
| S4 `CCRCC` | `a919b947-c876-4b68-909a-dbfbc84cf9df` | 5 | `4102a38c` | 00:00:12 to 00:00:16 | at most 0.75 | 281 s |
| S4 `CCRCC_merged` | `c9583ca5-4d29-49fd-ae5b-e79aadee3f20` | 5 | `4102a38c` | 00:00:12 to 00:00:16 | at most 0.73 | 289 s |
| S4 `INDIANA_KIDNEY` | `88faf860-7db6-4882-bc61-31444bcbac3b` | 5 | `4102a38c` | 00:00:10 to 00:00:18 | at most 0.48 | 288 s |
| S4 `LUNG_XENIUM` | `1301bb5d-9fd0-4aef-a6fd-7b4dfb461c5f` | 5 | `4102a38c` | 00:00:15 to 00:00:18 | at most 1.06 | 289 s |
| merges and numbers | lead | 4 (4903160, 4929664, 4930089, 4930091) | `d2b64931`, `fa8892c1` | 00:00:13 to 00:00:16 | at most 0.73 | |
| packs for copy back | lead | 2 (4929706, 4930175) | none | 00:00:01 | 0.01 | |
| code deliveries 13 to 16 | lead | 4 (4899823, 4902482, 4903007, 4930044) | none | 00:00:09 to 00:00:14 | at most 0.10 | |

The S2b jobs are listed in section 10 of the plan and in the ledger. One failed, the recount 4892100, on a `KeyError` in the merge of its own tables, and was rerun as 4892562 after the fix (escalation 1). The first numbers job for S2b items 2 and 3 (4892252) wrote a duplicate row type and was superseded by 4892563. The pack jobs of the sub-agents are not in the ledger, as in i01.

### 2.2 Code and deliveries

New in i02, with md5 at the last delivered commit `fa8892c1b46b54c26f7813e98bfdcbf8b810cd41` (from `results/round7/ppi/deliveries/delivery_16_job4930044.log`).

| script | md5 | what it does |
|---|---|---|
| `code/scripts/round7_ppi_s2b_theta2.py` | `6ebcf580572646124b52d6661de0cf43` | S2b item 1, the D0 reruns and the $\theta_2$ recount |
| `code/scripts/round7_ppi_s2b_numbers.py` | `678f92e364c1594e242a8f8ba8f22543` | S2b items 2 and 3, the numbers |
| `code/scripts/round7_ppi_s3_cube.py` | `bdad8f019054140a1ce1a13e73b9bfde` | the cube design, the mixture, the residual-form variance, test, masking and simulation modes |
| `code/scripts/round7_ppi_s4_kcenter.py` | `9e3a1ebca498e9fc2212a277ead14151` | greedy k-center, exact over the $G$ starts |
| `code/scripts/round7_ppi_s3s4_numbers.py` | `14250ac6609a6d1975d75ab35ff85351` | S3 and S4 merges with the stamp check, and the report numbers |
| `code/scripts/round7_ppi_s2_comparators.py` | `a30b7507a4c1e2d4a0efdc76a5032871` | `bh3_parts`, `rho_bh` and `bh_variants` added for S2b item 3 |
| `code/scripts/round7_ppi_s1_sim.py` | `b434987d5bc590945ec3486530bc9681` | `--by-population` added for S2b item 2 |

`round7_ppi_weighting.py` (`19137aac514748f8aa6b054157067e29`), `round7_ppi_d2.py` (`31d5b0e396d85d3c49709f216d89d4af`), `round7_ppi_s1_masking.py` (`9e945ff59c4363a5121e16335e2d6dcb`), `round7_ppi_merge.py` (`c8ad6fd5f63296a85c7f664d871631bb`) and `round7_ppi_run.py` (`3f37e77c2abe22afa6eca8772282f4f0`) are unchanged since i01. Theory sections 2.1 (the two Broska and Howes variants), 3 and 4 were committed before any run that uses them, at `4644d70b`, `df344a76` and `4102a38c`. Section 3.8, on the S3 test, was added after the test.

Seven deliveries carried the commits to the Longleaf clone, each a fast-forward from a bundle, each with a read-only snapshot. They are deliveries 10 to 16 in `results/round7/ppi/code_deliveries.csv`, with logs in `results/round7/ppi/deliveries/`. Delivery 13 (4899823) carried the S2b results commit `a0bad7f4` with the S3 code, as delivery 10 carried the S2 gate's results (escalation 2). The commit that holds this report and the copied-back S3 and S4 results is not delivered, since nothing runs from it.

### 2.3 Provenance index

`results/round7/ppi/provenance_index.csv`, rebuilt from the repository root with `round7_ppi_provenance_index.py` before the final commit, has 6893 rows from 484 `PROVENANCE.txt` records and 484 job ids. Check 1 (the recorded snapshot commit is an ancestor of `HEAD`) and check 2 (the recorded md5 equals the script's md5 at that commit) pass on every row.

## 3. Acceptance checks

### 3.1 S2b anchors

Each S2b rerun reproduces the S1 or S2 rows it repeats exactly. The D0 $\theta_2$ reruns match 9860 gene rows with differences of 0 in coverage, relative width and share formed (`results/round7/ppi/S2b_diagnostics/theta2_recount/recount_r2/s2b1_numbers.csv`). The by-population rerun matches all 220 of S1's rows with difference 0 (`results/round7/ppi/S2b_diagnostics/numbers_items_2_3_r2/s2b2_numbers.csv`). The published Broska and Howes interval in the S2b runs matches all 360 masking rows and 260 simulation rows of S2 with difference 0 (`.../numbers_items_2_3_r2/s2b3_numbers.csv`).

### 3.2 The S3 test

Slurm 4900059, `results/round7/ppi/S3_adaptive/tests/run1/s3_tests.csv`, theory section 3.8. The sampler passes. Over the 180 clusters of the six cells, one $\hat\pi_g$ is more than 3 Monte Carlo standard errors from its target (3.64, $G = 15$, normal), and $\hat\theta_{\mathrm{HT}}$ with the target probabilities has standardised biases from $-1.11$ to $1.19$. The primary variance does not pass. Its mean over the empirical variance in the normal-law cells is 0.979 at $G = 51$, 0.894 at $G = 24$ and 0.811 at $G = 15$, against the band of 0.10. The landing phase leaves the balance on $\bar f_g$ inexact in every draw, so the count of inexact draws the memo asked for is the whole sample. The median relative residual is reported in its place, 0.071 to 0.094 in the test cells. The fallback to conditional Poisson sampling was not used, because the sampler itself met its test within the cap. The residual form stays primary as written before the test (escalation 6).

### 3.3 Grids, stamps and merges

The S3 merge (4929664, rerun as 4930089 with the aggregates this report quotes) found 126 unit directories, all with the assigned frame id and `status: COMPLETED`, and merged all of them, 680 masking cells and 7800 simulation rows (`results/round7/ppi/S3_adaptive/_merged_r2/s3_stamp_check.csv` and `s3_report_numbers.csv`). The S4 merge (4903160, rerun as 4930091) found and merged 20 of 20, 150 cells (`results/round7/ppi/S4_kcenter/_merged_r2/`). The memo accepted keeping merged outputs in the merge jobs' directories with no copies, so `s3_masking_grid.csv`, `s3_sim.csv`, `s3_report_numbers.csv`, `s4_grid.csv` and `s4_report_numbers.csv` are in those `_merged_r2/` directories. The `_merged/` directories hold the first merge, whose rows the rerun repeats and extends.

Cells not run, from `.../S3_adaptive/_merged_r2/s3_skipped.csv` and `.../S4_kcenter/_merged_r2/s4_skipped.csv`. The second S3 score needs an embedding, so it is not run on census or on the constant arm (62 rows). The ACS mean is not run for the constant arm, as in round 5 (10). The cube design on `LUNG_XENIUM` $\theta_2$ is not run at $n_L$ of 8 and 12, which exceed the 9 valid clusters less 2 (10), and S4 skips the same lung $\theta_2$ cells (10).

**Degenerate cells.** As the memo asks, the 19 S1 cells of `LUNG_XENIUM` $\theta_2$ at $n_L = 12$ and $p_a = 0.01$ are degenerate. There $n_L$ exceeds the 9 valid clusters, every draw labels every valid cluster, and the estimate equals $\theta$. They are the arms `constant` (balances `own`, `pcF2`, `perm_cluster`) and `hoptimus0`, `permuted`, `resnet50` and `uni_v2` (each with `own`, `pcF2`, `pcE2`, `perm_cluster`), with support 4.55 in `results/round7/ppi/S1_weighting/_merged/s1_masking_diag.csv`. The 19 cells at $p_a = 0.1$ (support 45.5) are degenerate in the same way. The S3 mixture cells of `LUNG_XENIUM` $\theta_2$ at $n_L = 12$ (5 arms at each $p_a$) inherit the same degeneracy in their D2 half and are degenerate too.

## 4. What differs between the arms of each comparison

1. **Cube design against D2 with `rej_t` (S3.1).** The design (the cube method with probabilities from the first score, against rejective selection with fixed thresholds), the estimator (the Hájek mean against the classical mean), and the variance (the residual form of theory 3.4 against `rej_t`). Same task, arm, estimand, $n_L$ and genes. The D2 widths are S1's, from `s1m_genes`, on S1's draws.
2. **Cube design against D0 classical (S3.4).** Design, estimator and variance as above, against simple random selection with `textbook_t|fpc|lin`. The draws are independent. D0 coverage is S1's, conditional on an interval being formed, with S1's rule of dropping $\theta_2$ draws with fewer than two valid clusters.
3. **Cube design against the mixture (S3.5).** The design only, for the Hájek mean. The primary variance differs too (the residual form under the cube design, the Sen-Yates-Grundy form with simulated probabilities under the mixture), and section 6.2 gives the same comparison with the same variance on both sides.
4. **The two S3 scores.** The target probabilities only. The balance variables, the estimator and the intervals are the same.
5. **k-center against D0 and D2 (S4).** The design, and for S4.2 also the estimator ($\hat\theta_{\mathrm{HT}}$ under k-center against the classical mean under D0). The k-center quantities are exact over the $G$ starts, and the D0 and D2 quantities are S1's over 2,000 draws.
6. **Arms under k-center.** The selection depends on the encoder only, `resnet50` for the `resnet50`, `permuted` and `constant` arms, and the classical mean and $\hat\theta_{\mathrm{HT}}$ do not use the predictions. So those three arms give identical rows for these two estimators, and three encoders, not five arms, are distinct.

## 5. Predictions against outcomes

| prediction | as stated | measured | outcome |
|---|---|---|---|
| S2b.1 | outside `LUNG_XENIUM`, round 5's $\theta_2$ coverage equals round 7's conditional coverage times share formed within 0.03 | 368 cells. Per gene, largest difference 0.00775 and no cell outside Monte Carlo error. With the cell medians multiplied, largest difference 0.0272, none above 0.03 | held |
| S2b.2 | in the skewed simulation cell, at least 90% of populations with HT standardised bias above 3 have smallest $\hat\pi_g$ below $0.01\,n_L/G$ | 128 of 134 (0.955); 95 of the 134 have $\hat\pi_g = 0$ for some cluster, and all 134 biases are negative | held |
| S2b.3 | under D0 for the design target, `bh_t` covers at 0.85 or above at every $n_L$ on every tissue task | 16 of 16 task and $n_L$ medians at 0.85 or above, 0.872875 to 0.9975 | held |
| S2b.4 | superpopulation target, set `B_world`, `bh_t` covers at 0.80 or above at $n_L = 4$ on every task | 0.83375 (`CCRCC`) to 0.8875 (`ACS_STATES`) | held |
| S3.1 | at $n_L = 8$, own balance, first score, the Hájek width ratio to D2 `rej_t` is 0.95 to 1.15, $\theta_3$, `CCRCC`, `uni_v2` | 1.034 at $p_a = 0.1$, 1.040 at $p_a = 0.01$ (primary variance) | held |
| S3.2 | the Hájek interval covers within 0.03 of nominal in every simulation cell with $n_L \ge 8$ | 34 of 140 cells (0.243) with the primary variance, coverage 0.714 to 0.896; with the Sen-Yates-Grundy form 0.336 | refuted |
| S3.3 | in every S3 cell the smallest $\hat\pi_g$ is at least $0.45\,n_L/G$ | smallest over all cells 0.479 (cube design, simulation); real-task cube cells at least 0.489 | held |
| S3.4 | on the real tasks, S3's Hájek interval with its primary variance covers within 0.03 of D0 classical in at least 0.85 of cells (D2's Hájek with simulated pair probabilities did so in 0.71) | 0.694 of 180 cube cells with the first score (0.683 counting a missing interval as a miss) | refuted |
| S3.5 | at $n_L = 8$, own balance, the cube design's Hájek interval is narrower than the mixture's in at least three quarters of supported cells | 0.722 of 36 cells at both $p_a$ (primary variances) | refuted, narrowly |
| S4.1 | at $n_L = 8$ the classical interval as if simple random covers below 0.80 for $\theta_3$ on at least two tissue tasks | 1 of 4 tasks with the median over the five arms, 2 of 4 with the median over the three encoders | partly held |
| S4.2 | at $n_L = 8$ the exact sd of $\hat\theta_{\mathrm{HT}}$ under k-center is at least 1.5 times that of the classical mean under D0 on every tissue task | 4 of 4 tasks for $\theta_3$ (median ratio over arms 1.66 to 2.47); 11 of 12 task and encoder cells | held |

Sources. S2b.1 from `.../theta2_recount/recount_r2/s2b1_numbers.csv` (rows `r5_*|not_lung`). S2b.2 from `.../numbers_items_2_3_r2/s2b2_numbers.csv`. S2b.3 and S2b.4 from `.../numbers_items_2_3_r2/s2b3_numbers.csv`. S3 from `results/round7/ppi/S3_adaptive/_merged_r2/s3_report_numbers.csv`, S3.1 rows `S3.1_wr_D2rej|*|H_res`, S3.2 rows `S3.2_*`, S3.3 rows `S3.3_*`, S3.4 rows `S3.4_*|cube_u1|H_res|*`, S3.5 rows `S3.5_*|cube_H_res|mix_H_sim|*`. S4 from `results/round7/ppi/S4_kcenter/_merged_r2/s4_report_numbers.csv`, rows `S4.1_*` and `S4.2_*`. The baseline 0.71 of S3.4 is 0.7102 in `results/round7/ppi/_i01_numbers_r3/s1_report_numbers.csv`, over the 880 supported D2 cells. The cube design has no support constraint and no zero pair probabilities to speak of (section 6.2), so S3.4 counts every cube cell with the first score. S3.5 counts the cells whose D2 half has support of at least 1,000, as S1 did.

## 6. Results

### 6.1 S2b

**Item 1, the $\theta_2$ recount.** Outside `LUNG_XENIUM`, the difference between round 5 and round 7 in $\theta_2$ is the counting rule and nothing else, which the S2 memo inferred. Round 5 counted a draw with no interval as a miss. Round 7 reported coverage over the draws with an interval. Over the 420 D2 $\theta_2$ cells supported over all clusters (344 over the valid ones, and 38 degenerate cells where $n_L$ is at least the number of valid clusters), the section 6.1 table of the S2 report reads as follows over all draws, with the conditional value beside it (`.../recount_r2/s2b1_numbers.csv`, rows `t61_*|supported_all`).

| estimator, variance | coverage over all draws, median | minimum | conditional median | conditional minimum |
|---|---|---|---|---|
| classical, `textbook_t\|fpc\|lin` | 0.88825 | 0.755 | 0.8897 | 0.85025 |
| classical, `rej_t` | 0.87625 | 0.3165 | 0.8788 | 0.8039 |
| $\hat\theta_{\mathrm{HT}}$, `sim` | 0.87375 | 0.31275 | 0.87825 | 0.5225 |
| $\hat\theta_{\mathrm{H}}$, `sim` | 0.869375 | 0.30075 | 0.8724 | 0.6425 |

The minima over all draws are low because some cells form few intervals, with share formed down to 0 for `rej_t` and the weighted intervals. The D0 classical rule differs too. Round 7's S1 formed a $\theta_2$ interval with 2 or more degrees of freedom, while the estimator definition and round 5 use $t_{n_v - 1}$ with $n_v \ge 2$. Under the definition's rule, `wr_D0cl` for $\theta_2$ matches round 5 within 0.0092 outside lung and 0.0358 on lung, against 0.224 and 0.395 under S1's rule (rows `r5_max_abs_d_wr_*`). On `LUNG_XENIUM`, 8 of 112 cells differ by more than 0.03 per gene (30 with the cell medians multiplied). They are cells at $n_L$ of 6 and 8, where round 5 ran on snapshot `9185bc6` with float32 thresholds, while the cells at $n_L$ of 4 and 12 ran on `b410529` with float64 thresholds, as round 7 does, and match. Of the 128 lung $\theta_2$ cells, 2 have thresholds that differ from round 5's (`.../recount_r2/s2b1_thresholds.csv`), against 0 of 416 elsewhere. A threshold that falls on tied distances, which the valid-subset distance of $\theta_2$ makes common, would explain the rest, but this is not checked (escalation 3).

**Item 2, the simulation bias by population.** In the skewed cell at $G = 51$, $n_L = 8$, $k = 1$, 134 of 600 populations have a standardised HT bias above 3 in absolute value, every one negative, and 128 of them have a smallest $\hat\pi_g$ below $0.01\,n_L/G$ (`.../numbers_items_2_3_r2/s2b2_numbers.csv`). The bias comes from clusters that D2 almost never labels, as the S2 report suspected.

**Item 3, Broska and Howes with small-sample corrections.** Under D0 for the design target, the median over cells of the median coverage over genes is, at $n_L$ of 4, 6, 8, 12 and 16 (`.../numbers_items_2_3_r2/s2b3_numbers.csv`, rows `cov_median|A_fixed|*|design|nL*`), as follows.

| interval | 4 | 6 | 8 | 12 | 16 |
|---|---|---|---|---|---|
| `bh` | 0.707 | 0.80475 | 0.85775 | 0.92675 | 0.9405 |
| `bh_t` | 0.887875 | 0.906375 | 0.92175 | 0.956 | 0.957 |
| `bh_t_fpc` | 0.862375 | 0.858125 | 0.859 | 0.86175 | 0.93325 |
| `bh_t`, superpopulation target, `B_world` | 0.843625 | 0.854 | 0.8605 | 0.8695 | 0.89625 |

`bh_t` repairs the published interval's under-coverage at small $n_L$, and it over-covers the design target from $n_L = 12$, as the finite-population factor it lacks predicts. `bh_t_fpc` under-covers, with a median ratio of estimated to empirical variance of 0.842 against 1.246 for `bh_t` and 1.052 for `bh`, which contradicts theory 2.1's expectation that it stays conservative (escalation 4). The factor $\rho_{\mathrm{BH}}$ overstates the measured variance ratio, by a factor whose median over cells is 0.53, 0.63, 0.69, 0.73 and 0.89 at those $n_L$ (Spearman correlation 0.739 between measured ratio and $\rho_{\mathrm{BH}}$), and 0.42 to 0.81 in simulation (rows `rho|*`), most likely because $\hat\lambda$ is noisy and the labelled term is divided by $n_L$ (escalation 5).

### 6.2 S3, the cube design and the mixture

**Design diagnostics** (`.../S3_adaptive/_merged_r2/s3_masking_diag.csv` and `s3_report_numbers.csv`). Pairs with $\hat\pi_{gh} = 0$ are at most 0.0014 of a cell's pairs under the cube design with the first score, 0 with the second and 0 under the mixture, so the Sen-Yates-Grundy form is defined in every S3 cell. The largest standardised difference between $\hat\pi_g$ and its target in a cell has median 3.43 over cells and maximum 5.10, each cell comparing up to several thousand cluster and gene pairs. The landing leaves the balance on $\bar f_g$ inexact in every draw, with a median relative residual over cells of 0.077 (first score) and 0.121 (second score). Every $\theta_2$ interval under the cube design is formed in every draw (share formed 1, rows `S3m_share_formed_min`), since the design draws $n_L$ valid clusters. Under the mixture the $\theta_2$ share formed falls to 0.038 in the worst gene, in `LUNG_XENIUM` cells at $n_L = 4$, where most draws label fewer than 4 valid clusters.

**Real tasks.** Over cells, for the Hájek mean (rows `S3.4_*` and `S3m_est_over_emp_*`), with coverage the median over cells of the median over genes, the designs compare as follows.

| design | variance | cells | coverage | within 0.03 of D0 classical | below 0.80 | `wr_D0cl` | estimated over empirical variance |
|---|---|---|---|---|---|---|---|
| cube, first score | residual (primary) | 180 | 0.8756 | 0.694 | 0.039 | 0.944 | 0.966 |
| cube, first score | `sim` | 180 | 0.8849 | 0.767 | 0.017 | 0.953 | 0.977 |
| cube, first score | `apx_size` | 180 | 0.8928 | 0.594 | 0.022 | 0.951 | 0.938 |
| cube, second score | residual (primary) | 120 | 0.8451 | 0.283 | 0.208 | 0.878 | 0.816 |
| cube, second score | `sim` | 120 | 0.8766 | 0.892 | 0 | 0.980 | 0.983 |
| mixture | residual | 260 | 0.8502 | 0.496 | 0.119 | 0.952 | 0.809 |
| mixture | `sim` (primary) | 260 | 0.8893 | 0.912 | 0 | 1.008 | 0.976 |
| mixture | `apx_size` | 260 | 0.8970 | 0.719 | 0 | 1.030 | 0.987 |

The cube design with the first score gives intervals about 5% narrower than D0 classical and covers about as D2's weighted intervals did in S1. Its residual form is too small by a few percent on the real tasks and is too small by a fifth under the second score, whose probabilities do not follow $\bar f_g$, so that the imbalance left by the landing is larger. Under the mixture the Sen-Yates-Grundy form covers within 0.03 of D0 classical in 0.912 of cells, the best of any design-based interval in the track so far, at a median width equal to D0 classical's.

**S3.1 in detail** (`.../s3_masking_grid.csv`, `CCRCC`, `uni_v2`, $\theta_3$, $n_L = 8$, first score). The Hájek interval with the residual form covers 0.874, against 0.838 for D2 `rej_t` at $p_a = 0.1$ and 0.849 for D0 classical, at width ratio 1.034 to `rej_t` at $p_a = 0.1$ and 1.040 at $p_a = 0.01$.

**S3.5 in detail** (rows `S3.5_*`, 36 cells at $n_L = 8$). With each design's primary variance the cube design is narrower in 0.722 of cells at both $p_a$, with median width ratio 0.952 and 0.955. With `apx_size` on both sides it is narrower in 0.833 and 0.861. With the residual form on both sides, which is not derived for the mixture, it is narrower in only 0.306 and 0.278, because the residual form is too small under the mixture.

**Simulation** (rows `S3s_*` and `S3.2_*`, the 140 cells with $n_L \ge 8$). For the cube design with the first score, the Hájek coverage with the residual form has median 0.868 under the normal law (0.719 to 0.896) and 0.796 under the skewed law (0.714 to 0.842), and the Sen-Yates-Grundy form has 0.878 and 0.816. The median estimated over empirical variance is 0.900 and 0.920 with the residual form, and 0.955 and 0.976 with the Sen-Yates-Grundy form. Under the mixture at $p_a = 0.1$ the Sen-Yates-Grundy form has median coverage 0.910 (normal, 0.898 to 0.930) and 0.844 (skewed, 0.794 to 0.915), with variance ratios 1.001 and 0.999. The cube design's shortfall in simulation is therefore the variance's, not the skewed law's alone.

### 6.3 S4, greedy k-center

**The design** (`results/round7/ppi/S4_kcenter/_merged_r2/s4_diag.csv`, `s4_report_numbers.csv`). Over the 150 cells, the median number of distinct samples among the $G$ starts is 18.5, 17.5, 16 and 13 at $n_L$ of 4, 6, 8 and 12. The share of pairs with $\pi_{gh} = 0$ has median 0.732, 0.557, 0.431 and 0.225 at those $n_L$ (ranges 0.389 to 0.760, 0.111 to 0.607, 0.248 to 0.487, 0.048 to 0.268). Theory 4.3 expected more than half at $n_L \le 8$, which holds at 4 and 6 and fails at 8. At $n_L = 8$ every task has a smallest $\pi_g$ of $1/G$, a ratio of 0.125 to $n_L/G$, and up to 4 clusters with $\pi_g = 1$.

**At $n_L = 8$ for $\theta_3$** (`.../s4_grid.csv` and rows `S4.1_*`, `S4.2_*`), per task and encoder, the exact coverage of the classical interval applied as if simple random, and the exact sd of $\hat\theta_{\mathrm{HT}}$ over the sd of the classical mean under D0, medians over genes, are these.

| task | encoder | classical coverage, k-center | D0 classical coverage | HT sd over D0 classical sd |
|---|---|---|---|---|
| `CCRCC` | `resnet50` | 0.8125 | 0.849 | 2.29 |
| `CCRCC` | `hoptimus0` | 0.4167 | 0.849 | 3.33 |
| `CCRCC` | `uni_v2` | 0.4583 | 0.849 | 3.27 |
| `CCRCC_merged` | `resnet50` | 0.7174 | 0.841 | 2.47 |
| `CCRCC_merged` | `hoptimus0` | 0.3261 | 0.841 | 3.32 |
| `CCRCC_merged` | `uni_v2` | 0.4130 | 0.841 | 3.28 |
| `INDIANA_KIDNEY` | `resnet50` | 0.92 | 0.898 | 2.34 |
| `INDIANA_KIDNEY` | `hoptimus0` | 0.96 | 0.898 | 2.47 |
| `INDIANA_KIDNEY` | `uni_v2` | 0.92 | 0.898 | 2.48 |
| `LUNG_XENIUM` | `resnet50` | 1.0 | 0.8725 | 1.66 |
| `LUNG_XENIUM` | `hoptimus0` | 1.0 | 0.8725 | 1.38 |
| `LUNG_XENIUM` | `uni_v2` | 0.6667 | 0.8725 | 2.02 |

The k-center rule hurts the classical interval badly on the two kidney cancer tasks with the two foundation-model encoders, where the farthest-point samples are not representative of expression, and not at all on Indiana, where the classical interval over-covers. On lung the coverage over 15 starts of a sample that is the same for most starts is close to 0 or 1 per gene. $\hat\theta_{\mathrm{HT}}$ is unbiased (its largest absolute bias over cells is $8.9 \times 10^{-16}$, column `ht_unbiased_check_max` of `s4_diag.csv`), and its exact sd is 1.38 to 3.33 times the D0 classical sd. Over cells at $n_L = 8$, the median exact coverage for $\theta_3$ is 0.8125 for the classical interval, 0.855 for `bh` and `bh_t_fpc`, 0.918 for `bh_t`, 0.580 for HT with `apx_size` and 0.592 for Hájek with `apx_size`. For $\theta_2$ these are 0.875, 0.85, 0.909, 0.696 and 0.717 (rows `S4_coverage_median_over_cells|*`). As theory 4.3 expected, `apx_size` has no basis under this design and its intervals do not cover.

## 7. Discrepancies, open questions and escalations

1. **The first recount job failed.** Slurm 4892100 stopped on a `KeyError` in the merge of the recount's own tables. The fix is commit `3258eb1f`, delivered as delivery 12, and the rerun is 4892562. No result of the failed job is used.
2. **Deliveries carried results.** Delivery 10 carried the S2 gate commit's results into the Longleaf clone, and delivery 13 carried the S2b results commit `a0bad7f4`. Snapshots copy only `code/`, so no job read those files.
3. **Lung $\theta_2$ against round 5.** The 8 lung cells that differ from round 5 by more than 0.03 are the cells round 5 ran on its float32-threshold snapshot. Ties at the threshold would explain why the precision matters there. This is supported by the snapshot pattern and by 2 differing thresholds of 128 (`results/round7/ppi/S2b_diagnostics/theta2_recount/recount_r2/s2b1_thresholds.csv`), and was not checked draw by draw.
4. **`bh_t_fpc` under-covers.** Theory 2.1 expected it to stay conservative by about $(1 - (1 - f)R^2)/(1 - R^2)$. Its measured variance ratio has median 0.842 under D0 (`results/round7/ppi/S2b_diagnostics/numbers_items_2_3_r2/s2b3_numbers.csv`), so that expectation is wrong, and the reason is item 5.
5. **$\rho_{\mathrm{BH}}$ overstates the measured ratio,** by a factor of about 0.5 to 0.9 that rises with $n_L$, which places Broska and Howes's variance estimate closer to the design variance than theory 2.1 says. The likely cause is the noise of $\hat\lambda$ with a handful of labelled clusters and the divisor $n_L$ of the labelled term. The theory has not been revised.
6. **The S3 primary variance.** The residual form was made primary before the test and stays so. It is a few percent too small on the real tasks with the first score, a fifth too small with the second, and fails the test at $G \le 24$, because the landing leaves an imbalance of the order of one cluster that the form ignores. The Sen-Yates-Grundy form with simulated $\hat\pi_{gh}$ is defined in every S3 cell and does better on every measure here. Whether to change the primary is the memo's decision.
7. **The inexact-draw count is uninformative.** The memo asked for the draws whose landing left the balance inexact to be reported separately. Every draw is inexact, so the median balance residual is reported instead.
8. **Two sub-agents stopped and were resumed.** The `LUNG_XENIUM` and simulation sub-agents stopped on a connection error to the model service after about three hours, with their submitted jobs still running. I resumed both with an instruction to check `sacct` and to submit only units never submitted. Neither resubmitted a job, and the last simulation unit (`G51_s_k1_nL16`, 4924122) was submitted after the resumption.
9. **The largest $\hat\pi_g$ differences.** The maximum over cells of the largest standardised difference between $\hat\pi_g$ and its target is 5.10 (`results/round7/ppi/S3_adaptive/_merged_r2/s3_masking_diag.csv`, column `pi_hat_vs_target_zmax`). Each cell has up to several thousand comparisons and there are 300 cube cells, so a maximum of about 5 is not out of line, but no formal multiplicity check was made.
10. **Theory 4.3's first expectation fails at $n_L = 8$,** where the share of zero $\pi_{gh}$ has median 0.431 (`results/round7/ppi/S4_kcenter/_merged_r2/s4_report_numbers.csv`), below the half I expected.
11. **S4.1 depends on how arms are pooled.** The numbers script, written before the S4 run, takes the median over the five arms, which counts the `resnet50` selection three times. Counted over encoders, the prediction holds. Both are given in section 5.

## 8. What was not checked

1. The cube design's second-order probabilities were simulated and not derived, and their Monte Carlo error was not propagated into the Sen-Yates-Grundy intervals.
2. The landing term of theory 3.4 was not added to the residual form, so whether it accounts for the whole shortfall is not known.
3. The lung tie explanation of item 3 above.
4. The S3 simulation used one score and $k = 1$ only, and no superpopulation target. S3 on the real tasks scored the design target only.
5. S4 was not run on census, as the instruction says, and the k-center rule was run with one tie-breaking rule only.
6. The sub-agents' pack jobs are not in the job ledger, as in i01.

## 9. Proposed next step

For the memo. On these results the mixture of D2 and D0 with $\epsilon = 0.5$ and the Sen-Yates-Grundy form with its exact mixture probabilities is the design-based interval that comes closest to D0 classical's coverage, in 0.912 of real-task cells, at D0's width (`results/round7/ppi/S3_adaptive/_merged_r2/s3_report_numbers.csv`). The cube design with the first score is about 5% narrower and covers less well, with either variance. I propose that S5 take the mixture as the paper's candidate for balanced selection with a valid interval, with D0 classical and D2 `rej_t` beside it, and that the cube design's variance be revisited only if the memo wants it as the primary design. S3 succeeded only in part, so the batch version after Kluger and Bates is not proposed. k-center is not a design the paper can recommend for the classical interval, since its exact coverage falls to 0.3261 to 0.4583 on the kidney cancer tasks with foundation-model encoders, and $\hat\theta_{\mathrm{HT}}$, though unbiased, is 1.38 to 3.33 times as variable as D0's classical mean (`results/round7/ppi/S4_kcenter/_merged_r2/s4_report_numbers.csv`).
