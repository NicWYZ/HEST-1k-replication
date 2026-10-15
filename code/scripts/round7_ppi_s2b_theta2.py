"""Round 7 inference track, S2b item 1: the recount for theta2 (S2 memo, docs/round07/i02/ppi/round07_ppi_S2_decisions.md,
sections 3 and 5).

--mode d0. For one task and arm, theta2 only, every n_L given: the D0 classical interval textbook_t|fpc|lin on the D0
draws of S1 (round 4's draw_L seeds, candidate 0 of round5_ppi_e4b_rejective.cand_idx, draws with fewer than two valid
labelled clusters dropped as in S1), per gene, under two forming rules.
  * r7_df2. An interval is formed when its degrees of freedom are at least 2 (round7_ppi_weighting.summarise). This is
    what S1 did, so these rows must equal S1's D0 classical rows exactly (the anchor arm of this rerun).
  * def_df1. An interval is formed when it has at least two valid labelled clusters, with t_{n_v - 1}, so 1 degree of
    freedom is allowed (docs/round05/tracks/ppi/round5_ppi_estimator_definition.md, sections "The draw for theta2" and
    "The between-cluster coefficient and the interval").
  Writes s2b_d0__<vtag>__<arm>.csv: n_L, gene, rule, coverage (over formed draws), share_formed (over kept draws),
  share_dropped (over all draws), coverage_all (over all draws, a draw without an interval counted as a miss), width.

--mode recount. From the S1 unit gene tables of the merged directories, the d0 outputs, round 5's E4b tables and S1's
diagnostics, writes in the working directory:
  * s2b1_cells.csv. Every theta2 cell (D0 and D2) and every estimator, variance and reference: median over genes of the
    coverage over draws with an interval (coverage_cond), of the coverage over all draws with a miss for no interval
    (coverage_all = coverage x share_formed, and for D0 also x (1 - share_dropped)), of share_formed, and the width
    ratio to D0 classical under S1's rule (wr_D0cl_r7) and under the definition's rule (wr_D0cl_def).
  * s2b1_round5_check.csv. Every rej_t theta2 cell matched to round 5's e4b_rej_width_ratios.csv, with round 5's
    coverage, round 7's coverage_cond, its share formed, the memo's product of the two cell medians, the median over genes
    of the per-gene product, the differences, a Monte Carlo tolerance and the cells outside it, and the D0 classical
    coverage of both rounds.
  * s2b1_support.csv. Each theta2 D2 cell's support counted over all clusters and over the valid ones.
  * s2b1_thresholds.csv. Each matched theta2 D2 cell's median threshold in round 7 and round 5 and their ratio.
  * s2b1_numbers.csv (name, value, source, note). Every pooled number the S4 report quotes from this item.
"""
import argparse
import glob
import math
import os

import numpy as np
import pandas as pd

LIN = "textbook_t|fpc|lin"
TISSUE = ("CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM")
KEY = ["vtag", "arm", "estimand", "n_L", "design", "balance", "p_a", "estimator", "variance", "ref"]


def mode_d0(a):
    import round7_ppi_d2 as D2
    import round7_ppi_weighting as W
    import round5_ppi_balance as BAL
    from round7_ppi_s1_masking import summarise_nofloor
    cell = D2.load_cell(a.parquet, a.perm_parquet, a.ref_parquet, a.ref_arm, a.vtag, a.arm, "theta2", a.root,
                        a.theta2_kind)
    G, genes, theta = cell["G"], cell["genes"], cell["theta"]
    ng = len(genes)
    rows = []
    for nL in [int(x) for x in a.nls.split(",")]:
        if nL > cell["Gall"] - 2:
            continue
        first = D2.r5_first(cell, nL, n_cand=1)
        L0 = np.zeros((a.draws, G, ng), bool)
        for d in range(a.draws):
            L0[d] = np.isin(cell["vid"], first[d, 0])[:, None]
        bad0 = L0.sum(1).min(1) < 2
        idx = np.flatnonzero(~bad0)
        th = np.full((len(idx), ng), np.nan); v = th.copy(); df = th.copy()
        for i, d in enumerate(idx):
            out, _ = BAL.estimate_srs_like(cell["zbar"], cell["fbar"], L0[d], "none",
                                           f"q2|{cell['vtag']}|nL{nL}|m0|d{i}|theta2|donor|none")
            th[i], v[i], df[i] = out[LIN][0], out[LIN][1], np.broadcast_to(out[LIN][2], (ng,))
        for rule, s in (("r7_df2", W.summarise(th, v, df, theta)), ("def_df1", summarise_nofloor(th, v, df, theta))):
            kept = len(idx) / a.draws
            for j, g in enumerate(genes):
                rows.append(dict(vtag=a.vtag, arm=a.arm, estimand="theta2", n_L=nL, gene=g, rule=rule,
                                 coverage=s["coverage"][j], share_formed=s["share_formed"][j],
                                 share_dropped=1 - kept, coverage_all=s["coverage"][j] * s["share_formed"][j] * kept,
                                 width=s["width"][j]))
        print(f"{a.vtag} {a.arm} nL{nL} dropped {bad0.mean():.4f}", flush=True)
    os.makedirs(a.out_dir, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"s2b_d0__{a.vtag}__{a.arm}.csv"), index=False,
                              float_format="%.10g")


def merged_dirs(s1):
    st = pd.read_csv(os.path.join(s1, "_merged", "s1_stamp_check.csv"))
    return [os.path.join(s1, d) for d in st.loc[st["merged"] & (st["task"] != "sim"), "dir"]]


def mode_recount(a):
    num = []
    add = lambda n, v, src, note="": num.append(dict(name=n, value=v, source=src, note=note))
    parts = []
    for d in merged_dirs(a.s1_dir):
        for f in glob.glob(os.path.join(d, "s1m_genes__*.csv.gz")):
            for ch in pd.read_csv(f, chunksize=200_000, low_memory=False):
                parts.append(ch[ch["estimand"] == "theta2"])
    g = pd.concat(parts, ignore_index=True)
    g["coverage_all"] = g["coverage"] * g["share_formed"]
    d0 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(a.d0_dir, "**", "s2b_d0__*.csv"), recursive=True)], ignore_index=True)
    # anchor: the r7_df2 rerun equals S1's D0 classical rows
    s1d0 = g[(g["design"] == "D0") & (g["estimator"] == "classical") & (g["variance"] == LIN)]
    an = s1d0.merge(d0[d0["rule"] == "r7_df2"], on=["vtag", "arm", "n_L", "gene"], suffixes=("", "_re"))
    add("anchor_d0_rows_matched", len(an), "s2b_d0", f"of {len(s1d0)} S1 D0 classical theta2 gene rows on tissue")
    add("anchor_d0_max_abs_dcoverage", float(np.nanmax(np.abs(an["coverage"] - an["coverage_re"]))), "s2b_d0")
    add("anchor_d0_max_abs_dwidth_rel", float(np.nanmax(np.abs(an["width"] / an["width_re"] - 1))), "s2b_d0")
    add("anchor_d0_max_abs_dshare_formed", float(np.nanmax(np.abs(an["share_formed"] - an["share_formed_re"]))), "s2b_d0")
    # D0 coverage over all draws in S1 needs the dropped share
    drop = d0[d0["rule"] == "r7_df2"].groupby(["vtag", "arm", "n_L"])["share_dropped"].first().rename("share_dropped")
    g = g.merge(drop.reset_index(), on=["vtag", "arm", "n_L"], how="left")
    isd0 = g["design"] == "D0"
    g.loc[isd0, "coverage_all"] = g.loc[isd0, "coverage_all"] * (1 - g.loc[isd0, "share_dropped"].fillna(0))
    # widths: D0 classical under each rule
    w7 = s1d0[["vtag", "arm", "n_L", "gene", "width"]].rename(columns={"width": "w_d0_r7"})
    wd = d0[d0["rule"] == "def_df1"][["vtag", "arm", "n_L", "gene", "width", "coverage", "coverage_all", "share_formed"]].rename(
        columns={"width": "w_d0_def", "coverage": "cov_d0_def", "coverage_all": "covall_d0_def", "share_formed": "sf_d0_def"})
    g = g.merge(w7, on=["vtag", "arm", "n_L", "gene"], how="left").merge(wd, on=["vtag", "arm", "n_L", "gene"], how="left")
    g["wr_r7"] = g["width"] / g["w_d0_r7"]
    g["wr_def"] = g["width"] / g["w_d0_def"]
    med = lambda s: float(np.nanmedian(s)) if np.isfinite(s).any() else np.nan
    cells = g.groupby(KEY, dropna=False).agg(
        n_genes=("gene", "size"), coverage_cond=("coverage", med), coverage_all=("coverage_all", med),
        share_formed=("share_formed", med), wr_D0cl_r7=("wr_r7", med), wr_D0cl_def=("wr_def", med),
        coverage_D0cl_def=("cov_d0_def", med), coverage_all_D0cl_def=("covall_d0_def", med),
        share_formed_D0cl_def=("sf_d0_def", med)).reset_index()
    diag = pd.read_csv(os.path.join(a.s1_dir, "_merged", "s1_masking_diag.csv"))
    dd = diag[(diag["part"] == "D2") & (diag["estimand"] == "theta2")].copy()
    sup = dd[["vtag", "arm", "estimand", "n_L", "balance", "p_a", "G", "Gall", "threshold_median"]].copy()
    sup["support_all"] = [p * math.comb(int(Ga), int(n)) for p, Ga, n in zip(sup["p_a"], sup["Gall"], sup["n_L"])]
    sup["support_valid"] = [p * math.comb(int(G_), int(n)) if n <= G_ else 0.0 for p, G_, n in zip(sup["p_a"], sup["G"], sup["n_L"])]
    sup["supported_all"] = sup["support_all"] >= 1000
    sup["supported_valid"] = sup["support_valid"] >= 1000
    sup["degenerate_nL_ge_valid"] = sup["n_L"] >= sup["G"]
    sup.drop(columns=["threshold_median"]).to_csv("s2b1_support.csv", index=False, float_format="%.10g")
    kk = ["vtag", "arm", "estimand", "n_L", "balance", "p_a"]
    cells = cells.merge(sup[kk + ["support_all", "support_valid", "supported_all", "supported_valid"]], on=kk, how="left")
    cells.to_csv("s2b1_cells.csv", index=False, float_format="%.10g")
    add("theta2_cells_D2", int(len(sup)), "s2b1_support.csv")
    add("theta2_cells_supported_all", int(sup["supported_all"].sum()), "s2b1_support.csv")
    add("theta2_cells_supported_valid", int(sup["supported_valid"].sum()), "s2b1_support.csv")
    add("theta2_cells_degenerate_nL_ge_valid", int(sup["degenerate_nL_ge_valid"].sum()), "s2b1_support.csv")
    # the S2 report's section 6.1 table, theta2 rows, three forms, over cells supported by each count
    tab = [("classical", LIN, "n1"), ("classical", "rej_t", "res"), ("HT", "sim", "res"), ("H", "sim", "res"),
           ("H", "sim", "n1"), ("H", "apx_size", "res"), ("H", "apx_bal", "res"), ("HTl", "sim", "res"), ("BH", "bh", "normal")]
    d2c = cells[cells["design"] == "D2"]
    for sc in ("supported_all", "supported_valid"):
        for e_, v_, r_ in tab:
            x = d2c[(d2c["estimator"] == e_) & (d2c["variance"] == v_) & (d2c["ref"] == r_) & (d2c[sc] == True)]
            t = f"{e_}|{v_}|{r_}|{sc}"
            add(f"t61_cells|{t}", len(x), "s2b1_cells.csv")
            for col in ("coverage_all", "coverage_cond", "share_formed"):
                add(f"t61_{col}_median|{t}", med(x[col]), "s2b1_cells.csv")
                add(f"t61_{col}_min|{t}", float(x[col].min()) if len(x) else np.nan, "s2b1_cells.csv")
            add(f"t61_share_below_0.80_all|{t}", float((x["coverage_all"] < 0.80).mean()) if len(x) else np.nan, "s2b1_cells.csv")
            add(f"t61_share_below_0.80_cond|{t}", float((x["coverage_cond"] < 0.80).mean()) if len(x) else np.nan, "s2b1_cells.csv")
            add(f"t61_wr_D0cl_r7_median|{t}", med(x["wr_D0cl_r7"]), "s2b1_cells.csv")
            add(f"t61_wr_D0cl_def_median|{t}", med(x["wr_D0cl_def"]), "s2b1_cells.csv")
    # against round 5, cell by cell
    r5 = pd.read_csv(a.r5_e4b)
    r5 = r5[r5["estimand"] == "theta2"]
    rj = cells[(cells["design"] == "D2") & (cells["estimator"] == "classical") & (cells["variance"] == "rej_t")]
    j = rj.merge(r5[kk + ["coverage", "coverage_D0cl", "wr_D0cl", "support"]].rename(columns={
        "coverage": "coverage_r5", "coverage_D0cl": "coverage_D0cl_r5", "wr_D0cl": "wr_D0cl_r5", "support": "support_r5"}), on=kk)
    d0c = cells[(cells["design"] == "D0") & (cells["estimator"] == "classical") & (cells["variance"] == LIN)][
        ["vtag", "arm", "n_L", "coverage_cond", "coverage_all", "share_formed"]].rename(columns={
            "coverage_cond": "d0_r7_cond", "coverage_all": "d0_r7_all", "share_formed": "d0_r7_share_formed"})
    j = j.merge(d0c, on=["vtag", "arm", "n_L"], how="left")
    j["product_of_medians"] = j["coverage_cond"] * j["share_formed"]
    j["d_cond"] = j["coverage_cond"] - j["coverage_r5"]
    j["d_product"] = j["product_of_medians"] - j["coverage_r5"]
    j["d_all"] = j["coverage_all"] - j["coverage_r5"]
    j["mc_tol"] = 2 * np.sqrt(np.clip(j["coverage_r5"] * (1 - j["coverage_r5"]), 0.0025, None) / 2000)
    j["outside_mc_product"] = j["d_product"].abs() > j["mc_tol"]
    j["outside_mc_all"] = j["d_all"].abs() > j["mc_tol"]
    j["outside_0.03_product"] = j["d_product"].abs() > 0.03
    j["d_D0cl_def_all"] = j["coverage_all_D0cl_def"] - j["coverage_D0cl_r5"]
    j["d_wr_def"] = j["wr_D0cl_def"] - j["wr_D0cl_r5"]
    j["d_wr_r7"] = j["wr_D0cl_r7"] - j["wr_D0cl_r5"]
    j.to_csv("s2b1_round5_check.csv", index=False, float_format="%.10g")
    big = j["d_cond"].abs() > 0.03
    add("r5_cells_matched", len(j), "s2b1_round5_check.csv")
    add("r5_cells_dcond_gt_0.03", int(big.sum()), "s2b1_round5_check.csv")
    add("r5_share_formed_max_where_dcond_gt_0.03", float(j.loc[big, "share_formed"].max()), "s2b1_round5_check.csv")
    add("r5_share_formed_min_where_dcond_le_0.03", float(j.loc[~big, "share_formed"].min()), "s2b1_round5_check.csv")
    for sel, nm in ((j["vtag"] != "LUNG_XENIUM", "not_lung"), (j["vtag"] == "LUNG_XENIUM", "lung"), (j["vtag"].notna(), "all")):
        x = j[sel]
        add(f"r5_cells|{nm}", len(x), "s2b1_round5_check.csv")
        for c in ("d_cond", "d_product", "d_all", "d_D0cl_def_all", "d_wr_def", "d_wr_r7"):
            add(f"r5_max_abs_{c}|{nm}", float(x[c].abs().max()), "s2b1_round5_check.csv")
            add(f"r5_median_abs_{c}|{nm}", float(x[c].abs().median()), "s2b1_round5_check.csv")
        add(f"r5_median_abs_d_product_where_dcond_gt_0.03|{nm}", float(x.loc[x["d_cond"].abs() > 0.03, "d_product"].abs().median()), "s2b1_round5_check.csv")
        add(f"r5_cells_outside_0.03_product|{nm}", int(x["outside_0.03_product"].sum()), "s2b1_round5_check.csv")
        add(f"r5_cells_outside_mc_product|{nm}", int(x["outside_mc_product"].sum()), "s2b1_round5_check.csv")
        add(f"r5_cells_outside_mc_all|{nm}", int(x["outside_mc_all"].sum()), "s2b1_round5_check.csv")
        add(f"r5_cells_outside_0.03_all|{nm}", int((x["d_all"].abs() > 0.03).sum()), "s2b1_round5_check.csv")
    for t in TISSUE:
        for nl in sorted(j["n_L"].unique()):
            x = j[(j["vtag"] == t) & (j["n_L"] == nl)]
            if len(x):
                add(f"r5_share_formed_median|{t}|nL{nl}", med(x["share_formed"]), "s2b1_round5_check.csv")
                add(f"r5_cells_outside_0.03_all|{t}|nL{nl}", int((x["d_all"].abs() > 0.03).sum()), "s2b1_round5_check.csv", f"of {len(x)}")
    # thresholds
    r5d = pd.read_csv(a.r5_diag)
    r5d = r5d[r5d["estimand"] == "theta2"][kk + ["threshold_median"]].rename(columns={"threshold_median": "threshold_median_r5"})
    th = dd[kk + ["threshold_median"]].merge(r5d, on=kk)
    th["ratio"] = th["threshold_median"] / th["threshold_median_r5"]
    th["differs_1e-6"] = (th["ratio"] - 1).abs() > 1e-6
    th.to_csv("s2b1_thresholds.csv", index=False, float_format="%.10g")
    for nm, x in (("not_lung", th[th["vtag"] != "LUNG_XENIUM"]), ("lung", th[th["vtag"] == "LUNG_XENIUM"])):
        add(f"thr_cells|{nm}", len(x), "s2b1_thresholds.csv")
        add(f"thr_cells_differ_1e-6|{nm}", int(x["differs_1e-6"].sum()), "s2b1_thresholds.csv")
        add(f"thr_max_abs_rel_diff|{nm}", float((x["ratio"] - 1).abs().max()), "s2b1_thresholds.csv")
    pd.DataFrame(num).to_csv("s2b1_numbers.csv", index=False, float_format="%.10g")
    print(len(g), len(cells), len(j), len(th))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("d0", "recount"), required=True)
    ap.add_argument("--parquet"); ap.add_argument("--perm-parquet"); ap.add_argument("--ref-parquet")
    ap.add_argument("--ref-arm"); ap.add_argument("--vtag"); ap.add_argument("--arm")
    ap.add_argument("--nls", default="4,6,8,12")
    ap.add_argument("--draws", type=int, default=2000)
    ap.add_argument("--theta2-kind", default="neo_minus_stroma")
    ap.add_argument("--root", default="/work/users/w/e/weiyang/hest_replication")
    ap.add_argument("--s1-dir", default="/work/users/w/e/weiyang/hest_replication/results/round7/ppi/S1_weighting")
    ap.add_argument("--d0-dir")
    ap.add_argument("--r5-e4b", default="/work/users/w/e/weiyang/hest_code/round7-ppi/results/round5/ppi/E4b_rejective/e4b_rej_width_ratios.csv")
    ap.add_argument("--r5-diag", default="/work/users/w/e/weiyang/hest_code/round7-ppi/results/round5/ppi/E4b_rejective/e4b_d2_diagnostics.csv")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--arms", default=""); ap.add_argument("--pred-dir", default="")
    a = ap.parse_args()
    np.seterr(all="ignore")
    if a.mode == "recount":
        return mode_recount(a)
    import copy
    for arm in (a.arms.split(",") if a.arms else [a.arm]):
        b = copy.copy(a); b.arm = arm
        if a.arms and a.pred_dir:
            pq_ = lambda m: os.path.join(a.pred_dir, f"b1_predictions__{a.vtag}__{m}.parquet")
            b.parquet = pq_("resnet50" if arm in ("permuted", "constant") else arm)
            b.perm_parquet = b.ref_parquet = pq_("resnet50"); b.ref_arm = "resnet50"
        mode_d0(b)


if __name__ == "__main__":
    main()
