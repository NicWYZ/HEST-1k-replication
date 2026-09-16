# Stage 0 + Stage 1 Report — HEST-1k Replication

Date: 2026-09-13 · Operator: weiyang · Host: UNC Longleaf
Root: `/work/users/w/e/weiyang/hest_replication`

## 1. Stage and status

- **Stage 0 (Access and environment): COMPLETE.** All three acceptance checks pass.
- **Stage 1 (Benchmark data): COMPLETE**, with one acceptance criterion revised (below) and 12 logged discrepancies.
- **Stage 2 smoke test: PASSED** (ResNet50 x IDC, end to end, 3m05s).
- Not blocked. Two scope questions for the oversight chat before the full Stage 2 launch.

## 2. What was run

| # | SLURM job | What | Partition | Result |
|---|---|---|---|---|
| 1 | 1027353 | Compute-node internet / mount probe | spill | ok |
| 2 | 1027355 | GPU node probe (nvidia-smi) | l40-gpu | ok |
| 3 | 1027400 | Miniforge + `hest` env + HEST/TRIDENT install | hov | ok, 14 min |
| 4 | 1027661 | GPU acceptance check in env | l40-gpu | ok |
| 5 | 1027662 | `snapshot_download` hest-bench | spill | ok, 40 GB / 294 files |
| 6 | 1027799 | Inventory pass | spill | ok |
| 7 | (batch) | Barcode subset check, all 72 samples | general | ok |
| 8 | (batch) | 50-gene presence check, all 72 samples | general | ok |
| 9 | 1029002 | **Smoke test** `benchmark.py` resnet50 x IDC | l40-gpu | ok, 3m05s |

Environment (`env/versions.txt`): python 3.11.16 · torch 2.14.0+cu130 · timm 1.0.29 ·
transformers 4.57.6 · scanpy 1.11.5 · scikit-learn 1.9.1 · numpy 2.4.6 · libvips 8.18.6 · openslide 4.0.1.
**HEST** `3ddb5eaf5bd2a8133e0c0e8015816489a3d99dc3` · **TRIDENT** `f3eb7f301ce34f875306b545e6cfefc5d3335a5c` (v0.3.2).

Smoke-test config hash inputs: `seed=1, batch_size=128, gene_list=var_50genes.json, method=ridge,
normalize=True, dimreduce=PCA, latent_dim=256`.

## 3. Acceptance checks and actual numbers

### Stage 0
| check | result |
|---|---|
| `import hest, trident` | PASS |
| GPU test | PASS — L40S, 47.7 GB, capability 8.9, `torch.cuda.is_available()` True; TRIDENT `encoder_factory("resnet50")` forward pass returns (4, 1024) |
| HF login | PASS — `hf auth whoami` = `weiyangz` |

Gated-repo probe (16 repos): datasets `MahmoodLab/hest` and `MahmoodLab/hest-bench` both OK.
**Three** model repos returned GATED-no-access: `hoptimus1`, `hibou_l`, `h0-mini`.
**None of the paper's ten encoders is affected** — all ten plus `conch_v15` and `midnight12k` are accessible.
(The handoff anticipated only H-Optimus-1; `hibou_l` and `h0-mini` are additional, but neither is in the plan's encoder list.)

### Stage 1
| check | expected | result |
|---|---|---|
| Tasks present | 9 | **10** — `HCC` additional |
| Patch HDF5 shape | n_spots x 224 x 224 x 3 | PASS, 72/72, uint8 |
| Counts raw integers | integer | PASS, 72/72 (uint16 Xenium / float32 Visium, max 18,438) |
| Genes per task list | 50 | PASS, 50 for all 10 |
| All 50 genes present per sample | — | PASS, 72/72, zero missing |
| Split CSVs | k train/test pairs | PASS — 29 folds total |
| Barcodes vs `adata.obs_names` | exact match | **REVISED to subset — PASS 72/72** |

Totals: 72 samples · 256,060 adata spots · **236,495 patches** · 92.4% retention · 29 folds.

### Revised barcode criterion
Exact equality is the wrong test and fails for 6 of 10 tasks. Patch files carry fewer spots than the
AnnData (92.4% overall, as low as 57.8% on SKCM) because a patch is only extracted where a full
224x224 window fits. The correct invariant — **patch barcodes are a strict subset of `adata.obs_names`** —
holds for 72/72 with zero violations and no duplicates. This is safe because `benchmark.py` aligns by
label, not position: it reads barcodes from the embedding HDF5 and calls `adata[barcodes]`, which
reorders the AnnData to the embedding order and drops unmatched rows. Row identity in
`inference_dump.pkl` is therefore reconstructible for Stage 4a.

### Smoke test (ResNet50 x IDC, faithful settings)
| split | held out | n_train | n_test | Pearson mean |
|---|---|---|---|---|
| 0 | TENX99 | 14,775 | 20,761 | 0.4081 |
| 1 | TENX95 | 27,776 | 7,760 | 0.5138 |
| 2 | NCBI785 | 31,526 | 4,010 | 0.4555 |
| 3 | NCBI783 | 32,531 | 3,005 | 0.5180 |

**IDC mean = 0.4739.** Per-fold `n_train + n_test = 35,536` in every fold, matching the IDC patch count
exactly, and each fold's `n_test` matches the held-out sample's patch count exactly — confirming
leave-one-patient-out with no leakage or dropped rows. `alpha = 0.0078125 = 100/(256x50)`, confirming
the handoff's formula. All expected outputs present: `dataset_results.csv/json`, per-split
`results.json`, `summary.json`, `inference_dump.pkl`, and cached per-sample embeddings.

## 4. Discrepancies and open questions

Full table in `bench_data/INVENTORY.md`. The ones that change decisions:

1. **`HCC` is a 10th task** (2 NCBI Visium samples, 4,196 patches, 2 folds) shipping in hest-bench,
   absent from the handoff and commented out of `bench_config.yaml`. **Scope question.**
2. **Fold counts are not patient counts.** CCRCC: 24 samples but 6 folds (confirms the handoff's
   STFlow footnote). PRAD: 23 samples but **2** folds (8/15, 15/8) — the handoff's "k = number of
   patients" is wrong here.
3. **236,495 patches, not ~100k** — 2.4x the handoff's estimate. But see Section 6: the smoke test
   makes this a non-issue.
4. **Two gene lists ship**; COAD and LUNG ship only `var_50genes.json`. The dataclass default is
   `var_50genes.json`, which matches the paper's "50 most variable genes" and exists for all tasks.
5. **Defaults live in a `BenchmarkConfig` dataclass, not argparse** (all argparse defaults are `None`).
   Config-file values override CLI args. Relevant because `--normalize` is `type=bool`, where
   `--normalize False` would evaluate to `True`; we set everything via config file instead.
6. **CCRCC spans two gene spaces** (INT1-12: 36,601 vars; INT13-24: 17,943) and **PAAD/TENX116 has 538
   genes** vs 541. All 50 target genes are present everywhere, so no action needed — but this is why
   the gene-presence check was worth running.
7. `normalize_adata` is log1p only, despite its docstring claiming total-count normalization. Confirmed
   in source. Ridge uses `fit_intercept=False`, `solver='lsqr'`. Both as the handoff states.
8. TRIDENT is an **unpinned** git dependency in `pyproject.toml`. Resolved commit now recorded.

**Open questions for the oversight chat:**
- **Q1.** Include `HCC`? Recommendation: run it alongside the nine as a logged extra (1.8% of patches,
  minutes of compute) but exclude it from the paper/leaderboard comparison table, per the Section 6.0
  "faithful first, tailored alongside, never instead" principle.
- **Q2.** Pin TRIDENT to `f3eb7f30` in our install, or leave it floating? Recommendation: pin.

## 5. What was NOT checked

- **`ctranspath` weight download is untested.** It is one of the paper's ten. TRIDENT loads it via the
  `timm_ctp` fork rather than a plain HF repo, so my gated-repo probe could not test it (my guessed
  repo id returned NOT-FOUND, which reflects the guess, not availability). Will be exercised on first
  Stage 2 run.
- No encoder other than `resnet50` has been run. No ViT-giant memory behaviour measured on the L40S.
- Paper/leaderboard comparison not yet done — that is Stage 3. The 0.4739 IDC figure above is
  reported as-is and has **not** been compared against any published value.
- `HCC` technology assignment (Visium) is inferred from 10x-style barcodes and a 36,601-gene space,
  not from HEST metadata. Not yet cross-checked against the metadata CSV.
- `IDC/old/` and `COAD/patches_vis/` were not inspected; assumed unused.
- Storage: 40 GB bench_data + 8.8 GB env. `/work` has 535 TB free, so no quota risk. Home quota
  untouched (229 MB of 50 GB).

## 6. Proposed next step

Two facts reshape the Stage 2 plan favourably:

- The smoke test did **all** of IDC — 35,536 patches, extraction plus four folds — in **3m05s** on one
  L40S. Scaling to 236,495 patches puts ResNet50 at roughly 20 minutes for the whole benchmark.
  ViT-giant encoders will be slower per patch, but this is hours of GPU total, not the "few GPU-hours
  each" the handoff budgeted.
- GPU queue wait is currently ~20 minutes for short walls on `l40-gpu`, not the multi-day pend this
  account has seen before. There is a 70-task NextBrain array of yours pending on `a100-gpu`; keeping
  our walls short and preferring `l40-gpu` avoids competing with it.

Proposed: launch Stage 2 `faithful_pca_ridge` as one SLURM job per encoder (11 jobs: the ten from the
paper plus `conch_v15`), 2-hour walls, `-p l40-gpu,a100-gpu`, all 9 tasks (+HCC pending Q1). Embeddings
cache per sample, so the subsequent `faithful_ridge` (no PCA) and `faithful_xgb` runs are CPU-only.
Awaiting Q1/Q2 before launching.
