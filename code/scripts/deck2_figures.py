#!/usr/bin/env python
"""Build the figures for the second advisor deck into figures/deck2/.

Every figure is drawn from committed result files. Labels use plain names, with no stage or
rule codes. Run from the repository root:  python code/scripts/deck2_figures.py
"""
import math
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "figures/deck2"
os.makedirs(OUT, exist_ok=True)

# palette: three categorical slots that pass the all-pairs colour-vision checks, plus neutrals
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
GREY, INK, MUTED, GRID, SURF = "#8a8a86", "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 13, "axes.titlesize": 14, "axes.titleweight": "bold",
    "axes.labelsize": 13, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "legend.frameon": False,
    "lines.linewidth": 2.0, "lines.markersize": 7,
})

TASK = {"CCRCC": "Kidney cancer (Visium)", "INDIANA_KIDNEY": "Kidney, one lab (Visium)",
        "LUNG_XENIUM": "Lung (Xenium)", "ACS_STATES": "ACS income, states", "ACS_CA_PUMA": "ACS income, CA areas",
        "ACS": "ACS income, states"}
ENC = {"hoptimus0": "H-optimus-0", "uni_v2": "UNI2", "resnet50": "ResNet50", "package": "income model",
       "permuted": "permuted (no information)"}
ENC_COL = {"hoptimus0": BLUE, "uni_v2": ORANGE, "resnet50": AQUA, "package": BLUE, "permuted": GREY}


def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote", f"{OUT}/{name}.png")


def nominal(ax, y=0.9, label="nominal 0.90"):
    ax.axhline(y, color=INK, lw=1, ls=(0, (4, 3)))
    ax.text(ax.get_xlim()[1], y, " " + label, va="center", ha="left", color=MUTED, fontsize=11)


# ------------------------------------------------------------------ f01 coverage by calibration design
def f01():
    a = pd.read_csv("results/round3/A1_coverage/a1_coverage_by_design.csv")
    a = a[a.score == "abs"].set_index("design")
    order = ["random", "slide_out", "donor", "patient"]
    labs = ["random\nspots", "held-out\nslide", "held-out\ndonor", "held-out\npatient\n(as shipped)"]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), gridspec_kw=dict(width_ratios=[4, 2.2], wspace=0.3))
    ax = axes[0]
    v = [a.loc[d, "coverage_mean"] for d in order]
    ax.bar(labs, v, width=0.55, color=BLUE)
    for i, x in enumerate(v):
        ax.text(i, x + 0.004, f"{x:.2f}", ha="center", va="bottom", fontsize=12)
    ax.set_ylim(0.6, 0.95); ax.set_ylabel("coverage of a 90% interval")
    ax.set_title("Coverage depends on how the\ncalibration data are held out", loc="left")
    ax.grid(axis="x", visible=False); nominal(ax, label="")
    b = pd.read_csv("results/round3/A2_conditional/a2_unit_intervention.csv")
    b = b[(b.scope == "fold") & (b.score == "abs")]
    ax = axes[1]
    v = [b.coverage__C_unit.mean(), b.coverage__C_block.mean()]
    ax.bar(["other\ndonors", "blocks of the\ntraining slides"], v, width=0.55, color=BLUE)
    for i, x in enumerate(v):
        ax.text(i, x + 0.004, f"{x:.2f}", ha="center", va="bottom", fontsize=12)
    ax.set_ylim(0.6, 0.95); ax.set_title("Same model, calibrated on", loc="left")
    ax.grid(axis="x", visible=False); nominal(ax)
    save(fig, "f01_coverage_by_design")


# ------------------------------------------------------------------ f02 spot-level against donor-level intervals
def f02():
    b = pd.read_csv("results/round3/B2_semisynthetic/b2_coverage.csv")
    c = b[b.estimator == "classical"].groupby("variance").coverage.mean()
    labs = ["spots treated as\nindependent", "donor bootstrap", "donor-clustered\nvariance, t reference"]
    v = [c["iid"], c["boot"], c["cluster"]]
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.bar(labs, v, width=0.55, color=BLUE)
    for i, x in enumerate(v):
        ax.text(i, x + 0.012, f"{x:.2f}", ha="center", va="bottom", fontsize=12)
    ax.set_ylim(0, 1.05); ax.set_ylabel("coverage of a 90% confidence interval")
    ax.set_title("A population quantity estimated from spots:\nwhich interval covers?", loc="left")
    ax.grid(axis="x", visible=False); nominal(ax)
    save(fig, "f02_spot_vs_donor_interval")


# ------------------------------------------------------------------ f03 the two labelling regimes, schematic
def f03():
    rng = np.random.default_rng(7)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    G, per = 8, 28
    pts = [(rng.uniform(0.12, 0.88, per), rng.uniform(0.08, 0.92, per)) for _ in range(G)]
    for ax, title, mode in [(axes[0], "Regime A: label a few clusters fully", "A"),
                            (axes[1], "Regime B: label a few units in every cluster", "B")]:
        for g in range(G):
            x0 = g * 1.15
            ax.add_patch(plt.Rectangle((x0, 0), 1, 1, fill=False, ec=MUTED, lw=1.2))
            xs, ys = pts[g]
            if mode == "A":
                lab = np.ones(per, bool) if g in (1, 5) else np.zeros(per, bool)
            else:
                lab = np.zeros(per, bool); lab[:4] = True
            ax.scatter(x0 + xs[~lab], ys[~lab], s=22, facecolor="none", edgecolor=GREY, lw=1)
            ax.scatter(x0 + xs[lab], ys[lab], s=26, color=BLUE)
            ax.text(x0 + 0.5, -0.1, f"{g + 1}", ha="center", va="top", fontsize=11, color=MUTED)
        ax.set_xlim(-0.1, G * 1.15); ax.set_ylim(-0.3, 1.1); ax.axis("off")
        ax.set_title(title, loc="left")
    axes[0].scatter([], [], s=26, color=BLUE, label="labelled unit (measured)")
    axes[0].scatter([], [], s=22, facecolor="none", edgecolor=GREY, label="unlabelled unit (prediction only)")
    axes[0].legend(loc="upper left", bbox_to_anchor=(0, -0.08), ncol=2, fontsize=11)
    save(fig, "f03_two_regimes_schematic")


# ------------------------------------------------------------------ f04 interval coverage in simulation
def f04():
    q = pd.read_csv("results/round4/ppi/Q1_estimator/q1_coverage_by_G.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), sharey=True, gridspec_kw=dict(wspace=0.25))
    ax = axes[0]
    for rule, lab, col, mk in [("c_crossfit", "cross-fitted", BLUE, "o"),
                               ("a_b1", "tuned on the same clusters (unit-level)", ORANGE, "s"),
                               ("b_cluster", "tuned on the same clusters (cluster-level)", AQUA, "^")]:
        s = q[(q.target == "super") & (q.form == "complement") & (q.lambda_rule == rule) & (q.interval == "CR1_t") & (~q.fpc)].sort_values("G_L")
        ax.plot(s.G_L, s.cov_median, color=col, marker=mk, label=lab)
    ax.set_title("How the weight is tuned", loc="left"); ax.set_xlabel("labelled clusters"); ax.set_ylabel("coverage of a 90% interval")
    ax.set_xticks([4, 6, 8, 12, 20]); ax.set_ylim(0.84, 1.005); ax.legend(loc="upper left", bbox_to_anchor=(0, -0.2), fontsize=10.5)
    nominal(ax, label="")
    ax = axes[1]
    s1 = q[(q.target == "design") & (q.form == "textbook") & (q.lambda_rule == "c_crossfit") & (q.interval == "textbook_t") & (q.fpc)].sort_values("G_L")
    s0 = q[(q.target == "design") & (q.form == "complement") & (q.lambda_rule == "a_b1") & (q.interval == "CR1_t") & (~q.fpc)].sort_values("G_L")
    ax.plot(s1.G_L, s1.cov_median, color=BLUE, marker="o", label="with finite-population correction")
    ax.plot(s0.G_L, s0.cov_median, color=ORANGE, marker="s", label="without (earlier form)")
    ax.set_title("When the clusters at hand are the population (24)", loc="left"); ax.set_xlabel("labelled clusters, of 24")
    ax.set_xticks([4, 6, 8, 12, 20]); ax.legend(loc="upper left", bbox_to_anchor=(0, -0.2), fontsize=10.5)
    nominal(ax)
    save(fig, "f04_interval_coverage_simulation")


# ------------------------------------------------------------------ f05 floor against observed
def _gain_table(nL=8):
    r = pd.read_csv("results/round4/ppi/Q2_theory/q2_cluster_r2.csv")
    r = r[(r.scale == "z") & (r.population == "donor") & (r.estimand == "theta3")]
    R = r.groupby(["vtag", "arm"])[["R2_cluster_raw", "R2_within"]].median().reset_index()
    t = pd.read_csv("results/round4/ppi/Q4a_recompute/q4a_table61.csv")
    t = t[(t.estimand == "theta3") & (t.population == "donor") & (t.target == "design")
          & (t.lambda_rule == "c_crossfit_design") & (t.interval == "textbook_t|fpc|lin")]
    return R, t


GROUP = {"CCRCC": ("Visium kidney tasks", BLUE, "o"), "INDIANA_KIDNEY": ("Visium kidney tasks", BLUE, "o"),
         "LUNG_XENIUM": ("Lung Xenium", ORANGE, "s"), "ACS_STATES": ("ACS income", AQUA, "^"), "ACS_CA_PUMA": ("ACS income", AQUA, "^")}


def f05():
    R, t = _gain_table()
    fig, ax = plt.subplots(figsize=(6.6, 5.6))
    ax.plot([0, 1.1], [0, 1.1], color=INK, lw=1, ls=(0, (4, 3)))
    ax.text(0.33, 0.30, "theoretical floor", rotation=41, color=MUTED, fontsize=11, ha="center", va="top")
    ax.axhline(1, color=GREY, lw=1)
    ax.text(0.02, 1.012, "no gain", color=MUTED, fontsize=11)
    seen = set()
    for row in R.itertuples():
        if row.vtag not in GROUP:
            continue
        x = t[(t.vtag == row.vtag) & (t.arm == row.arm) & (t.n_L == 8)]
        if len(x) != 1:
            continue
        y = float(x.emp_var_ratio_median.iloc[0]); fl = 1 - row.R2_cluster_raw
        if row.arm == "permuted":
            ax.scatter(fl, y, s=70, facecolor="none", edgecolor=GREY, lw=1.6, marker="D",
                       label="permuted predictor" if "p" not in seen else None); seen.add("p")
        else:
            lab, col, mk = GROUP[row.vtag]
            ax.scatter(fl, y, s=80, color=col, marker=mk, edgecolor=SURF, lw=1.2, label=lab if lab not in seen else None); seen.add(lab)
    ax.set_xlim(0, 1.1); ax.set_ylim(0, 1.12)
    ax.set_xlabel(r"$1 - R^2_{\mathrm{cluster}}$  (measured on all clusters)")
    ax.set_ylabel("observed variance ratio, PPI / classical\n(8 labelled clusters)")
    ax.set_title("Gain follows cluster-level accuracy", loc="left")
    ax.legend(loc="lower right", fontsize=11)
    save(fig, "f05_gain_floor_vs_observed")


# ------------------------------------------------------------------ f06 gene axis
def f06():
    g = pd.read_csv("results/round4/ppi/Q4_tables/q4_gene_axis.csv")
    g = g[(g.vtag == "CCRCC") & (g.arm == "uni_v2") & (g.setting == "A_design_cd_lin")]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True, gridspec_kw=dict(wspace=0.12))
    for ax, col, lab in [(axes[0], "R2_cluster_corrected", r"cluster-level $R^2$ of the gene"), (axes[1], "pearson_unit", "unit-level correlation of the gene")]:
        ax.scatter(g[col], g.width_ratio, s=14, color=BLUE, alpha=0.55, edgecolor="none")
        ax.axhline(1, color=GREY, lw=1); ax.set_xlabel(lab)
        rho = g[[col, "width_ratio"]].corr(method="spearman").iloc[0, 1]
        ax.text(0.97, 0.95, f"Spearman {rho:.2f}", transform=ax.transAxes, ha="right", va="top", fontsize=12)
    axes[0].set_ylabel("interval width, PPI / classical")
    axes[0].set_title(f"One point per gene ({len(g)} genes, kidney cancer, UNI2)", loc="left")
    save(fig, "f06_gain_across_genes")


# ------------------------------------------------------------------ f07 ratio by number of labelled clusters
def f07():
    R, t = _gain_table()
    tasks = ["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM", "ACS_STATES"]
    fig, axes = plt.subplots(1, 4, figsize=(14, 4.3), sharey=True, gridspec_kw=dict(wspace=0.1))
    for ax, v in zip(axes, tasks):
        for arm in ["hoptimus0", "uni_v2", "resnet50", "package", "permuted"]:
            s = t[(t.vtag == v) & (t.arm == arm) & (t.n_L >= 6)].sort_values("n_L")
            if not len(s):
                continue
            ax.plot(s.n_L, s.emp_var_ratio_median, color=ENC_COL[arm], marker="o" if arm != "permuted" else "D",
                    ls="-" if arm != "permuted" else (0, (2, 2)), label=ENC[arm])
            rr = R[(R.vtag == v) & (R.arm == arm)]
            if arm != "permuted" and len(rr):
                ax.plot([s.n_L.max() + 0.6, s.n_L.max() + 1.6], [1 - rr.R2_cluster_raw.iloc[0]] * 2, color=ENC_COL[arm], lw=3, solid_capstyle="butt")
        ax.axhline(1, color=GREY, lw=1); ax.set_title(TASK[v], loc="left", fontsize=12.5)
        ax.set_xlabel("labelled clusters"); ax.set_xticks([6, 8, 12, 16]); ax.set_xlim(5, 18.5); ax.set_ylim(0, 1.15)
    axes[0].set_ylabel("variance ratio, PPI / classical")
    axes[0].text(17.6, 0.46, "floors", ha="center", va="top", fontsize=10, color=MUTED)
    h, l = [], []
    for ax in (axes[0], axes[3]):
        hh, ll = ax.get_legend_handles_labels()
        for a, b in zip(hh, ll):
            if b not in l:
                h.append(a); l.append(b)
    fig.legend(h, l, loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.1), fontsize=11)
    fig.suptitle("Observed ratio by number of labelled clusters; short bars on the right mark each predictor's floor",
                 x=0.07, ha="left", fontsize=13, fontweight="bold", y=1.02)
    save(fig, "f07_ratio_by_labelled_clusters")


# ------------------------------------------------------------------ f08 tuning cost, observed against predicted
def f08():
    th = pd.read_csv("results/round4/ppi/Q2_theory/theorem_v3/q2_sim_theorem_v3.csv")
    fig, ax = plt.subplots(figsize=(5.8, 5.4))
    lim = 0.45
    ax.plot([0, lim], [0, lim], color=INK, lw=1, ls=(0, (4, 3)))
    for GL, col, mk in [(6, BLUE, "o"), (12, ORANGE, "s")]:
        s = th[th.G_L == GL]
        ax.scatter(s.tuning_cost_pred, s.tuning_cost_obs, s=70, color=col, marker=mk, edgecolor=SURF, lw=1.2, label=f"{GL} labelled clusters")
    ax.set_xlim(0, lim); ax.set_ylim(0, lim)
    ax.set_xlabel(r"predicted cost,  $\mathrm{MSE}(\hat\lambda)\,\sigma_p^2/\sigma_u^2$")
    ax.set_ylabel("observed excess over the best-weight ratio")
    ax.set_title("Cost of estimating the weight (simulation)", loc="left"); ax.legend(loc="upper left", fontsize=11)
    save(fig, "f08_tuning_cost_simulation")


# ------------------------------------------------------------------ f09 regime B against regime A
def f09():
    f = pd.read_csv("results/round4/ppi/Q3_regimes/fig_q3_source_points.csv")
    f = f[f.target == "super"]
    tasks = ["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.3), gridspec_kw=dict(wspace=0.32))
    for ax, v in zip(axes, tasks):
        base = f[(f.vtag == v) & (f.regime == "A_nL8") & (f.budget == 2400)].emp_var_median.iloc[0]
        for reg, col, mk, lab in [("A_nL8", ORANGE, "s", "A: 8 clusters fully labelled"), ("B", BLUE, "o", "B: a few units in every cluster")]:
            s = f[(f.vtag == v) & (f.regime == reg)].sort_values("budget")
            ax.plot(s.budget, s.emp_var_median / base, color=col, marker=mk, label=lab)
        ax.set_title(TASK[v], loc="left", fontsize=12.5); ax.set_xlabel("labelled units in total"); ax.set_xticks([2400, 4800, 9600])
        ax.set_ylim(0, None)
    axes[0].set_ylabel("variance of the PPI estimate\n(relative to regime A at 2,400)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.12), fontsize=11)
    save(fig, "f09_regime_A_vs_B")


# ------------------------------------------------------------------ f10 regime B, predicted against observed
def f10():
    d = pd.read_csv("results/summary/deck2_numbers.csv").set_index("id").value
    fig, ax = plt.subplots(figsize=(5.8, 5.4))
    ax.plot([0, 1], [0, 1], color=INK, lw=1, ls=(0, (4, 3)))
    seen = set()
    for k in d.index:
        if not k.startswith("regimeB_width|"):
            continue
        _, v, arm = k.split("|")
        x = d[f"regimeB_predicted|{v}|{arm}"]; y = d[k]
        if arm == "permuted":
            ax.scatter(x, y, s=70, facecolor="none", edgecolor=GREY, lw=1.6, marker="D", label="permuted predictor" if "p" not in seen else None); seen.add("p")
        else:
            lab, col, mk = GROUP[v]
            ax.scatter(x, y, s=80, color=col, marker=mk, edgecolor=SURF, lw=1.2, label=lab if lab not in seen else None); seen.add(lab)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel(r"predicted,  $\sqrt{1 - R^2_{\mathrm{within}}}$"); ax.set_ylabel("observed interval width, PPI / classical")
    ax.set_title("Regime B: gain follows within-cluster accuracy", loc="left"); ax.legend(loc="upper left", fontsize=11)
    save(fig, "f10_regimeB_predicted_vs_observed")


# ------------------------------------------------------------------ f11 prediction sets against K
def f11():
    c = pd.read_csv("results/round4/conformal/C3_real/c3_report_numbers.csv")
    rows = []
    for K in [4, 6, 8, 10, 12, 14, 16, 18, 20]:
        sc = f"CCRCC alpha=0.1 K={K}"
        g = lambda q: float(c[(c.quantity == q) & (c.scope == sc)].value.iloc[0])
        rows.append((K, g("hcp coverage, mean over encoders"), g("pooled coverage, mean over encoders"), g("hcp/pooled mean width, mean over encoders")))
    d = pd.DataFrame(rows, columns=["K", "hcp_cov", "pool_cov", "ratio"])
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw=dict(wspace=0.3))
    ax = axes[0]
    ax.plot(d.K, d.hcp_cov, color=BLUE, marker="o", label="hierarchical (valid)")
    ax.plot(d.K, d.pool_cov, color=ORANGE, marker="s", label="pooled (no guarantee)")
    ax.set_ylim(0.82, 1.01); ax.set_xlabel("calibration donors K"); ax.set_ylabel("coverage of a 90% prediction set")
    ax.set_title("Coverage", loc="left"); ax.legend(loc="center right", fontsize=11); nominal(ax, label="")
    ax = axes[1]
    fin = d[d.ratio.notna()]
    ax.plot(fin.K, fin.ratio, color=BLUE, marker="o")
    ax.axvspan(3.5, 8.9, color=GRID, alpha=0.7, lw=0)
    ax.text(6.2, 1.5, "infinite\n(K + 1 < 1/α)", ha="center", va="center", color=MUTED, fontsize=11)
    ax.axhline(1, color=GREY, lw=1); ax.set_xlim(3.5, 20.5); ax.set_ylim(0.9, 2.1)
    ax.set_xlabel("calibration donors K"); ax.set_ylabel("width, hierarchical / pooled")
    ax.set_title("Price of validity (kidney cancer)", loc="left")
    save(fig, "f11_prediction_sets_by_K")


# ------------------------------------------------------------------ f12 prediction sets against labelled test units
def f12():
    o = pd.read_csv("results/round4/conformal/C3_real/c3_o_sweep_by_task.csv")
    o = o[(o.alpha == 0.1) & (o.K == 10) & (o.score == "abs")]
    g = o.groupby(["task", "method", "o"])[["coverage", "width_mean", "finite"]].mean().reset_index()
    tasks = ["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM", "ACS"]
    fig, axes = plt.subplots(1, 4, figsize=(14, 4.3), gridspec_kw=dict(wspace=0.25))
    for ax, v in zip(axes, tasks):
        hcp = g[(g.task == v) & (g.method == "hcp") & (g.o == 0)].width_mean.iloc[0]
        ax.axhline(hcp, color=GREY, lw=2, ls=(0, (4, 3)), label="hierarchical, no labelled units")
        for m, col, mk, lab in [("ghcp", ORANGE, "s", "generalized hierarchical (GHCP)"),
                                ("within_plain", BLUE, "o", "split within the new cluster"),
                                ("within", AQUA, "^", "split within, recentred")]:
            s = g[(g.task == v) & (g.method == m) & (g.finite > 0.999)].sort_values("o")
            ax.plot(s.o, s.width_mean, color=col, marker=mk, label=lab)
        ax.set_xscale("log"); ax.set_xticks([5, 10, 25, 50, 100, 200]); ax.set_xticklabels(["5", "10", "25", "50", "100", "200"])
        ax.minorticks_off(); ax.set_ylim(0, None); ax.set_title(TASK[v], loc="left", fontsize=12.5); ax.set_xlabel("labelled units, new cluster")
    axes[0].set_ylabel("mean width of a valid 90% set")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.12), fontsize=11)
    fig.suptitle("10 calibration clusters. A method is drawn only where its set is finite.", x=0.07, ha="left", fontsize=13, fontweight="bold", y=1.02)
    save(fig, "f12_prediction_sets_by_labelled_units")


# ------------------------------------------------------------------ f13 lower bound
def f13():
    lb = pd.read_csv("results/round4/conformal/C2_candidates/lower_bound/c2_lb_beta_star.csv")
    lb = lb[(lb.alpha == 0.1) & (lb.K <= 12)]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), gridspec_kw=dict(wspace=0.3))
    ax = axes[0]
    K = np.arange(1, 13)
    ax.bar(K, np.maximum(0, 1 - 0.1 * (K + 1)), width=0.6, color=BLUE)
    ax.set_xlabel("calibration clusters K"); ax.set_ylabel("probability an infinite set is forced")
    ax.set_title(r"$1 - \alpha(K+1)$ at $\alpha = 0.1$", loc="left"); ax.set_xticks(K); ax.grid(axis="x", visible=False)
    ax = axes[1]
    ax.plot(lb.K, lb.min_coverage_any_valid, color=BLUE, marker="o")
    ax.set_xlabel("calibration clusters K"); ax.set_ylabel("least coverage of any finite valid method")
    ax.set_title("A finite set must over-cover", loc="left"); ax.set_xticks(lb.K); ax.set_ylim(0.89, 1.005); nominal(ax, label="")
    save(fig, "f13_lower_bound_small_K")


if __name__ == "__main__":
    for fn in [f01, f02, f03, f04, f05, f06, f07, f08, f09, f10, f11, f12, f13]:
        fn()
