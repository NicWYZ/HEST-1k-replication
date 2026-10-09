"""Round 5 PPI, interval 2, stage E4: merge the six task units and the simulation, score E4.

Reads only result files under results/round5/ppi/E4_selection/ (each task's <arm>/ outputs, never
_superseded_* directories), the inclusion diagnostic, and round 4's q4a_table61.csv. Run from the
repository root: python code/scripts/round5_ppi_e4_merge.py

Writes e4_selection_grid.csv (all summary rows), e4_variance_ratios.csv (per gene ratios to the D0
classical estimator, summarised over genes), e4_acceptance.csv, e4_prediction_scores.csv,
e4_prediction_cells.csv, e4_report_numbers.csv.
"""
import glob

import numpy as np
import pandas as pd

D = "results/round5/ppi/E4_selection"
TASKS = ("CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM", "ACS_STATES", "ACS_CA_PUMA")
KIDNEY = TASKS[:3]
BASE = ("none", "textbook_t|fpc|lin")
PRIMARY = "textbook_t|fpc|lin|xf"
NUM = []


def num(name, value, source):
    NUM.append(dict(name=name, value=value, source=source))


def files(kind):
    fs = [f for f in glob.glob(f"{D}/*/*/{kind}__*") if "_superseded" not in f and "/sim/" not in f]
    return sorted(fs)


def main():
    grid = pd.concat([pd.read_csv(f) for f in files("e4_selection")], ignore_index=True)
    grid.to_csv(f"{D}/e4_selection_grid.csv", index=False)
    g = pd.concat([pd.read_csv(f) for f in files("e4_selection_genes")], ignore_index=True)
    key = ["vtag", "arm", "estimand", "n_L", "gene"]
    base = g[(g["design"] == "D0") & (g["rule"] == BASE[0]) & (g["interval"] == BASE[1])][key + ["emp_var"]]
    base = base.rename(columns={"emp_var": "ev0"})
    g = g.merge(base, on=key, how="left")
    g["ratio"] = g["emp_var"] / g["ev0"]
    grp = ["vtag", "arm", "estimand", "n_L", "design", "balance", "p_a", "rule", "interval"]
    r = (g.groupby(grp, dropna=False)
         .agg(ratio_median=("ratio", "median"), ratio_p10=("ratio", lambda x: x.quantile(0.1)),
              ratio_p90=("ratio", lambda x: x.quantile(0.9)), coverage_median=("coverage", "median"),
              n_genes=("gene", "nunique")).reset_index())
    r.to_csv(f"{D}/e4_variance_ratios.csv", index=False)
    acc = pd.concat([pd.read_csv(f).assign(source=f) for f in glob.glob(f"{D}/*/e4_unit_acceptance__*.csv")],
                    ignore_index=True, sort=False)
    acc.to_csv(f"{D}/e4_acceptance.csv", index=False)
    scores, cells = [], []

    def add(pid, verdict, text, c=None):
        if c is not None and len(c) == 0:
            verdict = "not assessed (no cells)"
        scores.append(dict(prediction=pid, verdict=verdict, summary=text))
        if c is not None and len(c):
            cells.append(c.assign(prediction=pid))
    # E4.1 from the simulation
    s = pd.read_csv(f"{D}/e4_sim.csv")
    s1 = s[(s["rule"] == "none") & (s["design"] == "D2") & (s["p_a"] == 0.01) & (s["interval"] == "textbook_t|fpc|lin")].copy()
    s1["target"] = 1 - s1["r2_fp_median"]
    s1["diff"] = s1["var_ratio_to_D0_classical_mean"] - s1["target"]
    ok = s1["diff"].abs() <= 0.05
    byg = "; ".join(f"G = {G}: {int(ok[s1['G'] == G].sum())} of {int((s1['G'] == G).sum())}" for G in sorted(s1["G"].unique()))
    add("E4.1", "held" if ok.all() else ("partly held" if ok.mean() >= 0.5 else "refuted"),
        f"simulated classical variance under D2 (p_a 0.01, balance on fbar) within 0.05 of 1 - R^2 in {int(ok.sum())} of {len(s1)} cells ({byg}); "
        f"differences {s1['diff'].min():.3f} to {s1['diff'].max():.3f}", s1)
    # E4.2 real, n_L = 8, own balance, D2 p_a 0.01, classical, against bands
    q = r[(r["n_L"] == 8) & (r["design"] == "D2") & (r["balance"] == "own") & (r["p_a"] == 0.01)
          & (r["rule"] == "none") & (r["interval"] == BASE[1])]
    t = r[(r["n_L"] == 8) & (r["design"] == "D0") & (r["rule"] == "c_crossfit_design") & (r["interval"] == "textbook_t|fpc|lin|xf")]
    bands = {("LUNG_XENIUM", None): (0.25, 0.40), ("CCRCC", "uni_v2"): (0.55, 0.70), ("ACS_STATES", "package"): (0.28, 0.40)}
    out = []
    for (vt, arm), (lo, hi) in bands.items():
        x = q[(q["vtag"] == vt) & ((q["arm"] == arm) if arm else q["arm"].isin(["hoptimus0", "uni_v2", "resnet50"]))]
        y = t[(t["vtag"] == vt) & ((t["arm"] == arm) if arm else t["arm"].isin(["hoptimus0", "uni_v2", "resnet50"]))]
        for _, row in x.iterrows():
            tt = y[(y["arm"] == row["arm"]) & (y["estimand"] == row["estimand"])]["ratio_median"]
            out.append(dict(vtag=vt, arm=row["arm"], estimand=row["estimand"], D2_own_classical=row["ratio_median"],
                            band_lo=lo, band_hi=hi, in_band=lo <= row["ratio_median"] <= hi,
                            tuned_D0=float(tt.iloc[0]) if len(tt) else np.nan))
    c2 = pd.DataFrame(out)
    th3 = c2[c2["estimand"] == "theta3"]
    add("E4.2", "held" if len(th3) and th3["in_band"].all() else ("partly held" if len(th3) and th3["in_band"].mean() >= 0.5 else "refuted"),
        "n_L = 8, theta3: " + "; ".join(f"{r_.vtag} {r_.arm} {r_.D2_own_classical:.3f} (band {r_.band_lo}-{r_.band_hi}, tuned D0 {r_.tuned_D0:.3f})"
                                         for r_ in th3.itertuples()), c2)
    # E4.3 pcF2 recovers >= half the gain on lung and < a third on kidney cancer
    out = []
    for vt in ("LUNG_XENIUM", "CCRCC"):
        for arm in ("hoptimus0", "uni_v2", "resnet50"):
            for est in ("theta3", "theta2"):
                def val(b):
                    z = r[(r["vtag"] == vt) & (r["arm"] == arm) & (r["estimand"] == est) & (r["n_L"] == 8) & (r["design"] == "D2")
                          & (r["balance"] == b) & (r["p_a"] == 0.01) & (r["rule"] == "none") & (r["interval"] == BASE[1])]["ratio_median"]
                    return float(z.iloc[0]) if len(z) else np.nan
                own, pc = val("own"), val("pcF2")
                frac = (1 - pc) / (1 - own) if own < 1 else np.nan
                out.append(dict(vtag=vt, arm=arm, estimand=est, own=own, pcF2=pc, fraction_of_gain=frac))
    c3 = pd.DataFrame(out)
    l3 = c3[(c3["vtag"] == "LUNG_XENIUM") & (c3["estimand"] == "theta3")]
    k3 = c3[(c3["vtag"] == "CCRCC") & (c3["estimand"] == "theta3")]
    ok_l, ok_k = (l3["fraction_of_gain"] >= 0.5), (k3["fraction_of_gain"] < 1 / 3)
    add("E4.3", "held" if ok_l.all() and ok_k.all() else ("partly held" if (ok_l.all() or ok_k.all()) else "refuted"),
        f"theta3, n_L = 8: lung fraction of the own-balance gain recovered by pcF2 {', '.join(f'{v:.2f}' for v in l3['fraction_of_gain'])}; "
        f"kidney cancer {', '.join(f'{v:.2f}' for v in k3['fraction_of_gain'])}", c3)
    # E4.4 real-data coverage, restricted to balance on the estimand's own fbar (plan: the predicted
    # over-coverage is a statement about balancing on a correlate of the outcome)
    cv = grid[grid["balance"].isin(["own"]) | grid["design"].isin(["D0", "D1"])].copy()
    d2c = cv[(cv["design"] == "D2") & (cv["rule"] == "none") & (cv["interval"] == BASE[1])]
    d0f = grid[(grid["design"] == "D0") & (grid["rule"] == "c_crossfit_design")][["vtag", "arm", "estimand", "n_L", "interval", "coverage_median"]]
    d2f = cv[(cv["design"] == "D2") & (cv["rule"] == "c_crossfit_design") & (cv["interval"] == PRIMARY)].merge(
        d0f, on=["vtag", "arm", "estimand", "n_L", "interval"], suffixes=("", "_D0"))
    d2f["diff"] = d2f["coverage_median"] - d2f["coverage_median_D0"]
    d1 = cv[(cv["design"] == "D1") & (cv["interval"] == "strat_t")]
    a, b_, c_ = d2c["coverage_median"] >= 0.93, d2f["diff"].abs() <= 0.02, d1["coverage_median"].between(0.88, 0.92)
    byp = "; ".join(f"p_a {pa}: {int(a[d2c['p_a'] == pa].sum())} of {int((d2c['p_a'] == pa).sum())}, median {d2c[d2c['p_a'] == pa]['coverage_median'].median():.3f}"
                    for pa in sorted(d2c["p_a"].dropna().unique()))
    part = lambda ok: "held" if ok.all() else ("partly held" if ok.mean() >= 0.5 else "refuted")
    v4 = "held" if (a.all() and b_.all() and c_.all()) else f"D2 over-coverage {part(a)}; D2 final vs D0 {part(b_)}; D1 {part(c_)}"
    add("E4.4", v4,
        f"real tasks, own balance: D2 classical coverage >= 0.93 in {int(a.sum())} of {len(a)} cells (median {d2c['coverage_median'].median():.3f}; {byp}); "
        f"D2 final (c_crossfit_design, xf interval) within 0.02 of D0 in {int(b_.sum())} of {len(b_)} (differences {d2f['diff'].min():.3f} to {d2f['diff'].max():.3f}); "
        f"D1 strat_t in 0.88-0.92 in {int(c_.sum())} of {len(c_)} (median {d1['coverage_median'].median():.3f})",
        pd.concat([d2c.assign(kind="D2_classical"), d2f.assign(kind="D2_final_minus_D0"), d1.assign(kind="D1")]))
    for pa in sorted(d2c["p_a"].dropna().unique()):
        num(f"E4.4|D2_classical_own|p_a{pa}|coverage_median_median", d2c[d2c["p_a"] == pa]["coverage_median"].median(), "e4_selection_grid.csv")
    # E4.5 embedding balance leaves the ratio at 0.9 or above on the kidney tasks
    e5 = r[(r["vtag"].isin(KIDNEY)) & (r["balance"].astype(str).str.startswith("pcE")) & (r["design"] == "D2")
           & (r["rule"] == "none") & (r["interval"] == BASE[1])]
    ok = e5["ratio_median"] >= 0.9
    add("E4.5", "held" if ok.all() else ("partly held" if ok.mean() >= 0.5 else "refuted"),
        f"kidney tasks, embedding balance, D2: classical variance ratio >= 0.9 in {int(ok.sum())} of {len(e5)} cells "
        f"(range {e5['ratio_median'].min():.3f} to {e5['ratio_median'].max():.3f})", e5)
    # Acceptance 2 diagnostic: permuted-balance D2 classical variance against D0, beside D0's own
    # estimated-over-empirical ratio (draw noise of D0's 200 draws, shared by every gene of a task)
    x = grid[(grid["rule"] == "none") & (grid["interval"] == BASE[1])]
    d0 = x[x["design"] == "D0"].drop_duplicates(["vtag", "estimand", "n_L"])[["vtag", "estimand", "n_L", "emp_var_median", "est_var_over_emp_var_median"]]
    pb = x[(x["design"] == "D2") & (x["balance"] == "perm")].drop_duplicates(["vtag", "estimand", "n_L", "p_a"])[
        ["vtag", "estimand", "n_L", "p_a", "emp_var_median", "est_var_over_emp_var_median"]]
    dg = pb.merge(d0, on=["vtag", "estimand", "n_L"], suffixes=("", "_D0"))
    dg["ratio_of_median_emp_var"] = dg["emp_var_median"] / dg["emp_var_median_D0"]
    dg["in_band_093_107"] = dg["ratio_of_median_emp_var"].between(0.93, 1.07)
    dg["D0_est_over_emp_outside_093_107"] = ~dg["est_var_over_emp_var_median_D0"].between(0.93, 1.07)
    dg.to_csv(f"{D}/e4_perm_balance_diagnostic.csv", index=False)
    for vt in TASKS:
        z = dg[dg["vtag"] == vt]
        num(f"A2diag|{vt}|n_cells", len(z), "e4_perm_balance_diagnostic.csv")
        num(f"A2diag|{vt}|n_in_band", int(z["in_band_093_107"].sum()), "e4_perm_balance_diagnostic.csv")
        num(f"A2diag|{vt}|D0_est_over_emp_min", z["est_var_over_emp_var_median_D0"].min(), "e4_perm_balance_diagnostic.csv")
        num(f"A2diag|{vt}|D0_est_over_emp_max", z["est_var_over_emp_var_median_D0"].max(), "e4_perm_balance_diagnostic.csv")
        num(f"A2diag|{vt}|ratio_min", z["ratio_of_median_emp_var"].min(), "e4_perm_balance_diagnostic.csv")
        num(f"A2diag|{vt}|ratio_max", z["ratio_of_median_emp_var"].max(), "e4_perm_balance_diagnostic.csv")
    inc = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"{D}/*/_inclusion/e4_inclusion_bias__*.csv"))], ignore_index=True)
    inc.to_csv(f"{D}/e4_inclusion_bias.csv", index=False)
    for r_ in inc.itertuples():
        k = f"incl|{r_.vtag}|{r_.estimand}|nL{r_.n_L}|p_a{r_.p_a}"
        num(f"{k}|inclusion_sd", r_.inclusion_sd_over_donors, "e4_inclusion_bias.csv")
        num(f"{k}|frac_abs_bias_z_gt_3", r_.frac_genes_abs_bias_z_gt_3, "e4_inclusion_bias.csv")
        num(f"{k}|spearman_vs_spots", r_.spearman_inclusion_vs_spots, "e4_inclusion_bias.csv")
    pd.DataFrame(NUM).to_csv(f"{D}/e4_report_numbers.csv", index=False)
    pd.DataFrame(scores).to_csv(f"{D}/e4_prediction_scores.csv", index=False)
    pd.concat(cells, ignore_index=True, sort=False).to_csv(f"{D}/e4_prediction_cells.csv", index=False)
    print(pd.DataFrame(scores).to_string())


if __name__ == "__main__":
    main()
