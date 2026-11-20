# Round 10, the final runs for an applied paper (6 to 15 November 2026)

Round 10 followed Nicolas's reframing of 6 November (`00_prep/round10_reframing.md`, section 1): answer the proposal's two questions, calibrated uncertainty for histology-predicted expression and valid inference with it, applying existing methods, with new method only where a documented literature search finds a gap. The plan of record is `masterplan.md`. Three tracks were planned, to run in order. Track `ledger` built the methods ledger (stages L0 to L3, gate L3 answered on 8 November, pull request #38, merge commit `5d7bf3d7`). Track `final-runs` produced one clean set of analyses on Longleaf (gates F1 to F4, tags `round10-final-runs-F1` to `round10-final-runs-F4`, pull request #39). Track `paper`, which was to draft v1 from the writing plan, never started: Nicolas approved gate F4 and closed the track on 15 November ("Gate approved, close the track, leave any open items in the report", `round10_final_runs_F4_decisions.md` (at tag `record-full-2026-11`)), and the round closed without draft v1, which carries to the next round.

The numbers of the paper are in one table, `results/round10/final_runs/F4/paper_numbers.csv` (443 rows, keyed by the identifiers of `00_prep/round10_findings_survey.md`, section 2, with file, selector, stage and commit for each value). The report that explains them is `i05/final-runs/round10_final_runs_report.md`. Paths below beginning `F1/` to `F4/` are under `results/round10/final_runs/`. Unless a line says otherwise the estimand is $\theta_3$ (donor-weighted), the encoder `uni_v2`, the scale $\log(1 + y)$, the nominal level 0.90, and "8 donors" means 8 labelled clusters in regime A.

## What the round established

What rounds 1 to 9 established is listed, by question and with status labels, in `00_prep/round10_findings_survey.md`, section 2. The findings below are round 10's, and several of them change what that survey says (marked).

**The data.**
- The federated project's corpus, read on Longleaf without a download, gave six tasks: kidney Visium (51 audited donors, 5 centers), breast ST, bowel Visium, brain Visium, breast Xenium and lung Xenium. Of 340 registry samples in the candidate groups, 278 were kept after a donor-label audit (`F1/aggregate/f1_task_list.csv`; F1 report, section 3). Breast Visium was dropped, its 7 kept samples coming from 6 donors. The nuclear covariates of round 3 were extended to the corpus (option (b)), so every corpus task carries $\mu$ and $\theta_1$ to $\theta_3$.
- Held out by donor, the median spot-level Pearson on $\log(1 + y)$ ranges from 0.140 (brain Visium, `hoptimus0`) to 0.746 (breast Xenium, `uni_v2`). Held out by center it falls on every task, to -0.123 to 0.022 on brain Visium and 0.004 to 0.123 on kidney Visium across encoders (`F1/aggregate/f1_predictions.csv`; F1 report, section 6).
- Spots are far from independent. The ratio of the donor-clustered to the i.i.d. standard error of the spot mean has median over genes 14.8 (LUNG_XENIUM) to 59.0 (brain Visium) (`F2/report_tables/r10b_d9_by_task.csv`).
- INT5 is the most extreme of kidney Visium's 51 donors on median raw library size per spot ($z$ 5.559) (`F1/aggregate/f1_d13_kidney.csv`).
- CCRCC is run on the 24-donor set, with the 23-donor merged set (`CCRCC_merged`) as the sensitivity row (Nicolas at F1; methods note, section 2).

**Round 5's intervals carried no level-dependent inflation (FR1).** With round 4's `lin` term, round 5's interval is as wide as Williams' two-fold form with the within-half variance at 8 donors, ratio of median widths 0.982 to 1.004 on CCRCC, INDIANA_KIDNEY, LUNG_XENIUM and ACS by state. Without the term the ratio is 1.085, 1.210, 2.144 and 16.765 (`F1/aggregate/f1_fr1.csv`; F1 report, section 6). Round 9's `R5` arm omitted the term, so round 9's widening factors (finding B10) describe round 4's withdrawn variance, not the intervals rounds 5 to 7 reported. The coverage of round 5's tuned interval at 8 donors is reproduced by the corrected form within 0.008: 0.8581 against 0.85775 on CCRCC, 0.896 against 0.895 on INDIANA_KIDNEY, 0.8752 against 0.8675 on LUNG_XENIUM (`F2/report_tables/r13_p10_1.csv`). This changes the survey's reading that rounds 5 to 7's numbers needed the correction.

**The estimator (question E) and the primary interval.** The final runs use the difference estimator with the coefficient fixed at 1 (`fix1`) as the paper's primary estimator (R7-6), the two-fold cross-fitted difference estimator in Mickey's (1959) form, which is Williams' (1961) form for even $n$, beside it from 6 donors, and the classical estimator as the control (`i01/ledger/round10_ledger_decisions.md`, sections 1 and 2; methods note, section 1). For the cross-fitted form the within-fold variance $\hat V_w$ stays primary: the smallest median over genes of $E(\hat V_w)/\text{Var}$ over 1432 cells with at least 6 donors is 0.9937 (`F2/aggregate/f2_switch_decision.json`). The exactly unbiased variance $\hat V$ is negative in a median 0.201 of draws at 6 donors (F2 report, section 6.2), so the cross-fitted interval under $\hat V$ alone covers only 0.73 to 0.75 on the HEST tasks at 8 donors (`F2/report_tables/r13_p10_1.csv`).

**Regime A, labelling whole donors.**
- At 8 donors on CCRCC `fix1` covers 0.8965 against `classical`'s 0.849 (keys `B8.CCRCC.*`). Over every task, encoder, scale and estimand its median coverage at 8 donors has median 0.896 over the HEST and ACS cells and 0.899 over the corpus cells (`F2/report_tables/r02_regimeA_grid_ranges.csv`).
- The width ratio of `fix1` to `classical` at 8 donors is 0.554 on ACS by state, 0.585 on LUNG_XENIUM, 0.878 on CCRCC and 0.664 to 0.948 on the corpus tasks (keys `B7.*`). The gain per gene follows the donor-level $R^2_c$ (Spearman over genes -0.63 to -0.99 within each task), not the spot-level Pearson (F2 report, section 6.7).
- The fixed coefficient costs width on some genes: the share of genes where `fix1` is wider than `classical` at 8 donors is 0.30 on CCRCC, 0.32 on INDIANA_KIDNEY and 0.044 on LUNG_XENIUM, read on median widths. On mean widths CCRCC's share is 0.20 (F2 report, sections 6.3 and 7, item 2).
- Below nominal, the coverage shortfall follows how much of the residual sum of squares sits in one donor ($\kappa(e)$, or $G^\ast$), more than skewness. The median Spearman correlation over genes of `fix1`'s coverage with $\kappa(e)$ is -0.556 over the HEST and ACS cells and -0.403 over the corpus cells (keys `B13.rho.*`). On CCRCC 0.98 of genes lie beyond round 9's frontier `kappa_sup` at 8 donors. Crossing the frontier is not by itself a large loss: on kidney Visium every gene lies beyond it and `fix1` covers 0.895 (F2 report, section 6.6). Only 26 of 1722 cells show coverage rising with $\kappa(e)$ (`F3/aggregate/f3_predictions.csv`; F3 report, section 6.7, item 7).

**Limits** (F2 report, section 6.4; final report, section 6.5). Same-sample tuning covers 0.840 at 4 donors against the control's 0.897, and Kluger et al.'s cluster bootstrap 0.7145 (keys `B5.*`). The pairs percentile bootstrap covers 0.771 at 4 donors and 0.982 at 16 (keys `S6-2.*`). Broska and Howes's interval without the small-sample correction covers 0.699 at 4 donors, and with it (`bh_t`) 0.875 (keys `S6.bh.n4`, `S6.bh_t.n4`). The interval without the finite-population factor covers 0.944 against the design target on CCRCC at 8 donors (key `S6-6.CCRCC.n8`). Round 4's PPI++ form forms no interval when one cluster is left unlabelled.

**Regime B, labelling a few spots in every donor, and the design comparison.**
- Round 5's regime B variance is unbiased on the real tasks: median $E(\hat V)/\text{Var}$ 0.998 for every form, coverage 0.8795 to 0.9130 in every cell (F2 report, section 6.5). The under-estimate of 0.76 to 0.80 that F1's toy enumeration found does not appear on the real tasks, and it is tied to the toy's small within-cluster size (F3 report, section 6.7, item 2).
- With the coefficient fixed at 1, regime B covers within 0.0205 of nominal in 30 of 30 cells at $m \ge 6$ (`F3/regimeB/aggregate_v1/box/f3_box_checks.json`).
- Cost-matched at a per-cluster cost of 10, regime B is narrower in 141 of 156 $\theta_3$ comparisons, median width ratio 0.473 (`F3/regimeB/aggregate_v1/regcomp/f3_regcomp_checks.json`), and in 1458 of 1458 for $\mu$ over all spots (keys `F4.mu.n`, `F4.mu.narrow`).
- On ACS by state it is narrower in only 3 of 12, median ratio 1.159 (key `E1.ACS_STATES.*`), and in 0.25 of the 12 pairs at unit cost (`F4/aggregate/f4_acs_summary.json`). The mechanism is the allocation: regime B labels each cluster in proportion to its size while the target weights clusters equally, which inflates its variance by about $\overline{M} \cdot \frac{1}{G}\sum_g 1/M_g$, 2.656 on ACS by state against at most 1.706 on the HEST tasks (`F4/readings/readings_alloc_v1/f4_alloc_summary.json`; final report, section 6.2). Round 11 measured the within-cluster variances and ran equal allocation: the factor stands on ACS by state (2.636 recomputed), and under equal allocation regime B is narrower in 12 of 12, median ratio 0.699 (`docs/round11/README.md`).
- The take-all design lifts CCRCC's coverage at 8 donors from 0.833 to 0.892 at 0.770 of the width (keys `E7.CCRCC.r10_*`), beside round 9's 0.825, 0.885 and 0.779.

**V, regime B with and without a share bound.** No published finite-sample bound on one cluster's share of the design variance was found; the nearest published object is the effective number of clusters $G^\ast$ (`i01/ledger/round10_ledger_decisions.md`, section 4). The theorem's required spots per donor rise from 10 under the bounded column to 100 under the unbounded one on CCRCC, and from 2 to 75 on ACS by state, while the simulated coverage at the chosen $m$ is 0.901 and 0.898 on CCRCC and lies between 0.8865 and 0.904 (bounded) and 0.889 and 0.90425 (unbounded) over every row (keys `V.*`). The share bound decides how many units the theorem needs, not whether the interval covers in these populations.

**The scale question (D5)** (F2 report, section 6.8; `F2/report_tables/r11_scale_diff_uni_v2_n8.csv`, `r11b_scale_diff_ranges.csv`). For $\theta_3$ the normalised scale $\log(1 + 10^4 y/n)$ changes `fix1`'s coverage at 8 donors by -0.0045 to 0.0053 on every task. For $\mu$ it raises it by 0.027 on CCRCC, 0.044 on CCRCC_merged, 0.013 on INDIANA_KIDNEY and 0.030 on bowel Visium. The normalised interval is narrower, median width ratio 0.866 on the corpus and 0.872 with the refitted HEST heads. The shared factor's share of between-donor variance falls on the normalised scale on every task, on CCRCC from 0.650 to 0.338 (keys `F2.pc1.CCRCC.*`).

**Prediction sets for a new donor** (F3 report, sections 6.1 to 6.3).
- HCP at 10 calibration donors with no labelled target spots covers 0.9694 on CCRCC, beside round 3's 0.9692 (keys `F3.A4.CCRCC`, `A4.hcp`).
- The target donor's own full conformal set is narrower than HCP by at least 1.729 on CCRCC and 1.562 on LUNG_XENIUM from 9 labelled spots (`F3/aggregate/t01_map_p103.csv`). On INDIANA_KIDNEY it is 1.049 to 1.072 times the plain within-donor split's width at 9 to 15 spots.
- The adaptive scores buy no width at their own guaranteed coverage: the locally weighted score and CQR are about as wide as the absolute score or wider, and the conformalised negative binomial set is often infinite (`F3/map/i7_aggregate/scores_margins.csv`).
- **The institution axis**, which round 3 could not measure, exists on the corpus. On kidney Visium, donor-level HCP pooled across centers covers 0.9057 at the median center and 0.655 on center S0006, while HCP over centers covers 1.0 at the median (`F3/institution/production/inst_fr8.csv`). S0006, the largest center with 24 donors, is predicted worst by the center-held-out heads in 5 of 6 encoder and scale cells, which round 10 read as center shift (`F4/aggregate/f4_s0006_summary.json`; final report, section 6.3). Round 11 found the cause: the calibration pool without S0006's 24 donors gives the narrowest half-width, and S0006 has a level shift whose removal raises its coverage from 0.6555 to 0.8184 (`docs/round11/README.md`).

**E8, one labelling budget for both purposes** (F3 report, section 6.6; final report, section 6.4). At $\alpha = 0.1$ and $m \ge 9$ labelled spots per donor, the regime B labels also give each labelled donor a valid within-donor set with no further labels. The apparent exceptions at $m = 15$ come from the mean-width rule choosing GHCP, not from the sets. Each guarantee is marginal; joint coverage is not claimed (Dobriban and Lin, arXiv:2303.00203, require multiplicity control for it).

**What the literature says** (`i01/ledger/round10_ledger.md`; `i01/ledger/round10_ledger_decisions.md`). Every formula the paper displays is classical or in print. The estimator is Mickey's (1959), and the exactly unbiased variance for the average over the two halves rests on an identity Nicolas checked and lifted from `[proposed]` (methods note, section 1, item 2). The prediction-set map is a measured comparison, not the first use of the target donor's labels. The small-sample correction to Broska and Howes is Cameron and Miller's and Bell and McCaffrey's. Round 9's theorems stay candidates. The ledger's evidence is under `results/round10/ledger/`.

**Caveats that apply across these findings.**
- The F3 decision file labels regime B's $\mu$ rows $\mu_J$ (the donor mean over spots joined to nuclear morphology, in both regimes). F4's check failed two of its three thresholds, so all 330 regime B $\mu$ units were rerun on all spots; $\mu_J$ applies only to F3's superseded tables, and F3's tables `t10` to `t16b` are not to be quoted for $\mu$ on the HEST and corpus tasks (final report, sections 1 and 7, item 2). The all-spot means equal the committed cluster values within 2.4e-13 (`F4/aggregate/f4_mu_check_populations.csv`).
- The numbers table's earlier-round rows were read from committed files and not rerun. Of its 443 values, 41 were checked against the F2 and F3 reports and the rest only by their selectors resolving to one row (final report, section 8).
- The gate tag `round10-final-runs-F4` (`fad48334`) sits one commit before a fix that cites the files for three claims; the branch head, merged in #39, carries the fix.
- FR4 holds on CCRCC exactly at its threshold and fails there under the mean-width reading. FR6's frontier clause holds under `kappa_star_v1` and not under `kappa_sup` (methods note, section 3, items 1 and 2).

## The expectations and their scores

The masterplan's predictions, as written:

- **P10.1** (scored at F2 and F3). "On CCRCC, INDIANA_KIDNEY and LUNG_XENIUM at 8 labelled donors, the median over genes of the tuned interval's coverage under the level-free variance is 0.02 to 0.05 below the value rounds 5 to 7 reported for the same cell, and the ordering of designs by median width on round 7's matched supported cells at 8 labelled clusters is unchanged." **Refuted.** Part 1 refuted on all three tasks, drops -0.0004, -0.0010 and -0.0077 (`F2/report_tables/r13_p10_1.csv`), since FR1 showed there was no inflation to remove. Part 2 refuted at $p_a = 0.1$, where `D2_rej_t` and `cube_S4b` change order, and held at $p_a = 0.01$, where they are tied in round 7 (`F3/aggregate/t24_balance_p101_part2.csv`).
- **P10.2** (scored at L3). "The ledger finds a published variance estimator for the exactly unbiased split-sample form under simple random sampling without replacement, and finds no published interval with a finite-sample coverage guarantee for the design target at 4 to 16 labelled clusters without a restriction on the population." **Held** (Mickey 1959, section 4, and Sanguiao Sande and Zhang for the single split; `i01/ledger/round10_ledger_decisions.md`, section 7).
- **P10.3** (scored at F3). "At 10 calibration donors and the nominal level of round 5's map, the target donor's own full conformal set becomes narrower in median width than HCP from 9 labelled spots on CCRCC and LUNG_XENIUM, and on INDIANA_KIDNEY its median width stays within 2% of the plain within-donor split's at 9 to 15 labelled spots." **Partly held.** Part 1 held (margins at least 1.729 and 1.562); part 2 refuted (ratios 1.049 to 1.072, `F3/aggregate/t01_map_p103.csv`).

The final-runs brief's predictions are written in full in `i01/final-runs/round10_final_runs_brief.md`, section 5, and the stage predictions in `tracks/final-runs/round10_final_runs_plan.md`, sections 4a, 5.8, 5d.6, 5d.7 and 5e.8, all before their runs. The final report's section 5 scored them as follows, and Nicolas accepted those scores at F2, F3 and F4. No later review scored any of them differently.

| prediction | in short | score |
|---|---|---|
| FR1 (F1) | with round 4's `lin` term, round 5's interval within 1.15 times Williams' form at 8 donors on every HEST task and ACS | held (0.982 to 1.004) |
| F1 anchors | round 5's and round 7's cells reproduce; the corpus prediction file matches round 3 within 0.01; breast ST's gene rule rebuilds kidney's list | held (both anchors exact; -0.0037) |
| FR2 (F2) | median $E(\hat V_w)/\text{Var} \ge 0.95$ in every cell; $\hat V < 0$ in at least 0.05 of draws at 6 donors on CCRCC and INDIANA_KIDNEY | held (0.9937; 0.197 and 0.208, `F2/aggregate/f2_scores.csv`) |
| FR3 (F2) | at 4 donors `fix1`'s RMSE below `classical`'s on every HEST task and ACS | held |
| FR4 (F2) | share of genes with `fix1` wider: at least 0.3 on CCRCC and INDIANA_KIDNEY, at most 0.2 on LUNG_XENIUM; narrower on ACS | held for $\theta_3$ (0.30, 0.32, 0.044; ACS ratio 0.554), at the threshold on CCRCC |
| FR5 (F2) | on CCRCC `fix1`'s coverage at least 0.02 higher on the normalised scale | refuted for $\theta_3$ (-0.0006); for $\mu$ it rose 0.027 |
| FR6 (F2) | kidney Visium beyond the frontier at 16 donors, `fix1` coverage below 0.88 | refuted (0.8924) |
| FR7 (F3) | regime B `fix1` within 0.03 of nominal at every $m \ge 6$; the unbounded column needs more units on every task | held (0.0205; 11 of 11 tasks) |
| FR8 (F3) | kidney Visium at $\alpha = 0.2$: donor-level HCP pooled below 0.75; HCP over centers at least 0.8 | clause 1 refuted (0.9057), clause 2 held (1.0) |
| R10-F3a (F3) | regime B narrower in at least 0.8 of cost-matched comparisons | held (141 of 156) |
| F3 open points 2 to 7 (plan 5d.6) | the toy shortfall, bootstrap arms under other encoders, limits arms on the refitted scale, regime B on the normalised scale, round 9's gene subset, cells where coverage rises with $\kappa(e)$ | 2 refuted, 3 held, 4 partly held, 5 held, 6 held, 7 held |
| F4-1 | all-spot donor means equal the committed $\mu$ rows within 1e-10 | held (2.4e-13 on 60 of 60) |
| F4-2 | on CCRCC the three thresholds of the $\mu$ check hold | refuted (coverage moved 0.012 against 0.01; width ratio 0.0375 relative against 0.02) |
| F4-3 | on ACS regime B is wider only in cost-matched cells, and its cost-matched $m$ is the smallest | refuted (narrower in 0.25 of unit-cost pairs) |
| F4-3b (added before its run) | the allocation factor is larger on ACS than on every HEST task | held (2.656 against at most 1.706) |
| F4-4 | S0006's median absolute residual exceeds every other center's | refuted as written (5 of 6 cells; not on `uni_v2` lognorm, 0.883 against 0.971) |
| F4-5 | E8's $m = 15$ rows come from how sets are selected | held |

Two scorings rest on readings decided after the run, both recorded at F2 (methods note, section 3): FR4 on the median width, and FR6's frontier clause on $\kappa$ of the fixed-coefficient residual against `kappa_sup`. Open point 2's verdict is the aggregate's re-derivation under the plan's rule, since its own output recorded none.

## What was tried and did not work

- **Round 5's estimator** is retired except for the anchors (question E). Its regime B variance and its coverage stand, but the paper's estimator is the fixed coefficient.
- **The exactly unbiased variance alone** as the interval's variance: it is negative in about a fifth of draws at 6 donors, and the interval then covers 0.73 to 0.75 (F2 report, section 6.2). Use $\hat V_w$, or $\max(\hat V, \hat V_w)$.
- **Coefficients fitted on the labelled donors** (round 4's rules (a) and (b), which are one formula on the donor target): coverage 0.840 at 4 donors. Rule (c) sets the coefficient to 0 in every draw at 4 donors and so equals the control (F2 report, section 6.4).
- **Resampling at few donors.** The pairs percentile bootstrap and Kluger et al.'s cluster bootstrap under-cover at 4 donors and over-cover at 16; the wild cluster bootstrap-$t$ with Webb's weights over-covers throughout at 1.17 to 1.79 times `fix1`'s width (`F2/report_tables/r03b_bootstrap_ranges.csv`; F2 report, section 6.1).
- **Round 4's PPI++ form with one unlabelled cluster** forms no interval in any draw (54 cells; F2 report, section 7, item 3).
- **A label-free corpus covariate** (option (c)). The search (107 queries) found no validated label-free substitute for CellViT's nuclear area, and the option was closed when option (b) delivered (F2 report, section 6.9).
- **Leave-one-center-out prediction on brain and kidney Visium**: the median gene's Pearson is near zero, so analyses on the center axis there rest on weak predictions. Breast Xenium's center design had to hold out S0253 and S0254 together, since they share two donors; lung Xenium (3 centers) and breast ST (2) are below the 4-center rule.
- **Regime B's $\mu$ on joined spots.** Regime B's loaders kept only spots joined to nuclear morphology, so its $\mu$ was a different population from the committed all-spot $\mu$ (up to 0.269 relative, `F3/regimeB/aggregate_v1/regcomp/f3_regcomp_checks.json`); every $\mu$ unit was rerun on all spots. The $\mu$ check's coverage threshold of 0.01 was about one Monte Carlo standard error of a difference between two runs, too tight to separate the estimands (final report, section 6.1).
- **Regime B under proportional allocation** loses to regime A on ACS by state. Round 11 ran the equal allocation, which removes the inflation (`docs/round11/README.md`).
- **The conformalised negative binomial set** is narrower only where finite, and it is often infinite: every set is finite in 0.762 of rows on CCRCC and 0.019 on LUNG_XENIUM (F3 report, section 6.2).

## What was presented outside the project

Nothing from round 10 was presented to the advisors or anyone outside the project. Nicolas decided on 6 November that there is no outside contact for now, and question Q1 was deferred to the next advisor deck, whose time is not set. The second advisor meeting stopped before the results of rounds 4 and later (`round5_ppi_track.md`, section 2.1 (at tag `record-full-2026-11`)), and the meeting of 12 October discussed round 6, so the record shows no result the advisors saw that this round changes.

## The open questions of the masterplan, at the close

| question | at the close | for Nicolas? |
|---|---|---|
| E, the estimator | settled at L3: the two-fold cross-fitted form in Mickey's form with $\hat V_w$ primary, confirmed at F2 by the switch rule (0.9937) | no |
| R7-6, the coefficient | settled at L3: fixed at 1, the paper's primary estimator | no |
| P, prediction sets | settled at L3: kept, with the narrowed claims of the ledger decisions, section 3 | no |
| E8, the joint design | settled at F3, when Nicolas adopted the session's recommendation ("For any open decisions, go with your recommendation"): a measured result inside the prediction-set section, not a method, marginal guarantees only, no novelty claimed; F4 found the $m = 15$ rows come from the width rule, which the paper names when it quotes E8 (`i05/final-runs/round10_final_runs_F3_decisions.md`, section 2.3) | settled; he may reopen it |
| V, the share bound | settled at F3 the same way: the unbounded column ($v_0 = 1$) primary, the bounded column conditional with each task's largest share and $G^\ast_B$ beside it, simulated coverage reported as empirical evidence only, the take-all design the answer when one donor dominates (same file, section 2.2). F4's all-spot rerun left the picture unchanged | settled; he may reopen it |
| D5, the scale | the testing is done (F2 report, section 6.8) and both scales are in the numbers table; which scale the paper calls primary was never decided | yes, with David |
| Q1, regime B on a spatial platform and its cost | untouched by the final runs, whose cost comparisons use a cost-model ratio, not a platform's prices; deferred to the next advisor deck | yes, with the advisors |
| Q3, venue and lead result | open; it waits on what the paper contains | yes |
| Which of round 9's theorems the paper keeps (O5) | not decided; they stay candidates | yes |
| DATA, O3, R7-7, R7-5 | decided (7 and 8 November) | no |

## Open threads

- **Draft v1.** Track `paper` never started. Its plan is `tracks/ledger/round10_writing_plan.md`, whose S3 and S5 paragraphs on E8 and V and whose section 5 ("Decisions the text waits on") predate the L3 answers and the F3 decisions, which win. The plan's section 4 lists the sources to read before the paper cites them.
- **From the final report, section 7.** The findings not in the numbers table: B2 and D7 have no number, B9 belongs to a supplement, D12's share of genes where the pooled head beats a constant (0.46 to 0.64) and round 9's E1 box numbers now have selectors (`results/round11/closeout/b6/stored_v1/b6_summary.json`), and B14 and E8's literature status are documents. E4's cell count of 1336 is a filtered count of a 1526-row file. Four F4 jobs ran on the `spill` partition and are of record.
- **From the final report, section 8.** The earlier-round rows of the numbers table were not rerun. 402 table values were checked only by their selectors. Jobs that wrote no provenance file are not in `results/round10/final_runs/job_ledger.csv`; round 11 counted 56 of them (`results/round11/closeout/b7/ledger_v2/b7_summary.json`).
- **The full texts of papers saved outside the repository by round 9's sessions** were not deleted, since the store that holds them was not reachable from the final-runs sessions (plan, section 2).

## Documents kept

- `masterplan.md`: the plan of record, with the predictions P10.1 to P10.3 as written and the open questions.
- `round10_methods_note.md`: the L3 answers, the F1 data decisions and the F2 settled deviations, word for word, which define how the final runs were designed and scored.
- `00_prep/round10_reframing.md`: Nicolas's reframing of 6 November, quoted, and the reading of it as an applied paper `[proposed]`.
- `00_prep/round10_findings_survey.md`: what rounds 1 to 9 established, by question, with the seventeen claims later found in print and the outline of the applied paper.
- `i01/ledger/round10_ledger_brief.md` and `i01/ledger/round10_ledger_L0_scope.md`: the ledger's design, the paper's sections and the criteria for a corpus task.
- `i01/ledger/round10_ledger.md`: the methods ledger, every result of the outline with its source, read level and code.
- `i01/ledger/round10_ledger_decisions.md`: question E decided, the recommendations, the literature on V and D5, P10.2 scored.
- `tracks/ledger/round10_writing_plan.md`: the plan for draft v1.
- `i01/final-runs/round10_final_runs_brief.md`: the final runs' design and its predictions FR1 to FR8, written before any run.
- `tracks/final-runs/round10_final_runs_plan.md`: the methods of every stage and the stage predictions; the reports cite it by section, and the scripts and provenance files under `results/round10/final_runs/` cite it.
- `i02/final-runs/round10_final_runs_F1_report.md`, `i03/final-runs/round10_final_runs_F2_report.md`, `i04/final-runs/round10_final_runs_F3_report.md`: the gate reports, with the full tables the final report summarises.
- `i05/final-runs/round10_final_runs_F3_decisions.md`: the decisions on V and E8 and the definition of $\mu_J$.
- `i05/final-runs/round10_final_runs_report.md`: the final report and the guide to the numbers table.
