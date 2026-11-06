# F2 BOUNDARY, interval 2 feasibility note (27 October 2026)

Verdict: stop. The plan's prediction for this track is mostly refuted. A selection effect on the boundary exists and is clean to state, but it does not produce size inflation at the bandwidths one would use, the standard robust bias correction does not help, and the test has little power at an estimated boundary.

## What was checked in the literature

I ran 22 queries (10 web, 12 arXiv API calls spaced 6 s apart; OpenAlex not used) aimed first at the named suspects. Cattaneo, Titiunik and Yu (arXiv 2511.06474, 2505.05670, 2505.07989) treat a known boundary, with distance-based local polynomials and robust bias correction with q = p + 1. Porter and Yu treat an unknown cutoff estimated on the same data in one dimension. Neufeld et al. and Dharamshi et al. supply the thinning construction, with independence of the two parts only given the latent mean. Hivert et al. (2210.13172) supply the continuum null for estimated clusters, without space. Inference post region selection (2506.11564) selects rectangles on the same data. Wombling papers are model based and have no thinning. I found no paper that thins, estimates a boundary on one part and runs a regression discontinuity test on the other for a latent random field. This is provisional. I read search excerpts and abstracts, not method sections, for every suspect in this interval (the interval 1 checker read some in full), the arXiv phrase queries returned almost nothing, and journal-only papers were not opened. Logs are in the two novelty CSVs.

## Derivation in the simplest case

Take one dimension, a stationary Gaussian log-intensity $g$, and a selection statistic $T=K_s*(g+\text{noise})$, where the noise comes from $Y_1$ and $K_s$ is the smoothing kernel. A boundary $x_0$ is a point where $T$ crosses its threshold $\tau$ upward with slope $v=T'(x_0)$. Conditioning on this event is a standard Slepian computation and I skip its algebra. It gives the mean profile of $g$ around the boundary

$$
m(d)=E\{g(x_0+d)\mid T(x_0)=\tau,\ T'(x_0)=v\}=a(d)\,\frac{\tau-\mu_T}{\sigma_T^2}+b(d)\,\frac{v}{\sigma_{T'}^2},
$$

with $a(d)=\mathrm{Cov}\{g(x_0+d),T(x_0)\}$ even in $d$ and $b(d)=\mathrm{Cov}\{g(x_0+d),T'(x_0)\}$ odd. Because $Y_2$ is independent of $Y_1$ given $\lambda$, the test at $\hat\Gamma$ is an ordinary regression discontinuity test at a fixed curve for this conditional profile, and the question reduces to what the local-linear jump estimator does to $m$.

For a power term $d^k$ on each side, the weighted local-linear intercepts on the two sides are $c_k h^k$ and $(-1)^k c_k h^k$. I computed $c_2=c_3=-0.1001$ numerically for the triangular kernel. The jump bias of the even term is therefore exactly zero at order $h^2$, which corrects the interval 1 checker's remark that the bias is $O(h^2)$ times curvature. That holds only when the second derivative jumps across the boundary, and it does not for a continuous field. For the odd term $m(d)=b_1d+b_3d^3+\dots$ the bias does not cancel,

$$
B_{LL}(h)=2c_3\,b_3\,h^3 .
$$

The profile is a smoothed step of width $w$ of order the smoothing scale, so $b_3<0$ and $B_{LL}$ has the sign of the high-minus-low direction. For $m(d)=\tanh(d/w)$ the numerical bias as a fraction of the half-step is 0.004, 0.026, 0.122, 0.237 and 0.421 at $h/w=0.5,1,2,3,5$. Standardised, $B_{LL}/\mathrm{se}$ grows like $h^{3}\sqrt{Lh}$ for a boundary of length $L$ spots, so the size distortion is controlled by $h/w$ and not by the field's own curvature. For a threshold away from the mean, $a(d)$ adds an even term that again cancels at $h^2$. A boundary taken from an independent replicate has a flat mean profile and a bias with mean zero.

Question (1) is a corollary. The two estimated domains have a mean difference of $(1-\epsilon)\{E[\lambda\mid T>\tau]-E[\lambda\mid T<\tau]\}$, which is of order one while the standard error shrinks with $n$, so the difference-in-means test rejects with probability tending to one.

## Simulation

I simulated a log-Matern field on a 64 by 64 lattice (periodic generation on 128 by 128, then cropped), standard deviation 0.7 on the log scale, with $\nu\in\{0.5,1.5,2.5\}$, range 3, 6, 12 spacings, mean count 2, 8, 20, and $\epsilon\in\{0.3,0.5,0.7\}$. The boundary came from a Gaussian smooth ($\sigma_s=2$) of $Y_1/\epsilon$ and a two-means threshold. Tests used $h\in\{2,3,5\}$. There were 89 settings with 1000 replicates each (Monte Carlo standard error at most 0.016) and fixed seeds. The control used the boundary of an independent replicate on the same $\lambda$. "RBC" is local quadratic at the same $h$, which is the Calonico-Cattaneo-Titiunik construction with equal bandwidths. "CR" uses 8 by 8 block clusters.

| Boundary | Test | h=2 | h=3 | h=5 |
|---|---|---|---|---|
| selected on Y1 | local linear | 0.055 | 0.056 | 0.212 |
| selected on Y1 | local linear, CR | 0.077 | 0.057 | 0.126 |
| selected on Y1 | RBC | 0.133 | 0.083 | 0.110 |
| selected on Y1 | local cubic | 0.143 | 0.101 | 0.070 |
| independent | local linear | 0.009 | 0.012 | 0.043 |

(Pooled rejection rates at nominal 0.05 over the settings with $\sigma=0.7$, $\sigma_s=2$.) Findings follow.

1. Difference in means rejected in every replicate of every setting (minimum 1.000).
2. The independent boundary is conservative (about 0.01), because the HC1 variance absorbs field variation. The selected boundary raises rejection to the nominal level at $h\le3$ and to 0.21 at $h=5$ (setting maximum 0.58). Root-mean-square bias over standard error is about 0.5 for the selected boundary and 0.2 to 0.3 for the independent one at $h\le3$. So selection adds bias, but it is masked by a conservative variance estimate at small $h$.
3. Inflation falls with range (0.34, 0.19, 0.11 at $h=5$ for ranges 3, 6, 12), the reverse of the plan's prediction, and it grows with mean count.
4. In one setting (mean count 8, $\nu=1.5$, range 6, $\epsilon=0.5$) size is nominal when $h/\sigma_s\le1.5$ (0.036 to 0.062 over four cases) and inflated when the ratio is 2 or more (0.116 to 0.210 over four cases, with $\sigma_s=3$, $h=5$ at 0.097 in between). Rule of thumb from this grid only: $h\lesssim1.5\sigma_s$.
5. Standard RBC and a local cubic correction both over-reject at $h=2,3$, so they do not restore size. I did not diagnose why. The cubic design is nearly collinear at $h=2$ on a lattice with few distinct distances, and the oracle bias over standard error is near 1.
6. Applying the local-linear operator to the simulated mean profile predicts the mean bias at $h=5$ (correlation 0.89 across 89 settings, sign agreement 0.92, fitted slope 0.39 because bins were coarse) and fails at $h=3$ (correlation 0.20). The mean bias at $h\le3$ is negative, opposite to the $h^3$ sign I predicted, and I have no explanation. The derivation is therefore supported only for $h$ well above the smoothing scale.
7. Optimal $\epsilon$. A power design (field sd 0.25, range 4, curved boundary, jump 0.8 on the log scale, mean count 20, $h=3$) gave power at the estimated boundary of 0.11 to 0.24 across $\epsilon$, against 1.00 at the true boundary, because boundary error (about 5 percent of pixels misassigned) blurs the step. Power peaks near $\epsilon=0.4$ to 0.5 and is flat within Monte Carlo error (0.029) over 0.3 to 0.6. A first power design with a stronger field produced boundaries unrelated to the jump and I discarded it.

## Data check

Predictions were published before the run (f_BOUNDARY_predictions_before_run.md). The check used 3 CCRCC and 3 INDIANA_KIDNEY slides, 8 genes per slide (top, middle and lowest mean count), 20 thinnings each with $\epsilon=0.5$, a spot-lattice version of the same pipeline. It is descriptive, with no truth, and covers 48 gene-slide cells.

| Prediction | Outcome |
|---|---|
| P1 difference in means rejects almost always above mean count 1, under 60 percent below 0.2 | held (1.00 and 0.49) |
| P2 local linear at h=3 rejects 15 to 40 percent | refuted (0.060) |
| P3 RBC rejects less than local linear in at least 70 percent of cells | refuted (40 percent) |
| P4 CR rejects less than HC in at least 80 percent | refuted (15 percent) |
| P5 local-linear rejection rises with h | held (0.039, 0.060, 0.160) |

## Stop rule and the plan's prediction

The first clause of the stop rule is not met, since size inflation exists at $h=5$. At $h=2,3$, which are within the smoothing scale, there is no inflation beyond Monte Carlo error, the real-tissue rejection rates are near nominal, and the test has little power at an estimated boundary. The selection effect is real, but the remedy is to keep $h$ below the smoothing scale, and the answer to question (3) in the bandwidth-for-size sense is that one simple inequality, not a new correction. I score the plan's prediction for F2 as refuted at the stated bandwidths and refuted on the range dependence. I recommend stop, and flag that this is a judgment: a fresh agent should check it before the session relies on it.

## What a paper would need

A theorem for random fields with an estimated boundary that gives $b_3$ in terms of the field covariance, the smoothing kernel and $\epsilon$, and a uniform-in-$\hat\Gamma$ statement conditional on $\lambda$. A bias correction that works for the odd selected profile, which neither $q=p+1$ nor a lattice cubic does here. A power theory for the estimated-boundary test, where the boundary error and not the noise limits power. The remainder is a short proposition plus simulation on top of Cattaneo, Titiunik and Yu, and I would not build a paper on it.
