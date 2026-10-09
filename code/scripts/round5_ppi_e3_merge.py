"""Round 5 PPI, interval 2, stage E3: merge the six task units and the simulation, score E3.

Reads only result files (the unit outputs copied back under results/round5/ppi/E3_twolevel/<vtag>/
<arm>__<part>/, the unit acceptance files, the E2 decomposition, round 4's tables). Run from the
repository root:  python code/scripts/round5_ppi_e3_merge.py

Writes under results/round5/ppi/E3_twolevel/:
  e3_regime_comparison.csv, e3_masking_grid.csv, e3_regimeB_small_m.csv, e3_unit_weighted.csv,
  e3_components.csv (full-data components and R^2, plus the fitted empirical components and m* from
  the masking grid), e3_acceptance.csv, e3_gene_ratios.csv.gz (per gene width and variance ratios),
  e3_prediction_scores.csv, e3_prediction_cells.csv, e3_report_numbers.csv,
  e3_superseded_round4_numbers.csv.
Primary design-target interval in regime A: textbook_t|fpc|lin|xf (E3a acceptance passed); the
uncorrected interval is kept beside it.
"""
import glob
import os

import numpy as np
import pandas as pd

D = "results/round5/ppi/E3_twolevel"
TASKS = ("CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM", "ACS_STATES", "ACS_CA_PUMA")
TISSUE = TASKS[:4]
KIDNEY = TASKS[:3]
ENC = ("hoptimus0", "uni_v2", "resnet50", "package")
PRIMARY = "textbook_t|fpc|lin|xf"
CLASSICAL_OF = {"r4_ppi": "r4_classical", "P_ppi": "P_classical", "C_ppi": "C_classical",
                "r4_classical": "r4_classical", "P_classical": "P_classical", "C_classical": "C_classical"}
NUM = []


def num(name, value, source):
    NUM.append(dict(name=name, value=value, source=source))


def cat(pattern):
    fs = sorted(glob.glob(pattern))
    return pd.concat([pd.read_csv(f, low_memory=False) for f in fs], ignore_index=True) if fs else pd.DataFrame()


def gene_ratios(part):
    g = cat(f"{D}/*/*__{part}/e3_{part}_genes__*.csv.gz")
    if g.empty:
        return g
    g["m"] = g["m"].astype(str)
    keys = ["vtag", "arm", "part", "regime", "budget", "cost", "n_L", "m", "estimand", "interval", "gene"]
    for k in ("budget",):
        g[k] = g[k].fillna(-1)
    base = g.set_index(keys + ["estimator"])
    cl = g.copy()
    cl["estimator"] = cl["estimator"].map(lambda e: e)
    w = g.pivot_table(index=keys, columns="estimator", values="width", aggfunc="first")
    v = g.pivot_table(index=keys, columns="estimator", values="emp_var", aggfunc="first")
    out = []
    for est in w.columns:
        c = CLASSICAL_OF.get(est)
        r = pd.DataFrame({"width": w[est], "emp_var": v[est],
                          "width_over_own_classical": w[est] / w[c] if c in w else np.nan,
                          "width_over_r4_classical": w[est] / w["r4_classical"] if "r4_classical" in w else np.nan,
                          "var_over_own_classical": v[est] / v[c] if c in v else np.nan})
        r["estimator"] = est
        out.append(r.reset_index())
    o = pd.concat(out, ignore_index=True)
    cov = g[keys + ["estimator", "coverage"]]
    return o.merge(cov, on=keys + ["estimator"], how="left")


def main():
    os.makedirs(D, exist_ok=True)
    parts = {}
    for part, fname in (("regcomp", "e3_regime_comparison.csv"), ("masking", "e3_masking_grid.csv"),
                        ("regb", "e3_regimeB_small_m.csv"), ("unitw", "e3_unit_weighted.csv")):
        t = cat(f"{D}/*/*__{part}/e3_{part}__*.csv")
        t.to_csv(f"{D}/{fname}", index=False)
        parts[part] = t
    comp = cat(f"{D}/*/*__components/e3_components__*.csv")
    # ---- gene-level ratios
    GR = {p: gene_ratios(p) for p in ("regcomp", "masking", "regb")}
    allgr = pd.concat([x for x in GR.values() if not x.empty], ignore_index=True)
    allgr.to_csv(f"{D}/e3_gene_ratios.csv.gz", index=False)
    med = (allgr.groupby(["vtag", "arm", "part", "regime", "budget", "cost", "n_L", "m", "estimand", "interval",
                          "estimator"], dropna=False)
           [["width_over_own_classical", "width_over_r4_classical", "var_over_own_classical", "coverage"]]
           .median().reset_index())
    # ---- fitted empirical components from the masking grid (m < all), per gene and estimator
    mg = GR["masking"]
    rows = []
    if not mg.empty:
        mm = mg[(mg["m"] != "all") & (mg["interval"] == PRIMARY)].copy()
        mm["m_num"] = mm["m"].astype(float)
        for key, g in mm.groupby(["vtag", "arm", "estimand", "estimator", "gene"]):
            X = np.column_stack([1.0 / g["n_L"], 1.0 / (g["n_L"] * g["m_num"]), np.ones(len(g))])
            beta, *_ = np.linalg.lstsq(X, g["emp_var"].to_numpy(), rcond=None)
            a, b, c = beta
            r = dict(zip(["vtag", "arm", "estimand", "estimator", "gene"], key), a_cluster=a, b_unit=b, c=c)
            for k in (10, 100, 1000):
                r[f"m_star_emp_cd{k}"] = np.sqrt(k * b / a) if a > 0 and b > 0 else np.nan
            rows.append(r)
    fit = pd.DataFrame(rows)
    comp.to_csv(f"{D}/e3_components.csv", index=False)
    fit.to_csv(f"{D}/e3_components_fitted.csv", index=False)
    # ---- acceptance
    acc = cat(f"{D}/*/e3_unit_acceptance__*.csv")
    acc.to_csv(f"{D}/e3_acceptance.csv", index=False)
    # ---- predictions
    scores, cells = [], []

    def add(pid, held, text, cdf=None):
        if cdf is not None and len(cdf) == 0:
            held = "not assessed (no cells)"
        scores.append(dict(prediction=pid, verdict=held, summary=text))
        if cdf is not None and len(cdf):
            c = cdf.copy(); c["prediction"] = pid; cells.append(c)
    rb = med[(med["part"] == "regb") & (med["interval"] == "regB_t")].copy()
    rb["m_num"] = pd.to_numeric(rb["m"], errors="coerce")
    # E3.1 regime B, permuted, C_ppi over C_classical, m >= 10
    x = rb[(rb["arm"] == "permuted") & (rb["estimator"] == "C_ppi") & (rb["m_num"] >= 10)]
    ok = x["width_over_own_classical"].between(0.97, 1.05)
    uw = parts["unitw"]
    u_txt = ""
    if not uw.empty:
        ug = cat(f"{D}/*/*__unitw/e3_unitw_genes__*.csv.gz")
        ug = ug[(ug["arm"] == "permuted") & (ug["interval"] == PRIMARY) & (ug["n_L"] >= 8)]
        pv = ug.pivot_table(index=["vtag", "estimand", "n_L", "gene"], columns="estimator", values="emp_var")
        if {"greg_ppi", "greg_classical"} <= set(pv.columns):
            vr = (pv["greg_ppi"] / pv["greg_classical"]).groupby(level=[0, 1, 2]).median().rename("var_ratio").reset_index()
            u_ok = vr["var_ratio"].between(0.95, 1.15)
            u_txt = f"; unit-weighted permuted variance ratio at n_L >= 8 in 0.95-1.15 in {int(u_ok.sum())} of {len(vr)} cells, range {vr['var_ratio'].min():.3f} to {vr['var_ratio'].max():.3f}"
            vr["prediction_part"] = "unitw"; add("E3.1b", "held" if u_ok.all() else "partly held", u_txt.strip("; "), vr)
    add("E3.1", "held" if ok.all() else ("partly held" if ok.mean() >= 0.5 else "refuted"),
        f"regime B permuted C_ppi/C_classical width at m >= 10 in 0.97-1.05 in {int(ok.sum())} of {len(x)} cells, "
        f"range {x['width_over_own_classical'].min():.3f} to {x['width_over_own_classical'].max():.3f}{u_txt}", x)
    # E3.2 real predictors C_ppi/C_classical in regime B vs E2 ratio to donor_constant
    e2 = pd.read_csv("results/round5/ppi/E2_regimeB/e2_decomposition.csv")
    e2 = e2[(e2["target"] == "design") & (e2["population"] == "donor")][["vtag", "arm", "m", "estimand", "width_over_donor_constant_median"]]
    e2["m_num"] = e2["m"].astype(float)
    y = rb[(rb["arm"].isin(ENC)) & (rb["estimator"] == "C_ppi")].merge(e2.drop(columns="m"), on=["vtag", "arm", "estimand", "m_num"], how="inner")
    y["diff"] = y["width_over_own_classical"] - y["width_over_donor_constant_median"]
    y = y[np.isfinite(y["diff"])]
    ok = y["diff"].abs() <= 0.05
    parts2 = "; ".join(f"{e}: {int((d['diff'].abs() <= 0.05).sum())} of {len(d)} (max {d['diff'].abs().max():.3f})"
                       for e, d in y.groupby("estimand"))
    add("E3.2", "held" if ok.all() else ("partly held" if ok.mean() >= 0.5 else "refuted"),
        f"|C_ppi/C_classical - E2 encoder/donor_constant| <= 0.05 in {int(ok.sum())} of {len(y)} cells; by estimand {parts2} "
        f"(E2's theta2 rows used the simple random draw, E3's the stratified draw)", y)
    # E3.3 C classical narrower than P classical at m >= 10 tissue by 3-20%; C covers 0.87-0.92 from m = 5
    gg = GR["regb"]
    gg = gg[(gg["interval"] == "regB_t")].copy()
    gg["m_num"] = pd.to_numeric(gg["m"], errors="coerce")
    pw = gg[gg["estimator"].isin(["C_classical", "P_classical"])].pivot_table(
        index=["vtag", "arm", "estimand", "m_num", "gene"], columns="estimator", values="width")
    cr = (pw["C_classical"] / pw["P_classical"]).groupby(level=[0, 1, 2, 3]).median().rename("C_over_P").reset_index()
    z = cr[(cr["vtag"].isin(TISSUE)) & (cr["m_num"] >= 10)].dropna(subset=["C_over_P"])
    ok1 = z["C_over_P"].between(0.80, 0.97)
    cv = rb[(rb["vtag"].isin(TISSUE)) & (rb["estimator"].isin(["C_classical", "C_ppi"])) & (rb["m_num"] >= 5)]
    ok2 = cv["coverage"].between(0.87, 0.92)
    add("E3.3", "held" if ok1.all() and ok2.all() else ("partly held" if (ok1.mean() >= 0.5 or ok2.mean() >= 0.5) else "refuted"),
        f"C_classical/P_classical width at m >= 10 on tissue in 0.80-0.97 in {int(ok1.sum())} of {len(z)} cells "
        f"(range {z['C_over_P'].min():.3f} to {z['C_over_P'].max():.3f}); form C coverage at m >= 5 in 0.87-0.92 in "
        f"{int(ok2.sum())} of {len(cv)} cells (range {cv['coverage'].min():.3f} to {cv['coverage'].max():.3f})", z)
    # E3.4 regime B narrower than A at cost ratio 10 under the two-level estimator, either form
    rc = GR["regcomp"]
    out4 = []
    if not rc.empty:
        A = rc[(rc["regime"] == "A") & (rc["interval"] == PRIMARY) & (rc["estimand"] == "theta3")]
        B = rc[(rc["regime"] == "B") & (rc["interval"] == "regB_t") & (rc["estimand"] == "theta3")]
        B = B[B["cost"].astype(str).str.startswith("cd_cs_10_")].copy()
        B["n_L_A"] = B["cost"].str.extract(r"nL(\d+)_B")[0].astype(int)
        B["budget_A"] = B["cost"].str.extract(r"_B(\d+)$")[0].astype(float)
        for est in ("P_ppi", "C_ppi", "r4_ppi"):
            a = A[A["estimator"] == est][["vtag", "arm", "n_L", "budget", "gene", "width"]].rename(columns={"width": "wA", "n_L": "n_L_A", "budget": "budget_A"})
            b = B[B["estimator"] == est][["vtag", "arm", "n_L_A", "budget_A", "gene", "width"]].rename(columns={"width": "wB"})
            j = a.merge(b, on=["vtag", "arm", "n_L_A", "budget_A", "gene"])
            j["ratio"] = j["wB"] / j["wA"]
            c4 = j.groupby(["vtag", "arm", "n_L_A", "budget_A"])["ratio"].median().reset_index()
            c4["estimator"] = est
            out4.append(c4)
        c4 = pd.concat(out4, ignore_index=True)
        c4 = c4[c4["arm"].isin(ENC + ("permuted",))]      # round 4's arms (its 232 cells)
        tl = c4[c4["estimator"].isin(["P_ppi", "C_ppi"])]
        nb = pd.DataFrame({e: dict(n=len(d), B_narrower=int((d["ratio"] < 1).sum()), med=float(d["ratio"].median()))
                           for e, d in tl.groupby("estimator")}).T
        ok = all(nb["B_narrower"] / nb["n"] >= 200 / 232)
        add("E3.4", "held" if ok else "refuted",
            "; ".join(f"{e}: B narrower in {int(r.B_narrower)} of {int(r.n)} comparisons, median ratio {r.med:.3f}" for e, r in nb.iterrows()), c4)
        for e, r in nb.iterrows():
            num(f"E3.4|{e}|n_comparisons", int(r.n), "e3_prediction_cells.csv"); num(f"E3.4|{e}|n_B_narrower", int(r.B_narrower), "e3_prediction_cells.csv")
    # E3.5 m* (classical) at cd 100 vs round 4, and m*_PP/m* vs theory
    r4m = {"CCRCC": 121.06163330599604, "INDIANA_KIDNEY": 235.8530014837651, "LUNG_XENIUM": 172.12974101946796,
           "ACS_STATES": 378.59518633633394}
    if not fit.empty:
        f5 = fit[fit["arm"].isin(["hoptimus0", "package"]) & (fit["estimand"] == "theta3")]
        ms = f5.groupby(["vtag", "estimator"])["m_star_emp_cd100"].median().unstack()
        lev = pd.read_csv("results/round5/ppi/E2_regimeB/e2_level_share.csv")
        lev = lev[(lev["arm"] == "constant") & (lev["estimand"] == "theta3") & (lev["population"] == "donor") & (lev["m"] == 20)]
        L = lev.set_index("vtag")["share_clipped_median"]
        t5 = []
        for vt, old in r4m.items():
            if vt not in ms.index:
                continue
            for est in ("P_classical", "C_classical"):
                new = ms.loc[vt, est] if est in ms.columns else np.nan
                t5.append(dict(vtag=vt, estimator=est, mstar_round4=old, mstar_new=new, ratio=new / old,
                               sqrt_1mL=float(np.sqrt(1 - L.get(vt, np.nan)))))
        t5 = pd.DataFrame(t5)
        fall = (t5["ratio"] < 1)
        # theory ratio vs empirical ratio per task, arm (encoders), form
        th = comp[(comp["estimand"] == "theta3") & comp["arm"].isin(ENC)].copy()
        th["theory_ratio"] = np.sqrt((1 - th["R2_w"]) / (1 - th["R2_c"]))
        thm = th.groupby(["vtag", "arm", "form"])["theory_ratio"].median().reset_index()
        em = fit[(fit["estimand"] == "theta3") & fit["arm"].isin(ENC)].pivot_table(
            index=["vtag", "arm", "gene"], columns="estimator", values="m_star_emp_cd100")
        er = []
        for form, (pp, cl) in (("C", ("C_ppi", "C_classical")), ("r4", ("r4_ppi", "r4_classical"))):
            if pp in em and cl in em:
                q = (em[pp] / em[cl]).groupby(level=[0, 1]).median().rename("emp_ratio").reset_index()
                q["form"] = form; er.append(q)
        er = pd.concat(er, ignore_index=True).merge(thm, on=["vtag", "arm", "form"], how="inner")
        er["rel_diff"] = er["emp_ratio"] / er["theory_ratio"] - 1
        okr = er["rel_diff"].abs() <= 0.15
        v5 = "held" if (fall.all() and okr.all()) else ("partly held" if (fall.mean() >= 0.5 and okr.mean() >= 0.5) else "refuted")
        add("E3.5", v5,
            f"classical m* at cd 100 below round 4 in {int(fall.sum())} of {len(t5)} task-form pairs; "
            f"m*_PP/m* within 15% of sqrt((1-R2w)/(1-R2c)) in {int(okr.sum())} of {len(er)} task-arm-form cells",
            pd.concat([t5.assign(kind="mstar"), er.assign(kind="ratio")], ignore_index=True))
    # E3.6 stratified theta2 coverage regime B, tissue, every arm
    s6 = rb[(rb["vtag"].isin(TISSUE)) & (rb["estimand"] == "theta2") & (rb["estimator"] == "C_ppi")]
    a6 = s6[s6["m_num"] >= 6]; b6 = s6[s6["m_num"] == 4]
    ok6a, ok6b = a6["coverage"].between(0.86, 0.92), b6["coverage"].between(0.83, 0.92)
    add("E3.6", "held" if ok6a.all() and ok6b.all() else ("partly held" if ok6a.mean() >= 0.5 else "refuted"),
        f"theta2 stratified regime B coverage (C_ppi, median over genes) at m >= 6 in 0.86-0.92 in {int(ok6a.sum())} of {len(a6)} cells "
        f"(range {a6['coverage'].min():.3f} to {a6['coverage'].max():.3f}); at m = 4 in 0.83-0.92 in {int(ok6b.sum())} of {len(b6)} "
        f"(range {b6['coverage'].min():.3f} to {b6['coverage'].max():.3f})", s6)
    # E3.7 regime B / regime A width ratio: two-level vs classical form C, cost-matched comparisons
    if out4:
        allc = []
        A = rc[(rc["regime"] == "A") & (rc["interval"] == PRIMARY) & (rc["estimand"] == "theta3")]
        B = rc[(rc["regime"] == "B") & (rc["interval"] == "regB_t") & (rc["estimand"] == "theta3")]
        B = B[B["cost"].astype(str).str.startswith("cd_cs_")].copy()
        B["n_L_A"] = B["cost"].str.extract(r"nL(\d+)_B")[0].astype(int)
        B["budget_A"] = B["cost"].str.extract(r"_B(\d+)$")[0].astype(float)
        B["cd"] = B["cost"].str.extract(r"cd_cs_(\d+)_")[0].astype(int)
        for est in ("C_ppi", "C_classical"):
            a = A[A["estimator"] == est][["vtag", "arm", "n_L", "budget", "gene", "width"]].rename(columns={"width": "wA", "n_L": "n_L_A", "budget": "budget_A"})
            b = B[B["estimator"] == est][["vtag", "arm", "cd", "n_L_A", "budget_A", "gene", "width"]].rename(columns={"width": "wB"})
            j = a.merge(b, on=["vtag", "arm", "n_L_A", "budget_A", "gene"])
            j["ratio"] = j["wB"] / j["wA"]
            q = j.groupby(["vtag", "arm", "cd", "n_L_A", "budget_A"])["ratio"].median().rename(est).reset_index()
            allc.append(q)
        c7 = allc[0].merge(allc[1], on=["vtag", "arm", "cd", "n_L_A", "budget_A"])
        c7 = c7[c7["arm"].isin(ENC)]
        c7["diff"] = c7["C_ppi"] - c7["C_classical"]
        k = c7[c7["vtag"].isin(KIDNEY)]; o = c7[~c7["vtag"].isin(KIDNEY)]
        okk, oko = k["diff"].abs() <= 0.10, o["diff"].between(-0.20, -0.05)
        add("E3.7", "held" if okk.all() and oko.all() else ("partly held" if (okk.mean() >= 0.5 or oko.mean() >= 0.5) else "refuted"),
            f"kidney: |two-level - classical| B/A ratio <= 0.10 in {int(okk.sum())} of {len(k)}; lung and ACS: two-level lower by 0.05-0.20 in "
            f"{int(oko.sum())} of {len(o)} (diff range {o['diff'].min():.3f} to {o['diff'].max():.3f}; median diff lung {o[o['vtag']=='LUNG_XENIUM']['diff'].median():.3f}, ACS_STATES {o[o['vtag']=='ACS_STATES']['diff'].median():.3f}, ACS_CA_PUMA {o[o['vtag']=='ACS_CA_PUMA']['diff'].median():.3f})", c7)
        c7.to_csv(f"{D}/e3_regime_ratio_two_level_vs_classical.csv", index=False)
    pd.DataFrame(scores).to_csv(f"{D}/e3_prediction_scores.csv", index=False)
    if cells:
        pd.concat(cells, ignore_index=True).to_csv(f"{D}/e3_prediction_cells.csv", index=False)
    med.to_csv(f"{D}/e3_median_ratios.csv", index=False)
    pd.DataFrame(NUM).to_csv(f"{D}/e3_report_numbers.csv", index=False)
    print(pd.DataFrame(scores).to_string())


if __name__ == "__main__":
    main()
