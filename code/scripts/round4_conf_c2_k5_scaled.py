#!/usr/bin/env python
"""Round 4, conformal track, stage C2, candidate K5: a scaled (adaptive) score inside HCP and GHCP.

docs/round4_conf_plan.md section 4 (C2, K5). Behind the C1 interface of round4_conf_sim.py
(md5 76fda34ee622e299bbaa806e5c8da98a); registered with register_fast.

----------------------------------------------------------------------------------------------
WHAT K5 IS
Score s = |r - c| / sigma_hat instead of |r - c|, where sigma_hat is a within-donor scale
estimate. The interval for a test spot is c +- q * sigma_hat_test, with q the host method's
weighted (1 - alpha) quantile of the scaled held-out scores. The guarantee is the host's,
unchanged.

VARIANTS
  k5_ghcp  GHCP (round4_conf_sim.ghcp_fast primary settings: eta = 0, within-group adaptation on,
           n_glob = 13) with the scaled score. Defined for o >= 4 (floor(o/2) >= 2); on the C1
           grid o in {5, 10, 25, 50, 100}. Not defined at o = 0 and not run there.
  k5_hcp   o = 0 only. A within-donor scale for the test donor needs observations from the test
           donor; at o = 0 there are none, so the only scale that can be attached to the test
           donor is a constant. A constant scale (the same for every donor) cancels in the scaled
           score, so K5 inside HCP at o = 0 IS HCP, computed by round4_conf_sim.f_hcp and reported
           under the name k5_hcp. (Scaling calibration donors by their own sigma_hat_j and
           multiplying back by an unobservable test sigma would be invalid.) It is a restatement
           of HCP and carries no information beyond C1's hcp rows; it is included so that the
           plan's "inside HCP" question has an explicit answer (width ratio 1 by construction).

ASSUMPTIONS AND GUARANTEE (GHCP appendix B.1, as the brief states it)
  Same as the host: A1 group-level exchangeability, A2 reference sizes exchangeable and
  independent of the group laws, A3 within-group i.i.d.; plus the one condition B.1 adds: the
  scale sigma_hat_j must be built in EVERY group (calibration groups and the test group) by the
  same rule from that group's local training block only. Here the block is the group's first
  m = floor(o/2) residuals and the rule is the function `scale_of` below; held-out scores
  (observations m, m+1, ...) are then conditionally i.i.d. within the group given the block, so
  the host's argument goes through. Guarantee: coverage at least 1 - alpha (GHCP Theorem 2.1),
  upper bound as GHCP's with ties absent. It is a finite-sample, distribution-free guarantee
  under A1 to A3; K5 does not alter the infinite-threshold pattern (same weights and +inf atom
  as ghcp, so frac_infinite equals the ghcp variant's when the same donor J0 is drawn).

IMPLEMENTATION CHOICES (fixed before running)
  1. Scale: sigma_hat = max(sd, FLOOR_REL * rms0, ABS_FLOOR) where sd is the sample standard
     deviation (ddof = 1) of the first m residuals about their mean (as the brief specifies),
     rms0 = sqrt(mean of the squared first m residuals) (about zero, the known global
     predictor), FLOOR_REL = 0.1, ABS_FLOOR = 1e-12. The relative floor keeps a block of m = 2
     near-equal residuals from producing a near-zero scale; it is scale-equivariant, a function
     of the block alone, and identical in every group. Chosen before any run and not tuned.
  2. Centre: c_j = lambda * mean(first m residuals), lambda = m / (13 + m), exactly as ghcp_fast.
     The scale is taken about the block's own mean, not about c_j.
  3. Held-out scores |r - c_j| / sigma_hat_j with the host's weights 1/((|S_cal|+1) L_j); the
     test donor's o - m held-out scores use sigma_hat_test and carry 1/((|S_cal|+1) L_{K+1}); the
     +inf atom is (N_J0 - o)/((|S_cal|+1) L_{K+1}). Remark 2.2 (empty pool, e.g. N = 100 at
     o = 100) is handled as in ghcp_fast, with the scaled held-out scores.
  4. Returned half-width q = q_scaled * sigma_hat_test (infinite stays infinite); centre c_test.
  5. Random stream. run_cell seeds the per-method generator from the registered name. K5 is
     registered under the name "ghcp" in this process only, so that its donor draw J0 is the
     same as C1's ghcp at the same (cell, replicate, o) and K5 rows pair with C1's ghcp rows.
     The output variant names are k5_ghcp and k5_hcp; the C1 "ghcp" entry is not run here.
  6. alpha = 0.1 only, 5000 replicates, seed_tag "C1" (draws identical to C1's).
  7. Top-decile coverage is not assessed in C1 (no predicted values); recorded as such.
"""
import argparse
import math
import os
import re
import sys
import time

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

WC = os.environ.get("R4CONF_CODE", "/Users/nicolaszhang/HEST-1k-replication-conformal")
sys.path.insert(0, os.path.join(WC, "code", "scripts"))
import round4_conf_sim as S      # noqa: E402
import round4_conf_io as IO      # noqa: E402

FLOOR_REL = 0.1
ABS_FLOOR = 1e-12
K_LIST = (5, 7, 9, 10, 12, 15, 20, 25, 50)
MOMENTS = os.environ.get("R4CONF_MOMENTS", os.path.join(WC, "results/round4/conformal/C1_testbed/inputs/a2_score_moments__resnet50.parquet"))
MOMENTS_SHA = "74f80322a653cc531af9b1a74ed90fba5be56aa5fc4e3cbc8d2272c5308bfd3c"
OUT = os.path.join(WC, "results/round4/conformal/C2_candidates/frag_K5")


def scale_of(block):
    """The group-wise scale rule: the same function of a group's training block in every group."""
    block = np.asarray(block, float)
    sd = float(np.std(block, ddof=1))
    rms0 = float(np.sqrt(np.mean(block * block)))
    return max(sd, FLOOR_REL * rms0, ABS_FLOOR)


def k5_ghcp_fast(prep, init, o, alphas, rng, n_glob=S.N_GLOB, scale_fn=scale_of):
    N = prep.N
    m = o // 2
    assert m >= 2
    lamv = m / (n_glob + m)
    pool = np.where(N > o)[0]            # eta = 0: both pool rules give {k : N_k > o}
    c_test = lamv * float(np.mean(init[:m]))
    s_test = scale_fn(init[:m])
    betas = [1 - a for a in alphas]
    if len(pool) == 0:                   # Remark 2.2
        held = np.abs(init[m:o] - c_test) / s_test
        L = o + 1 - m
        qs = S.wquantiles(held, np.full(len(held), 1.0 / L), 1.0 / L, betas)
        return [(q * s_test, c_test) for q in qs]
    J0 = pool[rng.integers(len(pool))]
    Scal = [j for j in pool if j != J0]
    M = len(Scal) + 1
    sc, wt = [], []
    for j in Scal:
        cj = lamv * float(np.mean(prep.cal[j][:m]))
        sj = scale_fn(prep.cal[j][:m])
        h = prep.held_abs(j, m, cj) / sj
        sc.append(h)
        wt.append(np.full(len(h), 1.0 / (M * len(h))))
    Lt = N[J0] - m
    h = np.abs(init[m:o] - c_test) / s_test
    sc.append(h)
    wt.append(np.full(len(h), 1.0 / (M * Lt)))
    qs = S.wquantiles(np.concatenate(sc), np.concatenate(wt), (N[J0] - o) / (M * Lt), betas)
    return [(q * s_test, c_test) for q in qs]


def k5_ghcp_ref(cal, init, o, alpha, rng, n_glob=S.N_GLOB):
    """Independent reference (plain arrays, S.wquantile) used to check the fast path."""
    N = np.array([len(x) for x in cal])
    m = o // 2
    lamv = m / (n_glob + m)
    pool = np.where(N > o)[0]
    c_test = lamv * float(np.mean(init[:m]))
    s_test = scale_of(init[:m])
    if len(pool) == 0:
        held = np.abs(init[m:o] - c_test) / s_test
        L = o + 1 - m
        return S.wquantile(held, np.full(len(held), 1.0 / L), 1.0 / L, 1 - alpha) * s_test, c_test
    J0 = pool[rng.integers(len(pool))]
    Scal = [j for j in pool if j != J0]
    M = len(Scal) + 1
    sc, wt = [], []
    for j in Scal:
        x = cal[j]
        cj = lamv * float(np.mean(x[:m]))
        h = np.abs(x[m:] - cj) / scale_of(x[:m])
        sc.append(h)
        wt.append(np.full(len(h), 1.0 / (M * len(h))))
    Lt = N[J0] - m
    sc.append(np.abs(init[m:o] - c_test) / s_test)
    wt.append(np.full(len(sc[-1]), 1.0 / (M * Lt)))
    q = S.wquantile(np.concatenate(sc), np.concatenate(wt), (N[J0] - o) / (M * Lt), 1 - alpha)
    return q * s_test, c_test


def f_k5(prep, rep, cell, o, rng, alphas):
    if o == 0:
        return {"k5_hcp": S.f_hcp(prep, rep, cell, 0, rng, alphas)["hcp"]}
    if o < 4:
        return {}
    return {"k5_ghcp": k5_ghcp_fast(prep, rep["init"], o, alphas, rng,
                                    cell.get("n_glob", S.N_GLOB))}


# registered under "ghcp" (this process only) so the per-method generator equals C1's ghcp stream
S.register_fast("ghcp", f_k5, True)


def check_fast(n=40):
    """Fast path vs reference, and unit-scale K5 vs S.ghcp_fast (max abs differences)."""
    w_ref = w_unit = 0.0
    for t in range(n):
        rng = np.random.default_rng(S.crc(f"k5check|{t}"))
        cell = dict(gen="t3" if t % 2 else "normal", K=int(rng.choice([5, 9, 10, 20])),
                    N=str(rng.choice(["100", "500", "unequal"])), sigma_a=float(rng.choice([0.0, 1.0])),
                    tau=float(rng.choice([0.0, 0.3])), n_test=50, n_glob=S.N_GLOB)
        rep = S.draw_replicate(cell, rng, 100, None)
        prep = S.Prep(rep["cal"])
        for o in (5, 10, 25, 50, 100):
            r1, r2, r3, r4 = (np.random.default_rng(t * 997 + o) for _ in range(4))
            qf, cf = k5_ghcp_fast(prep, rep["init"], o, [0.1], r1)[0]
            qr, cr = k5_ghcp_ref(rep["cal"], rep["init"], o, 0.1, r2)
            if np.isfinite(qf) or np.isfinite(qr):
                w_ref = max(w_ref, abs(qf - qr) if np.isfinite(qf) and np.isfinite(qr) else math.inf)
            w_ref = max(w_ref, abs(cf - cr))
            qu, cu = k5_ghcp_fast(prep, rep["init"], o, [0.1], r3, scale_fn=lambda b: 1.0)[0]
            qg, cg = S.ghcp_fast(prep, rep["init"], o, [0.1], r4, True, 0.0, S.N_GLOB)[0]
            if np.isfinite(qu) or np.isfinite(qg):
                w_unit = max(w_unit, abs(qu - qg) if np.isfinite(qu) and np.isfinite(qg) else math.inf)
            w_unit = max(w_unit, abs(cu - cg))
    return w_ref, w_unit


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--reps", type=int, default=5000)
    p.add_argument("--Ks", default=",".join(map(str, K_LIST)))
    p.add_argument("--cell-idx", default="", help="smoke only: comma list of cell indices per K")
    p.add_argument("--out", default=OUT)
    p.add_argument("--label", default="", help="suffix for the summary csv when a K is split over jobs")
    a = p.parse_args(argv)
    t0 = time.time()
    IO.stamp(a.out, "C2", "K5 scaled score inside HCP and GHCP, C2 candidate fragment frag_K5")
    wr, wu = check_fast()
    print(f"[check] fast-vs-ref {wr:.3g}  unit-scale-vs-ghcp {wu:.3g}", flush=True)
    assert wr < 1e-9 and wu < 1e-9
    import hashlib
    assert hashlib.sha256(open(MOMENTS, "rb").read()).hexdigest() == MOMENTS_SHA
    semi = S.SemiReal(MOMENTS)
    os.makedirs(f"{a.out}/reps", exist_ok=True)
    summ, ncell = [], 0
    for K in [int(x) for x in a.Ks.split(",")]:
        cells, sig = S.build_cells(K)
        if a.cell_idx:
            cells = [cells[int(i)] for i in a.cell_idx.split(",")]
        for cell in cells:
            tc = time.time()
            rr = S.run_cell(cell, [0.1], a.reps, S.O_GRID, semi, methods=["ghcp"])
            rs = S.realised_share(cell)
            for row in S.summarise(rr, cell):
                row["realised_share"] = rs
                summ.append(row)
            rr.insert(0, "cell_id", cell["cell_id"])
            rr["gene"] = rr["gene"].astype(str)
            safe = re.sub(r"[^A-Za-z0-9.]+", "_", cell["cell_id"])
            pq.write_table(pa.Table.from_pandas(rr[[f.name for f in S.REP_SCHEMA]], schema=S.REP_SCHEMA,
                                                preserve_index=False), f"{a.out}/reps/c2_reps__K5__{safe}.parquet")
            del rr
            ncell += 1
            pd.DataFrame(summ).to_csv(f"{a.out}/c2_grid__K5{a.label}.csv", index=False)
            print(f"[cell {ncell}] K{K} {cell['cell_id']} {time.time()-tc:.0f}s", flush=True)
    cfg = dict(stage="C2", candidate="K5", variants=["k5_hcp", "k5_ghcp"], Ks=a.Ks, reps=a.reps,
               alphas=[0.1], o_grid=list(S.O_GRID), floor_rel=FLOOR_REL, abs_floor=ABS_FLOOR,
               n_glob=S.N_GLOB, seed_tag="C1", moments=MOMENTS, moments_sha256=MOMENTS_SHA,
               sim_md5="76fda34ee622e299bbaa806e5c8da98a", registered_under="ghcp (stream pairing)")
    IO.write_provenance(a.out, "C2", os.path.abspath(__file__), cfg,
                        extra={"wall_seconds": round(time.time() - t0), "n_cells": ncell})
    print(f"[done] {ncell} cells {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    sys.exit(main())
