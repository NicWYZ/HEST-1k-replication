# Round 9, methods note

*Written when the record was reduced, November 2026. It holds, word for word, the parts of the two track briefs of round 9 that no kept document states. The briefs are at tag `record-full-2026-11` (`round09_fewcluster_brief.md` (at tag `record-full-2026-11`), `round09_newtopic_brief.md` (at tag `record-full-2026-11`)). What stands now: `docs/round09/README.md`.*

## 1. Prior art given to track fewcluster

From the fewcluster brief, section 3. It is the starting list of known results behind the plan (`i01/fewcluster/round09_fewcluster_plan.md`) and the frontier, tuned, stratified and critical-value notes, which cite these works rather than claim them.

Treat these as prior art, cite them and do not re-derive them as results. The verdicts and logs are in `results/round9/scan/`, and the round 8 note covers the survey-sampling side.

- The setting is two-stage survey sampling, and PPI with a fixed coefficient is the difference estimator (Mozer, arXiv:2603.19160). The regression estimator on cluster values, its design variance and the finite-population factor are Cochran's. The exactly unbiased split-sample regression estimator is Williams (1961), with the design-based cross-fitting papers of 2025 and 2026 (round 8 note, section 3.2).
- Small-sample corrections. The $t$ reference with $n - 1$ degrees of freedom, CR2 and Bell and McCaffrey (2002), Satterthwaite degrees of freedom, and Imbens and Kolesár (2016). Cornish-Fisher refinements of cluster-robust inference with about ten clusters (Gafarov and Ura, arXiv:2603.24786).
- Randomization and resampling with few clusters. Sign-change tests under approximate symmetry (Canay, Romano and Shaikh 2017), the wild bootstrap with few large clusters (Canay, Santos and Shaikh 2021), Ibragimov and Müller (2010, 2016), and Hagemann's permutation tests. Pseudo-population bootstraps with design replay (Booth, Butler and Hall 1994; Wang, Peng and Kim 2022; Cohen and Fogarty 2022 for rejective designs).
- Balanced and rejective selection of clusters and its interval (Yang, Qu and Li, JASA 2023, appendix A5).
- Cluster-robust PPI (Broska and Howes, arXiv:2610.09601), which names a small-sample correction and the wild cluster bootstrap as future work.
- Classical skewness corrections (Johnson's modified $t$, Hall's transformation, Edgeworth expansions under sampling without replacement), Cochran's rule for sample size under skewness, and finite-population Berry-Esseen bounds. These were cited from memory by the checkers and need checking `[verify]`.

## 2. The prediction files and data in hand

From the fewcluster brief, section 5. It describes the inputs of the scripts `code/scripts/round9_fewcluster_*`.

- **Data.** HEST-1k is gated and stays on Longleaf under `/work/users/w/e/weiyang/hest_replication` (`MANIFEST.md`). The per-spot prediction files are `results/round3/B1_ppi/b1_predictions__<TASK>__<encoder>.parquet` for CCRCC and the other benchmark tasks, `results/round4/ppi/Q2_theory/predictions/` for LUNG_XENIUM and the two ACS tasks, and `results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/` for INDIANA_KIDNEY. Their columns are `y__<gene>`, `f__<gene>`, `donor_id`, `sample_id`, `barcode` and `m_std`. Donor-level aggregates from round 9 are under `results/round9/claude_science/` on Longleaf. Only aggregates enter the repository. ACS PUMS 2018 is also at `~/hest-1k/acs_pums2018` on Nicolas's Mac. It is not gated, and its states and PUMAs give clusters at G = 51 and G = 265.

From the newtopic brief, section 4. It describes the inputs of the newtopic diagnostics (`code/scripts/round9_newtopic_n3_diagnostics.py`) and of the preparation's scripts. The interval 1 report of track newtopic corrects it: the HEST Xenium files on Longleaf are pseudo-spot binnings, and the cell-level transcripts were not downloaded (`i01/newtopic/round09_newtopic_i01_report.md`).

All HEST-1k data are gated and stay on Longleaf under `/work/users/w/e/weiyang/hest_replication` (`MANIFEST.md`, `bench_data/INVENTORY.md`). Only aggregates enter the repository.

- **HEST-Bench snapshot,** `bench_data/`, ten tasks (CCRCC, COAD, HCC, IDC, LUNG, LYMPH_IDC, PAAD, PRAD, READ, SKCM) with H&E patches, expression and the benchmark's patient splits.
- **Patch embeddings** from ten encoders (conch_v1, conch_v15, ctranspath, gigapath, hoptimus0, hoptimus1, phikon, resnet50, uni_v1, uni_v2) under `embeddings/<TASK>/<encoder>/<sample>.h5`, and for the extension sets under `embeddings_ext/` (kidney_visium_cell, lung_xenium, institution_breast_xenium).
- **Extension sets** under `hest_ext/`, with Visium kidney (INDIANA_KIDNEY, 25 donors) and Xenium lung (LUNG_XENIUM, 15 donors, 343 genes) as tasks defined in rounds 3 and 4.
- **Per-spot leave-donor-out predictions** with labels, for CCRCC, IDC, LYMPH_IDC, PRAD, INDIANA_KIDNEY and LUNG_XENIUM from three encoders. These are `b1_predictions__<TASK>__<encoder>.parquet` under `results/round3/B1_ppi/` and `results/round4/ppi/Q2_theory/predictions*/`. They also carry nuclear morphology (`area_mean`, `m_std`) and a neoplastic fraction per spot.
- **Morphology tables** under `instrumentation/`, and the HEST-1k release metadata. The project's on-disk table is v1_1_0, which the round 3 inventory (`results/round3/D0_inventory/hest_inventory.csv`) covers.
- **Raw counts** in each sample's `h5ad` (paths in the task definitions, for example `results/round4/data/P5_task/LUNG_XENIUM.json`).
- **ACS PUMS 2018,** all columns, at `~/hest-1k/acs_pums2018` on Nicolas's Mac. It is not gated.
- **Round 9's donor-level aggregates** under `results/round9/claude_science/` on Longleaf. These are donor by gene means, variances and covariances of labels and predictions, donor-mean embeddings, and normalized summaries.
