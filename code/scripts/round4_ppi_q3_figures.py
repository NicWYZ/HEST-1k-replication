#!/usr/bin/env python
"""Round 4 PPI, interval 2: report figures for Q2 and Q3, drawn from the merged tables.

Reads the tables written by round4_ppi_q3_merge.py under --res (results/round4/ppi):
  Q2_theory/q2_variance_grid.csv, Q2_theory/q2_cluster_r2.csv, Q2_theory/q2_fitted_components.csv,
  Q3_regimes/q3_regime_comparison.csv
and writes
  Q2_theory/fig_q2_gain_vs_cluster_r2.png, Q2_theory/fig_q2_variance_vs_m.png,
  Q2_theory/fig_q2_optimal_m.png, Q3_regimes/fig_q3_regimes.png
plus Q2_theory/fig_q2_source_points.csv and Q3_regimes/fig_q3_source_points.csv, the exact values drawn.

All panels use theta3, donor-weighted population, superpopulation target, CR1 with t
reference, as in the merge script.  Style rules are set inline (no plugin dependency).
"""
import argparse
import os

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

RC = {
    "font.family": "sans-serif", "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
    "legend.fontsize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6, "axes.linewidth": 0.6,
    "xtick.direction": "out", "ytick.direction": "out", "xtick.major.size": 3, "ytick.major.size": 3,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "savefig.dpi": 300, "savefig.bbox": "tight",
    "axes.titlelocation": "left", "lines.linewidth": 1.2, "pdf.fonttype": 42, "ps.fonttype": 42,
}
TASK_COLOR = {  # Okabe-Ito, colour-blind safe
    "CCRCC": "#0072B2", "CCRCC_merged": "#56B4E9", "INDIANA_KIDNEY": "#009E73",
    "LUNG_XENIUM": "#CC79A7", "ACS_STATES": "#E69F00", "ACS_CA_PUMA": "#D55E00",
}
TASK_LABEL = {
    "CCRCC": "CCRCC (24 donors)", "CCRCC_merged": "CCRCC merged (23)", "INDIANA_KIDNEY": "Indiana kidney (25)",
    "LUNG_XENIUM": "Lung Xenium (15)", "ACS_STATES": "ACS states (51)", "ACS_CA_PUMA": "ACS CA PUMAs (265)",
}
ARM_MARKER = {"hoptimus0": "o", "uni_v2": "s", "resnet50": "^", "package": "D", "permuted": "X"}
ARM_LABEL = {"hoptimus0": "H-optimus-0", "uni_v2": "UNI v2", "resnet50": "ResNet-50",
             "package": "ACS gradient boosting", "permuted": "permuted predictions"}


def sel(df, **kw):
    m = np.ones(len(df), bool)
    for k, v in kw.items():
        m &= (df[k] == v).to_numpy()
    return df[m]


def plain_int(x, _):
    return f"{x/1000:g}k" if x >= 1000 else f"{x:g}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--res", required=True)
    a = p.parse_args()
    plt.rcParams.update(RC)
    q2d, q3d = f"{a.res}/Q2_theory", f"{a.res}/Q3_regimes"
    grid = pd.read_csv(f"{q2d}/q2_variance_grid.csv", low_memory=False)
    r2 = pd.read_csv(f"{q2d}/q2_cluster_r2.csv", low_memory=False)
    fp = f"{q2d}/q2_fitted_components.csv"
    fit = pd.read_csv(fp if os.path.exists(fp) else fp + ".gz", low_memory=False)
    q3 = pd.read_csv(f"{q3d}/q3_regime_comparison.csv", low_memory=False)
    grid["m"] = grid.m.astype(str)
    g = sel(grid, estimand="theta3", population="donor", target="super", interval="CR1_t",
            lambda_rule="c_crossfit")
    r2z = sel(r2, scale="z", estimand="theta3", population="donor")
    tasks = [t for t in TASK_COLOR if t in set(g.vtag)]
    src = []

    # Figure Q2.1: variance ratio against 1 - cluster R2
    fig, ax = plt.subplots(figsize=(3.6, 3.2))
    for (vt, arm), gg in g.groupby(["vtag", "arm"]):
        s = gg[(gg.m == "all") & (gg.n_L == gg.n_L.max())]
        rz = r2z[(r2z.vtag == vt) & (r2z.arm == arm)]
        if not (len(s) and len(rz)):
            continue
        x = float(np.nanmedian(1 - rz.R2_cluster_raw)); y = float(s.emp_var_ratio_median.iloc[0])
        src.append(dict(figure="gain_vs_cluster_r2", vtag=vt, arm=arm, n_L=int(s.n_L.iloc[0]), x=x, y=y))
        ax.scatter(x, y, s=26, marker=ARM_MARKER[arm], color=TASK_COLOR[vt], edgecolor="white", lw=0.4, zorder=3)
    lim = (0, 1.05)
    ax.plot(lim, lim, color="0.45", lw=0.8, ls="--", zorder=1)
    ax.axhline(1, color="0.45", lw=0.6, ls=":", zorder=1)
    ax.text(0.50, 0.44, "ratio = 1 − R²", fontsize=7, color="0.35", ha="left", va="top")
    ax.text(0.02, 1.0, "no gain", fontsize=7, color="0.35", ha="left", va="bottom")
    ax.set_xlabel("1 − squared correlation of donor-level\nprediction and outcome (median over genes)")
    ax.set_ylabel("PPI rule (c) / classical variance\n(all spots, largest $n_L$)")
    ax.set_title("PPI reduces variance only with the ACS boosting predictor")
    ax.margins(0.05)
    th = [Line2D([], [], ls="", marker="o", color=TASK_COLOR[t], label=TASK_LABEL[t]) for t in tasks]
    arms = [a_ for a_ in ARM_MARKER if a_ in set(g.arm)]
    ah = [Line2D([], [], ls="", marker=ARM_MARKER[a_], color="0.4", label=ARM_LABEL[a_]) for a_ in arms]
    ax.legend(handles=th + ah, loc="center left", bbox_to_anchor=(1.01, 0.5), handletextpad=0.3)
    fig.savefig(f"{q2d}/fig_q2_gain_vs_cluster_r2.png"); plt.close(fig)

    # Figure Q2.2: variance against m, relative to m = all, one predictor per task
    fig, ax = plt.subplots(figsize=(3.8, 3.0))
    ends = []
    for vt in tasks:
        gg = g[(g.vtag == vt) & g.arm.isin(["hoptimus0", "package"])]
        if not len(gg):
            continue
        n = 8 if (gg.n_L == 8).any() else int(gg.n_L.max())
        s = gg[gg.n_L == n].copy(); s = s[s.m != "all"]; s["mn"] = s.m.astype(float); s = s.sort_values("mn")
        al = gg[(gg.n_L == n) & (gg.m == "all")]
        if not (len(s) and len(al)):
            continue
        yy = s.emp_var_median.to_numpy() / float(al.emp_var_median.iloc[0])
        for mv, yv in zip(s.mn, yy):
            src.append(dict(figure="variance_vs_m", vtag=vt, arm=s.arm.iloc[0], n_L=n, x=mv, y=yv))
        ax.plot(s.mn, yy, marker="o", ms=3, color=TASK_COLOR[vt])
        ends.append((vt, s.mn.iloc[-1], yy[-1]))
    ax.set_xscale("log"); ax.set_yscale("log")
    ms = sorted(set(x["x"] for x in src if x["figure"] == "variance_vs_m"))
    ax.xaxis.set_major_locator(FixedLocator(ms)); ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(plain_int))
    yt = [1, 2, 5, 10, 20, 50]
    ax.yaxis.set_major_locator(FixedLocator(yt)); ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(plain_int))
    ax.axhline(1, color="0.45", lw=0.6, ls=":")
    ends.sort(key=lambda e: e[2])
    lasty = -np.inf
    for vt, xe, ye in ends:  # stagger end labels in log space
        ly = max(np.log10(ye), lasty + 0.075); lasty = ly
        ax.text(xe * 1.12, 10 ** ly, TASK_LABEL[vt].split(" (")[0], color=TASK_COLOR[vt], fontsize=7, va="center")
    ax.set_xlabel("labelled spots per donor, m")
    ax.set_ylabel("variance / variance with all spots")
    ax.set_title("PPI rule (c) variance as spots per donor grow ($n_L$ = 8)")
    ax.margins(x=0.04)
    fig.savefig(f"{q2d}/fig_q2_variance_vs_m.png"); plt.close(fig)

    # Figure Q2.3: fitted optimal m at c_d / c_s = 100 (points, log axis)
    f = sel(fit, target="super", interval="CR1_t", estimand="theta3", population="donor")
    f = f[f.lambda_rule.isin(["none", "c_crossfit"])]
    cats = [(vt, arm) for vt in tasks for arm in ARM_MARKER if len(f[(f.vtag == vt) & (f.arm == arm)])]
    fig, ax = plt.subplots(figsize=(5.4, 2.8))
    for i, (vt, arm) in enumerate(cats):
        for rule, dx, mk in (("none", -0.15, "o"), ("c_crossfit", 0.15, "s")):
            v = f[(f.vtag == vt) & (f.arm == arm) & (f.lambda_rule == rule)].m_star_cd_cs_100
            med = float(np.nanmedian(v)) if v.notna().any() else np.nan
            src.append(dict(figure="optimal_m", vtag=vt, arm=arm, lambda_rule=rule, x=i, y=med,
                            n_genes=int(v.notna().sum())))
            if np.isfinite(med):
                ax.scatter(i + dx, med, marker=mk, s=22, color=TASK_COLOR[vt],
                           facecolor=TASK_COLOR[vt] if rule == "none" else "white", lw=0.9, zorder=3)
            else:
                ax.text(i + dx, 90, "n.d.", fontsize=6, ha="center", va="bottom", color="0.35", rotation=90)
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(FixedLocator([75, 100, 150, 200, 300, 400]))
    ax.yaxis.set_minor_locator(NullLocator()); ax.yaxis.set_major_formatter(FuncFormatter(plain_int))
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels([ARM_LABEL[arm].replace("ACS gradient boosting", "boosting").replace("permuted predictions", "permuted")
                        for _, arm in cats], rotation=60, ha="right")
    for vt in tasks:
        idx = [i for i, c in enumerate(cats) if c[0] == vt]
        if idx:
            ax.text(np.mean(idx), 1.02, TASK_LABEL[vt].split(" (")[0].replace("ACS ", "ACS\n"),
                    transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=7, color=TASK_COLOR[vt])
    ax.set_ylabel("$m^\\star$ at $c_d/c_s = 100$\n(median over genes)")
    ax.legend(handles=[Line2D([], [], ls="", marker="o", color="0.3", label="classical"),
                       Line2D([], [], ls="", marker="s", color="0.3", mfc="white", label="PPI rule (c)")],
              loc="upper left", bbox_to_anchor=(1.01, 1.0))
    ax.set_title("Fitted spots per donor that minimise variance at fixed cost", pad=24)
    ax.set_xlim(-0.6, len(cats) - 0.4); ax.margins(y=0.08)
    fig.savefig(f"{q2d}/fig_q2_optimal_m.png"); plt.close(fig)
    pd.DataFrame(src).to_csv(f"{q2d}/fig_q2_source_points.csv", index=False)

    # Figure Q3: regime B (spread over all donors) against regime A (n_L = 8), same budget
    q = sel(q3, estimand="theta3", population="donor", lambda_rule="c_crossfit", cost="unit")
    q = q[q.arm.isin(["hoptimus0", "package"])]
    q3tasks = [t for t in TASK_COLOR if t in set(q.vtag)]
    s3 = []
    fig, axs = plt.subplots(1, 2, figsize=(6.0, 2.9), sharey=True, gridspec_kw=dict(wspace=0.06))
    for ax, tgt, ttl in zip(axs, ("design", "super"), ("Design target", "Superpopulation target")):
        for vt in q3tasks:
            qq = q[(q.target == tgt) & (q.vtag == vt)]
            B = qq[qq.regime == "B"].sort_values("budget")
            A = qq[(qq.regime == "A") & (qq.n_L == 8)].sort_values("budget")
            ax.plot(B.budget, B.emp_var_median, marker="o", ms=3, color=TASK_COLOR[vt])
            ax.plot(A.budget, A.emp_var_median, marker="s", ms=3, ls="--", color=TASK_COLOR[vt], mfc="white")
            for rg, d in (("B", B), ("A_nL8", A)):
                for bb, vv in zip(d.budget, d.emp_var_median):
                    s3.append(dict(target=tgt, vtag=vt, regime=rg, budget=bb, emp_var_median=vv))
        ax.set_xscale("log"); ax.set_yscale("log")
        bud = sorted(q.budget.unique())
        ax.xaxis.set_major_locator(FixedLocator(bud)); ax.xaxis.set_minor_locator(NullLocator())
        ax.xaxis.set_major_formatter(FuncFormatter(plain_int))
        ax.set_xlabel("labelled spots, B"); ax.set_title(ttl); ax.margins(x=0.06)
    axs[0].set_ylabel("variance of PPI rule (c)\n(median over genes)")
    th = [Line2D([], [], color=TASK_COLOR[t], label=TASK_LABEL[t].split(" (")[0]) for t in q3tasks]
    rh = [Line2D([], [], color="0.3", marker="o", ms=3, label="regime B, all donors"),
          Line2D([], [], color="0.3", marker="s", ms=3, ls="--", mfc="white", label="regime A, $n_L$ = 8")]
    axs[1].legend(handles=th + rh, loc="center left", bbox_to_anchor=(1.02, 0.5))
    fig.suptitle("Spreading the budget over all donors lowers variance, except ACS states below 9.6k spots", x=0.125, ha="left",
                 fontsize=8, y=1.02)
    fig.savefig(f"{q3d}/fig_q3_regimes.png"); plt.close(fig)
    pd.DataFrame(s3).to_csv(f"{q3d}/fig_q3_source_points.csv", index=False)
    print(dict(q2_points=len(src), q3_points=len(s3), tasks=tasks, q3_tasks=q3tasks))


if __name__ == "__main__":
    main()
