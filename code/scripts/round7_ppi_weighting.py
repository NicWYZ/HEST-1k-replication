"""Round 7 inference track, S1: inclusion probabilities under D2 and the weighted estimators and intervals.

Theory: docs/round07/tracks/ppi/round07_ppi_theory.md sections 1 and 2.1. Arrays follow round 5's layout: cluster
values zbar, fbar (G, ncol) over the valid clusters, balance variables X (G, ncol or 1, k), labelled masks (G, ncol)
or, for many draws, (D, G, ncol).

* pi_stream: R accepted samples per column from D2 (fixed thresholds), as one i.i.d. candidate stream; returns
  inclusion counts (two halves kept apart), pair counts and the number of candidates.
* pi_exact: the same quantities by enumerating every sample, for the synthetic tests.
* pgh_apx_size, pgh_apx_bal: theory section 1.5.
* weighted(): Horvitz-Thompson, Hajek and the cross-fitted difference form with SYG or HT variances (section 1.4).
* bh(): Broska and Howes's interval for whole labelled clusters (section 2.1), and bh_direct(), its example-1 form.
"""
import itertools
import math
import zlib

import numpy as np
from scipy import stats

import round4_ppi_estimator as E
import round5_ppi_balance as BAL
import round5_ppi_estimator as R5

ALPHA = R5.ALPHA


def seed_of(s):
    return zlib.crc32(s.encode())


def srs_idx(rng, Gall, n, B):
    """B simple random samples of n of Gall, (B, n) int64 (row order random within a row is irrelevant)."""
    if n * (n - 1) / (2.0 * Gall) < 0.25:
        out = rng.integers(0, Gall, size=(int(B * 1.4) + 64, n))
        s = np.sort(out, axis=1)
        ok = (np.diff(s, axis=1) != 0).all(1)
        out = out[ok]
        while len(out) < B:
            extra = rng.integers(0, Gall, size=(B, n))
            s = np.sort(extra, axis=1)
            out = np.concatenate([out, extra[(np.diff(s, axis=1) != 0).all(1)]])
        return out[:B]
    return np.argsort(rng.random((B, Gall)), axis=1)[:, :n]


class Dist:
    """Mahalanobis distance of a sample's mean of X over its valid members from the valid-cluster mean, as
    round5_ppi_balance.mahalanobis_pool with round5_ppi_e4b_rejective.dist_valid (inf when fewer than two valid)."""

    def __init__(self, X, vid, Gall):
        G = X.shape[0]
        self.k = X.shape[2]
        self.Xc = X - X.mean(0, keepdims=True)                  # (G, ncol, k)
        S = np.einsum("gci,gcj->cij", self.Xc, self.Xc) / (G - 1)
        self.Si = np.linalg.pinv(S)
        self.vmap = np.full(Gall, -1, np.int64)
        self.vmap[vid] = np.arange(len(vid))
        self.G = G
        pad = np.zeros((1,) + self.Xc.shape[1:])
        self.Xp = np.concatenate([self.Xc, pad], 0)            # row G is the zero row for invalid donors

    def __call__(self, idx):
        vi = self.vmap[idx]                                      # (B, n), -1 invalid
        nv = (vi >= 0).sum(1).astype(float)
        vi = np.where(vi >= 0, vi, self.G)
        mL = self.Xp[vi].sum(1) / np.maximum(nv, 1)[:, None, None]   # (B, ncol, k)
        d = np.einsum("bci,cij,bcj->bc", mL, self.Si, mL)
        d[nv < 2] = np.inf
        return d


def pi_stream(X, vid, Gall, thr, n, R, seed_prefix, batch=20000, max_cand=400_000_000):
    """R accepted samples per column from D2. Returns dict(cnt_a, cnt_b (G, ncol) inclusion counts of the first
    and second halves of each column's accepted samples, pair (ncol, G, G) pair counts with zero diagonal, R,
    n_cand)."""
    dist = Dist(X, vid, Gall)
    G, ncol = len(vid), X.shape[1]
    cnt = np.zeros((2, G, ncol))
    pair = np.zeros((ncol, G * G))
    got = np.zeros(ncol, np.int64)
    n_cand, i = 0, 0
    half = R // 2
    tri = [(a, b) for a in range(n) for b in range(n) if a != b]
    ta, tb = np.array([t[0] for t in tri]), np.array([t[1] for t in tri])
    while (got < R).any():
        rng = np.random.default_rng(seed_of(f"{seed_prefix}|b{i}"))
        C = srs_idx(rng, Gall, n, batch)
        dd = dist(C)
        ok = dd <= thr[None, :]
        V = dist.vmap[C]                                          # (B, n)
        for j in np.flatnonzero(got < R):
            rows = np.flatnonzero(ok[:, j])[: R - got[j]]
            if not len(rows):
                continue
            Vj = V[rows]
            pos = got[j] + np.arange(len(rows))
            for h, sel in ((0, pos < half), (1, pos >= half)):
                if sel.any():
                    v = Vj[sel].ravel()
                    v = v[v >= 0]
                    cnt[h, :, j] += np.bincount(v, minlength=G)
            a, b = Vj[:, ta], Vj[:, tb]
            okp = (a >= 0) & (b >= 0)
            pair[j] += np.bincount((a * G + b)[okp], minlength=G * G)
            got[j] += len(rows)
        n_cand += batch
        i += 1
        if n_cand > max_cand:
            raise RuntimeError(f"fewer than {R} accepted after {n_cand} candidates")
    return dict(cnt_a=cnt[0], cnt_b=cnt[1], pair=pair.reshape(ncol, G, G), R=R, half=half, n_cand=n_cand)


def pi_exact(X, vid, Gall, thr, n):
    """Exact inclusion and pair probabilities by enumerating every sample of n of Gall (tests only)."""
    dist = Dist(X, vid, Gall)
    G, ncol = len(vid), X.shape[1]
    allc = np.array(list(itertools.combinations(range(Gall), n)), np.int64)
    pi = np.zeros((G, ncol)); pgh = np.zeros((ncol, G, G)); nacc = np.zeros(ncol)
    for c0 in range(0, len(allc), 200000):
        C = allc[c0:c0 + 200000]
        ok = dist(C) <= thr[None, :]
        V = dist.vmap[C]
        M = np.zeros((len(C), G))
        for col in range(n):
            vv = V[:, col]
            M[np.flatnonzero(vv >= 0), vv[vv >= 0]] = 1.0
        for j in range(ncol):
            Mj = M[ok[:, j]]
            pi[:, j] += Mj.sum(0); pgh[j] += Mj.T @ Mj; nacc[j] += ok[:, j].sum()
    pi /= nacc[None, :]
    pgh /= nacc[:, None, None]
    for j in range(ncol):
        np.fill_diagonal(pgh[j], 0.0)
    return pi, pgh, nacc


def from_counts(st):
    R = st["R"]
    cnt = st["cnt_a"] + st["cnt_b"]
    pi = cnt / R
    se = np.sqrt(pi * (1 - pi) / R)
    pgh = st["pair"] / R
    return pi, se, pgh


def pgh_apx_size(pi):
    """(G, ncol) -> (ncol, G, G) Hajek's approximation (theory section 1.5), zero diagonal."""
    a = pi * (1 - pi)
    d = a.sum(0)
    P = np.einsum("gc,hc->cgh", pi, pi) - np.einsum("gc,hc->cgh", a, a) / d[:, None, None]
    for j in range(P.shape[0]):
        np.fill_diagonal(P[j], 0.0)
    return P


def pgh_apx_bal(pi, X, va):
    """Balance-aware approximation (theory section 1.5). X (G, ncol or 1, k)."""
    G, ncol = pi.shape
    X = np.broadcast_to(X, (G, ncol, X.shape[2]))
    a = pi * (1 - pi)
    d = a.sum(0)
    xt = np.einsum("gc,gck->ck", a, X) / d[:, None]
    Xc = X - xt[None]
    V = np.einsum("gc,gci,gcj->cij", a, Xc, Xc)
    Vi = np.linalg.pinv(V)
    q = np.einsum("gci,cij,hcj->cgh", Xc, Vi, Xc)
    P = pgh_apx_size(pi) - (1 - va) * np.einsum("gc,hc->cgh", a, a) * q
    for j in range(ncol):
        np.fill_diagonal(P[j], 0.0)
    return P


def fix_nonpositive(P):
    """Replace nonpositive off-diagonal values by the smallest positive one of the column; returns (P, n_fixed)."""
    P = P.copy()
    nfix = 0
    G = P.shape[1]
    off = ~np.eye(G, dtype=bool)
    for j in range(P.shape[0]):
        bad = off & (P[j] <= 0)
        if bad.any():
            pos = P[j][off & (P[j] > 0)]
            P[j][bad] = pos.min() if len(pos) else 1e-12
            nfix += int(bad.sum())
    return P, nfix


def syg_var(L, a, W, denom):
    """L (D, G) bool, a (D, G) values (any outside L ignored), W (G, G) SYG coefficients with zero diagonal and
    zero where pi_gh = 0. Returns (D,) (1/(2 denom^2)) sum_{g != h in L} W_gh (a_g - a_h)^2."""
    Lf = L.astype(float)
    a = np.where(L, a, 0.0)
    WL = Lf @ W
    s1 = ((a ** 2) * WL).sum(1)
    s2 = np.einsum("dg,gh,dh->d", a, W, a)
    return (s1 - s2) / denom ** 2


def htv_var(L, b, pi, Q, denom):
    """Horvitz-Thompson variance for random size: b = y/pi, Q (G, G) = (pi_gh - pi_g pi_h)/pi_gh, zero diagonal."""
    b = np.where(L, b, 0.0)
    return (((1 - pi)[None, :] * b ** 2).sum(1) + np.einsum("dg,gh,dh->d", b, Q, b)) / denom ** 2


def coef(pi, pgh):
    """SYG W and HT Q coefficient matrices (G, G) for one column; zero where pgh == 0 and on the diagonal."""
    pp = np.outer(pi, pi)
    with np.errstate(divide="ignore", invalid="ignore"):
        W = np.where(pgh > 0, pp / pgh - 1.0, 0.0)
        Q = np.where(pgh > 0, 1.0 - pp / pgh, 0.0)
    np.fill_diagonal(W, 0.0); np.fill_diagonal(Q, 0.0)
    return W, Q


def weighted(zbar, fbar, Lall, pi, pghs, fixed_size, lam=None):
    """For D draws: Lall (D, G, ncol) bool; pi (G, ncol); pghs dict name -> (ncol, G, G).
    lam: optional (lamL (D, G, ncol), cU (D, ncol)) for the cross-fitted difference form.
    Returns dict: 'HT', 'H', ('HTl' if lam) -> dict(theta (D, ncol), var {name: (D, ncol)}, n_zero_pairs {name:
    (D, ncol)}, n_neg {name: (D, ncol)})."""
    D, G, ncol = Lall.shape
    Fbar = fbar.mean(0)
    out = {k: dict(theta=np.full((D, ncol), np.nan), var={nm: np.full((D, ncol), np.nan) for nm in pghs},
                   zero={nm: np.zeros((D, ncol)) for nm in pghs}) for k in (["HT", "H"] + (["HTl"] if lam else []))}
    for j in range(ncol):
        L = Lall[:, :, j]
        p = pi[:, j]
        ip = np.where(p > 0, 1.0 / np.where(p > 0, p, 1.0), np.nan)
        z = zbar[:, j][None, :]
        Lz = np.where(L, z * ip[None, :], 0.0)
        Nh = np.where(L, ip[None, :], 0.0).sum(1)
        ht = Lz.sum(1) / G
        h = Lz.sum(1) / Nh
        out["HT"]["theta"][:, j] = ht
        out["H"]["theta"][:, j] = h
        if lam:
            lamL, cU = lam[0][:, :, j], lam[1][:, j]
            r = zbar[:, j][None, :] - lamL * fbar[:, j][None, :]
            out["HTl"]["theta"][:, j] = cU * Fbar[j] + np.where(L, r * ip[None, :], 0.0).sum(1) / G
            e = r + (lamL - cU[:, None]) * Fbar[j]
            nn = L.sum(1).astype(float)
            dl = np.where(L, (lamL - cU[:, None]) ** 2, 0.0).sum(1) / nn
            fl = np.where(L, fbar[:, j][None, :], np.nan)
            sf2 = np.nanvar(fl, axis=1, ddof=1)
            xf = (nn / G) * dl * sf2 / nn
        u = zbar[:, j][None, :] - h[:, None]
        for nm, P in pghs.items():
            W, Q = coef(p, P[j])
            zero = (P[j] <= 0) & ~np.eye(G, dtype=bool)
            out_zero = np.einsum("dg,gh,dh->d", L.astype(float), zero.astype(float), L.astype(float)) / 2
            if fixed_size:
                vht = syg_var(L, z * ip[None, :], W, G)
                vh = syg_var(L, u * ip[None, :], W, Nh)
                vl = syg_var(L, e * ip[None, :], W, G) + xf if lam else None
            else:
                vht = htv_var(L, z * ip[None, :], p, Q, G)
                vh = htv_var(L, u * ip[None, :], p, Q, Nh)
                vl = htv_var(L, e * ip[None, :], p, Q, G) + xf if lam else None
            out["HT"]["var"][nm][:, j], out["H"]["var"][nm][:, j] = vht, vh
            out["HT"]["zero"][nm][:, j] = out["H"]["zero"][nm][:, j] = out_zero
            if lam:
                out["HTl"]["var"][nm][:, j] = vl
                out["HTl"]["zero"][nm][:, j] = out_zero
    return out


def bh(zbar, fbar, L, tiny=1e-24):
    """Broska and Howes's interval for whole labelled clusters (theory section 2.1). L (D, G, ncol) bool over the G
    clusters of the estimand. Returns dict(theta, se, lam, lam_zero) each (D, ncol); interval theta +- z se."""
    Lf = L.astype(float)
    n = Lf.sum(1)
    G = L.shape[1]
    N = G - n
    r = n / N
    Fbar = fbar.mean(0)[None, :]
    z = zbar[None]; f = fbar[None]
    zL = (Lf * z).sum(1) / n
    fL = (Lf * f).sum(1) / n
    fU = ((1 - Lf) * f).sum(1) / N
    fc = f - Fbar[:, None, :]
    Zh = (Lf - r[:, None, :] * (1 - Lf)) * fc

    def sig(theta):
        eps = Lf * (z - theta[:, None, :])
        return (eps ** 2).sum(1) / G, (eps * Zh).sum(1) / G, (Zh ** 2).sum(1) / G
    th1 = zL + (fU - fL)
    s11, s12, s22 = sig(th1)
    lz = s22 <= tiny * np.maximum(1.0, Fbar ** 2)
    lam = np.where(lz, 0.0, s12 / np.where(lz, 1.0, s22))
    th = zL + lam * (fU - fL)
    s11, s12, s22 = sig(th)
    sig2 = (G / n) * (s11 - 2 * lam * s12 + lam ** 2 * s22)
    return dict(theta=th, se=np.sqrt(np.maximum(sig2, 0) / n), lam=lam, lam_zero=lz)


def bh_direct(z, f, xi, lam):
    """Example-1 form for clusters of size one (theory section 2.1), one data set: z, f (G,), xi (G,) bool."""
    n, N = xi.sum(), (~xi).sum()
    Fbar = f.mean()
    th = z[xi].mean() + lam * (f[~xi].mean() - f[xi].mean())
    v_lab = np.mean(((z[xi] - th) - lam * (f[xi] - Fbar)) ** 2)
    v_unl = np.mean((f[~xi] - Fbar) ** 2)
    return th, v_lab + lam ** 2 * (n / N) * v_unl


def summarise(th, v, df, theta, normal=False):
    """th, v (D, ncol); df scalar or (D, ncol); returns per-gene dict of arrays. normal=True uses z quantiles.
    An interval is formed where v is finite and df >= 2 (or normal); negative v is set to 0 and counted."""
    D = th.shape[0]
    df = np.broadcast_to(np.asarray(df, float), th.shape)
    formed = np.isfinite(v) & np.isfinite(th) & (normal | (df >= 2))
    neg = formed & (v < 0)
    vv = np.where(formed, np.maximum(v, 0.0), np.nan)
    q = stats.norm.ppf(1 - ALPHA / 2) if normal else stats.t.ppf(1 - ALPHA / 2, np.where(df >= 1, df, np.nan))
    se = np.sqrt(vv)
    cov = np.where(formed, np.abs(th - theta[None, :]) <= q * se, np.nan)
    thf = np.where(np.isfinite(th), th, np.nan)
    nth = np.isfinite(thf).sum(0)
    mean = np.nanmean(thf, 0)
    sd = np.nanstd(thf, 0, ddof=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        bz = (mean - theta) / (sd / np.sqrt(nth))
    return dict(coverage=np.nanmean(cov, 0), width=np.nanmean(2 * q * se, 0), emp_var=sd ** 2,
                est_var=np.nanmean(vv, 0), bias=mean - theta, bias_z=bz, share_formed=formed.mean(0),
                share_neg=neg.sum(0) / np.maximum(formed.sum(0), 1), n_draws=np.full(th.shape[1], D))
