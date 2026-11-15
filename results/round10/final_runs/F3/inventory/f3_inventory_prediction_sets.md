# F3 source inventory: prediction sets (item 1), institution axis (item 2), P10.3 and FR8

Read-only inventory, round 10 track final-runs, for the lead session writing F3's methods. Repository clone read: `/work/users/w/e/weiyang/hest_code/round10-final-runs` (branch round10-final-runs, commit 71ed8070 per the brief; working tree read directly, no git run). Bulk roots read: `/work/users/w/e/weiyang/hest_replication/results/` (written `$B` below) and `$B/round10/final_runs/` (written `$F`). Line counts and md5 sums come from `wc -l` and `md5sum` on the clone's copy. No methods are proposed here.

## 0. Script registry (clone copies)

| script | lines | md5 | role for F3 |
|---|---|---|---|
| code/scripts/round4_conf_c3.py | 830 | 2d8418677cf8290eec89a14c315b92cd | shared real-data module: base-head refit per (fold, cal draw), HCP, pooled, one_per, GHCP family (paper eta 0, eq. 8 eta 0.5, released pool), within, within_plain, recentred |
| code/scripts/round5_conf_w3.py | 375 | 737a452b090da9609c798cc482f6896d | the K x o map driver; imports C3 unchanged and adds `within_full` |
| code/scripts/round5_conf_w3_merge.py | 282 | 88d41fb29ff244ea69112d50dfb0c2c9 | W3 merge: w3_by_fold.csv, w3_map_by_task.csv, reproduction of round-4 rows |
| code/scripts/round5_conf_w3_report.py | 272 | 60ab3948f2320f9734f761198980b5e8 | W3 report numbers and prediction scores |
| code/scripts/round5_conf_w5_map.py | 311 | d698a0c843249bdad3fb0b034ca9ea14 | the map on one axis (simulation, GHCP designs, real data) |
| code/scripts/round5_conf_w5_numbers.py | 46 | c195ec9e2342c938b3006d8fa7e930b3 | W5 report numbers |
| code/scripts/round5_conf_io.py | 130 | f18747b8a837e4e3b504edaf10999351 | provenance writer used by W3 |
| code/scripts/round4_conf_io.py | 176 | 1936e4350d2dfc5816b0fd45e343e810 | DATA_ROOT, round-3 module import, control-feature drop for lung |
| code/scripts/round4_conf_sim.py | 757 | 76fda34ee622e299bbaa806e5c8da98a | reference kernels (hcp_q, ghcp_q, wquantile, restricted_pool, QTOL) |
| code/scripts/round4_conf_c3_merge.py | 233 | 897b97b8e4db9f44b1c0c0d29ae87b5d | round-4 C3 merge |
| code/scripts/round3_a4b_hcp.py | 1189 | 56bf3621ae53efe41140c439164b5534 | round-3 HCP at K = 10 on CCRCC (24 and 23_merged); C3 imports its donor map, folds and k_specs |
| code/scripts/round3_a4_scores.py | 2483 | 541bca01159e06d971419391415c734c | adaptive scores: scaled, scaled_clip (locally weighted), cqr, nb, nb_conformal |
| code/scripts/round3_a0_harness.py | 1800 | 0ad7ae8efe554c1f285e5f384a9fb7f5 | load_task, fit_base, folds, size matching (imported unedited by all of the above) |
| code/scripts/round9_stud_feasibility.py | 89 | 2cbbe619e083114a7631c1b44ca84db3 | cross-gene studentized set (xgene), per-gene (pergene), own, hcp, oracle; per-donor coverage |
| code/scripts/round4_conf_c1_ghcp_compare.py | 259 | 85197b968ef4dfa6ed2297dae067e2aa | GHCP paper vs released code on simulation tables (no real data) |
| code/scripts/round4_conf_c1_ghcp_repro.py | 177 | b3ea4727024636111e4107b8d3e1de76 | runs the released GHCP launchers (simulation only) |
| code/scripts/round5_conf_w2_hcp_tie.py | 104 | 67ea1f2521ca9ec873d893ce9ae82831 | float-tie diagnosis, released HCP vs track hcp_q (simulation wrapper rows) |
| code/scripts/round5_conf_w4_hcp_pointwise.py | 127 | c81a2c92a60470f7c8726548073e2f5a | W4 theory probe (no real data) |
| code/scripts/round5_conf_w2_wrapper.py | 465 | 9c64eb0f6b56912e06654442f4a1ae6a | released GHCP code wrapper (simulation and ACS census designs) |
| code/scripts/round4_conf_c2_k5_scaled.py | 240 | 732425307f375ca5eaeb06df7639787a | per-gene scaled score inside HCP/GHCP (simulation interface) |
| code/scripts/round4_conf_c2_k4_qmodel.py | 188 | f2505a09e1adced5063e9f7994a6ffc1 | group-level quantile model (simulation interface) |
| results/round4/conformal/C3_real/frag_CCRCC_o/code/run_c34.py | 209 | 72bab24658a68639d554879e9f85f8f4 | GHCP and within_plain with the CQR score, CCRCC only (in the results tree, not in code/scripts) |
| results/round4/conformal/C3_real/frag_CCRCC_o/code/run_ccrcc_o.py | 74 | 83407489160ffd74659e3aa147159202 | round-4 C3 o-sweep driver for CCRCC (results tree) |
| code/scripts/round10_final_runs_f1_predict.py | 156 | cf0b96c4235282b5f2171922f88c1d12 | corpus prediction files (donor and center designs) |
| code/scripts/round3_b1_ppi.py | 1834 | 544721f07cb3d74dc5b92456d61fe450 | wrote round 3's b1_predictions files (leave-one-donor-unit-out) |

Four of the scripts the brief names as starting points (round4_conf_c1_ghcp_compare.py, round4_conf_c1_ghcp_repro.py, round5_conf_w2_hcp_tie.py, round5_conf_w4_hcp_pointwise.py) are simulation, reproduction or theory code and never touched the HEST tasks. The real-data map is round5_conf_w3.py over round4_conf_c3.py.

## 1. F3 item 1, the prediction-set map

### 1a. HCP, GHCP (paper rule and released rule), `within`, `within_plain`, `within_full`

(a) Scripts and functions.
- `round4_conf_c3.py`: `load_task` (l. 546), `_load_ccrcc` (l. 568), `_load_d4` (INDIANA_KIDNEY, l. 651), `_load_lung` (l. 675), `TaskData.fit` (l. 507: `H.fit_base` on the K-design's training donors, then residuals of calibration and test spots), `_ccrcc_specs` (l. 603, via `round3_a4b_hcp.k_specs`), `_a4b_like_specs` (l. 609, Indiana and lung), `o0_rows` (l. 351: pooled, hcp, one_per), `o_rows` (l. 448: GHCP variants, within, within_plain, recentred), `ghcp_cols` (l. 419), `label_stream` (l. 412), `selftest` (l. 760, against the round4_conf_sim reference kernels).
- GHCP variants (l. 139 to 145): `ghcp` (adaptation, eta 0, paper), `ghcp_noad` (eta 0, no adaptation), `ghcp_r05` (eta 0.5, paper eq. 8 pool), `ghcp_r05_noad`, `ghcp_r05code` (eta 0.5, the released code's pool, one group larger). On real data the released rule therefore exists only as `ghcp_r05code` inside this project's vectorised code. The released repository itself (soham-penn/hierarchical_CP, commit d1a69f4) was run only on simulations and the ACS census (round5_conf_w2_wrapper.py).
- `round5_conf_w3.py`: `wf_m` (l. 83), `wf_bounds`, `wf_hull`, `wf_exact_count`, `wf_metrics` (l. 122), `wf_rows` (l. 153: `within_full`), `rows_for_fit` (l. 264), `run` (l. 275), parts 1 to 3.

(b) Reports. `docs/round05/i02/conformal/round5_conf_final_report.md` section 6, "W3, real data above 10 calibration donors" (l. 97 to 113; first bullet: the narrowest valid method is HCP at o <= 5 and `within_full` from o = 9, except at o = 17 and on Indiana at o 9 to 15, where `within_plain` is narrowest); section 2 (scripts, md5s, jobs). Round 4: `docs/round04/i02/conformal/round4_conf_final_report.md` (C3, including the GHCP eta 0.5 rows). Ledger rows A4, A6, A7 in `docs/round10/i01/ledger/round10_ledger.md` l. 172 to 205.

(c) Inputs, and whether round 10's final files fit.
- C3 and W3 do NOT read prediction files. For every (task, encoder, K, fold, calibration draw) they refit the base head (`H.fit_base`, PCA-256 and ridge) on that design's training donors from embeddings and labels. Inputs: task definitions `results/round3/task_defs/CCRCC.json`, `results/round3/D4_expansion/task_defs/INDIANA_KIDNEY.json`, `results/round4/data/P5_task/LUNG_XENIUM.json` (under DATA_ROOT, `round4_conf_c3.py` l. 152 to 164); the donor audit `results/round3/D3_audit/donor_audit_r3.csv`; Indiana gene lists from `results/round3/D4_expansion` (`D4.read_genes`, per-fold gene lists through `D4.genes_for(sel, "a4b_k10", fold, -1)`, l. 667 to 671).
- Round 10's final files (`$B/round3/B1_ppi/b1_predictions__<TASK>__<enc>.parquet`, `$B/round4/ppi/Q2_theory/predictions/`, `.../predictions_INDIANA_KIDNEY/`) are leave-one-donor-unit-out predictions (`round3_b1_ppi.py` l. 361), one prediction per spot, with columns y__<gene>, f__<gene>, donor_id, sample_id, barcode, m_std. In those files a calibration donor's residual comes from a head that saw the other calibration donors and the target donor. In C3 the calibration and target donors are all outside the head's training set, and n_T_donors falls as K rises (CCRCC 13, Indiana 14, lung 4 at K = 10). So C3 and W3 cannot be pointed at the final files without a new residual source.
- Gene scope in C3 and W3: CCRCC 50 genes (task definition); Indiana per-fold gene lists (50 per fold, chosen per fold by D4); lung the task definition's `target_genes` (n_genes 343 in the JSON), with control features dropped at load (`IO.drop_control_features`, `IO.load_set_dropped`). Round 10's lung files carry 343 genes, and round 9's 42-gene subset is `crc32(gene) % 7 == 0`. I did not check whether Indiana's final file carries one fixed 50-gene list or the per-fold lists, because python cannot run on the login node.

(d) Parameter grids.
- `round4_conf_c3.py`: O_GRID (5, 10, 25, 50, 100, 200) l. 127; K_GRID_CCRCC (4 to 20 by 2) l. 128; K_GRID_LUNG (6, 8, 10) l. 129; ALPHAS (0.1, 0.2) l. 130; N_LABEL_DRAWS 20 l. 131; N_CAL_DRAWS 3 l. 132; MIN_SLIDE_SPOTS 50 l. 133; DWR_REPS 200 l. 134; SCORE "abs" l. 135; method lists l. 136 to 138. The label stream is the first o of one seeded permutation per label draw (`label_stream`, l. 412). The calibration draw seed is `f"{task}|a4b_k10|{fold}|cal{draw}"` (l. 631) for Indiana and lung; CCRCC uses `round3_a4b_hcp.k_specs`.
- `round5_conf_w3.py`: P1_O (3, 5, 9, 10, 12, 15, 17, 20, 25, 50, 100) l. 73, with part 1 at K = 10 (l. 284); P2_O (0, 5, 10, 15, 17, 25, 50) l. 74; C3_O_METHODS (ghcp, ghcp_noad, within, within_plain, recentred) l. 75; P2_K l. 76 to 77 (CCRCC 24 and 23_merged: 10 to 20 by 2; Indiana 10, 14, 18, 20); P3 tasks and head K = 20 l. 78 to 79; MGUARD 1e-9 l. 72. W3 did not run `ghcp_r05`, `ghcp_r05_noad` or `ghcp_r05code` (they are not in C3_O_METHODS). Those rows exist only in round 4's C3 (K up to 20 on CCRCC, 6 to 10 on lung).
- Encoders: all three in W3 (`--encoders` default C.ENCODERS, l. 357).

(e) Anchors (verbatim).
- `results/round5/conformal/W3_real/merged/w3_by_fold.csv` (columns part, task, label_set, encoder, method, score, alpha, o, K, fold, n_T_donors, coverage, width_mean, width_median, n_test, finite_frac, n_draws):
  - `1,CCRCC,shipped,uni_v2,hcp,abs,0.1,0,10,INT1,13,0.994458794587946,3.8797931795223435,3.820950865248102,1084.0,1.0,3`
  - `1,CCRCC,shipped,uni_v2,within_full,abs,0.1,9,10,INT1,13,0.9027435658914729,1.8448973093606125,1.80008989381594,1075.0,1.0,60`
  - `1,CCRCC,shipped,uni_v2,within_plain,abs,0.1,9,10,INT1,13,0.9116837209302326,2.047751582844251,1.9207671179015446,1075.0,1.0,60`
  - `1,LUNG_XENIUM,audited,uni_v2,hcp,abs,0.1,0,10,lungXen_THD0008,4,0.9891441354059188,4.4538958773262225,4.3271065380651335,1037.0,1.0,3`
  - `1,LUNG_XENIUM,audited,uni_v2,within_full,abs,0.1,9,10,lungXen_THD0008,4,0.9003181094561227,2.3438510363611815,2.1407641813034646,1028.0,1.0,60`
- `results/round5/conformal/W3_real/merged/w3_map_by_task.csv` (mean over encoders of fold means of width_mean; columns task, part, alpha, K, n_T_donors, o, method, valid, coverage, coverage_sd_folds, width_mean, finite, narrowest_valid): `CCRCC,1,0.1,10,13.0,0,hcp,True,0.9692115333343452,0.09847464295131296,4.10936740781251,1.0,True` and `CCRCC,1,0.1,10,13.0,9,within_full,True,0.901149546831403,0.0050819239478951,2.0807756206756403,1.0,True`.
- GHCP family, round 4, `results/round4/conformal/C3_real/c3_o_sweep_by_task.csv` (task, label_set, encoder, method, score, alpha, o, K, coverage, coverage_sd_folds, width_mean, finite, n_folds): `CCRCC,shipped,uni_v2,ghcp,abs,0.1,5,10,0.9944443494290586,0.023223054095128454,5.3641566882743,1.0,24`; `CCRCC,shipped,uni_v2,ghcp_r05code,abs,0.1,5,10,1.0,0.0,,0.0,24` (infinite, finite share 0.0); `CCRCC,shipped,uni_v2,hcp,abs,0.1,0,10,0.9694292116715538,0.10038119815317675,4.037801364039508,1.0,24`.
- Round 3 HCP, `results/round3/A4_scores/a4b_summary.csv`: `width_mean_by_encoder,donor_set=24 arm=K10 method=hcp encoder=uni_v2,4.037801364037815,72,` and `coverage_mean_by_encoder,donor_set=24 arm=K10 method=hcp encoder=uni_v2,0.9694292116715538,72,`. C3's HCP width matches round 3's to about 2e-12.

(f) Compute. W3 (`results/round5/conformal/W3_real/w3_jobs.csv`, 38 data rows; report section 2): 30 production jobs, 4 CPUs each, 48G requested. Longest wall time per unit, with peak memory: p1_ccrcc24 01:01:57 (17.7 GB), p1_ccrcc23m 00:57:56 (17.4), p1_indiana 00:22:52 (8.6), p1_lung 02:29:45 (23.5), p2_ccrcc24 05:04:06 (32.1), p2_ccrcc23m 02:42:29 (24.9), p2_indiana 01:52:02 (13.9), p3_fixedhead 04:20:42 (36.6). Merge: Slurm 4351817, 00:08:43, 9.6 GB. Round 4 C3 (`results/round4/conformal/C3_real/c3_jobs_sacct.csv`, 106 rows, 70 COMPLETED, 2 CPUs and 32G requested), completed jobs per unit with the longest elapsed time and largest MaxRSS: CCRCC K 23 jobs, 5509 s, 8.2 GB; CCRCC o 20, 4206 s, 7.2 GB; Lung o 11, 3457 s, 4.3 GB; Lung K 3, 1279 s, 1.6 GB; Indiana o 6, 1612 s, 3.1 GB; Indiana K 3, 611 s, 3.0 GB; core 3, 2462 s, 7.4 GB; ACS K 1, 2116 s, 2.5 GB.

(g) Gaps.
- No earlier script computes these sets from leave-one-donor-out prediction files. The C3/W3 code path refits a head per (fold, draw), with the calibration donors outside training. Running "on the final prediction files" needs either a new residual source or a decision to rerun the C3 path (which is the path that reproduces the anchors above).
- W3 did not run GHCP's eq. 8 or released-pool variants at K >= 10. Round 4 did, and at K = 10, alpha 0.1 on CCRCC they are infinite (row above).
- Normalised scale log(1 + 1e4 y/n): C3 and W3 build labels on log1p only (`_load_lung` l. 682 `np.log1p`, Indiana `D4.log1p_cols`, CCRCC through the harness's labels). Not implemented.
- Corpus tasks: not in C3's TASKS (l. 152 to 164). Not implemented.
- Indiana's per-fold gene lists against the final file's genes: not checked.

### 1b. Cross-gene studentized set and INT5 per donor

(a) `code/scripts/round9_stud_feasibility.py` (89 lines, md5 2cbbe619e083114a7631c1b44ca84db3, identical to the bulk copy `$B/round9/claude_science/S4_stud/round9_stud_feasibility.py`). Single function `main(pq, task, outdir, reps=40)`; methods hcp, own, pergene, xgene (cross-gene: |r| / (sigma_j c_g)) and oracle.

(b) Reported in `docs/round09/00_prep/round09_stud_and_depth.md` section 3 and `results/round9/stud/predictions_scored.md`. Ledger A9 and A10 (`round10_ledger.md` l. 214 to 228) and `results/round10/ledger/round10_ledger_L1_S3.md` l. 86 to 100, which records the correction: 0.878 is INT10's value, and INT5's is 0.9591.

(c) Input: one parquet per task with `y__<gene>`, `f__<gene>`, `donor_id` (l. 24 to 27), the same columns as round 10's HEST final files. The exact parquet paths of round 9's run (Longleaf job 741e07ed) are not recorded. There is no PROVENANCE file in `$B/round9/claude_science/S4_stud/`, and the docs say only "the gated per-spot prediction files". Gene counts in `results/round9/stud/stud_factor_log_resid_sd.csv`: LUNG_XENIUM J = 343, INDIANA_KIDNEY 50, CCRCC 50, with G = 15, 25 and 24.

(d) ALPHA = 0.1 (l. 18); OS = [1, 2, 3, 5, 9, 15] (l. 19); reps default 40 (l. 22, and the run used 40); K = G - 1, all other donors (l. 38); one calibration spot per reference donor (l. 47); kq = ceil((1 - alpha)(K + 1)) (l. 39); block floor 0.1 sigma_j (l. 53); seed `np.random.default_rng(abs(hash(task)) % 2**32)` (l. 35).

(e) Anchors.
- `results/round9/stud/stud_summary.csv` (task, o, method, coverage, frac_inf, hw): `CCRCC,3,hcp,0.9177009851842967,0.0,1.276242608949542`; `CCRCC,3,xgene,0.9155536062995282,0.0,1.2454890719925364`; `CCRCC,3,oracle,0.9167754450760957,0.0,1.1099626308307051`.
- `results/round9/stud/stud_per_donor_coverage.csv` (task, o, method, target, coverage): `CCRCC,3,hcp,INT5,0.3095532544378698`; `CCRCC,3,xgene,INT5,0.9591031276415892`; `CCRCC,3,xgene,INT10,0.8778886363636363`.
- `results/round9/stud/atypical_donor_diagnostics.csv`: `CCRCC,INT5,0.3096,24,1,1,15,22,3.98,1.83,-0.31,-1.13`.
- INT5 in the C3/W3 design (K = 10, all calibration spots, head refit), `w3_by_fold.csv`: `1,CCRCC,shipped,uni_v2,hcp,abs,0.1,0,10,INT5,13,0.4998875772906127,3.547821903497032,3.4080032471026875,1186.0,1.0,3`; `1,CCRCC,shipped,uni_v2,within_full,abs,0.1,9,10,INT5,13,0.9069416595865193,2.773333768173492,2.6364063529149493,1177.0,1.0,60`; `1,CCRCC,shipped,uni_v2,ghcp,abs,0.1,9,10,INT5,13,0.90501246105919,4.932880931364852,4.670760361582052,1177.0,1.0,60`. The fold column in C3 and W3 is the test donor, so INT5's per-donor values exist for every C3/W3 method.

(f) Compute: not recorded. I found no PROVENANCE or sacct record for job 741e07ed in the repository or in `$B/round9/claude_science/S4_stud/`.

(g) Gaps.
- Seeding uses Python's salted `hash(task)` (l. 35). The anchor rows therefore reproduce exactly only if PYTHONHASHSEED matches round 9's run, and that value is not recorded. Otherwise they reproduce only within Monte Carlo error.
- The script's `hcp` is one calibration spot per donor at K = G - 1, a single-subsampling form (l. 47 and 58). It is not C3's `hcp` (all spots, weights 1/((K+1)N_k)). The two INT5 coverages (0.3096 here, 0.4999 in W3) come from different designs.
- Its grid does not match the map: o only 1 to 15, K fixed at G - 1, alpha 0.1 only, and no `within_full` or GHCP.
- The aggregator that wrote stud_summary.csv, stud_per_donor_coverage.csv, stud_per_donor_coverage_sd.csv and atypical_donor_diagnostics.csv is not in code/scripts. A grep for those names over code/scripts returned nothing, and L1_S3 l. 99 says the same for the diagnostics. Round 10's F1 regenerated INT5's diagnostics with `round10_final_runs_f1_donor_diag.py` (plan section F1.4).
- Corpus column names differ (y_log1p__<ENSG>, f_log1p__, y_lognorm__, f_lognorm__; `round10_final_runs_f1_predict.py` l. 15). The script's `y__`/`f__` reader therefore does not apply unchanged to corpus files or to the normalised scale.

### 1c. Adaptive scores: CQR, the locally weighted score, the negative binomial head

(a) `code/scripts/round3_a4_scores.py` (2483 lines, md5 541bca01159e06d971419391415c734c). SCORES (l. 163): abs, scaled, scaled_clip, cqr, nb, nb_conformal; CONFORMAL_SCORES (l. 164).
- The locally weighted score is `scaled` (|y - yhat| / sigmahat, floored) and `scaled_clip` (sigmahat clipped at the calibration set's 1st and 99th percentiles, l. 168 to 169).
- CQR: QuantileRegressor (HiGHS) at quantiles 0.05 and 0.95 (l. 172 to 173) on the PCA-256 features, with score max(qlo - y, y - qhi).
- NB: a Poisson GLM on raw counts with an NB2 moment dispersion. `nb` is the model interval and is not conformal; `nb_conformal` conformalises |F(y) - 0.5|.
- It imports `round3_a0_harness.py` unedited. Round 4 also ran CQR inside GHCP and within_plain on CCRCC (`run_c34.py`, which lives only in the results tree, on A4's 6 genes with one calibration draw).

(b) `docs/round03/i03/exec/round3_final_report.md` and `docs/round03/i03/exec/round3_A3_decisions.md` (A4a). Round 4 C3.4: `docs/round04/i02/conformal/round4_conf_final_report.md` l. 103 and 170 ("held, provisional (6 genes)"). Ledger A5 (`round10_ledger.md` l. 179 to 185).

(c) Inputs: round 3's benchmark task definitions (`$B/round3/task_defs/<TASK>.json`, ten tasks: CCRCC, COAD, HCC, IDC, LUNG, LYMPH_IDC, PAAD, PRAD, READ, SKCM), read through the harness, which refits the head per fold. Raw counts come from `instrumentation/<task>/spots.parquet` (columns sample_id, barcode, gene, count, target). The script does not read prediction files. INDIANA_KIDNEY and LUNG_XENIUM were never run, since they are not round-3 benchmark tasks.

(d) Grids and run arguments.
- Defaults: `--alpha` 0.10 (l. 221); `--alpha-grid` 0.02, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30 (l. 222); `--n-cal-draws` 3 (l. 225); `--designs` random, patient, donor (l. 216); `--cqr-genes` 0 (l. 239); `--cqr-subsample` 20000 (l. 250); `--cqr-timebox-s` 1200 (l. 248); `--nb-genes` 0 (l. 280); `--nb-solver` newton-cholesky (l. 281); `--nb-tol` 1e-6 (l. 288); `--nb-score-tol` 1e-3 (l. 290).
- Values actually run (from `results/round3/A4_scores/PROVENANCE__uni_v2__cqrmain.txt` and `PROVENANCE__uni_v2__mainCCRCC.txt`): `--cqr-genes 6`, `--cqr-subsample 2500`, `--cqr-max-draws 1`, `--cqr-budget-s 2400`, `--nb-genes 12`. The committed tables show `gene_subset` every_kth_6 for the cqr rows and every_kth_16 for the nb rows on CCRCC.

(e) Anchors, `results/round3/A4_scores/a4_scores_by_task.csv` (task, label_set, encoder, design, score, alpha, subset, gene_subset, is_conformal, n_folds, n_cells, coverage, coverage_sd, width_mean, width_median, ...; n_genes and _source given after each row):
  - `CCRCC,shipped,uni_v2,donor,cqr,0.1,full,every_kth_6,True,24,24,0.8792600515797376,0.1444170483058502,2.020097908806086,1.8778604817894675`, n_genes 6, source a4_scores_by_task__uni_v2__cqrmain.csv
  - `CCRCC,shipped,uni_v2,donor,scaled_clip,0.1,full,all,True,24,72,0.873313516136088,0.1304325025514977,2.100504717348102,2.011982455531552`, n_genes 50, mainCCRCC
  - `CCRCC,shipped,uni_v2,donor,nb_conformal,0.1,full,every_kth_16,True,24,72,0.872477797456672,0.1474073014872803,1.714559074179805,1.6251631340501207`, n_genes 16, mainCCRCC
  - `CCRCC,shipped,uni_v2,donor,abs,0.1,full,all,True,24,72,0.8653727123020528,0.1442170586744276,2.0871553941898013,1.9860873215903756`, n_genes 50, mainCCRCC

(f) Compute: uni_v2 cqrmain ran as Slurm 2305540 with wall_seconds 5337 over ten tasks. CCRCC took 2101.2 s, of which CQR was 1809.9 s (`PROVENANCE__uni_v2__cqrmain.txt`). `a4_cqr_fits.csv` has 4824 fit rows. The a4b uni_v2 run has wall_seconds 3823.

(g) Gaps.
- Full gene scope was never run: CQR on 6 of 50 genes with T subsampled to 2500 spots, and NB on 12 to 16 genes.
- The design is round 3's `donor` design with A1's calibration rule (K_median 6 on CCRCC). The sets are pooled split conformal per score, not HCP and not the K x o map. The committed reading was not a comparison "at their own guaranteed coverage": the committed `a4_width_at_coverage.csv` matches levels using test coverage and is labelled a diagnostic.
- Not run on INDIANA_KIDNEY, LUNG_XENIUM, the corpus tasks or the normalised scale. The NB head needs raw counts per gene. The corpus files carry lib_size and n_detected but no per-gene raw count columns, and the HEST final files carry y__ on log1p. I did not check whether raw counts for INDIANA_KIDNEY and LUNG_XENIUM exist in `instrumentation/`.
- `run_c34.py` (the CQR-inside-GHCP diagnostic) is not under code/scripts.

### 1d. Bootstrap standard errors over draws on width margins

`round5_conf_w5_map.py` carries `margin_se` for the simulation source (l. 139) and `margin_mcse` for the GHCP designs (l. 160), and sets `margin_se=np.nan` for real data (l. 181). A grep for bootstrap, mcse and standard error found nothing else in round5_conf_w3.py, round5_conf_w3_merge.py, round5_conf_w3_report.py, round5_conf_w5_numbers.py, round4_conf_c3.py or round4_conf_c3_merge.py.

Gap: no earlier real-data width margin has a bootstrap or Monte Carlo standard error. `w3_by_fold.csv` keeps per-fold means over draws (n_draws 3 or 60), not per-draw rows. The per-draw rows are in the full tables (`w3_full__*.csv.gz` in the W3 unit directories, with columns cal_draw and label_draw per C3's EXTRA_COLS, l. 148).

## 2. F3 item 2, the institution axis

(a) Scripts: none.
- The ledger's entry "Institution axis on the corpus" (`round10_ledger.md` l. 230 to 239) says "Code: none in this repository".
- `grep -il` for leave-one-center, "leave one center" and loco over code/scripts returns only three files. `round10_final_runs_f1_predict.py` writes the center-design predictions. `round7_fedlearn_v2.py` and `round7_fedlearn_v4.py` are point-prediction federation code, with zero matches for hcp, conformal or quantile.
- The HCP kernel available for reuse is C3's `o0_rows` hcp (weights 1/((K+1)N_k), test mass at +inf) or `round4_conf_sim.hcp_q`. Neither has a center level.

(b) Reports.
- F1 report, `docs/round10/i02/final-runs/round10_final_runs_F1_report.md`: l. 84 (30 prediction files, 12 of them center-design), l. 116 to 123 (center-design Pearson), l. 149 (prediction across centers is weak on brain and kidney Visium).
- F1 decisions, `docs/round10/i03/final-runs/round10_final_runs_F1_decisions.md` l. 15: Nicolas chose "Grouped" for breast Xenium. Its `__center_grouped` files are the center-design files of record, and it stays on the center axis.

(c) Inputs.
- Files: `$F/F1/predict/<task>__<enc>/pred__<task>__<enc>__{donor,center}.parquet`, and for breast Xenium `breast__Xenium__<enc>__center_grouped/pred__breast__Xenium__<enc>__center.parquet`.
- Columns (`round10_final_runs_f1_predict.py` l. 15, 142 to 145): sample_id, barcode, donor_id, center_id, fold, lib_size, n_detected, then y_log1p__<g>, f_log1p__<g>, y_lognorm__<g>, f_lognorm__<g>. Genes are Ensembl ids (`genes_top50`, 50 genes). There is no m_std.
- Example provenance, kidney Visium uni_v2: Slurm 8687246, 4 CPUs, 48 GB, start 00:57:53, end 01:23:43, snapshot 3f99228e, script md5 afea0f074edee4c058a301f987025e45. The clone's current copy has md5 cf0b96c4235282b5f2171922f88c1d12, because commit 051fe05f added `--group-centers-by-donor` (F1 report l. 17).

(d) Center counts and donors per center, from `results/round10/final_runs/F1/aggregate/f1_task_list.csv` (columns centers_in, donors, donors_by_center).

| task | centers | donors | donors by center | spots |
|---|---|---|---|---|
| kidney__Visium | 5 | 51 | S0006:24; S0014:3; S0171:1; S0175:22; S0249:1 | 114137 |
| bowel__Visium | 9 | 18 | S0135:1; S0137:2; S0138:3; S0205:1; S0233:1; S0240:1; S0248:1; S0252:1; S0256:7 | 93733 |
| brain__Visium | 6 | 18 | S0032:1; S0166:3; S0173:11; S0231:1; S0235:1; S0251:1 | 123048 |
| breast__Xenium | 5 (4 held-out units) | 17 | S0178:2; S0228:12; S0253:2; S0254:2; S0255:1 | 152994 |
| lung__Xenium | 3 | 17 | S0180:15; S0188:1; S0201:1 | 23990 |
| breast__Spatial_Transcriptomics | 2 | 32 | S0133:8; S0136:24 | 45243 |

- Breast Xenium: S0253 and S0254 hold the same two donors and are held out together, which gives 4 units (F1 decisions l. 15 to 18).
- Lung Xenium and breast ST have fewer than 4 centers and run the donor design only.
- The alpha each count allows follows from HCP's finiteness rule (C3 docstring: infinite exactly when 1/(K+1) > alpha), with K = units - 1 calibration centers. Kidney has 5 units, so alpha >= 0.2. Brain has 6, alpha >= 1/6. Bowel has 9, alpha >= 1/9. Breast Xenium has 4, alpha >= 0.25. This is arithmetic on the stated rule, not a committed result.

(e) Anchors: none exist for HCP over centers. The nearest committed numbers are the center-design point metrics in `f1_predictions.csv`. For example, F1 report l. 123 gives `kidney__Visium | center | 5 | 114137 | 0.123 (-0.082 to 0.337) | 0.089 (-0.244 to 0.393)`, the median Pearson on log1p and on lognorm, uni_v2.

(f) Compute: the breast Xenium grouped center-design jobs took under 3 minutes each (F1 report l. 17). Kidney Visium's donor and center designs together took 25 min 50 s in one job (provenance above), at 22.7 s per center fold (`pred_summary__kidney__Visium__uni_v2__center.json`, seconds_per_fold).

(g) Gaps.
- There is no HCP-over-centers or leave-one-center-out conformal code anywhere in the repository.
- No earlier document fixes which residuals the comparator "donor-level HCP pooled across centers" uses: donor-design or center-design predictions, and whether the target center's own donors may calibrate. The brief and the ledger only name it.
- Two kidney centers (S0171, S0249) and several bowel and brain centers hold one donor each, so center-level and donor-level weights differ sharply. No earlier run handled single-donor centers.
- Corpus-specific: no m_std, Ensembl gene names, and two scale-specific column prefixes.

## 3. Prediction P10.3

- Level: round 5's map (W3 part 1, `fig_w3_map.png`) is at alpha 0.1, K = 10 (report l. 101).
- Code path: `round5_conf_w3.py --part 1` over `round4_conf_c3.py`, comparing `hcp` (o = 0) with `within_full`, and with `within_plain` on Indiana. o is from P1_O, where 9, 10, 12 and 15 are present.
- The committed uni_v2 values are per fold, in `w3_by_fold.csv` column `width_median` (anchors in 1a). Each fold holds out one donor (`_ccrcc_specs` via `round3_a4b_hcp.donor_folds`, and `_a4b_like_specs` with "one held-out donor unit per fold", `round4_conf_c3.py` l. 609 to 613), and the `fold` column carries that donor's id (INT1, INT5, lungXen_THD0008), so per fold here means per held-out donor. The map file `w3_map_by_task.csv` carries only width_mean averaged over encoders (merge l. 39 to 41). No committed table gives a median width over folds (that is, over held-out donors) or genes for uni_v2 at these cells.
- Encoder-mean width_mean at K = 10, alpha 0.1 (`w3_map_by_task.csv`):
  - CCRCC: hcp 4.10936740781251; within_full at o = 9 2.0807756206756403.
  - LUNG_XENIUM: hcp 4.542210546834191; within_full at o = 9 2.7301235249989695.
  - INDIANA_KIDNEY: within_full at o = 9 1.8695958245841393 against within_plain 1.8344622234763293; at o = 15, 2.074186215794269 against 2.0639563227497297.
- Gaps: "median width" needs a definition. C3's `width_median` is the median of the finite spot-gene widths within a fold (C3 docstring, l. 15), and no median over folds is committed. The prediction cannot be scored on the final prediction files unchanged (section 1a).

## 4. Prediction FR8

- Kidney Visium has 5 center units (S0006 with 24 donors, S0014 3, S0171 1, S0175 22, S0249 1), so alpha = 0.2 is the smallest level at which HCP over centers (K = 4) is finite.
- There is no code and no anchor (section 2). The center-design predictions on kidney Visium have median Pearson 0.123 (log1p, uni_v2).

## 5. Read-only actions taken

All Longleaf calls used ls, cat, sed, grep, awk, head, wc, md5sum and zcat on files under the clone and `$B`. One command started with `python3 -c 1 2>/dev/null`, a no-op left in a shell line by mistake. It read and wrote nothing. Nothing was written on Longleaf, and no job and no git command were run.
