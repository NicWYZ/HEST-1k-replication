# Round 5 PPI track, the estimator, defined once

This defines the paper's estimator as it stands after E3, E4b and the decision memo at the E4 gate (`docs/decisions/round5_ppi_E4_decisions.md` section 5, E5 item 1, transcribed in `docs/round5_ppi_plan.md` section 8.5). The round-4 definition `docs/round4_ppi_estimator_definition.md` stays as it is. Derivations are in `docs/round5_ppi_theory.md`. Every number is read from the file named beside it. Paths are relative to the repository root, and `E3a/`, `E3/`, `E4b/` and `E5/` stand for `results/round5/ppi/E3a_crossfit/`, `results/round5/ppi/E3_twolevel/`, `results/round5/ppi/E4b_rejective/` and `results/round5/ppi/E5_joint/`.

## Notation

Cluster $g$ of $G$ has $M_g$ units with label-free weights $w_{gi}$, outcomes $y_{gi}$ and predictions $\hat y_{gi}$, with $z_{gi} = w_{gi}y_{gi}$ and $f_{gi} = w_{gi}\hat y_{gi}$. The estimands are donor-weighted means of cluster contributions, $\theta = \frac{1}{G}\sum_g \bar z_g$. For the slope $\theta_3$ the weights sum to zero within every cluster. For the group difference $\theta_2$, $\bar z_g = \bar Y_{N,g} - \bar Y_{S,g}$, the difference of the neoplastic-dominant and stromal-dominant groups' means. The design target is the fixed set of $G$ clusters. $n_L$ clusters are labelled, and in cluster $g$ of $L$, $m_g$ units are labelled.

## The within-cluster form: form C

$$
\hat z_g = \lambda^w_g\,\bar f_g + \text{(labelled-unit estimate of the cluster's mean of } y - \lambda^w_g \hat y\text{)}
$$

For $\theta_3$ the labelled-unit term is $\frac{M_g - 1}{M_g}\frac{m_g}{m_g - 1}$ times the sample mean of $(w_i - \bar W_g)(r_i - \bar r_L)$ with $r = y - \lambda^w_g\hat y$, which centres $w$ at its known cluster mean (theory section 2.1). For $\theta_2$ the units are drawn by group (next section) and $\hat z_g = (\bar r_{N,L} - \bar r_{S,L}) + \lambda^w_g(\bar{\hat y}_N - \bar{\hat y}_S)$. $\lambda^w_g$ is cross-fitted over two halves of the labelled clusters and clipped to $[0, 1]$ (theory section 2.2). A predictor constant within each cluster changes nothing: under form C the constant arm gives exactly the classical estimate, with width ratio 1.000 and an identity check that holds in 420 of 420 simulation cells with difference 0 (`E3/e3_sim_summary.csv`, sections `const_width_ratio_own_classical` and `C_const_identity`), and on every real task to 2.1e-13 (E4 report section 3, largest on lung, e.g. `E3/LUNG_XENIUM/hoptimus0__accept/e3_accept_identity__LUNG_XENIUM__hoptimus0.csv`). Form P, the pooled-intercept GREG form of round 4, stays in the record as the comparator. For $\theta_3$ the form C classical estimator is 4 to 18% narrower than form P's at $m \ge 10$ on the tissue tasks, and for the stratified $\theta_2$ the two forms give the same width (memo section 2, from `E3/e3_prediction_cells.csv`, prediction E3.3).

## The draw for $\theta_2$

For $\theta_2$ the clusters are the donors where both groups are present, and the labelled clusters are drawn from those. Inside a cluster the draw is stratified by group, $\lfloor m/2 \rfloor$ and $\lceil m/2 \rceil$ with the larger share to the rarer group, each capped at the group's size, the shortfall given to the other group, and units in neither group not labelled. The variance is $\sum_h (1 - m_h/M_h)s_h^2/m_h$ over the two groups. The smallest $m$ is 4.

E4's code drew the labelled donors from all donors and dropped a draw with fewer than two valid labelled donors. The share dropped is 0.015 on Indiana at $n_L = 4$ and 0.190 and 0.025 on lung at $n_L = 4$ and 6, in E4's D0 cells, and 0 in every other $\theta_2$ cell of E4 and of the E3 masking grid (`E5/e5_theta2_dropped_draws.csv`). Those cells were not rerun.

## The between-cluster coefficient and the interval

$$
\hat\theta = c_U\,\bar F + \frac{1}{n_L}\sum_{g \in L}\big(\hat z_g - \lambda^c_g \bar f_g\big)
$$

$\lambda^c$ follows rule `c_crossfit_design`: tuned on each half of the labelled clusters, applied to the other, clipped to $[0, 1]$, and 0 when $n_L < 6$. The design-target interval is `textbook_t|fpc|lin|xf`,

$$
\widehat{\text{Var}} = \Big(1 - \frac{n_L}{G}\Big)\frac{s_e^2}{n_L} + \frac{n_L}{G}\cdot\frac{\overline{(\lambda_g - c')^2}\,s_f^2}{n_L} + \frac{1}{G\,n_L}\sum_{g \in L}\hat V_g
$$

with $t_{n_L - 1}$ when $n_L < G$. The second term is the cross-fitting term of theory section 2.0, which the finite-population factor does not scale. Without it, the ratio of estimated to empirical variance at $G = 15$, $n_L = 12$ and $\lambda^\star = 0.6$ is 0.691 to 0.909 and coverage 0.840 to 0.886, and with it 0.974 to 1.013 and 0.888 to 0.903 (`E3a/e3a_sim_prediction_cells.csv`). The third term is the within-stage variance of the labelled clusters, zero when every unit of a labelled cluster is labelled.

## Regime B

When every cluster is labelled ($n_L = G$) and $m_g < M_g$, the first two terms vanish and the reference is $t$ with $\sum_g (m_g - 2)$ degrees of freedom for $\theta_3$ and $\sum_{g,h}(m_{h,g} - 1)$ for the stratified $\theta_2$ (theory section 2.1, corners). Under form C the design-target coverage in regime B ranges 0.8735 to 0.9215 over every $m$, estimator and estimand in the simulation (`E3/e3_sim_summary.csv`, section `B_coverage_by_m`), and on the real tasks $\theta_2$ covers 0.885 to 0.913 at every $m \ge 6$ on every tissue task and arm (`E3/e3_prediction_scores.csv`, E3.6). Coverage statements about regime B are made only where every cluster gets at least 3 labelled units for $\theta_3$ and 4 for $\theta_2$. The joint design table marks the others (`E5/e5_joint_design.csv`, column `min_units_ok`).

## The design option: rejective selection with `rej_t`

Design D2 draws simple random samples of $n_L$ clusters and accepts the first whose Mahalanobis distance between the labelled and population means of $k$ balance variables, computed from no label, is at or below the $p_a$ quantile of that distance over simple random samples. The point estimate is the classical mean of the labelled clusters, and `rej_t` (theory section 3) is

$$
\widehat{\text{Var}}_{\text{rej}} = \Big(1 - \frac{n_L}{G}\Big)\frac{s^2_{\text{res}} + v_a\,\hat b^\top S_x\,\hat b}{n_L}, \qquad v_a = \frac{P(\chi^2_{k+2} \le q_a)}{P(\chi^2_k \le q_a)},
$$

with $t_{n_L - k - 1}$. Its support condition is $p_a\binom{G}{n_L} \ge 1{,}000$ distinct acceptable samples, and it needs $n_L - k - 1 \ge 2$.

The memo admits D2 with `rej_t` as the design option if E4b's acceptance passes and E4b.1's coverage clause holds. E4b.1's coverage clause holds: under the normal law with balance on $\bar f_g$ at $p_a = 0.01$, `rej_t` covers 0.894 to 0.906 in 60 of 60 cells with $n_L \ge 6$ and support of at least 1,000 (`E4b/e4b_prediction_scores.csv`). Acceptance checks 1 and 2 pass. Acceptance check 3 passes in 204 of 208 cells and fails in 4, all on census by state, $\theta_3$, $n_L = 4$, where the variance ratio under the cluster-level null control is 1.166 and 1.195 at $p_a = 0.1$ and 0.01, 3.2 to 3.8 bootstrap standard errors above 1 (`E4b/e4b_bootstrap.csv`, `E4b/e4b_acceptance.csv`). The four rows are two distinct designs, each repeated for the two arms, because the control and the classical estimate do not depend on the arm. Read strictly, the acceptance did not pass, so D2 with `rej_t` does not enter this definition as the design option. The final report records this as an escalation for the oversight chat to decide, with the evidence that follows.

What balance and `rej_t` do on the real tasks (`E4b/e4b_rej_width_ratios.csv`, `E4b/e4b_report_numbers.csv`). At $n_L = 8$ for $\theta_3$ with own balance at $p_a = 0.01$, `rej_t` is 0.726 of the D0 classical width for `uni_v2` on kidney cancer and 0.551 on census by state, and narrower than the tuned estimator's D0 interval for every encoder on both kidney cancer tasks. Over the 960 D2 cells with support of at least 1,000, `rej_t` covers with median 0.878, within 0.03 of the D0 classical interval in 861. The worst cells are Indiana $\theta_2$ at $n_L = 6$ with two balance variables, where it covers 0.641 to 0.684 against 0.872 for D0 and where up to 0.70 of genes carry a standardised bias above 3. That is $n_L - k - 1 = 3$ residual degrees of freedom, below what section 3.5's normal approximation needs.

So balance reduces the variance of the classical mean, as E4.1 and E4.2 found. `rej_t` captures the reduction in simulation and on most real cells, with the exceptions above.

## Superpopulation target

The paper's real-data claims use the design target only. In E3's simulation the superpopulation-target interval covers below 0.85 in 916 of 8,820 cells, all in regime A with a predictor ($r^2$ 0.5 and 0.8 arms), at $G = 15$ and 24, never at $G = 51$ and never in regime B. Its lowest coverage is 0.7050 for the mean and 0.7665 for $\theta_3$ at $G = 15$ (`E5/e5_superpop_undercoverage.csv`). This holds for form C, form P and the round-4 estimator alike.

## Allocation

Theory section 2.4's result holds for coefficients fixed in advance. With $\lambda^w$ and $\lambda^c$ fixed, the within and between variance components scale by $1 - R^2_w$ and $1 - R^2_c$, and the optimal number of labelled units per cluster becomes $m^\star\sqrt{(1 - R^2_w)/(1 - R^2_c)}$. With cross-fitted coefficients the between gain is zero below $n_L = 6$, where $\lambda^c = 0$, and pays a tuning cost above it, so `E5/e5_allocation.csv` replaces $1 - R^2_c$ by the measured between ratio $\rho_c(n_L)$, the ratio of median variances of `C_ppi` to `C_classical` with every unit labelled. The classical $m^\star$ at $c_d/c_s = 100$ from the components is 77.9 on kidney cancer, 77.2 on the merged task, 125.0 on Indiana, 74.5 on lung, 268.7 on census by state (the form C value E3.5 lacked) and 102.9 on census by area. On the kidney tasks $\rho_c$ is 0.82 to 1.04 at $n_L = 8$ and $m^\star_{\text{PP}}$ stays within 6 of $m^\star$ on kidney cancer. On lung and census, where $\rho_c$ is 0.20 to 0.46 at $n_L = 8$, the formula raises $m^\star_{\text{PP}}$ above $m^\star$ (86.7 against 74.5 on lung with `hoptimus0`), while the fitted curves of `E3/e3_components_fitted.csv` lower it (52.9). The two disagree because the fitted curve $a/n_L + b/(n_L m) + c$ cannot carry a between gain that changes with $n_L$ (memo section 2). Allocation statements in the paper use $m^\star$ for the classical estimator and give both PPI values with this caveat.

## Not chosen, and why

Form P as the paper's form, because form C is narrower for $\theta_3$ and exact for constant predictors. The uncorrected interval `textbook_t|fpc|lin`, because it under-covers where the sampling fraction is large. The simple random within-cluster draw for $\theta_2$, because it under-covers in regime B. D2 with the simple-random-sampling interval, because that interval does not see the variance reduction (memo section 2).
