# Master outline: progress update on HEST-1k replication and proposed directions

Target 15 minutes. Twelve main slides plus two backup slides. Slides carry bullets and one figure each; everything spoken is in the notes. Notes are dense and script-like; grammar is loose on purpose. Every number cites the repository file it comes from (commit `round2-final`, `3161a61`, plus the closeout commit).

Figure names refer to `figures/deck/` as specified in the companion instructions to the execution session.

---

## Slide 1. Title

**Bullets**
- HEST-1k replication and what it taught us about the problem
- Nicolas Zhang, 22 September 2026
- Repository: `NicWYZ/HEST-1k-replication`, tag `round2-final`

**Notes**
Preliminary update. Two parts. First, replicated the HEST benchmark as assigned; the faithful part is exact and short. Second, instrumented the replication to test whether two candidate directions hold up on the data. Along the way found several properties of the benchmark itself that anyone using it should know. Everything here is exploratory; want direction on which of the two topics, if either, fits what you have in mind.

---

## Slide 2. HEST-1k and its benchmark

**Figure** HEST paper Figure 1 (overview panel).

**Bullets**
- 1,229 ST samples (Visium, Xenium, ST), each aligned to an H&E whole-slide image; 153 cohorts, 26 organs
- Benchmark: predict expression of 50 highly variable genes from a 112 µm H&E patch centred on each spot
- Nine cancer tasks; frozen pathology foundation model → patch embedding → PCA-256 → ridge; Pearson per gene, patient-level folds
- Leaderboard of 25 encoders as of April 2026; best average Pearson ≈ 0.42

**Notes**
HEST-1k, NeurIPS 2024, Mahmood lab. Data contribution: pairs spatial transcriptomics with H&E at scale, harmonised alignment across three ST platforms. Benchmark contribution: a fixed protocol for asking whether image features predict expression. Each spot has a count vector over genes and a 224-pixel patch at 20× centred on it. Encoder is frozen; only a linear head is trained. Pearson correlation per gene between predicted and true log1p counts, averaged over 50 genes, cross-validated with patients as folds so the test patient is never in training. Encoder ranking is the headline: H-Optimus-0 tops the paper at 0.41, H-Optimus-1 tops the current leaderboard at 0.42. Assignment was to reproduce this. Did, and then used the reproduction to ask what the number means.

---

## Slide 3. Faithful replication

**Figure** `figures/deck/fig01_fidelity.png` (ours vs paper vs leaderboard, per encoder).

**Bullets**
- 12 encoders × 4 regression heads × 10 tasks; pipeline is HEST's own code with TRIDENT-loaded weights, pinned
- Against the live leaderboard: 108 encoder-task cells, mean |diff| 0.0002, max 0.016, 0 of 108 above the 0.03 threshold
- ResNet50 exact (0.3252); H-Optimus-1 exact (0.4229) on first run after the pipeline was frozen
- Everything downstream inherits this: the pipeline is the benchmark's pipeline

**Notes**
Reproduction is exact to the precision the leaderboard reports. Two cells carry the evidential weight. ResNet50 has no gated weights and no transform ambiguity, so an exact hit certifies splits, gene lists, normalisation, PCA and ridge are wired as the authors had them. H-Optimus-1's weights were approved after the pipeline was frozen, so nothing about it was tuned; an out-of-sample confirmation. One appendix-table cell was off by 0.03 (ResNet50 on raw-embedding ridge); explained on slide 6. Source: `results/summary/discrepancy_table.csv`, `results/summary/results_encoder.csv`. Won't dwell; this stage is the floor everything else stands on.

---

## Slide 4. Issue 1. The patient split does not measure what it says on two of ten tasks

**Figure** `figures/deck/fig02_replicate_leak.png` (per-slide with/without partner, IDC and READ, three encoders; IDC's share-of-gap annotated).

**Bullets**
- COAD: three distinct patients carry one `patient` label; the shipped fold holds out all three and trains on the fourth sample alone. Gap 0.317, largest of ten; others 0.050 to 0.193
- IDC: two 10x samples are probably two sections of one tumour, labelled as two patients; each is in the other's training set
- Measured with everything else fixed: a same-tumour section in training is worth +0.065 on IDC (6/6 cells), 54% of IDC's whole random-minus-patient gap; +0.090 on READ (12/12), where the folds happen to group the pairs correctly
- GitHub: COAD's labels are known (issue #133, splits deliberately left as is). The IDC pair, its measured cost, and everything on slides 5, 6 and A1 are not reported there as far as the tracker shows

**Notes**
Start with what the patient split is for: score generalisation to a patient the model has never seen. Two label faults, opposite directions. COAD first. HEST's `patient` column says three of four samples are one patient. Same rows' `subseries` strings say Sample P5, Sample P2, Sample P1. HEST's own issue #133 confirms the labels were wrong, corrected in v1.3.0, benchmark splits left unchanged on the reasoning that no patient spans train and test. True, but the consequence is a fold that trains on one donor and tests on three. Its random-minus-patient gap is 0.317, far above every other task. Not a fact about colorectal tissue; a fact about the fold.

IDC goes the other way. TENX95 and TENX99 come from 10x's demo datasets. The page for one states donorCount 1 and labels them Replicate 1 and Replicate 2. They carry byte-identical 541-entry gene panels, the only such pair in the task. When an encoder misclassifies a spot from one, 96% of the time it lands on the other. Not fully secured, since HEST attributes them to two different 10x pages and the second page rate-limited every fetch; stated as probable.

The measurement doesn't depend on the label. Design: hold out TENX99. Draw two training sets of identical size, one from TENX95 plus the NCBI slides, one from the NCBI slides only. Same test spots, same size, same pipeline, same metric. Only difference is whether the partner is in the pool. Partner is worth +0.065 Pearson within slide, positive in all six encoder-slide cells. IDC's whole random-minus-patient gap is 0.121, so more than half of what the split scores as cross-patient generalisation is recoverable from another section of the same tumour. Repeated on READ, whose pairs are replicate sections of the same specimen: +0.090, twelve of twelve. READ's folds group the pairs, so no leak is realised there; it's the counterfactual value of a replicate and a second estimate of the same quantity.

Why it matters for us: the sampling unit that carries shared information is the tumour section, not the spot and not even the slide. Comes back on slides 11 and 12.

Sources: `results/round2/R5b_audit/donor_audit.csv`, `r5b_coad_subseries_confirmation.csv`, `results/round2/R5c_leak/r5c_leak_summary.csv`, `results/round2/R3_splits/r3_per_task_terms.csv`, `docs/hest_bench_issue_draft.md` (unsent).

---

## Slide 5. Issue 2. Split design outweighs encoder choice

**Figure** `figures/deck/fig03_split_staircase.png` (five additive steps random → patient, mean over three encoders and ten tasks; encoder spread as a reference bar; inset: buffered vs unbuffered accuracy by grid size).

**Bullets**
- Between-encoder spread on the benchmark's own protocol: 0.098 (H-Optimus-1 0.423 to ResNet50 0.325)
- Ignoring slide boundaries when splitting is worth 0.159, 1.6× that spread
- Decomposed by nested designs: training size 0.013; spatial adjacency 0.033 plus 0.012 that only a buffer removes; slide-and-patient identity 0.102
- On tasks with several slides per patient: novel slide 0.015, novel patient 0.136
- Two methodological pieces: pooled Pearson over a multi-patient test set is inflated by +0.19; unbuffered spatial blocks give a result that depends on block size

**Notes**
Same head, same metric, same data. Vary only the split. Random spot split against the shipped patient split costs 0.159 within-slide Pearson. Entire spread across twelve foundation models is 0.098. So which slides the test set may contain moves the number more than which encoder supplies the features.

Decomposed with a chain of designs, each removing one more kind of shared information; steps sum exactly to the total. Random versus random-with-matched-training-size: 0.013, pure sample size. Random versus spatially blocked at matched size: 0.033, adjacency; neighbouring spots share tissue and, on Visium, leak transcripts. Blocked versus blocked-with-buffer: another 0.012 that leaks across block edges. Buffered versus patient: 0.102, slide and patient identity together. On PRAD, COAD and READ, where a patient has several slides, that last step splits: new slide with the patient's other slides in training costs 0.015; losing the patient entirely costs 0.136. Order of magnitude apart.

Two things learned about measurement on the way. First, Pearson computed over a pooled multi-patient test set carries between-patient variance in its denominator; measured inflation is exactly zero for single-patient test sets and +0.19 for nine-patient ones. So all of this uses within-slide Pearson, which is what the shipped folds already compute. Second, a blocked spatial split without a buffer leaks across block edges, and finer grids have more edge; accuracy rose monotonically with grid fineness, spread 0.028 across three grid sizes, almost the size of the adjacency term itself. With a 2.5-pitch buffer the spread is 0.010 and flat. Reusable for any spatial cross-validation.

First version of this analysis reported a leakage gap of 0.31; half was the pooled-Pearson artefact; retracted and rebuilt. Second version conflated slide and patient; rebuilt with the leave-one-slide-out arm. What's shown is the third.

Sources: `results/round2/R3_splits/r3_decomposition_terms.csv`, `r3_per_task_terms.csv`, `buffer_diagnostics__*.csv`; `results/summary/results_encoder.csv`.

---

## Slide 6. Issue 3. Table A13 ranks encoders by embedding width

**Figure** `figures/deck/fig04_raw_head_width.png` (rank on PCA-ridge vs rank on raw-ridge, points labelled by encoder and coloured by width; H-Optimus-1 highlighted).

**Bullets**
- Ridge penalty is $\alpha = 100/(d \cdot n_{\text{genes}})$; at $d = 256$ on standardised PCA features that is 0.008, indistinguishable from unpenalised least squares
- On raw embeddings the Gram matrix has condition number $3.0 \times 10^{15}$; the same $\alpha$ leaves the solve effectively singular
- Spearman(width, score): −0.95 on raw ridge, +0.73 on PCA ridge. Every encoder ≥1536 dims ranks 7–12 raw; every encoder ≤1024 ranks 1–6; 512-dim CONCH v1 wins
- H-Optimus-1: rank 1 on PCA ridge, rank 7 on raw ridge, exactly where 1536 dimensions puts it

**Notes**
Started as a discrepancy. ResNet50's raw-embedding ridge cell reproduced 0.03 low. Hypothesis: a penalty confound. Twelve-point penalty sweep at both feature widths with Gram condition numbers recorded. Result killed the hypothesis: at the benchmark's $\alpha$ the fit is OLS to solver tolerance, five orders of magnitude below where the penalty starts to matter. Replacement explanation: on raw embeddings the system is numerically singular and the answer depends on the linear algebra library, which is why that one cell moves and no other does.

Consequence for Table A13, the paper's raw-embedding ridge comparison: it ranks encoders by dimension. Spearman between embedding width and score is −0.95 there, +0.73 once width is equalised at 256 by PCA. No exceptions across twelve encoders. Falsification test: H-Optimus-1 is the strongest encoder in the set, rank 1 on PCA ridge; if the explanation is right it should rank mid-table on raw ridge. Rank 7.

Practical reading: Table A13 shouldn't be cited as an encoder comparison. Not in the issue tracker.

Sources: `results/tailored/regularization/alpha_sweep.csv`, `results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv`, `r8_width_correlations.csv`.

---

## Slide 7. Where the field is

**Bullets**
- Accuracy has a low ceiling: HEST 0.42, STFlow (ICML 2025, spatial context via flow matching) 0.415; HESCAPE (2025) finds contrastive image–expression pretraining *degrades* expression prediction; no clean scaling laws for single-cell foundation models (Nat Methods 2026)
- Embeddings are dominated by nuisance variation: institution recoverable from UNI2/Virchow2 at ~100% (GLMP, this group; Kömen et al.; de Jong et al.); stain normalisation does not fix it
- Predicted expression is used as if measured: super-resolution, biomarker maps, virtual ST on H&E-only cohorts
- Only two preprints (June 2026, Jan 2026) apply valid-inference machinery to ST, both narrow; TISSUE (Nat Methods 2024) gives conformal intervals for scRNA-reference imputation, not for histology prediction

**Notes**
Where the literature stands, in four lines. First, pushing Pearson is crowded and low-yield; dozens of histology-to-expression architectures since 2024, ceiling around 0.42, and the most recent evidence says the next obvious step (contrastive pretraining) makes direct prediction worse. Second, our own group's paper and two others show pathology foundation-model embeddings encode which hospital a slide came from more strongly than biology; our probes on slides 10 and A2 are the same finding from inside HEST. Third, the outputs of these models get consumed downstream as if they were measurements. Fourth, almost nobody has asked how wrong a given prediction is, or how to make inference on predicted expression valid. Two 2026 preprints, one on differential expression after imputation, one on segmentation bias via prediction-powered inference. Neither handles the dependence structure we just measured.

So the open problem is not accuracy; it is trust. Calibrated uncertainty, and valid inference when predictions replace measurements.

---

## Slide 8. Two candidate directions (exploratory)

**Bullets**
- **Topic A. Calibrated uncertainty for histology-to-expression prediction under cohort shift.** Per-spot, per-gene intervals with guaranteed coverage; characterise and repair coverage failure when the test slide, session or donor is new. Tools: split conformal, CQR, weighted conformal with an estimated density ratio; a negative-binomial head as model-based comparator
- **Topic B. Valid inference for population quantities using predicted expression.** Confidence intervals for a morphology–expression relationship on H&E-only slides, using a small set with measured expression. Tools: prediction-powered inference with cluster-robust variance; semi-synthetic validation by masking measured slides
- Both biology-light; both run on HEST-1k; both connect to the semi-supervised inference literature (PPI, DML, SynSurr)
- These are exploratory. The replication was instrumented to test whether they hold up on the data. Everything from here is what that instrumentation found

**Notes**
Two directions that follow from the gap. A asks: how wrong is this prediction, and does the answer survive a new cohort. B asks: if predictions stand in for measurements in a population estimate, how do we get a valid interval. Both are statistics questions; the biology is a wrapper. Both fit what I've been reading in journal club.

Framing to be explicit about: I don't yet know what you have in mind for the project, so treat these as a proposal, and treat the rest of the talk as evidence about whether they're worth pursuing rather than as commitments. The replication was set up so its byproducts answer three questions the topics need answered: is the base predictor sound enough to calibrate, what kind of shift actually exists on this data, and what is the unit of inference. Slides 9, 10, 11 in that order.

---

## Slide 9. Result 1. The benchmark head has no intercept, and the $R^2$ ladder

**Figure** `figures/deck/fig05_r2_ladder.png` (four rungs of fold-median $R^2$, pooled and per task; inset: $\rho/r$ by encoder, ordered).

**Bullets**
- Head is `Ridge(fit_intercept=False)` on centred PCA features: predictions have mean ≈ 0 while $\log(1+y)$ has mean ≈ 0.6. Pearson is shift-invariant, so the benchmark never noticed; $R^2$ is not
- Decomposition on stored columns, no refitting: $R^2 = 2r\rho - \rho^2 - b^2/s_y^2$, with $b$ level offset, $\rho = s_{\hat y}/s_y$, $r$ Pearson
- Fold-median $R^2$: −0.95 as shipped → −0.16 with a training-mean intercept → +0.03 with the test slide's own mean (oracle) → +0.10 with optimal scale, which equals $r^2$, the ceiling
- Predictions spread 1.84× more than optimal ($\rho/r$); ratio orders with encoder quality, 2.17 (ResNet50) to 1.65 (UNI2-h)

**Notes**
Why this comes first: Topic A works with residuals, interval widths, scoring rules, all on the absolute scale. Pearson is not. So before calibrating anything, ask whether the base predictor is even located correctly.

Found by reading the trainer: no intercept, on features that PCA centres by construction. Fitted predictions have training mean zero. Targets are non-negative with mean around 0.6. The benchmark stores per-fold $R^2$ and it is negative in 28 of 29 folds, median −0.95. Pearson unchanged, because it centres both series internally.

Then decomposed. Identity: $R^2 = 2r\rho - \rho^2 - b^2/s_y^2$. Three things you can get wrong, level, scale, pattern. Climb the ladder by fixing one at a time. Add a training-mean intercept: −0.95 to −0.16, recovers 0.80. Replace with the test slide's own mean, which uses test labels so it's diagnostic only: to +0.03, another 0.19, which is a slide-level mean shift that no training-mean intercept can track. Rescale optimally: to +0.10, which is exactly $r^2$, the most any level-and-scale recalibration can ever reach. So the deficit is two-thirds level, then slide shift, then scale, against a ceiling set by the pattern correlation.

The scale term has a direct reading. Best prediction under $r < 1$ shrinks toward the mean by factor $r$. Ours has $\rho = 0.58$ against $r = 0.32$: spreads 1.84× too much. Ratio is worst for the weakest encoder and best for the strongest. That's the concrete target for a calibration layer.

Head refit with intercept in float64 exact arithmetic; three-head identity holds to $10^{-13}$; Pearson unchanged to $10^{-13}$; that head is what Topic A builds on.

Sources: `results/round2/R1b_heads/r1b_ladder_by_task.csv`, `r1b_ladder_by_encoder.csv`, `acceptance__*__f64.csv`.

---

## Slide 10. Result 2. Encoders carry a slide-and-session signature that is in the features and not in the expression

**Figure** `figures/deck/fig06_session_signature.png` (left: probe accuracies within PRAD patient 2, slide and session, with chance lines; middle: accuracy lost to morphology adjustment, PRAD vs cross-patient tasks; right: expression variance components within patient 2 with session as top level).

**Bullets**
- PRAD patient 2: 15 slides, pixel size 0.341–0.349 µm/px (1.02× spread), two clusters 0.0066 apart with contiguous IDs ≈ two scan sessions
- Slide identity from frozen embeddings, spatial-block CV: 0.87–0.95 (chance 0.07). Session: 0.97–0.99. 94% of slide errors stay within session
- Regressing eight nuclear-morphology covariates out of the features removes 1.4% of it (17–27% on cross-patient tasks)
- PRAD patient 1 (8 slides, pixel sizes differing 20%): resolution class at chance. What is encoded is session and slide, not the pixel-size number
- Expression variance with session as top level: between-session ≈ 0 (28/50 genes at or below zero). The signature separates images at 0.98 and contributes nothing to targets

**Notes**
Topic A's premise is covariate shift: the features move between cohorts, the tissue-to-expression relationship doesn't. Wanted to measure that rather than assume it.

Round 1 found slides separable in embedding space at 0.98, but every pair of benchmark slides differs in patient, tissue, resolution and technical conditions at once, so that said nothing about mechanism. PRAD patient 2 is the one place where patient and tissue are fixed while slide varies: fifteen slides, one prostate. Inside those fifteen, pixel-size estimates form two tight clusters 0.0066 µm/px apart with contiguous sample IDs, which is what two scanning runs look like.

Probe design: logistic regression on PCA-256 features; target is the slide label; within each slide, hold out contiguous spatial blocks so a held-out patch's neighbours aren't in training and the classifier can't match local tissue. Slide decodable at 0.87 to 0.95 against chance 0.07. Session, two classes, leave-one-slide-out: 0.98. And 94% of the slide probe's errors land on another slide from the same session; the session axis is the easy one.

Is it tissue composition? Regress each feature on eight morphology covariates (nuclear count, area, class fractions), fit on training spots, probe the residuals. Within one patient the signature drops 1.4%. On tasks whose slides are different patients it drops 17 to 27%, which is the composition difference between patients you'd expect. So within patient it's not composition.

Is it resolution? The other PRAD patient has eight slides spanning a 20% pixel-size difference. Resolution class isn't decodable at all, 0.49 to 0.51. A first version of that probe reported 0.7 and was withdrawn when writing out class sizes showed 5:2 and a constant majority-class predictor scores 0.71. So the encoder reads session and slide; nominal resolution is a proxy for session, not the thing encoded.

Then the other side. Decompose expression within patient 2 with session as the top level. Between-session variance component is at or below zero for 28 of 50 genes. The thing that separates the two sessions at 0.98 in the images contributes no measurable variance to the measured expression. That is covariate shift, measured: $p(z)$ moves, $p(y \mid z)$ doesn't, at least through this channel. It's the case reweighted conformal is designed for, and the slide-and-session probe is the density-ratio estimator it needs. Also identifies the hard case: a test session with no calibration support, which is exactly PRAD's fold structure.

Benchmark-level context: scan resolution varies five-fold across the 72 samples and is aligned exactly with patient identity in PRAD and SKCM, so a patient fold there is a session fold too.

Sources: `results/round2/R4_probes/r4_probes_v2.csv`, `probe1_confusion__*.csv`, `results/round2/R6_variance/r6_prad_session_variance.csv`, `results/round2/R0_resolution/resolution_by_task.csv`.

---

## Slide 11. Result 3. The Topic B estimand is a slide-level quantity, and the unit of inference is the donor

**Figure** `figures/deck/fig07_theta_and_variance.png` (left: $\theta_1$ per IDC slide with bootstrap intervals; right: variance fractions per task on audited donor labels, between-donor / between-slide-within-donor / within-slide, with df annotated).

**Bullets**
- HEST's biomarker example, nuclear area vs GATA3, $r = 0.47$ on one slide: reproduces at 0.42 there, and is 0.15, 0.01, −0.06 on the other three IDC slides (all four under the current morphology build; round 1's build gives 0.46 on the first slide, which is the figure this line previously carried)
- Nested variance decomposition of expression on audited donor labels (moment estimator validated on simulation): between-donor 0.39 on CCRCC (24 donors), 0.34 on LYMPH_IDC; pooled 0.38 on the tasks with enough donors; within-slide 0.6–0.9 everywhere
- New slide with the donor's other slides in training: 0.015. New donor: 0.136
- Per gene, within task: split penalty tracks replicate gain (+0.38); between-slide variance tracks novel-slide cost (+0.21); between-donor variance does not track split penalty (+0.04, n.s.)

**Notes**
Topic B needs an estimand and a unit. Estimand candidate: HEST's own Figure 3, correlation of nuclear area with GATA3 expression, 0.47 on one Xenium breast slide, reported with $p < 10^{-4}$ and no accounting for spatial dependence or the fact that it's one slide. Rebuilt the morphology features from HEST's shipped segmentation with per-sample patch calibration, gated on reproducing that figure; it reproduces. Then computed on the other three IDC slides: 0.15, 0.01, −0.06. Same tissue type, same platform. The estimand is a slide-level quantity with large between-slide variance. That is the Topic B premise in one row of numbers.

The unit. Audited every sample's donor identity against sources outside HEST's metadata: 58 verified, 9 unverifiable, 5 contradicted. On the corrected labels, a nested decomposition of expression: spot within slide within donor. Estimator checked on simulation first. CCRCC has 24 donors, one slide each; between-donor fraction 0.39. LYMPH_IDC 0.34. Pooled over the well-powered tasks 0.38. Spot-level variance dominates everywhere, but a third of the variance sits at the donor level, and spot-level standard errors would ignore it entirely.

Which level carries the cost: from slide 5, a new slide with the donor's other slides in training costs 0.015; a new donor costs 0.136. So the effective sample size for any claim about new patients is the number of donors, and Topic B's variance has to be clustered there.

Per-gene results close the loop. Genes that lose most under a patient split are the genes a same-tumour section recovers most, +0.38. Genes whose level varies most between sections of one tumour lose most when the section is new, +0.21. Genes whose level differs most between donors are not the ones that lose most under a patient split, +0.04, not significant. Reading for Topic A: if the split penalty were donor biology, a per-donor random intercept would absorb it; it wouldn't. The penalty is slide-level shared state, technical and biological together. So the fix has to act on the features (slide 10's reweighting) and on slide-level offsets (slide 9's shift term), not through a donor effect alone.

Sources: `results/round2/R6_variance/r6_theta_build_comparison.csv`, `r6_variance_by_task.csv`, `r6_pooled_between_donor.csv`, `results/round2/R5b_audit/donor_audit.csv`, `results/round2/R7_pergene/r7_correlations_task_centred.csv`.

---

## Slide 12. Proposed next steps

**Bullets**
- Topic A, first experiment: split conformal and CQR on the float64 intercept head; calibrate on training donors; evaluate coverage and width under three fold designs (random spot, shipped patient, audited donor) with and without session reweighting; report beside the benchmark's Pearson table for all 12 encoders. Negative-binomial head as the model-based comparator
- Topic B, first result: $\theta_1$ per slide with donor-clustered PPI intervals against spot-level ones; validation by masking measured slides and checking coverage
- Institution axis: none exists in HEST-bench; needs full HEST-1k breast (Visium across labs) or brain if wanted
- Benchmark findings: draft issue written, not sent; decide whether it becomes an issue, a note, or the first section of a paper
- Standing rules that produced most of this: enumerate everything that differs between two arms before naming a term; audit a grouping variable against an outside source before using it for inference

**Notes**
What the replication leaves us with. For A: a correctly located predictor, per-spot residuals for twelve encoders, audited donor labels, session and resolution covariates on every row, a density-ratio estimator, and the shift mechanisms measured in order of size. The first experiment is fully specifiable: the result that would make it a paper is the pattern of coverage failure across the three fold designs and its repair. For B: morphology features, two estimands with their between-slide and between-donor variance measured, and the replicate-leak design as the validation harness. First result is half done.

Two things the replication changed. The shift axis is session, slide and donor novelty, not institution; the one contrast that looked like institution was two 10x samples at different resolutions, possibly one donor. And the unit is the donor with sections nested inside, and labels have to be audited before use.

Two things I'd like your read on, in whatever order suits: whether either topic matches what you have in mind, and what to do with the benchmark findings.

---

## Slide A1 (backup). Other benchmark properties found

**Bullets**
- Gene panels differ between samples within a task (PAAD: 159 genes common of 919; IDC: one sample measures 41 genes the others don't); leakage-free target selection is not well defined
- Target genes were selected on all spots including test folds; training-only selection changes the list by half and Pearson by +0.009 mean, up to +0.044; ranking itself has Spearman 0.51 with the all-spot ranking
- Xenium tasks' target lists are pairwise disjoint (14 genes common across all 15 Xenium samples); across-task transfer is blocked
- Scan resolution spans 0.137–0.688 µm/px across the 72 samples; aligned exactly with patient in PRAD and SKCM; 31 of 72 have no independent corroboration
- Per-gene Pearson under the benchmark's iterative solver carries ~$10^{-3}$ solver noise, up to $3 \times 10^{-3}$ for four encoders; predictions differ from the exact ridge solution by up to 0.35
- READ's two pairs are replicate sections of one specimen; folds group them correctly

**Notes**
Panels: Xenium panels are per-study; within PAAD three samples share 159 of 919 genes. Shipped targets sit on the intersection, so selection used the test slide's panel. Selecting from training only names genes the test slide can't measure; those were dropped and counted. Selection sensitivity: reimplemented the benchmark's selection and reproduced all ten lists exactly first; then per-fold training-only selection; 27 of 50 genes shared on average, 11 on PRAD; measured gap +0.009 with large task variation, mostly attributable to which genes rather than the ranking peeking. Fixed-list rank comparison isolates the latter: 0.51. Disjoint lists: no cross-task model can use the benchmark's own targets. Resolution: five-fold spread; patient folds in three tasks are resolution folds; mechanism per slide 10 is session not pixel size. Solver: per-gene values shouldn't be quoted past three decimals; task means fine. READ: label understates; pairs are same specimen. Sources: `results/round2/R2_fold_hvg/r2_panel_heterogeneity.csv`, `r2_leakage_summary.csv`, `r2_rank_supplement.csv`; `results/round2/R0_resolution/resolution_by_task.csv`; `results/round2/R1b_heads/r1b_solver_sensitivity.csv`; `results/round2/R5b_audit/donor_audit.csv`.

---

## Slide A2 (backup). Other results

**Bullets**
- Negative binomial without zero inflation is the observation model: NB beats Poisson on 478/488 gene-task pairs, ZINB beats NB on 28/488 by the stored convergence flags, median $\Delta\text{AIC} = -2.0019$ (exactly the one-parameter penalty); every gene overdispersed (min Fano 1.6); zero fraction 0.29 Xenium vs 0.61 Visium
- Buffered spatial-block CV makes the adjacency term well defined (grid-size spread 0.028 → 0.010)
- Float64 exact-solver head: three-head identity (no intercept, intercept, centred target) holds to $10^{-13}$; float32 faithful head violates it by up to 0.35 through solver tolerance
- Slide identity remains decodable at 0.98 under spatial-block CV on every task; composition explains 17–27% on cross-patient tasks, 1.4% within patient
- IDC same-donor pair: 96% of one TENX slide's misclassified spots land on the other (chance 33%)
- COAD's shipped fold is a three-donor holdout trained on one; its 0.317 gap is a fold property, not tissue
- $\theta_1$ per-slide values are robust to the morphology build (rank order identical across two builds; between-slide spread 0.49 vs 0.51)

**Notes**
NB/ZINB: prediction written before fitting that ZINB's AIC gain equals exactly −2 if zero inflation is unnecessary; observed −2.0019; diverged NB fits flagged as converged by the library were caught and excluded, otherwise they'd have reversed the conclusion. The bullet now quotes 28/488, which is what `count_diagnostics.csv` supports through its stored convergence flags; round 1 reported 14/474 after that exclusion, but the exclusion rule is not a column in the table and cannot be re-derived from it, so the smaller figure should not be quoted until whoever holds the criterion restates it. Buffer: without it a blocked-split result is partly a statement about block size. Float64: identity checks failed in float32 at a level matching $\sqrt{n}\,\varepsilon$ accumulation; passed by six orders in float64; that head is Topic A's base. Slide probe: round-1 result, now interpreted via slide 10. IDC confusion: embedding-side corroboration of the same-donor finding, from a run that already existed. COAD: v4 decomposition independently confirms the label fault, novel-slide term 0.11 sd from zero while patient term is 0.26. $\theta_1$ builds: acceptance value restated against the current build; the finding survives. Sources: `results/tailored/counts/count_diagnostics.csv`; `results/round2/R3_splits/buffer_diagnostics__*.csv`; `results/round2/R1b_heads/acceptance__*__f64.csv`; `results/tailored/site_probes/spatial_block_probe.csv`; `results/round2/R5c_leak/r5d_idc_partner_confusion.csv`; `results/round2/R3_splits/r3_per_task_terms.csv`; `results/round2/R6_variance/r6_theta_build_comparison.csv`.

## Changelog

- 21 September 2026: the nuclear-area/GATA3 line mixed two morphology builds -- its headline 0.46 came from round 1's build while the other three values came from the current one. Corrected to the current build throughout, with round 1's figure kept as a labelled comparison rather than deleted. Found by code/scripts/check_outline_currency.py, which the numeric sweep cannot catch because both builds are on disk and a stale quotation matches a stale file.
