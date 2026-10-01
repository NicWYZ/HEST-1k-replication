#!/usr/bin/env python
"""Round 4, conformal track, stage C1: merge the nine K fragments, the acceptance table and the
report numbers.

docs/round4_conf_plan.md section 4 (C1 acceptance and predictions) and section 10 item 1
(addendum 1: no-donor-effect acceptance against each method's own expected coverage, with the
literal reading beside it).

Inputs: results/round4/conformal/C1_testbed/frag_K??/<run>/c1_grid__K??__<tag>.csv and
results/round4/conformal/C1_testbed/c1_ghcp_reproduction.csv. Outputs in
results/round4/conformal/C1_testbed/: c1_grid.csv, c1_acceptance.csv, c1_report_numbers.csv.

--no-ghcp writes only the non-GHCP acceptance rows; it exists so that the merge can be checked
before the GHCP reproduction has passed, when no GHCP number may be read.
"""
import argparse
import glob
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

KEY = ["cell_id", "alpha", "method", "o"]
GHCP = ("ghcp", "ghcp_noad", "ghcp_r05", "ghcp_r05code")


def merge(root):
    files = sorted(glob.glob(f"{root}/frag_K??/*/c1_grid__K??__*.csv"))
    G = pd.concat([pd.read_csv(f).assign(source=os.path.relpath(f, root)) for f in files],
                  ignore_index=True)
    d = G[G.duplicated(KEY, keep=False)]
    vals = [c for c in G.columns if c not in KEY + ["source"]]
    clash = 0
    for _, g in d.groupby(KEY):
        if not g[vals].round(15).nunique(dropna=False).le(1).all():
            clash += 1
    G = G.drop_duplicates(KEY).sort_values(["K", "cell_id", "alpha", "method", "o"]).reset_index(drop=True)
    return G, files, len(d), clash


def own_expected(m, K, a, o, N):
    """Coverage each method is built to have when there is no donor effect (addendum 1 item 1.1)."""
    if m == "pooled":
        return 1 - a
    if m == "hcp":
        return 1.0 if K + 1 < 1 / a - 1e-12 else min(1.0, (1 - a) * (K + 1) / K)
    if m == "one_per":
        return 1.0 if K + 1 < 1 / a - 1e-12 else math.ceil((K + 1) * (1 - a) - 1e-9) / (K + 1)
    if m == "within":
        n1 = o - o // 2
        return 1.0 if n1 + 1 < 1 / a - 1e-12 else math.ceil((n1 + 1) * (1 - a) - 1e-9) / (n1 + 1)
    if m in ("ghcp", "ghcp_noad") and N not in ("unequal", "data"):
        # equal sizes, eta = 0: |S_cal| = K - 1, M = K, test mass at +inf (N - o)/(K (N - m))
        n = int(N)
        mm = o // 2 if m == "ghcp" else 0
        inf = (n - o) / (K * (n - mm))
        return 1.0 if inf > a + 1e-12 else min(1.0, (1 - a) / (1 - inf))
    return float("nan")


def acceptance(G, a4b, with_ghcp, repro=None):
    rows = []

    def add(check, scope, stat, value, tol, passed, note=""):
        rows.append(dict(check=check, scope=scope, statistic=stat, value=value, tol=tol,
                         passed=None if passed is None else bool(passed), note=note))

    h = G[(G.method == "hcp") & (G.K == 50) & (G.share == 0.1)]
    for a in (0.1, 0.2):
        x = h[h.alpha == a]
        add("A1_hcp_K50_share0.1_literal", f"alpha {a}", "max |coverage - (1-alpha)|",
            float((x.coverage - (1 - a)).abs().max()), 0.01, (x.coverage - (1 - a)).abs().max() <= 0.01,
            f"n {len(x)}; coverage {x.coverage.min():.4f} to {x.coverage.max():.4f}")
        lev = (1 - a) * 51 / 50
        add("A1_hcp_K50_share0.1_own_level", f"alpha {a}", "max |coverage - (1-alpha)(K+1)/K|",
            float((x.coverage - lev).abs().max()), 0.01, (x.coverage - lev).abs().max() <= 0.01,
            f"own calibration level {lev:.4f}")
    z = G[(G.share == 0) & (G.tau == 0)]
    if not with_ghcp:
        z = z[~z.method.isin(GHCP)]
    for m, g in z.groupby("method"):
        lit = (g.coverage - (1 - g.alpha)).abs()
        e = np.array([own_expected(m, r.K, r.alpha, r.o, r.N) for r in g.itertuples()])
        own = np.abs(g.coverage.values - e)
        ok_e = ~np.isnan(e)
        add(f"A2_no_donor_effect_literal_{m}", "share 0, tau 0", "max |coverage - (1-alpha)|",
            float(lit.max()), 0.01, lit.max() <= 0.01, f"n {len(g)}")
        if ok_e.any():
            tol = np.maximum(0.01, 3 * g.coverage_mcse.values[ok_e])
            add(f"A2_no_donor_effect_own_{m}", "share 0, tau 0", "max |coverage - own expected|",
                float(own[ok_e].max()), 0.01, bool((own[ok_e] <= tol).all()),
                f"n {int(ok_e.sum())}; tolerance max(0.01, 3 MCSE); rows above tolerance "
                f"{int((own[ok_e] > tol).sum())}")
        else:
            add(f"A2_no_donor_effect_own_{m}", "share 0, tau 0", "not defined", float("nan"), 0.01,
                None, "no closed-form expected coverage for this method; literal reading only")
    p = z[z.method == "pooled"]
    add("A2_pooled_price_no_donor_effect", "share 0, tau 0", "max |price - 1|",
        float((p.price - 1).abs().max()), 0.02, (p.price - 1).abs().max() <= 0.02, f"n {len(p)}")
    hh = G[G.method == "hcp"]
    expi = hh.K + 1 < 1 / hh.alpha - 1e-12
    bad = ~(((hh.frac_infinite == 1) & expi) | ((hh.frac_infinite == 0) & ~expi))
    add("A3_hcp_infinite_iff_K+1_lt_1/alpha", "all hcp rows", "rows violating", int(bad.sum()), 0,
        bad.sum() == 0, f"n {len(hh)}")
    s = G[(G.gen == "semireal") & (G.K == 10) & (G.alpha == 0.1)]
    ref_c = float(a4b.loc[(a4b.metric == "coverage_mean") & (a4b.scope == "donor_set=24 arm=K10 method=hcp"), "value"].iloc[0])
    ref_w = float(a4b.loc[(a4b.metric == "width_ratio_over_pooled") & (a4b.scope.str.contains("method=hcp")) & (a4b.scope.str.contains("donor_set=24")), "value"].iloc[0])
    for N in ("data", "500"):
        t = s[s.N.astype(str) == N].set_index("method")
        cv = float(t.loc["hcp", "coverage"])
        wr = float(t.loc["hcp", "halfwidth_mean"] / t.loc["pooled", "halfwidth_mean"])
        prim = N == "data"
        add(f"A4_semireal_K10_hcp_coverage_N{N}", "primary (CCRCC spot counts)" if prim else "secondary (N 500)",
            "|coverage - A4b|", abs(cv - ref_c), 0.02, abs(cv - ref_c) <= 0.02,
            f"semireal {cv:.4f}, A4b {ref_c:.4f}")
        add(f"A4_semireal_K10_width_ratio_N{N}", "primary (CCRCC spot counts)" if prim else "secondary (N 500)",
            "|hcp/pooled half-width - A4b|", abs(wr - ref_w), 0.15, abs(wr - ref_w) <= 0.15,
            f"semireal {wr:.4f}, A4b {ref_w:.4f}")
    if repro is not None:
        add("A5_ghcp_reproduction", "c1_ghcp_reproduction.csv", "rows outside MC error",
            int((~repro.within_mc).sum()), 0, bool(repro.within_mc.all()), f"n {len(repro)}")
    return pd.DataFrame(rows)


def report_numbers(G):
    R = []

    def add(name, value, note=""):
        R.append(dict(name=name, value=value, note=note))
    a = G[(G.alpha == 0.1) & (G.gen != "semireal") & (G.share > 0)]
    h = a[a.method == "hcp"]
    for K in (10, 25, 50):
        for gen in ("normal", "t3"):
            x = h[(h.K == K) & (h.gen == gen)]
            add(f"C1.1_hcp_price_K{K}_{gen}_min", float(x.price.min()))
            add(f"C1.1_hcp_price_K{K}_{gen}_max", float(x.price.max()))
            add(f"C1.1_hcp_price_K{K}_{gen}_mean", float(x.price.mean()))
    hf = G[(G.method == "hcp") & (G.frac_infinite == 0) & (G.gen != "semireal")]
    add("C1.1_hcp_min_coverage_minus_nominal_finite_cells", float((hf.coverage - (1 - hf.alpha)).min()),
        f"n {len(hf)}")
    add("C1.1_hcp_cells_below_nominal_by_more_than_3mcse",
        int(((1 - hf.alpha) - hf.coverage > 3 * hf.coverage_mcse).sum()), f"n {len(hf)}")
    p = a[a.method == "pooled"]
    for sh in (0.1, 0.3, 0.5):
        x = p[p.share == sh]
        add(f"C1.2_pooled_coverage_share{sh}_mean", float(x.coverage.mean()), f"n {len(x)}")
        add(f"C1.2_pooled_coverage_share{sh}_min", float(x.coverage.min()))
        add(f"C1.2_pooled_coverage_share{sh}_max", float(x.coverage.max()))
        byK = x.groupby("K").coverage.mean()
        add(f"C1.2_pooled_coverage_share{sh}_range_over_K", float(byK.max() - byK.min()))
        add(f"C1.2_pooled_coverage_share{sh}_spearman_K", float(stats.spearmanr(byK.index, byK.values)[0]))
    fin = a[(a.frac_infinite == 0)]
    o1 = fin[fin.method == "one_per"].set_index("cell_id")
    hc = fin[fin.method == "hcp"].set_index("cell_id")
    dw = fin[fin.method == "dwr_rep"].set_index("cell_id")
    j = o1[["coverage", "coverage_sd"]].join(hc[["coverage", "coverage_sd"]], rsuffix="_hcp", how="inner")
    add("C1.3_one_per_coverage_mean", float(j.coverage.mean()), f"cells {len(j)}")
    add("C1.3_sd_ratio_one_per_over_hcp_median", float((j.coverage_sd / j.coverage_sd_hcp).median()))
    add("C1.3_sd_ratio_one_per_over_hcp_min", float((j.coverage_sd / j.coverage_sd_hcp).min()))
    add("C1.3_sd_ratio_one_per_over_hcp_max", float((j.coverage_sd / j.coverage_sd_hcp).max()))
    j2 = o1[["coverage", "coverage_sd"]].join(dw[["coverage", "coverage_sd"]], rsuffix="_dwr", how="inner")
    add("C1.3_dwr_rep_coverage_mean", float(j2.coverage_dwr.mean()), f"cells {len(j2)}")
    add("C1.3_sd_ratio_dwr_over_one_per_median", float((j2.coverage_sd_dwr / j2.coverage_sd).median()))
    gh = a[a.method == "ghcp"]
    for o in (5, 25, 100):
        x = gh[gh.o == o]
        add(f"C1.4_ghcp_o{o}_coverage_min", float(x.coverage.min()), f"n {len(x)}")
        add(f"C1.4_ghcp_o{o}_cells_below_nominal_3mcse", int((0.9 - x.coverage > 3 * x.coverage_mcse).sum()))
        k10 = x[x.K == 10]
        add(f"C1.4_ghcp_o{o}_K10_price_median", float(k10.price.median()))
        add(f"C1.4_ghcp_o{o}_K10_price_max", float(k10.price.max()))
    w = a[a.method == "within"].set_index(["cell_id", "o"])
    g2 = gh.set_index(["cell_id", "o"])
    jj = w[["halfwidth_mean", "frac_infinite"]].join(g2[["halfwidth_mean"]], rsuffix="_ghcp", how="inner")
    for o in (5, 10, 25, 50, 100):
        x = jj.xs(o, level="o")
        xf = x[x.frac_infinite == 0]
        add(f"C1.4_within_over_ghcp_halfwidth_o{o}_median",
            float((xf.halfwidth_mean / xf.halfwidth_mean_ghcp).median()) if len(xf) else float("inf"),
            f"finite within cells {len(xf)} of {len(x)}")
    # C1.5: steps in the (K, o) price map, HCP at o = 0 and GHCP at o > 0
    steps = []
    for cid, g in a.groupby("cell_id"):
        hp = g[g.method == "hcp"].price
        seq = [float(hp.iloc[0]) if len(hp) else np.nan] + [
            float(g[(g.method == "ghcp") & (g.o == o)].price.iloc[0]) for o in (5, 10, 25, 50, 100)]
        for i, (o0, o1_) in enumerate(zip((0, 5, 10, 25, 50), (5, 10, 25, 50, 100))):
            if np.isfinite(seq[i]) and np.isfinite(seq[i + 1]):
                steps.append(dict(cell_id=cid, K=g.K.iloc[0], step=f"{o0}->{o1_}", drop=seq[i] - seq[i + 1]))
    S = pd.DataFrame(steps)
    big = S.loc[S.groupby("cell_id").drop.idxmax()]
    add("C1.5_cells_where_hcp0_to_ghcp5_is_largest_step", int((big.step == "0->5").sum()), f"of {len(big)} cells with all steps finite")
    for st, c in big.step.value_counts().items():
        add(f"C1.5_largest_step_count_{st}", int(c))
    return pd.DataFrame(R), S


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--a4b", required=True)
    p.add_argument("--no-ghcp", action="store_true")
    a = p.parse_args(argv)
    G, files, ndup, clash = merge(a.root)
    a4b = pd.read_csv(a.a4b)
    repro_p = f"{a.root}/c1_ghcp_reproduction.csv"
    repro = pd.read_csv(repro_p) if (not a.no_ghcp and os.path.exists(repro_p)) else None
    acc = acceptance(G, a4b, with_ghcp=not a.no_ghcp, repro=repro)
    acc = pd.concat([pd.DataFrame([dict(check="M0_merge", scope=f"{len(files)} fragment files",
                                        statistic="duplicated keys / clashing keys",
                                        value=f"{ndup}/{clash}", tol=0, passed=clash == 0,
                                        note=f"cells {G.cell_id.nunique()}, rows {len(G)}")]), acc])
    if a.no_ghcp:
        acc.to_csv(f"{a.root}/c1_acceptance_nonghcp.csv", index=False)
        print(acc.to_string(index=False))
        return 0
    G.drop(columns=["source"]).to_csv(f"{a.root}/c1_grid.csv", index=False)
    acc.to_csv(f"{a.root}/c1_acceptance.csv", index=False)
    R, S = report_numbers(G)
    R.to_csv(f"{a.root}/c1_report_numbers.csv", index=False)
    S.to_csv(f"{a.root}/c1_price_steps.csv", index=False)
    print(acc.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
