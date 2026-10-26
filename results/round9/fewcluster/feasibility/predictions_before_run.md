# Track fewcluster, step S3, predictions written before the run

*26 October 2026, before any code for S3 was written. Plan: `docs/round09/i01/fewcluster/round09_fewcluster_plan.md`, section 4.*

Definitions. For a population of cluster values $z_g$ and predictions $f_g$, the residual is $e_g = z_g - a - b f_g$ with $(a, b)$ the least-squares fit over all $G$ clusters (the population coefficient), and the raw version uses $b = 0$. The max-share is $\kappa = \max_g (e_g - \bar e)^2 / \sum_h (e_h - \bar e)^2$. The boundary $\kappa^\ast(n, G, \alpha)$ is $(1 - k^\ast/G)/k^\ast$, where $k^\ast$ is the smallest $k$ with $\binom{G - k}{n}/\binom{G}{n} \le \alpha$. This is the max-share of a two-point population with $k^\ast$ atypical clusters. By a hand count, $k^\ast = 6$ and $\kappa^\ast = 0.125$ at $G = 24$, $n = 8$, $\alpha = 0.10$. The code confirms this, and it is not a prediction.

HEST tasks use uni_v2, the 50 genes of each task, and donor means of log1p expression and of predictions.

- **P1.** On CCRCC the median over genes of the residual $\kappa$ is above 0.4, and donor INT5 carries the largest share for more than half of the genes.
- **P2.** On INDIANA_KIDNEY the median residual $\kappa$ is between 0.15 and 0.35, and on LUNG_XENIUM it is below 0.25.
- **P3.** On every HEST task the median gene's residual $\kappa$ is beyond the boundary at the task's middle design size ($n = 8$ for CCRCC and INDIANA_KIDNEY, $n = 6$ for LUNG_XENIUM), so the frontier would say no equivariant procedure is valid there for the median gene.
- **P4.** For ACS by state ($G = 51$, mean log income by state, raw values since the predictions are on Longleaf), $\kappa$ is below 0.15.
- **P5.** At $G = 24$, $n = 8$, over populations taking three distinct values with $\kappa \le \kappa^\ast$, the worst-case coverage of the 90% interval $\bar z_S \pm t_{n-1, 0.95}\sqrt{(1 - n/G)\,s^2/n}$ is below 0.85.

Each is scored after the run as held, partly held, refuted or not tested, in `predictions_scored.md` beside this file.

## Addendum, 26 October 2026, written before the second local run

After the novelty map returned and before any code for these quantities was written. The frontier is now defined with both blocks of a two-point population, $\pi(k) = \{\binom{G-k}{n} + \binom{k}{n}\}/\binom{G}{n}$, and $k_0(\kappa_0)$ is the smallest $k \le G/2$ with $(1 - k/G)/k \le \kappa_0$. A max-share bound $\kappa_0$ is equivalent to no residual lying more than $\Lambda_0 = \sqrt{\kappa_0 (G - 1)}$ residual standard deviations from the mean.

- **P6.** On the grid of `s3_boundary_grid.csv` the second-block term $\binom{k}{n}$ changes $k^\ast$ in no cell with $\alpha = 0.10$.
- **P7.** The bound on configurations whose largest level set is below $G/2$ is below 0.01 in every cell with $n \ge 6$, so the gap between the impossibility and the possibility conditions is empty there for $\alpha \ge 0.01$.
- **P8.** For $G = 24$, the fraction of populations of 24 independent standard normal values whose max-share is at most $\kappa^\ast(24, 8, 0.10)$ is below 0.2. For $G = 51$ at $n = 8$ it is below 0.05.
