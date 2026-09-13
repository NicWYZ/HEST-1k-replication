# hest-bench INVENTORY (Stage 1)

Generated: 2026-09-13T14:23:34  
Source: HuggingFace `MahmoodLab/hest-bench`, `ignore_patterns=['fm_v1/*']`  
Local path: `/work/users/w/e/weiyang/hest_replication/bench_data` (40 GB, 294 files)  
HEST commit: `3ddb5eaf5bd2a8133e0c0e8015816489a3d99dc3` · TRIDENT: `f3eb7f301ce34f875306b545e6cfefc5d3335a5c` (v0.3.2)

## Per-task summary

| task | samples | cohort src | technology | folds | adata spots | patches | patch retention |
|---|---|---|---|---|---|---|---|
| CCRCC | 24 | INT | Visium | 6 | 74,220 | 74,220 | 100.0% |
| COAD | 4 | TENX | Xenium (pseudo-Visium 55um) | 2 | 18,523 | 15,651 | 84.8% |
| HCC | 2 | NCBI | Visium | 2 | 4,248 | 4,196 | 98.7% |
| IDC | 4 | NCBI/TENX | Xenium (pseudo-Visium 55um) | 4 | 44,974 | 35,536 | 80.5% |
| LUNG | 2 | TENX | Xenium (pseudo-Visium 55um) | 2 | 7,505 | 5,206 | 68.3% |
| LYMPH_IDC | 4 | NCBI | Visium | 4 | 19,964 | 19,964 | 100.0% |
| PAAD | 3 | TENX | Xenium (pseudo-Visium 55um) | 3 | 9,793 | 7,571 | 78.0% |
| PRAD | 23 | MEND | Visium | 2 | 62,710 | 62,710 | 100.0% |
| READ | 4 | ZEN | Visium | 2 | 8,407 | 8,407 | 100.0% |
| SKCM | 2 | TENX | Xenium (pseudo-Visium 55um) | 2 | 5,716 | 3,034 | 57.8% |
| **TOTAL** | **72** | | | **29** | **256,060** | **236,495** | **92.4%** |

## Acceptance checks

| check | expected | result |
|---|---|---|
| Tasks present | 9 | **10 — `HCC` is additional** (see Discrepancies) |
| Patch HDF5 shape | n_spots x 224 x 224 x 3 | PASS — all 72 samples, uint8 |
| Counts are raw integers | integer | PASS — all 72 samples integral (dtypes `uint16` Xenium / `float32` Visium, max 18,438) |
| Genes in task gene list | 50 | PASS — 50 for all 10 tasks |
| All 50 genes present per sample | yes | PASS — 72/72 samples, zero missing |
| Split CSVs | k train/test pairs | PASS — 29 folds total; columns `sample_id, patches_path, expr_path` |
| Patch barcodes vs `adata.obs_names` | exact match | **REVISED: strict subset, PASS 72/72** (see below) |

### Barcode relationship (revised criterion)

The handoff expects patch barcodes to match `adata.obs_names` *exactly*. They do not, and should not. 
Patch files carry **fewer** spots than the AnnData (92.4% overall; as low as 57.8% for SKCM) because 
patches are only extracted where a full 224x224 window fits the tissue image. The correct invariant is 
**patch barcodes are a strict subset of `adata.obs_names`**, which holds for **72/72 samples with zero 
violations and no duplicates**.

This is safe because `benchmark.py` aligns by *label*, not position:

```python
barcodes = assets['barcodes'].flatten().astype(str).tolist()   # from embedding HDF5
adata = load_adata(expr_path, genes=genes, barcodes=barcodes, ...)
#   -> load_adata does:  adata = adata[barcodes]
```
`adata[barcodes]` reorders the AnnData to the embedding's barcode order and drops unmatched rows, so 
row identity in `inference_dump.pkl` is reconstructible for Stage 4a.

Barcode formats differ by platform: Xenium tasks use pseudo-Visium grid IDs (`000x002`), 
Visium tasks use 10x barcodes (`AAACACCAATAACTGC-1`).

## Discrepancies vs the handoff

| # | Handoff says | Actual | Impact |
|---|---|---|---|
| 1 | 9 tasks | **10** — `HCC` (2 NCBI Visium samples, 4,196 patches, 2 folds) ships in hest-bench and is absent from both the handoff and `bench_config.yaml` | Scope decision needed |
| 2 | ccRCC `INT1..INT24`, splits = n patients | 24 samples but **6 folds** (4 test / 20 train each) | Confirms handoff's STFlow footnote |
| 3 | PRAD `MEND139..MEND162`, 23 samples | 23 samples but **2 folds** (8/15 and 15/8), not 23 | Fold count assumption wrong |
| 4 | ~100k benchmark patches | **236,495** | Extraction cost ~2.4x the estimate |
| 5 | COAD is Xenium (updated post-paper) | Confirmed — 4 TENX Xenium samples, 541-gene panel | Paper Table 1 COAD will not match |
| 6 | `normalize_adata` is log1p only | Confirmed — docstring claims total-count normalization, body calls only `sc.pp.log1p` | Faithful run must not add normalization |
| 7 | Ridge `fit_intercept=False`, alpha=100/(256x50) | Confirmed — `alpha = 100/(X.shape[1]*y.shape[1])`, `solver='lsqr'` | As specified |
| 8 | (not mentioned) | **CCRCC spans two gene spaces**: INT1-12 have 36,601 vars, INT13-24 have 17,943 | All 50 target genes present in both; no action needed |
| 9 | (not mentioned) | **PAAD/TENX116 has 538 genes** vs 541 for other Xenium samples | All 50 target genes present |
| 10 | (not mentioned) | Two gene lists ship: `mean_50genes.json` and `var_50genes.json`. **COAD and LUNG ship only `var_`** | Default `gene_list='var_50genes.json'` matches the paper's 'most variable'; all tasks work |
| 11 | Config drives all params | Defaults live in a **dataclass** (`gene_list='var_50genes.json'`, `normalize=True`, `dimreduce='PCA'`, `latent_dim=256`, `method='ridge'`), not argparse (all argparse defaults are `None`) | Config file overrides CLI args |
| 12 | (not mentioned) | Extra dirs: `IDC/old/`, `COAD/patches_vis/` | Not used; ignore |

## Per-sample detail

| task | sample | cohort | adata spots | patches | retention | n_vars | X dtype |
|---|---|---|---|---|---|---|---|
| CCRCC | INT1 | INT | 1,084 | 1,084 | 100.0% | 36,601 | float32 |
| CCRCC | INT10 | INT | 1,983 | 1,983 | 100.0% | 36,601 | float32 |
| CCRCC | INT11 | INT | 1,439 | 1,439 | 100.0% | 36,601 | float32 |
| CCRCC | INT12 | INT | 1,451 | 1,451 | 100.0% | 36,601 | float32 |
| CCRCC | INT13 | INT | 4,359 | 4,359 | 100.0% | 17,943 | float32 |
| CCRCC | INT14 | INT | 4,562 | 4,562 | 100.0% | 17,943 | float32 |
| CCRCC | INT15 | INT | 4,940 | 4,940 | 100.0% | 17,943 | float32 |
| CCRCC | INT16 | INT | 3,206 | 3,206 | 100.0% | 17,943 | float32 |
| CCRCC | INT17 | INT | 3,585 | 3,585 | 100.0% | 17,943 | float32 |
| CCRCC | INT18 | INT | 4,915 | 4,915 | 100.0% | 17,943 | float32 |
| CCRCC | INT19 | INT | 4,948 | 4,948 | 100.0% | 17,943 | float32 |
| CCRCC | INT2 | INT | 2,580 | 2,580 | 100.0% | 36,601 | float32 |
| CCRCC | INT20 | INT | 4,860 | 4,860 | 100.0% | 17,943 | float32 |
| CCRCC | INT21 | INT | 4,975 | 4,975 | 100.0% | 17,943 | float32 |
| CCRCC | INT22 | INT | 3,829 | 3,829 | 100.0% | 17,943 | float32 |
| CCRCC | INT23 | INT | 4,755 | 4,755 | 100.0% | 17,943 | float32 |
| CCRCC | INT24 | INT | 4,510 | 4,510 | 100.0% | 17,943 | float32 |
| CCRCC | INT3 | INT | 2,007 | 2,007 | 100.0% | 36,601 | float32 |
| CCRCC | INT4 | INT | 1,349 | 1,349 | 100.0% | 36,601 | float32 |
| CCRCC | INT5 | INT | 1,186 | 1,186 | 100.0% | 36,601 | float32 |
| CCRCC | INT6 | INT | 1,678 | 1,678 | 100.0% | 36,601 | float32 |
| CCRCC | INT7 | INT | 2,374 | 2,374 | 100.0% | 36,601 | float32 |
| CCRCC | INT8 | INT | 1,949 | 1,949 | 100.0% | 36,601 | float32 |
| CCRCC | INT9 | INT | 1,696 | 1,696 | 100.0% | 36,601 | float32 |
| COAD | TENX111 | TENX | 6,138 | 5,079 | 82.7% | 541 | uint16 |
| COAD | TENX147 | TENX | 3,997 | 3,417 | 85.5% | 541 | uint16 |
| COAD | TENX148 | TENX | 4,379 | 3,535 | 80.7% | 541 | uint16 |
| COAD | TENX149 | TENX | 4,009 | 3,620 | 90.3% | 541 | uint16 |
| HCC | NCBI642 | NCBI | 1,987 | 1,941 | 97.7% | 36,601 | float32 |
| HCC | NCBI643 | NCBI | 2,261 | 2,255 | 99.7% | 36,601 | float32 |
| IDC | NCBI783 | NCBI | 3,869 | 3,005 | 77.7% | 541 | uint16 |
| IDC | NCBI785 | NCBI | 4,180 | 4,010 | 95.9% | 541 | uint16 |
| IDC | TENX95 | TENX | 11,845 | 7,760 | 65.5% | 541 | uint16 |
| IDC | TENX99 | TENX | 25,080 | 20,761 | 82.8% | 541 | uint16 |
| LUNG | TENX118 | TENX | 3,115 | 1,944 | 62.4% | 541 | uint16 |
| LUNG | TENX141 | TENX | 4,390 | 3,262 | 74.3% | 541 | uint16 |
| LYMPH_IDC | NCBI681 | NCBI | 4,992 | 4,992 | 100.0% | 33,931 | float32 |
| LYMPH_IDC | NCBI682 | NCBI | 4,988 | 4,988 | 100.0% | 33,931 | float32 |
| LYMPH_IDC | NCBI683 | NCBI | 4,992 | 4,992 | 100.0% | 33,931 | float32 |
| LYMPH_IDC | NCBI684 | NCBI | 4,992 | 4,992 | 100.0% | 33,931 | float32 |
| PAAD | TENX116 | TENX | 3,090 | 2,010 | 65.0% | 538 | uint16 |
| PAAD | TENX126 | TENX | 2,190 | 1,951 | 89.1% | 541 | uint16 |
| PAAD | TENX140 | TENX | 4,513 | 3,610 | 80.0% | 541 | uint16 |
| PRAD | MEND139 | MEND | 3,749 | 3,749 | 100.0% | 33,538 | float32 |
| PRAD | MEND140 | MEND | 1,935 | 1,935 | 100.0% | 33,538 | float32 |
| PRAD | MEND141 | MEND | 1,794 | 1,794 | 100.0% | 33,538 | float32 |
| PRAD | MEND142 | MEND | 2,997 | 2,997 | 100.0% | 33,538 | float32 |
| PRAD | MEND143 | MEND | 3,816 | 3,816 | 100.0% | 33,538 | float32 |
| PRAD | MEND144 | MEND | 4,074 | 4,074 | 100.0% | 33,538 | float32 |
| PRAD | MEND145 | MEND | 1,418 | 1,418 | 100.0% | 33,538 | float32 |
| PRAD | MEND146 | MEND | 1,964 | 1,964 | 100.0% | 33,538 | float32 |
| PRAD | MEND147 | MEND | 2,335 | 2,335 | 100.0% | 33,538 | float32 |
| PRAD | MEND148 | MEND | 1,633 | 1,633 | 100.0% | 33,538 | float32 |
| PRAD | MEND149 | MEND | 1,851 | 1,851 | 100.0% | 33,538 | float32 |
| PRAD | MEND150 | MEND | 1,751 | 1,751 | 100.0% | 33,538 | float32 |
| PRAD | MEND151 | MEND | 2,600 | 2,600 | 100.0% | 33,538 | float32 |
| PRAD | MEND152 | MEND | 3,082 | 3,082 | 100.0% | 33,538 | float32 |
| PRAD | MEND153 | MEND | 1,820 | 1,820 | 100.0% | 33,538 | float32 |
| PRAD | MEND154 | MEND | 2,736 | 2,736 | 100.0% | 33,538 | float32 |
| PRAD | MEND156 | MEND | 3,554 | 3,554 | 100.0% | 33,538 | float32 |
| PRAD | MEND157 | MEND | 3,190 | 3,190 | 100.0% | 33,538 | float32 |
| PRAD | MEND158 | MEND | 3,092 | 3,092 | 100.0% | 33,538 | float32 |
| PRAD | MEND159 | MEND | 3,856 | 3,856 | 100.0% | 33,538 | float32 |
| PRAD | MEND160 | MEND | 4,079 | 4,079 | 100.0% | 33,538 | float32 |
| PRAD | MEND161 | MEND | 2,775 | 2,775 | 100.0% | 33,538 | float32 |
| PRAD | MEND162 | MEND | 2,609 | 2,609 | 100.0% | 33,538 | float32 |
| READ | ZEN36 | ZEN | 1,691 | 1,691 | 100.0% | 36,601 | float32 |
| READ | ZEN40 | ZEN | 2,128 | 2,128 | 100.0% | 36,601 | float32 |
| READ | ZEN48 | ZEN | 2,385 | 2,385 | 100.0% | 36,601 | float32 |
| READ | ZEN49 | ZEN | 2,203 | 2,203 | 100.0% | 36,601 | float32 |
| SKCM | TENX115 | TENX | 3,886 | 1,741 | 44.8% | 541 | uint16 |
| SKCM | TENX117 | TENX | 1,830 | 1,293 | 70.7% | 541 | uint16 |
