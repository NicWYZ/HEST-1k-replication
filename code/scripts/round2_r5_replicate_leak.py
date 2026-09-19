#!/usr/bin/env python
"""Round 2, R3: split decomposition v4. Five designs, a grid sweep, per-gene storage.

Extends v3 (`code/scripts/split_decomposition.py`). The within-slide metric and the
training-size matching are carried over UNCHANGED, so v4 must reproduce v3's per-task means
on the shared designs to within 1e-3; that is the acceptance check.

What v3 could not separate, and v4 can:

  v3's `blocked - patient` term mixes slide identity with same-patient-other-slide
  information, because the blocked arm trains on other blocks of EVERY slide including
  other slides of the test patient. In the three tasks where a patient contributes more
  than one slide (PRAD, COAD, READ) those are different things, and COAD's term is 0.2938
  against 0.026-0.163 elsewhere. `slide_out` splits them.

  v3's `blocked` arm holds out whole grid cells but imposes no buffer, so a test spot on a
  block edge still has training neighbours one pitch away. `blocked_buffered` removes every
  training spot within 2.5 spot pitches of any test spot on the same slide.

Designs and what each permits:
  random             same slide and patient in training, adjacency intact
  blocked            same slide, adjacency partly broken (block edges leak)
  blocked_buffered   same slide, adjacency broken
  slide_out          test slide unseen, test PATIENT seen (multi-slide tasks only)
  patient            the shipped design: patient unseen

Terms, all in within-slide Pearson:
  adjacency              = random - blocked_buffered
  block-edge residual    = blocked - blocked_buffered      (diagnostic; small and positive)
  same-slide identity    = blocked_buffered - slide_out    (multi-slide tasks)
                         = blocked_buffered - patient      (single-slide tasks; they coincide)
  same-patient-other-slide = slide_out - patient           (multi-slide tasks only)

Usage: round2_split_v4.py <encoder>
"""
import glob
import json
import os
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
BD, EMB = f"{ROOT}/bench_data", f"{ROOT}/embeddings"
OUT = f"{ROOT}/results/round2/R3_splits"
META = f"{ROOT}/results/tailored/integrity/sample_metadata.csv"
GATE = f"{ROOT}/results/tailored/morphology/fig3e_gate.csv"

SEED, LATENT, N_REPEATS, MIN_SPOTS = 1, 256, 5, 50
GRIDS = (4, 6, 10)
BUFFER_PITCHES = 2.5
# Decision 3: slide_out runs only where some patient has more than one slide. Verified from
# sample_metadata.csv, not taken from the plan's parenthetical, which also listed LYMPH_IDC
# (four patients, one slide each -- it uses the single-slide branch).
SLIDE_OUT_TASKS = ("PRAD", "COAD", "READ")

enc = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

sm = pd.read_csv(META)
PATIENT = dict(zip(sm.sample_id, sm.patient.fillna("UNKNOWN").astype(str)))
RESGRP = dict(zip(sm.sample_id, sm.resolution_group.astype(str)))

# D4's resolution-uncertainty flags are read from D4's OWN output, not from
# sample_metadata.csv. The D4 job rewrites that CSV, and reading a file another job is
# rewriting is how you get a silently truncated table; this keeps the two jobs independent.
D4 = f"{ROOT}/results/round2/R1b_heads/d4_pixel_size_check.csv"
if os.path.exists(D4):
    _d4 = pd.read_csv(D4)
    UNCERTAIN = dict(zip(_d4.sample_id, _d4.resolution_uncertain.astype(bool)))
    print(f"[D4] uncertainty flags loaded for {len(UNCERTAIN)} samples, "
          f"{sum(UNCERTAIN.values())} flagged", flush=True)
else:
    UNCERTAIN = {}
    print("[D4] d4_pixel_size_check.csv absent; resolution_uncertain reported as False "
          "everywhere. Re-derive this column before relying on the stratification.", flush=True)
gate = pd.read_csv(GATE) if os.path.exists(GATE) else pd.DataFrame()
PITCH = dict(zip(gate.sample_id, gate.spot_pitch_px)) if len(gate) else {}


def load_task(task):
    """v3's loader, verbatim."""
    genes = json.load(open(f"{BD}/{task}/var_50genes.json"))["genes"]
    Xs, Ys, samp, xy = [], [], [], []
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        sid = os.path.basename(p)[:-5]
        with h5py.File(f"{EMB}/{task}/{enc}/{sid}.h5", "r") as f:
            k = "barcodes" if "barcodes" in f else "barcode"
            b = np.asarray(f[k][:]).reshape(-1)
            bc = [x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in b]
            Xs.append(np.asarray(f["embeddings"][:], dtype=np.float32))
            xy.append(np.asarray(f["coords"][:], dtype=np.float64))
        A = ad.read_h5ad(p)
        sc.pp.log1p(A)
        sub = A[bc, genes]
        Y = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
        Ys.append(np.asarray(Y, dtype=np.float32))
        samp += [sid] * len(bc)
    return np.vstack(Xs), np.vstack(Ys), np.array(samp), np.vstack(xy), genes


def fit(Xtr, Xte, Ytr):
    """v3's fit, verbatim. Pearson is shift-invariant, so the missing intercept is
    immaterial here and keeping it identical is what makes v3 reproduction meaningful."""
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=min(LATENT, Xtr.shape[1]), random_state=SEED))])
    A = pipe.fit_transform(Xtr)
    B = pipe.transform(Xte)
    reg = Ridge(solver="lsqr", alpha=100 / (A.shape[1] * Ytr.shape[1]),
                random_state=0, fit_intercept=False, max_iter=1000).fit(A, Ytr)
    return reg.predict(B)


def score_pergene(P, Yte, samp_te, genes):
    """Per (slide, gene) Pearson, plus v3's two aggregates derived from it.

    v3's `pearson_within` is: per slide with at least MIN_SPOTS spots, mean over genes of
    Pearson; then mean over slides. Deriving it from the per-gene table rather than
    recomputing guarantees the stored vector and the reported mean agree.
    """
    rows, per_slide = [], []
    for s in np.unique(samp_te):
        m = samp_te == s
        if m.sum() < MIN_SPOTS:
            continue
        rs = []
        for j, g in enumerate(genes):
            if np.std(Yte[m, j]) > 0 and np.std(P[m, j]) > 0:
                r = float(pearsonr(P[m, j], Yte[m, j])[0])
                rows.append((s, g, r))
                rs.append(r)
        if rs:
            per_slide.append(float(np.mean(rs)))
    pooled = [pearsonr(P[:, j], Yte[:, j])[0] for j in range(Yte.shape[1])
              if np.std(Yte[:, j]) > 0 and np.std(P[:, j]) > 0]
    return (float(np.mean(pooled)) if pooled else np.nan,
            float(np.mean(per_slide)) if per_slide else np.nan,
            len(per_slide), rows)


def block_test(samp, xy, target_frac, rng, grid):
    """v3's block chooser, with the grid size as a parameter."""
    te = np.zeros(len(xy), bool)
    for s in np.unique(samp):
        m = samp == s
        c = xy[m]
        lo, hi = c.min(0), c.max(0)
        span = np.where(hi - lo == 0, 1.0, hi - lo)
        key = (np.clip(((c - lo) / span * grid).astype(int), 0, grid - 1) * [grid, 1]).sum(1)
        blocks, counts = np.unique(key, return_counts=True)
        tgt, acc, chosen = target_frac * m.sum(), 0, []
        for j in rng.permutation(len(blocks)):
            if acc >= tgt:
                break
            chosen.append(blocks[j])
            acc += counts[j]
        idx = np.flatnonzero(m)
        te[idx[np.isin(key, chosen)]] = True
    return te


def pitch_for(sid, samp, xy):
    """Spot pitch in pixels: fig3e_gate.csv if present, else the median nearest-neighbour
    distance on that slide, which is the pitch by construction for a regular lattice."""
    p = PITCH.get(sid)
    if p is not None and np.isfinite(p) and p > 0:
        return float(p)
    c = xy[samp == sid]
    if len(c) < 3:
        return np.nan
    d, _ = cKDTree(c).query(c, k=2)
    return float(np.median(d[:, 1]))


def buffer_mask(samp, xy, te):
    """Training spots to DROP: within BUFFER_PITCHES pitches of any test spot, same slide."""
    drop = np.zeros(len(xy), bool)
    for s in np.unique(samp):
        m = samp == s
        t = m & te
        if not t.any():
            continue
        r = BUFFER_PITCHES * pitch_for(s, samp, xy)
        if not np.isfinite(r):
            continue
        cand = np.flatnonzero(m & ~te)
        if not len(cand):
            continue
        near = cKDTree(xy[t]).query_ball_point(xy[cand], r=r)
        drop[cand[[i for i, nb in enumerate(near) if len(nb)]]] = True
    return drop


def nn_train_dist(samp, xy, te, tr):
    """Median distance from a test spot to its nearest TRAINING spot on the same slide.
    This is the quantity that must widen from `blocked` to `blocked_buffered`."""
    ds = []
    for s in np.unique(samp):
        m = samp == s
        t, r = m & te, m & tr
        if not (t.any() and r.any()):
            continue
        d, _ = cKDTree(xy[r]).query(xy[t], k=1)
        ds.append(d)
    return float(np.median(np.concatenate(ds))) if ds else np.nan


def res_flags(samp_te, samp_tr):
    """Resolution stratification: the test slide's group, and whether training contains any
    slide in the same group. In PRAD the patient design never does; slide_out always does."""
    te_g = sorted({RESGRP.get(s, "NA") for s in np.unique(samp_te)})
    tr_g = {RESGRP.get(s, "NA") for s in np.unique(samp_tr)}
    return (";".join(te_g), bool(set(te_g) & tr_g),
            bool(any(UNCERTAIN.get(s, False) for s in np.unique(samp_te))))


rows, pergene, diag = [], [], []


def record(task, design, fold, rep, grid, P, Y, samp, te, tr, genes):
    # `fold` is an int for the shipped-split designs and a slide id for slide_out, which
    # made the per-gene column object-typed and killed the parquet write AFTER a full run.
    # Stored as a string throughout, with the integer folds zero-padded so they sort, and
    # the numeric value kept separately for the designs that have one.
    fold_num = fold if isinstance(fold, (int, np.integer)) else None
    fold = f"{int(fold):02d}" if fold_num is not None else str(fold)
    po, wi, ns, pg = score_pergene(P, Y[te], samp[te], genes)
    grp, same_grp, unc = res_flags(samp[te], samp[tr])
    rows.append(dict(encoder=enc, task=task, design=design, fold=fold, fold_num=fold_num,
                     repeat=rep, grid=grid,
                     n_train=int(tr.sum()), n_test=int(te.sum()), n_eval_samples=ns,
                     pearson_pooled=po, pearson_within=wi,
                     test_resolution_group=grp, train_has_same_resolution_group=same_grp,
                     test_resolution_uncertain=unc,
                     test_slides=";".join(sorted(set(samp[te])))))
    for s, g, r in pg:
        pergene.append((task, design, fold, -1 if rep is None else rep, grid, s, g, r))



# ------------------------------------------------------------------- replicate_leak
# Quantifies the leak that HEST's IDC patient split contains, now that R5 has established
# TENX95 and TENX99 are two 5um sections of one resected tumour mass from one donor
# (10x dataset page "FFPE Human Breast using the Entire Sample Area", donorCount: 1).
#
# The donor_out arm alone cannot answer it: holding out BOTH TENX samples leaves only
# ~7k training spots against ~27-32k for the single-sample folds, so its lower accuracy
# could be training-set size rather than the missing replicate. This arm fixes BOTH the
# test set and the training size and varies only whether the replicate is available:
#
#   test = TENX99 (or TENX95), n_train = N for both arms, and
#     with_replicate    training drawn from {the other TENX sample} + {NCBI783, NCBI785}
#     without_replicate training drawn from {NCBI783, NCBI785} only
#
# The difference is the replicate leak, in within-slide Pearson, on the benchmark's own
# held-out samples.
TASK = "IDC"
TENX = ["TENX95", "TENX99"]
NCBI = ["NCBI783", "NCBI785"]

X, Y, samp, xy, genes = load_task(TASK)
n = len(X)
assert set(samp) == set(TENX + NCBI), sorted(set(samp))
n_ncbi = int(np.isin(samp, NCBI).sum())
print(f"[{TASK}] spots: " + ", ".join(f"{s}={int((samp==s).sum())}" for s in sorted(set(samp))))
print(f"[{TASK}] NCBI pool = {n_ncbi} spots; this caps n_train for both arms", flush=True)

for test_slide in TENX:
    other = [s for s in TENX if s != test_slide][0]
    te = samp == test_slide
    pool_with = np.flatnonzero(np.isin(samp, [other] + NCBI))
    pool_without = np.flatnonzero(np.isin(samp, NCBI))
    # both arms get the same training size: everything the NCBI-only pool can supply
    N = int(min(len(pool_with), len(pool_without)))
    for rep in range(N_REPEATS):
        for arm, pool in (("with_replicate", pool_with), ("without_replicate", pool_without)):
            rng = np.random.default_rng(SEED + 7717 * rep
                                        + zlib.crc32((test_slide + arm).encode()) % 100000)
            sel = np.zeros(n, bool)
            sel[rng.choice(pool, size=N, replace=False)] = True
            assert not (sel & te).any()
            record(TASK, arm, test_slide, rep, None,
                   fit(X[sel], X[te], Y[sel]), Y, samp, te, sel, genes)
    print(f"  test={test_slide}: both arms n_train={N}, n_test={int(te.sum())}", flush=True)

d_ = pd.DataFrame(rows)
d_.to_csv(f"{OUT}/replicate_leak__{enc}.csv", index=False)
piv = d_.pivot_table(index="fold", columns="design", values="pearson_within",
                     aggfunc=["mean", "std"])
print(f"\nwrote {OUT}/replicate_leak__{enc}.csv ({len(d_)} rows)")
print(piv.round(4).to_string())
w = d_[d_.design == "with_replicate"].groupby("fold").pearson_within.mean()
o = d_[d_.design == "without_replicate"].groupby("fold").pearson_within.mean()
print("\nreplicate leak (with - without), within-slide Pearson:")
for s in sorted(w.index):
    print(f"  test={s}: {w[s]:.4f} - {o[s]:.4f} = {w[s]-o[s]:+.4f}")
print(f"  mean over the two held-out replicates: {(w-o).mean():+.4f}")
