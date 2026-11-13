#!/usr/bin/env python
"""Round 10, track final-runs, F3.4 (plan section 5d.4 items 2 to 5): E8, the joint design. Nothing here is a result.

Joins regime B's fixed-coefficient width ratio to the prediction-set map at o = m, per (task, encoder, scale,
estimand, m) and per (part, K) of the map, on CCRCC (24 donors), INDIANA_KIDNEY, LUNG_XENIUM, kidney__Visium and
ACS by state. It only joins and summarises outputs other jobs wrote; it reads no prediction file.

Inputs
  regime B   <regb_root>/regB_e8__*/regimeB_wr.csv (form C_fix1: median_wr = median over genes of the C_fix1 width
             over the C_classical width, boot_se = the unit's own bootstrap over draws, boot_B = 200) and
             regimeB_cells.csv (coverage_median of estimator C_fix1, interval regB_t). Joined as written.
  map        the map_full__*.csv.gz shards listed in <map_inputs> (F3/map/map_aggregate/inputs.txt), filtered to
             alpha 0.1, K with 1/(K + 1) <= 0.1 (K >= 9), o in {0} and the m grid, and the methods of round 5's
             VALID. CCRCC_23merged has no regime B rows and is not read.
  ACS        <acs> (F3/map/acs_prod/acs_o_sweep.csv), folds with k_meets_alpha01 (folds 0 to 3, K 9, 10, 10, 10)
             pooled as one K group (internal K = 9, K_desc names the folds' K); cal_draw = 0, label_draw = draw.
Name maps   map scale norm = regime B norm_refit (HEST tasks) and lognorm (kidney__Visium); ACS encoder package =
             pkg, scale log_income.

Rules
  overall    round 5's narrowest_valid, by import: round5_conf_w3_merge.by_fold and .map_by_task (lines 194 to
             235) are called per (task, encoder, scale), so their mean over encoders is over one encoder. The valid
             methods are round 5's VALID (hcp, ghcp, ghcp_noad, within, within_plain, within_full; one_per is
             excluded by the rule and is not on the map's grid). For ACS, whose o grid differs from W3's,
             round5_conf_w3_merge.GRID is set to {1: K {9}, o = the ACS o grid} for that one call, so hcp at o = 0
             is repeated at every o as W3 does, and restored afterwards (a module-level change, recorded here).
  no-extra   the same selection (round5_conf_w3_merge.py lines 227 to 231, transcribed) restricted to the sets that
             use only the target donor's o = m spots: within, within_plain, within_full.
  round 4    the fixed rule (round4_ppi_q5_joint.py lines 45 to 46): hcp at o = 0, ghcp for 0 < o < 9,
             within_plain for 9 <= o < 25, within from o = 25; reported beside with its width and finiteness.
Widths      width_median_* is P10.3's median width: the median over folds (target donors) of the fold mean over
             (calibration draw, label draw) of width_median. width_mean_* is round 5's selection metric.
Difference  diff = no-extra minus overall median width, with SE from boot_margin imported unchanged from
             round10_final_runs_f3_map_aggregate.py: within each fold B = 1000 resamples of the (cal_draw,
             label_draw) pairs, the same resample for both sets; hcp (o = 0) looked up by calibration draw. Seed
             zlib.crc32("f3e8|boot|<task>|<encoder>|<scale>|<part>|<K>|0.1|<o>|<no-extra>|<overall>").
Extra labels  sets in {hcp, ghcp, ghcp_noad} need K labelled calibration donors: n_C_median is the median of the
             map's n_C over the set's rows, and extra_labels_beyond_regB = max(n_C_median - n_C_donors * m, 0),
             since regime B already labels m spots of every donor.
Cells        a (part, K) at which m is not on the part's o grid is written with reason off_grid and not
             interpolated. A cell with no valid set, or no no-extra set finite in every row, is written with a
             reason. Each guarantee is marginal; joint coverage of the interval and a set built from the same labels
             is not claimed (Dobriban and Lin, arXiv:2303.00203, need multiplicity control for it).

usage: round10_final_runs_f3_e8_joint.py <out_dir> --regb-root DIR --map-inputs FILE --acs FILE
                                          --map-by-task FILE [--workers N]
"""
import argparse
import glob
import json
import os
import sys
import zlib
from multiprocessing import Pool

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round5_conf_w3_merge as R5M  # noqa: E402
from round10_final_runs_f3_map_aggregate import boot_margin, B as BOOT_B  # noqa: E402

ALPHA = 0.1
NOEXTRA = ("within", "within_plain", "within_full")
EXTRA = ("hcp", "ghcp", "ghcp_noad")
GUARANTEE = ("marginal for each method; joint coverage of the regime B interval and the set built from the same "
             "labels is not claimed (Dobriban and Lin, arXiv:2303.00203)")
TASKS = {"CCRCC": "CCRCC_24", "INDIANA_KIDNEY": "INDIANA_KIDNEY", "LUNG_XENIUM": "LUNG_XENIUM",
         "kidney__Visium": "kidney__Visium"}
USECOLS = ["task", "label_set", "encoder", "method", "score", "alpha", "o", "K", "fold", "draw", "coverage",
           "width_mean", "width_median", "n_test", "finite", "n_T_donors", "cal_draw", "label_draw", "n_C",
           "n_C_donors", "part", "scale"]
DKEY = ["part", "scale", "label_set", "method", "score", "o", "K", "fold", "cal_draw", "label_draw"]


def round4_rule(o):
    """round4_ppi_q5_joint.py lines 45 to 46."""
    return "hcp" if o == 0 else "ghcp" if o < 9 else "within_plain" if o < 25 else "within"


def load_regb(root):
    units = sorted(glob.glob(os.path.join(root, "regB_e8__*")))
    units = [u for u in units if os.path.isdir(u) and not u.endswith("_smoke")]
    wr, ce = [], []
    for u in units:
        w = pd.read_csv(os.path.join(u, "regimeB_wr.csv"))
        wr.append(w[w.form == "C_fix1"])
        c = pd.read_csv(os.path.join(u, "regimeB_cells.csv"))
        c = c[(c.estimator == "C_fix1") & (c.interval == "regB_t")]
        if "population" in c:
            c = c[(c.population == "donor") & (c.target == "design")]
        ce.append(c)
    W = pd.concat(wr, ignore_index=True)
    C = pd.concat(ce, ignore_index=True)
    k = ["task", "encoder", "scale", "estimand", "m"]
    C = C[k + ["coverage_median", "G"]]
    out = W.merge(C, on=k, how="left", validate="one_to_one")
    out = out.rename(columns=dict(median_wr="regB_wr_fix1", boot_se="regB_wr_se", boot_B="regB_boot_B", R="regB_R",
                                  genes="regB_genes", coverage_median="regB_cov_fix1", G="regB_G",
                                  boot_q05="regB_wr_q05", boot_q95="regB_wr_q95"))
    return out.drop(columns=["form"]), [os.path.basename(u) for u in units], int(W.duplicated(k).sum())


def fold_median(d, col="width_median"):
    f = d.groupby("fold")[col].mean()
    return float(np.median(f.to_numpy())) if len(f) else np.nan


def pick(sub, methods=None):
    """round5_conf_w3_merge.py lines 227 to 231, optionally restricted to `methods`."""
    c = sub[sub.valid & (sub.method != "one_per") & (sub.finite == 1.0) & np.isfinite(sub.width_mean)]
    if methods is not None:
        c = c[c.method.isin(methods)]
    return c.loc[c.width_mean.idxmin()] if len(c) else None


def set_cells(D, task, enc, scale, m_grid, part_ogrid, k_desc=None):
    """All set cells of one (task, encoder, scale). D: per-draw rows (VALID methods)."""
    BF = R5M.by_fold(D)
    M = R5M.map_by_task(BF)
    rows = []
    for (part, K), _ in D.groupby(["part", "K"]):
        ogrid = part_ogrid[int(part)]
        for m in m_grid:
            base = dict(task=task, encoder=enc, set_scale=scale, part=int(part), K=int(K),
                        K_desc=k_desc or str(int(K)), m=int(m), o=int(m), on_o_grid=bool(m in ogrid),
                        n_folds=int(D[(D.part == part) & (D.K == K)].fold.nunique()))
            if m not in ogrid:
                base["reason"] = "off_grid"
                rows.append(base)
                continue
            sub = M[(M.part == part) & (M.K == K) & (M.o == m) & np.isclose(M.alpha, ALPHA)]
            ov, ne = pick(sub), pick(sub, NOEXTRA)
            reasons = []

            def rows_of(meth):
                oo = 0 if meth in R5M.O_FREE else m
                return D[(D.part == part) & (D.K == K) & (D.method == meth) & (D.o == oo)]

            for tag, r in (("noextra", ne), ("overall", ov)):
                if r is None:
                    reasons.append("no_valid_set" if tag == "overall" else "no_noextra_set_finite")
                    continue
                d = rows_of(r.method)
                base.update({f"{tag}_method": r.method, f"{tag}_width_median": fold_median(d),
                             f"{tag}_width_mean": float(r.width_mean), f"{tag}_coverage": float(r.coverage),
                             f"{tag}_n_rows": len(d)})
            if ov is not None:
                d = rows_of(ov.method)
                need = ov.method in EXTRA
                base["overall_needs_extra_labels"] = need
                if need:
                    nC = float(d.n_C.median()) if "n_C" in d and d.n_C.notna().any() else np.nan
                    nCd = float(d.n_C_donors.median()) if "n_C_donors" in d and d.n_C_donors.notna().any() else np.nan
                    base.update(overall_extra_K_donors=int(K), overall_n_C_median=nC, overall_n_C_donors_median=nCd,
                                overall_extra_labels_beyond_regB=(max(nC - nCd * m, 0.0)
                                                                  if np.isfinite(nC) and np.isfinite(nCd) else np.nan))
                else:
                    base.update(overall_extra_K_donors=0, overall_extra_labels_beyond_regB=0.0)
            if ov is not None and ne is not None:
                tag = f"f3e8|boot|{task}|{enc}|{scale}|{int(part)}|{int(K)}|{ALPHA}|{m}|{ne.method}|{ov.method}"
                bm = boot_margin(rows_of(ne.method), rows_of(ov.method), "diff", seed_tag=tag)
                base.update(diff_width_median=bm["point"], diff_se=bm["se"], diff_boot_B=BOOT_B,
                            diff_seed_tag=tag, diff_n_folds=bm["n_folds"])
            r4 = round4_rule(m)
            s4 = sub[sub.method == r4]
            base["r4_method"] = r4
            if len(s4):
                s4 = s4.iloc[0]
                base.update(r4_finite=float(s4.finite), r4_width_mean=float(s4.width_mean),
                            r4_coverage=float(s4.coverage),
                            r4_width_median=fold_median(rows_of(r4)) if s4.finite == 1.0 else np.inf)
            else:
                reasons.append("r4_method_absent")
            base["reason"] = ";".join(reasons)
            rows.append(base)
    return rows


def _read(path, oset):
    d = pd.read_csv(path, usecols=USECOLS, low_memory=False)
    return d[np.isclose(d.alpha, ALPHA) & (d.K >= 9) & d.o.isin(oset) & d.method.isin(R5M.VALID)]


def work_hest(args):
    task, enc, paths, m_grid = args
    oset = {0} | set(m_grid)
    D = pd.concat([_read(p, oset) for p in paths], ignore_index=True)
    D = D[D.task == task]
    ndup = int(D.duplicated(DKEY + ["alpha"]).sum())
    nconf = int(D.drop_duplicates().duplicated(DKEY + ["alpha"]).sum())
    D = D.drop_duplicates(DKEY + ["alpha"])
    part_ogrid = {p: R5M.GRID[p]["o"] for p in (1, 2)}
    rows = []
    for scale, Ds in D.groupby("scale"):
        rows += set_cells(Ds.drop(columns=["scale"]).copy(), task, enc, scale, m_grid, part_ogrid)
    return rows, dict(task=task, encoder=enc, shards=len(paths), rows=len(D), dup_rows=ndup, dup_conflicting=nconf)


def work_acs(path, m_grid):
    a = pd.read_csv(path)
    a = a[np.isclose(a.alpha, ALPHA) & a.k_meets_alpha01.astype(bool) & a.method.isin(R5M.VALID)].copy()
    kd = ",".join(str(int(k)) for k in a.groupby("fold").K.first())
    folds = sorted(a.fold.unique())
    ogrid = set(int(o) for o in a.o.unique())
    a = a.assign(task="ACS_STATES", encoder="pkg", part=1, K=9, n_T_donors=np.nan, cal_draw=0,
                 label_draw=a["draw"], n_C=np.nan, n_C_donors=np.nan)
    a = a[a.o.isin({0} | set(m_grid))]
    saved = R5M.GRID
    R5M.GRID = {1: dict(K={9}, o=ogrid)}
    try:
        rows = set_cells(a, "ACS_STATES", "pkg", "log_income", m_grid, {1: ogrid},
                         k_desc=f"folds {folds[0]}-{folds[-1]} pooled, K {kd}")
    finally:
        R5M.GRID = saved
    return rows, dict(task="ACS_STATES", folds=[int(f) for f in folds], K=kd, rows=len(a))


def spot_check(cells, mbt_path):
    t = pd.read_csv(mbt_path)
    sel = t[(t.task == "CCRCC") & (t.encoder == "uni_v2") & (t.scale == "log1p") & (t.part == 1) & (t.K == 10) &
            np.isclose(t.alpha, ALPHA)]
    cand = pd.concat([sel[(sel.o == 10)], sel[(sel.o == 0) & sel.method.isin(R5M.O_FREE)]])
    cand = cand[cand.method.isin(R5M.VALID - {"one_per"}) & (cand.finite_mean == 1.0) &
                np.isfinite(cand.width_mean_mean)]
    ref = cand.loc[cand.width_mean_mean.idxmin()]
    mine = cells[(cells.task == "CCRCC") & (cells.encoder == "uni_v2") & (cells.set_scale == "log1p") &
                 (cells.part == 1) & (cells.K == 10) & (cells.m == 10)].iloc[0]
    return dict(cell="CCRCC uni_v2 log1p part 1 K 10 alpha 0.1 o 10", map_aggregate_method=ref.method,
                map_aggregate_width_mean_mean=float(ref.width_mean_mean),
                map_aggregate_width_median_median=float(ref.width_median_median),
                e8_overall_method=mine.overall_method, e8_overall_width_mean=float(mine.overall_width_mean),
                e8_overall_width_median=float(mine.overall_width_median),
                passed=bool(ref.method == mine.overall_method and
                            abs(float(ref.width_mean_mean) - float(mine.overall_width_mean)) < 1e-9 and
                            abs(float(ref.width_median_median) - float(mine.overall_width_median)) < 1e-9))


def main(a):
    os.makedirs(a.out_dir, exist_ok=True)
    RB, units, rb_dups = load_regb(a.regb_root)
    m_grid = sorted(int(m) for m in RB.m.unique())
    paths = [p.strip() for p in open(a.map_inputs) if p.strip()]
    jobs = []
    for task, tok in TASKS.items():
        for enc in sorted(RB[RB.task == task].encoder.unique()):
            ps = [p for p in paths if os.path.basename(p).startswith(f"map_full__{tok}__{enc}__p")]
            jobs.append((task, enc, ps, m_grid))
    with Pool(a.workers) as pool:
        res = pool.map(work_hest, jobs)
    rows, info = [], []
    for r, i in res:
        rows += r
        info.append(i)
        print(f"[e8] {i}", flush=True)
    r, i = work_acs(a.acs, m_grid)
    rows += r
    info.append(i)
    print(f"[e8] {i}", flush=True)
    cells = pd.DataFrame(rows)
    cells.to_csv(os.path.join(a.out_dir, "e8_set_cells.csv"), index=False)
    RB["set_scale"] = RB.apply(lambda r: "log1p" if r.scale == "log1p" else
                               ("log_income" if r.task == "ACS_STATES" else "norm"), axis=1)
    RB = RB.assign(set_encoder=RB.encoder)
    J = RB.merge(cells.rename(columns={"encoder": "set_encoder"}), on=["task", "set_encoder", "set_scale", "m"],
                 how="left", indicator=True)
    J["guarantee"] = GUARANTEE
    J.loc[J["_merge"] == "left_only", "reason"] = "no_set_side"
    J = J.drop(columns=["_merge", "set_encoder"])
    lead = ["task", "encoder", "scale", "estimand", "m", "set_scale", "part", "K", "K_desc", "n_folds", "on_o_grid",
            "reason", "regB_wr_fix1", "regB_wr_se", "regB_boot_B", "regB_R", "regB_genes", "regB_G", "regB_cov_fix1"]
    J = J[lead + [c for c in J.columns if c not in lead]].sort_values(
        ["task", "encoder", "scale", "estimand", "m", "part", "K"]).reset_index(drop=True)
    J.to_csv(os.path.join(a.out_dir, "e8_joint.csv"), index=False)
    on = J[J.on_o_grid == True]  # noqa: E712
    chk = dict(
        regb_units=len(units), regb_unit_names=units, regb_rows_fix1=len(RB), regb_duplicate_keys=rb_dups,
        regb_boot_B=sorted(int(b) for b in RB.regB_boot_B.unique()), m_grid=m_grid,
        set_side=info, set_cells=len(cells), joint_rows=len(J),
        rows_per_task_encoder_scale_estimand={"|".join(map(str, k)): int(v) for k, v in
                                              J.groupby(["task", "encoder", "scale", "estimand"]).size().items()},
        off_grid_rows=int((J.on_o_grid == False).sum()),  # noqa: E712
        off_grid_set_cells=int((cells.on_o_grid == False).sum()),  # noqa: E712
        on_grid_rows=len(on),
        rows_no_valid_set=int(on.reason.fillna("").str.contains("no_valid_set").sum()),
        rows_no_noextra_set=int(on.reason.fillna("").str.contains("no_noextra_set_finite").sum()),
        rows_no_set_side=int((J.reason == "no_set_side").sum()),
        set_cells_no_valid_set=int(cells.reason.fillna("").str.contains("no_valid_set").sum()),
        set_cells_no_noextra_set=int(cells.reason.fillna("").str.contains("no_noextra_set_finite").sum()),
        overall_needs_extra_rows=int((on.overall_needs_extra_labels == True).sum()),  # noqa: E712
        overall_method_counts={k: int(v) for k, v in on.overall_method.value_counts().items()},
        noextra_method_counts={k: int(v) for k, v in on.noextra_method.value_counts().items()},
        spot_check=spot_check(cells, a.map_by_task), diff_boot_B=BOOT_B, guarantee=GUARANTEE)
    json.dump(chk, open(os.path.join(a.out_dir, "e8_checks.json"), "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in chk.items() if k not in ("rows_per_task_encoder_scale_estimand",
                                                                "regb_unit_names")}, default=str), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("out_dir")
    p.add_argument("--regb-root", required=True)
    p.add_argument("--map-inputs", required=True)
    p.add_argument("--acs", required=True)
    p.add_argument("--map-by-task", required=True)
    p.add_argument("--workers", type=int, default=8)
    main(p.parse_args())
