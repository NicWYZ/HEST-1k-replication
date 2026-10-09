"""Round 5 PPI, E5 item 1: where the superpopulation-target interval covers below 0.85 in E3's
simulation (results/round5/ppi/E3_twolevel/e3_sim.csv). Writes
results/round5/ppi/E5_joint/e5_superpop_undercoverage.csv, one row per regime, estimand, estimator,
mu, G and arm: cells, cells below 0.85, and the smallest coverage."""
import pandas as pd


def main():
    s = pd.read_csv("results/round5/ppi/E3_twolevel/e3_sim.csv")
    x = s[s["target"] == "super"].copy()
    x["below"] = x["coverage"] < 0.85
    out = (x.groupby(["regime", "estimand", "estimator", "mu", "G", "arm"])
           .agg(n_cells=("coverage", "size"), n_below_085=("below", "sum"), coverage_min=("coverage", "min"))
           .reset_index())
    out.to_csv("results/round5/ppi/E5_joint/e5_superpop_undercoverage.csv", index=False)
    b = out[out["n_below_085"] > 0]
    print(len(out), len(b), int(out["n_below_085"].sum()), int(out["n_cells"].sum()))
    print(b.groupby(["regime", "estimand", "G"])["coverage_min"].min().to_string())


if __name__ == "__main__":
    main()
