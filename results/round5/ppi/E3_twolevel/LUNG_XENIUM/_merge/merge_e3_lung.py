
import pandas as pd, numpy as np, glob, os, sys
R = "/Users/nicolaszhang/hest-1k/HEST-1k-replication-PPI"
U = f"{R}/results/round5/ppi/E3_twolevel/LUNG_XENIUM"
V = "LUNG_XENIUM"
ARMS = ["hoptimus0", "uni_v2", "resnet50", "permuted", "constant", "donor_constant"]
rows = []
def add(check, arm, item, value, tol, passed, note=""):
    rows.append(dict(check=check, arm=arm, item=item, value=value, tolerance=tol, passed=passed, note=note))
# ---- acceptance 1(i)
for arm in ARMS[:4]:
    I = pd.read_csv(f"{U}/{arm}__accept/e3_accept_identity__{V}__{arm}.csv")
    for chk, g in I.groupby("check"):
        add("1i_identity", arm, chk + "|max_abs_theta", g.max_abs_theta.max(), 1e-10, bool(g.max_abs_theta.max() <= 1e-10), f"n={len(g)}")
        add("1i_identity", arm, chk + "|max_rel_var", g.max_rel_var.max(), 1e-10, bool(g.max_rel_var.max() <= 1e-10), f"n={len(g)}")
# ---- acceptance 1(ii)
q = pd.read_csv(f"{R}/results/round4/ppi/Q4_tables/q4_main_table.csv", low_memory=False)
q = q[q.vtag == V].copy()
q["m"] = q["m"].astype(str); q["n_L"] = q["n_L"].astype(int)
q4a = pd.read_csv(f"{R}/results/round4/ppi/Q4a_recompute/q4a_table61.csv", low_memory=False)
q4a = q4a[q4a.vtag == V]
detail = []
def cmp(arm, A, label, ref_sel):
    for _, r in A.iterrows():
        ref = ref_sel(r)
        if len(ref) > 1 and (ref.budget == 2400).any() and label == "A_m2400nL":
            ref = ref[ref.budget == 2400]
        if len(ref) > 1 and ref[["coverage_median", "emp_var_median", "est_var_over_emp_var_median"]].drop_duplicates().shape[0] == 1:
            ref = ref.iloc[:1]   # same cell listed in two q4 blocks (grid and A_budget), identical values
        if len(ref) != 1:
            detail.append(dict(arm=arm, group=label, estimand=r.estimand, n_L=r.n_L, m=r.m, estimator=r.estimator, status=f"ref_rows={len(ref)}"))
            continue
        z = ref.iloc[0]
        detail.append(dict(arm=arm, group=label, estimand=r.estimand, n_L=int(r.n_L), m=r.m, estimator=r.estimator, status="ok",
            abs_d_cov=abs(r.coverage_median - z.coverage_median),
            rel_d_empvar=abs(r.emp_var_median / z.emp_var_median - 1),
            rel_d_ratio=abs(r.est_var_over_emp_var_median / z.est_var_over_emp_var_median - 1)))
for arm in ARMS[:4]:
    A = pd.read_csv(f"{U}/{arm}__accept/e3_accept__{V}__{arm}.csv"); A["m"] = A["m"].astype(str)
    qa = q[(q.arm == arm)]
    Aa = A[(A.regime == "A") & (A.m != "all") & (A.estimator == "r4_ppi")]
    cmp(arm, Aa, "A_m2400nL", lambda r: qa[(qa.role == "final_design") & (qa.estimand == r.estimand) & (qa.population == "donor") & (qa.target == "design") & (qa.regime == "A") & (qa.n_L == int(r.n_L)) & (qa.m == str(int(2400 / r.n_L))) & (qa.lambda_rule == "c_crossfit_design") & (qa.interval == "textbook_t|fpc|lin")])
    Ab = A[(A.regime == "A") & (A.m == "all")]
    cmp(arm, Ab, "A_all", lambda r: qa[(qa.role == "final_design") & (qa.estimand == r.estimand) & (qa.population == "donor") & (qa.target == "design") & (qa.regime == "A") & (qa.n_L == int(r.n_L)) & (qa.m == "all") & (qa.lambda_rule == "c_crossfit_design") & (qa.interval == "textbook_t|fpc|lin")])
    Ac = A[A.regime == "B"]
    cmp(arm, Ac, "B_2400", lambda r: qa[(qa.role == "regimeB_c_crossfit") & (qa.estimand == r.estimand) & (qa.population == "donor") & (qa.target == "design") & (qa.regime == "B") & (qa.budget == 2400) & (qa.lambda_rule == "c_crossfit") & (qa.interval == "regB_t")])
D = pd.DataFrame(detail)
D.to_csv(f"{U}/_merge/accept_vs_q4_detail.csv", index=False)
ok = D[D.status == "ok"]
for (arm, grp), g in ok.groupby(["arm", "group"]):
    add("1ii_vs_q4", arm, grp + "|max_abs_coverage_median", g.abs_d_cov.max(), 0.005, bool(g.abs_d_cov.max() <= 0.005 + 1e-9), f"n={len(g)}")
    add("1ii_vs_q4", arm, grp + "|max_rel_emp_var_median", g.rel_d_empvar.max(), 1e-5, bool(g.rel_d_empvar.max() <= 1e-5), f"n={len(g)}")
    add("1ii_vs_q4", arm, grp + "|max_rel_est_var_over_emp_var_median", g.rel_d_ratio.max(), 1e-5, bool(g.rel_d_ratio.max() <= 1e-5), f"n={len(g)}")
bad = D[D.status != "ok"]
if len(bad): add("1ii_vs_q4", "all", "unmatched_rows", len(bad), 0, False, "see accept_vs_q4_detail.csv")
# ---- acceptance 3
for arm in ("constant", "donor_constant"):
    fs = sorted(glob.glob(f"{U}/{arm}__*/e3_*_formC_identity__{V}__{arm}.csv"))
    t = v = 0.0; n = 0
    for f in fs:
        F = pd.read_csv(f); n += len(F)
        t = max(t, F.max_abs_theta_Cppi_minus_Ccl.max()); v = max(v, F.max_abs_var_Cppi_minus_Ccl.max())
    add("3_formC_identity", arm, "max_abs_theta_Cppi_minus_Ccl", t, 1e-10, bool(t <= 1e-10), f"files={len(fs)} rows={n}")
    add("3_formC_identity", arm, "max_abs_var_Cppi_minus_Ccl", v, 1e-10, bool(v <= 1e-10), f"files={len(fs)} rows={n}")
# ---- acceptance 4
tabs = []
for arm in ("constant", "donor_constant"):
    f = f"{U}/{arm}__regb/e3_regb_genes__{V}__{arm}.csv.gz"
    if not os.path.exists(f): continue
    g = pd.read_csv(f)
    g = g[g.interval == "regB_t"]
    w = g.pivot_table(index=["estimand", "m", "gene"], columns="estimator", values="width").reset_index()
    w["ratio"] = w["P_ppi"] / w["P_classical"]
    s = w[w.m.astype(float) >= 20].groupby(["estimand", "m"]).ratio.agg(median_ratio="median", n_genes="count", min_gene="min", max_gene="max").reset_index()
    s.insert(0, "arm", arm); tabs.append(s)
    for est, gg in s.groupby("estimand"):
        for _, r in gg.iterrows():
            band = arm == "constant"
            add("4_regB_width_ratio_P", arm, f"{est}|m={int(float(r.m))}|median_P_ppi_over_P_classical", r.median_ratio, "0.97-1.05" if band else "none",
                (0.97 <= r.median_ratio <= 1.05) if band else None, f"n_genes={int(r.n_genes)}")
pd.concat(tabs).to_csv(f"{U}/_merge/acc4_width_ratio_P.csv", index=False)
out = pd.DataFrame(rows)
out.to_csv(f"{U}/e3_unit_acceptance__{V}.csv", index=False)
pd.set_option("display.width", 250, "display.max_rows", 500, "display.max_colwidth", 60)
print(out.to_string())
