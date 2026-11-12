# F3 inventory, item 3 (designs), item 5 (V) and prediction FR7

*Read-only source inventory for round 10, track final-runs, stage F3. Frame 94e92b9e-39ce-4829-aea9-3b57d8ff1a52, 11 November 2026. Everything below was read on Longleaf's login node from the clone `/work/users/w/e/weiyang/hest_code/round10-final-runs` (branch round10-final-runs, commit 71ed8070). Paths are relative to that clone unless they start with `/work`. Bulk paths start with `/work/users/w/e/weiyang/hest_replication/results/` (written `BULK/` below). Line counts are `wc -l`, md5 is `md5sum`. No job, no write and no git command was run. Values in anchor rows are copied from the files.*

## 0. Scripts read (path, lines, md5)

| script (code/scripts/) | lines | md5 |
|---|---|---|
| round5_ppi_e3_sim.py | 284 | 885918ff61abd753bffb14b49457d001 |
| round5_ppi_e3_twolevel.py | 547 | 80e52bfe1b2cf9e48c82f3828689d78f |
| round5_ppi_e3_merge.py | 269 | 5d7af79f2cb139b437a34686b688c901 |
| round5_ppi_twolevel.py | 323 | e13183a4ffdddf4f01ba5136844c606d |
| round5_ppi_e5_allocation.py | 59 | 3e45804f0eff3dc71a5eaf322e3adbc6 |
| round5_ppi_e4b_rejective.py | 380 | 059c18e1b4998b1ac9c9685ba324a872 |
| round5_ppi_balance.py | not counted (217 per ledger L1_S5) | d78b654d7fd8e6a824f73dd50ee2a0c1 |
| round7_ppi_d2.py | 257 | 31d5b0e396d85d3c49709f216d89d4af |
| round7_ppi_weighting.py | 344 | 19137aac514748f8aa6b054157067e29 |
| round7_ppi_s1_masking.py | 300 | 9e945ff59c4363a5121e16335e2d6dcb |
| round7_ppi_s3_cube.py | 564 | bdad8f019054140a1ce1a13e73b9bfde |
| round7_ppi_s4b_cube3.py | 345 | 67a99d8b7a48cb33d903d22681db0491 |
| round7_ppi_s3s4_numbers.py | 402 | 542139182263542c8ab57d2e671592bf |
| round7_ppi_s5_numbers.py | 255 | 0af7cd4c926e4a522185fa13b22adc92 |
| round9_fewcluster_box.py | 140 | eba7216fac3d8e938850e124705a9b99 |
| round9_fewcluster_strat_frontier.py | 247 | cfa00dcfe63dd18c7bbe522b53c94d75 |
| round9_fewcluster_regimeB_acs.py | 65 | 154492740268775f28cfe5aff8b10f1e |
| round9_fewcluster_takeall_kappa.py | 41 | d7d2982c64e05d397936d075c2f6d176 |
| round9_probe_takeall.py | 52 | c73df735db7c292d298d44f6c6f3d089 |
| round9_probe_feasibility.py | 73 | 2a172c3dd767f19ada01bcf43fa51e2a |
| round10_final_runs_estimators.py | 212 | 9580a38223ad46f5e141626572254fea |
| round10_final_runs_f2_regimeA.py | 214 | 774f14de3ed57d6eb110dec4128cec1c |
| round10_final_runs_f2_regimeB.py | 212 | 05f9c7a1a24a4bff1041ff5094dae011 |
| round10_final_runs_f2_regimeB_configs.py | 41 | 4446f762fa41cca632a61fe1d39cc58e |
| round10_final_runs_f2_regimeB_aggregate.py | 61 | a80a68637dea25ce6c385a98cf47c365 |
| round10_final_runs_f2_diagnostics.py | 211 | f0c32b1017ca8832f3e4b4c9b1807d15 |
| round4_ppi_q3_regimeB_sim.py | 191 | 02da231857f74978de92550b95cf62d2 |
| round5_ppi_e2_regimeB.py | 222 | b6e9ecc52ac5539682487d8e7c1451c6 |

The md5 of `round10_final_runs_f2_regimeB.py`, `round5_ppi_e3_twolevel.py` and `round5_ppi_twolevel.py` in the working tree equal the md5 that F2's regime B smoke job recorded (`results/round10/final_runs/F2/regimeB_smoke/PROVENANCE.txt`, `scripts_executed`), and `round10_final_runs_estimators.py` equals that file's 9580a382... entry.

## 1. F2's regime B, which F3 should reuse

**(a) Code.** `round10_final_runs_f2_regimeB.py` (212 lines). `run_cell` (lines 74 to 91) draws R samples of m units per valid cluster with round 5's `round5_ppi_e3_twolevel.units` and seeds `r5e3u|<vtag>|regb|B|Bnan|unit|nL<G>|m<m>|d<d>|<est>` (units) and `r5e3x|...` (cross-fit halves), through `tag_of` (lines 69 to 71). Every draw runs three forms on the same units, `FORMS` line 33: `C_fix1` (coefficient fixed at 1), `C_ppi` (round 5's cross-fitted, clipped within coefficient) and `C_classical`. They call `round10_final_runs_estimators.regime_b_formC` (lines 199 to 212), which for `fixed1` executes `round5_ppi_twolevel.estimate` with one inserted line (`_tl_fixed`, lines 181 to 197) that sets the within coefficient to 1 in every cluster. The regime B variance is round 5's `sum_g V_g / G^2` with `sum_g (m_g - 2)` degrees of freedom for theta3 and `sum_{g,h}(m_hg - 1)` over partly labelled strata for theta2 (`round5_ppi_twolevel.py`, `estimate`, between stage, `if regime_b:`). `gene_rows` (lines 94 to 113) writes coverage, its SE, widths, E(V)/Var and `frac_v_neg` per gene. `corpus_data` (lines 43 to 59) builds the corpus input from a corpus prediction file and the option (b) CellViT features. `check_cluster_values` (lines 116 to 131) compares the cluster means with F2's cluster values.

**Grid and outputs.** `round10_final_runs_f2_regimeB_configs.py` line 16, `M = [3, 4, 6, 8, 10, 15, 20, 30]`; R = 2000 (line 39); theta3 needs m >= 3 and theta2 m >= 4 (`round10_final_runs_f2_regimeB.py` line 190). HEST units (line 24) are on `scale="log1p"` only, with estimands theta3 and theta2, for CCRCC, CCRCC_merged, INDIANA_KIDNEY and LUNG_XENIUM times three encoders. ACS (lines 26 to 29) has `theta2_kind="mean"` (reported as mu) and theta3. The six corpus tasks run on both scales (`y_log1p__`/`f_log1p__` and `y_lognorm__`/`f_lognorm__` prefixes from `results/round10/final_runs/F2/configs/f2_cluster_values_v2_corpus.json`). That makes 31 units plus a smoke unit (`results/round10/final_runs/F2/configs/regimeB/`). Per-unit outputs are `BULK/round10/final_runs/F2/regimeB/<unit>/regimeB_summary.json`, `regimeB_cells.csv` and `regimeB_genes.parquet`. The aggregate is in `results/round10/final_runs/F2/aggregate_regimeB/`: `f2_regimeB_summary.csv` (md5 fe89af2e40be1c1e0a6924278729ed13), `f2_regimeB_fix1_vs_ppi.csv` (f6dbb9ff478924f1751879de1110bbd5), `f2_regimeB_units.csv` (4369dbf9026bf04c4ca1b2bd016ec8a3) and `f2_regimeB_checks.json` (31 of 31 units completed, 147603 rows, `cv_max_rel` 1.8091408397489947e-10).

**(b) Report.** `docs/round10/i03/final-runs/round10_final_runs_F2_report.md`, section 6.5 (regime B), the anchor row in section 3 (line 40), and the FR7 preview in section 5 (line 75). The preview is `results/round10/final_runs/F2/report_tables/r08d_regimeB_fr7_preview.csv`.

**(e) Anchors.**
- `results/round10/final_runs/F2/regimeB_smoke/regimeB_anchor_r5.csv` (md5 7221068d3ac02ef5f4678d4f0b2a8c9b), row CCRCC, uni_v2, regb, m 10, theta3, estimator C_ppi, interval regB_t, n_draws 200: emp_var_median 0.0038227345373680124, est_var_over_emp_var_median 1.0294782019269202, coverage_median 0.9075. The round 5 row in `results/round5/ppi/E3_twolevel/e3_regimeB_small_m.csv` (md5 879bd9c038f1368b5ada848a64974159) is the same: emp_var_median 0.003822734537368, est_var_over_emp_var_median 1.0294782019269202, coverage_median 0.9075, coverage_mean 0.9032, coverage_min 0.84.
- `f2_regimeB_summary.csv`, row CCRCC, uni_v2, log1p, theta3, m 6, C_fix1: G 24, genes 50, R 2000, median_coverage 0.899, q10_coverage 0.8925, q90_coverage 0.9071, median_width 0.2592332134806916, median_ev_over_var 0.9941217558072595.
- Same file, row ACS_STATES, pkg, log_income, mu, m 8, C_fix1: median_coverage 0.8795, median_width 0.11871267149767786, median_ev_over_var 0.9661955465570268. This is the largest FR7 deviation in the preview (`r08d`: ACS_STATES, 12 cells, cov_min 0.8795, cov_max 0.9115, max_abs_dev 0.0205, `pkg|log_income|mu|8`).

**(f) Compute.** `results/round10/final_runs/job_ledger.csv`, 32 regime B rows: 31 units (Slurm 8823517 to 8823729) and smoke 8814479 (00:00:49). Each unit requested 16G and ran 00:03:31 to 00:12:36 with max RSS 443328K to 2618908K. ACS took 00:03:33 and 1545008K. The HEST units took 00:03:31 to 00:11:05 (LUNG_XENIUM 00:06:11 to 00:11:05). The corpus units took 00:06:00 to 00:12:36. The aggregation ran as Slurm 8824760, 36 s.

**(g) Gaps for F3.** F2 regime B ran neither mu on the HEST tasks nor the HEST tasks' normalised scale (F2 decisions, section 3, item 5, left open). It ran no m outside the grid above.

## 2. Item 3 (i), regime A against regime B, cost-matched as in round 5's E3

**(a) Code.** `round5_ppi_e3_twolevel.py`, part `regcomp`. Its grid is line 56, `REGA_NL, BUDGETS, COSTS = (4, 6, 8, 12), (2400, 4800, 9600), (10.0, 100.0, 1000.0)`, and `part_cells` runs from line 179. Regime A labels n_L donors (`Q2.B1.draw_L`, line 225, seed `r5e3|<vtag>|<tag>|d<d>`) with `m_A = B // n_L` spots in each, for n_L <= G - 2. Regime B labels every valid donor with proportional allocation `m_g = min(M_g, max(1, round(B' M_g / N)))` (line 208). The cost-matched budget is `B' = n_L (c + B / n_L) - c G` (line 194), kept when positive, so `C = c_d n + c_s n m` with `c = c_d / c_s`. theta2 cells use the stratified-by-group draw (`units`, lines 89 to 117), and m below 4 is raised to 4 for theta2 (`run_part`, about lines 229 to 232). `run_draw` calls `round5_ppi_twolevel.estimate` with six estimators (`ESTIMATORS`, `round5_ppi_twolevel.py` line 37: r4_classical, r4_ppi, P_classical, P_ppi, C_classical, C_ppi). Regime A intervals are `textbook_t|fpc|lin` and `textbook_t|fpc|lin|xf`, and regime B uses `regB_t`. The draw count defaults to 200 (`--draws`, line 514). `round5_ppi_e3_merge.py` scores E3.4 (lines 162 to 189). It compares per-gene widths of regime A (`PRIMARY = "textbook_t|fpc|lin|xf"`, line 27) with regime B at `cd_cs_10_` budgets for theta3, takes the median over genes per (vtag, arm, n_L, budget), and keeps round 4's arms. E3.7 is lines 235 to 256. `round5_ppi_e3_sim.py` is the synthetic version (line 72: n_L 6, 8, 12, G; m 3, 5, 20, 100, all; mu 0, 3, 10; `--reps` 2000 at line 190).

**(b) Report.** `docs/round05/i02/ppi/round5_ppi_E4_report.md`, section 6.2 (E3, the two-level estimator; E3.4 and E3.7) and section 6.3 (stratified draw for theta2). Also `docs/round05/i03/ppi/round5_ppi_final_report.md`, section 6.2. The ledger row is `results/round10/ledger/round10_ledger_L1_S5.md`, S5.5.

**(c) Inputs.** `--parquet` is a round 3 or round 4 prediction parquet loaded by `round5_ppi_e2_regimeB.load_arm` (for example `BULK/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet`, in `results/round5/ppi/E3_twolevel/CCRCC/uni_v2__regcomp/PROVENANCE.txt`). These are the same files round 10 names for the HEST tasks on log(1+y), with the same columns (y__, f__, donor_id, m_std and the round 3 design constants). F2's regime B reads them through the same `load_arm`. ACS uses `BULK/round4/ppi/Q2_theory/predictions/ACS_STATES.parquet`, arm `package`.

**(d) Parameters.** Listed in (a). Encoders are hoptimus0, uni_v2, resnet50 and package, plus the arms permuted, constant and donor_constant (merge line 26). Tasks are CCRCC, CCRCC_merged, INDIANA_KIDNEY, LUNG_XENIUM, ACS_STATES and ACS_CA_PUMA (merge line 23). The gene scope is every gene of the parquet (LUNG_XENIUM 343). `--max-genes` defaults to 0.

**(e) Anchors.** `results/round5/ppi/E3_twolevel/e3_regime_comparison.csv` (md5 e08e687816855f9e5ededdb038b67e22, 17929 lines with header):
- Regime B row: vtag CCRCC, arm uni_v2, G 24, part regcomp, regime B, budget 2240.0, cost `cd_cs_10_vs_A_nL8_B2400`, n_L 24, m prop, estimand theta3, target design, interval regB_t, n_draws 200, n_genes 50, estimator C_ppi. Values: emp_var_median 0.0005179918654981, est_var_over_emp_var_median 0.9951539563920146, coverage_median 0.9, coverage_mean 0.9, coverage_min 0.855, m_median 79.0.
- The regime A row it is matched to: CCRCC, uni_v2, regcomp, A, budget 2400.0, cost unit, n_L 8, m 300, theta3, interval `textbook_t|fpc|lin|xf`, estimator C_ppi. Values: emp_var_median 0.0015819583782623, est_var_over_emp_var_median 0.9548431367224566, coverage_median 0.8825000000000001, coverage_mean 0.8797999999999999, coverage_min 0.81.
- The E3.4 score in `results/round5/ppi/E3_twolevel/e3_prediction_scores.csv` reads "C_ppi: B narrower in 210 of 232 comparisons, median ratio 0.430; P_ppi: B narrower in 211 of 232 comparisons, median ratio 0.513".

**(f) Compute.** `results/round5/ppi/E3_twolevel/CCRCC/e3_job_ledger__CCRCC.csv`, CCRCC uni_v2: regcomp Slurm 4317296 took 00:49:18 (8G requested, 2 CPUs, max RSS 0.607 GB, `elapsed_s` 2951.9 in PROVENANCE, 612 rows, 200 draws). regb 4317306 took 00:13:45 (0.568 GB). One job runs per (task, arm, part). Other tasks have their own `e3_job_ledger__<task>.csv`, which were not tabulated here.

**(g) Gaps.**
1. E3's regime A is two-stage (m_A = B/n_L spots in each labelled donor), not whole clusters. In regime A, `round5_ppi_twolevel.estimate` uses round 5's retired between coefficient (`E.lambda_rule("c_crossfit_design", ...)`, between stage), and the variance `(1 - n_L/G) s_e^2 / n_L + sum_g V_g / (G n_L)` plus `crossfit_extra`. No two-stage regime A form exists with the decided estimator: the fixed coefficient of 1 at both stages, or Mickey's two-fold form beside it from 6 labelled clusters. `_tl_fixed` sets only the within coefficient. With estimator `C_fix1`, `ppi` is False, so in regime A the between coefficient would be 0 (`lamc`, `cU` zero), which is not the fixed-coefficient difference estimator. F2's regime A (`round10_final_runs_f2_regimeA.py`, `round10_final_runs_estimators.difference_fixed` and `crossfit`) works on whole-cluster values (m = all) only. A cost-matched comparison therefore needs either a new two-stage regime A with the decided estimator, or a comparison of F2's whole-cluster regime A with regime B at a budget equal to the labelled donors' spot counts. Which of the two to use is for the lead to decide.
2. F2's regime B uses equal m per cluster (tag `regb|...|m<m>`). E3's cost-matched regime B uses proportional `m_g` and tags `regcomp|B|B<budget>|<cost>|nL<G>|mprop`. `run_cell` in `round10_final_runs_f2_regimeB.py` cannot reproduce regcomp seeds unchanged, because `tag_of` is fixed to regb. `E3.units` does accept a per-donor m array.
3. E3 covers neither the corpus tasks nor the normalised scale nor the 42-gene LUNG_XENIUM subset.

## 3. Item 3 (ii), question V: the bounded and unbounded columns, coverage at those m, largest share and G*

**(a) Code.** `round9_fewcluster_box.py` (140 lines):
- `k_min` (lines 29 to 31) is the smallest admissible two-point minority at Lambda_0.
- `box_worst(Ns, sds, m, lam0)` (lines 34 to 52) computes `V_h = sd_h^2 (1 - m/N_h)/m`, `v = V_h / sum V_h`, `v0 = max v` (line 39), `s = ceil(1/v0)` and the product of the s largest two-point factors (lower) and with the R level (upper). Clusters with m >= N_h are skipped (`prob = mm < Ns`, line 40).
- `regime_A(zbar, G)` (lines 55 to 58) gives Theorem 1 on the cluster means (kappa_A, n_min_A).
- `analyse` (lines 61 to 80) sets `Lambda_h = max|e - mean| / sd` per cluster and `Lambda0 = max_h`, and scans `M_GRID = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 75, 100]` (line 26). `m_min_B` is the first m with the upper bound <= alpha, and `m_min_B_twopoint` uses the lower bound. ALPHA is 0.10 (line 25).
- Mode `hest` (lines 109 to 136) reads three uni_v2 parquets (lines 110 to 112) and, for every gene and lambda in {0, 1}, forms spot residuals `e = y - lambda f` per donor (line 121). The estimand is the donor-weighted mean mu.
- Mode `acs_states` (lines 87 to 108) reads the aggregates `i32_acs_states.csv`.

The helpers are imported from `round9_fewcluster_strat_frontier.py` (`log_pi` line 36, `log_R` line 42, `thm1_frontier` line 134, `frontier` line 117, `kappa_st` line 122). `round9_fewcluster_regimeB_acs.py` (65 lines) rebuilds round 4's ACS person-level task (filters at its line 25, HistGradientBoostingRegressor over five crc32 folds of states, lines 28 to 33) and writes `i32_acs_states.csv` and `i32_acs_regimes.csv` (pooled-class frontier for m = 2..12, 15, 20, 30). The box verifier is `results/round9/fewcluster/verify_strat/check_box_class.py` (101 lines), with output `box_output.txt`: "formula == exact beta in 360 of 360" for Lambda0 >= 2. G* per gene is computed in `round10_final_runs_f2_diagnostics.py` line 47 (`Gstar_e = 1 / sum((d/ss)^2)`, the share of each cluster in the sum of squares of the fix1 residual `e_g = z_g - f_g`), with `kappa_e` the largest share.

**(b) Report.** `docs/round09/i03/fewcluster/round09_fewcluster_stratified.md`, section 4 (the box class, lines 101 to 113) and section 5 (the regime A against regime B table at lines 121 to 130, and the design table for v0 from 0.025 to 1 at lines 132 to 141). Predictions are in `results/round9/fewcluster/strat/predictions_before_run.md` and `predictions_scored.md` (R5b refuted on the low side, R6 held; the HEST run is Longleaf job 161e6b2b). The decision text is `docs/round10/i01/ledger/round10_ledger_decisions.md`, section 4. The ledger row is L1_S5.md S5.5, item 1.

**(c) Inputs.** HEST: `results/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet`, `results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__uni_v2.parquet` and `results/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__uni_v2.parquet`, relative to `<src>` (`BULK/..`, the hest_replication root). It reads columns `y__*`, `f__*` and `donor_id`, which are the same files and columns as round 10's final HEST files on log(1+y). ACS reads `acs_pums2018_all_columns.parquet` in an ACS directory given on the command line (not recorded in results). The box `acs_states` mode reads the committed `results/round9/fewcluster/strat/i32_acs_states.csv` (md5 fc561a7f80be6617b3463c1dc19040c8).

**(d) Parameters.** alpha 0.10 (line 25). M_GRID is at line 26. lambda in {0.0, 1.0} (line 120; lambda = 1 is the fixed coefficient). The genes are every y__ gene (LUNG_XENIUM 343; the hest summary shows n_genes 343). The encoder is uni_v2 only. `worst_m5`, `worst_m10` and `worst_m20` are recorded (line 76). The stylised table `i32_required_m_B.csv` has N in {2000, 20000}, Lambda0 in {2, 3, 4, 5, 6, 8, 10} and v0 in {1.0, 0.5, 0.2, 0.1, 0.05, 0.025}.

**(e) Anchors.** All files are in `results/round9/fewcluster/strat/`:
- `i32_hest_box_genes.csv` (md5 be645dc258d4dff761c5e4d66b0748f8), row CCRCC, AKAP8, lambda 1.0: G 24, N_median 2893.0, Lambda0 4.897104039833776, Lambda_h_median 3.7177774502771515, kappa_A 0.7114255434500643, n_min_A 17, frontier_A_mid 0.15833333333333333, worst_m5 0.12912661802131933, v0_m5 0.10074837168693684, s_m5 10, worst_m10 0.016611782023137286, v0_m10 0.1005491246683458, s_m10 10, m_min_B 6.0, m_min_B_twopoint 6.0.
- `i32_hest_box_summary.csv` (md5 3d9cc7ca166f0c4cc638a835b0d3d216), lambda 1.0 rows:
  - CCRCC: n_genes 50, Lambda0_median 5.332146346063535, m_min_B_median 6.0, frac_B_le10 0.96, n_min_A_median 17.0.
  - INDIANA_KIDNEY: 50, 6.341449387358195, 8.0, 0.82, 13.0.
  - LUNG_XENIUM: 343, 5.338684602637481, 8.0, 0.6647230320699709, 8.0, frac_B_none 0.0.
- `i32_acs_box.csv` (md5 51e8b800b1fe5c29b760a221195de718), lambda 1.0: G 51, Lambda0 8.929978495775948, kappa_A 0.09383067495029383, n_min_A 11, v0_m5 0.025097641877542622, s_m5 40, m_min_B 5, m_min_B_twopoint 5.
- `i32_required_m_B.csv` (md5 6fdea85a7512ac4278be7583b7c6d8a7), the unbounded column v0 = 1.0 at N = 2000: Lambda0 2 gives 11, 3 gives 22, 4 gives 38, 5 gives 58, 6 gives 81, 8 gives 143, 10 gives 217. At N = 20000: 11, 22, 38, 59, 84, 148, 229.
- Cross-check with round 10. `results/round10/final_runs/F2/diagnostics/f2_anchor_r9_c0.csv`, row CCRCC, uni_v2, log1p, mu, AKAP8 has kappa_e 0.7114255434500643 (equal to the box file's kappa_A at lambda 1) and Gstar_e 1.9402130494185492. The ACS row has kappa_e 0.09383067495029362 (box file 0.09383067495029383) and Gstar_e 22.35916815063716.

**(f) Compute.** The round 9 box HEST run is Longleaf job 161e6b2b (`predictions_scored.md`). Its wall time and memory are not found (looked in `results/round9/` and `docs/round09/`; there is no PROVENANCE.txt under `results/round9/fewcluster/strat/`).

**(g) Gaps.**
1. **The unbounded column has no code.** `box_worst` derives v0 from the population (line 39) and takes no v0 argument, so v0 = 1 (s = 1) needs an override of line 39. The producer of `i32_required_m_B.csv` was not found: I grepped `code/scripts/*.py` and `results/round9/` for `required_m_B`, and only the documents cite it. That table is stylised (equal N_h, not a task's own N_h and sd_h).
2. **M_GRID stops at 100** (line 26). At v0 = 1, the stylised table already needs 58 to 143 units at Lambda0 from 5 to 8, and ACS has Lambda0 8.93, so many genes would return None. The grid must extend above 100. m is also capped at N_h, and a fully sampled cluster drops out of the product (line 40).
3. **The hest mode is fixed** to uni_v2 and three task paths (lines 110 to 112) on log(1+y). It has no CCRCC_merged, no other encoder, no normalised scale and no corpus task. The normalised refits are `BULK/round10/final_runs/F2/refit_norm/<task>__<enc>/norm/b1_predictions__<TASK>__<enc>.parquet`; their y__/f__ naming is inferred from `round10_final_runs_f2_refit_norm.py` `compare` (line 101 reads the `y__` prefix), and the schema was not opened. Corpus files use the prefixes `y_log1p__`, `f_log1p__`, `y_lognorm__` and `f_lognorm__`, with the donor column from the config.
4. **mu only.** The box class is computed only for mu (spot residual `y - f`). No code computes it for theta3 or theta2, whose unit contributions are round 5's linear forms.
5. **Coverage at the box m.** F2's regime B has no mu cells on the HEST tasks and no HEST normalised scale, and its m grid {3, 4, 6, 8, 10, 15, 20, 30} does not contain the per-gene box m (for example 5, 12, 25, 40 to 100, or above 100). `run_cell` accepts any integer m. Per-gene m needs either runs at the union of m values with per-gene selection, or a change to the driver.
6. **Largest share and G* per gene.** These exist per gene in the bulk file `BULK/round10/final_runs/F2/diagnostics/diagnostics_v2/f2_gene_diag.parquet` (17442369 bytes, not committed; columns not opened). Committed per-gene rows exist only for the round 9 anchor populations (`f2_anchor_r9_c0.csv`, log1p, mu, 1480 rows), and the cell medians are in `f2_shortfall.csv`. Both are regime A cluster-level shares of `z_g - f_g`. The regime B share `v_h` (box_worst's `v0` at m) is a different quantity, and decisions section 4 does not say which one is meant beside the regime B columns.
7. **ACS.** The box run uses round 9's rebuild of the ACS predictions. F2's regime B uses round 4's `ACS_STATES.parquet` package predictions. They agree at the state level (kappa_e above to about 2e-16). Unit-level identity was not checked.
8. **LUNG_XENIUM** needs the 42-gene flag `zlib.crc32(gene) % 7 == 0` added, which the box script lacks.

## 4. Item 3 (iii), the allocation formula from the final components

**(a) Code.** `round5_ppi_e5_allocation.py` (59 lines, all read), `main` lines 25 to 55. It reads `results/round5/ppi/E3_twolevel/e3_components.csv` (form C, theta3) and takes medians over genes of `1 - R2_w`, `1 - R2_c` and `mstar_cd100`. It reads `e3_masking_grid.csv` and computes `rho_c(n_L)`, the ratio of the median-over-genes empirical variances of C_ppi to C_classical at m = all, design target, interval `textbook_t|fpc|lin|xf` (lines 30 to 32, 43 to 45). It reads `e3_components_fitted.csv` for the fitted check. Then `m_star_PP = m_star sqrt((1 - R2_w)/rho_c)` (line 49). The components come from `round5_ppi_e3_twolevel.components_part` (lines 347 to 415). That function computes the between variance A, the within variance B on each form's scale, `R2_c` with the clipped least-squares coefficient `lc`, `R2_w` with the clipped pooled within slope `lamC`, `mstar_cd<c> = sqrt(B0/A c)` and `mstarPP_cd<c> = mstar sqrt((1 - R2_w)/(1 - R2_c))` for c in {10, 100, 1000}.

**(b) Report.** `docs/round05/i03/ppi/round5_ppi_final_report.md`, section 6.6 (E5, allocation), and section 6.3, item 4 (E3.5). The ledger row is L1_S5.md S5.6.

**(c) Inputs.** Committed CSVs only (paths hard-coded at lines 18 and 19). The components were built from the same round 3 and round 4 parquets as E3.

**(d) Parameters.** `ENC` (line 20) covers the six round 5 tasks: three encoders on tissue, package on ACS. Form C, theta3, `c_d/c_s = 100` only. The n_L values are those of the masking grid, `MASK_NL = (4, 6, 8, 12, 16)` (`round5_ppi_e3_twolevel.py` line 57).

**(e) Anchors.** `results/round5/ppi/E5_joint/e5_allocation.csv` (md5 802b4abd4c56b86c056d85cac57b89e7, 67 rows):
- CCRCC, uni_v2, C, theta3, n_L 8: G 24, n_genes 50, one_minus_R2_w 0.9443644327339251, one_minus_R2_c 0.5612737576914483, rho_c 0.823570449019362, m_star_classical_cd100 77.88554998357554, m_star_PP_cd100 83.40197296555694, ratio_PP_over_classical 1.0708272970165158, fitted_m_star_classical_cd100 78.3803454280435, fitted_m_star_PP_cd100 80.239241968845.
- LUNG_XENIUM, uni_v2, C, theta3, n_L 8: one_minus_R2_w 0.49097990051160545, one_minus_R2_c 0.30509603779731753, rho_c 0.424697937725452, m_star_classical_cd100 74.48365729507627, m_star_PP_cd100 80.08529394191414.
- The input md5 are `e3_components.csv` 6592b3443792f7eabd27a950017717fe, `e3_masking_grid.csv` ad1e79207ea93763295724881e13934d and `e3_components_fitted.csv` e86daf2fc86090e264a4d6d997803e8e.

**(f) Compute.** This is a local CSV computation. The components part took 00:00:16 for CCRCC uni_v2 (Slurm 4317291, 0.691 GB).

**(g) Gaps.**
1. Both ingredients rest on round 5's coefficients. The R^2 use clipped fitted slopes in `components_part`, and rho_c is the C_ppi/C_classical ratio under the retired regime A estimator. Nothing computes the components for the coefficient fixed at 1 (for example `1 - R2` from `var(z - f)/var(z)` and its within analogue), or rho_c from F2's regime A (`regimeA_cells.parquet` carries `sd` per arm, so `fix1` against `classical`, and `xf2` from n_L >= 6).
2. It covers theta3 and form C only. It has no corpus tasks, no normalised scale, no mu and no theta2.
3. The paths are fixed to round 5's `results/round5/ppi/E3_twolevel`.

## 5. Item 3 (iv), `rej_t` and the cube design matched against simple random selection

**(a) Code.**
- `round5_ppi_balance.py`: `mahalanobis_pool`, `d2_select`, `va_nominal` (Morgan and Rubin's v_a), `rej_t(zbar, X, Lm, p_a)` and `perm_cluster_variable`. `rej_t` returns the classical labelled mean with variance `(1 - n/G)(s2_res + v_a b' S_x b)/n` from least squares of zbar on X with an intercept. Its df is `n - k - 1`, and it returns NaN when df < 2. It does not call round 4's `var_textbook`.
- `round5_ppi_e4b_rejective.py` (380 lines): `NL = (4, 6, 8, 12)` (line 51), `BATCH = 2000`, `RULES = ("none", "c_crossfit_design")`, `N_BOOT = 500`, `SUB = 200` (lines 52 to 55). `pool_thresholds` (line 84) sets the thresholds at p_a 0.1 and 0.01 (line 222) from a pool of `--pool-cand` 500 times 2000 draws. `cand_idx` (line 58) uses seeds `r5e4c|...`. The designs are D0, D1 and D2 (line 268). Its header has the balance variables own, pcF2, pcE2, perm and perm_cluster.
- `round7_ppi_d2.py` (257 lines): fixed thresholds, crc32 candidate streams, and `load_cell` (lines 51 to 75). `load_cell` reads `--parquet`, `--perm-parquet` and `--ref-parquet` through `load_arm`, plus embeddings `results/round4/ppi/Q5_joint/q5_mean_embeddings__<vtag>__<enc>.parquet` (`round5_ppi_e4_selection.embeddings`, line 61) for pcE2.
- `round7_ppi_s1_masking.py` (300 lines) makes the D2 masking rows (rej_t, H_sim). `NDRAW = 2000` (line 39); the balances are own and perm_cluster on census, plus pcF2 and pcE2 on tissue (line 145).
- `round7_ppi_s3_cube.py` (564 lines): `target_pi` with `TAU = 0.5`, `cube` (fast flight on 3 units, balance (pi_g, fbar_g)), `pi_sim`, `resid_var`, `all_intervals`. `NDRAW = 2000` (line 35); `--designs` is cube_u1, cube_u2 and mix; `--mix-pa` is 0.1 and 0.01.
- `round7_ppi_s4b_cube3.py` (345 lines): `cube_p` with balance (pi_g, 1, fbar_g), `resid_var_p`, and `intervals_p` (Hajek and HT with Sen-Yates-Grundy and simulated pi_gh, t_{n-rank}).
- `round7_ppi_s5_numbers.py` (255 lines) builds the matched table. Its designs are `MATCHED = ["D0_classical", "D0_tuned", "D2_rej_t", "D2_H_sim", "cube_S3", "cube_S4b", "mixture", "bh", "bh_t"]` (line 35) and `NOM = 0.90` (line 36). It reads the merged round 7 outputs `results/round7/ppi/{S1_weighting,S3_adaptive,S4b_cube_constant,S2_comparators,S2b_diagnostics}/.../*_genes__*.csv.gz` (`load`, lines 68 to 125).

**(b) Report.** `docs/round05/i03/ppi/round5_ppi_final_report.md`, section 6.4 (E4b), and escalations 1 and 7. `docs/round07/i03/ppi/round07_ppi_final_report.md`, sections 6.1 (S4b) and 6.2 (the designs on matched informative cells), and section 10. The ledger rows are L1_S5.md S5.7 and S5.9, and decisions section 6, item 1 (R7-7).

**(c) Inputs.** The round 3 and round 4 prediction parquets are the round 10 HEST log1p files, with the same columns. The permuted and reference arms use the resnet50 parquet; for example S4b and S1 commands in `results/round7/ppi/S4b_cube_constant/CCRCC/*/PROVENANCE.txt` and `S1_weighting/CCRCC/*/PROVENANCE.txt` pass `BULK/round3/B1_ppi/b1_predictions__CCRCC__resnet50.parquet` to `--parquet`, `--perm-parquet` and `--ref-parquet` for the constant arm. The embeddings are the round 4 Q5 mean embeddings.

**(d) Parameters.** n_L is 4, 6, 8 and 12. p_a is 0.1 and 0.01. Draws are 2000 (200 on E4's seeds in E4b). The support rule is `p_a C(G, n_L) >= 1000` (round 5 definition, final report section 6.5). The estimands are theta3 and theta2 (mean on ACS). The domains are tissue (the four HEST tasks) and census (ACS_STATES, ACS_CA_PUMA).

**(e) Anchors.**
- `results/round7/ppi/S5_numbers/run1/s5_matched.csv` (md5 9209f13fcf1e2ebeaf91e2d2416a4e30), columns domain, n_L, p_a, design, n_cells, coverage_all, coverage_all_min, coverage, share_formed, share_formed_min, wr_D0cl, wr_rej:
  - census, 8, 0.01, D2_rej_t: 4 cells, coverage_all 0.8885, coverage 0.8885, wr_D0cl 0.4560598818.
  - census, 8, 0.01, cube_S4b: 0.88525, wr_D0cl 0.5678732974.
  - census, 8, 0.01, cube_S3: 0.8985, wr_D0cl 0.9121489887.
  - census, 8, 0.01, D0_classical: coverage 0.88575, wr_D0cl 1.
  - tissue, 8, 0.01: 18 cells. D0_classical has coverage_all 0.875125. D2_rej_t has coverage_all 0.861125, coverage 0.8613395896 and wr_D0cl 0.887974678. cube_S3 has 0.88475 and 0.891492554. cube_S4b has 0.885 and 0.8827274207.
  - census, 4, 0.01, cube_S4b: n_cells 4, coverage_all 0, share_formed 0.
- `results/round5/ppi/E4b_rejective/e4b_rej_width_ratios.csv` (md5 cab5078856016c093bd90ac19ffe9efd), row CCRCC, uni_v2, theta3, n_L 8, own, p_a 0.01: wr_D0cl 0.7262961344734262, wr_D0tuned 0.8523229015770427, var_ratio 0.6327631433602424, coverage 0.83175, coverage_D0cl 0.849, n_genes 50, support 7354.71, frac_genes_abs_bias_z_gt_3 0.62.

**(f) Compute.** Round 7 final report section 2.1, for S4b:
- CCRCC: 20 jobs, 00:09:30 to 00:19:55, at most 0.93 GB.
- CCRCC_merged: 20 jobs, 00:09:11 to 00:20:19, at most 1.04 GB.
- INDIANA_KIDNEY: 20 jobs, 00:08:01 to 00:18:24, at most 0.80 GB.
- LUNG_XENIUM: 20 jobs, 00:18:34 to 00:59:56, at most 1.96 GB.
- ACS_STATES: 10 jobs, 00:00:44 to 00:01:21.
- ACS_CA_PUMA: 10 jobs, 00:03:11 to 00:44:56.
- S5 numbers: Slurm 4968458, 24.6 s, on a node with 49152 MB.

S1 and S3 jobs are rows of `results/round7/ppi/r7ppi_slurm_jobs.csv` (172 rows matching "S1", 134 matching "S3"), not tabulated here. Round 5 E4b jobs are in `results/round5/ppi/E4b_rejective/<task>/e4b_job_ledger__<task>.csv`, not tabulated.

**(g) Gaps.**
1. `rej_t` is the classical mean with a regression on the balance variables. No form exists with the coefficient fixed at 1, for example `rej_t` applied to `z - f`, or the D2 difference estimator. The cube intervals are HT and Hajek of zbar, with fbar as a balance variable, not the fix1 difference estimator.
2. The simple-random comparators in `s5_matched.csv` are `D0_classical` and `D0_tuned` (round 4's tuned rule), not `fix1` or `xf2`. F2's regime A has fix1 and xf2 under simple random sampling, but on different draws, so the matching would be by cell (task, encoder, estimand, n_L), not paired draws.
3. `s5_numbers.py` reads round 7's merged bulk outputs, so a round 10 rerun needs S1 masking, S3 masking and S4b masking rerun first. Their scripts take task paths on the command line and have no corpus loader, no normalised scale and no 42-gene flag.
4. The ACS_CA_PUMA task is not among round 10's tasks.

## 6. Item 3 (v), the probe and take-all design and its variance

**(a) Code.**
- `round9_probe_takeall.py` (52 lines, all read), `main(pq, task, out, reps=400, o=3)` (line 14). The probe takes o = 3 random spots per donor and sets `u_hat_g` to the mean over genes and probe spots of y. The k donors furthest from the median `u_hat` are taken with certainty, and n_L - k more are drawn at random from the rest.
  - T0 is `(sum over take-all + (G - k) mean of rest)/G` with `se = (N_r/G) sqrt((1 - n_r/N_r) s^2/n_r)` and `t_{n_r - 1}`, where `n_r = n_L - k`.
  - T2 adds a regression on `u_hat` within the rest, with `t_{n_r - 2}`.
  - D0 is the plain mean of a fresh SRS of n_L.
  - The loops are k in (1, 2) (line 22) and n_L in (6, 8, 12) (line 23), skipping n_L - k < 4 or n_L >= G. One generator, `default_rng(20261027)` (line 21), serves all cells.
- `round9_probe_feasibility.py` (73 lines): D0 to D3 regressions on the donor-mean prediction and/or `u_hat`, o in (1, 3) (line 36), n_L in (4, 6, 8, 12) (line 37), `default_rng(20261026)` (line 34), 400 reps.
- `round9_fewcluster_takeall_kappa.py` (41 lines): the residual max-share of CCRCC uni_v2 after removing INT5 or the top-residual donor, against the frontier of 7 of 23. It reads round 9's `c0_cluster_summaries.csv.gz`.

**(b) Report.** `docs/round09/00_prep/round09_probe_designs.md` (17 lines, sections 1 to 3). `results/round9/probe/predictions_before_run.md` and `predictions_scored.md` (R5 partly held, R6 held; take-all job 8f4d6844, probe job 74cc77e6). `docs/round09/i03/fewcluster/round09_fewcluster_stratified.md` line 143 (take-all in Theorem 3). The ledger row is L1_S5.md S5.11, item 7, which states that T0's variance does not include the first phase.

**(c) Inputs.** One prediction parquet per task (positional argument). It uses `y__*` and `donor_id` only; feasibility also uses `f__*`. The same column names exist in round 10's HEST files. The parquet paths of the round 9 runs are not recorded: there is no PROVENANCE in `results/round9/probe/`. The encoder does not affect T0 or D0, which use y only.

**(d) Parameters.** As in (a): reps 400, o 3, k {1, 2}, n_L {6, 8, 12}, alpha 0.10 (`stats.t.ppf(0.95, ...)`). The gene scope is every gene of the parquet.

**(e) Anchors.**
- `results/round9/probe/takeall_medians.csv` (md5 adefec680779cb089fc6ed23769a58e1), CCRCC, k 1, n_L 8:
  - D0: median_coverage 0.825, p10_coverage 0.675, median_width_ratio 1.0.
  - T0: 0.885, 0.8268, 0.7794.
  - T2: 0.8475, 0.797, 0.6658.
- The same file at INDIANA_KIDNEY, k 1, n_L 8: T0 0.855 against D0 0.865.
- `results/round9/fewcluster/design/i23_takeall_summary.csv`: n_genes 50, frontier_7_of_23 0.1565217391304348, median_kappa_all 0.5331713887432197, median_kappa_without_INT5 0.29257140632107703, frac_inside_without_INT5 0.06.
- `results/round9/probe/probe_medians.csv` (md5 1bc945fdd4916f642c3acc9bedd326f0), CCRCC, o 3, n_L 8: D2 has median_coverage 0.8112 and median_width_ratio 0.6298.

**(f) Compute.** Not found. The jobs are named 74cc77e6 and 8f4d6844 in `predictions_scored.md`, with no wall time or memory recorded in `results/round9/` or `docs/round09/`.

**(g) Gaps.**
1. No code implements the two-phase variance for a stratum chosen in phase one: I searched `code/scripts` names, and ledger S5.11 item 7 says Rao (1973) and the two-phase treatment are unread. T0's variance comes from the rest only and conditions on the first phase without saying so. The brief allows either the two-phase variance or a statement that the report conditions on the first phase.
2. T0 and T2 have no predictions. There is no fixed-coefficient or cross-fitted version of the take-all estimator: residuals `z - f` in the take-some stratum are not implemented.
3. 400 reps, one shared RNG stream across cells (results depend on loop order), no crc32 per-population seeds, and mu only.
4. No corpus loader (corpus prefixes differ), no normalised scale, no 42-gene flag. CCRCC_merged was not run in round 9 (`takeall_medians.csv` has CCRCC, INDIANA_KIDNEY and LUNG_XENIUM only).

## 7. Item 5 (V) and FR7

**Item 5** needs no new code beyond sections 3 and 1. The report sets side by side, per task (and gene), the bounded column (`m_min_B` at the population's own Lambda0 and v0), the unbounded column (the same Lambda0 with v0 = 1; gap 3.g.1), the largest share, and G* (gap 3.g.6 on which share). The only committed numbers today are round 9's, for uni_v2, log(1+y) and mu (section 3.e).

**FR7** (brief line 119). Clause 1 is median coverage of the regime B interval with the coefficient fixed at 1 within 0.03 of 0.90 at every m >= 6 on every HEST task and on ACS by state. The F2 preview `results/round10/final_runs/F2/report_tables/r08d_regimeB_fr7_preview.csv` already gives the maximum absolute deviation over its cells:
- CCRCC 0.0040000000000000036 (36 cells)
- CCRCC_merged 0.004249999999999976
- INDIANA_KIDNEY 0.0030000000000000027
- LUNG_XENIUM 0.00550000000000006
- ACS_STATES 0.020500000000000074 (12 cells)

Those cells cover only theta3 and theta2 on log(1+y) for HEST and mu and theta3 for ACS, on F2's m grid. Clause 2 (the unbounded column needs more units than the bounded one on every task) needs the unbounded column of section 3, which no script computes on task populations. By construction (s = 1 against s = ceil(1/v0) >= 1), the unbounded requirement is never smaller than the bounded one. Whether it is strictly larger on every task is the empirical part.
