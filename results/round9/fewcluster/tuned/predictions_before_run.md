# Track fewcluster, step I2-2, predictions written before the run

*26 October 2026, before any code for I2-2 was written. Plan: `docs/round09/i01/fewcluster/round09_fewcluster_decision.md`, section 5.*

Setting. PPI with the coefficient fitted by least squares with an intercept on the labelled clusters, $\hat\theta = \bar z_S + \hat\lambda_S(\bar F - \bar f_S)$, with the interval $\hat\theta \pm c\sqrt{(1 - n/G)\,s^2_{r,S}/n}$ and $s_{r,S}$ the residual standard deviation of the sample fit. Its coverage depends on the population only through the population least-squares residual $\hat e$ of $z$ on $(1, f)$. The class is $\{z : \kappa(\hat e) \le \kappa_0\}$. A finite $c$ is defeated on samples where $\hat e_S$ is affine in $f_S$ and the sample line does not pass through the population mean, so two-piece populations $z = 1_{B_2}(\delta_a + \delta_c f)$ play the part the two-point population plays for a fixed coefficient. The computed tuned frontier is the smallest $\kappa(\hat e)$ found over two-piece populations with $\pi(k) > \alpha$. It is an upper bound on the true tuned frontier, since the search over $B_2$ is not exhaustive.

Prediction vectors $f$: independent standard normal, lognormal ($\sigma = 1$), and standard normal with one value moved to 4 standard deviations, each at $G = 15$ and $G = 24$, with $n$ of 6, 8, 10 and 12, $\alpha = 0.10$.

- **Q1.** In every cell the computed tuned frontier is below the fixed-coefficient frontier $\kappa_2(k^\ast - 1)$ of `s3_frontier_exact.csv`.
- **Q2.** At $G = 24$, $n = 8$ with normal $f$, it is below 0.11, at least 30% below the fixed-coefficient value 0.158.
- **Q3.** Averaged over the three $f$ types, the tuned frontier at $n$ is within 25% of the fixed-coefficient frontier at $n - 1$ (tuning costs about one labelled cluster).
- **Q4.** For the population found at $G = 24$, $n = 8$ with normal $f$, the exact coverage of the tuned interval with $c = 100$ at the perturbed population is below 0.90, and equals $1 - \pi(k)$ to three decimals.
