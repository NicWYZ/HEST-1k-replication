import os, sys, math; sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from math import comb, lgamma, log, exp
from strat_lib import *

# ---------- (a) H=1 ----------
mism = 0; tot = 0; gaps = []; nok = 0
for N in range(4, 41):
    for n in range(2, N):
        for alpha in [0.05, 0.1, 0.2, 0.3]:
            ks = [k for k in range(1, N // 2 + 1) if pi_k(N, n, k) <= alpha]
            cl, _ = cap_knapsack([(N, n)], alpha, False); cu, _ = cap_knapsack([(N, n)], alpha, True)
            tot += 1
            if ks:
                kstar = ks[0]
                if kstar == 1:       # pi(1) <= alpha: no impossibility; Cap=-inf
                    if np.isfinite(cl): mism += 1
                    continue
                frontier = (1 - (kstar - 1) / N) / (kstar - 1)
                if abs(1 / cl - frontier) > 1e-12 or abs(1 / cu - frontier) > 1e-12: mism += 1; print('mismatch', N, n, alpha, 1/cl, 1/cu, frontier)
                else: nok += 1
            else:                    # k* does not exist: every k<=N/2 has pi>alpha
                if abs(cu - cl) > 1e-12: gaps.append((N, n, alpha, 1 / cu, 1 / cl))
print(f'(a) H=1: k* exists & kstar>=2: 1/Cap_low == 1/Cap_up == kappa2(k*-1) in {nok} cases, mismatches {mism}')
print(f'    cases with no k* (pi(floor(N/2))>alpha) where Cap_up>Cap_low (odd N, R-level): {len(gaps)}; e.g. {gaps[:2]}')

# ---------- (c) G=24, N=2000, m=4, alpha=0.1 ----------
G, N, m, alpha = 24, 2000, 4, 0.1
def lpi(k):  # exact big-integer binomials
    return log((comb(N - k, m) + comb(k, m)) / comb(N, m))
ks = np.arange(1, N // 2 + 1); cost = np.array([-lpi(int(k)) for k in ks]); capk = ks * N / (N - ks)
pi_half = exp(lpi(N // 2)); print(f'(c) pi(N/2)={pi_half:.5f} vs alpha={alpha}; 2^(1-m)={2**(1-m):.4f}; log2(2/alpha)={math.log2(2/alpha):.3f}; R_h={R_h(N, m):.5f} (<= pi(N/2))')
budget = -log(alpha)
def dp(res, round_up):
    nb = int(budget / res) + 1
    cs = np.ceil(cost / res).astype(int) if round_up else np.floor(cost / res).astype(int)
    best = np.full(nb, -np.inf); best[0] = 0.0       # best[c]= max capacity with cost units exactly <= c (monotone fill later)
    for _ in range(G):
        new = best.copy()
        for k in range(len(ks)):
            c = cs[k]
            if c >= nb: continue
            np.maximum(new[c:], best[:nb - c] + capk[k], out=new[c:])
        best = new
    best = np.maximum.accumulate(best)
    # strict product>alpha  <=> cost < budget
    cmax = int(math.ceil(budget / res)) - 1 if round_up else int(math.ceil(budget / res)) - 1
    return best[min(cmax, nb - 1)]
lo = dp(2e-4, True); hi = dp(2e-4, False)
print(f'    DP (res 2e-4): Cap_low >= {lo:.3f} (cost rounded up, conservative) ; Cap_low <= {hi:.3f} (cost rounded down)')
# exact-ish refinement: exhaustive local search around best structure: one large stratum k1 + others
best = (0, None)
for k1 in range(1, N // 2 + 1):
    c1 = cost[k1 - 1]
    if c1 >= budget: continue
    rest = budget - c1
    # remaining 23 identical strata with budget rest: capacity per cost is ~ concave? use DP-free greedy: marginal a/cost; do exact small DP at fine res
    pass
# direct exact check of the DP optimum structure using 1-big-stratum + best fill by fine DP over remaining budget
def fill(rest, Gleft, res=2e-5):
    nb = int(rest / res) + 1; cs = np.ceil(cost / res).astype(int); b = np.full(nb, -np.inf); b[0] = 0
    for _ in range(Gleft):
        nw = b.copy()
        for k in range(len(ks)):
            c = cs[k]
            if c >= nb: continue
            np.maximum(nw[c:], b[:nb - c] + capk[k], out=nw[c:])
        b = nw
    return np.maximum.accumulate(b)[-1]
res_tot = []
for k1 in [N // 2, N // 2 - 1, N // 2 - 5, N // 2 - 20, N // 2 - 50]:
    c1 = cost[k1 - 1]; rest = budget - c1 - 1e-9
    if rest <= 0: continue
    res_tot.append((k1, capk[k1 - 1] + fill(rest, G - 1, 5e-5)))
print('    big-stratum structure (k1, total capacity with rest filled optimally, res 5e-5 rounded up):', [(k, round(c, 2)) for k, c in res_tot])
Cap = max(c for _, c in res_tot)
print(f'    => Cap ~ {Cap:.2f}, frontier 1/Cap ~ {1/Cap:.4e}; DP bracket [{1/hi:.4e}, {1/lo:.4e}]')
# structure of one optimal solution via the 2-strata analysis: report best config explicitly
best_cfg = None
for k1 in range(1, N // 2 + 1):
    c1 = cost[k1 - 1]
    if c1 >= budget: continue
    cap1 = capk[k1 - 1]
    # second stratum: largest k2 with cost <= budget - c1
    ok = np.where(cost < budget - c1 - 1e-12)[0]
    cap2 = capk[ok[-1]] if len(ok) else 0
    # (3+ strata handled by DP above)
    if best_cfg is None or cap1 + cap2 > best_cfg[0]: best_cfg = (cap1 + cap2, k1, int(ks[ok[-1]]) if len(ok) else 0)
print('    best 2-stratum config (cap, k1, k2):', best_cfg, ' -> 1/cap =', 1 / best_cfg[0])

# ---------- iid normal kappa_st ----------
rs = np.random.default_rng(3); vals = []
for rep in range(20):
    e = rs.normal(size=(G, N)); d = e - e.mean(1, keepdims=True); S2 = (d**2).sum(1) / (N - 1)
    Vh = (1 - m / N) * S2 / m          # W_h equal (=1/G cancels in shares)
    V = Vh.sum(); c = (1 - m / N) * d**2 / (m * (N - 1) * V)
    vals.append(c.max())
print(f'    iid N(0,1), G={G},N={N},m={m}, equal W: kappa_st over 20 draws mean={np.mean(vals):.3e} min={np.min(vals):.3e} max={np.max(vals):.3e}')
# check against Design for a reduced version of identity
print('    1/(G*N)=%.3e (smallest possible kappa_st); single stratum 1/N=%.3e' % (1 / (G * N), 1 / N))
