#!/usr/bin/env python
"""Round 3, stage A4a: adaptive scores and the model-based comparator.

Stage: A4a (round3_execution_plan.md section 13.5.1, which amends section 4.6; the A3 decision
memo sections 5.1 and 10 predictions 1 to 4). No gate.

THIS SCRIPT DOES NOT EDIT THE HARNESS. It imports `round3_a0_harness.py` from the same
directory as a module and reuses its data loading (`load_task`), its base predictor
(`fit_base`, `fit_sigma`), its calibration-unit rule (`choose_calibration` through
`build_fold_specs`), its fold enumeration (`build_fold_specs`), its size matching
(`size_match_groups`, `apply_size_match`), its unit labelling (`unit_labels`), its conformal
quantile (`conformal_quantile`) and its constants unchanged, exactly as
`round3_a3_weighted.py` does. Every A4 fold is therefore an A1 fold by construction rather
than by re-derivation.

Reproducing A1's splits requires enumerating the same design set A1 enumerated, because
`size_match_groups()` takes its per-task `n_match` over every design REQUESTED in the run.
So the two invocations mirror A1's two, with IDC `audited` dropped (section 13.2 item 1: no
further stage runs it):

  main      --designs random,patient,donor   over the ten benchmark task files
  slideout  --designs slide_out              over PRAD and READ

and the ANCHOR, reported first, is that the `abs` score through this code reproduces
`results/round3/A1_coverage/a1_by_fold__<enc>__<tag>.csv` per-fold coverage for both
invocations.

SCORES (section 13.5.1). Six, all at the same alpha and on the same folds, so the only thing
that differs between them is the score function.

  abs          s = |y - yhat|; interval yhat +- qhat. A1's primary score, and the anchor.
  scaled       s = |y - yhat| / sigmahat, sigmahat FLOORED at the harness SIGMA_FLOOR and
               otherwise UNCLIPPED, which is exactly what A1 ran. Kept unclipped on purpose:
               the sigmahat ridge is unconstrained in sign, so wherever it predicts a
               negative value sigmahat lands on the floor and that calibration point's score
               is inflated by three orders of magnitude.
  scaled_clip  the same score with sigmahat CLIPPED to the 1st and 99th percentiles of the
               CALIBRATION set's own sigmahat values, on C and on E alike, the lower clip
               additionally floored at SIGMA_FLOOR, as A3 did. The fraction of folds where
               the lower clip binds is the first comparison's statistic.
  cqr          QuantileRegressor(quantile=q, alpha=0, solver='highs') on the PCA-256 features
               of T for q in {0.05, 0.95}, conformalised with the Romano-Patterson-Candes
               score s = max(qlo(x) - y, y - qhi(x)); interval [qlo(x) - qhat, qhi(x) + qhat].
               Time-boxed; see CQR SCOPE below.
  nb           per gene on RAW COUNTS, a Poisson GLM with log link on the PCA-256 features of
               T (`PoissonRegressor`, small L2) for muhat(x), then an NB2 dispersion per gene
               by the moment estimator on T's Pearson residuals,
               alphahat_g = max(0, (sum (y-mu)^2 - sum mu) / sum mu^2). Predictive
               distribution NB(muhat(x), alphahat_g); the central 1-alpha count interval is
               mapped to log(1+y) and scored against the harness's own log1p target. Not a
               conformal method: it has no calibration set and its level is the model's.
  nb_conformal the same predictive distribution conformalised with s = |F(y; mu, alpha) - 0.5|
               on C; the interval is the NB quantile band at 0.5 +- qhat, mapped to log(1+y).

EVERY score is evaluated at the primary alpha and at an ALPHA GRID, because width is only
comparable at matched coverage. `a4_width_at_coverage.csv` carries, per (task, design,
encoder, score), the width at the nominal level beside its realised coverage, and the width
at the grid level whose realised coverage equals 1 - alpha by monotone interpolation. The
second pair uses test coverage to pick the level, so it is labelled a diagnostic in the file,
the same standing the oracle row has.

RAW COUNTS come from `instrumentation/<task>/spots.parquet` (columns sample_id, barcode,
gene, count, target), the table round 1's `count_diagnostics.py` read. The join to the
harness's own spots is on (sample_id, barcode, gene) and is CHECKED, not assumed:
max |log1p(count) - Y| is asserted below 1e-5 on the joined spots and the joined fraction is
recorded per task. A task whose counts are missing runs every other score and records `nb`
and `nb_conformal` as unavailable rather than silently skipping them.

CONVERGENCE GUARD for the NB head, section 4.6: "Library convergence flags are not trusted;
the fitted deviance is checked and failures recorded, as round 1 did." Per gene the guard
records the fitted Poisson deviance, the intercept-only deviance, and the intercept score
residual |sum(y - mu)| / sum(y), which is zero at the optimum of a Poisson GLM WITH an
intercept and is therefore a sharp convergence statement that does not depend on the
library's own flag. A fit passes when the deviance is finite, does not exceed the
intercept-only deviance, and the score residual is below --nb-score-tol. sklearn's
`n_iter_` is recorded beside the guard and is not used to decide.

CQR SCOPE. Section 4.6 time-boxes each task-encoder CQR fit at 20 minutes with a
20,000-spot T subsample fallback, recorded per fit. Both are implemented (`--cqr-timebox-s`,
`--cqr-subsample`). Because a single QuantileRegressor LP on 36,000 x 256 does not finish in
seconds, the scope actually run is set by `--cqr-genes`, `--cqr-designs` and
`--cqr-max-folds` and is declared in the config hash, in `a4_cqr_fits__<enc><tag>.csv` per
fit, and in the stage report. `--cqr-genes N` takes an EVENLY SPACED subset of the task's own
gene list, `np.linspace(0, n_genes - 1, N).round()`, so the subset spans the variance-ranked
panel rather than its head.

DECILES. `a4_by_decile.csv` bins every test spot-gene by the decile of the BASE predictor's
predicted value, within task and gene over the design's pooled test spots, which is what
A2a's `predicted_value_decile` stratum did. The bins are the same for every score on purpose:
the point of section 13.3's reading is to compare scores inside one fixed stratification.

ORACLE ROW, a diagnostic. Per test slide and gene, b_s = mean(y) - mean(yhat) on that slide;
the `abs` interval is recentred on yhat + b_s and the half-width is the order statistic of
|y - yhat - b_s| that gives exactly 1 - alpha on that slide. It uses test labels, so it is
never a method. Reported separately on unit-calibrated folds (calibration unit donor,
patient or slide) and block-calibrated folds (calibration unit block), which is the split
section 13.3 reads b_s against.

Outputs under results/round3/A4_scores/, summaries before parquets, ACCEPTANCE FIRST:
  a4_acceptance__<enc><tag>.csv      the anchor to A1 and the two other checks
  a4_by_fold__<enc><tag>.csv         per (cell, score, alpha)
  a4_scores_by_task__<enc><tag>.csv  per (task, design, score) at the primary alpha
  a4_width_at_coverage__<enc><tag>.csv
  a4_by_decile__<enc><tag>.csv
  a4_oracle_recentred__<enc><tag>.csv
  a4_sigma_clip__<enc><tag>.csv      the clip-binding fractions, the first comparison
  a4_nb_dispersion__<enc><tag>.csv   alphahat_g beside the marginal Fano factor
  a4_nb_guard__<enc><tag>.csv        the deviance guard, per (task, design, fold, gene)
  a4_pit__<enc><tag>.csv             randomised PIT histogram, KS and log score
  a4_cqr_fits__<enc><tag>.csv        per fit: seconds, n_T used, subsample fallback
  a4_counts_join__<enc><tag>.csv     the raw-count join check
  a4_pergene__<enc><tag>.parquet     per (cell, score, slide, gene), explicit pa.schema
  PROVENANCE__<enc><tag>.txt

Modes:
  <encoder> --task-def ...            the production run
  --timing-probe                      fit-time measurement only; fits one cell of one task
                                      and writes a4_timing__<enc><tag>.csv
  --merge                             no encoder needed: merge the per-encoder tables into
                                      the deliverable names, add the HCP row from A3 and the
                                      oracle row, and render fig_a4_width_at_coverage.png

Usage:
  round3_a4_scores.py <encoder> --task-def <file> [options]
  round3_a4_scores.py --merge [--out-dir ...]
"""
import argparse
import glob as _glob
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import warnings
import zlib

import numpy as np

# An all-infinite interval for one (slide, gene) cell gives nanmean/nanmedian an empty
# slice. That case is COUNTED in n_infinite and reported; the warning would otherwise be
# emitted once per cell per level and bury the run log.
warnings.filterwarnings("ignore", message="Mean of empty slice")
warnings.filterwarnings("ignore", message="All-NaN slice encountered")
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy.stats import nbinom, poisson
from sklearn.linear_model import PoissonRegressor, QuantileRegressor

# --------------------------------------------------- import the A0 harness, unedited
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "round3_a0_harness", os.path.join(_HERE, "round3_a0_harness.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)

ROOT = H.ROOT
A1DIR = "results/round3/A1_coverage"
A3DIR = "results/round3/A3_weighted"

SCORES = ("abs", "scaled", "scaled_clip", "cqr", "nb", "nb_conformal")
CONFORMAL_SCORES = ("abs", "scaled", "scaled_clip", "cqr", "nb_conformal")

# ---- scaled_clip percentiles. A3's, from the A1 memo; carried unchanged so the A3 and A4
# ---- scaled_clip rows are the same quantity.
SIGMA_CLIP_LO_PCT = 1.0
SIGMA_CLIP_HI_PCT = 99.0

# ---- CQR. alpha = 0 is the plan's "no penalty"; the solver is named rather than defaulted.
CQR_QUANTILES = (0.05, 0.95)
CQR_SOLVER = "highs"

# ---- NB head. The L2 is "small" in the plan's words; it is the SAME alpha the mean head
# ---- uses, ALPHA_NUM / (n_components * n_genes), so the two heads are penalised alike and
# ---- the number is not a new free parameter.
NB_MAX_ITER = 300
NB_MIN_MU = 1e-8                  # mu below this is a numerical zero, not a rate
PIT_BINS_FINE = 1000              # the pooled PIT histogram the KS statistic is read from
PIT_BINS_REPORT = 20              # the histogram written out and plotted

N_DECILES = H.N_DECILES

DIFFERENCE_LIST = {
    "abs": "the base head's residual, unscaled. One half-width per gene per fold; sees no "
           "feature of the test point at all.",
    "scaled": "the same residual divided by a sigmahat ridge on the same PCA-256 features, "
              "floored at SIGMA_FLOOR and otherwise unclipped, which is what A1 ran. "
              "Differs from `abs` in exactly one thing: the per-spot scale.",
    "scaled_clip": "identical to `scaled` except that sigmahat is clipped to the 1st and "
                   "99th percentiles of the calibration set's own sigmahat, on C and on E "
                   "alike. Same head, same T, same C, same E, same score numerator.",
    "cqr": "two quantile regressions on the same PCA-256 features of the same T, "
           "conformalised by the Romano score. Differs from `abs` in the shape of the "
           "interval before calibration, not in the calibration set or the fold.",
    "nb": "a per-gene Poisson GLM on RAW COUNTS with an NB2 moment dispersion, on the same "
          "PCA-256 features of the same T. NOT a conformal method: it has no calibration "
          "set and its level is the model's, so it is the only score in the table whose "
          "coverage is not a split-conformal guarantee.",
    "nb_conformal": "the same predictive distribution, calibrated on the same C every "
                    "conformal score uses, with s = |F(y) - 0.5|. Differs from `nb` in "
                    "exactly one thing: the level is read off C instead of the model.",
}


# ------------------------------------------------------------------- arguments
def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("encoder", nargs="?", default=None,
                   help="required unless --merge is given")
    p.add_argument("--task-def", action="append", dest="task_def", default=None)
    p.add_argument("--out-dir", default="results/round3/A4_scores")
    p.add_argument("--tag", default="")
    p.add_argument("--designs", default="random,patient,donor")
    p.add_argument("--fit-designs", default="",
                   help="fit only these designs; --designs still governs enumeration and "
                        "therefore size matching, exactly as in the harness")
    p.add_argument("--scores", default=",".join(SCORES))
    p.add_argument("--alpha", type=float, default=0.10)
    p.add_argument("--alpha-grid", default="0.02,0.05,0.075,0.10,0.15,0.20,0.30",
                   help="levels at which every score's coverage and width are recorded, so "
                        "that width can be read at matched coverage")
    p.add_argument("--n-cal-draws", type=int, default=3)
    p.add_argument("--spot-cal-draws", type=int, default=1)
    p.add_argument("--n-repeats", type=int, default=None)
    p.add_argument("--max-folds", type=int, default=None)
    p.add_argument("--size-match", default="task", choices=("task", "fold", "none"))
    p.add_argument("--a1-dir", default=A1DIR)
    p.add_argument("--accept-tag", default="",
                   help="which A1 tag the `abs` anchor reads: main or slideout")
    p.add_argument("--anchor-tol", type=float, default=1e-12)
    p.add_argument("--counts-dir", default="instrumentation",
                   help="<counts-dir>/<task>/spots.parquet carries the raw counts")
    p.add_argument("--count-diag", default="results/tailored/counts/count_diagnostics.csv")
    p.add_argument("--counts-tol", type=float, default=1e-5)
    # ---- CQR scope, all declared in the config hash ----
    p.add_argument("--cqr-genes", type=int, default=0,
                   help="0 = every gene; N = an evenly spaced subset of N genes")
    p.add_argument("--cqr-designs", default="",
                   help="empty = every fitted design")
    p.add_argument("--cqr-max-folds", type=int, default=0,
                   help="0 = every fold; N = the first N folds of each design")
    p.add_argument("--cqr-max-draws", type=int, default=0,
                   help="0 = every calibration draw and repeat; N = cal_draw < N and "
                        "repeat < N")
    p.add_argument("--cqr-timebox-s", type=float, default=1200.0,
                   help="section 4.6's 20 minutes per task-encoder CQR block")
    p.add_argument("--cqr-subsample", type=int, default=20000,
                   help="section 4.6's T subsample once the time box is exceeded")
    p.add_argument("--cqr-presubsample", type=int, default=1,
                   help="1 = apply the subsample whenever n_T exceeds it, without first "
                        "paying for one over-box fit. Measured on this host: ONE "
                        "QuantileRegressor fit at n = 20,000 costs 395 to 1,016 s and at "
                        "n = 35,996 it is projected past 2,000 s, so the first fit of "
                        "CCRCC would exceed the 20-minute box by itself. The reason is "
                        "recorded per fit as pre_emptive_n_T_above_cap.")
    p.add_argument("--cqr-budget-s", type=float, default=0.0,
                   help="0 = no budget. Otherwise CQR stops for the rest of a task once "
                        "the task's cumulative CQR seconds pass this, recorded as "
                        "budget_exhausted, so a wall-clock stop cannot cost the other "
                        "five scores.")
    p.add_argument("--cqr-cells-only", type=int, default=0,
                   help="1 = fit and evaluate ONLY the cells cqr_cell() selects. "
                        "Enumeration is untouched, so size matching and therefore the "
                        "splits are A1's either way; this only avoids paying for base "
                        "fits on cells the CQR invocation would not score.")
    p.add_argument("--cqr-mark-only", type=int, default=0,
                   help="1 = do not fit CQR, but still MARK the cells and genes CQR "
                        "would have run on, so the other five scores emit their "
                        "`cqr_matched` subset rows on exactly those cells and genes. The "
                        "cell rule is deterministic (--cqr-designs, --cqr-max-folds, "
                        "--cqr-max-draws), so a mark-only run and the run that actually "
                        "fits CQR agree on the subset without either reading the other.")
    p.add_argument("--root", default=None,
                   help="override the harness ROOT. Used only by --merge, so the merge "
                        "and the figure can run off a local copy of the per-encoder CSVs.")
    # ---- NB scope ----
    p.add_argument("--nb-genes", type=int, default=0)
    p.add_argument("--nb-solver", default="newton-cholesky",
                   choices=("lbfgs", "newton-cholesky"),
                   help="the OPTIMISER for the per-gene Poisson GLM, not a model choice: "
                        "both minimise the same penalised Poisson deviance to the same "
                        "tolerance and the deviance guard checks which optimum was "
                        "reached. newton-cholesky factorises the 256 x 256 Hessian and is "
                        "the reason the NB head over 50 genes x every fold is affordable")
    p.add_argument("--nb-tol", type=float, default=1e-6)
    p.add_argument("--probe-nb-solvers", default="lbfgs,newton-cholesky")
    p.add_argument("--nb-score-tol", type=float, default=1e-3,
                   help="the intercept score residual |sum(y-mu)|/sum(y) the deviance "
                        "guard requires")
    p.add_argument("--no-parquet", action="store_true")
    p.add_argument("--timing-probe", action="store_true")
    p.add_argument("--probe-genes", type=int, default=2)
    p.add_argument("--probe-sizes", default="2000,5000,20000")
    p.add_argument("--merge", action="store_true")
    p.add_argument("--report-numbers", action="store_true",
                   help="compute every pooled number the stage report quotes into "
                        "a4_report_numbers.csv; implies nothing else and reads only the "
                        "merged CSVs")
    p.add_argument("--merge-encoders", default="hoptimus0,uni_v2,resnet50")
    a = p.parse_args(argv)
    if a.report_numbers:
        a.merge = True
    if not a.merge:
        assert a.encoder, "an encoder is required unless --merge is given"
        assert a.task_def, "--task-def is required unless --merge is given"
    return a


def harness_args(args, designs):
    """An argparse namespace the harness's own enumeration accepts, carrying A1's values for
    everything that touches the split. Built THROUGH the harness's parse_args so that a new
    harness flag with a split-relevant default cannot be missed here. A3 does the same."""
    argv = [args.encoder]
    for t in args.task_def:
        argv += ["--task-def", t]
    argv += ["--designs", ",".join(designs),
             "--alpha", str(args.alpha),
             "--n-cal-draws", str(args.n_cal_draws),
             "--spot-cal-draws", str(args.spot_cal_draws),
             "--size-match", args.size_match]
    if args.n_repeats is not None:
        argv += ["--n-repeats", str(args.n_repeats)]
    if args.max_folds:
        argv += ["--max-folds", str(args.max_folds)]
    return H.parse_args(argv)


SUBSET_DIFFERENCE_LIST = {
    "full": "every gene the score ran on, over every fold, repeat and calibration draw "
            "it ran on. For abs, scaled and scaled_clip that is all 50 genes and all "
            "cells; for nb and nb_conformal the NB gene subset on all cells; for cqr the "
            "CQR gene subset on the CQR cells. Comparing two scores here confounds any "
            "difference with the gene and cell selection.",
    "cqr_matched": "IDENTICAL cells and IDENTICAL genes for every score: the cells CQR "
                   "ran on (the calibration-draw-0, repeat-0 cell of every fold of every "
                   "design) and the CQR gene subset. Same task, design, fold, repeat, "
                   "draw, proper-training set, calibration set, test set, level and "
                   "aggregation; the ONLY thing that differs between two rows of this "
                   "subset is the score function.",
    "nb_matched": "the NB gene subset, which is the union of the NB and CQR evenly spaced "
                  "subsets, on every cell where the NB head fitted. Carries abs, scaled, "
                  "scaled_clip, nb and nb_conformal on identical cells and genes; cqr is "
                  "absent because fitting it on this many genes is not affordable.",
}


def _positions(gidx, want):
    """Column positions of `want` inside `gidx`, or None when `gidx` does not contain all
    of them. Used to slice a score's interval arrays down to a matched gene subset without
    recomputing the interval."""
    lut = {int(j): p for p, j in enumerate(np.asarray(gidx).tolist())}
    if any(int(j) not in lut for j in want):
        return None
    return np.array([lut[int(j)] for j in want], dtype=int)


def cqr_cell(design, nfold, sp, args):
    """Whether this (design, fold, repeat, calibration draw) cell is a CQR cell.

    Deterministic and independent of any fit, so a --cqr-mark-only run selects exactly the
    cells the CQR run fits."""
    cd = {d for d in args.cqr_designs.split(",") if d}
    if cd and design not in cd:
        return False
    if args.cqr_max_folds and nfold >= args.cqr_max_folds:
        return False
    if args.cqr_max_draws and not (sp["cal_draw"] < args.cqr_max_draws
                                   and sp["repeat"] < args.cqr_max_draws):
        return False
    return True


def nb_gene_indices(n_genes, args):
    """The NB gene subset: the union of the NB and CQR evenly spaced subsets.

    The union is what makes `cqr_matched` a subset on which nb and nb_conformal can be
    compared with the other four scores; without it the two linspace subsets of 50 genes
    share only their endpoints.
    """
    a = gene_subset(n_genes, args.nb_genes)
    b = gene_subset(n_genes, args.cqr_genes)
    return np.unique(np.concatenate([a, b]))


def gene_subset(n_genes, k):
    """An evenly spaced index subset of a gene list, or every gene when k is 0 or >= n.

    np.linspace over the task's own list order, so the subset spans the variance-ranked
    panel rather than its head. Deterministic and independent of any fit.
    """
    if not k or k >= n_genes:
        return np.arange(n_genes)
    return np.unique(np.round(np.linspace(0, n_genes - 1, k)).astype(int))


# ------------------------------------------------------------------ interval metrics
def fold_stats(Y, lo, hi, alpha, samp_E, min_spots):
    """Per-fold interval summary and the per (slide, gene) arrays behind it.

    Y, lo, hi are (n_spot, n_gene). Returns (summary, cells) where `cells` is a dict of
    (n_slide, n_gene) arrays plus the slide names and test counts, so the caller can emit
    per (slide, gene) rows without recomputing.

    The summary is A1's aggregation chain: restrict to slides with at least `min_spots` test
    spots, then the unweighted mean over the (slide, gene) cells. Identical to
    a1_by_fold's mean-over-genes-then-over-slides because the grid has no missing cell.
    Infinite widths cover by construction; they are counted and never averaged into a width.
    """
    below, above = Y < lo, Y > hi
    cov = ~(below | above)
    width = hi - lo
    fin = np.isfinite(width)
    wid_nan = np.where(fin, width, np.nan)
    isc = np.where(fin, width, np.nan)
    with np.errstate(invalid="ignore"):
        isc = np.where(below & fin, isc + (2.0 / alpha) * (lo - Y), isc)
        isc = np.where(above & fin, isc + (2.0 / alpha) * (Y - hi), isc)

    slides = np.unique(samp_E)
    ns = len(slides)
    ng = Y.shape[1]
    out = {k: np.empty((ns, ng), dtype=np.float64)
           for k in ("coverage", "width_mean", "width_median", "interval_score",
                     "miss_above", "miss_below")}
    out["n_covered"] = np.empty((ns, ng), dtype=np.int64)
    out["n_infinite"] = np.empty((ns, ng), dtype=np.int64)
    n_test = np.empty(ns, dtype=np.int64)
    with np.errstate(invalid="ignore"):
        for i, s in enumerate(slides):
            m = samp_E == s
            n_test[i] = int(m.sum())
            out["coverage"][i] = cov[m].mean(axis=0)
            out["n_covered"][i] = cov[m].sum(axis=0)
            out["width_mean"][i] = np.nanmean(wid_nan[m], axis=0)
            out["width_median"][i] = np.nanmedian(wid_nan[m], axis=0)
            out["interval_score"][i] = np.nanmean(isc[m], axis=0)
            out["miss_above"][i] = above[m].mean(axis=0)
            out["miss_below"][i] = below[m].mean(axis=0)
            out["n_infinite"][i] = (~fin[m]).sum(axis=0)
    out["slides"] = slides
    out["n_test"] = n_test

    keep = n_test >= min_spots
    if not keep.any():
        keep = np.ones(ns, bool)
    # The median is over the fold's individual finite (spot, gene) widths, restricted to the
    # same slides the mean is restricted to, so the two columns describe the same cells.
    keep_row = np.isin(samp_E, slides[keep])
    all_w = width[keep_row][fin[keep_row]]
    summary = dict(
        coverage=float(np.mean(out["coverage"][keep])),
        width_mean=float(np.nanmean(out["width_mean"][keep])),
        width_median_of_cells=float(np.nanmean(out["width_median"][keep])),
        width_median=float(np.median(all_w)) if all_w.size else np.nan,
        width_mean_spotgene=float(np.mean(all_w)) if all_w.size else np.nan,
        interval_score=float(np.nanmean(out["interval_score"][keep])),
        miss_above=float(np.mean(out["miss_above"][keep])),
        miss_below=float(np.mean(out["miss_below"][keep])),
        n_cells=int(keep.sum() * ng), n_slides=int(keep.sum()),
        n_infinite=int(out["n_infinite"].sum()), n_spot_gene=int(fin.size),
        frac_infinite=float((~fin).mean()))
    out["keep"] = keep
    return summary, out


# ----------------------------------------------------- the NB2 predictive distribution
def _nb_rp(mu, a):
    """scipy's (n, p) for NB2 with mean mu and var = mu + a mu^2: n = 1/a, p = n/(n+mu)."""
    r = 1.0 / a
    return r, r / (r + mu)


def nb_ppf(q, mu, alpha_g):
    """Count quantile per gene. `q` is a scalar or (n_gene,); mu is (n, n_gene).

    q <= 0 returns 0, the smallest possible count, and q >= 1 returns +inf, which is the
    honest upper end of a count distribution with unbounded support. alpha_g == 0 is the
    Poisson limit and is evaluated as Poisson rather than as NB with r = inf.
    """
    out = np.empty(mu.shape, dtype=np.float64)
    qv = np.broadcast_to(np.asarray(q, dtype=np.float64), (mu.shape[1],))
    for j in range(mu.shape[1]):
        qq = float(qv[j])
        if qq <= 0.0:
            out[:, j] = 0.0
        elif qq >= 1.0:
            out[:, j] = np.inf
        elif alpha_g[j] <= 0.0:
            out[:, j] = poisson.ppf(qq, np.maximum(mu[:, j], NB_MIN_MU))
        else:
            r, p = _nb_rp(np.maximum(mu[:, j], NB_MIN_MU), alpha_g[j])
            out[:, j] = nbinom.ppf(qq, r, p)
    return out


def nb_cdf(k, mu, alpha_g):
    """F(k; mu, alpha_g) per gene, k and mu both (n, n_gene). k < 0 gives 0."""
    out = np.empty(mu.shape, dtype=np.float64)
    for j in range(mu.shape[1]):
        m = np.maximum(mu[:, j], NB_MIN_MU)
        if alpha_g[j] <= 0.0:
            out[:, j] = poisson.cdf(k[:, j], m)
        else:
            r, p = _nb_rp(m, alpha_g[j])
            out[:, j] = nbinom.cdf(k[:, j], r, p)
    return np.where(k < 0, 0.0, out)


def nb_logpmf(k, mu, alpha_g):
    out = np.empty(mu.shape, dtype=np.float64)
    for j in range(mu.shape[1]):
        m = np.maximum(mu[:, j], NB_MIN_MU)
        if alpha_g[j] <= 0.0:
            out[:, j] = poisson.logpmf(k[:, j], m)
        else:
            r, p = _nb_rp(m, alpha_g[j])
            out[:, j] = nbinom.logpmf(k[:, j], r, p)
    return out


def poisson_deviance(y, mu):
    """2 sum [ y log(y/mu) - (y - mu) ], with the y = 0 term taken at its limit 0."""
    mu = np.maximum(mu, NB_MIN_MU)
    t = np.where(y > 0, y * np.log(np.where(y > 0, y, 1.0) / mu), 0.0)
    return float(2.0 * np.sum(t - (y - mu)))


# --------------------------------------------------------------- raw counts
def load_counts(task, samp, bc, genes, counts_dir, tol):
    """Raw integer counts per (spot, gene) in the harness's own spot order.

    Returns (counts (n_spot, n_gene) float64 with NaN where unjoined, info dict) or
    (None, info) when the file is absent. The join is on (sample_id, barcode, gene) and is
    CHECKED against the harness's own log1p target by the caller, not assumed.
    """
    p = f"{ROOT}/{counts_dir}/{task}/spots.parquet"
    info = dict(task=task, counts_path=os.path.relpath(p, ROOT), present=os.path.exists(p),
                n_spots=len(samp), n_genes=len(genes), n_joined_spot_gene=0,
                frac_joined=0.0, max_abs_log1p_minus_Y=np.nan, rows_in_file=0)
    if not info["present"]:
        print(f"[counts] {p} absent; `nb` and `nb_conformal` cannot run on {task}",
              flush=True)
        return None, info
    d = pq.read_table(p, columns=["sample_id", "barcode", "gene", "count"]).to_pandas()
    info["rows_in_file"] = int(len(d))
    for c in ("sample_id", "barcode", "gene", "count"):
        assert c in d.columns, f"{p}: no {c} column"
    d["sample_id"] = d["sample_id"].astype(str)
    d["barcode"] = d["barcode"].astype(str)
    d["gene"] = d["gene"].astype(str)
    gpos = {g: j for j, g in enumerate(genes)}
    spos = {(s, b): i for i, (s, b) in enumerate(zip(samp.tolist(), bc.tolist()))}
    C = np.full((len(samp), len(genes)), np.nan, dtype=np.float64)
    gi = d["gene"].map(gpos)
    ok = gi.notna().to_numpy()
    si = np.array([spos.get(k, -1) for k in zip(d["sample_id"].to_numpy(),
                                                d["barcode"].to_numpy())])
    m = ok & (si >= 0)
    C[si[m], gi.to_numpy()[m].astype(int)] = d["count"].to_numpy(dtype=np.float64)[m]
    njoin = int(np.isfinite(C).sum())
    info["n_joined_spot_gene"] = njoin
    info["frac_joined"] = float(njoin / C.size)
    print(f"[counts] {task}: {len(d):,} rows in file, "
          f"{njoin:,}/{C.size:,} spot-genes joined "
          f"({info['frac_joined']:.4f})", flush=True)
    return C, info


# --------------------------------------------------------------- the CQR head
def fit_cqr(A_T, Y_T, gidx, state, key, args):
    """Two QuantileRegressor fits per gene on the PCA-256 features of T.

    Returns (models, rows) with models a dict (gene index, quantile) -> fitted regressor and
    rows the per-fit timing records. The time box is section 4.6's: once the CUMULATIVE CQR
    time inside this task-encoder passes --cqr-timebox-s, every later fit in the task uses T
    subsampled to --cqr-subsample spots with a crc32 seed, and the fallback is recorded per
    fit rather than inferred from a wall time.
    """
    models, rows = {}, []
    n_T = A_T.shape[0]
    for j in gidx:
        for q in CQR_QUANTILES:
            if args.cqr_budget_s and state["cqr_seconds"] > args.cqr_budget_s:
                models[(j, q)] = None
                rows.append(dict(**state["base"], gene_index=int(j), quantile=q,
                                 n_T_natural=int(n_T), n_T_used=0,
                                 subsample_fallback=True,
                                 subsample_reason="budget_exhausted",
                                 subsample_size=int(args.cqr_subsample), seconds=0.0,
                                 cumulative_task_seconds=round(state["cqr_seconds"], 1),
                                 timebox_s=args.cqr_timebox_s, solver=CQR_SOLVER,
                                 failure="not fitted: task CQR budget exhausted"))
                continue
            reason = ""
            if state["cqr_fallback"] and n_T > args.cqr_subsample:
                reason = "timebox_exceeded"
            elif args.cqr_presubsample and n_T > args.cqr_subsample:
                reason = "pre_emptive_n_T_above_cap"
            fell_back = bool(reason)
            if fell_back:
                rng = np.random.default_rng(
                    zlib.crc32(f"{key}|cqr_sub|g{j}|q{q}".encode()))
                sel = rng.choice(n_T, size=args.cqr_subsample, replace=False)
                Xf, yf = A_T[sel], Y_T[sel, j]
            else:
                Xf, yf = A_T, Y_T[:, j]
            t0 = time.time()
            qr = QuantileRegressor(quantile=q, alpha=0.0, solver=CQR_SOLVER)
            failed = ""
            try:
                qr.fit(Xf, yf)
            except Exception as e:                     # recorded, never silently dropped
                failed = f"{type(e).__name__}: {e}"[:200]
                qr = None
            dt = time.time() - t0
            state["cqr_seconds"] += dt
            models[(j, q)] = qr
            rows.append(dict(**state["base"], gene_index=int(j), quantile=q,
                             n_T_natural=int(n_T), n_T_used=int(Xf.shape[0]),
                             subsample_fallback=bool(fell_back),
                             subsample_reason=reason,
                             subsample_size=int(args.cqr_subsample),
                             seconds=round(dt, 3),
                             cumulative_task_seconds=round(state["cqr_seconds"], 1),
                             timebox_s=args.cqr_timebox_s, solver=CQR_SOLVER,
                             failure=failed))
            if (state["cqr_seconds"] > args.cqr_timebox_s
                    and not state["cqr_fallback"]):
                state["cqr_fallback"] = True
                print(f"  [cqr] time box {args.cqr_timebox_s:.0f}s exceeded after "
                      f"{state['cqr_seconds']:.0f}s; T subsampled to "
                      f"{args.cqr_subsample} for every later fit in this task",
                      flush=True)
    return models, rows


def cqr_predict(models, A, gidx):
    """(n, len(gidx)) lower and upper quantile predictions; NaN where a fit failed."""
    lo = np.full((A.shape[0], len(gidx)), np.nan)
    hi = np.full((A.shape[0], len(gidx)), np.nan)
    for c, j in enumerate(gidx):
        m_lo, m_hi = models.get((j, CQR_QUANTILES[0])), models.get((j, CQR_QUANTILES[1]))
        if m_lo is not None:
            lo[:, c] = m_lo.predict(A)
        if m_hi is not None:
            hi[:, c] = m_hi.predict(A)
    return lo, hi


# --------------------------------------------------------------- the NB head
def fit_nb(A_T, cnt_T, gidx, ridge_alpha, genes, args, base):
    """Per-gene Poisson GLM on raw counts plus an NB2 moment dispersion, with the
    deviance-based convergence guard of section 4.6.

    Returns (models, alpha_g, guard_rows). A gene whose guard fails keeps its fit and is
    FLAGGED; nothing is dropped silently, which is what round 1's `nb_diverged` did.
    """
    models, alphas, rows = {}, np.zeros(len(gidx)), []
    for c, j in enumerate(gidx):
        y = cnt_T[:, j]
        fin = np.isfinite(y)
        if fin.sum() < H.MIN_C_SPOTS or not np.isfinite(y[fin]).all():
            rows.append(dict(**base, gene=genes[j], gene_index=int(j), n_T=int(fin.sum()),
                             status="too_few_joined_counts", guard_pass=False))
            models[j] = None
            continue
        t0 = time.time()
        gl = PoissonRegressor(alpha=ridge_alpha, fit_intercept=True,
                              max_iter=NB_MAX_ITER, tol=args.nb_tol,
                              solver=args.nb_solver)
        status = "ok"
        try:
            gl.fit(A_T[fin], y[fin])
        except Exception as e:
            status = f"fit_error:{type(e).__name__}"
            models[j] = None
            rows.append(dict(**base, gene=genes[j], gene_index=int(j),
                             n_T=int(fin.sum()), status=status, guard_pass=False,
                             seconds=round(time.time() - t0, 3)))
            continue
        mu = np.maximum(gl.predict(A_T[fin]), NB_MIN_MU)
        yv = y[fin]
        dev = poisson_deviance(yv, mu)
        dev0 = poisson_deviance(yv, np.full_like(yv, max(yv.mean(), NB_MIN_MU)))
        sy = float(yv.sum())
        score_res = float(abs(yv.sum() - mu.sum()) / sy) if sy > 0 else np.nan
        guard = bool(np.isfinite(dev) and dev <= dev0 * (1.0 + 1e-9)
                     and np.isfinite(score_res) and score_res < args.nb_score_tol)
        # NB2 moment dispersion on T's Pearson residuals, section 4.6's formula exactly.
        num = float(np.sum((yv - mu) ** 2) - np.sum(mu))
        den = float(np.sum(mu ** 2))
        a_g = max(0.0, num / den) if den > 0 else 0.0
        alphas[c] = a_g
        models[j] = gl
        rows.append(dict(**base, gene=genes[j], gene_index=int(j), n_T=int(fin.sum()),
                         status=status, guard_pass=guard,
                         deviance=dev, deviance_null=dev0,
                         deviance_ratio=float(dev / dev0) if dev0 > 0 else np.nan,
                         score_residual=score_res, score_tol=args.nb_score_tol,
                         n_iter=int(np.max(np.atleast_1d(getattr(gl, "n_iter_", -1)))),
                         max_iter=NB_MAX_ITER, solver=args.nb_solver, tol=args.nb_tol,
                         library_flag_trusted=False,
                         alpha_g=a_g, mean_count_T=float(yv.mean()),
                         var_count_T=float(yv.var(ddof=1)) if len(yv) > 1 else np.nan,
                         seconds=round(time.time() - t0, 3)))
    return models, alphas, rows


def nb_predict(models, A, gidx):
    mu = np.full((A.shape[0], len(gidx)), np.nan)
    for c, j in enumerate(gidx):
        m = models.get(j)
        if m is not None:
            mu[:, c] = np.maximum(m.predict(A), NB_MIN_MU)
    return mu


def interval_for(score, sc, alpha):
    """(lo, hi) on the log1p scale for one score at one level. The only place a level
    enters; every score is evaluated through this function so that the alpha grid cannot
    diverge from the primary level by an implementation difference."""
    if score in ("abs", "scaled", "scaled_clip"):
        q, _ = H.conformal_quantile(sc["S_C"], alpha)
        half = sc["unit_E"] * q[None, :]
        return sc["P_E"] - half, sc["P_E"] + half, q
    if score == "cqr":
        q, _ = H.conformal_quantile(sc["S_C"], alpha)
        return sc["qlo_E"] - q[None, :], sc["qhi_E"] + q[None, :], q
    if score == "nb":
        lo = nb_ppf(alpha / 2.0, sc["mu_E"], sc["alpha_g"])
        hi = nb_ppf(1.0 - alpha / 2.0, sc["mu_E"], sc["alpha_g"])
        return np.log1p(lo), np.log1p(hi), np.full(sc["mu_E"].shape[1], np.nan)
    if score == "nb_conformal":
        q, _ = H.conformal_quantile(sc["S_C"], alpha)
        lo = nb_ppf(0.5 - q, sc["mu_E"], sc["alpha_g"])
        hi = nb_ppf(0.5 + q, sc["mu_E"], sc["alpha_g"])
        return np.log1p(lo), np.log1p(hi), q
    raise ValueError(score)


def ks_from_fine_hist(hist):
    """The one-sample KS statistic against Uniform(0,1) read off a fine histogram.

    Resolution is the bin width, 1/PIT_BINS_FINE = 1e-3, which is stated wherever the
    statistic is reported. Exact per-cell KS values are computed on the cell's own PIT
    array and written beside this one, so the approximation is visible rather than assumed
    away.
    """
    n = float(hist.sum())
    if n <= 0:
        return np.nan
    cum = np.cumsum(hist) / n
    nb = len(hist)
    upper = np.arange(1, nb + 1) / nb
    lower = np.arange(0, nb) / nb
    return float(max(np.max(np.abs(cum - upper)),
                     np.max(np.abs(np.concatenate([[0.0], cum[:-1]]) - lower))))


def exact_ks_uniform(u):
    """Exact one-sample KS against Uniform(0,1) for a 1-D array."""
    u = np.sort(np.asarray(u, dtype=np.float64))
    n = len(u)
    if n == 0:
        return np.nan
    i = np.arange(1, n + 1)
    return float(max(np.max(i / n - u), np.max(u - (i - 1) / n)))


# =============================================================== the per-task engine
def run_task(td, enc, args, designs, scores, alphas, state):
    t0 = time.time()
    task, label_set = td["task"], td["label_set"]
    meta = dict(
        donor_of={s["sample_id"]: s["donor_id"] for s in td["samples"]},
        patient_of={s["sample_id"]: s["hest_patient"] for s in td["samples"]},
        resgroup_of={s["sample_id"]: s["resolution_group"] for s in td["samples"]},
        session_of={s["sample_id"]: s.get("session") for s in td["samples"]},
    )
    hargs = harness_args(args, designs)
    X, Y, samp, bc, xy, genes = H.load_task(td, enc)
    ngene = len(genes)
    print(f"[load] {task}/{label_set} {enc}: {X.shape[0]:,} spots x {X.shape[1]} dims, "
          f"{ngene} genes, {time.time()-t0:.0f}s", flush=True)
    state["dims"][task] = X.shape[1]
    state["n_spots"][task] = X.shape[0]

    need_nb = bool({"nb", "nb_conformal"} & set(scores))
    CNT, cinfo = (load_counts(task, samp, bc, genes, args.counts_dir, args.counts_tol)
                  if need_nb else (None, None))
    if cinfo is not None:
        if CNT is not None:
            fin = np.isfinite(CNT)
            if fin.any():
                d = np.abs(np.log1p(CNT[fin]) - Y.astype(np.float64)[fin])
                cinfo["max_abs_log1p_minus_Y"] = float(d.max())
                assert cinfo["max_abs_log1p_minus_Y"] < args.counts_tol, (
                    f"{task}: log1p(raw count) disagrees with the harness's own target by "
                    f"{cinfo['max_abs_log1p_minus_Y']:.3e} on the joined spot-genes, so the "
                    f"count table and the harness are not describing the same spots")
                print(f"[counts] {task}: max |log1p(count) - Y| = "
                      f"{cinfo['max_abs_log1p_minus_Y']:.3e}", flush=True)
        state["counts_join"].append(dict(encoder=enc, **cinfo))
    nb_ok = CNT is not None

    specs = H.build_fold_specs(td, samp, xy, designs, meta, hargs)
    H.size_match_groups(specs, args.size_match)
    fit_designs = {d for d in args.fit_designs.split(",") if d}
    cqr_designs = {d for d in args.cqr_designs.split(",") if d}
    print(f"[specs] {task}: {len(specs)} cells enumerated; "
          f"fitting {sorted(fit_designs) if fit_designs else 'all'}", flush=True)

    # Cells are processed DESIGN BY DESIGN so that the predicted-value decile bins, which
    # pool a design's test spots, can be built and then freed one design at a time.
    order = {d: i for i, d in enumerate(designs)}
    specs.sort(key=lambda s: (order.get(s["design"], 99),))
    # Fold ordinal WITHIN this task and design, assigned in order of first appearance, so
    # that --cqr-max-folds names the first N folds of each design deterministically.
    fold_ord = {}
    cstate = dict(cqr_seconds=0.0, cqr_fallback=False, base={})
    chunks = []
    cur_design = None

    for i, sp in enumerate(specs):
        Tm = H.apply_size_match(sp, task)
        Cm, Em, info = sp["C"], sp["E"], sp["info"]
        design = sp["design"]
        if fit_designs and design not in fit_designs:
            continue
        if design != cur_design:
            if cur_design is not None:
                _deciles_for_design(task, label_set, enc, cur_design, chunks, genes, state)
            chunks, cur_design = [], design
        if int(Tm.sum()) < H.MIN_T_SPOTS or int(Cm.sum()) < H.MIN_C_SPOTS:
            print(f"  [skip] {task} {design} {sp['fold']}: |T|={int(Tm.sum())} "
                  f"|C|={int(Cm.sum())} ({info['cal_status']})", flush=True)
            state["skipped"].append(dict(encoder=enc, task=task, label_set=label_set,
                                         design=design, fold=sp["fold"],
                                         repeat=sp["repeat"], cal_draw=sp["cal_draw"],
                                         n_T=int(Tm.sum()), n_C=int(Cm.sum()),
                                         cal_status=info["cal_status"]))
            continue
        fkey = (design, sp["fold"])
        if fkey not in fold_ord:
            fold_ord[fkey] = len({k for k in fold_ord if k[0] == design})
        nfold = fold_ord[fkey]
        if args.cqr_cells_only and not cqr_cell(design, nfold, sp, args):
            continue

        pipe, A, reg, ridge_alpha = H.fit_base(X[Tm], Y[Tm])
        sig = H.fit_sigma(A, Y[Tm], reg, ridge_alpha)
        A_C = pipe.transform(X[Cm].astype(np.float64, copy=False))
        B = pipe.transform(X[Em].astype(np.float64, copy=False))
        P_C, P_E = reg.predict(A_C), reg.predict(B)
        Y_C = Y[Cm].astype(np.float64, copy=False)
        Y_E = Y[Em].astype(np.float64, copy=False)
        samp_E = samp[Em]
        n_C, n_E = int(Cm.sum()), int(Em.sum())
        # K, the number of calibration UNITS, for context beside the oracle and the
        # decile tables. Under `random` the unit is the spot, so K is the spot count by
        # construction; the harness's unit_labels covers the other levels.
        if str(info["calibration_unit"]) == "spot":
            K = n_C
        else:
            K = len({str(u) for u in
                     H.unit_labels(info["calibration_unit"], Cm,
                                   sp.get("pool", Cm | sp["T"]), samp, xy, meta)[Cm]})

        base = dict(encoder=enc, task=task, label_set=label_set, design=design,
                    fold=sp["fold"], repeat=sp["repeat"], cal_draw=sp["cal_draw"],
                    calibration_unit=str(info["calibration_unit"]))
        cstate["base"] = dict(base)
        all_g = np.arange(ngene)
        mach = {}

        # ---------------------------------------------------------- abs
        if "abs" in scores:
            mach["abs"] = dict(kind="conformal", gidx=all_g, rows=None,
                               S_C=np.abs(Y_C - P_C), unit_E=np.ones_like(P_E),
                               P_E=P_E, Y_E=Y_E, samp_E=samp_E,
                               n_C_used=n_C, n_E_used=n_E)

        # -------------------------------------------- scaled and scaled_clip
        raw_C, raw_E = sig.predict(A_C), sig.predict(B)
        if "scaled" in scores:
            s_C = np.maximum(raw_C, H.SIGMA_FLOOR)
            u_E = np.maximum(raw_E, H.SIGMA_FLOOR)
            mach["scaled"] = dict(kind="conformal", gidx=all_g, rows=None,
                                  S_C=np.abs(Y_C - P_C) / s_C, unit_E=u_E,
                                  P_E=P_E, Y_E=Y_E, samp_E=samp_E,
                                  n_C_used=n_C, n_E_used=n_E)
        if "scaled_clip" in scores:
            lo_p = float(np.percentile(raw_C, SIGMA_CLIP_LO_PCT))
            hi_p = float(np.percentile(raw_C, SIGMA_CLIP_HI_PCT))
            lo_c = max(lo_p, H.SIGMA_FLOOR)
            hi_c = max(hi_p, lo_c * (1 + 1e-12))
            s_C = np.clip(raw_C, lo_c, hi_c)
            u_E = np.clip(raw_E, lo_c, hi_c)
            mach["scaled_clip"] = dict(kind="conformal", gidx=all_g, rows=None,
                                       S_C=np.abs(Y_C - P_C) / s_C, unit_E=u_E,
                                       P_E=P_E, Y_E=Y_E, samp_E=samp_E,
                                       n_C_used=n_C, n_E_used=n_E)
            state["sigma"].append(dict(
                **base, n_C=n_C, n_E=n_E,
                sigma_floor=H.SIGMA_FLOOR,
                sigma_clip_lo_pct=SIGMA_CLIP_LO_PCT,
                sigma_clip_hi_pct=SIGMA_CLIP_HI_PCT,
                sigma_clip_lo=lo_c, sigma_clip_hi=hi_c,
                sigma_p1_raw_cal=lo_p, sigma_p99_raw_cal=hi_p,
                sigma_min_raw_cal=float(raw_C.min()),
                sigma_min_raw_test=float(raw_E.min()),
                sigma_median_raw_cal=float(np.median(raw_C)),
                # the extrapolation defect that motivates the clip: an unconstrained ridge
                # on absolute residuals predicts negative values
                frac_cal_raw_below_floor=float((raw_C < H.SIGMA_FLOOR).mean()),
                frac_test_raw_below_floor=float((raw_E < H.SIGMA_FLOOR).mean()),
                p1_below_floor=bool(lo_p < H.SIGMA_FLOOR),
                # "the lower clip binds" on a fold when at least one TEST sigmahat falls
                # below the lower clip, so the clip changes that fold's intervals
                frac_test_clipped_low=float((raw_E < lo_c).mean()),
                frac_test_clipped_high=float((raw_E > hi_c).mean()),
                frac_cal_clipped_low=float((raw_C < lo_c).mean()),
                frac_cal_clipped_high=float((raw_C > hi_c).mean()),
                lower_clip_binds=bool((raw_E < lo_c).any()),
                upper_clip_binds=bool((raw_E > hi_c).any())))

        # ---------------------------------------------------------- cqr
        is_cqr_cell = cqr_cell(design, nfold, sp, args)
        cqr_gset = (gene_subset(ngene, args.cqr_genes)
                    if is_cqr_cell and ("cqr" in scores or args.cqr_mark_only) else None)
        nb_gset = None
        if "cqr" in scores and is_cqr_cell:
            gi = gene_subset(ngene, args.cqr_genes)
            mods, rows = fit_cqr(A, Y[Tm].astype(np.float64, copy=False), gi,
                                 cstate, f"{task}|{design}|{sp['fold']}|{sp['cal_draw']}",
                                 args)
            state["cqr"] += rows
            ok = np.array([mods.get((j, CQR_QUANTILES[0])) is not None
                           and mods.get((j, CQR_QUANTILES[1])) is not None for j in gi])
            gi = gi[ok]
            if len(gi):
                qlo_C, qhi_C = cqr_predict(mods, A_C, gi)
                qlo_E, qhi_E = cqr_predict(mods, B, gi)
                S_C = np.maximum(qlo_C - Y_C[:, gi], Y_C[:, gi] - qhi_C)
                mach["cqr"] = dict(kind="conformal", gidx=gi, rows=None, S_C=S_C,
                                   qlo_E=qlo_E, qhi_E=qhi_E,
                                   P_E=P_E[:, gi], Y_E=Y_E[:, gi], samp_E=samp_E,
                                   n_C_used=n_C, n_E_used=n_E)

        # ------------------------------------------------- nb and nb_conformal
        if need_nb and nb_ok:
            gi = nb_gene_indices(ngene, args)
            nb_gset = gi
            rowok_T = np.isfinite(CNT[Tm][:, gi]).all(axis=1)
            nbmods, a_g, grows = fit_nb(A[rowok_T], CNT[Tm][rowok_T], gi, ridge_alpha,
                                        genes, args, base)
            state["nbguard"] += grows
            gok = np.array([nbmods.get(j) is not None for j in gi])
            gi2, a_g2 = gi[gok], a_g[gok]
            if len(gi2):
                rowC = np.isfinite(CNT[Cm][:, gi2]).all(axis=1)
                rowE = np.isfinite(CNT[Em][:, gi2]).all(axis=1)
                mu_C = nb_predict(nbmods, A_C[rowC], gi2)
                mu_E = nb_predict(nbmods, B[rowE], gi2)
                cnt_C = CNT[Cm][rowC][:, gi2]
                cnt_E = CNT[Em][rowE][:, gi2]
                erows = np.flatnonzero(rowE)
                if "nb" in scores:
                    mach["nb"] = dict(kind="model", gidx=gi2, rows=erows,
                                      mu_E=mu_E, alpha_g=a_g2,
                                      P_E=P_E[rowE][:, gi2], Y_E=Y_E[rowE][:, gi2],
                                      samp_E=samp_E[rowE], n_C_used=0,
                                      n_E_used=int(rowE.sum()))
                if "nb_conformal" in scores:
                    F_C = nb_cdf(cnt_C, mu_C, a_g2)
                    mach["nb_conformal"] = dict(
                        kind="conformal", gidx=gi2, rows=erows, S_C=np.abs(F_C - 0.5),
                        mu_E=mu_E, alpha_g=a_g2, P_E=P_E[rowE][:, gi2],
                        Y_E=Y_E[rowE][:, gi2], samp_E=samp_E[rowE],
                        n_C_used=int(rowC.sum()), n_E_used=int(rowE.sum()))
                _nb_diagnostics(base, gi2, genes, cnt_E, mu_E, a_g2, samp_E[rowE],
                                state)
                gmap = {(g["gene"], g["gene_index"]): g for g in grows}
                for c, j in enumerate(gi2):
                    # alpha_g_oos: the SAME moment estimator on the CALIBRATION set's
                    # out-of-sample Pearson residuals. Not the plan's estimator, not used
                    # for any interval; recorded because the plan's in-sample version is
                    # degenerate wherever the PCA-256 mean head overfits T, and telling
                    # "the estimator collapsed" apart from "the conditional dispersion is
                    # zero" needs a residual the head has not seen.
                    num = float(np.sum((cnt_C[:, c] - mu_C[:, c]) ** 2)
                                - np.sum(mu_C[:, c]))
                    den = float(np.sum(mu_C[:, c] ** 2))
                    a_oos = max(0.0, num / den) if den > 0 else np.nan
                    gr = gmap.get((genes[j], int(j)), {})
                    state["nbdisp"].append(dict(
                        **base, gene=genes[j], gene_index=int(j),
                        alpha_g=float(a_g2[c]), alpha_g_oos=a_oos,
                        n_T=int(rowok_T.sum()), n_C=int(rowC.sum()),
                        deviance_ratio=gr.get("deviance_ratio", np.nan),
                        score_residual=gr.get("score_residual", np.nan),
                        guard_pass=gr.get("guard_pass", None),
                        mean_count_T=gr.get("mean_count_T", np.nan),
                        var_count_T=gr.get("var_count_T", np.nan),
                        mean_count_E=float(np.nanmean(cnt_E[:, c])),
                        var_count_E=float(np.nanvar(cnt_E[:, c], ddof=1))))

        # ------------------------------------------------- every score, every level
        # The predicted-value decile bins come from the BASE head's prediction, stored ONCE
        # per cell and shared by every score: section 13.3 asks A4 to compare scores inside
        # one fixed stratification, not each inside its own.
        prim_cell = dict(pred=P_E.astype(np.float32), per_score={},
                         fold=sp["fold"], repeat=sp["repeat"], cal_draw=sp["cal_draw"],
                         calibration_unit=str(info["calibration_unit"]),
                         cqr_gset=cqr_gset, nb_gset=nb_gset)
        for score, sc in mach.items():
            gnames = [genes[j] for j in sc["gidx"]]
            sub = ("all" if len(sc["gidx"]) == ngene
                   else f"every_kth_{len(sc['gidx'])}")
            # The matched subsets the lead's request 1 asks for: identical cells and
            # identical genes for every score, so that no difference between two scores is
            # confounded with the gene or fold selection. Computed by slicing the interval
            # arrays, so no interval is recomputed.
            subsets = [("full", np.arange(len(sc["gidx"])))]
            for nm, want in (("cqr_matched", cqr_gset), ("nb_matched", nb_gset)):
                if want is None:
                    continue
                pos = _positions(sc["gidx"], want)
                if pos is not None and len(pos) < len(sc["gidx"]):
                    subsets.append((nm, pos))
                elif pos is not None:
                    subsets.append((nm, pos))
            for al in alphas:
                lo, hi, q = interval_for(score, sc, al)
                for sname, pos in subsets:
                    summ, cells = fold_stats(sc["Y_E"][:, pos], lo[:, pos], hi[:, pos],
                                             al, sc["samp_E"], H.MIN_SLIDE_SPOTS)
                    state["fold"].append({
                        **base, "score": score, "alpha": al, "subset": sname,
                        "gene_subset": sub, "n_genes": len(pos),
                        "is_conformal": sc["kind"] == "conformal",
                        "n_T": int(Tm.sum()), "n_C": n_C, "n_E": n_E,
                        "n_C_used": sc["n_C_used"], "n_E_used": sc["n_E_used"],
                        "K": K, "q_mean": float(np.nanmean(q[pos])),
                        "is_cqr_cell": bool(cqr_gset is not None),
                        "primary": bool(al == args.alpha), **summ})
                    if al == args.alpha and sname == "full":
                        _pergene_rows(base, score, al, sub, gnames, cells, state)
                        if score == "abs":
                            _oracle_rows(base, sc, lo, hi, q, cells, K, state)
                if al == args.alpha:
                    prim_cell["per_score"][score] = dict(
                        covered=(~((sc["Y_E"] < lo) | (sc["Y_E"] > hi))),
                        width=(hi - lo).astype(np.float32),
                        rows=sc["rows"], gidx=sc["gidx"])
        if prim_cell["per_score"]:
            chunks.append(prim_cell)
        print(f"  [{i+1}/{len(specs)}] {task} {design} {sp['fold']} rep={sp['repeat']} "
              f"draw={sp['cal_draw']} unit={info['calibration_unit']} "
              f"n_T={int(Tm.sum())} n_C={n_C} n_E={n_E} K={K} "
              f"scores={sorted(mach)} {time.time()-t0:.0f}s", flush=True)

    if cur_design is not None:
        _deciles_for_design(task, label_set, enc, cur_design, chunks, genes, state)
    state["cqr_task_seconds"][f"{task}/{label_set}"] = round(cstate["cqr_seconds"], 1)
    del X, Y, CNT
    return time.time() - t0


PG_COLS = ["task", "label_set", "encoder", "design", "fold", "repeat", "cal_draw",
           "score", "alpha", "gene_subset", "calibration_unit", "slide", "gene",
           "n_test", "n_covered", "coverage", "width_mean", "width_median",
           "interval_score", "miss_above", "miss_below", "n_infinite",
           "slide_ge_min_spots"]


def _pergene_rows(base, score, alpha, sub, gnames, cells, state):
    """Per (test slide, gene) rows at the primary level, appended as tuples for the
    parquet. The parquet stays on Longleaf; the CSVs are the deliverables."""
    sl = cells["slides"]
    for i, s in enumerate(sl):
        ok = bool(cells["n_test"][i] >= H.MIN_SLIDE_SPOTS)
        for j, g in enumerate(gnames):
            state["pg"].append((
                base["task"], base["label_set"], base["encoder"], base["design"],
                base["fold"], base["repeat"], base["cal_draw"], score, alpha, sub,
                base["calibration_unit"], s, g, int(cells["n_test"][i]),
                int(cells["n_covered"][i, j]), float(cells["coverage"][i, j]),
                float(cells["width_mean"][i, j]), float(cells["width_median"][i, j]),
                float(cells["interval_score"][i, j]), float(cells["miss_above"][i, j]),
                float(cells["miss_below"][i, j]), int(cells["n_infinite"][i, j]), ok))


def _oracle_rows(base, sc, lo, hi, q, cells, K, state):
    """The oracle row of section 13.5.1, a DIAGNOSTIC: the `abs` interval recentred per
    test slide by b_s = mean(y) - mean(yhat) on that slide, with the half-width that then
    gives exactly 1 - alpha on that slide.

    Uses test labels twice over, for the offset and for the half-width, so it is never a
    method; it says what slide-level recentring would be worth in width. One row per
    (fold, test slide), with the per-gene ratio summed and counted so the pooled mean over
    (slide, gene) cells can be formed exactly at merge time.
    """
    Y_E, P_E, samp_E = sc["Y_E"], sc["P_E"], sc["samp_E"]
    alpha = state["alpha"]
    for i, s in enumerate(cells["slides"]):
        m = samp_E == s
        n = int(m.sum())
        Ys, Ps = Y_E[m], P_E[m]
        b_s = Ys.mean(axis=0) - Ps.mean(axis=0)
        s_y = Ys.std(axis=0)
        resid_rc = np.abs(Ys - (Ps + b_s[None, :]))
        w_star, _c = H.oracle_halfwidth(resid_rc, np.ones_like(resid_rc), alpha)
        # coverage of the recentred oracle on this slide; ceil((1-alpha) n)/n by
        # construction, recorded rather than assumed
        cov_rc = (resid_rc <= w_star[None, :]).mean(axis=0)
        w_hat = np.asarray(q, dtype=np.float64)
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(w_hat > 0, w_star / w_hat, np.nan)
        fin = np.isfinite(ratio)
        state["oracle"].append(dict(
            **base, slide=s, n_test=n, n_genes=int(len(w_hat)),
            slide_ge_min_spots=bool(n >= H.MIN_SLIDE_SPOTS), K=K,
            calibration_unit_class=("block" if base["calibration_unit"] == "block"
                                    else ("spot" if base["calibration_unit"] == "spot"
                                          else "unit")),
            alpha=alpha,
            w_hat_abs_mean=float(np.mean(w_hat)),
            w_star_recentred_mean=float(np.mean(w_star)),
            ratio_sum=float(np.sum(ratio[fin])), ratio_n=int(fin.sum()),
            ratio_mean=float(np.mean(ratio[fin])) if fin.any() else np.nan,
            ratio_median=float(np.median(ratio[fin])) if fin.any() else np.nan,
            coverage_abs=float(np.mean(cells["coverage"][i])),
            coverage_recentred=float(np.mean(cov_rc)),
            b_s_mean=float(np.mean(b_s)), b_s_abs_mean=float(np.mean(np.abs(b_s))),
            s_y_mean=float(np.mean(s_y)),
            b_s_over_sy_mean=float(np.mean(np.abs(b_s) / np.where(s_y > 0, s_y, np.nan)))))


def _nb_diagnostics(base, gidx, genes, cnt_E, mu_E, alpha_g, samp_E, state):
    """Randomised PIT, log score and KS for the NB predictive distribution.

    PIT = F(y-1) + U (F(y) - F(y-1)) with U ~ Uniform(0,1) from a crc32 seed, which is the
    standard randomisation for a discrete predictive distribution. The exact KS statistic is
    computed on this cell's own PIT values; a 1000-bin histogram is accumulated so a POOLED
    KS can be read across folds, resolved to 1e-3.
    """
    F_y = nb_cdf(cnt_E, mu_E, alpha_g)
    F_m1 = nb_cdf(cnt_E - 1.0, mu_E, alpha_g)
    rng = np.random.default_rng(zlib.crc32(
        f"{base['task']}|{base['design']}|{base['fold']}|{base['repeat']}|"
        f"{base['cal_draw']}|pit".encode()))
    U = rng.random(cnt_E.shape)
    pit = np.clip(F_m1 + U * (F_y - F_m1), 0.0, 1.0)
    lp = nb_logpmf(cnt_E, mu_E, alpha_g)
    for c, j in enumerate(gidx):
        g = genes[j]
        u = pit[:, c]
        u = u[np.isfinite(u)]
        key = (base["task"], base["label_set"], base["design"], g)
        hh = state["pithist"].get(key)
        if hh is None:
            hh = np.zeros(PIT_BINS_FINE, dtype=np.int64)
            state["pithist"][key] = hh
        hh += np.bincount(np.clip((u * PIT_BINS_FINE).astype(int), 0,
                                  PIT_BINS_FINE - 1), minlength=PIT_BINS_FINE)
        state["pit_cell"].append(dict(
            **base, gene=g, gene_index=int(j), n=int(len(u)),
            ks_exact=exact_ks_uniform(u), pit_mean=float(u.mean()) if len(u) else np.nan,
            pit_var=float(u.var()) if len(u) else np.nan,
            log_score_mean=float(-np.nanmean(lp[:, c])),
            alpha_g=float(alpha_g[c])))


def _deciles_for_design(task, label_set, enc, design, chunks, genes, state):
    """a4_by_decile: coverage and width by predicted-value decile, per design and score.

    The decile is taken WITHIN TASK AND GENE over the design's pooled test spots, which is
    what A2a's `predicted_value_decile` stratum did, and the bins come from the BASE head's
    prediction so that every score is read inside the same stratification. Aggregated
    before anything is written; no spot-level table is ever emitted.
    """
    if not chunks:
        return
    pred = np.concatenate([ch["pred"] for ch in chunks], axis=0)
    off = np.cumsum([0] + [len(ch["pred"]) for ch in chunks])
    dec = np.empty(pred.shape, dtype=np.int8)
    for j in range(pred.shape[1]):
        dec[:, j] = H.bin_edges_quantile(pred[:, j].astype(float), N_DECILES)
    # The decile BINS are per gene, so restricting to a matched gene subset does not move
    # them; the three subsets are three aggregations of the same stored arrays over
    # different cells and columns, which is why they cost no extra memory.
    acc = {}
    for ci, ch in enumerate(chunks):
        d_ch = dec[off[ci]:off[ci + 1]]
        p_ch = pred[off[ci]:off[ci + 1]]
        for score, r in ch["per_score"].items():
            rows = r["rows"]
            dsub = d_ch if rows is None else d_ch[rows]
            psub = p_ch if rows is None else p_ch[rows]
            dsub, psub = dsub[:, r["gidx"]], psub[:, r["gidx"]]
            cov, wid = r["covered"], r["width"]
            subsets = [("full", np.arange(dsub.shape[1]))]
            for nm, want in (("cqr_matched", ch["cqr_gset"]),
                             ("nb_matched", ch["nb_gset"])):
                if want is None:
                    continue
                pos = _positions(r["gidx"], want)
                if pos is not None:
                    subsets.append((nm, pos))
            for sname, pos in subsets:
                ds, ps = dsub[:, pos], psub[:, pos]
                cs, ws = cov[:, pos], wid[:, pos]
                for b in range(N_DECILES):
                    m = ds == b
                    if not m.any():
                        continue
                    k = (score, sname, ch["fold"], b)
                    a = acc.setdefault(k, [0, 0, 0.0, 0.0, 0, 0.0])
                    a[0] += int(m.sum())
                    a[1] += int(cs[m].sum())
                    w = ws[m]
                    f = np.isfinite(w)
                    a[2] += float(w[f].sum())
                    a[3] += float(ps[m].sum())
                    a[4] += int(f.sum())
                    a[5] += float((~f).sum())
    for (score, sname, fold, b), a in sorted(
            acc.items(), key=lambda kv: (kv[0][0], kv[0][1], str(kv[0][2]), kv[0][3])):
        state["decile"].append(dict(
            task=task, label_set=label_set, encoder=enc, design=design, score=score,
            subset=sname, alpha=state["alpha"], fold=fold,
            stratum_kind="predicted_value_decile",
            stratum_value=b, n_spot_gene=a[0], n_covered=a[1],
            coverage=a[1] / a[0] if a[0] else np.nan,
            width_mean=a[2] / a[4] if a[4] else np.nan,
            pred_mean=a[3] / a[0] if a[0] else np.nan,
            n_finite_width=a[4], n_infinite_width=int(a[5])))
        # The difference list for `subset` is a paragraph and is the same for every row of
        # a subset, so it lives in a4_difference_lists.csv rather than being repeated
        # 68,000 times; per-row it made this table 34 MB instead of 7 MB.
    print(f"[decile] {task} {design}: {len(acc)} (score, fold, decile) cells from "
          f"{pred.shape[0]:,} test spots", flush=True)
    chunks.clear()


# ==================================================================== acceptance
def _anchor_by_cell(prim, args, enc):
    """The per-CELL anchor: `abs` and `scaled` coverage per (fold, repeat, calibration
    draw) against a1_by_slide averaged over slides.

    a1_by_slide is already restricted to slides with at least MIN_SLIDE_SPOTS test spots
    and averaged over genes, so its mean over slides is exactly this stage's fold_stats
    coverage for the SAME cell. Unlike the by-fold anchor it holds whatever subset of a
    fold's cells a run scores, which is what an invocation run with --cqr-cells-only
    needs.
    """
    rows = []
    if not args.accept_tag:
        return rows
    src = f"{ROOT}/{args.a1_dir}/a1_by_slide__{enc}__{args.accept_tag}.csv"
    if not os.path.exists(src):
        return [dict(check="ANCHOR_cell_abs_reproduces_A1_by_slide", score="abs",
                     n_cells=0, statistic="source absent", value=np.nan,
                     tol=args.anchor_tol, passed=None, note=f"{src} not found")]
    a1 = pd.read_csv(src)
    key = ["task", "label_set", "design", "fold", "repeat", "cal_draw"]
    for sc in ("abs", "scaled"):
        ref = (a1[a1["score"] == sc].groupby(key, dropna=False)
               [["coverage", "width_mean"]].mean().reset_index())
        mine = prim[(prim["score"] == sc) & (prim["gene_subset"] == "all")][
            key + ["coverage", "width_mean"]]
        if not len(mine) or not len(ref):
            continue
        mine, ref = mine.copy(), ref.copy()
        mine["fold"] = mine["fold"].astype(str)
        ref["fold"] = ref["fold"].astype(str)
        j = mine.merge(ref, on=key, suffixes=("_a4", "_a1")).dropna(
            subset=["coverage_a4", "coverage_a1"])
        if not len(j):
            continue
        dc = float((j["coverage_a4"] - j["coverage_a1"]).abs().max())
        dw = float((j["width_mean_a4"] - j["width_mean_a1"]).abs().max())
        rows.append(dict(check=f"ANCHOR_cell_{sc}_reproduces_A1_by_slide", score=sc,
                         n_cells=len(j),
                         statistic="max |dcoverage| per (fold, repeat, cal draw)",
                         value=dc, tol=args.anchor_tol,
                         passed=bool(dc <= args.anchor_tol),
                         note=f"max |dwidth| {dw:.3e}; source "
                              f"{os.path.relpath(src, ROOT)}"))
    return rows


def acceptance(state, args, enc):
    """The anchor FIRST, then the two checks section 4.6 asks for.

    ANCHOR. A1 ran `abs` AND `scaled` on these folds, so both are anchored: the per-fold
    coverage of each, at the primary level, must reproduce
    a1_by_fold__<enc>__<accept-tag>.csv. That is a stronger statement than A3's single
    anchor and it is the first thing this stage reports.
    """
    fold = pd.DataFrame(state["fold"])
    rows, ok_all = [], True
    if not len(fold):
        return pd.DataFrame(), True
    # The anchor and the two checks read the FULL subset: A1's committed numbers are over
    # all 50 genes, so a matched-subset row is not the quantity they anchor to.
    prim = fold[fold["primary"] & (fold["subset"] == "full")]

    src = f"{ROOT}/{args.a1_dir}/a1_by_fold__{enc}__{args.accept_tag}.csv" \
        if args.accept_tag else ""
    if src and os.path.exists(src):
        a1 = pd.read_csv(src)
        for sc in ("abs", "scaled"):
            ref = a1[a1["score"] == sc][["task", "label_set", "design", "fold",
                                         "coverage", "width_mean"]]
            mine = (prim[(prim["score"] == sc) & (prim["gene_subset"] == "all")]
                    .groupby(["task", "label_set", "design", "fold"])
                    [["coverage", "width_mean"]].mean().reset_index())
            j = mine.merge(ref, on=["task", "label_set", "design", "fold"],
                           suffixes=("_a4", "_a1")).dropna(
                               subset=["coverage_a4", "coverage_a1"])
            if not len(j):
                rows.append(dict(check=f"ANCHOR_{sc}_reproduces_A1_by_fold", score=sc,
                                 n_cells=0, statistic="no overlapping folds",
                                 value=np.nan, tol=args.anchor_tol, passed=None,
                                 note=f"source {os.path.relpath(src, ROOT)}"))
                continue
            dc = float((j["coverage_a4"] - j["coverage_a1"]).abs().max())
            dw = float((j["width_mean_a4"] - j["width_mean_a1"]).abs().max())
            # a1_by_fold averages over every repeat and calibration draw of a fold. A run
            # that scores only some of a fold's cells cannot match it, and saying so is
            # the honest answer rather than widening a tolerance: the per-CELL anchor
            # below is the one that applies to such a run.
            inapplicable = bool(args.cqr_cells_only)
            passed = None if inapplicable else bool(dc <= args.anchor_tol)
            if not inapplicable:
                ok_all &= passed
            rows.append(dict(check=f"ANCHOR_{sc}_reproduces_A1_by_fold", score=sc,
                             n_cells=len(j),
                             statistic="max |dcoverage| against a1_by_fold",
                             value=dc, tol=args.anchor_tol, passed=passed,
                             note=("INAPPLICABLE: --cqr-cells-only scores one cell per "
                                   "fold while a1_by_fold averages over every repeat "
                                   "and calibration draw; see the per-cell anchor. "
                                   if inapplicable else "")
                                  + f"max |dwidth| {dw:.3e}; "
                                    f"source {os.path.relpath(src, ROOT)}"))
    else:
        rows.append(dict(check="ANCHOR_abs_reproduces_A1_by_fold", score="abs",
                         n_cells=0, statistic="source absent", value=np.nan,
                         tol=args.anchor_tol, passed=None,
                         note=f"{src or '--accept-tag not given'} not read"))

    # ---- the PER-CELL anchor, against a1_by_slide rather than a1_by_fold.
    # a1_by_fold averages over every repeat and calibration draw of a fold, so a run that
    # scores only a subset of a fold's cells (--cqr-cells-only) cannot match it and the
    # by-fold check above is inapplicable there. a1_by_slide carries one row per
    # (fold, repeat, cal_draw, slide), already restricted to slides with at least
    # MIN_SLIDE_SPOTS test spots and averaged over genes, so averaging it over slides is
    # exactly this stage's own fold_stats coverage for the SAME cell. This anchor holds
    # whatever subset of cells a run scores.
    rows += _anchor_by_cell(prim, args, enc)
    for r in rows:
        if r["check"].startswith("ANCHOR_cell") and r["passed"] is False:
            ok_all = False

    # ---- section 4.6: on `random`, CQR coverage is at nominal
    r = prim[(prim["design"] == "random") & (prim["score"] == "cqr")]
    if len(r):
        g = r.groupby(["task", "label_set"])["coverage"].mean()
        worst = float((g - (1.0 - args.alpha)).abs().max())
        passed = worst <= 0.02
        ok_all &= passed
        rows.append(dict(check="A4_cqr_coverage_at_nominal_on_random", score="cqr",
                         n_cells=len(g), statistic="max |coverage - nominal| over tasks",
                         value=worst, tol=0.02, passed=passed,
                         note=f"nominal {1-args.alpha:.2f}; mean over folds per task"))

    # ---- section 4.6: on `random`, the NB PIT histogram is close to uniform
    pit = pd.DataFrame(state["pit_cell"])
    if len(pit):
        p = pit[pit["design"] == "random"]
        if len(p):
            med = float(p["ks_exact"].median())
            mx = float(p["ks_exact"].max())
            passed = med <= 0.05
            ok_all &= passed
            rows.append(dict(check="A4_nb_pit_uniform_on_random", score="nb",
                             n_cells=len(p),
                             statistic="median exact KS over (fold, gene)", value=med,
                             tol=0.05, passed=passed,
                             note=f"max KS {mx:.4f}; the 0.05 threshold is this stage's "
                                  f"own, section 4.6 asks for the statistic to be "
                                  f"reported, not for a level"))
    return pd.DataFrame(rows), ok_all


# ======================================================================== outputs
PG_SCHEMA = pa.schema([
    ("task", pa.string()), ("label_set", pa.string()), ("encoder", pa.string()),
    ("design", pa.string()), ("fold", pa.string()), ("repeat", pa.int32()),
    ("cal_draw", pa.int32()), ("score", pa.string()), ("alpha", pa.float64()),
    ("gene_subset", pa.string()), ("calibration_unit", pa.string()),
    ("slide", pa.string()), ("gene", pa.string()), ("n_test", pa.int32()),
    ("n_covered", pa.int32()), ("coverage", pa.float64()),
    ("width_mean", pa.float64()), ("width_median", pa.float64()),
    ("interval_score", pa.float64()), ("miss_above", pa.float64()),
    ("miss_below", pa.float64()), ("n_infinite", pa.int32()),
    ("slide_ge_min_spots", pa.bool_()),
])


def _difference_list_file(out):
    """a4_difference_lists.csv: the difference list for every score and every matched
    subset, written once. The reporting rule is that a difference list exists for every
    comparison BEFORE the term is named; it does not require the paragraph to be repeated
    on each of tens of thousands of rows."""
    rows = [dict(kind="score", key=k, difference_list=v)
            for k, v in sorted(DIFFERENCE_LIST.items())]
    rows += [dict(kind="subset", key=k, difference_list=v)
             for k, v in sorted(SUBSET_DIFFERENCE_LIST.items())]
    pd.DataFrame(rows).to_csv(f"{out}/a4_difference_lists.csv", index=False)


def write_outputs(out, suf, state, args, enc, acc, ok_all):
    os.makedirs(out, exist_ok=True)
    written = []

    # ---- acceptance FIRST ----
    if len(acc):
        acc.to_csv(f"{out}/a4_acceptance{suf}.csv", index=False)
        written.append(f"a4_acceptance{suf}.csv")
        print(f"\n=== A4a ACCEPTANCE, encoder {enc} ===")
        print(acc.to_string(index=False), flush=True)
        print(f"ACCEPTANCE: {'PASS' if ok_all else 'FAIL'}", flush=True)

    fold = pd.DataFrame(state["fold"])
    if len(fold):
        fold.to_csv(f"{out}/a4_by_fold{suf}.csv", index=False)
        written.append(f"a4_by_fold{suf}.csv")
        print(f"[write] a4_by_fold{suf}.csv ({len(fold)} rows)", flush=True)
        grp = ["task", "label_set", "encoder", "design", "score", "alpha", "subset",
               "gene_subset", "is_conformal"]
        by_task = (fold.groupby(grp, dropna=False)
                   .agg(n_folds=("fold", "nunique"), n_cells=("coverage", "size"),
                        coverage=("coverage", "mean"), coverage_sd=("coverage", "std"),
                        width_mean=("width_mean", "mean"),
                        width_median=("width_median", "mean"),
                        width_median_of_cells=("width_median_of_cells", "mean"),
                        interval_score=("interval_score", "mean"),
                        miss_above=("miss_above", "mean"),
                        miss_below=("miss_below", "mean"),
                        n_infinite=("n_infinite", "sum"),
                        n_spot_gene=("n_spot_gene", "sum"),
                        n_genes=("n_genes", "min"),
                        n_T=("n_T", "min"), n_C=("n_C", "min"),
                        K_median=("K", "median"))
                   .reset_index())
        by_task["frac_infinite"] = by_task["n_infinite"] / by_task["n_spot_gene"]
        # The two difference lists are paragraphs, identical within a score and within a
        # subset, so they go in a lookup file keyed by score and by subset rather than
        # being repeated on every row.
        _difference_list_file(out)
        written.append("a4_difference_lists.csv")
        by_task.to_csv(f"{out}/a4_scores_by_task{suf}.csv", index=False)
        written.append(f"a4_scores_by_task{suf}.csv")
        print(f"[write] a4_scores_by_task{suf}.csv ({len(by_task)} rows)", flush=True)
        for sname in sorted(by_task["subset"].unique()):
            show = by_task[(by_task["alpha"] == args.alpha)
                           & (by_task["subset"] == sname)]
            print(f"\n--- subset {sname} at alpha {args.alpha} ---", flush=True)
            print(show[["task", "design", "score", "n_folds", "n_cells", "coverage",
                        "width_mean", "width_median", "n_genes", "frac_infinite"]]
                  .round(4).to_string(index=False), flush=True)

    for key, stem in (("sigma", "a4_sigma_clip"), ("decile", "a4_by_decile"),
                      ("oracle", "a4_oracle_recentred"), ("nbdisp", "a4_nb_dispersion"),
                      ("nbguard", "a4_nb_guard"), ("cqr", "a4_cqr_fits"),
                      ("counts_join", "a4_counts_join"), ("skipped", "a4_skipped"),
                      ("pit_cell", "a4_pit_by_cell")):
        if state[key]:
            d = pd.DataFrame(state[key])
            d.to_csv(f"{out}/{stem}{suf}.csv", index=False)
            written.append(f"{stem}{suf}.csv")
            print(f"[write] {stem}{suf}.csv ({len(d)} rows)", flush=True)

    # ---- the pooled PIT table: histogram, pooled KS and the exact per-cell KS beside it
    if state["pithist"]:
        rows = []
        pc = pd.DataFrame(state["pit_cell"])
        for (task, ls, design, gene), hh in sorted(state["pithist"].items()):
            n = int(hh.sum())
            coarse = hh.reshape(PIT_BINS_REPORT, -1).sum(axis=1) / max(n, 1)
            sel = pc[(pc["task"] == task) & (pc["design"] == design)
                     & (pc["gene"] == gene)] if len(pc) else pc
            rows.append(dict(
                task=task, label_set=ls, encoder=state["encoder"], design=design,
                gene=gene, n=n, ks_pooled_from_hist=ks_from_fine_hist(hh),
                ks_hist_resolution=1.0 / PIT_BINS_FINE,
                ks_cell_median=float(sel["ks_exact"].median()) if len(sel) else np.nan,
                ks_cell_max=float(sel["ks_exact"].max()) if len(sel) else np.nan,
                log_score_mean=float(sel["log_score_mean"].mean()) if len(sel) else np.nan,
                alpha_g_mean=float(sel["alpha_g"].mean()) if len(sel) else np.nan,
                n_cells=int(len(sel)),
                **{f"h{b:02d}": float(coarse[b]) for b in range(PIT_BINS_REPORT)}))
        d = pd.DataFrame(rows)
        d.to_csv(f"{out}/a4_pit{suf}.csv", index=False)
        written.append(f"a4_pit{suf}.csv")
        print(f"[write] a4_pit{suf}.csv ({len(d)} rows)", flush=True)

    if state["pg"] and not args.no_parquet:
        cols = [f.name for f in PG_SCHEMA]
        d = pd.DataFrame(state["pg"], columns=PG_COLS)[cols].copy()
        for f in PG_SCHEMA:
            if f.type == pa.string():
                d[f.name] = d[f.name].astype(str)
            elif f.type == pa.int32():
                d[f.name] = d[f.name].fillna(0).astype("int32")
            elif f.type == pa.float64():
                d[f.name] = d[f.name].astype("float64")
            elif f.type == pa.bool_():
                d[f.name] = d[f.name].astype(bool)
        pq.write_table(pa.Table.from_pandas(d, schema=PG_SCHEMA, preserve_index=False),
                       f"{out}/a4_pergene{suf}.parquet", compression="snappy")
        written.append(f"a4_pergene{suf}.parquet")
        print(f"[write] a4_pergene{suf}.parquet ({len(d):,} rows, explicit schema)",
              flush=True)
    return written


def provenance(out, suf, cfg, blob, chash, state, wall, written, ok_all, stage):
    """Section 13.4 item 5 (iii): the provenance records the working copy's HEAD AND the
    md5 of the script file actually executed, computed inside the job."""
    commit = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    with open(os.path.abspath(__file__), "rb") as f:
        sb = f.read()
    with open(os.path.join(_HERE, "round3_a0_harness.py"), "rb") as f:
        hb = f.read()
    os.makedirs(out, exist_ok=True)
    p = f"{out}/PROVENANCE{suf}.txt"
    with open(p, "w") as f:
        f.write(f"{'='*78}\n"
                f"Round 3, stage {stage} - adaptive scores and the model-based comparator, "
                f"encoder {cfg.get('encoder')}\n"
                f"tasks           : {', '.join(cfg.get('tasks', []))}\n"
                f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID','NA')}\n"
                f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION','NA')}\n"
                f"node            : {os.environ.get('SLURMD_NODENAME','NA')}\n"
                f"gpu             : {os.environ.get('SLURM_JOB_GPUS','none')}\n"
                f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
                f"repo_commit     : {commit}\n"
                f"script          : code/scripts/round3_a4_scores.py\n"
                f"script_file     : {os.path.abspath(__file__)}\n"
                f"script_md5      : {hashlib.md5(sb).hexdigest()}\n"
                f"script_sha256   : sha256/16 "
                f"{hashlib.sha256(sb).hexdigest()[:16]}\n"
                f"harness_md5     : {hashlib.md5(hb).hexdigest()}  "
                f"(imported unmodified, not edited)\n"
                f"harness_sha256  : sha256/16 {hashlib.sha256(hb).hexdigest()[:16]}\n"
                f"command_line    : {' '.join(sys.argv)}\n"
                f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED','unset')}\n"
                f"numpy           : {np.__version__}\n"
                f"pandas          : {pd.__version__}\n"
                f"n_spots_by_task : {json.dumps(state.get('n_spots', {}), sort_keys=True)}\n"
                f"embedding_dim   : {json.dumps(state.get('dims', {}), sort_keys=True)}\n"
                f"n_fold_rows     : {len(state.get('fold', []))}\n"
                f"wall_seconds    : {wall:.0f}\n"
                f"wall_by_task    : {json.dumps(state.get('wall', {}), sort_keys=True)}\n"
                f"cqr_seconds_by_task : "
                f"{json.dumps(state.get('cqr_task_seconds', {}), sort_keys=True)}\n"
                f"acceptance      : {'PASS' if ok_all else 'FAIL'}\n"
                f"files_written   : {', '.join(written)}\n"
                f"config_hash     : sha256/16 {chash}\n"
                f"config          : {blob}\n"
                f"plan            : round3_execution_plan.md sections 4.6 and 13.5.1\n")
    print(f"[write] PROVENANCE{suf}.txt (config_hash {chash})", flush=True)


# ==================================================================== timing probe
def timing_probe(args, designs, state):
    """Measure what a CQR and an NB fit cost on this host before the production run.

    Section 4.6's time box only says what to do when a fit is slow; whether 50 genes over
    every fold is feasible at all is a measurement, and it is taken here rather than
    discovered from a job that runs out of wall clock. One cell of each task definition
    given, at each --probe-sizes subsample of that cell's own T.
    """
    rows = []
    sizes = [int(s) for s in args.probe_sizes.split(",") if s]
    for p in args.task_def:
        td = json.load(open(p))
        task = td["task"]
        X, Y, samp, bc, xy, genes = H.load_task(td, args.encoder)
        meta = dict(
            donor_of={s["sample_id"]: s["donor_id"] for s in td["samples"]},
            patient_of={s["sample_id"]: s["hest_patient"] for s in td["samples"]},
            resgroup_of={s["sample_id"]: s["resolution_group"] for s in td["samples"]},
            session_of={s["sample_id"]: s.get("session") for s in td["samples"]})
        hargs = harness_args(args, designs)
        specs = H.build_fold_specs(td, samp, xy, designs, meta, hargs)
        H.size_match_groups(specs, args.size_match)
        sp = next((s for s in specs
                   if int(H.apply_size_match(s, task).sum()) >= H.MIN_T_SPOTS), None)
        if sp is None:
            continue
        Tm = H.apply_size_match(sp, task)
        t0 = time.time()
        pipe, A, reg, ridge_alpha = H.fit_base(X[Tm], Y[Tm])
        t_base = time.time() - t0
        CNT, cinfo = load_counts(task, samp, bc, genes, args.counts_dir, args.counts_tol)
        gi = gene_subset(len(genes), args.probe_genes)
        for n in sizes:
            if n > A.shape[0]:
                continue
            rng = np.random.default_rng(zlib.crc32(f"{task}|probe|{n}".encode()))
            sel = rng.choice(A.shape[0], size=n, replace=False)
            As, Ys = A[sel], Y[Tm][sel].astype(np.float64)
            for j in gi:
                for q in CQR_QUANTILES:
                    t0 = time.time()
                    st = "ok"
                    try:
                        QuantileRegressor(quantile=q, alpha=0.0,
                                          solver=CQR_SOLVER).fit(As, Ys[:, j])
                    except Exception as e:
                        st = f"{type(e).__name__}"
                    rows.append(dict(task=task, encoder=args.encoder, design=sp["design"],
                                     fold=sp["fold"], n_T_natural=int(Tm.sum()),
                                     n_used=n, fit="cqr", detail=f"q={q}",
                                     gene=genes[j], seconds=round(time.time() - t0, 3),
                                     status=st, base_fit_seconds=round(t_base, 2)))
                    print(f"  [probe] {task} cqr q={q} n={n} gene={genes[j]} "
                          f"{rows[-1]['seconds']}s {st}", flush=True)
                if CNT is not None:
                    cs = CNT[Tm][sel][:, j]
                    ok = np.isfinite(cs)
                    for solver in [s for s in args.probe_nb_solvers.split(",") if s]:
                        for tolv in (1e-4, args.nb_tol):
                            t0 = time.time()
                            st, dev, sres, nit = "ok", np.nan, np.nan, -1
                            try:
                                gl = PoissonRegressor(
                                    alpha=ridge_alpha, fit_intercept=True,
                                    max_iter=NB_MAX_ITER, tol=tolv,
                                    solver=solver).fit(As[ok], cs[ok])
                                mu = np.maximum(gl.predict(As[ok]), NB_MIN_MU)
                                dev = poisson_deviance(cs[ok], mu)
                                sres = float(abs(cs[ok].sum() - mu.sum())
                                             / max(cs[ok].sum(), 1e-12))
                                nit = int(np.max(np.atleast_1d(
                                    getattr(gl, "n_iter_", -1))))
                            except Exception as e:
                                st = f"{type(e).__name__}"
                            rows.append(dict(
                                task=task, encoder=args.encoder, design=sp["design"],
                                fold=sp["fold"], n_T_natural=int(Tm.sum()), n_used=n,
                                fit="nb_poisson", detail=f"{solver}|tol={tolv:g}",
                                gene=genes[j], seconds=round(time.time() - t0, 3),
                                status=st, base_fit_seconds=round(t_base, 2),
                                deviance=dev, score_residual=sres, n_iter=nit))
                            print(f"  [probe] {task} nb {solver} tol={tolv:g} n={n} "
                                  f"{rows[-1]['seconds']}s dev={dev:.6g} "
                                  f"score_res={sres:.3e} iters={nit} {st}", flush=True)
        del X, Y, CNT
    state["timing"] = rows
    return pd.DataFrame(rows)


# ==================================================================== merge and figure
def _style():
    """The figure-style ladder through rcParams so the figure renders the same wherever it
    runs: three font sizes mapped to role (8 base, 7 annotation, 6 ticks), outward ticks,
    frameless legends, 300 dpi."""
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


# One hue per score, threaded through every panel. `abs` is the reference and is drawn in
# neutral grey; the alarm hue is reserved for the two diagnostics.
PAL = {"abs": "#8C8C8C", "scaled": "#4C72B0", "scaled_clip": "#55A868",
       "cqr": "#8172B3", "nb": "#DD8452", "nb_conformal": "#937860",
       "HCP (A3, alpha 0.2)": "#4C72B0", "abs recentred (oracle)": "#C44E52"}
LABEL = {"abs": "abs", "scaled": "scaled (unclipped)", "scaled_clip": "scaled, clipped",
         "cqr": "CQR", "nb": "NB (model level)", "nb_conformal": "NB, conformalised"}


def width_at_coverage(fold, alpha, target=None):
    """Per (task, design, encoder, score): the width at the nominal level beside its
    realised coverage, and the width at the grid level whose realised coverage equals the
    target, by monotone interpolation over the alpha grid.

    The second pair picks the level from TEST coverage, so it is a diagnostic and is
    labelled as one in the file. `matched_in_range` says whether the target lay inside the
    grid's realised-coverage range; outside it nothing is extrapolated.
    """
    target = (1.0 - alpha) if target is None else target
    key = ["task", "label_set", "encoder", "design", "score", "subset", "gene_subset"]
    cell = (fold.groupby(key + ["alpha"], dropna=False)
            .agg(coverage=("coverage", "mean"), width_mean=("width_mean", "mean"),
                 width_median=("width_median", "mean"),
                 n_folds=("fold", "nunique"), n_genes=("n_genes", "min"),
                 is_conformal=("is_conformal", "first"),
                 coverage_sd=("coverage", "std"),
                 frac_infinite=("frac_infinite", "mean")).reset_index())
    out = []
    for k, g in cell.groupby(key, dropna=False):
        g = g.sort_values("coverage")
        nom = g[np.isclose(g["alpha"], alpha)]
        row = dict(zip(key, k))
        row.update(method=row["score"], source="A4a",
                   n_folds=int(g["n_folds"].max()), n_genes=int(g["n_genes"].min()),
                   is_conformal=bool(g["is_conformal"].iloc[0]),
                   alpha_nominal=alpha,
                   coverage_nominal=float(nom["coverage"].iloc[0]) if len(nom) else np.nan,
                   coverage_sd_nominal=(float(nom["coverage_sd"].iloc[0])
                                        if len(nom) else np.nan),
                   width_mean_nominal=(float(nom["width_mean"].iloc[0])
                                       if len(nom) else np.nan),
                   width_median_nominal=(float(nom["width_median"].iloc[0])
                                         if len(nom) else np.nan),
                   frac_infinite_nominal=(float(nom["frac_infinite"].iloc[0])
                                          if len(nom) else np.nan),
                   target_coverage=target, n_grid_levels=int(len(g)))
        inr = bool(len(g) >= 2 and g["coverage"].min() <= target <= g["coverage"].max())
        row["matched_in_range"] = inr
        row["matched_uses_test_labels"] = True
        row["width_mean_at_target"] = (float(np.interp(target, g["coverage"],
                                                       g["width_mean"])) if inr else np.nan)
        row["width_median_at_target"] = (float(np.interp(target, g["coverage"],
                                                         g["width_median"]))
                                         if inr else np.nan)
        row["alpha_at_target"] = (float(np.interp(target, g["coverage"],
                                                  g["alpha"])) if inr else np.nan)
        row["subset_difference_list"] = SUBSET_DIFFERENCE_LIST.get(row["subset"], "")
        out.append(row)
    return pd.DataFrame(out)


def _decile_prefer_source(m):
    """Order a4_by_decile rows so that drop_duplicates(keep='first') keeps the RIGHT
    source, not the alphabetically first filename.

    a4_by_decile rows are per-fold aggregates over the cells the writing invocation ran,
    so two invocations that both scored a fold do NOT produce the same row. `abs` is the
    one score written by both a main invocation and the CQR one, and the two differ:

      subset `full`       the main invocation covers every repeat and calibration draw of
                          the fold, the CQR invocation only the draw-0, repeat-0 cell
                          (--cqr-cells-only). The main row is the superset and is the one
                          this table means, so it wins.
      subset `cqr_matched` both cover the same cells, but each assigns deciles over its own
                          pooled test predictions, so the bin boundaries differ. The CQR
                          invocation's row wins, because `cqr`'s own rows can only come
                          from there and the point of the matched subset is that `abs` and
                          `cqr` are read inside ONE stratification.

    Every other (score, subset) pair is written by exactly one invocation and carries no
    preference. Sorting is stable, so within a preference class the previous
    filename order is unchanged.
    """
    cqr_src = m["_source"].astype(str).str.contains("cqrmain", regex=False)
    pref = pd.Series(1, index=m.index, dtype=int)
    full = m["subset"].eq("full")
    matched_abs = m["subset"].eq("cqr_matched") & m["score"].eq("abs")
    pref[~(full | matched_abs)] = 0
    pref[full & ~cqr_src] = 0
    pref[matched_abs & cqr_src] = 0
    m = m.copy()
    m["_pref"] = pref
    return m.sort_values("_pref", kind="stable")


def _assert_decile_sources(pre, post, key):
    """Key-exact check after the merge: for every key that BOTH a main and a CQR
    invocation wrote, the kept `full` row must be the main one and the kept
    `cqr_matched` `abs` row must be the CQR one."""
    def flag(d):
        return d["_source"].astype(str).str.contains("cqrmain", regex=False)
    pre, post = pre.copy(), post.copy()
    pre["_iscqr"], post["_iscqr"] = flag(pre), flag(post)
    both = (pre.groupby(key, dropna=False)["_iscqr"]
            .agg(lambda s: bool(s.any() and (~s).any())).rename("_both").reset_index())
    p = post.merge(both, on=key, how="left")
    p["_both"] = p["_both"].fillna(False)
    bad_full = int((p["_both"] & p["subset"].eq("full") & p["_iscqr"]).sum())
    assert bad_full == 0, (
        f"a4_by_decile: {bad_full} `full` rows were kept from a CQR invocation although a "
        f"main invocation wrote the same key; the source preference did not apply")
    bad_m = int((p["_both"] & p["subset"].eq("cqr_matched") & p["score"].eq("abs")
                 & ~p["_iscqr"]).sum())
    assert bad_m == 0, (
        f"a4_by_decile: {bad_m} `cqr_matched` abs rows were kept from a main invocation "
        f"although the CQR invocation wrote the same key")
    n_both = int(both["_both"].sum())
    only_main = int((p["subset"].eq("cqr_matched") & p["score"].eq("abs")
                     & ~p["_iscqr"]).sum())
    print(f"[decile-merge] {n_both} keys written by both a main and a CQR invocation, "
          f"resolved by preference; 0 `full` rows and 0 matched-abs rows kept from the "
          f"wrong side. {only_main} `cqr_matched` abs rows come from a main invocation "
          f"because the CQR invocation never reached that fold.", flush=True)


def merge(args):
    """Merge the per-encoder tables into the deliverable names, add the HCP row from A3 and
    the oracle row, and render the figure. Reads only the CSVs, never the parquets."""
    out = f"{ROOT}/{args.out_dir}"
    written = []
    stems = ["a4_acceptance", "a4_by_fold", "a4_scores_by_task", "a4_by_decile",
             "a4_oracle_recentred", "a4_sigma_clip", "a4_nb_dispersion",
             "a4_nb_guard", "a4_pit", "a4_pit_by_cell", "a4_cqr_fits",
             "a4_counts_join", "a4_skipped", "a4_timing"]
    # The CQR invocations carry `abs` as their own anchor, so `abs` rows arrive twice, once
    # from the main invocation and once from the CQR one, with identical values. They are
    # deduplicated on the natural key and the count of dropped duplicates is printed, so a
    # by-task mean cannot silently double-weight `abs`.
    # Every key carries `alpha` where the table has one, so a row at one level can never
    # deduplicate a row at another.
    DEDUP = {
        "a4_by_fold": ["encoder", "task", "label_set", "design", "fold", "repeat",
                       "cal_draw", "score", "alpha", "subset", "gene_subset"],
        "a4_by_decile": ["encoder", "task", "label_set", "design", "score", "subset",
                         "fold", "stratum_kind", "stratum_value", "alpha"],
        "a4_oracle_recentred": ["encoder", "task", "label_set", "design", "fold",
                                "repeat", "cal_draw", "slide", "alpha"],
        "a4_nb_dispersion": ["encoder", "task", "label_set", "design", "fold", "repeat",
                             "cal_draw", "gene"],
        "a4_nb_guard": ["encoder", "task", "label_set", "design", "fold", "repeat",
                        "cal_draw", "gene"],
        "a4_sigma_clip": ["encoder", "task", "label_set", "design", "fold", "repeat",
                          "cal_draw"],
        "a4_pit_by_cell": ["encoder", "task", "label_set", "design", "fold", "repeat",
                           "cal_draw", "gene"],
    }
    merged = {}
    for stem in stems:
        src = sorted(f for f in _glob.glob(f"{out}/{stem}__*.csv"))
        if not src:
            continue
        m = pd.concat([pd.read_csv(f).assign(_source=os.path.basename(f))
                       for f in src], ignore_index=True)
        # Paragraph columns are dropped from the bulk tables and kept once in
        # a4_difference_lists.csv; per-row they were most of these files' bytes.
        m = m.drop(columns=[c for c in ("difference_list", "subset_difference_list")
                            if c in m.columns])
        ndup = 0
        if stem in DEDUP and all(c in m.columns for c in DEDUP[stem]):
            n0 = len(m)
            if "fold" in m.columns:
                # fold ids are slide names under slide_out, donor ids under donor and
                # integers under random and patient, so a fragment whose folds are all
                # numeric reads back as int64 while its sibling reads back as object.
                # Without this cast the integer 0 and the string "0" are different keys
                # and a collision goes undetected.
                m["fold"] = m["fold"].astype(str)
            pre = None
            if stem == "a4_by_decile":
                m = _decile_prefer_source(m)
                pre = m
            m = m.drop_duplicates(subset=DEDUP[stem], keep="first").reset_index(drop=True)
            ndup = n0 - len(m)
            if stem == "a4_by_decile":
                _assert_decile_sources(pre, m, DEDUP[stem])
                m = m.drop(columns=["_pref"])
        m.to_csv(f"{out}/{stem}.csv", index=False)
        merged[stem] = m
        written.append(f"{stem}.csv")
        print(f"[write] {stem}.csv ({len(m)} rows from {len(src)} files"
              f"{f'; {ndup} duplicate rows dropped' if ndup else ''})", flush=True)

    _difference_list_file(out)
    written.append("a4_difference_lists.csv")
    assert "a4_by_fold" in merged, f"no a4_by_fold__*.csv under {out}"
    fold = merged["a4_by_fold"]

    # ---- the per-cell anchor, recomputed here over EVERY cell of every invocation, so
    # ---- the merged acceptance table carries one anchor that covers the whole stage.
    arows = []
    for enc in [e for e in args.merge_encoders.split(",") if e]:
        prim = fold[fold["primary"] & (fold["subset"] == "full")
                    & (fold["encoder"] == enc)]
        if not len(prim):
            continue
        for tag in ("main", "slideout"):
            a = argparse.Namespace(accept_tag=tag, a1_dir=args.a1_dir,
                                   anchor_tol=args.anchor_tol)
            for r in _anchor_by_cell(prim, a, enc):
                arows.append(dict(encoder=enc, a1_tag=tag, scope="merged, every cell",
                                  **r))
    if arows:
        acc = pd.DataFrame(arows)
        if "a4_acceptance" in merged:
            acc = pd.concat([merged["a4_acceptance"], acc], ignore_index=True)
        acc.to_csv(f"{out}/a4_acceptance.csv", index=False)
        print(f"\n=== A4a MERGED ACCEPTANCE (per-cell anchor over every invocation) ===")
        print(pd.DataFrame(arows)[["encoder", "a1_tag", "check", "n_cells", "value",
                                   "tol", "passed"]].to_string(index=False), flush=True)

    # ---------------- the primary table: width at matched coverage ----------------
    wac = width_at_coverage(fold, args.alpha)

    # HCP at alpha = 0.2 on CCRCC `donor` from A3's committed table, no rerun (13.2 item 5)
    a3p = f"{ROOT}/{A3DIR}/a3_by_fold.csv"
    if os.path.exists(a3p):
        a3 = pd.read_csv(a3p)
        h = a3[(a3["task"] == "CCRCC") & (a3["design"] == "donor")
               & (a3["weighting"] == "W3") & (a3["w3_variant"] == "nominal")
               & (a3["score"] == "abs") & (np.isclose(a3["alpha"], 0.20))
               & (a3["subset"] == "all")]
        assert len(h), f"{a3p}: no W3 nominal abs CCRCC donor rows at alpha 0.20"
        for enc, ge in list(h.groupby("encoder")) + [("all", h)]:
            wac = pd.concat([wac, pd.DataFrame([dict(
                task="CCRCC", label_set="shipped", encoder=enc, design="donor",
                score="abs", subset="full", gene_subset="all",
                method="HCP (A3, alpha 0.2)",
                source=f"A3 {os.path.relpath(a3p, ROOT)}",
                n_folds=int(ge["fold"].nunique()), n_genes=50, is_conformal=True,
                alpha_nominal=0.20,
                coverage_nominal=float(ge["coverage"].mean()),
                coverage_sd_nominal=float(ge["coverage"].std()),
                width_mean_nominal=float(ge["width_mean"].mean()),
                width_median_nominal=float(ge["width_median"].mean()),
                frac_infinite_nominal=float(ge["frac_infinite"].mean()),
                target_coverage=1.0 - args.alpha, n_grid_levels=1,
                matched_in_range=False, matched_uses_test_labels=False,
                width_mean_at_target=np.nan, width_median_at_target=np.nan,
                alpha_at_target=np.nan)])], ignore_index=True)
        print(f"[wac] HCP row(s) added from {os.path.relpath(a3p, ROOT)} "
              f"({len(h)} A3 fold rows)", flush=True)

    # the recentred oracle row, a diagnostic (13.5.1)
    if "a4_oracle_recentred" in merged:
        o = merged["a4_oracle_recentred"]
        o = o[o["slide_ge_min_spots"]]
        for (task, ls, enc, design, cls), g in o.groupby(
                ["task", "label_set", "encoder", "design", "calibration_unit_class"]):
            rs, rn = float(g["ratio_sum"].sum()), int(g["ratio_n"].sum())
            wac = pd.concat([wac, pd.DataFrame([dict(
                task=task, label_set=ls, encoder=enc, design=design, score="abs",
                subset="full", gene_subset="all",
                method=f"abs recentred (oracle), {cls}-calibrated folds",
                source="A4a diagnostic; uses test labels",
                n_folds=int(g["fold"].nunique()), n_genes=int(g["n_genes"].max()),
                is_conformal=False, alpha_nominal=args.alpha,
                coverage_nominal=float(g["coverage_recentred"].mean()),
                coverage_sd_nominal=float(g["coverage_recentred"].std()),
                width_mean_nominal=float(g["w_star_recentred_mean"].mean()),
                width_median_nominal=np.nan,
                frac_infinite_nominal=0.0,
                target_coverage=1.0 - args.alpha, n_grid_levels=1,
                matched_in_range=False, matched_uses_test_labels=True,
                width_mean_at_target=np.nan, width_median_at_target=np.nan,
                alpha_at_target=np.nan,
                oracle_width_ratio_to_abs=(rs / rn if rn else np.nan),
                abs_half_width_mean=float(g["w_hat_abs_mean"].mean()),
                b_s_over_sy_mean=float(g["b_s_over_sy_mean"].mean()))])],
                ignore_index=True)
    # NOTE the width columns here are HALF-widths for the oracle rows and FULL widths for
    # the score rows, so the oracle row carries its ratio to `abs` explicitly and the
    # column is named for what it is.
    wac.loc[wac["method"].str.startswith("abs recentred"),
            "width_is_half_width"] = True
    wac["width_is_half_width"] = wac.get("width_is_half_width", pd.Series(dtype=object)) \
        .fillna(False)
    wac.to_csv(f"{out}/a4_width_at_coverage.csv", index=False)
    written.append("a4_width_at_coverage.csv")
    print(f"[write] a4_width_at_coverage.csv ({len(wac)} rows)", flush=True)

    written += figure(out, fold, wac, merged, args)
    return written


def figure(out, fold, wac, merged, args):
    _style()
    import matplotlib.pyplot as plt
    written = []
    tgt = 1.0 - args.alpha

    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.9))
    hg = wac[(wac["method"] == "HCP (A3, alpha 0.2)") & (wac["encoder"] != "all")]
    og = wac[wac["method"].str.startswith("abs recentred")]
    # Panels a and b are the same quantity on two gene-and-cell subsets, so they share
    # both axes; read side by side they would otherwise imply a difference in width that
    # is only a difference in limits.
    _d = wac[(wac["source"] == "A4a") & (wac["encoder"] != "all")]
    _w = pd.concat([_d["width_mean_nominal"].dropna(),
                    og["width_mean_nominal"].dropna() * 2.0,
                    hg["width_mean_nominal"].dropna()])
    ylim = (float(_w.min()) * 0.8, float(_w.max()) * 1.3)
    xlim = (float(_d["coverage_nominal"].min()) - 0.02,
            float(_d["coverage_nominal"].max()) + 0.02)

    # ---- panels a and b: coverage against width, on the full and the matched subset ----
    for pi, (sname, ttl) in enumerate((
            ("full", "Every gene each score ran on"),
            ("cqr_matched", "Identical cells and genes\nfor all six scores"))):
        ax = axes[pi]
        d = wac[(wac["source"] == "A4a") & (wac["subset"] == sname)
                & wac["coverage_nominal"].notna() & (wac["encoder"] != "all")]
        for sc in SCORES:
            g = d[d["score"] == sc]
            if not len(g):
                continue
            ax.scatter(g["coverage_nominal"], g["width_mean_nominal"], s=9,
                       color=PAL[sc], alpha=0.75, edgecolors="none",
                       label=f"{LABEL[sc]}  ({len(g)})")
        if pi == 0:
            if len(hg):
                ax.scatter(hg["coverage_nominal"], hg["width_mean_nominal"], s=40,
                           marker="D", facecolors="none",
                           edgecolors=PAL["HCP (A3, alpha 0.2)"], linewidths=1.0,
                           label="HCP, CCRCC donor (A3)")
            if len(og):
                ax.scatter(og["coverage_nominal"], og["width_mean_nominal"] * 2.0, s=22,
                           marker="x", color=PAL["abs recentred (oracle)"],
                           alpha=0.8, linewidths=0.8, label="abs recentred (oracle)")
        ax.axvline(tgt, color="0.55", lw=0.7, ls="--")
        ax.annotate(f"nominal {tgt:.2f}", xy=(tgt, 0.985),
                    xycoords=("data", "axes fraction"), rotation=90, ha="right",
                    va="top", fontsize=6, color="0.35")
        # Widths span 0.4 to 27 on the log1p scale, almost all of it from the unclipped
        # sigmahat's blow-up on the small tasks. On a linear axis the other five scores
        # collapse into the bottom tenth of the panel.
        ax.set_yscale("log")
        ax.set_yticks([0.5, 1, 2, 5, 10, 20])
        ax.set_yticklabels(["0.5", "1", "2", "5", "10", "20"])
        ax.set_xlabel("realised coverage")
        if pi == 0:
            ax.set_ylabel(r"mean interval width, $\log(1+y)$")
            ax.annotate("lower and at nominal is better", xy=(0.03, 0.03),
                        xycoords="axes fraction", fontsize=6, color="0.35")
        ax.set_title(ttl)
        ax.set_ylim(*ylim)
        ax.set_xlim(*xlim)
        if pi == 1:
            ax.set_yticklabels([])
        if pi == 0:
            ax.legend(loc="upper left", markerscale=1.5, handletextpad=0.3,
                      borderaxespad=0.15, labelspacing=0.2)

    # ---- panel c: the level grid on one cell, the one the HCP row belongs to ----
    ax = axes[2]
    cell = fold[(fold["task"] == "CCRCC") & (fold["design"] == "donor")
                & (fold["subset"] == "cqr_matched")]
    if not len(cell):
        cell = fold[(fold["design"] == "donor") & (fold["subset"] == "cqr_matched")]
    if not len(cell):
        cell = fold[fold["subset"] == "full"]
    ttl_task = cell["task"].iloc[0] if len(cell) else ""
    ttl_design = cell["design"].iloc[0] if len(cell) else ""
    cv = (cell.groupby(["score", "alpha"])[["coverage", "width_mean"]]
          .mean().reset_index().sort_values("alpha"))
    for sc in SCORES:
        g = cv[cv["score"] == sc].sort_values("coverage")
        if len(g) < 2:
            continue
        ax.plot(g["coverage"], g["width_mean"], "-o", ms=2.2, color=PAL[sc],
                label=LABEL[sc])
    if len(hg):
        ax.scatter(hg["coverage_nominal"], hg["width_mean_nominal"], s=40, marker="D",
                   facecolors="none", edgecolors=PAL["HCP (A3, alpha 0.2)"],
                   linewidths=1.0)
    ax.axvline(tgt, color="0.55", lw=0.7, ls="--")
    ax.set_xlabel("realised coverage")
    ax.set_title(f"{ttl_task} {ttl_design} over the level grid")
    ax.margins(0.06)
    fig.suptitle("Width at matched coverage: a wide interval that covers is not useful",
                 fontsize=8, x=0.005, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(f"{out}/fig_a4_width_at_coverage.png")
    plt.close(fig)
    written.append("fig_a4_width_at_coverage.png")
    print("[write] fig_a4_width_at_coverage.png", flush=True)
    return written


# ============================================================== reported numbers
def report_numbers(args):
    """Every pooled number the stage report quotes, computed here into
    a4_report_numbers.csv so that nothing is retyped from a printed table.

    One row per number: name, scope, value, n, source file, note. Reads only the merged
    CSVs plus A2's committed decile table and round 1's count diagnostics.
    """
    out = f"{ROOT}/{args.out_dir}"
    R = []

    def add(name, scope, value, n, src, note=""):
        R.append(dict(name=name, scope=scope, value=value, n=n, source=src, note=note))

    fold = pd.read_csv(f"{out}/a4_by_fold.csv")
    prim = fold[fold["primary"]]
    wac = pd.read_csv(f"{out}/a4_width_at_coverage.csv")
    acc = pd.read_csv(f"{out}/a4_acceptance.csv")

    # ---------------- A. the anchor
    a = acc[acc["check"].str.startswith("ANCHOR_cell")]
    if len(a):
        add("anchor_cell_max_abs_dcoverage", "all encoders, all cells",
            float(a["value"].max()), int(a["n_cells"].sum()), "a4_acceptance.csv",
            "max over encoders and A1 tags of max |dcoverage| per (fold, repeat, draw) "
            "against a1_by_slide")
    b = acc[acc["check"].str.startswith("ANCHOR_abs_reproduces")
            | acc["check"].str.startswith("ANCHOR_scaled_reproduces")]
    b = b[b["passed"].astype(str) == "True"]
    if len(b):
        add("anchor_byfold_max_abs_dcoverage", "invocations scoring every cell",
            float(b["value"].max()), int(b["n_cells"].sum()), "a4_acceptance.csv",
            "max |dcoverage| against a1_by_fold, abs and scaled")

    # ---------------- B. the first comparison, scaled against scaled_clip against abs
    for sname in sorted(prim["subset"].unique()):
        p = prim[prim["subset"] == sname]
        for sc in ("abs", "scaled", "scaled_clip"):
            g = p[p["score"] == sc]
            if not len(g):
                continue
            add(f"width_mean_{sc}", f"subset {sname}, alpha {args.alpha}, all cells",
                float(g["width_mean"].mean()), len(g), "a4_by_fold.csv",
                "unweighted mean over (task, design, encoder, fold, repeat, draw) cells")
            add(f"width_median_{sc}", f"subset {sname}, alpha {args.alpha}, all cells",
                float(g["width_median"].mean()), len(g), "a4_by_fold.csv",
                "mean over cells of the within-cell median spot-gene width")
            add(f"coverage_{sc}", f"subset {sname}, alpha {args.alpha}, all cells",
                float(g["coverage"].mean()), len(g), "a4_by_fold.csv", "")
        key = ["encoder", "task", "label_set", "design", "fold", "repeat", "cal_draw"]
        w = p[p["score"].isin(("scaled", "scaled_clip", "abs"))].pivot_table(
            index=key, columns="score", values="width_mean")
        w = w.dropna()
        if len(w) and {"scaled", "scaled_clip"} <= set(w.columns):
            add("width_ratio_scaled_clip_over_scaled",
                f"subset {sname}, alpha {args.alpha}", 
                float((w["scaled_clip"] / w["scaled"]).mean()), len(w),
                "a4_by_fold.csv", "mean over cells of the per-cell width ratio")
            add("frac_cells_scaled_clip_narrows_scaled_by_half",
                f"subset {sname}, alpha {args.alpha}",
                float(((w["scaled_clip"] / w["scaled"]) < 0.5).mean()), len(w),
                "a4_by_fold.csv",
                "memo prediction 1 asks for a narrowing of more than half")
            add("width_ratio_scaled_over_abs", f"subset {sname}, alpha {args.alpha}",
                float((w["scaled"] / w["abs"]).mean()), len(w), "a4_by_fold.csv", "")

    sig = pd.read_csv(f"{out}/a4_sigma_clip.csv")
    if len(sig):
        add("frac_folds_lower_clip_binds", "every fold with scaled_clip",
            float(sig["lower_clip_binds"].mean()), len(sig), "a4_sigma_clip.csv",
            "binds = at least one TEST sigmahat below the lower clip, so the clip "
            "changes that fold's intervals")
        add("frac_folds_p1_of_sigma_below_harness_floor", "every fold with scaled_clip",
            float(sig["p1_below_floor"].mean()), len(sig), "a4_sigma_clip.csv",
            "the 1st percentile of the calibration sigmahat is itself below SIGMA_FLOOR, "
            "so the lower clip IS the floor and the percentile never acts")
        add("mean_frac_cal_sigma_below_floor", "every fold with scaled_clip",
            float(sig["frac_cal_raw_below_floor"].mean()), len(sig),
            "a4_sigma_clip.csv",
            "the extrapolation defect: an unconstrained ridge on absolute residuals "
            "predicting a negative sigmahat")
        add("mean_frac_test_sigma_clipped_high", "every fold with scaled_clip",
            float(sig["frac_test_clipped_high"].mean()), len(sig),
            "a4_sigma_clip.csv", "")

    # ---------------- C. the predicted-value decile
    dec = pd.read_csv(f"{out}/a4_by_decile.csv")
    for sname in sorted(dec["subset"].unique()):
        d = dec[(dec["subset"] == sname) & (dec["stratum_value"] == N_DECILES - 1)]
        for sc in sorted(d["score"].unique()):
            g = d[d["score"] == sc]
            add(f"top_decile_coverage_{sc}", f"subset {sname}, all designs",
                float(g["n_covered"].sum() / g["n_spot_gene"].sum()),
                int(g["n_spot_gene"].sum()), "a4_by_decile.csv",
                "pooled over task, design, encoder and fold; decile 9 of the base "
                "head's predicted value within task and gene")
            for dsg in sorted(g["design"].unique()):
                h = g[g["design"] == dsg]
                add(f"top_decile_coverage_{sc}__{dsg}", f"subset {sname}, design {dsg}",
                    float(h["n_covered"].sum() / h["n_spot_gene"].sum()),
                    int(h["n_spot_gene"].sum()), "a4_by_decile.csv", "")
    a2 = sorted(_glob.glob(f"{ROOT}/results/round3/A2_conditional/a2_strata__*.csv"))
    if a2:
        m = pd.concat([pd.read_csv(f) for f in a2], ignore_index=True)
        m = m[(m["stratum_kind"] == "predicted_value_decile")
              & (m["stratum_value"] == N_DECILES - 1)
              & (m["label_set"] != "audited")]
        for dsg in sorted(m["design"].unique()):
            h = m[m["design"] == dsg]
            add(f"A2_top_decile_coverage_abs__{dsg}", f"A2 baseline, design {dsg}",
                float(h["n_covered"].sum() / h["n_spot_gene"].sum()),
                int(h["n_spot_gene"].sum()),
                "results/round3/A2_conditional/a2_strata__*.csv",
                "A2's own committed decile table, IDC audited excluded; the memo's "
                "prediction 2 quotes 0.68 for this quantity")

    # ---------------- D. width at matched coverage
    w = wac[(wac["source"] == "A4a") & (wac["encoder"] != "all")]
    for sname in sorted(w["subset"].dropna().unique()):
        for sc in sorted(w[w["subset"] == sname]["score"].unique()):
            g = w[(w["subset"] == sname) & (w["score"] == sc)]
            add(f"width_mean_at_cov90_{sc}", f"subset {sname}",
                float(g["width_mean_at_target"].mean()),
                int(g["width_mean_at_target"].notna().sum()),
                "a4_width_at_coverage.csv",
                "width at the grid level whose realised coverage is 0.90; a DIAGNOSTIC, "
                "the level is picked with test labels")
            add(f"width_median_at_cov90_{sc}", f"subset {sname}",
                float(g["width_median_at_target"].mean()),
                int(g["width_median_at_target"].notna().sum()),
                "a4_width_at_coverage.csv", "")
            add(f"frac_cells_cov90_in_grid_{sc}", f"subset {sname}",
                float(g["matched_in_range"].mean()), len(g),
                "a4_width_at_coverage.csv",
                "0.90 lies inside the level grid's realised-coverage range; nothing is "
                "extrapolated outside it")
    h = wac[wac["method"] == "HCP (A3, alpha 0.2)"]
    if len(h):
        hh = h[h["encoder"] == "all"]
        if len(hh):
            add("HCP_alpha020_CCRCC_donor_coverage", "A3 W3 nominal, abs, all encoders",
                float(hh["coverage_nominal"].iloc[0]), int(hh["n_folds"].iloc[0]),
                "results/round3/A3_weighted/a3_by_fold.csv", "no rerun; 13.2 item 5")
            add("HCP_alpha020_CCRCC_donor_width_mean", "A3 W3 nominal, abs, all encoders",
                float(hh["width_mean_nominal"].iloc[0]), int(hh["n_folds"].iloc[0]),
                "results/round3/A3_weighted/a3_by_fold.csv", "")
            add("HCP_alpha020_CCRCC_donor_width_median",
                "A3 W3 nominal, abs, all encoders",
                float(hh["width_median_nominal"].iloc[0]), int(hh["n_folds"].iloc[0]),
                "results/round3/A3_weighted/a3_by_fold.csv", "")
    orc = pd.read_csv(f"{out}/a4_oracle_recentred.csv")
    orc = orc[orc["slide_ge_min_spots"]]
    for cls in sorted(orc["calibration_unit_class"].unique()):
        g = orc[orc["calibration_unit_class"] == cls]
        rs, rn = float(g["ratio_sum"].sum()), int(g["ratio_n"].sum())
        add("oracle_recentred_width_ratio_to_abs", f"{cls}-calibrated folds",
            rs / rn if rn else np.nan, rn, "a4_oracle_recentred.csv",
            "mean over (test slide, gene) of w_star(recentred) / w_hat(abs); "
            "a DIAGNOSTIC, uses test labels for the offset and the half-width")
        add("oracle_recentred_coverage", f"{cls}-calibrated folds",
            float(g["coverage_recentred"].mean()), len(g), "a4_oracle_recentred.csv",
            "by construction the ceil((1-alpha) n)/n order statistic on the slide")
        add("abs_coverage_on_same_slides", f"{cls}-calibrated folds",
            float(g["coverage_abs"].mean()), len(g), "a4_oracle_recentred.csv", "")
        add("b_s_over_s_y_mean", f"{cls}-calibrated folds",
            float(g["b_s_over_sy_mean"].mean()), len(g), "a4_oracle_recentred.csv",
            "A2 reported this near 0.5 on unit-calibrated slides")

    # ---------------- E. the NB head
    disp = pd.read_csv(f"{out}/a4_nb_dispersion.csv")
    cd = f"{ROOT}/{args.count_diag}"
    if os.path.exists(cd) and len(disp):
        fano = pd.read_csv(cd)[["task", "gene", "fano", "nb_alpha_mom"]]
        j = disp.merge(fano, on=["task", "gene"], how="left")
        add("nb_alpha_g_mean", "every (task, design, fold, gene) NB fit",
            float(j["alpha_g"].mean()), len(j), "a4_nb_dispersion.csv", "")
        add("nb_alpha_g_oos_mean", "every (task, design, fold, gene) NB fit",
            float(j["alpha_g_oos"].mean()), int(j["alpha_g_oos"].notna().sum()),
            "a4_nb_dispersion.csv",
            "the SAME moment estimator on the calibration set's out-of-sample Pearson "
            "residuals; a diagnostic, not the plan's estimator and not used for any "
            "interval")
        add("marginal_fano_mean", "the same (task, gene) pairs",
            float(j["fano"].mean()), int(j["fano"].notna().sum()),
            "results/tailored/counts/count_diagnostics.csv",
            "round 1's marginal Fano factor on the raw counts")
        add("nb_alpha_g_over_marginal_alpha_mom_mean", "the same (task, gene) pairs",
            float((j["alpha_g"] / j["nb_alpha_mom"]).mean()),
            int(j["nb_alpha_mom"].notna().sum()), "a4_nb_dispersion.csv",
            "conditional over marginal NB2 dispersion; the round-1 review's question")
        add("frac_nb_alpha_g_exactly_zero", "every NB fit",
            float((j["alpha_g"] <= 0).mean()), len(j), "a4_nb_dispersion.csv",
            "the moment estimator is max(0, .) and collapses wherever the in-sample "
            "residual variance falls below the Poisson mean")
        add("frac_nb_alpha_g_oos_exactly_zero", "every NB fit",
            float((j["alpha_g_oos"] <= 0).mean()),
            int(j["alpha_g_oos"].notna().sum()), "a4_nb_dispersion.csv", "")
        add("nb_deviance_ratio_mean", "every NB fit",
            float(j["deviance_ratio"].mean()),
            int(j["deviance_ratio"].notna().sum()), "a4_nb_dispersion.csv",
            "fitted Poisson deviance over the intercept-only deviance on T; small "
            "values are the in-sample overfit that collapses alpha_g")
        for tk in sorted(j["task"].unique()):
            g = j[j["task"] == tk]
            add("frac_nb_alpha_g_exactly_zero", f"task {tk}",
                float((g["alpha_g"] <= 0).mean()), len(g), "a4_nb_dispersion.csv", "")
            add("nb_deviance_ratio_mean", f"task {tk}",
                float(g["deviance_ratio"].mean()), len(g), "a4_nb_dispersion.csv", "")
    gd = pd.read_csv(f"{out}/a4_nb_guard.csv")
    if len(gd):
        add("nb_guard_fail_count", "every NB fit",
            int((~gd["guard_pass"].astype(bool)).sum()), len(gd), "a4_nb_guard.csv",
            "deviance finite, no worse than intercept-only, and intercept score "
            "residual under the tolerance; the library flag is recorded and not used")
        add("nb_max_score_residual", "every NB fit",
            float(gd["score_residual"].max()),
            int(gd["score_residual"].notna().sum()), "a4_nb_guard.csv", "")
        add("nb_max_n_iter", "every NB fit", int(gd["n_iter"].max()), len(gd),
            "a4_nb_guard.csv", f"max_iter {NB_MAX_ITER}")
    pit = pd.read_csv(f"{out}/a4_pit.csv")
    if len(pit):
        for dsg in sorted(pit["design"].unique()):
            g = pit[pit["design"] == dsg]
            add("nb_pit_ks_pooled_median", f"design {dsg}",
                float(g["ks_pooled_from_hist"].median()), len(g), "a4_pit.csv",
                "pooled over folds per (task, gene), read off a 1000-bin histogram so "
                "resolved to 1e-3")
            add("nb_pit_ks_cell_median", f"design {dsg}",
                float(g["ks_cell_median"].median()), len(g), "a4_pit.csv",
                "median over (task, gene) of the median exact per-cell KS")
            add("nb_log_score_mean", f"design {dsg}",
                float(g["log_score_mean"].mean()), len(g), "a4_pit.csv",
                "negative log predictive mass at the observed count")
        for tk in sorted(pit["task"].unique()):
            g = pit[(pit["task"] == tk) & (pit["design"] == "random")]
            if len(g):
                add("nb_pit_ks_pooled_median", f"task {tk}, design random",
                    float(g["ks_pooled_from_hist"].median()), len(g), "a4_pit.csv", "")
    for sname in sorted(prim["subset"].unique()):
        for dsg in sorted(prim["design"].unique()):
            p = prim[(prim["subset"] == sname) & (prim["design"] == dsg)]
            for sc in sorted(p["score"].unique()):
                g = p[p["score"] == sc]
                add(f"coverage_{sc}", f"subset {sname}, design {dsg}",
                    float(g["coverage"].mean()), len(g), "a4_by_fold.csv", "")
                add(f"width_mean_{sc}", f"subset {sname}, design {dsg}",
                    float(g["width_mean"].mean()), len(g), "a4_by_fold.csv", "")

    # ---------------- F. CQR scope actually run
    cq = pd.read_csv(f"{out}/a4_cqr_fits.csv")
    if len(cq):
        add("cqr_fits_total", "every encoder and task", len(cq), len(cq),
            "a4_cqr_fits.csv", "")
        add("cqr_seconds_total", "every encoder and task",
            float(cq["seconds"].sum()), len(cq), "a4_cqr_fits.csv", "")
        add("cqr_fits_subsampled", "every encoder and task",
            int(cq["subsample_fallback"].astype(bool).sum()), len(cq),
            "a4_cqr_fits.csv", "")
        add("cqr_fit_failures", "every encoder and task",
            int(cq["failure"].fillna("").astype(str).str.len().gt(0).sum()), len(cq),
            "a4_cqr_fits.csv", "")
        for tk in sorted(cq["task"].unique()):
            g = cq[cq["task"] == tk]
            add("cqr_folds_covered", f"task {tk}", int(g["fold"].nunique()),
                int(len(g)), "a4_cqr_fits.csv",
                "distinct fold labels; `random` and `patient` share fold labels by "
                "construction so this is a lower bound on the design-fold count")
            add("cqr_n_T_used_max", f"task {tk}", int(g["n_T_used"].max()), len(g),
                "a4_cqr_fits.csv", "")

    # ---------------- G. the raw-count join
    cj = pd.read_csv(f"{out}/a4_counts_join.csv")
    if len(cj):
        add("counts_min_frac_joined", "every task and encoder",
            float(cj["frac_joined"].min()), len(cj), "a4_counts_join.csv", "")
        add("counts_max_abs_log1p_minus_Y", "every task and encoder",
            float(cj["max_abs_log1p_minus_Y"].max()),
            int(cj["max_abs_log1p_minus_Y"].notna().sum()), "a4_counts_join.csv",
            "the raw-count table and the harness describe the same spots")
    sk = f"{out}/a4_skipped.csv"
    if os.path.exists(sk):
        s = pd.read_csv(sk)
        add("cells_skipped", "every invocation", len(s), len(s), "a4_skipped.csv",
            "cells whose T or C fell below the harness minima")

    d = pd.DataFrame(R)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d.to_csv(f"{out}/a4_report_numbers.csv", index=False)
    print(f"[write] a4_report_numbers.csv ({len(d)} rows)", flush=True)
    return ["a4_report_numbers.csv"]


# ======================================================================== main
def main(argv=None):
    global ROOT
    args = parse_args(argv or sys.argv[1:])
    t0 = time.time()
    if args.root:
        # --merge only: the per-encoder CSVs are read from a local copy of the results
        # tree, so the deliverable tables and the figure can be built off the cluster.
        ROOT = args.root
        print(f"[root] overridden to {ROOT}", flush=True)
    if args.merge:
        w = merge(args)
        if args.report_numbers:
            w += report_numbers(args)
        print(f"\n[done] merge {time.time()-t0:.0f}s; {len(w)} files", flush=True)
        return 0

    enc = args.encoder
    designs = [d for d in args.designs.split(",") if d]
    scores = [s for s in args.scores.split(",") if s]
    alphas = sorted({round(float(a), 6) for a in args.alpha_grid.split(",") if a}
                    | {round(args.alpha, 6)})
    for d in designs:
        assert d in H.DESIGNS, f"unknown design {d}"
    for s in scores:
        assert s in SCORES, f"unknown score {s}"

    tds = []
    for p in args.task_def:
        td = json.load(open(p))
        assert td["task_def_version"] == 1, f"{p}: task_def_version {td['task_def_version']}"
        td["_path"] = p
        tds.append(td)

    out = f"{ROOT}/{args.out_dir}"
    suf = f"__{enc}{args.tag}"
    cfg = dict(stage="round3_A4a", script="code/scripts/round3_a4_scores.py", encoder=enc,
               tasks=[f"{t['task']}/{t['label_set']}" for t in tds],
               task_defs=[os.path.relpath(os.path.abspath(t["_path"]), ROOT) for t in tds],
               designs=designs, fit_designs=args.fit_designs, scores=scores,
               alpha=args.alpha, alpha_grid=alphas,
               sigma_clip_lo_pct=SIGMA_CLIP_LO_PCT, sigma_clip_hi_pct=SIGMA_CLIP_HI_PCT,
               sigma_floor=H.SIGMA_FLOOR,
               cqr_quantiles=list(CQR_QUANTILES), cqr_solver=CQR_SOLVER,
               cqr_genes=args.cqr_genes, cqr_designs=args.cqr_designs,
               cqr_max_folds=args.cqr_max_folds, cqr_max_draws=args.cqr_max_draws,
               cqr_timebox_s=args.cqr_timebox_s, cqr_subsample=args.cqr_subsample,
               cqr_presubsample=args.cqr_presubsample,
               cqr_budget_s=args.cqr_budget_s,
               cqr_cells_only=args.cqr_cells_only,
               cqr_mark_only=args.cqr_mark_only,
               nb_gene_set="union of the NB and CQR evenly spaced subsets",
               nb_genes=args.nb_genes, nb_max_iter=NB_MAX_ITER,
               nb_solver=args.nb_solver, nb_tol=args.nb_tol,
               nb_score_tol=args.nb_score_tol,
               nb_l2="same as the mean head: ALPHA_NUM/(n_components*n_genes)",
               counts_dir=args.counts_dir, counts_tol=args.counts_tol,
               n_deciles=N_DECILES, pit_bins_fine=PIT_BINS_FINE,
               n_cal_draws=args.n_cal_draws, spot_cal_draws=args.spot_cal_draws,
               n_repeats=args.n_repeats, max_folds=args.max_folds,
               size_match=args.size_match, min_slide_spots=H.MIN_SLIDE_SPOTS,
               min_T_spots=H.MIN_T_SPOTS, min_C_spots=H.MIN_C_SPOTS,
               timing_probe=args.timing_probe, probe_sizes=args.probe_sizes,
               probe_genes=args.probe_genes,
               base_predictor="imported unmodified from round3_a0_harness.fit_base",
               seed_source="zlib.crc32 via the harness")
    blob = json.dumps(cfg, sort_keys=True)
    chash = hashlib.sha256(blob.encode()).hexdigest()[:16]
    print(f"[config] sha256/16 {chash}\n{blob}", flush=True)

    state = dict(encoder=enc, alpha=args.alpha, fold=[], pg=[], sigma=[], decile=[],
                 oracle=[], nbdisp=[], nbguard=[], cqr=[], counts_join=[], skipped=[],
                 pit_cell=[], pithist={}, dims={}, n_spots={}, wall={},
                 cqr_task_seconds={}, folds_done=set(), timing=[])

    if args.timing_probe:
        d = timing_probe(args, designs, state)
        os.makedirs(out, exist_ok=True)
        d.to_csv(f"{out}/a4_timing{suf}.csv", index=False)
        print(f"\n[write] a4_timing{suf}.csv ({len(d)} rows)", flush=True)
        if len(d):
            print(d.groupby(["task", "fit", "n_used"])["seconds"]
                  .agg(["count", "mean", "max"]).round(3).to_string(), flush=True)
        provenance(out, suf, cfg, blob, chash, state, time.time() - t0,
                   [f"a4_timing{suf}.csv"], True, "A4a timing probe")
        return 0

    for td in tds:
        state["wall"][f"{td['task']}/{td['label_set']}"] = round(
            run_task(td, enc, args, designs, scores, alphas, state), 1)

    acc, ok_all = acceptance(state, args, enc)
    written = write_outputs(out, suf, state, args, enc, acc, ok_all)
    provenance(out, suf, cfg, blob, chash, state, time.time() - t0, written, ok_all,
               "A4a")
    print(f"\n[done] {time.time()-t0:.0f}s  acceptance="
          f"{'PASS' if ok_all else 'FAIL'}", flush=True)
    return 0 if ok_all else 5


if __name__ == "__main__":
    sys.exit(main())
