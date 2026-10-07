# Round 5, the inference track: the interval validated, and estimators and designs under which a gain is real

7 October 2026. Prepared by the oversight chat for a fresh Claude Science session. This document is self-contained. The track starts from `main` of `NicWYZ/HEST-1k-replication` at the commit that carries this document, on its own branch `round5-ppi`, and runs concurrently with a second session on branch `round5-conformal`, which has its own document. Section 5 says how the two coexist. Read this document fully, then transcribe section 6 into `docs/round5_ppi_plan.md` before running anything.

---

## 1. Your role and the people

You are the execution agent. A separate chat session, the oversight chat, reviews your reports, makes scope decisions and writes decision memos, which Nicolas hands to you in full. Nicolas Weiyang Zhang (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`) is the first-year biostatistics PhD student whose project this is. He reads every command before it runs and will ask why. His advisors are Dr. Hongtu Zhu and Dr. Daiwei (David) Zhang at UNC. The target is a submittable paper by spring 2027.

Your responsibilities are to run the planned analyses on UNC Longleaf through Slurm, verify every stage's output against an expected value before moving on, write stage reports in the format of section 8, commit and push on your branch, and stop at each gate. You do not make scope decisions. Anything this document does not cover is reported as a proposal, not done.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

This track's gates are E2, E4 and E5.

**How Nicolas wants things written.** Plain, natural prose. No em-dashes. No colon-then-explanation constructions. No compressed or clever phrasing. Math as LaTeX, with each `$$` on a line of its own. Numbers quoted at the precision the comparison needs, with the relative scale stated. Full precision stays in the files. Every number in a report is read back from the file named beside it. A derivation shows every expression and skips only algebra, and says where a step of algebra is skipped. Do not inflate length.

---

## 2. The project, and what this track is for

### 2.1 In one page

Spatial transcriptomics measures gene expression at known spots on a tissue section. A frozen pathology foundation model maps each spot's H&E patch to an embedding, and a linear head (standardise, PCA to 256, ridge with an intercept in float64) predicts $y = \log(1 + \text{count})$ per gene. Spots are nested in slides and slides in donors. The second data set is ACS PUMS 2018 income, with people nested in states or in California PUMAs. In the paper's language a donor or a state is a cluster and a spot or a person is a unit.

The paper is "Labelling budgets for prediction-powered inference with clustered data". It is methodology first, with spatial transcriptomics as the main application and census income as the second. Prediction-powered inference (PPI) is the survey-sampling difference estimator (Mozer, arXiv:2603.19160), so the estimator is not new and the paper says so. What the paper adds is what the estimator does when units are nested in clusters, labels are bought by the cluster and by the unit, and only a handful of clusters can be labelled.

Round 4 ran two tracks and closed on 3 October. Its inference results are these, each with its file.

1. **A valid interval with 4 to 12 labelled clusters.** A cross-fitted tuning coefficient $\lambda$, a cluster-level variance, a $t$ reference, the finite-population factor for a design-based target, and one extra variance term for the cross-fitted coefficient (`docs/round4_ppi_estimator_definition.md`).
2. **What predictions buy.** With whole clusters labelled, the variance ratio against the classical estimator tends to $1 - R^2_{\text{cluster}}$, the cluster-level $R^2$ of the donor contributions. This is the cluster-randomised-trial formula for a covariate, carried over to a black-box predictor (`docs/round4_ppi_theory.md` sections 2 and 5.1).
3. **The price of tuning.** Cross-fitting $\lambda$ on half the labelled clusters costs variance, and predictions pay for it only when $n_L > 4 + 2/R^2_{\text{cluster}}$. This is the rule of Mani, Xu, Lipton and Oberst (arXiv:2505.20178) with clusters in place of units (`docs/round4_ppi_theory.md` section 5.2).
4. **Where to put the labels.** Labelling a few units in every cluster (regime B) gave narrower intervals than labelling a few clusters fully (regime A) in 216 of 232 comparisons when a cluster costs as much as 10 units (`results/round4/ppi/Q4_tables/q4_report_numbers.csv`). A literature check on 4 October did not find this comparison anywhere, and the paper is planned to lead with it.
5. **One design for both targets.** Tens of labelled units in every cluster serve the confidence interval and the prediction set for a new cluster together (`results/round4/ppi/Q5_joint/q5_joint_design.csv`).

The closing page of `docs/round4_ppi_final_report.md`, "What the PPI track established", is the summary, and its section 10 is the closing unit Q5a. `docs/deck2/deck2_new_results_explained.md` explains each result with its theory, and `docs/deck2/deck2_literature_check.md` says what is and is not new.

Three things were left unestablished, and this track exists for them.

- The final design-target tuning rule and the corrected variance were never run in simulation. On the real tasks the final interval covers 0.84 to 0.87 on kidney cancer, 0.88 to 0.91 on Indiana kidney and 0.85 to 0.87 on lung at 6 or more labelled donors (`results/round4/ppi/Q4a_recompute/q4a_table61.csv`).
- Regime B was never run below 6 labelled spots per donor on a tissue task (`results/round4/ppi/Q4_tables/q4_main_table.csv`).
- In regime B a permuted predictor, which carries no information, narrows the interval to 0.87 of the classical width on kidney cancer and 0.66 on lung, against 0.80 to 0.84 and 0.42 to 0.49 for the encoders (`q4_main_table.csv`). No check has said how much of regime B's gain is the predictor.

**What the advisors have seen.** Dr. Zhu and Dr. Zhang have seen the project up to the pivot and the originality check. They have not yet seen the round-4 results. Nothing in this round is a response to their feedback. Whether a few labelled spots per donor can be bought on a spatial platform, and at what cost, has not been asked of them. Treat regime B as general methodology and keep the cost ratio a free parameter.

### 2.2 What this track is for, and what is and is not new

Four jobs, in this order.

1. **Validate the final interval in simulation** (E1), and say why it covers below nominal on the real tasks.
2. **Complete regime B** (E2). Run it at 2 to 100 labelled units per cluster, and measure what part of its gain a predictor with no information reproduces.
3. **Put the estimators in regression form** (E3). The oversight chat's reading of the round-4 files, set out in section 2.4, is that the classical comparator in regime B has no intercept, so that any constant predictor appears to help. E3 builds a two-level estimator with an intercept and a coefficient for each level, and restates the design result of round 4 with it.
4. **Choose which clusters to label** (E4). Every prediction is known before any label is bought, so the labelled clusters can be chosen to be balanced on the predictions. Balance obtains by design what $\lambda$ obtains by estimation, and it has no tuning cost.

On originality. Everything this track builds is in the survey-sampling textbooks. Regression estimators for two-stage sampling with auxiliary information at both levels are in Särndal, Swensson and Wretman (1992, chapter 8). Balanced and rejective selection are in Deville and Tillé (2004) and Fuller (2009). The oversight chat is checking the literature for E3 and E4 in parallel. Do not claim novelty in any document. Say what was built and what it did.

### 2.3 The methods, stated once

**Notation.** Cluster $g = 1, \dots, G$ has $M_g$ units, and $N = \sum_g M_g$. Unit $i$ of cluster $g$ has outcome $y_{gi}$ and prediction $\hat y_{gi}$. Every estimand is the mean of a per-unit scalar $z_{gi} = w_{gi}\,y_{gi}$ with label-free weights $w_{gi}$ computed from all units, and its prediction counterpart is $f_{gi} = w_{gi}\,\hat y_{gi}$. For the mean, $w = 1$. For the within-cluster slope $\theta_3$ on a covariate $x$, $w_{gi} = (x_{gi} - \bar x_g)/v_g$ with $\bar x_g$ and $v_g$ the cluster's own mean and variance of $x$. For the group difference $\theta_2$, $w_{gi} = 1/\pi_{g,\text{neo}}$ on neoplastic-dominant spots and $-1/\pi_{g,\text{str}}$ on stromal-dominant spots. On the tissue tasks $x$ is standardised mean nuclear area. On ACS, $\theta_3$ is the slope of log income on standardised age and $\theta_2$ is the mean of log income. Cluster means are $\bar z_g$ and $\bar f_g$, and cluster totals are $Z_g$ and $F_g$.

**Two populations.** Donor-weighted, the average over clusters of the cluster's own value, which is the primary estimand. Spot-weighted, the pooled value over all units. For $\theta_2$ and $\theta_3$ donor-weighted, $\sum_i w_{gi} = 0$ within every cluster.

**Two targets, named on every row.** The design-based target is the value on the fixed set of $G$ clusters in hand, and real-data coverage is always of this target. The superpopulation target is the value in the population the clusters were drawn from, and it can only be checked in simulation.

**Regime A** labels $m$ units on each of $n_L$ clusters and none on the others. **Regime B** labels $m$ units, drawn uniformly without replacement, on every one of the $G$ clusters. Predictions exist on every unit of every cluster in both.

**The final design-target estimator of round 4**, regime A with every unit of a labelled cluster labelled, donor-weighted.

$$
\hat\theta = \frac{c_U}{G}\sum_{g=1}^{G}\bar f_g + \frac{1}{n_L}\sum_{g \in L}\big(\bar z_g - \lambda_g \bar f_g\big), \qquad \widehat{\text{Var}} = \Big(1 - \frac{n_L}{G}\Big)\frac{s_e^2}{n_L}
$$

Here $\lambda_g$ is the cross-fitted coefficient of cluster $g$ under rule `c_crossfit_design`. The labelled clusters are split in two halves, each half's coefficient is the least-squares slope of $\bar z_g$ on $\bar f_g$ over that half, clipped to $[0, 1]$, and it is applied to the other half. $\lambda = 0$ when $n_L < 6$. $c_U$ is the average of $\lambda_g$ over the labelled clusters. $s_e^2$ is the sample variance over labelled clusters of

$$
e_g = \bar z_g - \lambda_g \bar f_g + (\lambda_g - c_U)\,\bar F, \qquad \bar F = \frac{1}{G}\sum_{g=1}^{G}\bar f_g
$$

and the reference is $t_{n_L - 1}$. The last term of $e_g$ is the linearised term added in Q5a. In the tables this interval is `textbook_t|fpc|lin` and the interval without the last term is `textbook_t|fpc`. The full definition, the spot-weighted form and the superpopulation form are in `docs/round4_ppi_estimator_definition.md`.

**Regime B as round 4 ran it.** For cluster $g$ the estimate is the mean of $f$ over all its units times $\lambda_g$ plus the labelled units' mean of $z - \lambda_g f$. The coefficient is cross-fitted over two halves of the clusters as the pooled within-cluster slope of $z$ on $f$, clipped to $[0, 1]$. The design variance is $\frac{1}{G^2}\sum_g (1 - m_g/M_g)\,s^2_{r,g}/m_g$ with $s^2_{r,g}$ the labelled units' sample variance of $z - \lambda_g f$, and the reference is $t$ on $\sum_g (m_g - 1)$ degrees of freedom. The code is `regime_b` in `code/scripts/round4_ppi_q3_regimes.py`.

**Validation by masking.** The full data define the truth. Labelled clusters and labelled units are drawn 200 times with crc32 seeds, the interval is computed on each draw, and coverage of the full-data value is recorded. Variance ratios are empirical variances across the draws.

**The controls.** The permuted predictor is the `resnet50` prediction with rows permuted across the whole task, so it carries no information about any unit. This round adds two more. The constant predictor gives every unit the task-wide mean of the `resnet50` prediction for that gene. The donor-constant predictor gives every unit its own cluster's mean of the `resnet50` prediction. All three are label-free. On ACS they are built from the package predictor.

### 2.4 The level term, the oversight chat's reading that E2 tests

This is a reading of the round-4 files, not an established result. E2 tests it before E3 builds on it.

In regime B the classical estimate of a cluster's slope is the labelled units' mean of $z_{gi} = w_{gi}\,y_{gi}$. The outcome is not centred. Write $y_{gi} = \mu_g + \beta_g \tilde x_{gi} + \epsilon_{gi}$ with $\tilde x = x - \bar x_g$, so that $w = \tilde x / v_g$. If $\tilde x$ is symmetric within the cluster and $\epsilon$ is independent of it with variance $\sigma_g^2$, then

$$
\text{Var}(z_{gi}) = \frac{\mu_g^2 + \sigma_g^2}{v_g} + \beta_g^2\Big(\frac{\kappa_{4,g}}{v_g^2} - 1\Big)
$$

with $\kappa_{4,g}$ the fourth central moment of $x$ in the cluster. The term $\mu_g^2 / v_g$ comes from the level of the outcome and has nothing to do with the slope. A constant predictor $\hat y = c$ has $f = c\,w$, and regressing $z$ on $f$ removes exactly that term. So in regime B any predictor with a non-zero mean buys variance, and the round-4 comparator is a classical estimator that a statistician would not use, since the ordinary regression slope centres the outcome.

Four facts in the files agree with this.

- On ACS the permuted predictor has a within-cluster $R^2$ of 0.98 for the slope and 0.00 for the mean, where $w = 1$ and there is no weight to multiply a level (`results/round4/ppi/Q2_theory/q2_cluster_r2.csv`, scale `z`).
- For $\theta_2$ on kidney cancer the permuted predictor's within-cluster $R^2$ is 0.37, the same as `hoptimus0`'s 0.37, and on Indiana it is 0.32 against 0.18 (`q2_cluster_r2.csv`).
- For $\theta_3$ the permuted predictor's regime B width ratio is 0.87 on kidney cancer, 0.88 on Indiana, 0.66 on lung and 0.15 on ACS, against 0.80 to 0.84, 0.83 to 0.84, 0.42 to 0.49 and 0.08 for the real predictors (`q4_main_table.csv`, design target, donor-weighted, unit cost).
- The fitted optimal number of units per cluster at a cost ratio of 100 moves as far with the permuted predictor as with a real one. On kidney cancer it is 121 for the classical estimator, 108 with `hoptimus0` and 111 with the permuted predictor. On lung it is 172, 121 and 96. On census by state it is 379, 89 and 97 (`results/round4/ppi/Q2_theory/q2_report_numbers.csv`, $\theta_3$, donor-weighted).

If the reading holds, three round-4 statements change. Regime B's width against classical overstates what the encoders buy. The optimal number of units per cluster, which rests on the within-cluster variance, is too large for the classical estimator. And the spot-weighted rows that round 4 marked as nuisance rows are the same problem one level up, where the level multiplies the cluster's weight sum. The results with whole clusters labelled, donor-weighted, are not touched, because there the weights sum to zero exactly.

### 2.5 References

Mozer, arXiv:2603.19160. Särndal, Swensson and Wretman, *Model Assisted Survey Sampling*, 1992, chapter 8. Breidt and Opsomer, Statistical Science 32(2), 2017. Cochran, *Sampling Techniques*, 1977, chapters 10 and 11. Mani, Xu, Lipton and Oberst, arXiv:2505.20178. Raudenbush, Psychological Methods 1997, and Bloom, Richburg-Hayes and Black, Educational Evaluation and Policy Analysis 2007, for the trial-design formula. Angelopoulos, Duchi and Zrnic, PPI++, arXiv:2311.01453. Kluger, Lu, Zrnic, Wang and Bates, arXiv:2501.18577. Kennel and Valliant, Survey Methodology 2019. Shirota, arXiv:2608.10356. Fisch and colleagues, arXiv:2406.04291, on stratified PPI. Zrnic and Candès, "Active statistical inference", for label selection without clusters. Deville and Tillé, "Efficient balanced sampling: the cube method", Biometrika 2004. Fuller, "Some design properties of a rejective sampling procedure", Biometrika 2009. Morgan and Rubin, "Rerandomization to improve covariate balance in experiments", Annals of Statistics 2012. Li and Ding, "Rerandomization and regression adjustment", JRSS B 2020. Johnson, "Modified t tests and confidence intervals for asymmetrical populations", JASA 1978. Bell and McCaffrey 2002. Cameron and Miller 2015. MacKinnon, Nielsen and Webb 2023. The six from Zrnic and Candès to Johnson are named from the oversight chat's knowledge of the field and not from a search, so confirm that each is the right paper before you rely on it.

---

## 3. The repository, the data and the assets you build on

**Repository** at the starting commit. Everything under `results/round3/` and `results/round4/` is read-only for you, and so is every round-3 and round-4 script and document. `docs/WAYS_OF_WORKING.md` is the accumulated procedure. Read it before your first job.

**Longleaf** project tree `/work/users/w/e/weiyang/hest_replication`. It is the data root that the harness's `ROOT` points to. In round 4 it stayed on `main` at tag `round4-data-v2` (`9d7277d`) and nobody checked out a branch there. Keep it so. Never compute on the login node. The project's Python is `/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python` (Python 3.11.16, numpy 2.4.6, pandas 2.3.3, scipy 1.17.1), called by absolute path in every job script.

| asset | path | what it gives you |
|---|---|---|
| the estimator | `code/scripts/round4_ppi_estimator.py`, md5 `d79e69aa65800b9d24de556e019a0c64` | every $\lambda$ rule, the complement and textbook forms, CR1 and CR2. Import it unmodified |
| masking, regime A | `code/scripts/round4_ppi_q2_masking.py`, md5 `15f51917a5fb79702ba239e520e7ff86` | `load`, `z_arrays`, `donor_sums`, `run_cell`, and `textbook_two_stage`, the only place the linearised term is computed |
| regimes | `code/scripts/round4_ppi_q3_regimes.py`, md5 `6097231bc238c0a23387ce76029acefd` | `regime_b(z, zf, didx, valid, M, mg, sel, pop, rule, seed)`, which accepts any allocation `mg`. Its command line accepts only total budgets, spread in proportion to cluster size |
| simulations of round 4 | `round4_ppi_q1_sim.py`, `round4_ppi_q1b_sim.py`, `round4_ppi_q2_theorem_sim.py`, `round4_ppi_q3_regimeB_sim.py` | the generators. None of them runs `c_crossfit_design` or the linearised interval, and the outcome level is zero in all of them |
| unit tests | `round4_ppi_q4a_tests.py` (13 tests), `round4_ppi_q1b_tests.py` (135 tests) | your first anchor |
| the harness | `code/scripts/round3_a0_harness.py`, md5 `0ad7ae8efe554c1f285e5f384a9fb7f5` | imported unmodified by the round-4 modules |
| prediction parquets, Longleaf only | `results/round3/B1_ppi/b1_predictions__<CCRCC or CCRCC_merged>__<enc>.parquet`, `results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__<enc>.parquet`, `results/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__<enc>.parquet`, `.../predictions/ACS_STATES.parquet`, `.../predictions/ACS_CA_PUMA.parquet`, all under the project tree | per-unit outcome, prediction, cluster and covariate for every task. The md5s of the tissue files are in `results/round4/ppi/Q5_joint/cluster_unit/q5_input_md5.json` |
| the paper's tables so far | `results/round4/ppi/Q4_tables/q4_main_table.csv` (40,096 rows), `results/round4/ppi/Q4a_recompute/q4a_table61.csv` (3,840 rows) | every regime A and B row of round 4. Filter on `vtag`, not on `task`. The `role` column marks the final estimators |
| variance components | `results/round4/ppi/Q2_theory/q2_cluster_r2.csv` | unit-level, within-cluster and cluster-level $R^2$ per task, predictor, estimand and gene, on the `z` scale and on the outcome scale |
| the cluster table | `results/round4/ppi/Q5_joint/q5_cluster_table.csv` (261 rows) | one row per donor, task and encoder with its spot count and the key of its mean embedding. The mean-embedding parquets are on Longleaf under `results/round4/ppi/Q5_joint/`, with md5s in `PROVENANCE_cluster.txt` |
| the numeric-claim gate | `code/scripts/sweep_table.py`, `code/scripts/verify_numeric_claims.py` | run before every handover |

**The tasks.** Kidney cancer (`CCRCC`, 24 donors, Visium, 50 genes) and the same with donors `INT4` and `INT24` merged (`CCRCC_merged`, 23 donors), because the two may be one donor. Indiana kidney (`INDIANA_KIDNEY`, 25 donor units, Visium, 50 genes). Lung (`LUNG_XENIUM`, 15 donors, 343 genes), where disease is not fixed, so donor effects carry disease as well as person. Census income by state (`ACS_STATES`, 51 clusters) and by California PUMA (`ACS_CA_PUMA`, 265 clusters), one outcome. Three encoders on the tissue tasks, `hoptimus0`, `uni_v2` and `resnet50`. The package predictor on ACS.

**Known limitations you inherit.** Round 4's later runs were local, so the Longleaf project tree may lack some round-4 result directories. The committed copies in your clone are the record. The Longleaf code clones of round 4, under `/work/users/w/e/weiyang/hest_code/round4-ppi` and `round4-conformal`, are behind `main`. Do not use or update them. In `round4_ppi_q1_sim.py` and `round4_ppi_q2_masking.py` the seed of the cross-fit split contains the rule's name, so `c_crossfit` and `c_crossfit_design` do not share halves within a draw. Keep that behaviour wherever a round-4 row must be reproduced. `code/scripts/verify_numeric_claims.py` runs clean under the project environment's pandas. Under pandas 3 it raises a `TypeError` on cited files with empty cells. The oversight chat fixes that separately. Do not edit the checker.

---

## 4. Standing rules and conventions

- Silent failure is the main risk. Verify each stage's output against an expected value before moving on. Every rerun has one arm anchored to a prior result.
- Never assert a number you have not read back from a file. Cite the path.
- Read the whole grid before writing a headline. Before a summary sentence goes into a report, tabulate the quantity over every axis the experiment varied and check that the sentence holds in each cell it claims.
- When you explain a number, state the mechanism and name what in the files would contradict it, then check that. Round 4 explained a median of several hundred as dominated by a few draws, which a median cannot be.
- Before naming a term, list in writing every variable that differs between its arms.
- Write predictions down before running, and report them beside the outcomes.
- Do not quote a ratio whose denominator is within noise of zero.
- Longleaf is where work runs. Nothing runs on Nicolas's Mac unless he asks for that specific task in chat. Such a request is written into the plan as a numbered extension before the task runs, covers the work it names, and does not carry across a gate. A local run records the host, the library versions, the md5 of every script and input, and the command line in place of the Slurm fields.
- A job that has waited four hours is reported to Nicolas in chat with what it needs, and it keeps waiting. A pending job's time limit and memory may be reduced with `scontrol` to a sibling's measured values, and a pending job may be switched between `rc_htzhu_pi` and `rc_tengfei_pi`. It is not moved anywhere else.
- Every output directory gets `PROVENANCE.txt` (job id, partition actually used, node, date, the code clone's commit, command line, config hash with its config, `PYTHONHASHSEED`, md5 of every script that ran) and is stamped with `stamp_dir()` from the `longleaf-provenance` skill, written by the job on the node. Before reusing or rebuilding any output you did not create, run `whose()` on it. If the verdict is `sibling` or `unstamped`, ask the oversight chat.
- A job runs from its own output directory, never from inside the code clone. The clone goes on `PYTHONPATH`.
- The submission route replaces `--job-name`, so jobs are identified by Slurm id. Record the intended prefix `r5ppi_` and the stage in `PROVENANCE.txt`.
- Explicit `pa.schema` on every parquet. Summaries before bulk tables. Seeds from `zlib.crc32`, never `hash()`.
- Memory and time from a sibling's `sacct`. Slurm time limits at about three times the expected runtime, never a blanket 16 h. The harness ceiling counts queue time, so set it from queue time plus runtime. Record the partition the job ran on.
- Put a time cap on anything that is not analysis, and stop at the cap.
- Commit messages through a file. Sub-agents run no git command. The lead is the only committer and checks every hand-back against its primary tables before commit. One writer per file. Fragments plus a merge step with collision reporting.
- A file too large for GitHub is committed compressed, with the md5 of the plain file recorded. The plain file stays at the same path in the Longleaf project tree.
- Do not edit `README.md`, `docs/README.md`, `docs/WAYS_OF_WORKING.md`, any round-3 or round-4 file, or anything in the other track's areas. Proposed edits go in the report.
- Run `code/scripts/sweep_table.py` over the README and `docs/round5_ppi_*.md` before every handover.
- After opening a pull request, confirm on GitHub that it exists, and put its number in the report. In round 4 a report named a pull request that had not been created.

**Fan-out.** Every stage below names its parallel units. Dispatch one sub-agent per unit with a written brief. The brief carries the sub-agent's own frame id, written in by you, and the sentence "Stamp every output directory with `stamp_dir()` from the `longleaf-provenance` skill under the frame id given in this brief. Before reusing or rebuilding any output you did not create, run `whose()` on it; if the verdict is `sibling` or `unstamped`, ask me rather than rebuilding." Compare the id in every returned stamp with the id you assigned before the fragment is merged. Each sub-agent writes its own fragment under its own directory. The lead merges, recomputes every pooled number from the merged tables into a `<stage>_report_numbers.csv`, and commits.

---

## 5. Two sessions on one repository

The prediction-set track runs at the same time, on branch `round5-conformal`, writing under `results/round5/conformal/`, `code/scripts/round5_conf_*.py` and `docs/round5_conf_*.md`. You never write there and it never writes in your areas.

Your areas. Branch `round5-ppi`, from the starting commit, never rebased, never merged into `main` by you, and with nothing merged into it. Record the starting commit's hash in the plan. Scripts `code/scripts/round5_ppi_*.py`. Results `results/round5/ppi/<STAGE>/`. Documents `docs/round5_ppi_plan.md`, `docs/round5_ppi_theory.md`, `docs/round5_ppi_estimator_definition.md`, `docs/round5_ppi_E2_report.md`, `docs/round5_ppi_E4_report.md`, `docs/round5_ppi_final_report.md`. Longleaf outputs under `results/round5/ppi/` in the project tree, stamped. Tags `round5-ppi-E2`, `round5-ppi-E4`, `round5-ppi-final`.

**Working copies.** Each session has its own working copy, locally and on Longleaf, and never checks out a branch in a copy another session uses. Locally, reuse the round-4 clone at `~/hest-1k/HEST-1k-replication-PPI`, which Nicolas has brought up to date with `main`. It was left on branch `round4-ppi`, and that branch stays as it is. Confirm the working tree is clean, fetch, and create `round5-ppi` from `origin/main` at the starting commit. If the tree is not clean or a `.git/index.lock` is present, tell Nicolas and wait. The other two clones under `~/hest-1k` belong to the other track and to the oversight chat. Do not run git in them. On Longleaf your code runs from a fresh clone at `/work/users/w/e/weiyang/hest_code/round5-ppi/`, which is updated only by fast-forward from your pushed branch, by the route round 4 used (`results/round4/ppi/interval3_slurm_jobs.csv` records one such job). Every job records that clone's HEAD and the md5 of each script it executed.

**Pull requests.** At each gate you commit, tag and push your branch, open a pull request into `main`, and stop. You never merge. Nicolas merges with a merge commit after the oversight chat accepts the report. Branches are never rebased, squashed, amended after a push or force-pushed. A rejected gate is fixed with new commits on the same open pull request.

---

## 6. The plan

Five stages of analysis and one closing stage. Gates at E2, E4 and E5.

### E0. Setup and anchors (half a day, capped at one day)

1. Read this document, `docs/WAYS_OF_WORKING.md`, `docs/round4_ppi_estimator_definition.md`, `docs/round4_ppi_theory.md`, the closing page and section 10 of `docs/round4_ppi_final_report.md`, `docs/decisions/round4_ppi_Q5a_closing.md` and part A4 of `docs/deck2/deck2_new_results_explained.md`. Transcribe section 6 into `docs/round5_ppi_plan.md` with the predictions of section 7. List anything in this document that looks wrong in a numbered section of the plan and in the E2 report. Do not change it.
2. Create the branch in the reused local clone as section 5 says, and make the Longleaf clone. Confirm the four md5s of section 3 in the Longleaf clone. Read the project tree's HEAD with `git --no-optional-locks rev-parse HEAD` and record it. If it is not `9d7277d`, record that as an escalation and change nothing. Run `whose()` on `results/round4/`. Confirm that every prediction parquet of section 3 exists on Longleaf and that the tissue files match `q5_input_md5.json`. Record the md5s of the two ACS parquets.
3. **Anchors, all on Longleaf.** Round 4's last runs were local, so this is also the first run of the final code there.
   - `round4_ppi_q4a_tests.py` passes 13 of 13 and `round4_ppi_q1b_tests.py` passes 135 of 135.
   - `round4_ppi_q2_masking.py` on `CCRCC` with `hoptimus0`, `--nl-grid 8 --m-grid 0 --draws 200 --rules none,c_crossfit,c_crossfit_design`, reproduces the matching rows of `q4a_table61.csv`. The tolerance is 0.005 on `coverage_median`, which is one draw of 200, and $10^{-5}$ relative on the variance columns, which is above the cross-node drift recorded in `docs/WAYS_OF_WORKING.md`. Report the largest difference in each column.
   - `round4_ppi_q3_regimes.py` on `CCRCC` with `hoptimus0`, `--budgets 2400 --parts B --rules none,c_crossfit`, reproduces the matching regime B rows of `q4_main_table.csv` at the same tolerances.

Nothing in E1 starts until all three pass.

### E1. The final design-target interval in simulation (two days; no gate, reported with E2)

**Why.** The paper's design-target interval has been checked only on masking draws of the real tasks. On kidney cancer with 24 donors, Indiana and lung it covers 0.84 to 0.91. In the same cells the classical interval covers 0.85 to 0.92, and the two differ by at most 0.025 in any cell (`q4a_table61.csv`, $\theta_3$, donor-weighted, encoders, $n_L \ge 6$). So most of the shortfall looks like the classical interval's own, and a smaller part looks like the tuning. At $n_L \ge 8$ the final interval's estimated variance is 0.87 to 1.01 of the empirical variance on kidney cancer and 0.83 to 0.90 on lung, against 0.98 to 1.10 and 0.94 to 0.96 for the classical interval (`q4a_table61.csv`). E1 separates the two parts and checks the linearised term where it matters.

**The simulation runs at the level the theory lives at.** With every unit of a labelled cluster labelled, the estimator, the tuning rule and the variance depend on the data only through the $G$ pairs $(\bar z_g, \bar f_g)$. So E1 draws those pairs directly. For each cell, draw 60 finite populations of $G$ pairs

$$
\bar f_g = \kappa + p_g, \qquad \bar z_g = \lambda^\star p_g + \xi_g
$$

with $p_g$ and $\xi_g$ independent, $\text{Var}(p_g) = 1$, and $\text{Var}(\xi_g)$ set so that the squared correlation of $\bar z_g$ and $\bar f_g$ is $R^2$. At $R^2 = 0$ set $\bar z_g = \xi_g$ with unit variance. For each population draw 1,000 simple random samples of $n_L$ clusters with crc32 seeds, and compute the classical and tuned estimates and their intervals against that population's own mean of $\bar z_g$.

**The grid.** $G \in \{15, 24, 51\}$. $n_L \in \{4, 6, 8, 12, 16, 20\}$ with $n_L \le G - 3$. $R^2 \in \{0, 0.2, 0.4, 0.7, 0.9\}$. $\lambda^\star \in \{0.6, 1.2\}$, the second because the real unclipped coefficients reach 1.2 on ACS. The level $\kappa \in \{0, 2, 10\}$ in units of the between-cluster standard deviation of $\bar f_g$, because the linearised term is $(\lambda_g - c_U)\bar F$ and vanishes when the level is zero. Three laws for $p_g$ and $\xi_g$, which are normal, skewed and heavy. The skewed and heavy laws are standardised log-normals whose shape is set from the real tasks, as the next paragraph says.

**The real-task diagnostic, run first.** For each task, predictor, estimand ($\theta_3$ and $\theta_2$, donor-weighted) and gene, compute from the full data the sample skewness and excess kurtosis of the $G$ contributions $\bar z_g$, the same for $\bar z_g - \lambda \bar f_g$ at the finite-population coefficient, the finite-population $R^2$, and the level $\bar F$ over the standard deviation of $\bar f_g$. Write `e1_contribution_moments.csv`. Set the skewed law's shape so that the median absolute skewness of simulated populations of 24 equals the median over genes on `CCRCC`, and the heavy law's shape to the 90th percentile. Then rerun the masking with `--rules none --nl-grid 8 --m-grid 0` on each task, keep the per-gene coverage, and report the Spearman correlation between a gene's classical coverage and the absolute skewness of its contributions.

**Rules and intervals.** Rules `none`, `c_crossfit_design`, and an oracle arm with $\lambda$ fixed at the population's own least-squares coefficient. Intervals `textbook_t|fpc` and `textbook_t|fpc|lin`. One further interval as a diagnostic, capped at half a day, which is Johnson's skewness-adjusted $t$ applied to $e_g$. If it does not restore coverage, report that and drop it.

**Scripts.** `code/scripts/round5_ppi_estimator.py` holds what this round adds to the estimator and imports the round-4 modules unmodified. Its first function is the linearised design variance for whole labelled clusters. `code/scripts/round5_ppi_e1_sim.py` runs the grid. Build the sufficient-statistic arrays the way `synth()` in `round4_ppi_q4a_tests.py` does, so that `lambda_rule` is called unmodified. Fan out by $G$, three units, plus one unit for the diagnostic.

**Acceptance.**

1. The new variance function equals `textbook_two_stage(..., lin=True)` of `round4_ppi_q2_masking.py` on identical inputs with every unit labelled, to $10^{-12}$ relative, on one synthetic array and on one `CCRCC` masking draw.
2. Under rule `none` the two intervals are identical, because the added term is zero when every cluster has the same coefficient.
3. In the oracle arm the empirical variance over draws, divided by $(1 - n_L/G)\,S_r^2/n_L$ computed on the population, is 1 within three Monte Carlo standard errors in every cell. This checks the simulator, since that formula is exact for a fixed coefficient.
4. Under the normal law at $G = 24$, the classical interval's median coverage over cells is within 0.01 of 0.90 at every $n_L$. The round-4 design arm has medians of 0.896 to 0.900 across $n_L$ from 4 to 20 (`results/round4/ppi/Q1_estimator/q1_coverage_by_G.csv`, target `design`, form `textbook`, rule `none`, with the finite-population factor).

**Predictions.**

1. E1.1. Under the normal law the final interval covers 0.88 to 0.91 on average over populations in every cell with $n_L \ge 6$, and within 0.02 of the classical interval in the same cell.
2. E1.2. At $\kappa = 10$ and $R^2 \ge 0.4$ the interval without the linearised term has an estimated variance more than twice the empirical one in at least half the cells, and the interval with it has 0.85 to 1.10 in every cell. At $\kappa = 0$ the two intervals' coverages differ by less than 0.01 in every cell.
3. E1.3. The tuned interval's ratio of estimated to empirical variance is below the classical interval's in the same cell by 0.03 to 0.15 when $n_L/G \ge 1/3$ and $R^2 \ge 0.4$, and by less than 0.05 at $G = 51$ with $n_L \le 12$. That is, the tuning costs a little coverage, and less when the population is large against the sample.
4. E1.4. Coverage varies from one finite population to the next. Under the normal law at $G = 24$ and $n_L = 8$ the 5th to 95th percentile range of the classical interval's per-population coverage is at least 0.03 wide and lies above 0.87. Under the skewed law the classical interval covers 0.85 to 0.89 on average, so the kidney cancer shortfall is reproduced by skewness of the cluster contributions and not by the tuning.
5. E1.5. In every cell above the break-even count $n_L > 4 + 2/R^2$ the empirical variance ratio of the tuned estimator to the classical one is below 1. Below the count it is above 1 in at least half the cells.

**Outputs.** `results/round5/ppi/E1_interval/e1_sim_grid.csv` (one row per cell, rule and interval with coverage, its standard deviation and percentiles across populations, the ratio of estimated to empirical variance, the variance ratio to classical, the median clipped and unclipped coefficient and the Monte Carlo standard error), `e1_contribution_moments.csv`, `e1_real_coverage_vs_skewness.csv`, `e1_acceptance.csv`, `e1_report_numbers.csv`, `fig_e1_coverage.png`.

### E2. Regime B, completed (three days; gate)

**Why.** Regime B is the result the paper leads with. It has not been run below 6 labelled units per cluster on a tissue task, and section 2.4 says its comparator may be the wrong one.

**Derivation first.** Before any E2 job runs, write section 1 of `docs/round5_ppi_theory.md`. Derive the within-cluster variance of $z_{gi}$ for $\theta_3$ and for $\theta_2$ without the two simplifying assumptions of section 2.4, the variance that a constant predictor removes, and the share $L$ of the within-cluster variance that it removes. Check section 2.4's expression as the special case. If the derivation contradicts section 2.4, stop and report.

**Part 1, equal labelled units per cluster.** Script `code/scripts/round5_ppi_e2_regimeB.py`. It imports `regime_b` unmodified and calls it with $m_g = \min(m, M_g)$ for $m \in \{2, 3, 4, 5, 6, 8, 10, 15, 20, 25, 50, 100\}$. Tasks are all six of section 3. Arms are the three encoders, the permuted predictor, the constant predictor and the donor-constant predictor on the tissue tasks, and the package predictor with the same three controls on ACS. Rules `none` and `c_crossfit`. Both estimands, both populations, both targets. 200 draws with crc32 seeds under a new tag. Skip a control wherever it has no within-cluster variance, which is the case for both constant controls when $w = 1$. Write the unclipped half-sample coefficients beside the clipped ones, since the constant predictor's coefficient is the ratio of the outcome's level to the constant and can exceed 1. Round 4's small ACS settings spread a total budget in proportion to state size, so its "4 units per state" was a median with many states at one unit, where the variance formula has nothing to estimate from. Equal $m$ removes that.

**Part 2, the same question in simulation.** `code/scripts/round5_ppi_e2_sim.py`, built on the generator of `round4_ppi_q3_regimeB_sim.py` with an outcome level added. $G = 24$, $M = 1000$, $m \in \{2, 5, 20, 100\}$, between-cluster share 0.3, outcome level $\mu \in \{0, 1, 3, 10\}$ in units of the outcome's standard deviation, predictors with unit-level correlation $r \in \{0.5, 0.8\}$, an uninformative predictor with the same level as the outcome, and the constant predictor. Estimands $\theta_3$ and the mean. 2,000 replicates per cell.

**Part 3, the decomposition.** For every task, estimand and $m$, the width ratio against the round-4 classical estimator for the constant, donor-constant and permuted predictors and for each real predictor, and the width of each real predictor over the width of the constant and of the donor-constant predictor. Beside them, $\sqrt{1 - R^2_{\text{within}}}$ for each arm, computed on the full data.

Fan out by task, six units, plus one for the simulation.

**Acceptance.**

1. With $m_g = M_g$ regime B returns the full-data value exactly.
2. With the round-4 proportional allocation and the round-4 seed strings, the new script reproduces the E0 regime B anchor rows exactly.
3. In the simulation at $\mu = 0$, the constant predictor's variance ratio is 1.00 within 0.02 and the round-4 simulation's coverage at $m = 5$ and $m = 20$ is reproduced within 0.01 (`results/round4/ppi/Q3_regimes/sim_regimeB/regimeB_sim__G24.csv`).

**Predictions.**

1. E2.1. With equal $m$, the design-target coverage of regime B is 0.87 to 0.92 for every $m \ge 5$ on every task and arm, and 0.78 to 0.90 at $m = 2$ and $m = 3$.
2. E2.2. The constant predictor's width ratio is at or below the permuted predictor's for $\theta_3$ and $\theta_2$ on every tissue task and for $\theta_3$ on ACS, and on the tissue tasks the gap is no more than 0.06. For the mean on ACS the permuted predictor's ratio is 1.00 within 0.01.
3. E2.3. The real predictors' width over the constant predictor's width is 0.93 to 1.00 for $\theta_3$ on kidney cancer and Indiana, at least 0.97 for $\theta_2$ on both, 0.60 to 0.85 for $\theta_3$ on lung, and 0.4 to 0.8 for the package predictor's $\theta_3$ on ACS. So on the Visium tasks nearly all of regime B's gain over the round-4 classical estimator is the level term.
4. E2.4. In the simulation the constant predictor's variance ratio equals $1 - L$ from the derivation within 0.03 at $m \ge 20$, for every $\mu$.
5. E2.5. The ratio of a real predictor's width to the constant predictor's width is flat in $m$ within 0.03 for $m \ge 5$ on every task.

**Outputs.** `results/round5/ppi/E2_regimeB/e2_regimeB_grid.csv`, `e2_level_share.csv`, `e2_decomposition.csv`, `e2_sim.csv`, `e2_acceptance.csv`, `e2_report_numbers.csv`, `fig_e2_coverage_by_m.png`, `fig_e2_decomposition.png`, and section 1 of the theory document. Report E1 and E2 together as `docs/round5_ppi_E2_report.md`, tag `round5-ppi-E2`, and stop.

### E3. The regression form and the two-level estimator (four days; no gate, reported with E4)

This stage is written on the expectation that E2 confirms section 2.4. The decision memo at the E2 gate will say whether it runs as written.

**Why.** A gain from predictions is real only against a classical estimator that already uses everything known without a predictor. A cluster's slope is defined with the cluster's own intercept, and the ordinary regression slope estimates it that way. The round-4 comparator did not. And round 4 used one coefficient for both levels of a two-stage sample, which is why its allocation condition carried a penalty term (`docs/round4_ppi_theory.md` section 5.3). A coefficient for each level removes it.

**The estimator, as the oversight chat has worked it out.** Check every step in the theory document before any code. If a step does not close, stop and report. It has two stages with a coefficient for each, and the within-cluster stage has two candidate forms. E3 runs both.

*Within a labelled cluster, form C, the cluster's own intercept.* Let $L_g$ be the $m_g$ labelled units. For $\theta_3$,

$$
\hat z_g = \frac{M_g - 1}{M_g}\Big(\lambda^{w}_g\,S_{w\hat y,g} + s_{w,\,y - \lambda^{w}_g \hat y,\,g}\Big)
$$

where $S_{w\hat y,g}$ is the covariance of $w$ and $\hat y$ over all units of the cluster, with divisor $M_g - 1$, and $s_{w,\,y - \lambda \hat y,\,g}$ is the sample covariance of $w$ and $y - \lambda \hat y$ over the labelled units, with divisor $m_g - 1$. A sample covariance is design-unbiased for the cluster's covariance under simple random sampling without replacement, and $\bar z_g = \frac{M_g - 1}{M_g}\,S_{wy,g}$ because $\sum_i w_{gi} = 0$. So $\hat z_g$ is design-unbiased for $\bar z_g$ at any coefficient that does not depend on cluster $g$'s labels. For $\theta_2$, $\hat z_g$ is the difference between the two groups of the labelled units' mean of $y - \lambda^{w}_g \hat y$, plus $\lambda^{w}_g$ times the difference between the two groups of the all-unit mean of $\hat y$. At $\lambda^{w} = 0$ these are the ordinary regression slope and the ordinary difference of group means. A predictor that is constant within the cluster changes neither estimate at all.

*Within a labelled cluster, form P, one pooled intercept.* Write $a_{gi} = w_{gi}$ for the constant predictor's contribution, with cluster mean $\bar a_g$ over all units, which is zero for donor-weighted $\theta_2$ and $\theta_3$.

$$
\hat z_g = \gamma_g\,\bar a_g + \lambda^{w}_g\,\bar f_g + \frac{1}{m_g}\sum_{i \in L_g}\big(z_{gi} - \gamma_g\,a_{gi} - \lambda^{w}_g\,f_{gi}\big)
$$

This stays inside the linear machinery of round 4, is design-unbiased for any coefficients that do not depend on cluster $g$'s labels, and has the simple variance $(1 - m_g/M_g)\,s^2_{r,g}/m_g$ with $s^2_{r,g}$ the labelled units' sample variance of $z - \gamma_g a - \lambda^{w}_g f$. It removes the level common to all clusters and leaves the differences between the clusters' levels.

*Between clusters*, donor-weighted,

$$
\hat\theta = c_U\,\bar F + \frac{1}{n_L}\sum_{g \in L}\big(\hat z_g - \lambda^{c}_g\,\bar f_g\big)
$$

and the variance estimate is the two-stage one,

$$
\widehat{\text{Var}} = \Big(1 - \frac{n_L}{G}\Big)\frac{s_e^2}{n_L} + \frac{1}{G\,n_L}\sum_{g \in L}\hat V_g
$$

with $e_g = \hat z_g - \lambda^{c}_g \bar f_g + (\lambda^{c}_g - c_U)\bar F$ and $\hat V_g$ the estimated within-cluster variance of $\hat z_g$. Under form P, $\hat V_g$ is the simple variance above. Under form C it is the variance of a sample covariance, which the theory document derives by linearisation.

The within coefficients are cross-fitted over two halves of the labelled clusters, as the pooled within-cluster least-squares coefficients, with $\lambda^{w}$ clipped to $[0, 1]$ and $\gamma$ not clipped. The between coefficient $\lambda^{c}_g$ is rule `c_crossfit_design` applied to $(\hat z_g, \bar f_g)$. With every unit labelled the within stage vanishes and both forms are the round-4 final estimator. With $n_L = G$ the between stage vanishes and this is regime B with an intercept. The classical estimator of each form is the same with $\lambda^{w} = \lambda^{c} = 0$.

**What the theory document derives, as its section 2, before any E3 job.**

1. Design-unbiasedness of $\hat z_g$ in both forms and of $\hat\theta$, the two-stage variance and its estimator, and the linearised variance of form C, step by step. State the reference distribution in each corner, and the smallest $m_g$ each form needs.
2. That under form C a predictor constant within clusters changes the estimate by exactly zero, and that under form P a predictor constant over the whole task has zero partial within-cluster $R^2$ given $a$.
3. The allocation result with two coefficients. With $c_d$ per cluster and $c_s$ per unit, show that the optimal units per cluster is $m^\star_{\text{PP}} = m^\star \sqrt{(1 - R^2_{w})/(1 - R^2_{c})}$, where $R^2_w$ is the within-cluster $R^2$ and $R^2_c$ the cluster-level one, both against the classical estimator of the same form, and that $m^\star_{\text{PP}} \le m^\star$ exactly when $R^2_w \ge R^2_c$, with no penalty term.
4. The unit-weighted target. There the cluster-level auxiliary is the cluster's weight sum $A_g = \sum_i w_{gi}$, which is $M_g$ for the mean. Write the estimator with $(A_g, F_g)$ as auxiliaries and with the linearised variance for both coefficients, and the ratio form for the mean beside it as the textbook comparator.
5. The cost of tuning $p$ coefficients. The oversight chat's working is that with $p$ least-squares coefficients estimated on a half of $n_h$ clusters, Gaussian regressors and known population means, the variance ratio against the classical estimator is $(1 - R^2_p)\,(n_h - 2)/(n_h - p - 2)$, so predictions pay for their tuning when $n_L > 4 + 2p/R^2_p$. At $p = 1$ this is round 4's rule. Derive it or correct it.

**Experiments.** Script `code/scripts/round5_ppi_e3_twolevel.py` for the real data and `round5_ppi_e3_sim.py` for the simulation.

- **Simulation.** A two-level generator with an outcome level and cluster-specific levels. $G \in \{15, 24\}$, $n_L \in \{6, 8, 12, G\}$, $m \in \{3, 5, 20, 100, \text{all}\}$, $M = 1000$, between-cluster share 0.3, level $\mu \in \{0, 3, 10\}$, predictors as in E2. Both targets. 2,000 replicates per cell.
- **The regime comparison, rerun.** The round-4 budgets 2,400, 4,800 and 9,600 and cost ratios 10, 100 and 1,000 on all six tasks. Six estimators on every draw, which are the classical and the PPI estimator in the round-4 form, in form P and in form C. Arms as in E2.
- **The masking grid, rerun.** $n_L \in \{4, 6, 8, 12, 16\}$ and $m \in \{25, 50, 100, 200, 500, \text{all}\}$ with the same six estimators, and the variance components on the scale of each form, with $m^\star$ and $m^\star_{\text{PP}}$ at cost ratios 10, 100 and 1,000.
- **Regime B at small $m$, rerun.** The $m$ grid of E2 with forms P and C, to say from how many labelled units per cluster each form's interval covers.
- **The unit-weighted rows.** The spot-weighted estimands at every unit labelled, with the estimator of item 4.

Fan out by task, six units, plus one for the simulation.

**Acceptance.**

1. With $\gamma = 0$ and $\lambda^{w} = \lambda^{c}$ equal to round 4's coefficient, form P reproduces the round-4 regime A rows of `q4_main_table.csv` at $m <$ all, and with $n_L = G$ and $\gamma = 0$ the regime B rows, at the E0 tolerances.
2. With every unit labelled, donor-weighted, both forms reproduce the `final_design` rows of `q4_main_table.csv` at the E0 tolerances.
3. Under form C the constant and the donor-constant predictor leave every estimate unchanged to $10^{-10}$ on every draw. This is an identity, and it is the check that form C is coded as written.
4. Under form P the constant predictor's width ratio against the form P classical estimator is 0.97 to 1.05 at $m \ge 20$ in regime B on every task. The expected value is 1 plus a small tuning cost. The donor-constant predictor has no band under form P, since with a pooled intercept it can remove real differences between clusters' levels, and its ratio is reported as a measure of them.

**Predictions.**

1. E3.1. The permuted predictor's width ratio against the form C classical estimator is 0.97 to 1.05 in regime B at $m \ge 10$ on every task and both estimands. On the unit-weighted rows its variance ratio is 0.95 to 1.15 at $n_L \ge 8$, where round 4 had 0.09 to 0.48 on the tissue tasks (`results/round4/ppi/Q5a/q5a_spot_weighted_permuted.csv`).
2. E3.2. The real predictors' width ratio against the form C classical estimator in regime B agrees with E2's ratio to the donor-constant predictor within 0.05 on every task.
3. E3.3. The form C classical estimator is narrower than the form P classical estimator at every $m \ge 10$ on the tissue tasks, by 3 to 20%, and its interval covers 0.87 to 0.92 from $m = 5$.
4. E3.4. Regime B stays narrower than regime A in at least 200 of the 232 comparisons at a cost ratio of 10 under the two-level estimator in either form.
5. E3.5. The classical optimal units per cluster at a cost ratio of 100 falls on every task from round 4's 121 on kidney cancer, 236 on Indiana, 172 on lung and 379 on census by state (`results/round4/ppi/Q2_theory/q2_report_numbers.csv`). The fall is by about $\sqrt{1 - L}$, with $L$ the level share of E2 at the median gene, and on census by state the new value is below 100. $m^\star_{\text{PP}}/m^\star$ equals $\sqrt{(1 - R^2_w)/(1 - R^2_c)}$ within 15% on every task and predictor where both are defined.

**Outputs.** `results/round5/ppi/E3_twolevel/e3_sim.csv`, `e3_regime_comparison.csv`, `e3_masking_grid.csv`, `e3_regimeB_small_m.csv`, `e3_components.csv`, `e3_unit_weighted.csv`, `e3_superseded_round4_numbers.csv` (every round-4 number that the regression form changes, old and new side by side, with both paths), `e3_acceptance.csv`, `e3_report_numbers.csv`, figures, and section 2 of the theory document.

### E4. Which clusters to label (three days; gate)

**Why.** The break-even counts of round 4 run from 6 to 43 labelled clusters across tasks and predictors, so with 4 to 12 clusters the tuning cost eats much of the gain. If the labelled clusters are balanced on $\bar f_g$, so that their mean of $\bar f_g$ equals $\bar F$, the term $\lambda(\bar F - \bar f_L)$ is zero for every $\lambda$ and the classical mean of the labelled clusters already has the reduced variance. Nothing is tuned.

**Designs.** All are randomised, since a design-based interval needs a known random design. Nothing computed from a label enters any of them.

- D0. Simple random sampling, as round 4.
- D1. Two per stratum. Sort the clusters by the first balance variable, cut them into $n_L/2$ strata of nearly equal size, and draw two per stratum.
- D2. Rejective sampling. Draw simple random samples and keep the first whose Mahalanobis distance between the labelled mean and the population mean of the balance variables is below a threshold set so that a fraction $p_a$ of samples is accepted, $p_a \in \{0.1, 0.01\}$.

**Balance variables.** (i) The estimand's own $\bar f_g$, which is one variable per gene and is the case of a study with one outcome. (ii) The first $k \in \{1, 2, 3\}$ principal components of the $G$ by genes matrix of $\bar f_g$, which gives one design for all genes. (iii) The first $k$ principal components of the clusters' mean embeddings from the cluster table, which uses no head at all. (iv) The permuted predictor's $\bar f_g$, as the control.

**Estimators and intervals.** The classical mean and the round-4 final design estimator. For D0 and D2 the interval is `textbook_t|fpc|lin`. Fuller (2009) is the reference for using the regression estimator's ordinary variance after rejective sampling. For D1 the stratified variance with two per stratum and $n_L/2$ degrees of freedom.

**Experiments.** `code/scripts/round5_ppi_e4_sim.py` reuses E1's generator at $G \in \{15, 24, 51\}$, $n_L \in \{4, 6, 8, 12\}$, the $R^2$ grid, $\kappa = 0$ and the normal and skewed laws. `round5_ppi_e4_selection.py` runs the masking on all six tasks for $\theta_3$ and $\theta_2$, donor-weighted, every unit labelled, design target, $n_L \in \{4, 6, 8, 12\}$, 200 accepted draws, the three encoders and the permuted control. Fan out by task, six units, plus one for the simulation.

**Acceptance.**

1. D2 with the threshold at infinity is D0 and reproduces the matching rows of `q4a_table61.csv` at the E0 tolerances.
2. Balancing on the permuted predictor leaves the classical estimator's empirical variance at 0.93 to 1.07 of its value under D0, taking the median over genes. The expected value is 1, and the band is the Monte Carlo error of a variance ratio from 200 draws after the median over 50 genes.

**Predictions.**

1. E4.1. In the simulation, the classical estimator under D2 with $p_a = 0.01$ on $\bar f_g$ has a variance within 0.05 of $1 - R^2$ times its variance under D0, at every $n_L$ from 4 to 12.
2. E4.2. On the real tasks at $n_L = 8$ with balance on the estimand's own $\bar f_g$, the same ratio is 0.25 to 0.40 on lung, 0.55 to 0.70 for `uni_v2` on kidney cancer and 0.28 to 0.40 on census by state, against 0.43 to 0.54, 0.84 and 0.43 for the tuned estimator under D0 (`q4a_table61.csv`).
3. E4.3. With balance on two principal components of the predictions, the median-gene ratio recovers at least half of that gain on lung and less than a third on kidney cancer.
4. E4.4. Under D2 the classical estimator's interval from the simple-random-sampling formula over-covers, at 0.93 or above, and the final design estimator's interval covers within 0.02 of its coverage under D0. Under D1 the stratified interval covers 0.88 to 0.92.
5. E4.5. Balance on the mean embeddings leaves the ratio at 0.9 or above on the kidney tasks.

**Outputs.** `results/round5/ppi/E4_selection/e4_sim.csv`, `e4_selection_grid.csv`, `e4_acceptance.csv`, `e4_report_numbers.csv`, `fig_e4_variance_by_design.png`. Report E3 and E4 together as `docs/round5_ppi_E4_report.md`, tag `round5-ppi-E4`, and stop.

### E5. The closing report (two days; gate, end of track)

**The estimator, defined once.** `docs/round5_ppi_estimator_definition.md`, the paper's estimator as it stands after E3 and the decision memo at the E4 gate, which says which within-cluster form is the paper's, in the paper's notation, with its simulated behaviour quoted beside each choice. The round-4 definition stays as it is.

**The joint design table, rebuilt.** `results/round5/ppi/E5_joint/e5_joint_design.csv`, one row per task and $m \in \{5, 10, 15, 20, 25, 50, 100\}$ with regime B's width against the classical estimator of the chosen form and its coverage. If the prediction-set track's `results/round5/conformal/W3_real/w3_map_by_task.csv` is on `main` when E5 starts, read it there, record the commit, and add the narrowest valid prediction set at $o = m$ with its coverage and width for each number of calibration clusters that file carries. If it is not, write the inference columns only and mark the others pending.

`docs/round5_ppi_final_report.md` in the format of section 8, covering E1 to E5, the full predictions-against-outcomes table, an "Escalations" section, a section listing every round-4 statement that this round changes with the old and new values, and a closing page titled "What the round-5 inference track established", at most one page, every sentence naming its file. Run the numeric-claim sweep. Tag `round5-ppi-final`. Then stop.

**Time.** About fifteen working days with the gates.

---

## 7. Predictions for the track, consolidated

The stage predictions above, numbered E1.1 to E1.5, E2.1 to E2.5, E3.1 to E3.5 and E4.1 to E4.5, are the track's predictions. Copy them into `docs/round5_ppi_plan.md` before running and score each in the report of its gate as held, partly held, refuted or not tested. They are the oversight chat's. In round 4 most of its magnitude predictions were refuted and two were wrong in direction, so a refuted prediction is an ordinary outcome and is reported as plainly as a held one.

---

## 8. Reporting format

After each gate, in this order. 1. Stage and status. 2. What was run (scripts with md5s, commits, job ids, partitions, wall times, peak memory from `sacct`). 3. Acceptance checks with the actual numbers and file paths. 4. For every comparison, the list of variables that differ between its arms, written out. 5. Predictions against outcomes, as a table. 6. Results, numbers from files with paths, dispersion beside every mean, and paths in place of pasted tables over 20 rows. 7. Discrepancies, open questions and escalations. 8. What was not checked. 9. Proposed next step.

Keep prose plain, as section 1 asks.

---

## 9. Decision boundaries

**You decide alone.** Sub-agent structure. Seeds. Replicate and population counts above the stated ones. Job sizing. Which of two equivalent implementations to use. The exact parametrisation of the skewed and heavy laws, provided the plan records it before the run.

**Record as an escalation and continue.** The project tree not being at `9d7277d`. A prediction parquet whose md5 differs from the record (use the file, say so). Any acceptance check failing at a tolerance the dtype supports (fix, rerun, say so). The Johnson interval reaching its cap. A balance design that cannot be formed at some $n_L$ (skip that cell, say so). Any task where regime B at small $m$ leaves a cluster with no usable units. Any new property of the data. Any need to change a shared file.

**Stop and report.** Any E0 anchor failing. A derivation in E2 or E3 that does not close, including any disagreement with section 2.4 or with the working given in E3. E3's acceptance check 3 or 4 failing.

**Never yours.** Contact with anyone outside the project. Changes to `main`, to round-3 or round-4 files, to the project tree's checkout, or to the other track's areas. Any download of data. Any local run that Nicolas has not asked for in chat. Reopening what round 4 closed, which is a pre-test for $\lambda$, any bootstrap interval, tuning $\lambda$ on the clusters it is applied to, recalibration of donor offsets, and two-way clustering. Any claim of novelty.
