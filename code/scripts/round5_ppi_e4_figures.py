"""E4 figure, read only from committed merge outputs.

fig_e4_variance_by_design.png
  a  classical variance under D2 (p_a 0.01, theta3, n_L 8) over its D0 variance, by balance variable
     and task, encoder arms (package on census); median over genes per arm.
  b  coverage of the classical interval from the simple-random-sampling formula under D2 with own
     balance, against n_L, by task (theta3 and theta2 pooled, median over arms).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

D = "results/round5/ppi/E4_selection"
ORDER = ["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM", "ACS_STATES", "ACS_CA_PUMA"]
COL = {"CCRCC": "#1b6ca8", "CCRCC_merged": "#7fb3d5", "INDIANA_KIDNEY": "#2a9d8f", "LUNG_XENIUM": "#e76f51",
       "ACS_STATES": "#6d597a", "ACS_CA_PUMA": "#b56576"}
NAME = {"CCRCC": "kidney cancer", "CCRCC_merged": "kidney cancer, merged", "INDIANA_KIDNEY": "Indiana kidney",
        "LUNG_XENIUM": "lung", "ACS_STATES": "census, states", "ACS_CA_PUMA": "census, CA areas"}
BAL = ["own", "pcF2", "pcE2", "perm"]
BALNAME = {"own": "own prediction mean", "pcF2": "2 prediction PCs", "pcE2": "2 embedding PCs", "perm": "permuted (noise)"}
ARMS = ["hoptimus0", "uni_v2", "resnet50", "package"]


def main():
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 6.5,
                         "ytick.labelsize": 6.5, "legend.fontsize": 6.5, "axes.spines.top": False,
                         "axes.spines.right": False})
    r = pd.read_csv(f"{D}/e4_variance_ratios.csv", low_memory=False)
    q = r[(r["design"] == "D2") & (r["p_a"] == 0.01) & (r["rule"] == "none") & (r["interval"] == "textbook_t|fpc|lin")
          & (r["estimand"] == "theta3") & (r["n_L"] == 8) & r["arm"].isin(ARMS)]
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 2.8), gridspec_kw={"wspace": 0.3, "width_ratios": [1.4, 1]})
    ax = axs[0]
    w = 0.18
    for j, b in enumerate(BAL):
        for i, v in enumerate(ORDER):
            z = q[(q["vtag"] == v) & (q["balance"] == b)]["ratio_median"].to_numpy()
            if len(z) == 0:
                ax.text(i + (j - 1.5) * w, 0.05, "n.d.", fontsize=5, ha="center", rotation=90)
                continue
            x = i + (j - 1.5) * w
            ax.scatter(np.full(len(z), x), z, s=9, color=plt.cm.Greys(0.35 + 0.18 * j), lw=0, zorder=3,
                       label=BALNAME[b] if i == 0 else None)
    ax.axhline(1.0, color="k", lw=0.6, ls=":")
    ax.set_xticks(range(len(ORDER))); ax.set_xticklabels([NAME[v] for v in ORDER], rotation=35, ha="right")
    ax.set_ylabel("variance, D2 over D0 (classical, theta3)")
    ax.set_title("Balancing on the prediction mean gains most", loc="left")
    ax.legend(frameon=False, loc="upper right", ncol=2, title="balance variable", title_fontsize=6.5, columnspacing=0.8, handletextpad=0.2)
    ax.set_ylim(0, 1.42); ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])

    g = pd.read_csv(f"{D}/e4_selection_grid.csv", low_memory=False)
    c = g[(g["design"] == "D2") & (g["balance"] == "own") & (g["p_a"] == 0.01) & (g["rule"] == "none")
          & (g["interval"] == "textbook_t|fpc|lin")]
    ax = axs[1]
    for v in ORDER:
        z = c[c["vtag"] == v].groupby("n_L")["coverage_median"].median()
        ax.plot(z.index, z.values, marker="o", ms=3, lw=1.1, color=COL[v], label=NAME[v])
    ax.axhline(0.90, color="k", lw=0.6, ls=":")
    ax.axhline(0.93, color="#9a9a9a", lw=0.8, ls="--")
    ax.text(12.2, 0.932, "predicted floor", fontsize=6, color="#6a6a6a", va="bottom", ha="right")
    ax.set_xlabel("labelled clusters, n_L"); ax.set_ylabel("coverage of 90% interval (median gene)")
    ax.set_title("Over-coverage on lung and census only", loc="left")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=6)
    ax.margins(0.04)
    for a, l in zip(axs, "ab"):
        a.text(-0.16, 1.07, l, transform=a.transAxes, fontweight="bold", fontsize=10)
    fig.savefig(f"{D}/fig_e4_variance_by_design.png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    main()
