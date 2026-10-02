# Round 4 PPI track, the estimator, defined once

This is the final estimator of the Q3 decision memo section 2 (`docs/decisions/round4_ppi_Q3_decisions.md`, plan section 14.2). It replaces the version proposed at the Q1 gate. The estimator is the survey-sampling difference estimator, in its PPI++ form the generalised regression estimator (Mozer, arXiv:2603.19160; Särndal, Swensson and Wretman 1992, chapter 8; Breidt and Opsomer 2017), with Liang and Zeger's sandwich clustered by donor. None of it is new. The code is `code/scripts/round4_ppi_estimator.py`.

Numbers are read from the file named beside them. Simulation numbers come from `results/round4/ppi/Q1_estimator/q1_report_numbers.csv` (2,000 replicates per cell), from `results/round4/ppi/Q1_estimator/q1b/q1b_sim_coverage.csv.gz` and from the interval-3 check `results/round4/ppi/Q4_tables/spot_cr2_check/q4_spot_cr2_check.csv`. Real-data numbers come from `results/round4/ppi/Q4a_recompute/q4a_table61.csv`, where each entry is a median over genes of 200 masking draws (`n_draws` in `results/round4/ppi/Q4_tables/q4_main_table.csv`).

## Notation

Donor $g$, spot $i$. Each estimand is the mean of a per-spot scalar linear in the outcome, $z_{gi} = w_{gi}\,y_{gi}$, with label-free weights $w_{gi}$ computed from all spots. For $\theta_3$ the weight is $w = (m - \mu_m)/V_m$, and for a mean it is $w = 1$. The prediction term is $f_{gi} = w_{gi}\,\hat y_{gi}$. There are $n_L$ labelled donors in $L$ and $G_U$ unlabelled donors in $U$. The rectifier is $r_{gi} = z_{gi} - \lambda f_{gi}$.

## Choice of $\lambda$, common to both targets

The labelled donors are split into two halves by a `zlib.crc32` seed. $\lambda$ is tuned on each half and applied to the other half, and $\lambda = 0$ whenever $n_L < 6$. The two targets differ only in the objective minimised on the tuning half. The pre-test rules (d1) and (d2) are dropped (memo section 2). On CCRCC `uni_v2` at $n_L = 16$, design target, (d2) has an empirical variance ratio of 1.17 against 1.03 for (c), with median $\lambda$ of 0 (memo section 2). The draws that pass the pre-test are those with a large half-sample slope, so the pre-test selects a biased $\lambda$. The paper reports $\hat\lambda$ with its standard error and uses the break-even rule of `docs/round4_ppi_theory.md` section 5 to say when a gain is expected.

## Superpopulation target, fresh donors in $U$ (the complement form)

$$
\hat\theta = \lambda\,\bar f_U + \bar r_L
$$

$$
\widehat{\text{Var}}_{\text{CR2}} = \sum_{g \in L} \tilde S_g^2 + \sum_{g \in U} \tilde S_g^2
$$

Here $\tilde S_g$ is the donor's summed influence contribution after the Bell and McCaffrey CR2 leverage adjustment, computed separately within $L$ and within $U$ (`variances`, entry `CR2_bm`). The reference is $t$ with the Bell and McCaffrey Satterthwaite degrees of freedom of the labelled term. There is no Welch-Satterthwaite combination. Spot-weighted, $\bar f_U$ and $\bar r_L$ are spot means. Donor-weighted, they are means of donor means. Every superpopulation row states $G_U$.

$\lambda$ is rule `c_crossfit`. On each half it minimises the donor-clustered variance of $\hat\theta$ including the $U$ term, clipped to $[0, 1]$. The coefficient on $\bar f_U$ is the matching average, so the estimator stays unbiased given the two values. The labelled term is centred within halves.

Behaviour in the simulation (`q1_report_numbers.csv`). Median coverage of the 90% interval is 0.902 at $n_L = 4$ and 0.9005 over $n_L \ge 6$. Against the classical estimator, for $r > 0$ the median width ratio is 1.009 at $n_L = 4$, 0.87 at 6 and 0.85 at 8 and 12. At $r = 0$ it is 1.319 at $n_L = 4$, which is why $\lambda = 0$ below $n_L = 6$. The Welch-Satterthwaite combination narrows the interval (median width 0.961 of the $t$ interval at $G_U = 10$) and under-covers (0.86 at $n_L = 4$), so it is not used.

CR2 against CR1 (`results/round4/ppi/Q4_tables/spot_cr2_check/q4_spot_cr2_summary.csv`, from `q4_spot_cr2_check.csv`, spot-weighted $\theta_3$, no finite-population correction). Over the 30 cells of the classical and `c_crossfit` rules, CR2 equals CR1 when donor sizes are equal, with median coverage 0.8806 for both. With unequal sizes the median coverage is 0.8789 for CR2 against 0.8521 for CR1. The minimum over cells is 0.8408 against 0.8028, and the cell medians of empirical sd over root mean square standard error run from 0.9930 to 1.1892 for CR2 against 1.0028 to 1.2785 for CR1.

## Design-based target, the fixed set of $G$ donors (the textbook form)

Predictions exist on every spot of every donor (addendum 1 section 2), so

$$
\text{donor-weighted}\quad \hat\theta = \frac{\lambda}{G}\sum_{g=1}^{G}\bar f_g + \frac{1}{n_L}\sum_{g \in L}\bar r_g, \qquad \widehat{\text{Var}} = \Big(1 - \frac{n_L}{G}\Big)\frac{s_r^2}{n_L},
$$

$$
\text{spot-weighted}\quad \hat\theta = \frac{\lambda}{N}\sum_{i=1}^{N} f_i + \frac{G}{N\,n_L}\sum_{g \in L} R_g, \qquad \widehat{\text{Var}} = \Big(1 - \frac{n_L}{G}\Big)\frac{G^2}{N^2}\frac{s_R^2}{n_L},
$$

with the $t_{n_L - 1}$ reference. Here $\bar r_g$ is the donor mean of the rectifier and $R_g = Z_g - \lambda F_g$ its donor total.

$\lambda$ is rule `c_crossfit_design`. Write $(a_g, b_g)$ for the textbook-form donor contributions, $(\bar z_g, \bar f_g)$ donor-weighted and $(Z_g, F_g)$ spot-weighted. On tuning half $H$ with $n_H$ donors, $\lambda$ minimises the between-donor sample variance of the rectifier with no unlabelled term,

$$
\hat\lambda_H = \underset{\lambda \in [0,1]}{\arg\min}\ \frac{1}{n_H - 1}\sum_{g \in H}\big(a_g - \lambda b_g - \overline{(a - \lambda b)}_H\big)^2 = \Pi_{[0,1]}\!\left(\frac{\sum_{g \in H}(a_g - \bar a_H)(b_g - \bar b_H)}{\sum_{g \in H}(b_g - \bar b_H)^2}\right),
$$

which is the GREG coefficient of survey sampling. Each half's value is applied to the other half, and the coefficient on the population term is the labelled-weight average of the two. The old rows stay labelled `c_crossfit` so the two rules can be compared.

Behaviour in the simulation (`q1_report_numbers.csv`, with rule c). Median coverage is 0.89 at every $n_L$ from 4 to 20 (0.8915 at $n_L = 4$, 0.894 at 20). The complement form without the finite-population correction over-covers more as $n_L$ grows, 0.977 at $n_L = 12$ of 24, which is the over-coverage B2 saw.

Behaviour on the real tasks (`q4a_table61.csv`, $\theta_3$, donor-weighted, $m$ = all, $n_L = 8$). The design rule lowers the empirical variance ratio against classical most where the prediction carries signal. On LUNG_XENIUM `hoptimus0` the ratio is 0.4282 with median $\lambda$ 0.8163, against 0.6268 and 0.4922 under `c_crossfit`. On CCRCC `uni_v2` it is 0.8440 against 0.8576. On INDIANA_KIDNEY `hoptimus0` it is 0.9752 against 0.9572. Median coverage of the design interval is 0.8700 to 0.8800 on CCRCC, 0.8900 to 0.8950 on INDIANA_KIDNEY and 0.8650 to 0.8750 on LUNG_XENIUM, over all four arms. The median $\lambda$ is often exactly 0.5000, because the two halves frequently clip at opposite ends.

## Not chosen, and why

No bootstrap is used. In the simulation the percentile bootstrap covers 0.760 at $n_L = 4$ and 0.84 at 8 (superpopulation, rule c), BCa is no better, and the bootstrap-$t$ covers 0.852 at $n_L = 4$ (`q1_report_numbers.csv`). The wild cluster bootstrap-$t$ is dropped because Mammen weights cover less than CR1 at every $G_L$ and Rademacher weights come within 0.03 of it (memo section 2). The spot i.i.d. variance is not a candidate.

## Limits of this definition

The coverage minimum is set by the slope estimand on the spot-weighted population. At a between-donor share of 0.1 and 1,000 or more spots per donor the classical interval covers a median 0.8445, while its standard error is right on average, with empirical sd over root mean estimated variance 0.99 (`q1_report_numbers.csv`). The shortfall comes from skewed donor-level contributions, not from the variance formula, and no interval in this comparison removes it. The spot-weighted slope is therefore reported with CR2 and this finding stated beside it. The interval-3 check agrees. With equal sizes and no finite-population correction, the cell means of bias over sd run from $-0.0504$ to $0.0259$ and the cell medians of sd over root mean square standard error from 0.9755 to 1.0293, yet median coverage is 0.8806 (`results/round4/ppi/Q4_tables/spot_cr2_check/q4_spot_cr2_summary.csv`).

## The $r = 0$ predictor

At $r = 0$ the predictor is $\hat y_{gi} = \nu + p_g + d_{gi}$ with $p_g \sim N(0, \sigma_u^2)$ and $d_{gi} \sim N(0, \sigma_e^2)$, independent of everything else, with $\nu = 0$ (addendum 1 section 1 item 1).
