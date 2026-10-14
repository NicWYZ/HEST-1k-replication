# Round 7, the inference track, decisions at the S2 gate

14 October 2026. Written by the oversight chat for the execution session of the inference track, after reviewing the S2 report (`docs/round07/i01/ppi/round07_ppi_S2_report.md`, pull request #29, tag `round7-ppi-S2`). This memo opens interval i02. Commit it unchanged at this path on your branch as the first commit of i02. Nicolas merges pull request #29 before your next push.

**What was read and checked.** The whole report, sections 1.8, 1.9 and 2.1 of the theory document (`docs/round07/tracks/ppi/round07_ppi_theory.md`), the merged tables and the numbers files. These were recomputed from the files on the branch.
- In `results/round7/ppi/S1_weighting/_merged/s1_masking_diag.csv` there are 1336 D2 rows. 225 have a cluster with $\hat\pi_g = 0$ (51 `CCRCC`, 47 `CCRCC_merged`, 33 `INDIANA_KIDNEY`, 94 `LUNG_XENIUM`, none on census) and 665 have a pair with $\hat\pi_{gh} = 0$. All 225 rest on $R = 100{,}000$ simulated draws.
- In `results/round7/ppi/S2_comparators/_merged/s2_masking_grid.csv`, the median over cells of Broska and Howes's design-target coverage under D0 is 0.707 at $n_L = 4$, rising to 0.941 at 16, and 0.698 to 0.724 per tissue task at $n_L = 4$. Kluger et al.'s cluster bootstrap covers the superpopulation target at a median of 0.624 (uniform) and 0.618 (score-mixed) at $n_L = 4$.
- The join of `rej_t` with round 5 (`results/round7/ppi/_i01_numbers_r3/i01_rej_t_vs_round5.csv`), set beside both rounds' D2 diagnostics. Section 3 gives what this showed.

**The gate rule** is section 2 of `docs/EXECUTION_RULES.md`, in the wording Nicolas approved. Nothing of S2b, S3 or S4 starts before this memo, and nothing of S5 starts before the S4 memo.

## 1. Acceptance

The S2 gate is accepted. Exit items 1, 3, 4 and 5 are met. Exit item 2 is met in its second form, since the report says which cells of the synthetic test fail and why, and the theory document's section 1.9 gives the mechanism with exact pair probabilities. The report scores every prediction plainly, runs a draw-count diagnostic before trusting its own first reading of the simulation bias, and raises the disagreement with round 5 rather than explaining it away. That last point turned out to matter most (section 3). Nicolas can merge pull request #29.

## 2. What S0 to S2 establish for the paper

1. **Weighting under rejective selection is a negative result, with a mechanism the project can state.** Rejective balance at a small acceptance probability gives some clusters an inclusion probability that is zero or nearly zero. A $\hat\pi_g = 0$ from 100,000 draws means $\pi_g$ is below about $3 \times 10^{-5}$ at 95% confidence, which for weighting is the same failure. It also gives many pairs $\pi_{gh} = 0$, which removes terms from the Sen-Yates-Grundy form and biases it down. Your section 5, expectation 1, left 20 of the 156 cells with a biased $\hat\theta_{\mathrm{HT}}$ unexplained. They are explained. Of the 880 supported cells, 51 have a share of genes with standardised bias above 3 that exceeds 0.1, and 50 of them have a $\hat\pi_g = 0$. The other is `CCRCC`, permuted arm, $\theta_2$, `pcF2`, $n_L = 8$, $p_a = 0.1$, whose smallest $\hat\pi_g$ is $3 \times 10^{-5}$ times $n_L/G$. The remaining 19 unsupported cells are `LUNG_XENIUM` $\theta_2$ at $n_L = 12$ and $p_a = 0.01$, where $n_L$ exceeds the 9 valid clusters (item 5 of section 4 asks about them). The weighted intervals with simulated pair probabilities have long lower tails of coverage (minimum 0.42 to 0.55) and are no narrower than `rej_t` at the median. So `rej_t` stays D2's interval, and the paper reports the weighting as what fails under this design and why.
2. **Design-based weighting needs inclusion probabilities bounded away from zero.** That is what S3's design gives by construction, since the mixture with $\tau = 0.5$ makes every $\pi^{(\tau)}_g \ge 0.5\,n_L/G$. Among the weighted intervals under D2, the Hájek interval with `apx_size` did best (median coverage 0.893, minimum 0.792), because it does not use the pair probabilities.
3. **The comparators from the literature under-cover at few clusters, for either target.** Broska and Howes cover the design target at a median of 0.707 at $n_L = 4$, and Kluger et al.'s bootstrap covers the superpopulation target at 0.62. Round 5's superpopulation interval is the only one near nominal for the superpopulation target at every $n_L$. For the design target Broska and Howes become conservative as $n_L/G$ grows, by less than the factor $\rho_{\mathrm{BH}}$ of theory section 2.1 suggests (S2.2 refuted).
4. **That comparison is not yet fair enough for the paper.** At $n_L = 4$ most of Broska and Howes's shortfall comes from the normal quantile and the divisor $n$. Replacing them with $t_{n_L-1}$ and $n_L - 1$ widens the interval by
$$
\frac{t_{3,\,0.95}}{z_{0.95}}\sqrt{\frac{4}{3}} = \frac{2.353}{1.645} \times 1.155 \approx 1.65,
$$
and a referee will ask for exactly that change. The paper's ground in the few-cluster regime has to be shown against the corrected interval, where what remains is the finite-population factor, the design-target factor $\rho_{\mathrm{BH}}$ and the design questions. S2b item 3 runs it.
5. **Independent Bernoulli designs are awkward at few clusters.** Under Kluger et al.'s design up to 0.098 of draws label fewer than two clusters, the bootstrap drops up to 0.123 of its replicates, and the Horvitz-Thompson interval with the Poisson variance is conservative at $n_L = 4$ (0.957). This supports fixed-size designs for the paper's regime.
6. **$\theta_2$ under D2 is unconfirmed,** in round 7 and in round 5, until S2b item 1 settles it (section 3). Every $\theta_3$ result stands.

## 3. Escalation 12, the disagreement with round 5 on $\theta_2$

Your hypothesis was that round 5 fell back to the last of 2,000 candidates where round 7 scans on. Round 5's own record contradicts it. The E4b script, `code/scripts/round5_ppi_e4b_rejective.py`, says in its docstring that a column with no accepted candidate continues past 2,000 and that no draw falls back. Its diagnostics, `results/round5/ppi/E4b_rejective/e4b_d2_diagnostics.csv`, record `n_beyond_first_batch` of at most 1 over all 1,536 rows, and a largest `candidates_max` of 2,026 over all of them. The fallback of `d2_select` belongs to E4, not E4b.

What the files show instead is that the two rounds' draws agree and the intervals' coverage does not.
- The median thresholds of every matched D2 cell are equal between `s1_masking_diag.csv` and round 5's diagnostics (ratio 1 in every $\theta_2$ cell outside `LUNG_XENIUM`, 0.87 to 1.001 there).
- The share of genes with standardised bias above 3 for the classical mean is the same cell for cell in the differing cells of `CCRCC` and `CCRCC_merged` at $n_L = 4$ and of `INDIANA_KIDNEY` at $n_L = 6$ (largest difference 0.02). So the accepted draws are the same.
- In those cells the width ratio `wr_D0cl` agrees to within 2% (median ratio of round 7 to round 5 is 1.000 on `CCRCC`, 1.015 on `INDIANA_KIDNEY` at $n_L = 6$). Yet `INDIANA_KIDNEY`, `uni_v2`, `pcF2`, $p_a = 0.1$, $n_L = 6$ covers 0.883 in round 7 and 0.654 in round 5.
- The D0 classical coverage agrees between the rounds, so the genes and the target are the same.

The same draws and the same width with a different coverage put the difference in the centre of `rej_t` for $\theta_2$, or in how coverage is tallied for $\theta_2$, in one of the two codes. One cell points to round 5. In `LUNG_XENIUM`, `uni_v2`, $\theta_2$, $n_L = 4$, $p_a = 0.1$, balance on `perm_cluster` covered 0.12 in round 5 with a width of 0.47 of D0's. A balance variable that is pure noise cannot do that to a valid interval. Round 7 gives 0.93 there. This is suggestive and not settled, and S2b item 1 settles it.

Two smaller differences surfaced on the way. Round 7 records the support of a $\theta_2$ cell as $p_a\binom{G_{\mathrm{all}}}{n_L}$ over all clusters, round 5 as $p_a\binom{G}{n_L}$ over the valid ones, so `LUNG_XENIUM` at $n_L = 4$ has support 136.5 in round 7 and 12.6 in round 5. Both draw over all clusters, so this changes only which $\theta_2$ cells count as supported. And the lung thresholds differ by up to 13% in some $\theta_2$ cells. Report both in the S4 report.

This bears on the paper. Round 5's closing memo (`docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, section 3 item 3) states where the design failed, two balance variables at few residual degrees of freedom, from the eight Indiana $\theta_2$ cells at $n_L = 6$. If round 5's $\theta_2$ `rej_t` is wrong, that statement goes, and the oversight chat records the correction in round 7's README.

## 4. Answers to the escalations

1. **Anchor code version.** Accepted. The anchors pass to four decimals with the starting-commit script.
2. **Thresholds recomputed from round 5's pool.** Accepted for $\theta_3$, where the medians match. For $\theta_2$ on lung they differ in some cells (section 3), which S2b item 1 covers.
3. **Zero inclusion probabilities.** The defensive mixture is not adopted. With $\epsilon$ small the weights reach $G/(\epsilon\,n_L)$ on the clusters D2 rarely accepts, so the estimator regains unbiasedness at a variance that defeats the balance. The paper's remedy is a design whose probabilities are bounded below, which is S3. S3 and S4 report the smallest $\hat\pi_g$ and the share of zero $\hat\pi_{gh}$ in every cell.
4. **The threshold-tie fix.** Accepted.
5. **The Ω fix.** Accepted.
6. **The degenerate columns and the lung reruns.** Accepted. S1 mixes two snapshots, with the difference confined to approximate intervals on degenerate columns, as the report argues.
7. **The superpopulation target measured in resampled worlds.** Accepted. The paper states the `B_world` results as statements about worlds built from the observed clusters.
8. **Pilot outputs on Longleaf.** Accepted.
9. **Output locations.** Accepted. Keep them in the merge jobs' `_merged/` directories, with no copies. S3 and S4 may do the same.
10. **Frame ids in a second message.** Accepted. `docs/EXECUTION_RULES.md` section 6 now allows it (revision of 14 October).
11. **The duplicate row type.** Accepted.
12. **$\theta_2$ against round 5.** Section 3, and S2b item 1.

**Section 8 of the report.** Item 1 is S2b item 2. Item 2 is S2b item 3. Items 3 and 4 stay as they are, and the authors' implementations are still not fetched. Item 5 needs no action. Item 6 is S2b item 1.

## 5. Interval i02, as fixed

Interval i02 runs S2b, S3 and S4, then stops at the S4 gate. Section 7 of the instruction is the default, with the changes below. Theory goes into new sections of `docs/round07/tracks/ppi/round07_ppi_theory.md` before any run that uses it (section 3 for S3, section 4 for S4).

### S2b. Three diagnostics (capped at one day, before S3)

1. **The $\theta_2$ replay.** Take two cells, `INDIANA_KIDNEY`, `uni_v2`, $\theta_2$, `pcF2`, $p_a = 0.1$, $n_L = 6$ (round 5 coverage 0.654, round 7 0.883), and `LUNG_XENIUM`, `uni_v2`, $\theta_2$, `perm_cluster`, $p_a = 0.1$, $n_L = 4$ (0.12 and 0.93). Run two arms, as S0 did for $\theta_3$.
   - Arm 1 is round 5's E4b script as S0's arm 1 ran it, from the starting commit, with round 5's seeds. It must reproduce round 5's row of `e4b_rej_width_ratios.csv` to four decimals. If it does not, run it again from snapshot `9185bc6`, which wrote round 5's rows.
   - Arm 2 is round 7's code on arm 1's accepted draws.
   - For every draw and gene, write the accepted candidate, the valid labelled clusters, the centre, the half-width, the residual degrees of freedom and whether the interval covers. Find the first of these that differs between the arms, name the line of code responsible, and say which of the two computations is right for $\theta_2$ as the estimator definition defines it.
   If arm 1 does not reproduce round 5's row from either commit, stop and report, as for a failed S0 anchor. If round 7's code is the one in error, fix it and rerun every $\theta_2$ tissue cell of S1 before S3, and record it as an escalation. If round 5's code is, change nothing in round 7 and say exactly what round 5 computed. Either way, recompute the comparison of report section 6.5 and the S1 table of section 6.1 for $\theta_2$ with the support counted both ways. Outputs in `results/round7/ppi/S2b_diagnostics/theta2_replay/`.
2. **The simulation bias by population.** Change `round7_ppi_s1_sim.py` to write, per population, the smallest $\hat\pi_g$, the share of pairs with $\hat\pi_{gh} = 0$, and the signed standardised bias of the classical mean, $\hat\theta_{\mathrm{HT}}$ and $\hat\theta_{\mathrm{H}}$. Rerun the skewed cell of report section 6.2 ($G = 51$, $n_L = 8$, $k = 1$, $\lambda^\star = 0.6$, both $p_a$) with 1,000 draws. Say whether the biased populations are the ones with a zero or near-zero $\hat\pi_g$. Outputs in `results/round7/ppi/S2b_diagnostics/sim_by_population/`.
3. **Broska and Howes with small-sample corrections.** Two variants of their interval, with the same estimator and $\hat\lambda$.
   - `bh_t` multiplies $\hat\sigma^2_{\hat\lambda}$ by $n_L/(n_L - 1)$ and uses the $t_{n_L-1}$ quantile.
   - `bh_t_fpc` multiplies it further by $1 - n_L/G$.

   Run both on S2's D0 grids, real tasks and simulation, both targets. Beside them, report per cell the median over genes of the cluster-level $R^2$ and the factor $\rho_{\mathrm{BH}}(n_L/G, R^2)$ of theory section 2.1, against the measured ratio of Broska and Howes's variance estimate to the empirical variance. This closes item 2 of the report's section 8. Outputs in `results/round7/ppi/S2b_diagnostics/bh_small_sample/`. From here on both variants enter every design where Broska and Howes's interval does.

### S3. The adaptive, balanced design (two days)

As in the instruction, with these changes.
1. **Comparators.** D2 with `rej_t` and D0 with the classical and tuned intervals, as prediction S3.1 states. Add `bh_t` and `bh_t_fpc` beside Broska and Howes.
2. **The variance.** Before any run, derive in theory section 3 an interval for $\hat\theta_{\mathrm{H}}$ under the cube design that does not need $\pi_{gh} > 0$, such as the residual form for balanced sampling, built from the residuals of $\bar z_g/\pi_g$ on the balance variables over $\pi_g$. Say which interval is primary and why. Report the Sen-Yates-Grundy form with simulated $\hat\pi_{gh}$ and `apx_size` beside it, with the share of zero $\hat\pi_{gh}$ in every cell. The standard reference for the residual form is Deville and Tillé on variance approximation under balanced sampling. The project does not hold it, so derive the form from the cube method's balancing equations and do not cite that paper's formula.
3. **The test.** Besides the inclusion frequencies against their targets, check on the synthetic populations of S1's test that $\hat\theta_{\mathrm{HT}}$ is unbiased within Monte Carlo error and that the primary variance's mean is within 0.10 of the empirical variance in the normal-law cells.
4. **$\theta_2$** runs only after S2b item 1, on whichever code that item leaves correct.

Outputs as in the instruction, in `results/round7/ppi/S3_adaptive/`.

### S4. Greedy k-center (one day; gate)

As in the instruction, with `bh_t` and `bh_t_fpc` beside Broska and Howes, and with the Hájek interval with `apx_size` added, its exact coverage by enumeration of the $G$ starts. Outputs in `results/round7/ppi/S4_kcenter/`. Then write the S4 report in `docs/round07/i02/ppi/round07_ppi_S4_report.md` covering S2b, S3 and S4, in the format of section 7 of `docs/EXECUTION_RULES.md`, with every prediction of section 6 below scored. Run the sweep, commit, tag `round7-ppi-S4`, push the branch and the tag together, open one pull request, and stop.

**Exit items.** S2b item 1 names the line of code responsible, or the report says why it cannot. The cube test passes or its fallback is recorded. Every cell has run or is listed. The predictions are scored. The provenance index passes both checks.

## 6. Predictions for interval i02

Written before any run. S3.1, S3.2, S4.1 and S4.2 stand as in the instruction. These are added.
- **S2b.1** In both cells arm 1 reproduces round 5's coverage and arm 2, on the same draws, reproduces round 7's, and the computation found to be wrong is round 5's.
- **S2b.2** In the skewed simulation cell, at least 90% of the populations in which $\hat\theta_{\mathrm{HT}}$ has a standardised bias above 3 have a smallest $\hat\pi_g$ below $0.01\,n_L/G$.
- **S2b.3** Under D0 for the design target, `bh_t` covers at 0.87 or above at every $n_L$ on every tissue task (median over arms and estimands of the median over genes).
- **S2b.4** For the superpopulation target in set `B_world`, `bh_t` covers at 0.80 or above at $n_L = 4$ on every task.
- **S3.3** In every S3 cell the smallest $\hat\pi_g$ is at least $0.45\,n_L/G$.
- **S3.4** On the supported real-task cells, S3's Hájek interval with its primary variance covers within 0.03 of D0 classical in at least 0.85 of the cells, where D2's Hájek interval with simulated pair probabilities did so in 0.71.

## 7. What the session does next

1. Fetch `main` and read revision 14 October of `docs/EXECUTION_RULES.md` (sections 4 and 6). Transcribe this memo into the plan as interval i02, with S2b before S3.
2. Commit this memo unchanged at `docs/round07/i02/ppi/round07_ppi_S2_decisions.md`, after Nicolas has merged pull request #29.
3. Run S2b, S3 and S4 in that order, and stop at the S4 gate.
