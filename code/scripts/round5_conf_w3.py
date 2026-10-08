#!/usr/bin/env python
"""Round 5, prediction-set track, W3: real data above 10 calibration donors.

docs/round5_conf_plan.md section 2 (W3) and section 6.5 (the W2 decision memo's changes). This
script imports round4_conf_c3.py unmodified and adds one method, `within_full`. Nothing in this
file is a result.

PARTS
  1  The fine grid at K = 10 calibration donors. o in {3, 5, 9, 10, 12, 15, 17, 20, 25, 50, 100}
     with ghcp, ghcp_noad, within, within_plain, within_full and recentred, and pooled, hcp and
     one_per at o = 0. Tasks CCRCC:24, CCRCC:23_merged, INDIANA_KIDNEY, LUNG_XENIUM.
  2  The sweep over K with labelled units. K in {10, 12, 14, 16, 18, 20} on both kidney cancer
     sets and {10, 14, 18, 20} on Indiana, o in {0, 5, 10, 15, 17, 25, 50}, the methods of part 1.
     The training-donor count n_T_donors falls as K rises and is on every row; comparisons between
     methods are within a K.
  3  The sweep in which only K changes (CCRCC:24 and Indiana). For each fold and calibration draw
     the base head is the K = 20 design's (fitted once on that design's training donors) and the
     calibration set is the calibration donors of the K design of part 2 for the same fold and
     draw. Those are the first K donors of the same seeded permutation that gives the K = 20
     design its 20 (round 3 harness choose_calibration for CCRCC, round4_conf_c3._a4b_like_specs
     for Indiana), so the sets are nested and the job asserts it. n_T_donors is the K = 20 design's
     at every K.

The labelled spots at each o are the first o of round 4's label stream (round4_conf_c3.label_stream),
so every round-4 row at the same (task, encoder, K, fold, draw, o, method) is reproduced, and the
o values are nested within a label draw.

THE ADDED METHOD (assumption and guarantee, written before anything runs)
  within_full  Full conformal inside the test donor with the mean as the fitted model, per gene. For
               a candidate residual x, the fitted centre is c(x) = (S + x)/(o + 1), S the sum of the
               o labelled residuals; x is kept when #{i : |r_i - c(x)| >= |x - c(x)|} + 1 >
               alpha (o + 1), i.e. when at least m = floor(alpha (o + 1)) of the o labelled points
               satisfy the inequality. Each inequality holds on the closed interval between r_i and
               (2S - (o + 1) r_i)/(o - 1) (docs/round5_conf_plan.md section 4 item 5). The kept set
               is the set of points covered by at least m of these intervals. It is bounded once
               m >= 1, that is from o = 9 at alpha 0.1 and from o = 4 at alpha 0.2. The reported
               interval is the convex hull [L, H] of the kept set, written as centre (L + H)/2 and
               half-width (H - L)/2 so that round4_conf_c3's metric chain applies unchanged. Where
               the kept set of a gene is not one interval, that gene's coverage is computed from the
               exact set and its width from the hull; the share of such genes is in column
               wf_frac_not_interval. Assumes the labelled spots and the evaluation spots are
               exchangeable within the donor (true by construction: the labelled spots are a uniform
               random subset of the donor's spots). Guarantee: coverage
               (o + 1 - floor(alpha (o + 1)))/(o + 1) = ceil((o + 1)(1 - alpha))/(o + 1) marginally,
               the same as within_plain's. The coverage per fold is the average over the donor's
               remaining spots for one label draw, so only the mean over draws is compared with it.
  The other methods are round4_conf_c3's, unchanged; their assumptions and guarantees are in its
  docstring.

RECORDS. Every output directory gets PROVENANCE.txt with the snapshot commit the job ran from (the
snapshot directory is named by the full commit hash), the CPU model, and the md5 of every executed
script. The full table carries `part` and `wf_frac_not_interval` beside round4_conf_c3's columns.

Usage
  python round5_conf_w3.py --task CCRCC:24 --part 1 --encoders uni_v2 --out DIR [--folds F1,F2]
  python round5_conf_w3.py --selftest --out DIR
"""
import argparse
import math
import os
import re
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_c3 as C  # noqa: E402
import round5_conf_io as IO5  # noqa: E402

MGUARD = 1e-9                       # as round5_conf_w1_sim.wf_m
P1_O = (3, 5, 9, 10, 12, 15, 17, 20, 25, 50, 100)
P2_O = (0, 5, 10, 15, 17, 25, 50)
C3_O_METHODS = ("ghcp", "ghcp_noad", "within", "within_plain", "recentred")
P2_K = {"CCRCC:24": (10, 12, 14, 16, 18, 20), "CCRCC:23_merged": (10, 12, 14, 16, 18, 20),
        "INDIANA_KIDNEY": (10, 14, 18, 20)}
P3_TASKS = ("CCRCC:24", "INDIANA_KIDNEY")
P3_HEAD_K = 20


# ================================================================== within_full, gene-vectorised
def wf_m(o, alpha):
    return int(math.floor(alpha * (o + 1) + MGUARD))


def wf_bounds(init):
    """End points (lo, hi), each (o, G), of the intervals on which labelled point i satisfies the
    full-conformal inequality."""
    o = init.shape[0]
    S = init.sum(axis=0)
    other = (2.0 * S[None, :] - (o + 1) * init) / (o - 1)
    return np.minimum(init, other), np.maximum(init, other)


def wf_hull(init, m):
    """Hull [L, H] (each (G,)) of {x : #{i : lo_i <= x <= hi_i} >= m}, and whether the set is one
    interval, per gene."""
    lo, hi = wf_bounds(init)
    o = lo.shape[0]
    los, his = np.sort(lo, axis=0), np.sort(hi, axis=0)
    k1 = np.arange(1, o + 1)[:, None]
    # count at x = lo_(k): k - #{hi < lo_(k)}   (count rises only at lo points)
    cnt_lo = k1 - (his[None, :, :] < los[:, None, :]).sum(axis=1)
    L = np.where(cnt_lo >= m, los, np.inf).min(axis=0)
    # count at x = hi_(k) (closed): #{lo <= hi_(k)} - (k - 1)
    nlo_le_hi = (los[None, :, :] <= his[:, None, :]).sum(axis=1)
    cnt_hi = nlo_le_hi - (k1 - 1)
    H = np.where(cnt_hi >= m, his, -np.inf).max(axis=0)
    # just right of hi_(k): #{lo <= hi_(k)} - k ; a drop below m strictly inside [L, H) splits it
    right = nlo_le_hi - k1
    gap = (right < m) & (his >= L[None, :]) & (his < H[None, :])
    return L, H, ~gap.any(axis=0), lo, hi


def wf_exact_count(lo, hi, t):
    """#{i : lo_i <= t <= hi_i} for targets t (n,) against one gene's lo, hi (o,)."""
    los, his = np.sort(lo), np.sort(hi)
    return np.searchsorted(los, t, side="right") - np.searchsorted(his, t, side="left")


def wf_metrics(R, keep, init, m, sl):
    """Round-3 metric chain for within_full, as round4_conf_c3.centred_metrics, with the exact set's
    coverage on genes whose kept set is not one interval. Returns (metrics, finite, frac_not_int)."""
    G = R.shape[1]
    o = init.shape[0]
    if o < 2 or m == 0:
        c, q = np.zeros(G), np.full(G, np.inf)
        return C.centred_metrics(R, keep, c, q, sl), False, 0.0
    L, H, is_int, lo, hi = wf_hull(init, m)
    c, q = (L + H) / 2.0, (H - L) / 2.0
    if is_int.all():
        return C.centred_metrics(R, keep, c, q, sl), bool(np.isfinite(q).all()), 0.0
    cov = np.abs(R - c) <= q
    for g in np.flatnonzero(~is_int):
        cov[:, g] = wf_exact_count(lo[:, g], hi[:, g], R[:, g]) >= m
    n_slide, cr = [], []
    for i in sl.idx:
        k = i[keep[i]]
        n_slide.append(len(k))
        cr.append(cov[k].mean(axis=0) if len(k) else np.full(G, np.nan))
    n_slide = np.array(n_slide)
    cr = np.stack(cr)
    fin = np.isfinite(q)
    w = np.where(fin, 2.0 * q, np.nan)
    wc = np.where((n_slide[:, None] > 0) & fin[None, :], w[None, :], np.nan)
    present = n_slide > 0
    out = C._summ(cr[present], n_slide[present], wc[present], 2.0 * q[fin])
    out["finite"] = bool(fin.all())
    return out, out["finite"], float((~is_int).mean())


def wf_rows(fit, o_grid, label_draws=range(C.N_LABEL_DRAWS), alphas=C.ALPHAS, min_eval=10):
    rows = []
    base = fit.base_row()
    sl = fit.slides
    R = fit.R_E
    for ld in label_draws:
        perm = C.label_stream(fit, ld)
        for o in o_grid:
            if o == 0 or fit.n_E - o < min_eval:
                continue
            lab_idx = perm[:o]
            keep = np.ones(fit.n_E, bool)
            keep[lab_idx] = False
            init = R[lab_idx]
            for a in alphas:
                m = wf_m(o, a)
                met, fin, fni = wf_metrics(R, keep, init, m, sl)
                r = C._row(base, "within_full", a, o, ld, met, fin, o, int(keep.sum()))
                r["wf_frac_not_interval"] = fni
                rows.append(r)
    return rows


def selftest(n=300, seed="W3wfselftest"):
    """wf_hull against brute force (a fine grid of candidates) and against W1's interval sweep."""
    out = []
    worst, n_mis, n_pts, n_nonint = 0.0, 0, 0, 0
    for t in range(n):
        rng = np.random.default_rng(C.crc(f"{seed}|{t}"))
        o = int(rng.choice([4, 5, 9, 10, 12, 17, 25, 50, 100]))
        G = 7
        init = (rng.standard_t(3, (o, G)) * rng.choice([0.3, 1, 3], G)[None, :]
                + rng.normal(0, 2, G)[None, :])
        for a in C.ALPHAS:
            m = wf_m(o, a)
            if m == 0:
                continue
            L, H, is_int, lo, hi = wf_hull(init, m)
            for g in range(G):
                span = H[g] - L[g]
                grid = np.linspace(L[g] - 0.5 * span - 1, H[g] + 0.5 * span + 1, 6001)
                S = init[:, g].sum()
                cc = (S + grid) / (o + 1)
                cnt = (np.abs(init[:, g][None, :] - cc[:, None]) >= np.abs(grid - cc)[:, None]).sum(1)
                kept = grid[cnt >= m]
                ends = np.concatenate([lo[:, g], hi[:, g]])
                near = np.min(np.abs(grid[:, None] - ends[None, :]), 1) < 1e-7
                cnt_int = wf_exact_count(lo[:, g], hi[:, g], grid)
                n_mis += int(((cnt != cnt_int) & ~near).sum())
                n_pts += int((~near).sum())
                step = grid[1] - grid[0]
                worst = max(worst, abs(kept.min() - L[g]) - step, abs(kept.max() - H[g]) - step, 0.0)
                inside = (grid >= L[g]) & (grid <= H[g]) & ~near
                n_nonint += int(bool(is_int[g]) and bool((cnt[inside] < m).any()))
    out.append(dict(check="count_vs_brute_force_mismatches", value=n_mis, tol=0, n=n_pts))
    out.append(dict(check="hull_end_vs_grid_beyond_one_step", value=worst, tol=1e-9, n=n))
    out.append(dict(check="flagged_interval_but_gap_on_grid", value=n_nonint, tol=0, n=n))
    try:
        import round5_conf_w1_sim as W1
        d = 0.0
        for t in range(100):
            rng = np.random.default_rng(C.crc(f"{seed}|w1|{t}"))
            o = int(rng.choice([9, 10, 12, 17, 25, 50]))
            r = rng.normal(0, 1, (o, 1)) + rng.normal()
            for a in C.ALPHAS:
                m = wf_m(o, a)
                lo1, hi1 = W1.wf_intervals(r[:, 0])
                comps = W1.wf_set(lo1, hi1, m)
                L, H, _, _, _ = wf_hull(r, m)
                d = max(d, abs(comps[0][0] - L[0]), abs(comps[-1][1] - H[0]))
        out.append(dict(check="hull_vs_round5_conf_w1_sim_wf_set", value=d, tol=1e-12, n=100))
    except Exception as e:     # recorded, not hidden
        out.append(dict(check=f"hull_vs_w1_not_run_{e.__class__.__name__}", value=np.nan, tol=np.nan, n=0))
    for r in out:
        r["passed"] = bool(r["value"] <= r["tol"]) if r["tol"] == r["tol"] else None
    return out


# ================================================================== part 3 support
def subset_fit(fit, donors, K):
    """A Fit with the same head and test donor, calibrating only on `donors`."""
    keep = np.isin(fit.lab_C.astype(str), sorted(map(str, donors)))
    kw = {k: v for k, v in fit.__dict__.items() if k not in ("groups", "_sl", "_ctx")}
    lab = fit.lab_C[keep]
    kw.update(S_C=fit.S_C[keep], R_C=fit.R_C[keep], lab_C=lab, n_C=int(keep.sum()),
              n_C_donors=len(set(lab.tolist())), cal_donors=sorted(set(lab.tolist())), K=int(K))
    return C.Fit(**kw)


def cal_donors_of(T, spec):
    return {T.meta["donor_of"][s] for s in np.unique(T.samp[spec["C"]])}


# ================================================================== driver
def cpu_model():
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    import platform
    return platform.processor() or "unknown"


def snapshot_commit():
    root = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return root if re.fullmatch(r"[0-9a-f]{40}", root) else f"not a snapshot ({root})"


def rows_for_fit(fit, o_grid, o0=True):
    rows = []
    if o0 and 0 in o_grid:
        rows += C.o0_rows(fit, alphas=C.ALPHAS, methods=C.O0_METHODS, dwr_reps=C.DWR_REPS)
    og = tuple(o for o in o_grid if o > 0)
    rows += C.o_rows(fit, o_grid=og, label_draws=range(C.N_LABEL_DRAWS), alphas=C.ALPHAS,
                     methods=C3_O_METHODS)
    rows += wf_rows(fit, og)
    return rows


def run(a):
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    rows, checks = [], []
    folds = a.folds.split(",") if a.folds else None
    for enc in a.encoders.split(","):
        T = C.load_task(a.task, enc)
        fsel = folds or T.fold_names()
        if a.part == 1:
            specs = T.specs(10, n_cal_draws=C.N_CAL_DRAWS, folds=fsel)
            o_grid = (0,) + P1_O
            for i, sp in enumerate(specs):
                fit = T.fit(sp)
                if i == 0 and enc == a.encoders.split(",")[0]:
                    for r in C.selftest(fit):
                        checks.append(dict(check="c3_selftest:" + r["check"], value=r["max_abs_diff"],
                                           tol=1e-12, passed=bool(r["max_abs_diff"] <= 1e-12)))
                for r in rows_for_fit(fit, o_grid):
                    r["part"] = 1
                    rows.append(r)
                print(f"[w3] {a.task} p1 {enc} {i + 1}/{len(specs)} {time.time() - t0:.0f}s", flush=True)
        elif a.part == 2:
            for K in (a.K or P2_K[a.task]):
                specs = T.specs(K, n_cal_draws=C.N_CAL_DRAWS, folds=fsel)
                for i, sp in enumerate(specs):
                    fit = T.fit(sp)
                    for r in rows_for_fit(fit, P2_O):
                        r["part"] = 2
                        rows.append(r)
                    print(f"[w3] {a.task} p2 {enc} K{K} {i + 1}/{len(specs)} {time.time() - t0:.0f}s",
                          flush=True)
        else:
            assert a.task in P3_TASKS
            Ks = a.K or P2_K[a.task]
            head_specs = T.specs(P3_HEAD_K, n_cal_draws=C.N_CAL_DRAWS, folds=fsel)
            by_k = {K: {(s["fold"], s["cal_draw"]): s for s in
                        T.specs(K, n_cal_draws=C.N_CAL_DRAWS, folds=fsel)} for K in Ks}
            for i, sp in enumerate(head_specs):
                fit20 = T.fit(sp)
                d20 = cal_donors_of(T, sp)
                prev = set()
                for K in sorted(Ks):
                    sK = by_k[K].get((sp["fold"], sp["cal_draw"]))
                    if sK is None:
                        checks.append(dict(check=f"p3_missing_spec:{sp['fold']}:{sp['cal_draw']}:K{K}",
                                           value=1, tol=0, passed=False))
                        continue
                    dK = cal_donors_of(T, sK)
                    nested = dK <= d20 and prev <= dK and len(dK) == K
                    checks.append(dict(check=f"p3_nested:{enc}:{sp['fold']}:{sp['cal_draw']}:K{K}",
                                       value=int(not nested), tol=0, passed=bool(nested)))
                    assert nested, (sp["fold"], sp["cal_draw"], K)
                    prev = dK
                    fit = fit20 if K == P3_HEAD_K else subset_fit(fit20, dK, K)
                    for r in rows_for_fit(fit, P2_O):
                        r["part"] = 3
                        rows.append(r)
                print(f"[w3] {a.task} p3 {enc} {i + 1}/{len(head_specs)} {time.time() - t0:.0f}s",
                      flush=True)
    full = pd.DataFrame(rows)
    if "wf_frac_not_interval" not in full:
        full["wf_frac_not_interval"] = np.nan
    cols = C.FIXED_COLS + C.EXTRA_COLS + ["part", "wf_frac_not_interval"]
    tag = f"{C.TASKS[a.task]['out_task']}_p{a.part}_{a.encoders.replace(',', '-')}"
    if a.folds:
        tag += "_f" + a.folds.replace(",", "-")
    full[cols].to_csv(os.path.join(a.out, f"w3_full__{tag}.csv.gz"), index=False)
    pd.DataFrame(checks).to_csv(os.path.join(a.out, f"w3_checks__{tag}.csv"), index=False)
    cfg = dict(task=a.task, part=a.part, encoders=a.encoders, folds=a.folds, K=a.K,
               o_grid=P1_O if a.part == 1 else P2_O, methods=list(C.O0_METHODS) +
               list(C3_O_METHODS) + ["within_full"], label_draws=C.N_LABEL_DRAWS,
               cal_draws=C.N_CAL_DRAWS, alphas=list(C.ALPHAS))
    IO5.write_provenance(a.out, f"W3_p{a.part}", __file__, cfg,
                         extra=dict(snapshot_commit=snapshot_commit(), cpu_model=cpu_model(),
                                    rows=len(full), wall_seconds=int(time.time() - t0)))
    print(f"[w3] done {len(full)} rows {time.time() - t0:.0f}s", flush=True)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--task", choices=list(C.TASKS))
    p.add_argument("--part", type=int, choices=[1, 2, 3])
    p.add_argument("--encoders", default=",".join(C.ENCODERS))
    p.add_argument("--folds", default=None)
    p.add_argument("--K", type=int, nargs="*", default=None)
    p.add_argument("--out", required=True)
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args(argv)
    if a.selftest:
        os.makedirs(a.out, exist_ok=True)
        r = pd.DataFrame(selftest())
        r.to_csv(os.path.join(a.out, "w3_selftest.csv"), index=False)
        print(r.to_string())
        IO5.write_provenance(a.out, "W3_selftest", __file__, dict(selftest=True),
                             extra=dict(snapshot_commit=snapshot_commit(), cpu_model=cpu_model()))
        sys.exit(0 if r.passed.dropna().all() else 3)
    run(a)


if __name__ == "__main__":
    main()
