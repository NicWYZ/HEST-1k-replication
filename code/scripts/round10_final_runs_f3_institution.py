#!/usr/bin/env python
"""Round 10, track final-runs, stage F3, item F3.2: the institution axis (plan section 5d.2).

Nothing in this file is a result. It forms two conformal sets for every held-out center unit of
the corpus tasks with at least 4 center units, from F1's center-design prediction files. Each
center's spots carry residuals from the head trained on the other centers, and both arms use these
residuals, so the arms differ only in how calibration is grouped.

  hcp_center  HCP over centers. The target center unit is held out and the calibration groups are
              the other K center units, each spot of unit c weighted 1/((K + 1) N_c), with the
              target's mass 1/(K + 1) at +inf. Finite only when 1/(K + 1) <= alpha.
  hcp_donor   Donor-level HCP pooled across centers, the comparator. The calibration groups are the
              donors of the other center units, each spot of donor d weighted 1/((K_d + 1) N_d),
              K_d the number of those donors, with the target's mass 1/(K_d + 1) at +inf.

Both use C3's hcp kernel unchanged (round4_conf_c3.wq_cols with C3's weights, score |y - yhat|,
the QTOL convention, and `finite_code`, the upward-tie reading). The set for a spot is yhat +- q_g
per gene. Coverage and width are taken per (held-out center, gene) over that center's spots, then
per center the median over genes, then over centers the median of the per-center medians. No random
draws enter, so the dispersion reported is over genes and over centers. Coverage is empirical, and
no finite-sample guarantee is claimed for these grouped designs (plan 5d.0, decision of 11 November).

Levels (5d.2): alpha in {0.2, 0.25} wherever hcp_center is finite (1/units <= alpha), plus the
task's smallest finite level 1/units. hcp_donor runs at the same levels.

Subcommands
  anchor_kernel   5d.2 anchor check 1. C3's CCRCC (24 donors), uni_v2, K = 10, fold INT1, its 3
                  calibration draws. This module's hcp with donors as groups must reproduce W3's
                  committed row (w3_by_fold.csv: part 1, hcp, alpha 0.1, o 0) to 1e-9, and C3's own
                  o0_rows hcp on the same fits.
  anchor_pearson  5d.2 anchor check 2. The center-design file's median over genes of the per-gene
                  Pearson (F1's formula, all spots pooled) must reproduce f1_predictions.csv's
                  pearson_<scale>_median for the task, encoder and design `center` to 1e-9.
  run             Production cells from a JSON config (list of {task, encoder, pred}).

Seeds: none (no random draws). Parquet: explicit pa.schema. Summaries before the bulk table.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_c3 as C  # noqa: E402
import round4_conf_sim as SIM  # noqa: E402

SCALES = ("log1p", "lognorm")
ARMS = ("hcp_center", "hcp_donor")
BASE_LEVELS = (0.2, 0.25)
EXPECTED_UNITS = {"kidney__Visium": 5, "brain__Visium": 6, "bowel__Visium": 9, "breast__Xenium": 4}
ANCHOR_TOL = 1e-9
REF_TOL = 1e-12


# ================================================================== the kernel
def hcp_q_groups(S, groups, alphas):
    """C3's hcp threshold with arbitrary calibration groups. S (n, G) scores, groups (n,) labels.
    Each spot of group g carries 1/((K + 1) N_g), the +inf atom 1/(K + 1), K = number of groups.
    Returns (q (A, G), finite_code (A,), K)."""
    lab = np.asarray(groups).astype(str)
    names, inv, counts = np.unique(lab, return_inverse=True, return_counts=True)
    K = len(names)
    w = np.array([1.0 / ((K + 1) * int(counts[i])) for i in inv], dtype=np.float64)
    q, fc = C.wq_cols(S, w, 1.0 / (K + 1), [1 - a for a in alphas])
    return q, fc, K


def ref_check(S, groups, alphas, q, genes_idx):
    """Max |q - SIM.hcp_q| over the given gene columns (the round4_conf_sim reference kernel)."""
    lab = np.asarray(groups).astype(str)
    names = sorted(set(lab.tolist()))
    worst = 0.0
    for j in genes_idx:
        cal = [S[lab == g, j] for g in names]
        for i, a in enumerate(alphas):
            r = SIM.hcp_q(cal, a)
            if math.isinf(r) and math.isinf(q[i, j]):
                continue
            if math.isinf(r) or math.isinf(q[i, j]):
                worst = math.inf
            else:
                worst = max(worst, abs(r - q[i, j]))
    return worst


def levels_for(units):
    lv = {a for a in BASE_LEVELS if 1.0 / units <= a * (1 + C.QTOL)}
    lv.add(1.0 / units)
    return sorted(lv)


# ================================================================== anchor 1
def anchor_kernel(a):
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    ref = pd.read_csv(a.w3_by_fold)
    sel = ref[(ref.part == 1) & (ref.task == "CCRCC") & (ref.encoder == "uni_v2") & (ref.method == "hcp")
              & np.isclose(ref.alpha, 0.1) & (ref.o == 0) & (ref.K == 10) & (ref.fold.astype(str) == "INT1")]
    assert len(sel) == 1, f"reference row count {len(sel)}"
    rr = sel.iloc[0]
    T = C.load_task("CCRCC:24", "uni_v2")
    specs = T.specs(10, n_cal_draws=C.N_CAL_DRAWS, folds=["INT1"])
    per, refk = [], []
    for sp in specs:
        fit = T.fit(sp)
        q, fc, K = hcp_q_groups(fit.S_C, fit.lab_C, (0.1,))
        m = C.interval_metrics(fit.Y_E, fit.P_E - q[0], fit.P_E + q[0], fit.slides)
        c3 = C.o0_rows(fit, alphas=(0.1,), methods=("hcp",))[0]
        refk.append(ref_check(fit.S_C, fit.lab_C, (0.1,), q, range(min(5, q.shape[1]))))
        per.append(dict(cal_draw=fit.cal_draw, K=K, n_C=fit.n_C, n_E=fit.n_E, coverage=m["coverage"],
                        width_mean=m["width_mean"], width_median=m["width_median"], finite=m["finite"],
                        finite_code=bool(fc[0]), c3_coverage=c3["coverage"], c3_width_mean=c3["width_mean"],
                        c3_width_median=c3["width_median"], sim_ref_maxdiff=refk[-1]))
        print(f"[anchor_kernel] draw {fit.cal_draw} K={K} cov {m['coverage']:.12f} "
              f"wmed {m['width_median']:.12f} {time.time() - t0:.0f}s", flush=True)
    P = pd.DataFrame(per)
    P.to_csv(os.path.join(a.out, "anchor_kernel_per_draw.csv"), index=False)
    rows = []
    for col in ("coverage", "width_mean", "width_median"):
        mine, c3m, refv = float(P[col].mean()), float(P["c3_" + col].mean()), float(rr[col])
        rows.append(dict(check=f"w3_row_{col}", reference=refv, reproduced=mine, abs_diff=abs(mine - refv),
                         tol=ANCHOR_TOL, passed=bool(abs(mine - refv) <= ANCHOR_TOL)))
        rows.append(dict(check=f"c3_o0_rows_{col}", reference=c3m, reproduced=mine, abs_diff=abs(mine - c3m),
                         tol=ANCHOR_TOL, passed=bool(abs(mine - c3m) <= ANCHOR_TOL)))
    rows.append(dict(check="n_draws", reference=float(rr["n_draws"]), reproduced=float(len(P)),
                     abs_diff=abs(len(P) - float(rr["n_draws"])), tol=0, passed=bool(len(P) == rr["n_draws"])))
    rows.append(dict(check="K_groups", reference=10.0, reproduced=float(P.K.min()),
                     abs_diff=float(abs(P.K - 10).max()), tol=0, passed=bool((P.K == 10).all())))
    rows.append(dict(check="sim_hcp_q_maxdiff_5genes", reference=0.0, reproduced=float(max(refk)),
                     abs_diff=float(max(refk)), tol=REF_TOL, passed=bool(max(refk) <= REF_TOL)))
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(a.out, "anchor_kernel_checks.csv"), index=False)
    json.dump(dict(reference_file=a.w3_by_fold, reference_row=rr.to_dict(), passed=bool(R.passed.all()),
                   wall_seconds=int(time.time() - t0)), open(os.path.join(a.out, "anchor_kernel.json"), "w"),
              indent=1, default=str)
    print(R.to_string(), flush=True)
    return 0 if R.passed.all() else 4


# ================================================================== anchor 2
def pearson(a, b):
    """round10_final_runs_f1_predict.pearson, copied."""
    a = a - a.mean(); b = b - b.mean(); d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else float("nan")


def anchor_pearson(a):
    import pyarrow.parquet as pq
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    ref = pd.read_csv(a.f1_predictions)
    sel = ref[(ref.task == a.task) & (ref.encoder == a.encoder) & (ref.design == "center")]
    assert len(sel) == 1, f"reference row count {len(sel)}"
    rr = sel.iloc[0]
    tab = pq.read_table(a.pred)
    cols = tab.column_names
    rows = []
    for sc in SCALES:
        genes = [c.split("__", 1)[1] for c in cols if c.startswith(f"y_{sc}__")]
        rs = [pearson(tab.column(f"y_{sc}__{g}").to_numpy(), tab.column(f"f_{sc}__{g}").to_numpy()) for g in genes]
        v = [x for x in rs if x == x]
        mine, refv = float(np.median(v)), float(rr[f"pearson_{sc}_median"])
        rows.append(dict(check=f"median_pearson_{sc}", n_genes=len(genes), reference=refv, reproduced=mine,
                         abs_diff=abs(mine - refv), tol=ANCHOR_TOL, passed=bool(abs(mine - refv) <= ANCHOR_TOL),
                         primary=(sc == "log1p")))
    rows.append(dict(check="spots", n_genes=np.nan, reference=float(rr["spots_predicted"]),
                     reproduced=float(tab.num_rows), abs_diff=abs(tab.num_rows - float(rr["spots_predicted"])),
                     tol=0, passed=bool(tab.num_rows == rr["spots_predicted"]), primary=False))
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(a.out, "anchor_pearson_checks.csv"), index=False)
    ok = bool(R.passed.all())
    json.dump(dict(reference_file=a.f1_predictions, reference_row=rr.to_dict(), pred=a.pred, passed=ok,
                   wall_seconds=int(time.time() - t0)), open(os.path.join(a.out, "anchor_pearson.json"), "w"),
              indent=1, default=str)
    print(R.to_string(), flush=True)
    return 0 if ok else 4


# ================================================================== production
def gene_q(v, x):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    return float(np.quantile(v, x)) if len(v) else float("nan")


def run_cell(cell):
    """All rows of one (task, encoder) center-design file. Returns (by_gene, by_center, weights, checks)."""
    import pyarrow.parquet as pq
    task, enc = cell["task"], cell["encoder"]
    tab = pq.read_table(cell["pred"])
    meta = {k: tab.column(k).to_numpy(zero_copy_only=False).astype(str) for k in ("fold", "donor_id")}
    fold, donor = meta["fold"], meta["donor_id"]
    units = sorted(set(fold.tolist()))
    exp = EXPECTED_UNITS[task]
    checks = [dict(task=task, encoder=enc, check="n_units", value=float(len(units)), expected=float(exp),
                   passed=bool(len(units) == exp))]
    assert len(units) == exp, (task, units)
    alphas = levels_for(len(units))
    don_by_unit = {u: sorted(set(donor[fold == u].tolist())) for u in units}
    n_by_unit = {u: int((fold == u).sum()) for u in units}
    overlap = 0
    for u in units:
        overlap += len(set(don_by_unit[u]) & set(donor[fold != u].tolist()))
    checks.append(dict(task=task, encoder=enc, check="donors_shared_across_units", value=float(overlap),
                       expected=0.0, passed=bool(overlap == 0)))
    assert overlap == 0, f"{task}: donors shared across center units"
    gb, bc, wt = [], [], []
    for sc in SCALES:
        genes = [c.split("__", 1)[1] for c in tab.column_names if c.startswith(f"y_{sc}__")]
        Y = np.column_stack([tab.column(f"y_{sc}__{g}").to_numpy() for g in genes]).astype(np.float64)
        F = np.column_stack([tab.column(f"f_{sc}__{g}").to_numpy() for g in genes]).astype(np.float64)
        nonfin = int((~np.isfinite(Y)).sum() + (~np.isfinite(F)).sum())
        checks.append(dict(task=task, encoder=enc, check=f"nonfinite_{sc}", value=float(nonfin), expected=0.0,
                           passed=bool(nonfin == 0)))
        assert nonfin == 0
        Sabs = np.abs(Y - F)
        for u in units:
            E = fold == u
            Cm = ~E
            YE, FE = Y[E], F[E]
            for arm in ARMS:
                grp = fold[Cm] if arm == "hcp_center" else donor[Cm]
                q, fc, K = hcp_q_groups(Sabs[Cm], grp, alphas)
                rdiff = ref_check(Sabs[Cm], grp, alphas, q, (0, len(genes) // 2))
                checks.append(dict(task=task, encoder=enc, check=f"sim_hcp_q_maxdiff:{sc}:{u}:{arm}",
                                   value=float(rdiff), expected=0.0, passed=bool(rdiff <= REF_TOL)))
                for i, al in enumerate(alphas):
                    lo, hi = FE - q[i], FE + q[i]
                    cov = ((YE >= lo) & (YE <= hi)).mean(axis=0)
                    width = 2.0 * q[i]
                    fin = np.isfinite(width)
                    for j, g in enumerate(genes):
                        gb.append(dict(task=task, encoder=enc, scale=sc, arm=arm, alpha=al, center_unit=u, gene=g,
                                       K=K, n_spots=int(E.sum()), coverage=float(cov[j]), width=float(width[j]),
                                       finite=bool(fin[j])))
                    wf = width[fin]
                    bc.append(dict(task=task, encoder=enc, scale=sc, arm=arm, alpha=al, center_unit=u,
                                   n_spots=int(E.sum()), n_donors=len(don_by_unit[u]), K=K, n_cal_spots=int(Cm.sum()),
                                   n_genes=len(genes), coverage_median_gene=float(np.median(cov)),
                                   coverage_mean_gene=float(np.mean(cov)), coverage_q10_gene=gene_q(cov, 0.1),
                                   coverage_q90_gene=gene_q(cov, 0.9),
                                   width_median_gene=float(np.median(wf)) if len(wf) else float("inf"),
                                   width_q10_gene=gene_q(wf, 0.1), width_q90_gene=gene_q(wf, 0.9),
                                   finite_share=float(fin.mean()), finite_code=bool(fc[i])))
            if sc == SCALES[0]:
                Kc = len(units) - 1
                Kd = sum(len(don_by_unit[v]) for v in units if v != u)
                for v in units:
                    if v == u:
                        continue
                    wt.append(dict(task=task, encoder=enc, target_unit=u, cal_unit=v, n_donors=len(don_by_unit[v]),
                                   n_spots=n_by_unit[v], K_center=Kc, K_donor=Kd,
                                   weight_center_arm=1.0 / (Kc + 1),
                                   weight_donor_arm=len(don_by_unit[v]) / (Kd + 1)))
        print(f"[run] {task} {enc} {sc} done", flush=True)
    return gb, bc, wt, checks


def summarise(BC):
    keys = ["task", "encoder", "scale", "arm", "alpha"]
    out = []
    for k, g in BC.groupby(keys, sort=True):
        out.append(dict(zip(keys, k), n_centers=len(g), coverage_median_center=float(np.median(g.coverage_median_gene)),
                        coverage_min_center=float(g.coverage_median_gene.min()),
                        coverage_max_center=float(g.coverage_median_gene.max()),
                        width_median_center=float(np.median(g.width_median_gene)),
                        width_min_center=float(g.width_median_gene.min()),
                        width_max_center=float(g.width_median_gene.max()),
                        finite_share_min=float(g.finite_share.min()), finite_code_all=bool(g.finite_code.all())))
    return pd.DataFrame(out)


def score_fr8(SU, BC):
    """FR8 (5d.2), fixed before the run. Kidney Visium, alpha 0.2, uni_v2, log1p. Clause 1 holds if the
    comparator's (hcp_donor) median over the five held-out centers of the per-center median-gene coverage
    is below 0.75. Clause 2 holds if that value for hcp_center is at least 0.8."""
    def sel(D, arm):
        return D[(D.task == "kidney__Visium") & (D.encoder == "uni_v2") & (D.scale == "log1p")
                 & (D.arm == arm) & np.isclose(D.alpha, 0.2)]
    rows = []
    for clause, arm, thr, op in ((1, "hcp_donor", 0.75, "lt"), (2, "hcp_center", 0.8, "ge")):
        s = sel(SU, arm)
        if len(s) != 1:
            rows.append(dict(clause=clause, arm=arm, value=np.nan, threshold=thr, comparison=op, holds=None,
                             n_centers=0, per_center=""))
            continue
        v = float(s.coverage_median_center.iloc[0])
        per = sel(BC, arm).sort_values("center_unit")
        rows.append(dict(clause=clause, arm=arm, value=v, threshold=thr, comparison=op,
                         holds=bool(v < thr) if op == "lt" else bool(v >= thr), n_centers=int(s.n_centers.iloc[0]),
                         per_center=";".join(f"{r.center_unit}:{r.coverage_median_gene:.6f}" for r in per.itertuples())))
    return pd.DataFrame(rows)


def by_gene_schema():
    import pyarrow as pa
    return pa.schema([pa.field("task", pa.string()), pa.field("encoder", pa.string()), pa.field("scale", pa.string()),
                      pa.field("arm", pa.string()), pa.field("alpha", pa.float64()),
                      pa.field("center_unit", pa.string()), pa.field("gene", pa.string()), pa.field("K", pa.int64()),
                      pa.field("n_spots", pa.int64()), pa.field("coverage", pa.float64()),
                      pa.field("width", pa.float64()), pa.field("finite", pa.bool_())])


def run(a):
    import pyarrow as pa
    import pyarrow.parquet as pq
    os.makedirs(a.out, exist_ok=True)
    cfg = json.load(open(a.config))
    t0 = time.time()
    GB, BCr, WT, CK, tim = [], [], [], [], []
    for cell in cfg["cells"]:
        t1 = time.time()
        gb, bc, wt, ck = run_cell(cell)
        GB += gb; BCr += bc; WT += wt; CK += ck
        tim.append(dict(task=cell["task"], encoder=cell["encoder"], seconds=time.time() - t1))
        print(f"[run] cell {cell['task']} {cell['encoder']} {time.time() - t1:.1f}s", flush=True)
    BC = pd.DataFrame(BCr)
    SU = summarise(BC)
    CKd = pd.DataFrame(CK)
    SU.to_csv(os.path.join(a.out, "inst_summary.csv"), index=False)
    BC.to_csv(os.path.join(a.out, "inst_by_center.csv"), index=False)
    pd.DataFrame(WT).to_csv(os.path.join(a.out, "inst_weights.csv"), index=False)
    CKd.to_csv(os.path.join(a.out, "inst_checks.csv"), index=False)
    pd.DataFrame(tim).to_csv(os.path.join(a.out, "inst_timing.csv"), index=False)
    if cfg.get("score_fr8"):
        score_fr8(SU, BC).to_csv(os.path.join(a.out, "inst_fr8.csv"), index=False)
    sch = by_gene_schema()
    G = pd.DataFrame(GB)
    pq.write_table(pa.Table.from_pandas(G[[f.name for f in sch]], schema=sch, preserve_index=False),
                   os.path.join(a.out, "inst_by_gene.parquet"))
    ok = bool(CKd.passed.all())
    json.dump(dict(cells=len(cfg["cells"]), rows_by_gene=len(G), rows_by_center=len(BC), checks_passed=ok,
                   wall_seconds=int(time.time() - t0)), open(os.path.join(a.out, "inst_run.json"), "w"), indent=1)
    print(SU.to_string(), flush=True)
    print(f"[run] done {len(G)} gene rows, checks passed {ok}, {time.time() - t0:.0f}s", flush=True)
    return 0 if ok else 5


def main(argv=None):
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)
    k = sp.add_parser("anchor_kernel")
    k.add_argument("--w3-by-fold", required=True)
    k.add_argument("--out", required=True)
    r = sp.add_parser("anchor_pearson")
    for x in ("--pred", "--f1-predictions", "--task", "--encoder", "--out"):
        r.add_argument(x, required=True)
    u = sp.add_parser("run")
    u.add_argument("--config", required=True)
    u.add_argument("--out", required=True)
    a = p.parse_args(argv)
    return {"anchor_kernel": anchor_kernel, "anchor_pearson": anchor_pearson, "run": run}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
