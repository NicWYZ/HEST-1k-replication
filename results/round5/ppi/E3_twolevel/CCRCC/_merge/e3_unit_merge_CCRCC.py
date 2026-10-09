"""E3 CCRCC unit: acceptance 1-4 from the harvested result files (local, result files only)."""
import glob, os, json
import numpy as np, pandas as pd
R = "/Users/nicolaszhang/hest-1k/HEST-1k-replication-PPI"
D = R + "/results/round5/ppi/E3_twolevel/CCRCC"
ARMS = ["hoptimus0", "uni_v2", "resnet50", "permuted"]
rows = []
def add(check, arm, what, value, tol, n, note=""):
    rows.append(dict(check=check, arm=arm, quantity=what, worst=value, tolerance=tol,
                     passed=(bool(value <= tol) if (tol is not None and np.isfinite(value)) else None), n=n, note=note))

# ---- acceptance 1(i): identity
q = pd.read_csv(R + "/results/round4/ppi/Q4_tables/q4_main_table.csv")
q = q[(q.vtag == "CCRCC") & (q.population == "donor") & (q.target == "design")].copy()
q["m"] = q["m"].astype(str).str.replace(r"\.0$", "", regex=True)
q4a = pd.read_csv(R + "/results/round4/ppi/Q4a_recompute/q4a_table61.csv")
cmp_all = []
for arm in ARMS:
    idt = pd.read_csv(f"{D}/{arm}__accept/e3_accept_identity__CCRCC__{arm}.csv")
    for chk, g in idt.groupby("check"):
        add("1i_identity", arm, f"{chk}: max_abs_theta", g.max_abs_theta.max(), 1e-10, len(g))
        add("1i_identity", arm, f"{chk}: max_rel_var", g.max_rel_var.max(), 1e-10, len(g),
            note=f"NaN rows: {int(g.max_rel_var.isna().sum())}")
    acc = pd.read_csv(f"{D}/{arm}__accept/e3_accept__CCRCC__{arm}.csv")
    acc["m"] = acc["m"].astype(str).str.replace(r"\.0$", "", regex=True)
    qa = q[(q.arm == arm)]
    def pick(df, **kw):
        s = df
        for k, v in kw.items(): s = s[s[k] == v] if not isinstance(v, (list, tuple)) else s[s[k].isin(v)]
        return s
    qrefs = {
      "A_budget2400": pick(qa, role="final_design", regime="A", budget=2400.0, lambda_rule="c_crossfit_design",
                           interval=["textbook_t|fpc", "textbook_t|fpc|lin"]),
      "A_all": pick(qa, role="final_design", regime="A", m="all", lambda_rule="c_crossfit_design",
                    interval=["textbook_t|fpc", "textbook_t|fpc|lin"]),
      "B_budget2400": pick(qa, role="regimeB_c_crossfit", regime="B", budget=2400.0, interval="regB_t"),
    }
    sel = {
      "A_budget2400": acc[(acc.regime == "A") & (acc.m != "all") & (acc.estimator == "r4_ppi")],
      "A_all": acc[(acc.regime == "A") & (acc.m == "all")],
      "B_budget2400": acc[(acc.regime == "B") & (acc.estimator == "r4_ppi")],
    }
    for k, a in sel.items():
        r = qrefs[k]
        for est_name, aa in (a.groupby("estimator") if k == "A_all" else [("r4_ppi", a)]):
            mm = aa.merge(r, on=["estimand", "n_L"] + ([] if k != "A_budget2400" else ["m"]), suffixes=("", "_q4"))
            if k == "A_all": pass
            mm = mm.assign(estimator_r5=est_name)
            nexp = len(aa)
            cov = (mm.coverage_median - mm.coverage_median_q4).abs()
            ev = (mm.emp_var_median / mm.emp_var_median_q4 - 1).abs()
            er = (mm.est_var_over_emp_var_median / mm.est_var_over_emp_var_median_q4 - 1).abs()
            note = f"matched {len(mm)}/{nexp}"
            add("1ii_vs_q4", arm, f"{k} [{est_name}]: max abs diff coverage_median", cov.max(), 0.005, len(mm), note)
            add("1ii_vs_q4", arm, f"{k} [{est_name}]: max rel diff emp_var_median", ev.max(), 1e-5, len(mm), note)
            add("1ii_vs_q4", arm, f"{k} [{est_name}]: max rel diff est_var_over_emp_var_median", er.max(), 1e-5, len(mm), note)
            cmp_all.append(mm.assign(set=k, d_cov=cov, rel_emp=ev, rel_ratio=er)[
                ["arm", "set", "estimator_r5", "estimand", "n_L", "m", "interval", "interval_q4" if "interval_q4" in mm else "interval",
                 "coverage_median", "coverage_median_q4", "emp_var_median", "emp_var_median_q4",
                 "est_var_over_emp_var_median", "est_var_over_emp_var_median_q4", "d_cov", "rel_emp", "rel_ratio"]])
pd.concat(cmp_all).to_csv(D + "/_merge/e3_accept_vs_q4_rows__CCRCC.csv", index=False)

# ---- acceptance 3: form C identity of the constant arms
for arm in ("constant", "donor_constant"):
    fs = sorted(glob.glob(f"{D}/{arm}__*/e3_*_formC_identity__CCRCC__{arm}.csv"))
    d = pd.concat([pd.read_csv(f).assign(f=os.path.basename(f)) for f in fs])
    for col in ("max_abs_theta_Cppi_minus_Ccl", "max_abs_var_Cppi_minus_Ccl"):
        add("3_formC_identity", arm, col, d[col].max(), 1e-10, len(d),
            note=f"files {len(fs)}; NaN {int(d[col].isna().sum())}; by estimand max: " +
                 json.dumps({k: float(v) for k, v in d.groupby('estimand')[col].max().items()}))

# ---- acceptance 4: regb, form P width ratio P_ppi / P_classical
ratio_rows = []
for arm in ("constant", "donor_constant"):
    g = pd.read_csv(f"{D}/{arm}__regb/e3_regb_genes__CCRCC__{arm}.csv.gz")
    gc = [c for c in g.columns if "width" in c]
    wc = "width"
    g = g[g.interval == "regB_t"]
    g["mnum"] = pd.to_numeric(g["m"], errors="coerce")
    g = g[g.mnum >= 20]
    p = g[g.estimator == "P_ppi"].set_index(["estimand", "mnum", "gene"])[wc]
    c = g[g.estimator == "P_classical"].set_index(["estimand", "mnum", "gene"])[wc]
    rr = (p / c).rename("ratio").reset_index()
    med = rr.groupby(["estimand", "mnum"]).ratio.median().reset_index()
    med["arm"] = arm; med["width_col"] = wc; ratio_rows.append(med)
    for est, s in med.groupby("estimand"):
        lo, hi = s.ratio.min(), s.ratio.max()
        rows.append(dict(check="4_regb_width_ratio_P", arm=arm, quantity=f"{est}: median-over-genes P_ppi/P_classical, m>=20, min..max over m ({','.join(str(int(x)) for x in s.mnum)})",
                         worst=(max(abs(lo - 1), abs(hi - 1)) if False else (hi if hi - 1 > 1 - lo else lo)), tolerance="0.97..1.05" if arm == "constant" else "no band",
                         passed=(bool(lo >= 0.97 and hi <= 1.05) if arm == "constant" else None), n=len(s),
                         note=f"min {lo:.4f} max {hi:.4f}"))
rat = pd.concat(ratio_rows); rat.to_csv(D + "/_merge/e3_regb_widthratio__CCRCC.csv", index=False)
out = pd.DataFrame(rows); out.to_csv(D + "/e3_unit_acceptance__CCRCC.csv", index=False)
print(out.groupby(["check"]).passed.agg(lambda s: (s == True).sum()).to_string())
print(out[out.passed == False].to_string())
