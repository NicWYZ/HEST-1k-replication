# Round 4, conformal track: the lower-bound scoping at $o = 0$

Stage C2, lead's parallel item (`docs/round4_conf_plan.md` section 4, C2). Started 30 September
2026 while the C1 setup job waited in the queue; the three-day cap runs to 3 October. Each step is
marked **derived**, **conjectured** or **failed**. The numbers are computed by
`code/scripts/round4_conf_c2_lower_bound.py` into
`results/round4/conformal/C2_candidates/lower_bound/c2_lb_beta_star.csv`,
`results/round4/conformal/C2_candidates/lower_bound/c2_lb_switch_probe.csv` and
`results/round4/conformal/C2_candidates/lower_bound/c2_lb_case3.csv`.

Status at the time of writing. There is a statement with a proof sketch (Propositions 1 and 2,
section 3 and 4), which settles the case $K + 1 < 1/\alpha$. For $K + 1 \ge 1/\alpha$ the same
arguments give nothing. Section 5 and its completion in section 8.3 show that valid methods
narrower than HCP on data without a donor effect exist in the revealed-law limit, and none of them
dominates HCP. Under the stop rule the report states what the statement is and the
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
3. *(Written in full in section 8.1.)* The class of continuous $G$ is closed under increasing bijections,
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

## 5. $K + 1 \ge 1/\alpha$: HCP looks improvable (conjectured, partial argument; see section 8.3, where the rule as stated fails case 3 and a repaired rule is derived)

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

## 8. Addendum 1 items, 30 September (the remaining cap)

Addendum 1 (plan section 10 item 3) asks for four items in order, each marked, stopping at the cap
on 3 October. All four were reached on 30 September. The case-3 counterexample, the repaired
levels and the DKW widths below are computed into
`results/round4/conformal/C2_candidates/lower_bound/c2_lb_case3.csv`.

### 8.1 Proposition 2, step 3 in full (derived)

**Claim.** Let $\hat q = \hat q(X_1, \dots, X_K, U)$ be finite-valued, with $U$ independent auxiliary
randomness. For every $\eta \in (0, 1)$ there is a continuous law $G$ with
$P\bigl(X_{K+1} > \hat q \mid X_{K+1} > \max_{k \le K} X_k\bigr) \ge 1 - \eta$ when $X_1, \dots, X_{K+1}$ are i.i.d. $G$.

**Construction.** Write $X_j = \varphi(V_j)$ with $V_j$ i.i.d. uniform on $(0,1)$ and $\varphi$ increasing and
continuous, so that $G$ is the law of $\varphi(V)$. Choose $r \in (0, 1)$ with $r(1+r)/2 \ge 1 - \eta/2$, and cut
$(0, 1)$ into blocks $I_n = [1 - r^n, 1 - r^{n+1})$ for $n \ge 0$, with midpoints $m_n$. Let
$V^\star = \max_{k \le K} V_k$.

1. Define $\varphi$ block by block. On $I_0$ let $\varphi$ be any increasing continuous map.
2. Suppose $\varphi$ is defined on $I_0 \cup \dots \cup I_n$. On the event $\{V^\star \in I_n\}$ every calibration value
   is $\varphi$ of a point in $I_0 \cup \dots \cup I_n$, so the law of $\hat q$ on that event is now fixed. Let $M_n$ be
   its $(1 - \eta/2)$ quantile, finite because $\hat q$ is finite-valued.
3. On the lower half of $I_{n+1}$ let $\varphi$ rise linearly from its value at the end of $I_n$ to
   $\max\{M_n, \varphi(1 - r^{n+1}-)\} + 1$ at $m_{n+1}$, and on the upper half rise linearly by one more unit.
   Then $\varphi$ is increasing and continuous, $\varphi(v) > M_n$ for $v \ge m_{n+1}$, and $\varphi(v) \to \infty$ as
   $v \to 1$. Step 2 for block $n+1$ uses $\varphi$ on $I_{n+1}$, which is now defined, so the recursion is
   well founded.
4. Given $V^\star = v \in I_n$, the interval $(v, 1)$ has length at most $r^n$ and its part beyond $m_{n+1}$ has
   length $r^{n+1}(1 + r)/2$, so $P(V_{K+1} \ge m_{n+1} \mid V_{K+1} > V^\star, V^\star \in I_n) \ge r(1+r)/2 \ge 1 - \eta/2$.
5. On $\{V^\star \in I_n,\ V_{K+1} \ge m_{n+1}\}$ we have $X_{K+1} > M_n$, and $V_{K+1}$ is independent of
   $(V_1, \dots, V_K, U)$, so $P(\hat q \ge X_{K+1} \mid \text{that event}) \le P(\hat q \ge M_n \mid V^\star \in I_n)$. Taking $M_n$
   as the smallest value with $P(\hat q \ge M_n \mid V^\star \in I_n) \le \eta/2$ (it exists since $\hat q$ is finite), this is
   at most $\eta/2$.
6. Summing over $n$, $P(X_{K+1} \le \hat q \mid X_{K+1} > \max_k X_k) \le \eta/2 + \eta/2 = \eta$.

This completes step 3 of Proposition 2. The degenerate hierarchical model with group values
$X_j \sim G$ is a legitimate model (point-mass group laws), so Proposition 2 holds as stated.

### 8.2 Does randomised HCP attain Proposition 1's floor? (derived that the question does not apply; the general form is attained)

Proposition 1 concerns methods that are finite almost surely under $\Pi_0$. Randomised HCP is
infinite with probability $\pi = 1 - \alpha(K+1) > 0$ under every model, so the floor does not apply
to it. Keeping the infinite probability in step 3 of Proposition 1's proof gives the general
constraint $(1-\varepsilon)^K\bigl[(1-\pi_\infty)\varepsilon + (1-\varepsilon)\beta\bigr] \le \alpha$ for all $\varepsilon$. In the degenerate model
randomised HCP has $\pi_\infty = 1 - \alpha(K+1)$ and miscoverage $\beta = \alpha(K+1)\cdot\frac{1}{K+1} = \alpha$, so the left side is
$\alpha(1-\varepsilon)^K(1 + K\varepsilon)$, whose derivative is $-\alpha K(K+1)\varepsilon(1-\varepsilon)^{K-1} \le 0$. The maximum is $\alpha$ at
$\varepsilon = 0$, so randomised HCP meets the general constraint with equality. Whether some valid method
that is finite almost surely under a given $\Pi_0$ attains $1 - \beta^\star$ was **not settled** (a candidate
would return $+\infty$ whenever the data do not look like $\Pi_0$, which cannot be decided exactly).

### 8.3 Case 3 of section 5 (derived: the rule as stated is not valid; a repaired rule is)

**Counterexample.** $K = 10$, $\alpha = 0.1$, $\delta = 0$, $d$ any value at which ten identical laws pass the
check. Ten groups have law $N(0, 1)$ and one group $j_0$ is a point mass at $a$ just above the pooled
threshold $q_p = \Phi^{-1}(0.9) = 1.2816$. The ten normal groups pass the check, so when $j_0$ is the test
group the pooled term covers it with probability $0$. When $j_0$ is in calibration the check fails
(Kolmogorov distance from a point mass to a normal law exceeds $d$), HCP's threshold lies above $a$,
and each normal test group is covered with probability $8.9/9 = 0.98889$. Coverage is
$10 \times 0.98889 / 11 = 0.89899 < 0.9$. This equals the worst-case bound of section 5, so that bound is
attained. The section 5 probe missed it because it used only normal location shifts.

**Repair (derived).** Run the HCP branch at a stricter level $1 - \alpha'$ with
$$1 - \alpha' = \frac{(K-1)\bigl[(1-\alpha)(K+1)/K + d\bigr] + 1}{K+1},$$
and the pooled branch at $1 - \alpha + 2d$. Case 1 is HCP at level $1 - \alpha' \ge 1 - \alpha$. Case 2 is as
before. In case 3 the pooled term is at least $0$ and each HCP term at least
$\bigl((K+1)(1-\alpha') - 1\bigr)/(K-1) - d$, and the choice of $\alpha'$ makes the total $1 - \alpha$. So, with laws
revealed exactly, the repaired rule is valid for every configuration, hence for every model. At
$K = 10$, $\alpha = 0.1$ the HCP branch runs at 0.900909 for $d = 0$ and 0.941818 for $d = 0.05$, against
HCP's 0.9. The repaired rule is narrower than HCP on data whose groups look alike and wider than HCP
otherwise, so **it does not dominate HCP**.

### 8.4 The finite-$N_k$ version (derived, with a coverage loss that the addendum's DKW level does not cover)

With finite $N_k$ the check uses empirical CDFs. Let $E$ be the event that every calibration group's
empirical CDF is within $\epsilon_{N_k} = \sqrt{\log(2/\gamma)/(2N_k)}$ of its law (DKW at level $\gamma$ per group), so
$P(E^c) \le K\gamma$. On $E$, observed spread at most $d$ implies true spread at most $d + 2\epsilon$, so cases
1 to 3 hold with $d$ replaced by $d + 2\epsilon$. Off $E$ the rule's coverage is bounded below by zero. The
repaired rule therefore covers at least $1 - \alpha - K\gamma$. At the addendum's $\gamma = 0.01$ that is a
possible loss of $0.1$ at $K = 10$, so exact validity needs $\gamma$ of order $\alpha/K$ or smaller, charged to
the level. The widening is also large: $2\epsilon_N$ is 0.3256, 0.1456 and 0.0728 in Kolmogorov distance
at $N_k = 100, 500, 2000$ and $\gamma = 0.01$, and the repaired HCP branch at $d = 0.05$ is already at 0.94.

### 8.5 Consequence for candidate K6

K6 as addendum 1 specifies it is the unrepaired rule with $d$ widened by the DKW band and $\delta$
from the probe. Section 8.3 shows the unrepaired rule is not valid even with laws revealed exactly,
and section 8.4 shows the DKW event adds a possible loss of $K\gamma$. K6's part (c) is therefore unmet,
as the addendum anticipated. The repaired rule of section 8.3 with $\gamma$ charged to the level is a
proposal for the oversight chat, not run.
