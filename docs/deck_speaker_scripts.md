# Speaker scripts for the progress update

Full scripts, one per slide, written to be spoken at about 150 words per minute. Total spoken length is about 2,300 words, which is 15 minutes with pauses for figures. Bullets and figure choices are unchanged from `deck_master_outline.md`; this file replaces its notes sections.

---

## Slide 1. Title (20 seconds)

This is a preliminary progress update, in two parts. The first part is the replication of the HEST-1k benchmark that I was assigned. That part is exact, and I will get through it quickly. The second part is what I did with the replication once it was working. I instrumented it to test whether two candidate research directions hold up on this data, and along the way I found several properties of the benchmark itself that I think anyone using it should know about. I want to be clear that the two directions are a proposal, not a commitment. I do not yet know what you have in mind for the project, so the point of today is to show you what the data say and get your read on where to go.

---

## Slide 2. HEST-1k and its benchmark (60 seconds)

HEST-1k is a NeurIPS 2024 dataset from the Mahmood lab. Its data contribution is scale and alignment: 1,229 spatial transcriptomics samples from 153 cohorts, each one aligned to an H&E whole-slide image, harmonised across Visium, Xenium and the older ST platform. Its second contribution is a benchmark, which is a fixed protocol for asking one question: can image features predict gene expression?

The protocol works like this. Each spatial transcriptomics spot has a count vector over genes and a 224-pixel H&E patch at 20× centred on it, which is 112 microns on a side. A frozen pathology foundation model turns the patch into an embedding. The embedding goes through PCA to 256 dimensions and then a ridge regression predicts the log counts of the 50 most variable genes for that task. There are nine cancer tasks. The metric is Pearson correlation per gene between predicted and true values, averaged over the 50 genes, and the cross-validation uses patients as folds so the test patient is never in training.

The headline of the paper is an encoder ranking. H-Optimus-0 topped the paper at 0.41; H-Optimus-1 tops the current leaderboard of 25 encoders at 0.42. My assignment was to reproduce this. I did, and then I used the reproduction to ask what that number actually means.

---

## Slide 3. Faithful replication (50 seconds)

The replication is exact to the precision the leaderboard reports. Twelve encoders, four regression heads, ten tasks, using HEST's own code with encoder weights loaded through their TRIDENT library, everything pinned. Against the live leaderboard, that is 108 encoder-by-task cells with a mean absolute difference of 0.0002 and none above the 0.03 threshold we set in advance.

Two cells carry most of the evidential weight. ResNet50 reproduces exactly at 0.3252. It has no gated weights and no ambiguity about image transforms, so an exact hit there certifies that the splits, gene lists, normalisation, PCA and ridge head are all wired the way the authors had them. H-Optimus-1 also reproduces exactly at 0.4229, and its weights were approved only after the pipeline was frozen, so nothing was tuned to it. That is an out-of-sample confirmation.

One appendix cell was off by 0.03, ResNet50 on ridge without PCA, and I will explain that on slide 6 because the explanation turned out to be a finding. Otherwise, this stage is the floor everything else stands on. The pipeline is the benchmark's pipeline.

---

## Slide 4. Issue 1. The patient split does not measure what it says on two of ten tasks (2 minutes 15 seconds)

Let me start with what the patient split is for. It exists to score generalisation to a patient the model has never seen. On at least two of the ten tasks it does not do that, and the two faults go in opposite directions.

COAD first. HEST's metadata has a patient column, and for COAD it says three of the four samples come from one patient. But the same rows have a subseries field that reads Sample P5, Sample P2, Sample P1. Three different patients. HEST's own GitHub issue 133 confirms the labels were wrong, says they were corrected in a later data release, and says the benchmark splits were deliberately left alone on the reasoning that no patient spans train and test. That reasoning is correct as far as it goes, but the consequence is a fold that holds out three donors and trains on the one remaining sample. COAD's gap between a random spot split and the patient split is 0.317, far above every other task, which sits between 0.05 and 0.19. That is not a fact about colorectal tissue. It is a fact about the fold.

IDC goes the other way. Two of its four samples, TENX95 and TENX99, come from 10x Genomics' demonstration datasets. The dataset page for one of them states donor count one and labels them Replicate 1 and Replicate 2. They carry byte-identical gene panels, which no other pair in the task does. And when an encoder misclassifies a spot from one of them, 96% of the time it lands on the other. I am calling this probable rather than certain, because HEST attributes the two samples to two different 10x pages and the second page rate-limited every attempt to fetch it. But the label is the only thing that depends on it. The measurement does not.

Here is the measurement. Hold out TENX99. Build two training sets of identical size: one drawn from TENX95 plus the two other IDC slides, one drawn from the two other slides only. Same test spots, same training size, same pipeline, same metric. The only thing that differs is whether the partner section is in the pool. The partner is worth 0.065 Pearson within slide, positive in all six encoder-by-slide cells. IDC's entire random-minus-patient gap is 0.121, so more than half of what the benchmark's patient split scores as generalisation to a new patient is recoverable from having another section of the same tumour in training.

I repeated the design on READ, whose two pairs are replicate sections of the same specimens. The value of a replicate there is 0.090, positive in twelve of twelve cells. READ's folds happen to group the pairs correctly, so no leak is realised in the shipped split. That makes READ a second independent estimate of the same quantity rather than a second defect.

On overlap with the GitHub tracker: COAD's labels are known there. The IDC pair, the size of the replicate effect, and everything on the next two slides and the backup slide are not reported there as far as I can find.

Why this matters for us is that the unit that carries shared information is the tumour section. Not the spot, and not even the slide as an image. I will come back to that.

---

## Slide 5. Issue 2. Split design outweighs encoder choice (2 minutes)

Same head, same metric, same data. Vary only how you split.

The spread between the best and worst of twelve foundation models on the benchmark's own protocol is 0.098. If instead you split spots at random, ignoring which slide they came from, and compare to the shipped patient split, the difference is 0.159. So which slides the test set is allowed to contain moves the number more than which encoder supplies the features does.

I decomposed that 0.159 with a chain of designs where each step removes one more kind of shared information, so the steps add up to the total exactly. First, random versus random with the training set shrunk to match the patient design's size: 0.013, and that is pure sample size. Second, random versus a spatially blocked split at matched size, where held-out spots are contiguous patches instead of scattered: 0.033, which is adjacency, because neighbouring spots share tissue and, on Visium, physically leak transcripts into each other. Third, blocked versus blocked with a buffer that drops training spots within two and a half spot pitches of any test spot: another 0.012 that was leaking across the block edges. Fourth, buffered versus the patient split: 0.102, which is slide and patient identity together. On the three tasks where a patient contributes several slides, that last step splits again. A new slide with the patient's other slides still in training costs 0.015. Losing the patient entirely costs 0.136. An order of magnitude apart.

Two things about measurement came out of this that I think are reusable. Pearson computed over a pooled test set containing several patients carries between-patient variance in its denominator. I measured the inflation: exactly zero for single-patient test sets, plus 0.19 for nine-patient ones. So every number here is Pearson within slide, which is also what the shipped folds already compute. And a blocked spatial split without a buffer gives a result that depends on the grid size you chose, because finer grids have more edge. Across three grid sizes the unbuffered spread was 0.028, almost the size of the adjacency term. With the buffer the spread is 0.010 and flat.

For honesty about process: the first version of this reported a leakage gap of 0.31, and half of that was the pooled-Pearson artefact. It was retracted and rebuilt. The second version conflated slide and patient. What you see is the third version.

---

## Slide 6. Issue 3. Table A13 ranks encoders by embedding width (1 minute 20 seconds)

This one started as the discrepancy I mentioned. ResNet50's cell in the paper's appendix table for ridge on raw embeddings reproduced 0.03 low, and my first hypothesis was a penalty confound. The benchmark sets its ridge penalty as 100 divided by the number of features times the number of genes. On 256 PCA components that is about 0.008.

I ran a twelve-point sweep of the penalty at both feature widths and recorded the condition number of the Gram matrix each time. The sweep killed the hypothesis. At the benchmark's value the fit is indistinguishable from unpenalised least squares, five orders of magnitude below where the penalty starts to matter. But it produced a better explanation. On raw embeddings of 1,500 to 2,500 dimensions the Gram matrix has condition number near 10 to the 15, which means the same tiny penalty leaves the system effectively singular, and the answer depends on the linear algebra library. That is why that one cell moves and nothing else does.

The consequence is for Table A13, the paper's comparison of encoders on raw embeddings. It ranks encoders by dimension. Spearman correlation between embedding width and score is minus 0.95 in that table, and plus 0.73 once you equalise width at 256 with PCA. Every encoder with 1,536 or more dimensions sits in ranks 7 through 12; every encoder with 1,024 or fewer sits in ranks 1 through 6; the 512-dimensional CONCH v1 wins outright.

As a falsification test I ran H-Optimus-1, the strongest encoder in the set, on the raw head. It is rank 1 with PCA. If the explanation is right it should land mid-table without PCA. It landed seventh. The practical reading is that Table A13 should not be cited as an encoder comparison.

---

## Slide 7. Where the field is (1 minute 30 seconds)

Let me step back and place this in the literature, in four lines.

First, accuracy has a low ceiling and pushing it is crowded. HEST sits at 0.42. STFlow, an ICML 2025 method that adds spatial context through flow matching, reaches 0.415. Dozens of histology-to-expression architectures have appeared since 2024. And the most recent evidence, the HESCAPE benchmark, finds that the obvious next step, contrastive pretraining on paired images and expression, makes direct expression prediction worse. A Nature Methods paper this year found no clean data scaling laws for single-cell foundation models across four hundred pretrained models.

Second, embeddings are dominated by nuisance variation. GLMP from this group, and two other 2025 papers, show that a linear probe recovers which institution a slide came from at near 100% accuracy from UNI2 or Virchow2 embeddings, and stain normalisation does not fix it. What I will show on slide 10 is the same phenomenon measured from inside HEST.

Third, the outputs of these models are consumed downstream as if they were measurements: super-resolution, biomarker maps, virtual spatial transcriptomics on H&E-only cohorts.

Fourth, almost nobody has asked how wrong a given prediction is, or how to make inference on predicted expression valid. Two preprints from this year apply valid-inference machinery to spatial transcriptomics, one on differential expression after imputation and one on segmentation bias through prediction-powered inference. Both are narrow, and neither handles the dependence structure I just showed you.

So the open problem, as I read it, is not accuracy. It is trust: calibrated uncertainty, and valid inference when predictions replace measurements.

---

## Slide 8. Two candidate directions, exploratory (1 minute 15 seconds)

Two directions follow from that gap.

Topic A is calibrated uncertainty for histology-to-expression prediction under cohort shift. Per spot and per gene, produce an interval with a coverage guarantee, and characterise what happens to coverage when the test slide, scanning session, or donor is new, and how to repair it. The tools are split conformal prediction, its quantile-regression variant, and weighted conformal with an estimated density ratio for the shift, with a negative-binomial head as a model-based comparator.

Topic B is valid inference for population quantities using predicted expression. Suppose you want a confidence interval for a relationship between morphology and expression across a cohort of H&E-only slides, and you have a small set of slides where expression was measured. Prediction-powered inference gives valid intervals in that setting for independent data; the work is to make it valid under the dependence structure here, with a cluster-robust variance and a validation that masks measured slides to check coverage.

Both are statistics problems; the biology is a wrapper. Both run on HEST-1k. Both connect to the semi-supervised inference literature I have been reading.

I want to be explicit about framing. These are exploratory. The replication was instrumented so that its byproducts would answer three questions the topics need answered: is the base predictor sound enough to calibrate, what kind of shift actually exists on this data, and what is the right unit of inference. The next three slides take those in order.

---

## Slide 9. Result 1. The benchmark head has no intercept, and the $R^2$ ladder (2 minutes)

Topic A works with residuals, interval widths and scoring rules, all of which live on the absolute scale. Pearson does not; it is invariant to shifting or scaling the predictions. So the first thing to check was whether the base predictor is even located correctly.

It is not. The benchmark's ridge head is fit with no intercept, on PCA features that are centred by construction. That means the fitted predictions have a mean of about zero, while the targets, log of one plus count, are non-negative with a mean around 0.6. The benchmark already stores an $R^2$ per fold, and it is negative in 28 of 29 folds, with a median of minus 0.95. Nobody noticed because Pearson centres both series internally before comparing them.

To see where the deficit goes, I used the identity $R^2 = 2r\rho - \rho^2 - b^2/s_y^2$, where $b$ is the level offset, $\rho$ is the ratio of predicted spread to true spread, and $r$ is Pearson. That splits everything a predictor can get wrong into level, scale and pattern. Then I climbed a ladder, fixing one at a time, computed on stored predictions with no refitting.

Add a training-mean intercept: median $R^2$ goes from minus 0.95 to minus 0.16, recovering 0.80. Replace it with the test slide's own gene mean, which uses test labels and so is a diagnostic rather than a method: plus 0.03, another 0.19. That gap is a slide-level mean shift that no intercept estimated from training can track. Rescale optimally on top: plus 0.10, which equals $r^2$ exactly, the ceiling that no recalibration of level and scale can pass. So the deficit is two-thirds level, then slide shift, then scale, against a ceiling set by how well the pattern correlates.

The scale term has a direct reading. When correlation is below one, the best prediction shrinks toward the mean by a factor of $r$. This head has a spread ratio of 0.58 against a correlation of 0.32, so it spreads 1.84 times more than it should. The ratio is worst for the weakest encoder and best for the strongest. That is the concrete target a calibration layer has to hit.

I refit the head with an intercept in exact double-precision arithmetic, verified that the intercept changes predictions by exactly a per-gene constant and leaves Pearson unchanged to thirteen decimal places, and that head is what Topic A builds on.

---

## Slide 10. Result 2. Encoders carry a slide-and-session signature that is in the features and not in the expression (2 minutes 15 seconds)

Topic A's premise is covariate shift: the features move between cohorts while the relationship between tissue and expression does not. I wanted to measure that rather than assume it.

Round one had found slides separable in embedding space at 0.98, but every pair of benchmark slides differs in patient, tissue, resolution and technical conditions all at once, so that number said nothing about mechanism. PRAD patient 2 is the one place in the benchmark where patient and tissue are fixed while slide varies: fifteen slides from one prostate, with estimated pixel sizes that differ by only two percent. And inside those fifteen, the pixel-size estimates form two tight clusters, 0.0066 microns per pixel apart, with contiguous sample IDs. That is what two scanning sessions look like.

The probe is a logistic regression on the PCA features whose target is the slide label. Within each slide, contiguous spatial blocks are held out, so a held-out patch's neighbours are not in training and the classifier cannot succeed by matching nearby tissue. Slide identity is decodable at 0.87 to 0.95 against a chance level of 0.07. Session, two classes with one slide held out at a time, is decodable at 0.98. And 94% of the slide probe's errors land on another slide from the same session. The session axis is the easy one.

Is that tissue composition? I regressed each feature on eight nuclear-morphology covariates, fit on training spots only, and probed the residuals. Within one patient the signature drops by 1.4%. On tasks where the slides are different patients it drops by 17 to 27%, which is the composition difference between patients you would expect. Within a patient, it is not composition.

Is it resolution? The other PRAD patient has eight slides whose pixel sizes differ by 20%. Resolution class is not decodable at all, 0.49 to 0.51. A first version of that probe reported 0.7, and I withdrew it when writing out the class sizes showed a five-to-two split, where a classifier that always predicts the majority scores 0.71. So the encoder reads session and slide. Nominal resolution is a proxy for session, not the thing encoded.

Then the other side of the premise. Decompose the expression within patient 2 with session as the top level. The between-session variance component is at or below zero for 28 of 50 genes. The thing that separates the two sessions at 0.98 in the images contributes no measurable variance to the measured expression. That is covariate shift, measured: the feature distribution moves, the conditional does not. It is the case that reweighted conformal prediction is designed for, and the slide-and-session probe is the density-ratio estimator it needs. It also identifies the hard case, a test session with no calibration support, which is exactly what PRAD's fold structure creates.

For context on the benchmark: scan resolution varies five-fold across the 72 samples and lines up exactly with patient identity in PRAD and SKCM, so a patient fold there is a session fold as well.

---

## Slide 11. Result 3. The Topic B estimand is a slide-level quantity, and the unit of inference is the donor (2 minutes)

Topic B needs an estimand and a unit.

For the estimand, I took HEST's own biomarker example. Figure 3 of the paper reports the correlation between nuclear area and GATA3 expression on one Xenium breast slide, 0.47, with a p-value below ten to the minus four and no accounting for spatial dependence or for the fact that it is one slide. I rebuilt the morphology features from HEST's shipped nuclear segmentation, with a per-sample calibration of patch geometry that turned out to be necessary, and gated everything on reproducing that figure. It reproduces at 0.46. Then I computed the same quantity on the other three IDC slides: 0.15, 0.01, and minus 0.06. Same tissue type, same platform. The estimand is a slide-level quantity with large between-slide variance. That is the Topic B premise in one row of numbers.

For the unit, I first audited every sample's donor identity against sources outside HEST's metadata, because two of the tasks I had examined had labels that were wrong. Fifty-eight verified, nine unverifiable, five contradicted. On the corrected labels, I ran a nested variance decomposition of expression, spot within slide within donor, with a moment estimator I checked on simulation first. CCRCC has 24 donors with one slide each and a between-donor fraction of 0.39. LYMPH_IDC has four donors and 0.34. Pooled over the tasks with enough donors to estimate it, 0.38. Spot-level variance dominates everywhere, at 60 to 90%, but a third of the variance sits at the donor level, and spot-level standard errors would ignore it entirely.

Which level carries the cost we saw on slide 5: a new slide with the donor's other slides in training costs 0.015; a new donor costs 0.136. So the effective sample size for any claim about new patients is the number of donors, and Topic B's variance has to be clustered there.

The per-gene results close the loop. Genes that lose most under a patient split are the genes a same-tumour section recovers most, correlation 0.38. Genes whose level varies most between sections of one tumour are the genes that lose most when the section is new, 0.21. And genes whose level differs most between donors are not the genes that lose most under a patient split, 0.04, not significant. The reading for Topic A: if the split penalty were donor biology, a per-donor random intercept would absorb it. It would not. The penalty is slide-level shared state, technical and biological together. So the fix has to act on the features, through the reweighting from the last slide, and on slide-level offsets, through the shift term from slide 9, and not through a donor effect alone.

---

## Slide 12. Proposed next steps (1 minute 15 seconds)

What the replication leaves us with. For Topic A: a correctly located predictor, per-spot residuals for twelve encoders, audited donor labels, session and resolution covariates on every prediction row, a density-ratio estimator, and the shift mechanisms measured in order of size. The first experiment is fully specifiable. Split conformal and its quantile variant on the corrected head, calibrated on training donors, evaluated for coverage and width under three fold designs: random spot, the shipped patient split, and the audited donor split, with and without session reweighting, reported next to the benchmark's own Pearson table for all twelve encoders. The result that would make it a paper is the pattern of coverage failure across those three designs and its repair.

For Topic B: the morphology features, two estimands with their between-slide and between-donor variance measured, and the replicate-leak design as the validation harness. The first result, per-slide correlation with donor-clustered intervals against spot-level ones, is half done.

Two things the replication changed about the plan. The shift axis is session, slide and donor novelty, not institution; the one contrast that looked like institution was two 10x samples at different resolutions, possibly from one donor. An institution axis would need full HEST-1k, breast on Visium across labs or brain across many sources. And the unit is the donor with sections nested inside, and labels have to be audited before they are used.

The benchmark findings exist as a draft issue that has not been sent. Whether that becomes an issue to the authors, a short note, or the first section of a paper is something I would like your view on, along with whether either topic matches what you had in mind.

---

## Slide A1 (backup). Other benchmark properties found (as needed)

Xenium gene panels are set per study, so within a task the samples do not measure the same genes. PAAD's three samples share 159 genes out of a union of 919. The benchmark's 50 targets sit on the intersection across all samples, which means selection used the test slide's panel. When I selected targets from training samples only, some of the chosen genes were not on the test slide's panel at all and could not be evaluated. So leakage-free target selection is not well defined here.

On selection sensitivity: I reimplemented the benchmark's selection and reproduced all ten shipped lists exactly before changing anything. Training-only selection shares 27 of 50 genes with the shipped list on average, 11 on PRAD, and moves Pearson by 0.009 on average with a task range from minus 0.07 to plus 0.04. Most of that is which genes are picked rather than the ranking having seen test spots; holding the gene set fixed, the two rankings correlate at 0.51.

The five Xenium tasks' target lists are pairwise disjoint, with 14 genes common to all fifteen Xenium samples, so across-task transfer is blocked outright.

Scan resolution spans a five-fold range and lines up exactly with patient in PRAD and SKCM; 31 of 72 samples have no independent corroboration of their pixel size.

Per-gene Pearson under the benchmark's iterative solver carries about a thousandth of solver noise, and the faithful head's predictions differ from the exact ridge solution by up to 0.35 in the worst cell. Task means are unaffected.

READ's two pairs are replicate sections of one specimen each; the folds group them correctly.

---

## Slide A2 (backup). Other results (as needed)

Negative binomial without zero inflation is the right observation model. NB beats Poisson on 478 of 488 gene-task pairs, zero-inflated NB beats NB on 14 of 474, and the median AIC difference is minus 2.0019, which is exactly the penalty for a parameter that buys nothing. I wrote that prediction down before fitting. Fourteen NB fits that the library reported as converged had in fact diverged; taken at face value they would have reversed the conclusion.

The buffered spatial-block design makes the adjacency term well defined; without it the result is partly a statement about block size.

The corrected head was refit in exact double precision; the three algebraically identical heads agree to ten to the minus thirteen, while the benchmark's float32 iterative solver violates the identity by up to 0.35.

Slide identity is decodable at 0.98 under spatial-block cross-validation on every task, and composition explains 17 to 27% of that on cross-patient tasks against 1.4% within a patient.

For the IDC pair, 96% of one TENX slide's misclassified spots land on the other, against 33% by chance; embedding-side corroboration of the same-donor finding from a run that already existed.

COAD's decomposition independently confirms its label fault: the novel-slide term is a tenth of a standard deviation from zero while the patient term is 0.26.

The per-slide correlation values are robust to the morphology build; rank order is identical across two builds and the between-slide spread is 0.49 against 0.51.
