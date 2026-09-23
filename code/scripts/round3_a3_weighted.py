#!/usr/bin/env python
"""Round 3, stage A3: weighted and hierarchical conformal under slide and session shift.

Stage: A3 (round3_execution_plan.md section 4.5 as amended by section 12.4, which transcribes
docs/decisions/round3_A1_decisions.md). Gate stage.

THIS SCRIPT DOES NOT EDIT THE HARNESS. It imports `round3_a0_harness.py` from the same
directory as a module and reuses its data loading, its base predictor, its calibration-unit
rule, its fold enumeration and its size matching unchanged, so every A3 fold is an A1 fold by
construction rather than by re-derivation. The only thing A3 adds is what happens to the
calibration scores after they are computed.

Reproducing A1's splits requires enumerating the same design set A1 enumerated, because
size_match_groups() takes its per-task n_match over every design requested in the run. So the
two invocations mirror A1's two:

  main      --designs random,patient,donor   over the eleven task files
  slideout  --designs slide_out              over PRAD, READ, IDC_audited

and the `none` weighting's per-fold coverage is checked against
results/round3/A1_coverage/a1_by_fold__<enc>__<tag>.csv as a fourth acceptance check, beyond
the three the plan requires.

SCORES (memo section on scores; plan section 12.4).
  abs          s = |y - yhat|, the primary score.
  scaled_clip  s = |y - yhat| / sigmahat, with sigmahat CLIPPED to the 1st and 99th
               percentiles of the CALIBRATION set's own sigmahat values, both on C and on E.
               Unclipped `scaled` is not run here; A4 compares them. Because the sigmahat
               ridge is unconstrained in sign, the lower clip is additionally floored at the
               harness's SIGMA_FLOOR and the rate at which that guard binds is recorded.

WEIGHTINGS, and the difference list for each, written before any result is named.
  none  every calibration spot weight 1 and the test point's weight 1. Run through the same
        weighted-quantile code path as the rest, so that the `none` rows cannot drift from
        the weighted ones by an implementation difference; with equal weights the weighted
        quantile IS the ceil((n+1)(1-alpha))/n order statistic.
  W1    logistic regression on the PCA-256 features from the SAME PCA fit on T, class
        balanced, L2 at a fixed C, separating C (label 0) from E (label 1).
        w(z) = [p(1|z)/p(0|z)] * (n_C/n_E), clipped at the 99.5th percentile of the
        calibration weights. SEES: everything the encoder represents, which includes the
        slide signature, the stain, the section thickness and the scanner, not only biology.
  W1b   the same classifier on the eight morphology_v2 covariates only. SEES: tissue
        composition only, and nothing that identifies the slide as an image.
  W2    ratio of test to calibration proportions within cells of (resolution_group,
        session). SEES: resolution group and session, and nothing else. A test cell with no
        calibration mass has no finite weight, so the fold is flagged no_support and falls
        back to unweighted, which is reported rather than hidden.
  W3    HCP. For calibration spot i in unit k with N_k spots, w_i = 1/N_k, and the test
        point's weight is 1, so each of the K units and the test point carries 1/(K+1) of the
        normalised mass. The unit is the fold's own recorded calibration_unit. SEES: the unit
        structure, and no features at all. Run at alpha = 0.10 and 0.20. Where the weighted
        quantile is infinite, which happens exactly when K + 1 < 1/alpha, the interval is
        RECORDED AS INFINITE and counted, and a second row reports the interval at the
        largest feasible level 1 - 1/(K+1) (the maximum calibration score) with its realised
        coverage beside its guaranteed level K/(K+1). A finite interval is never substituted
        for an infinite one.

WEIGHTED QUANTILE (plan section 4.5). For each test point,
  qhat = inf{ q : sum_{i in C} wtilde_i 1[s_i <= q] >= 1 - alpha },
  wtilde_i = w(z_i) / (sum_{j in C} w(z_j) + w(z_test)),
the test point's own weight in the normaliser. Scores are sorted once per (fold, gene) and
the weight cumulative sum reused across every test point.

n_eff = (sum_i w_i)^2 / sum_i w_i^2 over calibration spots, reported as the median over a
test slide's spots, and also as a fraction of the calibration size.

TWO AGGREGATION CONVENTIONS, kept apart on purpose and named in the column names.
  coverage, width_mean, interval_score are the unweighted mean over (test slide, gene) cells
  with at least MIN_SLIDE_SPOTS test spots, which is the chain a1_by_fold uses, so the `none`
  rows are directly comparable to A1's committed table.
  width_median and width_mean_spotgene are over the fold's individual finite (spot, gene)
  widths, which is the only footing on which a median is meaningful once the weighted
  quantile varies from test point to test point.

Outputs under results/round3/A3_weighted/, summaries before parquets:
  a3_acceptance__<enc><tag>.csv   the four checks, written and printed FIRST
  a3_by_fold__<enc><tag>.csv      per (fold, score, weighting, alpha, variant)
  a3_by_slide__<enc><tag>.csv     per test slide
  a3_by_task__<enc><tag>.csv      per (task, design, score, weighting, alpha, variant)
  a3_weights__<enc><tag>.csv      per fold: AUC, clip rates, n_eff, no_support, K, sigma clips
  a3_pergene__<enc><tag>.parquet  per (fold, slide, gene), explicit pa.schema
  PROVENANCE__<enc><tag>.txt

Usage:
  round3_a3_weighted.py <encoder> --task-def <file> [--designs ...] [--tag ...]
"""
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import zlib

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

# --------------------------------------------------- import the A0 harness, unedited
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "round3_a0_harness", os.path.join(_HERE, "round3_a0_harness.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)

ROOT = H.ROOT
A1DIR = "results/round3/A1_coverage"

# ---- W1 and W1b classifier. Fixed, not tuned: a tuned C would make the weights a function
# ---- of a selection procedure run on C and E, which is the thing the weights are meant to
# ---- measure. Declared in the config hash and in the stage report.
W1_C = 1.0
W1_MAX_ITER = 500
W1_CLIP_PCT = 99.5

# ---- scaled_clip percentiles, from the memo.
SIGMA_CLIP_LO_PCT = 1.0
SIGMA_CLIP_HI_PCT = 99.0

ALPHAS = (0.10, 0.20)
WEIGHTINGS = ("none", "W1", "W1b", "W2", "W3")

# The eight morphology_v2 covariates: nuclear count, mean and median area, five class
# fractions. Named explicitly so a change in the parquet's column set is an error and not a
# silently smaller feature matrix.
MORPH_COVARS = ("n_nuclei", "area_mean", "area_median", "frac_connective", "frac_dead",
                "frac_epithelial", "frac_inflammatory", "frac_neoplastic")

# Relative nudge on the weighted-quantile threshold. With equal weights the cumulative sum is
# 1, 2, ..., n exactly while (1-alpha)*(n+1) is a float product, so a threshold that should
# land exactly on an integer can land one ULP above it and select the next order statistic.
# The nudge is 1e-12 relative, twelve orders of magnitude smaller than any weight difference
# that carries information, and it is what makes the `random` W3 acceptance check exact.
QTOL = 1e-12

DIFFERENCE_LIST = {
    "none": "no weights; every calibration spot and the test point carry equal mass. Sees "
            "nothing.",
    "W1": "sees everything the encoder represents, which includes the slide signature, stain "
          "and scanner, not only biology. Trained on the PCA-256 features of C against E "
          "from the PCA fit on T.",
    "W1b": "sees tissue composition only: nuclear count, mean and median nuclear area and "
           "the five class fractions. It cannot see the slide as an image. Fitted and "
           "evaluated on the morphology-joined subset of spots, with `none` reported on that "
           "same subset beside it so the comparison is like for like.",
    "W2": "sees resolution group and, where the task definition defines it, capture session. "
          "Nothing else. On every task but PRAD the session field is null for every sample, "
          "so the cell is the resolution group alone.",
    "W3": "sees the unit structure of the calibration set and no features whatever: only "
          "which calibration unit each spot belongs to and how many spots that unit has.",
}


# ------------------------------------------------------------------- arguments
def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("encoder", nargs="?", default=None,
                   help="required unless --figures is given")
    p.add_argument("--task-def", action="append", dest="task_def", default=None)
    p.add_argument("--out-dir", default="results/round3/A3_weighted")
    p.add_argument("--tag", default="")
    p.add_argument("--designs", default="random,patient,donor")
    p.add_argument("--fit-designs", default="",
                   help="fit only these designs; --designs still governs enumeration and "
                        "therefore size matching, exactly as in the harness")
    p.add_argument("--scores", default="abs,scaled_clip")
    p.add_argument("--weightings", default=",".join(WEIGHTINGS))
    p.add_argument("--alpha", type=float, default=0.10, help="the primary level")
    p.add_argument("--alpha-store", type=float, default=0.20)
    p.add_argument("--n-cal-draws", type=int, default=3)
    p.add_argument("--spot-cal-draws", type=int, default=1)
    p.add_argument("--n-repeats", type=int, default=None)
    p.add_argument("--max-folds", type=int, default=None)
    p.add_argument("--size-match", default="task", choices=("task", "fold", "none"))
    p.add_argument("--morph-dir", default=H.MORPH_DIR)
    p.add_argument("--a1-dir", default=A1DIR,
                   help="A1's committed tables, for the fourth acceptance check")
    p.add_argument("--accept-tag", default="",
                   help="which A1 tag to anchor `none` against: __main or __slideout")
    p.add_argument("--random-tol", type=float, default=0.005)
    p.add_argument("--hcp-tol", type=float, default=1e-6)
    p.add_argument("--no-parquet", action="store_true")
    p.add_argument("--figures", action="store_true",
                   help="render the two A3 figures from the a3_by_fold tables already "
                        "written under --out-dir and exit; needs no encoder and no "
                        "task definition, and reads no parquet")
    a = p.parse_args(argv)
    if not a.figures:
        assert a.encoder, "an encoder is required unless --figures is given"
        assert a.task_def, "--task-def is required unless --figures is given"
    return a


def harness_args(args, designs):
    """An argparse namespace the harness's own enumeration accepts, carrying A1's values for
    everything that touches the split. Built through the harness's parse_args so that a new
    harness flag with a split-relevant default cannot be missed here."""
    argv = [args.encoder]
    for t in args.task_def:
        argv += ["--task-def", t]
    argv += ["--designs", ",".join(designs),
             "--alpha", str(args.alpha), "--alpha-store", str(args.alpha_store),
             "--n-cal-draws", str(args.n_cal_draws),
             "--spot-cal-draws", str(args.spot_cal_draws),
             "--size-match", args.size_match]
    if args.n_repeats is not None:
        argv += ["--n-repeats", str(args.n_repeats)]
    if args.max_folds:
        argv += ["--max-folds", str(args.max_folds)]
    return H.parse_args(argv)


# ------------------------------------------------------------- the weighted quantile
def weighted_quantile(S_C, w_C, w_test, alpha):
    """Per test point and gene, the weighted conformal quantile of the calibration scores.

    S_C is (n_C, n_gene), w_C is (n_C,) and strictly positive, w_test is (n_E,). Returns
    (q, infinite) with q of shape (n_E, n_gene) carrying +inf where the level is not
    attainable, and `infinite` the (n_E,) mask of test points for which that is so.

    The level is unattainable exactly when (1-alpha) * (sum_C w + w_test) exceeds sum_C w,
    which for W3 reduces to K + 1 < 1/alpha. Returning +inf is the honest answer; the largest
    calibration score is a different interval and is reported separately, never substituted.
    """
    n_C, n_gene = S_C.shape
    w_C = np.asarray(w_C, dtype=np.float64)
    w_test = np.atleast_1d(np.asarray(w_test, dtype=np.float64)).ravel()
    assert np.all(np.isfinite(w_C)) and np.all(w_C > 0), "non-positive or non-finite w_C"
    assert np.all(np.isfinite(w_test)) and np.all(w_test > 0), "bad test weight"
    total = float(w_C.sum())
    thr = (1.0 - alpha) * (total + w_test)                      # (n_E,)
    infinite = thr > total * (1.0 + QTOL)
    order = np.argsort(S_C, axis=0, kind="stable")
    Ssort = np.take_along_axis(S_C, order, axis=0)
    cumw = np.cumsum(w_C[order], axis=0)                        # (n_C, n_gene)
    q = np.empty((len(thr), n_gene), dtype=np.float64)
    thr_eff = thr * (1.0 - QTOL)
    for j in range(n_gene):
        idx = np.searchsorted(cumw[:, j], thr_eff, side="left")
        q[:, j] = Ssort[np.clip(idx, 0, n_C - 1), j]
    q[infinite, :] = np.inf
    return q, infinite


def n_eff(w_C):
    w = np.asarray(w_C, dtype=np.float64)
    s = w.sum()
    return float(s * s / np.square(w).sum())


# ------------------------------------------------------------------ weight estimators
def fit_ratio_classifier(Z_C, Z_E, seed_tag):
    """The W1 and W1b classifier. Returns (w_on_C, w_on_E, auc_in, auc_holdout, converged).

    w(z) = [p(1|z) / p(0|z)] * (n_C / n_E) with label 1 the test set, which is the density
    ratio p_test/p_cal up to the class-prior correction the n_C/n_E factor removes. The
    WEIGHTS are in-sample predictions, which is how the plan defines W1, so they stay that
    way.

    TWO AUCs are returned and both are written out, because they answer different questions
    and the in-sample one alone would be misleading on the small tasks. auc_in is measured on
    the same rows the classifier was fitted to and is an upper bound on separability: on a
    null shift with 8 features and 1,000 rows it reads about 0.58 rather than 0.50.
    auc_holdout refits on a stratified random half and scores the held-out half, so it is an
    honest estimate of whether calibration and test are distinguishable at all, and it is the
    one the `random` acceptance check uses and the one the AUC predictions are read against.
    The split is seeded from seed_tag with crc32, never hash().
    """
    Z = np.vstack([Z_C, Z_E])
    y = np.concatenate([np.zeros(len(Z_C), dtype=int), np.ones(len(Z_E), dtype=int)])
    # `penalty="l2"` is deprecated from scikit-learn 1.8 and removed in 1.10; the DEFAULT
    # penalty is L2, so omitting the argument keeps the plan's "L2 with a fixed C" and is
    # forward-compatible. The realised penalty is asserted below rather than assumed.
    clf = LogisticRegression(C=W1_C, class_weight="balanced",
                             max_iter=W1_MAX_ITER, solver="lbfgs")
    pen = clf.get_params().get("penalty", "l2")
    l1r = clf.get_params().get("l1_ratio", None)
    assert pen in ("l2", None, "deprecated") and (l1r in (None, 0.0)), (
        f"the classifier is not L2 as the plan specifies: penalty={pen!r} l1_ratio={l1r!r}")
    clf.fit(Z, y)
    n_iter = int(np.max(np.atleast_1d(clf.n_iter_)))
    lo = clf.decision_function(Z_C)
    le = clf.decision_function(Z_E)
    # exp of the logit is p1/p0 exactly, formed in log space so a confident classifier does
    # not overflow to inf before the clip can act on it
    ratio = float(len(Z_C)) / float(len(Z_E))
    with np.errstate(over="ignore"):
        w_C = np.exp(np.clip(lo, -700, 700)) * ratio
        w_E = np.exp(np.clip(le, -700, 700)) * ratio
    auc_in = float(roc_auc_score(y, clf.decision_function(Z)))

    rng = np.random.default_rng(zlib.crc32(f"{seed_tag}|holdout".encode()))
    tr = np.zeros(len(y), bool)
    for lab in (0, 1):
        idx = np.flatnonzero(y == lab)
        tr[rng.permutation(idx)[: max(1, len(idx) // 2)]] = True
    auc_ho = np.nan
    if tr.sum() >= 4 and (~tr).sum() >= 4 \
            and len(np.unique(y[tr])) == 2 and len(np.unique(y[~tr])) == 2:
        c2 = LogisticRegression(C=W1_C, class_weight="balanced",
                                max_iter=W1_MAX_ITER, solver="lbfgs").fit(Z[tr], y[tr])
        auc_ho = float(roc_auc_score(y[~tr], c2.decision_function(Z[~tr])))
    return w_C, w_E, auc_in, auc_ho, bool(n_iter < W1_MAX_ITER)


def clip_weights(w_C, w_E):
    """Clip both at the 99.5th percentile OF THE CALIBRATION WEIGHTS, per plan section 4.5,
    and floor at a tiny positive value so every weight stays strictly positive, which the
    weighted quantile requires and which the acceptance check verifies."""
    hi = float(np.percentile(w_C, W1_CLIP_PCT))
    if not (np.isfinite(hi) and hi > 0):
        fin = w_C[np.isfinite(w_C) & (w_C > 0)]
        hi = float(fin.max()) if fin.size else 1.0
    floor = 1e-12
    cr_C = float(np.mean(w_C > hi))
    cr_E = float(np.mean(w_E > hi))
    return (np.clip(w_C, floor, hi), np.clip(w_E, floor, hi), hi, cr_C, cr_E)


def w2_cells(samp_sub, meta):
    """(resolution_group, session) cell label per spot. Where the task definition leaves
    session null the pair degenerates to the resolution group alone, which is the rule the
    lead's note asks for, reached without a second code path: `__NA__` is one session level,
    and on a task where every sample has it the cell IS the resolution group."""
    return np.array([f"{meta['resgroup_of'].get(s)}|{meta['session_of'].get(s) or '__NA__'}"
                     for s in samp_sub], dtype=object)


def w2_weights(cell_C, cell_E):
    """Test-to-calibration proportion ratio per cell. Returns (w_C, w_E, no_support, detail).

    A test cell carrying no calibration mass has no finite weight. The fold is then flagged
    no_support and the caller falls back to unweighted for the WHOLE fold, which is what the
    plan specifies and what is counted in the output.
    """
    n_C, n_E = len(cell_C), len(cell_E)
    vc_C = pd.Series(cell_C).value_counts()
    vc_E = pd.Series(cell_E).value_counts()
    missing = [c for c in vc_E.index if c not in vc_C.index]
    if missing:
        return None, None, True, (f"test cells absent from calibration: "
                                  f"{';'.join(map(str, sorted(missing)))}")
    r = {c: (vc_E.get(c, 0) / n_E) / (vc_C[c] / n_C) for c in vc_C.index}
    w_C = np.array([r[c] for c in cell_C], dtype=np.float64)
    w_E = np.array([r.get(c, 0.0) for c in cell_E], dtype=np.float64)
    # A calibration cell absent from test gets ratio 0, which is a legitimate zero weight but
    # would break strict positivity; floor it and record nothing else, since the zero-mass
    # cell contributes no information either way.
    w_C = np.maximum(w_C, 1e-12)
    w_E = np.maximum(w_E, 1e-12)
    return w_C, w_E, False, (f"{len(vc_C)} calibration cells, {len(vc_E)} test cells")


def w3_weights(unit_lab_C, n_E):
    """HCP: w_i = 1/N_k inside the fold's calibration unit, test weight 1. Returns
    (w_C, w_E, K). Each unit then carries total mass 1 and the test point 1, so the
    normalised mass per unit and per test point is 1/(K+1)."""
    lab = np.asarray(unit_lab_C, dtype=object).astype(str)
    uniq, counts = np.unique(lab, return_counts=True)
    size = dict(zip(uniq.tolist(), counts.tolist()))
    w_C = np.array([1.0 / size[u] for u in lab], dtype=np.float64)
    return w_C, np.ones(n_E, dtype=np.float64), int(len(uniq))


# ------------------------------------------------------------------- morphology
def load_morph_covars(task, morph_dir):
    """The eight morphology_v2 covariates per spot, keyed (sample_id, barcode).

    Returns (dict key -> np.ndarray of 8 floats, n_rows) or (None, 0) when the file is
    absent. Column presence is asserted, not assumed: a missing covariate would otherwise
    become a silently narrower feature matrix for W1b.
    """
    p = f"{ROOT}/{morph_dir}/{task}_morph.parquet"
    if not os.path.exists(p):
        print(f"[morph] {p} absent; W1b cannot run on {task}", flush=True)
        return None, 0
    d = pq.read_table(p).to_pandas()
    miss = [c for c in MORPH_COVARS if c not in d.columns]
    assert not miss, f"{p}: missing morphology covariates {miss}; have {list(d.columns)}"
    for c in ("sample_id", "barcode"):
        assert c in d.columns, f"{p}: no {c} column"
    M = d[list(MORPH_COVARS)].to_numpy(dtype=np.float64)
    ok = np.isfinite(M).all(axis=1)
    keys = list(zip(d["sample_id"].astype(str), d["barcode"].astype(str)))
    out = {keys[i]: M[i] for i in np.flatnonzero(ok)}
    print(f"[morph] {task}: {len(d):,} rows, {len(out):,} with all eight covariates finite",
          flush=True)
    return out, len(d)


# ------------------------------------------------------------------- metrics
def cell_metrics(Y, lo, hi, alpha, samp_E, genes, min_spots):
    """Per (test slide, gene) coverage, mean and median width, Winkler interval score and the
    two one-sided misses, plus the fold-level spot-gene width mean and median over FINITE
    widths only. Infinite intervals cover by construction and are counted, never averaged
    into a width."""
    below, above = Y < lo, Y > hi
    cov = ~(below | above)
    width = hi - lo
    fin = np.isfinite(width)
    w = np.where(fin, width, 0.0)
    isc = w.copy()
    with np.errstate(invalid="ignore"):
        isc = np.where(below & fin, isc + (2.0 / alpha) * (lo - Y), isc)
        isc = np.where(above & fin, isc + (2.0 / alpha) * (Y - hi), isc)
    rows = []
    for s in np.unique(samp_E):
        m = samp_E == s
        nsl = int(m.sum())
        for j, g in enumerate(genes):
            fm = fin[m, j]
            rows.append(dict(
                slide=s, gene=g, n_test=nsl, n_covered=int(cov[m, j].sum()),
                coverage=float(cov[m, j].mean()),
                width_mean=float(width[m, j][fm].mean()) if fm.any() else np.nan,
                width_median=float(np.median(width[m, j][fm])) if fm.any() else np.nan,
                interval_score=float(isc[m, j][fm].mean()) if fm.any() else np.nan,
                miss_above=float(above[m, j].mean()), miss_below=float(below[m, j].mean()),
                n_infinite=int((~fm).sum()),
                slide_ge_min_spots=bool(nsl >= min_spots)))
    cells = pd.DataFrame(rows)
    allw = width[fin]
    return cells, (float(allw.mean()) if allw.size else np.nan), \
        (float(np.median(allw)) if allw.size else np.nan), int((~fin).sum()), int(fin.size)


def fold_summary(cells):
    """A1's aggregation chain: restrict to slides with at least MIN_SLIDE_SPOTS test spots,
    then the unweighted mean over the (slide, gene) cells. Identical to a1_by_fold's
    mean-over-genes-then-over-slides because the (slide, gene) grid has no missing cell."""
    use = cells[cells["slide_ge_min_spots"]]
    if not len(use):
        use = cells
    return dict(coverage=float(use["coverage"].mean()),
                width_mean=float(use["width_mean"].mean()),
                width_median_of_cells=float(use["width_median"].mean()),
                interval_score=float(use["interval_score"].mean()),
                miss_above=float(use["miss_above"].mean()),
                miss_below=float(use["miss_below"].mean()),
                n_cells=int(len(use)), n_slides=int(use["slide"].nunique()))


# =============================================================== the per-fold engine
def run_task(td, enc, args, designs, scores, weightings, state):
    t0 = time.time()
    task, label_set = td["task"], td["label_set"]
    meta = dict(
        donor_of={s["sample_id"]: s["donor_id"] for s in td["samples"]},
        patient_of={s["sample_id"]: s["hest_patient"] for s in td["samples"]},
        resgroup_of={s["sample_id"]: s["resolution_group"] for s in td["samples"]},
        session_of={s["sample_id"]: s.get("session") for s in td["samples"]},
    )
    n_sess = len({v for v in meta["session_of"].values() if v})
    n_res = len(set(meta["resgroup_of"].values()))
    state["w2_basis"].append(dict(
        encoder=enc, task=task, label_set=label_set, n_resolution_groups=n_res,
        n_sessions_defined=n_sess,
        n_samples_with_null_session=sum(1 for v in meta["session_of"].values() if not v),
        n_samples=len(meta["session_of"]),
        w2_cell_basis=("resolution_group x session" if n_sess else "resolution_group alone"),
        w2_can_vary=bool(n_res > 1 or n_sess > 1)))

    hargs = harness_args(args, designs)
    X, Y, samp, bc, xy, genes = H.load_task(td, enc)
    print(f"[load] {task}/{label_set} {enc}: {X.shape[0]:,} spots x {X.shape[1]} dims, "
          f"{len(genes)} genes, {time.time()-t0:.0f}s", flush=True)
    state["dims"][task] = X.shape[1]
    state["n_spots"][task] = X.shape[0]

    morph, morph_rows = (load_morph_covars(task, args.morph_dir)
                         if "W1b" in weightings else (None, 0))
    specs = H.build_fold_specs(td, samp, xy, designs, meta, hargs)
    H.size_match_groups(specs, args.size_match)
    fit_designs = {d for d in args.fit_designs.split(",") if d}
    print(f"[specs] {task}: {len(specs)} cells enumerated; "
          f"fitting {sorted(fit_designs) if fit_designs else 'all'}", flush=True)

    for i, sp in enumerate(specs):
        Tm = H.apply_size_match(sp, task)
        Cm, Em, info = sp["C"], sp["E"], sp["info"]
        if fit_designs and sp["design"] not in fit_designs:
            continue
        if int(Tm.sum()) < H.MIN_T_SPOTS or int(Cm.sum()) < H.MIN_C_SPOTS:
            print(f"  [skip] {task} {sp['design']} {sp['fold']}: |T|={int(Tm.sum())} "
                  f"|C|={int(Cm.sum())} ({info['cal_status']})", flush=True)
            continue

        pipe, A, reg, ridge_alpha = H.fit_base(X[Tm], Y[Tm])
        sig = H.fit_sigma(A, Y[Tm], reg, ridge_alpha) if "scaled_clip" in scores else None
        A_C = pipe.transform(X[Cm].astype(np.float64, copy=False))
        B = pipe.transform(X[Em].astype(np.float64, copy=False))
        P_C, P_E = reg.predict(A_C), reg.predict(B)
        Y_C = Y[Cm].astype(np.float64, copy=False)
        Y_E = Y[Em].astype(np.float64, copy=False)
        samp_C, samp_E = samp[Cm], samp[Em]
        bc_C, bc_E = bc[Cm], bc[Em]
        n_C, n_E = int(Cm.sum()), int(Em.sum())

        # ---------------- the weight sets, one per weighting, built once per fold ----
        W = {}
        diag = dict(encoder=enc, task=task, label_set=label_set, design=sp["design"],
                    fold=sp["fold"], repeat=sp["repeat"], cal_draw=sp["cal_draw"],
                    calibration_unit=str(info["calibration_unit"]),
                    n_T=int(Tm.sum()), n_C=n_C, n_E=n_E)

        W["none"] = dict(w_C=np.ones(n_C), w_E=np.ones(n_E), subset=None, auc=np.nan,
                         auc_holdout=np.nan,
                         clip_rate=0.0, clip_rate_test=0.0, no_support=0, K=np.nan,
                         converged=True)

        if "W1" in weightings:
            tag = f"{task}|{sp['design']}|{sp['fold']}|{sp['repeat']}|{sp['cal_draw']}|W1"
            wc, we, auc, auc_ho, conv = fit_ratio_classifier(A_C, B, tag)
            wc, we, hi, crc, cre = clip_weights(wc, we)
            W["W1"] = dict(w_C=wc, w_E=we, subset=None, auc=auc, auc_holdout=auc_ho,
                           clip_rate=crc, clip_rate_test=cre, no_support=0, K=np.nan,
                           converged=conv, clip_value=hi)

        if "W1b" in weightings and morph is not None:
            kc = [(s, b) for s, b in zip(samp_C.tolist(), bc_C.tolist())]
            ke = [(s, b) for s, b in zip(samp_E.tolist(), bc_E.tolist())]
            jc = np.array([k in morph for k in kc])
            je = np.array([k in morph for k in ke])
            frac = float((jc.sum() + je.sum()) / (len(jc) + len(je)))
            if jc.sum() >= H.MIN_C_SPOTS and je.sum() >= 1:
                # Index the Python lists, not np.array(list_of_tuples): numpy turns a list
                # of 2-tuples into a 2-D object array whose rows are ndarrays, and an
                # ndarray is not hashable, so the dict lookup raises.
                Mc = np.vstack([morph[kc[i]] for i in np.flatnonzero(jc)])
                Me = np.vstack([morph[ke[i]] for i in np.flatnonzero(je)])
                mu, sd = Mc.mean(0), Mc.std(0)
                sd = np.where(sd > 0, sd, 1.0)
                tagb = (f"{task}|{sp['design']}|{sp['fold']}|{sp['repeat']}"
                        f"|{sp['cal_draw']}|W1b")
                wc, we, auc, auc_ho, conv = fit_ratio_classifier(
                    (Mc - mu) / sd, (Me - mu) / sd, tagb)
                wc, we, hi, crc, cre = clip_weights(wc, we)
                W["W1b"] = dict(w_C=wc, w_E=we, subset=(jc, je), auc=auc,
                                auc_holdout=auc_ho, clip_rate=crc, clip_rate_test=cre,
                                no_support=0, K=np.nan, converged=conv, clip_value=hi,
                                frac_joined=frac)
                W["none_sub"] = dict(w_C=np.ones(int(jc.sum())), w_E=np.ones(int(je.sum())),
                                     subset=(jc, je), auc=np.nan, auc_holdout=np.nan, clip_rate=0.0,
                                     clip_rate_test=0.0, no_support=0, K=np.nan,
                                     converged=True, frac_joined=frac)
            else:
                print(f"  [W1b] {task} {sp['design']} {sp['fold']}: only {int(jc.sum())} "
                      f"calibration and {int(je.sum())} test spots join morphology; skipped",
                      flush=True)

        if "W2" in weightings:
            wc, we, ns, detail = w2_weights(w2_cells(samp_C, meta), w2_cells(samp_E, meta))
            if ns:
                W["W2"] = dict(w_C=np.ones(n_C), w_E=np.ones(n_E), subset=None, auc=np.nan,
                               auc_holdout=np.nan, clip_rate=0.0, clip_rate_test=0.0,
                               no_support=1, K=np.nan, converged=True, detail=detail)
            else:
                W["W2"] = dict(w_C=wc, w_E=we, subset=None, auc=np.nan, auc_holdout=np.nan,
                               clip_rate=0.0, clip_rate_test=0.0, no_support=0, K=np.nan,
                               converged=True, detail=detail)

        if "W3" in weightings:
            lvl = info["calibration_unit"]
            if lvl == "spot":
                lab = np.array([f"spot{i}" for i in range(n_C)], dtype=object)
            else:
                ul = H.unit_labels(lvl, Cm, sp.get("pool", Cm | sp["T"]), samp, xy, meta)
                lab = ul[Cm]
            wc, we, K = w3_weights(lab, n_E)
            W["W3"] = dict(w_C=wc, w_E=we, subset=None, auc=np.nan, auc_holdout=np.nan,
                           clip_rate=0.0, clip_rate_test=0.0, no_support=0, K=K,
                           converged=True)

        for nm, d in W.items():
            state["weights"].append({**diag, "weighting": nm,
                                     **{k: v for k, v in d.items()
                                        if k not in ("w_C", "w_E", "subset")},
                                     "n_eff": n_eff(d["w_C"]),
                                     "n_eff_frac": n_eff(d["w_C"]) / len(d["w_C"]),
                                     "w_C_min": float(np.min(d["w_C"])),
                                     "w_C_max": float(np.max(d["w_C"])),
                                     "all_positive_finite": bool(
                                         np.all(np.isfinite(d["w_C"]))
                                         and np.all(d["w_C"] > 0)
                                         and np.all(np.isfinite(d["w_E"]))
                                         and np.all(d["w_E"] > 0)),
                                     "difference_list": DIFFERENCE_LIST.get(
                                         nm if nm != "none_sub" else "none", "")})

        # -------------------------------------------- scores, then every weighting ----
        for score in scores:
            if score == "abs":
                S_C_full = np.abs(Y_C - P_C)
                unit_E_full = np.ones_like(P_E)
                sclip = dict(sigma_clip_lo=np.nan, sigma_clip_hi=np.nan,
                             sigma_lo_hit_guard=False, sigma_clip_rate_cal=np.nan,
                             sigma_clip_rate_test=np.nan)
            elif score == "scaled_clip":
                raw_C, raw_E = sig.predict(A_C), sig.predict(B)
                lo_p = float(np.percentile(raw_C, SIGMA_CLIP_LO_PCT))
                hi_p = float(np.percentile(raw_C, SIGMA_CLIP_HI_PCT))
                guard = lo_p < H.SIGMA_FLOOR
                lo_c = max(lo_p, H.SIGMA_FLOOR)
                hi_c = max(hi_p, lo_c * (1 + 1e-12))
                s_C = np.clip(raw_C, lo_c, hi_c)
                unit_E_full = np.clip(raw_E, lo_c, hi_c)
                S_C_full = np.abs(Y_C - P_C) / s_C
                sclip = dict(sigma_clip_lo=lo_c, sigma_clip_hi=hi_c,
                             sigma_lo_hit_guard=bool(guard),
                             sigma_clip_rate_cal=float(np.mean((raw_C < lo_c)
                                                               | (raw_C > hi_c))),
                             sigma_clip_rate_test=float(np.mean((raw_E < lo_c)
                                                                | (raw_E > hi_c))))
            else:
                raise ValueError(score)

            for nm, d in W.items():
                jc, je = (d["subset"] if d["subset"] is not None
                          else (np.ones(n_C, bool), np.ones(n_E, bool)))
                S_C = S_C_full[jc]
                uE = unit_E_full[je]
                PE, YE = P_E[je], Y_E[je]
                sE = samp_E[je]
                plans = [(args.alpha, "nominal")]
                if nm == "W3":
                    plans = [(args.alpha, "nominal"), (args.alpha_store, "nominal")]
                    if d["K"] >= 1:
                        plans.append((1.0 / (d["K"] + 1.0), "feasible_level"))
                elif nm in ("none", "none_sub"):
                    plans = [(args.alpha, "nominal"), (args.alpha_store, "nominal")]
                for al, variant in plans:
                    q, infm = weighted_quantile(S_C, d["w_C"], d["w_E"], al)
                    half = uE * q
                    ilo, ihi = PE - half, PE + half
                    cells, wm_sg, wmd_sg, n_inf, n_tot = cell_metrics(
                        YE, ilo, ihi, al, sE, genes, H.MIN_SLIDE_SPOTS)
                    fs = fold_summary(cells)
                    Kv = d["K"]
                    row = {**diag, "score": score,
                           "weighting": ("none" if nm == "none_sub" else nm),
                           "subset": ("morph_joined" if d["subset"] is not None else "all"),
                           "alpha": al, "w3_variant": (variant if nm == "W3" else ""),
                           "feasible_level": (1.0 - 1.0 / (Kv + 1.0)
                                              if nm == "W3" and Kv >= 1 else np.nan),
                           "guaranteed_level": (Kv / (Kv + 1.0)
                                                if nm == "W3" and Kv >= 1 else np.nan),
                           "K": Kv, "auc": d["auc"], "auc_holdout": d["auc_holdout"],
                           "clip_rate": d["clip_rate"],
                           "clip_rate_test": d["clip_rate_test"],
                           "no_support": d["no_support"],
                           "classifier_converged": d["converged"],
                           "n_eff_median": n_eff(d["w_C"]),
                           "n_eff_frac": n_eff(d["w_C"]) / len(d["w_C"]),
                           "n_C_used": int(jc.sum()), "n_E_used": int(je.sum()),
                           "frac_morph_joined": d.get("frac_joined", np.nan),
                           "n_infinite": n_inf, "n_spot_gene": n_tot,
                           "frac_infinite": (n_inf / n_tot if n_tot else np.nan),
                           "n_test_points_infinite": int(infm.sum()),
                           "width_mean_spotgene": wm_sg, "width_median": wmd_sg,
                           **sclip, **fs}
                    state["fold"].append(row)
                    for _, c in cells.iterrows():
                        state["slide"].append({
                            **{k: row[k] for k in (
                                "encoder", "task", "label_set", "design", "fold", "repeat",
                                "cal_draw", "score", "weighting", "subset", "alpha",
                                "w3_variant", "calibration_unit", "K", "n_eff_median",
                                "n_eff_frac", "auc", "auc_holdout", "no_support")},
                            "slide": c["slide"], "gene": c["gene"], "n_test": c["n_test"],
                            "n_covered": c["n_covered"], "coverage": c["coverage"],
                            "width_mean": c["width_mean"],
                            "width_median": c["width_median"],
                            "interval_score": c["interval_score"],
                            "miss_above": c["miss_above"], "miss_below": c["miss_below"],
                            "n_infinite": c["n_infinite"],
                            "slide_ge_min_spots": c["slide_ge_min_spots"]})
        print(f"  [{i+1}/{len(specs)}] {task} {sp['design']} {sp['fold']} "
              f"rep={sp['repeat']} draw={sp['cal_draw']} unit={info['calibration_unit']} "
              f"n_T={int(Tm.sum())} n_C={n_C} n_E={n_E} {time.time()-t0:.0f}s", flush=True)

    del X, Y
    return time.time() - t0


# ==================================================================== acceptance
def acceptance(state, args, enc):
    """The four checks, written and printed before anything else. Plan section 4.5 plus the
    memo's addition, plus a fourth anchoring `none` to A1's committed table."""
    fold = pd.DataFrame(state["fold"])
    rows, ok_all = [], True
    if not len(fold):
        return pd.DataFrame(), True

    prim_all = fold[(fold["alpha"] == args.alpha)
                    & (fold["w3_variant"] != "feasible_level")]
    prim = prim_all[prim_all["subset"] == "all"]

    # ---- A1: on `random`, weighted coverage within --random-tol of unweighted, W1 AUC ~0.5
    # Each weighting is compared to `none` ON ITS OWN SUBSET. W1b runs on the
    # morphology-joined spots only, so comparing it to `none` on all spots would charge it
    # with the subset difference as well as with the weights.
    rnd_all = prim_all[prim_all["design"] == "random"]
    rnd = prim[prim["design"] == "random"]
    if len(rnd_all):
        for wt in ("W1", "W1b", "W2", "W3"):
            d = rnd_all[rnd_all["weighting"] == wt]
            if not len(d):
                continue
            sub = d["subset"].iloc[0]
            base = (rnd_all[(rnd_all["weighting"] == "none")
                            & (rnd_all["subset"] == sub)]
                    .groupby(["task", "label_set", "score"])["coverage"].mean())
            g = d.groupby(["task", "label_set", "score"])["coverage"].mean()
            j = pd.concat([g.rename("weighted"), base.rename("unweighted")],
                          axis=1).dropna()
            if not len(j):
                rows.append(dict(check="A1_random_weighted_equals_unweighted",
                                 weighting=wt, n_cells=0,
                                 statistic="no comparable `none` rows on subset " + str(sub),
                                 value=np.nan, tol=args.random_tol, passed=None))
                continue
            worst = float((j["weighted"] - j["unweighted"]).abs().max())
            passed = worst <= args.random_tol
            ok_all &= passed
            rows.append(dict(check="A1_random_weighted_equals_unweighted", weighting=wt,
                             n_cells=len(j), statistic="max |coverage difference|",
                             value=worst, tol=args.random_tol, passed=passed,
                             note=f"compared to `none` on subset {sub}"))
        au = rnd[rnd["weighting"] == "W1"]["auc_holdout"].dropna()
        if len(au):
            worst = float((au - 0.5).abs().max())
            passed = worst <= 0.10
            ok_all &= passed
            rows.append(dict(check="A1_random_W1_auc_near_half", weighting="W1",
                             n_cells=len(au), statistic="max |AUC - 0.5|", value=worst,
                             tol=0.10, passed=passed,
                             note="held-out AUC, refit on a stratified half and scored on the "
                                  "other; the in-sample AUC is reported beside it"))

    # ---- A2: weights positive and finite after clipping, every fold and weighting
    wt = pd.DataFrame(state["weights"])
    if len(wt):
        bad = int((~wt["all_positive_finite"]).sum())
        passed = bad == 0
        ok_all &= passed
        rows.append(dict(check="A2_weights_positive_and_finite", weighting="all",
                         n_cells=len(wt), statistic="folds with a non-positive or "
                         "non-finite weight", value=bad, tol=0, passed=passed,
                         note=f"smallest calibration weight anywhere "
                              f"{wt['w_C_min'].min():.3e}"))

    # ---- A3: on `random`, W3 at the primary alpha has K = n_C and equals unweighted to tol
    if len(rnd):
        a = rnd[rnd["weighting"] == "W3"]
        b = rnd[rnd["weighting"] == "none"]
        key = ["task", "label_set", "design", "fold", "repeat", "cal_draw", "score"]
        j = a.merge(b, on=key, suffixes=("_w3", "_none"))
        if len(j):
            kbad = int((j["K_w3"] != j["n_C_w3"]).sum())
            dc = float((j["coverage_w3"] - j["coverage_none"]).abs().max())
            dw = float((j["width_mean_w3"] - j["width_mean_none"]).abs().max())
            passed = (kbad == 0) and (dc <= args.hcp_tol) and (dw <= args.hcp_tol)
            ok_all &= passed
            rows.append(dict(check="A3_random_W3_equals_unweighted", weighting="W3",
                             n_cells=len(j),
                             statistic="max |dcoverage|, max |dwidth|, K != n_C count",
                             value=max(dc, dw), tol=args.hcp_tol, passed=passed,
                             note=f"max |dcoverage| {dc:.3e}, max |dwidth| {dw:.3e}, "
                                  f"K != n_C on {kbad} of {len(j)} cells"))

    # ---- A4: `none` reproduces A1's committed per-fold coverage
    if args.accept_tag:
        src = f"{ROOT}/{args.a1_dir}/a1_by_fold__{enc}__{args.accept_tag}.csv"
        if os.path.exists(src):
            a1 = pd.read_csv(src)
            a1 = a1[a1["score"] == "abs"][["task", "label_set", "design", "fold",
                                           "coverage", "width_mean"]]
            mine = (prim[(prim["weighting"] == "none") & (prim["score"] == "abs")]
                    .groupby(["task", "label_set", "design", "fold"])
                    [["coverage", "width_mean"]].mean().reset_index())
            j = mine.merge(a1, on=["task", "label_set", "design", "fold"],
                           suffixes=("_a3", "_a1")).dropna()
            if len(j):
                dc = float((j["coverage_a3"] - j["coverage_a1"]).abs().max())
                dw = float((j["width_mean_a3"] - j["width_mean_a1"]).abs().max())
                passed = dc <= 1e-9
                ok_all &= passed
                rows.append(dict(
                    check="A4_none_reproduces_A1_by_fold", weighting="none", n_cells=len(j),
                    statistic="max |dcoverage| against a1_by_fold", value=dc, tol=1e-9,
                    passed=passed,
                    note=f"max |dwidth| {dw:.3e}; source {os.path.relpath(src, ROOT)}"))
        else:
            rows.append(dict(check="A4_none_reproduces_A1_by_fold", weighting="none",
                             n_cells=0, statistic="source absent", value=np.nan, tol=1e-9,
                             passed=None, note=f"{src} not found"))
    return pd.DataFrame(rows), ok_all


# ======================================================================== outputs
PG_SCHEMA = pa.schema([
    ("task", pa.string()), ("label_set", pa.string()), ("encoder", pa.string()),
    ("design", pa.string()), ("fold", pa.string()), ("repeat", pa.int32()),
    ("cal_draw", pa.int32()), ("score", pa.string()), ("weighting", pa.string()),
    ("subset", pa.string()), ("alpha", pa.float64()), ("w3_variant", pa.string()),
    ("calibration_unit", pa.string()), ("K", pa.float64()), ("slide", pa.string()),
    ("gene", pa.string()), ("n_test", pa.int32()), ("n_covered", pa.int32()),
    ("coverage", pa.float64()), ("width_mean", pa.float64()),
    ("width_median", pa.float64()), ("interval_score", pa.float64()),
    ("miss_above", pa.float64()), ("miss_below", pa.float64()),
    ("n_infinite", pa.int32()), ("n_eff_median", pa.float64()),
    ("n_eff_frac", pa.float64()), ("auc", pa.float64()), ("auc_holdout", pa.float64()),
    ("no_support", pa.int32()),
    ("slide_ge_min_spots", pa.bool_()),
])


def write_outputs(out, suf, state, args, enc, acc, ok_all):
    os.makedirs(out, exist_ok=True)
    written = []
    # ---- acceptance FIRST, per the plan's "reported first" ----
    if len(acc):
        acc.to_csv(f"{out}/a3_acceptance{suf}.csv", index=False)
        written.append(f"a3_acceptance{suf}.csv")
        print(f"\n=== A3 ACCEPTANCE, encoder {enc} ===")
        print(acc.to_string(index=False), flush=True)
        print(f"ACCEPTANCE: {'PASS' if ok_all else 'FAIL'}", flush=True)

    fold = pd.DataFrame(state["fold"])
    if len(fold):
        fold.to_csv(f"{out}/a3_by_fold{suf}.csv", index=False)
        written.append(f"a3_by_fold{suf}.csv")
        print(f"[write] a3_by_fold{suf}.csv ({len(fold)} rows)", flush=True)
        grp = ["task", "label_set", "encoder", "design", "score", "weighting", "subset",
               "alpha", "w3_variant"]
        by_task = (fold.groupby(grp, dropna=False)
                   .agg(n_folds=("fold", "nunique"),
                        coverage=("coverage", "mean"), coverage_sd=("coverage", "std"),
                        width_mean=("width_mean", "mean"),
                        width_median=("width_median", "mean"),
                        width_mean_spotgene=("width_mean_spotgene", "mean"),
                        interval_score=("interval_score", "mean"),
                        miss_above=("miss_above", "mean"),
                        miss_below=("miss_below", "mean"),
                        neff_median=("n_eff_median", "median"),
                        neff_frac=("n_eff_frac", "median"),
                        clip_rate=("clip_rate", "mean"),
                        clip_rate_test=("clip_rate_test", "mean"),
                        auc=("auc", "mean"), auc_holdout=("auc_holdout", "mean"),
                        no_support=("no_support", "sum"),
                        n_infinite=("n_infinite", "sum"),
                        n_spot_gene=("n_spot_gene", "sum"),
                        n_test_points_infinite=("n_test_points_infinite", "sum"),
                        K_median=("K", "median"),
                        feasible_level=("feasible_level", "mean"),
                        guaranteed_level=("guaranteed_level", "mean"),
                        frac_morph_joined=("frac_morph_joined", "mean"),
                        sigma_clip_rate_cal=("sigma_clip_rate_cal", "mean"),
                        classifier_converged=("classifier_converged", "all"))
                   .reset_index())
        by_task["frac_infinite"] = by_task["n_infinite"] / by_task["n_spot_gene"]
        by_task["difference_list"] = by_task["weighting"].map(DIFFERENCE_LIST)
        by_task.to_csv(f"{out}/a3_by_task{suf}.csv", index=False)
        written.append(f"a3_by_task{suf}.csv")
        print(f"[write] a3_by_task{suf}.csv ({len(by_task)} rows)", flush=True)
        show = by_task[(by_task["score"] == "abs") & (by_task["subset"] == "all")
                       & (by_task["w3_variant"] != "feasible_level")
                       & (by_task["alpha"] == args.alpha)]
        print(show[["task", "design", "weighting", "n_folds", "coverage", "width_mean",
                    "neff_frac", "auc", "no_support", "n_infinite"]]
              .round(4).to_string(index=False), flush=True)

    if state["weights"]:
        w = pd.DataFrame(state["weights"])
        w.to_csv(f"{out}/a3_weights{suf}.csv", index=False)
        written.append(f"a3_weights{suf}.csv")
        print(f"[write] a3_weights{suf}.csv ({len(w)} rows)", flush=True)
    if state["w2_basis"]:
        pd.DataFrame(state["w2_basis"]).to_csv(f"{out}/a3_w2_basis{suf}.csv", index=False)
        written.append(f"a3_w2_basis{suf}.csv")

    if state["slide"] and not args.no_parquet:
        sl = pd.DataFrame(state["slide"])
        cols = [f.name for f in PG_SCHEMA]
        for c in cols:
            if c not in sl.columns:
                sl[c] = np.nan
        d = sl[cols].copy()
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
                       f"{out}/a3_pergene{suf}.parquet", compression="snappy")
        written.append(f"a3_pergene{suf}.parquet")
        print(f"[write] a3_pergene{suf}.parquet ({len(d):,} rows, explicit schema)",
              flush=True)
        by_slide = (sl.groupby([c for c in ("encoder", "task", "label_set", "design", "fold",
                                            "score", "weighting", "subset", "alpha",
                                            "w3_variant", "slide")], dropna=False)
                    .agg(n_test=("n_test", "first"), n_genes=("gene", "nunique"),
                         coverage=("coverage", "mean"), width_mean=("width_mean", "mean"),
                         width_median=("width_median", "mean"),
                         interval_score=("interval_score", "mean"),
                         miss_above=("miss_above", "mean"),
                         miss_below=("miss_below", "mean"),
                         n_infinite=("n_infinite", "sum"),
                         n_eff_median=("n_eff_median", "first"),
                         n_eff_frac=("n_eff_frac", "first"), auc=("auc", "first"),
                         auc_holdout=("auc_holdout", "first"),
                         K=("K", "first"), no_support=("no_support", "first"))
                    .reset_index())
        by_slide.to_csv(f"{out}/a3_by_slide{suf}.csv", index=False)
        written.append(f"a3_by_slide{suf}.csv")
        print(f"[write] a3_by_slide{suf}.csv ({len(by_slide)} rows)", flush=True)
    return written


def provenance(out, suf, cfg, blob, chash, state, wall, written, ok_all):
    commit = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    with open(os.path.abspath(__file__), "rb") as f:
        ssha = hashlib.sha256(f.read()).hexdigest()[:16]
    with open(os.path.join(_HERE, "round3_a0_harness.py"), "rb") as f:
        hsha = hashlib.sha256(f.read()).hexdigest()[:16]
    p = f"{out}/PROVENANCE{suf}.txt"
    with open(p, "w") as f:
        f.write(f"{'='*78}\n"
                f"Round 3, stage A3 - weighted and hierarchical conformal, encoder "
                f"{cfg['encoder']}\n"
                f"tasks           : {', '.join(cfg['tasks'])}\n"
                f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID','NA')}\n"
                f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION','NA')}\n"
                f"node            : {os.environ.get('SLURMD_NODENAME','NA')}\n"
                f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
                f"repo_commit     : {commit}\n"
                f"script          : code/scripts/round3_a3_weighted.py\n"
                f"script_file     : {os.path.abspath(__file__)}\n"
                f"script_sha256   : sha256/16 {ssha}\n"
                f"harness_sha256  : sha256/16 {hsha}  (imported unmodified, not edited)\n"
                f"command_line    : {' '.join(sys.argv)}\n"
                f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED','unset')}\n"
                f"n_spots_by_task : {json.dumps(state['n_spots'], sort_keys=True)}\n"
                f"embedding_dim   : {json.dumps(state['dims'], sort_keys=True)}\n"
                f"n_fold_rows     : {len(state['fold'])}\n"
                f"wall_seconds    : {wall:.0f}\n"
                f"wall_by_task    : {json.dumps(state['wall'], sort_keys=True)}\n"
                f"acceptance      : {'PASS' if ok_all else 'FAIL'}\n"
                f"files_written   : {', '.join(written)}\n"
                f"config_hash     : sha256/16 {chash}\n"
                f"config          : {blob}\n"
                f"plan            : round3_execution_plan.md sections 4.5 and 12.4\n")
    print(f"[write] PROVENANCE{suf}.txt (config_hash {chash})", flush=True)


def _style():
    """The figure-style ladder applied through rcParams so the figure renders the same
    wherever it runs: three font sizes mapped to role, outward ticks, frameless legends,
    300 dpi."""
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


PAL = {"none": "#8C8C8C", "W1": "#4C72B0", "W1b": "#55A868", "W2": "#DD8452",
       "W3": "#C44E52"}


def stage_figures(args):
    """fig_a3_coverage_vs_neff.png and fig_a3_hcp_by_K.png, rendered from the a3_by_fold
    tables alone so the figures can be regenerated without the parquets."""
    import glob as _glob
    _style()
    import matplotlib.pyplot as plt
    out = f"{ROOT}/{args.out_dir}"
    fs = sorted(_glob.glob(f"{out}/a3_by_fold__*.csv"))
    assert fs, f"no a3_by_fold__*.csv under {out}"
    d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    print(f"[figures] {len(fs)} fold tables, {len(d):,} rows, "
          f"{d['encoder'].nunique()} encoders", flush=True)
    written = []
    key = ["encoder", "task", "label_set", "design", "fold", "repeat", "cal_draw", "score"]

    # ---- merge the per-encoder, per-tag tables into the deliverable names the plan asks
    # ---- for. The per-encoder files stay on disk as the sources.
    for stem in ("a3_by_task", "a3_by_slide", "a3_acceptance", "a3_weights", "a3_w2_basis"):
        src = sorted(_glob.glob(f"{out}/{stem}__*.csv"))
        if not src:
            continue
        m = pd.concat([pd.read_csv(f).assign(
            _source=os.path.basename(f)) for f in src], ignore_index=True)
        m.to_csv(f"{out}/{stem}.csv", index=False)
        written.append(f"{stem}.csv")
        print(f"[write] {stem}.csv ({len(m)} rows from {len(src)} files)", flush=True)
    d.to_csv(f"{out}/a3_by_fold.csv", index=False)
    written.append("a3_by_fold.csv")
    print(f"[write] a3_by_fold.csv ({len(d)} rows)", flush=True)

    # ------------------------------------------- fig_a3_coverage_vs_neff.png
    prim = d[(d["score"] == "abs") & (d["alpha"] == args.alpha)
             & (d["w3_variant"] != "feasible_level")]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8))
    ax = axes[0]
    for wt in ("W1", "W1b", "W2"):
        w = prim[prim["weighting"] == wt]
        if not len(w):
            continue
        base = prim[(prim["weighting"] == "none")
                    & (prim["subset"] == w["subset"].iloc[0])]
        j = w.merge(base[key + ["coverage"]], on=key, suffixes=("", "_none"))
        j = j[np.isfinite(j["n_eff_frac"])]
        ax.scatter(j["n_eff_frac"], j["coverage"] - j["coverage_none"], s=6, alpha=0.5,
                   color=PAL[wt], edgecolors="none",
                   label=f"{wt}  (n={len(j)} folds)")
    ax.axhline(0, color="0.55", lw=0.6, zorder=0)
    ax.set_xscale("log")
    ax.set_xlabel(r"$n_{\mathrm{eff}}$ as a fraction of the calibration size")
    ax.set_ylabel("coverage, weighted minus unweighted")
    ax.set_title("Does reweighting move coverage,\nand does the move track $n_{eff}$?")
    ax.margins(0.05)
    ax.legend(loc="best", markerscale=2.2)
    ax = axes[1]
    nb = prim[(prim["weighting"] == "none") & (prim["subset"] == "all")]
    ax.scatter(nb["n_eff_frac"] * 0 + 1.0, nb["coverage"], s=6, alpha=0.35,
               color=PAL["none"], edgecolors="none", label="unweighted")
    for wt in ("W1", "W1b", "W2"):
        w = prim[prim["weighting"] == wt]
        w = w[np.isfinite(w["n_eff_frac"])]
        if len(w):
            ax.scatter(w["n_eff_frac"], w["coverage"], s=6, alpha=0.5, color=PAL[wt],
                       edgecolors="none", label=wt)
    ax.axhline(1 - args.alpha, color="0.55", lw=0.7, ls="--")
    ax.annotate(f"nominal {1-args.alpha:.2f}", xy=(0.99, 1 - args.alpha),
                xycoords=("axes fraction", "data"), ha="right", va="bottom",
                fontsize=7, color="0.35")
    ax.set_xscale("log")
    ax.set_xlabel(r"$n_{\mathrm{eff}}$ as a fraction of the calibration size")
    ax.set_ylabel("coverage")
    ax.set_title("Coverage against calibration support")
    ax.margins(0.05)
    ax.legend(loc="lower right", markerscale=2.2)
    fig.tight_layout()
    fig.savefig(f"{out}/fig_a3_coverage_vs_neff.png")
    plt.close(fig)
    written.append("fig_a3_coverage_vs_neff.png")
    print("[write] fig_a3_coverage_vs_neff.png", flush=True)

    # ------------------------------------------------- fig_a3_hcp_by_K.png
    # `random` is EXCLUDED from this figure. There the calibration unit is the spot, so K is
    # the spot count by construction and its alpha for the feasible level is ~1e-4; keeping
    # it would stretch the K axis to 1e5 and mix a control into a plot about unit structure.
    # That random is the control, with K = n_C and W3 equal to unweighted, is the A3
    # acceptance table's business and is stated there.
    # The two alphas are the CONFIGURED ones, not the smallest in the frame: the
    # feasible-level rows carry alpha = 1/(K+1), which would otherwise be picked first.
    h = d[(d["score"] == "abs") & (d["subset"] == "all")
          & (d["design"] != "random") & (d["weighting"].isin(["W3", "none"]))]
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.8))
    # K belongs to W3's unit structure, so the `none` rows carry K = NaN and cannot be
    # plotted against it until each fold's K is joined on from its own W3 row. Without this
    # the unweighted series is silently absent and its legend entry resolves to nothing.
    fkey = ["encoder", "task", "label_set", "design", "fold", "repeat", "cal_draw"]
    kmap = (h[h["weighting"] == "W3"].groupby(fkey, dropna=False)["K"]
            .first().rename("K_fold").reset_index())
    for ai, al in enumerate([args.alpha, args.alpha_store]):
        ax = axes[ai]
        hn = h[(h["weighting"] == "none") & (h["alpha"] == al)].merge(
            kmap, on=fkey, how="left")
        hn = hn.assign(K=hn["K_fold"])
        hw = h[(h["weighting"] == "W3") & (h["alpha"] == al)
               & (h["w3_variant"] == "nominal")]
        ax.scatter(hn["K"], hn["coverage"], s=8, color=PAL["none"], alpha=0.45,
                   edgecolors="none", label="unweighted")
        inf = hw["frac_infinite"] > 0
        ax.scatter(hw.loc[~inf, "K"], hw.loc[~inf, "coverage"], s=10, color=PAL["W3"],
                   alpha=0.7, edgecolors="none", label="W3, finite interval")
        ax.scatter(hw.loc[inf, "K"], hw.loc[inf, "coverage"], s=22, facecolors="none",
                   edgecolors=PAL["W3"], linewidths=0.8,
                   label="W3, interval infinite")
        ax.axhline(1 - al, color="0.55", lw=0.7, ls="--")
        # The y limits must span BOTH series. Left to autoscale they follow W3, which sits
        # at 1.0 wherever the interval is infinite, and the unweighted points at 0.6 to 0.9
        # fall off the bottom, leaving a legend entry that resolves to nothing on the panel.
        both = np.concatenate([hn["coverage"].to_numpy(dtype=float),
                               hw.loc[~inf, "coverage"].to_numpy(dtype=float)])
        both = both[np.isfinite(both)]
        ylo = float(both.min()) - 0.04 if both.size else 0.0
        ax.set_ylim(ylo, 1.03)
        ax.annotate(f"nominal {1-al:.2f}", xy=(0.02, 1 - al),
                    xycoords=("axes fraction", "data"), ha="left", va="bottom",
                    fontsize=7, color="0.35")
        ax.axvline(1.0 / al - 1.0, color="#C44E52", lw=0.6, ls=":")
        ax.annotate(r"$K+1=1/\alpha$", xy=(1.0 / al - 1.0, 0.02),
                    xycoords=("data", "axes fraction"), rotation=90, fontsize=6,
                    color="#C44E52", ha="right", va="bottom")
        ax.set_xscale("log")
        ax.set_xlabel("number of calibration units $K$")
        if ai == 0:
            ax.set_ylabel("coverage")
        ax.set_title(rf"HCP at $\alpha={al:.2f}$")
        if ai == 0:
            ax.legend(loc="center right", markerscale=1.8)
    ax = axes[2]
    fb = d[(d["score"] == "abs") & (d["weighting"] == "W3")
           & (d["w3_variant"] == "feasible_level") & (d["subset"] == "all")
           & (d["design"] != "random")]
    if len(fb):
        ax.scatter(fb["guaranteed_level"], fb["coverage"], s=10, color=PAL["W3"],
                   alpha=0.6, edgecolors="none", label="realised")
        lim = [float(np.nanmin(fb["guaranteed_level"])) * 0.98, 1.005]
        ax.plot(lim, lim, color="0.55", lw=0.7, ls="--")
        ax.annotate("realised = guaranteed", xy=(lim[0], lim[0]), fontsize=6,
                    color="0.35", ha="left", va="bottom", rotation=45)
        ax.set_xlabel(r"guaranteed level $K/(K+1)$")
        ax.set_ylabel("realised coverage")
        ax.set_title(f"Feasible-level fallback\n{len(fb)} folds")
        ax.margins(0.05)
    fig.tight_layout()
    fig.savefig(f"{out}/fig_a3_hcp_by_K.png")
    plt.close(fig)
    written.append("fig_a3_hcp_by_K.png")
    print("[write] fig_a3_hcp_by_K.png", flush=True)
    return written


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    if args.figures:
        stage_figures(args)
        return 0
    t0 = time.time()
    enc = args.encoder
    designs = [d for d in args.designs.split(",") if d]
    scores = [s for s in args.scores.split(",") if s]
    weightings = [w for w in args.weightings.split(",") if w]
    for d in designs:
        assert d in H.DESIGNS, f"unknown design {d}"

    tds = []
    for p in args.task_def:
        td = json.load(open(p))
        assert td["task_def_version"] == 1, f"{p}: task_def_version {td['task_def_version']}"
        td["_path"] = p
        tds.append(td)

    out = f"{ROOT}/{args.out_dir}"
    suf = f"__{enc}{args.tag}"
    cfg = dict(stage="round3_A3", script="code/scripts/round3_a3_weighted.py", encoder=enc,
               tasks=[f"{t['task']}/{t['label_set']}" for t in tds],
               task_defs=[os.path.relpath(os.path.abspath(t["_path"]), ROOT) for t in tds],
               designs=designs, fit_designs=args.fit_designs, scores=scores,
               weightings=weightings, alpha=args.alpha, alpha_store=args.alpha_store,
               w1_C=W1_C, w1_max_iter=W1_MAX_ITER, w1_clip_pct=W1_CLIP_PCT,
               w1_auc_in_sample_and_holdout=True,
               sigma_clip_lo_pct=SIGMA_CLIP_LO_PCT, sigma_clip_hi_pct=SIGMA_CLIP_HI_PCT,
               sigma_lo_guard=H.SIGMA_FLOOR, morph_covars=list(MORPH_COVARS),
               morph_dir=args.morph_dir, quantile_rel_tol=QTOL,
               n_cal_draws=args.n_cal_draws, spot_cal_draws=args.spot_cal_draws,
               n_repeats=args.n_repeats, max_folds=args.max_folds,
               size_match=args.size_match, min_slide_spots=H.MIN_SLIDE_SPOTS,
               min_T_spots=H.MIN_T_SPOTS, min_C_spots=H.MIN_C_SPOTS,
               base_predictor="imported unmodified from round3_a0_harness.fit_base",
               seed_source="zlib.crc32 via the harness")
    blob = json.dumps(cfg, sort_keys=True)
    chash = hashlib.sha256(blob.encode()).hexdigest()[:16]
    print(f"[config] sha256/16 {chash}\n{blob}", flush=True)

    state = dict(fold=[], slide=[], weights=[], w2_basis=[], dims={}, n_spots={}, wall={})
    for td in tds:
        state["wall"][f"{td['task']}/{td['label_set']}"] = round(
            run_task(td, enc, args, designs, scores, weightings, state), 1)

    acc, ok_all = acceptance(state, args, enc)
    written = write_outputs(out, suf, state, args, enc, acc, ok_all)
    provenance(out, suf, cfg, blob, chash, state, time.time() - t0, written, ok_all)
    print(f"\n[done] {time.time()-t0:.0f}s  acceptance="
          f"{'PASS' if ok_all else 'FAIL'}", flush=True)
    return 0 if ok_all else 5


if __name__ == "__main__":
    sys.exit(main())
