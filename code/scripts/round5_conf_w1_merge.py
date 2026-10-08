#!/usr/bin/env python
"""Round 5, prediction-set track, stage W1: merge the per-K fragments, acceptance, report numbers.

docs/round5_conf_plan.md section 2, W1 (Acceptance, Predictions, Outputs). Runs on Longleaf after
the ten frag_K<KK> directories exist. It reads them and the committed round-4 c1_grid.csv, and
writes w1_grid.csv, w1_within_full_shape.csv, w1_narrowest_valid.csv, w1_acceptance.csv,
w1_predictions.csv, w1_report_numbers.csv, w1_merge_checks.csv and fig_w1_map.png into OUT.

Acceptance, with each method's own expected coverage.
  1. Every (cell, method, o) of c1_grid.csv at K in {9, 10, 12, 20, 25, 50} that the W1 grid also
     contains is reproduced: coverage within 1e-4, price within 1e-6 relative, frac_infinite
     identical (round 4's rows were computed on a laptop).
  2. within_plain is infinite in every replicate for o < 9 at alpha 0.1 and o < 4 at alpha 0.2,
     and finite in every replicate otherwise. within is infinite for o < 17 at alpha 0.1, and, as
     added in plan section 4 item 2, for o < 7 at alpha 0.2.
  3. Where within_plain is finite, its coverage is within 3 MC standard errors of
     ceil((o+1)(1-alpha))/(o+1); the same for within with n = o - floor(o/2) in place of o.
  4. within_full is finite in every replicate from o = 9 at alpha 0.1 and from o = 4 at alpha 0.2
     and infinite below, and its exact-set coverage is within 3 MC standard errors of the same
     expected value as within_plain's. The hull coverage is reported beside it.
  A 3-standard-error check fails by chance in about 0.27% of cells when the method is exact, so
  checks 3 and 4 report the count of failures beside the count expected by chance. The literal
  reading (zero failures) is reported too.
"""
import glob
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round5_conf_io as IO5  # noqa: E402

KEY = ["cell_id", "alpha", "method", "o"]
GHCP = ("ghcp", "ghcp_noad", "ghcp_r05", "ghcp_r05code")


def expected(n, a):
    return math.ceil((n + 1) * (1 - a) - 1e-9) / (n + 1)


def load(frag_root, pattern):
    fs = sorted(glob.glob(os.path.join(frag_root, "frag_K*", pattern)))
    return pd.concat([pd.read_csv(f).assign(_src=os.path.basename(os.path.dirname(f))) for f in fs],
                     ignore_index=True), fs


def main(frag_root, out):
    os.makedirs(out, exist_ok=True)
    IO5.stamp(out, track="conformal-W1", note="W1 merge, acceptance and report numbers")
    G, gf = load(frag_root, "w1_grid__K??.csv")
    WF, _ = load(frag_root, "w1_within_full_shape__K??.csv")
    NV, _ = load(frag_root, "w1_narrowest_valid__K??.csv")
    checks = []
    dup = int(G.duplicated(KEY).sum())
    checks.append(dict(check="duplicated_keys_w1_grid", value=dup, passed=dup == 0))
    ncell = G.groupby("K").cell_id.nunique()
    checks.append(dict(check="cells_per_K", value=ncell.to_dict(), passed=bool((ncell == 74).all())))
    G = G.drop(columns="_src")
    G.to_csv(os.path.join(out, "w1_grid.csv"), index=False)
    WF.drop(columns="_src").to_csv(os.path.join(out, "w1_within_full_shape.csv"), index=False)
    NV.drop(columns="_src").to_csv(os.path.join(out, "w1_narrowest_valid.csv"), index=False)
    pd.DataFrame(checks).to_csv(os.path.join(out, "w1_merge_checks.csv"), index=False)

    acc = []
    # 1. reproduction of round 4
    R4 = pd.read_csv(os.path.join(IO5.CLONE, "results", "round4", "conformal", "C1_testbed", "c1_grid.csv"))
    R4 = R4[R4.K.isin([9, 10, 12, 20, 25, 50])]
    m = R4.merge(G, on=KEY, suffixes=("_r4", "_r5"))
    inW1 = R4.cell_id.isin(G.cell_id) & R4.method.isin(G.method) & R4.o.isin(G.o)
    miss = int(inW1.sum() - len(m))
    fin = np.isfinite(m.price_r4) & np.isfinite(m.price_r5)
    dcov = float((m.coverage_r5 - m.coverage_r4).abs().max())
    dpr = float(((m.price_r5 - m.price_r4).abs() / m.price_r4.abs())[fin].max())
    inf_same = bool((np.isinf(m.price_r4) == np.isinf(m.price_r5)).all())
    dfi = float((m.frac_infinite_r5 - m.frac_infinite_r4).abs().max())
    acc += [dict(check="1_rows_compared", value=len(m), tol=np.nan, passed=miss == 0, note=f"{miss} expected rows missing"),
            dict(check="1_max_abs_diff_coverage", value=dcov, tol=1e-4, passed=dcov <= 1e-4),
            dict(check="1_max_rel_diff_price", value=dpr, tol=1e-6, passed=bool(dpr <= 1e-6 and inf_same)),
            dict(check="1_max_abs_diff_frac_infinite", value=dfi, tol=0.0, passed=dfi == 0.0)]
    # 2. finiteness patterns
    def fin_check(meth, a, thresh, name):
        d = G[(G.method == meth) & (G.alpha == a) & (G.o > 0)]
        bad = d[((d.o < thresh) & (d.frac_infinite != 1.0)) | ((d.o >= thresh) & (d.frac_infinite != 0.0))]
        acc.append(dict(check=name, value=len(bad), tol=0, passed=len(bad) == 0, note=f"{len(d)} rows"))
    fin_check("within_plain", 0.1, 9, "2_within_plain_finite_from_o9_a0.1")
    fin_check("within_plain", 0.2, 4, "2_within_plain_finite_from_o4_a0.2")
    fin_check("within", 0.1, 17, "2_within_finite_from_o17_a0.1")
    fin_check("within", 0.2, 7, "2_within_finite_from_o7_a0.2")
    fin_check("within_full", 0.1, 9, "4_within_full_finite_from_o9_a0.1")
    fin_check("within_full", 0.2, 4, "4_within_full_finite_from_o4_a0.2")
    # 3 and 4. coverage against each method's own expected value
    rows = []
    for meth in ("within_plain", "within"):
        d = G[(G.method == meth) & (G.frac_infinite == 0.0)].copy()
        n = d.o if meth == "within_plain" else d.o - d.o // 2
        d["expected"] = [expected(int(k), a) for k, a in zip(n, d.alpha)]
        d["z"] = (d.coverage - d.expected) / d.coverage_mcse
        rows.append(d.assign(check=f"3_{meth}"))
    W = WF.copy()
    W = W[W.exact_coverage_sd > 0]
    W["coverage"] = W.exact_coverage
    W["coverage_mcse"] = W.exact_coverage_sd / np.sqrt(W.n)
    W["method"] = "within_full"
    W["expected"] = [expected(int(o), a) for o, a in zip(W.o, W.alpha)]
    W["z"] = (W.coverage - W.expected) / W.coverage_mcse
    rows.append(W.assign(check="4_within_full_exact"))
    Z = pd.concat(rows, ignore_index=True)
    Z[["check", "cell_id", "alpha", "o", "coverage", "coverage_mcse", "expected", "z"]].to_csv(
        os.path.join(out, "w1_coverage_z.csv"), index=False)
    for ch, d in Z.groupby("check"):
        nf = int((d.z.abs() > 3).sum())
        acc.append(dict(check=f"{ch}_cov_within_3se", value=nf, tol=0, passed=nf == 0,
                        note=f"{len(d)} cells; {0.0027 * len(d):.1f} expected by chance; max |z| {d.z.abs().max():.2f}"))
    hull = G[(G.method == "within_full") & (G.frac_infinite == 0.0)]
    acc.append(dict(check="4_within_full_frac_not_interval_max", value=float(WF.frac_not_interval.max()),
                    tol=np.nan, passed=np.nan, note="share of replicates whose set is not one interval"))
    acc.append(dict(check="4_within_full_hull_minus_exact_cov_max",
                    value=float((hull.merge(WF, on=["cell_id", "alpha", "o"]).eval("coverage - exact_coverage")).max()),
                    tol=np.nan, passed=np.nan))
    A = pd.DataFrame(acc)
    A.to_csv(os.path.join(out, "w1_acceptance.csv"), index=False)

    # predictions, read at normal tails, tau 0, N 500, alpha 0.1 unless named
    base = NV[(NV.gen == "normal") & (NV.tau == 0.0) & (NV.N.astype(str) == "500") & (NV.alpha == 0.1)]
    GG = G[(G.gen == "normal") & (G.tau == 0.0) & (G.N.astype(str) == "500") & (G.alpha == 0.1)]
    def hw(K, share, meth, o):
        d = GG[(GG.K == K) & (GG.share == share) & (GG.method == meth) & (GG.o == (0 if meth == "hcp" else o))]
        return float(d.halfwidth_mean.iloc[0]) if len(d) and d.frac_infinite.iloc[0] == 0 else math.inf
    P = []
    for _, r in base.iterrows():
        P.append(dict(K=r.K, share=r.share, o=r.o, narrowest=r.narrowest, runner_up=r.get("runner_up"),
                      margin_rel=r.get("margin_rel"), margin_gt_2se=r.get("margin_gt_2se"),
                      ghcp_over_hcp=hw(r.K, r.share, "ghcp", r.o) / hw(r.K, r.share, "hcp", 0),
                      within_plain_over_ghcp=hw(r.K, r.share, "within_plain", r.o) / hw(r.K, r.share, "ghcp", r.o),
                      within_full_over_ghcp=hw(r.K, r.share, "within_full", r.o) / hw(r.K, r.share, "ghcp", r.o),
                      within_full_over_within=hw(r.K, r.share, "within_full", r.o) / hw(r.K, r.share, "within", r.o)))
    Pd = pd.DataFrame(P)
    Pd.to_csv(os.path.join(out, "w1_predictions.csv"), index=False)
    rn = []
    def add(name, val, src="w1_predictions.csv"):
        rn.append(dict(name=name, value=val, source=src))
    k10 = Pd[Pd.K <= 10]
    add("W1.1_n_cells_ghcp_narrowest_K_le_10", int(k10.narrowest.isin(GHCP).sum()))
    d = Pd[(Pd.K >= 20) & (Pd.share >= 0.3) & Pd.o.isin([3, 5])]
    add("W1.2_n_cells", len(d)); add("W1.2_n_ghcp_narrowest", int(d.narrowest.isin(GHCP).sum()))
    add("W1.2_ghcp_over_hcp_min", float(d.ghcp_over_hcp.min())); add("W1.2_ghcp_over_hcp_max", float(d.ghcp_over_hcp.max()))
    d = Pd[(Pd.share == 0.3) & Pd.o.isin([9, 10, 12])]
    add("W1.3_plain_lt_ghcp_K_le_15_n", int((d[d.K <= 15].within_plain_over_ghcp < 1).sum()))
    add("W1.3_K_le_15_cells", int((d.K <= 15).sum()))
    add("W1.3_plain_gt_ghcp_K_ge_25_n", int((d[d.K >= 25].within_plain_over_ghcp > 1).sum()))
    add("W1.3_K_ge_25_cells", int((d.K >= 25).sum()))
    add("W1.3_full_lt_ghcp_all_K_n", int((d.within_full_over_ghcp < 1).sum())); add("W1.3_cells", len(d))
    d = Pd[Pd.o.isin([20, 25, 35, 50])]
    add("W1.4_full_over_within_o20_50_min", float(d.within_full_over_within.min()))
    add("W1.4_full_over_within_o20_50_max", float(d.within_full_over_within.max()))
    d17 = Pd[Pd.o == 17]
    add("W1.4_full_over_within_o17_min", float(d17.within_full_over_within.min()))
    add("W1.4_full_over_within_o17_max", float(d17.within_full_over_within.max()))
    d = Pd[(Pd.o >= 9) & (Pd.share >= 0.3)]
    add("W1.4_cells_o_ge_9_share_ge_0.3", len(d)); add("W1.4_n_full_narrowest", int((d.narrowest == "within_full").sum()))
    d = Pd[(Pd.K == 20) & (Pd.share == 0.9)]
    add("W1.5_share0.9_reached", bool(len(d) > 0))
    if len(d):
        add("W1.5_ghcp_over_hcp_o5", float(d[d.o == 5].ghcp_over_hcp.iloc[0]))
        add("W1.5_full_over_ghcp_o_ge_9_max", float(d[d.o >= 9].within_full_over_ghcp.max()))
    rs = G[(G.share == 0.9)].groupby("gen").realised_share.agg(["min", "max"]).reset_index()
    for _, r in rs.iterrows():
        add(f"realised_share_0.9_{r.gen}_min", float(r["min"]), "w1_grid.csv")
        add(f"realised_share_0.9_{r.gen}_max", float(r["max"]), "w1_grid.csv")
    pd.DataFrame(rn).to_csv(os.path.join(out, "w1_report_numbers.csv"), index=False)
    figure(NV, out)
    IO5.write_provenance(out, "W1_merge", __file__, dict(stage="W1 merge", frags=[os.path.dirname(f) for f in gf]),
                         extra=dict(acceptance_all_literal=bool(A.passed.dropna().astype(bool).all())))
    print(A.to_string(), flush=True)


def figure(NV, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7,
                         "xtick.labelsize": 6, "ytick.labelsize": 6, "axes.spines.top": False,
                         "axes.spines.right": False})
    names = {"hcp": "HCP", "ghcp": "GHCP", "ghcp_noad": "GHCP, no adaptation", "within_plain": "plain split in cluster",
             "within": "half-split in cluster (Std-CP)", "within_full": "full conformal in cluster", "none": "none finite"}
    abbr = {"hcp": "H", "ghcp": "G", "ghcp_noad": "Gn", "within_plain": "P", "within": "S", "within_full": "F", "none": "-"}
    col = {"hcp": "#999999", "ghcp": "#E69F00", "ghcp_noad": "#F0E442", "within_plain": "#56B4E9",
           "within": "#009E73", "within_full": "#0072B2", "none": "#FFFFFF"}
    shares = (0.3, 0.9)
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.0), sharey=True, gridspec_kw=dict(wspace=0.06))
    for ax, s in zip(axs, shares):
        d = NV[(NV.gen == "normal") & (NV.tau == 0.0) & (NV.N.astype(str) == "500") & (NV.alpha == 0.1) & (NV.share == s)]
        Ks = sorted(d.K.unique()); os_ = sorted(d.o.unique())
        for i, K in enumerate(Ks):
            for j, o in enumerate(os_):
                r = d[(d.K == K) & (d.o == o)]
                m = r.narrowest.iloc[0] if len(r) and isinstance(r.narrowest.iloc[0], str) else "none"
                weak = bool(len(r)) and str(r["margin_gt_2se"].iloc[0]) == "False"
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color=col[m], alpha=0.45 if weak else 1.0, lw=0))
                ax.text(j, i, abbr[m], ha="center", va="center", fontsize=6,
                        color="white" if m in ("within_full", "within") and not weak else "black")
        ax.set_xlim(-0.5, len(os_) - 0.5); ax.set_ylim(-0.5, len(Ks) - 0.5)
        ax.set_xticks(range(len(os_))); ax.set_xticklabels(os_)
        ax.set_yticks(range(len(Ks))); ax.set_yticklabels(Ks)
        ax.set_xlabel("labelled units in the test cluster, o")
        ax.set_title(f"between-cluster share of score variance {s}", loc="left")
    axs[0].set_ylabel("calibration clusters, K")
    sl = NV[(NV.gen == "normal") & (NV.tau == 0.0) & (NV.N.astype(str) == "500") & (NV.alpha == 0.1) & NV.share.isin(shares)]
    used = [m for m in ("hcp", "ghcp", "ghcp_noad", "within_plain", "within", "within_full") if (sl.narrowest == m).any()]
    fig.legend(handles=[Patch(color=col[m], label=f"{abbr[m]}  {names[m]}") for m in used], loc="lower center",
               ncol=min(len(used), 4), frameon=False, bbox_to_anchor=(0.5, 0.0))
    anypale = (sl.margin_gt_2se.astype(str) == "False").any()
    fig.suptitle("Narrowest method with a finite-sample guarantee, by K and o\n"
                 "normal tails, no scale variation, 500 units per cluster, alpha 0.1, 5,000 replicates"
                 + ("; pale: margin within 2 MC s.e." if anypale else ""), x=0.08, ha="left", fontsize=7)
    fig.subplots_adjust(bottom=0.24, top=0.84, left=0.08, right=0.99)
    fig.savefig(os.path.join(out, "fig_w1_map.png"), dpi=300)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
