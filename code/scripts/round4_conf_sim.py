#!/usr/bin/env python
"""Round 4, conformal track, stage C1: the simulation testbed and the known methods.

docs/round4_conf_plan.md section 4 (C1) and section 7 (conventions fixed before running).
One interface for the generator, every method and the oracle, so that C2's candidates plug in
through `register_method` without touching this file's code.

----------------------------------------------------------------------------------------------
THE GENERATOR (C1 "The generator"; plan section 7 items 1 to 3)

A replicate draws K calibration donors, one test donor with n_test = 500 evaluation spots, and a
stream of o_max initial observations from the same test donor; the method at o uses the first o
of that stream, so every o is evaluated on the same draw (paired across o).

  normal / t3   r_ki = a_k + b_k eps_ki, a_k ~ N(0, sigma_a^2), b_k = exp(tau eta_k),
                eta_k ~ N(0,1), eps standard normal or unscaled Student t_3; the score is |r|.
                sigma_a is solved per tail at tau = 0 so that the between-donor share of SCORE
                variance, Var(E[s | k]) / Var(s), equals the target share (plan section 7 item 1);
                the same sigma_a is kept at tau = 0.3 and the realised share is recorded.
  semireal      per gene g of CCRCC's 50 genes, donor-level parameters (mu_k, sigma_k, N_k) are
                resampled with replacement from the units of the round-3 score-moment file
                (a2_score_moments__<enc>.parquet, task CCRCC, design donor, every fold, draw and
                role), where (mu_k, sigma_k) are the folded-normal parameters matching that unit's
                score mean and variance; scores are |mu_k + sigma_k eps|. A replicate draws its
                gene uniformly. When a unit's mean-to-second-moment ratio is below the folded
                normal's floor 2/pi, mu_k = 0 and sigma_k matches the second moment; the number of
                such units is recorded. (Plan section 7 item 6.)

  N_k           equal at 100, 500 or 2000, or `unequal`: log-uniform on [100, 2000], rounded, per
                donor and replicate. On semireal N_k is the resampled unit's spot count unless a
                fixed N is requested.

THE ORACLE (C1 method 7; plan section 7 item 3)
  q_star        the (1 - alpha) quantile of the new-donor score mixture, from 10^6 spots each from
                a freshly drawn donor.
  own_raw       per replicate, the test donor's own (1 - alpha) quantile of |r| (what enough raw
                test observations would reveal).
  own_centred   per replicate, the test donor's own (1 - alpha) quantile of |r - a_k| (what enough
                test observations would reveal after recentring). Reported as half-widths only.

----------------------------------------------------------------------------------------------
THE KNOWN METHODS. For each: what it assumes and the guarantee it carries, written before it runs.
Every method returns a threshold q and a centre c for the test donor; a test spot is covered when
|r - c| <= q. Quantiles are Q_beta(nu) = inf{t : nu((-inf, t]) >= beta} with the atom at +inf,
evaluated with the relative tolerance 1e-12 that round 3's A3 weighted_quantile uses.

  pooled     split conformal on all sum_k N_k calibration spots with equal weights and one atom
             at +inf. Assumes spot-level exchangeability of calibration and test spots, which
             hierarchical data violate. Guarantee: none for a new donor.
  hcp        Lee, Barber and Willett: donor k's spots carry 1/((K+1) N_k), the test donor's mass
             1/(K+1) sits at +inf. Assumes hierarchical exchangeability. Guarantee: coverage at
             least 1 - alpha for any K; at most 1 - alpha + 2/(K+1) with distinct scores; infinite
             exactly when 1/(K+1) > alpha.
  one_per    Dunn, Wasserman and Ramdas, single subsampling: one spot per donor drawn uniformly,
             split conformal on the K scores. Assumes hierarchical exchangeability. Guarantee:
             coverage at least 1 - alpha (their Theorem 5); nontrivial iff K >= 1/alpha - 1.
  dwr_rep    Dunn, Wasserman and Ramdas, repeated subsampling, as their section 4.3 states it:
             B = 100 single subsamples, pi_b(s) = (1 + #{i : R_bi >= s})/(K+1), and the set
             {s : B^{-1} sum_b pi_b(s) >= alpha}; the threshold is therefore the m-th largest of
             the B K pooled subsample scores with m = ceil(B (alpha (K+1) - 1)), infinite when
             m <= 0. Guarantee as the paper states it: coverage at least 1 - 2 alpha (Theorem 10),
             "close to 1 - alpha in practice". NOTE the GHCP code's `repeated subsampling`
             baseline averages the B quantiles instead; that is not this definition.
  ghcp       Mallick, Tchetgen Tchetgen, Dobriban and Lee (arXiv:2608.15500 v1), eq. (4)-(5),
             Algorithm 1. Selection S = {k : N_k > o}, restricted to the m_eta smallest when
             eta > 0 (paper eq. 8, ties at random; `pool_rule='code'` reproduces the released
             code's pool, which is one group larger); donor J0 ~ Unif(S_eta); S_cal = S_eta \ {J0};
             the test donor is given size N_J0. Within-group training block m = floor(o/2) when
             adaptation is on and 0 when off; the centre of group j is c_j = lambda * mean of its
             first m residuals, lambda = m / (n_glob + m) (paper eq. 3 with |S_train| replaced by
             n_glob, the number of donors the fixed global predictor was trained on: in C1 the
             global predictor is the known zero mean and n_glob = 13, CCRCC's K = 10 training-donor
             count, fixed across cells). Held-out scores |r - c_j| carry 1/((|S_cal|+1) L_j),
             L_j = N_j - m; the test donor's o - m held-out scores carry 1/((|S_cal|+1) L_{K+1}),
             L_{K+1} = N_J0 - m, and (N_J0 - o)/((|S_cal|+1) L_{K+1}) sits at +inf. With S_eta
             empty it is split conformal within the test group with N_{K+1} = o + 1 (Remark 2.2).
             Assumes A1 (group-level exchangeability), A2 (reference sizes exchangeable and
             independent of the group laws) and A3 (within-group i.i.d.). Guarantee: coverage at
             least 1 - alpha (Theorem 2.1, Corollary 2.6 for eta > 0); upper bound
             1 - alpha + E[(1 + rho_o(max N))/|S|] under no ties. In C1 A1 to A3 hold by
             construction (sizes are drawn independently of a_k, b_k).
             Variants: ghcp (eta 0, adaptation on), ghcp_noad (eta 0, off), ghcp_r05 (eta 0.5,
             on, the paper's restricted pool, eq. 8, the rule Corollary 2.6 is stated for; in C1
             the groups outside the pool are unused because the global predictor is fixed), and
             at alpha = 0.1 only ghcp_r05code (the same with the released code's pool, one group
             larger), the secondary variant addendum 1 item 2 requires. At eta = 0 both pool rules
             give S = {k : N_k > o}.
  within     split conformal inside the test donor alone: c = mean of its first floor(o/2)
             residuals (lambda = 1), the other o - floor(o/2) scores calibrate, one atom at +inf.
             The GHCP paper's Std-CP with the absolute score. Assumes within-donor i.i.d.
             Guarantee: coverage at least 1 - alpha; infinite when 1/(o - floor(o/2) + 1) > alpha.

C2 candidates register with `register_fast(name, fn, uses_o)`; fn(prep, rep, cell, o, rng, alphas)
returns {variant_name: [(q, c) or None, one per alpha]}. The functions m_* and ghcp_q are the
reference implementations; the f_* functions are the fast path the runner uses, checked equal by
fast_equals_reference().
"""
import argparse
import json
import math
import os
import re
import sys
import time
import zlib

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy import stats

QTOL = 1e-12
O_GRID = (0, 5, 10, 25, 50, 100)
K_GRID = (5, 7, 9, 10, 12, 15, 20, 25, 50)
N_GRID = ("100", "500", "2000", "unequal")
SHARE_GRID = (0.1, 0.3, 0.5)
TAU_GRID = (0.0, 0.3)
ALPHA_GRID = (0.1, 0.2)
N_TEST = 500
N_REPS = 5000
DWR_B = 100
N_GLOB = 13
N_ORACLE = 10 ** 6


def crc(key):
    return zlib.crc32(key.encode())


# ============================================================================ quantiles
def wquantile(scores, weights, inf_mass, beta):
    """Q_beta of sum_i w_i delta_{s_i} + inf_mass delta_inf (weights need not be normalised with
    inf_mass; they are, by construction, in every caller). Relative tolerance QTOL as A3."""
    if len(scores) == 0:
        return math.inf
    o = np.argsort(scores, kind="stable")
    cw = np.cumsum(np.asarray(weights, float)[o])
    tot = cw[-1] + inf_mass
    idx = np.searchsorted(cw, beta * tot * (1 - QTOL), side="left")
    if idx >= len(cw):
        return math.inf
    return float(np.asarray(scores)[o][idx])


def split_q(scores, alpha):
    n = len(scores)
    k = math.ceil((n + 1) * (1 - alpha) * (1 - QTOL))
    if k > n or n == 0:
        return math.inf
    return float(np.partition(np.asarray(scores), k - 1)[k - 1])


# ============================================================================ generator
def _share_of(sigma_a, tail, n=400_000, seed=11):
    rng = np.random.default_rng(seed)
    na = 400
    a = rng.normal(0, 1, na) * sigma_a
    e = (rng.standard_normal((na, n // na)) if tail == "normal"
         else rng.standard_t(3, (na, n // na)))
    s = np.abs(a[:, None] + e)
    return float(s.mean(1).var() / s.var())


def solve_sigma_a(share, tail):
    """sigma_a with between-donor share of score variance = share at tau = 0 (bisection)."""
    if share == 0:
        return 0.0
    lo, hi = 0.0, 20.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if _share_of(mid, tail) < share:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def folded_normal_params(m, v):
    """(mu, sigma, floor_hit) of |N(mu, sigma^2)| with mean m and variance v."""
    m2 = v + m * m
    if m * m / m2 <= 2 / math.pi + 1e-12:
        return 0.0, math.sqrt(m2), True

    def mean_of(mu):
        s2 = m2 - mu * mu
        if s2 <= 0:
            return mu
        s = math.sqrt(s2)
        return s * math.sqrt(2 / math.pi) * math.exp(-mu * mu / (2 * s2)) + mu * (1 - 2 * stats.norm.cdf(-mu / s))
    lo, hi = 0.0, math.sqrt(m2) * (1 - 1e-12)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if mean_of(mid) < m:
            lo = mid
        else:
            hi = mid
    mu = 0.5 * (lo + hi)
    return mu, math.sqrt(max(m2 - mu * mu, 1e-300)), False


class SemiReal:
    """Per-gene pools of CCRCC donor units: (mu, sigma, n) folded-normal parameters."""

    def __init__(self, moments_path, task="CCRCC"):
        m = pd.read_parquet(moments_path)
        m = m[(m.task == task) & (m.design == "donor") & (m.score == "abs")]
        self.genes = sorted(m.gene.unique())
        self.pool, self.n_floor, rows = {}, 0, []
        for g, d in m.groupby("gene"):
            P = []
            for r in d.itertuples():
                mu, sg, hit = folded_normal_params(float(r.mean), float(r.variance))
                self.n_floor += hit
                P.append((mu, sg, int(r.n)))
                rows.append(dict(gene=g, unit_id=r.unit_id, fold=r.fold, cal_draw=r.cal_draw,
                                 unit_role=r.unit_role, n=r.n, mean=r.mean, variance=r.variance,
                                 q50=r.q50, q90=r.q90, mu=mu, sigma=sg, floor_hit=hit))
            self.pool[g] = np.array(P, float)
        self.fit = pd.DataFrame(rows)
        self.n_units = len(self.fit)

    def fit_quality(self):
        f = self.fit
        q50 = [stats.foldnorm.ppf(0.5, c=mu / s, scale=s) for mu, s in zip(f.mu, f.sigma)]
        q90 = [stats.foldnorm.ppf(0.9, c=mu / s, scale=s) for mu, s in zip(f.mu, f.sigma)]
        f = f.assign(q50_fit=q50, q90_fit=q90)
        # between-donor share of score variance per gene, from the unit moments
        g = f.groupby("gene").apply(lambda d: pd.Series(dict(
            between=float(np.var(d["mean"])), within=float(np.mean(d["variance"])))),
            include_groups=False)
        g["share"] = g.between / (g.between + g.within)
        return f, g


def draw_sizes(rng, spec, K):
    if spec == "unequal":
        return np.rint(np.exp(rng.uniform(math.log(100), math.log(2000), K))).astype(int)
    return np.full(K, int(spec))


def draw_replicate(cell, rng, o_max, semi=None):
    """Returns dict(cal=[r_k arrays], init=r (o_max), test=r (n_test), a=, b=, gene=)."""
    K = cell["K"]
    if cell["gen"] == "semireal":
        g = semi.genes[rng.integers(len(semi.genes))]
        P = semi.pool[g]
        idx = rng.integers(len(P), size=K + 1)
        mus, sgs, ns = P[idx, 0], P[idx, 1], P[idx, 2].astype(int)
        if cell["N"] != "data":
            ns[:K] = draw_sizes(rng, cell["N"], K)
        cal = [mus[k] + sgs[k] * rng.standard_normal(ns[k]) for k in range(K)]
        a, b = mus[K], sgs[K]
        init = a + b * rng.standard_normal(o_max)
        test = a + b * rng.standard_normal(cell["n_test"])
        return dict(cal=cal, init=init, test=test, a=a, b=b, gene=g, tail="normal")
    ns = draw_sizes(rng, cell["N"], K)
    a = rng.normal(0, 1, K + 1) * cell["sigma_a"]
    b = np.exp(cell["tau"] * rng.standard_normal(K + 1))
    eps = (lambda n: rng.standard_normal(n)) if cell["gen"] == "normal" else (lambda n: rng.standard_t(3, n))
    cal = [a[k] + b[k] * eps(ns[k]) for k in range(K)]
    init = a[K] + b[K] * eps(o_max)
    test = a[K] + b[K] * eps(cell["n_test"])
    return dict(cal=cal, init=init, test=test, a=a[K], b=b[K], gene=None, tail=cell["gen"])


def oracle_qstar(cell, alpha, semi=None, n=N_ORACLE):
    rng = np.random.default_rng(crc(f"oracle|{cell['cell_id']}|{alpha}"))
    if cell["gen"] == "semireal":
        out = {}
        for g in semi.genes:
            P = semi.pool[g]
            i = rng.integers(len(P), size=n)
            out[g] = float(np.quantile(np.abs(P[i, 0] + P[i, 1] * rng.standard_normal(n)), 1 - alpha))
        return out
    a = rng.normal(0, 1, n) * cell["sigma_a"]
    b = np.exp(cell["tau"] * rng.standard_normal(n))
    e = rng.standard_normal(n) if cell["gen"] == "normal" else rng.standard_t(3, n)
    return float(np.quantile(np.abs(a + b * e), 1 - alpha))


def own_quantiles(a, b, tail, alpha):
    """(own_raw, own_centred): quantiles of |a + b e| and |b e| at 1 - alpha (bisection on the
    exact CDF via scipy.special, 60 steps)."""
    from scipy import special
    cdf1 = special.ndtr if tail == "normal" else (lambda z: special.stdtr(3, z))
    lo, hi = 0.0, abs(a) + b * 200.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if cdf1((mid - a) / b) - cdf1((-mid - a) / b) < 1 - alpha:
            lo = mid
        else:
            hi = mid
    key = (tail, alpha)
    if key not in _PPF:
        _PPF[key] = float(stats.norm.ppf(1 - alpha / 2) if tail == "normal" else stats.t(3).ppf(1 - alpha / 2))
    return 0.5 * (lo + hi), float(b * _PPF[key])


_PPF = {}


# ============================================================================ methods
METHODS = {}


def register_method(name, fn, uses_o):
    METHODS[name] = (fn, uses_o)


def m_pooled(rep, cell, o, rng, alpha):
    s = np.abs(np.concatenate(rep["cal"]))
    return {"pooled": (split_q(s, alpha), 0.0)}


def hcp_q(cal_scores, alpha):
    K = len(cal_scores)
    s = np.concatenate(cal_scores)
    w = np.concatenate([np.full(len(x), 1.0 / ((K + 1) * len(x))) for x in cal_scores])
    return wquantile(s, w, 1.0 / (K + 1), 1 - alpha)


def m_hcp(rep, cell, o, rng, alpha):
    return {"hcp": (hcp_q([np.abs(x) for x in rep["cal"]], alpha), 0.0)}


def m_one_per(rep, cell, o, rng, alpha):
    s = np.array([abs(x[rng.integers(len(x))]) for x in rep["cal"]])
    return {"one_per": (split_q(s, alpha), 0.0)}


def m_dwr_rep(rep, cell, o, rng, alpha, B=DWR_B):
    K = len(rep["cal"])
    m = math.ceil(B * (alpha * (K + 1) - 1) * (1 - QTOL))
    if m <= 0:
        return {"dwr_rep": (math.inf, 0.0)}
    S = np.concatenate([np.abs(x[rng.integers(len(x), size=B)]) for x in rep["cal"]])
    return {"dwr_rep": (float(-np.partition(-S, m - 1)[m - 1]), 0.0)}


def restricted_pool(N, o, eta, rng, rule="paper"):
    S = np.where(N > o)[0]
    if eta <= 0 or len(S) == 0:
        return S
    K = len(N)
    m_eta = min(len(S), math.ceil((1 - eta) * K) + (1 if rule == "code" else 0))
    if m_eta == 0:
        return S[:0]
    sizes = np.sort(N[S])
    c = sizes[m_eta - 1]
    lt, eq = S[N[S] < c], S[N[S] == c]
    pick = rng.choice(eq, size=m_eta - len(lt), replace=False) if len(eq) else eq
    return np.sort(np.concatenate([lt, pick]).astype(int))


def ghcp_q(cal, init, o, alpha, rng, adapt=True, eta=0.0, n_glob=N_GLOB, pool_rule="paper",
           lam=None, J0=None):
    """GHCP threshold and test centre. cal: list of residual arrays; init: test residual stream."""
    N = np.array([len(x) for x in cal])
    m = (o // 2) if adapt else 0
    lamv = (m / (n_glob + m) if m > 0 else 0.0) if lam is None else lam
    S = restricted_pool(N, o, eta, rng, pool_rule)
    c_test = lamv * float(np.mean(init[:m])) if m > 0 else 0.0
    if len(S) == 0:     # Remark 2.2: within-group split conformal, N_{K+1} = o + 1
        held = np.abs(init[m:o] - c_test)
        L = o + 1 - m
        return wquantile(held, np.full(len(held), 1.0 / L), 1.0 / L, 1 - alpha), c_test
    J0 = S[rng.integers(len(S))] if J0 is None else int(J0)
    assert J0 in S, "donor must be in the pool"
    Scal = [j for j in S if j != J0]
    M = len(Scal) + 1
    sc, wt = [], []
    for j in Scal:
        x = cal[j]
        cj = lamv * float(np.mean(x[:m])) if m > 0 else 0.0
        h = np.abs(x[m:] - cj)
        sc.append(h)
        wt.append(np.full(len(h), 1.0 / (M * len(h))))
    Lt = N[J0] - m
    h = np.abs(init[m:o] - c_test)
    sc.append(h)
    wt.append(np.full(len(h), 1.0 / (M * Lt)))
    inf_mass = (N[J0] - o) / (M * Lt)
    return wquantile(np.concatenate(sc), np.concatenate(wt), inf_mass, 1 - alpha), c_test


def m_ghcp(rep, cell, o, rng, alpha):
    ng = cell.get("n_glob", N_GLOB)
    out = {}
    out["ghcp"] = ghcp_q(rep["cal"], rep["init"], o, alpha, rng, True, 0.0, ng)
    out["ghcp_noad"] = ghcp_q(rep["cal"], rep["init"], o, alpha, rng, False, 0.0, ng)
    out["ghcp_r05"] = ghcp_q(rep["cal"], rep["init"], o, alpha, rng, True, 0.5, ng)
    if abs(alpha - 0.1) < 1e-12:   # addendum 1 item 2: the released code's pool, secondary
        out["ghcp_r05code"] = ghcp_q(rep["cal"], rep["init"], o, alpha, rng, True, 0.5, ng,
                                     pool_rule="code")
    return out


def m_within(rep, cell, o, rng, alpha):
    m = o // 2
    c = float(np.mean(rep["init"][:m])) if m > 0 else 0.0
    return {"within": (split_q(np.abs(rep["init"][m:o] - c), alpha), c)}


register_method("pooled", m_pooled, False)
register_method("hcp", m_hcp, False)
register_method("one_per", m_one_per, False)
register_method("dwr_rep", m_dwr_rep, False)
register_method("ghcp", m_ghcp, True)
register_method("within", m_within, True)



# ============================================================================ fast path
class Prep:
    """Per-replicate sorted views of each calibration group's residuals, so that every method
    builds its sorted score arrays from presorted runs (merged by a stable sort in near-linear
    time). Results equal the reference functions above (checked in the C1 smoke)."""

    def __init__(self, cal):
        self.cal = cal
        self.N = np.array([len(x) for x in cal])
        self.order = [np.argsort(x, kind="stable") for x in cal]
        self.xs = [x[o] for x, o in zip(cal, self.order)]
        self.rank = []
        for o in self.order:
            r = np.empty_like(o)
            r[o] = np.arange(len(o))
            self.rank.append(r)

    def held_abs(self, j, m, c):
        """Two sorted runs whose union is {|x_i - c| : i >= m} for group j."""
        v = self.xs[j]
        if m > 0:
            keep = np.ones(len(v), bool)
            keep[self.rank[j][:m]] = False
            v = v[keep]
        k = np.searchsorted(v, c)
        return np.concatenate([(c - v[:k])[::-1], v[k:] - c])


def wquantiles(scores, weights, inf_mass, betas):
    if len(scores) == 0:
        return [math.inf] * len(betas)
    o = np.argsort(scores, kind="stable")
    cw = np.cumsum(weights[o])
    tot = cw[-1] + inf_mass
    s = scores[o]
    out = []
    for b in betas:
        i = np.searchsorted(cw, b * tot * (1 - QTOL), side="left")
        out.append(math.inf if i >= len(cw) else float(s[i]))
    return out


def split_qs(scores, alphas):
    n = len(scores)
    ks = [math.ceil((n + 1) * (1 - a) * (1 - QTOL)) for a in alphas]
    fin = [k for k in ks if 1 <= k <= n]
    part = np.partition(scores, [k - 1 for k in fin]) if fin else None
    return [float(part[k - 1]) if 1 <= k <= n else math.inf for k in ks]


def f_pooled(prep, rep, cell, o, rng, alphas):
    s = np.concatenate([prep.held_abs(j, 0, 0.0) for j in range(len(prep.N))])
    return {"pooled": [(q, 0.0) for q in split_qs(s, alphas)]}


def f_hcp(prep, rep, cell, o, rng, alphas):
    K = len(prep.N)
    s = np.concatenate([prep.held_abs(j, 0, 0.0) for j in range(K)])
    w = np.concatenate([np.full(n, 1.0 / ((K + 1) * n)) for n in prep.N])
    return {"hcp": [(q, 0.0) for q in wquantiles(s, w, 1.0 / (K + 1), [1 - a for a in alphas])]}


def f_one_per(prep, rep, cell, o, rng, alphas):
    s = np.array([abs(x[rng.integers(len(x))]) for x in prep.cal])
    return {"one_per": [(q, 0.0) for q in split_qs(s, alphas)]}


def f_dwr_rep(prep, rep, cell, o, rng, alphas, B=DWR_B):
    K = len(prep.N)
    S = np.concatenate([np.abs(x[rng.integers(len(x), size=B)]) for x in prep.cal])
    out = []
    for a in alphas:
        m = math.ceil(B * (a * (K + 1) - 1) * (1 - QTOL))
        out.append((math.inf, 0.0) if m <= 0 else (float(-np.partition(-S, m - 1)[m - 1]), 0.0))
    return {"dwr_rep": out}


def ghcp_fast(prep, init, o, alphas, rng, adapt=True, eta=0.0, n_glob=N_GLOB, pool_rule="paper",
              J0=None):
    N = prep.N
    m = (o // 2) if adapt else 0
    lamv = m / (n_glob + m) if m > 0 else 0.0
    S = restricted_pool(N, o, eta, rng, pool_rule)
    c_test = lamv * float(np.mean(init[:m])) if m > 0 else 0.0
    betas = [1 - a for a in alphas]
    if len(S) == 0:
        held = np.abs(init[m:o] - c_test)
        L = o + 1 - m
        return [(q, c_test) for q in wquantiles(held, np.full(len(held), 1.0 / L), 1.0 / L, betas)]
    J0 = S[rng.integers(len(S))] if J0 is None else int(J0)
    Scal = [j for j in S if j != J0]
    M = len(Scal) + 1
    sc, wt = [], []
    for j in Scal:
        cj = lamv * float(np.mean(prep.cal[j][:m])) if m > 0 else 0.0
        h = prep.held_abs(j, m, cj)
        sc.append(h)
        wt.append(np.full(len(h), 1.0 / (M * len(h))))
    Lt = N[J0] - m
    h = np.abs(init[m:o] - c_test)
    sc.append(h)
    wt.append(np.full(len(h), 1.0 / (M * Lt)))
    qs = wquantiles(np.concatenate(sc), np.concatenate(wt), (N[J0] - o) / (M * Lt), betas)
    return [(q, c_test) for q in qs]


def f_ghcp(prep, rep, cell, o, rng, alphas):
    ng = cell.get("n_glob", N_GLOB)
    out = {"ghcp": ghcp_fast(prep, rep["init"], o, alphas, rng, True, 0.0, ng),
           "ghcp_noad": ghcp_fast(prep, rep["init"], o, alphas, rng, False, 0.0, ng),
           "ghcp_r05": ghcp_fast(prep, rep["init"], o, alphas, rng, True, 0.5, ng)}
    if any(abs(a - 0.1) < 1e-12 for a in alphas):
        r = ghcp_fast(prep, rep["init"], o, alphas, rng, True, 0.5, ng, pool_rule="code")
        out["ghcp_r05code"] = [x if abs(a - 0.1) < 1e-12 else None for a, x in zip(alphas, r)]
    return out


def f_within(prep, rep, cell, o, rng, alphas):
    m = o // 2
    c = float(np.mean(rep["init"][:m])) if m > 0 else 0.0
    return {"within": [(q, c) for q in split_qs(np.abs(rep["init"][m:o] - c), alphas)]}


FAST = {}


def register_fast(name, fn, uses_o):
    """C2 candidates register here: fn(prep, rep, cell, o, rng, alphas) -> {variant: [(q, c) or
    None per alpha]}."""
    FAST[name] = (fn, uses_o)


for _n, _f, _u in (("pooled", f_pooled, False), ("hcp", f_hcp, False), ("one_per", f_one_per, False),
                   ("dwr_rep", f_dwr_rep, False), ("ghcp", f_ghcp, True), ("within", f_within, True)):
    register_fast(_n, _f, _u)

# ============================================================================ cells
def build_cells(K, include_semireal=True, semireal_N=("data", "500")):
    cells = []
    sig = {}
    for gen in ("normal", "t3"):
        for share in SHARE_GRID:
            sig[(gen, share)] = solve_sigma_a(share, gen)
        for N in N_GRID:
            for share in SHARE_GRID:
                for tau in TAU_GRID:
                    cells.append(dict(gen=gen, K=K, N=N, share=share, tau=tau,
                                      sigma_a=sig[(gen, share)]))
            cells.append(dict(gen=gen, K=K, N=N, share=0.0, tau=0.0, sigma_a=0.0))
    if include_semireal:
        for N in semireal_N:
            cells.append(dict(gen="semireal", K=K, N=N, share=float("nan"), tau=float("nan"),
                              sigma_a=float("nan")))
    for c in cells:
        c["n_test"] = N_TEST
        c["n_glob"] = N_GLOB
        c["cell_id"] = (f"{c['gen']}|K{K}|N{c['N']}|share{c['share']}|tau{c['tau']}")
    return cells, sig


# ============================================================================ runner
def run_cell(cell, alphas, n_reps, o_grid, semi=None, methods=None, seed_tag="C1"):
    """Per-replicate rows (one per alpha, method variant, o, replicate). Uses the fast path."""
    methods = methods or list(FAST)
    o_max = max(o_grid)
    qstar = {a: oracle_qstar(cell, a, semi) for a in alphas}
    rows = []
    for r in range(n_reps):
        rng = np.random.default_rng(crc(f"{seed_tag}|{cell['cell_id']}|rep{r}"))
        rep = draw_replicate(cell, rng, o_max, semi)
        prep = Prep(rep["cal"])
        test = rep["test"]
        own = {a: own_quantiles(rep["a"], rep["b"], rep["tail"], a) for a in alphas}
        qsv = {a: (qstar[a][rep["gene"]] if isinstance(qstar[a], dict) else qstar[a]) for a in alphas}
        for mname in methods:
            fn, uses_o = FAST[mname]
            for o in (o_grid if uses_o else (0,)):
                if mname == "within" and o == 0:
                    continue
                mrng = np.random.default_rng(crc(f"{seed_tag}|{cell['cell_id']}|rep{r}|{mname}|o{o}"))
                for vname, res in fn(prep, rep, cell, o, mrng, alphas).items():
                    for a, qc in zip(alphas, res):
                        if qc is None:
                            continue
                        q, c = qc
                        cov = float(np.mean(np.abs(test - c) <= q)) if np.isfinite(q) else 1.0
                        rows.append((a, vname, o, r, cov, q, qsv[a], own[a][0], own[a][1],
                                     rep["gene"] or ""))
    return pd.DataFrame(rows, columns=["alpha", "method", "o", "rep", "coverage", "q", "q_star",
                                       "own_raw", "own_centred", "gene"])


def fast_equals_reference(n=60, seed_tag="C1fastcheck"):
    """Max |difference| between the fast path and the reference functions on random replicates."""
    worst = 0.0
    for t in range(n):
        rng = np.random.default_rng(crc(f"{seed_tag}|{t}"))
        K = int(rng.choice([5, 9, 10, 20]))
        cell = dict(gen="t3" if t % 2 else "normal", K=K, N=str(rng.choice(["100", "500", "unequal"])),
                    sigma_a=float(rng.choice([0.0, 1.0])), tau=float(rng.choice([0.0, 0.3])),
                    n_test=50, n_glob=N_GLOB)
        rep = draw_replicate(cell, rng, 100, None)
        prep = Prep(rep["cal"])
        for a in (0.1, 0.2):
            pairs = [(f_pooled(prep, rep, cell, 0, None, [a])["pooled"][0][0],
                      m_pooled(rep, cell, 0, None, a)["pooled"][0]),
                     (f_hcp(prep, rep, cell, 0, None, [a])["hcp"][0][0],
                      m_hcp(rep, cell, 0, None, a)["hcp"][0])]
            for o in O_GRID:
                for ad, eta, rule in ((True, 0.0, "paper"), (False, 0.0, "paper"), (True, 0.5, "paper"),
                                      (True, 0.5, "code")):
                    r1 = np.random.default_rng(t * 1000 + o)
                    r2 = np.random.default_rng(t * 1000 + o)
                    qf, cf = ghcp_fast(prep, rep["init"], o, [a], r1, ad, eta, N_GLOB, rule)[0]
                    qr, cr = ghcp_q(rep["cal"], rep["init"], o, a, r2, ad, eta, N_GLOB, rule)
                    pairs.append((qf, qr))
                    pairs.append((cf, cr))
            for x, y in pairs:
                if np.isfinite(x) or np.isfinite(y):
                    worst = max(worst, abs(x - y) if np.isfinite(x) and np.isfinite(y) else math.inf)
    return worst


def summarise(rr, cell):
    out = []
    for (a, m, o), d in rr.groupby(["alpha", "method", "o"]):
        fin = np.isfinite(d.q.values)
        n = len(d)
        cov = d.coverage.values
        pr = (d.q.values / d.q_star.values)
        out.append(dict(
            cell_id=cell["cell_id"], gen=cell["gen"], K=cell["K"], N=cell["N"],
            share=cell["share"], tau=cell["tau"], sigma_a=cell["sigma_a"], alpha=a, method=m,
            o=o, n_reps=n, coverage=float(cov.mean()), coverage_sd=float(cov.std(ddof=1)),
            coverage_mcse=float(cov.std(ddof=1) / math.sqrt(n)),
            frac_infinite=float(1 - fin.mean()),
            halfwidth_mean=float(d.q.values[fin].mean()) if fin.any() else math.inf,
            halfwidth_median=float(np.median(d.q.values[fin])) if fin.any() else math.inf,
            price=float(pr[fin].mean()) if fin.all() else math.inf,
            price_finite_reps=float(pr[fin].mean()) if fin.any() else math.inf,
            price_median=float(np.median(pr)) if fin.mean() > 0.5 else math.inf,
            q_star=float(d.q_star.mean()), own_raw_mean=float(d.own_raw.mean()),
            own_centred_mean=float(d.own_centred.mean()),
            price_own_raw=float((d.own_raw / d.q_star).mean()),
            price_own_centred=float((d.own_centred / d.q_star).mean())))
    return out


GRID_SCHEMA = pa.schema([
    ("cell_id", pa.string()), ("gen", pa.string()), ("K", pa.int64()), ("N", pa.string()),
    ("share", pa.float64()), ("tau", pa.float64()), ("sigma_a", pa.float64()),
    ("alpha", pa.float64()), ("method", pa.string()), ("o", pa.int64()), ("n_reps", pa.int64()),
    ("coverage", pa.float64()), ("coverage_sd", pa.float64()), ("coverage_mcse", pa.float64()),
    ("frac_infinite", pa.float64()), ("halfwidth_mean", pa.float64()),
    ("halfwidth_median", pa.float64()), ("price", pa.float64()),
    ("price_finite_reps", pa.float64()), ("price_median", pa.float64()), ("q_star", pa.float64()),
    ("own_raw_mean", pa.float64()), ("own_centred_mean", pa.float64()),
    ("price_own_raw", pa.float64()), ("price_own_centred", pa.float64()),
    ("realised_share", pa.float64())])

REP_SCHEMA = pa.schema([
    ("cell_id", pa.string()), ("alpha", pa.float64()), ("method", pa.string()), ("o", pa.int64()),
    ("rep", pa.int64()), ("coverage", pa.float64()), ("q", pa.float64()), ("q_star", pa.float64()),
    ("own_raw", pa.float64()), ("own_centred", pa.float64()), ("gene", pa.string())])


def realised_share(cell, semi=None, n_don=4000, n_per=200):
    if cell["gen"] == "semireal":
        return float("nan")
    rng = np.random.default_rng(crc(f"share|{cell['cell_id']}"))
    a = rng.normal(0, 1, n_don) * cell["sigma_a"]
    b = np.exp(cell["tau"] * rng.standard_normal(n_don))
    e = rng.standard_normal((n_don, n_per)) if cell["gen"] == "normal" else rng.standard_t(3, (n_don, n_per))
    s = np.abs(a[:, None] + b[:, None] * e)
    return float(s.mean(1).var() / s.var())


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--K", type=int, required=True)
    p.add_argument("--N", default=",".join(N_GRID) + ",semireal",
                   help="comma list of N specs to run in this job; 'semireal' adds those cells")
    p.add_argument("--reps", type=int, default=N_REPS)
    p.add_argument("--alphas", default="0.1,0.2")
    p.add_argument("--moments", default="/work/users/w/e/weiyang/hest_replication/results/"
                   "round3/A2_conditional/a2_score_moments__resnet50.parquet")
    p.add_argument("--out", required=True)
    p.add_argument("--tag", default="")
    p.add_argument("--cells-regex", default="", help="regex filter on cell_id, used to split a K "
                   "into Slurm jobs, e.g. '^t3\\|.*\\|N2000\\|share0\\.(1|3)'")
    a = p.parse_args(argv)
    t0 = time.time()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import round4_conf_io as IO
    os.makedirs(a.out, exist_ok=True)
    alphas = [float(x) for x in a.alphas.split(",")]
    Ns = a.N.split(",")
    cells, sig = build_cells(a.K, include_semireal="semireal" in Ns)
    cells = [c for c in cells if (c["gen"] == "semireal" or c["N"] in Ns)
             and re.search(a.cells_regex, c["cell_id"])]
    semi = SemiReal(a.moments) if any(c["gen"] == "semireal" for c in cells) else None
    suf = f"__K{a.K:02d}{a.tag}"
    summ = []
    os.makedirs(f"{a.out}/reps", exist_ok=True)
    for i, cell in enumerate(cells):
        tc = time.time()
        rr = run_cell(cell, alphas, a.reps, O_GRID, semi)
        rs = realised_share(cell)
        for row in summarise(rr, cell):
            row["realised_share"] = rs
            summ.append(row)
        rr.insert(0, "cell_id", cell["cell_id"])
        rr["gene"] = rr["gene"].astype(str)
        safe = re.sub(r"[^A-Za-z0-9.]+", "_", cell["cell_id"])
        pq.write_table(pa.Table.from_pandas(rr[[f.name for f in REP_SCHEMA]], schema=REP_SCHEMA,
                                            preserve_index=False), f"{a.out}/reps/c1_reps__{safe}.parquet")
        del rr
        print(f"[cell {i+1}/{len(cells)}] {cell['cell_id']} {time.time()-tc:.0f}s", flush=True)
        # summaries first, rewritten after every cell so a timeout keeps finished cells
        pd.DataFrame(summ).to_csv(f"{a.out}/c1_grid{suf}.csv", index=False)
    S = pd.DataFrame(summ)
    pq.write_table(pa.Table.from_pandas(S[[f.name for f in GRID_SCHEMA]], schema=GRID_SCHEMA,
                                        preserve_index=False), f"{a.out}/c1_grid{suf}.parquet")
    sa = pd.DataFrame([dict(gen=g, share=s, sigma_a=v) for (g, s), v in sig.items()])
    sa.to_csv(f"{a.out}/c1_sigma_a{suf}.csv", index=False)
    if semi is not None:
        f, g = semi.fit_quality()
        g.reset_index().to_csv(f"{a.out}/c1_semireal_gene_share{suf}.csv", index=False)
        pd.DataFrame([dict(n_units=semi.n_units, n_floor_hit=semi.n_floor,
                           q50_abs_err_median=float((f.q50_fit - f.q50).abs().median()),
                           q90_abs_err_median=float((f.q90_fit - f.q90).abs().median()),
                           q90_rel_err_median=float(((f.q90_fit - f.q90) / f.q90).abs().median()))]
                     ).to_csv(f"{a.out}/c1_semireal_fit{suf}.csv", index=False)
    cfg = dict(stage="C1", K=a.K, N=Ns, reps=a.reps, alphas=alphas, o_grid=list(O_GRID),
               n_test=N_TEST, dwr_B=DWR_B, n_glob=N_GLOB, n_oracle=N_ORACLE, qtol=QTOL,
               moments=a.moments, cells_regex=a.cells_regex, seed="zlib.crc32 keys C1|cell|rep")
    IO.write_provenance(a.out, "C1", __file__, cfg, extra={"wall_seconds": round(time.time() - t0),
                                                          "n_cells": len(cells)})
    print(f"[done] {len(cells)} cells {time.time()-t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
