# HEST-1k replication and instrumentation — final stage report

*Generated 2026-09-15 22:39 from the saved result tables. Structure follows handoff Section 9. Every number below traces to a committed file; paths are given relative to the repository root and are live on `origin/main`.*

**Repository:** `NicWYZ/HEST-1k-replication` · commit `ff98418` · 3,906 tracked files

---

## 0. How to audit this

| to check | read |
|---|---|
| headline encoder numbers | [`reports/results_encoder.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/results_encoder.csv) |
| per-task numbers | [`reports/results_task.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/results_task.csv) (340 rows) |
| per-gene numbers | [`reports/results_gene.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/results_gene.csv) (17,000 rows) |
| per-fold numbers | [`reports/results_split.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/results_split.csv) |
| paper/leaderboard comparison | [`reports/discrepancy_table_v2.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/discrepancy_table_v2.csv) (238 rows) |
| the aggregation logic itself | [`code/scripts/aggregate_results.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/aggregate_results.py) |
| benchmark data inventory | [`bench_data/INVENTORY.md`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/bench_data/INVENTORY.md) |
| environment / reproduction | [`env/REBUILD.md`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/env/REBUILD.md), [`env/requirements.lock`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/env/requirements.lock) |
| file-level provenance | [`MANIFEST.md`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/MANIFEST.md) (998 hashed dumps, 2,776 files, 57.9 GB) |

---

## 1. Stage and status

| handoff stage | status | primary evidence |
|---|---|---|
| 0 · access and environment | complete | [`env/`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/env), [`env/ENV_NOTES.txt`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/env/ENV_NOTES.txt) |
| 1 · benchmark data and inventory | complete, 1 documented deviation | [`bench_data/INVENTORY.md`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/bench_data/INVENTORY.md) |
| 2 · faithful runs, 4 heads | complete for 11 encoders × 4 heads; hoptimus1 (12th, newly approved) 1 of 10 tasks done | [`reports/results_encoder.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/results_encoder.csv) |
| 3 · verification vs paper and leaderboard | complete | [`reports/replication_memo_v2.md`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/replication_memo_v2.md) |
| 4a · joined prediction table + metadata | complete | [`instrumentation/stage4a_integrity.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/stage4a_integrity.csv) |
| 4b · split-design decomposition | complete | [`instrumentation/split_decomposition.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/split_decomposition.csv) |
| 4c · count diagnostics | complete | [`instrumentation/count_diagnostics_v2.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/count_diagnostics_v2.csv) |
| 4d · site-predictability probes | complete | [`instrumentation/site_probe_v2.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/site_probe_v2.csv) |
| 4e · morphology features + Fig 3.e gate | complete, gate PASSED | [`instrumentation/fig3e_gate.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/fig3e_gate.csv) |
| 4f · held-out-gene check | complete | [`instrumentation/heldout_gene_check.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/heldout_gene_check.csv) |
| 5 · STFlow stronger baseline | setup complete, training blocked on GPU | [`code/stage5_provenance/STFLOW_SOURCE.txt`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/stage5_provenance/STFLOW_SOURCE.txt) |
| 6.2 deliverables | complete | this report, [`reports/motivation_draft.md`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/motivation_draft.md), 4 figures |

---

## 2. What was run

### 2.1 Compute and configuration

All work ran on the UNC Longleaf cluster, Slurm account `rc_htzhu_pi`, across ~150 tracked jobs. Per-experiment job-id manifests were kept locally during execution; the reproducible record is the scripts in [`code/scripts/`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts) plus the YAML configs in [`code/configs/`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/configs) (one per encoder × head), which together regenerate every number in this report.

The faithful configuration was **read out of HEST's `BenchmarkConfig` dataclass source**, not assumed from argparse defaults (the two differ — the defaults live in the dataclass):

| setting | value |
|---|---|
| `gene_list` | `var_50genes.json` (variance-ranked 50 genes — matches the paper's wording) |
| `normalize` | `True` (log1p) |
| `dimreduce` / `latent_dim` | `PCA` / 256 |
| `method` | `ridge`, with `alpha = 100 / (latent_dim × n_genes)` |
| `seed` | 1 |
| `batch_size` | 128 (64 for hoptimus1, to fit ViT-giant on a 16 GB card) |

XGBoost hyperparameters were verified against the paper in `trainer.py` rather than trusted: **100 estimators, learning rate 0.1, max depth 3, subsample 0.8** — exact match.

### 2.2 Benchmark data

HuggingFace `MahmoodLab/hest-bench`, downloaded with `ignore_patterns=['fm_v1/*']` so that encoder weights come from their own official repositories rather than HEST's repackaged bundle — this keeps version claims verifiable. Full inventory: [`bench_data/INVENTORY.md`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/bench_data/INVENTORY.md), [`bench_data/hest_bench_sample_inventory.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/bench_data/hest_bench_sample_inventory.csv).

- **72 samples**, **236,495 patches**, 10 tasks, **29 shipped fold pairs**, 50 target genes per task.
- Patch retention 92.4% of AnnData spots (patches are cut only where a full 224×224 window fits the tissue; 57.8% for SKCM, the extreme).
- Two distinct gene spaces inside CCRCC (36,601 vs 17,943 vars) — all 50 target genes verified present in all 72 samples regardless.
- ccRCC ships **6** folds, not the 24 the handoff anticipated. Confirmed and explained in §4 (D3).

### 2.3 Runs completed

**Four regression heads × 11–12 encoders × 10 tasks.** Encoders: resnet50, ctranspath, phikon, conch_v1, conch_v15, uni_v1, uni_v2, gigapath, virchow, virchow2, hoptimus0, and hoptimus1 (newly approved — see §6).

| head | configuration | coverage |
|---|---|---|
| `pca_ridge` | PCA-256 → ridge (the paper's Table 1 protocol) | 11 encoders × 10 tasks = 110 runs; hoptimus1 in progress |
| `ridge_nopca` | raw embeddings → ridge (Table A13) | 110 runs |
| `xgb_nopca` | raw embeddings → XGBoost (Table A14, selected) | 110 runs |
| `xgb_pca` | PCA-256 → XGBoost (Table A14, rejected candidate) | 10 runs (resnet50 pilot) |

The two XGBoost variants exist because the paper's Table A14 does not state which feature scale it used. Piloting both on resnet50 resolved it by measurement: raw gives 0.3278 against A14's 0.326 (+0.0018), PCA-256 gives 0.3046 (−0.0214) — a twelve-fold difference in agreement. The rejected candidate is therefore *evidence for the selection*, not a replication failure, and [`reports/discrepancy_table_v2.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/discrepancy_table_v2.csv) carries a `config_role` column recording that distinction.

### 2.4 Instrumentation layer

Built by [`code/scripts/build_instrumentation.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/build_instrumentation.py), validated by [`code/scripts/check_instrumentation.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/check_instrumentation.py) and [`code/scripts/verify_row_identity.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/verify_row_identity.py).

- **130,072,250 prediction rows** — every (spot × gene × encoder) triple, partitioned per task.
- **236,495 spots** joined to AnnData spot metadata, HEST sample metadata (72 samples × 21 fields, [`instrumentation/sample_metadata.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/sample_metadata.csv)), and CellViT morphology over **13,530,431 segmented nuclei**.
- Join integrity: 236,495/236,495 keys matched, 0 duplicates, complete for 10/10 tasks ([`instrumentation/morphology_qc.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/morphology_qc.csv)).

### 2.5 Diagnostic experiments

| experiment | script | output |
|---|---|---|
| Split-design decomposition (4 designs × 5 repeats) | [`split_decomposition.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/split_decomposition.py) | [`split_decomposition__*.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation) |
| Split comparison (3 designs, superseded) | [`split_comparison_v2.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/split_comparison_v2.py) | [`split_comparison__*.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation) |
| Count diagnostics (Poisson/NB/ZINB, AIC) | [`count_diagnostics_v2.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/count_diagnostics_v2.py) | [`count_diagnostics_v2.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation) |
| Site-predictability probes (slides held out) | [`site_probe_v2.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/site_probe_v2.py) | [`site_probe_v2__*.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation) |
| Spatial-block probe (block CV) | [`spatial_block_probe.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/spatial_block_probe.py) | [`spatial_block_probe__*.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation) |
| Leave-cohort-source-out shift | [`cohort_shift.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/cohort_shift.py) | [`cohort_shift__*.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation) |
| Across-task shift (matched + unmatched) | [`across_task_shift.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/across_task_shift.py) | [`across_task_shift__*.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation) |
| Size-matched slide-novelty shift | [`site_shift_matched.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/site_shift_matched.py) | [`site_shift_matched__*.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation) |
| Held-out-gene check (alpha separated) | [`heldout_gene_check.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/heldout_gene_check.py) | [`heldout_gene_check__*.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation) |
| Ridge penalty sweep (12 points × 2 scales) | [`alpha_sweep.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/alpha_sweep.py) | [`alpha_sweep__*.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation) |
| Morphology features (true patch box) | [`morphology_features_v2.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/morphology_features_v2.py) | [`morphology_summary_v2__*.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation) |
| HEST Figure 3.e reproduction gate | [`fig3e_gate.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/fig3e_gate.py) | [`fig3e_gate.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation) |
| Sample-metadata join | [`metadata_join.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/metadata_join.py) | [`sample_metadata.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation) |

---

## 3. What was checked

### 3.1 Replication fidelity — the headline result

Against the live GitHub leaderboard (parsed at the 03.04.26 version the handoff names, 26 models, [`reports/hest_leaderboard_030426.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/hest_leaderboard_030426.csv)), the `pca_ridge` head over **99 encoder–task cells**:

| statistic | value |
|---|---|
| mean \|diff\| | **0.0002** |
| median \|diff\| | 0.0000 |
| max \|diff\| | 0.0155 |
| cells over the handoff's 0.03 threshold | **0 of 99** |

Ten of eleven encoders match to ≤0.0001; the exception is uni_v1 at −0.0017.

**The three paper configurations:**

| paper table | head | ours | paper | diff |
|---|---|---|---|---|
| Table 1 | `pca_ridge`, resnet50 | 0.3252 | 0.3252 | **+0.0000** |
| Table A14 | `xgb_nopca`, resnet50 | 0.3278 | 0.3260 | +0.0018 |
| Table A13 | `ridge_nopca`, resnet50 | 0.2843 | 0.3140 | **−0.0297** |

ResNet50 is the informative case: no gated weights, no version ambiguity, no transform drift. An exact hit on Table 1 means the protocol, splits, gene list, normalisation and ridge head are all wired as the authors had them. The A13 gap is the one open discrepancy — see D1.

### 3.2 Encoder ranking, all four heads — HEADLINE TABLE

Average Pearson over the nine paper tasks (HCC excluded, as the handoff specifies). Full table: [`reports/head_comparison_paper9.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/head_comparison_paper9.csv).

| encoder | dim | `pca_ridge` | `ridge_nopca` | `xgb_nopca` |
|---|---|---|---|---|
| hoptimus0 | 1536 | 0.4150 | 0.2756 | 0.3955 |
| uni_v2 | 1536 | 0.4142 | 0.2765 | 0.3933 |
| virchow | 2560 | 0.4060 | 0.2654 | 0.3967 |
| virchow2 | 2560 | 0.4033 | 0.2613 | 0.3920 |
| gigapath | 1536 | 0.3875 | 0.2664 | 0.3692 |
| uni_v1 | 1024 | 0.3856 | 0.2981 | 0.3810 |
| conch_v15 | 768 | 0.3792 | 0.3474 | 0.3725 |
| conch_v1 | 512 | 0.3696 | 0.3543 | 0.3728 |
| phikon | 768 | 0.3661 | 0.2974 | 0.3577 |
| ctranspath | 768 | 0.3468 | 0.2984 | 0.3463 |
| resnet50 | 1024 | 0.3252 | 0.2843 | 0.3278 |
| *head mean* | | *0.3817* | *0.2932* | *0.3732* |

**Between-encoder spread on the benchmark's own protocol: 0.0898** (0.3252 to 0.4150). This is the reference against which every design effect below is measured.

### 3.3 Data invariants

From [`instrumentation/stage4a_integrity.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/stage4a_integrity.csv), all verified against the independently-built Stage 1 inventory rather than against the build's own arithmetic — 10/10 tasks pass each:

| invariant | result |
|---|---|
| per-task spot counts match the inventory | PASS, summing to **236,495** |
| every spot carries exactly 50 gene rows | PASS |
| every spot appears in exactly one test fold | PASS |
| prediction rows = spots × 50 × 11 encoders | PASS |
| stored raw counts still integral | PASS |
| all 50 target genes present in all 72 samples | PASS |

Row identity was **proven, not assumed**: each prediction row's target must equal an independently reconstructed value from the AnnData, asserted inline during the build, with a permutation control confirming the check has power (aligned max \|diff\| 4.4e-7 at float32 epsilon; permuted ≈8.0). See [`instrumentation/row_identity_check.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/row_identity_check.csv).

### 3.4 Split-design decomposition — HEADLINE TABLE

Three encoders (the top three by Pearson) × 10 tasks × 5 random repeats, 1,077 rows. [`instrumentation/split_decomposition.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/split_decomposition.csv), terms in [`instrumentation/split_decomposition_terms.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/split_decomposition_terms.csv), script [`split_decomposition.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/split_decomposition.py).

**The metric artefact, measured first** because it determines whether any other number is interpretable. Pearson computed on a pooled test set carries between-patient variance in its denominator, so the same model scores higher on a more heterogeneous test set:

| design | patients in test set | pooled Pearson | within-patient | inflation |
|---|---|---|---|---|
| `blocked` | 8.9 | 0.6659 | 0.4639 | **+0.2020** |
| `patient` | 2.5 | 0.3736 | 0.3587 | **+0.0149** |
| `random` | 8.9 | 0.6880 | 0.4960 | **+0.1920** |
| `source_seen` | 1.0 | 0.5870 | 0.5870 | **+0.0000** |
| `source_unseen` | 1.0 | 0.5452 | 0.5452 | **+0.0000** |

The inflation is a near-mechanical function of test-set heterogeneity: **exactly 0.0000** when the test set is a single patient, +0.19 to +0.20 when it spans ~9. All numbers below therefore use **within-patient Pearson for every design**, with the pooled value retained so the artefact's size is measured rather than assumed.

**The decomposition** (within-patient metric, additive to machine precision):

| term | contrast | value | × encoder spread | sign consistency |
|---|---|---|---|---|
| spatial adjacency | random − spatially blocked | **0.0335** | 0.37× | 30/30 |
| slide identity | blocked − shipped patient folds | **0.1241** | 1.38× | 30/30 |
| *total leakage* | *random − shipped* | ***0.1575*** | *1.75×* | *30/30* |
| institution shift | source-seen − source-unseen | **0.0419** | 0.47× | — |

Monte-Carlo SD over the five repeats is 0.0069 for the adjacency term and 0.0016 for the total — so the effects are ~5× and ~96× their repeat-to-repeat noise. Per-task range is wide (COAD 0.328, CCRCC 0.057); CCRCC is the one task where adjacency exceeds slide identity, consistent with its 24 slides being a single institution and study.

**Figure:** [`figures/stage4b_split_decomposition.png`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/figures/stage4b_split_decomposition.png)

### 3.5 Non-exchangeability: are slides identifiable from features?

[`site_probe_v2.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/site_probe_v2.py), [`spatial_block_probe.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/spatial_block_probe.py). Outputs [`instrumentation/site_probe_v2__*.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation), [`instrumentation/spatial_block_probe.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/spatial_block_probe.csv).

A logistic probe recovers **slide identity** at **0.9898** balanced accuracy under random spot splitting and **0.9805** under spatial block cross-validation, where whole contiguous grid blocks are held out. The block design was **verified before any accuracy was read**: the median distance from a test spot to its nearest training spot widened **2.83×** in all 110 cells. So near-ceiling separability is a genuine slide-level signature, not nearest-neighbour lookup on adjacent tissue.

**Three site probes, with an explicit note on which is safe to quote:**

| probe | balanced acc | chance | confounded? |
|---|---|---|---|
| assay technology | 0.9940 | 0.50 | **yes** — the 5 imaging tasks are different organs from the 5 sequencing tasks, and preservation method is perfectly collinear with assay |
| cohort source | 0.9378 | 0.20 | **yes** — most sources appear in exactly one task, so the probe can succeed by recognising tissue |
| IDC institution | 0.6818 | 0.50 | **no** — two sources of the same breast tissue on the same 541-gene panel |

The confound-free contrast is the only one that speaks to institution, and it is **underpowered**: with four folds, only **2 of 11** encoders is distinguishable from chance at 95%. So the *consequence* (performance degrades across sites) is measured and large, while the *mechanism* (embeddings carry site identity) is established for slides and **unresolved for institutions**.

**Figure:** [`figures/stage4d_site_probe_v2.png`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/figures/stage4d_site_probe_v2.png)

### 3.6 Distribution shift, three designs

These measure genuinely different contrasts and are reported separately rather than averaged:

| design | what varies | shift | notes |
|---|---|---|---|
| slide novelty, sizes matched | test slide seen vs unseen in training | **+0.3213** | 4 encoders × 7 tasks, positive in 262/264 cells; both train and test sizes fixed by construction |
| institution novelty (IDC) | held-out cohort source | **+0.0867** | the two directions have very different training sizes (28,521 vs 7,015), so the mean is the reportable figure, not either arm |
| across-task (organ) | held-out task, sizes matched | **not a scalar** | varies monotonically with in-domain data — see below |

**Across-task shift is not identified as a single number.** Even with training volume matched, the cost of training on other organs tracks how much in-domain data exists:

| held-out task | in-domain train spots | matched shift |
|---|---|---|
| IDC | 26,652 | +0.1453 |
| COAD | 7,825 | +0.0593 |
| PAAD | 5,047 | -0.0195 |
| LUNG | 2,603 | +0.0089 |
| SKCM | 1,517 | -0.0295 |

IDC, with the most in-domain data, shows **+0.1453**; the smallest tasks go slightly *negative* — a size-matched mix of four other organs does marginally better than their own scarce data. Task diversity substitutes for task specificity at small sample size, so any single across-domain number is a function of the reference task. Scripts: [`across_task_shift.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/across_task_shift.py), [`cohort_shift.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/cohort_shift.py), [`site_shift_matched.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/site_shift_matched.py).

One structural finding constrains this arm: the five imaging-based tasks' top-50 gene lists are **completely disjoint**, and their underlying panels share only **14 real genes** across all 15 samples (panels differ *within* tasks too). No across-task model can use the benchmark's own targets; the arm runs on those shared genes with a within-task baseline on the same genes, so the gap measures shift rather than gene-set difficulty.

### 3.7 Observation model — what noise distribution the data actually supports

Per-gene maximum-likelihood fits on the benchmark's own 50-gene target panel, 500 gene–task pairs. [`count_diagnostics_v2.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/count_diagnostics_v2.py) → [`instrumentation/count_diagnostics_v2.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/count_diagnostics_v2.csv).

| comparison | result |
|---|---|
| NB preferred over Poisson (AIC) | **478/488** converged genes, median ΔAIC 57,812 |
| genes overdispersed (Fano > 1) | **500/500** — all of them |
| ZINB preferred over NB (AIC) | **14/474** |
| median ΔAIC, NB vs ZINB | **-2.0019** |

The zero-inflation result was framed as a **falsifiable prediction** rather than a preference count: if the extra ZINB parameter contributes no likelihood at all, AIC's one-parameter penalty forces ΔAIC to **exactly −2.000**. Observed median **-2.0019**, with **455/474** genes within 0.5 of that value. The verdict is identical under BIC, so it is not criterion-dependent.

**Conclusion for downstream modelling: a heteroscedastic negative-binomial head is the right conditional model; zero-inflation buys nothing.** The apparent excess of zeros is an assay property, not a separate biological process — median zero fraction 0.29 for imaging-based tasks against 0.61 for sequencing-based ones, a split that follows the technology and not the tissue.

**Data-quality flag carried in the output rather than dropped:** 14 genes show implausibly large evidence for zero inflation. These are diverged NB fits that statsmodels nonetheless reports as converged, clustered at extreme overdispersion (median Fano 59 versus 13.2 elsewhere). They are marked in the table; trusting the convergence flag would have inverted the headline conclusion.

**Figure:** [`figures/stage4c_count_diagnostics_v2.png`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/figures/stage4c_count_diagnostics_v2.png)

### 3.8 The ridge penalty is inert — and what that explains

[`alpha_sweep.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/alpha_sweep.py) → [`instrumentation/alpha_sweep__*.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation). 12 penalties × 2 feature scales × 2 folds, on two encoders and two tasks, recording Gram-matrix condition numbers so the answer arrives with its mechanism.

This sweep was run to test a hypothesis of mine — that Table A13's no-PCA comparison was confounded because `alpha = 100/(d × n_genes)` changes 4× when `d` goes from 256 to 1024. **The sweep eliminated that hypothesis:** at the formula values the fit is indistinguishable from unpenalised OLS at both scales (\|diff vs OLS\| ≤ 2.7e-4). The penalty never binds, so the 4× difference is immaterial and A13 is *not* alpha-confounded.

What the sweep found instead is more consequential:

| feature scale | dim | mean Gram condition number | formula α |
|---|---|---|---|
| `pca256` | 256 | 595 | 0.01 |
| `raw` | 1024 | 755,577,089,195,412 | 0 |

At raw width the Gram matrix is **numerically singular** — condition number 3.0 × 10¹⁵ at 1536 dims, at the float64 limit — so an effectively-unpenalised fit is catastrophic. With the penalty properly tuned, PCA's advantage vanishes and slightly reverses, and the no-PCA head recovers +0.019 (resnet50) to +0.144 (hoptimus0) of Pearson that the benchmark's formula leaves on the table.

### 3.9 Held-out-gene check, with a third instance of the same confound

[`heldout_gene_check.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/heldout_gene_check.py) → [`instrumentation/heldout_gene_check__*.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation).

Handoff 4f asks whether holding out 10 of the 50 target genes leaves the remaining 40 comparable. Writing it surfaced that the benchmark's penalty formula depends on `n_genes`, so dropping targets also changes regularisation by 25% — the same structural confound as the no-PCA comparison. Three fits per fold therefore separate the two effects: all 50 targets at the benchmark's alpha; 40 targets at the formula's alpha; 40 targets with alpha **held at the 50-gene value**.

**Result: with the penalty held fixed, the retained genes' predictions are identical to machine precision (max \|prediction diff\| 6.2e-06).** Multi-output ridge fits each target independently, so gene subsetting cannot leak — stated as a falsifiable prediction beforehand, so a violation would have meant something genuinely couples the targets.

### 3.10 Morphology features and the Figure 3.e gate

[`morphology_features_v2.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/morphology_features_v2.py), [`fig3e_gate.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/fig3e_gate.py), [`morphology_qc.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/morphology_qc.py).

**The gate passed before any features were built.** Reproducing HEST Figure 3.e — Pearson(GATA3, mean neoplastic nuclear area per spot) on an IDC sample — gives **0.4578** against the paper's **0.47**, \|diff\| 0.0122, inside the 0.05 tolerance ([`instrumentation/fig3e_gate.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/fig3e_gate.csv)). Raw counts match better than log1p, resolving an ambiguity the paper leaves open. This validated the coordinate handling before committing to all 72 samples.

Two findings from the gate that bear on how Figure 3.e should be read:

- **The relationship is sample-specific, not a general IDC property.** Three of four IDC samples give \|r\| ≤ 0.14 and one is slightly negative. The paper's wording is about "this tumor" so it does not overclaim, but nuclear area is not a dependable morphological proxy for GATA3 across breast samples.
- **Identifying the sample by nucleus count failed.** The paper reports 168,033 and 342,018 nuclei; our per-slide totals are 119,826 / 178,322 / 497,508 / 710,379 — no match within 2,000. Those figures likely count a displayed region or come from a different CellViT version. The correlation identifies the sample unambiguously instead.

**Per-spot features** (count, mean and median nuclear area, fractions across all five CellViT classes, plus neoplastic-only area and count) computed over **the true patch box the encoder saw**, with overlapping patches counted for every spot they belong to. 13,530,431 nuclei; coverage 0.960 of predicted spots, with the remainder carrying NaN rather than imputed zeros so empty stroma cannot be read as unusually small nuclei.

**Patch geometry is self-calibrated per sample and this is load-bearing:** patch extents span **163–818 px** across the 72 samples (scale factor 0.727–3.654), including a factor-of-two difference *between two samples of the same task and assay*. Seven samples have factor < 1, meaning the source region is **smaller** than 224 px and is upsampled. No constant patch size — in pixels or microns — is correct for this benchmark. Sources recorded in [`instrumentation/patch_scale_sources.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/patch_scale_sources.csv).

---

## 4. Discrepancies and open questions

Tabulated with IDs so downstream work can cite them. Underlying data: [`reports/discrepancy_table_v2.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/discrepancy_table_v2.csv) (238 rows, all four heads, with paper and leaderboard columns and a `config_role` flag).

### D1 · Table A13 `ridge_nopca` resnet50, −0.0297 — explained, not closed numerically

The alpha-confound hypothesis is **withdrawn**: the penalty sweep shows it is inert at both feature scales. The remaining account is numerical. At raw width the Gram matrix is ill-conditioned (2.5 × 10⁴ at 1024 dims, 3.0 × 10¹⁵ at 1536 — numerically singular), so BLAS, solver tolerance and library version differences move the answer materially. This account makes a prediction that holds: the gap should appear **only** in this head, and Table 1 is exact (+0.0000) while A14 is +0.0018.

### D2 · Table A13's encoder ranking is embedding width, not representation quality

| head | Spearman(embedding dim, score) | p |
|---|---|---|
| `ridge_nopca` | **-0.954** | 5.4e-06 |
| `pca_ridge` | +0.735 | — |

The two **narrowest** encoders take the top two slots under the no-PCA head (conch_v1 at 512 dims, 0.3543; conch_v15 at 768, 0.3474) and the three lowest are all ≥1536 dims (virchow2 2560 at 0.2613, virchow 2560 at 0.2654, gigapath 1536 at 0.2664). Combined with §3.8, that ranking measures Gram conditioning.

**Recommendation: if Table A13 is cited downstream, cite D2 with it.** The paper's "PCA helps" conclusion is under-regularisation, not a property of the representations.

*Provenance note:* virchow2's value was 0.2692 in an earlier table built before its 4-task completion run was merged with its 6-task original; the merged value is 0.2613 and strengthens ρ from −0.930 to −0.954.

### D3 · ccRCC ships 6 folds, not 24 — RESOLVED

Patient-level stratification. Verified directly from the metadata join: no shipped fold places a patient in both train and test ([`instrumentation/sample_metadata.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/sample_metadata.csv)). The 24 samples map to 6 patients.

### D4 · Figure 2a R = 0.81 — RESOLVED

0.81 is the **raw**-parameter correlation; log10 parameters give 0.942, while the caption's framing implies a log scale. Both computed in [`reports/scaling_law_inputs.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/scaling_law_inputs.csv).

### D5 · Imaging-task gene panels are disjoint — FINDING, not a discrepancy

The five imaging-based tasks' top-50 lists share **zero** genes, and the underlying panels share only **14 real genes** across all 15 samples (after excluding assay control probes). Panels differ within tasks too. Consequence: no across-task experiment can use the benchmark's own targets, which is why §3.6's across-task arm runs on the shared subset with a matched within-task baseline.

### Q1 · Do embeddings encode institution specifically? — UNRESOLVED

See §3.5. The consequence is measured; the mechanism is confounded for two of three probes and underpowered for the third (2/11 encoders distinguishable from chance). Resolving it needs more institution pairs holding tissue and assay fixed, which this benchmark does not contain.

### Q2 · Across-task shift as a scalar — NOT IDENTIFIED

See §3.6. It varies monotonically with in-domain sample size even with training volume matched, so reporting one number would be a statement about the reference task rather than about shift.

---

## 5. What was NOT checked

Stated explicitly so the audit does not have to infer coverage:

1. **Gene-selection leakage — and no refit can detect it.** The 50 targets per task were variance-ranked over *every spot including the test folds*. This is a property of the shipped benchmark data. A leakage-free evaluation would recompute the ranking inside each fold. Stage 4f establishes only that the ridge fit does not couple targets, which is a different question.
2. **Assumption diagnostics for the count fits** — residual checks and dispersion-model adequacy beyond AIC/BIC were not assessed.
3. **The penalty sweep covers 3 cells** (2 tasks × 2 encoders), so the task-by-conditioning interaction is not fully mapped.
4. **The decomposition covers 3 encoders**, the top three as the handoff specifies, not all 11.
5. **Institution shift rests on one task.** Only IDC contains two cohort sources of the same tissue and assay, so that contrast has 4 slides.
6. **Spatial-block probe used 6×6 grids**; sensitivity to block size was not explored.
7. **Stage 5 STFlow training has not run** — setup and data-path validation are complete, training is GPU-blocked.
8. **hoptimus1 is 1 of 10 tasks complete** at the time of writing (SKCM); the other nine are queued.

---

## 6. Open decisions — for the oversight chat

Four protocol deviations require sign-off under handoff Section 8 (report-and-wait). None is resolved unilaterally; all four are live.

### OD1 · Barcode criterion revised: exact match → strict subset

**Handoff requires:** patch barcodes match `adata.obs_names` **exactly**.  
**Observed:** they do not, and cannot. Patch files carry *fewer* spots than the AnnData — 92.4% overall, 57.8% for SKCM — because patches are extracted only where a full 224×224 window fits the tissue.  
**Revised criterion:** patch barcodes are a strict **subset** of `adata.obs_names`, which passes 72/72 samples.  
**Why it is safe:** `benchmark.py` aligns spots by label, not by position, so a subset cannot misalign targets.  
**Evidence:** [`bench_data/INVENTORY.md`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/bench_data/INVENTORY.md) acceptance table.  
**Decision needed:** accept the revised criterion, or treat the mismatch as a blocking defect.

### OD2 · `hoptimus1` — APPROVED, now executing

Weights were gated; access has been granted and verified. `trident` implements the encoder natively, so no code change was required. The SKCM pilot is complete (Pearson **0.6589**, 1536-dim, 1 min 52 s on an L40S at batch 64) and the remaining nine tasks are queued. **No decision outstanding** — recorded here because it closes a previously-open item.

### OD3 · `predictions.parquet` partitioned per task

**Handoff names** a single joined prediction table. **Delivered** as 10 per-task table pairs (`spots.parquet` + `preds.parquet`), totalling 130,072,250 rows, so each file stays loadable on a laptop. Information content is identical and the integrity assertions run across the partitions.  
**Decision needed:** accept partitioning, or require a single concatenated file.

### OD4 · CellViT segmentations read as parquet rather than zipped GeoJSON

**Handoff names** the zipped GeoJSON distribution. **Used** the parquet distribution of the same segmentations — identical content, no geometry parsing step. This is the deviation I consider clearly within tolerance, but it is a deviation.  
**Decision needed:** confirm, or require the GeoJSON path for exactness.

### Also requiring a decision, outside the four deviations

**OD5 · Stage 5 STFlow.** Setup is complete and the integration question is answered favourably: STFlow's `uni_v1_official` is a path component and dimension key rather than an extractor, so our cached UNI v1 embeddings are the intended input, not a substitution ([`code/stage5_provenance/STFLOW_SOURCE.txt`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/stage5_provenance/STFLOW_SOURCE.txt)). Training needs CUDA and the GPU partitions are saturated with >1,100 jobs pending. It also needs its **own conda environment**, because `scprep` pins `pandas<2.1` which is incompatible with this project's pandas 2.3.3 ([`env/ENV_NOTES.txt`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/env/ENV_NOTES.txt)). **Decision needed:** is STFlow worth a dedicated env plus a multi-day GPU wait, or is it dropped as the optional arm the handoff marks it?

---

## 7. Proposed next step

1. **Resolve OD1, OD3, OD4 and OD5.** Only OD1 has scientific content.
2. **Build the calibration baseline on the shipped patient folds** — the only design here with no leakage. Split conformal with a global quantile first, then site-aware variants. The instrumentation gives per-spot residuals joined to slide, patient, cohort source, sequencing depth, expression level and morphology, so coverage can be audited **per slide** rather than marginally.
3. **Use a negative-binomial head, not Gaussian or ZINB** — 478/488 genes reject Poisson and zero-inflation buys nothing (§3.7).
4. **Expect a global conformal interval to under-cover across slide boundaries** by roughly the slide-identity term, **0.124** Pearson. That is the quantity a site-aware method has to recover, and it is the concrete success criterion for the next stage.
5. **Do not condition on institution without more data.** Q1 is unresolved; a density-ratio estimator trained on the confounded probes would be learning tissue, not site.

---

## 8. Figures

| figure | shows |
|---|---|
| [`figures/stage4b_split_decomposition.png`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/figures/stage4b_split_decomposition.png) | the metric artefact scaling with test-set heterogeneity; the adjacency/slide-identity decomposition per task; both terms against the encoder spread |
| [`figures/stage4c_count_diagnostics_v2.png`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/figures/stage4c_count_diagnostics_v2.png) | zero fraction by assay; Fano factors; the ΔAIC = −2 prediction test |
| [`figures/stage4d_site_probe_v2.png`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/figures/stage4d_site_probe_v2.png) | site predictability by encoder, separating the two confounded targets from the confound-free institution contrast |
| [`figures/stage4c_split_comparison.png`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/figures/stage4c_split_comparison.png) | the superseded three-design comparison, retained for provenance |

---

## 9. Method note on the headline leakage number

An earlier version of the split analysis reported the leakage gap as **+0.3143**. That figure was inflated by **+0.1770** because Pearson was computed on whatever spots the test set contained: a pooled test set spanning many patients carries between-patient variance in the correlation denominator, so the same model scores higher on a more heterogeneous test set. Every number in §3.4 uses within-patient Pearson for all designs, with the pooled value retained so the artefact is measured rather than assumed — exactly 0.0000 for the single-slide arms and +0.1920 for random splits. The corrected total is **0.1575**.
