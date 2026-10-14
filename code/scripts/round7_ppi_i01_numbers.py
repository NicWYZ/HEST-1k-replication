"""Round 7 inference track, interval i01: pooled numbers and the scores of predictions S1.1 to S2.4.

Reads the merged tables (round7_ppi_merge.py) from --s1-dir and --s2-dir and writes in the working directory
s1_report_numbers.csv, s2_report_numbers.csv (name, value, source, note), i01_prediction_scores.csv and
i01_prediction_cells.csv. Every number of the S2 report that is pooled over cells is a row here.
Operational definitions of the predictions are in the docstrings of score_* and are repeated in the report.
"""
import argparse
import os

import numpy as np
import pandas as pd

NOM = 0.90
TISSUE = ("CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM")
CENSUS = ("ACS_STATES", "ACS_CA_PUMA")
LIN = "textbook_t|fpc|lin"


class Num:
    def __init__(self):
        self.rows = []

    def add(self, name, value, source, note=""):
        self.rows.append(dict(name=name, value=value, source=source, note=note))


def verdict(ok_all, ok_part):
    return "held" if ok_all else ("partly held" if ok_part else "refuted")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s1-dir", required=True)
    ap.add_argument("--s2-dir", required=True)
    a = ap.parse_args()
    S1M = os.path.join(a.s1_dir, "s1_masking_grid.csv"); S1D = os.path.join(a.s1_dir, "s1_masking_diag.csv")
    S1S = os.path.join(a.s1_dir, "s1_sim.csv"); S2M = os.path.join(a.s2_dir, "s2_masking_grid.csv")
    S2S = os.path.join(a.s2_dir, "s2_sim.csv")
    m = pd.read_csv(S1M); dg = pd.read_csv(S1D); s = pd.read_csv(S1S)
    m2 = pd.read_csv(S2M); s2 = pd.read_csv(S2S)
    n1, n2 = Num(), Num()
    scores, cells = [], []
    d2diag = dg[dg["part"] == "D2"].copy()
    sup = d2diag[["vtag", "arm", "estimand", "n_L", "balance", "p_a", "support"]]
    md2 = m[m["design"] == "D2"].merge(sup, on=["vtag", "arm", "estimand", "n_L", "balance", "p_a"], how="left")

    # ---------------- S1 predictions
    # S1.1: sim, k = 2, n_L <= 6, D2 cells: classical |bias|/sd (noise-corrected rms) > 0.1 in >= 1/4 of cells; Hajek
    # (sim, t_{n-k-1}) covers within 0.03 of 0.90 in >= 3/4 of them (cells where it is not formed count as not within).
    c = s[(s["design"] == "D2") & (s["k"] == 2) & (s["n_L"] <= 6)]
    cl = c[(c["estimator"] == "classical") & (c["variance"] == LIN)]
    hj = c[(c["estimator"] == "H") & (c["variance"] == "sim") & (c["ref"] == "res")]
    hj1 = c[(c["estimator"] == "H") & (c["variance"] == "sim") & (c["ref"] == "n1")]
    sb = float((cl["bias_over_sd_rms_corrected"] > 0.1).mean())
    sh = float((np.abs(hj["coverage_mean"] - NOM) <= 0.03).mean())
    sh1 = float((np.abs(hj1["coverage_mean"] - NOM) <= 0.03).mean())
    scores.append(dict(prediction="S1.1", verdict=verdict(sb >= 0.25 and sh >= 0.75, sb >= 0.25 or sh >= 0.75),
                       summary=f"share of cells with classical bias > 0.1 sd: {sb:.3f} of {len(cl)}; Hajek (t_(n-k-1)) within 0.03 of 0.90: {sh:.3f}; with t_(n-1): {sh1:.3f}"))
    n1.add("S1.1_share_classical_bias_gt_0.1sd", sb, S1S, f"{len(cl)} cells, k=2, n_L<=6")
    n1.add("S1.1_share_H_sim_res_within_0.03", sh, S1S); n1.add("S1.1_share_H_sim_n1_within_0.03", sh1, S1S)
    cells.append(cl.assign(prediction="S1.1", part="classical")); cells.append(hj.assign(prediction="S1.1", part="H_res"))
    # S1.2: real tasks, pcF2 and pcE2, n_L = 6: among cells where rej_t covered < 0.80, Hajek (sim, res) covers within
    # 0.03 of the D0 classical interval in at most half.
    r = md2[(md2["balance"].isin(["pcF2", "pcE2"])) & (md2["n_L"] == 6)]
    rj = r[(r["estimator"] == "classical") & (r["variance"] == "rej_t")][["vtag", "arm", "estimand", "balance", "p_a", "coverage_median", "coverage_D0cl_median"]]
    low = rj[rj["coverage_median"] < 0.80]
    h = r[(r["estimator"] == "H") & (r["variance"] == "sim") & (r["ref"] == "res")][["vtag", "arm", "estimand", "balance", "p_a", "coverage_median"]]
    j = low.merge(h, on=["vtag", "arm", "estimand", "balance", "p_a"], suffixes=("_rej", "_H"))
    within = np.abs(j["coverage_median_H"] - j["coverage_D0cl_median"]) <= 0.03
    share = float(within.mean()) if len(j) else np.nan
    scores.append(dict(prediction="S1.2", verdict=("not tested" if not len(j) else ("held" if share <= 0.5 else "refuted")),
                       summary=f"{len(j)} cells with rej_t below 0.80 at n_L 6 with pcF2/pcE2; Hajek within 0.03 of D0 classical in {int(within.sum())} ({share:.3f})"))
    n1.add("S1.2_n_cells_rej_below_0.80", len(j), S1M); n1.add("S1.2_n_H_within_0.03", int(within.sum()), S1M)
    cells.append(j.assign(prediction="S1.2", within=within))
    # S1.3: n_L = 8, own balance, supported cells (support >= 1000): Hajek (sim, res) wider than rej_t in every cell,
    # by a width ratio (ratio of median widths) of 1.10 to 1.50.
    r = md2[(md2["balance"] == "own") & (md2["n_L"] == 8) & (md2["support"] >= 1000)]
    k_ = ["vtag", "arm", "estimand", "p_a"]
    w = r[(r["estimator"] == "H") & (r["variance"] == "sim") & (r["ref"] == "res")][k_ + ["width_median"]].merge(
        r[(r["estimator"] == "classical") & (r["variance"] == "rej_t")][k_ + ["width_median"]], on=k_, suffixes=("_H", "_rej"))
    w["ratio"] = w["width_median_H"] / w["width_median_rej"]
    wider = (w["ratio"] > 1).mean(); inband = w["ratio"].between(1.10, 1.50).mean()
    scores.append(dict(prediction="S1.3", verdict=verdict(wider == 1 and inband == 1, wider >= 0.5 or inband >= 0.5),
                       summary=f"{len(w)} cells; Hajek wider in {wider:.3f}; ratio in 1.10-1.50 in {inband:.3f}; ratio range {w['ratio'].min():.3f} to {w['ratio'].max():.3f}, median {w['ratio'].median():.3f}"))
    for nm, v in (("n_cells", len(w)), ("share_wider", wider), ("share_in_band", inband), ("ratio_min", w["ratio"].min()),
                  ("ratio_max", w["ratio"].max()), ("ratio_median", w["ratio"].median())):
        n1.add(f"S1.3_{nm}", v, S1M)
    cells.append(w.assign(prediction="S1.3"))
    # S1.4: theta3, own, p_a 0.01, n_L 4: smallest pi_hat below 0.5 n_L/G on both census tasks (package arm).
    q = d2diag[(d2diag["vtag"].isin(CENSUS)) & (d2diag["arm"] == "package") & (d2diag["estimand"] == "theta3")
               & (d2diag["balance"] == "own") & (np.isclose(d2diag["p_a"], 0.01)) & (d2diag["n_L"] == 4)]
    okq = (q["pi_ratio_min_min"] < 0.5)
    scores.append(dict(prediction="S1.4", verdict=verdict(len(q) == 2 and okq.all(), okq.any()),
                       summary="; ".join(f"{r_.vtag} min pi_hat / (n_L/G) = {r_.pi_ratio_min_min:.4f}" for r_ in q.itertuples())))
    for r_ in q.itertuples():
        n1.add(f"S1.4_pi_ratio_min_{r_.vtag}", r_.pi_ratio_min_min, S1D)
    cells.append(q.assign(prediction="S1.4"))

    # ---------------- S1 pooled numbers
    for est, var, ref in (("classical", LIN, "n1"), ("classical", "rej_t", "res"), ("HT", "sim", "res"), ("H", "sim", "res"),
                          ("H", "sim", "n1"), ("H", "apx_size", "res"), ("H", "apx_bal", "res"), ("HTl", "sim", "res"), ("BH", "bh", "normal")):
        x = md2[(md2["estimator"] == est) & (md2["variance"] == var) & (md2["ref"] == ref) & (md2["support"] >= 1000)]
        tag = f"{est}|{var}|{ref}"
        n1.add(f"S1m_supported_cells|{tag}", len(x), S1M)
        n1.add(f"S1m_coverage_median_over_cells|{tag}", x["coverage_median"].median(), S1M, "support >= 1000, median over cells of the median over genes")
        n1.add(f"S1m_coverage_min_over_cells|{tag}", x["coverage_median"].min(), S1M)
        n1.add(f"S1m_share_within_0.03_of_D0cl|{tag}", (np.abs(x["coverage_median"] - x["coverage_D0cl_median"]) <= 0.03).mean(), S1M)
        n1.add(f"S1m_share_below_0.80|{tag}", (x["coverage_median"] < 0.80).mean(), S1M)
        n1.add(f"S1m_wr_D0cl_median|{tag}", x["wr_D0cl_median"].median(), S1M)
        n1.add(f"S1m_share_bias_z_gt3_median|{tag}", x["share_bias_z_gt3"].median(), S1M)
    n1.add("S1m_D2_cells", len(d2diag), S1D)
    n1.add("S1m_D2_cells_with_pgh_zero", int((d2diag["share_pairs_pgh_zero"] > 0).sum()), S1D)
    for t in TISSUE + CENSUS:
        x = d2diag[d2diag["vtag"] == t]
        n1.add(f"S1m_cells_with_pgh_zero|{t}", int((x["share_pairs_pgh_zero"] > 0).sum()), S1D, f"of {len(x)}")
        n1.add(f"S1m_max_share_pairs_pgh_zero|{t}", x["share_pairs_pgh_zero"].max(), S1D)
    n1.add("S1m_D2_cells_with_pi_zero_column", int((d2diag["n_columns_with_pi_zero"] > 0).sum()), S1D)
    n1.add("S1m_apx_bal_rel_err_median", d2diag["apx_bal_rel_err_median"].median(), S1D)
    n1.add("S1m_apx_size_rel_err_median", d2diag["apx_size_rel_err_median"].median(), S1D)
    for col in ("share_genes_bias_z_gt3_classical", "share_genes_bias_z_gt3_HT", "share_genes_bias_z_gt3_H",
                "share_genes_bias_z_gt3_HT_pi_half_a", "share_genes_bias_z_gt3_HT_pi_half_b"):
        n1.add(f"S1m_median_over_D2_cells|{col}", d2diag[col].median(), S1D)
        n1.add(f"S1m_max_over_D2_cells|{col}", d2diag[col].max(), S1D)
    d0 = dg[dg["part"] == "D0_identity"]
    n1.add("S1m_D0_identity_HT_minus_classical_max", d0["ht_minus_classical_max"].max(), S1D)
    # Bias of the weighted estimators against a zero pi_hat in the cell (S2 report, expectation 1 of theory 1.8).
    zc = d2diag["n_columns_with_pi_zero"] > 0
    for t in TISSUE + CENSUS:
        n1.add(f"S1m_D2_cells_with_pi_zero_column|{t}", int((zc & (d2diag["vtag"] == t)).sum()), S1D)
    for e_ in ("classical", "HT", "H"):
        col = f"share_genes_bias_z_gt3_{e_}"
        hi = d2diag[col] > 0.1
        n1.add(f"S1m_D2_cells_bias_share_gt_0.1|{e_}", int(hi.sum()), S1D, "share of genes with |z| > 3 above 0.1")
        n1.add(f"S1m_D2_cells_bias_share_gt_0.1_with_pi_zero_column|{e_}", int((hi & zc).sum()), S1D)
        n1.add(f"S1m_median_bias_share_cells_without_pi_zero_column|{e_}", d2diag.loc[~zc, col].median(), S1D)
        n1.add(f"S1m_median_bias_share_cells_with_pi_zero_column|{e_}", d2diag.loc[zc, col].median(), S1D)
    sd2 = s[s["design"] == "D2"]
    for est, var, ref in (("classical", LIN, "n1"), ("classical", "rej_t", "res"), ("HT", "sim", "res"), ("H", "sim", "res"),
                          ("H", "sim", "n1"), ("H", "apx_size", "res"), ("H", "apx_bal", "res"), ("HTl", "sim", "res"), ("BH", "bh", "normal")):
        for law in ("n", "s"):
            for k in (1, 2):
                x = sd2[(sd2["estimator"] == est) & (sd2["variance"] == var) & (sd2["ref"] == ref) & (sd2["law"] == law) & (sd2["k"] == k)]
                tag = f"{est}|{var}|{ref}|{law}|k{k}"
                n1.add(f"S1s_cells|{tag}", len(x), S1S)
                n1.add(f"S1s_coverage_mean_over_cells|{tag}", x["coverage_mean"].mean(), S1S)
                n1.add(f"S1s_share_within_0.03_of_0.90|{tag}", (np.abs(x["coverage_mean"] - NOM) <= 0.03).mean(), S1S)
                n1.add(f"S1s_coverage_min|{tag}", x["coverage_mean"].min(), S1S)
                n1.add(f"S1s_est_over_emp_median|{tag}", x["est_over_emp_mean"].median(), S1S)
                n1.add(f"S1s_wr_D0cl_median|{tag}", x["wr_D0cl"].median(), S1S)
                n1.add(f"S1s_share_cells_bias_gt_0.1sd|{tag}", (x["bias_over_sd_rms_corrected"] > 0.1).mean(), S1S)
    n1.add("S1s_D2_cells_with_pgh_zero", int((sd2.drop_duplicates(["G", "n_L", "R2", "lambda_star", "law", "k", "p_a"])["share_pairs_pgh_zero"] > 0).sum()), S1S)
    n1.add("S1s_D2_cells", int(len(sd2.drop_duplicates(["G", "n_L", "R2", "lambda_star", "law", "k", "p_a"]))), S1S)

    # ---------------- S2 predictions
    A = m2[m2["set"] == "A_fixed"]; Bw = m2[m2["set"] == "B_world"]
    bh = A[(A["design"] == "D0") & (A["estimator"] == "BH")]
    # S2.1: D0, design target, BH covers below 0.85 at n_L 4 on at least two of four tissue tasks (per task, the median
    # over arms and estimands of the median-over-genes coverage).
    t = bh[(bh["vtag"].isin(TISSUE)) & (bh["n_L"] == 4)].groupby("vtag")["coverage_design_median"].median()
    nb = int((t < 0.85).sum())
    scores.append(dict(prediction="S2.1", verdict="held" if nb >= 2 else "refuted",
                       summary="; ".join(f"{k} {v:.3f}" for k, v in t.items()) + f"; tasks below 0.85: {nb}"))
    for k, v in t.items():
        n2.add(f"S2.1_BH_design_coverage_nL4|{k}", v, S2M, "median over arms and estimands")
    # S2.2: design target, n_L/G >= 0.5 (lung n_L 8, 12; CCRCC and CCRCC_merged n_L 12): BH covers above 0.95.
    x = bh[((bh["vtag"] == "LUNG_XENIUM") & (bh["n_L"].isin([8, 12]))) | ((bh["vtag"].isin(["CCRCC", "CCRCC_merged"])) & (bh["n_L"] == 12))]
    ok = x["coverage_design_median"] > 0.95
    scores.append(dict(prediction="S2.2", verdict=verdict(ok.all(), ok.mean() >= 0.5),
                       summary=f"{int(ok.sum())} of {len(x)} cells above 0.95; range {x['coverage_design_median'].min():.3f} to {x['coverage_design_median'].max():.3f}"))
    n2.add("S2.2_cells", len(x), S2M); n2.add("S2.2_cells_above_0.95", int(ok.sum()), S2M)
    n2.add("S2.2_coverage_min", x["coverage_design_median"].min(), S2M); n2.add("S2.2_coverage_max", x["coverage_design_median"].max(), S2M)
    cells.append(x.assign(prediction="S2.2"))
    # S2.3: superpopulation target, BH covers below 0.85 at n_L <= 6 in every simulation cell with G = 15.
    y = s2[(s2["design"] == "D0") & (s2["estimator"] == "BH") & (s2["G"] == 15) & (s2["n_L"] <= 6)]
    ok = y["coverage_super_mean"] < 0.85
    scores.append(dict(prediction="S2.3", verdict=verdict(ok.all(), ok.mean() >= 0.5),
                       summary=f"{int(ok.sum())} of {len(y)} cells below 0.85; range {y['coverage_super_mean'].min():.3f} to {y['coverage_super_mean'].max():.3f}"))
    n2.add("S2.3_cells", len(y), S2S); n2.add("S2.3_cells_below_0.85", int(ok.sum()), S2S)
    n2.add("S2.3_coverage_min", y["coverage_super_mean"].min(), S2S); n2.add("S2.3_coverage_max", y["coverage_super_mean"].max(), S2S)
    cells.append(y.assign(prediction="S2.3"))
    # S2.4: superpopulation target, Kluger's cluster bootstrap covers below 0.85 at n_L <= 8 on every task (resampled
    # world, both Bernoulli designs, every arm and estimand).
    z = Bw[(Bw["estimator"] == "kluger_ptd") & (Bw["n_L"] <= 8)]
    pt = z.groupby("vtag")["coverage_super_median"].agg(["median", "max", "size"])
    okc = z["coverage_super_median"] < 0.85
    scores.append(dict(prediction="S2.4", verdict=verdict(okc.all(), okc.mean() >= 0.5),
                       summary=f"{int(okc.sum())} of {len(z)} cells below 0.85; per task median " + "; ".join(f"{k} {r_['median']:.3f}" for k, r_ in pt.iterrows())))
    n2.add("S2.4_cells", len(z), S2M); n2.add("S2.4_cells_below_0.85", int(okc.sum()), S2M)
    for k, r_ in pt.iterrows():
        n2.add(f"S2.4_kluger_super_coverage_median|{k}", r_["median"], S2M); n2.add(f"S2.4_kluger_super_coverage_max|{k}", r_["max"], S2M)
    cells.append(z.assign(prediction="S2.4"))
    # ---------------- S2 pooled numbers
    for setname, X, tgts in (("A_fixed", A, ("design",)), ("B_world", Bw, ("design", "super"))):
        for (dname, est, iv), x in X.groupby(["design", "estimator", "interval"]):
            for tg in tgts:
                for nl in sorted(x["n_L"].unique()):
                    xx = x[x["n_L"] == nl]
                    tag = f"{setname}|{dname}|{est}|{iv}|{tg}|nL{nl}"
                    n2.add(f"S2m_coverage_median_over_cells|{tag}", xx[f"coverage_{tg}_median"].median(), S2M)
                    n2.add(f"S2m_coverage_min|{tag}", xx[f"coverage_{tg}_median"].min(), S2M)
                    n2.add(f"S2m_coverage_max|{tag}", xx[f"coverage_{tg}_median"].max(), S2M)
            n2.add(f"S2m_wr_D0cl_median|{setname}|{dname}|{est}|{iv}", x["wr_D0cl_median"].median(), S2M)
    for (dname, est, iv, G), x in s2.groupby(["design", "estimator", "interval", "G"]):
        for tg in ("design", "super"):
            for nl in sorted(x["n_L"].unique()):
                xx = x[x["n_L"] == nl]
                tag = f"{dname}|{est}|{iv}|{tg}|G{G}|nL{nl}"
                n2.add(f"S2s_coverage_mean_over_cells|{tag}", xx[f"coverage_{tg}_mean"].mean(), S2S)
                n2.add(f"S2s_coverage_min|{tag}", xx[f"coverage_{tg}_mean"].min(), S2S)
                n2.add(f"S2s_coverage_max|{tag}", xx[f"coverage_{tg}_mean"].max(), S2S)
    kl = m2[(m2["design"].str.startswith("bern"))]
    n2.add("S2m_share_nL_lt2_max", kl["share_nL_lt2_median"].max(), S2M)
    n2.add("S2m_boot_drop_max", kl["boot_drop_mean_median"].max() if "boot_drop_mean_median" in kl else np.nan, S2M)
    pd.DataFrame(n1.rows).to_csv("s1_report_numbers.csv", index=False, float_format="%.10g")
    pd.DataFrame(n2.rows).to_csv("s2_report_numbers.csv", index=False, float_format="%.10g")
    pd.DataFrame(scores).to_csv("i01_prediction_scores.csv", index=False)
    pd.concat(cells, ignore_index=True).to_csv("i01_prediction_cells.csv", index=False, float_format="%.10g")
    print(pd.DataFrame(scores).to_string())


if __name__ == "__main__":
    main()
