# Round 4 PPI track, the theory for Q2 and Q3

Written before the Q2 and Q3 experiments run, as the instruction (`docs/round04/i01/ppi/round4_ppi_track.md`,
Q2 and Q3) and the Q1 decision memo (`docs/round04/i02/ppi/round4_ppi_Q1_decisions.md`, sections 2 and 5)
require. Transcribed in `docs/round04/tracks/ppi/round4_ppi_plan.md`, sections 3 and 13. None of the results below is
new. They are the difference estimator's variance in the one-way random-effects model (Särndal,
Swensson and Wretman 1992, chapter 8; Cochran 1977, chapter 10 for two-stage sampling), written in
the notation of prediction-powered inference. Each section ends with what the experiment checks.

## 1. Model and notation

Donor (cluster) $g$, spot (unit) $i$. The outcome and the predictor are

$$
y_{gi} = \mu + u_g + e_{gi}, \qquad \hat y_{gi} = \nu + p_g + d_{gi},
$$

with $u_g$ and $p_g$ the cluster components and $e_{gi}$ and $d_{gi}$ the unit components, mean zero,
independent across clusters, and independent of each other across levels. Write
$\sigma_u^2 = \text{Var}(u_g)$, $\sigma_e^2 = \text{Var}(e_{gi})$, $\sigma_p^2 = \text{Var}(p_g)$,
$\sigma_d^2 = \text{Var}(d_{gi})$, $C_u = \text{Cov}(u_g, p_g)$ and $C_e = \text{Cov}(e_{gi}, d_{gi})$.
The cluster-level and within-cluster coefficients of determination are

$$
R^2_{\text{cluster}} = \frac{C_u^2}{\sigma_u^2 \sigma_p^2}, \qquad R^2_{\text{within}} = \frac{C_e^2}{\sigma_e^2 \sigma_d^2}.
$$

The Q1 generator is the special case $\hat y_{gi} = y_{gi} - a_g - \epsilon_{gi}$ with $a_g$ and
$\epsilon_{gi}$ independent of everything else, for which $p_g = u_g - a_g$, $C_u = \sigma_u^2$,
$\sigma_p^2 = \sigma_u^2 + \sigma_a^2$ and so $R^2_{\text{cluster}} = \sigma_u^2/(\sigma_u^2 + \sigma_a^2)$.

The rectifier is $r_{gi} = y_{gi} - \lambda \hat y_{gi}$. Its cluster and unit components are
$u_g - \lambda p_g$ and $e_{gi} - \lambda d_{gi}$, with variances

$$
\sigma_{u,r}^2(\lambda) = \sigma_u^2 - 2\lambda C_u + \lambda^2 \sigma_p^2, \qquad \sigma_{e,r}^2(\lambda) = \sigma_e^2 - 2\lambda C_e + \lambda^2 \sigma_d^2.
$$

Under the Q1 generator the rectifier's cluster component is $(1 - \lambda) u_g + \lambda a_g$, as the
memo's section 5 states, so $\sigma_{u,r}^2(\lambda) = (1 - \lambda)^2 \sigma_u^2 + \lambda^2 \sigma_a^2$.

## 2. The gain theorem (regime A, the donor-weighted mean)

Regime A labels $m$ spots on each of $n_L$ donors and none on $G_U$ further donors, whose spots are all
predicted. For the donor-weighted mean with $m$ spots per labelled donor and $M$ per unlabelled donor,
the complement-form estimator is $\hat\theta = \lambda \bar{\hat y}_U + \bar r_L$, the mean over
unlabelled donors of their donor means of $\hat y$ plus the mean over labelled donors of their donor
means of $r$. Its two terms use disjoint, independent donors, so

$$
\text{Var}(\hat\theta_{\text{PP}}) = \frac{\sigma_{u,r}^2}{n_L} + \frac{\sigma_{e,r}^2}{n_L m} + V_U, \qquad V_U = \frac{\lambda^2}{G_U}\Big(\sigma_p^2 + \frac{\sigma_d^2}{M}\Big),
$$

and the classical estimator ($\lambda = 0$) has

$$
\text{Var}(\hat\theta_{\text{cl}}) = \frac{\sigma_u^2}{n_L} + \frac{\sigma_e^2}{n_L m}.
$$

**Step 1, the large-$m$ limit.** As $m$ and $M$ grow the unit terms vanish and

$$
\frac{\text{Var}(\hat\theta_{\text{PP}})}{\text{Var}(\hat\theta_{\text{cl}})} \to \frac{\sigma_{u,r}^2}{\sigma_u^2} + \frac{n_L V_U}{\sigma_u^2}, \qquad V_U \to \frac{\lambda^2 \sigma_p^2}{G_U}.
$$

**Step 2, the labelled term at its optimal $\lambda$.** $\sigma_{u,r}^2(\lambda)$ is a quadratic in
$\lambda$ minimised at $\lambda_c = C_u/\sigma_p^2$, where

$$
\sigma_{u,r}^2(\lambda_c) = \sigma_u^2 - \frac{C_u^2}{\sigma_p^2} = \sigma_u^2 \big(1 - R^2_{\text{cluster}}\big).
$$

Under the Q1 generator $\lambda_c = \sigma_u^2/(\sigma_u^2 + \sigma_a^2)$, and the endpoint is the same
$\sigma_u^2(1 - R^2_{\text{cluster}})$, so the form of the predictor's error does not change it.

**Step 3, the full ratio.** At $\lambda_c$ the unlabelled term is
$\lambda_c^2 \sigma_p^2/G_U = R^2_{\text{cluster}} \sigma_u^2/G_U$, and the large-$m$ ratio is

$$
\rho_A(\lambda_c) = 1 - R^2_{\text{cluster}} + \frac{n_L}{G_U} R^2_{\text{cluster}}.
$$

The tuning rules of Q1 minimise the estimated variance of both terms together, so they target the
$\lambda$ that minimises $\sigma_{u,r}^2(\lambda) + (n_L/G_U)\lambda^2\sigma_p^2$, which is
$\lambda_A = \lambda_c\, G_U/(G_U + n_L)$, and there

$$
\rho_A(\lambda_A) = 1 - R^2_{\text{cluster}}\,\frac{G_U}{G_U + n_L}.
$$

Both forms equal $1 - R^2_{\text{cluster}}$ only as $G_U/n_L \to \infty$, which corrects the source's
statement as plan section 8 item 4 flagged and memo section 5 adopts.

**The theorem in words.** With few labelled clusters and many units in each, the PPI estimator's
variance is set by how well the predictor tracks the cluster effects. The share of the classical
variance that remains is one minus the predictor's cluster-level $R^2$ for the labelled term, plus the
cost of estimating the prediction mean on the unlabelled clusters, which is a fraction $n_L/G_U$ of
the explained part. A predictor that is accurate spot by spot but tracks no cluster effect gains
nothing at large $m$.

**The $\lambda$ corollary.** The optimal $\lambda$ is the cluster-level regression coefficient of
$u_g$ on $p_g$, shrunk by $G_U/(G_U + n_L)$ for the unlabelled term. It is not the spot-level
coefficient that PPI++ estimates by default.

**The no-gain corollary.** When $R^2_{\text{cluster}} = 0$ the optimal $\lambda$ is zero and no
$\lambda$ makes the ratio fall below one; any $\lambda \neq 0$ raises the variance by
$\lambda^2 \sigma_p^2 (1/n_L + 1/G_U)$ at large $m$, so it raises the ratio by
$\lambda^2 \sigma_p^2 (1 + n_L/G_U)/\sigma_u^2$.

**The pre-test corollary, rule (d)** (Q1 memo section 2; rule (d) was dropped by the Q3 memo, section 2, in favour of the break-even rule of section 5.2). When $R^2_{\text{cluster}}$ is near zero,
the objective $\sigma_{u,r}^2(\lambda) + (n_L/G_U)\lambda^2\sigma_p^2$ is nearly flat in $\lambda$
whenever $\sigma_p^2$ is small against $\sigma_u^2$, because both $\lambda$ terms scale with
$\sigma_p^2$ and $C_u$. The tuned $\lambda$ is then unidentified: its sampling spread over a few
donors is of order one, and clipping to $[0, 1]$ turns that spread into point masses at both ends.
Its value is nearly harmless for the labelled term, since
$\text{Var}(u_g - \lambda p_g) \approx \sigma_u^2$ when $\sigma_p^2$ is small. The permuted
predictor of Q1 is this case (`results/round4/ppi/Q1_estimator/permuted_mechanism/q1_permuted_lambda_mechanism.csv`).
Rule (d) sets a half-sample's $\lambda$ to zero unless its estimate exceeds $k$ ordinary standard
errors of the half's donor-level slope, $k = 1$ (d1) or $k = 2$ (d2), which reports zero where
$\lambda$ is unidentified and leaves the estimator unchanged where it is identified. The price is a
pre-test bias toward the classical estimator when the cluster-level signal is real but weak, which
Q1b measures as the width ratio against rule (c).

**Implementation of the pre-test, recorded so the reader can check it.** For each half the unclipped
estimate is rule (c)'s ratio before clipping. The standard error is the ordinary least-squares slope
standard error, with intercept and $k_h - 2$ degrees of freedom over the half's $k_h \ge 3$ donors, of
the donor outcome contributions on the donor prediction contributions. These are $(t_g, \hat t_g)$
for the donor-weighted population and the donor totals of $z$ and $\hat z$ centred at the half's spot
means for the spot-weighted population. Where both halves fail, the classical estimator and its
interval are reported for that column (`code/scripts/round4_ppi_estimator.py`, rules `d1_pretest`
and `d2_pretest`).

**What the experiment checks.** The theorem simulation (memo section 5, plan section 13.5) sets
$\sigma_a^2/\sigma_u^2 \in \{0.25, 1, 4\}$, so $R^2_{\text{cluster}} \in \{0.8, 0.5, 0.2\}$, and records
the empirical variance ratio beside $1 - R^2_{\text{cluster}}$ and the full ratio, with
$\rho_A(\lambda_A)$ as the full ratio because rule (c) tunes on both terms. The masking experiment of
Q2 sets the measured $R^2_{\text{cluster}}$ beside the variance ratio at the largest $m$.

**Measuring $R^2_{\text{cluster}}$ with small clusters.** The donor mean of $\hat y$ over $m_g$ spots
has variance $\sigma_p^2 + \sigma_d^2/m_g$, so the naive correlation of donor means is attenuated.
The corrected value replaces the between-donor variances and covariance of donor means by their
one-way ANOVA estimates, the between-donor mean square minus the within-donor mean square over the
mean cluster size, as in the intraclass-correlation estimator.

## 3. The allocation result

At a cost of $c_d$ per labelled donor and $c_s$ per labelled spot, the total cost is
$K = n_L(c_d + c_s m)$. The classical variance is $\sigma_u^2/n_L + \sigma_e^2/(n_L m)$.

**Step 1.** Substituting $n_L = K/(c_d + c_s m)$, the variance is
$K^{-1}(c_d + c_s m)(\sigma_u^2 + \sigma_e^2/m)$, which up to the constant is
$c_d\sigma_u^2 + c_s\sigma_e^2 + c_s m \sigma_u^2 + c_d\sigma_e^2/m$. Setting its derivative in
$m$ to zero gives

$$
m^\star = \sqrt{\frac{c_d}{c_s}\,\frac{\sigma_e^2}{\sigma_u^2}}.
$$

**Step 2.** For the PPI estimator the labelled part has the same form with
$(\sigma_{u,r}^2, \sigma_{e,r}^2)$, and $V_U$ depends on neither $n_L$ nor $m$, so

$$
m^\star_{\text{PP}} = \sqrt{\frac{c_d}{c_s}\,\frac{\sigma_{e,r}^2}{\sigma_{u,r}^2}}.
$$

**Step 3, the comparison.** The source asks to show $m^\star_{\text{PP}} \le m^\star$. That holds if
and only if

$$
\frac{\sigma_{e,r}^2}{\sigma_e^2} \le \frac{\sigma_{u,r}^2}{\sigma_u^2},
$$

that is, when the predictor removes at least as large a share of the unit-level variance as of the
cluster-level variance. With $\lambda$ at the cluster optimum and the Q1 generator, the left side is
$(1 - \lambda_c)^2 + \lambda_c^2 \sigma_\epsilon^2/\sigma_e^2$ and the right side is
$1 - R^2_{\text{cluster}}$, and the inequality can go either way. It does not hold in general, so this
step of the derivation does not close as the source states it. The correct statement is the
condition above. A predictor that captures cluster effects better than within-cluster variation
(the case Q2 measures, comparing $R^2_{\text{cluster}}$ with $R^2_{\text{within}}$) raises the optimal
number of spots per donor. This goes to the Q3 report under escalations, and the experiment reports
$m^\star$ and $m^\star_{\text{PP}}$ side by side for each task.

**Step 4, when the unit term stops mattering.** With $\rho_r = \sigma_{u,r}^2/(\sigma_{u,r}^2 + \sigma_{e,r}^2)$
the rectifier's intraclass correlation, the unit term is at most a fraction $f$ of the cluster term
when $\sigma_{e,r}^2/m \le f \sigma_{u,r}^2$, that is

$$
m \ge \frac{1 - \rho_r}{f \rho_r}.
$$

Q2 reports this $m$ at $f = 0.1$ for each task's fitted $\rho_r$.

## 4. Regime B, every donor partly labelled (Q3)

Regime B labels $m$ spots drawn uniformly without replacement from each of all $G$ donors, with $M_g$
spots on donor $g$, and predicts every spot.

### 4.1 Design-based target

The target is the fixed population's value. For donor $g$ the difference estimator of its mean is
$\hat{\bar y}_g = \lambda \bar{\hat y}_g^{\text{all}} + \bar r_g^{\text{lab}}$, the mean of $\hat y$
over all $M_g$ spots plus the labelled spots' mean rectifier. Under simple random sampling within the
donor its design variance is $(1 - m/M_g)S_{r,g}^2/m$, with $S_{r,g}^2$ the population variance of
$r$ within the donor. The donors are sampled independently, so the donor-weighted estimator
$\hat\theta_B = G^{-1}\sum_g \hat{\bar y}_g$ has

$$
\text{Var}_B^{\text{design}} = \frac{1}{G^2}\sum_{g=1}^{G}\Big(1 - \frac{m}{M_g}\Big)\frac{S_{r,g}^2}{m},
$$

and the spot-weighted estimator $\sum_g (M_g/N)\hat{\bar y}_g$ has

$$
\text{Var}_B^{\text{design, spot}} = \sum_{g=1}^{G}\Big(\frac{M_g}{N}\Big)^2\Big(1 - \frac{m}{M_g}\Big)\frac{S_{r,g}^2}{m}.
$$

**The ratio.** $S_{r,g}^2 = S_{y,g}^2 - 2\lambda S_{y\hat y,g} + \lambda^2 S_{\hat y,g}^2$. The donor
constants $u_g$, $p_g$ and, under the Q1 generator, $a_g$ are constant within a donor, so they drop out
of every within-donor variance and covariance. Pooling over donors with the weights above, the
variance is minimised at the within-cluster coefficient $\lambda_w = S_{y\hat y}/S_{\hat y}^2$ and
the ratio to the classical design variance is

$$
\frac{\text{Var}_B^{\text{design}}(\lambda_w)}{\text{Var}_B^{\text{design}}(0)} = 1 - R^2_{\text{within}},
$$

exactly when the within-donor moments are common to the donors, and as a weighted average otherwise.

**The variance estimator.** The plug-in $\widehat{\text{Var}}_B$ replaces $S_{r,g}^2$ by the
labelled spots' sample variance $s_{r,g}^2$, which is design-unbiased for it, so the plug-in is
design-unbiased for $\text{Var}_B^{\text{design}}$ at fixed $\lambda$. The reference is $t$ on
$G(m - 1)$ degrees of freedom, or the Satterthwaite value when the donors' terms differ.

### 4.2 Superpopulation target

When the donors are a sample from a superpopulation of donors and the target is its mean, the
between-donor variance enters in full, because every donor contributes its own mean once, and

$$
\text{Var}_B^{\text{super}} = \frac{\sigma_u^2}{G} + \text{Var}_B^{\text{design}}
$$

up to the finite-population factors $(1 - m/M_g)$. The estimator is the cluster-robust variance of the
$G$ per-donor estimates with a $t_{G-1}$ reference. The predictor cannot reduce the first term, since
it is the spread of the true donor means, so as $m$ grows the ratio to the classical estimator tends
to one and the gain vanishes.

### 4.3 Regimes A and B at equal unit budget

At $B = n_L m_A = G m_B$ labelled spots, and large $M_g$,

$$
\text{Var}_A \approx \frac{\sigma_u^2(1 - R^2_{\text{cluster}})}{n_L} + \frac{\sigma_{e,r}^2}{B} + V_U, \qquad \text{Var}_B \approx \frac{\sigma_u^2}{G} + \frac{\sigma_{e,r,w}^2}{B},
$$

where $\sigma_{e,r}^2$ is the unit variance at regime A's $\lambda$ and $\sigma_{e,r,w}^2$ at regime B's
within-cluster $\lambda_w$. On the between term regime B wins when

$$
R^2_{\text{cluster}} < 1 - \frac{n_L}{G}.
$$

This is the superpopulation comparison. Against the design-based target regime B has no
between-donor term at all, and its variance is $\text{Var}_B^{\text{design}}$.

**The crossover cost ratio.** With $c_d$ per donor touched and $c_s$ per labelled spot, regime A at
total cost $K$ affords $B_A = (K - n_L c_d)/c_s$ spots and regime B affords $B_B = (K - G c_d)/c_s$.
Regime A is preferred when

$$
\frac{\sigma_u^2(1 - R^2_{\text{cluster}})}{n_L} + \frac{\sigma_{e,r}^2 c_s}{K - n_L c_d} + V_U < \frac{\sigma_u^2}{G} + \frac{\sigma_{e,r,w}^2 c_s}{K - G c_d},
$$

and the crossover $c_d/c_s$ at a given $K$ solves this with equality. Q3 evaluates it with each task's
fitted components and reports it beside the cost-weighted comparison at $c_d/c_s = 100$.

**Training.** The prediction head is trained on other donors (the harness's calibration-fraction-zero
`donor` mode), so the labelled spots enter only the rectifier and the derivations above apply with
the predictor fixed.

## 5. Interval 3 additions (Q3 decision memo section 4, plan section 14.4)

Written before the Q4 tables, and checked in Q4 by predictions Q4.3 and Q4.4 (plan section 4).

### 5.1 The general setting

Every estimand of the track is the population mean of a per-spot scalar that is linear in the
outcome, $z_{gi} = w_{gi} y_{gi}$, with label-free weights $w_{gi}$ computed from all spots, and its
prediction counterpart $f_{gi} = w_{gi} \hat y_{gi}$ (`docs/round04/tracks/ppi/round4_ppi_estimator_definition.md`).
For the mean $w_{gi} = 1$. For the group difference $\theta_2$, $w_{gi} = 1/\pi_{g,\text{neo}}$ on
neoplastic spots and $-1/\pi_{g,\text{str}}$ on stromal spots. For the within-donor slope
$\theta_3$, $w_{gi} = (x_{gi} - \bar x_g)/v_g$ with $x$ the standardised morphology covariate.

**Step 1, donor contributions.** For the donor-weighted population the estimand is
$\theta = G^{-1}\sum_g z_g$ with donor contribution $z_g = M_g^{-1}\sum_i z_{gi}$, and likewise
$f_g$. Write

$$
z_g = \mu_z + u_g + \bar e_g, \qquad f_g = \mu_f + p_g + \bar d_g,
$$

with $u_g$ and $p_g$ the centred between-donor parts and $\bar e_g$, $\bar d_g$ the within-donor
sampling parts, which vanish at $m$ = all. Section 2's $\sigma_u^2$, $\sigma_p^2$, $C_u$ and
$R^2_{\text{cluster}} = C_u^2/(\sigma_u^2\sigma_p^2)$ are read on this scale. This is the `z`
scale of `results/round4/ppi/Q2_theory/q2_cluster_r2.csv`.

**Step 2, invariance to donor offsets.** For $\theta_2$ and $\theta_3$ the weights sum to zero
within each donor, $\sum_i w_{gi} = 0$, because each donor is centred on its own design
constants. A donor-constant shift $\hat y_{gi} \mapsto \hat y_{gi} + c_g$ changes $f_g$ by
$c_g M_g^{-1}\sum_i w_{gi} = 0$. So $p_g$ is a within-donor contrast of the predictions, and no
offset recalibration can change these estimators. For the mean, $\sum_i w_{gi} = M_g$, and the
offset enters $f_g$ in full.

**Step 3, the superpopulation target (complement form).** Section 2's argument goes through with
$(z_g, f_g)$ in place of the donor means of $(y, \hat y)$, since it used only that the labelled
and unlabelled donors are independent draws of the pairs. At $m$ = all, with a fixed $\lambda$,

$$
\frac{\text{Var}(\hat\theta_{\text{PP}})}{\text{Var}(\hat\theta_{\text{cl}})} = \frac{\sigma_u^2 - 2\lambda C_u + \lambda^2\sigma_p^2}{\sigma_u^2} + \frac{n_L}{G_U}\frac{\lambda^2\sigma_p^2}{\sigma_u^2},
$$

which is minimised at $\lambda_A = \lambda^\star G_U/(G_U + n_L)$, $\lambda^\star = C_u/\sigma_p^2$,
where it equals $1 - R^2_{\text{cluster}}\,G_U/(G_U + n_L)$. It reaches
$1 - R^2_{\text{cluster}}$ only as $G_U/n_L \to \infty$.

**Step 4, the design-based target (textbook form).** The population is the fixed set of $G$
donors, the $n_L$ labelled donors are a simple random sample from it, and $\bar F = G^{-1}\sum_g f_g$
is known because every spot is predicted. The estimator
$\hat\theta = \lambda \bar F + n_L^{-1}\sum_{g \in L}(z_g - \lambda f_g)$ is a sample mean of
$r_g = z_g - \lambda f_g$ plus a constant, so for a fixed $\lambda$

$$
\text{Var}(\hat\theta) = \Big(1 - \frac{n_L}{G}\Big)\frac{S_r^2}{n_L}, \qquad S_r^2 = \frac{1}{G - 1}\sum_{g=1}^{G}(r_g - \bar r)^2,
$$

and the classical estimator is the case $\lambda = 0$. The ratio is exactly $S_r^2/S_z^2$, with no
$G_U$ term, and it is minimised at the finite-population regression coefficient
$\lambda = S_{zf}/S_f^2$, where it equals $1 - R^2_{\text{fp}}$ with $R^2_{\text{fp}}$ the
squared finite-population correlation of $z_g$ and $f_g$. The design-target rule
`c_crossfit_design` estimates this coefficient, so its objective has no unlabelled term
(memo section 2).

### 5.2 The cost of tuning $\lambda$

**Setting.** The labelled donors are split into halves $A$ and $B$ of $n_h = n_L/2$ donors. The
coefficient $\hat\lambda_B$ is estimated from half $B$ only and applied to half $A$, and the reverse.
Take the between-donor parts as in 5.1 at $m$ = all, with $p_g$ centred, and write the half-$A$
labelled term as

$$
\bar r_A = \frac{1}{n_h}\sum_{g \in A}\big(u_g - \hat\lambda_B\,p_g\big).
$$

Write $\bar\lambda = E[\hat\lambda]$, $\lambda^\star = C_u/\sigma_p^2$ and
$\text{MSE}(\hat\lambda) = \text{Var}(\hat\lambda) + (\bar\lambda - \lambda^\star)^2$.

**Step 1, conditioning on $\hat\lambda_B$.** Half $A$'s donors are independent of $\hat\lambda_B$.
Given $\hat\lambda_B$ the summands are independent with mean zero and variance
$\sigma_u^2 - 2\hat\lambda_B C_u + \hat\lambda_B^2\sigma_p^2$, so

$$
E\big[\bar r_A \mid \hat\lambda_B\big] = 0, \qquad \text{Var}\big(\bar r_A \mid \hat\lambda_B\big) = \frac{\sigma_u^2 - 2\hat\lambda_B C_u + \hat\lambda_B^2\sigma_p^2}{n_h}.
$$

**Step 2, the law of total variance.** The conditional mean is constant, so

$$
\text{Var}(\bar r_A) = E\big[\text{Var}(\bar r_A \mid \hat\lambda_B)\big] = \frac{\sigma_u^2 - 2\bar\lambda C_u + (\text{Var}(\hat\lambda) + \bar\lambda^2)\sigma_p^2}{n_h} = \frac{\text{Var}(u_g - \bar\lambda\,p_g) + \text{Var}(\hat\lambda)\,\sigma_p^2}{n_h}.
$$

**Step 3, completing the square.** $\text{Var}(u_g - \bar\lambda p_g) = \sigma_u^2(1 - R^2_{\text{cluster}}) + (\bar\lambda - \lambda^\star)^2\sigma_p^2$,
so against the classical half-mean variance $\sigma_u^2/n_h$,

$$
\frac{\text{Var}(\bar r_A)}{\sigma_u^2/n_h} = 1 - R^2_{\text{cluster}} + \text{MSE}(\hat\lambda)\,\frac{\sigma_p^2}{\sigma_u^2}.
$$

**Step 4, what averaging the two halves adds.** The labelled term is $(\bar r_A + \bar r_B)/2$.
Expanding $E[\bar r_A \bar r_B]$ term by term, every term containing $u_g$ or $p_g$ for a donor in
one half and nothing else from that half has mean zero, which leaves

$$
\text{Cov}(\bar r_A, \bar r_B) = \kappa_A\,\kappa_B, \qquad \kappa_A = \frac{1}{n_h}\sum_{g \in A}E\big[\hat\lambda_A\,p_g\big].
$$

$\kappa_A$ is the covariance between half $A$'s coefficient and its own predictions. It is zero when
the joint law of $(u_g, p_g)$ is symmetric under $(u, p) \mapsto (-u, -p)$, since $\hat\lambda$ is
invariant and $p_g$ changes sign, and it is $O(1/n_h)$ in general because one donor moves
$\hat\lambda$ by $O(1/n_h)$. So the covariance is $O(1/n_h^2)$, and

$$
\text{Var}\Big(\frac{\bar r_A + \bar r_B}{2}\Big) = \frac{\text{Var}(\bar r_A)}{2}\big(1 + O(1/n_h)\big),
$$

whose ratio to the classical $\sigma_u^2/n_L$ is the half ratio of step 3. Averaging restores the
sample size but not the tuning cost, because each half is rectified with a coefficient estimated
from only $n_h$ donors. In the complement form the population term $\bar\lambda \bar f_U$ adds the
section 2 term with $E[c_U^2]$ in place of $\lambda^2$, where $c_U$ is the average coefficient;
in the textbook form with $p_g$ centred on the population it adds nothing.

**Corollary, when predictions pay for their tuning.** Since $R^2_{\text{cluster}} = \lambda^{\star 2}\sigma_p^2/\sigma_u^2$,
the ratio of step 3 is below one if and only if

$$
\lambda^{\star 2} > \text{Var}(\hat\lambda) + (\bar\lambda - \lambda^\star)^2,
$$

that is, when $\hat\lambda$'s mean squared error is below the square of what it estimates.

**Corollary, the break-even number of labelled clusters.** For the unclipped least-squares slope of
$u_g$ on $p_g$ over $n_h$ donors with Gaussian $p_g$, $\hat\lambda$ is unbiased and
$\text{Var}(\hat\lambda) = \sigma_u^2(1 - R^2_{\text{cluster}})\,E[1/S_{pp}] = \sigma_u^2(1 - R^2_{\text{cluster}})/\{(n_h - 3)\sigma_p^2\}$,
using $E[1/\chi^2_{n_h - 1}] = 1/(n_h - 3)$. So

$$
\text{Var}(\hat\lambda)\frac{\sigma_p^2}{\sigma_u^2} = \frac{1 - R^2_{\text{cluster}}}{n_h - 3},
$$

and predictions reduce the variance if and only if $R^2_{\text{cluster}} > (1 - R^2_{\text{cluster}})/(n_h - 3)$,
which rearranges to

$$
n_h > 2 + \frac{1}{R^2_{\text{cluster}}}, \qquad n_L > 4 + \frac{2}{R^2_{\text{cluster}}}.
$$

Clipping $\hat\lambda$ to $[0, 1]$ lowers its variance at the price of a bias toward the interval,
so for $\lambda^\star \in [0, 1]$ the count is conservative. A predictor with donor-level
$R^2_{\text{cluster}} = 0.44$ on the contrast scale needs $n_L > 8.5$; at 0.2 it needs $n_L > 14$;
at 0.95 it needs $n_L > 6.1$. This is the answer to "how many labelled clusters before a predictor
pays for its own tuning".

**What the experiment checks.** Prediction Q4.3 compares the theorem check's
estimated-$\lambda$ minus oracle-$\lambda$ ratio with $\text{MSE}(\hat\lambda)\sigma_p^2/\sigma_u^2$,
both measured across replicates (`round4_ppi_q2_theorem_sim.py`, columns `tuning_cost_obs` and
`tuning_cost_pred`; `tuning_cost_pred_with_U` adds the complement form's population term).
Prediction Q4.4 evaluates the corollary on the real tasks from each cell's own $\hat\lambda$ and its
standard error.

### 5.3 The allocation condition

Section 3 step 3 found that $m^\star_{\text{PP}} \le m^\star$ if and only if

$$
\frac{\sigma^2_{e,r}(\lambda)}{\sigma^2_e} \le \frac{\sigma^2_{u,r}(\lambda)}{\sigma^2_u}.
$$

At the cluster optimum $\lambda = \lambda^\star$ the right side is $1 - R^2_{\text{cluster}}$. The
left side is a quadratic in $\lambda$ minimised at the within-cluster coefficient
$\lambda_w = C_e/\sigma_d^2$, where it equals $1 - R^2_{\text{within}}$, so at any $\lambda$ it is at
least $1 - R^2_{\text{within}}$. Two statements follow, and together they are the memo's condition
made exact.

1. If $R^2_{\text{within}} < R^2_{\text{cluster}}$, the left side exceeds $1 - R^2_{\text{within}} > 1 - R^2_{\text{cluster}}$
   and $m^\star_{\text{PP}} > m^\star$. So $R^2_{\text{within}} \ge R^2_{\text{cluster}}$ is necessary.
2. If the two coefficients coincide, $\lambda_w = \lambda^\star$ (as under the Q1 generator when the
   predictor's error is in the same proportion at both levels), the condition is exactly
   $R^2_{\text{within}} \ge R^2_{\text{cluster}}$. When they differ the left side at $\lambda^\star$
   is $1 - R^2_{\text{within}} + (\lambda^\star - \lambda_w)^2\sigma_d^2/\sigma_e^2$, and the
   condition is $R^2_{\text{within}} - (\lambda^\star - \lambda_w)^2\sigma_d^2/\sigma_e^2 \ge R^2_{\text{cluster}}$.

In words, a predictor moves the optimal design toward more clusters with fewer units each when it
ranks units within clusters better than it ranks clusters, by a margin that covers any mismatch
between the two levels' coefficients. In the Q2 data the within-cluster $R^2$ on the `z` scale
exceeds the cluster-level one for every HEST encoder except `uni_v2` on CCRCC and CCRCC merged
(`q2_cluster_r2.csv`), and the fitted $m^\star_{\text{PP}}$ is below $m^\star$ in every case where both
are defined (`q2_report_numbers.csv`).
