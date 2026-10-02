# Round 4, conformal track, stage C2: candidate definitions

Each section below is the definition the candidate's unit wrote before its run, copied unchanged
from `results/round4/conformal/C2_candidates/frag_<K>/candidate_definition_<K>.md`. The module that
implements each one is in `code/scripts/round4_conf_c2_<name>.py`, byte-identical to the copy in
the fragment's `code/` directory (md5 recorded in the C2 report, section 4). The fixed criterion and its
application are in `docs/round4_conf_C2_report.md`.


### K1, smoothed HCP at $o = 0$ (method name `k1_smoothed`)

**Construction.** HCP at level $\beta = 1 - \alpha$ takes the measure $\nu = \frac{1}{K+1}\sum_{k \le K} \hat F_k + \frac{1}{K+1}\delta_{+\infty}$, where $\hat F_k$ is donor $k$'s empirical score distribution (each spot carries $1/N_k$), and sets $q = Q_\beta(\nu)$. Each donor, and the test donor's atom at $+\infty$, carries a block of mass $1/(K+1)$, so the levels HCP can resolve at the donor level are multiples of $1/(K+1)$. Write $x = \beta (K+1)$, $m = \lfloor x \rfloor$ and $\theta = x - m \in [0,1)$. K1 draws $U \sim \mathrm{Unif}(0,1)$, independent of the data, and sets $q = Q_{(m+1)/(K+1)}(\nu)$ if $U < \theta$ and $q = Q_{m/(K+1)}(\nu)$ otherwise. This is the smoothed conformal construction of Vovk, Gammerman and Shafer applied to donor blocks: $U$ decides how many whole donor blocks are counted below the threshold, so the fractional block that HCP's ceiling rounds up is counted with probability $\theta$. $U$ does not enter the within-donor weights $1/((K+1)N_k)$, and the test donor's mass stays at $+\infty$ in both branches. At $\alpha = 0.1$: $\theta = 0$ at $K = 9$ (K1 equals HCP there); $q = +\infty$ with probability $\theta$ at $K = 5$ ($0.4$) and $K = 7$ ($0.2$); for $K \ge 10$ the threshold is always finite.

**Assumptions.** Hierarchical exchangeability of the $K+1$ donors, as for HCP; $U$ independent of everything.

**Guarantee.** Lee, Barber and Willett's theorem holds for HCP at every level, so given $U$ the coverage is at least the level used, and at most the level plus $2/(K+1)$ when scores are distinct. Averaging over $U$,
$$P(\text{cover}) \ge (1-\theta)\frac{m}{K+1} + \theta\frac{m+1}{K+1} = \frac{m+\theta}{K+1} = 1-\alpha,$$
and $P(\text{cover}) \le 1 - \alpha + 2/(K+1)$ with distinct scores. The probability is joint over data, test spot and $U$. The lower bound is attained when each donor's score distribution is concentrated at a point and the points are distinct (between-donor share 1), where the rule is the rank-randomised split-conformal rule on $K+1$ exchangeable donor scores with coverage exactly $(m+\theta)/(K+1)$; "equality in expectation" holds in that configuration. In other configurations HCP's own slack remains (with no donor effect the coverage is about $\beta(K+1)/K$), and tie handling cannot remove it. Criterion part (c) is met.

**Implementation choices.** Tolerance: $m = \lfloor x(1+10^{-12})\rfloor$, $\theta = \max(0, x-m)$, and quantiles with C1's relative tolerance $10^{-12}$. One $U$ per replicate and $\alpha$, from the method's own generator (seed key `C1|cell|rep|k1_smoothed|o0`), so replicate data are those of C1; $U$ is drawn even when $\theta = 0$. Scores, sorted runs and weights are those of C1's fast HCP. Only $o = 0$, only $\alpha = 0.1$, one variant. Coverage in a replicate is the fraction of 500 test spots with $|r| \le q$; the reported cell coverage is the mean over replicates, so it estimates the marginal-over-$U$ coverage.

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

## K5. A scaled score inside HCP and GHCP

**Idea.** Replace the absolute score $|r - c|$ by $|r - c| / \hat\sigma$, where $\hat\sigma$ is an estimate of the within-donor residual scale. A donor with heavier-than-average noise (under $\tau = 0.3$ the donor scale is $b_k = \exp(\tau\eta_k)$) then contributes smaller scaled scores, and the test donor's interval is stretched or shrunk by its own scale. The prediction interval for a test spot is $c \pm q\,\hat\sigma_{\text{test}}$, where $q$ is the host method's weighted $(1-\alpha)$ quantile of the scaled held-out scores.

**Variants.**

- `k5_ghcp`: GHCP with the primary settings of the C1 simulator (selection $\{k : N_k > o\}$, $\eta = 0$, within-group adaptation on, $n_{\text{glob}} = 13$) and the scaled score. For each participating group $j$ the training block is its first $m = \lfloor o/2 \rfloor$ residuals; the centre is $c_j = \lambda\,\bar r_{j,1:m}$ with $\lambda = m/(n_{\text{glob}} + m)$ as in GHCP; the scale $\hat\sigma_j$ is computed from the same block by one rule, identical in every group (below). Held-out scores are $|r_{ji} - c_j|/\hat\sigma_j$ for $i > m$, with GHCP's weights $1/((|S_{\text{cal}}|+1)L_j)$, $L_j = N_j - m$. The test donor's $o - m$ held-out scores use $\hat\sigma_{\text{test}}$ built from its own first $m$ observations, with the weight $1/((|S_{\text{cal}}|+1)L_{K+1})$ each and the atom $(N_{J_0} - o)/((|S_{\text{cal}}|+1)L_{K+1})$ at $+\infty$. The reported half-width is $q\,\hat\sigma_{\text{test}}$. Defined for $o \ge 4$ (so that $m \ge 2$); on the C1 grid, $o \in \{5, 10, 25, 50, 100\}$. When the selection set is empty (for example $N = 100$ at $o = 100$) the within-test-donor split rule of GHCP Remark 2.2 is used with the scaled held-out scores.
- `k5_hcp`: defined at $o = 0$ only. A within-donor scale for the test donor needs observations from the test donor, and there are none. The only scale that can be attached to a donor without observations is a constant shared by all donors, and a shared constant cancels in the scaled score. K5 inside HCP at $o = 0$ therefore coincides with HCP, and the rows are HCP computed by the simulator's HCP function and reported under this name. They carry no information beyond C1's `hcp` rows; the width ratio to HCP is 1 by construction. Estimating each calibration donor's scale from its own data and multiplying back by a guessed test-donor scale would not be valid and is not done.

**Scale rule.** $\hat\sigma = \max\{\,\mathrm{sd}_{1:m},\ 0.1\cdot\mathrm{rms}_{1:m},\ 10^{-12}\}$, where $\mathrm{sd}_{1:m}$ is the sample standard deviation (divisor $m-1$) of the block about its own mean and $\mathrm{rms}_{1:m}$ is the root mean square of the block about zero (the global predictor is the known zero mean). The relative floor stops a block of two nearly equal residuals from producing a near-zero scale; it is equivariant to rescaling the data, depends only on the group's own block, and is the same function in every group. It was fixed before any run and not tuned.

**Assumptions.** Those of GHCP: group-level exchangeability (A1), reference sizes exchangeable and independent of the group laws (A2), and within-group i.i.d. observations (A3). In addition, as GHCP appendix B.1 requires, $\hat\sigma_j$ must be built in every group, test group included, by the same rule from that group's local training block only. All of this holds by construction in C1.

**Guarantee.** The host's, unchanged. Conditional on the training blocks, the held-out scaled scores within each group are i.i.d., and the test spot's scaled score is exchangeable with the test group's held-out scores and, across groups, with those of the calibration groups. Coverage is at least $1-\alpha$ in finite samples without distributional assumptions (GHCP Theorem 2.1), and at most $1 - \alpha + E[(1 + \rho_o(\max N))/|S|]$ when there are no ties. The pattern of infinite thresholds is that of GHCP with the same selected donor, because the weights and the atom at $+\infty$ are unchanged. At $o = 0$ the guarantee is HCP's.

**Implementation notes.** The generator seed used by the runner is keyed on the registered method name; K5 is registered under the name of the C1 `ghcp` entry inside its own process so that the selected test-size donor $J_0$ is the same as C1's GHCP at each (cell, replicate, $o$). The output variants are named `k5_ghcp` and `k5_hcp`. Run at $\alpha = 0.1$ only, 5000 replicates, seed tag `C1`, so the replicate draws coincide with C1's. The fast path is checked equal to an independent plain-array implementation and, with the scale set to one, to the simulator's GHCP function (maximum absolute difference 0 on 40 random replicates at all five $o$).

**Not assessed.** Top-decile coverage has no meaning in C1, which has no predicted values; it is left to C3. Width at matched coverage is computed by the lead from the per-replicate tables, pairing `k5_ghcp` with C1's `ghcp` on the same replicate and $o$.

## K6, the switch rule (lower-bound document section 5, addendum 1 item 4)

**Method name and scope.** `k6_switch`, evaluated at $o = 0$ only, $\alpha = 0.1$, on the whole C1 grid. The score is $s = |r|$ and the centre is $c = 0$.

**The rule.** Let $F_1, \dots, F_K$ be the empirical score CDFs of the $K$ calibration donors and let $D = \max_{k,l} \sup_t |F_k(t) - F_l(t)|$. The code evaluates $D = \sup_t [\max_k F_k(t) - \min_k F_k(t)]$ at the pooled score points, which is the same number. The tolerance is
$$d = d_0 + 2\epsilon_N, \qquad \epsilon_N = \sqrt{\frac{\log(2/0.01)}{2 N_{\min}}}, \qquad N_{\min} = \min_k N_k,$$
the Dvoretzky-Kiefer-Wolfowitz half-width at level 0.01 for the smallest calibration donor. If $D \le d$ the threshold is the empirical quantile at level $1 - \alpha + \delta$ of the donor mixture $K^{-1}\sum_k F_k$ (weight $1/(K N_k)$ per spot, no atom at $+\infty$). Otherwise the threshold is the HCP threshold at level $1 - \alpha$ (weight $1/((K+1)N_k)$ per spot and mass $1/(K+1)$ at $+\infty$), identical to the C1 method `hcp`, so it is infinite exactly when $1/(K+1) > \alpha$, that is at $K = 5$ and $K = 7$.

**Assumptions.** Hierarchical exchangeability of the calibration and test donors, and independent identically distributed scores within a donor.

**Guarantee.** None is stated, and part (c) of the criterion is unmet. Section 8.3 of the lower-bound document shows that the rule as specified is not valid even when the donor laws are revealed exactly: with ten $N(0,1)$ donors and one point mass just above the pooled threshold, at $K = 10$ and $\alpha = 0.1$, the coverage is $0.89899 < 0.9$, which attains the worst-case bound of case 3 of section 5. With finite $N_k$ the DKW event has probability at least $1 - K\gamma$, $\gamma = 0.01$, and off that event coverage is bounded below only by zero, so even the repaired rule of section 8.3 covers at least $1 - \alpha - K\gamma$ (a possible loss of $0.1$ at $K = 10$). The repaired rule is not run.

**Implementation choices.**

1. $d_0 = 0$, so the tolerance is the DKW noise band alone.
2. $\delta$ comes from the probe in `round4_conf_c2_lower_bound.py`, which measures distance as a normal location shift $g$ in within-donor standard deviations. The Kolmogorov distance between $N(0,1)$ and $N(g,1)$ is $2\Phi(g/2) - 1$, so $g = 2\Phi^{-1}((1+d)/2)$. $\delta(K, d)$ is the smallest value on the probe's bisection (14 steps on $[0, \alpha - 10^{-9}]$, upper end returned, $\delta = 0$ if the worst coverage at $\delta = 0$ is already at least $1 - \alpha$) at which `worst(K, alpha, g, delta)` has coverage at least $1 - \alpha$. `worst` is imported; the bisection is the one in the probe's `main()`, restated because `main()` has no callable form.
3. $\delta$ is computed exactly on a grid of $d \in \{0.03, 0.05, 0.0728, 0.1, 0.1456, 0.2, 0.3256, 0.5, 0.8664\}$ for each $K$. The grid contains the tolerances $2\epsilon_N$ at $N = 2000, 500, 100$ (0.0728, 0.1456, 0.3256), so equal-$N$ cells use the exact $\delta$ for their $(K, N_{\min})$. For unequal $N$ and for the semi-real pools, $\delta$ is linearly interpolated in $d$ between grid points and clamped at the ends. $\delta$ is increasing and convex in $d$ on this range, so interpolation can only overstate $\delta$ slightly.
4. Cap. The probe's configurations reach Kolmogorov distance at most $2\Phi(1.5) - 1 = 0.8664$ ($g \le 3$), so beyond that tolerance the probe measures nothing and the rule is HCP. Because $N_{\min} \ge 100$ on the grid, the largest tolerance is $0.3256$ and the cap never binds.
5. The pooled quantile is the donor mixture quantile (the object the probe uses), not the spot-weighted pooled quantile of the C1 method `pooled`; they coincide when the $N_k$ are equal.
6. $D \le d$ is inclusive. The rule is deterministic given the calibration data. Replicate draws are those of C1 (seed tag `C1`), so rows pair with C1's reference methods.

**Prediction C2.6** (addendum 1): K6 covers at least 0.89 in every cell and meets (b) only in cells with between-donor share 0.1, so it fails (b) overall, and its price of validity equals HCP's at shares 0.3 and 0.5.

**Run record.** The grid was computed on Longleaf in ten jobs (one per $K$, with $K = 50$ split in two by cell), from the module `round4_conf_c2_k6_switch.py` and the C1 simulator at md5 76fda34ee622e299bbaa806e5c8da98a, with 5,000 replicates in each of 522 cells. The per-donor-count $\delta$ tables for $K = 5, 7, 9, 10$ were computed once locally by the same code and staged as an input; the other $K$ computed theirs in the job. Pooled-branch frequency, mean $D$, mean $d$ and mean $\delta$ per cell are in `k6_branch_stats.csv`. At $K = 5$ and $K = 7$ the probe's $\delta$ is 0.097 and 0.085, and the pooled branch is rarely taken.
