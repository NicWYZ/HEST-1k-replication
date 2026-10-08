"""Round 5 PPI, interval 2, stage E3: the two-level estimator in forms P and C (theory section 2).

One function, estimate(), computes on one draw the design-target estimate, its variance and its
degrees of freedom for one estimand and every gene, for six estimators:
    r4_classical, r4_ppi    round 4's form (form P with gamma = 0 and one coefficient for both
                            stages, the round-4 coefficient)
    P_classical, P_ppi      form P, one pooled intercept, gamma fitted (theory 2.1, 2.2)
    C_classical, C_ppi      form C, each cluster's own intercept (theory 2.1, 2.2)
'classical' means lambda^w = lambda^c = 0 (form P keeps its gamma).

Inputs are per-unit arrays, so the real-data driver (round5_ppi_e3_twolevel.py) and the
simulation (round5_ppi_e3_sim.py) call the same code.

Kinds of estimand (donor-weighted):
    'theta3'  weights sum to zero in every cluster; form C is the sample covariance of w and
              y - lambda yhat, linearised variance (theory 2.1).
    'theta2'  group of each unit 0 (neoplastic-dominant), 1 (stromal-dominant), -1 (neither);
              within-cluster draws stratified by group when m < all (memo section 5, E3 item 1);
              form C is the difference of the groups' labelled means of y - lambda yhat plus
              lambda times the difference of their all-unit means of yhat. Forms r4 and P use the
              stratified Horvitz-Thompson mean of their residual, which is exact because z, f and
              a are zero outside the two groups.
    'mean'    w = 1 (ACS theta2); form C is lambda fbar_g + rbar_g with the pooled within-cluster
              slope of y on yhat (cluster intercepts).

Cross-fitting: the halves of the labelled clusters are round4_ppi_estimator._crossfit_halves(Lm,
seed), per gene, the same halves that lambda_rule('c_crossfit_design', ..., seed) uses for the
between coefficient. Each cluster's within coefficients come from the other half's labelled units.
In regime B (every valid cluster labelled) the between stage is not used (lambda^c = 0) and the
variance is sum_g V_g / G^2 (theory 2.1, corners).
"""
import numpy as np

import round4_ppi_estimator as E
import round5_ppi_estimator as R5

ESTIMATORS = ("r4_classical", "r4_ppi", "P_classical", "P_ppi", "C_classical", "C_ppi")
NSTAT = 100.0


def prepare(y, yhat, w, didx, G, kind, group=None, valid=None):
    """Per-unit and per-cluster quantities that do not depend on the draw.
    y, yhat (n, ng); w (n,) design weights (w = 1 for 'mean'); didx (n,) cluster index;
    group (n,) for 'theta2'; valid (G,) clusters that admit the estimand."""
    y = np.asarray(y, float); yhat = np.asarray(yhat, float)
    w = np.nan_to_num(np.asarray(w, float))
    n, ng = y.shape
    H = 2 if kind == "theta2" else 1
    if group is None:
        group = np.zeros(n, int)
    group = np.asarray(group, int)
    if kind != "theta2":
        group = np.zeros(n, int)
    M = np.bincount(didx, minlength=G).astype(float)
    ing = group >= 0
    Mh = np.zeros((G, H))
    np.add.at(Mh, (didx[ing], group[ing]), 1.0)
    z = w[:, None] * y
    f = w[:, None] * yhat

    def cmean(v):
        s = np.zeros((G, v.shape[1])); np.add.at(s, didx, v)
        return s / np.maximum(M, 1)[:, None]
    zbar, fbar = cmean(z), cmean(f)
    abar = np.bincount(didx, weights=w, minlength=G) / np.maximum(M, 1)
    T = dict(kind=kind, y=y, yhat=yhat, w=w, z=z, f=f, didx=np.asarray(didx), group=group, G=G, H=H,
             M=M, Mh=Mh, zbar=zbar, fbar=fbar, abar=abar, ng=ng,
             valid=np.ones(G, bool) if valid is None else np.asarray(valid, bool))
    if kind == "theta3":
        # S_{w yhat, g} with divisor M - 1 (w has cluster mean zero up to rounding)
        wc = w - abar[didx]
        s = np.zeros((G, ng)); np.add.at(s, didx, wc[:, None] * yhat)
        T["Swh"] = s / np.maximum(M - 1, 1)[:, None]
    if kind == "theta2":
        hm = np.zeros((G, 2, ng))
        np.add.at(hm, (didx[ing], group[ing]), yhat[ing])
        T["hbar"] = hm / np.maximum(Mh, 1)[:, :, None]
    T["theta_full"] = zbar[T["valid"]].mean(0)
    return T


def _segments(T, sel):
    """Sort the labelled units by (cluster, stratum); returns the sorted unit index, the key of each
    segment, segment starts, cluster and stratum per segment, and per-unit segment id."""
    d, h = T["didx"][sel], T["group"][sel]
    keep = h >= 0
    idx = np.asarray(sel)[keep]
    key = d[keep] * T["H"] + h[keep]
    o = np.argsort(key, kind="stable")
    idx, key = idx[o], key[o]
    starts = np.flatnonzero(np.r_[True, key[1:] != key[:-1]]) if len(key) else np.zeros(0, int)
    ukey = key[starts]
    seg = np.cumsum(np.r_[False, key[1:] != key[:-1]]) if len(key) else np.zeros(0, int)
    return idx, ukey, starts, ukey // T["H"], ukey % T["H"], seg


def _segsum(v, starts):
    if len(starts) == 0:
        return np.zeros((0,) + v.shape[1:])
    return np.add.reduceat(v, starts, axis=0)


def _to_gh(T, vals, gseg, hseg):
    out = np.zeros((T["G"], T["H"]) + vals.shape[1:])
    out[gseg, hseg] = vals
    return out


def _half_sums(X, half):
    """X (G, ng) per-cluster statistic; half (G, ng) in {0, 1, -1}; returns (XA, XB) (ng,)."""
    return np.where(half == 0, X, 0.0).sum(0), np.where(half == 1, X, 0.0).sum(0)


def _assign(vA, vB, half):
    """Each cluster gets the OTHER half's value."""
    return np.where(half == 0, vB[None, :], np.where(half == 1, vA[None, :], 0.0))


def _clip(num, den):
    with np.errstate(invalid="ignore", divide="ignore"):
        r = np.where(den > 0, num / np.where(den > 0, den, 1.0), 0.0)
    return np.clip(r, 0.0, 1.0)


def _coef_P(T, idx, ukey_g, starts, half, ppi):
    """Form P coefficients: pooled least squares of z on (a, f) with one intercept over the half's
    labelled units; lambda clipped to [0, 1] and gamma refitted at the clipped lambda. 'mean': a = 1,
    gamma = 0. Classical: lambda = 0, gamma fitted. Returns gamma, lam (G, ng), each from the other half."""
    G, ng = T["G"], T["ng"]
    a = T["w"][idx][:, None]
    z, f = T["z"][idx], T["f"][idx]
    one = np.ones((len(idx), 1))
    stats = {}
    for k, v in (("n", one), ("a", a), ("f", f), ("z", z), ("aa", a * a), ("af", a * f), ("ff", f * f),
                 ("az", a * z), ("fz", f * z)):
        s = _segsum(v, starts)
        full = np.zeros((G, s.shape[1])); np.add.at(full, ukey_g, s)
        stats[k] = np.broadcast_to(full, (G, ng)) if full.shape[1] == 1 else full
    hs = {k: _half_sums(v, half) for k, v in stats.items()}
    out = []
    for j in (0, 1):
        S = {k: v[j] for k, v in hs.items()}
        N = np.maximum(S["n"], 1.0)
        Caa = S["aa"] - S["a"] ** 2 / N
        Caf = S["af"] - S["a"] * S["f"] / N
        Cff = S["ff"] - S["f"] ** 2 / N
        Caz = S["az"] - S["a"] * S["z"] / N
        Cfz = S["fz"] - S["f"] * S["z"] / N
        if T["kind"] == "mean":
            g = np.zeros(ng)
            lam = _clip(Cfz, Cff) if ppi else np.zeros(ng)
        else:
            if ppi:
                det = Caa * Cff - Caf ** 2
                sing = ~(det > 1e-12 * np.maximum(Caa * Cff, 1e-300))
                with np.errstate(invalid="ignore", divide="ignore"):
                    lraw = np.where(sing, 0.0, (Caa * Cfz - Caf * Caz) / np.where(sing, 1.0, det))
                lam = np.clip(lraw, 0.0, 1.0)
            else:
                lam = np.zeros(ng)
            with np.errstate(invalid="ignore", divide="ignore"):
                g = np.where(Caa > 0, (Caz - lam * Caf) / np.where(Caa > 0, Caa, 1.0), 0.0)
        out.append((g, lam))
    (gA, lA), (gB, lB) = out
    return _assign(gA, gB, half), _assign(lA, lB, half)


def _coef_slope(T, xs, ys, starts, ukey_g, half, centre=True):
    """Pooled slope of ys on xs over the half's labelled units, centred within segments (cluster or
    cluster x group) when centre, through the origin otherwise; clipped; from the other half."""
    G, ng = T["G"], T["ng"]
    if centre:
        n = np.diff(np.r_[starts, len(xs)]).astype(float)[:, None]
        sx, sy = _segsum(xs, starts), _segsum(ys, starts)
        sxy = _segsum(xs * ys, starts) - sx * sy / n
        sxx = _segsum(xs * xs, starts) - sx * sx / n
    else:
        sxy, sxx = _segsum(xs * ys, starts), _segsum(xs * xs, starts)
    Fxy = np.zeros((G, ng)); np.add.at(Fxy, ukey_g, sxy)
    Fxx = np.zeros((G, ng)); np.add.at(Fxx, ukey_g, sxx)
    (xyA, xyB), (xxA, xxB) = _half_sums(Fxy, half), _half_sums(Fxx, half)
    return _assign(_clip(xyA, xxA), _clip(xyB, xxB), half)


def ht_means(T, sel):
    """Stratified Horvitz-Thompson estimates of each cluster's mean of z and f (G, ng): round 4's
    t and tf, the plain labelled means when there is one stratum."""
    idx, ukey, starts, gseg, hseg, seg = _segments(T, sel)
    n = np.diff(np.r_[starts, len(idx)]).astype(float)[:, None]
    out = []
    for v in (T["z"][idx], T["f"][idx]):
        mh = _to_gh(T, _segsum(v, starts) / n, gseg, hseg)
        out.append((T["Mh"][:, :, None] / np.maximum(T["M"], 1)[:, None, None] * mh).sum(1))
    return out


def estimate(T, Lmask, sel, estimator, seed, regime_b=False, xf=True, lam_r4=None):
    """One draw. Lmask (G,) labelled clusters; sel (index array) labelled units (only units of
    labelled clusters and, for theta2, of the two groups, are used); estimator in ESTIMATORS;
    seed the cross-fit seed string; lam_r4: dict from round4 lambda_rule (regime A) or a (G, ng)
    array (regime B) giving round 4's coefficient, required for r4_ppi.
    Returns dict(theta, var, df, zhat, V, lam_w, lam_c)."""
    G, ng, kind = T["G"], T["ng"], T["kind"]
    form, kindc = estimator.split("_")
    ppi = kindc == "ppi"
    Lc = Lmask & T["valid"]
    sel = np.asarray(sel)
    sel = sel[Lc[T["didx"][sel]]]
    idx, ukey, starts, gseg, hseg, seg = _segments(T, sel)
    Lm = np.broadcast_to(Lc[:, None], (G, ng)).copy()
    Um = np.broadcast_to((~Lc & T["valid"])[:, None], (G, ng)).copy()
    half = E._crossfit_halves(Lm, seed)
    nseg = np.diff(np.r_[starts, len(idx)]).astype(float)
    mh = _to_gh(T, nseg, gseg, hseg)                       # (G, H) labelled units per stratum
    Mh, M = T["Mh"], T["M"]
    fac = np.where(mh > 0, 1.0 - mh / np.maximum(Mh, 1), 0.0)
    gam = np.zeros((G, ng))
    # ---- within coefficients
    if form == "r4":
        if ppi:
            lamw = lam_r4["lamL"] if isinstance(lam_r4, dict) else np.asarray(lam_r4)
        else:
            lamw = np.zeros((G, ng))
    elif form == "P":
        gam, lamw = _coef_P(T, idx, gseg, starts, half, ppi)
    else:  # C
        if not ppi:
            lamw = np.zeros((G, ng))
        elif kind == "theta3":
            ys, hs, ws = T["y"][idx], T["yhat"][idx], T["w"][idx][:, None]
            n1 = nseg[:, None]
            wb = (_segsum(ws, starts) / n1)[seg]
            yb = (_segsum(ys, starts) / n1)[seg]
            hb = (_segsum(hs, starts) / n1)[seg]
            lamw = _coef_slope(T, (ws - wb) * (hs - hb), (ws - wb) * (ys - yb), starts, gseg, half, centre=False)
        else:   # theta2 (centred within cluster x group) and mean (within cluster)
            lamw = _coef_slope(T, T["yhat"][idx], T["y"][idx], starts, gseg, half, centre=True)
    # ---- within stage: zhat_g and V_g
    lw = lamw[T["didx"][idx]]                               # per labelled unit, the cluster's coefficient
    n1 = nseg[:, None]
    if form in ("r4", "P") or (form == "C" and kind == "mean"):
        if form == "C":
            r = T["y"][idx] - lw * T["yhat"][idx]
        else:
            r = T["z"][idx] - gam[T["didx"][idx]] * T["w"][idx][:, None] - lw * T["f"][idx]
        sr = _segsum(r, starts); sq = _segsum(r * r, starts)
        rb = sr / n1
        s2 = np.where(n1 > 1, (sq - n1 * rb ** 2) / np.maximum(n1 - 1, 1), 0.0)
        RB, S2 = _to_gh(T, rb, gseg, hseg), _to_gh(T, s2, gseg, hseg)
        pi = Mh / np.maximum(M, 1)[:, None]
        known = gam * T["abar"][:, None] + lamw * T["fbar"]
        zhat = known + (pi[:, :, None] * RB).sum(1)
        V = ((pi ** 2 * fac)[:, :, None] * S2 / np.maximum(mh, 1)[:, :, None]).sum(1)
        dfw = np.maximum(mh - 1, 0)
    elif kind == "theta3":
        ys, hs, ws = T["y"][idx], T["yhat"][idx], T["w"][idx][:, None]
        r = ys - lw * hs
        wb = (_segsum(ws, starts) / n1)
        rb = _segsum(r, starts) / n1
        du = (ws - wb[seg]) * (r - rb[seg])
        swr = _segsum(du, starts) / np.maximum(n1 - 1, 1)
        # linearised variance (theory 2.1): u_i = (w_i - Wbar)(r_i - rbar_L) with the cluster's known
        # Wbar = abar_g (zero up to rounding), times (m/(m-1))^2 from s_wr = m/(m-1) * mean(u) + ...
        uk = (ws - T["abar"][T["didx"][idx]][:, None]) * (r - rb[seg])
        ukm = _segsum(uk, starts) / n1
        su2 = np.where(n1 > 1, (_segsum(uk * uk, starts) - n1 * ukm ** 2) / np.maximum(n1 - 1, 1), 0.0)
        su2 = su2 * (n1 / np.maximum(n1 - 1, 1)) ** 2
        SWR, SU2 = _to_gh(T, swr, gseg, hseg)[:, 0], _to_gh(T, su2, gseg, hseg)[:, 0]
        k = ((M - 1) / np.maximum(M, 1))[:, None]
        zhat = k * (lamw * T["Swh"] + SWR)
        V = k ** 2 * fac[:, :1] * SU2 / np.maximum(mh[:, :1], 1)
        dfw = np.maximum(mh - 2, 0)
    else:  # C, theta2
        r = T["y"][idx] - lw * T["yhat"][idx]
        sr = _segsum(r, starts); sq = _segsum(r * r, starts)
        rb = sr / n1
        s2 = np.where(n1 > 1, (sq - n1 * rb ** 2) / np.maximum(n1 - 1, 1), 0.0)
        RB, S2 = _to_gh(T, rb, gseg, hseg), _to_gh(T, s2, gseg, hseg)
        sign = np.array([1.0, -1.0])
        zhat = (sign[None, :, None] * RB).sum(1) + lamw * (T["hbar"][:, 0] - T["hbar"][:, 1])
        V = (fac[:, :, None] * S2 / np.maximum(mh, 1)[:, :, None]).sum(1)
        dfw = np.maximum(mh - 1, 0)
    zhat = np.where(Lm, zhat, 0.0)
    V = np.where(Lm, V, 0.0)
    nL = Lc.sum()
    Gv = T["valid"].sum()
    fb = T["fbar"]
    Fbar = fb[T["valid"]].mean(0)
    # ---- between stage
    if regime_b:
        theta = zhat[Lc].mean(0)
        var = V.sum(0) / Gv ** 2
        partial = (fac > 0) & (mh > 0)
        df = float(np.where(partial, dfw, 0).sum()) if kind == "theta2" and form == "C" else \
            float(np.maximum((mh.sum(1) - (2 if (form == "C" and kind == "theta3") else 1))[Lc], 0).sum())
        lamc = np.zeros((G, ng)); cU = np.zeros(ng)
    else:
        if form == "r4" and ppi:
            lamc, cU = lam_r4["lamL"], lam_r4["cU"]
            lam = lam_r4
        elif not ppi:
            lamc, cU = np.zeros((G, ng)), np.zeros(ng)
            lam = dict(lamL=lamc, cU=cU)
        else:
            D = dict(n=np.full((G, ng), NSTAT), Sz=zhat * NSTAT, Sf=fb * NSTAT)
            D["Szz"], D["Sff"], D["Szf"] = D["Sz"] ** 2 / NSTAT, D["Sf"] ** 2 / NSTAT, D["Sz"] * D["Sf"] / NSTAT
            lam = E.lambda_rule("c_crossfit_design", "donor", D, Lm, Um, seed=seed)
            lamc, cU = lam["lamL"], lam["cU"]
        R = np.where(Lm, zhat - lamc * fb, 0.0)
        theta = cU * Fbar + R.sum(0) / nL
        e = np.where(Lm, R + (lamc - cU[None, :]) * Fbar[None, :], 0.0)
        em = e.sum(0) / nL
        s2e = np.where(Lm, (e - em) ** 2, 0.0).sum(0) / (nL - 1.0)
        var = (1.0 - nL / Gv) * s2e / nL + V.sum(0) / (Gv * nL)
        if xf:
            var = var + R5.crossfit_extra("donor", fb, Lm, lam, np.broadcast_to(T["valid"][:, None], (G, ng)))
        df = float(nL - 1)
    return dict(theta=theta, var=var, df=df, zhat=zhat, V=V, lam_w=lamw, lam_c=lamc, gamma=gam)
