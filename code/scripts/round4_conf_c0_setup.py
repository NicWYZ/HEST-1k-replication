#!/usr/bin/env python
"""Round 4, conformal track, stage C0: the lung reader check and the anchor.

docs/round4_conf_plan.md section 4, C0 items 2 and 3.

  lung    Exercises round4_conf_io.load_set_dropped on NCBI865 for each encoder and records the
          embedding-file rows (expected 2,143), the rows dropped (1, barcode 051x019) and the rows
          kept (expected 2,142). Also records that round 3's own load_set raises on NCBI865, which
          is why the wrapper exists, and that the lung target list carries no control feature.
  anchor  Reads the output of an unmodified rerun of round3_a4b_hcp.py (arms a1_rule_K6 and K10,
          donor set 24, one encoder) and checks it against the committed round-3 files:
            A  a1_rule_K6 pooled coverage, fold mean over draws (A4b's own aggregation), against
               A1's committed CCRCC `donor` `abs` coverage in a1_by_fold__<enc>__main.csv, at 1e-15;
            B  every K10 hcp, pooled and dwr row (fold, draw) against the committed
               a4b_hcp_K10__<enc>.csv, coverage at 1e-12, widths reported;
            C  the rerun's mean K10 hcp coverage against the committed per-encoder mean, at 1e-12;
            D  a4b_summary.csv's `coverage_mean` for donor_set=24 arm=K10 method=hcp against the
               mean over the three committed per-encoder tables, at 1e-12. This is the check that
               ties a one-encoder rerun to a three-encoder summary (plan section 8 flag 2);
            E  the rerun's own anchor table (a4b_anchor__<enc>.csv) passes.
          A miss in A is examined for a count flip before it is read as a failure (plan flag 2).
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_io as IO  # noqa: E402

ROOT = IO.DATA_ROOT
LUNG_TD = f"{ROOT}/results/round4/data/P5_task/LUNG_XENIUM.json"
A1_DIR = f"{ROOT}/results/round3/A1_coverage"
A4_DIR = f"{ROOT}/results/round3/A4_scores"
ENCODERS = ("hoptimus0", "uni_v2", "resnet50")


def run_lung(out):
    td = json.load(open(LUNG_TD))
    D4 = IO.import_round3("round3_d4_sets")
    genes, n_ctrl_list = IO.drop_control_features(td["target_genes"]["list"])
    rows = []
    for enc in ENCODERS:
        X, Y, samp, bc, xy, rec, n_ctrl = IO.load_set_dropped(td, enc, genes, ["NCBI865"], D4=D4)
        n_emb, n_drop, n_kept = rec["NCBI865"]
        rows.append(dict(check="wrapper_NCBI865", encoder=enc, n_embedding_rows=n_emb,
                         n_dropped=n_drop, n_kept=n_kept, X_rows=X.shape[0], Y_rows=Y.shape[0],
                         xy_rows=xy.shape[0], n_genes=Y.shape[1], dropped_in_output=int(
                             "051x019" in set(bc)), passed=bool(n_emb == 2143 and n_drop == 1
                             and n_kept == 2142 and X.shape[0] == Y.shape[0] == 2142
                             and "051x019" not in set(bc))))
    # round 3's own loader, unmodified, on the same one sample: expected to raise.
    td1 = dict(td, samples=[s for s in td["samples"] if s["sample_id"] == "NCBI865"])
    try:
        D4.load_set(td1, "resnet50", genes)
        raised, msg = False, ""
    except AssertionError as e:
        raised, msg = True, str(e)
    rows.append(dict(check="round3_load_set_raises_on_NCBI865", encoder="resnet50",
                     passed=raised, note=msg))
    rows.append(dict(check="lung_target_list_controls", encoder="", n_genes=len(genes),
                     n_dropped=n_ctrl_list, passed=bool(n_ctrl_list == 0 and len(genes) == 343)))
    d = pd.DataFrame(rows)
    d.to_csv(f"{out}/c0_lung_wrapper.csv", index=False)
    print(d.to_string(index=False), flush=True)
    return bool(d["passed"].all())


def run_anchor(out, rerun_dir, enc):
    rows = []

    def add(check, n, stat, value, tol, passed, note=""):
        rows.append(dict(check=check, n=n, statistic=stat, value=value, tol=tol,
                         passed=bool(passed), note=note))

    mine = pd.read_csv(f"{rerun_dir}/a4b_hcp_K10__{enc}.csv")
    ref = pd.read_csv(f"{A4_DIR}/a4b_hcp_K10__{enc}.csv")
    mine["fold"] = mine["fold"].astype(str)
    ref["fold"] = ref["fold"].astype(str)

    # A: A1 donor coverage at 1e-15
    a1 = pd.read_csv(f"{A1_DIR}/a1_by_fold__{enc}__main.csv")
    a1 = a1[(a1.task == "CCRCC") & (a1.design == "donor") & (a1.score == "abs")].copy()
    a1["fold"] = a1["fold"].astype(str)
    k6 = mine[(mine.arm == "a1_rule_K6") & (mine.method == "pooled") & (mine.donor_set.astype(str) == "24")]
    g = k6.groupby("fold")[["coverage", "width_mean"]].mean().reset_index()
    j = g.merge(a1[["fold", "coverage", "width_mean"]], on="fold", suffixes=("_mine", "_a1"))
    dc = (j.coverage_mine - j.coverage_a1).abs()
    add("A_K6_pooled_vs_A1_donor", len(j), "max |dcoverage|", float(dc.max()), 1e-15,
        len(j) == a1.fold.nunique() == 24 and dc.max() <= 1e-15,
        f"{len(j)} of {a1.fold.nunique()} folds; max |dwidth| "
        f"{float((j.width_mean_mine - j.width_mean_a1).abs().max()):.3e}; "
        f"folds with dcoverage > 1e-15: {int((dc > 1e-15).sum())}")
    j.to_csv(f"{out}/c0_anchor_A_by_fold.csv", index=False)

    # B, C: K10 rows against the committed per-encoder table
    key = ["donor_set", "arm", "fold", "draw", "method"]
    for t in (mine, ref):
        t["donor_set"] = t["donor_set"].astype(str)
    sel = lambda t: t[(t.arm == "K10") & (t.donor_set == "24")]
    jb = sel(mine)[key + ["coverage", "width_mean", "finite"]].merge(
        sel(ref)[key + ["coverage", "width_mean", "finite"]], on=key, suffixes=("_mine", "_ref"))
    for m in ("hcp", "pooled", "dwr"):
        jm = jb[jb.method == m]
        dcv = float((jm.coverage_mine - jm.coverage_ref).abs().max())
        dw = float((jm.width_mean_mine - jm.width_mean_ref).abs().max())
        add(f"B_K10_{m}_rows_vs_committed", len(jm), "max |dcoverage|", dcv, 1e-12,
            len(jm) == 72 and dcv <= 1e-12, f"max |dwidth_mean| {dw:.3e}; finite mine "
            f"{int(jm.finite_mine.sum())} ref {int(jm.finite_ref.sum())}")
    cm = float(sel(mine)[sel(mine).method == "hcp"].coverage.mean())
    cr = float(sel(ref)[sel(ref).method == "hcp"].coverage.mean())
    add("C_K10_hcp_mean_vs_committed_encoder_mean", 72, "|mine - committed|", abs(cm - cr), 1e-12,
        abs(cm - cr) <= 1e-12, f"mine {cm!r}, committed {cr!r}, encoder {enc}")

    # D: the three-encoder summary equals the mean of the per-encoder tables
    s = pd.read_csv(f"{A4_DIR}/a4b_summary.csv")
    sv = float(s[(s.metric == "coverage_mean") &
                 (s.scope == "donor_set=24 arm=K10 method=hcp")].value.iloc[0])
    allr = pd.concat([pd.read_csv(f"{A4_DIR}/a4b_hcp_K10__{e}.csv") for e in ENCODERS])
    allr["donor_set"] = allr["donor_set"].astype(str)
    h = allr[(allr.arm == "K10") & (allr.donor_set == "24") & (allr.method == "hcp")]
    add("D_summary_equals_mean_of_encoder_tables", len(h), "|summary - mean|",
        abs(sv - float(h.coverage.mean())), 1e-12, abs(sv - float(h.coverage.mean())) <= 1e-12,
        f"summary {sv!r}, mean {float(h.coverage.mean())!r}, n {len(h)}")

    # E: the rerun's own anchor table
    acc = pd.read_csv(f"{rerun_dir}/a4b_anchor__{enc}.csv")
    bad = acc[acc.passed.astype(str) == "False"]
    add("E_rerun_own_anchor_table", len(acc), "rows failing", len(bad), 0, len(bad) == 0,
        "; ".join(bad.check.astype(str)))

    d = pd.DataFrame(rows)
    d.to_csv(f"{out}/c0_anchor.csv", index=False)
    print(d.to_string(index=False), flush=True)
    return bool(d.passed.all())


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("lung", "anchor"))
    p.add_argument("--out", required=True)
    p.add_argument("--rerun-dir")
    p.add_argument("--encoder", default="resnet50")
    a = p.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    IO.check_harness()
    cfg = dict(stage="C0", mode=a.mode, encoder=a.encoder, lung_td=LUNG_TD,
               rerun_dir=a.rerun_dir, anchor_tols={"A": 1e-15, "B": 1e-12, "C": 1e-12, "D": 1e-12})
    ok = run_lung(a.out) if a.mode == "lung" else run_anchor(a.out, a.rerun_dir, a.encoder)
    IO.write_provenance(a.out, "C0", __file__, cfg, extra={"mode": a.mode, "passed": ok})
    print(f"[C0 {a.mode}] {'PASS' if ok else 'FAIL'}", flush=True)
    return 0 if ok else 5


if __name__ == "__main__":
    sys.exit(main())
