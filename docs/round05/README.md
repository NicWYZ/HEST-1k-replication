# Round 5, two tracks on intervals and prediction sets (7 to 9 October 2026)

Round 5 ran two tracks from `main` at `d82c3f3`. The inference track (`round5-ppi`, stages E0 to E5 with E3a and E4b) validated round 4's design-target interval in simulation, completed regime B, put the estimators in regression form, chose which clusters to label and defined the estimator once. The prediction-set track (`round5-conformal`, stages W0 to W5) completed the simulation map, ran GHCP in its own designs, extended the real-data map above 10 calibration donors and took up two theory questions. Gate tags are `round5-ppi-E2`, `round5-ppi-E4`, `round5-ppi-final`, `round5-conf-W2` and `round5-conf-final`. No masterplan was written at the time. The predictions were written in the two track instructions and are transcribed in the track plans, with those added at the E2 and E4 gates (section 2).

`docs/round10/00_prep/round10_findings_survey.md` lists what rounds 1 to 9 established by question with a status label. Round 5's findings are its rows A6 and A8 (prediction sets), B6 to B10 (inference) and E1 to E4 (design), and its section 3.1 table records which round-5 claims were later found in print. Round 10's final runs reran several of them (`docs/round10/i05/final-runs/round10_final_runs_report.md`, numbers in `results/round10/final_runs/F4/paper_numbers.csv`). Each finding below says where that changed it.

## 1. What the round established, as it now stands

Results paths below are under `results/round5/ppi/` for findings 1 to 8 and `results/round5/conformal/` for findings 9 to 13 unless written in full.

**Inference** (closing page of `docs/round05/i03/ppi/round5_ppi_final_report.md`; the estimator is `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`).

1. **The design-target interval needs the cross-fitting term.** At $G = 15$ and $n_L = 12$ in simulation, `textbook_t|fpc|lin|xf` has a ratio of estimated to empirical variance of 0.974 to 1.013 and covers 0.888 to 0.903, against 0.691 to 0.909 and 0.840 to 0.886 without the term (`E3a_crossfit/e3a_sim_prediction_cells.csv`; E4 report section 6.1; theory section 2.0). On the real tasks the remaining shortfall is mostly the classical $t$ interval's own under-coverage when donor contributions are skewed, which Johnson's correction does not repair (`E1_interval/e1_johnson.csv`, `E1_interval/e1_real_coverage_vs_skewness.csv`; survey row B8). *Later rounds.* Round 8 found that round 5's cross-fitted estimator is, for even $n_L$, Williams' (1961) split-sample regression estimator without the factor $1 - n/G$ on its correction term, so the cross-fitting term is that omission and not a result of the project's own (`docs/round08/i01/positioning/round08_positioning_note.md`, section 3.2; survey row B9). Round 9 found that the variance without round 4's linearised term grows with the level of the predictions (survey row B10). Round 10 checked that the interval as round 5 ran it, with that term, is 0.982 to 1.004 of the width of Williams' form at 8 labelled clusters on the four tasks (`results/round10/final_runs/F1/aggregate/f1_fr1.csv`, prediction FR1 held), so round 5's tuned intervals do not carry the inflation. Round 10's runs use Williams' form and a fixed coefficient of 1 (`fix1`) as primary (`docs/round10/masterplan.md`, amendment of 8 November).
2. **Most of round 4's regime B gain on the Visium tasks was a level term.** Round 4's regime B classical comparator had no intercept, so any predictor with a level appeared to help. Against it a constant predictor gives a $\theta_3$ width ratio of 0.81 to 0.82 on kidney cancer, 0.85 to 0.86 on Indiana, 0.57 to 0.59 on lung and 0.12 to 0.13 on census income. Measured against the constant predictor, the encoders' width is 0.98 to 1.04 on the three kidney tasks, 0.74 to 0.84 on lung and 0.60 to 0.64 for the package predictor on census (`E2_regimeB/e2_decomposition.csv`, $\theta_3$, donor-weighted, design target, $m \ge 5$; E2 report section 6.4). The reading held for $\theta_3$ and not for $\theta_2$. Its derivation is the methods note, section 2. The constant predictor is the primary control and the permuted predictor is reported beside it. The mechanism is classical, the regression estimator's intercept (survey row B6).
3. **Form C is the within-cluster estimator.** Giving each cluster its own intercept makes a predictor constant within a cluster change nothing, and for $\theta_3$ form C's classical estimator is 0.818 to 0.854 of the pooled-intercept form P's width on the two kidney cancer tasks (`E3_twolevel/e3_prediction_cells.csv`; final report section 6.3). Round 10 reran regime B under form C, where `C_ppi`, `C_fix1` and `C_classical` cover 0.8795 to 0.913 over 736 cells (`paper_numbers.csv`, keys `B6.*`).
4. **The group difference needs a draw stratified by group inside each cluster.** Under simple random draws inside a donor, $\theta_2$ under-covers in regime B, down to 0.225 on lung at two units per donor (`E2_regimeB/e2_regimeB_grid.csv`). The stratified draw covers 0.885 to 0.913 at $m \ge 6$ in 192 of 192 cells (`E3_twolevel/e3_prediction_scores.csv`, E3.6). Round 7 found that round 5 and round 7 count draws with no $\theta_2$ interval differently, and every $\theta_2$ coverage is now reported with the share of draws that formed an interval (`docs/round07/README.md`).
5. **Regime B against regime A, and what predictions buy there.** Under the two-level estimator regime B is narrower than regime A in 210 of 232 comparisons with `C_ppi` and 211 of 232 with `P_ppi` at $c_d/c_s = 10$ (`E3_twolevel/e3_prediction_scores.csv`, E3.4). Its advantage is the design, since on the kidney tasks the regime ratio is the same with and without the predictor (E4 report section 6.2). In regime B against form C's classical estimator, the $\theta_3$ width ratio is 0.982 to 1.009 on the three kidney tasks, 0.706 to 0.847 on lung and 0.594 to 0.625 on census, and `C_ppi` covers 0.855 to 0.950 over the 196 rows (`E5_joint/e5_joint_design.csv`). *Later rounds.* The comparison is in print for the superpopulation target (Broska and Howes) and textbook for the design target with costs (Cochran, `[verify]`, chapters unread), so it is not the project's own (survey row E1 and section 3.1). Round 10 finds regime B narrower in 141 of 156 cost-matched $\theta_3$ comparisons (final-runs report section 6.5, keys `E1.*`), and finds that regime B's allocation in proportion to cluster size, a design choice made in E3, makes regime B wider than regime A on census by state in most unit-cost pairs (same report, section 6.2).
6. **Balanced selection of the labelled clusters is a design result with conditions.** Rejective selection on the estimand's own $\bar f_g$ at $p_a = 0.01$ takes the classical variance to 0.604 of simple random selection on kidney cancer with `uni_v2` and 0.264 on census by state at $n_L = 8$ (`E4_selection/e4_variance_ratios.csv`). The simple-random-sampling interval does not see the fall. The interval `rej_t` (theory section 3) does, at 0.726 and 0.551 of the D0 classical width in those two cells and 0.852 and 0.892 of the tuned estimator's D0 interval (`E4b_rejective/e4b_rej_width_ratios.csv`). Over the 960 real-task D2 cells with support of at least 1,000 it covers with median 0.878, range 0.641 to 0.931 (same file). Its cluster-level null control failed in 4 of 208 cells, two census-by-state designs at $n_L = 4$, for a reason not established (`E4b_rejective/e4b_acceptance.csv`; methods note section 4). So the estimator definition's default stays simple random selection, and balanced selection enters as a design result under its conditions (one balance variable, the estimand's own $\bar f_g$, support $p_a\binom{G}{n_L}$ of at least 1,000, $n_L$ of 8 or more), with where it failed (two balance variables at few residual degrees of freedom). *Caveats.* The conditions were read from the same runs and are not a validated rule. Round 7 found that the worst $\theta_2$ cells (Indiana, $n_L = 6$, 0.641 to 0.684) counted draws with no interval as misses, and the intervals that are formed there cover 0.86 to 0.89 (`docs/round07/README.md`). The variance of `rej_t` is Yang, Qu and Li (JASA 2023), Corollary A5, at the cluster level (survey row E3). Round 10's matched comparison at $n_L = 8$ and $p_a = 0.1$ gives `rej_t` coverage 0.859 at 0.960 of the D0 classical width on tissue and 0.8845 at 0.603 on census (`paper_numbers.csv`, keys `E3.tissue.D2_rej_t.*` and `E3.census.D2_rej_t.*`).
7. **Allocation.** With the classical estimator of form C, the cost-optimal number of labelled units per cluster at $c_d/c_s = 100$ is 77.9 on kidney cancer, 125.0 on Indiana, 74.5 on lung and 268.7 on census by state, against round 4's 121, 236, 172 and 379 (`E5_joint/e5_allocation.csv`; final report section 9). With a predictor the paper uses $m^\star\sqrt{(1 - R^2_w)/\rho_c(n_L)}$ with the measured between ratio and gives the fitted value beside it. On lung at $n_L = 8$ it is 80 to 88 across the three encoders. The optimum is flat (methods note section 4, "Escalation 9"). The formula is Snijders (2001) and Raudenbush (1997), and the measured $\rho_c$ is a small step (survey row E2). Round 10's medians of the PP to classical ratio at $n_L = 8$ are 1.087 on CCRCC, 1.016 on Indiana, 1.425 on lung and 1.080 on census by state (`paper_numbers.csv`, keys `E2.*`).
8. **The superpopulation-target interval under-covers in regime A with few clusters.** It covers below 0.85 in 916 of 8,820 simulation cells, all in regime A with a predictor at $G$ of 15 and 24, minimum 0.705 (`E5_joint/e5_superpop_undercoverage.csv`). Real-data claims use the design target.

**Prediction sets** (closing page of `docs/round05/i02/conformal/round5_conf_final_report.md`; the map is "own, provisional" in survey row A6).

9. **The simulation map.** At 90%, normal tails and a between-cluster share of 0.3 or more, the narrowest method with a finite-sample guarantee is HCP with no labelled target units, GHCP at 3 to 5 labelled units from about 14 calibration clusters, and the full conformal set inside the target cluster (`within_full`) from 9 labelled units, except at $o = 17$, where the half split is narrower by discreteness (`W1_sim/merged/w1_narrowest_valid.csv`). `within_full` is narrowest in 1,350 of 1,440 cells at share 0.3 and in 1,440 of 1,440 at share 0.9 (`W1_sim/w1_whole_grid_counts.csv`). Its definition is the methods note, section 3.
10. **The real-data map at 10 calibration donors.** HCP with no labelled target spots is the narrowest valid method up to $o = 5$ on every task. GHCP is 1.231 to 1.552 times HCP's width there and covers 0.992 to 0.999. From $o = 9$ `within_full` is 0.416 to 0.677 of HCP's width and the narrowest method, except at $o = 17$ and on Indiana at $o$ from 9 to 15, where the plain split is narrower by at most 2% (`W5_map/w5_report_numbers.csv`; `W3_real/w3_report_numbers.csv`, W3.2). It replaces round 4's recommendation of the plain split and the half split. On kidney cancer it is 2.116 wide at $o = 10$ against the plain split's 2.321, 1.967 at $o = 25$ against 2.137 (half split) and 2.300 (plain), and 1.709 at $o = 100$ against 1.754 and 2.109 (`w5_report_numbers.csv`). *Round 10.* HCP at $K = 10$ and $o = 0$ covers 0.9694 on CCRCC in the final runs. HCP is wider than `within_full` by at least 1.729 on CCRCC and 1.562 on lung from 9 spots, and on Indiana `within_full` is 1.049 to 1.072 times the plain split's width at 9 to 15 spots, so there the plain split leads by more than round 5's 2% (`docs/round10/i05/final-runs/round10_final_runs_report.md`, section 5, P10.3; keys `F3.A4.CCRCC`, `F3.A6.*`).
11. **GHCP and the number of calibration donors.** On kidney cancer, GHCP at $o = 5$ becomes narrower than HCP from $K = 12$ (0.963) to 0.831 at $K = 20$, and 0.796 on the merged label set. On Indiana at $K$ from 14 to 20 it stays within 4% of HCP. With the head held fixed, GHCP at $o = 5$ on kidney cancer falls from 5.30 to 2.70 as $K$ goes from 10 to 20, against HCP's 4.47 to 3.25, so the calibration count alone produces the fall (`w5_report_numbers.csv`, parts 2 and 3).
12. **GHCP's own designs.** In the fixed design of 20 groups at $o = 5$ the released GHCP is 27.55 wide against 33.40 for HCP (`W2_ghcp_settings/w2_sim_designs.csv`). From 9 labelled units `within_full` is 2.0 to 4.1 times narrower than the released GHCP wherever GHCP is finite (`docs/round05/tracks/conformal/round5_conf_plan.md`, section 7.3). On the census task GHCP is narrowest at every $o \ge 2$ with 30 or 50 PUMAs, and with 20 PUMAs `within_full` is narrower at $o = 9$ and 10, at 210,334 and 221,958 dollars (`W2_ghcp_settings/w2_census.csv`). The released code calibrates HCP on half of the reference groups, so its 20-group design sits at 10 calibration clusters, the real-data map's $K = 10$ (`W5_map/w5_method_groups.csv`). GHCP's coverage held in every setting.
13. **Theory** (`docs/round05/tracks/conformal/round5_conf_theory.md`). Two parts of round 4's small-$K$ Proposition 2 are direct corollaries of Tibshirani, Barber and Ramdas (arXiv:2608.27310), Theorems 3 and 7 (A.2). The bound for randomised methods and the coverage floor of Proposition 1 rest on round 4's proofs and were not found in print (A.3), which survey row A8 keeps as own and provisional. For $K + 1 \ge 1/\alpha$, in the revealed-law model, HCP is not tight, and no valid symmetric method is narrower than HCP at a configuration of continuous laws without being wider at another configuration, one that contains a group whose scores are all equal (B.5). Whether HCP is dominated in expected width is open.

## 2. Expectations and their scores

The predictions are the oversight's, written before the runs. Their full wording is in `docs/round05/tracks/ppi/round5_ppi_plan.md` section 2.1 (E1 to E4), `docs/round05/i02/ppi/round5_ppi_E2_decisions.md` section 5 (E3a.1 to E3a.3, E3.6, E3.7), `docs/round05/i03/ppi/round5_ppi_E4_decisions.md` section 5 (E4b.1 to E4b.4) and `docs/round05/tracks/conformal/round5_conf_plan.md` section 2 (W1 to W4). The track's scores are in the reports' section 5, and the gate reviews accepted them except where noted.

**Inference.**

| prediction, in short | score |
|---|---|
| E1.1 final interval 0.88 to 0.91 under the normal law at $n_L \ge 6$ | partly held (341 of 390 cells, minimum 0.840) |
| E1.2 the linearised term needed at $\kappa = 10$ | partly held |
| E1.3 tuning costs 0.03 to 0.15 of the variance ratio when $n_L/G \ge 1/3$ | partly held |
| E1.4 coverage varies by population; skewed law 0.85 to 0.88 | partly held |
| E1.5 variance ratio below 1 above the break-even count, above 1 below it | refuted in its second half |
| E2.1 regime B covers 0.87 to 0.92 at $m \ge 5$ | held for $\theta_3$, refuted for $\theta_2$ |
| E2.2 constant predictor at or below the permuted one, gap at most 0.06 | partly held |
| E2.3 encoders over constant 0.93 to 1.00 on Visium, lower on lung and ACS | held in substance |
| E2.4 constant predictor's ratio equals $1 - L$ within 0.03 | partly held |
| E2.5 encoder over constant flat in $m$ | held for $\theta_3$, refuted for $\theta_2$ |
| E3a.1 corrected variance ratio 0.90 to 1.05 at $G = 15$, $n_L = 12$ | held |
| E3a.2 the two intervals agree at $G = 51$ | held |
| E3a.3 lung at $n_L = 12$ within 0.015 of the classical 0.885 | held for $\theta_3$ |
| E3.1 permuted predictor null under form C | held |
| E3.2 regime B ratios agree with E2's within 0.05 | partly held |
| E3.3 form C 3 to 20% narrower than form P, covers 0.87 to 0.92 | partly held (track); held for $\theta_3$ and not applicable to $\theta_2$ (E4 review, `round5_ppi_E4_decisions.md` section 2) |
| E3.4 regime B narrower in at least 200 of 232 | held |
| E3.5 classical $m^\star$ falls by about $\sqrt{1 - L}$ | refuted; the E4 review found its second clause compared the formula with a fitted curve that cannot express the between gain |
| E3.6 stratified $\theta_2$ covers 0.86 to 0.92 | held |
| E3.7 regime ratio with and without predictor | partly held |
| E4.1 balanced variance within 0.05 of $1 - R^2$ in simulation | partly held |
| E4.2 real-task balanced variance in its bands | partly held |
| E4.3 two principal components recover half the gain on lung | partly held |
| E4.4 classical interval over-covers under D2 | over-coverage refuted, the rest partly held |
| E4.5 embedding balance leaves the ratio at 0.9 or above on kidney | partly held |
| E4b.1 to E4b.4 `rej_t` coverage and width, the null controls, lung's ratios | held (`E4b_rejective/e4b_prediction_scores.csv`) |

E4 acceptance check 2 failed, and the E4 review found its band was set wrongly, as if the 50 genes were independent replicates when every gene shares the same draws. E4b redid the check.

**Prediction sets.**

| prediction, in short | score |
|---|---|
| W1.1 GHCP narrowest nowhere at $K \le 10$ | partly held (1 cell) |
| W1.2 GHCP narrowest at $o$ 3 and 5 from $K = 20$, 3 to 10% below HCP | partly held (3 to 13%) |
| W1.3 plain split against GHCP by $K$ | held, apart from one cell |
| W1.4 first sentence, `within_full` against `within` | held |
| W1.4 second sentence, `within_full` narrowest from $o = 9$ | refuted as written; the W2 review called the prediction self-contradictory and its own error |
| W1.5 margins at share 0.9 | refuted on both magnitudes |
| W2.1 to W2.3 in GHCP's designs | held |
| W2.4 GHCP against HCP by number of groups | partly held; the W2 review found it could not be scored as written at 90% |
| W2.5 census, 20 and 10 PUMAs | refuted at $o = 9$ and 10; the W2 review found its second clause could not be scored as written |
| W3.1 original wording | refuted |
| W3.1 as amended by the W2 review before W3 ran | partly held (in full on the two kidney cancer label sets) |
| W3.2 `within_full` margins over the splits | partly held |
| W3.3 GHCP within 8% of HCP on kidney cancer for $K$ 12 to 20 | refuted |
| W3.4 head held fixed | partly held |
| W3.5 Indiana repeats kidney cancer | partly held |
| W4.1 Proposition 2 a corollary | partly held, as the W2 review directed |
| W4.2 Proposition 1's floor not found | held |
| W4.3 step 4 a result, dominance unresolved | held |

## 3. What was tried and did not work

- **The uncorrected design-target interval** `textbook_t|fpc|lin`, which loses coverage when most clusters are labelled (0.840 at $G = 15$, $n_L = 12$). Replaced by the `xf` form, itself now read as Williams' estimator with a factor missing (finding 1).
- **Johnson's skewness correction** does not restore the classical interval's coverage under skewed contributions (`E1_interval/e1_johnson.csv`).
- **A regime B comparator without an intercept, and the permuted predictor as the only control.** Both credit a predictor with the level term (finding 2).
- **Simple random draws inside a cluster for $\theta_2$**, which miss rare groups (finding 4).
- **The simple-random-sampling interval under balanced selection**, which does not see the variance reduction (E4 decision memo section 2).
- **`rej_t` with two balance variables at few residual degrees of freedom**, and the rule $n_L - k - 1 \ge 2$ as a floor (final report escalation 7).
- **A unit-level permuted balance variable as the null control.** It falls outside three standard errors in 44 of 64 kidney cancer $\theta_2$ cells against 8 of 64 for the cluster-level control (E4b.3).
- **A fitted variance-components curve $a/n_L + b/(n_L m) + c$ for allocation**, which cannot carry a between gain that is zero below $n_L = 6$ (E4 decision memo section 2).
- **The superpopulation interval for real-data claims** (finding 8).
- **GHCP with a few labelled spots at 10 calibration donors**, wide and conservative (finding 10), as round 4 had found.
- **Process.** Uploading scripts loose into jobs left provenance records that were hard to read, and was replaced by code delivered as bundles and run from read-only snapshots (E2 decision memo section 4). A threshold computed in float32 accepted no candidate where the support was tiny (final report escalation 2).
- The dead ends carried in from round 4 (a pre-test for $\lambda$, bootstrap intervals with few clusters, tuning on the clusters it is applied to, recalibrating donor offsets, two-way clustering, spot-weighted rows as evidence, the four prediction-set candidates with no labelled test units, claiming the break-even rule or gain limit as new) are in the methods note, section 6.

## 4. What was presented outside the project, and what has changed since

The second advisor meeting, on 7 October, stopped at slide 8 of the deck prepared from outline revision 3 of 4 October (`00_prep/deck2/deck2_outline.md` at the tag `record-full-2026-11`). The record does not hold the deck as built, so whether slides 1 to 8 as shown matched that outline is not shown. In the outline they covered the literature read, the two original topics, the first experiments with the correction that two breast-cancer samples presented on 21 September as one donor are two donors from one laboratory, the roadblocks, what the first experiments established (spot-level intervals cover 0.04 and donor-clustered ones 0.91; HCP at 10 donors covers 0.97 at 1.95 times the naive width), the originality check, and the pivot to "what does a labelling budget buy" with regimes A and B and three questions. Slides 9 to 16, with round 4's results, the data sets and the questions to the advisors, were not reached, and no result of round 5 has been presented. What has changed since in slides 1 to 8:

- Slide 7 said that PPI with few labelled clusters and the comparison of where to put the labels were found nowhere. Kluger et al. (arXiv:2501.18577) had already given bootstrap intervals for PPI under clustered designs, Broska and Howes (arXiv:2610.09601) give cluster-robust PPI++, and the regime comparison is in print for the superpopulation target and textbook for the design target (`docs/round07/README.md`; survey section 3.1). `00_prep/deck2/deck2_literature_check.md` states the same novelty verdicts and must not be read as current.
- Slide 7 said that GHCP did not treat fewer than 20 groups. The released code calibrates HCP on half of the groups, so its 20-group design sits at 10 calibration clusters (finding 12).
- Slide 8's framing as a methods paper on labelling budgets was reframed on 6 November as an applied paper on the proposal's two questions (`docs/round10/00_prep/round10_reframing.md`, section 1).
- Slide 6's HCP coverage stands (0.9694 on CCRCC in round 10's final runs, finding 10).

## 5. Open threads

- Why the cluster-level null control fails in two census-by-state designs at $n_L = 4$ is not established (finding 6).
- Weighting the labelled clusters by inclusion probabilities simulated under rejective selection, the question the inference track left, was run in round 7 and fails (survey row E4).
- Whether HCP is dominated in expected width is open (finding 13).
- Two round-4 rows of the real-data map were not reproduced, `within` at $o = 10$, one by one test spot in coverage and one by $5.9 \times 10^{-8}$ in median width, and were not rerun (`W3_real/merged/w3_repro_mismatch_rows.csv`).
- Whether regime B can be bought on a spatial transcriptomics platform, and at what cost, is question Q1 of the state block.
- Fuller (2009) was read only in abstract, so it is cited for the regression estimator under rejective sampling only as far as the abstract supports (final report escalation 11).

## Documents kept

| document | what it is for |
|---|---|
| `round05_methods_note.md` | the definitions, the reading E2 tested, the closing checks and the dead ends, taken word for word from working papers that go |
| `masterplan.md` | where the round's predictions are written |
| `00_prep/deck2/deck2_literature_check.md` | the originality check of round 4's results on 4 October, with what was confirmed and what was only reported; its novelty verdicts are superseded (section 4) |
| `i01/ppi/round5_ppi_E2_report.md` | E0 to E2 in full: the interval in simulation, regime B and the level term |
| `i02/ppi/round5_ppi_E2_decisions.md` | the predictions E3a.1 to E3a.3, E3.6 and E3.7, the designs of E3a and the stratified draw, and the code-delivery rules |
| `i02/ppi/round5_ppi_E4_report.md` | E3a, E3 and E4 in full |
| `i03/ppi/round5_ppi_E4_decisions.md` | the predictions E4b.1 to E4b.4 and the design of E4b |
| `i03/ppi/round5_ppi_final_report.md` | the inference track's final report; its closing page is the track's summary |
| `tracks/ppi/round5_ppi_plan.md` | the inference track's plan, with the predictions as written and their scores |
| `tracks/ppi/round5_ppi_theory.md` | the level term, the cross-fitting term, the two-level estimator, allocation and the variance under rejective selection |
| `tracks/ppi/round5_ppi_estimator_definition.md` | the estimator as round 5 defined it |
| `i01/conformal/round5_conf_W2_report.md` | W0 to W2 in full: the simulation map and GHCP's designs |
| `i02/conformal/round5_conf_final_report.md` | the prediction-set track's closing report; its closing page is the track's summary |
| `tracks/conformal/round5_conf_plan.md` | the prediction-set track's plan, with the predictions and the gate decisions transcribed |
| `tracks/conformal/round5_conf_theory.md` | the two W4 theory questions |
