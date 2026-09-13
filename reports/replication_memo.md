# Stage 3 Replication Memo — HEST-1k Benchmark

Date: 2026-09-13 · Operator: weiyang · Host: UNC Longleaf
Reference: Jaume et al., *HEST-1k: A Dataset for Spatial Transcriptomics and Histology Image Analysis*, NeurIPS 2024
Repo: https://github.com/NicWYZ/HEST-1k-replication

## 1. Verdict

**The PCA+ridge head replicates.** Across 90 task-level comparisons (10 encoders x 9 paper
tasks) the mean absolute difference from Table 1 is **0.0053**, median
0.0030, max **0.0284**. 83% of cells agree within
0.01 and **100% within 0.03**. No comparison approaches the pre-registered investigation
threshold of 0.05, so no per-cell investigation was triggered.

Encoder-level averages agree to **0.0026** mean absolute difference
(max 0.0083), with Spearman rank correlation **0.976**. The paper's
headline ordering is reproduced: H-Optimus-0 first, UNIv1.5 second, ResNet50 last. The single
rank change is Virchow/Virchow2 swapping 3rd and 4th, which the paper itself separates by
0.0007.

## 2. Encoder-level comparison (average over the 9 paper tasks)

| paper name | paper | ours | diff | paper rank | our rank |
|---|---|---|---|---|---|
| H-Optimus-0 | 0.4146 | 0.4150 | +0.0004 | 1 | 1 |
| UNIv1.5 | 0.4090 | 0.4142 | +0.0052 | 2 | 2 |
| Virchow2 | 0.3984 | 0.4033 | +0.0049 | 3 | 4 |
| Virchow | 0.3977 | 0.4060 | +0.0083 | 4 | 3 |
| UNI | 0.3862 | 0.3856 | -0.0006 | 5 | 6 |
| GigaPath | 0.3853 | 0.3875 | +0.0022 | 6 | 5 |
| CONCH | 0.3709 | 0.3696 | -0.0013 | 7 | 7 |
| Phikon | 0.3656 | 0.3661 | +0.0005 | 8 | 8 |
| CTransPath | 0.3447 | 0.3468 | +0.0021 | 9 | 9 |
| ResNet50 (IN) | 0.3260 | 0.3252 | -0.0008 | 10 | 10 |

Remedis (paper average 0.3742) was **not run**: its weights require a separate access request
to Google and are not on HuggingFace. Ten of the paper's eleven encoders are covered. We
additionally ran CONCH v1.5 (0.3792) and the tenth task HCC, neither of which appears in the
paper; both are excluded from every comparison above.

## 3. Largest task-level discrepancies

| paper name | task | paper | ours | diff |
|---|---|---|---|---|
| Virchow | PAAD | 0.4875 | 0.5159 | +0.0284 |
| Virchow2 | SKCM | 0.6174 | 0.6398 | +0.0224 |
| UNIv1.5 | SKCM | 0.6401 | 0.6612 | +0.0211 |
| Virchow | LUNG | 0.5459 | 0.5663 | +0.0204 |
| UNI | PRAD | 0.3140 | 0.2943 | -0.0197 |
| Virchow | SKCM | 0.6088 | 0.6242 | +0.0154 |

All six are below 0.03. The largest, Virchow on PAAD (+0.0284), is a 3-fold task, so a single
fold shifting by 0.085 accounts for it. The pattern across the worst cells is mild positive
bias on small-k tasks (PAAD k=3, SKCM k=2, LUAD k=2), consistent with fold-level variance
rather than a protocol difference: the mean signed difference over all 90 cells is
+0.0021, i.e. our values run marginally high but within noise.

## 4. Confirmed against the paper

| item | paper source | status |
|---|---|---|
| log1p-only normalization | S5.2 "log1p-normalized expression" | confirmed; `normalize_adata` calls only `sc.pp.log1p` despite a docstring claiming total-count normalization |
| Variance-ranked top-50 genes | S5.1 "top 50 genes with the highest normalized variance" | confirmed; `var_50genes.json` is the dataclass default |
| Patch geometry | S5.1 "112x112 um ... 224x224-pixel patches at 20x" | confirmed; all 72 patch arrays are n x 224 x 224 x 3 |
| PCA 256 + ridge, adaptive regularization | Table 1 caption, S5.2 | confirmed; alpha = 100/(n_features x n_genes) |
| Patient-stratified k-fold, k = patients | S5.1 | confirmed via Table A11 (see S5) |
| XGBoost 100 estimators, max depth 3 | S5.2 | confirmed in `trainer.py`; paper does not state subsample/colsample, code uses 0.8/0.8 |
| Raw integer counts | S3.4 "No additional normalization was conducted" | confirmed; all 72 matrices integral |

## 5. Discrepancies found

**5.1 Figure 2a's reported correlation does not match its stated method.** The paper describes
"a logarithmic scaling law (Pearson correlation of R=0.81, P-value<0.01)" and the Figure 2a
caption plots parameters on a log scale. Using Table A12 parameter counts with Table 1
averages:

- log10(params) vs performance: **R = 0.942**, p < 0.0001 (11 encoders)
- raw params vs performance: **R = 0.811, p = 0.0025** (11 encoders)

R=0.81 is reproduced to three decimals only by correlating against *untransformed* parameter
counts. Our own values give the same picture (log R = 0.945, raw R = 0.818). The
qualitative claim - performance increases with model size, strongly and significantly - holds
under either computation; the specific statistic reported corresponds to the raw-parameter
correlation, not the log one the text describes. We initially hypothesised that excluding
Remedis explained the gap and tested it: including Remedis gives R = 0.942, so that
hypothesis was wrong and was discarded.

**5.2 ccRCC fold count has drifted from the paper.** S5.1 states ccRCC uses k/2-fold
cross-validation, and Table A11 lists 24 patients, implying 12 folds. The shipped splits
provide **6 folds of 4 test samples**, i.e. k/4. Our ccRCC values nonetheless agree with
Table 1 to within 0.012, so the coarser folds do not materially shift the mean - but the
standard deviations are computed over 6 folds rather than 12 and are not comparable.

**5.3 A tenth task ships that is not in the paper.** `HCC` (2 NCBI Visium samples, 4,196
patches, 2 folds) is present in `MahmoodLab/hest-bench` and commented out of the stock
`bench_config.yaml`. Run alongside and excluded from all comparisons, per instruction.

**5.4 TRIDENT's `uni_v2` may not be the paper's UNIv1.5.** Table A12 describes UNIv1.5 as
ViT-g with 1.13B parameters, 350K slides, 432M patches. TRIDENT's `uni_v2` resolves to
`MahmoodLab/UNI2-h`, whose name indicates a ViT-H. Our value (0.4142) sits 0.0052 above the
paper's UNIv1.5 (0.4090), which is consistent with the same or a closely related checkpoint,
but **we have not verified the parameter count of the loaded model**. Treat this row as
provisional. All other encoder identifications are unambiguous.

## 6. Two handoff claims the paper contradicts

Both were recorded as discrepancies in `bench_data/INVENTORY.md` on the handoff's authority
and are now **retracted**:

1. **"COAD was Visium in the paper and is now Xenium."** Table A11 lists COAD as **Xenium, 2
   patients, 4 samples** - exactly what ships. There was no post-paper technology change, and
   COAD is directly comparable (ResNet50 0.2500 vs 0.2528 published).
2. **"Fold counts should equal sample counts."** Table A11 reports patients and samples as
   separate columns. PRAD is 2 patients / 23 samples; COAD and READ are 2 patients / 4
   samples. Folds are patients, so every shipped fold count is correct except ccRCC (S5.2).
   This one was my error rather than the handoff's.

## 7. Open item: which head Table A14 used

The paper lists three regression models: (i) PCA-reduced embeddings + ridge, (ii) ridge, (iii)
XGBoost with 100 estimators and max depth 3. Reading (ii) as "ridge without PCA" - which
Table A13's much lower values confirm - leaves (iii) ambiguous: XGBoost on PCA-256, or on raw
embeddings? The benchmark code applies PCA whenever `dimreduce == 'PCA'` regardless of method,
so the authors' own default config would give XGBoost on PCA-256. Rather than argue the point,
both variants are running on ResNet50; Table A14 reports 0.326 for ResNet50, so whichever
variant reproduces it settles the question empirically. Result pending.

## 8. What was not checked

- Table A13 (ridge without PCA) comparison is incomplete: 2 of 11 encoders finished at the
  time of writing. Note that A13 is **not** directly comparable to a naive rerun, because
  ridge alpha is recomputed as 100/(d x 50) and therefore changes with embedding dimension -
  0.0078 under PCA-256 versus 0.0020 for a 1024-dim encoder. Any A13 gap conflates removing
  PCA with a 4x change in regularization.
- Table A14 (XGBoost) comparison not yet possible; see S7.
- Figure 2b (data scaling law, R=0.48) not attempted: it needs pretraining patch counts, which
  Table A12 gives, but the claim is explicitly weak in the paper and is not load-bearing here.
- Figure 3e (nuclear area vs GATA3, r~0.47) is a Stage 4e acceptance check, not yet run.
- The identity of the loaded `uni_v2` checkpoint (S5.4).
- Per-fold standard deviations were computed but not compared against the paper's; only means
  were compared.

## 9. Recommendation

Stage 3 passes for the PCA+ridge head, which is the paper's headline result and the one the
leaderboard tracks. The protocol is faithful: an exact hit on ResNet50 (0.3252 vs the
leaderboard's 0.3252) plus 100% of cells within 0.03 of Table 1 leaves little room for a
systematic error in splits, gene selection, normalization, or the regression head.

Proceed to Stage 4 instrumentation. The two head-variant tables (A13, A14) are worth
completing for the record but are not a gate: they vary the probe, not the data pipeline, and
the pipeline is what Stage 4 depends on.
