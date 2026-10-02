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
