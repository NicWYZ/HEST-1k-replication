"""Round 7 inference track, interval i02: merge the S3 or S4 unit fragments and compute the report numbers.

--stage S3 reads results/round7/ppi/S3_adaptive/<task>/<arm>_nL<n>/ and .../sim/<tag>/ under --root, checks every
unit directory's stamp against results/round7/ppi/S3_adaptive/s3_assigned_frame_ids.csv in --clone (as
round7_ppi_merge.stamps), and writes in the working directory s3_stamp_check.csv, s3_masking_grid.csv (one row per
cell and interval, with the medians over genes of the per-gene width ratios to D0 classical and to D2 own rej_t at
p_a 0.1 and 0.01 from S1, and D0 classical's coverage), s3_masking_diag.csv, s3_skipped.csv, s3_sim.csv (with the
same ratios from S1's merged simulation table) and s3_report_numbers.csv (predictions S3.1 to S3.5).
--stage S4 does the same for results/round7/ppi/S4_kcenter/ and writes s4_stamp_check.csv, s4_grid.csv (k-center
cells with the D0 and D2 own comparators of S1 beside them), s4_diag.csv, s4_pi.csv and s4_report_numbers.csv
(S4.1, S4.2).
"""
import argparse
import glob
import os

import numpy as np
import pandas as pd

from round7_ppi_merge import stamps

LIN = "textbook_t|fpc|lin"
NOM = 0.90


class Numbers:
    def __init__(self):
        self.rows = []

    def add(self, name, value, source, note=""):
        self.rows.append(dict(name=name, value=value, source=source, note=note))

    def write(self, path):
        pd.DataFrame(self.rows).to_csv(path, index=False, float_format="%.10g")


def read_all(dirs, pat, gz=False):
    fs = [f for d in dirs for f in glob.glob(os.path.join(d, pat))]
    fs = [f for f in fs if os.path.getsize(f) > 2]
    if not fs:
        return pd.DataFrame()
    return pd.concat([pd.read_csv(f, low_memory=False) for f in fs], ignore_index=True)


def s1_genes(root, tasks):
    """S1's per-gene D0 classical and D2 own rows (rej_t and Hajek sim res)."""
    base = os.path.join(root, "results/round7/ppi/S1_weighting")
    out = []
    for t in tasks:
        for f in sorted(glob.glob(os.path.join(base, t, "*", "s1m_genes__*.csv.gz"))):
            g = pd.read_csv(f, low_memory=False)
            keep = ((g["design"] == "D0") & (g["estimator"] == "classical") & (g["variance"] == LIN)) | \
                   ((g["design"] == "D2") & (g["balance"] == "own") &
                    (((g["estimator"] == "classical") & (g["variance"].isin([LIN, "rej_t"]))) |
                     ((g["estimator"].isin(["H", "HT"])) & (g["variance"] == "sim") & (g["ref"] == "res"))))
            out.append(g[keep])
    g = pd.concat(out, ignore_index=True)
    g["coverage_all"] = np.where(g["share_formed"] > 0, g["coverage"].fillna(0) * g["share_formed"], 0.0)
    return g


def comparators(g1):
    key = ["vtag", "arm", "estimand", "n_L", "gene"]
    d0 = g1[(g1["design"] == "D0")][key + ["width", "coverage", "coverage_all", "emp_var"]].rename(
        columns={"width": "width_D0cl", "coverage": "coverage_D0cl", "coverage_all": "coverage_all_D0cl", "emp_var": "emp_var_D0cl"})
    out = d0
    for pa_ in (0.1, 0.01):
        r = g1[(g1["design"] == "D2") & (g1["variance"] == "rej_t") & (np.isclose(g1["p_a"], pa_))][key + ["width", "coverage"]]
        out = out.merge(r.rename(columns={"width": f"width_D2rej_pa{pa_}", "coverage": f"coverage_D2rej_pa{pa_}"}), on=key, how="left")
        c = g1[(g1["design"] == "D2") & (g1["variance"] == LIN) & (np.isclose(g1["p_a"], pa_))][key + ["coverage", "emp_var"]]
        out = out.merge(c.rename(columns={"coverage": f"coverage_D2cl_pa{pa_}", "emp_var": f"emp_var_D2cl_pa{pa_}"}), on=key, how="left")
    return out


def run_s3(a):
    sd = "S3_adaptive"
    base = os.path.join(a.root, "results/round7/ppi", sd)
    asg = pd.read_csv(os.path.join(a.clone, "results/round7/ppi", sd, "s3_assigned_frame_ids.csv"))
    assigned = dict(zip(asg["unit"], asg["frame_id"]))
    tasks = [t for t in assigned if t != "sim"]
    st, dirs = stamps(base, assigned, tasks + ["sim"])
    st.to_csv("s3_stamp_check.csv", index=False)
    mdirs = [d for d in dirs if "/sim/" not in d]
    sdirs = [d for d in dirs if "/sim/" in d]
    cells = read_all(mdirs, "s3m_cells__*.csv")
    genes = read_all(mdirs, "s3m_genes__*.csv.gz")
    diag = read_all(mdirs, "s3m_diag__*.csv")
    diag.to_csv("s3_masking_diag.csv", index=False, float_format="%.10g")
    read_all(mdirs, "s3m_skipped__*.csv").to_csv("s3_skipped.csv", index=False)
    comp = comparators(s1_genes(a.root, tasks))
    key = ["vtag", "arm", "estimand", "n_L", "gene"]
    g = genes.merge(comp, on=key, how="left")
    g["wr_D0cl"] = g["width"] / g["width_D0cl"]
    for pa_ in (0.1, 0.01):
        g[f"wr_D2rej_pa{pa_}"] = g["width"] / g[f"width_D2rej_pa{pa_}"]
    ck = ["vtag", "arm", "estimand", "n_L", "design", "p_a", "estimator", "variance", "ref"]
    agg = g.groupby(ck, dropna=False).agg(
        wr_D0cl_median=("wr_D0cl", "median"), wr_D2rej_pa01_median=("wr_D2rej_pa0.1", "median"),
        wr_D2rej_pa001_median=("wr_D2rej_pa0.01", "median"), coverage_D0cl_median=("coverage_D0cl", "median"),
        coverage_all_D0cl_median=("coverage_all_D0cl", "median"),
        coverage_D2rej_pa01_median=("coverage_D2rej_pa0.1", "median"),
        coverage_D2rej_pa001_median=("coverage_D2rej_pa0.01", "median")).reset_index()
    grid = cells.merge(agg, on=ck, how="left")
    # D2 own support from S1, for the mixture's "supported" cells
    d1 = pd.read_csv(os.path.join(a.root, "results/round7/ppi/S1_weighting/_merged/s1_masking_diag.csv"))
    d1 = d1[(d1["part"] == "D2") & (d1["balance"] == "own")][["vtag", "arm", "estimand", "n_L", "p_a", "support"]]
    grid = grid.merge(d1, on=["vtag", "arm", "estimand", "n_L", "p_a"], how="left")
    grid.to_csv("s3_masking_grid.csv", index=False, float_format="%.10g")
    sim = read_all(sdirs, "s3_sim__*.csv")
    if len(sim):
        s1s = pd.read_csv(os.path.join(a.root, "results/round7/ppi/S1_weighting/_merged/s1_sim.csv"))
        s1s = s1s[s1s["k"] == 1]
        sk = ["G", "n_L", "R2", "lambda_star", "law"]
        d0 = s1s[(s1s["design"] == "D0") & (s1s["estimator"] == "classical") & (s1s["variance"] == LIN)][sk + ["width_mean", "coverage_mean"]]
        sim = sim.merge(d0.rename(columns={"width_mean": "width_D0cl", "coverage_mean": "coverage_D0cl"}), on=sk, how="left")
        for pa_ in (0.1, 0.01):
            r = s1s[(s1s["design"] == "D2") & (s1s["variance"] == "rej_t") & np.isclose(s1s["p_a"], pa_)][sk + ["width_mean", "coverage_mean"]]
            sim = sim.merge(r.rename(columns={"width_mean": f"width_D2rej_pa{pa_}", "coverage_mean": f"coverage_D2rej_pa{pa_}"}), on=sk, how="left")
            sim[f"wr_D2rej_pa{pa_}"] = sim["width_mean"] / sim[f"width_D2rej_pa{pa_}"]
        sim["wr_D0cl"] = sim["width_mean"] / sim["width_D0cl"]
    sim.to_csv("s3_sim.csv", index=False, float_format="%.10g")
    # ---------------- numbers
    N = Numbers()
    SG, SS, SD = "s3_masking_grid.csv", "s3_sim.csv", "s3_masking_diag.csv"
    N.add("S3_stamp_dirs", len(st), "s3_stamp_check.csv"); N.add("S3_stamp_merged", int(st["merged"].sum()), "s3_stamp_check.csv")
    N.add("S3_masking_cells", len(diag), SD); N.add("S3_sim_rows", len(sim), SS)
    # S3.1
    for pa_, col in ((0.1, "wr_D2rej_pa01_median"), (0.01, "wr_D2rej_pa001_median")):
        for var in ("res", "sim", "apx_size"):
            x = grid[(grid["vtag"] == "CCRCC") & (grid["arm"] == "uni_v2") & (grid["estimand"] == "theta3") & (grid["n_L"] == 8)
                     & (grid["design"] == "cube_u1") & (grid["estimator"] == "H") & (grid["variance"] == var)]
            N.add(f"S3.1_wr_D2rej|pa{pa_}|H_{var}", float(x[col].iloc[0]) if len(x) else np.nan, SG,
                  "CCRCC uni_v2 theta3 nL8 cube_u1, median over genes of the per-gene width ratio")
    # S3.2
    for var in ("res", "sim", "apx_size"):
        x = sim[(sim["design"] == "cube_u1") & (sim["estimator"] == "H") & (sim["variance"] == var) & (sim["n_L"] >= 8)]
        for cname in ("coverage_mean", "coverage_all_mean"):
            N.add(f"S3.2_n_cells|H_{var}|{cname}", len(x), SS)
            N.add(f"S3.2_share_within_0.03|H_{var}|{cname}", float((np.abs(x[cname] - NOM) <= 0.03).mean()), SS)
            N.add(f"S3.2_min|H_{var}|{cname}", float(x[cname].min()), SS)
            N.add(f"S3.2_max|H_{var}|{cname}", float(x[cname].max()), SS)
        for law in ("n", "s"):
            y = x[x["law"] == law]
            N.add(f"S3.2_share_within_0.03|H_{var}|law_{law}", float((np.abs(y["coverage_mean"] - NOM) <= 0.03).mean()), SS)
    # S3.3
    pm = pd.concat([diag[["design", "pi_hat_ratio_min_min"]].assign(src="masking"),
                    sim.drop_duplicates(["design", "p_a", "G", "n_L", "R2", "lambda_star", "law"])[["design", "pi_hat_ratio_min_min"]].assign(src="sim")])
    for (des, src), x in pm.groupby(["design", "src"]):
        N.add(f"S3.3_min_pi_hat_ratio|{des}|{src}", float(x["pi_hat_ratio_min_min"].min()), SD if src == "masking" else SS)
        N.add(f"S3.3_share_cells_ge_0.45|{des}|{src}", float((x["pi_hat_ratio_min_min"] >= 0.45).mean()), SD if src == "masking" else SS)
    N.add("S3.3_min_pi_hat_ratio_all", float(pm["pi_hat_ratio_min_min"].min()), SD + "; " + SS)
    for des in ("cube_u1", "cube_u2"):
        x = diag[diag["design"] == des]
        N.add(f"S3_share_pairs_pgh_zero_max|{des}", float(x["share_pairs_pgh_zero"].max()), SD)
        N.add(f"S3_landing_resid_median_median|{des}", float(x["resid_median_eval"].median()), SD)
    x = diag[diag["design"] == "mix_D2D0"]
    N.add("S3_share_pairs_pgh_zero_max|mix_D2D0", float(x["mix_share_pairs_pgh_zero"].max()), SD)
    # S3.4 (cells: every cube cell; D0 classical from S1)
    for des in ("cube_u1", "cube_u2", "mix_D2D0"):
        for var in ("res", "sim", "apx_size"):
            x = grid[(grid["design"] == des) & (grid["estimator"] == "H") & (grid["variance"] == var)]
            if des == "mix_D2D0":
                x = x[x["support"] >= 1000]
            for cov, ref in (("coverage_median", "coverage_D0cl_median"), ("coverage_all_median", "coverage_all_D0cl_median")):
                N.add(f"S3.4_share_within_0.03_of_D0cl|{des}|H_{var}|{cov}", float((np.abs(x[cov] - x[ref]) <= 0.03).mean()), SG,
                      f"{len(x)} cells" + ("; mixture cells with D2 own support >= 1000" if des == "mix_D2D0" else ""))
            N.add(f"S3.4_n_cells|{des}|H_{var}", len(x), SG)
            N.add(f"S3.4_coverage_median_over_cells|{des}|H_{var}", float(x["coverage_median"].median()), SG)
            N.add(f"S3.4_wr_D0cl_median_over_cells|{des}|H_{var}", float(x["wr_D0cl_median"].median()), SG)
            N.add(f"S3.4_share_below_0.80|{des}|H_{var}", float((x["coverage_median"] < 0.80).mean()), SG)
    # S3.5
    ky = ["vtag", "arm", "estimand", "n_L"]
    cu = grid[(grid["design"] == "cube_u1") & (grid["estimator"] == "H") & (grid["n_L"] == 8)]
    mx = grid[(grid["design"] == "mix_D2D0") & (grid["estimator"] == "H") & (grid["n_L"] == 8) & (grid["support"] >= 1000)]
    for vc, vm in (("res", "sim"), ("sim", "sim"), ("res", "res"), ("apx_size", "apx_size")):
        j = cu[cu["variance"] == vc][ky + ["width_median"]].merge(
            mx[mx["variance"] == vm][ky + ["p_a", "width_median"]], on=ky, suffixes=("_cube", "_mix"))
        for pa_ in (0.1, 0.01):
            jj = j[np.isclose(j["p_a"], pa_)]
            N.add(f"S3.5_share_cube_narrower|cube_H_{vc}|mix_H_{vm}|pa{pa_}", float((jj["width_median_cube"] < jj["width_median_mix"]).mean()), SG,
                  f"{len(jj)} supported cells at nL 8")
            N.add(f"S3.5_width_ratio_median|cube_H_{vc}|mix_H_{vm}|pa{pa_}", float((jj["width_median_cube"] / jj["width_median_mix"]).median()), SG)
    # further aggregates quoted in the S4 report
    for des in ("cube_u1", "cube_u2", "mix_D2D0"):
        for var in ("res", "sim", "apx_size"):
            x = grid[(grid["design"] == des) & (grid["estimator"] == "H") & (grid["variance"] == var)]
            N.add(f"S3m_est_over_emp_median_over_cells|{des}|H_{var}", float(x["est_over_emp_median"].median()), SG)
            for est in ("theta3", "theta2"):
                y = x[x["estimand"] == est]
                N.add(f"S3m_share_formed_min|{des}|H_{var}|{est}", float(y["share_formed_min"].min()), SG)
    if len(sim):
        y = sim[(sim["estimator"] == "H") & (sim["n_L"] >= 8)]
        for (des, pa_, var, law), x in y.groupby(["design", "p_a", "variance", "law"], dropna=False):
            tag = f"{des}|pa{pa_}|H_{var}|law_{law}"
            N.add(f"S3s_coverage_min|{tag}", float(x["coverage_mean"].min()), SS, "n_L >= 8, over cells")
            N.add(f"S3s_coverage_median|{tag}", float(x["coverage_mean"].median()), SS, "n_L >= 8, over cells")
            N.add(f"S3s_coverage_max|{tag}", float(x["coverage_mean"].max()), SS, "n_L >= 8, over cells")
            N.add(f"S3s_est_over_emp_median|{tag}", float(x["est_over_emp_mean"].median()), SS, "n_L >= 8, over cells")
            for G, xg in x.groupby("G"):
                N.add(f"S3s_coverage_median|{tag}|G{G}", float(xg["coverage_mean"].median()), SS, "n_L >= 8, over cells")
    N.write("s3_report_numbers.csv")
    print(len(st), int(st["merged"].sum()), len(cells), len(sim))


def run_s4(a):
    sd = "S4_kcenter"
    base = os.path.join(a.root, "results/round7/ppi", sd)
    asg = pd.read_csv(os.path.join(a.clone, "results/round7/ppi", sd, "s4_assigned_frame_ids.csv"))
    assigned = dict(zip(asg["unit"], asg["frame_id"]))
    tasks = list(assigned)
    st, dirs = stamps(base, assigned, tasks)
    st.to_csv("s4_stamp_check.csv", index=False)
    cells = read_all(dirs, "s4_cells__*.csv"); genes = read_all(dirs, "s4_genes__*.csv.gz")
    diag = read_all(dirs, "s4_diag__*.csv"); diag.to_csv("s4_diag.csv", index=False, float_format="%.10g")
    read_all(dirs, "s4_pi__*.csv").to_csv("s4_pi.csv", index=False, float_format="%.10g")
    read_all(dirs, "s4_skipped__*.csv").to_csv("s4_skipped.csv", index=False)
    comp = comparators(s1_genes(a.root, tasks))
    key = ["vtag", "arm", "estimand", "n_L", "gene"]
    g = genes.merge(comp, on=key, how="left")
    g["sd_ratio_D0cl"] = g["exact_sd"] / np.sqrt(g["emp_var_D0cl"])
    for pa_ in (0.1, 0.01):
        g[f"sd_ratio_D2cl_pa{pa_}"] = g["exact_sd"] / np.sqrt(g[f"emp_var_D2cl_pa{pa_}"])
    ck = ["vtag", "arm", "estimand", "n_L", "estimator", "variance", "ref"]
    agg = g.groupby(ck, dropna=False).agg(
        sd_ratio_D0cl_median=("sd_ratio_D0cl", "median"), sd_ratio_D2cl_pa01_median=("sd_ratio_D2cl_pa0.1", "median"),
        sd_ratio_D2cl_pa001_median=("sd_ratio_D2cl_pa0.01", "median"),
        sd_D0cl_median=("emp_var_D0cl", lambda v: float(np.nanmedian(np.sqrt(v)))),
        coverage_D0cl_median=("coverage_D0cl", "median"), coverage_all_D0cl_median=("coverage_all_D0cl", "median"),
        coverage_D2cl_pa01_median=("coverage_D2cl_pa0.1", "median"), coverage_D2cl_pa001_median=("coverage_D2cl_pa0.01", "median"),
        coverage_D2rej_pa01_median=("coverage_D2rej_pa0.1", "median"),
        coverage_D2rej_pa001_median=("coverage_D2rej_pa0.01", "median")).reset_index()
    grid = cells.merge(agg, on=ck, how="left").merge(
        diag[["vtag", "arm", "estimand", "n_L", "n_distinct_samples", "pi_ratio_min", "pi_ratio_max", "share_pairs_pgh_zero"]],
        on=["vtag", "arm", "estimand", "n_L"], how="left")
    grid.to_csv("s4_grid.csv", index=False, float_format="%.10g")
    N = Numbers(); SG = "s4_grid.csv"
    N.add("S4_stamp_dirs", len(st), "s4_stamp_check.csv"); N.add("S4_stamp_merged", int(st["merged"].sum()), "s4_stamp_check.csv")
    N.add("S4_cells", len(diag), "s4_diag.csv")
    for nL in sorted(diag["n_L"].unique()):
        x = diag[diag["n_L"] == nL]
        N.add(f"S4_share_pairs_pgh_zero_median|nL{nL}", float(x["share_pairs_pgh_zero"].median()), "s4_diag.csv")
        N.add(f"S4_share_pairs_pgh_zero_range|nL{nL}", f"{x['share_pairs_pgh_zero'].min():.4f} to {x['share_pairs_pgh_zero'].max():.4f}", "s4_diag.csv")
        N.add(f"S4_n_distinct_median|nL{nL}", float(x["n_distinct_samples"].median()), "s4_diag.csv")
    for est in ("theta3", "theta2"):
        cl = grid[(grid["estimator"] == "classical") & (grid["n_L"] == 8) & (grid["estimand"] == est)]
        for t, x in cl.groupby("vtag"):
            N.add(f"S4.1_classical_coverage_median_over_arms|{est}|{t}", float(x["coverage_median"].median()), SG,
                  "median over arms of the median over genes, exact over the G starts")
            N.add(f"S4.1_classical_coverage_range_over_arms|{est}|{t}", f"{x['coverage_median'].min():.4f} to {x['coverage_median'].max():.4f}", SG)
        per = cl.groupby("vtag")["coverage_median"].median()
        N.add(f"S4.1_n_tasks_below_0.80|{est}", int((per < 0.80).sum()), SG, f"of {len(per)} tasks")
        ht = grid[(grid["estimator"] == "HT") & (grid["n_L"] == 8) & (grid["estimand"] == est)]
        for t, x in ht.groupby("vtag"):
            N.add(f"S4.2_HT_sd_over_D0cl_sd_median_over_arms|{est}|{t}", float(x["sd_ratio_D0cl_median"].median()), SG,
                  "per gene exact sd of HT over the sd of the classical mean under D0 (S1, 2,000 draws); median over genes, then over arms")
            N.add(f"S4.2_HT_sd_ratio_min_over_arms|{est}|{t}", float(x["sd_ratio_D0cl_median"].min()), SG)
        per = ht.groupby("vtag")["sd_ratio_D0cl_median"].median()
        N.add(f"S4.2_n_tasks_ratio_ge_1.5|{est}", int((per >= 1.5).sum()), SG, f"of {len(per)} tasks")
        # the selection depends only on the encoder (resnet50 for the resnet50, permuted and constant arms), and the
        # classical mean and HT do not use the predictions, so the encoder is the unit for these two estimators
        ce = cl.drop_duplicates(["vtag", "encoder"])
        pe = ce.groupby("vtag")["coverage_median"].median()
        for t, v in pe.items():
            N.add(f"S4.1_classical_coverage_median_over_encoders|{est}|{t}", float(v), SG)
        N.add(f"S4.1_n_tasks_below_0.80_over_encoders|{est}", int((pe < 0.80).sum()), SG, f"of {len(pe)} tasks")
        for _, r in ce.iterrows():
            N.add(f"S4.1_classical_coverage|{est}|{r['vtag']}|{r['encoder']}", float(r["coverage_median"]), SG)
        he = ht.drop_duplicates(["vtag", "encoder"])
        for _, r in he.iterrows():
            N.add(f"S4.2_HT_sd_over_D0cl_sd|{est}|{r['vtag']}|{r['encoder']}", float(r["sd_ratio_D0cl_median"]), SG)
        N.add(f"S4.2_n_task_encoder_cells_ge_1.5|{est}", int((he["sd_ratio_D0cl_median"] >= 1.5).sum()), SG, f"of {len(he)} task and encoder cells")
        for (estr, var), x in grid[(grid["n_L"] == 8) & (grid["estimand"] == est)].groupby(["estimator", "variance"]):
            N.add(f"S4_coverage_median_over_cells|{est}|nL8|{estr}_{var}", float(x["coverage_median"].median()), SG)
    N.write("s4_report_numbers.csv")
    print(len(st), int(st["merged"].sum()), len(cells))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("S3", "S4"), required=True)
    ap.add_argument("--root", default="/work/users/w/e/weiyang/hest_replication")
    ap.add_argument("--clone", default="/work/users/w/e/weiyang/hest_code/round7-ppi")
    a = ap.parse_args()
    run_s3(a) if a.stage == "S3" else run_s4(a)


if __name__ == "__main__":
    main()
