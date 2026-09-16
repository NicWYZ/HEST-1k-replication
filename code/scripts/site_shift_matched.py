#!/usr/bin/env python
"""Stage 4c': site shift, with test-set AND training-set size held fixed.

The earlier three-design comparison (split_comparison.py) could not identify site shift: for
6/10 tasks leave-one-sample equals the shipped design by construction, and where a contrast did
exist the grouping change also changed test-set size (CCRCC 12,370 -> 3,092 test spots), giving
gaps of both signs -- the signature of a test-size artefact, since a single-slide test set has
restricted outcome range and depresses correlation regardless of any shift.

This design varies ONE thing. For each held-out slide s of a task:
    m       = n_spots(s)                      test-set size
    n_train = n_spots(task) - m               training-set size
  cross_slide : train on every spot NOT in s        -> test slide UNSEEN in training
  within_slide: test on m spots drawn at random from ALL slides, then train on n_train spots
                sampled from the remainder        -> test spots' own slides ARE in training
Both arms get exactly m test spots and exactly n_train training spots, by construction. The only
difference is slide novelty, so (within_slide - cross_slide) is a clean site-shift estimate.

Pipeline is the benchmark's, verbatim: StandardScaler -> PCA(256) fit on train only -> Ridge(
solver='lsqr', alpha=100/(d*n_genes), fit_intercept=False, max_iter=1000); per-gene Pearson
then mean.

Usage: site_shift_matched.py <encoder>
"""
import os, sys, json, glob
import numpy as np, pandas as pd, h5py, anndata as ad, scanpy as sc
from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, EMB, OUT = f"{ROOT}/bench_data", f"{ROOT}/embeddings", f"{ROOT}/results/tailored/shift"
SEED, LATENT = 1, 256
enc = sys.argv[1]

def load(task):
    genes = json.load(open(f"{BD}/{task}/var_50genes.json"))["genes"]
    Xs, Ys, labels = [], [], []
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        sl = os.path.basename(p)[:-5]
        with h5py.File(f"{EMB}/{task}/{enc}/{sl}.h5", "r") as f:
            k = "barcodes" if "barcodes" in f else "barcode"
            b = np.asarray(f[k][:]).reshape(-1)
            bc = [x.decode() if isinstance(x,(bytes,np.bytes_)) else str(x) for x in b]
            Xs.append(np.asarray(f["embeddings"][:], dtype=np.float32))
        A = ad.read_h5ad(p); sc.pp.log1p(A)
        sub = A[bc, genes]
        Y = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
        Ys.append(np.asarray(Y, dtype=np.float32)); labels += [sl]*len(bc)
    return np.vstack(Xs), np.vstack(Ys), np.array(labels), genes

def fit_eval(Xtr, Xte, Ytr, Yte):
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=LATENT, random_state=SEED))])
    A = pipe.fit_transform(Xtr); B = pipe.transform(Xte)
    reg = Ridge(solver="lsqr", alpha=100/(A.shape[1]*Ytr.shape[1]),
                random_state=0, fit_intercept=False, max_iter=1000).fit(A, Ytr)
    P = reg.predict(B)
    r = [pearsonr(P[:, j], Yte[:, j])[0] for j in range(Yte.shape[1])
         if np.std(Yte[:, j]) > 0 and np.std(P[:, j]) > 0]
    return float(np.mean(r)), len(r)

rows = []
tasks = sorted([d for d in os.listdir(BD) if os.path.isdir(f"{BD}/{d}") and not d.startswith('.')])
for task in tasks:
    if not glob.glob(f"{EMB}/{task}/{enc}/*.h5"):
        print(f"[skip] {task}: no embeddings", flush=True); continue
    X, Y, slide_of, genes = load(task)
    slides = sorted(set(slide_of))
    if len(slides) < 3:
        print(f"[skip] {task}: {len(slides)} slides, need >=3 so the within-slide arm can "
              f"still train on other slides", flush=True)
        continue
    n = len(X)
    rng = np.random.default_rng(SEED)
    for s in slides:
        held = slide_of == s
        m = int(held.sum())
        n_train = n - m
        if m < 50 or n_train < 100:
            continue

        # --- cross_slide: test slide unseen ---
        r_cross, ng = fit_eval(X[~held], X[held], Y[~held], Y[held])

        # --- within_slide: same m test spots drawn from everywhere, same n_train ---
        te_idx = rng.choice(n, size=m, replace=False)
        te = np.zeros(n, bool); te[te_idx] = True
        pool = np.flatnonzero(~te)
        tr_idx = rng.choice(pool, size=n_train, replace=False) if len(pool) > n_train else pool
        tr = np.zeros(n, bool); tr[tr_idx] = True
        assert int(te.sum()) == m, (int(te.sum()), m)
        assert int(tr.sum()) == n_train, (int(tr.sum()), n_train)
        assert not (te & tr).any(), "train/test overlap"
        r_within, _ = fit_eval(X[tr], X[te], Y[tr], Y[te])

        rows.append(dict(encoder=enc, task=task, held_slide=s, n_slides=len(slides),
                         m_test=m, n_train=n_train, n_genes=ng,
                         pearson_cross=r_cross, pearson_within=r_within,
                         site_shift=r_within - r_cross,
                         test_slides_in_train=int(len(set(slide_of[te]) & set(slide_of[tr])))))
        print(f"  {task:10s} hold={s:10s} m={m:6d} n_train={n_train:6d}  "
              f"cross={r_cross:.4f} within={r_within:.4f} shift={r_within-r_cross:+.4f}",
              flush=True)
    del X, Y

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/site_shift_matched__{enc}.csv", index=False)
print()
print(d.groupby("task")[["pearson_cross","pearson_within","site_shift"]].mean().round(4).to_string())
print(f"\nsizes matched exactly in all {len(d)} comparisons: "
      f"{bool((d.m_test > 0).all() and (d.n_train > 0).all())}")
print(f"mean site shift (within - cross): {d.site_shift.mean():+.4f}  "
      f"[{d.site_shift.min():+.4f}, {d.site_shift.max():+.4f}]")
print(f"positive in {int((d.site_shift > 0).sum())}/{len(d)} held-out slides")
