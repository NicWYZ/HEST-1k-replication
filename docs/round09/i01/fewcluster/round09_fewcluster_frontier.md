# Round 9, track fewcluster, the max-share frontier

*26 October 2026. Written by the fewcluster session. The statements were proved by the session, then proved again independently by a fresh agent that had seen only the statements, with brute-force checks at small sizes (`results/round9/fewcluster/verify/verify_frontier_report.md` and the scripts and CSV files beside it). That agent found one error, an off-by-one in where the frontier lies, and several missing hypotheses. All are corrected below. The literature position is in section 6 and is provisional until the precise-statement check (NOV6) returns. Recommendations are `[proposed]`.*

## 1. Setting

There are $G$ clusters with values $z \in \mathbb{R}^G$ and predictions $f \in \mathbb{R}^G$ known for every cluster. Fix a coefficient $\lambda$ (any real number, including 0) and write the residuals and the target as

$$
e = z - \lambda f, \qquad \theta = \frac{1}{G}\sum_{g} z_g = \lambda \bar F + \bar e .
$$

The design is simple random sampling without replacement of $n$ clusters, $2 \le n < G$, and the data are $D = (S, z_S, f)$. The max-share of a non-constant $e$ is

$$
\kappa(e) = \frac{\max_g (e_g - \bar e)^2}{\sum_h (e_h - \bar e)^2},
$$

and the class is $\mathcal{K}(\kappa_0) = \{z : e \text{ non-constant},\ \kappa(e) \le \kappa_0\}$. Equivalently, no residual lies more than $\Lambda_0 = \sqrt{\kappa_0 (G - 1)}$ residual standard deviations from the residual mean. This is the finite-sample form of Hájek's (1960) condition for the sample mean to be asymptotically normal.

A procedure $C$ maps $D$ to a subset of the line. It is equivariant if, for every $a \in \mathbb{R}$ and $b > 0$, the population $z' = \lambda f + a + b(z - \lambda f)$ gives

$$
C(S, z'_S, f) = \lambda \bar F + a + b\,\big\{C(S, z_S, f) - \lambda \bar F\big\}.
$$

The difference-estimator (PPI) interval with the coefficient $\lambda$, of the form estimate plus or minus a multiple of a standard error, is equivariant. So are sign-change, wild-bootstrap and $t$-type intervals built on the residuals. PPI with a least-squares coefficient fitted with an intercept is equivariant for every reference $\lambda$, while the coefficient fitted without an intercept is not (verification report, Theorem 1, remark e). A procedure that is not equivariant must use a known scale, such as a bound on the residuals' range, which is the bounded-residual setting of claim B, already in print.

Two quantities carry the results. For $1 \le k \le G/2$,

$$
\kappa_2(k) = \frac{1 - k/G}{k}, \qquad \pi(k) = \frac{\binom{G-k}{n} + \binom{k}{n}}{\binom{G}{n}},
$$

with $\binom{k}{n} = 0$ when $k < n$. A two-point population, with $k$ clusters at one value and $G - k$ at another, has max-share $\kappa_2(k)$, and $\pi(k)$ is the probability that the sample falls inside one of its two groups. $\kappa_2$ decreases in $k$, and $\pi$ is non-increasing on $k \le G/2$. Let $k^\ast$ be the smallest $k \le G/2$ with $\pi(k) \le \alpha$.

## 2. Lemma 0, the unrestricted impossibility

*If $C$ covers $\theta$ with probability at least $1 - \alpha$ at every population in $\mathbb{R}^G$, then for every population $z$ and every $M$,*

$$
P_z\big(\theta + M/G \in C(D)\big) \;\ge\; \frac{1 - \alpha - n/G}{1 - n/G}.
$$

Let $z^{j}$ equal $z$ with $z_j$ replaced by $z_j + M$, so $\theta(z^j) = \theta + M/G$, and let $A = \{\theta + M/G \in C(D)\}$ under $z$. Samples without $j$ give the same data under $z$ and $z^j$, so

$$
P_z(j \notin S,\ A) = P_{z^j}\big(j \notin S,\ \theta(z^j) \in C(D)\big) \;\ge\; 1 - \alpha - \frac{n}{G}.
$$

Every sample leaves exactly $G - n$ clusters out, so $\sum_j 1\{j \notin S\} = G - n$ in every sample, and summing over $j$ gives

$$
\sum_{j=1}^{G} P_z(j \notin S,\ A) = (G - n)\,P_z(A) \;\ge\; G\Big(1 - \alpha - \frac{n}{G}\Big).
$$

Dividing by $G - n$ gives the claim. The bound is on the unconditional probability. Two of the novelty checkers (NOV2 and NOV3) read it as conditional on $j \notin S$, and the verifier confirmed the unconditional reading by proof and by checking the identity to $10^{-12}$ on 300 random procedures. The lemma is the total-variation form of Bahadur and Savage (1956), with total variation $n/G$, and is not claimed as new.

## 3. Lemma 1, the two-point population is extremal

*If $e$ is constant on a set $B$ of $G - k$ clusters, $1 \le k \le G - 1$, then $\kappa(e) \ge (1 - k/G)/k$. For $k \le G/2$, equality holds exactly when $e$ takes one common value off $B$, different from its value on $B$.*

Shift and scale so that $e = 0$ on $B$, with values $x_1, \dots, x_k$ on the complement $A$. Write $\bar e = \sum_i x_i / G$, $d_i = x_i - \bar e$ and $\bar x = \sum_i x_i / k$. Then $\sum_{i \in A} d_i = k \bar x (1 - k/G)$, and by Cauchy-Schwarz

$$
P := \sum_{i \in A} d_i^2 \;\ge\; \frac{\big(\sum_i d_i\big)^2}{k} = k\,\bar x^2\Big(1 - \frac{k}{G}\Big)^2, \qquad Q := (G - k)\,\bar e^2 = \frac{(G - k)\,k^2\,\bar x^2}{G^2},
$$

so $P \ge Q\,(G - k)/k$. The largest share is at least the average share in $A$,

$$
\kappa(e) \;\ge\; \frac{P/k}{P + Q},
$$

which increases in $P/Q$, and at $P/Q = (G - k)/k$ it equals $(1 - k/G)/k$. Equality needs every $d_i$ equal and the largest share to fall in $A$. The share of a cluster in $B$ is $\bar e^2/(P + Q) = k/\{G(G - k)\}$ at the two-point population, which is at most $(1 - k/G)/k$ exactly when $k \le G/2$. Numerical minimisation at $G$ of 8, 10 and 12 reproduced $(1 - k/G)/k$ to $10^{-6}$ for every $k \le G/2$ (verification report).

## 4. The frontier

**Theorem 1 (impossibility).** *Suppose that $\kappa_2(k) < \kappa_0$ and $\pi(k) > \alpha$ for some $k \le G/2$. Then every equivariant procedure with coverage at least $1 - \alpha$ at every population in $\mathcal{K}(\kappa_0)$ satisfies, for every population $z \in \mathbb{R}^G$,*

$$
P_z\big(C(D) \text{ is unbounded}\big) \;\ge\; \pi(k) - \alpha .
$$

Fix $z$, put $u = z - \lambda f$, choose any set $B_2$ of $k$ clusters with complement $B_1$, and for $\varepsilon > 0$ let

$$
z_\varepsilon = \lambda f + 1_{B_2} + \varepsilon u, \qquad \theta(z_\varepsilon) = \lambda \bar F + \frac{k}{G} + \varepsilon \bar u .
$$

The residual $1_{B_2} + \varepsilon u$ tends to the two-point population, whose max-share is $\kappa_2(k) < \kappa_0$. Since $\kappa$ is continuous at non-constant points, $z_\varepsilon \in \mathcal{K}(\kappa_0)$ for small $\varepsilon$. This is where the strict inequality is used. For $S \subseteq B_1$ the data of $z_\varepsilon$ are those of the transform of $z$ with $(a, b) = (0, \varepsilon)$, and for $S \subseteq B_2$ with $(a, b) = (1, \varepsilon)$. By equivariance, $z_\varepsilon$ is covered on such a sample exactly when

$$
S \subseteq B_1:\ \ \lambda \bar F + \frac{k/G}{\varepsilon} + \bar u \in C(S, z_S, f), \qquad S \subseteq B_2:\ \ \lambda \bar F - \frac{1 - k/G}{\varepsilon} + \bar u \in C(S, z_S, f).
$$

The samples inside $B_1$ or $B_2$ have probability $\pi(k)$, so coverage at least $1 - \alpha$ forces the covered ones among them to have probability at least $\pi(k) - \alpha$, for every $\varepsilon$. There are finitely many samples, so along a sequence $\varepsilon_j \to 0$ one fixed set $W$ of them, with probability at least $\pi(k) - \alpha$, is covered every time. On $W$ the set $C(S, z_S, f)$, which does not depend on $\varepsilon$, contains points tending to $+\infty$ (samples in $B_1$) or $-\infty$ (samples in $B_2$). The conclusion is that the procedure is unbounded, which allows half-lines and does not require $C$ to be the whole line.

**Theorem 2 (possibility).** *Let $\beta(\kappa_0)$ be the largest, over $z \in \mathcal{K}(\kappa_0)$, of the fraction of samples on which $e$ is constant. If $\beta(\kappa_0) \le \alpha$, there is a finite $c$ such that the fixed-coefficient interval*

$$
\lambda \bar F + \bar e_S \;\pm\; c\,\sqrt{\Big(1 - \frac{n}{G}\Big)\frac{s^2_{e,S}}{n}}
$$

*(a single point when $s_{e,S} = 0$) covers $\theta$ with probability at least $1 - \alpha$ at every population in $\mathcal{K}(\kappa_0)$.*

Coverage is invariant under $e \mapsto a + b e$, so it suffices to take $e$ in the compact set $\{\bar e = 0,\ \sum_g e_g^2 = 1,\ \kappa(e) \le \kappa_0\}$. Suppose no finite $c$ works. Then for each $j$ some $e_j$ in the set has more than $\alpha\binom{G}{n}$ samples missed at $c = j$. By pigeonhole, one fixed set $W$ of more than $\alpha\binom{G}{n}$ samples is missed along a subsequence, and by compactness $e_j \to e^\ast$ in the set. A missed sample has

$$
s_{e,S}(e_j) \;<\; \frac{|\bar e_S(e_j)|}{j\sqrt{(1 - n/G)/n}} \;\le\; \frac{1}{j\sqrt{(1 - n/G)/n}} \;\to\; 0,
$$

so $e^\ast$ is constant on every sample in $W$, and $|W| \le \beta(\kappa_0)\binom{G}{n} \le \alpha\binom{G}{n}$, a contradiction. The theorem is for a fixed coefficient. For a least-squares coefficient Theorem 1 still applies, and Theorem 2 has not been shown. The worst-case coverage over the class is never above $1 - \beta(\kappa_0)$, and in the verifier's searches it reached $1 - \beta(\kappa_0)$ at a finite $c$ between 1 and 10.

**Proposition 3 (computing $\beta$).** *With $R = \max_{m < G/2}\{\lfloor G/m \rfloor \binom{m}{n} + \binom{G \bmod m}{n}\}/\binom{G}{n}$,*

$$
\max\{\pi(k) : k \le G/2,\ \kappa_2(k) \le \kappa_0\} \;\le\; \beta(\kappa_0) \;\le\; \max\Big(\max\{\pi(k) : k \le G/2,\ \kappa_2(k) \le \kappa_0\},\ R\Big).
$$

The lower bound is the two-point population. For the upper bound, let the level sets of $e$ have sizes $m_1 \ge m_2 \ge \dots$, so that $\binom{G}{n}\beta$ counts $\sum_i \binom{m_i}{n}$. If $m_1 \ge G/2$, put $k = G - m_1$. Lemma 1 gives $\kappa_2(k) \le \kappa_0$, and since $\binom{a}{n} + \binom{b}{n} \le \binom{a + b}{n}$ the count is at most $\binom{G-k}{n} + \binom{k}{n}$. If $m_1 < G/2$, convexity of $\binom{x}{n}$ in $x$ bounds the count by $\lfloor G/m_1 \rfloor\binom{m_1}{n} + \binom{G \bmod m_1}{n}$. On every cell of the project's grid with $n \ge 6$, $R < 0.02$ (`s3_frontier_exact.csv`, column `rest_bound`), so at $\alpha = 0.10$ the two theorems meet and the frontier is exact. The verifier enumerated every partition for $G$ from 6 to 16 and $n$ from 2 to 6 (932 cases) with no violation.

**The frontier.** Combining the three results, for $n \ge 6$ on the grid and $\alpha = 0.10$, a finite-length equivariant interval valid over $\mathcal{K}(\kappa_0)$ exists when $\kappa_0 < \kappa^\ast = \kappa_2(k^\ast - 1)$, and none exists when $\kappa_0 > \kappa^\ast$. At $\kappa_0 = \kappa^\ast$ the theorems are silent. The session first placed the frontier at $\kappa_2(k^\ast)$, which is where the $k^\ast$ two-point population enters the class and is one step too low. The verifier found this, and an exact search over every partition put the smallest $\kappa_0$ with $\beta > \alpha$ at $\kappa_2(k^\ast - 1)$ in all 22 cells where $k^\ast$ exists. As $G$ grows with $\Lambda_0$ fixed, the two-point population with a fraction $p$ of atypical clusters has $\Lambda = \sqrt{(1 - p)/p}$ and is missed with probability near $(1 - p)^n$, so the frontier in standard-deviation units tends to

$$
\Lambda^\ast(n, \alpha) = \sqrt{\frac{\alpha^{1/n}}{1 - \alpha^{1/n}}},
$$

which is 1.13, 1.46, 1.73, 2.17 and 2.54 at $n$ of 4, 6, 8, 12 and 16 for $\alpha = 0.10$. At $\Lambda_0 \to \infty$ the condition becomes $2^{1 - n} > \alpha$, that is $n < 1 + \log_2(1/\alpha)$, which is the iid boundary of Hendriks, IJzerman-Boon and Klaassen (2006) as the checkers report it.

**Corollary 4 (design).** *For any design of fixed size $n$ that may depend on the predictions but not on $z$, some choice of $B_2$ with $|B_2| = k$ has probability at least $\pi(k)$ that the sample falls inside $B_1$ or $B_2$, so Theorem 1 holds for that design with the same condition.* For a fixed sample $S$ and $B_2$ drawn uniformly among sets of size $k$, $P(S \subseteq B_2) + P(S \subseteq B_1) = \pi(k)$ by the identity $\binom{G}{n}\binom{G-n}{k-n} = \binom{G}{k}\binom{k}{n}$ and its counterpart for $G - k$. Averaging over the design gives exactly $\pi(k)$, so some $B_2$ attains at least $\pi(k)$. The class is invariant under permutations of the clusters, and the proof of Theorem 1 goes through with that $B_2$. Simple random sampling is therefore minimax among fixed-size designs for this purpose. A design informed by the predictions cannot move the frontier unless the class itself ties atypical clusters to the predictions.

## 5. The frontier in numbers

From `results/round9/fewcluster/feasibility/s3_frontier_exact.csv`, $\alpha = 0.10$. The last column is the fraction of 20,000 populations of independent standard normal values that lie strictly inside the frontier.

| $G$ | $n$ | $k^\ast$ | $\pi(k^\ast - 1)$ | $\kappa^\ast = \kappa_2(k^\ast - 1)$ | $\Lambda^\ast$ | Gaussian populations inside |
|---|---|---|---|---|---|---|
| 15 | 4 | 7 | 0.103 | 0.100 | 1.18 | 0.000 |
| 15 | 6 | 4 | 0.185 | 0.267 | 1.93 | 0.446 |
| 15 | 8 | 3 | 0.200 | 0.433 | 2.46 | 0.923 |
| 15 | 12 | 2 | 0.200 | 0.933 | 3.61 | 1.000 |
| 24 | 4 | 11 | 0.114 | 0.058 | 1.16 | 0.000 |
| 24 | 6 | 7 | 0.138 | 0.125 | 1.70 | 0.022 |
| 24 | 8 | 6 | 0.103 | 0.158 | 1.91 | 0.167 |
| 24 | 12 | 4 | 0.109 | 0.292 | 2.59 | 0.878 |
| 24 | 16 | 3 | 0.101 | 0.458 | 3.25 | 0.996 |
| 51 | 4 | none | | | | none |
| 51 | 6 | 16 | 0.108 | 0.047 | 1.53 | 0.000 |
| 51 | 8 | 12 | 0.121 | 0.071 | 1.89 | 0.009 |
| 51 | 12 | 8 | 0.133 | 0.123 | 2.48 | 0.533 |
| 51 | 16 | 6 | 0.138 | 0.180 | 3.00 | 0.915 |

At $n = 4$ of 51 no max-share bound supports a guarantee. The partition into two groups of 25 and one singleton already gives $\beta > \alpha$ at $\kappa_0 = 0.020$ (verification report). At 8 labelled clusters of 24, a guarantee needs every residual within 1.91 standard deviations of the mean, which 0.167 of Gaussian populations of that size satisfy. At 8 of 51 the share is 0.009.

The project's data sit beyond the frontier where they could be checked. Mean log income by state, without predictions, has max-share 0.209 (DC, 3.23 standard deviations from the mean of states, `s3_acs_states_kappa.csv`), above $\kappa^\ast$ at every $n \le 16$ of 51. The HEST tasks could not be checked on 26 October because Longleaf was unreachable. The CCRCC donor INT5 has average expression 3.98 standard deviations above the donor mean (`results/round9/stud/atypical_donor_diagnostics.csv`), which as a single-cluster share would be about $3.98^2/23 = 0.69$, but that is an average over genes and not a residual max-share for any gene.

## 6. What is prior art and what may be new (provisional)

Five checkers (`results/round9/fewcluster/novelty/novelty_structured_results.json`) found no paper stating Theorems 1 and 2 or Proposition 3 for sampling without replacement from a finite population under a max-share bound. The closest precedents they found are these. Pötscher and Preinerstorfer (arXiv:2412.17470, Theorem 2.2) give a finite-sample necessary and sufficient leverage condition for a size-controlling critical value of heteroskedasticity-robust tests, in a Gaussian regression model. Hendriks, IJzerman-Boon and Klaassen (2006) give the iid boundary that the frontier tends to as $\Lambda_0 \to \infty$. Bahadur and Savage (1956), Dufour (1997) and Bertanha and Moreira (2020) give the unrestricted impossibility. Hájek (1960), Bloznelis (1999) and Chiang, Sasaki and Wang (arXiv:2308.10138) give asymptotic or Berry-Esseen versions of the max-share condition. Several checkers judged the impossibility half routine and the possibility half a short but genuine argument. A deeper check of the exact statements against these papers in full (NOV6) has been dispatched. This section will be superseded by the decision memo once it returns.

## 7. Limits

- Theorem 2 covers the fixed-coefficient interval only. Its critical value is shown to exist, not computed. The few-valued populations of `s3_worstcase_by_kappa0.csv` give a lower bound on it, and the general search at $G = 15$, $n = 6$ found populations worse than any two- or three-point one, so an exact $c(n, G, \kappa_0, \alpha)$ would need a certified global search (claim K, not attempted).
- The boundary point $\kappa_0 = \kappa^\ast$ and, at $n \le 4$, the window between the two bounds of Proposition 3 are not settled.
- The worst case behind the frontier is a population whose clusters fall in two groups of nearly equal values. Real populations are rarely like that, so the frontier says what a max-share bound alone can guarantee, not how a given method behaves on a given population.
