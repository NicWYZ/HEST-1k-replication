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
| 5 · STFlow stronger baseline | setup complete; training not yet run (CUDA-only, GPU queue) |
| round 2 · replication extensions (splits, probes, θ₁, variance) | complete |
| round 2 closeout (freeze, numeric-claim sweep, IDC-attribution note) | complete |

Repository tagged [`round2-final`](../../releases/tag/round2-final) at the closeout commit; `HEAD`
is five commits past the tag (the closeout report and IDC fetch log, a documentation cleanup, the
seven-figure deck under committed scripts, and two AppleDouble-sidecar removals) — no results
changed in those five commits.

## Headline result

Against the live leaderboard snapshot, the `pca_ridge` head agrees to **mean |diff| 0.0002**
over 108 encoder–task cells (12 encoders × 9 paper tasks), with **0 of 108** exceeding the 0.03
acceptance threshold ([`results/summary/discrepancy_table.csv`](results/summary/discrepancy_table.csv)).
ResNet50 reproduces Table 1 **exactly** (0.3252) — the informative case, since it has no gated
weights, no version ambiguity and no transform drift.

Average Pearson over the nine paper tasks (HCC excluded, the paper's convention;
[`results/summary/results_encoder.csv`](results/summary/results_encoder.csv); encoder dimension from
[`r8_raw_head_leaderboard.csv`](results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv), column `width`):

| encoder | dim | `pca_ridge` | `raw_ridge` | `raw_xgb` |
|---|---|---|---|---|
| hoptimus1 | 1536 | **0.4229** | 0.2859 | — |
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

`pca_xgb` (Table A14's rejected candidate, resnet50 only): 0.3046. hoptimus1's `raw_ridge` cell is
now folded in from `results/summary/results_encoder.csv`, which carries it as `avg_paper9` on nine
tasks, the convention this table uses. Its `raw_xgb` cell stays empty because that head was never
run for this encoder ([known limitation 8](#known-limitations)). Full tables in
[`results/summary/`](results/summary).

## Repository layout

```
results/
  faithful/<head>/<encoder>/<task>/   the paper's four configurations
  tailored/<question>/                our own diagnostics, grouped by question
  summary/                            aggregated official tables, incl. deck_numbers.csv
  round2/<STAGE>/                     round-2 extensions, one directory per stage,
                                       each with a PROVENANCE.txt
code/
  scripts/                            one script per experiment, all rerunnable
  configs/<head>__<encoder>.yaml      one config per faithful run
  figures/                            one script per deck figure, plus make_all.py
  stage5_provenance/                  upstream commit + integration findings for STFlow
bench_data/                           benchmark inventory and provenance (no gated data)
env/                                  pinned environment and rebuild recipe
figures/                              fig_<topic>.png (round 1), deck/ (round 2, see below)
figures/deck/                         seven round-2 deck figures, 300 dpi PNG + PDF, and a
                                       generated README listing each figure's sources
docs/                                 narrative stage reports and the closeout report
docs/decisions/                       round-2 decision memos — not yet added to the
                                       repository; pending from the project lead
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

Reordered to the synthesis ranking (patient split and replicate leak; split design vs encoder;
session signature; intercept and ladder; A13 width; panels and selection; NB; θ₁ and variance
components). Round-1 figures are established in
[`docs/round1_final_stage_report.md`](docs/round1_final_stage_report.md); round-2 figures cite
their own result files inline, each checked against its file with
`code/scripts/verify_numeric_claims.py`.

**1. Patient identity, not slide novelty, drives the split penalty — and part of what the
benchmark scores as losing a patient is losing a replicate.** Holding training-set size and test
spots fixed and varying only whether another slide from the same patient is in training, a novel
slide costs **+0.0148** against **+0.1357** for losing the patient altogether, averaged over the
three multi-slide tasks
([`r3_decomposition_terms.csv`](results/round2/R3_splits/r3_decomposition_terms.csv)). IDC's
TENX95 and TENX99 are two sections that HEST-bench's own `donorCount: 1` field and 10x's
"Replicate 1 / Replicate 2" language describe as one specimen, but they carry distinct patient
labels; holding
the test slide and training-set size fixed and varying only whether the same-donor section is
available, the replicate is worth **+0.0652** within-slide Pearson, positive in all 6
encoder–slide cells — **54%** of IDC's reported random-minus-patient gap of 0.1210
([`r5c_leak_summary.csv`](results/round2/R5c_leak/r5c_leak_summary.csv)). READ's two replicate
pairs are worth **+0.0901**, positive in all 12 cells, but READ's shipped folds hold each pair out
together, so the leak there is a counterfactual, not a property of the published benchmark
(`leak_realised_in_shipped_split` is `False` for READ, `True` for IDC, same file). The **+0.0652**
measurement does not depend on how the IDC pair is attributed — see [property 1](#properties-of-hest-bench-found-in-this-replication)
and [known limitation 2](#known-limitations).

**2. Split design costs more than encoder choice.** Over ten tasks, the benchmark's own
random-minus-patient gap averages **0.1586** Pearson
([`r3_decomposition_terms.csv`](results/round2/R3_splits/r3_decomposition_terms.csv), row `TOTAL
random - patient`) against a between-encoder spread of **0.0977** on the same protocol (H-Optimus-1
0.4229 to ResNet50 0.3252,
[`results_encoder.csv`](results/summary/results_encoder.csv)) — 1.6× the spread. Decomposing the
gap: training-set size **0.0126**, spatial adjacency **0.0327**, a residual adjacency term removed
only by a spatial buffer **0.0115**, and a slide-and-patient identity term of **0.1018** that
absorbs the rest
([`r3_decomposition_terms.csv`](results/round2/R3_splits/r3_decomposition_terms.csv)). COAD is the
outlier at 0.3172 (finding 1's decomposition attributes most of it to the mislabelled patients in
[property 3](#properties-of-hest-bench-found-in-this-replication)), against 0.0504–0.1931 for the
other nine tasks ([`r3_per_task_terms.csv`](results/round2/R3_splits/r3_per_task_terms.csv)).

**3. Slides are identifiable from frozen features, and the signature is the scan session, not
tissue or resolution.** Holding one PRAD patient fixed (patient 2, 15 slides, pixel size spanning
only 1.02×), a linear probe recovers slide identity at **0.871–0.949** against a chance of 1/15,
with a confusion-mass share landing inside the correct scan session of **0.9326–0.9639**
against a chance share of **0.4667**
([`r4_probes_v2.csv`](results/round2/R4_probes/r4_probes_v2.csv), `probe1_slide_within_patient`).
The two scan sessions themselves (0.0066 µm/px apart) are separable at **0.967–0.991**, while a
20% *resolution* difference within a different PRAD patient is not decodable at all (pooled
balanced accuracy **0.489–0.511** against chance 0.5, majority-class baseline **0.714**; same
file, `probe1b_scan_subcluster` and `probe2_2class`). Regressing out nuclear count, mean nuclear
area and the five CellViT class fractions removes only **1.4%** of the signature within that one
patient, against **17–27%** on tasks whose slides come from different patients — except IDC at
**3.0%**, the smallest cross-patient value in the table (same file, `probe3_composition_adjusted`).
At the gene level, 28 of the 50 PRAD target genes show a between-session variance component at or
below zero
([`r6_prad_session_variance.csv`](results/round2/R6_variance/r6_prad_session_variance.csv)) — the
probe-level separability is real but does not translate one-to-one into every gene's variance
decomposition. This result rests on **one PRAD patient**; see
[known limitation 6](#known-limitations).

**4. The benchmark head has no intercept, and most of its apparent skill is scale, not level.**
Pooled fold-median R² for the head as shipped is **−0.953**; adding a training-mean intercept
alone brings it to **−0.155**; giving the test fold its own mean (an oracle upper bound) reaches
**+0.030**; adding the test fold's own optimal scale on top reaches **+0.100**, the per-cell R²
ceiling
([`r1b_ladder_pooled.csv`](results/round2/R1b_heads/r1b_ladder_pooled.csv)). The last step alone
is worth **+0.070** ([same file], column `gain_3`) — the model's predictions are correlated with
truth (that is what Pearson credits) but at the wrong scale, with a pooled prediction-to-target
ratio of **1.840** (ResNet50 worst at 2.165, UNI2-h best at 1.650,
[`r1b_ladder_by_encoder.csv`](results/round2/R1b_heads/r1b_ladder_by_encoder.csv)).

**5. Table A13's raw-embedding ranking tracks embedding width, not representation quality.**
Spearman(width, score) is **−0.950** on the raw head against **+0.727** on the PCA-256 head, over
the current 12-encoder cohort
([`r8_width_correlations.csv`](results/round2/R8_raw_heads/r8_width_correlations.csv)).
H-Optimus-1 ranks **1st of 12** on the PCA head and **7th of 12** on the raw head
([`r8_raw_head_leaderboard.csv`](results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv)); the
512-dimensional CONCH v1 wins the raw head outright. (Round 1's 11-encoder cohort, before
H-Optimus-1 had raw-head cells, gives −0.954 / +0.735 on the same statistic — both figures are
correct, they are different cohorts; same file, `n_encoders` column.)

**6. Gene panels and gene selection are both sources of leakage-shaped variation the benchmark
does not control.** Samples within one task do not always share a gene panel: PAAD's three
samples intersect on only **159** genes against a **919**-gene union, so its shipped 50-gene
target list is not well defined without the held-out slide's own panel
([`r2_panel_heterogeneity.csv`](results/round2/R2_fold_hvg/r2_panel_heterogeneity.csv)). Separately,
the 50 target genes are variance-ranked over every spot, test folds included; recomputing the
ranking inside each fold changes the list by roughly half its members (mean **25.2** of 50 genes
shared, as few as **11** on PRAD) and changes measured Pearson by a mean of **+0.0048**, up to
**+0.0441** on the most affected task
([`r2_leakage_summary.csv`](results/round2/R2_fold_hvg/r2_leakage_summary.csv)). This is not
reported as leakage in the usual sense — selection acts *through* which genes are chosen, so
gene-set composition is the mechanism rather than a confound removable by re-running the same
design (see [known limitation 1](#known-limitations)).

**7. Negative binomial is the right observation model; zero-inflation buys almost nothing.** NB
beats Poisson for **478 of 488** converged gene–task pairs, and all 500 gene–task pairs are
overdispersed (smallest Fano factor **1.638**,
[`count_diagnostics.csv`](results/tailored/counts/count_diagnostics.csv)). ZINB beats NB for only
**28 of 488** — with median ΔAIC **−2.002**, matching AIC's exact penalty for one unused parameter
to three decimals (same file). Sparsity follows the assay, not the tissue: the median zero
fraction across the five Xenium (imaging-panel) tasks (COAD, IDC, LUNG, PAAD, SKCM) is **0.29**,
against **0.61** across the five Visium (sequencing-panel) tasks (CCRCC, HCC, LYMPH_IDC, PRAD,
READ) — assay from the `st_technology` column of
[`sample_metadata.csv`](results/tailored/integrity/sample_metadata.csv), zero fractions from
[`count_diagnostics.csv`](results/tailored/counts/count_diagnostics.csv).

**8. θ₁ is sensitive to the morphology build, and the pooled between-donor variance share depends
on which tasks are pooled.** IDC's slide-level estimand θ₁ (a GATA3 read on NCBI785) moved from
0.4578 under round 1's morphology build to **0.4106** (log1p) / **0.4209** (raw) under the current
one, tolerance 1e-3 either way — the same computation, a different input
([`r6_theta_acceptance.csv`](results/round2/R6_theta/r6_theta_acceptance.csv)); its spot bootstrap
(200 resamples) gives a 95% interval of **[0.377, 0.472]**
([`r6_theta_bootstrap_ci.csv`](results/round2/R6_theta/r6_theta_bootstrap_ci.csv)). The
method-of-moments variance-component estimator recovers simulated donor/slide/spot shares to
within 1–2% (true 0.5/0.2/1.0, recovered 0.494/0.202/0.998 over 40 simulations,
[`r6_estimator_validation.csv`](results/round2/R6_variance/r6_estimator_validation.csv)), but the
donor share itself ranges **0.061–0.393** across tasks
([`r6_variance_by_task.csv`](results/round2/R6_variance/r6_variance_by_task.csv)) and pooling it
is not a single number: the directive's own CCRCC+PRAD pairing gives **0.122**, but PRAD's donor
degrees of freedom is 1 and its raw component is negative for 68% of genes, so that pools one
well-determined value with a truncated zero; restricting to the two tasks with ≥3 donor degrees of
freedom and verified labels (CCRCC+LYMPH_IDC) gives **0.376**; pooling all ten tasks gives
**0.085** ([`r6_pooled_between_donor.csv`](results/round2/R6_variance/r6_pooled_between_donor.csv)).
See [known limitations 4–5](#known-limitations).

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

### Round 2, from cached embeddings

Each script reads `bench_data/` inventory and cached embeddings/results from steps 1–3 above and
writes to its own `results/round2/<STAGE>/` directory (see that directory's `PROVENANCE.txt`); run
in this order:

```bash
python code/scripts/round2_r0_resolution_columns.py     # R0_resolution
python code/scripts/round2_r1b_heads.py                 # R1b_heads: 12-encoder intercept refit
python code/scripts/round2_r1b_ladder.py                 #   the four-rung R2 ladder
python code/scripts/build_r1b_ladder_by_encoder.py        #   per-encoder ladder summary
python code/scripts/round2_r2_gene_check.py              # R2_fold_hvg: reproduction check
python code/scripts/round2_r2_fold_hvg.py                 #   per-fold training-only selection
python code/scripts/round2_r2_rank_supplement.py          #   ranking-only supplement
python code/scripts/round2_split_v4.py                    # R3_splits: five split designs
# R5b_audit's donor_audit.csv and its companions were produced by a script that is not
# present under code/scripts/ in this checkout (see Reproducing note below); its outputs are
# committed, but it cannot currently be rerun from this repository.
python code/scripts/round2_r4_probes.py                  # R4_probes
python code/scripts/round2_r5c_replicate_leak.py          # R5c_leak: generalised replicate leak
python code/scripts/round2_r5d_confusion.py                #   IDC partner-confusion detail
python code/scripts/round2_r6_theta.py                    # R6_theta: theta1 and its acceptance
python code/scripts/build_r6_theta_bootstrap.py            #   spot bootstrap CI
python code/scripts/round2_r6_donor_variance.py           # R6_variance: nested variance components
python code/scripts/round2_r7_pergene.py                  # R7_pergene: per-gene decomposition
python code/scripts/build_summary_tables.py               # results/summary/ tables
python code/scripts/build_deck_numbers.py                 # results/summary/deck_numbers.csv
python code/figures/make_all.py                           # figures/deck/fig01-fig07, PNG+PDF
```

**Note on `R5b_audit`:** the R5b donor provenance audit was a *reading* task — vendor dataset
pages, GEO subseries strings and an upstream issue thread — so no script can redo it, and for a
while none existed to regenerate its output either, which the closeout report recorded as a
reproducibility gap. That gap is now closed, though not by making the reading reproducible.
`donor_audit.csv` is a **derived** file, rebuilt by
[`code/scripts/round2_r5b_audit.py`](code/scripts/round2_r5b_audit.py) from the two inputs that
together determine it:

| input | what it is | reproducible? |
|---|---|---|
| [`hest_source_map.csv`](results/round2/R5b_audit/hest_source_map.csv) | per-sample task, patient label, subseries string, dataset title and source page, extracted from HEST's own `HEST_v1_1_0.csv` | yes, from HEST |
| [`donor_verdicts.csv`](results/round2/R5b_audit/donor_verdicts.csv) | the audit's human output — `donor_id`, `donor_label_status`, and the source citation and statement per sample | **no** — this is the reading, and it is committed because it cannot be recomputed |

The script asserts it reproduces the committed `donor_audit.csv` **byte for byte**, and it
*derives* rather than copies the one field that follows a rule: COAD's `donor_id` comes from each
slide's own subseries string (`"Xenium In Situ, Sample P5 CRC"` → `COAD_Oliveira_P5`; a COAD slide
whose subseries carries no such identifier is its own donor). The rule is applied and then checked
against the recorded verdict, so if the two ever disagree the script fails rather than silently
preferring one — verified by perturbing a verdict and confirming it refuses.

This matters beyond tidiness: `donor_id` is the grouping variable R6 and R7 use, and a grouping
variable with no regeneration path is one nobody can check. Nine of the 72 labels remain
`unverifiable` and five `contradicted`; those are audit findings, not gaps in the regeneration.

`code/figures/make_all.py` renders all seven deck figures at 300 dpi (PNG and PDF) and fails if
any figure reports a text overlap; see [`figures/deck/README.md`](figures/deck/README.md) for the
per-figure source and number list, generated from `results/summary/deck_numbers.csv` by
`code/figures/make_readme.py`.

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
| 1 | **IDC's TENX95/TENX99 pair is probably one donor, and the question is unresolved.** HEST-bench's `donorCount: 1` and "Replicate 1 / Replicate 2" language belong to the page HEST's `download_page_link1` associates with TENX99 only; TENX95 is attributed to a different product page, three fetches of which returned HTTP 429. The two carry byte-identical 541-entry gene panels — the only such pair in IDC — and 123 of 128 (96.1%) of the TENX slides' classification errors land on the partner against 33.3% expected; but their spot counts differ 2.1-fold (25,080 vs 11,845), which two sections of one imaged area should not show, and Janesick et al. 2023 is the source for neither, since its Xenium runs used the 280-gene breast panel plus 33 add-on genes while both samples carry exactly 280 real genes. The **+0.0652** replicate-leak measurement does not depend on which reading is right. | [`donor_audit.csv`](results/round2/R5b_audit/donor_audit.csv), [`r5d_idc_partner_confusion.csv`](results/round2/R5c_leak/r5d_idc_partner_confusion.csv), [`r5_idc_panels_observed.csv`](results/round2/R5b_audit/r5_idc_panels_observed.csv), [`sample_metadata.csv`](results/tailored/integrity/sample_metadata.csv) |
| 2 | **COAD's patient labels collapse three distinct patients into one.** TENX147/148/149 are Patient 1/2/5 in the source subseries but share one HEST patient label; TENX111 has no patient label at all. Confirmed upstream at HEST issue #133: a collaborator states it was wrong in v1.1.0 and fixed in v1.3.0, and that this benchmark's splits were deliberately not updated. | [`r3_patient_label_audit.csv`](results/round2/R3_splits/r3_patient_label_audit.csv), [`r5b_issue133_evidence.md`](results/round2/R5b_audit/r5b_issue133_evidence.md) |
| 3 | **READ's "patients" are same-specimen replicate pairs, not distinct donors.** ZEN36/ZEN40 share specimen A938797 and ZEN48/ZEN49 share specimen A121573 — same block, not merely same patient — so READ's patient-identity term is a same-specimen term and an upper bound on any patient effect. | [`r3_patient_label_audit.csv`](results/round2/R3_splits/r3_patient_label_audit.csv) |
| 4 | **Samples within a task do not share a gene panel.** PAAD's three samples intersect on 159 genes against a 919-gene union; the shipped 50 targets are the intersection over *all* samples, held-out ones included, so leakage-free selection is not well defined without the held-out slide's panel. IDC's own panels differ too: NCBI785 measures 41 real genes none of the other three measure, and NCBI783 adds 8 `antisense_*` probes. | [`r2_panel_heterogeneity.csv`](results/round2/R2_fold_hvg/r2_panel_heterogeneity.csv), [`r5_idc_panels_observed.csv`](results/round2/R5b_audit/r5_idc_panels_observed.csv) |
| 5 | **Selection-protocol sensitivity of the target list.** The 50 target genes were variance-ranked over every spot, test folds included; recomputing inside each fold changes the list by roughly half its members and measured Pearson by a mean of +0.0048, up to +0.0441 on the most affected task. | [`r2_leakage_summary.csv`](results/round2/R2_fold_hvg/r2_leakage_summary.csv) |
| 6 | **Scan resolution is aligned with patient identity in PRAD, SKCM and PAAD**, so those shipped patient folds are also resolution folds — but the mechanism is scan *session*, not sampling resolution: within one PRAD patient a 0.0066 µm/px session difference is decodable at up to 0.991, while a 20% resolution difference in a different patient is at chance (0.489–0.511 against 0.5). | [`resolution_by_task.csv`](results/round2/R0_resolution/resolution_by_task.csv), [`r4_probes_v2.csv`](results/round2/R4_probes/r4_probes_v2.csv) |
| 7 | **The ridge penalty is inert, and Table A13's raw-head ranking tracks embedding width.** At the benchmark's α = 100/(d·n_genes) (0.0078 at d=256) the Gram matrix at raw width is ill-conditioned (condition number ≈3.0×10¹⁵ at 1536 dimensions, against ≈544 after PCA-256), and Spearman(width, raw-head score) is −0.950 against +0.727 on the PCA head. | [`alpha_sweep.csv`](results/tailored/regularization/alpha_sweep.csv), [`r8_width_correlations.csv`](results/round2/R8_raw_heads/r8_width_correlations.csv) |
| 8 | **The benchmark head has no intercept.** Its predictions have training-mean zero per gene while `log1p(y)` does not; Pearson hides this, R² does not. Pooled fold-median R² is −0.953 as shipped, −0.155 with an intercept alone. | [`r1b_ladder_pooled.csv`](results/round2/R1b_heads/r1b_ladder_pooled.csv) |
| 9 | **Per-gene Pearson under the shipped `lsqr` solver carries measurable solver noise.** Median per-gene noise across encoder–task cells is 0.0005, rising to 0.0276 for the single noisiest gene (PAAD); the shipped head's A2b residual reaches 0.352 (CONCH v1.5), meaning it is not the ridge solution to any tight tolerance, which is why round 2's Topic-A work builds on the float64 `cholesky` head instead. | [`r1b_solver_sensitivity.csv`](results/round2/R1b_heads/r1b_solver_sensitivity.csv), [`acceptance__conch_v15.csv`](results/round2/R1b_heads/acceptance__conch_v15.csv) |
| 10 | **Nine of the 72 samples' donor labels cannot be verified against any source outside HEST, and five are contradicted by one.** A systematic audit against 10x/GEO/journal sources classified 58 of 72 sample-level donor labels as verified, 9 as unverifiable, and 5 as contradicted. | [`donor_audit.csv`](results/round2/R5b_audit/donor_audit.csv) |

Properties 2, 3 and 10 are the strongest candidates for reporting upstream; property 1 is not
reported upstream while the attribution stays unresolved (see [known limitation 3](#known-limitations)).

## Known limitations

1. **Selection-protocol sensitivity of the target list.** The 50 target genes per task were
   variance-ranked over *every* spot, test folds included — a property of the shipped benchmark
   data. Recomputing the ranking inside each fold changes the list by roughly half its members
   (mean 25.2 of 50 genes shared) and changes measured Pearson by a mean of **+0.0048**, up to
   **+0.0441** on individual tasks
   ([`r2_leakage_summary.csv`](results/round2/R2_fold_hvg/r2_leakage_summary.csv)). This is
   **not** reported as leakage: selection acts *through* which genes are chosen, so gene-set
   composition is the mechanism rather than a confound, and no design comparing two different
   gene lists can separate the two. On four Xenium tasks a training-only selection can name genes
   the held-out slide does not measure at all.
2. **Per-gene Pearson under the faithful head carries solver noise.** The benchmark's `lsqr` head
   leaves a median of about 0.0005 per-gene noise, rising to 0.0276 for the single noisiest gene
   ([`r1b_solver_sensitivity.csv`](results/round2/R1b_heads/r1b_solver_sensitivity.csv)).
   Relatedly, the faithful head's A2b residual reaches **0.352** (CONCH v1.5,
   [`acceptance__conch_v15.csv`](results/round2/R1b_heads/acceptance__conch_v15.csv)), meaning its
   predictions are not the ridge solution to any tight tolerance, which is why the Topic A work
   builds on the float64 `cholesky` head rather than on the shipped one.
3. **The IDC same-donor attribution is unresolved.** The evidence is genuinely mixed — identical
   541-entry panels and 96.1% of TENX misclassifications landing on the partner slide, against a
   2.1-fold spot-count difference and Janesick et al. 2023 being the source for neither sample —
   and the page that would settle it returned HTTP 429 on all three fetch attempts, spaced
   unevenly (175 minutes, then 12 minutes) rather than the intended even spacing, so this is weaker
   evidence of a persistent block than three properly spaced failures would be. The **+0.0652**
   replicate-leak measurement does not depend on the label; the authors' draft issue carries a
   blocking note on this item and has not been sent
   ([`donor_audit.csv`](results/round2/R5b_audit/donor_audit.csv),
   [`round2_closeout_report.md`](docs/round2_closeout_report.md)).
4. **Nine of the 72 samples' donor labels cannot be verified against any source outside HEST, and
   five are contradicted by one.** A systematic audit against 10x/GEO/journal sources classified
   58 of 72 sample-level donor labels as verified, 9 as unverifiable, and 5 as contradicted
   ([`donor_audit.csv`](results/round2/R5b_audit/donor_audit.csv)). The variance-component and θ₁
   work in finding 8 is built on these labels; the 9 unverifiable and 5 contradicted samples are a
   standing source of uncertainty in any donor-level quantity.
5. **The variance-component shares have no bootstrap or other interval.** θ₁ has a 200-resample
   spot bootstrap ([`r6_theta_bootstrap_ci.csv`](results/round2/R6_theta/r6_theta_bootstrap_ci.csv)),
   but the per-task donor/slide/spot variance shares
   ([`r6_variance_by_task.csv`](results/round2/R6_variance/r6_variance_by_task.csv)) and the three
   pooled between-donor definitions
   ([`r6_pooled_between_donor.csv`](results/round2/R6_variance/r6_pooled_between_donor.csv)) are
   point estimates only; the method-of-moments estimator is validated against simulation
   ([`r6_estimator_validation.csv`](results/round2/R6_variance/r6_estimator_validation.csv)), not
   against a resampled interval on the real data. Nor does the decomposition carry any nested-ANOVA
   diagnostics (F-tests, residual checks, a normality assumption on the random effects) — the
   variance shares are method-of-moments point estimates and nothing in the pipeline tests whether
   the nested model itself fits.
6. **The session-signature result rests on one patient.** Finding 3's session/resolution
   separation ([`r4_probes_v2.csv`](results/round2/R4_probes/r4_probes_v2.csv),
   [`r6_prad_session_variance.csv`](results/round2/R6_variance/r6_prad_session_variance.csv)) holds
   the patient fixed within PRAD patient 2, the only task and patient with two scan sessions and
   enough slides to test it; it has not been replicated in a second patient or a second task.
7. **Across-task shift is not a scalar.** Even with training volume matched it varies monotonically
   with in-domain sample size, so any single number describes the reference task chosen.
8. **Head coverage is uneven across encoders and across summary files.** `pca_ridge` has all 12 in
   [`results_encoder.csv`](results/summary/results_encoder.csv). `raw_ridge` has 11 there;
   H-Optimus-1's ten `raw_ridge` task cells were measured separately in round 2
   ([`r8_hoptimus1_raw_ridge_by_task.csv`](results/round2/R8_raw_heads/r8_hoptimus1_raw_ridge_by_task.csv),
   0.2590 average over all ten tasks) but have not been folded into
   `results_encoder.csv`, so the headline table above still shows H-Optimus-1's `raw_ridge` cell as
   "—". `raw_xgb` has 11, missing H-Optimus-1 by the decision in item 9. `pca_xgb` has 1
   (`resnet50`), by design.
9. **`raw_xgb` for H-Optimus-1 was deliberately not run.** All ten of its `raw_xgb` task cells are
   missing, and this is a decision rather than an omission: the falsification test it would have
   contributed to is settled by `raw_ridge` alone, where H-Optimus-1 is best of twelve on
   `pca_ridge` and 7th of twelve on `raw_ridge`, with Spearman −0.950 between embedding width and
   raw-head score reversing to +0.727 once PCA equalises width at 256
   ([`r8_raw_head_leaderboard.csv`](results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv)). The
   cost of confirming the same conclusion on a second head was measured before stopping: **70
   minutes per split**, so about **34 CPU-hours** for the 29 splits, against an 8-hour wall. A
   future session wanting it should fan out ten per-task jobs rather than submit one long one —
   the same right-sizing lesson as item 10.
10. **Resource asks were oversized for most of round 2, and that cost queue time.** `sacct` over
    the round shows the heaviest job peaked at **8.8 GB on 4 CPUs**; asks of 64 GB and 8 CPUs sat
    at `(Priority)` for **5.5 hours** while every right-sized job ran. Size from the accounting
    record, not from intuition.
11. **Stage 5 (STFlow) training has not run** — CUDA-only against a saturated GPU queue.

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
([`r4_probes_v2.csv`](results/round2/R4_probes/r4_probes_v2.csv)):

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
