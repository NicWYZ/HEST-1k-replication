# Round 7, the inference track, decisions at the S2 gate

14 October 2026. Written by the oversight chat for the execution session of the inference track, after reviewing the S2 report (`docs/round07/i01/ppi/round07_ppi_S2_report.md`, pull request #29, tag `round7-ppi-S2`). This memo opens interval i02. Commit it unchanged at this path on your branch as the first commit of i02. Nicolas merges pull request #29 before your next push.

**Revisions**
- 14 October 2026. First version.
- 14 October 2026, before handover. Revised after an independent check. The disagreement with round 5 on $\theta_2$ is settled from the files (section 3), so the replay of S2b is replaced by a recount. The 19 lung cells, the cap rule of S3's probabilities, the `apx_size` reading, the small-sample variants of Broska and Howes, the defensive mixture and the S3 variance were corrected or made precise.

**What was read and checked.** The whole report, sections 1.8, 1.9 and 2.1 of the theory document (`docs/round07/tracks/ppi/round07_ppi_theory.md`), the merged tables and the numbers files, and round 5's `rej_t` and its coverage tally. These were recomputed from the files on the branch.
- In `results/round7/ppi/S1_weighting/_merged/s1_masking_diag.csv` there are 1336 D2 rows. 225 have a cluster with $\hat\pi_g = 0$ (51 `CCRCC`, 47 `CCRCC_merged`, 33 `INDIANA_KIDNEY`, 94 `LUNG_XENIUM`, none on census) and 665 have a pair with $\hat\pi_{gh} = 0$. All 225 rest on $R = 100{,}000$ simulated draws.
- In `results/round7/ppi/S2_comparators/_merged/s2_masking_grid.csv`, the median over cells of Broska and Howes's design-target coverage under D0 is 0.707 at $n_L = 4$, rising to 0.941 at 16, and 0.698 to 0.724 per tissue task at $n_L = 4$. Kluger et al.'s cluster bootstrap covers the superpopulation target at a median of 0.624 (uniform) and 0.618 (score-mixed) at $n_L = 4$.
- The join of `rej_t` with round 5 (`results/round7/ppi/_i01_numbers_r3/i01_rej_t_vs_round5.csv`) against the share of draws with an interval formed (`share_formed_median` in `results/round7/ppi/S1_weighting/_merged/s1_masking_grid.csv`). Section 3 gives what this showed.

**The gate rule** is section 2 of `docs/EXECUTION_RULES.md`, in the wording Nicolas approved. Nothing of S2b, S3 or S4 starts before this memo, and nothing of S5 starts before the S4 memo.

**Standing rules.** Your track started before `docs/EXECUTION_RULES.md` existed. From this memo on, the track follows that file, at its revision of 14 October, wherever your instruction does not say otherwise. Read it in full.

## 1. Acceptance

The S2 gate is accepted. Exit items 1, 3, 4 and 5 are met. For exit item 2 the synthetic test does not pass in full, and the report says which cells fail and why, which the exit item allows. Theory section 1.9 gives the mechanism with exact pair probabilities. The report scores every prediction plainly, runs a draw-count diagnostic before trusting its own first reading of the simulation bias, and raises the disagreement with round 5 rather than explaining it away. Nicolas can merge pull request #29.

## 2. What S0 to S2 establish for the paper

1. **Weighting under rejective selection is a negative result, with a mechanism the project can state.** Rejective balance at a small acceptance probability gives some clusters an inclusion probability that is zero or nearly zero. A $\hat\pi_g = 0$ from 100,000 draws means $\pi_g$ is below about $3 \times 10^{-5}$ at 95% confidence. A weight of $1/\pi_g$ on such a cluster is unusable, so in practice this is the same failure as a true zero. Rejective balance also gives many pairs $\pi_{gh} = 0$, which removes terms from the Sen-Yates-Grundy form and biases it down. Your section 5, expectation 1, left 20 of the 156 cells with a biased $\hat\theta_{\mathrm{HT}}$ unexplained. They are explained.
   - Of the 880 supported cells, 51 have a share of genes with standardised bias above 3 that exceeds 0.1, and 50 of them have a $\hat\pi_g = 0$. The other is `CCRCC`, permuted arm, $\theta_2$, `pcF2`, $n_L = 8$, $p_a = 0.1$, whose smallest $\hat\pi_g$ is $3 \times 10^{-5}$ times $n_L/G$.
   - The remaining 19 cells are `LUNG_XENIUM` $\theta_2$ at $n_L = 12$ and $p_a = 0.01$, all unsupported. There $n_L$ exceeds the 9 valid clusters, so every draw labels every valid cluster, $\hat\pi_g = 1$ for each, and the estimate equals $\theta$. The share of genes with standardised bias above 3 is an artefact of a variance of zero, and the classical mean shows it too. List these cells as degenerate in the S4 report, as round 5 skipped cells where $n_L$ exceeds the valid clusters.

   The weighted intervals with simulated pair probabilities have long lower tails of coverage (minimum 0.42 to 0.55) and are no narrower than `rej_t` at the median. So `rej_t` stays D2's interval, and the paper reports the weighting as what fails under this design and why.
2. **Design-based weighting needs inclusion probabilities bounded away from zero.** S3's design gives that by construction (section 5, S3 item 1). Among the weighted intervals under D2, the Hájek interval with `apx_size` had the best coverage (median 0.893, minimum 0.792). Its approximate $\pi_{gh}$ are built from the $\hat\pi_g$ and are never zero. In simulation it overstates the variance, with a median ratio of estimated to empirical variance of 1.51 to 1.73 (`results/round7/ppi/_i01_numbers_r3/s1_report_numbers.csv`), so part of its coverage is conservatism.
3. **The comparators from the literature under-cover at few clusters, for either target.** Broska and Howes cover the design target at a median of 0.707 at $n_L = 4$, and Kluger et al.'s bootstrap covers the superpopulation target at 0.62. Round 5's superpopulation interval is the only one near nominal for the superpopulation target at every $n_L$. For the design target Broska and Howes become conservative as $n_L/G$ grows, by less than the factor $\rho_{\mathrm{BH}}$ of theory section 2.1 suggests (S2.2 refuted).
4. **That comparison is not yet fair enough for the paper.** At $n_L = 4$ a large part of Broska and Howes's shortfall comes from the normal quantile and the divisor $n$. Replacing both with $t_{n_L-1}$ and $n_L - 1$ would widen the interval by at most
$$
\frac{t_{3,\,0.95}}{z_{0.95}}\sqrt{\frac{4}{3}} = \frac{2.353}{1.645} \times 1.155 \approx 1.65,
$$
and a referee will ask for that change. So the paper compares against the corrected interval as well as the published one. Whatever advantage the paper's intervals keep against the corrected interval comes from the finite-population factor and from the factor $\rho_{\mathrm{BH}}$, and that is what the paper can claim in this regime, beside its design results. S2b item 3 runs the corrected interval.
5. **Independent Bernoulli designs are awkward at few clusters.** Under Kluger et al.'s design up to 0.098 of draws label fewer than two clusters, the bootstrap drops up to 0.123 of its replicates, and the Horvitz-Thompson interval with the Poisson variance is conservative at $n_L = 4$ (0.957). This supports fixed-size designs for the paper's regime.
6. **For $\theta_2$, `rej_t` often forms no interval at small $n_L$** (section 3). Every coverage of $\theta_2$ in the paper is reported with the share of draws that formed an interval beside it.

## 3. Escalation 12, the disagreement with round 5 on $\theta_2$

Your hypothesis was that round 5 fell back to the last of 2,000 candidates where round 7 scans on. Round 5's own record contradicts it. The E4b script, `code/scripts/round5_ppi_e4b_rejective.py`, says in its docstring that a column with no accepted candidate continues past 2,000 and that no draw falls back. Its diagnostics, `results/round5/ppi/E4b_rejective/e4b_d2_diagnostics.csv`, record `n_beyond_first_batch` of at most 1 over all 1,536 rows. The fallback of `d2_select` belongs to E4, not E4b.

The difference is in how coverage is counted when no interval is formed. For $\theta_2$ the number of valid labelled clusters $n_v$ varies from draw to draw, and `rej_t` in `code/scripts/round5_ppi_balance.py` sets the variance to missing when its residual degrees of freedom $n_v - k - 1$ fall below 2. Round 5 averaged coverage over all draws, so a draw with no interval counted as a miss. Round 7 averages coverage over the draws that formed one. The files bear this out.
- In the Indiana cell (`uni_v2`, `pcF2`, $p_a = 0.1$, $n_L = 6$), round 7's coverage is 0.882591 and its share of draws with an interval is 0.741. Their product is 0.654, round 5's value.
- All 157 $\theta_2$ cells where the rounds differ by more than 0.03 have a share formed below 1, and the median absolute difference between round 7's coverage times its share formed and round 5's coverage is 0.0032. The other 323 $\theta_2$ cells have a share formed of at least 0.9825.
- The draws are the same. The median thresholds of every matched $\theta_2$ cell outside `LUNG_XENIUM` are equal, and the share of genes with standardised bias above 3 for the classical mean agrees within 0.02 in the differing cells of `CCRCC`, `CCRCC_merged` and `INDIANA_KIDNEY`.
- The share formed among the differing cells has a median of 0.434 for `INDIANA_KIDNEY` at $n_L = 4$, 0.875 at $n_L = 6$, and 0.109 and 0.522 for `LUNG_XENIUM` at $n_L = 4$ and 6.

Neither code is wrong. They answer different questions. Round 7's number is the coverage given that an interval was formed, and it hides that `rej_t` forms none in a quarter of Indiana's draws at $n_L = 6$ and in most of lung's at $n_L = 4$. A user who gets no interval has no coverage, so for the paper the primary figure counts a draw without an interval as a miss, as round 5 did, and the conditional coverage and the share formed stand beside it. Round 5's reading of its eight worst cells, two balance variables at few residual degrees of freedom, therefore stands. Its mechanism is that the interval often cannot be formed, not that the intervals formed miss.

The lung cells differ by more than the tally alone explains, with an absolute difference of up to 0.189, and their width ratios also differ (`wr_D0cl` 0.469 in round 5 against 0.864 in round 7 for `perm_cluster`, $p_a = 0.1$, $n_L = 4$). The likely cause is the D0 reference. Round 7 forms a D0 classical interval only with at least 2 degrees of freedom, which happens in 0.52 of the lung draws at $n_L = 4$, while round 5 kept intervals with 1 degree of freedom and the $t_1$ quantile. S2b item 1 checks this.

Two smaller differences surfaced. Round 7 records the support of a $\theta_2$ cell as $p_a\binom{G_{\mathrm{all}}}{n_L}$ over all clusters, round 5 as $p_a\binom{G}{n_L}$ over the valid ones, so `LUNG_XENIUM` at $n_L = 4$ has support 136.5 in round 7 and 12.6 in round 5. Both draw over all clusters, so this changes only which $\theta_2$ cells count as supported. And the lung thresholds of some $\theta_2$ cells differ from round 5's medians by up to 13%.

## 4. Answers to the escalations

1. **Anchor code version.** Accepted. The anchors pass to four decimals with the starting-commit script.
2. **Thresholds recomputed from round 5's pool.** Accepted for $\theta_3$, where the medians match. Report the lung $\theta_2$ cells whose thresholds differ (S2b item 1).
3. **Zero inclusion probabilities.** A defensive mixture with a small $\epsilon$ is not adopted. It restores a positive $\pi_g$ only by putting weights near $G/(\epsilon\,n_L)$ on the clusters that D2 rarely accepts, and the variance that brings is not worth having. The useful version is a large mixture. With $\epsilon = 0.5$, D2 mixed with simple random selection has the same floor $\pi_g \ge 0.5\,n_L/G$ as S3's design and every $\pi_{gh} > 0$, so it is the natural control for the cube method and enters S3 (section 5). S3 and S4 report the smallest $\hat\pi_g$ and the share of zero $\hat\pi_{gh}$ in every cell.
4. **The threshold-tie fix.** Accepted.
5. **The Ω fix.** Accepted.
6. **The degenerate columns and the lung reruns.** Accepted. S1 mixes two snapshots, with the difference confined to approximate intervals on degenerate columns, as the report argues.
7. **The superpopulation target measured in resampled worlds.** Accepted. The paper states the `B_world` results as statements about worlds built from the observed clusters.
8. **Pilot outputs on Longleaf.** Accepted.
9. **Output locations.** Accepted. Keep them in the merge jobs' `_merged/` directories, with no copies. S3 and S4 may do the same.
10. **Frame ids in a second message.** Accepted. `docs/EXECUTION_RULES.md` section 6 now allows it (revision of 14 October).
11. **The duplicate row type.** Accepted.
12. **$\theta_2$ against round 5.** Settled in section 3. S2b item 1 recounts.

**Section 8 of the report.** Item 1 is S2b item 2. Item 2 is S2b item 3. Items 3 and 4 stay as they are, and the authors' implementations are still not fetched. Item 5 needs no action. Item 6 is settled by section 3 and S2b item 1.

## 5. Interval i02, as fixed

Interval i02 runs S2b, S3 and S4, then stops at the S4 gate. Section 7 of the instruction is the default, with the changes below. Theory goes into new sections of `docs/round07/tracks/ppi/round07_ppi_theory.md` before any run that uses it (section 3 for S3, section 4 for S4).

### S2b. Three diagnostics (capped at one day, before S3)

1. **The recount for $\theta_2$.** From the existing outputs, with no new draws.
   - Recompute every $\theta_2$ row of the S1 table of report section 6.1 and of the comparison of section 6.5 in three forms: coverage over all draws with no interval counted as a miss, coverage over the draws that formed one, and the share formed. Do this for every estimator, not only `rej_t`.
   - Check the reading of section 3 cell by cell, and list any cell where round 5's coverage is not round 7's conditional coverage times its share formed, within Monte Carlo error.
   - State the rule each round used for forming the D0 classical interval for $\theta_2$, and the rule in the estimator definition (`docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`). Report `wr_D0cl` for $\theta_2$ under the definition's rule. If that needs the D0 intervals with 1 degree of freedom, which round 7 did not form, rerun only the D0 classical rows of the $\theta_2$ tissue cells.
   - Give each $\theta_2$ cell's support counted over all clusters and over the valid ones, and list the lung $\theta_2$ cells whose thresholds differ from round 5's medians.

   Outputs in `results/round7/ppi/S2b_diagnostics/theta2_recount/`. From here on every $\theta_2$ coverage in a report carries its share formed.
2. **The simulation bias by population.** Change `round7_ppi_s1_sim.py` to write, per population, the smallest $\hat\pi_g$, the share of pairs with $\hat\pi_{gh} = 0$, and the signed standardised bias of the classical mean, $\hat\theta_{\mathrm{HT}}$ and $\hat\theta_{\mathrm{H}}$. Rerun the skewed cell of report section 6.2 ($G = 51$, $n_L = 8$, $k = 1$, $\lambda^\star = 0.6$, both $p_a$) with 1,000 draws. Say whether the biased populations are the ones with a zero or near-zero $\hat\pi_g$. Outputs in `results/round7/ppi/S2b_diagnostics/sim_by_population/`.
3. **Broska and Howes with small-sample corrections.** Two variants of their interval, with the same estimator and $\hat\lambda$. Write both in theory section 2.1 before the run.
   - `bh_t` multiplies the labelled clusters' term of $\hat\sigma^2_{\hat\lambda}$ (the first term of the expanded form in theory section 2.1) by $n_L/(n_L - 1)$, leaves the unlabelled clusters' term as it is, and uses the $t_{n_L-1}$ quantile. Report beside it the same interval with $t_{n_L-2}$, since $\hat\lambda$ is fitted.
   - `bh_t_fpc` is `bh_t` with the whole variance multiplied by $1 - n_L/G$. It removes only the factor $1/(1 - f)$ of $\rho_{\mathrm{BH}}$, so for the design target it should stay conservative by about $(1 - (1 - f)R^2)/(1 - R^2)$.

   Run both on S2's D0 grids, real tasks and simulation, both targets. Beside them, report per cell the median over genes of the cluster-level $R^2$ and the factor $\rho_{\mathrm{BH}}(n_L/G, R^2)$, against the measured ratio of Broska and Howes's variance estimate to the empirical variance. This closes item 2 of the report's section 8. Outputs in `results/round7/ppi/S2b_diagnostics/bh_small_sample/`. From here on both variants enter every design where Broska and Howes's interval does.

### S3. The adaptive, balanced design (two days)

As in the instruction, with these changes.
1. **The target probabilities.** Where $\pi^{(\tau)}_g$ exceeds 1, set it to 1 and rescale the uncapped clusters' probabilities proportionally so that they sum to $n_L$ minus the number capped, repeating until none exceeds 1. Proportional rescaling only raises the uncapped probabilities, so every $\pi^{(\tau)}_g \ge 0.5\,n_L/G$ holds. Reapplying the mixture to the remaining clusters would not keep that floor.
2. **Comparators.** D2 with `rej_t`, and D0 with the classical and tuned intervals, as prediction S3.1 states. Add `bh_t` and `bh_t_fpc` beside Broska and Howes. Add the mixture of D2 and D0 with $\epsilon = 0.5$ (each draw is D2's with probability 0.5 and simple random otherwise), with its simulated $\hat\pi_g$ and $\hat\pi_{gh}$ and the same Hájek intervals as the cube design.
3. **The variance.** Before any run, derive in theory section 3 an interval for $\hat\theta_{\mathrm{H}}$ under the cube design that does not need $\pi_{gh} > 0$. One candidate is the residual form for balanced sampling, applied to the linearised values $\bar z_g - \hat\theta_{\mathrm{H}}$ divided by $\pi_g$ and regressed on the balance variables divided by $\pi_g$. The derivation should say how it treats $\hat N = \sum_{g \in L} 1/\pi_g$, which balancing on $\pi_g$ fixes the sample size but not, what the landing phase's approximate balance does to it, and which reference distribution and degrees of freedom the interval uses. Say which interval is primary and why. Report the Sen-Yates-Grundy form with simulated $\hat\pi_{gh}$ and `apx_size` beside it, with the share of zero $\hat\pi_{gh}$ in every cell. The standard reference for the residual form is Deville and Tillé on variance approximation under balanced sampling. The project does not hold it, so derive the form from the cube method's balancing equations and do not cite that paper's formula.
4. **The test.** Besides the inclusion frequencies against their targets, check on the synthetic populations of S1's test that $\hat\theta_{\mathrm{HT}}$ is unbiased within Monte Carlo error and that the primary variance's mean is within 0.10 of the empirical variance in the normal-law cells. Report separately the draws whose landing phase left the balance inexact.
5. **$\theta_2$** coverages carry their share formed, as in S2b item 1.

Outputs as in the instruction, in `results/round7/ppi/S3_adaptive/`.

### S4. Greedy k-center (one day; gate)

As in the instruction, with `bh_t` and `bh_t_fpc` beside Broska and Howes, and with the Hájek interval with `apx_size` added, its exact coverage by enumeration of the $G$ starts. Outputs in `results/round7/ppi/S4_kcenter/`. Then write the S4 report in `docs/round07/i02/ppi/round07_ppi_S4_report.md` covering S2b, S3 and S4, in the format of section 7 of `docs/EXECUTION_RULES.md`, with every prediction of section 6 below scored. Run the sweep, commit, tag `round7-ppi-S4`, push the branch and the tag together, open one pull request, and stop.

**Exit items.** S2b item 1 confirms or corrects section 3 cell by cell. The cube test passes or its fallback is recorded. Every cell has run or is listed. The predictions are scored. The provenance index passes both checks.

## 6. Predictions for interval i02

Written before any run. S3.1, S3.2, S4.1 and S4.2 stand as in the instruction. These are added.
- **S2b.1** In every $\theta_2$ cell outside `LUNG_XENIUM`, round 5's coverage equals round 7's conditional coverage times its share formed to within 0.03.
- **S2b.2** In the skewed simulation cell, at least 90% of the populations in which $\hat\theta_{\mathrm{HT}}$ has a standardised bias above 3 have a smallest $\hat\pi_g$ below $0.01\,n_L/G$.
- **S2b.3** Under D0 for the design target, `bh_t` covers at 0.85 or above at every $n_L$ on every tissue task (median over arms and estimands of the median over genes).
- **S2b.4** For the superpopulation target in set `B_world`, `bh_t` covers at 0.80 or above at $n_L = 4$ on every task.
- **S3.3** In every S3 cell the smallest $\hat\pi_g$ is at least $0.45\,n_L/G$.
- **S3.4** On the supported real-task cells, S3's Hájek interval with its primary variance covers within 0.03 of D0 classical in at least 0.85 of the cells, where D2's Hájek interval with simulated pair probabilities did so in 0.71.
- **S3.5** At $n_L = 8$ with own balance, the cube design's Hájek interval is narrower than the Hájek interval under the mixture of D2 and D0 in at least three quarters of the supported cells.

## 7. What the session does next

1. Fetch `main` and read `docs/EXECUTION_RULES.md` in full. Transcribe this memo into the plan as interval i02, with S2b before S3.
2. Commit this memo unchanged at `docs/round07/i02/ppi/round07_ppi_S2_decisions.md`, after Nicolas has merged pull request #29.
3. Run S2b, S3 and S4 in that order, and stop at the S4 gate.
