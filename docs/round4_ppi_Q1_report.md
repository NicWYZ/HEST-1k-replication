# Round 4, the PPI track, Q1 report (covering Q0 and Q1)

Instruction: `docs/decisions/round4_ppi_track.md`, with addendum 1
(`docs/decisions/round4_ppi_addendum1.md`) and the oversight notes on working copies and version
management. All of it is transcribed in `docs/round4_ppi_plan.md`, sections 1 to 12. Format: the
instruction's section 8. Branch `round4-ppi`. Date: 1 October 2026.

The estimator built here is not new. It is the survey-sampling difference estimator, and in its
PPI++ form the generalised regression estimator, with a donor-clustered sandwich. What Q1 settles is
which variant to use, against which target, and how it behaves with few labelled donors.

## 1. Stage and status

Q0 and Q1 are complete apart from one Q0 unit, and this report is the Q1 gate. The work stops here
until the oversight chat replies.

- The Q0 anchor passes. B1's rerun reproduces `results/round3/B1_ppi/b1_acceptance.csv` with a
  maximum difference of 0.0.
- The estimator module reproduces B1 in B1's configuration to about $10^{-15}$.
- All fifteen simulation units ran, at 2,000 replicates per cell.
- The addendum's permuted-$\lambda$ check ran.
- The one unit that did not run is the ACS PUMS 2018 pull (plan 11.4). Its Longleaf job sat
  pending until the twelve-hour cap and was cancelled before it started. Section 7 item 3 gives
  the detail.

Two decisions by Nicolas changed where things ran (plan section 12). The fifteen simulation units,
the module-acceptance run and the permuted-$\lambda$ check ran on the local Mac, because their
Longleaf jobs sat pending for hours with none started. Everything that needed Longleaf data had
already been harvested from it.

## 2. What was run

Commits on `round4-ppi`, oldest first:

- `47edb81`, instruction and plan;
- `ca96d3e`, the working-copy amendment;
- `d784aaf`, the version-management amendment;
- `65ca58f`, the Q1 code;
- `38e9c29`, the Q0 outputs;
- `df23ee2`, addendum 1;
- `de3d1f2`, the addendum-1 code;
- `80aa36e`, the merge script;
- `4eb13b4` and `413da2e`, plan section 12;
- then the commit carrying this report.

The Longleaf project tree stayed on `main` at `9d7277d` throughout. Code ran from the track clone
`/work/users/w/e/weiyang/hest_code/round4-ppi`.

Scripts, with the md5 of the committed file:

| script | md5 |
|---|---|
| `code/scripts/round4_ppi_estimator.py` | `10c76fd4706435a2ad71a8c5f53fb938` |
| `code/scripts/round4_ppi_q1_sim.py` | `873dad7f383eb99826b2d0b990cd6914` |
| `code/scripts/round4_ppi_q1_acceptance.py` | `4f1993e527e88277bd42f3137ea12336` |
| `code/scripts/round4_ppi_q1_merge.py` | `756f8ca93c72fc5db84a003a89d80a16` |
| `code/scripts/round4_ppi_q1_permuted_lambda.py` | `94fffd08ada0d6c5623094fd05db2a85` |
| `code/scripts/round4_ppi_q1_permuted_mechanism.py` | `552ca5fcc5ca8425948e067a6811416e` |
| `code/scripts/round4_ppi_data.py` | `2a26eb3ce74815e3e7c63cccd0527398` |

Jobs. `results/round4/ppi/Q1_estimator/q1_slurm_jobs.csv` lists all 42 Slurm jobs of this track,
each with its account, partition, state, submit and start times, elapsed time, node and the
intent it was submitted with. They were matched to the session's job ledger by job name.

- **Longleaf, Q0.** These ran on `rc_tengfei_pi`, partition `spill`, and
  `results/round4/ppi/Q0_setup/q0_lead_verification.md` records them.
  - Slurm 3074938, the B1 anchor, on node c151417, elapsed 00:10:30.
  - Slurm 3074935, the lung reader, on node c151412, elapsed 00:00:24.
  - Slurm 3078654 and 3078825, the ACS `ppi_py` fetch and its task definition.
  - Slurm 3074937 was a first ACS attempt that failed on the unit's own import-path bug.
- **Local.** The fifteen simulation units took 2,594 s to 3,367 s of wall time each, with all 15
  running at once (`results/round4/ppi/Q1_estimator/q1_unit_walltimes.csv`, which also lists each
  unit's 9,600 rows and the frame id in its stamp).
- **Cancelled before starting.** 37 jobs were cancelled while still pending, with elapsed 00:00:00,
  so none produced anything. They were submitted before an instruction changed the code or the
  site:
  - 3074092, 3074101 and 3074111, before the working-copy note;
  - 3082178 and the fifteen first-round simulation jobs from 3082461 to 3082548, before addendum 1;
  - the fifteen second-round simulation jobs from 3114712 to 3114729, then 3114810 and 3115093,
    before Nicolas moved the work to the local machine.
  - 3115277, the ACS PUMS unit, cancelled by the run-clock ceiling at its twelve-hour cap.

Each local `PROVENANCE.txt` records the platform, library versions, the md5 of every script and
input, the command line and `PYTHONHASHSEED`.

## 3. Acceptance checks

Source: `results/round4/ppi/Q1_estimator/q1_acceptance.csv`, and for Q0
`results/round4/ppi/Q0_setup/anchor/q0_anchor_compare_summary.json` and
`results/round4/ppi/Q0_setup/lung_wrapper/q0_lung_wrapper_check.csv`.

1. **Q0 anchor.** 92 of 92 CCRCC rows of `b1_acceptance.csv` reproduced, with a maximum absolute
   difference of 0.0. Passes.
2. **Lung reader.** `NCBI865` has 2,143 embedding rows and 2,142 after the drop, on all three
   encoders. The subset relation holds after the drop and fails without it. Rows equal the task
   file's `n_patch_spots` on all 60 sample-encoder pairs. Controls removed: 0 on lung, 61 on breast.
   Passes.
3. **Module in B1's configuration.** The module reproduces all 1,200 CCRCC rows of
   `b1_estimates.csv` to $8.9 \times 10^{-16}$ and all 92 CCRCC rows of `b1_acceptance.csv` to
   $1.3 \times 10^{-15}$. Passes.
4. **At $m = 1$, clustered variance equals the i.i.d. one.** CR1 and CR2, under the classical, B1 and
   cluster-tuned rules, agree to at most $1.4 \times 10^{-15}$ relative difference. Passes. The
   cross-fitted rule is left out of this check, because at $m = 1$ it equals the stratified i.i.d.
   form by construction, so the check could not fail.
5. **At $r = 0$, $\lambda$ within 0.05 of 0.** This is scored on the superpopulation arm.
   - The largest cell median is 0.032 under rule (a) and under rule (b). Passes on the median.
   - The mean fails (0.253 and 0.274), because a clipped estimator of zero has a positive mean.
   - Rule (c) fails, with a largest cell median of 0.382 and a median over cells of 0.15. Its
     reported $\lambda$ averages two half-sample values, each clipped at 0, so it is zero only when
     both are.
   - In the design arm, $\lambda$ is reported and not scored, because a fixed population of 24
     donors has a non-zero finite-population covariance between $y$ and an independent predictor.
6. **At $r = 0$, coverage in [0.89, 0.91].** Scored on the variants addendum 1 names, the band holds
   in only part of the cells:

   | variant | cells inside the band | inside the band widened by 2 MC se |
   |---|---|---|
   | CR2 with Satterthwaite, every $G_L$ | 0.446 | 0.729 |
   | CR1 at $G_L \ge 6$ | 0.492 | 0.8025 |
   | bootstrap-$t$ | 0.277 | 0.539 |
   | textbook form with FPC | 0.378 | 0.609 |

   The failures are concentrated in $\theta_3$ spot-weighted (section 6.4). Fails as scored.
7. **At $G_L = 20$ and $m = 200$, analytic variants within 0.02 of each other.** The largest coverage
   spread is 0.0135 in the superpopulation arm and 0.0 in the design arm. Passes. With the three
   bootstraps included, the spread is 0.0805 and 0.0745. That fails, because the bootstraps
   under-cover.

## 4. What differs between the arms of each comparison

- **Superpopulation against design-based target.** What differs:
  - whether the donors are redrawn every replicate or fixed once per cell;
  - the population of $G = 24$ against $G_L + G_U$ fresh donors;
  - the estimator form, complement in one and textbook or complement in the other;
  - the truth, the model value against the fixed population's value;
  - the covariate constants, known (0, 1) against the fixed population's.
- **Textbook against complement form (design arm).** What differs is whether the prediction term
  averages all $G$ donors or only the unlabelled ones, and the variance (finite-population formula
  against a cluster-robust sum of two terms). The $\lambda$ rule, data and draws are the same.
- **$\lambda$ rules (a), (b), (c).** What differs is the variance minimised (spot i.i.d. against
  donor-clustered, for the spot-weighted population only), the zero threshold at $G_L < 4$, and
  whether $\lambda$ is tuned on the donors it is applied to. For the donor-weighted population (a)
  and (b) are the same formula. Data, draws and variance are the same.
- **CR1, CR2, WS.** What differs is the leverage adjustment, the degrees of freedom of the
  reference, and whether the $U$ term's degrees of freedom enter. With equal cluster sizes, CR2
  equals CR1 exactly.
- **Classical against PPI.** The same draws and the same interval method; only $\lambda$ differs.

## 5. Predictions against outcomes

Numbers from `results/round4/ppi/Q1_estimator/q1_report_numbers.csv` (superpopulation rows unless
stated) and `results/round4/ppi/Q1_estimator/q1_permuted_lambda.csv`.

| # | prediction | outcome | score |
|---|---|---|---|
| Q1.1 | CR1 $t_{G_L-1}$ covers 0.87 to 0.91 at $G_L \ge 6$ and 0.82 to 0.88 at $G_L = 4$; CR2 brings $G_L = 4$ to 0.87 or above | Medians at $G_L \ge 6$: classical 0.898, rule (a) 0.8895, rule (c) 0.9005. At $G_L = 4$: rule (a) 0.8735 and rule (b) 0.856, inside the band, but classical 0.8978 and rule (c) 0.902, above it. CR2 equals CR1 in this design | partly held; CR2 not tested |
| Q1.2 | percentile bootstrap under-covers by at least 0.10 at $G_L \le 8$; bootstrap-$t$ within 0.03; BCa between | Percentile medians (rule c) 0.760, 0.8135, 0.8355 at $G_L$ = 4, 6, 8, a shortfall of at least 0.10 only at 4. Bootstrap-$t$ 0.8518 at 4 (outside 0.03), 0.8718 at 6, 0.8795 at 8. BCa 0.7588 at 4, no better than percentile | partly held |
| Q1.3 | with FPC and design target, coverage at 12 of 24 is 0.89 to 0.92; cross-fitting moves it by less than 0.02 at under 3% width | Textbook FPC median 0.8932 (rule c), 0.889 (rule a). The complement form without FPC covers 0.9768, reproducing B2's over-coverage. Rule (c) minus rule (a) median 0.0038 (largest 0.0995), at a median width ratio of 1.0323 | coverage held; width cost 3.2%, just over |
| Q1.4 | WS matters only at $G_U \le 10$, widening by 5% or more | WS narrows at every $G_U$, with median width 0.9611, 0.96 and 0.967 of the $t$ interval at $G_U$ = 10, 20, 50, and under-covers (0.8602 at $G_L = 4$) | refuted |
| Q1.5 | width ratio below 0.9 only when $r \ge 0.5$ and $\rho \le 0.3$; above 0.9 for every $r$ at $\rho = 0.5$ | At $\rho = 0.5$ the medians are 0.8927 at $r = 0.5$ and 0.8651 at $r = 0.8$ | refuted, as plan section 8 item 3 expected |
| Q1.6 | rules (b) and (c) median within 0.1 of 0; rule (a) reproduces Q0 | Rule (a) at B1's draw gives 1.0, 0.8604, 0.4612. Over 200 draws, (b) has donor medians 0.522, 0.495, 0.346 for $\theta_2$, and (c) gives 0.5 in every donor cell | rule (a) held; (b) and (c) refuted |

## 6. Results

### 6.1 Superpopulation target

From `results/round4/ppi/Q1_estimator/q1_report_numbers.csv` and
`results/round4/ppi/Q1_estimator/q1_coverage_by_G.csv`; figure
`results/round4/ppi/Q1_estimator/fig_q1_coverage_by_G.png`. Coverage is the median over 432 cells
per $G_L$ (288 at $G_L = 20$), with each cell's MC standard error near 0.007.

- **Classical with a CR1 $t_{G_L-1}$ interval.** Covers 0.898 at $G_L = 4$, so the small-$G$ $t$
  reference is enough for the classical estimator with equal cluster sizes.
- **PPI.** Inherits a small-$G$ problem from tuning $\lambda$ on the donors it is evaluated on.
  Rule (a) covers 0.8735 at $G_L = 4$ and rule (b) 0.856, while cross-fitting restores 0.902.
- **Widths, for $r > 0$.** The median PPI-to-classical width ratio is:

  | rule | $G_L = 4$ | $G_L = 20$ |
  |---|---|---|
  | (a) | 0.7365 | 0.8707 |
  | (b) | 0.6055 | 0.8044 |
  | (c) | 1.009 | 0.8667 |

  At $G_L = 6$ to 12, (c) is 0.8655 to 0.8465. So the rules that under-cover are also the ones that
  look narrowest, and cross-fitting gives back the gain at $G_L = 4$.
- **FPC applied against the superpopulation target.** Coverage falls from 0.8885 at $G_L = 4$ to
  0.8078 at $G_L = 20$, which is the expected sign. The correction belongs to the design target.

### 6.2 Design-based target

From `results/round4/ppi/Q1_estimator/q1_report_numbers.csv`.

- **Textbook form with FPC and cross-fitting.** Covers 0.8915 to 0.894 at every $G_L$. With
  rule (a) it covers 0.8442 at $G_L = 4$, rising to 0.8958 at 20.
- **Complement form without FPC (B1's).** With rule (a) it covers 0.9768 at $G_L = 12$. Classical
  covers 0.9995 at $G_L = 20$. FPC on the complement form brings rule (a) at $G_L = 12$ to 0.9158.
- **Reading.** B2's over-coverage at $n_L = 12$ is mostly the missing correction together with the
  complement form, and the textbook form removes it.
- **Width.** For $r > 0$ the textbook PPI-to-classical median width ratio is 0.8284 (rule a) and
  0.8237 (rule c).

### 6.3 The chosen estimator

`docs/round4_ppi_estimator_definition.md` states it. It is cross-fitted $\lambda$ in both arms,
with the complement form, CR1 and a $t_{n_L-2}$ reference against the superpopulation target, and
the textbook form, its finite-population variance and $t_{n_L-1}$ against the design-based target.
This is a proposal for the oversight chat's decision.

### 6.4 Where intervals fail

From `results/round4/ppi/Q1_estimator/q1_report_numbers.csv`.

The minimum coverage of the classical CR1 interval is 0.8015, and it occurs on $\theta_3$
spot-weighted. On $\theta_3$ spot-weighted at $\rho = 0.1$ with $m \ge 1000$, the median coverage
is 0.8445 while the empirical sd over the root mean estimated variance is 0.9908. The variance is
right and the reference distribution is not. The donor-level contribution
$\bar z_g = \text{mean}_i\,(m_{gi} y_{gi})$ contains products of donor effects, $c_g u_g$ and
$\beta c_g^2$, so it is skewed. On the mean and on $\theta_3$ donor-weighted, the classical minima
are 0.8805 and 0.8815.

### 6.5 The permuted predictor's $\lambda$ (addendum 1 section 3)

From `results/round4/ppi/Q1_estimator/q1_permuted_lambda.csv` and
`results/round4/ppi/Q1_estimator/permuted_mechanism/q1_permuted_lambda_mechanism.csv`.

- **Scope.** The check runs on 50 genes of CCRCC, not all of them (the `n_genes` column), with 200
  draws, so its medians are provisional.
- **Reproduction.** B1's own draw is reproduced by rule (a), giving donor medians 1.0, 0.8604 and
  0.4612 for $\theta_2$.
- **Over 200 draws.** The rule (a) donor medians are 0.522, 0.495 and 0.346 at $n_L$ = 6, 8, 12.
  For $\theta_3$ the pooled medians are 0.465, 0.641 and 0.618. The median over draws of each
  draw's median is 0.0668 at $n_L = 6$ but 0.4011 at 8 and 0.624 at 12, so B1's $\theta_3$
  figure of 0 at every $n_L$ is a property of its single draw.
- **Mechanism.** The donor-pairs $\lambda$ is a clipped slope of the labelled donors' $t_g$ on
  $\hat t_g$. The permuted predictor's donor values hardly vary, with sd($t$)/sd($\hat t$) at a
  median 3.943 over genes for $\theta_2$ and 10.299 for $\theta_3$. Its slope is therefore noisy at
  six to twelve donors. Clipping to $[0, 1]$ turns that noise into point masses at both ends:
  $\lambda = 0$ in 0.3413 and $\lambda = 1$ in 0.38 of the $\theta_2$ cells at $n_L = 6$.
- **Shared realisation.** One permutation is shared by every gene, and genes are correlated, so the
  noise does not average out over genes. The full-sample slope over all 23 donors has median 0.985
  over genes for $\theta_2$. The lead's rebuild matches B1's sufficient statistics to
  $4.9 \times 10^{-8}$
  (`results/round4/ppi/Q1_estimator/permuted_mechanism/q1_permuted_lambda_mechanism_check.csv`).
- **Spot-weighted population.** The large $\lambda$ there is the covariance-estimand effect round 3
  already recorded.

### 6.6 Q0 records

The lung task file says 20 samples, 15 donors, 343 target genes and one dropped barcode, as in plan
section 7. The ACS file from `ppi_py` holds 380,091 incomes in dollars, with predictions and an
unlabelled age-and-sex array, and no state, PUMA or year
(`results/round4/ppi/Q0_setup/acs/acs_inventory.json`).

## 7. Discrepancies, open questions and escalations

### Escalations

1. **Execution site.** Plan sections 12 and 12.1, Nicolas's decisions: the simulation, the
   module-acceptance run and the permuted-$\lambda$ check ran locally. The instruction says Longleaf
   through Slurm. These outputs are therefore not byte-comparable to a node run, and their
   provenance records the local host.
2. **Sub-agent frame ids.** Six stamps carried the lead's frame id: the lung wrapper, and five
   simulation fragments in their first versions. The cause is that a sub-agent's context shows the
   lead's id, and some sub-agents copied it into the stamp. The five simulation stamps were
   re-stamped by their own sub-agents before merge, and the lead checked every fragment's stamp
   against the sub-agent's frame id. The lung stamp stays as it is, per addendum 1. Proposed fix
   for the briefs: give each sub-agent its own frame id explicitly.
3. **ACS PUMS 2018 (plan 11.4) reached its cap without running.**
   - Slurm 3115277 sat pending on `spill` from 30 September 16:56 local time until the
     twelve-hour cap, and was cancelled with elapsed 00:00:00 and no node
     (`results/round4/ppi/Q1_estimator/q1_slurm_jobs.csv`).
   - Nothing was downloaded, and the one authorised download is unused. The directory
     `results/round4/ppi/Q0_setup/acs_pums2018/` does not exist on Longleaf, so there is no
     inventory and no task definition to commit.
   - The fetch and analysis scripts are committed unrun as
     `code/scripts/round4_ppi_acs_pums2018_fetch.py` and
     `code/scripts/round4_ppi_acs_pums2018_analyze.py`. The fetch script is standalone.
   - The queued job script carried the lead's frame id in its stamp call, although the brief gave
     the unit its own id. No stamp was written, because the job never ran. The job script is not
     committed, and it should not be resubmitted as it stands.
   - Options for the memo:
     - resubmit with the corrected stamp and a shorter wall of about 1.5 hours;
     - have Nicolas run the fetch script on his own machine, with the analysis on its output;
     - drop ACS from Q2 and Q4.
   - The ACS units of Q2 and Q4 cannot start until one of these is done.
4. **CR2 cannot be assessed in this simulation.** Every donor has $m$ spots, so CR2 equals CR1 and
   the Bell-McCaffrey df equal $G_L - 1$. Real data has unequal donors. Proposal: add an
   unequal-size arm, for example $m_g$ drawn from CCRCC's spot counts, before CR2 is accepted or
   rejected.
5. **B1's check 4 is not the identity the instruction names.** The instruction words it as
   "donor-weighted $\lambda$ is 0". B1's check 4 is a width ratio against 0.95, and it fails on 21
   of 36 CCRCC rows in the committed file and in the rerun alike
   (`results/round4/ppi/Q0_setup/anchor/run/b1_acceptance.csv`).
6. **The $r = 0$ acceptance band fails broadly.** The main reason is section 6.4's skew. The band is
   also about 1.4 MC standard errors wide at 2,000 replicates.
7. **The ACS `ppi_py` file lacks clusters.** Addendum 1 replaces it, and it is used for nothing
   clustered.
8. **`whose()` on `results/round4/data/`.** The verdicts were `unstamped` and `foreign_session` (the
   data-pull session). These directories are inputs only and nothing was rebuilt (plan section 7).

### Discrepancies and records

- The merged table is committed gzipped (`q1_sim_coverage.csv.gz`, 144,000 rows), because the
  plain file is 44 MB. The fifteen per-unit fragments are kept as session artifacts and are not
  committed.
- `design_exact_t`, the linearised design variance of the complement form, was a proposal of plan
  section 8 item 6. It stays in the table as a labelled variant. Addendum 1's textbook form
  supersedes it.
- The Longleaf project tree had one `git fetch` before the working-copy note, which changed only its
  remote-tracking refs (plan section 10).
- Unspecified simulation constants were fixed in the config: $\mu = 0$, $\beta = 0.3$, and a
  covariate between-donor share of 0.3 (`q1_sim_config__*.json`).

- The full numeric-claim gate of `docs/WAYS_OF_WORKING.md` passes on every `docs/round4_ppi_*.md`
  file and on the deck outline. It still exits non-zero on ten claims in
  `docs/deck_speaker_scripts.md` and `docs/first_year_ST_project_proposal.md`. This branch does
  not touch those files, so the claims come from `main` and are left for the oversight chat.
  Five exceptions were added to `.verify-exceptions`, each with its source: one rounding of a
  stored value, one Monte Carlo standard error, and three queue-snapshot figures with no file.
- This report was first tagged as `round4-ppi-Q1` at `768b43a`, while the ACS PUMS unit was
  still pending. The unit then reached its cap, and one further commit records that outcome, the
  50-gene scope of the permuted check and the two unrun ACS scripts. The tag was not moved. The
  pull request head is the later commit.

### Proposed edits to shared documents, for the oversight chat to merge

- **`docs/WAYS_OF_WORKING.md`, scheduler.** On 30 September a queue snapshot showed our jobs at
  priority 228 on `rc_tengfei_pi` against a median of 292 over 28,720 pending jobs on `spill`, and
  none of the Q1 jobs started in hours. For work that reads no Longleaf data, ask before waiting.
- **`docs/WAYS_OF_WORKING.md`, sub-agents.** Each sub-agent brief states the sub-agent's own frame
  id for stamps.

## 8. What was not checked

- CR2 against CR1 with unequal cluster sizes.
- Any Q1 component on real data beyond B1's configuration and the permuted-$\lambda$ check.
- Bootstraps with a finite-population correction.
- The Q3 regime B arm of the simulation, which is Q3's.
- Cross-node determinism, since the simulation ran on one machine.
- The ACS PUMS data and its predictor, because the unit did not run.
- The permuted-predictor $\lambda$ on all genes, rather than the 50 used.

## 9. Proposed next step

The Q1 decision memo should settle the following:

1. The estimator in section 6.3.
2. Whether to add an unequal-cluster-size arm so CR2 can be judged.
3. How to treat the skew of $\theta_3$ spot-weighted at small $\rho$.
4. Whether the Q2 statement of the gain theorem takes the $G_U$ condition and the $\sigma_a^2$ axis
   (addendum 1 items 3 and 4).
5. Which of the three ACS options in section 7 item 3 to take.

Nothing in Q2 starts before the memo.
