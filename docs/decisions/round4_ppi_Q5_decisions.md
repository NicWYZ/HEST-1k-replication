# Round 4, the PPI track, the Q5 decision memo (end of track, with one closing unit)

2 October 2026. Written by the oversight chat after reading `docs/round4_ppi_final_report.md` at tag `round4-ppi-final` (`a4f1e5b`, pull request #8), `docs/round4_ppi_theory.md` section 5 and the final estimator definition, and checking the report's numbers against `q4a_table61.csv`, `q4_prediction_scores.csv`, `q5_joint_design.csv` and `final_gate_sweep.tsv`. Nicolas hands this to the PPI session in full. Transcribe it into `docs/round4_ppi_plan.md` as section 15 before anything in it runs. The track is accepted subject to one closing unit, Q5a, capped at one day, after which the session pushes to the same branch, pull request #8 picks up the commits, and the track is closed.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

---

## 1. Acceptance, and two things I found in the tables

The final report is accepted, with the closing unit of section 3. Every number I checked reads back from the files as quoted. The Q4a recompute reproduces interval 2 exactly under the old rules, the Q4a and Q1b tests pass, the joint design table reads the C3 file at the md5 addendum 2 names, and the one unresolved numeric claim (0.32 in the Q3 report) is in a frozen document and stays.

Reading `q4a_table61.csv` beyond the rows the report tabulates, two things need acting on before the tables go into the paper.

1. **Every spot-weighted PPI row under `c_crossfit_design` is nuisance-driven, and the permuted predictor proves it.** On the spot-weighted $\theta_3$ design rows the permuted predictor gets a median $\hat\lambda$ of 0.86 to 0.92 on CCRCC and 0.95 to 0.98 on lung, with empirical variance ratios of 0.29 to 0.44 on CCRCC, 0.09 to 0.14 on lung and 0.000 on ACS states $\theta_2$. A predictor with no information cannot halve a variance. What it removes is the between-donor variance of the design-weight sums $\sum_i w_{gi}$, which under task-wide weights enters every donor's contribution $z_g$ through the outcome mean, and which any predictor that is constant across spots reproduces. Round 3 named this the covariance-estimand effect and the Q3 report said the spot-weighted ratios are not evidence that the encoders predict expression; the textbook form with the whole-population prediction term makes it total. Coverage of those rows is 0.72 to 0.88, below nominal, which is the other symptom. The donor-weighted estimands centre each donor on its own constants and do not have this. Section 3 says what to do, and the paper treats it as a finding about estimand choice, not as a gain.
2. **The ACS states $\theta_2$ donor-weighted diagnostic (escalation 2) is a defect in one of two columns, and the report cannot go to the paper until it is known which.** On the design target under both PPI rules the median of estimated over empirical variance is 204 to 1165 while the classical row's is 0.94 to 1.02 and the superpopulation rows' under the same $\lambda$ rule are 1.0 to 1.6. An interval whose estimated variance is hundreds of times its empirical variance covers 1.000, and these rows cover 0.91 to 0.975. So either the diagnostic column or the interval is computed wrongly for these rows, and nothing in the file says which. The report's reading, a median dominated by a few draws, cannot be right for a median.

The rest of the escalations are answered in section 4.

## 2. What the record says, for the paper

With the two corrections above, the PPI track's results read as follows, and this is what the paper's inference and design sections say.

- **The gain theorem holds, and its practical form is the tuning cost.** With the oracle $\lambda$ the simulated ratio sits within 0.08 of $1 - R^2_{\text{cluster}}$ at $G_U = 100$; with $\lambda$ cross-fitted from $n_h$ donors the ratio is $1 - R^2_{\text{cluster}} + [\text{Var}(\hat\lambda) + (\bar\lambda - \lambda^\star)^2]\text{Var}(p_g)/\sigma_u^2$, which the theorem check reproduces within 0.043 in all 24 cells (Q4.3, scored refuted at the 0.03 line, held at 0.05). The break-even $n_L > 4 + 2/R^2_{\text{cluster}}$ is the structural statement; it does not predict real-data cells one by one (Q4.4), and the paper says so.
- **On the Visium tasks the donor-weighted gain is small.** Design-target ratios at $n_L \ge 8$ are 0.93 to 1.09 for every encoder except `uni_v2` on CCRCC (0.81 to 0.90), consistent with donor-level $R^2$ of the within-donor contrast at or below 0.44 and the tuning cost at 3 to 8 donors per half.
- **On lung Xenium the gain is large and stable under the corrected rule.** 0.41 to 0.55 at $n_L = 6$ to 12 for every encoder, where the old rule's gain shrank with $n_L$; the permuted predictor stays at 1.03 to 1.05.
- **On ACS the gain is large**, 0.34 to 0.45 on states and 0.17 to 0.23 on PUMAs, with $\hat\lambda$ near 1 for a well-calibrated predictor.
- **The gain tracks the cluster-level $R^2$ of the within-donor contrast across genes**, with Spearman correlations of $-0.80$ to $-0.90$ on CCRCC against $-0.24$ to $-0.45$ for the unit-level Pearson correlation (Q4.1).
- **The design results stand.** Regime B is narrower than regime A at equal unit budget on every task at $n_L \le 8$, by the design alone (the permuted predictor's regime B ratio is 0.87 on CCRCC and 0.66 on lung), and more so with a predictor; the cost ratio at which regime A overtakes it is the affordability limit in 181 of 240 cells. The allocation condition is stated with its exception (`uni_v2` on CCRCC), as the theory document has it.
- **The joint table** supports the second half of addendum 2's statement and not the "from the first spot" clause, as escalation 9 says; the closing page's qualification stands.

## 3. Closing unit Q5a (one day, capped), then stop

No new simulation and no new masking draws. Everything below is recomputation from committed or kept per-draw outputs.

1. **Escalation 2.** From the per-draw outputs of the ACS states $\theta_2$ donor-weighted design rows (the Q4a unit records or the per-gene grid kept as an artifact), recompute for every draw the estimated variance, the interval half-width, the empirical variance across draws and the coverage indicator, and reconcile them. Report which column is wrong and why, fix the merge or the estimator code as the case may be, regenerate every affected row of `q4a_table61.csv` and `q4_main_table.csv`, and record the before and after values. If the interval itself is wrong, say so in the report and mark the rows; do not drop them.
2. **The spot-weighted PPI rows.** Add to `q4_main_table.csv` and `q4a_table61.csv` a `role` value `nuisance` for every spot-weighted PPI row (both targets, every $\lambda$ rule), with a one-line note column citing the permuted predictor's ratio in the same cell. No row is deleted. Write a short section in the final report, "The spot-weighted PPI rows", with a table of the permuted predictor's $\hat\lambda$ and variance ratio by task and $n_L$ from the existing rows, so the paper can show the artefact in one table.
3. **The Indiana genes with corrected cluster-level $R^2$ of 1.0** (escalation 10). Add a flag column to `q4_gene_axis.csv` and recompute `q4_gene_axis_summary.csv` with and without them, both kept.
4. **$\hat\lambda$ in the tables.** Every table that reports $\hat\lambda$ carries the mean of the two unclipped half-sample estimates and its standard error beside the clipped median, so the 0.5 artefact (halves clipping at opposite ends) is visible and the paper can report the unclipped value with its error.
5. **The closing page.** Revise "What the PPI track established" to carry items 1 and 2, in the readings of section 2 above, with every sentence naming its file. The theory document's section 5 and the estimator definition are unchanged.
6. Run the numeric-claim sweep, commit on `round4-ppi` with the reason in the message, push, and stop. Pull request #8 picks up the commits. Nicolas merges after the oversight chat reads the Q5a commit.

## 4. Answers to the other escalations

- 1 (ACS states $\theta_2$ spot-weighted design coverage 0.72 to 0.79): the shared shortfall with the classical interval is the skewed-contribution limit with very unequal state sizes, as the report reads it; under item 2 these PPI rows are nuisance rows anyway, and the classical spot-weighted row carries the Q1 caveat.
- 3 (the gene-axis union list): accepted; the intersection check is the sensitivity analysis and both stay.
- 4 (local runs under section 12.4): Nicolas's instruction; recorded.
- 5 (frame ids set at commit with a `frame_id_note`): accepted as the record; the `WAYS_OF_WORKING.md` rule now on `main` is the fix for the next round.
- 6 (the stray write): accepted.
- 7 (my allocation sentence): the report is right and my memo was wrong; the theory document's statement with the `uni_v2` exception stands.
- 8 (Q4.3 at 21 of 24): scored as the session scored it; the paper quotes the 0.043 maximum.
- 9 (the joint table and the "from the first spot" clause): the qualification stands and the closing page keeps it.
- 11 (Indiana prediction md5s): accepted as computed and recorded.
- 12 (lung $n_L = 16$): accepted.

## 5. Open items that leave this track

- The ACS donor-weighted $\theta_2$ column, if Q5a finds the interval rather than the diagnostic wrong, goes to the paper's authors as a correction to carry, not to a further stage.
- Round 5's candidates, in the handoff's order, start from `q5_cluster_table.csv`: active cluster selection, and the joint design section of the paper from Q5 and C3.
- A regression-form spot-weighted estimand (the estimating-equation influence function with the intercept, under which donor-level weight sums cancel) is the right fix for item 1 of section 1 if the paper wants spot-weighted PPI rows at all. It is a round-5 item, not this track's.
