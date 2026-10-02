#!/usr/bin/env python
"""Round 4, conformal track, stage C2, candidate K6: the switch rule of docs/round4_conf_lower_bound.md
section 5, as addendum 1 (plan section 10 item 4) specifies it. o = 0 only, method 'k6_switch'.

THE RULE (finite N_k, alpha fixed per call, scores s = |r|)
  1. For each of the K calibration donors take the empirical CDF of its scores. D = the maximum
     pairwise Kolmogorov distance between them, computed exactly as sup_t [max_k F_k(t) - min_k F_k(t)]
     over the pooled score points (identical to the maximum over pairs of the pairwise sup distances).
  2. Tolerance d = d_0 + 2 eps_N, eps_N = sqrt(log(2/0.01) / (2 N_min)) (DKW half-width at level 0.01
     for the smallest calibration donor, N_min = min_k N_k). d_0 = 0 (the natural reading: the tolerance
     is the DKW noise band alone). If D > d_cap = 2 Phi(1.5) - 1 = 0.8664 (see 'cap') the rule is HCP.
  3. If D <= d: pooled branch. The threshold is the empirical quantile at level 1 - alpha + delta of the
     donor mixture sum_k (1/K) F_k (weight 1/(K N_k) per spot, no atom at +infinity), the object the probe
     of section 5 calls 'the pooled quantile of their mixture'. Else: HCP (Lee, Barber and Willett) at
     level 1 - alpha, identical to the C1 'hcp' method (weight 1/((K+1)N_k), atom 1/(K+1) at +infinity,
     so infinite when 1/(K+1) > alpha; K = 5 and 7 at alpha = 0.1). Centre c = 0 on both branches.
  4. delta = delta(K, d). The probe code/scripts/round4_conf_c2_lower_bound.py measures distance as a
     normal location shift g in within-donor standard deviations. The Kolmogorov distance between N(0,1)
     and N(g,1) is 2 Phi(g/2) - 1, so g = 2 Phi^{-1}((1 + d)/2). delta is the smallest value on that
     file's bisection (14 steps on [0, 0.1 - 1e-9], return the upper end; delta = 0 if the worst
     coverage at delta = 0 is already >= 1 - alpha) at which the file's worst(K, alpha, g, delta)
     coverage is >= 1 - alpha. worst() is imported, the bisection is the one in its main() restated.

IMPLEMENTATION CHOICES (decided before running)
  - d_0 = 0.
  - delta cache: computed exactly at a grid of d values per K (D_GRID below, which contains the three
    equal-N tolerances 2 eps at N = 100, 500, 2000, so equal-N cells use the exact delta for their
    (K, N_min)); other N_min (unequal N, semireal) use linear interpolation of delta in d between grid
    points, clamped to the grid ends. delta is increasing and convex in d on the probe's range, so linear
    interpolation can only overstate delta (conservative). Cached to k6_delta_table.json.
  - cap: the probe's configurations reach Kolmogorov distance at most 2 Phi(1.5) - 1 = 0.8664 (g <= 3), so
    beyond that tolerance the probe says nothing; there the rule is HCP. With N_min >= 100 the largest
    tolerance is 0.3256, so the cap never binds on the C1 grid (reported, not a reduction).
  - alpha: the probe was run at alpha = 0.1; delta is computed at the call's alpha (0.1 only here).
  - Ties and boundaries: D <= d inclusive; quantile tolerance QTOL as the C1 methods.
  - The rule is deterministic given the calibration data; the supplied rng is unused. Replicate draws
    are C1's (seed_tag 'C1').

ASSUMPTIONS AND GUARANTEE (lower-bound document sections 8.3, 8.4, 8.5)
  Assumes hierarchical exchangeability of calibration and test donors and within-donor i.i.d. scores.
  The rule as specified is NOT valid, even with the group laws revealed exactly: section 8.3 gives a
  counterexample (ten N(0,1) groups and one point mass just above the pooled threshold, K = 10, alpha =
  0.1, coverage 0.89899 < 0.9), which attains the worst-case bound of section 5, case 3. With finite N_k
  the DKW event (probability at least 1 - K gamma, gamma = 0.01) adds a possible loss of K gamma (0.1 at
  K = 10), so the repaired rule of 8.3 would cover at least 1 - alpha - K gamma, and the unrepaired rule
  carries no stated finite-sample guarantee. Criterion part (c) is unmet. The repaired rule is not run.
  Prediction C2.6 (addendum 1): K6 covers at least 0.89 in every cell and meets (b) only in cells with
  between-donor share 0.1, so it fails (b) overall; its price of validity equals HCP's at shares 0.3
  and 0.5.
"""
import json
import math
import os
import re
import sys
import time

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("R4K6_CODE_CLONE", "/Users/nicolaszhang/HEST-1k-replication-conformal")
sys.path.insert(0, os.path.join(REPO, "code", "scripts"))
import round4_conf_sim as S  # noqa: E402
import round4_conf_c2_lower_bound as LB  # noqa: E402

NAME = "k6_switch"
D0 = 0.0
GAMMA = 0.01
D_CAP = 2 * stats.norm.cdf(1.5) - 1
D_GRID = [0.03, 0.05, 0.0728, 0.1, 0.1456, 0.2, 0.3256, 0.5, D_CAP]
DELTA_CACHE = os.environ.get("R4K6_DELTA_CACHE", os.path.join(HERE, "..", "k6_delta_table.json"))
_TABLE = None
BR = {}   # cell_id -> [n, n_pooled, sum_D, sum_d, sum_delta_pooled]


def eps_n(nmin):
    return math.sqrt(math.log(2 / GAMMA) / (2 * nmin))


def g_of_d(d):
    return 2 * stats.norm.ppf((1 + d) / 2)


def probe_delta(K, alpha, g):
    """The bisection of the probe's main(), with its worst() imported."""
    if LB.worst(K, alpha, g, 0.0)[0] >= 1 - alpha:
        return 0.0
    lo, hi = 0.0, alpha - 1e-9
    for _ in range(14):
        mid = (lo + hi) / 2
        if LB.worst(K, alpha, g, mid)[0] >= 1 - alpha:
            hi = mid
        else:
            lo = mid
    return hi


def delta_table():
    global _TABLE
    if _TABLE is None:
        _TABLE = json.load(open(DELTA_CACHE)) if os.path.exists(DELTA_CACHE) else {}
    return _TABLE


def delta_for(K, alpha, d):
    t = delta_table()
    key = f"{K}|{alpha}"
    if key not in t:
        t[key] = {"d": [], "g": [], "delta": []}
        for dd in D_GRID:
            g = float(g_of_d(dd))
            t0 = time.time()
            t[key]["d"].append(float(dd)); t[key]["g"].append(g)
            t[key]["delta"].append(float(probe_delta(K, alpha, g)))
            print(f"[delta] K={K} d={dd:.4f} g={g:.4f} delta={t[key]['delta'][-1]:.6f} {time.time()-t0:.0f}s", flush=True)
        json.dump(t, open(DELTA_CACHE, "w"), indent=1)
    e = t[key]
    return float(np.interp(d, e["d"], e["delta"]))


def kolmogorov_spread(lab_sorted, N):
    """sup_t [max_k F_k - min_k F_k] over the pooled points, from the donor label of each pooled score
    in sorted order (ECDF of donor k at each pooled point = running count of its label / N_k). With
    continuous scores there are no ties across donors; the result equals the searchsorted form."""
    n = len(lab_sorted)
    mx = np.zeros(n); mn = np.ones(n)
    for k in range(len(N)):
        F = np.cumsum(lab_sorted == k, dtype=np.int32) * (1.0 / N[k])
        np.maximum(mx, F, out=mx); np.minimum(mn, F, out=mn)
    return float((mx - mn).max())


def _q(cw, P, tot, beta):
    i = np.searchsorted(cw, beta * tot * (1 - S.QTOL), side="left")
    return math.inf if i >= len(cw) else float(P[i])


def k6_switch(prep, rep, cell, o, rng, alphas):
    K = len(prep.N)
    A = prep.cal
    sc = np.abs(np.concatenate(A))
    o_ = np.argsort(sc, kind="stable")
    P = sc[o_]
    lab = np.repeat(np.arange(K, dtype=np.int16), prep.N)
    D = kolmogorov_spread(lab[o_], prep.N)
    d = D0 + 2 * eps_n(int(prep.N.min()))
    res = []
    b = BR.setdefault(cell["cell_id"], [0, 0, 0.0, 0.0, 0.0])
    for a in alphas:
        pooled = (D <= d) and (d <= D_CAP)
        if pooled:
            dl = delta_for(K, a, d)
            w = np.concatenate([np.full(len(x), 1.0 / (K * len(x))) for x in A])
            cw = np.cumsum(w[o_])
            q = _q(cw, P, cw[-1], 1 - a + dl)
            b[1] += 1; b[4] += dl
        else:
            w = np.concatenate([np.full(len(x), 1.0 / ((K + 1) * len(x))) for x in A])
            cw = np.cumsum(w[o_])
            q = _q(cw, P, cw[-1] + 1.0 / (K + 1), 1 - a)
        b[0] += 1; b[2] += D; b[3] += d
        res.append((q, 0.0))
    return {NAME: res}


S.register_fast(NAME, k6_switch, False)


def _code_head_nogit(clone=None):
    clone = clone or REPO
    try:
        h = open(os.path.join(clone, ".git", "HEAD")).read().strip()
        if h.startswith("ref:"):
            ref = h.split()[1]
            pr = os.path.join(clone, ".git", "packed-refs")
            p = os.path.join(clone, ".git", ref)
            if os.path.exists(p):
                return open(p).read().strip()
            for ln in open(pr):
                if ln.strip().endswith(" " + ref):
                    return ln.split()[0]
            return f"unresolved ref {ref}"
        return h
    except Exception as e:
        return f"unreadable ({e.__class__.__name__})"


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--reps", type=int, default=5000)
    p.add_argument("--Ks", default="5,7,9,10,12,15,20,25,50")
    p.add_argument("--cells", default="", help="comma list of cell indices per K (smoke)")
    p.add_argument("--regex", default="", help="regex filter on cell_id, used to split a K over jobs")
    p.add_argument("--tag", default="", help="suffix of the per-job summary files")
    p.add_argument("--moments", default=os.environ.get("R4K6_MOMENTS", os.path.join(
        REPO, "results/round4/conformal/C1_testbed/inputs/a2_score_moments__resnet50.parquet")))
    a = p.parse_args()
    import round4_conf_io as IO
    t0 = time.time()
    out = os.path.abspath(a.out)
    IO.stamp(out, "C2", "candidate K6 switch rule, C1 grid at alpha 0.1, fragment frag_K6")
    os.makedirs(f"{out}/reps", exist_ok=True)
    IO.code_head = _code_head_nogit   # the brief forbids git commands; read .git/HEAD instead
    semi = S.SemiReal(a.moments)
    sel = [int(x) for x in a.cells.split(",")] if a.cells else None
    summ, nc, tt = [], 0, []
    for K in [int(x) for x in a.Ks.split(",")]:
        cells, _ = S.build_cells(K)
        for ci, cell in enumerate(cells):
            if sel is not None and ci not in sel:
                continue
            if not re.search(a.regex, cell["cell_id"]):
                continue
            tc = time.time()
            rr = S.run_cell(cell, [0.1], a.reps, S.O_GRID, semi, methods=[NAME])
            rs = S.realised_share(cell)
            for row in S.summarise(rr, cell):
                row["realised_share"] = rs
                summ.append(row)
            rr.insert(0, "cell_id", cell["cell_id"])
            rr["gene"] = rr["gene"].astype(str)
            safe = re.sub(r"[^A-Za-z0-9.]+", "_", cell["cell_id"])
            pq.write_table(pa.Table.from_pandas(rr[[f.name for f in S.REP_SCHEMA]], schema=S.REP_SCHEMA,
                                                preserve_index=False), f"{out}/reps/c2_k6_reps__{safe}.parquet")
            del rr
            nc += 1
            pd.DataFrame(summ).to_csv(f"{out}/c2_grid__K6{a.tag}.csv", index=False)
            pd.DataFrame([dict(cell_id=k, n=v[0], frac_pooled=v[1] / v[0], mean_D=v[2] / v[0],
                               mean_d=v[3] / v[0], mean_delta_when_pooled=(v[4] / v[1] if v[1] else float("nan")))
                          for k, v in BR.items()]).to_csv(f"{out}/k6_branch_stats{a.tag}.csv", index=False)
            print(f"[cell {nc}] {cell['cell_id']} {time.time()-tc:.0f}s total {time.time()-t0:.0f}s", flush=True)
    cfg = dict(stage="C2", candidate=NAME, Ks=a.Ks, reps=a.reps, alphas=[0.1], o_grid=[0], d0=D0, gamma=GAMMA,
               d_cap=float(D_CAP), d_grid=D_GRID, seed_tag="C1", cells=a.cells, regex=a.regex, tag=a.tag, moments=a.moments)
    IO.write_provenance(out, "C2", os.path.abspath(__file__), cfg,
                        extra={"wall_seconds": round(time.time() - t0), "n_cells": nc,
                               "sim_md5": IO.md5(os.path.join(REPO, "code/scripts/round4_conf_sim.py"))})
    print(f"[done] {nc} cells {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
