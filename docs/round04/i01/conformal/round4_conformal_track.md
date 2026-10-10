> **Active instruction document for the round-4 conformal track, dated 30 September 2026.** This copy includes section 5's working-copies paragraph, which the session received separately as a note and transcribed as section 2 of `docs/round04/tracks/conformal/round4_conf_plan.md` on its branch.

# Round 4, the conformal track: sharper valid prediction sets for a new donor

30 September 2026, revised after the data-pull report. Prepared by the oversight chat for a fresh Claude Science session. This document is self-contained. The track starts from tag `round4-data-v2` on `NicWYZ/HEST-1k-replication`, on its own branch `round4-conformal`, and runs concurrently with a second session on branch `round4-ppi`, which has its own document. Section 5 says how the two coexist. The P8 addendum that produced it is reported in `docs/round04/i02/data/round4_data_P8_report.md`. Read this document fully, then transcribe section 6 into `docs/round04/tracks/conformal/round4_conf_plan.md` before running anything.

---

## 1. Your role and the people

You are the execution agent. A separate chat session, the oversight chat, reviews your reports, makes scope decisions and writes decision memos, which Nicolas hands to you in full. Nicolas Weiyang Zhang (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`) is the first-year biostatistics PhD student whose project this is. He reads every command before it runs and will ask why. His advisors are Dr. Hongtu Zhu and Dr. Daiwei (David) Zhang at UNC.

Your responsibilities are to run the planned analyses on UNC Longleaf through Slurm, verify every stage's output against an expected value before moving on, write stage reports in the format of section 8, commit and push on your branch, and stop at each gate. You do not make scope decisions. Anything this document does not cover is reported as a proposal, not done.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. This track's gates are C2 (the go or no-go) and C4. Contact with anyone outside the project is never the session's decision.

**How Nicolas wants things written.** Plain, natural prose. No em-dashes. No colon-then-explanation constructions. Math as LaTeX. Numbers quoted at the precision the comparison needs, with the relative scale stated; full precision stays in the files. Every number in a report is read back from the file named beside it. When a derivation is asked for, write it out step by step. Do not inflate length.

---

## 2. The project, and what this track is for

### 2.1 In one page

Spatial transcriptomics measures gene expression at known spots on a tissue section. A frozen pathology foundation model maps each spot's H&E patch to an embedding, and a linear head (standardise, PCA to 256, ridge with an intercept in float64) predicts $y_{ig} = \log(1 + \text{count}_{ig})$ per gene. Per-gene Pearson is about 0.3 to 0.4. The data are nested, spots inside slides inside donors.

Rounds 1 to 3 replicated the HEST-1k benchmark exactly, instrumented it, and measured what happens to prediction intervals when the test spots come from a donor the model never saw. The results this track builds on, with their files:

1. **Coverage under donor shift is set by where the calibration scores come from.** On one shared training set, split conformal calibrated on held-out donors covers 0.856 and calibrated on spatial blocks inside the training slides covers 0.744, block lower in 138 of 138 cells; block intervals fail by being too narrow, not misplaced (`results/round3/A2_conditional/a2_unit_intervention.csv`, `a2_level_scale.csv`). Even at the donor level the pooled spot quantile under-covers by three to four points with wide fold-to-fold scatter (CCRCC 0.25 to 0.98 across folds), and that shortfall does not track the number of calibration donors $K$ or the between-donor share of score variance (`a2_coverage_vs_K.csv`).
2. **Feature-based reweighting cannot help.** Calibration and test slides are separable at held-out AUC 0.97 or better from the embedding and 0.90 from eight morphology covariates alone; weighted conformal's effective calibration size collapses to a median 2% (`results/round3/A3_report_numbers.csv`). Closed.
3. **The valid method exists and is conservative.** Hierarchical conformal prediction (HCP, Lee, Barber and Willett, arXiv:2306.06342) is infinite wherever $K + 1 < 1/\alpha$, in 1,932 of 1,932 cells. With $K = 10$ calibration donors on CCRCC it is finite in every cell and covers 0.969 at 1.95 times the pooled quantile's width; the one-score-per-donor interval of Dunn, Wasserman and Ramdas (JASA 2023) covers 0.911 at 1.43 times; the pooled quantile covers 0.864 whether 6 or 10 donors calibrate it. On Indiana kidney at $K = 10$, HCP covers 0.988 at 1.91 times (`results/round3/A4_scores/a4b_summary.csv`, `results/round3/D4_expansion/d4_pooled_numbers.csv`).
4. **Adaptive scores buy little width at matched coverage except in the upper tail.** CQR is 2.65 wide against 2.69 for the absolute score at 90%; in the top decile of predicted values, where the absolute score covers 0.72, CQR and conformalised negative binomial reach 0.87 (`results/round3/A4_scores/a4_report_numbers.csv`).
5. **The labels are audited.** Every donor label used in round 4 comes from `results/round4/data/P4_audit/donor_audit_r4.csv`. CCRCC's 24 donor labels are unverifiable at donor level and `INT4` and `INT24` may be one donor, so every CCRCC analysis runs with 24 donors and with the two merged, both reported. IDC's four benchmark samples are four donors.

The full account is in `docs/round03/i03/exec/round3_final_report.md` (read its closing page, "What round 3 established", and section 6.3) and `docs/round03/i02/exec/round3_A3_stage_report.md` section 6.8. The scripts you start from are `code/scripts/round3_a4b_hcp.py` (HCP, the one-per-donor interval and the pooled quantile on the harness's $K = 10$ design) and `code/scripts/round3_a3_weighted.py` (the weighted quantile machinery HCP runs through).

### 2.2 What this track is for, and what is and is not new

The gap between HCP's 0.97 and nominal 0.90, at double the width, was the open problem round 3 left. The oversight chat checked the literature on 28 September, and the position is this. Mallick, Tchetgen Tchetgen, Dobriban and Lee, "Generalized Hierarchical Conformal Prediction" (GHCP, arXiv:2608.15500, 15 August 2026), start from the same observation, that HCP with $K$ calibration groups calibrates at level $(1-\alpha)(K+1)/K$ and is conservative at small $K$. Their method assumes $o \ge 1$ initial observations from the test group, restores hierarchical exchangeability by a random donation of a reference group's size, uses part of the $o$ observations to adapt the score to the test group, and is provably valid under their assumptions A1 to A3 and empirically narrower than HCP. Their real-data example is ACS PUMS income. Two consequences. The labelled-spots-on-the-test-slide idea is their setting, and GHCP is the method for it; this track implements it, uses it, cites it, and does not compete with it. And the case with no test-group observations, $o = 0$, is not treated beyond HCP, and no lower bound on the price of validity at small $K$ exists in the literature they cite.

So the track has three jobs, in this order of value to the paper. First, the price of validity as a map over $(K, o)$, in simulation with an oracle and on real data, with HCP at $o = 0$ and GHCP at $o > 0$; this is the paper's prediction-set section and the conformal half of its joint-design result. Second, the spatial transcriptomics application on three tasks with audited donors, and ACS on the same footing as the GHCP paper. Third, a bounded theoretical scoping of the $o = 0$ question, whether any valid method can be sharper than HCP at small $K$, which is a lower-bound question; it gets three days and a stop rule, and it is the one place a theoretical contribution is possible. The candidate methods of C2 are kept only where they still have a role beside GHCP.

The PPI track handles the confidence-interval side of the same labelled units; the joint-design table is built by the PPI track's Q5 from your C3 outputs, which is why C3's output format is fixed below.

### 2.3 The methods, stated once

**Split conformal.** Scores $s_i$ on a calibration set of $n$ spots; the interval for a new spot is $\{y : s(y) \le \hat q\}$ with $\hat q$ the $\lceil (n+1)(1-\alpha) \rceil$-th smallest calibration score. If the $n+1$ scores are exchangeable, coverage is at least $1 - \alpha$ and at most $1 - \alpha + 1/(n+1)$. A finite $\hat q$ exists only if $n \ge (1-\alpha)/\alpha$. Equivalently, $\hat q$ is the $(1-\alpha)$ quantile of the distribution that puts mass $\frac{1}{n+1}$ on each calibration score and $\frac{1}{n+1}$ on an atom at $+\infty$ standing for the unseen test score.

**Hierarchical exchangeability.** Donors are exchangeable with each other and spots are exchangeable within a donor, but a spot from one donor is not exchangeable with a spot from another. The question is coverage for a spot from a new donor.

**HCP.** Each of the $K$ calibration donors gets total mass $\frac{1}{K+1}$, spread equally over its $N_k$ spots, so spot $i$ of donor $k$ has weight $\frac{1}{(K+1)N_k}$; the test donor's $\frac{1}{K+1}$ is an atom at $+\infty$. With $F_k$ donor $k$'s empirical score CDF and $\bar F = \frac{1}{K}\sum_k F_k$, the cumulative mass at a finite $q$ is $\frac{K}{K+1}\bar F(q)$, and $\hat q$ is the smallest $q$ with $\frac{K}{K+1}\bar F(q) \ge 1-\alpha$, which at $K = 10$ and $\alpha = 0.1$ is the 99th percentile of the donor-balanced score distribution. Coverage is at least $1-\alpha$ for any $K \ge 1$ and at most $1 - \alpha + 2/(K+1)$ when scores are distinct; the interval is finite only when $\frac{1}{K+1} \le \alpha$.

**One score per donor** (Dunn, Wasserman and Ramdas). Draw one calibration spot per donor, apply split conformal to the $K$ resulting scores. Valid, noisy, wasteful. Their repeated-subsampling and CDF-pooling variants are in the same paper.

**GHCP** (Mallick, Tchetgen Tchetgen, Dobriban and Lee 2026). With $o$ initial observations from the test group, the test group is assigned a randomly donated size from the reference groups that have more than $o$ observations, which restores the symmetry HCP needs; part of the $o$ observations may train a test-group-specific score, the rest calibrate. The guarantee is finite-sample under their assumptions A1 to A3, which generalise hierarchical exchangeability by allowing separate mechanisms for the observed test-group size and the reference-group sizes. Implement it from the paper (check whether code is released; if it is, use it and record the commit; if not, implement and validate against every simulation figure the paper reports that can be reproduced from its stated settings). Its restricted-donor variant is included if the paper's description is complete enough to implement inside the cap; otherwise it is listed as not run.

**The oracle.** In simulation, the new-donor score distribution is known, so the half-width $q^\star$ at which a new donor's spot is covered with probability exactly $1-\alpha$ is computable. The price of validity of a method is $\hat q / q^\star$.

**References.** Mallick, Tchetgen Tchetgen, Dobriban and Lee, arXiv:2608.15500; Lee, Barber and Willett, ACM Journal of Data Science 2026, arXiv:2306.06342; Dobriban and Yu 2025 and Duchi et al. 2025 as GHCP cites them; Dunn, Wasserman and Ramdas, JASA 118(544), 2023, arXiv:1809.07441; Vovk, Gammerman and Shafer, *Algorithmic Learning in a Random World*, 2005 (smoothed conformal); Romano, Patterson and Candès, NeurIPS 2019 (CQR); Barber, Candès, Ramdas and Tibshirani, Annals of Statistics 2023 (beyond exchangeability); Lei, G'Sell, Rinaldo, Tibshirani and Wasserman, JASA 2018.

---

## 3. The repository, the data and the assets you build on

**Repository** at tag `round4-data-v2`. `results/round3/` and `results/round4/data/` are read-only for you. `docs/WAYS_OF_WORKING.md` is the accumulated procedure; read it before your first job. `docs/round04/i01/data/round4_data_report.md` and `docs/round04/i02/data/round4_data_P7_decisions.md` say what the data pull delivered and what the oversight chat decided about it.

**Longleaf** project tree `/work/users/w/e/weiyang/hest_replication`. Never compute on the login node.

| asset | path | what it gives you |
|---|---|---|
| audited labels | `results/round4/data/P4_audit/donor_audit_r4.csv` | the only grouping source |
| task definitions | `results/round3/task_defs/`, `results/round3/D4_expansion/task_defs/`, `results/round4/data/P5_task/LUNG_XENIUM.json` | CCRCC, Indiana kidney (25 donor units), lung Xenium (20 samples and 15 donors after the P8 addendum; read the counts and the `dropped_patch_barcodes` list from the file), the other benchmark tasks; the $K = 10$ design is recorded for CCRCC, Indiana and lung, and on lung it trains on 4 donors |
| the harness | `code/scripts/round3_a0_harness.py`, md5 `0ad7ae8efe554c1f285e5f384a9fb7f5` | folds, size matching, the float64 head, the calibration-unit rule; the $K = 10$ design is reached by passing $(K - 0.5)/n_{\text{units}}$ as the calibration fraction; import it unmodified |
| A4b | `code/scripts/round3_a4b_hcp.py`, `results/round3/A4_scores/a4b_hcp_K10.csv`, `a4b_summary.csv` | HCP, one-per-donor and pooled at $K = 10$ on CCRCC; your anchor |
| A3 | `code/scripts/round3_a3_weighted.py`, `results/round3/A3_weighted/a3_by_fold.csv` | the weighted-quantile code path with the test point's own weight in the normaliser |
| score moments | `results/round3/A2_conditional/a2_score_moments__<enc>.parquet` | per (fold, unit, gene) mean, variance and quantiles of calibration and test scores; the empirical basis for the simulation model |
| embeddings | `embeddings/<task>/<encoder>/`, `embeddings_ext/<set>/<encoder>/<sample>.h5` | `hoptimus0`, `uni_v2`, `resnet50`; expansion rows are patches in patch order with readable barcodes |
| gene lists | `results/round4/data/P6_genes/genes__<TASK>__<k>.csv` | training-only lists; C3 uses the 50-gene lists for comparability with round 3 and reports the 200-gene lists as a supplement; on lung the target list is the 343-gene panel in the task file |
| the numeric-claim gate | `code/scripts/sweep_table.py` | run before every handover |

**The lung task, as delivered.** Twenty TGen fibrosis TMA cores (sixteen of 3 mm, four of 5 mm) from fifteen donors, one laboratory, one instrument (`XETG00048`), one software generation, one pixel size, 343 target genes after the 198 controls are removed. Disease is not fixed (IPF, control lung, sarcoidosis and four other diagnoses), so donor effects there carry disease as well as person, which is one reason to expect a larger between-donor share of score variance than on the kidney tasks; say so wherever lung is compared with them. Every capture slide carries two to five donors, so there is no slide-out design, and the slide id is recorded per sample. Five donors have two samples, ten have one. Each donor fold leaves 14 donors, so the $K = 10$ design trains on 4 donors; record the training-donor count beside every lung number. `NCBI865` is a member with one patch barcode (`051x019`) dropped, listed under `dropped_patch_barcodes` in the file; its embedding file still has 2,143 rows. Apply the drop list before any subset assertion. Round 3's `round3_d4_sets.load_set` asserts the relation on the embedding file's barcodes and will raise on `NCBI865` if called directly, so read lung through a wrapper in your own module that removes dropped barcodes first and then asserts; do not edit the round-3 loader. Exercise the wrapper on `NCBI865` in setup and record 2,142 rows. Core size also varies. Sixteen samples are 3 mm cores and four (`NCBI864`, `NCBI865`, `NCBI867`, `NCBI884`) are 5 mm cores from a different TMA, recorded per sample under `expansion.core_diameter_mm_source`; it is on the lung difference list beside disease, and a 5 mm core contributes more spots per donor.

**Xenium control features.** Any Xenium panel or target list you read has `NegControl*`, `UnassignedCodeword*` and `BLANK*` features removed first, and the count removed is recorded. Round 3's `BREAST_XENIUM.json` carries 61 such features in its target list; the lung file carries none.

**Quarantined.** Round 3's D4 probe box was twice too wide, so its statement that morphology removes 31% to 34% of the probe signal is not to be cited.

---

## 4. Standing rules and conventions

- Silent failure is the main risk. Verify each stage's output against an expected value before moving on. Every refit has one arm anchored to a prior result.
- Never assert a number you have not read back from a file. Cite the path.
- Before naming a term, list in writing every variable that differs between its arms. For each candidate method, write out what it assumes and what guarantee it carries before it runs.
- Write predictions down before running, and report them beside the outcomes. The go or no-go criterion is written before C2 runs and is not revised after.
- Every output directory gets `PROVENANCE.txt` (job id, partition actually used, node, date, commit, command line, config hash with its config, `PYTHONHASHSEED`, md5 of the script that ran) and is stamped with `stamp_dir()` from the `longleaf-provenance` skill, written by the job on the node. A sub-agent stamps from its own process, so the frame id recorded is its own and not the lead's. Before reusing or rebuilding any output you did not create, run `whose()` on it; if the verdict is `sibling` or `unstamped`, ask the oversight chat rather than rebuilding.
- Explicit `pa.schema` on every parquet; summaries before bulk tables; seeds from `zlib.crc32`, never `hash()`.
- The submission route replaces `--job-name`, so jobs are identified by Slurm id. Record the intended prefix `r4conf_` and the stage in `PROVENANCE.txt` instead.
- Memory from `sacct` (16 GB on 4 CPUs for head fitting; the simulation is small). Slurm time limits at about three times the expected runtime from a sibling job, never a blanket 16 h. Harness ceiling from queue time plus runtime. Record the partition the job ran on. Set the working directory explicitly in every job script.
- Put a time cap on anything that is not analysis, and stop at the cap. Checker or tooling work is capped at half a day per interval.
- Commit messages through a file. Sub-agents run no git command; the lead is the only committer and checks every hand-back against its primary tables before commit. One writer per file; fragments plus a merge step with collision reporting.
- Do not edit `README.md`, `docs/WAYS_OF_WORKING.md`, `docs/README.md`, any round-3 file, or anything under `results/round4/data/` or the PPI track's areas. Proposed edits go in the report.
- Run `code/scripts/sweep_table.py` over the README and `docs/round04/**/round4_conf_*.md` before every handover.

**Fan-out.** Every stage below names its parallel units. Dispatch one sub-agent per unit with a written brief that includes, verbatim, "Stamp every output directory with `stamp_dir()` from the `longleaf-provenance` skill. Before reusing or rebuilding any output you did not create, run `whose()` on it; if the verdict is `sibling` or `unstamped`, ask me rather than rebuilding." Each sub-agent writes its own fragment under its own directory; the lead merges, recomputes every pooled number from the merged tables into a `<stage>_report_numbers.csv`, and commits.

---

## 5. Two sessions on one repository

The PPI track runs at the same time, on branch `round4-ppi`, writing under `results/round4/ppi/`, `code/scripts/round4_ppi_*.py`, `docs/round04/**/round4_ppi_*.md` and, on Longleaf, `results/round4/ppi/`. You never write there and it never writes in your areas.

Your areas. Branch `round4-conformal`, from tag `round4-data-v2`, never rebased and never merged into `main` by you. Scripts `code/scripts/round4_conf_*.py`. Results `results/round4/conformal/<STAGE>/`. Documents `docs/round04/tracks/conformal/round4_conf_plan.md`, `docs/round04/i01/conformal/round4_conf_C2_report.md`, `docs/round04/i02/conformal/round4_conf_final_report.md`. Longleaf scratch `results/round4/conformal/` under the project tree, stamped. Tags `round4-conf-C2`, `round4-conf-final`.

Shared and read-only for both are everything under `results/round3/` and `results/round4/data/`, the embeddings, the morphology parquets and the harness. If you find you need to change a shared file, that is an escalation, not an edit. Neither track writes the audit file.

**Working copies.** Each session has its own working copy, locally and on Longleaf, and never checks out a branch in a working copy the other session uses. Locally, the PPI track works in `~/HEST-1k-replication` and the conformal track in a sibling clone `~/HEST-1k-replication-conformal`. On Longleaf, the project tree `/work/users/w/e/weiyang/hest_replication` stays on `main` at `round4-data-v2` and nobody checks out a branch there; it is the data root that the harness's `ROOT` points to, and your results directories inside it are disjoint from the other track's. Your code runs from your own clone under `/work/users/w/e/weiyang/hest_code/<branch>/`, put on `PYTHONPATH` in every job script, and every job records that clone's HEAD and the md5 of the script it executed. Before your first job, confirm that the harness in your clone has md5 `0ad7ae8efe554c1f285e5f384a9fb7f5`.

---

## 6. The plan

### C0. Setup (half a day, capped at one day)

1. Read this document, `docs/WAYS_OF_WORKING.md`, `docs/round03/i03/exec/round3_final_report.md` section 6.3 and its closing page, `docs/round03/i02/exec/round3_A3_stage_report.md` section 6.8, `docs/round04/i01/data/round4_data_report.md` and `docs/round04/i02/data/round4_data_P7_decisions.md`. Transcribe section 6 into `docs/round04/tracks/conformal/round4_conf_plan.md`, including the go or no-go criterion verbatim. Flag anything that looks wrong in the C2 report rather than changing it.
2. Create the branch and directories. Run `whose()` on `results/round4/data/` and record the verdict. Read the lung task file and record its sample count, donor count, `a4b_k10` fold count and dropped barcodes in the plan; the counts in this document are what the file is expected to say, and the file wins.
3. **Anchor.** Rerun `round3_a4b_hcp.py`'s $K = 6$ arm on CCRCC for one encoder and reproduce A1's committed `donor` coverage to $10^{-15}$, and its $K = 10$ HCP coverage to `a4b_summary.csv` at $10^{-12}$. Nothing in C1 starts until this passes.

### C1. The simulation testbed and the known methods (three days; no gate, reported with C2)

**Why.** The candidates have to be compared against a known truth, with the oracle width available, before anything runs on real data. The testbed is also where the paper's "price of validity as a function of $K$" figure comes from.

**Script.** `round4_conf_sim.py`, with the generator, every method and the oracle behind one interface, so C2's candidates plug in without touching C1's code.

**The generator.** Hierarchical scores, with an $o$ axis. Each replicate draws $K$ calibration donors, one test donor with 500 test spots, and additionally $o \in \{0, 5, 10, 25, 50, 100\}$ initial observations from the test donor that the $o > 0$ methods may use and the $o = 0$ methods ignore. For donor $k$, a location shift $a_k \sim N(0, \sigma_a^2)$ and a scale multiplier $b_k = \exp(\tau\,\eta_k)$ with $\eta_k \sim N(0, 1)$; for spot $i$ of donor $k$, a residual $r_{ki} = a_k + b_k\,\epsilon_{ki}$ with $\epsilon$ standard normal or Student $t_3$ (two tail settings); the score is $s_{ki} = |r_{ki}|$. A third generator resamples residuals from the round-3 score-moment files so that one setting is anchored to CCRCC's measured between-donor and within-donor score variances; call it the semi-real setting and report its fitted parameters. Grid: $K \in \{5, 7, 9, 10, 12, 15, 20, 25, 50\}$; $N_k \in \{100, 500, 2000\}$ (equal, and one unequal setting with $N_k$ log-uniform over that range); the between-donor share of score variance $\in \{0.1, 0.3, 0.5\}$ set through $\sigma_a$ at $\tau = 0$, plus $\tau \in \{0, 0.3\}$; $\alpha \in \{0.1, 0.2\}$. 5,000 replicates per cell; each replicate draws $K$ calibration donors and one test donor with 500 test spots. Fan out by $K$, nine units.

**The known methods.** (1) The pooled spot-level quantile. (2) HCP. (3) One score per donor, single draw. (4) Dunn, Wasserman and Ramdas's repeated subsampling, implemented as the paper states it, with the guarantee recorded as the paper states it. (5) GHCP at every $o > 0$, with its within-group adaptation on and off. (6) Within-test-group split conformal alone at $o > 0$, using only the $o$ observations, as the naive comparator GHCP should beat at small $o$. (7) The oracle $q^\star$, from a $10^6$-spot draw of new donors per cell, and at $o > 0$ the oracle for the test donor itself, its own $(1-\alpha)$ score quantile, which is what enough test observations would reveal.

**Metrics per cell and method.** Realised coverage for the new donor's spots, its across-replicate standard deviation, the fraction of replicates with an infinite interval, mean half-width, and the price of validity $\hat q / q^\star$. Monte Carlo standard error beside every coverage.

**Acceptance.** At $K = 50$ and share 0.1, HCP's coverage is within 0.01 of nominal. GHCP reproduces every figure in its paper that its stated settings allow, within Monte Carlo error, before any other GHCP number is read. At $\sigma_a = 0$ and $\tau = 0$ (no donor effect), every method's coverage is within 0.01 of nominal and the pooled quantile's price of validity is within 0.02 of 1. HCP is infinite exactly when $K + 1 < 1/\alpha$. On the semi-real setting at $K = 10$, HCP's coverage and width ratio to pooled reproduce A4b's 0.969 and 1.95 within 0.02 and 0.15.

**Predictions.**

1. HCP covers at least $1 - \alpha$ in every cell; its price of validity is 1.8 to 2.2 at $K = 10$, 1.3 to 1.5 at $K = 25$ and 1.1 to 1.2 at $K = 50$, higher under $t_3$ tails.
2. The pooled quantile under-covers in proportion to the between-donor share (about 0.87 at share 0.3, 0.83 at 0.5) at every $K$, with no $K$ dependence.
3. The one-per-donor interval covers at nominal with an across-replicate standard deviation three to five times HCP's; repeated subsampling reduces that spread at the same mean.
4. GHCP at $o = 25$ covers at or above $1 - \alpha$ in every cell and has a price of validity below 1.4 at $K = 10$, and at $o = 100$ below 1.15; within-group split conformal alone matches it at $o \ge 100$ and is worse at $o \le 25$.
5. The gap between HCP at $o = 0$ and GHCP at $o = 5$ is the largest single step in the whole $(K, o)$ map.

**Outputs.** `results/round4/conformal/C1_testbed/c1_grid.csv` (one row per cell, method and $o$), `c1_ghcp_reproduction.csv`, `c1_acceptance.csv`, `c1_report_numbers.csv`, `fig_c1_price_of_validity.png` (the $(K, o)$ map).

### C2. The remaining candidates, the lower-bound scoping, and the go or no-go (four days; gate)

**The criterion, fixed here.** A candidate goes forward to real data if, at $\alpha = 0.1$, across every C1 cell at its $o$, (a) its realised coverage is at least 0.89 in every cell, (b) its price of validity is at most $1 + \tfrac{1}{2}(\pi_{\text{ref}} - 1)$ in at least two thirds of the cells, where $\pi_{\text{ref}}$ is the reference method's price in the same cell, HCP at $o = 0$ and GHCP at $o > 0$, and (c) it carries a stated guarantee, finite-sample under hierarchical exchangeability or model-based with the model named. A candidate that meets (a) and (b) without (c) is reported as a heuristic and does not go forward alone. Whatever the candidates do, C3 runs; the criterion decides only whether any candidate joins the known methods there.

**The candidates**, each behind the C1 interface, with assumptions and guarantee in the docstring before it runs. Double conformal and repeated subsampling are dropped as candidates (the first is infinite at $K = 10$; the second stays as a known method in C1).

- **K1, smoothed HCP at $o = 0$.** The smoothed conformal construction of Vovk, Gammerman and Shafer applied at the donor level, so that the guarantee holds with equality in expectation. State the threshold rule and its guarantee before running. Expected to recover little; it is cheap and it bounds what tie-handling alone can do.
- **K4, a group-level quantile model at $o = 0$.** Per calibration donor its empirical $(1-\alpha)$ score quantile $q_k$; a location-scale model across donors; the new donor's quantile predicted as $\hat q = \bar q + t_{K-1,\,1-\alpha'}\, s_q \sqrt{1 + 1/K}$ for $\alpha' \in \{0.5, 0.25, 0.1\}$. Not distribution-free; model-based, conditional on the $q_k$ being approximately normal across donors, checked in the semi-real setting. The route most likely to be sharp and least likely to be safe under $t_3$ tails; say so.
- **K5, an adaptive score inside HCP and GHCP.** The scaled score $|r|/\hat\sigma$ with a within-donor scale estimate and, in C3, the CQR score, tested under $\tau = 0.3$. The guarantee is the host method's, unchanged. The question is width at matched coverage and top-decile coverage.

Fan out by candidate, three units.

**The lower-bound scoping at $o = 0$ (three days, capped, run by the lead in parallel with the candidate units).** The question is whether any distribution-free method with finite-sample coverage $1 - \alpha$ for a spot of a new group, given $K$ exchangeable calibration groups and no observation from the test group, can have expected width below HCP's by more than a vanishing amount, or whether HCP is minimax-optimal in a sense that can be stated. Work from the standard lower-bound arguments for exchangeable conformal (the impossibility of conditional validity, Lei and Wasserman 2014 and Vovk 2012, and the Foygel Barber et al. 2021 limits) lifted to the group level, where the object the test group contributes is a whole score distribution rather than a score. Write `docs/round04/i01/conformal/round4_conf_lower_bound.md` as you go, with each step marked derived, conjectured or failed. Stop rule. If after three days there is no statement with a proof sketch, write the document as a record of what was tried and stop; the scoping is then reported as no-go on the theory and nothing further is spent on it. If there is a statement, the report says what it is and the oversight chat decides whether it is pursued.

**Predictions.**

1. K1 recovers less than a tenth of the gap at $K = 10$; the atom's mass, not tie-breaking, is what costs width.
2. K4 at $\alpha' = 0.5$ covers 0.88 to 0.92 at a price of validity 1.1 to 1.3 under normal tails and under-covers by three to six points under $t_3$ tails at share 0.5; at $\alpha' = 0.25$ it covers at or above 0.90 everywhere at a price of 1.2 to 1.4, and it meets (a) and (b) but not (c).
3. K5 leaves marginal coverage unchanged and reduces width at matched coverage by 5 to 15% under $\tau = 0.3$, inside HCP and inside GHCP alike.
4. No $o = 0$ candidate meets all three parts of the criterion; GHCP at $o \ge 5$ is the method that goes to real data, with K5 as its score.
5. The lower-bound scoping produces a conjecture with a partial argument, not a theorem, inside its three days.

**Outputs.** `results/round4/conformal/C2_candidates/c2_grid.csv`, `c2_criterion.csv` (one row per candidate and $o$ with (a), (b), (c) and the verdict), `c2_report_numbers.csv`, `fig_c2_candidates.png`, `docs/round04/i01/conformal/round4_conf_candidate_definitions.md` and `docs/round04/i01/conformal/round4_conf_lower_bound.md`. Report C1 and C2 together, predictions against outcomes, the criterion table, and stop.

### C3. Real data, the $(K, o)$ map (four days; no gate)

**The tasks.** CCRCC (24 donors and merged), Indiana kidney (25 donor units), lung Xenium (15 donors), and ACS PUMS income with states as groups, the dataset the GHCP paper uses, fetched by the PPI track in its Q0 into `results/round4/ppi/Q0_setup/acs/` (read it there; if it is not present when C3 starts, run the HEST tasks and add ACS when it appears, recording the commit you read it from). Three encoders on the HEST tasks; the package predictor on ACS.

**The $K$ axis.** The $K = 10$ design from the task definitions, and on CCRCC a sweep $K \in \{4, 6, 8, 10, 12, 14, 16, 18, 20\}$ through the calibration fraction, with the training-donor count recorded beside each $K$ since it falls as $K$ rises. On lung the $K = 10$ design trains on 4 donors, so run $K \in \{6, 8, 10\}$ there and read the three together; at $K = 6$ HCP is finite only at $\alpha = 0.2$, and that row is still reported. Methods at $o = 0$ are the pooled quantile, HCP, one-per-donor, and any $o = 0$ candidate that passed C2.

**The $o$ axis.** For each test donor, $o \in \{5, 10, 25, 50, 100, 200\}$ labelled spots drawn uniformly from the test donor's own spots (on lung a donor's core or cores, never the capture slide, which carries other donors), 20 draws with crc32 seeds. Methods are GHCP (with and without within-group adaptation), within-slide split conformal alone (the $o$ spots as the only calibration), and the recentred cross-donor interval (the pooled cross-donor quantile of round 3's `donor` design after shifting predictions by the labelled spots' mean residual), which is the cheapest thing a practitioner would try. Absolute score and, for K5, the scaled and CQR scores. Coverage and width for the slide's remaining spots, per slide, then the metric convention. This is the arm that was in the PPI track's plan as within-slide conformal; it lives here now and runs GHCP as the reference.

**The output format is fixed**, because the PPI track's Q5 reads it. `results/round4/conformal/C3_real/c3_o_sweep.csv` with columns task, label_set, encoder, method, score, alpha, o, K, fold, draw, coverage, width_mean, width_median, n_test, finite, and the by-task pooled version `c3_o_sweep_by_task.csv`. Also `c3_K_sweep.csv`, `c3_by_fold.csv`, `c3_report_numbers.csv`, `fig_c3_K_sweep.png`, `fig_c3_o_sweep.png`.

**Acceptance.** The $K = 10$, $o = 0$ pooled, HCP and one-per-donor rows on CCRCC reproduce `a4b_summary.csv` to $10^{-12}$ before any other row is read. GHCP on ACS with the GHCP paper's settings reproduces its reported numbers within Monte Carlo error where the settings are stated.

**Predictions.**

1. HCP's coverage on CCRCC falls from about 0.99 at $K = 4$ (finite only at $\alpha = 0.2$) to about 0.95 at $K = 20$, and its width ratio to pooled from above 3 to about 1.4; the pooled quantile stays at 0.86 to 0.87 at every $K$.
2. GHCP at $o = 25$ covers 0.90 to 0.94 on every HEST task at $K = 10$ with a width ratio to pooled of 1.2 to 1.4; at $o = 100$ its width is within 10% of within-slide split conformal, which is at nominal from $o = 50$ on.
3. Recentring alone recovers more than half of the cross-donor shortfall at $o = 25$ on the unit-calibrated tasks and less than a third on the block-calibrated ones (HCC, LUNG, SKCM), where the failure is scale.
4. The top-decile shortfall (0.72 under the cross-donor absolute score) closes to 0.85 or above under GHCP with the CQR score at $o \ge 25$.
5. Indiana reproduces the CCRCC pattern with a smaller gap (its fold scatter is a third of CCRCC's); lung Xenium has a larger one; ACS sits between, and the GHCP paper's ACS numbers are reproduced.

Fan out by task and axis, eight units.

### C4. The closing report (two days; gate, end of track)

`docs/round04/i02/conformal/round4_conf_final_report.md` in the format of section 8, covering C1 to C3, the full predictions-against-outcomes table, an "Escalations" section, and a closing page titled "What the conformal track established", at most one page, every sentence naming its file, ending with a one-paragraph statement of what the prediction-set section of the paper says and whether the lower-bound scoping produced anything worth pursuing. Run the numeric-claim sweep. Tag `round4-conf-final`. Then stop.

**Time.** About fourteen working days with the gates.

---

## 7. Predictions for the track, consolidated

The stage predictions above, numbered C1.1 to C1.5, C2.1 to C2.5 and C3.1 to C3.5, are the track's predictions. Copy them into `docs/round04/tracks/conformal/round4_conf_plan.md` before running and score each in the closing report as held, partly held, refuted or not tested.

---

## 8. Reporting format

After each gate, in this order. 1. Stage and status. 2. What was run (scripts with md5s, commits, job ids, partitions, wall times, peak memory from `sacct`). 3. Acceptance checks with the actual numbers and file paths. 4. For every method, its assumptions and guarantee as written before it ran, and for every comparison the list of variables that differ between its arms. 5. Predictions against outcomes, as a table. 6. Results, numbers from files with paths, dispersion beside every mean; paths rather than pasted tables over 20 rows. 7. Discrepancies, open questions and escalations. 8. What was not checked. 9. Proposed next step.

Keep prose plain, per section 1.

---

## 9. Decision boundaries

**You decide alone.** Sub-agent structure; seeds; replicate counts above 5,000; the exact form of the semi-real generator's fit; job sizing; implementation details of a candidate that its definition leaves open, provided the docstring records the choice before the run.

**Record as an escalation and continue.** The lung task file disagreeing with the counts in this document (use the file); any acceptance check failing at a tolerance the dtype supports (fix, rerun, say so); any candidate whose stated guarantee you cannot verify against its source paper (run it, mark (c) as unmet, say why); any new property of the data.

**Stop and report.** The C0 anchor failing. The C1 acceptance on the semi-real setting failing to reproduce A4b, which would mean the generator does not represent the data.

**Never yours.** Spending more than three days on the lower-bound scoping; revising the go or no-go criterion after C2 starts; contact with anyone outside the project; changes to `main`, to round-3 files, to the data-pull outputs, to the audit file, or to the PPI track's areas; any download.
