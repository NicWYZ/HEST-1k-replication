"""Round 9, track fewcluster, step I2-6: exact tuned-coefficient frontier kappa_dagger(f, G, n, alpha).

kappa_dagger = inf { kappa(e) : e perp (1, f), e != 0, #{S : e_S affine in f_S} > alpha * C(G, n) }.
A sample is affine iff its points (f_g, e_g) are collinear; each affine sample lies on one maximal line, so the
count is sum_lines C(|L|, n). When only a single line can push the count above T = alpha C(G, n) (checked by
`multi_line_possible`), kappa_dagger = min over lines L with |L| = m_min of kappa_min(V_L), where
V_L = {e perp 1, f : e affine on L}. Parametrise e = a + b f on L and free values u on the k = G - m others.
kappa_min(V_L) = 1 / max{ ||e||^2 : |e_g| <= 1 }, a convex maximisation over a polytope, attained at a vertex.
On L only the rows at min f and max f bind, so a vertex fixes k of the k + 2 box rows (with signs) and solves
the two equalities sum e = 0, sum f e = 0 with them.

Usage:
  python round9_fewcluster_exact_tuned.py bench <outdir>        benchmark against the verifier's flat lattice
  python round9_fewcluster_exact_tuned.py synth <outdir>        synthetic f at the project's sizes
  python round9_fewcluster_exact_tuned.py real <c0_summaries.csv.gz> <outdir>   ACS and HEST prediction vectors
"""
import itertools, sys, time
import numpy as np, pandas as pd
from math import comb


def m_min(G, n, alpha):
    T = alpha * comb(G, n)
    return next(m for m in range(n, G + 1) if comb(m, n) > T)


def multi_line_possible(G, n, alpha):
    """Can two or more lines, each smaller than m_min, give a count above alpha C(G,n)?
    Lines pairwise share at most one point, so r lines of sizes m_i need at least sum m_i - C(r,2) points."""
    T = alpha * comb(G, n); mm = m_min(G, n, alpha)
    sizes = range(n, mm)
    for r in range(2, G // n + 3):
        for combo in itertools.combinations_with_replacement(sizes, r):
            if sum(comb(m, n) for m in combo) > T and sum(combo) - comb(r, 2) <= G:
                return True
    return False


def kappa_min_lines(f, m, block=600):
    """min over all lines L of size m of kappa_min(V_L); returns (kappa, L, e)."""
    G = len(f); k = G - m
    rows = k + 2                          # box rows: line-min, line-max, free 1..k
    pats = []
    for act in itertools.combinations(range(rows), k):
        for sg in itertools.product((-1.0, 1.0), repeat=k):
            pats.append((act, sg))
    P = len(pats)
    act_idx = np.array([p[0] for p in pats]); sgn = np.array([p[1] for p in pats])
    best = (np.inf, None, None)
    Ls = list(itertools.combinations(range(G), m))
    for st in range(0, len(Ls), block):
        Lb = np.array(Ls[st:st + block]); B = len(Lb)
        mask = np.zeros((B, G), bool); mask[np.arange(B)[:, None], Lb] = True
        fL = np.where(mask, f[None, :], np.nan)
        sL = mask.sum(1).astype(float); s1 = np.nansum(fL, 1); s2 = np.nansum(fL ** 2, 1)
        fmin = np.nanmin(fL, 1); fmax = np.nanmax(fL, 1)
        free = np.array([np.where(~mask[i])[0] for i in range(B)])          # B x k
        ff = f[free]                                                        # B x k
        # x = (a, b, u_1..u_k); equalities A x = 0
        A = np.zeros((B, 2, k + 2))
        A[:, 0, 0] = sL; A[:, 0, 1] = s1; A[:, 0, 2:] = 1.0
        A[:, 1, 0] = s1; A[:, 1, 1] = s2; A[:, 1, 2:] = ff
        R = np.zeros((B, rows, k + 2))
        R[:, 0, 0] = 1; R[:, 0, 1] = fmin; R[:, 1, 0] = 1; R[:, 1, 1] = fmax
        R[:, 2:, 2:] = np.eye(k)[None]
        Ract = R[:, act_idx, :]                                             # B x P x k x (k+2)
        M = np.concatenate([np.broadcast_to(A[:, None], (B, P, 2, k + 2)), Ract], axis=2)   # B x P x (k+2) x (k+2)
        rhs = np.concatenate([np.zeros((B, P, 2)), np.broadcast_to(sgn[None], (B, P, k))], axis=2)
        det = np.linalg.det(M); ok = np.abs(det) > 1e-10
        X = np.full((B, P, k + 2), np.nan)
        X[ok] = np.linalg.solve(M[ok], rhs[ok][..., None])[..., 0]
        a, b, u = X[..., 0], X[..., 1], X[..., 2:]
        lo = a + b * fmin[:, None]; hi = a + b * fmax[:, None]
        feas = ok & (np.abs(lo) <= 1 + 1e-9) & (np.abs(hi) <= 1 + 1e-9) & (np.abs(u).max(-1) <= 1 + 1e-9)
        # ||e||^2 = sum_L (a + b f)^2 + sum u^2
        val = sL[:, None] * a ** 2 + 2 * s1[:, None] * a * b + s2[:, None] * b ** 2 + (u ** 2).sum(-1)
        val = np.where(feas, val, -np.inf)
        per_L = val.max(1)                      # per line, the vertex maximum of ||e||^2
        kap_L = 1.0 / per_L
        il = int(np.argmin(kap_L))
        if kap_L[il] < best[0]:
            jj = int(np.argmax(val[il])); x = X[il, jj]
            e = np.empty(G); e[Lb[il]] = x[0] + x[1] * f[Lb[il]]; e[free[il]] = x[2:]
            best = (float(kap_L[il]), Lb[il], e)
    return best


def kappa(e):
    d = e - e.mean(); return float((d ** 2).max() / (d ** 2).sum())


def check_solution(f, e, n, alpha):
    """independent checks on the returned extremal e: orthogonality, kappa, affine count."""
    G = len(f); X = np.c_[np.ones(G), f]
    orth = float(np.abs(X.T @ e).max())
    S = np.array(list(itertools.combinations(range(G), n)))
    fS, eS = f[S], e[S]
    fc = fS - fS.mean(1, keepdims=True); ec = eS - eS.mean(1, keepdims=True)
    lam = (fc * ec).sum(1) / (fc ** 2).sum(1)
    rss = ((ec - lam[:, None] * fc) ** 2).sum(1)
    aff = int((rss < 1e-18 * max(1.0, (e ** 2).sum())).sum())
    return orth, kappa(e), aff, aff / comb(G, n)


def synth_f(G, kind, rng):
    if kind == 'normal':
        return rng.standard_normal(G)
    if kind == 'lognormal':
        return rng.lognormal(0, 1, G)
    x = rng.standard_normal(G); x[np.argmax(x)] = x.mean() + 4 * x.std(); return x


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'bench':
        out = sys.argv[2]; rows = []
        ver = pd.read_csv('checks_T2prime_G10n5.csv')
        for kind, seed in [('normal', 21), ('lognormal', 22), ('normal_outlier', 23)]:
            f = synth_f(10, kind, np.random.default_rng(seed))
            for m in (5, 6, 7, 8, 9):
                kv, L, e = kappa_min_lines(f, m)
                lvl = comb(m, 5)
                ref = ver[(ver.f_kind == kind) & (ver.count_level == lvl)].kappa_star_count
                orth, kk, aff, _ = check_solution(f, e, 5, 0.1)
                rows.append(dict(G=10, n=5, f_kind=kind, line_size=m, count_level=lvl, kappa_exact=kv,
                                 kappa_verifier=float(ref.iloc[0]) if len(ref) else np.nan,
                                 abs_diff=abs(kv - float(ref.iloc[0])) if len(ref) else np.nan,
                                 check_orth=orth, check_kappa=kk, check_affine_count=aff))
        df = pd.DataFrame(rows); df.to_csv(f'{out}/i26_benchmark.csv', index=False); print(df.to_string(index=False))
    elif mode == 'synth':
        out = sys.argv[2]; rows = []
        for (G, n) in [(15, 6), (15, 8), (24, 8), (24, 10), (24, 12)]:
            mm = m_min(G, n, 0.10); ml = multi_line_possible(G, n, 0.10)
            for kind in ('normal', 'lognormal', 'normal_outlier'):
                for seed in range(10):
                    f = synth_f(G, kind, np.random.default_rng(1000 + seed))
                    t0 = time.time(); kv, L, e = kappa_min_lines(f, mm)
                    orth, kk, aff, frac = check_solution(f, e, n, 0.10) if comb(G, n) <= 800000 else (np.nan,) * 4
                    rows.append(dict(G=G, n=n, f_kind=kind, seed=1000 + seed, m_min=mm, multi_line_possible=ml,
                                     kappa_dagger=kv, check_kappa=kk, check_orth=orth, check_affine_frac=frac,
                                     seconds=time.time() - t0))
                    print(G, n, kind, seed, round(kv, 4), round(time.time() - t0, 1), flush=True)
        pd.DataFrame(rows).to_csv(f'{out}/i26_synth_exact.csv', index=False)
    elif mode == 'real':
        src, out = sys.argv[2], sys.argv[3]
        MID = {'CCRCC': 8, 'INDIANA_KIDNEY': 8, 'LUNG_XENIUM': 6, 'ACS_STATES': 8}
        d = pd.read_csv(src)
        d = d[((d.encoder == 'uni_v2') & d.task.isin(['CCRCC', 'INDIANA_KIDNEY', 'LUNG_XENIUM'])) |
              ((d.task == 'ACS_STATES') & (d.encoder == 'pkg'))]
        only = sys.argv[4] if len(sys.argv) > 4 else None
        if only:
            d = d[d.task == only]
        rows = []
        for (task, gene), g in d.groupby(['task', 'gene']):
            g = g.sort_values('donor'); y = g.mean_y.to_numpy(float); f = g.mean_f.to_numpy(float); G = len(f)
            n = MID[task]; mm = m_min(G, n, 0.10); ml = multi_line_possible(G, n, 0.10)
            X = np.c_[np.ones(G), f]; r = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
            t0 = time.time(); kv, L, e = kappa_min_lines(f, mm)
            rows.append(dict(task=task, gene=gene, G=G, n=n, m_min=mm, multi_line_possible=ml,
                             kappa_dagger=kv, kappa_resid=kappa(r), beyond=kappa(r) > kv, seconds=time.time() - t0))
        t = pd.DataFrame(rows); t.to_csv(f'{out}/i26_real_exact{"_" + only if only else ""}.csv', index=False)
        print(t.groupby('task').agg(n_genes=('gene', 'size'), median_kappa_dagger=('kappa_dagger', 'median'),
                                    median_kappa_resid=('kappa_resid', 'median'), frac_beyond=('beyond', 'mean'),
                                    any_multi=('multi_line_possible', 'max')).to_string())
