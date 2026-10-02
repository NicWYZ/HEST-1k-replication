# Round 4 PPI track, the theory for Q2 and Q3

Written before the Q2 and Q3 experiments run, as the instruction (`docs/decisions/round4_ppi_track.md`,
Q2 and Q3) and the Q1 decision memo (`docs/decisions/round4_ppi_Q1_decisions.md`, sections 2 and 5)
require. Transcribed in `docs/round4_ppi_plan.md`, sections 3 and 13. None of the results below is
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

**The pre-test corollary, rule (d)** (memo section 2). When $R^2_{\text{cluster}}$ is near zero,
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
