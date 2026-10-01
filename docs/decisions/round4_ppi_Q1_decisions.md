# Round 4, the PPI track, the Q1 decision memo

1 October 2026. Written by the oversight chat after reading `docs/round4_ppi_Q1_report.md` at tag `round4-ppi-Q1` (`768b43a`) and the follow-up commit `2385298`, and checking its numbers against the files it names. Nicolas hands this to the PPI session in full. Transcribe it into `docs/round4_ppi_plan.md` as section 13 before anything in it runs. Interval 2 (Q2 and Q3, ending at the Q3 gate) starts when the transcription is committed.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. This track's gates are Q1, Q3 and Q5. Contact with anyone outside the project is never the session's decision.

---

## 1. Acceptance

The Q1 report is accepted. Every number I checked reads back from `q1_report_numbers.csv`, `q1_acceptance.csv` and `q1_permuted_lambda.csv` as quoted, including the Q1.1 to Q1.6 outcomes, the $r = 0$ band fractions, the design-arm coverages and the widths. I also read the merged table `q1_sim_coverage.csv.gz` directly for two things the report does not say.

- The $\theta_3$ spot-weighted shortfall is confined to that estimand. At $r = 0$ the band holds in 0.82 to 0.87 of the cells for the mean and for $\theta_3$ donor-weighted under the cross-fitted CR2 interval, and in 0.23 of the $\theta_3$ spot-weighted cells.
- It is the reference distribution and nothing else. For the classical CR1 interval on $\theta_3$ spot-weighted, the median of bias over empirical sd is at most 0.007 in every $(\rho, m)$ cell and the median of empirical sd over root mean estimated variance is 0.99 to 1.00. The shortfall decays slowly with $G_L$ (median coverage 0.821 at $G_L = 4$ and 0.863 at $G_L = 20$, at $\rho = 0.1$ and $m = 5000$), which is what heavy-tailed donor contributions do to a $t$ reference. The report's diagnosis stands, and section 4 below acts on it.

Predictions scored as the report scores them, with one note on Q1.4. The Welch-Satterthwaite combination adds the unlabelled term's degrees of freedom to the labelled term's, so the combined degrees of freedom exceed $n_L - 1$ and the critical value falls. My prediction had the sign wrong. It is dropped from every later stage.

The pull request. The report says the pull request's head is `2385298`, but no pull request beyond #1 existed on GitHub this morning. Nicolas has since created a new token with pull-request read and write access and updated it in the session's credential settings. Before any interval-2 work, open the Q1 pull request from `round4-ppi` into `main` with the new token, titled "Round 4 PPI track, gate Q1", as plan section 10 specifies, and tell Nicolas its number in chat. Do not merge it; Nicolas merges it with a merge commit. Record in the Q3 report why the first attempt produced no pull request.

## 2. The estimator, decided provisionally

Section 6.3 of the report is adopted as the working estimator for Q2 and Q3, with one addition, and the final choice is made at the Q3 gate.

- **Superpopulation target.** The complement form, cross-fitted $\lambda$ (rule c), CR1 with a $t_{n_L - 2}$ reference. No finite-population correction. No Welch-Satterthwaite combination.
- **Design-based target.** The textbook form with the finite-population correction and a $t_{n_L - 1}$ reference, cross-fitted $\lambda$.
- **No bootstrap** is a candidate for the interval. The three bootstraps are dropped from Q2 onward, except as section 4 says.

**The addition, rule (d), cross-fitted with a pre-test.** Rule (c) fails the $r = 0$ acceptance for a structural reason the report gives correctly. Each half's $\lambda$ is clipped at zero, so the average of the two is zero only when both are, and the median over cells is 0.15 with a width ratio of 1.32 at $G_L = 4$. The same mechanism puts the permuted predictor's cross-fitted $\lambda$ at exactly 0.5 in every donor-weighted cell of the real-data check. A paper cannot carry a tuning rule that gives a useless predictor a positive weight more often than not. Rule (d) is rule (c) with two changes.

1. Each half's $\lambda$ is set to zero unless the half's unclipped estimate exceeds its own standard error, with the standard error taken from the regression of the half's donor rectifier contributions on its donor prediction contributions (the slope's ordinary standard error over the half's donors, which needs at least three donors in the half). Otherwise the half's $\lambda$ is the clipped estimate, as in rule (c). Run two thresholds, the estimate exceeding one standard error (d1) and two (d2).
2. When $n_L < 6$ a half has fewer than three donors, and $\lambda = 0$ throughout, so the estimator is classical. At $n_L = 4$ rule (c) already gives a median width ratio of 1.009 for $r > 0$, so nothing is lost.

The pre-test is a heuristic for a well-posed problem, and the theory document should say why it is needed. When the predictor's cluster-level $R^2$ is near zero, $\lambda$ minimises a function that is nearly flat, so it is unidentified, and its value is nearly harmless for the labelled term because $\text{Var}(u_g - \lambda p_g) \approx \text{Var}(u_g)$ when $\text{Var}(p_g)$ is small. The permuted predictor in the real-data check is this case, with sd$(t)/$sd$(\hat t)$ at a median of 3.9 for $\theta_2$ and 10.3 for $\theta_3$. The pre-test makes the reported $\lambda$ zero where it is unidentified and leaves the estimator's variance alone where it is not. This is a corollary of the gain theorem and belongs in `docs/round4_ppi_theory.md` under the $\lambda$ corollary.

Q2 and Q3 compute every row under rules (c), (d1) and (d2); the extra cost is three scalars per cell. Every table carries `lambda_rule`. The Q3 report proposes which of the three the paper uses, and the estimator definition is finalised in the Q3 memo.

## 3. A Q1 supplement, run inside interval 2 and reported with Q3

One unit, `Q1b`, fanned out by $G_L$ (five sub-agents), run on Longleaf through Slurm under section 7, with the Q1 tables left as they are and the new tables beside them under `results/round4/ppi/Q1_estimator/q1b/`. It uses the Q1 generator and the Q1 code paths with three additions, and it is capped at one and a half days of the session's time.

**Grid.** $G_L \in \{4, 6, 8, 12, 20\}$, $G_U = 20$, $m \in \{200, 1000\}$, $\rho \in \{0.1, 0.3, 0.5\}$, $r \in \{0, 0.5, 0.8\}$, both estimands and populations, both targets, 2,000 replicates per cell.

**Addition 1, rule (d).** Rules (c), (d1) and (d2), with CR1 $t$ and the textbook form.

**Addition 2, unequal donor sizes, so that CR2 can be judged** (escalation 4, accepted). Beside the equal-size arm, an arm in which donor $g$ has $m_g = m \cdot s_g$ spots, where $s_1, \dots, s_{24}$ are CCRCC's 24 donors' spot counts divided by their mean, read from the task definition and recorded in the config, assigned to donors by `zlib.crc32` of the donor index and recycled when $G > 24$. CR1 with $t_{G_L - 1}$ and CR2 with Bell and McCaffrey degrees of freedom on both arms.

**Addition 3, the wild cluster bootstrap-$t$ for the skewed estimand** (section 4). On the $\theta_3$ spot-weighted cells only, superpopulation target, classical and rule (c), the wild cluster bootstrap-$t$ of Cameron, Gelbach and Miller (2008) on the labelled donors' influence contributions, 500 draws, with Rademacher weights and with Mammen's two-point weights, each as its own interval name. The unlabelled term is held fixed.

**Predictions, written here before Q1b runs.**

- Q1b.1. At $r = 0$, rules (d1) and (d2) give a median $\lambda$ of 0 in every cell and a median width ratio within 0.02 of 1 at every $n_L \ge 6$.
- Q1b.2. At $r \ge 0.5$ and $n_L \ge 8$, rule (d1)'s median width ratio is within 0.02 of rule (c)'s; rule (d2) gives up more, by 0.02 to 0.05.
- Q1b.3. With unequal sizes, CR1 at $G_L = 4$ loses 0.02 to 0.04 of coverage against the equal-size arm, and CR2 with Satterthwaite recovers at least half of that; at $G_L \ge 8$ CR1 and CR2 are within 0.01.
- Q1b.4. On $\theta_3$ spot-weighted at $\rho = 0.1$, the wild bootstrap-$t$ with Mammen weights covers at least 0.88 at every $G_L \ge 6$, and the Rademacher version sits between it and the CR1 $t$ interval.

**The real-data permuted check**, rerun under rules (d1) and (d2) on the same 50 genes and 200 draws, into `q1_permuted_lambda_d.csv`, with the prediction that the median $\lambda$ is 0 in every donor-weighted cell and below 0.1 in every spot-weighted cell. Extend it to all genes only if that costs under two hours.

## 4. The $\theta_3$ spot-weighted reference, and the paper's primary estimand

The donor-weighted population is the paper's primary estimand for every real-data table from Q2 on, because its target population is patients, its unit is the donor, and its interval covers at nominal in Q1 (classical minimum 0.8815). The spot-weighted slope is reported in every table as before, with the Q1 finding stated beside it, that with donor-level covariate variation its donor contributions are products of donor effects and the $t$ reference under-covers by three to five points even at twenty donors. Q1b's addition 3 measures whether the wild cluster bootstrap closes that, and the Q3 memo decides whether it becomes the spot-weighted interval in Q4's tables.

## 5. The Q2 theorem and its simulation check (plan section 8 items 3 and 4)

Both corrections flagged in plan section 8 are adopted for `docs/round4_ppi_theory.md`.

- The gain theorem's limit carries the unlabelled term. As $m$ grows the ratio tends to $\sigma_{u,r}^2/\sigma_u^2 + n_L V_U/\sigma_u^2$ with $V_U = \lambda^2\,\text{Var}(p_g)/G_U$, and it equals $1 - R^2_{\text{cluster}}$ only as $G_U/n_L \to \infty$. State the theorem for the labelled term, and state the full ratio with the $G_U$ term beside it.
- Under $\hat y = y - a - \epsilon$, the rectifier's cluster component is $(1 - \lambda)u_g + \lambda a_g$, and the endpoint at the optimal $\lambda$ is unchanged.

**A simulation check of the theorem**, as a sixth unit of Q2, with the Q1 generator and the Q1 code, run on Longleaf through Slurm under section 7, capped at half a day. Grid $G_L \in \{6, 12\}$, $G_U \in \{20, 100\}$, $m \in \{200, 5000\}$, $\rho = 0.3$, $r = 0.5$, and $\sigma_a^2/\sigma_u^2 \in \{0.25, 1, 4\}$, which sets $R^2_{\text{cluster}} = 1/(1 + \sigma_a^2/\sigma_u^2)$ to 0.8, 0.5 and 0.2; 2,000 replicates; rule (c), donor-weighted mean, superpopulation target. Record the empirical PPI-to-classical variance ratio, $1 - R^2_{\text{cluster}}$ from the parameters, and the theorem's full ratio with the $G_U$ term, in `results/round4/ppi/Q2_theory/q2_sim_theorem.csv`. Prediction Q2.7, written now: at $m = 5000$ and $G_U = 100$ the empirical ratio is within 0.05 of $1 - R^2_{\text{cluster}}$ in all three cells, and at $G_U = 20$ it is within 0.05 of the full ratio and above $1 - R^2_{\text{cluster}}$ by at least the $G_U$ term's size.

Everything else in Q2 and Q3 runs as the instruction document and addendum 1 say, with rules (c), (d1) and (d2) on every row.

## 6. ACS, decided

Option 2 of escalation 3, already done. Nicolas ran `code/scripts/round4_ppi_acs_pums2018_fetch.py` on his own machine and has given the session the output directory. Nothing is downloaded again.

1. Read `raw_manifest.json` and `fetch_info.json` in that directory and record them, with the directory's path on Nicolas's machine, in the Q3 report.
2. Copy the directory to `results/round4/ppi/Q0_setup/acs_pums2018/` in the Longleaf project tree. Verify every file's md5 on Longleaf against `raw_manifest.json` before anything reads it, and record the comparison in `acs_pums2018_transfer_check.csv`. A single mismatch stops the ACS unit and goes to escalations. Stamp the directory.
3. Run `round4_ppi_acs_pums2018_analyze.py` on Longleaf through Slurm against that copy, with 32 GB of memory, and commit `acs_pums2018_inventory.json` and `acs_pums_task_def.json` as addendum 1 section 4 specifies. The raw files are not committed.

The ACS units of Q2 and Q4 run on Longleaf against the same copy. The previously queued job script, whose stamp carried the lead's frame id, is not resubmitted. The conformal track reads the Longleaf copy in its C3.

## 7. Where interval 2 runs

Every job in interval 2 runs on Longleaf through Slurm, with walls sized from a sibling's `sacct` and never a blanket limit. Nicolas's section-12 decisions applied to the Q1 work they named and do not carry forward. Nothing runs locally unless Nicolas asks for that specific task, in chat; each such request is recorded as a numbered extension of plan section 12 before the task runs.

If a Longleaf job has not started four hours after submission, the session tells Nicolas in chat what the job needs (inputs and their sizes, memory, expected runtime and the queue state) and keeps waiting. It does not move the job, harvest its inputs or propose running it locally unless Nicolas asks. Work that does not depend on the waiting job continues meanwhile, under the gate rule.

## 8. Procedural points

1. **Sub-agent frame ids.** The proposed fix is adopted. Every brief states the sub-agent's own frame id, and the lead checks the stamp on each hand-back before merge.
2. **`docs/WAYS_OF_WORKING.md`.** Both proposed edits are accepted; the oversight chat applies them on `main` between intervals.
3. **B1's check 4** (escalation 5). The instruction's wording was mine and did not describe B1's committed check. B1's file stands as it is; nothing to do.
4. **The ten unresolved claims** in the pre-round-3 documents stay a round-5 item.
5. **`docs/round4_ppi_estimator_definition.md`** does not render in Markdown previews because its display equations open and close `$$` inside running lines. Put each `$$` on a line of its own with the formula on the line between, in the next commit, and do the same in `docs/round4_ppi_theory.md` from the start.
6. **The Q0 `ppi_py` ACS file** is used for nothing clustered. It stays where it is.

## 9. What the Q3 report decides

Besides the instruction's Q2 and Q3 content, the Q3 report carries Q1b and the theorem check, scores Q1b.1 to Q1b.4 and Q2.7 beside Q2.1 to Q3.4, and proposes the final $\lambda$ rule, the CR1 or CR2 choice, and the spot-weighted interval. The Q3 memo finalises the estimator definition. Report and wait.
