> **Live operating plan for round 3, opened 2026-09-22.** This is the execution session's own
> transcription of `docs/decisions/round3_execution_handoff.md`, written before anything was run.
> It is updated when a new instruction or decision document arrives and at no other time. It is
> not a stage report and carries no results.

# Round 3 operating plan

Transcribed from the round-3 execution handoff (22 September 2026), which starts the round from tag
`round2-docs-clean`, commit `4da6b86`. Its companion, `round3_oversight_handoff.md`, is context
rather than instruction; it was committed by Nicolas in `80f1ae5` together with the six round-2
decision memos, and its action items that bear on execution are transcribed here too, in § 1.1
and § 10. An earlier revision of this section said the oversight handoff had not been supplied,
which stopped being true when that commit landed.

The transcription rule that produced this document is itself a standing instruction from Nicolas:
every instruction or decision document is transcribed into the operating plan before anything in it
is run, and the plan is updated again each time a decision memo hands work back. Anything in an
instruction that looks wrong is flagged in the next stage report rather than changed silently here.

---

## 0. Role and responsibilities

This session is the execution agent. A separate oversight chat reviews the stage reports, makes
scope decisions and writes decision memos, which Nicolas hands over in full. Nicolas Weiyang Zhang
(Longleaf ONYEN `weiyang`, Slurm account `rc_htzhu_pi`) reads every command before it runs.

The responsibilities, as stated in the handoff § 0, are to run the planned analyses; to SSH into
Longleaf and submit Slurm jobs; to extract and analyse results; to debug and iterate; to generate
figures; to write stage reports in the § 8 format; to transcribe each instruction document into this
plan before starting work on it; to commit, push and maintain the GitHub repository, keeping only
the most up-to-date results in it, moving anything superseded into a `superseded/` folder and
keeping every working document under `docs/`; and everything carried over from the two previous
rounds.

### 0.1 Repository route for this round

Round 3 introduces one change of mechanism, not of practice. Nicolas has granted this session
read-write access to the local clone at `/Users/nicolaszhang/HEST-1k-replication`, so that clone is
now the sole committing and pushing copy of the repository, over HTTPS with the configured GitHub
token. That token carries push rights on `NicWYZ/HEST-1k-replication`; it neither replaces nor
disturbs the SSH key the Longleaf tree at `/work/users/w/e/weiyang/hest_replication` uses, which
remains configured there and untouched.

The Longleaf tree becomes a pull-only working copy for this round. Results are produced there by
Slurm jobs, the summary tables and provenance files are transferred down into the local clone, and
every commit and tag is made locally and pushed from there. One committer, so the two copies cannot
diverge; this is the same one-writer-per-file rule the handoff § 7 applies to parallel jobs, applied
to the repository itself.

---

### 0.2 Parallel execution

Nicolas's second standing instruction for this round: work that can be done in parallel is always
fanned out to sub-agents rather than run sequentially by the lead session. Each interval is therefore
split into a parallel part and a sequential part, and § 3 names the tracks.

Two constraints on the fan-out.

- **One writer per file**, which the handoff § 7 requires: tracks are cut so that no two write the
  same path, and where several must contribute to one table, each writes its own fragment and a
  merge step reports collisions.
- **One committer**, which is this session's decision rather than an instruction. The handoff says
  nothing about who may commit; it requires only that commit messages go through a file and that a
  gate message state the full table. Extending the one-writer rule to the repository itself, no
  sub-agent commits, pushes or tags: a sub-agent's outputs come back as files, the lead session
  places them in the repository, and the lead makes the commit. Flagged here as a choice so it can
  be overruled.

A track that would submit Slurm jobs does so under the same account, so the tracks are also sized
against the queue rather than against the node: jobs go out early and the wall is the wall the work
needs.

---

## 1. Working principles carried over

Each of these earned its place in an earlier round by catching something.
`docs/WAYS_OF_WORKING.md` is the accumulated version and was re-read in full before the first job of
this round.

- Silent failure is the main risk. Verify each stage's output against an expected value before
  moving on.
- Never assert a number that has not been read back from a file. Cite the path.
- Before naming a term or a probe, list in writing every variable that differs between its arms.
- Audit a grouping variable against a source outside the dataset before grouping by it. That is
  done for donors, so `donor_id` is the grouping variable and `patient` is not.
- Write predictions down before running, and report them beside the outcomes.
- Every output directory gets `PROVENANCE.txt`. Every parquet is written with an explicit schema.
  Summaries are written before bulk tables. Seeds come from `zlib.crc32`, never `hash()`.
- In reports, quote numbers at the precision the comparison needs and state the relative scale.
  Full precision stays in the files and in the computations.
- Do not reconstruct or revise a past working document that has served its purpose. A memo that was
  not saved is listed as absent, not rewritten.
- Put a time cap on anything that is not analysis. Round 3's caps are in § 7.

Three more from the oversight handoff's own standing list (its § 10) that the execution handoff
does not restate:

- State an acceptance threshold in the units the arithmetic supports, and when a check fails,
  decide whether the threshold or the claim is wrong before restating either.
- Every refit has one arm anchored to the prior result. In round 3 that arm is A0's H1 check
  against R1b.
- Do not quote a ratio whose denominator is within noise of zero. Report the numerator and the
  denominator with their dispersion and say which one is resolved from zero.

### 1.1 How the reports are written, from the oversight handoff § 0.1

These are Nicolas's stated preferences, several of them repeated after a correction, so they bind
every report and message this session writes.

- Plain, natural writing. No em-dashes, no colon-then-explanation constructions, no compressed or
  clever phrasing. Maths as rendered LaTeX rather than code blocks or plain-text notation.
- Numbers at the precision the comparison needs. What matters in prose is the relative scale, that
  one effect is 1.6 times another or that a term is an order of magnitude smaller, not the fourth
  decimal. Full precision belongs in the computations and the files.
- When he asks how something works, derive it slowly. The compressed version has not been enough
  any of the times he has asked.
- Do not inflate length anywhere, including speaker notes, which cover only what is on the slide.
- Minimal biology by design. Expression is a signal to predict, calibrate and use for inference;
  do not introduce gene-level biology.
- The skills the project is chosen for are calibration, distribution shift, semi-supervised
  inference and cluster-robust variance, and the venue preference is ML conferences or statistics
  journals. Keep that framing when choosing between options.

---

## 2. Flags every round-3 table carries

| flag | applies to | effect |
|---|---|---|
| `patient_labels_unreliable` | COAD | excluded from any patient-level claim under shipped labels; included under `donor_id`, where COAD has four donors and TENX111 is its own donor |
| `same_specimen_pairs` | READ | its patient term is a same-specimen term |
| `idc_attribution_unresolved` | IDC | run under shipped labels (four patients) and audited labels (three donors, TENX95 and TENX99 merged); both reported |
| `resolution_uncertain` | 31 of 72 samples | carried as a column from `results/tailored/integrity/sample_metadata.csv` |
| `donor_label_status` | every sample | `verified`, `unverifiable` or `contradicted`, from `results/round2/R5b_audit/donor_audit.csv` |
| `calibration_unit` | every fold in round 3 | `donor`, `slide` or `block`; set by the rule in § 4.2 |

The evaluation runs under three fold designs (random spot, shipped patient, audited donor) plus
`slide_out`, with COAD flagged, READ flagged, IDC run under both label sets, and `donor_id` as the
grouping variable throughout. The shift to be handled is slide and session novelty with donor
novelty on top. The base predictor is the float64 intercept head, `intercept_f64`, from round 2's
R1b. The variance for Topic B is clustered by donor.

---

## 3. Gates and sequencing

Report-and-wait means that no stage after the gated stage starts until the oversight chat has
reviewed the report and Nicolas has handed back the decision. Not the dependent stages only, and
not the expensive ones only. Every stage. Nothing after a gate is set up, staged or piloted.

Inside an interval there are no interim reports and no interim stop conditions. Anything that would
have halted work is handled under § 8, recorded in an "Escalations" section of the next report, and
work continues. If a defect invalidates a completed stage's numbers, it is fixed and rerun inside
the interval and the report says so. The one exception is an H1 or H2 failure in A0, where work
stops immediately because nothing downstream would be interpretable.

| interval | parallel tracks | sequential part | report |
|---|---|---|---|
| 1 | Housekeeping (S0 and the task-definition files), Harness (A0 and its acceptance checks), Inventory (D0) | A1, which needs both the harness and the task definitions | **A1 report, then wait.** D0's proposal is in it |
| 2 | Conditional (A2), Weighted (A3), Expansion (D1 to D3) | none | **A3 report, then wait.** A2 and the D status are in it |
| 3 | Scores (A4), Inference (B1 and B2), Lab shift (D4) | none | **B2 report, end of round** |

The tracks within an interval are independent by construction: they read the same inputs and write
disjoint paths. A1 is sequential because it runs the harness the Harness track builds over the task
definitions the Housekeeping track writes. The gate report at the end of each interval is written by
the lead session, since it is the synthesis across tracks.

Idle capacity inside an interval may go to housekeeping and to supplements of stages already
complete in that interval, never to a stage after the gate. D1 carries a second condition besides
the interval gate: it does not start without Nicolas's approval of the selected sets and the storage
ask.

When a decision memo arrives, the first action of the next interval is to transcribe it into this
document and into the session's operating plan. Only then does the interval begin.

---

## 4. The stages

### 4.1 S0. Housekeeping (half a day, capped at one day)

1. Transcribe the handoff into this operating plan. Flag anything that looks wrong in the A1 report
   rather than changing it silently.
2. The round-2 decision memos (`round2_R3_decisions.md`, `round2_R5_decisions.md`,
   `round2_closeout_decisions.md`, `deck_figures_and_repo_update.md`,
   `post_deck_repo_instructions.md`, and the round-3 handoff itself as
   `round3_execution_handoff.md`) go under `docs/decisions/`. Nicolas is placing and committing
   these himself, so S0 does not wait on them; once present, each is bannered as a closed record and
   swept with the `historical` class. `round2_R1_decisions.md` was not saved, is listed in
   `docs/README.md` as not in the repository, and is not reconstructed.
3. Update `docs/README.md`. It omits five documents that are present, and it lists
   `r5_idc_provenance.md` as absent when the file is in the directory.
4. Check the README headline table shows H-Optimus-1's `raw_ridge` average now that
   `results/summary/results_encoder.csv` carries it.
5. Create `results/round3/` and the `round3_` script convention, and commit this document.

### 4.2 A0. The conformal harness (one to two days)

**Why.** Every Topic A number comes out of this harness. A calibration set that is not exchangeable
with the test set under the design's assumption, a PCA that saw calibration spots, or an overlap
between sets would all produce coverage numbers that mean nothing. So the harness is built and
checked before any result is read.

**Script.** `code/scripts/round3_a0_harness.py <encoder> --task-def <file>`, extending
`code/scripts/round2_split_v4.py`. For each task, design and fold it produces three disjoint spot
sets, proper-training $T$, calibration $C$ and test $E$, fits the base predictor on $T$ only, and
evaluates conformal intervals on $E$.

**Task definition.** A task is a file, not one of the benchmark's ten hard-coded names. It lists
sample ids with `donor_id`, `lab`, `session`, `resolution_group`, the § 2 flags, the fold
assignments per design, and the target-gene list with how it was chosen. The ten benchmark tasks are
written as `results/round3/task_defs/<task>.json` in S0; track D's expansion sets become further
files. The harness assumes nothing about the benchmark's directory layout beyond what the task file
points at.

**Base predictor.** On $T$ only: `StandardScaler`, then `PCA(256, random_state=1)`, then a float64
Cholesky ridge with intercept at $\alpha = 100/(256 \times 50)$, which is exactly the R1b
`intercept_f64` head. Predictions for $C$ and $E$. Nothing is fit on $C$ or $E$ except the conformal
quantile on $C$ and, in A3, weights that use features only.

**Designs.** Four, each yielding $(T, C, E)$ per fold. Proper-training sets are size-matched across
designs within a fold by subsampling to the smallest, as R3 did, and the sizes are recorded.

| design | test $E$ | pool for $T \cup C$ | calibration unit |
|---|---|---|---|
| `random` | a random draw of the shipped fold's test size over all spots of the task, 5 repeats | the rest | spot; $C$ is a random 20% of the pool |
| `patient` | the shipped fold's test slides | the shipped fold's training slides | highest available level using HEST `patient` |
| `donor` | leave-one-donor-out by `donor_id` (COAD four folds; IDC three folds under audited labels plus the shipped four-fold version) | all other donors | highest available level using `donor_id` |
| `slide_out` | one slide, on PRAD, READ and IDC under audited labels only (corrected at the A1 gate, see § 12.1; the handoff's list also named COAD and LYMPH_IDC, where each donor has one slide and the design is the `donor` partition exactly) | all other slides, including the donor's other slides | slide; record `cal_shares_donor_with_test` |

**Calibration-unit rule.** Within the pool, hold out about 25% of the units at the highest level the
pool supports, rounding up to at least one unit. Use the donor if the pool has at least two donors
(patients, under `patient`); otherwise the slide if it has at least two slides; otherwise buffered
spatial blocks within the single slide (grid 6, 2.5-pitch buffer, about 20% of blocks). Record
`calibration_unit`, `n_cal_units`, `n_cal_spots`, `cal_shares_session_with_test` (any calibration
slide in the test slide's `resolution_group`, and for PRAD patient 2 the same session) and
`cal_shares_donor_with_test`. Where the pool has at least three units, draw three calibration sets
with crc32 seeds and report the dispersion. This rule is part of the design, because the table's
structure, which folds could calibrate at the donor level and which could not, is itself a result.

**Scores and intervals**, per gene, at $\alpha = 0.10$, with the $\alpha = 0.20$ quantile also
stored and 0.10 reported.

- `abs`: $s_i = |y_i - \hat y_i|$; interval $\hat y \pm \hat q$, with $\hat q$ the
  $\lceil (n+1)(1-\alpha) \rceil / n$ empirical quantile of the calibration scores.
- `scaled`: $s_i = |y_i - \hat y_i| / \hat\sigma(x_i)$, with $\hat\sigma$ a ridge regression of
  $|y - \hat y|$ on the PCA-256 features fit on $T$'s in-sample residuals and floored at $10^{-3}$;
  interval $\hat y \pm \hat q\, \hat\sigma(x)$.

**Metrics** per (task, design, fold, repeat, encoder, score, gene, test slide): `coverage`,
`width_mean`, `interval_score` (Winkler at $\alpha$), `miss_above`, `miss_below`, `n_test`.
Aggregation follows the project's metric convention, per slide, then mean over slides, then over
genes, then over folds with the standard deviation across folds.

**Outputs** under `results/round3/A1_coverage/`, since A0 writes the harness and A1 runs it at
scale: `a1_calibration_units.csv`; `a1_by_task.csv` with columns task, design, encoder, score,
calibration_unit, n_folds, coverage_mean, coverage_sd, width_mean, width_sd, interval_score_mean,
n_train_matched; `a1_by_slide.csv`; `pergene__<enc>.parquet` with an explicit `pa.schema` and fold
as a string. Summaries before parquets.

**Acceptance checks.**

- **H1, anchor to the prior result.** With the calibration fraction set to zero on the `patient`
  design, the harness's per-task Pearson equals R1b's `intercept_f64` per-task Pearson for every
  encoder-task cell to within $10^{-6}$, against
  `results/round2/R1b_heads/faithful_check__<enc>__f64.csv` and the R1b intercept summaries. If it
  does not, the pipeline differs from R1b, and that is found out before anything else.
- **H2, harness correctness.** On `random` with the `abs` score, marginal coverage pooled over folds
  is within 0.02 of 0.90 for every task-encoder cell. If it is not, the conformal implementation is
  wrong.
- **H3, disjointness.** Assert per fold that $T$, $C$ and $E$ are disjoint on (sample id, barcode),
  and that the scaler and PCA were fit on $T$ only.
- **H4, engineering.** Explicit parquet schema; summaries written first; crc32 seeds; provenance
  with config hash and `pythonhashseed`; a two-fold, one-task smoke run before any full job.

An H1 or H2 failure stops work and is reported. That is the one in-interval stop condition.

### 4.3 A1. Marginal coverage across designs (one to two days; gate)

**Why.** This is the first coverage table across designs and the core of Topic A. Its shape is the
result: where coverage holds, where it fails, and by how much.

**Run.** The A0 harness on all ten tasks, all 12 encoders, four designs, two scores, fanned out as
one job per encoder. Memory is sized from `sacct` on R1b, whose peak for head fitting was 16.7 GB
(`docs/WAYS_OF_WORKING.md`), so 24 GB and 4 CPUs is the honest ask, with a generous wall and a
harness ceiling set from queue time plus runtime rather than from runtime.

**Predictions, written before running.**

1. `random` at nominal for every task and encoder. This is H2.
2. `patient` and `donor` under-cover, worst where the shift is largest, on PRAD and SKCM patient
   folds, which are session folds, and on COAD under shipped labels. COAD improves under `donor`.
3. Coverage at or near nominal under `donor` only in folds where `calibration_unit = donor`; folds
   calibrated at slide or block level under-cover.
4. `slide_out` sits between `random` and `donor`, and folds whose calibration slide shares the test
   slide's donor do better than folds where it does not.
5. Under-coverage is larger for weaker encoders in absolute terms, but the ordering across designs
   is the same for every encoder.
6. IDC under audited labels (three donors) under-covers more than IDC under shipped labels, because
   the shipped folds leak the partner section.

**Report** the coverage table beside the benchmark's Pearson table for the same encoders and tasks,
the calibration-unit table, and predictions against outcomes, with the "what was not checked"
section. Then stop.

### 4.4 A2. Conditional coverage and the anatomy of failure (one day; no gate)

**Why.** Marginal coverage says whether intervals fail; this says where and how. Two questions. Is
the failure concentrated in some slides, sessions or genes, or diffuse? And is a failing interval
centred wrong, a level error, or too narrow, a scale error? Round 2's $R^2$ ladder found the
remaining deficit after an intercept to be a slide-level mean shift plus a scale error, so this
stage asks whether the coverage failure has the same anatomy.

**Script.** `code/scripts/round3_a2_conditional.py`, reading A1's per-gene parquets and per-slide
tables plus covariates. No refitting.

**Strata.** Test slide; `resolution_group` and session (PRAD patient 2);
`cal_shares_session_with_test`; predicted-value decile within task; gene; neoplastic-fraction
tertile of the test spot, from `instrumentation/morphology_v2/`; `donor_label_status`.

**Level-versus-scale decomposition** per (test slide, gene) under `patient`, `donor`, `slide_out`:

- miss asymmetry $a = (\text{miss}_{\text{above}} - \text{miss}_{\text{below}}) /
  (\text{miss}_{\text{above}} + \text{miss}_{\text{below}})$, where near $\pm 1$ means the interval
  is centred wrong;
- standardised slide offset $b_s / s_y$ with $b_s = \bar y_s - \bar{\hat y}_s$ on the test slide,
  which uses test labels and is labelled in the report as a diagnostic rather than a method;
- oracle width ratio $w^\star / \hat w$, with $w^\star$ the half-width that would give exactly 90%
  coverage on the test slide and $\hat w$ the calibrated half-width, where above 1 means too narrow;
- a regression of the coverage shortfall on $|b_s| / s_y$ and $\log(w^\star / \hat w)$ across
  slides, reporting the shares.

**Per-gene join.** Spearman, within task, between gene-level coverage shortfall under `donor` and
R7's per-gene `random − patient` from `results/round2/R7_pergene/`.

**Predictions.** Shortfall under `donor` is mostly level, meaning asymmetric misses and large
$|b_s|$, consistent with the ladder. Gene-level shortfall correlates positively with the per-gene
split penalty. Coverage is worse for spots in the predicted-value tails. Session-unsupported folds
on PRAD and SKCM are the worst stratum.

**Outputs.** `results/round3/A2_conditional/a2_by_stratum.csv`, `a2_level_scale.csv`,
`a2_pergene_join.csv`, and one figure `fig_a2_anatomy.png`.

### 4.5 A3. Weighted conformal under slide and session shift (two days; gate)

**Why.** Round 2 measured that the features move between slides and sessions while the expression
does not. That is the covariate-shift case, and weighted conformal (Tibshirani, Barber, Candès,
Ramdas 2019) is the method built for it: it reweights calibration scores by the density ratio
$w(z) = p_{\text{test}}(z) / p_{\text{cal}}(z)$. It also has a known failure, no calibration
support, which PRAD's and SKCM's patient folds create. This stage tests both.

**Script.** `code/scripts/round3_a3_weighted.py <encoder>`, on the A0 harness, designs `patient`,
`donor`, `slide_out`, scores `abs` and `scaled`, encoders `hoptimus0`, `uni_v2`, `resnet50`, and
`random` as the control where weights should be near 1.

**Weight estimators.**

- **W1, embedding classifier.** Per fold, logistic regression on the PCA-256 features from the same
  PCA fit on $T$, class-balanced, L2 with a fixed $C$, trained to separate $C$ (label 0) from $E$
  (label 1) using features only. $w(z) = \frac{\hat p(1 \mid z)}{\hat p(0 \mid z)} \cdot
  \frac{n_C}{n_E}$, clipped at the 99.5th percentile of the calibration weights, recording the
  clipping rate and the classifier's AUC.
- **W2, covariate weights.** Ratio of test to calibration proportions within cells of
  (`resolution_group`, session where defined). A test cell absent from calibration has no finite
  weight, so the fold is flagged `no_support` and falls back to unweighted, which is reported.
- **W3, hierarchical arm.** Only if the oversight chat's literature memo specifies one before the
  interval starts. Otherwise a placeholder column.

**Weighted quantile.** For each test point,
$\hat q = \inf\{ q : \sum_{i \in C} \tilde w_i \mathbf{1}[s_i \le q] \ge 1 - \alpha \}$ with
$\tilde w_i = w(z_i) / (\sum_{j \in C} w(z_j) + w(z_{\text{test}}))$, the test point's own weight in
the normaliser. Calibration scores are sorted once per fold and cumulative sums used.

**Calibration-support diagnostic.** Effective sample size per test slide,
$n_{\text{eff}} = (\sum_i w_i)^2 / \sum_i w_i^2$ over calibration spots, reported as the median over
the slide's test spots.

**Acceptance.** On `random`, weighted coverage equals unweighted within 0.005 and the classifier AUC
is near 0.5. Weights are positive and finite after clipping. On a fold whose test session is absent
from calibration, $n_{\text{eff}}$ collapses, and the value is reported.

**Predictions.** Reweighting restores coverage towards nominal where $n_{\text{eff}}$ stays high
(slide-out on PRAD patient 2, donor folds on CCRCC, IDC's TENX pair) and does not where it collapses
(PRAD and SKCM patient folds). Coverage gain is monotone in $n_{\text{eff}}$. W1 beats W2 where the
shift is within a covariate cell, at slide level, and the two agree where it is between cells. The
scaled score narrows intervals at matched coverage.

**Outputs.** `results/round3/A3_weighted/a3_by_task.csv` with weighting in {none, W1, W2, W3},
coverage, width, interval score, `neff_median`, `clip_rate`, `auc`, `no_support` count;
`a3_by_slide.csv`; `fig_a3_coverage_vs_neff.png`.

A2 and A3 are reported together, with predictions against outcomes, and then work stops.

### 4.6 A4. Adaptive scores and the model-based comparator (two to three days; no gate)

**Why.** Two comparisons the paper needs. Width at matched coverage across scores, since a wide
interval that covers is not useful. And whether a model-based predictive distribution, the negative
binomial that round 1 settled on, is calibrated across designs, and what conformalising it does.
This stage also measures the conditional dispersion the round-1 review asked for.

**Script.** `code/scripts/round3_a4_scores.py <encoder>`, three encoders, all tasks, the A0 designs.

**CQR.** `QuantileRegressor(quantile=q, alpha=0, solver='highs')` on PCA-256 for
$q \in \{0.05, 0.95\}$ fit on $T$, conformalised with
$s_i = \max(\hat q_{0.05}(x_i) - y_i,\; y_i - \hat q_{0.95}(x_i))$ (Romano, Patterson, Candès 2019).
Each task-encoder fit is time-boxed at 20 minutes; if exceeded, $T$ is subsampled to 20,000 spots
and that is recorded.

**Negative-binomial head.** Per gene on raw counts, a Poisson GLM with log link on PCA-256
(`PoissonRegressor`, small L2) for $\hat\mu(x)$, then an NB2 dispersion per gene by the moment
estimator on $T$'s Pearson residuals,
$\hat\alpha_g = \max\!\left(0, \frac{\sum (y - \hat\mu)^2 - \sum \hat\mu}{\sum \hat\mu^2}\right)$.
Predictive distribution $\text{NB}(\hat\mu(x), \hat\alpha_g)$. Report the central 90% interval on the
count scale mapped to $\log(1+y)$, its coverage, the PIT values
$F(y; \hat\mu, \hat\alpha)$ randomised for discreteness, the log score, and $\hat\alpha_g$ beside the
marginal Fano factor from `results/tailored/counts/count_diagnostics.csv`. Library convergence flags
are not trusted; the fitted deviance is checked and failures recorded, as round 1 did.

**Conformalised NB.** Score $s_i = |F(y_i; \hat\mu_i, \hat\alpha) - 0.5|$ on $C$; the calibrated
interval is the NB quantile band at $0.5 \pm \hat q$.

**Acceptance.** On `random`, the NB PIT histogram is close to uniform, with the KS statistic
reported, and CQR coverage is at nominal.

**Predictions.** NB intervals under-cover under `donor` in the same pattern as the conformal ones,
and conformalising restores marginal coverage. CQR and `scaled` are narrower than `abs` at matched
coverage, most on the Xenium tasks where variance depends strongly on the mean. Conditional
dispersion is well below the marginal Fano factor but far from zero.

**Outputs.** `results/round3/A4_scores/a4_scores_by_task.csv` with score in
{abs, scaled, cqr, nb, nb_conformal}, `a4_nb_dispersion.csv`, `a4_pit.csv`,
`fig_a4_width_at_coverage.png`.

### 4.7 B1. Prediction-powered inference with donor-clustered variance (two days; no gate)

**Why.** Topic B's claim is that inference on predicted expression can be valid if the variance
respects the dependence, and that the gain from predictions is real but bounded. Round 2 measured
the between-donor variance share and derived the consequence: with $m$ spots per donor and
between-donor share $\rho$, the variance of a mean is inflated by $1 + (m-1)\rho$ relative to the
i.i.d. formula, and the effective sample size is about $n_{\text{donors}} / \rho$. This stage builds
the estimator and the three variances and shows the difference on real data.

**Script.** `code/scripts/round3_b1_ppi.py`. Inputs are predictions from the A1 `donor` design, so
every spot is predicted by a head that never saw its donor and cross-fitting holds; measured
$\log(1+y)$; and `instrumentation/morphology_v2/` covariates.

**Estimands**, per task and gene $g$, with $m$ the standardised mean nuclear area of the spot:

- $\theta_3$, primary: the slope of $\log(1+y_g)$ on $m$ over the population of spots,
  $\theta_3 = \text{Cov}(m, \log(1+y_g)) / \text{Var}(m)$.
- $\theta_2$: difference in mean $\log(1+y_g)$ between neoplastic-dominant spots, fraction above
  0.7, and stromal-dominant spots, below 0.3.
- $\theta_1$, the motivating example only: the correlation of mean nuclear area with raw GATA3 count
  on IDC, per slide and pooled.

Two population definitions, both reported: spot-weighted, the mean over all spots of the task, and
donor-weighted, the mean over donors of the donor-level value, which is the one whose target
population is donors.

**Data split.** Labelled set $L$ is a subset of donors with measured expression; unlabelled set $U$
is the remaining donors, for which only the predictions are used.

**Estimators.** The classical estimator on $L$ alone, and the prediction-powered estimator in the
estimating-equation form (PPI++, Angelopoulos, Duchi, Zrnic 2023), solving

$$\frac{1}{N}\sum_{i \in U} \psi(\hat y_i, m_i; \theta) + \frac{1}{n}\sum_{i \in L}\big[\psi(y_i, m_i; \theta) - \psi(\hat y_i, m_i; \theta)\big] = 0,$$

with the power-tuning parameter $\lambda$ estimated as in PPI++ and reported. For $\theta_3$ and
$\theta_2$, $\psi$ is linear in the outcome, so this reduces to the plug-in estimate on $U$ plus the
rectifier on $L$.

**Variance estimators**, for both the classical and the PPI estimator:

- (a) spot i.i.d., the default in the PPI papers;
- (b) donor cluster-robust: sum the influence-function contributions within each donor, take the
  variance across donors with the $G/(G-1)$ correction, separately for the $U$ and $L$ terms since
  the donor sets are disjoint, and use a $t$ reference with $G - 1$ degrees of freedom;
- (c) donor bootstrap: resample donors with replacement within $U$ and within $L$, 500 draws,
  percentile interval.

**Tasks and settings.** CCRCC is the powered case with 24 donors, labelling 6, 8 and 12.
LYMPH_IDC has four donors, labelling 2. PRAD has two donors over 23 slides and is the expected
failure case with one donor degree of freedom; it is run and reported as such. IDC carries
$\theta_1$ as illustration. Three encoders, `hoptimus0`, `uni_v2`, `resnet50`, plus a
permuted-predictions arm as the deliberately useless predictor.

**Acceptance.** With $U$ empty the PPI estimate equals the classical one exactly. With predictions
equal to the measured values the PPI estimate equals the full-data value exactly. With one spot per
donor, (b) equals (a). The permuted predictor's PPI interval still covers, and is at least as wide
as the classical one.

**Outputs.** `results/round3/B1_ppi/b1_estimates.csv` with task, gene, estimand, population,
encoder, n_L_donors, n_U_donors, theta_full, theta_classical, theta_pp, lambda, se_iid, se_cluster,
se_boot and width ratios; `fig_b1_intervals.png`, showing $\theta_1$ per IDC slide with spot-level
against donor-level intervals, and $\theta_3$ on CCRCC by variance estimator.

### 4.8 B2. Semi-synthetic coverage (one to two days; end-of-round report)

**Why.** B1 is one partition. Validity is a statement about repeated sampling, so this stage repeats
the partition many times, treating the full-data value as truth, which is R5c's masking design
applied to donors. This is what turns B1 into a claim.

**Script.** `code/scripts/round3_b2_semisynthetic.py`. For each task and each $n_L$ from B1's
settings, draw 200 random labelled-donor sets with crc32 seeds, compute classical and PPI intervals
under the three variance estimators, and record whether each covers the full-data value. Also a
slide-masking variant on PRAD, masking whole slides within the two donors, to show the $G = 2$
failure.

**Report** empirical coverage at nominal 0.90, mean width, and the PPI-to-classical width ratio as a
function of encoder quality, its Pearson on the task, and $n_L$, for each estimand and population
definition.

**Predictions.** Spot i.i.d. intervals cover far below 0.90 for both estimators. Donor
cluster-robust intervals cover near 0.90 for $n_L \ge 8$ and below for $n_L = 4$ or 6 unless the $t$
reference is used, and the donor bootstrap behaves similarly. The PPI width ratio is below 1 only
for the better encoders and approaches 1 as the estimand's between-donor variance share grows,
because predictions on unlabelled donors cannot reduce the donor-level variance in the labelled
rectifier. The permuted predictor's ratio is at or above 1 everywhere.

**Outputs.** `results/round3/B2_semisynthetic/b2_coverage.csv`, `b2_width_ratio.csv`,
`fig_b2_coverage.png`. The end-of-round report covers A4, B1 and B2, plus an escalations section and
the full predictions-versus-outcomes table for the round.

### 4.9 D0. Inventory of full HEST-1k and the expansion proposal (one day, capped at one day)

**Why.** The benchmark subset is 72 samples with at most 24 donors in a task, one lab per task, and
50 genes chosen with test spots. The project needs an institution contrast, donors in the tens to
hundreds, and gene lists chosen without test data, none of which the subset has. Full HEST-1k has
them. The whole archive is over 2 TB, almost all of it whole-slide images the pipeline does not need
once patches exist, so the plan is a designed subset and selection comes before download.

**Inputs.** HEST's metadata table already on disk, `HEST_v1_1_0.csv`, read by R5b, checking the
HuggingFace page for a newer release and recording which version is used; and the HuggingFace file
listing of `MahmoodLab/hest` for per-sample sizes of `patches/`, `st/`, `cellvit_seg/` and
`metadata/`. Listing only, no download.

**Script.** `code/scripts/round3_d0_inventory.py`. Writes
`results/round3/D0_inventory/hest_inventory.csv`, one row per sample with organ, species,
technology, oncotree, cohort or dataset title, HEST patient label, pixel size, spot count and bytes
per component; and `expansion_candidates.csv`, one row per candidate set with the samples it
contains and the counts of samples, HEST-labelled patients, cohorts and labs, and total bytes.

**Sets to propose**, each with a stated selection rule and its size.

- **Institution set.** One organ and one technology with at least three distinct labs, meaning
  cohorts from different generating institutions rather than merely different download sources, the
  IDC lesson in `docs/HEST_replication_review.md` § 5.4, and at least three donors per lab. Human
  breast on Visium and brain on Visium are the review's candidates; propose whichever the table
  supports, with alternatives.
- **Donor-power set.** The organ and technology combination with the most distinct HEST-labelled
  donors, for Topic B.
- **Platform-pair set.** Tissues profiled on more than one technology, ideally the same block on
  Visium and Xenium, for a platform-shift axis.

For each set record how many samples carry `resolution_uncertain`, how the HEST patient labels look
(repeated labels across cohorts, missing labels), and any sample already in the benchmark. Report
the storage ask against the current `/work` quota.

**Acceptance.** Every benchmark sample appears in the inventory with the same metadata the benchmark
used. The three sets' sizes sum from the listing, not from an estimate. The proposal goes into the
A1 report, and nothing is downloaded.

### 4.10 D1 to D4. Download, embed, audit, and measure lab shift

**D1, download** (after Nicolas approves the sets; half a day of wall time plus transfer).
`snapshot_download` on `MahmoodLab/hest` with `allow_patterns` restricted to the approved sample ids
under `patches/`, `st/`, `cellvit_seg/` and `metadata/`. No `wsis/`. Target
`/work/users/w/e/weiyang/hest_replication/hest_ext/<set>/`, with a `PROVENANCE.txt` naming the
HuggingFace revision and the sample list. Check `quota` before and after. Verify every expected file
is present and that patch counts match the expression files' spot counts, as Stage 1 did for the
benchmark.

**D2, embeddings** (GPU; one job per encoder per set). `hoptimus0`, `uni_v2`, `resnet50` only. Use
the benchmark's own extraction path so embeddings are cached per sample under
`embeddings_ext/<set>/<encoder>/` and a killed job resumes. Check `sinfo` for the current GPU
partitions, since the queue was saturated in round 1, so submit early in interval 2, and size the
wall from the round-1 actuals per sample. Record the TRIDENT commit, which must be the pinned one.

**D3, label audit** (reading; capped at two days). For every sample in the approved sets, record
donor, generating lab, scanner or session where stated, and technology, from the source, meaning the
GEO record, the 10x page or the publication's methods, not from HEST's fields, with
`donor_label_status` and a new `lab_label_status`, in
`results/round3/D3_audit/donor_lab_audit_ext.csv` with the same column conventions as
`results/round2/R5b_audit/donor_audit.csv`. No grouping by donor or lab happens before this file
exists. The lab field is expected to need it, since the benchmark's patient field was wrong in two
tasks.

**D4, lab-shift decomposition on the institution set** (interval 3).
`code/scripts/round3_d4_lab_decomposition.py`, extending `round2_split_v4.py` with a `lab_out` arm,
testing on one lab and training on the others, size-matched, alongside `random`,
`blocked_buffered`, `slide_out` and `donor_out`. Target genes for the set are chosen on training
samples only, per fold, with R2's reproduction check as the template. Report the chain of terms per
gene set and, before naming the lab term, the written list of everything that differs between labs:
scanner, protocol, resolution, tissue preparation, donor population. Rerun the R4 probes with lab as
the target. This is the first measurement of institution shift with donor and slide separated, and
it is the input to round 4's Topic A under lab shift.

**Predictions.** The lab term is at least as large as the patient-identity term on the benchmark,
and it is not explained by tissue composition, so the morphology adjustment removes a minority of
it. Lab is decodable from embeddings at well above chance under spatial-block CV, as GLMP found.
Some of HEST's lab or donor labels in the sets are wrong.

---

## 5. Time and compute

| stage | days | jobs |
|---|---|---|
| S0 | 0.5, cap 1 | none |
| A0 | 1 to 2 | smoke jobs only |
| A1 | 1 to 2 | 12, one per encoder |
| A2 | 1 | 1 |
| A3 | 2 | 3 |
| A4 | 2 to 3 | 3, CQR time-boxed |
| B1 | 2 | 1 to 3 |
| B2 | 1 to 2 | 1 to 3 |
| D0 | 1, cap 1 | none |
| D1 | 0.5 plus transfer | none |
| D2 | queue-bound | 3 per set, GPU |
| D3 | 1 to 2, cap 2 | none |
| D4 | 2 | 3 |

About two to three weeks of wall time with the gates. Head fitting is minutes per encoder per fold,
and the A1 volume of 12 encoders by 29 folds by four designs by repeats is well under R3's 47-hour
actuals. Ask for the wall the work needs, do not chase backfill, set harness ceilings from queue
time plus runtime, and record the partition the job actually ran on.

---

## 6. Repository practice for this round

- **Layout.** `code/scripts/round3_*.py`, `results/round3/<STAGE>/`, `docs/round3_*.md`,
  `docs/decisions/`. Figures for the next deck under `figures/deck/` as `fig08_` onward, rendered by
  scripts under `code/figures/`, numbers read from files, and added to
  `results/summary/deck_numbers.csv` by `build_deck_numbers.py`.
- **Only current results in the repository.** When a result is superseded, it moves to a
  `superseded/` subfolder beside its replacement, or to the root `superseded/` for root-level files,
  never deleted, and the commit message says so. Every file present is current.
- **Working documents live in `docs/`.** Stage reports are written once and frozen; corrections go
  in the next report and in the README. `docs/README.md` is updated whenever a document is added.
- **Provenance.** `PROVENANCE.txt` per output directory with job ID, partition actually used, node,
  date, commit, command line, config hash with the config it hashes, and `pythonhashseed`.
- **Writes.** Explicit `pa.schema` on every parquet; summaries and acceptance tables before bulk
  tables; never pipe a long job through `tail`.
- **Parallel work.** One writer per file. If several workers must contribute, each writes its own
  fragment and a merge step with collision reporting produces the shared file.
- **Commits.** Messages through a file, `git commit -F`. A message that summarises a gate states the
  full table or points to the file that does. Tags `round3-A1`, `round3-A3`, `round3-final`.
- **Documents.** Run the numeric-claim sweep over the README and `docs/round3_*.md` before each
  report. Scope for round 3 is the round-3 documents plus the README; the round-2 documents are not
  re-swept unless edited.

---

## 7. Caps

S0 is capped at one day. Any checker or tooling work is capped at half a day per interval. Triage of
the numeric-claim sweep is capped at two hours per report. A false failure that blocks a handover is
fixed in the checker with a fixture, time-boxed at half a day, and anything beyond that is reported
as a limitation rather than fixed. D0 is capped at one day and D3 at two. Anything that is not
analysis and is not in this plan is reported as a proposal and not done.

---

## 8. Decision boundaries

**Decided alone.** Script structure; seeds; the exact calibration fraction within 20 to 30%; block
grid and buffer within the R3 ranges; clipping percentile within 99 to 99.9%; bootstrap counts;
which additional encoders to include beyond those named; job sizing.

**Reported as an escalation inside the interval, then work continues.** Any change to a design's arm
definitions or to the calibration-unit rule; any fold where the harness cannot produce a calibration
set; any new property of the benchmark found along the way; any per-task result that reverses a
round-2 sign. The exception is an H1 or H2 failure in A0, where work stops and reports immediately,
since nothing downstream is interpretable.

**Escalated to Nicolas.** The D0 proposal, meaning which sets and how much storage, before any
download; any download beyond the approved sets, including whole-slide images; anything that would
be sent to the HEST authors, so `docs/hest_bench_issue_draft.md` stays unsent; anything touching the
scientific framing of the two topics; and STFlow, which stays deferred.

---

## 9. Report format

After each gate, in this order: stage and status; what was run, meaning scripts, commits, job IDs,
partitions, wall times and peak memory from `sacct`; acceptance checks with the actual numbers and
file paths; for every design and every weighting, the list of variables that differ between its
arms, written out; predictions against outcomes, as a table; results, with numbers quoted from files
with paths and dispersion beside every mean, and paths rather than pasted tables for anything over
20 rows; discrepancies, open questions and escalations; what was not checked; proposed next step.

Prose stays plain. No em-dashes, no colon-then-explanation constructions, maths as LaTeX. Numbers at
the precision the comparison needs, with the relative scale stated; full precision stays in the
files.

---

## 10. Open items carried into the A1 report

Two defects in the round-2 document tooling, found while re-reading it before the first job. Both
are reported rather than changed silently, per § 4.1 item 1.

1. The sweep command printed in `docs/WAYS_OF_WORKING.md` omits the `--derived` and `--always`
   arguments that `code/scripts/sweep_table.py` passes, so the command as printed does not reproduce
   the gate that closed round 2. Run as printed over the README and the current `docs/*.md`, it
   reports substantially more unresolved claims than the full invocation does, and the residual under
   the full invocation is concentrated in one document.
2. A derived-claim formula that cites a gitignored parquet cannot resolve in a clone of the
   repository, so the gate is only fully reproducible where those working files exist. This is a
   property of the split between committed summaries and uncommitted bulk tables, not a defect in
   any document.

Numbers for both go in the A1 report, read back from the sweep output at the time it is run.

Four more found while building the task-definition files, all recorded here and reported rather
than acted on beyond what is noted.

3. **The `slide_out` design is degenerate on more tasks than the handoff's list implies.** The
   handoff § 6.2 names PRAD, COAD, READ, LYMPH_IDC and IDC-audited as the multi-slide tasks that
   carry `slide_out`. Read back from the task files, eight of the eleven have exactly one slide per
   donor, including COAD and LYMPH_IDC, so on those `slide_out` and `donor` are the same partition
   and the arm adds nothing. The three where the design is genuinely distinct are PRAD (23 slides,
   2 donors), READ (4 slides, 2 donors) and IDC-audited (4 slides, 3 donors). The task files
   enumerate `slide_out` folds everywhere, which is harmless; `results/round3/task_defs/task_def_validation.csv`
   carries a `slide_out_equals_donor_design` column marking the eight. Under § 8 this is a change
   to a design's arm definitions, so it is an escalation: A1 runs `slide_out` where it is not
   degenerate and the report says so, rather than reporting eight duplicate rows as a result.
4. **COAD's TENX111 spot count disagrees between two sources in the repository.** The AnnData has
   6,138 rows against `spots_under_tissue` 6,643 in `sample_metadata.csv`, a difference of 505.
   The task files carry the AnnData count, which is also the count round 2's per-gene table was
   computed on. Which of the two is right is not resolved here. This is a new property of the
   benchmark found along the way, so § 8 makes it an escalation.
5. **`lab` in the benchmark task files is a cohort title, not an audited institution.** It is the
   `dataset_title` column of `sample_metadata.csv`, copied verbatim, and `lab_label_status` is
   `unverified` on all 72 samples. By that column IDC and PAAD carry three distinct values and COAD
   and LUNG two, which does not match the handoff's description of one lab per task. Nothing is
   grouped by lab before D3 audits it, so this changes no round-3 result; it is recorded because
   the D4 lab term will be read against it.
6. **Three tasks have no verified donor label at all.** LUNG, PAAD and SKCM are `unverifiable` on
   every sample, and COAD is `contradicted` on three of four. The `donor` design still runs on
   them, since `donor_id` is the audit's best reading, but a donor-design coverage number on those
   tasks rests on labels the audit could not confirm, and the A1 table carries
   `donor_label_status` so that is visible rather than implied.

---

## 11. References for the methods

- Tibshirani, Barber, Candès, Ramdas. Conformal prediction under covariate shift. NeurIPS 2019.
- Barber, Candès, Ramdas, Tibshirani. Conformal prediction beyond exchangeability. Annals of
  Statistics 2023.
- Romano, Patterson, Candès. Conformalized quantile regression. NeurIPS 2019.
- Lei, G'Sell, Rinaldo, Tibshirani, Wasserman. Distribution-free predictive inference for
  regression. JASA 2018, locally weighted conformal.
- Angelopoulos, Bates, Fannjiang, Jordan, Zrnic. Prediction-powered inference. Science 2023.
  Angelopoulos, Duchi, Zrnic. PPI++. arXiv:2311.01453. Zrnic and Candès.
  Cross-prediction-powered inference. PNAS 2024.
- Hierarchical conformal and PPI under clustering: supplied by the A1 decision memo, and listed in
  § 12.3 below.

---

## 12. Interval 2, transcribed from the A1 decision memo

Transcribed from `docs/decisions/round3_A1_decisions.md` (22 September 2026) before anything in it
was run, as the memo and Nicolas's standing rule both require. Where this section and §§ 3 to 8
above differ, this section governs, because it is the later instruction. §§ 3 to 8 are left as
transcribed at the start of the round, since they are the record of what the handoff said.

### 12.1 The gate, and what it opened

- **A1 is accepted.** Interval 2 opens on receipt of the memo. Nothing in the A1 report is
  withdrawn; the oversight review read the same files differently in places and those readings
  change A2 and A3.
- **D1's second condition is met.** Nicolas approved the expansion on 22 September with the sets
  in § 12.6 and stated that storage is not a constraint on Longleaf. D1 runs without waiting for
  anything further.
- **Remaining gates are A3 and B2.** The gate rule, restated in the memo in the wording Nicolas
  approved: report-and-wait means that no stage after the gated stage starts until the oversight
  chat has reviewed the report and replied; every stage, not only the dependent or expensive ones;
  nothing after the gate is set up, staged or piloted. Inside an interval there are no interim
  reports and no interim stop conditions; anything that would have halted work is handled under the
  decision boundaries, recorded in an Escalations section of the next report, and work continues.
  Contact with anyone outside the project is never this session's decision.
- **`slide_out` is defined only on PRAD, READ and IDC under audited labels.** The handoff's
  multi-slide list was wrong for COAD and LYMPH_IDC. § 4.2's design table is corrected in place.
- **Job sizing for every interval-2 job: 16 GB on 4 CPUs**, from A1's peak of 11.98 GB in
  `results/round3/A1_coverage/a1_job_accounting.csv`. Wall as the
  work needs, harness ceiling from queue time plus runtime, the partition actually used recorded.

### 12.2 How the oversight review reads A1, and what each reading changes

1. **The calibration-unit table mixes two mechanisms, and $K$ is the missing column.** $K$ is the
   number of calibration units per fold. Mechanism (a) is too few units at the right level: in every
   task except CCRCC and PRAD, calibrating at donor level means calibrating on one donor, so fold
   coverage is a unit-level draw that scatters rather than a systematic shortfall. Mechanism (b) is
   calibration below the level of the test unit: in the two-sample tasks and COAD's fold that trains
   on TENX111 alone, calibration scores are within-slide residuals and test scores are new-slide
   residuals, which fails systematically and cannot be repaired inside those tasks. The arithmetic
   bounding (a): with one exchangeable score per unit, split conformal at level $1-\alpha$ needs
   $K \ge (1-\alpha)/\alpha$ for a finite interval, which is $K \ge 9$ at $\alpha = 0.1$ and $K \ge 4$
   at $\alpha = 0.2$. No benchmark fold clears the first. This makes track D a Topic A need too.
   **Changes:** A2 adds the experiments that separate (a) from (b), items A2b and A2c in § 12.4. The
   COAD recovery of 0.145 is re-read as a change in both labels and fold structure, not labels alone.
2. **`scaled` under `random` is a conditional-coverage finding.** Its slide-mean coverage is
   0.898 to 0.902 on every task with across-encoder sd under 0.001, where `abs` varies across
   slides. **Change:** A2a adds the across-slide sd of coverage per task and score under `random`.
3. **`scaled` width explodes under shift,** with means set by a few cells. **Change:** A3 and A4
   carry `scaled_clip`, $\hat\sigma$ clipped to the 1st and 99th percentiles of the calibration
   set's $\hat\sigma$, and every report gives median width beside mean width.
4. **Encoder quality is reported as ranges, not correlations.** The $+0.74$ under `random` is over a
   coverage range of 0.0018, which is noise. Coverage is a property of the calibration design;
   encoder quality changes width. **Change:** A2e reports width by encoder.
5. **The within-PRAD donor-sharing contrast exists** in the 120 folds A1 excluded, where one draw's
   calibration set contains a same-donor slide and another's does not with the training set fixed.
   **Change:** A2d.
6. **PRAD's two folds are not alike.** The fold calibrated on four of patient 2's slides
   under-covers at a narrower width than the fold calibrated on two of patient 1's, so $K$ does not
   explain it; the calibration set's own between-slide spread does. **Change:** an A2a stratum.
7. **The D0 kidney set is not a laboratory contrast.** Its three arms are ccRCC tumour, healthy and
   injured cortex, and stone-disease papilla, so a source term there is tumour against non-tumour
   first. Holding organ, technology, oncotree code and disease fixed, no HEST cell has three
   laboratories with three donors each. The closest cell is breast Xenium IDC, 18 samples from two
   sources with four donors each, disease, platform and preservation fixed. The IDC attribution
   question is reopened by the `TENX97` and `TENX98` siblings. **Changes:** § 12.6 and D4's renaming
   in § 12.5.

### 12.3 Literature supplied

- Lee, Barber and Willett, "Distribution-free inference with hierarchical data", arXiv:2306.06342,
  ACM Journal of Data Science, DOI 10.1145/3786352. Hierarchical conformal prediction (HCP). The
  oversight handoff named the third author as Tibshirani; that was wrong.
- Dunn, Wasserman and Ramdas, "Distribution-free prediction sets for two-layer hierarchical models",
  JASA 118(544), 2023, arXiv:1809.07441.
- Salerno, Wu and McCormick, "Spatially robust inference with predicted and missing at random
  labels", arXiv:2603.11368, March 2026.
- Shirota, "Design-based prediction-powered inference for spatial data", arXiv:2608.10356, August
  2026.
- Cameron and Miller, "A practitioner's guide to cluster-robust inference", Journal of Human
  Resources 50(2), 2015.
- MacKinnon, Nielsen and Webb, "Cluster-robust inference: a guide to empirical practice", Journal
  of Econometrics 232(2), 2023.
- Fisch et al., "Stratified prediction-powered inference for hybrid language model evaluation",
  arXiv:2406.04291, 2024. To be read before B1.

The memo's verdict on the pivot trigger: neither 2026 PPI paper treats units nested in groups or a
donor-level unit of inference, and neither mentions spatial transcriptomics, so there is no pivot.
B1 and B2 position against both by name.

### 12.4 Interval 2 stages

**H0, housekeeping from the A1 escalations, capped at one day in total.**

1. Fix the sweep command printed in `docs/WAYS_OF_WORKING.md` to the one
   `code/scripts/sweep_table.py` runs. Fifteen minutes.
2. `docs/r5_idc_provenance.md`: two hours of triage, then stop. Fix what that allows, banner the
   document as a closed record of a reading task, sweep it under the `historical` class, and put the
   per-document sweep table for the whole docs tree into the A3 report.
3. README known limitations gain two lines: the derived-claim formula in `round2_R3_stage_report.md`
   that cites a gitignored parquet, and COAD `TENX111`'s spot count after a one-hour check of where
   6,643 came from against the AnnData's 6,138, recording both and the likely cause if the hour does
   not settle it.
4. README properties: property 2 (COAD) gains that HEST v1.3.0 corrects the labels upstream, which
   corroborates the audit; property 1 (IDC) gains the sibling observation, marked pending D3.
5. **Determinism.** Rerun the `resnet50` A1 job unchanged and diff every summary CSV and the
   per-gene parquet against the committed run. Report byte-identical or not, and if not, which
   columns moved. This closes H4.
6. This section.

**A2, conditional coverage and the anatomy of failure, two days, no gate.** Everything in § 4.4
stands: strata, the level-versus-scale decomposition, the R7 per-gene join, `fig_a2_anatomy.png`.
Six items are added, of which A2b and A2c are the important ones.

- **A2a, strata, as planned plus three.** The `random` design by test slide for `abs` against
  `scaled`, as the across-slide sd of coverage per task and score. PRAD by fold, with the held-out
  patient, its session structure and its resolution class written out. $K$ as a stratum for every
  fold.
- **A2b, the calibration-unit intervention.** On every task file with at least two units in the
  training pool (CCRCC, LYMPH_IDC, PAAD, COAD under `donor_id`, IDC under both label sets, PRAD,
  READ), for each `donor` fold and three encoders (`hoptimus0`, `uni_v2`, `resnet50`): hold $E$
  fixed; build one proper-training set $T$ and two calibration sets from the same pool.
  $C_{\text{unit}}$ is the A1 calibration set. $C_{\text{block}}$ is buffered spatial blocks (grid 6,
  2.5-pitch buffer, about 20% of blocks) carved out of the slides that form $T$. $T$ is the A1
  proper-training set minus $C_{\text{block}}$, the same for both arms, so head, scaler and PCA are
  fit once per fold. Size-match $C_{\text{block}}$ to $C_{\text{unit}}$ by subsampling the larger.
  Report coverage and width per arm per fold, and the difference with its across-fold dispersion.
  A fold where $T$ falls below 1,000 spots after carving is dropped and listed, not shrunk further.
- **A2c, coverage against $K$ and the between-unit share of the score.** A harness flag writes, per
  (fold, calibration draw, unit, gene), count, mean, variance and the 0.5 and 0.9 quantiles of the
  calibration scores, and the same for the test unit, to `a2_score_moments__<enc>.parquet` with an
  explicit schema. From it, the between-unit share of calibration-score variance per (fold, gene),
  and observed coverage tabulated against $K$ and that share for `abs` over all `patient`, `donor`
  and `slide_out` folds. Then a location-shift simulation, 1,000 replicates per fold, reporting
  simulated expected coverage beside observed per fold and pooled by $K$. Moments come from the A1
  harness rerun in moments-only mode for the three encoders.
- **A2d, donor sharing within PRAD.** From the A1 per-draw files, per PRAD `slide_out` test slide,
  coverage between draws that include a same-donor slide and draws that do not, with the test slide
  fixed, as a paired difference. Then one new arm, `slide_out_cal_other_donor`, calibration drawn
  only from the other donor's slides, three draws, on PRAD, three encoders. The arms differ in
  whether calibration shares the test slide's donor and, in PRAD, in resolution class and session.
- **A2e, width by encoder.** Mean and median `abs` width per encoder per design, joined to benchmark
  Pearson.
- **A2f, the level-versus-scale decomposition as planned,** run separately for block-calibrated and
  unit-calibrated folds.

Outputs under `results/round3/A2_conditional/`: `a2_by_stratum.csv`, `a2_level_scale.csv`,
`a2_pergene_join.csv`, `a2_unit_intervention.csv`, `a2_coverage_vs_K.csv`,
`a2_simulated_coverage.csv`, `a2_prad_donor_sharing.csv`, `a2_width_by_encoder.csv`,
`fig_a2_anatomy.png`, `fig_a2_coverage_vs_K.png`. Summaries before parquets.

**A3, weighted and hierarchical conformal, two days, gate.** § 4.5 stands in structure, with four
changes.

- **Scores.** `abs` primary; `scaled_clip` in place of `scaled`; median width beside mean width.
- **Weights.** W1 as specified. **W1b**, new: the same classifier on the eight `morphology_v2`
  covariates only (nuclear count, mean and median area, five class fractions). W2 as specified.
  **W3 is HCP**: for calibration spot $i$ in unit $k$ with $N_k$ spots, $w_i = 1/N_k$, the test
  point's own weight 1, so each unit and the test point carry $1/(K+1)$; the unit is the fold's
  recorded `calibration_unit`. Run W3 at $\alpha = 0.10$ and $0.20$. Where the weighted quantile is
  infinite, record the interval as infinite, count it, and also report the interval at the largest
  feasible level $1 - 1/(K+1)$, which is the maximum calibration score, with its realised coverage
  against its guaranteed level. **Never substitute a finite interval for an infinite one silently.**
- **Difference lists.** W1 sees everything the encoder represents, including the slide signature;
  W1b composition only; W2 resolution group and session; W3 the unit structure and no features.
- **Acceptance** as specified, plus: on `random`, W3 at $\alpha = 0.1$ has $K$ equal to the spot
  count and reproduces the unweighted interval to $10^{-6}$ in coverage and width.

A3 predictions, quoted from the memo so the report can set outcomes beside them: W1's AUC above 0.9
on every different-slide fold, $n_{\text{eff}}$ under 5% of calibration size, and little coverage
movement except on CCRCC and PRAD `slide_out`; W1b keeps $n_{\text{eff}}$ above 30% and moves
coverage slightly toward nominal, most on IDC and CCRCC; W2 has no support on PRAD and SKCM
`patient`; W3 infinite at $\alpha = 0.1$ on folds with $K \le 8$, finite at $\alpha = 0.2$ on CCRCC,
PRAD's $K = 4$ fold and PRAD `slide_out` with coverage at or above 0.80 and an upper bound near
$0.80 + 2/(K+1)$, the feasible-level fallback covering at or above $K/(K+1)$ in the mean,
and W3 inert on block folds; no weighting repairs the two-sample tasks.

Outputs under `results/round3/A3_weighted/`: `a3_by_task.csv` with weighting in
{none, W1, W1b, W2, W3}, score, $\alpha$, coverage, mean and median width, interval score,
`neff_median`, `clip_rate`, `auc`, `no_support` count, `n_infinite`, `feasible_level`;
`a3_by_slide.csv`; `fig_a3_coverage_vs_neff.png`; `fig_a3_hcp_by_K.png`.

**D3 starts now,** reading, capped at two days, and may run into interval 3. In priority order:
breast Xenium IDC (the eleven `TENX191` to `TENX202` samples, then the seven 10x samples with two
hours on the `TENX95`/`TENX97`/`TENX98`/`TENX99` question); kidney Visium for the Washington
University and Indiana samples; `resolution_uncertain` re-derived from source for every sample in
the two analysis sets; the four held-out kidney samples if time remains. Output
`results/round3/D3_audit/donor_lab_audit_ext.csv`, a citation per row. No grouping by donor, source
or laboratory on expansion data before that file exists.

**D1 and D2.** Covered in § 12.6.

### 12.5 Interval-3 changes, recorded now and specified in full at the A3 gate

- **A4.** Adds `scaled` unclipped against `scaled_clip` as the first comparison, and W3 at
  $\alpha = 0.2$ on CCRCC in the width-at-matched-coverage table.
- **B1.** Uses the harness's calibration-fraction-zero `donor` predictions (the H1 mode), so every
  spot's prediction comes from a head trained on all other donors. Cites the § 12.3 references,
  positions against Salerno et al. and Shirota in its opening paragraph, and derives the parallel
  between the donor-limited effective sample size and the $K \ge 9$ condition.
- **B2.** As planned.
- **D4.** `lab_out` is renamed **`source_out`**, and no report calls it a laboratory term unless D3
  establishes that the sources differ in laboratory and agree in disease, tissue, preservation and
  platform. On the kidney set, a **`population_out`** arm (Sorbonne tumour against Washington
  University non-tumour, both directions), named as a population-shift term with its difference list
  written out. On breast Xenium, `source_out` is a two-arm contrast and described as such. No D4 arm
  on the platform-pair set.

### 12.6 Track D

**Sets, approved.** Verified by this session against `results/round3/D0_inventory/hest_inventory.csv`
before transcription, after removing flagged duplicates; every figure matches the memo.

| set | samples | GB | in benchmark | round-3 use |
|---|---|---|---|---|
| kidney Visium, the whole human cell | 58 | 23.3 | 24 | Topic B's second donor set; Topic A's `population_out` arm; the Washington University against Indiana pair |
| breast Xenium IDC | 18 | 22.9 | 4 | the two-source contrast with disease, platform and preservation fixed; extends IDC from 4 to 18 samples |
| platform-pair | 32 | 25.8 | 5 | none this round; downloaded and left on disk for round 4 |
| union | 105 | 70.3 | 31 | |

The three breast samples `NCBI783`, `NCBI784` and `NCBI785` sit in both the breast Xenium and
platform-pair sets, which is why the union is 105 rather than 108. The kidney cell's four additions
over D0's 54 are `NCBI538`, `NCBI539`, `NCBI540` (KTH, `Treated`) and `TENX71` (a 10x vendor page);
they are downloaded, kept out of every set definition, and left for D3.

Before D1, write the 18 breast ids into `expansion_set_members.csv` as `institution_breast_xenium`
with the selection rule, and the four kidney additions as `kidney_visium_cell_extras` with the reason
each was excluded from the analysis set.

**D1** downloads all 105 in HEST-1k's own layout, including the 31 already in the benchmark, without
reusing the benchmark copies. Order kidney, then breast Xenium, then platform-pair. Four components
only, no `wsis/`. HuggingFace revision and sample list in `PROVENANCE.txt`; filesystem checked
before and after; every expected file verified present; patch counts checked against the expression
files' spot counts.

**D2** embeds the kidney and breast Xenium sets only, 76 samples, with `hoptimus0`, `uni_v2` and
`resnet50`. The platform-pair set stays unembedded. **Anchor check:** for the 24 CCRCC and 4 IDC
samples present in both layouts, the new embeddings from HEST-1k patches must equal the cached
benchmark embeddings for the same encoder to the float32 floor, about $10^{-5}$ relative. If they do
not, the two layouts' patches differ, and that is understood before any expansion result is read.

**What the advisors are told** is Nicolas's to say; this session contacts no one. Every round-3
document that reports a source term states that HEST-1k contains no organ-by-technology cell with
three laboratories at three or more donors each once disease state is held fixed, checked across all
46 cells, so the institution axis this round is a two-source contrast.

### 12.7 The A3 report, and decision boundaries

The A3 report follows § 9's nine items with A2's results in full and D3's status, and adds, as item
4, the difference list for every weighting and for the A2b and A2d arms, plus H0's per-document
sweep table. The sweep runs with the corrected command over the README and `docs/round3_*.md`.
Tag `round3-A3`.

Decision boundaries are § 8's with two additions. An A2b fold whose $T$ falls below 1,000 spots is
dropped and listed. A D3 finding that changes a benchmark donor label is an escalation recorded in
the A3 report and does not change `donor_audit.csv` inside the interval; the round-2 file is frozen,
and a round-3 audit file supersedes it explicitly only if the decision goes that way.

### 12.8 How the interval is cut into parallel tracks

Per Nicolas's standing rule, parallel work goes to sub-agents. The cut, and why it falls where it does:

| track | stages | writes |
|---|---|---|
| Housekeeping | H0 items 1 to 4 | `docs/WAYS_OF_WORKING.md`, `docs/r5_idc_provenance.md`, `README.md`, the per-document sweep table |
| Anatomy | the parts of A2 answerable from A1's committed outputs: A2a's slide, session, resolution, calibration-sharing, gene, `donor_label_status`, $K$, `random` `abs`-against-`scaled` and PRAD-by-fold strata; A2d's paired within-PRAD comparison; A2e; the R7 per-gene join | `a2_by_stratum__anatomy.csv`, `a2_prad_donor_sharing__paired.csv`, `a2_width_by_encoder.csv`, `a2_pergene_join.csv` |
| Mechanisms | H0 item 5, then the parts of A2 that need a harness rerun: A2a's predicted-value decile and neoplastic-fraction strata; A2b; A2c; A2d's new arm; A2f; both A2 figures. Then A3 | the harness, `a2_by_stratum__spot.csv`, `a2_prad_donor_sharing__arm.csv`, and every other A2 and A3 output |
| Expansion | the set-member additions, D1, then D2 with its anchor check | `expansion_set_members.csv`, `hest_ext/`, `embeddings_ext/` |
| Audit | D3 | `results/round3/D3_audit/` |

A2 splits where it does because the A1 per-gene parquet carries coverage and misses per slide and
gene but not the slide offset $b_s$, the oracle width $w^\star$, or anything at spot level, so the
predicted-value, neoplastic-fraction and level-versus-scale analyses need a rerun and the others do
not. The two tracks that both contribute to `a2_by_stratum.csv` and `a2_prad_donor_sharing.csv`
write fragments, and the lead merges them with collision reporting.

A3 goes to the Mechanisms track after A2, rather than to a fresh sub-agent, because the memo says A3
needs A2's per-fold tables and because both stages extend the same harness file. Only one track
edits `code/scripts/round3_a0_harness.py`.

### 12.9 Points in the memo flagged for the A3 report rather than changed

Recorded here so they are not changed silently.

1. **§ 4's opening says D1 and D2 run "once Nicolas approves the sets";** §§ 1 and 6.1 say he has.
   Read as a leftover from an earlier draft; D1 runs.
2. **A3 prediction 4 and consolidated prediction 7 say W3 is infinite at $\alpha = 0.1$ on every fold
   "outside CCRCC's donor design".** By the memo's own condition in §§ 2.1 and 3, a finite HCP
   interval at $\alpha = 0.1$ needs $K \ge 9$, and CCRCC's `donor` folds have $K = 6$, so W3 is
   infinite there too. § 2.1 itself says no fold clears the bar at $\alpha = 0.1$. A3 runs as
   specified and reports the outcome against both readings.
3. **§ 2.1 says "the two task files that clear the bar" at $\alpha = 0.2$ and then lists three
   items,** and CCRCC's `patient` design, with $K = 5$, also clears $K \ge 4$. No effect on any
   stage.
4. **A2c's between-unit share is not estimable from calibration scores alone when $K = 1$,** which
   is most folds, since one unit has no between-unit variance. This session computes the share over
   the $K$ calibration units together with the test unit, labels it a test-label diagnostic in the
   same way § 4.4 labels $b_s$, and uses the same estimate in the simulation. This is a change needed
   to make the item computable, and it is recorded as an escalation.
5. **A2b's $C_{\text{unit}}$ arm is fit on $T$ minus $C_{\text{block}}$,** so it will not reproduce
   A1 exactly and the prediction that unit calibration "reproduces A1" can hold only approximately.
   A third arm is added as an anchor, per the rule that every refit has one arm anchored to the prior
   result: A1's own $T$ with A1's $C_{\text{unit}}$, which must reproduce A1's per-fold coverage to
   floating-point resolution. This adds a check and changes no arm.
6. **§ 4 orders the interval as H0, then A2.** Read as requiring the determinism rerun, which is the
   H0 item that bears on the harness A2 extends, to go first on the harness track, while H0's
   document items run in parallel under Nicolas's fan-out rule. If the memo meant all of H0 first,
   the cost of this reading is that A2 starts some hours earlier than it would have.


---

## 13. Interval 3, transcribed from the A3 decision memo

Transcribed from `docs/decisions/round3_A3_decisions.md` (23 September 2026) before anything in it
was run, as the memo and Nicolas's standing rule both require. The memo answers
`docs/round3_A3_stage_report.md` revision 2 (tag `round3-A3-r2`, commit `5bc4bb3`). Where this
section and §§ 4.6 to 4.10 or § 12.5 differ, this section governs, because it is the later
instruction; those sections are left as they were, as the record of what earlier documents said.

### 13.1 The gate, and what it opened

- **A3 is accepted; interval 3 opens on receipt of the memo.** Nothing in the A3 report is
  withdrawn. The memo's own check of the repository reproduced A2b's arm means and 138-of-138 count,
  the five level-scale groups, the W3 infinite-interval predicate on all 1,932 nominal cells, the
  D2 anchor rows, the determinism diff and the D3 status counts, and found
  `results/round3/A3_report_numbers.csv` in agreement with the primary tables.
- **The remaining gate is the end-of-round report after B2.** The gate rule is unchanged, in the
  wording Nicolas approved: report-and-wait means no stage after the gated stage starts, every stage,
  and nothing after the gate is set up, staged or piloted. Inside the interval there are no interim
  reports and no interim stop conditions; anything that would have halted work is handled under the
  decision boundaries (§ 13.8), recorded in the Escalations section of the end-of-round report, and
  work continues. Contact with anyone outside the project is never this session's decision.
- **Three errors in the A1 memo are acknowledged by the oversight chat:** the W3 parenthetical at
  $\alpha = 0.1$, the "two task files" that listed three, and the mechanism-(a) prediction that A2c
  refuted. § 12.9 items 2 and 3 are closed by this.

### 13.2 The five decisions

1. **IDC `audited` is superseded.** Build `results/round3/D3_audit/donor_audit_r3.csv`: the 72
   benchmark rows of `results/round2/R5b_audit/donor_audit.csv` unchanged except IDC, where `TENX95`
   and `TENX99` receive distinct `donor_id` values and `donor_label_status = verified` citing D3's
   rows; then the 76 rows of `donor_lab_audit_ext.csv` appended. `donor_audit.csv` stays frozen, its
   provenance saying it is superseded. Every round-3 table carrying an IDC `audited` row keeps the row,
   tagged `superseded_label_set`; no further stage runs IDC `audited`.
   `docs/r5_idc_provenance.md` stays frozen, gains a one-line banner pointing to D3 and the memo, and
   its line 47 is not edited. README consequences are H1's (§ 13.4): property 1 withdrawn; the 96%
   `TENX95`/`TENX99` partner confusion re-read as two donors from one laboratory, instrument, panel and
   pixel size three weeks apart, the session signature of finding 3 in a second task; R5c's
   $+0.0652$ kept as a measurement and renamed as the value of a same-laboratory, same-instrument
   slide in the training pool across donors, with IDC's `leak_realised_in_shipped_split` set to
   `False`; READ's $+0.0901$ remaining the only same-specimen replicate figure.
   `docs/hest_bench_issue_draft.md` has its IDC item struck and stays unsent. The deck's `issue1`
   slide is on Nicolas's running list, not this session's.
2. **The D2 layout finding is a property of the public data; no re-embedding.** The 28 anchor
   samples are already embedded from HEST-1k patches, so the expansion is internally consistent. Whether
   a benchmark result moves with the layout is measured by D4's layout anchor (§ 13.7.1), and expansion
   results are set beside benchmark results only through it. README property 11 records the layout
   difference, with the anchor's outcome added when it exists.
3. **The D1 criterion is the subset relation.** Expansion analyses use patched spots only, and
   every expansion task definition records the unpatched fraction per sample. Why HEST drops a spot is
   not pursued this round.
4. **D4 is re-scoped, and no round-3 document carries a laboratory term.** Breast Xenium is one
   laboratory; kidney's two laboratories are separated exactly by tumour status and further by
   preservation, region, instrument and pixel size. The kidney contrast is a population-and-source
   shift, named as such with its difference list. Two limitations go into every document reporting a
   source term and into what Nicolas tells the advisors: HEST-1k has no organ-by-technology cell with
   three laboratories at three or more donors each, and, the stronger, no two-laboratory cell with
   disease held fixed.
5. **A4 absorbs A3's consequences.** W1 and W1b run in no further stage. HCP at $\alpha = 0.2$ on
   CCRCC joins A4's width-at-matched-coverage table from A3's tables, without a rerun. `scaled`
   against `scaled_clip` is A4's first comparison. A4 gains A4b (§ 13.5.2).

### 13.3 How the oversight review reads interval 2

Recorded here; it adds no action beyond what the stage sections below carry.

- **A2b is the interval's result** and goes on the deck as a figure: calibration level, not
  calibration size, sets coverage.
- **Mechanism (a) is refuted as a mean effect.** The small-$K$ account explains fold-level scatter,
  not the unit-calibrated mean shortfall of three to four points, which nothing measured yet explains.
  The best current account is intervals of about the right width with a positive miss asymmetry.
- **The level-scale shares are shares of across-slide variance.** A constant offset is invisible to
  them; the mean $|b_s|/s_y \approx 0.5$ on unit-calibrated slides is large and absorbed by the width.
  Slide-level recentring would buy width, not coverage, hence A4's oracle row.
- **A3 is a clean negative result with its mechanism measured**, including the new finding that
  eight morphology covariates separate slides at a median AUC of 0.90.
- **The predicted-value decile failure is the $R^2$ ladder's scale error seen from the interval
  side**, and A4 reports every score by decile to test it.
- **`INT5` and CCRCC's donor labels** matter for B1, B2 and A4b; H1 item 4 reads the sources, and
  every CCRCC analysis in B1, B2 and A4b runs twice, with 24 donors and with `INT4` and `INT24` merged.

### 13.4 H1. Housekeeping from the A3 escalations (capped at one day in total)

1. The round-3 audit file of § 13.2 item 1, and the `superseded_label_set` tag on every round-3
   table carrying an IDC `audited` row.
2. README: property 1 withdrawn and rewritten per § 13.2 item 1; property 11 added; known limitations
   updated for the D2 layout, the subset relation, the CCRCC labels and the determinism note; the
   `raw_ridge` sentence and everything else untouched.
3. `docs/hest_bench_issue_draft.md`: IDC item struck with a dated note; stays unsent.
4. Two reading items, one hour each: the Immunity paper's patient table for CCRCC's donor count and
   any per-sample donor mapping, and `INT5`'s source record. Recorded in `donor_audit_r3.csv`.
5. `docs/WAYS_OF_WORKING.md` gains three notes: (i) with fairshare near 0.007 jobs start through
   backfill or not at all, so the time limit is about three times the expected runtime, sized from a
   sibling's `sacct`, never a blanket 16 h; (ii) determinism across nodes holds to about
   $3 \times 10^{-6}$ absolute in widths and exactly in every count, and bit for bit on one node, so
   provenance records the node and a byte-identical rerun is a same-node claim; (iii) a provenance
   `commit` field records the working copy's HEAD, not the script that ran, so every job's provenance
   also records the md5 of the script file it executed.
6. This transcription.

### 13.5 A4. Scores, the model-based comparator, and the $K \ge 9$ experiment (three days; no gate)

**13.5.1 A4a.** § 4.6 as specified, with these changes. Scores `abs`, `scaled` (unclipped),
`scaled_clip`, `cqr`, `nb`, `nb_conformal`; three encoders (`hoptimus0`, `uni_v2`, `resnet50`); the
A0 designs; every task file except IDC `audited`. First comparison `scaled` against `scaled_clip`
against `abs`, with the fraction of folds where the lower clip binds. Every score reported by
predicted-value decile per design. Width at matched coverage is the primary table, mean and median
width beside each other, with HCP at $\alpha = 0.2$ on CCRCC `donor` from A3's tables as a row. One
oracle row: the `abs` interval recentred per test slide by $b_s$, with the width that then gives 90%
on that slide; it uses test labels and is labelled a diagnostic. The NB head as in § 4.6 with the
convergence guard, the PIT histogram and KS statistic on `random`, and $\hat\alpha_g$ beside the
marginal Fano factor. CQR time-boxed at 20 minutes per task-encoder fit with the 20,000-spot fallback
recorded. Outputs as § 4.6, with `scaled_clip` added to the score set, plus `a4_by_decile.csv` and
`a4_oracle_recentred.csv`.

**13.5.2 A4b. HCP with $K = 10$ exchangeable donors on CCRCC.** CCRCC, `donor` design, one held-out
donor per fold: 24 folds with 24 donors, and 23 folds with `INT4` and `INT24` merged. From the
remaining pool, 10 donors form $C$ and the rest train, three calibration draws with crc32 seeds. Score
`abs`, three encoders. Four intervals per fold at $\alpha = 0.1$: A1's pooled spot-level quantile; HCP
with group-equal weights (A3's W3); the Dunn-Wasserman-Ramdas one-score-per-group subsample (one
calibration spot per donor, $K + 1 = 11$ exchangeable scores, 200 repetitions, width averaged and
coverage reported per repetition); and, as the control, the same on `random` with $K$ equal to the
spot count. Record the training-set size beside A1's, and, as the anchor, the pooled-quantile
coverage against A1's CCRCC `donor` row. $K = 10$ is fixed and is not a session choice (§ 13.8).
Outputs `results/round3/A4_scores/a4b_hcp_K10.csv` (fold, draw, encoder, method, coverage,
width_mean, width_median, K, n_T, n_C, finite) and `fig_a4b_hcp_K10.png`, coverage against width for
the four methods with A1's point marked.

### 13.6 B1 and B2. As §§ 4.7, 4.8 and 12.5, with four changes

- **Inputs.** B1 uses the calibration-fraction-zero `donor` predictions (the H1 mode). IDC
  $\theta_1$ runs under the four-donor labels of `donor_audit_r3.csv`. CCRCC runs with 24 donors and
  with `INT4` and `INT24` merged, both reported; the same for B2's semi-synthetic partitions.
- **References and positioning** as § 12.3 and § 12.5: the four references, and the positioning
  against Salerno, Wu and McCormick (arXiv:2603.11368) and Shirota (arXiv:2608.10356) in the B1
  report's opening paragraph; Fisch et al. (arXiv:2406.04291) read first and the difference stated.
- **The parallel with A4b.** A short paragraph setting $n_{\text{eff}} \approx n_{\text{donors}}/\rho$
  beside the $K \ge 9$ condition, quoting A4b's result once it exists.
- **No expansion task in B this round.**

B2 as specified: 200 partitions per setting, the slide-masking variant on PRAD, and the end-of-round
report as the gate.

### 13.7 D4. The expansion, re-scoped (two days; inside interval 3)

Every D4 arm runs on HEST-1k-layout embeddings only, on patched spots only, with
`donor_audit_r3.csv` as the grouping source, and the four contradicted papilla samples (`NCBI563` to
`NCBI566`) excluded from any donor unit. Expansion task definitions are written first, in the A0
format, with columns `lab`, `source`, `population`, `instrument_generation`, `preservation`, `region`,
the audit statuses and the unpatched fraction per sample.

1. **The layout anchor, first, and a condition for reading anything else in D4.** CCRCC, 24
   samples, HEST-1k-layout embeddings, three encoders, the A1 harness on `random` and `donor` with A1's
   seeds and rule. Compare per-task Pearson and coverage with A1's committed CCRCC rows. If either moves
   more than predicted, the end-of-round report says so before any expansion number and property 11
   is extended.
2. **The Indiana donor set.** The 23 atlas samples (22 donors; `NCBI701` and `NCBI702` are one
   participant) plus the three single-donor papilla samples, 25 donor units, one laboratory, instrument
   and objective, fresh frozen throughout. 50 target genes chosen on training samples only per fold,
   with R2's reproduction check as the template. The A1 harness on `random`, `donor` (25% rule) and the
   A4b design ($K = 10$; 24 in the pool, 10 calibration, 14 training), `abs`, three encoders, and the
   R7-style per-gene decomposition. Difference list for `donor`: donor, disease (reference, diabetic,
   acute injury), region where stated, section and capture area; not laboratory, instrument,
   preservation or pixel size.
3. **The kidney population-and-source shift.** `population_out` both ways on the 54-sample set:
   train on the 24 Cordeliers ccRCC samples and test on the 30 Indiana non-tumour samples, and the
   reverse, calibration at donor level within the training population, training-only gene selection on
   the intersection panel. Difference list, written before the term is named: tissue state, anatomical
   region, disease, preservation (partly), laboratory, instrument, objective, pixel size and the
   pixel-size provenance flag. Reported as a population-and-source shift, never a laboratory term. The
   R4-style probe with population as the target, with and without the morphology adjustment, which
   uses the shipped CellViT counts and areas per spot with round 2's per-sample geometry calibration.
4. **Breast Xenium, one laboratory, two instrument generations.** Fifteen donor groups; the `donor`
   design at the 25% rule, `abs`, three encoders, target genes on the common panel chosen on training
   samples. Two strata: instrument generation, and disease. Difference list for `donor`: donor,
   disease, block source, instrument generation for some pairs, run date and slide; not laboratory,
   platform, panel or preservation. No source term is reported from this set.
5. **What D4 does not do:** no `lab_out` anywhere; no platform-pair set; no Topic B on expansion
   data; no morphology build beyond the 7.3 probe's inputs.

### 13.8 End-of-round report and decision boundaries

**The end-of-round report** follows § 9's nine items, covering H1, A4, B1, B2 and D4, plus the full
predictions-against-outcomes table for the round (every prediction from the execution handoff and the
two memos, with its outcome), an Escalations section, and a closing section titled "What round 3
established", at most one page, every sentence naming its file. The sweep runs with the corrected
command over the README and `docs/round3_*.md`. Tag `round3-final`, then stop; the round-4 plan is
the oversight chat's to write.

**Decision boundaries** are § 8's and § 12.7's, with two additions: A4b's calibration size is fixed at
$K = 10$ and is not a session choice; and any D4 result that would be read against a benchmark result
waits for § 13.7.1's anchor and is reported beside it or not at all. Jobs are charged to
`rc_htzhu_pi`. Nicolas was added to `rc_tengfei_pi` on 23 September, but at transcription time his
Slurm association did not yet list it, and spending another group's allocation is his decision, so no
job uses it unless he says so.

**Predictions for interval 3**, consolidated in the memo's § 10 and quoted there so the end-of-round
report can set outcomes beside them: eleven rows, A4a (1 to 4), A4b (5), B1 (6), B2 (7) and D4.1 to
D4.4 (8 to 11). They are not restated here, so they cannot drift from the memo's wording.

### 13.9 How the interval is cut into parallel tracks

Per Nicolas's standing rule, parallel work goes to sub-agents. The round-3 audit file comes first,
built by the lead, because the Inference, HCP and Expansion tracks all group by it; everything else
fans out once it exists.

| track | stages | writes |
|---|---|---|
| lead, before fan-out | § 13.4 item 1's audit file; this transcription | `results/round3/D3_audit/donor_audit_r3.csv`, `docs/round3_execution_plan.md` |
| Housekeeping | H1 items 1 (the `superseded_label_set` tags), 2 to 5 | the tag column on committed round-3 tables, `README.md`, `docs/hest_bench_issue_draft.md`, `docs/WAYS_OF_WORKING.md`, the banner on `docs/r5_idc_provenance.md`, and only the status, citation and notes columns of `donor_audit_r3.csv`, never `donor_id` |
| Scores | A4a | `code/scripts/round3_a4_scores.py`, `results/round3/A4_scores/` except `a4b_*` |
| HCP | A4b | `code/scripts/round3_a4b_hcp.py`, `results/round3/A4_scores/a4b_*` |
| Inference | B1, then B2 | `code/scripts/round3_b1_ppi.py`, `code/scripts/round3_b2_semisynthetic.py`, `results/round3/B1_ppi/`, `results/round3/B2_semisynthetic/` |
| Expansion | D4, the layout anchor first | expansion task definitions, `code/scripts/round3_d4_*.py`, `results/round3/D4_expansion/` |

No track edits `code/scripts/round3_a0_harness.py`. Each new script imports the harness unmodified,
as A3 did, so every result stays anchored to A1's folds. A track that finds it needs a harness edit
records that as an escalation and works around it in its own script. As before, sub-agents run no
git command, including read-only queries; the local clone is the only committer.

### 13.10 Points in the memo flagged for the end-of-round report rather than changed

1. **A4b's training size.** § 5.2 says training "falls from 18 to 13 donors". A1's CCRCC `donor`
   folds have 23 donors in the pool and 6 in calibration
   (`results/round3/A1_coverage/a1_calibration_units__resnet50__main.csv`), so they train on 17, and
   the fall is 17 to 13. With `INT4` and `INT24` merged it is 22 in the pool, 10 calibration and 12
   training; the memo fixes $K = 10$ and does not state this case, so it runs at $K = 10$.
2. **The round-3 audit file duplicates 28 samples, and the two rows disagree on all 28.** The 76
   expansion rows include the 24 CCRCC and 4 IDC benchmark samples. On CCRCC, round 2's rows say
   `verified` and D3's say `unverifiable`; the memo carries round 2's rows unchanged, while its § 3.4
   accepts D3's reading. On IDC, the memo corrects `TENX95` and `TENX99`, but `NCBI783` and `NCBI785`
   also differ (round 2 `unverifiable` with per-sample donor ids, D3 `verified` with `NCBI784` and
   `NCBI785` sharing a donor). The file keeps every row as the memo says, adds a `row_origin` column
   (`benchmark_r2` or `expansion_d3`), and lists the 28 pairs and their disagreements in a companion
   file. No row is dropped and no status is chosen between them. Stages that group benchmark tasks use
   the `benchmark_r2` rows, which is the memo's instruction, and those that group expansion sets use
   the `expansion_d3` rows.
3. **The breast instrument-generation stratum.** § 7.4 says "the three Janesick prototype samples
   against the twelve production-instrument samples". The set has 18 samples, 3 of them Janesick, so
   the sample split is 3 against 15; the donor-group split is 2 against 13, because `NCBI784` and
   `NCBI785` share a donor. Twelve matches neither. The stratum is reported both by sample and by donor
   group.
4. **README property 11's citation.** § 2.2 cites `anchor_check_consolidated.csv` for the 6% to 15%
   range, but that file holds only `resnet50`'s rows. The per-encoder range is in
   `results/round3/D2_embeddings/anchor_check__<set>__<enc>.csv` and in
   `results/round3/A3_report_numbers.csv`, which property 11 cites instead.
5. **The `population_out` test set contains the four contradicted papilla samples.** § 7 excludes
   them from any donor unit, and § 7.3's test population is all 30 Indiana samples. They stay in the
   test set as spots, and are excluded from any donor-level calibration or clustering.
