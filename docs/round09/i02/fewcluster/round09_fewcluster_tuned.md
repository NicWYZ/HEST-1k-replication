# Round 9, track fewcluster, the frontier with a tuned coefficient, and the real tasks

*26 October 2026. Written by the fewcluster session, interval 2, steps I2-2 and I2-4. It extends `docs/round09/i01/fewcluster/round09_fewcluster_frontier.md` to PPI whose coefficient is fitted on the labelled clusters, and places the project's tasks against both frontiers. The statements were proved by the session and again by a fresh agent from the statements alone, with exact enumeration at small sizes (`results/round9/fewcluster/verify_tuned/verify_tuned_report.md`). That agent's corrections are taken in below. One of them corrects a remark in `results/round9/fewcluster/tuned/predictions_scored.md` (section 4). The novelty of the tuned statements has not yet been checked. NOV6 covered the fixed-coefficient statements only. Recommendations are `[proposed]`.*

## 1. Setting

The notation is that of the frontier note. On a sample $S$ the coefficient is the least-squares slope with an intercept, and the interval is

$$
\hat\theta_S = \bar z_S + \hat\lambda_S\,(\bar F - \bar f_S), \qquad \hat\theta_S \;\pm\; c\,\sqrt{\Big(1 - \frac{n}{G}\Big)\frac{s^2_{r,S}}{n}},
$$

where $s^2_{r,S}$ is the residual sum of squares of the sample fit over $n - 2$. It needs $3 \le n < G$ and $f$ non-constant on every sample. Let $\hat e(z)$ be the residual of the least-squares regression of $z$ on $(1, f)$ over all $G$ clusters, and define the class through it,

$$
\mathcal{K}_{\text{OLS}}(\kappa_0) = \{z : \hat e(z) \ne 0,\ \kappa(\hat e(z)) \le \kappa_0\}.
$$

A procedure is equivariant in this setting if $z' = a + c f + b z$ with $b > 0$ gives $C(S, z'_S, f) = a + c\bar F + b\,C(S, z_S, f)$. The tuned interval is equivariant in this sense.

## 2. Statements

**T0 (reduction).** *The coverage of the tuned interval at $z$ depends on $z$ only through $\hat e(z)$, and is unchanged when $\hat e(z)$ is multiplied by any $b \ne 0$.* Write $z = a + c f + \hat e$. Then $\theta = a + c\bar F$, because $\hat e$ has mean zero, and the sample fit gives $\hat\lambda_S = c + \hat\lambda_S(\hat e)$. Hence

$$
\hat\theta_S - \theta = \bar{\hat e}_S + \hat\lambda_S(\hat e)\,(\bar F - \bar f_S),
$$

and the sample residuals of $z$ are those of $\hat e$. Both sides of the coverage inequality scale with $|b|$. The verifier confirmed this to $10^{-14}$.

**T1′ (impossibility).** *Suppose some $z^\ast$ has $\kappa(\hat e(z^\ast)) < \kappa_0$, and a set $W$ of samples with $P(W) > \alpha$ has, for each $S \in W$, $z^\ast_S = a_S + c_S f_S$ exactly with $a_S + c_S \bar F \ne \theta(z^\ast)$. Then every equivariant procedure with coverage at least $1 - \alpha$ on $\mathcal{K}_{\text{OLS}}(\kappa_0)$ has $P_x(C \text{ unbounded}) \ge P(W) - \alpha$ for every population $x$.* For $z_\varepsilon = z^\ast + \varepsilon x$ and $S \in W$, the data are the transform of $x$'s data with $(a, c, b) = (a_S, c_S, \varepsilon)$, so covering $\theta(z_\varepsilon) = \theta(z^\ast) + \varepsilon\bar x$ requires

$$
\frac{\theta(z^\ast) - a_S - c_S\bar F}{\varepsilon} + \bar x \;\in\; C(S, x_S, f),
$$

which tends to $\pm\infty$. Since $\kappa$ is continuous, $z_\varepsilon$ stays in the class for small $\varepsilon$, which is where the strict inequality is used. The verifier found no random direction that keeps the class at equality. The pigeonhole step is that of Theorem 1. For two-piece populations $z^\ast = 1_{B_2}(d_a + d_c f)$ with $|B_2| = k$, every sample inside $B_2$ or its complement is affine in $f$, and $P(W) = \pi(k)$ unless one of two linear conditions on $(d_a, d_c)$ holds, which is not generic. In 1,037 and 5,173 affine structures at $G$ of 8 and 10 the verifier found no case where the sample line passes through the mean.

**T2′ (possibility).** *Let $\beta_{\text{OLS}}(\kappa_0)$ be the largest, over the class, of the fraction of samples on which $\hat e(z)_S$ is affine in $f_S$. If $\beta_{\text{OLS}}(\kappa_0) \le \alpha$, a finite $c$ makes the tuned interval valid over the class.* By T0 it suffices to take $\hat e$ in the compact set $\{e \perp 1, f;\ \sum_g e_g^2 = 1;\ \kappa(e) \le \kappa_0\}$. On that set the numerator above is bounded, because the sample spread of $f$ is positive on every sample. A sample missed at $c_j \to \infty$ therefore has $s_{r,S} \to 0$, and the limit point is affine in $f$ on every sample missed along the sequence. The rest is the argument of Theorem 2. T1′ and T2′ meet at

$$
\kappa^\dagger(f, G, n, \alpha) = \inf\big\{\kappa(\hat e(z)) : \text{the fraction of samples on which } \hat e(z)_S \text{ is affine in } f_S \text{ exceeds } \alpha\big\},
$$

except at the boundary point and in degenerate structures. On exact enumerations of every affine structure at $(G, n)$ of $(8, 4)$ and $(10, 5)$, the verifier's worst-case search found coverage at least $1 - \alpha$ just below each level and exactly one minus the affine fraction just above it, in 68 of 68 cases.

**What changes with tuning.** For a fixed coefficient the defeating samples are those on which the residual is constant, and the frontier $\kappa_2(k^\ast - 1)$ depends on $(G, n, \alpha)$ alone. With a tuned coefficient the defeating samples are those on which the residual is affine in the predictions. The frontier then depends on $f$, through which subsets of the points $(f_g, \hat e_g)$ can be collinear, and it has no closed form. The verifier sketched an exact computation. An affine sample lies on a unique maximal line, the count is a sum of $\binom{m}{n}$ over lines, and for $G = 24$, $n = 8$, $\alpha = 0.10$ only a single line of at least 19 clusters can exceed $\alpha$. The smallest max-share on each such structure is the reciprocal of a convex maximisation attained at a vertex. It has not been run.

## 3. Numbers

From `results/round9/fewcluster/tuned/i22_tuned_frontier.csv` (two-piece search, an upper bound on $\kappa^\dagger$) at $\alpha = 0.10$. With independent standard normal, lognormal and normal-with-one-outlier predictions at $G$ of 15 and 24 and $n$ of 6 to 12, the tuned frontier found is 0.37 to 0.74 of the fixed-coefficient frontier in all 24 cells. At $G = 24$, $n = 8$ with normal predictions it is 0.0936, against 0.158. Over 12 further normal draws of $f$ the verifier found 0.0785 to 0.1008, with mean 0.0890, and for one draw an exhaustive search over all 42,504 sets $B_2$ gave 0.0826. Allowing the second piece to be any function rather than a line lowered that value by 0.1% (`checks_numbers_G24_freeu_top40.csv`, provisional). The exact coverage of the tuned interval at the population found, perturbed, with $c = 100$, is 0.897233 over all 735,471 samples. This equals $1 - \pi(5) = 1 - 75{,}582/735{,}471$, by the session's run and independently by the verifier's.

In standard-deviation units, $\Lambda = \sqrt{\kappa_0(G - 1)}$, the tuned frontier of 0.0936 at 8 of 24 is $\Lambda = 1.47$, against 1.91 for a fixed coefficient.

## 4. A correction, the spike at a high-leverage cluster

`results/round9/fewcluster/tuned/predictions_scored.md` says a spike at a cluster with an extreme prediction is nearly invisible to a max-share bound. That overstates it. For a spike at cluster $g$ the population residual has

$$
\kappa(\hat e) = \frac{\max\{(1 - h_{gg})^2,\ \max_{j \ne g} h_{gj}^2\}}{1 - h_{gg}},
$$

with $h$ the hat matrix of $(1, f)$ (verifier, T3a, to $4 \times 10^{-15}$). Since $\sum_{j \ne g} h_{gj}^2 = h_{gg}(1 - h_{gg})$, the largest share stays at $g$ only while $h_{gg} \le 1 - 1/G$. At $G = 24$ the verifier's scan gave $\kappa = 0.575 = 1 - h_{gg}$ for a prediction 4 standard deviations out and 0.261 at 8, and then a floor between about 0.21 and 0.25 set by the other clusters' predictions, even at 512 standard deviations. So a spike at a high-leverage cluster is cheaper in max-share than a spike elsewhere, down to that floor, and it defeats every equivariant interval whenever the cluster is unsampled. The correct sufficient condition for such a spike to be in the class is the strict inequality $\max\{(1 - h_{gg})^2, \max_{j \ne g} h_{gj}^2\} < \kappa_0 (1 - h_{gg})$.

## 5. The real tasks

From `results/round9/fewcluster/hest/i24_task_summary.csv` (Longleaf job 9f5ad9c3, uni_v2, residuals of donor means on donor-mean predictions; scores in `results/round9/fewcluster/feasibility/predictions_scored_i24.md`).

| Task | $G$ | middle $n$ | median residual max-share | fixed frontier | genes beyond it | median tuned frontier (upper bound) | genes beyond it |
|---|---|---|---|---|---|---|---|
| CCRCC | 24 | 8 | 0.533 | 0.158 | 1.00 | 0.095 | 1.00 |
| INDIANA_KIDNEY | 25 | 8 | 0.336 | 0.160 | 0.90 | 0.093 | 1.00 |
| LUNG_XENIUM | 15 | 6 | 0.312 | 0.267 | 0.71 | 0.153 | 0.997 |
| ACS by state | 51 | 8 | 0.147 | 0.071 | 1 of 1 | 0.053 | 1 of 1 |

On CCRCC, INT5 carries the largest residual share for 0.80 of the 50 genes. LUNG_XENIUM has 343 genes. For ACS the predictions move the largest share from DC (raw max-share 0.209) to Alaska (residual 0.147). At the design sizes the project uses, essentially no gene on any task is inside the frontier that a scale-free guarantee needs, with either coefficient. The project's repeated under-coverage at these sizes is what the theory predicts.

## 6. What this adds, and what is open

- The tuned frontier is where the predictions enter the theory. Fitting the coefficient on the sample enlarges the set of populations that defeat every equivariant interval. The adversary can now hide a second line, not only a second level, and high-leverage clusters are cheap places to hide a spike. On synthetic predictions the frontier drops by a quarter to two thirds. That is a finite-sample cost of tuning in validity, as distinct from the variance cost that Mani, Xu, Lipton and Oberst (arXiv:2505.20178) give for independent samples (round 8 note, section 3.2), and from first-order asymptotics, where tuning is free. Whether it is in print has not been checked (next step).
- Open are an exact computation of $\kappa^\dagger$ on the project's prediction vectors (the verifier's route), the boundary points, and the stratified and two-phase designs (I2-3).
