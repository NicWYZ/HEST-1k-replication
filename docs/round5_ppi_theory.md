# Round 5 PPI track, the theory

Written before the experiments it supports, as `docs/decisions/round5_ppi_track.md` asks (E2, "Derivation first"; transcribed in `docs/round5_ppi_plan.md`). Section 1 is written before any E2 job. Section 2 is written at E3, after the E2 gate memo. None of the results below is new. They are finite-population moments of a weighted unit-level variable, in the notation of the brief.

## 1. The level term in regime B

### 1.1 Setting and conventions

Cluster $g$ has $M_g$ units. Every moment in this section is a finite-population moment over the $M_g$ units of one cluster, with divisor $M_g$, and is written $\langle \cdot \rangle_g$. For example, $\langle x \rangle_g = M_g^{-1}\sum_i x_{gi}$. The code computes the design constants this way. `round3_b1_ppi.design_consts` takes the covariate's variance with `ddof=0` and the group fractions as plain proportions.

The estimand's unit-level variable is $z_{gi} = w_{gi}\,y_{gi}$, with label-free weights $w_{gi}$. Its prediction counterpart is $f_{gi} = w_{gi}\,\hat y_{gi}$. For both estimands of this section the weights have cluster mean zero, $\langle w \rangle_g = 0$ (brief section 2.3, tissue tasks; on ACS $\theta_2$ is the mean, $w = 1$, and this section does not apply there).

In regime B the classical estimate of cluster $g$'s value is the mean of $z$ over $m_g$ labelled units drawn without replacement. Its design variance is

$$
\text{Var}(\hat z_g) = \Big(1 - \frac{m_g}{M_g}\Big)\frac{S^2_{z,g}}{m_g}, \qquad S^2_{z,g} = \frac{M_g}{M_g - 1}\,V_g, \qquad V_g = \langle z^2 \rangle_g - \langle z \rangle_g^2 .
$$

The factor $M_g/(M_g - 1)$ multiplies every variance and covariance of this section alike, so it cancels from every share below and I work with $V_g$.

### 1.2 What a constant predictor removes, in general

Take a predictor that is constant in a cluster, $\hat y_{gi} = c_g$. Then $f_{gi} = c_g\,w_{gi}$. In regime B the rectifier is $z - \lambda f = z - \lambda c_g w$, and its within-cluster variance is

$$
V_g(\lambda) = V_g - 2\lambda c_g\,C_g + \lambda^2 c_g^2\,A_g, \qquad C_g = \langle w\,z \rangle_g = \langle w^2 y \rangle_g, \qquad A_g = \langle w^2 \rangle_g .
$$

Both moments are written without centring because $\langle w \rangle_g = 0$, so $\text{Cov}_g(z, w) = \langle wz \rangle_g$ and $\text{Var}_g(w) = \langle w^2 \rangle_g$. If cluster $g$ had its own coefficient, the best one would be $\lambda c_g = C_g/A_g$, and it would remove

$$
D_g = \frac{C_g^2}{A_g},
$$

so the share of the cluster's within variance that a constant predictor can remove is

$$
L_g = \frac{D_g}{V_g} = \frac{\langle w^2 y \rangle_g^2}{\langle w^2 \rangle_g\,\big(\langle w^2 y^2 \rangle_g - \langle w y \rangle_g^2\big)} .
$$

This is exact. It needs no model for $y$ and no assumption on the law of the covariate. It is the squared within-cluster correlation of $z$ with $w$, which is the within-cluster $R^2$ of the constant predictor.

**The pooled coefficient that regime B uses.** Round 4's regime B fits one coefficient for each half of the clusters, the pooled within-cluster slope of $z$ on $f$, clipped to $[0, 1]$, and applies it to the other half (`regime_b` in `code/scripts/round4_ppi_q3_regimes.py`). With a common constant $c$, the task-wide mean of the predictor, the design variance of the donor-weighted estimate is proportional to $\sum_g \omega_g V_g(\lambda)$ with $\omega_g = (1 - m_g/M_g)\,M_g/\{(M_g - 1)\,m_g\}$. Minimised over $\lambda$,

$$
\lambda^\star c = \frac{\sum_g \omega_g C_g}{\sum_g \omega_g A_g}, \qquad L = \frac{\big(\sum_g \omega_g C_g\big)^2}{\sum_g \omega_g A_g\ \sum_g \omega_g V_g} .
$$

$L$ is the share that E2 calls the level share. By the Cauchy-Schwarz inequality $L \le \sum_g \omega_g D_g / \sum_g \omega_g V_g$, with equality when $C_g/A_g$ is the same in every cluster. If $\lambda^\star > 1$ the clip binds at $\lambda = 1$, and the share removed is $\{2c\sum_g\omega_g C_g - c^2\sum_g\omega_g A_g\}/\sum_g\omega_g V_g$, which is smaller than $L$. The donor-constant predictor has $c_g$ equal to the cluster's own mean prediction. Its pooled share is the same expression with $c_g C_g$ and $c_g^2 A_g$ inside the sums, and it reaches $\sum_g\omega_g D_g/\sum_g\omega_g V_g$ when $c_g$ is proportional to $C_g/A_g$.

The cross-fitting does not change these expressions. It replaces $\lambda^\star$ by a half-sample estimate, which adds a tuning cost of order $1/G$ that section 5.2 of `docs/round4_ppi_theory.md` describes for the cluster level. E2's prediction E2.4 compares the simulated variance ratio with $1 - L$ at $m \ge 20$, where that cost and the sampling error of $s^2_{r,g}$ are small.

### 1.3 The slope $\theta_3$

Here $w_{gi} = \tilde x_{gi}/v_g$, with $\tilde x = x - \langle x \rangle_g$ and $v_g = \langle \tilde x^2 \rangle_g$. Decompose the outcome by the cluster's own least-squares line,

$$
y_{gi} = \mu_g + \beta_g\,\tilde x_{gi} + \epsilon_{gi}, \qquad \mu_g = \langle y \rangle_g, \qquad \beta_g = \frac{\langle \tilde x\,y \rangle_g}{v_g},
$$

so that, by construction and with no assumption, $\langle \epsilon \rangle_g = 0$ and $\langle \tilde x\,\epsilon \rangle_g = 0$. Write $\kappa_{3,g} = \langle \tilde x^3 \rangle_g$ and $\kappa_{4,g} = \langle \tilde x^4 \rangle_g$. The cluster's value is $\langle z \rangle_g = \langle \tilde x y \rangle_g / v_g = \beta_g$.

**The within variance.** Substituting the decomposition,

$$
z_{gi} - \beta_g = \mu_g\frac{\tilde x_{gi}}{v_g} + \beta_g\Big(\frac{\tilde x_{gi}^2}{v_g} - 1\Big) + \frac{\tilde x_{gi}\,\epsilon_{gi}}{v_g}.
$$

Squaring and averaging over the cluster's units, using $\langle \tilde x^2 \rangle_g = v_g$ and $\langle \tilde x\epsilon \rangle_g = 0$,

$$
V_g = \frac{\mu_g^2}{v_g} + \beta_g^2\Big(\frac{\kappa_{4,g}}{v_g^2} - 1\Big) + \frac{\langle \tilde x^2\epsilon^2 \rangle_g}{v_g^2} + \frac{2\mu_g\beta_g\,\kappa_{3,g}}{v_g^2} + \frac{2\mu_g\,\langle \tilde x^2\epsilon \rangle_g}{v_g^2} + \frac{2\beta_g\,\langle \tilde x^3\epsilon \rangle_g}{v_g^2} .
$$

The six terms come from the three squares and the three cross products of the three terms above, in that order. The cross product of the second and third terms is $2\beta_g\langle(\tilde x^2/v_g - 1)\tilde x\epsilon\rangle_g/v_g$, and its part $-2\beta_g\langle\tilde x\epsilon\rangle_g/v_g$ is zero.

**What a constant predictor removes.** Here $A_g = \langle \tilde x^2 \rangle_g / v_g^2 = 1/v_g$ and

$$
C_g = \frac{\langle \tilde x^2 y \rangle_g}{v_g^2} = \frac{\mu_g v_g + \beta_g\kappa_{3,g} + \langle \tilde x^2\epsilon \rangle_g}{v_g^2},
$$

so that

$$
D_g = \frac{C_g^2}{A_g} = \frac{1}{v_g}\Big(\mu_g + \frac{\beta_g\,\kappa_{3,g} + \langle \tilde x^2 \epsilon \rangle_g}{v_g}\Big)^2 .
$$

The first term of $D_g$ is the level of the outcome. The second is a skewness of the covariate times the slope, and a dependence of the residual's level on $\tilde x^2$, which is curvature of the cluster's regression.

**Section 2.4 as the special case.** Section 2.4 of the brief assumes that $\tilde x$ is symmetric in the cluster and that $\epsilon$ is independent of $\tilde x$ with variance $\sigma_g^2$. Symmetry gives $\kappa_{3,g} = 0$. Independence gives $\langle \tilde x^2 \epsilon^2 \rangle_g = v_g\sigma_g^2$ and $\langle \tilde x^2\epsilon \rangle_g = \langle \tilde x^3\epsilon \rangle_g = 0$, read as population identities (in a finite cluster they hold up to the sampling fluctuation of a product moment). Then

$$
V_g = \frac{\mu_g^2 + \sigma_g^2}{v_g} + \beta_g^2\Big(\frac{\kappa_{4,g}}{v_g^2} - 1\Big), \qquad D_g = \frac{\mu_g^2}{v_g},
$$

which is section 2.4's expression and its statement that the term $\mu_g^2/v_g$ is what a constant predictor removes. The derivation agrees with section 2.4.

In units of the outcome, with $\tilde x$ standardised so that $v_g = 1$ and $\kappa_{4,g} = 3$ (a normal covariate), the share is

$$
L_g = \frac{\mu_g^2}{\mu_g^2 + \sigma_g^2 + 2\beta_g^2} .
$$

The share is large when the outcome's level is large against its within-cluster spread. Log income is such an outcome, and on ACS by state the permuted predictor's within-cluster $R^2$ for the slope, median over the one outcome, is 0.976, against 0.0000042 for the mean, where there is no weight to multiply a level (`results/round5/ppi/E0_anchors/e0_brief_claims.csv`, rows `R2_within_median_over_genes`, read from `results/round4/ppi/Q2_theory/q2_cluster_r2.csv`).

### 1.4 The group difference $\theta_2$

Here $w_{gi} = 1/\pi_{N,g}$ on the units of the first group (neoplastic-dominant, $N$), $-1/\pi_{S,g}$ on the second (stromal-dominant, $S$), and 0 on the rest, with $\pi_{N,g}$ and $\pi_{S,g}$ the groups' fractions of the cluster. Write $\mu_{N,g}$, $\mu_{S,g}$ for the groups' means of $y$ and $\sigma^2_{N,g}$, $\sigma^2_{S,g}$ for their within-group variances (divisor the group's size). The cluster's value is $\langle z \rangle_g = \mu_{N,g} - \mu_{S,g}$.

**The within variance.** $\langle z^2 \rangle_g = \pi_{N,g}\langle y^2 \rangle_{N,g}/\pi_{N,g}^2 + \pi_{S,g}\langle y^2 \rangle_{S,g}/\pi_{S,g}^2$, so

$$
V_g = \frac{\mu_{N,g}^2 + \sigma_{N,g}^2}{\pi_{N,g}} + \frac{\mu_{S,g}^2 + \sigma_{S,g}^2}{\pi_{S,g}} - \big(\mu_{N,g} - \mu_{S,g}\big)^2 .
$$

This needs no assumption.

**What a constant predictor removes.** $A_g = 1/\pi_{N,g} + 1/\pi_{S,g}$ and $C_g = \langle w^2 y \rangle_g = \mu_{N,g}/\pi_{N,g} + \mu_{S,g}/\pi_{S,g}$, so

$$
D_g = \frac{\big(\mu_{N,g}/\pi_{N,g} + \mu_{S,g}/\pi_{S,g}\big)^2}{1/\pi_{N,g} + 1/\pi_{S,g}} = \frac{\big(\pi_{S,g}\,\mu_{N,g} + \pi_{N,g}\,\mu_{S,g}\big)^2}{\pi_{N,g}\,\pi_{S,g}\,(\pi_{N,g} + \pi_{S,g})},
$$

where the second form multiplies the numerator and the denominator by $\pi_{N,g}^2\pi_{S,g}^2$ and skips that algebra. $\pi_{S,g}\mu_{N,g} + \pi_{N,g}\mu_{S,g}$ is $(\pi_{N,g} + \pi_{S,g})$ times a weighted level of the outcome over the two groups, with each group weighted by the other's fraction. So $D_g$ is again a squared level of the outcome divided by a measure of the weight's spread, the analogue of $\mu_g^2/v_g$.

**The special case.** If the two groups have a common mean $\mu_g$ and a common variance $\sigma_g^2$, then $\langle z \rangle_g = 0$,

$$
V_g = (\mu_g^2 + \sigma_g^2)\Big(\frac{1}{\pi_{N,g}} + \frac{1}{\pi_{S,g}}\Big), \qquad D_g = \mu_g^2\Big(\frac{1}{\pi_{N,g}} + \frac{1}{\pi_{S,g}}\Big), \qquad L_g = \frac{\mu_g^2}{\mu_g^2 + \sigma_g^2} .
$$

When the groups' means differ, $D_g$ stays a level term and $V_g$ gains the difference, so the share falls but stays of the order of $\mu_g^2/(\mu_g^2 + \sigma_g^2)$ when the difference is small against the level.

### 1.5 Consequences, and what E2 checks

1. Any predictor whose cluster mean is not zero carries the term $C_g$ through $f = \hat y\,w$, so in regime B it buys at least the share that a constant at its level buys, less whatever the clip and the pooling cost. The permuted predictor has the task-wide level and its within-cluster correlation with $y$ is zero in expectation, so its share should be close to the constant predictor's. The donor-constant predictor carries each cluster's own level, so its share is at least the constant's in the pooled sense when the clusters' levels differ.
2. A comparison that isolates what an encoder knows about units within a cluster is the encoder's width over the constant or donor-constant predictor's width, not over the round-4 classical width. E2 part 3 computes both.
3. The level share is a property of the outcome, the weights and the design weights $\omega_g$. It does not involve the predictor at all. E2 computes $L$ from the full data for every task, estimand and gene, and reports $1 - L$ beside the constant predictor's variance ratio (E2.4 in simulation, and the decomposition on the real tasks).
4. With whole clusters labelled, donor-weighted, the cluster contributions are $\langle z \rangle_g$ and $\langle f \rangle_g = \langle \hat y w \rangle_g$. A constant predictor has $\langle f \rangle_g = c\langle w \rangle_g = 0$, so nothing here touches regime A at $m$ = all, which agrees with the brief.
5. In the E2 simulation at outcome level $\mu = 0$ the cluster levels are the cluster effects alone, so $C_g$ is not zero and neither is $L$. But the constant predictor's $c$ is the task-wide mean prediction, which is close to zero, and the coefficient is clipped to $[0, 1]$, so $\lambda c$ cannot approach $C_g/A_g$ and the share actually removed is close to zero. This is why E2's acceptance check 3 expects a variance ratio of 1.00 at $\mu = 0$. E2.4 is scored at $\mu > 0$ against $1 - L$ with the clip applied as in section 1.2, and at $\mu = 0$ against the clipped share. Plan section 5 item 2 records this reading.

## 2. The cross-fitting term and the two-level estimator

### 2.0 The cross-fitting term of the design-target interval

This section answers section 5, E3a, of `docs/decisions/round5_ppi_E2_decisions.md`. It concerns the round-4 final design estimator with every unit of a labelled cluster labelled, donor-weighted, rule `c_crossfit_design`, as `round5_ppi_estimator.design_whole_clusters` computes it.

**Setting.** There are $G$ clusters with values $(z_g, f_g)$, the cluster means of $z$ and $f$. The target is $\theta = \bar Z$, the mean of $z_g$ over the $G$ clusters, and $\bar F$ is the mean of $f_g$, which is known. A simple random sample $L$ of $n$ clusters is drawn and split at random into halves $A$ and $B$ of sizes $n_A = \lfloor n/2 \rfloor$ and $n_B = n - n_A$, so $A$ and $B$ are disjoint simple random samples. $\lambda_A$ is a function of the values in $A$ only (the clipped least-squares slope of $z$ on $f$ with intercept, or 0 when $n < 6$), and likewise $\lambda_B$. Clusters in $B$ carry $\lambda_A$ and clusters in $A$ carry $\lambda_B$, so the coefficient of cluster $g$ is $\lambda_{(g)}$ and the coefficient on $\bar F$ is their mean over $L$,

$$
c' = \frac{n_B\,\lambda_A + n_A\,\lambda_B}{n}.
$$

Write $\delta = \lambda_B - \lambda_A$, $\Delta = \bar f_A - \bar f_B$ and $\kappa = n_A n_B / n^2$, which is $1/4$ when $n$ is even.

**An exact identity.** The estimator $\hat\theta = c'\bar F + \frac{1}{n}\sum_{g \in L}(z_g - \lambda_{(g)} f_g)$ equals

$$
\hat\theta = \underbrace{\bar z_L - c'(\bar f_L - \bar F)}_{T_1} \; - \; \underbrace{\kappa\,\delta\,\Delta}_{T_2}.
$$

To see it, note that $\frac{1}{n}\sum_L \lambda_{(g)} f_g = \frac{1}{n}(n_A \lambda_B \bar f_A + n_B \lambda_A \bar f_B)$, and that $n_A \bar f_A(\lambda_B - c') + n_B \bar f_B(\lambda_A - c') = n_A n_B\,\delta\,\Delta / n$, because $\lambda_B - c' = n_B\delta/n$ and $\lambda_A - c' = -n_A\delta/n$. For even $n$, with $c = (\lambda_A + \lambda_B)/2$ and $d = \delta/2$, this is the memo's form $\bar z_L - c(\bar f_L - \bar F) - \tfrac{d}{2}(\bar f_A - \bar f_B)$. The identity holds draw by draw and needs no approximation.

**Which part the finite-population factor governs.** $T_1$ is a labelled-sample mean minus a coefficient times $\bar f_L - \bar F$. Both $\bar z_L - \bar Z$ and $\bar f_L - \bar F$ have variances proportional to $1 - n/G$, and both are zero when $n = G$. $T_2$ is a difference between the two halves of the sample. For disjoint simple random samples of sizes $n_A$ and $n_B$,

$$
\text{Var}(\bar f_A - \bar f_B) = \Big(\frac{1}{n_A} + \frac{1}{n_B}\Big) S_f^2 = \frac{n}{n_A n_B}\,S_f^2,
$$

with $S_f^2$ the population variance of $f_g$ (divisor $G - 1$). The two covariance terms of $-S_f^2/G$ cancel the two finite-population terms, so there is no factor $1 - n/G$. The sharpest form is at $n = G$. Then $T_1 = \bar Z = \theta$ exactly and $\hat\theta - \theta = -\kappa\delta\Delta$, which is not zero whenever the halves' coefficients differ, while the current variance estimate is exactly zero.

**The variance of $T_2$, and the dependence between coefficients and means.** $\delta$ and $\Delta$ are computed from the same halves, so in general

$$
E[T_2^2] = \kappa^2\,E[\delta^2\Delta^2].
$$

If $\delta$ and $\Delta$ were independent this would be $\kappa^2 E[\delta^2]\,E[\Delta^2] = \kappa\,E[\delta^2]\,S_f^2/n$. Under a normal population the slope fitted on a half depends on the half's deviations from its own means and not on the means themselves, so $\delta$ and $\Delta$ are independent up to finite-population terms, and $E[T_2] = 0$. Under a skewed population a large $f_g$ raises its half's mean and also has high leverage on its half's slope, so $\delta$ and $\Delta$ are dependent, $E[T_2] = \kappa E[\delta\Delta]$ can differ from zero, and the product form is an approximation. Clipping keeps $|\delta| \le 1$, so $T_2$ is bounded in either case. The cross-moment $E[T_1 T_2]$ vanishes under the normal law by the same argument (the halves' slopes are independent of the halves' means and of the residual means), and is again an approximation under skewness. The skewed grids of E3a measure how much the dependence matters.

**What the current estimate contains.** The current estimate is $(1 - n/G)\,s_e^2/n$ with $e_g = z_g - \lambda_{(g)} f_g + (\lambda_{(g)} - c')\bar F$. Take even $n = 2h$, the unclipped case and a normal population, with $z_g = \alpha + \lambda^\circ f_g + u_g$, $u_g$ of variance $\sigma^2$ independent of $f_g$. Then $\lambda_A = b_A$, the half's own least-squares slope, with intercept $a_A$ and residuals $\varepsilon_g$ that sum to zero and are orthogonal to $f$ within the half. For $g \in A$, $e_g = a_A + \varepsilon_g - \delta f_g + \tfrac{\delta}{2}\bar F$, and for $g \in B$, $e_g = a_B + \varepsilon_g + \delta f_g - \tfrac{\delta}{2}\bar F$. By the orthogonality, the total sum of squares of $e$ over $L$ splits into three parts.

1. The within-half residual sums of squares, $\text{RSS}_A + \text{RSS}_B$, with expectation $(n - 4)\sigma^2$.
2. The terms $\delta^2(SS_A + SS_B)$, with $SS_h$ the half's sum of squares of $f$. Since $(b_A - \lambda^\circ)^2 SS_A$ has expectation $\sigma^2$ and $(b_B - \lambda^\circ)^2 SS_A$ has expectation $\sigma^2 (h-1)/(h-3)$, this part has expectation $4\sigma^2 (h - 2)/(h - 3) = 4\sigma^2 (n - 4)/(n - 6)$.
3. The between-half term $\tfrac{n}{4}(\bar e_A - \bar e_B)^2$. Its leading part is $\bar u_A - \bar u_B$, whose variance is $4\sigma^2/n$ with no finite-population factor, so its expectation is about $\sigma^2$.

So

$$
E[s_e^2] \approx \frac{\sigma^2}{n - 1}\Big[(n - 3) + \frac{4(n - 4)}{n - 6}\Big].
$$

The true variance follows from the identity. $T_1$ contributes $(1 - n/G)\,(\sigma^2 + \text{Var}(c') S_f^2)/n$, where the second part is the variance of $(c' - \lambda^\circ)(\bar f_L - \bar F)$, and $T_2$ contributes $\kappa E[\delta^2] S_f^2 / n$. With independent halves $\text{Var}(c') = E[\delta^2]/4$, and under the normal law $E[\delta^2] S_f^2 = 2\sigma^2/(h - 3) = 4\sigma^2/(n - 6)$. With $\kappa = 1/4$,

$$
\text{Var}(\hat\theta) \approx \frac{\sigma^2}{n}\Big[\Big(1 - \frac{n}{G}\Big)\Big(1 + \frac{1}{n - 6}\Big) + \frac{1}{n - 6}\Big].
$$

The true variance minus the expected current estimate simplifies to

$$
\frac{\sigma^2}{n}\Big[\Big(1 - \frac{n}{G}\Big)\frac{3 - n}{(n - 1)(n - 6)} + \frac{1}{n - 6}\Big].
$$

At $n/G \to 0$ this is $\frac{\sigma^2}{n}\cdot\frac{2}{(n-1)(n-6)}$, a shortfall of $2/((n-1)(n-5))$ of the true variance, about 3% at $n = 12$, because the extra $\delta^2$ in $s_e^2$ and the overfitted residuals nearly cancel. At $n = G$ it is $\frac{\sigma^2}{n(n - 6)}$, all of $T_2$. In between, the shortfall grows linearly in $n/G$. At $G = 15$ and $n = 12$ the formulas give a ratio of expected estimate to true variance of 0.65, which is close to the memo's worst cell, 0.69 at $\lambda^\star = 0.6$ (`results/round5/ppi/E1_interval/e1_sim_grid.csv`). The moment $E[\delta^2]$ is finite only for $h > 3$, that is $n \ge 8$. At $n = 6$ only the clip bounds it.

So the memo's reading is right in its conclusion and needs one correction in its reasoning. The current estimate does not carry $d^2 s_f^2$ inside $s_e^2$. It carries about $\delta^2 s_f^2 = 4 d^2 s_f^2$, which together with the overfitted residual variance makes the estimate nearly right when $n/G$ is small. The factor $1 - n/G$ then removes a fraction $n/G$ of the whole $T_2$ term from what would otherwise be about right, which is what is missed. The derivation closes under the normal law, without clipping, to the order shown.

**The corrected estimate.** The candidate of the memo restores what the factor removes,

$$
\widehat{\text{Var}}_{\text{xf}} = \Big(1 - \frac{n}{G}\Big)\frac{s_e^2}{n} + \frac{n}{G}\cdot\frac{\overline{(\lambda_{(g)} - c')^2}_L\; s_f^2}{n},
$$

with $s_f^2$ the labelled clusters' sample variance of $f_g$ and $\overline{(\lambda_{(g)} - c')^2}_L$ the mean over $L$ of the squared deviation of each cluster's coefficient from $c'$. That mean equals $\kappa\,\delta^2$ for any split, $\delta^2/4 = d^2$ for even $n$, so for even $n$ this is the memo's formula exactly. The form with the mean over $L$ also covers odd $n$, where the memo's $d^2$ would be off by the factor $4\kappa$. Its expectation under the normal law adds $(n/G)\,\sigma^2/(n(n-6))$ to the current estimate, which removes the $1/(n - 6)$ term of the shortfall above and leaves $(1 - n/G)\,\frac{\sigma^2}{n}\cdot\frac{2}{(n-1)(n-6)}$. At $G = 15$ and $n = 12$ the expected ratio becomes 0.985. It needs no new quantity, since the coefficients and $f_g$ are already at hand.

**Properties that the acceptance checks test.** When both halves get the same coefficient, every $\lambda_{(g)} = c'$, the added term is zero and the two intervals are identical. That includes both halves clipping at the same bound, $n < 6$ (where both coefficients are 0), rule `none` and any fixed coefficient. At $n = G$ the corrected estimate is $\kappa\delta^2 s_f^2/n$ against the current zero. The degrees of freedom stay $n - 1$.

**What is approximate, and what E3a measures.** The derivation treats the halves' coefficients as independent of the halves' means, ignores clipping in the size of $s_{\text{res}}^2$, and uses the normal-law moment of the half slope. Clipping shrinks $\delta$ and so shrinks both the missed term and the correction. Under skewed contributions the dependence between $\delta$ and $\Delta$ makes $E[T_2^2]$ differ from the plug-in. The E3a reruns of the E1 normal and skewed grids on the same seeds, and the masking reruns on the six tasks, measure the corrected interval where these approximations do not hold.

### 2.1 The two-level estimator, design-unbiasedness and the variance

This and the next four sections answer "What the theory document derives" under E3 of the brief, with the change of section 5, E3 item 1, of the E2 decision memo. Notation is that of section 1.1. Cluster $g$ has $M_g$ units with label-free weights $w_{gi}$, outcomes $y_{gi}$ and predictions $\hat y_{gi}$, and $z_{gi} = w_{gi} y_{gi}$, $f_{gi} = w_{gi}\hat y_{gi}$. For the donor-weighted $\theta_3$ and $\theta_2$ the weights sum to zero within every cluster, $\sum_i w_{gi} = 0$. For $\theta_2$ the cluster contribution is $\bar z_g = \bar Y_{N,g} - \bar Y_{S,g}$, the difference of the neoplastic-dominant and stromal-dominant group means, because $w = 1/\pi_N$ on the first group, $-1/\pi_S$ on the second and 0 elsewhere, with $\pi_h = M_{h,g}/M_g$.

**Form C for $\theta_3$, unbiasedness.** Under simple random sampling of $m_g$ of the $M_g$ units, the sample covariance $s_{ab}$ with divisor $m_g - 1$ is unbiased for the cluster covariance $S_{ab}$ with divisor $M_g - 1$. The shortest proof writes $s_{ab} = \frac{1}{2m(m-1)}\sum_{i \ne j}(a_i - a_j)(b_i - b_j)$, a mean over the sampled pairs, and the sampled pairs are a simple random sample of the cluster's pairs. Because $\sum_i w_{gi} = 0$, $\bar z_g = \frac{1}{M_g}\sum_i w_{gi} y_{gi} = \frac{M_g - 1}{M_g} S_{wy,g}$. Covariance is bilinear, so $S_{wy} = \lambda S_{w\hat y} + S_{w,\,y - \lambda\hat y}$ for any $\lambda$. $S_{w\hat y,g}$ is computed from all units. So for any $\lambda^w_g$ that does not depend on cluster $g$'s labels, $E[\hat z_g] = \frac{M_g - 1}{M_g}(\lambda^w_g S_{w\hat y,g} + S_{w,\,y-\lambda^w_g\hat y,g}) = \bar z_g$. The cross-fitting of section 2.2 gives every labelled cluster a coefficient from the other half of the clusters, so this holds.

**Form C for $\theta_3$, the variance.** Only $s_{w,r,g}$ with $r = y - \lambda^w_g \hat y$ is random. Write $s_{wr} = \frac{1}{m-1}\big[\sum_L (w_i - \bar W)(r_i - \bar R) - m(\bar w_L - \bar W)(\bar r_L - \bar R)\big]$, where $\bar W = 0$ and $\bar R$ are the cluster means. The second term is of order $1/m$ smaller than the first, so to first order $s_{wr}$ is $\frac{m}{m-1}$ times the sample mean of $u_i = (w_i - \bar W)(r_i - \bar R)$, and

$$
\text{Var}(\hat z_g) \approx \Big(\frac{M_g - 1}{M_g}\Big)^2\Big(\frac{m_g}{m_g - 1}\Big)^2\Big(1 - \frac{m_g}{M_g}\Big)\frac{S^2_{u,g}}{m_g}.
$$

$\bar W$ is known, so $S^2_{u,g}$ is estimated by the sample variance of $\hat u_i = (w_i - \bar W)(r_i - \bar r_L)$ over the labelled units, which gives $\hat V_g$ with the same factors. Centring $w$ at its sample mean instead, or dropping the factor $(m/(m-1))^2$, gives estimates that are too small at small $m$. In a synthetic check with 3,000 draws (`code/scripts/round5_ppi_e3_tests.py`, test 4) the version above has a ratio of mean estimated to empirical variance near 1 at $m = 12$, where the sample-centred version without the factor had about 0.76. The estimate needs $m_g \ge 2$, and an interval needs $m_g \ge 3$, since each cluster's covariance spends two degrees of freedom on its two means.

**Form C for $\theta_2$ under the stratified draw.** Section 5, E3 item 1 of the memo draws $m_{N,g}$ units from the neoplastic-dominant group and $m_{S,g}$ from the stromal-dominant group of each cluster, each a simple random sample within its group, and labels nothing outside the two groups. The estimate is

$$
\hat z_g = (\bar r_{N,L} - \bar r_{S,L}) + \lambda^w_g(\bar{\hat y}_N - \bar{\hat y}_S), \qquad r = y - \lambda^w_g \hat y,
$$

with the second difference over all units of each group. Each group's labelled mean is unbiased for the group's mean of $r$, so $E[\hat z_g] = \bar R_N - \bar R_S + \lambda^w_g(\bar{\hat Y}_N - \bar{\hat Y}_S) = \bar Y_N - \bar Y_S = \bar z_g$. The draws in the two groups are independent, so the variance is exact,

$$
\text{Var}(\hat z_g) = \sum_{h \in \{N, S\}}\Big(1 - \frac{m_{h,g}}{M_{h,g}}\Big)\frac{S^2_{r,h,g}}{m_{h,g}},
$$

estimated with the groups' sample variances. A group with $m_{h,g} = M_{h,g}$ is labelled completely and contributes zero, whatever its size. The smallest $m_g$ is 4, two per group, unless a group is smaller than two and is labelled completely.

**Form P.** $\hat z_g = \gamma_g \bar a_g + \lambda^w_g \bar f_g + \frac{1}{m_g}\sum_{L_g}(z - \gamma_g a - \lambda^w_g f)$. The first two terms are known, and the sample mean of a simple random sample is unbiased for the cluster mean of $z - \gamma a - \lambda f$, so $E[\hat z_g] = \bar z_g$ for coefficients that do not depend on $g$'s labels. The variance is exactly $(1 - m_g/M_g)\,S^2_{r,g}/m_g$, estimated with $s^2_{r,g}$. It needs $m_g \ge 2$. For the donor-weighted estimands $\bar a_g = 0$.

**Between clusters.** $\hat\theta = c_U\bar F + \frac{1}{n_L}\sum_L(\hat z_g - \lambda^c_g \bar f_g)$. Condition on the labelled clusters. The within stage replaces $\bar z_g$ by $\hat z_g$, which is unbiased for it, so $E[\hat\theta \mid L]$ is the whole-cluster estimator of section 2.0 and the round-4 final estimator, with its approximate unbiasedness under cross-fitted $\lambda^c$. The usual two-stage decomposition gives

$$
\text{Var}(\hat\theta) = \Big(1 - \frac{n_L}{G}\Big)\frac{S_e^2}{n_L} + \frac{\bar V}{n_L},
$$

with $S_e^2$ the population variance of the whole-cluster contributions $e_g$ and $\bar V$ the mean of $V_g$ over all $G$ clusters, since the expected within-stage variance given $L$ is $\frac{1}{n_L^2}\sum_L V_g$. The sample variance of $\hat e_g$ over $L$ has expectation $S_e^2 + \bar V$, because each $\hat e_g$ carries its own within-stage error. So $(1 - n_L/G)s^2_{\hat e}/n_L$ already contains $(1 - n_L/G)\bar V/n_L$ and is short by $(n_L/G)\bar V/n_L$, which $\frac{1}{G n_L}\sum_L \hat V_g$ estimates without bias. This is the brief's estimator,

$$
\widehat{\text{Var}} = \Big(1 - \frac{n_L}{G}\Big)\frac{s_e^2}{n_L} + \frac{1}{G\,n_L}\sum_{g \in L}\hat V_g .
$$

When E3a chooses the corrected interval, the cross-fitting term of section 2.0 for $\lambda^c$ is added to it.

**Corners and reference distributions.** With every unit labelled ($m_g = M_g$) every $\hat V_g = 0$ and $\hat z_g = \bar z_g$ in both forms, and the estimator is the round-4 final estimator, with $t_{n_L - 1}$. With $n_L < G$ and $m_g < M_g$ the between term dominates, and the reference is $t_{n_L - 1}$. With $n_L = G$ the first term vanishes, $\hat\theta = \frac{1}{G}\sum_g \hat z_g$ (since $\frac{1}{G}\sum_g \bar f_g = \bar F$), the variance is $\frac{1}{G^2}\sum_g \hat V_g$, and the reference is $t$ with the within-cluster degrees of freedom, $\sum_g (m_g - 1)$ for form P as in round 4, $\sum_g (m_g - 2)$ for form C on $\theta_3$, where each cluster's covariance spends two degrees of freedom on its two means, and $\sum_{g,h}(m_{h,g} - 1)$ over the incompletely labelled groups for form C on $\theta_2$.

### 2.2 The coefficients

The within coefficients are cross-fitted over two halves of the labelled clusters, as the brief says. For form P they are the pooled least-squares coefficients of $z$ on $(a, f)$ with one intercept over the labelled units of the half's clusters, $\gamma$ unclipped and $\lambda^w$ clipped to $[0, 1]$. For form C on $\theta_3$, the first-order variance of $\hat z_g$ is the variance of the mean of $u = (w - \bar W)\big((y - \bar Y) - \lambda(\hat y - \bar{\hat Y})\big)$, so the coefficient that minimises the pooled within-cluster variance is the least-squares slope through the origin of $(w - \bar w_L)(y - \bar y_L)$ on $(w - \bar w_L)(\hat y - \bar{\hat y}_L)$ over the half's labelled units, clipped to $[0, 1]$. For form C on $\theta_2$ it is the pooled least-squares slope of $y$ on $\hat y$ with an intercept for each group of each cluster, clipped. With $\lambda^w = 0$ and $\lambda^c = 0$ both forms are their classical estimators, which for form C are the ordinary within-cluster regression slope and the ordinary difference of the two groups' sample means.

### 2.3 Constant predictors

**Form C.** Let $\hat y_{gi} = c_g$ for every unit of cluster $g$. Then $S_{w\hat y,g} = 0$, because a covariance with a constant is zero, and $s_{w,\,y - \lambda c_g} = s_{wy}$, because subtracting a constant does not change a covariance. So $\hat z_g = \frac{M_g - 1}{M_g}s_{wy,g}$ whatever $\lambda^w_g$ is. For $\theta_2$, $\bar r_{N,L} - \bar r_{S,L} = \bar y_{N,L} - \bar y_{S,L}$ and $\bar{\hat y}_N - \bar{\hat y}_S = 0$. Between clusters, $\bar f_g = c_g \bar w_g = 0$ for every cluster, so $\bar F = 0$ and the between term $\lambda^c_g \bar f_g$ vanishes. The estimate is therefore unchanged exactly, for the constant predictor and for the donor-constant predictor alike. In code the identity holds to rounding, which is E3 acceptance check 3.

**Form P.** Let $\hat y_{gi} = c$ for every unit of the task. Then $f_{gi} = c\,w_{gi} = c\,a_{gi}$, so $f$ is a multiple of $a$, and its partial within-cluster $R^2$ given $a$ is zero. The pooled regression on $(a, f)$ is singular in that case. The code then sets $\lambda^w = 0$ and fits $\gamma$ alone, so the estimator is form P's classical estimator plus the tuning of $\gamma$, whose cost is what E3 acceptance check 4 bounds. A donor-constant predictor is not a multiple of $a$, and with a pooled intercept it can remove differences between the clusters' levels, so it has no band.

### 2.4 Allocation with two coefficients

Take the per-cluster cost $c_d$, the per-unit cost $c_s$, the total $C = n_L(c_d + c_s m)$ with equal $m$, and ignore finite-population factors. The classical estimator of a form has variance $A/n_L + B/(n_L m)$, with $A$ the between-cluster variance of $\bar z_g$ and $B$ the mean within-cluster variance on the form's scale ($S^2_{u}$ times the constant for form C, $S^2_z$ for form P). Minimising the variance at fixed cost gives $m^\star = \sqrt{(B/A)(c_d/c_s)}$. In the two-level estimator the between residual is $\bar z_g - \lambda^c \bar f_g$, with variance $A(1 - R^2_c)$, and the within residual is the form's residual at $\lambda^w$, with variance $B(1 - R^2_w)$, where $R^2_c$ and $R^2_w$ are the cluster-level and within-cluster $R^2$ against the classical estimator of the same form. $\bar f_g$ is known for every cluster, so the between coefficient does not touch the within noise, and the within coefficient does not touch $\bar z_g$. The variance is $A(1 - R^2_c)/n_L + B(1 - R^2_w)/(n_L m)$, and the same minimisation gives

$$
m^\star_{\text{PP}} = \sqrt{\frac{B(1 - R^2_w)}{A(1 - R^2_c)}\cdot\frac{c_d}{c_s}} = m^\star\sqrt{\frac{1 - R^2_w}{1 - R^2_c}},
$$

so $m^\star_{\text{PP}} \le m^\star$ exactly when $R^2_w \ge R^2_c$. Round 4's penalty term came from one coefficient serving both components, which is optimal for neither. With one coefficient per component it does not arise. The tuning cost of section 2.6 is ignored here, as in round 4.

### 2.5 The unit-weighted target

For the spot-weighted estimands the target is $\theta = \frac{1}{N}\sum_g Z_g$ with $Z_g = \sum_i w_{gi} y_{gi}$ and $N = \sum_g M_g$, and the weights no longer sum to zero within a cluster. The cluster-level auxiliaries are $A_g = \sum_i w_{gi}$, which is $M_g$ for the mean, and $F_g = \sum_i f_{gi}$, both known for every cluster with known totals $A_U$ and $F_U$. With $x_g = (A_g, F_g)$ and coefficients $\beta_{(g)} = (\gamma_{(g)}, \lambda_{(g)})$ cross-fitted over the halves of the labelled clusters, least squares of $Z_g$ on $x_g$ without an intercept over the tuning half, $\gamma$ unclipped and $\lambda$ clipped to $[0, 1]$,

$$
\hat\theta = \frac{1}{N}\Big[\bar\beta^\top x_U + \frac{G}{n_L}\sum_{g \in L}\big(Z_g - \beta_{(g)}^\top x_g\big)\Big],
$$

with $\bar\beta$ the mean of $\beta_{(g)}$ over $L$ and $x_U = (A_U, F_U)$. The linearised contribution is $e_g = \frac{G}{N}\big(Z_g - \beta_{(g)}^\top x_g + (\beta_{(g)} - \bar\beta)^\top x_U/G\big)$, the two-coefficient version of round 4's term, and the variance estimate is $(1 - n_L/G)s_e^2/n_L$ with $t_{n_L - 1}$. The cross-fitting term of section 2.0 generalises to $-\kappa\,\delta^\top(\bar x_A - \bar x_B)\,G/N$ with $\delta = \beta_B - \beta_A$, and its correction to $\frac{n_L}{G}\cdot\frac{G^2}{N^2}\cdot\frac{1}{n_L}\overline{(\beta_{(g)} - \bar\beta)^\top S_x(\beta_{(g)} - \bar\beta)}_L$ with $S_x$ the labelled clusters' sample covariance matrix of $x_g$. The textbook comparator for the mean is the ratio estimator, $\lambda = 0$ and $\gamma = \sum_L Z_g/\sum_L M_g$ estimated on all labelled clusters, which gives $\hat\theta = \sum_L Z_g/\sum_L M_g$ with linearised variance $(1 - n_L/G)\frac{G^2}{N^2}s^2_{Z - \hat R M}/n_L$ (Särndal, Swensson and Wretman 1992, section 7.3). Section 2.4's allocation result and section 2.6's tuning cost apply with $p = 2$.

### 2.6 The cost of tuning $p$ coefficients

Take clusters as independent draws, $p$ regressors $x_g$ that are jointly normal with known population mean $\mu$, and a coefficient vector $\hat\beta$ fitted by least squares with an intercept on one half of $n_h$ clusters and applied to the other half's mean of $z_g - \hat\beta^\top(x_g - \mu)$. Let $\sigma^2 = (1 - R^2_p)\sigma^2_z$ be the residual variance at the population coefficient. $\hat\beta$ is independent of the half it is applied to, and $E[x_g] = \mu$, so the applied half's mean has no term from $E[\cdot \mid \hat\beta]$ and its variance is $\frac{1}{n_h}\big(\sigma^2 + E[(\hat\beta - \beta)^\top \Sigma_x (\hat\beta - \beta)]\big)$. For normal regressors $E[(\hat\beta - \beta)(\hat\beta - \beta)^\top] = \sigma^2 E[(X_c^\top X_c)^{-1}] = \sigma^2\Sigma_x^{-1}/(n_h - p - 2)$, the mean of an inverse Wishart with $n_h - 1$ degrees of freedom. So the per-cluster variance is $\sigma^2\big(1 + \frac{p}{n_h - p - 2}\big) = \sigma^2\frac{n_h - 2}{n_h - p - 2}$, and the ratio against the classical estimator is

$$
(1 - R^2_p)\,\frac{n_h - 2}{n_h - p - 2},
$$

as the oversight chat worked it out. The two halves' means are uncorrelated, since each half's error and its own fitted coefficient are uncorrelated given the regressors, and the other half's centred regressor mean has mean zero, so the ratio holds for the cross-fitted estimator over $n_L = 2n_h$ clusters. It is below 1 when $(1 - R^2_p)(n_h - 2) < n_h - p - 2$, that is $n_h > 2 + p/R^2_p$, or $n_L > 4 + 2p/R^2_p$. At $p = 1$ this is round 4's rule. The derivation is in the superpopulation, without the finite-population factor and without the clip. Section 2.0 shows that under the design with a large sampling fraction the cross-fitting adds the term that the factor does not scale, and E1 showed that clipping lowers the cost below this value, so the count is conservative under the design rule.
