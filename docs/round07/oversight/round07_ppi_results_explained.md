# The PPI paper's results explained, after round 7

15 October 2026. Written by the oversight chat for Nicolas after both tracks of round 7 ended. It replaces the round-5 explainer (`docs/round06/00_prep/round06_round5_results_explained.md`) as the current account of what the paper "Labelling budgets for prediction-powered inference with clustered data" has found. It covers everything that explainer covered, says for each result whether it stands, was revised by round 7, or is now held by published work, and adds what round 7 found. The round-5 explainer is kept as the record of what was believed on 11 October.

Part A explains the main results, each with what we found, why we looked, what changed, why it matters, and the theory with its expressions. A step is skipped only when it is algebra between two displayed lines, and the text says so each time. Part B gives the other results briefly. Part C says what published work now holds. Part D lists what is not established, and Part E the decisions that are Nicolas's.

The derivations are in `docs/round05/tracks/ppi/round5_ppi_theory.md`, `docs/round05/tracks/conformal/round5_conf_theory.md` and `docs/round07/tracks/ppi/round07_ppi_theory.md`. The readings for the paper are in section 3 of the two round-5 closing memos (`docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, `docs/round05/i03/conformal/round5_conformal_W5_decisions.md`) and section 2 of round 7's closing memo for the inference track (`docs/round07/i04/ppi/round07_ppi_final_decisions.md`). The positioning against published work is `docs/round07/oversight/round07_ppi_positioning.md`. Every number is read from the file named beside it.

## The status of each round-5 result, at a glance

| Round-5 result | Status after round 7 |
|---|---|
| A1. In regime B most of the predictions' apparent gain was a level term, and form C removes it | stands. The superpopulation comparison of the two regimes is now published by Broska and Howes, and round 4's condition for it is superseded (Part C) |
| A2. The design-target interval needed a cross-fitting term | stands. Below six labelled clusters the coefficient is zero by rule, and a corrected version of Broska and Howes's interval is narrower there (A5) |
| A3. Inside the target donor, the full conformal set is the method from 9 labelled spots | stands, untouched by the new literature |
| A4. Rejective balanced selection with `rej_t` narrows the interval under conditions | revised. It is the narrowest valid interval on census. On tissue it covers below simple random selection, and a cube design is as narrow. Round 5's worst cells were draws with no interval, not intervals that missed |
| Open question. Inclusion-probability weighting under rejective selection | answered, negatively (A5) |
| The gain theorem of round 4 | implied by Broska and Howes's published formula, and classical (Part C) |

---

## The setting, once

There are $G$ clusters (donors, or states and areas on the census tasks). Cluster $g$ has $M_g$ units (spots, or people). For unit $i$ of cluster $g$ we have the label $y_{gi}$, which costs money to measure, the prediction $\hat y_{gi}$, which is free, and a label-free weight $w_{gi}$ computed from the image or the covariates. Every estimand is a donor-weighted mean,

$$
\theta = \frac{1}{G}\sum_{g=1}^{G} \bar z_g, \qquad z_{gi} = w_{gi}\,y_{gi}, \qquad f_{gi} = w_{gi}\,\hat y_{gi},
$$

with $\bar z_g$ and $\bar f_g$ the cluster means. For the slope $\theta_3$ the weight is the centred covariate over its variance, $w_{gi} = \tilde x_{gi}/v_g$, so $\bar z_g$ is the cluster's own least-squares slope. For the group difference $\theta_2$ the weight is $1/\pi_{N,g}$ on the neoplastic-dominant spots, $-1/\pi_{S,g}$ on the stromal-dominant spots and 0 elsewhere, so $\bar z_g$ is the difference of the two groups' means, and only donors where both groups are present are valid clusters for $\theta_2$. In both cases

$$
\sum_i w_{gi} = 0 .
$$

There are two ways to spend a labelling budget. In **regime A** we label every unit of $n_L$ clusters and none of the others. In **regime B** we label a few units, $m_g$, in every cluster. The **design target** is the fixed set of $G$ clusters we have, and the variance is over which clusters and units we label. The **superpopulation target** treats the clusters as draws from a larger population. D0 is simple random selection of the $n_L$ labelled clusters, and D2 is rejective selection (A4).

---

# Part A. The main results

## A1. In regime B, most of what the predictions seemed to buy was a level term

**Status: stands. The superpopulation comparison of the regimes is published (Part C).**

### What we found

Round 4 measured what the predictions buy in regime B against a classical estimator that was the plain mean of $z_{gi}$ over the labelled units. That estimator carries noise from the outcome's level, $\mu_g = \bar y_g$, multiplied by the chance imbalance of the weights in the labelled units. Any predictor whose cluster mean is not zero removes that noise, including a constant. So part of round 4's gain was a constant doing the work.

- **A constant predictor already narrows round 4's classical interval.** Its width ratio against round 4's classical estimator is 0.81 to 0.82 on kidney cancer, 0.85 to 0.86 on Indiana, 0.57 to 0.59 on lung and 0.12 to 0.13 on census income (`results/round5/ppi/E2_regimeB/e2_decomposition.csv`, $\theta_3$, donor-weighted, design target, $m \ge 5$).
- **Against the constant, the encoders add little or nothing on Visium.** Their width over the constant predictor's is 0.98 to 1.04 on the three kidney tasks, 0.74 to 0.84 on lung and 0.60 to 0.64 for the package predictor on census income (same file).
- **The paper's numbers, against the better classical estimator (form C).** In regime B the $\theta_3$ width ratio is 0.982 to 1.009 on the three kidney tasks, 0.706 to 0.847 on lung and 0.594 to 0.625 on the two census tasks, and the interval covers 0.855 to 0.950 over all 196 rows (`results/round5/ppi/E5_joint/e5_joint_design.csv`).

Under the two-level estimator regime B stays narrower than regime A in 210 of 232 comparisons, and on the kidney tasks the regime ratio is the same with and without the predictor, so there regime B's advantage is the design and not the predictor (`docs/round05/i03/ppi/round5_ppi_E4_decisions.md`, section 3 item 4).

### Why we looked for it

Round 4's theory said the regime-B gain follows the within-cluster $R^2$ of the predictor. For a weight with cluster mean zero, the within-cluster $R^2$ of a constant predictor is not zero (`docs/round05/i01/ppi/round5_ppi_track.md`, section 2.4). Stage E2 tested that reading.

### What changed, then and now

Round 4 reported regime B's width as 0.81 to 0.84 of classical on the Visium tasks, 0.42 on lung and 0.08 on census by state, and read the gain as within-cluster prediction. That reading was withdrawn in round 5 and stays withdrawn.

Round 7 changed what the paper can claim about the comparison of the regimes. The round-5 explainer called that comparison the result the paper leads with, because the literature check had found nothing like it. Broska and Howes (arXiv:2610.09601, 7 October 2026) now show, for a superpopulation target, that spreading labels over all clusters beats labelling whole clusters, and their variance formula supersedes round 4's condition for when regime B wins (Part C). What stays the paper's own is the comparison for the design target, where regime B has no between-cluster term at all, the costs per cluster and per unit, and the level term with form C. Which result the paper leads with is open (Q3).

### Why it matters

A reviewer who knows survey sampling would spot the level term at once, because it is why a regression estimator carries an intercept. The constant predictor is the primary control in every regime-B comparison.

### The theory

**Where the level enters.** Take one cluster in regime B with $m$ labelled units drawn without replacement, and drop the index $g$. With $s_{wy}$ the labelled units' sample covariance (divisor $m - 1$) and $\bar w_L$, $\bar y_L$ their sample means,

$$
\frac{1}{m}\sum_{i \in L} w_i\,y_i = \frac{m-1}{m}\,s_{wy} + \bar w_L\,\bar y_L ,
$$

which is the definition of the sample covariance rearranged, so that algebra is skipped. The first term estimates the cluster's value. The second has mean zero, since $\bar w_L$ has mean 0, but to first order it behaves like $\mu\,\bar w_L$, with variance

$$
\text{Var}(\mu\,\bar w_L) = \mu^2\Big(1 - \frac{m}{M}\Big)\frac{S_w^2}{m}.
$$

This is the outcome's level times the chance imbalance of the weights. It has nothing to do with prediction.

**What a constant predictor removes.** Let the predictor be a constant $c$ in the cluster, so $f = c\,w$, and take the rectifier $z - \lambda f$. With cluster moments $\langle\cdot\rangle$ (divisor $M$), $C = \langle w^2 y \rangle$ and $A = \langle w^2 \rangle$, the within-cluster variance of the rectifier is

$$
V(\lambda) = V - 2\lambda c\,C + \lambda^2 c^2 A, \qquad V = \langle z^2 \rangle - \langle z \rangle^2 ,
$$

minimised at $\lambda c = C/A$, where it removes $D = C^2/A$. The share removed is

$$
L = \frac{D}{V} = \frac{\langle w^2 y \rangle^2}{\langle w^2 \rangle\,\big(\langle w^2 y^2 \rangle - \langle w y \rangle^2\big)} ,
$$

the squared within-cluster correlation of $z$ with $w$, exact and with no model for $y$.

**For the slope, the share is the level against the spread.** Write $y_i = \mu + \beta\,\tilde x_i + \epsilon_i$ by the cluster's own least-squares line. With $\tilde x$ standardised and normal and $\epsilon$ independent with variance $\sigma^2$, the skewness and curvature terms vanish and

$$
L = \frac{\mu^2}{\mu^2 + \sigma^2 + 2\beta^2},
$$

after algebra that is skipped. Log income has a large level against its spread, which is why round 4's census gain looked so large. On census by state the permuted predictor's within-cluster $R^2$ for the slope is 0.976 (`results/round5/ppi/E0_anchors/e0_brief_claims.csv`).

**Form C removes the level without any predictor.** Form C estimates the cluster's value from the labelled covariance, $\hat z = \frac{M-1}{M}\,s_{wy}$, which is the first term above. With a predictor,

$$
\hat z = \frac{M-1}{M}\Big(\lambda\,S_{w\hat y} + s_{w,\,y - \lambda\hat y}\Big),
$$

with $S_{w\hat y}$ from all units. A constant predictor gives $S_{w\hat y} = 0$ and $s_{w,\,y - \lambda c} = s_{wy}$, so under form C it gives exactly the classical estimate, as the code confirms in 420 of 420 simulation cells (`results/round5/ppi/E3_twolevel/e3_sim_summary.csv`). Form C is the paper's within-cluster estimator.

---

## A2. The design-target interval was missing a term

**Status: stands. Below six labelled clusters the estimator does not tune, which round 7 brought into focus (A5, item 4).**

### What we found

When most clusters are labelled, the coefficients fitted on two halves of the labelled clusters add a variance term that the finite-population factor does not shrink, and round 4's interval under-covers. The worst simulated case is 0.840 at $G = 15$, $n_L = 12$, with estimated over empirical variance 0.69 (`results/round5/ppi/E1_interval/e1_sim_grid.csv`). With the term restored, the ratio is 0.974 to 1.013 and coverage 0.888 to 0.903 (`results/round5/ppi/E3a_crossfit/e3a_sim_prediction_cells.csv`). The corrected interval, `textbook_t|fpc|lin|xf`, is the paper's design-target interval.

### What changed in round 7

Nothing in the derivation. Two things around it.
- Broska and Howes's interval has no small-sample correction and no finite-population factor, and they name small-sample corrections as future work. The paper's design-target interval keeps its own finite-population factor and cross-fitting term, but at the smallest $n_L$ a small-sample correction of their interval does as well or better (A5, item 4, and Part C).
- The estimator's rule `c_crossfit_design` sets the coefficient to zero below six labelled clusters (`docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`), so at four labelled clusters the tuned interval is the classical one. Round 7 found that a single coefficient fitted on all labelled clusters, with a $t$ reference, does better there (A5, item 4). Whether to change the rule is Nicolas's decision (R7-6).

### The theory

Draw $n$ clusters and split them into halves $A$ and $B$. Fit $\lambda_A$ on $A$, apply it to $B$, and the reverse. With $c' = (n_B\lambda_A + n_A\lambda_B)/n$,

$$
\hat\theta = c'\,\bar F + \frac{1}{n}\sum_{g \in L}\big(z_g - \lambda_{(g)} f_g\big).
$$

With $\delta = \lambda_B - \lambda_A$, $\Delta = \bar f_A - \bar f_B$ and $\kappa = n_A n_B/n^2$, draw by draw,

$$
\hat\theta = \underbrace{\bar z_L - c'\,(\bar f_L - \bar F)}_{T_1} \; - \; \underbrace{\kappa\,\delta\,\Delta}_{T_2},
$$

after algebra that is skipped. $T_1$ has variance proportional to $1 - n/G$. $T_2$ does not, because for disjoint simple random halves

$$
\text{Var}(\bar f_A - \bar f_B) = \Big(\frac{1}{n_A} + \frac{1}{n_B}\Big)S_f^2 ,
$$

the covariance terms cancelling the finite-population terms. At $n = G$, $T_1 = \theta$ exactly but $T_2$ is not zero, while round 4's variance estimate is zero. The correction restores what the factor removed,

$$
\widehat{\text{Var}}_{\text{xf}} = \Big(1 - \frac{n}{G}\Big)\frac{s_e^2}{n} + \frac{n}{G}\cdot\frac{\overline{(\lambda_{(g)} - c')^2}_L\;s_f^2}{n},
$$

and under the normal law at $G = 15$, $n = 12$ it raises the expected ratio of estimate to true variance from 0.65 to 0.985 (`docs/round05/tracks/ppi/round5_ppi_theory.md`, section 2.0).

---

## A3. Inside the target donor, the full conformal set is the method from 9 labelled spots

**Status: stands. Neither the lab's manuscript nor the new papers touch the prediction-set part (`docs/round07/00_prep/round07_overlap_check.md`). The nearest work remains GHCP.**

### What we found

For a prediction set for the spots of a new donor, with $o$ labelled spots from that donor, at $K = 10$ calibration donors and 90%, the narrowest valid method on real data is HCP, which uses no labelled target spots, up to $o = 5$, and from $o = 9$ the full conformal set built from the target donor's own residuals (`within_full`), at 0.416 to 0.677 of HCP's width on every task. `within_full` covers 0.900 to 0.923 at $o$ of 10, 25 and 100 (`results/round5/conformal/W5_map/w5_report_numbers.csv`). In simulation it is the narrowest valid method in 1,350 of 1,440 cells at a between-cluster share of 0.3 and in all 1,440 at 0.9 (`results/round5/conformal/W1_sim/w1_whole_grid_counts.csv`).

### Why it matters

It answers the prediction-set half of the paper's design question with one rule. Below 9 labelled target spots, use the other donors (HCP). From 9 on, use the target donor's own spots.

### The theory

Let $r_1, \dots, r_o$ be the target donor's labelled residuals, with sum $S$. For a candidate residual $r$, the fitted mean is $c(r) = (S + r)/(o + 1)$, the scores are $s_i(r) = |r_i - c(r)|$ and $s(r) = |r - c(r)|$, and $r$ is kept when

$$
1 + \#\{i : s_i(r) \ge s(r)\} > \alpha\,(o + 1).
$$

Each comparison $|(o+1)\,r_i - S - r| \ge |o\,r - S|$ becomes, after squaring and factorising (algebra skipped),

$$
(o+1)\,(r_i - r)\,\big[(o+1)\,r_i - 2S + (o-1)\,r\big] \ge 0,
$$

which holds on the closed interval between $r = r_i$ and $r = (2S - (o+1)\,r_i)/(o-1)$. The set is finite once $\alpha(o + 1) \ge 1$, which at 90% is $o \ge 9$ (`docs/round05/i02/conformal/round5_conf_final_report.md`, section 4). At the true residual the $o + 1$ scores are exchangeable, so

$$
P(\text{covered}) = \frac{\lceil (1-\alpha)(o+1) \rceil}{o+1},
$$

exactly 0.9 at $o = 9$, confirmed on the real data within 0.005 in all 362 cells (`results/round5/conformal/W3_real/merged/w3_acceptance.csv`). The plain split ranks uncentred residuals, so the donor's offset inflates every score. The half split removes the offset but needs $\lceil o/2 \rceil + 1 > 1/\alpha$. The full set centres on all spots and ranks all of them.

---

## A4. Choosing balanced clusters: what holds after round 7

**Status: revised.**

### What round 5 found

Rejective selection (D2) draws samples of $n_L$ clusters until the sample's mean of a label-free balance variable, such as each cluster's mean prediction $\bar f_g$, is close to the population mean. Under this design the variance of the plain classical mean falls, and the interval `rej_t` captures the fall. At $n_L = 8$ for $\theta_3$, with balance on the estimand's own $\bar f_g$ at acceptance probability 0.01, `rej_t` was 0.726 of the simple-random classical width on kidney cancer with `uni_v2` and 0.551 on census by state, against 0.852 and 0.618 for the tuned estimator (`results/round5/ppi/E4b_rejective/e4b_rej_width_ratios.csv`). It seemed to fail with two balance variables at few residual degrees of freedom, down to 0.641 to 0.684 on Indiana $\theta_2$ at $n_L = 6$.

### What round 7 changed

1. **The worst cells were draws with no interval.** For $\theta_2$ the number of valid labelled clusters varies from draw to draw, and `rej_t` forms no interval when its residual degrees of freedom fall below 2. Round 5 counted those draws as misses. In the Indiana cell with `uni_v2` and `pcF2` at $p_a = 0.1$, the intervals that are formed cover 0.883, and 0.741 of draws form one. Their product, 0.654, is round 5's figure (`docs/round07/i02/ppi/round07_ppi_S2_decisions.md`, section 3). Round 5's statement of where the design fails stands, with this mechanism.
2. **Compared on matched cells, the picture differs by domain.** Round 7 compared every design on exactly the same task, arm, estimand and $n_L$, only where rejective selection has at least 1,000 acceptable samples, and counted a draw with no interval as a miss. At $n_L = 8$ and $p_a = 0.01$, over the informative predictors (`results/round7/ppi/S5_numbers/run1/s5_matched.csv`):

   | design | tissue coverage | tissue width | census coverage | census width |
   |---|---|---|---|---|
   | D0, classical | 0.875 | 1 | 0.886 | 1 |
   | D0, tuned (`xf`) | 0.871 | 0.975 | 0.894 | 0.531 |
   | D2, `rej_t` | 0.861 | 0.888 | 0.889 | 0.456 |
   | cube design, $\pi_g$, 1 and $\bar f_g$ balanced | 0.885 | 0.883 | 0.885 | 0.568 |

   On census `rej_t` is the narrowest valid interval in the track. On tissue it is narrower than simple random selection but covers below it, and a cube design with known inclusion probabilities is as narrow and covers better. At $n_L = 12$ on tissue the cube design is narrower (0.801 against 0.921).
3. **The headline cell.** On kidney cancer with `uni_v2`, $\theta_3$, $n_L = 8$, `rej_t` keeps its width of 0.726 but covers 0.832 against 0.849 for simple random selection, and S3's cube design there has width 0.768 at coverage 0.881 (`results/round7/ppi/S1_weighting/_merged/s1_masking_grid.csv`, `results/round7/ppi/S3_adaptive/_merged_r2/s3_masking_grid.csv`).
4. **The principle is classical.** Balancing on an auxiliary variable and using the simple mean is classical survey sampling (Morgan and Rubin for treatment assignment, Fuller for sampling). Balancing a unit-level active design on its predictions is Chen et al.'s "Balanced Active Inference" (NeurIPS 2025), whose remark 1 notes that balancing on the predictions themselves collapses to the weighted mean of the labels. What stays the paper's own is the few-cluster comparison with its conditions.

Which design the paper recommends is Nicolas's decision (R7-7).

### The theory of `rej_t`

Let $x_g$ be the $k$ balance variables with population mean $\bar X$ and covariance $S_X$. With $B = S_X^{-1}S_{Xz}$ the population least-squares coefficient and $e_g = z_g - \bar Z - B^\top(x_g - \bar X)$ the residual, for any sample

$$
\bar z_L - \bar Z = \bar e_L + B^\top(\bar x_L - \bar X).
$$

Under simple random sampling the two terms are uncorrelated, since $S_{eX} = 0$, and nearly jointly normal when $n$ and $G - n$ are large. Rejection keeps a sample when its Mahalanobis distance is below its $p_a$ quantile, so it restricts only the balance term, whose covariance shrinks by

$$
v_a = \frac{P(\chi^2_{k+2} \le q_a)}{P(\chi^2_k \le q_a)},
$$

Morgan and Rubin's Theorem 3.1, with $q_a$ the $p_a$ quantile of $\chi^2_k$. So

$$
\text{Var}_{D2}(\bar z_L) = \frac{1-f}{n}\Big(S_e^2 + v_a\,B^\top S_X B\Big),
$$

and `rej_t` estimates the two pieces from a regression of $z_g$ on $x_g$ over the labelled clusters,

$$
\widehat{\text{Var}}_{\text{rej}} = \Big(1 - \frac{n}{G}\Big)\frac{s^2_{\text{res}} + v_a\,\hat b^\top S_x\,\hat b}{n},
$$

with $t_{n-k-1}$. The derivation needs a normal approximation over clusters, enough distinct acceptable samples, and enough residual degrees of freedom. When the residual degrees of freedom fall below 2 no interval is formed, which is item 1 above. Round 5's wording of the conditions (one balance variable, the estimand's own $\bar f_g$, at least 1,000 acceptable samples, $n_L \ge 8$) still describes where it works, and round 7 adds that its coverage on tissue sits a little below simple random selection's even there.

---

## A5. What round 7 added

### 1. Weighting by inclusion probabilities under rejective selection fails

This was round 5's open question. Each cluster's inclusion probability $\pi_g = P(g \in L)$ under D2 can be found by simulating the design before any label is bought, and the Horvitz-Thompson and Hájek means

$$
\hat\theta_{\mathrm{HT}} = \frac{1}{G}\sum_{g \in L}\frac{\bar z_g}{\pi_g}, \qquad \hat\theta_{\mathrm{H}} = \frac{\sum_{g \in L} \bar z_g/\pi_g}{\sum_{g \in L} 1/\pi_g}
$$

are then design-unbiased or nearly so, provided every $\pi_g > 0$. The Sen-Yates-Grundy variance

$$
\widehat{\text{Var}}_{\mathrm{SYG}}(\hat\theta_{\mathrm{HT}}) = \frac{1}{2G^2}\sum_{g \ne h \in L}\frac{\pi_g\pi_h - \pi_{gh}}{\pi_{gh}}\left(\frac{\bar z_g}{\pi_g} - \frac{\bar z_h}{\pi_h}\right)^2
$$

needs every pair probability $\pi_{gh} > 0$. Rejective balance at a small acceptance probability breaks both. In 225 of 1336 real-task cells some cluster was never accepted in 100,000 simulated draws, and in 665 some pair never appeared together (`results/round7/ppi/_i01_numbers_r3/s1_report_numbers.csv`). Clusters with extreme balance variables are almost never chosen. In simulation, 128 of the 134 populations where $\hat\theta_{\mathrm{HT}}$ was badly biased had a smallest $\hat\pi_g$ below $0.01\,n_L/G$ (`results/round7/ppi/S2b_diagnostics/numbers_items_2_3_r2/s2b2_numbers.csv`). On matched census cells at $n_L = 8$, the Hájek interval covers 0.828 at width 0.579, against 0.889 at 0.456 for `rej_t` (`s5_matched.csv`). So the paper reports weighting under rejective selection as a negative result with this mechanism.

### 2. A cube design with bounded probabilities works, once the constant is balanced

The cube method (Deville and Tillé) draws a fixed-size sample with prescribed inclusion probabilities while balancing chosen variables. Round 7 used a cluster-level version of Chen et al.'s design, with target probabilities that mix a label-free score $u_g = |\bar f_g - \bar F|$ with uniform ones,

$$
\pi^{(\tau)}_g = \tau\,\frac{n_L\,u_g}{\sum_h u_h} + (1 - \tau)\,\frac{n_L}{G}, \qquad \tau = 0.5,
$$

so every $\pi_g \ge 0.5\,n_L/G$ and almost no pair is never sampled together. With the Hájek mean and the Sen-Yates-Grundy form using simulated $\hat\pi_{gh}$, it covers like simple random selection.

Balancing only on $\pi_g$ and $\bar f_g$ lost most of the gain on census (width 0.912). The reason is that it fixes the sample size but not $\hat N = \sum_{g \in L} 1/\pi_g$, while it makes the Horvitz-Thompson total of $\bar f_g$ exact. The Hájek mean of the predictions is then

$$
\frac{\sum_{g \in L} \bar f_g/\pi_g}{\hat N} = \bar F\,\frac{G}{\hat N},
$$

which misses $\bar F$ by $\bar F\,(G/\hat N - 1)$, a multiple of the level of the predictions, large for income. Balancing also on the constant, $x_g = 1$, targets $\hat N = G$. It halved the census width, from 0.912 to 0.568 at $n_L = 8$ (`results/round7/ppi/S4b_cube_constant/_merged/s4b_report_numbers.csv`). The cube method's last step never meets that equation exactly, and $|\hat N/G - 1|$ stays at a median of 0.03 to 0.05 (`docs/round07/tracks/ppi/round07_ppi_theory.md`, section 3.10). The Hájek mean divides by $\hat N$ and is unaffected, but the Horvitz-Thompson mean divides by $G$ and carries the level of income times that deviation, so it stays unusable on census (width 3.48 of D0's). With three balance variables the interval has too few degrees of freedom at $n_L = 4$, so this design is stated for $n_L \ge 6$.

### 3. Greedy k-center is a negative result

Choosing the labelled clusters by greedy k-center on the clusters' mean embeddings, after a random first cluster, gives each cluster a positive inclusion probability, so $\hat\theta_{\mathrm{HT}}$ is unbiased, but many pairs are never sampled together and no design-based variance exists. Computed exactly over all starts, the classical interval applied as if the sample were random covers 0.326 to 0.458 on the two kidney cancer tasks with the foundation-model encoders, and $\hat\theta_{\mathrm{HT}}$ is 1.38 to 3.33 times as variable as the classical mean under simple random selection (`results/round7/ppi/S4_kcenter/_merged_r2/s4_report_numbers.csv`). Deterministic or near-deterministic selection rules built for coverage of the embedding space are not compatible with design-based inference.

### 4. The comparators from the literature, and a correction that changes the positioning

Broska and Howes's interval, specialised to whole labelled clusters, is

$$
\hat\theta^{PP}_\lambda = \bar z_L + \lambda\big(\bar f_U - \bar f_L\big), \qquad \frac{\hat\sigma^2_\lambda}{n} = \frac{1}{n}\Big[\frac{1}{n}\sum_{g \in L}\Big(\big(z_g - \hat\theta^{PP}_\lambda\big) - \lambda\big(f_g - \bar F\big)\Big)^2 + \lambda^2\,\frac{n}{N}\,\frac{1}{N}\sum_{g \in U}\big(f_g - \bar F\big)^2\Big],
$$

with $n$ labelled and $N$ unlabelled clusters, one global $\hat\lambda$, and the normal quantile (`docs/round07/tracks/ppi/round07_ppi_theory.md`, section 2.1). As published it under-covers at few clusters, 0.704 on tissue and 0.717 on census at $n_L = 4$ for the design target. Kluger et al.'s cluster bootstrap under independent Bernoulli selection covers 0.618 at $n_L = 4$ on tissue for the design target and 0.565 to 0.808 for the superpopulation target (`results/round7/ppi/S5_numbers/run1/s5_bh_vs_tuned.csv`).

The project then made the obvious small-sample correction (`bh_t`), multiplying the labelled term by $n/(n - 1)$ and using $t_{n-1}$. At $n_L = 4$ this widens the interval by at most

$$
\frac{t_{3,\,0.95}}{z_{0.95}}\sqrt{\frac{4}{3}} = \frac{2.353}{1.645} \times 1.155 \approx 1.65 .
$$

With it the interval covers 0.884 on tissue and 0.882 on census at $n_L = 4$, at widths of 0.867 and 0.444 of D0 classical's, while the paper's tuned interval there is the classical one (width 1), because its rule does not tune below six clusters. From $n_L = 8$ the corrected interval is wider than the tuned one on tissue (1.108 against 0.977) and over-covers the design target, because it has no finite-population factor. Since anyone could make this correction, the paper cannot claim the few-cluster regime in general. What it keeps is the finite-population factor for the design target at moderate and large $n_L/G$, the cross-fitting term, and the design results. This is Nicolas's decision with David (R7-5).

### 5. The gains come from the predictor

With the constant or the permuted predictor, no design narrows the interval. On tissue at $n_L = 8$ the constant arm's widths are 0.971 for `rej_t`, 1.007 and 1.011 for the two cube designs and 1.023 for the mixture of rejective and simple random selection (`results/round7/ppi/S5_numbers/run1/s5_controls.csv`). The width gains in this account are information in $\bar f_g$.

---

# Part B. The other results, briefly

- **The stratified draw for $\theta_2$** (stands). Simple random draws inside a donor miss rare groups, and coverage fell to 0.23 on lung at two units per donor. Drawing stratified by group gives 0.885 to 0.913 for every $m \ge 6$ on every tissue task (`results/round5/ppi/E3_twolevel/e3_prediction_scores.csv`).
- **Skewed cluster contributions** (stands, and round 7 confirms it). The classical $t$ interval under-covers when slope contributions are skewed. In round 7's skewed simulation every design-based interval under-covered, the cube design's Hájek interval to a median of 0.820 with an accurate variance (`results/round7/ppi/S4b_cube_constant/_merged/s4b_report_numbers.csv`), so the shortfall is the reference distribution at these sizes, not the variance.
- **Allocation** (stands, and is the paper's own). The optimal number of labelled units per cluster with a predictor is $m^\star\sqrt{(1 - R^2_w)/\rho_c(n_L)}$, with $\rho_c$ the measured between ratio. The classical optimum at a cost ratio of 100 is 77.9 on kidney cancer, 125.0 on Indiana, 74.5 on lung and 268.7 on census by state (`results/round5/ppi/E5_joint/e5_allocation.csv`). Broska and Howes name cost-based allocation as future work.
- **The superpopulation interval has a limit** (stands). Round 5's covers below 0.85 in 916 of 8,820 simulation cells, all in regime A at $G$ of 15 and 24 (`results/round5/ppi/E5_joint/e5_superpop_undercoverage.csv`). In round 7 it was still the only interval near nominal for the superpopulation target at every $n_L$ in S2, and on matched cells the corrected Broska and Howes interval is close to it from $n_L = 6$.
- **GHCP and the number of calibration donors** (stands). At $K = 10$ GHCP is 1.23 to 1.55 times HCP's width and conservative. On kidney cancer at $o = 5$ it becomes narrower than HCP from $K = 12$ (`results/round5/conformal/W5_map/w5_report_numbers.csv`).
- **The small-$K$ conformal theory** (stands). Two parts of round 4's Proposition 2 are corollaries of Tibshirani, Barber and Ramdas. HCP is not pointwise dominated.
- **Process.** Round 5 reproduced round 4's rows in all but 2 of 1,694,142 matched rows (`docs/round05/i03/conformal/round5_conformal_W5_decisions.md`, sections 1 and 2). In round 7 every gate passed its provenance checks, and two of the oversight chat's own memos were corrected before handover by independent checks.

# Part C. What published work now holds

From the full reading of the three papers in `docs/round07/oversight/round07_ppi_positioning.md`, updated with round 7's results.

| Claim | Status |
|---|---|
| A cluster-robust PPI++ interval, valid as the number of clusters grows | Broska and Howes |
| PPI under weighted or whole-cluster labelling designs, with a cluster bootstrap | Kluger et al., without theory for the bootstrap |
| The gain at large cluster size, $1 - R^2_{\text{cluster}}\,G_U/(G_U + n_L)$, with the coefficient shrunk by $G_U/(G_U + n_L)$ | classical, and implied by Broska and Howes's formula. The paper gives the cluster-level reading, the no-gain corollary and the design-target version, $1 - R^2_{\text{cluster}}$ |
| For a superpopulation target, spreading labels over clusters beats labelling whole clusters | Broska and Howes. Their formula also supersedes round 4's condition, which left out the unlabelled clusters' term. With it, regime A's between-cluster term is at least $\sigma_u^2/G$, so regime B never loses on that term |
| The design-target regime comparison, costs per cluster and per unit, the level term | the paper's own |
| A design-target interval at 4 to 16 labelled clusters | the paper's own for the finite-population factor and the cross-fitting term. At the smallest $n_L$ a small-sample correction of Broska and Howes's interval does as well or better (A5, item 4) |
| Label-free balanced selection | classical in principle, unit-level balanced active inference is Chen et al. The few-cluster comparison on matched cells, and the cube design with the constant balanced at cluster level, are the paper's own |
| Inclusion-probability weighting of labelled clusters | prior art for independent Bernoulli selection (Kluger et al.). Its failure under fixed-size rejective selection is the paper's own negative result |
| The prediction-set map and the joint design | the paper's own. GHCP is the nearest work |

An unpublished lab manuscript on choosing slides to profile was also checked (`docs/round07/00_prep/round07_overlap_check.md`). It makes no claim the paper makes, and its details are in the private project documents only.

# Part D. What is not established

From round 5, with their status now:
- **The census null control at $n_L = 4$** (variance ratio 1.166 and 1.195 under the cluster-level null). Still not worked out.
- **Inclusion-probability weighting under rejective selection.** Answered (A5, item 1).
- **Whether HCP is dominated in expected width.** Still open.
- **The conditions for `rej_t`.** Still read from runs, now refined by the matched comparison (A4).
- **Real-data width margins in the prediction-set map** have no standard error. Still so.

From round 7:
- The superpopulation target for the cube designs and the mixture.
- Every result that took one value of the probability score, of $\tau$, of the mixture's $\epsilon$, or of the skewed simulation law.
- Why $\hat N$ misses $G$ under the cube design and whether a different final step fixes it, and why balancing the constant also helps on tissue.
- The lung $\theta_2$ differences from round 5 at $n_L$ of 6 and 8, read as ties at a float32 threshold and not checked.
- Why Broska and Howes's variance estimate is less conservative for the design target than its derivation says, read as the noise of $\hat\lambda$ and not derived.
- The cube designs' pair probabilities, which are simulated and not derived.

# Part E. The decisions that are Nicolas's

| # | Decision | With |
|---|---|---|
| R7-5 | The paper's positioning against Broska and Howes, given that a corrected version of their interval covers at four labelled clusters | David |
| R7-6 | Whether the tuned estimator uses one global coefficient below six labelled clusters, which changes a rule round 5 closed | |
| R7-7 | Which balanced design the paper recommends. `[proposed]` `rej_t` where its support and one balance variable allow, the cube design with the constant balanced as the design-based alternative | David |
| Q3 | Which result the paper leads with, now that the superpopulation regime comparison is published | his advisors |
| O5 | The positioning note's revision after the round closes | David |
