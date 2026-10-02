#!/usr/bin/env python
"""Round 4, conformal track, stage C3: the shared module for the real-data (K, o) map.

docs/round4_conf_plan.md section 6 (C3), section 7 (conventions), section 10 (addendum 1) and
section 12 (the C2 decision memo; 12.2 and 12.3 govern the methods below). Nothing in this file is
a result. It builds, for one (task, label set, encoder, K, fold, calibration draw), the fitted base
head and the absolute residuals, and forms every interval the C3 units need.

THE UNIT OF WORK. A `Fit` is one fold and one calibration draw: the base head fitted on the
training donors T (after the harness's size matching), the signed residuals r = y - yhat of every
calibration spot grouped by calibration donor, and of every test-donor spot, per gene. The score is
s = |r| (score `abs`). Interval for a test spot is [yhat + c - q, yhat + c + q]; c = 0 unless a
method recentres. Coverage and width follow round 3: per (test slide, gene) cell, slides with fewer
than 50 evaluation spots dropped (all kept if none has 50), then the unweighted mean over cells
(A3.fold_summary's chain); width_median is the median of the finite spot-gene widths of the fold,
as a4b's `width_median`. Infinite intervals count as covering and are reported as `finite = False`;
a width is never averaged over an infinite interval.

QUANTILE CONVENTION (memo 12.2 item 1). Q_beta(nu) = inf{t : nu((-inf, t]) >= beta} with the
relative tolerance 1e-12 of round4_conf_sim (QTOL), the same tolerance round 3's A3 uses. The
released GHCP code resolves an exact tie upward. Every row carries `finite_code`, the finiteness
the upward resolution would give (an exact tie at the last finite atom returns +inf), so the two
conventions are read side by side wherever they differ (alpha = 0.1, K = 10, o = 0 for GHCP).

DESIGN K. `K` in the output is the number of calibration donors of the design (the K axis of the
plan). `K_eff` in the full table is the number of exchangeable units the method's quantile rests on
(n_C for pooled, K for hcp and one_per, the pool size for ghcp, and so on). The training-donor
count (`n_T_donors`) falls as K rises and is recorded in every row.

----------------------------------------------------------------------------------------------
METHODS (assumption and guarantee, written before anything runs)

o = 0 (no labelled spot in the test donor)

  pooled      Split conformal on all calibration spots with equal weights, quantile level
              ceil((n+1)(1-alpha)) of the n calibration scores. Assumes spot-level exchangeability
              of calibration and test spots, which hierarchical data violate. Guarantee: none for
              a new donor; round 3's A1 interval.
  hcp         Lee, Barber and Willett. Calibration donor k's spots carry 1/((K+1) N_k), the test
              donor's mass 1/(K+1) sits at +inf (A3's W3). Assumes hierarchical exchangeability of
              donors, within donor exchangeability. Guarantee: coverage >= 1 - alpha for any K when
              the assumption holds; infinite exactly when 1/(K+1) > alpha (K <= 8 at alpha 0.1).
              Real donors are not exchangeable in features or in prediction error; the guarantee
              is conditional on that assumption, which A4b tested on CCRCC.
  one_per     Dunn, Wasserman and Ramdas single subsampling as round 3's a4b `dwr` applies it: one
              calibration spot drawn per donor, ordinary conformal quantile of the K scores,
              repeated `dwr_reps` times (200, crc32 seeds) with the coverage and width averaged over
              repetitions. Each repetition is a valid single-subsampling interval (coverage >=
              1 - alpha under hierarchical exchangeability, nontrivial iff K >= 1/alpha - 1);
              the average is a summary of valid intervals, not itself a conformal set. It is NOT
              the repeated-subsampling set of the paper's section 4.3, which C3 does not run
              (memo 12.2 item 5). Output name `one_per`; a4b called it `dwr`.

o > 0 (o labelled spots, uniform without replacement from the test donor's own spots; nested
across o by taking the first o of one seeded permutation per label draw; evaluation on the
donor's other spots)

  ghcp, ghcp_noad, ghcp_r05, ghcp_r05_noad, ghcp_r05code
              Mallick, Tchetgen Tchetgen, Dobriban and Lee, Algorithm 1, as round4_conf_sim.ghcp_q
              implements it (this module is a gene-vectorised copy, checked equal to ghcp_q in
              `selftest`). Selection S = {k : N_k > o}, restricted to the m_eta smallest when
              eta > 0 (eq. 8: ceil((1-eta)K) groups; `r05code` uses the released code's pool, one
              group larger); a donor J0 is drawn uniformly from the pool, the test donor is given
              size N_J0 and the other pool donors calibrate. Within-group adaptation: the first
              m = floor(o/2) residuals of each group recentre it with shrinkage
              lambda = m/(n_glob + m), n_glob = n_T_donors (the donors the base head was trained
              on); `_noad` sets m = 0. Held-out scores |r - c_j| carry 1/((|S_cal|+1) L_j); the
              test donor's o - m scores carry 1/((|S_cal|+1) L_{K+1}) and the rest, (N_J0 - o)/
              ((|S_cal|+1) L_{K+1}), sits at +inf. Assumes A1 group exchangeability, A2 sizes
              exchangeable with and independent of the group laws, A3 within-group exchangeable.
              On real donors A1 and A2 are not established (donor size is tied to the slide
              count, not drawn from the group law). Guarantee: coverage >= 1 - alpha under A1-A3
              (Thm 2.1; Cor 2.6 for eta > 0, whose pool rule is eq. 8, hence `ghcp_r05` is the
              primary variant per memo 12.2 item 2 and `ghcp_r05code` the secondary at alpha 0.1
              only). The calibration spots' order inside a donor, which fixes the adaptation
              block, is a seeded permutation (crc32 of task, fold, donor).
  within      Split conformal inside the test donor alone, the GHCP paper's Std-CP form: the mean
              of the first floor(o/2) labelled residuals recentres, the other o - floor(o/2)
              calibrate |r - c|. Assumes the labelled spots and the evaluation spots are exchangeable
              within the donor (true here by construction: the labelled spots are a uniform random
              subset of the donor's spots, so the guarantee is marginal over that draw). Guarantee:
              coverage >= 1 - alpha; infinite when 1/(o - floor(o/2) + 1) > alpha.
  within_plain
              (memo 12.3 item 1.) Split conformal inside the test donor with all o labelled
              spots calibrating the absolute score and no recentring: q = the ceil((o+1)(1-alpha))-th
              smallest of the o scores |r|, interval yhat +- q. Same assumption and guarantee as
              `within`: coverage >= 1 - alpha marginally over the labelled draw and the evaluation
              spot, from the exchangeability of the o labelled and the evaluation spots. Finite from
              o = 9 at alpha = 0.1 and o = 4 at alpha = 0.2. The coverage statement is for a
              random evaluation spot; the fold coverage reported here is the average over the
              donor's remaining spots for one labelled draw, so single-draw coverages scatter around
              the guarantee and only the mean over the 20 draws should be compared to it.
  recentred   The cheapest practitioner rule (plan C3, memo 12.3 item 4). The pooled cross-donor
              quantile q of the calibration scores |r| (the K-donor design's calibration set,
              round 3's `donor` design, uncentred) with the interval shifted by c, the mean of the
              labelled spots' residuals, per gene: yhat + c +- q. Assumes the calibration donors'
              scores are a fair proxy for the test donor's centred scores, which they are not:
              q still contains the between-donor bias that c removes from the test donor only, so
              the interval is expected to be conservative where the failure is bias and not where it
              is scale. Guarantee: none.

Reuses round4_conf_sim (restricted_pool, QTOL, and, in `selftest`, hcp_q, ghcp_q, wquantile,
split_q as the reference implementations) and round 3's harness, A3, a4b and D4 modules unedited.
----------------------------------------------------------------------------------------------
PUBLIC API: load_task, TaskData.specs, TaskData.fit, Fit, o0_rows, o_rows, to_c3, by_fold_table,
k_table, write_frag, selftest, metrics_vs_a3, O_GRID, K_GRID_CCRCC, K_GRID_LUNG, ALPHAS.
"""
import json
import math
import os
import sys
import time
import types
import zlib
from datetime import datetime, timezone

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_io as IO  # noqa: E402
import round4_conf_sim as SIM  # noqa: E402

QTOL = SIM.QTOL
ROOT = IO.DATA_ROOT
ENCODERS = ("hoptimus0", "uni_v2", "resnet50")
O_GRID = (5, 10, 25, 50, 100, 200)
K_GRID_CCRCC = (4, 6, 8, 10, 12, 14, 16, 18, 20)
K_GRID_LUNG = (6, 8, 10)
ALPHAS = (0.1, 0.2)
N_LABEL_DRAWS = 20
N_CAL_DRAWS = 3
MIN_SLIDE_SPOTS = 50
DWR_REPS = 200
SCORE = "abs"
O0_METHODS = ("pooled", "hcp", "one_per")
O_METHODS = ("ghcp", "ghcp_noad", "ghcp_r05", "ghcp_r05_noad", "ghcp_r05code", "within",
             "within_plain", "recentred")
GHCP_VARIANTS = {
    "ghcp": dict(adapt=True, eta=0.0, rule="paper"),
    "ghcp_noad": dict(adapt=False, eta=0.0, rule="paper"),
    "ghcp_r05": dict(adapt=True, eta=0.5, rule="paper"),
    "ghcp_r05_noad": dict(adapt=False, eta=0.5, rule="paper"),
    "ghcp_r05code": dict(adapt=True, eta=0.5, rule="code"),
}
FIXED_COLS = ["task", "label_set", "encoder", "method", "score", "alpha", "o", "K", "fold",
              "draw", "coverage", "width_mean", "width_median", "n_test", "finite"]
EXTRA_COLS = ["finite_code", "donor_set", "cal_draw", "label_draw", "K_eff", "n_T_donors",
              "n_T_natural", "n_T_matched", "n_C", "n_C_donors", "n_cells", "n_slides",
              "n_reps"]

TASKS = {
    "CCRCC:24": dict(task="CCRCC", out_task="CCRCC", kind="ccrcc", donor_set="24",
                     td=f"{ROOT}/results/round3/task_defs/CCRCC.json"),
    "CCRCC:23_merged": dict(task="CCRCC", out_task="CCRCC_23merged", kind="ccrcc",
                            donor_set="23_merged",
                            td=f"{ROOT}/results/round3/task_defs/CCRCC.json"),
    "INDIANA_KIDNEY": dict(task="INDIANA_KIDNEY", out_task="INDIANA_KIDNEY", kind="d4",
                           donor_set="25",
                           td=f"{ROOT}/results/round3/D4_expansion/task_defs/INDIANA_KIDNEY.json"),
    "LUNG_XENIUM": dict(task="LUNG_XENIUM", out_task="LUNG_XENIUM", kind="lung",
                        donor_set="15",
                        td=f"{ROOT}/results/round4/data/P5_task/LUNG_XENIUM.json"),
}

_MODS = {}


def _r3(name):
    if name not in _MODS:
        _MODS[name] = IO.import_round3(name)
    return _MODS[name]


def crc(key):
    return zlib.crc32(key.encode())


# ================================================================== quantile kernels
def split_q_cols(S, alphas):
    """Column-wise SIM.split_q for several alphas. S (n, G). Returns (q (A, G), finite_code (A,))
    where finite_code is the upward-tie reading (the released code's)."""
    n, G = S.shape
    q = np.full((len(alphas), G), np.inf)
    fcode = np.zeros(len(alphas), bool)
    for i, a in enumerate(alphas):
        k = math.ceil((n + 1) * (1 - a) * (1 - QTOL))
        kc = math.ceil((n + 1) * (1 - a) * (1 + QTOL))
        fcode[i] = (n > 0 and kc <= n)
        if n > 0 and 1 <= k <= n:
            q[i] = np.partition(S, k - 1, axis=0)[k - 1]
    return q, fcode


def wq_cols(S, w, inf_mass, betas):
    """Column-wise SIM.wquantile: S (n, G), w (n,) weights shared by the columns, inf_mass the
    atom at +inf. Returns (q (B, G), finite_code (B,)); the cumulative weights are built in each
    column's own stable sort order, exactly as SIM.wquantile does per gene."""
    n, G = S.shape
    q = np.full((len(betas), G), np.inf)
    if n == 0:
        return q, np.zeros(len(betas), bool)
    order = np.argsort(S, axis=0, kind="stable")
    Ss = np.take_along_axis(S, order, axis=0)
    cw = np.cumsum(w[order], axis=0)
    tot = cw[-1] + inf_mass
    cols = np.arange(G)
    fcode = np.zeros(len(betas), bool)
    for i, b in enumerate(betas):
        idx = (cw < (b * tot * (1 - QTOL))[None, :]).sum(axis=0)
        ok = idx < n
        q[i, ok] = Ss[idx[ok], cols[ok]]
        idc = (cw < (b * tot * (1 + QTOL))[None, :]).sum(axis=0)
        fcode[i] = bool((idc < n).all())
    return q, fcode


# ================================================================== metrics
def _summ(cov_rate, n_slide, width_cell, widths_fin):
    """A3.fold_summary's chain from per-(slide, gene) coverage rates. cov_rate, width_cell are
    (S, G); n_slide (S,); widths_fin the finite spot-gene widths of the fold."""
    use = n_slide >= MIN_SLIDE_SPOTS
    if not use.any():
        use = np.ones_like(use)
    cr, wc = cov_rate[use], width_cell[use]
    fin = np.isfinite(wc)
    return dict(coverage=float(cr.mean()),
                width_mean=float(wc[fin].mean()) if fin.any() else float("nan"),
                width_median=float(np.median(widths_fin)) if len(widths_fin) else float("nan"),
                n_cells=int(cr.size), n_slides=int(use.sum()))


class _Slides:
    """Row groups of the evaluation spots by test slide, in a fixed order."""

    def __init__(self, samp_E):
        self.names = list(np.unique(samp_E))
        self.idx = [np.flatnonzero(samp_E == s) for s in self.names]


def interval_metrics(Y, lo, hi, sl):
    """Metrics of [lo, hi] (n, G) against Y by the round-3 chain, from Y, lo, hi directly (the
    form A3.cell_metrics uses). Used for every o = 0 row."""
    cov = (Y >= lo) & (Y <= hi)
    width = hi - lo
    fin = np.isfinite(width)
    n_slide = np.array([len(i) for i in sl.idx])
    cr = np.stack([cov[i].mean(axis=0) for i in sl.idx])
    wf = np.where(fin, width, np.nan)
    wc = np.stack([_nanmean0(wf[i]) for i in sl.idx])
    out = _summ(cr, n_slide, wc, width[fin])
    out["finite"] = bool(fin.all())
    return out


def _nanmean0(a):
    ok = np.isfinite(a)
    cnt = ok.sum(axis=0)
    s = np.where(ok, a, 0.0).sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(cnt > 0, s / np.maximum(cnt, 1), np.nan)


def centred_metrics(R, keep, c, q, sl):
    """Metrics of yhat + c +- q on the kept rows, covered iff |r - c| <= q, width 2q at every
    spot of a gene (so the finite spot-gene widths have the same median as the finite 2q).
    R (n_E, G) signed residuals, keep (n_E,) bool, c, q (G,)."""
    cov = np.abs(R - c) <= q
    n_slide, cr = [], []
    for i in sl.idx:
        k = i[keep[i]]
        n_slide.append(len(k))
        cr.append(cov[k].mean(axis=0) if len(k) else np.full(R.shape[1], np.nan))
    n_slide = np.array(n_slide)
    cr = np.stack(cr)
    fin = np.isfinite(q)
    w = np.where(fin, 2.0 * q, np.nan)
    wc = np.where((n_slide[:, None] > 0) & fin[None, :], w[None, :], np.nan)
    # slides with no kept spot contribute no cell
    present = n_slide > 0
    out = _summ(cr[present], n_slide[present], wc[present], 2.0 * q[fin])
    out["finite"] = bool(fin.all())
    return out


# ================================================================== the Fit
class Fit:
    """One fold and one calibration draw. Attributes (all float64 arrays are copies owned here):
      P_E, Y_E, R_E (n_E, G)  test-donor predictions, labels, signed residuals
      S_C (n_C, G)            |y - yhat| of every calibration spot, R_C the signed residual
      lab_C (n_C,)            calibration donor of each calibration spot; groups = sorted donors
      samp_E (n_E,)           test slide (core) of each test spot
      genes, n_T_donors, n_T_natural, n_T_matched, n_C, n_C_donors, n_E, K (design), pearson_mean
    """

    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.groups = sorted(set(map(str, self.lab_C.tolist())))
        self._sl = None
        self._ctx = None

    @property
    def slides(self):
        if self._sl is None:
            self._sl = _Slides(self.samp_E)
        return self._sl

    def base_row(self):
        return dict(task=self.out_task, label_set=self.label_set, encoder=self.enc,
                    score=SCORE, K=self.K, fold=self.fold, donor_set=self.donor_set,
                    cal_draw=self.cal_draw, n_T_donors=self.n_T_donors,
                    n_T_natural=self.n_T_natural, n_T_matched=self.n_T_matched,
                    n_C=self.n_C, n_C_donors=self.n_C_donors)

    # ---- calibration-donor machinery for the o > 0 methods
    def ctx(self):
        if self._ctx is None:
            self._ctx = _GhcpCtx(self)
        return self._ctx


class _GhcpCtx:
    """Per-donor signed residual arrays in a seeded within-donor order, and the held-out score
    arrays |x_j[m:] - c_j| cached per m (they do not depend on the test donor's draw)."""

    def __init__(self, fit):
        self.fit = fit
        lab = fit.lab_C.astype(str)
        self.X = []
        for g in fit.groups:
            idx = np.flatnonzero(lab == g)
            perm = np.random.default_rng(crc(f"{fit.task_key}|{fit.fold}|donorperm|{g}")
                                         ).permutation(len(idx))
            self.X.append(fit.R_C[idx[perm]])
        self.N = np.array([len(x) for x in self.X])
        self._csum = [np.cumsum(x, axis=0) for x in self.X]
        self._held = {}

    def centre(self, j, m, lam):
        if m == 0:
            return 0.0
        return lam * (self._csum[j][m - 1] / m)

    def held(self, m, lam):
        if m not in self._held:
            self._held[m] = [np.abs(x[m:] - self.centre(j, m, lam)) for j, x in enumerate(self.X)]
        return self._held[m]


# ================================================================== o = 0
def o0_rows(fit, alphas=ALPHAS, methods=O0_METHODS, dwr_reps=DWR_REPS):
    """Full-table rows (dicts) for the o = 0 methods of one Fit, one per (method, alpha)."""
    rows = []
    K = len(fit.groups)
    sl = fit.slides
    N = np.array([int((fit.lab_C.astype(str) == g).sum()) for g in fit.groups])
    base = fit.base_row()
    Y, P = fit.Y_E, fit.P_E
    betas = [1 - a for a in alphas]
    if "pooled" in methods:
        q, fc = split_q_cols(fit.S_C, alphas)
        for i, a in enumerate(alphas):
            m = interval_metrics(Y, P - q[i], P + q[i], sl)
            rows.append(_row(base, "pooled", a, 0, 0, m, fc[i], K_eff=fit.n_C, n_test=fit.n_E))
    if "hcp" in methods:
        lab = fit.lab_C.astype(str)
        sizes = {g: int((lab == g).sum()) for g in fit.groups}
        w = np.array([1.0 / ((K + 1) * sizes[g]) for g in lab])
        q, fc = wq_cols(fit.S_C, w, 1.0 / (K + 1), betas)
        for i, a in enumerate(alphas):
            m = interval_metrics(Y, P - q[i], P + q[i], sl)
            rows.append(_row(base, "hcp", a, 0, 0, m, fc[i], K_eff=K, n_test=fit.n_E))
    if "one_per" in methods:
        A4B = _r3("round3_a4b_hcp")
        acc = {a: [] for a in alphas}
        inf = {a: 0 for a in alphas}
        fcs = {a: True for a in alphas}
        for rep in range(dwr_reps):
            tag = (f"{fit.task}|{fit.donor_set}|K{fit.K}|donor|{fit.fold}|"
                   f"draw{fit.cal_draw}|dwr{rep}")
            rng = np.random.default_rng(crc(tag))
            sel = A4B.dwr_pick(fit.lab_C, rng)
            q, fc = split_q_cols(fit.S_C[sel], alphas)
            for i, a in enumerate(alphas):
                m = interval_metrics(Y, P - q[i], P + q[i], sl)
                acc[a].append(m)
                inf[a] += int(not m["finite"])
                fcs[a] &= bool(fc[i])
        for a in alphas:
            ms = acc[a]
            mm = dict(coverage=float(np.mean([x["coverage"] for x in ms])),
                      width_mean=float(np.mean([x["width_mean"] for x in ms])),
                      width_median=float(np.mean([x["width_median"] for x in ms])),
                      n_cells=ms[0]["n_cells"], n_slides=ms[0]["n_slides"],
                      finite=bool(inf[a] == 0))
            rows.append(_row(base, "one_per", a, 0, 0, mm, fcs[a], K_eff=K, n_test=fit.n_E,
                             n_reps=dwr_reps))
    return rows


def _row(base, method, alpha, o, label_draw, m, finite_code, K_eff, n_test, n_reps=1):
    r = dict(base)
    r.update(method=method, alpha=alpha, o=o, label_draw=label_draw,
             draw=(r["cal_draw"] if o == 0 else r["cal_draw"] * N_LABEL_DRAWS + label_draw),
             coverage=m["coverage"], width_mean=m["width_mean"], width_median=m["width_median"],
             n_test=int(n_test), finite=bool(m["finite"]), finite_code=bool(finite_code),
             K_eff=K_eff, n_cells=m["n_cells"], n_slides=m["n_slides"], n_reps=n_reps)
    return r


# ================================================================== o > 0
def label_stream(fit, ld):
    """The labelled-spot order for label draw ld: a seeded permutation of the test donor's spot
    rows, independent of encoder, K and calibration draw. The method at o uses the first o."""
    return np.random.default_rng(crc(f"{fit.task_key}|{fit.fold}|ld{ld}|stream")
                                 ).permutation(fit.n_E)


def ghcp_cols(ctx, init, o, betas, variant, n_glob, seed_key):
    """Gene-vectorised GHCP threshold and test centre; returns (q (B, G), c (G,), fcode (B,),
    K_eff). init (o, G) is the labelled residual stream in order."""
    v = GHCP_VARIANTS[variant]
    G = init.shape[1]
    N = ctx.N
    m = (o // 2) if v["adapt"] else 0
    lam = m / (n_glob + m) if m > 0 else 0.0
    rng = np.random.default_rng(crc(seed_key + "|" + variant))
    S = SIM.restricted_pool(N, o, v["eta"], rng, v["rule"])
    c_test = lam * init[:m].mean(axis=0) if m > 0 else np.zeros(G)
    if len(S) == 0:
        held = np.abs(init[m:o] - c_test)
        L = o + 1 - m
        q, fc = wq_cols(held, np.full(len(held), 1.0 / L), 1.0 / L, betas)
        return q, c_test, fc, 0
    J0 = int(S[rng.integers(len(S))])
    Scal = [int(j) for j in S if j != J0]
    M = len(Scal) + 1
    H_ = ctx.held(m, lam)
    sc = [H_[j] for j in Scal]
    wt = [np.full(len(H_[j]), 1.0 / (M * len(H_[j]))) for j in Scal]
    Lt = N[J0] - m
    sc.append(np.abs(init[m:o] - c_test))
    wt.append(np.full(o - m, 1.0 / (M * Lt)))
    q, fc = wq_cols(np.concatenate(sc, axis=0), np.concatenate(wt), (N[J0] - o) / (M * Lt), betas)
    return q, c_test, fc, len(Scal)


def o_rows(fit, o_grid=O_GRID, label_draws=range(N_LABEL_DRAWS), alphas=ALPHAS,
           methods=O_METHODS, min_eval=10, log=None):
    """Full-table rows for the o > 0 methods of one Fit. o values leaving fewer than `min_eval`
    evaluation spots are skipped and listed in fit.skipped_o."""
    rows = []
    base = fit.base_row()
    sl = fit.slides
    R = fit.R_E
    G = R.shape[1]
    betas = [1 - a for a in alphas]
    ctx = fit.ctx() if any(m.startswith("ghcp") for m in methods) else None
    S_abs_C = fit.S_C
    q_rec, fc_rec = split_q_cols(S_abs_C, alphas)
    fit.skipped_o = [o for o in o_grid if fit.n_E - o < min_eval]
    for ld in label_draws:
        perm = label_stream(fit, ld)
        for o in o_grid:
            if o in fit.skipped_o:
                continue
            lab_idx = perm[:o]
            keep = np.ones(fit.n_E, bool)
            keep[lab_idx] = False
            init = R[lab_idx]
            n_test = int(keep.sum())
            m0 = o // 2
            seed = f"{fit.task_key}|{fit.fold}|K{fit.K}|cal{fit.cal_draw}|o{o}|ld{ld}"

            def emit(method, alpha, q, c, fc, K_eff):
                m = centred_metrics(R, keep, c, q, sl)
                rows.append(_row(base, method, alpha, o, ld, m, fc, K_eff, n_test))

            for variant in [x for x in methods if x.startswith("ghcp")]:
                q, c, fc, Kn = ghcp_cols(ctx, init, o, betas, variant, fit.n_T_donors, seed)
                for i, a in enumerate(alphas):
                    if variant == "ghcp_r05code" and abs(a - 0.1) > 1e-12:
                        continue
                    emit(variant, a, q[i], c, fc[i], Kn)
            if "within" in methods:
                c = init[:m0].mean(axis=0) if m0 > 0 else np.zeros(G)
                q, fc = split_q_cols(np.abs(init[m0:] - c), alphas)
                for i, a in enumerate(alphas):
                    emit("within", a, q[i], c, fc[i], o - m0)
            if "within_plain" in methods:
                q, fc = split_q_cols(np.abs(init), alphas)
                for i, a in enumerate(alphas):
                    emit("within_plain", a, q[i], np.zeros(G), fc[i], o)
            if "recentred" in methods:
                c = init.mean(axis=0)
                for i, a in enumerate(alphas):
                    emit("recentred", a, q_rec[i], c, fc_rec[i], fit.n_C)
    return rows


# ================================================================== data and folds
class TaskData:
    """A loaded task for one encoder. Use `specs(K, ...)` for the folds and draws and `fit(spec)`
    to fit one. Attributes: key, enc, td, task, label_set, X, samp, xy, meta, folds, n_match,
    genes (CCRCC and lung) or per-fold gene lists (Indiana)."""

    def fit(self, spec):
        H = self.H
        Tm = H.apply_size_match(spec, self.task)
        Cm, Em = spec["C"], spec["E"]
        if int(Tm.sum()) < H.MIN_T_SPOTS or int(Cm.sum()) < H.MIN_C_SPOTS:
            raise ValueError(f"{self.key} {spec['fold']} draw{spec['cal_draw']}: |T|="
                             f"{int(Tm.sum())} |C|={int(Cm.sum())}")
        genes, Y = self._labels(spec)
        pipe, A, reg, ridge_alpha = H.fit_base(self.X[Tm], Y[Tm])
        P_C = reg.predict(pipe.transform(self.X[Cm].astype(np.float64, copy=False)))
        P_E = reg.predict(pipe.transform(self.X[Em].astype(np.float64, copy=False)))
        Y_C, Y_E = Y[Cm].astype(np.float64, copy=False), Y[Em].astype(np.float64, copy=False)
        donor_of = self.meta["donor_of"]
        don_T = {donor_of[s] for s in np.unique(self.samp[Tm])}
        lab_C = np.array([donor_of[s] for s in self.samp[Cm]], dtype=object)
        rs = [np.corrcoef(P_E[:, j], Y_E[:, j])[0, 1] if Y_E[:, j].std() > 0 and
              P_E[:, j].std() > 0 else np.nan for j in range(len(genes))]
        return Fit(task_key=self.key, task=self.task, out_task=self.out_task,
                   label_set=self.label_set, enc=self.enc, donor_set=self.donor_set,
                   fold=str(spec["fold"]), cal_draw=int(spec["cal_draw"]),
                   K=int(spec["info"]["n_cal_units"]), genes=list(genes), P_E=P_E, Y_E=Y_E,
                   R_E=Y_E - P_E, S_C=np.abs(Y_C - P_C), R_C=Y_C - P_C, lab_C=lab_C,
                   samp_E=self.samp[Em], n_T_donors=len(don_T),
                   n_T_natural=int(spec["n_train_natural"]),
                   n_T_matched=int(spec["n_train_matched"]), n_C=int(Cm.sum()),
                   n_C_donors=len(set(lab_C.tolist())), n_E=int(Em.sum()),
                   pearson_mean=float(np.nanmean(rs)), cal_donors=sorted(set(lab_C.tolist())))

    def _labels(self, spec):
        return self.genes, self.Y

    def fold_names(self):
        return [str(f["fold"]) for f in self.folds]


def _ns(**kw):
    return types.SimpleNamespace(**kw)


def load_task(task_key, enc, size_match="task", log=print):
    """Load one task for one encoder. task_key in TASKS."""
    spec = TASKS[task_key]
    IO.check_harness()
    t0 = time.time()
    td = json.load(open(spec["td"]))
    kind = spec["kind"]
    if kind == "ccrcc":
        T = _load_ccrcc(task_key, spec, td, enc, size_match)
    elif kind == "d4":
        T = _load_d4(task_key, spec, td, enc, size_match)
    else:
        T = _load_lung(task_key, spec, td, enc, size_match)
    T.key, T.enc, T.td = task_key, enc, td
    T.task, T.out_task, T.donor_set = spec["task"], spec["out_task"], spec["donor_set"]
    T.label_set = td["label_set"]
    log(f"[load] {task_key} {enc}: {T.X.shape[0]:,} spots x {T.X.shape[1]} dims, "
        f"{len(np.unique(T.samp))} slides, {len({T.meta['donor_of'][s] for s in np.unique(T.samp)})}"
        f" donors, n_match={T.n_match}, {time.time()-t0:.0f}s")
    return T


def _load_ccrcc(task_key, spec, td, enc, size_match):
    H, A4B = _r3("round3_a0_harness"), _r3("round3_a4b_hcp")
    T = TaskData()
    T.H = H
    X, Y, samp, bc, xy, genes = H.load_task(td, enc)
    ids = sorted(s["sample_id"] for s in td["samples"])
    audit, rec = A4B.audit_donor_map(f"{ROOT}/{A4B.AUDIT}", "CCRCC", td)
    rebuilt = A4B.donor_folds(audit, ids)
    shipped = [dict(fold=str(f["fold"]), test=sorted(f["test"]), train=sorted(f["train"]))
               for f in td["folds"]["donor"]]
    assert rebuilt == shipped, "rebuilt 24-donor folds differ from the shipped donor folds"
    if spec["donor_set"] == "24":
        donor_of = dict(audit)
    else:
        donor_of = {s: (A4B.MERGED_ID if audit[s] in A4B.MERGE_PAIR else audit[s]) for s in ids}
    meta = dict(donor_of=donor_of,
                patient_of={s["sample_id"]: s["hest_patient"] for s in td["samples"]},
                resgroup_of={s["sample_id"]: s["resolution_group"] for s in td["samples"]},
                session_of={s["sample_id"]: s.get("session") for s in td["samples"]})
    folds = A4B.donor_folds(donor_of, ids)
    tdv = dict(td)
    tdv["folds"] = dict(td["folds"])
    tdv["folds"]["donor"] = folds
    designs = ["random", "patient", "donor"]
    args = _ns(encoder=enc, task_def=[spec["td"]], alpha=0.10, alpha_store=0.20,
               n_cal_draws=3, spot_cal_draws=1, size_match=size_match, n_repeats=None,
               max_folds=None)
    a1specs, n_match = A4B.a1_enumeration(tdv, samp, xy, meta, args, designs)
    del a1specs
    T.X, T.Y, T.samp, T.xy, T.genes = X, Y, samp, xy, genes
    T.meta, T.folds, T.tdv, T.n_match, T.A4B = meta, folds, tdv, n_match, A4B
    T.specs = lambda K, n_cal_draws=N_CAL_DRAWS, folds=None: _ccrcc_specs(T, K, n_cal_draws, folds)
    return T


def _ccrcc_specs(T, K, n_cal_draws, fold_names):
    fl = [f for f in T.folds if fold_names is None or str(f["fold"]) in set(map(str, fold_names))]
    args = _ns(max_folds=None, n_cal_draws=n_cal_draws)
    return T.A4B.k_specs(T.tdv, T.samp, T.xy, T.meta, fl, K, T.n_match, args)


def _a4b_like_specs(T, K, n_cal_draws, fold_names):
    """round3_d4_sets.a4b_specs with K a parameter: one held-out donor unit per fold; K donor
    units of the remaining pool calibrate (the first K of the crc32 permutation of the sorted
    eligible units, seed f'{task}|a4b_k10|{fold}|cal{draw}', so K = 10 is a4b_specs itself and
    smaller K is a prefix of it), the other eligible pool donors train; samples flagged
    excluded_from_donor_units never calibrate."""
    td, samp, meta, H = T.td, T.samp, T.meta, T.H
    task = td["task"]
    donor_of = meta["donor_of"]
    barred = {s["sample_id"] for s in td["samples"] if s.get("excluded_from_donor_units")}
    out = []
    for fd in td["folds"]["donor"]:
        if fold_names is not None and str(fd["fold"]) not in set(map(str, fold_names)):
            continue
        E = np.isin(samp, fd["test"])
        pool = np.isin(samp, fd["train"])
        if not E.any() or not pool.any():
            continue
        units = sorted({donor_of[s] for s in fd["train"] if s not in barred})
        if len(units) <= K:
            continue
        for draw in range(n_cal_draws):
            rng = np.random.default_rng(zlib.crc32(f"{task}|a4b_k10|{fd['fold']}|cal{draw}".encode()))
            pick = set(rng.permutation(np.array(units, dtype=object))[:K].tolist())
            cal_samples = [s for s in fd["train"] if s not in barred and donor_of[s] in pick]
            C = np.isin(samp, cal_samples)
            Tm = pool & ~C
            info = dict(calibration_unit="donor", n_cal_units=len(pick), n_units_in_pool=len(units),
                        n_cal_spots=int(C.sum()), n_pool_spots=int(pool.sum()), cal_status="ok")
            out.append(dict(task=task, design="a4b_k10", fold=str(fd["fold"]), repeat=-1,
                            cal_draw=draw, T=Tm, C=C, E=E, pool=pool, info=info,
                            n_match=T.n_match))
    return out


def _nmatch_d4(T, td, samp, xy, meta, size_match):
    D4 = _r3("round3_d4_sets")
    specs = D4.H.build_fold_specs(td, samp, xy, ["random", "donor"], meta, D4.HArgs())
    D4.H.size_match_groups(specs, size_match)
    return (specs[0]["n_match"] if specs else None), D4


def _load_d4(task_key, spec, td, enc, size_match):
    T = TaskData()
    D4 = _r3("round3_d4_sets")
    T.H = D4.H
    sel, meta_files = D4.read_genes(td["task"], f"{ROOT}/results/round3/D4_expansion")
    union = sorted({g for v in sel.values() for g in v["genes"]})
    T.col_of = {g: i for i, g in enumerate(union)}
    T.sel = sel
    X, Yraw, samp, bc, xy = D4.load_set(td, enc, union)
    T.X, T.Yraw, T.samp, T.xy = X, Yraw, samp, xy
    T.meta = D4.meta_of(td)
    T.folds = td["folds"]["donor"]
    T.n_match, _ = _nmatch_d4(T, td, samp, xy, T.meta, size_match)
    T.D4 = D4
    T.specs = lambda K, n_cal_draws=N_CAL_DRAWS, folds=None: _a4b_like_specs(T, K, n_cal_draws, folds)

    def _labels(spec):
        gsel = D4.genes_for(sel, "a4b_k10", spec["fold"], -1)
        genes = gsel["genes"]
        return genes, D4.log1p_cols(Yraw, [T.col_of[g] for g in genes])
    T._labels = _labels
    return T


def _load_lung(task_key, spec, td, enc, size_match):
    T = TaskData()
    D4 = _r3("round3_d4_sets")
    T.H = D4.H
    genes, n_ctrl_list = IO.drop_control_features(list(td["target_genes"]["list"]))
    X, Yraw, samp, bc, xy, rec, n_ctrl = IO.load_set_dropped(td, enc, genes, None, D4=D4)
    T.X, T.samp, T.xy = X, samp, xy
    T.Y = np.log1p(Yraw.astype(np.float64))
    T.genes = list(genes)
    T.meta = D4.meta_of(td)
    T.folds = td["folds"]["donor"]
    T.n_match, _ = _nmatch_d4(T, td, samp, xy, T.meta, size_match)
    T.D4, T.drop_rec, T.n_ctrl = D4, rec, n_ctrl + n_ctrl_list
    T.specs = lambda K, n_cal_draws=N_CAL_DRAWS, folds=None: _a4b_like_specs(T, K, n_cal_draws, folds)
    return T


# ================================================================== tables and writer
def to_c3(rows):
    """The fixed c3_o_sweep column set, exactly."""
    d = pd.DataFrame(rows)
    return d[FIXED_COLS].copy()


def full_table(rows):
    d = pd.DataFrame(rows)
    return d[FIXED_COLS + EXTRA_COLS].copy()


def by_fold_table(rows):
    """Mean over calibration and label draws within (task, encoder, method, alpha, o, K, fold)."""
    d = pd.DataFrame(rows)
    keys = ["task", "label_set", "encoder", "method", "score", "alpha", "o", "K", "fold",
            "n_T_donors"]
    g = d.groupby(keys, dropna=False)
    out = g.agg(coverage=("coverage", "mean"), width_mean=("width_mean", "mean"),
                width_median=("width_median", "mean"), n_test=("n_test", "mean"),
                finite_frac=("finite", "mean"), finite_code_frac=("finite_code", "mean"),
                n_draws=("draw", "nunique")).reset_index()
    return out


def k_table(rows):
    """The K-sweep table: o = 0 rows with the training-donor count, per (K, fold, calibration
    draw)."""
    d = pd.DataFrame(rows)
    d = d[d["o"] == 0]
    return d[FIXED_COLS + EXTRA_COLS].copy()


def _read_head(clone=None):
    clone = clone or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    clone = os.environ.get("R4C3_CODE_CLONE", clone)
    try:
        h = open(os.path.join(clone, ".git", "HEAD")).read().strip()
        if h.startswith("ref:"):
            ref = h.split(None, 1)[1]
            p = os.path.join(clone, ".git", ref)
            if os.path.exists(p):
                return open(p).read().strip()
            for line in open(os.path.join(clone, ".git", "packed-refs")):
                if line.strip().endswith(ref):
                    return line.split()[0]
        return h
    except Exception as e:
        return f"unreadable ({e.__class__.__name__})"


def write_frag(rows, outdir, tag, stage="C3_core", script=None, cfg=None, note=""):
    """Write the three tables for a fragment with provenance. Tables: c3_o_sweep__<tag>.csv (fixed
    columns), c3_full__<tag>.csv (fixed + extra), c3_by_fold__<tag>.csv, c3_K_sweep__<tag>.csv."""
    os.makedirs(outdir, exist_ok=True)
    IO.code_head = _read_head      # no git command is run; HEAD is read from the clone's files
    IO.stamp(outdir, track="conformal-C3", note=note or f"C3 fragment {tag}")
    d = pd.DataFrame(rows)
    to_c3(rows).to_csv(f"{outdir}/c3_o_sweep__{tag}.csv", index=False)
    full_table(rows).to_csv(f"{outdir}/c3_full__{tag}.csv", index=False)
    by_fold_table(rows).to_csv(f"{outdir}/c3_by_fold__{tag}.csv", index=False)
    k_table(rows).to_csv(f"{outdir}/c3_K_sweep__{tag}.csv", index=False)
    IO.write_provenance(outdir, stage, script or __file__, cfg or {}, extra={"tag": tag,
                        "rows": len(d)})
    return outdir


# ================================================================== self tests
def selftest(fit, n_rep=3, seed="selftest"):
    """Checks the vectorised kernels against round4_conf_sim's reference implementations on a
    Fit: split_q, wquantile/hcp_q, ghcp_q (every variant, several o), and the metric chain
    against A3.cell_metrics + fold_summary. Returns a list of dicts (check, max_abs_diff)."""
    out = []
    G = fit.S_C.shape[1]
    gi = list(range(0, G, max(1, G // 5)))[:5]
    # split_q
    q, _ = split_q_cols(fit.S_C, [0.1, 0.2])
    d = max(abs(q[i, g] - SIM.split_q(fit.S_C[:, g], a)) for i, a in enumerate([0.1, 0.2])
            for g in gi if np.isfinite(q[i, g]))
    out.append(dict(check="split_q_cols_vs_SIM.split_q", max_abs_diff=float(d)))
    # hcp_q
    lab = fit.lab_C.astype(str)
    K = len(fit.groups)
    w = np.array([1.0 / ((K + 1) * (lab == g).sum()) for g in lab])
    q, _ = wq_cols(fit.S_C, w, 1.0 / (K + 1), [0.9, 0.8])
    d = 0.0
    for g in gi:
        cal = [fit.S_C[lab == gg, g] for gg in fit.groups]
        for i, a in enumerate([0.1, 0.2]):
            ref = SIM.hcp_q(cal, a)
            d = max(d, 0.0 if (np.isinf(ref) and np.isinf(q[i, g])) else abs(ref - q[i, g]))
    out.append(dict(check="wq_cols_vs_SIM.hcp_q", max_abs_diff=float(d)))
    # ghcp
    ctx = fit.ctx()
    cal_signed = ctx.X
    R = fit.R_E
    perm = label_stream(fit, 0)
    dmax = {}
    for o in (5, 25, 100):
        if fit.n_E - o < 10:
            continue
        init = R[perm[:o]]
        for variant, v in GHCP_VARIANTS.items():
            seed_key = f"{seed}|o{o}"
            q, c, fc, Kn = ghcp_cols(ctx, init, o, [0.9], variant, fit.n_T_donors, seed_key)
            for g in gi[:3]:
                rng = np.random.default_rng(crc(seed_key + "|" + variant))
                rq, rc = SIM.ghcp_q([x[:, g] for x in cal_signed], init[:, g], o, 0.1, rng,
                                    adapt=v["adapt"], eta=v["eta"], n_glob=fit.n_T_donors,
                                    pool_rule=v["rule"])
                dq = 0.0 if (np.isinf(rq) and np.isinf(q[0, g])) else abs(rq - q[0, g])
                dmax[variant] = max(dmax.get(variant, 0.0), dq, abs(rc - c[g]))
    for k, v in dmax.items():
        out.append(dict(check=f"ghcp_cols_vs_SIM.ghcp_q[{k}]", max_abs_diff=float(v)))
    # metric chain vs A3
    out.append(dict(check="metrics_vs_A3_cell_metrics", max_abs_diff=metrics_vs_a3(fit)))
    return out


def metrics_vs_a3(fit):
    """Max |difference| between interval_metrics / centred_metrics and round 3's A3.cell_metrics +
    fold_summary on a pooled-quantile interval (and a shifted one for centred_metrics)."""
    A3 = _r3("round3_a3_weighted")
    H = _r3("round3_a0_harness")
    q, _ = split_q_cols(fit.S_C, [0.1])
    P, Y = fit.P_E, fit.Y_E
    lo, hi = P - q[0], P + q[0]
    cells, wm, wmd, ninf, ntot = A3.cell_metrics(Y, lo, hi, 0.1, fit.samp_E, fit.genes,
                                                 H.MIN_SLIDE_SPOTS)
    fs = A3.fold_summary(cells)
    m = interval_metrics(Y, lo, hi, fit.slides)
    d = max(abs(m["coverage"] - fs["coverage"]), abs(m["width_mean"] - fs["width_mean"]),
            abs(m["width_median"] - wmd))
    keep = np.ones(fit.n_E, bool)
    c = np.zeros(len(fit.genes))
    m2 = centred_metrics(fit.R_E, keep, c, q[0], fit.slides)
    d = max(d, abs(m2["coverage"] - fs["coverage"]), abs(m2["width_mean"] - fs["width_mean"]),
            abs(m2["width_median"] - wmd))
    return float(d)
