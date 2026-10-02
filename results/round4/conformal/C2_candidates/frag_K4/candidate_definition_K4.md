## K4, a group-level quantile model at $o = 0$

**Definition.** For each calibration donor $k = 1, \dots, K$ let $q_k$ be the empirical $(1-\alpha)$ quantile of its own scores $|r_{ki}|$ (centre 0, the zero-mean global predictor of C1). It is the order statistic $Q_\beta$ of the donor's $N_k$ scores with $\beta = 1 - \alpha$, that is the $\lceil N_k \beta (1 - 10^{-12}) \rceil$-th smallest, the same convention and tolerance as the C1 code. Across donors the $q_k$ are treated as an i.i.d. normal sample, and the new donor's quantile is predicted by the upper limit of the usual prediction interval for one new normal draw,
$$\hat q = \bar q + t_{K-1,\,1-\alpha'}\, s_q \sqrt{1 + 1/K}, \qquad \alpha' \in \{0.5, 0.25, 0.1\},$$
where $\bar q$ and $s_q$ (with divisor $K - 1$) are the mean and standard deviation of the $q_k$ and $t_{K-1,p}$ is the $p$-quantile of Student's $t$ with $K-1$ degrees of freedom. The set for a test spot is $|r| \le \hat q$. The variants are `k4_a050`, `k4_a025` and `k4_a010`, evaluated at $o = 0$ only, because the method does not use the test donor's observations. Since $t_{K-1,0.5} = 0$, `k4_a050` equals $\bar q$ exactly and carries no allowance for between-donor spread.

**Assumptions.** (i) The donors are exchangeable. (ii) The $q_k$, which vary through both the donor effect and the finite $N_k$, are approximately normal across donors. (iii) The test donor's own $(1-\alpha)$ quantile $q_{\text{new}}$ is a draw from the same normal law, independent of the $q_k$. (iv) A donor's spot coverage is close to $1 - \alpha$ when the threshold equals that donor's own quantile.

**Guarantee.** The method is model-based and not distribution-free. Under (i) to (iii) exactly, $P(q_{\text{new}} \le \hat q) = 1 - \alpha'$. This is a prediction-interval statement about the new donor's quantile, not a statement about spot coverage, and $\alpha'$ is not the miscoverage level of the set. No finite-sample guarantee for spot coverage is claimed, and none holds without the normality model. The criterion's part (c) is therefore met only in the sense of a model-based guarantee with the model named.

**Risk under heavy tails.** This is the route most likely to be sharp and least likely to be safe under $t_3$ tails. Under $t_3$ the donor quantile is a right-skewed function of the donor scale and of the estimation noise of the 90 percent quantile of a heavy-tailed law, so the normal prediction limit from $K$ donors is too small in the upper tail exactly when an unusually heavy donor arrives. The $t$ factor corrects for estimating $s_q$ from $K$ donors but not for the departure from normality.

**Implementation choices, fixed before the full run.**

1. $q_k$ uses the order-statistic definition above and not an interpolated quantile.
2. The centre is 0 and the threshold $\hat q$ is not clipped. Because $q_k \ge 0$ and the $t$ factor is nonnegative for $\alpha' \le 0.5$, $\hat q \ge 0$. The threshold is finite for every $K \ge 5$, so `frac_infinite` is 0 in every row by construction.
3. Rows are produced for $\alpha = 0.1$ only. Replicate draws use seed tag `C1`, so each replicate is identical to C1's and the rows pair with C1's reference methods. 5,000 replicates in every one of the 522 cells (58 cells at each of $K \in \{5, 7, 9, 10, 12, 15, 20, 25, 50\}$, semireal included).
4. The price of validity is the mean over replicates of $\hat q / q^\star$ with $q^\star$ the C1 oracle, as in `summarise`.
5. Normality check, `k4_qk_normality.csv`: for every cell at $K = 10$ (the two semireal cells, plus the synthetic normal and $t_3$ cells as a reference, column `kind`), per replicate the Shapiro-Wilk test on the ten simulated $q_k$ with its $p$-value, sample skewness and excess kurtosis, summarised per cell (`level = cell`) and, for the semireal cells, per gene (`level = gene`). The check does not change any method output.

**Evidence on the normality assumption (semireal, $K = 10$).** In both semireal cells the median Shapiro-Wilk $p$ is 0.07, the share of replicates rejecting at 0.05 is about 0.46 and at 0.01 about 0.31, the mean skewness is 1.1 to 1.2 and the mean excess kurtosis 1.8 to 1.9. Under no donor effect (synthetic, share 0) the check behaves as a calibrated test (median $p$ about 0.5, rejection about 0.05). As the between-donor share rises the $q_k$ become right-skewed and normality is rejected at 0.05 in 10 to 49 percent of replicates (the larger values at tau 0), so assumption (ii) does not hold in the semireal setting.

**Outcome at $\alpha = 0.1$, all 522 cells (own results only; criterion part (b) needs the C1 reference prices and was not assessed here).**

| variant | minimum coverage | cells with coverage $\ge 0.89$ | price range (all cells) |
|---|---|---|---|
| `k4_a050` | 0.775 | 72 of 522 | 0.76 to 1.00 |
| `k4_a025` | 0.869 | 468 of 522 (all 54 failures are $t_3$ at share 0.5) | 0.97 to 1.17 |
| `k4_a010` | 0.908 | 522 of 522 | 1.02 to 1.43 |
