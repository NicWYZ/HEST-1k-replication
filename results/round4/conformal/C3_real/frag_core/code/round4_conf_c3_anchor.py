#!/usr/bin/env python
"""Round 4, conformal track, C3 core: the acceptance anchor and the smoke of every o > 0 method.

docs/round4_conf_plan.md section 6 (C3 Acceptance): the CCRCC K = 10, o = 0 pooled, HCP and
one-per-donor rows from round4_conf_c3 reproduce results/round3/A4_scores/a4b_hcp_K10__<enc>.csv to
1e-12, on both donor sets (24 and 23_merged) and every (fold, draw) cell (72 and 69 per method).
The three-encoder a4b_summary.csv is checked after the per-encoder jobs finish, by the merge step
(`--merge`), which also writes c3_anchor.csv.

Per-encoder run:   round4_conf_c3_anchor.py run --encoder <enc> --out <dir> [--smoke]
Merge (light):     round4_conf_c3_anchor.py merge --dir <dir>
"""
import argparse
import glob
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_c3 as C  # noqa: E402
import round4_conf_io as IO  # noqa: E402

A4 = f"{IO.DATA_ROOT}/results/round3/A4_scores"
MAP = {"pooled": "pooled", "hcp": "hcp", "one_per": "dwr"}
TOL = 1e-12


def run(a):
    IO.check_harness()
    os.makedirs(a.out, exist_ok=True)
    IO.code_head = C._read_head      # no git command: HEAD is read from the clone's files
    IO.stamp(a.out, track="conformal-C3-core", note=f"C3 anchor and smoke, {a.encoder}")
    checks, mine_rows = [], []
    ref = pd.read_csv(f"{A4}/a4b_hcp_K10__{a.encoder}.csv")
    ref["fold"] = ref["fold"].astype(str)
    ref["donor_set"] = ref["donor_set"].astype(str)
    smoke_done = False
    times = []
    for key in ("CCRCC:24", "CCRCC:23_merged"):
        T = C.load_task(key, a.encoder)
        specs = T.specs(10, 3)
        for i, sp in enumerate(specs):
            t0 = time.time()
            fit = T.fit(sp)
            rows = C.o0_rows(fit, alphas=(0.1,), dwr_reps=C.DWR_REPS)
            mine_rows += rows
            times.append(time.time() - t0)
            if i == 0 and key == "CCRCC:24":
                for r in C.selftest(fit):
                    checks.append(dict(check="selftest:" + r["check"], encoder=a.encoder, n=1,
                                       max_abs_diff=r["max_abs_diff"], tol=1e-12,
                                       passed=bool(r["max_abs_diff"] <= 1e-12),
                                       note="fast kernels against round4_conf_sim / A3 references"))
                if a.smoke and not smoke_done:
                    sm = C.o_rows(fit, o_grid=(25,), label_draws=range(2))
                    sm += C.o0_rows(fit, dwr_reps=5)
                    pd.DataFrame(sm)[C.FIXED_COLS + C.EXTRA_COLS].to_csv(
                        f"{a.out}/c3_smoke.csv", index=False)
                    smoke_done = True
            if (i + 1) % 12 == 0:
                print(f"  [{key}] {i+1}/{len(specs)} fits, {np.mean(times):.1f}s per fit "
                      f"(o=0 methods)", flush=True)
        del T
    mine = pd.DataFrame(mine_rows)
    mine.to_csv(f"{a.out}/c3_anchor_rows__{a.encoder}.csv", index=False)

    for key, ds in (("CCRCC:24", "24"), ("CCRCC:23_merged", "23_merged")):
        for m, rm in MAP.items():
            x = mine[(mine.donor_set == ds) & (mine.method == m) & (mine.alpha == 0.1)].copy()
            r = ref[(ref.arm == "K10") & (ref.donor_set == ds) & (ref.method == rm)].copy()
            x["fold"] = x["fold"].astype(str)
            r = r.rename(columns=lambda c: c + "_ref")
            j = x.merge(r, left_on=["fold", "cal_draw"], right_on=["fold_ref", "draw_ref"])
            ok_n = len(j) == len(x) == len(r)
            for col in ("coverage", "width_mean", "width_median"):
                d = float((j[col] - j[col + "_ref"]).abs().max()) if len(j) else np.nan
                checks.append(dict(check=f"K10_{ds}_{m}_vs_a4b_{rm}_{col}", encoder=a.encoder,
                                   n=len(j), max_abs_diff=d, tol=TOL,
                                   passed=bool(ok_n and d <= TOL),
                                   note=f"rows mine {len(x)} ref {len(r)}"))
            dfin = int((j["finite"] != j["finite_ref"]).sum()) if len(j) else -1
            checks.append(dict(check=f"K10_{ds}_{m}_finite_flag", encoder=a.encoder, n=len(j),
                               max_abs_diff=float(dfin), tol=0.0, passed=bool(ok_n and dfin == 0),
                               note="rows where finite differs"))
            for mc, rc in (("n_T_donors", "n_T_donors"), ("n_T_matched", "n_T_spots_matched"),
                           ("n_C", "n_C"), ("K", "n_cal_units")):
                d = float((j[mc] - j[rc + "_ref"]).abs().max()) if len(j) else np.nan
                checks.append(dict(check=f"K10_{ds}_{m}_design_{mc}", encoder=a.encoder, n=len(j),
                                   max_abs_diff=d, tol=0.0, passed=bool(ok_n and d == 0),
                                   note=f"{mc} against a4b {rc}"))
    d = pd.DataFrame(checks)
    d.to_csv(f"{a.out}/c3_anchor__{a.encoder}.csv", index=False)
    print(d[["check", "n", "max_abs_diff", "tol", "passed"]].to_string(index=False), flush=True)
    IO.write_provenance(a.out, "C3core", __file__, dict(encoder=a.encoder, smoke=a.smoke,
                        tol=TOL, dwr_reps=C.DWR_REPS), extra={"passed": bool(d.passed.all()),
                        "fit_seconds_mean_o0": float(np.mean(times)), "n_fits": len(times)})
    return 0 if bool(d.passed.all()) else 5


def merge(a):
    parts = sorted(glob.glob(f"{a.dir}/anchor_*/c3_anchor__*.csv"))
    d = pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
    rows = pd.concat([pd.read_csv(p) for p in sorted(glob.glob(f"{a.dir}/anchor_*/c3_anchor_rows__*.csv"))])
    s = pd.read_csv(f"{a.a4}/a4b_summary.csv")
    add = []
    for ds in ("24", "23_merged"):
        for m, rm in MAP.items():
            sc = f"donor_set={ds} arm=K10 method={rm}"
            x = rows[(rows.donor_set.astype(str) == ds) & (rows.method == m) & (rows.alpha == 0.1)]
            for metric, col in (("coverage_mean", "coverage"), ("width_mean", "width_mean"),
                                ("width_median", "width_median")):
                v = float(s[(s.metric == metric) & (s.scope == sc)].value.iloc[0])
                mv = float(x[col].mean())
                add.append(dict(check=f"summary_{metric}_{sc}", encoder="all3", n=len(x),
                                max_abs_diff=abs(mv - v), tol=TOL,
                                passed=bool(abs(mv - v) <= TOL and x.encoder.nunique() == 3),
                                note=f"mine {mv!r} summary {v!r}"))
    d = pd.concat([d, pd.DataFrame(add)], ignore_index=True)
    d = d[["check", "encoder", "n", "max_abs_diff", "tol", "passed", "note"]]
    d.to_csv(f"{a.dir}/c3_anchor.csv", index=False)
    print(d[["check", "encoder", "n", "max_abs_diff", "passed"]].to_string(index=False))
    print("ALL PASSED" if d.passed.all() else "SOME FAILED")
    return 0 if d.passed.all() else 5


def final(a):
    """Recompute every anchor comparison from saved row tables (one per encoder) against the
    committed a4b tables. Reading (the C0 reading, oversight-accepted): the anchor passes when
    coverage agrees at 1e-12 and the finite flags and design columns agree exactly; width
    differences are recorded beside it with the CPU vendor of the node that produced the rows,
    because the base head's floating point differs between AMD and Intel nodes at about 1e-10."""
    specs = [x.split("=", 1) for x in a.rows]            # enc=path:vendor
    out, allrows = [], []
    for enc, pv in specs:
        path, vendor = pv.rsplit(":", 1)
        mine = pd.read_csv(path)
        mine["fold"] = mine["fold"].astype(str)
        allrows.append(mine)
        ref = pd.read_csv(f"{a.a4}/a4b_hcp_K10__{enc}.csv")
        ref["fold"] = ref["fold"].astype(str)
        ref["donor_set"] = ref["donor_set"].astype(str)
        for ds in ("24", "23_merged"):
            for m, rm in MAP.items():
                x = mine[(mine.donor_set.astype(str) == ds) & (mine.method == m)
                         & (mine.alpha == 0.1)]
                r = ref[(ref.arm == "K10") & (ref.donor_set == ds) & (ref.method == rm)]
                r = r.rename(columns=lambda c: c + "_ref")
                j = x.merge(r, left_on=["fold", "cal_draw"], right_on=["fold_ref", "draw_ref"])
                ok_n = len(j) == len(x) == len(r)
                dc = float((j.coverage - j.coverage_ref).abs().max())
                dw = float((j.width_mean - j.width_mean_ref).abs().max())
                dm = float((j.width_median - j.width_median_ref).abs().max())
                dfin = int((j.finite != j.finite_ref).sum())
                dsg = max(float((j[c1] - j[c2 + "_ref"]).abs().max()) for c1, c2 in (
                    ("n_T_donors", "n_T_donors"), ("n_T_matched", "n_T_spots_matched"),
                    ("n_C", "n_C"), ("K", "n_cal_units")))
                out.append(dict(check=f"K10_{ds}_{m}_vs_a4b_{rm}", encoder=enc, n=len(j),
                                max_abs_dcoverage=dc, tol_coverage=TOL,
                                max_abs_dwidth_mean=dw, max_abs_dwidth_median=dm,
                                finite_flag_mismatches=dfin, design_col_max_diff=dsg,
                                cpu_vendor=vendor,
                                passed=bool(ok_n and dc <= TOL and dfin == 0 and dsg == 0)))
    d = pd.DataFrame(out)
    rows = pd.concat(allrows)
    s = pd.read_csv(f"{a.a4}/a4b_summary.csv")
    add = []
    for ds in ("24", "23_merged"):
        for m, rm in MAP.items():
            sc = f"donor_set={ds} arm=K10 method={rm}"
            x = rows[(rows.donor_set.astype(str) == ds) & (rows.method == m) & (rows.alpha == 0.1)]
            v = {mt: float(s[(s.metric == mt) & (s.scope == sc)].value.iloc[0])
                 for mt in ("coverage_mean", "width_mean", "width_median")}
            dc = abs(float(x.coverage.mean()) - v["coverage_mean"])
            add.append(dict(check=f"summary_{sc}", encoder="all3", n=len(x),
                            max_abs_dcoverage=dc, tol_coverage=TOL,
                            max_abs_dwidth_mean=abs(float(x.width_mean.mean()) - v["width_mean"]),
                            max_abs_dwidth_median=abs(float(x.width_median.mean())
                                                      - v["width_median"]),
                            finite_flag_mismatches=0, design_col_max_diff=0.0,
                            cpu_vendor=";".join(sorted({p.rsplit(":", 1)[1] for _, p in specs})),
                            passed=bool(dc <= TOL and x.encoder.nunique() == 3)))
    d = pd.concat([d, pd.DataFrame(add)], ignore_index=True)
    d.insert(2, "n", d.pop("n"))
    d.insert(3, "max_abs_diff", d["max_abs_dcoverage"])
    d.insert(4, "tol", d["tol_coverage"])
    d = d.drop(columns=["tol_coverage"])
    cols = ["check", "encoder", "n", "max_abs_diff", "tol", "passed"]
    d = d[cols + [c for c in d.columns if c not in cols]]
    IO.stamp(a.out, track="conformal-C3-core", note="C3 core anchor table (final)")
    d.to_csv(f"{a.out}/c3_anchor.csv", index=False)
    print(d[cols + ["max_abs_dwidth_mean", "cpu_vendor"]].to_string(index=False))
    print("ALL PASSED (coverage reading)" if d.passed.all() else "SOME FAILED")
    return 0 if d.passed.all() else 5


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--encoder", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--smoke", action="store_true")
    m = sub.add_parser("merge")
    m.add_argument("--dir", required=True)
    m.add_argument("--a4", default=A4)
    f = sub.add_parser("final")
    f.add_argument("--rows", nargs="+", required=True, help="enc=path:vendor")
    f.add_argument("--a4", required=True)
    f.add_argument("--out", required=True)
    a = p.parse_args()
    sys.exit({"run": run, "merge": merge, "final": final}[a.cmd](a))
