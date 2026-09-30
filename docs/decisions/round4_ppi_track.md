# Round 4, the PPI track: inference and design with the donor as the unit

30 September 2026, revised after the data-pull report. Prepared by the oversight chat for a fresh Claude Science session. This document is self-contained. The track starts from tag `round4-data-v2` on `NicWYZ/HEST-1k-replication`, on its own branch `round4-ppi`, and runs concurrently with a second session on branch `round4-conformal`, which has its own document. Section 5 says how the two coexist. The P8 addendum that produced it is reported in `docs/round4_data_P8_report.md`. Read this document fully, then transcribe section 6 into `docs/round4_ppi_plan.md` before running anything.

---

## 1. Your role and the people

You are the execution agent. A separate chat session, the oversight chat, reviews your reports, makes scope decisions and writes decision memos, which Nicolas hands to you in full. Nicolas Weiyang Zhang (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`) is the first-year biostatistics PhD student whose project this is. He reads every command before it runs and will ask why. His advisors are Dr. Hongtu Zhu and Dr. Daiwei (David) Zhang at UNC. The target is a submittable paper by spring 2027, and this track produces that paper's methodological core.

Your responsibilities are to run the planned analyses on UNC Longleaf through Slurm, verify every stage's output against an expected value before moving on, write stage reports in the format of section 8, commit and push on your branch, and stop at each gate. You do not make scope decisions. Anything this document does not cover is reported as a proposal, not done.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. This track's gates are Q1, Q3 and Q5. Contact with anyone outside the project is never the session's decision.

**How Nicolas wants things written.** Plain, natural prose. No em-dashes. No colon-then-explanation constructions. Math as LaTeX. Numbers quoted at the precision the comparison needs, with the relative scale stated; full precision stays in the files. Every number in a report is read back from the file named beside it. When a derivation is asked for, write it out step by step; he will read it. Do not inflate length.

---

## 2. The project, and what this track is for

### 2.1 In one page

Spatial transcriptomics measures gene expression at known spots on a tissue section. A frozen pathology foundation model maps each spot's H&E patch to an embedding $z_i$, and a linear head (standardise, PCA to 256, ridge with an intercept in float64) predicts $y_{ig} = \log(1 + \text{count}_{ig})$ per gene. Per-gene Pearson is about 0.3 to 0.4. The data are nested, spots inside slides inside donors, and everything below turns on that.

Rounds 1 to 3 replicated the HEST-1k benchmark exactly, instrumented it so every prediction sits in a table with its spot, slide and donor, and measured the premises of two topics. The results that this track builds on, with their files:

1. **The donor is the unit of every uncertainty statement.** On CCRCC (24 donors, Visium, ccRCC tumour), a donor-clustered standard error for the slope of expression on nuclear area is 29 to 68 times the spot i.i.d. one. Over 200 random choices of labelled donors, a spot i.i.d. 90% interval covers the full-data value 4% of the time; a donor cluster-robust interval with the $G/(G-1)$ correction and a $t_{G-1}$ reference covers 91%; a percentile donor bootstrap covers 71% (`results/round3/B2_semisynthetic/b2_coverage.csv`, `results/round3/B1_ppi/b1b2_report_numbers.csv`).
2. **Prediction-powered inference under donor clustering works and gains modestly.** PPI++ intervals are 0.85 to 0.89 as wide as classical for the three encoders in the donor-weighted population and 0.98 for a permuted predictor; the power-tuning weight $\lambda$ falls from about 0.7 at six labelled donors to about 0.2 at eight or more; better-predicted genes gain more (Spearman $-0.6$ to $-0.7$ between a gene's Pearson and its width ratio) (`results/round3/B2_semisynthetic/b2_width_ratio.csv`, `results/round3/B1_ppi/b1_estimates.csv`).
3. **The between-donor share of expression variance is about 0.3 to 0.4** on the tasks that can measure it (`results/round2/R6_variance/`), and the effective sample size of $n$ donors with $m$ spots each is $nm / (1 + (m-1)\rho)$, about $n/\rho$ for large $m$.
4. **The same integer limits prediction intervals.** A distribution-free interval for a new donor needs $K + 1 \ge 1/\alpha$ calibration donors, and hierarchical conformal prediction at $K = 10$ is finite and covers 0.969 at 1.95 times the pooled width (`results/round3/A4_scores/a4b_summary.csv`). The conformal track works on that; you cite it.
5. **The labels are audited.** Every donor and source label used in round 4 comes from `results/round4/data/P4_audit/donor_audit_r4.csv`. IDC's four benchmark samples are four donors (round 2's merge was wrong). CCRCC's 24 donor labels are `unverifiable` at donor level and `INT4` and `INT24` may be one donor, so every CCRCC analysis runs with 24 donors and with the two merged, both reported.

The full account is in `docs/round3_final_report.md` (read its closing page, "What round 3 established") and the round-3 B1 sections (`docs/round3_final_report.md` section 6.4). The estimator you start from is `code/scripts/round3_b1_ppi.py`; the semi-synthetic harness is `code/scripts/round3_b2_semisynthetic.py`.

### 2.2 The paper this track serves, and what is and is not new

Working title, "Labelling budgets for prediction-powered inference with clustered data". Methodology first, two application domains, spatial transcriptomics as the main case study.

Be clear about originality from the first line of every document you write, because the oversight chat checked the literature on 28 September and the position is this. Prediction-powered inference is the survey-sampling difference estimator (Mozer, arXiv:2603.19160, March 2026), and its PPI++ form is the generalised regression estimator; model-assisted estimation under two-stage and cluster sampling with cluster-level variance is textbook (Särndal, Swensson and Wretman 1992, chapter 8; Breidt and Opsomer, Statistical Science 2017). So the estimator this track builds is not new, and the paper says so. What is new, and general, is what the estimator does when the predictor's error has a cluster-level component and the labelling budget is spent on clusters and units. Nobody has written down, for PPI under cluster sampling, the gain bound (section Q2), the allocation of a budget between clusters and units with a predictor, the comparison of labelling few clusters fully against a few units in every cluster, or the behaviour with few labelled clusters. Every user of PPI with clustered data needs those, in any field.

The paper's claims. A spot-level (unit-level) uncertainty statement about predicted outcomes is off by an order of magnitude when units are nested in clusters. Valid inference clusters by the cluster. The gain from predictions under cluster sampling is governed by the predictor's cluster-level accuracy, not its unit-level accuracy. A labelling budget should be spent on clusters before units, and a better predictor moves the optimum further toward clusters. And the same few labelled units per cluster serve both population inference and prediction sets for units in new clusters, which is the conformal track's part.

Applications. ACS PUMS income (the dataset in the PPI package and in the generalised hierarchical conformal paper, so every number is comparable to two literatures) with states or PUMAs as clusters, and HEST-1k on three tasks with audited donors, where the cluster-level error is large and measured. The round-3 coverage results are the motivation section, not the contribution.

### 2.3 The methods, stated once

**PPI++ for an estimand defined by an estimating equation** $\mathbb{E}[\psi(y, m; \theta)] = 0$, with a labelled set $L$ of $n$ spots on $G_L$ donors and an unlabelled set $U$ of $N$ spots on $G_U$ donors. The estimator solves

$$\frac{\lambda}{N}\sum_{i \in U}\psi(\hat y_i, m_i; \theta) + \frac{1}{n}\sum_{i \in L}\big[\psi(y_i, m_i; \theta) - \lambda\,\psi(\hat y_i, m_i; \theta)\big] = 0.$$

It is unbiased for any predictor and any $\lambda \in [0, 1]$; $\lambda = 0$ is the classical estimator. For the estimands here $\psi$ is linear in the outcome, so the solution is explicit.

**The influence function.** With $A = \mathbb{E}[\partial\psi/\partial\theta]$, the estimator's error is an average of per-spot contributions, $\hat\theta - \theta \approx \frac{1}{N}\sum_U \phi_i^U + \frac{1}{n}\sum_L \phi_i^L$, with $\phi_i^U = -A^{-1}\lambda\psi(\hat y_i, m_i;\theta)$ and $\phi_i^L = -A^{-1}[\psi(y_i, m_i;\theta) - \lambda\psi(\hat y_i, m_i;\theta)]$.

**The cluster-robust variance.** Sum the contributions within each donor, $S_g = \sum_{i \in g}\phi_i$, then

$$\widehat{\text{Var}} = \frac{G_U}{G_U - 1}\cdot\frac{1}{N^2}\sum_{g \in U}\hat S_g^2 + \frac{G_L}{G_L - 1}\cdot\frac{1}{n^2}\sum_{g \in L}\hat S_g^2,$$

with a $t$ reference on few donors. Different donors are assumed independent; nothing is assumed inside a donor. This is Liang and Zeger's sandwich on the PPI influence function, with the small-$G$ practice of Cameron and Miller (2015) and MacKinnon, Nielsen and Webb (2023).

**Two population definitions**, both always reported. Spot-weighted, the estimand over all spots pooled. Donor-weighted, the estimand computed within each donor and averaged over donors with equal weight, which is the one whose target population is patients and whose unit is the donor.

**Semi-synthetic validation.** The full dataset defines the truth $\theta_{\text{full}}$. A partition draws labelled donors (or labelled spots), intervals are computed, and whether each covers $\theta_{\text{full}}$ is recorded over 200 crc32-seeded draws. This is design-based coverage of this dataset's value.

**Estimands.** $\theta_3$, the slope of $\log(1+y_g)$ on standardised mean nuclear area, primary. $\theta_2$, the difference in mean expression between neoplastic-dominant and stromal-dominant spots. $\theta_1$, the correlation of mean nuclear area with raw GATA3 count on IDC, the illustration only. Morphology covariates come from `instrumentation/morphology_v2/` (benchmark) and `instrumentation/morphology_ext/` (expansion, built in the data pull).

**References** to cite. Mozer, "PPI is the Difference Estimator", arXiv:2603.19160; Särndal, Swensson and Wretman, *Model Assisted Survey Sampling*, 1992; Breidt and Opsomer, Statistical Science 32(2), 2017; Chen, Guo and Li, "Power Analysis for Prediction-Powered Inference", arXiv:2603.16041; "Stratified Sampling for Model-Assisted Estimation with Surrogate Outcomes", arXiv:2602.12992; Innocenti et al., Statistics in Medicine 2019 and 2021 (optimal two-stage allocation without predictions); Mallick, Tchetgen Tchetgen, Dobriban and Lee, "Generalized Hierarchical Conformal Prediction", arXiv:2608.15500 (the conformal track's reference method, cited here for the joint design). And, already in the round-3 documents, Angelopoulos, Bates, Fannjiang, Jordan and Zrnic, Science 2023; Angelopoulos, Duchi and Zrnic, PPI++, arXiv:2311.01453; Zrnic and Candès, PNAS 2024; Fisch et al., arXiv:2406.04291 (stratified PPI; the donor is a cluster, not a stratum, which B1 established); Salerno, Wu and McCormick, arXiv:2603.11368 and Shirota, arXiv:2608.10356 (PPI with spatial dependence; neither treats nested units); Cameron and Miller 2015; MacKinnon, Nielsen and Webb 2023; Bell and McCaffrey 2002 for the CR2 correction; Cochran's *Sampling Techniques* chapter on two-stage sampling for the allocation result.

---

## 3. The repository, the data and the assets you build on

**Repository** at tag `round4-data-v2`. `results/round3/` and `results/round4/data/` are read-only for you. `docs/WAYS_OF_WORKING.md` is the accumulated procedure; read it before your first job. `docs/round4_data_report.md` and `docs/decisions/round4_data_P7_decisions.md` say what the data pull delivered and what the oversight chat decided about it.

**Longleaf** project tree `/work/users/w/e/weiyang/hest_replication`. Never compute on the login node.

| asset | path | what it gives you |
|---|---|---|
| audited labels | `results/round3/D3_audit/donor_audit_r3.csv`, `results/round4/data/P4_audit/donor_audit_r4.csv` | `donor_id`, `donor_label_status`, source and instrument fields; the only grouping source |
| task definitions | `results/round3/task_defs/`, `results/round3/D4_expansion/task_defs/`, `results/round4/data/P5_task/LUNG_XENIUM.json` | CCRCC, the other benchmark tasks, Indiana kidney (25 donor units), lung Xenium (20 samples and 15 donors after the P8 addendum; read the counts and the `dropped_patch_barcodes` list from the file), in the A0 format with fold assignments |
| the harness | `code/scripts/round3_a0_harness.py`, md5 `0ad7ae8efe554c1f285e5f384a9fb7f5` | fold construction, size matching, the float64 head, the calibration-fraction-zero mode that gives every spot a prediction from a head that never saw its donor; import it unmodified |
| B1 and B2 | `code/scripts/round3_b1_ppi.py`, `round3_b2_semisynthetic.py` | the estimator, its acceptance identities, the masking harness; your starting point, extended into a `round4_ppi_` module |
| benchmark embeddings | `embeddings/<task>/<encoder>/<sample>.h5` | 12 encoders; this track uses `hoptimus0`, `uni_v2`, `resnet50` and a permuted predictor |
| expansion embeddings | `embeddings_ext/<set>/<encoder>/<sample>.h5` | kidney (Indiana and Cordeliers), breast Xenium, lung Xenium; three encoders; rows are patches, in patch order, with readable barcodes |
| morphology | `instrumentation/morphology_v2/`, `instrumentation/morphology_ext/{indiana_kidney, breast_xenium, lung_xenium}/morphology.parquet` | per-spot nuclear count, mean and median area, five class fractions; pooled join rates 0.999 on Indiana, 0.970 on breast (`TENX197` at 0.862) and 0.984 on lung |
| gene lists | `results/round4/data/P6_genes/genes__<TASK>__<k>.csv` | per-fold training-only top 50, 200 and 500 for every Visium task; one Indiana fold is short at 200 and 500 and is used as it is; the Xenium panels in `p6_xenium_panels.csv` and, after P8, `results/round4/data/P8_addendum/xenium_panels_genes_only.csv` |
| variance components | `results/round2/R6_variance/r6_variance_by_task.csv` | the between-donor share per task and gene |
| the numeric-claim gate | `code/scripts/sweep_table.py` | run before every handover |

**Known limitations you inherit.** CCRCC's donor labels are unverifiable at donor level (run 24 and merged). The 50-gene lists of the benchmark tasks were chosen with test spots; the gene-axis results in Q4 use the training-only lists. 4.6% of benchmark spots lack a morphology row and are excluded from morphology estimands, per task and recorded. PRAD has two donors and is the failure case, kept as such. B1's $\lambda$ was tuned on the spot-level variance because tuning on the clustered one at $G_L = 2$ drives it to zero; Q1 replaces that choice. Round 3's D4 probe box was twice too wide, so its statement that morphology removes 31% to 34% of the probe signal is quarantined; do not cite it.

**The lung task, as delivered.** Twenty TGen fibrosis TMA cores (sixteen of 3 mm, four of 5 mm) from fifteen donors, one laboratory, one instrument (`XETG00048`), one software generation, one pixel size, 343 target genes after the 198 controls are removed. Disease is not fixed (IPF, control lung, sarcoidosis and four other diagnoses), so donor effects there carry disease as well as person; say so wherever lung is compared with the kidney tasks. Every capture slide carries two to five donors, so there is no slide-out design, and the slide id is recorded per sample. Five donors have two samples, ten have one. Each donor fold leaves 14 donors, so the $K = 10$ design trains on 4 donors; record the training-donor count beside every lung number. `NCBI865` is a member with one patch barcode (`051x019`) dropped, listed under `dropped_patch_barcodes` in the file; its embedding file still has 2,143 rows. Apply the drop list before any subset assertion. Round 3's `round3_d4_sets.load_set` asserts the relation on the embedding file's barcodes and will raise on `NCBI865` if called directly, so read lung through a wrapper in your own module that removes dropped barcodes first and then asserts; do not edit the round-3 loader. Exercise the wrapper on `NCBI865` in setup and record 2,142 rows. Core size also varies. Sixteen samples are 3 mm cores and four (`NCBI864`, `NCBI865`, `NCBI867`, `NCBI884`) are 5 mm cores from a different TMA, recorded per sample under `expansion.core_diameter_mm_source`; it is on the lung difference list beside disease, and a 5 mm core contributes more spots per donor.

**Xenium control features.** Any Xenium panel or target list you read has `NegControl*`, `UnassignedCodeword*` and `BLANK*` features removed first, and the count removed is recorded. Round 3's `BREAST_XENIUM.json` carries 61 such features in its target list; the lung file carries none.

---

## 4. Standing rules and conventions

- Silent failure is the main risk. Verify each stage's output against an expected value before moving on. Every refit has one arm anchored to a prior result.
- Never assert a number you have not read back from a file. Cite the path.
- Before naming a term, list in writing every variable that differs between its arms.
- Write predictions down before running, and report them beside the outcomes.
- Do not quote a ratio whose denominator is within noise of zero.
- Every output directory gets `PROVENANCE.txt` (job id, partition actually used, node, date, commit, command line, config hash with its config, `PYTHONHASHSEED`, md5 of the script that ran) and is stamped with `stamp_dir()` from the `longleaf-provenance` skill, written by the job on the node. A sub-agent stamps from its own process, so the frame id recorded is its own and not the lead's. Before reusing or rebuilding any output you did not create, run `whose()` on it; if the verdict is `sibling` or `unstamped`, ask the oversight chat rather than rebuilding.
- The submission route replaces `--job-name`, so jobs are identified by Slurm id. Record the intended prefix `r4ppi_` and the stage in `PROVENANCE.txt` instead.
- Explicit `pa.schema` on every parquet; summaries before bulk tables; seeds from `zlib.crc32`, never `hash()`.
- Memory from `sacct` (16 GB on 4 CPUs is the honest ask for head fitting; B1 and B2 peaked at 11.2 GB). Slurm time limits at about three times the expected runtime from a sibling job, never a blanket 16 h. Harness ceiling from queue time plus runtime. Record the partition the job ran on. Set the working directory explicitly in every job script.
- Put a time cap on anything that is not analysis, and stop at the cap. Checker or tooling work is capped at half a day per interval.
- Commit messages through a file. Sub-agents run no git command; the lead is the only committer and checks every sub-agent hand-back against its primary tables before commit. One writer per file; fragments plus a merge step with collision reporting.
- Do not edit `README.md`, `docs/WAYS_OF_WORKING.md`, `docs/README.md`, any round-3 file, or anything under `results/round4/data/` or the conformal track's areas. Proposed edits go in the report.
- Run `code/scripts/sweep_table.py` over the README and `docs/round4_ppi_*.md` before every handover.

**Fan-out.** Every stage below names its parallel units. Dispatch one sub-agent per unit with a written brief that includes, verbatim, "Stamp every output directory with `stamp_dir()` from the `longleaf-provenance` skill. Before reusing or rebuilding any output you did not create, run `whose()` on it; if the verdict is `sibling` or `unstamped`, ask me rather than rebuilding." Each sub-agent writes its own fragment under its own directory; the lead merges, recomputes every pooled number from the merged tables into a `<stage>_report_numbers.csv`, and commits.

---

## 5. Two sessions on one repository

The conformal track runs at the same time, on branch `round4-conformal`, writing under `results/round4/conformal/`, `code/scripts/round4_conf_*.py`, `docs/round4_conf_*.md` and, on Longleaf, `results/round4/conformal/`. You never write there and it never writes in your areas.

Your areas. Branch `round4-ppi`, from tag `round4-data-v2`, never rebased onto anything else and never merged into `main` by you. Scripts `code/scripts/round4_ppi_*.py`. Results `results/round4/ppi/<STAGE>/`. Documents `docs/round4_ppi_plan.md`, `docs/round4_ppi_theory.md`, `docs/round4_ppi_estimator_definition.md`, `docs/round4_ppi_Q1_report.md`, `docs/round4_ppi_Q3_report.md`, `docs/round4_ppi_final_report.md`. Longleaf scratch `results/round4/ppi/` under the project tree, stamped. Tags `round4-ppi-Q1`, `round4-ppi-Q3`, `round4-ppi-final`.

Shared and read-only for both are everything under `results/round3/` and `results/round4/data/`, the embeddings, the morphology parquets, the harness. If you find you need to change a shared file, that is an escalation, not an edit.

The one file both tracks will want to write is the audit file. Neither does. Any label change is proposed in a report with its source, and the oversight chat applies it between intervals.

---

## 6. The plan

Four stages of analysis and one closing stage. Gates at Q1, Q3 and Q5.

### Q0. Setup (half a day, capped at one day)

1. Read this document, `docs/WAYS_OF_WORKING.md`, `docs/round3_final_report.md` sections 6.4 and the closing page, `docs/round4_data_report.md` and `docs/decisions/round4_data_P7_decisions.md`. Transcribe section 6 into `docs/round4_ppi_plan.md`. Flag anything that looks wrong in the Q1 report rather than changing it.
2. Create the branch and directories. Run `whose()` on `results/round4/data/` and record the verdict. Read the lung task file and record its sample count, donor count and dropped barcodes in the plan; the counts in this document are what the file is expected to say, and the file wins.
3. **The general dataset.** Fetch the ACS PUMS income data as packaged by `ppi_py` (its `census` dataset, the one the PPI Science paper and the generalised hierarchical conformal paper use), with the state and PUMA identifiers, into `results/round4/ppi/Q0_setup/acs/` with a `PROVENANCE.txt` naming the source URL, version and hashes. If Longleaf's network refuses the download, record the refusal and continue; the oversight chat will have Nicolas supply the file, and the ACS units of Q2 and Q4 wait for it while everything else proceeds. Write `results/round4/ppi/Q0_setup/acs_task_def.json` in the A0 format with the cluster variable (state, and PUMA as a second level), the outcome (log income), the covariate for $\theta_3$ (age, standardised), and the predictor (the package's gradient-boosted predictions; if absent, fit one on a held-out split of the labelled data and record it).
4. **Anchor.** Rerun `round3_b1_ppi.py`'s four acceptance identities on CCRCC with one encoder (with $U$ empty PPI equals classical; with $\hat y = y$ PPI equals the full-data value; with one spot per donor the cluster variance equals the i.i.d. one; the permuted predictor's donor-weighted $\lambda$ is 0) and reproduce `results/round3/B1_ppi/b1_acceptance.csv` to $10^{-10}$. Nothing in Q1 starts until this passes.

### Q1. The estimator, made right (three days; gate)

**Why.** Round 3's estimator has five soft spots that a paper cannot carry. $\lambda$ is tuned on the spot-level variance. The two clustered terms have no combined degrees of freedom. The percentile bootstrap fails at small $G$. The CR1 correction is known to under-cover with few and unequal clusters. And B2's target is the full-data value of a fixed set of 24 donors, yet its variance carries no finite-population correction, so drawing 12 of 24 donors is treated as drawing 12 from infinitely many; that alone would predict over-coverage at $n_L = 12$, which B2 saw (0.94 to 0.95). Q1 settles one estimator, with a stated finite-sample behaviour and a stated target, that every later stage uses.

**Two targets, named on every row.** The design-based target is $\theta_{\text{full}}$, the value on the fixed set of $G$ donors in hand, and its variance carries the finite-population correction $(1 - n_L/G)$ on the between-donor term. The superpopulation target is the value in the population the donors were drawn from, whose variance has no such correction and can only be checked in simulation, where fresh donors can be drawn. Real-data coverage is always of the design-based target. Every table in this track carries a `target` column.

**Script.** `round4_ppi_estimator.py`, a module with one entry point per component, imported by every later stage, plus `round4_ppi_q1_sim.py` for the simulation.

**Components to compare.**

- $\lambda$. (a) B1's, tuned on the spot i.i.d. variance. (b) Tuned on the clustered variance, restricted to $[0, 1]$, and fixed at 0 when $G_L < 4$. (c) Cross-fitted, estimated on half the labelled donors and applied to the other half, then swapped and averaged, which removes the optimism of tuning and evaluating on the same donors. Report all three; (c) is the expected choice.
- Variance and reference. (a) CR1 with $t_{G_L - 1}$, as B1. (b) CR2 (Bell and McCaffrey's leverage adjustment) with its Satterthwaite degrees of freedom. (c) Either, with a Welch-Satterthwaite combination of the $U$ and $L$ terms' degrees of freedom, since the two terms have different cluster counts.
- Bootstraps. (a) Percentile donor bootstrap, as B1. (b) Studentised (bootstrap-$t$) donor bootstrap. (c) BCa. 500 draws each.
- Finite-population correction. (a) None, as B1. (b) $(1 - n_L/G)$ on the labelled between-donor term when the target is design-based. Reported for both targets so the simulation shows which target each variance is right for.

**The simulation.** Donors $g = 1, \dots, G$ with $m$ spots. Covariate $m_{gi} = c_g + d_{gi}$ with a donor mean $c_g$ and spot deviation, standardised overall. Outcome $y_{gi} = \mu + u_g + \beta m_{gi} + e_{gi}$ with $u_g \sim N(0, \sigma_u^2)$, $e_{gi} \sim N(0, \sigma_e^2)$ and between-donor share $\rho = \sigma_u^2/(\sigma_u^2 + \sigma_e^2)$. Predictor $\hat y_{gi} = y_{gi} - a_g - \epsilon_{gi}$ with a donor-level error $a_g \sim N(0, \sigma_a^2)$ and a spot-level error $\epsilon_{gi}$, scaled so that the spot-level correlation between $y$ and $\hat y$ is $r$. Grid: $G_L \in \{4, 6, 8, 12, 20\}$, $G_U \in \{10, 20, 50\}$, $m \in \{200, 1000, 5000\}$, $\rho \in \{0.1, 0.3, 0.5\}$, $r \in \{0, 0.3, 0.5, 0.8\}$, with $\sigma_a^2$ set so the predictor's donor-level error is half of $\sigma_u^2$. Estimands $\theta_3$ (slope) and the mean, spot-weighted and donor-weighted. 2,000 replicates per cell. Both targets. For the superpopulation target every replicate draws fresh donors; for the design-based one a fixed population of $G = 24$ donors is drawn once per cell and the labelled donors are drawn from it without replacement. Coverage at 90%, mean width, width relative to the classical estimator with the same variance. Fan out by $(G_L, \rho)$, fifteen units.

**Acceptance.** At $m = 1$ every clustered variance equals the i.i.d. one to $10^{-12}$. At $r = 0$, $\lambda$ is within 0.05 of 0 under every tuning rule and every interval covers 0.89 to 0.91. At $G_L = 20$ and $m = 200$ every variance variant is within 0.02 coverage of every other. The module reproduces `b1_acceptance.csv` when run in B1's configuration.

**Predictions.**

1. CR1 with $t_{G_L-1}$ covers 0.87 to 0.91 at $G_L \ge 6$ and 0.82 to 0.88 at $G_L = 4$; CR2 with Satterthwaite brings $G_L = 4$ to 0.87 or above.
2. The percentile bootstrap under-covers by at least 0.10 at $G_L \le 8$; bootstrap-$t$ recovers to within 0.03 of nominal; BCa sits between.
3. The over-coverage B2 saw at $n_L = 12$ (0.94 to 0.95) is mostly the missing finite-population correction, not $\lambda$ optimism. With the correction and the design-based target, coverage at $n_L = 12$ of 24 lands at 0.89 to 0.92; cross-fitted $\lambda$ on its own moves it by less than 0.02, at a width cost under 3%.
4. The Welch-Satterthwaite combination matters only when $G_U \le 10$, where it widens the interval by 5% or more.
5. PPI's width relative to classical is below 0.9 only when $r \ge 0.5$ and $\rho \le 0.3$; at $\rho = 0.5$ it stays above 0.9 for every $r$, because predictions do not reduce the between-donor component.

**Outputs.** `results/round4/ppi/Q1_estimator/q1_sim_coverage.csv` (cell, component choices, coverage, width, width ratio, MC standard error), `q1_acceptance.csv`, `q1_report_numbers.csv`, `fig_q1_coverage_by_G.png`, and `docs/round4_ppi_estimator_definition.md`, a one-page definition of the chosen estimator in the paper's notation with its finite-sample behaviour from the simulation quoted beside each choice. Report and wait.

### Q2. The gain theorem and the allocation result (three days; no gate)

**Why.** The paper's two theorems. First, what predictions can buy under cluster sampling. Second, how a labelling budget should be split between clusters and units when a predictor is available.

**Derivation, written out in `docs/round4_ppi_theory.md` before the experiment runs, step by step, in the paper's notation.**

*The gain theorem.* Write each unit's rectifier contribution as $\phi^L_{gi} = u^r_g + e^r_{gi}$, a cluster-level part with variance $\sigma_{u,r}^2$ and a unit-level part with variance $\sigma_{e,r}^2$, and the outcome's own contribution as $u_g + e_{gi}$ with $\sigma_u^2$ and $\sigma_e^2$. With $n_L$ labelled clusters of $m$ units each and the unlabelled term fixed by $G_U$,

$$\text{Var}(\hat\theta_{\text{PP}}) = \frac{\sigma_{u,r}^2}{n_L} + \frac{\sigma_{e,r}^2}{n_L m} + V_U, \qquad \text{Var}(\hat\theta_{\text{cl}}) = \frac{\sigma_u^2}{n_L} + \frac{\sigma_e^2}{n_L m}.$$

Show that as $m$ grows the ratio tends to $\sigma_{u,r}^2 / \sigma_u^2$ (plus the vanishing $V_U$ term), and that with the predictor's error decomposed the same way, $\hat y_{gi} = y_{gi} - a_g - \epsilon_{gi}$, the rectifier's cluster component is $u_g - \lambda a_g$ up to the estimand's weights, so $\sigma_{u,r}^2/\sigma_u^2 = 1 - R^2_{\text{cluster}}$ at the optimal $\lambda$, where $R^2_{\text{cluster}}$ is the squared correlation between the outcome's and the prediction's cluster-level components. State the theorem in words. Under cluster sampling with many units per cluster, the variance reduction from predictions is governed by the predictor's cluster-level $R^2$, not its unit-level $R^2$; a predictor that is accurate within clusters but misses cluster means buys nothing. Give the corollary for $\lambda$ (it tends to the cluster-level regression coefficient of $u$ on $a$, not the unit-level one) and the corollary for when PPI cannot help at all.

*The allocation result.* Start from the classical two-stage sampling result. With costs $c_d$ per cluster and $c_s$ per unit, minimising the classical variance at fixed cost gives $m^\star = \sqrt{(c_d/c_s)\,(\sigma_e^2/\sigma_u^2)}$, with $n_L$ set by the budget. Derive the PPI version, $m^\star_{\text{PP}} = \sqrt{(c_d/c_s)\,(\sigma_{e,r}^2/\sigma_{u,r}^2)}$, and show that because a predictor removes unit-level variation more than cluster-level variation ($\sigma_{e,r}^2 < \sigma_e^2$ while $\sigma_{u,r}^2$ falls only with $R^2_{\text{cluster}}$), $m^\star_{\text{PP}} \le m^\star$. State it in words. A better predictor makes units within a cluster cheaper to skip, so the optimal design moves toward more clusters and fewer units per cluster. Give the point beyond which units buy almost nothing. The unit term is a fraction $f$ of the cluster term once $m \ge (1 - \rho_r)/(f\,\rho_r)$, with $\rho_r$ the between-cluster share of the rectifier contribution; state that $m$ at $f = 0.1$ for each task's fitted $\rho_r$.

**Experiment, by masking.** On CCRCC (24 and merged), Indiana (25 units), lung Xenium (15 donors) and ACS (states as clusters, and PUMAs within one large state as a second setting), for $n_L \in \{4, 6, 8, 12, 16\}$ where the task has enough donors and $m \in \{25, 50, 100, 200, 500, \text{all}\}$, draw $n_L$ labelled clusters and $m$ labelled units within each, compute the classical and PPI estimates with the Q1 estimator, and record the empirical variance across 200 draws, the mean estimated variance, and coverage of $\theta_{\text{full}}$. Three encoders and the permuted predictor on the HEST tasks; the package predictor and a permuted one on ACS. Both populations, $\theta_3$ and $\theta_2$ (on ACS, $\theta_3$ is the slope of log income on standardised age and $\theta_2$ the mean). Measure directly, per task and predictor, the predictor's unit-level $R^2$, within-cluster $R^2$ (pooled over clusters after removing cluster means) and cluster-level $R^2$ (the squared correlation of cluster means of $y$ and $\hat y$, with the small-cluster correction), and set them beside the observed variance ratio at the largest $m$. Fit the derived variance surface to the empirical one and report the fitted components and the implied $m^\star$ at $c_d/c_s \in \{10, 100, 1000\}$. Fan out by task, four units, each running its own grid.

**The recalibration test, a fifth unit (one day, capped).** The theorem says the gain moves with cluster-level $R^2$. The direct test is to change the predictor's cluster-level accuracy while leaving its within-cluster accuracy alone and watch the variance ratio follow. On CCRCC and Indiana, with `hoptimus0`, for each donor compute the mean embedding of its spots (the 256 PCA coordinates averaged, a 256-vector per donor) and, leaving that donor out, fit a ridge regression of the other donors' mean residuals (their offsets $b_g$, the mean of $y - \hat y$ over the donor, per gene on the 50-gene list) on their mean embeddings, then predict the held-out donor's offset and add it to its predictions. Report, per gene, the leave-one-donor-out $R^2$ of predicted against actual offsets, the predictor's cluster-level $R^2$ before and after, its within-cluster $R^2$ before and after (which should be unchanged, since a per-donor constant does not change within-donor ranking), and the Q2 variance ratio at $m = $ all before and after, in `q2_recalibration.csv`. This is the cheapest thing a practitioner could do to a foundation model before spending a labelling budget, and it needs no labels on the test donor. Do not tune the ridge penalty on the held-out donor.

**Predictions.**

1. The observed PPI-to-classical variance ratio at $m = $ all is within 0.1 of $1 - R^2_{\text{cluster}}$ on every task and predictor, and is not predicted by the unit-level $R^2$ (the HEST encoders have unit-level $R^2$ of 0.1 to 0.2 and cluster-level $R^2$ under 0.3; the ACS predictor has a higher cluster-level $R^2$ and a larger gain).
2. The empirical variance is flat in $m$ beyond 100 to 200 units per cluster on every task, within Monte Carlo error.
3. The fitted $\sigma_{e,r}^2$ falls with encoder quality and $\sigma_{u,r}^2$ barely does, so $m^\star_{\text{PP}}$ is smaller for `hoptimus0` than for `resnet50` than for the permuted predictor, on every task.
4. At $c_d/c_s = 100$, $m^\star$ is between 30 and 150 on the Visium tasks and larger on lung Xenium and ACS, whose within-cluster variance is higher.
5. The estimated variance tracks the empirical one within 15% across the grid, except at $n_L = 4$.
6. The recalibration test predicts donor offsets with leave-one-donor-out $R^2$ between 0.1 and 0.4 on the median gene of both tasks, raises the cluster-level $R^2$ by at least 0.1 on those genes, leaves the within-cluster $R^2$ unchanged to $10^{-3}$, and lowers the variance ratio at $m = $ all by an amount within 0.1 of the change in $1 - R^2_{\text{cluster}}$.

**Outputs.** `results/round4/ppi/Q2_theory/q2_variance_grid.csv`, `q2_cluster_r2.csv`, `q2_fitted_components.csv`, `q2_recalibration.csv`, `q2_report_numbers.csv`, `fig_q2_gain_vs_cluster_r2.png`, `fig_q2_variance_vs_m.png`, `fig_q2_optimal_m.png`, and the theory document.

### Q3. Two labelling regimes (three days; gate)

**Why.** The practical question the paper answers. With a fixed budget, is it better to label a few clusters completely or a few units on every cluster? The prediction-set side of the same labelled units (a few labelled spots on the test slide) is the conformal track's C3, using generalised hierarchical conformal prediction; you do not run it here, and Q5 joins the two.

**Regime A**, few clusters fully labelled. This is B1 and B2's design, rerun with the Q1 estimator.

**Regime B**, few units on every cluster. Every donor's slides carry $m$ labelled spots drawn uniformly at random; every other spot is unlabelled. The labelled and unlabelled sets now share clusters, and what the variance is depends on the target, so derive both versions in `docs/round4_ppi_theory.md` before running, in the Q2 notation, with the outcome $y_{gi} = \mu + u_g + e_{gi}$ and the prediction $\hat y_{gi} = \nu + p_g + d_{gi}$.

*Design-based target.* Every cluster is observed, so there is no uncertainty about which clusters were labelled and the clusters act as strata. Per cluster the estimator is the difference estimator $\hat\theta_g = \frac{1}{M_g}\sum_{i \in g}\lambda\hat y_i + \frac{1}{m}\sum_{i \in L_g}(y_i - \lambda\hat y_i)$, whose design variance is $(1 - m/M_g)\,S^2_{r,g}/m$ with $S^2_{r,g}$ the within-cluster variance of the rectifier $y - \lambda\hat y$. The donor-weighted estimate averages the $\hat\theta_g$, so

$$\text{Var}_B^{\text{design}} = \frac{1}{G^2}\sum_g \Big(1 - \frac{m}{M_g}\Big)\frac{S^2_{r,g}}{m},$$

and the classical version has $S^2_{y,g}$ in place of $S^2_{r,g}$. Show that the ratio is $1 - R^2_{\text{within}}$ at the within-cluster optimal $\lambda$, that the cluster-level error $a_g$ of the predictor drops out entirely because it is constant within a cluster and the cluster's own labelled units measure it, and that the variance estimator is the plug-in with the within-cluster sample variances, with a $t$ reference on $G(m - 1)$ degrees of freedom or its Satterthwaite version. Give the spot-weighted version with weights $M_g/N$.

*Superpopulation target.* The $G$ clusters are themselves a sample, so $\text{Var}_B^{\text{super}} = \sigma_u^2/G + \text{Var}_B^{\text{design}}$ up to the finite-population factor, and the between-cluster term cannot be reduced by predictions on the same clusters. Here the cluster-robust estimator $\frac{G}{G-1}\sum_g \hat S_g^2$ over all $G$ clusters, with $S_g$ the cluster's total influence from its labelled and unlabelled contributions and a $t_{G-1}$ reference, is the right one. Show that as $m$ grows this regime's gain from predictions vanishes, because only the within term shrinks.

*The comparison.* At equal unit budget $B = n_L m_A = G m_B$ under the superpopulation target, regime A's variance is $\sigma_u^2(1 - R^2_{\text{cluster}})/n_L + \sigma^2_{e,r}/B$ and regime B's is $\sigma_u^2/G + \sigma^2_{e,r}/B$, so regime B wins on the between term exactly when $R^2_{\text{cluster}} < 1 - n_L/G$; with $n_L = 8$ of $G = 24$ that is $R^2_{\text{cluster}} < 0.67$, which every HEST encoder satisfies. Under the design-based target regime B has no between term at all. State both, and state the crossover in the cost ratio $c_d/c_s$ at which regime A's smaller cluster count pays for its larger variance. The head is trained on the other donors (the harness's calibration-fraction-zero `donor` mode), so no labelled spot on the test donor enters training; the labelled spots are used only in the rectifier.

**Budget matching.** Compare at equal unit budgets $B \in \{2400, 4800, 9600\}$. Regime A spends it on $n_L \in \{4, 6, 8, 12\}$ clusters with $m = B/n_L$ labelled units each (the Q2 grid, reused). Regime B spends it on all $G$ clusters with $m = B/G$ units per cluster, spread over a donor's slides in proportion to their spot counts. Also report a cost-weighted version with $c_d/c_s = 100$, where labelling any unit in a cluster incurs the cluster cost once, so regime B pays $G$ cluster costs and regime A pays $n_L$. Tasks are CCRCC, Indiana, lung Xenium and ACS. Both targets on every row, with the design-based variance for the design-based rows and the cluster-robust one for the superpopulation rows; in the Q1 simulation, add a regime B arm so that superpopulation coverage is checked where fresh donors can be drawn. Fan out by task, four units.

**Acceptance.** Regime B at $m = $ all units equals the full-data value exactly. At $m = 1$ the regime B cluster variance reduces to the formula with one labelled unit per cluster. Regime A reproduces B2's coverage on CCRCC within Monte Carlo error when run with B1's estimator settings.

**Predictions.**

1. At equal unit budget, regime B intervals are narrower than regime A for $\theta_3$ donor-weighted on every task, by 20% or more, because every cluster contributes to the rectifier and the $t$ reference has more degrees of freedom; the advantage shrinks under the cost-weighted budget and reverses when $c_d/c_s \ge 1000$.
2. Regime B design-based coverage is 0.88 to 0.92 at every $m \ge 25$ with the design-based variance, and above 0.97 when the cluster-robust variance is used against the design-based target, because that variance carries a between-donor term the target does not have.
3. The crossover cost ratio at which regime A overtakes regime B is predicted by the Q2 decomposition within a factor of two on every task.
4. Regime A's PPI-to-classical variance ratio tracks the predictor's cluster-level $R^2$ and regime B's tracks its within-cluster $R^2$. Across the three encoders and the permuted predictor on every task, the Spearman correlation of the regime A ratio with $1 - R^2_{\text{cluster}}$ is above 0.8 and with $1 - R^2_{\text{within}}$ below 0.5, and the reverse holds for regime B. The slide offsets of about half a standard deviation seen in round 3 suggest the encoders' within-cluster $R^2$ exceeds their cluster-level $R^2$; if Q2's measurement confirms that, regime B gains more from predictions than regime A on every HEST task.

**Outputs.** `results/round4/ppi/Q3_regimes/q3_regime_comparison.csv`, `q3_report_numbers.csv`, `fig_q3_regimes.png`, and the regime B derivation in the theory document. Report Q2 and Q3 together, predictions against outcomes, and stop.

### Q4. The paper's tables, the ACS application and the gene axis (three days; no gate)

**Real-data tables.** For CCRCC (24 and merged), Indiana and lung Xenium, with the Q1 estimator, the Q2 curves and both Q3 regimes. $\theta_3$ and $\theta_2$ in both populations, $\theta_1$ on IDC under the four-donor labels as the illustration (its four per-donor intervals and the pooled donor-clustered one, which spans zero at 59 times the spot-level width, `results/round3/B1_ppi/b1_theta1_by_slide.csv`). Three encoders and the permuted predictor. 200 draws per setting.

**The ACS application**, as its own unit, in the same table format. Clusters are states (51) and, in a second setting, PUMAs within the largest state. Estimands are the slope of log income on standardised age and the mean of log income, spot-weighted and cluster-weighted. The package predictor and a permuted one. Labelled clusters $n_L \in \{4, 6, 8, 12, 20\}$ under regime A and $m \in \{25, 50, 100, 200\}$ per cluster under regime B. Report the predictor's unit-level and cluster-level $R^2$ beside its gain, per the Q2 theorem. This is the table that makes the paper's results read as general.

**The gene axis.** On CCRCC and Indiana, with the training-only 200-gene lists from `results/round4/data/P6_genes/` under the `donor` folds, the PPI-to-classical width ratio per gene against the gene's cluster-level $R^2$ and its unit-level Pearson, for $n_L = 8$ in regime A and $m = 100$ in regime B. Report the fraction of genes where PPI narrows the interval by more than 5%, and the correlations. The prediction is that the ratio correlates with cluster-level $R^2$ more strongly than with unit-level Pearson, and that fewer than a third of genes gain more than 5% under regime A at $n_L = 8$.

**Two-way clustering, a supplement (one day, capped).** The donor is not the only grouping in the data. The audit file and the task definitions record a second grouping for some tasks, such as the capture slide on lung (four slides carrying two to five donors each), the run or session where the audit records one, and the instrument generation on breast Xenium. Where the second grouping is nested in the donor it adds nothing to a donor-clustered variance and is reported as such. Where the donor is nested in it, as on lung, the higher level is the honest cluster and there are too few of them for a $t$ reference; report the ratio of the slide-clustered to the donor-clustered variance for $\theta_3$ on lung as a diagnostic, with the slide count beside it, and no interval. Where the two groupings cross, compute the two-way cluster-robust variance of Cameron, Gelbach and Miller (2011), the sum of the two one-way sandwiches minus the intersection's, for $\theta_3$ under regime A with the Q1 estimator, and report it beside the donor-only variance. List every task with the second grouping's name, its count and its relation to the donor (nested in, containing, crossed) in `q4_two_way.csv` before any number is computed. The prediction is that no HEST task has a crossed second grouping with more than four levels, so the two-way variance is reported for ACS (state by year of survey, if the package data carries the year) and the HEST result is the nesting table itself.

Fan out by task and estimand, eight units including ACS and the two-way supplement.

**Outputs.** `results/round4/ppi/Q4_tables/q4_main_table.csv` (the paper's Table 2, HEST and ACS in one format), `q4_gene_axis.csv`, `q4_two_way.csv`, `q4_report_numbers.csv`, figure scripts under `code/figures/round4_ppi_fig*.py` writing to `figures/round4/ppi/`, numbers read from files by a `build_q4_numbers.py`.

### Q5. The closing report (two days; gate, end of track)

**The joint design table.** Once the conformal track has committed its C3 outputs (`results/round4/conformal/C3_real/c3_o_sweep.csv`, on branch `round4-conformal`; read it, never write it, and record the commit you read), build `results/round4/ppi/Q5_joint/q5_joint_design.csv`. For each task and each $m$ labelled units per cluster, the row carries regime B's confidence-interval width ratio from Q3 and the prediction-set coverage and width from GHCP at $o = m$ from C3, so the paper can show what one labelling design buys for both targets at once. If C3 is not committed when Q5 starts, build the table with the PPI columns only, mark the conformal columns pending, and say so in the report.

**Inputs for the next round, recorded and not analysed.** Round 5 will ask which clusters to label, not only how many, so write `results/round4/ppi/Q5_joint/q5_cluster_table.csv` with one row per donor and task carrying the donor's spot count, its mean embedding (as a path to a parquet, not inline), its mean residual per gene on the 50-gene list, its within-donor residual variance, and its leave-one-out offset prediction from Q2's recalibration test. No analysis of it in this track.

`docs/round4_ppi_final_report.md` in the format of section 8, covering Q1 to Q5, the full predictions-against-outcomes table for the track, an "Escalations" section, and a closing page titled "What the PPI track established", at most one page, every sentence naming its file. Run the numeric-claim sweep. Tag `round4-ppi-final`. Then stop.

**Time.** About eighteen working days with the gates, the two capped supplements included.

---

## 7. Predictions for the track, consolidated

The stage predictions above, numbered Q1.1 to Q1.5, Q2.1 to Q2.6, Q3.1 to Q3.4, and Q4.1 (the gene axis) and Q4.2 (the two-way table), are the track's predictions. Copy them into `docs/round4_ppi_plan.md` before running and score each in the closing report as held, partly held, refuted or not tested.

---

## 8. Reporting format

After each gate, in this order. 1. Stage and status. 2. What was run (scripts with md5s, commits, job ids, partitions, wall times, peak memory from `sacct`). 3. Acceptance checks with the actual numbers and file paths. 4. For every comparison, the list of variables that differ between its arms, written out. 5. Predictions against outcomes, as a table. 6. Results, numbers from files with paths, dispersion beside every mean; paths rather than pasted tables over 20 rows. 7. Discrepancies, open questions and escalations. 8. What was not checked. 9. Proposed next step.

Keep prose plain, per section 1.

---

## 9. Decision boundaries

**You decide alone.** Sub-agent structure; seeds; the simulation's replicate count above 2,000; bootstrap draws above 500; job sizing; which of two equivalent implementations to use.

**Record as an escalation and continue.** The ACS download being refused by the network (continue with the HEST units; the oversight chat supplies the file); the lung task file disagreeing with the counts in this document (use the file); the recalibration test or the two-way supplement reaching its cap (stop it, report what exists); any acceptance identity failing at a tolerance the dtype supports (fix, rerun, say so); any task where a fold cannot be formed; any new property of the data; any per-task result that reverses a round-3 sign; any need to change a shared file.

**Stop and report.** The Q0 anchor failing. A derivation in Q2 or Q3 that does not close (report the step that fails; the oversight chat will work it with you).

**Never yours.** Contact with anyone outside the project; changes to `main`, to round-3 files, to the data-pull outputs, to the audit file, or to the conformal track's areas; any download.
