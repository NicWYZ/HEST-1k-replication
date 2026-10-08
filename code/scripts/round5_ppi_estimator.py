"""Round 5 PPI track, what this round adds to the estimator.

Imports the round-4 modules unmodified (round4_ppi_estimator.py md5 d79e69aa65800b9d24de556e019a0c64).

1. design_whole_clusters: the design-target difference estimator and its linearised variance when
   every unit of a labelled cluster is labelled (brief section 2.3). It is the m = all case of
   round4_ppi_q2_masking.textbook_two_stage, written on the cluster contributions directly so
   that a simulation can call it without unit-level data. E1 acceptance check 1 compares the two.
2. oracle_lambda: the lambda dict of a fixed coefficient, the population's own least-squares slope.
3. johnson_interval: Johnson's (1978) skewness-adjusted t interval applied to the contributions
   e_g, a diagnostic of E1 capped at half a day.
"""
import numpy as np
from scipy import stats

import round4_ppi_estimator as E  # noqa: F401  (imported unmodified; lambda_rule is called from here)

ALPHA = E.ALPHA


def contributions_textbook(pop, zbar, fbar, M=None):
    """The (a_g, b_g) of the textbook form: cluster means donor-weighted, cluster totals
    spot-weighted (M the cluster sizes, (G,))."""
    if pop == "donor":
        return zbar, fbar
    return zbar * M[:, None], fbar * M[:, None]


def design_whole_clusters(pop, zbar, fbar, Lm, lam, Am=None, M=None, lin=True):
    """Design-target estimator with every unit of each labelled cluster labelled.

    zbar, fbar: (G, ncol) cluster means of z and f over all units. Lm: (G, ncol) labelled mask.
    lam: dict with lamL (G, ncol) and cU (ncol,), as returned by round4 lambda_rule. Am: the
    population mask (default all True). M: (G,) cluster sizes, needed for pop='spot'.

    Donor-weighted, with Fbar the population mean of fbar over the G clusters,
        theta = cU Fbar + mean_{g in L}(zbar_g - lamL_g fbar_g)
        e_g   = zbar_g - lamL_g fbar_g + (lamL_g - cU) Fbar        (lin=True)
        var   = (1 - n_L/G) s_e^2 / n_L,   df = n_L - 1.
    Spot-weighted, with totals Z_g = M_g zbar_g, F_g = M_g fbar_g and N the population size,
        theta = cU Ftot/N + (G/(N n_L)) sum_L (Z_g - lamL_g F_g)
        e_g   = (G/N)(Z_g - lamL_g F_g + (lamL_g - cU) (Ftot/N) M_g).
    Returns dict(theta, var, df, e) with e zero outside L.
    """
    if Am is None:
        Am = np.ones_like(Lm, dtype=bool)
    lamL, cU = lam["lamL"], lam["cU"]
    GL = Lm.sum(0).astype(float)
    G = Am.sum(0).astype(float)
    if pop == "spot":
        Mc = M[:, None]
        N = np.where(Am, Mc, 0.0).sum(0)
        Ftot = np.where(Am, fbar * Mc, 0.0).sum(0)
        R = np.where(Lm, zbar * Mc - lamL * fbar * Mc, 0.0)
        theta = cU * Ftot / N + (G / (N * GL)) * R.sum(0)
        e = np.where(Lm, (G / N)[None, :] * R, 0.0)
        if lin:
            e = np.where(Lm, e + (G / N)[None, :] * (Ftot / N)[None, :] * Mc * (lamL - cU[None, :]), 0.0)
    else:
        Fbar = np.where(Am, fbar, 0.0).sum(0) / G
        R = np.where(Lm, zbar - lamL * fbar, 0.0)
        theta = cU * Fbar + R.sum(0) / GL
        e = R
        if lin:
            e = np.where(Lm, e + Fbar[None, :] * (lamL - cU[None, :]), 0.0)
    em = e.sum(0) / GL
    s2 = np.where(Lm, (e - em) ** 2, 0.0).sum(0) / (GL - 1.0)
    var = (1.0 - GL / G) * s2 / GL
    return dict(theta=theta, var=var, df=GL - 1.0, e=e)


def oracle_lambda(pop, zbar, fbar, Lm, Am=None, M=None):
    """Fixed coefficient: the finite-population least-squares slope of a_g on b_g over all G
    clusters (unclipped), the same value on every labelled cluster, so cU equals it."""
    if Am is None:
        Am = np.ones_like(Lm, dtype=bool)
    a, b = contributions_textbook(pop, zbar, fbar, M)
    k = Am.sum(0).astype(float)
    am, bm = np.where(Am, a, 0).sum(0) / k, np.where(Am, b, 0).sum(0) / k
    sbb = np.where(Am, (b - bm) ** 2, 0).sum(0)
    sab = np.where(Am, (a - am) * (b - bm), 0).sum(0)
    lamv = np.where(sbb > 0, sab / np.where(sbb > 0, sbb, 1.0), 0.0)
    return dict(lamL=np.broadcast_to(lamv, Lm.shape).copy(), cU=lamv.copy(), lam=lamv, basis="oracle_fixed")


def population_rectifier_var(pop, zbar, fbar, lamv, Am=None, M=None):
    """S_r^2 over the G clusters of the textbook contributions at a fixed coefficient lamv,
    so that (1 - n_L/G) S_r^2 / n_L is the exact design variance of the estimator (spot-weighted
    on the (G/N) scale)."""
    if Am is None:
        Am = np.ones_like(zbar, dtype=bool)
    a, b = contributions_textbook(pop, zbar, fbar, M)
    r = a - lamv[None, :] * b
    if pop == "spot":
        N = np.where(Am, M[:, None], 0.0).sum(0)
        G = Am.sum(0).astype(float)
        r = (G / N)[None, :] * r
    k = Am.sum(0).astype(float)
    rm = np.where(Am, r, 0).sum(0) / k
    return np.where(Am, (r - rm) ** 2, 0).sum(0) / (k - 1.0)


def t_interval(theta, var, df, alpha=ALPHA):
    q = stats.t.ppf(1 - alpha / 2, df)
    se = np.sqrt(np.maximum(var, 0.0))
    return theta - q * se, theta + q * se


def johnson_interval(e, Lm, theta, var, df, alpha=ALPHA):
    """Johnson (1978) modified t for a mean, applied to the contributions e_g of the labelled
    clusters. With d = thetahat - theta, s^2 the variance estimate (finite-population factor
    included) and mu3 the sample third central moment of e over L,
        t1 = (d + mu3 / (6 s_e^2 n) + mu3 / (3 s_e^4) d^2) / sqrt(var)
    where s_e^2 is the sample variance of e. The interval is {theta : |t1| <= t_{df}}, solved as
    the root of the quadratic in d nearest zero; where the quadratic has no real root the linear
    form (b = 0) is used. Returns (lo, hi)."""
    n = Lm.sum(0).astype(float)
    em = np.where(Lm, e, 0).sum(0) / n
    dev = np.where(Lm, e - em, 0.0)
    s2e = (dev ** 2).sum(0) / (n - 1.0)
    mu3 = (dev ** 3).sum(0) * n / ((n - 1.0) * (n - 2.0))
    a = mu3 / (6.0 * s2e * n)
    b = mu3 / (3.0 * s2e ** 2)
    q = stats.t.ppf(1 - alpha / 2, df)
    se = np.sqrt(np.maximum(var, 0.0))
    out = []
    for c in (q * se, -q * se):
        # b d^2 + d + a - c = 0, root nearest zero
        disc = 1.0 - 4.0 * b * (a - c)
        with np.errstate(invalid="ignore", divide="ignore"):
            root = (-1.0 + np.sqrt(np.maximum(disc, 0.0))) / (2.0 * b)
        lin = c - a
        d = np.where((np.abs(b) > 1e-14) & (disc >= 0), root, lin)
        out.append(d)
    d_hi, d_lo = out          # d = thetahat - theta; |t1| <= q gives d in [d_lo, d_hi]
    return theta - d_hi, theta - d_lo
