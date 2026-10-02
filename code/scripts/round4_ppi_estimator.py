#!/usr/bin/env python
"""Round 4, PPI track, stage Q1: the estimator module.

One entry point per component, imported by every later stage of the track
(docs/decisions/round4_ppi_track.md section 6, Q1; transcribed in docs/round4_ppi_plan.md).

WHAT IS NOT NEW. The estimator is the survey-sampling difference estimator and, in its PPI++
form, the generalised regression estimator (Mozer, arXiv:2603.19160; Sarndal, Swensson and
Wretman 1992 ch. 8; Breidt and Opsomer 2017). The variance is Liang and Zeger's sandwich on
the PPI influence function with the small-G practice of Cameron and Miller (2015) and
MacKinnon, Nielsen and Webb (2023), the CR2 leverage adjustment of Bell and McCaffrey (2002).

DATA INTERFACE. Every estimand of the track is the mean of a per-spot scalar z that is linear
in the outcome (round3_b1_ppi.py writes theta_3 and theta_2 that way, with label-free design
constants), so everything here works on PER-DONOR sufficient statistics, arrays of shape
(n_donor, ncol):

    n    spots of the donor in the set
    Sz   sum of z(y)        Sf   sum of z(yhat)
    Szz  sum of z(y)^2      Sff  sum of z(yhat)^2      Szf  sum of z(y) z(yhat)

The column axis is genes for real data and Monte Carlo replicates for the simulation.
Labelled and unlabelled donors are boolean masks Lm, Um of the same shape (they may differ by
column, as they do in the design-based simulation). For the DONOR-weighted population the
observation is the donor-level value t_d = Sz_d / n_d (and tf_d = Sf_d / n_d); for the
SPOT-weighted population it is the spot.

THE ESTIMATOR, in general form. theta = cU * mean_U(f) + mean_L(z - lamL * f), where lamL may
vary by labelled donor (cross-fitting) and cU is the coefficient on the unlabelled mean. For
ordinary PPI++ lamL = cU = lambda; lambda = 0 is the classical estimator.

COMPONENTS (section 6 Q1).
  lambda      rule 'a_b1'       B1's rule: spot population tuned on the spot i.i.d. variance;
                                donor population tuned on the donor pairs (0 if G_L < 4 or
                                G_U < 2). This reproduces round3_b1_ppi.py exactly.
              rule 'b_cluster'  tuned on the donor-clustered (CR1) variance, clipped to [0, 1],
                                fixed at 0 when G_L < 4. For the donor population this is the
                                same formula as 'a_b1'.
              rule 'c_crossfit' labelled donors split in two halves (crc32 seed); lambda tuned
                                by the 'b_cluster' formula (no G threshold) on each half with U,
                                and applied to the OTHER half; cU is the matching weighted
                                average so the estimator stays unbiased given the lambdas.
                                Variances centre the rectifier within halves.
              rules 'd1_pretest', 'd2_pretest'  (Q1 decision memo section 2) rule (c) with a
                                pre-test: a half's lambda is 0 unless its unclipped estimate
                                exceeds k = 1 or 2 OLS slope standard errors over the half's
                                donors (three or more), and 0 throughout when n_L < 6;
                                columns where both halves are 0 are
                                reported as the classical estimator with classical variances.
  variance    CR1 (G/(G-1)), CR2 (Bell-McCaffrey leverage adjustment), spot i.i.d.;
              references t_{G_L-1} (CR1), Bell-McCaffrey Satterthwaite df of the L term (CR2),
              and a Welch-Satterthwaite combination of the U and L terms' df (either).
  fpc         (1 - G_L/G) on the labelled between-donor term.
  design_exact  (PROPOSAL, flagged in plan section 8 item 6; not a component the source names)
              linearised design variance under simple random sampling of G_L of G donors
              without replacement when U is exactly the complement of L.
  bootstrap   donor bootstrap within L and within U, lambda held fixed: percentile,
              studentised (bootstrap-t on the CR1 standard error), BCa (jackknife over donors).
"""
import zlib

import numpy as np
from scipy import stats

ALPHA = 0.10
MIN_TUNE_G = 4
PRETEST_K = {"d1_pretest": 1.0, "d2_pretest": 2.0}
N_BOOT = 500

STAT_KEYS = ("n", "Sz", "Sf", "Szz", "Sff", "Szf")


# ============================================================== helpers
def _m(x, mask):
    """Masked sum over the donor axis."""
    return np.where(mask, x, 0.0).sum(axis=0)


def _safe_div(a, b):
    b = np.asarray(b, dtype=float)
    return np.where(b != 0, a / np.where(b != 0, b, 1.0), np.nan)


def seed_rng(tag):
    return np.random.default_rng(zlib.crc32(str(tag).encode()))


def aggregate_to_donors(S, group_donor_idx, n_donor):
    """Sum per-group (e.g. per-slide) statistics to per-donor statistics.
    S: dict of arrays (n_group, ncol). group_donor_idx: (n_group,) int."""
    out = {}
    for k in STAT_KEYS:
        a = np.asarray(S[k], dtype=float)
        if a.ndim == 1:
            a = a[:, None]
        z = np.zeros((n_donor,) + a.shape[1:])
        np.add.at(z, group_donor_idx, a)
        out[k] = z
    return out


def donor_values(D):
    """Donor-level values for the donor-weighted population."""
    t = _safe_div(D["Sz"], D["n"])
    tf = _safe_div(D["Sf"], D["n"])
    return t, tf


# ============================================================== lambda rules
def _clip01(num, den):
    return np.where(den > 0, np.clip(_safe_div(num, den), 0.0, 1.0), 0.0)


def _cluster_lambda_spot(D, Lm, Um, raw=False):
    """lambda minimising the CR1 variance (spot population), no threshold applied.
    raw=True returns the unclipped ratio (nan where the denominator is 0)."""
    nL, NU = _m(D["n"], Lm), _m(D["n"], Um)
    zb, fbL, fbU = _m(D["Sz"], Lm) / nL, _m(D["Sf"], Lm) / nL, _m(D["Sf"], Um) / NU
    qa = (D["Sz"] - D["n"] * zb) / nL
    qb = (D["Sf"] - D["n"] * fbL) / nL
    q0 = (D["Sf"] - D["n"] * fbU) / NU
    GL, GU = Lm.sum(0), Um.sum(0)
    cL = GL / np.maximum(GL - 1.0, 1e-300)
    cU = GU / np.maximum(GU - 1.0, 1e-300)
    num = cL * _m(qa * qb, Lm)
    den = cU * _m(q0 ** 2, Um) + cL * _m(qb ** 2, Lm)
    if raw:
        return _safe_div(num, den)
    return _clip01(num, den)


def _cluster_lambda_donor(t, tf, Lm, Um, raw=False):
    """lambda from the donor pairs (donor population); identical to B1's donor_pairs rule."""
    GL, GU = Lm.sum(0), Um.sum(0)
    tLm = _m(t, Lm) / GL
    tfLm = _m(tf, Lm) / GL
    tfUm = _m(tf, Um) / GU
    aL = np.where(Lm, t - tLm, 0.0)
    bL = np.where(Lm, tf - tfLm, 0.0)
    dU = np.where(Um, tf - tfUm, 0.0)
    cU = GU / np.maximum(GU - 1.0, 1e-300)
    cL = GL / np.maximum(GL - 1.0, 1e-300)
    num = cL * (aL * bL).sum(0) / GL ** 2
    den = cU * (dU ** 2).sum(0) / GU ** 2 + cL * (bL ** 2).sum(0) / GL ** 2
    if raw:
        return _safe_div(num, den)
    return _clip01(num, den)


def _ols_slope_se(y, x, mask):
    """Ordinary least-squares slope standard error of y on x (with intercept) over the
    masked donors, per column; nan where fewer than three donors or x has no spread."""
    k = mask.sum(0).astype(float)
    xm, ym = _m(x, mask) / np.maximum(k, 1.0), _m(y, mask) / np.maximum(k, 1.0)
    dx = np.where(mask, x - xm, 0.0)
    dy = np.where(mask, y - ym, 0.0)
    sxx = (dx ** 2).sum(0)
    b = _safe_div((dx * dy).sum(0), sxx)
    rss = ((dy - b * dx) ** 2 * mask).sum(0)
    s2 = np.where(k >= 3, rss / np.maximum(k - 2.0, 1.0), np.nan)
    return np.where((k >= 3) & (sxx > 0), np.sqrt(s2 / np.where(sxx > 0, sxx, 1.0)), np.nan)


def _donor_contributions(pop, D, Lh):
    """The half's donor-level outcome and prediction contributions used by the pre-test:
    donor population (t_d, tf_d); spot population the donor totals of z and f centred at the
    half's spot means (the CR1 influence pieces of _cluster_lambda_spot, up to scale)."""
    if pop == "donor":
        return donor_values(D)
    nL = _m(D["n"], Lh)
    zb, fb = _m(D["Sz"], Lh) / nL, _m(D["Sf"], Lh) / nL
    return D["Sz"] - D["n"] * zb, D["Sf"] - D["n"] * fb


def lambda_spot_iid(D, Lm, Um):
    """B1's spot-population rule: minimise the spot i.i.d. variance (PPI++'s prescription)."""
    nL, NU = _m(D["n"], Lm), _m(D["n"], Um)
    zb, fbL = _m(D["Sz"], Lm) / nL, _m(D["Sf"], Lm) / nL
    fbU = _m(D["Sf"], Um) / NU
    cov = (_m(D["Szf"], Lm) - nL * zb * fbL) / nL ** 2
    sqb = (_m(D["Sff"], Lm) - nL * fbL ** 2) / nL ** 2
    sqU = (_m(D["Sff"], Um) - NU * fbU ** 2) / NU ** 2
    fU = np.where(NU > 1, NU / np.maximum(NU - 1.0, 1e-300), np.inf)
    fL = np.where(nL > 1, nL / np.maximum(nL - 1.0, 1e-300), np.inf)
    return _clip01(fL * cov, fU * sqU + fL * sqb)


def lambda_rule(rule, pop, D, Lm, Um, seed=None):
    """Returns dict(lamL (n_donor, ncol), cU (ncol,), strata (n_donor, ncol) int or None,
    lam (ncol,) the scalar reported, basis str)."""
    ncol = Lm.shape[1]
    GL, GU = Lm.sum(0), Um.sum(0)
    t, tf = donor_values(D) if pop == "donor" else (None, None)

    def full(lam):
        return dict(lamL=np.broadcast_to(lam, Lm.shape).copy(), cU=lam.copy(),
                    strata=None, lam=lam)

    if rule == "none":
        out = full(np.zeros(ncol)); out["basis"] = "classical"; return out
    if rule == "a_b1":
        if pop == "spot":
            lam = np.where(GU > 0, lambda_spot_iid(D, Lm, Um), 0.0)
            basis = "spot_iid"
        else:
            ok = (GL >= MIN_TUNE_G) & (GU >= 2)
            lam = np.where(ok, _cluster_lambda_donor(t, tf, Lm, Um), 0.0)
            basis = "donor_pairs"
        out = full(lam); out["basis"] = basis; return out
    if rule == "b_cluster":
        ok = (GL >= MIN_TUNE_G) & (GU >= 2)
        lam = (_cluster_lambda_spot(D, Lm, Um) if pop == "spot"
               else _cluster_lambda_donor(t, tf, Lm, Um))
        lam = np.where(ok, lam, 0.0)
        out = full(lam); out["basis"] = "cluster_cr1"; return out
    if rule == "c_crossfit":
        rng = seed_rng(f"crossfit|{seed}")
        half = np.full(Lm.shape, -1, dtype=int)
        for j in range(ncol):
            idx = np.flatnonzero(Lm[:, j])
            perm = rng.permutation(idx)
            h = len(perm) // 2
            half[perm[:h], j] = 0
            half[perm[h:], j] = 1
        LA, LB = half == 0, half == 1
        if pop == "spot":
            lamA = _cluster_lambda_spot(D, LA, Um)
            lamB = _cluster_lambda_spot(D, LB, Um)
        else:
            lamA = _cluster_lambda_donor(t, tf, LA, Um)
            lamB = _cluster_lambda_donor(t, tf, LB, Um)
        okU = GU >= 2
        lamA, lamB = np.where(okU, lamA, 0.0), np.where(okU, lamB, 0.0)
        lamL = np.where(LA, lamB[None, :], np.where(LB, lamA[None, :], 0.0))
        if pop == "spot":
            w = np.where(Lm, D["n"], 0.0)
        else:
            w = Lm.astype(float)
        cU = (w * lamL).sum(0) / w.sum(0)
        return dict(lamL=lamL, cU=cU, strata=np.where(Lm, half, -1), lam=cU,
                    lamA=lamA, lamB=lamB, basis="crossfit_cluster")
    if rule in PRETEST_K:
        # Rule (d), Q1 decision memo section 2 (plan section 13.2): rule (c) with a pre-test on
        # each half. The halves are the same as rule (c)'s (same seed tag). A half's lambda is
        # its clipped estimate only if its unclipped estimate exceeds k times the OLS slope
        # standard error of the half's donor outcome contributions on its donor prediction
        # contributions (at least three donors in the half); otherwise 0. Columns where both
        # halves are 0 are classical; all_intervals then reports the classical estimator and its
        # variance there (flag 'classical_cols').
        k = PRETEST_K[rule]
        rng = seed_rng(f"crossfit|{seed}")
        half = np.full(Lm.shape, -1, dtype=int)
        for j in range(ncol):
            idx = np.flatnonzero(Lm[:, j])
            perm = rng.permutation(idx)
            h = len(perm) // 2
            half[perm[:h], j] = 0
            half[perm[h:], j] = 1
        LA, LB = half == 0, half == 1
        okU = GU >= 2
        lams, raws, ses = [], [], []
        for Lh in (LA, LB):
            if pop == "spot":
                raw = _cluster_lambda_spot(D, Lh, Um, raw=True)
                clip = _cluster_lambda_spot(D, Lh, Um)
            else:
                raw = _cluster_lambda_donor(t, tf, Lh, Um, raw=True)
                clip = _cluster_lambda_donor(t, tf, Lh, Um)
            yv, xv = _donor_contributions(pop, D, Lh)
            se = _ols_slope_se(yv, xv, Lh)
            # memo section 2 item 2: when n_L < 6 lambda is 0 throughout (classical)
            passed = (okU & (GL >= 6) & (Lh.sum(0) >= 3) & np.isfinite(se) & np.isfinite(raw)
                      & (raw > k * se))
            lams.append(np.where(passed, clip, 0.0)); raws.append(raw); ses.append(se)
        lamA, lamB = lams
        lamL = np.where(LA, lamB[None, :], np.where(LB, lamA[None, :], 0.0))
        w = np.where(Lm, D["n"], 0.0) if pop == "spot" else Lm.astype(float)
        cU = (w * lamL).sum(0) / w.sum(0)
        classical_cols = (lamA == 0.0) & (lamB == 0.0)
        return dict(lamL=lamL, cU=cU, strata=np.where(Lm, half, -1), lam=cU,
                    lamA=lamA, lamB=lamB, rawA=raws[0], rawB=raws[1], seA=ses[0], seB=ses[1],
                    classical_cols=classical_cols, basis=f"crossfit_pretest_k{k:g}")
    raise ValueError(rule)


# ============================================================== the estimator
def estimate(pop, D, Lm, Um, lam):
    """Point estimate and the per-donor influence pieces the variances need.

    lam is the dict from lambda_rule. Returns dict with theta, and for each term ('L', 'U'):
    q (n_donor, ncol) per-donor influence totals (zero off the term's mask), sq (per-donor
    sums of squared per-observation influence, for the i.i.d. variance), w (the donor's share
    of its term's observations, for CR2), mask, and the observation counts.
    """
    lamL, cU, strata = lam["lamL"], lam["cU"], lam["strata"]
    GU = Um.sum(0)
    res = {}
    # The classical estimator has no unlabelled term at all (B1: a zero U term, never a NaN
    # when G_U = 1), so its U mask is emptied for the variances; theta is unaffected (cU = 0).
    Um_var = Um if lam.get("basis") != "classical" else np.zeros_like(Um)
    if pop == "spot":
        n = D["n"]
        nL, NU = _m(n, Lm), _m(n, Um)
        Sr = D["Sz"] - lamL * D["Sf"]
        Srr = D["Szz"] - 2.0 * lamL * D["Szf"] + lamL ** 2 * D["Sff"]
        rbar = _m(Sr, Lm) / nL
        fU = np.where(GU > 0, _safe_div(_m(D["Sf"], Um), NU), 0.0)
        res["theta"] = np.where(GU > 0, cU * fU, 0.0) + rbar
        rc = _centre(Sr, n, Lm, strata)
        qL = np.where(Lm, (Sr - n * rc) / nL, 0.0)
        sqL = np.where(Lm, (Srr - 2.0 * rbar * Sr + n * rbar ** 2) / nL ** 2, 0.0)
        qU = np.where(Um, cU * (D["Sf"] - n * fU) / np.where(NU > 0, NU, 1.0), 0.0)
        sqU = np.where(Um, cU ** 2 * (D["Sff"] - 2.0 * fU * D["Sf"] + n * fU ** 2)
                       / np.where(NU > 0, NU, 1.0) ** 2, 0.0)
        res["L"] = dict(q=qL, sq=sqL, mask=Lm, nobs=nL, size=n, strata=strata)
        res["U"] = dict(q=qU, sq=sqU, mask=Um_var, nobs=NU, size=n, strata=None)
    else:
        t, tf = donor_values(D)
        GL = Lm.sum(0)
        r = t - lamL * tf
        rbar = _m(r, Lm) / GL
        tfU = np.where(GU > 0, _safe_div(_m(tf, Um), GU), 0.0)
        res["theta"] = np.where(GU > 0, cU * tfU, 0.0) + rbar
        rc = _centre(r, np.ones_like(r), Lm, strata)
        devL = np.where(Lm, r - rc, 0.0)
        devLp = np.where(Lm, r - rbar, 0.0)
        devU = np.where(Um, tf - tfU, 0.0)
        nd = np.where(D["n"] > 0, D["n"], 1.0)
        res["L"] = dict(q=devL / GL, sq=devLp ** 2 / nd / GL ** 2, mask=Lm,
                        nobs=_m(D["n"], Lm), size=np.ones_like(t), strata=strata)
        res["U"] = dict(q=cU * devU / np.where(GU > 0, GU, 1.0),
                        sq=cU ** 2 * devU ** 2 / nd / np.where(GU > 0, GU, 1.0) ** 2,
                        mask=Um_var, nobs=_m(D["n"], Um), size=np.ones_like(t), strata=None)
    res["G_L"], res["G_U"] = Lm.sum(0), GU
    res["pop"] = pop
    return res


def _centre(x, n, mask, strata):
    """Per-observation centring value for each donor: the pooled mean over the mask, or the
    within-stratum mean when strata are given."""
    if strata is None:
        return (_m(x, mask) / _m(n, mask))[None, :] * np.ones_like(x)
    out = np.zeros_like(x, dtype=float)
    for h in np.unique(strata[strata >= 0]):
        s = mask & (strata == h)
        out = np.where(s, (_m(x, s) / _m(n, s))[None, :], out)
    return out


def _n_strata(term):
    if term["strata"] is None:
        return 1
    return int(len(np.unique(term["strata"][term["strata"] >= 0])))


# ============================================================== variances
def var_iid(res):
    """Spot i.i.d. variance, n/(n-1) sum h_i^2 per term (B1's form)."""
    v = 0.0
    for key in ("L", "U"):
        T = res[key]
        nobs = T["nobs"]
        f = np.where(nobs > 1, nobs / np.maximum(nobs - 1.0, 1e-300), np.nan)
        s = T["sq"].sum(0)
        v = v + np.where(T["mask"].sum(0) > 0, f * s, 0.0)
    return v


def var_term_cr1(T):
    G = T["mask"].sum(0)
    k = _n_strata(T)
    c = np.where(G > k, G / np.maximum(G - float(k), 1e-300), np.nan)
    return np.where(G > 0, c * (T["q"] ** 2).sum(0), 0.0)


def _shares(T):
    """Each donor's share of its (stratum's) observations in the term."""
    size, mask, strata = T["size"], T["mask"], T["strata"]
    if strata is None:
        tot = _m(size, mask)[None, :]
    else:
        tot = np.ones_like(size, dtype=float)
        for h in np.unique(strata[strata >= 0]):
            s = mask & (strata == h)
            tot = np.where(s, _m(size, s)[None, :], tot)
    return np.where(mask, size / tot, 0.0)


def var_term_cr2(T):
    w = _shares(T)
    adj = np.where(T["mask"], 1.0 / np.maximum(1.0 - w, 1e-300), 0.0)
    return np.where(T["mask"].sum(0) > 0, (T["q"] ** 2 * adj).sum(0), 0.0)


def df_term_bm(T):
    """Bell-McCaffrey Satterthwaite degrees of freedom for one term, under an i.i.d.
    working model at the observation level, closed form for a (stratified) mean."""
    size, mask, strata = T["size"], T["mask"], T["strata"]
    labels = [None] if strata is None else list(np.unique(strata[strata >= 0]))
    ntot = _m(size, mask)
    trQ = np.zeros(mask.shape[1])
    trQ2 = np.zeros(mask.shape[1])
    for h in labels:
        s = mask if h is None else (mask & (strata == h))
        nh = _m(size, s)
        w = np.where(s, size / np.where(nh > 0, nh, 1.0)[None, :], 0.0)
        a = np.where(s, w / np.maximum(1.0 - w, 1e-300), 0.0)
        u2 = np.where(s, w ** 2 / np.maximum(1.0 - w, 1e-300), 0.0)
        tr = a.sum(0) - u2.sum(0)
        tr2 = (a ** 2).sum(0) - 2.0 * (a * u2).sum(0) + u2.sum(0) ** 2
        sc = nh / np.where(ntot > 0, ntot, 1.0) ** 2
        trQ += sc * tr
        trQ2 += sc ** 2 * tr2
    return np.where(trQ2 > 0, trQ ** 2 / np.where(trQ2 > 0, trQ2, 1.0), np.nan)


def df_term_cr1(T):
    return T["mask"].sum(0) - float(_n_strata(T))


def ws_df(vL, dfL, vU, dfU):
    """Welch-Satterthwaite combination of the two terms' degrees of freedom."""
    num = (vL + vU) ** 2
    den = vL ** 2 / dfL + np.where(vU > 0, vU ** 2 / np.where(dfU > 0, dfU, np.nan), 0.0)
    return np.where(den > 0, num / np.where(den > 0, den, 1.0), dfL)


def fpc_factor(G_L, G_pop):
    return np.clip(1.0 - np.asarray(G_L, dtype=float) / float(G_pop), 0.0, 1.0)


def variances(res, G_pop=None):
    """All analytic variance-reference pairs for one estimate. Returns dict
    name -> (var, df); df = np.inf means a normal reference."""
    L, U = res["L"], res["U"]
    out = {"iid_z": (var_iid(res), np.full(L["mask"].shape[1], np.inf))}
    vL1, vU1 = var_term_cr1(L), var_term_cr1(U)
    vL2, vU2 = var_term_cr2(L), var_term_cr2(U)
    dL1, dU1 = df_term_cr1(L), df_term_cr1(U)
    dL2, dU2 = df_term_bm(L), df_term_bm(U)
    fac = [(False, 1.0)]
    if G_pop is not None:
        fac.append((True, fpc_factor(res["G_L"], G_pop)))
    for is_fpc, f in fac:
        sfx = "|fpc" if is_fpc else ""
        out["CR1_t" + sfx] = (f * vL1 + vU1, dL1)
        out["CR2_bm" + sfx] = (f * vL2 + vU2, dL2)
        out["CR1_ws" + sfx] = (f * vL1 + vU1, ws_df(f * vL1, dL1, vU1, dU1))
        out["CR2_ws" + sfx] = (f * vL2 + vU2, ws_df(f * vL2, dL2, vU2, dU2))
    return out


def design_exact_var(pop, D, Lm, Um, lam, G_pop):
    """PROPOSAL (plan section 8 item 6). Linearised design variance of the PPI estimator when
    U is exactly the complement of L in a fixed population of G_pop donors and L is a simple
    random sample of G_L donors without replacement. The estimator is written as a function
    of the labelled sums X = sum_L (n_d, Z_d, F_d), with the population totals known:
        theta = cU (F_tot - X_F) / (N_tot - X_n) + (X_Z - lam X_F) / X_n.
    Its linearised variance is G_L (1 - G_L/G) s^2_e with e_d = grad . x_d and s^2 the sample
    variance over labelled donors. For the donor population x_d = (1, t_d, tf_d).
    Lambdas (per labelled donor, and cU on the unlabelled mean) are treated as fixed.
    """
    if pop == "spot":
        nd, Zd, Fd = D["n"], D["Sz"], D["Sf"]
    else:
        t, tf = donor_values(D)
        nd, Zd, Fd = np.ones_like(t), t, tf
    A = Lm | Um
    Ntot, Ftot = _m(nd, A), _m(Fd, A)
    Xn, XZ, XF = _m(nd, Lm), _m(Zd, Lm), _m(Fd, Lm)
    c = lam["cU"]
    lamL = lam["lamL"]
    XR = _m(Zd - lamL * Fd, Lm)
    g_n = c * (Ftot - XF) / (Ntot - Xn) ** 2 - XR / Xn ** 2
    e = (g_n[None, :] * nd + Zd / Xn[None, :] - (c / (Ntot - Xn))[None, :] * Fd
         - lamL * Fd / Xn[None, :])
    GL = Lm.sum(0)
    em = _m(e, Lm) / GL
    s2 = _m((e - em) ** 2, Lm) / (GL - 1.0)
    return GL * fpc_factor(GL, G_pop) * s2, GL - 1.0


# ============================================================== intervals
def t_interval(theta, var, df, alpha=ALPHA):
    se = np.sqrt(np.maximum(var, 0.0))
    q = np.where(np.isinf(df), stats.norm.ppf(1 - alpha / 2),
                 stats.t.ppf(1 - alpha / 2, np.where(np.isinf(df), 1.0, df)))
    return theta - q * se, theta + q * se


# ============================================================== bootstrap
def _gather(x, mask):
    """Columns of x restricted to the masked donors, in ascending donor order.
    Returns (k, ncol); k is constant across columns."""
    k = int(mask.sum(0)[0])
    assert np.all(mask.sum(0) == k), "term size must be constant across columns"
    idx = np.argsort(~mask, axis=0, kind="stable")[:k]
    return np.take_along_axis(x, idx, axis=0)


def draw_counts(k, n_boot, ncol, rng, shared=False):
    """Multinomial donor counts. shared=True gives one (n_boot, k) matrix used for every
    column, drawn exactly as round3_b1_ppi.py draws it."""
    if k == 0:
        return None
    if shared:
        return rng.multinomial(k, np.full(k, 1.0 / k), size=n_boot).astype(float)
    return rng.multinomial(k, np.full(k, 1.0 / k), size=(ncol, n_boot)).astype(float)


def _cdot(cnt, x):
    """cnt (B, k) or (ncol, B, k) times x (k, ncol) -> (ncol, B)."""
    if cnt.ndim == 2:
        return (cnt @ x).T
    return np.einsum("cbk,kc->cb", cnt, x)


def bootstrap(pop, D, Lm, Um, lam, theta_hat, se_hat, n_boot=N_BOOT, seed=0,
              alpha=ALPHA, shared=False, cntL=None, cntU=None):
    """Donor bootstrap within L and within U, lambda held fixed. Returns dict of (lo, hi)
    for 'boot_pct', 'boot_t', 'boot_bca', and the bootstrap se."""
    ncol = Lm.shape[1]
    GL, GU = int(Lm.sum(0)[0]), int(Um.sum(0)[0])
    lamL = lam["lamL"]
    cU = lam["cU"]
    if cntL is None:
        rng = seed_rng(seed)
        cntL = draw_counts(GL, n_boot, ncol, rng, shared)
        cntU = draw_counts(GU, n_boot, ncol, rng, shared) if GU else None
    if pop == "spot":
        nL = _gather(D["n"], Lm); SrL = _gather(D["Sz"] - lamL * D["Sf"], Lm)
        Sr2 = _gather((D["Sz"] - lamL * D["Sf"]) ** 2, Lm)
        n_L = _cdot(cntL, nL); R1 = _cdot(cntL, SrL)
        rb = R1 / n_L
        vL = (_cdot(cntL, Sr2) - 2 * rb * _cdot(cntL, nL * SrL) + rb ** 2 * _cdot(cntL, nL ** 2)) / n_L ** 2
        th = rb
        vU = 0.0
        if GU:
            nU = _gather(D["n"], Um); SfU = _gather(D["Sf"], Um)
            N_U = _cdot(cntU, nU); F1 = _cdot(cntU, SfU)
            fb = F1 / N_U
            th = th + cU[:, None] * fb
            vU = cU[:, None] ** 2 * (_cdot(cntU, SfU ** 2) - 2 * fb * _cdot(cntU, nU * SfU)
                                      + fb ** 2 * _cdot(cntU, nU ** 2)) / N_U ** 2
    else:
        t, tf = donor_values(D)
        rL = _gather(t - lamL * tf, Lm)
        m1 = _cdot(cntL, rL) / GL
        vL = (_cdot(cntL, rL ** 2) / GL - m1 ** 2) / GL
        th = m1
        vU = 0.0
        if GU:
            fU = _gather(tf, Um)
            u1 = _cdot(cntU, fU) / GU
            th = th + cU[:, None] * u1
            vU = cU[:, None] ** 2 * (_cdot(cntU, fU ** 2) / GU - u1 ** 2) / GU
    cL1 = GL / (GL - 1.0) if GL > 1 else np.nan
    cU1 = GU / (GU - 1.0) if GU > 1 else 0.0
    se_star = np.sqrt(np.maximum(cL1 * vL + cU1 * vU, 0.0))
    q = [100.0 * alpha / 2.0, 100.0 * (1.0 - alpha / 2.0)]
    out = {"boot_pct": (np.percentile(th, q[0], axis=1), np.percentile(th, q[1], axis=1)),
           "se_boot": th.std(axis=1, ddof=1)}
    tstar = (th - theta_hat[:, None]) / np.where(se_star > 0, se_star, np.nan)
    tlo = np.nanpercentile(tstar, q[1], axis=1)
    thi = np.nanpercentile(tstar, q[0], axis=1)
    out["boot_t"] = (theta_hat - tlo * se_hat, theta_hat - thi * se_hat)
    # BCa: bias correction from the bootstrap draws, acceleration from the donor jackknife
    p0 = (th < theta_hat[:, None]).mean(1) + 0.5 * (th == theta_hat[:, None]).mean(1)
    z0 = stats.norm.ppf(np.clip(p0, 1e-12, 1 - 1e-12))
    jk = _jackknife(pop, D, Lm, Um, lam)
    jm = jk.mean(0)
    d = jm[None, :] - jk
    acc = (d ** 3).sum(0) / (6.0 * np.maximum((d ** 2).sum(0), 1e-300) ** 1.5)
    za = stats.norm.ppf([alpha / 2.0, 1.0 - alpha / 2.0])
    ths = np.sort(th, axis=1)
    lo_hi = []
    for z in za:
        a1 = stats.norm.cdf(z0 + (z0 + z) / (1.0 - acc * (z0 + z)))
        lo_hi.append(_row_quantile(ths, a1))
    out["boot_bca"] = (lo_hi[0], lo_hi[1])
    return out


def _row_quantile(xs, a):
    """Per-row quantile at level a (in [0, 1]) of row-sorted xs, numpy's default 'linear'
    method, vectorised over rows."""
    B = xs.shape[1]
    pos = np.clip(np.asarray(a, dtype=float), 0.0, 1.0) * (B - 1)
    ok = np.isfinite(pos)
    pos = np.where(ok, pos, 0.0)
    lo = np.floor(pos).astype(int)
    hi = np.minimum(lo + 1, B - 1)
    fr = pos - lo
    r = np.arange(xs.shape[0])
    v = xs[r, lo] * (1.0 - fr) + xs[r, hi] * fr
    return np.where(ok, v, np.nan)


def _jackknife(pop, D, Lm, Um, lam):
    """Leave-one-donor-out estimates over all labelled and unlabelled donors, lambda fixed.
    Returns (G_L + G_U, ncol)."""
    lamL, cU = lam["lamL"], lam["cU"]
    if pop == "spot":
        n = D["n"]
        Sr = np.where(Lm, D["Sz"] - lamL * D["Sf"], 0.0)
        SL, nL = Sr.sum(0), _m(n, Lm)
        SfU, NU = _m(D["Sf"], Um), _m(n, Um)
        rbar = SL / nL
        fb = _safe_div(SfU, NU)
        jl = cU * fb + (SL - Sr) / (nL - np.where(Lm, n, 0.0))
        ju = cU * (SfU - D["Sf"]) / (NU - n) + rbar
    else:
        t, tf = donor_values(D)
        GL, GU = Lm.sum(0), Um.sum(0)
        r = np.where(Lm, t - lamL * tf, 0.0)
        SL = r.sum(0)
        SU = _m(tf, Um)
        fb = _safe_div(SU, GU)
        jl = cU * fb + (SL - r) / (GL - 1.0)
        ju = cU * (SU - np.where(Um, tf, 0.0)) / (GU - 1.0) + SL / GL
    L = _gather(jl, Lm)
    if Um.sum(0)[0] > 0:
        return np.concatenate([L, _gather(ju, Um)], axis=0)
    return L


# ============================================================== the textbook form
# Addendum 1 section 2 (plan section 11.2). For the DESIGN-BASED target the population is the
# fixed set of G donors and predictions exist on every spot of every donor, so the primary
# estimator is the textbook difference estimator with the prediction term over the WHOLE
# population (labelled donors included). The only randomness is which n_L of the G donors are
# labelled (simple random sampling without replacement), and the finite-population correction
# is then exact for the mean.
#   donor-weighted  theta = lam/G sum_{all g} tf_g + 1/n_L sum_{g in L} (t_g - lam_g tf_g)
#                   Var  = (1 - n_L/G) s_r^2 / n_L,           t_{n_L - 1}
#   spot-weighted   theta = lam/N sum_{all i} f_i + G/(N n_L) sum_{g in L} R_g,
#                   R_g = sum_{i in g} (z_i - lam_g f_i)
#                   Var  = (1 - n_L/G) (G/N)^2 s_R^2 / n_L,    t_{n_L - 1}
# lam_g is the lambda applied to labelled donor g (one value for rules a and b; the other
# half's value under cross-fitting) and the coefficient on the population term is cU, as in the
# complement form. The lambda rules are unchanged (addendum 1): they are computed exactly as
# for the complement form, with U the unlabelled donors, and then plugged in.
def estimate_textbook(pop, D, Lm, Am, lam):
    """Am is the population mask (all G donors). Returns dict(theta, e, G, n_L) with e the
    per-labelled-donor terms whose sample variance gives the variance."""
    lamL, cU = lam["lamL"], lam["cU"]
    GL = Lm.sum(0).astype(float)
    G = Am.sum(0).astype(float)
    if pop == "spot":
        N = _m(D["n"], Am)
        Ftot = _m(D["Sf"], Am)
        R = np.where(Lm, D["Sz"] - lamL * D["Sf"], 0.0)
        theta = cU * Ftot / N + (G / (N * GL)) * R.sum(0)
        e = np.where(Lm, (G / N)[None, :] * R, 0.0)   # scaled so Var = (1-f) s_e^2 / n_L
    else:
        t, tf = donor_values(D)
        Ftot = _m(tf, Am)
        R = np.where(Lm, t - lamL * tf, 0.0)
        theta = cU * Ftot / G + R.sum(0) / GL
        e = R
    return dict(theta=theta, e=e, mask=Lm, G=G, n_L=GL)


def var_textbook(tb, fpc=True):
    e, Lm, GL, G = tb["e"], tb["mask"], tb["n_L"], tb["G"]
    em = _m(e, Lm) / GL
    s2 = _m((e - em) ** 2, Lm) / (GL - 1.0)
    f = np.clip(1.0 - GL / G, 0.0, 1.0) if fpc else 1.0
    return f * s2 / GL, GL - 1.0


def bootstrap_textbook(tb, se_hat, n_boot=N_BOOT, seed=0, alpha=ALPHA):
    """Labelled donors resampled with replacement (the population term is fixed); lambda
    held fixed. Studentised on the non-fpc textbook standard error."""
    e, Lm, GL = tb["e"], tb["mask"], int(tb["n_L"][0])
    ncol = Lm.shape[1]
    rng = seed_rng(seed)
    cnt = draw_counts(GL, n_boot, ncol, rng, shared=False)
    eL = _gather(e, Lm)
    base = tb["theta"] - eL.mean(0)                  # the fixed population term
    m1 = _cdot(cnt, eL) / GL
    th = base[:, None] + m1
    v = (_cdot(cnt, eL ** 2) / GL - m1 ** 2) * GL / (GL - 1.0) / GL
    se_star = np.sqrt(np.maximum(v, 0.0))
    q = [100.0 * alpha / 2.0, 100.0 * (1.0 - alpha / 2.0)]
    theta_hat = tb["theta"]
    out = {"boot_pct": (np.percentile(th, q[0], axis=1), np.percentile(th, q[1], axis=1)),
           "se_boot": th.std(axis=1, ddof=1)}
    tstar = (th - theta_hat[:, None]) / np.where(se_star > 0, se_star, np.nan)
    out["boot_t"] = (theta_hat - np.nanpercentile(tstar, q[1], axis=1) * se_hat,
                     theta_hat - np.nanpercentile(tstar, q[0], axis=1) * se_hat)
    p0 = (th < theta_hat[:, None]).mean(1) + 0.5 * (th == theta_hat[:, None]).mean(1)
    z0 = stats.norm.ppf(np.clip(p0, 1e-12, 1 - 1e-12))
    jk = (eL.sum(0)[None, :] - eL) / (GL - 1.0) + base[None, :]
    d = jk.mean(0)[None, :] - jk
    acc = (d ** 3).sum(0) / (6.0 * np.maximum((d ** 2).sum(0), 1e-300) ** 1.5)
    ths = np.sort(th, axis=1)
    lo_hi = []
    for z in stats.norm.ppf([alpha / 2.0, 1.0 - alpha / 2.0]):
        a1 = stats.norm.cdf(z0 + (z0 + z) / (1.0 - acc * (z0 + z)))
        lo_hi.append(_row_quantile(ths, a1))
    out["boot_bca"] = (lo_hi[0], lo_hi[1])
    return out


def textbook_intervals(pop, D, Lm, Um, rule, seed=0, n_boot=N_BOOT, alpha=ALPHA,
                       do_boot=True):
    """Every interval of the textbook form for one estimator (rule 'none' = classical, for
    which the textbook form is the labelled-donor expansion mean). U is the complement of L
    and the population is L | U."""
    lam = lambda_rule(rule, pop, D, Lm, Um, seed=seed)
    tb = estimate_textbook(pop, D, Lm, Lm | Um, lam)
    th = tb["theta"]
    iv = {}
    for fpc in (False, True):
        v, df = var_textbook(tb, fpc=fpc)
        lo, hi = t_interval(th, v, df, alpha)
        iv["textbook_t" + ("|fpc" if fpc else "")] = dict(lo=lo, hi=hi, df=df, var=v)
    if do_boot:
        se0 = np.sqrt(np.maximum(iv["textbook_t"]["var"], 0.0))
        b = bootstrap_textbook(tb, se0, n_boot=n_boot, seed=f"tb|{seed}", alpha=alpha)
        for k in ("boot_pct", "boot_t", "boot_bca"):
            iv[k] = dict(lo=b[k][0], hi=b[k][1], df=np.full(th.shape, np.nan),
                         var=b["se_boot"] ** 2)
    return lam, tb, iv


# ============================================================== one call for everything
def all_intervals(pop, D, Lm, Um, rule, truth, G_pop=None, seed=0, n_boot=N_BOOT,
                  alpha=ALPHA, do_boot=True, design_exact=False, shared_boot=False,
                  with_ws=True):
    """Every interval of the Q1 comparison for one estimator (rule 'none' = classical) in the
    complement form. Returns (lam dict, res, dict name -> dict(lo, hi, df, var))."""
    lam = lambda_rule(rule, pop, D, Lm, Um, seed=seed)
    res = estimate(pop, D, Lm, Um, lam)
    th = res["theta"]
    iv = {}
    for name, (v, df) in variances(res, G_pop).items():
        if not with_ws and "_ws" in name:
            continue
        lo, hi = t_interval(th, v, df, alpha)
        iv[name] = dict(lo=lo, hi=hi, df=df, var=v)
    if design_exact and G_pop is not None:
        v, df = design_exact_var(pop, D, Lm, Um, lam, G_pop)
        lo, hi = t_interval(th, v, df, alpha)
        iv["design_exact_t"] = dict(lo=lo, hi=hi, df=df, var=v)
    if lam.get("classical_cols") is not None and lam["classical_cols"].any():
        # Rule (d): where both halves fail the pre-test the estimator is classical, so the
        # classical estimate and its variances replace the cross-fitted ones in those columns.
        cc = lam["classical_cols"]
        lam0 = lambda_rule("none", pop, D, Lm, Um, seed=seed)
        res0 = estimate(pop, D, Lm, Um, lam0)
        th0 = res0["theta"]
        for name, (v, df) in variances(res0, G_pop).items():
            if name not in iv:
                continue
            lo, hi = t_interval(th0, v, df, alpha)
            for key, val in (("lo", lo), ("hi", hi), ("df", df), ("var", v)):
                iv[name][key] = np.where(cc, val, iv[name][key])
        if "design_exact_t" in iv:
            v, df = design_exact_var(pop, D, Lm, Um, lam0, G_pop)
            lo, hi = t_interval(th0, v, df, alpha)
            for key, val in (("lo", lo), ("hi", hi), ("df", df), ("var", v)):
                iv["design_exact_t"][key] = np.where(cc, val, iv["design_exact_t"][key])
        res = dict(res, theta=np.where(cc, th0, th))
        th = res["theta"]
    if do_boot:
        se1 = np.sqrt(np.maximum(iv["CR1_t"]["var"], 0.0))
        b = bootstrap(pop, D, Lm, Um, lam, th, se1, n_boot=n_boot, seed=seed, alpha=alpha,
                      shared=shared_boot)
        for k in ("boot_pct", "boot_t", "boot_bca"):
            iv[k] = dict(lo=b[k][0], hi=b[k][1], df=np.full(th.shape, np.nan),
                         var=b["se_boot"] ** 2)
    return lam, res, iv
