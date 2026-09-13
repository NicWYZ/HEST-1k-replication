# HEST-1k Benchmark Replication

Replication of the HEST-1k benchmark (Jaume et al., NeurIPS 2024, arXiv:2406.16192) on UNC
Longleaf, instrumented so its byproducts feed two methodological projects on calibrated
uncertainty and valid inference for histology-to-expression prediction.

**This repository is private and contains no gated data.** See "What is not here".

## Status

| Stage | State |
|---|---|
| 0 — Access and environment | complete |
| 1 — Benchmark data inventory | complete |
| 2 — Faithful runs (PCA+ridge, ridge, XGBoost) | in progress |
| 3 — Verification vs paper and leaderboard | not started |
| 4 — Instrumentation | not started |
| 5 — STFlow baseline (optional) | not started |

## Environment

Reproduced exactly by `env/REBUILD.md`. TRIDENT is an **unpinned** git dependency in HEST's
`pyproject.toml` and its encoder transforms have changed between versions, which would shift
Pearson values with no error raised — so it is pinned explicitly in the rebuild recipe.

- HEST `3ddb5eaf5bd2a8133e0c0e8015816489a3d99dc3`
- TRIDENT `f3eb7f301ce34f875306b545e6cfefc5d3335a5c` (v0.3.2)
- python 3.11.16, torch 2.14.0+cu130
- Exact package set: `env/requirements.lock`, `env/conda_env.yaml`

## Layout

```
bench_data/INVENTORY.md   benchmark inventory + discrepancy log   (data itself untracked)
code/configs/             benchmark configs, one per encoder x head
code/scripts/             inventory, instrumentation, analysis scripts
env/                      versions.txt, requirements.lock, REBUILD.md
results/faithful/         per-split results.json / summary.json / dataset_results.csv
results/tailored/         Stage 4 additional runs
instrumentation/          joined tables (large outputs untracked)
reports/                  replication memo, discrepancy table, motivation draft
figures/                  publication figures
MANIFEST.md               path, size and SHA256 of every large artifact left on Longleaf
```

## Benchmark data

Ten tasks, 72 samples, 236,495 patches, 29 folds. Full per-task and per-sample tables in
`bench_data/INVENTORY.md`. Note the benchmark has moved on from the paper: COAD is now Xenium
(the paper describes it as Visium), and `HCC` is a tenth task absent from the paper — it is run
alongside but excluded from all paper and leaderboard comparisons.

## What is not here

`bench_data/` (40 GB), `embeddings/` (several GB), `inference_dump.pkl` (~2 GB per head) and the
Stage 4a prediction table are **not tracked**. Two reasons: GitHub's 100 MB per-file limit, and
the fact that `MahmoodLab/hest-bench` is gated — `inference_dump.pkl` carries `targets_all`,
the measured expression, so committing it would redistribute gated data in derived form.

They live on Longleaf at `/work/users/w/e/weiyang/hest_replication/`. `MANIFEST.md` records the
path, size and SHA256 of each so a collaborator can verify a copy obtained through proper
channels. Everything needed to regenerate them is committed.

To reproduce from scratch: follow `env/REBUILD.md`, accept the terms on
`MahmoodLab/hest-bench`, then run the configs in `code/configs/` in stage order.

## Provenance

Every results directory carries a `PROVENANCE.txt` with SLURM job ID, commit, date and config.
