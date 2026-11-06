# Independent verification: finite-population frontier statements

Scope: all seven statements (Lemma 0, Lemma 1, Theorems 1-2, Proposition 3, Corollary 4, CONSEQUENCE) were proved by hand and checked by exact enumeration of all C(G,n) samples at G in {8,10,12} (plus G up to 16 for Prop 3, G=24,n=8 for CONSEQUENCE). Searches for worst-case populations are heuristic (random restarts + hill-climbing), hence "found", not "proved".
Notation: e = z - lambda f, kappa as in the task, k2(k) = kappa2(k), pi(k) as in the task, N = C(G,n).

## Summary of verdicts

| Statement | Verdict | Key remark |
|--|--|--|
| Lemma 0 | proved | The constant is UNCONDITIONAL; the two earlier reviewers are wrong. Hypothesis needed: coverage at every z in R^G (not only K(kappa0)). |
| Lemma 1 | proved with corrections | Bracket "k <= G/2" is needed for the equality case; for k > G/2 the inequality is strict (true minimum is 1/G for the even G tested). |
| Theorem 1 | proved with corrections | Strictness k2(k) < kappa0 is essential for the proof (boundary kappa0 = k2(k) is NOT settled). "Unbounded" is the right conclusion (half-lines allowed). OLS-tuned lambda satisfies (E) only with an intercept. |
| Theorem 2 | proved with corrections | Needs 2 <= n < G; non-strict beta <= alpha suffices. Applies to fixed lambda only (not OLS-tuned). Worst-case coverage over K converges to exactly 1-beta (from below), it does not exceed it. |
| Proposition 3 | proved | Both bounds hold at all 932 (G,n,kappa0) cases; convention max over empty set = 0 for the lower bound. |
| Corollary 4 | proved with corrections | Needs FIXED sample size n. The "cannot be removed" conclusion needs the (easy) re-run of Thm 1 with P_p in place of SRSWOR. |
| CONSEQUENCE | proved with corrections | All numbers reproduce (pi(6)=0.0595, pi(5)=0.1028, k2(6)=0.125; G=51,n=8: k2(12)=0.0637; G=51,n=4: no k<=25 works, min pi = pi(25)=0.1104). BUT "largest admissible kappa0 = k2(6)" is off by one step: the sup is k2(k*-1) = k2(5) = 0.1583 (0.0713 for G=51,n=8). k2(k*) is the SMALLEST kappa0 at which the k* two-point enters K. Table columns k_star, kappa_star, rest_bound reproduce exactly. |

## Lemma 0 (unconditional)
Proof. Fix z, M, alpha-valid C (coverage >= 1-alpha at every population in R^G), SRSWOR. For j in 1..G let z^j = z + M e_j; theta(z^j) = theta(z) + M/G. Samples with j not in S have identical data under z and z^j. Hence
P_z(j notin S, theta(z)+M/G in C(D)) = P_{z^j}(j notin S, theta(z^j) in C(D)) >= (1-alpha) - P(j in S) = 1 - alpha - n/G.
Sum over j. In every sample exactly G-n indices j are unsampled, so sum_j 1{j notin S} = G-n identically, thus sum_j P(j notin S, A) = (G-n) P(A), A = {theta+M/G in C(D)}. Dividing by G-n: P_z(A) >= (1-alpha-n/G)/(1-n/G) = unconditional. QED.
Who is right: the averaged quantity is the unconditional probability P(A) (not P(A | j notin S)); the per-j conditional versions are only the intermediate step. Verified: identity sum_j P(j notin S, A) = (G-n)P(A) to 1e-12 over 300 random procedures/populations/M at G=8,n=3; the per-j transfer holds in all; unconditional bound holds in 300/300 (min slack > 0).
Caveats: (i) the hypothesis is coverage over ALL of R^G (the perturbation z+M e_j leaves K(kappa0) for large M), so Lemma 0 is not a statement about K(kappa0); (ii) vacuous if 1-alpha <= n/G; (iii) the bound is not claimed sharp. The test procedures were "R on a set of samples of prob 1-alpha', t-interval elsewhere" (valid at every population by construction).

## Lemma 1 (two-point extremal)
Proof. WLOG e = 0 on B, free x_1..x_k on A (|A| = k), shift/scale invariance. Let ebar = sum x/G, d_i = x_i - ebar (i in A); sum_A d_i = k xbar (1-k/G) where xbar = mean of x. P = sum_A d_i^2 >= (sum d_i)^2/k = k xbar^2 (1-k/G)^2 (Cauchy-Schwarz, equality iff all d_i equal). Q = (G-k) ebar^2 = (G-k)k^2 xbar^2/G^2. So P >= Q (G-k)/k. SS = P+Q. Max share >= (P/k)/(P+Q) (average of A-deviations <= max), which increases in P/Q; at P/Q = (G-k)/k it equals (1-k/G)/k. Equality iff all d_i equal (single common value on A, different from the value on B since e non-constant) AND the max share is the A-share; B-share is ebar^2/SS = k/(G(G-k)) which is <= (1-k/G)/k iff k <= G/2. For k > G/2 the max is the B-share, so the bound is strict. QED.
Numerics (G=8,10,12, all k, SLSQP epigraph minimisation, 40 restarts): min kappa = (1-k/G)/k to 1e-6 for every k <= G/2; for k > G/2 the minimum is strictly larger and equals 1/G (G even: 0.125, 0.1, 0.0833). 200,000 random draws: 0 violations.

## Theorem 1
Proof. Fix k, kappa0 > k2(k), pi(k) > alpha, any z, u = z - lambda f. B2 any k-set, B1 its complement, e_eps = 1_{B2} + eps u. kappa(1_{B2}) = k2(k) for k <= G/2 (A-share (1-k/G)^2/(k(1-k/G))), kappa is continuous at non-constant e, hence e_eps in K(kappa0) for eps <= eps0 (this is where strictness is used). For S in B1: data of z_eps equal data of the (E)-transform of z with (a,b)=(0,eps); for S in B2, (a,b)=(1,eps). (E) is applied to populations z^{(a,b)}; C depends on the data only, so C(S,(z_eps)_S,f) = lambda Fbar + a + eps(C(S,z_S,f)-lambda Fbar). theta(z_eps) = lambda Fbar + k/G + eps ubar. Covering theta(z_eps) is therefore equivalent to: S in B1: lambda Fbar + k/(G eps) + ubar in C(S,z_S,f); S in B2: lambda Fbar - (1-k/G)/eps + ubar in C(S,z_S,f). Let T = {S in B1 or S in B2}, P(T) = pi(k). Coverage >= 1-alpha gives P(T and covered) >= pi(k) - alpha for every eps. T is finite, so some W subset T with P(W) >= pi(k)-alpha is "covered" along a sequence eps_j -> 0. For S in W, C(D_S) (D_S fixed, independent of eps) contains points tending to +inf (S in B1) or -inf (S in B2), so C(D) is unbounded on W. QED.
Remarks: (a) 'unbounded' is the correct conclusion: C(D) need not be R; a half-line is consistent. Specifically unbounded above on B1-samples, below on B2-samples. (b) If k < n only B1-samples count (C(k,n)=0), fine. (c) Strictness: at kappa0 = k2(k) the perturbation can leave K for generic u, so the argument gives nothing; the statement at equality is not settled by this proof (Thm 2 also does not apply since beta >= pi(k) > alpha). (d) (E) is used only in the b = eps -> 0 direction plus shift a in {0,1}. (e) OLS-tuned lambda-hat (PPI with an estimated slope) satisfies (E) for every reference lambda iff the OLS includes an intercept: then lambda-hat' = lambda + b(lambda-hat - lambda) and residuals transform as a + b e. Without intercept (slope = sum f z / sum f^2) (E) fails in a (numerically error 8.3 vs 1e-14 with intercept). Requires f_S non-constant.
Numerics: 420 configurations (G,n) in {(8,3),(10,4),(12,4)}, every k <= G/2, 4 types of u, c in {1,...,1e5}, kappa0 = 1.02 k2(k): coverage of the fpc-t interval at eps = 1e-8 is <= 1-pi(k) in 407/420; all 13 exceptions are c = 1e5 with u of scale 1e3 (eps*c*scale not << 1, as expected for a limit at fixed c); redoing c = 1e5 with eps <= 1e-9 gives 120/120. For c >= 5 coverage equals 1-pi(k) exactly (mixed samples all covered). The OLS-tuned PPI interval (with intercept) also has coverage -> 1-pi(k) (c=100: equal). At G=24,n=8 k=5, coverage is 0.89723 = 1-pi(5) for c in {3,100,1000}.

## Theorem 2
Proof. Interval covers iff |ebar_S - ebar| <= c sqrt((1-n/G)s^2/n) (if s = 0: iff ebar_S = ebar). The event is invariant under e -> a + b e (b>0), so it suffices to take e in K' = {ebar=0, sum e^2=1, kappa<=kappa0}, which is compact (closed conditions, all e non-constant). Let miss_c(e) = #{S: not covered}. Suppose no finite c works: for each j there is e_j in K' with miss_{c=j}(e_j) > alpha N. Pigeonhole on the finite family of miss-sets: a fixed set W with |W| > alpha N and a subsequence along which every S in W is missed; pass to e_j -> e* in K'. For S in W: if s_S(e_j)=0 then s_S(e*)=0; otherwise |ebar_S(e_j)| <= 1 forces s_S(e_j) <= |ebar_S|/(j sqrt((1-n/G)/n)) -> 0, so s_S(e*) = 0. Thus e* is constant on every S in W, so |W| <= beta N <= alpha N, contradiction. QED.
Remarks: n >= 2 and n < G needed (s^2 and fpc). beta<=alpha non-strict suffices (integer counts). beta is a max of a finite set of integers, so it exists. The theorem is for FIXED lambda; an OLS-tuned lambda-hat is a different procedure (the interval above is not it). Converse-type fact: miss_c(e*) >= beta N at a maximiser e* in K (up to the coincidence ebar_S = ebar, which perturbations remove), so worst-case coverage is <= 1-beta for every c and tends to 1-beta from below; it is not "approaching >= 1-beta" from above. Numerically it reaches exactly 1-beta at finite c (c0 between 1 and 10 in all 11 configurations).
Numerics: 11 (G,n,kappa0) configurations ((8,3),(10,4),(12,4), 3-4 each, kappa0 in interiors of the exact beta steps), c in {1,2,3,5,10,30,100,1e3,...,1e6}; 24 starts x 600 hill-climb steps per (config,c). The worst coverage found rises monotonically in c, equals 1-beta exactly for all c >= c0 (c0 <= 10), never below 1-beta for c >= c0 (0 violations). Heuristic search - provisional evidence of sharpness, not proof; the proof above is independent of it.

## Proposition 3
Proof. Lower bound: for k <= G/2, kappa2(k) <= kappa0, e = 1_{B2} is in K and is constant on exactly C(G-k,n)+C(k,n) = pi(k)N samples. Upper bound: let e in K have level sets of sizes m_1 >= m_2 >= ... (count = sum C(m_i,n)). Case M = m_1 >= G/2: put k = G-M <= G/2, k >= 1; Lemma 1 gives kappa2(k) <= kappa(e) <= kappa0; the count is C(G-k,n) + sum_{i>=2} C(m_i,n) <= C(G-k,n)+C(k,n) = pi(k)N, by superadditivity C(a,n)+C(b,n) <= C(a+b,n). Case M < G/2: C(x,n) is convex on the integers (second difference C(x-1,n-2) >= 0), so over {m_i <= M, sum = G} the sum is maximal at (M,...,M,G mod M) by majorisation: count <= floor(G/M) C(M,n) + C(G mod M, n), at most R. QED.
Numerics: all integer partitions of G for G = 6..16, n = 2..6; kappa_min(partition) computed exactly by vertex enumeration of max sum m_i w_i^2 over {w in [0,1]^r, sum s_i m_i w_i = 0} (checked vs Nelder-Mead: agree to 3e-8, numerical never below exact); beta(kappa0) evaluated at every step point and just above it: 932 combos, 0 violations; beta = LB in 87.8%, and in the remaining 114 cases (e.g. G=7 where the k-set is empty, so LB=0 and beta = R) beta = UB exactly.

## Corollary 4
Proof. For fixed S with |S| = n and B2 uniformly random k-set: P(S in B2) = C(G-n,k-n)/C(G,k), P(S in B1) = C(G-n,k)/C(G,k); the identity C(G,n)C(G-n,k-n) = C(G,k)C(k,n) (and the same with k -> G-k) gives the sum exactly pi(k) for EVERY S. Averaging p(S) over S: the mean over B2 of P_p(S in B1 or B2) is exactly pi(k); a maximiser has >= pi(k). QED. Needs a fixed-size design (for a mixed-size design the S-wise value is pi_{|S|}(k), decreasing in |S|; e.g. G=10,k=3: 0.1667 at n=4 vs 0.5333 at n=2). To get "cannot be removed by changing the design": rerun Theorem 1 with that B2 (K(kappa0) is permutation invariant, z_eps = lambda f + 1_{B2} + eps u needs nothing about f), giving P_p(C unbounded) >= pi(k) - alpha for any f-dependent, z-independent design.
Numerics: 200 random designs (Dirichlet, point masses), G in 6..12, n in 2..4, all k<=G/2: max |avg_B P_p - pi(k)| = 4.4e-16; max_B P_p - pi(k) >= 0 in all.

## CONSEQUENCE (alpha = 0.10)
Recomputed (checks_consequence_table.csv):
- G=24,n=8: pi(6)=0.059497, pi(5)=0.102767, kappa2(6)=0.125, kappa2(5)=0.158333, R=0.000449. Reproduced.
- G=51,n=8: kappa2(12)=0.063725 (pi(12)=0.09662, pi(11)=0.12077), kappa2(11)=0.071301, R=0.003397. Reproduced.
- G=51,n=4: min_k pi(k) = pi(25) = 0.110444 > 0.10 for all k<=25. Reproduced. (R = 0.101240 comes from the (25,25,1) partition.) Exact frontier from all partitions: beta > alpha already at kappa0 = 1/50 = 0.02, vs T1 threshold kappa2(25) = 0.020392: a narrow undecided window; for kappa0 > 0.020392 impossible.
- Asymptotics: pi(floor(G/2)) < 2^(1-n) and -> 2^(1-n) from below, and pi(k) is nonincreasing on k<=G/2 (checked G<=60, n<=12), so pi(k) > alpha for every k<=G/2 for all large G iff 2^(1-n) > alpha, i.e. n < 1 + log2(1/alpha) (= 4.32 for alpha=0.1, so n<=4; first G with pi(G/2)>0.1: G=7 for n=3, G=31 for n=4). Correct, with quantifiers: 'for G >= G0(n,alpha), every kappa0 > kappa2(floor(G/2)) ~ 1/G'. Not an iff for impossibility at FIXED kappa0: for fixed kappa0 the two-point with k ~ 1/kappa0 has pi(k) -> 1 as G -> infinity, so impossibility at fixed kappa0 holds for any n, alpha<1.
- CORRECTION: with k* = smallest k with pi(k) <= alpha, possibility (Thm 2) holds for kappa0 < kappa2(k*-1) when R <= alpha; impossibility (Thm 1) for kappa0 > kappa2(k*-1); kappa2(k*) is the smallest kappa0 at which the k*-two-point enters K, not the largest admissible. Exact check by DFS over all partitions: smallest kappa0 with beta > alpha equals kappa2(k*-1) in all rows where k* exists (table below). Direct G=24,n=8 coverage of the fpc-t interval: at kappa0 = 0.14 (between 0.125 and 0.1583) worst found coverage = 0.940503 = 1-pi(6) >= 0.90 for c >= 10; at kappa0 = 0.17 the z_eps with k=5 has coverage 0.89723 < 0.90 for any c. At exactly kappa0 = kappa2(k*-1) the theorems are silent.

Table (alpha=0.10; 'matches table' compares k_star, kappa_star, rest_bound with the attached CSV; the other columns k_star_one_block, pi_at_k_star_minus1, Lambda_star etc. were not part of the request):

| G | n | k* | kappa2(k*) (table col kappa_star) | R (rest_bound) | kappa2(k*-1) | exact frontier (smallest kappa0 with beta>alpha) | matches table |
|--|--|--|--|--|--|--|--|
| 15 | 4 | 7 | 0.07619 | 0.05128 | 0.10000 | 0.10000 | yes |
| 15 | 6 | 4 | 0.18333 | 0.00280 | 0.26667 | 0.26667 | yes |
| 15 | 8 | 3 | 0.26667 | 0.00000 | 0.43333 | 0.43333 | yes |
| 15 | 10 | 2 | 0.43333 | 0.00000 | 0.93333 | 0.93333 | yes |
| 15 | 12 | 2 | 0.43333 | 0.00000 | 0.93333 | 0.93333 | yes |
| 24 | 4 | 11 | 0.04924 | 0.06211 | 0.05833 | 0.05833 | yes |
| 24 | 6 | 7 | 0.10119 | 0.00686 | 0.12500 | 0.12500 | yes |
| 24 | 8 | 6 | 0.12500 | 0.00045 | 0.15833 | 0.15833 | yes |
| 24 | 10 | 4 | 0.20833 | 0.00001 | 0.29167 | 0.29167 | yes |
| 24 | 12 | 4 | 0.20833 | 0.00000 | 0.29167 | 0.29167 | yes |
| 24 | 16 | 3 | 0.29167 | 0.00000 | 0.45833 | 0.45833 | yes |
| 25 | 4 | 12 | 0.04333 | 0.07826 | 0.05091 | 0.05091 | yes |
| 25 | 6 | 8 | 0.08500 | 0.01043 | 0.10286 | 0.10286 | yes |
| 25 | 8 | 6 | 0.12667 | 0.00092 | 0.16000 | 0.16000 | yes |
| 25 | 10 | 5 | 0.16000 | 0.00004 | 0.21000 | 0.21000 | yes |
| 25 | 12 | 4 | 0.21000 | 0.00000 | 0.29333 | 0.29333 | yes |
| 25 | 16 | 3 | 0.29333 | 0.00000 | 0.46000 | 0.46000 | yes |
| 51 | 4 | none | - | 0.10124 | - | 0.02000 | yes |
| 51 | 6 | 16 | 0.04289 | 0.01967 | 0.04706 | 0.04706 | yes |
| 51 | 8 | 12 | 0.06373 | 0.00340 | 0.07130 | 0.07130 | yes |
| 51 | 10 | 10 | 0.08039 | 0.00051 | 0.09150 | 0.09150 | yes |
| 51 | 12 | 8 | 0.10539 | 0.00007 | 0.12325 | 0.12325 | yes |
| 51 | 16 | 6 | 0.14706 | 0.00000 | 0.18039 | 0.18039 | yes |

Table is the attached vbf739906_s3_frontier_exact.csv, alpha=0.10 rows (23 of 46 rows). k_star is NaN exactly when no k <= G/2 has pi(k) <= alpha (G=51,n=4); all 23 rows match.

## Files
Scripts: frontier_common.py, check_lemma0_lemma1_cor4.py, check_theorem1.py, check_theorem1_b.py, check_prop3.py, check_theorem2.py, check_consequence.py, check_consequence2.py, make_summary.py. CSVs: verify_frontier_numerical_checks.csv (summary), checks_consequence_table.csv, checks_prop3.csv, checks_theorem2.csv, checks_theorem1.csv.
