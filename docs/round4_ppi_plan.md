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

**Added by the Q1 decision memo (plan section 13), copied verbatim before Q1b and the theorem check run.** Q1.4 is dropped from every later stage (memo section 1).

- Q1b.1. At $r = 0$, rules (d1) and (d2) give a median $\lambda$ of 0 in every cell and a median width ratio within 0.02 of 1 at every $n_L \ge 6$.
- Q1b.2. At $r \ge 0.5$ and $n_L \ge 8$, rule (d1)'s median width ratio is within 0.02 of rule (c)'s; rule (d2) gives up more, by 0.02 to 0.05.
- Q1b.3. With unequal sizes, CR1 at $G_L = 4$ loses 0.02 to 0.04 of coverage against the equal-size arm, and CR2 with Satterthwaite recovers at least half of that; at $G_L \ge 8$ CR1 and CR2 are within 0.01.
- Q1b.4. On $\theta_3$ spot-weighted at $\rho = 0.1$, the wild bootstrap-$t$ with Mammen weights covers at least 0.88 at every $G_L \ge 6$, and the Rademacher version sits between it and the CR1 $t$ interval.

- Prediction Q2.7, written now: at $m = 5000$ and $G_U = 100$ the empirical ratio is within 0.05 of $1 - R^2_{\text{cluster}}$ in all three cells, and at $G_U = 20$ it is within 0.05 of the full ratio and above $1 - R^2_{\text{cluster}}$ by at least the $G_U$ term's size.

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

## 10. Amendment of 30 September 2026, version management (oversight chat note)

Transcribed before any further work. It applies from the Q1 gate on. What the instruction document
already says stands, namely that this session commits only on `round4-ppi`, tags each gate and never
merges into `main`. The note adds how accepted work reaches `main`, which is through a pull request at
each gate, merged on GitHub by Nicolas with a merge commit after the oversight chat accepts the gate
report. The conformal track follows the same procedure on `round4-conformal`, on disjoint files.

At each gate (Q1, Q3 and Q5), in this order.

1. Commit the gate report and everything it cites on `round4-ppi`, run the numeric-claim sweep, tag
   the commit (`round4-ppi-Q1`, `round4-ppi-Q3`, `round4-ppi-final`), and push the branch and the tag.
2. Open a pull request from `round4-ppi` into `main`, titled "Round 4 PPI track, gate Q1" (or Q3, or
   final). The description gives the tag, the head commit, the path of the gate report, and one
   paragraph on what the stage produced. No reviewers, labels or auto-merge.
3. Stop, as the gate rule requires.

This session never merges the pull request, never pushes to `main` and never changes `main` in any
other way.

Rules for the branch, because every provenance record cites its commit hashes.

- Never rebase, squash, amend a pushed commit, or force-push `round4-ppi`.
- After a merge, keep working on `round4-ppi`. Do not merge or pull `main` into it unless the oversight
  chat asks. The conformal track's merged work being in `main` and not in this branch is intended.
- If a gate is not accepted, fix it with new commits on `round4-ppi` and push; move the tag only if the
  oversight chat asks. The open pull request picks up the new commits; no second one is opened.

The Longleaf project tree `/work/users/w/e/weiyang/hest_replication` does not follow `main` during the
round. It stays at `round4-data-v2` as the data root, and nothing is pulled, fetched into or checked
out there. It is updated once, between rounds.

If opening the pull request fails, the branch and tag are pushed anyway, the report carries the GitHub
compare URL for `main...round4-ppi`, and the failure is recorded under escalations for Nicolas to open
it.

Two facts recorded against this note.

1. The `gh` command-line tool cannot verify TLS certificates in this session's sandbox, so every
   `gh` call fails here. The pull request is therefore opened through GitHub's REST API with the
   configured token, which creates the same pull request `gh pr create` would. If that also fails, the
   fallback above applies.
2. Before this note and the working-copy note arrived, this session's first read-only check of the
   Longleaf project tree ran `git fetch -q origin` there (30 September, about 12:25 local time). That
   updated only the tree's remote-tracking refs (it now lists `origin/round4-ppi`); the checked-out
   branch, HEAD (`9d7277d`) and working files were not changed. Nothing has been fetched into the tree
   since, and nothing will be.

## 11. Addendum 1 (30 September 2026), transcribed before any of it is acted on

Source `docs/decisions/round4_ppi_addendum1.md`, the oversight chat's answer to section 8, handed
over by Nicolas. It does not move the Q1 gate and nothing in it starts Q2. Where this section and
the source differ, the source governs.

### 11.1 The eight points of section 8

1. The $r = 0$ cells use a predictor drawn independently of $y$ with the same structure,
   $\hat y_{gi} = \nu + p_g + d_{gi}$, $p_g \sim N(0, \sigma_u^2)$, $d_{gi} \sim N(0, \sigma_e^2)$,
   independent of everything else, so its between-donor share is $\rho$. This replaces the
   construction in the committed simulation script. It is recorded in
   `docs/round4_ppi_estimator_definition.md` and the report.
2. The 0.89 to 0.91 band at $r = 0$ is scored only on CR2 with Satterthwaite at every $G_L$, CR1 at
   $G_L \ge 6$, and the bootstrap-$t$, with the MC standard error beside every cell. The other
   variants are scored against Q1.1 and Q1.2, not the band.
3. Q1.5 is scored as written. Nothing in Q1 changes.
4. The $V_U$ and rectifier corrections are accepted for the Q2 theory document. Nothing in Q1
   changes.
5. The ACS reading was correct; section 11.4 authorises one more download.
6. Changes Q1 now; 11.2.
7. Q4 placement accepted as plan section 8 item 7 places it.
8. Lung runs at the $n_L$ values that leave at least two unlabelled donors, counts recorded.

### 11.2 The design-based arm uses the textbook difference estimator

Predictions are on every spot of every donor of the fixed population, so the primary design-arm
estimator is the difference estimator over the whole population; the only randomness is which
$n_L$ of the $G$ donors are labelled.

- Donor-weighted.
  $\hat\theta = \frac{\lambda}{G}\sum_{g=1}^{G}\bar{\hat y}_g + \frac{1}{n_L}\sum_{g \in L}(\bar y_g - \lambda\bar{\hat y}_g)$,
  $\widehat{\text{Var}} = (1 - n_L/G)\, s_r^2/n_L$, $s_r^2$ the sample variance of the labelled
  donors' rectifier means, $t_{n_L - 1}$ reference.
- Spot-weighted. $\hat\theta = \frac{\lambda}{N}\sum_{i=1}^{N}\hat y_i + \frac{G}{N n_L}\sum_{g \in L} R_g$
  with $R_g = \sum_{i \in g}(y_i - \lambda\hat y_i)$, $\widehat{\text{Var}} = (1 - n_L/G)\frac{G^2}{N^2}\frac{s_R^2}{n_L}$.
- $\theta_3$. The same two forms on the per-spot contributions, with the covariate's constants
  computed over all $N$ spots.
- B1's complement form $\lambda\bar{\hat y}_U + \bar r_L$ stays as a named legacy variant,
  `form = complement`, with its own coverage in the design arm.
- The superpopulation arm is unchanged ($U$ is $G_U$ fresh donors, no correction).
- Welch-Satterthwaite and the $G_U$ axis apply to the superpopulation arm only; Q1.4 is scored
  there.
- Q1.3 is scored with the textbook form as primary and the complement form beside it.
- The three $\lambda$ rules apply to both forms.
- Every row carries a `form` column (`textbook` or `complement`) beside `target`.
- `docs/round4_ppi_estimator_definition.md` states both forms and which target uses which.

### 11.3 A real-data check of the permuted predictor's $\lambda$ (half a day, capped)

On CCRCC with the permuted predictor, $\theta_2$ and $\theta_3$, $n_L \in \{6, 8, 12\}$, 200 draws,
$\lambda$ under rules (a), (b) and (c); median and interquartile range per rule in
`results/round4/ppi/Q1_estimator/q1_permuted_lambda.csv`. The Q1 report explains why rule (a)
gives the permuted $\theta_2$ a donor-weighted $\lambda$ far from 0. Prediction, written by the
oversight chat before running: rules (b) and (c) give a median within 0.1 of 0 in every cell and
rule (a) reproduces Q0's figures. Recorded as prediction Q1.6.

### 11.4 The ACS source, replaced (half a day, capped, in parallel with Q1; reported under Q0)

The `ppi_py` file stays where it is and is used for no clustered unit.

- Authorisation for one download, and only this one. The 2018 ACS PUMS person file, 1-Year, for
  the 50 states and DC, through `folktables`
  (`ACSDataSource(survey_year='2018', horizon='1-Year', survey='person').get_data(states=[...], download=True)`).
  `folktables` may be installed into the track's environment.
- Raw files to `results/round4/ppi/Q0_setup/acs_pums2018/raw/` on Longleaf, every column kept,
  nothing committed; a parquet with an explicit `pa.schema` of all columns beside them;
  `PROVENANCE.txt` naming source URLs, `folktables` version and md5 of every downloaded file;
  stamped. Committed record `acs_pums2018_inventory.json` (rows per state, column list, md5s).
  32 GB memory.
- Task definition `results/round4/ppi/Q0_setup/acs_pums_task_def.json` in the A0 format.
  Population the folktables ACSIncome filter (`AGEP > 16`, `PINCP > 100`, `WKHP > 0`,
  `PWGTP >= 1`), survey weights not used and the file says so; the design-based target is the
  finite population of sampled persons passing the filter. Outcome $\log$ `PINCP`; $\theta_3$
  covariate `AGEP` standardised. Clusters `ST` (51 levels) and, as a second setting, PUMAs within
  the state with the most persons after the filter, named from the file. Predictor a
  gradient-boosted regression of $\log$ `PINCP` on `AGEP`, `COW`, `SCHL`, `MAR`, `OCCP`, `POBP`,
  `RELP`, `WKHP`, `SEX`, `RAC1P`, cross-fitted over five folds of states assigned by `zlib.crc32`
  of the state code, library defaults, no tuning, library, version and settings recorded.
  Unit-level, within-state and state-level $R^2$ recorded in the inventory as description only.
- If the network refuses, record it and stop the unit; the fetch is a standalone script with no
  Longleaf dependency so Nicolas can run it himself.
- The ACS units of Q2 and Q4 read this file, not the `ppi_py` one.

### 11.5 Procedure

- The lung wrapper's stamp stays as it is. Every later fan-out stamps from the sub-agent's own
  process, and the lead checks the frame id on each hand-back before commit.
- The gate pull request through GitHub's REST API is accepted; the report records the route.

### 11.6 What this does to work in flight

The fifteen Q1 simulation jobs and the Q1 acceptance job were submitted from `65ca58f` and are
still pending. They are cancelled before they start, the simulation and module are changed for
section 11.1 item 1 and section 11.2, committed, and the jobs resubmitted from the new commit. Two new parallel
units start alongside, the permuted-$\lambda$ check (section 11.3) and the ACS PUMS pull (section 11.4).

## 12. Decision of 30 September 2026 (Nicolas), where the Q1 simulation runs

All nineteen interval-1 jobs sat pending on Longleaf for one to three hours with none started
(28,720 jobs pending on `spill` at a median priority of 292, ours at 228 on `rc_tengfei_pi`).
Asked whether to keep waiting, Nicolas chose to run the fifteen simulation units locally. The
simulation uses synthetic data only.

- The fifteen pending simulation jobs are cancelled before they start.
- Each unit runs the committed `code/scripts/round4_ppi_q1_sim.py` at `de3d1f2` (md5
  `873dad7f383eb99826b2d0b990cd6914`, with `round4_ppi_estimator.py` md5
  `10c76fd4706435a2ad71a8c5f53fb938`) with the same arguments, on the local Mac, one unit per
  sub-agent, single-threaded BLAS. `PROVENANCE.txt` records the local host, platform, Python and
  library versions and wall time in place of the Slurm fields.
- The acceptance job, the permuted-lambda check and the ACS PUMS pull read Longleaf data and stay
  on Longleaf.
- The Q1 report lists this as a deviation from "run the planned analyses on UNC Longleaf through
  Slurm", with Nicolas's decision as its authority.

### 12.1 Extension of 1 October 2026 (Nicolas)

The formal module-acceptance run and the permuted-lambda check (section 11.3) were still pending on
Longleaf after about six hours. Both read only the B1 sufficient statistics regenerated by the Q0
anchor (`b1_suffstats__CCRCC__resnet50.npz`, 0.6 MB, harvested as an artifact, md5 recorded).
Nicolas chose to run both locally as well. Their Longleaf jobs are cancelled before starting, the
committed scripts run on the local Mac against the harvested file, and provenance records the
local host and the input's md5. The ACS PUMS pull (section 11.4) stays on Longleaf.

### 12.2 Extension of 2 October 2026 (Nicolas), interval 2

Recorded under memo section 7 (plan section 13.7) before any task moves. Nicolas wrote in chat, on
2 October 2026 at about 01:25 UTC: "if longleaf is cluttered then run anything you can locally".
Interval-2 jobs had waited one to nine hours on `spill` (`general` at 264 of 264 nodes) and then
ran for minutes. Under this extension the following run on the local Mac from committed code, with
provenance recording the local host, the commit, every script's and input's md5, and wall time.

1. Synthetic simulations with no cluster inputs: the theorem check with the oracle-lambda arm
   (`round4_ppi_q2_theorem_sim.py` at `de3b71f`) and any remaining Q1b work.
2. Q2 masking and Q3 regime comparison for every task whose inputs are prediction parquets small
   enough to copy (CCRCC, CCRCC merged, and the ACS parquets once converted, and Indiana and lung
   once their predictions exist), each copy checked by md5 against Longleaf.
3. Longleaf jobs of these tasks that have not started are cancelled before they start; jobs already
   running finish where they are.

What stays on Longleaf: steps that need the harness, the embeddings or the morphology files (the
Indiana and lung prediction steps, the ACS conversion that reads the 448 MB parquet, and the
recalibration test). The Q3 report lists every local run as a deviation from "run on UNC Longleaf
through Slurm", with this message as its authority.

### 12.3 Extension of 2 October 2026 (Nicolas), interval 2

Nicolas wrote in chat on 2 October 2026, about four hours after 12.2: he is unavailable to grant
permissions for about nine hours, so anything gated on his permission is worked around; local
compute is allowed and preferred where it genuinely speeds the work, until he says to stop; the
conformal track also uses the local machine. Consequences for this track: local runs are the
default for anything that does not need cluster-only data, at most four local processes at a
time and fewer when the machine is loaded; an action that would need his approval is replaced by
one that does not, or deferred, and recorded under escalations in the Q3 report (in particular, if
the gate push or pull request needs an approval, the branch is committed and tagged locally and
the push and pull request wait for him). The gate rule of section 13.1 is unchanged.

## 13. The Q1 decision memo (1 October 2026), transcribed before any of it is acted on

Source `docs/decisions/round4_ppi_Q1_decisions.md` (md5 `b7dafd175f42d55a21c5387437cd0dd3`),
written by the oversight chat and handed over by Nicolas. Interval 2 (Q2 and Q3, ending at the Q3
gate) starts when this transcription is committed. Where this section and the source differ, the
source governs.

### 13.1 Gate rule and state at hand-over

- Report-and-wait means no stage after a gated stage starts until the oversight chat has replied.
  Every stage, set up, staged or piloted. Inside an interval there are no interim reports and no
  interim stop conditions; anything that would have halted work is handled under the decision
  boundaries, recorded under "Escalations" in the next report, and work continues. Gates Q1, Q3, Q5.
  Contact with anyone outside the project is never the session's decision.
- The Q1 report is accepted. Q1.4's prediction had the wrong sign and is dropped from every later
  stage.
- The pull request. The memo asks the session to open it. At hand-over it already existed and was
  merged: pull request #2 from `round4-ppi`, merged into `main` by Nicolas with the merge commit
  `75e630a` over the branch head `2385298`. The session does not reopen it. The Q3 report records
  why the session's own attempt produced none (HTTP 403, the earlier token lacked
  `pull_requests=write`), and that the session's GitHub API calls on 1 October returned HTTP 401.
- The branch continues from `2385298`. `main` is never merged or pulled into it (section 10).
- Nicolas renamed the local working copy to `~/HEST-1k-replication-PPI`. It is this track's
  working tree from now on.

### 13.2 The working estimator for Q2 and Q3 (memo section 2)

1. Superpopulation target: complement form, cross-fitted $\lambda$, CR1 with $t_{n_L-2}$, no
   finite-population correction, no Welch-Satterthwaite.
2. Design-based target: textbook form with the finite-population correction, $t_{n_L-1}$,
   cross-fitted $\lambda$.
3. No bootstrap is an interval candidate from Q2 on, except Q1b addition 3 (section 13.3).
4. New rule (d), cross-fitted with a pre-test. Each half's $\lambda$ is zero unless its unclipped
   estimate exceeds $k$ times its own standard error, the ordinary standard error of the slope of
   the half's donor rectifier contributions on its donor prediction contributions over the half's
   donors (at least three donors in the half); otherwise the clipped estimate, as in rule (c).
   Rule (d1) has $k = 1$, rule (d2) $k = 2$. When $n_L < 6$, $\lambda = 0$ throughout (classical).
5. Every Q2 and Q3 row is computed under rules (c), (d1) and (d2); every table carries
   `lambda_rule`. The Q3 report proposes one; the Q3 memo finalises the definition.
6. `docs/round4_ppi_theory.md` states the pre-test as a corollary of the gain theorem under the
   $\lambda$ corollary: near-zero cluster-level $R^2$ leaves $\lambda$ unidentified and nearly
   harmless, and the pre-test reports zero there.

### 13.3 Unit Q1b, a Q1 supplement (memo section 3)

Run inside interval 2, reported with Q3. Five sub-agents by $G_L$, on Longleaf through Slurm,
capped at one and a half days. Outputs under `results/round4/ppi/Q1_estimator/q1b/`; the Q1
tables are not touched. Q1 generator and code paths, plus three additions.

- Grid: $G_L \in \{4, 6, 8, 12, 20\}$, $G_U = 20$, $m \in \{200, 1000\}$,
  $\rho \in \{0.1, 0.3, 0.5\}$, $r \in \{0, 0.5, 0.8\}$, both estimands and populations, both
  targets, 2,000 replicates per cell.
- Addition 1: rules (c), (d1), (d2), with CR1 $t$ and the textbook form.
- Addition 2: an unequal-size arm beside the equal-size arm, $m_g = m \cdot s_g$ with $s_g$ the
  24 CCRCC donors' spot counts over their mean, read from the task definition and recorded in the
  config, assigned by `zlib.crc32` of the donor index and recycled when $G > 24$. CR1 with
  $t_{G_L-1}$ and CR2 with Bell-McCaffrey df on both arms.
- Addition 3: on $\theta_3$ spot-weighted, superpopulation target, classical and rule (c) only,
  the wild cluster bootstrap-$t$ (Cameron, Gelbach and Miller 2008) on the labelled donors'
  influence contributions, 500 draws, Rademacher and Mammen weights as separate interval names,
  the unlabelled term held fixed.
- Predictions Q1b.1 to Q1b.4 are copied from the memo into section 4's list before Q1b runs.
- The real-data permuted check reruns under (d1) and (d2) on the same 50 genes and 200 draws, into
  `q1_permuted_lambda_d.csv`. Prediction: median $\lambda$ 0 in every donor-weighted cell, below
  0.1 in every spot-weighted cell. All genes only if that costs under two hours.

### 13.4 Primary estimand (memo section 4)

The donor-weighted population is the primary estimand of every real-data table from Q2 on. The
spot-weighted slope is reported beside it with the Q1 finding stated. The Q3 memo decides whether
the wild cluster bootstrap becomes the spot-weighted interval in Q4.

### 13.5 The Q2 theorem and its simulation check (memo section 5)

- The gain theorem is stated for the labelled term, with the full ratio
  $\sigma_{u,r}^2/\sigma_u^2 + n_L V_U/\sigma_u^2$, $V_U = \lambda^2 \text{Var}(p_g)/G_U$, beside
  it; it equals $1 - R^2_{\text{cluster}}$ only as $G_U/n_L \to \infty$.
- Under $\hat y = y - a - \epsilon$ the rectifier's cluster component is
  $(1 - \lambda)u_g + \lambda a_g$, with the endpoint at the optimal $\lambda$ unchanged.
- A sixth Q2 unit, the theorem check, on Longleaf, capped at half a day: $G_L \in \{6, 12\}$,
  $G_U \in \{20, 100\}$, $m \in \{200, 5000\}$, $\rho = 0.3$, $r = 0.5$,
  $\sigma_a^2/\sigma_u^2 \in \{0.25, 1, 4\}$, 2,000 replicates, rule (c), donor-weighted mean,
  superpopulation target. Output `results/round4/ppi/Q2_theory/q2_sim_theorem.csv` with the
  empirical variance ratio, $1 - R^2_{\text{cluster}}$ and the full ratio. Prediction Q2.7 is
  copied into section 4.
- Everything else in Q2 and Q3 runs as the instruction and addendum 1 say, under (c), (d1), (d2).

### 13.6 ACS (memo section 6)

Nicolas ran the fetch script on his machine; the output is `~/acs_pums2018` (read-only grant).
Nothing is downloaded again.

1. Read `raw_manifest.json` and `fetch_info.json` and record them, with the local path, in the Q3
   report.
2. Copy the directory to `results/round4/ppi/Q0_setup/acs_pums2018/` in the Longleaf project tree,
   verify every file's md5 there against `raw_manifest.json` into
   `acs_pums2018_transfer_check.csv`, and stamp the directory. One mismatch stops the ACS unit and
   goes to escalations.
3. Run `round4_ppi_acs_pums2018_analyze.py` on Longleaf through Slurm against that copy with 32 GB,
   and commit `acs_pums2018_inventory.json` and `acs_pums_task_def.json`. Raw files are not
   committed. The old job script is not resubmitted.
4. The ACS units of Q2 and Q4 run on Longleaf against the same copy.

### 13.7 Where interval 2 runs (memo section 7)

Every interval-2 job runs on Longleaf through Slurm, walls sized from a sibling's `sacct`.
Section 12's local decisions do not carry forward. Local runs only on Nicolas's request in chat,
each recorded first as a numbered extension of section 12. If a job has not started four hours
after submission, the session tells Nicolas in chat what it needs (inputs and sizes, memory,
expected runtime, queue state) and keeps waiting, without moving it, harvesting its inputs or
proposing a local run; independent work continues.

### 13.8 Procedure (memo section 8)

1. Every sub-agent brief states the sub-agent's own frame id; the lead checks each hand-back's
   stamp before merge.
2. The two `docs/WAYS_OF_WORKING.md` edits are applied by the oversight chat on `main`.
3. B1's check 4 stands; nothing to do.
4. The ten unresolved claims in pre-round-3 documents are a round-5 item.
5. In `docs/round4_ppi_estimator_definition.md` each `$$` goes on its own line, in the next commit;
   `docs/round4_ppi_theory.md` does the same from the start.
6. The Q0 `ppi_py` ACS file stays where it is and is used for nothing clustered.

### 13.9 What the Q3 report carries (memo section 9)

The instruction's Q2 and Q3 content, plus Q1b and the theorem check, scoring Q1b.1 to Q1b.4 and
Q2.7 beside Q2.1 to Q3.4, and proposals for the final $\lambda$ rule, CR1 or CR2, and the
spot-weighted interval. Report and wait.
