# Round 10, track `final-runs`, gate F1 report

*Written on 10 November 2026 by the second session of track `final-runs` (frame `862fd1a1-1068-44b1-a365-9bc7cae686fe`), from the track plan `docs/round10/tracks/final-runs/round10_final_runs_plan.md` and the brief `docs/round10/i01/final-runs/round10_final_runs_brief.md`. Every number below is read from the file named beside it. The aggregate tables are in `results/round10/final_runs/F1/aggregate/`, written by `code/scripts/round10_final_runs_f1_aggregate.py`, and the bulk outputs stay on Longleaf under `/work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/`.*

## 1. Stage and status

Stage F1 (setup, anchors and data) is complete, and every F1 item of the brief has an output. The estimator module passes its acceptance, both anchors reproduce exactly, FR1 holds on all four tasks, and held-out prediction files exist for six proposed corpus tasks, with D12 on each and D13 on kidney Visium. The gate asks Nicolas to confirm the task list and the audit's exclusions and to decide the point on the morphology covariate (section 7). No stop condition of the brief was met.

## 2. What was run

All jobs ran on Longleaf through the submission route, which names jobs `claude-science-<uuid8>` and so identifies them by Slurm id. Every job appears in `results/round10/final_runs/job_ledger.csv` with its partition, node, submit, start and end times, state, wall time, requested memory, peak memory and commit. Every job that ran through Slurm landed on `spill`, the general partition's overflow.

The F1.4c and F1.4 units of this session were these.

- Held-out predictions, `code/scripts/round10_final_runs_f1_predict.py` (md5 `afea0f074edee4c058a301f987025e45` at commit `3f99228e`) with `code/scripts/round3_a0_harness.py` (md5 `0ad7ae8efe554c1f285e5f384a9fb7f5`). These were 15 jobs for kidney, bowel and brain Visium and breast and lung Xenium, three encoders each, Slurm `8687246` to `8687547`. They were submitted by the first session around 20:10 UTC on 9 November, started between 05:57 and 07:40 UTC on 10 November, and ran 2 to 43 minutes each, with a MaxRSS of at most 12283016 KB (job ledger). Three more jobs did breast ST, Slurm `8738506`, `8738508` and `8738513`, taking 8 to 10 minutes each.
- Breast ST's task definition, `code/scripts/round10_final_runs_f1_task_build.py` (md5 `0bff32060d55f5c490eb7b461d3427f3`, commit `10d578c5`), Slurm `8688100`, 105 s.
- Breast Xenium's center design rerun with donor-linked centers held out together, the same predict script with a new flag (md5 `cf0b96c4235282b5f2171922f88c1d12`, commit `051fe05f`), Slurm `8760597`, `8760599` and `8760603`, under 3 minutes each.
- D12 and D13 on the 18 donor-design files, `code/scripts/round10_final_runs_f1_donor_diag.py` (md5 `bd1396e22455d0081c08d8f19984610e`, commit `051fe05f` snapshot), Slurm `8760871`, 47 s.
- The aggregation, `round10_final_runs_f1_aggregate.py` (md5 `44b80ada973f54699d7b22e414958045`, commit `fd110920`), Slurm `8761194`.
- The provenance index, `code/scripts/round10_final_runs_provenance_index.py` (commit `5e381147`). Its first run reported two false mismatches from a parsing bug, which was fixed before the second run (section 7).

The earlier F1 units (the module check, both anchors, the inflation check, the registry counts, the audit inputs and verdicts, the prediction anchor and the CCRCC diagnostics) are in the plan's section 4 with their Slurm ids and commits.

The donor-label audit used four sub-agents of the first session, `Kidney+lung` (frame `a64e3562-6e9e-425a-aa3d-148233168a84`), `Brain` (`20f0c6ea-bfee-4084-9443-3a6883b7a69a`), `Bowel` (`6926c04e-080a-4d26-939a-42ef2c632449`) and `Breast` (`8e126741-416e-4824-87a4-9ac2e1d6bf28`), under one written brief kept in that session's transcript. They gathered evidence and ran no job and no git. The verdicts were assigned by the lead (plan, section 4, F1.4). This session used no sub-agents.

**Provenance.** The index `results/round10/final_runs/F1/provenance_index.csv` covers the 42 `PROVENANCE*.txt` files under `F1/`. Every recorded snapshot commit is an ancestor of the gate commit, and all 103 recorded script md5s equal the md5 of the script at that commit. This includes the earlier rounds' code reproduced by the anchors.

## 3. Acceptance checks and exit items

**F1.1, the estimator module** (`results/round10/final_runs/F1/aggregate/f1_module.csv`).

- In part 1, 180 of 180 printed fields of the 30 enumeration rows agree, with largest absolute difference 4.99e-07 at the printed six decimals.
- In part 2, 2100 of 2100 draw-for-draw checks of `FIX1`, `W_within` and `FOLD` on CCRCC's 50 genes agree, and 42 of 42 summary rows equal round 9's.
- In part 3, `bh`, `bh_t` and `bh_t_fpc` agree with round 7 in 180 of 180 checks, with largest difference 0.

Form C for regime B is checked by exact enumeration on toy populations (plan, section 4, F1.1, part 4).

**F1.2, the anchors** (`results/round10/final_runs/F1/aggregate/f1_anchors.csv`). The pass rule, written before the runs, asked for exact agreement under the same seed and code, else agreement within 3 Monte Carlo standard errors.

- Round 5's cell (CCRCC, `uni_v2`, $\theta_3$, $G = 24$, 8 labelled donors, D0, `c_crossfit_design`, `textbook_t|fpc|lin|xf`, `n_sub` 2000) gives `coverage_median` 0.85775 and `width_median` 0.113623215193696, equal to the file.
- Round 7's cell (ACS_STATES, $\theta_3$, 8 labelled clusters, $p_a = 0.01$, `D2_rej_t`) gives coverage 0.879 and `wr_D0cl` 0.5512905600863858 against the file's 0.5512905601, which stores 10 significant digits.

Both anchors pass exactly, with all recorded scripts matching and all compared tables identical.

**F1.3, the inflation check and FR1** (`results/round10/final_runs/F1/aggregate/f1_fr1.csv`, all $n_L$ in `f1_fr1_all_n.csv`). The arms `R5`, `W_within` and `FIX1` reproduce round 9's summary rows exactly (119 of 119 on HEST and 42 of 42 on ACS, plan section 4, F1.3).

| task | $n_L$ | median width `R5_lin` | median width `W_within` | ratio | per-gene ratio, median (10% to 90%) | ratio without the term (`R5`) | coverage `R5_lin` | coverage `W_within` |
|---|---|---|---|---|---|---|---|---|
| ACS_STATES | 8 | 0.1137 | 0.1158 | 0.982 | 0.982 (0.982 to 0.982) | 16.765 | 0.891 | 0.891 |
| CCRCC | 8 | 0.4584 | 0.4643 | 0.987 | 0.984 (0.982 to 0.990) | 1.085 | 0.839 | 0.837 |
| INDIANA_KIDNEY | 8 | 0.1834 | 0.1862 | 0.985 | 0.985 (0.982 to 0.987) | 1.210 | 0.863 | 0.863 |
| LUNG_XENIUM | 8 | 0.3026 | 0.3013 | 1.004 | 1.004 (0.994 to 1.011) | 2.144 | 0.890 | 0.891 |

**F1.4, the data stage.** The candidate groups and their counts are tabulated over the registry (`results/round10/final_runs/F1/data_registry/f1_data_groups.csv`) and over the audit (`results/round10/final_runs/F1/aggregate/f1_task_list.csv`).

- Of 340 registry samples in the seven groups with at least 10 source donor labels, 278 are kept by the audit. Their verdicts are verified for 160, naming for 89, record audit for 28 and single section for 1. Left out are 38 unverifiable samples, 6 duplicate measurements, 6 sections whose donor split was not resolved, 6 kidney organoid samples (not donor tissue), 4 pooled-donor sections and 2 sections carrying a second donor's tissue (`results/round10/final_runs/F1/aggregate/f1_task_list.csv`).

| task | samples, registry | samples kept | donors, corpus labels | donors, audited | centers kept | verified | naming | record audit | single section |
|---|---|---|---|---|---|---|---|---|---|
| kidney Visium | 62 | 52 | 50 | 51 | 5 | 28 | 0 | 24 | 0 |
| breast Spatial Transcriptomics | 108 | 108 | 32 | 32 | 2 | 36 | 72 | 0 | 0 |
| bowel Visium | 73 | 34 | 16 | 18 | 9 | 29 | 1 | 4 | 0 |
| brain Visium | 42 | 34 | 19 | 18 | 6 | 20 | 14 | 0 | 0 |
| breast Xenium | 21 | 21 | 11 | 17 | 5 | 21 | 0 | 0 | 0 |
| lung Xenium | 24 | 22 | 22 | 17 | 3 | 22 | 0 | 0 | 0 |
| breast Visium | 10 | 7 | 10 | 6 | 7 | 4 | 2 | 0 | 1 |

- The corpus's directories carry the stamps of the federated project's data track, project `proj_179f7d052fd3`, frame `25143d4e-106b-450b-974c-e169a1aec08a` (`results/round10/final_runs/F1/data_registry/f1_data_stamps.json`), so they are a sibling's outputs. The brief names the corpus as this track's input, and it is only read, which needs no question (rules, section 4).
- Breast Visium's 7 kept samples come from 6 donors, below the 10-donor criterion, so the task is dropped. The six proposed tasks are kidney Visium, breast ST, bowel Visium, brain Visium, breast Xenium and lung Xenium (`results/round10/final_runs/F1/aggregate/f1_task_list.csv`).
- Licences per group, over the registry's samples before the audit (`results/round10/final_runs/F1/data_registry/f1_data_groups.csv`):

| group | samples in the registry | no licence | marked internal | other licence |
|---|---|---|---|---|
| kidney Visium | 62 | 8 | 24 | 30 |
| breast Spatial Transcriptomics | 108 | 4 | 0 | 104 |
| bowel Visium | 73 | 0 | 0 | 73 |
| brain Visium | 42 | 31 | 0 | 11 |
| breast Xenium | 21 | 3 | 0 | 18 |
| lung Xenium | 24 | 20 | 0 | 4 |
| breast Visium | 10 | 1 | 0 | 9 |

- Kidney Visium against the HEST tasks (`results/round10/final_runs/F1/data_registry/f1_data_registry_summary.json`, per sample in `f1_data_hest_match.csv`). CCRCC's 24 samples are all in the corpus and their donor partitions agree. INDIANA_KIDNEY's 26 samples are all in the corpus, but the partitions disagree because three samples without a source label share one corpus donor where the audited labels give three. Of kidney Visium's samples, 50 belong to a HEST task. The audited donor map is used throughout, so no donor is counted twice.
- Breast ST has no corpus task file, so its gene set is built by the corpus's rule. Rebuilt from kidney Visium's 62 members by the same rule, the rule returns kidney's committed `genes_top50` in the same order and its 17351-gene intersection exactly. Breast ST's file holds 108 samples from 2 centers, a common panel of 10495 genes and its 50 top genes, with embeddings for every sample (`/work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F1/task_build_breast_ST/task_build_summary.json`, Slurm `8688100`).
- **Held-out prediction files** (`results/round10/final_runs/F1/aggregate/f1_predictions.csv`). There are 30 files, 18 with the donor held out and 12 with the center held out. The donor-design files cover six tasks and three encoders. The center-design files cover kidney, bowel and brain Visium and breast Xenium, the four tasks with at least 4 centers. In all 30 files every spot is predicted once, and the number of folds equals the number of donors, centers or center groups. The prediction-file anchor holds. On CCRCC's subset with round 3's genes the median spot-level Pearson is 0.2895 against round 3's 0.2932, a difference of -0.0037 against the stated bound of 0.01 (`results/round10/final_runs/F1/aggregate/f1_aggregate_log.txt`).
- **D12** (`results/round10/final_runs/F1/aggregate/f1_d12.csv`). All 18 donor-design files have D12 on both scales, 36 rows, and each median equals the diagnostics script's own medians file.
- **D13 and INT5 on kidney Visium** (`results/round10/final_runs/F1/aggregate/f1_d13_kidney.csv`). 51 donors per encoder, regenerated from committed code.

## 4. Variables that differ between the arms of each comparison

- **FR1, `R5_lin` against `W_within`.** The estimator's code path differs. `R5_lin` is round 5's `design_whole_clusters(..., lin=True, xf=True)`, which adds round 4's term $(\lambda_{(g)} - c_U)\bar F$ to each contribution, uses round 5's coefficient rule, and uses round 5's linearised variance with its $t$ quantile. `W_within` is the two-fold form in Mickey's arrangement with the within-half variance. The tasks, genes, draws, $n_L$, seed and nominal level are the same. `R5` differs from `R5_lin` only by `lin=False`.
- **Prediction-file anchor, corpus against round 3 on CCRCC.** The patches differ (HEST-1k's release against HEST-bench's), and so do the loader, the gene identifiers (Ensembl ids mapped from round 3's symbols) and the spots that survive the join. The 24 donors and their labels, the head (`intercept_f64`), the leave-one-donor-out folds, the encoder and the scale are the same.
- **Donor design against center design, within a task.** The held-out unit differs (a donor, or a center or group of centers), and with it the training set's size and composition. The task, spots, genes, encoder, head and scales are the same.
- **Across tasks and encoders.** The rows of the prediction and D12 tables differ in platform, organ, number of donors, spots per donor, gene set and encoder. They are reported as the files' values, and no effect is named from them.
- **INT5 on kidney Visium against INT5 on CCRCC.** The reference set of donors differs (51 against 24). The donor's spots, raw counts and the definitions are the same.

## 5. Predictions against outcomes

| prediction | gate | outcome | verdict |
|---|---|---|---|
| FR1. With round 4's `lin` term, round 5's interval has median width within 1.15 times that of `W_within` at 8 labelled clusters, on every HEST task and on ACS by state | F1 | ratios 0.982 to 1.004 on the four tasks (`results/round10/final_runs/F1/aggregate/f1_fr1.csv`) | held |
| The two anchors agree exactly under the same seed and code, or within 3 Monte Carlo standard errors | F1 | both exact (`results/round10/final_runs/F1/aggregate/f1_anchors.csv`) | held |
| On CCRCC's subset, the corpus prediction file's median spot-level Pearson on $\log(1 + y)$ differs from round 3's by at most 0.01 | F1 | difference -0.0037 (`results/round10/final_runs/F1/aggregate/f1_aggregate_log.txt`) | held |
| Breast ST's gene rule, rebuilt on kidney Visium, returns kidney's committed gene list in order and its intersection | F1 | both equal (`task_build_summary.json`, Slurm `8688100`) | held |
| P10.1, P10.3, FR2 to FR8 | F2, F3 | not run at F1 | not tested |

The P10.1 references were named before F2 in the plan's section 4a.

## 6. Results

**FR1 and the variance of rounds 5 to 7.** With the `lin` term, round 5's interval is as wide as Williams' form with the within-half variance at 8 labelled clusters. The ratio of median widths is 0.982 to 1.004 across the four tasks, and per-gene ratios have their 10% to 90% range inside 0.982 to 1.011. Coverage agrees within 0.002. Without the term, the ratio is 1.085 on CCRCC, 1.210 on INDIANA_KIDNEY, 2.144 on LUNG_XENIUM and 16.765 on ACS by state (table in section 3). So the intervals reported in rounds 5 to 7, whose label `textbook_t|fpc|lin|xf` names the term, did not carry the level-dependent variance that round 9 measured. Round 9's `R5` arm called round 5's code without the term. Without it, each contribution keeps a piece that scales with the level $\bar F$ of the predictions, which is what round 9 measured as width growing with the level (`docs/round10/i01/ledger/round10_ledger_L1_S4.md`, section 0). The file would contradict this if `R5_lin`'s ratio departed from 1 at another $n_L$, and `f1_fr1_all_n.csv` holds every $n_L$ for that check. This bears on P10.1, which predicts a coverage drop of 0.02 to 0.05 from the corrected variance. F2 scores it.

**Prediction files, `uni_v2`** (`results/round10/final_runs/F1/aggregate/f1_predictions.csv`, which also has `hoptimus0` and `resnet50`). The figures are the median over the 50 genes of the spot-level Pearson between held-out prediction and observation, with the 10% and 90% quantiles over genes.

| task | design | folds | spots | Pearson $\log(1+y)$, median (10% to 90%) | Pearson $\log(1+10^4y/n)$, median (10% to 90%) |
|---|---|---|---|---|---|
| bowel__Visium | center | 9 | 93733 | 0.418 (0.269 to 0.580) | 0.298 (0.133 to 0.500) |
| bowel__Visium | donor | 18 | 93733 | 0.511 (0.374 to 0.650) | 0.398 (0.147 to 0.544) |
| brain__Visium | center | 6 | 123048 | 0.022 (-0.113 to 0.153) | -0.062 (-0.224 to 0.063) |
| brain__Visium | donor | 18 | 123048 | 0.249 (0.027 to 0.540) | 0.193 (0.019 to 0.481) |
| breast__Spatial_Transcriptomics | donor | 32 | 45243 | 0.388 (0.255 to 0.493) | 0.254 (0.119 to 0.398) |
| breast__Xenium | center | 4 | 152994 | 0.686 (0.445 to 0.854) | 0.521 (0.201 to 0.725) |
| breast__Xenium | donor | 17 | 152994 | 0.746 (0.528 to 0.891) | 0.629 (0.351 to 0.774) |
| kidney__Visium | center | 5 | 114137 | 0.123 (-0.082 to 0.337) | 0.089 (-0.244 to 0.393) |
| kidney__Visium | donor | 51 | 114137 | 0.471 (0.371 to 0.672) | 0.392 (0.167 to 0.676) |
| lung__Xenium | donor | 17 | 23990 | 0.634 (0.474 to 0.730) | 0.537 (0.288 to 0.676) |

Across the three encoders, holding the donor out, the median Pearson on $\log(1 + y)$ ranges from 0.140 (brain Visium, `hoptimus0`) to 0.746 (breast Xenium, `uni_v2`). `resnet50` is lowest on five of the six tasks. Holding the center out lowers the median on every task where it runs. The drop is largest on brain Visium, where it falls to -0.123 to 0.022 across encoders, and on kidney Visium, where it falls to 0.004 to 0.123 (`results/round10/final_runs/F1/aggregate/f1_predictions.csv`). It is smallest on breast Xenium and bowel Visium.

**D12, the leave-one-donor-out $R^2$ of donor means against the leave-one-out constant, `uni_v2`** (`results/round10/final_runs/F1/aggregate/f1_d12.csv`, which also has the other encoders, round 9's full-mean baseline and the raw-prediction form). The figures are the median over genes with the 10% and 90% quantiles.

| task | donors $G$ | $\log(1+y)$, median (10% to 90%) | $\log(1+10^4y/n)$, median (10% to 90%) |
|---|---|---|---|
| bowel__Visium | 18 | 0.222 (0.015 to 0.527) | 0.238 (-0.090 to 0.554) |
| brain__Visium | 18 | 0.232 (-0.184 to 0.620) | 0.207 (-0.202 to 0.662) |
| breast__Spatial_Transcriptomics | 32 | 0.300 (0.014 to 0.497) | 0.189 (-0.044 to 0.457) |
| breast__Xenium | 17 | 0.509 (-0.056 to 0.750) | 0.356 (-0.031 to 0.711) |
| kidney__Visium | 51 | 0.382 (0.205 to 0.644) | 0.349 (0.097 to 0.717) |
| lung__Xenium | 17 | 0.190 (-0.079 to 0.646) | 0.225 (-0.130 to 0.773) |

Every task's median is positive under `uni_v2` on both scales. On $\log(1 + y)$ the 10% quantile is below zero on brain Visium, breast Xenium and lung Xenium. With `resnet50` the median is negative on bowel Visium on both scales (-0.085 on $\log(1 + y)$ and -0.052 on $\log(1 + 10^4 y/n)$, `results/round10/final_runs/F1/aggregate/f1_d12.csv`).

**D13 and INT5 on kidney Visium** (`results/round10/final_runs/F1/aggregate/f1_d13_kidney.csv`). Among kidney Visium's 51 donors, INT5 ranks first on average expression ($z$ 3.255), first on median raw library size per spot (44594.5, $z$ 5.559, against the next donor's 17979) and first on median detected genes per spot (8366.5, $z$ 3.735), under every encoder. On residual scale it ranks first under `uni_v2` and second under the other two. On prediction outlyingness it ranks 11th, 6th and 5th under `uni_v2`, `hoptimus0` and `resnet50`. On embedding outlyingness it ranks 17th, computed under `uni_v2` only. Within CCRCC's 24 donors its library-size $z$ was 3.94 (`results/round10/final_runs/F1/diagnostics/d13_donor_diagnostics__corpus_CCRCC_uni_v2.csv`). The larger reference set leaves it as the most extreme donor on library size by a wider margin.

## 7. Discrepancies, open questions and escalations

1. **No morphology covariate on the corpus.** The HEST tasks' $\theta_2$ and $\theta_3$ use `frac_neoplastic` and `m_std` from round 3's nuclear instrumentation, which the corpus does not carry. As things stand only $\theta_1$ can be formed on the corpus tasks. There are three options for Nicolas. (a) Run the corpus tasks for $\theta_1$ only, as F2's illustration estimand, and keep $\theta_2$ and $\theta_3$ on the three HEST tasks and ACS. (b) Extend round 3's nuclear instrumentation to the corpus's patches, which is new computation on data already on Longleaf. (c) Define a corpus covariate from what the corpus carries, which would need the literature-first step of the brief's section 7. Nothing has been built for this.
2. **The task list and the audit's exclusions**, for confirmation together. Left out are the pooled-donor sections NCBI563, NCBI564, NCBI885 and NCBI886 and the sections NCBI565 and NCBI566, which carry a second donor's tissue. So are the six kidney organoid samples of S0135, the six RRST brain sections whose donor split was not resolved, and six duplicate measurements. The 38 unverifiable samples, all in bowel Visium, are left out too. The plan records 38 of COLON MAP's 41 sections as having no donor in the record. 89 samples rest on naming evidence only (provisional) and are kept. Two flags are kept. INT4 and INT24 share the tumour code c_2 (the 24-donor set is primary and the merged set the sensitivity row), and NCBI599 may be the donor of NCBI714 (not merged).
3. **Breast Xenium's center design, a method choice made at this stage.** Studies S0253 and S0254 hold sections of the same two donors. The leave-one-center-out run therefore stopped on the script's guard, which refuses a fold with a donor on both sides, in all three encoders (Slurm `8687463`, `8687469`, `8687541`; their donor designs had completed and passed). The rerun holds out together the centers that share a donor, giving 4 held-out units (S0178, S0228, S0253 with S0254, and S0255) from 5 centers, and every fold is donor-disjoint. The alternative is the donor design only, as for lung Xenium and breast ST. Nicolas may prefer it.
4. **Prediction across centers is weak on brain and kidney Visium** (section 6). Any F2 or F3 analysis on the center axis, FR8 among them, will rest on center-held-out predictions whose median gene has a Pearson near zero on brain Visium.
5. **Round 5's regime B variance for $\theta_3$** under-estimates in the toy enumeration, with expectation 0.76 to 0.80 of the true variance (plan, section 4, F1.1, part 4). F2's regime B arm measures this on the real tasks, and nothing was changed for it.
6. **FR1 and P10.1.** The intervals of rounds 5 to 7 carried no level-dependent inflation (section 6). This makes P10.1's predicted coverage drop of 0.02 to 0.05 less likely, and F2 scores it as written.
7. **Queue.** The 15 prediction jobs pended for 9.8 to 11.5 hours at priority 239 on `spill`, and the four-hour notice was given in the session on 10 November at 00:15 UTC. Breast ST's three smaller jobs (32G and 2 hours against 48G and 4 hours), submitted about 5.6 hours later, started at 05:52 UTC, five minutes before the first of the others, so the wait looks like the queue's and not the request's.
8. **The provenance index's first run** (harness job `23dc7aea`) reported two false mismatches. The parser cut the scripts section at the word `inputs` inside the name `round10_final_runs_f1_audit_inputs.py`. Fixed in commit `5e381147`, after which the second run finds every md5 matching.
9. **This seat.** Harvested job files are readable here only through the file reader, not from the kernels, so every number in this report comes from tables written on Longleaf by committed scripts.

## 8. What was not checked

- Spot-level identity between the corpus's patches and HEST-bench's, which is not expected (data card, section 6). Only the gene-level summary of the prediction anchor was compared.
- The 89 samples with naming evidence and COLON MAP's unresolved sections were not checked beyond the audit's sources. Some of those sources were read only through search snippets (plan, section 4, F1.4b).
- Center-design files on lung Xenium (3 centers) and breast ST (2 centers), which fall below the 4-center rule and were not run.
- Embedding outlyingness under `hoptimus0` and `resnet50`, and D13 outside kidney Visium beyond the files the diagnostics script wrote (`d13_donor_diagnostics__<task>__<encoder>.csv` on Longleaf), which are not read here.
- Licences after the audit's exclusions. The licence counts above are over the registry's samples.

## 9. Proposed next step

After Nicolas confirms the six tasks and the exclusions, decides the morphology point and says which center design breast Xenium uses, the session writes F2's methods into the plan. These cover the design-simulation driver, the switch rule of decisions section 1.1, the arms of brief F2 on every task, encoder, scale and estimand, and the P10.1 cells named in section 4a. Then it runs F2. His reply goes into `docs/round10/i03/final-runs/` as the next interval's decision file before any F2 work.
