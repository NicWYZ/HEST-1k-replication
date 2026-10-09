"""Round 5 PPI, E5 item 1: share of draws dropped for theta2 where the draw was taken from all donors.

E4 (round5_ppi_e4_selection.py) and the E3 masking grid draw the labelled donors from all donors
and drop a draw with fewer than two valid labelled donors (donors where both groups are present).
This writes, per cell, n_draws kept out of the nominal 200 and the share dropped:
results/round5/ppi/E5_joint/e5_theta2_dropped_draws.csv (theta2 rows of e4_selection_grid.csv for
D0 and D2, and of e3_masking_grid.csv, regime A, m = all).
"""
import pandas as pd

OUT = "results/round5/ppi/E5_joint/e5_theta2_dropped_draws.csv"


def main():
    rows = []
    g = pd.read_csv("results/round5/ppi/E4_selection/e4_selection_grid.csv", low_memory=False)
    g = g[(g["estimand"] == "theta2") & g["design"].isin(["D0", "D2"]) & (g["rule"] == "none")
          & (g["interval"] == "textbook_t|fpc|lin")]
    for r in g.drop_duplicates(["vtag", "arm", "n_L", "design", "balance", "p_a"]).itertuples():
        rows.append(dict(source="e4_selection_grid.csv", vtag=r.vtag, arm=r.arm, G_valid=r.G, n_L=r.n_L,
                         design=r.design, balance=r.balance, p_a=r.p_a, n_draws_kept=r.n_draws,
                         share_dropped=1 - r.n_draws / 200.0))
    m = pd.read_csv("results/round5/ppi/E3_twolevel/e3_masking_grid.csv", low_memory=False)
    m = m[(m["estimand"] == "theta2") & (m["m"].astype(str) == "all") & (m["estimator"] == "C_classical")
          & (m["interval"] == "textbook_t|fpc|lin|xf")]
    for r in m.drop_duplicates(["vtag", "arm", "n_L"]).itertuples():
        rows.append(dict(source="e3_masking_grid.csv", vtag=r.vtag, arm=r.arm, G_valid=r.G, n_L=r.n_L,
                         design="regime A, m = all", balance="", p_a=None, n_draws_kept=r.n_draws,
                         share_dropped=1 - r.n_draws / 200.0))
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    x = out[out["share_dropped"] > 0]
    print(len(out), len(x)); print(x.groupby(["source", "vtag", "n_L"])["share_dropped"].agg(["min", "max"]).round(3).to_string())


if __name__ == "__main__":
    main()
