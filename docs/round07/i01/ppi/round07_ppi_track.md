# Round 7, the inference track on choosing the labelled clusters, instruction

*Frozen at the close of round 7, 15 October 2026.*

13 October 2026. Prepared by the oversight chat for a fresh Claude Science session. This document is self-contained. The track starts from `main` of `NicWYZ/HEST-1k-replication` at the commit that carries the first version of this document, on its own branch `round7-ppi`. Record that commit's hash in your plan. Read this document fully, then transcribe section 7 into `docs/round07/tracks/ppi/round07_ppi_plan.md` before running anything.

This instruction stays living on `main` while the track runs. The oversight chat revises it in place and adds a dated line below. When Nicolas tells you to check for updates, fetch `main`, read the revisions, and transcribe any change into your plan.

**Revisions**
- 13 October 2026. First version.
- 13 October 2026, before handover. Revised after an independent check. The k-center design has every $\pi_g > 0$ and most $\pi_{gh} = 0$, Kluger et al.'s design has a random sample size and needs its own variance, Broska and Howes's interval is computed with cluster counts and enters every design, the fixed thresholds of round 5 define D2, census has one balance variable, the second simulated balance variable is defined, and several predictions, outputs, fan-out units and time caps were corrected.

---

## 1. Your role and the people

You are the execution agent. A separate chat session, the oversight chat, reviews your reports, makes scope decisions and writes decision memos, which Nicolas hands to you or tells you to fetch from `main`. Nicolas Weiyang Zhang (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`) is the first-year biostatistics PhD student whose project this is. He reads every command before it runs and will ask why. His advisors are Dr. Hongtu Zhu and Dr. Daiwei (David) Zhang at UNC. The target is a submittable paper by spring 2027.

Your responsibilities are to derive and run the analyses below on UNC Longleaf through Slurm, verify every stage's output against an expected value before moving on, write gate reports in the format of section 9, commit on your branch, and stop at each gate. You do not make scope decisions. Anything this document does not cover is reported as a proposal, not done.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

This track's gates are S2, S4 and S5. The stop conditions of section 10 are the only exceptions to "no interim stop conditions", as they were in round 5, and a stop produces a report in the format of section 9.

**How Nicolas wants things written.** Plain, natural prose. No em-dashes. No colon-then-explanation constructions. No compressed or clever phrasing. Math as LaTeX, with each `$$` on a line of its own. Numbers quoted at the precision the comparison needs, with the relative scale stated. Full precision stays in the files. Every number in a report is read back from the file named beside it. A derivation shows every expression and skips only algebra, and says where a step of algebra is skipped. Do not inflate length.

A second session runs at the same time, round 7's federated learning track on branch `round7-fedlearn`. It writes only under `results/round7/fedlearn/`, `code/scripts/round7_fedlearn_*.py`, `docs/round07/**/round07_fedlearn_*.md` and `.verify-exceptions-round7-fedlearn`. Both tracks submit jobs to the same Slurm accounts, so the queue rules of section 4 apply to your own jobs only. You never write there and it never writes in your areas.

---

## 2. What this track is for

### 2.1 The paper, and why the question changed

The paper is "Labelling budgets for prediction-powered inference with clustered data", applied to HEST-1k spatial transcriptomics and ACS PUMS 2018 income. Round 5 defined its estimator (`docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`) and closed with one open question, weighting the labelled clusters by their inclusion probabilities under rejective selection (`docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, section 5).

Two documents of 13 October reframe that question. Read both before S0.
- `docs/round07/00_prep/round07_overlap_check.md`. Selection rules built for training or coverage, rather than for inference, are often deterministic given the slides already profiled, or depend on expression already measured. Neither gives the labelled clusters the known inclusion probabilities that design-based PPI needs. Weighting by inclusion probabilities under a randomised, histology-guided design is what lets such a design coexist with a valid interval.
- `docs/round07/oversight/round07_ppi_positioning.md`. After a full reading of the closest literature, the paper's own ground is the few-cluster, design-target regime and the design questions. Broska and Howes (arXiv:2610.09601) give the large-sample cluster-robust PPI++ interval and have no small-sample correction. Kluger et al. (arXiv:2501.18577) already weight whole clusters by known probabilities under independent Bernoulli selection, with a cluster bootstrap. Chen et al. ("Balanced Active Inference", NeurIPS 2025) balance a unit-level active design by the cube method.

Nicolas accepted the reframing on 13 October with the positioning note's three changes (its section 6). This track carries them out.

### 2.2 The questions

- **Q1. Weighting under rejective selection.** Under round 5's design D2, with inclusions that are dependent and unequal, do the Horvitz-Thompson and Hájek estimators with simulated inclusion probabilities remove the bias that the classical mean showed at small $n_L$ and with two balance variables, and does an interval built on them cover at 4 to 16 labelled clusters? Is a floor on the residual degrees of freedom still needed, and what does the weighting cost in width against `rej_t`?
- **Q2. The comparators from the literature.** How do Broska and Howes's cluster-robust interval and Kluger et al.'s cluster bootstrap behave at 4 to 16 labelled clusters, for the design target and for the superpopulation target, against the paper's intervals?
- **Q3. An adaptive, balanced design at the cluster level.** Clusters drawn with unequal probabilities that mix a label-free score with uniform probabilities, balanced by the cube method, with the Hájek estimator. Is it narrower than D2 with `rej_t`, and does it cover?
- **Q4. A deterministic rule.** What happens to the paper's interval when the labelled clusters are chosen by greedy k-center selection on the clusters' mean embeddings, and what can the weighting do there?

### 2.3 The methods, stated once

Notation is the estimator definition's. Cluster $g$ of $G$ contributes $\bar z_g$ to the estimand $\theta = \frac{1}{G}\sum_g \bar z_g$ and $\bar f_g$ to its prediction counterpart $\bar F = \frac{1}{G}\sum_g \bar f_g$. $L$ is the set of $n_L$ labelled clusters. In this track every unit of a labelled cluster is labelled (regime A), unless a stage says otherwise, so $\bar z_g$ is known exactly for $g \in L$.

**Inclusion probabilities.** For a design that draws $L$ at random, $\pi_g = P(g \in L)$ and $\pi_{gh} = P(g, h \in L)$. Under D2 they have no closed form. Estimate them by drawing $R$ accepted samples from the design with seeds disjoint from every evaluation draw,

$$
\hat\pi_g = \frac{1}{R}\sum_{r=1}^{R} \mathbf{1}\{g \in L_r\}, \qquad \hat\pi_{gh} = \frac{1}{R}\sum_{r=1}^{R} \mathbf{1}\{g, h \in L_r\},
$$

with $R$ chosen so that the expected count behind every $\hat\pi_{gh}$ is at least 100 where that is feasible, and at least 100,000 in any case, and record the Monte Carlo standard error of each. On the census tasks at small $n_L$ the pairwise counts stay small at any feasible $R$, so the theory document also derives an approximation to $\pi_{gh}$ for a high-entropy fixed-size design from the $\pi_g$ alone, and S1 compares it with the simulated values where both are available. D2 is the design with round 5's fixed thresholds (`results/round5/ppi/E4b_rejective/_threshold/`) and with further candidates drawn until one is accepted, as `code/scripts/round5_ppi_e4b_sim.py` does, never with the fallback to the last candidate of `d2_select`. Nothing in this computation uses a label.

**Estimators.**

$$
\hat\theta_{\mathrm{HT}} = \frac{1}{G}\sum_{g \in L}\frac{\bar z_g}{\pi_g}, \qquad \hat\theta_{\mathrm{H}} = \frac{\sum_{g \in L} \bar z_g/\pi_g}{\sum_{g \in L} 1/\pi_g},
$$

and the difference form with the predictions, with $\lambda$ cross-fitted over two halves of the labelled clusters as in rule `c_crossfit_design`,

$$
\hat\theta_{\mathrm{HT},\lambda} = \lambda\bar F + \frac{1}{G}\sum_{g \in L}\frac{\bar z_g - \lambda \bar f_g}{\pi_g}.
$$

Under simple random selection $\pi_g = n_L/G$, and $\hat\theta_{\mathrm{HT}}$ and $\hat\theta_{\mathrm{H}}$ both equal the classical mean of the labelled clusters.

**Variance.** The Sen-Yates-Grundy form for a fixed-size design,

$$
\widehat{\text{Var}}_{\mathrm{SYG}}(\hat\theta_{\mathrm{HT}}) = \frac{1}{2G^2}\sum_{g \ne h \in L}\frac{\pi_g\pi_h - \pi_{gh}}{\pi_{gh}}\left(\frac{\bar z_g}{\pi_g} - \frac{\bar z_h}{\pi_h}\right)^2,
$$

and for the Hájek estimator the same form applied to the residuals $\bar z_g - \hat\theta_{\mathrm{H}}$, scaled by $G^2/\hat N^2$ with $\hat N = \sum_{g \in L} 1/\pi_g$. It needs every $\pi_{gh} > 0$ for pairs in the sample. Derive in the theory document what happens when some $\hat\pi_{gh}$ is zero or rests on very few draws, and propose the interval's reference distribution with its degrees of freedom before any real-data run. Write the derivation of every interval you use into the theory document, including the cross-fitted difference form, and test it on a synthetic population before the real tasks.

**The paper's comparators.** `textbook_t|fpc|lin` for the classical mean, `textbook_t|fpc|lin|xf` for the tuned estimator and `rej_t` under D2, as round 5 defined them (`code/scripts/round5_ppi_balance.py`, `round5_ppi_estimator.py`).

**Broska and Howes's interval.** Their estimator is PPI++ with one global $\lambda$, and their appendix A allows cluster-level weights, so with weight $1/m_g$ on each unit each cluster counts once. In the formulas below, as they write them for unit weights, $\xi_{g,i}$ are the label indicators, $n$ and $N$ count labelled and unlabelled units, and $\hat\theta_f$ is the mean of the predictions over all units. With the weights, $n$ and $N$ become the numbers of labelled and unlabelled clusters and $\hat\theta_f$ the mean of the clusters' $\bar f_g$; left as unit counts, the standard error is off by the cluster size. They define

$$
\hat\varepsilon_g = \sum_i \xi_{g,i}\big(Y_{g,i} - \hat\theta^{PP}_\lambda\big), \qquad \hat Z_g = \sum_i \Big(\xi_{g,i} - \frac{n}{N}(1 - \xi_{g,i})\Big)\big(f(X_{g,i}) - \hat\theta_f\big),
$$

$$
\hat\Sigma = \frac{1}{G}\sum_{g=1}^{G}\begin{pmatrix}\hat\varepsilon_g^2 & \hat\varepsilon_g\hat Z_g \\ \hat Z_g\hat\varepsilon_g & \hat Z_g^2\end{pmatrix}, \qquad \hat\sigma^2_\lambda = \frac{G}{n}\Big(\hat\Sigma_{11} - 2\lambda\hat\Sigma_{12} + \lambda^2\hat\Sigma_{22}\Big),
$$

with $\hat\lambda = \hat\Sigma_{12}/\hat\Sigma_{22}$, where $\hat\Sigma$ is first computed with the estimate at $\lambda = 1$, and the interval $\hat\theta^{PP}_{\hat\lambda} \pm z_{1-\alpha/2}\,\hat\sigma_{\hat\lambda}/\sqrt n$ (their equations 6, 7, 9 and 12, and remark 1). Write its specialisation to the estimand's cluster contributions in the theory document, and check it in two ways before using it. On simulated i.i.d. data with every cluster of size one, its variance must equal the PPI++ variance of their example 1, $\text{Var}(Y - \lambda f) + \lambda^2 r\,\text{Var}(f)$ with $r = n/N$, computed directly from the same data, to $10^{-10}$. In a simulation where their assumptions hold and $G$ is large, it must cover within Monte Carlo error of nominal. With a constant predictor $\hat\Sigma_{22} = 0$, so set $\hat\lambda = 0$ there and record it. Their interval treats the unlabelled clusters' predictions as random and has no finite-population factor, so for the design target it should overstate the variance, by a factor that the theory document derives as a function of $n_L/G$ and the cluster-level $R^2$ before any run. Their implementation is at `github.com/Michael-Howes/ppi_py`. Fetching it is Nicolas's decision, so implement from the paper and propose the comparison with their code in a report if it would help. The paper's PDF is on the Mac at `~/hest-1k/ppi_conf_papers/cluster_ppi.pdf`.

**Kluger et al.'s cluster design.** Whole clusters are labelled by independent Bernoulli draws with known probabilities $\pi_k$, so the number of labelled clusters is random. Their estimator is predict-then-debias with weights $\xi_k/\pi_k$ on the labelled clusters and $(1 - \xi_k)/(1 - \pi_k)$ on the unlabelled ones and a tuned coefficient, and the interval is the percentile interval of a cluster bootstrap that resamples all clusters, labelled and unlabelled, with replacement (their algorithm 5, appendix B.1). Use 2,000 bootstrap draws. Under this design $\pi_{gh} = \pi_g\pi_h$, so the Sen-Yates-Grundy form is zero and does not apply. For the inverse-probability-weighted mean beside it, use the Poisson-design variance $\frac{1}{G^2}\sum_{g \in L}(1 - \pi_g)\bar z_g^2/\pi_g^2$ and its Hájek analogue, derived in the theory document. A draw that labels fewer than two clusters gets no interval. Record the share of such draws in every cell and report coverage over the remaining draws, as round 5 did for $\theta_2$. The PDF is `~/hest-1k/ppi_conf_papers/kluger.pdf`.

**Chen et al.'s design, at the cluster level.** With a label-free score $u_g \ge 0$ and $\tau = 0.5$, the target inclusion probabilities are

$$
\pi^{(\tau)}_g = \tau\,\frac{n_L\,u_g}{\sum_h u_h} + (1 - \tau)\,\frac{n_L}{G},
$$

capped at 1 with the excess redistributed, and the sample is drawn by the cube method (Deville and Tillé, Biometrika 2004). Its flight phase keeps $\sum_{g \in L} x_g/\pi_g = \sum_g x_g$ exactly for the balance variables $x_g$, which include $\pi_g$ itself so that the sample size is fixed, and its landing phase meets the balance only approximately. Because the realised design can differ from the targets, the $\pi_g$ and $\pi_{gh}$ used for estimation are simulated from the implemented sampler, as for D2. The PDF is `~/hest-1k/ppi_conf_papers/balanced_active_inference.pdf`. Their variance estimators are in a supplement that the project does not have, so derive the one you use.

**Greedy k-center.** Choose the first cluster uniformly at random, then repeatedly add the cluster farthest, in the space of the first 10 principal components of the clusters' mean embeddings, from its nearest labelled cluster, until $n_L$ clusters are chosen. The random first cluster makes this a design with at most $G$ distinct samples, each start having probability $1/G$. So every $\pi_g \ge 1/G > 0$ and $\hat\theta_{\mathrm{HT}}$ is exactly design-unbiased, but most $\pi_{gh}$ are zero, so no design-based variance estimate exists. Everything about this design, coverage included, is computed exactly by enumerating the $G$ starts. Without the random start the rule is deterministic and every $\pi_g$ is 0 or 1.

---

## 3. The repository, the data and the assets

**Repository** at the starting commit. Everything under `results/round3/` to `results/round6/` is read only for you, and so is every earlier script and document. `docs/WAYS_OF_WORKING.md` is the accumulated procedure. Read it before your first job.

**Longleaf** project tree `/work/users/w/e/weiyang/hest_replication`, on `main` at tag `round4-data-v2`. Read it with `git --no-optional-locks` and never check out, fetch or pull there. Never compute on the login node. The project's Python is `/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python`, called by absolute path in every job script.

| asset | path | what it gives you |
|---|---|---|
| the estimators | `code/scripts/round5_ppi_estimator.py` (md5 `2de31569ffe72239062fbeb0c9a50fc5`), `round5_ppi_twolevel.py` (`e13183a4ffdddf4f01ba5136844c606d`) | form C, rule `c_crossfit_design`, `textbook_t|fpc|lin|xf`. Import unmodified |
| the balance designs | `code/scripts/round5_ppi_balance.py` (`d78b654d7fd8e6a824f73dd50ee2a0c1`) | `mahalanobis_pool`, `d2_select`, `va_nominal`, `rej_t`, `perm_cluster_variable`. Import unmodified |
| the E4b run | `code/scripts/round5_ppi_e4b_rejective.py` (`059c18e1b4998b1ac9c9685ba324a872`), `round5_ppi_e4_selection.py` | how D2 cells, candidate pools, thresholds and the embedding principal components were built |
| shared helpers | `code/scripts/round5_ppi_common.py` (`122375c3acb103ed93e3e687644d7f6d`) | data loading and seeds |
| inclusion diagnostics | `code/scripts/round5_ppi_e4_inclusion.py`, `results/round5/ppi/E4b_rejective/e4b_d2_diagnostics.csv` | round 5's inclusion frequencies and their correlation with $\lvert\bar f_g - \bar F\rvert$ |
| the anchors | `results/round5/ppi/E4b_rejective/e4b_rej_width_ratios.csv`, `results/round5/ppi/E5_joint/e5_report_numbers.csv` | the rows S0 reproduces |
| prediction parquets and mean embeddings, Longleaf only | the paths in `docs/round05/i01/ppi/round5_ppi_track.md`, section 3, and the mean-embedding parquets under `results/round4/ppi/Q5_joint/` | per-unit outcome, prediction and donor for every task, and each donor's mean embedding |
| the numeric-claim gate | `code/scripts/verify_numeric_claims.py` | run before every handover |

**The tasks,** as in round 5. `CCRCC` (24 donors), `CCRCC_merged` (23, with `INT4` and `INT24` merged), `INDIANA_KIDNEY` (25 donor units), `LUNG_XENIUM` (15 donors), `ACS_STATES` (51 clusters) and `ACS_CA_PUMA` (265 clusters). Encoders `hoptimus0`, `uni_v2` and `resnet50` on the tissue tasks, the package predictor on census. Estimands $\theta_3$ and $\theta_2$, donor-weighted, design target, with the superpopulation target where a stage asks for it. The constant predictor is the primary control in every cell where a predictor enters an estimator ($\hat\theta_{\mathrm{HT},\lambda}$, the tuned estimator and Broska and Howes's), as round 5's E2 memo set, with the permuted predictor beside it. Census has one outcome, so on census `own` is the only balance variable for D2 ($k = 1$, and round 5's `pcF2` rows there equal the `own` rows), and the embedding-based score of S3 and the k-center design of S4 run on the tissue tasks only.

---

## 4. Standing rules and conventions

- Silent failure is the main risk. Verify each stage's output against an expected value before moving on. Every rerun has one arm anchored to a prior result.
- Never assert a number you have not read back from a file. Cite the path.
- Read the whole grid before writing a headline. Tabulate the quantity over every axis the experiment varied and check that the sentence holds in each cell it claims.
- When you explain a number, state the mechanism and name what in the files would contradict it, then check that.
- Before naming a term, list in writing every variable that differs between its arms.
- Write predictions down before running, and report them beside the outcomes. Do not quote a ratio whose denominator is within noise of zero.
- Longleaf is where work runs. Nothing runs on Nicolas's Mac unless he asks for that specific task in chat. Such a request is written into the plan as a numbered extension before the task runs, covers the work it names, and does not carry across a gate. A local run records the host, the library versions, the md5 of every script and input, and the command line in place of the Slurm fields. The numeric-claim sweep of your own documents before a handover is documentation work, done in your clone as every earlier track did.
- A job that has waited four hours is reported to Nicolas in chat with what it needs, and it keeps waiting. A pending job of this track's own may have its time limit and memory reduced with `scontrol` to a sibling's measured values, and may be switched between `rc_htzhu_pi` and `rc_tengfei_pi`. Only the lead cancels a Slurm job, and only after confirming with `squeue -u weiyang` and the track's job ledger, `results/round7/ppi/r7ppi_slurm_jobs.csv`, that the job is the track's own, since the federated learning track uses the same accounts. A sub-agent never runs `scancel`.
- Every output directory gets `PROVENANCE.txt` (job id, partition actually used, node, date, the commit of the snapshot the job ran from, command line, config hash with its config, `PYTHONHASHSEED`, md5 of every script that ran) and is stamped with `stamp_dir()` from the `longleaf-provenance` skill, written by the job on the node. Before reusing or rebuilding any output you did not create, run `whose()` on it, and if the verdict is `sibling` or `unstamped`, ask the oversight chat through the report.
- The submission route replaces `--job-name`, so jobs are identified by Slurm id. Record the intended prefix `r7ppi_` and the stage in `PROVENANCE.txt`.
- Give every parquet an explicit `pa.schema`, write summaries before bulk tables, and take seeds from `zlib.crc32`, never from `hash()`.
- Take memory and time from a sibling job's `sacct`, and set Slurm time limits at about three times the expected runtime. Put a time cap on anything that is not analysis, and stop at the cap.
- Write commit messages through a file. Sub-agents run no git command. The lead is the only committer and checks every hand-back against its primary tables before commit. Each file has one writer, and parallel work writes fragments that a merge step joins, reporting any collisions.
- Do not edit `README.md`, `CLAUDE.md`, `docs/README.md`, `docs/progress-log.md`, `docs/WAYS_OF_WORKING.md`, any earlier round's files, or anything in the other track's areas. Proposed edits go in the report.
- Run `code/scripts/verify_numeric_claims.py` over your documents before every handover, with your exceptions in `.verify-exceptions-round7-ppi`.
- After opening a pull request, confirm on GitHub that it exists and put its number in the report.

**Fan-out.** Every stage names its parallel units. Dispatch one sub-agent per unit with a written brief, and put the sub-agent's frame id in the first message of its brief, as round 5's E5 memo asked. The brief carries the sentence "Stamp every output directory with `stamp_dir()` from the `longleaf-provenance` skill under the frame id given in this brief. Before reusing or rebuilding any output you did not create, run `whose()` on it; if the verdict is `sibling` or `unstamped`, ask me rather than rebuilding." Compare the id in every returned stamp with the id you assigned before the fragment is merged. The lead merges, recomputes every pooled number from the merged tables into a `<stage>_report_numbers.csv`, and commits. Mechanical sub-agent work may run one model tier below yours. Derivations stay with you.

---

## 5. Working copies, code delivery and where to write

**Your areas.** Branch `round7-ppi`, from the starting commit, never rebased, never merged into `main` by you, and with nothing merged into it. Scripts `code/scripts/round7_ppi_*.py`. Results `results/round7/ppi/<STAGE>/`. The exceptions file `.verify-exceptions-round7-ppi` at the repository root. Documents, with these exact names:

| document | path | kind |
|---|---|---|
| operating plan | `docs/round07/tracks/ppi/round07_ppi_plan.md` | living |
| theory | `docs/round07/tracks/ppi/round07_ppi_theory.md` | living |
| S2 gate report | `docs/round07/i01/ppi/round07_ppi_S2_report.md` | frozen once handed over |
| S4 gate report | `docs/round07/i02/ppi/round07_ppi_S4_report.md` | frozen once handed over |
| closing report | `docs/round07/i03/ppi/round07_ppi_final_report.md` | frozen once handed over |

Tags `round7-ppi-S2`, `round7-ppi-S4` and `round7-ppi-final`. Longleaf outputs under `results/round7/ppi/` in the project tree, stamped. When Nicolas hands you a decision memo, commit it unchanged at the path it names on your branch, so that it merges cleanly with the copy on `main`.

**Working copies.** On the Mac, reuse the PPI clone `~/hest-1k/HEST-1k-replication-PPI`, which Nicolas brings up to date with `main` before you start. It was left on branch `round5-ppi`, and that branch stays as it is. Confirm the working tree is clean, fetch, and create `round7-ppi` from `origin/main` at the starting commit. If the tree is not clean or a `.git/index.lock` is present, tell Nicolas and wait. The other clones under `~/hest-1k` belong to other sessions. Do not run git in them. On Longleaf, make a fresh code clone at `/work/users/w/e/weiyang/hest_code/round7-ppi/` in S0 by a Slurm job over the SSH key on Longleaf. The round-5 code clones are not used.

**Code delivery.** From the first job, as round 5's E2 memo set (`docs/round05/i02/ppi/round5_ppi_E2_decisions.md`, section 4). Commits reach the Longleaf clone as a git bundle applied by a short Slurm job with `git merge --ff-only`. The same job writes a read-only snapshot of the delivered commit's `code/` directory to `/work/users/w/e/weiyang/hest_code/round7-ppi_snapshots/<full commit hash>/`, and every job runs from its own output directory with that snapshot on `PYTHONPATH`. Each delivery is a row of `results/round7/ppi/code_deliveries.csv`. Results come back to the Mac clone by copying over your Longleaf access and are committed there. Before each gate push, run that memo's two provenance checks and commit `results/round7/ppi/provenance_index.csv`.

**Pull requests.** GitHub sees one push per gate. At each gate you commit, tag and push the branch and the tag together, open one pull request into `main`, and stop. You never merge. Nicolas merges with a merge commit after the oversight chat accepts the report. Do not push again while that pull request is open. Branches are never rebased, squashed, amended after a push or force-pushed. A rejected gate is fixed with new commits on the same open pull request.

---

## 6. Simulation and masking, the shared grid

Unless a stage says otherwise, every stage runs on two grids.

**Simulation.** Round 5's E4b simulation (`code/scripts/round5_ppi_e4b_sim.py`, which uses E1's generator through `round5_ppi_e4_sim.py`) with its settings, which are $G \in \{15, 24, 51\}$, $n_L \in \{4, 6, 8, 12\}$, E1's $R^2$ grid, $\lambda^\star \in \{0.6, 1.2\}$, $\kappa = 0$, the normal and skewed laws and $p_a \in \{0.1, 0.01\}$, with balance on the own $\bar f_g$ ($k = 1$). Add the case $k = 2$, where the second balance variable is a standard normal variable drawn per cluster independently of everything else, as a stand-in for a principal component that carries no signal. Add one cell family with $G = 51$ and $n_L = 16$.

**Masking on the real tasks.** The six tasks, $\theta_3$ and $\theta_2$, donor-weighted, every unit of a labelled cluster labelled, design target, $n_L \in \{4, 6, 8, 12\}$ (and 16 on the census tasks), the three encoders and the permuted arm on tissue, 2,000 accepted draws per cell, with E5's seeds for the first 2,000 where a cell repeats E5. Balance variables `own` (the estimand's own $\bar f_g$, $k = 1$), `pcF2` and `pcE2` (tissue only), and `perm_cluster` as the control, at $p_a \in \{0.1, 0.01\}$. Arms are the three encoders, the permuted predictor and the constant predictor on tissue, and the package predictor and the constant predictor on census. Report beside every D2 cell its support $p_a\binom{G}{n_L}$, the range of $\hat\pi_g$ over clusters as a ratio to $n_L/G$, and the share of genes with standardised bias above 3.

Coverage is reported at 90% with its Monte Carlo standard error. Width is reported as the ratio to the D0 classical width of the same cell, as round 5 did.

---

## 7. The plan

Six stages. Gates at S2, S4 and S5. Transcribe this section into the plan before running anything, and keep a current-state block at the plan's top so that a compacted or restarted session can resume from the plan alone.

### Interval i01

**Entry gate.** This document is on `main`, Nicolas has brought the PPI clone up to date, and the session can reach Longleaf.

#### S0. Setup and anchors (half a day, capped at one day)

1. Read this document, `docs/WAYS_OF_WORKING.md`, the two documents of section 2.1, the estimator definition, section 3 of `docs/round05/tracks/ppi/round5_ppi_theory.md`, and section 4 of round 5's E2 memo.
2. Set up the branch, the Longleaf code clone and the first bundle delivery (section 5), and transcribe section 7 into the plan.
3. Anchor. Rerun round 5's E5 cells with round 5's code and seeds and reproduce, to four decimals, the `rej_t` width ratio in column `wr_D0cl` of `results/round5/ppi/E4b_rejective/e4b_rej_width_ratios.csv` for $\theta_3$, own balance, $p_a = 0.01$, $n_L = 8$, on `CCRCC` with arm `uni_v2` (0.7263) and on `ACS_STATES` with arm `package` (0.5513). Then rerun the same cells with the new code and match them within the Monte Carlo error of the draw count.

**Exit.** Both anchors pass, with the numbers in `results/round7/ppi/S0_anchors/s0_anchors.csv`.

#### S1. Weighting under rejective selection (three days, capped at four)

Time cap three days, with the runs fanned out by task (six units) plus one simulation unit.

1. **Theory first.** In `docs/round07/tracks/ppi/round07_ppi_theory.md` section 1, write the estimators and variances of section 2.3 for D2, the conditions under which $\hat\theta_{\mathrm{HT}}$ is unbiased for the design (every $\pi_g > 0$), the effect of estimating $\pi_g$ and $\pi_{gh}$ by simulation, the interval's reference distribution, and how the cross-fitted difference form interacts with the weights. Say what you expect the weighting to do in the cells where round 5's `rej_t` failed, before any run.
2. **Synthetic test.** Extend round 5's test 3 (`code/scripts/round5_ppi_e4b_tests.py`) to the weighted estimators. Check that $\hat\theta_{\mathrm{HT}}$ is unbiased within Monte Carlo error under D2 at $(G, n_L, k) \in \{(51, 8, 1), (51, 8, 2), (24, 8, 1), (15, 6, 2)\}$, and that the mean of the variance estimate is within 0.10 of the empirical variance where the support is at least 1,000.
3. **Runs.** The simulation and masking grids of section 6 under D2, with estimators the classical mean with `textbook_t|fpc|lin` and `rej_t`, $\hat\theta_{\mathrm{HT}}$, $\hat\theta_{\mathrm{H}}$ and $\hat\theta_{\mathrm{HT},\lambda}$ with their intervals, and Broska and Howes's interval applied as if the clusters had been drawn without balance, and D0 with the classical and tuned estimators as the reference.

**Outputs.** `results/round7/ppi/S1_weighting/` with `s1_pi_hat.parquet` (every cell's $\hat\pi_g$ with Monte Carlo errors), `s1_sim.csv`, `s1_masking_grid.csv`, `s1_report_numbers.csv`.

#### S2. The comparators from the literature (two days, capped at three; gate)

1. **Theory.** Section 2 of the theory document gives Broska and Howes's interval specialised to the cluster contributions, with the checks against their example 1 and a simulation under their assumptions, and Kluger et al.'s weighted estimator and cluster bootstrap.
2. **Runs.** On the shared grids, under D0 (simple random selection of $n_L$ clusters), Broska and Howes's interval for the design target and for the superpopulation target, beside `textbook_t|fpc|lin|xf` and round 5's superpopulation interval. Kluger et al.'s design with $\pi_k = n_L/G$, which gives a random number of labelled clusters whose mean is $n_L$, and with $\pi_k$ proportional to $\lvert\bar f_k - \bar F\rvert$ mixed half and half with uniform, each with their estimator and cluster bootstrap and with the inverse-probability-weighted mean and its Poisson-design variance under the same draws, for the design and the superpopulation targets. Fan out by task, six units, plus one simulation unit.

**Outputs.** `results/round7/ppi/S2_comparators/` with `tests/`, `s2_sim.csv`, `s2_masking_grid.csv`, `s2_report_numbers.csv`.
3. **The S2 report** in `docs/round07/i01/ppi/round07_ppi_S2_report.md`, covering S0 to S2, with predictions S1.1 to S2.4 scored. Run the sweep, commit, tag `round7-ppi-S2`, push, open the pull request, and stop.

**Exit items, each with its evidence.**
1. The anchors of S0 pass (`S0_anchors/`).
2. The synthetic test of S1 passes, or the report says which cells fail and why (`S1_weighting/tests/`).
3. Every cell of both grids has run under every design and estimator named, or the report lists the cells that did not and why.
4. Broska and Howes's interval passes both checks of section 2.3 (`S2_comparators/tests/`).
5. The provenance index passes both checks.

**Predictions for interval i01.**
- **S1.1** In the simulation with $k = 2$ and $n_L \le 6$, the classical mean's bias exceeds 0.1 of its standard deviation in at least a quarter of the cells, and the Hájek interval covers within 0.03 of nominal in at least three quarters of them.
- **S1.2** On the real tasks with `pcF2` and `pcE2` at $n_L = 6$, the Hájek interval covers within 0.03 of the D0 classical interval in at most half of the cells where `rej_t` covered below 0.80.
- **S1.3** At $n_L = 8$ with own balance, the Hájek interval is wider than `rej_t` in every supported cell, by a width ratio of 1.10 to 1.50.
- **S1.4** For $\theta_3$ with own balance at $p_a = 0.01$ and $n_L = 4$, the smallest $\hat\pi_g$ is below 0.5 times $n_L/G$ on both census tasks.
- **S2.1** Under D0 for the design target, Broska and Howes's interval covers below 0.85 at $n_L = 4$ on at least two of the four tissue tasks.
- **S2.2** For the design target with $n_L/G$ of 0.5 or more (lung at $n_L = 8$ and 12, `CCRCC` and `CCRCC_merged` at $n_L = 12$), it covers above 0.95 at nominal 0.90, since it counts the unlabelled clusters' predictions as random and has no finite-population factor.
- **S2.3** For the superpopulation target it covers below 0.85 at $n_L \le 6$ in every simulation cell with $G = 15$.
- **S2.4** For the superpopulation target, Kluger et al.'s cluster bootstrap covers below 0.85 at $n_L \le 8$ on every task, in line with the project's own donor bootstrap at 0.71 to 0.84, as round 5's deck-2 literature check recorded.

### Interval i02, opened by the S2 decision memo

What follows is the default. The S2 memo fixes the design, and nothing of it is set up, staged or piloted before the memo.

#### S3. An adaptive, balanced design at the cluster level (two days)

The design of section 2.3 after Chen et al., with two scores, $u_g = \lvert\bar f_g - \bar F\rvert$ on every task and, on the tissue tasks only, the distance in the space of the first 10 embedding principal components from cluster $g$ to its nearest other cluster. Balance variables are $\pi_g$ and the estimand's own $\bar f_g$. A constant predictor makes the first score zero everywhere, which gives uniform probabilities, so the constant arm is that design. Implement the cube method's flight and landing phases in Python, with a time cap of one day, and test that its realised inclusion frequencies match the targets within Monte Carlo error. If the cap is reached, record the escalation and use conditional Poisson sampling with the same targets and rejection on the balance condition, which this instruction allows as the fallback. The estimator is $\hat\theta_{\mathrm{H}}$ with the interval derived in S1, beside Broska and Howes's interval, on the shared grids. With balance on the own $\bar f_g$ the difference form adds nothing, since the $\lambda$ term is balanced away, which is Chen et al.'s remark 1. Fan out by task, six units, plus one simulation unit. Outputs in `results/round7/ppi/S3_adaptive/` with `tests/`, `s3_sim.csv`, `s3_masking_grid.csv` and `s3_report_numbers.csv`. A version that labels in batches, after Kluger and Bates (arXiv:2602.16933), is not run this round. If S3 succeeds, propose it in the S4 report.

**Predictions.**
- **S3.1** At $n_L = 8$ with own balance and the first score, the adaptive design's Hájek interval has a width ratio of 0.95 to 1.15 against D2 with `rej_t`, for $\theta_3$ on `CCRCC` with `uni_v2`.
- **S3.2** It covers within 0.03 of nominal in every simulation cell with $n_L \ge 8$.

#### S4. A deterministic rule (one day; gate)

Greedy k-center on the tissue tasks of the shared masking grid, at $n_L \in \{4, 6, 8, 12\}$, computed exactly over the $G$ starts. For each cell, report the exact $\pi_g$, the share of pairs with $\pi_{gh} = 0$, the exact coverage of `textbook_t|fpc|lin` applied as if the sample were simple random, Broska and Howes's interval applied the same way, and the exact standard deviation of $\hat\theta_{\mathrm{HT}}$. Put each beside the same quantities under D0 and under D2 with own balance at the same $n_L$. Fan out by task, four units. Outputs in `results/round7/ppi/S4_kcenter/` with `s4_grid.csv` and `s4_report_numbers.csv`. Then write the S4 report in `docs/round07/i02/ppi/round07_ppi_S4_report.md` covering S3 and S4, with predictions scored, and stop at tag `round7-ppi-S4`.

**Predictions.**
- **S4.1** At $n_L = 8$, the classical interval applied as if the sample were simple random covers below 0.80 for $\theta_3$ on at least two tissue tasks.
- **S4.2** At $n_L = 8$, the exact standard deviation of $\hat\theta_{\mathrm{HT}}$ under k-center is at least 1.5 times that of the classical mean under D0, on every tissue task.

**Exit items.** S3's cube test passes or its fallback is recorded. Every cell has run or is listed. The predictions are scored. The provenance index passes both checks.

### Interval i03, opened by the S4 decision memo

#### S5. The closing report (one day; gate, end of track)

`docs/round07/i03/ppi/round07_ppi_final_report.md`, ending with a closing page "What the inference track established in round 7". It states, for each design, whether the paper can recommend it, under which conditions, and against which comparator, and lists what is not established. The memo at S4 may add stages before S5.

---

## 8. Predictions for the track, consolidated

The predictions above, S1.1 to S4.2, are the oversight chat's, written before any run. Copy them into the plan before running and score each in its gate report as held, partly held, refuted or not tested. In earlier rounds most of the oversight chat's magnitude predictions were refuted, so a refuted prediction is an ordinary outcome and is reported as plainly as a held one.

---

## 9. Reporting format

After each gate, in this order. 1. Stage and status. 2. What was run (scripts with md5s, commits, job ids, partitions, wall times, peak memory from `sacct`). 3. Acceptance checks with the actual numbers and file paths. 4. For every comparison, the list of variables that differ between its arms, written out. 5. Predictions against outcomes, as a table. 6. Results, numbers from files with paths, dispersion beside every mean, and paths in place of pasted tables over 20 rows. 7. Discrepancies, open questions and escalations. 8. What was not checked. 9. Proposed next step.

---

## 10. Decision boundaries

**You decide alone.** Sub-agent structure. Seeds. Replicate and draw counts above the stated ones. Job sizing. Which of two equivalent implementations to use. The number of simulation draws for $\hat\pi_g$ above 100,000. The reference distribution of each interval, provided the theory document derives it before the run.

**Record as an escalation and continue.** A design that cannot be formed at some $n_L$ (skip that cell, say so). A $\hat\pi_{gh}$ of zero outside the census tasks, or the approximation of section 2.3 disagreeing with simulated values (report the cells, propose a remedy). Any acceptance check failing at a tolerance the dtype supports (fix, rerun, say so). The cube method reaching its cap (use the fallback). A prediction parquet whose md5 differs from the record (use the file, say so). Any new property of the data.

**Stop and report.** An S0 anchor failing after one fix. A derivation in S1 or S2 that does not close. Broska and Howes's interval failing the first check of section 2.3 after one fix.

**Never the session's decision.** Contact with anyone outside the project. Any download of data or code, including the authors' implementations. Changes to `main`, to earlier rounds' files, to the project tree's checkout, or to the other track's areas. Any local run that Nicolas has not asked for in chat. Reopening what round 5 closed, which is form C, the cross-fitting term and the stratified draw for $\theta_2$. Any claim of novelty.

---

## 11. Needs, and what Nicolas does before starting

**The session needs** Longleaf by the route round 5's tracks used (with the SSH key on Longleaf for GitHub), the PPI clone on the Mac, read access to `~/hest-1k/ppi_conf_papers/`, the project's Python environment, and the `longleaf-provenance` skill.

**Nicolas does**

1. Brings the PPI clone up to date, with `git -C ~/hest-1k/HEST-1k-replication-PPI fetch origin` and a clean working tree, leaving it on `round5-ppi`.
2. Starts a fresh Claude Science session with access to that clone, to `~/hest-1k/ppi_conf_papers/` and to Longleaf, and gives it this message. "You are the execution session of round 7's inference track. Read `docs/round07/i01/ppi/round07_ppi_track.md` on `main` of `NicWYZ/HEST-1k-replication` in full and follow it. Your clone is `~/hest-1k/HEST-1k-replication-PPI`. Start with S0."
