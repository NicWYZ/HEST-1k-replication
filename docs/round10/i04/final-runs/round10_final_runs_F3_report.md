# Round 10, track `final-runs`, gate F3 report

*Written on 14 November 2026 by the seventh session of track `final-runs` (frame `b66915a6-d96c-42d1-b0b7-edb7f5bf423f`), from the track plan `docs/round10/tracks/final-runs/round10_final_runs_plan.md` (section 5d) and the F2 decision file `docs/round10/i04/final-runs/round10_final_runs_F2_decisions.md`. The F3 methods, anchors and the first production waves were run by the sixth session (frame `7744bd42-579b-40da-aa6c-80d67b9dbbdc`) and its sub-agents. Every number below is read from the file named beside it. Paths that begin `aggregate/`, `map/`, `institution/`, `regimeB/`, `allocation/`, `balance/`, `takeall/`, `e8/`, `reruns/` or `toy/` are relative to `results/round10/final_runs/F3/`. The tables of `aggregate/` are written by `code/scripts/round10_final_runs_f3_aggregate.py`, which selects and summarises the committed per-item outputs and re-estimates nothing. Bulk outputs stay on Longleaf under `/work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F3/`.*

## 1. Stage and status

Stage F3 (prediction sets and designs) is complete. Every item of plan section 5d has an output on every task, encoder, scale and estimand it names, every unit's `PROVENANCE.txt` reads `COMPLETED` or is a failed attempt kept and superseded (section 3), and no job of the track is running. Of the predictions scored at F3, R10-F3a, FR7, FR8 clause 2, P10.3 part 1, open points 3, 5 and 7 hold, P10.3 part 2 and FR8 clause 1 are refuted, P10.1 part 2 is refuted at $p_a = 0.1$ and holds at $p_a = 0.01$, open point 4 partly holds, and open point 2, which its item output does not score, is refuted under the plan's rule (section 5). One finding limits what the regime A against regime B comparison can say about $\mu$ (section 7, item 1). The gate asks Nicolas to review the scores, the $\mu$ finding and the escalations of section 7, and to decide V (section 6.5), before F4.

## 2. What was run

All jobs ran on Longleaf through the submission route and are identified by Slurm id. Each F3 job that wrote a `PROVENANCE.txt` is a row of `results/round10/final_runs/job_ledger.csv` (stage `F3`) with its account, partition, node, submit, start and end times, state, wall time, requested memory, peak memory and commit, read from `sacct` by `code/scripts/round10_final_runs_ledger_rows.py` (unit `F3_ledger/ledger_v1`, Slurm `9149435`). Jobs that wrote no `PROVENANCE.txt` are not in it: the ten regcomp runs that hit their time limit, and the harness backstop's cancellations of jobs that had not started; the per-track CSVs on Longleaf list them (`F3/map/map_production_jobs.csv`, `F3/regimeB/f3_slurm_ids.csv`, `F3/designs/f3_designs_production_jobs.csv`, `F3/reruns/production_jobs.csv`).

Work by item, with the commits the jobs ran from (each job ran from a read-only snapshot of its commit's `code/`):

- Map (5d.1): the grid from `a0c34de5` and the split units from `0ff3345c`; item 7 from `cfa69897`, after the check `item7_check` (Slurm `9039656`) and `item7_anchor_rerun` (Slurm `9060384`); the map aggregate from `cfa69897` (Slurm `9086594`) and the item 7 summary from `93d4be97` (Slurm `9091533`).
- Institution (5d.2) and the toy (5d.6 item 2): committed at the sixth session (`cdc659f7`, `1de5376e`).
- Regime B, regcomp and box (5d.3 i and ii, 5d.4 item 2, open point 5): from `134508da` and `e063d110`, aggregate from `5c81baae` (Slurm `9135882`); the $\mu$ check from `a7ad790e` (Slurm `9148713`).
- Allocation, balance and take-all (5d.3 iii to v): from `dd1ba88b`, `137f28af` and `a5641c23`; the balance aggregate from `3c1de525` (Slurm `9097032`).
- E8 (5d.4 items 3 to 5): the anchor from `07016c8c`, the join from `9450861b` (Slurm `9120588`).
- Open points 1, 3, 4, 6 and 7: from `67358092` and `eb1cbb81` (aggregate Slurm `9066838`) and the sixth session's commits.
- The F3 aggregate: from `0d4946b8` (Slurm `9149619`).

Sub-agents of this session, each given a written brief with its frame id: Map `09de02c2`, Regime B `60dea19b`, Designs `94567b60`, Reruns `61745042` (resuming the sixth session's parked tracks from their `RESUME.md` files), E8 `4ca471b7` (built 5d.4, which had not been built), and F3 aggregate `2b764a2a`. The lead stopped Designs after it stalled on a local file read once its aggregate had completed, and finished its end steps (section 7, item 9). Sub-agents ran no git command; the lead made every commit after checking each hand-back against its files.

## 3. Acceptance checks and exit items

- **Item 7 code (5d.1 item 7).** `item7_check` found the default scores run and the merged gene-range parts byte-identical to their references (four `IDENTICAL` lines, `map/item7_check/check_compare.txt`). Its A4 step failed only on its output path (section 7, item 2). Run on that table, the committed comparator matched the 42 rows of round 3's table, with coverage difference 0 and width difference at most 1.4e-14 against a criterion of 1e-9 (`map/item7_check/item7_anchor_rerun/anchor_a4.json`).
- **Item 7 summary.** Over 162 shard files its fold means equal each shard's own `scores_by_fold` file to 1.8e-15, with no duplicate rows, and 24, 25 and 15 folds on CCRCC, INDIANA_KIDNEY and LUNG_XENIUM (`map/i7_aggregate/scores_checks.json`).
- **Reruns (open points 3 and 4).** The analytic rows equal F2's: 29640 rows, none unmatched, maximum absolute difference 0; all 126 bootstrap parts complete and pass their check; all 270 normalised-scale cells match regime A (`reruns/prod_aggregate/f3_prod_scores.json`).
- **Regime B.** All 806 regcomp units completed, with 2084280 gene rows and no duplicates (`regimeB/aggregate_v1/regcomp/f3_regcomp_checks.json`). The regime B and E8 units reproduce F2's rows with maximum absolute difference 0 (`regimeB/aggregate_v1/regimeB/f3_regB_checks.json`), and all 61 box units completed (`regimeB/aggregate_v1/box/f3_box_checks.json`). The cluster-value check holds for $\theta_2$, $\theta_3$ and ACS and fails for $\mu$ elsewhere (section 7, item 1).
- **Balance.** The aggregate was run three times (section 7, item 4). The final run's matched-designs, P10.1 and cells tables are byte-identical to the second run's, and its limits table is no longer empty. Exactly the twelve LUNG_XENIUM $\theta_2$ units at $n_L$ 8 and 12 contribute no rows, because every cell has $n_L > G - 2$ with $G = 9$ (`balance/aggregate/f3_balance_units.csv`).
- **E8 anchor.** `round5_ppi_e5_joint.py`, run unchanged, reproduces round 5's joint table: 354 of 354 rows, every numeric column within 4.4e-16, text columns equal, and the check row CCRCC `uni_v2` $\theta_3$ $m = 10$ width ratio 0.9920276526390102 (`e8/anchor_e5.json`). The first run failed only an exact-zero criterion (section 7, item 5).
- **E8 join.** The production run is byte-identical to its overlay test. It wrote 2094 rows, of which 774 are off the map's $o$ grid and marked, and 1320 are on it. No on-grid row lacks a valid set, and 208 lack a set that needs no further labels and is finite in every row (`aggregate/t30_e8_row_counts.csv`). At CCRCC `uni_v2` log1p part 1, $K = 10$, $o = 10$, the narrowest valid set equals the map aggregate's (`e8/e8_checks.json`).
- **F3 aggregate.** Every item verdict is copied into `aggregate/f3_predictions.csv`, and where an item's table and rule allow it the verdict is re-derived beside it; no re-derived verdict disagrees. The manifest records the md5 of every input (`aggregate/f3_aggregate_manifest.json`).
- **Provenance and claims.** The provenance index over F1 to F3 and the numeric-claim sweep over this report run in the gate job (section 8).

## 4. Variables that differ between the arms of each comparison

- **P10.3** compares `hcp` with `within_full` (part 1) and `within_full` with `within_plain` (part 2) on the same folds, calibration draws and label draws, at $\alpha = 0.1$, $K = 10$, `uni_v2` and $\log(1 + y)$. Only the conformal method differs.
- **Item 7 margins** compare each adaptive score with the absolute-residual score inside one method and $o$, on the same folds and draws, with the same bootstrap resample. The score differs, and so does the share of sets that are finite, which is reported beside each margin.
- **R10-F3a** compares regime A (labelled clusters, all units) with regime B (all clusters, $m$ units each) at matched cost, cost ratio 10. Design, number of labelled clusters, units per cluster and the variance estimator (fixed-coefficient form in both) differ; data, genes and predictions are the same.
- **FR7** compares regime B coverage across $m$, and the bounded with the unbounded box allocation. Only $m$ or the allocation rule differs.
- **FR8** compares HCP over centers with donor-level HCP pooled, both on F1's center-out residuals. The exchangeability unit differs.
- **P10.1 part 2** compares round 10's design ranking with round 7's on round 7's 18 tissue cells. The estimator code, the prediction files, the cluster values and the number of draws differ between rounds; the designs compared are the three both rounds share.
- **E8** compares the narrowest set needing no further labels with the narrowest valid set overall, on the same folds and draws. The method family differs, and the overall set may need labelled calibration donors.
- **Open points 3, 4 and 5** compare F3 reruns with F2. The encoder (3), the scale (4 and 5) differ; code and seeds are the same.

## 5. Predictions against outcomes

From `aggregate/f3_predictions.csv`.

| prediction | verdict | deciding numbers |
|---|---|---|
| P10.1 part 2, $p_a = 0.1$, classical and fixed coefficient | refuted | D2_rej_t and cube_S4b change order: round 7 0.8933 and 0.8827, round 10 0.9043 and 0.9413 (classical) |
| P10.1 part 2, $p_a = 0.01$, classical and fixed coefficient | held | the same pair is tied in round 7 |
| P10.3 part 1, CCRCC | held | hcp minus within_full at least 1.729 (SE 0.056) at all nine $o$ |
| P10.3 part 1, LUNG_XENIUM | held | at least 1.562 (SE 0.022) at all nine $o$ |
| P10.3 part 2, INDIANA_KIDNEY | refuted | within_full over within_plain 1.049 to 1.072 against 1.02, SE 0.0078 at the smallest |
| FR7 clause 1 | held | 30 of 30 cells within 0.03 of 0.90, largest deviation 0.0205 |
| FR7 clause 2 | held | 11 of 11 tasks |
| FR8 clause 1 | refuted | hcp_donor median over centers 0.9057, threshold below 0.75 |
| FR8 clause 2 | held | hcp_center 1.0, threshold at least 0.8 |
| R10-F3a | held | 141 of 156 comparisons with regime B narrower, share 0.904 (round 5's C_ppi 210 of 232) |
| Open point 2 | refuted (not scored by its item) | at $m/M_0 \ge 0.4$ the largest V ratio is 0.959 against below 0.85; at $m/M_0 = 0.5$ it rises with $M_0$, 0.7787 at $M_0 = 10$ to 0.8904 at $M_0 = 20$ ($G_s = 1$) |
| Open point 3 | held | share within 0.02 of `uni_v2`: 0.998, 0.959, 0.998 |
| Open point 4 | partly held | ranking identical at $n = 4$ with Kluger lowest; at $n = 8$ Kendall's tau 0.905 |
| Open point 5 | held | 108 of 108 cells, E(V)/Var 0.985 to 1.011, coverage 0.894 to 0.9025 |
| Open point 7 | held | 26 of 1722 cells show a genuine rise, share 0.0151, against below 0.1 |
| Open points 1 and 6 | descriptive | see section 6.6 |

## 6. Results

### 6.1 The prediction-set map and P10.3 (5d.1)

`within_full` is narrower than `hcp` by at least 1.729 on CCRCC and 1.562 on LUNG_XENIUM at every $o$ from 9 to 100, each more than twenty standard errors from zero (`aggregate/t01_map_p103.csv`). On INDIANA_KIDNEY the ratio of `within_full` to `within_plain` is 1.049 to 1.072 at the four $o$ part 2 names, against a threshold of 1.02, so part 2 is refuted at each of them. The by-task table over every task, encoder, scale, part, $K$ and $o$ is `aggregate/t02_map_by_task_p103_methods_alpha01.csv`, and ACS by state is `aggregate/t04_map_acs_o_sweep_summary.csv`.

### 6.2 The adaptive scores (5d.1 item 7)

Margins are each score's median width minus the absolute score's, with the bootstrap standard error of item 8 (`map/i7_aggregate/scores_margins.csv`). At $o = 9$ under `within_plain`, `scaled_clip` is wider than the absolute score by a ratio of 1.012 (SE 0.008) on CCRCC, 1.049 (SE 0.014) on INDIANA_KIDNEY and 1.069 (SE 0.012) on LUNG_XENIUM, and CQR's ratio is 1.005 on CCRCC, 0.999 on INDIANA_KIDNEY and 1.071 on LUNG_XENIUM. The conformalised negative binomial set is narrower, ratio 0.762 on CCRCC, but its sets are not all finite: the share of rows with every set finite is 0.762 there and 0.019 on LUNG_XENIUM, and at `hcp` $o = 0$ it is 0.125 and 0 (same file). Its widths are medians over finite sets only and are not comparable with the others where that share is below one. The model interval `nb` carries no conformal guarantee and is marked so in `map/i7_aggregate/scores_by_task.csv`.

### 6.3 The institution axis and FR8 (5d.2)

Donor-level HCP pooled over kidney Visium centers covers 0.9057 at the median over its five centers, with S0006 lowest at 0.655, so clause 1, which predicted coverage below 0.75, is refuted. HCP over centers covers 1.0 at the median, so clause 2 holds (`institution/production/inst_fr8.csv`). As decided at plan time, coverage is reported as empirical with no finite-sample guarantee claimed. The second clause's value sits on the case where $\alpha$ equals one over the number of exchangeable units, and the corpus predictions with the center held out are weak on this task.

### 6.4 Designs (5d.3)

**(i) Regime A against regime B.** Under the fixed coefficient, $\theta_3$, cost ratio 10, regime B is narrower in 141 of 156 comparisons, share 0.904, median width ratio 0.473 (`regimeB/aggregate_v1/regcomp/f3_regcomp_checks.json`). By task it is narrower in 36 of 36 on CCRCC, 33 of 36 on INDIANA_KIDNEY and LUNG_XENIUM, and only 3 of 12 on ACS by state, where the median ratio is 1.159 (same file). On the normalised scale it is narrower in 134 of 144. The $\mu$ rows on the HEST and corpus tasks are excluded (section 7, item 1); the remaining summaries are `aggregate/t11_regcomp_r10f3a_primary.csv` to `aggregate/t14_regcomp_beside_mu_excluded.csv`.

**(ii) The box and FR7.** Regime B coverage at $m \ge 6$ stays within 0.0205 of 0.90 across 30 cells, from 0.8795 to 0.9115, and clause 2, as defined in plan section 5d.3 (ii), holds on 11 of 11 tasks (`regimeB/aggregate_v1/box/f3_box_checks.json`).

**(iii) Allocation.** The allocation's cluster values and variance components reproduce F2's and round 5's to numerical precision; on CCRCC $\theta_3$, for example, the relative differences are 2.0e-13 and 2.2e-16 (`allocation/aggregate/f3_allocation_checks.csv`). Round 10's fitted ratio of the prediction-powered to the classical optimal $m$ is beside round 5's in `allocation/aggregate/f3_allocation_vs_r5.csv`; on CCRCC `hoptimus0` $\theta_3$ at $n_L = 4$ it is 1.084 against round 5's 0.987.

**(iv) Balance and P10.1 part 2.** At $p_a = 0.1$ round 10 ranks cube_S4b above D2_rej_t by `wr_D0cl` (0.9413 against 0.9043, classical), where round 7 ranked them the other way (0.8827 against 0.8933), a gap of 0.0105 in round 7, just past the 0.01 tie margin. At $p_a = 0.01$ the pair is tied in round 7 and the prediction holds (`balance/aggregate/f3_p101_part2.csv`). The limit arms at $n_L = 4$ form no interval, because the two-covariate adjustment leaves no degrees of freedom with four labelled clusters; they are marked in `aggregate/t23_balance_limits.csv`.

**(v) Take-all.** Round 10's take-all coverage and width ratios sit beside round 9's in `takeall/aggregate/f3_takeall_vs_r9.csv`; on CCRCC with $k = 1$ at $n_L = 8$, T0's coverage is 0.892 against round 9's 0.885 and its width ratio to D0 0.770 against 0.779.

### 6.5 V (5d.5)

`aggregate/t16b_V_side_by_side.csv` sets the bounded and unbounded box columns side by side for each task, encoder, scale and $\lambda$, with the median chosen $m$, the coverage at it, $G^\ast_B$ and the coverage at each $m$. On CCRCC `uni_v2` log1p with $\lambda = 0$, the bounded rule chooses a median $m$ of 10 and the unbounded 100, with coverage 0.9015 and 0.899; on ACS by state the bounded rule chooses 2 and the unbounded 75. The report makes no recommendation; Nicolas decides V at this gate.

### 6.6 E8, the joint design (5d.4)

Regime B's fixed-coefficient width over the classical width, at the map's $o = m$, is near one on CCRCC (1.015 at $m = 10$, `uni_v2` $\theta_3$ log1p), below one on INDIANA_KIDNEY (0.993) and kidney Visium (0.970), and well below on LUNG_XENIUM (0.733) and ACS by state (0.595) (`aggregate/t31_e8_on_grid_by_m.csv`). In each of these rows at $m = 10$ and 25, the narrowest valid set is one built from the target donor's own $o = m$ regime B labels, so it needs no further labels and the width difference is 0; at $m = 5$ no such set is finite in every row, and the overall narrowest set needs labelled calibration donors (same file). Over all on-grid rows, 208 have no finite set needing no further labels (`aggregate/t30_e8_row_counts.csv`). Each guarantee is marginal. Joint coverage of the interval and a set built from the same labels is not claimed, because Dobriban and Lin (arXiv:2303.00203) require multiplicity control for it.

### 6.7 The open points carried from F2 (5d.6)

1. Without the 54 cells with one unlabelled cluster, Kluger's cluster bootstrap at $n = 4$ keeps its median coverage 0.7145 (`aggregate/f3_predictions.csv`); the unfiltered run reproduced F2's tables byte for byte (`reruns/limits_g1/f3_limits_g1_summary.json`).
2. The toy's shortfall is not driven by the sampling fraction alone. At $m/M_0 \ge 0.4$ the V ratio reaches 0.959, and at a fraction of 0.5 it rises from 0.7787 at $M_0 = 10$ to 0.8904 at $M_0 = 20$, which points to the small within-cluster size the plan named as the alternative (`aggregate/f3_predictions.csv`; grid in `aggregate/t37_op2_toy_grid.csv`). The item output recorded only its anchor and no verdict, and the verdict here is the aggregate's re-derivation under the plan's stated rule.
3. The bootstrap arms under `hoptimus0` and `resnet50` stay within 0.02 of `uni_v2` in 0.998, 0.959 and 0.998 of cells (`reruns/prod_aggregate/f3_prod_scores.json`).
4. On the normalised scale the limits arms keep F2's ranking at $n = 4$ with Kluger lowest; at $n = 8$ two arms swap, on a coverage gap of 0.00025 (0.87375 against 0.8735, `reruns/prod_aggregate/f3_limits_norm_refit_ranking.csv`).
5. Regime B on the HEST normalised scale: E(V)/Var 0.985 to 1.011 and coverage 0.894 to 0.9025 across 108 cells (`regimeB/aggregate_v1/regimeB/f3_regB_checks.json`).
6. Every comparison with round 9 tabulated at both gene scopes reaches the same verdict at both, 10 of 10 (`aggregate/f3_predictions.csv`; `reruns/r9g42/f3_r9g42_scores_side_by_side.csv`).
7. 26 of 1722 cells show a genuine rise of coverage with $\kappa(e)$ (`aggregate/f3_predictions.csv`), so the reading that the shortfall tracks $\kappa(e)$ stands.

## 7. Discrepancies, open questions and escalations

1. **The regime B $\mu$ is a different estimand from the committed $\mu$.** The regcomp cluster-value check fails for $\mu$ on every HEST and HEST-1k corpus population, up to 0.269 relative, and passes for $\theta_2$, $\theta_3$ and ACS (`regimeB/aggregate_v1/regcomp/f3_regcomp_checks.json`). The regime B loaders keep only spots joined to nuclear morphology, so regime B's $\mu$ is the donor mean over those spots, while the committed cluster values average all of a donor's spots. A check on CCRCC `uni_v2` log1p found regime B's $\mu$ equal to the mean over the 67673 loaded spots, of 74220, with difference 0.0, and 0.133 from the committed value (`regimeB/regcomp_mu_check/mu_check.json`). The all-spot mean itself was not recomputed in that check. The regcomp $\mu$ rows of those tasks are excluded from every summary; R10-F3a ($\theta_3$) is unaffected. **Proposal:** rerun the regcomp $\mu$ units with regime B reading all spots for $\mu$, or define F3's $\mu$ comparison on joined spots in both regimes. This is Nicolas's decision.
2. **Item 7's check wrote outside its directory.** `round3_a4_scores.py` writes to `ROOT/<out-dir>`, so the absolute path given by `item7_check` put its tables under the project tree at `work/...`. The comparator ran on that table (section 3), and the directory was removed on Nicolas's instruction on 14 November.
3. **Two scripts were written in this session beyond the plan's list.** The map aggregate reads only the grid, so `round10_final_runs_f3_map_scores_aggregate.py` summarises item 7, and E8's join `round10_final_runs_f3_e8_joint.py` had not been built. Both were tested on overlays before their commits.
4. **Two faults in the balance aggregate.** An empty `balance_cells.csv` stopped the first run (fixed in `bb2abf50`), and the limits table came out empty because the two SRS baselines were not labelled for it (fixed in `3c1de525`).
5. **The E8 anchor's first run** failed an exact-zero criterion at one ulp in `pset_width`; it was rerun with a 1e-12 criterion. Its single `git show` call was served from a committed copy, md5-checked, because sub-agents run no git.
6. **Ten regcomp units ended at their time limit**, all LUNG_XENIUM packs. Each was moved to `F3/regimeB/_failed_attempts/` and completed on one resubmission with a 180-minute limit. The completed LUNG_XENIUM packs had used on average about a third of their limit, so the limits of the other units were not raised.
7. **Caps were raised** when tracks finished: Map from 30 to 45 and Regime B from 25 to 40.
8. **Regime B on ACS by state is wider** than regime A in 9 of 12 comparisons (median ratio 1.159), the reverse of the HEST tasks (section 6.4). Not examined further at F3.
9. **The Designs sub-agent was stopped** after it stalled on a local read; its track's `RESUME.md` was not finalised, and the lead ran and committed its last aggregate.
10. The sixth session's escalations stand as listed in the plan's state block of 13 November: the plan correction to 5d.3 (iii), the W3 anchor's relative criterion, the pcE2 limit arm, the regime B seed scheme, the regcomp re-split, the map split, the ACS unit split, the SSH outage, the backstop timeout change and the sub-agent rule slips.

## 8. What was not checked

- The all-spot donor mean of $\mu$ was not recomputed against the committed cluster values (section 7, item 1).
- The cases where regime B is wider on ACS (section 7, item 8) and the four-donor S0006 coverage in FR8 were not examined beyond their tables.
- The provenance index over F1 to F3 and the numeric-claim sweep run in the gate job that tags this report; their outputs are `results/round10/final_runs/F3/provenance_index.csv` and the job's log.
- The job ledger does not list jobs that wrote no `PROVENANCE.txt` (section 2).

## 9. Proposed next step

After Nicolas's review: record his answers in the i05 decision file, settle the $\mu$ question of section 7, item 1, and decide V. Then plan F4.
