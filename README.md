# HEST-1k benchmark replication and instrumentation

Replication of the HEST-1k benchmark (Jaume et al., NeurIPS 2024, arXiv:2406.16192) on UNC
Longleaf, instrumented so its byproducts support downstream work on calibrated uncertainty for
histology-to-expression prediction.

**Contains no gated data** — see [What is not here](#what-is-not-here).

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
over 108 encoder–task cells (12 encoders × 9 paper tasks), with **0 of 108** exceeding the 0.03
acceptance threshold. ResNet50
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
`results/summary/discrepancy_table.csv` flags it with a `config_role` column.

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

Round-1 figures in this section are established in
[`docs/round1_final_stage_report.md`](docs/round1_final_stage_report.md); round-2 figures cite
their own result files inline.

Each is reproducible from the named table; the reasoning lives with the script that produced it.

**1. Split design matters more than encoder choice.** The entire between-encoder spread on the
benchmark's own protocol is **0.0977** Pearson (hoptimus1 0.4229 to resnet50 0.3252, 12 encoders).
Ignoring slide boundaries is worth **0.1575** — 1.61× that spread, positive in 30 of 30 encoder–task
cells — decomposing into spatial adjacency (0.0335) and a slide-level signature (0.1241).
The `blocked − patient` term is reported per task rather than pooled, because in multi-slide tasks
it contains same-patient-other-slide information as well as slide identity. In R3's v4
decomposition COAD's same-patient-other-slide term is **0.2578**, against 0.0910 for READ and
0.0583 for PRAD — the only other two tasks where that term is defined — and its total
`random − patient` gap is **0.3172**, the largest of the ten, where the other nine run 0.0504 to
0.1931 ([`r3_per_task_terms.csv`](r3_per_task_terms.csv)). COAD's figure is a labelling artefact:
its fold 0 holds out three donors at once and trains on one (see benchmark properties). The contrast previously labelled "institution shift, 0.0419" is **not** an
institution contrast and has been withdrawn as a scalar — see limitation 3.

Round 2 remeasured this with a buffered, size-matched design and found the dominant term is
**patient identity, not slide novelty**: once another slide from the same patient is in training, a
novel slide costs only **+0.0148** against **+0.1357** for losing the patient
([`r3_decomposition_terms.csv`](r3_decomposition_terms.csv)).

**And part of what the benchmark scores as losing a patient is losing a replicate.** IDC's TENX95
and TENX99 are two 5 µm sections of one resected tumour mass — 10x's own dataset page reports
`donorCount: 1` — but carry distinct HEST patient labels, so on 2 of IDC's 4 patient folds the
held-out sample's own donor is still in training. Holding the test slide and the training-set size
fixed and varying only whether the same-donor section is available, the replicate is worth
**+0.0651** within-slide Pearson, positive in 6 of 6 encoder–slide cells — **54% of IDC's entire
reported `random − patient` gap of 0.1210**
([`r5_idc_replicate_leak.csv`](r5_idc_replicate_leak.csv),
[`r5_idc_provenance.md`](r5_idc_provenance.md)).

The decomposition itself was run on three encoders
(hoptimus0, uni_v2, virchow), so it does not include hoptimus1; the spread it is compared against is
the current 12-encoder one.
[`results/tailored/splits/`](results/tailored/splits)

**2. Pooled Pearson is not a constant yardstick.** Correlation computed on a pooled test set
carries between-patient variance in its denominator, so the same model scores higher on a more
heterogeneous test set — **exactly 0.0000** inflation when the test set is one patient, **+0.19**
when it spans nine. All split results therefore use **within-slide** Pearson (the correlation is
computed per sample, then averaged over genes and over slides), with the pooled value retained so
the artefact is measured rather than assumed. On the three tasks where a patient contributes more
than one slide — PRAD (23 slides, 2 patients), COAD (4, 2) and READ (4, 2) — within-slide is not
the same as within-patient and does not equal the benchmark's own Table 1 number. On the other
seven tasks, including LYMPH_IDC (4 slides, 4 distinct patients), each patient contributes exactly
one slide and the two metrics coincide.

**3. Table A13's encoder ranking tracks embedding width, not representation quality.**
Spearman(dim, score) = **−0.954** (p = 5.4 × 10⁻⁶) for `raw_ridge`, against **+0.735** for
`pca_ridge`. The 512-dim CONCH v1 wins the raw head. The penalty sweep explains why: at the
benchmark's `alpha = 100/(d × n_genes)` the fit is indistinguishable from unpenalised OLS
(|diff| ≤ 2.7e-4), and at raw width the Gram matrix is numerically singular (condition number
3.0 × 10¹⁵ at 1536 dims). That head is measuring conditioning.
[`results/tailored/regularization/`](results/tailored/regularization)
   These are the **11-encoder** figures, round 1's cohort. R8 added H-optimus-1's raw-head
   cells, and on all **12** the same statistics are **−0.950** and **+0.727**
   ([`r8_width_correlations.csv`](results/round2/R8_raw_heads/r8_width_correlations.csv)), which
   is where the report's figures come from — the two documents quote different cohorts of the
   same statistic, not different results.

**4. Negative binomial is the right observation model; zero-inflation buys nothing.** NB beats
Poisson for **478 of 488** converged genes, and all 500 are overdispersed. ZINB beats NB for only
**14 of 474** — with median ΔAIC **−2.002**, matching AIC's exact penalty for one unused parameter
to three decimals. Sparsity follows the assay, not the tissue (median zero fraction 0.29 for
imaging-based tasks vs 0.61 for sequencing-based).
[`results/tailored/counts/`](results/tailored/counts)

**5. Slides are identifiable from frozen features, and round 2 established that the signature is
technical rather than tissue.** A linear probe
recovers slide identity at **0.980** balanced accuracy under spatial block cross-validation (0.990
under random splitting), with the nearest-training-spot distance verified to widen 2.83×. Round 1
could not say what that separability was made of, because patient, resolution and stain batch all
varied together. Round 2's probes hold the patient fixed and answer it
([`r4_probes_v2.csv`](r4_probes_v2.csv)): within **one** PRAD patient, across 15 slides at a
1.02× pixel-size spread, slide identity is still decodable at **0.871–0.949** against 1/15;
**93–96%** of the confusion mass falls inside a scan session against 46.7% expected; and
regressing out nuclear count, mean nuclear area and the five CellViT class fractions removes only
**1.4%** of it, against 17–27% on tasks whose slides come from different patients. So the
signature is neither tissue composition nor — by the resolution probe above — sampling
resolution: it is the slide and the scan session. This is the clearest evidence in the repository
that pathology encoders carry a technical signature independent of tissue. The IDC
TENX-versus-NCBI probe,
previously described here as a confound-free institution contrast, is neither confound-free nor an
institution contrast (both halves were generated by the same company, and the two halves differ in
scan resolution); at **0.682** balanced accuracy on four slides with **2 of 11** encoders
distinguishable from chance it is **inconclusive**. The technology (0.994) and cohort-source
(0.938) probes are confounded by construction — each task is one technology and most sources occur
in one task only — so they measure tissue, not site.
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

## Properties of HEST-bench found in this replication

Findings about the **public benchmark itself**, as distinct from this replication's own results.
Maintained as they are found; this is the list that goes to David and, where appropriate, to the
HEST-1k authors. Each entry names the file that establishes it.

| # | property | established by |
|---|---|---|
| 1 | **The ridge penalty is inert.** The benchmark's α leaves the fit essentially unregularised, and Table A13's encoder ranking tracks prediction *width* rather than accuracy. | `results/tailored/alpha/`, Table A13 reproduction |
| 2 | **The head has no intercept**, so its predictions have training mean zero per gene while `log1p(y)` does not. Pearson hides this; R², CRPS and interval width do not. Median R² is **−0.95**, rising to **−0.16** with an intercept alone. | [`r1b_ladder_by_task.csv`](r1b_ladder_by_task.csv) |
| 3 | **Per-gene Pearson carries ~1e-3 of solver noise** under the shipped `lsqr` head, up to 3e-3 on four encoders; the head's A2b residual of 0.35 means it is not the ridge solution to any tight tolerance. | [`r1b_solver_sensitivity.csv`](r1b_solver_sensitivity.csv) |
| 4 | **Scan resolution varies 5.02× across the 72 samples** and is aligned with patient identity in PRAD, SKCM and PAAD, so those shipped patient folds are also resolution folds. The mechanism is not resolution, though: within one patient a 0.0066 µm/px scan-session difference is decodable at 0.977 while a 20% resolution difference is at chance (0.489–0.511), so `pixel_size_um` is a proxy for scan session. | [`r4_probes_v2.csv`](r4_probes_v2.csv), sample metadata |
| 5 | **Samples within a task do not share a gene panel.** PAAD's three samples share 159 genes against a 919 union; the shipped 50 are the intersection over *all* samples, held-out ones included, so leakage-free selection is not well defined without the held-out slide's panel. | [`r2_panel_heterogeneity.csv`](r2_panel_heterogeneity.csv) |
| 6 | **COAD's patient labels collapse distinct patients** into one label and leave another sample unlabelled, so COAD's shipped patient split does not separate patients. | [`r3_patient_label_audit.csv`](r3_patient_label_audit.csv) |
| 7 | **IDC's patient labels split one donor into two.** TENX95 and TENX99 are two 5 µm sections of one resected tumour mass (10x reports `donorCount: 1`), but carry distinct patient labels. Measured cost: **+0.065** within-slide Pearson, **54%** of IDC's whole reported patient gap. | [`r5_idc_replicate_leak.csv`](r5_idc_replicate_leak.csv), [`r5_idc_provenance.md`](r5_idc_provenance.md) |
| 8 | **READ's "patients" are same-specimen replicate pairs**, so its patient-identity term is a same-specimen term and an upper bound on a patient effect. | [`r3_per_task_terms.csv`](r3_per_task_terms.csv) |
| 9 | **The IDC gene panels differ between samples.** NCBI785 measures 41 real genes none of the other three measure; NCBI783 adds 8 `antisense_*` probes; only TENX95/TENX99 match. | [`r5_idc_panels_observed.csv`](r5_idc_panels_observed.csv) |
| 10 | **The scan-resolution differences have no documented cause.** No 10x dataset page, GEO record or published Methods reached in this work states an H&E scanner model or nominal magnification for any IDC sample. | [`r5_idc_provenance.md`](r5_idc_provenance.md) §4.3 |
| 11 | **Selection-protocol sensitivity of the target list** — see known limitation 1. | [`r2_leakage_summary.csv`](r2_leakage_summary.csv) |

Entries 4 through 11 concern the benchmark's *design and metadata* rather than its code, and 6, 7
and 9 are the candidates for reporting upstream.

## Known limitations

1. **Selection-protocol sensitivity of the target list.** The 50 target genes per task were
   variance-ranked over *every* spot, test folds included — a property of the shipped benchmark
   data. Recomputing the ranking inside each fold changes the list by roughly half its members and
   changes measured Pearson by +0.009 on average, up to +0.044 on individual tasks
   ([`r2_leakage_summary.csv`](r2_leakage_summary.csv)). This is **not** reported as leakage:
   selection acts *through* which genes are chosen, so gene-set composition is the mechanism rather
   than a confound, and no design comparing two different gene lists can separate the two. On four
   Xenium tasks a training-only selection can name genes the held-out slide does not measure at all.
2. **Per-gene Pearson under the faithful head carries solver noise.** The benchmark's `lsqr` head
   leaves about 1e-3 of run-to-run noise in a per-gene Pearson for most encoders and up to 3e-3 for
   `conch_v1`, `conch_v15`, `ctranspath` and `virchow`, so a per-gene value should not be quoted
   beyond three decimals; task-level means, averaging 50 genes, are unaffected at the precision
   Table 1 reports. Relatedly, the faithful head's A2b residual of **0.35** means its predictions
   are not the ridge solution to any tight tolerance, which is why the Topic A work builds on
   `intercept_f64` rather than on the shipped head
   ([`r1b_solver_sensitivity.csv`](r1b_solver_sensitivity.csv)).
3. **The R² ladder's scale rung is an upper bound, not an achievable gain.** It uses the test
   fold's own optimal ρ, so the +0.070 it reports is the most any level-and-scale recalibration
   could recover; what a calibration fitted on training or calibration data actually delivers is
   necessarily less ([`r1b_ladder_by_task.csv`](r1b_ladder_by_task.csv)).
4. **Across-task shift is not a scalar.** Even with training volume matched it varies monotonically
   with in-domain sample size, so any single number describes the reference task chosen.
5. **There is no clean institution contrast in HEST-bench, and the IDC one has been withdrawn.**
   The contrast used in round 1 — TENX95/TENX99 against NCBI783/NCBI785 within IDC — was labelled
   "differing only in source institution." Both halves were in fact generated by 10x Genomics (the
   NCBI pair is the GEO deposit of Janesick et al. 2023, whose authors are 10x staff), and they
   also differ in scan resolution (0.2125 µm/px against 0.274 and 0.364). The four per-slide gaps
   are asymmetric in the direction a resolution explanation predicts, not the symmetric pattern an
   institution effect would give (gaps from
   [`docs/round1_final_stage_report.md`](docs/round1_final_stage_report.md); pixel sizes from
   [`sample_metadata.csv`](results/tailored/integrity/sample_metadata.csv)):

   | held-out slide | µm/px | gap (source seen − unseen) |
   |---|---|---|
   | NCBI783 | 0.274 | 0.002 |
   | NCBI785 | 0.364 | 0.014 |
   | TENX95 | 0.2125 | 0.052 |
   | TENX99 | 0.2125 | 0.099 |

   The mean of these four, 0.0419, is therefore **not** reported as a site-shift effect. The
   correct description of the contrast is "novel slide, same generating lab, different scan
   resolution." An institution axis needs full HEST-1k, not the benchmark subset.
6. **Head coverage is uneven across encoders.** `pca_ridge` has all 12. `raw_ridge` now has
   all 12 as well — R8 added H-optimus-1's ten task cells
   ([`r8_hoptimus1_raw_ridge_by_task.csv`](results/round2/R8_raw_heads/r8_hoptimus1_raw_ridge_by_task.csv)).
   `raw_xgb` has 11, missing H-optimus-1 by the decision in item 8. `pca_xgb` has 1
   (`resnet50`), by design.
7. **Stage 5 training has not run** — CUDA-only against a saturated GPU queue.

8. **`raw_xgb` for H-optimus-1 was deliberately not run.** All ten of its `raw_xgb` task cells are
   missing, and this is a decision rather than an omission. The falsification test it would have
   contributed to is settled by `raw_ridge` alone, where H-optimus-1 is best of twelve on
   `pca_ridge` (0.3891) and 7th of twelve on `raw_ridge` (0.2590), with Spearman −0.95 between
   embedding width and raw-head score reversing to +0.73 once PCA equalises width at 256
   ([`r8_raw_head_leaderboard.csv`](r8_raw_head_leaderboard.csv)). The cost of confirming the same
   conclusion on a second head was measured before stopping: **70 minutes per split, so about 34
   CPU-hours for the 29 splits**, against an 8-hour wall. A future session wanting it should
   fan out ten per-task jobs rather than submit one long one — this queue schedules short,
   small-memory jobs far sooner, which is the same lesson as limitation 9.

9. **Resource asks were oversized for most of round 2, and that cost queue time.** `sacct` over the
   round shows the heaviest job peaked at **8.8 GB on 4 CPUs**; asks of 64 GB and 8 CPUs sat at
   `(Priority)` for 5.5 hours while every right-sized job ran. Size from the accounting record,
   not from intuition.

10. **The IDC same-donor attribution is unresolved, and the round-2 close did not resolve it.**
    The `donorCount: 1` and "Replicate 1 / Replicate 2" language that motivated reading TENX95 and
    TENX99 as one donor belongs to the "FFPE Human Breast using the Entire Sample Area" page,
    which HEST's `download_page_link1` associates with **TENX99 only**; TENX95 is attributed to a
    different product, "FFPE Human Breast with Pre-designed Panel". Three attempts to read that
    second page returned HTTP 429, and no other route was tried. The evidence is genuinely mixed:
    the two carry byte-identical 541-entry panels, the only such pair in IDC, and 123 of 128
    (96.1%) of the TENX slides' classification errors land on the partner against 33.3% expected
    ([`r5d_idc_partner_confusion.csv`](results/round2/R5c_leak/r5d_idc_partner_confusion.csv));
    but their spot counts differ 2.1-fold (25,080 against 11,845), which two replicate sections of
    one imaged area should not show, and Janesick et al. is the source for neither, since its
    Xenium runs used the 280-gene breast panel plus 33 add-on genes while both samples carry
    exactly 280 real genes
    ([`r5_idc_panels_observed.csv`](results/round2/R5b_audit/r5_idc_panels_observed.csv)).

    **The measurement does not depend on the label.** The +0.0652 replicate leak
    ([`r5c_leak_summary.csv`](results/round2/R5c_leak/r5c_leak_summary.csv)) is what having TENX95
    in training is worth for predicting TENX99, whatever the relationship between them is called.
    What is unresolved is the *explanation* — one donor, or two donors sharing a lab, panel and
    scanner. The draft issue to the HEST authors carries a blocking note on this item and has not
    been sent.

### Scan resolution

The estimated pixel size of the source image varies **5.02-fold across the 72 benchmark samples**
(0.137 to 0.688 µm/px) and, in three tasks, varies *within* the task in a way that is aligned with
patient identity. Computed from
[`results/tailored/integrity/sample_metadata.csv`](results/tailored/integrity/sample_metadata.csv)
(`pixel_size_um`, `resolution_group`) and
[`results/tailored/morphology/patch_scale_sources.csv`](results/tailored/morphology/patch_scale_sources.csv).

| task | samples | patients | distinct µm/px (count) | within-task spread | consequence |
|---|---|---|---|---|---|
| PRAD | 23 | 2 | 0.172 (1), 0.341–0.349 (15), 0.573–0.574 (5), 0.688 (2) | 4.00× | no resolution group contains both patients, so resolution predicts patient perfectly |
| PAAD | 3 | 3 | 0.137 (1), 0.274 (2) | 2.00× | one of three patients differs two-fold |
| SKCM | 2 | 2 | 0.137 (1), 0.274 (1) | 2.00× | the two patients differ two-fold; resolution predicts patient |
| IDC | 4 | 4 | 0.2125 (2), 0.274 (1), 0.364 (1) | 1.71× | cohort source is aligned with resolution (TENX 0.2125; NCBI 0.274 and 0.364) |
| COAD | 4 | 2 | 0.250 (1), 0.274 (3) | 1.10× | small, and hidden inside a single resolution bin |
| CCRCC, HCC, LUNG, LYMPH_IDC, READ | 24, 2, 2, 4, 4 | — | uniform within task | ≤ 1.01× | no confound |

Three consequences, none of which round 1 accounted for:

- **In PRAD, SKCM and PAAD the shipped patient folds are also resolution folds.** Part of what
  Table 1 calls generalisation to a new patient in those tasks is generalisation to a new scan
  resolution. This is a property of the public benchmark, not of this replication.
- **Every slide-identity and cohort-source probe is partly a resolution probe**, and every
  slide-signature term includes it. Seven PRAD slides come from source regions of about 195 px
  upsampled to 224, and one from a 652 px region downsampled; interpolation leaves a per-slide
  signature in sharpness and texture statistics that an encoder will represent and a linear probe
  will read.
- **Resolution is a per-slide technical covariate that is neither biology nor institution.** It is
  joined to every prediction row (`pixel_size_um`, `resolution_group`) and is used as a covariate
  or stratification variable in every probe and shift analysis from round 2 onward.

**What the encoders actually read is the scan session, not the pixel size.** Round 2's probes
separated the two by holding the patient fixed
([`r4_probes_v2.csv`](r4_probes_v2.csv)):

- Within PRAD **patient 2** — 15 slides, one patient, pixel size spanning only 1.02× — slide
  identity is decodable at **0.871–0.949** against a chance of 1/15, and the two scan sessions
  (MEND139–146 at 0.3413–0.3418 µm/px, MEND147–153 at 0.3484–0.3492, **0.0066 µm/px apart**) are
  separable at **0.977**, with all 15 slides assigned to the right session by majority vote.
- Within PRAD **patient 1**, whose slides differ in nominal resolution by **20%** (0.573 against
  0.688), resolution class is **not decodable at all**: pooled balanced accuracy 0.489–0.511
  against a chance of 0.5, with the majority vote 5/7 for every encoder — exactly the
  constant-prediction outcome.

A 0.0066 µm/px session difference is separable; a 20% resolution difference is not. So
**`pixel_size_um` is best read as a proxy for scan session** rather than as the property the
encoder responds to. The alignment of resolution with patient identity in PRAD, SKCM and PAAD
remains a fact about the benchmark's design and still confounds those folds; what changes is the
mechanism, which is session and slide rather than sampling resolution.
