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
