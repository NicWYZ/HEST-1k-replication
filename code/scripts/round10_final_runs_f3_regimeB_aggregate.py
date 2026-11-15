"""Round 10, track final-runs, F3: aggregation of the regime B track's regB_norm and e8 units (plan 5d.6 item 5,
5d.4 item 2).

usage: round10_final_runs_f3_regimeB_aggregate.py <units_root> <production_index.json> <f2_summary.csv> <out_dir>
  units_root  $BASE/F3/regimeB (one directory per unit);
  f2_summary  F2's committed f2_regimeB_summary.csv (log(1 + y) rows printed beside open point 5's score).
Writes (summaries first):
  f3_regB_checks.json             completeness, cluster-value check maxima, F2 row check maxima, open point 5 verdict;
  f3_regB_units.csv               per unit: item, PROVENANCE status, rows, cv_max_rel, donors matched, F2 rows matched
                                  and their largest absolute difference, seconds;
  f3_regB_norm_summary.csv        regB_norm rows with F2's aggregate columns (per task, encoder, scale, estimand, m, form);
  f3_regB_norm_fix1_vs_ppi.csv    F2's per-cell comparison of the three forms (median over genes of per-gene width ratios);
  f3_op5_score.csv                open point 5: per HEST task, encoder, estimand and m >= 6, C_fix1's median E(V)/Var and
                                  median coverage on norm_refit, both conditions, and F2's log(1 + y) values beside;
  f3_e8_summary.csv, f3_e8_fix1_vs_ppi.csv   the same two tables for the e8 units;
  f3_e8_wr.csv                    every unit's width ratios with their bootstrap standard errors;
  f3_e8_f2check.csv               every e8 unit's check of its rows at F2's m against F2's gene rows.
Open point 5 is held when every cell meets both conditions (0.93 <= median E(V)/Var <= 1.05, |median coverage - 0.90|
<= 0.03), and refuted otherwise; the counts per condition and task are printed beside.
"""
import glob, json, os, sys
import numpy as np, pandas as pd

root, idxp, f2sum, out = sys.argv[1:5]
os.makedirs(out, exist_ok=True)
idx = json.load(open(idxp))
K = ["task", "encoder", "scale", "estimand", "m"]
q = lambda p: (lambda s: s.quantile(p))
HEST = ["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM"]


def status(d):
    pv = os.path.join(d, "PROVENANCE.txt")
    if not os.path.exists(pv):
        return "missing"
    return next((l.split(":", 1)[1].strip() for l in open(pv) if l.startswith("status:")), "no status")


def summarise(D):
    D = D.copy(); D["bias_z"] = D.bias / D.mcse_bias.replace(0, np.nan)
    S = D.groupby(K + ["form"]).agg(G=("G", "first"), genes=("gene", "size"), R=("R", "first"),
                                    median_coverage=("coverage", "median"), q10_coverage=("coverage", q(0.1)),
                                    q90_coverage=("coverage", q(0.9)), median_coverage_se=("coverage_se", "median"),
                                    median_width=("median_width", "median"), median_ev_over_var=("ev_over_var", "median"),
                                    q10_ev_over_var=("ev_over_var", q(0.1)), median_frac_no_interval=("frac_no_interval", "median"),
                                    median_frac_v_neg=("frac_v_neg", "median"), median_bias_z=("bias_z", "median")).reset_index()
    w = D.pivot_table(index=K + ["gene"], columns="form", values=["median_width", "coverage"]).reset_index()
    w.columns = ["_".join([c for c in col if c]) for col in w.columns]
    F = None
    if {"median_width_C_fix1", "median_width_C_classical", "median_width_C_ppi"} <= set(w.columns):
        w["wr_fix1"] = w.median_width_C_fix1 / w.median_width_C_classical
        w["wr_ppi"] = w.median_width_C_ppi / w.median_width_C_classical
        F = w.groupby(K).agg(genes=("gene", "size"), cov_fix1=("coverage_C_fix1", "median"), cov_ppi=("coverage_C_ppi", "median"),
                             cov_classical=("coverage_C_classical", "median"), median_wr_fix1=("wr_fix1", "median"),
                             median_wr_ppi=("wr_ppi", "median"),
                             share_fix1_wider=("wr_fix1", lambda s: float((s > 1).mean()))).reset_index()
    return S, F


units, frames, wrs, chks = [], {"regB_norm": [], "e8": []}, [], []
for u in idx["units"]:
    if u["item"] not in ("regB_norm", "e8"):
        continue
    d = os.path.join(root, u["unit"]); st = status(d)
    row = dict(unit=u["unit"], item=u["item"], task=u["task"], status=st)
    gp, sp = os.path.join(d, "regimeB_genes.parquet"), os.path.join(d, "regimeB_summary.json")
    if st == "COMPLETED" and os.path.exists(gp) and os.path.exists(sp):
        s = json.load(open(sp)); x = pd.read_parquet(gp); frames[u["item"]].append(x)
        cvs = [v for p in s.get("populations", []) for v in (p.get("cv_check") or {}).values()]
        mx = [v.get("max_rel") for v in cvs if v.get("max_rel") is not None and np.isfinite(v.get("max_rel"))]
        row.update(rows=len(x), cv_max_rel=max(mx) if mx else np.nan,
                   cv_donors_all_matched=bool(all(v.get("n_common", 0) == v.get("n_valid_regimeB", -1) for v in cvs if v.get("n_matched", 1) != 0)),
                   seconds=sum(p.get("seconds", 0) for p in s.get("populations", [])))
        if s.get("f2_check"):
            row.update(f2_rows_matched=s["f2_check"]["rows_matched"], f2_max_abs=s["f2_check"]["max_abs_all"])
        wp = os.path.join(d, "regimeB_wr.csv")
        if os.path.exists(wp) and os.path.getsize(wp) > 0:
            wrs.append(pd.read_csv(wp))
        cp = os.path.join(d, "regimeB_f2check.csv")
        if os.path.exists(cp):
            chks.append(pd.read_csv(cp).assign(unit=u["unit"]))
    units.append(row)
U = pd.DataFrame(units)
res = dict(units_expected=len(U), units_completed=int((U.status == "COMPLETED").sum()),
           units_not_completed=U[U.status != "COMPLETED"].unit.tolist(),
           cv_max_rel=float(U.cv_max_rel.max()) if "cv_max_rel" in U and U.cv_max_rel.notna().any() else None,
           cv_donors_all_matched=bool(U["cv_donors_all_matched"].fillna(True).all()) if "cv_donors_all_matched" in U else None,
           f2_rows_matched=int(U["f2_rows_matched"].fillna(0).sum()) if "f2_rows_matched" in U else 0,
           f2_max_abs=float(U.f2_max_abs.max()) if "f2_max_abs" in U and U.f2_max_abs.notna().any() else None)
json.dump(res, open(os.path.join(out, "f3_regB_checks.json"), "w"), indent=1, default=str)
U.to_csv(os.path.join(out, "f3_regB_units.csv"), index=False)

for item in ("regB_norm", "e8"):
    if not frames[item]:
        continue
    D = pd.concat(frames[item], ignore_index=True)
    res[f"{item}_rows"] = len(D); res[f"{item}_duplicates"] = int(D.duplicated(subset=K + ["form", "gene"]).sum())
    S, F = summarise(D)
    S.to_csv(os.path.join(out, f"f3_{item}_summary.csv"), index=False)
    if F is not None:
        F.to_csv(os.path.join(out, f"f3_{item}_fix1_vs_ppi.csv"), index=False)
    if item == "regB_norm":
        c = S[(S.form == "C_fix1") & (S.m >= 6) & (S.task.isin(HEST))].copy()
        c["ok_ev"] = c.median_ev_over_var.between(0.93, 1.05)
        c["ok_cov"] = (c.median_coverage - 0.90).abs() <= 0.03
        c["ok_both"] = c.ok_ev & c.ok_cov
        f2 = pd.read_csv(f2sum)
        f2 = f2[(f2.form == "C_fix1") & (f2.scale == "log1p")][["task", "encoder", "estimand", "m", "median_coverage", "median_ev_over_var"]]
        c = c.merge(f2, on=["task", "encoder", "estimand", "m"], how="left", suffixes=("", "_log1p_f2"))
        c.to_csv(os.path.join(out, "f3_op5_score.csv"), index=False)
        prim = c[c.task != "CCRCC_merged"]
        res["op5"] = dict(cells=len(prim), cells_ok_ev=int(prim.ok_ev.sum()), cells_ok_cov=int(prim.ok_cov.sum()),
                          cells_ok_both=int(prim.ok_both.sum()),
                          ev_range=[float(prim.median_ev_over_var.min()), float(prim.median_ev_over_var.max())],
                          cov_range=[float(prim.median_coverage.min()), float(prim.median_coverage.max())],
                          by_task={t: dict(cells=len(g), ok_ev=int(g.ok_ev.sum()), ok_cov=int(g.ok_cov.sum()), ok_both=int(g.ok_both.sum()))
                                   for t, g in c.groupby("task")},
                          verdict="held" if len(prim) and prim.ok_both.all() else "refuted",
                          rule="every HEST task (CCRCC, INDIANA_KIDNEY, LUNG_XENIUM; CCRCC_merged beside), encoder, estimand "
                               "(theta3, theta2) and m >= 6 on norm_refit: 0.93 <= median E(V)/Var <= 1.05 and "
                               "|median coverage - 0.90| <= 0.03")
if wrs:
    W = pd.concat(wrs, ignore_index=True); W.to_csv(os.path.join(out, "f3_e8_wr.csv"), index=False)
    res["e8_wr_rows"] = len(W); res["e8_wr_median_boot_se"] = float(W.boot_se.median())
if chks:
    C = pd.concat(chks, ignore_index=True); C.to_csv(os.path.join(out, "f3_e8_f2check.csv"), index=False)
    res["e8_f2check_rows_matched"] = int(C.rows_matched.sum()); res["e8_f2check_max_abs_all"] = float(C.max_abs_all.max())
json.dump(res, open(os.path.join(out, "f3_regB_checks.json"), "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
