# Round 9, track fewcluster. The supplied papers, and a side result on the median

27 October 2026. Written by the fewcluster session after the position note (`round09_fewcluster_position.md`). It records two things. The first is what the four papers Nicolas supplied in `refs/` contain, read in full by a fresh checker (NOV9). The second is a side result that came out of comparing Theorem 1 with Lanke (1974). It proves, in its natural reading, the conjecture stated in Paul and Kuchibhotla (arXiv:2403.06357, Remark 1), checked by a second fresh agent. Neither changes the position note's proposal for D1.

## 1. The four supplied papers (NOV9)

The checker read Lanke (1974), Gleser and Hwang (1987), Basu and DasGupta (1995) and Bakirov and Székely (2006) in full. Its record is `results/round9/fewcluster/novelty/novelty_NOV9_structured.json`. Its verdicts are these.

1. None of the four contains the fixed-coefficient frontier (A) or the tuned-coefficient frontier (B). None treats a finite population, sampling without replacement, the residual max-share, $\pi(k)$ or $k^\ast$, the possibility half, or a coefficient fitted on the sample.
2. Lanke's Theorem 2 states the number $n < 1 + \log_2(1/\alpha)$ for iid samples from continuous laws symmetric about $\theta$, over all locally bounded procedures, as NOV8 reported. The printed proof establishes only the one-sided bound $2^{-n}$, and the step to $2^{1-n}$ is not displayed. This matches Paul and Kuchibhotla's remark that Lanke's claim fails without shift invariance.
3. Bakirov and Székely's extremal case is $k$ equal nonzero scales in a Gaussian scale-mixture model. It has no threshold in $n$ and $\alpha$ and is model-based, not a finite population.
4. Basu and DasGupta's two-point contaminations show the spike phenomenon for the $t$ statistic, the $k = 1$ analogue of our spike population, with a threshold that does not depend on $n$ or $\alpha$. Gleser and Hwang give the qualitative unboundedness argument only.

The checker read Bakirov and Székely and Lanke from the PDF text layer and the two scans as page images. It saved nothing from the papers. With NOV9, all sources the position note listed as unread have been read, and the novelty status of A and B in the position note stands.

## 2. The Paul and Kuchibhotla conjecture

**Their setting.** Let $X_1, \dots, X_n$ be iid with a continuous distribution. A confidence interval is a pair of real functions $g_L \le g_R$ on $\mathbb{R}^n$. It is locally bounded if both are bounded on bounded sets. It is shift-invariant if, for every $c \in \mathbb{R}$,

$$
g(x + c\mathbf{1}) = g(x) + c .
$$

Paul and Kuchibhotla build a shift-invariant interval from order statistics that is valid for the median whenever $n \ge \log_2(2/\alpha)$. They show that Lanke's Theorem 2 fails for $\log_2(1/\alpha) \le n < \log_2(2/\alpha)$ when shift invariance is not required. They conjecture that no shift-invariant, locally bounded interval for the median exists when $n < \log_2(2/\alpha)$. The paper does not define the two terms formally, and the reading above is the natural one. Version 2 (July 2026) still states it as a conjecture.

**Result.** Under that reading the conjecture holds. Let $\mathcal{P}$ be the continuous distributions that are symmetric about $\theta$ and have unique median $\theta$. If $(g_L, g_R)$ is shift-invariant and locally bounded, then

$$
\sup_{P \in \mathcal{P}} P\big(\theta \notin [g_L(X), g_R(X)]\big) \ge 2^{1-n} .
$$

So coverage $1 - \alpha$ over $\mathcal{P}$ requires $\alpha \ge 2^{1-n}$, which is $n \ge \log_2(2/\alpha)$. The bound is sharp, because their order-statistic interval attains it. It holds for open and closed intervals, and over any class of laws containing $\mathcal{P}$, such as all laws with a common median.

**Proof.** Let $K = [-1, 1]^n$ and

$$
M = \max\Big\{ \sup_{K} |g_L| ,\ \sup_{K} |g_R| \Big\} < \infty ,
$$

which is finite by local boundedness. Fix $D > M + 1$, a weight $\eta \in (0, 1)$ and a width $w \in (0, 1)$. Let $P_{\eta, D}$ put mass $(1 - \eta)/2$ uniformly on $A = [-1, 1]$, mass $(1 - \eta)/2$ uniformly on $B = [2D - 1, 2D + 1]$, and mass $\eta$ uniformly on $C = [D - w, D + w]$. It is continuous and symmetric about $D$. Its distribution function is strictly increasing on $C$ with $F(D) = 1/2$, so its median $\theta = D$ is unique.

On the event that every observation falls in $A$, we have $X \in K$, so

$$
g_R(X) \le M < D = \theta ,
$$

and the interval misses $\theta$.

On the event that every observation falls in $B$, write $X = Y + 2D\mathbf{1}$ with $Y \in K$. Shift invariance gives

$$
g_L(X) = g_L(Y) + 2D \ge 2D - M > D = \theta ,
$$

and the interval misses $\theta$ again. The two events are disjoint, each with probability $\{(1 - \eta)/2\}^n$, so

$$
P_{\eta, D}\big(\theta \notin [g_L(X), g_R(X)]\big) \ge 2 \left(\frac{1 - \eta}{2}\right)^n = 2^{1-n} (1 - \eta)^n .
$$

Letting $\eta \to 0$ gives the bound. $\square$

**Why Lanke's argument gave only $2^{-n}$, and where the factor 2 comes from.** Lanke's population is $P_{0, D}$, two clusters with no central mass. Local boundedness controls the procedure only near the origin, so only the event "all in $A$" is forced to miss. Shift invariance carries the control at $K$ over to $K + 2D\mathbf{1}$, which forces the second miss. The central mass $\eta$ makes the median unique. A two-cluster version with unequal masses $1/2 \pm \epsilon$ does not work, because then the median lies inside the heavier cluster and only one event is forced to miss. The first fresh agent found this gap in the session's own sketch.

**Relation to Theorem 1.** The construction is the two-block population of Theorem 1, the one constant on $k$ clusters and on the other $G - k$, at $k = G/2$, with the target placed between the blocks. As $G \to \infty$ with $n$ fixed,

$$
\pi(G/2) = \frac{2\binom{G/2}{n}}{\binom{G}{n}} \to 2^{1-n} ,
$$

which is where the iid threshold appears as the limit of the finite-population one. For the mean, in the finite population, the target falls between the blocks without any perturbation. For the median it takes the central mass.

**Checks.**

1. A fresh agent that had not seen the work checked the session's sketch against the paper's exact text (`results/round9/fewcluster/median_conjecture/verify_conjecture_report.md`, structured record `verify_conjecture_structured.json`). It found the gap and supplied the three-cluster repair above. The session then checked the repair line by line.
2. Monte Carlo with $4 \times 10^5$ replicates at $D = 10^4$ and $\eta = 10^{-3}$ (`verify_conjecture.py`). For $n = 3, 4, 5$, the smallest miss over all order-statistic intervals and over mean $\pm c \cdot$ range for $c \in \{0.5, 1, 2, 5\}$ was 0.2488, 0.1245 and 0.0622. The bound $2\{(1 - \eta)/2\}^n$ is 0.2493, 0.1245 and 0.0622, so the two agree to Monte Carlo error. The paper's interval that is not shift-invariant ($n = 3$, $\alpha = 0.2$) missed 0.124 and 0.126 at $\eta = 0.001$ and $0.2$, below $\alpha$, as their counterexample to Lanke says it should, while every shift-invariant candidate missed at least 0.249.

**Not checked.** Randomised intervals were not considered. The bound is on outer probability when $g_L$ or $g_R$ is not measurable. The result is for the reading of "shift-invariant" given above, since the paper does not define it.

**Novelty status: not found in print, provisional.**

1. The fresh agent searched arXiv and the web with about five queries and screened Semantic Scholar forward citations, which returned two unrelated works.
2. The session then searched OpenAlex (`results/round9/fewcluster/median_conjecture/openalex_conjecture_queries.csv`, 7 queries). OpenAlex records no works citing arXiv:2403.06357. The seven works citing the HulC paper (Kuchibhotla, Balakrishnan and Wasserman) do not address the conjecture. Searches on the conjecture's wording found nothing that proves or refutes it.

Coverage is thin, because indexes of a 2024 preprint's citations are sparse. The argument is short and uses Lanke's own population, so it may exist in an unindexed source or in correspondence. It should be presented as a remark, not as a headline result.

## 3. What this means for the paper

The side result does not change the proposal for D1. It gives the theory section one more link to the literature. The finite-population frontier contains, as its large-$G$ limit, the sharp iid threshold for shift-invariant intervals, and the same two-block construction settles a question left open in the HulC line of work. Whether to mention it in the paper, and whether to write to Paul and Kuchibhotla, are Nicolas's decisions (section 5 of CLAUDE.md, item 7).
