# Round 4, methods note: passages kept from documents that were removed

Each section below is moved word for word from a round 4 document that was removed from the tree when the record was reduced. The full documents are kept at the tag `record-full-2026-11`. Each section says which report, script or results file the passage describes. What stands now is in `docs/round04/README.md`.

## 1. Dead ends, ruled out and why

From section 12 of the oversight handoff of 30 September 2026 (`docs/round04/oversight/round4_oversight_handoff.md` at the tag). The items describe round 3's results (`docs/round03/i03/exec/round3_final_report.md`) and the choices that set up round 4's two tracks (`docs/round04/00_prep/round3_directions.md`, `docs/round04/00_prep/round4_originality_check.md`). "My" in the ninth item is the oversight session's.

- Institution or laboratory shift from HEST-1k. No cell with three laboratories at three donors; no two-laboratory cell with disease fixed; the one kidney "laboratory" contrast was tumour against non-tumour, and the Washington University label was generated at Indiana.
- Feature-based reweighting (weighted conformal with a density ratio). Slides are identifiable from features at AUC 0.97 and from tissue composition at 0.90; $n_{\text{eff}}$ collapses to 2%; weights move coverage a long way in both directions with no mean movement.
- The scaled score as a repair. 14.8 wide at matched coverage against 2.69.
- The small-$K$ explanation of the unit-calibrated shortfall. Refuted by A2c; the shortfall is scale, and the top-decile failure is the head's over-dispersion.
- Double conformal and repeated subsampling as C2 candidates. The first is infinite at $K = 10$; the second stays only as a known method in C1.
- Within-slide split conformal as our own method. GHCP is that setting with a better construction; we implement and cite it.
- "Cluster-robust PPI" as a new estimator. It is model-assisted survey estimation under two-stage sampling; the contribution is what predictions buy and the design, not the estimator.
- Treating IDC's `TENX95` and `TENX99` as one donor, and the replicate-leak reading of IDC. Withdrawn by D3.
- The ST platform and unlabelled samples as ways to reach my set-V prediction. Not applied; the tracks need donor-labelled, spot-resolved samples.
- The 1.6 mm edge threshold as a fixed rule. Four cores are 5 mm; the diagnostic is report-only either way.

## 2. Why the data pull did not widen set V

From the decision on the P1 stop of 28 September 2026 (`docs/round04/i01/data/round4_data_P1_decision.md` at the tag), whose decisions are transcribed in `docs/round04/tracks/data/round4_data_plan.md` section 8. It describes the selection made by `code/scripts/round4_data_select.py` (`results/round4/data/P1_selection/`). Round 10 later used a breast Spatial Transcriptomics task in its corpus (`results/round10/final_runs/F4/paper_numbers.csv`, key `B7.breast__Spatial_Transcriptomics`).

The two readings that would reach the predicted range are not applied. The older Spatial Transcriptomics platform (104 samples) has 100 µm spots, a few hundred spots per section and an uncertain pixel size on every sample, and no round-4 stage uses it. Samples with no label or a whitespace label (299) cannot be donor units and are what the label requirement exists to exclude. Storage is not the constraint; the tracks' needs are, and the tracks need donor-labelled samples. If either track later finds a use for the ST platform, it comes back as a proposal.

## 3. The reading of the Q3 grid that changed the design-target tuning rule

From section 1 of the Q3 decision memo of 2 October 2026 (`docs/round04/i03/ppi/round4_ppi_Q3_decisions.md` at the tag), which `docs/round04/tracks/ppi/round4_ppi_plan.md` section 14.1 transcribes in summary. It reads `results/round4/ppi/Q2_theory/q2_variance_grid.csv` for $\theta_3$ donor-weighted at $m$ = all under rule (c), against escalation 1 of `docs/round04/i02/ppi/round4_ppi_Q3_report.md`. "Section 3", "section 4" and "section 5" are the memo's, transcribed as plan sections 14.3, 14.4 and 14.5. The rule it led to, `c_crossfit_design`, is defined in `docs/round04/tracks/ppi/round4_ppi_estimator_definition.md`.

- **At $n_L \le 8$ the encoders gain on CCRCC and lung.** Superpopulation target, empirical variance ratio: CCRCC `uni_v2` 0.84, 0.75, 0.82 at $n_L = 4, 6, 8$; `hoptimus0` 0.93, 0.86, 1.02; lung `hoptimus0` 0.55, 0.52, 0.56 and `uni_v2` 0.54, 0.51, 0.55. Indiana is at 1.0 throughout. The loss appears at $n_L = 12$ and 16.
- **The loss at large $n_L$ is the complement form's unlabelled term.** With $n_L = 16$ of 24 donors, $U$ has 8 donors, and on lung with $n_L = 12$ of 15 it has 3, where the superpopulation ratio is 1.4 to 1.6 against 0.87 to 0.91 on the design target. $V_U = \lambda^2 \text{Var}(p_g)/G_U$ is as large as the labelled term there. That is a fact about the superpopulation form with a small complement, not about the predictors, and the design-based target, which every real-data coverage check uses, does not have it.
- **The design-target ratios drift to 1 as $n_L$ grows because $\lambda$ is tuned for the wrong objective.** The tuned $\lambda$ is identical on both targets in every cell, and it falls from about 0.45 at $n_L = 4$ to 0.29 at $n_L = 16$ on CCRCC as $G_U$ shrinks, because the tuning rule minimises the complement form's variance, whose $U$ term penalises $\lambda$ by $\lambda^2 \text{Var}(p_g)/G_U$. The textbook form has no such term, so for the design target $\lambda$ should minimise the between-donor variance of the rectifier over the labelled donors alone. Addendum 1 section 2 said the rules were unchanged for the textbook form, and that was my error. Section 3 corrects it and section 4 recomputes.

So the honest statement is narrower than escalation 1. On the real HEST tasks the achievable gain is small, because the predictors' donor-level squared correlation on the contrast scale is at most 0.44, and at $n_L \le 16$ the cost of estimating $\lambda$ takes much of what remains; where $G_U$ is small the complement form adds a loss of its own. On ACS, with donor-level $R^2$ of 0.57 and 0.95, the gain is large under either target. The gain theorem itself holds, since the oracle-$\lambda$ arm of the theorem check sits 0.03 to 0.08 above $1 - R^2_{\text{cluster}}$ at $G_U = 100$ and the estimated-$\lambda$ arm is what moves away from it. Section 5 makes the tuning cost a stated result.

## 4. The estimand of the closing page's ranges

From section 3 of the Q5a closing memo of 3 October 2026 (`docs/round04/i05/ppi/round4_ppi_Q5a_closing.md` at the tag). It describes the closing page "What the PPI track established" of `docs/round04/i03/ppi/round4_ppi_final_report.md` and the rows of `results/round4/ppi/Q4a_recompute/q4a_table61.csv`.

The closing page's ranges for the Visium tasks and for lung Xenium are for the estimand $\theta_3$ on the donor-weighted population. The $\theta_2$ rows in `q4a_table61.csv` show smaller gains on the same tasks. The paper quotes the closing page's ranges as $\theta_3$ numbers and reports $\theta_2$ beside them.

## 5. The conformal methods, stated once

From `round4_conformal_track.md` (at tag `record-full-2026-11`) (the conformal track's instruction, section 2.3; at tag `record-full-2026-11`), word for word. It defines the methods that `docs/round04/tracks/conformal/round4_conf_plan.md` and `docs/round04/i02/conformal/round4_conf_final_report.md` run.


**Split conformal.** Scores $s_i$ on a calibration set of $n$ spots; the interval for a new spot is $\{y : s(y) \le \hat q\}$ with $\hat q$ the $\lceil (n+1)(1-\alpha) \rceil$-th smallest calibration score. If the $n+1$ scores are exchangeable, coverage is at least $1 - \alpha$ and at most $1 - \alpha + 1/(n+1)$. A finite $\hat q$ exists only if $n \ge (1-\alpha)/\alpha$. Equivalently, $\hat q$ is the $(1-\alpha)$ quantile of the distribution that puts mass $\frac{1}{n+1}$ on each calibration score and $\frac{1}{n+1}$ on an atom at $+\infty$ standing for the unseen test score.

**Hierarchical exchangeability.** Donors are exchangeable with each other and spots are exchangeable within a donor, but a spot from one donor is not exchangeable with a spot from another. The question is coverage for a spot from a new donor.

**HCP.** Each of the $K$ calibration donors gets total mass $\frac{1}{K+1}$, spread equally over its $N_k$ spots, so spot $i$ of donor $k$ has weight $\frac{1}{(K+1)N_k}$; the test donor's $\frac{1}{K+1}$ is an atom at $+\infty$. With $F_k$ donor $k$'s empirical score CDF and $\bar F = \frac{1}{K}\sum_k F_k$, the cumulative mass at a finite $q$ is $\frac{K}{K+1}\bar F(q)$, and $\hat q$ is the smallest $q$ with $\frac{K}{K+1}\bar F(q) \ge 1-\alpha$, which at $K = 10$ and $\alpha = 0.1$ is the 99th percentile of the donor-balanced score distribution. Coverage is at least $1-\alpha$ for any $K \ge 1$ and at most $1 - \alpha + 2/(K+1)$ when scores are distinct; the interval is finite only when $\frac{1}{K+1} \le \alpha$.

**One score per donor** (Dunn, Wasserman and Ramdas). Draw one calibration spot per donor, apply split conformal to the $K$ resulting scores. Valid, noisy, wasteful. Their repeated-subsampling and CDF-pooling variants are in the same paper.

**GHCP** (Mallick, Tchetgen Tchetgen, Dobriban and Lee 2026). With $o$ initial observations from the test group, the test group is assigned a randomly donated size from the reference groups that have more than $o$ observations, which restores the symmetry HCP needs; part of the $o$ observations may train a test-group-specific score, the rest calibrate. The guarantee is finite-sample under their assumptions A1 to A3, which generalise hierarchical exchangeability by allowing separate mechanisms for the observed test-group size and the reference-group sizes. Implement it from the paper (check whether code is released; if it is, use it and record the commit; if not, implement and validate against every simulation figure the paper reports that can be reproduced from its stated settings). Its restricted-donor variant is included if the paper's description is complete enough to implement inside the cap; otherwise it is listed as not run.

**The oracle.** In simulation, the new-donor score distribution is known, so the half-width $q^\star$ at which a new donor's spot is covered with probability exactly $1-\alpha$ is computable. The price of validity of a method is $\hat q / q^\star$.

**References.** Mallick, Tchetgen Tchetgen, Dobriban and Lee, arXiv:2608.15500; Lee, Barber and Willett, ACM Journal of Data Science 2026, arXiv:2306.06342; Dobriban and Yu 2025 and Duchi et al. 2025 as GHCP cites them; Dunn, Wasserman and Ramdas, JASA 118(544), 2023, arXiv:1809.07441; Vovk, Gammerman and Shafer, *Algorithmic Learning in a Random World*, 2005 (smoothed conformal); Romano, Patterson and Candès, NeurIPS 2019 (CQR); Barber, Candès, Ramdas and Tibshirani, Annals of Statistics 2023 (beyond exchangeability); Lei, G'Sell, Rinaldo, Tibshirani and Wasserman, JASA 2018.

---


## 6. The conformal track's inputs

From the same instruction, section 3, word for word: the repository, the data and the assets the track built on.


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
