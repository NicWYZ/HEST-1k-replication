"""E3 figures, read only from committed merge outputs.

fig_e3_summary.png
  a  theta2 regime B coverage against m: E2's simple random draw (r4 estimator, c_crossfit) and
     E3's stratified draw (C_ppi), encoder arms on the tissue tasks, design target.
  b  form C over form P classical width ratio against m on the tissue tasks (E3.3 cells).
  c  two-level minus classical regime B over regime A width ratio, by task (E3.7 cells).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

D = "results/round5/ppi/E3_twolevel"
E2 = "results/round5/ppi/E2_regimeB/e2_regimeB_grid.csv"
TISSUE = ["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM"]
ENC = ["hoptimus0", "uni_v2", "resnet50"]
COL = {"CCRCC": "#1b6ca8", "CCRCC_merged": "#7fb3d5", "INDIANA_KIDNEY": "#2a9d8f", "LUNG_XENIUM": "#e76f51",
       "ACS_STATES": "#6d597a", "ACS_CA_PUMA": "#b56576"}
NAME = {"CCRCC": "kidney cancer", "CCRCC_merged": "kidney cancer, merged", "INDIANA_KIDNEY": "Indiana kidney",
        "LUNG_XENIUM": "lung", "ACS_STATES": "census, states", "ACS_CA_PUMA": "census, CA areas"}


def main():
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 6.5,
                         "ytick.labelsize": 6.5, "legend.fontsize": 7, "axes.spines.top": False,
                         "axes.spines.right": False})
    fig, axs = plt.subplots(1, 3, figsize=(7.6, 2.8), gridspec_kw={"wspace": 0.55})

    ax = axs[0]
    e2 = pd.read_csv(E2, low_memory=False)
    e2 = e2[(e2["estimand"] == "theta2") & (e2["target"] == "design") & (e2["lambda_rule"] == "c_crossfit")
            & e2["vtag"].isin(TISSUE) & e2["arm"].isin(ENC)].copy()
    e3 = pd.read_csv(f"{D}/e3_regimeB_small_m.csv", low_memory=False)
    e3 = e3[(e3["estimand"] == "theta2") & (e3["estimator"] == "C_ppi") & e3["vtag"].isin(TISSUE)
            & e3["arm"].isin(ENC)].copy()
    for d in (e2, e3):
        d["m_num"] = pd.to_numeric(d["m"], errors="coerce")
    e3 = e3[e3["m_num"] >= 4]
    for d, lab, mk, c in ((e2, "simple random draw (E2)", "o", "#9a9a9a"), (e3, "stratified draw (E3)", "s", "#1b6ca8")):
        ax.scatter(d["m_num"] * np.exp(np.random.default_rng(0).uniform(-0.06, 0.06, len(d))), d["coverage_median"],
                   s=6, color=c, alpha=0.35, lw=0, marker=mk)
        med = d.groupby("m_num")["coverage_median"].median()
        ax.plot(med.index, med.values, color=c, marker=mk, ms=3.5, lw=1.2, label=lab)
    ax.axhspan(0.86, 0.92, color="#1b6ca8", alpha=0.08, lw=0)
    ax.axhline(0.90, color="k", lw=0.6, ls=":")
    ax.set_xscale("log"); ax.set_xticks([2, 4, 10, 25, 100]); ax.set_xticklabels(["2", "4", "10", "25", "100"])
    ax.set_xlabel("labelled units per cluster, m"); ax.set_ylabel("coverage of 90% interval (median gene)")
    ax.set_title("Stratified draw holds coverage", loc="left")
    ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0.12, 0.22))
    ax.margins(0.04)

    ax = axs[1]
    c = pd.read_csv(f"{D}/e3_prediction_cells.csv", low_memory=False)
    c3 = c[(c["prediction"] == "E3.3") & c["C_over_P"].notna()]
    for v in TISSUE:
        s = c3[c3["vtag"] == v]
        med = s.groupby("m_num")["C_over_P"].median()
        ax.plot(med.index, med.values, marker="o", ms=3, lw=1.1, color=COL[v], label=NAME[v])
    ax.axhspan(0.80, 0.97, color="#9a9a9a", alpha=0.12, lw=0)
    ax.axhline(1.0, color="k", lw=0.6, ls=":")
    ax.set_xscale("log"); ax.set_xticks([10, 25, 50, 100]); ax.set_xticklabels(["10", "25", "50", "100"])
    ax.set_xlabel("labelled units per cluster, m"); ax.set_ylabel("width, form C over form P (classical)")
    ax.set_title("Form C narrows kidney cancer most", loc="left")
    ax.legend(frameon=False, loc="lower left", fontsize=6.5)
    ax.margins(0.04)

    ax = axs[2]
    r = pd.read_csv(f"{D}/e3_regime_ratio_two_level_vs_classical.csv")
    order = ["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM", "ACS_STATES", "ACS_CA_PUMA"]
    rng = np.random.default_rng(1)
    for i, v in enumerate(order):
        s = r[r["vtag"] == v]["diff"].to_numpy()
        ax.scatter(i + rng.uniform(-0.18, 0.18, len(s)), s, s=6, color=COL[v], alpha=0.5, lw=0)
        ax.plot([i - 0.28, i + 0.28], [np.median(s)] * 2, color="k", lw=1.2)
    ax.axhline(0, color="k", lw=0.6, ls=":")
    ax.axhspan(-0.20, -0.05, xmin=0.5, color="#e76f51", alpha=0.10, lw=0)
    ax.set_xticks(range(len(order))); ax.set_xticklabels([NAME[v] for v in order], rotation=40, ha="right")
    ax.set_ylabel("B/A width ratio, two-level minus classical")
    ax.set_title("Kidney ratio unchanged", loc="left")
    ax.margins(0.04)

    for a, l in zip(axs, "abc"):
        a.text(-0.28, 1.08, l, transform=a.transAxes, fontweight="bold", fontsize=10)
    fig.savefig(f"{D}/fig_e3_summary.png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    main()
