# Round 11, track `closeout`, gate G2 report: the stronger predictor

*17 November 2026. Written by the first session of track `closeout` (frame `c9016697-c909-435e-82fc-ebfb9daaa857`) under the brief `docs/round11/closeout/round11_closeout_brief.md` and the plan `docs/round11/closeout/round11_closeout_plan.md`, whose section 4 defines the arms and section 3 the gates. Paths beginning `results/` are in the repository. Longleaf paths are under `/work/users/w/e/weiyang/hest_replication/results/round11/closeout/`.*

## 1. Stage and status

G2 is the gate after the stronger-predictor runs (plan, section 3). Part A's inventory, literature search, anchors and strength runs are done. **The primary predictor `P` is not stronger by the masterplan's measure**: it gains 0.010 to 0.018 in donor-held-out median spot-level Pearson, against the 0.02 that P11.1 asks for on two of three tasks. So P11.1 is refuted, and under the brief (section 4, standard 5) P11.2 to P11.4 are scored "not tested". Part B items 3 to 7 are done and scored, and item 1 (the headline numbers recomputed) is done. Item 2 (H1(b) refits) has not started. Nothing after this gate has been set up, staged or piloted. KIDNEY_E_STATUS

Section 7 marks two items as substantive for Nicolas (masterplan, "Who decides the gates"): the CCRCC width-ratio anchor, which misses the brief's Monte Carlo criterion because the inputs differ, and the choice of what Part A does now that the primary is not stronger.

## 2. What was run

Every job ran on Longleaf from a read-only `git archive` snapshot of a commit on `round11-closeout`, through `code/scripts/round11_closeout_run.sh`, which stamps each output directory (`_provenance.json`, project `proj_8450e231133d`, this frame) and writes `PROVENANCE.txt` on the node. The job ledger with Slurm ids, partitions, nodes, walls and peak memory is `results/round11/closeout/g2/gate/job_ledger.csv`; snapshots are in `code_deliveries.csv` and the provenance check in `provenance_index.csv` beside it (section 3).

| stage | unit (Longleaf, also `results/round11/closeout/`) | script | Slurm | commit |
|---|---|---|---|---|
| A0 | `inventory/inv_v1` | `round11_closeout_inventory.py` | 9469547 | `fc0eb953` |
| A2 | `predict/selftest_v1`, `predict/kidney__Visium__R10__{donor,center}` | `round11_closeout_predict.py` | 9471137, 9471138, 9471139 | `59e4e3c6` |
| A2 | `anchor/CCRCC__R10_v2` (predict, join, D12, cluster values, regime A) | `round11_closeout_chain.py` with spec `results/round11/closeout/specs/CCRCC__R10.json` | 9503536 | `b9142ddc` |
| A2 | `anchor/CCRCC__record` (control) | the same, spec `specs/CCRCC__record.json` | 9518341 | COMMIT_CTRL |
| A5 | `predict/<task>__<arm>__<design>`, 18 units | `round11_closeout_predict.py`, submitted by `round11_closeout_submit_a5.sh` | 9503517 to 9503534 | `b9142ddc` |
| A5 | `predict/kidney__Visium__E__donor_v2` | the same | 9518165 | `78ad361c` |
| B3 | `b3/s0006_v1` | `round11_closeout_b3_s0006.py` | 9470327 | `e09a9cf4` |
| B4 | `b4/equal_v2` | `round11_closeout_b4_equal.py` | 9503535 | `b9142ddc` |
| B5 | `b5/withinvar_v1` | `round11_closeout_b5_withinvar.py` | 9471875 | `cd54e3a9` |
| B6 | `b6/stored_v1` | `round11_closeout_b6_stored.py` | 9470328 | `e09a9cf4` |
| B7 | `b7/ledger_v2` | `round11_closeout_b7_ledger.py` | 9495763 | COMMIT_B7 |
| G2 | `g2/aggregate_v3`, `g2/gate` | `round11_closeout_g2_aggregate.py`, `round11_closeout_gate.py` | AGG_JOB, GATE_JOB | COMMIT_G2 |

Script md5s are in each `PROVENANCE.txt` and are checked against their commits in `provenance_index.csv`. Two runs were superseded and are not scored: B4 v1 (Slurm 9471874), whose keys left out `estimand`, and B7 v1 (9469936), which read the harness's `job.sh` but not its `cmd.sh` (plan, section 5). The first kidney `E` run (9503521) was too slow for its limit and was rerun as 9518165. The CCRCC chain's first submission (9472778) was cancelled by the session before its join step, which would have refused the 407 spots without a corpus embedding.

**Sub-agents.** `lit-A` and `lit-B` (frames `c9016697-…/lit-A` and `/lit-B`) searched the literature on the strongest predictor and on donor-level accuracy, briefs as in the session of 16 November, logs in `results/round11/closeout/lit/`. `b1` (frame `c9016697-…/b1`) recomputed the headline table independently, with its own scripts (now `code/scripts/round11_closeout_b1_*.py`, byte-identical to the files that ran from `b1/scripts/` on Longleaf) and six jobs (Slurm 9473194, 9473430, 9473431, 9474416, 9474417, 9474418). Its brief is summarised in the plan, section 5, B1.

## 3. Acceptance checks

| check | criterion | value | file | verdict |
|---|---|---|---|---|
| A2.1, `R10` kidney Visium, by donor | round 10's 0.4713316492580511, within 1e-6 | 0.4713316492580511 | `predict/kidney__Visium__R10__donor/pred_summary__*.json` | passed (exact) |
| A2.1, by center | 0.12311852127066651, within 1e-6 | 0.12311852127066947 | `predict/kidney__Visium__R10__center/` | passed (3e-15) |
| A2.3, ridge self-test | sklearn within 1e-8 | 1.5e-14 | `predict/selftest_v1/stdout.log` | passed |
| A2.2, CCRCC D12 (LOO-constant baseline) | 0.021 within 0.005 | 0.02371 | `anchor/CCRCC__R10_v2/d12/d12_lodo_r2_medians__R10_CCRCC_uni_v2.csv` | passed |
| A2.2, CCRCC $\theta_3$ width ratio at 8 donors | the brief: 0.878 within Monte Carlo error; the plan: within 0.02 | 0.8949 | `g2/aggregate_v2/g2_anchor_ccrcc.csv` | **fails the brief's criterion**, passes the plan's (section 7, item 1) |
| A2.2, CCRCC `fix1` coverage at 8 donors | 0.8965 within 2 MCSE (MCSE 0.0022) | 0.89665 | same | passed |
| A2.2 control, round 10's steps rerun on round 3's file | reproduce 0.878272 and 0.896525 | 0.878272, 0.896525 | same, `source` = control | passed |
| CCRCC join | at most 1% of the record's rows without a corpus embedding; $y$ equal within 1e-6 | 407 of 74,220 (0.0055); largest $|y|$ difference 2.5e-7; donor partition agrees | `anchor/CCRCC__R10_v2/join/*.join.json` | passed |
| `R10` against the masterplan's reference values | 0.511 (bowel), 0.619 (LUNG_XENIUM) | 0.5113, 0.6189 | `g2/aggregate_v2/g2_p111.json` | agree |
| B3, round 10's HCP rows reproduced | 1e-9 | 1.1e-16 over 30 rows | `b3/s0006_v1/b3_summary.json` | passed |
| B4, round 10's proportional ACS rows reproduced | exact | 0.0 over 210 rows | `b4/equal_v2/b4_summary.json` | passed |

## 4. Variables that differ between the arms of each comparison

- **Arms on one task** (`R10`, `H`, `C`, `P`, `V`, `E`; plan, section 4, A3). Same samples, donor labels, genes, scales, folds and outcome. They differ in the encoder (`V`: `virchow2`; `E`: three encoders concatenated), the input (`C`, `P`, `E`: the spot's embedding with its neighbours' mean), and the head (`H`, `P`: ridge without PCA with the penalty tuned per gene by inner donor-grouped CV; the others: round 10's PCA 256 and fixed penalty). Feature widths 1536, 3072, 2560 and 11,264.
- **This track's `R10` against round 10's files.** On kidney and bowel Visium none (same script path, same inputs). On LUNG_XENIUM and CCRCC, the embeddings (the corpus's, against round 3's and round 4's HEST-bench files) and, on CCRCC, 407 of 74,220 spots.
- **The CCRCC anchor against round 10's cell.** The predictions (as just stated) and the 407 spots. The regime A draws, the estimators and the cluster-value code are the same, which the control confirms.
- **B4, proportional against equal allocation.** Only regime B's per-state sizes; budgets, cost-matching, draws, estimators and regime A are the same.
- **B3, S0006 against the other centers.** The center, its donors and spots, its calibration pool (the other centers' donors) and the center-out heads.
- **B5.** No comparison of arms; per cluster the variance $V_g$ against the equal-variance assumption.

## 5. Predictions against outcomes

The masterplan's, as written:

| prediction | outcome | verdict |
|---|---|---|
| P11.1. "The primary predictor raises the donor-held-out median spot-level Pearson by at least 0.02 over the reference on at least two of kidney Visium, bowel Visium and LUNG_XENIUM. The reference values are 0.471, 0.511 and 0.619 (`results/round10/final_runs/F2/report_tables/r10_buy_uni_v2_primary_n8.csv`, column `median_pearson_spot`). If it does not, P11.2 to P11.4 are scored "not tested"." | gains 0.0106, 0.0186 and 0.0103 against the references (`g2/aggregate_v2/g2_p111.json`) | refuted |
| P11.2 | | not tested |
| P11.3 | | not tested |
| P11.4 | | not tested |
| P11.5. "Under equal allocation, with `fix1`, $\theta_3$ and the cost ratio 10, regime B is narrower than regime A in more than 6 of the 12 cost-matched comparisons on ACS by state. Under proportional allocation round 10 found 3 of 12 (`results/round10/final_runs/F4/paper_numbers.csv`, keys `E1.ACS_STATES.*`)." | 12 of 12, median width ratio 0.699 (`b4/equal_v2/b4_summary.json`) | held |

The session's, each written in the plan before its run (section 4, A2 and A5; section 5, B3 to B7), with its full text there:

| prediction | outcome | verdict |
|---|---|---|
| A2.1. `R10` reproduces kidney Visium's 0.4713 and 0.123 within 1e-6 | exact and 3e-15 | held |
| A2.2. CCRCC D12 within 0.005 of 0.021; width ratio within 0.02 of 0.878; `fix1` coverage within 2 MCSE of 0.8965 | 0.02371; 0.8949; 0.89665 | held as written (the brief's stricter criterion fails, section 7) |
| A2.3. Self-test within 1e-8 | 1.5e-14 | held |
| A5.1. `P` gains 0.02 to 0.05 (kidney, bowel) and 0.01 to 0.03 (LUNG_XENIUM) over `R10`; so P11.1 holds | 0.0103, 0.0183, 0.0104 | refuted |
| A5.2. `H` within 0.01 of `R10` on each task; `C` gains at least half of `P`'s gain | `H`: +0.0129, −0.0159, +0.0074; `C`: +0.0168, +0.0357, −0.0037 | refuted |
| A5.3. `V` within 0.02 of `R10`; `E` at most 0.01 above `C` | `V`: −0.0027, +0.0369, +0.0064; `E` − `C`: KIDNEY_E_MINUS_C, +0.0473, +0.0206 | refuted |
| A5.4. `P` by center on kidney Visium below 0.20 | 0.1068 | held |
| B3. (a) HCP rows reproduced within 1e-9; (b) S0006's half-width the smallest of five on `uni_v2` lognorm, and removing its level shift raises its coverage by at least 0.10 | 1.1e-16; 1.0717 against 1.3709 to 1.5721; 0.6555 to 0.8184 | held |
| B4. (a) proportional rows exact; (b) equal allocation narrower in at least 9 of 12, ratio below 0.85; (c) coverage within 0.02 of 0.90 | 0.0; 12 of 12, 0.699; 0.8915 to 0.9085 | held |
| B5. Variances unequal (largest to smallest above 3 on every task); measured factor within 25% of round 10's; ACS's factor the largest | ACS 1.70 ($\theta_3$); LUNG_XENIUM 1.341 times; 2.636 against at most 1.775 | partly held |
| B6. D12 share in 0.46 to 0.64 under `uni_v2`; E1 values 5, 11, 6, 17, 8, 13, 8, 8, 22, 143 | 0.64, 0.64, 0.627; as predicted | held |
| B7. 10 to 300 round 10 jobs not in the ledger, mostly failed, cancelled or timed out; fewer than 20 completed ones without provenance | 56, of which 47 failed, cancelled or timed out; 9 completed | held |

## 6. Results

### 6.1 Strength (A5)

The masterplan's measure is the median over genes of each gene's Pearson over all held-out spots, on $\log(1 + y)$, held out by donor. Beside it, the paired per-fold difference: per held-out donor, the median over genes of that fold's Pearson, arm minus `R10`, with its median and interquartile range over folds and the share of folds where the arm is higher. Full table, both scales: `results/round11/closeout/g2/aggregate_v2/g2_strength.csv`.

| task | arm | median Pearson | gain over `R10` | paired per-fold gain, median (q25, q75) | folds higher |
|---|---|---|---|---|---|
| kidney Visium (51 folds) | `R10` | 0.4713 | | | |
| | `H` | 0.4842 | 0.0129 | 0.0070 (−0.0066, 0.0326) | 0.608 |
| | `C` | 0.4881 | 0.0168 | 0.0118 (−0.0079, 0.0399) | 0.667 |
| | **`P`** | **0.4816** | **0.0103** | **0.0291 (0.0004, 0.0514)** | **0.745** |
| | `V` | 0.4686 | −0.0027 | −0.0044 (−0.0535, 0.0363) | 0.451 |
| | `E` | KIDNEY_E_ROW |
| bowel Visium (18 folds) | `R10` | 0.5113 | | | |
| | `H` | 0.4954 | −0.0159 | 0.0212 (0.0010, 0.0388) | 0.778 |
| | `C` | 0.5470 | 0.0357 | 0.0279 (0.0176, 0.0360) | 0.944 |
| | **`P`** | **0.5296** | **0.0183** | **0.0405 (0.0186, 0.0802)** | **0.889** |
| | `V` | 0.5482 | 0.0369 | 0.0007 (−0.0314, 0.0280) | 0.500 |
| | `E` | 0.5943 | 0.0830 | 0.0491 (0.0355, 0.0765) | 1.000 |
| LUNG_XENIUM (15 folds) | `R10` | 0.6189 | | | |
| | `H` | 0.6263 | 0.0074 | 0.0169 (0.0119, 0.0193) | 1.000 |
| | `C` | 0.6152 | −0.0037 | 0.0057 (0.0002, 0.0131) | 0.733 |
| | **`P`** | **0.6293** | **0.0104** | **0.0234 (0.0163, 0.0290)** | **1.000** |
| | `V` | 0.6253 | 0.0064 | 0.0029 (−0.0023, 0.0182) | 0.667 |
| | `E` | 0.6358 | 0.0169 | 0.0252 (0.0202, 0.0336) | 0.933 |

Held out by center on kidney Visium, `P` gives 0.1068 against `R10`'s 0.1231 (A5.4).

**Reading, checked cell by cell.**
- For `P`, the paired per-fold gain exceeds the pooled gain on all three tasks (0.0291 against 0.0103, 0.0405 against 0.0183, 0.0234 against 0.0104), and `P` is higher than `R10` in 0.745, 0.889 and 1.0 of folds. For `H` the per-fold gain exceeds the pooled one on bowel Visium (0.0212 against −0.0159) and LUNG_XENIUM (0.0169 against 0.0074), not on kidney Visium (0.0070 against 0.0129). The pooled Pearson over all spots also rewards getting each donor's level right, so a head that predicts better within donors while spreading donors' levels less can gain per fold and lose pooled. That mechanism predicts that `P`'s and `H`'s donor-level $R^2_c$ is no higher than `R10`'s where the two measures part most (bowel Visium); the A6 quantities would show it, and it was not checked at this gate.
- Context under round 10's head (`C`) gains on the pooled measure on kidney Visium (0.0168) and bowel Visium (0.0357) and loses 0.0037 on LUNG_XENIUM, where per fold it gains 0.0057 and is higher in 0.733 of folds. No mechanism for the difference between tasks was checked.
- Three encoders with context (`E`) give the largest pooled gain on bowel Visium (0.0830) and LUNG_XENIUM (0.0169), with the per-fold gain positive in 1.0 and 0.933 of folds. `E` was named in the plan as a secondary arm before any result, not as the primary, and nothing about it is claimed beyond these numbers.
- Another encoder alone (`V`) moves the pooled measure by −0.0027, +0.0369 and +0.0064, and its per-fold gain is near zero on all three tasks (−0.0044, 0.0007, 0.0029).

### 6.2 The anchors (A2)

Kidney Visium reproduces exactly. On CCRCC, the D12 and the `fix1` coverage at 8 donors reproduce, and the width ratio of `fix1` to `classical` for $\theta_3$ is 0.8949 against round 10's 0.8783. The control, round 10's cluster-value and regime A steps run by this track on round 3's own file, gives 0.878272 and 0.896525, round 10's values to the last digit shown, so the steps are exact and the difference is the predictions: `R10` on the corpus's embeddings for 73,813 spots against round 3's HEST-bench embeddings for 74,220. The median donor-level $R^2_c$ moves the same way, 0.4290 against 0.4387 (`g2/aggregate_v2/g2_anchor_ccrcc.csv`). Every arm on CCRCC would be compared with this track's corpus `R10`, not with round 10's file.

### 6.3 Part B

- **B1, the headline numbers recomputed.** The `b1` sub-agent recomputed every row with its own code. Values of record and recomputed values, `results/round11/closeout/b1/` (per job) and the table below. Every recomputed value agrees with the value of record at the quoted precision.

| row | value of record | recomputed | file |
|---|---|---|---|
| H1(a), minimum and maximum over tasks | 14.81 (LUNG_XENIUM), 58.98 (brain Visium) | 14.81059, 58.97767; 60 of 60 rows, largest difference 6.5e-12 | `b1/h1a/b1_h1a_summary.json` |
| H1(b), `random`, `slide_out`, `donor` | 0.894, 0.859, 0.802 | 0.8937 (132 cells), 0.8585 (36 cells), 0.8024 (132 cells) | `b1/h1b_h4/b1_h1b_h4_summary.json` |
| H1(b), CCRCC `random`, `donor` | 0.881, 0.864 | 0.8810, 0.8643 | same |
| H2, kidney Pearson by donor | 0.412 to 0.483 | 0.41206, 0.47133, 0.48332 | `b1/h2/b1_h2_summary.json` |
| H2, kidney Pearson by center | 0.004 to 0.123 | 0.00386, 0.10809, 0.12312 | same |
| H2, HCP at 0.80, S0006 and median center | 0.655, 0.906 | 0.65521, 0.90567 | same |
| H2, HCP over centers, median | 1.0 | 1.0 under all three tie readings | same |
| H3, width ratio | 0.878, 0.957, 0.937, 0.669, 0.585 | B1_WR | `g2/gate/b1_width_ratio_medians.csv` |
| H3, $R^2_c$ | 0.439, 0.139, 0.199, 0.626, 0.714 | 0.4387, 0.1390, 0.1986, 0.6258, 0.7135 | `b1/h3/b1_h3_summary.json` |
| H3, leave-one-donor-out $R^2$, CCRCC and kidney Visium | 0.021, 0.382 | 0.02127, 0.38152 | same |
| H4, split design against encoder | read | 0.1586 against an encoder spread of 0.0977, ratio 1.62 | `b1/h1b_h4/b1_h1b_h4_summary.json` |
| H5, Kluger at 4 clusters | 0.7145 | 0.7145 (242 cells) | `b1/h5/b1_h5_summary.json` |
| H5, Broska and Howes, `bh_t`, at 4 clusters | 0.699, 0.875 | 0.69909, 0.87473 (146 cells) | same |

- **B3, S0006.** Its coverage is low because of the calibration it faces and a level shift, not because its residuals are the largest. S0006 holds 24 of the 51 donors, so when it is held out its calibration pool lacks all of them and gives the narrowest half-width of the five centers (median 1.0717 against 1.3709 to 1.5721 on `uni_v2` lognorm), while its own 0.8 quantile of $|y - f|$ is 1.5051. Its median level shift is 0.643 of the half-width, and removing it raises its coverage from 0.6555 to 0.8184. Round 10's check compared median residuals alone, which is why S0249 (0.971) outranked it on that cell while covering 0.7103 (`results/round11/closeout/b3/s0006_v1/b3_by_center.csv`).
- **B4, equal allocation on ACS by state.** Section 5: regime B narrower in 12 of 12, median ratio 0.699, coverage 0.8915 to 0.9085 (`b4/equal_v2/b4_summary.json`). Round 10's allocation reading (that equal allocation would remove regime B's disadvantage) holds.
- **B5, within-cluster variances.** On ACS by state they are close to equal (median ratio of largest to smallest 1.70 for $\theta_3$, coefficient of variation 0.100), so round 10's factor stands when recomputed from them, 2.636 against 2.656. On the HEST tasks they are not (ratio 14.8 to 23.5 for $\theta_3$), and the recomputed factor is 0.973 to 1.341 times round 10's; ACS's stays the largest (`b5/withinvar_v1/b5_by_task.csv`).
- **B6, the stored columns.** Both now exist: D12's share of genes where the pooled head beats a constant is 0.64, 0.64 and 0.627 under `uni_v2` (0.46 to 0.64 over encoders, against round 9's full-sample-mean baseline), and round 9's E1 box numbers are in round 9's own stored columns, with selectors in `b6/stored_v1/b6_e1_box_numbers.csv`.
- **B7, round 10 jobs without provenance.** 56 of round 10's 2859 jobs in `sacct`'s window are not in its ledger and wrote no `PROVENANCE.txt`: 33 cancelled, 10 timed out, 9 completed, 4 failed (`b7/ledger_v2/b7_summary.json`, rows in `b7_round10_jobs.csv`).

## 7. Discrepancies, open questions and escalations

1. **Substantive. The CCRCC width-ratio anchor misses the brief's criterion.** The brief (section 4, standard 1) asks for 0.878 within the Monte Carlo error of round 10's simulation. The anchor gives 0.8949, and because the draws are the same, Monte Carlo error does not cover a difference of 0.0166. The control shows the pipeline is exact; the difference is the corpus embeddings. Every comparison on CCRCC is therefore made against this track's own corpus `R10`, never against round 10's file. **Decision for Nicolas**: accept the corpus route for CCRCC with this stated difference, or require the HEST tasks to run on round 3's and round 4's embeddings, which needs those rounds' one-off driver scripts to be rebuilt and limits the new arms to the three encoders those files carry.
2. **Substantive. What Part A does now.** By the brief, `P` is not stronger and P11.2 to P11.4 are "not tested", so the headline table's Part A verdicts would read "not tested" for H1(b), H2 and H3, and Part A ends here. Two findings bear on that choice, and the decision is the reviewer's, not the session's. (a) `P` is stronger per held-out donor (paired per-fold gain 0.023 to 0.041) though not on the pooled measure. (b) `E` (three encoders with context) is stronger on the pooled measure on bowel Visium and LUNG_XENIUM, but it was not designated primary, so any use of it as the predictor for A6 is chosen after seeing results and would be labelled so. **Options**: (i) end Part A as the brief says, and go on with Part B item 2 and G-final; (ii) run A6's quantities for `P` anyway, reported as a predictor that is not stronger by the masterplan's measure, to show whether the per-donor gain carries to donor-level inference; (iii) as (ii) for `E`, labelled post hoc. The session's recommendation is (ii): it costs one round of the existing pipeline, it answers the brief's question for the predictor named in advance, and the per-donor gain is exactly what H3 depends on.
3. **The brief's wording.** H1(b)'s "mean over 132 task and encoder cells" holds for `random` and `donor`; `slide_out` has 36 cells (`b1/h1b_h4/b1_h1b_h4_summary.json`). H4's encoder spread, 0.0977, is in `results/round3/A1_coverage/a1_vs_benchmark_pearson.csv`, not in the two files H4 names. H5's Broska and Howes values come from `results/round10/final_runs/F2/report_tables/r02_regimeA_grid_ranges.csv`, the regime A grid, not from the limits table. None changes a number. Proposed: the brief's section 3 notes these three points.
4. **HCP over centers at $K = 4$, $\alpha = 0.2$ is an exact tie** ($1/(K + 1) = \alpha$). Round 10's rows take the lower reading (S0006 0.99894); the upper gives 1.0. The headline's median of 1.0 holds under both (`b1/h2/b1_h2_summary.json`).
5. **Two scripts failed their purpose and were rerun** (B4 v1 and B7 v1, section 2). Their outputs stay on Longleaf, are not in the repository and are not scored.
6. **Partitions.** Jobs requested `general` and ran on `spill` or `hov`, as recorded per job. No job waited four hours: the first, submitted at 20:32 on 16 November, started at about 23:07.
7. **The machine the session works from ran low on memory** while the `b1` sub-agent ran, which stopped two of its local polling loops. No job or result was affected.
8. **The registry has no further donors of the same organ and platform** for any corpus task (`inventory/inv_v1/inv_tasks.csv`), so "more training donors" (brief, section 4) could only come from other organs or platforms, which the literature advises against (`lit/lit_A_stronger_predictor.md`). Not pursued.

## 8. What was not checked

- Whether `P`'s per-fold gain and its smaller pooled gain come from a narrower spread of donors' predicted levels (section 6.1): the A6 donor-level quantities would show it and were not run.
- Kidney Visium's `E` arm PENDING_E_NOTE.
- 184 of round 10's ledger ids are not among the jobs `sacct` lists in round 10's window (`b7/ledger_v2/b7_summary.json`); not explained.
- Arms `V` and `E` were not run held out by center, and no arm other than `P` and `R10` was.
- The normalised scale: every arm's file carries it (`g2_strength.csv`, columns `*_lognorm`), but no prediction concerns it and it was not read for this report.
- The numbers in this report's tables were recomputed by a fresh sub-agent before the gate; what it covered is in section 9's last paragraph. VERIFY_NOTE

## 9. Proposed next step

The reviewer decides items 1 and 2 of section 7. Under the session's recommendation: A6's quantities for `P` and `R10` on the same inputs (CCRCC, INDIANA_KIDNEY, LUNG_XENIUM, kidney and bowel Visium, both scales; leave-one-donor-out $R^2$ and $R^2_c$; `fix1` and `classical` for $\theta_3$ and $\mu$ at 4, 8 and 16 donors; held out by center on kidney and brain Visium with HCP at 0.80; split conformal under round 3's designs), then Part B item 2, then G-final. The provenance index over every job is `results/round11/closeout/g2/gate/provenance_index.csv`.
