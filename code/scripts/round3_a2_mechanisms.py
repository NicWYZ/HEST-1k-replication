#!/usr/bin/env python
"""Round 3, stage A2: the mechanism analyses that need a harness rerun.

Stage: A2, conditional coverage and the anatomy of failure
(round3_execution_plan.md sections 4.4 and 12.4; the Mechanisms track of section 12.8).

Reads what `code/scripts/round3_a0_harness.py` writes in its A2 modes, plus A1's own
committed tables, and produces the five A2 tables this track owns and the two A2 figures.
It fits nothing and re-splits nothing: every coverage number here was produced by the
harness.

INPUTS, under results/round3/A2_conditional unless stated
  a2_score_moments__<enc>__mech_{main,slideout}.parquet   A2c, per (fold, draw, unit, gene)
  a2_slidegene__<enc>__mech_{main,slideout}.parquet       A2f, per (fold, slide, gene)
  a2_slidegene__<enc>__{a2b,od}.parquet                   the A2b arms and A2d's new arm
  a2_strata__<enc>__mech_{main,slideout}.csv              A2a's two spot-level strata
  a2b_by_fold__<enc>__a2b.csv, a2b_cells__<enc>__a2b.csv  A2b per arm and per fold-draw
  results/round3/A1_coverage/a1_by_fold__<enc>__{main,slideout}.csv        observed coverage
  results/round3/A1_coverage/a1_calibration_units__<enc>__{main,slideout}.csv   K per fold

OUTPUTS, under results/round3/A2_conditional
  a2_score_moments__<enc>.parquet      the two moments invocations consolidated
  a2_slidegene__<enc>.parquet          the four anatomy invocations consolidated
  a2_unit_intervention.csv             A2b, three arms per fold and the per-task summary
  a2_coverage_vs_K.csv                 A2c, observed coverage against K and the share
  a2_simulated_coverage.csv            A2c, the location-shift simulation beside observed
  a2_level_scale.csv                   A2f, per slide and the two regressions
  a2_by_stratum__spot.csv              A2a, predicted-value decile and neoplastic tertile
  a2_prad_donor_sharing__arm.csv       A2d's new arm against A1's slide_out on PRAD
  fig_a2_anatomy.png, fig_a2_coverage_vs_K.png

THE BETWEEN-UNIT SHARE IS A TEST-LABEL DIAGNOSTIC. Section 12.9 item 4: with K = 1
calibration unit, which is most folds, the between-unit variance is not estimable from the
calibration scores alone, because one unit has no between-unit variance. It is therefore
computed over the K calibration units TOGETHER WITH THE TEST UNIT, whose scores use test
labels, and the same estimate drives the simulation. It has the standing section 4.4 gives
b_s: a diagnostic, not a method. Every table that carries it also carries the column
`uses_test_labels`.

Usage:
  round3_a2_mechanisms.py --stage tables    # on Longleaf, reads the parquets
  round3_a2_mechanisms.py --stage figures   # from the CSVs alone, runs anywhere
"""
import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys
import time
import zlib

import numpy as np
import pandas as pd

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
A1DIR = "results/round3/A1_coverage"
A2DIR = "results/round3/A2_conditional"
ENCODERS = ("hoptimus0", "uni_v2", "resnet50")
ALPHA = 0.10
NOMINAL = 1.0 - ALPHA
SCORE = "abs"

N_SIM = 1000                  # replicates per fold, section 12.4 A2c
SIM_MAX_N_PER_UNIT = 2000     # cap on simulated spots per calibration unit; recorded in
                              # the output and in the stage report as a reduction
MIN_SLIDE_SPOTS = 50          # the harness's own slide_ge_min_spots convention

# The three A2b arms and, for each, what differs from the arm above it. Written into
# a2_unit_intervention.csv so the difference list travels with the numbers.
A2B_DIFFERENCE = {
    "anchor_a1": "A1's own proper-training set and A1's full C_unit; nothing differs from "
                 "A1 except that the run is a rerun",
    "C_unit": "against anchor_a1: the proper-training set loses the carved blocks and "
              "their 2.5-pitch buffer, and C_unit is subsampled only if it is larger than "
              "C_block; nothing else differs",
    "C_block": "against C_unit: the SOURCE OF THE CALIBRATION SCORES only. Same T, same "
               "head, same scaler, same PCA, same E, same score, same alpha, same "
               "calibration spot count",
}


# ------------------------------------------------------------------ small helpers
def rp(p):
    return p if os.path.isabs(p) else f"{ROOT}/{p}"


def read_many(pattern, kind="csv"):
    """Concatenate every file matching `pattern`, recording which file each row came
    from. Returns an empty frame rather than raising when nothing matches, and prints the
    file list, because a silently missing encoder would shrink every table downstream."""
    import pyarrow.parquet as pq
    fs = sorted(glob.glob(rp(pattern)))
    if not fs:
        print(f"[read] NOTHING matched {pattern}", flush=True)
        return pd.DataFrame()
    out = []
    for f in fs:
        d = pq.read_table(f).to_pandas() if kind == "parquet" else pd.read_csv(f)
        d["_src"] = os.path.basename(f)
        out.append(d)
        print(f"[read] {os.path.basename(f)}: {len(d):,} rows", flush=True)
    return pd.concat(out, ignore_index=True)


def ols_shares(y, X, names):
    """OLS of y on X with an intercept. Returns the coefficients, their t statistics and
    two-sided p values, R^2, and each regressor's share of the variance of y.

    The share is beta_j * cov(x_j, y) / var(y), the covariance decomposition, so the
    shares sum to R^2 exactly. That is the decomposition section 4.4 asks for when it says
    "reporting the shares": it answers how much of the spread in coverage shortfall each
    of the level term and the scale term accounts for, and it does not require the two
    regressors to be uncorrelated.
    """
    from scipy import stats
    y = np.asarray(y, dtype=float)
    X = np.asarray(X, dtype=float)
    ok = np.isfinite(y) & np.isfinite(X).all(axis=1)
    y, X = y[ok], X[ok]
    n, k = X.shape
    if n < k + 3 or np.var(y) == 0:
        return None
    A = np.column_stack([np.ones(n), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ beta
    ssr = float(resid @ resid)
    sst = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ssr / sst if sst > 0 else np.nan
    dof = n - k - 1
    s2 = ssr / dof if dof > 0 else np.nan
    XtXinv = np.linalg.pinv(A.T @ A)
    se = np.sqrt(np.maximum(np.diag(XtXinv) * s2, 0))
    with np.errstate(divide="ignore", invalid="ignore"):
        tvals = beta / se
    pvals = 2 * stats.t.sf(np.abs(tvals), dof) if dof > 0 else np.full(k + 1, np.nan)
    vy = float(np.var(y, ddof=0))
    out = dict(n=n, r2=r2, intercept=float(beta[0]))
    for j, nm in enumerate(names):
        cov = float(np.cov(X[:, j], y, ddof=0)[0, 1])
        out[f"coef_{nm}"] = float(beta[j + 1])
        out[f"t_{nm}"] = float(tvals[j + 1])
        out[f"p_{nm}"] = float(pvals[j + 1])
        out[f"share_{nm}"] = float(beta[j + 1] * cov / vy) if vy > 0 else np.nan
    return out


# --------------------------------------------------------- A2c, moments to a share
def between_within(mom):
    """Between- and within-unit variance of the calibration score per (fold, gene).

    Computed over the K calibration units TOGETHER WITH the test unit, per section 12.9
    item 4, using the count/mean/variance moments the harness wrote. With n_k spots,
    mean m_k and population variance v_k in unit k and N = sum n_k:

        within  = sum_k n_k v_k / N
        between = sum_k n_k m_k^2 / N  -  ( sum_k n_k m_k / N )^2
        share   = between / (between + within)

    which is the exact decomposition of the pooled population variance, so `share` is the
    fraction of the score's total spread that sits between units rather than inside one.
    """
    d = mom.copy()
    d["nm"] = d["n"] * d["mean"]
    d["nm2"] = d["n"] * d["mean"] ** 2
    d["nv"] = d["n"] * d["variance"]
    keys = ["encoder", "task", "label_set", "design", "fold", "cal_draw", "gene"]
    g = d.groupby(keys, dropna=False).agg(
        N=("n", "sum"), snm=("nm", "sum"), snm2=("nm2", "sum"), snv=("nv", "sum"),
        n_units_total=("unit_id", "nunique"),
        calibration_unit=("calibration_unit", "first")).reset_index()
    kcal = (d[d["unit_role"] == "calibration"].groupby(keys, dropna=False)
            .agg(K=("unit_id", "nunique"), n_cal=("n", "sum")).reset_index())
    g = g.merge(kcal, on=keys, how="left")
    ntest = (d[d["unit_role"] == "test"].groupby(keys, dropna=False)["n"].sum()
             .rename("n_test").reset_index())
    g = g.merge(ntest, on=keys, how="left")
    mbar = g["snm"] / g["N"]
    g["within_var"] = g["snv"] / g["N"]
    g["between_var"] = (g["snm2"] / g["N"] - mbar ** 2).clip(lower=0.0)
    tot = g["between_var"] + g["within_var"]
    g["between_share"] = np.where(tot > 0, g["between_var"] / tot, np.nan)
    g["uses_test_labels"] = True
    return g.drop(columns=["snm", "snm2", "snv"])


def fold_level_share(pg):
    """One row per (encoder, task, design, fold): the median over genes and calibration
    draws of the share and of the two variances. Median, not mean, because the share is a
    ratio bounded in [0, 1] whose across-gene distribution is skewed on the folds where a
    handful of genes carry almost all the between-unit spread."""
    keys = ["encoder", "task", "label_set", "design", "fold"]
    return (pg.groupby(keys, dropna=False)
              .agg(K=("K", "median"), n_units_total=("n_units_total", "median"),
                   calibration_unit=("calibration_unit", "first"),
                   n_cal=("n_cal", "median"), n_test=("n_test", "median"),
                   between_share=("between_share", "median"),
                   between_share_q25=("between_share", lambda s: s.quantile(0.25)),
                   between_share_q75=("between_share", lambda s: s.quantile(0.75)),
                   between_var=("between_var", "median"),
                   within_var=("within_var", "median"),
                   n_genes=("gene", "nunique"),
                   n_cal_draws=("cal_draw", "nunique")).reset_index())


def a1_observed_coverage():
    """A1's committed per-fold coverage for the `abs` score. This is read, never
    recomputed: A1 is the published number these tables are set beside."""
    d = read_many(f"{A1DIR}/a1_by_fold__*__main.csv")
    e = read_many(f"{A1DIR}/a1_by_fold__*__slideout.csv")
    a = pd.concat([x for x in (d, e) if len(x)], ignore_index=True)
    a = a[(a["score"] == SCORE) & (a["encoder"].isin(ENCODERS))]
    return a.rename(columns={"coverage": "coverage_observed",
                             "width_mean": "width_observed"})[
        ["encoder", "task", "label_set", "design", "fold", "coverage_observed",
         "width_observed", "miss_above", "miss_below", "calibration_unit"]]


# ------------------------------------------------------- A2c, the simulation
def simulate_fold(sb2, sw2, n_per_unit, n_cal_units, seed, n_sim=N_SIM):
    """The location-shift simulation of section 12.4 A2c.

    Each unit k gets a mean mu_k ~ N(0, sb2); a spot in unit k has score mu_k + N(0, sw2).
    The K calibration units' scores are pooled and the conformal ceil((n+1)(1-alpha))/n
    order statistic taken, which is the quantile the harness itself uses. The test unit
    gets its own mu ~ N(0, sb2) from the same distribution.

    The test unit's coverage is then evaluated ANALYTICALLY as Phi((qhat - mu_test)/sw),
    the exact expected fraction of that unit's scores below qhat, rather than by drawing
    test points. The quantity is the same in expectation and carries no Monte Carlo noise
    from the test side, and it removes the largest cost in the loop.
    """
    from scipy.stats import norm
    rng = np.random.default_rng(seed)
    K = int(n_cal_units)
    sb, sw = float(np.sqrt(max(sb2, 0.0))), float(np.sqrt(max(sw2, 0.0)))
    if K < 1 or not np.isfinite(sb) or not np.isfinite(sw) or sw <= 0:
        return None
    ns = [int(min(max(n, 2), SIM_MAX_N_PER_UNIT)) for n in n_per_unit[:K]]
    while len(ns) < K:
        ns.append(ns[-1] if ns else 2)
    mu = rng.normal(0.0, sb, size=(n_sim, K))
    parts = [mu[:, [k]] + rng.normal(0.0, sw, size=(n_sim, ns[k])) for k in range(K)]
    S = np.concatenate(parts, axis=1)
    n_cal = S.shape[1]
    kq = int(np.ceil((n_cal + 1) * NOMINAL))
    if kq > n_cal:
        return dict(simulated_coverage_mean=np.nan, quantile_infinite=True,
                    n_cal_simulated=n_cal, n_sim=n_sim)
    qhat = np.partition(S, kq - 1, axis=1)[:, kq - 1]
    mu_t = rng.normal(0.0, sb, size=n_sim)
    cov = norm.cdf((qhat - mu_t) / sw)
    return dict(simulated_coverage_mean=float(cov.mean()),
                simulated_coverage_sd=float(cov.std(ddof=1)),
                simulated_coverage_q05=float(np.quantile(cov, 0.05)),
                simulated_coverage_q50=float(np.quantile(cov, 0.50)),
                simulated_coverage_q95=float(np.quantile(cov, 0.95)),
                quantile_infinite=False, n_cal_simulated=n_cal, n_sim=n_sim)


# ------------------------------------------------------ A2f, level against scale
def level_scale_rows(sg, group_name):
    """Per (encoder, task, design, fold, test slide), the four quantities of section 4.4,
    aggregated over genes.

    miss asymmetry a is formed from the SUMMED miss rates over genes, not from the mean of
    per-gene ratios, because a gene with no misses at all has an undefined ratio and
    averaging ratios would let the genes with one or two misses dominate.
    """
    d = sg[(sg["score"] == SCORE) & sg["slide_ge_min_spots"]].copy()
    if not len(d):
        return pd.DataFrame()
    d["abs_b_over_sy"] = np.where(d["s_y"] > 0, np.abs(d["b_s"]) / d["s_y"], np.nan)
    d["log_w_ratio"] = np.where((d["w_star"] > 0) & (d["w_hat"] > 0),
                                np.log(d["w_star"] / d["w_hat"]), np.nan)
    keys = ["encoder", "task", "label_set", "design", "arm", "fold", "slide"]
    g = d.groupby(keys, dropna=False).agg(
        n_genes=("gene", "nunique"), n_test=("n_test", "first"),
        coverage=("coverage", "mean"), width_mean=("width_mean", "mean"),
        sum_miss_above=("miss_above", "sum"), sum_miss_below=("miss_below", "sum"),
        abs_b_over_sy=("abs_b_over_sy", "mean"),
        b_over_sy_signed=("b_s", "mean"),
        log_w_ratio=("log_w_ratio", "mean"),
        w_star_over_w_hat=("w_star", "mean"),
        w_hat=("w_hat", "mean"),
        calibration_unit=("calibration_unit", "first")).reset_index()
    tot = g["sum_miss_above"] + g["sum_miss_below"]
    g["miss_asymmetry"] = np.where(tot > 0,
                                   (g["sum_miss_above"] - g["sum_miss_below"]) / tot,
                                   np.nan)
    g["w_star_over_w_hat"] = np.where(g["w_hat"] > 0,
                                      g["w_star_over_w_hat"] / g["w_hat"], np.nan)
    g["shortfall"] = NOMINAL - g["coverage"]
    g["group"] = group_name
    g["uses_test_labels"] = True
    return g


def level_scale_regressions(rows):
    """The section 4.4 regression of coverage shortfall on |b_s|/s_y and log(w*/w-hat),
    run separately for each group, which is what section 12.4 A2f means by "separately for
    block-calibrated and unit-calibrated folds"."""
    out = []
    for grp, d in rows.groupby("group", dropna=False):
        r = ols_shares(d["shortfall"].values,
                       np.column_stack([d["abs_b_over_sy"].values,
                                        d["log_w_ratio"].values]),
                       ["level", "scale"])
        if r is None:
            out.append(dict(scope="regression", group=grp, n=len(d),
                            note="too few finite slides to fit"))
            continue
        r.update(scope="regression", group=grp,
                 n_tasks=d["task"].nunique(), n_folds=d["fold"].nunique(),
                 mean_shortfall=float(d["shortfall"].mean()),
                 mean_abs_b_over_sy=float(d["abs_b_over_sy"].mean()),
                 mean_miss_asymmetry=float(d["miss_asymmetry"].mean()),
                 mean_w_star_over_w_hat=float(d["w_star_over_w_hat"].mean()),
                 uses_test_labels=True)
        out.append(r)
    return pd.DataFrame(out)


# =============================================================== the tables stage
def stage_tables(args):
    out = rp(A2DIR)
    os.makedirs(out, exist_ok=True)
    written = []

    # ---------- consolidate the harness's per-invocation parquets ----------
    import pyarrow as pa
    import pyarrow.parquet as pq
    mom_all, sg_all = [], []
    for enc in ENCODERS:
        m = read_many(f"{A2DIR}/a2_score_moments__{enc}__mech_*.parquet", "parquet")
        if len(m):
            m = m.drop(columns=["_src"])
            pq.write_table(pa.Table.from_pandas(m, preserve_index=False),
                           f"{out}/a2_score_moments__{enc}.parquet",
                           compression="snappy")
            print(f"[write] a2_score_moments__{enc}.parquet ({len(m):,} rows)", flush=True)
            mom_all.append(m)
        s = read_many(f"{A2DIR}/a2_slidegene__{enc}__*.parquet", "parquet")
        if len(s):
            s = s.drop(columns=["_src"])
            pq.write_table(pa.Table.from_pandas(s, preserve_index=False),
                           f"{out}/a2_slidegene__{enc}.parquet", compression="snappy")
            print(f"[write] a2_slidegene__{enc}.parquet ({len(s):,} rows)", flush=True)
            sg_all.append(s)
    mom = pd.concat(mom_all, ignore_index=True) if mom_all else pd.DataFrame()
    sg = pd.concat(sg_all, ignore_index=True) if sg_all else pd.DataFrame()

    obs = a1_observed_coverage()

    # ---------------------------------------------------------- A2b, the intervention
    a2b = read_many(f"{A2DIR}/a2b_by_fold__*__a2b.csv")
    cells = read_many(f"{A2DIR}/a2b_cells__*__a2b.csv")
    if len(a2b):
        d = a2b[a2b["score"] == SCORE]
        keys = ["encoder", "task", "label_set", "fold"]
        wide = d.pivot_table(index=keys, columns="arm",
                             values=["coverage", "width_mean", "n_T", "n_C"],
                             aggfunc="mean")
        wide.columns = [f"{a}__{b}" for a, b in wide.columns]
        wide = wide.reset_index()
        ref = obs[obs["design"] == "donor"][
            ["encoder", "task", "label_set", "fold", "coverage_observed",
             "width_observed"]]
        wide = wide.merge(ref, on=keys, how="left")
        wide["anchor_minus_a1"] = (wide.get("coverage__anchor_a1")
                                   - wide["coverage_observed"])
        wide["cov_unit_minus_block"] = (wide.get("coverage__C_unit")
                                        - wide.get("coverage__C_block"))
        wide["width_unit_minus_block"] = (wide.get("width_mean__C_unit")
                                          - wide.get("width_mean__C_block"))
        wide["unit_minus_a1"] = wide.get("coverage__C_unit") - wide["coverage_observed"]
        wide["block_minus_a1"] = wide.get("coverage__C_block") - wide["coverage_observed"]
        wide["scope"] = "fold"
        agg = (wide.groupby(["encoder", "task", "label_set"], dropna=False)
               .agg(n_folds=("fold", "nunique"),
                    coverage__anchor_a1=("coverage__anchor_a1", "mean"),
                    coverage__C_unit=("coverage__C_unit", "mean"),
                    coverage__C_block=("coverage__C_block", "mean"),
                    width_mean__C_unit=("width_mean__C_unit", "mean"),
                    width_mean__C_block=("width_mean__C_block", "mean"),
                    coverage_observed=("coverage_observed", "mean"),
                    anchor_minus_a1_max_abs=("anchor_minus_a1",
                                             lambda s: s.abs().max()),
                    cov_unit_minus_block=("cov_unit_minus_block", "mean"),
                    cov_unit_minus_block_sd=("cov_unit_minus_block", "std"),
                    width_unit_minus_block=("width_unit_minus_block", "mean"),
                    width_unit_minus_block_sd=("width_unit_minus_block", "std"),
                    unit_minus_a1=("unit_minus_a1", "mean"),
                    block_minus_a1=("block_minus_a1", "mean")).reset_index())
        agg["scope"] = "task"
        ui = pd.concat([wide, agg], ignore_index=True)
        ui["difference_list_C_unit_vs_C_block"] = A2B_DIFFERENCE["C_block"]
        ui["difference_list_anchor_vs_C_unit"] = A2B_DIFFERENCE["C_unit"]
        ui["score"] = SCORE
        ui.to_csv(f"{out}/a2_unit_intervention.csv", index=False)
        written.append("a2_unit_intervention.csv")
        print(f"[write] a2_unit_intervention.csv ({len(ui)} rows)", flush=True)
    if len(cells):
        dropped = cells[cells["status"] != "ok"]
        dropped.to_csv(f"{out}/a2_dropped_folds.csv", index=False)
        written.append("a2_dropped_folds.csv")
        print(f"[write] a2_dropped_folds.csv ({len(dropped)} dropped fold-draw cells)",
              flush=True)

    # ------------------------------------------------- A2c, coverage against K
    if len(mom):
        pergene = between_within(mom)
        fold = fold_level_share(pergene)
        cvk = fold.merge(obs, on=["encoder", "task", "label_set", "design", "fold"],
                         how="left", suffixes=("", "_a1"))
        cvk["block_fold"] = cvk["calibration_unit"].astype(str).eq("block")
        cvk["shortfall"] = NOMINAL - cvk["coverage_observed"]
        cvk["score"] = SCORE
        cvk["uses_test_labels"] = True
        cvk.to_csv(f"{out}/a2_coverage_vs_K.csv", index=False)
        written.append("a2_coverage_vs_K.csv")
        print(f"[write] a2_coverage_vs_K.csv ({len(cvk)} folds)", flush=True)

        # ------------------------------------------ A2c, the location-shift simulation
        nper = (pergene.merge(
            mom[mom["unit_role"] == "calibration"]
            .groupby(["encoder", "task", "label_set", "design", "fold", "cal_draw",
                      "unit_id"], dropna=False)["n"].first().reset_index()
            .groupby(["encoder", "task", "label_set", "design", "fold"], dropna=False)["n"]
            .apply(list).rename("unit_sizes").reset_index(),
            on=["encoder", "task", "label_set", "design", "fold"], how="left"))
        sizes = nper.groupby(["encoder", "task", "label_set", "design",
                              "fold"], dropna=False)["unit_sizes"].first()
        rows = []
        for _, r in cvk.iterrows():
            key = (r["encoder"], r["task"], r["label_set"], r["design"], r["fold"])
            ns = sizes.get(key, [])
            seed = zlib.crc32("|".join(str(x) for x in key).encode())
            s = simulate_fold(r["between_var"], r["within_var"], list(ns),
                              int(r["K"]) if np.isfinite(r["K"]) else 0, seed)
            base = dict(encoder=r["encoder"], task=r["task"],
                        label_set=r["label_set"], design=r["design"], fold=r["fold"],
                        K=r["K"], calibration_unit=r["calibration_unit"],
                        block_fold=r["block_fold"],
                        between_var=r["between_var"], within_var=r["within_var"],
                        between_share=r["between_share"],
                        coverage_observed=r["coverage_observed"],
                        n_cal_per_unit_cap=SIM_MAX_N_PER_UNIT,
                        uses_test_labels=True, scope="fold")
            base.update(s or dict(simulated_coverage_mean=np.nan,
                                  note="not simulable: K<1 or a non-finite variance"))
            rows.append(base)
        sim = pd.DataFrame(rows)
        sim["observed_minus_simulated"] = (sim["coverage_observed"]
                                           - sim["simulated_coverage_mean"])
        pooled = (sim.groupby(["K", "block_fold"], dropna=False)
                  .agg(n_folds=("fold", "count"),
                       coverage_observed=("coverage_observed", "mean"),
                       coverage_observed_sd=("coverage_observed", "std"),
                       simulated_coverage_mean=("simulated_coverage_mean", "mean"),
                       simulated_coverage_sd=("simulated_coverage_sd", "mean"),
                       observed_minus_simulated=("observed_minus_simulated", "mean"),
                       between_share=("between_share", "median")).reset_index())
        pooled["scope"] = "pooled_by_K"
        sim = pd.concat([sim, pooled], ignore_index=True)
        sim["n_sim_requested"] = N_SIM
        sim.to_csv(f"{out}/a2_simulated_coverage.csv", index=False)
        written.append("a2_simulated_coverage.csv")
        print(f"[write] a2_simulated_coverage.csv ({len(sim)} rows)", flush=True)

    # ------------------------------------------------- A2f, level against scale
    if len(sg):
        parts = []
        a1like = sg[sg["arm"] == "a1"]
        if len(a1like):
            blk = a1like["calibration_unit"].astype(str).eq("block")
            parts.append(level_scale_rows(a1like[~blk], "A1_unit_calibrated"))
            parts.append(level_scale_rows(a1like[blk], "A1_block_calibrated"))
        for arm in ("anchor_a1", "C_unit", "C_block"):
            a = sg[sg["arm"] == arm]
            if len(a):
                parts.append(level_scale_rows(a, f"A2b_{arm}"))
        rows = pd.concat([p for p in parts if len(p)], ignore_index=True)
        reg = level_scale_regressions(rows)
        rows["scope"] = "slide"
        ls = pd.concat([rows, reg], ignore_index=True)
        ls.to_csv(f"{out}/a2_level_scale.csv", index=False)
        written.append("a2_level_scale.csv")
        print(f"[write] a2_level_scale.csv ({len(rows)} slide rows, "
              f"{len(reg)} regressions)", flush=True)
        print(reg.round(4).to_string(index=False), flush=True)

        # ----------------------------------- A2d, PRAD's other-donor calibration arm
        od = sg[(sg["design"] == "slide_out_cal_other_donor") & (sg["task"] == "PRAD")]
        base = sg[(sg["design"] == "slide_out") & (sg["task"] == "PRAD")]
        if len(od):
            def perslide(d, arm):
                dd = d[(d["score"] == SCORE) & d["slide_ge_min_spots"]]
                return (dd.groupby(["encoder", "fold", "slide"], dropna=False)
                        .agg(coverage=("coverage", "mean"),
                             width_mean=("width_mean", "mean"),
                             n_cal_draws=("cal_draw", "nunique"),
                             n_genes=("gene", "nunique")).reset_index()
                        .assign(arm=arm))
            a = perslide(od, "slide_out_cal_other_donor")
            b = perslide(base, "slide_out") if len(base) else pd.DataFrame()
            pr = pd.concat([x for x in (a, b) if len(x)], ignore_index=True)
            if len(b):
                w = pr.pivot_table(index=["encoder", "fold", "slide"], columns="arm",
                                   values="coverage").reset_index()
                if "slide_out" in w.columns:
                    w["same_donor_minus_other_donor"] = (
                        w["slide_out"] - w["slide_out_cal_other_donor"])
                    w["scope"] = "paired_by_slide"
                    pr = pd.concat([pr.assign(scope="arm_by_slide"), w],
                                   ignore_index=True)
            pr["task"] = "PRAD"
            pr["difference_list"] = (
                "the two arms differ in whether the calibration slides share the test "
                "slide's donor; on PRAD they also differ in resolution class and in "
                "capture session, because the two donors do not share either")
            pr.to_csv(f"{out}/a2_prad_donor_sharing__arm.csv", index=False)
            written.append("a2_prad_donor_sharing__arm.csv")
            print(f"[write] a2_prad_donor_sharing__arm.csv ({len(pr)} rows)", flush=True)

    # ------------------------------------------------------ A2a, the spot strata
    st = read_many(f"{A2DIR}/a2_strata__*__mech_*.csv")
    if len(st):
        st = st.drop(columns=["_src"])
        st["scope"] = "fold"
        pooled = (st.groupby(["task", "label_set", "encoder", "design", "score",
                              "stratum_kind", "stratum_value"], dropna=False)
                  .agg(n_folds=("fold", "nunique"),
                       n_spot_gene=("n_spot_gene", "sum"),
                       n_covered=("n_covered", "sum"),
                       width_mean=("width_mean", "mean"),
                       pred_mean=("pred_mean", "mean")).reset_index())
        pooled["coverage"] = pooled["n_covered"] / pooled["n_spot_gene"]
        pooled["scope"] = "pooled_over_folds"
        allst = pd.concat([st, pooled], ignore_index=True)
        allst.to_csv(f"{out}/a2_by_stratum__spot.csv", index=False)
        written.append("a2_by_stratum__spot.csv")
        print(f"[write] a2_by_stratum__spot.csv ({len(allst)} rows)", flush=True)

    _provenance(out, written, args)
    return 0


# ================================================================ the figures stage
def _style():
    """The figure-style ladder applied without the kernel helper, so the script renders
    the same figure wherever it runs: three font sizes mapped to role, outward ticks, no
    legend frame, 300 dpi."""
    import matplotlib as mpl
    mpl.use("Agg")
    mpl.rcParams.update({
        "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
        "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
        "legend.fontsize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6,
        "axes.titlelocation": "left", "axes.titleweight": "normal",
        "axes.spines.top": False, "axes.spines.right": False,
        "xtick.direction": "out", "ytick.direction": "out",
        "legend.frameon": False, "axes.grid": False, "lines.linewidth": 1.2,
    })


def stage_figures(args):
    _style()
    import matplotlib.pyplot as plt
    out = rp(A2DIR)
    written = []

    # -------------------------------------------------------- fig_a2_anatomy.png
    p = f"{out}/a2_level_scale.csv"
    if os.path.exists(p):
        ls = pd.read_csv(p)
        sl = ls[ls["scope"] == "slide"].copy()
        reg = ls[ls["scope"] == "regression"].copy()
        order = [g for g in ["A1_unit_calibrated", "A1_block_calibrated",
                             "A2b_anchor_a1", "A2b_C_unit", "A2b_C_block"]
                 if g in set(sl["group"])]
        pal = {"A1_unit_calibrated": "#4C72B0", "A1_block_calibrated": "#DD8452",
               "A2b_anchor_a1": "#8C8C8C", "A2b_C_unit": "#55A868",
               "A2b_C_block": "#C44E52"}
        nice = {"A1_unit_calibrated": "A1 folds, unit calibration",
                "A1_block_calibrated": "A1 folds, block calibration",
                "A2b_anchor_a1": "A2b anchor to A1",
                "A2b_C_unit": "A2b, held-out donor calibration",
                "A2b_C_block": "A2b, spatial-block calibration"}
        short = {"A1_unit_calibrated": "A1, unit cal.",
                 "A1_block_calibrated": "A1, block cal.",
                 "A2b_anchor_a1": "A2b anchor",
                 "A2b_C_unit": "A2b, donor cal.",
                 "A2b_C_block": "A2b, block cal."}
        fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.6))
        # Descriptive panel titles, not claim-titles: which of the level term and the
        # scale term carries the shortfall is the RESULT, and it differs by group, so a
        # sentence-title asserting either one would be contradicted by some of the rows
        # plotted beside it.
        ax = axes[0]
        for g in order:
            d = sl[sl["group"] == g]
            ax.scatter(d["abs_b_over_sy"], d["miss_asymmetry"], s=5, alpha=0.45,
                       color=pal[g], edgecolors="none", label=nice[g])
        ax.axhline(0, color="0.55", lw=0.6, zorder=0)
        ax.set_xlabel(r"standardised slide offset  $|b_s|/s_y$")
        ax.set_ylabel("miss asymmetry")
        ax.set_title(f"Miss asymmetry against the offset\n{len(sl):,} test slides")
        ax.margins(0.04)
        ax = axes[1]
        for g in order:
            d = sl[sl["group"] == g]
            ax.scatter(d["abs_b_over_sy"], d["shortfall"], s=5, alpha=0.45,
                       color=pal[g], edgecolors="none")
        ax.axhline(0, color="0.55", lw=0.6, zorder=0)
        ax.set_xlabel(r"$|b_s|/s_y$")
        ax.set_ylabel("coverage shortfall")
        ax.set_title("Shortfall against the level term\nshortfall = 0.90 - coverage")
        ax.margins(0.04)
        ax = axes[2]
        if len(reg):
            r = reg[reg["group"].isin(order)].set_index("group")
            gs = [g for g in order if g in r.index
                  and np.isfinite(r.loc[g].get("share_level", np.nan))]
            y = np.arange(len(gs))
            lv = [r.loc[g, "share_level"] for g in gs]
            sc = [r.loc[g, "share_scale"] for g in gs]
            ax.barh(y + 0.19, lv, 0.36, color="#4C72B0", label="level  $|b_s|/s_y$")
            ax.barh(y - 0.19, sc, 0.36, color="#DD8452",
                    label=r"scale  $\log(w^\star/\hat w)$")
            ax.set_yticks(y)
            ax.set_yticklabels([short[g] for g in gs])
            ax.set_xlabel("share of shortfall variance")
            ax.set_title("Variance shares of the shortfall\nshares sum to $R^2$")
            ax.axvline(0, color="0.55", lw=0.6)
            # An empty slot above the top group keeps the two-entry legend off the bars;
            # at "lower right" it lands on top of the longest bar of the bottom group.
            ax.set_ylim(-0.6, len(gs) - 0.4 + 1.1)
            ax.set_xlim(0, max(max(lv), max(sc)) * 1.08)
            ax.legend(loc="upper right")
        h, lb = axes[0].get_legend_handles_labels()
        fig.legend(h, lb, loc="lower center", ncol=min(3, len(lb)),
                   bbox_to_anchor=(0.5, -0.17), markerscale=2.2)
        fig.tight_layout()
        fig.savefig(f"{out}/fig_a2_anatomy.png")
        written.append("fig_a2_anatomy.png")
        plt.close(fig)
        print("[write] fig_a2_anatomy.png", flush=True)

    # -------------------------------------------------- fig_a2_coverage_vs_K.png
    p = f"{out}/a2_simulated_coverage.csv"
    if os.path.exists(p):
        sim = pd.read_csv(p)
        d = sim[sim["scope"] == "fold"].copy()
        d = d[np.isfinite(d["K"])]
        fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7))
        ax = axes[0]
        blk = d["block_fold"].fillna(False).astype(bool)
        ax.scatter(d.loc[~blk, "K"], d.loc[~blk, "coverage_observed"], s=10,
                   color="#4C72B0", alpha=0.6, edgecolors="none",
                   label="observed, unit-calibrated fold")
        ax.scatter(d.loc[blk, "K"], d.loc[blk, "coverage_observed"], s=18,
                   facecolors="none", edgecolors="#DD8452", linewidths=0.8,
                   label="observed, block-calibrated fold")
        ax.scatter(d["K"], d["simulated_coverage_mean"], s=10, marker="_",
                   color="#000000", alpha=0.75, label="simulated")
        ax.axhline(NOMINAL, color="0.55", lw=0.7, ls="--")
        ax.annotate("nominal 0.90", xy=(0.99, NOMINAL), xycoords=("axes fraction", "data"),
                    ha="right", va="bottom", fontsize=7, color="0.35")
        if d["K"].max() / max(d["K"].min(), 1) > 8:
            ax.set_xscale("log")
        ax.set_xlabel("number of calibration units $K$")
        ax.set_ylabel("coverage")
        ax.set_title(f"Coverage against $K$\n{len(d)} folds, three encoders")
        ax.margins(0.06)
        ax.legend(loc="lower right")
        ax = axes[1]
        ax.scatter(d.loc[~blk, "between_share"], d.loc[~blk, "coverage_observed"],
                   s=10, color="#4C72B0", alpha=0.6, edgecolors="none")
        ax.scatter(d.loc[blk, "between_share"], d.loc[blk, "coverage_observed"],
                   s=18, facecolors="none", edgecolors="#DD8452", linewidths=0.8)
        ax.axhline(NOMINAL, color="0.55", lw=0.7, ls="--")
        ax.annotate("nominal 0.90", xy=(0.99, NOMINAL), xycoords=("axes fraction", "data"),
                    ha="right", va="bottom", fontsize=7, color="0.35")
        ax.set_xlabel("between-unit share of calibration-score variance\n"
                      "(a test-label diagnostic)")
        ax.set_ylabel("coverage")
        ax.set_title("Coverage against the between-unit share")
        ax.margins(0.06)
        fig.tight_layout()
        fig.savefig(f"{out}/fig_a2_coverage_vs_K.png")
        written.append("fig_a2_coverage_vs_K.png")
        plt.close(fig)
        print("[write] fig_a2_coverage_vs_K.png", flush=True)

    _provenance(out, written, args)
    return 0


def _provenance(out, written, args):
    cfg = dict(stage="round3_A2_mechanisms",
               script="code/scripts/round3_a2_mechanisms.py",
               sub_stage=args.stage, alpha=ALPHA, score=SCORE,
               encoders=list(ENCODERS), n_sim=N_SIM,
               sim_max_n_per_unit=SIM_MAX_N_PER_UNIT,
               between_share_includes_test_unit=True,
               min_slide_spots=MIN_SLIDE_SPOTS, seed_source="zlib.crc32",
               queue_note=(
                   "The nine A2 harness jobs were submitted with #SBATCH -t 16:00:00. On "
                   "2026-09-22 the five that were still pending (2135301 mech hoptimus0, "
                   "2135302 mech uni_v2, 2135303 a2b resnet50, 2135304 a2b hoptimus0, "
                   "2135310 a2b uni_v2) had their limit lowered in place to 03:00:00 with "
                   "`scontrol update JobId=<id> TimeLimit=03:00:00`, because a 16 h limit "
                   "blocks SLURM backfill and the group's fairshare of 0.0066 meant they "
                   "would not start on priority. The bound came from measurement: job "
                   "2135300, the same mech mode on resnet50, ran 1163 s on the main "
                   "designs plus 748 s on slide_out. Nothing about the jobs' work, "
                   "resources or seeds was changed."))
    blob = json.dumps(cfg, sort_keys=True)
    chash = hashlib.sha256(blob.encode()).hexdigest()[:16]
    commit = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    with open(os.path.abspath(__file__), "rb") as f:
        ssha = hashlib.sha256(f.read()).hexdigest()[:16]
    p = f"{out}/PROVENANCE__mechanisms__{args.stage}.txt"
    with open(p, "w") as f:
        f.write(f"{'='*78}\n"
                f"Round 3, stage A2 mechanisms - {args.stage}\n"
                f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID','NA')}\n"
                f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION','NA')}\n"
                f"node            : {os.environ.get('SLURMD_NODENAME','NA')}\n"
                f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
                f"repo_commit     : {commit}\n"
                f"script          : code/scripts/round3_a2_mechanisms.py\n"
                f"script_file     : {os.path.abspath(__file__)}\n"
                f"script_sha256   : sha256/16 {ssha}\n"
                f"command_line    : {' '.join(sys.argv)}\n"
                f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED','unset')}\n"
                f"root            : {ROOT}\n"
                f"files_written   : {', '.join(written) if written else 'none'}\n"
                f"config_hash     : sha256/16 {chash}\n"
                f"config          : {blob}\n"
                f"plan            : round3_execution_plan.md sections 4.4 and 12.4\n")
    print(f"[write] {os.path.basename(p)} (config_hash {chash})", flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=("tables", "figures"), required=True)
    args = ap.parse_args(argv or sys.argv[1:])
    return stage_tables(args) if args.stage == "tables" else stage_figures(args)


if __name__ == "__main__":
    sys.exit(main())
