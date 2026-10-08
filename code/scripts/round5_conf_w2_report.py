#!/usr/bin/env python
"""Round 5, prediction-set track, W2: numbers for scoring W2.1 to W2.5, and the two W2 figures.

Reads the merged tables written by round5_conf_w2_merge.py (w2_sim_designs.csv, w2_census.csv,
w2_narrowest_valid.csv) from IN and writes into OUT:
  w2_report_numbers.csv   one row per number the W2 report quotes: name, value, source file, filter.
                          W2.1 to W2.5 are scored in the report, by the lead, from these numbers.
  fig_w2_fixed_design.png, fig_w2_census.png
Tabulation only; it runs wherever the merged tables are (extension 2 of docs/round5_conf_plan.md).
"Width" is the mean width over replicates; a method enters a width comparison at (setting, alpha, o)
only when it is finite in every replicate there, as in the narrowest-valid rule. GHCP in the
predictions is the released GHCP (released_ghcp, the paper's code); this track's ghcp is reported
beside it.
"""
import argparse
import os

import numpy as np
import pandas as pd

NUM = []


def add(name, value, src, filt):
    NUM.append(dict(name=name, value=value, source=src, filter=filt))
    return value


def cell(S, keys, method, o, alpha=0.1):
    q = S[(S.method == method) & (S.o == o) & np.isclose(S.alpha, alpha)]
    for k, v in keys.items():
        q = q[q[k] == v]
    assert len(q) == 1, (keys, method, o, alpha, len(q))
    return q.iloc[0]


def width(S, keys, method, o, alpha=0.1):
    r = cell(S, keys, method, o, alpha)
    return float(r.width_mean_finite) if r.finite_frac == 1.0 else np.inf


def sim_numbers(S, NV):
    src = "w2_sim_designs.csv"
    k20 = dict(design="fixedN21", K=20)
    d = S[(S.method == "within_full") & (S.o >= 9) & np.isclose(S.alpha, 0.1)]
    add("W2.1_within_full_min_finite_frac_o_ge_9_a0.1_all_designs", float(d.finite_frac.min()), src, "method within_full, o>=9, alpha 0.1, all designs and K")
    for o in (10, 15, 20):
        wf, rg, g = (width(S, k20, m, o) for m in ("within_full", "released_ghcp", "ghcp"))
        add(f"W2.1_K20_o{o}_within_full_width", wf, src, f"fixedN21 K20 alpha 0.1 o {o}")
        add(f"W2.1_K20_o{o}_released_ghcp_width", rg, src, f"fixedN21 K20 alpha 0.1 o {o}")
        add(f"W2.1_K20_o{o}_ghcp_width", g, src, f"fixedN21 K20 alpha 0.1 o {o}")
        add(f"W2.1_K20_o{o}_within_full_over_released_ghcp", wf / rg, src, "ratio")
        add(f"W2.1_K20_o{o}_within_full_over_ghcp", wf / g, src, "ratio")
    for o in (10, 20):
        wp, rg, g = (width(S, k20, m, o) for m in ("within_plain", "released_ghcp", "ghcp"))
        add(f"W2.2_K20_o{o}_within_plain_width", wp, src, f"fixedN21 K20 alpha 0.1 o {o}")
        add(f"W2.2_K20_o{o}_within_plain_over_released_ghcp", wp / rg, src, "ratio")
        add(f"W2.2_K20_o{o}_within_plain_over_ghcp", wp / g, src, "ratio")
    nsrc = "w2_narrowest_valid.csv"
    for o in (5, 8):
        r = NV[(NV.setting == "sim") & (NV.design == "fixedN21") & (NV.K == 20) & (NV.o == o) & np.isclose(NV.alpha, 0.1)].iloc[0]
        add(f"W2.3_K20_o{o}_narrowest", r.narrowest, nsrc, f"fixedN21 K20 alpha 0.1 o {o}")
        add(f"W2.3_K20_o{o}_runner_up", r.runner_up, nsrc, "")
        add(f"W2.3_K20_o{o}_margin", float(r.margin), nsrc, "runner-up minus narrowest mean width")
        add(f"W2.3_K20_o{o}_margin_mcse", float(r.margin_mcse), nsrc, "paired MCSE")
        h = width(S, k20, "hcp", o)
        best_non_ghcp = min(width(S, k20, m, o) for m in ("hcp", "released_stdcp", "within_plain", "within_full"))
        add(f"W2.3_K20_o{o}_narrowest_non_ghcp_width", best_non_ghcp, src, "min over hcp, released_stdcp, within_plain, within_full finite in every replicate")
    for m in ("released_ghcp", "ghcp"):
        add(f"W2.3_K20_o5_{m}_over_hcp", width(S, k20, m, 5) / width(S, k20, "hcp", 5), src, "fixedN21 K20 alpha 0.1 o 5")
    for a in (0.1, 0.2):
        for K in sorted(S[S.design == "fixedN21"].K.unique()):
            kk = dict(design="fixedN21", K=int(K))
            h = width(S, kk, "hcp", 5, a)
            for m in ("released_ghcp", "ghcp"):
                g = width(S, kk, m, 5, a)
                add(f"W2.4_a{a}_K{K}_o5_{m}_width", g, src, f"fixedN21 K{K} alpha {a} o 5")
                add(f"W2.4_a{a}_K{K}_o5_{m}_over_hcp", g / h if np.isfinite(g) and np.isfinite(h) else np.nan, src, "ratio; nan where either is infinite in some replicate")
            add(f"W2.4_a{a}_K{K}_o5_hcp_width", h, src, f"fixedN21 K{K} alpha {a} o 5")
            add(f"W2.4_a{a}_K{K}_hcp_finite_frac", float(cell(S, kk, "hcp", 5, a).finite_frac), src, "")
    # whole map at alpha 0.1
    v = NV[(NV.setting == "sim") & np.isclose(NV.alpha, 0.1)]
    for (des, K), g in v.groupby(["design", "K"]):
        K = int(K)
        add(f"map_{des}_K{K}_narrowest_by_o", ";".join(f"o{int(o)}:{n}" for o, n in zip(g.o, g.narrowest.fillna("none"))), nsrc, "alpha 0.1")


def census_numbers(C, NV):
    src, nsrc = "w2_census.csv", "w2_narrowest_valid.csv"
    v = NV[NV.setting == "census"]
    for a in (0.1, 0.2):
        for p, g in v[np.isclose(v.alpha, a)].groupby("n_puma"):
            p = int(p)
            add(f"census_a{a}_puma{p}_narrowest_by_o", ";".join(f"o{int(o)}:{n}" for o, n in zip(g.o, g.narrowest.fillna("none"))), nsrc, "")
            for _, r in g.iterrows():
                if isinstance(r.narrowest, str):
                    add(f"census_a{a}_puma{p}_o{int(r.o)}_narrowest_margin", f"{r.narrowest}>{r.runner_up}:{r.margin:.6g}+-{r.margin_mcse:.3g}" if isinstance(r.runner_up, str) else r.narrowest, nsrc, "")
    for a in (0.1, 0.2):
        for p in sorted(C.n_puma.unique()):
            for o in sorted(C.o.unique()):
                if o > 20:
                    continue
                kk = dict(n_puma=int(p))
                g, h = width(C, kk, "GHCP", o, a), width(C, kk, "HCP", o, a)
                add(f"census_a{a}_puma{p}_o{o}_GHCP_width", g, src, "")
                add(f"census_a{a}_puma{p}_o{o}_HCP_width", h, src, "")
                add(f"census_a{a}_puma{p}_o{o}_GHCP_finite_frac", float(cell(C, kk, "GHCP", o, a).finite_frac), src, "")
                add(f"census_a{a}_puma{p}_o{o}_HCP_finite_frac", float(cell(C, kk, "HCP", o, a).finite_frac), src, "")


COL = {"released_ghcp": "#1f5fa8", "ghcp": "#7fa7d6", "hcp": "#555555", "released_stdcp": "#c98a1b",
       "within_plain": "#9a9a9a", "within_full": "#b2182b",
       "GHCP": "#1f5fa8", "HCP": "#555555", "Std-CP": "#c98a1b"}
LAB = {"released_ghcp": "GHCP (released code)", "ghcp": "GHCP (this track)", "hcp": "HCP",
       "released_stdcp": "Std-CP (released code)", "within_plain": "within-group split",
       "within_full": "within-group full conformal", "GHCP": "GHCP", "HCP": "HCP", "Std-CP": "Std-CP"}


def style():
    import matplotlib as mpl
    mpl.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7,
                         "xtick.labelsize": 6, "ytick.labelsize": 6, "axes.spines.top": False,
                         "axes.spines.right": False, "savefig.dpi": 300})


def fig_fixed(S, NV, out):
    import matplotlib.pyplot as plt
    style()
    from matplotlib.colors import ListedColormap
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw=dict(width_ratios=[1.15, 1], wspace=0.45))
    ax = axes[0]
    k20 = S[(S.design == "fixedN21") & (S.K == 20) & np.isclose(S.alpha, 0.1)]
    for m in ("hcp", "released_ghcp", "released_stdcp", "within_plain", "within_full"):
        d = k20[(k20.method == m) & (k20.finite_frac == 1.0)].sort_values("o")
        ax.plot(d.o, d.width_mean_finite, "-o", ms=3, lw=1.6 if m == "within_full" else 1.0, color=COL[m], label=LAB[m])
    ax.set_xlabel("labelled units in the target group, o")
    ax.set_ylabel("mean interval width")
    ax.set_title("a  Fixed design, K = 20, 90%", loc="left")
    ax.set_ylim(bottom=0)
    ax.margins(x=0.04)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(-0.02, -0.2), ncol=2, columnspacing=1.0)
    ax = axes[1]
    v = NV[(NV.setting == "sim") & (NV.design == "fixedN21") & np.isclose(NV.alpha, 0.1)]
    cats = ["none", "hcp", "released_ghcp", "ghcp", "released_stdcp", "within_full"]
    Ks = sorted(v.K.unique()); os_ = sorted(v.o.unique())
    M = np.full((len(Ks), len(os_)), 0)
    for _, r in v.iterrows():
        M[Ks.index(r.K), os_.index(r.o)] = cats.index(r.narrowest if isinstance(r.narrowest, str) else "none")
    cmap = ListedColormap(["#eeeeee"] + [COL[c] for c in cats[1:]])
    ax.imshow(M, aspect="auto", cmap=cmap, vmin=-0.5, vmax=len(cats) - 0.5, origin="lower")
    ax.set_xticks(range(len(os_)), [str(int(o)) for o in os_])
    ax.set_yticks(range(len(Ks)), [str(int(k)) for k in Ks])
    ax.set_xlabel("labelled units in the target group, o")
    ax.set_ylabel("reference groups, K")
    ax.set_title("b  Narrowest valid method, 90%", loc="left")
    used = sorted(set(M.ravel()))
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=cmap(i), label=("no method finite in every replicate" if cats[i] == "none" else LAB[cats[i]])) for i in used],
              frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig_census(C, out):
    import matplotlib.pyplot as plt
    style()
    P = sorted(C.n_puma.unique())
    fig, axes = plt.subplots(1, len(P), figsize=(1.6 * len(P) + 0.6, 2.6), sharey=True, sharex=True, gridspec_kw=dict(wspace=0.06))
    axes = np.atleast_1d(axes)
    for ax, p in zip(axes, P):
        d0 = C[(C.n_puma == p) & np.isclose(C.alpha, 0.1)]
        for m in ("HCP", "GHCP", "Std-CP", "within_plain", "within_full"):
            d = d0[(d0.method == m) & (d0.finite_frac == 1.0)].sort_values("o")
            ax.plot(d.o, d.width_mean_finite / 1000, "-o", ms=2.5, lw=1.6 if m == "within_full" else 1.0, color=COL[m], label=LAB[m])
        ax.set_title(f"{p} PUMAs", loc="left")
        ax.set_xlim(-1, 21)
        ax.set_xticks([0, 5, 10, 15, 20])
    axes[0].set_ylabel("mean interval width ($1,000)")
    axes[0].set_ylim(bottom=0)
    axes[-1].legend(frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.supxlabel("labelled persons in the target PUMA, o", fontsize=8, y=-0.04)
    fig.suptitle("Census task, 90%: methods finite in every replicate", x=0.01, y=1.06, ha="left", fontsize=8)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main(a):
    os.makedirs(a.out, exist_ok=True)
    NV = pd.read_csv(os.path.join(a.inp, "w2_narrowest_valid.csv"))
    have_sim = os.path.exists(os.path.join(a.inp, "w2_sim_designs.csv"))
    have_cen = os.path.exists(os.path.join(a.inp, "w2_census.csv"))
    if have_sim:
        S = pd.read_csv(os.path.join(a.inp, "w2_sim_designs.csv"))
        sim_numbers(S, NV)
        fig_fixed(S, NV, os.path.join(a.out, "fig_w2_fixed_design.png"))
    if have_cen:
        C = pd.read_csv(os.path.join(a.inp, "w2_census.csv"))
        census_numbers(C, NV)
        fig_census(C, os.path.join(a.out, "fig_w2_census.png"))
    pd.DataFrame(NUM).to_csv(os.path.join(a.out, "w2_report_numbers.csv"), index=False)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--out", required=True)
    main(p.parse_args())
