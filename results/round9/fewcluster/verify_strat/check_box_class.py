"""Box class A = {v_h <= v0, kappa_h (N_h-1) <= Lam0^2 for all h}.
Claimed: beta(A) = prod of pi_h(kmin_h(Lam0)) over the ceil(1/v0) strata with largest such pi (two-point levels dominate when Lam0>=2).
Brute force: exact beta by exhaustive enumeration of multiplicity patterns (partitions) with kappa_min(pattern) by optimisation,
(a) beta_exact = max over choices of >= m0 nonconstant strata of prod p, box-feasible patterns only;
(b) explicit attaining population + full sample-space enumeration; (c) random populations in the box class never exceed beta."""
import os, sys, math, itertools; sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from math import comb
from strat_lib import *
from check_levels_domination import partitions, kappa_min
rng = np.random.default_rng(5)

def kmin_h(N, Lam0):
    for k in range(1, N // 2 + 1):
        if (N - k) * (N - 1) / (N * k) <= Lam0**2 + 1e-12: return k
    return None
def formula(strata, v0, Lam0, use_R=False):
    m0 = math.ceil(1 / v0 - 1e-12)
    ps = []
    for N, n, W in strata:
        k = kmin_h(N, Lam0)
        p = pi_k(N, n, k) if k else 0.0
        if use_R and (N - 1) / N <= Lam0**2 + 1e-12: p = max(p, R_h(N, n))   # R level (kappa=1/N) admissible if (N-1)/N <= Lam0^2
        ps.append(p)
    if len(ps) < m0: return 0.0          # class empty
    return float(np.prod(sorted(ps, reverse=True)[:m0]))
def exact_beta(strata, v0, Lam0):
    m0 = math.ceil(1 / v0 - 1e-12); ps = []
    for N, n, W in strata:
        best = 0.0
        for p in partitions(N):
            if len(p) < 2: continue
            if kappa_min(p) * (N - 1) <= Lam0**2 + 1e-9:
                best = max(best, sum(comb(m, n) for m in p) / comb(N, n))
        ps.append(best)
    if len(ps) < m0: return 0.0
    return float(np.prod(sorted(ps, reverse=True)[:m0]))

def attaining_pop(D, strata, v0, Lam0):
    m0 = math.ceil(1 / v0 - 1e-12)
    ranked = sorted(range(D.H), key=lambda h: -(pi_k(D.Ns[h], D.ns[h], kmin_h(D.Ns[h], Lam0)) if kmin_h(D.Ns[h], Lam0) else 0))[:m0]
    e = []
    for h in range(D.H):
        N, n, W = D.Ns[h], D.ns[h], D.Ws[h]
        if h in ranked:
            k = kmin_h(N, Lam0); x = np.zeros(N); x[:k] = 1.0
            coef = W**2 * (1 - n / N) / (n * (N - 1)) * k * (1 - k / N)
            x *= math.sqrt((1 / m0) / coef); e.append(x)
        else: e.append(np.zeros(N))
    return e

rows = []; fails = 0
for trial in range(40):
    H = int(rng.integers(3, 6)); Ns = [int(rng.integers(4, 9)) for _ in range(H)]
    ns = [int(rng.integers(2, min(N, 4))) for N in Ns]; Ws = list(rng.uniform(0.5, 2, H))
    strata = list(zip(Ns, ns, Ws)); D = Design(Ns, ns, Ws)
    for v0 in [0.5, 0.34, 0.3]:
        for Lam0 in [1.05, 1.3, 1.6, 2.0, 2.5, 3.5]:
            m0 = math.ceil(1 / v0 - 1e-12)
            fa = formula(strata, v0, Lam0); fR = formula(strata, v0, Lam0, True); ex = exact_beta(strata, v0, Lam0)
            rows.append((Ns, ns, v0, Lam0, fa, fR, ex))
            if Lam0 >= 2.0 and abs(fa - ex) > 1e-9: fails += 1; print('MISMATCH Lam0>=2', Ns, ns, v0, Lam0, fa, ex)
            if ex > max(fa, fR) + 1e-9: fails += 1; print('EXACT EXCEEDS FORMULA(+R)', Ns, ns, v0, Lam0, fa, fR, ex)
print('Lam0>=2: formula == exact beta in', sum(1 for r in rows if r[3] >= 2 and abs(r[4] - r[6]) < 1e-9), 'of', sum(1 for r in rows if r[3] >= 2))
low = [r for r in rows if r[3] < 2]
print('Lam0<2: two-point-only formula < exact beta in', sum(1 for r in low if r[4] < r[6] - 1e-9), 'of', len(low),
      '| formula+R >= exact in', sum(1 for r in low if r[5] >= r[6] - 1e-9), 'of', len(low), '| formula+R == exact in', sum(1 for r in low if abs(r[5] - r[6]) < 1e-9))
ex_low = [r for r in low if r[4] < r[6] - 1e-9][:3]; print('examples (N,n,v0,Lam0,two-pt formula,formula+R,exact):', ex_low)
# attaining population + full enumeration, and random-population ceiling
att_ok = 0; att_tot = 0; viol = 0; nrand = 0
for trial in range(25):
    H = int(rng.integers(3, 5)); Ns = [int(rng.integers(4, 8)) for _ in range(H)]; ns = [int(rng.integers(2, 4)) for N in Ns]; Ws = list(rng.uniform(.5, 2, H))
    strata = list(zip(Ns, ns, Ws)); D = Design(Ns, ns, Ws)
    for v0 in [0.5, 0.34]:
        for Lam0 in [2.0, 3.0]:
            if len(strata) < math.ceil(1 / v0 - 1e-12) or any(kmin_h(N, Lam0) is None for N in Ns): continue
            e = attaining_pop(D, strata, v0, Lam0); Vh = D.V_h(e); v = Vh / Vh.sum()
            inbox = (v.max() <= v0 + 1e-12) and all(D.kappa_h(e[h]) * (Ns[h] - 1) <= Lam0**2 + 1e-12 for h in range(D.H) if Vh[h] > 0)
            diff, se = D.dist(e); p_enum = np.mean(se == 0); f = formula(strata, v0, Lam0)
            att_tot += 1; att_ok += int(inbox and abs(p_enum - f) < 1e-12)
            # random in-class populations: P(SE=0) <= f
            for _ in range(300):
                ee = []
                for h in range(D.H):
                    N = Ns[h]; g = int(rng.integers(1, 4)); lab = rng.integers(0, g, N)
                    if rng.random() < .5: k = int(rng.integers(1, N // 2 + 1)); lab = np.zeros(N, int); lab[:k] = 1; g = 2
                    x = (rng.normal(size=max(g, 2))[lab] * math.exp(rng.normal())); ee.append(x + (1e-3 * rng.normal(size=N) if rng.random() < .3 else 0))
                Vh = D.V_h(ee)
                if Vh.sum() <= 0 or all(np.ptp(x) == 0 for x in ee): continue
                # try to rescale strata to satisfy v_h<=v0: random v
                kap = np.array([D.kappa_h(x) for x in ee]); nz = [h for h in range(D.H) if np.ptp(ee[h]) > 0]
                if len(nz) < math.ceil(1 / v0 - 1e-12): continue
                if any(kap[h] * (Ns[h] - 1) > Lam0**2 + 1e-12 for h in nz): continue
                w = rng.dirichlet(np.ones(len(nz)) * 3); 
                if w.max() > v0: continue
                for wi, h in zip(w, nz): ee[h] = ee[h] * math.sqrt(wi / Vh[h])
                nrand += 1; p = D.p_se0(ee)
                if p > f + 1e-12: viol += 1
print(f'attaining two-point population: in box class and exact P(SE=0) (full enumeration) == formula in {att_ok}/{att_tot}')
print(f'random box-class populations tested: {nrand}; with P(SE=0) > formula: {viol}')
print('total flagged problems', fails)
