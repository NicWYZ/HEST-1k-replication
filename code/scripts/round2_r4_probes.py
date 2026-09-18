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
  PRAD patient 1: 8 slides. Grouping the raw pixel sizes by nominal value gives
  {0.57: MEND154/156/157/158/160 (5), 0.69: MEND159/161 (2), 0.17: MEND162 (1)}, which is
  the plan's own breakdown. Target: that nominal group, evaluated leave-one-slide-out so the
  held-out slide's group is always represented in training by another slide.
  DEVIATION, reported: the plan says "chance is 1/3 balanced", but its own instruction to
  exclude the single 0.172 slide from leave-one-slide-out leaves TWO evaluable classes over
  7 slides, so balanced chance is 1/2. Both are reported: `probe2_2class` is the primary
  result (7 held-out slides, chance 1/2), and `probe2_3class` keeps the 0.172 slide in
  training only, never held out, where chance is not well defined and which is reported for
  completeness only. Note also that under R0's binning these 8 slides occupy only TWO bins
  (0.15-0.23 and >0.50, since 0.573 and 0.688 both exceed 0.50), so the binned version of
  this probe is undefined for this patient; nominal raw values are used instead.
  RULE: high accuracy => scan resolution is decodable from the embeddings independently of
  patient, and every slide-identity probe is partly a resolution probe.

Probe 3 -- composition-adjusted slide probe.
  IDC, PAAD, LUNG, SKCM (single-slide patients, Xenium). The PCA-256 features are regressed
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

import h5py
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

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
    clf = LogisticRegression(max_iter=2000, n_jobs=-1).fit(Z, y[tr])
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
            acc_b = probe(Xs, ys, ~te_b, te_b)
            rows.append(dict(
                probe="probe1_slide_within_patient", encoder=enc, task="PRAD",
                unit="PRAD patient 2", n_classes=len(p2), chance=1.0 / len(p2),
                n_spots=int(keep.sum()), spots_per_slide=SUBSAMPLE,
                acc_random_split=acc_r, acc_blocked=acc_b, acc_drop=acc_r - acc_b,
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

        for variant, classes in (("probe2_2class", multi),
                                 ("probe2_3class", set(sizes))):
            ev = [s for s in p1 if grp.get(s) in multi]        # only these can be held out
            keepmask = np.isin(slide_of, [s for s in p1 if grp.get(s) in classes])
            accs, held = [], []
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
                yy = np.array([grp[x] for x in slide_of])
                a = probe(X[sub], yy[sub], (tr & sub)[sub], (te & sub)[sub])
                accs.append(a); held.append(s)
            if accs:
                rows.append(dict(
                    probe=variant, encoder=enc, task="PRAD", unit="PRAD patient 1",
                    n_classes=len(classes), chance=1.0 / len(multi),
                    n_folds=len(accs), acc_blocked=float(np.mean(accs)),
                    acc_sd=float(np.std(accs, ddof=1)) if len(accs) > 1 else np.nan,
                    held_out_slides=";".join(held),
                    px_values=";".join(f"{g}:{n_}" for g, n_ in sorted(sizes.items())),
                    rule="high accuracy => resolution is decodable independently of patient",
                    note=("primary; the single 0.17 slide is excluded from hold-out per the "
                          "plan, which leaves 2 evaluable classes and chance 1/2, not the "
                          "1/3 the plan states" if variant == "probe2_2class" else
                          "0.17 slide in training only, never held out; chance not well "
                          "defined for this variant, reported for completeness")))
                print(f"  {variant} {enc}: {len(accs)} LOSO folds, chance {1/len(multi):.3f}, "
                      f"acc {np.mean(accs):.4f}", flush=True)
        del X

    # ------------------------------------------------------- Probe 3: composition adjustment
    for task in PROBE3_TASKS:
        X, slide_of, xy, bc = load(task, enc)
        if X is None:
            print(f"[skip] {task}/{enc}: no embeddings", flush=True)
            continue
        mp = f"{MORPH}/{task}_morph.parquet"
        if not os.path.isfile(mp):
            print(f"[skip] probe3 {task}: no morphology parquet", flush=True)
            del X
            continue
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
            unit=f"{task}, single-slide patients", n_classes=len(set(ys)),
            chance=1.0 / len(set(ys)), n_spots=int(keep.sum()),
            morph_match_frac=float(matched.mean()),
            acc_blocked=a_before, acc_blocked_adjusted=a_after,
            acc_drop=a_before - a_after,
            acc_blocked_adjusted_planset=a_after_plan,
            acc_drop_planset=a_before - a_after_plan,
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
        f"probe3_tasks    : {PROBE3_TASKS}\n"
        f"config_hash     : {abs(hash((SEED,LATENT,GRID,TEST_FRAC,SUBSAMPLE,tuple(MORPH_COVS)))):016x}\n"
        "plan            : round2_execution_plan.md stage R4 / plan phase R4\n"
        "deviation       : probe 2 balanced chance is 1/2 not 1/3, see script docstring\n")
