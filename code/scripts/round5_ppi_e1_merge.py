"""Round 5 PPI, stage E1: merge the unit fragments, run the acceptance checks, score the predictions.

Run on Longleaf from results/round5/ppi/E1_interval/ (the stage directory). Reads
  frag_G15/*/e1_sim_grid__*.csv, frag_G24/..., frag_G51/...   (tags containing 'smoke' are ignored)
  frag_diag/moments/{e1_contribution_moments.csv,e1_acceptance1.csv,e1_law_shapes.json}
  frag_diag/spearman/e1_real_coverage_vs_skewness.csv
and checks every fragment directory's _provenance.json against the frame id assigned to its unit
(--frames G15=<id>,G24=<id>,G51=<id>,diag=<id>). Writes, summaries first:
  e1_stamp_check.csv, e1_acceptance.csv, e1_prediction_cells.csv (every cell each prediction is
  scored on, with the quantity), e1_prediction_scores.csv, e1_report_numbers.csv (name,value),
  e1_johnson.csv, e1_sim_grid.csv (merged; law_name normal/skewed/heavy), copies of the diagnostic
  tables, and fig_e1_coverage.png.
"""
import argparse
import glob
import json
import os
import shutil

import numpy as np
import pandas as pd

FINAL = ("c_crossfit_design", "textbook_t|fpc|lin")
NOLIN = ("c_crossfit_design", "textbook_t|fpc")
CLASS = ("none", "textbook_t|fpc")
ORACLE = ("oracle", "textbook_t|fpc|lin")
JOHN_F = ("c_crossfit_design", "johnson|fpc|lin")
JOHN_C = ("none", "johnson|fpc|lin")
KEYS = ["G", "n_L", "R2", "lambda_star", "kappa", "law_name"]


def law_name(s):
    if s == "normal":
        return "normal"
    sig = float(s.split(":")[1])
    return "skewed" if sig < 1.5 else "heavy"


def pick(df, ri):
    r, i = ri
    return df[(df.rule == r) & (df.interval == i)].set_index(KEYS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    a = ap.parse_args()
    frames = dict(x.split("=") for x in a.frames.split(","))
    # stamps
    st = []
    for unit, fid in frames.items():
        base = "frag_diag" if unit == "diag" else f"frag_{unit}"
        for p in sorted(glob.glob(f"{base}/**/_provenance.json", recursive=True)):
            s = json.load(open(p))
            st.append(dict(unit=unit, path=p, frame_id=s.get("frame_id"), assigned=fid, match=s.get("frame_id") == fid))
    st = pd.DataFrame(st)
    st.to_csv("e1_stamp_check.csv", index=False)
    # merge grids
    parts = []
    for f in sorted(glob.glob("frag_G*/*/e1_sim_grid__*.csv")):
        if "smoke" in f:
            continue
        d = pd.read_csv(f)
        d["source_file"] = f
        parts.append(d)
    g = pd.concat(parts, ignore_index=True)
    g["law_name"] = g.law.map(law_name)
    dup = g.duplicated(KEYS + ["rule", "interval"], keep=False)
    coll = g[dup]
    if len(coll):
        # identical duplicates are reported, differing ones are an error
        num = coll.select_dtypes("number").columns
        same = coll.groupby(KEYS + ["rule", "interval"])[list(num)].nunique().max(axis=1).max() == 1
        print("collisions", len(coll), "identical" if same else "DIFFERING")
        assert same, "differing duplicate rows across fragments"
        g = g.drop_duplicates(KEYS + ["rule", "interval"])
    g.to_csv("e1_sim_grid.csv", index=False)
    n_cells = g.groupby(["G", "law_name"]).apply(lambda x: len(x.drop_duplicates(KEYS))).to_dict()
    for src in ("frag_diag/moments/e1_contribution_moments.csv", "frag_diag/moments/e1_acceptance1.csv",
                "frag_diag/spearman/e1_real_coverage_vs_skewness.csv", "frag_diag/moments/e1_law_shapes.json"):
        shutil.copy(src, os.path.basename(src))

    fin, nol, cla, orc = pick(g, FINAL), pick(g, NOLIN), pick(g, CLASS), pick(g, ORACLE)
    rn, cells, scores, acc = [], [], [], []

    def num(name, value):
        rn.append(dict(name=name, value=value))

    # ---------------- acceptance
    a1 = pd.read_csv("e1_acceptance1.csv")
    acc.append(dict(check="1_variance_function_equals_textbook_two_stage_lin", n=len(a1), n_pass=int(a1.passes.sum()),
                    worst=float(max(a1.rel_diff_theta.max(), a1.rel_diff_var.max())), tolerance=1e-12))
    none_f = pick(g, ("none", "textbook_t|fpc")); none_l = pick(g, ("none", "textbook_t|fpc|lin"))
    cols = [c for c in none_f.columns if c not in ("interval", "rule", "source_file", "law")]
    same = (none_f[cols].sort_index().round(15).fillna(-9) == none_l[cols].sort_index().round(15).fillna(-9)).all(axis=1)
    acc.append(dict(check="2_rule_none_fpc_equals_fpc_lin", n=len(same), n_pass=int(same.sum()), worst=np.nan, tolerance=0))
    z = (orc.emp_over_exact_fixed_mean - 1) / orc.emp_over_exact_fixed_mc_se
    for ln in ("normal", "skewed", "heavy"):
        zz = z[z.index.get_level_values("law_name") == ln]
        acc.append(dict(check=f"3_oracle_within_3_mcse|{ln}", n=len(zz), n_pass=int((zz.abs() <= 3).sum()),
                        worst=float(zz.abs().max()), tolerance=3))
        for idx, v in zz[zz.abs() > 3].items():
            cells.append(dict(prediction="acceptance3_exceedance", **dict(zip(KEYS, idx)), quantity="z", value=v,
                              in_band=False))
    c24 = cla[(cla.index.get_level_values("G") == 24) & (cla.index.get_level_values("law_name") == "normal")]
    med = c24.groupby(level="n_L").coverage_mean.median()
    for nl, v in med.items():
        num(f"acc4|classical_median_coverage_over_cells|G24|normal|nL{nl}", v)
    acc.append(dict(check="4_classical_normal_G24_median_coverage_within_0.01_of_0.90", n=len(med),
                    n_pass=int((med.sub(0.90).abs() <= 0.01).sum()), worst=float(med.sub(0.90).abs().max()), tolerance=0.01))
    pd.DataFrame(acc).to_csv("e1_acceptance.csv", index=False)

    def score(pred, sel_df, qty, lo=None, hi=None, need="all", frac=None):
        ok = pd.Series(True, index=sel_df.index)
        if lo is not None:
            ok &= sel_df[qty] >= lo
        if hi is not None:
            ok &= sel_df[qty] <= hi
        for idx, row in sel_df.iterrows():
            cells.append(dict(prediction=pred, **dict(zip(KEYS, idx)), quantity=qty, value=row[qty], in_band=bool(ok[idx])))
        n, k = len(ok), int(ok.sum())
        held = (k == n) if need == "all" else (k >= frac * n)
        scores.append(dict(prediction=pred, n_cells=n, n_in_band=k, rule=need if need == "all" else f">= {frac} of cells",
                           band=f"[{lo}, {hi}]", qty_min=float(sel_df[qty].min()) if n else np.nan,
                           qty_median=float(sel_df[qty].median()) if n else np.nan,
                           qty_max=float(sel_df[qty].max()) if n else np.nan, held=bool(held) if n else None))

    def sub(df, **kw):
        m = pd.Series(True, index=df.index)
        for k, f in kw.items():
            m &= f(df.index.get_level_values(k))
        return df[m]

    for ln in ("normal", "skewed", "heavy"):
        L = lambda s: s == ln
        # E1.1
        f6 = sub(fin, law_name=L, n_L=lambda x: x >= 6)
        score(f"E1.1a|{ln}|final coverage in [0.88,0.91], nL>=6", f6, "coverage_mean", 0.88, 0.91)
        d = (f6.coverage_mean - cla.loc[f6.index].coverage_mean).abs().to_frame("abs_diff_final_minus_classical")
        score(f"E1.1b|{ln}|final within 0.02 of classical, nL>=6", d, "abs_diff_final_minus_classical", None, 0.02)
        # E1.2
        k10 = sub(nol, law_name=L, kappa=lambda x: x == 10, R2=lambda x: x >= 0.4, n_L=lambda x: x >= 6)
        score(f"E1.2a|{ln}|no-lin est/emp > 2 in >= half, kappa10 R2>=0.4 nL>=6", k10, "est_over_emp_median", 2.0, None,
              need="frac", frac=0.5)
        k10f = fin.loc[k10.index]
        score(f"E1.2b|{ln}|lin est/emp in [0.85,1.10], kappa10 R2>=0.4 nL>=6", k10f, "est_over_emp_median", 0.85, 1.10)
        k0 = sub(fin, law_name=L, kappa=lambda x: x == 0)
        d = (k0.coverage_mean - nol.loc[k0.index].coverage_mean).abs().to_frame("abs_cov_diff_lin_minus_nolin")
        score(f"E1.2c|{ln}|kappa0 lin vs no-lin coverage differ < 0.01", d, "abs_cov_diff_lin_minus_nolin", None, 0.0099999)
        # E1.3
        fa = sub(fin, law_name=L, n_L=lambda x: x >= 6, R2=lambda x: x >= 0.4)
        fa = fa[fa.index.get_level_values("n_L") / fa.index.get_level_values("G") >= 1 / 3]
        d = (cla.loc[fa.index].est_over_emp_median - fa.est_over_emp_median).to_frame("classical_minus_final_est_over_emp")
        score(f"E1.3a|{ln}|classical minus final est/emp in [0.03,0.15], nL/G>=1/3 R2>=0.4", d,
              "classical_minus_final_est_over_emp", 0.03, 0.15)
        fb = sub(fin, law_name=L, G=lambda x: x == 51, n_L=lambda x: (x >= 6) & (x <= 12))
        d = (cla.loc[fb.index].est_over_emp_median - fb.est_over_emp_median).to_frame("classical_minus_final_est_over_emp")
        score(f"E1.3b|{ln}|classical minus final est/emp < 0.05, G51 nL6-12", d, "classical_minus_final_est_over_emp",
              None, 0.0499999)
        # E1.5
        f5 = sub(fin, law_name=L, R2=lambda x: x > 0, n_L=lambda x: x >= 6)
        be = 4 + 2 / f5.index.get_level_values("R2")
        above = f5[f5.index.get_level_values("n_L") > be]
        below = f5[f5.index.get_level_values("n_L") <= be]
        score(f"E1.5a|{ln}|tuned/classical variance < 1 above break-even", above, "var_ratio_to_classical_mean", None, 0.9999999)
        score(f"E1.5b|{ln}|tuned/classical variance > 1 in >= half below break-even (nL>=6)", below,
              "var_ratio_to_classical_mean", 1.0000001, None, need="frac", frac=0.5)
    # E1.4
    c = sub(cla, law_name=lambda s: s == "normal", G=lambda x: x == 24, n_L=lambda x: x == 8)
    d = (c.coverage_p95 - c.coverage_p05).to_frame("p95_minus_p05")
    score("E1.4a|normal G24 nL8 classical per-population 5-95 range >= 0.03", d, "p95_minus_p05", 0.03, None)
    score("E1.4b|normal G24 nL8 classical per-population p05 > 0.87", c, "coverage_p05", 0.8700001, None)
    for ln in ("skewed", "heavy"):
        cs = sub(cla, law_name=lambda s: s == ln, G=lambda x: x == 24)
        byn = cs.groupby(level="n_L").coverage_mean.mean().to_frame("mean_over_cells_classical_coverage")
        byn["G"] = 24; byn["R2"] = np.nan; byn["lambda_star"] = np.nan; byn["kappa"] = np.nan; byn["law_name"] = ln
        byn = byn.reset_index().set_index(KEYS)
        score(f"E1.4c|{ln} G24 classical coverage averaged over cells in [0.85,0.89], per nL", byn,
              "mean_over_cells_classical_coverage", 0.85, 0.89)
    pd.DataFrame(scores).to_csv("e1_prediction_scores.csv", index=False)
    pd.DataFrame(cells).to_csv("e1_prediction_cells.csv", index=False)
    # Johnson
    jr = []
    for (lab, base, jo) in (("final", FINAL, JOHN_F), ("classical", CLASS, JOHN_C)):
        b, j = pick(g, base), pick(g, jo)
        for (G, ln), bb in b.groupby(level=["G", "law_name"]):
            jj = j.loc[bb.index]
            jr.append(dict(estimator=lab, G=G, law_name=ln, n_cells=len(bb), t_coverage_mean=bb.coverage_mean.mean(),
                           johnson_coverage_mean=jj.coverage_mean.mean(), t_coverage_min=bb.coverage_mean.min(),
                           johnson_coverage_min=jj.coverage_mean.min(),
                           johnson_width_over_t_width=float((jj.width_mean / bb.width_mean).median())))
    pd.DataFrame(jr).to_csv("e1_johnson.csv", index=False)
    # headline numbers per law and G (every number the report quotes comes from here)
    for (G, ln), bb in fin.groupby(level=["G", "law_name"]):
        cc = cla.loc[bb.index]
        for nm, s in (("final_coverage", bb.coverage_mean), ("classical_coverage", cc.coverage_mean),
                      ("final_est_over_emp", bb.est_over_emp_median), ("classical_est_over_emp", cc.est_over_emp_median),
                      ("final_var_ratio_to_classical", bb.var_ratio_to_classical_mean)):
            s6 = s[s.index.get_level_values("n_L") >= 6]
            num(f"{nm}|G{G}|{ln}|nL>=6|min", float(s6.min())); num(f"{nm}|G{G}|{ln}|nL>=6|median", float(s6.median()))
            num(f"{nm}|G{G}|{ln}|nL>=6|max", float(s6.max()))
    for k, v in n_cells.items():
        num(f"n_cells|G{k[0]}|{k[1]}", v)
    sp = pd.read_csv("e1_real_coverage_vs_skewness.csv")
    for _, r in sp.iterrows():
        num(f"spearman_cov_abs_skew|{r.vtag}|{r.arm}|{r.estimand}", r.spearman_cov_abs_skew)
    mom = pd.read_csv("e1_contribution_moments.csv")
    for (vt, est), mm in mom[mom.arm.isin(["hoptimus0", "package"])].groupby(["vtag", "estimand"]):
        num(f"median_abs_skew_z|{vt}|{est}", float(mm.skew_z.abs().median()))
        num(f"median_level_over_sd_f|{vt}|{est}", float(mm.level_over_sd_f.abs().median()))
    pd.DataFrame(rn).to_csv("e1_report_numbers.csv", index=False)
    # figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 7,
                         "ytick.labelsize": 7, "legend.fontsize": 7, "axes.spines.top": False, "axes.spines.right": False})
    colors = {"normal": "#1b6ca8", "skewed": "#d08c00", "heavy": "#7a3d9a"}
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.5), sharey=True, gridspec_kw=dict(wspace=0.08))
    for ax, G in zip(axes, (15, 24, 51)):
        for ln in ("normal", "skewed", "heavy"):
            for (ri, ls, lab) in ((FINAL, "-", "final interval"), (CLASS, "--", "classical")):
                d = pick(g, ri)
                d = d[(d.index.get_level_values("G") == G) & (d.index.get_level_values("law_name") == ln)]
                m = d.groupby(level="n_L").coverage_mean.mean()
                ax.plot(m.index, m.values, ls=ls, marker="o", ms=3, color=colors[ln], lw=1.4 if ls == "-" else 1.0,
                        label=f"{ln}, {lab}")
        ax.axhline(0.90, color="0.5", lw=0.6, ls=":")
        ax.set_xlabel("labelled clusters $n_L$")
        ax.set_title(f"G = {G} clusters", loc="left")
        ax.margins(0.05)
    axes[0].set_ylabel("coverage of nominal 90% interval\n(mean over cells)")
    axes[0].legend(frameon=False, loc="lower right", ncol=1)
    fig.savefig("fig_e1_coverage.png", dpi=300, bbox_inches="tight")
    print(pd.DataFrame(acc).to_string()); print(pd.DataFrame(scores).to_string())


if __name__ == "__main__":
    main()
