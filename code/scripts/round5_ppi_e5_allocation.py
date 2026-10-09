"""Round 5 PPI, interval 3, E5 item 2: allocation for form C and theta3 (memo E4 decisions section 5).

One row per task, encoder and n_L, computed locally from committed E3 files:
  1 - R2_w, 1 - R2_c   medians over genes of e3_components.csv (form C, theta3)
  m_star               classical m* at c_d/c_s = 100 from the components (median over genes of
                       e3_components.csv mstar_cd100, form C)
  rho_c(n_L)           ratio of median-over-genes empirical variances of C_ppi to C_classical at every
                       unit labelled (m = all) in e3_masking_grid.csv (design target, interval
                       textbook_t|fpc|lin|xf; the point estimates do not depend on the interval)
  m_star_PP(n_L)       m_star * sqrt((1 - R2_w) / rho_c(n_L))
  fitted check         medians over genes of m_star_emp_cd100 for C_classical and C_ppi in
                       e3_components_fitted.csv, and their ratio
Writes results/round5/ppi/E5_joint/e5_allocation.csv.
"""
import numpy as np
import pandas as pd

D = "results/round5/ppi/E3_twolevel"
OUT = "results/round5/ppi/E5_joint/e5_allocation.csv"
ENC = {"CCRCC": ("hoptimus0", "uni_v2", "resnet50"), "CCRCC_merged": ("hoptimus0", "uni_v2", "resnet50"),
       "INDIANA_KIDNEY": ("hoptimus0", "uni_v2", "resnet50"), "LUNG_XENIUM": ("hoptimus0", "uni_v2", "resnet50"),
       "ACS_STATES": ("package",), "ACS_CA_PUMA": ("package",)}


def main():
    comp = pd.read_csv(f"{D}/e3_components.csv")
    comp = comp[(comp["form"] == "C") & (comp["estimand"] == "theta3")]
    fit = pd.read_csv(f"{D}/e3_components_fitted.csv")
    fit = fit[fit["estimand"] == "theta3"]
    mg = pd.read_csv(f"{D}/e3_masking_grid.csv", low_memory=False)
    mg = mg[(mg["estimand"] == "theta3") & (mg["m"].astype(str) == "all") & (mg["interval"] == "textbook_t|fpc|lin|xf")
            & (mg["target"] == "design") & mg["estimator"].isin(["C_ppi", "C_classical"])]
    rows = []
    for vt, arms in ENC.items():
        for arm in arms:
            c = comp[(comp["vtag"] == vt) & (comp["arm"] == arm)]
            f = fit[(fit["vtag"] == vt) & (fit["arm"] == arm)]
            fc = f[f["estimator"] == "C_classical"]["m_star_emp_cd100"].median()
            fp = f[f["estimator"] == "C_ppi"]["m_star_emp_cd100"].median()
            ms = c["mstar_cd100"].median()
            w, b = 1 - c["R2_w"].median(), 1 - c["R2_c"].median()
            m = mg[(mg["vtag"] == vt) & (mg["arm"] == arm)]
            for nL in sorted(m["n_L"].unique()):
                x = m[m["n_L"] == nL].drop_duplicates("estimator").set_index("estimator")["emp_var_median"]
                rho = x["C_ppi"] / x["C_classical"] if {"C_ppi", "C_classical"} <= set(x.index) else np.nan
                rows.append(dict(vtag=vt, arm=arm, form="C", estimand="theta3", n_L=int(nL), G=int(c["G"].iloc[0]),
                                 n_genes=int(c["gene"].nunique()), one_minus_R2_w=w, one_minus_R2_c=b, rho_c=rho,
                                 m_star_classical_cd100=ms,
                                 m_star_PP_cd100=ms * np.sqrt(w / rho) if rho and rho > 0 else np.nan,
                                 ratio_PP_over_classical=np.sqrt(w / rho) if rho and rho > 0 else np.nan,
                                 fitted_m_star_classical_cd100=fc, fitted_m_star_PP_cd100=fp,
                                 fitted_ratio=fp / fc if fc and fc > 0 else np.nan))
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    print(out.round(3).to_string())


if __name__ == "__main__":
    main()
