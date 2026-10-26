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
