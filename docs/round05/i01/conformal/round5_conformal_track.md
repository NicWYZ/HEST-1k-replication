# Round 5, the prediction-set track: the map completed, and what can and cannot beat the hierarchical method

7 October 2026. Prepared by the oversight chat for a fresh Claude Science session. This document is self-contained. The track starts from `main` of `NicWYZ/HEST-1k-replication` at the commit that carries this document, on its own branch `round5-conformal`, and runs concurrently with a second session on branch `round5-ppi`, which has its own document. Section 5 says how the two coexist. Read this document fully, then transcribe section 6 into `docs/round05/tracks/conformal/round5_conf_plan.md` before running anything.

---

## 1. Your role and the people

You are the execution agent. A separate chat session, the oversight chat, reviews your reports, makes scope decisions and writes decision memos, which Nicolas hands to you in full. Nicolas Weiyang Zhang (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`) is the first-year biostatistics PhD student whose project this is. He reads every command before it runs and will ask why. His advisors are Dr. Hongtu Zhu and Dr. Daiwei (David) Zhang at UNC. The target is a submittable paper by spring 2027.

Your responsibilities are to run the planned analyses on UNC Longleaf through Slurm, verify every stage's output against an expected value before moving on, write stage reports in the format of section 8, commit and push on your branch, and stop at each gate. You do not make scope decisions. Anything this document does not cover is reported as a proposal, not done.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

This track's gates are W2 and W5.

**How Nicolas wants things written.** Plain, natural prose. No em-dashes. No colon-then-explanation constructions. No compressed or clever phrasing. Math as LaTeX, with each `$$` on a line of its own. Numbers quoted at the precision the comparison needs, with the relative scale stated. Full precision stays in the files. Every number in a report is read back from the file named beside it. A derivation shows every expression and skips only algebra, and says where a step of algebra is skipped. Do not inflate length.

---

## 2. The project, and what this track is for

### 2.1 In one page

Spatial transcriptomics measures gene expression at known spots on a tissue section. A frozen pathology foundation model maps each spot's H&E patch to an embedding, and a linear head predicts $y = \log(1 + \text{count})$ per gene. Spots are nested in slides and slides in donors. The second data set is ACS PUMS 2018 income, with people nested in states or in California PUMAs. In the paper's language a donor or a state is a cluster, or group, and a spot or a person is a unit.

The paper is "Labelling budgets for prediction-powered inference with clustered data". Its prediction-set section asks what a labelling budget buys for a prediction set for a unit of a cluster the model never saw. Two numbers describe a design. $K$ is the number of calibration clusters, and $o$ is the number of labelled units in the test cluster itself.

Round 4 ran this track once and closed it on 2 October. Its results are these, each with its file.

1. **The valid method with no labelled test units is hierarchical conformal prediction (HCP).** It is finite only when $K + 1 \ge 1/\alpha$, and its width premium over the naive pooled interval falls with $K$. On kidney cancer it covers 0.97 at 1.95 times the pooled width with 10 calibration donors and 0.94 at 1.36 times with 20, while the pooled interval covers 0.86 to 0.87 (`results/round4/conformal/C3_real/c3_report_numbers.csv`).
2. **Generalized hierarchical conformal prediction (GHCP) is reproduced.** The released code reproduces the paper's simulation tables at 254 of 254 values and its census tables at 53 of 53 (`results/round4/conformal/C1_testbed/c1_ghcp_reproduction.csv`, `results/round4/conformal/C3_real/frag_ACS_o/acs_ghcp_reproduction.csv`).
3. **With 10 calibration donors a few labelled units do not help.** On kidney cancer HCP's mean width is 4.11. GHCP's is 5.46 at $o = 5$ and 5.06 at $o = 10$, covering above 0.99. A plain split inside the test donor is finite from $o = 9$, and at $o = 10$ its width is 2.32 with coverage 0.91 (`results/round4/conformal/C3_real/c3_o_sweep_by_task.csv`).
4. **A lower bound for very few clusters.** When $K + 1 < 1/\alpha$ every valid method returns an infinite set with probability at least $1 - \alpha(K + 1)$, and a valid method that is always finite must cover at least $1 - \beta^\star(K, \alpha)$, which at 90% is 0.951, 0.923, 0.910, 0.903 and 0.901 for 4 to 8 clusters (`docs/round04/i01/conformal/round4_conf_lower_bound.md`, `results/round4/conformal/C2_candidates/lower_bound/c2_lb_beta_star.csv`).
5. **Four candidate methods with no labelled test units were tried against a criterion fixed in advance, and none met it.** They are closed.

The closing page of `docs/round04/i02/conformal/round4_conf_final_report.md`, "What the conformal track established", is the summary.

Four things were left open, and this track exists for them.

- **The simulation map has a hole where the methods cross.** Its grid of labelled units was 0, 5, 10, 25, 50 and 100, and the plain split was added only on real data, after the simulation had run. So the region from 1 to 24 labelled units is unmapped in simulation.
- **GHCP's own setting has not been set beside ours.** In the GHCP paper's fixed design of 20 groups, GHCP's width is 27.5 at $o = 5$ and 13.6 at $o = 20$ against 33.5 for HCP, which is 18% and 60% narrower (`c1_ghcp_reproduction.csv`, table T2). On its census task GHCP's width is 316 thousand dollars at $o = 5$ against 531 thousand for HCP (`acs_ghcp_reproduction.csv`). In our own simulation with 20 clusters GHCP's price of validity is 1.09 at $o = 5$ against 1.16 for HCP (`results/round4/conformal/C1_testbed/c1_grid.csv`, normal tails, share 0.3, 500 units per cluster). So GHCP has a real niche at about 20 groups with a few labelled units, which our results at 10 donors do not show. The same reproduction holds a row the paper's simulation tables do not print. The released code's within-group baseline, Std-CP, has a width of 5.3 at $o = 20$ in that design against GHCP's 13.6, and is infinite in 648, 416 and 96 of 1,000 replicates at $o = 5$, 10 and 15 (`results/round4/conformal/C1_testbed/ghcp_repro_longleaf/compare/ours_fixedN21_summary_by_alpha_o_method.csv`).
- **Real data above 10 calibration donors have one follow-up run.** At $o = 25$ on kidney cancer GHCP's width falls from 4.43 with 10 calibration donors to 2.24 with 20, and the plain split's rises from 2.30 to 2.47, so the two cross near 18 (`results/round4/conformal/C3_real/frag_CCRCC_K/ghcp_o25/c3_by_fold_ghcp_o25__CCRCC.csv`). But the head is trained on 13 donors at one end of that sweep and on 3 at the other, so the sweep changes two things at once.
- **Two theory questions.** Whether the two propositions of result 4 are already in print, and whether HCP can be beaten when $K + 1 \ge 1/\alpha$. The round-4 closing memo recorded the second as open and not to be pursued. Nicolas has since asked for both, and this document replaces that line.

**What the advisors have seen.** Dr. Zhu and Dr. Zhang have seen the project up to the pivot and the originality check. They have not yet seen the round-4 results. Nothing in this round is a response to their feedback.

### 2.2 What this track is for, and what is and is not new

Four jobs.

1. **Complete the map in simulation** (W1), with the plain split, a full conformal set inside the test cluster, a fine grid of labelled units and more values of $K$.
2. **Run GHCP's own settings with the comparators its paper does not show, and with the number of groups varied** (W2).
3. **Run the real data above 10 calibration donors with labelled units** (W3), with a sweep in which only $K$ changes.
4. **Work on the two theory questions under a cap** (W4).

The output is a map that says, for each $(K, o)$, which method with a finite-sample guarantee is narrowest, in simulation, in the GHCP paper's settings and on real data. It includes the cells where that method is GHCP.

On originality and on tone. None of the methods here is new. The plain split is split conformal prediction inside one group, and the full conformal set is the textbook construction. GHCP is the reference method for labelled test units. This track uses it, cites it and does not compete with it. Report numbers and say what was run. Do not write anything that reads as criticism of the GHCP paper, and do not claim novelty for anything. Whether to tell its authors about anything found here is a decision for Nicolas with his advisors.

### 2.3 The methods, stated once

**Split conformal.** Scores $s_1, \dots, s_n$ on a calibration set. The set for a new unit is $\{y : s(y) \le \hat q\}$ with $\hat q$ the $\lceil (n + 1)(1 - \alpha) \rceil$-th smallest calibration score. If the $n + 1$ scores are exchangeable and distinct, coverage is exactly $\lceil (n + 1)(1 - \alpha) \rceil / (n + 1)$ on average, which is at least $1 - \alpha$. A finite $\hat q$ exists only if $n \ge (1 - \alpha)/\alpha$, which is $n \ge 9$ at 90%. The score here is the absolute residual $|y - \hat y|$.

**Hierarchical exchangeability.** Clusters are exchangeable with each other and units are exchangeable within a cluster. The question is coverage for a unit of a new cluster.

**HCP** (Lee, Barber and Willett, arXiv:2306.06342). Each of the $K$ calibration clusters gets total mass $1/(K + 1)$ spread equally over its units, and the test cluster's $1/(K + 1)$ is an atom at $+\infty$. The threshold is the $(1 - \alpha)$ quantile of that distribution. It is valid for any $K$ and finite only when $1/(K + 1) \le \alpha$. It ignores labelled test units, so it is available at every $o$.

**GHCP** (Mallick, Tchetgen Tchetgen, Dobriban and Lee, arXiv:2608.15500). With $o$ observations from the test group, the test group is assigned a size donated at random by a reference group with more than $o$ observations, part of the $o$ observations recentres the score, and the rest calibrate. The primary form here, `ghcp`, has $\eta = 0$ and adaptation on. `ghcp_noad` has adaptation off. Two conventions from round 4 stand. This track's tie convention is the standard one, under which the threshold is the $\lceil (n + 1)(1 - \alpha) \rceil$-th smallest score, and the released code's finiteness is reported beside it. And the paper's pool rule, its equation (8), is primary, with the released code's rule, one group larger, as a secondary variant.

**Inside the test cluster.** Three methods use only the $o$ labelled units, so they do not depend on $K$.

- `within_plain` is split conformal on the $o$ absolute residuals, uncentred. It is finite from $o = 9$ at 90%.
- `within` recentres on the first $\lfloor o/2 \rfloor$ residuals and calibrates on the rest. This is the GHCP paper's Std-CP with the absolute score. It is finite from $o = 17$ at 90%.
- `within_full` is added in this round. It is full conformal prediction with the mean as the fitted model. For a candidate residual $r$ of the test unit, let $c(r)$ be the mean of the $o$ labelled residuals and $r$, let $s_i(r) = |r_i - c(r)|$ and $s(r) = |r - c(r)|$, and keep $r$ when $1 + \#\{i : s_i(r) \ge s(r)\} > \alpha\,(o + 1)$. The oversight chat's working is that each condition $s_i(r) \ge s(r)$ holds on a closed interval with end points $r_i$ and $(2S - (o + 1)\,r_i)/(o - 1)$, where $S$ is the sum of the labelled residuals, so the set is found exactly from $2o$ end points, that it is finite from $o = 9$ at 90%, and that its coverage is $\lceil (o + 1)(1 - \alpha) \rceil/(o + 1)$, the same as the plain split's. A brute-force check of the end points on random draws found no mismatch. Check all three before you use them. Report the length of the set's convex hull, and record whenever the set is not an interval.

**No guarantee.** The pooled quantile of all calibration units, and `recentred`, which shifts the pooled interval by the labelled units' mean residual. They are reported as what a practitioner would try and are never called valid.

**The oracle and the price of validity.** In simulation the half-width $q^\star$ at which a new cluster's unit is covered with probability exactly $1 - \alpha$ is computable, and a method's price of validity is its mean threshold over $q^\star$. Simulation tables carry half-widths and real-data tables carry full widths.

**A valid method, in this document,** is one of `hcp`, `ghcp`, `ghcp_noad`, `within_plain`, `within` and `within_full`. The narrowest valid method in a cell is the one with the smallest mean width among those that are finite in every replicate or draw of that cell.

### 2.4 References

Mallick, Tchetgen Tchetgen, Dobriban and Lee, arXiv:2608.15500. Lee, Barber and Willett, arXiv:2306.06342. Dunn, Wasserman and Ramdas, JASA 2023, arXiv:1809.07441. Tibshirani, Barber and Ramdas, "Conformal Prediction Through the Lens of Hypothesis Testing: Universality, Impossibility, and Optimality", arXiv:2608.27310. Vovk, Gammerman and Shafer, *Algorithmic Learning in a Random World*, 2005. Lei, G'Sell, Rinaldo, Tibshirani and Wasserman, JASA 2018. Barber, Candès, Ramdas and Tibshirani, "The limits of distribution-free conditional predictive inference", Information and Inference 2021. Lei and Wasserman, JRSS B 2014. Vovk, "Conditional validity of inductive conformal predictors", 2012. Angelopoulos, Barber and Bates, "Theoretical Foundations of Conformal Prediction". Dobriban and Yu 2025 and Duchi and colleagues 2025, as the GHCP paper cites them. Several of these are named from the oversight chat's knowledge of the field and not from a search, so confirm that each is the right paper before you rely on it.

---

## 3. The repository, the data and the assets you build on

**Repository** at the starting commit. Everything under `results/round3/` and `results/round4/` is read-only for you, and so is every round-3 and round-4 script and document. `docs/WAYS_OF_WORKING.md` is the accumulated procedure. Read it before your first job.

**Longleaf** project tree `/work/users/w/e/weiyang/hest_replication`. It is the data root that the harness's `ROOT` points to. In round 4 it stayed on `main` at tag `round4-data-v2` (`9d7277d`) and nobody checked out a branch there. Keep it so. Never compute on the login node. The project's Python environment is `/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest` (Python 3.11.16, numpy 2.4.6, pandas 2.3.3).

| asset | path | what it gives you |
|---|---|---|
| the simulation testbed | `code/scripts/round4_conf_sim.py`, md5 `76fda34ee622e299bbaa806e5c8da98a` | the generator, every round-4 method and the oracle behind one interface. `run_cell(cell, alphas, n_reps, o_grid, semi, methods, seed_tag)` runs one cell, and `register_fast(name, fn, uses_o)` adds a method without touching the module. Import it unmodified |
| the round-4 simulation grid | `results/round4/conformal/C1_testbed/c1_grid.csv` (31,320 rows) | $K \in \{5, 7, 9, 10, 12, 15, 20, 25, 50\}$, $o \in \{0, 5, 10, 25, 50, 100\}$, 5,000 replicates. It has no `within_plain` |
| the real-data module | `code/scripts/round4_conf_c3.py`, md5 `2d8418677cf8290eec89a14c315b92cd`, with `round4_conf_io.py` and `round4_conf_c3_merge.py` | `load_task`, `TaskData.specs(K, ...)`, `TaskData.fit(spec)`, `o0_rows`, `o_rows(fit, o_grid, label_draws, alphas, methods)`, `selftest`. Each round-4 unit's runner is under its `frag_<unit>/code/` |
| the real-data tables | `results/round4/conformal/C3_real/c3_o_sweep.csv.gz` (1,424,918 rows, md5 of the plain file `2c3ceaa42528a1e3ad2979dc1161e542`), `c3_o_sweep_by_task.csv`, `c3_K_sweep_by_task.csv`, `frag_CCRCC_K/ghcp_o25/` | the map at 10 calibration donors, the HCP sweep over $K$, and the one follow-up with labelled units above 10 |
| the released GHCP code | on Longleaf at `/work/users/w/e/weiyang/hest_code/ghcp_code`, repository `github.com/soham-penn/hierarchical_CP`, commit `d1a69f4a35b260b592d3ea39d7c7ad7133459cba` | used unmodified in round 4. Launchers are under its `code/marginal/` |
| the reproduction wrappers | `code/scripts/round4_conf_c1_ghcp_repro.py`, `round4_conf_c1_ghcp_compare.py`, `round4_conf_c1_codepath.py` | run a released launcher unmodified, compare with the paper, and check our implementation against the released functions |
| the reproduction record | `results/round4/conformal/C1_testbed/ghcp_repro_longleaf/` | the job ledger `repro_jobs_sacct.csv`, the environment's freeze file `setup/ghcp_venv_freeze.txt`, and the summaries under `compare/`. The reproduced outputs are on Longleaf under the same path's `final/` |
| census data, Longleaf only | `results/round4/ppi/Q0_setup/acs_pums2018/` under the project tree | the raw 2018 one-year person files `raw/2018/1-Year/psam_p??.csv` and the processed parquets |
| round 4's census reproduction | `results/round4/conformal/C3_real/frag_ACS_o/` | the paper's values in `acs_paper_reference.csv`, the comparison, and the logs under `ghcp_repro/` with the released commands |
| the lower bound | `docs/round04/i01/conformal/round4_conf_lower_bound.md`, `code/scripts/round4_conf_c2_lower_bound.py`, `results/round4/conformal/C2_candidates/lower_bound/` | both propositions with proofs, the switching rule and its counterexample, the repaired rule, and the steps that failed |
| the harness | `code/scripts/round3_a0_harness.py`, md5 `0ad7ae8efe554c1f285e5f384a9fb7f5` | imported unmodified by the real-data module |
| the numeric-claim gate | `code/scripts/sweep_table.py`, `code/scripts/verify_numeric_claims.py` | run before every handover |

**The tasks.** Kidney cancer with 24 donors (`CCRCC:24`, written `CCRCC` in the round-4 tables) and with donors `INT4` and `INT24` merged (`CCRCC:23_merged`, written `CCRCC_23merged`), because the two may be one donor. Indiana kidney (25 donor units). Lung (15 donors), where disease is not fixed and each fold of the 10-donor design trains on 4 donors. Three encoders, `hoptimus0`, `uni_v2` and `resnet50`. The 50-gene lists on the kidney tasks and the 343-gene panel on lung, as round 4.

**Known properties you inherit.**

- In the round-4 real-data tables the column `label_set` does not tell the two kidney cancer sets apart. Filter on `task`.
- GHCP's shrinkage constant `n_glob` is 13 in the simulation and the number of training donors in the real-data module, which changes with $K$.
- The transcription of the paper's simulation tables is not in the repository. It survives as the `paper` and `paper_se` columns of `c1_ghcp_reproduction.csv`.
- The paper's fixed design is 20 reference groups of 21 units each. Its second design has Poisson group sizes with mean 25. The repository does not record the generating model of either. Read it from the released launchers.
- The Longleaf reproduction ran under Python 3.11.16 with the released pins, and the release pins Python 3.13. Round 4 found that the two interpreters give different random streams, so values agree with the paper within Monte Carlo error and not digit for digit (`compare/c1_ghcp_python_version_check.csv`). The path of the environment built for it on Longleaf was not recorded.
- Round 4's census reproduction ran on Nicolas's Mac, on the released pipeline's own input file, which holds 378,817 California rows. That input does not exist on Longleaf.
- The census task of the released code uses California PUMAs with at least 21 people after its cohort filters, and draws 20 calibration PUMAs and one target per replicate. The commands are in `frag_ACS_o/ghcp_repro/suite_main.log`. They pass `--target_index 20`, which appears to set the number of calibration groups. Confirm that in the code before you vary it.
- Round 4's later simulation runs were local, so the Longleaf project tree may lack some round-4 result directories. The committed copies in your clone are the record. The Longleaf code clones of round 4 under `/work/users/w/e/weiyang/hest_code/` are behind `main`. Do not use or update them.
- `code/scripts/verify_numeric_claims.py` runs clean under the project environment's pandas. Under pandas 3 it raises a `TypeError` on cited files with empty cells. The oversight chat fixes that separately. Do not edit the checker.

---

## 4. Standing rules and conventions

- Silent failure is the main risk. Verify each stage's output against an expected value before moving on. Every rerun has one arm anchored to a prior result.
- Never assert a number you have not read back from a file. Cite the path.
- Read the whole grid before writing a headline. Before a summary sentence goes into a report, tabulate the quantity over every axis the experiment varied and check that the sentence holds in each cell it claims.
- When you explain a number, state the mechanism and name what in the files would contradict it, then check that.
- For each method, write out what it assumes and what guarantee it carries before it runs. Before a tolerance is set on a method's coverage, work out that method's own expected coverage. A within-cluster split on $n$ scores covers $\lceil (n + 1)(1 - \alpha) \rceil/(n + 1)$, not $1 - \alpha$.
- Write predictions down before running, and report them beside the outcomes.
- Longleaf is where work runs. Nothing runs on Nicolas's Mac unless he asks for that specific task in chat. Such a request is written into the plan as a numbered extension before the task runs, covers the work it names, and does not carry across a gate. A local run records the host, the library versions, the md5 of every script and input, and the command line in place of the Slurm fields.
- A job that has waited four hours is reported to Nicolas in chat with what it needs, and it keeps waiting. A pending job's time limit and memory may be reduced with `scontrol` to a sibling's measured values, and a pending job may be switched between `rc_htzhu_pi` and `rc_tengfei_pi`. It is not moved anywhere else.
- Every output directory gets `PROVENANCE.txt` (job id, partition actually used, node, date, the code clone's commit, command line, config hash with its config, `PYTHONHASHSEED`, md5 of every script that ran) and is stamped with `stamp_dir()` from the `longleaf-provenance` skill, written by the job on the node. Before reusing or rebuilding any output you did not create, run `whose()` on it. If the verdict is `sibling` or `unstamped`, ask the oversight chat.
- A job runs from its own output directory, never from inside the code clone. The clone goes on `PYTHONPATH`.
- The submission route replaces `--job-name`, so jobs are identified by Slurm id. Record the intended prefix `r5conf_` and the stage in `PROVENANCE.txt`.
- Explicit `pa.schema` on every parquet. Summaries before bulk tables. Seeds from `zlib.crc32`, never `hash()`.
- Memory and time from a sibling's `sacct`. Slurm time limits at about three times the expected runtime, never a blanket 16 h. The harness ceiling counts queue time, so set it from queue time plus runtime. Record the partition the job ran on.
- Put a time cap on anything that is not analysis, and stop at the cap.
- Commit messages through a file. Sub-agents run no git command. The lead is the only committer and checks every hand-back against its primary tables before commit. One writer per file. Fragments plus a merge step with collision reporting.
- A file too large for GitHub is committed compressed, with the md5 of the plain file recorded. The plain file stays at the same path in the Longleaf project tree.
- Do not edit `README.md`, `docs/README.md`, `docs/WAYS_OF_WORKING.md`, any round-3 or round-4 file, the released GHCP code, or anything in the other track's areas. Proposed edits go in the report.
- Run `code/scripts/sweep_table.py` over the README and `docs/round05/**/round5_conf_*.md` before every handover.
- After opening a pull request, confirm on GitHub that it exists, and put its number in the report.

**Fan-out.** Every stage below names its parallel units. Dispatch one sub-agent per unit with a written brief. The brief carries the sub-agent's own frame id, written in by you, and the sentence "Stamp every output directory with `stamp_dir()` from the `longleaf-provenance` skill under the frame id given in this brief. Before reusing or rebuilding any output you did not create, run `whose()` on it; if the verdict is `sibling` or `unstamped`, ask me rather than rebuilding." Compare the id in every returned stamp with the id you assigned before the fragment is merged. Each sub-agent writes its own fragment under its own directory. The lead merges, recomputes every pooled number from the merged tables into a `<stage>_report_numbers.csv`, and commits.

**Reading and outside code.** W4 needs the full texts of papers. Read them with your own literature tools on the machine you run on, and keep the reading log W4 describes. If the released GHCP code or its environment is missing on Longleaf, cloning that repository again at the recorded commit and rebuilding the environment from the committed freeze file are permitted, and are recorded as an escalation. No data are downloaded anywhere.

---

## 5. Two sessions on one repository

The inference track runs at the same time, on branch `round5-ppi`, writing under `results/round5/ppi/`, `code/scripts/round5_ppi_*.py` and `docs/round05/**/round5_ppi_*.md`. You never write there and it never writes in your areas. Its closing stage reads your `results/round5/conformal/W3_real/w3_map_by_task.csv` from `main`, which is why that file's columns are fixed below.

Your areas. Branch `round5-conformal`, from the starting commit, never rebased, never merged into `main` by you, and with nothing merged into it. Record the starting commit's hash in the plan. Scripts `code/scripts/round5_conf_*.py`. Results `results/round5/conformal/<STAGE>/`. Documents `docs/round05/tracks/conformal/round5_conf_plan.md`, `docs/round05/tracks/conformal/round5_conf_theory.md`, `docs/round05/i01/conformal/round5_conf_W2_report.md`, `docs/round05/i02/conformal/round5_conf_final_report.md`. Longleaf outputs under `results/round5/conformal/` in the project tree, stamped. Tags `round5-conf-W2`, `round5-conf-final`.

**Working copies.** Each session has its own working copy, locally and on Longleaf, and never checks out a branch in a copy another session uses. Locally, reuse the round-4 clone at `~/hest-1k/HEST-1k-replication-conformal`, which Nicolas has brought up to date with `main`. It was left on branch `round4-conformal`, and that branch stays as it is. Confirm the working tree is clean, fetch, and create `round5-conformal` from `origin/main` at the starting commit. If the tree is not clean or a `.git/index.lock` is present, tell Nicolas and wait. The other two clones under `~/hest-1k` belong to the other track and to the oversight chat. Do not run git in them. On Longleaf your code runs from a fresh clone at `/work/users/w/e/weiyang/hest_code/round5-conformal/`, which is updated only by fast-forward from your pushed branch, by the route round 4 used. Every job records that clone's HEAD and the md5 of each script it executed.

**Pull requests.** At each gate you commit, tag and push your branch, open a pull request into `main`, and stop. You never merge. Nicolas merges with a merge commit after the oversight chat accepts the report. Branches are never rebased, squashed, amended after a push or force-pushed. A rejected gate is fixed with new commits on the same open pull request.

---

## 6. The plan

Three stages of experiments, one of theory that runs beside them, and a closing stage. Gates at W2 and W5.

### W0. Setup and anchors (half a day, capped at one day)

1. Read this document, `docs/WAYS_OF_WORKING.md`, the closing page and sections 4 and 6 of `docs/round04/i02/conformal/round4_conf_final_report.md`, `docs/round04/i01/conformal/round4_conf_C2_report.md` sections 6 and 7, `docs/round04/i02/conformal/round4_conformal_C2_decisions.md`, `docs/round04/i03/conformal/round4_conformal_C4_decisions.md`, `docs/round04/i01/conformal/round4_conf_lower_bound.md` in full, and part A5 of `docs/round05/00_prep/deck2/deck2_new_results_explained.md`. Transcribe section 6 into `docs/round05/tracks/conformal/round5_conf_plan.md` with the predictions of section 7. List anything in this document that looks wrong in a numbered section of the plan and in the W2 report. Do not change it.
2. Create the branch in the reused local clone as section 5 says, and make the Longleaf clone. Confirm the three md5s of section 3 in the Longleaf clone. Read the project tree's HEAD with `git --no-optional-locks rev-parse HEAD` and record it. If it is not `9d7277d`, record that as an escalation and change nothing. Run `whose()` on `results/round4/`. Confirm that the released GHCP code is at its path and at commit `d1a69f4a`, and find or rebuild its environment.
3. **Anchors, all on Longleaf.**
   - `round4_conf_sim.py` unmodified, on the cells `normal|K10|N500|share0.3|tau0.0` and `normal|K20|N500|share0.3|tau0.0` with 5,000 replicates, reproduces the matching rows of `c1_grid.csv`. Those rows were computed on a laptop, so the tolerance is $10^{-4}$ on coverage, $10^{-6}$ relative on the price of validity, and identical infinite fractions. Report the largest difference in each column.
   - `selftest` of `round4_conf_c3.py` passes. For `CCRCC:24` with `uni_v2` at $K = 10$, the rows at $o = 0$ and at $o = 25$ reproduce `c3_o_sweep.csv.gz` with coverage difference 0.0 and width difference at most $3 \times 10^{-10}$, which is the cross-vendor floor round 4 measured.
   - `round4_conf_c1_codepath.py` reproduces the mismatch counts of `ghcp_repro_longleaf/setup/c1_codepath.csv`.

Nothing in W1 starts until all three pass.

### W1. The simulation map, completed (three days; no gate, reported with W2)

**Why.** The paper's map needs every valid method on one grid, and the round-4 grid cannot say where the plain split overtakes HCP, where GHCP overtakes the plain split, or what a properly centred within-cluster set does between 9 and 25 labelled units.

**Script.** `code/scripts/round5_conf_w1_sim.py`. It imports the round-4 module unmodified, registers `within_plain` and `within_full` through `register_fast`, builds its own cells, and calls `run_cell` with the seed tag round 4 used, so that every round-4 row is reproduced and every replicate is paired across methods and across $o$.

**The grid.** $K \in \{9, 10, 12, 14, 16, 18, 20, 25, 30, 50\}$. $o \in \{0, 3, 5, 9, 10, 12, 15, 17, 20, 25, 35, 50, 100\}$. Units per calibration cluster $N \in \{21, 100, 500\}$ and the unequal setting, where 21 is the GHCP paper's group size. Between-cluster share of score variance $\in \{0.1, 0.3, 0.5, 0.9\}$ at $\tau = 0$ and $\tau = 0.3$, plus the cell with no cluster effect. The share of 0.9 is added because the GHCP paper's design has cluster effects that large, as its HCP width of 33.5 against 5.3 for the within-group baseline shows. Normal and $t_3$ tails, and the two semi-real cells. $\alpha \in \{0.1, 0.2\}$. 5,000 replicates. Methods are `pooled`, `hcp` and `one_per` at $o = 0$, and `ghcp`, `ghcp_noad`, `ghcp_r05`, `within`, `within_plain` and `within_full` at every $o$ they are defined for. Fan out by $K$, ten units, and split a $K$ into several jobs by cell where a sibling's runtime says so.

**Acceptance.**

1. Every (cell, method, $o$) already in `c1_grid.csv` at $K \in \{9, 10, 12, 20, 25, 50\}$ is reproduced at the W0 tolerances.
2. `within_plain` is infinite in every replicate for $o < 9$ at $\alpha = 0.1$ and for $o < 4$ at $\alpha = 0.2$, and finite in every replicate otherwise. `within` is infinite for $o < 17$ at $\alpha = 0.1$.
3. Wherever `within_plain` is finite its coverage is within three Monte Carlo standard errors of $\lceil (o + 1)(1 - \alpha) \rceil/(o + 1)$, which at $\alpha = 0.1$ is 0.900, 0.909, 0.923, 0.938, 0.944, 0.905, 0.923, 0.917, 0.902 and 0.901 at $o = 9$, 10, 12, 15, 17, 20, 25, 35, 50 and 100. The same holds for `within` with $n = o - \lfloor o/2 \rfloor$ in place of $o$.
4. `within_full` is finite in every replicate from $o = 9$ at $\alpha = 0.1$ and from $o = 4$ at $\alpha = 0.2$, and infinite below. Its coverage is within three Monte Carlo standard errors of the same expected value as `within_plain`'s.

**Predictions.** Unless a cell is named, they are read at normal tails, $\tau = 0$, 500 units per cluster and $\alpha = 0.1$.

1. W1.1. At $K \le 10$ GHCP is the narrowest valid method in no cell at any $o$.
2. W1.2. At $K \ge 20$ and share at least 0.3, GHCP is the narrowest valid method at $o = 3$ and $o = 5$, with a price 3 to 10% below HCP's.
3. W1.3. At $o \in \{9, 10, 12\}$ and share 0.3, `within_plain` is narrower than GHCP for $K \le 15$ and wider for $K \ge 25$, and `within_full` is narrower than GHCP at every $K$ up to 50.
4. W1.4. `within_full` is narrower than `within` at every $o$ from 20 to 50, by 5 to 18%, and wider at $o = 17$, where `within` calibrates on 9 scores. From $o = 9$ the narrowest valid method is `within_full` at every $K$ and every share of 0.3 or more. So in this generator GHCP's cells are those below 9 labelled units.
5. W1.5. At share 0.9 and $K = 20$, GHCP at $o = 5$ is at least 15% narrower than HCP, and `within_full` from $o = 9$ is at least 40% narrower than GHCP.

**Outputs.** `results/round5/conformal/W1_sim/w1_grid.csv` (one row per cell, method and $o$, with the columns of `c1_grid.csv`), `w1_narrowest_valid.csv` (one row per cell and $o$ with the narrowest valid method, its price, the runner-up, the margin and whether the margin exceeds two Monte Carlo standard errors), `w1_acceptance.csv`, `w1_report_numbers.csv`, `fig_w1_map.png`.

### W2. GHCP's own settings, with the missing comparators (three days; gate)

**Why.** The paper should show that at 20 groups our numbers agree with the GHCP paper's, and say what the map looks like in that paper's own designs once the within-group methods are on it and the number of groups is varied.

**Part 1, the paper's simulation designs.** Run the released launchers for the fixed design and for the Poisson design, unmodified, through `round4_conf_c1_ghcp_repro.py`, at $\alpha \in \{0.1, 0.2\}$ and $o \in \{0, 2, 5, 8, 9, 10, 12, 15, 17, 20\}$, with the released Std-CP kept on. Add `within_plain` and `within_full`, and this track's own `hcp` and `ghcp`, through a wrapper `code/scripts/round5_conf_w2_wrapper.py` that draws the same replicates from the released generator with the launcher's seeds. The released code is not edited. Then vary the number of reference groups over $\{10, 12, 15, 20, 30, 50\}$ in the fixed design, through the launcher's own argument if it has one and through the wrapper if it does not. 1,000 replicates per setting, as the paper.

**Part 2, the paper's census task.** Build the released pipeline's input on Longleaf from the raw person files under `raw/2018/1-Year/` with the released code's own processing under its `real_data/acs/`, as round 4 did on the Mac. Record its md5 and its row count, which should be 378,817, and run the released census experiment with the round-4 commands. Then add the two within-group methods through the wrapper, extend $o$ to the grid of part 1, and vary the number of calibration PUMAs over $\{10, 15, 20, 30, 50\}$.

Fan out by design and by number of groups. Size each job from `repro_jobs_sacct.csv`, where one chunk of the fixed design took one to three and a half hours on one core.

**Acceptance.**

1. Run the launchers first with the paper's own values of $o$, which are 0, 5, 10, 15 and 20. Their output equals the `ours` column of `c1_ghcp_reproduction.csv` for tables T2 and T3 to $10^{-9}$, since both ran on Longleaf under one environment. Only then run the extended grid. If the environment had to be rebuilt and the values differ, the test is the agreement rule of `round4_conf_c1_ghcp_compare.py` against the `paper` column, and the difference is an escalation.
2. On every replicate, the wrapper's HCP and GHCP coverage indicators equal the launcher's, and their widths agree to $10^{-9}$. The wrapper is not used until this passes.
3. The census run on Longleaf agrees with `acs_paper_reference.csv` under the same agreement rule at 53 of 53 values. Digit-for-digit agreement with round 4's local run is not expected, because that run used Python 3.13.
4. `within_plain` and `within_full` meet W1's acceptance checks 2 to 4 in these designs.

**Predictions.** In the fixed design at 20 groups and $\alpha = 0.1$ unless another setting is named.

1. W2.1. `within_full` is finite in every replicate from $o = 9$, and at $o \in \{10, 15, 20\}$ it is at least 40% narrower than GHCP, whose widths there are 21.2, 17.5 and 13.6.
2. W2.2. `within_plain` is within 25% of GHCP's width at $o = 10$ and wider than GHCP at $o = 20$, because it does not centre and the cluster effects in this design are large.
3. W2.3. At $o = 5$ and $o = 8$ GHCP is the narrowest valid method, and at $o = 5$ it is 10 to 25% narrower than HCP.
4. W2.4. At $o = 5$, GHCP is wider than HCP with 10 groups, and its width is 0.75 to 0.92 of HCP's with 20 or more.
5. W2.5. On the census task with 20 calibration PUMAs, GHCP remains the narrowest valid method at every $o \le 20$, so the paper's own finding stands with the comparators added. With 10 it is wider than HCP at $o \le 10$.

**Outputs.** `results/round5/conformal/W2_ghcp_settings/w2_sim_designs.csv`, `w2_census.csv`, `w2_narrowest_valid.csv`, `w2_wrapper_check.csv`, `w2_acceptance.csv`, `w2_report_numbers.csv`, `fig_w2_fixed_design.png`, `fig_w2_census.png`. Report W1 and W2 together as `docs/round05/i01/conformal/round5_conf_W2_report.md`, with the state of the W4 document, tag `round5-conf-W2`, and stop.

### W3. Real data above 10 calibration donors (four days; no gate, reported at W5)

**Why.** Every real study the paper speaks to has more than 9 clusters, and round 4 mapped labelled units only at 10.

**Script.** `code/scripts/round5_conf_w3.py`, which imports `round4_conf_c3.py` unmodified and adds `within_full`. The labelled units at each $o$ are the first $o$ of the round-4 label stream, so every round-4 row is reproduced.

**Part 1, the fine grid at 10 calibration donors.** $o \in \{3, 5, 9, 10, 12, 15, 17, 20, 25, 50, 100\}$ on both kidney cancer sets, Indiana and lung, with `ghcp`, `ghcp_noad`, `within`, `within_plain`, `within_full` and `recentred`, and `pooled`, `hcp` and `one_per` at $o = 0$.

**Part 2, the sweep over $K$ with labelled units.** $K \in \{10, 12, 14, 16, 18, 20\}$ on both kidney cancer sets and $K \in \{10, 14, 18, 20\}$ on Indiana, each at $o \in \{0, 5, 10, 15, 17, 25, 50\}$ with the methods of part 1. The number of training donors falls as $K$ rises, from 13 to 3 on kidney cancer with 24 donors, from 12 to 2 on the merged set and from 14 to 4 on Indiana, and is written on every row. Comparisons between methods are made within a $K$.

**Part 3, the sweep in which only $K$ changes.** On kidney cancer with 24 donors and on Indiana, fix the head at the training donors of the $K = 20$ design, and calibrate on the first $K$ donors of that design's calibration permutation for each $K$ of part 2. The calibration sets are nested and the head is the same at every $K$. This is the sweep to read across $K$.

Lung has 15 donors and stays at $K = 10$. The census task is covered by W2, since its state design cannot go above 10 calibration clusters with a guarantee.

Fan out by task and part, eight units.

**The output format is fixed**, because the inference track reads it. `results/round5/conformal/W3_real/w3_map_by_task.csv` has columns task, part, alpha, K, n_T_donors, o, method, valid, coverage, coverage_sd_folds, width_mean, finite, narrowest_valid. Coverage and width are means over encoders of the mean over folds of the per-fold mean over draws, as round 4. `valid` says whether the method carries a guarantee, and `narrowest_valid` marks one method per task, part, alpha, K and $o$.

**Acceptance.**

1. Every row of part 1 and part 2 that exists in `c3_o_sweep.csv.gz`, in the round-4 $K$ sweep or in `frag_CCRCC_K/ghcp_o25/` is reproduced with coverage difference 0.0 and width difference at most $3 \times 10^{-10}$.
2. `within_plain` and `within` cover within 0.005 of their expected values of W1's acceptance check 3 on every task. Round 4's rows were within 0.002.
3. `within_full` covers within 0.005 of the same expected value as `within_plain` on every task.

**Predictions.** At $\alpha = 0.1$.

1. W3.1. At $K = 10$ on every task, GHCP is wider than HCP at $o = 3$ and $o = 5$ by a factor of 1.2 to 1.5, and from $o = 9$ the narrowest valid method is `within_full`, at 0.45 to 0.65 of HCP's width for $o$ from 9 to 15.
2. W3.2. `within_full` is 5 to 15% narrower than `within_plain` at every $o$ from 9, and 5 to 12% narrower than `within` from $o = 20$. The first margin is small because on these tasks a donor's offset is well under one standard deviation of its residuals.
3. W3.3. On kidney cancer at $o = 5$, GHCP's width is within 8% of HCP's at every $K$ from 12 to 20, so on these data GHCP has no cell below 9 labelled units where it is narrower by a margin that matters.
4. W3.4. In part 3 the within-cluster methods do not change with $K$ and GHCP's width falls with $K$. At $o$ from 9 to 25 GHCP is not the narrowest valid method by more than 5% at any $K$ up to 20.
5. W3.5. Indiana repeats kidney cancer's pattern in parts 2 and 3.

**Outputs.** `results/round5/conformal/W3_real/w3_o_sweep.csv.gz` and `w3_K_sweep.csv.gz` with the fifteen columns of round 4's `c3_o_sweep.csv` and `n_T_donors`, `w3_fixed_head.csv.gz`, `w3_map_by_task.csv`, `w3_by_fold.csv`, `w3_acceptance.csv`, `w3_report_numbers.csv`, `fig_w3_map.png`, `fig_w3_fixed_head.png`.

### W4. Two theory questions (five working days in total, capped; run by the lead beside W1 to W3)

Write `docs/round05/tracks/conformal/round5_conf_theory.md` as you go, with each step marked derived, conjectured or failed. `docs/round04/i01/conformal/round4_conf_lower_bound.md` is a record and is not edited. Keep a reading log at the head of the new document, one row per paper, with its identifier, whether the full text, the abstract only or nothing could be opened, the sections read and the date. A paper whose full text was not opened is not cited for anything beyond its abstract.

**Part A, whether the two propositions are in print (at most one and a half days).** Proposition 1 is the coverage floor $1 - \beta^\star(K, \alpha)$ for a valid method that is finite almost surely when $K + 1 < 1/\alpha$. Proposition 2 is that every valid method returns an infinite set with probability at least $1 - \alpha(K + 1)$. The degenerate hierarchical model, in which every group's law is a point mass, is ordinary exchangeable data with $n = K$, so a statement for ordinary data with $n + 1 < 1/\alpha$ transfers. Read Tibshirani, Barber and Ramdas in full first, then Vovk, Gammerman and Shafer on universality, Angelopoulos, Barber and Bates, Lei and Wasserman, Barber, Candès, Ramdas and Tibshirani, Vovk on conditional validity, Lee, Barber and Willett, the GHCP paper, and Dunn, Wasserman and Ramdas. For each proposition the outcome is one of three statements. It is in print, with the paper, the theorem number and the statement transcribed. Or it is a direct corollary of a named result, with the few lines written out. Or it was not found after the search the log records.

**Part B, whether HCP can be beaten when $K + 1 \ge 1/\alpha$ (at most three and a half days).** Unused time from part A may be spent here. The order of work is this.

1. Transcribe the optimality theorem of Tibshirani, Barber and Ramdas with its number, and say which sense of optimal it uses. Then write down three senses of "beaten" for grouped data. A method is dominated if another valid method is no wider in expectation under every law and narrower under some. It is beaten at a law if another valid method is narrower in expectation under that law. It is beaten in the minimax sense over a named class of laws. Say which of these the ordinary-data theorem answers.
2. Take randomised HCP as the baseline. Deterministic HCP is beaten by its own randomisation whenever the threshold's level is rounded up, and that is not the question.
3. Work first in the model of the round-4 document in which each group's law is seen exactly. The data are then $K$ laws drawn from $\Pi$, and the test unit is one draw from a further law that is not seen. Ask whether the universality argument lifts, that is, whether every valid method must satisfy the permutation form of validity of the round-4 document's section 2 and nothing more, and whether HCP is a conformal method for some score on that model.
4. Settle what is already known from round 4. The repaired switching rule is valid, is narrower than HCP when the groups look alike and is wider otherwise, so HCP is beaten at the homogeneous law and that rule does not dominate it. State this as a result with its conditions, including the loss at finite group sizes that section 8.4 of the round-4 document found.
5. Then attempt the question of dominance. Either construct a valid method that is never wider than randomised HCP and narrower somewhere, or show that none exists, or record the steps that failed.

Small numerical probes are allowed, as scripts `code/scripts/round5_conf_w4_*.py` with outputs under `results/round5/conformal/W4_theory/`. No method from this stage is run on the simulation grid or on real data. The four candidates of round 4 are closed and are not reopened.

**Stop rule.** At each cap write the document as a record of what exists and stop. The oversight chat decides at the gates whether anything is pursued.

**Predictions.**

1. W4.1. Proposition 2 is a direct corollary of a named universality or impossibility result for ordinary data, and is not found stated for groups.
2. W4.2. Proposition 1's floor is not found.
3. W4.3. Part B ends with the statement of step 4 written as a result and with dominance unresolved.

### W5. The closing report (two days; gate, end of track)

`results/round5/conformal/W5_map/w5_map.csv`, the map as one table, with source (simulation, the GHCP paper's designs, real data), the setting, $K$, $o$, the narrowest valid method, its width or price, the runner-up and the margin. One figure per source.

`docs/round05/i02/conformal/round5_conf_final_report.md` in the format of section 8, covering W1 to W4, the full predictions-against-outcomes table, an "Escalations" section, a section listing every statement of the round-4 closing page and of `docs/round04/i03/conformal/round4_conformal_C4_decisions.md` that this round changes with the old and new values, and a closing page titled "What the round-5 prediction-set track established", at most one page, every sentence naming its file. The closing page ends with one paragraph on what the paper's prediction-set section should say about GHCP, in numbers. Run the numeric-claim sweep. Tag `round5-conf-final`. Then stop.

**Time.** About fourteen working days with the gates, the theory stage running beside the others.

---

## 7. Predictions for the track, consolidated

The stage predictions above, numbered W1.1 to W1.5, W2.1 to W2.5, W3.1 to W3.5 and W4.1 to W4.3, are the track's predictions. Copy them into `docs/round05/tracks/conformal/round5_conf_plan.md` before running and score each in the report of its gate as held, partly held, refuted or not tested. They are the oversight chat's. In round 4 most of its magnitude predictions were refuted and one was wrong in direction, so a refuted prediction is an ordinary outcome and is reported as plainly as a held one.

---

## 8. Reporting format

After each gate, in this order. 1. Stage and status. 2. What was run (scripts with md5s, commits, job ids, partitions, wall times, peak memory from `sacct`). 3. Acceptance checks with the actual numbers and file paths. 4. For every method, its assumptions and guarantee as written before it ran, and for every comparison the list of variables that differ between its arms. 5. Predictions against outcomes, as a table. 6. Results, numbers from files with paths, dispersion beside every mean, and paths in place of pasted tables over 20 rows. 7. Discrepancies, open questions and escalations. 8. What was not checked. 9. Proposed next step.

Keep prose plain, as section 1 asks.

---

## 9. Decision boundaries

**You decide alone.** Sub-agent structure. Seeds for anything round 4 did not seed. Replicate counts above the stated ones. Job sizing. How the wrapper reaches the released generator, provided acceptance check 2 of W2 passes. Implementation details of `within_full` that its definition leaves open, provided the docstring records the choice before the run.

**Record as an escalation and continue.** The project tree not being at `9d7277d`. The released GHCP code or its environment having to be rebuilt. The share of 0.9 not being reachable by the round-4 solver (use the largest share it reaches, say so). A launcher that cannot vary the number of groups (use the wrapper). A $K$ that leaves a task fewer than 2 training donors (skip it, say so). The census input not being buildable on Longleaf (finish part 1 of W2, report what blocked part 2, and do not run it locally). Any acceptance check failing at a tolerance the dtype supports (fix, rerun, say so). The oversight chat's working on `within_full` being wrong (correct it in the docstring and the plan, say so). A paper whose full text cannot be opened. Any new property of the data. Any need to change a shared file.

**Stop and report.** Any W0 anchor failing. Acceptance check 1 of W1 failing, which would mean the testbed no longer reproduces round 4. Acceptance check 2 of W2 failing after one day of work on the wrapper.

**Never yours.** Spending more than the caps of W4. Running any W4 method on the grid or on data. Reopening the four candidates of round 4. Contact with anyone outside the project, the GHCP authors included. Edits to the released GHCP code. Changes to `main`, to round-3 or round-4 files, to the project tree's checkout, or to the other track's areas. Any download of data. Any local run that Nicolas has not asked for in chat. Any claim of novelty, and any sentence that reads as criticism of another paper.
