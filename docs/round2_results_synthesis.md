# What the HEST-1k replication found, and where Topics A and B stand

19 September 2026, final version. Synthesis of every result outside the faithful replication stage, from rounds 1 and 2 of `NicWYZ/HEST-1k-replication`, ranked by significance. Written for the Monday progress presentation and as the record of where the project stands before Topic A begins.

The repository is frozen at commit `3161a61`, tagged `round2-final`. Every number below was checked against the file it cites by a verification script that is now a required step before any document leaves the project (296 claims verified, 0 unresolved). The sweep's own first finding was that fifteen evidence files the reports cited had existed only as session artifacts and were never committed; they are in the repository now, so anyone cloning it can open the evidence behind each claim.

The faithful replication itself is not covered here beyond one sentence. Twelve encoders, four heads, 0 of 108 per-task cells outside the acceptance threshold against the live leaderboard, exact agreement on ResNet50 and H-Optimus-1. The pipeline is the benchmark's pipeline, and every result below rests on that.

---

## The results, ranked

### 1. The patient split does not measure what the benchmark says it measures

**What was found.** HEST-bench's patient-stratified folds are meant to score generalisation to an unseen patient. On at least two of ten tasks they do not, and the amount by which they do not was measured.

COAD's metadata labels three of its four samples as one patient. The subseries strings in the same rows read "Sample P5", "Sample P2", "Sample P1", and HEST's own issue tracker (#133) confirms the labels were wrong and were corrected in v1.3.0 while the benchmark splits were deliberately left alone. The consequence is that COAD's shipped `test_0` holds out three donors and trains on one. Its random-minus-patient gap is 0.317, the largest of the ten tasks, against 0.050 to 0.193 for the other nine. That number is a three-donor holdout, not a fact about colorectal tissue.

IDC's two TENX samples are probably two sections of one tumour. The 10x page for one of them states `donorCount: 1` and presents "Replicate 1" and "Replicate 2"; the two carry byte-identical gene panels, the only such pair in the task; and when an encoder misclassifies a spot from one, it lands on the other 96% of the time. Against that, their spot counts differ two-fold, which two sections of one imaged area should not show. The attribution stays unresolved at the end of the round, because HEST's metadata associates the two samples with two different 10x product pages and the second page returned a rate-limit error on every fetch. What does not depend on the label is the measurement. Holding the test slide and the training size fixed and varying only whether the partner TENX slide is in the training pool, the partner is worth $+0.065$ within-slide Pearson, positive in 6 of 6 encoder-slide cells, which is 54% of IDC's entire random-minus-patient gap. Two of IDC's four shipped folds have the partner in training.

READ's two pairs are replicate sections of the same specimens. Its folds group the pairs correctly, so no leak is realised in the shipped split. But the same controlled design gives the counterfactual value of a replicate at $+0.090$, positive in 12 of 12 cells, a second independent estimate of the same quantity.

**Why it matters.** For the benchmark, absolute Pearson on COAD and IDC is inflated and the per-task numbers are not comparable across tasks in the way Table 1 presents them. For the project, this is the empirical version of Topic B's premise. The unit that carries shared information is the tumour section, and having another section of the same tumour in training recovers more than half of what a patient split calls generalisation. Any inference that treats spots, or even slides, as the sampling unit will understate its uncertainty by that much.

**How it was obtained.** The first sign was in round 1, where COAD's blocked-minus-patient term (0.29) was three times any other task's and its fold-to-fold dispersion was implausibly tight. The review read that as same-patient leakage, which was the right mechanism and the wrong direction. In round 2 the split decomposition was redesigned with a leave-one-slide-out arm for multi-slide patients, and COAD's novel-slide term came out at 0.11 of its own standard deviation while its patient term stayed at 0.26, which is the signature of a holdout that removes several donors at once. That prompted a metadata check, which found the subseries strings. A provenance audit of all 72 samples followed, reading each sample's 10x or GEO source rather than HEST's `patient` field. It found IDC, corrected three of its own verdicts when the assumed source pages turned out not to be the ones HEST cites, and produced a `donor_id` column that every later stage uses in place of `patient`.

The replicate-leak design went through one wrong version. The first attempt held out both TENX slides together, which removed 80% of the training spots, so the drop it measured was mostly training size. A size-matched variant silently dropped the fold that mattered. The version that stands draws two equal-size training sets, one with the partner and one without, for the same test slide, so nothing but the partner's presence differs.

### 2. Which slides the test set may contain matters more than which encoder supplies the features

**What was found.** Under the benchmark's own head and metric, ignoring slide boundaries when splitting is worth $0.159$ within-slide Pearson, 1.6 times the entire spread between the best and worst of twelve foundation models ($0.098$). That total decomposes, by a chain of designs where each step removes one more kind of shared information, into training-set size ($0.013$), spatial adjacency within a slide ($0.033$, plus $0.012$ that only a buffer around held-out blocks removes), and slide-plus-patient identity ($0.102$). On the tasks where a patient contributes several slides, the last term splits again into novel slide ($0.015$) and patient identity ($0.136$), an order of magnitude apart. PRAD is the only task where the novel-slide term is resolved from zero, at $0.028$ with a standard deviation of $0.002$.

Two supporting results. Pooled Pearson computed over a multi-patient test set is inflated by between-patient variance in its denominator: measured at exactly zero for single-patient test sets and $+0.19$ for nine-patient ones. And a blocked spatial split without a buffer gives a result that depends on the block size chosen (spread $0.028$ across three grid sizes); with a buffer of 2.5 spot pitches the spread is $0.010$ and the adjacency term becomes a well-defined quantity.

**Why it matters.** The benchmark's ranking of encoders is a small effect sitting on top of a large split-design effect. Anyone reporting a number on this data has to say which design produced it, and a random spot split, which several published methods use, is not comparable to the shipped one. The buffered block design and the within-slide metric are reusable pieces of methodology for any spatial cross-validation. For Topic A, the decomposition names the shift mechanisms a calibration method has to survive, in order of size.

**How it was obtained.** The first version reported a leakage gap of $0.31$. Half of that was the pooled-Pearson artefact; a variance decomposition of Pearson into between- and within-patient components showed why, and the metric was fixed to within-slide before anything else was reported. The second version had three designs (random, blocked, patient) and a two-gap decomposition. The review pointed out that blocked-minus-patient conflated slide and patient, that the arms differed in training size, and that block edges leak. The third version added size matching, a buffered arm, a leave-one-slide-out arm and a grid sweep, and reproduced the earlier version's shared arms to four decimals before any new term was read. The pooled term was withdrawn in favour of per-task terms once COAD's label fault showed the same term does not mean the same thing in every task.

### 3. Pathology encoders carry a scan-session and slide signature that has nothing to do with tissue, and that signature is in the features but not in the expression

**What was found.** Within one PRAD patient, across fifteen slides whose nominal pixel sizes differ by 2%, a linear probe on frozen embeddings identifies which slide a patch came from at 0.87 to 0.95 balanced accuracy (chance 0.07), under a spatial block split that removes local neighbours. The fifteen slides fall into two clusters by pixel size, 0.0066 µm/px apart with contiguous sample IDs, consistent with two scanning sessions; session is decodable at 0.98, and 94% of the probe's errors fall within a session. Regressing eight nuclear-morphology covariates out of the features removes 1.4% of the signature. On tasks whose slides come from different patients, the same adjustment removes 17% to 27%, which is the composition difference one expects between patients.

Two further results sharpen this. Within the other PRAD patient, whose eight slides differ in nominal pixel size by 20%, the pixel-size class is not decodable at all (0.49 to 0.51, chance 0.5). So what the encoder reads is the session and the slide, not the resolution number. And when the expression itself is decomposed with session as the top level, the between-session variance is zero for 28 of 50 genes and negligible for the rest. The session signature that separates the two clusters at 0.98 in the features contributes no measurable variance to the targets.

The benchmark-level fact that motivated this line is that scan resolution varies five-fold across the 72 samples (0.137 to 0.688 µm/px), is aligned exactly with patient identity in PRAD and SKCM and partly in PAAD, and has no independent corroboration for 31 of the 72 samples. In those tasks a patient fold is also a scan-session fold.

**Why it matters.** This is the covariate-shift premise of Topic A stated as a measurement rather than assumed. The features move between slides and sessions; the conditional relationship between tissue and expression does not, at least not through this channel. That is exactly the situation in which reweighting by an estimated density ratio should restore coverage, and the slide-and-session probe built here is the density-ratio estimator. It also identifies the hard case, a test session with no calibration support, which is what PRAD's fold structure creates.

**How it was obtained.** Round 1's slide-identity probe reached 0.98 but could not say whether it was reading tissue, resolution or a technical signature, because every pair of slides in the benchmark differs in all three. The review identified PRAD patient 2 as the one place where patient and resolution are nearly fixed while slide varies, and the sub-cluster structure in the metadata as a session contrast inside that. The resolution probe on patient 1 first reported values near 0.7 and was withdrawn when writing out the class sizes (5 against 2) showed the per-fold statistic equalled a constant majority-class predictor; the pooled version replaced it. The session-in-expression check was run because a directive asked for the opposite caveat, that PRAD's slide variance "contains the session effect," and the data reversed it.

### 4. The benchmark head has no intercept, most of its unexplained variance is level and slide-level shift, and it is over-dispersed by a factor of 1.8

**What was found.** The benchmark's ridge head is fit with `fit_intercept=False` on features that are centred by construction, so its predictions have training mean near zero while $\log(1+\text{count})$ has a positive mean. Pearson is invariant to that and the benchmark never noticed. $R^2$ is not. Decomposing $R^2 = 2r\rho - \rho^2 - b^2/s_y^2$ over 12 encoders, 29 folds and 50 genes, with $b$ the level offset, $\rho$ the ratio of predicted to true spread and $r$ the correlation, the fold-median $R^2$ climbs a ladder of four rungs: $-0.95$ as shipped; $-0.16$ with a training-mean intercept; $+0.03$ with the test slide's own mean (an oracle); $+0.10$ with the optimal scale as well, which equals $r^2$ and is the ceiling no recalibration can pass. So the deficit is two-thirds level, then a slide-level mean shift that no training-mean intercept can track, then scale, against a pattern ceiling of about 0.10.

The scale term has a direct reading. The head's predictions vary 1.84 times more than is optimal given how well they correlate ($\rho / r$), and the ratio orders with encoder quality, from 2.17 for ResNet50 down to 1.65 for UNI2-h.

**Why it matters.** Every quantity Topic A works with (absolute residuals, interval width, CRPS, log score) is on the absolute scale, so the intercept is mandatory before any calibration and was missing. The over-dispersion ratio is the concrete target a calibration layer has to hit. And the slide-level mean shift, worth $+0.185$ of $R^2$ that only the test slide's own mean recovers, is the same slide-level structure that result 1 found from the other side.

**How it was obtained.** The review noticed the `fit_intercept=False` line while reading the trainer for the replication and predicted that the per-fold $R^2$ the benchmark already stores would be negative; it was, in 28 of 29 folds. Three heads were refit (no intercept, intercept, target-centred) and shown algebraically to share one slope vector, so the change is a per-gene constant and Pearson is untouched. The identity checks failed in float32 at a level consistent with accumulation error, and were redone in a float64 exact-solver head, which passed by six orders of magnitude and is the base predictor Topic A will use. The ladder was computed from stored columns without refitting.

### 5. Table A13's encoder ranking is a ranking by embedding width, because the ridge penalty is inert

**What was found.** The benchmark sets $\alpha = 100/(d \times n_{\text{genes}})$, which at $d = 256$ is about 0.008. On standardised PCA features that is indistinguishable from unpenalised least squares (differences below $3 \times 10^{-4}$, five orders of magnitude from where the penalty starts to matter). On raw embeddings the Gram matrix has condition number $7.6 \times 10^{14}$ and the same $\alpha$ leaves the solve effectively singular. The consequence is that the raw-embedding ridge table ranks encoders by dimensionality: Spearman between width and score is $-0.95$ on `raw_ridge` and $+0.73$ on `pca_ridge` (twelve encoders; the eleven-encoder value from round 1 was $-0.954$, and both are now tabulated with their cohort size). Every encoder with 1536 or more dimensions occupies raw-ridge ranks 7 to 12; every encoder with 1024 or fewer occupies ranks 1 to 6; the 512-dimensional CONCH v1 wins. H-Optimus-1, the strongest encoder in the set, is rank 1 on `pca_ridge` and rank 7 on `raw_ridge`, exactly where 1536 dimensions places it.

**Why it matters.** Table A13 should not be cited as an encoder comparison, and anyone in the group using it should know. It is also a clean, self-contained note for the benchmark's authors.

**How it was obtained.** Round 1 found a 0.03 discrepancy on ResNet50's raw-ridge cell and hypothesised a penalty confound. A twelve-point penalty sweep at both feature widths, with Gram condition numbers recorded, eliminated that hypothesis (the penalty is inert) and replaced it with the width explanation. Round 2 ran H-Optimus-1 on the raw ridge head as a falsification test that had not been run: it should rank poorly there if the explanation is right, and it did. The same test on the raw XGBoost head was started and closed unfinished, since the ridge result settles the question and the second head would have cost about 34 CPU-hours to say the same thing.

### 6. Gene panels differ between samples within a task, the target genes were selected on test spots, and the selection protocol moves the answer

**What was found.** In every Xenium task the samples do not share a gene panel. PAAD's three samples have 159 genes in common out of a union of 919; LUNG 259 of 823; IDC 280 real genes in common, with one sample measuring 41 that the others do not. The benchmark's 50 target genes per task were selected from the all-sample intersection using all spots, test folds included. Selecting instead from training samples only changes the target list by roughly half its members (27 of 50 shared on average, 11 on PRAD), changes measured Pearson by $+0.009$ on average and up to $+0.044$ on individual tasks, and on four Xenium tasks names genes the held-out slide cannot measure at all. Holding the gene set fixed and varying only whether the ranking sees test spots, the Spearman rank correlation between the two rankings is 0.51, with 32 of 50 genes moving more than five ranks.

**Why it matters.** Leakage-free target selection is not well defined on this benchmark without knowing the held-out slide's panel, which is itself test-set information. Absolute Pearson carries an unquantifiable selection component. Across-task transfer is blocked outright, since the five Xenium tasks' target lists are disjoint and their panels share 14 genes. For Topic A, the target list is a fixed given and coverage claims are conditional on it.

**How it was obtained.** The shipped selection procedure was reimplemented and shown to reproduce all ten lists exactly, set and order, which was the gate for anything further. The within-fold version then raised a `KeyError` on the first Xenium task because a fold-selected gene was absent from the held-out slide; that error was the finding. The gap was first labelled leakage and then relabelled selection-protocol sensitivity once the arms were enumerated and the gene-set difference between them was found to correlate at 0.76 with the gap; the fixed-list rank comparison was added to isolate the ranking's dependence on test spots from the composition change.

### 7. Negative binomial without zero inflation is the observation model

**What was found.** Per-gene maximum-likelihood fits on the 500 benchmark gene-task pairs: negative binomial beats Poisson on 478 of 488 converged pairs and every gene is overdispersed (minimum Fano factor 1.6). Zero-inflated NB beats NB on 14 of 474, and the median AIC difference is $-2.0019$, which is exactly the one-parameter penalty for a parameter that buys nothing. Sparsity follows the assay (median zero fraction 0.29 on Xenium tasks, 0.61 on Visium), not the tissue.

**Why it matters.** This settles the likelihood for Topic A's model-based head and for any count-level work in Topic B. STFlow's ZINB prior is not supported on these targets.

**How it was obtained.** The prediction that ZINB's AIC gain would equal exactly $-2$ if zero inflation is unnecessary was written down before the fit. Fourteen genes whose NB fits diverged while the library reported convergence were flagged rather than trusted; taken at face value they would have read as strong support for ZINB and reversed the conclusion.

### 8. The Topic B estimand is a slide-level and donor-level quantity, and the variance components say how much

**What was found.** The correlation between nuclear area and GATA3 expression that HEST reports as a biomarker finding ($r = 0.47$ on one slide) reproduces at 0.46 on that slide under the morphology build the check was defined on, and at 0.42 under the current build, which assigns more nuclei per spot; it is 0.15, 0.01 and $-0.06$ on the other three IDC slides under either build, with identical rank order. It is a slide-level quantity with large between-slide variance. A nested variance decomposition of expression on audited donor labels, validated on simulation before use, gives a between-donor fraction of 0.39 on CCRCC (24 donors) and 0.34 on LYMPH_IDC (4), pooled 0.38 on the tasks with enough donors to estimate it; within-slide spot variance dominates everywhere (0.6 to 0.9). Per gene, the genes that lose most under a patient split are the genes a same-donor replicate recovers most (within-task Spearman $+0.38$), and between-slide-within-donor variance predicts the novel-slide cost ($+0.21$); between-donor biological variance does not predict the split penalty within a task ($+0.04$, not significant).

**Why it matters.** For Topic B, the cluster in the cluster-robust variance is the donor, with slides nested inside, and the between-donor fraction is large enough that spot-level standard errors would be wrong by a wide margin. For Topic A, the per-gene result says a donor-level random effect on its own will not absorb the split penalty; the penalty is about slide-level shared state, technical and biological together, which is what the replicate leak measures.

**How it was obtained.** The morphology features were rebuilt from the shipped CellViT segmentation with a per-sample patch-geometry calibration (patch extents span 163 to 818 pixels across samples, so no constant patch size is correct), and gated on reproducing HEST's own figure before use. The variance components used a Henderson moment estimator checked against known values on 40 unbalanced simulations. A pooled estimate that paired CCRCC with PRAD, as directed, came out at 0.12 and was recognised as an artefact of PRAD's two donors giving a truncated zero; the well-powered pairing is the one reported.

### 9. A footnote on precision

Per-gene Pearson under the benchmark's iterative solver carries about $10^{-3}$ of solver noise, up to $3 \times 10^{-3}$ for four encoders, and the faithful head's predictions differ from the exact ridge solution by up to 0.35 in the worst cell. Task-level means are unaffected. Per-gene values should not be quoted past three decimals, and Topic A builds on the exact float64 head.

---

## Where Topics A and B stand

### What exists

For Topic A: a float64 exact-solver head with an intercept on every task and fold, per-spot residuals for all twelve encoders, a `donor_id` column that supersedes the benchmark's patient labels, scan-session and resolution covariates on every prediction row, the slide-and-session probe as a density-ratio estimator, the negative-binomial likelihood as the model-based comparator, and a decomposition of the shift mechanisms in order of size.

For Topic B: per-spot morphology features with calibrated geometry, two candidate estimands ($\theta_1$ the area-expression correlation, $\theta_2$ a difference in means by nuclear class) with their slide-level and donor-level variance measured, and the replicate-leak design as the template for semi-synthetic validation (hold out sections, mask their expression, check coverage against the full-data value).

Both have the same motivation figure, the $R^2$ ladder, and the same benchmark-hygiene section, the list of properties above.

### How the replication changed the approach

Three things are different from the proposal written before the replication.

The shift axis is not institution. HEST-bench contains no clean institution contrast; the one pair that looked like one is two 10x samples at different scan resolutions, possibly from one donor. The shift that exists and is measured is slide and session novelty, with donor novelty on top. Topic A's weighted conformal should target that, using the probe built in R4, and the institution axis needs full HEST-1k (breast across Visium sources; brain across many) if it is wanted at all.

The unit of inference is the donor, with sections nested inside, and labels have to be audited before they are used. The proposal said slide; the data say donor, with novel-slide cost an order of magnitude below patient-identity cost, and two of ten tasks' labels wrong in opposite directions. Topic B's variance is donor-clustered, and any coverage claim in Topic A is stated per fold design with `donor_id` folds as the honest one.

The problem is not level alone. Fixing the intercept recovers most of the $R^2$ deficit, but a slide-level mean shift and a scale error remain, and the per-gene analysis says a donor random effect does not absorb the split penalty. So Topic A needs feature-side shift handling (the reweighting) and target-side recalibration (scale, and possibly a slide-level offset estimated from the test slide's own predictions), not one or the other.

### Are A and B still the right directions

Yes, and the case is stronger than when they were proposed, because the motivation is now measured rather than argued. Two adjustments to sequencing.

The benchmark-hygiene findings (results 1, 5 and 6 above, plus the resolution alignment) are a contribution on their own. Whether they become a short note, an issue to the authors, or the first section of the Topic A paper is a decision for Monday, and it is Nicolas's and David's decision, not the execution session's. The draft issue exists and has not been sent.

Topic A remains the first paper. Its concrete first experiment is now specifiable without further exploration: split conformal and CQR on the float64 head, calibration on training donors, evaluated under three fold designs (random spot, shipped patient, audited `donor_id`), with and without session reweighting, reporting coverage and width per encoder and task alongside the benchmark's own Pearson table. The result that would make it a paper is the pattern of coverage failure across the three designs and its repair.

Topic B follows, using Topic A's predictor and the replicate-leak design as its validation harness. Its first result is already half-written: $\theta_1$ per slide with donor-clustered intervals against spot-level ones.

### How to proceed

Present Monday with the ranked list above and the $R^2$ ladder as the opening figure. Ask for two decisions: what to do with the benchmark findings, and whether to pull full HEST-1k breast and brain for an institution axis. Then open round 3 as Topic A's first experiment.

Round 2 is closed. The one item left open is the IDC same-donor attribution, which needs a single page that 10x has been rate-limiting; it affects one label in the authors' draft and no measurement, and the draft carries a blocking note until it is settled.
