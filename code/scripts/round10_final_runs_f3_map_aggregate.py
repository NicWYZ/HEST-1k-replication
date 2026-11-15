#!/usr/bin/env python
"""Round 10, track final-runs, F3.1: the map's tables, bootstrap standard errors of width margins and the P10.3
score (plan section 5d.1 items 6 and 8 and the P10.3 rule, fixed before the run). Nothing here is a result.

Inputs are the per-draw full tables of the map units (map_full__*.csv.gz). Definitions.
  fold value     the mean over a fold's (calibration draw, label draw) rows of width_median (or coverage).
  median width   the median over folds (target donors) of the fold value (P10.3's definition).
  bootstrap      within each fold, B = 1000 resamples of the (calibration draw, label draw) pairs with
                 replacement, the same resample for both methods. A method at o = 0 has one row per calibration
                 draw; its value for a pair is that calibration draw's row. The statistic (difference or ratio of
                 the two methods' median widths) is recomputed on each resample; its SE is the SD over resamples.
                 Seed crc32("f3map|boot|<task>|<encoder>|<scale>|<K>|<alpha>|<o>|<method A>|<method B>").
P10.3 (fixed rule). Round 5's map is at alpha 0.1 and K = 10, uni_v2, log1p. Part one holds on a task if within_full's
median width is below hcp's (o = 0) at o = 9 and at every larger o of part 1; scored on CCRCC and LUNG_XENIUM. Part two
holds if on INDIANA_KIDNEY within_full's median width is within 2% of within_plain's at o in {9, 10, 12, 15}. A
margin within two standard errors of its threshold is scored as partly held.

usage: round10_final_runs_f3_map_aggregate.py <out_dir> <map_full csv.gz> [...]
"""
import json
import os
import sys
import zlib

import numpy as np
import pandas as pd

B = 1000
P1_LARGE_O = (9, 10, 12, 15, 17, 20, 25, 50, 100)
P2_O = (9, 10, 12, 15)


def _pairs(d):
    """Per fold: an array (n_pairs, 2) of (cal_draw, label_draw)."""
    return {f: g[["cal_draw", "label_draw"]].drop_duplicates().sort_values(["cal_draw", "label_draw"]).to_numpy()
            for f, g in d.groupby("fold")}


def _lookup(d, col):
    o0 = (d["o"] == 0).all()
    if o0:
        return o0, {(r.fold, int(r.cal_draw)): getattr(r, col) for r in d.itertuples()}
    return o0, {(r.fold, int(r.cal_draw), int(r.label_draw)): getattr(r, col) for r in d.itertuples()}


def boot_margin(dA, dB, stat="diff", col="width_median", n_boot=B, seed_tag="f3map|boot"):
    """Point value and bootstrap SE of stat(median_fold(mean A), median_fold(mean B)); A minus B or A over B."""
    folds = sorted(set(dA.fold) & set(dB.fold))
    ref = dB if not (dB["o"] == 0).all() else dA
    pairs = _pairs(ref[ref.fold.isin(folds)])
    oA, LA = _lookup(dA, col)
    oB, LB = _lookup(dB, col)

    def vals(L, o0, f, P):
        return np.array([L[(f, int(c))] if o0 else L[(f, int(c), int(l))] for c, l in P], float)
    VA = {f: vals(LA, oA, f, pairs[f]) for f in folds}
    VB = {f: vals(LB, oB, f, pairs[f]) for f in folds}

    def st(a, b):
        ma, mb = np.median(a), np.median(b)
        return (ma - mb) if stat == "diff" else (ma / mb if mb != 0 else np.nan)
    point_a = np.array([np.nanmean(VA[f]) for f in folds])
    point_b = np.array([np.nanmean(VB[f]) for f in folds])
    point = st(point_a, point_b)
    rng = np.random.default_rng(zlib.crc32(seed_tag.encode()))
    bs = np.empty(n_boot)
    for b in range(n_boot):
        ma, mb = [], []
        for f in folds:
            n = len(pairs[f])
            ix = rng.integers(0, n, n)
            ma.append(np.nanmean(VA[f][ix]))
            mb.append(np.nanmean(VB[f][ix]))
        bs[b] = st(np.array(ma), np.array(mb))
    return dict(point=float(point), se=float(np.nanstd(bs, ddof=1)), med_A=float(np.median(point_a)),
                med_B=float(np.median(point_b)), n_folds=len(folds))


def by_task(full):
    keys = ["task", "encoder", "scale", "part", "method", "alpha", "o", "K"]
    fold = full.groupby(keys + ["fold"]).agg(coverage=("coverage", "mean"), width_mean=("width_mean", "mean"),
                                             width_median=("width_median", "mean"),
                                             finite=("finite", "mean")).reset_index()
    return fold.groupby(keys).agg(n_folds=("fold", "nunique"), coverage_mean=("coverage", "mean"),
                                  coverage_min=("coverage", "min"), width_median_median=("width_median", "median"),
                                  width_mean_mean=("width_mean", "mean"), finite_mean=("finite", "mean")).reset_index()


def _cell(full, task, enc, scale, K, alpha, method, o):
    d = full[(full.task == task) & (full.encoder == enc) & (full.scale == scale) & (full.K == K) &
             (np.isclose(full.alpha, alpha)) & (full.method == method) & (full.o == o)]
    return d[["fold", "cal_draw", "label_draw", "o", "width_median", "coverage"]]


def verdict(margin, se, threshold, better):
    """better(margin) True when the prediction's side holds; partly when within 2 SE of the threshold."""
    if not np.isfinite(margin):
        return "not tested"
    if abs(margin - threshold) <= 2 * se:
        return "partly held"
    return "held" if better(margin) else "refuted"


def p103(full, enc="uni_v2", scale="log1p"):
    rows = []
    for task in ("CCRCC", "LUNG_XENIUM"):
        hcp = _cell(full, task, enc, scale, 10, 0.1, "hcp", 0)
        for o in P1_LARGE_O:
            wf = _cell(full, task, enc, scale, 10, 0.1, "within_full", o)
            if not len(hcp) or not len(wf):
                rows.append(dict(part=1, task=task, o=o, verdict="not tested"))
                continue
            tag = f"f3map|boot|{task}|{enc}|{scale}|10|0.1|{o}|hcp|within_full"
            r = boot_margin(hcp, wf, "diff", seed_tag=tag)
            rows.append(dict(part=1, task=task, o=o, method_A="hcp", method_B="within_full", stat="hcp - within_full",
                             median_A=r["med_A"], median_B=r["med_B"], margin=r["point"], se=r["se"],
                             n_folds=r["n_folds"], threshold=0.0,
                             verdict=verdict(r["point"], r["se"], 0.0, lambda m: m > 0)))
    task = "INDIANA_KIDNEY"
    for o in P2_O:
        wf = _cell(full, task, enc, scale, 10, 0.1, "within_full", o)
        wp = _cell(full, task, enc, scale, 10, 0.1, "within_plain", o)
        if not len(wf) or not len(wp):
            rows.append(dict(part=2, task=task, o=o, verdict="not tested"))
            continue
        tag = f"f3map|boot|{task}|{enc}|{scale}|10|0.1|{o}|within_full|within_plain"
        r = boot_margin(wf, wp, "ratio", seed_tag=tag)
        dev = abs(r["point"] - 1.0)
        v = "not tested" if not np.isfinite(dev) else (
            "partly held" if abs(dev - 0.02) <= 2 * r["se"] else ("held" if dev < 0.02 else "refuted"))
        rows.append(dict(part=2, task=task, o=o, method_A="within_full", method_B="within_plain",
                         stat="within_full / within_plain", median_A=r["med_A"], median_B=r["med_B"],
                         margin=r["point"], se=r["se"], n_folds=r["n_folds"], threshold=0.02, verdict=v))
    return pd.DataFrame(rows)


def overall(p):
    out = {}
    for (part, task), g in p.groupby(["part", "task"]):
        vs = set(g["verdict"])
        out[f"part{part}_{task}"] = ("not tested" if "not tested" in vs else "refuted" if "refuted" in vs
                                     else "partly held" if "partly held" in vs else "held")
    return out


def main(out_dir, paths):
    os.makedirs(out_dir, exist_ok=True)
    full = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
    bt = by_task(full)
    p = p103(full)
    p.to_csv(os.path.join(out_dir, "map_p103.csv"), index=False)
    json.dump(overall(p), open(os.path.join(out_dir, "map_p103_overall.json"), "w"), indent=1)
    bt.to_csv(os.path.join(out_dir, "map_by_task.csv"), index=False)
    print(p.to_string(), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
