#!/usr/bin/env python
"""Round 4, PPI track, stage Q1: merge the fifteen simulation fragments and compute every pooled
number the Q1 report quotes (plan section 6, "fragments plus a merge step with collision
reporting"; every pooled number recomputed from the merged table).

Inputs: --frag-dir holding q1_sim__GL<g>__rho<r>.csv (one per unit); --acc-part12 the
Longleaf acceptance table (B1 configuration and m = 1); --perm the permuted-lambda table.
Outputs in --out-dir:
  q1_sim_coverage.csv       the merged table, one row per (cell, estimand, population, form,
                            lambda rule, interval, fpc)
  q1_merge_report.json      fragment list, row counts, key collisions
  q1_coverage_by_G.csv      coverage summary per (target, form, estimator, rule, interval, fpc,
                            G_L) over the other cell axes (min, q25, median, q75, max)
  q1_acceptance.csv         the acceptance table: part 1 and 2 from Longleaf plus the simulation
                            items (r = 0, and G_L = 20 at m = 200)
  q1_report_numbers.csv     every pooled number of the report, with its definition
  fig_q1_coverage_by_G.png
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

import numpy as np
import pandas as pd

KEY = ["target", "G_L", "G_U", "m", "rho", "r", "estimand", "population", "form",
       "lambda_rule", "interval", "fpc"]
NOM = 0.90


def load(frag_dir):
    files = sorted(glob.glob(f"{frag_dir}/**/q1_sim__GL*__rho*.csv", recursive=True))
    parts, info = [], []
    for f in files:
        d = pd.read_csv(f)
        m = re.search(r"q1_sim__GL(\d+)__rho([0-9.]+)\.csv", f)
        d["unit"] = f"GL{m.group(1)}__rho{m.group(2)}"
        info.append(dict(file=os.path.relpath(f, frag_dir), rows=len(d),
                         md5=hashlib.md5(open(f, "rb").read()).hexdigest()))
        parts.append(d)
    df = pd.concat(parts, ignore_index=True)
    dup = df.duplicated(KEY, keep=False)
    return df, info, int(dup.sum())


def summ(df):
    g = df.groupby(["target", "form", "estimator", "lambda_rule", "interval", "fpc", "G_L"])
    s = g.coverage.agg(n_cells="size", cov_min="min", cov_q25=lambda x: x.quantile(.25),
                       cov_median="median", cov_q75=lambda x: x.quantile(.75), cov_max="max")
    s["mc_se_mean"] = g.mc_se.mean()
    s["width_ratio_median"] = g.width_ratio.median()
    return s.reset_index()


def sel(df, **kw):
    m = np.ones(len(df), bool)
    for k, v in kw.items():
        m &= df[k].isin(v).to_numpy() if isinstance(v, (list, tuple)) else (df[k] == v).to_numpy()
    return df[m]


def numbers(df):
    rows = []

    def add(name, value, definition, n=None):
        rows.append(dict(name=name, value=float(value) if value is not None else np.nan,
                         n_cells=n, definition=definition))

    sup = sel(df, target="super", form="complement")
    des = sel(df, target="design")
    # ---- Q1.1 ----
    for est, rule in (("ppi", "c_crossfit"), ("ppi", "a_b1"), ("ppi", "b_cluster"), ("classical", "none")):
        for iv in ("CR1_t", "CR2_bm"):
            for lab, gl in (("GLge6", [6, 8, 12, 20]), ("GL4", [4])):
                x = sel(sup, estimator=est, lambda_rule=rule, interval=iv, fpc=False, G_L=gl)
                for stat in ("min", "median", "max"):
                    add(f"Q1.1|super|{rule}|{iv}|{lab}|cov_{stat}", getattr(x.coverage, stat)(),
                        f"superpopulation, complement form, {est} rule {rule}, {iv}, no fpc, "
                        f"G_L {gl}; {stat} coverage over G_U, m, rho, r, estimand, population",
                        len(x))
    # ---- Q1.2 ----
    for rule in ("c_crossfit", "none"):
        for iv in ("boot_pct", "boot_t", "boot_bca", "CR1_t"):
            for gl in (4, 6, 8, 12, 20):
                x = sel(sup, lambda_rule=rule, interval=iv, fpc=False, G_L=gl)
                add(f"Q1.2|super|{rule}|{iv}|GL{gl}|cov_median", x.coverage.median(),
                    f"superpopulation, complement, rule {rule}, {iv}, G_L {gl}; median coverage "
                    "over G_U, m, rho, r, estimand, population", len(x))
                add(f"Q1.2|super|{rule}|{iv}|GL{gl}|cov_min", x.coverage.min(),
                    f"as above, minimum", len(x))
    # ---- Q1.3 ---- design, G_L = 12 of 24
    for form, iv, fpc in (("textbook", "textbook_t", True), ("textbook", "textbook_t", False),
                          ("complement", "CR1_t", False), ("complement", "CR1_t", True),
                          ("complement", "design_exact_t", False)):
        for rule in ("a_b1", "b_cluster", "c_crossfit", "none"):
            x = sel(des, form=form, interval=iv, fpc=fpc, lambda_rule=rule, G_L=12)
            for stat in ("min", "median", "max"):
                add(f"Q1.3|design|{form}|{iv}|fpc{int(fpc)}|{rule}|GL12|cov_{stat}",
                    getattr(x.coverage, stat)(),
                    f"design target (G = 24), G_L 12, {form} form, {iv}, fpc {fpc}, rule {rule}; "
                    f"{stat} coverage over m, rho, r, estimand, population", len(x))
    for form, iv, fpc in (("textbook", "textbook_t", True), ("complement", "CR1_t", False)):
        a = sel(des, form=form, interval=iv, fpc=fpc, lambda_rule="a_b1", G_L=12).set_index(
            ["m", "rho", "r", "estimand", "population"])
        c = sel(des, form=form, interval=iv, fpc=fpc, lambda_rule="c_crossfit", G_L=12).set_index(
            ["m", "rho", "r", "estimand", "population"])
        d = (c.coverage - a.coverage)
        w = (c.mean_width / a.mean_width)
        add(f"Q1.3|design|{form}|{iv}|fpc{int(fpc)}|GL12|crossfit_minus_b1_cov_maxabs",
            d.abs().max(), "max over cells of |coverage(c_crossfit) - coverage(a_b1)|", len(d))
        add(f"Q1.3|design|{form}|{iv}|fpc{int(fpc)}|GL12|crossfit_minus_b1_cov_median",
            d.median(), "median over cells of coverage(c_crossfit) - coverage(a_b1)", len(d))
        add(f"Q1.3|design|{form}|{iv}|fpc{int(fpc)}|GL12|crossfit_over_b1_width_median",
            w.median(), "median over cells of mean width(c_crossfit) / mean width(a_b1)", len(w))
    # ---- Q1.4 ---- super, WS vs t, by G_U
    for rule in ("c_crossfit", "a_b1"):
        for gu in sorted(sup.G_U.unique()):
            a = sel(sup, lambda_rule=rule, interval="CR1_t", fpc=False, G_U=gu).set_index(
                ["G_L", "m", "rho", "r", "estimand", "population"])
            b = sel(sup, lambda_rule=rule, interval="CR1_ws", fpc=False, G_U=gu).set_index(
                ["G_L", "m", "rho", "r", "estimand", "population"])
            wr = b.mean_width / a.mean_width
            add(f"Q1.4|super|{rule}|GU{gu}|ws_over_t_width_median", wr.median(),
                f"superpopulation, rule {rule}, G_U {gu}: median over cells of mean width CR1 "
                "with Welch-Satterthwaite df / CR1 with t_(G_L-1)", len(wr))
            add(f"Q1.4|super|{rule}|GU{gu}|ws_over_t_width_min", wr.min(), "as above, minimum",
                len(wr))
            add(f"Q1.4|super|{rule}|GU{gu}|ws_over_t_width_max", wr.max(), "as above, maximum",
                len(wr))
    # ---- Q1.5 ---- super, width ratio by (r, rho)
    for rr in sorted(sup.r.unique()):
        for rho in sorted(sup.rho.unique()):
            x = sel(sup, lambda_rule="c_crossfit", interval="CR1_t", fpc=False, r=rr, rho=rho)
            for stat in ("min", "median", "max"):
                add(f"Q1.5|super|c_crossfit|CR1_t|r{rr}|rho{rho}|width_ratio_{stat}",
                    getattr(x.width_ratio, stat)(),
                    f"superpopulation, rule c_crossfit, CR1_t: {stat} over G_L, G_U, m, estimand, "
                    f"population of PPI/classical mean width, r {rr}, rho {rho}", len(x))
    # ---- supplementary numbers quoted in the report ----
    z = sel(sup, r=0.0, estimator="ppi").drop_duplicates(
        ["G_L", "G_U", "m", "rho", "estimand", "population", "lambda_rule"])
    for rule in ("a_b1", "b_cluster", "c_crossfit"):
        x = sel(z, lambda_rule=rule)
        add(f"S|super|r0|{rule}|lambda_median_max", x.lambda_median.max(),
            f"superpopulation, r = 0, rule {rule}: max over cells of the median lambda", len(x))
        add(f"S|super|r0|{rule}|lambda_median_median", x.lambda_median.median(),
            f"superpopulation, r = 0, rule {rule}: median over cells of the median lambda", len(x))
        for gl in (4, 20):
            y = sel(x, G_L=gl)
            add(f"S|super|r0|{rule}|GL{gl}|lambda_median_median", y.lambda_median.median(),
                f"as above at G_L {gl}", len(y))
    for rule in ("none", "c_crossfit", "a_b1"):
        for est in ("mean", "theta3"):
            for pop in ("spot", "donor"):
                x = sel(sup, lambda_rule=rule, interval="CR1_t", fpc=False, estimand=est,
                        population=pop)
                add(f"S|super|{rule}|CR1_t|{est}|{pop}|cov_min", x.coverage.min(),
                    f"superpopulation, rule {rule}, CR1_t, {est} {pop}: minimum coverage over cells",
                    len(x))
                add(f"S|super|{rule}|CR1_t|{est}|{pop}|cov_median", x.coverage.median(),
                    "as above, median", len(x))
        x = sel(sup, lambda_rule=rule, interval="CR1_t", fpc=False, estimand="theta3",
                population="spot", rho=0.1, m=[1000, 5000])
        add(f"S|super|{rule}|CR1_t|theta3|spot|rho0.1|m1000+|cov_median", x.coverage.median(),
            "superpopulation, theta3 spot, rho 0.1, m 1000 and 5000: median coverage", len(x))
        add(f"S|super|{rule}|CR1_t|theta3|spot|rho0.1|m1000+|emp_sd_over_rms_se_median",
            (x.emp_sd / x.rms_se).median(),
            "as above: median of empirical sd of the estimate / root mean estimated variance",
            len(x))
    for rule in ("a_b1", "b_cluster", "c_crossfit"):
        for gl in (4, 6, 8, 12, 20):
            x = sel(sup, lambda_rule=rule, interval="CR1_t", fpc=False, G_L=gl, r=[0.3, 0.5, 0.8])
            add(f"S|super|{rule}|CR1_t|GL{gl}|r>0|width_ratio_median", x.width_ratio.median(),
                f"superpopulation, rule {rule}, CR1_t, G_L {gl}, r > 0: median PPI/classical width",
                len(x))
            x0 = sel(sup, lambda_rule=rule, interval="CR1_t", fpc=False, G_L=gl, r=0.0)
            add(f"S|super|{rule}|CR1_t|GL{gl}|r0|width_ratio_median", x0.width_ratio.median(),
                "as above at r = 0", len(x0))
    for rule in ("c_crossfit", "a_b1", "none"):
        for iv, fpc in (("CR1_ws", False), ("CR1_t", True)):
            for gl in (4, 6, 8, 12, 20):
                x = sel(sup, lambda_rule=rule, interval=iv, fpc=fpc, G_L=gl)
                add(f"S|super|{rule}|{iv}|fpc{int(fpc)}|GL{gl}|cov_median", x.coverage.median(),
                    f"superpopulation, rule {rule}, {iv}, fpc {fpc}, G_L {gl}: median coverage",
                    len(x))
    for form, iv, fpc in (("textbook", "textbook_t", True), ("complement", "CR1_t", False),
                          ("complement", "CR1_t", True), ("textbook", "boot_pct", False),
                          ("textbook", "boot_t", False)):
        for rule in ("none", "a_b1", "b_cluster", "c_crossfit"):
            for gl in (4, 6, 8, 12, 20):
                x = sel(des, form=form, interval=iv, fpc=fpc, lambda_rule=rule, G_L=gl)
                add(f"S|design|{form}|{iv}|fpc{int(fpc)}|{rule}|GL{gl}|cov_median",
                    x.coverage.median(), f"design, {form}, {iv}, fpc {fpc}, rule {rule}, G_L {gl}: "
                    "median coverage over m, rho, r, estimand, population", len(x))
                add(f"S|design|{form}|{iv}|fpc{int(fpc)}|{rule}|GL{gl}|cov_min",
                    x.coverage.min(), "as above, minimum", len(x))
    x = sel(des, form="textbook", interval="textbook_t", fpc=True, lambda_rule="none")
    for (est, pop), y in x.groupby(["estimand", "population"]):
        add(f"S|design|textbook|classical|{est}|{pop}|cov_min", y.coverage.min(),
            f"design, textbook fpc, classical, {est} {pop}: minimum coverage", len(y))
        add(f"S|design|textbook|classical|{est}|{pop}|cov_median", y.coverage.median(),
            "as above, median", len(y))
    for rule in ("a_b1", "c_crossfit"):
        x = sel(des, form="textbook", interval="textbook_t", fpc=True, lambda_rule=rule,
                r=[0.3, 0.5, 0.8])
        add(f"S|design|textbook|{rule}|r>0|width_ratio_median", x.width_ratio.median(),
            f"design, textbook fpc, rule {rule}, r > 0: median PPI/classical width", len(x))
    return pd.DataFrame(rows)


def sim_acceptance(df):
    rows = []
    # r = 0: lambda within 0.05 of 0 under every rule
    z = sel(df, r=0.0, estimator="ppi")
    # Scored on the superpopulation arm, where an independent predictor has population lambda 0.
    # In the design arm the fixed 24-donor population has a non-zero finite-population covariance
    # between y and the independent predictor, so its lambda is not expected to be 0; reported.
    for tgt in ("super", "design"):
        for rule in ("a_b1", "b_cluster", "c_crossfit"):
            x = sel(z, lambda_rule=rule, target=tgt).drop_duplicates(
                ["G_L", "G_U", "m", "rho", "estimand", "population", "form"])
            for stat in ("lambda_median", "lambda_mean"):
                v = float(x[stat].max())
                rows.append(dict(part="3_sim_r0_lambda" + ("" if tgt == "super" else "_reported"),
                                 check=f"r = 0, {tgt} target: {stat} within 0.05 of 0, rule {rule}",
                                 statistic=f"max over cells of {stat}", value=v,
                                 tol=0.05 if tgt == "super" else np.nan,
                                 passed=bool(v <= 0.05) if tgt == "super" else True,
                                 detail=f"{len(x)} cells (G_L x G_U x m x rho x estimand x "
                                        "population x form)"
                                        + ("" if tgt == "super" else "; reported, not scored")))
    # r = 0 band, scoped per addendum 1 section 1 item 2
    scoped = [("CR2_bm", None), ("CR1_t", [6, 8, 12, 20]), ("boot_t", None),
              ("textbook_t", None)]
    for iv, gls in scoped:
        x = sel(z, interval=iv, fpc=(iv == "textbook_t"))
        if iv == "textbook_t":
            x = sel(z, interval=iv, fpc=True)
        if gls is not None:
            x = sel(x, G_L=gls)
        if iv in ("CR1_t", "CR2_bm", "boot_t"):
            x = x[x.target == "super"]
        inside = ((x.coverage >= 0.89) & (x.coverage <= 0.91))
        within_mc = ((x.coverage - NOM).abs() <= 0.01 + 2 * x.mc_se)
        rows.append(dict(part="3_sim_r0_band", check=f"r = 0: coverage in [0.89, 0.91], {iv}"
                         + (f" at G_L {gls}" if gls else " at every G_L"),
                         statistic="fraction of cells inside the band", value=float(inside.mean()),
                         tol=np.nan, passed=bool(inside.all()),
                         detail=f"{len(x)} cells; coverage min {x.coverage.min():.4f} max "
                                f"{x.coverage.max():.4f}; fraction within the band widened by "
                                f"2 MC se {within_mc.mean():.4f}; mean MC se "
                                f"{x.mc_se.mean():.4f}; "
                                + ("design target, textbook form, fpc" if iv == "textbook_t"
                                   else "superpopulation target")))
    # G_L = 20, m = 200: variance variants within 0.02 of each other
    for tgt, ivs in (("super", ["CR1_t", "CR2_bm", "CR1_ws", "CR2_ws"]),
                     ("design", ["CR1_t", "CR2_bm"])):
        x = sel(df, target=tgt, G_L=20, m=200, interval=ivs, fpc=False)
        sp = x.groupby(["G_U", "rho", "r", "estimand", "population", "form", "lambda_rule"]
                       ).coverage.agg(lambda s: s.max() - s.min())
        rows.append(dict(part="4_sim_GL20_m200", check=f"G_L = 20, m = 200: analytic variance "
                         f"variants {ivs} within 0.02 coverage of each other ({tgt})",
                         statistic="max over cells of the coverage spread", value=float(sp.max()),
                         tol=0.02, passed=bool(sp.max() <= 0.02), detail=f"{len(sp)} cells"))
        xb = sel(df, target=tgt, G_L=20, m=200, fpc=False,
                 interval=ivs + ["boot_pct", "boot_t", "boot_bca"])
        spb = xb.groupby(["G_U", "rho", "r", "estimand", "population", "form", "lambda_rule"]
                         ).coverage.agg(lambda s: s.max() - s.min())
        rows.append(dict(part="4_sim_GL20_m200", check="as above including the three "
                         f"bootstraps ({tgt})", statistic="max over cells of the coverage spread",
                         value=float(spb.max()), tol=0.02, passed=bool(spb.max() <= 0.02),
                         detail=f"{len(spb)} cells"))
    return rows


def figure(S, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    try:
        from figure_style_shim import apply  # optional
        apply()
    except Exception:
        pass
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
    specs = {
        "super": [("complement", "CR1_t", False, "CR1, $t_{G_L-1}$", "#1f4e79"),
                  ("complement", "CR2_bm", False, "CR2, Bell-McCaffrey df (identical to CR1 at equal cluster sizes)", "#6fa8dc"),
                  ("complement", "boot_pct", False, "percentile bootstrap", "#b45f06"),
                  ("complement", "boot_t", False, "bootstrap-$t$", "#38761d"),
                  ("complement", "boot_bca", False, "BCa", "#999999")],
        "design": [("textbook", "textbook_t", True, "textbook, fpc, $t_{n_L-1}$", "#1f4e79"),
                   ("complement", "CR1_t", False, "complement, CR1, no fpc (B1)", "#cc4125"),
                   ("complement", "CR1_t", True, "complement, CR1, fpc", "#e69138"),
                   ("textbook", "boot_pct", False, "textbook, percentile bootstrap", "#b45f06")],
    }
    titles = {"super": "Superpopulation target (fresh donors)",
              "design": "Design-based target (24 fixed donors)"}
    for ax, tgt in zip(axes, ("super", "design")):
        for form, iv, fpc, lab, col in specs[tgt]:
            x = S[(S.target == tgt) & (S.form == form) & (S.interval == iv) & (S.fpc == fpc)
                  & (S.lambda_rule == "c_crossfit")].sort_values("G_L")
            if x.empty:
                continue
            ax.fill_between(x.G_L, x.cov_q25, x.cov_q75, color=col, alpha=0.18, lw=0)
            ax.plot(x.G_L, x.cov_median, "-o", color=col, ms=3.5, lw=1.4, label=lab)
        ax.axhline(NOM, color="black", lw=0.7, ls="--")
        ax.set_xticks([4, 6, 8, 12, 20])
        ax.set_xlabel("labelled donors $G_L$")
        ax.set_title(titles[tgt], loc="left", fontsize=8)
        ax.legend(frameon=False, fontsize=6, loc="lower right")
        ax.margins(x=0.04)
    axes[0].set_ylabel("coverage of 90% interval")
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    return fig


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--frag-dir", required=True)
    p.add_argument("--acc-part12", required=True)
    p.add_argument("--out-dir", required=True)
    a = p.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    df, info, ncol = load(a.frag_dir)
    rep = dict(fragments=info, n_fragments=len(info), n_rows=len(df), key=KEY,
               n_key_collisions=ncol, n_reps_values=sorted(df.n_reps.unique().tolist()),
               n_nonfinite_total=int(df.n_nonfinite.sum()))
    with open(f"{a.out_dir}/q1_merge_report.json", "w") as fh:
        json.dump(rep, fh, indent=1)
    assert ncol == 0, f"{ncol} colliding rows"
    S = summ(df)
    S.to_csv(f"{a.out_dir}/q1_coverage_by_G.csv", index=False)
    acc = pd.read_csv(a.acc_part12)
    acc = pd.concat([acc, pd.DataFrame(sim_acceptance(df))], ignore_index=True)
    acc.to_csv(f"{a.out_dir}/q1_acceptance.csv", index=False)
    numbers(df).to_csv(f"{a.out_dir}/q1_report_numbers.csv", index=False)
    figure(S, f"{a.out_dir}/fig_q1_coverage_by_G.png")
    df.to_csv(f"{a.out_dir}/q1_sim_coverage.csv", index=False)
    print(json.dumps({k: v for k, v in rep.items() if k != "fragments"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
