"""Round 10, track final-runs, F2: aggregation of the regime A units (plan, sections 5.3 and 5.8).

usage: round10_final_runs_f2_aggregate.py <regimeA_root> <out_dir>
Reads every <regimeA_root>/<unit>/regimeA_cells.parquet and writes, switch rule first:
  f2_switch_rule.csv     per (task, encoder, scale, estimand, n >= 6): median over genes of E(V_w)/Var for xf2_r5,
                         its 10% quantile and minimum, the share of genes below 0.95, the median share of draws
                         with V < 0, and an approximate Monte Carlo standard error of the median ratio,
                         ratio * sqrt(2 / (R - 1)), which carries only the error of the empirical variance;
  f2_switch_decision.json  the rule's verdict over every cell, and over the cells of the primary scales only;
  f2_regimeA_summary.csv per (task, encoder, scale, estimand, n, arm, variance): genes, median and 10%/90% quantiles
                         of coverage, median of median width, median RMSE, median share of no-interval draws,
                         median E(V)/Var;
  f2_fix1_cost.csv       per (task, encoder, scale, estimand, n): share of genes whose fix1 median width exceeds
                         classical's, and the same with mean widths;
  f2_units.csv           the units read, with their row counts and summary fields.
"""
import glob, json, os, sys
import numpy as np, pandas as pd

root, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
units, frames = [], []
for d in sorted(glob.glob(os.path.join(root, "*", "regimeA_cells.parquet"))):
    u = os.path.basename(os.path.dirname(d))
    s = json.load(open(os.path.join(os.path.dirname(d), "regimeA_summary.json")))
    x = pd.read_parquet(d); frames.append(x)
    units.append(dict(unit=u, rows=len(x), n_populations=s.get("n_populations"), n_skipped=s.get("n_skipped"),
                      max_const_identity_dev=s.get("max_const_identity_dev"), seconds=s.get("seconds")))
pd.DataFrame(units).to_csv(os.path.join(out, "f2_units.csv"), index=False)
D = pd.concat(frames, ignore_index=True)
K = ["task", "encoder", "scale", "estimand", "n"]
# switch rule
w = D[(D.arm == "xf2_r5") & (D.variance == "V_w") & (D.n >= 6)]
v = D[(D.arm == "xf2_r5") & (D.variance == "V") & (D.n >= 6)][K + ["gene", "frac_v_neg"]]
w = w.merge(v, on=K + ["gene"], suffixes=("", "_V"))
sw = w.groupby(K).agg(G=("G", "first"), genes=("gene", "size"), R=("R", "first"),
                      median_ev_over_var=("ev_over_var", "median"),
                      q10_ev_over_var=("ev_over_var", lambda s: s.quantile(0.1)),
                      min_ev_over_var=("ev_over_var", "min"),
                      share_genes_below_095=("ev_over_var", lambda s: float((s < 0.95).mean())),
                      median_frac_V_neg=("frac_v_neg_V", "median")).reset_index()
sw["approx_mcse"] = sw.median_ev_over_var * np.sqrt(2.0 / (sw.R - 1))
sw["below_095"] = sw.median_ev_over_var < 0.95
sw["within_2se_of_095"] = (sw.median_ev_over_var - 0.95).abs() < 2 * sw.approx_mcse
sw.to_csv(os.path.join(out, "f2_switch_rule.csv"), index=False)
prim = sw[sw.scale.isin(["log1p", "lognorm", "log_income"])]
dec = dict(cells=len(sw), cells_below=int(sw.below_095.sum()), min_median=float(sw.median_ev_over_var.min()),
           cell_of_min=sw.loc[sw.median_ev_over_var.idxmin(), K].astype(str).to_dict(),
           cells_within_2se=int(sw.within_2se_of_095.sum()),
           primary_scales_cells=len(prim), primary_scales_cells_below=int(prim.below_095.sum()),
           verdict_all="switch to V_max" if sw.below_095.any() else "V_w stays primary",
           verdict_primary_scales="switch to V_max" if prim.below_095.any() else "V_w stays primary",
           tasks=sorted(sw.task.unique().tolist()))
json.dump(dec, open(os.path.join(out, "f2_switch_decision.json"), "w"), indent=1)
print(json.dumps(dec, indent=1), flush=True)
# summary over genes
q = lambda p: (lambda s: s.quantile(p))
sm = D.groupby(K + ["arm", "variance"]).agg(G=("G", "first"), genes=("gene", "size"), R=("R", "first"),
                                           median_coverage=("coverage", "median"), q10_coverage=("coverage", q(0.1)),
                                           q90_coverage=("coverage", q(0.9)), median_width=("median_width", "median"),
                                           median_rmse=("rmse", "median"), median_frac_no_interval=("frac_no_interval", "median"),
                                           median_ev_over_var=("ev_over_var", "median")).reset_index()
sm.to_csv(os.path.join(out, "f2_regimeA_summary.csv"), index=False)
a = D[(D.arm == "fix1")][K + ["gene", "median_width", "mean_width"]]
b = D[(D.arm == "classical")][K + ["gene", "median_width", "mean_width"]]
m = a.merge(b, on=K + ["gene"], suffixes=("_fix1", "_cl"))
m["wider_median"] = m.median_width_fix1 > m.median_width_cl
m["wider_mean"] = m.mean_width_fix1 > m.mean_width_cl
cost = m.groupby(K).agg(genes=("gene", "size"), share_fix1_wider_median=("wider_median", "mean"),
                        share_fix1_wider_mean=("wider_mean", "mean"),
                        median_width_ratio=("median_width_fix1", "median")).reset_index()
cost["median_width_ratio"] = m.assign(r=m.median_width_fix1 / m.median_width_cl).groupby(K).r.median().to_numpy()
cost.to_csv(os.path.join(out, "f2_fix1_cost.csv"), index=False)
print(f"units {len(units)}, rows {len(D)}, summary rows {len(sm)}")
