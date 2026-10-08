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
with variance sum_h (G_h/G)^2 (1 - 2/G_h) s_{e,h}^2 / 2 and n_L/2 degrees of freedom.
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
    thr = np.full(dist.shape[1], np.inf) if p_a >= 1 else np.quantile(dist, p_a, axis=0)
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
    return {"strat_t": (theta, var, float(H))}, lam
