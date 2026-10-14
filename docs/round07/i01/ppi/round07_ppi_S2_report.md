# Round 7, the inference track, the S2 report (S0 to S2)

Written 14 October 2026 by the execution session at the gate of interval i01, in the format of section 9 of `docs/round07/i01/ppi/round07_ppi_track.md`. Every number below is read from the file named in its paragraph or table row. Numbers pooled over cells are rows of `results/round7/ppi/_i01_numbers_r3/s1_report_numbers.csv` or `results/round7/ppi/_i01_numbers_r3/s2_report_numbers.csv`, recomputed from the merged tables by `code/scripts/round7_ppi_i01_numbers.py` on Longleaf. Its operational definitions of predictions S1.1 to S2.4 are in that script's comments and are repeated in section 5.

## 1. Stage and status

S0, S1 and S2 are complete, and the track stops here until the oversight chat's S2 decision memo. Nothing of S3, S4 or S5 has been set up, staged or piloted. This report is committed on branch `round7-ppi` and tagged `round7-ppi-S2`, and the branch and tag are pushed once, with one pull request into `main`. The pull request is opened after the commit that holds this report, so its number is not written here. It is given in the chat handover and is the open pull request from `round7-ppi`, confirmed on GitHub.

The exit items of S2, each with its evidence, are these.

1. The anchors of S0 pass, in `results/round7/ppi/S0_anchors/s0_anchors.csv` (section 3.1).
2. The synthetic test of S1 does not pass in full. $\hat\theta_{\mathrm{HT}}$ is unbiased in every cell, and the Sen-Yates-Grundy variance fails in every skewed cell with support of at least 1,000, because of pairs with $\pi_{gh} = 0$ (section 3.2, `results/round7/ppi/S1_weighting/tests/run2/s1_tests.csv`).
3. Every cell of both grids has run under every design and estimator named, apart from the skips listed in section 3.4 (`results/round7/ppi/S1_weighting/_merged/s1_skipped.csv`).
4. Broska and Howes's interval passes both checks of section 2.3 of the track document (section 3.3, `results/round7/ppi/S2_comparators/tests/bh_tests.csv`).
5. The provenance index passes both checks over 308 records (section 2.3, `results/round7/ppi/provenance_index.csv`).

Four results stand out. Under D2 the weighted intervals do not repair the cells where `rej_t` failed, and on the real tasks they cover no better than `rej_t` (section 6.1). And D2 gives some clusters an inclusion probability of zero in 225 of its 1336 cells on the real tasks, so $\hat\theta_{\mathrm{HT}}$ is not design-unbiased there (section 7, escalation 3). In simulation the weighted estimators are biased in part of the skewed populations, and a rerun with five times the draws shows that this is not a finite-draw effect (section 6.2). And `rej_t` for $\theta_2$ at the smallest $n_L$ of each tissue task does not reproduce round 5's values, which makes the S1 results for those cells unconfirmed (section 6.5, escalation 12).

## 2. What was run

### 2.1 Jobs, partitions, wall times and memory

All 320 jobs of the interval ran on partition `spill` under account `rc_htzhu_pi`, with every job id, wall time and peak memory in `results/round7/ppi/r7ppi_slurm_jobs.csv` (from `sacct`). Of the 320, 10 failed, all of them `LUNG_XENIUM` S1 units on snapshot `ba3129e4` (section 7, escalation 6), and each was rerun once into a directory with suffix `_r2`.

| unit | frame id | jobs | snapshot | longest wall | peak memory (GB) |
|---|---|---|---|---|---|
| lead (S0) | `89b5f4ed-6180-409e-831d-0fecc6ce5f4e` | 9 | `c9570f7b`, `27037522` | 00:05:06 | 1.99 |
| S1 `CCRCC` | `d8ef1094-c17e-4919-8b0f-ee5f4cf4ba8a` | 20 | `ba3129e4` | 00:14:38 | 1.67 |
| S1 `CCRCC_merged` | `8dc076ae-e062-4abe-bbf5-02e428742e42` | 20 | `ba3129e4` | 00:13:45 | 1.74 |
| S1 `INDIANA_KIDNEY` | `d84f7666-c888-47e7-98c1-84dbf9e94f1e` | 20 | `ba3129e4` | 00:25:15 | 1.6 |
| S1 `LUNG_XENIUM` | `8315bff1-6d24-4553-9ea7-1ad958cd9523` | 30 | `ba3129e4`, `136ed26f` | 01:30:52 | 2.2 |
| S1 `ACS_STATES` | `ff3cdc81-7d4a-4d3c-83da-71602ccbbcbc` | 10 | `ba3129e4` | 00:05:41 | 1.77 |
| S1 `ACS_CA_PUMA` | `aff927e9-f507-44a1-8468-c911a2ed1806` | 10 | `ba3129e4` | 00:09:45 | 1.47 |
| S1 simulation | `38f638e9-8e8e-4aad-a4f0-c96d7384f6ae` | 52 | `ba3129e4` | 00:41:17 | 2.8 |
| S2 `CCRCC` | `25d95705-daea-40d4-9555-2aae3eeb1a53` | 20 | `d0462a70` | 00:06:58 | 0.86 |
| S2 `CCRCC_merged` | `3092c493-9be0-43fd-adb6-100c6ffc244d` | 20 | `d0462a70` | 00:07:23 | 1.04 |
| S2 `INDIANA_KIDNEY` | `fb7f28c6-c807-4e4a-ab72-d6e6447518a3` | 20 | `d0462a70` | 00:08:12 | 0.8 |
| S2 `LUNG_XENIUM` | `ebfe87d1-3899-4862-a114-ebc0341386a2` | 20 | `d0462a70` | 00:33:28 | 1.62 |
| S2 `ACS_STATES` | `35df0f02-52a0-41eb-94a4-571597d4b9d0` | 10 | `d0462a70` | 00:03:04 | 1.81 |
| S2 `ACS_CA_PUMA` | `ff331d11-67ef-4720-aec6-66fa647c4eef` | 10 | `d0462a70` | 00:16:15 | 0.71 |
| S2 simulation | `a475380c-f66c-4d8a-a5b0-effd5e46dbb4` | 26 | `d0462a70` | 00:13:49 | 0.35 |

The lead's own S1 and S2 jobs (tests, pilots, the two merges, the numbers job, code deliveries and copy-back packs) are the remaining rows of `results/round7/ppi/r7ppi_slurm_jobs.csv` with frame id `89b5f4ed-6180-409e-831d-0fecc6ce5f4e`. The merges are Slurm 4840163 (S1) and 4834044 (S2), on snapshot `136ed26f`. The numbers were computed three times. Slurm 4840279 on `136ed26f` wrote `results/round7/ppi/_i01_numbers/`. Slurm 4841335 on `e74913ec` wrote `results/round7/ppi/_i01_numbers_r2/`, adding the breakdown by zero $\hat\pi_g$ of section 5 and removing a duplicate row type. Slurm 4842169 on `83f9970b` wrote `results/round7/ppi/_i01_numbers_r3/`, adding the comparison of `rej_t` with round 5 of section 6.5. The three give the same prediction scores and cells, every row of an earlier run is in the later ones, and the report cites the third.

### 2.2 Code and deliveries

Nine deliveries reached the Longleaf clone as git bundles, each a row of `results/round7/ppi/code_deliveries.csv` with its log under `results/round7/ppi/deliveries/`. Delivery 7 (Slurm 4827320) carried `d6e55bb8`, `a46ac67d` and `136ed26f`, delivery 8 (Slurm 4841313) carried `e74913ec`, the first additions to the numbers script and the index builder, and delivery 9 (Slurm 4842129) carried `83f9970b`, the comparison with round 5.

The md5 of each round 7 script at each snapshot it ran from is below, read from `results/round7/ppi/provenance_index.csv`.

| script | `ba3129e4` (S1 units) | `d0462a70` (S2 units) | `136ed26f` (lung reruns, merges, numbers) |
|---|---|---|---|
| `round7_ppi_run.py` | `3f37e77c2abe22afa6eca8772282f4f0` | `3f37e77c2abe22afa6eca8772282f4f0` | `3f37e77c2abe22afa6eca8772282f4f0` |
| `round7_ppi_d2.py` | `31d5b0e396d85d3c49709f216d89d4af` | `31d5b0e396d85d3c49709f216d89d4af` | `31d5b0e396d85d3c49709f216d89d4af` |
| `round7_ppi_weighting.py` | `ee9f238c793912cd3045e88aba89c5e8` | `ee9f238c793912cd3045e88aba89c5e8` | `19137aac514748f8aa6b054157067e29` |
| `round7_ppi_s1_masking.py` | `9e945ff59c4363a5121e16335e2d6dcb` | | `9e945ff59c4363a5121e16335e2d6dcb` |
| `round7_ppi_s1_sim.py` | `f14f4527435618596d0097ab41bb51e2` | | |
| `round7_ppi_s2_comparators.py` | | `7fc22eab8e5ef6f9f6047281878629be` | |
| `round7_ppi_merge.py` | | | `c8ad6fd5f63296a85c7f664d871631bb` |
| `round7_ppi_i01_numbers.py` | | | `9f4e020fe598f59b778ea9583ae2e892` |

The cited numbers run is from `83f9970b`, where `round7_ppi_i01_numbers.py` has md5 `93069cf054df1796ba64ce6c8d597d09`. The draw-count diagnostic ran from `e74913ec`, and the scripts it ran are unchanged from `136ed26f` (`round7_ppi_s1_sim.py` `f14f4527435618596d0097ab41bb51e2`, `round7_ppi_weighting.py` `19137aac514748f8aa6b054157067e29`).

`code/scripts/round7_ppi_provenance_index.py` builds the index. It runs in the Mac clone as documentation work, like the sweep, and reads only the committed records.

### 2.3 Provenance index

`results/round7/ppi/provenance_index.csv` has 4280 rows, one per job and script, over 308 `PROVENANCE.txt` records. These are every compute job of the interval, including the four pilots whose records stay on Longleaf and are copied to `results/round7/ppi/provenance_raw/`. Every recorded commit is an ancestor of the commit tested, and every script md5 equals the md5 of that script at the recorded commit. The commit tested is the parent of the gate commit, and the gate tag is a descendant of it, so check 1 carries over to the tag. Code deliveries, the clone job and the copy-back packs write no `PROVENANCE.txt` and are not in the index.

## 3. Acceptance checks

### 3.1 S0 anchors

From `results/round7/ppi/S0_anchors/s0_anchors.csv`.

| cell | target `wr_D0cl` | arm 1, round 5 code | arm 2, round 5 draws, new code | arm 2, new draws | z of arm 2 |
|---|---|---|---|---|---|
| `CCRCC`, `uni_v2` | 0.7262961345 | 0.7262961345 | difference 2.220446049e-16 | 0.731627244 | 0.445761984 |
| `ACS_STATES`, `package` | 0.55129056 | 0.55129056 | difference -2.220446049e-16 | 0.5523268228 | 0.1616101163 |

Both cells are $\theta_3$, own balance, $p_a = 0.01$, $n_L = 8$. The tolerance for arm 2 with new draws is twice the root sum of squares of the two bootstrap standard errors, 0.023919 and 0.012824. The median thresholds agree with round 5's to ratios of 0.9999999285 and 1.000000008.

### 3.2 S1 synthetic test

From `results/round7/ppi/S1_weighting/tests/run2/s1_tests.csv` (Slurm 4824390, snapshot `ba3129e4`). $\hat\theta_{\mathrm{HT}}$ is unbiased within Monte Carlo error in every cell, while the classical mean's standardised bias reaches -37.39 in the skewed cells. The Sen-Yates-Grundy mean over empirical variance lies between 0.9190678323 and 1.031688318 in the normal cells and passes in each. It fails in the six skewed cells with support of at least 1,000, with values from -0.1684027842 to 0.438891062. Section 1.9 of `docs/round07/tracks/ppi/round07_ppi_theory.md` gives the cause, exact zero pair probabilities. The first run (Slurm 4820548) failed check C on a threshold tie, fixed in `ba3129e4` (escalation 4). Job ids are rows of `results/round7/ppi/r7ppi_slurm_jobs.csv`.

### 3.3 Comparator checks

From `results/round7/ppi/S2_comparators/tests/bh_tests.csv` (Slurm 4820550). On 200 i.i.d. data sets with every cluster of size one, Broska and Howes's variance equals the PPI++ variance of their example 1 to a relative difference of 1.65215258938e-15 against a tolerance of 1e-10. With a constant predictor $\hat\lambda$ is set to 0. At $G = 2000$ under Bernoulli(0.2) selection of whole clusters it covers 0.9025 over 4000 replicates, within three standard errors (0.0142) of 0.90. The job is a row of `results/round7/ppi/r7ppi_slurm_jobs.csv`.

From `results/round7/ppi/S2_comparators/tests/impl_run2/s2_impl_tests.csv` (Slurm 4825394, snapshot `d0462a70`), the implementation checks all pass. The cluster-count form equals the direct one with a difference of 0, the score probabilities sum to $n_L$ within 7.1054273576e-15, none exceeds 1, and with a constant predictor Kluger et al.'s estimate is the labelled mean within 4.85722573274e-17. The first run (Slurm 4824921) failed the constant-predictor check, fixed in `d0462a70` (escalation 5). Both jobs are rows of `results/round7/ppi/r7ppi_slurm_jobs.csv`.

### 3.4 Coverage of the grids, stamps and merges

The S1 merge (Slurm 4840163 in `results/round7/ppi/r7ppi_slurm_jobs.csv`) found 162 unit directories and merged 152, listed with their stamps in `results/round7/ppi/S1_weighting/_merged/s1_stamp_check.csv`. The 10 left out are the failed lung directories, whose `_r2` reruns are merged in their place. Every merged directory carries the frame id assigned in `results/round7/ppi/S1_weighting/s1_assigned_frame_ids.csv`. The S2 merge (Slurm 4834044) merged 126 of 126 directories, with no stamp mismatch, in `results/round7/ppi/S2_comparators/_merged/s2_stamp_check.csv` against `results/round7/ppi/S2_comparators/s2_assigned_frame_ids.csv`.

The cells not run are those of `results/round7/ppi/S1_weighting/_merged/s1_skipped.csv`, which are of two kinds. The constant arm has no embedding, so `pcE2` is skipped for it on the four tissue tasks. The constant arm is skipped on the census mean, as in round 5. S2 uses no balance variable, so its only skip is the constant arm on the census mean, as `results/round7/ppi/S2_comparators/_merged/s2_masking_grid.csv` shows. No design was impossible to form at any $n_L$.

## 4. What differs between the arms of each comparison

1. **S0 arm 1 against round 5.** Nothing differs. The script, seeds, threshold pool and draws are round 5's E4b, run from snapshot `c9570f7b`. The only difference from the run that wrote the anchor rows is the script version (escalation 1).
2. **S0 arm 2 with round 5's draws against arm 1.** The code that turns accepted draws into intervals differs (`round7_ppi_d2.py` against round 5's script). Draws, thresholds, genes and interval are the same.
3. **S0 arm 2 with new draws against arm 1.** The accepted draws differ (new seeds and accept-until-accepted with no fallback) and so does the code. Thresholds, genes and interval are the same.
4. **S1, weighted estimators against the classical mean with `rej_t`, under D2.** The weights differ ($1/\hat\pi_g$ against equal), and so do the variance estimate (Sen-Yates-Grundy with simulated $\hat\pi_{gh}$, or one of the two approximations, against `rej_t`) and, for the reference `n1`, the degrees of freedom ($t_{n_L-1}$ against $t_{n_L-k-1}$). The draws, thresholds, genes, balance variable and $p_a$ are the same. $\hat\theta_{\mathrm{HT},\lambda}$ also differs by its cross-fitted coefficient.
5. **S1, any D2 interval against D0 classical (`wr_D0cl`).** The design differs (D2 against simple random selection) and so do the draws. The genes, task, arm, estimand and $n_L$ are the same.
6. **S2, Broska and Howes against `textbook_t|fpc|lin|xf` and round 5's superpopulation interval, under D0.** The estimator differs (one global $\hat\lambda$ against round 5's cross-fitted coefficient), the variance differs (their plug-in with no finite-population factor against the design forms), and the quantile differs (normal against $t$). The draws, genes and target are the same.
7. **S2, Kluger et al.'s designs against D0.** The design differs (independent Bernoulli with random size, uniform or score-mixed, against fixed-size simple random), the draws differ, and the interval differs (cluster bootstrap percentile with $B = 2000$, or the Poisson-design variance with $t$, against `textbook_t|fpc|lin`). Genes and target are the same.
8. **S2, the design target in set `A_fixed` against the superpopulation target in set `B_world`.** The world differs (the observed clusters against clusters resampled from them, theory section 2.3), and so does the target (the observed clusters' mean against the mean of the world's generating distribution). Estimators and intervals are the same.

## 5. Predictions against outcomes

The verdicts are those of `results/round7/ppi/_i01_numbers_r3/i01_prediction_scores.csv`, with the cells behind them in `results/round7/ppi/_i01_numbers_r3/i01_prediction_cells.csv`.

| id | prediction | operational test | outcome | verdict |
|---|---|---|---|---|
| S1.1 | Simulation, $k = 2$, $n_L \le 6$. The classical mean's bias exceeds 0.1 of its standard deviation in at least a quarter of the cells, and the Hájek interval covers within 0.03 of nominal in at least three quarters | noise-corrected root mean square of bias over sd per cell, D2; Hájek with `sim` and $t_{n_L-k-1}$ | bias above 0.1 sd in 0.654 of 240 cells; Hájek within 0.03 of 0.90 in 0.046, and with $t_{n_L-1}$ in 0.000 | partly held |
| S1.2 | Real tasks, `pcF2` and `pcE2`, $n_L = 6$. The Hájek interval covers within 0.03 of D0 classical in at most half of the cells where `rej_t` covered below 0.80 | median over genes of coverage per cell | 4 such cells, Hájek within 0.03 in 0 of them | held |
| S1.3 | $n_L = 8$, own balance. The Hájek interval is wider than `rej_t` in every supported cell, by a ratio of 1.10 to 1.50 | ratio of median widths, cells with support of at least 1,000 | 72 cells; wider in 0.708, in the band in 0.194; ratios 0.869 to 1.891, median 1.028 | partly held |
| S1.4 | $\theta_3$, own balance, $p_a = 0.01$, $n_L = 4$. The smallest $\hat\pi_g$ is below 0.5 $n_L/G$ on both census tasks | smallest $\hat\pi_g/(n_L/G)$, package arm | `ACS_STATES` 0.0144, `ACS_CA_PUMA` 0.1464 | held |
| S2.1 | D0, design target. Broska and Howes covers below 0.85 at $n_L = 4$ on at least two of four tissue tasks | per task, median over arms and estimands of the median coverage over genes | `CCRCC` 0.698, `CCRCC_merged` 0.707, `INDIANA_KIDNEY` 0.698, `LUNG_XENIUM` 0.724, so 4 tasks | held |
| S2.2 | Design target with $n_L/G \ge 0.5$. It covers above 0.95 | the same, per cell | 5 of 30 cells above 0.95; range 0.878 to 0.995 | refuted |
| S2.3 | Superpopulation target. It covers below 0.85 at $n_L \le 6$ in every simulation cell with $G = 15$ | mean coverage per simulation cell | 40 of 40 cells below 0.85; range 0.584 to 0.825 | held |
| S2.4 | Superpopulation target. Kluger et al.'s cluster bootstrap covers below 0.85 at $n_L \le 8$ on every task | set `B_world`, both Bernoulli designs, every arm and estimand | 266 of 266 cells below 0.85; per-task medians 0.710 (`LUNG_XENIUM`) to 0.765 (`ACS_CA_PUMA`) | held |

S1.1 holds on the bias and fails on the coverage. S1.2 holds in the strongest form, since in all 4 cells the Hájek interval covers less than `rej_t` does (0.73775, 0.74950, 0.73125 and 0.63375 against 0.787, 0.79975, 0.79825 and 0.791, `results/round7/ppi/_i01_numbers_r3/i01_prediction_cells.csv`). S2.2 fails because the conservatism of Broska and Howes's interval at large $n_L/G$ is real but smaller than predicted. The per-task maxima of S2.4 are 0.810 to 0.841 (`results/round7/ppi/_i01_numbers_r3/s2_report_numbers.csv`), so the prediction holds in every cell and not only at the median.

My own expectations of theory section 1.8, scored on the same files (`results/round7/ppi/_i01_numbers_r3/s1_report_numbers.csv`), are these.

1. **Bias.** Held where every $\hat\pi_g$ is positive, with exceptions. Over the 1336 D2 cells of the real tasks the median share of genes with standardised bias above 3 is 0.44 for the classical mean, 0 for $\hat\theta_{\mathrm{HT}}$ and 0.02 for $\hat\theta_{\mathrm{H}}$. That share exceeds 0.1 in 930 cells for the classical mean, 156 for $\hat\theta_{\mathrm{HT}}$ and 525 for $\hat\theta_{\mathrm{H}}$. Of the 156, 136 are cells with a zero $\hat\pi_g$ (escalation 3), where the median share for $\hat\theta_{\mathrm{HT}}$ is 0.28 against 0 elsewhere. The other cells among the 156 have every $\hat\pi_g$ positive, and I have not explained them. For $\hat\theta_{\mathrm{H}}$, 224 of the 525 have a zero $\hat\pi_g$. The rest may be the ratio bias of the Hájek mean at few labelled clusters, which section 1.2 of the theory does not treat, and that is not checked.
2. **Coverage where `rej_t` failed.** Refuted, with a caveat. Only a share of 0.009 of the 880 supported cells has `rej_t` below 0.80, not the 17 cells of round 5, and in the 4 of them at $n_L = 6$ the Hájek interval covers less than `rej_t` (S1.2 above). Round 5's worst cells, Indiana $\theta_2$ at $n_L = 6$, no longer fail in round 7, for a reason not yet settled (escalation 12).
3. **Width.** Partly held. The Hájek interval is wider than `rej_t` in 0.708 of the cells at $n_L = 8$ with own balance, with a median ratio of 1.028, below the 1.05 to 1.40 I expected.
4. **The approximations.** Held. Over supported cells the median of `wr_D0cl` is 1.027 for the Hájek interval with `apx_size`, against 0.9971 for the classical interval, and the median relative error of `apx_bal` against the simulated $\hat\pi_{gh}$ is 0.03626818.
5. **The difference form.** Held. The median `wr_D0cl` is 1.041 for $\hat\theta_{\mathrm{HT},\lambda}$ against 1.011 for the Hájek interval.

## 6. Results

### 6.1 S1 on the real tasks

Over the 880 supported D2 cells (support of at least 1,000) of the four tissue and two census tasks, per estimator and interval, from `results/round7/ppi/_i01_numbers_r3/s1_report_numbers.csv`. Coverage is the median over cells of the median over genes, with the minimum over cells beside it.

| estimator, variance, reference | median coverage | minimum | share below 0.80 | share within 0.03 of D0 classical | median `wr_D0cl` |
|---|---|---|---|---|---|
| classical, `textbook_t\|fpc\|lin`, $t_{n_L-1}$ | 0.8879 | 0.8097 | 0 | 0.8886 | 0.9971 |
| classical, `rej_t` | 0.8779 | 0.781 | 0.009091 | 0.8557 | 1.016 |
| $\hat\theta_{\mathrm{HT}}$, `sim`, $t_{n_L-k-1}$ | 0.8699 | 0.4165 | 0.1568 | 0.6489 | 1.025 |
| $\hat\theta_{\mathrm{H}}$, `sim`, $t_{n_L-k-1}$ | 0.8665 | 0.5523 | 0.1125 | 0.7102 | 1.011 |
| $\hat\theta_{\mathrm{H}}$, `sim`, $t_{n_L-1}$ | 0.8464 | 0.5105 | 0.183 | 0.483 | 0.9538 |
| $\hat\theta_{\mathrm{H}}$, `apx_size`, $t_{n_L-k-1}$ | 0.8932 | 0.7923 | 0.001136 | 0.7 | 1.027 |
| $\hat\theta_{\mathrm{H}}$, `apx_bal`, $t_{n_L-k-1}$ | 0.8719 | 0.483 | 0.1398 | 0.6716 | 0.983 |
| $\hat\theta_{\mathrm{HT},\lambda}$, `sim`, $t_{n_L-k-1}$ | 0.8771 | 0.4165 | 0.1034 | 0.7125 | 1.041 |
| Broska and Howes, normal | 0.8466 | 0.5753 | 0.25 | 0.2386 | 0.8451 |

Of the D2 intervals, `rej_t` and the Hájek interval with `apx_size` cover best, and at the median both are about as wide as the D0 classical interval (median `wr_D0cl` 1.016 and 1.027). The weighted intervals with simulated pair probabilities have long lower tails of coverage and are no narrower than `rej_t` at the median. The mechanism of the lower tails is section 1.9 of the theory. Pairs with $\hat\pi_{gh} = 0$ occur in 665 of the 1336 D2 cells, with the largest share of such pairs in a cell 0.9722222 on `LUNG_XENIUM` and 0.6521739 on `CCRCC`, and the Sen-Yates-Grundy form loses their terms. The `apx_size` variance ignores the balance, which keeps it from losing those terms, as expectation 4 anticipated.

### 6.2 S1 in simulation

Over the D2 cells of `results/round7/ppi/S1_weighting/_merged/s1_sim.csv` (260 cells per law and $k$), from `results/round7/ppi/_i01_numbers_r3/s1_report_numbers.csv`. Coverage is the mean over cells of the mean over 60 populations, with the minimum over cells beside it.

| estimator | law, $k$ | mean coverage | minimum | share within 0.03 of 0.90 | share of cells with bias above 0.1 sd |
|---|---|---|---|---|---|
| classical, `rej_t` | normal, 1 | 0.9015 | 0.8723 | 0.9962 | 0.2423 |
| classical, `rej_t` | normal, 2 | 0.9075 | 0.8765 | 0.7462 | 0.2808 |
| classical, `rej_t` | skewed, 1 | 0.814 | 0.7734 | 0.03846 | 0.7038 |
| classical, `rej_t` | skewed, 2 | 0.8297 | 0.7737 | 0.05385 | 0.7346 |
| $\hat\theta_{\mathrm{H}}$, `sim`, $t_{n_L-k-1}$ | normal, 1 | 0.7682 | 0.1306 | 0.3538 | 0.05769 |
| $\hat\theta_{\mathrm{H}}$, `sim`, $t_{n_L-k-1}$ | normal, 2 | 0.8035 | 0.4926 | 0.2731 | 0.06154 |
| $\hat\theta_{\mathrm{H}}$, `sim`, $t_{n_L-k-1}$ | skewed, 1 | 0.6627 | 0.1429 | 0 | 0.7231 |
| $\hat\theta_{\mathrm{H}}$, `sim`, $t_{n_L-k-1}$ | skewed, 2 | 0.7131 | 0.3938 | 0 | 0.6692 |
| $\hat\theta_{\mathrm{HT}}$, `sim`, $t_{n_L-k-1}$ | skewed, 1 | 0.6686 | 0.1451 | 0 | 0.7154 |
| $\hat\theta_{\mathrm{HT},\lambda}$, `sim`, $t_{n_L-k-1}$ | normal, 2 | 0.8803 | 0.5744 | 0.65 | 0.2769 |
| Broska and Howes | normal, 1 | 0.9019 | 0.682 | 0.2115 | 0.25 |

In simulation too, weighting under D2 lowers coverage against `rej_t`. The classical mean is biased as theory section 1.2 says, by more than 0.1 sd in 0.7038 of the skewed cells with $k = 1$ against 0.2423 of the normal ones.

The weighted estimators also show a standardised bias above 0.1 sd in most skewed cells, which a design-unbiased estimator should not. In the skewed cell at $G = 51$, $n_L = 8$, $k = 1$, $p_a = 0.1$, $\lambda^* = 0.6$, the noise-corrected bias of $\hat\theta_{\mathrm{HT}}$ rises with the cluster $R^2$, from 0.020942 at $R^2 = 0$ to 0.652589 at $R^2 = 0.9$, and the mean ratio of estimated to empirical variance rises with it, from 1.004624 to 1.469514 (`results/round7/ppi/S1_weighting/_merged/s1_sim.csv`). Under D0, with equal probabilities, $\hat\theta_{\mathrm{HT}}$ shows no bias above 0.1 sd in any cell of either law.

My first reading was that this is a property of the finite set of 1,000 replayed draws per population, since at high $R^2$ the clusters with the largest $z_g$ have extreme $f_g$ and D2 rarely accepts them. A diagnostic run refutes it. The same cell rerun with 5,000 draws per population (Slurm 4841362, snapshot `e74913ec`) gives a noise-corrected bias of 0.635143 at $R^2 = 0.9$ against 0.652589 with 1,000, and 0.693763 against 0.722836 at $p_a = 0.01$, so the bias does not shrink with the number of draws (`results/round7/ppi/S1_weighting/tests/sim_draws_diag/G51_s_k1_nL8_D5000/s1_sim__G51_s_k1_nL8.csv`, with the command line in `results/round7/ppi/S1_weighting/tests/sim_draws_diag/G51_s_k1_nL8_D5000/PROVENANCE.txt` and the job in `results/round7/ppi/r7ppi_slurm_jobs.csv`). The share of populations with standardised bias above 3 stays near a quarter (0.216667 against 0.283333), while for the classical mean it rises from 0.266667 to 0.55, as a bias common to all populations would. So the weighted estimators are biased in a subset of the 60 populations and not in the others. The likeliest cause is the one of escalation 3, a cluster that D2 never accepts in those populations, since the median over populations of the smallest $\hat\pi_g/(n_L/G)$ in that cell is 0.083194. The simulation output keeps only that median and not each population's smallest $\hat\pi_g$, so this is not yet checked (section 8). The synthetic test of section 3.2, on round 5's test 3 populations rather than these, finds $\hat\theta_{\mathrm{HT}}$ unbiased in its skewed cells.

### 6.3 S2 on the real tasks

Median over cells of the median coverage over genes, nominal 0.90, from `results/round7/ppi/_i01_numbers_r3/s2_report_numbers.csv`. Set `A_fixed` is the design target. Set `B_world` gives the superpopulation target in resampled worlds.

| set, target | design, interval | $n_L = 4$ | 6 | 8 | 12 | 16 (census) |
|---|---|---|---|---|---|---|
| `A_fixed`, design | D0, classical `textbook_t\|fpc\|lin` | 0.900 | 0.890 | 0.882 | 0.885 | 0.899 |
| `A_fixed`, design | D0, tuned `textbook_t\|fpc\|lin\|xf` | 0.900 | 0.886 | 0.876 | 0.879 | 0.908 |
| `A_fixed`, design | D0, Broska and Howes | 0.707 | 0.805 | 0.858 | 0.927 | 0.941 |
| `A_fixed`, design | Bernoulli uniform, Kluger cluster bootstrap | 0.679 | 0.795 | 0.852 | 0.927 | 0.935 |
| `A_fixed`, design | Bernoulli uniform, Hájek Poisson | 0.866 | 0.863 | 0.865 | 0.873 | 0.886 |
| `A_fixed`, design | Bernoulli uniform, HT Poisson | 0.957 | 0.908 | 0.884 | 0.891 | 0.912 |
| `B_world`, super | D0, Broska and Howes | 0.664 | 0.747 | 0.784 | 0.823 | 0.863 |
| `B_world`, super | D0, classical round 5 superpopulation | 0.878 | 0.881 | 0.882 | 0.881 | 0.898 |
| `B_world`, super | D0, tuned round 5 superpopulation | 0.878 | 0.864 | 0.864 | 0.863 | 0.855 |
| `B_world`, super | Bernoulli uniform, Kluger cluster bootstrap | 0.624 | 0.718 | 0.771 | 0.815 | 0.865 |
| `B_world`, super | Bernoulli score-mixed, Kluger cluster bootstrap | 0.618 | 0.720 | 0.775 | 0.814 | 0.861 |

Both comparators from the literature under-cover badly at few labelled clusters, for either target. For the design target they reach nominal only as $n_L/G$ grows, where their missing finite-population factor makes them conservative. Their median widths against D0 classical are 0.768633 for Broska and Howes and 0.793928 for Kluger et al.'s bootstrap under the uniform design. The round 5 superpopulation interval is the only one near nominal for the superpopulation target at every $n_L$. Under Kluger et al.'s Bernoulli designs a draw has fewer than two labelled clusters with probability up to 0.098, and the bootstrap drops up to 0.12297 of its replicates as degenerate.

### 6.4 S2 in simulation

Mean coverage over cells, nominal 0.90, from `results/round7/ppi/_i01_numbers_r3/s2_report_numbers.csv`.

| G | design, interval, target | $n_L = 4$ | 6 | 8 | 12 |
|---|---|---|---|---|---|
| 15 | D0, Broska and Howes, design | 0.783 | 0.862 | 0.911 | 0.979 |
| 15 | D0, Broska and Howes, super | 0.685 | 0.738 | 0.765 | 0.795 |
| 15 | D0, classical round 5 superpopulation, super | 0.853 | 0.858 | 0.863 | 0.871 |
| 15 | Bernoulli uniform, Kluger cluster bootstrap, super | 0.628 | 0.711 | 0.744 | 0.691 |
| 51 | D0, Broska and Howes, design | 0.707 | 0.790 | 0.834 | 0.882 |
| 51 | D0, Broska and Howes, super | 0.671 | 0.743 | 0.776 | 0.809 |
| 51 | Bernoulli uniform, Kluger cluster bootstrap, super | 0.604 | 0.700 | 0.757 | 0.804 |

The simulation repeats the real-task pattern, with Broska and Howes reaching 0.979 for the design target at $G = 15$, $n_L = 12$, where $n_L/G$ is 0.8.

### 6.5 `rej_t` against round 5, cell by cell

The S0 anchor checks one estimand and one balance variable. The numbers job therefore joins every D2 `rej_t` cell of the S1 grid to round 5's `results/round5/ppi/E4b_rejective/e4b_rej_width_ratios.csv`, which matches 960 of the 1336 cells (the others are cells round 5 did not run, the constant arm, census at $n_L = 16$, and two balance variables at $n_L = 4$ on the tissue tasks). The joined table is `results/round7/ppi/_i01_numbers_r3/i01_rej_t_vs_round5.csv` and the counts are in `results/round7/ppi/_i01_numbers_r3/s1_report_numbers.csv`.

For $\theta_3$ the two agree. Coverage differs by more than 0.03 in 3 of 480 cells, all on `LUNG_XENIUM` with round 5 supports of at most 13.65, and by at most 0.00275 on the other tasks. For $\theta_2$ coverage differs by more than 0.03 in 157 of 480 cells, by up to 0.877, and the round 7 value is the higher one, by a median of 0.2079303 over those cells. The differences sit at the smallest $n_L$ of every tissue task. Every $\theta_2$ cell differs at $n_L = 4$ on all four tissue tasks, at $n_L = 6$ on `INDIANA_KIDNEY` and `LUNG_XENIUM`, and 29 of 32 at $n_L = 8$ on `LUNG_XENIUM`, while no census cell differs. The D0 classical coverage of the same cells agrees with round 5 to 0.00816288, so the difference is in the D2 draws or in `rej_t` for $\theta_2$, not in the genes or the reference interval.

Round 5's eight worst cells, Indiana $\theta_2$ at $n_L = 6$ with two balance variables, covered 0.641 to 0.684 according to `docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, and they are among the cells that differ. Section 7, escalation 12, gives what I think the difference is and what would settle it.

## 7. Discrepancies, open questions and escalations

1. **Anchor code version.** The `rej_t` anchor rows of round 5 were written by E4b jobs 4382135 and 4382108 at snapshot `9185bc6`, script md5 `228972e745a16ad91b5a368600e6acda`, with a float32 threshold. The script at the starting commit has md5 `059c18e1b4998b1ac9c9685ba324a872`, with a float64 threshold. Arm 1 ran the starting-commit script, and the anchors pass to four decimals regardless (section 3.1, `results/round7/ppi/S0_anchors/s0_anchors.csv`).
2. **Round 5's `_threshold/` holds only the medians over genes.** The per-gene thresholds were recomputed deterministically from round 5's pool and match the medians to the ratios of section 3.1.
3. **Zero inclusion probabilities on the real tasks.** Under D2, 225 of the 1336 cells on the real tasks have a column with some $\hat\pi_g = 0$, all on the tissue tasks (51 on `CCRCC`, 47 on `CCRCC_merged`, 33 on `INDIANA_KIDNEY`, 94 on `LUNG_XENIUM`, 0 on either census task), and 665 have pairs with $\hat\pi_{gh} = 0$ (`results/round7/ppi/_i01_numbers_r3/s1_report_numbers.csv`). The track lists a zero $\hat\pi_{gh}$ outside the census tasks as an escalation, and a zero $\hat\pi_g$ is stronger, since $\hat\theta_{\mathrm{HT}}$ is then not design-unbiased. In those cells, rejective balance at a small $p_a$ excludes the clusters whose balance variable is extreme. One remedy is a defensive mixture, drawing by simple random selection with a small probability $\epsilon$ and by D2 otherwise, which makes every $\pi_g$ at least $\epsilon\,n_L/G$ and every $\pi_{gh}$ positive. It is the oversight chat's decision.
4. **The threshold-tie fix.** Check C of the first synthetic test failed at $G = 15$, $n_L = 6$, $p_a = 0.01$ because a candidate exactly at the threshold was accepted by one code path and not the other. Acceptance is now at the threshold times $1 + 10^{-9}$ in both (`ba3129e4`), and the second run passes the check.
5. **The Ω fix.** The first S2 implementation check (Slurm 4824921) failed for Kluger et al.'s estimator with a constant predictor. A threshold on Ω now treats it as zero there (`d0462a70`), and the second run passes (section 3.3).
6. **The degenerate-π fix and the lung reruns.** Ten S1 `LUNG_XENIUM` jobs at $n_L$ of 4 and 12 on snapshot `ba3129e4` failed in `pgh_apx_bal` with "SVD did not converge", for example `LUNG_XENIUM_resnet50_nL4` (Slurm 4826736), on columns whose $\hat\pi_g$ are all 0 or 1. Commit `136ed26f` gives such a column no approximation, and the ten were rerun into `_r2` directories on that snapshot. In `ba3129e4` any such column raises the same error, so every unit that completed on it had no such column, and its outputs would be the same under `136ed26f`. S1 therefore mixes two snapshots, with the difference confined to approximate intervals on degenerate columns.
7. **The superpopulation target on the real tasks** is measured in resampled worlds (theory section 2.3), not on the observed clusters, since the observed clusters have one design-target value per gene and no superpopulation replicate. The `B_world` numbers of section 6.3 are therefore statements about worlds built from the observed clusters.
8. **Pilot outputs stay on Longleaf**, under `results/round7/ppi/S1_weighting/_pilot/` and `results/round7/ppi/S2_comparators/_pilot/` there. Their provenance records are in `results/round7/ppi/provenance_raw/`.
9. **Output locations.** The track names `s1_pi_hat.parquet`, `s1_sim.csv`, `s1_masking_grid.csv`, `s2_sim.csv` and `s2_masking_grid.csv` directly under `S1_weighting/` and `S2_comparators/`. They are in the merge jobs' own output directories `results/round7/ppi/S1_weighting/_merged/` and `results/round7/ppi/S2_comparators/_merged/`, beside their `PROVENANCE.txt`, and the two report-number files are in `results/round7/ppi/_i01_numbers_r3/`. I can copy them to the named places if the memo prefers.
10. **How the sub-agents got their frame ids.** The track asks for the frame id in the first message of the brief. The id of a sub-agent exists only once it is spawned, so each brief said that the id would follow and forbade any job before it, and the id went in the second message seconds later. Every returned stamp carries the assigned id (section 3.4).
11. **A duplicate row type in the first numbers file.** `results/round7/ppi/_i01_numbers/s2_report_numbers.csv` wrote each `S2m_wr_D0cl_median` row of set `B_world` twice, once per target, with equal values. Commit `e74913ec` writes it once, and the cited rerun in `results/round7/ppi/_i01_numbers_r3/` has it once.
12. **`rej_t` for $\theta_2$ does not reproduce round 5 at small $n_L$** (section 6.5). The two runs use the same candidate seeds and thresholds, and differ in that round 7 scans past 2,000 candidates until one is accepted, where round 5's `d2_select` fell back to the last candidate. A fallback would be most frequent where few candidates are acceptable, which for $\theta_2$ is where few labelled clusters are valid, at small $n_L$, and that is where the differences sit. But they also include cells at $p_a = 0.1$ with a round 5 support of up to 3876, where a fallback within 2,000 candidates should be rare, so the fallback may not be the whole explanation. What would settle it is the share of round 5's draws that used the fallback, cell by cell, which round 5's files do not record and which a replay of round 5's own selection could count. Until then the S1 numbers for $\theta_2$ at $n_L \le 6$ on the tissue tasks, and every comparison of them with round 5, should be read as unconfirmed. This bears on S1.2 and on expectation 2 of section 5. Round 5's eight worst cells of `rej_t` were $\theta_2$ cells of this kind, and round 7 does not see them fail.

## 8. What was not checked

1. Whether the populations in which $\hat\theta_{\mathrm{HT}}$ and $\hat\theta_{\mathrm{H}}$ are biased in the skewed simulation cells are those with some $\hat\pi_g = 0$ (section 6.2). The diagnostic run shows the bias is not a finite-draw effect. Settling the cause needs the per-population smallest $\hat\pi_g$ and signed bias, which the simulation script does not write.
2. The overstatement factor of Broska and Howes's interval derived in theory section 2.1 against the measured widths, cell by cell. Section 6.3 gives only the median width ratio.
3. A comparison with the authors' implementations of either comparator, which would need a download, Nicolas's decision.
4. The per-gene tables of the four pilots, which stay on Longleaf.
5. Whether the 10 failed lung directories left partial outputs that differ from their reruns. They are kept in the commit as a record and were not merged.
6. The cause of the $\theta_2$ difference from round 5 of section 6.5. The S0 anchor covers $\theta_3$ with own balance only, and no anchor was run for $\theta_2$.

## 9. Proposed next step

The track proceeds to S3 only on the S2 decision memo. Before it, four things would help the memo. A replay of round 5's own selection for the $\theta_2$ cells of section 6.5 that counts its fallbacks, which would settle escalation 12 and is the most important of the four. A per-population output for section 8 item 1, a small change to `round7_ppi_s1_sim.py` and a job of about ten minutes on the cell of section 6.2. A decision on the zero inclusion probabilities of escalation 3, since the adaptive design of S3 and the k-center rule of S4 both rely on $\hat\theta_{\mathrm{HT}}$ being design-unbiased. And, given that `rej_t` outperforms the weighted intervals under D2, a view on whether S3's comparison should be against D2 with `rej_t`, as prediction S3.1 already states.
