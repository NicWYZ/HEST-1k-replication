"""Round 7 inference track, S2b items 2 and 3: merged tables, anchor checks and pooled numbers (S2 memo, section 5).

Item 2 (--pop-dir). Reads s1_sim__<tag>.csv and s1_sim_pop__<tag>.csv of the rerun cell. Anchor: every cell row of the
rerun equals the S1 row of the same cell in --s1-sim. Then, per p_a and R^2 and over the whole cell, the populations in
which each estimator has a standardised bias above 3, and how many of them have a smallest pi_hat below 0.01 n_L/G
(prediction S2b.2) or equal to 0.
Item 3 (--bh-dir). Merges every s2bm_cells__*.csv and s2b_sim__*.csv under it into s2b3_masking_grid.csv and
s2b3_sim.csv. Anchor: the published interval's rows equal S2's rows of the same cells in --s2-merged. Then the pooled
coverage of bh, bh_t, bh_t_n2 and bh_t_fpc by set, target and n_L, the per-task tests of predictions S2b.3 and S2b.4,
and the measured ratio of estimated to empirical variance against rho_BH.
Writes s2b2_numbers.csv, s2b3_numbers.csv and s2b_prediction_scores.csv in the working directory.
"""
import argparse
import glob
import os

import numpy as np
import pandas as pd

TISSUE = ("CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM")
CENSUS = ("ACS_STATES", "ACS_CA_PUMA")
VARIANTS = ("bh", "bh_t", "bh_t_n2", "bh_t_fpc")


def verdict(ok_all, ok_part):
    return "held" if ok_all else ("partly held" if ok_part else "refuted")


def item2(a, scores):
    num = []
    add = lambda n, v, src, note="": num.append(dict(name=n, value=v, source=src, note=note))
    cf = glob.glob(os.path.join(a.pop_dir, "s1_sim__*.csv"))[0]
    pf = glob.glob(os.path.join(a.pop_dir, "s1_sim_pop__*.csv"))[0]
    new = pd.read_csv(cf); pop = pd.read_csv(pf)
    old = pd.read_csv(a.s1_sim)
    k = ["G", "n_L", "R2", "lambda_star", "law", "k", "design", "p_a", "estimator", "variance", "ref"]
    oo = old.merge(new[k], on=k)
    j = oo.merge(new, on=k, suffixes=("_s1", "_re"))
    cols = ["coverage_mean", "width_mean", "bias_over_sd_rms_corrected", "share_pop_bias_z_gt3"]
    add("anchor_rows", len(j), cf, f"of {len(new)} rerun rows")
    for c in cols:
        add(f"anchor_max_abs_diff|{c}", float(np.nanmax(np.abs(j[c + "_s1"] - j[c + "_re"]))), cf)
    thr = 0.01
    for e_ in ("HT", "H", "classical"):
        x = pop[pop["estimator"] == e_]
        b = x["bias_z"].abs() > 3
        add(f"pops|{e_}", len(x), pf)
        add(f"pops_bias_z_gt3|{e_}", int(b.sum()), pf)
        add(f"pops_bias_z_gt3_pi_lt_0.01|{e_}", int((b & (x["pi_ratio_min"] < thr)).sum()), pf)
        add(f"pops_bias_z_gt3_pi_zero|{e_}", int((b & (x["n_clusters_pi_zero"] > 0)).sum()), pf)
        add(f"pops_pi_lt_0.01|{e_}", int((x["pi_ratio_min"] < thr).sum()), pf)
        add(f"pops_pi_lt_0.01_bias_z_gt3|{e_}", int(((x["pi_ratio_min"] < thr) & b).sum()), pf)
        add(f"pops_bias_z_gt3_positive_bias|{e_}", int((b & (x["bias"] > 0)).sum()), pf)
        share = float((x.loc[b, "pi_ratio_min"] < thr).mean()) if b.any() else np.nan
        add(f"share_biased_with_pi_lt_0.01|{e_}", share, pf)
        for (pa_, R2), y in x.groupby(["p_a", "R2"]):
            bb = y["bias_z"].abs() > 3
            add(f"cell_pops_bias_z_gt3|{e_}|pa{pa_}|R2{R2}", int(bb.sum()), pf, f"of {len(y)}")
            add(f"cell_pops_bias_z_gt3_pi_lt_0.01|{e_}|pa{pa_}|R2{R2}", int((bb & (y["pi_ratio_min"] < thr)).sum()), pf)
            add(f"cell_pops_pi_lt_0.01|{e_}|pa{pa_}|R2{R2}", int((y["pi_ratio_min"] < thr).sum()), pf)
            add(f"cell_median_abs_bias_z|{e_}|pa{pa_}|R2{R2}", float(y["bias_z"].abs().median()), pf)
        if e_ == "HT":
            scores.append(dict(prediction="S2b.2", verdict=("held" if share >= 0.9 else "refuted") if b.any() else "not tested",
                               summary=f"{int(b.sum())} populations with |z| > 3 for HT; share with smallest pi_hat below 0.01 n_L/G {share:.3f}"))
    pd.DataFrame(num).to_csv("s2b2_numbers.csv", index=False, float_format="%.10g")


def item3(a, scores):
    num = []
    add = lambda n, v, src, note="": num.append(dict(name=n, value=v, source=src, note=note))
    m = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(a.bh_dir, "*", "s2bm_cells__*.csv"))], ignore_index=True)
    s = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(a.bh_dir, "sim", "*", "s2b_sim__*.csv"))], ignore_index=True)
    m.to_csv("s2b3_masking_grid.csv", index=False, float_format="%.10g")
    s.to_csv("s2b3_sim.csv", index=False, float_format="%.10g")
    M, S = "s2b3_masking_grid.csv", "s2b3_sim.csv"
    # anchor against S2
    s2m = pd.read_csv(os.path.join(a.s2_merged, "s2_masking_grid.csv"))
    s2s = pd.read_csv(os.path.join(a.s2_merged, "s2_sim.csv"))
    k = ["vtag", "arm", "estimand", "n_L", "set", "design", "estimator", "interval"]
    jm = m[m["interval"] == "bh"].merge(s2m[s2m["interval"] == "bh"], on=k, suffixes=("", "_s2"))
    add("anchor_masking_rows", len(jm), M, f"of {int((m['interval'] == 'bh').sum())} bh rows")
    for c in ("coverage_design_median", "coverage_super_median", "width_median"):
        if c in jm and c + "_s2" in jm:
            add(f"anchor_masking_max_abs_diff|{c}", float(np.nanmax(np.abs(jm[c] - jm[c + "_s2"]))), M)
    ks = ["G", "n_L", "R2", "lambda_star", "law", "design", "estimator", "interval"]
    js = s[s["interval"] == "bh"].merge(s2s[s2s["interval"] == "bh"], on=ks, suffixes=("", "_s2"))
    add("anchor_sim_rows", len(js), S, f"of {int((s['interval'] == 'bh').sum())} bh rows")
    for c in ("coverage_design_mean", "coverage_super_mean", "width_mean"):
        add(f"anchor_sim_max_abs_diff|{c}", float(np.nanmax(np.abs(js[c] - js[c + "_s2"]))), S)
    # pooled masking
    for (st, v), x in m.groupby(["set", "interval"]):
        for tg in (("design",) if st == "A_fixed" else ("design", "super")):
            col = f"coverage_{tg}_median"
            for nl, y in x.groupby("n_L"):
                add(f"cov_median|{st}|{v}|{tg}|nL{nl}", float(y[col].median()), M)
                add(f"cov_min|{st}|{v}|{tg}|nL{nl}", float(y[col].min()), M)
                if tg == "design":
                    add(f"share_formed_min|{st}|{v}|nL{nl}", float(y["share_formed_median"].min()), M)
                for t in TISSUE + CENSUS:
                    yt = y[y["vtag"] == t]
                    if len(yt):
                        add(f"cov_task|{st}|{v}|{tg}|{t}|nL{nl}", float(yt[col].median()), M, "median over arms and estimands")
        add(f"est_over_emp_median|{st}|{v}", float(x["est_over_emp_median"].median()), M)
    # S2b.3: A_fixed, design, bh_t, every n_L, every tissue task >= 0.85
    x = m[(m["set"] == "A_fixed") & (m["interval"] == "bh_t") & (m["vtag"].isin(TISSUE))]
    t3 = x.groupby(["vtag", "n_L"])["coverage_design_median"].median()
    ok = t3 >= 0.85
    scores.append(dict(prediction="S2b.3", verdict=verdict(ok.all(), ok.mean() >= 0.5),
                       summary=f"{int(ok.sum())} of {len(ok)} task-by-n_L medians at 0.85 or above; range {t3.min():.3f} to {t3.max():.3f}"))
    add("S2b.3_cells", len(ok), M); add("S2b.3_cells_ge_0.85", int(ok.sum()), M)
    add("S2b.3_min", float(t3.min()), M); add("S2b.3_max", float(t3.max()), M)
    # S2b.4: B_world, super, bh_t, n_L = 4, every task >= 0.80
    x = m[(m["set"] == "B_world") & (m["interval"] == "bh_t") & (m["n_L"] == 4)]
    t4 = x.groupby("vtag")["coverage_super_median"].median()
    ok4 = t4 >= 0.80
    scores.append(dict(prediction="S2b.4", verdict=verdict(ok4.all(), ok4.mean() >= 0.5),
                       summary="; ".join(f"{kk} {vv:.3f}" for kk, vv in t4.items()) + f"; tasks at 0.80 or above: {int(ok4.sum())} of {len(ok4)}"))
    for kk, vv in t4.items():
        add(f"S2b.4|{kk}", float(vv), M)
    # rho_BH against the measured ratio, published interval, design target (set A, and simulation)
    xa = m[(m["set"] == "A_fixed") & (m["interval"] == "bh")].copy()
    xa["meas_over_rho"] = xa["est_over_emp_median"] / xa["rho_bh_median"]
    for nl, y in xa.groupby("n_L"):
        add(f"rho|A_fixed|nL{nl}|rho_median", float(y["rho_bh_median"].median()), M)
        add(f"rho|A_fixed|nL{nl}|measured_median", float(y["est_over_emp_median"].median()), M)
        add(f"rho|A_fixed|nL{nl}|measured_over_rho_median", float(y["meas_over_rho"].median()), M)
    add("rho|A_fixed|spearman_measured_vs_rho", float(xa[["est_over_emp_median", "rho_bh_median"]].corr("spearman").iloc[0, 1]), M)
    xs = s[(s["design"] == "D0") & (s["interval"] == "bh")].copy()
    xs["meas_over_rho"] = xs["est_over_emp_mean"] / xs["rho_bh_mean"]
    for (G, nl), y in xs.groupby(["G", "n_L"]):
        add(f"rho|sim|G{G}|nL{nl}|measured_over_rho_median", float(y["meas_over_rho"].median()), S)
    for (v, G, nl), y in s[s["design"] == "D0"].groupby(["interval", "G", "n_L"]):
        for tg in ("design", "super"):
            add(f"sim_cov_mean|{v}|{tg}|G{G}|nL{nl}", float(y[f"coverage_{tg}_mean"].mean()), S)
            add(f"sim_cov_min|{v}|{tg}|G{G}|nL{nl}", float(y[f"coverage_{tg}_mean"].min()), S)
    pd.DataFrame(num).to_csv("s2b3_numbers.csv", index=False, float_format="%.10g")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop-dir"); ap.add_argument("--s1-sim")
    ap.add_argument("--bh-dir"); ap.add_argument("--s2-merged")
    a = ap.parse_args()
    scores = []
    if a.pop_dir:
        item2(a, scores)
    if a.bh_dir:
        item3(a, scores)
    pd.DataFrame(scores).to_csv("s2b_prediction_scores.csv", index=False)
    print(scores)


if __name__ == "__main__":
    main()
