#!/usr/bin/env python3
"""Round 3, stage A1: build the report tables from the per-encoder harness outputs.

Stage: A1, the marginal-coverage table across fold designs. Reads the per-encoder
summary CSVs written by code/scripts/round3_a0_harness.py into
results/round3/A1_coverage/ and produces the tables the A1 stage report quotes,
plus the benchmark-Pearson comparison the handoff asks to be shown beside them.

This file exists rather than living in a notebook cell because the numeric-claim
gate requires every reported number to be re-readable from a file, and because the
tables get rebuilt each time another encoder lands.

Writes, in this order (summaries before anything bulky, per WAYS_OF_WORKING):
  a1_coverage_by_design.csv      design x score, pooled over tasks and encoders
  a1_coverage_by_task_design.csv task x design x score, over encoders
  a1_coverage_by_encoder.csv     encoder x design x score, over tasks
  a1_calibration_unit_table.csv  which folds calibrated at donor, slide, block
  a1_vs_benchmark_pearson.csv    coverage beside the benchmark's own Pearson
  a1_aggregation_note.csv        pooled versus slide-mean coverage on the random design

No seeds, no randomness: this is aggregation only.
"""
import argparse
import csv
import glob
import json
import os
import statistics as st
from collections import defaultdict

DESIGNS = ["random", "patient", "donor", "slide_out"]
SCORES = ["abs", "scaled"]


def read_rows(pattern):
    out = []
    for p in sorted(glob.glob(pattern)):
        with open(p) as fh:
            for r in csv.DictReader(fh):
                r["_src"] = os.path.relpath(p)
                out.append(r)
    return out


def f(x):
    return None if x in (None, "", "nan") else float(x)


def agg(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None, None, 0
    return (st.mean(vals), st.stdev(vals) if len(vals) > 1 else 0.0, len(vals))


def write(path, fieldnames, rows):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", default="results/round3/A1_coverage")
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args(argv)
    D = args.in_dir

    by_task = read_rows(f"{D}/a1_by_task__*__main.csv") + \
              read_rows(f"{D}/a1_by_task__*__slideout.csv")
    cal = read_rows(f"{D}/a1_calibration_units__*__main.csv") + \
          read_rows(f"{D}/a1_calibration_units__*__slideout.csv")
    if not by_task:
        raise SystemExit(f"no per-task tables found under {D}")

    encoders = sorted({r["encoder"] for r in by_task})
    tasks = sorted({(r["task"], r["label_set"]) for r in by_task})

    # ---- design x score, over every task-encoder cell -------------------------
    rows = []
    for d in DESIGNS:
        for s in SCORES:
            sel = [r for r in by_task if r["design"] == d and r["score"] == s]
            if not sel:
                continue
            cm, csd, n = agg([f(r["coverage_mean"]) for r in sel])
            wm, wsd, _ = agg([f(r["width_mean"]) for r in sel])
            im, _, _ = agg([f(r["interval_score_mean"]) for r in sel])
            ma, _, _ = agg([f(r["miss_above_mean"]) for r in sel])
            mb, _, _ = agg([f(r["miss_below_mean"]) for r in sel])
            rows.append(dict(
                design=d, score=s, n_cells=n,
                n_encoders=len({r["encoder"] for r in sel}),
                n_tasks=len({(r["task"], r["label_set"]) for r in sel}),
                coverage_mean=cm, coverage_sd_across_cells=csd,
                shortfall_from_nominal=None if cm is None else 0.90 - cm,
                width_mean=wm, width_sd_across_cells=wsd,
                interval_score_mean=im,
                miss_above_mean=ma, miss_below_mean=mb,
                miss_asymmetry=None if (ma is None or mb is None or ma + mb == 0)
                else (ma - mb) / (ma + mb),
                calibration_units=";".join(sorted({r["calibration_unit"] for r in sel})),
            ))
    write(f"{D}/a1_coverage_by_design.csv", list(rows[0].keys()), rows)

    # ---- task x design x score ------------------------------------------------
    trows = []
    for (t, ls) in tasks:
        for d in DESIGNS:
            for s in SCORES:
                sel = [r for r in by_task
                       if r["task"] == t and r["label_set"] == ls
                       and r["design"] == d and r["score"] == s]
                if not sel:
                    continue
                cm, csd, n = agg([f(r["coverage_mean"]) for r in sel])
                wm, _, _ = agg([f(r["width_mean"]) for r in sel])
                nf = sorted({int(r["n_folds"]) for r in sel})
                trows.append(dict(
                    task=t, label_set=ls, design=d, score=s,
                    n_encoders=n, n_folds=";".join(str(x) for x in nf),
                    coverage_mean=cm, coverage_sd_across_encoders=csd,
                    shortfall_from_nominal=None if cm is None else 0.90 - cm,
                    width_mean=wm,
                    calibration_units=";".join(sorted({r["calibration_unit"] for r in sel})),
                    n_train_matched=";".join(sorted({r["n_train_matched"] for r in sel})),
                ))
    write(f"{D}/a1_coverage_by_task_design.csv", list(trows[0].keys()), trows)

    # ---- encoder x design x score --------------------------------------------
    erows = []
    for e in encoders:
        for d in DESIGNS:
            for s in SCORES:
                sel = [r for r in by_task
                       if r["encoder"] == e and r["design"] == d and r["score"] == s]
                if not sel:
                    continue
                cm, csd, n = agg([f(r["coverage_mean"]) for r in sel])
                wm, _, _ = agg([f(r["width_mean"]) for r in sel])
                erows.append(dict(
                    encoder=e, design=d, score=s, n_tasks=n,
                    coverage_mean=cm, coverage_sd_across_tasks=csd,
                    shortfall_from_nominal=None if cm is None else 0.90 - cm,
                    width_mean=wm))
    write(f"{D}/a1_coverage_by_encoder.csv", list(erows[0].keys()), erows)

    # ---- calibration-unit structure ------------------------------------------
    crows = []
    if cal:
        key = defaultdict(list)
        for r in cal:
            key[(r["task"], r["label_set"], r["design"])].append(r)
        for (t, ls, d), sel in sorted(key.items()):
            units = defaultdict(int)
            for r in sel:
                units[r["calibration_unit"]] += 1
            shares_donor = sum(1 for r in sel
                               if str(r.get("cal_shares_donor_with_test")).lower() == "true")
            shares_sess = sum(1 for r in sel
                              if str(r.get("cal_shares_exact_session_with_test")).lower() == "true")
            bad = sorted({r.get("cal_status", "") for r in sel} - {"ok", ""})
            crows.append(dict(
                task=t, label_set=ls, design=d,
                n_fold_draw_rows=len(sel),
                unit_counts=";".join(f"{k}={v}" for k, v in sorted(units.items())),
                n_cal_units_min=min(int(r["n_cal_units"]) for r in sel),
                n_cal_units_max=max(int(r["n_cal_units"]) for r in sel),
                n_cal_spots_median=int(st.median(int(r["n_cal_spots"]) for r in sel)),
                rows_cal_shares_donor_with_test=shares_donor,
                rows_cal_shares_exact_session_with_test=shares_sess,
                non_ok_cal_status=";".join(bad) if bad else "",
            ))
        write(f"{D}/a1_calibration_unit_table.csv", list(crows[0].keys()), crows)

    # ---- coverage beside the benchmark's own Pearson --------------------------
    enc_pearson = {}
    p = os.path.join(args.repo_root, "results/summary/results_encoder.csv")
    if os.path.exists(p):
        with open(p) as fh:
            for r in csv.DictReader(fh):
                if r["head"] == "pca_ridge":
                    enc_pearson[r["encoder"]] = f(r["avg_paper9"])
    brows = []
    for e in encoders:
        row = dict(encoder=e, benchmark_pca_ridge_avg_paper9=enc_pearson.get(e))
        for d in DESIGNS:
            sel = [r for r in by_task if r["encoder"] == e and r["design"] == d
                   and r["score"] == "abs"]
            cm, _, _ = agg([f(r["coverage_mean"]) for r in sel])
            row[f"coverage_{d}_abs"] = cm
        brows.append(row)
    write(f"{D}/a1_vs_benchmark_pearson.csv", list(brows[0].keys()), brows)

    # ---- the aggregation note: pooled versus slide-mean on random ------------
    # H2 measured POOLED coverage (one fraction over all test points). The tables
    # above follow the project's metric convention instead: per slide, then mean
    # over slides, then over genes, then over folds. On tasks with many small
    # slides the two differ, and the difference is an aggregation property rather
    # than under-coverage. Both are reported so the report cannot conflate them.
    arows = []
    for pat, tag in ((f"{D}/../A0_smoke/h2_coverage__*__h2.csv", "A0_H2_pooled"),):
        for r in read_rows(pat):
            arows.append(dict(source=tag, task=r["task"], label_set=r["label_set"],
                              encoder=r["encoder"], design="random", score="abs",
                              coverage=f(r["coverage_pooled"]),
                              aggregation="pooled over all test points",
                              src=r["_src"]))
    for r in by_task:
        if r["design"] == "random" and r["score"] == "abs":
            arows.append(dict(source="A1_slide_mean", task=r["task"],
                              label_set=r["label_set"], encoder=r["encoder"],
                              design="random", score="abs",
                              coverage=f(r["coverage_mean"]),
                              aggregation="per slide, then genes, then folds",
                              src=r["_src"]))
    if arows:
        write(f"{D}/a1_aggregation_note.csv", list(arows[0].keys()), arows)

    # ---- coverage by calibration unit ---------------------------------------
    # This is the stage's headline grouping, so it gets its own file rather than
    # being recomputed in prose. random is excluded because its unit is always
    # the spot and it is the no-shift control.
    urows = []
    g = defaultdict(list)
    for r in by_task:
        if r["score"] != "abs" or r["design"] == "random":
            continue
        g[r["calibration_unit"]].append(r)
    for u, sel in sorted(g.items(), key=lambda kv: -st.mean([f(r["coverage_mean"]) for r in kv[1]])):
        cm, csd, n = agg([f(r["coverage_mean"]) for r in sel])
        wm, _, _ = agg([f(r["width_mean"]) for r in sel])
        urows.append(dict(
            calibration_unit=u, n_cells=n, coverage_mean=cm, coverage_sd=csd,
            shortfall_from_nominal=0.90 - cm, width_mean=wm,
            designs=";".join(sorted({r["design"] for r in sel})),
            tasks=";".join(sorted({r["task"] for r in sel}))))
    write(f"{D}/a1_coverage_by_calibration_unit.csv", list(urows[0].keys()), urows)

    # ---- does encoder quality predict coverage under shift? -----------------
    def pearson(xs, ys):
        n = len(xs)
        mx, my = st.mean(xs), st.mean(ys)
        num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
        den = (sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys)) ** 0.5
        return num / den if den else None
    qrows = []
    for d in DESIGNS:
        pts = []
        for e in encoders:
            if enc_pearson.get(e) is None:
                continue
            sel = [r for r in by_task if r["encoder"] == e and r["design"] == d
                   and r["score"] == "abs"]
            if sel:
                pts.append((enc_pearson[e], st.mean([f(r["coverage_mean"]) for r in sel])))
        if len(pts) > 2:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            qrows.append(dict(
                design=d, n_encoders=len(pts),
                corr_benchmark_pearson_vs_coverage=pearson(xs, ys),
                benchmark_pearson_min=min(xs), benchmark_pearson_max=max(xs),
                coverage_min=min(ys), coverage_max=max(ys),
                coverage_range=max(ys) - min(ys)))
    write(f"{D}/a1_encoder_quality_correlation.csv", list(qrows[0].keys()), qrows)

    # ---- slide_out: does the calibration slide share the test donor? --------
    # The flag lives per (fold, repeat, cal draw) in the calibration table while
    # coverage lives per fold, so a fold is usable only where the flag is constant
    # across its draws. Folds where it varies are counted and excluded, not merged.
    srows = []
    so_cal = [r for r in cal if r["design"] == "slide_out"]
    if so_cal:
        byfold = defaultdict(set)
        for r in so_cal:
            byfold[(r["encoder"], r["task"], r["label_set"], r["fold"])].add(
                str(r.get("cal_shares_donor_with_test")).lower())
        const = {k: list(v)[0] for k, v in byfold.items() if len(v) == 1}
        n_varied = len(byfold) - len(const)
        fold_rows = read_rows(f"{D}/a1_by_fold__*__slideout.csv")
        buckets = defaultdict(lambda: defaultdict(list))
        for r in fold_rows:
            if r.get("score") != "abs":
                continue
            k = (r["encoder"], r["task"], r["label_set"], r["fold"])
            if k in const:
                buckets[r["task"]][const[k]].append(f(r["coverage"]))
                buckets["ALL"][const[k]].append(f(r["coverage"]))
        for t in sorted(buckets):
            for flag in ("true", "false"):
                v = buckets[t].get(flag, [])
                if not v:
                    continue
                srows.append(dict(
                    scope=t, cal_shares_donor_with_test=flag, n_folds=len(v),
                    coverage_mean=st.mean(v),
                    coverage_sd=st.stdev(v) if len(v) > 1 else 0.0,
                    n_folds_flag_varied_across_draws_excluded=n_varied if t == "ALL" else ""))
        write(f"{D}/a1_slideout_donor_sharing.csv", list(srows[0].keys()), srows)

    print(json.dumps(dict(
        encoders=len(encoders), tasks=len(tasks),
        by_task_rows=len(by_task), cal_rows=len(cal),
        wrote=["a1_coverage_by_design.csv", "a1_coverage_by_task_design.csv",
               "a1_coverage_by_encoder.csv", "a1_calibration_unit_table.csv",
               "a1_vs_benchmark_pearson.csv", "a1_aggregation_note.csv"]), indent=2))


if __name__ == "__main__":
    main()
