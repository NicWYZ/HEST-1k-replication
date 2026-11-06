"""Round 9, track fewcluster, step I2-2: the frontier for PPI with a least-squares coefficient.

Two-piece populations z = 1_{B2} * (cos(phi) + sin(phi) * ftilde) are affine in f on B1 and on B2, so every
sample inside B1 or B2 has zero residual variance in the sample fit. For each k <= k*-1 (pi(k) > alpha) we search
B2 (|B2| = k) and phi to minimise kappa of the population least-squares residual e_hat of z on (1, f). The smallest
value found is an UPPER bound on the tuned frontier (the search over B2 is not exhaustive).
Predictions: results/round9/fewcluster/tuned/predictions_before_run.md
Outputs: results/round9/fewcluster/tuned/i22_tuned_frontier.csv, i22_coverage_check.csv
"""
import itertools, math, sys
import numpy as np, pandas as pd
from scipy.special import comb

OUT = sys.argv[1] if len(sys.argv) > 1 else 'results/round9/fewcluster/tuned'
ALPHA = 0.10
rng = np.random.default_rng(20261026)


def C(a, b):
    return comb(a, b, exact=True) if 0 <= b <= a else 0


def pi_k(G, n, k):
    return (C(G - k, n) + C(k, n)) / C(G, n)


def fixed_frontier(G, n, alpha=ALPHA):
    ks = next((k for k in range(1, G // 2 + 1) if pi_k(G, n, k) <= alpha), None)
    if ks is None:
        return None, float('nan')
    return ks, (float('inf') if ks == 1 else (1 - (ks - 1) / G) / (ks - 1))


def make_f(kind, G):
    x = rng.standard_normal(G)
    if kind == 'lognormal':
        x = np.exp(x)
    if kind == 'normal_outlier':
        x[np.argmax(x)] = x.mean() + 4 * x.std()
    return x


def kappa_rows(E):
    D = E - E.mean(-1, keepdims=True)
    ss = (D ** 2).sum(-1)
    return (D ** 2).max(-1) / np.where(ss > 0, ss, np.nan)


def search(f, k, n_random=3000, n_phi=181, n_local=300):
    G = len(f)
    ft = (f - f.mean()) / f.std()
    X = np.c_[np.ones(G), ft]
    P = np.eye(G) - X @ np.linalg.pinv(X)            # residual maker for (1, f)
    phis = np.linspace(0, np.pi, n_phi, endpoint=False)
    order = np.argsort(f)
    cands = [order[i:i + k] for i in range(G - k + 1)]
    cands += [rng.choice(G, k, replace=False) for _ in range(n_random)]

    def best_for(sets):
        M = np.zeros((len(sets), G))
        for i, s in enumerate(sets):
            M[i, s] = 1.0
        shape = np.cos(phis)[:, None] + np.sin(phis)[:, None] * ft[None, :]    # A x G
        Z = M[:, None, :] * shape[None, :, :]                                  # M x A x G
        Eh = Z @ P
        K = kappa_rows(Eh)
        K = np.where(np.isnan(K), np.inf, K)
        i, j = np.unravel_index(np.argmin(K), K.shape)
        return K[i, j], sets[i], phis[j]

    best = (np.inf, None, None)
    for start in range(0, len(cands), 500):
        r = best_for(cands[start:start + 500])
        if r[0] < best[0]:
            best = r
    cur_k, cur_s, cur_phi = best
    for _ in range(n_local):                         # single swaps
        s = list(cur_s)
        out = rng.integers(k)
        inn = rng.choice([g for g in range(G) if g not in s])
        s2 = s.copy(); s2[out] = inn
        r = best_for([np.array(s2)])
        if r[0] < cur_k:
            cur_k, cur_s, cur_phi = r
    return cur_k, np.sort(cur_s), cur_phi


rows = []
store = {}
for G in (15, 24):
    for kind in ('normal', 'lognormal', 'normal_outlier'):
        f = make_f(kind, G)
        for n in (6, 8, 10, 12):
            ks, kfix = fixed_frontier(G, n)
            _, kfix_m1 = fixed_frontier(G, n - 1)
            if ks is None:
                continue
            best = (np.inf, None, None, None)
            for k in range(max(1, 2), ks):           # k <= k*-1 has pi(k) > alpha; k = 1 is the one-cluster case
                kv, s, phi = search(f, k)
                if kv < best[0]:
                    best = (kv, k, s, phi)
            # k = 1 (a single atypical cluster) as well
            kv1, s1, phi1 = search(f, 1, n_random=G, n_local=0)
            if kv1 < best[0]:
                best = (kv1, 1, s1, phi1)
            rows.append(dict(G=G, f_kind=kind, n=n, alpha=ALPHA, k_star=ks, fixed_frontier=kfix,
                             fixed_frontier_n_minus_1=kfix_m1, tuned_frontier_upper=best[0], k_found=best[1],
                             pi_at_k_found=pi_k(G, n, best[1]), phi_found=best[3],
                             B2_found=' '.join(map(str, best[2]))))
            store[(G, kind, n)] = (f, best)
            print(G, kind, n, round(kfix, 4), round(best[0], 4), best[1], flush=True)
df = pd.DataFrame(rows)
df.to_csv(f'{OUT}/i22_tuned_frontier.csv', index=False)

# ---------- Q4: exact coverage of the tuned interval at the found population, G = 24, n = 8, normal f
G, n = 24, 8
f, (kv, k, s, phi) = store[(G, 'normal', n)]
ft = (f - f.mean()) / f.std()
z0 = np.zeros(G); z0[s] = np.cos(phi) + np.sin(phi) * ft[s]
u = rng.standard_normal(G)
subsets = np.array(list(itertools.combinations(range(G), n)))
cov_rows = []
for eps in (1e-3, 1e-5, 1e-7):
    z = z0 + eps * u
    zs, fs = z[subsets], f[subsets]
    fm, zm = fs.mean(1), zs.mean(1)
    sxx = ((fs - fm[:, None]) ** 2).sum(1); sxz = ((fs - fm[:, None]) * (zs - zm[:, None])).sum(1)
    lam = sxz / sxx
    res = zs - zm[:, None] - lam[:, None] * (fs - fm[:, None])
    s2 = (res ** 2).sum(1) / (n - 2)
    th = zm + lam * (f.mean() - fm)
    for c in (3.0, 100.0):
        hw = c * np.sqrt((1 - n / G) * s2 / n)
        cov = float(np.mean(np.abs(th - z.mean()) <= hw))
        cov_rows.append(dict(G=G, n=n, eps=eps, c=c, coverage=cov, one_minus_pi=1 - pi_k(G, n, k), k=k,
                             kappa_hat_e=kv))
pd.DataFrame(cov_rows).to_csv(f'{OUT}/i22_coverage_check.csv', index=False)
print(pd.DataFrame(cov_rows).to_string(index=False))
