#!/usr/bin/env python
"""Round 2, stage R4: probes v2.

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
rows = []

for enc in sys.argv[1:]:
    t0 = time.time()
    print(f"\n################ {enc} ################", flush=True)

    # ------------------------------------------------------------------ Probes 1 and 2: PRAD
    X, slide_of, xy, bc = load("PRAD", enc)
    if X is None:
        print(f"[skip] PRAD/{enc}: no embeddings", flush=True)
    else:
        # --- Probe 1: slide id among patient 2's slides
        p2 = sorted({s for s in set(slide_of) if pat_norm("PRAD", s) == "patient2"})
        # The plan specifies 15 slides at 0.341-0.349 um/px. Asserted rather than assumed,
        # because the whole interpretation rule rests on resolution being near-constant.
        assert len(p2) == 15, f"probe 1 expected 15 PRAD patient-2 slides, got {len(p2)}: {p2}"
        _pv = [px_of[("PRAD", s)] for s in p2]
        assert max(_pv) / min(_pv) < 1.05, f"probe 1 resolution not near-constant: {_pv}"
        if len(p2) < 2:
            print(f"[warn] probe 1: patient 2 has {len(p2)} slides in PRAD; skipped", flush=True)
        else:
            m = np.isin(slide_of, p2)
            rng = np.random.default_rng(SEED)
            keep = np.zeros(len(slide_of), bool)
            sel = subsample(slide_of[m], SUBSAMPLE, rng)
            keep[np.flatnonzero(m)[sel]] = True
            Xs, ys, xys = X[keep], slide_of[keep], xy[keep]
            pxs = sorted({round(px_of[("PRAD", s)], 4) for s in p2})

            itr, ite = train_test_split(np.arange(len(Xs)), test_size=TEST_FRAC,
                                        random_state=SEED, stratify=ys)
            te_r = np.zeros(len(Xs), bool); te_r[ite] = True
            acc_r = probe(Xs, ys, ~te_r, te_r)
            te_b = block_split(ys, xys, np.random.default_rng(SEED))
            acc_b, y_true, y_pred = probe_pred(Xs, ys, ~te_b, te_b)

            # Confusion matrix, and how much of the confusion mass is WITHIN a scan
            # sub-cluster versus BETWEEN them (decision 2.1). Sub-cluster membership is
            # derived from the pixel sizes themselves, not from the slide-id ranges, so it
            # cannot silently disagree with the metadata.
            labs = sorted(str(v) for v in set(ys))
            CM = confusion_matrix(y_true, y_pred, labels=labs)
            pxv = np.array([px_of[("PRAD", s)] for s in labs])
            cut = (pxv.min() + pxv.max()) / 2.0
            sub = np.where(pxv < cut, "A", "B")
            off = CM.copy()
            np.fill_diagonal(off, 0)
            same = float(off[np.equal.outer(sub, sub)].sum())
            diff = float(off[~np.equal.outer(sub, sub)].sum())
            # If the two sub-clusters were interchangeable, off-diagonal mass would split in
            # proportion to the number of available (i != j) cells in each group.
            n_same_cells = int(np.equal.outer(sub, sub).sum() - len(labs))
            n_diff_cells = int((~np.equal.outer(sub, sub)).sum())
            exp_same = n_same_cells / (n_same_cells + n_diff_cells)
            pd.DataFrame(CM, index=labs, columns=labs).to_csv(
                f"{OUT}/probe1_confusion__{enc}.csv")
            print(f"  probe1 confusion {enc}: off-diagonal mass within sub-cluster "
                  f"{same/(same+diff):.3f} (chance {exp_same:.3f}); "
                  f"sub-cluster A={sorted(np.array(labs)[sub=='A'])[:3]}... "
                  f"B={sorted(np.array(labs)[sub=='B'])[:3]}...", flush=True)

            # --- Probe 1b: the scan sub-cluster itself, leave-one-slide-out, chance 0.5
            ysub = np.array([("A" if px_of[("PRAD", s)] < cut else "B") for s in ys])
            # Held-out spots all share one sub-cluster label, so per-fold balanced accuracy is
            # degenerate (single class in y_true) and sklearn warns. Pool the leave-one-slide-out
            # predictions across folds and score ONCE on the pooled pair, which contains both
            # classes, and separately record the per-slide majority vote -- the quantity the
            # decision-2.1 rule is actually about ("is this slide placed in the right session").
            pool_true, pool_pred, maj = [], [], []
            for s in p2:
                te = ys == s
                tr = ~te
                if te.sum() < 50 or len(set(ysub[tr])) < 2:
                    continue
                _, yt, yp = probe_pred(Xs, ysub, tr, te)
                pool_true.append(yt); pool_pred.append(yp)
                vals, cnts = np.unique(yp, return_counts=True)
                maj.append(bool(vals[cnts.argmax()] == ysub[te][0]))
            accs_sc = ([balanced_accuracy_score(np.concatenate(pool_true),
                                                np.concatenate(pool_pred))]
                       if pool_true else [])
            rows.append(dict(
                probe="probe1b_scan_subcluster", encoder=enc, task="PRAD",
                unit="PRAD patient 2", n_classes=2, chance=0.5, n_folds=len(maj),
                acc_blocked=float(accs_sc[0]) if accs_sc else np.nan,
                acc_sd=np.nan,
                n_slides_majority_correct=int(sum(maj)), n_slides_scored=len(maj),
                majority_vote_acc=float(np.mean(maj)) if maj else np.nan,
                px_values=f"cut at {cut:.4f}",
                all_resolution_uncertain=True,
                rule="decision 2.1: high accuracy means part of the slide signature is a "
                     "scan-session effect rather than per-slide"))
            print(f"  probe1b {enc}: scan sub-cluster, {len(maj)} LOSO folds, chance 0.500, "
                  f"pooled balanced acc {accs_sc[0] if accs_sc else float('nan'):.4f}, "
                  f"majority vote {sum(maj)}/{len(maj)} slides correct", flush=True)
            rows.append(dict(
                probe="probe1_slide_within_patient", encoder=enc, task="PRAD",
                unit="PRAD patient 2", n_classes=len(p2), chance=1.0 / len(p2),
                n_spots=int(keep.sum()), spots_per_slide=SUBSAMPLE,
                acc_random_split=acc_r, acc_blocked=acc_b, acc_drop=acc_r - acc_b,
                confusion_within_subcluster_frac=same / (same + diff) if (same + diff) else np.nan,
                confusion_within_subcluster_chance=exp_same,
                confusion_off_diagonal_mass=int(same + diff),
                subcluster_A=";".join(sorted(np.array(labs)[sub == "A"])),
                subcluster_B=";".join(sorted(np.array(labs)[sub == "B"])),
                all_resolution_uncertain=True,
                nn_dist_random=nn_dist(ys, xys, te_r), nn_dist_blocked=nn_dist(ys, xys, te_b),
                px_values=";".join(f"{v}" for v in pxs),
                rule="blocked>0.8 => technical origin; near chance => round 1's 0.98 was biology+resolution",
                verdict=("technical" if acc_b > 0.8 else
                         "near chance" if acc_b < 2.0 / len(p2) else "intermediate")))
            print(f"  probe1 {enc}: {len(p2)} slides, chance {1/len(p2):.4f}, "
                  f"random {acc_r:.4f}, blocked {acc_b:.4f} -> {rows[-1]['verdict']}", flush=True)

        # --- Probe 2: nominal resolution group among patient 1's slides
        p1 = sorted({s for s in set(slide_of) if pat_norm("PRAD", s) == "patient1"})
        grp = {s: round(px_of[("PRAD", s)], 2) for s in p1 if ("PRAD", s) in px_of}
        assert sorted(pd.Series(grp).value_counts().to_dict().items()) == \
               [(0.17, 1), (0.57, 5), (0.69, 2)], f"probe 2 grouping changed: {grp}"
        sizes = pd.Series(grp).value_counts().to_dict()
        multi = {g for g, n_ in sizes.items() if n_ >= 2}
        print(f"  probe2 groups: {sizes}; evaluable classes {sorted(multi)}", flush=True)

        # Decision 1.1: nominal pixel-size groups, NOT R0's bins; the single 0.17 slide is
        # excluded from BOTH training and evaluation, since it cannot be held out with its
        # class present and adds only an untested class if left in training. Two classes,
        # leave-one-slide-out over the 7 remaining slides, chance 0.5. The binned variant is
        # dropped entirely rather than reported, per the same decision.
        for variant, classes in (("probe2_2class", multi),):
            ev = [s for s in p1 if grp.get(s) in multi]        # the 7 evaluable slides
            keepmask = np.isin(slide_of, ev)                   # training pool is those 7 only
            # Scored the same way as probe 1b, and for the same reason. Each held-out slide
            # carries ONE resolution class, so a per-fold balanced accuracy is recall on that
            # class and a classifier that always predicts the majority class scores
            # n_majority/n_slides -- here 5/7 = 0.714 -- with no resolution signal whatsoever.
            # The first run of this probe returned 0.712, 0.683, 0.669 against exactly that
            # baseline, which is uninterpretable. So: pool the leave-one-slide-out predictions
            # and score once on the pooled pair (both classes present), record the per-slide
            # majority vote, and carry the trivial baseline in the output so no reader has to
            # reconstruct it.
            accs, held = [], []
            pool_t, pool_p, maj2 = [], [], []
            for s in ev:
                te = keepmask & (slide_of == s)
                tr = keepmask & (slide_of != s)
                if te.sum() < 50 or tr.sum() < 100:
                    continue
                rng = np.random.default_rng(SEED)
                sub = np.zeros(len(slide_of), bool)
                for mm in (tr, te):
                    idx = np.flatnonzero(mm)
                    sl = subsample(slide_of[mm], SUBSAMPLE, rng)
                    sub[idx[sl]] = True
                # grp is keyed by patient-1 slides only, while slide_of spans the whole task,
                # so a direct lookup KeyErrors on patient-2 slides. Only entries under `sub`
                # (a subset of keepmask, itself a subset of the 7 evaluable slides) are ever
                # read, and the assert makes that explicit rather than implicit.
                yy = np.array([grp.get(x, "?") for x in slide_of])
                assert not (yy[sub] == "?").any(), "unlabelled slide inside the probe-2 sample"
                a, yt2, yp2 = probe_pred(X[sub], yy[sub], (tr & sub)[sub], (te & sub)[sub])
                accs.append(a); held.append(s)
                pool_t.append(yt2); pool_p.append(yp2)
                v2, c2 = np.unique(yp2, return_counts=True)
                maj2.append(bool(str(v2[c2.argmax()]) == str(yy[te][0])))
            if accs:
                rows.append(dict(
                    probe=variant, encoder=enc, task="PRAD", unit="PRAD patient 1",
                    n_classes=len(multi), chance=1.0 / len(multi),
                    n_folds=len(accs),
                    acc_blocked=float(balanced_accuracy_score(np.concatenate(pool_t),
                                                              np.concatenate(pool_p))),
                    acc_pooled_balanced=float(balanced_accuracy_score(
                        np.concatenate(pool_t), np.concatenate(pool_p))),
                    acc_mean_per_slide_recall=float(np.mean(accs)),
                    acc_sd=float(np.std(accs, ddof=1)) if len(accs) > 1 else np.nan,
                    majority_class_baseline=float(max(sizes[g] for g in multi) / len(ev)),
                    n_slides_majority_correct=int(sum(maj2)), n_slides_scored=len(maj2),
                    majority_vote_acc=float(np.mean(maj2)) if maj2 else np.nan,
                    held_out_slides=";".join(held),
                    px_values=";".join(f"{g}:{n_}" for g, n_ in sorted(sizes.items())),
                    excluded_slides=";".join(sorted(s for s in p1 if grp.get(s) not in multi)),
                    all_resolution_uncertain=True,
                    rule="high accuracy => resolution is decodable independently of patient",
                    note=("decision 1.1: nominal pixel-size groups, not R0's bins; the single "
                          "0.17 slide is excluded from BOTH training and evaluation; 2 classes "
                          "over 7 slides, chance 0.5. PRAD carries no embedded pixel size, so "
                          "these labels rest on the spot-spacing estimate alone - for Visium "
                          "the more reliable of the two sources, being derived from the known "
                          "100um pitch, so a caveat and not a blocker.")))
                print(f"  {variant} {enc}: {len(accs)} LOSO folds, chance {1/len(multi):.3f}, "
                      f"acc {np.mean(accs):.4f}", flush=True)
        del X

    # ------------------------------------------------------- Probe 3: composition adjustment
    # Decision 2.1 adds PRAD patient 2, so Probe 1 has an adjusted counterpart. PRAD is
    # handled as a special case because it is restricted to one patient's 15 slides rather
    # than using every slide in the task.
    for task in PROBE3_TASKS + ["PRAD"]:
        X, slide_of, xy, bc = load(task, enc)
        if X is None:
            print(f"[skip] {task}/{enc}: no embeddings", flush=True)
            continue
        mp = f"{MORPH}/{task}_morph.parquet"
        if not os.path.isfile(mp):
            print(f"[skip] probe3 {task}: no morphology parquet", flush=True)
            del X
            continue
        if task == "PRAD":
            keep_slides = sorted({s for s in set(slide_of) if pat_norm("PRAD", s) == "patient2"})
            m_ = np.isin(slide_of, keep_slides)
            X, slide_of, xy, bc = X[m_], slide_of[m_], xy[m_], bc[m_]
        M = pd.read_parquet(mp)
        M["key"] = M.sample_id.astype(str) + "|" + M.barcode.astype(str)
        key = pd.Series([f"{s}|{b}" for s, b in zip(slide_of, bc)])
        cov = (M.set_index("key").reindex(key)[MORPH_COVS]
                .astype(float).to_numpy())
        matched = np.isfinite(cov).all(axis=1)
        n_slides = len(set(slide_of))
        rng = np.random.default_rng(SEED)
        keep = subsample(slide_of, SUBSAMPLE, rng) & matched
        if keep.sum() < 200 or len(set(slide_of[keep])) < 2:
            print(f"[skip] probe3 {task}: only {keep.sum()} spots matched morphology "
                  f"({matched.mean():.1%} of rows)", flush=True)
            del X
            continue
        Xs, ys, xys, cs = X[keep], slide_of[keep], xy[keep], cov[keep]
        te_b = block_split(ys, xys, np.random.default_rng(SEED))
        a_before = probe(Xs, ys, ~te_b, te_b)
        a_after = probe(Xs, ys, ~te_b, te_b, resid_cov=cs)
        # The plan-exact covariate set as well, so the reported drop cannot be an artefact
        # of the one covariate this script adds beyond the plan.
        idx_plan = [MORPH_COVS.index(c) for c in MORPH_COVS_PLAN]
        a_after_plan = probe(Xs, ys, ~te_b, te_b, resid_cov=cs[:, idx_plan])
        rows.append(dict(
            probe="probe3_composition_adjusted", encoder=enc, task=task,
            unit=("PRAD patient 2 (adjusted counterpart to probe 1)" if task == "PRAD"
                  else f"{task}, single-slide patients"),
            all_resolution_uncertain=bool(task == "PRAD"),
            n_classes=len(set(ys)),
            chance=1.0 / len(set(ys)), n_spots=int(keep.sum()),
            morph_match_frac=float(matched.mean()),
            acc_blocked=a_before, acc_blocked_adjusted=a_after,
            acc_drop=a_before - a_after,
            acc_blocked_adjusted_planset=a_after_plan,
            acc_drop_planset=a_before - a_after_plan,
            n_slides_resolution_uncertain=int(sum(unc_of.get((task, s), False)
                                                  for s in sorted(set(ys)))),
            n_slides_total=len(set(ys)),
            covariates=";".join(MORPH_COVS),
            covariates_planset=";".join(MORPH_COVS_PLAN),
            rule="large drop => composition explains separability; no drop => it does not",
            verdict=("composition explains most" if a_before - a_after > 0.15 else
                     "composition explains little" if a_before - a_after < 0.05 else
                     "partial")))
        print(f"  probe3 {enc} {task}: {len(set(ys))} slides, before {a_before:.4f}, "
              f"after {a_after:.4f} (drop {a_before-a_after:+.4f}), plan-set after "
              f"{a_after_plan:.4f} (drop {a_before-a_after_plan:+.4f}) -> {rows[-1]['verdict']}",
              flush=True)
        del X

    print(f"[{enc}] done in {time.time()-t0:.0f}s", flush=True)

d = pd.DataFrame(rows)
tag = sys.argv[1]
d.to_csv(f"{OUT}/probes_v2__{tag}.csv", index=False)
print(f"\nwrote {OUT}/probes_v2__{tag}.csv ({len(d)} rows)")
for pn, g in d.groupby("probe"):
    cols = [c for c in ("task", "encoder", "chance", "acc_blocked", "acc_random_split",
                        "acc_blocked_adjusted", "acc_drop", "verdict") if c in g]
    print(f"\n=== {pn} ===")
    print(g[cols].to_string(index=False))

with open(f"{OUT}/PROVENANCE__{tag}.txt", "w") as f:
    f.write(
        f"Round 2, stage R4 - probes v2, encoders {' '.join(sys.argv[1:])}\n"
        f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID','NA')}\n"
        f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION','NA')}\n"
        f"node            : {os.environ.get('SLURMD_NODENAME','NA')}\n"
        f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
        f"repo_commit     : {os.popen(f'git -C {ROOT} rev-parse HEAD').read().strip()}\n"
        f"script          : code/scripts/round2_r4_probes.py\n"
        f"command_line    : {' '.join(sys.argv)}\n"
        f"seed/latent/grid/test_frac/subsample : {SEED}/{LATENT}/{GRID}/{TEST_FRAC}/{SUBSAMPLE}\n"
        f"morph_covariates: {MORPH_COVS}\n"
        f"morph_covariates_planset : {MORPH_COVS_PLAN}\n"
        f"probe3_tasks    : {PROBE3_TASKS + ['PRAD (patient 2, decision 2.1)']}\n"
        f"probe2_design   : decision 1.1 - nominal groups, 0.17 slide excluded from "
        f"training AND evaluation, 2 classes over 7 slides, chance 0.5, binned variant dropped\n"
        f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED', 'unset')}\n"
        f"config_hash     : {config_hash(SEED, LATENT, GRID, TEST_FRAC, SUBSAMPLE, tuple(MORPH_COVS)):08x}\n"
        "plan            : round2_execution_plan.md stage R4 / plan phase R4\n"
        "decisions       : round2_R3_decisions.md sections 1.1 and 2.1\n")
