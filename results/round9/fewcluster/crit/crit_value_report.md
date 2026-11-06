# crit_value_report.md — critical value c(κ0) for the fixed-coefficient finite-population interval

All code is in the attached scripts (core.py, moments.py, majorant.py, block.py, strat.py, search_grouped.py, run_search_grouped.py, refine.py, verify_all.py).
`python crit/verify_all.py` re-runs every brute-force check quoted below. No literature was consulted (as instructed).
Labels: **[P]** proved here; **[N]** numerical; **[E]** exact enumeration / exact rational arithmetic.

## 0. Setting and reduction (checked)

x = e − ē, A_S = Σ_S x, Q_S = Σ_S x², t_S = A_S²/(n Q_S) ∈ [0,1] (t_S := 0 if x_S ≡ 0).
**[P+E] Reduction.** S is missed ⇔ A_S² > ρ n Q_S, ρ = g/(1+g), g = c²(1−f)/(n−1) ⇔ t_S > ρ. This also covers s_S = 0: x constant ≠ 0 gives t_S = 1 > ρ (a miss); x_S ≡ 0 is covered. Verified by comparing the raw interval test with t_S > ρ on all samples of random heavy-tailed populations, (G,n) = (10,3),(12,4),(14,5), c ∈ {1,2,3.5,8}: 0 discrepancies. Equivalent form: s'_S < η|x̄_S|, η² = (n−1)/(c²(1−f)).
**[P] Monotonicity.** The miss set shrinks as c grows, so P_e(miss; c) is non-increasing in c. K(κ0) grows with κ0, so c(κ0) is non-decreasing in κ0. c_pop(e) := min{c : P_e(miss) ≤ α} is the upper-α quantile of t_S mapped through ρ ↦ c. **c_L(κ0) = max over any set of e ∈ K(κ0) of c_pop(e) is a valid lower bound on c(κ0)**: if c < c_pop(e), the population e has coverage < 1−α.
**[P] Non-emptiness.** κ(e) ≥ 1/G always (max x² ≥ mean x²), with equality iff all |x| are equal. So K(κ0) = ∅ for κ0 < 1/G. 0.25·frontier is empty for (24,8) (0.0396 < 0.0417) and (51,8) (0.0178 < 0.0196); I report 0.4·frontier for those two.
Frontiers: (24,8): k*=6, κ2(5)=0.15833; (24,12): k*=4, 0.29167; (51,8): k*=12, 0.07130; (51,16): k*=6, 0.18039.

## 1. Proved results

**Lemma 1 (generalized; checked).** If m values of x lie in [a, Ra], a>0, R≥1 (same sign), and k = G−m ≥ 1, then κ ≥ m/(k(m + R²k)).
*Proof.* Let Σ be the sum of the m values (Σ ≥ ma). The other k values sum to −Σ, so B := max|x| ≥ Σ/k ≥ ma/k. T = Σx² ≤ mR²a² + kB². Hence κ = B²/T ≥ B²/(mR²a² + kB²), which is increasing in B², so it is ≥ its value at B = ma/k, namely m/(k(m+R²k)). ∎ (R=1 gives (G−k)/(kG) = κ2(k).) Checked on 3000 random populations (every window of consecutive positive values): 0 violations. Consequence: M(R,κ0) := max{m ≤ G−1 : m/((G−m)(m+R²(G−m))) ≤ κ0} bounds the size of any same-sign set with max/min ≤ R.

**Lemma 2 (tight band; checked).** If δ := (n−1)/(c√(1−f)) < 1, every missed sample has all x_i ≠ 0 of one sign with max|x|/min|x| < r = (1+δ)/(1−δ).
*Proof.* |x_i − x̄_S| ≤ √(n−1) s'_S < √(n−1) η |x̄_S| = δ|x̄_S|. ∎
This confines the method to c > (n−1)/√(1−f): 8.6 for (24,8), 15.6 for (24,12), 7.6 for (51,8), 18.1 for (51,16). It is the reason the block certificate is large.

**Theorem B (block-counting certificate; [P], integer dynamic programme; 4000 (population,c,s) checks, 0 violations).** Fix s ∈ {1,2}, b = r^(1/s). Cut each sign axis into blocks [θb^t, θb^(t+1)). A tight n-subset whose minimum lies in block t lies in blocks t..t+s, a set of ratio < b^(s+1) = r^((s+1)/s). By Lemma 1 every window of s+1 consecutive blocks holds ≤ M := M(r^((s+1)/s), κ0) values. The number of missed samples is ≤ Σ_sides Σ_t [C(S_t,n) − C(S_t − m_t,n)], S_t = m_t+…+m_(t+s). Maximise over block sizes with window sums ≤ M and Σ_sides Σ_t m_t ≤ G (dynamic programme, F*(P)). Then P(miss) ≤ max_(P+ + P− ≤ G)[F*(P+)+F*(P−)]/C(G,n), and any c making this ≤ α is certified. The bound is monotone in c.
*Limitation:* the DP only constrains windows of ≤ s+1 blocks, so as c→∞ it tends to a limit strictly above π(k_min) (for (24,8) at 0.9 frontier: 0.117 vs π(6)=0.0595). That is why it gives nothing (up to c = 400·(n−1)/√(1−f)) at the larger κ0 fractions.

**Theorem Q (quadratic-majorant certificate; [P+E]).** Normalise Σx = 0, Σx² = 1 (the miss event is scale-free). Put u = A_S², q = Q_S; always q ≥ u/n, and a miss means u>0, q < u/(ρn). For a1 ≥ 0 with a1 + a2/n ≥ 0 and a1 + a2/(ρn) ≥ 0, L = 1 + a1u + a2q ≥ 1 on the miss wedge (L−1 is linear and non-negative on both bounding rays). So 1[miss] ≤ L² and **P(miss) ≤ E L²**.
The SRSWOR moments E A², E Q, E A⁴, E A²Q, E Q² are expanded exactly over set partitions (moments.py; 11 monomials verified against full enumeration for (G,n) ∈ {(7,3),(8,4),(9,3)}). With p1 = 0, p2 = 1 they involve only p4 (no p3), linearly, so E L² = c0(a1,a2) + c1(a1,a2)·p4. Since 1/G ≤ p4 ≤ max x²·Σx² ≤ κ0 (Cauchy–Schwarz and the class constraint), sup_K P(miss) ≤ max(E L²|_{p4=1/G}, E L²|_{p4=κ0}).
(a1,a2) is optimised numerically; the chosen rational (a1,a2) and a rational c are then **re-evaluated in exact Fraction arithmetic**. All three certified cells re-checked exactly: 0.0999999, 0.0999461, 0.0999805 ≤ 0.1. The bound was also compared with the exact miss probability of 100 random populations × 3 values of c, each at its own κ: 0 violations. Slicing the class by p4 does not help (the worst slice is p4 = κ0).

**Remark (c→∞).** For two-point extremal populations the c→∞ miss probability is β = π(k_min(κ0)). Neither Theorem B's limit nor Theorem Q's plateau (column "plateau" in the table; 0.04–0.25 here) equals β, so I did not obtain a bound that is exact as c→∞.

## 2. Part 1 table (α = 0.10; normal 90% two-sided quantile 1.645 for scale)

c_L: best explicit population found by stochastic search over d-valued populations (d = 2..6; exact enumeration of every count vector, so exact coverage, not Monte Carlo). For G=24 it was re-checked by full enumeration over all C(24,n) samples (identical values). c_U: min of the two certificates. All c_U are valid; all c_L are lower bounds on the true c(κ0), but the search is stochastic, so a larger c_L may exist (c_L is "best found").

| G | n | κ0 / frontier | κ0 | Λ0 (SD units) | c_L (exact enum., explicit population) | c_U quad-majorant (exact-rational certificate) | c_U block-counting (integer DP) | c_U reported (min) |
|---|---|---|---|---|---|---|---|---|
| 24 | 8 | 0.25 | 0.0396 | 0.954 | class empty (κ0 < 1/G = 0.0417) | — | — | — |
| 24 | 8 | 0.4 | 0.0633 | 1.207 | 2.086 | 3.775 | 33.200 | 3.775 |
| 24 | 8 | 0.5 | 0.0792 | 1.349 | 2.449 | 7.405 | 43.500 | 7.405 |
| 24 | 8 | 0.75 | 0.1187 | 1.653 | 2.449 | none (plateau 0.161 > 0.1) | 269.4 | 269.4 |
| 24 | 8 | 0.9 | 0.1425 | 1.810 | 4.473 | none (plateau 0.197 > 0.1) | — | — |
| 24 | 12 | 0.25 | 0.0729 | 1.295 | 1.914 | 2.892 | 39.600 | 2.892 |
| 24 | 12 | 0.4 | 0.1167 | 1.638 | 2.098 | 4.580 | 50.200 | 4.580 |
| 24 | 12 | 0.5 | 0.1458 | 1.831 | 2.098 | none (plateau 0.109 > 0.1) | 58.100 | 58.100 |
| 24 | 12 | 0.75 | 0.2188 | 2.243 | 2.849 | none (plateau 0.170 > 0.1) | 96.700 | 96.700 |
| 24 | 12 | 0.9 | 0.2625 | 2.457 | 4.971 | none (plateau 0.203 > 0.1) | 196.1 | 196.1 |
| 51 | 8 | 0.25 | 0.0178 | 0.944 | class empty (κ0 < 1/G = 0.0196) | — | — | — |
| 51 | 8 | 0.4 | 0.0285 | 1.194 | 2.358 | 4.403 | 44.700 | 4.403 |
| 51 | 8 | 0.5 | 0.0357 | 1.335 | 2.372 | none (plateau 0.105 > 0.1) | 62.900 | 62.900 |
| 51 | 8 | 0.75 | 0.0535 | 1.635 | 2.990 | none (plateau 0.179 > 0.1) | — | — |
| 51 | 8 | 0.9 | 0.0642 | 1.791 | 4.415 | none (plateau 0.218 > 0.1) | — | — |
| 51 | 16 | 0.25 | 0.0451 | 1.502 | 1.981 | 3.234 | 44.200 | 3.234 |
| 51 | 16 | 0.4 | 0.0722 | 1.899 | 2.114 | none (plateau 0.112 > 0.1) | 61.600 | 61.600 |
| 51 | 16 | 0.5 | 0.0902 | 2.124 | 2.580 | none (plateau 0.144 > 0.1) | 84.900 | 84.900 |
| 51 | 16 | 0.75 | 0.1353 | 2.601 | 2.782 | none (plateau 0.214 > 0.1) | — | — |
| 51 | 16 | 0.9 | 0.1624 | 2.849 | 4.680 | none (plateau 0.251 > 0.1) | — | — |

"—" in the block column = no certificate for c ≤ 400·(n−1)/√(1−f). c_pop is an atom-valued quantile (e.g. 2.4495 = √6), so c_L jumps with κ0.

Worst populations found (x/SD with multiplicities; κ/κ0 = 1 means the cap binds):

| G | n | κ0/frontier | d | values x/SD | multiplicities | κ/κ0 |
|---|---|---|---|---|---|---|
| 24 | 8 | 0.40 | 3 | [-1.024, 1.207, -0.274] | [9, 9, 6] | 1.000 |
| 24 | 8 | 0.50 | 2 | [-1.264, 0.758] | [9, 15] | 0.877 |
| 24 | 8 | 0.75 | 2 | [1.264, -0.758] | [9, 15] | 0.585 |
| 24 | 8 | 0.90 | 3 | [-1.81, 1.15, 0.297] | [5, 4, 15] | 1.000 |
| 24 | 8 | 0.95 | 3 | [0.342, 0.901, -1.86] | [14, 5, 5] | 1.000 |
| 24 | 12 | 0.25 | 3 | [0.806, 1.198, -0.893] | [4, 7, 13] | 0.855 |
| 24 | 12 | 0.50 | 2 | [-0.692, 1.384] | [16, 8] | 0.571 |
| 24 | 12 | 0.75 | 3 | [-2.243, 0.151, 1.933] | [3, 19, 2] | 1.000 |
| 24 | 12 | 0.90 | 3 | [-0.216, 2.457, -1.162] | [18, 3, 3] | 1.000 |
| 24 | 12 | 0.95 | 3 | [-0.779, 2.524, -0.23] | [5, 3, 16] | 1.000 |
| 51 | 8 | 0.40 | 4 | [-1.17, -1.192, 1.115, 0.766] | [14, 7, 5, 25] | 0.997 |
| 51 | 8 | 0.50 | 4 | [-1.33, -1.206, 0.795, -1.23] | [4, 15, 31, 1] | 0.993 |
| 51 | 8 | 0.75 | 4 | [-1.635, 1.276, 0.229, 0.346] | [12, 10, 27, 2] | 1.000 |
| 51 | 8 | 0.90 | 4 | [0.254, 1.789, 0.869, -1.791] | [26, 1, 13, 11] | 1.000 |
| 51 | 8 | 0.95 | 4 | [0.8, 0.33, -1.84, 1.265] | [13, 26, 11, 1] | 1.000 |
| 51 | 16 | 0.25 | 4 | [-0.674, 1.333, -0.733, 1.469] | [1, 17, 32, 1] | 0.957 |
| 51 | 16 | 0.50 | 2 | [2.005, -0.489] | [10, 41] | 0.891 |
| 51 | 16 | 0.75 | 6 | [0.166, -2.601, -0.623, 2.208, 0.168, 0.169] | [29, 5, 1, 3, 7, 6] | 1.000 |
| 51 | 16 | 0.90 | 5 | [2.849, -0.889, -0.154, -1.492, -0.152] | [5, 8, 3, 1, 34] | 1.000 |
| 51 | 16 | 0.95 | 6 | [-0.289, 2.927, 2.927, -0.29, -1.303, 0.411] | [38, 4, 1, 5, 2, 1] | 1.000 |

## 3. Method for c_U and honest assessment
* Certified region: small κ0 (about ≤ 0.4–0.5 frontier) via Theorem Q, where c_U/c_L ≈ 1.5–2 (e.g. (24,12) at 0.25: 2.892 vs 1.914; (51,16): 3.234 vs 1.981; (24,8) at 0.4: 3.775 vs 2.086).
* Elsewhere only Theorem B is available and it is very loose (c_U 40–270 vs c_L 2–3). Lemma 2's √(n−1) deviation bound is sharp only for one-outlier samples and needs δ<1. For c in the relevant range 2–10 a missed sample need not be a one-signed tight band (half-and-half samples of two-point populations are missed at c<3). I could not produce a certified bound for 3 < c < 40 near the frontier. Moment (Cantelli-type) bounds lose a factor ≈3 in probability there: for the k=7 two-point population in (24,8), the best per-population quadratic or degree-2-in-(u,q) majorant has Eψ ≥ 0.10 at c=4, while the true miss probability is 0.033. Higher-degree majorants therefore would not close the gap; an argument that tracks the whole population, not one tight window, is needed.
* A Chernoff/Hoeffding-with-replacement bound with a moment-LP dual was tried and is useless here (bound > 0.66 at all c).

## 4. Exact global optimisation at small G (conjecture test)
(G,n) = (10,4), α=0.1, frontier 0.2333. General 10-variable differential evolution (6 seeds, exact enumeration of 210 samples) vs the d-valued search: κ0/frontier 0.6: 3.1667 vs 3.1667; 0.75: 3.1667 vs 3.1665; 0.9: 4.637 vs 4.607 (the DE optimum has 5 distinct values: −1.37×3, 0.08, 0.46×2, 0.58×3, 1.37). So the worst case is clustered with few distinct values, but the d-valued search under-shot by 0.7% in one cell; my c_L may be ≈1% low.
For G=24, local search with all 24 values free (full enumeration, 3 seeds, 900–2500 steps, only the cells where the tie-broken start stayed feasible) did not exceed the grouped populations. This is weak evidence.

## 5. Stratified / box class (second part)

D_h = W_h(ē_Sh − ē_h), V̂_h = W_h²(1−f_h)s_h²/m_h, miss ⇔ (ΣD_h)² > c²ΣV̂_h (SE=0 with D≠0 counted as a miss).
**Theorem S [P+E].** Same argument with u = (ΣD_h)², q = ΣV̂_h: L = 1 + a1u + a2q ≥ 1 on {u > c²q ≥ 0} iff a1 ≥ 0 and a2 + a1c² ≥ 0. With V := ΣV_h = 1 and independent strata,
E L² = 1 + 2(a1+a2) + 3a1² + 2a1a2 + a2² + Σ_h v_h²[a1²(r4(s_h)−3) + 2a1a2(rDV(s_h)−1) + a2²(rVV(s_h)−1)],
with v_h = V_h/V, s_h = p4_h/p2_h², and r4 = E D_h⁴/V_h², rDV = E[D_h²V̂_h]/V_h², rVV = E V̂_h²/V_h² exact linear functions of s_h (moments.py, SRSWOR inside the stratum). Class: s_h ∈ [1/N_h, Λ0²/(N_h−1)] and v_h ≤ v0, hence Σv_h² ≤ v0. So sup P(miss) ≤ min over feasible (a1,a2) of [base + v0·max(0, max_s K(s))]. The formula agrees to 1e-8 with full enumeration of a 3-stratum population (N=7, m=3); the bound is ≥ the exact miss probability on 120 random small designs.

| setting | c_L (two-point strata, MC/exact-checked) | worst design found | certified c (quad. majorant) |
|---|---|---|---|
| G=51, N_h=20000, m_h=5, Λ0=9, v0=0.025 | 2.843 | K=42 active strata, minority fraction 0.0183, P(all SE_h=0)=0.0208 | none (bound plateaus at 0.287 > 0.1) |
| G=51, N_h=20000, m_h=10, Λ0=9, v0=0.025 | 2.296 | K=43 active strata, minority fraction 0.0122, P(all SE_h=0)=0.0051 | none (bound plateaus at 0.167 > 0.1) |
| G=24, N_h=2000, m_h=10, Λ0=6, v0=0.1 | 2.607 | K=12 active strata, minority fraction 0.0300, P(all SE_h=0)=0.0256 | none (bound plateaus at 0.260 > 0.1) |
| G=24, N_h=2000, m_h=20, Λ0=6, v0=0.1 | 2.089 | K=12 active strata, minority fraction 0.0275, P(all SE_h=0)=0.0012 | none (bound plateaus at 0.148 > 0.1) |

**No certified c exists from this method at the four requested settings**: the bound plateaus (c→∞) above α. The obstruction is real, not an artefact. A two-point stratum with minority fraction p = 1/(1+Λ0²) has a constant sample with probability (1−p)^m (0.94 for m=5, Λ0=9). With K = 1/v0 = 40 active strata, P(SE=0) = 0.0858 (m=5, Λ0=9), within 14% of α, and the certificate would have to be accurate to that level on an atom, which variance-type inequalities cannot do. c_L is nevertheless finite, because the worst design uses more strata (K=42 gives P(SE=0)=0.021). Certified c does exist when v0·Λ0²/m is smaller:

| N_h | m_h | Lambda0 | v0 | certified_c | bound_at_c60 |
|---|---|---|---|---|---|
| 20000.0 | 5.0 | 9.0 | 0.025 | — | 0.287 |
| 20000.0 | 10.0 | 9.0 | 0.025 | — | 0.167 |
| 2000.0 | 10.0 | 6.0 | 0.1 | — | 0.2599 |
| 2000.0 | 20.0 | 6.0 | 0.1 | — | 0.1483 |
| 20000.0 | 5.0 | 9.0 | 0.005 | 3.029 | 0.1 |
| 20000.0 | 5.0 | 9.0 | 0.002 | 2.46 | 0.1 |
| 20000.0 | 10.0 | 9.0 | 0.01 | 3.021 | 0.1 |
| 20000.0 | 10.0 | 9.0 | 0.005 | 2.515 | 0.1 |
| 2000.0 | 10.0 | 6.0 | 0.02 | 2.849 | 0.1 |
| 2000.0 | 20.0 | 6.0 | 0.05 | 3.222 | 0.1 |
| 2000.0 | 20.0 | 6.0 | 0.02 | 2.481 | 0.1 |
| 20000.0 | 5.0 | 3.0 | 0.025 | 2.57 | 0.1 |
| 20000.0 | 10.0 | 3.0 | 0.025 | 2.402 | 0.1 |
| 20000.0 | 10.0 | 4.0 | 0.025 | 2.514 | 0.1 |
| 20000.0 | 20.0 | 4.0 | 0.025 | 2.385 | 0.1 |
| 2000.0 | 20.0 | 3.0 | 0.1 | 2.546 | 0.1 |
| 2000.0 | 20.0 | 2.0 | 0.1 | 2.387 | 0.1 |

Largest Λ0 certifiable at the requested (N_h,m_h,v0), by bisection (c blows up near the boundary): m=5: 4.77 (c≈21); m=10: 6.72 (c≈20); G=24, m=10: 3.45 (c≈19); G=24, m=20: 4.83 (c≈28). v0 needed at the requested Λ0: G=51, m=5: v0 ≤ 0.005 gives c=3.03; m=10: v0 ≤ 0.01 gives 3.02; G=24, m=10, Λ0=6: v0 ≤ 0.02 gives 2.85; m=20: v0 ≤ 0.05 gives 3.22.
Stratum certificates were optimised in double precision (SLSQP) with +0.0005 margin and were not re-verified in exact rationals (the Part 1 certificates were).
c_L (stratified) is a two-point-strata family search (K active identical strata, minority count M_h scanned); the K=42, m=5 value was reproduced by exact multinomial enumeration (2.84336 both ways). Other values come from 3×10^6 Monte Carlo draws × 2 seeds (identical, since the quantile is atom-valued). Only identical two-point strata were searched, so these are lower estimates.

## 6. Conjectures (numerical evidence only)
1. The worst case in K(κ0) is attained by a population with ≤ 3 distinct values for G=24 (d=3 equals d=6 to ±0.5% in all G=24 cells) and ≤ 4–6 for G=51 (d=4–6 needed at 0.75–0.95 frontier; likely not fully converged).
2. c(κ0) is non-monotone in the multiplicity k of the two-point population but monotone in κ0 (proved). For κ0 ≤ ~0.75 frontier the maximiser is two-point (G=24, n=8: k=9, c=√6) or a near-two-point 3-valued population; near the frontier (≥0.9) a spike group (3–5 units at ±1.8–2.9 SD, rest near 0) dominates and c rises sharply (2.4, 4.5, 6.5 at 0.75, 0.9, 0.95 for (24,8)).
3. True c(κ0) is probably within a few % of c_L for κ0 ≤ 0.5 frontier.
4. Stratified: the worst box design is identical two-point strata with minority fraction ≈ 0.012–0.03 (Λ ≈ 5.7–9) and K just above 1/v0 active strata; c_L ≈ 2.1–2.8, so a certified value near 3 should be provable with an atom-aware argument.
