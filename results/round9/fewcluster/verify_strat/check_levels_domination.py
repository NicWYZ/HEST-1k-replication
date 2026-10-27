"""(IV) core lemma: for every nonconstant single-stratum population, (P(const sample), 1/kappa_h) is dominated
coordinatewise by a level (pi(k),a(k)) (k<=N/2) or (R,N). Exhaustive over multiplicity patterns (partitions of N),
kappa_min(partition) by multistart SLSQP (infimum over values)."""
import math
from math import comb
import numpy as np
from scipy.optimize import minimize
import os, sys; sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from strat_lib import *
rng = np.random.default_rng(1)
def partitions(N, maxpart=None):
    if maxpart is None: maxpart = N
    if N == 0: yield (); return
    for m in range(min(N, maxpart), 0, -1):
        for rest in partitions(N - m, m): yield (m,) + rest
_cache = {}
def kappa_min(ms, tries=25):
    if ms in _cache: return _cache[ms]
    m_ = np.array(ms, float); g = len(m_); N = m_.sum()
    if g == 2:
        r = (1 - min(m_) / N) / min(m_); _cache[ms] = r; return r
    def share_max(x):
        xb = (m_ * x).sum() / N; d2 = (x - xb)**2; return d2.max() / (m_ * d2).sum()
    best = np.inf
    for _ in range(tries):
        x0 = rng.normal(size=g); xb = (m_ * x0).sum() / N; x0 = (x0 - xb) / math.sqrt((m_ * (x0 - xb)**2).sum())
        ci = lambda z: z[g] - (z[:g] - (m_ * z[:g]).sum() / N)**2
        ce = lambda z: (m_ * (z[:g] - (m_ * z[:g]).sum() / N)**2).sum() - 1
        r = minimize(lambda z: z[g], np.append(x0, (x0**2).max()), constraints=[{'type': 'ineq', 'fun': ci}, {'type': 'eq', 'fun': ce}], method='SLSQP', options={'maxiter': 300, 'ftol': 1e-14})
        if np.isfinite(r.x).all(): best = min(best, share_max(r.x[:g]))
    _cache[ms] = best; return best
if __name__ == '__main__':
    viol = []; checked = 0; Rviol = []; mono = []
    for N in range(4, 11):
        parts = [p for p in partitions(N) if len(p) > 1]
        for n in range(2, N):
            pis = [pi_k(N, n, k) for k in range(1, N // 2 + 1)]
            if any(pis[i] < pis[i + 1] - 1e-15 for i in range(len(pis) - 1)): mono.append((N, n))
            if R_h(N, n) > pis[-1] + 1e-15: Rviol.append((N, n))
            L = levels(N, n, True)
            for p in parts:
                pc = sum(comb(m, n) for m in p) / comb(N, n); cap = 1 / kappa_min(p)
                checked += 1
                if not any(l[0] >= pc - 1e-12 and l[1] >= cap - 1e-7 for l in L): viol.append((N, n, p, pc, cap))
    print('partitions x n checked', checked, '| domination violations', len(viol), viol[:3])
    print('pi(k) non-monotone cases', mono, '| R > pi(floor(N/2)) cases', Rviol)
    nd = [(N, n) for N in range(4, 41) for n in range(2, N)
          if not any(pi_k(N, n, k) >= R_h(N, n) - 1e-15 and a_k(N, k) >= N - 1e-12 for k in range(1, N // 2 + 1))]
    print('R-level not dominated by two-point levels: #', len(nd), 'all odd N:', all(N % 2 for N, n in nd))
