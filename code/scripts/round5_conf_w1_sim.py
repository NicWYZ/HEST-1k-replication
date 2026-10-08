#!/usr/bin/env python
"""Round 5, prediction-set track, stage W1: the simulation map, completed.

docs/round5_conf_plan.md section 2, W1. Imports round4_conf_sim.py unmodified (md5 checked),
registers two methods through its register_fast, builds its own cells in round 4's cell format,
and calls run_cell with round 4's seed tag "C1". A replicate's draw depends only on (cell_id,
replicate), the labelled stream is the first o of a stream of o_max = 100, and each method's
randomness is keyed by (cell_id, replicate, method, o). So every round-4 row is reproduced, and
every replicate is paired across methods and across o.

----------------------------------------------------------------------------------------------
THE GRID. K is set per job. o in {0, 3, 5, 9, 10, 12, 15, 17, 20, 25, 35, 50, 100}. N in {21, 100,
500, unequal}. Share in {0.1, 0.3, 0.5, 0.9} at tau 0 and 0.3, plus share 0 at tau 0. Normal and
t3 tails. The two semi-real cells (N = data and N = 500) use the round-4 moments file, md5
27352567fdbeab21d830e57a3b28fbec. alpha in {0.1, 0.2}, 5,000 replicates. sigma_a for share 0.9 is
found by round 4's own bisection, solve_sigma_a, and the realised share is recorded per cell.

THE METHODS, with what each assumes and the guarantee it carries, written before any run.
Round 4's methods are unchanged and documented in round4_conf_sim.py. They are pooled (no
guarantee), hcp (valid for any K, infinite iff 1/(K+1) > alpha), one_per (valid), ghcp, ghcp_noad
and ghcp_r05 (valid under GHCP's A1 to A3, which hold by construction here), ghcp_r05code (the
released code's pool, secondary), and within (Std-CP form: centre on floor(o/2), calibrate on the
rest; valid, expected coverage ceil((n+1)(1-alpha))/(n+1) with n = o - floor(o/2), infinite when
n < (1-alpha)/alpha). Note: with fixed N_k = N and o >= N, GHCP's pool {k : N_k > o} is empty and
the module's GHCP is the within-group split with N_{K+1} = o + 1 (paper Remark 2.2). Such rows
carry ghcp_pool_empty = True and are not counted as GHCP cells in the narrowest-valid table.

  within_plain  split conformal inside the test cluster on the o absolute residuals |r_i|,
                uncentred (c = 0, the known global predictor). Assumes the o labelled units and
                the test unit are exchangeable within the test cluster, true by construction.
                Guarantee: coverage at least 1 - alpha, and with distinct scores exactly
                ceil((o+1)(1-alpha))/(o+1). Finite iff o >= (1-alpha)/alpha, that is o >= 9 at
                alpha 0.1 and o >= 4 at alpha 0.2.
  within_full   full conformal inside the test cluster with the mean as the fitted model. For a
                candidate residual r of the test unit let c(r) = (S + r)/(o + 1), S the sum of the
                o labelled residuals, s_i(r) = |r_i - c(r)|, s(r) = |r - c(r)|, and keep r iff
                1 + #{i : s_i(r) >= s(r)} > alpha (o + 1). Same assumption as within_plain.
                Guarantee: coverage at least 1 - alpha. With distinct scores it is exactly
                (o + 1 - floor(alpha(o+1)))/(o + 1) = ceil((o+1)(1-alpha))/(o+1), the same as
                within_plain's.
                Derivation (checked in docs/round5_conf_plan.md section 4 item 5): (r_i - c)^2 -
                (r - c)^2 = (r_i - r)(r_i + r - 2c(r)), a quadratic in r with leading coefficient
                -(o - 1)/(o + 1). So {r : s_i(r) >= s(r)} is the closed interval I_i with end points
                r_i and (2S - (o + 1) r_i)/(o - 1), for o >= 2. The kept set is
                {r : #{i : r in I_i} >= m} with m = floor(alpha (o + 1)), evaluated with a 1e-9
                guard on the floor. When m = 0, which is alpha (o + 1) < 1, the set is the whole
                line and the method returns +inf. So it is finite from o = 9 at alpha 0.1 and from
                o = 4 at alpha 0.2.
                CHOICES THE DEFINITION LEAVES OPEN, recorded here before the run (instruction
                section 9). (1) The returned (q, c) is the convex hull of the kept set,
                c = midpoint and q = half its length, so run_cell's coverage and price for
                within_full are those of the hull. The instruction asks for the hull's length.
                (2) Beside it, the exact set's coverage of the 500 evaluation units and whether the
                set is one interval are recorded for every replicate, summarised per (cell, alpha,
                o) in w1_within_full_shape__<tag>.csv. (3) Ties in s are kept (>=), as in the
                definition. (4) selftest_within_full() checks the interval end points and the
                kept set against brute force on a grid of candidate r before any cell runs. The
                job stops if the check fails.

THE NARROWEST VALID METHOD per (cell, alpha, o) is the method with the smallest mean half-width
among hcp (available at every o, since it ignores labelled units), ghcp, ghcp_noad, within,
within_plain and within_full that are finite in every replicate. GHCP rows with an empty pool are
excluded. Ties of mean half-width within 1e-12 relative are listed. The margin is the runner-up's
mean half-width minus the narrowest's, with a paired Monte Carlo standard error, the sd over
replicates of the per-replicate difference divided by sqrt(n_reps). margin_gt_2se says whether
the margin exceeds two of them.
"""
import argparse
import hashlib
import math
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_sim as SIM  # noqa: E402
import round5_conf_io as IO5  # noqa: E402

SIM_MD5 = "76fda34ee622e299bbaa806e5c8da98a"
MOMENTS_MD5 = "27352567fdbeab21d830e57a3b28fbec"
O_GRID = (0, 3, 5, 9, 10, 12, 15, 17, 20, 25, 35, 50, 100)
N_GRID = ("21", "100", "500", "unequal")
SHARE_GRID = (0.1, 0.3, 0.5, 0.9)
TAU_GRID = (0.0, 0.3)
ALPHAS = (0.1, 0.2)
METHODS = ("pooled", "hcp", "one_per", "ghcp", "within", "within_plain", "within_full")
VALID = ("hcp", "ghcp", "ghcp_noad", "within", "within_plain", "within_full")
MGUARD = 1e-9
_WF_LOG = []   # per call: (o, alpha, exact_coverage, is_interval); reset per cell


# ============================================================ within_plain
def f_within_plain(prep, rep, cell, o, rng, alphas):
    if o == 0:
        return {"within_plain": [None for _ in alphas]}
    return {"within_plain": [(q, 0.0) for q in SIM.split_qs(np.abs(rep["init"][:o]), alphas)]}


# ============================================================ within_full
def wf_intervals(r):
    """End points (lo, hi) of I_i = {x : |r_i - c(x)| >= |x - c(x)|}, c(x) = (S + x)/(o + 1)."""
    o = len(r)
    S = float(np.sum(r))
    other = (2.0 * S - (o + 1) * r) / (o - 1)
    return np.minimum(r, other), np.maximum(r, other)


def wf_m(o, alpha):
    return int(math.floor(alpha * (o + 1) + MGUARD))


def wf_set(lo, hi, m):
    """The kept set {x : #{i : lo_i <= x <= hi_i} >= m} as a list of closed intervals."""
    ev = np.concatenate([np.stack([lo, np.ones_like(lo)], 1), np.stack([hi, -np.ones_like(hi)], 1)])
    ev = ev[np.lexsort((-ev[:, 1], ev[:, 0]))]      # at equal x, openings before closings
    out, k, start = [], 0, None
    for x, d in ev:
        k += int(d)
        if d > 0 and k == m:
            start = x
        if d < 0 and k == m - 1:
            if out and out[-1][1] == start:
                out[-1] = (out[-1][0], x)
            else:
                out.append((start, x))
    return out


def wf_count(lo, hi, t):
    los, his = np.sort(lo), np.sort(hi)
    return np.searchsorted(los, t, side="right") - np.searchsorted(his, t, side="left")


def f_within_full(prep, rep, cell, o, rng, alphas):
    res = []
    for a in alphas:
        m = wf_m(o, a) if o > 0 else 0
        if o < 2 or m == 0:
            res.append(None if o == 0 else (math.inf, 0.0))
            if o > 0:
                _WF_LOG.append((o, a, 1.0, True))
            continue
        r = rep["init"][:o]
        lo, hi = wf_intervals(r)
        comps = wf_set(lo, hi, m)
        L, H = comps[0][0], comps[-1][1]
        exact = float(np.mean(wf_count(lo, hi, rep["test"]) >= m))
        _WF_LOG.append((o, a, exact, len(comps) == 1))
        res.append(((H - L) / 2.0, (H + L) / 2.0))
    return {"within_full": res}


def selftest_within_full(n=400, seed="W1wfselftest"):
    """Max discrepancy between the interval construction and brute force, over random draws."""
    worst_end, n_mismatch, n_pts = 0.0, 0, 0
    for t in range(n):
        rng = np.random.default_rng(SIM.crc(f"{seed}|{t}"))
        o = int(rng.choice([4, 5, 9, 10, 12, 17, 25, 50]))
        r = rng.standard_t(3, o) * float(rng.choice([0.5, 1, 3])) + float(rng.normal(0, 2))
        lo, hi = wf_intervals(r)
        S = r.sum()
        for i in range(o):   # each I_i end point solves s_i = s
            for x in (lo[i], hi[i]):
                c = (S + x) / (o + 1)
                worst_end = max(worst_end, abs(abs(r[i] - c) - abs(x - c)))
        span = np.ptp(np.concatenate([lo, hi]))
        grid = np.linspace(lo.min() - 0.5 * span - 1, hi.max() + 0.5 * span + 1, 4001)
        c = (S + grid) / (o + 1)
        cnt_brute = (np.abs(r[None, :] - c[:, None]) >= np.abs(grid - c)[:, None]).sum(1)
        cnt_int = wf_count(lo, hi, grid)
        # exclude grid points within 1e-9 of an end point, where floating rounding may flip >=
        near = np.min(np.abs(grid[:, None] - np.concatenate([lo, hi])[None, :]), 1) < 1e-9
        n_mismatch += int(((cnt_brute != cnt_int) & ~near).sum())
        n_pts += int((~near).sum())
        for a in ALPHAS:
            m = wf_m(o, a)
            if m == 0:
                continue
            comps = wf_set(lo, hi, m)
            keep = cnt_int >= m
            inside = np.zeros_like(keep)
            for (u, v) in comps:
                inside |= (grid >= u) & (grid <= v)
            n_mismatch += int(((keep != inside) & ~near).sum())
    return dict(n_draws=n, max_endpoint_residual=worst_end, n_grid_points=n_pts,
                n_mismatch=n_mismatch)


SIM.register_fast("within_plain", f_within_plain, True)
SIM.register_fast("within_full", f_within_full, True)


# ============================================================ cells
def build_cells(K, semireal=True):
    cells = []
    for gen in ("normal", "t3"):
        sig = {s: SIM.solve_sigma_a(s, gen) for s in SHARE_GRID}
        for N in N_GRID:
            for s in SHARE_GRID:
                for tau in TAU_GRID:
                    cells.append(dict(gen=gen, K=K, N=N, share=s, tau=tau, sigma_a=sig[s]))
            cells.append(dict(gen=gen, K=K, N=N, share=0.0, tau=0.0, sigma_a=0.0))
    if semireal:
        for N in ("data", "500"):
            cells.append(dict(gen="semireal", K=K, N=N, share=float("nan"), tau=float("nan"),
                              sigma_a=float("nan")))
    for c in cells:
        c["n_test"] = SIM.N_TEST
        c["n_glob"] = SIM.N_GLOB
        c["cell_id"] = f"{c['gen']}|K{K}|N{c['N']}|share{c['share']}|tau{c['tau']}"
    return cells


# ============================================================ one cell
def narrowest(rr, cell):
    """One row per (alpha, o): the narrowest valid method, the runner-up and the paired margin."""
    out = []
    fixedN = cell["N"] not in ("unequal", "data")
    for a in ALPHAS:
        ra = rr[rr.alpha == a]
        hcp = ra[ra.method == "hcp"].set_index("rep").q
        for o in O_GRID:
            cand = {}
            if len(hcp):
                cand["hcp"] = hcp
            for m in VALID[1:]:
                d = ra[(ra.method == m) & (ra.o == o)]
                if not len(d):
                    continue
                if m.startswith("ghcp") and fixedN and o >= int(cell["N"]):
                    continue
                cand[m] = d.set_index("rep").q
            fin = {m: q for m, q in cand.items() if np.isfinite(q.values).all()}
            row = dict(cell_id=cell["cell_id"], gen=cell["gen"], K=cell["K"], N=cell["N"],
                       share=cell["share"], tau=cell["tau"], alpha=a, o=o,
                       n_valid_finite=len(fin), valid_finite=";".join(sorted(fin)))
            if not fin:
                out.append(dict(row, narrowest=None))
                continue
            means = sorted((float(q.mean()), m) for m, q in fin.items())
            best_w, best = means[0]
            ties = [m for w, m in means if abs(w - best_w) <= 1e-12 * max(abs(best_w), 1)]
            row.update(narrowest=best, ties=";".join(ties), narrowest_halfwidth=best_w)
            qs = ra.groupby("rep").q_star.first()
            row["narrowest_price"] = float((fin[best] / qs.loc[fin[best].index]).mean())
            if len(means) > 1:
                w2, m2 = means[1]
                diff = (fin[m2] - fin[best]).values
                se = float(diff.std(ddof=1) / math.sqrt(len(diff)))
                row.update(runner_up=m2, runner_up_halfwidth=w2, margin=w2 - best_w,
                           margin_rel=(w2 - best_w) / best_w, margin_se=se,
                           margin_gt_2se=bool(w2 - best_w > 2 * se))
            out.append(row)
    return out


def run_one(args):
    cell, reps, moments = args
    _WF_LOG.clear()
    semi = SIM.SemiReal(moments) if cell["gen"] == "semireal" else None
    t0 = time.time()
    rr = SIM.run_cell(cell, list(ALPHAS), reps, O_GRID, semi, methods=list(METHODS), seed_tag="C1")
    summ = SIM.summarise(rr, cell)
    rs = SIM.realised_share(cell)
    fixedN = cell["N"] not in ("unequal", "data")
    for r in summ:
        r["realised_share"] = rs
        r["ghcp_pool_empty"] = bool(r["method"].startswith("ghcp") and fixedN and r["o"] >= int(cell["N"]))
    wf = pd.DataFrame(_WF_LOG, columns=["o", "alpha", "exact_coverage", "is_interval"])
    wfs = (wf.groupby(["alpha", "o"]).agg(n=("is_interval", "size"),
                                          frac_not_interval=("is_interval", lambda x: float(1 - x.mean())),
                                          exact_coverage=("exact_coverage", "mean"),
                                          exact_coverage_sd=("exact_coverage", "std")).reset_index())
    wfs.insert(0, "cell_id", cell["cell_id"])
    nv = narrowest(rr, cell)
    return cell["cell_id"], summ, wfs, nv, time.time() - t0


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--K", type=int, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--reps", type=int, default=5000)
    p.add_argument("--cells-regex", default="")
    p.add_argument("--moments", default=f"{IO5.DATA_ROOT}/results/round3/A2_conditional/"
                   "a2_score_moments__resnet50.parquet")
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--tag", default="")
    p.add_argument("--selftest-only", action="store_true")
    a = p.parse_args(argv)
    t0 = time.time()
    os.makedirs(a.out, exist_ok=True)
    IO5.stamp(a.out, track="conformal-W1", note=f"W1 simulation K={a.K} {a.cells_regex} {a.tag}")
    got = IO5.md5(SIM.__file__)
    assert got == SIM_MD5, f"round4_conf_sim.py md5 {got}"
    st = selftest_within_full()
    pd.DataFrame([st]).to_csv(os.path.join(a.out, f"w1_within_full_selftest__K{a.K:02d}{a.tag}.csv"), index=False)
    print("[selftest]", st, flush=True)
    assert st["n_mismatch"] == 0 and st["max_endpoint_residual"] < 1e-9, st
    cells = [c for c in build_cells(a.K) if re.search(a.cells_regex, c["cell_id"])]
    if any(c["gen"] == "semireal" for c in cells):
        mm = IO5.md5(a.moments)
        assert mm == MOMENTS_MD5, f"moments md5 {mm}"
    cfg = dict(stage="W1", K=a.K, reps=a.reps, alphas=list(ALPHAS), o_grid=list(O_GRID),
               N=list(N_GRID), shares=list(SHARE_GRID), taus=list(TAU_GRID), methods=list(METHODS),
               cells_regex=a.cells_regex, moments=a.moments, moments_md5=MOMENTS_MD5,
               seed="zlib.crc32 keys C1|cell|rep (round 4's)", n_cells=len(cells))
    if a.selftest_only:
        IO5.write_provenance(a.out, "W1_selftest", __file__, cfg, extra=dict(selftest=st))
        return 0
    suf = f"__K{a.K:02d}{a.tag}"
    S, WF, NV, T = [], [], [], []
    jobs = [(c, a.reps, a.moments) for c in cells]
    ex = ProcessPoolExecutor(a.workers) if a.workers > 1 else None
    it = ex.map(run_one, jobs) if ex else map(run_one, jobs)
    for i, (cid, summ, wfs, nv, sec) in enumerate(it):
        S += summ
        WF.append(wfs)
        NV += nv
        T.append(dict(cell_id=cid, seconds=round(sec, 1)))
        print(f"[cell {i + 1}/{len(cells)}] {cid} {sec:.0f}s", flush=True)
        # summaries first, rewritten after every cell so a timeout keeps the finished cells
        pd.DataFrame(S).to_csv(os.path.join(a.out, f"w1_grid{suf}.csv"), index=False)
        pd.concat(WF).to_csv(os.path.join(a.out, f"w1_within_full_shape{suf}.csv"), index=False)
        pd.DataFrame(NV).to_csv(os.path.join(a.out, f"w1_narrowest_valid{suf}.csv"), index=False)
        pd.DataFrame(T).to_csv(os.path.join(a.out, f"w1_cell_seconds{suf}.csv"), index=False)
    if ex:
        ex.shutdown()
    IO5.write_provenance(a.out, "W1", __file__, cfg, extra=dict(wall_seconds=round(time.time() - t0),
                                                                selftest=st))
    print(f"[done] {len(cells)} cells {time.time() - t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
