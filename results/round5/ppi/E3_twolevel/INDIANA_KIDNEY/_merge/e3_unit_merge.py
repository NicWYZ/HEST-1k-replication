"""E3 unit acceptance for INDIANA_KIDNEY: reads result files only. Usage: python e3_unit_merge.py <repo root>"""
import sys, glob, os, warnings, pandas as pd, numpy as np
warnings.filterwarnings("ignore")
R = sys.argv[1]; V = "INDIANA_KIDNEY"
D = f"{R}/results/round5/ppi/E3_twolevel/{V}"
acc = pd.concat([pd.read_csv(f) for f in glob.glob(f"{D}/*__accept/e3_accept__*.csv")])
idn = pd.concat([pd.read_csv(f) for f in glob.glob(f"{D}/*__accept/e3_accept_identity__*.csv")])
q = pd.read_csv(f"{R}/results/round4/ppi/Q4_tables/q4_main_table.csv"); q = q[q.vtag == V].copy()
q["m"] = q.m.astype(str); q["n_L"] = q.n_L.astype(int)
key = ["arm", "estimand", "population", "target", "n_L", "interval"]
vals = ["coverage_median", "emp_var_median", "est_var_over_emp_var_median"]
def cmp(s, qs, on):
    s = s.copy(); s["m"] = s.m.astype(str).str.replace(r"\.0$", "", regex=True)
    mm = s.merge(qs[on + vals].drop_duplicates(), on=on, suffixes=("", "_q4"), how="left", indicator=True)
    mm["dcov"] = (mm.coverage_median - mm.coverage_median_q4).abs()
    mm["drel_ev"] = (mm.emp_var_median / mm.emp_var_median_q4 - 1).abs()
    mm["drel_ratio"] = (mm.est_var_over_emp_var_median / mm.est_var_over_emp_var_median_q4 - 1).abs()
    return mm
fd = q[(q.role == "final_design") & (q.regime == "A") & (q.lambda_rule == "c_crossfit_design")]
sets = [("accept2_regimeA_m2400", acc[(acc.regime == "A") & (acc.budget == 2400) & (acc.estimator == "r4_ppi")], fd[fd.budget == 2400], key + ["m"]),
        ("accept2_regimeA_mall", acc[(acc.regime == "A") & acc.budget.isna()], fd[fd.m == "all"], key + ["m"]),
        ("accept2_regimeB_2400", acc[acc.regime == "B"], q[(q.role == "regimeB_c_crossfit") & (q.regime == "B") & (q.budget == 2400)], key)]
out = []
for i, (lab, s, qs, on) in enumerate(sets):
    mm = cmp(s, qs, on)
    for est, g in mm.groupby("estimator"):
        out.append(dict(check=lab, estimator=est, n_rows=len(g), n_matched=int((g._merge == "both").sum()),
                        worst_abs_coverage_diff=g.dcov.max(), worst_rel_emp_var_diff=g.drel_ev.max(),
                        worst_rel_est_over_emp_diff=g.drel_ratio.max(), tolerance="cov 0.005, rel 1e-5",
                        pass_=bool(g.dcov.max() <= 0.005 and g.drel_ev.max() <= 1e-5 and g.drel_ratio.max() <= 1e-5 and (g._merge == "both").all())))
for ch, g in idn.groupby("check"):
    out.append(dict(check="accept1_identity_" + ch, estimator="r4_ppi", n_rows=len(g), n_matched=len(g),
                    worst_abs_coverage_diff=g.max_abs_theta.max(), worst_rel_emp_var_diff=g.max_rel_var.max(),
                    worst_rel_est_over_emp_diff=np.nan, tolerance="theta/var ~1e-12 or smaller", pass_=bool(g.max_abs_theta.max() < 1e-10 and g.max_rel_var.max() < 1e-10)))
fc = pd.concat([pd.read_csv(f).assign(arm=a) for a in ("constant", "donor_constant") for f in glob.glob(f"{D}/{a}__*/e3_*_formC_identity__*.csv")])
for a, g in fc.groupby("arm"):
    out.append(dict(check="accept3_formC_identity", estimator=a, n_rows=len(g), n_matched=len(g),
                    worst_abs_coverage_diff=g.max_abs_theta_Cppi_minus_Ccl.max(), worst_rel_emp_var_diff=g.max_abs_var_Cppi_minus_Ccl.max(),
                    worst_rel_est_over_emp_diff=np.nan, tolerance="<= 1e-10 (cols: theta, var diffs)",
                    pass_=bool(g.max_abs_theta_Cppi_minus_Ccl.max() <= 1e-10 and g.max_abs_var_Cppi_minus_Ccl.max() <= 1e-10)))
for a in ("constant", "donor_constant"):
    g = pd.read_csv(glob.glob(f"{D}/{a}__regb/e3_regb_genes__*.csv.gz")[0]); g = g[pd.to_numeric(g.m) >= 20]
    w = g.pivot_table(index=["estimand", "m", "gene"], columns="estimator", values="width")
    w["ratio"] = w.P_ppi / w.P_classical
    med = w.groupby(level=[0, 1]).ratio.median().reset_index()
    for est, x in med.groupby("estimand"):
        out.append(dict(check="accept4_regB_P_width_ratio", estimator=f"{a}:{est}", n_rows=len(x), n_matched=len(x),
                        worst_abs_coverage_diff=x.ratio.min(), worst_rel_emp_var_diff=x.ratio.max(), worst_rel_est_over_emp_diff=np.nan,
                        tolerance="band 0.97-1.05 (cols: min, max over m>=20 of median-over-genes ratio)" if a == "constant" else "no band (reported)",
                        pass_=bool(x.ratio.min() >= 0.97 and x.ratio.max() <= 1.05) if a == "constant" else np.nan))
res = pd.DataFrame(out)
res.to_csv(f"{D}/e3_unit_acceptance__{V}.csv", index=False)
print(res.to_string())
