# Round 4 PPI track, the estimator, defined once

Proposed by the execution session at the Q1 gate for the oversight chat's decision. The estimator is
the survey-sampling difference estimator, in its PPI++ form the generalised regression estimator
(Mozer, arXiv:2603.19160; Särndal, Swensson and Wretman 1992, chapter 8; Breidt and Opsomer 2017),
with Liang and Zeger's sandwich clustered by donor. None of it is new. Code is
`code/scripts/round4_ppi_estimator.py`; every number below is read from
`results/round4/ppi/Q1_estimator/q1_report_numbers.csv`, which is computed from the merged
simulation `results/round4/ppi/Q1_estimator/q1_sim_coverage.csv.gz` (2,000 replicates per cell).

## Notation

Donor $g$, spot $i$. Each estimand is the mean of a per-spot scalar linear in the outcome,
$z_{gi} = w_{gi}\,y_{gi}$, with label-free weights $w_{gi}$ computed from all spots (for $\theta_3$,
$w = (m - \mu_m)/V_m$; for a mean, $w = 1$), and $f_{gi} = w_{gi}\,\hat y_{gi}$. Labelled donors $L$
($n_L$ of them), unlabelled donors $U$ ($G_U$). Rectifier $r_{gi} = z_{gi} - \lambda f_{gi}$.

## Superpopulation target, fresh donors in $U$ (the complement form)

$$\hat\theta = \lambda\,\bar f_U + \bar r_L,\qquad
\widehat{\text{Var}} = \frac{n_L}{n_L - 2}\sum_{g \in L}\hat S_g^2 + \frac{G_U}{G_U - 1}\sum_{g \in U}\hat S_g^2,$$

with $\hat S_g$ the donor's summed influence contribution, a $t_{n_L - 2}$ reference, and
$\lambda$ cross-fitted (rule c). The labelled donors are split in two halves by a `zlib.crc32`
seed; $\lambda$ is tuned on each half with $U$ by minimising the donor-clustered variance, clipped
to $[0, 1]$, and applied to the other half; the coefficient on $\bar f_U$ is the matching average
so the estimator stays unbiased given the two values, and the labelled term is centred within
halves, which is why the reference loses two degrees of freedom. Spot-weighted, $\bar f_U$ and
$\bar r_L$ are spot means; donor-weighted, they are means of donor means.

Behaviour in the simulation. Median coverage of the 90% interval is 0.902 at $n_L = 4$ and 0.9005
over $n_L \ge 6$. B1's rule (a) covers 0.87 at $n_L = 4$ and the cluster-tuned rule (b) 0.856,
because they tune and evaluate on the same donors. The price of cross-fitting is width. Against the
classical estimator, for $r > 0$ the median width ratio is 1.009 at $n_L = 4$, 0.87 at 6 and 0.85 at
8 and 12. At $r = 0$ it is 1.319 at $n_L = 4$, because a $\lambda$ tuned on two donors is noisy and
clipping keeps it positive. CR2 is identical to CR1 in this design, because every donor has the same
spot count, so the simulation cannot separate them. The Welch-Satterthwaite combination narrows
the interval (median width 0.961 of the $t$ interval at $G_U = 10$) and under-covers (0.86 at
$n_L = 4$), so it is not used.

## Design-based target, the fixed set of $G$ donors (the textbook form)

Addendum 1 section 2. Predictions exist on every spot of every donor, so

$$\text{donor-weighted}\quad \hat\theta = \frac{\lambda}{G}\sum_{g=1}^{G}\bar f_g + \frac{1}{n_L}\sum_{g \in L}\bar r_g,
\qquad \widehat{\text{Var}} = \Big(1 - \frac{n_L}{G}\Big)\frac{s_r^2}{n_L},$$

$$\text{spot-weighted}\quad \hat\theta = \frac{\lambda}{N}\sum_{i=1}^{N} f_i + \frac{G}{N\,n_L}\sum_{g \in L} R_g,
\qquad \widehat{\text{Var}} = \Big(1 - \frac{n_L}{G}\Big)\frac{G^2}{N^2}\frac{s_R^2}{n_L},$$

with $t_{n_L - 1}$ and cross-fitted $\lambda$. Median coverage is 0.89 at every $n_L$ from 4 to 20
(0.8915 at $n_L = 4$, 0.894 at 20). B1's rule (a) covers 0.844 at $n_L = 4$, rising to 0.896 at 20.
B1's complement form without the finite-population correction over-covers more as $n_L$ grows,
0.977 at $n_L = 12$ of 24, which is the over-coverage B2 saw.

## Not chosen, and why

The percentile bootstrap covers 0.760 at $n_L = 4$ and 0.84 at 8 (superpopulation, rule c). BCa
is no better, and the bootstrap-$t$ covers 0.852 at $n_L = 4$. The spot i.i.d. variance is not a
candidate.

## Limits of this definition

The coverage minimum is set by the slope estimand on the spot-weighted population. At a
between-donor share of 0.1 and 1,000 or more spots per donor the classical interval covers a median
0.8445, while its standard error is right on average (empirical sd over root mean estimated variance
0.99). The shortfall comes from skewed donor-level contributions, not from the variance formula, and
no interval in this comparison removes it. All donors have equal sizes here, which is why CR2 has not
yet been separated from CR1.

## The $r = 0$ predictor

At $r = 0$ the predictor is $\hat y_{gi} = \nu + p_g + d_{gi}$ with $p_g \sim N(0, \sigma_u^2)$ and
$d_{gi} \sim N(0, \sigma_e^2)$, independent of everything else, with $\nu = 0$ (addendum 1 section 1
item 1).
