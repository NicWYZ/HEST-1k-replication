# Round 9, track fewcluster, interval 1 plan

*26 October 2026. Written by the fewcluster session at the start of its work, after reading the brief, the round 9 masterplan, the round 8 positioning note in full, the direction scan, the probe documents and the SIGN, PROXY and SENS verdicts. Living until the interval's first decision memo, then frozen. Recommendations are `[proposed]`.*

## 1. The setting, written once

A population has $G$ clusters. Cluster $g$ has a contribution $z_g$, such as a donor's mean expression of one gene, and a prediction $f_g$, such as the donor's mean prediction, known for every cluster. A design draws $n$ clusters to label, by default simple random sampling without replacement, and the target is the design-based mean

$$
\theta = \frac{1}{G}\sum_{g=1}^{G} z_g .
$$

The data are $D = \big(S, \{z_g\}_{g \in S}, \{f_g\}_{g = 1}^{G}\big)$. The project's sizes are $n$ of 4 to 16 and $G$ of 14 to 51. With a fixed coefficient $\lambda$ the PPI estimator is the difference estimator $\bar z_S - \lambda(\bar f_S - \bar F)$, whose error is the sample mean error of the residuals $e_g = z_g - \lambda f_g$. A guarantee here means a statement about coverage that holds for every $n$ and $G$ and every population in a stated class, not as $n$ or $G$ grows.

## 2. What no procedure can do, and what that leaves

The first fact the track works from is a finite-population form of the Bahadur and Savage (1956) impossibility. It is written here so the novelty map can check it and so the candidate claims below can be stated against it. It is expected to be classical.

Take any procedure $C(D)$ and any population $z$. For a cluster $j$ and a number $M$, let $z^{(j, M)}$ equal $z$ except that $z_j$ is replaced by $z_j + M$. Its mean is $\theta + M/G$. On the event $j \notin S$, the data under $z^{(j, M)}$ are the data under $z$. So if $C$ covers with probability at least $1 - \alpha$ under every $z^{(j, M)}$,

$$
P_z\big(j \notin S,\; \theta + M/G \in C(D)\big) \;\ge\; 1 - \alpha - \frac{n}{G} \qquad \text{for every } j .
$$

Averaging over $j$, and using that given $S$ a fraction $1 - n/G$ of clusters are unsampled while the event $\theta + M/G \in C(D)$ does not depend on $j$,

$$
P_z\big(\theta + M/G \in C(D)\big) \;\ge\; \frac{1 - \alpha - n/G}{1 - n/G} \qquad \text{for every } M .
$$

When $\alpha < 1 - n/G$ the right side is positive for every population, so a procedure valid over all populations returns an interval that is unbounded with at least that probability. At $G = 24$, $n = 8$ and $\alpha = 0.10$ the bound is $0.85$. Predictions do not change this, since $f_j$ is the same under $z$ and $z^{(j, M)}$. A valid interval of finite length therefore needs a restriction on the population. The useful questions are which restriction a user can check or defend, what the sharpest procedure under it is, and how much the predictions and the design move the boundary.

The data say what kind of restriction matters (brief, section 4). On CCRCC the skew comes from one technical-outlier donor that the predictions do not see. A restriction on the predictions' errors in absolute units is not something a user can defend there. A scale-free restriction on how much of the residual variation a few clusters can carry is closer to what the probe and the multi-gene structure can inform.

## 3. Candidate claims for the novelty map

Each is written as a claim the track might prove. None is believed yet, and each goes to the novelty map before any work is built on it. The scan's SIGN (sign-change tests for few-cluster PPI), PROXY (a prediction-built pseudo-population bootstrap) and SENS (bounded selection odds) are not re-proposed. Claim K below differs from SIGN in asking for a finite-sample guarantee over an explicit population class under sampling without replacement, with no symmetry assumption.

- **F, a frontier.** Let $\kappa(e) = \max_g (e_g - \bar e)^2 / \sum_h (e_h - \bar e)^2$ be the largest share of the residual sum of squares carried by one cluster. Under simple random sampling of $n$ of $G$, there is a sharp, explicit boundary $\kappa^\ast(n, G, \alpha)$, set by the hypergeometric probability that a sample misses every one of $k$ atypical clusters. Below it, a location and scale equivariant procedure can be valid in finite samples over every population with $\kappa \le \kappa_0$. Above it, none can. Predictions and the design move a task across the boundary only by changing $\kappa$ of the residuals, not by changing the boundary.
- **K, a calibrated interval.** Below the boundary, a studentized difference-estimator interval with an exact critical value $c(n, G, \kappa_0, \alpha)$ covers at least $1 - \alpha$ for every population with $\kappa \le \kappa_0$, with the worst case attained at populations taking few distinct values, so that $c$ can be computed exactly. It is compared with the $t$ reference, CR2 and the sign-change test of Canay, Romano and Shaikh.
- **B, bounded residuals.** Given a bound on the residuals' range, a finite-sample valid interval for few-cluster PPI under sampling without replacement (Hoeffding and Serfling, empirical Bernstein and Serfling, or betting), with a minimax statement about its length at $n \le 16$. Expected to be mostly in print through the betting and risk-limiting audit literature.
- **D, what the design buys.** With a cheap first phase that measures every cluster noisily (the probe), the smallest take-all set that brings the remaining residuals below $\kappa^\ast$. Expected to be close to two-phase sampling, so it is checked but not led with.

## 4. Steps of this interval

- **S1. This plan.** Written and committed before any run or search.
- **S2. The novelty map.** Five independent subagents, one theme each, none of which has seen this session's reasoning beyond the claims of section 3. The themes are (1) the exact or worst-case coverage of $t$-type intervals under sampling without replacement from finite populations, with Lindeberg or Hájek-type and max-share conditions, and finite-population Berry-Esseen bounds; (2) finite-sample valid intervals for a finite-population mean under sampling without replacement with side information (Hoeffding and Serfling, betting, risk-limiting audits with reported values, prediction-powered e-values); (3) impossibility and minimax results (Bahadur and Savage and its finite-population forms, minimax strategies in survey sampling, rare-element detection, lower bounds for PPI); (4) few-cluster econometrics and cluster randomized trials under skew and heterogeneity (sign-change and wild bootstrap tests, Ibragimov and Müller, Hagemann, size results of Pötscher and Preinerstorfer, few treated clusters, constrained randomization); (5) survey sampling with few primary units and skewed populations (Cochran's rule and its Edgeworth form, outlier-robust estimation, take-all strata, Pólya posterior and Bayesian bootstrap intervals). Each grades every claim of section 3 as taken, mostly taken, partly open or open, with a query log and a candidate table in the scan's format, saved to `results/round9/fewcluster/novelty/`. OpenAlex is not used by the subagents. The session runs forward-citation lookups itself if Nicolas approves the credential.
- **S3. Feasibility computations,** run while S2 works, with predictions written before the run in `results/round9/fewcluster/feasibility/predictions_before_run.md`. They are the boundary $\kappa^\ast(n, G, \alpha)$ over the project's grid, the residual $\kappa$ of the real tasks (ACS by state locally, HEST tasks on Longleaf from the per-spot prediction files), and the exact worst-case coverage of the finite-population $t$ interval over populations with few distinct values.
- **S4. A decision memo** that reads S2 against S3, says which claim the track takes forward or why none survives, and fixes the next interval. If no claim survives, the memo says so and the session reports to Nicolas as a roadblock.

## 5. What would count

A result for this track is a theorem with a finite-sample guarantee or a sharp impossibility, stated for a class a user can check or defend, that survives S2 and its follow-up checks, and that changes what happens on at least one of the project's tasks. A computation that only reproduces under-coverage already in the record does not count.
