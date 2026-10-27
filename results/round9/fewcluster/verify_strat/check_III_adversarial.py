"""(III): at kappa0 just below 1/Cap_up search adversarially for max over the class of c_needed(e)
(smallest c with exact coverage of T+-c SE >= 1-alpha). Also: just above 1/Cap_low the same search diverges."""
import os, sys, math, time; sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from strat_lib import *
rng = np.random.default_rng(11)

def rand_pop(D, rng, kmax_groups=4):
    shapes = []
    for h in range(D.H):
        N = D.Ns[h]
        if rng.random() < 0.55:                      # two-point like (+ optional jitter)
            k = int(rng.integers(1, N // 2 + 1)); x = np.zeros(N); x[:k] = 1.0; rng.shuffle(x)
        else:
            g = int(rng.integers(1, kmax_groups + 1)); lab = rng.integers(0, g, N); x = rng.normal(size=g)[lab] * 3
        dl = 10 ** (-rng.uniform(0, 7)) if rng.random() < 0.7 else 0.0
        shapes.append(x + dl * rng.normal(size=N))
    shapes = [x if np.ptp(x) > 1e-10 else np.full_like(x, x[0]) for x in shapes]
    # choose stratum scales so that v_h ~ 1/kappa_h (best use of capacity), randomly perturbed
    kap = np.array([D.kappa_h(x) if np.ptp(x) > 1e-10 else 0.0 for x in shapes]); Vh1 = np.where(kap > 0, D.V_h(shapes), 0.0)
    w = np.where(kap > 0, 1.0 / np.where(kap > 0, kap, 1) * rng.uniform(0.5, 1.5, D.H) ** rng.choice([0, 1]) , 0.0)
    if w.sum() == 0: return shapes
    if rng.random() < 0.15: w = w * (rng.random(D.H) < 0.7)   # drop some strata (constant)
    if w.sum() == 0: return shapes
    v = w / w.sum()
    out = []
    for h in range(D.H):
        x = shapes[h]
        if v[h] <= 0 or Vh1[h] <= 0: out.append(np.zeros_like(x) + (rng.normal() if rng.random() < .5 else 0)); continue
        out.append(x * math.sqrt(v[h] / Vh1[h]))
    return out

def search(D, alpha, kappa0, budget_s=25, climb=True):
    best = (0.0, None); t0 = time.time(); nin = 0; maxp0 = 0.0
    cands = []
    while time.time() - t0 < budget_s:
        e = rand_pop(D, rng)
        if all(np.ptp(x) == 0 for x in e): continue      # V = 0 exactly (roundoff V>0 is spurious)
        ks = D.kappa_st(e)
        if ks is None or ks > kappa0: continue
        nin += 1
        ds = D.dist(e); c = D.c_needed(e, alpha, ds); maxp0 = max(maxp0, D.p_se0(e))
        cands.append((c, e))
        if c > best[0]: best = (c, e)
    # local hill-climb from the 10 worst
    if climb:
        cands.sort(key=lambda t: -t[0] if np.isfinite(t[0]) else -1e300)
        for c0, e0 in cands[:10]:
            cur, ecur = c0, e0
            for it in range(600):
                en = [x + (10 ** (-rng.uniform(2, 8))) * rng.normal(size=x.size) * (np.abs(x).max() + 1e-12) if rng.random() < .5 else x.copy() for x in ecur]
                if rng.random() < .3: h = rng.integers(D.H); en[h] = en[h] * math.exp(rng.normal() * .3)
                if all(np.ptp(x) == 0 for x in en): continue
                ks = D.kappa_st(en)
                if ks is None or ks > kappa0: continue
                c = D.c_needed(en, alpha)
                if c >= cur: cur, ecur = c, en
            nin += 1
            if cur > best[0]: best = (cur, ecur)
    return best, nin, maxp0

configs = [([(6, 2), (6, 2)], 0.2), ([(7, 2), (7, 2)], 0.3), ([(8, 3), (6, 2)], 0.1), ([(5, 2), (7, 2), (6, 2)], 0.3), ([(6, 2), (6, 3)], 0.15)]
for strata, alpha in configs:
    Ns = [s[0] for s in strata]; ns = [s[1] for s in strata]
    D = Design(Ns, ns, [1.0] * len(Ns))
    cu, _ = cap_knapsack(strata, alpha, True); cl, _ = cap_knapsack(strata, alpha, False)
    print(f'strata={strata} alpha={alpha} Cap_low={cl:.3f} Cap_up={cu:.3f} sumN={sum(Ns)} -> frontier in [{1/cu:.4f},{1/cl:.4f}]')
    if 1 / cu <= 1 / sum(Ns) + 1e-12: print('   class empty below 1/Cap_up (Cap_up = sum N): possibility vacuous; skipped'); continue
    for lab, kap0 in [('0.99/Cap_up', 0.99 / cu), ('0.80/Cap_up', 0.8 / cu), ('1.05/Cap_low', 1.05 / cl)]:
        (c, e), nin, maxp0 = search(D, alpha, kap0, budget_s=12)
        print(f'   kappa0={lab}={kap0:.4f}: class members tried {nin}, max P(SE=0) seen={maxp0:.4f} (alpha={alpha}); worst c_needed found = {c:.4g}')
