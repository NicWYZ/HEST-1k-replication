
import numpy as np, sys, time, pandas as pd
sys.path.insert(0, ".")
from tuned_lib import *
from beta_exact import *

CS = np.array([1.96, 5, 10, 30, 100, 300, 1e3, 1e4, 1e6, 1e8])

def batched_cov(E, f, S, cs, chunk=20000):
    """coverage of tuned interval at theta=0 for each row of E (m x G), each c in cs -> (m, len(cs))"""
    G = len(f); n = S.shape[1]
    fS = f[S]; fb = fS.mean(1); fc = fS - fb[:, None]; Sxx = (fc**2).sum(1); dF = f.mean() - fb
    out = np.empty((len(E), len(cs)))
    for a in range(0, len(E), chunk):
        e = E[a:a + chunk]
        zS = e[:, S]                              # m x NS x n
        zb = zS.mean(2)
        lam = (fc[None] * (zS - zb[..., None])).sum(2) / Sxx[None]
        th = zb + lam * dF[None]
        res = zS - zb[..., None] - lam[..., None] * fc[None]
        rss = (res**2).sum(2)
        hw = np.sqrt((1 - n / G) * rss / (n - 2) / n)
        # relative tolerance for the exact-zero case: scale by max|e| per row
        sc = np.abs(e).max(1)[:, None]
        for j, c in enumerate(cs):
            out[a:a + chunk, j] = (np.abs(th) <= c * hw + 1e-13 * sc).mean(1)
    return out

def worst_case_search(f, S, flats_out, kappa0, rng, nT=12, nU=6, keep=600):
    G = len(f); B0 = base_basis(f)
    feas = [(cnt, d, kmin, v) for (cnt, d, kmin, v) in flats_out if kmin <= kappa0]
    feas.sort(key=lambda t: -t[0]); feas = feas[:keep]
    ts = np.logspace(-10, -0.3, nT)
    E = []
    for cnt, d, kmin, v in feas:
        v = v / np.linalg.norm(v)
        E.append(v)
        for _ in range(nU):
            u = B0 @ rng.standard_normal(B0.shape[1]); u /= np.linalg.norm(u)
            for t in ts:
                E.append(v + t * u)
    E = np.array(E)
    kap = ((E**2).max(1)) / (E**2).sum(1)
    E = E[kap <= kappa0 * (1 + 1e-12)]
    return E

def run(G, n, seed, kind, rng_seed=0):
    rng = np.random.default_rng(seed); f = synth_f(G, kind, rng)
    S = all_samples(G, n); NS = len(S); Q = sample_constraints(f, S)
    flats = enumerate_flats(f, S, Q)
    out, _, _ = beta_curve(f, n, flats, S, Q)
    rows = []
    cnts = sorted({c for c, d, k, v in out if c > 0})
    kstar = {m: min(k for c, d, k, v in out if c >= m) for m in cnts}
    rng2 = np.random.default_rng(rng_seed)
    for m in cnts:
        for sign, fac in [("below", 0.97), ("above", 1.03)]:
            kappa0 = fac * kstar[m]
            beta_cnt = max((c for c, d, k, v in out if k <= kappa0), default=-1)
            if sign == "below": alpha_cnt = beta_cnt          # tight: alpha*NS = beta*NS
            else: alpha_cnt = m - 1                           # alpha just below the structure's count
            if beta_cnt < 0: continue
            E = worst_case_search(f, S, out, kappa0, rng2)
            cov = batched_cov(E, f, S, CS)
            mincov = cov.min(0)
            alpha = alpha_cnt / NS
            ok_cs = [c for c, mc in zip(CS, mincov) if mc >= 1 - alpha - 1e-12]
            rows.append(dict(statement="T2prime", G=G, n=n, f_kind=kind, NS=NS, count_level=m, side=sign,
                             kappa_star_count=kstar[m], kappa0=kappa0, beta_exact_count=beta_cnt, alpha_count=alpha_cnt,
                             predicts="tuned valid for large c" if beta_cnt <= alpha_cnt else "tuned fails for every c (if theta_hat_S!=0 on affine S)",
                             n_candidates=len(E), **{f"mincov_c{c:g}": mc for c, mc in zip(CS, mincov)},
                             smallest_c_on_grid_with_mincov_ge_1_minus_alpha=(min(ok_cs) if ok_cs else np.nan),
                             one_minus_alpha=1 - alpha))
    return rows

if __name__ == "__main__":
    allrows = []
    for (G, n) in [(8, 4)]:
        for kind, seed in [("normal", 11), ("lognormal", 12), ("normal_outlier", 13)]:
            t = time.time(); r = run(G, n, seed, kind); allrows += r; print(G, n, kind, len(r), time.time() - t, flush=True)
    pd.DataFrame(allrows).to_csv("checks_T2prime_G8.csv", index=False)
