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
