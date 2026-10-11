# Round 5, the results explained

11 October 2026. Written by the oversight chat for Nicolas after round 5 closed, in the same form as the round-4 explainer (`docs/round05/00_prep/deck2/deck2_new_results_explained.md`). Part A explains the four results that matter most, in order of importance. For each one it says what we found, why we looked for it, how it changes what we already knew, why it matters, and the theory with its expressions. A step is skipped only when it is algebra between two displayed lines, and the text says so each time. Part B describes the other results briefly. Part C lists what is not established.

The full derivations are in `docs/round05/tracks/ppi/round5_ppi_theory.md` and `docs/round05/tracks/conformal/round5_conf_theory.md`. The readings for the paper are in section 3 of the two closing memos, `docs/round05/i04/ppi/round5_ppi_E5_decisions.md` and `docs/round05/i03/conformal/round5_conformal_W5_decisions.md`. Every number is read from the file named beside it.

---

## The setting, once

There are $G$ clusters (donors, or states on the census task). Cluster $g$ has $M_g$ units (spots, or people). For unit $i$ of cluster $g$ we have the label $y_{gi}$, which costs money to measure, the prediction $\hat y_{gi}$, which is free, and a label-free weight $w_{gi}$ computed from the image or the covariates. Every estimand is written as a donor-weighted mean,

$$
\theta = \frac{1}{G}\sum_{g=1}^{G} \bar z_g, \qquad z_{gi} = w_{gi}\,y_{gi}, \qquad f_{gi} = w_{gi}\,\hat y_{gi},
$$

with $\bar z_g$ and $\bar f_g$ the cluster means. Two estimands matter here. For the slope $\theta_3$ the weight is the centred covariate over its variance, $w_{gi} = \tilde x_{gi}/v_g$, so $\bar z_g$ is the cluster's own least-squares slope. For the group difference $\theta_2$ the weight is $1/\pi_{N,g}$ on the neoplastic-dominant spots, $-1/\pi_{S,g}$ on the stromal-dominant spots and 0 elsewhere, so $\bar z_g$ is the difference of the two groups' means. In both cases the weights sum to zero within every cluster,

$$
\sum_i w_{gi} = 0 .
$$

That one fact drives the first result.

There are two ways to spend a labelling budget. In **regime A** we label every unit of $n_L$ clusters and none of the others. In **regime B** we label a few units, $m_g$, in every cluster. The **design target** is the fixed set of $G$ clusters we have, and the variance is over which clusters and units we label.

---

# Part A. The four main results

## A1. In regime B, most of what the predictions seemed to buy was a level term

### What we found

Round 4 measured what the predictions buy in regime B against a classical estimator that was the plain mean of $z_{gi}$ over the labelled units. That estimator carries a source of noise that has nothing to do with predicting expression. It is the outcome's level, $\mu_g = \bar y_g$, multiplied by the chance imbalance of the weights in the labelled units. Any predictor whose cluster mean is not zero removes that noise, including a constant. So part of round 4's gain was a constant doing the work.

Measured properly, the gain is much smaller on the Visium kidney tasks and still real on lung and census.

- **A constant predictor already narrows round 4's classical interval.** Its width ratio against round 4's classical estimator is 0.81 to 0.82 on kidney cancer, 0.85 to 0.86 on Indiana, 0.57 to 0.59 on lung and 0.12 to 0.13 on census income (`results/round5/ppi/E2_regimeB/e2_decomposition.csv`, $\theta_3$, donor-weighted, design target, $m \ge 5$).
- **Against the constant, the encoders add little or nothing on Visium.** Their width over the constant predictor's is 0.98 to 1.04 on the three kidney tasks, 0.74 to 0.84 on lung and 0.60 to 0.64 for the package predictor on census income (same file).
- **The paper's numbers, against the better classical estimator (form C).** In regime B the $\theta_3$ width ratio is 0.982 to 1.009 on the three kidney tasks, 0.706 to 0.847 on lung and 0.594 to 0.625 on the two census tasks, and the interval covers 0.855 to 0.950 over all 196 rows (`results/round5/ppi/E5_joint/e5_joint_design.csv`).

### Why we looked for it

Round 4's theory said the regime-B gain follows the within-cluster $R^2$ of the predictor. When the round-5 instruction was written, the oversight chat noticed that for a weight with cluster mean zero, the within-cluster $R^2$ of a constant predictor is not zero (`docs/round05/i01/ppi/round5_ppi_track.md` section 2.4). Stage E2 was set up to test that reading and to measure how much of the round-4 gain the constant accounts for.

### How it changes what we knew

Round 4 reported regime B's PPI-to-classical width as 0.81 to 0.84 on the Visium tasks, 0.42 on lung and 0.08 on ACS states (`results/round4/ppi/Q5_joint/q5_joint_design.csv`), and read the gain as coming from within-cluster prediction. That reading is withdrawn. On Visium the encoders buy nothing measurable in regime B. On lung they buy 15 to 29% of the width, and on census 38 to 41%. Every round-4 statement of what predictions buy in regime B is superseded by these numbers.

What survives is the regime comparison itself. Under the two-level estimator regime B stays narrower than regime A in 210 of 232 comparisons. On the kidney tasks the regime ratio is the same with and without the predictor, so regime B's advantage there is the design and not the predictor (`docs/round05/i03/ppi/round5_ppi_E4_decisions.md` section 3 item 4, from `results/round5/ppi/E3_twolevel/e3_regime_comparison.csv`).

### Why it matters

The comparison of the two regimes is the result the paper leads with, since the literature check found nothing like it. A reviewer who knows survey sampling would spot the level term at once, because it is the reason a regression estimator always carries an intercept. Had the paper claimed round 4's regime-B gains, its central empirical claim would have rested on a weak comparator. The constant predictor is now the primary control in every regime-B comparison.

### The theory

**Where the level enters.** Take one cluster in regime B with $m$ labelled units drawn without replacement, and drop the index $g$. Round 4's classical estimate of the cluster's value is the labelled mean of $z = wy$. Write $s_{wy}$ for the labelled units' sample covariance of $w$ and $y$ (divisor $m - 1$), and $\bar w_L$, $\bar y_L$ for their sample means. Then

$$
\frac{1}{m}\sum_{i \in L} w_i\,y_i = \frac{m-1}{m}\,s_{wy} + \bar w_L\,\bar y_L ,
$$

which is the definition of the sample covariance rearranged, so that algebra is skipped. The first term estimates the cluster's value. The second term has mean zero, because $\bar w_L$ has mean $\bar W = 0$, but it is not small. To first order $\bar y_L \approx \mu$, so the second term behaves like $\mu\,\bar w_L$, with variance

$$
\text{Var}(\mu\,\bar w_L) = \mu^2\Big(1 - \frac{m}{M}\Big)\frac{S_w^2}{m}.
$$

This is noise from the outcome's level times the chance imbalance of the weights. It does not involve how well anything predicts $y$.

**What a constant predictor removes, exactly.** Now let the predictor be a constant $c$ in the cluster, so $f = c\,w$, and take the rectifier $z - \lambda f$. Write the cluster moments with divisor $M$ as $\langle \cdot \rangle$. Because $\langle w \rangle = 0$, the covariance of $z$ with $w$ is $C = \langle w z \rangle = \langle w^2 y \rangle$ and the variance of $w$ is $A = \langle w^2 \rangle$. The within-cluster variance of the rectifier is

$$
V(\lambda) = V - 2\lambda c\,C + \lambda^2 c^2 A, \qquad V = \langle z^2 \rangle - \langle z \rangle^2 .
$$

This is a quadratic in $\lambda c$, minimised at $\lambda c = C/A$, where it removes

$$
D = \frac{C^2}{A}.
$$

So the share of the within variance that a constant can remove is

$$
L = \frac{D}{V} = \frac{\langle w^2 y \rangle^2}{\langle w^2 \rangle\,\big(\langle w^2 y^2 \rangle - \langle w y \rangle^2\big)} ,
$$

which is the squared within-cluster correlation of $z$ with $w$. It is exact and needs no model for $y$ (theory section 1.2).

**For the slope, the share is the level against the spread.** Decompose the outcome by the cluster's own least-squares line, $y_i = \mu + \beta\,\tilde x_i + \epsilon_i$, so that $\langle \epsilon \rangle = 0$ and $\langle \tilde x\,\epsilon \rangle = 0$ by construction. With $w = \tilde x/v$, the moments are

$$
A = \frac{1}{v}, \qquad C = \frac{\langle \tilde x^2 y \rangle}{v^2} = \frac{\mu v + \beta\,\langle \tilde x^3 \rangle + \langle \tilde x^2 \epsilon \rangle}{v^2} .
$$

When $\tilde x$ is symmetric in the cluster and $\epsilon$ is independent of $\tilde x$ with variance $\sigma^2$, the skewness and curvature terms vanish and

$$
D = \frac{\mu^2}{v}, \qquad V = \frac{\mu^2 + \sigma^2}{v} + \beta^2\Big(\frac{\langle \tilde x^4 \rangle}{v^2} - 1\Big).
$$

Standardising $\tilde x$ so that $v = 1$, with a normal covariate so that $\langle \tilde x^4 \rangle = 3$,

$$
L = \frac{\mu^2}{\mu^2 + \sigma^2 + 2\beta^2} .
$$

The share is large when the outcome's level is large against its spread within the cluster. Log income is such an outcome. On ACS by state the permuted predictor's within-cluster $R^2$ for the slope is 0.976 (`results/round5/ppi/E0_anchors/e0_brief_claims.csv`, from `results/round4/ppi/Q2_theory/q2_cluster_r2.csv`). That is why round 4's census gain looked so large. Note that $D = \mu^2/v = \mu^2 A$ is the variance of the $\mu\,\bar w_L$ term above, up to the sampling factor. The constant removes exactly the level noise.

**Form C removes the level without any predictor.** Form C estimates the cluster's slope from the labelled covariance, $\hat z = \frac{M-1}{M}\,s_{wy}$, which is the first term of the decomposition above and has no $\bar w_L\,\bar y_L$ term. It is unbiased under simple random sampling, because the sample covariance with divisor $m - 1$ is unbiased for the cluster covariance with divisor $M - 1$, and $\bar z = \frac{M-1}{M} S_{wy}$ when $\sum_i w_i = 0$. With a predictor, form C uses

$$
\hat z = \frac{M-1}{M}\Big(\lambda\,S_{w\hat y} + s_{w,\,y - \lambda\hat y}\Big),
$$

where $S_{w\hat y}$ is computed from all units, since predictions are free. If the predictor is constant in the cluster, $S_{w\hat y} = 0$, because a covariance with a constant is zero, and $s_{w,\,y - \lambda c} = s_{wy}$, because subtracting a constant does not change a covariance. So under form C a constant predictor gives exactly the classical estimate (theory section 2.3). The code confirms it in 420 of 420 simulation cells with difference 0 (`results/round5/ppi/E3_twolevel/e3_sim_summary.csv`). Measured against form C's classical estimator, a predictor is credited only with what it knows about units within a cluster, which is the right measure. For $\theta_3$ form C's classical estimator is also 4 to 18% narrower than round 4's pooled form (`results/round5/ppi/E3_twolevel/e3_prediction_cells.csv`), and it became the paper's within-cluster estimator.

---

## A2. The design-target interval was missing a term, and coverage is restored

### What we found

The round-4 interval for regime A ignores one piece of the variance. When most clusters are labelled, the coefficients fitted on the two halves of the labelled clusters add a term that the finite-population factor does not shrink, and the interval under-covers. The worst case in simulation is 0.840 at $G = 15$ and $n_L = 12$, where the ratio of estimated to empirical variance is 0.69 (`results/round5/ppi/E1_interval/e1_sim_grid.csv`). With the term restored, the ratio is 0.974 to 1.013 and coverage 0.888 to 0.903, against 0.691 to 0.909 and 0.840 to 0.886 without it (`results/round5/ppi/E3a_crossfit/e3a_sim_prediction_cells.csv`). On lung at $n_L = 12$ the corrected $\theta_3$ interval is 0.702 of the classical width against 0.649 uncorrected, and it covers 0.885, the same as the classical interval, against 0.870 uncorrected (`results/round5/ppi/E3a_crossfit/e3a_masking_E3a3_table_nL8_12_16.csv`). The corrected interval is `textbook_t|fpc|lin|xf`, the paper's design-target interval.

### Why we looked for it

Stage E1 validated round 4's final interval in simulation before the paper relies on it. The shortfall was not spread over the grid. It sat where $n_L/G$ is large and grew with $R^2$, and it vanished when both halves' coefficients clipped to the same value. That pattern pointed at the cross-fitting. Lung has only 15 donors, so its real-task coverage at $n_L = 12$, 0.86 to 0.87 against 0.885 for the classical interval, showed the same thing (`results/round4/ppi/Q4a_recompute/q4a_table61.csv`).

### How it changes what we knew

Round 4 said the final interval was valid with 4 to 12 labelled clusters. That holds when the sampling fraction is small. When most clusters are labelled the round-4 interval is too narrow, and part of round 4's apparent gain on lung at large $n_L$ was that missing variance. The correction costs width only where the term is real. At $G = 51$ the two intervals differ by less than 0.01 in coverage (`results/round5/ppi/E3a_crossfit/e3a_sim_prediction_cells.csv`, prediction E3a.2).

### Why it matters

A design-target interval is the paper's main inferential tool, and the design target is most interesting exactly when the labelled clusters are a large share of the clusters we have. A small-$G$ setting like lung, with 15 donors, is common in spatial transcriptomics. Without the term, the interval would under-cover in the setting the paper most wants to cover.

### The theory

**The estimator.** Draw a simple random sample $L$ of $n$ clusters and split it at random into halves $A$ and $B$ of sizes $n_A = \lfloor n/2 \rfloor$ and $n_B = n - n_A$. Fit the coefficient $\lambda_A$ on half $A$ and apply it to half $B$, and the reverse. The coefficient on the known total $\bar F$ is the mean of the applied coefficients,

$$
c' = \frac{n_B\,\lambda_A + n_A\,\lambda_B}{n}, \qquad \hat\theta = c'\,\bar F + \frac{1}{n}\sum_{g \in L}\big(z_g - \lambda_{(g)} f_g\big),
$$

where $z_g$, $f_g$ are the cluster values and $\lambda_{(g)}$ is the coefficient cluster $g$ carries.

**An exact identity.** Write $\delta = \lambda_B - \lambda_A$, $\Delta = \bar f_A - \bar f_B$ and $\kappa = n_A n_B/n^2$, which is $1/4$ for even $n$. Then, draw by draw,

$$
\hat\theta = \underbrace{\bar z_L - c'\,(\bar f_L - \bar F)}_{T_1} \; - \; \underbrace{\kappa\,\delta\,\Delta}_{T_2}.
$$

It follows because $\lambda_B - c' = n_B\delta/n$ and $\lambda_A - c' = -n_A\delta/n$, after collecting terms, which is algebra and is skipped.

**Which part the finite-population factor governs.** $T_1$ is a labelled-sample mean minus a coefficient times $\bar f_L - \bar F$. Both $\bar z_L - \bar Z$ and $\bar f_L - \bar F$ have variances proportional to $1 - n/G$, and both are zero when every cluster is labelled. $T_2$ is a difference between the two halves. For disjoint simple random samples,

$$
\text{Var}(\bar f_A) = \Big(1 - \frac{n_A}{G}\Big)\frac{S_f^2}{n_A}, \qquad \text{Cov}(\bar f_A, \bar f_B) = -\frac{S_f^2}{G},
$$

with $S_f^2$ the variance of $f_g$ over the $G$ clusters (divisor $G - 1$). So

$$
\text{Var}(\bar f_A - \bar f_B) = \Big(\frac{1}{n_A} + \frac{1}{n_B}\Big)S_f^2 ,
$$

because the two covariance terms cancel the two finite-population terms. There is no factor $1 - n/G$. At $n = G$ the effect is sharpest. Then $T_1 = \theta$ exactly, so $\hat\theta - \theta = -\kappa\,\delta\,\Delta$, which is not zero whenever the halves' coefficients differ, while round 4's variance estimate $(1 - n/G)\,s_e^2/n$ is exactly zero.

**How much is missed, under the normal law.** Take $z_g = \alpha + \lambda^\circ f_g + u_g$ with $u_g$ of variance $\sigma^2$ independent of $f_g$, even $n = 2h$ and no clipping. Each half's coefficient is its own least-squares slope. For normal $f$, the half's sum of squares is $S_f^2$ times a $\chi^2_{h-1}$ variable, and $E[1/\chi^2_{h-1}] = 1/(h-3)$, so

$$
E[\delta^2]\,S_f^2 = 2\cdot\frac{\sigma^2}{h-3} = \frac{4\sigma^2}{n-6},
$$

since the two halves' slope errors are independent. The true variance follows from the identity. $T_1$ contributes $(1 - n/G)\big(\sigma^2 + \text{Var}(c')\,S_f^2\big)/n$ with $\text{Var}(c') = E[\delta^2]/4$, and $T_2$ contributes $\kappa\,E[\delta^2]\,S_f^2/n$ with $\kappa = 1/4$. So

$$
\text{Var}(\hat\theta) \approx \frac{\sigma^2}{n}\Big[\Big(1 - \frac{n}{G}\Big)\Big(1 + \frac{1}{n-6}\Big) + \frac{1}{n-6}\Big].
$$

The round-4 estimate uses the spread of the contributions $e_g$ over the labelled clusters. Its sum of squares splits into the two halves' residual sums of squares, with expectation $(n-4)\sigma^2$, the terms $\delta^2$ times each half's sum of squares of $f$, with expectation $4\sigma^2(n-4)/(n-6)$, and a between-half term with expectation about $\sigma^2$ (theory section 2.0). So

$$
E[s_e^2] \approx \frac{\sigma^2}{n-1}\Big[(n-3) + \frac{4(n-4)}{n-6}\Big].
$$

The true variance minus the expected estimate $(1 - n/G)\,E[s_e^2]/n$ is then, after algebra that is skipped,

$$
\frac{\sigma^2}{n}\Big[\Big(1 - \frac{n}{G}\Big)\frac{3 - n}{(n-1)(n-6)} + \frac{1}{n-6}\Big].
$$

When $n/G$ is small this is a shortfall of about 3% at $n = 12$, because the extra $\delta^2$ inside $s_e^2$ and the overfitted residuals nearly cancel. The factor $1 - n/G$ then removes a fraction $n/G$ of the whole $T_2$ term, and that is what is missed. At $G = 15$ and $n = 12$ the formulas give a ratio of expected estimate to true variance of 0.65, close to the 0.69 seen in the worst simulated cell (`docs/round05/tracks/ppi/round5_ppi_theory.md` section 2.0).

**The correction.** Restore what the factor removed,

$$
\widehat{\text{Var}}_{\text{xf}} = \Big(1 - \frac{n}{G}\Big)\frac{s_e^2}{n} + \frac{n}{G}\cdot\frac{\overline{(\lambda_{(g)} - c')^2}_L\;s_f^2}{n},
$$

with $s_f^2$ the labelled clusters' sample variance of $f_g$. The mean of the squared deviations equals $\kappa\,\delta^2$ for any split, so the added term estimates the part of $T_2$ the factor removed. Under the normal law it removes the $1/(n-6)$ term of the shortfall, and at $G = 15$ and $n = 12$ the expected ratio becomes 0.985 (same section). When both halves get the same coefficient, every $\lambda_{(g)} = c'$, and the added term is zero, so the two intervals coincide whenever there is nothing to correct.

---

## A3. Inside the target donor, the full conformal set is the method from 9 labelled spots

### What we found

For a prediction set for the spots of a new donor, with $o$ labelled spots from that donor, the narrowest valid method on real data at $K = 10$ calibration donors and 90% is

- HCP, which uses no labelled target spots, up to $o = 5$ on every task;
- from $o = 9$, the full conformal set built from the target donor's own residuals (`within_full`), at 0.416 to 0.677 of HCP's width on every task.

The two exceptions are $o = 17$, where the half split is narrower by discreteness, and Indiana at $o$ from 9 to 15, where the plain split is narrower by at most 2%. `within_full` covers 0.900 to 0.923 at $o$ of 10, 25 and 100, in line with its guarantee (`results/round5/conformal/W5_map/w5_report_numbers.csv`). In simulation it is the narrowest valid method in 1,350 of 1,440 cells at a between-cluster share of 0.3 and in all 1,440 at 0.9 (`results/round5/conformal/W1_sim/w1_whole_grid_counts.csv`). In GHCP's own simulation designs it is 2 to 4 times narrower than GHCP from 9 labelled units, wherever GHCP is finite (`results/round5/conformal/W2_ghcp_settings/w2_sim_designs.csv`).

### Why we looked for it

Round 4 left a gap between two within-donor methods. The plain split conformal set on the uncentred residuals is finite from $o = 9$ at 90% but does not remove the donor's offset. The half split, the GHCP paper's Std-CP baseline, centres on half the spots and calibrates on the other half, so it is finite only from $o = 17$. The textbook full conformal set uses all $o$ spots both to centre and to rank. It was added in stage W1 as the obvious missing comparator, not as a new method (`docs/round05/i01/conformal/round5_conformal_track.md` section 2).

### How it changes what we knew

Round 4 recommended the plain split from $o = 10$ and the half split from $o = 25$, and said labelled spots buy little below about 25. Both recommendations are replaced from $o = 9$. On CCRCC, `within_full` is 2.116 wide at $o = 10$ against the plain split's 2.321, 1.967 at $o = 25$ against 2.137 and 2.300, and 1.709 at $o = 100$ against 1.754 and 2.109 (`results/round5/conformal/W5_map/w5_report_numbers.csv`). Round 4's three values reproduce exactly. So labelled spots of the target donor start paying at 9, not at 25.

### Why it matters

This is the prediction-set half of the paper's design question, how to split a labelling budget between other donors and the target donor. The answer is now one clean rule on real data. Below 9 labelled target spots, use the other donors (HCP). From 9 on, use the target donor's own spots (`within_full`). It also lets the paper state the comparison with GHCP fairly. The released GHCP code calibrates HCP on half of the reference groups, so the GHCP paper's design with 20 groups sits at 10 calibration clusters, the same place on the axis as our real-data map at $K = 10$ (`results/round5/conformal/W5_map/w5_map.csv`).

### The theory

**The construction.** Let $r_1, \dots, r_o$ be the residuals $y - \hat y$ of the target donor's labelled spots, with sum $S$. For a candidate residual $r$ of a new spot, fit the mean to all $o + 1$ residuals,

$$
c(r) = \frac{S + r}{o + 1},
$$

score each residual by its distance from that mean, $s_i(r) = |r_i - c(r)|$ and $s(r) = |r - c(r)|$, and keep $r$ when

$$
1 + \#\{i : s_i(r) \ge s(r)\} > \alpha\,(o + 1).
$$

**Each comparison holds on an interval.** Multiply the condition $|r_i - c(r)| \ge |r - c(r)|$ through by $o + 1$. It becomes

$$
\big|(o+1)\,r_i - S - r\big| \ge \big|o\,r - S\big| .
$$

Squaring both sides and factorising the difference of squares gives

$$
(o+1)\,(r_i - r)\,\big[(o+1)\,r_i - 2S + (o-1)\,r\big] \ge 0,
$$

where the factorisation is algebra and is skipped. The left side is a quadratic in $r$ with negative leading coefficient $-(o+1)(o-1)$ and roots

$$
r = r_i \qquad \text{and} \qquad r = \frac{2S - (o+1)\,r_i}{o-1}.
$$

So the condition holds on the closed interval $I_i$ between these two roots. The set is the set of $r$ that lie in more than $\alpha(o+1) - 1$ of the intervals $I_1, \dots, I_o$, which is found exactly from $2o$ end points. On the real data it was always a single interval (`results/round5/conformal/W3_real/merged/w3_within_coverage.csv`).

**When it is finite.** If $\alpha(o+1) < 1$, the condition holds with no interval at all, so every $r$ is kept and the set is the whole line. At 90% that is $o \le 8$ (`docs/round05/i02/conformal/round5_conf_final_report.md` section 4). From $o = 9$ the condition needs $r$ to lie in at least one $I_i$, and each $I_i$ is bounded, so the set is finite.

**Its coverage.** Let the true residual of the new spot be $r_{o+1}$, exchangeable with $r_1, \dots, r_o$. At $r = r_{o+1}$ the fitted mean is the mean of all $o + 1$ residuals, which is symmetric in them, so the $o + 1$ scores are exchangeable too. Let $k$ be the number of scores at least as large as the new spot's, counting itself. With continuous residuals there are no ties, so $k$ is uniform on $\{1, \dots, o+1\}$. The new spot is covered when $k > \alpha(o+1)$, so

$$
P(\text{covered}) = 1 - \frac{\lfloor \alpha(o+1) \rfloor}{o+1} = \frac{\lceil (1-\alpha)(o+1) \rceil}{o+1}.
$$

At $o = 9$ and $\alpha = 0.1$ this is exactly 0.9. W3's check confirmed it on the real data to within 0.005 in all 362 cells (`results/round5/conformal/W3_real/merged/w3_acceptance.csv`). The guarantee needs only that the target donor's labelled and new spots are exchangeable. It does not involve the other donors at all.

**Why it is narrower than the two splits.** The plain split ranks the uncentred residuals $|r_i|$, so the donor's offset, the mean of its residuals, inflates every score. The half split removes the offset but estimates it from $\lfloor o/2 \rfloor$ spots and ranks only the other $\lceil o/2 \rceil$, so it needs $\lceil o/2 \rceil + 1 > 1/\alpha$ before it is finite and pays twice for the halving. The full set centres on all the spots and ranks all of them, at the same coverage. Against HCP, it does not have to cover the spread of other donors' residuals, which is what makes HCP wide when donors differ.

---

## A4. Choosing balanced clusters cuts the variance of the plain labelled mean, under conditions

### What we found

In regime A we can choose which clusters to label using quantities that need no label, such as each cluster's mean prediction $\bar f_g$. Rejective selection draws samples of $n_L$ clusters until one is balanced, meaning its mean of the balance variable is close to the population mean. Under this design the variance of the plain classical mean falls a lot, and an interval built for the design, `rej_t`, captures most of the fall.

- At $n_L = 8$ for $\theta_3$, balancing on the estimand's own $\bar f_g$ at an acceptance probability of 0.01, `rej_t` is 0.726 of the simple-random classical width on kidney cancer with `uni_v2` and 0.551 on census by state, against 0.852 and 0.618 for the tuned PPI estimator under simple random selection (`results/round5/ppi/E4b_rejective/e4b_rej_width_ratios.csv`). So in these cells balanced selection with no coefficient beats tuning.
- In simulation under the normal law, `rej_t` covers 0.894 to 0.906 in 60 of 60 cells with $n_L \ge 6$ and enough distinct acceptable samples (`results/round5/ppi/E4b_rejective/e4b_prediction_scores.csv`).
- On the real tasks, over the 960 cells with at least 1,000 acceptable samples, it covers with median 0.878, within 0.03 of the classical interval in 861 (`docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`, from `results/round5/ppi/E4b_rejective/e4b_rej_width_ratios.csv`). It fails with two balance variables at few residual degrees of freedom, down to 0.641 to 0.684 on Indiana $\theta_2$ at $n_L = 6$.

### Why we looked for it

Stage E4 asked which clusters to label. Balancing reduced the variance of the classical mean as theory predicted, but the ordinary interval did not see it. Under balanced selection its ratio of estimated to empirical variance rose to 1.2 to 1.5 on the kidney cancer tasks, 3.2 to 4.0 on lung, and 3.3 and 7.4 on the two census tasks (`results/round5/ppi/E4_selection/e4_selection_grid.csv`). So stage E4b derived an interval that uses the balance.

### How it changes what we knew

Round 4 had only one way to use predictions in regime A, which was tuning a coefficient, and that costs about $p/(n_h - p - 2)$ in variance with few clusters. Balanced selection uses the predictions at the design stage instead, so nothing is tuned and there is no tuning cost. That is why it beats tuning at $n_L = 8$. It enters the paper as a design result with conditions, and the paper's default stays simple random selection.

### Why it matters

It answers the "which clusters" half of the labelling-budget question, and it is the one place where predictions help in regime A at small $n_L$ without the tuning cost. It also links the paper to the rerandomisation literature (Morgan and Rubin 2012), carried over from treatment assignment to sampling.

### The theory

**A decomposition that holds for every sample.** Let $x_g$ be the $k$ balance variables, known for every cluster, with population mean $\bar X$ and covariance $S_X$ (divisor $G - 1$). Let $B = S_X^{-1}S_{Xz}$ be the population least-squares coefficient of $z_g$ on $x_g$ over the $G$ clusters, and $e_g = z_g - \bar Z - B^\top(x_g - \bar X)$ the residual, so that $\sum_g e_g = 0$ and $\sum_g e_g(x_g - \bar X) = 0$. Then for any sample $L$,

$$
\bar z_L - \bar Z = \bar e_L + B^\top(\bar x_L - \bar X).
$$

**Under simple random sampling the two terms are uncorrelated.** With $f = n/G$,

$$
\text{Var}(\bar e_L) = (1-f)\frac{S_e^2}{n}, \qquad \text{Cov}(\bar x_L) = (1-f)\frac{S_X}{n}, \qquad \text{Cov}(\bar e_L, \bar x_L) = (1-f)\frac{S_{eX}}{n} = 0,
$$

the last because $B$ is the least-squares coefficient, which makes $S_{eX} = 0$. This is exact for every $G$ and $n$. When $n$ and $G - n$ are large, the finite-population central limit theorem makes $(\bar e_L, \bar x_L)$ nearly jointly normal, and uncorrelated jointly normal terms are independent.

**Rejection restricts only the balance term.** The design accepts a sample when its Mahalanobis distance $(\bar x_L - \bar X)^\top S_X^{-1}(\bar x_L - \bar X)$ is at or below its $p_a$ quantile. In standardised form, with $\xi$ the standardised $\bar x_L - \bar X$, approximately $N(0, I_k)$, acceptance is the event $|\xi|^2 \le q_a$, with $q_a$ the $p_a$ quantile of $\chi^2_k$. Because $\bar e_L$ is independent of $\xi$, conditioning on acceptance leaves it unchanged. The accepted $\xi$ keeps mean zero by symmetry, and its covariance is a multiple of the identity, $v_a I_k$, again by symmetry. Taking the trace,

$$
k\,v_a = E\big[|\xi|^2 \,\big|\, |\xi|^2 \le q_a\big] = \frac{E\big[\chi^2_k\,\mathbf{1}\{\chi^2_k \le q_a\}\big]}{P(\chi^2_k \le q_a)} .
$$

The $\chi^2$ densities satisfy $x\,p_k(x) = k\,p_{k+2}(x)$, which follows from the Gamma function identity $\Gamma(k/2 + 1) = (k/2)\,\Gamma(k/2)$ and is algebra, so it is skipped. Integrating up to $q_a$ gives $E[\chi^2_k\,\mathbf{1}\{\chi^2_k \le q_a\}] = k\,P(\chi^2_{k+2} \le q_a)$, and so

$$
v_a = \frac{P(\chi^2_{k+2} \le q_a)}{P(\chi^2_k \le q_a)}.
$$

This is Morgan and Rubin's Theorem 3.1 (`docs/round05/tracks/ppi/round5_ppi_theory.md` section 3.3). Its proof uses only the normality of the restricted vector and the spherical acceptance region, so it carries over to sampling. With $k = 1$, $v_a$ is 0.0053 at $p_a = 0.1$ and 0.00005 at $p_a = 0.01$, and with $k = 2$ it is 0.0518 and 0.0050 (`results/round5/ppi/E5_joint/e5_report_numbers.csv`).

**The variance of the classical mean under the design.** Putting the two terms back together,

$$
E_{D2}(\bar z_L) = \theta, \qquad \text{Var}_{D2}(\bar z_L) = \frac{1-f}{n}\Big(S_e^2 + v_a\,B^\top S_X B\Big).
$$

Under simple random sampling the bracket is $S_e^2 + B^\top S_X B = S_z^2$, so the variance ratio is

$$
1 - (1 - v_a)\,R^2_c, \qquad R^2_c = \frac{B^\top S_X B}{S_z^2},
$$

which is close to $1 - R^2_c$ because $v_a$ is small. Balancing removes almost all of the variance the balance variable explains, with nothing tuned.

**Why the ordinary interval misses it, and the interval that sees it.** The ordinary interval uses $(1-f)\,s_z^2/n$, the spread of $z_g$ among the labelled clusters. Balancing the mean of $x$ does not change the expected spread of $z_g$ within the sample, so that interval still estimates the simple-random variance. The interval `rej_t` estimates the two pieces separately. Fit $z_g$ on $x_g$ with an intercept over the labelled clusters, giving $\hat b$ and the residual variance $s^2_{\text{res}}$ with divisor $n - k - 1$, and let $S_x$ be the labelled clusters' covariance of $x_g$. Then

$$
\widehat{\text{Var}}_{\text{rej}} = \Big(1 - \frac{n}{G}\Big)\frac{s^2_{\text{res}} + v_a\,\hat b^\top S_x\,\hat b}{n},
$$

with $t_{n-k-1}$ as the reference. The point estimate is still the plain mean $\bar z_L$, so $\hat b$ enters only the variance and there is no tuning cost. In a synthetic check the empirical variance of the accepted means is 1.017 to 1.077 times the formula's, and the mean estimate is 0.916 to 1.039 times the empirical variance (`results/round5/ppi/E4b_rejective/tests/e4b_tests.csv`).

**The conditions, which the failures show.** The derivation needs a normal approximation over clusters, enough distinct acceptable samples for the accepted set to behave like a smooth truncation, and enough residual degrees of freedom. On lung, with 15 donors and $n_L = 8$, there are 6,435 possible samples and $p_a = 0.01$ keeps about 64, so lung's balanced design is nearly fixed (`docs/round05/tracks/ppi/round5_ppi_theory.md` section 3.5). The paper states the result for one balance variable, the estimand's own $\bar f_g$, at least 1,000 distinct acceptable samples and $n_L$ of 8 or more (`docs/round05/i04/ppi/round5_ppi_E5_decisions.md` section 3 item 3). The worst real cells have $n - k - 1 = 3$. The paper says these conditions were read from the same runs and are not a validated rule.

---

# Part B. The other results, briefly

- **Form C and the stratified draw for $\theta_2$.** Form C (A1) is the paper's within-cluster estimator. For the group difference, simple random draws inside a donor miss rare groups, and coverage fell to 0.23 on lung at two units per donor (`results/round5/ppi/E2_regimeB/e2_regimeB_grid.csv`). Drawing the labelled spots stratified by group repairs it, at 0.885 to 0.913 for every $m \ge 6$ on every tissue task (`results/round5/ppi/E3_twolevel/e3_prediction_scores.csv`).
- **Skewed cluster contributions are the larger source of under-coverage on real data.** The classical $t$ interval under-covers when the slope contributions are skewed, which tuning does not cause. The median absolute skewness is 1.76 on kidney cancer, 0.87 on lung and 0.60 on Indiana (`results/round5/ppi/E1_interval/e1_report_numbers.csv`). The paper states this beside A2.
- **Allocation, with the measured between ratio.** The optimal number of labelled units per cluster with a predictor is $m^\star\sqrt{(1 - R^2_w)/\rho_c(n_L)}$, where $\rho_c(n_L)$ is the measured between-cluster variance ratio, which is 1 below $n_L = 6$ because the between coefficient is set to zero there. The classical optimum at a cost ratio of 100 is 77.9 on kidney cancer, 125.0 on Indiana, 74.5 on lung and 268.7 on census by state (`results/round5/ppi/E5_joint/e5_allocation.csv`). The optimum is flat. Labelling 0.61 of the optimal number costs 6% in variance in the lung example of the E5 memo.
- **The superpopulation-target interval has a limit.** It covers below 0.85 in 916 of 8,820 simulation cells, all in regime A with a predictor at $G$ of 15 and 24, with minimum 0.705 (`results/round5/ppi/E5_joint/e5_superpop_undercoverage.csv`). Real-data claims use the design target.
- **GHCP and the number of calibration donors.** At $K = 10$ GHCP is 1.23 to 1.55 times HCP's width and covers 0.992 to 0.999, so it is wide and conservative there. On CCRCC at $o = 5$ it becomes narrower than HCP from $K = 12$ and reaches 0.831 at $K = 20$. With the prediction head held fixed it falls from 5.304 to 2.702 as $K$ goes from 10 to 20, against HCP's 4.469 to 3.252, so the number of calibration donors alone produces the fall (`results/round5/conformal/W5_map/w5_report_numbers.csv`). On Indiana it stays within 4% of HCP.
- **The small-$K$ theory, checked against the literature.** Two parts of round 4's Proposition 2 are direct corollaries of Tibshirani, Barber and Ramdas, Theorems 3 and 7. The probability bound for randomised methods and Proposition 1's floor were not found in print and rest on round 4's proofs. For $K + 1 \ge 1/\alpha$, HCP is not tight, and no valid symmetric method is narrower than HCP at one configuration of continuous laws without being wider at another that contains a degenerate group. So HCP is not pointwise dominated (`docs/round05/tracks/conformal/round5_conf_theory.md`, B.5).
- **Process.** Code reached Longleaf as bundles with read-only snapshots, one push per gate, and every sub-agent stamp carried its own frame id by the end. The round-4 rows reproduced in all but 2 of 1,694,142 matched rows, both within a test spot or the eighth decimal place (`docs/round05/i03/conformal/round5_conformal_W5_decisions.md` sections 1 and 2).

# Part C. What is not established

- **Why balanced selection's null control fails in two census designs at $n_L = 4$.** The variance ratio under the cluster-level null control is 1.166 and 1.195, 3.2 to 3.8 bootstrap standard errors above 1 (`results/round5/ppi/E4b_rejective/e4b_bootstrap.csv`). The bootstrap leaves out the spread over permutations, so this may be within chance, but that was not worked out.
- **Inclusion-probability weighting under rejective selection.** Each cluster's inclusion probability can be computed by simulating the design before any label is bought. A Horvitz-Thompson or Hájek mean weighted by those probabilities would be unbiased for the design. Whether it removes the small-$n_L$ bias and what it costs in width is the first question for a next round (`docs/round05/i04/ppi/round5_ppi_E5_decisions.md` section 5).
- **Whether HCP is dominated in expected width.** The induction on the number of degenerate groups failed at its last step. The paper states it as open.
- **The conditions for `rej_t`** were read from the same runs and are not a validated rule.
- **Real-data width margins in the prediction-set map have no standard error.** Only the spread over folds of coverage is given.
