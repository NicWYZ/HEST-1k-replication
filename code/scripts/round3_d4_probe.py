#!/usr/bin/env python
"""Round 3, stage D4.3b: the R4-style population probe on the kidney set, with and without the
morphology adjustment, and the CellViT morphology build the adjustment needs.

Stage: D4 (round3_execution_plan.md section 13.7.3, transcribing docs/decisions/
round3_A3_decisions.md section 7.3): "The R4-style probe runs with population as the target and
the same difference list, and with the morphology adjustment, so the fraction of the signature
that composition explains is measured on the hardest contrast too."

THE TARGET IS `population`, NEVER A LABORATORY TERM (section 13.2 item 4). The two classes are
cordeliers_ccRCC (24 samples) and indiana_nontumour (30 samples), and the difference list
between them is in results/round3/D4_expansion/task_defs/KIDNEY_POP54.json under
expansion.difference_list_for_population_out: tissue state, anatomical region, disease,
preservation in part, laboratory, instrument, objective, pixel size, and the pixel-size
provenance flag. A high balanced accuracy is a statement about all nine at once.

MORPHOLOGY (section 13.7.5: "no morphology build beyond the 7.3 probe's inputs"). Per patched
spot, over the SAME pixels the encoder saw, using round 2's per-sample geometry calibration from
code/scripts/morphology_features.py: the patch half-width in WSI pixels is 112 * `factor`, where
`factor` is an attribute of the patches/<sid>.h5 'img' dataset -- the value the extraction itself
used, so it cannot drift from the pixels the encoder embedded. Where the attribute is absent the
fallback is 112 / pixel_size_um_estimated, which that script verified agrees with 224 * factor to
0.000 px on 72 of 72 benchmark samples; which source was used is recorded per sample. Nuclei are
assigned by a KD-tree ball query at the circumscribing radius followed by an exact box filter, so
a nucleus in the overlap of two patches counts toward both, as round 2's v2 build does.
The CellViT parquets are the ones D1 downloaded (hest_ext/<set>/cellvit_seg/), so nothing is
downloaded here; the revision is D1's, 7e8d5a0b0aace41d8c8ec0f6ecea80e4ad2a61ec.

COVARIATES, exactly round 2 R4's eight: n_nuclei, area_mean, the five CellViT class fractions,
and neo_area_mean. CellViT's `dead` class is absent from some samples' segmentations; its
fraction is then 0 by construction and that is recorded rather than dropped.

PROTOCOLS. Two, because `population` is a SLIDE-level label and R4's protocol was built for a
within-slide target:
  block       R4's own protocol, kept so the number is comparable to round 2's probes: whole
              6x6 spatial blocks per slide held out, about 30% of each slide's spots, every
              slide present in training. This is an UPPER BOUND for a slide-level label -- the
              classifier can memorise each slide.
  slide_out   leave-one-slide-out grouped CV: the held-out slide contributes no training spot,
              so the probe has to generalise across slides within a population. This is the
              honest protocol for a slide-level target and is the primary row.
Each protocol runs with and without the morphology adjustment. The adjustment regresses the
PCA-256 scores on the eight covariates with the regression FIT ON TRAINING ROWS ONLY and reruns
the probe on the residuals, which is round 2 R4's probe 3 verbatim.
RULE, fixed before the run: a large drop from unadjusted to adjusted means tissue composition
explains the population signature; no drop means composition does not capture it.

Outputs under results/round3/D4_expansion/:
  d4_population_probe__<enc>.csv        one row per (protocol, adjustment)
  d4_population_probe_folds__<enc>.csv  per held-out slide, slide_out protocol
  d4_morphology_summary.csv             per sample, the build's own accounting
  instrumentation/morphology_v2_ext/KIDNEY_POP54_morph.parquet  (gitignored, stays on Longleaf)
  PROVENANCE__d4_population_probe__<enc>.txt

Usage:
  round3_d4_probe.py --stage morph
  round3_d4_probe.py --stage probe --encoder hoptimus0
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

import anndata as ad
import geopandas as gpd
import h5py
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "round3_a0_harness", os.path.join(_HERE, "round3_a0_harness.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)

ROOT = H.ROOT
OUTDIR = "results/round3/D4_expansion"
TD = f"{ROOT}/{OUTDIR}/task_defs/KIDNEY_POP54.json"
MORPH_DIR = f"{ROOT}/instrumentation/morphology_v2_ext"
MORPH_PARQUET = f"{MORPH_DIR}/KIDNEY_POP54_morph.parquet"
HEST_REVISION = "7e8d5a0b0aace41d8c8ec0f6ecea80e4ad2a61ec"

# Round 2 R4's constants, carried unchanged so the accuracies are comparable to it.
SEED, LATENT, GRID, TEST_FRAC, SUBSAMPLE = 1, 256, 6, 0.30, 800
MORPH_COVS = ["n_nuclei", "area_mean", "frac_connective", "frac_dead", "frac_epithelial",
              "frac_inflammatory", "frac_neoplastic", "neo_area_mean"]
EXPECTED_CLASSES = {"neoplastic", "inflammatory", "connective", "epithelial", "dead"}
CHUNK = 20000


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


# ------------------------------- round 2 R4's helpers, copied verbatim with attribution
def subsample(slide_of, per_slide, rng):
    """Equal spots per slide, so balanced accuracy is not driven by slide size.
    code/scripts/round2_r4_probes.py::subsample."""
    keep = np.zeros(len(slide_of), bool)
    for s in np.unique(slide_of):
        idx = np.flatnonzero(slide_of == s)
        take = idx if len(idx) <= per_slide else rng.choice(idx, per_slide, replace=False)
        keep[take] = True
    return keep


def block_split(slide_of, xy, rng, grid=GRID, frac=TEST_FRAC):
    """Whole spatial blocks per slide to test, targeting `frac` of that slide's spots.
    code/scripts/round2_r4_probes.py::block_split."""
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


def probe_pred(X, y, tr, te, resid_cov=None):
    """PCA-256 fit on train, logistic regression, balanced accuracy, plus the predictions for
    the confusion matrix. code/scripts/round2_r4_probes.py::probe_pred, unchanged: `resid_cov`
    is regressed out of the PCA scores with the regression FIT ON TRAINING ROWS ONLY."""
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=min(LATENT, X.shape[1]), random_state=SEED))])
    Z, Zt = pipe.fit_transform(X[tr]), pipe.transform(X[te])
    if resid_cov is not None:
        ok = np.isfinite(resid_cov).all(axis=1)
        if not ok[tr].any():
            return np.nan, None, None
        lr = LinearRegression().fit(resid_cov[tr][ok[tr]], Z[ok[tr]])
        Z = Z - lr.predict(np.nan_to_num(resid_cov[tr], nan=0.0))
        Zt = Zt - lr.predict(np.nan_to_num(resid_cov[te], nan=0.0))
    clf = LogisticRegression(max_iter=2000).fit(Z, y[tr])
    pred = clf.predict(Zt)
    return float(balanced_accuracy_score(y[te], pred)), y[te], pred


# ------------------------------------------------------------------------ morphology build
def patch_geometry(td, sid, px_est):
    p = f"{ROOT}/{td['paths']['patches'].format(sample_id=sid)}"
    with h5py.File(p, "r") as f:
        at = dict(f["img"].attrs)
    keys = {str(k): str(v) for k, v in at.items()}
    if "factor" in at:
        return 112.0 * float(np.asarray(at["factor"]).ravel()[0]), "patch_attr_factor", keys
    if "patch_size_level0" in at:
        return float(np.asarray(at["patch_size_level0"]).ravel()[0]) / 2.0, \
            "patch_attr_patch_size_level0", keys
    return 112.0 / float(px_est), "112_over_pixel_size_um_estimated", keys


def build_morphology(td):
    os.makedirs(MORPH_DIR, exist_ok=True)
    setname = td["expansion"]["set_name"]
    frames, summary = [], []
    for s in td["samples"]:
        sid = s["sample_id"]
        half, src, attrs = patch_geometry(td, sid, s["pixel_size_um"])
        fp = f"{ROOT}/hest_ext/{setname}/cellvit_seg/{sid}_cellvit_seg.parquet"
        assert os.path.exists(fp), f"{sid}: no CellViT parquet at {fp}"
        nuc = gpd.read_parquet(fp)
        assert nuc.geometry.notna().all(), f"{sid}: null geometry"
        cls = nuc["class"].astype(str).str.lower().to_numpy()
        unknown = set(np.unique(cls)) - EXPECTED_CLASSES
        assert not unknown, f"{sid}: unexpected CellViT classes {unknown}"
        cent = nuc.geometry.centroid
        cx, cy = cent.x.to_numpy(), cent.y.to_numpy()
        area = nuc.geometry.area.to_numpy()
        assert (area > 0).all(), f"{sid}: non-positive nuclear area"

        ep = f"{ROOT}/{td['paths']['embeddings'].format(encoder='resnet50', sample_id=sid)}"
        with h5py.File(ep, "r") as f:
            k = "barcodes" if "barcodes" in f else "barcode"
            b = np.asarray(f[k][:]).reshape(-1)
            bc = np.array([x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x)
                           for x in b], dtype=object)
            xy = np.asarray(f["coords"][:], dtype=np.float64)
        tree = cKDTree(np.c_[cx, cy])
        recs = []
        for s0 in range(0, len(xy), CHUNK):
            block = xy[s0:s0 + CHUNK]
            balls = tree.query_ball_point(block, r=half * np.sqrt(2.0), workers=-1)
            for li, idxs in enumerate(balls):
                if not idxs:
                    continue
                ii = np.asarray(idxs)
                inbox = ((np.abs(cx[ii] - block[li, 0]) <= half)
                         & (np.abs(cy[ii] - block[li, 1]) <= half))
                ii = ii[inbox]
                if ii.size == 0:
                    continue
                a_, c_ = area[ii], cls[ii]
                rec = dict(spot=s0 + li, n_nuclei=int(ii.size), area_mean=float(a_.mean()),
                           area_median=float(np.median(a_)))
                for k_ in sorted(EXPECTED_CLASSES):
                    rec[f"frac_{k_}"] = float((c_ == k_).mean())
                neo = a_[c_ == "neoplastic"]
                rec["n_neoplastic"] = int(neo.size)
                rec["neo_area_mean"] = float(neo.mean()) if neo.size else np.nan
                recs.append(rec)
        feat = pd.DataFrame(recs).set_index("spot") if recs else pd.DataFrame()
        full = pd.DataFrame(index=np.arange(len(xy))).join(feat)
        full.insert(0, "barcode", bc)
        full.insert(0, "sample_id", sid)
        full.insert(0, "task", td["task"])
        for col in ("n_nuclei", "n_neoplastic"):
            full[col] = full[col].fillna(0).astype(int)
        for k_ in sorted(EXPECTED_CLASSES):
            full[f"frac_{k_}"] = full[f"frac_{k_}"].fillna(0.0)
        frames.append(full.reset_index(drop=True))
        summary.append(dict(
            task=td["task"], sample_id=sid, population=s["population"],
            n_patched_spots=len(xy), n_nuclei=int(len(nuc)), half_width_px=half,
            half_width_source=src, nucleus_spot_pairs=int(full.n_nuclei.sum()),
            spots_with_nuclei=int((full.n_nuclei > 0).sum()),
            mean_nuclei_per_spot=float(full.n_nuclei.mean()),
            classes_present="|".join(sorted(np.unique(cls))),
            dead_class_present=bool("dead" in set(np.unique(cls))),
            patch_attrs=json.dumps(attrs, sort_keys=True)))
        print(f"  [{sid}] {len(nuc):,} nuclei, half {half:.1f}px ({src}), "
              f"{int(full.n_nuclei.sum()):,} nucleus-spot pairs, "
              f"{int((full.n_nuclei>0).sum())}/{len(xy)} spots covered", flush=True)
    M = pd.concat(frames, ignore_index=True)
    M.to_parquet(MORPH_PARQUET, index=False)
    S = pd.DataFrame(summary)
    S.to_csv(f"{ROOT}/{OUTDIR}/d4_morphology_summary.csv", index=False)
    print(f"\n[write] {MORPH_PARQUET} ({len(M):,} spot rows)")
    print(f"[write] {OUTDIR}/d4_morphology_summary.csv")
    print(S[["sample_id", "population", "n_patched_spots", "n_nuclei", "half_width_px",
             "half_width_source", "spots_with_nuclei", "mean_nuclei_per_spot",
             "dead_class_present"]].to_string(index=False), flush=True)
    return S


# ------------------------------------------------------------------------------ the probe
def load_probe_inputs(td, enc):
    ids = sorted(s["sample_id"] for s in td["samples"])
    pop = {s["sample_id"]: s["population"] for s in td["samples"]}
    Xs, lab, xys, bcs = [], [], [], []
    for sid in ids:
        p = f"{ROOT}/{td['paths']['embeddings'].format(encoder=enc, sample_id=sid)}"
        with h5py.File(p, "r") as f:
            k = "barcodes" if "barcodes" in f else "barcode"
            b = np.asarray(f[k][:]).reshape(-1)
            bcs.append(np.array([x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x)
                                 for x in b], dtype=object))
            Xs.append(np.asarray(f["embeddings"][:], dtype=np.float32))
            xys.append(np.asarray(f["coords"][:], dtype=np.float64))
        lab += [sid] * len(bcs[-1])
    X = np.vstack(Xs)
    slide = np.array(lab)
    xy = np.vstack(xys)
    bc = np.concatenate(bcs)
    y = np.array([pop[s] for s in slide])
    return X, y, slide, xy, bc


def morph_matrix(slide, bc):
    M = pd.read_parquet(MORPH_PARQUET)
    idx = pd.MultiIndex.from_arrays([M.sample_id.astype(str), M.barcode.astype(str)])
    M = M.set_index(idx)
    want = pd.MultiIndex.from_arrays([pd.Series(slide).astype(str),
                                      pd.Series(bc).astype(str)])
    sub = M.reindex(want)
    cov = sub[MORPH_COVS].to_numpy(dtype=np.float64)
    matched = int(sub["n_nuclei"].notna().sum())
    return cov, matched


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", required=True, choices=("morph", "probe"))
    ap.add_argument("--encoder", default="")
    a = ap.parse_args(argv or sys.argv[1:])
    td = json.load(open(TD))
    out = f"{ROOT}/{OUTDIR}"
    t_start = time.time()

    cfg = dict(stage=f"round3_D4.3b_{a.stage}", script="code/scripts/round3_d4_probe.py",
               encoder=a.encoder, target="population", classes=["cordeliers_ccRCC",
                                                                "indiana_nontumour"],
               protocols=["block", "slide_out"], adjustments=["none", "morphology_v2_ext"],
               morph_covs=MORPH_COVS, seed=SEED, latent=LATENT, grid=GRID,
               test_frac=TEST_FRAC, subsample_per_slide=SUBSAMPLE,
               hest_revision=HEST_REVISION,
               harness_md5=md5(os.path.join(_HERE, "round3_a0_harness.py")),
               task_def=f"{OUTDIR}/task_defs/KIDNEY_POP54.json")
    blob = json.dumps(cfg, sort_keys=True)
    chash = hashlib.sha256(blob.encode()).hexdigest()[:16]
    print(f"[config] sha256/16 {chash}\n{blob}", flush=True)

    if a.stage == "morph":
        build_morphology(td)
        print(f"[done] {time.time()-t_start:.0f}s", flush=True)
        return 0

    enc = a.encoder
    assert enc, "--stage probe needs --encoder"
    X, y, slide, xy, bc = load_probe_inputs(td, enc)
    print(f"[load] {enc}: {X.shape[0]:,} patched spots x {X.shape[1]} dims, "
          f"{len(np.unique(slide))} slides, classes "
          f"{dict(zip(*np.unique(y, return_counts=True)))}", flush=True)
    cov, matched = morph_matrix(slide, bc)
    print(f"[morph] {matched:,}/{len(bc):,} spots matched the morphology table; "
          f"finite on all eight covariates: {int(np.isfinite(cov).all(axis=1).sum()):,}",
          flush=True)

    rng = np.random.default_rng(zlib.crc32(f"KIDNEY_POP54|probe|{enc}".encode()))
    keep = subsample(slide, SUBSAMPLE, rng)
    Xs, ys, ss, xys, covs = X[keep], y[keep], slide[keep], xy[keep], cov[keep]
    print(f"[subsample] {keep.sum():,} spots, {SUBSAMPLE} per slide cap", flush=True)

    rows, fold_rows = [], []
    for adj_name, rc in (("none", None), ("morphology_v2_ext", covs)):
        # ---- protocol `block`: R4's own, an upper bound for a slide-level label
        te = block_split(ss, xys, np.random.default_rng(
            zlib.crc32(f"KIDNEY_POP54|block|{enc}".encode())))
        tr = ~te
        acc, yt, yp = probe_pred(Xs, ys, tr, te, rc)
        cm = (confusion_matrix(yt, yp, labels=sorted(set(ys))).tolist()
              if yt is not None else None)
        rows.append(dict(encoder=enc, target="population", protocol="block",
                         adjustment=adj_name, balanced_accuracy=acc, chance=0.5,
                         n_train=int(tr.sum()), n_test=int(te.sum()),
                         n_slides_train=int(len(np.unique(ss[tr]))),
                         n_slides_test=int(len(np.unique(ss[te]))),
                         confusion=json.dumps(cm), labels=";".join(sorted(set(ys)))))
        # ---- protocol `slide_out`: the honest one for a slide-level target
        accs = []
        for s in sorted(np.unique(ss)):
            te = ss == s
            tr = ~te
            acc_s, yt, yp = probe_pred(Xs, ys, tr, te, rc)
            # one class in the test set, so balanced accuracy on one slide is the recall of
            # that slide's own population; recorded as accuracy on the held-out slide
            rec = float((yp == yt).mean()) if yt is not None else np.nan
            accs.append(rec)
            fold_rows.append(dict(encoder=enc, protocol="slide_out", adjustment=adj_name,
                                  held_out_slide=s, population=ys[te][0],
                                  accuracy_on_held_out_slide=rec,
                                  n_train=int(tr.sum()), n_test=int(te.sum())))
        pops = np.array([ys[ss == s][0] for s in sorted(np.unique(ss))])
        acc_arr = np.array(accs, dtype=float)
        bal = float(np.mean([acc_arr[pops == p].mean() for p in sorted(set(pops))]))
        rows.append(dict(encoder=enc, target="population", protocol="slide_out",
                         adjustment=adj_name, balanced_accuracy=bal, chance=0.5,
                         n_train=int(len(ss) - 1), n_test=int(len(np.unique(ss))),
                         n_slides_train=int(len(np.unique(ss)) - 1), n_slides_test=1,
                         confusion=json.dumps(None),
                         labels=";".join(sorted(set(ys)))))
        print(f"  [{adj_name}] block {rows[-2]['balanced_accuracy']:.4f}, "
              f"slide_out {bal:.4f}", flush=True)

    R = pd.DataFrame(rows)
    F = pd.DataFrame(fold_rows)
    # the fraction of the signature composition explains, on both protocols
    extra = []
    for proto in ("block", "slide_out"):
        u = float(R[(R.protocol == proto) & (R.adjustment == "none")].balanced_accuracy.iloc[0])
        adj = float(R[(R.protocol == proto)
                      & (R.adjustment == "morphology_v2_ext")].balanced_accuracy.iloc[0])
        extra.append(dict(encoder=enc, protocol=proto, balanced_accuracy_unadjusted=u,
                          balanced_accuracy_adjusted=adj, drop=u - adj,
                          fraction_above_chance_removed=((u - adj) / (u - 0.5)
                                                         if u > 0.5 else np.nan),
                          composition_explains_majority=bool(u > 0.5 and (u - adj) / (u - 0.5)
                                                             > 0.5)))
    E = pd.DataFrame(extra)
    R.to_csv(f"{out}/d4_population_probe__{enc}.csv", index=False)
    F.to_csv(f"{out}/d4_population_probe_folds__{enc}.csv", index=False)
    E.to_csv(f"{out}/d4_population_probe_adjustment__{enc}.csv", index=False)
    print(f"\n[write] d4_population_probe__{enc}.csv\n"
          + R.drop(columns=["confusion"]).round(5).to_string(index=False))
    print("\n" + E.round(5).to_string(index=False), flush=True)

    with open(f"{out}/PROVENANCE__d4_population_probe__{enc}.txt", "w") as f:
        f.write("=" * 78 + "\n"
                f"Round 3, stage D4.3b - the population probe, encoder {enc}\n"
                f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID', 'NA')}\n"
                f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION', 'NA')}\n"
                f"node            : {os.environ.get('SLURMD_NODENAME', 'NA')}\n"
                f"gpu             : none (CPU job)\n"
                f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
                f"repo_commit     : "
                f"{subprocess.run(['git', '-C', ROOT, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()}\n"
                f"script          : code/scripts/round3_d4_probe.py\n"
                f"script_md5      : {md5(os.path.abspath(__file__))}\n"
                f"harness_md5     : {cfg['harness_md5']}\n"
                f"command_line    : {' '.join(sys.argv)}\n"
                f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED', 'unset')}\n"
                f"config_hash     : sha256/16 {chash}\n"
                f"config          : {blob}\n"
                f"morph_parquet   : instrumentation/morphology_v2_ext/KIDNEY_POP54_morph.parquet\n"
                f"cellvit_source  : hest_ext/kidney_visium_cell/cellvit_seg/, D1's download at "
                f"HEST revision {HEST_REVISION}\n"
                f"wall_seconds    : {time.time() - t_start:.0f}\n"
                "plan            : round3_execution_plan.md section 13.7.3\n")
    print(f"\n[done] {time.time()-t_start:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
