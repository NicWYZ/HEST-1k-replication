"""Round 10, track final-runs, F3.3 (i): aggregation of the regcomp units (plan 5d.3 (i)) and the score of R10-F3a.

usage: round10_final_runs_f3_regcomp_aggregate.py <units_root> <production_index.json> <out_dir>
Reads every regcomp unit's regcomp_genes.parquet (round10_final_runs_f3_regcomp.RCSCHEMA). Writes (summaries first):
  f3_regcomp_checks.json      completeness, duplicate rows, cluster-value check maxima, the R10-F3a verdict;
  f3_regcomp_units.csv        per unit: PROVENANCE status, rows, seconds;
  f3_regcomp_cells.csv        per (task, encoder, scale, estimand, regime, budget, cost, n_L, form, interval): genes,
                              median, 10% and 90% coverage, median coverage standard error, median of the per-gene mean
                              width and of the per-gene median width, median E(V)/Var;
  f3_regcomp_comparisons.csv  per regime A cell (task, encoder, scale, estimand, budget B, n_L) and cost ratio c with its
                              cost-matched regime B cell (cost 'cd_cs_<c>_vs_A_nL<n_L>_B<B>'), for each arm pair
                              (fix1: A C_fix1 'twostage_t|fpc' against B C_fix1; ppi: A C_ppi 'textbook_t|fpc|lin|xf'
                              against B C_ppi; classical: A C_classical 'textbook_t|fpc|lin|xf' against B C_classical):
                              genes, the median over genes of regime B's width over regime A's (per-gene mean width, as
                              round 5's E3.4 takes it, and per-gene median width beside), the share of genes where B is
                              narrower, both regimes' median coverage and their median Monte Carlo standard errors;
  f3_regcomp_r10f3a.csv       the comparisons R10-F3a counts.
R10-F3a (plan 5d.7): under the fixed coefficient, regime B is narrower than regime A in at least 0.8 of the
cost-matched comparisons on the HEST tasks and ACS by state. Counted as round 5's E3.4 counted (round5_ppi_e3_merge.py,
E3.4): theta3, cost ratio 10, one comparison per (task, encoder, n_L, budget), narrower when the median over genes of
the per-gene mean-width ratio is below 1; on log(1 + y) (ACS: log income), with norm_refit, the other estimands and
the C_ppi pair (round 5's own arm) printed beside.
"""
import json, os, sys
import numpy as np, pandas as pd

root, idxp, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
idx = json.load(open(idxp))
q = lambda p: (lambda s: s.quantile(p))
HEST_ACS = ["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM", "ACS_STATES"]
PAIRS = {"fix1": (("C_fix1", "twostage_t|fpc"), ("C_fix1", "regB_t")),
         "ppi": (("C_ppi", "textbook_t|fpc|lin|xf"), ("C_ppi", "regB_t")),
         "classical": (("C_classical", "textbook_t|fpc|lin|xf"), ("C_classical", "regB_t"))}


def status(d):
    pv = os.path.join(d, "PROVENANCE.txt")
    if not os.path.exists(pv):
        return "missing"
    return next((l.split(":", 1)[1].strip() for l in open(pv) if l.startswith("status:")), "no status")


units, frames, cvmax = [], [], []
for u in idx["units"]:
    if u["item"] != "regcomp":
        continue
    d = os.path.join(root, u["unit"]); st = status(d)
    row = dict(unit=u["unit"], task=u["task"], status=st)
    gp, sp = os.path.join(d, "regcomp_genes.parquet"), os.path.join(d, "regcomp_summary.json")
    if st == "COMPLETED" and os.path.exists(gp):
        x = pd.read_parquet(gp); frames.append(x); row["rows"] = len(x)
        if os.path.exists(sp):
            s = json.load(open(sp)); row["seconds"] = sum(p.get("seconds", 0) for p in s.get("populations", []))
            for p in s.get("populations", []):
                for v in (p.get("cv_check") or {}).values():
                    if v.get("max_rel") is not None and np.isfinite(v["max_rel"]):
                        cvmax.append(v["max_rel"])
    units.append(row)
U = pd.DataFrame(units)
res = dict(units_expected=len(U), units_completed=int((U.status == "COMPLETED").sum()),
           units_not_completed=U[U.status != "COMPLETED"].unit.tolist(), cv_max_rel=max(cvmax) if cvmax else None)
json.dump(res, open(os.path.join(out, "f3_regcomp_checks.json"), "w"), indent=1, default=str)
U.to_csv(os.path.join(out, "f3_regcomp_units.csv"), index=False)
D = pd.concat(frames, ignore_index=True)
KC = ["task", "encoder", "scale", "estimand", "regime", "budget", "cost", "n_L", "form", "interval"]
res["rows"] = len(D); res["duplicate_rows"] = int(D.duplicated(subset=KC + ["gene"]).sum())
C = D.groupby(KC).agg(G=("G", "first"), genes=("gene", "size"), R=("R", "first"), m_label=("m_label", "first"),
                      m_median=("m_median", "first"), median_coverage=("coverage", "median"), q10_coverage=("coverage", q(0.1)),
                      q90_coverage=("coverage", q(0.9)), median_coverage_se=("coverage_se", "median"),
                      median_mean_width=("mean_width", "median"), median_median_width=("median_width", "median"),
                      median_ev_over_var=("ev_over_var", "median")).reset_index()
C.to_csv(os.path.join(out, "f3_regcomp_cells.csv"), index=False)

A = D[D.regime == "A"].copy(); Bm = D[(D.regime == "B") & (D.cost != "unit")].copy()
Bm["c"] = Bm.cost.str.extract(r"cd_cs_([0-9.]+)_vs")[0].astype(float)
Bm["n_L_A"] = Bm.cost.str.extract(r"nL(\d+)_B")[0].astype(int)
Bm["budget_A"] = Bm.cost.str.extract(r"_B(\d+)$")[0].astype(float)
KG = ["task", "encoder", "scale", "estimand", "gene"]
rows = []
for pair, ((fa, ia), (fb, ib)) in PAIRS.items():
    a = A[(A.form == fa) & (A.interval == ia)][KG + ["budget", "n_L", "mean_width", "median_width", "coverage", "coverage_se"]]
    a = a.rename(columns={"budget": "budget_A", "n_L": "n_L_A"})
    b = Bm[(Bm.form == fb) & (Bm.interval == ib)][KG + ["budget_A", "n_L_A", "c", "budget", "m_median", "mean_width", "median_width",
                                                       "coverage", "coverage_se"]]
    j = a.merge(b, on=KG + ["budget_A", "n_L_A"], suffixes=("_A", "_B"))
    j["r_mean"] = j.mean_width_B / j.mean_width_A; j["r_median"] = j.median_width_B / j.median_width_A
    g = j.groupby(["task", "encoder", "scale", "estimand", "budget_A", "n_L_A", "c"]).agg(
        genes=("gene", "size"), budget_B=("budget", "first"), m_median_B=("m_median", "first"),
        median_ratio_mean_width=("r_mean", "median"), median_ratio_median_width=("r_median", "median"),
        share_B_narrower=("r_mean", lambda s: float((s < 1).mean())), cov_A=("coverage_A", "median"),
        cov_B=("coverage_B", "median"), mcse_cov_A=("coverage_se_A", "median"), mcse_cov_B=("coverage_se_B", "median")).reset_index()
    g["pair"] = pair; rows.append(g)
M = pd.concat(rows, ignore_index=True)
M.to_csv(os.path.join(out, "f3_regcomp_comparisons.csv"), index=False)


def count(sel):
    return dict(n=len(sel), B_narrower=int((sel.median_ratio_mean_width < 1).sum()),
                share=float((sel.median_ratio_mean_width < 1).mean()) if len(sel) else None,
                median_ratio=float(sel.median_ratio_mean_width.median()) if len(sel) else None)


base = M[(M.task.isin(HEST_ACS)) & (M.c == 10.0)]
prim = base[(base.pair == "fix1") & (base.estimand == "theta3") & (base.scale.isin(["log1p", "log_income"]))]
prim.to_csv(os.path.join(out, "f3_regcomp_r10f3a.csv"), index=False)
sc = count(prim)
res["r10f3a"] = dict(primary=sc, verdict=("held" if sc["n"] and sc["share"] >= 0.8 else "refuted"),
                     rule="fix1 pair, theta3, cost ratio 10, HEST tasks with CCRCC_merged and ACS by state, log(1 + y) and log income; "
                          "one comparison per (task, encoder, n_L, budget); narrower when the median over genes of the mean-width ratio < 1",
                     beside=dict(norm_refit_fix1_theta3=count(base[(base.pair == "fix1") & (base.estimand == "theta3") & (base.scale == "norm_refit")]),
                                 fix1_theta2=count(base[(base.pair == "fix1") & (base.estimand == "theta2")]),
                                 fix1_mu=count(base[(base.pair == "fix1") & (base.estimand == "mu")]),
                                 ppi_theta3_log1p=count(base[(base.pair == "ppi") & (base.estimand == "theta3") & (base.scale.isin(["log1p", "log_income"]))]),
                                 classical_theta3_log1p=count(base[(base.pair == "classical") & (base.estimand == "theta3") & (base.scale.isin(["log1p", "log_income"]))]),
                                 fix1_all_tasks_all_c=count(M[M.pair == "fix1"]),
                                 round5_E3_4="C_ppi: B narrower in 210 of 232 comparisons, median ratio 0.430 (results/round5/ppi/E3_twolevel/e3_prediction_scores.csv)"))
res["by_task_fix1_theta3_c10"] = {t: count(g) for t, g in prim.groupby("task")}
json.dump(res, open(os.path.join(out, "f3_regcomp_checks.json"), "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
