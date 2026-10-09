"""E3: every round-4 number that the regression form changes, old and new side by side.

Writes results/round5/ppi/E3_twolevel/e3_superseded_round4_numbers.csv (long format, one row per
quantity and cell, with the source path of both sides). Reads only committed files.

Parts
  mstar       classical optimal units per cluster at c_d/c_s = 100 (round 4 Q2 vs E3 forms P and C)
  q31_count   regime B narrower than regime A at c_d/c_s = 10 (round 4 q31 vs E3.4)
  unitw_perm  unit-weighted permuted variance ratio (round 4 Q5a vs E3 GREG)
  theta2_rows round-4 regime A and B theta2 rows with m < all (design target, c_crossfit), against
              E3's stratified draw under C_ppi, C_classical and P_ppi
"""
import pandas as pd

R4 = "results/round4/ppi"
D = "results/round5/ppi/E3_twolevel"
PRIMARY = "textbook_t|fpc|lin|xf"
OUT = []


def row(part, old, old_src, new, new_src, **k):
    OUT.append(dict(part=part, **k, round4_value=old, round4_source=old_src, round5_value=new, round5_source=new_src))


def mnorm(m):
    try:
        return str(int(float(m)))
    except (TypeError, ValueError):
        return str(m)


def main():
    cells = pd.read_csv(f"{D}/e3_prediction_cells.csv", low_memory=False)
    ms = cells[(cells["prediction"] == "E3.5") & (cells["kind"] == "mstar")]
    for r in ms.itertuples():
        row("mstar", r.mstar_round4, f"{R4}/Q2_theory/q2_report_numbers.csv", r.mstar_new, f"{D}/e3_prediction_cells.csv",
            vtag=r.vtag, estimator=r.estimator, quantity="m_star_classical_cd100")

    q4 = pd.read_csv(f"{R4}/Q4_tables/q4_report_numbers.csv").set_index("name")["value"]
    sc = pd.read_csv(f"{D}/e3_prediction_scores.csv").set_index("prediction")["summary"]
    import re
    m4 = re.findall(r"(C_ppi|P_ppi): B narrower in (\d+) of (\d+)", sc["E3.4"])
    for est, k, n in m4:
        row("q31_count", q4["q31|cd10|super|c_crossfit|n_B_narrower"], f"{R4}/Q4_tables/q4_report_numbers.csv",
            int(k), f"{D}/e3_prediction_scores.csv", estimator=est, quantity="n_B_narrower_cd10",
            note=f"of {int(q4['q31|cd10|super|c_crossfit|n_cells'])} (round 4, super, c_crossfit) and of {n} (E3, design)")

    q5 = pd.read_csv(f"{R4}/Q5a/q5a_spot_weighted_permuted.csv")
    u = pd.read_csv(f"{D}/e3_unit_weighted.csv", low_memory=False)
    u = u[(u["arm"] == "permuted") & (u["interval"] == PRIMARY)]
    pv = u.pivot_table(index=["vtag", "estimand", "n_L"], columns="estimator", values="emp_var_median")
    if {"greg_ppi", "greg_classical"} <= set(pv.columns):
        rat = (pv["greg_ppi"] / pv["greg_classical"]).rename("new").reset_index()
        j = q5.merge(rat, on=["vtag", "estimand", "n_L"], how="left")
        for r in j.itertuples():
            row("unitw_perm", r.emp_var_ratio_median, f"{R4}/Q5a/q5a_spot_weighted_permuted.csv", r.new,
                f"{D}/e3_unit_weighted.csv", vtag=r.vtag, estimand=r.estimand, n_L=r.n_L, arm="permuted",
                quantity="emp_var_ratio_ppi_over_classical", note="E3 value is the ratio of median-over-genes variances")

    q3 = pd.read_csv(f"{R4}/Q3_regimes/q3_regime_comparison.csv", low_memory=False)
    t = q3[(q3["estimand"] == "theta2") & (q3["m"].astype(str) != "all") & (q3["target"] == "design")
           & (q3["lambda_rule"] == "c_crossfit")].copy()
    e = pd.read_csv(f"{D}/e3_regime_comparison.csv", low_memory=False)
    e = e[(e["estimand"] == "theta2") & (e["m"].astype(str) != "all") & (e["target"] == "design")
          & (((e["regime"] == "A") & (e["interval"] == PRIMARY)) | ((e["regime"] == "B") & (e["interval"] == "regB_t")))
          & (e["estimator"].isin(["C_ppi", "C_classical", "P_ppi"]))].copy()
    keys = ["vtag", "arm", "regime", "budget", "cost", "n_L", "m"]
    for d in (t, e):
        d["m"] = d["m"].map(mnorm)
        d["budget"] = pd.to_numeric(d["budget"], errors="coerce")
    for q in ("coverage_median", "emp_var_median", "est_var_over_emp_var_median"):
        for est in ("C_ppi", "C_classical", "P_ppi"):
            ee = e[e["estimator"] == est][keys + [q]].rename(columns={q: "new", "m": "m_round5"})
            # regime B: round 5 records the allocation as m = 'prop' or a number; match on everything but m
            ee = ee.drop_duplicates(subset=keys[:-1] + ["m_round5"])
            ja = t[t["regime"] == "A"][keys + [q]].merge(ee[ee["regime"] == "A"], left_on=keys, right_on=keys[:-1] + ["m_round5"], how="left")
            jb = t[t["regime"] == "B"][keys + [q]].merge(ee[ee["regime"] == "B"], on=keys[:-1], how="left")
            j = pd.concat([ja, jb], ignore_index=True)
            for r in j.itertuples(index=False):
                row("theta2_rows", getattr(r, q), f"{R4}/Q3_regimes/q3_regime_comparison.csv", r.new,
                    f"{D}/e3_regime_comparison.csv", vtag=r.vtag, arm=r.arm, estimand="theta2", regime=r.regime,
                    budget=r.budget, cost=r.cost, n_L=r.n_L, m=r.m, m_round5=r.m_round5, estimator=est, quantity=q,
                    note="round 4 simple random draw, r4 estimator, c_crossfit; round 5 stratified draw")
    out = pd.DataFrame(OUT)
    out.to_csv(f"{D}/e3_superseded_round4_numbers.csv", index=False)
    print(out.groupby("part").agg(n=("round4_value", "size"), new_missing=("round5_value", lambda s: int(s.isna().sum()))).to_string())


if __name__ == "__main__":
    main()
