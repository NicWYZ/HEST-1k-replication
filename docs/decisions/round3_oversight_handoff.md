# Handoff to the next oversight session: HEST-1k replication, results to date, and the round 3 plan

22 September 2026. Written by the oversight chat that ran rounds 1 and 2, for the chat session that will run round 3. Repository `NicWYZ/HEST-1k-replication` at tag `round2-docs-clean` (commit `4da6b86`). A companion document, `round3_execution_handoff.md`, carries the same content framed for the Claude Science session that executes the work. Read both, since the execution handoff has the stage specifications in full and this document has the reasoning behind them.

---

## 0. Your role

You are the oversight chat. The project runs as three parties.

- **Nicolas Weiyang Zhang** (Longleaf ONYEN `weiyang`) is the first-year biostatistics PhD student whose project this is. He reads everything, understands every command before it runs, and pushes back on unexplained steps. He carries documents between the two Claude sessions by hand, so every memo you write for Claude Science goes to him in full, ready to paste.
- **The Claude Science session** executes. It has SSH access to UNC Longleaf, submits Slurm jobs, runs the analyses, writes stage reports, and maintains the GitHub repository. It does not make scope decisions.
- **You** supervise. Your standing responsibilities, as Nicolas stated them:
  - supervise the Claude Science session, which means writing its instruction documents and decision memos, and enforcing the gate rules in § 9.5;
  - come up with the methodology and the implementation plan;
  - review its analysis reports critically, checking numbers against files where the local repository is connected, and catching mislabelled terms;
  - consolidate results into presentations in Nicolas's preferred style;
  - update Nicolas on progress and explain concepts, with derivations done slowly;
  - conduct internet and literature research;
  - steer the general direction of the project.

### 0.1 How Nicolas works, and what he has asked for

These are stated preferences, several repeated after a correction, so treat them as fixed.

- Plain, natural writing. No em-dashes. No colon-then-explanation constructions. No compressed or clever phrasing. Math as rendered LaTeX, not code blocks or plain-text notation.
- Speaker notes for a slide cover only what is on the slide and are brief. He said of one slide, "This slide is not worth that much of my supervisor's time." Do not inflate length anywhere.
- When he asks how something works, derive it slowly. He asked for the R² decomposition, the within-patient Pearson derivation, the design effect and effective sample size, all step by step, and each time the first compressed version was not enough.
- In reports, memos and slides, quote numbers at the precision the comparison needs. With this many numbers in hand, what matters when reporting is the relative scale (one effect is 1.6 times another; a term is an order of magnitude smaller), not the fourth decimal. Full precision belongs in computations and in the files, not in prose. He said this after the round 2 write-ups, so earlier documents in the repository do not follow it.
- Do not have Claude Science reconstruct or revise a past working document that has served its purpose (a decision memo that was not saved, the deck outline). Those records stand as they are.
- Decision memos to Claude Science are handed over as complete documents ("Just revise the decision doc and give it to me in full"), not as diffs or summaries.
- He has minimal biology background by design; the project treats expression as a signal to predict, calibrate and use for inference. Do not introduce gene-level biology.
- His career goal is quantitative research in finance. The project was chosen so that its skills (calibration, distribution shift, semi-supervised inference, cluster-robust variance) transfer. Keep that framing when choosing between options.
- He prefers ML venues (NeurIPS, ICML, AISTATS) or top statistics journals over biology journals.

### 0.2 How the Claude Science session works, and what to watch

It is thorough, honest about failures, and finds things. It also over-runs when given an open-ended target with no time cap. The last instruction (bring 437 unresolved numeric claims to zero, no deadline) turned into a full day fixing fifteen bugs in the claim checker. It runs several parallel workers when it can and once lost entries in a shared file to concurrent writes. Two rules follow from that. Put a time cap on any task that is not analysis, and specify one writer per file.

It has repeatedly misread gate rules in the permissive direction. Nicolas corrected this twice in round 2 and the wording in § 9.5 is the one he approved. Restate it in every memo.

Its stage reports are long and well structured, with numbers cited to files. Read the "what was not checked" and "escalations" sections first; that is where the round 2 findings that changed the plan surfaced.

---

## 1. Context

### 1.1 People and goal

Nicolas is in Dr. Hongtu Zhu's group at UNC Gillings. His GRA is supervised by Dr. Daiwei (David) Zhang, first author of iStar (super-resolution ST from histology, Nature Biotechnology 2024) and corresponding author of GLMP (batch-robust histology embeddings through an LLM text bottleneck). The advisors set spatial transcriptomics as the year's focus and said the work must be methodological, not applied. Target is a submittable paper by spring or summer 2027. The first concrete instruction from the advisors was to download HEST-1k and replicate the paper. Everything below grew out of that.

### 1.2 Where things stand on 22 September

Nicolas presented on Monday 21 September but only got through the first half of the deck (title, the benchmark, the faithful replication, and the three benchmark issues). The next presentation starts from the literature-review slide (slide 7) and continues through the two topics, the three results, and the proposed next steps, then adds new results from round 3. The two decisions the deck asked the advisors for (what to do with the benchmark findings, and whether to pull full HEST-1k for an institution axis) are therefore still open. Round 3 proceeds on the default for the first, which is that the authors' draft issue stays unsent. On the second, Nicolas has decided that the project will expand beyond the benchmark subset regardless, since 72 samples cannot carry a methodological project; the expansion is track D in § 9, and the advisors are informed of the selected set rather than asked whether to pull data at all.

Nicolas has decided the project is ready for round 3, which is Topic A's first experiment and Topic B's first result. Round 3 will run in a new chat session and a new Claude Science session; that is why this document exists.

### 1.3 Timeline so far

| dates | what |
|---|---|
| early September | literature review; two topics proposed; project framed as exploratory first-year work |
| 12 Sept | original handoff to Claude Science (`docs/HEST_replication_handoff.md`) |
| 12 to 16 Sept | round 1: faithful replication of the benchmark, instrumentation layer, first tailored analyses |
| 16 Sept | oversight review of round 1 (`docs/HEST_replication_review.md`), round 2 execution plan |
| 16 to 19 Sept | round 2, stages R0 to R8, with report-and-wait gates at R1, R3, R5 and end-of-round at R8 |
| 19 Sept | closeout memo; repository frozen at `round2-final`; results synthesis written |
| 20 to 21 Sept | seven deck figures under committed scripts; repository refresh; deck built and reviewed by Nicolas through artifact comments; tag `round2-final-deck` |
| 21 Sept | numeric-claim gate closed at zero unresolved; tag `round2-docs-clean` |
| 21 Sept | half the deck presented |

---

## 2. Background in one page

Gene expression is a count of mRNA transcripts per gene. Spatial transcriptomics measures it at known positions on a tissue section. Sequencing platforms (Visium, 55 µm spots, whole transcriptome) and imaging platforms (Xenium, subcellular, panels of a few hundred genes) both appear in HEST; HEST pools Xenium transcripts into 55 µm pseudo-Visium spots so both share one format.

An H&E whole-slide image is a gigapixel scan of the stained section. HEST extracts a 224 × 224 patch at 20× centred on each spot. A frozen pathology foundation model (UNI, Virchow, H-Optimus, CONCH, GigaPath and others) maps each patch to an embedding.

The benchmark task, per cancer task, is to predict $\log(1 + \text{count})$ of the 50 most variable genes from the patch embedding, scored by Pearson correlation per gene averaged over genes, under patient-stratified cross-validation folds. The head is `StandardScaler`, then `PCA(256)` fit on training embeddings, then `Ridge(alpha = 100/(256 × 50), fit_intercept=False, solver='lsqr')`. Two things about this head became findings (no intercept; a penalty that does nothing).

Ten tasks in the current benchmark. Five Xenium (IDC, PAAD, SKCM, COAD, LUNG) and five Visium (PRAD, READ, CCRCC, LYMPH_IDC, HCC). 72 samples, 29 shipped folds in total, 50 target genes per task, 500 gene-task pairs.

Statistical properties of the target that matter here. Counts are sparse and overdispersed (negative binomial, as round 1 confirmed), spatially autocorrelated within a slide, and subject to technical variation across slides, scan sessions, labs and platforms. Spots are nested in slides, which are nested in donors.

---

## 3. The literature and the gap

The full landscape is in `docs/literature_landscape.md` (ranked shortlist of eight directions; the two topics below are its #5 and #1). The four points that matter:

1. Accuracy has a low ceiling and the direction is crowded. Best average Pearson on HEST is about 0.42 (H-Optimus-1). STFlow (ICML 2025) reaches 0.415 with spatial context. HESCAPE (2025) found contrastive image-expression pretraining degrades direct expression prediction and blamed batch effects. Dozens of histology-to-expression architectures appeared in 2025 and 2026. Do not compete there.
2. Embeddings are dominated by nuisance variation. GLMP (this group), Kömen et al. (arXiv:2411.05489) and de Jong et al. (arXiv:2501.18055) show a linear probe recovers the source institution from pathology foundation-model embeddings at near-perfect accuracy, and stain normalisation does not fix it.
3. Predicted expression is consumed downstream as if measured (super-resolution, biomarker maps, virtual ST on H&E-only cohorts) with no accounting for error.
4. Only two preprints apply valid-inference machinery to ST. TIDEST (Testa, Lei, Roeder, CMU; bioRxiv June 2026) calibrates differential-expression testing on imputed expression using measured genes. CSDE (Boyeau, Bates, Jordan, Yosef; bioRxiv January 2026) applies prediction-powered inference to segmentation bias. Neither treats the dependence structure (spots in slides in donors). TISSUE (Nature Methods 2024) gives conformal intervals for scRNA-reference imputation, not for the histology map. The general theory is prediction-powered inference (Angelopoulos et al., Science 2023; PPI++; cross-PPI, Zrnic and Candès, PNAS 2024) and post-prediction inference (Wang, McCormick, Leek, PNAS 2020; POP-Inf, JMLR 2025); conformal prediction under covariate shift (Tibshirani, Barber, Candès, Ramdas, NeurIPS 2019) and beyond exchangeability (Barber et al., Annals of Statistics 2023).

The gap, in one sentence. The field has moderately accurate point predictors whose errors depend on slide, session and donor, and their outputs are used as if measured; nobody has characterised per-spot uncertainty under that shift or made inference on the predictions valid under the dependence.

Two literature items round 3 needs that have not been read yet, and that you should look up in the first week. First, conformal prediction with hierarchical or clustered data, where the test point comes from a new group (the references to start from are Dunn, Wasserman and Ramdas on distribution-free prediction sets for two-layer hierarchical models, and Lee, Barber and Tibshirani on distribution-free inference with hierarchical data; verify titles and dates with a search). Second, prediction-powered inference with clustered or dependent data; search for stratified or cluster-robust variants of PPI and for anything that has appeared since June 2026 extending PPI to spatial dependence, since the landscape document flagged that as the pivot trigger.

---

## 4. The two topics, as they stand after the replication

### Topic A. Calibrated uncertainty for histology-to-expression prediction under cohort shift

For each held-out spot $i$ and gene $g$, produce an interval $C_{ig}$ with $\mathbb{P}(y_{ig} \in C_{ig}) \ge 1 - \alpha$, and characterise coverage when the held-out slide, scan session or donor is new. Base predictor is the benchmark's head with an intercept in float64 exact arithmetic (round 2 built this). Tools are split conformal on absolute and scaled residuals, CQR, weighted conformal with a density ratio estimated by a slide-and-session probe on the embeddings, and a negative-binomial head as the model-based comparator. Deliverable is a table like HEST Table 1 with coverage and width per encoder and task under three fold designs, and a finding on where coverage fails and what repairs it.

### Topic B. Valid inference for population quantities using predicted expression

For a scalar estimand $\theta$ defined on expression and an H&E-derived covariate (nuclear morphology from HEST's shipped CellViT segmentation), deliver a confidence interval that is valid regardless of predictor quality and narrower than the labelled-only interval when the predictor is good. Tools are PPI++ with cross-fitting, a donor-clustered variance in place of the i.i.d. one, and semi-synthetic validation by masking measured slides or donors and checking coverage against the full-data value.

### What the replication changed

Three things differ from the proposal written before the replication.

- The shift axis is not institution. HEST-bench has no clean institution contrast; the one pair that looked like one is two 10x samples at different scan resolutions, probably from one donor. The shift that exists and was measured is slide and session novelty, with donor novelty on top. An institution axis needs full HEST-1k (breast across Visium sources; brain across many), which is why track D in § 9 pulls a designed subset of it.
- The unit of inference is the donor, with sections nested inside, and donor labels have to be audited before use. Two of ten tasks had labels wrong in opposite directions.
- The base predictor's problem is not level alone. An intercept recovers most of the $R^2$ deficit, but a slide-level mean shift and a scale error remain, and the per-gene analysis says a donor-level random effect would not absorb the split penalty. Topic A needs feature-side shift handling (reweighting) and target-side recalibration (scale and possibly slide-level offset), not one or the other.

Both topics are stronger than when proposed because their premises are now measured rather than argued. Topic A is the first paper. Topic B follows using Topic A's predictor and the replicate-leak design as its validation harness.

---

## 5. What was done, round by round

### 5.1 Round 1 (12 to 16 September): faithful replication and instrumentation

Stage 0 set up the environment on Longleaf (HEST at commit `3ddb5ea`, TRIDENT v0.3.2 pinned explicitly because it is an unpinned dependency upstream whose transforms change between versions). Stage 1 inventoried `MahmoodLab/hest-bench`. Stage 2 ran the four heads (`pca_ridge`, `raw_ridge`, `raw_xgb`, and `pca_xgb` as Table A14's rejected candidate) for twelve encoders. Stage 3 verified against the paper and the live leaderboard. Stage 4 built the instrumentation layer (joined prediction tables with row identity verified against the AnnData with a permutation control, count diagnostics, site probes, split comparison, morphology features from the CellViT segmentation gated on reproducing HEST's Figure 3e, a held-out-gene check). Stage 5 (STFlow) was set up but not trained and stays deferred.

The faithful result. Over 108 encoder-task cells against the live leaderboard, mean absolute difference 0.0002, 0 of 108 over the 0.03 threshold. ResNet50 reproduces Table 1 exactly (0.3252), which is the informative case since it has no gated weights or transform ambiguity. H-Optimus-1 also matched exactly and was run after the pipeline was frozen. The pipeline is the benchmark's pipeline; every result below rests on that.

Round 1's tailored stage produced four results that survived (pooled-versus-within Pearson, the inert penalty and width-ranked Table A13, negative binomial without zero inflation, the disjointness of Xenium target lists) and three attribution claims that did not survive review (a "slide-level signature" term that conflated slide and patient, an "institution shift" scalar of 0.0419 that was a resolution contrast within one lab, and slide-identity probes labelled as technical without evidence). The review also found, in the repository's own metadata, that scan resolution varies five-fold across the 72 samples and is aligned with patient identity in three tasks.

### 5.2 Round 2 (16 to 19 September): from replication to project motivation

Everything on cached embeddings, no GPU. Stages R0 (resolution columns, relabelling), R1 and R1b (intercept refit, float64 head, $R^2$ ladder, solver sensitivity), R2 (within-fold gene selection), R3 (split decomposition v4), R4 (probes within one patient), R5 (IDC provenance), R5b (donor audit of all 72 samples), R5c (replicate leak generalised to READ), R6 (donor-level estimands and variance components), R7 (per-gene decomposition), R8 (H-Optimus-1 on raw heads). Gates at R1, R3, R5, then one report at R8. Decision memos at each gate are in `/home/claude/outputs/` of the old session and should now be committed under `docs/decisions/` (see § 8.4).

### 5.3 Closeout, deck, and documentation gate (19 to 21 September)

The closeout restated $\theta_1$ against the current morphology build, fixed the pooled between-donor estimate, made one attempt at the IDC attribution (rate-limited, unresolved), wrote the numeric-claim checker and made it a required step, and froze the repository. The deck (twelve main slides, two backup) was built from a master outline with every number generated into `results/summary/deck_numbers.csv` by script. The final instruction closed the documentation gate at zero unresolved claims across nineteen documents, and in doing so found and fixed fifteen defects in the checker, seven small document errors (none changing a conclusion), a bug in the summary-table aggregator, and two result files that three documents cited but that had never been committed.

---

## 6. The results in detail

Each result gives what was found, how it was obtained, what was tried that did not work, why it matters, and how it changed the direction. Numbers are from the README at `round2-docs-clean`, which was checked mechanically against its files. Ranked by significance, as in `docs/round2_results_synthesis.md`.

### 6.1 The patient split does not measure what the benchmark says on two of ten tasks

**What.** HEST-bench's patient-stratified folds are meant to score generalisation to an unseen patient. In COAD, three of four samples share one HEST patient label while the source subseries strings read Sample P1, P2 and P5, and HEST issue #133 confirms the labels were wrong and corrected in v1.3.0 without updating the benchmark splits. COAD's shipped fold therefore trains on one donor and tests on three; its random-minus-patient gap of about 0.32 is the largest of the ten tasks against 0.05 to 0.19 elsewhere, and it is a fold property, not a tissue property. IDC is the reverse. TENX95 and TENX99 carry different patient labels but are probably two sections of one tumour (10x's page says `donorCount: 1` with Replicate 1 and Replicate 2; the two carry byte-identical 541-entry panels, the only such pair in the task; 96% of the TENX slides' misclassified spots land on the partner slide against 33% at chance). Against that, their spot counts differ 2.1-fold. The attribution is unresolved because the second 10x page returned HTTP 429 on every fetch.

The measurement that does not depend on the label. Holding the test slide and the training-set size fixed and varying only whether the partner section is in the training pool, the partner is worth about $+0.065$ within-slide Pearson on IDC, positive in 6 of 6 encoder-slide cells, which is 54% of IDC's whole random-minus-patient gap of 0.12. READ's two same-specimen pairs give a second estimate, $+0.090$, positive in 12 of 12 cells; READ's folds group the pairs correctly, so there the leak is counterfactual.

**How.** The first sign was in round 1, where COAD's blocked-minus-patient term was three times any other task's with implausibly tight fold dispersion. The review read that as same-patient leakage, which was the right mechanism and the wrong direction. Round 2's split decomposition added a leave-one-slide-out arm, and COAD's novel-slide term came out at 0.11 of its own standard deviation while its patient term stayed at 0.26, which is the signature of a holdout removing several donors at once. That prompted the metadata check, then the audit of all 72 samples against 10x, GEO and journal sources rather than HEST's `patient` field (58 verified, 9 unverifiable, 5 contradicted), producing the `donor_id` column every later stage uses.

**What did not work.** The first replicate-leak design held out both TENX slides together, which removed 80% of the training spots, so it measured training size. A size-matched variant silently dropped the fold that mattered. The design that stands draws two equal-size training sets, one with the partner and one without, for the same test slide. Also, the audit corrected three of its own verdicts when the assumed source pages turned out not to be the ones HEST cites.

**Why it matters and what it changed.** For the benchmark, absolute Pearson on COAD and IDC is inflated and the tasks are not comparable as Table 1 presents them. For the project, this is Topic B's premise measured. The unit that carries shared information is the tumour section, and a second section of the same tumour in training recovers more than half of what a patient split calls generalisation. Four consequences were carried forward. COAD is flagged `patient_labels_unreliable` and excluded from patient-level claims; READ's patient term is a same-specimen term; `donor_id` supersedes `patient` everywhere; every grouping variable is audited against an outside source before use.

### 6.2 Split design matters more than encoder choice

**What.** Under the benchmark's own head and metric, ignoring slide boundaries when splitting is worth about 0.16 within-slide Pearson over ten tasks, against a spread of about 0.10 between the best and worst of twelve foundation models, so 1.6 times the whole encoder ranking. The gap decomposes along a chain of designs, each removing one more kind of shared information, into training-set size 0.013, spatial adjacency within a slide 0.033, a residual adjacency term that only a buffer around held-out blocks removes 0.012, and slide-and-patient identity 0.10. On the three tasks where a patient contributes several slides, the last term splits into novel slide 0.015 and patient identity 0.14, an order of magnitude apart. PRAD is the only task where the novel-slide term is resolved from zero (0.028 with sd 0.002).

Two supporting results. Pooled Pearson over a multi-patient test set is inflated by between-patient variance in its denominator, measured at zero for single-patient test sets and $+0.19$ for nine-patient ones. And a blocked spatial split without a buffer depends on the grid size chosen (spread 0.028 over three sizes); with a 2.5-pitch buffer the spread is 0.010.

**How.** Version 1 reported a leakage gap of 0.31, half of which was the pooled-Pearson artefact; a variance decomposition of Pearson into between- and within-patient parts showed why, and the metric was changed to within-slide before anything else was reported. Version 3 had random, blocked and patient designs and a two-gap decomposition; the review pointed out that blocked-minus-patient conflated slide and patient, that arms differed in training size, and that block edges leak. Version 4 added size matching, a buffered arm, a leave-one-slide-out arm and a grid sweep, and reproduced version 3's shared arms to four decimals before reading any new term. The pooled slide term was withdrawn in favour of per-task terms once COAD's label fault showed the term means different things in different tasks.

**What did not work.** A `donor_out_matched` arm whose per-fold training sizes did not match was rejected by reading the per-fold sizes rather than the mean. A ratio of COAD's patient term to its novel-slide term (199×) was withdrawn because its denominator is within noise of zero; it moved to 115× on a rerun. The R3 jobs, about 35 CPU-hours, completed every design and then died on the final parquet write because a column mixed integers and strings across designs; the summaries survived only because they were written first.

**Why it matters and what it changed.** The benchmark's encoder ranking is a small effect on top of a large split-design effect, and a random spot split (used by several published methods) is not comparable to the shipped one. For Topic A the decomposition names the shift mechanisms in order of size, and the three-design evaluation (random spot, shipped patient, audited donor) is the structure of round 3's first experiment. The buffered block design and the within-slide metric are reusable methodology.

### 6.3 Encoders carry a slide-and-session signature that is in the features and not in the expression

**What.** Within PRAD patient 2, fifteen slides whose pixel sizes span only 1.02×, a linear probe on frozen embeddings identifies the slide at 0.87 to 0.95 balanced accuracy (chance 1/15) under spatial-block cross-validation. The fifteen slides fall into two clusters 0.0066 µm/px apart with contiguous sample IDs, consistent with two scanning sessions; session is decodable at 0.97 to 0.99, and 93 to 96% of the slide probe's confusion mass stays within a session (chance 47%). Regressing eight nuclear-morphology covariates out of the features removes 1.4% of the signature within that patient, against 17 to 27% on tasks whose slides are different patients (IDC 3.0%, consistent with two of its slides being one tumour). Within PRAD patient 1, whose slides differ in nominal pixel size by 20%, resolution class is not decodable at all (0.49 to 0.51 against chance 0.5). And when expression within patient 2 is decomposed with session as the top level, between-session variance is about 3% of the total, at or below zero for 28 of 50 genes, against about 24% between slides within a session and about 74% within slide.

Benchmark-level context. Scan resolution spans 0.137 to 0.688 µm/px across the 72 samples and is aligned exactly with patient identity in PRAD and SKCM and partly in PAAD, so a patient fold there is also a session fold; 31 of 72 samples have no independent corroboration of their resolution.

**How.** Round 1's slide probe reached 0.98 but every pair of benchmark slides differs in patient, tissue, resolution and technical conditions at once. The review identified PRAD patient 2 as the one place where patient and resolution are nearly fixed while slide varies, and the sub-clusters in the metadata as a session contrast inside that. The probes reuse round 1's machinery (scaler, PCA-256 fit on train, logistic regression, balanced accuracy, 800 spots per slide). The session-in-expression check was run because a directive asked for the opposite caveat (that PRAD's slide variance "contains the session effect"), and the data reversed it.

**What did not work.** The resolution probe first reported values near 0.7 and was withdrawn when the class sizes (5 against 2) were written out and the per-fold statistic turned out to equal a constant majority-class predictor (0.714); the pooled statistic replaced it. The "either/or" interpretation rule set before the run (technical or biological) was retired because the data showed both, with session the stronger axis.

**Why it matters and what it changed.** This is Topic A's covariate-shift premise measured rather than assumed. The feature distribution $p(z)$ moves between slides and sessions while $p(y \mid z)$ does not, at least through this channel. It is the case weighted conformal is designed for, and the slide-and-session probe is the density-ratio estimator it needs. It also identifies the hard case, a test session with no calibration support, which PRAD's and SKCM's fold structure creates. The mechanism finding (session, not pixel size) changed how the resolution covariate is read, so that `pixel_size_um` is a proxy for session.

### 6.4 The benchmark head has no intercept, and the $R^2$ ladder

**What.** The head is fit with `fit_intercept=False` on features PCA centres by construction, so predictions have training mean about zero while $\log(1+y)$ has mean about 0.6. Pearson is invariant to that; $R^2$ is not, and is negative in 28 of 29 folds. The identity

$$R^2 = 2r\rho - \rho^2 - b^2 / s_y^2,$$

with $b$ the level offset, $\rho = s_{\hat y} / s_y$ the ratio of prediction to target standard deviation, and $r$ the Pearson correlation, splits the deficit into level, scale and pattern and can be computed on stored columns with no refitting (it reconstructs stored $R^2$ to $10^{-14}$). Fold-median $R^2$ over 12 encoders, 29 folds and 50 genes climbs four rungs, $-0.95$ as shipped; $-0.16$ with a training-mean intercept (gain 0.80); $+0.03$ with the test fold's own mean, an oracle (gain 0.19); $+0.10$ with the optimal scale as well (gain 0.07), which equals $r^2$ and is the ceiling for any level-and-scale recalibration. The scale term reads directly. Since $R^2$ is maximised at $\rho = r$, the head's predictions spread $\rho / r = 1.84$ times more than optimal (median $\rho$ 0.58 against median $r$ 0.32), and the ratio orders with encoder quality, from 2.2 for ResNet50 to 1.7 for UNI2-h.

**How.** The review noticed the `fit_intercept=False` line while reading the trainer and predicted that stored per-fold $R^2$ would be negative. Three heads were refit (no intercept, intercept, target-centred) and shown algebraically to share one slope vector, so the change is a per-gene constant and Pearson is untouched. The float64 exact-solver (Cholesky) head passed the three-head identity checks to $10^{-13}$ and reproduces round 1's per-task Pearson to a mean of $1.5 \times 10^{-4}$; it is the base predictor Topic A uses.

**What did not work.** The identity checks first ran in float32 with tolerances of $10^{-6}$ and $10^{-4}$ and three of four failed on arithmetic that was correct; the float32 accumulation floor is about $10^{-5}$ relative, and the faithful `lsqr` head is not the ridge solution to any tight tolerance (its predictions differ from the exact solution by up to 0.35). The lesson recorded in `WAYS_OF_WORKING.md` is to set thresholds in units the dtype supports and to decide whether the threshold or the claim is wrong before restating either.

**Why it matters and what it changed.** Every Topic A quantity (residuals, widths, CRPS, log score) lives on the absolute scale, so the intercept was mandatory and missing. The over-dispersion ratio is the concrete target a calibration layer must hit. The oracle-level rung is a retrospective diagnostic using test labels, not a method; a real method must estimate shrinkage and any offset on held-out calibration data, and the slide-level mean shift worth $+0.185$ is the same slide-level structure result 6.1 found from the other side. Nicolas asked about this distinction twice; keep it explicit in every write-up.

### 6.5 Table A13 ranks encoders by embedding width because the ridge penalty is inert

**What.** The benchmark's $\alpha = 100 / (d \times n_{\text{genes}})$ is 0.0078 at $d = 256$, indistinguishable from unpenalised least squares on standardised PCA features (five orders of magnitude below where the penalty starts to matter). On raw embeddings the Gram matrix has condition number about $3.0 \times 10^{15}$ at 1536 dimensions (against about 544 after PCA-256), and the same $\alpha$ leaves the solve effectively unregularised, so wider embeddings fit more noise. Spearman between width and score is $-0.95$ on `raw_ridge` and $+0.73$ on `pca_ridge` over twelve encoders. Every encoder with 1536 or more dimensions sits in raw-ridge ranks 7 to 12, every encoder with 1024 or fewer in ranks 1 to 6, and the 512-dimensional CONCH v1 wins the raw head. H-Optimus-1, the strongest encoder, is rank 1 on `pca_ridge` and rank 7 on `raw_ridge`.

**How.** Round 1 found a 0.03 discrepancy on ResNet50's raw-ridge cell and hypothesised a penalty confound. A twelve-point penalty sweep at both widths with Gram condition numbers recorded eliminated that hypothesis and replaced it with width. Round 2 ran H-Optimus-1 on the raw ridge head as a falsification test, since if the explanation is right it should rank poorly there, and it did. The raw XGBoost head for H-Optimus-1 was started and closed unfinished (70 minutes per split, about 34 CPU-hours) because the ridge result settles the question.

**Why it matters.** Table A13 should not be cited as an encoder comparison. Nicolas's own speaker notes for this slide were revised to say that PCA to 256 equalises feature count, which is why the correlation flips; the condition number is a symptom, not the mechanism. This is a self-contained note for the benchmark's authors.

### 6.6 Gene panels differ within a task, targets were selected on test spots, and the selection protocol moves the answer

**What.** In every Xenium task the samples do not share a panel (PAAD 159 genes in common of 919; LUNG 259 of 823; IDC 280 common, with one sample measuring 41 the others do not). The 50 targets per task were selected from the all-sample intersection using all spots, test folds included. Selecting from training samples only changes the list by about half (25 of 50 shared on average, 11 on PRAD), changes measured Pearson by about $+0.005$ on average and up to $+0.04$ on individual tasks, and on four Xenium tasks names genes the held-out slide cannot measure. Holding the gene set fixed and varying only whether the ranking sees test spots, the rank correlation between the two rankings is 0.51.

**How.** The shipped selection was reimplemented and shown to reproduce all ten lists exactly (set and order) before anything else. The within-fold version raised a `KeyError` on the first Xenium task because a fold-selected gene was absent from the held-out slide; the error was the finding. The gap was first labelled leakage, then relabelled selection-protocol sensitivity once the gene-set difference between arms was found to correlate at 0.76 with the gap; selection acts through which genes are chosen, so composition is the mechanism, not a confound.

**Why it matters.** Leakage-free target selection is not well defined on this benchmark. For Topic A the target list is a fixed given and coverage claims are conditional on it. Across-task transfer is blocked outright (the five Xenium tasks' target lists are disjoint; their panels share 14 genes).

### 6.7 Negative binomial without zero inflation is the observation model

**What.** Per-gene maximum-likelihood fits on the 500 gene-task pairs give NB over Poisson on 478 of 488 converged pairs, every gene is overdispersed (minimum Fano 1.6), ZINB beats NB on 28 of 488 with median $\Delta\text{AIC}$ of $-2.002$, which is AIC's exact penalty for one parameter that buys nothing. Sparsity follows the assay (median zero fraction 0.29 on Xenium, 0.61 on Visium).

**How and what to note.** The prediction that ZINB's AIC gain would be exactly $-2$ was written before the fit. Fourteen genes whose NB fits diverged while the library reported convergence were flagged rather than trusted; taken at face value they would have reversed the conclusion. The review's caveat stands, that these are marginal fits pooled over spots, so the Fano factors include between-spot biological variation; the conditional dispersion after an image-conditioned NB head is fit has not been measured and is part of round 3.

**Why it matters.** Settles the likelihood for Topic A's model-based head and for count-level work in Topic B. STFlow's ZINB prior is not supported on these targets.

### 6.8 The Topic B estimand is slide-level, and the unit of inference is the donor

**What.** HEST's own biomarker example, the correlation of mean nuclear area with GATA3 on one Xenium breast slide ($r = 0.47$ in the paper), reproduces at 0.46 on that slide under the morphology build the check was defined on and at 0.42 under the current build (spot bootstrap interval 0.38 to 0.47); it is 0.15, 0.01 and $-0.06$ on the other three IDC slides under either build, with identical rank order. It is a slide-level quantity with large between-slide variance. A nested variance decomposition of expression (spot within slide within donor) on audited donor labels, using a Henderson moment estimator validated on 40 unbalanced simulations (it recovers the true shares to within 1 to 2%), gives a between-donor fraction of 0.39 on CCRCC (24 donors) and 0.34 on LYMPH_IDC (4), pooled 0.38 over the tasks with at least three donor degrees of freedom and verified labels; within-slide variance is 0.6 to 0.9 everywhere. Per gene, within task, genes that lose most under a patient split are the genes a same-tumour section recovers most (Spearman $+0.38$); between-slide-within-donor variance predicts the novel-slide cost ($+0.21$); between-donor variance does not predict the split penalty ($+0.04$, not significant).

**How.** Morphology features were rebuilt from the shipped CellViT segmentation with a per-sample patch-geometry calibration (patch extents span 163 to 818 pixels across samples, so no constant patch size is correct) and gated on reproducing Figure 3e. The variance decomposition used `donor_id` from the audit. A pooled estimate pairing CCRCC with PRAD, as the directive said, came out at 0.122 and was recognised as an artefact (PRAD has two donors and a truncated zero component for 68% of genes); the well-powered pairing was reported instead, with the directive's version beside it.

**Why it matters and what it changed.** For Topic B, the cluster is the donor with slides nested inside; with thousands of spots per donor and a between-donor share near 0.4, the design effect $1 + (m - 1)\rho$ is in the hundreds, spot-level standard errors are off by a factor of about 30, and the effective sample size $n_{\text{eff}} = nm / (1 + (m-1)\rho) \approx n / \rho$ is set by the donor count. (Nicolas worked through this derivation on 21 September; the derivation is in this chat's transcript and should be reused if he asks again. The notes for slide 11 should say precision is "set by the number of donors", not "is the number of donors".) For Topic A, the per-gene result says a donor-level random intercept would not absorb the split penalty, because the penalty does not track donor-level mean differences in expression; it tracks what a replicate section shares, which is the state of that piece of tissue and its processing. So the correction acts on the features and on slide-level offsets, while the variance is still clustered by donor.

### 6.9 A footnote on precision

Per-gene Pearson under the benchmark's iterative solver carries about $10^{-3}$ of solver noise (median 0.0005, up to 0.0276 for one gene). Task-level means are unaffected. Per-gene values should not be quoted past three decimals, and Topic A builds on the exact float64 head.

---

## 7. Benchmark properties and known limitations

The README carries the maintained list of ten properties of HEST-bench found by this replication, each with its establishing file, and eleven known limitations. The properties, in one line each, are (1) IDC's TENX95/TENX99 pair is probably one donor, unresolved; (2) COAD's patient labels merge three donors; (3) READ's patients are same-specimen replicate pairs; (4) samples within a task do not share a gene panel; (5) target selection saw test spots; (6) scan resolution aligns with patient in PRAD, SKCM, PAAD, and the mechanism is session; (7) the ridge penalty is inert and Table A13 ranks by width; (8) the head has no intercept; (9) per-gene Pearson carries `lsqr` solver noise; (10) nine of 72 donor labels are unverifiable and five contradicted.

Six limitations constrain round 3. Selection-protocol sensitivity means coverage is conditional on the shipped gene list; the IDC attribution is unresolved, so IDC should be run under both the shipped labels and the probable-one-donor labels; the variance-component shares have no intervals; the session result rests on one patient; H-Optimus-1 has no `raw_xgb` cells (deliberate); STFlow has not run.

`docs/hest_bench_issue_draft.md` is a draft GitHub issue to the HEST authors covering the IDC pair, COAD, READ, panel heterogeneity and three questions. It is unsent, and sending it is Nicolas's decision with David.

---

## 8. The repository, the data on Longleaf, and the documents

### 8.1 Repository (`NicWYZ/HEST-1k-replication`, public)

```
README.md              entry point: status, headline result, key findings, benchmark properties,
                       known limitations, reproduction commands
MANIFEST.md            sizes and hashes of the large artifacts that stay on Longleaf
results/
  faithful/<head>/<encoder>/<task>/    the paper's four configurations, per-fold results.json
  tailored/<question>/                 round 1 diagnostics: splits, site_probes, shift, counts,
                                       morphology, regularization, genes, integrity
  round2/<STAGE>/                      R0_resolution, R1_intercept, R1b_heads, R2_fold_hvg, R3_splits,
                                       R4_probes, R5b_audit, R5c_leak, R6_theta, R6_variance,
                                       R7_pergene, R8_raw_heads; each with PROVENANCE.txt
  summary/                             results_encoder.csv, discrepancy_table.csv, deck_numbers.csv, ...
code/
  scripts/                             one script per experiment; round2_* prefix for round 2;
                                       verify_numeric_claims.py, build_deck_numbers.py, build_summary_tables.py
  figures/                             fig01..fig07 scripts, make_all.py, make_readme.py
  configs/                             one YAML per faithful run
  checks/                              parquet verification
figures/deck/                          seven deck figures, PNG and PDF, generated README
docs/                                  all reports and working documents (index in docs/README.md)
bench_data/                            inventory only (the dataset is gated)
env/                                   requirements.lock, conda_env.yaml, versions.txt, REBUILD.md
superseded/                            root-level superseded files (currently one)
```

Tags are `round2-final` (freeze), `round2-final-deck`, `round2-docs-clean` (current HEAD).

### 8.2 Data on Longleaf (not committed; `/work/users/w/e/weiyang/hest_replication`)

| asset | size | used by |
|---|---|---|
| `bench_data/` (hest-bench snapshot, gated) | 39 GB | everything |
| `embeddings/<task>/<encoder>/<sample>.h5` | 14 GB | any head refit, probes |
| `instrumentation/<task>/preds.parquet, spots.parquet` | 0.7 GB | round 1 joined predictions |
| `instrumentation/round2_intercept_f64/<task>/preds__<enc>__f64.parquet` | 3.3 GB | **the Topic A base predictions**, float64 intercept head, per spot per gene per fold |
| `instrumentation/morphology_v2/` | 6.5 MB | per-spot morphology, current build (Topic B covariates) |
| `results/round2/R3_splits/pergene__*.parquet` | in repo | per-gene within-slide Pearson per design |

Slurm account `rc_htzhu_pi`. The scheduler notes in `docs/WAYS_OF_WORKING.md` (priority is effectively fixed for small CPU jobs; size memory from `sacct`; set harness ceilings from queue time plus runtime; never compute on the login node) are the accumulated hard-won knowledge and Claude Science should re-read them.

### 8.3 Documents in `docs/` and what each is for

`HEST_replication_handoff.md` (12 Sept, original plan and ground rules), `round1_final_stage_report.md` (frozen record), `HEST_replication_review.md` (the audit that produced round 2), `round2_execution_plan.md` (stages R0 to R8), the frozen stage reports `round2_R0_R1_stage_report.md`, `round2_R3_stage_report.md`, `round2_R5_stage_report.md`, `round2_R8_stage_report.md`, `round2_closeout_report.md`, `round2_results_synthesis.md` (the ranked synthesis; also in the Biostat Research project as `claude/hest-replication-synthesis.md`), `literature_landscape.md`, `deck_master_outline.md`, `hest_bench_issue_draft.md` (unsent), `r5_idc_provenance.md`, `closeout_gate_report.md`, `docs_clean_report.md`, and `WAYS_OF_WORKING.md` (living list of procedures, each tied to the failure it prevents; the most useful document for anyone new to the project).

### 8.4 Gaps to close before round 3 work starts

- The decision memos are not in the repository. Nicolas has `round2_R3_decisions.md`, `round2_R5_decisions.md`, `round2_closeout_decisions.md`, `deck_figures_and_repo_update.md` and `post_deck_repo_instructions.md` from the old session's outputs; `round2_R1_decisions.md` was not saved. Whatever he supplies goes under `docs/decisions/` with the historical banner; whatever he does not is listed in `docs/README.md` as not in the repository, and nothing is reconstructed. `docs/README.md` also needs its index brought up to date (it is missing `docs_clean_report.md`, `literature_landscape.md` and `round2_results_synthesis.md`, and lists `r5_idc_provenance.md` as absent when it is present).
- The deck's backup slide and the synthesis quote the selection gap from an earlier tabulation than the README's; the difference does not change the reading and the outline is not revised.
- `results/summary/results_encoder.csv` now has H-Optimus-1's `raw_ridge` cells; the README's headline table may still show a dash for that cell. Check.

### 8.5 The deck

Artifact `https://claude.ai/artifact/FB3N6rXBZKnhMf4wvdmq9x` (Slides type; files `project/deck.json` and `project/slides/<id>.html`, slide order cover, intro, faithful, issue1, issue2, issue3, landscape, topics, result1, result2, result3, next, backup1, backup2). Nicolas edits speaker notes directly in the editor and sends comment threads to Claude; each was answered in its thread. Three suggested edits were posted in threads but not applied because the editor's autosave blocked publishing, namely revised notes for slide 6 (thread 89e406fd), the last bullet and a standard-deviation-versus-variance correction for slide 9 (thread b63c7f43), and a rewording of the last two paragraphs of slide 11's notes (threads 9daf4f2e and this chat). Check whether he applied them before building the next deck.

The next presentation starts from slide 7 and goes through 12, then add round 3 results. Plan for the same 15-minute budget unless he says otherwise, and keep the same style (figure left, bullets right at 30 px, brief notes).

---

## 9. Round 3: what to do next, how, and why

### 9.1 Goals

Round 3 turns the motivation into Topic A's first experiment and Topic B's first result. The result that would make Topic A a paper is the pattern of coverage failure across fold designs and its repair. The result that would make Topic B a paper is that spot-level PPI intervals fail and donor-clustered ones hold, with the width gain from predictions bounded by the donor count.

Round 3 also opens the data expansion (track D), because the benchmark subset cannot carry the project past this round; see § 9.3. The A and B stages run on cached embeddings, the float64 head's machinery, the audited labels, the morphology parquets and the probe machinery, and need no GPU. Track D is the only part that downloads data and, at its embedding step, needs the GPU queue.

### 9.2 Stages

Full specifications with inputs, outputs, acceptance checks and predictions are in the execution handoff § 6. In brief:

| stage | what | why | gate |
|---|---|---|---|
| S0 | housekeeping: commit memos, update docs index, `round3_` and `results/round3/` conventions, transcribe the plan into the operating plan | the record has to be complete before it grows | no |
| A0 | the conformal harness: three fold designs (random spot, shipped patient, audited donor; plus slide-out on multi-slide tasks) each yielding proper-training, calibration and test sets; calibration unit chosen at the highest level the training pool supports (donor, else slide, else buffered block) and recorded; float64 intercept head fit on proper-training only; scores, intervals, coverage, width, interval score per gene and slide | the harness is where design errors live; it is checked before any result is read | no |
| A1 | marginal coverage at $\alpha = 0.1$, all ten tasks, twelve encoders, absolute and scaled residual scores | the first coverage table across designs is the core result | **report and wait** |
| A2 | conditional coverage: by slide, session and resolution group, calibration-support flag, predicted-expression decile, gene (against the R7 per-gene split penalty), nuclear composition; decomposition of misses into level (asymmetry above versus below) and scale (oracle width versus calibrated width) | says where coverage fails and whether the failure is a centring or a width problem, tying back to the ladder | no |
| A3 | weighted conformal with two density-ratio estimators (a calibration-versus-test classifier on PCA-256 features, using test features only; and a coarse covariate weight on session and resolution group), with the effective sample size of the weights per test slide as the calibration-support diagnostic; a hierarchical-conformal arm if the literature search in § 3 supports one | the repair; the test of whether reweighting restores coverage where the test session has calibration support and fails where it does not | **report and wait** |
| A4 | adaptive scores and the model-based comparator: CQR on PCA-256, the negative-binomial head with its predictive quantiles, log score, and its conditional dispersion; conformalised NB | width at matched coverage; whether model-based uncertainty is calibrated across designs; the conditional dispersion the review asked for | no |
| D0 | inventory of full HEST-1k from the metadata table already on disk, and a proposal of three expansion sets with sizes | selecting the data by design criteria before downloading anything | no (proposal goes in the A1 report) |
| D1 to D3 | download the approved set (patches, expression, segmentation, metadata; no whole-slide images), embed it with three encoders, audit its donor, lab and session labels against sources | the institution axis and the donor count the topics need | no (status in the A3 report) |
| D4 | the R3 decomposition and R4 probes rerun with a lab arm on the institution set | the first measurement of lab shift with donor and slide separated | end-of-round report |
| B1 | PPI for a morphology-expression estimand with three variance estimators (spot i.i.d., donor cluster-robust, donor bootstrap), cross-fitted through the donor-out folds; CCRCC as the powered task, IDC $\theta_1$ as the example, PRAD as the two-donor failure case | Topic B's first result | no |
| B2 | semi-synthetic coverage over repeated labelled/unlabelled donor partitions, masking whole donors; coverage of the full-data value, width ratio against classical | the validation that makes B1 a claim rather than an illustration | **end-of-round report** |

Predictions to write down before running, per the project's practice. Random-spot coverage at nominal for every task and encoder (if not, the harness is wrong). Under-coverage under the patient and donor designs, worst where the shift is largest (PRAD and SKCM patient folds, which are session folds; COAD under shipped labels versus audited ones). Coverage nominal under the donor design only when the calibration unit is the donor. Per-gene under-coverage correlated with the R7 per-gene split penalty. Reweighting restores coverage where the effective calibration sample size stays high and cannot where it collapses. NB intervals under-cover under the donor design like the conformal ones do, and conformalising them fixes marginal coverage. In B, spot-level PPI intervals under-cover badly, donor-clustered ones hold at nominal with few donors, and the width gain from predictions shrinks as the between-donor share grows.

### 9.3 Track D. Expanding the data beyond the benchmark

**Why.** The benchmark subset is 72 samples, at most 24 donors in any task, one lab per task, and 50 genes per task chosen with test spots. It was enough to measure the premises. It cannot carry a methodological project. Topic A's institution axis does not exist in it; Topic B's donor-clustered inference has one task with enough donors; every per-gene claim is conditional on a list chosen the wrong way; and a paper evaluated on ten small tasks from one benchmark will be read as a benchmark note. Full HEST-1k has about 1,200 samples from 153 cohorts across 26 organs, mostly Visium, with per-sample patches, expression, CellViT segmentation and metadata on HuggingFace. It is gated, and Nicolas already has access (round 1 pulled the CellViT segmentation from it). The plan is a designed subset, not the archive, which is over 2 TB mostly because of the whole-slide images that the pipeline does not need once patches exist.

**What more data buys.** A real institution contrast, meaning one organ and one technology profiled by several labs with several donors each, so lab, donor and slide effects can be separated by the same decomposition machinery as R3 with a `lab_out` arm. Donors in the tens to hundreds for Topic B. Same-tissue pairs across platforms (a block profiled on both Visium and Xenium) for a platform-shift axis. On Visium, the whole transcriptome, so target genes can be chosen on training data only and coverage claims stop being conditional on the shipped lists, and per-gene analyses run on hundreds of genes rather than 50. Non-cancer and mouse tissue as out-of-distribution test sets for coverage. And it opens the landscape's directions #2 (batch-robust evaluation) and #3 (cross-panel generalisation) if the topics widen later.

**Stages.** D0 is an inventory and a selection from HEST's metadata table, which is already on disk (R5b read it), so it costs nothing and needs no approval. It counts samples, HEST-labelled patients, cohorts, technology, organ, species and pixel size, adds bytes per sample from the HuggingFace listing, and proposes three sets with sizes and storage: an institution set (one organ, one technology, at least three labs with at least three donors each), a donor-power set (the organ and technology with the most distinct donors), and a platform-pair set. Nicolas approves the sets and the storage ask; the advisors are told which sets and why. D1 downloads patches, expression, segmentation and metadata for the approved sets to `/work`, after a quota check. D2 embeds them with three encoders (`hoptimus0`, `uni_v2`, `resnet50`), the only GPU work in the round, using the benchmark's own extraction path so embeddings are cached per sample. D3 audits the donor, lab, scanner and session labels against sources before anything is grouped by them, as R5b did, because HEST's patient field was wrong twice. D4 reruns the split decomposition and the probes on the institution set with a lab arm, listing every variable that differs between arms (lab, scanner, protocol, resolution, donor). The Topic A harness is written so a task is any set of samples with donor, lab and session labels and a target-gene list, so it runs on the expansion sets unchanged; the expanded-data experiments proper (Topic A under lab shift, Topic B with many donors, training-only gene selection) are round 4.

**Risks.** Metadata quality (expect the lab and donor fields to need auditing). Storage (patches for a few hundred samples are on the order of 100 GB; D0 gives the exact figure). The GPU queue, which was saturated in round 1; three encoders only, and per-sample caching so a killed job resumes. Target-gene selection on new tasks needs a training-only protocol from the start.

### 9.4 Sequencing and time

A0 and A1 first (two to three days, including the harness check), with D0 alongside since it is reading and counting. A2 after A1's report is answered (one day). A3 (two days) and A4 (two to three days) in that interval, A3 before A4 since A3 gates; D1 to D3 run in the same interval once Nicolas approves the sets. B1 (two days) and B2 (one to two days) after A3's report is answered, with D4 alongside; B1 needs A1's donor-out predictions. About two to three weeks of wall time with the gates. R3's actuals (47 hours for three encoders with a grid sweep) are the sizing reference; head fitting alone is minutes per encoder, so fan out by encoder.

### 9.5 The gate rule, in the wording Nicolas approved

Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Round 3's gates are A1, A3 and B2. Track D's download (D1) additionally waits for Nicolas's approval of the selected sets. Contact with anyone outside the project is never the session's decision.

### 9.6 What you do first

1. Read this document, the execution handoff, the README, and `WAYS_OF_WORKING.md`. Have Nicolas connect the local repository so you can check numbers against files.
2. Do the two literature searches in § 3 (hierarchical conformal; PPI under clustering) and decide whether A3 gets a hierarchical arm and whether B1's variance estimator has a published form to cite. Update the execution handoff's § 6 if so, before Nicolas hands it over.
3. Give Nicolas the execution handoff in full for Claude Science, with any updates from step 2.
4. When A1's report arrives, check the random-design coverage first. If it is not at nominal, nothing else in the report is interpretable. Then review D0's proposed sets against the criteria in § 9.3 and give Nicolas a recommendation with the storage figure, so he can approve the download.
5. Keep a running list of what goes on the next deck. Slides 7 to 12 of the current deck come first; round 3 adds the coverage table across designs (the new Table 1), the failure-and-repair figure, and the PPI interval comparison.

### 9.7 Decisions still open, and who owns them

- Whether the benchmark findings become a GitHub issue, a short note, or the first section of the Topic A paper. Nicolas and David.
- Which expansion sets to pull and how much storage to ask for. Nicolas, on D0's proposal, with the advisors informed. Pulling more data is decided; the sets are not.
- Whether Topic A targets AISTATS or ICML for 2027, which changes framing (theory versus empirical). Nicolas, after round 3's results.

---

## 10. Standing rules that produced most of round 2's findings

These are the ones to repeat in every memo, because each caught an error that would otherwise have propagated.

- Before naming a term in a decomposition or a probe, list every variable that differs between its arms, in writing.
- Audit a grouping variable against a source outside the dataset before grouping by it.
- Numbers in any document come from files, cited by path, and the numeric-claim sweep runs before any document is handed over.
- State acceptance thresholds in units the arithmetic supports, and when a check fails decide whether the threshold or the claim is wrong before restating either.
- Every refit has one arm anchored to the prior result.
- Write predictions down before running the experiment.
- Do not quote a ratio whose denominator is within noise of zero.
- Put a time cap on anything that is not analysis.
