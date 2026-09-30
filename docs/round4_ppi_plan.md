# Round 4, the PPI track, operating plan

Transcribed on 30 September 2026 from `docs/decisions/round4_ppi_track.md` (the oversight chat's
instruction document of the same date, md5 `2857ff9e0d78b8264d501833c5af7480`) before anything in it
was run, as that document and Nicolas's standing rule both require. The source is committed beside
this plan so the transcription can be checked against it. Where this plan and the source differ, the
source governs. Points in the source that look wrong are listed in section 8 and are not changed;
they go into the Q1 report.

The track runs on branch `round4-ppi`, created from tag `round4-data-v2` (commit `9d7277d`). It is
never rebased onto anything else and never merged into `main` by this session. The conformal track
runs at the same time on branch `round4-conformal`.

Originality, stated first as the source asks. The estimator this track builds is the survey-sampling
difference estimator (Mozer, arXiv:2603.19160) and, in its PPI++ form, the generalised regression
estimator, with cluster-level variance as in Särndal, Swensson and Wretman (1992, chapter 8) and
Breidt and Opsomer (2017). It is not new. What is new is its behaviour when the predictor's error has
a cluster-level component and the labelling budget is spent on clusters and units, namely the gain
bound, the allocation between clusters and units with a predictor, the comparison of labelling few
clusters fully against few units in every cluster, and the behaviour with few labelled clusters.

---

## 1. The gates

The track has three gates, at Q1, Q3 and Q5. The gate rule, in the wording Nicolas approved, is that
report-and-wait means no stage after the gated stage starts until the oversight chat has reviewed the
report and replied. Not the dependent stages only, and not the expensive ones only. Every stage.
Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports
and no interim stop conditions; anything that would have halted work is handled under the decision
boundaries (section 5), recorded in an "Escalations" section of the next report, and work continues.
The two exceptions the source names are the Q0 anchor failing and a Q2 or Q3 derivation that does
not close, which are stop-and-report. Contact with anyone outside the project is never this
session's decision.

| interval | stages | ends with | tag |
|---|---|---|---|
| 1 | Q0, Q1 | `docs/round4_ppi_Q1_report.md`, **report and wait** | `round4-ppi-Q1` |
| 2 | Q2, Q3 | `docs/round4_ppi_Q3_report.md` covering Q2 and Q3, **report and wait** | `round4-ppi-Q3` |
| 3 | Q4, Q5 | `docs/round4_ppi_final_report.md`, **report and wait, end of track** | `round4-ppi-final` |

Each decision memo that hands work back is transcribed into this plan, as a new section, before any
work from it runs.

## 2. Conventions for this track

- Scripts are `code/scripts/round4_ppi_*.py`. Results go under `results/round4/ppi/<STAGE>/` in the
  repository and on Longleaf under the project tree `/work/users/w/e/weiyang/hest_replication`.
  Documents are `docs/round4_ppi_plan.md`, `docs/round4_ppi_theory.md`,
  `docs/round4_ppi_estimator_definition.md`, `docs/round4_ppi_Q1_report.md`,
  `docs/round4_ppi_Q3_report.md` and `docs/round4_ppi_final_report.md`.
- Read-only for this track are everything under `results/round3/` and `results/round4/data/`, the
  embeddings, the morphology parquets, the harness (`code/scripts/round3_a0_harness.py`, md5
  `0ad7ae8efe554c1f285e5f384a9fb7f5`, imported unmodified), the audit file, `main`, and the conformal
  track's areas (`results/round4/conformal/`, `code/scripts/round4_conf_*.py`,
  `docs/round4_conf_*.md`). `README.md`, `docs/WAYS_OF_WORKING.md`, `docs/README.md` and every
  round-3 file are not edited; proposed edits go in the report. A needed change to a shared file is an
  escalation, not an edit. A label change is proposed in a report with its source.
- Every output directory gets `PROVENANCE.txt` (job id, partition actually used, node, date, commit,
  command line, config hash with its config, `PYTHONHASHSEED`, md5 of the script that ran, intended
  job prefix `r4ppi_` and the stage) and is stamped with `stamp_dir()` from the `longleaf-provenance`
  skill, written by the job on the node. A sub-agent stamps from its own process. Before reusing or
  rebuilding any output this session did not create, run `whose()` on it; `sibling` or `unstamped`
  goes to the oversight chat rather than being rebuilt.
- Jobs are identified by Slurm id, since the submission route replaces `--job-name`.
- Explicit `pa.schema` on every parquet; summaries before bulk tables; seeds from `zlib.crc32`, never
  `hash()`.
- Memory from `sacct` (16 GB on 4 CPUs for head fitting; B1 and B2 peaked at 11.2 GB). Slurm time
  limits at about three times a sibling's runtime, never a blanket 16 h; smoke-test first where there
  is no sibling. Harness ceiling from queue time plus runtime. Working directory set explicitly in
  every job script. Never compute on the login node.
- Non-analysis work has a time cap and stops at it. Checker or tooling work is capped at half a day
  per interval.
- Commit messages through a file. The lead is the only committer and runs every git command; it
  checks every sub-agent hand-back against its primary tables before commit. One writer per file;
  fragments plus a merge step with collision reporting.
- Every table carries a `target` column (`design` or `super`). Every lung number carries its
  training-donor count. Every CCRCC analysis runs with 24 donors and with `INT4` and `INT24` merged,
  both reported. Donor and source labels come only from
  `results/round4/data/P4_audit/donor_audit_r4.csv` (and the round-3 audit file it extends).
- Xenium panels and target lists have `NegControl*`, `UnassignedCodeword*` and `BLANK*` removed at
  read time, with the count recorded.
- Lung is read through this track's own wrapper, which removes `dropped_patch_barcodes` before the
  subset assertion; `round3_d4_sets.load_set` is not edited and not called directly on lung.
- Before naming a term, list in writing every variable that differs between its arms. Predictions are
  written before running and reported beside outcomes. No ratio whose denominator is within noise of
  zero. Every number in a report is read back from the file named beside it.
- `code/scripts/sweep_table.py` runs over `README.md` and `docs/round4_ppi_*.md`, in the local clone
  where the documents sit, before every handover.
- Writing. Plain prose, no em-dashes, no colon-then-explanation constructions, math as LaTeX, numbers
  at the precision the comparison needs with the relative scale stated.

Not to cite. Round 3's D4 statement that morphology removes 31% to 34% of the probe signal is
quarantined.

## 3. The stages (source section 6)

### Q0. Setup (half a day, capped at one day)

1. Read the source, `docs/WAYS_OF_WORKING.md`, `docs/round3_final_report.md` section 6.4 and its
   closing page, `docs/round4_data_report.md` and `docs/decisions/round4_data_P7_decisions.md`.
   Transcribe section 6 into this plan. Flag anything that looks wrong in the Q1 report.
2. Create the branch and directories. Run `whose()` on `results/round4/data/` and record the verdict.
   Read the lung task file and record its sample count, donor count and dropped barcodes here; the
   file wins over the source's counts. Both are recorded in section 7.
3. The general dataset. Fetch the ACS PUMS income data as packaged by `ppi_py` (its `census`
   dataset), with state and PUMA identifiers, into `results/round4/ppi/Q0_setup/acs/` with a
   `PROVENANCE.txt` naming source URL, version and hashes. If Longleaf's network refuses, record the
   refusal and continue; the ACS units of Q2 and Q4 wait for the file. Write
   `results/round4/ppi/Q0_setup/acs_task_def.json` in the A0 format with the cluster variable (state,
   and PUMA as a second level), the outcome (log income), the $\theta_3$ covariate (age,
   standardised) and the predictor (the package's gradient-boosted predictions, or if absent one fit
   on a held-out split of the labelled data and recorded).
4. Anchor. Rerun `round3_b1_ppi.py`'s four acceptance identities on CCRCC with one encoder (with $U$
   empty PPI equals classical; with $\hat y = y$ PPI equals the full-data value; with one spot per
   donor the cluster variance equals the i.i.d. one; the permuted predictor's donor-weighted
   $\lambda$ is 0) and reproduce `results/round3/B1_ppi/b1_acceptance.csv` to $10^{-10}$. Nothing in
   Q1 starts until this passes. Failure is stop-and-report.

Parallel units. ACS data; B1 anchor; lung wrapper (exercise on `NCBI865`, record 2,142 rows).

### Q1. The estimator, made right (three days; **gate**)

Script `code/scripts/round4_ppi_estimator.py` (one entry point per component, imported by every later
stage) and `code/scripts/round4_ppi_q1_sim.py`.

Two targets on every row. Design-based, $\theta_{\text{full}}$ on the fixed set of $G$ donors, with
the finite-population correction $(1 - n_L/G)$ on the between-donor term. Superpopulation, checked
only in simulation where fresh donors can be drawn, with no correction. Real-data coverage is always
of the design-based target.

Components compared.

- $\lambda$. (a) B1's, tuned on the spot i.i.d. variance. (b) Tuned on the clustered variance,
  restricted to $[0, 1]$, fixed at 0 when $G_L < 4$. (c) Cross-fitted over halves of the labelled
  donors, swapped and averaged. All three reported; (c) is the expected choice.
- Variance and reference. (a) CR1 with $t_{G_L - 1}$. (b) CR2 (Bell and McCaffrey) with Satterthwaite
  degrees of freedom. (c) Either, with a Welch-Satterthwaite combination of the $U$ and $L$ terms'
  degrees of freedom.
- Bootstraps. (a) Percentile donor bootstrap. (b) Studentised donor bootstrap. (c) BCa. 500 draws
  each.
- Finite-population correction. (a) None. (b) $(1 - n_L/G)$ on the labelled between-donor term for
  the design-based target. Reported for both targets.

The simulation. Donors $g = 1, \dots, G$ with $m$ spots; $m_{gi} = c_g + d_{gi}$ standardised
overall; $y_{gi} = \mu + u_g + \beta m_{gi} + e_{gi}$, $u_g \sim N(0, \sigma_u^2)$,
$e_{gi} \sim N(0, \sigma_e^2)$, $\rho = \sigma_u^2/(\sigma_u^2 + \sigma_e^2)$;
$\hat y_{gi} = y_{gi} - a_g - \epsilon_{gi}$ with $a_g \sim N(0, \sigma_a^2)$, $\sigma_a^2 =
\sigma_u^2/2$, and $\epsilon_{gi}$ scaled so the spot-level correlation of $y$ and $\hat y$ is $r$.
Grid $G_L \in \{4, 6, 8, 12, 20\}$, $G_U \in \{10, 20, 50\}$, $m \in \{200, 1000, 5000\}$,
$\rho \in \{0.1, 0.3, 0.5\}$, $r \in \{0, 0.3, 0.5, 0.8\}$. Estimands $\theta_3$ (slope) and the
mean, spot-weighted and donor-weighted. 2,000 replicates per cell. Superpopulation draws fresh donors
every replicate; design-based draws a fixed population of $G = 24$ once per cell and labelled donors
from it without replacement. Record coverage at 90%, mean width, width relative to classical with the
same variance, MC standard error.

Acceptance. At $m = 1$ every clustered variance equals the i.i.d. one to $10^{-12}$. At $r = 0$,
$\lambda$ within 0.05 of 0 under every tuning rule and every interval covering 0.89 to 0.91. At
$G_L = 20$ and $m = 200$ every variance variant within 0.02 coverage of every other. The module
reproduces `b1_acceptance.csv` in B1's configuration.

Parallel units. Fifteen, one per $(G_L, \rho)$.

Outputs. `results/round4/ppi/Q1_estimator/q1_sim_coverage.csv`, `q1_acceptance.csv`,
`q1_report_numbers.csv`, `fig_q1_coverage_by_G.png`, and `docs/round4_ppi_estimator_definition.md`
(one page, the chosen estimator in the paper's notation, finite-sample behaviour quoted beside each
choice). Then `docs/round4_ppi_Q1_report.md` covering Q0 and Q1 in the section 8 format, sweep,
commit, tag `round4-ppi-Q1`, and **stop until the Q1 decision memo is handed back**.

### Q2. The gain theorem and the allocation result (three days; no gate)

Derivation first, written step by step in `docs/round4_ppi_theory.md` before the experiment runs.

- The gain theorem. With $\phi^L_{gi} = u^r_g + e^r_{gi}$ and the outcome's own contribution
  $u_g + e_{gi}$,
  $\text{Var}(\hat\theta_{\text{PP}}) = \sigma_{u,r}^2/n_L + \sigma_{e,r}^2/(n_L m) + V_U$ and
  $\text{Var}(\hat\theta_{\text{cl}}) = \sigma_u^2/n_L + \sigma_e^2/(n_L m)$. Show the ratio tends to
  $\sigma_{u,r}^2/\sigma_u^2$ as $m$ grows, that with $\hat y_{gi} = y_{gi} - a_g - \epsilon_{gi}$
  this is $1 - R^2_{\text{cluster}}$ at the optimal $\lambda$, and state the theorem in words, the
  $\lambda$ corollary (the cluster-level regression coefficient) and the no-gain corollary.
- The allocation result. Classical $m^\star = \sqrt{(c_d/c_s)(\sigma_e^2/\sigma_u^2)}$; derive
  $m^\star_{\text{PP}} = \sqrt{(c_d/c_s)(\sigma_{e,r}^2/\sigma_{u,r}^2)}$ and show
  $m^\star_{\text{PP}} \le m^\star$; the unit term is a fraction $f$ of the cluster term once
  $m \ge (1 - \rho_r)/(f \rho_r)$; state that $m$ at $f = 0.1$ for each task's fitted $\rho_r$.
- A derivation that does not close is stop-and-report, naming the failing step.

Experiment by masking. CCRCC (24 and merged), Indiana (25 units), lung Xenium (15 donors), ACS
(states, and PUMAs within one large state). $n_L \in \{4, 6, 8, 12, 16\}$ where the task has enough
donors, $m \in \{25, 50, 100, 200, 500, \text{all}\}$, 200 draws, Q1 estimator; empirical variance,
mean estimated variance, coverage of $\theta_{\text{full}}$. Three encoders and the permuted predictor
on HEST; the package predictor and a permuted one on ACS. Both populations, $\theta_3$ and $\theta_2$
(ACS $\theta_3$ is the slope of log income on standardised age, $\theta_2$ the mean). Measure per task
and predictor the unit-level, within-cluster and cluster-level $R^2$ (with the small-cluster
correction) and set them beside the variance ratio at the largest $m$. Fit the variance surface and
report components and $m^\star$ at $c_d/c_s \in \{10, 100, 1000\}$.

The recalibration test (one day, capped). CCRCC and Indiana, `hoptimus0`. Per donor, mean of the 256
PCA coordinates; leaving that donor out, ridge regression of the other donors' mean residual offsets
$b_g$ (per gene, 50-gene list) on their mean embeddings; add the predicted offset to the held-out
donor's predictions. Report per gene the leave-one-donor-out $R^2$ of offsets, cluster-level and
within-cluster $R^2$ before and after, and the variance ratio at $m = $ all before and after, in
`q2_recalibration.csv`. The ridge penalty is not tuned on the held-out donor.

Parallel units. Five, CCRCC, Indiana, lung, ACS, recalibration.

Outputs. `results/round4/ppi/Q2_theory/q2_variance_grid.csv`, `q2_cluster_r2.csv`,
`q2_fitted_components.csv`, `q2_recalibration.csv`, `q2_report_numbers.csv`,
`fig_q2_gain_vs_cluster_r2.png`, `fig_q2_variance_vs_m.png`, `fig_q2_optimal_m.png`, and the theory
document.

### Q3. Two labelling regimes (three days; **gate**)

Regime A, few clusters fully labelled (B1 and B2's design with the Q1 estimator). Regime B, $m$
labelled spots on every donor's slides, drawn uniformly, every other spot unlabelled.

Derivation first, in `docs/round4_ppi_theory.md`, in the Q2 notation with $y_{gi} = \mu + u_g +
e_{gi}$ and $\hat y_{gi} = \nu + p_g + d_{gi}$.

- Design-based. Per-cluster difference estimator with design variance $(1 - m/M_g) S^2_{r,g}/m$;
  donor-weighted $\text{Var}_B^{\text{design}} = G^{-2}\sum_g (1 - m/M_g) S^2_{r,g}/m$; show the
  ratio is $1 - R^2_{\text{within}}$ at the within-cluster optimal $\lambda$, that $a_g$ drops out,
  that the plug-in estimator with a $t$ reference on $G(m - 1)$ degrees of freedom (or Satterthwaite)
  is the variance estimator; give the spot-weighted version with weights $M_g/N$.
- Superpopulation. $\text{Var}_B^{\text{super}} = \sigma_u^2/G + \text{Var}_B^{\text{design}}$ up to
  the finite-population factor; the cluster-robust estimator over all $G$ clusters with a $t_{G-1}$
  reference; show the gain vanishes as $m$ grows.
- The comparison at equal unit budget $B = n_L m_A = G m_B$. Regime A
  $\sigma_u^2(1 - R^2_{\text{cluster}})/n_L + \sigma^2_{e,r}/B$ against regime B
  $\sigma_u^2/G + \sigma^2_{e,r}/B$; regime B wins on the between term when
  $R^2_{\text{cluster}} < 1 - n_L/G$. State both targets and the crossover cost ratio.
- The head is trained on other donors (calibration-fraction-zero `donor` mode); labelled spots enter
  only the rectifier.

Budget matching. $B \in \{2400, 4800, 9600\}$. Regime A on $n_L \in \{4, 6, 8, 12\}$ with
$m = B/n_L$ (the Q2 grid reused). Regime B on all $G$ with $m = B/G$ per cluster, spread over a
donor's slides in proportion to spot counts. A cost-weighted version with $c_d/c_s = 100$ (regime B
pays $G$ cluster costs, regime A pays $n_L$). CCRCC, Indiana, lung Xenium, ACS. Both targets on every
row, the design-based variance on design rows and the cluster-robust one on superpopulation rows. A
regime B arm is added to the Q1 simulation to check superpopulation coverage.

Acceptance. Regime B at $m = $ all equals the full-data value exactly. At $m = 1$ the regime B cluster
variance reduces to the one-labelled-unit formula. Regime A reproduces B2's CCRCC coverage within MC
error in B1's settings.

Parallel units. Five, CCRCC, Indiana, lung, ACS, and the simulation's regime B arm.

Outputs. `results/round4/ppi/Q3_regimes/q3_regime_comparison.csv`, `q3_report_numbers.csv`,
`fig_q3_regimes.png`, and the regime B derivation. Then `docs/round4_ppi_Q3_report.md` covering Q2 and
Q3, predictions against outcomes, sweep, commit, tag `round4-ppi-Q3`, and **stop until the Q3
decision memo is handed back**.

### Q4. The paper's tables, the ACS application and the gene axis (three days; no gate)

- Real-data tables. CCRCC (24 and merged), Indiana, lung Xenium with the Q1 estimator, the Q2 curves
  and both Q3 regimes; $\theta_3$ and $\theta_2$ in both populations; $\theta_1$ on IDC under the
  four-donor labels as the illustration (four per-donor intervals and the pooled donor-clustered
  one, `results/round3/B1_ppi/b1_theta1_by_slide.csv`). Three encoders and the permuted predictor.
  200 draws per setting.
- The ACS application. States (51) and PUMAs within the largest state; slope of log income on
  standardised age and mean log income, spot- and cluster-weighted; package and permuted predictors;
  regime A $n_L \in \{4, 6, 8, 12, 20\}$, regime B $m \in \{25, 50, 100, 200\}$; unit-level and
  cluster-level $R^2$ beside the gain.
- The gene axis. CCRCC and Indiana, training-only 200-gene lists from
  `results/round4/data/P6_genes/` under the `donor` folds; per-gene width ratio against cluster-level
  $R^2$ and unit-level Pearson at $n_L = 8$ (regime A) and $m = 100$ (regime B); the fraction gaining
  more than 5% and the correlations.
- Two-way clustering supplement (one day, capped). `q4_two_way.csv` lists every task's second
  grouping, its count and its relation to the donor (nested in, containing, crossed) before any number
  is computed. Nested in the donor, reported as adding nothing. Containing the donor (lung slides),
  the slide-clustered to donor-clustered variance ratio for $\theta_3$ as a diagnostic with the slide
  count and no interval. Crossed, the Cameron, Gelbach and Miller (2011) two-way variance for
  $\theta_3$ under regime A beside the donor-only one.

Parallel units. Eight, by task and estimand, including ACS and the two-way supplement.

Outputs. `results/round4/ppi/Q4_tables/q4_main_table.csv`, `q4_gene_axis.csv`, `q4_two_way.csv`,
`q4_report_numbers.csv` (from `build_q4_numbers.py`), figure scripts `code/figures/round4_ppi_fig*.py`
writing to `figures/round4/ppi/`.

### Q5. The closing report (two days; **gate, end of track**)

- The joint design table `results/round4/ppi/Q5_joint/q5_joint_design.csv`, reading the conformal
  track's committed `results/round4/conformal/C3_real/c3_o_sweep.csv` on branch `round4-conformal`
  (read only, recording the commit read). Per task and $m$, regime B's CI width ratio from Q3 and
  GHCP's coverage and width at $o = m$. Conformal columns marked pending if C3 is not committed.
- `results/round4/ppi/Q5_joint/q5_cluster_table.csv`, one row per donor and task, with spot count,
  mean embedding (as a parquet path), mean residual per gene on the 50-gene list, within-donor
  residual variance and the leave-one-out offset prediction from Q2. No analysis.
- `docs/round4_ppi_final_report.md` in the section 8 format covering Q1 to Q5, the full predictions
  table, "Escalations", and a closing page "What the PPI track established" of at most one page, each
  sentence naming its file. Sweep, tag `round4-ppi-final`, **stop**.

About eighteen working days with the gates.

## 4. Predictions (source sections 6 and 7), copied before running

Each is scored in the closing report as held, partly held, refuted or not tested.

**Q1.1.** CR1 with $t_{G_L-1}$ covers 0.87 to 0.91 at $G_L \ge 6$ and 0.82 to 0.88 at $G_L = 4$; CR2
with Satterthwaite brings $G_L = 4$ to 0.87 or above.

**Q1.2.** The percentile bootstrap under-covers by at least 0.10 at $G_L \le 8$; bootstrap-$t$
recovers to within 0.03 of nominal; BCa sits between.

**Q1.3.** The over-coverage B2 saw at $n_L = 12$ (0.94 to 0.95) is mostly the missing
finite-population correction, not $\lambda$ optimism. With the correction and the design-based
target, coverage at $n_L = 12$ of 24 lands at 0.89 to 0.92; cross-fitted $\lambda$ on its own moves it
by less than 0.02, at a width cost under 3%.

**Q1.4.** The Welch-Satterthwaite combination matters only when $G_U \le 10$, where it widens the
interval by 5% or more.

**Q1.5.** PPI's width relative to classical is below 0.9 only when $r \ge 0.5$ and $\rho \le 0.3$; at
$\rho = 0.5$ it stays above 0.9 for every $r$, because predictions do not reduce the between-donor
component.

**Q2.1.** The observed PPI-to-classical variance ratio at $m = $ all is within 0.1 of
$1 - R^2_{\text{cluster}}$ on every task and predictor, and is not predicted by the unit-level $R^2$
(the HEST encoders have unit-level $R^2$ of 0.1 to 0.2 and cluster-level $R^2$ under 0.3; the ACS
predictor has a higher cluster-level $R^2$ and a larger gain).

**Q2.2.** The empirical variance is flat in $m$ beyond 100 to 200 units per cluster on every task,
within Monte Carlo error.

**Q2.3.** The fitted $\sigma_{e,r}^2$ falls with encoder quality and $\sigma_{u,r}^2$ barely does, so
$m^\star_{\text{PP}}$ is smaller for `hoptimus0` than for `resnet50` than for the permuted predictor,
on every task.

**Q2.4.** At $c_d/c_s = 100$, $m^\star$ is between 30 and 150 on the Visium tasks and larger on lung
Xenium and ACS, whose within-cluster variance is higher.

**Q2.5.** The estimated variance tracks the empirical one within 15% across the grid, except at
$n_L = 4$.

**Q2.6.** The recalibration test predicts donor offsets with leave-one-donor-out $R^2$ between 0.1 and
0.4 on the median gene of both tasks, raises the cluster-level $R^2$ by at least 0.1 on those genes,
leaves the within-cluster $R^2$ unchanged to $10^{-3}$, and lowers the variance ratio at $m = $ all by
an amount within 0.1 of the change in $1 - R^2_{\text{cluster}}$.

**Q3.1.** At equal unit budget, regime B intervals are narrower than regime A for $\theta_3$
donor-weighted on every task, by 20% or more, because every cluster contributes to the rectifier and
the $t$ reference has more degrees of freedom; the advantage shrinks under the cost-weighted budget and
reverses when $c_d/c_s \ge 1000$.

**Q3.2.** Regime B design-based coverage is 0.88 to 0.92 at every $m \ge 25$ with the design-based
variance, and above 0.97 when the cluster-robust variance is used against the design-based target,
because that variance carries a between-donor term the target does not have.

**Q3.3.** The crossover cost ratio at which regime A overtakes regime B is predicted by the Q2
decomposition within a factor of two on every task.

**Q3.4.** Regime A's PPI-to-classical variance ratio tracks the predictor's cluster-level $R^2$ and
regime B's tracks its within-cluster $R^2$. Across the three encoders and the permuted predictor on
every task, the Spearman correlation of the regime A ratio with $1 - R^2_{\text{cluster}}$ is above
0.8 and with $1 - R^2_{\text{within}}$ below 0.5, and the reverse holds for regime B. If Q2's
measurement confirms that the encoders' within-cluster $R^2$ exceeds their cluster-level $R^2$,
regime B gains more from predictions than regime A on every HEST task.

**Q4.1.** The gene-axis width ratio correlates with cluster-level $R^2$ more strongly than with
unit-level Pearson, and fewer than a third of genes gain more than 5% under regime A at $n_L = 8$.

**Q4.2.** No HEST task has a crossed second grouping with more than four levels, so the two-way
variance is reported for ACS (state by survey year, if the package data carries the year) and the
HEST result is the nesting table itself.

## 5. Decision boundaries (source section 9)

- Decided alone. Sub-agent structure; seeds; replicate counts above 2,000; bootstrap draws above 500;
  job sizing; which of two equivalent implementations to use.
- Recorded as an escalation, and work continues. The ACS download refused (HEST units continue); the
  lung task file disagreeing with the source's counts (the file is used); the recalibration test or
  the two-way supplement reaching its cap (stopped, what exists reported); an acceptance identity
  failing at a tolerance the dtype supports (fixed, rerun, said so); a task where a fold cannot be
  formed; any new property of the data; a per-task result reversing a round-3 sign; any need to change
  a shared file.
- Stop and report. The Q0 anchor failing. A Q2 or Q3 derivation that does not close.
- Never this session's. Contact outside the project; changes to `main`, round-3 files, data-pull
  outputs, the audit file or the conformal track's areas; any download other than the Q0 ACS fetch
  the source instructs (see section 8, item 5).

## 6. Parallel units and sub-agent structure

Every stage's named parallel units go to one sub-agent each, with a written brief that includes,
verbatim, "Stamp every output directory with `stamp_dir()` from the `longleaf-provenance` skill.
Before reusing or rebuilding any output you did not create, run `whose()` on it; if the verdict is
`sibling` or `unstamped`, ask me rather than rebuilding." Each sub-agent writes its own fragment
under its own directory, runs no git command, and hands back its files. The lead merges with
collision reporting, recomputes every pooled number from the merged tables into
`<stage>_report_numbers.csv`, and commits.

| stage | units |
|---|---|
| Q0 | ACS data; B1 anchor; lung wrapper |
| Q1 | fifteen simulation units, one per $(G_L, \rho)$ |
| Q2 | CCRCC; Indiana; lung; ACS; recalibration |
| Q3 | CCRCC; Indiana; lung; ACS; simulation regime B arm |
| Q4 | CCRCC $\theta_3$ with gene axis; CCRCC $\theta_2$; Indiana $\theta_3$ with gene axis; Indiana $\theta_2$; lung $\theta_3$; lung $\theta_2$; ACS; two-way supplement |

The estimator module, the derivations, the merges, the reports and the commits are the lead's.

## 7. Records made in Q0 step 2

`whose()` on `results/round4/data/` at `round4-data-v2`, run from this session on the local clone.
The directory root carries no stamp and reads `unstamped`. The stamped subdirectories `P0_setup`,
`P1_download`, `P2_embeddings`, `P4_audit`, `P5_task/panel_job` and `P8_addendum` read
`foreign_session`, which is the data-pull session in this project. `P1_selection`, `P3_morphology`,
`P5_task`, `P6_genes` and `P7_report` read `unstamped`. This track only reads these directories, as
the source designates them the track's inputs, and rebuilds none of them. The verdicts go into the Q1
report so the oversight chat can say whether that reading needs anything further.

The lung task file `results/round4/data/P5_task/LUNG_XENIUM.json` says 20 samples, 15 donors (none
excluded from donor units), 15 donor folds, 45 `a4b_k10` rows, 343 target genes with no control
features among them, four capture slides (`0003392`, `0003400`, `0003789`, `0003817`), and
`dropped_patch_barcodes` equal to `{"NCBI865": ["051x019"]}`. `NCBI865` records 2,142 patch spots
after the drop. These agree with the source.

## 8. Points in the source flagged for the Q1 report rather than changed

1. **The $r = 0$ cells of the Q1 simulation cannot be built as written.** With
   $\hat y_{gi} = y_{gi} - a_g - \epsilon_{gi}$ and $a$, $\epsilon$ independent of $y$, the spot
   correlation is $\text{sd}(y)/\text{sd}(\hat y) > 0$, and it reaches 0 only as the spot noise
   diverges. The implementation needs a construction for $r = 0$ (for example a predictor drawn
   independently of $y$ with the same donor and spot structure), and the choice is reported.
2. **Q1's $r = 0$ acceptance band conflicts with two predictions.** Every interval covering 0.89 to
   0.91 includes the percentile bootstrap, which Q1.2 predicts under-covers by 0.10 at $G_L \le 8$,
   and CR1 at $G_L = 4$, which Q1.1 predicts at 0.82 to 0.88. The band is also about 1.5 Monte Carlo
   standard errors wide at 2,000 replicates ($\sqrt{0.09/2000} \approx 0.0067$), so over hundreds of
   cells some valid intervals fall outside it by chance. The report will score the band against the
   variants and $G_L$ the predictions call valid, with the MC error beside it, and say so.
3. **Q1.5 looks inconsistent with the simulation design.** With $\sigma_a^2 = \sigma_u^2/2$ in every
   cell, the predictor's cluster component is $u_g - a_g$ and its cluster-level $R^2$ is
   $\sigma_u^2/(\sigma_u^2 + \sigma_a^2) = 2/3$ regardless of $r$. The Q2 theorem then predicts a
   substantial gain at large $m$ even at $\rho = 0.5$, which Q1.5 rules out. The prediction stays as
   written and is scored against the outcome.
4. **The gain theorem's $V_U$ term does not vanish with $m$.** It is fixed by $G_U$ and carries the
   predictions' own between-donor variance, $\lambda^2 \text{Var}(p_g)/G_U$, so the ratio tends to
   $\sigma_{u,r}^2/\sigma_u^2 + n_L V_U/\sigma_u^2$ and reaches $1 - R^2_{\text{cluster}}$ only when
   $G_U \gg n_L$. Also, under $\hat y = y - a - \epsilon$ the rectifier's cluster component is
   $(1 - \lambda) u_g + \lambda a_g$ rather than $u_g - \lambda a_g$; the end result
   $1 - R^2_{\text{cluster}}$ at the optimal $\lambda$ is unaffected. Both are for the Q2 derivation;
   raised now so the Q1 decision can say whether the Q2 statement should change.
5. **The ACS fetch against "any download" being never the session's.** Section 9 lists any download
   as never the session's, while Q0 step 3 instructs this one. The plan reads Q0 step 3 as the
   specific authorisation for this dataset only.
6. **The design-based variance when $U$ is the complement of $L$.** If the unlabelled set is exactly
   the donors not labelled, the PPI estimator is $\lambda\bar{\hat y}_U + \bar r_L$, not the
   textbook difference estimator $\lambda\bar{\hat y}_{\text{all}} + \bar r_L$, and the $U$ and $L$
   terms are negatively correlated under sampling without replacement. A finite-population correction
   on the labelled term alone may then not be the exact design variance. Q1 checks this in the
   design-based simulation and reports it.
7. **Q4's eight units leave two items unplaced.** Eight units by task and estimand, with ACS and the
   two-way supplement, means six HEST units. The gene axis is placed in the CCRCC and Indiana
   $\theta_3$ units and the IDC $\theta_1$ illustration in the CCRCC $\theta_2$ unit, unless the Q3
   memo says otherwise.
8. **Lung and $n_L = 16$.** Lung has 15 donors, so $n_L = 16$ is infeasible, and at $n_L = 12$ only
   three donors are unlabelled. Q2 and Q3 run lung at the $n_L$ values that leave at least two
   unlabelled donors, and record the counts.

## 9. Amendment of 30 September 2026, working copies (oversight chat note)

Transcribed before any further work, and applied for the rest of the track. The note covers a point
the instruction document did not, namely that each session needs its own working copy, because a git
working copy has one checked-out branch at a time and two sessions sharing one decide for each other
what is checked out.

The rule. Each session has its own working copy, locally and on Longleaf, and never checks out a
branch in a working copy the other session uses.

- Locally, `~/HEST-1k-replication` belongs to this session alone. It stays on `round4-ppi`, and no
  other branch is checked out there. The conformal session moves to a sibling clone,
  `~/HEST-1k-replication-conformal`, made from this local repository. The `round4-conformal` branch in
  this clone is not deleted, renamed or moved.
- On Longleaf, the project tree `/work/users/w/e/weiyang/hest_replication` stays on `main` at
  `round4-data-v2` (`9d7277d`) and nobody checks out a branch there. It is the data root only (the
  harness hard-codes it as `ROOT`).
- This track's code runs from its own clone, `/work/users/w/e/weiyang/hest_code/round4-ppi/`, which
  is on `PYTHONPATH` in every job script. Every job records that clone's HEAD as its commit and the md5
  of every script it executed. Before the first job from the clone, the harness there is confirmed at
  md5 `0ad7ae8efe554c1f285e5f384a9fb7f5`.
- Results still go to `results/round4/ppi/` inside the project tree, which the conformal track never
  writes. The conformal track's results go to `results/round4/conformal/`, which this track never
  writes.

What the note asked for before continuing, and what was found.

1. The Longleaf project tree reads branch `main`, HEAD `9d7277dc8c4bfade08d5895051666ee134b8396a`,
   working tree matching `origin/main` apart from untracked files that predate round 4. It was not
   changed.
2. Jobs already submitted that imported code from the project tree. Three Q0 jobs were submitted by
   this session's sub-agents before the note, Slurm `3074092` (ACS fetch, a self-contained staged
   script), `3074101` (B1 anchor, which ran `code/scripts/round3_b1_ppi.py` and the harness from the
   project tree) and `3074111` (lung wrapper, which imported `round3_d4_sets.py` and the harness from
   the project tree). All three were still pending and never started; `sacct` records each as
   cancelled with elapsed `00:00:00`. They produced nothing, so there is nothing to check against a
   committed md5, and all three are resubmitted from the new clone.
3. `docs/decisions/round4_ppi_track.md` is this session's copy of the instruction document. It was
   committed on `round4-ppi` in `47edb81` together with this plan, before the note arrived, and is
   tracked.
4. The clone was created at `/work/users/w/e/weiyang/hest_code/round4-ppi/` from GitHub, on branch
   `round4-ppi` at `47edb81`. Its harness md5 is `0ad7ae8efe554c1f285e5f384a9fb7f5`, as required. The
   clone is pull-only; the local clone stays the sole committer.
