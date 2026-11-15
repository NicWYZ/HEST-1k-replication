"""Round 10, track final-runs, F2.1: aggregation of the limits-arm units (plan, sections 5.2 and 5.8).

usage: round10_final_runs_f2_limits_aggregate.py <limits_root> <regimeA_aggregate_dir> <configs_dir> <out_dir>
Reads every <limits_root>/<unit>/limits_cells.parquet and limits_diag.parquet whose unit has a config in
<configs_dir> (the smoke unit is left out), and writes
  f2_limits_units.csv     the units read, their PROVENANCE status, rows, populations, check maxima and seconds;
  f2_limits_checks.json   completeness (every unit present and COMPLETED; the populations and n_L of the limits arms
                          equal those of regime A for every task, encoder, scale and estimand) and the controls'
                          maxima over all units (rule none against the classical estimator, a_b1 against b_cluster);
  f2_limits_summary.csv   per (task, encoder, scale, estimand, n, arm, variance) the gene summaries of regime A's
                          aggregation (median and 10%/90% coverage, median of median width, median RMSE, median share
                          of no-interval draws, median E(V)/Var);
  f2_limits_vs_regimeA.csv per (task, encoder, scale, estimand, n) the median coverage and median width of each limits
                          arm beside regime A's classical, fix1 and xf2_r5 (V_w) rows, and each arm's median width
                          divided by classical's (median over genes of the per-gene ratio, limits and regime A arms on
                          their own draws, so the ratio compares like designs, not like draws);
  f2_limits_diag.csv      per (task, encoder, scale, estimand, n, arm) the median over genes of the coefficient's mean
                          and of its share at 0 and at 1 (Kluger: Omega), and Kluger's bootstrap drop share.
"""
import glob, json, os, sys
import numpy as np, pandas as pd

root, agg, cfgdir, out = sys.argv[1:5]; os.makedirs(out, exist_ok=True)
K = ["task", "encoder", "scale", "estimand", "n"]
want = sorted(os.path.basename(p)[len("f2_limits__"):-5] for p in glob.glob(os.path.join(cfgdir, "f2_limits__*.json")))
want = [u for u in want if u != "smoke"]
units, frames, dframes, chk = [], [], [], {}
for u in want:
    d = os.path.join(root, u)
    st = "missing"
    pv = os.path.join(d, "PROVENANCE.txt")
    if os.path.exists(pv):
        st = next((l.split(":", 1)[1].strip() for l in open(pv) if l.startswith("status:")), "no status line")
    row = dict(unit=u, status=st)
    cp, sp = os.path.join(d, "limits_cells.parquet"), os.path.join(d, "limits_summary.json")
    if os.path.exists(cp) and os.path.exists(sp):
        s = json.load(open(sp)); x = pd.read_parquet(cp); frames.append(x)
        dframes.append(pd.read_parquet(os.path.join(d, "limits_diag.parquet")))
        for k, v in (s.get("checks_max") or {}).items():
            chk[k] = max(chk.get(k, 0.0), v)
        row.update(rows=len(x), n_populations=s.get("n_populations"), n_skipped=s.get("n_skipped"),
                   checks_failed=json.dumps(s.get("checks_failed")), seconds=s.get("seconds"))
    units.append(row)
U = pd.DataFrame(units); U.to_csv(os.path.join(out, "f2_limits_units.csv"), index=False)
D = pd.concat(frames, ignore_index=True); DG = pd.concat(dframes, ignore_index=True)
RA = pd.read_csv(os.path.join(agg, "f2_regimeA_summary.csv.gz" if os.path.exists(os.path.join(agg, "f2_regimeA_summary.csv.gz")) else os.path.join(agg, "f2_regimeA_summary.csv")))
# completeness against regime A
cl = RA[(RA.arm == "classical") & (RA.variance == "fpc")][K + ["genes"]]
li = D[(D.arm == "r4_none")].groupby(K).gene.nunique().rename("genes_limits").reset_index()
cmp_ = cl.merge(li, on=K, how="outer", indicator=True)
dup = int(D.duplicated(subset=K + ["gene", "arm", "variance"]).sum())
checks = dict(units_expected=len(want), units_completed=int((U.status == "COMPLETED").sum()),
              units_not_completed=U[U.status != "COMPLETED"].unit.tolist(),
              cells_regimeA=int(len(cl)), cells_limits=int(len(li)),
              cells_only_regimeA=int((cmp_._merge == "left_only").sum()), cells_only_limits=int((cmp_._merge == "right_only").sum()),
              cells_gene_count_differs=int((cmp_.dropna().genes != cmp_.dropna().genes_limits).sum()),
              duplicate_rows=dup, controls_max=chk)
json.dump(checks, open(os.path.join(out, "f2_limits_checks.json"), "w"), indent=1)
print(json.dumps(checks, indent=1), flush=True)
q = lambda p: (lambda s: s.quantile(p))
sm = D.groupby(K + ["arm", "variance"]).agg(G=("G", "first"), genes=("gene", "size"), R=("R", "first"),
                                           median_coverage=("coverage", "median"), q10_coverage=("coverage", q(0.1)),
                                           q90_coverage=("coverage", q(0.9)), median_width=("median_width", "median"),
                                           median_rmse=("rmse", "median"), median_frac_no_interval=("frac_no_interval", "median"),
                                           median_ev_over_var=("ev_over_var", "median")).reset_index()
sm.to_csv(os.path.join(out, "f2_limits_summary.csv"), index=False)
# beside regime A: per-gene width ratios to classical within each regime
base = D[(D.arm == "r4_none")][K + ["gene", "median_width"]].rename(columns={"median_width": "w_cl_limits"})
x = D.merge(base, on=K + ["gene"]); x["wr"] = x.median_width / x.w_cl_limits
lw = x.groupby(K + ["arm", "variance"]).agg(median_coverage=("coverage", "median"), median_width=("median_width", "median"),
                                           median_width_ratio_to_classical=("wr", "median")).reset_index()
lw["label"] = lw.arm + "|" + lw.variance
wide = lw.pivot_table(index=K, columns="label", values=["median_coverage", "median_width_ratio_to_classical"])
wide.columns = [f"{a}__{b}" for a, b in wide.columns]
ra = RA[((RA.arm == "classical") & (RA.variance == "fpc")) | ((RA.arm == "fix1") & (RA.variance == "fpc")) |
        ((RA.arm == "xf2_r5") & (RA.variance == "V_w"))].copy()
ra["label"] = "regimeA_" + ra.arm + "|" + ra.variance
raw = ra.pivot_table(index=K, columns="label", values=["median_coverage", "median_width"])
raw.columns = [f"{a}__{b}" for a, b in raw.columns]
both = wide.join(raw, how="left").reset_index()
both.to_csv(os.path.join(out, "f2_limits_vs_regimeA.csv"), index=False)
dg = DG.groupby(K + ["arm"]).agg(genes=("gene", "size"), median_lam_mean=("lam_mean", "median"),
                                 median_frac_lam0=("frac_lam0", "median"), median_frac_lam1=("frac_lam1", "median"),
                                 median_boot_drop=("boot_drop_mean", "median")).reset_index()
dg.to_csv(os.path.join(out, "f2_limits_diag.csv"), index=False)
print(f"units {len(U)}, rows {len(D)}, summary rows {len(sm)}, beside rows {len(both)}")
