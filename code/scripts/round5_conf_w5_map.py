#!/usr/bin/env python
"""Round 5, prediction-set track, W5: the map as one table, on one axis.

Reads the three narrowest-valid tables the track has already written and committed
  simulation      results/round5/conformal/W1_sim/merged/w1_narrowest_valid.csv
  ghcp_designs    results/round5/conformal/W2_ghcp_settings/w2_narrowest_valid.csv
  real_data       results/round5/conformal/W3_real/merged/w3_map_by_task.csv
and writes into results/round5/conformal/W5_map/
  w5_map.csv            one row per (source, setting, K, alpha, o): narrowest valid method, its size,
                        the runner-up, the margin, and the number of clusters (groups, donors) each of
                        HCP, the narrowest and the runner-up calibrates on and fits its score on
  w5_method_groups.csv  the rule behind those counts, per source and method, with the code it is read from
  fig_w5_map_simulation.png, fig_w5_map_ghcp_designs.png, fig_w5_map_real_data.png  one per source

THE AXIS (W2 decisions memo, sections 3 item 3 and 5 item 7). Every row is placed by axis_n_cal_hcp,
the number of clusters HCP calibrates on in that setting. The per-method counts are columns
n_cal_<role> and n_fit_<role> for role in hcp, narrowest, runner_up. Units of the target cluster that
a within-cluster method calibrates on are in n_cal_units_<role>; they are not clusters.

THE COUNTS, read from the code (n is the number of reference groups K, or of PUMAs in the census):
  simulation (code/scripts/round4_conf_sim.py, round5_conf_w1_sim.py): scores come from the generator,
    no model is fitted, so every n_fit is 0. hcp and one_per calibrate on all K. ghcp and ghcp_noad
    (eta = 0, paper pool) calibrate on |S| - 1 where S = {k : N_k > o} (one pool group is the size
    donor); with N = 21, 100 or 500 that is K - 1 for every o < N; with N = unequal or data it is at
    most K - 1 and is recorded as K - 1 with n_cal_exact = False. within calibrates on o - floor(o/2)
    target units, within_plain and within_full on o; none on a cluster.
  ghcp_designs (released code, commit d1a69f4, methods/donor_hcp.py; this track's
    round5_conf_w2_wrapper.py; eta = alpha_selection = 0.5):
    released_hcp, hcp   get_hcp_train_cal_split at o = 0: p = 1 - 0.5, n_sel = ceil(n/2) groups
                        calibrate (the restricted pool), the other n - ceil(n/2) fit the forest.
    released_ghcp       get_donor_style_train_cal_split: S_tilde of ceil(n/2) + 1 groups, one is the
                        donor, ceil(n/2) calibrate; the n - ceil(n/2) - 1 groups outside S_tilde fit.
    ghcp                this track's paper pool (eq. 8): ceil(n/2) groups, one is the donor,
                        ceil(n/2) - 1 calibrate; the n - ceil(n/2) outside the pool fit the forest.
    released_stdcp      no group calibrates or fits: a local forest on o // 2 target units, calibrated
                        on the other o - o // 2 (run_acs_experiments._compute_std_cp_interval and the
                        simulation launcher's run_one_experiment).
    within_plain, within_full  calibrate on the o target units; the forest is the one fitted on the
                        n - ceil(n/2) groups outside this track's pool.
    These hold when every group has more than o units (the fixed design, N = 21, o <= 20, and every
    census PUMA at o <= 20). In the Poisson design (mean 25) groups with N_k <= o leave the pool, so the
    counts are the all-groups-eligible values and n_cal_exact = False for o > 0.
    Census method names GHCP, HCP and Std-CP are the released code's and are mapped to released_ghcp,
    released_hcp and released_stdcp.
  real_data (code/scripts/round4_conf_c3.py through round5_conf_w3.py): K calibration donors, the head
    fitted on n_T_donors training donors (the map's median over folds). hcp and one_per calibrate on K,
    ghcp and ghcp_noad (eta = 0) on K - 1 (every donor has more than o spots), every method's score
    is fitted on n_T_donors. within, within_plain and within_full calibrate on target units only.

NARROWEST AND RUNNER-UP are as each source's own table defines them (W1: half-width, with price; W2:
mean width over replicates finite in every replicate; W3: mean width, valid methods finite in every row,
one_per excluded). For W3 the runner-up is the second-narrowest by the same rule; margin is the
runner-up's size minus the narrowest's, margin_rel the margin over the narrowest's size.
"""
import math
import os

import numpy as np
import pandas as pd

ROOT = "results/round5/conformal"
OUT = os.path.join(ROOT, "W5_map")
CEN_NAMES = {"GHCP": "released_ghcp", "HCP": "released_hcp", "Std-CP": "released_stdcp"}
ORDER = ["hcp", "released_hcp", "ghcp", "ghcp_noad", "released_ghcp", "within", "released_stdcp",
         "within_plain", "within_full"]
COL = {"hcp": "#000000", "released_hcp": "#4d4d4d", "ghcp": "#1b6ca8", "ghcp_noad": "#8fbbd9",
       "released_ghcp": "#0b3c66", "within": "#c98a1b", "released_stdcp": "#7a5c1e",
       "within_plain": "#e8a87c", "within_full": "#8e2c1f"}
LABEL = {"hcp": "HCP", "released_hcp": "HCP, released code", "ghcp": "GHCP",
         "ghcp_noad": "GHCP, no size adjustment", "released_ghcp": "GHCP, released code",
         "within": "within donor, half split", "released_stdcp": "Std-CP, released code",
         "within_plain": "within donor, split", "within_full": "within donor, full conformal"}


def counts_sim(method, K, o, N):
    exact = str(N) in ("21", "100", "500")
    if method in ("hcp", "one_per"):
        return K, 0, 0, True
    if method in ("ghcp", "ghcp_noad"):
        return K - 1, 0, 0, exact
    if method == "within":
        return 0, 0, o - o // 2, True
    if method in ("within_plain", "within_full"):
        return 0, 0, o, True
    return np.nan, np.nan, np.nan, False


def counts_w2(method, n, o, exact):
    h = math.ceil(n / 2)
    if method in ("released_hcp", "hcp"):
        return h, n - h, 0, True
    if method == "released_ghcp":
        return h, n - h - 1, 0, exact
    if method == "ghcp":
        return h - 1, n - h, 0, exact
    if method == "released_stdcp":
        return 0, 0, o - o // 2, True
    if method in ("within_plain", "within_full"):
        return 0, n - h, o, exact
    return np.nan, np.nan, np.nan, False


def counts_w3(method, K, o, nT):
    if method in ("hcp", "one_per"):
        return K, nT, 0, True
    if method in ("ghcp", "ghcp_noad"):
        return K - 1, nT, 0, True
    if method == "within":
        return 0, nT, o - o // 2, True
    if method in ("within_plain", "within_full"):
        return 0, nT, o, True
    return np.nan, np.nan, np.nan, False


def attach(r, f, *args):
    for role in ("hcp", "narrowest", "runner_up"):
        m = r.get("hcp_name") if role == "hcp" else r.get(role)
        if not isinstance(m, str) or not m:
            r.update({f"n_cal_{role}": np.nan, f"n_fit_{role}": np.nan, f"n_cal_units_{role}": np.nan})
            continue
        c, fi, u, ex = f(m, *args)
        r.update({f"n_cal_{role}": c, f"n_fit_{role}": fi, f"n_cal_units_{role}": u})
        if role == "narrowest":
            r["n_cal_exact"] = ex
    r["axis_n_cal_hcp"] = r["n_cal_hcp"]
    return r


def sim_rows():
    d = pd.read_csv(os.path.join(ROOT, "W1_sim/merged/w1_narrowest_valid.csv"))
    rows = []
    for _, x in d.iterrows():
        r = dict(source="simulation", setting=x.cell_id, gen=x.gen, N=str(x.N), share=x.share, tau=x.tau,
                 n_puma=np.nan, task="", part=np.nan, K=int(x.K), alpha=x.alpha, o=int(x.o),
                 n_valid_finite=x.n_valid_finite, narrowest=x.narrowest if isinstance(x.narrowest, str) else "",
                 ties=x.ties, size_measure="half-width", narrowest_size=x.narrowest_halfwidth,
                 narrowest_price=x.narrowest_price, runner_up=x.runner_up if isinstance(x.runner_up, str) else "",
                 runner_up_size=x.runner_up_halfwidth, margin=x.margin, margin_rel=x.margin_rel,
                 margin_se=x.margin_se, margin_gt_2se=x.margin_gt_2se, hcp_name="hcp")
        rows.append(attach(r, counts_sim, int(x.K), int(x.o), x.N))
    return rows


def w2_rows():
    d = pd.read_csv(os.path.join(ROOT, "W2_ghcp_settings/w2_narrowest_valid.csv"))
    rows = []
    for _, x in d.iterrows():
        cen = x.setting == "census"
        n = int(x.n_puma if cen else x.K)
        nar = CEN_NAMES.get(x.narrowest, x.narrowest) if isinstance(x.narrowest, str) else ""
        run = CEN_NAMES.get(x.runner_up, x.runner_up) if isinstance(x.runner_up, str) else ""
        exact = cen or x.design == "fixedN21" or int(x.o) == 0
        setting = f"census_puma{n}" if cen else f"{x.design}_K{n}"
        r = dict(source="ghcp_designs", setting=setting, gen="census" if cen else x.design, N="", share=np.nan,
                 tau=np.nan, n_puma=n if cen else np.nan, task="", part=np.nan, K=n, alpha=x.alpha, o=int(x.o),
                 n_valid_finite=x.n_eligible, narrowest=nar, ties=x.ties, size_measure="width",
                 narrowest_size=x.narrowest_width, narrowest_price=np.nan, runner_up=run,
                 runner_up_size=x.runner_up_width, margin=x.margin,
                 margin_rel=x.margin / x.narrowest_width if x.narrowest_width else np.nan,
                 margin_se=x.margin_mcse, margin_gt_2se=x.margin_gt_2se, hcp_name="released_hcp")
        rows.append(attach(r, counts_w2, n, int(x.o), exact))
    return rows


def w3_rows():
    M = pd.read_csv(os.path.join(ROOT, "W3_real/merged/w3_map_by_task.csv"))
    M["valid"] = M.valid.astype(str) == "True"
    rows = []
    for (t, p, a, K, o), g in M.groupby(["task", "part", "alpha", "K", "o"]):
        c = g[g.valid & (g.method != "one_per") & (g.finite == 1.0) & np.isfinite(g.width_mean)]
        c = c.sort_values("width_mean")
        nT = float(g.n_T_donors.median())
        nar = c.method.iloc[0] if len(c) else ""
        run = c.method.iloc[1] if len(c) > 1 else ""
        ns = float(c.width_mean.iloc[0]) if len(c) else np.nan
        rs = float(c.width_mean.iloc[1]) if len(c) > 1 else np.nan
        r = dict(source="real_data", setting=f"{t}_part{p}", gen="", N="", share=np.nan, tau=np.nan,
                 n_puma=np.nan, task=t, part=int(p), K=int(K), alpha=a, o=int(o), n_valid_finite=len(c),
                 narrowest=nar, ties="", size_measure="width", narrowest_size=ns, narrowest_price=np.nan,
                 runner_up=run, runner_up_size=rs, margin=rs - ns, margin_rel=(rs - ns) / ns if ns else np.nan,
                 margin_se=np.nan, margin_gt_2se=np.nan, hcp_name="hcp", n_T_donors=nT)
        rows.append(attach(r, counts_w3, int(K), int(o), nT))
    return rows


def method_groups():
    R = []
    for m in ("hcp", "one_per", "ghcp", "ghcp_noad", "within", "within_plain", "within_full"):
        c = {"hcp": "K", "one_per": "K", "ghcp": "|S| - 1 (K - 1 when every N_k > o)", "ghcp_noad": "|S| - 1",
             "within": "0 (o - floor(o/2) target units)", "within_plain": "0 (o target units)",
             "within_full": "0 (o target units)"}[m]
        R.append(dict(source="simulation", method=m, calibrates_on=c, fits_score_on="0 (scores from the generator)",
                      code="code/scripts/round4_conf_sim.py hcp_q, ghcp_q, restricted_pool (eta = 0); round5_conf_w1_sim.py"))
    W2 = {"released_hcp": ("ceil(n/2) groups (restricted pool)", "n - ceil(n/2) groups",
                           "methods/donor_hcp.py get_hcp_train_cal_split (o = 0, alpha_selection 0.5)"),
          "hcp": ("ceil(n/2) groups (released_hcp's scores)", "n - ceil(n/2) groups", "round5_conf_w2_wrapper.py hcp"),
          "released_ghcp": ("ceil(n/2) groups (S_tilde of ceil(n/2) + 1 minus the donor)", "n - ceil(n/2) - 1 groups",
                            "methods/donor_hcp.py get_donor_style_train_cal_split, _select_s_tilde_with_tie_randomization"),
          "ghcp": ("ceil(n/2) - 1 groups (paper pool of ceil(n/2) minus the donor)", "n - ceil(n/2) groups",
                   "round5_conf_w2_wrapper.py ghcp; round4_conf_sim.restricted_pool (eta 0.5, rule paper)"),
          "released_stdcp": ("0 groups (o - o//2 target units)", "0 groups (o//2 target units, local forest)",
                             "simulation launcher run_one_experiment; code/marginal/run_acs_experiments.py _compute_std_cp_interval"),
          "within_plain": ("0 groups (o target units)", "n - ceil(n/2) groups", "round5_conf_w2_wrapper.py within_plain"),
          "within_full": ("0 groups (o target units)", "n - ceil(n/2) groups", "round5_conf_w2_wrapper.py within_full")}
    for m, (c, f, code) in W2.items():
        R.append(dict(source="ghcp_designs", method=m, calibrates_on=c, fits_score_on=f, code=code))
    for m in ("hcp", "one_per", "ghcp", "ghcp_noad", "within", "within_plain", "within_full"):
        c = {"hcp": "K donors", "one_per": "K donors", "ghcp": "K - 1 donors", "ghcp_noad": "K - 1 donors",
             "within": "0 (o - floor(o/2) target spots)", "within_plain": "0 (o target spots)",
             "within_full": "0 (o target spots)"}[m]
        R.append(dict(source="real_data", method=m, calibrates_on=c, fits_score_on="n_T_donors training donors",
                      code="code/scripts/round4_conf_c3.py (Fit, ghcp_cols), round5_conf_w3.py"))
    return pd.DataFrame(R)


def _style():
    import matplotlib as mpl
    mpl.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7,
                         "xtick.labelsize": 6, "ytick.labelsize": 6, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.titlelocation": "left", "savefig.dpi": 300})


def tiles(ax, D, title):
    os_ = sorted(D.o.unique())
    ys = sorted(D.axis_n_cal_hcp.unique())
    for _, r in D.iterrows():
        m = r.narrowest
        x, y = os_.index(r.o), ys.index(r.axis_n_cal_hcp)
        if isinstance(m, str) and m in COL:
            ax.add_patch(__import__("matplotlib").patches.Rectangle((x - 0.45, y - 0.45), 0.9, 0.9, color=COL[m], lw=0))
        else:
            ax.add_patch(__import__("matplotlib").patches.Rectangle((x - 0.45, y - 0.45), 0.9, 0.9, fill=False,
                                                                    hatch="////", ec="#bbbbbb", lw=0.3))
    ax.set_xlim(-0.6, len(os_) - 0.4); ax.set_ylim(-0.6, len(ys) - 0.4)
    ax.set_xticks(range(len(os_))); ax.set_xticklabels([str(o) for o in os_])
    ax.set_yticks(range(len(ys))); ax.set_yticklabels([f"{y:g}" for y in ys])
    ax.set_title(title)
    used = set(D.narrowest.dropna()) - {""}
    if (~D.narrowest.isin(list(COL))).any():
        used.add("none")
    return used


def legend(fig, used):
    from matplotlib.patches import Patch
    h = [Patch(color=COL[m], label=LABEL[m]) for m in ORDER if m in used]
    if "none" in used:
        h.append(Patch(fill=False, hatch="////", ec="#bbbbbb", label="no valid method finite in every replicate"))
    fig.legend(handles=h, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.0))


def figures(W):
    from matplotlib import pyplot as plt
    _style()
    ylab = "clusters HCP calibrates on"
    # simulation: normal tails, N = 21, tau = 0, 90%, by share
    S = W[(W.source == "simulation") & (W.gen == "normal") & (W.N == "21") & (W.tau == 0) & (W.alpha == 0.1)]
    shares = sorted(S.share.unique())
    fig, axes = plt.subplots(1, len(shares), figsize=(7.2, 2.9), sharey=True, gridspec_kw=dict(wspace=0.06))
    used = set()
    for ax, s in zip(np.atleast_1d(axes), shares):
        used |= tiles(ax, S[S.share == s], f"share {s:g}")
        ax.tick_params(axis="x", labelrotation=90)
    np.atleast_1d(axes)[0].set_ylabel(ylab)
    fig.supxlabel("labelled units in the target cluster, o (normal tails, 21 units per cluster, no scale spread, 90%; share = between-cluster share of score variance)", y=0.2, fontsize=7)
    legend(fig, used)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.9, bottom=0.33)
    fig.savefig(os.path.join(OUT, "fig_w5_map_simulation.png")); plt.close(fig)
    # GHCP designs: fixed, Poisson, census; 90%
    G = W[(W.source == "ghcp_designs") & (W.alpha == 0.1)]
    panels = [("fixedN21", "fixed design, 21 units per group"), ("poissonNmean25", "Poisson design, mean 25 units"),
              ("census", "census, PUMAs as groups")]
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.7), gridspec_kw=dict(wspace=0.25))
    used = set()
    for ax, (g, t) in zip(axes, panels):
        used |= tiles(ax, G[G.gen == g], t)
    axes[0].set_ylabel(ylab)
    fig.supxlabel("labelled units in the target group, o (90%)", y=0.2, fontsize=8)
    legend(fig, used)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.9, bottom=0.33)
    fig.savefig(os.path.join(OUT, "fig_w5_map_ghcp_designs.png")); plt.close(fig)
    # real data: part 1 at K = 10, part 2 at K > 10; 90%
    R = W[(W.source == "real_data") & (W.alpha == 0.1)]
    R = R[((R.part == 1) & (R.K == 10)) | ((R.part == 2) & (R.K > 10))]
    T = sorted(R.task.unique())
    names = {"CCRCC": "CCRCC, 24 donors", "CCRCC_23merged": "CCRCC, 23 merged", "INDIANA_KIDNEY": "Indiana kidney",
             "LUNG_XENIUM": "Lung (Xenium)"}
    fig, axes = plt.subplots(1, len(T), figsize=(7.2, 2.9), gridspec_kw=dict(wspace=0.25))
    used = set()
    for ax, t in zip(axes, T):
        used |= tiles(ax, R[R.task == t], names.get(t, t))
        ax.tick_params(axis="x", labelrotation=90)
    axes[0].set_ylabel(ylab + " (K)")
    fig.supxlabel("labelled spots in the target donor, o (K = 10: part 1 grid; K > 10: part 2 grid; 90%)", y=0.2, fontsize=8)
    legend(fig, used)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.9, bottom=0.33)
    fig.savefig(os.path.join(OUT, "fig_w5_map_real_data.png")); plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    W = pd.DataFrame(sim_rows() + w2_rows() + w3_rows())
    W = W.drop(columns=["hcp_name"])
    W.to_csv(os.path.join(OUT, "w5_map.csv"), index=False)
    method_groups().to_csv(os.path.join(OUT, "w5_method_groups.csv"), index=False)
    figures(W)
    print(W.groupby("source").size().to_string())


if __name__ == "__main__":
    main()
