# Round 7, the inference track, the final report (S4b and S5)

Written on 15 October 2026 by the execution session (frame `89b5f4ed-6180-409e-831d-0fecc6ce5f4e`) under `docs/round07/i03/ppi/round07_ppi_S4_decisions.md` and `docs/EXECUTION_RULES.md` (revision of 14 October). Paths are relative to the repository root unless they start with `/work`. On Longleaf every result directory named here sits under `/work/users/w/e/weiyang/hest_replication/` at the same relative path.

## 1. Stage and status

S4b and S5 of interval i03 are complete, and with them the track. This report is committed on branch `round7-ppi` and tagged `round7-ppi-final`, and the branch and tag are pushed together once, with one pull request into `main`. The pull request is opened after the commit that holds this report, so its number is not written here. It is given in the chat handover and is the open pull request from `round7-ppi`, confirmed on GitHub.

The S4 memo was committed unchanged as `4d99b33d` and transcribed into section 11 of the plan as `f128e416`, before any i03 run. S4b's three predictions are scored in section 5. The S5 numbers job built every table the memo's section 5 asks for from the merged tables of S1 to S4b, with no new draws. The theory note on $\rho_{\mathrm{BH}}$ is in section 2.1 of `docs/round07/tracks/ppi/round07_ppi_theory.md`. The closing page is section 10.

## 2. What was run

### 2.1 Jobs, partitions, wall times and memory

Every job ran under account `rc_htzhu_pi`, was submitted to `general` and ran on `spill`, and is a row of `results/round7/ppi/r7ppi_slurm_jobs.csv` (630 rows, 125 of them for i03, all `COMPLETED`). Sub-agents ran from the read-only snapshot of `44032ae0` through `round7_ppi_run.py`, with the frame ids in `results/round7/ppi/S4b_cube_constant/s4b_assigned_frame_ids.csv`, each sent as a second message seconds after the brief, which forbade any job before it. The briefs are those of S3 with the stage, script, snapshot, outputs and resources changed.

| unit | runner | jobs | wall time per job | peak memory (GB) | sub-agent wall time |
|---|---|---|---|---|---|
| S4b test and pilots | lead | 4 (4950711, 4951133, 4951135, 4951136) | 00:15:06 to 04:12:20 | at most 1.73 | |
| S4b `CCRCC` | `fa6a8465-5404-4fda-bbcd-d46f62e1cf1b` | 20 | 00:09:30 to 00:19:55 | at most 0.93 | 2495 s |
| S4b `CCRCC_merged` | `1ed59637-4762-4bbf-bf2d-fef2af877953` | 20 | 00:09:11 to 00:20:19 | at most 1.04 | 2441 s |
| S4b `INDIANA_KIDNEY` | `a3a770ed-5647-4779-918c-95f86171fb58` | 20 | 00:08:01 to 00:18:24 | at most 0.80 | 2381 s |
| S4b `LUNG_XENIUM` | `c2c93fd8-7b79-42f5-bf3a-27183bd1c6c4` | 20 | 00:18:34 to 00:59:56 | at most 1.96 | 6156 s |
| S4b `ACS_STATES` | `95aa8242-c701-4faf-aa46-6e4abe841758` | 10 | 00:00:44 to 00:01:21 | at most 1.58 | 248 s |
| S4b `ACS_CA_PUMA` | `953d1dc0-1608-4061-9681-8fb004ecc9f3` | 10 | 00:03:11 to 00:44:56 | at most 0.85 | 2847 s |
| S4b simulation | `3066688c-fa60-4986-9d3c-6ce728d82ea3` | 14 | 00:22:32 to 04:29:45 | at most 0.81 | 17198 s |
| S4b merge, S5 dry run and S5 numbers | lead | 3 (4968431, 4951950, 4968458) | 00:00:17 to 00:00:46 | at most 0.58 | |
| pack for copy back | lead | 1 (4968468) | 00:00:02 | 0.03 | |
| code deliveries 17 to 19 | lead | 3 (4950694, 4951848, 4951929) | 00:00:12 to 00:00:20 | at most 0.19 | |

The pack jobs of the sub-agents are not in the ledger, as in i01 and i02.

### 2.2 Code and deliveries

New in i03, with md5 at the last delivered commit `61a60229f96ef8c54ec5d255da85dddac6b5be94` (from `results/round7/ppi/deliveries/delivery_19_job4951929.log`).

| script | md5 | what it does |
|---|---|---|
| `code/scripts/round7_ppi_s4b_cube3.py` | `67a99d8b7a48cb33d903d22681db0491` | the cube design for any number of balance variables, with $\pi_g$, $1$ and $\bar f_g$ for S4b; test, masking and simulation modes |
| `code/scripts/round7_ppi_s3s4_numbers.py` | `542139182263542c8ab57d2e671592bf` | `--stage S4b` added, the merge with the stamp check and S4b.1 to S4b.3 |
| `code/scripts/round7_ppi_s5_numbers.py` | `0af7cd4c926e4a522185fa13b22adc92` | the S5 tables, from the per-gene tables of S1 to S4b of the unit directories each stage's merge accepted |

`round7_ppi_s3_cube.py` is unchanged (`bdad8f019054140a1ce1a13e73b9bfde`), and S4b imports its target probabilities, step sizes and summaries. Theory section 3.9 was committed with the S4b code at `44032ae0`, before any S4b run, and section 3.10 on the S4b test after it. Deliveries 17 to 19 are in `results/round7/ppi/code_deliveries.csv`, with logs in `results/round7/ppi/deliveries/`. Delivery 17 carried the S4 gate commit `96b8ee28`, the memo and the plan with the S4b code. The commit that holds this report is not delivered, since nothing runs from it.

### 2.3 Provenance index

`results/round7/ppi/provenance_index.csv`, rebuilt from the repository root before the final commit, has 8731 rows from 605 records and 605 job ids. Both checks pass on every row.

## 3. Acceptance checks

### 3.1 The S4b sampler test

Slurm 4950711, `results/round7/ppi/S4b_cube_constant/tests/run1/s4b_tests.csv`, theory section 3.10. The sampler passes. No $\hat\pi_g$ of the 180 clusters is more than 3 Monte Carlo standard errors from its target (largest 2.82), $\hat\theta_{\mathrm{HT}}$ with the target probabilities has standardised biases from $-1.08$ to $1.93$, no pair has $\hat\pi_{gh} = 0$, and the balance variables have rank 3 in every cell. The primary variance, now the Sen-Yates-Grundy form, has its mean within 0.10 of the empirical variance of the Hájek mean in all six cells (0.977 to 1.003). The residual form misses at $G = 24$ (0.829). $\hat N = G$ never holds exactly (escalation 1).

### 3.2 Grids, stamps and merges

The S4b merge (4968431) found 114 unit directories, all with the assigned frame id and `status: COMPLETED`, and merged all of them, 180 masking cells and 2240 simulation rows (`results/round7/ppi/S4b_cube_constant/_merged/s4b_stamp_check.csv`, `s4b_report_numbers.csv`). Not run, from `.../_merged/s4b_skipped.csv`: the ACS mean on the constant arm, as in round 5, and `LUNG_XENIUM` $\theta_2$ at $n_L$ of 8 and 12, which exceed the 9 valid clusters less 2. The S5 numbers job read only the directories each stage's merge accepted.

**An anchor for the S5 tables.** The dry run of the S5 script before the S4b outputs existed (4951950, `results/round7/ppi/S5_numbers/_pilot/dryrun_without_S4b/s5_matched.csv`) reproduces the memo's section 2 table cell for cell, on 18 tissue cells and 4 census cells at $n_L = 8$ and $p_a = 0.01$. D0 classical covers 0.875 and 0.886, `rej_t` 0.861 and 0.889 at width 0.888 and 0.456, the cube design 0.885 and 0.899 at 0.891 and 0.912, and the mixture 0.886 and 0.912 at 1.004 and 0.834. The final run gives the same rows.

## 4. What differs between the arms of each comparison

1. **The S4b cube design against S3's (S4b.2).** One balance variable, the constant, and the reference distribution. S4b's primary interval uses $t_{n_L - 3}$ on informative arms and S3's used $t_{n_L - 2}$, so S4b also reports its intervals with $t_{n_L - 2}$, and section 6.1 gives both. The target probabilities, score, estimator and variance are the same. The draws are independent.
2. **Each design against D0 classical and D2 `rej_t` (S5).** Design and estimator. The cells are matched exactly (task, arm, estimand, $n_L$) across the nine designs of each table, kept only where D2 with own balance has support of at least 1,000 at the table's $p_a$, so degenerate cells drop out. Every design's coverage counts a draw without an interval as a miss.
3. **Broska and Howes's interval and the tuned interval (S5).** The estimator and interval, under D0 on the same draws. For the design target the tuned interval is `textbook_t|fpc|lin|xf` and for the superpopulation target it is round 5's tuned superpopulation interval, in S2's two sets (`A_fixed`, the fixed task, and `B_world`, its bootstrap worlds).
4. **Control arms.** The predictor only (the constant and the permuted predictor against the informative ones), and for `perm_cluster` the balance variable only.

## 5. Predictions against outcomes

| prediction | as stated | measured | outcome |
|---|---|---|---|
| S4b.1 | on census at $n_L = 8$, the Hájek width under the new design is at most 0.70 of D0 classical (median over informative cells) | 0.568 over 4 cells ($t_{n_L-3}$), 0.548 with $t_{n_L-2}$, against 0.912 for S3's cube design | held |
| S4b.2 | on the matched supported tissue cells at $n_L = 8$, its width is within 0.03 of S3's cube design's and its coverage within 0.03 of D0 classical | 18 cells. Width 0.883 of D0 classical against S3's 0.891; coverage 0.885 against 0.875 (both $t_{n_L-3}$, medians over cells) | held |
| S4b.3 | its Horvitz-Thompson width on census at $n_L = 8$ is below 1 | 3.484 of D0 classical, against 3.477 under S3's design | refuted |

All from `results/round7/ppi/S4b_cube_constant/_merged/s4b_report_numbers.csv`, rows `S4b.1_*`, `S4b.2_*` and `S4b.3_*`. S4b.2 holds on the medians, which is how it is stated. Per cell, the width is within 0.03 of S3's in 0.889 of the 18 cells and the coverage within 0.03 of D0 classical in 0.778 (rows `S4b.2_*_share_cells_*`).

## 6. Results

### 6.1 S4b, the constant balanced

**Census.** Balancing on the constant halves the Hájek interval's width on census, from 0.912 of D0 classical to 0.568 at $n_L = 8$, at coverage 0.885 counting misses (`s4b_report_numbers.csv`, rows `S4b.1_*`). At $n_L = 12$ it is 0.532, at coverage 0.879. The memo's reading of S3's loss on census is borne out for the Hájek mean.

**The Horvitz-Thompson mean does not improve,** contrary to S4b.3 and to theory 3.9's second expectation. The landing never leaves $\hat N = G$ exactly. Its median relative deviation is 0.036 over the census cells (`s4b_report_numbers.csv`, row `S4b_diag_median|census|resid_N_median`), and $\hat\theta_{\mathrm{HT}}$, which divides by $G$, carries the level of $\bar z_g$ times that deviation, which for income is large against its spread. The Hájek mean divides by $\hat N$ and so carries no level whatever $\hat N$ is. This reading fits the numbers and is not checked further (escalation 2).

**Tissue.** The new design is no wider than S3's. With its own reference $t_{n_L - 3}$ the Hájek width at $n_L = 8$ is 0.883 of D0 classical, and with S3's $t_{n_L - 2}$ it is 0.851, so on the same quantile it is about 4% narrower than S3's design (0.891), where theory 3.9 expected no change (rows `S4b.2_*|res` and `S4b.2_*|n2`).

**At $n_L = 4$** the primary reference has one degree of freedom on informative arms, so no interval is formed under the floor of theory 1.6, and S4b's coverage over all draws is 0 there. With $t_{n_L - 2}$ the Hájek interval on census has width 0.724 of D0 classical (`results/round7/ppi/S5_numbers/run1/s5_cube_widths.csv`).

**Simulation** (the 70 cells of each law with $n_L \ge 8$, rows `S4b_sim_*`). The Hájek interval with the Sen-Yates-Grundy form has median coverage 0.884 under the normal law (0.826 to 0.915) and 0.820 under the skewed law (0.775 to 0.874), with median estimated over empirical variance 0.993 and 0.992. It covers within 0.03 of nominal in 0.786 of normal-law cells and 0.043 of skewed-law cells. The residual form has median coverage 0.854 and 0.775. Under the skewed law the shortfall is not the variance's, which is accurate, but the normal reference's at these sample sizes.

**Design diagnostics** (rows `S4b_diag_*`). The smallest $\hat\pi_g$ is at least 0.482 of $n_L/G$ on census and 0.486 on tissue. The share of pairs with $\hat\pi_{gh} = 0$ is at most 0.0005 on census and 0.0048 on tissue. No cell has a draw with $\hat N = G$ exactly.

### 6.2 The designs on matched informative cells

From `results/round7/ppi/S5_numbers/run1/s5_matched.csv`. Coverage over all draws, a draw without an interval counted as a miss, and width as the per-gene ratio to D0 classical, both medians over cells of the median over genes. `bh` and `bh_t` are under D0. The cube designs and the mixture use the Hájek mean with the Sen-Yates-Grundy form, and the cube designs their primary reference.

**Tissue, $p_a = 0.01$** (18 cells at each $n_L$; no tissue cell reaches the support at $n_L = 4$).

| design | coverage, $n_L$ 6 | 8 | 12 | width, $n_L$ 6 | 8 | 12 |
|---|---|---|---|---|---|---|
| D0 classical | 0.878 | 0.875 | 0.878 | 1 | 1 | 1 |
| D0 tuned | 0.874 | 0.871 | 0.869 | 0.974 | 0.975 | 0.973 |
| D2 `rej_t` | 0.852 | 0.861 | 0.866 | 0.876 | 0.888 | 0.921 |
| D2 Hájek, `sim` | 0.839 | 0.860 | 0.871 | 0.958 | 0.963 | 0.953 |
| cube, S3 | 0.897 | 0.885 | 0.876 | 0.931 | 0.891 | 0.820 |
| cube, S4b | 0.894 | 0.885 | 0.873 | 0.983 | 0.883 | 0.801 |
| mixture | 0.878 | 0.886 | 0.881 | 1.029 | 1.004 | 0.982 |
| `bh` | 0.798 | 0.853 | 0.919 | 0.730 | 0.885 | 1.156 |
| `bh_t` | 0.892 | 0.912 | 0.948 | 0.997 | 1.102 | 1.330 |

**Census, $p_a = 0.01$** (4 cells at each $n_L$).

| design | coverage, $n_L$ 4 | 6 | 8 | 12 | 16 | width, $n_L$ 4 | 6 | 8 | 12 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|
| D0 classical | 0.905 | 0.894 | 0.886 | 0.887 | 0.900 | 1 | 1 | 1 | 1 | 1 |
| D0 tuned | 0.905 | 0.896 | 0.894 | 0.902 | 0.908 | 1.000 | 0.551 | 0.531 | 0.506 | 0.492 |
| D2 `rej_t` | 0.902 | 0.888 | 0.888 | 0.895 | 0.897 | 0.535 | 0.467 | 0.456 | 0.451 | 0.449 |
| D2 Hájek, `sim` | 0.747 | 0.846 | 0.828 | 0.794 | 0.790 | 0.649 | 0.620 | 0.579 | 0.526 | 0.502 |
| cube, S3 | 0.889 | 0.904 | 0.898 | 0.898 | 0.907 | 1.132 | 0.957 | 0.912 | 0.887 | 0.858 |
| cube, S4b | 0 | 0.886 | 0.885 | 0.879 | 0.878 | none | 0.637 | 0.568 | 0.532 | 0.524 |
| mixture | 0.935 | 0.921 | 0.912 | 0.908 | 0.907 | 0.988 | 0.863 | 0.834 | 0.814 | 0.800 |
| `bh` | 0.717 | 0.819 | 0.870 | 0.923 | 0.962 | 0.278 | 0.370 | 0.436 | 0.521 | 0.588 |
| `bh_t` | 0.882 | 0.912 | 0.924 | 0.948 | 0.972 | 0.444 | 0.486 | 0.528 | 0.587 | 0.641 |

At $p_a = 0.1$ the rows are close to these, and the file has them. The one difference worth stating is tissue at $n_L = 4$, where 12 cells reach the support. There `rej_t` covers 0.798 counting misses, D0 classical 0.874, the S3 cube design 0.919 at width 1.104 and the mixture 0.834 (escalation 3 on the memo's figure for D0 here). Widths against `rej_t` are in the column `wr_rej` of the same file. On census at $n_L = 8$ the S4b cube design is 1.259 times as wide as `rej_t` and the tuned interval 1.195 times.

**$\theta_2$ and the share formed.** Every row above counts draws without an interval as misses. The smallest share formed in a matched cell is 0.903 for `rej_t` and D2's Hájek interval and 0.908 for the mixture, on tissue at $n_L = 6$ and $p_a = 0.01$, and 0.354 and 0.386 on tissue at $n_L = 4$ and $p_a = 0.1$, all in $\theta_2$ cells with few valid clusters. D0 classical forms its $\theta_2$ interval in at least 0.857 of draws there, and the cube designs, which draw over the valid clusters, in every draw except S4b at $n_L = 4$ (column `share_formed_min`).

### 6.3 Broska and Howes's interval against the tuned interval, under D0

From `results/round7/ppi/S5_numbers/run1/s5_bh_vs_tuned.csv`, informative arms, cells matched across the designs (tissue 24, 24, 21 and 21 cells at $n_L$ of 4, 6, 8 and 12, census 4 at each $n_L$). Widths are against D0 classical in the same set.

| target, domain | interval | coverage, $n_L$ 4 | 6 | 8 | 12 | width, $n_L$ 4 | 6 | 8 | 12 |
|---|---|---|---|---|---|---|---|---|---|
| design, tissue | tuned, `textbook_t\|fpc\|lin\|xf` | 0.900 | 0.885 | 0.874 | 0.876 | 1.000 | 0.981 | 0.977 | 0.989 |
| design, tissue | `bh` | 0.704 | 0.801 | 0.859 | 0.929 | 0.497 | 0.714 | 0.889 | 1.167 |
| design, tissue | `bh_t` | 0.884 | 0.904 | 0.922 | 0.958 | 0.867 | 0.997 | 1.108 | 1.336 |
| design, tissue | `bh_t_n2` | 0.922 | 0.913 | 0.928 | 0.960 | 1.168 | 1.066 | 1.136 | 1.354 |
| design, census | tuned, `xf` | 0.905 | 0.896 | 0.894 | 0.902 | 1.000 | 0.552 | 0.532 | 0.507 |
| design, census | `bh_t` | 0.882 | 0.912 | 0.924 | 0.948 | 0.444 | 0.486 | 0.528 | 0.587 |
| super, tissue | tuned, round 5 | 0.877 | 0.850 | 0.854 | 0.852 | 1.103 | 1.108 | 1.163 | 1.350 |
| super, tissue | `bh_t` | 0.840 | 0.848 | 0.858 | 0.860 | 0.873 | 0.994 | 1.099 | 1.350 |
| super, census | tuned, round 5 | 0.891 | 0.873 | 0.868 | 0.858 | 1.025 | 0.578 | 0.562 | 0.553 |
| super, census | `bh_t` | 0.856 | 0.876 | 0.888 | 0.894 | 0.446 | 0.487 | 0.524 | 0.584 |

Under the design target (`results/round7/ppi/S5_numbers/run1/s5_bh_vs_tuned.csv`, and `results/round7/ppi/S5_numbers/run1/s5_matched.csv` for `rej_t`) `bh_t` beats the tuned interval at $n_L = 4$, where the tuned rule sets its coefficient to zero, on both domains. On census it is as narrow as `rej_t` there (0.444 against 0.535). From $n_L = 8$ on tissue it is wider than the tuned interval and over-covers, because it has no finite-population factor. Under the superpopulation target `bh_t` covers less than the tuned interval on tissue at $n_L = 4$ (0.840 against 0.877) and about the same from $n_L = 6$, and on census it is narrower up to $n_L = 8$ and slightly wider at 12 (0.584 against 0.553). Kluger et al.'s cluster bootstrap under Bernoulli designs covers 0.618 to 0.927 for the design target on tissue (uniform, $n_L$ 4 to 12) and 0.565 to 0.808 for the superpopulation target, in the same file.

### 6.4 Controls and the cube designs' widths

**Control arms** (`results/round7/ppi/S5_numbers/run1/s5_controls.csv`). With the constant or the permuted predictor no design gains width. At $n_L = 8$ and $p_a = 0.01$ on tissue, the constant arm's widths against D0 classical are 0.971 for `rej_t`, 1.007 for the S3 cube design, 1.011 for S4b's and 1.023 for the mixture, and the permuted arm's 0.973, 0.979, 0.992 and 1.024. D2 with `perm_cluster` balance on the informative arms has width 1.030 on tissue and 1.038 on census. So almost all of the gains in sections 6.2 and 6.3 come from the predictor's information.

**Horvitz-Thompson and Hájek widths** (`results/round7/ppi/S5_numbers/run1/s5_cube_widths.csv`, informative cells, no support restriction). On tissue the two means have close widths under both cube designs (at $n_L = 8$, 0.870 and 0.844 under S3's, 0.868 and 0.867 under S4b's). On census the Horvitz-Thompson mean is 3.477 times as wide as D0 classical under S3's design and 3.484 under S4b's at $n_L = 8$, against 0.912 and 0.568 for the Hájek mean. The balance residual on $\bar f_g$ has median 0.059 to 0.061 on tissue and 0.034 on census at $n_L = 8$ under both designs, and $\lvert\hat N/G - 1\rvert$ under S4b has median 0.031 and 0.035.

## 7. Discrepancies, open questions and escalations

1. **$\hat N = G$ never holds exactly under S4b.** Theory 3.9 expected it to hold in most draws. With $n_L$ of 4 to 16 the landing always ends on the size equation alone with two units left, so the constant is always dropped, and $\lvert\hat N/G - 1\rvert$ has a median of 0.031 on tissue and 0.035 on census at $n_L = 8$ (`results/round7/ppi/S5_numbers/run1/s5_cube_widths.csv`).
2. **S4b.3 is refuted, and the reason given here is a reading.** The Horvitz-Thompson mean carries the level of $\bar z_g$ through $\hat N/G - 1$, which the landing leaves at a few percent, while the Hájek mean carries none. A landing that keeps the constant to the end, dropping the size equation in its place, would be the direct test. It was not run.
3. **The memo's D0 classical figure at $n_L = 4$.** The memo gives D0 classical a coverage of 0.903 on the 12 supported tissue cells at $p_a = 0.1$, against 0.797 for `rej_t`. On the same 12 cells, with draws without an interval counted as misses for both, S5 gives 0.874 for D0 classical and 0.798 for `rej_t` (`s5_matched.csv`). The difference is the Indiana $\theta_2$ cells, where D0 forms its interval in 0.857 of draws under S1's rule of at least 2 degrees of freedom (`s5_matched_cells.csv`), so 0.903 is close to D0's coverage over formed draws. The contrast with `rej_t` stands, smaller.
4. **The reference distribution of the cube designs at $n_L = 4$.** With three balance variables the primary reference $t_{n_L - 3}$ leaves one degree of freedom at $n_L = 4$, and no interval is formed. S4b's coverage over all draws is therefore 0 at $n_L = 4$, which says nothing about the design. With $t_{n_L - 2}$ an interval exists, and its width is reported.
5. **Theory 3.9's tissue expectation.** It expected no change on tissue, and the new design is about 4% narrower on the same quantile. Why the constant helps on tissue too is not examined.
6. **The skewed simulation law.** Every design-based interval of S3 and S4b under-covers there, to a median of 0.820 for the Hájek interval with its accurate variance, so the shortfall is the normal approximation at these sample sizes. Only one skewed law was run.

## 8. What was not checked

1. A landing that keeps the constant to the end (item 2 of section 7).
2. The superpopulation target for the S3 and S4b designs and the mixture. S5 compares them on the design target only.
3. Every S3 and S4b result rests on one score for the probabilities (the first, except S3's second-score rows), one value of $\tau$, one value of $\epsilon$ for the mixture, and one skewed simulation law.
4. The Monte Carlo error of the simulated $\hat\pi_{gh}$ is not propagated into the Sen-Yates-Grundy intervals.
5. The S4 report's section 8 items, and escalations 3 (lung $\theta_2$ against round 5) and 5 ($\rho_{\mathrm{BH}}$) of the S4 memo, which theory 2.1 now notes as an explanation not derived or checked.

## 9. Proposed next step

None for the session. The track ends at this gate. Section 10 states what the evidence supports, and whether the paper recommends a design is Nicolas's decision.

## 10. What the inference track established in round 7

Throughout, coverage counts a draw without an interval as a miss, nominal is 0.90, widths are against D0 classical's `textbook_t|fpc|lin` on the same cells, and the figures are those of sections 6.2 to 6.4 unless another file is named. "Supported" means D2 with own balance has support of at least 1,000. $\theta_2$ coverages carry their share formed as section 6.2 states.

**D0, simple random selection with the classical interval.** The evidence supports it as the reference design. It covers 0.874 to 0.905 on the matched cells of both domains at every $n_L$, forms its interval in every $\theta_3$ draw and in at least 0.857 of $\theta_2$ draws, and every design below is measured against it. Its weakness is width, which the tuned interval addresses on census from $n_L = 6$ (width about half) and barely on tissue (0.97). Source (`results/round7/ppi/S5_numbers/run1/s5_matched.csv`).

**D2, rejective selection with `rej_t`.** Supported on census, where it gives the narrowest valid interval in the track at $n_L \ge 6$ (width 0.449 to 0.467, coverage 0.888 to 0.897), with the tuned interval 1.15 to 1.21 times as wide and the S4b cube design 1.18 to 1.39 times. On tissue its width is 0.876 to 0.921 at $n_L \ge 6$ but it covers 0.852 to 0.866, below D0's, and at $n_L = 4$ it falls to 0.798. It needs a support of at least 1,000, which no tissue cell reaches at $n_L = 4$ and $p_a = 0.01$. Its $\theta_2$ share formed drops below one where the valid clusters are few. Source (`results/round7/ppi/S5_numbers/run1/s5_matched.csv`).

**D2 with weighting (Horvitz-Thompson or Hájek with simulated probabilities).** Not supported. It is wider than `rej_t` on every matched row and covers less except on tissue at $n_L = 12$ (on census at $n_L = 8$, 0.828 at width 0.579), because D2 almost never labels some clusters, and its $\hat\theta_{\mathrm{HT}}$ is biased where $\hat\pi_g$ is near zero (S2b item 2, S4 report section 6.1). Source (`results/round7/ppi/S5_numbers/run1/s5_matched.csv`).

**The cube design with $\pi_g$ and $\bar f_g$ balanced (S3).** Supported on tissue as an alternative to `rej_t` with a design-based interval, with the Sen-Yates-Grundy form. At $n_L = 8$ it covers 0.885 at width 0.891, against 0.861 at 0.888 for `rej_t`, and at $n_L = 12$ it is narrower (0.820 against 0.921). Its inclusion probabilities are bounded below by half of $n_L/G$ and almost no pair is never sampled together. Not supported on census, where its width is 0.912. Its residual-form variance is too small and should not be used. Source (`results/round7/ppi/S5_numbers/run1/s5_matched.csv`).

**The cube design with $\pi_g$, $1$ and $\bar f_g$ balanced (S4b).** Supported on both domains at $n_L \ge 6$ with the Hájek mean and the Sen-Yates-Grundy form, within the limits below. On tissue it matches the S3 design (0.885 at 0.883 for $n_L = 8$). On census it halves S3's width (0.568 at coverage 0.885), and is then 1.26 times as wide as `rej_t` and close to the tuned interval (0.531). Its Horvitz-Thompson mean is not usable on census. At $n_L = 4$ its primary interval is not formed. It rests on one score, one $\tau$ and the design target only. Source (`results/round7/ppi/S5_numbers/run1/s5_matched.csv`).

**The mixture of D2 and D0 with $\epsilon = 0.5$.** Supported as a control, as the S4 memo put it. It gives the most reliable design-based coverage of any design (0.878 to 0.886 on tissue, 0.907 to 0.935 on census) at a width near D0's on tissue (0.98 to 1.03) and 0.80 to 0.99 on census. It shows that bounding every inclusion probability below makes a design-based interval valid after balance, and that the price is most of balance's gain in width. Only $\epsilon = 0.5$ was run. Source (`results/round7/ppi/S5_numbers/run1/s5_matched.csv`).

**Greedy k-center.** Not supported. Exact enumeration over the starts shows the classical interval applied as if simple random covering 0.326 to 0.458 on the two kidney cancer tasks with the foundation-model encoders, many pairs never sampled together, so no design-based variance exists, and an unbiased $\hat\theta_{\mathrm{HT}}$ 1.38 to 3.33 times as variable as D0's classical mean (`results/round7/ppi/S4_kcenter/_merged_r2/s4_report_numbers.csv`).

**Broska and Howes's interval, as published.** Not supported at small $n_L$ for either target. It covers 0.704 on tissue and 0.717 on census at $n_L = 4$ for the design target, and 0.659 and 0.669 for the superpopulation target, rising to nominal only by $n_L = 12$ on the design target. Source (`results/round7/ppi/S5_numbers/run1/s5_bh_vs_tuned.csv`).

**Broska and Howes's interval with the project's correction (`bh_t`).** Supported at small $n_L$. With the divisor $n_L - 1$ on the labelled term and $t_{n_L - 1}$, it covers 0.884 on tissue and 0.882 on census at $n_L = 4$ for the design target, narrower than the tuned interval there (0.867 and 0.444 against 1.000), and 0.840 and 0.856 for the superpopulation target. From $n_L = 8$ it over-covers the design target and is wider than the tuned interval on tissue (1.108 against 0.977), so its use is at small $n_L$. The correction is this project's, not its authors', and `bh_t_fpc`, its finite-population version, under-covers and is not supported (S4 report, section 6.1). Source (`results/round7/ppi/S5_numbers/run1/s5_bh_vs_tuned.csv`).

**Kluger et al.'s cluster bootstrap under Bernoulli designs.** Not supported at the cluster counts of these tasks. It covers 0.618 at $n_L = 4$ and 0.848 at $n_L = 8$ on tissue for the design target under the uniform design, and 0.565 to 0.808 for the superpopulation target. Source (`results/round7/ppi/S5_numbers/run1/s5_bh_vs_tuned.csv`).

**What is not established.**
1. The superpopulation target for the cube designs and the mixture.
2. Any result that depends on the probability score, on $\tau$, on $\epsilon$, or on the skewed simulation law, each of which took one value.
3. Why $\hat N$ deviates from $G$ under S4b and whether a different landing removes it (section 7, items 1 and 2), and why the constant helps on tissue.
4. The lung $\theta_2$ differences from round 5, read as ties at a float32 threshold and not checked.
5. The explanation of $\rho_{\mathrm{BH}}$'s overstatement by the noise of $\hat\lambda$, noted in theory 2.1 and not derived.
6. The S4 report's section 8 items, among them the cube designs' second-order probabilities, which are simulated and not derived.
7. Whether the paper's tuned estimator should change below $n_L = 6$, and the paper's positioning against Broska and Howes, which the S4 memo leaves to Nicolas.
