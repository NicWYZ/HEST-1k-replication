"""Round 10, track final-runs, F2.4: aggregation of the regime B units (plan, section 5.4).

usage: round10_final_runs_f2_regimeB_aggregate.py <regimeB_root> <configs_dir> <out_dir>
Reads every <regimeB_root>/<unit>/regimeB_genes.parquet and regimeB_summary.json whose unit has a config in
<configs_dir> (smoke left out) and writes
  f2_regimeB_units.csv    units, PROVENANCE status, rows, populations, the cluster-value check maxima, seconds;
  f2_regimeB_summary.csv  per (task, encoder, scale, estimand, m, form): genes, median, 10% and 90% coverage, median of
                          median width, median E(V)/Var, its 10% quantile, median share of no-interval draws, median
                          share of draws with V < 0, median bias over its Monte Carlo standard error;
  f2_regimeB_fix1_vs_ppi.csv per (task, encoder, scale, estimand, m): median coverage and width of the three forms and
                          the median over genes of the per-gene width ratios C_fix1 / C_classical and C_ppi / C_classical;
  f2_regimeB_checks.json  completeness and the largest relative difference between TL.prepare's cluster means and the
                          cluster values of regime A, over every unit.
"""
import glob, json, os, sys
import numpy as np, pandas as pd

root, cfgdir, out = sys.argv[1:4]; os.makedirs(out, exist_ok=True)
want = sorted(os.path.basename(p)[len("f2_regimeB__"):-5] for p in glob.glob(os.path.join(cfgdir, "f2_regimeB__*.json")))
want = [u for u in want if u != "smoke"]
units, frames, cvmax = [], [], 0.0
for u in want:
    d = os.path.join(root, u); pv = os.path.join(d, "PROVENANCE.txt")
    st = next((l.split(":", 1)[1].strip() for l in open(pv) if l.startswith("status:")), "no status") if os.path.exists(pv) else "missing"
    row = dict(unit=u, status=st)
    gp, sp = os.path.join(d, "regimeB_genes.parquet"), os.path.join(d, "regimeB_summary.json")
    if os.path.exists(gp) and os.path.exists(sp):
        s = json.load(open(sp)); x = pd.read_parquet(gp); frames.append(x)
        mx = [v.get("max_rel", np.nan) for p in s.get("populations", []) for v in (p.get("cv_check") or {}).values()]
        nm = [v.get("n_common", 0) == v.get("n_valid_regimeB", -1) for p in s.get("populations", []) for v in (p.get("cv_check") or {}).values() if v.get("n_matched", 1) != 0]
        mx = [m for m in mx if m is not None and np.isfinite(m)]
        cvmax = max([cvmax] + mx)
        row.update(rows=len(x), populations=len(s.get("populations", [])), cv_max_rel=max(mx) if mx else np.nan,
                   cv_donors_all_matched=bool(all(nm)), seconds=sum(p.get("seconds", 0) for p in s.get("populations", [])))
    units.append(row)
U = pd.DataFrame(units); U.to_csv(os.path.join(out, "f2_regimeB_units.csv"), index=False)
D = pd.concat(frames, ignore_index=True)
K = ["task", "encoder", "scale", "estimand", "m"]
D["bias_z"] = D.bias / D.mcse_bias.replace(0, np.nan)
q = lambda p: (lambda s: s.quantile(p))
S = D.groupby(K + ["form"]).agg(G=("G", "first"), genes=("gene", "size"), R=("R", "first"),
                               median_coverage=("coverage", "median"), q10_coverage=("coverage", q(0.1)),
                               q90_coverage=("coverage", q(0.9)), median_width=("median_width", "median"),
                               median_ev_over_var=("ev_over_var", "median"), q10_ev_over_var=("ev_over_var", q(0.1)),
                               median_frac_no_interval=("frac_no_interval", "median"),
                               median_frac_v_neg=("frac_v_neg", "median"), median_bias_z=("bias_z", "median")).reset_index()
S.to_csv(os.path.join(out, "f2_regimeB_summary.csv"), index=False)
w = D.pivot_table(index=K + ["gene"], columns="form", values=["median_width", "coverage"]).reset_index()
w.columns = ["_".join([c for c in col if c]) for col in w.columns]
w["wr_fix1"] = w.median_width_C_fix1 / w.median_width_C_classical
w["wr_ppi"] = w.median_width_C_ppi / w.median_width_C_classical
F = w.groupby(K).agg(genes=("gene", "size"), cov_fix1=("coverage_C_fix1", "median"), cov_ppi=("coverage_C_ppi", "median"),
                     cov_classical=("coverage_C_classical", "median"), median_wr_fix1=("wr_fix1", "median"),
                     median_wr_ppi=("wr_ppi", "median"), share_fix1_wider=("wr_fix1", lambda s: float((s > 1).mean()))).reset_index()
F.to_csv(os.path.join(out, "f2_regimeB_fix1_vs_ppi.csv"), index=False)
chk = dict(units_expected=len(want), units_completed=int((U.status == "COMPLETED").sum()),
           units_not_completed=U[U.status != "COMPLETED"].unit.tolist(), cv_max_rel=cvmax,
           cv_donors_all_matched=bool(U.get("cv_donors_all_matched", pd.Series([True])).fillna(True).all()),
           duplicate_rows=int(D.duplicated(subset=K + ["form", "gene"]).sum()), rows=len(D))
json.dump(chk, open(os.path.join(out, "f2_regimeB_checks.json"), "w"), indent=1)
print(json.dumps(chk, indent=1))
