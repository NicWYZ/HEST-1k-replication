"""(II): build the defeating (jittered two-point) population for configurations with prod pi > alpha and
sum a > 1/kappa0; show exact coverage of T +- c SE for huge c is < 1-alpha; show the equality-boundary behaviour."""
import os, sys, math; sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from math import comb
from strat_lib import *
rng = np.random.default_rng(7)

def build_pop(D, A_k, v, delta, rng, Jscale=1.0, signs=None):
    """A_k: dict h->k ; v: dict h->share. returns e (list of arrays). cluster1 = k units at location Delta_h, rest at 0, jitter delta*J.
    strata not in A: constant 0 (delta=0) or delta*J if delta>0 (tiny share)."""
    e = []; Vtot = 1.0
    for h in range(D.H):
        N, n, W = D.Ns[h], D.ns[h], D.Ws[h]
        if h in A_k:
            k = A_k[h]
            # V_h = W^2(1-f)/(n(N-1)) * k(1-k/N) Delta^2 = v_h
            Vh = v[h]; coef = W**2 * (1 - n / N) / (n * (N - 1)) * k * (1 - k / N)
            Dl = math.sqrt(Vh / coef) * (signs[h] if signs else 1)
            x = np.zeros(N); x[:k] = Dl
            x = x + delta * rng.normal(size=N) * Jscale
        else:
            x = delta * rng.normal(size=N) if delta > 0 else np.zeros(N)
        e.append(x)
    return e

def run(strata_NW, alpha, ratio=1.05):
    Ns = [s[0] for s in strata_NW]; ns = [s[1] for s in strata_NW]; Ws = [s[2] for s in strata_NW]
    D = Design(Ns, ns, Ws)
    cap, arg = cap_knapsack([(N, n) for N, n in zip(Ns, ns)], alpha, use_R=False)
    if not np.isfinite(cap): return None
    kappa0 = ratio / cap                       # kappa0 > 1/Cap_low  => sum a > 1/kappa0 for the argmax
    A_k = {}; 
    for h, c in enumerate(arg):
        if c is not None: A_k[h] = int(c[2].split('=')[1])
    # v_h proportional to a_h with random generic perturbation, satisfying v_h kappa2 < kappa0
    a = {h: a_k(Ns[h], k) for h, k in A_k.items()}
    while True:
        w = np.array([a[h] * rng.uniform(0.9, 1.1) for h in A_k]); w /= w.sum()
        v = dict(zip(A_k, w))
        if all(v[h] / a[h] < kappa0 for h in A_k): break
    signs = {h: rng.choice([-1, 1]) for h in A_k}
    P_E = np.prod([pi_k(Ns[h], ns[h], k) for h, k in A_k.items()])
    out = dict(N=Ns, n=ns, W=[round(w,2) for w in Ws], alpha=alpha, A_k=A_k, cap=cap, kappa0=kappa0, P_E=P_E, rows=[])
    for delta in [0.0, 1e-9, 1e-6, 1e-3]:
        e = build_pop(D, A_k, v, delta, rng, signs=signs)
        ks = D.kappa_st(e); ds = D.dist(e)
        diff, se = ds
        # collapsed-point offset on constant-sample patterns: min |theta - t0| over E patterns
        patt_off = np.abs(diff[se <= 1e-3 * np.abs(diff).max() * 1e-6 + (delta > 0) * 1e-3 * delta])  # patterns with tiny SE
        row = dict(delta=delta, kappa_st=ks, in_class=bool(ks <= kappa0 + 1e-12), p_se0=D.p_se0(e) if delta == 0 else None,
                   min_offset=float(patt_off.min()) if len(patt_off) else None)
        for c in [1e2, 1e4, 1e6]:
            row[f'cov(c={c:g})'] = 1 - D.fail_prob(e, c, ds)
        out['rows'].append(row)
    return out

cfgs = [([(6, 2, 1.0), (6, 2, 1.0)], 0.2), ([(8, 3, 1.0), (6, 2, 2.0)], 0.1), ([(5, 2, 1.0), (7, 2, .5), (6, 2, 1.5)], 0.3),
        ([(8, 3, 1.0), (8, 4, 1.0)], 0.05), ([(6, 2, 1.0), (9, 3, 1.0)], 0.1), ([(7,2,1.0),(6,3,1.0),(8,2,1.0)], 0.2)]
for strata, alpha in cfgs:
    r = run(strata, alpha)
    if r is None: print('no defeating config', strata, alpha); continue
    print(f"strata(N,n,W)={strata} alpha={alpha} Cap_low={r['cap']:.3f} kappa0={r['kappa0']:.4f} A_k={r['A_k']} prod_pi={r['P_E']:.4f}  1-prod_pi={1-r['P_E']:.4f}  1-alpha={1-alpha}")
    for row in r['rows']:
        print('   delta=%g in_class=%s kappa_st=%.4f p_se0=%s min|theta-t0|=%s' % (row['delta'], row['in_class'], row['kappa_st'], row['p_se0'] and round(row['p_se0'],4), row['min_offset'] and round(row['min_offset'],4)),
              {k: round(v, 4) for k, v in row.items() if k.startswith('cov')})

# ---- equality boundary: kappa0 = 1/sum a exactly: exact two-point population is in the class, P(SE=0)>alpha (so IV needs >=)
print('\nEquality case (sum a = 1/kappa0):')
Ns, ns, Ws = [6, 6], [2, 2], [1.0, 1.0]; D = Design(Ns, ns, Ws); alpha = 0.2
cap, arg = cap_knapsack(list(zip(Ns, ns)), alpha, False); kappa0 = 1 / cap
A_k = {h: int(c[2].split('=')[1]) for h, c in enumerate(arg) if c is not None}
a = {h: a_k(Ns[h], k) for h, k in A_k.items()}; v = {h: kappa0 * a[h] for h in A_k}
e = build_pop(D, A_k, v, 0.0, rng)
print(' kappa0=%.6f kappa_st(two-point)=%.6f in class(<=)=%s ; P(SE=0)=%.4f > alpha=%s' % (kappa0, D.kappa_st(e), D.kappa_st(e) <= kappa0 + 1e-12, D.p_se0(e), alpha))
# H=1, N even, kappa0=1/N: class = balanced two-point populations; midpoint procedure (R if constant) has coverage 1
N, n = 8, 3; D1 = Design([N], [n], [1.0]); covs = []
for trial in range(200):
    x = np.zeros(N); x[:N // 2] = rng.normal() * 5 + rng.choice([-1, 1]) * 1; perm = rng.permutation(N); x = x[perm] + rng.normal()
    ix = D1.idx[0]; vals = x[ix]; mid = (vals.max(1) + vals.min(1)) / 2; const = (vals.max(1) == vals.min(1))
    theta = x.mean(); covs.append(np.mean(const | (np.abs(mid - theta) < 1e-9)))
print(' H=1 N=8 kappa0=1/N exactly: midpoint-or-R procedure coverage over 200 class members: min=%.6f (so impossibility fails at equality; Thm 1 needs strict)' % min(covs))
