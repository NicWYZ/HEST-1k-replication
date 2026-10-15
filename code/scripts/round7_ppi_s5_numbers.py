"""Round 7 inference track, S5: the closing numbers, from the merged tables of S1 to S4b with no new draws.

S4 memo, section 5, S5 item 1. Reads the per-gene tables of S1 (results/round7/ppi/S1_weighting/<task>/*/s1m_genes),
S2 (S2_comparators/<task>/*/s2m_genes), S2b item 3 (S2b_diagnostics/bh_small_sample/<task>/s2bm_genes), S3
(S3_adaptive/<task>/*/s3m_genes) and S4b (S4b_cube_constant/<task>/*/s4bm_genes), only from unit directories that their
stage's merge accepted (the stamp checks in the _merged directories), and writes in the working directory:

* s5_genes_long.csv.gz   one row per gene, cell and design, with coverage over formed draws, share formed and
                         coverage over all draws (a draw without an interval counted as a miss);
* s5_matched.csv         memo section 2 tables: informative arms, own balance, D2 support >= 1,000 at the given p_a,
                         degenerate cells dropped, cells matched across every design, by domain, n_L and p_a;
* s5_bh_vs_tuned.csv     D0 only: the classical and tuned intervals, Broska and Howes's interval as published and with
                         the project's correction, and Kluger et al., by domain, n_L and target, matched cells;
* s5_controls.csv        the same designs as s5_matched.csv on the constant and permuted arms, and D2 rej_t with
                         perm_cluster balance on the informative arms;
* s5_cube_widths.csv     HT and Hajek widths and balance residuals of every cube design, by domain and n_L;
* s5_report_numbers.csv  the numbers the final report quotes.
Figures are medians over cells of the median over genes. Widths are per-gene ratios to D0 classical
(`textbook_t|fpc|lin`) and to D2 rej_t at the same p_a, before the medians.
"""
import argparse
import glob
import os

import numpy as np
import pandas as pd

LIN, XF = "textbook_t|fpc|lin", "textbook_t|fpc|lin|xf"
INFORMATIVE = ("hoptimus0", "uni_v2", "resnet50", "package")
CONTROLS = ("constant", "permuted")
CENSUS = ("ACS_STATES", "ACS_CA_PUMA")
TASKS = ("CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM", "ACS_STATES", "ACS_CA_PUMA")
KEY = ["vtag", "arm", "estimand", "n_L", "gene"]
CELL = ["vtag", "arm", "estimand", "n_L"]
MATCHED = ["D0_classical", "D0_tuned", "D2_rej_t", "D2_H_sim", "cube_S3", "cube_S4b", "mixture", "bh", "bh_t"]
NOM = 0.90


class Numbers:
    def __init__(self):
        self.rows = []

    def add(self, name, value, source, note=""):
        self.rows.append(dict(name=name, value=value, source=source, note=note))

    def write(self, path):
        pd.DataFrame(self.rows).to_csv(path, index=False, float_format="%.10g")


def accepted(root, stage_dir, check):
    """unit directories the stage's merge accepted."""
    p = os.path.join(root, "results/round7/ppi", stage_dir, check)
    st = pd.read_csv(p)
    return {os.path.join(root, "results/round7/ppi", stage_dir, d) for d in st.loc[st["merged"], "dir"]}


def take(g, mask, design, cov="coverage", pa=None):
    x = g[mask].copy()
    out = pd.DataFrame({k: x[k] for k in KEY})
    out["design"] = design
    out["p_a"] = x["p_a"].values if pa == "col" else np.nan
    out["width"] = x["width"].values
    out["coverage"] = x[cov].values
    out["share_formed"] = x["share_formed"].values
    return out


def load(root):
    parts = []
    s1ok = accepted(root, "S1_weighting", "_merged/s1_stamp_check.csv")
    for f in sorted(glob.glob(os.path.join(root, "results/round7/ppi/S1_weighting/*/*/s1m_genes__*.csv.gz"))):
        if os.path.dirname(f) not in s1ok:
            continue
        g = pd.read_csv(f, low_memory=False)
        d0 = g["design"] == "D0"; d2 = g["design"] == "D2"
        parts += [take(g, d0 & (g["estimator"] == "classical") & (g["variance"] == LIN), "D0_classical"),
                  take(g, d0 & (g["estimator"] == "tuned") & (g["variance"] == LIN), "D0_tuned"),
                  take(g, d2 & (g["balance"] == "own") & (g["estimator"] == "classical") & (g["variance"] == "rej_t"), "D2_rej_t", pa="col"),
                  take(g, d2 & (g["balance"] == "own") & (g["estimator"] == "H") & (g["variance"] == "sim") & (g["ref"] == "res"), "D2_H_sim", pa="col"),
                  take(g, d2 & (g["balance"] == "perm_cluster") & (g["estimator"] == "classical") & (g["variance"] == "rej_t"), "D2pc_rej_t", pa="col")]
    s3ok = accepted(root, "S3_adaptive", "_merged_r2/s3_stamp_check.csv")
    for f in sorted(glob.glob(os.path.join(root, "results/round7/ppi/S3_adaptive/*/*/s3m_genes__*.csv.gz"))):
        if os.path.dirname(f) not in s3ok:
            continue
        g = pd.read_csv(f, low_memory=False)
        hs = (g["variance"] == "sim") & (g["ref"] == "res")
        parts += [take(g, (g["design"] == "cube_u1") & (g["estimator"] == "H") & hs, "cube_S3"),
                  take(g, (g["design"] == "cube_u1") & (g["estimator"] == "HT") & hs, "cube_S3_HT"),
                  take(g, (g["design"] == "cube_u2") & (g["estimator"] == "H") & hs, "cube_S3_u2"),
                  take(g, (g["design"] == "mix_D2D0") & (g["estimator"] == "H") & hs, "mixture", pa="col")]
    s4bok = accepted(root, "S4b_cube_constant", "_merged/s4b_stamp_check.csv")
    for f in sorted(glob.glob(os.path.join(root, "results/round7/ppi/S4b_cube_constant/*/*/s4bm_genes__*.csv.gz"))):
        if os.path.dirname(f) not in s4bok:
            continue
        g = pd.read_csv(f, low_memory=False)
        hs = g["variance"] == "sim"
        parts += [take(g, (g["estimator"] == "H") & hs & (g["ref"] == "res"), "cube_S4b"),
                  take(g, (g["estimator"] == "H") & hs & (g["ref"] == "n2"), "cube_S4b_n2"),
                  take(g, (g["estimator"] == "HT") & hs & (g["ref"] == "res"), "cube_S4b_HT")]
    # S2 and S2b: D0 comparators for both targets
    s2ok = accepted(root, "S2_comparators", "_merged/s2_stamp_check.csv")
    for f in sorted(glob.glob(os.path.join(root, "results/round7/ppi/S2_comparators/*/*/s2m_genes__*.csv.gz"))):
        if os.path.dirname(f) not in s2ok:
            continue
        g = pd.read_csv(f, low_memory=False)
        for s_, cov, suf in (("A_fixed", "coverage_design", ""), ("B_world", "coverage_super", "_super")):
            gs = g["set"] == s_
            d0 = gs & (g["design"] == "D0")
            parts += [take(g, d0 & (g["estimator"] == "tuned") & (g["interval"] == XF), "D0_tuned_xf" + suf, cov),
                      take(g, d0 & (g["estimator"] == "tuned") & (g["interval"] == "round5_superpop"), "D0_tuned_r5super" + suf, cov),
                      take(g, d0 & (g["estimator"] == "classical") & (g["interval"] == "round5_superpop"), "D0_classical_r5super" + suf, cov),
                      take(g, d0 & (g["estimator"] == "classical") & (g["interval"] == LIN), "D0_classical_S2" + suf, cov),
                      take(g, gs & (g["design"] == "bern_uniform") & (g["estimator"] == "kluger_ptd"), "kluger_uniform" + suf, cov),
                      take(g, gs & (g["design"] == "bern_score") & (g["estimator"] == "kluger_ptd"), "kluger_score" + suf, cov)]
    for f in sorted(glob.glob(os.path.join(root, "results/round7/ppi/S2b_diagnostics/bh_small_sample/*/s2bm_genes__*.csv.gz"))):
        g = pd.read_csv(f, low_memory=False)
        for s_, cov, suf in (("A_fixed", "coverage_design", ""), ("B_world", "coverage_super", "_super")):
            gs = (g["set"] == s_) & (g["design"] == "D0") & (g["estimator"] == "BH")
            for iv in ("bh", "bh_t", "bh_t_n2"):
                parts.append(take(g, gs & (g["interval"] == iv), iv + suf, cov))
    L = pd.concat(parts, ignore_index=True)
    L["coverage_all"] = np.where(L["share_formed"] > 0, L["coverage"].fillna(0) * L["share_formed"], 0.0)
    return L


def ratios(L, pa):
    """per-gene width ratios to D0 classical and to D2 rej_t at p_a pa, for rows valid at that p_a."""
    x = L[L["p_a"].isna() | np.isclose(L["p_a"], pa)].copy()
    d0 = L[L["design"] == "D0_classical"][KEY + ["width"]].rename(columns={"width": "w_D0"})
    rj = L[(L["design"] == "D2_rej_t") & np.isclose(L["p_a"], pa)][KEY + ["width"]].rename(columns={"width": "w_rej"})
    x = x.merge(d0, on=KEY, how="left").merge(rj, on=KEY, how="left")
    x["wr_D0cl"] = x["width"] / x["w_D0"]
    x["wr_rej"] = x["width"] / x["w_rej"]
    return x


def per_cell(x):
    return x.groupby(CELL + ["design"]).agg(coverage_all=("coverage_all", "median"), coverage=("coverage", "median"),
                                            share_formed=("share_formed", "median"),
                                            share_formed_min=("share_formed", "min"),
                                            wr_D0cl=("wr_D0cl", "median"), wr_rej=("wr_rej", "median")).reset_index()


def table(L, support, arms, designs, balance_support="own"):
    out = []
    for pa in (0.1, 0.01):
        x = ratios(L[L["arm"].isin(arms) & L["design"].isin(designs)], pa)
        c = per_cell(x)
        sup = support[(support["balance"] == balance_support) & np.isclose(support["p_a"], pa)][CELL + ["support"]]
        c = c.merge(sup, on=CELL, how="left")
        c = c[c["support"] >= 1000]
        full = c.groupby(CELL)["design"].nunique()
        keep = full[full == len(designs)].index
        c = c.set_index(CELL).loc[keep].reset_index() if len(keep) else c.iloc[0:0]
        c["domain"] = np.where(c["vtag"].isin(CENSUS), "census", "tissue")
        c["p_a"] = pa
        out.append(c)
    return pd.concat(out, ignore_index=True)


def agg(c, by):
    g = c.groupby(by)
    r = g.agg(n_cells=("vtag", "size"), coverage_all=("coverage_all", "median"), coverage_all_min=("coverage_all", "min"),
              coverage=("coverage", "median"), share_formed=("share_formed", "median"),
              share_formed_min=("share_formed_min", "min"), wr_D0cl=("wr_D0cl", "median"), wr_rej=("wr_rej", "median"))
    return r.reset_index()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/work/users/w/e/weiyang/hest_replication")
    a = ap.parse_args()
    L = load(a.root)
    L.to_csv("s5_genes_long.csv.gz", index=False, float_format="%.8g")
    diag = pd.read_csv(os.path.join(a.root, "results/round7/ppi/S1_weighting/_merged/s1_masking_diag.csv"))
    support = diag[diag["part"] == "D2"][CELL + ["balance", "p_a", "support"]]
    N = Numbers()
    # 1. matched informative cells, memo section 2
    m = table(L, support, INFORMATIVE, MATCHED)
    mt = agg(m, ["domain", "n_L", "p_a", "design"])
    mt.to_csv("s5_matched.csv", index=False, float_format="%.10g")
    m.to_csv("s5_matched_cells.csv", index=False, float_format="%.10g")
    for _, r in mt.iterrows():
        tg = f"{r['domain']}|nL{r['n_L']}|pa{r['p_a']}|{r['design']}"
        for k in ("n_cells", "coverage_all", "coverage", "share_formed_min", "wr_D0cl", "wr_rej"):
            N.add(f"S5m_{k}|{tg}", r[k], "s5_matched.csv")
    # 2. bh_t and bh_t_n2 against the tuned interval, D0 only, both targets
    out = []
    for target, des, ref in (("design", ["D0_classical", "D0_tuned", "D0_tuned_xf", "bh", "bh_t", "bh_t_n2", "kluger_uniform", "kluger_score"], "D0_classical"),
                             ("super", ["D0_classical_r5super_super", "D0_tuned_r5super_super", "bh_super", "bh_t_super", "bh_t_n2_super",
                                        "kluger_uniform_super", "kluger_score_super"], "D0_classical_S2_super")):
        x = L[L["arm"].isin(INFORMATIVE) & L["design"].isin(des + [ref])].copy()
        w0 = x[x["design"] == ref][KEY + ["width"]].rename(columns={"width": "w_ref"})
        x = x[x["design"].isin(des)].merge(w0, on=KEY, how="left")
        x["wr_D0cl"] = x["width"] / x["w_ref"]; x["wr_rej"] = np.nan
        c = per_cell(x)
        full = c.groupby(CELL)["design"].nunique()
        keep = full[full == len(des)].index
        c = c.set_index(CELL).loc[keep].reset_index()
        c["domain"] = np.where(c["vtag"].isin(CENSUS), "census", "tissue")
        c["target"] = target
        out.append(c)
    bt = pd.concat(out, ignore_index=True)
    btt = agg(bt, ["target", "domain", "n_L", "design"])
    btt.to_csv("s5_bh_vs_tuned.csv", index=False, float_format="%.10g")
    for _, r in btt.iterrows():
        tg = f"{r['target']}|{r['domain']}|nL{r['n_L']}|{r['design']}"
        for k in ("n_cells", "coverage_all", "coverage", "share_formed_min", "wr_D0cl"):
            N.add(f"S5bt_{k}|{tg}", r[k], "s5_bh_vs_tuned.csv")
    # 3. controls
    cc = table(L, support, CONTROLS, MATCHED)
    cc["group"] = cc["arm"]
    pc = table(L, support, INFORMATIVE, ["D0_classical", "D2pc_rej_t"], balance_support="perm_cluster")
    pc["group"] = "perm_cluster_balance"
    ct = agg(pd.concat([cc, pc], ignore_index=True), ["group", "domain", "n_L", "p_a", "design"])
    ct.to_csv("s5_controls.csv", index=False, float_format="%.10g")
    for _, r in ct.iterrows():
        tg = f"{r['group']}|{r['domain']}|nL{r['n_L']}|pa{r['p_a']}|{r['design']}"
        for k in ("n_cells", "coverage_all", "wr_D0cl", "wr_rej"):
            N.add(f"S5c_{k}|{tg}", r[k], "s5_controls.csv")
    # 4. cube widths and residuals, informative cells, no support restriction
    cub = ["cube_S3", "cube_S3_HT", "cube_S3_u2", "cube_S4b", "cube_S4b_n2", "cube_S4b_HT"]
    x = ratios(L[L["arm"].isin(INFORMATIVE) & L["design"].isin(cub + ["D0_classical"])], 0.01)
    x = x[x["design"].isin(cub)]
    c = per_cell(x)
    c["domain"] = np.where(c["vtag"].isin(CENSUS), "census", "tissue")
    cw = agg(c, ["domain", "n_L", "design"])
    d3 = pd.read_csv(os.path.join(a.root, "results/round7/ppi/S3_adaptive/_merged_r2/s3_masking_diag.csv"))
    d4 = pd.read_csv(os.path.join(a.root, "results/round7/ppi/S4b_cube_constant/_merged/s4b_masking_diag.csv"))
    res = []
    for dd, des, col_f, col_n in ((d3[d3["design"] == "cube_u1"], "cube_S3", "resid_median_eval", None),
                                  (d3[d3["design"] == "cube_u2"], "cube_S3_u2", "resid_median_eval", None),
                                  (d4, "cube_S4b", "resid_f_median", "resid_N_median")):
        dd = dd[dd["arm"].isin(INFORMATIVE)].copy()
        dd["domain"] = np.where(dd["vtag"].isin(CENSUS), "census", "tissue")
        for (dom, nL), y in dd.groupby(["domain", "n_L"]):
            res.append(dict(domain=dom, n_L=nL, design=des, resid_f_median=float(y[col_f].median()),
                            resid_N_median=float(y[col_n].median()) if col_n else np.nan))
    cw = cw.merge(pd.DataFrame(res), on=["domain", "n_L", "design"], how="left")
    cw.to_csv("s5_cube_widths.csv", index=False, float_format="%.10g")
    for _, r in cw.iterrows():
        tg = f"{r['domain']}|nL{r['n_L']}|{r['design']}"
        for k in ("n_cells", "wr_D0cl", "coverage_all", "resid_f_median", "resid_N_median"):
            N.add(f"S5w_{k}|{tg}", r[k], "s5_cube_widths.csv")
    N.add("S5_gene_rows", len(L), "s5_genes_long.csv.gz")
    N.write("s5_report_numbers.csv")
    print(len(L), len(mt), len(btt), len(ct), len(cw))


if __name__ == "__main__":
    main()
