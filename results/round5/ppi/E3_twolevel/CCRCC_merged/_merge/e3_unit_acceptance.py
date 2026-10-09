"""E3 unit acceptance for CCRCC_merged (local, result files only)."""
import glob, os, numpy as np, pandas as pd
R = "/Users/nicolaszhang/hest-1k/HEST-1k-replication-PPI"
D = f"{R}/results/round5/ppi/E3_twolevel/CCRCC_merged"
V = "CCRCC_merged"
rows = []
q = pd.read_csv(f"{R}/results/round4/ppi/Q4_tables/q4_main_table.csv")
q = q[(q.vtag == V) & (q.population == "donor") & (q.target == "design")]
q4a = pd.read_csv(f"{R}/results/round4/ppi/Q4a_recompute/q4a_table61.csv")
q4a = q4a[(q4a.vtag == V) & (q4a.population == "donor") & (q4a.target == "design") & (q4a.lambda_rule == "c_crossfit_design")]
ACC_ARMS = ["hoptimus0", "uni_v2", "resnet50", "permuted"]
Q4ARM = {"hoptimus0": "hoptimus0", "uni_v2": "uni_v2", "resnet50": "resnet50", "permuted": "permuted"}
detail = []
# ---- acceptance 1(i): identity
for arm in ACC_ARMS:
    ai = pd.read_csv(f"{D}/{arm}__accept/e3_accept_identity__{V}__{arm}.csv")
    rows.append(dict(check="1i_identity", arm=arm, subset="all", n=len(ai), metric="max_abs_theta", worst=ai.max_abs_theta.max(), tol=np.nan))
    rows.append(dict(check="1i_identity", arm=arm, subset="all", n=len(ai), metric="max_rel_var", worst=ai.max_rel_var.max(), tol=np.nan))
    for ck, s in ai.groupby("check"):
        rows.append(dict(check="1i_identity", arm=arm, subset=ck, n=len(s), metric="max_abs_theta", worst=s.max_abs_theta.max(), tol=np.nan))
        rows.append(dict(check="1i_identity", arm=arm, subset=ck, n=len(s), metric="max_rel_var", worst=s.max_rel_var.max(), tol=np.nan))
# ---- acceptance 1(ii)
def rel(a, b):
    return (a - b).abs() / b.abs().clip(lower=1e-300)
for arm in ACC_ARMS:
    a = pd.read_csv(f"{D}/{arm}__accept/e3_accept__{V}__{arm}.csv")
    qa = q[(q.arm == Q4ARM[arm])]
    sets = {}
    A = a[(a.regime == "A") & (a.budget == 2400) & (a.estimator == "r4_ppi") & (a.interval == "textbook_t|fpc|lin")].copy()
    qq = qa[(qa.regime == "A") & (qa.budget == 2400) & (qa.lambda_rule == "c_crossfit_design") & (qa.interval == "textbook_t|fpc|lin") & (qa.role == "final_design")]
    sets["A_m2400/nL"] = (A.merge(qq, on=["estimand", "n_L"], suffixes=("", "_q4")), None)
    Aall = a[(a.regime == "A") & (a.m.astype(str) == "all") & (a.interval == "textbook_t|fpc|lin")].copy()
    qq2 = q4a[(q4a.arm == Q4ARM[arm]) & (q4a.interval == "textbook_t|fpc|lin")]
    sets["A_m_all"] = (Aall.merge(qq2, on=["estimand", "n_L"], suffixes=("", "_q4")), None)
    B = a[(a.regime == "B") & (a.estimator == "r4_ppi") & (a.interval == "regB_t")].copy()
    qq3 = qa[(qa.regime == "B") & (qa.budget == 2400) & (qa.role == "regimeB_c_crossfit") & (qa.interval == "regB_t")]
    sets["B_2400"] = (B.merge(qq3, on=["estimand"], suffixes=("", "_q4")), None)
    for name, (mg, _) in sets.items():
        mg = mg.copy()
        mg["d_cov"] = (mg.coverage_median - mg.coverage_median_q4).abs()
        mg["r_emp"] = rel(mg.emp_var_median, mg.emp_var_median_q4)
        mg["r_est"] = rel(mg.est_var_over_emp_var_median, mg.est_var_over_emp_var_median_q4)
        mg["arm_"] = arm; mg["set"] = name
        detail.append(mg[["arm_", "set", "estimand", "n_L", "m", "estimator", "coverage_median", "coverage_median_q4", "d_cov", "r_emp", "r_est"]])
        for met, tol in (("d_cov", 0.005), ("r_emp", 1e-5), ("r_est", 1e-5)):
            rows.append(dict(check="1ii_vs_round4", arm=arm, subset=name, n=len(mg), metric={"d_cov": "max_abs_diff_coverage_median", "r_emp": "max_rel_diff_emp_var_median", "r_est": "max_rel_diff_est_var_over_emp_var_median"}[met],
                             worst=mg[met].max(), tol=tol))
det = pd.concat(detail); det.to_csv(f"{D}/_merge/accept1ii_detail.csv", index=False)
# ---- acceptance 3
for arm in ("constant", "donor_constant"):
    fs = sorted(glob.glob(f"{D}/{arm}__*/e3_*_formC_identity__{V}__{arm}.csv"))
    mt, mv, nn = 0, 0, 0
    for f in fs:
        d = pd.read_csv(f); nn += len(d)
        rows.append(dict(check="3_formC_identity", arm=arm, subset=os.path.basename(f).split("_formC")[0], n=len(d), metric="max_abs_theta_Cppi_minus_Ccl", worst=d.max_abs_theta_Cppi_minus_Ccl.max(), tol=1e-10))
        rows.append(dict(check="3_formC_identity", arm=arm, subset=os.path.basename(f).split("_formC")[0], n=len(d), metric="max_abs_var_Cppi_minus_Ccl", worst=d.max_abs_var_Cppi_minus_Ccl.max(), tol=1e-10))
        mt = max(mt, d.max_abs_theta_Cppi_minus_Ccl.max()); mv = max(mv, d.max_abs_var_Cppi_minus_Ccl.max())
    rows.append(dict(check="3_formC_identity", arm=arm, subset=f"ALL ({len(fs)} files)", n=nn, metric="max_of_both", worst=max(mt, mv), tol=1e-10))
# ---- acceptance 4
for arm in ("constant", "donor_constant"):
    g = pd.read_csv(f"{D}/{arm}__regb/e3_regb_genes__{V}__{arm}.csv.gz")
    g = g[(g.interval == "regB_t") & (g.m.astype(float) >= 20)]
    p = g[g.estimator == "P_ppi"].set_index(["estimand", "m", "gene"]).width
    c = g[g.estimator == "P_classical"].set_index(["estimand", "m", "gene"]).width
    r = (p / c).rename("ratio").reset_index()
    med = r.groupby(["estimand", "m"]).ratio.agg(["median", "count"]).reset_index()
    med["arm"] = arm
    med.to_csv(f"{D}/_merge/accept4_width_ratio__{arm}.csv", index=False)
    for est, s in med.groupby("estimand"):
        lo, hi = s["median"].min(), s["median"].max()
        ok = bool(lo >= 0.97 and hi <= 1.05)
        rows.append(dict(check="4_regb_width_ratio", arm=arm, subset=est, n=len(s), metric="min_median_ratio_m>=20", worst=lo, tol=0.97))
        rows.append(dict(check="4_regb_width_ratio", arm=arm, subset=est, n=len(s), metric="max_median_ratio_m>=20", worst=hi, tol=1.05))
out = pd.DataFrame(rows)
def verdict(r):
    if r.check == "1ii_vs_round4": return "pass" if r.worst <= r.tol else "FAIL"
    if r.check == "3_formC_identity": return "pass" if r.worst <= r.tol else "FAIL"
    if r.check == "4_regb_width_ratio" and r.arm == "constant":
        return "pass" if (r.worst >= 0.97 if r.metric.startswith("min") else r.worst <= 1.05) else "FAIL"
    if r.check == "4_regb_width_ratio": return "no band (reported)"
    return "report (expected <=~1e-12)"
out["verdict"] = out.apply(verdict, axis=1)
out.to_csv(f"{R}/results/round5/ppi/E3_twolevel/CCRCC_merged/e3_unit_acceptance__CCRCC_merged.csv", index=False)
pd.set_option("display.width", 250, "display.max_rows", 500)
print(out[~out.subset.str.startswith("e3_", na=False) | (out.check != "3_formC_identity")].to_string())
