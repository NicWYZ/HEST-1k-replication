#!/usr/bin/env python
"""Round 4, conformal track, stage C3: merge the eight unit fragments and compute report numbers.

docs/round4_conf_plan.md section 6 (C3), section 12.3 (memo changes) and section 12.8. Inputs are
the fragment tables under results/round4/conformal/C3_real/frag_<unit>/. Outputs in C3_real/:

  c3_o_sweep.csv          the fixed-format o-axis table (task, label_set, encoder, method, score,
                          alpha, o, K, fold, draw, coverage, width_mean, width_median, n_test,
                          finite), every HEST task and ACS, o = 0 included. Read by the PPI
                          track's Q5.
  c3_o_sweep_by_task.csv  per (task, label_set, encoder, method, score, alpha, o, K): mean over
                          folds of the per-fold mean over draws (coverage), its sd over folds, the
                          mean width over finite rows, and the finite share.
  c3_K_sweep.csv          the o = 0 K axis (CCRCC both donor sets, Indiana K = 10, lung K 6/8/10,
                          ACS K 4 to 10), plus the CCRCC GHCP o = 25 K rows when present.
  c3_by_fold.csv          per fold, mean over draws, for both tables.
  c3_merge_checks.csv     collisions, row counts, normalisation applied, K = 10 o = 0 equality
                          between the K units and the o units on each HEST task.
  c3_report_numbers.csv   the numbers the C4 report cites, by prediction.

Normalisation, applied to ACS rows only and recorded in the checks: score 'absolute' -> 'abs',
method 'dwr' -> 'one_per', K cast to int. ACS `finite` is the share of a fold's test states with
a finite interval (the ACS units aggregate states per fold); HEST `finite` is 0/1 per row. Task
names keep the donor set: 'CCRCC' is the 24-donor set and 'CCRCC_23merged' the merged set.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_io as IO  # noqa: E402

FIXED = ["task", "label_set", "encoder", "method", "score", "alpha", "o", "K", "fold", "draw",
         "coverage", "width_mean", "width_median", "n_test", "finite"]
KEY = FIXED[:10]
O_FILES = ["frag_CCRCC_o/c3_o_sweep__CCRCC.csv", "frag_Indiana_o/c3_o_sweep__INDIANA.csv",
           "frag_Lung_o/c3_o_sweep__LUNG.csv", "frag_ACS_o/c3_o_sweep__ACS.csv"]
K_FILES = ["frag_CCRCC_K/c3_K_sweep__CCRCC.csv", "frag_Indiana_K/c3_K_sweep__INDIANA.csv",
           "frag_Lung_K/c3_K_sweep__LUNG.csv", "frag_ACS_K/c3_K_sweep__ACS.csv"]
K_GHCP = "frag_CCRCC_K/ghcp_o25/c3_K_sweep_ghcp_o25__CCRCC.csv"
K_COLS = ["task", "label_set", "encoder", "method", "score", "alpha", "o", "K", "n_T_donors",
          "fold", "draw", "coverage", "width_mean", "width_median", "n_test", "finite"]


def norm(d):
    d = d.copy()
    d["score"] = d["score"].replace({"absolute": "abs"})
    d["method"] = d["method"].replace({"dwr": "one_per"})
    d["K"] = d["K"].round().astype(int)
    d["finite"] = d["finite"].astype(float)
    if "o" not in d.columns:
        d["o"] = 0
    if "n_T_donors" not in d.columns and "n_train_groups" in d.columns:
        d["n_T_donors"] = d["n_train_groups"]
    return d


def by_fold(d, extra=()):
    g = list(KEY[:8]) + list(extra) + ["fold"]
    d = d.assign(w_fin=d.width_mean.where(np.isfinite(d.width_mean)))
    return (d.groupby(g, dropna=False)
             .agg(coverage=("coverage", "mean"), width_mean=("w_fin", "mean"),
                  finite=("finite", "mean"), n_draws=("draw", "size"))
             .reset_index())


def by_task(bf, extra=()):
    g = list(KEY[:8]) + list(extra)
    return (bf.groupby(g, dropna=False)
              .agg(coverage=("coverage", "mean"), coverage_sd_folds=("coverage", "std"),
                   width_mean=("width_mean", "mean"), finite=("finite", "mean"),
                   n_folds=("fold", "size"))
              .reset_index())


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True, help="results/round4/conformal/C3_real")
    a = p.parse_args(argv)
    R = a.root
    checks = []

    def chk(name, value, passed, note=""):
        checks.append(dict(check=name, value=value, passed=passed, note=note))

    parts = []
    for f in O_FILES:
        d = pd.read_csv(os.path.join(R, f), low_memory=False)
        assert list(d.columns) == FIXED, (f, list(d.columns))
        parts.append(norm(d))
        chk(f"rows {f}", len(d), True)
    O = pd.concat(parts, ignore_index=True)[FIXED]
    dup = int(O.duplicated(KEY).sum())
    chk("o sweep duplicated keys", dup, dup == 0)
    O.to_csv(os.path.join(R, "c3_o_sweep.csv"), index=False)
    bfo = by_fold(O)
    bto = by_task(bfo)
    bto.to_csv(os.path.join(R, "c3_o_sweep_by_task.csv"), index=False)

    kp = []
    for f in K_FILES:
        d = norm(pd.read_csv(os.path.join(R, f), low_memory=False))
        kp.append(d[K_COLS])
        chk(f"rows {f}", len(d), True)
    gk = os.path.join(R, K_GHCP)
    if os.path.exists(gk):
        d = norm(pd.read_csv(gk, low_memory=False))
        kp.append(d[K_COLS])
        chk(f"rows {K_GHCP}", len(d), True)
    else:
        chk(f"rows {K_GHCP}", 0, False, "file absent")
    Kt = pd.concat(kp, ignore_index=True)
    dupk = int(Kt.duplicated(KEY).sum())
    chk("K sweep duplicated keys", dupk, dupk == 0)
    Kt.to_csv(os.path.join(R, "c3_K_sweep.csv"), index=False)
    bfk = by_fold(Kt, extra=("n_T_donors",))
    btk = by_task(bfk, extra=("n_T_donors",))
    btk.to_csv(os.path.join(R, "c3_K_sweep_by_task.csv"), index=False)
    pd.concat([bfo.assign(table="o_sweep"), bfk.assign(table="K_sweep")],
              ignore_index=True).to_csv(os.path.join(R, "c3_by_fold.csv"), index=False)

    # K = 10, o = 0 rows: K units against o units, HEST tasks
    m = Kt[(Kt.K == 10) & (Kt.o == 0) & (Kt.task != "ACS")]
    n = O[(O.K == 10) & (O.o == 0) & (O.task != "ACS")]
    j = m.merge(n, on=KEY, suffixes=("_k", "_o"))
    dc = float((j.coverage_k - j.coverage_o).abs().max()) if len(j) else float("nan")
    fin = np.isfinite(j.width_mean_k) & np.isfinite(j.width_mean_o)
    dw = float((j.width_mean_k - j.width_mean_o)[fin].abs().max()) if fin.any() else float("nan")
    chk("K=10 o=0 K units vs o units, matched rows", len(j), len(j) > 0)
    chk("same, max |dcoverage|", dc, dc <= 1e-12)
    chk("same, max |dwidth_mean| (AMD/Intel nodes)", dw, dw <= 1e-9)
    pd.DataFrame(checks).to_csv(os.path.join(R, "c3_merge_checks.csv"), index=False)

    report_numbers(bto, btk, R)
    IO.write_provenance(R, "C3", __file__, dict(stage="C3 merge", o_files=O_FILES, k_files=K_FILES))
    print(pd.DataFrame(checks).to_string(index=False))
    return 0


def report_numbers(bto, btk, R):
    rows = []

    def add(pred, qty, scope, val):
        rows.append(dict(prediction=pred, quantity=qty, scope=scope, value=val))

    def enc_mean(d, col):
        return float(d[col].mean()) if len(d) else float("nan")

    # C3.1, CCRCC K axis (both donor sets), mean over encoders
    for task in ["CCRCC", "CCRCC_23merged"]:
        for alpha in [0.1, 0.2]:
            for K in sorted(btk[btk.task == task].K.unique()):
                s = btk[(btk.task == task) & (btk.alpha == alpha) & (btk.K == K) & (btk.o == 0)]
                h, pl = s[s.method == "hcp"], s[s.method == "pooled"]
                sc = f"{task} alpha={alpha} K={K}"
                add("C3.1", "hcp coverage, mean over encoders", sc, enc_mean(h, "coverage"))
                add("C3.1", "hcp finite share, mean over encoders", sc, enc_mean(h, "finite"))
                add("C3.1", "pooled coverage, mean over encoders", sc, enc_mean(pl, "coverage"))
                if len(h) and len(pl):
                    r = h.merge(pl, on=["encoder"], suffixes=("_h", "_p"))
                    add("C3.1", "hcp/pooled mean width, mean over encoders", sc,
                        float((r.width_mean_h / r.width_mean_p).mean()))
                add("C3.1", "training donors", sc, float(s.n_T_donors.mean()) if len(s) else np.nan)
    # revised C3.2 at K = 10 on every HEST task (primary GHCP = 'ghcp')
    for task in ["CCRCC", "CCRCC_23merged", "INDIANA_KIDNEY", "LUNG_XENIUM"]:
        s = bto[(bto.task == task) & (bto.K == 10) & (bto.alpha == 0.1)]
        g = s[s.method == "ghcp"]
        add("C3.2r", "ghcp coverage, min over o and encoders", task, float(g.coverage.min()))
        hcp0 = s[(s.method == "hcp") & (s.o == 0)].set_index("encoder").width_mean
        wp = s[s.method == "within_plain"].set_index(["encoder", "o"]).width_mean
        for o in sorted(g.o.unique()):
            gi = g[g.o == o].set_index("encoder").width_mean
            add("C3.2r", "ghcp coverage, mean over encoders", f"{task} o={o}",
                float(g[g.o == o].coverage.mean()))
            add("C3.2r", "ghcp / hcp(o=0) width, mean over encoders", f"{task} o={o}",
                float((gi / hcp0).mean()))
            w = pd.Series({e: wp.get((e, o), np.nan) for e in gi.index})
            add("C3.2r", "ghcp / within_plain width, mean over encoders", f"{task} o={o}",
                float((gi / w).mean()))
    gk = btk[(btk.method == "ghcp") & (btk.o == 25) & (btk.task == "CCRCC")]
    for alpha in [0.1]:
        for K in sorted(gk.K.unique()):
            s = gk[(gk.alpha == alpha) & (gk.K == K)]
            add("C3.2r", "CCRCC ghcp coverage at o=25, mean over encoders", f"alpha={alpha} K={K}",
                float(s.coverage.mean()))
    # C3.5: gaps at K = 10, o = 0, alpha 0.1
    for task in ["CCRCC", "CCRCC_23merged", "INDIANA_KIDNEY", "LUNG_XENIUM", "ACS"]:
        s = bto[(bto.task == task) & (bto.K == 10) & (bto.o == 0) & (bto.alpha == 0.1)]
        pl, h = s[s.method == "pooled"], s[s.method == "hcp"]
        add("C3.5", "pooled coverage shortfall from 0.9, mean over encoders", task,
            0.9 - enc_mean(pl, "coverage"))
        add("C3.5", "pooled coverage sd over folds, mean over encoders", task,
            enc_mean(pl, "coverage_sd_folds"))
        if len(h) and len(pl):
            r = h.merge(pl, on="encoder", suffixes=("_h", "_p"))
            add("C3.5", "hcp/pooled width, mean over encoders", task,
                float((r.width_mean_h / r.width_mean_p).mean()))
    # C3.6: recentred
    for task in ["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM"]:
        s = bto[(bto.task == task) & (bto.K == 10) & (bto.alpha == 0.1)]
        pc = enc_mean(s[(s.method == "pooled") & (s.o == 0)], "coverage")
        add("C3.6", "pooled coverage at o=0, mean over encoders", task, pc)
        for o in sorted(s[s.method == "recentred"].o.unique()):
            rc = enc_mean(s[(s.method == "recentred") & (s.o == o)], "coverage")
            add("C3.6", "recentred coverage, mean over encoders", f"{task} o={o}", rc)
            add("C3.6", "recentred minus pooled coverage", f"{task} o={o}", rc - pc)
            add("C3.6", "recentred minus nominal 0.9", f"{task} o={o}", rc - 0.9)
    # C3.4: top-decile coverage, CCRCC, the 6-gene CQR set of round 3 A4 (gene_set 'cqr6')
    t4p = os.path.join(R, "frag_CCRCC_o", "c3_c34_top_decile__CCRCC.csv")
    if os.path.exists(t4p):
        t4 = pd.read_csv(t4p)
        t4 = t4[t4.gene_set == "cqr6"]
        for (meth, sc, o), g in t4.groupby(["method", "score", "o"]):
            add("C3.4", f"top-decile coverage, {meth} {sc}, mean over encoders", f"cqr6 o={o}",
                float(g.top_cov.mean()))
            add("C3.4", f"overall coverage, {meth} {sc}, mean over encoders", f"cqr6 o={o}",
                float(g.all_cov.mean()))
    # C3.5: the ACS reproduction of the GHCP paper
    ap = os.path.join(R, "frag_ACS_o", "acs_ghcp_reproduction.csv")
    if os.path.exists(ap):
        a = pd.read_csv(ap)
        for t, g in a.groupby("table"):
            add("C3.5", "ACS paper values reproduced within tolerance", f"table {t}",
                int(g.within_tolerance.sum()))
            add("C3.5", "ACS paper values transcribed", f"table {t}", int(len(g)))
    pd.DataFrame(rows).to_csv(os.path.join(R, "c3_report_numbers.csv"), index=False)


if __name__ == "__main__":
    sys.exit(main())
