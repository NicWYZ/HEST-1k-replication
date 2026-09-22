#!/usr/bin/env python
"""Round 3, stage A0: the conformal harness. Every Topic A number comes out of this file.

Stage: A0, the conformal harness and its acceptance checks (round3_execution_plan.md section 4.2).

Extends `code/scripts/round2_split_v4.py` (size matching, buffered spatial blocks at 2.5
pitches, per-gene storage with an explicit schema, crc32 seeding) and takes its base predictor
verbatim from `code/scripts/round2_r1b_heads.py` (the `intercept_f64` head: StandardScaler ->
PCA(256, random_state=1) -> float64 Cholesky ridge WITH intercept at alpha = 100/(256*50), the
whole chain built in float64 from the raw embeddings because casting after a float32 scaler
leaves the PCA column means at ~5e-08 and breaks the head identity; see that file's
`features` docstring).

For each task, design and fold it produces three disjoint spot sets, proper-training T,
calibration C and test E; fits the base predictor on T only; and evaluates split-conformal
intervals on E at alpha = 0.10, storing the alpha = 0.20 quantile beside them.

Nothing is fit on C or E except the conformal quantile on C.

Designs, section 4.2 design table:

  random     E is a random draw of the shipped fold's test size over ALL spots of the task,
             5 repeats; pool is the rest; calibration unit is the SPOT and C is a random 20%
             of the pool.
  patient    E is the shipped fold's test slides, pool is the shipped fold's training slides,
             calibration at the highest level the pool supports using HEST `patient`.
  donor      leave-one-donor-out by `donor_id`, calibration at the highest level the pool
             supports using `donor_id`.
  slide_out  E is one slide, pool is every other slide INCLUDING the donor's other slides,
             calibration unit is the slide.

Calibration-unit rule, section 4.2: within the pool hold out about 25% of the units at the
highest level the pool supports, rounding up to at least one unit; donor if the pool has at
least two donors (patients, under `patient`), else slide if it has at least two slides, else
buffered spatial blocks inside the single slide (grid 6, 2.5-pitch buffer, about 20% of
blocks). Which folds could calibrate at donor level is itself a result, so it is recorded per
fold rather than assumed.

Scores, per gene:
  abs     s = |y - yhat|;                 interval yhat +- qhat
  scaled  s = |y - yhat| / sigmahat(x);   interval yhat +- qhat * sigmahat(x)
          sigmahat is a ridge of |y - yhat| on the same PCA-256 features, fit on T's
          IN-SAMPLE residuals, floored at 1e-3.
with qhat the ceil((n+1)(1-alpha))/n empirical quantile of the calibration scores.

Outputs, summaries before bulk tables (round 2 R3 lost 35 CPU-hours of per-gene table to a
final parquet write and kept its summaries only by luck):
  a1_calibration_units__<enc>.csv   one row per (design, fold, repeat, cal draw)
  a1_by_slide__<enc>.csv            per test slide
  a1_by_task__<enc>.csv             per (task, design, encoder, score)
  a1_cal_dispersion__<enc>.csv      spread across the three crc32 calibration draws
  h3_disjointness__<enc>.csv        T/C/E disjointness and "scaler and PCA saw only T"
  pergene__<enc>.parquet            explicit pa.schema, `fold` a STRING
  PROVENANCE.txt                    job id, partition actually used, node, commit, command
                                    line, config hash WITH the config it hashes, PYTHONHASHSEED

Acceptance modes (section 4.2 H1-H4):
  --h1-anchor   patient design, calibration fraction ZERO, no size matching, no conformal.
                Per-task Pearson must equal R1b's `intercept_f64` per-task Pearson to within
                1e-6 for every encoder-task cell, read from
                results/round2/R1b_heads/head_intercept__<enc>__f64.csv.
  --h2-check    random design, `abs` score: marginal coverage pooled over folds must be
                within 0.02 of 0.90 for every task-encoder cell.
An H1 or H2 failure is the one in-interval stop condition. This script exits non-zero and says
so; it does not adjust a threshold.

Usage:
  round3_a0_harness.py <encoder> --task-def <file> [options]
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

import anndata as ad
import h5py
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import scanpy as sc
from scipy.spatial import cKDTree
from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline

ROOT = "/work/users/w/e/weiyang/hest_replication"

# Base-predictor constants. These are round 2 R1b's, not new choices.
SEED, LATENT = 1, 256
ALPHA_NUM = 100.0                 # alpha = ALPHA_NUM / (n_components * n_genes)
SIGMA_FLOOR = 1e-3                # section 4.2 `scaled` score

# Calibration-unit rule constants, section 4.2.
CAL_UNIT_FRAC = 0.25              # 25% of units at the highest level the pool supports
CAL_SPOT_FRAC = 0.20              # random design: C is a random 20% of the pool
CAL_BLOCK_FRAC = 0.20             # block fallback: about 20% of blocks
BLOCK_GRID = 6
BUFFER_PITCHES = 2.5

MIN_SLIDE_SPOTS = 50              # project metric convention, carried from round 2 R3
MIN_T_SPOTS = 2 * LATENT          # a T smaller than this cannot support PCA-256 honestly
MIN_C_SPOTS = 9                   # ceil((n+1)*0.9) <= n first holds at n = 9

DESIGNS = ("random", "patient", "donor", "slide_out")


# ----------------------------------------------------------------------- arguments
def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("encoder")
    p.add_argument("--task-def", required=True, action="append", dest="task_def",
                   help="path to a task-definition JSON conforming to "
                        "task_def.schema.json. May be repeated: one invocation then covers "
                        "several tasks and writes ONE set of files per encoder, which is "
                        "what A1's `pergene__<enc>.parquet` wants and what keeps the "
                        "one-writer-per-file rule when 12 encoder jobs run concurrently.")
    p.add_argument("--out-dir", default="results/round3/A1_coverage",
                   help="relative to the project root")
    p.add_argument("--tag", default="", help="suffix on every output filename")
    p.add_argument("--designs", default=",".join(DESIGNS))
    p.add_argument("--scores", default="abs,scaled")
    p.add_argument("--alpha", type=float, default=0.10)
    p.add_argument("--alpha-store", type=float, default=0.20,
                   help="second quantile stored beside the reported one")
    p.add_argument("--n-cal-draws", type=int, default=3,
                   help="calibration draws where the pool has at least three UNITS")
    p.add_argument("--spot-cal-draws", type=int, default=1,
                   help="calibration draws for the spot-level unit (the `random` design). "
                        "1 by default: the design already carries 5 independent repeats, "
                        "each of which redraws C as well as E, so the dispersion the rule "
                        "asks for is already measured and three more draws would triple "
                        "the cost of the largest design for no new information. Declared "
                        "in the config hash and in the stage report.")
    p.add_argument("--n-repeats", type=int, default=None,
                   help="override the task definition's random n_repeats")
    p.add_argument("--max-folds", type=int, default=None,
                   help="use only the first N folds of each design (smoke runs)")
    p.add_argument("--size-match", default="task", choices=("task", "fold", "none"),
                   help="see size_match_groups()")
    p.add_argument("--h1-anchor", action="store_true")
    p.add_argument("--h2-check", action="store_true")
    p.add_argument("--r1b-dir", default="results/round2/R1b_heads")
    p.add_argument("--h1-tol", type=float, default=1e-6)
    p.add_argument("--h2-tol", type=float, default=0.02)
    p.add_argument("--no-parquet", action="store_true")
    return p.parse_args(argv)


# ---------------------------------------------------------------------- data loading
def load_task(td, enc):
    """Round 2 R1b's `load_task`, with the coordinates R3 needs and the paths taken from the
    task definition instead of a hard-coded benchmark layout.

    The sample ORDER is `sorted(sample_id)`, which is the order
    `sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad"))` produces because the directory prefix is
    constant. That equality is load-bearing: H1 compares against stored R1b numbers, and a
    different row order changes the PCA (randomized SVD) and hence the fit.
    """
    genes = list(td["target_genes"]["list"])
    gpath = f"{ROOT}/{td['paths']['target_genes']}"
    if os.path.exists(gpath):
        on_disk = list(json.load(open(gpath))["genes"])
        assert on_disk == genes, (f"task definition gene list disagrees with {gpath}; "
                                  f"first difference at index "
                                  f"{next(i for i, (a, b) in enumerate(zip(on_disk, genes)) if a != b)}")
    ids = sorted(s["sample_id"] for s in td["samples"])
    Xs, Ys, samp, bcs, xy = [], [], [], [], []
    for sid in ids:
        ep = f"{ROOT}/{td['paths']['embeddings'].format(encoder=enc, sample_id=sid)}"
        ap = f"{ROOT}/{td['paths']['adata'].format(sample_id=sid)}"
        with h5py.File(ep, "r") as f:
            k = "barcodes" if "barcodes" in f else "barcode"
            b = np.asarray(f[k][:]).reshape(-1)
            bc = [x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in b]
            Xs.append(np.asarray(f["embeddings"][:], dtype=np.float32))
            xy.append(np.asarray(f["coords"][:], dtype=np.float64))
        A = ad.read_h5ad(ap)
        sc.pp.log1p(A)
        sub = A[bc, genes]
        Y = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
        Ys.append(np.asarray(Y, dtype=np.float32))
        samp += [sid] * len(bc)
        bcs += bc
    return (np.vstack(Xs), np.vstack(Ys), np.array(samp),
            np.array(bcs, dtype=object), np.vstack(xy), genes)


# ------------------------------------------------------------------- base predictor
def fit_base(Xtr, Ytr):
    """R1b's `intercept_f64` head. Returns (pipeline, A_train, ridge, sigma_ridge, alpha).

    float64 from the RAW embeddings through the scaler and the PCA, not a cast of float32
    features: R1b measured that the cast leaves the PCA column means at ~5e-08 and the
    three-head identity at ~7e-07 instead of ~2e-15.
    """
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=min(LATENT, Xtr.shape[1]),
                                 random_state=SEED))])
    A = pipe.fit_transform(Xtr.astype(np.float64, copy=False))
    Yd = Ytr.astype(np.float64, copy=False)
    alpha = ALPHA_NUM / (A.shape[1] * Yd.shape[1])
    reg = Ridge(alpha=alpha, random_state=0, fit_intercept=True,
                solver="cholesky").fit(A, Yd)
    return pipe, A, reg, alpha


def fit_sigma(A, Ytr, reg, alpha):
    """sigmahat for the `scaled` score: ridge of |y - yhat| on the PCA features, fit on T's
    in-sample residuals, at the same alpha as the mean head."""
    resid = np.abs(Ytr.astype(np.float64, copy=False) - reg.predict(A))
    return Ridge(alpha=alpha, random_state=0, fit_intercept=True,
                 solver="cholesky").fit(A, resid)


def scaler_pca_saw_only_T(pipe, Xtr):
    """H3's second half, checked rather than asserted by construction.

    Recomputes the scaler's and the PCA's fitted statistics from X[T] and compares. A scaler
    that had seen one calibration spot would not reproduce.
    """
    Xd = Xtr.astype(np.float64, copy=False)
    sc_ = pipe.named_steps["scaler"]
    pca = pipe.named_steps["PCA"]
    d_mean = float(np.max(np.abs(sc_.mean_ - Xd.mean(axis=0))))
    d_var = float(np.max(np.abs(sc_.var_ - Xd.var(axis=0))))
    Z = sc_.transform(Xd)
    d_pca_mean = float(np.max(np.abs(pca.mean_ - Z.mean(axis=0))))
    return dict(n_samples_seen=int(sc_.n_samples_seen_),
                pca_n_samples=int(getattr(pca, "n_samples_", -1)),
                max_abs_scaler_mean_minus_T=d_mean,
                max_abs_scaler_var_minus_T=d_var,
                max_abs_pca_mean_minus_T=d_pca_mean)


# ---------------------------------------------------------------- spatial helpers
def pitch_for(sid, samp, xy):
    """Spot pitch in pixels: median nearest-neighbour distance on the slide, which is the
    pitch by construction for a regular lattice. round2_split_v4.pitch_for, minus the
    fig3e_gate lookup, which covers 4 of 72 samples."""
    c = xy[samp == sid]
    if len(c) < 3:
        return np.nan
    d, _ = cKDTree(c).query(c, k=2)
    return float(np.median(d[:, 1]))


def block_pick(pool_idx, samp, xy, frac, rng, grid=BLOCK_GRID):
    """Choose whole grid cells of a slide until `frac` of the pool's spots are covered.
    round2_split_v4.block_test restricted to the pool."""
    chosen = np.zeros(len(samp), bool)
    n_blocks_total, n_blocks_chosen = 0, 0
    for s in np.unique(samp[pool_idx]):
        m = np.zeros(len(samp), bool)
        m[pool_idx] = True
        m &= (samp == s)
        c = xy[m]
        lo, hi = c.min(0), c.max(0)
        span = np.where(hi - lo == 0, 1.0, hi - lo)
        key = (np.clip(((c - lo) / span * grid).astype(int), 0, grid - 1)
               * [grid, 1]).sum(1)
        blocks, counts = np.unique(key, return_counts=True)
        n_blocks_total += len(blocks)
        tgt, acc, pick = frac * m.sum(), 0, []
        for j in rng.permutation(len(blocks)):
            if acc >= tgt:
                break
            pick.append(blocks[j])
            acc += counts[j]
        n_blocks_chosen += len(pick)
        idx = np.flatnonzero(m)
        chosen[idx[np.isin(key, pick)]] = True
    return chosen, n_blocks_chosen, n_blocks_total


def buffer_drop(samp, xy, cal_mask, cand_mask):
    """Spots in `cand_mask` to DROP: within BUFFER_PITCHES pitches of any calibration spot on
    the same slide. round2_split_v4.buffer_mask, with the roles renamed."""
    drop = np.zeros(len(samp), bool)
    for s in np.unique(samp[cal_mask]):
        m = samp == s
        t = m & cal_mask
        cand = np.flatnonzero(m & cand_mask)
        if not t.any() or not len(cand):
            continue
        r = BUFFER_PITCHES * pitch_for(s, samp, xy)
        if not np.isfinite(r):
            continue
        near = cKDTree(xy[t]).query_ball_point(xy[cand], r=r)
        drop[cand[[i for i, nb in enumerate(near) if len(nb)]]] = True
    return drop


# ------------------------------------------------------- calibration-unit rule
def unit_hierarchy(design):
    """The levels the calibration-unit rule may use, highest first, per the section 4.2
    design table. `patient` uses HEST `patient`; `donor` uses `donor_id`; `slide_out`'s
    calibration unit is the slide; `random`'s is the spot."""
    if design == "random":
        return ["spot"]
    if design == "patient":
        return ["patient", "slide", "block"]
    if design == "donor":
        return ["donor", "slide", "block"]
    if design == "slide_out":
        return ["slide", "block"]
    raise ValueError(design)


def sharing_flags(C, E, samp, meta):
    """The section 4.2 record of what the calibration set shares with the test set.

    `cal_shares_session_with_test` is the plan's column and its definition is the plan's
    parenthetical: "any calibration slide in the test slide's resolution_group, and for PRAD
    patient 2 the same session". The two halves are also stored separately, because a slide
    sharing a resolution group is a weaker statement than a slide from the same capture
    session and A2 stratifies on both.
    """
    cal_slides = set(np.unique(samp[C]).tolist()) if C.any() else set()
    test_slides = set(np.unique(samp[E]).tolist())
    cal_don = {meta["donor_of"].get(s) for s in cal_slides}
    te_don = {meta["donor_of"].get(s) for s in test_slides}
    cal_grp = {meta["resgroup_of"].get(s) for s in cal_slides}
    te_grp = {meta["resgroup_of"].get(s) for s in test_slides}
    cal_ses = {meta["session_of"].get(s) for s in cal_slides} - {None}
    te_ses = {meta["session_of"].get(s) for s in test_slides} - {None}
    return dict(
        n_cal_slides=len(cal_slides),
        cal_shares_donor_with_test=bool(cal_don & te_don),
        cal_shares_resolution_group_with_test=bool(cal_grp & te_grp),
        cal_shares_exact_session_with_test=(bool(cal_ses & te_ses) if te_ses else None),
        cal_shares_session_with_test=bool((cal_grp & te_grp) or (cal_ses & te_ses)))


def choose_calibration(design, pool, E, samp, xy, meta, seed_key, draw, cal_frac_units,
                       cal_frac_spots):
    """Split the pool into T and C. Returns (T_mask, C_mask, info dict).

    `pool` and `E` are boolean masks over the task's spots. The returned info carries the
    section 4.2 record: calibration_unit, n_cal_units, n_cal_spots and the three sharing
    flags, plus a cal_status that is not "ok" when no calibration set could be produced.
    """
    n = len(samp)
    pool_idx = np.flatnonzero(pool)
    rng = np.random.default_rng(zlib.crc32(f"{seed_key}|cal{draw}".encode()))
    info = dict(calibration_unit=None, n_cal_units=0, n_units_in_pool=0,
                n_cal_spots=0, n_pool_spots=int(pool.sum()), cal_status="ok",
                n_blocks_total=None, n_train_buffer_dropped=0)

    if cal_frac_units <= 0 and cal_frac_spots <= 0:
        # H1 anchor: no calibration at all, T is the whole pool.
        info.update(calibration_unit="none", cal_status="cal_fraction_zero",
                    n_units_in_pool=len(np.unique(samp[pool])))
        return pool.copy(), np.zeros(n, bool), info

    for level in unit_hierarchy(design):
        if level == "spot":
            k = max(MIN_C_SPOTS, int(np.ceil(cal_frac_spots * len(pool_idx))))
            if k >= len(pool_idx):
                info.update(cal_status="pool_too_small_for_spot_calibration")
                return pool.copy(), np.zeros(n, bool), info
            C = np.zeros(n, bool)
            C[rng.choice(pool_idx, size=k, replace=False)] = True
            T = pool & ~C
            info.update(calibration_unit="spot", n_cal_units=k,
                        n_units_in_pool=len(pool_idx), n_cal_spots=int(C.sum()),
                        **sharing_flags(C, E, samp, meta))
            return T, C, info

        if level in ("patient", "donor", "slide"):
            keyf = {"patient": meta["patient_of"], "donor": meta["donor_of"],
                    "slide": {s: s for s in np.unique(samp)}}[level]
            lab = np.array([keyf.get(s) if keyf.get(s) is not None else "__NA__"
                            for s in samp], dtype=object)
            units = sorted({u for u in lab[pool]})
            info["n_units_in_pool"] = len(units)
            if len(units) < 2:
                continue                       # not supported; fall to the next level
            k = max(1, int(np.ceil(cal_frac_units * len(units))))
            k = min(k, len(units) - 1)         # T must keep at least one unit
            pick = set(rng.permutation(np.array(units, dtype=object))[:k].tolist())
            C = pool & np.isin(lab, list(pick))
            T = pool & ~C
            if C.sum() < MIN_C_SPOTS or T.sum() < MIN_T_SPOTS:
                continue
            info.update(calibration_unit=level, n_cal_units=k, n_cal_spots=int(C.sum()))
            break

        if level == "block":
            C, nb_ch, nb_tot = block_pick(pool_idx, samp, xy, CAL_BLOCK_FRAC, rng)
            T = pool & ~C
            drop = buffer_drop(samp, xy, C, T)
            T = T & ~drop
            info.update(calibration_unit="block", n_cal_units=nb_ch,
                        n_units_in_pool=nb_tot, n_cal_spots=int(C.sum()),
                        n_blocks_total=nb_tot, n_train_buffer_dropped=int(drop.sum()))
            break
    else:
        info.update(cal_status="no_calibration_set_possible")
        return pool.copy(), np.zeros(n, bool), info

    if C.sum() < MIN_C_SPOTS:
        info["cal_status"] = f"calibration_too_small_{int(C.sum())}_spots"
    elif T.sum() < MIN_T_SPOTS:
        info["cal_status"] = f"training_too_small_{int(T.sum())}_spots"

    info.update(**sharing_flags(C, E, samp, meta))
    return T, C, info


# ------------------------------------------------------------------- fold specs
def build_fold_specs(td, samp, xy, designs, meta, args):
    """Enumerate every (design, fold, repeat, cal draw) BEFORE any fitting, so that size
    matching can subsample to the smallest proper-training set and so that a fold with no
    possible calibration set is reported rather than discovered mid-run."""
    n = len(samp)
    task = td["task"]
    specs = []
    of_sample = {s: (samp == s) for s in np.unique(samp)}

    def mask_of(ids):
        m = np.zeros(n, bool)
        for s in ids:
            m |= of_sample[s]
        return m

    n_rep = args.n_repeats if args.n_repeats is not None else \
        td["folds"]["random"]["n_repeats"]
    cal_fu = 0.0 if args.h1_anchor else CAL_UNIT_FRAC
    cal_fs = 0.0 if args.h1_anchor else CAL_SPOT_FRAC

    for design in designs:
        if design == "random":
            folds = td["folds"]["patient"]           # test_size_from_fold
            if args.max_folds:
                folds = folds[:args.max_folds]
            for fd in folds:
                sz = int(mask_of(fd["test"]).sum())
                for rep in range(n_rep):
                    rng = np.random.default_rng(
                        zlib.crc32(f"{task}|random|{fd['fold']}|rep{rep}".encode()))
                    E = np.zeros(n, bool)
                    E[rng.choice(n, size=sz, replace=False)] = True
                    pool = ~E
                    ndraw = args.spot_cal_draws if not args.h1_anchor else 1
                    for draw in range(ndraw):
                        key = f"{task}|random|{fd['fold']}|rep{rep}"
                        T, C, info = choose_calibration(
                            design, pool, E, samp, xy, meta, key, draw, cal_fu, cal_fs)
                        specs.append(dict(task=task, design=design, fold=str(fd["fold"]),
                                          repeat=rep, cal_draw=draw, T=T, C=C, E=E,
                                          info=info))
            continue

        folds = td["folds"][design]
        if args.max_folds:
            folds = folds[:args.max_folds]
        for fd in folds:
            E = mask_of(fd["test"])
            pool = mask_of(fd["train"])
            assert not (E & pool).any(), f"{task} {design} {fd['fold']}: train/test overlap"
            if not E.any() or not pool.any():
                continue
            # Three calibration draws where the pool has at least three units at the level
            # the rule will actually use, one otherwise. Probing with draw 0 is how the unit
            # level becomes known without duplicating the hierarchy logic here.
            _, _, probe = choose_calibration(design, pool, E, samp, xy, meta,
                                             f"{task}|{design}|{fd['fold']}", 0,
                                             cal_fu, cal_fs)
            ndraw = (args.n_cal_draws
                     if (probe["n_units_in_pool"] or 0) >= 3 and not args.h1_anchor else 1)
            for draw in range(ndraw):
                key = f"{task}|{design}|{fd['fold']}"
                T, C, info = choose_calibration(design, pool, E, samp, xy, meta, key,
                                                draw, cal_fu, cal_fs)
                specs.append(dict(task=task, design=design, fold=str(fd["fold"]),
                                  repeat=-1, cal_draw=draw, T=T, C=C, E=E, info=info))
    return specs


def size_match_groups(specs, mode):
    """Section 4.2: "Proper-training sets are size-matched across designs within a fold by
    subsampling to the smallest, as R3 did, and the sizes are recorded."

    INTERPRETATION, flagged in the stage report rather than applied silently. "Within a fold"
    is well defined only for `random` and `patient`, which share the shipped fold index -- and
    on those two the pools are the SAME SIZE by construction (both are the task minus a test
    set of the shipped fold's size), so a per-fold match across those two designs is a no-op.
    `donor` folds are keyed by donor_id and `slide_out` folds by slide name; neither has a
    shipped fold index, so there is no fold to match them within. The comparison A1 actually
    makes is across designs WITHIN A TASK (a1_by_task.csv), so the default here matches every
    proper-training set in the task to the smallest one in the task, which is the literal
    "subsampling to the smallest across designs".

      task  one n_match per task, the minimum natural |T| over every design, fold, repeat and
            calibration draw REQUESTED IN THIS RUN. The requested design list is therefore
            part of the config hash: running one design alone gives a different n_match.
      fold  match within (fold id) only, which leaves donor and slide_out unmatched across
            designs. Provided so the choice can be overruled with a flag.
      none  no subsampling. Used by --h1-anchor, which must reproduce R1b's full training set.
    """
    if mode == "none":
        for s in specs:
            s["n_match"] = None
        return
    key = ((lambda s: s["task"]) if mode == "task"
           else (lambda s: (s["task"], s["fold"])))
    mins = {}
    for s in specs:
        k = key(s)
        mins[k] = min(mins.get(k, np.inf), int(s["T"].sum()))
    for s in specs:
        s["n_match"] = int(mins[key(s)])


def apply_size_match(spec, task):
    """Subsample T to n_match with a crc32 seed. Never touches C or E."""
    T = spec["T"]
    nat = int(T.sum())
    spec["n_train_natural"] = nat
    nm = spec["n_match"]
    if nm is None or nm >= nat:
        spec["n_train_matched"] = nat
        return T
    rng = np.random.default_rng(zlib.crc32(
        f"{task}|{spec['design']}|{spec['fold']}|rep{spec['repeat']}|"
        f"draw{spec['cal_draw']}|match{nm}".encode()))
    sel = np.zeros(len(T), bool)
    sel[rng.choice(np.flatnonzero(T), size=nm, replace=False)] = True
    spec["n_train_matched"] = nm
    return sel


# ------------------------------------------------------------------ conformal core
def conformal_quantile(S, alpha):
    """Per-column ceil((n+1)(1-alpha))/n empirical quantile of calibration scores.

    S is (n_cal, n_gene) and finite. Returns (n_gene,), +inf where n_cal is too small for the
    level to be attainable, which is the honest answer rather than the largest score.
    """
    n = S.shape[0]
    k = int(np.ceil((n + 1) * (1.0 - alpha)))
    if k > n:
        return np.full(S.shape[1], np.inf), True
    return np.sort(S, axis=0)[k - 1, :], False


def interval_metrics(y, lo, hi, alpha):
    """Per-gene coverage, mean width, Winkler interval score, and the two one-sided misses.
    All arrays are (n_spot, n_gene); returns dict of (n_gene,)."""
    below = y < lo
    above = y > hi
    cov = ~(below | above)
    width = hi - lo
    w = width.copy()
    w = np.where(below, w + (2.0 / alpha) * (lo - y), w)
    w = np.where(above, w + (2.0 / alpha) * (y - hi), w)
    return dict(coverage=cov.mean(axis=0), width_mean=width.mean(axis=0),
                interval_score=w.mean(axis=0), miss_above=above.mean(axis=0),
                miss_below=below.mean(axis=0), n_cov=cov.sum(axis=0))


# ------------------------------------------------------------------------- main
def run_one(td, enc, args, designs, scores, state):
    """Run every (design, fold, repeat, calibration draw) cell of ONE task definition,
    appending into `state`. Returns the load and fit wall time."""
    t0 = time.time()
    task, label_set = td["task"], td["label_set"]
    meta = dict(
        donor_of={s["sample_id"]: s["donor_id"] for s in td["samples"]},
        patient_of={s["sample_id"]: s["hest_patient"] for s in td["samples"]},
        resgroup_of={s["sample_id"]: s["resolution_group"] for s in td["samples"]},
        session_of={s["sample_id"]: s["session"] for s in td["samples"]},
    )
    X, Y, samp, bc, xy, genes = load_task(td, enc)
    n, dim = X.shape
    state["dims"][task] = dim
    state["n_spots"][task] = n
    print(f"[load] {task}/{label_set} {enc}: {n:,} spots x {dim} dims, {len(genes)} genes, "
          f"{len(np.unique(samp))} slides, {time.time()-t0:.0f}s", flush=True)

    specs = build_fold_specs(td, samp, xy, designs, meta, args)
    size_match_groups(specs, args.size_match)
    print(f"[specs] {task}: {len(specs)} cells; size_match={args.size_match}", flush=True)

    for i, sp in enumerate(specs):
        Tm = apply_size_match(sp, task)
        Cm, Em = sp["C"], sp["E"]
        info = sp["info"]

        # ---- H3, disjointness: asserted per fold on (sample_id, barcode) ----
        keys = {nm: set(zip(samp[m].tolist(), bc[m].tolist()))
                for nm, m in (("T", Tm), ("C", Cm), ("E", Em))}
        ov_tc = len(keys["T"] & keys["C"])
        ov_te = len(keys["T"] & keys["E"])
        ov_ce = len(keys["C"] & keys["E"])
        assert ov_tc == ov_te == ov_ce == 0, (
            f"{task} {sp['design']} {sp['fold']}: T/C/E not disjoint on "
            f"(sample_id, barcode): T&C={ov_tc} T&E={ov_te} C&E={ov_ce}")
        assert len(keys["T"]) == int(Tm.sum()), \
            f"{task}: duplicate (sample_id, barcode) inside T"

        if int(Tm.sum()) < MIN_T_SPOTS:
            if info["cal_status"] == "ok":
                info["cal_status"] = f"training_too_small_{int(Tm.sum())}_spots"
            print(f"  [skip] {task} {sp['design']} fold={sp['fold']}: |T|="
                  f"{int(Tm.sum())} < {MIN_T_SPOTS} ({info['cal_status']})", flush=True)
            state["cal"].append(_cal_row(enc, td, sp, info, Tm, Cm, Em, samp, args))
            continue

        pipe, A, reg, ridge_alpha = fit_base(X[Tm], Y[Tm])
        chk = scaler_pca_saw_only_T(pipe, X[Tm])
        state["h3"].append(dict(
            encoder=enc, task=task, label_set=label_set, design=sp["design"],
            fold=sp["fold"], repeat=sp["repeat"], cal_draw=sp["cal_draw"],
            n_T=int(Tm.sum()), n_C=int(Cm.sum()), n_E=int(Em.sum()),
            overlap_T_C=ov_tc, overlap_T_E=ov_te, overlap_C_E=ov_ce,
            disjoint=bool(ov_tc == ov_te == ov_ce == 0),
            scaler_pca_fit_rows_equal_T=bool(chk["n_samples_seen"] == int(Tm.sum())
                                             and chk["pca_n_samples"] == int(Tm.sum())),
            **chk))

        E_idx = np.flatnonzero(Em)
        B = pipe.transform(X[Em].astype(np.float64, copy=False))
        P_E = reg.predict(B)
        Y_E = Y[Em].astype(np.float64, copy=False)

        if args.h1_anchor:
            # Per-gene Pearson pooled over the whole test fold, which is exactly how R1b's
            # head_intercept__<enc>__f64.csv computes the column H1 anchors to.
            for j, g in enumerate(genes):
                r = (float(pearsonr(P_E[:, j], Y_E[:, j])[0])
                     if np.std(Y_E[:, j]) > 0 and np.std(P_E[:, j]) > 0 else np.nan)
                state["h1"].append(dict(encoder=enc, task=task, fold=sp["fold"], gene=g,
                                        pearson=r, n_train=int(Tm.sum()),
                                        n_test=int(Em.sum())))
            state["cal"].append(_cal_row(enc, td, sp, info, Tm, Cm, Em, samp, args))
            print(f"  [{i+1}/{len(specs)}] {task} h1 fold={sp['fold']} "
                  f"n_train={int(Tm.sum())} n_test={int(Em.sum())} "
                  f"{time.time()-t0:.0f}s", flush=True)
            continue

        if Cm.sum() < MIN_C_SPOTS:
            state["cal"].append(_cal_row(enc, td, sp, info, Tm, Cm, Em, samp, args))
            print(f"  [skip] {task} {sp['design']} fold={sp['fold']}: |C|="
                  f"{int(Cm.sum())} < {MIN_C_SPOTS}; {info['cal_status']}", flush=True)
            continue

        A_C = pipe.transform(X[Cm].astype(np.float64, copy=False))
        P_C = reg.predict(A_C)
        Y_C = Y[Cm].astype(np.float64, copy=False)
        sig = fit_sigma(A, Y[Tm], reg, ridge_alpha) if "scaled" in scores else None

        for score in scores:
            if score == "abs":
                S_C = np.abs(Y_C - P_C)
                unit_E = np.ones_like(P_E)
            elif score == "scaled":
                s_raw_C, s_raw_E = sig.predict(A_C), sig.predict(B)
                s_C = np.maximum(s_raw_C, SIGMA_FLOOR)
                unit_E = np.maximum(s_raw_E, SIGMA_FLOOR)
                S_C = np.abs(Y_C - P_C) / s_C
                # Diagnostic, not part of the section 4.2 specification. A ridge on absolute
                # residuals is unconstrained in sign, so wherever it predicts a negative
                # value sigmahat lands on the 1e-3 floor and that calibration point's score
                # is inflated by three orders of magnitude, which drags the 90% quantile up
                # and makes every `scaled` interval on the fold enormous. The smoke run
                # showed mean widths of 13 to 14 on a log1p target that tops out near 3, so
                # the rate is recorded per fold rather than left to be discovered from a
                # width column in A1.
                state["sigma"].append(dict(
                    encoder=enc, task=task, label_set=label_set, design=sp["design"],
                    fold=sp["fold"], repeat=sp["repeat"], cal_draw=sp["cal_draw"],
                    sigma_floor=SIGMA_FLOOR,
                    frac_cal_at_floor=float((s_raw_C < SIGMA_FLOOR).mean()),
                    frac_test_at_floor=float((s_raw_E < SIGMA_FLOOR).mean()),
                    sigma_median_cal=float(np.median(s_C)),
                    sigma_median_test=float(np.median(unit_E)),
                    sigma_min_raw_cal=float(s_raw_C.min()),
                    score_p90_cal=float(np.quantile(S_C, 0.90)),
                    score_p99_cal=float(np.quantile(S_C, 0.99))))
            else:
                raise ValueError(score)
            q_rep, inf_rep = conformal_quantile(S_C, args.alpha)
            q_sto, _ = conformal_quantile(S_C, args.alpha_store)
            half = unit_E * q_rep[None, :]
            lo, hi = P_E - half, P_E + half

            for s in np.unique(samp[Em]):
                sl = samp[E_idx] == s
                if not sl.any():
                    continue
                m = interval_metrics(Y_E[sl], lo[sl], hi[sl], args.alpha)
                nsl = int(sl.sum())
                for j, g in enumerate(genes):
                    state["pg"].append((
                        task, label_set, enc, sp["design"], sp["fold"], sp["repeat"],
                        sp["cal_draw"], score, info["calibration_unit"], s, g,
                        nsl, int(m["n_cov"][j]), float(m["coverage"][j]),
                        float(m["width_mean"][j]), float(m["interval_score"][j]),
                        float(m["miss_above"][j]), float(m["miss_below"][j]),
                        float(q_rep[j]), float(q_sto[j]),
                        bool(nsl >= MIN_SLIDE_SPOTS), bool(inf_rep)))

        state["cal"].append(_cal_row(enc, td, sp, info, Tm, Cm, Em, samp, args))
        print(f"  [{i+1}/{len(specs)}] {task} {sp['design']} fold={sp['fold']} "
              f"rep={sp['repeat']} draw={sp['cal_draw']} unit={info['calibration_unit']} "
              f"n_T={int(Tm.sum())} n_C={int(Cm.sum())} n_E={int(Em.sum())} "
              f"{time.time()-t0:.0f}s", flush=True)

    del X, Y
    return time.time() - t0


PG_COLS = ["task", "label_set", "encoder", "design", "fold", "repeat", "cal_draw",
           "score", "calibration_unit", "slide", "gene", "n_test", "n_covered",
           "coverage", "width_mean", "interval_score", "miss_above", "miss_below",
           "q_alpha_reported", "q_alpha_stored", "slide_ge_min_spots",
           "quantile_infinite"]


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    enc = args.encoder
    t_start = time.time()

    designs = [d for d in args.designs.split(",") if d]
    scores = [s for s in args.scores.split(",") if s]
    if args.h1_anchor:
        designs, scores = ["patient"], []
        args.size_match = "none"
    elif args.h2_check:
        designs = [d for d in designs if d == "random"] or ["random"]
        scores = ["abs"]
    for d in designs:
        assert d in DESIGNS, f"unknown design {d}"

    tds = []
    for p in args.task_def:
        td = json.load(open(p))
        assert td["task_def_version"] == 1, f"{p}: task_def_version {td['task_def_version']}"
        td["_path"] = p
        tds.append(td)

    out = f"{ROOT}/{args.out_dir}"
    os.makedirs(out, exist_ok=True)
    suf = f"__{enc}{args.tag}"

    config = dict(
        stage="round3_A0", script="code/scripts/round3_a0_harness.py",
        encoder=enc,
        tasks=[f"{t['task']}/{t['label_set']}" for t in tds],
        task_defs=[os.path.relpath(os.path.abspath(t["_path"]), ROOT) for t in tds],
        task_def_is_fixture=any("fixture_task_defs" in t["_path"] for t in tds),
        designs=designs, scores=scores, alpha=args.alpha, alpha_store=args.alpha_store,
        base_predictor="intercept_f64: StandardScaler -> PCA(256, random_state=1) -> "
                       "Ridge(alpha=100/(256*50), fit_intercept=True, solver=cholesky), "
                       "float64 from the raw embeddings",
        latent=LATENT, alpha_num=ALPHA_NUM, sigma_floor=SIGMA_FLOOR,
        cal_unit_frac=CAL_UNIT_FRAC, cal_spot_frac=CAL_SPOT_FRAC,
        cal_block_frac=CAL_BLOCK_FRAC, block_grid=BLOCK_GRID,
        buffer_pitches=BUFFER_PITCHES, n_cal_draws=args.n_cal_draws,
        spot_cal_draws=args.spot_cal_draws, n_repeats=args.n_repeats,
        max_folds=args.max_folds, size_match=args.size_match,
        min_slide_spots=MIN_SLIDE_SPOTS, min_T_spots=MIN_T_SPOTS,
        min_C_spots=MIN_C_SPOTS, h1_anchor=args.h1_anchor, h2_check=args.h2_check,
        seed_source="zlib.crc32",
    )
    # sha256 over canonical JSON. NOT hash(): Python randomises str hashing per process, so a
    # config_hash computed over a tuple containing strings identifies nothing, which is the
    # opposite of what a provenance record is for.
    config_blob = json.dumps(config, sort_keys=True)
    config_hash = hashlib.sha256(config_blob.encode()).hexdigest()[:16]
    print(f"[config] sha256/16 {config_hash}\n{config_blob}", flush=True)

    state = dict(cal=[], pg=[], h3=[], h1=[], sigma=[], dims={}, n_spots={},
                 wall={})
    for td in tds:
        state["wall"][f"{td['task']}/{td['label_set']}"] = round(
            run_one(td, enc, args, designs, scores, state), 1)

    # --------------------------------------------------- SUMMARIES BEFORE PARQUETS
    # Round 2 R3 lost the per-gene table of three completed 35-CPU-hour jobs to the final
    # parquet write and kept its reported results only because the summaries happened to be
    # written first. Ordered deliberately here.
    status = {"exit": 0, "notes": []}
    cal = pd.DataFrame(state["cal"])
    cal.to_csv(f"{out}/a1_calibration_units{suf}.csv", index=False)
    print(f"\n[write] a1_calibration_units{suf}.csv ({len(cal)} rows)", flush=True)
    if state["h3"]:
        h3 = pd.DataFrame(state["h3"])
        h3.to_csv(f"{out}/h3_disjointness{suf}.csv", index=False)
        ok = int((h3["disjoint"] & h3["scaler_pca_fit_rows_equal_T"]
                  & (h3["max_abs_scaler_mean_minus_T"] == 0)
                  & (h3["max_abs_scaler_var_minus_T"] == 0)
                  & (h3["max_abs_pca_mean_minus_T"] == 0)).sum())
        print(f"[write] h3_disjointness{suf}.csv ({len(h3)} folds); "
              f"disjoint AND scaler/PCA statistics reproduced exactly from T: "
              f"{ok}/{len(h3)}", flush=True)
        if ok != len(h3):
            status["exit"] = max(status["exit"], 4)
            status["notes"].append(f"H3 FAILURE: {len(h3)-ok}/{len(h3)} folds")

    if state["sigma"]:
        sg = pd.DataFrame(state["sigma"])
        sg.to_csv(f"{out}/a1_sigma_diagnostics{suf}.csv", index=False)
        print(f"[write] a1_sigma_diagnostics{suf}.csv ({len(sg)} rows); "
              f"fraction of calibration spot-genes whose sigmahat hit the {SIGMA_FLOOR:g} "
              f"floor: min {sg['frac_cal_at_floor'].min():.4f} "
              f"median {sg['frac_cal_at_floor'].median():.4f} "
              f"max {sg['frac_cal_at_floor'].max():.4f}", flush=True)

    pg = pd.DataFrame(state["pg"], columns=PG_COLS)
    if args.h1_anchor:
        _h1(out, suf, enc, pd.DataFrame(state["h1"]), args, status)
    else:
        _summaries(out, suf, pg, cal, args)
        if args.h2_check:
            _h2(out, suf, pg, args, status)
        if not args.no_parquet and len(pg):
            _parquet(out, suf, pg, PG_COLS)

    _provenance(out, suf, config, config_blob, config_hash, args, state,
                len(state["cal"]), time.time() - t_start, status)

    print(f"\n[done] {time.time()-t_start:.0f}s  exit={status['exit']}", flush=True)
    for nt in status["notes"]:
        print(f"  {nt}", flush=True)
    return status["exit"]


def _cal_row(enc, td, sp, info, Tm, Cm, Em, samp, args):
    return dict(encoder=enc, task=td["task"], label_set=td["label_set"],
                design=sp["design"], fold=sp["fold"], repeat=sp["repeat"],
                cal_draw=sp["cal_draw"],
                calibration_unit=info["calibration_unit"],
                n_units_in_pool=info["n_units_in_pool"],
                n_cal_units=info["n_cal_units"], n_cal_spots=int(Cm.sum()),
                n_cal_slides=info.get("n_cal_slides"),
                n_pool_spots=info["n_pool_spots"],
                n_train_natural=sp.get("n_train_natural", int(Tm.sum())),
                n_train_matched=sp.get("n_train_matched", int(Tm.sum())),
                n_match_target=sp.get("n_match"),
                n_train_buffer_dropped=info.get("n_train_buffer_dropped", 0),
                n_blocks_total=info.get("n_blocks_total"),
                n_test=int(Em.sum()),
                n_test_slides=len(np.unique(samp[Em])),
                test_slides=";".join(sorted(set(np.unique(samp[Em]).tolist()))),
                cal_slides=";".join(sorted(set(np.unique(samp[Cm]).tolist())))
                           if Cm.any() else "",
                cal_shares_donor_with_test=info.get("cal_shares_donor_with_test"),
                cal_shares_session_with_test=info.get("cal_shares_session_with_test"),
                cal_shares_resolution_group_with_test=info.get(
                    "cal_shares_resolution_group_with_test"),
                cal_shares_exact_session_with_test=info.get(
                    "cal_shares_exact_session_with_test"),
                cal_status=info["cal_status"], size_match=args.size_match)


def _summaries(out, suf, pg, cal, args):
    if not len(pg):
        print("[summaries] no per-gene rows", flush=True)
        return
    use = pg[pg["slide_ge_min_spots"]]
    if not len(use):
        use = pg
    grp = ["task", "label_set", "encoder", "design", "score", "fold", "repeat",
           "cal_draw", "calibration_unit"]
    # per slide -> mean over slides -> per gene
    by_slide = (use.groupby(grp + ["slide"], dropna=False)
                   .agg(coverage=("coverage", "mean"),
                        width_mean=("width_mean", "mean"),
                        interval_score=("interval_score", "mean"),
                        miss_above=("miss_above", "mean"),
                        miss_below=("miss_below", "mean"),
                        n_test=("n_test", "first"), n_genes=("gene", "nunique"))
                   .reset_index())
    by_slide.to_csv(f"{out}/a1_by_slide{suf}.csv", index=False)
    print(f"[write] a1_by_slide{suf}.csv ({len(by_slide)} rows)", flush=True)

    per_gene_over_slides = (use.groupby(grp + ["gene"], dropna=False)
                               [["coverage", "width_mean", "interval_score",
                                 "miss_above", "miss_below"]].mean().reset_index())
    per_cell = (per_gene_over_slides.groupby(grp, dropna=False)
                [["coverage", "width_mean", "interval_score", "miss_above",
                  "miss_below"]].mean().reset_index())
    # mean over repeats and calibration draws inside a fold, then over folds
    fold_grp = ["task", "label_set", "encoder", "design", "score", "fold"]
    per_fold = (per_cell.groupby(fold_grp, dropna=False)
                [["coverage", "width_mean", "interval_score", "miss_above",
                  "miss_below"]].mean().reset_index())
    unit = (cal.groupby(["task", "design", "fold"])["calibration_unit"]
              .agg(lambda s: ";".join(sorted({str(x) for x in s}))).reset_index())
    per_fold = per_fold.merge(unit, on=["task", "design", "fold"], how="left")
    per_fold.to_csv(f"{out}/a1_by_fold{suf}.csv", index=False)

    nmatch = (cal.groupby(["task", "design"])["n_train_matched"].min()
                 .rename("n_train_matched").reset_index())
    by_task = (per_fold.groupby(["task", "label_set", "encoder", "design", "score"],
                                dropna=False)
               .agg(n_folds=("fold", "nunique"),
                    coverage_mean=("coverage", "mean"), coverage_sd=("coverage", "std"),
                    width_mean=("width_mean", "mean"), width_sd=("width_mean", "std"),
                    interval_score_mean=("interval_score", "mean"),
                    miss_above_mean=("miss_above", "mean"),
                    miss_below_mean=("miss_below", "mean"))
               .reset_index())
    cu = (per_fold.groupby(["task", "design"])["calibration_unit"]
            .agg(lambda s: ";".join(sorted({str(x) for x in s.dropna()}))).reset_index())
    by_task = by_task.merge(cu, on=["task", "design"], how="left").merge(
        nmatch, on=["task", "design"], how="left")
    by_task.to_csv(f"{out}/a1_by_task{suf}.csv", index=False)
    print(f"[write] a1_by_task{suf}.csv ({len(by_task)} rows)", flush=True)
    print(by_task.round(4).to_string(index=False), flush=True)

    disp = (per_cell.groupby(fold_grp + ["calibration_unit"], dropna=False)
            .agg(n_cal_draws=("cal_draw", "nunique"),
                 coverage_mean=("coverage", "mean"),
                 coverage_sd_across_cal_draws=("coverage", "std"),
                 width_sd_across_cal_draws=("width_mean", "std")).reset_index())
    disp.to_csv(f"{out}/a1_cal_dispersion{suf}.csv", index=False)
    print(f"[write] a1_cal_dispersion{suf}.csv ({len(disp)} rows)", flush=True)


def _parquet(out, suf, pg, cols):
    SCHEMA = pa.schema([
        ("task", pa.string()), ("label_set", pa.string()), ("encoder", pa.string()),
        ("design", pa.string()),
        # `fold` is a STRING for every design. The slide_out design's fold ids are slide
        # names and the donor design's are donor ids, while patient's are integers; pandas
        # type inference read int64 from the leading rows and killed three completed round-2
        # R3 jobs at the final write. Naming the type removes the pyarrow version dependence
        # rather than making the failure less likely.
        ("fold", pa.string()),
        ("repeat", pa.int32()), ("cal_draw", pa.int32()), ("score", pa.string()),
        ("calibration_unit", pa.string()), ("slide", pa.string()), ("gene", pa.string()),
        ("n_test", pa.int32()), ("n_covered", pa.int32()),
        ("coverage", pa.float32()), ("width_mean", pa.float32()),
        ("interval_score", pa.float32()), ("miss_above", pa.float32()),
        ("miss_below", pa.float32()), ("q_alpha_reported", pa.float32()),
        ("q_alpha_stored", pa.float32()), ("slide_ge_min_spots", pa.bool_()),
        ("quantile_infinite", pa.bool_()),
    ])
    assert [f.name for f in SCHEMA] == cols, "schema/column mismatch"
    d = pg.copy()
    for f in SCHEMA:
        if f.type == pa.string():
            d[f.name] = d[f.name].astype(str)
        elif f.type == pa.int32():
            d[f.name] = d[f.name].astype("int32")
        elif f.type == pa.float32():
            d[f.name] = d[f.name].astype("float32")
        elif f.type == pa.bool_():
            d[f.name] = d[f.name].astype(bool)
    pq.write_table(pa.Table.from_pandas(d[cols], schema=SCHEMA, preserve_index=False),
                   f"{out}/pergene{suf}.parquet", compression="snappy")
    print(f"[write] pergene{suf}.parquet ({len(d):,} rows, explicit schema)", flush=True)


def _h1(out, suf, enc, h1, args, status):
    """H1, the anchor to the prior result: the harness's per-task Pearson under the `patient`
    design with the calibration fraction set to zero must equal R1b's `intercept_f64`
    per-task Pearson to within --h1-tol for every encoder-task cell.

    The reference is read from results/round2/R1b_heads/head_intercept__<enc>__f64.csv, rows
    with head == "intercept_f64", aggregated mean over genes within a fold then mean over
    folds. That is the same aggregation R1b's own faithful_check__<enc>__f64.csv applies to
    its `nointercept_f64` rows, and R1b measured max|dPearson(intercept - nointercept)| at
    1.95e-14, so the two R1b columns are the same number to machine precision.
    """
    assert len(h1), "H1 mode produced no per-gene rows"
    h1.to_csv(f"{out}/h1_pergene{suf}.csv", index=False)
    ours = (h1.groupby(["task", "fold"])["pearson"].mean()
              .groupby("task").mean().rename("ours").reset_index())
    src = f"{ROOT}/{args.r1b_dir}/head_intercept__{enc}__f64.csv"
    if not os.path.exists(src):
        status["exit"] = 3
        status["notes"].append(f"H1 CANNOT RUN: {src} absent")
        ours.to_csv(f"{out}/h1_by_task{suf}.csv", index=False)
        return
    r1 = pd.read_csv(src)
    r1 = r1[r1["head"] == "intercept_f64"]
    assert len(r1), f"{src} has no intercept_f64 rows; heads = {sorted(r1['head'].unique())}"
    ref = (r1.groupby(["task", "fold"])["pearson"].mean()
             .groupby("task").mean().rename("r1b_intercept_f64").reset_index())
    cmp = ours.merge(ref, on="task", how="left")
    cmp["abs_diff"] = (cmp["ours"] - cmp["r1b_intercept_f64"]).abs()
    cmp["tol"] = args.h1_tol
    cmp["passed"] = cmp["abs_diff"] < args.h1_tol
    cmp["encoder"] = enc
    cmp["r1b_source"] = os.path.relpath(src, ROOT)
    cmp.to_csv(f"{out}/h1_by_task{suf}.csv", index=False)
    print(f"\n=== H1 anchor to R1b intercept_f64, source {os.path.relpath(src, ROOT)} ===")
    print(cmp.to_string(index=False), flush=True)
    npass, ntot = int(cmp["passed"].sum()), len(cmp)
    mx = float(cmp["abs_diff"].max())
    print(f"H1: {npass}/{ntot} task cells within {args.h1_tol:g}; "
          f"max |diff| = {mx:.3e}  {'PASS' if npass == ntot else 'FAIL'}", flush=True)
    if npass != ntot:
        status["exit"] = 1
        status["notes"].append(
            f"*** H1 FAILURE, STOP CONDITION *** {ntot-npass}/{ntot} cells exceed "
            f"{args.h1_tol:g}; max |diff| = {mx:.3e}. Section 4.2: work stops and reports.")


def _h2(out, suf, pg, args, status):
    """H2: on random with abs, marginal coverage POOLED over folds within 0.02 of 0.90."""
    d = pg[(pg["design"] == "random") & (pg["score"] == "abs")]
    if not len(d):
        status["exit"] = 3
        status["notes"].append("H2 CANNOT RUN: no random/abs rows")
        return
    g = (d.groupby(["task", "label_set", "encoder"])
          .agg(n_covered=("n_covered", "sum"), n_points=("n_test", "sum"),
               n_folds=("fold", "nunique"), n_repeats=("repeat", "nunique"),
               n_genes=("gene", "nunique"), n_slides=("slide", "nunique"),
               any_infinite_quantile=("quantile_infinite", "any")).reset_index())
    # n_test is per (slide, gene) so the pooled denominator counts each spot once per gene,
    # which is the spot-gene level the intervals are formed at.
    g["coverage_pooled"] = g["n_covered"] / g["n_points"]
    g["deviation_from_nominal"] = (g["coverage_pooled"] - (1.0 - args.alpha)).abs()
    g["tol"] = args.h2_tol
    g["passed"] = g["deviation_from_nominal"] <= args.h2_tol
    g.to_csv(f"{out}/h2_coverage{suf}.csv", index=False)
    print(f"\n=== H2 pooled marginal coverage, random/abs, nominal {1-args.alpha:.2f} ===")
    print(g.round(5).to_string(index=False), flush=True)
    npass, ntot = int(g["passed"].sum()), len(g)
    worst = float(g["deviation_from_nominal"].max())
    print(f"H2: {npass}/{ntot} cells within {args.h2_tol:g}; worst deviation = "
          f"{worst:.4f}  {'PASS' if npass == ntot else 'FAIL'}", flush=True)
    if npass != ntot:
        status["exit"] = 2
        status["notes"].append(
            f"*** H2 FAILURE, STOP CONDITION *** {ntot-npass}/{ntot} cells outside "
            f"{args.h2_tol:g} of {1-args.alpha:.2f}; worst {worst:.4f}. "
            f"Section 4.2: the conformal implementation is wrong; work stops and reports.")


def _provenance(out, suf, config, blob, chash, args, state, nspecs, wall, status):
    """One provenance file per invocation, named for the encoder and tag.

    Not a shared appended PROVENANCE.txt: 12 encoder jobs run concurrently in A1 and an
    append from 12 processes to one file is exactly the multi-writer case the handoff's
    one-writer-per-file rule exists to prevent. A single directory-level PROVENANCE.txt is
    assembled afterwards by one writer.
    """
    p = f"{out}/PROVENANCE{suf}.txt"
    commit = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    with open(p, "w") as f:
        f.write(
            f"{'='*78}\n"
            f"Round 3, stage A0 - conformal harness, encoder {config['encoder']}\n"
            f"tasks           : {', '.join(config['tasks'])}\n"
            f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID','NA')}\n"
            f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION','NA')}\n"
            f"node            : {os.environ.get('SLURMD_NODENAME','NA')}\n"
            f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
            f"repo_commit     : {commit}\n"
            f"script          : code/scripts/round3_a0_harness.py\n"
            f"command_line    : {' '.join(sys.argv)}\n"
            f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED', 'unset')}\n"
            f"task_defs       : {'; '.join(config['task_defs'])}"
            f"{'   (FIXTURE, not results/round3/task_defs/)' if config['task_def_is_fixture'] else ''}\n"
            f"n_spots_by_task : {json.dumps(state['n_spots'], sort_keys=True)}\n"
            f"embedding_dim   : {json.dumps(state['dims'], sort_keys=True)}\n"
            f"n_cells_run     : {nspecs} (design, fold, repeat, cal draw)\n"
            f"wall_seconds    : {wall:.0f}\n"
            f"wall_by_task    : {json.dumps(state['wall'], sort_keys=True)}\n"
            f"exit            : {status['exit']}\n"
            f"config_hash     : sha256/16 {chash}\n"
            f"config          : {blob}\n"
            f"plan            : round3_execution_plan.md section 4.2\n")
    print(f"[write] PROVENANCE{suf}.txt (config_hash {chash})", flush=True)


if __name__ == "__main__":
    sys.exit(main())
