"""Round 5 PPI, stage E2: merge the unit fragments, decomposition (part 3), acceptance, scoring.

Run on Longleaf from results/round5/ppi/E2_regimeB/. Reads every frag_<unit>/**/ output (directories
whose name contains 'smoke' are ignored), checks each _provenance.json against the frame id assigned
to its unit (--frames vtag=<id>,...,sim=<id>), and writes, summaries first:
  e2_stamp_check.csv, e2_acceptance.csv, e2_prediction_scores.csv, e2_prediction_cells.csv,
  e2_report_numbers.csv, e2_decomposition.csv, e2_level_share.csv, e2_regimeB_grid.csv, e2_sim.csv,
  e2_shares_genes.csv.gz, e2_decomposition_genes.csv.gz, fig_e2_coverage_by_m.png, fig_e2_decomposition.png.
With --e1-dir it also tabulates the E1 prediction cells by the grid axes into e1_tabulations.csv there.

Decomposition. For each task, estimand, population, target, rule and m, the width ratio of every arm
against the round-4 classical estimator (rule none of the same arm's run; the classical estimator uses
only z and the paired draws, so it is the same in every arm, which is checked), and per gene the width
of each real predictor over the constant's and the donor-constant's, as medians over genes. Beside them
sqrt(1 - R2_within) per arm, median over genes, on the z scale from the full data (e2_r2 files).
"""
import argparse
import glob
import json
import os

import numpy as np
import pandas as pd

TASKS = ("CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM", "ACS_STATES", "ACS_CA_PUMA")
REAL = {"CCRCC": ("hoptimus0", "uni_v2", "resnet50"), "CCRCC_merged": ("hoptimus0", "uni_v2", "resnet50"),
        "INDIANA_KIDNEY": ("hoptimus0", "uni_v2", "resnet50"), "LUNG_XENIUM": ("hoptimus0", "uni_v2", "resnet50"),
        "ACS_STATES": ("package",), "ACS_CA_PUMA": ("package",)}
CONTROLS = ("permuted", "constant", "donor_constant")


def files(pattern):
    return [f for f in sorted(glob.glob(pattern, recursive=True)) if "smoke" not in f]


def cat(pattern):
    fs = files(pattern)
    parts = []
    for f in fs:
        d = pd.read_csv(f)
        d["source_file"] = f
        parts.append(d)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def dedupe(df, keys, label):
    dup = df.duplicated(keys, keep=False)
    if dup.any():
        num = [c for c in df.select_dtypes("number").columns]
        nun = df[dup].groupby(keys)[num].nunique().max(axis=1).max()
        assert nun == 1, f"{label}: differing duplicate rows"
        print(label, "identical duplicates dropped:", int(dup.sum()))
        df = df.drop_duplicates(keys)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--round4-sim", required=True)
    ap.add_argument("--e1-dir", default="")
    a = ap.parse_args()
    frames = dict(x.split("=") for x in a.frames.split(","))
    st = []
    for unit, fid in frames.items():
        for p in sorted(glob.glob(f"frag_{unit}/**/_provenance.json", recursive=True)):
            s = json.load(open(p))
            st.append(dict(unit=unit, path=p, frame_id=s.get("frame_id"), assigned=fid, match=s.get("frame_id") == fid))
    pd.DataFrame(st).to_csv("e2_stamp_check.csv", index=False)

    grid = cat("frag_*/**/e2_regimeB_grid__*.csv")
    gkeys = ["vtag", "arm", "m", "estimand", "population", "target", "lambda_rule", "interval"]
    grid = dedupe(grid, gkeys, "grid")
    genes = cat("frag_*/**/e2_regimeB_genes__*.csv.gz")
    genes = dedupe(genes, gkeys + ["gene"], "genes")
    shares = cat("frag_*/**/e2_shares__*.csv.gz")
    shares = dedupe(shares, ["vtag", "arm", "m", "estimand", "population", "gene"], "shares")
    r2 = cat("frag_*/**/e2_r2__*.csv")
    r2 = dedupe(r2, ["vtag", "arm", "estimand", "population", "gene"], "r2")
    accf = cat("frag_*/**/e2_acceptance__*.csv")
    sim = cat("frag_sim/**/e2_sim__*.csv")
    sim = dedupe(sim, ["mu", "arm", "m", "estimand", "population", "target", "lambda_rule"], "sim")
    grid.to_csv("e2_regimeB_grid.csv", index=False)
    sim.to_csv("e2_sim.csv", index=False)
    shares.to_csv("e2_shares_genes.csv.gz", index=False)
    rn, scores, cells, acc = [], [], [], []

    def num(n, v):
        rn.append(dict(name=n, value=v))

    # ---- acceptance 1 and 2 (from the units' acceptance files), 3 (simulation)
    a1 = accf[accf.check == "m_all_equals_theta_full"]
    for vt, d in a1.groupby("vtag"):
        acc.append(dict(check=f"1_m_all_equals_full_data_abs_below_1e-10|{vt}", n=len(d), worst_abs=float(d.value.max()),
                        design_var_max=float(d.design_var_max.max()), passes=bool(d.value.max() < 1e-10)))
    a2 = accf[accf.check.str.startswith("reproduce_round4_B2400")]
    acc.append(dict(check="2_reproduce_E0_regimeB_anchor_CCRCC_hoptimus0", n=len(a2), worst_abs=float(a2.value.max()),
                    n_matched=int(a2.n_matched.min()), n_ref=int(a2.n_ref.max()), passes=bool(a2.value.max() <= 1e-15)))
    r4 = pd.read_csv(a.round4_sim)
    r4 = r4[(r4.rho == 0.3) & r4.m.isin([5, 20]) & r4.lambda_rule.isin(["none", "c_crossfit"])]
    s0 = sim[(sim.mu == 0) & sim.arm.isin(["r0.5", "r0.8", "uninf"]) & sim.m.isin([5, 20])].copy()
    s0["r"] = s0.arm.map({"r0.5": 0.5, "r0.8": 0.8, "uninf": 0.0})
    j = s0.merge(r4, on=["r", "m", "estimand", "population", "target", "lambda_rule"], suffixes=("", "_r4"))
    jj = j[np.isfinite(j.coverage) | np.isfinite(j.coverage_r4)]
    d = (jj.coverage - jj.coverage_r4).abs()
    acc.append(dict(check="3a_sim_mu0_reproduces_round4_coverage_m5_m20", n=len(jj), worst_abs=float(d.max()),
                    n_exact=int((d == 0).sum()), passes=bool(d.max() <= 0.01)))
    c0 = sim[(sim.mu == 0) & (sim.arm == "const") & (sim.lambda_rule == "c_crossfit") & (sim.estimand == "theta3")]
    dd = (c0.design_err_var_ratio_to_classical - 1).abs()
    acc.append(dict(check="3b_sim_mu0_constant_variance_ratio_1_within_0.02", n=len(c0), worst_abs=float(dd.max()),
                    passes=bool(dd.max() <= 0.02)))
    # classical identical across arms (pairing check)
    cl = genes[(genes.lambda_rule == "none")]
    spread = cl.groupby(["vtag", "m", "estimand", "population", "target", "gene"]).width.agg(lambda x: x.max() - x.min())
    acc.append(dict(check="pairing_classical_width_identical_across_arms", n=len(spread), worst_abs=float(spread.max()),
                    passes=bool(spread.max() <= 1e-9)))
    pd.DataFrame(acc).to_csv("e2_acceptance.csv", index=False)

    # ---- level share and R2 within
    ls = (shares.groupby(["vtag", "arm", "m", "estimand", "population"])
          .agg(share_unclipped_median=("share_unclipped", "median"), share_clipped_median=("share_clipped", "median"),
               share_clipped_p10=("share_clipped", lambda x: x.quantile(0.1)),
               share_clipped_p90=("share_clipped", lambda x: x.quantile(0.9)),
               coef_unclipped_median=("coef_unclipped", "median"), n_genes=("gene", "nunique")).reset_index())
    ls.to_csv("e2_level_share.csv", index=False)
    r2m = (r2.assign(sqrt_1m_r2w=np.sqrt(np.clip(1 - r2.R2_within, 0, None)))
           .groupby(["vtag", "arm", "estimand", "population"]).agg(sqrt_1m_R2_within_median=("sqrt_1m_r2w", "median"),
                                                                    R2_within_median=("R2_within", "median")).reset_index())

    # ---- decomposition
    g = genes[genes.lambda_rule == "c_crossfit"].copy()
    g["w_ratio_classical"] = g.width / g.width_classical
    key = ["vtag", "m", "estimand", "population", "target", "gene"]
    piv = g.pivot_table(index=key, columns="arm", values="width")
    dec_rows, dg = [], []
    for vt in TASKS:
        for arm in REAL[vt]:
            for ctrl in ("constant", "donor_constant"):
                if arm not in piv.columns or ctrl not in piv.columns:
                    continue
                rr = (piv[arm] / piv[ctrl]).dropna()
                rr = rr[rr.index.get_level_values("vtag") == vt]
                dg.append(rr.rename("ratio").reset_index().assign(arm=arm, over=ctrl))
    dg = pd.concat(dg, ignore_index=True)
    dg.to_csv("e2_decomposition_genes.csv.gz", index=False)
    over = dg.groupby(["vtag", "arm", "over", "m", "estimand", "population", "target"]).ratio.median().unstack("over")
    over.columns = [f"width_over_{c}_median" for c in over.columns]
    wr = (grid[grid.lambda_rule == "c_crossfit"][["vtag", "arm", "m", "estimand", "population", "target",
                                                  "width_ratio_median", "coverage_median"]])
    dec = wr.merge(over.reset_index(), on=["vtag", "arm", "m", "estimand", "population", "target"], how="left")
    dec = dec.merge(r2m, on=["vtag", "arm", "estimand", "population"], how="left")
    dec.to_csv("e2_decomposition.csv", index=False)

    # ---- scoring
    def score(pred, df, qty, lo=None, hi=None, need="all", frac=None, keys=None):
        ok = pd.Series(True, index=df.index)
        if lo is not None:
            ok &= df[qty] >= lo
        if hi is not None:
            ok &= df[qty] <= hi
        for i, row in df.iterrows():
            cells.append(dict(prediction=pred, **{k: row[k] for k in (keys or []) if k in row}, quantity=qty,
                              value=row[qty], in_band=bool(ok[i])))
        n, k = len(df), int(ok.sum())
        held = (k == n) if need == "all" else (k >= frac * n)
        scores.append(dict(prediction=pred, n_cells=n, n_in_band=k, band=f"[{lo}, {hi}]",
                           qty_min=float(df[qty].min()) if n else np.nan, qty_median=float(df[qty].median()) if n else np.nan,
                           qty_max=float(df[qty].max()) if n else np.nan, held=bool(held) if n else None))
    K = ["vtag", "arm", "m", "estimand", "population", "target", "lambda_rule"]
    dsg = grid[(grid.target == "design") & (grid.population == "donor")]
    score("E2.1a|design donor coverage in [0.87,0.92], m>=5, all tasks arms estimands rules",
          dsg[dsg.m >= 5], "coverage_median", 0.87, 0.92, keys=K)
    score("E2.1b|design donor coverage in [0.78,0.90], m in {2,3}", dsg[dsg.m.isin([2, 3])], "coverage_median", 0.78, 0.90, keys=K)
    d2 = dec[(dec.target == "design") & (dec.population == "donor")]
    pv = d2.pivot_table(index=["vtag", "m", "estimand"], columns="arm", values="width_ratio_median").reset_index()
    tis = pv[~pv.vtag.str.startswith("ACS")]
    acs3 = pv[pv.vtag.str.startswith("ACS") & (pv.estimand == "theta3")]
    for nm, df in (("tissue theta3+theta2", tis), ("ACS theta3", acs3)):
        df = df.assign(constant_minus_permuted=df.constant - df.permuted)
        score(f"E2.2a|{nm}|constant width ratio <= permuted", df, "constant_minus_permuted", None, 0.0,
              keys=["vtag", "m", "estimand"])
    score("E2.2b|tissue|permuted minus constant <= 0.06", tis.assign(gap=tis.permuted - tis.constant), "gap", None, 0.06,
          keys=["vtag", "m", "estimand"])
    am = pv[pv.vtag.str.startswith("ACS") & (pv.estimand == "theta2")]
    score("E2.2c|ACS mean|permuted width ratio 1.00 within 0.01", am.assign(dev=(am.permuted - 1).abs()), "dev", None, 0.01,
          keys=["vtag", "m", "estimand"])
    oc = d2[d2.arm.isin(["hoptimus0", "uni_v2", "resnet50", "package"])]
    bands = [("kidney theta3", oc.vtag.isin(["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY"]) & (oc.estimand == "theta3"), 0.93, 1.00),
             ("kidney theta2", oc.vtag.isin(["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY"]) & (oc.estimand == "theta2"), 0.97, None),
             ("lung theta3", (oc.vtag == "LUNG_XENIUM") & (oc.estimand == "theta3"), 0.60, 0.85),
             ("ACS theta3", oc.vtag.str.startswith("ACS") & (oc.estimand == "theta3"), 0.40, 0.80)]
    for nm, msk, lo, hi in bands:
        score(f"E2.3|{nm}|real over constant width", oc[msk], "width_over_constant_median", lo, hi,
              keys=["vtag", "arm", "m", "estimand"])
    sc = sim[(sim.arm == "const") & (sim.lambda_rule == "c_crossfit") & (sim.target == "design_on_realised") & (sim.m >= 20)]
    sc = sc.assign(one_minus_L=1 - sc.share_clipped_mean,
                   abs_dev=(sc.design_err_var_ratio_to_classical - (1 - sc.share_clipped_mean)).abs())
    score("E2.4|sim constant variance ratio equals 1-L within 0.03, m>=20", sc, "abs_dev", None, 0.03,
          keys=["mu", "m", "estimand", "population"])
    fl = oc[oc.m >= 5].groupby(["vtag", "arm", "estimand"]).width_over_constant_median.agg(lambda x: x.max() - x.min())
    score("E2.5|real over constant flat in m within 0.03, m>=5", fl.rename("range_over_m").reset_index(), "range_over_m",
          None, 0.03, keys=["vtag", "arm", "estimand"])
    pd.DataFrame(scores).to_csv("e2_prediction_scores.csv", index=False)
    pd.DataFrame(cells).to_csv("e2_prediction_cells.csv", index=False)

    # ---- report numbers
    for _, r in d2[d2.m.isin([2, 5, 20, 100])].iterrows():
        for c in ("width_ratio_median", "coverage_median", "width_over_constant_median", "width_over_donor_constant_median",
                  "sqrt_1m_R2_within_median"):
            if c in r and pd.notna(r[c]):
                num(f"dec|{r.vtag}|{r.arm}|{r.estimand}|m{r.m}|{c}", r[c])
    for _, r in ls[(ls.population == "donor") & ls.arm.isin(["constant"])].iterrows():
        num(f"level_share|{r.vtag}|{r.estimand}|m{r.m}|clipped_median", r.share_clipped_median)
        num(f"level_share|{r.vtag}|{r.estimand}|m{r.m}|unclipped_median", r.share_unclipped_median)
    for _, r in sc.iterrows():
        num(f"sim|const|mu{r.mu}|m{r.m}|{r.estimand}|{r.population}|var_ratio", r.design_err_var_ratio_to_classical)
        num(f"sim|const|mu{r.mu}|m{r.m}|{r.estimand}|{r.population}|one_minus_L", r.one_minus_L)
    for (vt, est), d in dsg.groupby(["vtag", "estimand"]):
        for mm, lab in ((d.m >= 5, "m>=5"), (d.m.isin([2, 3]), "m2-3")):
            num(f"coverage_range|{vt}|{est}|design|donor|{lab}|min", float(d[mm].coverage_median.min()))
            num(f"coverage_range|{vt}|{est}|design|donor|{lab}|max", float(d[mm].coverage_median.max()))
    pd.DataFrame(rn).to_csv("e2_report_numbers.csv", index=False)

    # ---- figures
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 7,
                         "ytick.labelsize": 7, "legend.fontsize": 7, "axes.spines.top": False, "axes.spines.right": False})
    col = {"hoptimus0": "#1b6ca8", "uni_v2": "#3fa34d", "resnet50": "#7a3d9a", "package": "#1b6ca8",
           "permuted": "#999999", "constant": "#d08c00", "donor_constant": "#8c5a00"}
    fig, axes = plt.subplots(2, 6, figsize=(10.5, 3.8), sharex=True, sharey="row", gridspec_kw=dict(wspace=0.08, hspace=0.25))
    for j, vt in enumerate(TASKS):
        for i, est in enumerate(("theta3", "theta2")):
            ax = axes[i, j]
            d = dsg[(dsg.vtag == vt) & (dsg.estimand == est) & (dsg.lambda_rule == "c_crossfit")]
            for arm, dd in d.groupby("arm"):
                dd = dd.sort_values("m")
                ax.plot(dd.m, dd.coverage_median, marker="o", ms=2.5, lw=1, color=col.get(arm, "k"), label=arm)
            dn = dsg[(dsg.vtag == vt) & (dsg.estimand == est) & (dsg.lambda_rule == "none") & (dsg.arm == REAL[vt][0])].sort_values("m")
            ax.plot(dn.m, dn.coverage_median, ls="--", lw=1, color="k", label="classical")
            ax.axhline(0.90, color="0.6", lw=0.6, ls=":")
            ax.set_xscale("log"); ax.set_xticks([2, 5, 20, 100]); ax.set_xticklabels(["2", "5", "20", "100"])
            if i == 0:
                ax.set_title(vt.replace("_", " "), loc="left")
            if j == 0:
                ax.set_ylabel(f"{'slope' if est == 'theta3' else 'group difference or mean'}\ncoverage (median over genes)")
            if i == 1:
                ax.set_xlabel("labelled units per cluster m")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, loc="upper center", ncol=7, bbox_to_anchor=(0.5, 1.02))
    fig.savefig("fig_e2_coverage_by_m.png", dpi=300, bbox_inches="tight")
    fig, axes = plt.subplots(1, 6, figsize=(10.5, 2.4), sharey=True, gridspec_kw=dict(wspace=0.08))
    for j, vt in enumerate(TASKS):
        ax = axes[j]
        d = d2[(d2.vtag == vt) & (d2.estimand == "theta3")]
        for arm, dd in d.groupby("arm"):
            dd = dd.sort_values("m")
            ax.plot(dd.m, dd.width_ratio_median, marker="o", ms=2.5, lw=1.4 if arm in REAL[vt] else 1, color=col.get(arm, "k"),
                    ls="-" if arm in REAL[vt] else "--", label=arm)
        ax.axhline(1.0, color="0.6", lw=0.6, ls=":")
        ax.set_xscale("log"); ax.set_xticks([2, 5, 20, 100]); ax.set_xticklabels(["2", "5", "20", "100"])
        ax.set_title(vt.replace("_", " "), loc="left"); ax.set_xlabel("m")
    axes[0].set_ylabel("slope: width over the\nround-4 classical width")
    h, l = [], []
    for ax in axes:
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            if ll not in l:
                h.append(hh); l.append(ll)
    fig.legend(h, l, frameon=False, loc="upper center", ncol=7, bbox_to_anchor=(0.5, 1.08))
    fig.savefig("fig_e2_decomposition.png", dpi=300, bbox_inches="tight")

    if a.e1_dir:
        c = pd.read_csv(os.path.join(a.e1_dir, "e1_prediction_cells.csv"))
        tabs = []
        for ax_ in ("G", "n_L", "R2", "kappa", "lambda_star"):
            t = c.groupby(["prediction", ax_]).in_band.agg(["size", "sum"]).reset_index().rename(
                columns={ax_: "level", "size": "n_cells", "sum": "n_in_band"})
            t["axis"] = ax_
            tabs.append(t)
        pd.concat(tabs).to_csv(os.path.join(a.e1_dir, "e1_tabulations.csv"), index=False)
    print(pd.DataFrame(acc).to_string()); print(pd.DataFrame(scores).to_string())


if __name__ == "__main__":
    main()
