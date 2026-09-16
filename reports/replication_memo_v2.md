# HEST-1k replication and instrumentation — memo

Generated 2026-09-14T03:03  
Format follows handoff Section 9.

## 1. Stage and status

| stage | status |
|---|---|
| 0 · environment and access | complete |
| 1 · benchmark data inventory | complete, one criterion revised (see §4) |
| 2 · faithful runs | PCA+ridge 11/11 encoders; ridge-no-PCA 11/11; XGBoost raw 1/11 + 10 running; hoptimus1 BLOCKED (gated weights) |
| 3 · verification | complete |
| 4a · joined predictions + metadata | complete |
| 4c · count diagnostics | complete |
| 4d · site-predictability probe | complete |
| 4e · morphology + Figure 3.e gate | gate PASSED; feature rebuild running |
| 4f · held-out-gene check | complete |
| 4b · split decomposition | running (four-design version) |

## 2. What was run

- Benchmark data: 72 samples over 10 tasks, 236,495 patches, 50 target genes per task.
- Heads: pca_ridge, ridge_nopca, xgb_nopca, xgb_pca.
- Encoders: conch_v1, conch_v15, ctranspath, gigapath, hoptimus0, phikon, resnet50, uni_v1, uni_v2, virchow, virchow2 (11 of the 12 named in the handoff).
- Instrumentation: 130,072,250 prediction rows across 10 per-task table pairs.
- Config defaults read from the `BenchmarkConfig` dataclass, not argparse: `seed=1`, `batch_size=128`, `gene_list='var_50genes.json'`, `normalize=True`, `dimreduce='PCA'`, `latent_dim=256`, `method='ridge'`.
- XGBoost params verified exact against the paper: `n_estimators=100`, `learning_rate=0.1`, `max_depth=3`, `subsample=0.8`.

## 3. What was checked, with numbers

### 3.1 Table 1 / live leaderboard (03.04.26)

PCA+ridge against the leaderboard, 99 cells (11 encoders x 9 tasks; HCC is not a leaderboard task): mean |diff| **0.0002**, median 0.0000, max 0.0155. Cells over the 0.03 threshold: **0/99**.

| encoder | ours (9 tasks) | leaderboard | diff |
|---|---|---|---|
| hoptimus0 | 0.4150 | 0.4150 | +0.0000 |
| uni_v2 | 0.4142 | 0.4141 | +0.0001 |
| virchow | 0.4060 | 0.4061 | -0.0001 |
| virchow2 | 0.4033 | 0.4034 | -0.0001 |
| gigapath | 0.3875 | 0.3875 | -0.0000 |
| uni_v1 | 0.3856 | 0.3873 | -0.0017 |
| conch_v15 | 0.3792 | 0.3792 | -0.0000 |
| conch_v1 | 0.3696 | 0.3696 | +0.0000 |
| phikon | 0.3661 | 0.3660 | +0.0001 |
| ctranspath | 0.3468 | 0.3468 | +0.0000 |
| resnet50 | 0.3252 | 0.3252 | +0.0000 |

Largest single deviation: uni_v1 on IDC, 0.5735 vs 0.5890. uni_v1 is gated, so a checkpoint-version difference is the natural hypothesis.

### 3.2 Head variants

| head | ours (resnet50, 9 tasks) | paper | diff | role |
|---|---|---|---|---|
| pca_ridge | 0.3252 | 0.3252 | +0.0000 | replicates Table 1 |
| ridge_nopca | 0.2843 | 0.314 | -0.0297 | replicates Table A13 |
| xgb_nopca | 0.3278 | 0.326 | +0.0018 | A14 candidate — SELECTED |
| xgb_pca | 0.3046 | 0.326 | -0.0214 | A14 candidate — rejected |

**Table A14 resolved.** XGBoost on raw embeddings reproduces 0.326 to +0.0018; the PCA-256 variant misses by -0.0214. The paper fed raw features to XGBoost. Both rows target the same 0.326, so the rejected row's gap is the evidence, not a replication failure.

**Table A13 is the one unexplained gap**: -0.0297, just inside the 0.03 threshold. Suspected mechanism is `alpha = 100/(d*n_genes)` falling from 0.0078 (PCA-256) to 0.00195 (1024 raw dims) while raw features are standardised but not decorrelated. An alpha sweep is running to settle it. Note the direction reverses by head: dropping PCA hurts ridge (0.3252 -> 0.2843) but helps XGBoost (0.3046 -> 0.3278).

### 3.3 Figure 2.a — parameter-count trend

R = 0.811 on raw parameter counts reproduces the paper's stated 0.81. The log-scale correlation its caption implies is 0.942. Logged as a reporting discrepancy in the paper.

### 3.4 Stage 4a integrity

130,072,250 prediction rows. Five assertions pass on 10/10 tasks: spot counts match the independent inventory (236,495 total), 50 gene rows per spot, each spot in exactly one test fold, prediction rows = spots x 50 x encoders, stored raw counts integral. Row identity proven against a permuted null.

Metadata joined for 72/72 samples. Audits: my derived technology labels agree with `st_technology` 72/72; **zero** shipped folds place a patient in both train and test across all 10 tasks, so HEST's patient-stratification holds.

### 3.5 Count diagnostics (handoff 4c)

- Poisson decisively rejected: NB preferred in 478/488 genes, median delta_AIC 57,812; Fano > 1 for 500/500 genes.
- ZINB adds nothing: preferred in only 14/474 genes, median delta_AIC -2.002 against the **-2.000** predicted if the zero-inflation parameter buys zero likelihood.
- Not criterion-dependent: BIC agrees on 468/474 genes.
- 14 genes flagged as diverged NB fits (|delta_AIC| > 100 while statsmodels reported convergence), retained and flagged rather than dropped.
- Zero fraction is a platform effect: Xenium 0.286 vs Visium 0.610.

**Implication for Topic A**: plain negative binomial is the right observation model.

### 3.6 Site predictability (handoff 4d)

| probe | classes | balanced acc range | beats chance at 95% | confounded |
|---|---|---|---|---|
| technology | 2 | 0.9814–0.9983 | 11/11 | yes |
| cohort_source | 5 | 0.9225–0.9586 | 11/11 | yes |
| idc_institution | 2 | 0.4603–0.9103 | 2/11 | no |

The two high probes are the confounded ones. Cohort source is near-collinear with tissue (INT only in CCRCC, MEND only in PRAD, ZEN only in READ) and with technology; technology is additionally **perfectly** collinear with fixation (all 15 Xenium samples FFPE, all 33 annotated Visium Fresh Frozen). The one confound-free arm — TENX vs NCBI within IDC, same tissue and assay — is distinguishable from chance for only 2 of 11 encoders on 4 folds.

**So the mechanism claim does not survive**: whether embeddings encode institution is unresolved on this data. The consequence claim does survive and is what Topic A needs.

### 3.7 Morphology gate (handoff 4e)

**PASS.** NCBI785 gives Pearson(GATA3, mean neoplastic nuclear area per spot) = **+0.4578** against the paper's 0.47, |diff| 0.0122. Raw counts match better than log1p (+0.4248).

Two caveats recorded. Identifying the sample by nucleus count **failed** — the paper's 168,033 and 342,018 match none of our per-slide totals; the correlation identified it instead, the other three samples giving +0.133, +0.012, -0.048. And the relationship is **sample-specific**, not a general IDC property.

### 3.8 Held-out-gene check (handoff 4f)

Dropping 10 of 50 targets with alpha held fixed leaves the retained 40 genes' predictions identical: worst gene-subsetting effect 7.45e-09, max |prediction difference| 6.2e-06 (solver tolerance) over 6 folds on 2 tasks. Confirms the sharp prediction that multi-output ridge fits each target independently.

### 3.9 Across-task transfer, unmatched arm

On the 14 genes shared by all five Xenium assay panels (61 negative-control probes excluded), within-task Pearson exceeds the benchmark's own 50-gene averages by +0.212 across four encoders — immune and proliferation markers are markedly easier to predict from morphology than variance-ranked genes.

The shift estimate itself is **not identified** in the unmatched arm: Spearman(training-size ratio, shift) = -0.822 (p < 0.0001, n = 20), so the gap tracks the across-task arm's data advantage rather than shift. A size-matched arm is running.

## 4. Discrepancies and open questions

| # | item | status |
|---|---|---|
| D1 | Table A13 ridge-no-PCA: ours 0.2843 vs 0.314 (-0.0297) | open; alpha sweep running |
| D2 | Figure 2.a R=0.81 is the raw-parameter correlation; log scale gives 0.942 | paper reporting ambiguity |
| D3 | ccRCC ships 6 folds where Table A11's patient count implies more | benign: folds are patient-disjoint, verified |
| D4 | uni_v1 / IDC differs from the leaderboard by -0.0155 | within tolerance; gated-checkpoint hypothesis |
| D5 | The five Xenium tasks' top-50 gene lists are **completely disjoint**; assay panels share only 14 real genes | structural property of the benchmark |
| D6 | Xenium panels differ **within** tasks too — no task has identical panels across its samples | structural |

### Deviations from the faithful protocol — awaiting sign-off (handoff §8)

| # | deviation | rationale |
|---|---|---|
| V1 | Barcode criterion: handoff requires patch barcodes to match `adata.obs_names` **exactly**; they do not. Revised to **strict subset** | patches are cut only where a full 224x224 window fits (92.4% of spots overall, 57.8% for SKCM); passes 72/72; `benchmark.py` aligns by label, not position |
| V2 | `hoptimus1` absent — 11 of the 12 named encoders | weights gated; `bench_config.yaml` states a request is required. Report-and-wait per §8 |
| V3 | `predictions.parquet` partitioned per task rather than one file | 130M rows; each task file stays laptop-loadable with identical information |
| V4 | CellViT read as parquet rather than zipped GeoJSON | identical content, no geometry parsing |

## 5. What was NOT checked

- **Highly-variable-gene selection leakage.** The 50 genes were ranked using every spot in each task, test folds included. 4f cannot detect this — it needs the ranking recomputed inside each fold. This is a property of the shipped benchmark data, not of the fit.
- **Encoder weight provenance.** Checkpoints are taken as published; no hash comparison against the authors' versions was possible for the gated models.
- **Stage 5 (STFlow).** Optional in the handoff and not started.
- **Assumption diagnostics** for the ridge fits (residual structure, heteroscedasticity) beyond what the count diagnostics cover.

## 6. Proposed next step

1. Land the alpha sweep and close D1 — either confirming the A13 confound or withdrawing it.
2. Finish the four-design split decomposition, which replaces the single 'leakage' number with spatial-autocorrelation, slide-identity and site-shift terms under a fixed within-patient metric.
3. Complete the A14 arm across all encoders on the now-known raw configuration.
4. Join the rebuilt morphology features into 4a and write the Topic A motivation draft.
