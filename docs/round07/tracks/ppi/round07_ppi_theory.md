# Round 7 inference track, the theory

Living document of the round 7 inference track (`docs/round07/i01/ppi/round07_ppi_track.md`, plan `docs/round07/tracks/ppi/round07_ppi_plan.md`). Notation is the estimator definition's (`docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`). Section 1 is written for S1 before any S1 run. Section 2.1, Broska and Howes's interval, is written before S1's runs as well, because S1 applies that interval under D2. Section 2.2, Kluger et al.'s design, follows in S2. Where a step of algebra is skipped, the text says so.

## 1. Weighting under rejective selection (S1)

### 1.1 The design and its inclusion probabilities

There are $G$ clusters with contributions $z_g = \bar z_g$ to $\theta = \frac{1}{G}\sum_g z_g$, prediction contributions $f_g = \bar f_g$ with mean $\bar F$, and $k$ balance variables $x_g \in \mathbb{R}^k$ with mean $\bar X$ and covariance matrix $S_X$ (divisor $G - 1$), all computed from no label. Every unit of a labelled cluster is labelled. Let $\mathcal{S}$ be the set of all $\binom{G}{n}$ samples of $n = n_L$ clusters and, for $s \in \mathcal{S}$,

$$
M_s = (\bar x_s - \bar X)^\top S_X^{-1}(\bar x_s - \bar X).
$$

D2 draws simple random samples one after another and keeps the first with $M_s \le t_a$, where $t_a$ is the fixed threshold of the cell (plan section 1.1 item 2). The accepted sample is therefore uniform on the accepted set $A = \{s \in \mathcal{S} : M_s \le t_a\}$,

$$
P_{D2}(L = s) = \frac{\mathbf{1}\{s \in A\}}{\lvert A\rvert},
$$

because each candidate is uniform on $\mathcal{S}$ and the first candidate that falls in $A$ is uniform on $A$. The support of round 5 is $\lvert A\rvert \approx p_a\binom{G}{n}$. The design has fixed size $n$, and its inclusion probabilities are the shares of accepted samples that contain a cluster or a pair,

$$
\pi_g = \frac{\lvert\{s \in A : g \in s\}\rvert}{\lvert A\rvert}, \qquad \pi_{gh} = \frac{\lvert\{s \in A : g, h \in s\}\rvert}{\lvert A\rvert},
$$

with $\sum_g \pi_g = n$ and $\sum_{h \ne g}\pi_{gh} = (n - 1)\pi_g$. They depend on the $x_g$ only, so they can be computed before any label is bought. With balance on the estimand's own $\bar f_g$ every gene has its own $x_g$ and so its own $\pi_g$ and $\pi_{gh}$. With `pcF2`, `pcE2` and the simulation's $k = 2$ there is one design for every gene.

**Two departures from fixed size.** For $\theta_2$ the candidates are drawn from all donors, as in round 5's E4b, and only the clusters valid for $\theta_2$ enter $\bar x_s$, so the number of valid labelled clusters is random. For $\theta_2$ the design on the valid clusters therefore has random size, $\sum_g \pi_g$ is its expected size, and section 1.4 uses the Horvitz-Thompson variance in place of the Sen-Yates-Grundy form there. For $\theta_3$, and for $\theta_2$ on tasks where every donor is valid, the size is fixed.

**Why D2 makes $\pi_g$ unequal.** A cluster with $x_g$ far from $\bar X$ pulls $\bar x_s$ away from $\bar X$, so fewer of the samples that contain it are accepted. Under D2, $\pi_g$ falls with the Mahalanobis norm of $x_g - \bar X$, which round 5 measured as a Spearman correlation of $-0.57$ to $-0.68$ between inclusion frequency and $\lvert \bar f_g - \bar F\rvert$ at $n_L = 4$ (`docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, section 2).

### 1.2 The bias of the classical mean, and when the weighting removes it

Under any design of fixed size $n$, the classical mean $\bar z_L$ has

$$
E(\bar z_L) - \theta = \frac{1}{n}\sum_g \pi_g z_g - \theta = \frac{1}{n}\sum_g \Big(\pi_g - \frac{n}{G}\Big)(z_g - \theta),
$$

where the second form uses $\sum_g(\pi_g - n/G) = 0$. So the classical mean is biased exactly when the inclusion probabilities covary with the contributions over the $G$ clusters. Under D2, $\pi_g$ is a function of $x_g - \bar X$ that is even to first order (section 1.1), while the linear part of $z_g$ in $x_g$ is odd. The two are uncorrelated in a symmetric population, and correlated when the population of $x_g$ is skewed or when $z_g$ depends on $x_g$ nonlinearly. The residual part $e_g$ of section 3.1 of `docs/round05/tracks/ppi/round5_ppi_theory.md` is uncorrelated with $x_g$ in the least-squares sense but not with an even function of it. With a second balance variable that carries no signal, $\pi_g$ also varies with that variable, and its finite-population covariance with $z_g$ is not zero in any given population, although its mean over populations is. This is the mechanism I expect behind round 5's standardised biases at small $n_L$ with two balance variables. If it is right, the share of genes with standardised bias above 3 should rise with the spread of $\hat\pi_g$ over clusters, which S1 reports beside every cell.

The Horvitz-Thompson estimator

$$
\hat\theta_{\mathrm{HT}} = \frac{1}{G}\sum_{g \in L}\frac{z_g}{\pi_g}
$$

has $E(\hat\theta_{\mathrm{HT}}) = \frac{1}{G}\sum_g \pi_g z_g/\pi_g = \theta$ whenever every $\pi_g > 0$, under any design, fixed size or not. If some $\pi_g = 0$, which can happen under D2 when the support is a handful of samples and a cluster is extreme, its bias is $-\frac{1}{G}\sum_{g : \pi_g = 0} z_g$ and no weighting can remove it. S1 records the smallest $\hat\pi_g$ of every cell for this reason. The Hájek estimator

$$
\hat\theta_{\mathrm{H}} = \frac{\sum_{g \in L} z_g/\pi_g}{\sum_{g \in L} 1/\pi_g} = \frac{\hat\theta_{\mathrm{HT}}}{\hat N/G}, \qquad \hat N = \sum_{g \in L}\frac{1}{\pi_g},
$$

is a ratio of two design-unbiased estimators, of $\theta$ and of $1$. A first-order expansion around $E(\hat N/G) = 1$ gives

$$
\hat\theta_{\mathrm{H}} - \theta \approx \frac{1}{G}\sum_{g \in L}\frac{z_g - \theta}{\pi_g},
$$

so it is unbiased to first order with a bias of order $1/n$, and it is invariant to adding a constant to every $z_g$. Under simple random selection both equal $\bar z_L$.

### 1.3 Estimated inclusion probabilities

The $\pi_g$ and $\pi_{gh}$ are estimated by drawing $R$ accepted samples from D2 with seeds disjoint from every evaluation draw (track document section 2.3). Every accepted candidate of an independent stream is an independent draw from D2 (section 1.1), so all accepted candidates of one stream are used. Then $R\hat\pi_g$ is binomial with mean $R\pi_g$, so

$$
\text{se}(\hat\pi_g) = \sqrt{\frac{\pi_g(1 - \pi_g)}{R}}, \qquad \frac{\text{se}(\hat\pi_g)}{\pi_g} = \sqrt{\frac{1 - \pi_g}{R\pi_g}},
$$

and likewise for $\hat\pi_{gh}$ with the expected count $C_{gh} = R\pi_{gh}$.

**Effect on the point estimate.** $1/\hat\pi_g$ has mean $\frac{1}{\pi_g}\big(1 + \frac{1 - \pi_g}{R\pi_g} + O(R^{-2})\big)$ by a second-order expansion (algebra skipped), so the bias of $\hat\theta_{\mathrm{HT}}$ with plugged-in $\hat\pi_g$, conditional on nothing else, is about $\frac{1}{G}\sum_g z_g (1 - \pi_g)/(R\pi_g)$. At $R = 100{,}000$ and $\pi_g \ge 0.02$, the relative error is below $5 \times 10^{-4}$ per cluster. The same $\hat\pi_g$ serve every evaluation draw of a cell, so their error is a fixed perturbation of the weights, shared by all 2,000 draws, and not noise that averages out. It enters a standardised bias over 2,000 draws as a fixed shift, and S1 reports it by recomputing the bias with $\hat\pi_g$ from two independent halves of the $R$ draws. The Hájek estimator is invariant to a common factor in the $\hat\pi_g$, so the part of the error shared by all clusters cancels.

**Effect on the variance estimate.** The Sen-Yates-Grundy weights are $w_{gh} = \pi_g\pi_h/\pi_{gh} - 1$. Under simple random selection $w_{gh} = (G - n)/(G(n - 1))$, which is 0.095 at $G = 24$, $n = 8$. With $\hat\pi_{gh}$ in the denominator, $\hat w_{gh}$ has relative noise $1/\sqrt{C_{gh}}$ on $\pi_g\pi_h/\pi_{gh}$, which is near 1, and a Jensen bias of about $+\pi_g\pi_h/(\pi_{gh} C_{gh})$. At $C_{gh} = 100$ that bias is about $0.01$, a tenth of the simple-random weight at $G = 24$, $n = 8$. So the variance estimate needs larger counts than the point estimate. With $R = 100{,}000$ the expected count is about $10^4$ on the tissue tasks at $n_L = 8$ and the bias is negligible. On `ACS_CA_PUMA` at $n_L = 4$, $\pi_{gh} \approx 1.7 \times 10^{-4}$ under simple random selection, and a count of 100 needs $R \approx 6 \times 10^5$. S1 sets $R = \max(100{,}000, \lceil 400/\pi^{\mathrm{SRS}}_{gh}\rceil)$, capped at $10^6$, records the smallest count of every cell, and on the cells where counts stay small uses the approximation of section 1.5 beside the simulated values.

### 1.4 The variance estimates

**Fixed size.** For a design of fixed size with every $\pi_{gh} > 0$, the variance of $\hat\theta_{\mathrm{HT}}$ is

$$
\text{Var}(\hat\theta_{\mathrm{HT}}) = \frac{1}{2G^2}\sum_{g \ne h}\big(\pi_g\pi_h - \pi_{gh}\big)\Big(\frac{z_g}{\pi_g} - \frac{z_h}{\pi_h}\Big)^2,
$$

a sum over ordered pairs of all clusters, and the Sen-Yates-Grundy estimator

$$
\widehat{\text{Var}}_{\mathrm{SYG}}(\hat\theta_{\mathrm{HT}}) = \frac{1}{2G^2}\sum_{g \ne h \in L}\frac{\pi_g\pi_h - \pi_{gh}}{\pi_{gh}}\Big(\frac{z_g}{\pi_g} - \frac{z_h}{\pi_h}\Big)^2
$$

is unbiased for it, since each pair enters with probability $\pi_{gh}$. For the Hájek estimator the same form is applied to the residuals $u_g = z_g - \hat\theta_{\mathrm{H}}$ and scaled by $G^2/\hat N^2$, following the linearisation of section 1.2,

$$
\widehat{\text{Var}}_{\mathrm{SYG}}(\hat\theta_{\mathrm{H}}) = \frac{1}{2\hat N^2}\sum_{g \ne h \in L}\frac{\pi_g\pi_h - \pi_{gh}}{\pi_{gh}}\Big(\frac{u_g}{\pi_g} - \frac{u_h}{\pi_h}\Big)^2.
$$

Under simple random selection both reduce to $(1 - n/G)s_z^2/n$, the classical estimate, by direct substitution (algebra skipped).

**Pairs with $\pi_{gh} = 0$.** If a pair of clusters is never jointly accepted, it never appears in a sample and its term is missing from the estimator, while it is present in the variance with the positive coefficient $\pi_g\pi_h$. The estimator then has expectation

$$
E\big(\widehat{\text{Var}}_{\mathrm{SYG}}\big) = \text{Var}(\hat\theta_{\mathrm{HT}}) - \frac{1}{2G^2}\sum_{g \ne h:\,\pi_{gh} = 0}\pi_g\pi_h\Big(\frac{z_g}{\pi_g} - \frac{z_h}{\pi_h}\Big)^2,
$$

so it is biased downward by the missing pairs. No design-based estimator can recover their terms, since nothing in any sample informs them. A $\hat\pi_{gh}$ resting on very few draws behaves between the two cases, with the noise and Jensen bias of section 1.3. S1 records, per cell, the share of pairs with $\hat\pi_{gh} = 0$ and the smallest nonzero count, and a zero outside the census tasks is an escalation under section 10 of the track document.

**A negative estimate.** Under D2 some pairs have $\pi_{gh} > \pi_g\pi_h$, namely clusters with $x_g - \bar X$ and $x_h - \bar X$ on opposite sides that balance each other. Their coefficients are negative, so the estimate can be negative in a sample made mostly of such pairs. A negative estimate is set to zero and counted. The interval is then a point, which counts as not covering unless the estimate equals $\theta$.

**Random size ($\theta_2$ with invalid donors).** The Sen-Yates-Grundy form needs fixed size. With random size the Horvitz-Thompson form,

$$
\widehat{\text{Var}}_{\mathrm{HTV}}(\hat\theta_{\mathrm{HT}}) = \frac{1}{G^2}\Big[\sum_{g \in L}\frac{1 - \pi_g}{\pi_g^2}z_g^2 + \sum_{g \ne h \in L}\frac{\pi_{gh} - \pi_g\pi_h}{\pi_{gh}}\cdot\frac{z_g z_h}{\pi_g\pi_h}\Big],
$$

is unbiased when every $\pi_{gh} > 0$, by the same argument, and S1 uses it with $u_g$ and $G^2/\hat N^2$ for the Hájek estimator. It is not invariant to a shift of $z_g$, which is why the Hájek residual form is the one that matters there.

**The cross-fitted difference form.** With $\lambda$ cross-fitted under rule `c_crossfit_design`, cluster $g$ carries the coefficient $\lambda_{(g)}$ of the other half and the coefficient on $\bar F$ is $c'$, their mean over $L$ (round 5 theory section 2.0). The Horvitz-Thompson difference form is

$$
\hat\theta_{\mathrm{HT},\lambda} = c'\bar F + \frac{1}{G}\sum_{g \in L}\frac{z_g - \lambda_{(g)}f_g}{\pi_g}.
$$

For fixed coefficients it is design-unbiased whenever every $\pi_g > 0$, since its expectation is $c'\bar F + \frac{1}{G}\sum_g(z_g - \lambda_{(g)} f_g)$, which is $\theta$ when every $\lambda_{(g)} = c'$. With cross-fitted coefficients, each cluster's coefficient comes from the other half, and the same identity as round 5's section 2.0 holds with $1/\pi_g$ weights in place of $1/n$, so

$$
\hat\theta_{\mathrm{HT},\lambda} = \hat\theta_{\mathrm{HT}}(z) - c'\big(\hat\theta_{\mathrm{HT}}(f) - \bar F\big) - \frac{1}{G}\sum_{g \in L}\frac{(\lambda_{(g)} - c')f_g}{\pi_g}.
$$

The first two terms are a Horvitz-Thompson difference estimator with coefficient $c'$, whose variance is the Sen-Yates-Grundy form applied to $e_g = z_g - \lambda_{(g)}f_g + (\lambda_{(g)} - c')\bar F$, the same $e_g$ as `design_whole_clusters` with `lin=True`. The third term is the half-difference term $T_2$ of round 5's section 2.0, which reduces to it exactly when $\pi_g = n/G$. Its variance has no finite-population factor (round 5, section 2.0). So S1 uses

$$
\widehat{\text{Var}}(\hat\theta_{\mathrm{HT},\lambda}) = \widehat{\text{Var}}_{\mathrm{SYG}}(e) + \frac{n}{G}\cdot\frac{\overline{(\lambda_{(g)} - c')^2}_L\,s_f^2}{n},
$$

the second term being round 5's cross-fitting term unchanged. That the term carries over unchanged is exact under simple random selection and an approximation under D2, where the halves are not disjoint simple random samples. Two further facts bound what this form can do. With balance on the estimand's own $\bar f_g$, D2 nearly fixes the unweighted mean $\bar f_L$ at $\bar F$, but the weighted $\hat\theta_{\mathrm{HT}}(f)$ is not fixed, so the $c'$ term does not vanish under weighting as it does for the unweighted mean. And below $n_L = 6$ the rule sets every coefficient to zero, so $\hat\theta_{\mathrm{HT},\lambda} = \hat\theta_{\mathrm{HT}}$ there, which S1 checks.

### 1.5 Approximating $\pi_{gh}$ from the $\pi_g$, with and without the balance

**The approximation for a high-entropy design of fixed size.** Let $I_g$ be the inclusion indicators. For a design of maximal entropy given its $\pi_g$, the $I_g$ behave like independent Bernoulli variables with means near $\pi_g$, conditioned on their sum $S = \sum_g I_g$ being $n$. Treat $(I_g, I_h, S)$ under independence as jointly normal, with $\text{Var}(I_g) = a_g = \pi_g(1 - \pi_g)$, $\text{Cov}(I_g, S) = a_g$ and $\text{Var}(S) = d = \sum_g a_g$. Normal conditioning on $S = n$ gives

$$
\text{Cov}(I_g, I_h \mid S = n) \approx 0 - \frac{a_g a_h}{d},
$$

so

$$
\pi_{gh} \approx \pi_g\pi_h - \frac{a_g a_h}{d} = \pi_g\pi_h\Big[1 - \frac{(1 - \pi_g)(1 - \pi_h)}{d}\Big],
$$

which is Hájek's (1964) approximation for rejective sampling. Under simple random selection, with $f = n/G$, it gives $f(n - 1 + f)/G$ against the exact $f(n - 1)/(G - 1)$, so it is close when $G$ is large (algebra skipped).

**What it leaves out under D2.** D2 conditions on the balance as well as the size. In the same normal treatment let $T = \sum_g I_g(x_g - \tilde x)$ with $\tilde x = \sum_g a_g x_g/d$, which given $S$ has covariance $V = \sum_g a_g(x_g - \tilde x)(x_g - \tilde x)^\top$ and $\text{Cov}(I_g, T \mid S) = a_g(x_g - \tilde x)$. D2 keeps samples whose $\bar x_s$ lies in an ellipsoid centred at $\bar X$, which in the canonical form of round 5's theory section 3.3 is a ball, and the ball shrinks the covariance of $T$ to $v_a V$ while leaving its mean (Morgan and Rubin 2012, theorem 3.1). For jointly normal variables, changing the covariance of $T$ from $V$ to $v_a V$ changes $\text{Cov}(I_g, I_h)$ by $-(1 - v_a)\,c_g^\top V^{-1}c_h$, where $c_g = \text{Cov}(I_g, T)$. That step is the normal-conditioning identity and is exact only under normality. Hence

$$
\pi_{gh} \approx \pi_g\pi_h - \frac{a_g a_h}{d} - (1 - v_a)\,a_g a_h\,(x_g - \tilde x)^\top V^{-1}(x_h - \tilde x).
$$

The third term lowers $\pi_{gh}$ for two clusters on the same side of $\bar X$ and raises it for two on opposite sides, which is how D2 makes the labelled mean of $x$ hold still. Two consequences follow. The size-only approximation, used in the Sen-Yates-Grundy form, estimates a variance close to the simple-random one and does not see the variance reduction, as `textbook_t|fpc|lin` does not (round 5 theory, section 3.4). The balance-aware approximation does see it, to the order of the normal approximation. S1 computes both, `apx_size` and `apx_bal`, compares each with the simulated $\hat\pi_{gh}$ where counts are large, and uses them for the variance estimate beside the simulated version. $v_a$ is the nominal value of `round5_ppi_balance.va_nominal`, as in `rej_t`. Neither approximation is guaranteed to give $\pi_{gh} > 0$, so a nonpositive value is replaced by the smallest positive value of the cell and counted.

### 1.6 The reference distribution

Section 3.3 of the round 5 theory shows that under D2, to the order of the normal approximation, the variance of the labelled mean is that of the residual part $e_g$ plus a small $v_a$ part. The same decomposition applies to $\hat\theta_{\mathrm{HT}}$, with $\pi$-weighted means (algebra skipped), so the Sen-Yates-Grundy estimate is, in effect, estimating a residual variance. By analogy with `rej_t`, whose $t_{n - k - 1}$ is a convention and not derived (round 5 theory, section 3.4), the primary reference for every weighted interval under D2 is

$$
t_{\nu}, \qquad \nu = n_L - k - 1,
$$

and the interval is formed only when $\nu \ge 2$, the floor that `rej_t` uses. To answer whether that floor is still needed (question Q1), S1 also forms every weighted interval with $t_{n_L - 1}$ and without the floor, and reports both. Under D0, $k = 0$ and both references are $t_{n_L - 1}$. These degrees of freedom are a convention, as for `rej_t`, and the coverage in S1 is the evidence for or against them.

### 1.7 The intervals S1 computes under D2

For each evaluation draw of a D2 cell.

1. The classical mean with `textbook_t|fpc|lin` and with `rej_t` (round 5).
2. $\hat\theta_{\mathrm{HT}}$ and $\hat\theta_{\mathrm{H}}$ with the Sen-Yates-Grundy estimate (Horvitz-Thompson form for random size), each with three versions of $\pi_{gh}$, simulated (`sim`), `apx_size` and `apx_bal`, and each with the two references of section 1.6. The primary interval is the `sim` version with $t_{n_L - k - 1}$.
3. $\hat\theta_{\mathrm{HT},\lambda}$ under `c_crossfit_design` with the variance of section 1.4, `sim` version, both references.
4. Broska and Howes's interval as if the clusters had been drawn without balance (section 2.1).

The point estimates use the simulated $\hat\pi_g$. Under D0 the reference rows are the classical mean and the tuned estimator with `textbook_t|fpc|lin` and `textbook_t|fpc|lin|xf`, and the weighted estimators with $\pi_g = n/G$ and the exact $\pi_{gh}$, which equal the classical ones and serve as an identity check.

### 1.8 What I expect, written before any S1 run

1. **Bias.** In the cells where round 5's classical mean carried standardised bias above 3 in many genes (the kidney cancer tasks with `pcF2` at $n_L$ of 6 and 8, shares 0.48 to 0.94, and Indiana $\theta_2$ at $n_L = 6$), $\hat\theta_{\mathrm{HT}}$ and $\hat\theta_{\mathrm{H}}$ bring that share down to near the 0.003 expected under no bias, provided every $\hat\pi_g$ is well above zero. If the share stays high where the $\hat\pi_g$ are all well estimated, section 1.2's mechanism is wrong.
2. **Coverage where `rej_t` failed.** In the 17 supported cells where `rej_t` covered below 0.80 (all with two balance variables on tissue tasks), the Hájek interval with `sim` and $t_{n_L - k - 1}$ covers within 0.05 of the D0 classical interval in most of them. Where it does not, I expect the cause to be the three residual degrees of freedom of Indiana $\theta_2$ at $n_L = 6$, which the $t_3$ quantile only partly absorbs, and I expect the $t_{n_L - 1}$ version to cover less there.
3. **Width.** The weights undo part of the balance, because D2 balances the unweighted mean of $x$, not the weighted one. So the Hájek interval is wider than `rej_t`, by more where the spread of $\hat\pi_g$ is larger, that is at small $n_L$, small $p_a$ and with two balance variables. With one balance variable at $n_L = 8$ I expect a ratio of 1.05 to 1.40 over the supported cells.
4. **The approximations.** `apx_size` gives intervals close to the classical `textbook_t|fpc|lin` widths and so loses the balance gain. `apx_bal` is within 10% of the `sim` variance in cells with support of at least 1,000.
5. **The difference form.** With own balance, $\hat\theta_{\mathrm{HT},\lambda}$ is no narrower than $\hat\theta_{\mathrm{H}}$ by more than a few percent at $n_L \ge 8$, since the coefficient multiplies a term that balance has largely removed, and it equals $\hat\theta_{\mathrm{HT}}$ below $n_L = 6$.

### 1.9 What the synthetic test showed, written after S1.2

This subsection was added after the synthetic test of S1.2 and before any real-data run of S1. The test is `results/round7/ppi/S1_weighting/tests/run2/s1_tests.csv` (Slurm job 4824390, snapshot `ba3129e`). $\hat\theta_{\mathrm{HT}}$ is unbiased within Monte Carlo error in every cell, with simulated and with exact probabilities, while the classical mean carries standardised biases of up to 37 in the skewed cells. The Sen-Yates-Grundy estimate matches the empirical variance in every cell drawn under the normal law, and fails in every skewed cell. In the two skewed cells that can be enumerated, 0.72% of the pairs at $G = 24$ and 0.95% to 5.71% at $G = 15$ have exact $\pi_{gh} = 0$. These are pairs of clusters on the same side of $\bar X$ that are never accepted together, and section 1.4 says what follows. The estimator loses their terms and is biased downward, here so far that its mean is negative. With the exact $\pi_{gh}$ the result is the same as with the simulated ones, so it is a property of the design and not of the simulation. Under D2 with a skewed balance variable, therefore, no design-based unbiased variance estimator of $\hat\theta_{\mathrm{HT}}$ exists, and an interval has to rest on an approximation. Of the two in section 1.5, `apx_size` overestimates the variance by factors of 1.3 to 2.6 in these cells and `apx_bal` inherits the same failure, because it too gives near-zero probabilities for those pairs (`results/round7/ppi/S1_weighting/tests/run2/s1_tests_cells.csv`). The pilot on `CCRCC` found such pairs on real data as well, in up to 0.8% of the pairs of a cell.

## 2. The comparators (S2)

### 2.1 Broska and Howes's interval for whole labelled clusters

**Their estimator and interval.** Broska and Howes (arXiv:2610.09601v1, section 2) write PPI++ for the mean as

$$
\hat\theta^{PP}_\lambda = \frac{\lambda}{N}\sum_{i=1}^{N} f(\tilde X_i) + \frac{1}{n}\sum_{i=1}^{n}\big(Y_i - \lambda f(X_i)\big),
$$

their equation (1), with the labelled units as one data set and the unlabelled units as the other. Their cluster-robust interval is $\hat\theta^{PP}_{\hat\lambda} \pm z_{1 - \alpha/2}\,\hat\sigma_{\hat\lambda}/\sqrt n$ (remark 1), with $\hat\sigma^2_\lambda$ of equation (9) built from $\hat\varepsilon_g$ and $\hat Z_g$ of equations (6) and (7) and $\hat\Sigma$, and $\hat\lambda = \hat\Sigma_{12}/\hat\Sigma_{22}$ of equation (12) with $\hat\Sigma$ first computed at $\lambda = 1$ (section 2.4).

**Specialisation.** Their appendix A allows cluster-level weights, and weight $1/m_g$ on each unit makes each cluster count once. With whole clusters labelled, cluster $g$ then acts as one unit with outcome $z_g$ and prediction $f_g$, $\xi_g = \mathbf{1}\{g \in L\}$, and $n = n_L$ and $N = G - n_L$ count clusters. $\hat\theta_f$ becomes $\bar F$. Hence

$$
\hat\theta^{PP}_\lambda = \bar z_L + \lambda\big(\bar f_U - \bar f_L\big), \qquad \hat\varepsilon_g = \xi_g\big(z_g - \hat\theta^{PP}_\lambda\big), \qquad \hat Z_g = \Big(\xi_g - \frac{n}{N}(1 - \xi_g)\Big)\big(f_g - \bar F\big),
$$

with $\bar f_U$ the mean over the unlabelled clusters, and

$$
\hat\sigma^2_\lambda = \frac{G}{n}\Big(\hat\Sigma_{11} - 2\lambda\hat\Sigma_{12} + \lambda^2\hat\Sigma_{22}\Big), \qquad \hat\Sigma = \frac{1}{G}\sum_{g=1}^{G}\begin{pmatrix}\hat\varepsilon_g^2 & \hat\varepsilon_g\hat Z_g \\ \hat Z_g\hat\varepsilon_g & \hat Z_g^2\end{pmatrix}.
$$

Writing out the sums, with $r = n/N$,

$$
\frac{\hat\sigma^2_\lambda}{n} = \frac{1}{n}\Big[\frac{1}{n}\sum_{g \in L}\Big(\big(z_g - \hat\theta^{PP}_\lambda\big) - \lambda\big(f_g - \bar F\big)\Big)^2 + \lambda^2\,r\,\frac{1}{N}\sum_{g \in U}\big(f_g - \bar F\big)^2\Big],
$$

because the labelled clusters contribute $\hat\varepsilon_g^2 - 2\lambda\hat\varepsilon_g\hat Z_g + \lambda^2\hat Z_g^2 = ((z_g - \hat\theta) - \lambda(f_g - \bar F))^2$ and the unlabelled ones contribute $\lambda^2 r^2 (f_g - \bar F)^2$ (algebra skipped). This is their example 1, $\text{Var}(Y - \lambda f) + \lambda^2 r\,\text{Var}(f)$, with the two variances computed as mean squares about $\hat\theta - \lambda\bar F$ over the labelled clusters and about $\bar F$ over the unlabelled ones. The identity is exact, so the first check of track document section 2.3 compares the implementation of equations (6), (7), (9) and (12) with this direct form on simulated i.i.d. data with clusters of size one, to $10^{-10}$.

**Choices this implementation makes.** $\hat\lambda$ comes from $\hat\Sigma$ at $\lambda = 1$, then $\hat\theta^{PP}_{\hat\lambda}$ is formed, and $\hat\sigma^2_{\hat\lambda}$ uses $\hat\Sigma$ recomputed at $\hat\theta^{PP}_{\hat\lambda}$, since equation (6) centres at the estimate whose variance is wanted. With a constant predictor $\hat\Sigma_{22} = 0$, so $\hat\lambda = 0$ is set and counted, and the interval is then $\bar z_L \pm z_{1 - \alpha/2}\sqrt{\frac{1}{n^2}\sum_L(z_g - \bar z_L)^2}$, with no finite-population factor and divisor $n$. $\hat\lambda$ is not clipped, as in the paper. Their implementation at `github.com/Michael-Howes/ppi_py` is not fetched.

**What the interval estimates under the design target.** Take simple random selection of $n$ of $G$ clusters, $f = n/G$, a fixed $\lambda$, and write $S_z^2$, $S_f^2$ and $S_{zf}$ for the population moments over the $G$ clusters. Using $\bar f_U = (G\bar F - n\bar f_L)/N$,

$$
\hat\theta^{PP}_\lambda - \theta = (\bar z_L - \theta) - \frac{\lambda}{1 - f}\big(\bar f_L - \bar F\big),
$$

so its design variance is

$$
\text{Var}_{D0}\big(\hat\theta^{PP}_\lambda\big) = \frac{1 - f}{n}\Big(S_z^2 - \frac{2\lambda}{1 - f}S_{zf} + \frac{\lambda^2}{(1 - f)^2}S_f^2\Big),
$$

minimised at $\lambda = (1 - f)B$ with $B = S_{zf}/S_f^2$, where it equals $\frac{1 - f}{n}S_z^2(1 - R^2)$ with $R^2 = S_{zf}^2/(S_z^2 S_f^2)$, the cluster-level $R^2$. The expectation of $\hat\sigma^2_\lambda/n$ is, to leading order in $1/n$ and $1/N$ (the centring at $\hat\theta$ and the divisors $n$ and $N$ are of lower order and skipped),

$$
\frac{1}{n}\Big(S_z^2 - 2\lambda S_{zf} + \lambda^2 S_f^2\Big) + \frac{\lambda^2 r}{n}S_f^2 = \frac{1}{n}\Big(S_z^2 - 2\lambda S_{zf} + \frac{\lambda^2}{1 - f}S_f^2\Big),
$$

since $1 + r = 1/(1 - f)$. Their $\hat\lambda$ estimates $S_{zf}(1 - f)/S_f^2 = (1 - f)B$, the design optimum. At that $\lambda$ their expectation is $\frac{S_z^2}{n}\big(1 - (1 - f)R^2\big)$, so the ratio of what their interval estimates to the design variance is

$$
\rho_{\mathrm{BH}}(f, R^2) = \frac{1 - (1 - f)R^2}{(1 - f)(1 - R^2)} \;\ge\; \frac{1}{1 - f} .
$$

It is $1/(1 - f)$ at $R^2 = 0$, which is the missing finite-population factor alone, and grows with $R^2$, because their variance treats the unlabelled clusters' predictions as random while the design target holds them fixed. At $f = 0.5$ it is 2 at $R^2 = 0$ and 6 at $R^2 = 0.8$, so a nominal 0.90 interval would have the width of a 0.98 or a 0.9999 interval if the variance were known. At small $n_L$ two effects pull the other way, the normal quantile in place of a $t$ quantile and the divisor $n$ in place of $n - 1$. So the design-target coverage of their interval should fall below nominal at small $n_L$ and small $f$, and rise above it as $f$ grows, by more where $R^2$ is high.

**Two small-sample variants (S2b item 3, written before the run).** The S2 memo asks for two variants with the same $\hat\theta^{PP}_{\hat\lambda}$ and $\hat\lambda$. Split the expanded form above into its two terms,

$$
\frac{\hat\sigma^2_{\hat\lambda}}{n} = T_L + T_U, \qquad T_L = \frac{1}{n^2}\sum_{g \in L}\Big(\big(z_g - \hat\theta^{PP}_{\hat\lambda}\big) - \hat\lambda\big(f_g - \bar F\big)\Big)^2, \qquad T_U = \frac{\hat\lambda^2 r^2}{n^2}\sum_{g \in U}\big(f_g - \bar F\big)^2 .
$$

`bh_t` replaces the divisor $n$ of the labelled mean square by $n - 1$ and the normal quantile by a $t$ quantile,

$$
\widehat{\text{Var}}_{\text{bh\_t}} = \frac{n}{n - 1}\,T_L + T_U, \qquad \hat\theta^{PP}_{\hat\lambda} \pm t_{n - 1,\,1 - \alpha/2}\sqrt{\widehat{\text{Var}}_{\text{bh\_t}}},
$$

and S2b reports beside it the same variance with $t_{n - 2}$, since $\hat\lambda$ is fitted from the same labelled clusters. The unlabelled term is left as it is, because its divisor is $N$, which is not small. `bh_t_fpc` multiplies the whole variance by the finite-population factor,

$$
\widehat{\text{Var}}_{\text{bh\_t\_fpc}} = \Big(1 - \frac{n}{G}\Big)\widehat{\text{Var}}_{\text{bh\_t}}, \qquad \hat\theta^{PP}_{\hat\lambda} \pm t_{n - 1,\,1 - \alpha/2}\sqrt{\widehat{\text{Var}}_{\text{bh\_t\_fpc}}} .
$$

For $\theta_2$ the count $n$ is the number of valid labelled clusters in the draw, so the factor and the degrees of freedom vary from draw to draw, and a draw with $n - 2 < 1$ forms no interval in the $t_{n-2}$ version.

What to expect. To leading order the expectation of $\widehat{\text{Var}}_{\text{bh\_t}}$ is that of $\hat\sigma^2_{\hat\lambda}/n$, so for the design target under D0 it still carries the factor $\rho_{\mathrm{BH}}(f, R^2)$, and the change at small $n$ is only the factor $n/(n - 1)$ on $T_L$ and the wider quantile. At $n = 4$ the two together widen the interval by at most $\frac{t_{3,0.95}}{z_{0.95}}\sqrt{4/3}$, about 1.65, as the memo computes. `bh_t_fpc` removes the factor $1/(1 - f)$ of $\rho_{\mathrm{BH}}$ and leaves

$$
\frac{\text{E}\,\widehat{\text{Var}}_{\text{bh\_t\_fpc}}}{\text{Var}_{D0}\big(\hat\theta^{PP}_\lambda\big)} \approx \frac{1 - (1 - f)R^2}{1 - R^2},
$$

which is 1 at $R^2 = 0$ and grows with $R^2$, so for the design target it should be conservative wherever the cluster-level $R^2$ is not small. For the superpopulation target the finite-population factor does not belong, so `bh_t_fpc` should cover less than `bh_t` there, by more as $f$ grows. S2b reports beside every cell the median over genes of the cluster-level $R^2$, the factor $\rho_{\mathrm{BH}}(n_L/G, R^2)$ at that median, and the measured ratio of the mean variance estimate to the empirical variance of $\hat\theta^{PP}_{\hat\lambda}$ over the draws, which is what $\rho_{\mathrm{BH}}$ predicts for the published interval.

**Under D2.** S1 applies the interval to D2's labelled clusters as if they had been drawn without balance. Its variance estimate is built from the labelled clusters' spread, which balance on the mean of $x$ does not reduce, so it carries the factor above and misses D2's variance reduction as well.

**For the superpopulation target** their interval is the large-$G$ interval they derive, and its shortfall at few clusters is what S2 measures.

**A note on $\rho_{\mathrm{BH}}$ after S2b, added on 15 October 2026 at the S4 memo's request.** S2b item 3 found that $\rho_{\mathrm{BH}}$ overstates the measured ratio of Broska and Howes's variance estimate to the empirical variance, by a factor whose median rises from about 0.5 at $n_L = 4$ to about 0.9 at $n_L = 16$ (S4 report, section 6.1), and that `bh_t_fpc` under-covers where the derivation above says it should stay conservative. A likely reason is that the derivation holds $\lambda$ fixed, while the empirical variance of $\hat\theta^{PP}_{\hat\lambda}$ includes the noise of $\hat\lambda$ fitted on a handful of labelled clusters. That noise raises the denominator of the measured ratio, most at small $n_L$, which is the pattern seen. This explanation is not derived and not checked.

### 2.2 Kluger et al.'s design and estimators for whole labelled clusters

Written before any S2 run. Kluger, Lu, Zrnic, Wang and Bates (arXiv:2501.18577v3, appendix B.1) label whole clusters by independent Bernoulli draws $\xi_k \sim \text{Bernoulli}(\pi_k)$ with known $\pi_k$, so $n_L = \sum_k \xi_k$ is random with mean $\sum_k \pi_k$. With each cluster as one unit (outcome $z_k$, prediction $f_k$) and the mean as the estimand, their estimator function $A(\cdot\,; W)$ is the weighted mean, so

$$
\hat\theta^\bullet = \frac{\sum_k W_k z_k}{\sum_k W_k}, \qquad \hat\gamma^\bullet = \frac{\sum_k W_k f_k}{\sum_k W_k}, \qquad \hat\gamma^\circ = \frac{\sum_k \bar W_k f_k}{\sum_k \bar W_k},
$$

with $W_k = \xi_k/\pi_k$ and $\bar W_k = (1 - \xi_k)/(1 - \pi_k)$ (their section 2.1). The tuned predict-then-debias estimator is $\hat\theta^{\mathrm{PTD}} = \hat\Omega\hat\gamma^\circ + (\hat\theta^\bullet - \hat\Omega\hat\gamma^\bullet)$, their equation (1). $\hat\Omega$ follows their subroutine 1 with $d = 1$,

$$
\hat\Omega = \frac{\widehat{\text{Cov}}^*(\hat\theta^\bullet, \hat\gamma^\bullet)}{\widehat{\text{Var}}^*(\hat\gamma^\bullet) + \widehat{\text{Var}}^*(\hat\gamma^\circ)},
$$

with the moments taken over the bootstrap draws. The interval is the percentile interval of $\hat\theta^{\mathrm{PTD},(b)}$ over $B = 2{,}000$ draws of their algorithm 5, which resamples all $G$ clusters with replacement, labelled and unlabelled, carrying each cluster's weights. A draw that labels fewer than two clusters, or none of whose resamples can form $\hat\theta^\bullet$, gets no interval and is counted. A bootstrap resample with no labelled cluster has no $\hat\theta^{\bullet,(b)}$ and is dropped from the quantiles; the share dropped is recorded.

**The inverse-probability-weighted means beside it.** Under this design $\pi_{gh} = \pi_g\pi_h$, so every Sen-Yates-Grundy coefficient is zero and that form does not apply. The Horvitz-Thompson mean $\hat\theta_{\mathrm{HT}} = \frac{1}{G}\sum_k \xi_k z_k/\pi_k$ has, since the $\xi_k$ are independent with $\text{Var}(\xi_k) = \pi_k(1 - \pi_k)$,

$$
\text{Var}(\hat\theta_{\mathrm{HT}}) = \frac{1}{G^2}\sum_k \frac{1 - \pi_k}{\pi_k}z_k^2, \qquad \widehat{\text{Var}}_{\mathrm{Pois}}(\hat\theta_{\mathrm{HT}}) = \frac{1}{G^2}\sum_{k \in L}\frac{1 - \pi_k}{\pi_k^2}z_k^2,
$$

and the estimator is unbiased because each term enters with probability $\pi_k$. It carries the variability of the random sample size, through the uncentred $z_k^2$, so it is not invariant to a shift of $z$. The Hájek mean, which is $\hat\theta^\bullet$ above, linearises as in section 1.2 to $\frac{1}{G}\sum_k \xi_k(z_k - \theta)/\pi_k$, so

$$
\widehat{\text{Var}}_{\mathrm{Pois}}(\hat\theta_{\mathrm{H}}) = \frac{1}{\hat N^2}\sum_{k \in L}\frac{1 - \pi_k}{\pi_k^2}\big(z_k - \hat\theta_{\mathrm{H}}\big)^2, \qquad \hat N = \sum_{k \in L}\frac{1}{\pi_k}.
$$

With $\pi_k = f = n/G$ for all $k$, $\hat N = n_L/f$ and this is $\frac{1 - f}{n_L}\cdot\frac{1}{n_L}\sum_L(z_k - \bar z_L)^2$, the classical estimate with divisor $n_L$ in place of $n_L - 1$. The reference for both is $t_{n_L - 1}$ with the realised $n_L$, a convention by analogy with the classical interval.

**The two designs of S2.** The uniform design has $\pi_k = n_L/G$. The score design has

$$
\pi_k = \frac{1}{2}\cdot\frac{n_L\,u_k}{\sum_h u_h} + \frac{1}{2}\cdot\frac{n_L}{G}, \qquad u_k = \lvert f_k - \bar F\rvert,
$$

with every $\pi_k$ above 1 set to 1 and the excess spread over the others in proportion to their $\pi_k$, repeated until none exceeds 1. The score is the estimand's own prediction contribution, so each gene has its own design. With a constant predictor every $u_k$ is zero and the score design is the uniform one. For each draw one uniform variable per cluster, shared by all genes, decides $\xi_{kj} = \mathbf{1}\{U_k < \pi_{kj}\}$, so that the genes' designs are coupled the way one physical labelling would be.

**What to expect.** For the design target the Poisson-design interval of the Hájek mean is a design-based interval and should cover near nominal when $n_L$ is not small, while the cluster bootstrap estimates a superpopulation variance and has no finite-population factor, so for the design target it should be conservative as $n_L/G$ grows, by the same mechanism as section 2.1. For the superpopulation target the bootstrap's percentile interval at few labelled clusters is expected to under-cover, as round 4's percentile donor bootstrap did (0.760 at $n_L = 4$ and 0.84 at 8, `docs/round04/tracks/ppi/round4_ppi_estimator_definition.md`), which is prediction S2.4.

### 2.3 The two targets, and how S2 measures the superpopulation target on the real tasks

Written before any S2 run. **Simulation.** The populations of round 5's generator are $G$ independent clusters from a law with mean zero (`round5_ppi_e1_sim.draw_law` standardises both laws), so in every population the design target is the population's mean of $z_g$ and the superpopulation target is zero. Every interval is scored against both.

**Real tasks.** A real task is one fixed set of $G$ clusters, so its superpopulation mean is unknown, and coverage of it cannot be measured from that set alone. S2 measures it in a resampled world. For each draw, $G$ clusters are drawn with replacement from the task's clusters, which makes a population of $G$ clusters drawn independently from the task's empirical distribution, whose mean is the task's $\theta$. The design is then applied to that world, and each interval is scored against the task's $\theta$, the superpopulation target of the world, and against the world's own mean, its design target. This is the bootstrap world of the task's clusters. Its law is discrete, with the task's skewness and its few clusters, so it is a fair stand-in for a superpopulation of clusters like the task's, and it is not the true population that the donors came from. The superpopulation rows of the masking grid are read with that limit. The draws on the fixed task, which score the design target, are the ones of round 5 for D0 (round 4's `draw_L` seeds), and the worlds use new seeds `r7ppi|S2|world|...`.

**The intervals scored against each target.** Under D0: the classical and tuned estimators with `textbook_t|fpc|lin` and `textbook_t|fpc|lin|xf` (design), round 5's superpopulation interval for both (the same point estimate with variance $s_e^2/n_L$, no finite-population factor and no cross-fitting term, $t_{n_L - 1}$, as `round5_ppi_e3_sim.one_draw` computes it in regime A), and Broska and Howes's interval. Under each Bernoulli design: Kluger et al.'s estimator with its cluster bootstrap, and the Horvitz-Thompson and Hájek means with the Poisson-design variance. Every interval is scored against both targets, so that each comparison reads one interval against the target it was built for and against the other.

## 3. The adaptive, balanced design (S3)

Written on 14 October 2026, before any S3 run, from section 2.3 of the track document and section 5 of the S2 memo. Chen, Zhou, Peng and Wang ("Balanced Active Inference", NeurIPS 2025, read in full from `~/hest-1k/ppi_conf_papers/balanced_active_inference.pdf`, section 3 and algorithm 1) draw units with probabilities that mix an uncertainty score with uniform probabilities, $\tau = 0.5$ in their equation (6), and balance the sample by the cube method on the score. Their variance estimators are in a supplement the project does not have. Here the units are whole clusters, and the balance variables are $\pi_g$ and the estimand's own $\bar f_g$, as the track document fixes. For $\theta_2$ the design draws from the valid clusters only, as the estimator definition does, so every draw labels $n_L$ valid clusters.

### 3.1 The target probabilities

With a label-free score $u_g \ge 0$,

$$
\pi^{(0)}_g = \tau\,\frac{n_L\,u_g}{\sum_h u_h} + (1 - \tau)\,\frac{n_L}{G}, \qquad \tau = 0.5,
$$

and $\pi^{(0)}_g = n_L/G$ for every $g$ when $\sum_h u_h = 0$, which is the constant arm with the first score. If some $\pi^{(0)}_g$ exceeds 1, the memo's rule sets every such probability to 1 and multiplies the others by the common factor that makes them sum to $n_L$ minus the number capped, and repeats until none exceeds 1. The factor is at least 1 at every round, because the capped probabilities lose mass to the others, so every final $\pi_g \ge (1 - \tau)\,n_L/G = 0.5\,n_L/G$. Scores are $u_g = \lvert\bar f_g - \bar F\rvert$ on every task and, on the tissue tasks, the Euclidean distance from cluster $g$ to its nearest other cluster in the first 10 principal components of the clusters' mean embeddings (the encoder of the arm, `resnet50` for the permuted arm, none for the constant arm, whose second score is therefore not run).

### 3.2 The cube method

Write $x_g = (\pi_g, \bar f_g)^\top$, $p = 2$, and $a_g = x_g/\pi_g$. A sample $\xi \in \{0, 1\}^G$ is balanced when

$$
\sum_{g=1}^{G} a_g\,\xi_g = \sum_{g=1}^{G} x_g ,
$$

whose first row says $\sum_g \xi_g = n_L$ and whose second says that the Horvitz-Thompson estimate of $\sum_g \bar f_g$ is exact. The flight phase moves a vector $\pi(t)$, started at $\pi(0) = \pi$, by random steps that keep $\sum_g a_g\pi_g(t)$ fixed. At step $t$, take $p + 1 = 3$ units that are still fractional, in a random order fixed for the draw (the fast version of the method, which works on $p + 1$ units at a time), and a nonzero $v$ with $\sum_{g} a_g v_g = 0$ over those three, which for $p = 2$ is the cross product of the two rows of the $2 \times 3$ matrix of their $a_g$ (and a vector orthogonal to the nonzero row when the rows are dependent). Let $\lambda_1, \lambda_2 > 0$ be the largest steps that keep $\pi(t) + \lambda_1 v$ and $\pi(t) - \lambda_2 v$ in $[0, 1]^G$. Then

$$
\pi(t + 1) = \begin{cases} \pi(t) + \lambda_1 v & \text{with probability } \lambda_2/(\lambda_1 + \lambda_2), \\ \pi(t) - \lambda_2 v & \text{with probability } \lambda_1/(\lambda_1 + \lambda_2), \end{cases}
$$

so $\text{E}[\pi(t + 1) \mid \pi(t)] = \pi(t)$, the balance is kept exactly, and at least one more unit becomes 0 or 1. The flight ends when fewer than three units are fractional. The landing phase drops the second balance variable and continues with the first row alone, whose kernel on two fractional units is $v = (1, -1)$, so the sample size stays exactly $n_L$ and only the balance on $\bar f_g$ is lost, on at most two units. Every step of both phases is a martingale step, so

$$
\text{E}\,\xi_g = \pi_g \quad \text{for every } g,
$$

exactly, for any order of processing. The second-order probabilities depend on the order and have no closed form, and the track document asks for both orders to be simulated from the implemented sampler. S3 simulates $\hat\pi_g$ and $\hat\pi_{gh}$ from $R = \max(100{,}000, \lceil 400/\pi^{\mathrm{SRS}}_{gh}\rceil)$ draws, capped at $10^6$, with seeds disjoint from the evaluation draws, and the test of section 3.6 checks $\hat\pi_g$ against $\pi_g$. Each draw records its balance residual $\lvert\sum_L \bar f_g/\pi_g - \sum_g \bar f_g\rvert / \sum_g\lvert\bar f_g\rvert$, and a draw is counted as inexact when it exceeds $10^{-9}$.

### 3.3 The estimators

$\hat\theta_{\mathrm{HT}}$ and $\hat\theta_{\mathrm{H}}$ are those of section 1, with the cube's $\pi_g$. The first balance row makes the size fixed, so the Sen-Yates-Grundy form applies. The second makes $\frac{1}{G}\sum_L \bar f_g/\pi_g = \bar F$ exactly after the flight, so the difference form $\hat\theta_{\mathrm{HT},\lambda}$ equals $\hat\theta_{\mathrm{HT}}$ for every $\lambda$ when the landing leaves the balance exact, which is Chen et al.'s remark 1, and S3 does not run it. $\hat N = \sum_L 1/\pi_g$ is not fixed by the balance unless every $\pi_g$ is equal, so the Hájek mean is a ratio and not the Horvitz-Thompson mean.

### 3.4 An interval for the Hájek mean that does not need $\pi_{gh} > 0$

Write $w_g = \xi_g/\pi_g - 1$. The Hájek mean's error is, exactly,

$$
\hat\theta_{\mathrm{H}} - \theta = \frac{1}{\hat N}\sum_{g=1}^{G}\frac{\xi_g}{\pi_g}\big(\bar z_g - \theta\big) = \frac{1}{\hat N}\sum_{g=1}^{G} w_g\,y_g, \qquad y_g = \bar z_g - \theta,
$$

because $\sum_g y_g = 0$. The balance says $\sum_g w_g x_g = 0$, so the error depends on $y_g$ only through its part that $x_g$ does not explain. To get a variance, approximate the cube design by a Poisson design with the same $\pi_g$ conditioned on the balance equations. Under the Poisson design the $w_g$ are independent with mean 0 and variance $v_g = (1 - \pi_g)/\pi_g$. Treating $T = \sum_g w_g y_g$ and $S = \sum_g w_g x_g$ as jointly normal and conditioning on $S = 0$,

$$
\text{Var}(T \mid S = 0) = \sum_g v_g y_g^2 - \Big(\sum_g v_g y_g x_g\Big)^{\!\top}\Big(\sum_g v_g x_g x_g^\top\Big)^{-1}\Big(\sum_g v_g x_g y_g\Big) = \sum_{g=1}^{G} v_g\big(y_g - x_g^\top\beta\big)^2,
$$

with $\beta = \big(\sum_g v_g x_g x_g^\top\big)^{-1}\sum_g v_g x_g y_g$, the weighted least-squares coefficient (the last step is the usual expansion of a weighted residual sum of squares, skipped). Only the residuals of the regression of $y_g$ on the balance variables, with weights $v_g$, enter, and no $\pi_{gh}$ appears. A cluster with $\pi_g = 1$ has $v_g = 0$ and contributes nothing, as it should, since it is in every sample.

The estimate replaces each population sum by its Horvitz-Thompson estimate over the labelled clusters, $\theta$ by $\hat\theta_{\mathrm{H}}$, and uses the divisor $n_L - p$ in place of $n_L$ for the $p$ fitted coefficients,

$$
\widehat{\text{Var}}_{\mathrm{res}}\big(\hat\theta_{\mathrm{H}}\big) = \frac{1}{\hat N^2}\,\frac{n_L}{n_L - p}\sum_{g \in L}\frac{v_g}{\pi_g}\,\hat e_g^2, \qquad \hat e_g = u_g - x_g^\top\hat\beta, \qquad \hat\beta = \Big(\sum_{g \in L}\frac{v_g}{\pi_g}x_g x_g^\top\Big)^{-1}\sum_{g \in L}\frac{v_g}{\pi_g}x_g u_g ,
$$

with $u_g = \bar z_g - \hat\theta_{\mathrm{H}}$ and $p$ the rank of the $x_g$ over the labelled clusters (2, or 1 when $\bar f_g$ is proportional to $\pi_g$, as on the constant arm with uniform probabilities). The factor $1/\hat N^2$ is the ratio estimator's scaling, as in the Hájek form of section 1.4, so the variability of $\hat N$ enters through the residuals $u_g$ and not separately. With equal probabilities $v_g/\pi_g$ is constant, the regression is on an intercept and $\bar f_g$, and the form becomes $(1 - n_L/G)$ times the residual mean square over $n_L$, the regression estimator's variance under simple random selection, which is the structure of `rej_t` without its $v_a$ term.

Two approximations stand behind it. The conditional Poisson design and the normal approximation in the conditioning hold for a balanced design of high entropy with many units, and with $G$ of 15 to 51 they are rough. And the landing phase leaves $\sum_g w_g \bar f_g = \Delta$ slightly off zero, which adds $\hat N^{-1}\beta_f\Delta$ to the error that the form ignores. That term involves at most two clusters, so it should be small except at the smallest $n_L$, and S3 reports the inexact draws separately.

**The reference distribution** is $t_{n_L - p}$, with the floor $n_L - p \ge 2$ of section 1.6, so the interval is formed at $n_L = 4$ with 2 degrees of freedom.

**Which interval is primary.** The residual form is primary under the cube design. It uses only the labelled clusters and the known $\pi_g$, it needs no $\pi_{gh}$, and its structure is the one the balance creates. Beside it S3 reports the Sen-Yates-Grundy form with simulated $\hat\pi_{gh}$, with the share of zero $\hat\pi_{gh}$ in every cell, and the form with the `apx_size` approximation of section 1.5.

### 3.5 The mixture of D2 and D0

Each draw is D2's (own balance, at $p_a$ of 0.1 and 0.01) with probability 0.5 and simple random otherwise, decided by a seeded coin per draw. Its probabilities are exact mixtures,

$$
\pi^{\mathrm{mix}}_g = 0.5\,\pi^{\mathrm{D2}}_g + 0.5\,\frac{n_L}{G}, \qquad \pi^{\mathrm{mix}}_{gh} = 0.5\,\pi^{\mathrm{D2}}_{gh} + 0.5\,\frac{n_L(n_L - 1)}{G(G - 1)},
$$

computed from D2's simulated $\hat\pi_g$ and $\hat\pi_{gh}$, so every $\pi^{\mathrm{mix}}_{gh} > 0$ and the Sen-Yates-Grundy form is defined. The same three Hájek intervals are computed. The residual form is not derived for this design, whose balance holds only on its D2 half, so under the mixture the Sen-Yates-Grundy form with these probabilities is the primary interval, and the residual form is reported beside it.

### 3.6 The test

On the populations of S1's synthetic test (section 1.9, `round7_ppi_s1_tests.pop`), with $\bar f_g$ the first balance column and $\bar z_g$ as there, at $(G, n_L) \in \{(51, 8), (24, 8), (15, 6)\}$, normal and skewed. The checks are that $\hat\pi_g$ from $10^6$ draws matches $\pi_g$ within three Monte Carlo standard errors for every cluster, that $\hat\theta_{\mathrm{HT}}$ is unbiased within three Monte Carlo standard errors over 20,000 independent draws, that the mean of the primary variance is within 0.10 of the empirical variance of $\hat\theta_{\mathrm{H}}$ in the normal-law cells, and the share of draws with inexact balance.

### 3.7 What I expect, written before any S3 run

1. The inclusion frequencies match the targets, since every step is a martingale, and the smallest $\hat\pi_g$ is at least $0.5\,n_L/G$ less Monte Carlo error (prediction S3.3).
2. The residual form has its mean within 0.10 of the empirical variance in the normal-law test cells, and overstates it in the skewed ones less than the Sen-Yates-Grundy form understates it under D2, because it needs no pair probabilities.
3. On the real tasks, the cube design with the first score is as balanced on $\bar f_g$ as D2 at a small $p_a$, but its weights cost width, so its Hájek interval has a width ratio to D2's `rej_t` of about 1.0 to 1.2 at $n_L = 8$, in line with prediction S3.1.
4. The second score, a distance in embedding space, is unrelated to the residuals, so it gains nothing over uniform probabilities and loses a little width against the first score.
5. The mixture with $\epsilon = 0.5$ is wider than the cube design, since half its draws carry no balance, which is prediction S3.5.

### 3.8 What the synthetic test showed, written after it

The test ran as Slurm job 4900059 on the snapshot of `df344a76`, and every number here is read from `results/round7/ppi/S3_adaptive/tests/run1/s3_tests.csv`.

**The sampler passes.** Over the 180 clusters of the six cells, the largest standardised difference between $\hat\pi_g$ and its target is 3.64, at $G = 15$ with the normal law, and it is the only one above 3, about what 180 independent comparisons give by chance. The Horvitz-Thompson mean with the target probabilities has standardised biases between $-1.11$ and $1.19$ over 20,000 draws. No pair of clusters has $\hat\pi_{gh} = 0$ in any cell, so the Sen-Yates-Grundy form with simulated pair probabilities is defined under the cube design, unlike under D2.

**The landing never leaves the balance exact.** Every draw in every cell has a relative balance residual above $10^{-9}$, so the count of inexact draws planned in section 3.2 is the whole sample and carries no information. With $n_L$ of 6 or 8, the at most two clusters decided in the landing carry weights $1/\pi_g$ of about $G/n_L$, so the imbalance they leave is of the order of a few clusters' share of $\sum_g \lvert\bar f_g\rvert$. Its median over draws is 0.071 to 0.094 of that sum, and its largest value 0.29 to 0.39. The real-task runs report the median residual instead of the count.

**The primary variance falls short at small $G$.** In the normal-law cells, the mean of the residual-form variance of the Hájek mean over the empirical variance is 0.979 at $G = 51$, 0.894 at $G = 24$ and 0.811 at $G = 15$, so it is within 0.10 at $G = 51$ only, and misses by 0.006 at $G = 24$. The Sen-Yates-Grundy form with simulated $\hat\pi_{gh}$ gives 0.980, 0.915 and 0.958 in the same cells, and the Hájek coverages are 0.896, 0.875 and 0.846 with the residual form against 0.899, 0.880 and 0.913 with the Sen-Yates-Grundy form. The shortfall grows as $n_L/G$ grows and is what the landing term of section 3.4 predicts, since the form assumes exact balance on $\bar f_g$ and the landing leaves an imbalance of the order of one cluster. The residual form stays the primary interval as written in section 3.4, because the choice was made before the test, and the Sen-Yates-Grundy form is reported beside it in every cell. Which of the two the paper should use is a question for the S4 memo.

### 3.9 The cube design with the constant balanced (S4b)

Written on 15 October 2026, before any S4b run, from section 5 of the S4 memo. Every S4b run uses the target probabilities of section 3.1 with the first score.

**The balance equations.** Take $x_g = (\pi_g, 1, \bar f_g)^\top$, so $p = 3$ and $a_g = x_g/\pi_g = (1, 1/\pi_g, \bar f_g/\pi_g)^\top$. A balanced sample satisfies $\sum_g a_g\xi_g = \sum_g x_g$, three equations that say

$$
\sum_{g \in L} 1 = n_L, \qquad \hat N = \sum_{g \in L}\frac{1}{\pi_g} = G, \qquad \sum_{g \in L}\frac{\bar f_g}{\pi_g} = \sum_{g=1}^{G}\bar f_g .
$$

The second is the new one. When it holds, $\hat\theta_{\mathrm{H}} = \hat\theta_{\mathrm{HT}}$, since the Hájek mean divides by $\hat N$ and the Horvitz-Thompson mean by $G$. The Hájek mean of the predictions is then $\bar F$ exactly, which removes the error $\bar F(G/\hat N - 1)$ that the S4 memo identified in S3's design. For the outcome, write the error as in section 3.4, $\hat\theta_{\mathrm{HT}} - \theta = \frac{1}{G}\sum_g w_g\bar z_g$ with $w_g = \xi_g/\pi_g - 1$. The new equation is $\sum_g w_g = 0$, so the error no longer depends on the level of $\bar z_g$, only on its part that $(\pi_g, 1, \bar f_g)$ does not explain. On census, where income has a large level against its spread, the Horvitz-Thompson mean under S3's design carried that level, and this design removes it.

**Feasibility.** The flight phase starts from $\pi$ itself, which satisfies the equations, so the equations are met by a fractional point at every $n_L$. Each step works on $p + 1 = 4$ fractional units, takes a nonzero vector in the null space of the $3 \times 4$ matrix of their $a_g$ (found by a singular value decomposition, so a rank below 3 needs no special case), and moves as in section 3.2, keeping all three equations and resolving at least one unit. The flight ends with at most 3 fractional units. The landing then drops $\bar f_g$ and continues on the first two equations, which on 3 fractional units still has a null vector, and ends with at most 2. It then drops the constant and finishes with the size equation alone, by $v = (1, -1)$. Every step is a martingale step, so $\text{E}\,\xi_g = \pi_g$ still holds exactly. The size equation holds exactly. $\hat N = G$ holds exactly when the second landing stage has nothing left to resolve, and otherwise up to the last two units, so each draw records $\lvert\hat N/G - 1\rvert$ beside the residual of the $\bar f_g$ equation. Where every $\pi_g$ is equal (any cell where the first score is zero) $\pi_g$ and $1$ are proportional, the rank is 2, and the design is S3's. On the constant arm $\bar f_g$ is constant too, the rank is 1, and only the size is balanced, a fixed-size design with equal probabilities.

**The intervals.** From S4b on, the primary interval is the Hájek mean with the Sen-Yates-Grundy form and simulated $\hat\pi_{gh}$ (S4 memo, section 3, item 6), with $\hat\pi_g$ and $\hat\pi_{gh}$ from $R$ draws as in section 3.2. The residual form of section 3.4 is reported beside it with $x_g = (\pi_g, 1, \bar f_g)$, and with the failure of section 3.8 stated. The reference distribution is $t_{n_L - p}$, with $p$ the rank of the balance variables over the labelled clusters (3 on informative arms), as $t_{n_L - k - 1}$ in section 1.6 with $k = 2$ balance variables besides the size, and the floor $\nu \ge 2$. So no interval is formed at $n_L = 4$ on informative arms, which counts as a miss in the coverage over all draws. Beside it S4b reports the same intervals with $t_{n_L - 2}$, S3's reference, so that its widths compare with S3's on the same quantile. At $n_L = 8$ the ratio of the two quantiles is $t_{5}/t_{6}$ at 0.95, about 1.04.

**What I expect, written before any S4b run.**
1. The sampler passes the test of section 3.6 as S3's did, and $\lvert\hat N/G - 1\rvert$ is zero in most draws and small in the rest.
2. On census, the Hájek width falls well below S3's 0.912 of D0 classical at $n_L = 8$, and the Horvitz-Thompson width, now close to the Hájek width, falls below 1 (S4b.3), since the level of income no longer enters.
3. On tissue, where $\bar f_g$ varies little in level against its spread across genes, the new design changes little, so the width with S3's quantile is within 0.03 of S3's (S4b.2). With $t_{n_L - 3}$ it is about 4% wider.
4. The residual form remains too small, as in section 3.8, for the same reason.

### 3.10 What the S4b sampler test showed, written after it

Slurm job 4950711 on the snapshot of `44032ae0`, read from `results/round7/ppi/S4b_cube_constant/tests/run1/s4b_tests.csv`. The sampler passes. No cluster of the 180 has $\hat\pi_g$ more than 3 Monte Carlo standard errors from its target (largest 2.82), and the Horvitz-Thompson mean with the target probabilities has standardised biases from $-1.08$ to $1.93$. No pair has $\hat\pi_{gh} = 0$. The rank of the balance variables is 3 in every cell.

**$\hat N = G$ never holds exactly** (`results/round7/ppi/S4b_cube_constant/tests/run1/s4b_tests.csv`). Expectation 1 of section 3.9 is wrong. In every draw of every cell the second landing stage has two units left to resolve, so the constant is always dropped before the end, and $\lvert\hat N/G - 1\rvert$ has a median of 0.028 to 0.048 and a largest value of 0.13 to 0.17. That is about one cluster's weight $1/\pi_g$ against $G$. The balance on $\bar f_g$ is left as inexact as under S3 (median relative residual 0.073 to 0.125).

**The primary variance passes.** With the Sen-Yates-Grundy form, the mean of the Hájek variance over the empirical variance is 0.997, 0.977 and 0.985 in the normal-law cells at $G$ of 51, 24 and 15, and 1.003, 0.985 and 0.980 under the skewed law, so it is within 0.10 everywhere. The residual form gives 0.967, 0.829 and 0.913 in the normal-law cells, too small again at $G = 24$.

## 4. Greedy k-center (S4)

Written on 14 October 2026, before any S4 run, from section 2.3 of the track document and the S4 part of section 5 of the S2 memo.

### 4.1 The design and its exact probabilities

On a tissue task, take the mean embedding of each cluster of the estimand (all clusters for $\theta_3$, the valid ones for $\theta_2$) under the arm's encoder, with `resnet50` for the permuted and constant arms, whose predictions do not enter the selection. Let $d(g, h)$ be the Euclidean distance between clusters $g$ and $h$ in the first 10 principal components of those embeddings (`pcs`, as round 5 computes them). From a start $s$, the rule labels $s$, then repeatedly the cluster whose distance to its nearest labelled cluster is largest, ties going to the lowest index, until $n_L$ clusters are labelled. Call that sample $S(s)$. The start is uniform over the $G$ clusters, so the design has at most $G$ distinct samples, and

$$
\pi_g = \frac{1}{G}\sum_{s=1}^{G}\mathbb{1}\{g \in S(s)\}, \qquad \pi_{gh} = \frac{1}{G}\sum_{s=1}^{G}\mathbb{1}\{g \in S(s),\, h \in S(s)\},
$$

exactly. Every $\pi_g \ge 1/G$, since $g \in S(g)$, so $\hat\theta_{\mathrm{HT}}$ is design-unbiased. At most $G\binom{n_L}{2}$ ordered starts contribute pairs, against $\binom{G}{2}$ pairs in all, and the farthest-point rule tends to return the same outlying clusters from most starts, so most $\pi_{gh}$ are zero and no design-based variance estimate exists.

### 4.2 What is computed, exactly

Every quantity is an average over the $G$ equally likely starts, so it is exact and carries no Monte Carlo error. For each interval, the coverage is $\frac{1}{G}\sum_s \mathbb{1}\{\theta \in I(S(s))\}$, with a start whose interval is not formed counted as a miss beside the conditional coverage and the share formed. The intervals are `textbook_t|fpc|lin` for the classical mean applied as if the sample were simple random, Broska and Howes's interval with `bh_t` and `bh_t_fpc` applied the same way (section 2.1), and the Hájek mean with the exact $\pi_g$ and the `apx_size` approximation of section 1.5 built from them, with $t_{n_L - 1}$ since nothing is balanced. The exact standard deviation of $\hat\theta_{\mathrm{HT}}$ is $\big(\frac{1}{G}\sum_s(\hat\theta_{\mathrm{HT}}(S(s)) - \theta)^2\big)^{1/2}$, its mean being $\theta$, and the classical mean's exact bias and root mean squared error are reported beside it. The same quantities under D0 and under D2 with own balance at the same $n_L$ are read from S1's per-gene tables (`s1m_genes`), the D0 standard deviation being that of the classical mean over its 2,000 draws.

### 4.3 What I expect, written before any S4 run

1. The farthest-point rule labels the outlying clusters from almost every start, so the $\pi_g$ range from $1/G$ to nearly 1 and the share of pairs with $\pi_{gh} = 0$ is above one half at $n_L \le 8$.
2. The classical mean is biased towards the outlying clusters' values, and the interval applied as if the sample were simple random covers well below nominal for $\theta_3$, which is prediction S4.1, wherever the outlying clusters in embedding space differ in expression from the rest.
3. $\hat\theta_{\mathrm{HT}}$ divides the values of the clusters labelled only from their own start by $1/G$, which multiplies them by $G$ in the sum, so its exact standard deviation is several times that of the classical mean under D0, prediction S4.2.
4. `apx_size` assumes a design of high entropy, and k-center is close to the lowest-entropy design there is, so the Hájek interval built on it has no reason to cover and I expect it to miss in either direction.
