"""Round 5 PPI, interval 3, E4b: merge the six task units and the simulation, run the acceptance
checks and score E4b.1 to E4b.4 (memo docs/decisions/round5_ppi_E4_decisions.md section 5; plan 8.4).

Reads only results/round5/ppi/E4b_rejective/ (unit directories <vtag>/<arm>/<estimand>_nL<n>/, never
_pilot or _draws), results/round5/ppi/E4b_rejective/_threshold/, and E4's
results/round5/ppi/E4_selection/ files. Run from the repository root.

Writes in results/round5/ppi/E4b_rejective/:
  e4b_grid.csv, e4b_genes.csv.gz, e4b_d2_diagnostics.csv, e4b_bootstrap.csv, e4b_skipped.csv,
  e4b_threshold.csv, e4b_acceptance.csv, e4b_prediction_cells.csv, e4b_prediction_scores.csv,
  e4b_report_numbers.csv, fig_e4b_summary.png
"""
import glob
import os

import numpy as np
import pandas as pd

D = "results/round5/ppi/E4b_rejective"
E4 = "results/round5/ppi/E4_selection"
TISSUE = ("CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM")
KC = ("CCRCC", "CCRCC_merged")
ENC = ("hoptimus0", "uni_v2", "resnet50")
LIN, XF = "textbook_t|fpc|lin", "textbook_t|fpc|lin|xf"
NUM = []


def num(name, value, source):
    NUM.append(dict(name=name, value=value, source=source))


def cat(kind):
    fs = [f for f in glob.glob(f"{D}/*/*/*/{kind}__*") if "/_pilot" not in f and "/_draws" not in f
          and "/_threshold" not in f]
    parts = []
    for f in sorted(fs):
        if os.path.getsize(f) > 1:
            try:
                parts.append(pd.read_csv(f, low_memory=False))
            except pd.errors.EmptyDataError:
                pass
    return pd.concat(parts, ignore_index=True, sort=False) if parts else pd.DataFrame()


def main():
    grid = cat("e4b_rejective")
    genes = cat("e4b_rejective_genes")
    diag = cat("e4b_d2_diagnostics")
    boot = cat("e4b_bootstrap")
    skip = cat("e4b_skipped")
    for name, df in (("grid", grid), ("d2_diagnostics", diag), ("bootstrap", boot), ("skipped", skip)):
        df.to_csv(f"{D}/e4b_{name}.csv", index=False)
    genes.to_csv(f"{D}/e4b_genes.csv.gz", index=False)
    thf = sorted(glob.glob(f"{D}/_threshold/*/*/e4b_threshold__*.csv"))
    thr = pd.concat([pd.read_csv(f) for f in thf], ignore_index=True) if thf else pd.DataFrame()
    thr.to_csv(f"{D}/e4b_threshold.csv", index=False)
    full = grid[grid["n_sub"] == grid["n_draws"]].copy() if "n_sub" in grid else grid
    full = grid[grid["n_sub"] > 200].copy()
    acc = []
    # acceptance 1: first 200 draws of D0 and D1 against E4, at the E0 tolerances
    e4 = pd.read_csv(f"{E4}/e4_selection_grid.csv", low_memory=False)
    keys = ["vtag", "arm", "estimand", "n_L", "design", "balance", "rule", "interval"]
    s200 = grid[(grid["n_sub"] <= 200) & grid["design"].isin(["D0", "D1"])]
    j = s200.merge(e4[e4["design"].isin(["D0", "D1"])], on=keys, suffixes=("", "_e4"))
    dc = (j[["coverage_median", "coverage_mean"]].values - j[["coverage_median_e4", "coverage_mean_e4"]].values)
    rel = []
    for c in ("emp_var_median", "est_var_over_emp_var_median", "width_median"):
        rel.append(np.abs(j[c] / j[c + "_e4"] - 1).values)
    rel = np.nanmax(np.vstack(rel), 0) if len(j) else np.array([])
    ok1 = (np.nanmax(np.abs(dc), 1) <= 0.005) & (rel <= 1e-5) if len(j) else np.array([], bool)
    n_cmp = len(s200[s200["balance"] != "perm_cluster"])
    acc.append(dict(check="1 D0 and D1 first 200 draws reproduce E4", n=len(j), n_pass=int(ok1.sum()),
                    worst_abs_coverage=float(np.nanmax(np.abs(dc))) if len(j) else np.nan,
                    worst_rel=float(np.nanmax(rel)) if len(j) else np.nan, passed=bool(ok1.all() and len(j) == n_cmp),
                    note=f"{n_cmp} comparable rows (perm_cluster excluded), {len(j)} matched"))
    if len(thr):
        acc.append(dict(check="1 D2 threshold change, E4b over E4 (median over genes)", n=len(thr), n_pass=np.nan,
                        worst_abs_coverage=np.nan, worst_rel=np.nan, passed=np.nan,
                        note=f"ratio median {thr['ratio_E4b_over_E4_median'].median():.3f}, range "
                             f"{thr['ratio_E4b_over_E4_median'].min():.3f} to {thr['ratio_E4b_over_E4_median'].max():.3f}"))
        num("acc1|threshold_ratio|median", thr["ratio_E4b_over_E4_median"].median(), "e4b_threshold.csv")
        num("acc1|threshold_ratio|min", thr["ratio_E4b_over_E4_median"].min(), "e4b_threshold.csv")
        num("acc1|threshold_ratio|max", thr["ratio_E4b_over_E4_median"].max(), "e4b_threshold.csv")
    d2s = grid[(grid["n_sub"] <= 200) & (grid["design"] == "D2")].merge(
        e4[e4["design"] == "D2"], on=keys + ["p_a"], suffixes=("", "_e4"))
    if len(d2s):
        r = d2s["emp_var_median"] / d2s["emp_var_median_e4"]
        acc.append(dict(check="1 D2 first 200 draws beside E4 (no tolerance)", n=len(d2s), n_pass=np.nan,
                        worst_abs_coverage=float((d2s["coverage_median"] - d2s["coverage_median_e4"]).abs().max()),
                        worst_rel=float((r - 1).abs().max()), passed=np.nan,
                        note=f"emp_var ratio median {r.median():.3f}, range {r.min():.3f} to {r.max():.3f}"))
    # acceptance 2
    a2 = diag["acc2_rej_minus_classical_max"].astype(float)
    acc.append(dict(check="2 rej_t point estimate equals the classical estimate", n=int(a2.notna().sum()),
                    n_pass=int((a2.dropna() <= 1e-5).sum()), worst_abs_coverage=np.nan, worst_rel=float(a2.max()),
                    passed=bool((a2.dropna() <= 1e-5).all()), note="largest |rej_t - classical| over draws and genes, per D2 cell"))
    # acceptance 3
    b = boot[(boot["design"] == "D2")].copy()
    b["within3"] = b["z_from_1"].abs() <= 3
    pc = b[(b["balance"] == "perm_cluster") & (b["support"] >= 1000)]
    acc.append(dict(check="3 perm_cluster D2 ratio within 3 bootstrap se of 1, support >= 1000", n=len(pc),
                    n_pass=int(pc["within3"].sum()), worst_abs_coverage=np.nan,
                    worst_rel=float(pc["z_from_1"].abs().max()) if len(pc) else np.nan,
                    passed=bool(pc["within3"].all()) if len(pc) else np.nan,
                    note="worst_rel holds the largest |z|"))
    for vt in sorted(pc["vtag"].unique()):
        x = pc[pc["vtag"] == vt]
        num(f"acc3|{vt}|n_cells", len(x), "e4b_bootstrap.csv"); num(f"acc3|{vt}|n_within3", int(x["within3"].sum()), "e4b_bootstrap.csv")
    pd.DataFrame(acc).to_csv(f"{D}/e4b_acceptance.csv", index=False)

    scores, cells = [], []

    def add(pid, verdict, text, c=None):
        scores.append(dict(prediction=pid, verdict=verdict, summary=text))
        if c is not None and len(c):
            cells.append(c.assign(prediction=pid))
    part = lambda ok: "held" if len(ok) and ok.all() else ("partly held" if len(ok) and ok.mean() >= 0.5 else "refuted")
    # E4b.1, simulation
    s = pd.read_csv(f"{D}/sim/e4b_sim.csv")
    r = s[(s["interval"] == "rej_t") & (s["p_a"] == 0.01) & (s["law"] == "normal") & (s["n_L"] >= 6) & (s["support"] >= 1000)]
    okc = r["coverage_mean"].between(0.88, 0.92)
    t = s[(s["design"] == "D0") & (s["rule"] == "c_crossfit_design") & (s["interval"] == XF)][
        ["G", "n_L", "R2", "lambda_star", "law", "width_mean"]]
    m = r.merge(t, on=["G", "n_L", "R2", "lambda_star", "law"], suffixes=("", "_tunedD0"))
    m = m[(m["n_L"] <= 8) & (m["R2"] >= 0.4)]
    m["width_ratio_to_tunedD0"] = m["width_mean"] / m["width_mean_tunedD0"]
    okw = m["width_ratio_to_tunedD0"] < 1
    add("E4b.1", "held" if okc.all() and okw.all() else ("partly held" if okc.mean() >= 0.5 or okw.mean() >= 0.5 else "refuted"),
        f"normal law, own balance, p_a 0.01, n_L >= 6, support >= 1000: rej_t coverage in 0.88-0.92 in {int(okc.sum())} of {len(r)} cells "
        f"(range {r['coverage_mean'].min():.3f} to {r['coverage_mean'].max():.3f}); narrower than the tuned D0 interval in {int(okw.sum())} of "
        f"{len(m)} cells with n_L <= 8 and R2 >= 0.4 (width ratio {m['width_ratio_to_tunedD0'].min():.3f} to {m['width_ratio_to_tunedD0'].max():.3f})",
        pd.concat([r.assign(part="coverage"), m.assign(part="width")]))
    # gene-level widths and variances, all draws
    g = genes[genes["n_sub"] > 200]
    gk = ["vtag", "arm", "estimand", "n_L", "gene"]
    d0c = g[(g["design"] == "D0") & (g["rule"] == "none") & (g["interval"] == LIN)][gk + ["width", "emp_var", "coverage"]]
    d0t = g[(g["design"] == "D0") & (g["rule"] == "c_crossfit_design") & (g["interval"] == XF)][gk + ["width"]]
    rj = g[(g["design"] == "D2") & (g["interval"] == "rej_t")][gk + ["balance", "p_a", "width", "coverage", "emp_var"]]
    w = rj.merge(d0c, on=gk, suffixes=("", "_D0cl")).merge(d0t.rename(columns={"width": "width_D0tuned"}), on=gk)
    w["wr_D0cl"] = w["width"] / w["width_D0cl"]
    w["wr_D0tuned"] = w["width"] / w["width_D0tuned"]
    w["var_ratio"] = w["emp_var"] / w["emp_var_D0cl"]
    wm = (w.groupby(["vtag", "arm", "estimand", "n_L", "balance", "p_a"])
          .agg(wr_D0cl=("wr_D0cl", "median"), wr_D0tuned=("wr_D0tuned", "median"), var_ratio=("var_ratio", "median"),
               coverage=("coverage", "median"), coverage_D0cl=("coverage_D0cl", "median"), n_genes=("gene", "nunique"))
          .reset_index())
    sup = diag[["vtag", "arm", "estimand", "n_L", "balance", "p_a", "support", "frac_genes_abs_bias_z_gt_3"]].drop_duplicates()
    wm = wm.merge(sup, on=["vtag", "arm", "estimand", "n_L", "balance", "p_a"], how="left")
    wm["coverage_minus_D0cl"] = wm["coverage"] - wm["coverage_D0cl"]
    wm.to_csv(f"{D}/e4b_rej_width_ratios.csv", index=False)
    for lab, z in (("support_ge_1000", wm[wm["support"] >= 1000]), ("support_lt_1000", wm[wm["support"] < 1000]),
                   ("support_ge_1000_nL_ge_6", wm[(wm["support"] >= 1000) & (wm["n_L"] >= 6)])):
        num(f"rej|{lab}|n_cells", len(z), "e4b_rej_width_ratios.csv")
        num(f"rej|{lab}|coverage_median", z["coverage"].median(), "e4b_rej_width_ratios.csv")
        num(f"rej|{lab}|coverage_min", z["coverage"].min(), "e4b_rej_width_ratios.csv")
        num(f"rej|{lab}|coverage_max", z["coverage"].max(), "e4b_rej_width_ratios.csv")
        num(f"rej|{lab}|n_within_0.03_of_D0cl", int((z["coverage_minus_D0cl"].abs() <= 0.03).sum()), "e4b_rej_width_ratios.csv")
        num(f"rej|{lab}|coverage_minus_D0cl_median", z["coverage_minus_D0cl"].median(), "e4b_rej_width_ratios.csv")
        num(f"rej|{lab}|coverage_minus_D0cl_min", z["coverage_minus_D0cl"].min(), "e4b_rej_width_ratios.csv")
    # E4b.2
    x = wm[(wm["n_L"] == 8) & (wm["estimand"] == "theta3") & (wm["balance"] == "own") & (wm["p_a"] == 0.01)]
    bands = [("CCRCC", ("uni_v2",), (0.72, 0.88)), ("ACS_STATES", ("package",), (0.45, 0.62)),
             ("LUNG_XENIUM", ENC, (0.50, 0.65))]
    c2 = []
    for vt, arms, (lo, hi) in bands:
        for _, rr in x[(x["vtag"] == vt) & x["arm"].isin(arms)].iterrows():
            c2.append(dict(part="band", vtag=vt, arm=rr["arm"], value=rr["wr_D0cl"], lo=lo, hi=hi, ok=lo <= rr["wr_D0cl"] <= hi))
    for _, rr in x[x["vtag"].isin(KC) & x["arm"].isin(ENC)].iterrows():
        c2.append(dict(part="narrower_than_tuned_D0", vtag=rr["vtag"], arm=rr["arm"], value=rr["wr_D0tuned"], lo=np.nan, hi=1.0,
                       ok=rr["wr_D0tuned"] < 1))
        c2.append(dict(part="coverage_within_0.03_of_D0_classical", vtag=rr["vtag"], arm=rr["arm"],
                       value=rr["coverage"] - rr["coverage_D0cl"], lo=-0.03, hi=0.03, ok=abs(rr["coverage"] - rr["coverage_D0cl"]) <= 0.03))
    c2 = pd.DataFrame(c2)
    txt = "; ".join(f"{p}: {int(c2[c2['part'] == p]['ok'].sum())} of {int((c2['part'] == p).sum())}" for p in c2["part"].unique())
    add("E4b.2", part(c2["ok"]), "theta3, n_L 8, own balance, p_a 0.01: " + txt + "; band values " +
        ", ".join(f"{rr.vtag} {rr.arm} {rr.value:.3f}" for rr in c2[c2["part"] == "band"].itertuples()), c2)
    # E4b.3
    k3 = b[(b["vtag"].isin(KC)) & (b["estimand"] == "theta2") & b["balance"].isin(["perm", "perm_cluster"])]
    n_out = k3.assign(out=~k3["within3"]).groupby("balance")["out"].sum()
    held3 = n_out.get("perm", 0) > n_out.get("perm_cluster", 0)
    add("E4b.3", "held" if held3 else "refuted",
        f"kidney cancer tasks, theta2, D2: outside 3 bootstrap se of 1 in {int(n_out.get('perm', 0))} of {int((k3['balance'] == 'perm').sum())} "
        f"perm cells and {int(n_out.get('perm_cluster', 0))} of {int((k3['balance'] == 'perm_cluster').sum())} perm_cluster cells", k3)
    # E4b.4
    vr = pd.read_csv(f"{E4}/e4_variance_ratios.csv")
    e44 = vr[(vr["vtag"] == "LUNG_XENIUM") & (vr["estimand"] == "theta3") & (vr["n_L"] == 8) & (vr["design"] == "D2")
             & (vr["balance"] == "own") & (vr["p_a"] == 0.01) & (vr["rule"] == "none") & (vr["interval"] == LIN) & vr["arm"].isin(ENC)]
    gl = g[(g["vtag"] == "LUNG_XENIUM") & (g["estimand"] == "theta3") & (g["n_L"] == 8) & (g["rule"] == "none") & (g["interval"] == LIN)]
    a_ = gl[(gl["design"] == "D2") & (gl["balance"] == "own") & (gl["p_a"] == 0.01)][["arm", "gene", "emp_var"]]
    b_ = gl[gl["design"] == "D0"][["arm", "gene", "emp_var"]]
    q = a_.merge(b_, on=["arm", "gene"], suffixes=("", "_0"))
    q["ratio"] = q["emp_var"] / q["emp_var_0"]
    q4 = q.groupby("arm")["ratio"].median().rename("E4b").reset_index().merge(
        e44[["arm", "ratio_median"]].rename(columns={"ratio_median": "E4"}), on="arm")
    q4["diff"] = q4["E4b"] - q4["E4"]
    add("E4b.4", part(q4["diff"].abs() <= 0.05),
        "lung, theta3, n_L 8, own balance, p_a 0.01, median over genes of the D2 over D0 classical variance ratio: " +
        ", ".join(f"{rr.arm} {rr.E4b:.3f} (E4 {rr.E4:.3f})" for rr in q4.itertuples()), q4)
    pd.DataFrame(scores).to_csv(f"{D}/e4b_prediction_scores.csv", index=False)
    pd.concat(cells, ignore_index=True, sort=False).to_csv(f"{D}/e4b_prediction_cells.csv", index=False)
    pd.DataFrame(NUM).to_csv(f"{D}/e4b_report_numbers.csv", index=False)
    print(pd.DataFrame(acc).to_string()); print(pd.DataFrame(scores).to_string())
    figure(s, wm, b)


def figure(s, wm, b):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 6.5,
                         "ytick.labelsize": 6.5, "legend.fontsize": 6.5, "axes.spines.top": False, "axes.spines.right": False})
    COL = {"CCRCC": "#1b6ca8", "CCRCC_merged": "#7fb3d5", "INDIANA_KIDNEY": "#2a9d8f", "LUNG_XENIUM": "#e76f51",
           "ACS_STATES": "#6d597a", "ACS_CA_PUMA": "#b56576"}
    NAME = {"CCRCC": "kidney cancer", "CCRCC_merged": "kidney cancer, merged", "INDIANA_KIDNEY": "Indiana kidney",
            "LUNG_XENIUM": "lung", "ACS_STATES": "census, states", "ACS_CA_PUMA": "census, CA areas"}
    fig, axs = plt.subplots(1, 3, figsize=(7.6, 2.7), gridspec_kw={"wspace": 0.45})
    ax = axs[0]
    r = s[(s["interval"] == "rej_t") & (s["law"] == "normal")]
    for pa, mk in ((0.1, "o"), (0.01, "s")):
        z = r[r["p_a"] == pa]
        ax.scatter(z["support"], z["coverage_mean"], s=8, marker=mk, color="#1b6ca8" if pa == 0.01 else "#9a9a9a",
                   alpha=0.6, lw=0, label=f"p_a = {pa}")
    ax.axhspan(0.88, 0.92, color="#1b6ca8", alpha=0.08, lw=0); ax.axhline(0.9, color="k", lw=0.6, ls=":")
    ax.axvline(1000, color="#9a9a9a", lw=0.6, ls="--")
    ax.set_xscale("log"); ax.set_xlabel("support, p_a x C(G, n_L)"); ax.set_ylabel("rej_t coverage (normal law)")
    ax.set_title("rej_t coverage in simulation", loc="left"); ax.legend(frameon=False, loc="lower right")
    ax = axs[1]
    x = wm[(wm["estimand"] == "theta3") & (wm["n_L"] == 8) & (wm["balance"] == "own") & (wm["p_a"] == 0.01)
           & wm["arm"].isin(ENC + ("package",))]
    order = ["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM", "ACS_STATES", "ACS_CA_PUMA"]
    for i, vt in enumerate(order):
        z = x[x["vtag"] == vt]
        ax.scatter(np.full(len(z), i - 0.12), z["wr_D0cl"], s=12, color=COL[vt], marker="o", lw=0)
        ax.scatter(np.full(len(z), i + 0.12), z["wr_D0cl"] / z["wr_D0tuned"], s=12, color=COL[vt], marker="x", lw=0.8)
    ax.axhline(1, color="k", lw=0.6, ls=":")
    ax.set_xticks(range(len(order))); ax.set_xticklabels([NAME[v] for v in order], rotation=40, ha="right")
    ax.set_ylabel("width over D0 classical width")
    ax.scatter([], [], s=12, color="#555555", marker="o", label="rej_t under D2"); ax.scatter([], [], s=12, color="#555555", marker="x", label="tuned, D0")
    ax.legend(frameon=False, loc="lower left"); ax.set_title("Width, theta3, n_L 8", loc="left")
    ax = axs[2]
    z = b[(b["design"] == "D2") & b["balance"].isin(["perm", "perm_cluster"])]
    for bal, c_ in (("perm", "#9a9a9a"), ("perm_cluster", "#1b6ca8")):
        q = z[z["balance"] == bal]
        q = q[q["support"] >= 1]
        ax.scatter(q["support"], q["z_from_1"].clip(-10, 10), s=7, color=c_, alpha=0.6, lw=0, label=bal)
    ax.axhspan(-3, 3, color="#1b6ca8", alpha=0.06, lw=0); ax.axvline(1000, color="#9a9a9a", lw=0.6, ls="--")
    ax.set_xscale("log"); ax.set_xlabel("support (cells with support >= 1)"); ax.set_ylabel("(ratio - 1) / bootstrap se, clipped at 10")
    ax.set_title("Null controls, D2 against D0", loc="left"); ax.legend(frameon=False, loc="lower right")
    ax.set_ylim(-10.5, 10.5)
    for a_, l in zip(axs, "abc"):
        a_.text(-0.25, 1.07, l, transform=a_.transAxes, fontweight="bold", fontsize=10)
    fig.savefig(f"{D}/fig_e4b_summary.png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    main()
