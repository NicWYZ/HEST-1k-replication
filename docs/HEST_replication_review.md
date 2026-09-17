# Review of the HEST-1k replication and instrumentation

Written 16 September 2026 against `NicWYZ/HEST-1k-replication` at commit `eb670fa` and the final stage report (revision 2). Everything asserted below was checked in the repository files; where a claim rests on something I could not verify from the repository, that is stated.

---

## 1. Verdict in brief

The faithful stage is complete and correct. The instrumentation layer is well built and is the asset the project will run on. The tailored stage contains four results that are genuinely new and defensible, and three attribution claims that the data do not support in the form the report states them. There is also one property of the benchmark data, visible in the repository's own metadata table but not discussed in the report, that changes how several tailored results must be read: scan resolution varies four-fold across samples and is aligned with patient identity in three tasks.

Keep: fidelity, the prediction table, the pooled-versus-within measurement, the inert penalty and the width-ranked Table A13, negative binomial without zero inflation, the gene-list disjointness finding.

Reframe: the "slide-level signature" term, the "institution shift" number, and the slide-identity probes. Each measures something real; none measures what its label says.

Add, cheaply: an intercept in the head (mandatory before Topic A), within-fold gene selection, a within-patient slide probe on PRAD, a leave-slide-out arm for multi-slide patients, block-size sensitivity, and resolution as a covariate everywhere.

---

## 2. What I checked and how

Read in full: `split_decomposition.py`, `site_probe.py`, `spatial_block_probe.py`, the per-encoder split rows, `sample_metadata.csv`, `patch_scale_sources.csv`, `fig3e_gate.csv`, `count_diagnostics.csv`, the per-fold `results.json` for `hoptimus0/pca_ridge`, the README, and the provenance files. Recomputed from the split rows: the per-task decomposition terms, the per-slide site-shift gaps, and the across-fold dispersion of the patient design. Not verifiable from the repository: the parquet prediction tables, embeddings, and anything under `instrumentation/`, which are excluded by design.

---

## 3. The faithful stage

Complete. Twelve encoders on the primary head, 108 per-task cells against the live leaderboard with zero over threshold, exact agreement for ResNet50 and H-Optimus-1. The report's argument that these two encoders carry the evidential weight is right: one has no gated weights or transform ambiguity, the other was run after the pipeline was frozen. D1 (raw ridge on ResNet50 off by 0.03) is adequately explained by the penalty sweep; that head solves a numerically singular system and its result depends on the linear algebra library. D4 (`uni_v1` off by 0.0017) changes nothing. Nothing in this stage needs to be rerun.

One presentational point. The README still says "Private repository" and "99 encoder-task cells." Both are stale.

---

## 4. The instrumentation layer

The row-identity check (every prediction row's target reconstructed independently from the AnnData, with a permutation control showing the check has power) is the right construction and should be kept exactly as is. The invariant table in `stage4a_integrity.csv` is what lets every later experiment skip re-verifying alignment. The per-task partition (OD3) is fine. The barcode criterion revision (OD1, strict subset with exact ordering) is safe for replication; note for Topic B that the excluded spots are the ones nearest the tissue edge, so the labeled set is not a uniform sample of the slide.

Approve OD1, OD3, OD4.

---

## 5. The tailored stage, result by result

### 5.1 Pooled versus within-unit Pearson

Valid and important. The script computes both metrics side by side, and the measured inflation (zero for single-patient test sets, +0.19 for nine-patient ones) is the empirical version of the variance decomposition we derived. Keep.

One correction to the label. `score()` in `split_decomposition.py` computes the correlation per *sample* (`samp` is the slide ID from the filename), averages over genes, then over slides. That is within-slide Pearson, not within-patient. For tasks where each patient contributes one slide the two coincide. For PRAD (2 patients, 23 slides), COAD (one patient with 3 slides plus a fourth of unknown patient), READ and LYMPH_IDC (2 slides per patient), they do not, and the "patient" design's within-slide number is not the benchmark's number for those tasks. Within-slide is the better-behaved metric, so keep it; just call it what it is throughout the report and note that it differs from Table 1 on multi-slide tasks.

### 5.2 The split decomposition

Two things the report claims that I confirmed in code: training-set size is matched across the random, blocked and patient designs (the random and blocked arms take each shipped fold's test size, so their training size equals the patient design's), and the site-shift arms have identical training size and identical test slide by construction with assertions. Good.

Three things the labels overstate.

**"Slide identity (stain/scanner memorisation)" conflates slide and patient.** The blocked design trains on the other blocks of every slide; the patient design trains on other patients only. In single-slide-per-patient tasks the difference is slide identity. In multi-slide tasks it is slide identity plus same-patient-other-slide information, and COAD shows how large the second part can be: its term is 0.294, against 0.03 to 0.16 everywhere else. COAD's two folds are one slide of unknown patient versus three slides of one patient, so the blocked arm trains on three slides of the test patient. That is patient leakage, not stain memorisation. The per-task terms, recomputed from the rows:

| task | adjacency | blocked − patient | total |
|---|---|---|---|
| CCRCC | 0.031 | 0.026 | 0.057 |
| COAD | 0.034 | 0.294 | 0.328 |
| HCC | 0.063 | 0.108 | 0.170 |
| IDC | 0.027 | 0.097 | 0.123 |
| LUNG | 0.020 | 0.163 | 0.183 |
| LYMPH_IDC | 0.031 | 0.071 | 0.102 |
| PAAD | 0.023 | 0.130 | 0.153 |
| PRAD | 0.024 | 0.090 | 0.114 |
| READ | 0.051 | 0.120 | 0.171 |
| SKCM | 0.030 | 0.144 | 0.174 |

The pooled 0.124 is a mean over tasks that differ in what the term contains. Report it per task, and add a leave-one-slide-out-within-patient arm for PRAD, COAD, READ and LYMPH_IDC so the slide and patient components can be separated where they differ.

**The adjacency term is a lower bound.** The blocked design holds out whole grid cells but imposes no buffer, so test spots on a block edge still have training neighbours one pitch away. The nearest-training-spot distance widened by a median 2.8× (verified in `spatial_block_probe.csv`), which is a real change, but adjacency is only partially broken. A buffered block design would give a cleaner number. This is a refinement, not a flaw.

**One grid size.** The report says so. Two more (4×4, 10×10) would show whether the adjacency term is stable.

The dispersion across folds of the patient design is available in the rows and should be in the report next to every mean: for example IDC 0.591 ± 0.091, PAAD 0.502 ± 0.054, CCRCC 0.203 ± 0.057. COAD's ± 0.002 across two folds and three encoders looks too tight to be typical and is worth a glance.

### 5.3 Scan resolution varies four-fold and is aligned with patient identity

This is in the repository's own tables and is the most consequential thing the report does not say. From `sample_metadata.csv` and `patch_scale_sources.csv`, the estimated pixel size of the source image for each benchmark sample:

| task | samples and µm/px | consequence |
|---|---|---|
| PRAD | patient 2: 15 slides at 0.341 to 0.349; patient 1: 5 at 0.573, 2 at 0.688, 1 at 0.172 | the two patients are two resolution groups |
| SKCM | TENX115 at 0.274; TENX117 at 0.137 | the two patients differ two-fold |
| PAAD | TENX116 at 0.137; TENX126 and TENX140 at 0.274 | one of three patients differs two-fold |
| IDC | TENX95 and TENX99 at 0.2125; NCBI783 at 0.274; NCBI785 at 0.364 | source is aligned with resolution |
| COAD | TENX147 at 0.250; the other three at 0.274 | small |
| CCRCC, READ, LUNG, LYMPH_IDC, HCC | uniform within task | no confound |

Seven PRAD slides come from source regions of about 195 px that were upsampled to 224; one comes from a 652 px region downsampled. Interpolation leaves a per-slide signature in sharpness and texture statistics that any encoder will pick up and a linear probe will read. Three consequences follow.

First, in PRAD, SKCM and PAAD the shipped patient folds are resolution folds. Part of what Table 1 calls generalisation to a new patient in those tasks is generalisation to a new scan resolution. This is a property of the public benchmark, and nobody has written it down.

Second, every slide-identity and source probe in the report is partly a resolution probe, and every "slide signature" term includes it. The report's inference that slide identity reflects "stain, scanner, section" is not wrong, but resolution is a fourth candidate and in three tasks it is the dominant one.

Third, resolution is a per-slide technical covariate that is neither biology nor institution, which makes it the cleanest example the project has of the kind of nuisance variable Topic A's density-ratio weighting is supposed to handle. Add `pixel_size_um_estimated` to the metadata joined to every prediction row and use it as a covariate or stratification variable in every probe and shift analysis from here on.

### 5.4 The IDC "institution" contrast is not an institution contrast

The report calls TENX versus NCBI within IDC "the only confound-free contrast: same tissue, same assay, same panel, differing only in source institution." The repository's own metadata says otherwise on two counts.

The cohort prefix is the repository the file was downloaded from, not the lab that generated it. NCBI783 and NCBI785 are the GEO deposit of Janesick et al. (2023), whose authors are 10x Genomics staff; TENX95 and TENX99 are from 10x's own portal. Both halves were generated by the same company. The label "institution" does not apply.

Resolution differs: the TENX slides are at 0.2125 µm/px, the NCBI slides at 0.274 and 0.364. So even setting the lab aside, the contrast moves resolution.

The per-slide gaps, recomputed from the rows and averaged over the three encoders, are asymmetric in exactly the way a resolution explanation predicts:

| held-out slide | gap (seen − unseen) |
|---|---|
| NCBI783 | 0.002 |
| NCBI785 | 0.014 |
| TENX95 | 0.052 |
| TENX99 | 0.099 |

Adding the other TENX slide (same 0.2125 resolution) to training helps predict a TENX slide by 0.05 to 0.10; adding the other NCBI slide (different resolution, 0.274 versus 0.364) helps predict an NCBI slide by almost nothing. An institution effect would be roughly symmetric. The headline 0.0419 is the mean of these four and should not be reported as a scalar site-shift effect.

There is a further possibility I cannot verify from the repository: 10x reused one breast cancer FFPE block across several of its public Xenium demos, and the Janesick paper's Xenium data is that demo. HEST's metadata assigns four distinct patient labels, but if any two of these slides are serial sections of the same block, the IDC task's own folds contain patient leakage and its Pearson of 0.59 is inflated. This needs a check against the Janesick methods and the 10x dataset pages before the IDC task is used as the site-shift headline for anything.

The honest statement is that HEST-bench contains no clean institution contrast at all. That is a finding about the benchmark. It also settles where the site-shift axis of Topic A has to come from: full HEST-1k, where breast appears on Visium across several labs and brain has over two hundred samples from many sources.

### 5.5 The probes

The technology probe (0.994) and cohort-source probe (0.938) are labelled as confounded in the report and in the script docstring, which is correct; each task is one technology and most sources appear in one task, so these are tissue probes. Drop them from the site narrative or move them to an appendix.

The slide-identity probe under spatial blocking (0.98) establishes that slides are linearly separable in embedding space even when local neighbours are removed. It does not establish that the separating signal is technical. Two patients' tumours look different; two scan resolutions look different; two stain batches look different; the probe cannot tell them apart. The design that can is a slide probe *within one patient at one resolution*: PRAD patient 2 has fifteen slides at pixel sizes between 0.341 and 0.349, so biology and resolution are nearly fixed and only section, staining and scanning vary. If slide identity is decodable there, that is a technical signature. If it is not, the 0.98 elsewhere is mostly biology and resolution. This is one script on cached embeddings.

The IDC institution probe (0.68 balanced accuracy, encoder-level range 0.46 to 0.91, standard deviations of 0.3 to 0.45 on four leave-one-out folds) is uninformative at this sample size and, per 5.4, mislabelled. Report it as inconclusive and drop it from the headline table.

### 5.6 The ridge penalty, Table A13, and the missing intercept

The penalty sweep is the best result in the tailored stage. At $\alpha = 100/(256 \times 50) \approx 0.008$ on standardised-then-PCA features, the fit is OLS on 256 principal components to solver tolerance; at raw width the Gram condition number is $7.6 \times 10^{14}$ and the same $\alpha$ leaves the solve effectively unregularised. Spearman(embedding dimension, score) of $-0.954$ on `raw_ridge` against $+0.735$ on `pca_ridge` means Table A13 ranks encoders by width. Keep; write it up as a self-contained note for David now.

What the report does not say, and the per-fold results confirm: the benchmark head has no intercept. `Ridge(fit_intercept=False)` on PCA features that are centred by construction gives predictions with training mean zero for each gene, while $\log(1+y)$ has a positive mean. Pearson is invariant to that shift, so the benchmark never noticed. The trainer also records $R^2$, and across the 29 folds of `hoptimus0/pca_ridge` the median per-gene $R^2$ is negative in 28 of them, with fold medians from $-0.1$ to $-4.7$. That is the signature of a level offset, not of a bad slope. Every quantity Topic A cares about (absolute residuals, CRPS, interval width) is not shift-invariant, so the head must be refit with an intercept (or $y$ centred per gene on the training fold) before any calibration work. Pearson should be unchanged to numerical tolerance; confirm that.

### 5.7 Observation model

Valid. NB beats Poisson on 478 of 488 converged pairs; ZINB beats NB on 14 of 474; the median $\Delta\text{AIC}$ of $-2.0019$ is exactly the one-parameter penalty, which is what you get when $\hat\pi = 0$ at the boundary. The catch of fourteen diverged NB fits flagged as converged by the library is the kind of silent failure the group's principles are about.

Two caveats to add to the text. The 50 genes were selected for high normalised dispersion, so "every gene is overdispersed" is partly selection. And these are marginal fits pooled over spots, so the Fano factors (median 3 to 7 on Visium tasks, 40 to 100 on Xenium) include between-spot biological variation, not only measurement noise. The number that matters for Topic A is the conditional dispersion after an image-conditioned NB head is fit; that has not been measured.

### 5.8 Morphology and the Figure 3e gate

Valid. $r = 0.458$ on NCBI785 against the paper's 0.47. Note that the gate is computed per spot (mean neoplastic nuclear area against spot-level GATA3 count) while the paper computed it per cell with CellViT nuclei matched to Xenium cells, so agreement to 0.01 is partly luck; the two units need not give the same number.

The slide-specificity result is the important one: 0.458 on NCBI785, 0.133 on NCBI783, 0.012 on TENX95, $-0.048$ on TENX99. Whatever $\theta_1$ is, it is a slide-level quantity with large between-slide variance. That is the strongest single motivation Topic B has, because it is exactly the between-cluster variance component that spot-level inference ignores and that the cluster-level PPI variance is designed to capture. It also raises the question of whether TENX95 and TENX99 are biologically different from NCBI785 or whether the 0.2125 µm/px scan changes CellViT's area estimates; the nuclear-area distributions per slide would answer that.

The patch-geometry finding (extents 163 to 818 px) is the same fact as 5.3 seen from the morphology side, and the report's conclusion that no constant patch size in pixels or microns is correct across samples is right.

### 5.9 Held-out gene check

The script establishes that ridge does not couple targets, which is true by construction of a per-target linear solve. The report says so and correctly identifies the leakage that matters as gene selection on all spots including test folds. It then says quantifying that "would be a different benchmark." It would not; it is one extra loop: per fold, rank genes on training spots only, take the top 50, fit, evaluate on those genes on the test slide, and compare to the shipped protocol on the same fold. The gene set differs slightly per fold, which is fine for a paired comparison. This turns a disclaimer into a number.

### 5.10 Across-task shift

The finding that the five Xenium tasks' top-50 lists are disjoint and their panels share 14 genes (D5) is correct and closes this direction. Record it and stop.

---

## 6. What to change and rerun

Ordered by how much they change conclusions. All run on cached embeddings; none needs a GPU.

1. **Refit the head with an intercept** and confirm Pearson unchanged and $R^2$ positive. Blocks Topic A.
2. **Add `pixel_size_um_estimated` to the joined metadata** and re-run every probe and shift table stratified by it or with it as a covariate.
3. **Split decomposition:** report per-task terms with fold dispersion; add a leave-one-slide-out-within-patient arm for PRAD, COAD, READ, LYMPH_IDC; add a buffered block variant and two more grid sizes; relabel the metric as within-slide.
4. **Relabel the IDC contrast** as "novel slide, same generating lab, different scan resolution," report the four per-slide gaps, and remove 0.0419 from the headline table.
5. **Probes:** move technology and cohort-source probes to an appendix; report the IDC probe as inconclusive; add the PRAD patient 2 within-patient slide probe.
6. **README:** remove "Private," update 99 to 108 cells, and add the resolution table from 5.3 to the known-limitations section.

---

## 7. Additional experiments

1. **Within-fold gene selection** (5.9). One script. Gives the size of the benchmark's selection leakage.
2. **Within-patient slide probe, PRAD patient 2** (5.5). Decides whether slide signatures are technical.
3. **Per-slide $\theta_1$ with variance components** for every benchmark slide with enough neoplastic nuclei: within-slide sampling variance against between-slide variance. Topic B's opening figure.
4. **Per-gene leakage.** From the existing rows, the random-minus-patient gap per gene rather than averaged. If leakage concentrates in a few genes, per-gene coverage in Topic A will be heterogeneous in a predictable way.
5. **Nuclear-area distributions by slide and resolution**, to check whether CellViT's area estimates shift with scan resolution. Cheap, and it decides whether the morphology covariates need a resolution correction before Topic B.
6. **Provenance check on the IDC slides** against the Janesick methods and 10x dataset descriptions (5.4, last paragraph). A reading task, not a compute task.
7. **H-Optimus-1 on the raw heads.** Cheap falsification of D2. Nothing depends on it.
8. **STFlow.** Defer.

---

## 8. What this means for the two topics

Topic A. The base predictor needs an intercept before anything else. The shift axis that HEST-bench actually supports is resolution and slide novelty, not institution; the report's numbers, reframed, are the right motivation for that. Institution shift will need full HEST-1k. The negative-binomial head is justified marginally; conditional dispersion is the next measurement.

Topic B. The slide-specificity of $\theta_1$ (5.8) and the COAD result (5.2) are the two clearest demonstrations in the whole repository that the slide, not the spot, is the unit of inference. Both belong in the motivation.

---

## 9. Process

The report retracted an inflated number, measured an artefact instead of assuming it, caught diverged fits behind a false convergence flag, and left provenance on everything. That is the right way to work and it made this review possible. The failure mode to watch is the one visible in 5.3 and 5.4: a label chosen at design time ("institution," "stain/scanner") carried through to the conclusions without being re-checked against the metadata that was sitting in the same directory. The fix is procedural: before any term in a decomposition is named, list every variable that moves between its two arms.
