#!/usr/bin/env python
"""Round 4, conformal track, stage C2, candidate K1: smoothed HCP at o = 0.

docs/round4_conf_plan.md section 4 (C2). Method name 'k1_smoothed', o = 0 only (uses_o False),
one variant 'k1_smoothed'. Written before it runs.

THRESHOLD RULE
  HCP (Lee, Barber and Willett) at level beta = 1 - alpha uses the measure
      nu = sum_{k<=K} (1/(K+1)) F_k  +  (1/(K+1)) delta_{+inf},
  F_k donor k's empirical score distribution (each spot 1/N_k), and q = Q_beta(nu), the generalised
  quantile with the atom at +inf. The test donor's block of mass 1/(K+1) is one whole donor's
  worth, so the achievable HCP levels move in steps of 1/(K+1) at the donor level. With
  x = beta (K+1), m = floor(x) and theta = x - m in [0, 1), K1 draws U ~ Unif(0,1), independent
  of all data, and uses
      level_lo = m/(K+1)        if U >= theta,
      level_hi = (m+1)/(K+1)    if U <  theta,
      q = Q_level(nu).
  This is Vovk, Gammerman and Shafer's smoothed (randomised) conformal p-value applied to the donor
  blocks: the random variable U decides how many whole donor blocks of mass 1/(K+1) are counted
  below the threshold (the fractional block that the ceiling in HCP rounds up is counted with
  probability theta). U does not enter the within-donor weights 1/((K+1) N_k), which are
  untouched, and the test donor's 1/(K+1) stays at +inf in both branches. When x is an integer
  (K = 9 at alpha = 0.1) theta = 0 and K1 equals HCP. When m + 1 = K + 1 (K = 5, 7 at alpha = 0.1)
  the upper branch is q = +inf, so q is infinite with probability theta (0.4 and 0.2).

GUARANTEE (finite-sample, under hierarchical exchangeability, same assumptions as HCP)
  Lee, Barber and Willett's theorem holds for HCP at every level, so conditional on U the
  coverage of the test donor's spot is at least level_U, and at most level_U + 2/(K+1) when
  scores are distinct. Averaging over U, with P(level_hi) = theta,
      P(cover) >= (1 - theta) m/(K+1) + theta (m+1)/(K+1) = (m + theta)/(K+1) = 1 - alpha
  exactly, and P(cover) <= 1 - alpha + 2/(K+1) with distinct scores. The coverage is over the draw
  of data, the test spot and U jointly (marginal, not conditional on U). The lower bound is an
  equality when the donors' score distributions are point-mass-like and separated (between-donor
  share 1, the one-spot-per-donor case, where the rule is exactly the rank-randomised split
  conformal rule with P(cover) = (m + theta)/(K+1) = beta). So "equality in expectation" holds
  in that extremal configuration, which is what a distribution-free statement can demand; in
  other configurations HCP's own slack (the test donor's absence from its own measure, about
  beta/K more than beta with no donor effect) remains and tie-handling cannot remove it. Part (c)
  of the criterion is MET: finite-sample, distribution-free under hierarchical exchangeability.
  Not claimed: conditional-on-U validity, validity for the donor's own spot distribution.

IMPLEMENTATION CHOICES (also in candidate_definition_K1.md)
  * Float tolerance: m = floor(x (1 + 1e-12)), theta = max(0, x - m) (so an integer x gives
    theta = 0), quantiles with C1's QTOL = 1e-12 via wquantiles.
  * One U per replicate per alpha, from the method's own rng (seed key C1|cell|repR|k1_smoothed|o0),
    so replicate data are identical to C1's; U is drawn even when theta = 0 (stream fixed).
  * Weights and score arrays are those of C1's f_hcp (Prep.held_abs, 1/((K+1)N_k), atom 1/(K+1)).

PREDICTION C2.1: K1 recovers less than a tenth of the gap between HCP and the oracle at K = 10,
because the lower level moves only from 10/11 down to 9/11 with probability 0.1 and the mean level
stays 0.909 versus 0.9; the atom's mass (the donor block), not tie handling, is what costs width.
"""
import argparse
import math
import os
import sys
import time

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

WC = os.environ.get("R4CONF_CODE", "/Users/nicolaszhang/HEST-1k-replication-conformal")
sys.path.insert(0, os.path.join(WC, "code", "scripts"))
import round4_conf_sim as S  # noqa: E402

NAME = "k1_smoothed"
SEMI_PATH = os.environ.get("R4CONF_MOMENTS", "results/round4/conformal/C1_testbed/inputs/a2_score_moments__resnet50.parquet")
SEMI_SHA = "74f80322a653cc531af9b1a74ed90fba5be56aa5fc4e3cbc8d2272c5308bfd3c"
KS = (5, 7, 9, 10, 12, 15, 20, 25, 50)


def levels(K, alpha):
    """(level_lo, level_hi, theta) of the smoothed rule."""
    x = (1 - alpha) * (K + 1)
    m = math.floor(x * (1 + 1e-12))
    th = max(0.0, x - m)
    return m / (K + 1), (m + 1) / (K + 1), th


def k1_smoothed(prep, rep, cell, o, rng, alphas):
    K = len(prep.N)
    s = np.concatenate([prep.held_abs(j, 0, 0.0) for j in range(K)])
    w = np.concatenate([np.full(n, 1.0 / ((K + 1) * n)) for n in prep.N])
    out = []
    for a in alphas:
        lo, hi, th = levels(K, a)
        u = rng.random()
        beta = hi if u < th else lo
        out.append((S.wquantiles(s, w, 1.0 / (K + 1), [beta])[0], 0.0))
    return {NAME: out}


S.register_fast(NAME, k1_smoothed, False)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--reps", type=int, default=S.N_REPS)
    p.add_argument("--Ks", default=",".join(map(str, KS)))
    p.add_argument("--cells", type=int, default=0, help="smoke: first n cells per K")
    p.add_argument("--smoke-pick", default="", help="comma list of cell indices (smoke)")
    a = p.parse_args(argv)
    t0 = time.time()
    sys.path.insert(0, os.path.join(WC, "code", "scripts"))
    import round4_conf_io as IO
    import hashlib
    assert hashlib.md5(open(os.path.join(WC, "code", "scripts", "round4_conf_sim.py"), "rb").read()).hexdigest() == \
        "76fda34ee622e299bbaa806e5c8da98a"
    assert hashlib.sha256(open(SEMI_PATH, "rb").read()).hexdigest() == SEMI_SHA
    IO.stamp(a.out, "C2", "candidate K1, smoothed HCP at o=0, C1 grid at alpha 0.1, 5000 reps")
    os.makedirs(f"{a.out}/reps", exist_ok=True)
    semi = S.SemiReal(SEMI_PATH)
    summ, n_done = [], 0
    pick = [int(x) for x in a.smoke_pick.split(",") if x != ""]
    for K in [int(x) for x in a.Ks.split(",")]:
        cells, _ = S.build_cells(K)
        if pick:
            cells = [cells[i] for i in pick]
        elif a.cells:
            cells = cells[:a.cells]
        for cell in cells:
            tc = time.time()
            rr = S.run_cell(cell, [0.1], a.reps, S.O_GRID, semi, methods=[NAME])
            rs = S.realised_share(cell)
            for row in S.summarise(rr, cell):
                row["realised_share"] = rs
                summ.append(row)
            rr.insert(0, "cell_id", cell["cell_id"])
            rr["gene"] = rr["gene"].astype(str)
            safe = "".join(c if c.isalnum() or c == "." else "_" for c in cell["cell_id"])
            pq.write_table(pa.Table.from_pandas(rr[[f.name for f in S.REP_SCHEMA]],
                           schema=S.REP_SCHEMA, preserve_index=False),
                           f"{a.out}/reps/c2_reps__{NAME}__{safe}.parquet")
            n_done += 1
            pd.DataFrame(summ).to_csv(f"{a.out}/c2_grid__K1.csv", index=False)
            print(f"[cell {n_done}] {cell['cell_id']} {time.time()-tc:.1f}s", flush=True)
    cfg = dict(stage="C2", candidate="K1", method=NAME, Ks=a.Ks, reps=a.reps, alphas=[0.1],
               o_grid=list(S.O_GRID), n_test=S.N_TEST, qtol=S.QTOL, seed_tag="C1",
               moments=SEMI_PATH, moments_sha256=SEMI_SHA, smoke_cells=a.cells,
               smoke_pick=a.smoke_pick)
    IO.write_provenance(a.out, "C2", __file__, cfg,
                        extra={"wall_seconds": round(time.time() - t0), "n_cells": n_done})
    print(f"[done] {n_done} cells {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
