
import numpy as np, sys, itertools, pandas as pd
sys.path.insert(0, ".")
from tuned_lib import *
rng = np.random.default_rng(777)
rows = []; detail = []

def best_two_piece(f, k, nphi=181):
    G = len(f); H = hat_matrix(f)
    phis = np.linspace(0, np.pi, nphi, endpoint=False)
    best = (np.inf, None, None)
    for B in itertools.combinations(range(G), k):
        B = list(B)
        ind = np.zeros(G); ind[B] = 1
        v1 = ind - H @ ind; w = ind * f; v2 = w - H @ w
        E = np.cos(phis)[:, None] * v1 + np.sin(phis)[:, None] * v2   # nphi x G
        ss = (E**2).sum(1)
        with np.errstate(divide="ignore", invalid="ignore"):
            kap = (E**2).max(1) / ss
        kap[ss < 1e-12] = np.inf
        i = np.argmin(kap)
        if kap[i] < best[0]: best = (kap[i], B, phis[i])
    return best

cfgs = [(8,4,0.05),(10,4,0.05),(10,5,0.05),(12,5,0.05),(12,5,0.10)]
for (G, n, alpha) in cfgs:
    S = all_samples(G, n); NS = len(S)
    for kind in ["normal", "lognormal", "normal_outlier"]:
        f = synth_f(G, kind, rng)
        ks = [k for k in range(1, G) if pi_k(G, n, k) > alpha]
        # choose the k in ks with smallest achievable kappa (grid search over B, phi)
        res = {k: best_two_piece(f, k) for k in ks}
        k = min(res, key=lambda q: res[q][0]); kap, B, phi = res[k]
        z = np.zeros(G); z[B] = np.cos(phi) + np.sin(phi) * f[B]
        theta = z.mean(); kappa0 = kap * 1.05
        th, rss, _ = sample_stats(f, z, S)
        aff = affine_mask(f, z, S); W = aff & (np.abs(th - theta) > 1e-9)
        PW = W.mean()
        # kappa(e_hat(z_eps)) < kappa0 for eps used; coverage for several c and eps; several random x
        out = {}
        for c in [1.96, 10.0, 100.0, 1e4]:
            for eps in [1.0, 1e-1, 1e-2, 1e-4, 1e-6]:
                cov = []; kmax = 0
                for t in range(8):
                    x = rng.standard_normal(G) * rng.choice([1, 10])
                    ze = z + eps * x
                    cov.append(coverage(f, ze, S, c)); kmax = max(kmax, kappa(e_hat(ze, f)))
                out[(c, eps)] = (max(cov), kmax)
        eps_small_ok = all(out[(c, 1e-6)][0] <= 1 - PW + 1e-12 for c in [1.96, 10.0, 100.0, 1e4])
        inK = all(out[(c, e)][1] < kappa0 for c in [1.96] for e in [1e-4, 1e-6])
        for (c, eps), (cv, km) in out.items():
            detail.append(dict(G=G, n=n, alpha=alpha, f_kind=kind, k=k, B="|".join(map(str, B)), phi=phi, c=c, eps=eps,
                               max_cov_over_8x=cv, max_kappa=km, one_minus_PW=1 - PW))
        rows.append(dict(statement="T1prime", test=f"tuned coverage at z*+eps x, eps=1e-6, c<=1e4 <= 1-P(W) (max over 8 random x)",
                         G=G, n=n, alpha=alpha, f_kind=kind, k=k, kappa_zstar=kap, kappa0=kappa0, P_W_enumerated=PW, pi_k=pi_k(G, n, k),
                         coverage_eps1e6_c100=out[(100.0, 1e-6)][0], one_minus_PW=1 - PW, passed=bool(eps_small_ok and inK and abs(PW - pi_k(G, n, k)) < 1e-12)))
        print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv("checks_T1prime.csv", index=False)
pd.DataFrame(detail).to_csv("checks_T1prime_detail.csv", index=False)
