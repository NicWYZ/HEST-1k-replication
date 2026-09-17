# HEST-1k replication and instrumentation — final stage report

*Revision 2, generated 2026-09-16 from the saved result tables.*

**Repository:** `NicWYZ/HEST-1k-replication`, branch `main`.

**What changed since revision 1.** Three things, all material to an audit:

1. **`hoptimus1` completed** as the twelfth encoder on the primary head and is the new top
   performer. It also reproduces the leaderboard *exactly*, which strengthens the fidelity result.
2. **The repository was reorganised**, so every path in revision 1 is stale. Experiment
   directories, the four head names, and the diagnostics layout all changed. This revision's links
   are against the current tree, and every link was checked to resolve against it
   (46 unique file paths and 12 directory paths).
3. **D6 was opened and closed within this revision.** Three analysis tables carried head names made
   stale by the rename and omitted `hoptimus1`. They are now derived by script rather than
   hand-maintained, which also raised the per-task leaderboard comparison from 99 cells to
   **108**.

Two consequences for numbers quoted in revision 1: the between-encoder spread is **0.0977**, not
0.0898 (it was an 11-encoder figure), so the leakage-to-spread ratio is **1.61×**, not 1.75×.

---

## 0. How to audit this

Each question below names the file that answers it. Nothing in this report is asserted without a
file behind it.

| to check | read |
|---|---|
| does it replicate? | [`results/summary/results_encoder.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/summary/results_encoder.csv), [`results/summary/discrepancy_table.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/summary/discrepancy_table.csv) |
| exactly what was run? | [`code/configs/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/code/configs) — one config per run, named `<head>__<encoder>.yaml` |
| is the raw output intact? | [`results/faithful/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/results/faithful) — `<head>/<encoder>/<task>/results_kfold.json` |
| how was each number computed? | [`code/scripts/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/code/scripts) — one script per experiment |
| what do the diagnostics show? | [`results/tailored/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/results/tailored) — grouped by question, each with a `PROVENANCE.txt` |
| can the environment be rebuilt? | [`env/REBUILD.md`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/env/REBUILD.md), [`env/requirements.lock`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/env/requirements.lock) |
| what is deliberately absent? | [`README.md`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/README.md) § *What is not here*, plus each `PROVENANCE.txt` |

**Head naming.** The four configurations are named `<features>_<model>`:

| head | configuration | paper reference | encoders |
|---|---|---|---|
| `pca_ridge` | PCA-256 + ridge | Table 1 | 12 |
| `raw_ridge` | raw embeddings + ridge | Table A13 | 11 |
| `raw_xgb` | raw embeddings + XGBoost | Table A14, as the paper ran it | 11 |
| `pca_xgb` | PCA-256 + XGBoost | Table A14, **rejected** candidate | 1 |

Revision 1 called the middle two `ridge_nopca` and `xgb_nopca`. Every committed table now uses
the names above; the mapping from revision 1 is `ridge_nopca`→`raw_ridge`,
`xgb_nopca`→`raw_xgb`, `xgb_pca`→`pca_xgb`. The three analysis tables that had carried the
legacy names are now *derived* by [`code/scripts/build_summary_tables.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/build_summary_tables.py) rather than
hand-maintained, so they cannot drift from the results again (D6, closed).

---

## 1. Stage and status

| stage | state |
|---|---|
| 0 · access and environment | complete |
| 1 · benchmark data inventory | complete, with one criterion revision awaiting sign-off (OD1) |
| 2 · faithful runs, four heads | complete — 35 (head, encoder) pairs × 10 tasks = 350 task results |
| 3 · verification vs paper and leaderboard | complete |
| 4 · instrumentation and diagnostics | complete — eight diagnostic areas |
| 5 · STFlow stronger baseline | setup and data-path validation complete; training blocked on GPU |

---

## 2. What was run

### 2.1 Compute and configuration

UNC Longleaf, Slurm account `rc_htzhu_pi`, roughly 160 tracked jobs. The reproducible record is
the configs in [`code/configs/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/code/configs) (one per faithful run) plus the scripts in
[`code/scripts/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/code/scripts).

The faithful configuration was **read out of HEST's `BenchmarkConfig` dataclass source**, not
inferred from argparse defaults, which expose only a subset: `seed=1`, `batch_size=128`,
`gene_list=var_50genes.json`, `normalize=True`, `dimreduce=PCA`, `latent_dim=256`, `method=ridge`.
The XGBoost hyperparameters were verified against the paper in `trainer.py` (100 estimators,
learning rate 0.1, max depth 3, subsample 0.8) rather than assumed.

`hoptimus1` used `batch_size=64` — it is a ViT-giant, and 64 keeps inference inside a 16 GB card,
widening the eligible GPU pool. The head is fitted on cached embeddings, so batch size affects
extraction throughput only, not the result.

**TRIDENT is an unpinned git dependency** in HEST's `pyproject.toml`, and its encoder transforms
have changed between versions — which would move Pearson values with no error raised. It is pinned
explicitly at `f3eb7f30` (v0.3.2) in the rebuild recipe.

### 2.2 Benchmark data

72 samples, 10 tasks, 236,495 patches, 29 shipped train/test fold pairs, 50 target genes per
task. Full inventory: [`bench_data/INVENTORY.md`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/bench_data/INVENTORY.md) and
[`bench_data/hest_bench_sample_inventory.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/bench_data/hest_bench_sample_inventory.csv).
Downloaded with `ignore_patterns=['fm_v1/*']` so encoder weights come from their official repos
rather than HEST's repackaging — which matters for provenance.

### 2.3 Runs completed

| head | encoders | task results | config |
|---|---|---|---|
| `pca_ridge` | 12 | 120 | `code/configs/pca_ridge__<encoder>.yaml` |
| `raw_ridge` | 11 | 110 | `code/configs/raw_ridge__<encoder>.yaml` |
| `raw_xgb` | 11 | 110 | `code/configs/raw_xgb__<encoder>.yaml` |
| `pca_xgb` | 1 | 10 | `code/configs/pca_xgb__resnet50.yaml` |

**350 task results, zero NaN, every (head, encoder) pair covering all 10 tasks** — verified by the
integrity block in [`code/scripts/aggregate_results.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/aggregate_results.py), which now reports missing tasks explicitly
rather than skipping them silently.

That guard exists because of two real failures. An exp-code prefix absent from the head map once
routed ten encoders into a skip branch that reported only to stderr, showing 1 encoder where 11
had run; and a per-directory merge once kept a 4-task completion run while discarding the 6 tasks
it was meant to complete. Both are now structurally impossible: wall-limited `_part2` runs and
partial task directories are resolved **on disk** by [`code/scripts/reorganize_repo.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/reorganize_repo.py) per
(head, encoder, task), so the aggregator walks a fixed tree.

### 2.4 Instrumentation layer

**130,072,250 prediction rows** joined to spot metadata, per-task to keep each file loadable
(OD3). Row identity was **proven, not assumed**: every prediction row's target must equal an
independently reconstructed value from the AnnData, asserted inline during the build, with a
permutation control confirming the check has power — aligned max |diff| 4.4e-7 (float32 epsilon)
against ~8.0 permuted. See [`results/tailored/integrity/row_identity_check.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/tailored/integrity/row_identity_check.csv) and [`code/scripts/verify_row_identity.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/verify_row_identity.py).

### 2.5 Diagnostic experiments

| area | question | script |
|---|---|---|
| [`results/tailored/splits/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/results/tailored/splits) | what does a split design cost? | [`split_decomposition.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/split_decomposition.py) |
| [`results/tailored/site_probes/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/results/tailored/site_probes) | are slide / institution / assay recoverable from features? | [`site_probe.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/site_probe.py), [`spatial_block_probe.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/spatial_block_probe.py) |
| [`results/tailored/shift/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/results/tailored/shift) | what does crossing a boundary cost? | [`cohort_shift.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/cohort_shift.py), [`site_shift_matched.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/site_shift_matched.py), [`across_task_shift.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/across_task_shift.py) |
| [`results/tailored/counts/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/results/tailored/counts) | which observation model do the counts support? | [`count_diagnostics.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/count_diagnostics.py) |
| [`results/tailored/morphology/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/results/tailored/morphology) | per-spot nuclear features; Figure 3.e gate | [`morphology_features.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/morphology_features.py), [`fig3e_gate.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/fig3e_gate.py) |
| [`results/tailored/regularization/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/results/tailored/regularization) | does the benchmark's ridge penalty bind? | [`alpha_sweep.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/alpha_sweep.py) |
| [`results/tailored/genes/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/results/tailored/genes) | does holding out targets change the rest? | [`heldout_gene_check.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/heldout_gene_check.py) |
| [`results/tailored/integrity/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/results/tailored/integrity) | does instrumentation match independent references? | [`check_instrumentation.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/check_instrumentation.py), [`metadata_join.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/metadata_join.py) |

---

## 3. What was checked

### 3.1 Replication fidelity — the headline result

Two independent comparisons against the leaderboard snapshot
([`results/summary/hest_leaderboard_030426.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/summary/hest_leaderboard_030426.csv), 26 models, of which 13 map to encoders we ran).

**Encoder level, all 12 encoders** ([`results/summary/results_encoder.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/summary/results_encoder.csv) vs the leaderboard `Average`):

| statistic | value |
|---|---|
| encoders compared | **12 of 12** |
| mean \|diff\| | **0.00017** |
| max \|diff\| | 0.0017 (uni_v1) |
| exactly equal | **7 of 12** |
| within 0.0001 | 11 of 12 |
| over the 0.03 threshold | **0 of 12** |

**Per-task cells, all 12 encoders** ([`results/summary/discrepancy_table.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/summary/discrepancy_table.csv)): **108 cells**
(12 × 9 paper tasks), mean \|diff\| **0.00020**, median 0.00000, max
0.0155 (uni_v1/IDC), **0 of 108** over the 0.03 threshold.
`hoptimus1`'s nine cells agree to a maximum of 0.0001.

**Two cases carry most of the evidential weight:**

- **ResNet50 is exact at 0.3252.** It is the informative case: no gated weights, no version
  ambiguity, no transform drift. An exact hit says the splits, gene list, normalisation, PCA and
  ridge head are all wired as the authors had them.
- **`hoptimus1` is exact at 0.4229 on its first run.** Its weights were gate-approved only after
  the pipeline was fixed, so nothing about it was tuned — an out-of-sample confirmation that the
  protocol transfers to an encoder the pipeline had never seen.

The one cell above 0.0001 is `uni_v1` at **−0.0017**, discussed as D4.

### 3.2 Encoder ranking, all four heads — HEADLINE TABLE

Average Pearson over the nine paper tasks (HCC excluded, the paper's convention).
Source: [`results/summary/results_encoder.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/summary/results_encoder.csv).

| encoder | dim | `pca_ridge` | `raw_ridge` | `raw_xgb` |
|---|---|---|---|---|
| hoptimus1 | 1536 | **0.4229** | — | — |
| hoptimus0 | 1536 | **0.4150** | 0.2756 | 0.3955 |
| uni_v2 | 1536 | **0.4142** | 0.2765 | 0.3932 |
| virchow | 2560 | **0.4060** | 0.2654 | 0.3967 |
| virchow2 | 2560 | **0.4033** | 0.2613 | 0.3919 |
| gigapath | 1536 | **0.3875** | 0.2664 | 0.3692 |
| uni_v1 | 1024 | **0.3856** | 0.2981 | 0.3810 |
| conch_v15 | 768 | **0.3792** | 0.3474 | 0.3725 |
| conch_v1 | 512 | **0.3696** | 0.3543 | 0.3728 |
| phikon | 768 | **0.3661** | 0.2974 | 0.3577 |
| ctranspath | 768 | **0.3468** | 0.2984 | 0.3463 |
| resnet50 | 1024 | **0.3252** | 0.2843 | 0.3278 |
| *`pca_xgb`, resnet50 only* | 1024 | — | — | *0.3046* |

**Between-encoder spread on the primary head: 0.0977** (hoptimus1 0.4229 to
resnet50 0.3252). This is the yardstick every effect below is measured against.

### 3.3 Data invariants

Verified against an **independently computed inventory**, not against the build's own arithmetic
([`results/tailored/integrity/stage4a_integrity.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/tailored/integrity/stage4a_integrity.csv), [`code/scripts/check_instrumentation.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/check_instrumentation.py)):

| invariant | result |
|---|---|
| per-task spot counts match the inventory | PASS, 10/10 tasks, 236,495 total |
| every spot carries exactly 50 gene rows | PASS |
| every spot appears in exactly one test fold | PASS |
| prediction rows = spots × 50 × encoders | PASS |
| stored raw counts still integral | PASS |
| all 50 target genes present in all 72 samples | PASS |

The last one matters more than it looks: CCRCC ships samples in two different gene spaces (36,601
vs 17,943 vars), so absent genes would have made the 50-gene subsetting silently misalign.

### 3.4 Split-design decomposition — HEADLINE TABLE

Three encoders (the top three by Pearson at the time: hoptimus0, uni_v2, virchow) × 10 tasks × 5
random repeats, 1,077 rows. [`results/tailored/splits/split_decomposition.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/tailored/splits/split_decomposition.csv), terms in
[`results/tailored/splits/split_decomposition_terms.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/tailored/splits/split_decomposition_terms.csv), script [`code/scripts/split_decomposition.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/split_decomposition.py).

**Read the metric caveat first.** Pooled Pearson divides by the spread of true expression *in the
test set*, so the same model scores higher on a more heterogeneous test set. Measured against how
many patients the test set spans: **exactly 0.0000** inflation for the single-patient
arms, **+0.1920** for the nine-patient random arms. All numbers below therefore use
**within-patient** Pearson, with the pooled value retained so the artefact is measured rather than
assumed.

| mechanism | contrast | within-patient Pearson | vs encoder spread |
|---|---|---|---|
| spatial adjacency | random − blocked | **0.0335** | 0.34× |
| slide-level signature | blocked − patient | **0.1241** | 1.27× |
| **total slide leakage** | random − patient | **0.1575** | **1.61×** |
| institution shift | source-seen − source-unseen | **0.0419** | 0.43× |

The two mechanisms are additive and consistently signed: adjacency positive in
30/30 cells, slide identity in 30/30. The slide-level
term is about four fifths of the total, which the probe in 3.5 corroborates independently.

**So the dominant determinant of a measured score is not which foundation model supplies the
features — it is which slides the test set may contain.**

### 3.5 Non-exchangeability: are slides identifiable from features?

A linear probe used as a measuring instrument, not a model: if logistic regression can read the
slide off frozen embeddings, the information is unambiguously present. [`results/tailored/site_probes/site_probe.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/tailored/site_probes/site_probe.csv),
[`results/tailored/site_probes/spatial_block_probe.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/tailored/site_probes/spatial_block_probe.csv).

| probe | balanced accuracy | chance | verdict |
|---|---|---|---|
| assay technology | 0.9940 | 0.50 | trivially separable |
| cohort source | 0.9378 | 0.20 | **confounded** — most sources occur in one task only |
| institution, within IDC | 0.6818 | 0.50 | the only confound-free contrast |

**Slide identity survives a spatial-block design.** Under random within-slide splitting the probe
reaches 0.9898, which is an upper bound: adjacent tissue lands on both sides. Holding out
contiguous grid blocks widens the nearest-training-spot distance by a verified median
2.83× and accuracy falls only to **0.9805** — so this is a genuine slide-wide
signature (stain, scanner, section), not local appearance matching.

**But institution is not resolved.** The one confound-free contrast — two institutions, same
tissue, same assay, same gene panel — reaches 0.6818 with only **2 of
11** encoders distinguishable from chance at 95% on four folds. The *consequence* of
site shift is measured (3.4); the *mechanism* is not established for institutions. This is Q1.

### 3.6 Distribution shift, three designs

Reported separately because they are different contrasts, not three estimates of one quantity.
[`results/tailored/shift/`](https://github.com/NicWYZ/HEST-1k-replication/tree/main/results/tailored/shift)

| design | result | interpretability |
|---|---|---|
| leave-cohort-source-out | smaller than slide novelty but still exceeds the encoder spread | training-set sizes differ between directions, so each direction is not individually interpretable |
| size-matched slide novelty | **0.0419** on IDC, both arms evaluated on a single slide | clean: carries no aggregation artefact by construction |
| across-task | varies monotonically with in-domain size; IDC loses most (+0.1453), the smallest tasks go slightly negative | **not a scalar** (Q2) |

The across-task arm also hit a structural obstacle worth recording: **the five imaging-based tasks'
top-50 gene lists are completely disjoint**, and their underlying panels share only 14 real genes
across all 15 samples. No across-task model can use the benchmark's own targets, so that arm runs
on the shared genes with a within-task baseline on the same genes — making the gap measure shift
rather than gene-set difficulty. This is D5.

### 3.7 Observation model

Per-gene maximum-likelihood fits on the benchmark's own target panel, 500 gene–task
pairs. [`results/tailored/counts/count_diagnostics.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/tailored/counts/count_diagnostics.csv), script [`code/scripts/count_diagnostics.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/count_diagnostics.py).

| comparison | result |
|---|---|
| NB beats Poisson (AIC) | **478 of 488** converged pairs |
| minimum Fano factor | 1.638 — every gene overdispersed; Poisson is never adequate |
| ZINB beats NB (AIC) | **14 of 474** |
| median ΔAIC (NB − ZINB) | **-2.0019** |

That median is the point, and it was framed as a falsifiable prediction before being computed: if
the zero-inflation parameter buys no likelihood at all, the AIC difference must equal exactly the
penalty for one unused parameter, −2. The observed −2.0019 matches to three decimals. **Plain
negative binomial is the right observation model.**

Sparsity follows the **assay, not the tissue**: median zero fraction 0.2856 for
imaging-based tasks vs 0.6103 for sequencing-based.

**14 genes are flagged `nb_diverged`** rather than dropped silently: their NB fits diverged
while the fitting library still reported convergence. Trusting that flag would have read them as
overwhelming support for ZINB and inverted the conclusion.

### 3.8 The ridge penalty is inert — and what that explains

A 12-point penalty sweep at both feature scales, with Gram condition numbers recorded so the
answer arrives with its mechanism. [`results/tailored/regularization/alpha_sweep.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/tailored/regularization/alpha_sweep.csv), script [`code/scripts/alpha_sweep.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/alpha_sweep.py).

The benchmark sets `alpha = 100 / (latent_dim × n_genes)`. At that value the fit is
indistinguishable from unpenalised OLS — |diff| ≤ 2.7e-4 at both scales, five to seven orders of
magnitude below where the penalty starts to matter.

| | PCA-256 | raw |
|---|---|---|
| mean Gram condition number | 595 | **7.56e+14** |

At raw width the Gram matrix is **numerically singular** — condition number at the float64 limit —
so an unregularised solve is catastrophic. This sweep eliminated my own prior hypothesis (that a
4× penalty difference confounded Table A13) rather than confirming it, and replaced it with a
better-supported account: see D1 and D2.

### 3.9 Held-out-gene check

[`results/tailored/genes/heldout_gene_check.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/tailored/genes/heldout_gene_check.csv), script [`code/scripts/heldout_gene_check.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/heldout_gene_check.py).

The benchmark's penalty formula depends on the number of target genes, so dropping 10 of 50 changes
the regularisation *and* the gene set simultaneously. Three fits per fold on identical folds and
features separate them: all 50 at the benchmark's alpha; 40 at the formula's alpha; 40 with alpha
held at the 50-gene value. Maximum absolute prediction difference: **0.0000** — the
retained genes' predictions are unchanged at solver tolerance, so the ridge fit does not couple
targets.

**This does not test the leakage that matters.** See § 5, item 1.

### 3.10 Morphology features and the Figure 3.e gate

**Gate first, features second.** Before building anything, the pipeline had to reproduce HEST
Figure 3.e: Pearson(GATA3, mean neoplastic nuclear area per spot) = **0.4578** on
NCBI785 against the paper's 0.47, |diff| 0.0122. [`results/tailored/morphology/fig3e_gate.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/tailored/morphology/fig3e_gate.csv), script
[`code/scripts/fig3e_gate.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/fig3e_gate.py). Raw counts match better than log1p, resolving an ambiguity the paper leaves
open. Two caveats recorded rather than buried: identifying the sample by nucleus count **failed**
(the paper's figures match no per-slide total within 2,000, so they likely count a displayed
region), and the relationship is **sample-specific** — three of four IDC samples give |r| ≤ 0.14.

**13,530,431 segmented nuclei** across all 72 samples. [`results/tailored/morphology/morphology_summary.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/tailored/morphology/morphology_summary.csv),
QC in [`results/tailored/morphology/morphology_qc.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/tailored/morphology/morphology_qc.csv).

**Patch geometry must be calibrated per sample.** Extents span **163–818 px**
(scale factor 0.727–3.654), including a factor-of-two difference between two
samples of the *same task and assay*, and **7 samples** whose source region is
*smaller* than 224 px and is upsampled. No constant patch size — pixels or microns — is correct.
Sources in [`results/tailored/morphology/patch_scale_sources.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/tailored/morphology/patch_scale_sources.csv).

---

## 4. Discrepancies and open questions

IDs are stable across revisions so downstream work can cite them. **D6 is new in this revision.**

### D1 · Table A13 `raw_ridge` resnet50, −0.0297 — explained, not closed numerically

Our 0.2843 against the paper's printed 0.314. The penalty-confound hypothesis was **eliminated** by
3.8 — the penalty is inert, so a 4× difference in it cannot explain anything. The surviving account
is numerical: this is the one head effectively solving a singular system (condition number ~10¹⁵),
where BLAS version, solver tolerance and library build move the answer materially. That account
predicts the discrepancy should appear **only** in `raw_ridge`, which is what we observe —
`pca_ridge` is exact and `raw_xgb` is +0.0018.

### D2 · Table A13's encoder ranking is embedding width, not representation quality

Spearman(embedding dim, score) = **-0.954** (p = 5.4e-06) for `raw_ridge`,
against **+0.735** for `pca_ridge`. The 512-dim CONCH v1 *wins* the raw head (0.3543);
the three lowest are virchow2 (2560), virchow (2560) and gigapath (1536). Combined with 3.8, that
head is measuring Gram conditioning. **Any downstream use of Table A13's ranking should cite D2.**
Table: [`results/summary/head_comparison_paper9.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/summary/head_comparison_paper9.csv) (legacy head names inside — see D6).

### D3 · ccRCC ships 6 folds, not 24 — RESOLVED

The handoff flagged a possible 24. The shipped split CSVs contain 6, and the benchmark's own
stratification is by patient, not sample — which explains the count. Not a discrepancy.

### D4 · `uni_v1` — the only encoder above 0.0001, and the largest per-task cell

Ours 0.3856 vs 0.3873 at the encoder level (−0.0017), and its IDC cell is the largest single
per-task discrepancy at 0.0155. Both are well inside the 0.03 threshold, and it is the only
encoder that is not effectively exact. Most plausibly an encoder-weight or transform revision upstream; not chased
further because it changes no conclusion.

### D5 · Imaging-task gene panels are disjoint — FINDING, not a discrepancy

The five imaging-based tasks' top-50 lists share **no** genes, and the underlying panels share only
14 across all 15 samples. This constrains any across-task or transfer experiment on this benchmark
and is a property of the data, not an error.

### D6 · Two committed tables carried legacy head names — RESOLVED

[`results/summary/discrepancy_table.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/summary/discrepancy_table.csv) and [`results/summary/head_comparison_paper9.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/summary/head_comparison_paper9.csv) used
`ridge_nopca` / `xgb_nopca` in their `head` column, and `hoptimus1` was absent from the per-task
table, because both were hand-maintained analysis products rather than script output. Every value
in them was correct; only the labels were stale.

**Closed.** Both, plus [`results/summary/faithful_pca_ridge_task_matrix.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/summary/faithful_pca_ridge_task_matrix.csv), are now derived by
[`code/scripts/build_summary_tables.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/build_summary_tables.py). The per-task leaderboard comparison consequently rises from 99
cells to **108** (12 encoders × 9 tasks), and § 3.1's two comparisons now cover the same
12 encoders. `discrepancy_table_v2.csv` was renamed to `discrepancy_table.csv`, the `_v2` marker
having stopped distinguishing anything once the v1 file was deleted.

One table is deliberately **not** regenerated: [`results/summary/scaling_law_inputs.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/results/summary/scaling_law_inputs.csv) compares against the
paper's Table 1, which reports 10 encoders. `conch_v15` and `hoptimus1` postdate the paper —
`hoptimus1` is on the live leaderboard but not in Table 1 — so there are no paper values to add,
and inventing them is what the table exists to guard against.

### Q1 · Do embeddings encode institution specifically? — UNRESOLVED

See 3.5. The confound-free contrast has 4 slides and 2 of 11 encoders
distinguishable from chance. Resolving it needs more institutions per tissue-and-assay stratum than
HEST-bench contains.

### Q2 · Across-task shift as a scalar — NOT IDENTIFIED

Size matching barely reduced the dependence on task size, because matching cannot change *which*
task is held out. Reported as the monotone per-task structure instead, with IDC — the naturally
size-balanced case — as the interpretable cell.

---

## 5. What was NOT checked

Stated explicitly so absence is not read as a negative result.

1. **Gene-selection leakage — the most important item on this list, and no refit can detect it.**
   The 50 target genes per task were variance-ranked over *every* spot, test folds included. That
   is a property of the shipped benchmark data. Every absolute performance number in this report,
   and on the public leaderboard, inherits it. A leakage-free evaluation would recompute the
   ranking inside each fold — a different benchmark, not a re-analysis. § 3.9 establishes only
   that the ridge fit does not couple targets, which is a different question.
2. **`hoptimus1` on the other three heads.** `pca_ridge` only; `raw_ridge` and `raw_xgb` have 11
   encoders, `pca_xgb` has 1.
3. **`pca_xgb` beyond resnet50** — piloted to identify the paper's configuration, not extended.
4. **Assumption diagnostics** for the ridge fits (residual structure, influence) — not assessed.
5. **Spatial-block sensitivity to block size.** One 6×6 grid was used; the design was verified by
   measuring buffer width, not by sweeping the block size.
6. **Institution shift beyond one task** — 4 slides, the only confound-free stratum available.
7. **STFlow training.** Setup and data-path validation are complete; training is CUDA-only against
   a saturated GPU queue.

---

## 6. Open decisions — for the oversight chat

Three protocol deviations require sign-off under the handoff's report-and-wait clause. None has
been resolved unilaterally. **OD2 is now closed** — `hoptimus1` was approved and has completed.

### OD1 · Barcode criterion revised: exact match → strict subset

**Required:** patch barcodes match `adata.obs_names` exactly.
**Observed:** they do not, and cannot. Patch files carry *fewer* spots than the AnnData — 92.4%
overall, 57.8% for SKCM — because patches are extracted only where a full 224×224 window fits the
tissue.
**Adopted:** strict-subset plus exact ordering, verified per sample.
**Why it is safe:** every retained barcode matches exactly, so no misalignment is possible; the
benchmark's own splits reference the patch files, so the excluded spots are not evaluated by the
paper either.
**Evidence:** [`bench_data/INVENTORY.md`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/bench_data/INVENTORY.md) acceptance table.

### OD3 · Prediction table partitioned per task

**Required:** a single `predictions.parquet`. **Adopted:** one file pair per task, 130,072,250
rows total. Identical information; each file stays loadable on a laptop. The row-identity assertion
is retained inside the build, so a future refactor cannot silently break alignment.

### OD4 · CellViT segmentations read as parquet rather than zipped GeoJSON

**Required:** the zipped GeoJSON the handoff names. **Adopted:** the parquet HEST-bench actually
ships, same geometry content. This looks clearly within tolerance but is a named format
substitution, so it is listed rather than assumed.

### Also requiring a decision, outside the three deviations

- **Stage 5** — STFlow needs its own environment (its `scprep` pins `pandas<2.1`, ABI-incompatible
  with this project's pandas 2.3.3; recorded in [`env/ENV_NOTES.txt`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/env/ENV_NOTES.txt)) plus
  a multi-day GPU allocation. Nothing in this report depends on it.

---

## 7. Proposed next steps

1. **Extend `hoptimus1` to `raw_ridge` and `raw_xgb`** — it is the top encoder on the primary head
   and D2 predicts it should rank *poorly* on `raw_ridge` given its 1536-dim width. That is a
   sharp, cheap falsification test of D2: the embeddings are already cached, so it is head-fitting
   only, no GPU.
2. **Use the instrumentation layer for its purpose** — the slide-level term (0.1241) is the
   quantity a site-aware calibration method has to recover, and a global conformal interval should
   be expected to under-cover across slide boundaries by roughly that much.
3. **Do not build on Table A13's ranking** without citing D2.
4. **Treat every absolute number as inheriting the § 5.1 gene-selection leakage.** Comparisons
   between encoders under an identical protocol are unaffected; absolute claims are not.

---

## 8. Figures

| figure | shows |
|---|---|
| [`figures/fig_replication_fidelity.png`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/figures/fig_replication_fidelity.png) | ours vs paper vs leaderboard |
| [`figures/fig_split_decomposition.png`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/figures/fig_split_decomposition.png) | the metric artefact, the two mechanisms, both vs the encoder spread |
| [`figures/fig_count_diagnostics.png`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/figures/fig_count_diagnostics.png) | zero fraction, Fano, NB-vs-ZINB by AIC |
| [`figures/fig_site_predictability.png`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/figures/fig_site_predictability.png) | probe accuracy by encoder, confounded vs confound-free |

Note: `fig_split_decomposition.png` predates `hoptimus1`, so its encoder-spread reference line is
the 11-encoder 0.0898 rather than the current 0.0977. The mechanism terms it plots are
unaffected — the decomposition was run on three encoders, none of them `hoptimus1`.

---

## 9. Method note on the headline leakage number

Revision 1 of this report initially quoted **0.3143** as the leakage gap. That figure
was inflated by **0.1568** of pooled-Pearson aggregation artefact — 50% of it — and
was retracted. The corrected figure is the within-patient
**0.1575** reported in § 3.4.

The artefact's size is measured rather than asserted: pooled-minus-within inflation is exactly
0.0000 for the single-patient arms and +0.1920 for the nine-patient random
arms, scaling with test-set heterogeneity exactly as the mechanism predicts. Holding the metric
fixed across designs is also what made the decomposition into named mechanisms possible at all.

Separately, the encoder-spread denominator was **0.0977** once `hoptimus1` landed, not
the 11-encoder 0.0898 quoted in revision 1, so the ratio in § 3.4 is 1.61×, not 1.75×.
