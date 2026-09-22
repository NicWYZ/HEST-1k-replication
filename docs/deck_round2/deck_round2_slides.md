# HEST-1k Replication Update (round 2 deck, as presented 21 September 2026)

Text export of the Slides artifact, one section per slide: title, bullets, figure, sources line, and speaker notes as they stood in the editor on 22 September 2026. Slide source files are in `slides/`, deck order in `deck.json`. Figures are the committed files in `figures/deck/`; the intro slide uses Figure 1 of Jaume et al. (NeurIPS 2024), which is not reproduced here.

Presented on 21 September through slide 6. The next presentation resumes at slide 7.

## Slide 1. HEST-1k replication and more

**Speaker notes**

This presentation will have two parts. The first part is the replication of the HEST-1k benchmark that I was assigned, and some properties/issues with the benchmark I found along the way . The second part is some additional analysis I did once the replication was complete, as a proof of concept for two candidate research directions I came up with after some literature review using Claude.

## Slide 2. HEST-1k and its benchmark

**Figure** HEST-1k paper, Figure 1 (not reproduced)

- 1,229 ST samples aligned to H&E whole-slide images; 153 cohorts, 26 organs
- Task: predict 50 highly variable genes from a 112 µm H&E patch per spot
- Frozen encoder → PCA-256 → ridge; Pearson per gene; patient-level folds; nine cancer tasks
- Leaderboard of 25 encoders; best average Pearson ≈ 0.42

*Sources:* Jaume et al., HEST-1k, NeurIPS 2024, Figure 1. github.com/mahmoodlab/HEST

**Speaker notes**

HEST-1k. Its data contribution is scale and alignment: 1,229 spatial transcriptomics samples from 153 cohorts, each one aligned to an H&E whole-slide image, harmonised across Visium, Xenium and the older ST platform. Its second contribution is a benchmark, which is a fixed protocol for asking the question of whether image features can predict gene expression. The way it works is each spatial transcriptomics spot has a count vector over genes and a 224-pixel H&E patch at 20x centered on it, which is 112 micrometer on a side. A frozen pathology foundation model turns the patch into an embedding, which then goes through PCA to 256 dimensions and then a ridge regression head predicts the log counts of the 50 most variable genes for that task. There are nine cancer tasks. The metric is Pearson correlation per gene between predicted and true values, averaged over the 50 genes, and the cross-validation uses patients as folds so the test patient is never in training. The headline of the paper is an encoder ranking. H-Optimus-0 tops the 11 encoders in the paper, and H-Optimus-1 tops the current leaderboard of 25 encoders.

## Slide 3. Faithful replication

**Figure** `figures/deck/fig01_fidelity.png`

- 12 encoders × 3 heads × 9 tasks, on HEST's own code with pinned weights
- 108 cells vs the live leaderboard: mean |diff| 0.0002, max 0.016, 0 above 0.03
- ResNet50 exact at 0.3252; H-Optimus-1 exact at 0.4229 on its first run
- The pipeline is the benchmark's pipeline; everything downstream inherits this

*Sources:* results/summary/discrepancy_table.csv · results/summary/results_encoder.csv

**Speaker notes**

The replication is exact to the precision the current leaderboard reports. Twelve encoders (we added HO-1), 3 regression heads, ten tasks, using their own code with encoder weights loaded through their TRIDENT library on Huggingface. Against the live leaderboard, the 108 encoder and task combos all have a mean absolute difference of 0.0002. Two cells carry most of the evidential weight. ResNet50 and H-Optimus-1 both reproduces exactly. Overall I would say that the splits, gene lists, normalisation, PCA and ridge head are all wired the way the authors had them, and this is the most trivial part of the presentation.

## Slide 4. Issue 1 · The patient split does not measure what it says on two of ten tasks

**Figure** `figures/deck/fig02_replicate_leak.png`

- COAD: three patients under one label; the fold trains on one donor, tests on three. Gap 0.317 vs 0.05–0.19 elsewhere
- IDC: two 10x samples are probably two sections of one tumour, labelled as two patients
- Same-tumour section in training, all else fixed: +0.065 on IDC (6/6), 54% of its gap; +0.090 on READ (12/12)
- GitHub: COAD's labels are known (#133); the rest is not in the tracker

*Sources:* results/round2/R5b_audit/donor_audit.csv · R5c_leak/r5c_leak_summary.csv · R3_splits/r3_per_task_terms.csv

**Speaker notes**

The patient split is meant to score generalisation to an unseen patient. On two of the ten tasks it does not. In COAD, three patients share one label, so its patient fold trains on one donor and tests on three. Its gap of 0.317 is far above the 0.05 to 0.19 of the other tasks, and reflects the fold, not the tissue. IDC is the reverse: two samples are probably two sections of one tumour, labelled as different patients. The figure measures what that is worth. With the test slide and training size held fixed, adding the partner section to training raises Pearson by 0.065 on IDC, in all six cells, which is more than half of IDC's gap. READ gives a second estimate of the same effect, 0.090. COAD's labels are already known on HEST's GitHub; the rest is not reported there. The implication for us: the unit that carries shared information is the tumour, not the spot.

## Slide 5. Issue 2 · Split design outweighs encoder choice

**Figure** `figures/deck/fig03_split_staircase.png`

- Encoder spread on the benchmark's protocol: 0.098. Ignoring slide boundaries: 0.159, 1.6× that
- Steps: training size 0.013; adjacency 0.033 + 0.011 past block edges; slide-and-patient 0.102
- Multi-slide tasks: novel slide 0.015, novel patient 0.136
- Pooled Pearson over nine patients is inflated by +0.19; unbuffered blocks depend on grid size

*Sources:* results/round2/R3_splits/r3_decomposition_terms.csv · r3_per_task_terms.csv · split_v4__*.csv

**Speaker notes**

Same head, same metric, same data, the results vary only how you split. The spread between the best and worst of twelve foundation models on the benchmark's own protocol is 0.098. If instead you split spots at random, ignoring which slide they came from, and compare to the shipped patient split, the difference is 0.159. So which slides the test set is allowed to contain moves the number more than which encoder supplies the features does. I decomposed that 0.159 with a chain of designs where each step removes one more kind of shared information, so the steps add up to the total exactly. First, matching the random design's training size with the patient design's contributes 0.013, and that is pure sample size. Second, random versus a spatially blocked split at matched size, where held-out spots are contiguous patches instead of scattered: 0.033, which is adjacency, because neighbouring spots share tissue and, on Visium, physically leak transcripts into each other. Third, blocked versus blocked with a buffer that drops training spots within two and a half spot pitches of any test spot: another 0.011 that was leaking across the block edges. Fourth, buffered versus the patient split: 0.102, which is slide and patient identity together. On the three tasks where a patient contributes several slides, that last step can be splits again. A new slide with the patient's other slides still in training costs 0.015. Losing the patient entirely costs 0.136. An order of magnitude apart. Two takeaways here. Pearson computed over a pooled test set containing several patients carries between-patient variance in its denominator. I measured the inflation: exactly zero for single-patient test sets, plus 0.19 for nine-patient ones. So every number here is Pearson within slide, which matches the paper design. And a blocked spatial split without a buffer gives a result that depends on the grid size you chose, because finer grids have more edge.

## Slide 6. Issue 3 · Table A13 ranks encoders by embedding width

**Figure** `figures/deck/fig04_raw_head_width.png`

- Penalty α = 100/(d·n_genes) ≈ 0.008 at d = 256: unpenalised least squares in effect
- Raw embeddings: Gram condition number up to 3.0 × 10¹⁵; the same α leaves the solve singular
- Spearman(width, score): −0.95 raw ridge, +0.73 PCA ridge. ≥1536 dims rank 7–12; ≤1024 rank 1–6
- H-Optimus-1: rank 1 with PCA, rank 7 without

*Sources:* results/tailored/regularization/alpha_sweep.csv · results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv

**Speaker notes**

This is something I found along the way. The benchmark sets its ridge penalty as 100 divided by the number of features times the number of genes. On 256 PCA components that is about 0.008, which makes the fit indistinguishable from unpenalized least squares; a sweep over the penalty shows it is about five orders of magnitude below where it starts to matter. On raw embeddings of 1,500 to 2,500 dimensions the same tiny penalty does nothing either, and the Gram matrix has condition number near 10^15. So the raw head is effectively unregularized least squares on an ill-conditioned design, and the more dimensions an encoder has, the more noise the fit absorbs. That is why Table A13, the paper's comparison on raw embeddings, ranks encoders by width: Spearman correlation between width and score is negative 0.95. Every encoder with 1,536 or more dimensions sits in ranks 7 through 12, every encoder with 1,024 or fewer in ranks 1 through 6, and the 512-dimensional CONCH v1 wins. PCA to 256 gives every encoder the same number of features, which removes that penalty for width. The correlation then flips to plus 0.73: with width held equal, the wider, larger encoders are actually the better ones. That reversal is what shows Table A13 measures width, not representation quality. As a falsification test I ran H-Optimus-1, the strongest encoder, on the raw head: rank 1 with PCA, seventh without.

## Slide 7. Where the field is

- Accuracy has a low ceiling: HEST 0.42, STFlow 0.415; HESCAPE (2025) finds contrastive pretraining degrades expression prediction; no clean scaling laws (Nat Methods 2026)
- Embeddings are dominated by nuisance variation: institution recoverable at ~100% from UNI2/Virchow2 (GLMP, this group; Kömen et al.; de Jong et al.)
- Predicted expression is used as if measured: super-resolution, biomarker maps, virtual ST on H&E-only cohorts
- Only two 2026 preprints apply valid-inference machinery to ST, both narrow; TISSUE (2024) covers scRNA-reference imputation, not histology

**Speaker notes**

Once I finished the replication I did a brief literature review. First, accuracy has a low ceiling and pushing it is a crowded field. HEST sits at 0.42. STFlow which adds spatial context through flow matching is similar at 0.415. Dozens of histology-to-expression architectures have appeared since 2024. And the most recent evidence, the HESCAPE benchmark, finds that the obvious next step, namely contrastive pretraining on paired images and expression, makes direct expression prediction worse. A Nature Methods paper this year found no clean data scaling laws for single-cell foundation models across four hundred pretrained models. Secondly, embeddings are dominated by nuisance variation. GLMP and two other 2025 papers, show that a linear probe recovers which institution a slide came from at near 100% accuracy from UNI2 or Virchow2 embeddings, and stain normalization does not fix it. I did a similar experiment which i'll show later. Third, the outputs of these models are consumed downstream as if they were measurements. Fourth, almost nobody has asked how wrong a given prediction is, or how to make inference on predicted expression valid. Two preprints from this year apply valid-inference machinery to spatial transcriptomics, one on differential expression after imputation and one on segmentation bias through prediction-powered inference. Both are narrow, and neither handles the dependence structure I just showed, the fact that spots are clustered within slides and donors rather than independent. So the open problem, as I read it, is not accuracy. It is trust: calibrated uncertainty, and valid inference when predictions replace measurements.

## Slide 8. Two candidate directions (exploratory)

- Topic A · Calibrated uncertainty for histology-to-expression prediction under cohort shift: per-spot, per-gene intervals with guaranteed coverage; characterise and repair failure when the slide, session or donor is new
- Topic B · Valid inference for population quantities using predicted expression: intervals for a morphology–expression relationship on H&E-only slides, from a small measured set; prediction-powered inference with cluster-robust variance
- Both biology-light; both run on HEST-1k; both connect to the semi-supervised inference literature (PPI, DML, SynSurr)
- The replication was instrumented to answer three questions these need: is the predictor sound enough to calibrate; what shift exists; what is the unit of inference

**Speaker notes**

Two directions. Topic A is calibrated uncertainty for histology-to-expression prediction under cohort shift. Per spot and per gene, produce an interval with a coverage guarantee, and characterize what happens to coverage when the test slide, scanning session, or donor is new, and how to repair it. The tools are split conformal prediction, its quantile-regression variant, and weighted conformal with an estimated density ratio for the shift, with a negative-binomial head as a model-based comparator. Topic B is valid inference for population quantities using predicted expression. Suppose you want a confidence interval for a relationship between morphology and expression across a cohort of H&E-only slides, and you have a small set of slides where expression was measured. Prediction-powered inference gives valid intervals in that setting for independent data; the work is to make it valid under the dependence structure here, with a cluster-robust variance and a validation that masks measured slides to check coverage. Both run on HEST-1k. Both connect to the semi-supervised inference literature I have been reading. The additional analysis were conducted to answer three questions the topics need answered: is the base predictor sound enough to calibrate, what kind of shift actually exists on this data, and what is the right unit of inference. The next three slides take those in order.

## Slide 9. Result 1 · The benchmark head has no intercept: the R² ladder

**Figure** `figures/deck/fig05_r2_ladder.png`

- fit_intercept=False on centred PCA features: predictions mean ≈ 0, targets ≈ 0.6. Pearson hides it; R² does not
- R² = 2rρ − ρ² − b²/s²: level b, scale ρ, pattern r
- Fold-median R²: −0.95 → −0.16 (intercept) → +0.03 (oracle level) → +0.10 (optimal scale) = r², the ceiling
- Predictions spread 1.84× more than optimal; ratio orders with encoder quality
- ρ = SD(prediction) / SD(target). With b = 0, R² peaks at ρ = r, so optimal predictions have variance r² × the true variance

*Sources:* results/round2/R1b_heads/r1b_ladder_by_task.csv · r1b_ladder_pooled.csv · acceptance__*__f64.csv

**Speaker notes**

Topic A works with residuals, interval widths and scoring rules, all of which live on the absolute scale. Pearson is invariant to shifting or scaling the predictions. So the first thing to check was whether the base predictor is located correctly. It is not. The benchmark's ridge head is fit with no intercept, on PCA features that are centered by construction. That means the fitted predictions have a mean of about zero, while the targets, log(1+y), are non-negative with a mean around 0.6. The benchmark R^2 per fold is negative in 28 of 29 folds, with a median of minus 0.95. Not noticeable because Pearson centers both series internally before comparing them. To see where the deficit goes, I used the identity R² = 2rρ − ρ² − b²/s², where b is the difference in prediction vs true mean, ρ is the ratio of prediction SD to true SD, and r is Pearson. That splits the R^2 into level, scale and pattern component (first two plots). Each component can be separately computed on stored predictions with no refitting. Add a training-mean intercept: median R² goes from minus 0.95 to minus 0.16, recovering 0.80. Instead if we use the test slide's own gene mean, which uses test labels and so is a diagnostic rather than a method, R^2 becomes +0.03. But that gap, what the test mean recovers more than using the training mean, is a slide-level mean shift that no intercept estimated from training can track. With some algebra we can show that the R^2 is maximized at rho=r (assuming b is 0), so the optimal prediction has a variance a factor of r^2 smaller than the true variance. Rescale the predictions optimally adds another 0.10, which equals r² exactly, the ceiling of R^2. So the R^2 deficit is two-thirds level, then slide shift, then scale, against a ceiling set by how well the pattern correlates, namely pearson r. The scale term has a direct reading. This head has a spread ratio rho of 0.58 against a correlation of 0.32, so it spreads 1.84 times more than it should. The ratio is worst for the weakest encoder and best for the strongest, because stronger models create a higher r but all models create similar rho (last plot). That is the concrete target a calibration layer has to hit. I refit the head with an intercept, which leaves pearson unchanged, and that head is what Topic A will builds on.

## Slide 10. Result 2 · A slide-and-session signature in the features, not in the expression

**Figure** `figures/deck/fig06_session_signature.png`

- PRAD patient 2: 15 slides, one prostate; two scan sessions 0.0066 µm/px apart
- Slide identity from embeddings: 0.87–0.95 (chance 0.07). Session: 0.97–0.99
- Morphology regressed out: 1.4% of the signature removed within patient, 17–27% across patients
- Patient 1, pixel sizes 20% apart: resolution class at chance
- Expression variance with session on top: ≈ 0 (28/50 genes at or below zero)

*Sources:* results/round2/R4_probes/r4_probes_v2.csv · R6_variance/r6_prad_session_variance.csv · R0_resolution/resolution_by_task.csv

**Speaker notes**

Topic A's premise is covariate shift: the features move between cohorts while the relationship between tissue and expression does not. To measure that, we use PRAD patient 2 who has 15 slides from one prostate, so patient and tissue are fixed while slide varies. And inside those fifteen, the pixel-size estimates form two tight clusters, with contiguous sample IDs which signals two scanning sessions. (first plot) The slide probe is a logistic regression on the PCA features whose target is the slide label. Within each slide, contiguous spatial blocks are held out, so spatial adjacency is accounted for. Slide identity is predictable at ~91% accuracy against a chance level of 7%. The session probe with one slide held out at a time predicts session at 98%. And 94% of the slide probe's errors land on another slide from the same session. To see if tissue composition/biology is what predicts the slides, we regressed out eight nuclear-morphology covariates on the training spots, and refit the probes on the residuals. (second plot) Within one patient the accuracy drops by 1.4%, meaning composition does not predict slide. On tasks where the slides are different patients it drops by 17 to 27%, which is the composition difference between patients you would expect. To see if it is resolution, on the other PRAD patient with eight slides whose pixel sizes differ by 20%, resolution class is not predictable at all. Then on the expression side. With a nested variance decomposition in patient PRAD 2 using a nested ANOVA (that is spot within slide within session), the between-session variance component is at or below zero for 28 of 50 genes. Whatever separates the two sessions at 98% in the images contributes no measurable variance to the measured expression. That is covariate shift, because the feature distribution moves, the conditional does not. It is the case that reweighted conformal prediction is designed for, and the slide-and-session probe is the density-ratio estimator it needs. It also identifies the hard case, a test session with no support in the calibration set, which is exactly what PRAD's fold structure creates. For context on the benchmark: scan resolution varies five-fold across the 72 samples and lines up exactly with patient identity in PRAD and SKCM, so a patient fold there is a session fold as well.

## Slide 11. Result 3 · The estimand is slide-level; the unit of inference is the donor

**Figure** `figures/deck/fig07_theta_and_variance.png`

- Nuclear area vs GATA3: 0.46 on HEST's slide; 0.15, 0.01, −0.06 on the other three IDC slides
- Between-donor variance fraction: 0.39 (CCRCC, 24 donors), 0.34 (LYMPH_IDC); pooled 0.38
- New slide with the donor's other slides in training: 0.015. New donor: 0.136
- Per gene: split penalty tracks replicate gain (+0.38); between-donor variance does not (+0.04, n.s.)

*Sources:* results/round2/R6_variance/r6_theta_build_comparison.csv · r6_variance_by_task.csv · R7_pergene/r7_correlations_task_centred.csv

**Speaker notes**

Topic B needs an estimand and a unit. For the estimand, I took HEST's own biomarker example. Figure 3 of the paper reports the correlation between nuclear area and GATA3 expression on one Xenium breast slide, r=0.47, with a low p-value and not accounting for spatial dependence. I rebuilt the morphology features from HEST's shipped nuclear segmentation, with a per-sample calibration of patch geometry that turned out to be necessary and reproduces the result at r=0.46. Then I computed the same quantity on the other three IDC slides: 0.15, 0.01, and -0.06. Same tissue type, same platform. The estimand is a slide-level quantity with large between-slide variance. That is the Topic B premise. For the unit of inference, I first audited every sample's donor identity against sources outside HEST's metadata, because two of the tasks I had examined had labels that were wrong. On the corrected labels, I ran a nested variance decomposition of expression, spot within slide within donor. Pooled over the tasks with enough donors to estimate it, the cross-donor component contributes 38%. Spot-level variance dominates everywhere, at 60 to 90%. However a slide level standard error assumes independent spots and does not account for the between-donor variance, hence too narrow. Going back to the cross-validation split experiment, generalizing to a new slide when the donor's other slides are in training costs 0.015; a new donor costs 0.136. So the effective sample size for any claim about new patients should be set by the number of donors, scaled by the donor component of expression variance (derived elsewhere). And Topic B's variance has to be clustered at the donor level. For topic A: We ran a couple correlations at the individual-gene level, and found that genes whose prediction accuracy degrades most by the patient split are the ones a replicate (2 sections of 1 tumor as 2 patients) section recovers most (r=0.38), and genes that vary most between slides lose most accuracy on a new slide (r=0.21). Genes that differ most between donors are not the ones that lose most accuracy under the patient split (r=0.04). So the loss from random -> patient split is not donor-level expression offsets, which a donor intercept would capture. It is the state of the section itself (biological, technical). The correction belongs in both the features (reweight) and in slide-level offsets (intercept).

## Slide 12. Proposed next steps

- Topic A, first experiment: split conformal and CQR on the float64 intercept head; calibrate on training donors; coverage and width under three fold designs (random spot, shipped patient, audited donor), with and without session reweighting; beside the Pearson table for all 12 encoders
- Topic B, first result: θ₁ per slide with donor-clustered PPI intervals against spot-level ones; validation by masking measured slides
- Institution axis: none exists in HEST-bench; needs full HEST-1k breast (Visium across labs) or brain
- Benchmark findings: draft issue written, not sent; decide whether it becomes an issue, a note, or a paper section
- Standing rules that produced most of this: enumerate everything that differs between two arms before naming a term; audit a grouping variable against an outside source before using it

**Speaker notes**

What the replication leaves us with. For Topic A: a correctly located predictor, per-spot residuals for twelve encoders, audited donor labels, session and resolution covariates on every prediction row, a density-ratio estimator, and the shift mechanisms measured in order of size. The first experiment is fully specifiable. Split conformal and its quantile variant on the corrected head, calibrated on training donors, evaluated for coverage and width under three fold designs: random spot, the shipped patient split, and the audited donor split, with and without session reweighting, reported next to the benchmark's own Pearson table for all twelve encoders. The result that would make it a paper is the pattern of coverage failure across those three designs and its repair.

For Topic B: the morphology features, two estimands with their between-slide and between-donor variance measured, and the replicate-leak design as the validation harness. The first result, per-slide correlation with donor-clustered intervals against spot-level ones, is half done.

Two things the replication changed about the plan. The shift axis is session, slide and donor novelty, not institution; the one contrast that looked like institution was two 10x samples at different resolutions, possibly from one donor. An institution axis would need full HEST-1k, breast on Visium across labs or brain across many sources. And the unit is the donor with sections nested inside, and labels have to be audited before they are used.

The benchmark findings exist as a draft issue that has not been sent. Whether that becomes an issue to the authors, a short note, or the first section of a paper is something I would like your view on, along with whether either topic matches what you had in mind.

## Slide 13. Backup · Other benchmark properties found

- Gene panels differ within a task (PAAD: 159 genes common of 919; IDC: one sample measures 41 genes the others don't); leakage-free target selection is not well defined
- Targets were selected on all spots incl. test folds; training-only selection changes the list by half, Pearson by +0.009 mean (up to +0.044); fixed-list rank Spearman 0.51
- Xenium tasks' target lists are pairwise disjoint (14 genes common across all 15 Xenium samples)
- Scan resolution 0.137–0.688 µm/px across 72 samples; aligned exactly with patient in PRAD and SKCM; 31 of 72 uncorroborated
- Per-gene Pearson carries ~10⁻³ solver noise under the benchmark's iterative solver; predictions differ from the exact solution by up to 0.35
- READ's pairs are replicate sections of one specimen; folds group them correctly

*Sources:* results/round2/R2_fold_hvg · R0_resolution · R1b_heads/r1b_solver_sensitivity.csv · R5b_audit/donor_audit.csv

**Speaker notes**

Xenium gene panels are set per study, so within a task the samples do not measure the same genes. PAAD's three samples share 159 genes out of a union of 919. The benchmark's 50 targets sit on the intersection across all samples, which means selection used the test slide's panel. When I selected targets from training samples only, some of the chosen genes were not on the test slide's panel at all and could not be evaluated. So leakage-free target selection is not well defined here.

On selection sensitivity: I reimplemented the benchmark's selection and reproduced all ten shipped lists exactly before changing anything. Training-only selection shares 27 of 50 genes with the shipped list on average, 11 on PRAD, and moves Pearson by 0.009 on average with a task range from minus 0.07 to plus 0.04. Most of that is which genes are picked rather than the ranking having seen test spots; holding the gene set fixed, the two rankings correlate at 0.51.

The five Xenium tasks' target lists are pairwise disjoint, with 14 genes common to all fifteen Xenium samples, so across-task transfer is blocked outright.

Scan resolution spans a five-fold range and lines up exactly with patient in PRAD and SKCM; 31 of 72 samples have no independent corroboration of their pixel size.

Per-gene Pearson under the benchmark's iterative solver carries about a thousandth of solver noise, and the faithful head's predictions differ from the exact ridge solution by up to 0.35 in the worst cell. Task means are unaffected.

READ's two pairs are replicate sections of one specimen each; the folds group them correctly.

## Slide 14. Backup · Other results

- Negative binomial without zero inflation: NB beats Poisson 478/488; ZINB beats NB 28/488 by the stored flags; median ΔAIC = −2.0019; min Fano 1.6
- Buffered spatial-block CV makes the adjacency term well defined (grid-size spread 0.028 → 0.010)
- Float64 exact-solver head: three-head identity holds to 10⁻¹³; the float32 faithful head violates it by up to 0.35
- Slide identity decodable at 0.98 under spatial-block CV on every task; composition explains 17–27% cross-patient, 1.4% within patient
- IDC pair: 96% of one TENX slide's misclassified spots land on the other (chance 33%)
- COAD's shipped fold is a three-donor holdout trained on one; its 0.317 gap is a fold property
- θ₁ per-slide values robust to the morphology build (rank order identical; spread 0.49 vs 0.51)

*Sources:* results/tailored/counts · R3_splits/buffer_diagnostics · R1b_heads/acceptance__*__f64.csv · R5c_leak/r5d_idc_partner_confusion.csv

**Speaker notes**

Negative binomial without zero inflation is the right observation model. NB beats Poisson on 478 of 488 gene-task pairs, zero-inflated NB beats NB on 28 of 488 by the stored convergence flags, and the median AIC difference is minus 2.0019, which is exactly the penalty for a parameter that buys nothing. I wrote that prediction down before fitting. Some NB fits that the library reported as converged had in fact diverged; round 1 excluded them and reported 14 of 474, but that exclusion is not a column in the table, so the 28 is the number the file supports as it stands.

The buffered spatial-block design makes the adjacency term well defined; without it the result is partly a statement about block size.

The corrected head was refit in exact double precision; the three algebraically identical heads agree to ten to the minus thirteen, while the benchmark's float32 iterative solver violates the identity by up to 0.35.

Slide identity is decodable at 0.98 under spatial-block cross-validation on every task, and composition explains 17 to 27% of that on cross-patient tasks against 1.4% within a patient.

For the IDC pair, 96% of one TENX slide's misclassified spots land on the other, against 33% by chance; embedding-side corroboration of the same-donor finding from a run that already existed.

COAD's decomposition independently confirms its label fault: the novel-slide term is a tenth of a standard deviation from zero while the patient term is 0.26.

The per-slide correlation values are robust to the morphology build; rank order is identical across two builds and the between-slide spread is 0.49 against 0.51.
