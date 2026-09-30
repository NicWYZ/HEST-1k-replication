# Round 4, conformal track: the lower-bound scoping at $o = 0$

Stage C2, lead's parallel item (`docs/round4_conf_plan.md` section 4, C2). Started 30 September
2026 while the C1 setup job waited in the queue; the three-day cap runs to 3 October. Each step is
marked **derived**, **conjectured** or **failed**. The numbers are computed by
`code/scripts/round4_conf_c2_lower_bound.py` into
`results/round4/conformal/C2_candidates/lower_bound/c2_lb_beta_star.csv` and
`results/round4/conformal/C2_candidates/lower_bound/c2_lb_switch_probe.csv`.

Status at the time of writing. There is a statement with a proof sketch (Propositions 1 and 2,
section 3 and 4), which settles the case $K + 1 < 1/\alpha$. For $K + 1 \ge 1/\alpha$ the same
arguments give nothing, and a numerical probe (section 5) points the other way, toward valid
methods sharper than HCP. Under the stop rule the report states what the statement is and the
oversight chat decides whether it is pursued, so the scoping stops here rather than running to the
cap.

## 1. The question, written out

There are $K$ calibration groups and a test group. Group $j$ has a random score law $P_j$, and
$P_1, \dots, P_{K+1}$ are i.i.d. draws from a law $\Pi$ on score distributions. Group $k \le K$
contributes $N_k$ scores i.i.d. from $P_k$. The test score $S$ is one draw from $P_{K+1}$, and no
other test-group score is seen ($o = 0$). A method is a threshold $\hat q = \hat q(D, U)$ of the
calibration data $D$ and independent randomness $U$. It is *valid* at level $1 - \alpha$ if

$$P_\Pi(S \le \hat q) \ge 1 - \alpha \quad \text{for every } \Pi \text{ and every } (N_1, \dots, N_K).$$

This is hierarchical exchangeability in the form of GHCP's assumptions A1 to A3 with $o = 0$. HCP is
valid. The question is whether a valid method can be sharper than HCP by more than a vanishing
amount, and if not, in what sense HCP is optimal.

## 2. The permutation form of validity (derived, standard)

If $\Pi$ is the uniform law on a large finite set of distinct score laws, i.i.d. draws from it are
distinct with probability tending to one, so validity for every $\Pi$ implies validity when the
$K + 1$ laws are a fixed configuration $\{F_1, \dots, F_{K+1}\}$ and the test group is a uniformly
random one of them:

$$\frac{1}{K+1} \sum_{j=1}^{K+1} E\left[F_j\bigl(\hat q(D_{-j})\bigr)\right] \ge 1 - \alpha,$$

where $D_{-j}$ is data from the other $K$ laws. This is the device Barber, Candès, Ramdas and
Tibshirani use for their conditional-coverage limits, lifted from points to laws. Sections 4 and 5
use it; section 3 does not need it.

## 3. Proposition 1, a floor on coverage for $K + 1 < 1/\alpha$ (derived)

**Statement.** Let $\hat q$ be valid, and let $\Pi_0$ be any model under which $\hat q$ is finite
almost surely. Then the coverage of $\hat q$ under $\Pi_0$ is at least $1 - \beta^\star(K, \alpha)$, with

$$\beta^\star(K, \alpha) = \begin{cases} \alpha, & (K+1)\alpha \ge 1, \\[2pt] \max\left\{0,\; 1 - \dfrac{K}{K+1}\bigl(\alpha (K+1)\bigr)^{-1/K}\right\}, & (K+1)\alpha < 1. \end{cases}$$

**Proof sketch.** Contaminate. For $\varepsilon \in (0, 1)$ and $M > 0$ let
$\Pi_{\varepsilon, M} = (1 - \varepsilon)\Pi_0 + \varepsilon\, \delta_{Q_M}$ with $Q_M$ a law on $[M, \infty)$.

1. Let $A$ be the event that no calibration group drew $Q_M$. Then $P(A) = (1 - \varepsilon)^K$, and
   given $A$ the calibration data have their law under $\Pi_0$, independently of the test group.
2. On $A^c$ bound coverage by one. On $A$ the test group is from $\Pi_0$ with probability
   $1 - \varepsilon$, covered with probability $c_0$, its coverage under $\Pi_0$, and is from $Q_M$
   with probability $\varepsilon$, covered only if $\hat q \ge M$.
3. So $1 - \alpha \le 1 - (1-\varepsilon)^K + (1-\varepsilon)^K\bigl[(1-\varepsilon) c_0 + \varepsilon P_{\Pi_0}(\hat q \ge M)\bigr]$.
   Let $M \to \infty$; since $\hat q < \infty$ almost surely under $\Pi_0$, the last probability goes
   to zero.
4. With $c_0 = 1 - \beta$ this is $h_\beta(\varepsilon) := (1-\varepsilon)^K\bigl[\varepsilon(1 - \beta) + \beta\bigr] \le \alpha$ for every $\varepsilon$.
5. $h_\beta'(\varepsilon) = (1 - \varepsilon)^{K-1}\bigl[(1 - \beta) - K\beta - \varepsilon(1-\beta)(K+1)\bigr]$, which is zero at
   $\varepsilon_0 = \dfrac{1 - \beta(K+1)}{(1-\beta)(K+1)}$. If $\beta(K+1) \ge 1$ the maximum is at
   $\varepsilon = 0$ and equals $\beta$, so the constraint is $\beta \le \alpha$ and nothing is forced.
6. Otherwise $1 - \varepsilon_0 = \dfrac{K}{(1-\beta)(K+1)}$ and $\varepsilon_0(1-\beta) + \beta = \dfrac{1}{K+1}$, so the maximum is
   $\dfrac{1}{K+1}\left(\dfrac{K}{(1-\beta)(K+1)}\right)^K$. Setting it equal to $\alpha$ gives the second line of the
   statement. Since $\beta \le \alpha$, step 5's case $\beta(K+1) \ge 1$ can only arise when
   $\alpha(K+1) \ge 1$, which gives the first line.

**What it says.** The floor binds exactly when $K + 1 < 1/\alpha$, the condition under which HCP is
infinite. At $\alpha = 0.1$ a valid method that is finite under $\Pi_0$ must cover at least 0.923 at
$K = 5$, 0.951 at $K = 4$, and 1 at $K \le 3$; the floor falls to 0.900673 at $K = 8$ and is
nominal from $K = 9$. At $\alpha = 0.2$ it binds only for $K \le 3$ (0.808 at $K = 3$). Source:
`results/round4/conformal/C2_candidates/lower_bound/c2_lb_beta_star.csv`.

## 4. Proposition 2, the forced probability of an infinite interval (derived, one step sketched)

**Statement.** If $K + 1 < 1/\alpha$, then for every valid method there is a model under which
$P(\hat q = \infty) \ge 1 - \alpha(K+1)$. The bound is attained: the randomised HCP that returns
$+\infty$ with probability $1 - \alpha(K+1)$ and otherwise HCP's feasible-level threshold (the
$K/(K+1)$ quantile of the HCP measure, which is finite) is valid.

**Proof sketch.**

1. Take the degenerate models, in which every group's law is a point mass $\delta_{X_j}$ with
   $X_j$ i.i.d. from a continuous law $G$. The data are then $K$ i.i.d. values and the problem is
   ordinary prediction of $X_{K+1}$.
2. The rank of $X_{K+1}$ among the $K + 1$ values is uniform, so $X_{K+1}$ exceeds every calibration
   value with probability $1/(K+1)$.
3. *(Sketched, not written out.)* The class of continuous $G$ is closed under increasing bijections,
   so for any finite-valued rule and any $\eta > 0$ there is a $G$ under which a new value that exceeds
   all calibration values also exceeds $\hat q$ with probability at least $1 - \eta$. This is the
   standard equivariance argument; the construction chooses the bijection to grow fast enough above
   each order statistic.
4. Then coverage is at most $P(\hat q = \infty) + \bigl(1 - P(\hat q = \infty)\bigr)\dfrac{K}{K+1} + \eta$. Validity
   requires this to be at least $1 - \alpha$, and letting $\eta \to 0$ gives
   $P(\hat q = \infty) \ge (K+1)(1-\alpha) - K = 1 - \alpha(K+1)$.
5. Attainment. HCP at level $1 - 1/(K+1)$ is valid at that level, and mixing it with $+\infty$ at
   probability $\pi$ gives coverage at least $\pi + (1 - \pi)K/(K+1)$, which equals $1 - \alpha$ at
   $\pi = 1 - \alpha(K+1)$.

**What it says.** For $K + 1 < 1/\alpha$ the infinite interval HCP returns is not forced with
probability one; at $\alpha = 0.1$ the forced probability is 0.4 at $K = 5$ and 0.1 at $K = 8$. It is
forced with positive probability, so every valid method has infinite expected width there, and a
comparison of widths is only meaningful through the fraction of finite intervals and their median.
Together with Proposition 1, a finite outcome must over-cover. Randomised HCP is the method that
meets step 4 with equality; whether it also meets Proposition 1's floor with equality was not
checked.

## 5. $K + 1 \ge 1/\alpha$: HCP looks improvable (conjectured, partial argument)

Neither argument forces anything here, since $\beta^\star = \alpha$. To see whether HCP is optimal
anyway, I probed a rule that uses the within-group information HCP discards.

**The rule.** Let the laws be revealed exactly ($N_k \to \infty$). If the $K$ observed laws are
within distance $d$ of one another, use the pooled quantile of their mixture at level
$1 - \alpha + \delta$; otherwise use HCP.

**Partial argument (derived for two of three cases).** Use the permutation form of section 2, with
Kolmogorov distance between laws. Let $J_h$ be the set of $j$ for which $D_{-j}$ passes the check.

1. $|J_h| = 0$. The rule is HCP everywhere, which is permutation-valid.
2. $|J_h| \ge 2$. For $j, l \in J_h$ every law other than $j$ is within $d$ of every other, and the same
   for $l$. With $K + 1 \ge 3$ laws there is a third law within $d$ of both, so all $K + 1$ laws are
   within $2d$ of one another. A pooled term then covers at least $1 - \alpha + \delta - 2d$, and an
   HCP term covers at least $(1-\alpha)(K+1)/K - 2d$. With $\delta = 2d$ the configuration is covered
   at level $1 - \alpha$.
3. $|J_h| = 1$ (**open**). One law $F_{j_0}$ sits apart and is the test group in the one pooled term.
   Bounding that term by zero and each HCP term by its worst case gives coverage at least
   $\dfrac{K}{K+1}\left[\dfrac{(K+1)(1-\alpha) - 1}{K-1} - d\right]$, which falls short of $1 - \alpha$ by
   $\dfrac{K - (K+1)(1-\alpha)}{(K+1)(K-1)} + O(d)$ when $K + 1 > 1/\alpha$, for example by about 0.001 at $K = 10$
   with $d = 0$. The two bounds used cannot bind at once (a law far enough out that the pooled term
   misses it pushes every HCP threshold into its range), but that step was not proved.

**Numerical probe.** Normal within-group laws, revealed exactly, with one-sided scores. The
configuration families are $m \in \{1, 2, 3, 5\}$ groups shifted by $g$, $K+1$ locations evenly
spread on $[0, g]$, and two halves at $0$ and $g$, for 61 values of $g$ in $[0, 3]$ (in within-group
standard deviations). The smallest $\delta$ that keeps the worst configuration at $1 - \alpha$ is
tiny. At $K = 10$ and $\alpha = 0.1$ it is 0.000391 for $d = 0.25$, 0.001526 for $d = 0.5$ and 0.006323
for $d = 1$, so the rule calibrates at level 0.906323 or less on data that look homogeneous, where
HCP calibrates at 0.99. At $K = 9$, the smallest $K$ at which HCP is finite, the $d = 1$ value is
0.007141. Source: `results/round4/conformal/C2_candidates/lower_bound/c2_lb_switch_probe.csv`.

**Conjecture.** For $K + 1 \ge 1/\alpha$, HCP is not optimal among valid methods. There are valid
methods whose coverage on models with no donor effect is $1 - \alpha + O(d)$, where $d$ is a
homogeneity tolerance, while HCP's is about $(1-\alpha)(K+1)/K$. The gain is confined to data whose
groups look alike, which is the opposite of the donor-shift regime the track cares about: on CCRCC
the between-donor share is large and such a rule would fall back to HCP.

What a proof would still need. (a) Case 3 above. (b) Finite $N_k$, where the distance check is itself
noisy; a DKW band of half-width $\epsilon_N$ around each group's empirical CDF would add $2\epsilon_N$ to $d$.
(c) Arbitrary shapes, which the Kolmogorov formulation already allows, but only the normal
location family was probed.

## 6. Steps that failed

1. **A minimax statement over all models.** I tried to show that HCP minimises the worst-case price
   $\sup_\Pi E[\hat q]/q^\star(\Pi)$ by reducing to the degenerate family, where HCP is ordinary conformal
   on the $K$ group values. The reduction does not go through, because the ratio is not bounded on
   the degenerate family for heavy-tailed $G$ (it is infinite for every valid method), so the
   supremum does not separate methods. **Failed.**
2. **Group-level full conformal as a sharper method.** Replacing the unknown test law by the point
   mass at the candidate score, $\nu(s) = \frac{1}{K+1}\bigl(\sum_k F_k + \delta_s\bigr)$, and keeping
   $s \le Q_{1-\alpha}(\nu(s))$, gives exactly HCP's set: for $s$ below HCP's threshold the jump at $s$
   is not needed, and for $s$ above it the level is reached before $s$. **Derived, and it rules this
   route out.** It is also a second reading of why HCP is the natural construction.
3. **The single-contamination argument at $K + 1 \ge 1/\alpha$.** Proposition 1's family forces
   nothing there (step 5 of its proof). A family with several distinct far laws gives the same bound,
   because returning $+\infty$ whenever a far law is seen costs nothing in coverage. **Failed** as a
   route to a lower bound in that regime.

## 7. What this means for the track

For $K + 1 < 1/\alpha$ the price of validity is characterised. Every valid method has infinite
expected width, the forced probability of an infinite interval is $1 - \alpha(K+1)$ and is attained
by randomised HCP, and a finite interval must over-cover to at least $1 - \beta^\star(K, \alpha)$. For
$K + 1 \ge 1/\alpha$ the scoping found no lower bound and some evidence that none of the form sought
exists: HCP's conservatism at $K = 10$ is not forced, at least on data without a donor effect. I have
not established whether either proposition is new; neither appears in the papers the instruction
names, and I did not search further. The decision on whether to pursue section 5 as a method is the
oversight chat's.
