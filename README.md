# HEST-1k benchmark replication and instrumentation

Replication of the HEST-1k benchmark (Jaume et al., NeurIPS 2024, arXiv:2406.16192) on UNC
Longleaf, instrumented so its byproducts support downstream work on calibrated uncertainty for
histology-to-expression prediction.

**Private repository. Contains no gated data** — see [What is not here](#what-is-not-here).

This repository holds results, code and reference documentation only. Narrative write-ups and
working documents are kept outside it; this README is the entry point.

## Status

| stage | state |
|---|---|
| 0 · access and environment | complete |
| 1 · benchmark data inventory | complete (one documented criterion revision) |
| 2 · faithful runs, four heads | complete — 35 (head, encoder) pairs × 10 tasks |
| 3 · verification vs paper and leaderboard | complete |
| 4 · instrumentation and diagnostics | complete |
| 5 · STFlow stronger baseline | setup complete; training blocked on GPU availability |

## Headline result

Against the live leaderboard snapshot, the `pca_ridge` head agrees to **mean |diff| 0.0002**
over 99 encoder–task cells, with **0 of 99** exceeding the 0.03 acceptance threshold. ResNet50
reproduces Table 1 **exactly** (0.3252) — the informative case, since it has no gated weights,
no version ambiguity and no transform drift.

Average Pearson over the nine paper tasks (HCC excluded, the paper's convention):

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

`pca_xgb` (Table A14's rejected candidate, resnet50 only): 0.3046. Full tables in
[`results/summary/`](results/summary).

## Repository layout

```
results/
  faithful/<head>/<encoder>/<task>/   the paper's four configurations
  tailored/<question>/                our own diagnostics, grouped by question
  summary/                            aggregated official tables
code/
  scripts/                            one script per experiment, all rerunnable
  configs/<head>__<encoder>.yaml      one config per faithful run
  stage5_provenance/                  upstream commit + integration findings for STFlow
bench_data/                           benchmark inventory and provenance (no gated data)
env/                                  pinned environment and rebuild recipe
figures/                              fig_<topic>.png
```

Every directory under `results/` carries a `PROVENANCE.txt` explaining what is in it, how it
was produced, and what was deliberately excluded.

### The four heads

Named `<features>_<model>`:

| head | configuration | paper reference | encoders |
|---|---|---|---|
| `pca_ridge` | PCA-256 + ridge | Table 1 | 12 |
| `raw_ridge` | raw embeddings + ridge | Table A13 | 11 |
| `raw_xgb` | raw embeddings + XGBoost | Table A14, as the paper ran it | 11 |
| `pca_xgb` | PCA-256 + XGBoost | Table A14, **rejected** candidate | 1 |

`pca_xgb` is kept on purpose. The paper does not state which feature scale Table A14 used;
piloting both on resnet50 settled it by measurement (raw 0.3278 vs the printed 0.326; PCA
0.3046). That mismatch is the *evidence for the selection*, not a replication failure, and
`results/summary/discrepancy_table_v2.csv` flags it with a `config_role` column.

### The diagnostics

| area | question | script |
|---|---|---|
| [`splits/`](results/tailored/splits) | what does a split design cost? | `split_decomposition.py` |
| [`site_probes/`](results/tailored/site_probes) | are slide / institution / assay recoverable from features? | `site_probe.py`, `spatial_block_probe.py` |
| [`shift/`](results/tailored/shift) | how much does crossing a boundary cost? | `cohort_shift.py`, `site_shift_matched.py`, `across_task_shift.py` |
| [`counts/`](results/tailored/counts) | which observation model do the counts support? | `count_diagnostics.py` |
| [`morphology/`](results/tailored/morphology) | per-spot nuclear features, and the Figure 3.e gate | `morphology_features.py`, `fig3e_gate.py`, `morphology_qc.py` |
| [`regularization/`](results/tailored/regularization) | does the benchmark's ridge penalty bind? | `alpha_sweep.py` |
| [`genes/`](results/tailored/genes) | does holding out target genes change the rest? | `heldout_gene_check.py` |
| [`integrity/`](results/tailored/integrity) | does the instrumentation layer match independent references? | `check_instrumentation.py`, `verify_row_identity.py`, `metadata_join.py` |

## Key findings

Each is reproducible from the named table; the reasoning lives with the script that produced it.

**1. Split design matters more than encoder choice.** The entire between-encoder spread on the
benchmark's own protocol is **0.0977** Pearson (hoptimus1 0.4229 to resnet50 0.3252, 12 encoders).
Ignoring slide boundaries is worth **0.1575** — 1.61× that spread, positive in 30 of 30 encoder–task
cells — decomposing into spatial adjacency (0.0335) and a slide-level signature (0.1241).
Crossing institutions costs a further 0.0419. The decomposition itself was run on three encoders
(hoptimus0, uni_v2, virchow), so it does not include hoptimus1; the spread it is compared against is
the current 12-encoder one.
[`results/tailored/splits/`](results/tailored/splits)

**2. Pooled Pearson is not a constant yardstick.** Correlation computed on a pooled test set
carries between-patient variance in its denominator, so the same model scores higher on a more
heterogeneous test set — **exactly 0.0000** inflation when the test set is one patient, **+0.19**
when it spans nine. All split results therefore use within-patient Pearson, with the pooled value
retained so the artefact is measured rather than assumed.

**3. Table A13's encoder ranking tracks embedding width, not representation quality.**
Spearman(dim, score) = **−0.954** (p = 5.4 × 10⁻⁶) for `raw_ridge`, against **+0.735** for
`pca_ridge`. The 512-dim CONCH v1 wins the raw head. The penalty sweep explains why: at the
benchmark's `alpha = 100/(d × n_genes)` the fit is indistinguishable from unpenalised OLS
(|diff| ≤ 2.7e-4), and at raw width the Gram matrix is numerically singular (condition number
3.0 × 10¹⁵ at 1536 dims). That head is measuring conditioning.
[`results/tailored/regularization/`](results/tailored/regularization)

**4. Negative binomial is the right observation model; zero-inflation buys nothing.** NB beats
Poisson for **478 of 488** converged genes, and all 500 are overdispersed. ZINB beats NB for only
**14 of 474** — with median ΔAIC **−2.002**, matching AIC's exact penalty for one unused parameter
to three decimals. Sparsity follows the assay, not the tissue (median zero fraction 0.29 for
imaging-based tasks vs 0.61 for sequencing-based).
[`results/tailored/counts/`](results/tailored/counts)

**5. Slides are identifiable from frozen features; institutions are not resolved.** A linear probe
recovers slide identity at **0.980** balanced accuracy under spatial block cross-validation (0.990
under random splitting), with the nearest-training-spot distance verified to widen 2.83×. But the
only confound-free site contrast — two institutions, same tissue, same gene panel — reaches
**0.682** with just **2 of 11** encoders distinguishable from chance. The consequence of site shift
is measured; the mechanism is not established for institutions.
[`results/tailored/site_probes/`](results/tailored/site_probes)

**6. Patch geometry must be calibrated per sample.** Patch extents span **163–818 px** across the
72 samples (scale factor 0.727–3.654), including a factor-of-two difference between two samples of
the same task and assay, and 7 samples whose source region is *smaller* than 224 px. No constant
patch size — in pixels or microns — is correct. Validated by reproducing HEST Figure 3.e at
r = 0.4578 against the paper's 0.47 before any features were built.
[`results/tailored/morphology/`](results/tailored/morphology)

## Reproducing

```bash
# 1. environment (pinned; TRIDENT is an UNPINNED git dep upstream and its encoder
#    transforms have changed between versions, which would move Pearson silently)
cat env/REBUILD.md

# 2. a faithful run
python code/HEST/src/hest/bench/benchmark.py --config code/configs/pca_ridge__hoptimus0.yaml

# 3. normalise raw output into the canonical layout, then aggregate
python code/scripts/reorganize_repo.py --dry-run   # review, then drop the flag
python code/scripts/aggregate_results.py           # writes results/summary/
```

`benchmark.py` writes `<exp_code>::<timestamp>` directories and splits wall-limited runs across
`_part2` completions. `reorganize_repo.py` resolves that per (head, encoder, task) — the directory
holding `results_kfold.json` wins, partial task directories are dropped — so `aggregate_results.py`
walks a fixed tree and reports genuine gaps instead of hiding them behind a naming mismatch.

## Environment

- HEST `3ddb5eaf5bd2a8133e0c0e8015816489a3d99dc3`
- TRIDENT `f3eb7f301ce34f875306b545e6cfefc5d3335a5c` (v0.3.2) — pinned explicitly
- python 3.11.16, torch 2.14.0+cu130
- exact package set: [`env/requirements.lock`](env/requirements.lock), [`env/conda_env.yaml`](env/conda_env.yaml)

[`env/ENV_NOTES.txt`](env/ENV_NOTES.txt) records one conflict worth knowing before installing
anything here: STFlow's `scprep` pins `pandas<2.1`, which is ABI-incompatible with this project's
pandas 2.3.3. STFlow needs its own environment.

## What is not here

| excluded | why |
|---|---|
| `bench_data/` contents beyond the inventory | HEST-bench is a **gated** HuggingFace dataset; committing it would redistribute gated data |
| `embeddings/`, `*.h5`, `*.pkl`, `*.parquet` | large derived data; regenerable from the configs |
| `instrumentation/` | working tree for the 130M-row prediction parquets, CellViT segmentations and morphology parquets. Scripts write large intermediates there and their summary CSVs to `results/tailored/` |
| `code/stage5/` | third-party STFlow clone; upstream URL and pinned commit in [`code/stage5_provenance/`](code/stage5_provenance/STFLOW_SOURCE.txt) |
| narrative reports and working documents | kept outside the repository by design |

Superseded outputs were removed rather than kept alongside their replacements, so that every file
present is current. They remain recoverable from git history.

## Known limitations

1. **Gene-selection leakage, which no refit can detect.** The 50 target genes per task were
   variance-ranked over *every* spot, test folds included — a property of the shipped benchmark
   data. A leakage-free evaluation would recompute the ranking inside each fold. The held-out-gene
   check establishes only that the ridge fit does not couple targets, a different question.
2. **Across-task shift is not a scalar.** Even with training volume matched it varies monotonically
   with in-domain sample size, so any single number describes the reference task chosen.
3. **Institution shift rests on one task** (4 slides), the only one with two cohort sources of the
   same tissue and assay.
4. **`hoptimus1` covers `pca_ridge` only.** `raw_ridge` and `raw_xgb` have 11 encoders each;
   `pca_xgb` has 1 (resnet50), by design.
5. **Stage 5 training has not run** — CUDA-only against a saturated GPU queue.
