#!/usr/bin/env python
"""Round 4, conformal track, stage C2, candidate K4: a group-level quantile model at o = 0.

docs/round4_conf_plan.md section 4 (C2, K4) and section 7. Runs behind the C1 simulation
interface (code/scripts/round4_conf_sim.py, md5 76fda34ee622e299bbaa806e5c8da98a).

THE METHOD
  For each calibration donor k = 1..K, q_k is the empirical (1 - alpha) quantile of its own
  scores |r_ki| (centre 0, the zero-mean global predictor of C1), taken as the order statistic
  Q_beta of the donor's N_k scores, Q_beta = inf{t : F_k(t) >= beta}, beta = 1 - alpha, with the
  relative tolerance 1e-12 the C1 code uses (i.e. the ceil(N_k beta (1 - 1e-12))-th smallest).
  Across donors, q_1..q_K are treated as an i.i.d. normal sample, and the new donor's quantile is
  predicted by the upper limit of the usual prediction interval for one new normal draw,
      qhat = qbar + t_{K-1, 1-alpha'} s_q sqrt(1 + 1/K),
  qbar the mean and s_q the sample standard deviation (ddof = 1) of the q_k, t_{K-1, p} the
  p-quantile of Student's t with K - 1 degrees of freedom, alpha' in {0.5, 0.25, 0.1}. The set
  for a test spot is |r - 0| <= qhat. Variants k4_a050, k4_a025, k4_a010, at o = 0 only (the
  method does not use the test donor's observations). Note t_{K-1, 0.5} = 0, so k4_a050 is
  exactly qbar, the plug-in mean of the donors' quantiles, with no allowance for spread.

ASSUMPTIONS AND GUARANTEE (model-based, NOT distribution-free)
  Assumptions: (i) exchangeability of donors; (ii) the q_k, which are random through both the
  donor effect and the finite N_k, are approximately normal across donors; (iii) the test
  donor's own (1 - alpha) quantile q_new is a draw from the same normal law, independent of the
  q_k; (iv) coverage of the donor's 500 test spots is approximately 1 - alpha when qhat equals
  q_new. Guarantee: under (i)-(iii) exactly, P(q_new <= qhat) = 1 - alpha', a prediction-interval
  statement about the new donor's quantile and not about coverage of a spot. The marginal
  spot-level coverage is then near (1 - alpha) only in the sense that E over donors of
  F_new(qhat) is about 1 - alpha' x (something below 1) plus the amount by which the average
  quantile level overshoots; no finite-sample guarantee for spot coverage is claimed, and
  none holds without the normality model. alpha' is NOT the miscoverage level of the set.
  This is the route most likely to be sharp and least likely to be safe under t_3 tails: under
  t_3 the donor quantile q_k is a heavy-tailed, right-skewed function of the scale b_k and the
  estimation noise of the 90 percent quantile of t_3, so the normal prediction limit from K
  donors is too small in the tail exactly when a heavy donor arrives, and the t correction has
  K - 1 degrees of freedom only, so at K = 5 and 7 the interval is wide but the normal
  tail still misstates the coverage. Part (c) of the criterion is met only in the model-based
  sense with the model named; the normality check below is the evidence on the model.

IMPLEMENTATION CHOICES (written before running)
  1. q_k uses the order-statistic definition above, not an interpolated np.quantile.
  2. The score centre is 0 and qhat is the threshold; q is finite always (K >= 5 >= 2), so
     frac_infinite is 0 in every row by construction.
  3. qhat is not clipped; q_k >= 0 and the t multiplier is >= 0 for alpha' <= 0.5, so qhat >= 0.
  4. Normality check (semireal cells at K = 10 only, both N specs): per replicate the
     Shapiro-Wilk test on the 10 simulated q_k (alpha 0.1), recording the p-value, sample skewness
     and excess kurtosis; summarised per cell and per gene in k4_qk_normality.csv. The check does
     not alter any method output. For comparison the same statistics are recorded for the
     synthetic normal and t3 cells at K = 10 (a reference, flagged in the column `kind`).
  5. Replicate draws use seed_tag 'C1' (the default), so the rows pair with C1's.
  6. Rows are for alpha = 0.1 only; the fast-path function returns None for other alphas.
"""
import hashlib
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
WC = os.environ.get("R4CONF_CODE", "/Users/nicolaszhang/HEST-1k-replication-conformal")
sys.path.insert(0, os.path.join(WC, "code", "scripts"))
import round4_conf_sim as S  # noqa: E402

ALPHA_PRIMES = {"k4_a050": 0.5, "k4_a025": 0.25, "k4_a010": 0.1}
KS = (5, 7, 9, 10, 12, 15, 20, 25, 50)
STATE = {"norm": [], "count": 0}
RECORD_KINDS = {"semireal", "normal", "t3"}


def donor_quantile(x, alpha):
    s = np.abs(x)
    n = len(s)
    k = max(1, math.ceil(n * (1 - alpha) * (1 - S.QTOL)))
    return float(np.partition(s, k - 1)[k - 1])


def f_k4(prep, rep, cell, o, rng, alphas):
    K = len(prep.cal)
    out = {v: [] for v in ALPHA_PRIMES}
    for a in alphas:
        if abs(a - 0.1) > 1e-12:
            for v in out:
                out[v].append(None)
            continue
        q = np.array([donor_quantile(x, a) for x in prep.cal])
        qbar, sq = q.mean(), q.std(ddof=1)
        for v, ap in ALPHA_PRIMES.items():
            t = stats.t.ppf(1 - ap, K - 1)
            out[v].append((float(qbar + t * sq * math.sqrt(1 + 1 / K)), 0.0))
        if K == 10 and cell["gen"] in RECORD_KINDS:
            w = stats.shapiro(q)
            STATE["norm"].append(dict(cell_id=cell["cell_id"], kind=cell["gen"], rep=STATE["count"],
                                      gene=rep["gene"] or "", p=float(w.pvalue), W=float(w.statistic),
                                      skew=float(stats.skew(q, bias=False)),
                                      exkurt=float(stats.kurtosis(q, bias=False))))
    STATE["count"] += 1
    return out


S.register_fast("k4", f_k4, False)


def normality_summary(rows):
    d = pd.DataFrame(rows)
    if d.empty:
        return pd.DataFrame()
    def agg(g):
        return pd.Series(dict(
            n_reps=len(g), median_p=g.p.median(), mean_p=g.p.mean(), frac_p_lt_05=(g.p < 0.05).mean(),
            frac_p_lt_01=(g.p < 0.01).mean(), mean_skew=g["skew"].mean(), mean_exkurt=g["exkurt"].mean()))

    def grp(frame, keys):
        rows = []
        for k, g in frame.groupby(keys):
            rows.append(dict(zip(keys, k), **agg(g).to_dict()))
        return pd.DataFrame(rows)

    c = grp(d, ["cell_id", "kind"])
    c.insert(2, "level", "cell")
    c.insert(3, "gene", "")
    sr = d[d.kind == "semireal"]
    if len(sr):
        g = grp(sr, ["cell_id", "kind", "gene"])
        g.insert(2, "level", "gene")
        c = pd.concat([c, g[c.columns]], ignore_index=True)
    return c


def main(argv=None):
    import argparse
    import round4_conf_io as IO
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--reps", type=int, default=S.N_REPS)
    p.add_argument("--Ks", default=",".join(map(str, KS)))
    p.add_argument("--cells", default="", help="comma list of cell indices (smoke only)")
    p.add_argument("--moments", default=os.path.join(
        WC, "results/round4/conformal/C1_testbed/inputs/a2_score_moments__resnet50.parquet"))
    a = p.parse_args(argv)
    t0 = time.time()
    got = hashlib.sha256(open(a.moments, "rb").read()).hexdigest()
    assert got == "74f80322a653cc531af9b1a74ed90fba5be56aa5fc4e3cbc8d2272c5308bfd3c", got
    assert IO.md5(S.__file__) == "76fda34ee622e299bbaa806e5c8da98a"
    IO.stamp(a.out, "C2", "K4 group-level quantile model, C2 fragment")
    os.makedirs(f"{a.out}/reps", exist_ok=True)
    semi = S.SemiReal(a.moments)
    alphas = [0.1]
    summ, ncell, norm_rows = [], 0, []
    for K in [int(x) for x in a.Ks.split(",")]:
        cells, _ = S.build_cells(K)
        if a.cells:
            cells = [cells[int(i)] for i in a.cells.split(",")]
        for cell in cells:
            tc = time.time()
            STATE["norm"], STATE["count"] = [], 0
            rr = S.run_cell(cell, alphas, a.reps, S.O_GRID, semi, methods=["k4"])
            rs = S.realised_share(cell)
            for row in S.summarise(rr, cell):
                row["realised_share"] = rs
                summ.append(row)
            norm_rows += STATE["norm"]
            rr.insert(0, "cell_id", cell["cell_id"])
            rr["gene"] = rr["gene"].astype(str)
            safe = re.sub(r"[^A-Za-z0-9.]+", "_", cell["cell_id"])
            pq.write_table(pa.Table.from_pandas(rr[[f.name for f in S.REP_SCHEMA]], schema=S.REP_SCHEMA,
                                                preserve_index=False), f"{a.out}/reps/c2_k4_reps__{safe}.parquet")
            del rr
            ncell += 1
            pd.DataFrame(summ).to_csv(f"{a.out}/c2_grid__K4.csv", index=False)
            print(f"[cell {ncell}] {cell['cell_id']} {time.time()-tc:.1f}s", flush=True)
    normality_summary(norm_rows).to_csv(f"{a.out}/k4_qk_normality.csv", index=False)
    cfg = dict(stage="C2", candidate="K4", Ks=a.Ks, reps=a.reps, alphas=alphas, o_grid=list(S.O_GRID),
               alpha_primes=ALPHA_PRIMES, moments=a.moments, seed="zlib.crc32 keys C1|cell|rep (default seed_tag C1)",
               cells=a.cells)
    IO.write_provenance(a.out, "C2", __file__, cfg, extra={"wall_seconds": round(time.time() - t0),
                                                          "n_cells": ncell})
    print(f"[done] {ncell} cells {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    sys.exit(main())
