"""Round 10, track final-runs, stage F1.1: the estimator module.

Design target: the mean theta = (1/G) sum_g z_g over a fixed population U of G clusters, z_g a cluster value and f_g
the cluster's mean prediction. n clusters are labelled by simple random sampling without replacement. Every function
is vectorised over draws: index arrays have shape (R, n) (or (R, n_k) per fold) and return arrays of shape (R,).

Entries.
  classical(z, f, L)                     labelled mean, (1 - n/G) s_z^2 / n, t_{n-1}.
  difference_fixed(z, f, L, c=1.0)       difference estimator with a preassigned coefficient c (Cochran Thm 7.1;
                                         Sarndal et al. Result 6.3.1), (1 - n/G) s_{z-cf}^2 / n, t_{n-1}.
  crossfit(z, f, folds, rule)            the K-fold cross-fitted difference estimator in Mickey's (1959) form
                                         (ledger decisions section 1.1; Williams 1961 for K = 2 and even n). For fold k
                                         the coefficient b_{-k} is fitted on the labelled clusters outside fold k, those
                                         clusters are kept as observed, and the rest of U is estimated by the difference
                                         estimator on fold k. Returns theta = mean_k t_k and the variances
                                           V_w    = (1 - n/G) s_w^2 / n, s_w^2 pooled within folds on n - K df (round 9);
                                           V      = mean_k s_k^2 - mean_k (t_k - theta)^2 (exactly unbiased; Mickey 4.4);
                                           V_max  = max(V, V_w);
                                           V_cons = mean_k s_k^2,
                                         each with and without the finite-population factors (fpc=False drops them).
  fold_r9(z, f, A, B, U, ua, lA, lB)     round 9's fold-wise form FOLD (unlabelled clusters split between folds), for
                                         the anchor only.
  regime_b_formC(T, sel, seed, coef)  form C for regime B with the coefficient fixed at 1, cross-fitted, or 0,
                                         on round 5's two-level code (round5_ppi_twolevel.py).
  bh_parts / bh_variants(z, f, L)        Broska and Howes's interval (bh) and the small-sample variants bh_t and
                                         bh_t_fpc of round 7 (code/scripts/round7_ppi_s2_comparators.py, bh3_parts and
                                         bh_variants), with the correction credited to Bell and McCaffrey (2002) and
                                         Cameron and Miller (2015).
  interval(est, v, df, alpha)            t interval; a draw with v < 0, v not finite or df < 1 forms no interval.

Coefficient rules (argument `rule` of crossfit):
  'r5'    round 5's rule: least squares with intercept on the fit set's cluster means, clipped to [0, 1], and 0 when the
          total number of labelled clusters n is below 6 (round 4's c_crossfit_design);
  'ols'   the unclipped least-squares slope with intercept;
  float   a fixed coefficient (1.0 for the paper's primary estimator).
"""
import numpy as np
from scipy import stats

ALPHA = 0.10


def _take(x, idx):
    return np.asarray(x, float)[idx]


def slope(z, f):
    """Least-squares slope with intercept along the last axis, 0 where f has no spread (round 9's `slope`)."""
    fc = f - f.mean(-1, keepdims=True); zc = z - z.mean(-1, keepdims=True)
    v = (fc ** 2).sum(-1)
    return np.where(v > 0, (fc * zc).sum(-1) / np.where(v > 0, v, 1), 0.0)


def coefficient(z_fit, f_fit, rule, n_total):
    R = z_fit.shape[0]
    if isinstance(rule, (int, float)) and not isinstance(rule, bool):
        return np.full(R, float(rule))
    if rule == 'r5':
        if n_total < 6:
            return np.zeros(R)
        return np.clip(slope(z_fit, f_fit), 0.0, 1.0)
    if rule == 'ols':
        return slope(z_fit, f_fit)
    raise ValueError(f'unknown coefficient rule {rule!r}')


def classical(z, f, L, fpc=True):
    z = np.asarray(z, float); G = len(z); n = L.shape[1]
    zL = z[L]
    est = zL.mean(1)
    v = (1 - n / G if fpc else 1.0) * zL.var(1, ddof=1) / n
    return dict(est=est, v=v, df=n - 1)


def difference_fixed(z, f, L, c=1.0, fpc=True):
    z = np.asarray(z, float); f = np.asarray(f, float); G = len(z); n = L.shape[1]
    d = z[L] - c * f[L]
    est = d.mean(1) + c * f.mean()
    v = (1 - n / G if fpc else 1.0) * d.var(1, ddof=1) / n
    return dict(est=est, v=v, df=n - 1)


def crossfit(z, f, folds, rule='r5', fpc=True):
    """folds: list of K index arrays, fold k of shape (R, n_k); together they are the labelled sample.

    t_k = (1/G)[ sum_{g in L minus k} z_g + (G - a_k){ b_{-k} Fbar_{U minus (L minus k)} + mean_{g in k}(z_g - b_{-k} f_g) } ]
    with a_k = n - n_k, and s_k^2 = ((G - a_k)/G)^2 (1 - n_k/(G - a_k)) s_{e,k}^2 / n_k
    (ledger check `fold_piece`, results/round10/ledger/checks/l3_split_variance_check.py).
    """
    z = np.asarray(z, float); f = np.asarray(f, float); G = len(z)
    K = len(folds); sizes = [fk.shape[1] for fk in folds]; n = sum(sizes)
    Ftot = f.sum()
    ts, s2s, ssr, bs = [], [], [], []
    for k in range(K):
        fit = np.concatenate([folds[j] for j in range(K) if j != k], axis=1)
        est_idx = folds[k]
        a, m = fit.shape[1], est_idx.shape[1]
        b = coefficient(z[fit], f[fit], rule, n)
        e = z[est_idx] - b[:, None] * f[est_idx]
        mux_rest = (Ftot - f[fit].sum(1)) / (G - a)
        rest = b * mux_rest + e.mean(1)
        t = (z[fit].sum(1) + (G - a) * rest) / G
        sek2 = e.var(1, ddof=1) if m > 1 else np.full(e.shape[0], np.nan)
        fac = (1 - m / (G - a)) if fpc else 1.0
        s2 = ((G - a) / G) ** 2 * fac * sek2 / m
        ts.append(t); s2s.append(s2); bs.append(b)
        ssr.append(((e - e.mean(1, keepdims=True)) ** 2).sum(1))
    ts = np.array(ts); s2s = np.array(s2s)
    theta = ts.mean(0)
    V = s2s.mean(0) - ((ts - theta) ** 2).mean(0)
    Vcons = s2s.mean(0)
    sw2 = np.array(ssr).sum(0) / (n - K)
    Vw = (1 - n / G if fpc else 1.0) * sw2 / n
    return dict(est=theta, V_w=Vw, V=V, V_max=np.maximum(V, Vw), V_cons=Vcons, df_w=n - K, t_k=ts, s2_k=s2s,
                b_k=np.array(bs))


def fold_r9(z, f, A, B, U, ua, lA, lB):
    """Round 9's FOLD (code/scripts/round9_fewcluster_williams.py): the unlabelled clusters U are split between the
    folds, the first ua[r] of U[r] going to fold A. Fold A uses the coefficient fitted on B (lB) and vice versa.
    Variance sum_j (N_j/G)^2 (1 - n_j/N_j) s^2_{e,S_j}/n_j with t_{n-2}."""
    z = np.asarray(z, float); f = np.asarray(f, float); G = len(z)
    hA, hB = A.shape[1], B.shape[1]; nu = U.shape[1]
    fU = f[U]; inA = np.arange(nu)[None, :] < ua[:, None]
    zA, zB, fA, fB = z[A], z[B], f[A], f[B]
    sumA = np.where(inA, fU, 0).sum(1) + fA.sum(1); NA = ua + hA
    sumB = np.where(~inA, fU, 0).sum(1) + fB.sum(1); NB = (nu - ua) + hB
    tA = lB * sumA / NA + zA.mean(1) - lB * fA.mean(1)
    tB = lA * sumB / NB + zB.mean(1) - lA * fB.mean(1)
    est = (NA / G) * tA + (NB / G) * tB
    eA = zA - lB[:, None] * fA; eB = zB - lA[:, None] * fB
    v = (NA / G) ** 2 * (1 - hA / NA) * eA.var(1, ddof=1) / hA + (NB / G) ** 2 * (1 - hB / NB) * eB.var(1, ddof=1) / hB
    return dict(est=est, v=v, df=hA + hB - 2)


def bh_parts(z, f, L, tiny=1e-24):
    """Broska and Howes's estimator and its variance split into the labelled and unlabelled terms, as round 7's
    bh3_parts, for one population and labelled index array L (R, n). Returns theta, T_L, T_U, n."""
    z = np.asarray(z, float); f = np.asarray(f, float); G = len(z); R, n = L.shape
    Lf = np.zeros((R, G)); np.put_along_axis(Lf, L, 1.0, axis=1)
    N = G - n; r = n / N
    Fbar = f.mean(); fc = f - Fbar
    zL = (Lf * z).sum(1) / n; fL = (Lf * f).sum(1) / n; fU = ((1 - Lf) * f).sum(1) / N
    Zh = (Lf - r * (1 - Lf)) * fc[None, :]

    def sig(th):
        eps = Lf * (z[None, :] - th[:, None])
        return (eps ** 2).sum(1) / G, (eps * Zh).sum(1) / G, (Zh ** 2).sum(1) / G
    s11, s12, s22 = sig(zL + (fU - fL))
    lz = s22 <= tiny * max(1.0, Fbar ** 2)
    lam = np.where(lz, 0.0, s12 / np.where(lz, 1.0, s22))
    th = zL + lam * (fU - fL)
    TL = (Lf * (z[None, :] - th[:, None] - lam[:, None] * fc[None, :]) ** 2).sum(1) / n ** 2
    TU = lam ** 2 * r ** 2 * ((1 - Lf) * fc[None, :] ** 2).sum(1) / n ** 2
    return th, TL, TU, n


def bh_variants(z, f, L):
    """bh: T_L + T_U with the normal reference; bh_t: T_L n/(n-1) + T_U with t_{n-1}; bh_t_fpc: bh_t x (1 - n/G)."""
    G = len(z)
    th, TL, TU, n = bh_parts(z, f, L)
    v_t = TL * n / (n - 1) + TU
    return dict(bh=dict(est=th, v=TL + TU, df=np.inf), bh_t=dict(est=th, v=v_t, df=n - 1),
                bh_t_fpc=dict(est=th, v=v_t * (1 - n / G), df=n - 1))


def interval(est, v, df, alpha=ALPHA):
    """Two-sided t interval (normal when df is inf). Draws with v < 0, v not finite or df < 1 form no interval."""
    q = stats.norm.ppf(1 - alpha / 2) if np.isinf(df) else (stats.t.ppf(1 - alpha / 2, df) if df >= 1 else np.nan)
    ok = np.isfinite(v) & (v >= 0) & np.isfinite(q)
    half = np.where(ok, q * np.sqrt(np.where(ok, v, 0.0)), np.nan)
    return est - half, est + half, ok


# ---------------------------------------------------------------------------------------------------------------
# Regime B, form C (round 5's estimator definition, section "Regime B"; code/scripts/round5_ppi_twolevel.py)
# ---------------------------------------------------------------------------------------------------------------
_TL_FIXED = None


def _tl_fixed():
    """round5_ppi_twolevel.estimate, unchanged except one inserted line: for estimator 'C_fix1' the within-cluster
    coefficient is set to 1 in every cluster after the coefficient block (ppi is False for 'fix1', so the block first
    sets it to 0). Everything else, zhat_g, V_g, the regime B variance sum_g V_g / G^2 and the degrees of freedom
    (sum_g (m_g - 2) for theta3, sum_{g,h} (m_hg - 1) over partially labelled strata for theta2), is round 5's code."""
    global _TL_FIXED
    if _TL_FIXED is None:
        import inspect, textwrap
        import round5_ppi_twolevel as TL
        src = textwrap.dedent(inspect.getsource(TL.estimate))
        anchor = "    # ---- within stage: zhat_g and V_g\n"
        assert src.count(anchor) == 1
        src = src.replace(anchor, "    if kindc == 'fix1':\n        lamw = np.ones((G, ng))\n" + anchor)
        ns = dict(vars(TL)); exec(compile(src, 'round5_twolevel_estimate_fix1', 'exec'), ns)
        _TL_FIXED = ns['estimate']
    return _TL_FIXED


def regime_b_formC(T, sel, seed, coef='fixed1'):
    """Form C in regime B (every valid cluster labelled, m_g units in cluster g). T from round5_ppi_twolevel.prepare.
    coef: 'fixed1' (the paper's coefficient of 1), 'crossfit' (round 5's C_ppi: the within coefficient fitted on the
    other half of the clusters' labelled units, clipped to [0, 1]) or 'classical' (coefficient 0).
    Returns round 5's dict (theta, var, df, zhat, V, lam_w, ...)."""
    import round5_ppi_twolevel as TL
    Lmask = np.asarray(T['valid'], bool).copy()
    if coef == 'crossfit':
        return TL.estimate(T, Lmask, sel, 'C_ppi', seed, regime_b=True)
    if coef == 'classical':
        return TL.estimate(T, Lmask, sel, 'C_classical', seed, regime_b=True)
    if coef == 'fixed1':
        return _tl_fixed()(T, Lmask, sel, 'C_fix1', seed, regime_b=True)
    raise ValueError(coef)
