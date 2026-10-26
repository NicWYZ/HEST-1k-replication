
import numpy as np, sys, time, itertools, pandas as pd
sys.path.insert(0, ".")
from tuned_lib import *
from beta_exact import *
from check_T2prime import batched_cov, worst_case_search, CS

def line_flat_basis(f, L):
    G = len(f); X = np.column_stack([np.ones(G), f])
    rows = [X.T]
    Lc = list(L)
    XL = np.column_stack([np.ones(len(Lc)), f[Lc]])
    u, _, _ = np.linalg.svd(XL, full_matrices=True)
    Qn = u[:, 2:].T                                    # (m-2) x m
    C = np.zeros((Qn.shape[0], G)); C[:, Lc] = Qn
    A = np.vstack([X.T, C])
    _, sv, Vt = np.linalg.svd(A, full_matrices=True)
    r = int((sv > 1e-9).sum())
    return Vt[r:].T                                    # G x d

def run12(seed, kind, G=12, n=5, mmin=7):
    rng = np.random.default_rng(seed); f = synth_f(G, kind, rng)
    S = all_samples(G, n); NS = len(S); Q = sample_constraints(f, S)
    out = []
    out.append((0, G - 2, *kappa_min_exact(base_basis(f))))
    starts = []
    for m in range(mmin, G):
        for L in itertools.combinations(range(G), m):
            Bs = line_flat_basis(f, L)
            if Bs.shape[1] >= 1: starts.append(Bs)
    flats = enumerate_flats(f, S, Q, starts=starts)       # all flats below the single-line flats (incl. plateau sub-flats)
    print("n flats", len(flats), flush=True)
    for cnt, d, Bs in flats:
        k, v = kappa_min_exact(Bs)
        out.append((cnt, d, k, v))
    rows = []
    cnts = sorted({c for c, d, k, v in out if c > 0})
    levels = sorted({c for c in cnts if c >= 21})
    kstar = {m: min(k for c, d, k, v in out if c >= m) for m in levels}
    rng2 = np.random.default_rng(1)
    for m in levels:
        for sign, fac in [("below", 0.97), ("above", 1.03)]:
            kappa0 = fac * kstar[m]
            beta_cnt = max((c for c, d, k, v in out if k <= kappa0), default=-1)
            alpha_cnt = beta_cnt if sign == "below" else m - 1
            E = worst_case_search(f, S, out, kappa0, rng2, nT=12, nU=4, keep=300)
            cov = batched_cov(E, f, S, CS); mincov = cov.min(0); alpha = alpha_cnt / NS
            ok = [c for c, mc in zip(CS, mincov) if mc >= 1 - alpha - 1e-12]
            rows.append(dict(statement="T2prime", G=G, n=n, f_kind=kind, NS=NS, count_level=m, side=sign, kappa_star_count=kstar[m],
                             kappa0=kappa0, beta_exact_count=beta_cnt, alpha_count=alpha_cnt,
                             predicts="tuned valid for large c" if beta_cnt <= alpha_cnt else "tuned fails for every c",
                             n_candidates=len(E), **{f"mincov_c{c:g}": mc for c, mc in zip(CS, mincov)},
                             smallest_c_on_grid_with_mincov_ge_1_minus_alpha=(min(ok) if ok else np.nan), one_minus_alpha=1 - alpha,
                             note="flat list = lattice of all flats contained in a single-line flat with >=7 collinear clusters (two-line flats with <7 on each line excluded)"))
    return rows

if __name__ == "__main__":
    allr = []
    for kind, seed in [("normal", 31)]:
        t = time.time(); allr += run12(seed, kind); print(kind, time.time() - t, flush=True)
        pd.DataFrame(allr).to_csv("checks_T2prime_G12n5_partial.csv", index=False)
