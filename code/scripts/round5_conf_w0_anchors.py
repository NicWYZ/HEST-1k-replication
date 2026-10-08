#!/usr/bin/env python
"""Round 5, prediction-set track, stage W0: the three anchors.

docs/round5_conf_plan.md section 2, W0 item 3. Each anchor reruns an unmodified round-4 module on
Longleaf and compares the result with the committed round-4 record in this clone. Nothing in W1
starts until all three pass. Every output directory is stamped and gets PROVENANCE.txt
(round5_conf_io).

  sim       round4_conf_sim.run_cell, unmodified, seed tag "C1", the round-4 o grid and every
            registered method, on normal|K10|N500|share0.3|tau0.0 and normal|K20|N500|share0.3|tau0.0
            with 5,000 replicates and alpha in {0.1, 0.2}. Compared with c1_grid.csv on the key
            (cell_id, alpha, method, o). Tolerances: coverage 1e-4 absolute, price 1e-6 relative,
            frac_infinite identical. Those rows were computed on a laptop. Every other numeric
            column is reported with its largest difference and no tolerance.
  c3        round4_conf_c3.selftest on the first fit, then for CCRCC:24 with uni_v2 at K = 10, every
            fold and the 3 calibration draws, o0_rows (o = 0) and o_rows at o = 25 with the 20 label
            draws and the module's methods. Seeds in the module depend on (task, fold, K, calibration
            draw, o, label draw) only, not on the o grid, so a run at o = 25 alone reproduces the
            round-4 rows. Compared with c3_o_sweep.csv.gz rows of task CCRCC, encoder uni_v2, K 10,
            o in {0, 25}, on (task, label_set, encoder, method, score, alpha, o, K, fold, draw).
            Tolerances: coverage difference 0.0, width_mean and width_median at most 3e-10 (the
            cross-vendor floor round 4 measured), n_test and finite identical, selftest at most 1e-12.
  codepath  compares a fresh run of round4_conf_c1_codepath.py (run by the job, unmodified) with
            ghcp_repro_longleaf/setup/c1_codepath.csv. Test: n and n_nonzero identical per check,
            and max_diff reported beside the round-4 value.
"""
import argparse
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round5_conf_io as IO5  # noqa: E402

R4 = os.path.join(IO5.CLONE, "results", "round4", "conformal")
SIM_CELLS = ("normal|K10|N500|share0.3|tau0.0", "normal|K20|N500|share0.3|tau0.0")


def _diff(a, b, rel=False):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    both_nan = np.isnan(a) & np.isnan(b)
    both_inf = np.isinf(a) & np.isinf(b) & (np.sign(a) == np.sign(b))
    d = np.abs(a - b)
    if rel:
        d = d / np.maximum(np.abs(b), 1e-300)
    d = np.where(both_nan | both_inf, 0.0, d)
    d = np.where(np.isnan(d), np.inf, d)  # one side NaN or inf only: a mismatch
    return float(d.max()) if d.size else 0.0


def anchor_sim(a):
    import round4_conf_sim as SIM
    t0 = time.time()
    rows = []
    for cid in SIM_CELLS:
        K = int(cid.split("|")[1][1:])
        cells, _ = SIM.build_cells(K, include_semireal=False)
        cell = [c for c in cells if c["cell_id"] == cid]
        assert len(cell) == 1, cid
        cell = cell[0]
        tc = time.time()
        rr = SIM.run_cell(cell, [0.1, 0.2], a.reps, SIM.O_GRID, None)
        rs = SIM.realised_share(cell)
        for r in SIM.summarise(rr, cell):
            r["realised_share"] = rs
            rows.append(r)
        print(f"[sim] {cid} {time.time() - tc:.0f}s", flush=True)
    new = pd.DataFrame(rows)
    new.to_csv(os.path.join(a.out, "w0_sim_rows.csv"), index=False)
    ref = pd.read_csv(os.path.join(R4, "C1_testbed", "c1_grid.csv"))
    ref = ref[ref.cell_id.isin(SIM_CELLS)]
    key = ["cell_id", "alpha", "method", "o"]
    m = ref.merge(new, on=key, how="outer", suffixes=("_r4", "_r5"), indicator=True)
    n_only_r4 = int((m._merge == "left_only").sum())
    n_only_r5 = int((m._merge == "right_only").sum())
    b = m[m._merge == "both"]
    tol = {"coverage": ("abs", 1e-4), "price": ("rel", 1e-6), "frac_infinite": ("abs", 0.0)}
    out = [dict(check="rows_only_in_round4", value=n_only_r4, tol=0, passed=n_only_r4 == 0),
           dict(check="rows_only_in_round5", value=n_only_r5, tol=0, passed=n_only_r5 == 0),
           dict(check="rows_matched", value=len(b), tol=np.nan, passed=len(b) > 0)]
    num = [c for c in ref.columns if c not in key and pd.api.types.is_numeric_dtype(ref[c])]
    for c in num:
        kind, t = tol.get(c, ("abs", np.nan))
        d = _diff(b[f"{c}_r5"], b[f"{c}_r4"], rel=(kind == "rel"))
        out.append(dict(check=f"max_{kind}_diff:{c}", value=d, tol=t,
                        passed=(d <= t) if not np.isnan(t) else np.nan))
    res = pd.DataFrame(out)
    res.to_csv(os.path.join(a.out, "w0_sim_anchor.csv"), index=False)
    ok = bool(res.passed.dropna().astype(bool).all())
    IO5.write_provenance(a.out, "W0_sim", __file__, dict(stage="W0 sim anchor", cells=SIM_CELLS,
                         reps=a.reps, alphas=[0.1, 0.2], o_grid=list(SIM.O_GRID), seed_tag="C1"),
                         extra=dict(passed=ok, wall_seconds=round(time.time() - t0)))
    print(res.to_string(), flush=True)
    return ok


def anchor_c3(a):
    import round4_conf_c3 as C
    t0 = time.time()
    T = C.load_task(a.task, a.encoder)
    specs = T.specs(K=10, n_cal_draws=C.N_CAL_DRAWS)
    rows, checks = [], []
    for i, sp in enumerate(specs):
        fit = T.fit(sp)
        if i == 0:
            for r in C.selftest(fit):
                checks.append(dict(check="selftest:" + r["check"], value=r["max_abs_diff"],
                                   tol=1e-12, passed=bool(r["max_abs_diff"] <= 1e-12)))
        rows += C.o0_rows(fit, alphas=C.ALPHAS)
        rows += C.o_rows(fit, o_grid=(25,), label_draws=range(C.N_LABEL_DRAWS), alphas=C.ALPHAS)
        if (i + 1) % 6 == 0:
            print(f"[c3] {i + 1}/{len(specs)} fits {(time.time() - t0) / (i + 1):.1f}s per fit",
                  flush=True)
    new = C.to_c3(rows)
    new.to_csv(os.path.join(a.out, "w0_c3_rows.csv"), index=False)
    ref = pd.read_csv(os.path.join(R4, "C3_real", "c3_o_sweep.csv.gz"), dtype={"fold": str})
    task = new.task.iloc[0]
    ref = ref[(ref.task == task) & (ref.encoder == a.encoder) & (ref.K == 10) & ref.o.isin([0, 25])]
    new["fold"] = new["fold"].astype(str)
    key = ["task", "label_set", "encoder", "method", "score", "alpha", "o", "K", "fold", "draw"]
    m = ref.merge(new, on=key, how="outer", suffixes=("_r4", "_r5"), indicator=True)
    n4 = int((m._merge == "left_only").sum())
    n5 = int((m._merge == "right_only").sum())
    b = m[m._merge == "both"]
    checks += [dict(check="rows_only_in_round4", value=n4, tol=0, passed=n4 == 0),
               dict(check="rows_only_in_round5", value=n5, tol=0, passed=n5 == 0),
               dict(check="rows_matched", value=len(b), tol=np.nan, passed=len(b) > 0)]
    for c, t in (("coverage", 0.0), ("width_mean", 3e-10), ("width_median", 3e-10),
                 ("n_test", 0.0), ("finite", 0.0)):
        d = _diff(b[f"{c}_r5"], b[f"{c}_r4"])
        checks.append(dict(check=f"max_abs_diff:{c}", value=d, tol=t, passed=bool(d <= t)))
    res = pd.DataFrame(checks)
    res.to_csv(os.path.join(a.out, "w0_c3_anchor.csv"), index=False)
    ok = bool(res.passed.dropna().astype(bool).all())
    IO5.write_provenance(a.out, "W0_c3", __file__, dict(stage="W0 c3 anchor", task=a.task,
                         encoder=a.encoder, K=10, o=[0, 25], label_draws=C.N_LABEL_DRAWS,
                         cal_draws=C.N_CAL_DRAWS, alphas=list(C.ALPHAS)),
                         extra=dict(passed=ok, fits=len(specs), wall_seconds=round(time.time() - t0)))
    print(res.to_string(), flush=True)
    return ok


def anchor_codepath(a):
    new = pd.read_csv(os.path.join(a.fresh, "c1_codepath.csv"))
    ref = pd.read_csv(os.path.join(R4, "C1_testbed", "ghcp_repro_longleaf", "setup", "c1_codepath.csv"))
    m = ref.merge(new, on="check", how="outer", suffixes=("_r4", "_r5"))
    m["passed"] = (m.n_r4 == m.n_r5) & (m.n_nonzero_r4 == m.n_nonzero_r5)
    m.to_csv(os.path.join(a.out, "w0_codepath_anchor.csv"), index=False)
    ok = bool(m.passed.all())
    IO5.write_provenance(a.out, "W0_codepath", __file__, dict(stage="W0 codepath anchor",
                         fresh=a.fresh), extra=dict(passed=ok))
    print(m.to_string(), flush=True)
    return ok


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("anchor", choices=["sim", "c3", "codepath"])
    p.add_argument("--out", required=True)
    p.add_argument("--reps", type=int, default=5000)
    p.add_argument("--task", default="CCRCC:24")
    p.add_argument("--encoder", default="uni_v2")
    p.add_argument("--fresh", default="", help="codepath: directory of the fresh c1_codepath.csv")
    a = p.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    IO5.stamp(a.out, track="conformal-W0", note=f"W0 anchor {a.anchor}")
    ok = dict(sim=anchor_sim, c3=anchor_c3, codepath=anchor_codepath)[a.anchor](a)
    print(f"[done] anchor {a.anchor} passed={ok}", flush=True)
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
