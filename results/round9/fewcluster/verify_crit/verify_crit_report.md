# verify_crit_report.md — independent verification of crit_value_report.md (sections 0,1,2,5)
No literature consulted. All checks by own code (scripts listed at end). Exact = Python Fractions / full enumeration.

## Verdicts
| item | verdict |
|---|---|
| (1) reduction miss <=> t_S > rho | **proved** (own algebra; 62,808 samples vs raw interval test, 0 discrepancies; constant-sample and x_S=0 edge cases agree) |
| (2) Lemma 1 (generalised) | **proved** (own proof; 20,000 random + tight R=1 case, 0 violations, min kappa/bound = 1.00001) |
| (2) Lemma 2 (band) | **proved** (uses |d_i|^2 <= (n-1)/n * sum d^2; 2,023 missed samples, 0 violations) |
| (3) Theorem Q: majorant validity | **proved_with_changes** — correct; `a1>=0` is not needed (the two ray conditions suffice), harmless |
| (3) moment expansions, p4-only/linear/no p3, 1/G<=p4<=kappa0 | **proved** (derived by Moebius inversion over set partitions; general power-sum formula equals exact enumeration, error 0, 6 (G,n)) |
| (3) four certified cells | **proved** (exact rational; bounds below). Caveat: report's tabulated kappa0 are rounded; exact values are fraction x frontier (below) |
| (4) Theorem S | **proved** (derivation re-done; E L^2 formula equals exact 3-stratum enumeration; plateaus 0.28698/0.16701/0.25988/0.14829 reproduced; c=3.029 etc. reproduced). Certificates are double-precision optima, not exact-rational (as report states) |
| (5) c_L spot checks | **proved** (5 cells, full enumeration of all C(G,n) samples with the raw interval) |

## (1) Reduction
x=e-ebar, A=sum_S x, Q=sum_S x^2, xbar_S=A/n, s^2=(Q-A^2/n)/(n-1). Miss <=> xbar_S^2 > c^2(1-f)s^2/n <=> A^2 > g n Q - g A^2 (g=c^2(1-f)/(n-1)) <=> A^2/(nQ) > g/(1+g)=rho. s=0, xbar!=0 gives t=1>rho (miss); x_S=0 gives 0>rho false (cover).

## (2) Lemmas
Lemma 1: others sum to -Sigma <= -ma, so B=max of the k others >= ma/k; T<=mR^2a^2+kB^2; B^2/(mR^2a^2+kB^2) increasing in B^2, evaluate at B=ma/k: m/(k(m+R^2 k)). Tight at R=1 (G=24,m=18: 0.125 = bound).
Lemma 2: miss <=> sum d_i^2 < n(n-1) xbar^2/(c^2(1-f)); |d_i|^2 <= (n-1)/n sum d^2 so |d_i| < delta |xbar|, delta=(n-1)/(c sqrt(1-f)); delta<1 => one sign, ratio<(1+delta)/(1-delta).

## (3) Theorem Q
Validity: wedge {u>0, u/n<=q<u/(rho n)} is the cone on rays q=u/n and q=u/(rho n); L-1 linear => >=0 on cone iff >=0 on both rays; so 1[miss]<=L^2.
Exact moments (own derivation, p1=0,p2=1; p4=sum x^4):
- E A^2 = n(G-n)/(G(G-1)),  E Q = n/G
- E A^4 = n(G-n)[(G^2-6Gn+G+6n^2)p4 + 3Gn-3G-3n^2+3] / (G(G-1)(G-2)(G-3))
- E A^2Q = -n(G-n)[(2n-G)p4 - n + 1] / (G(G-1)(G-2))
- E Q^2 = n[(G-n)p4 + n - 1] / (G(G-1))
All weight-4 monomials in power sums: p4, p3p1, p2^2, p2p1^2, p1^4 => with p1=0,p2=1 only p4 survives (p3 only enters multiplied by p1), linearly. 1/G<=p4 (Cauchy-Schwarz), p4<=max x^2 * sum x^2 <= kappa0. E L^2 is linear in p4 => sup at endpoints.
Frontier recomputed (alpha=1/10, k* = smallest k<=G/2 with [C(G-k,n)+C(k,n)]/C(G,n)<=alpha; kappa2(k*-1)=(1-(k*-1)/G)/(k*-1)):
| (G,n) | k* | frontier | fraction | exact kappa0 | reported c_U | exact bound (own rational a1,a2) | own min c |
|---|---|---|---|---|---|---|---|
| (24,8) | 6 | 19/120=0.158333 | 0.4 | 19/300=0.0633333 | 3.775 | 0.0999844430 (a1=69046177/10^8, a2=-31803679/10^7) | 3.7744 |
| (24,12) | 4 | 7/24=0.291667 | 0.25 | 7/96=0.0729167 | 2.892 | 0.0999461188 (a1=16166747/25000000, a2=-106875037/50000000) | 2.8912 |
| (51,16) | 6 | 46/255=0.180392 | 0.25 | 23/510=0.0450980 | 3.234 | 0.0999805349 (a1=32030439/5e7, a2=-331723817/1e8) | 3.2335 |
| (51,8) | 12 | 40/561=0.071301 | 0.4 | 16/561=0.0285205 | 4.403 | 0.0999916513 (a1=121013737/1e8, a2=-135565417/2e7) | 4.4025 |
All four: feasibility conditions hold exactly (rho rational from rational c), max over p4 in {1/G,kappa0} <= 1/10 in exact arithmetic (binding endpoint p4=kappa0). Reported c_U are tight to the 3rd decimal (c-0.01 gives >0.1). Sanity: E L^2 from the formula equals full-enumeration E L^2 for 10 random populations (G=24,n=8), and L>=1 on every missed sample; true P(miss) there is ~0.01-0.02, so the certificate is valid but far from tight (c_U 3.775 vs c_L 2.086).

## (4) Theorem S
Wedge {q>=0, u>c^2 q}: rays (1,0),(c^2,1) => a1>=0 and a2+a1c^2>=0 (exactly as stated). E u=V=1, E q=V (unbiased), E u^2=3V^2+sum V_h^2(r4-3), E[uq]=V^2+sum V_h^2(rDV-1) (cross terms vanish by independence and zero means), E q^2=V^2+sum V_h^2(rVV-1): reproduces the report's formula. Formula equals exact enumeration of a 3-stratum population (N=7,m=3, unequal W_h): both 0.9219461826116027 (Fraction equality True). Sum v_h^2 <= v0 and max(0,.) gives a valid (conservative) upper bound. Reported numbers reproduced: plateau (c=60) 0.28698 (N=20000,m=5,L0=9,v0=.025; reported 0.287), 0.16701 (0.167), 0.25988 (0.2599), 0.14829 (0.1483); certified c: (20000,5,9,0.005): bound 0.099968 at 3.029 (my min c 3.0281); (2000,20,6,0.05): 0.099988 at 3.222 (3.2215); (20000,5,3,0.025): 0.099925 at 2.57 (2.5692). Doubles only (SLSQP), margins ~1e-4..3e-5.

## (5) c_L spot checks (all C(G,n) samples, raw interval formula; c_pop = smallest c with coverage>=0.9)
| population | kappa | c_pop (own) | reported | coverage at c_pop / just below |
|---|---|---|---|---|
| (24,8) 2-pt, 9 x(-5), 15 x(3) (=[-1.264,0.758]) | 0.069444 <= 0.0792 | 2.44949 = sqrt 6 | 2.449 | 0.97851 / 0.89977 |
| (24,8) 3-valued [-1.024,1.207,-0.274]x[9,9,6] (rounded) | 0.063330 <= 19/300 | 2.08629 (jitter +-5e-4 in values: 2.08574..2.08705) | 2.086 | 0.92222 / 0.89138 |
| (24,12) 3-valued [0.806,1.198,-0.893]x[4,7,13] | 0.062364 <= 7/96 | 1.91331 | 1.914 | 0.90047 / 0.89999 |
| (24,12) 2-pt [-0.692,1.384]x[16,8] | 0.083333 <= 0.1458 | 2.09762 | 2.098 | 0.97281 / 0.88989 |
Note: c_pop sits on an atom; the (24,12) 3-valued value is within 5e-5 coverage of the 0.9 threshold, so is rounding-sensitive (1.9133 vs 1.914 reflects the rounded inputs). The two-point population (kappa=0.0694) is NOT in the 0.4-frontier class (kappa0=0.0633), consistent with the report using the 3-valued one there. These are lower bounds only (c_L valid for any member of the class).

## Scripts
v1_reduction_lemmas.py, v3_moments.py, qlib.py, v3_thmQ.py, v4_thmS.py, v5_cL.py, v6_QvsEnum.py (v/ directory).
