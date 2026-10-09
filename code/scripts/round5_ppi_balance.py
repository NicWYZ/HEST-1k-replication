"""Round 5 PPI, interval 2, stage E4: which clusters to label (brief section 6, E4).

Randomised designs for choosing the n_L labelled clusters of G, every unit of a labelled cluster
labelled, and the estimators and intervals under each, for many columns at once (genes on the
real tasks, populations in the simulation). Nothing computed from a label enters a design.

    D0  simple random sampling.
    D1  two per stratum: sort the clusters by the first balance variable, cut them into n_L/2
        strata of nearly equal size (numpy.array_split of the sorted order), draw two per stratum.
    D2  rejective sampling: simple random samples are drawn in order, and the first whose
        Mahalanobis distance between the labelled mean and the population mean of the balance
        variables is below the threshold is kept. The threshold is the p_a quantile of that
        distance over the candidate pool, so a fraction p_a of simple random samples is accepted.
        With the threshold at infinity the first candidate is kept, which is D0.

Candidates. Accepted draw d of D2 scans candidates k = 0, 1, ...; candidate 0 is the D0 draw d, so
D2 at threshold infinity reproduces D0 draw by draw. The candidate pool is shared by every column,
and each column with its own balance variable accepts its own first candidate.

Estimators. 'classical' (lambda = 0) and 'final' (round 4's final design estimator, rule
c_crossfit_design, round5_ppi_estimator.design_whole_clusters with the linearised term, and the
E3a correction as a second interval). Under D0 and D2 the interval is textbook_t|fpc|lin (and
|lin|xf); Fuller (2009) is the reference for using the regression estimator's ordinary variance
after rejective sampling. Under D1 the stratified estimator sum_h (G_h/G) mean_{L_h}(e_g) + cU Fbar
with variance sum_h (G_h/G)^2 (1 - 2/G_h) s_{e,h}^2 / 2 and n_L/2 degrees of freedom, less one for
every stratum of two clusters, which is labelled completely and contributes no variance.
"""
import numpy as np

import round4_ppi_estimator as E
import round5_ppi_estimator as R5

NSTAT = 100.0


def stats_arrays(z, f):
    n = np.full(z.shape, NSTAT)
    D = dict(n=n, Sz=z * n, Sf=f * n)
    D["Szz"], D["Sff"], D["Szf"] = D["Sz"] ** 2 / n, D["Sf"] ** 2 / n, D["Sz"] * D["Sf"] / n
    return D


def mahalanobis_pool(masks, X):
    """masks (K, G) bool candidate samples; X (G, ncol, k) balance variables per column (k = 1 for a
    per-column variable). Returns (K, ncol) squared Mahalanobis distances of the labelled mean from
    the population mean, with the population covariance of X over the G clusters."""
    K, G = masks.shape
    n = masks.sum(1).astype(float)
    Xc = X - X.mean(0, keepdims=True)                      # (G, ncol, k)
    ncol, k = X.shape[1], X.shape[2]
    S = np.einsum("gci,gcj->cij", Xc, Xc) / (G - 1)        # (ncol, k, k)
    Si = np.linalg.pinv(S)
    mL = np.einsum("Kg,gck->Kck", masks.astype(float), Xc) / n[:, None, None]
    return np.einsum("Kci,cij,Kcj->Kc", mL, Si, mL)


def d2_select(dist, n_draws, n_cand, p_a):
    """dist (n_draws * n_cand, ncol) in draw-major order (candidate k of draw d at d*n_cand + k).
    Returns (n_draws, ncol) index of the accepted candidate (k) per draw and column, the threshold
    per column, and the number of draws with no accepted candidate (then the last candidate)."""
    # a candidate whose distance is not finite (fewer than two valid labelled clusters) is never
    # accepted below a finite threshold and does not enter the quantile
    dist = np.where(np.isfinite(dist), dist, np.inf)
    if p_a >= 1:
        thr = np.full(dist.shape[1], np.inf)
    else:
        thr = np.nanquantile(np.where(np.isfinite(dist), dist, np.nan), p_a, axis=0)
    D = dist.reshape(n_draws, n_cand, -1)
    ok = D <= thr[None, None, :]
    first = np.where(ok.any(1), ok.argmax(1), n_cand - 1)
    return first, thr, int((~ok.any(1)).sum())


def d1_strata(x, n_L):
    """x (G, ncol) first balance variable. Returns strata (G, ncol) ints 0..n_L/2-1."""
    G, ncol = x.shape
    H = n_L // 2
    st = np.empty((G, ncol), int)
    for j in range(ncol):
        o = np.argsort(x[:, j], kind="stable")
        for h, part in enumerate(np.array_split(o, H)):
            st[part, j] = h
    return st


def d1_draw(strata, rng):
    """Two clusters per stratum per column. Returns Lm (G, ncol)."""
    G, ncol = strata.shape
    Lm = np.zeros((G, ncol), bool)
    for j in range(ncol):
        for h in np.unique(strata[:, j]):
            idx = np.flatnonzero(strata[:, j] == h)
            Lm[rng.choice(idx, 2, replace=False), j] = True
    return Lm


def estimate_srs_like(zbar, fbar, Lm, rule, seed, Am=None):
    """D0 and D2: returns dict iv -> (theta, var, df) for the estimator of `rule` ('none' or
    'c_crossfit_design'), intervals textbook_t|fpc|lin and textbook_t|fpc|lin|xf."""
    D = stats_arrays(zbar, fbar)
    lam = E.lambda_rule(rule, "donor", D, Lm, ~Lm, seed=seed)
    o = R5.design_whole_clusters("donor", zbar, fbar, Lm, lam, Am=Am, lin=True)
    ox = R5.design_whole_clusters("donor", zbar, fbar, Lm, lam, Am=Am, lin=True, xf=True)
    return {"textbook_t|fpc|lin": (o["theta"], o["var"], o["df"]),
            "textbook_t|fpc|lin|xf": (ox["theta"], ox["var"], ox["df"])}, lam


def estimate_d1(zbar, fbar, Lm, strata, rule, seed):
    """D1: the stratified estimator with two per stratum; interval 'strat_t'."""
    G, ncol = zbar.shape
    D = stats_arrays(zbar, fbar)
    lam = E.lambda_rule(rule, "donor", D, Lm, ~Lm, seed=seed)
    lamL, cU = lam["lamL"], lam["cU"]
    Fbar = fbar.mean(0)
    e = zbar - lamL * fbar + (lamL - cU[None, :]) * Fbar[None, :]
    H = strata.max() + 1
    theta = cU * Fbar
    var = np.zeros(ncol)
    dfc = np.zeros(ncol)     # degrees of freedom: strata with G_h > 2 (a stratum of two is labelled completely)
    for h in range(H):
        sh = strata == h
        Gh = sh.sum(0).astype(float)
        lh = Lm & sh
        mh = np.where(lh, e - (lamL - cU[None, :]) * Fbar[None, :], 0.0).sum(0) / 2.0   # mean of z - lam f
        theta = theta + (Gh / G) * mh
        eh = np.where(lh, e, 0.0)
        mean_e = eh.sum(0) / 2.0
        s2 = np.where(lh, (e - mean_e) ** 2, 0.0).sum(0) / 1.0
        var = var + (Gh / G) ** 2 * (1.0 - 2.0 / Gh) * s2 / 2.0
        dfc = dfc + (Gh > 2)
    return {"strat_t": (theta, var, np.maximum(dfc, 1.0))}, lam


# ---------------------------------------------------------------------------------------------
# Interval 3, stage E4b: an interval that uses the balance (docs/round5_ppi_theory.md section 3)
# ---------------------------------------------------------------------------------------------

def va_nominal(k, p_a):
    """Morgan and Rubin (2012) Theorem 3.1: v_a = P(chi2_{k+2} <= q_a) / P(chi2_k <= q_a), q_a the
    p_a quantile of chi2_k. 1.0 at p_a >= 1 (no restriction)."""
    from scipy import stats
    if p_a >= 1:
        return 1.0
    q = stats.chi2.ppf(p_a, k)
    return float(stats.chi2.cdf(q, k + 2) / p_a)


def rej_t(zbar, X, Lm, p_a):
    """The rejective-sampling interval for the classical mean under D2 (theory section 3.4).

    zbar (G, ncol) cluster values; X (G, ncol, k) balance variables (k = 1 per-column, or a shared
    design broadcast to every column); Lm (G, ncol) bool labelled clusters, n per column.
    Returns (theta, var, df): theta the classical mean of the labelled clusters, var
    (1 - n/G)(s2_res + v_a b' S_x b)/n with b and s2_res (divisor n - k - 1) from least squares of
    zbar on X with an intercept over the labelled clusters, S_x their sample covariance of X, and
    df = n - k - 1. Columns with n - k - 1 < 2 get var = nan."""
    G, ncol = zbar.shape
    k = X.shape[2]
    if X.shape[1] == 1 and ncol > 1:
        X = np.broadcast_to(X, (G, ncol, k))
    nn = Lm.sum(0)
    if not (nn == nn[0]).all():
        # columns with different numbers of labelled clusters (theta2 per-gene designs): by group
        theta, var, dfa = np.full(ncol, np.nan), np.full(ncol, np.nan), np.full(ncol, np.nan)
        for nv in np.unique(nn):
            c = np.flatnonzero(nn == nv)
            if nv < 2:
                continue
            t_, v_, d_ = rej_t(zbar[:, c], X[:, c, :], Lm[:, c], p_a)
            theta[c], var[c], dfa[c] = t_, v_, d_
        return theta, var, dfa
    n = int(nn[0])
    # gather the labelled clusters per column: idx (ncol, n)
    idx = np.argsort(~Lm, axis=0, kind="stable")[:n].T
    cols = np.arange(ncol)[:, None]
    zl = zbar[idx, cols]                         # (ncol, n)
    xl = X[idx, cols, :]                         # (ncol, n, k)
    theta = zl.mean(1)
    zc = zl - theta[:, None]
    xc = xl - xl.mean(1, keepdims=True)
    Sxx = np.einsum("cni,cnj->cij", xc, xc)      # (ncol, k, k)
    Sxz = np.einsum("cni,cn->ci", xc, zc)
    df = n - k - 1
    with np.errstate(invalid="ignore", divide="ignore"):
        b = np.linalg.solve(Sxx + 0.0, Sxz[:, :, None])[:, :, 0] if df >= 1 else np.full((ncol, k), np.nan)
        res = zc - np.einsum("cni,ci->cn", xc, b)
        s2 = (res ** 2).sum(1) / df if df >= 1 else np.full(ncol, np.nan)
        Sx = Sxx / (n - 1)
        quad = np.einsum("ci,cij,cj->c", b, Sx, b)
        var = (1.0 - n / G) * (s2 + va_nominal(k, p_a) * quad) / n
    if df < 2:
        var = np.full(ncol, np.nan)
    return theta, var, np.full(ncol, float(df))


def perm_cluster_variable(f_ref, genes, seed_prefix):
    """The cluster-level null control: f_ref (G, ng), the reference arm's own fbar_g over the valid
    clusters, permuted across clusters with one crc32 seed per gene ('<seed_prefix>|<gene>'), so
    each gene keeps its distribution over clusters and loses any link to a cluster's own weights.
    Returns (G, ng, 1)."""
    import zlib
    G, ng = f_ref.shape
    out = np.empty_like(f_ref)
    for j, g in enumerate(genes):
        p = np.random.default_rng(zlib.crc32(f"{seed_prefix}|{g}".encode())).permutation(G)
        out[:, j] = f_ref[p, j]
    return out[:, :, None]


def first_accepted(dist_batch, thr, k0, done):
    """dist_batch (K, ncol) distances of candidates k0..k0+K-1 of one draw; thr (ncol,); done (ncol,)
    bool columns already accepted. Returns (kacc (ncol,) int or -1, done updated)."""
    ok = dist_batch <= thr[None, :]
    has = ok.any(0) & ~done
    kacc = np.full(dist_batch.shape[1], -1)
    kacc[has] = k0 + ok[:, has].argmax(0)
    return kacc, done | has
