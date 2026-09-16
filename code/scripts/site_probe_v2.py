#!/usr/bin/env python
"""Stage 4d (CORRECTED): site-predictability probe as the handoff specifies.

Handoff 4d: "train a logistic-regression probe (with the same PCA-256 preprocessing) to predict
COHORT SOURCE and TECHNOLOGY from embeddings; evaluate with SAMPLE-LEVEL cross-validation so no
slide appears in both train and test. Report accuracy against a chance baseline."

My first attempt predicted SLIDE IDENTITY with a random within-slide split. That was wrong on
both counts, and structurally so: a slide-ID target cannot be evaluated with slides held out,
because the held-out slide's label is never in training. It also cannot serve the stated
downstream purpose -- this probe is Topic A's density-ratio estimator w(z)=p_test(z)/p_cal(z) for
weighted conformal, which requires generalisation to an UNSEEN slide.

Three probes here, every one with slides held out (StratifiedGroupKFold grouped on slide, or
leave-one-slide-out):

  1. technology   Xenium vs Visium, 72 slides.        CAVEAT: confounded with tissue -- the five
                  Xenium tasks are different organs from the five Visium tasks.
  2. cohort       5 sources (INT/MEND/TENX/NCBI/ZEN). CAVEAT: badly confounded. INT appears only
                  in CCRCC, MEND only in PRAD, ZEN only in READ, so the probe can succeed by
                  recognising TISSUE, not institution. TENX is all-Xenium and NCBI all-Visium,
                  so cohort is near-collinear with technology too.
  3. idc_institution  TENX vs NCBI within IDC only. Same tissue, same 541-gene Xenium assay,
                  differing only in source institution. THE ONLY CONFOUND-FREE CONTRAST, and
                  therefore the one to quote for "encoders encode site". 4 slides, leave-one-out.

DECLARED SUBSAMPLE: spots are subsampled to N_PER_SLIDE per slide (uniformly at random, seeded)
to keep PCA tractable when pooling all tasks. This is a probe, not a benchmark score.

Usage: site_probe_v2.py <encoder> [<encoder> ...]
"""
import os, sys, glob
import numpy as np, pandas as pd, h5py
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold, LeaveOneGroupOut
from sklearn.metrics import balanced_accuracy_score

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, EMB, OUT = f"{ROOT}/bench_data", f"{ROOT}/embeddings", f"{ROOT}/instrumentation"
SEED, LATENT, N_PER_SLIDE = 1, 256, 800
XENIUM = {"IDC","PAAD","SKCM","COAD","LUNG"}

def load_all(enc):
    """Pooled, subsampled spots across every task. Returns X, and a frame of slide-level labels."""
    rng = np.random.default_rng(SEED)
    Xs, meta = [], []
    for task in sorted(os.listdir(BD)):
        if not os.path.isdir(f"{BD}/{task}") or task.startswith("."):
            continue
        for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
            slide = os.path.basename(p)[:-5]
            f5 = f"{EMB}/{task}/{enc}/{slide}.h5"
            if not os.path.isfile(f5):
                continue
            with h5py.File(f5, "r") as f:
                n = f["embeddings"].shape[0]
                take = np.sort(rng.choice(n, size=min(N_PER_SLIDE, n), replace=False))
                E = np.asarray(f["embeddings"][take], dtype=np.float32)
            Xs.append(E)
            cohort = "".join(ch for ch in slide if ch.isalpha())
            meta += [dict(task=task, slide=slide, cohort=cohort,
                          technology="Xenium" if task in XENIUM else "Visium")]*len(E)
    if not Xs:
        return None, None
    return np.vstack(Xs), pd.DataFrame(meta)

def run(X, y, groups, splitter, name, enc, extra=None):
    accs, n_tr, n_te = [], [], []
    for tr, te in splitter.split(X, y, groups):
        if len(set(y[tr])) < len(set(y)):        # a class vanished from training: fold unusable
            continue
        pipe = Pipeline([("scaler", StandardScaler()),
                         ("PCA", PCA(n_components=min(LATENT, X.shape[1]), random_state=SEED))])
        Z = pipe.fit_transform(X[tr]); Zt = pipe.transform(X[te])
        clf = LogisticRegression(max_iter=3000, n_jobs=-1).fit(Z, y[tr])
        accs.append(balanced_accuracy_score(y[te], clf.predict(Zt)))
        n_tr.append(len(tr)); n_te.append(len(te))
    if not accs:
        print(f"  [skip] {enc} {name}: no usable fold (a class was always missing from training)",
              flush=True)
        return None
    k = len(set(y)); chance = 1.0/k
    row = dict(encoder=enc, probe=name, n_classes=k, n_folds=len(accs),
               n_slides=len(set(groups)), balanced_acc=float(np.mean(accs)),
               acc_std=float(np.std(accs)), chance=chance,
               lift=float(np.mean(accs))/chance, excess=float(np.mean(accs))-chance,
               mean_n_train=int(np.mean(n_tr)), mean_n_test=int(np.mean(n_te)))
    if extra: row.update(extra)
    print(f"  {enc:11s} {name:16s} k={k} folds={len(accs):2d}  "
          f"bal.acc={row['balanced_acc']:.4f}+-{row['acc_std']:.4f}  chance={chance:.3f}  "
          f"lift={row['lift']:.2f}x", flush=True)
    return row

rows = []
for enc in sys.argv[1:]:
    X, m = load_all(enc)
    if X is None:
        print(f"[skip] {enc}: no embeddings", flush=True); continue
    print(f"[{enc}] pooled X={X.shape}, {m.slide.nunique()} slides, "
          f"{m.cohort.nunique()} cohorts", flush=True)

    # 1. technology, slides held out
    r = run(X, m.technology.to_numpy(), m.slide.to_numpy(),
            StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED),
            "technology", enc, dict(confounded="yes: Xenium and Visium tasks are different organs"))
    if r: rows.append(r)

    # 2. cohort source, slides held out
    r = run(X, m.cohort.to_numpy(), m.slide.to_numpy(),
            StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED),
            "cohort_source", enc,
            dict(confounded="yes: INT/MEND/ZEN each occur in one task only, so tissue is a proxy"))
    if r: rows.append(r)

    # 3. IDC institution only -- same tissue, same assay, leave one slide out
    sel = (m.task == "IDC").to_numpy()
    if sel.sum() and m.loc[sel, "cohort"].nunique() > 1:
        r = run(X[sel], m.loc[sel,"cohort"].to_numpy(), m.loc[sel,"slide"].to_numpy(),
                LeaveOneGroupOut(), "idc_institution", enc,
                dict(confounded="no: same tissue, same 541-gene Xenium assay, differs only by source"))
        if r: rows.append(r)
    del X

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/site_probe_v2__{sys.argv[1]}.csv", index=False)
print()
print(d.groupby("probe")[["balanced_acc","chance","lift","n_folds"]].mean().round(4).to_string())
