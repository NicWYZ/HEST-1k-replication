#!/usr/bin/env python
"""Round 2, stage R4: probes v2.

Stage: R5d, the IDC partner-confusion probe (round2_R5_decisions.md directive 2.2).

Three probes, each with its interpretation rule fixed in this docstring BEFORE the run,
per the plan's acceptance requirement. Probe 4 is a relabelling with no new compute and is
handled in the report, not here.

Probe 1 -- slide identity WITHIN one patient.
  PRAD patient 2: 15 slides, pixel sizes 0.3412 to 0.3492 um/px, one patient, so biology
  and resolution are near-constant across the 15 classes. Target: slide id, chance 1/15.
  Evaluated under spatial block CV (whole blocks held out, as round 1's spatial_block_probe)
  with the random within-slide split as an upper bound.
  RULE: blocked balanced accuracy above 0.8 => slide signatures are technical in origin
  (section, stain lot, scanner), since biology and resolution are nearly constant here.
  Near chance => round 1's 0.98 across-patient figure was mostly biology and resolution.

Probe 2 -- resolution WITHIN one patient.
  PRAD patient 1. Grouping the raw pixel sizes by nominal value gives
  {0.57: MEND154/156/157/158/160 (5), 0.69: MEND159/161 (2), 0.17: MEND162 (1)}.
  Per oversight decision 1.1 the single 0.17 slide is excluded from BOTH training and
  evaluation -- it cannot be held out with its class present, and left in training it only
  adds a class that is never tested. Two classes, leave-one-slide-out over the remaining
  seven slides, balanced chance 0.5. The binned variant is dropped entirely, not reported:
  under R0's bins these eight slides occupy only two bins, since 0.573 and 0.688 both
  exceed 0.50, so the binned form of this probe is undefined for this patient.
  PRAD carries no embedded pixel size, so the class labels rest on the spot-spacing
  estimate alone. For Visium that is the more reliable of the two sources, being derived
  from the known 100 um pitch, so the probe is well defined and the flag is a caveat.
  RULE: high accuracy => scan resolution is decodable from the embeddings independently of
  patient, and every slide-identity probe is partly a resolution probe.

Probe 1b -- the scan sub-cluster (oversight decision 2.1).
  PRAD patient 2's fifteen slides fall in two tight sub-clusters, verified from the
  metadata rather than from the slide-id ranges: eight at 0.3412-0.3418 (MEND139-MEND146)
  and seven at 0.3484-0.3492 (MEND147-MEND153), separated by 0.0066 um/px. Target that
  membership, leave-one-slide-out, chance 0.5. Probe 1's confusion matrix is also written
  out and its off-diagonal mass split into within- against between-sub-cluster.
  RULE: if slide identity is decodable but the confusion is mostly WITHIN sub-cluster, the
  signature is per-slide; if it is BETWEEN sub-clusters, part of it is a scan-session
  effect.

Probe 3 -- composition-adjusted slide probe.
  IDC, PAAD, LUNG, SKCM (single-slide patients, Xenium), plus PRAD patient 2 per decision
  2.1 so that Probe 1 has an adjusted counterpart. The PCA-256 features are regressed
  on per-spot morphology covariates (n_nuclei, neo_area_mean, and the five CellViT class
  fractions) with the regression FIT ON TRAINING SPOTS ONLY, and the slide probe is rerun on
  the residuals. Accuracy is reported before and after.
  RULE: a large drop => tissue composition explains the slide separability. No drop => it
  does not, and the separability is something composition does not capture.

Usage: round2_r4_probes.py <encoder> [<encoder> ...]
"""
import glob
import os
import sys
import time
import zlib

import h5py
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


def config_hash(*parts):
    """Stable across processes and Python versions.

    NOT `hash()`: Python randomises str hashing per process unless PYTHONHASHSEED is
    set, so a config_hash over anything containing a string identified nothing — it
    differed on every run, which defeats the point of recording it in PROVENANCE.
    """
    return zlib.crc32(repr(parts).encode()) & 0xFFFFFFFF

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, EMB = f"{ROOT}/bench_data", f"{ROOT}/embeddings"
MORPH = f"{ROOT}/instrumentation/morphology_v2"
META = f"{ROOT}/results/tailored/integrity/sample_metadata.csv"
OUT = f"{ROOT}/results/round2/R4_probes"

# Carried over from round 1 unchanged, so that accuracies are comparable to it.
SEED, LATENT, GRID, TEST_FRAC, SUBSAMPLE = 1, 256, 6, 0.30, 800
# The plan specifies "nuclear count, mean nuclear area, the five CellViT class fractions".
# morphology_v2 carries BOTH a generic `area_mean` over all nuclei and a neoplastic-only
# `neo_area_mean`. "Mean nuclear area" is the generic one, so `area_mean` is what the plan
# asks for; an earlier draft of this script used `neo_area_mean`, which is a different
# covariate and would have silently narrowed the adjustment to neoplastic nuclei.
# `neo_area_mean` is appended as an EXTRA covariate rather than a substitute, so the
# adjustment is at least as strong as specified, and both are named in the output.
MORPH_COVS = ["n_nuclei", "area_mean", "frac_connective", "frac_dead",
              "frac_epithelial", "frac_inflammatory", "frac_neoplastic",
              "neo_area_mean"]
MORPH_COVS_PLAN = MORPH_COVS[:7]   # exactly the plan's list, reported alongside
PROBE3_TASKS = ["IDC", "PAAD", "LUNG", "SKCM"]


def load(task, enc):
    """X (n,d) embeddings, slide_of (n,), xy (n,2) pixel coords, bc (n,) barcodes."""
    Xs, lab, xy, bcs = [], [], [], []
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        s = os.path.basename(p)[:-5]
        f5 = f"{EMB}/{task}/{enc}/{s}.h5"
        if not os.path.isfile(f5):
            return (None,) * 4
        with h5py.File(f5, "r") as f:
            Xs.append(np.asarray(f["embeddings"][:], dtype=np.float32))
            xy.append(np.asarray(f["coords"][:], dtype=np.float64))
            bcs.append(np.asarray(f["barcodes"][:]).astype(str).ravel()
                       if "barcodes" in f else np.array([f"{s}_{i}" for i in range(len(Xs[-1]))]))
        lab += [s] * len(Xs[-1])
    return np.vstack(Xs), np.array(lab), np.vstack(xy), np.concatenate(bcs)


def subsample(slide_of, per_slide, rng):
    """Equal spots per slide, so balanced accuracy is not driven by slide size."""
    keep = np.zeros(len(slide_of), bool)
    for s in np.unique(slide_of):
        idx = np.flatnonzero(slide_of == s)
        take = idx if len(idx) <= per_slide else rng.choice(idx, per_slide, replace=False)
        keep[take] = True
    return keep


def block_split(slide_of, xy, rng, grid=GRID, frac=TEST_FRAC):
    """Whole spatial blocks per slide to test, targeting `frac` of that slide's spots."""
    test = np.zeros(len(xy), bool)
    for s in np.unique(slide_of):
        m = slide_of == s
        c = xy[m]
        lo, hi = c.min(0), c.max(0)
        span = np.where(hi - lo == 0, 1.0, hi - lo)
        bi = np.clip(((c - lo) / span * grid).astype(int), 0, grid - 1)
        key = bi[:, 0] * grid + bi[:, 1]
        blocks, counts = np.unique(key, return_counts=True)
        order = rng.permutation(len(blocks))
        target, chosen, acc = frac * m.sum(), [], 0
        for j in order:
            if acc >= target:
                break
            chosen.append(blocks[j])
            acc += counts[j]
        idx = np.flatnonzero(m)
        test[idx[np.isin(key, chosen)]] = True
    return test


def nn_dist(slide_of, xy, test):
    d = []
    for s in np.unique(slide_of):
        m = slide_of == s
        tr, te = m & ~test, m & test
        if tr.sum() and te.sum():
            d.append(cKDTree(xy[tr]).query(xy[te], k=1)[0])
    return float(np.median(np.concatenate(d))) if d else np.nan


def probe_pred(X, y, tr, te, resid_cov=None):
    """As probe(), but returns (balanced_accuracy, y_true, y_pred) for the confusion matrix."""
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=min(LATENT, X.shape[1]), random_state=SEED))])
    Z, Zt = pipe.fit_transform(X[tr]), pipe.transform(X[te])
    if resid_cov is not None:
        ok = np.isfinite(resid_cov).all(axis=1)
        lr = LinearRegression().fit(resid_cov[tr][ok[tr]], Z[ok[tr]])
        Z = Z - lr.predict(np.nan_to_num(resid_cov[tr], nan=0.0))
        Zt = Zt - lr.predict(np.nan_to_num(resid_cov[te], nan=0.0))
    clf = LogisticRegression(max_iter=2000).fit(Z, y[tr])
    pred = clf.predict(Zt)
    return float(balanced_accuracy_score(y[te], pred)), y[te], pred


def probe(X, y, tr, te, resid_cov=None):
    """PCA-256 fit on train, logistic regression, balanced accuracy.

    `resid_cov` (n,k), when given, is regressed out of the PCA scores with the regression
    fit on TRAINING rows only; the probe then runs on the residuals. Fitting the adjustment
    on training rows only is what keeps the comparison honest -- an adjustment fit on all
    rows could itself remove or inject slide information.
    """
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=min(LATENT, X.shape[1]), random_state=SEED))])
    Z, Zt = pipe.fit_transform(X[tr]), pipe.transform(X[te])
    if resid_cov is not None:
        ok = np.isfinite(resid_cov).all(axis=1)
        if not ok[tr].any():
            return np.nan
        lr = LinearRegression().fit(resid_cov[tr][ok[tr]], Z[ok[tr]])
        Z = Z - lr.predict(np.nan_to_num(resid_cov[tr], nan=0.0))
        Zt = Zt - lr.predict(np.nan_to_num(resid_cov[te], nan=0.0))
    clf = LogisticRegression(max_iter=2000).fit(Z, y[tr])
    return float(balanced_accuracy_score(y[te], clf.predict(Zt)))


# ---------------------------------------------------------------- patient / resolution map
meta = pd.read_csv(META)
SID = "sample_id" if "sample_id" in meta.columns else meta.columns[0]
PAT = next(c for c in meta.columns if "patient" in c.lower())
PX = "pixel_size_um" if "pixel_size_um" in meta.columns else "pixel_size_um_estimated"
TASKC = next(c for c in meta.columns if c.lower() == "task")
# Keyed by (task, sample_id), NOT sample_id: the benchmark's patient labels are only unique
# within a task. Five non-PRAD samples (INT23, TENX95, TENX115, TENX116, TENX118) also carry
# "patient 2", so a sample_id-keyed map would silently mix tasks in any probe that selects
# slides by patient label.
patient_of = {(t, str(s)): str(p).strip() for t, s, p
              in zip(meta[TASKC], meta[SID], meta[PAT])}
px_of = {(t, str(s)): float(v) for t, s, v in zip(meta[TASKC], meta[SID], meta[PX])}
UNCC = next((c for c in meta.columns if c.lower() == "resolution_uncertain"), None)
unc_of = ({(t, str(s)): bool(v) for t, s, v in zip(meta[TASKC], meta[SID], meta[UNCC])}
          if UNCC else {})


def pat_norm(task, s):
    return patient_of.get((task, s), "?").lower().replace(" ", "")

os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------- R5 decisions, directive 2.7
# Slide-identity confusion matrices for the probe-3 tasks. The directive asks specifically
# whether TENX95 and TENX99 confuse with EACH OTHER more than either does with the NCBI
# slides: if they do, that is embedding-side corroboration of the same-donor finding, which
# R5 established from 10x's own dataset metadata rather than from the data.
#
# Same probe as R4's: PCA-256 fit on training rows, logistic regression, spatial block split.
# No morphology adjustment here - the question is what the raw embedding carries.
# The encoder comes from argv. round2_r4_probes.py sets it in a `for enc in sys.argv[1:]`
# loop that sits below the point this file was lifted from, so it has to be set here.
enc = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

CONF_TASKS = ["IDC", "PAAD", "LUNG", "SKCM"]
rows, mats = [], {}
for task in CONF_TASKS:
    hs = sorted(glob.glob(f"{EMB}/{task}/{enc}/*.h5"))
    if not hs:
        print(f"[skip] {task}: no embeddings for {enc}", flush=True)
        continue
    X, slide_of, xys = [], [], []
    for hp in hs:
        sid = os.path.basename(hp)[:-3]
        with h5py.File(hp, "r") as f:
            X.append(np.asarray(f["embeddings"][:], dtype=np.float32))
            xys.append(np.asarray(f["coords"][:], dtype=np.float64))
            slide_of += [sid] * len(f["embeddings"])
    X = np.vstack(X); xy = np.vstack(xys); slide_of = np.asarray(slide_of)
    if len(set(slide_of)) < 2:
        continue
    te = block_split(slide_of, xy, np.random.default_rng(SEED))
    acc, y_true, y_pred = probe_pred(X, slide_of, ~te, te)
    labels = sorted(set(slide_of))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cmn = cm / cm.sum(axis=1, keepdims=True)
    mats[task] = pd.DataFrame(cm, index=labels, columns=labels)
    mats[task].to_csv(f"{OUT}/slide_confusion__{task}__{enc}.csv")

    # off-diagonal mass, split by whether the confused pair is the same donor
    off = cm.sum() - np.trace(cm)
    rec = dict(encoder=enc, task=task, n_slides=len(labels), chance=1.0 / len(labels),
               balanced_acc=acc, off_diagonal_mass=int(off),
               slides=";".join(labels))
    if task == "IDC" and {"TENX95", "TENX99"} <= set(labels):
        i95, i99 = labels.index("TENX95"), labels.index("TENX99")
        pair = cm[i95, i99] + cm[i99, i95]
        # each TENX slide's off-diagonal mass, and how much of it lands on its partner
        for a, b, nm in ((i95, i99, "TENX95"), (i99, i95, "TENX99")):
            row_off = cm[a].sum() - cm[a, a]
            rec[f"{nm}_off_diag"] = int(row_off)
            rec[f"{nm}_onto_partner"] = int(cm[a, b])
            rec[f"{nm}_frac_onto_partner"] = float(cm[a, b] / row_off) if row_off else np.nan
            # chance share if the slide's errors were spread over the other 3 slides
            rec[f"{nm}_chance_share"] = 1.0 / (len(labels) - 1)
        rec["tenx_pair_mass"] = int(pair)
        rec["tenx_pair_frac_of_off_diag"] = float(pair / off) if off else np.nan
    rows.append(rec)
    print(f"[{task}] {len(labels)} slides, balanced acc {acc:.4f} (chance {1/len(labels):.4f}), "
          f"off-diagonal mass {int(off)}", flush=True)
    if task == "IDC":
        print("  IDC row-normalised confusion:")
        print(pd.DataFrame(cmn, index=labels, columns=labels).round(4).to_string())

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/slide_confusion_summary__{enc}.csv", index=False)
print(f"\nwrote {OUT}/slide_confusion_summary__{enc}.csv")
print(d.to_string(index=False))
