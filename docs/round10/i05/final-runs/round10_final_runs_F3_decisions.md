# Round 10, track `final-runs`, decisions at gate F3

*Written on 14 November 2026 by the eighth session of track `final-runs` (frame `bdb361de-6630-44e8-b0f8-8bd63dae9ad3`). It records Nicolas's reply, given in the session, to the F3 report `docs/round10/i04/final-runs/round10_final_runs_F3_report.md` (tag `round10-final-runs-F3`, commit `9183ab32`). Item numbers in brackets are those of the report's section 7, and "section 8" is the report's list of what was not checked. Paths that begin `aggregate/` are relative to `results/round10/final_runs/F3/`.*

## 1. The reply

Nicolas, 14 November, in the session: "Gate F3 accepted. For any open decisions, go with your recommendation."

This session reads the reply in three parts. The scores of the report's section 5 stand as reported. The decisions the gate left open are the $\mu$ question [1], V (report section 6.5) and E8 (brief, F3 item 4). Each is taken on this session's recommendation, written in section 2 with its grounds. The brief (section 9) names V and E8 as Nicolas's decisions, so the record should show that he made them by adopting these recommendations, and that he may reopen any of them. The rule of the F2 reply still holds. Settled deviations are recorded as decided in section 3, and points that further analysis can resolve go to F4 as work in section 4.

## 2. Decisions taken on the session's recommendation

### 2.1 The regime B $\mu$ [1]

**What the code shows, which corrects the report's reading.** In `code/scripts/round10_final_runs_f3_regcomp.py`, `run_cell` gives both regimes one object `T`, built by `F2.load` from the spots joined to nuclear morphology, and scores both against the same truth `T["theta_full"]`. Regime A (`regimeA_fix1` and `TL.estimate`) and regime B (`E.regime_b_formC`) therefore estimate the same quantity, the donor mean over joined spots, written $\mu_J$ here. The regcomp $\mu$ rows are a valid comparison of the two regimes on $\mu_J$. They differ from the estimand of record, the donor mean over all of a donor's spots (F2's cluster values and round 9's population), and so from F2's regime A $\mu$ rows. The report's section 7, item 1 and the F3 aggregate read these rows as a comparison of two estimands. That reading is corrected here, and the F4 report carries the correction.

The same holds outside regcomp. `code/scripts/round10_final_runs_f3_box.py` reads each population through `F2.load`, as its docstring says, so the box requirements and the regime B coverage cells for $\mu$ on the HEST and corpus tasks are also $\mu_J$. These carry V (section 2.2) and FR7. ACS by state is unaffected, since its cluster-value check passes (`regimeB/aggregate_v1/regcomp/f3_regcomp_checks.json`).

**Decision.** The report's second option, extended to every output it touches. Every regime B $\mu$ output on the HEST and corpus tasks is defined on joined spots in both regimes and is labelled $\mu_J$ wherever it is reported. No all-spot production rerun is started now. F4 runs a check (section 4, item 1) with three parts. It recomputes the all-spot donor mean against the committed cluster values, which section 8 left unchecked. It tabulates $\mu - \mu_J$ for each population and gene against the between-donor standard deviation. It reruns one anchored population, CCRCC `uni_v2` $\log(1 + y)$, on all spots for the regcomp $\mu$ cells and the box $\mu$ unit, and compares coverage, width ratio and required $m$ with the $\mu_J$ rows. The thresholds are written into F4's plan before the run. If any of the three quantities moves beyond its threshold, the $\mu$ units are rerun on all spots in F4 and the report says so.

**Why.** A comparison of designs is a statement about how a design behaves on a finite population, and $\mu_J$ is a finite population with a stated definition. The committed rows already compare the two regimes on that population, so this option needs no new production. Rerunning the regcomp $\mu$ third of the 806 units and the box units would cost a production wave, and the check answers the same question on one population first. What the paper must not do is set regime A's all-spot $\mu$ beside regime B's $\mu_J$ as if they were one estimand, and the label prevents that.

### 2.2 V

**Evidence** (report section 6.5, `aggregate/t16b_V_side_by_side.csv`). In every row of the table, which covers every task, encoder, scale and $\lambda$, the design simulation's coverage of the regime B interval is near 0.90 both at the bounded $m$ and at the unbounded $m$. The median coverage per row lies between 0.8865 and 0.904 at the bounded $m$ and between 0.889 and 0.9035 at the unbounded $m$. Coverage stays near 0.90 at every $m$ of the grid from 3 to 500, with the lowest single value 0.88. The unbounded column asks for many more units, for example 100 against 10 on CCRCC `uni_v2` $\log(1 + y)$ with $\lambda = 0$, and 75 against 2 on ACS by state. Coverage does not track $G^\ast_B$, and the Spearman correlations in both columns are close to zero. The share bound therefore decides how many units the theorem needs, not whether the interval covers in these populations. The bounded column's $v_0$ is also the population's own largest share. A user cannot know it before sampling, and the literature gives no rule for choosing it (ledger decisions, section 4).

**Decision.** The ledger's recommendation, now made on F3's evidence. The paper states regime B's guarantee with the unbounded column ($v_0 = 1$) as primary. The bounded column is reported as conditional on the share bound, with each task's observed largest share and $G^\ast_B$ printed beside the $v_0$ used. The simulation's coverage at every $m$ is reported as empirical evidence, with no finite-sample claim beyond the theorem. The take-all design stays the paper's answer when one donor dominates. On the HEST and corpus tasks these numbers are for $\mu_J$ (section 2.1) unless F4's check finds otherwise.

### 2.3 E8

**Evidence** (report section 6.6, `aggregate/t31_e8_on_grid_by_m.csv`, `aggregate/t30_e8_row_counts.csv`). At $\alpha = 0.1$ a within-donor set needs $o + 1 \ge 1/\alpha$ labelled target spots. With $m$ labelled spots per donor for regime B, at every $m$ from 9 upward except 15, the narrowest valid set for a labelled donor is built from that donor's own $m$ labels in every row, so it needs no further labels. At $m = 3$ and 5 no such set is finite, and the narrowest valid set needs labelled calibration donors. Regime B's fixed-coefficient width over the classical width at $o = m$ ranges from near one on CCRCC to 0.595 on ACS by state (report, section 6.6). Each guarantee is marginal. Joint coverage of the interval and the set is not claimed, because Dobriban and Lin (arXiv:2303.00203) require multiplicity control for it.

**Decision.** E8 stays in the paper as a measured result inside the prediction-set section, not as a method. The result is that at least 9 labelled spots per donor at $\alpha = 0.1$ let the regime B labels also give each labelled donor a valid within-donor set with no further labelling. Each guarantee is stated as marginal, and joint coverage is not claimed. Whether anything about it is new is not the session's decision, and no novelty is claimed. E8 is not developed further. Before any E8 number is quoted, F4 examines the rows at $m = 15$ (section 4, item 4).

## 3. Settled deviations, recorded as decided for the rest of round 10

1. **Item 7's check wrote outside its directory** [2]. The tables `round3_a4_scores.py` wrote under the project tree were used once by the comparator and removed on Nicolas's instruction on 14 November. Later calls pass that script a path relative to the project root.
2. **The two scripts beyond the plan's list** [3], `round10_final_runs_f3_map_scores_aggregate.py` and `round10_final_runs_f3_e8_joint.py`, are part of the record as committed.
3. **The balance aggregate's two faults** [4] are fixed in `bb2abf50` and `3c1de525`, and the third run's tables are of record.
4. **The E8 anchor's criterion** [5] of 1e-12, in place of an exact zero, stands.
5. **The ten regcomp units that ended at their time limit** [6] stay in `F3/regimeB/_failed_attempts/`, and their resubmissions are of record.
6. **The raised sub-agent caps** [7] are recorded.
7. **The stopped Designs sub-agent** [9]. Its `RESUME.md` stays unfinalised, the lead's aggregate is of record, and no later stage reads that file.
8. **The sixth session's escalations** [10] stand as listed in the plan.
9. **Open point 2's verdict** is the aggregate's re-derivation under the plan's rule (refuted), since its item output recorded none.
10. **Jobs that wrote no `PROVENANCE.txt`** (report sections 2 and 8) are listed in the per-track CSVs on Longleaf and not in `job_ledger.csv`.

## 4. Open points carried to F4

Each can be resolved by further analysis. F4 plans them beside the final report's methods and scores them in the F4 report.

1. **The $\mu$ check** of section 2.1, with its thresholds written before the run.
2. **Regime B is wider than regime A on ACS by state** [8], in 9 of 12 comparisons with median ratio 1.159, the reverse of the HEST tasks. Explain it, listing first every variable that differs between the arms there.
3. **FR8's lowest center**, S0006 at coverage 0.655 with four donors (report section 6.3 and section 8). Examine it beyond its table.
4. **E8 at $m = 15$.** It is the only $m$ from 9 upward where the overall narrowest set needs extra labels in some rows (share up to 0.5). In four rows (CCRCC `resnet50` `norm_refit` and kidney Visium `hoptimus0` `lognorm`, each under $\theta_2$ and $\theta_3$), the set needing no further labels is narrower than the reported overall narrowest set, and kidney Visium `lognorm` shows negative median differences (`aggregate/t31_e8_on_grid_by_m.csv`). Find out how the overall set is selected there before quoting it.
5. **The regcomp $\mu$ rows** that the F3 aggregate excludes are brought back into F4's tables under the label $\mu_J$, after the check of item 1.

## 5. How the work goes on

Nicolas's rule of 10 November keeps the session that ran a gate to bookkeeping after it. The eighth session did not run F3, so after this file it writes F4's methods into the plan before any job, with the open points of section 4, and then runs F4. F4 is the final stage. The report goes to `docs/round10/i05/final-runs/round10_final_runs_report.md` with the table that maps each number the paper quotes to its file, the tag is `round10-final-runs-F4`, and one pull request goes into `main`. Which scale the paper calls primary (D5) is still Nicolas's decision with David, so the final report presents both scales.
