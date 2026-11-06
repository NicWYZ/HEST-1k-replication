
import numpy as np, sys, time, itertools, pandas as pd
from math import comb
sys.path.insert(0, ".")
from tuned_lib import *
from beta_exact import kappa_min_exact

def two_piece_scan(f, k, nphi=181):
    """for all |B|=k and phi grid: kappa(e_hat(1_B (cos phi + sin phi f))) ; return (kappa_min_per_B, phi_per_B, combos)"""
    G = len(f); H = hat_matrix(f)
    combos = np.array(list(itertools.combinations(range(G), k)))
    ind = np.zeros((len(combos), G)); ind[np.arange(len(combos))[:, None], combos] = 1
    HB1 = H[:, combos].sum(2).T                                    # nB x G : H @ 1_B
    HBf = np.einsum("gbk,bk->bg", H[:, combos], f[combos])        # H @ (1_B f)
    V1 = ind - HB1; V2 = ind * f - HBf
    phis = np.linspace(0, np.pi, nphi, endpoint=False)
    bestk = np.full(len(combos), np.inf); bestphi = np.zeros(len(combos))
    for ph in phis:
        E = np.cos(ph) * V1 + np.sin(ph) * V2
        ss = (E**2).sum(1)
        with np.errstate(divide="ignore", invalid="ignore"):
            kap = (E**2).max(1) / ss
        kap[ss < 1e-10] = np.inf
        m = kap < bestk; bestk[m] = kap[m]; bestphi[m] = ph
    return bestk, bestphi, combos

if __name__ == "__main__":
    G, n, alpha = 24, 8, 0.10
    ks = [k for k in range(1, G // 2 + 1) if pi_k(G, n, k) > alpha]
    print("valid k (<=G/2):", ks, [round(pi_k(G, n, k), 4) for k in ks], flush=True)
    rows = []; chosen = None
    for seed in range(100, 112):
        rng = np.random.default_rng(seed); f = rng.standard_normal(G)
        res = {}
        for k in ks:
            bk, bp, cb = two_piece_scan(f, k)
            i = np.argmin(bk); res[k] = (bk[i], list(cb[i]), bp[i])
        kbest = min(res, key=lambda q: res[q][0])
        rows.append(dict(seed=seed, **{f"kmin_two_piece_k{k}": res[k][0] for k in ks}, k_best=kbest, kappa_best=res[kbest][0]))
        print(rows[-1], flush=True)
        if chosen is None and res[5][0] < 0.10:
            chosen = (seed, f, res[5])
    pd.DataFrame(rows).to_csv("checks_numbers_G24_twopiece_scan.csv", index=False)
    seed, f, (kap5, B, phi) = chosen
    print("chosen seed", seed, "kappa", kap5, "B", B, "phi", phi, flush=True)
    z = np.zeros(G); z[B] = np.cos(phi) + np.sin(phi) * f[B]
    theta = z.mean(); S = all_samples(G, n); print("NS", len(S), flush=True)
    th, rss, _ = sample_stats(f, z, S)
    aff = affine_mask(f, z, S); W = aff & (np.abs(th - theta) > 1e-9)
    print("P(W) enumerated", W.mean(), "pi(5)", pi_k(G, n, 5), "n aff", aff.sum(), "W", W.sum(), flush=True)
    out = []
    rng = np.random.default_rng(1)
    for t in range(2):
        u = rng.standard_normal(G)
        for eps in [1.0, 1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6]:
            ze = z + eps * u
            ke = kappa(e_hat(ze, f))
            for c in [1.96, 100.0, 1e4]:
                cov = coverage(f, ze, S, c)
                out.append(dict(u_id=t, eps=eps, c=c, coverage=cov, kappa_e_hat=ke, one_minus_pi5=1 - pi_k(G, n, 5), one_minus_PW=1 - W.mean()))
        print(t, flush=True)
    o = pd.DataFrame(out); o.to_csv("checks_numbers_G24_coverage.csv", index=False)
    print(o.to_string())
    # free-u refinement (exact vertex enumeration in d=5) for the best 40 two-piece B at k=5
    bk, bp, cb = two_piece_scan(f, 5)
    top = np.argsort(bk)[:40]; H = hat_matrix(f); free = []
    for i in top:
        B_ = cb[i]; ind = np.zeros(G); ind[B_] = 1
        M = np.eye(G)[:, B_] - H[:, B_]                  # (I-H) 1_B columns, G x 5
        q, r_ = np.linalg.qr(M); kk, v = kappa_min_exact(q)
        free.append((bk[i], kk))
    free = np.array(free)
    print("top-40 B: two-piece kappa min", free[:, 0].min(), " free-u exact kappa min", free[:, 1].min(), flush=True)
    pd.DataFrame(free, columns=["two_piece_kappa", "free_u_kappa_exact"]).to_csv("checks_numbers_G24_freeu_top40.csv", index=False)
