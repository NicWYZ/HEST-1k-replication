# Round 10, track `final-runs`, the brief

*8 November 2026. Written by the oversight chat as track `ledger`'s stage L3 output, under `../../masterplan.md`. A fresh agent checked it before the L3 gate, and its findings were worked in. Nicolas answered L3 on 8 November (`docs/round10/i02/ledger/round10_ledger_L3_answers.md`), and this brief was revised the same evening to carry his answers. The track starts only after the ledger's pull request (#38) is merged, since F1's acceptance test reads a file it brings to `main`. The brief is living on `main` while the track runs. The oversight chat revises it in place, and Nicolas tells the session to check for updates.*

## 1. Where it runs, and where the plan is

- **Session.** One Claude Science session on Longleaf, on Nicolas's seat on David's team account. The rules are `docs/EXECUTION_RULES.md` at the commit the track starts from.
- **Branch.** `round10-final-runs`, created from `main` at the commit that carries Nicolas's L3 answer.
- **Clone.** The session creates its own clone as its first step (Nicolas, 8 November), at `/work/users/w/e/weiyang/hest_code/round10-final-runs/`, cloning `NicWYZ/HEST-1k-replication` over SSH, which Nicolas's Longleaf account already has (`docs/environment.md`, clones and trees). It then creates branch `round10-final-runs` there. If the path already exists, it stops and asks Nicolas rather than reuse or remove it.
- **The plan.** `docs/round10/tracks/final-runs/round10_final_runs_plan.md` on the branch. It opens with a `state` block in the shape of `CLAUDE.md`'s, with `unit: final-runs`, recording the step in hand, what the last run produced and where, the Slurm jobs running with their IDs, the next action and anything waiting on Nicolas (`docs/EXECUTION_RULES.md`, section 1). The first session writes the plan before any job. A later session reads `docs/EXECUTION_RULES.md` and the block first, then only what the block points to.
- **A departure from `docs/EXECUTION_RULES.md`, section 5.** The session works in its own Longleaf clone, so commits are made there and pushed over SSH, with no git bundle. Every job still runs from a read-only snapshot of the committed `code/` directory in its own output directory, and each snapshot is a row of `code_deliveries.csv`. The rest of section 5 applies.
- **Housekeeping at the start** (scheduled on 7 November at Nicolas's request, `CLAUDE.md`, carried line). Delete the full texts of papers that round 9's sessions saved to the Claude Science artifact store, list what was deleted in the plan, and keep no copy.

## 2. Goal

One clean set of analyses, with the methods the ledger cites, from which the paper's numbers are quoted. The methods and their sources are `docs/round10/i01/ledger/round10_ledger.md`. The estimator and the recommendations are `docs/round10/i01/ledger/round10_ledger_decisions.md`, read together with Nicolas's L3 answer in `docs/round10/i02/ledger/`, which wins where they differ. No method outside the ledger enters the results without the literature-first step of section 7. The paper's primary estimator is the difference estimator with the coefficient fixed at 1 (R7-6, decided at L3), and the two-fold cross-fitted form of question E is reported beside it from 6 labelled clusters.

## 3. Data

- **The four tasks in hand.** CCRCC (24 donors), INDIANA_KIDNEY (25), LUNG_XENIUM (15) and ACS PUMS 2018 by state (51). The prediction files are on Longleaf under `/work/users/w/e/weiyang/hest_replication/`:
  - `results/round3/B1_ppi/b1_predictions__<TASK>__<encoder>.parquet` for CCRCC;
  - `results/round4/ppi/Q2_theory/predictions/` for LUNG_XENIUM and the two ACS tasks;
  - `results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/` for INDIANA_KIDNEY.

  Their columns are `y__<gene>`, `f__<gene>`, `donor_id`, `sample_id`, `barcode` and `m_std`, for the encoders `uni_v2`, `hoptimus0` and `resnet50`. Round 9's donor-level aggregates are under `results/round9/` on Longleaf, among them `c0_cluster_summaries.csv.gz`. CCRCC is run on the 24-donor set, with the 23-donor merged set as a sensitivity row, and the report recommends which the paper uses.
- **The corpus.** The federated project's corpus at `/work/users/w/e/weiyang/st_fed_learn/data/` is read only, with no new download (Nicolas, 7 November). Its data card is `NicWYZ/ST-Fed-Learn`, `docs/round01/tracks/data/data_card.md`. The criteria for a corpus task and the candidate tasks are in `docs/round10/i01/ledger/round10_ledger_L0_scope.md`, section 3. The session proposes the corpus tasks at F1 with their confirmed counts, and kidney Visium is one of them. Kidney Visium contains the samples of CCRCC and INDIANA_KIDNEY, so it is one multi-center task with those two as its anchors, and the session checks that its donors agree with theirs rather than counting them twice. Nicolas confirms the list at the F1 gate.
- **The two scales (D5).** Every expression inference cell on $\log(1 + y)$ of raw counts, the earlier rounds' scale, and on $\log(1 + 10^4 y/n)$ with $n$ the spot's total count. On the three HEST tasks the raw counts and library sizes are recovered as round 9 did (`code/scripts/round9_c2_normalized_summaries.py`). On the corpus the `lognorm` and `log1p` layers are used as provided. ACS has one outcome on its own scale (log personal income), so the scale comparison does not apply to it.

## 4. Stages and gates

**F1. Setup, anchors and data.** Gate F1.
1. **The estimator module.** `code/scripts/round10_final_runs_estimators.py`, with:
   - the classical estimator, the fixed-coefficient difference estimator, and the $K$-fold cross-fitted form of the decision (section 1.1 of the decisions document) with $K = 2$ as the paper's form, with the variances $\hat V_w$, $\hat V$, $\max(\hat V, \hat V_w)$ and the conservative $\frac{1}{K}\sum_k s_k^2$, and with the coefficient rule as an argument (round 5's clipped rule, the unclipped slope, or fixed);
   - round 9's fold-wise form `FOLD`, for the anchor only;
   - form C for regime B with the coefficient fixed at 1 and cross-fitted;
   - the comparators `bh`, `bh_t` and `bh_t_fpc`.

   Acceptance has two parts. The module reproduces every row of `results/round10/ledger/checks/l3_split_variance_check_output.txt` (branch `round10-ledger`, merged at L3) by exact enumeration. It also reproduces the forms `FIX1`, `W_within` and `FOLD` of `code/scripts/round9_fewcluster_williams.py` draw for draw on CCRCC at that script's seed.
2. **The anchors.** Two cells, each reproduced from the code path that made it before any new code touches it:
   - round 5: `results/round5/ppi/E4b_rejective/e4b_grid.csv`, CCRCC, `uni_v2`, $\theta_3$, $G = 24$, 8 labelled donors, design D0, rule `c_crossfit_design`, interval `textbook_t|fpc|lin|xf`, `n_sub` 2000, where the file gives `coverage_median` 0.85775 and `width_median` 0.113623;
   - round 7: `results/round7/ppi/S5_numbers/run1/s5_matched_cells.csv`, ACS_STATES, $\theta_3$, 8 labelled clusters, $p_a = 0.01$, `D2_rej_t`, where the file gives `coverage` 0.87900 and `wr_D0cl` 0.551291.

   A reproduction within Monte Carlo error passes.
3. **The inflation check.** Rerun round 9's comparison (`round9_fewcluster_williams.py`) with an `R5_lin` arm that adds round 4's `lin` term, as section 0 of `round10_ledger_L1_S4.md` describes. This settles whether the intervals reported in rounds 5 to 7 carried the level-dependent variance.
4. **The data stage.** For each proposed corpus task:
   - the sample, center and donor counts from the registry;
   - a donor-label audit of the kind of `results/round2/R5b_audit/`, recording verdicts and not inferring them;
   - the licences, noting the samples with none and those marked internal;
   - held-out prediction files from a ridge head on frozen embeddings, with the donor held out, and with the center held out for the institution axis;
   - the leave-one-donor-out $R^2$ of donor means against the leave-one-out constant (ledger, D12);
   - on kidney Visium, the atypical-donor diagnostics of `results/round9/stud/atypical_donor_diagnostics.csv`, regenerated from committed code (ledger, D13).

   Each output is stamped with provenance, and only aggregates enter the repository. INT5's raw library size and detection rate are reported here.

**F2. Inference** (topic B). Gate F2.
1. **Regime A, design target.** Whole clusters are labelled at $n_L \in \{4, 6, 8, 10, 12, 16\}$, and up to $G/2$ on corpus tasks with more donors. The design simulation draws simple random samples of labelled clusters from each task's own cluster values, at round 9's draw counts or more. It covers every estimand ($\theta_2$, $\theta_3$, and $\theta_1$ as an illustration), encoder, scale and task. The arms are:
   - the classical estimator;
   - the fixed coefficient of 1;
   - the two-fold cross-fitted form from 6 labelled clusters, with its four variances;
   - same-sample tuning by round 4's rules (a) and (b) and the cross-fitted rule (c), for the limits section;
   - the fixed-coefficient and cross-fitted forms without the finite-population factor (ledger, S6-3);
   - `bh`, `bh_t`, `bh_t_fpc` and Kluger et al.'s cluster bootstrap;
   - the pairs percentile bootstrap, the wild cluster bootstrap-$t$ with Webb's six-point weights, and a design-based bootstrap-$t$ that reproduces the finite-population factor (Rao and Wu's rescaling; ledger, S6-2);
   - the constant and permuted predictors as controls.

   Report bias, root mean squared error, coverage with its Monte Carlo standard error, median width, and the share of draws that formed no interval.
2. **The switch rule of decisions section 1.1.** In every cell with $n_L \ge 6$, report the median over genes of $E(\hat V_w)/\text{Var}(\hat\theta)$ and the fraction of draws with $\hat V < 0$. Then say which variance is primary for the cross-fitted form under the rule.
3. **The fixed coefficient's cost.** Per task and scale, the share of genes where the fixed-coefficient interval is wider than the classical one.
4. **Regime B, design target.** Form C with every cluster labelled at $m$ units per cluster, $m \ge 3$ for $\theta_3$ and $m \ge 4$ for $\theta_2$, with the coefficient fixed at 1 and cross-fitted. Use the variance and degrees of freedom of `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`, section "Regime B".
5. **The shortfall and its explanation.** Per gene, the skewness of the cluster contributions, the residual max-share $\kappa(e)$ against round 9's frontiers at that task's $G$ and $n_L$, $G^\ast = 1/\sum_g s_g^2$, and coverage against each.
6. **What predictions buy.** The width ratio against the classical estimator per gene, against cluster-level $R^2$ and spot-level Pearson (ledger, B4). Also the ratio of the donor-clustered to the i.i.d. standard error on the corpus tasks (ledger, D9).
7. **The scale difference (D5).** The difference in coverage and width between the two scales, per HEST and corpus task, with the shared factor's share on each.
8. **Superpopulation interval.** On the four tasks, as a stated limit (ledger, S6-6).

**F3. Prediction sets and designs.** Gate F3. Nicolas kept prediction sets at L3 (question P), so the prediction-set parts run and P10.3 and FR8 are scored.
1. **The prediction-set map** over calibration donors $K$ and labelled target spots $o$ on the final prediction files:
   - HCP, GHCP (the paper's rule and the released one), `within`, `within_full`, and the cross-gene studentized set;
   - INT5 reported per donor;
   - the adaptive scores (CQR, the locally weighted score, the negative binomial head) at full gene scope, compared at their own guaranteed coverage, not at matched coverage;
   - bootstrap standard errors over draws on every width margin.
2. **The institution axis.** On the corpus tasks with at least 4 centers, leave-one-center-out calibration with HCP over centers at the $\alpha$ the center count allows, and donor-level HCP pooled across centers as the comparator.
3. **Designs.**
   - Regime A against regime B, cost-matched as in round 5's E3, with the decided estimator and the fixed coefficient.
   - For question V, on every task: the required units per cluster for regime B under round 9's box class (`code/scripts/round9_fewcluster_box.py`) at each population's own observed $(\Lambda_0, v_0)$, the bounded column, and at the same $\Lambda_0$ with $v_0 = 1$, the unbounded column. Also the design simulation's coverage of the regime B interval at each of those $m$, and each task's largest share and $G^\ast$ per gene (decisions, section 4).
   - The allocation formula recomputed from the final components.
   - `rej_t` and the cube design matched against simple random selection.
   - The probe and take-all design. Its variance either uses the two-phase variance for a stratum chosen in phase one, or the report states that it conditions on the first phase.
4. **E8, the joint design** (Nicolas, 8 November, deferred to this analysis). One budget of labelled spots per donor serves both the regime B estimator and a prediction set for that donor.
   - **Literature first.** Before any analysis, search for any method that splits one labelling budget between design-based inference and prediction sets, across survey sampling, conformal prediction and PPI, with subagents, and log the queries (section 7). The starting points are round 8's note, section 3.10, round 9's direction scan, row JOINT, and the ledger's E8 row (`round10_ledger_L1_S5.md`, S5.12).
   - **The analysis.** Rerun round 4's joint table (`code/scripts/round4_ppi_q5_joint.py`) on the final prediction files. That means the regime B width ratio at $m$ labelled spots per donor beside GHCP and `within_full` at $o = m$, for every $K$ the task allows at $lpha = 0.1$, with the cheapest-valid-set rule, on the four tasks and kidney Visium.
   - **The report.** What the joint design buys over labelling for each purpose separately, with Monte Carlo standard errors, so that Nicolas can decide E8 at F3.
5. **V, decided by Nicolas after this stage** (8 November, "further analysis first, then decide based on empirical evidence"). The report sets the two columns of item 3 side by side with each task's largest share and $G^\ast$, and makes no recommendation of its own beyond what the evidence shows.

**F4. Final report and pull request.** Gate F4.
- The report follows `docs/EXECUTION_RULES.md`, section 7, and scores every prediction of section 5.
- It includes a table that maps each number the paper will quote to its file.
- It goes to `docs/round10/i05/final-runs/round10_final_runs_report.md`.
- One pull request into `main`, which Nicolas merges.

The intermediate reports go to `docs/round10/i02/final-runs/` (F1), `i03` (F2) and `i04` (F3). Nicolas's replies go into the next interval's decision file.

**Decision boundaries and stop conditions.**
- If an anchor of F1.2 does not reproduce, or the module fails its acceptance in F1.1, the session reports at F1 with the discrepancy. It builds no arm of F2 or F3 on it.
- If a corpus task fails the donor criterion of the L0 scope once audited, it is dropped and the report says so.
- Every other problem is handled under section 7 and recorded under "Escalations" in the next report, and work continues (`docs/EXECUTION_RULES.md`, section 2).

## 5. Predictions, written before any run

Scored at the gate named, as held, partly held, refuted or not tested. P10.1 and P10.3 are the masterplan's and are restated here. Unless a prediction says otherwise, "the HEST tasks" are CCRCC, INDIANA_KIDNEY and LUNG_XENIUM, the estimand is $\theta_3$ (donor-weighted), the encoder is `uni_v2`, ACS by state is one population (state means of log income, as round 9 ran it), and the nominal level is 0.90.

- **P10.1** (F2 and F3). On CCRCC, INDIANA_KIDNEY and LUNG_XENIUM at 8 labelled donors, the median over genes of the tuned interval's coverage under the level-free variance is 0.02 to 0.05 below the value rounds 5 to 7 reported for the same cell. The ordering of designs by median width on round 7's matched supported cells at 8 labelled clusters is unchanged. Before F2, the plan names the round 5 to 7 file, row and interval label that each comparison uses.
- **P10.3** (F3). At 10 calibration donors and the nominal level of round 5's map, the target donor's own full conformal set becomes narrower in median width than HCP from 9 labelled spots on CCRCC and LUNG_XENIUM. On INDIANA_KIDNEY its median width stays within 2% of the plain within-donor split's at 9 to 15 labelled spots.
- **FR1** (F1). With round 4's `lin` term, round 5's estimator's interval has a median width within 1.15 times that of Williams' form with the within-half variance at 8 labelled clusters, on every HEST task and on ACS by state. Round 9's `R5` arm, without the term, gave 9.3 to 20.3 on ACS (`docs/round09/i03/fewcluster/round09_fewcluster_williams.md`, section 2, item 3).
- **FR2** (F2). The median over genes of $E(\hat V_w)/\text{Var}(\hat\theta)$ is at least 0.95 in every cell of the switch rule, so $\hat V_w$ stays primary. $\hat V$ is negative in at least 0.05 of draws at 6 labelled clusters on CCRCC and INDIANA_KIDNEY.
- **FR3** (F2). At 4 labelled clusters, the fixed coefficient's median root mean squared error is below the classical estimator's on every HEST task on $\log(1 + y)$ and on ACS by state, as in round 9.
- **FR4** (F2). At 8 labelled donors at least 0.3 of genes have a wider fixed-coefficient interval than the classical one on CCRCC and on INDIANA_KIDNEY, and at most 0.2 on LUNG_XENIUM. On ACS by state, the one population's fixed-coefficient interval is narrower than the classical one.
- **FR5** (F2). On CCRCC at 8 labelled donors, the fixed-coefficient interval's median coverage is at least 0.02 higher on $\log(1 + 10^4 y/n)$ than on $\log(1 + y)$.
- **FR6** (F2). On the corpus kidney Visium task, the median gene's residual max-share at 16 labelled donors lies beyond round 9's Theorem 1 frontier at that $G$. There, the fixed-coefficient interval's median coverage at 16 labelled donors is below 0.88.
- **FR7** (F3). In regime B with the coefficient fixed at 1, median coverage is within 0.03 of nominal at every $m \ge 6$ on every HEST task and on ACS by state. The unbounded column needs more units per cluster than the bounded column on every task.
- **FR8** (F3). On kidney Visium at $\alpha = 0.2$, donor-level HCP pooled across centers covers the held-out center's spots below 0.75 at the median gene. HCP over centers covers at least 0.8 there.

## 6. Standards

These are the standards of `docs/EXECUTION_RULES.md` (evidence, provenance, reports), with four points specific to this track.
1. Every number the paper may quote is produced by committed code from committed or stamped inputs, with its Monte Carlo standard error.
2. Tables cover every axis the stage varied before any headline is written.
3. Run `code/scripts/verify_numeric_claims.py` over every report. Branch `round10-ledger` carries its R7.6 fix for comma-grouped integers.
4. Gated data, papers and transcripts never enter the repository.

## 7. When the work meets a problem the ledger does not cover

Search the literature first, with subagents, across survey sampling, econometrics and machine learning, and record the queries. Report the search at the next gate with what it found. A derivation starts only after Nicolas has seen the search and agreed the gap is genuine (masterplan, track `final-runs`; `CLAUDE.md`, "Literature first"). Papers the session cannot retrieve go to Nicolas as one list of at most 10 with UNC proxy links.

## 8. Where it writes

- `docs/round10/tracks/final-runs/` (the plan) and `docs/round10/iKK/final-runs/` (gate reports and decision files).
- `results/round10/final_runs/` (aggregates, job ledger, `code_deliveries.csv`, `provenance_index.csv`).
- `code/scripts/round10_final_runs_*`.
- Bulk outputs on Longleaf under `/work/users/w/e/weiyang/hest_replication/results/round10/final_runs/`, an output directory and not a change to the project tree's checkout, as in round 9.

## 9. Not this track's decision

- Which scale the paper calls primary (D5), after F2.
- V and E8, which Nicolas decides after F3; Q1 and Q3. P, R7-6, R7-7, R7-5 and O5 were decided at L3 and are not reopened by the session.
- Which of round 9's theorems the paper keeps.
- Any claim of novelty.
- Any contact outside the project.
- Any download of data or code.
- Adding corpus tasks Nicolas has not confirmed at F1.
- Changes to `main`, to earlier rounds' files or to the project tree's checkout.
