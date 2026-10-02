#!/usr/bin/env python
"""Round 4, PPI track: merge the Q2 and Q3 unit outputs and compute the numbers the Q3 report quotes.

Input: a staging directory holding each unit's hand-back (--stage), with
  Q2_theory/<TASK>/**/nL*/q2_variance_grid__<vtag>__<arm>.csv   (+ q2_cluster_r2__*, fitted components)
  Q3_regimes/<TASK>/**/q3_regime_comparison__*.csv or a combined *_all.csv, and q3_acceptance files.
Output under --out (the repository's results/round4/ppi/):
  Q2_theory/q2_variance_grid.csv, q2_cluster_r2.csv, q2_fitted_components.csv, q2_report_numbers.csv,
  fig_q2_gain_vs_cluster_r2.png, fig_q2_variance_vs_m.png, fig_q2_optimal_m.png;
  Q3_regimes/q3_regime_comparison.csv, q3_acceptance.csv, q3_report_numbers.csv, fig_q3_regimes.png.
Every number in q2_report_numbers.csv and q3_report_numbers.csv is a named scalar (name, value).

Conventions. The primary estimand is theta_3 donor-weighted (memo section 4). "Superpopulation" rows use
CR1 with t; "design" rows the textbook form with the finite-population correction. The variance ratio at
m = all is the PPI-to-classical ratio of empirical variances over draws, median over genes, at the
largest n_L the task allows. R^2 values are on the estimator's own per-spot scale (z, f-z), median over
genes. Two cluster-level values are reported: `raw`, the squared correlation of the donor values of z and
f-z over donors (what the donor-weighted estimator at m = all actually regresses), and `corrected`, the
one-way ANOVA estimate of the infinite-m value, which is undefined (negative variance components) for some
estimands; the fraction of genes where it is undefined is reported.
"""
import argparse
import glob
import os

import numpy as np
import pandas as pd
from scipy import stats

KEY = ["vtag", "arm", "n_L", "m", "estimand", "population", "target", "lambda_rule", "interval"]
RULES = ("c_crossfit", "d1_pretest", "d2_pretest")


def read_all(pattern):
    fs = sorted(set(glob.glob(pattern, recursive=True)))
    if not fs:
        return pd.DataFrame(), []
    return pd.concat([pd.read_csv(f) for f in fs], ignore_index=True), fs


def q2_merge(stage, out):
    grid, gf = read_all(f"{stage}/Q2_theory/**/nL*/q2_variance_grid__*.csv")
    assert len(grid), "no Q2 grid files"
    dup = grid.duplicated(KEY)
    assert not dup.any(), f"{int(dup.sum())} duplicated Q2 rows"
    r2, _ = read_all(f"{stage}/Q2_theory/**/nL*/q2_cluster_r2__*.csv")
    r2 = r2.drop_duplicates(["vtag", "arm", "scale", "estimand", "population", "gene"])
    fparts = []
    for f in sorted(set(glob.glob(f"{stage}/Q2_theory/**/q2_fitted_components__*.csv", recursive=True))):
        stem = os.path.basename(f)[len("q2_fitted_components__"):-4]
        vt, arm = stem.rsplit("__", 1)
        d = pd.read_csv(f)
        d.insert(0, "arm", arm); d.insert(0, "vtag", vt)
        fparts.append(d)
    fit = pd.concat(fparts, ignore_index=True) if fparts else pd.DataFrame()
    if len(fit):
        fk = ["vtag", "arm", "estimand", "population", "target", "lambda_rule", "interval", "gene"]
        fit = fit.drop_duplicates(fk + ["sigma2_cluster"])
        assert not fit.duplicated(fk).any(), "conflicting fitted-components rows"
    os.makedirs(f"{out}/Q2_theory", exist_ok=True)
    grid.to_csv(f"{out}/Q2_theory/q2_variance_grid.csv", index=False)
    r2.to_csv(f"{out}/Q2_theory/q2_cluster_r2.csv", index=False)
    if len(fit):
        fit.to_csv(f"{out}/Q2_theory/q2_fitted_components.csv", index=False)
    return grid, r2, fit, gf


def q2_numbers(grid, r2, fit):
    rows = []

    def add(name, v):
        rows.append(dict(name=name, value=float(v) if v is not None and np.isfinite(v) else np.nan))

    g = grid.copy()
    g["m_all"] = g["m"].astype(str) == "all"
    r2z = r2[r2.scale == "z"]
    for (vt, arm), gg in g.groupby(["vtag", "arm"]):
        nmax = gg.n_L.max()
        add(f"Q2|{vt}|{arm}|nL_max", nmax)
        for est in ("theta3", "theta2"):
            for pop in ("donor", "spot"):
                rz = r2z[(r2z.vtag == vt) & (r2z.arm == arm) & (r2z.estimand == est) & (r2z.population == pop)]
                one_c = float(np.nanmedian(1 - rz.R2_cluster_corrected)) if len(rz) else np.nan
                one_u = float(np.nanmedian(1 - rz.R2_unit)) if len(rz) else np.nan
                one_w = float(np.nanmedian(1 - rz.R2_within)) if len(rz) else np.nan
                one_r = float(np.nanmedian(1 - rz.R2_cluster_raw)) if len(rz) else np.nan
                frac_nan_c = float(rz.R2_cluster_corrected.isna().mean()) if len(rz) else np.nan
                tag = f"{vt}|{arm}|{est}|{pop}"
                add(f"Q2.1|{tag}|one_minus_R2_cluster", one_c)
                add(f"Q2.1|{tag}|one_minus_R2_unit", one_u)
                add(f"Q2.1|{tag}|one_minus_R2_within", one_w)
                add(f"Q2.1|{tag}|R2_cluster_raw", float(np.nanmedian(rz.R2_cluster_raw)) if len(rz) else np.nan)
                add(f"Q2.1|{tag}|one_minus_R2_cluster_raw", one_r)
                add(f"Q2.1|{tag}|frac_genes_R2_cluster_corrected_undefined", frac_nan_c)
                for rule in RULES:
                    for tgt, iv in (("super", "CR1_t"), ("design", "textbook_t|fpc")):
                        s = gg[(gg.estimand == est) & (gg.population == pop) & (gg.target == tgt) &
                               (gg.interval == iv) & (gg.lambda_rule == rule)]
                        sa = s[s.m_all & (s.n_L == nmax)]
                        v = float(sa.emp_var_ratio_median.iloc[0]) if len(sa) else np.nan
                        add(f"Q2.1|{tag}|{tgt}|{rule}|var_ratio_mall_nLmax", v)
                        if tgt == "super":
                            add(f"Q2.1|{tag}|{tgt}|{rule}|var_ratio_minus_one_minus_R2c", v - one_c)
                            add(f"Q2.1|{tag}|{tgt}|{rule}|var_ratio_minus_one_minus_R2c_raw", v - one_r)
                        # Q2.2: flatness of the empirical variance in m (classical and rule c)
                        for m in ("100", "200", "500"):
                            sm = s[(s.m.astype(str) == m) & (s.n_L == nmax)]
                            if len(sm) and len(sa):
                                add(f"Q2.2|{tag}|{tgt}|{rule}|emp_var_m{m}_over_mall",
                                    float(sm.emp_var_median.iloc[0] / sa.emp_var_median.iloc[0]))
                        # Q2.5: estimated over empirical variance by n_L
                        for n in sorted(s.n_L.unique()):
                            add(f"Q2.5|{tag}|{tgt}|{rule}|nL{n}|est_over_emp_median",
                                float(s[s.n_L == n].est_var_over_emp_var_median.median()))
                        add(f"Q2.5|{tag}|{tgt}|{rule}|coverage_median_all_cells", float(s.coverage_median.median()))
                for tgt, iv in (("super", "CR1_t"), ("design", "textbook_t|fpc")):
                    s = gg[(gg.estimand == est) & (gg.population == pop) & (gg.target == tgt) &
                           (gg.interval == iv) & (gg.lambda_rule == "none")]
                    for n in sorted(s.n_L.unique()):
                        add(f"Q2.5|{tag}|{tgt}|none|nL{n}|est_over_emp_median",
                            float(s[s.n_L == n].est_var_over_emp_var_median.median()))
                    sa = s[s.m_all & (s.n_L == nmax)]
                    for m in ("100", "200", "500"):
                        sm = s[(s.m.astype(str) == m) & (s.n_L == nmax)]
                        if len(sm) and len(sa):
                            add(f"Q2.2|{tag}|{tgt}|none|emp_var_m{m}_over_mall",
                                float(sm.emp_var_median.iloc[0] / sa.emp_var_median.iloc[0]))
                    add(f"Q2.5|{tag}|{tgt}|none|coverage_median_all_cells", float(s.coverage_median.median()))
    if len(fit):
        f = fit[(fit.target == "super") & (fit.interval == "CR1_t")]
        for (vt, arm, est, pop, rule), ff in f.groupby(["vtag", "arm", "estimand", "population", "lambda_rule"]):
            tag = f"{vt}|{arm}|{est}|{pop}|{rule}"
            for k in ("sigma2_cluster", "sigma2_unit", "rho_r", "m_star_cd_cs_10", "m_star_cd_cs_100",
                      "m_star_cd_cs_1000", "m_at_f0.1"):
                if k in ff:
                    add(f"Q2.3|{tag}|{k}_median", float(np.nanmedian(ff[k])))
    return pd.DataFrame(rows)


def q3_merge(stage, out):
    parts, fs = [], []
    for pat in (f"{stage}/Q3_regimes/**/q3_regime_comparison__*.csv",):
        d, f = read_all(pat)
        if len(d):
            parts.append(d); fs += f
    d, f = read_all(f"{stage}/Q3_regimes/**/*regime_comparison*_all.csv")
    if len(d):
        parts.append(d); fs += f
    q3 = pd.concat(parts, ignore_index=True)
    k = ["vtag", "arm", "regime", "budget", "cost", "n_L", "m", "estimand", "population", "target",
         "lambda_rule", "interval"]
    q3 = q3.drop_duplicates(k + ["emp_var_median", "coverage_median"])
    assert not q3.duplicated(k).any(), "conflicting duplicate Q3 rows"
    acc, _ = read_all(f"{stage}/Q3_regimes/**/q3_acceptance*.csv")
    os.makedirs(f"{out}/Q3_regimes", exist_ok=True)
    q3.to_csv(f"{out}/Q3_regimes/q3_regime_comparison.csv", index=False)
    acc.drop_duplicates().to_csv(f"{out}/Q3_regimes/q3_acceptance.csv", index=False)
    return q3, acc.drop_duplicates(), fs


def q3_numbers(q3, acc, r2):
    rows = []

    def add(name, v):
        rows.append(dict(name=name, value=float(v) if v is not None and np.isfinite(v) else np.nan))

    if len(acc):
        for chk, aa in acc.groupby("check"):
            add(f"Q3.acc|{chk}|max", aa.value.max())
    for (vt, arm), qq in q3.groupby(["vtag", "arm"]):
        for est in ("theta3", "theta2"):
            for pop in ("donor", "spot"):
                for rule in ("none",) + RULES:
                    base = qq[(qq.estimand == est) & (qq.population == pop) & (qq.lambda_rule == rule)]
                    tag = f"{vt}|{arm}|{est}|{pop}|{rule}"
                    for tgt in ("design", "super"):
                        A = base[(base.regime == "A") & (base.target == tgt)]
                        Bu = base[(base.regime == "B") & (base.cost == "unit") & (base.target == tgt)]
                        for B in sorted(Bu.budget.unique()):
                            vb = Bu[Bu.budget == B].emp_var_median.iloc[0]
                            add(f"Q3.2|{tag}|{tgt}|regB|B{B}|coverage_median", Bu[Bu.budget == B].coverage_median.iloc[0])
                            add(f"Q3.2|{tag}|{tgt}|regB|B{B}|m_median", Bu[Bu.budget == B].m.iloc[0])
                            for n in sorted(A.n_L.unique()):
                                aa = A[(A.budget == B) & (A.n_L == n)]
                                if len(aa):
                                    add(f"Q3.1|{tag}|{tgt}|B{B}|nL{n}|width_ratio_B_over_A",
                                        float(np.sqrt(vb / aa.emp_var_median.iloc[0])))
                                    add(f"Q3.1|{tag}|{tgt}|B{B}|nL{n}|regA_coverage_median",
                                        aa.coverage_median.iloc[0])
                        Bc = base[(base.regime == "B") & (base.cost != "unit") & (base.target == tgt)]
                        for _, row in Bc.iterrows():
                            parts = row.cost.split("_")
                            nl = parts[-2].replace("nL", ""); bb = parts[-1].replace("B", "")
                            aa = A[(A.budget == int(bb)) & (A.n_L == int(nl))]
                            if len(aa):
                                add(f"Q3.1|{tag}|{tgt}|cost100|B{bb}|nL{nl}|width_ratio_B_over_A",
                                    float(np.sqrt(row.emp_var_median / aa.emp_var_median.iloc[0])))
                                add(f"Q3.1|{tag}|{tgt}|cost100|B{bb}|nL{nl}|regB_budget", row.budget)
    # Q3.4: rank correlation across arms of each regime's variance ratio with 1 - R^2
    r2z = r2[(r2.scale == "z")]
    for est, pop, tgt in (("theta3", "donor", "super"), ("theta3", "donor", "design")):
        recs = []
        for (vt, arm), qq in q3.groupby(["vtag", "arm"]):
            rz = r2z[(r2z.vtag == vt) & (r2z.arm == arm) & (r2z.estimand == est) & (r2z.population == pop)]
            if not len(rz):
                continue
            for reg in ("A", "B"):
                s = qq[(qq.regime == reg) & (qq.cost == "unit") & (qq.estimand == est) & (qq.population == pop)
                       & (qq.target == tgt) & (qq.lambda_rule == "c_crossfit") & (qq.budget == 9600)]
                if reg == "A":
                    s = s[s.n_L == s.n_L.max()]
                if len(s):
                    recs.append(dict(vtag=vt, arm=arm, regime=reg, ratio=float(s.emp_var_ratio_median.iloc[0]),
                                     omc=float(np.nanmedian(1 - rz.R2_cluster_corrected)),
                                     omw=float(np.nanmedian(1 - rz.R2_within))))
        rr = pd.DataFrame(recs)
        for reg in ("A", "B"):
            x = rr[rr.regime == reg]
            if len(x) >= 3:
                add(f"Q3.4|{est}|{pop}|{tgt}|regime{reg}|spearman_ratio_vs_one_minus_R2c_pooled",
                    stats.spearmanr(x.ratio, x.omc)[0])
                add(f"Q3.4|{est}|{pop}|{tgt}|regime{reg}|spearman_ratio_vs_one_minus_R2w_pooled",
                    stats.spearmanr(x.ratio, x.omw)[0])
                add(f"Q3.4|{est}|{pop}|{tgt}|regime{reg}|n_points", len(x))
            for vt, xv in x.groupby("vtag"):
                if len(xv) >= 3:
                    add(f"Q3.4|{vt}|{est}|{pop}|{tgt}|regime{reg}|spearman_ratio_vs_one_minus_R2c",
                        stats.spearmanr(xv.ratio, xv.omc)[0])
                    add(f"Q3.4|{vt}|{est}|{pop}|{tgt}|regime{reg}|spearman_ratio_vs_one_minus_R2w",
                        stats.spearmanr(xv.ratio, xv.omw)[0])
    return pd.DataFrame(rows)


def figures(grid, r2, fit, q3, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    g = grid[(grid.estimand == "theta3") & (grid.population == "donor") & (grid.target == "super")
             & (grid.interval == "CR1_t") & (grid.lambda_rule == "c_crossfit")]
    r2z = r2[(r2.scale == "z") & (r2.estimand == "theta3") & (r2.population == "donor")]
    # gain vs cluster R2
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    for (vt, arm), gg in g.groupby(["vtag", "arm"]):
        s = gg[(gg.m.astype(str) == "all") & (gg.n_L == gg.n_L.max())]
        rz = r2z[(r2z.vtag == vt) & (r2z.arm == arm)]
        if len(s) and len(rz):
            x = float(np.nanmedian(1 - rz.R2_cluster_raw))
            ax.scatter(x, s.emp_var_ratio_median.iloc[0], s=30)
            ax.annotate(f"{vt}:{arm}", (x, s.emp_var_ratio_median.iloc[0]), fontsize=6)
    lim = [0, 1.4]
    ax.plot(lim, lim, color="grey", lw=0.8)
    ax.set_xlabel("1 - cluster-level $R^2$ of donor values (median over genes)")
    ax.set_ylabel("PPI / classical variance at m = all, largest $n_L$")
    ax.set_title(r"$\theta_3$ donor-weighted, rule (c)", fontsize=9)
    fig.tight_layout(); fig.savefig(f"{out}/Q2_theory/fig_q2_gain_vs_cluster_r2.png", dpi=200); plt.close(fig)
    # variance vs m
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    for (vt, arm), gg in g[g.arm.isin(["hoptimus0", "package"])].groupby(["vtag", "arm"]):
        n = 8 if (gg.n_L == 8).any() else gg.n_L.max()
        s = gg[gg.n_L == n].copy()
        s["mn"] = pd.to_numeric(s.m.replace("all", np.nan))
        s = s.dropna(subset=["mn"]).sort_values("mn")
        a = gg[(gg.n_L == n) & (gg.m.astype(str) == "all")]
        if len(s) and len(a):
            ax.plot(s.mn, s.emp_var_median / a.emp_var_median.iloc[0], marker="o", label=f"{vt} ({arm}, n_L={n})")
    ax.set_xscale("log"); ax.axhline(1, color="grey", lw=0.8)
    ax.set_xlabel("labelled spots per donor m"); ax.set_ylabel("empirical variance / variance at m = all")
    ax.legend(fontsize=6); fig.tight_layout(); fig.savefig(f"{out}/Q2_theory/fig_q2_variance_vs_m.png", dpi=200); plt.close(fig)
    # optimal m
    if len(fit):
        f = fit[(fit.target == "super") & (fit.interval == "CR1_t") & (fit.estimand == "theta3")
                & (fit.population == "donor") & (fit.lambda_rule.isin(["none", "c_crossfit"]))]
        piv = f.groupby(["vtag", "arm", "lambda_rule"])["m_star_cd_cs_100"].median().unstack()
        fig, ax = plt.subplots(figsize=(6.2, 4.2))
        piv.plot.bar(ax=ax)
        ax.set_yscale("log"); ax.set_ylabel(r"$m^\star$ at $c_d/c_s = 100$ (median over genes)")
        ax.tick_params(axis="x", labelsize=6); fig.tight_layout()
        fig.savefig(f"{out}/Q2_theory/fig_q2_optimal_m.png", dpi=200); plt.close(fig)
    # regimes
    q = q3[(q3.estimand == "theta3") & (q3.population == "donor") & (q3.lambda_rule == "c_crossfit")
           & (q3.cost == "unit")]
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.8), sharey=False)
    for ax, tgt in zip(axs, ("design", "super")):
        for (vt, arm), qq in q[(q.target == tgt) & q.arm.isin(["hoptimus0", "package"])].groupby(["vtag", "arm"]):
            B = qq[qq.regime == "B"].sort_values("budget")
            ax.plot(B.budget, B.emp_var_median, marker="o", label=f"{vt} B")
            A = qq[(qq.regime == "A") & (qq.n_L == 8)].sort_values("budget")
            ax.plot(A.budget, A.emp_var_median, marker="s", ls="--", label=f"{vt} A n_L=8")
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_title(tgt, fontsize=9)
        ax.set_xlabel("labelled spots B"); ax.set_ylabel("empirical variance (median over genes)")
    axs[1].legend(fontsize=6); fig.tight_layout(); fig.savefig(f"{out}/Q3_regimes/fig_q3_regimes.png", dpi=200); plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stage", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    grid, r2, fit, gf = q2_merge(a.stage, a.out)
    q2n = q2_numbers(grid, r2, fit)
    q2n.to_csv(f"{a.out}/Q2_theory/q2_report_numbers.csv", index=False)
    q3, acc, qf = q3_merge(a.stage, a.out)
    q3n = q3_numbers(q3, acc, r2)
    q3n.to_csv(f"{a.out}/Q3_regimes/q3_report_numbers.csv", index=False)
    figures(grid, r2, fit, q3, a.out)
    print(dict(q2_files=len(gf), q2_rows=len(grid), q2_numbers=len(q2n), q2_nan=int(q2n.value.isna().sum()),
               q3_rows=len(q3), q3_numbers=len(q3n), q3_nan=int(q3n.value.isna().sum()),
               tasks=sorted(grid.vtag.unique()), q3_tasks=sorted(q3.vtag.unique())))


if __name__ == "__main__":
    main()
