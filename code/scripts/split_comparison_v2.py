#!/usr/bin/env python
"""Stage 4c: how much of the benchmark score is leakage, and how much is site shift?

Three fold designs on identical data, with the benchmark's exact pipeline
(StandardScaler -> PCA(256, random_state=seed) fit on train only -> Ridge(solver='lsqr',
alpha=100/(d*n_genes), fit_intercept=False, max_iter=1000), per-gene Pearson then mean):

  A random_spot  spots assigned to folds at random, IGNORING sample. Train and test therefore
                 contain neighbouring spots from the same slide. Fold SIZES are matched to the
                 shipped folds exactly, so A vs B differs only in grouping -> the gap is leakage.
  B patient      the shipped patient-stratified folds (splits/{train,test}_<k>.csv).
  C leave_one_sample  one held-out sample per fold: the strictest site shift available here.
                 Identical to B for tasks where n_folds == n_samples.

Usage: split_comparison.py <encoder>
Writes instrumentation/split_comparison_v2__<encoder>.csv
"""
import os, sys, json, glob
import numpy as np, pandas as pd, h5py, anndata as ad, scanpy as sc
from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, EMB, OUT = f"{ROOT}/bench_data", f"{ROOT}/embeddings", f"{ROOT}/instrumentation"
SEED, LATENT, N_REPEATS = 1, 256, 5
enc = sys.argv[1]

def load_task(task):
    """Concatenate embeddings + log1p targets for every sample, in embedding-file order."""
    genes = json.load(open(f"{BD}/{task}/var_50genes.json"))["genes"]
    Xs, Ys, sids = [], [], []
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        sid = os.path.basename(p)[:-5]
        with h5py.File(f"{EMB}/{task}/{enc}/{sid}.h5", "r") as f:
            k = "barcodes" if "barcodes" in f else "barcode"
            b = np.asarray(f[k][:]).reshape(-1)
            bc = [x.decode() if isinstance(x,(bytes,np.bytes_)) else str(x) for x in b]
            Xs.append(np.asarray(f["embeddings"][:], dtype=np.float32))
        A = ad.read_h5ad(p); sc.pp.log1p(A)
        sub = A[bc, genes]
        Y = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
        Ys.append(np.asarray(Y, dtype=np.float32)); sids += [sid]*len(bc)
    return np.vstack(Xs), np.vstack(Ys), np.array(sids), genes

def fit_eval(Xtr, Xte, Ytr, Yte):
    """The benchmark's pipeline, verbatim."""
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=LATENT, random_state=SEED))])
    Xtr2 = pipe.fit_transform(Xtr); Xte2 = pipe.transform(Xte)
    alpha = 100 / (Xtr2.shape[1] * Ytr.shape[1])
    reg = Ridge(solver="lsqr", alpha=alpha, random_state=0, fit_intercept=False, max_iter=1000)
    reg.fit(Xtr2, Ytr)
    P = reg.predict(Xte2)
    r = []
    for j in range(Yte.shape[1]):
        if np.std(Yte[:, j]) == 0 or np.std(P[:, j]) == 0:
            continue
        r.append(pearsonr(P[:, j], Yte[:, j])[0])
    return float(np.mean(r)), len(r), alpha

rows = []
tasks = sorted([d for d in os.listdir(BD) if os.path.isdir(f"{BD}/{d}") and not d.startswith('.')])
for task in tasks:
    if not glob.glob(f"{EMB}/{task}/{enc}/*.h5"):
        print(f"[skip] {task}: no embeddings for {enc}", flush=True); continue
    X, Y, sid, genes = load_task(task)
    n = len(X)
    shipped = sorted(glob.glob(f"{BD}/{task}/splits/test_*.csv"))

    # --- B: shipped patient-stratified folds ---
    shipped_sizes = []
    for sp in shipped:
        k = int(os.path.basename(sp).split("_")[1].split(".")[0])
        test_ids = {os.path.basename(x).replace(".h5ad","")
                    for x in pd.read_csv(sp)["expr_path"]}
        te = np.isin(sid, list(test_ids)); tr = ~te
        shipped_sizes.append(int(te.sum()))
        m, ng, a = fit_eval(X[tr], X[te], Y[tr], Y[te])
        rows.append(dict(encoder=enc, task=task, design="patient", fold=k, repeat=None,
                         n_train=int(tr.sum()), n_test=int(te.sum()), n_genes=ng,
                         alpha=a, pearson=m, n_test_samples=len(test_ids)))
        print(f"  {task} patient fold{k}: r={m:.4f}", flush=True)

    # --- A: random spot folds, sizes matched to the shipped folds, N_REPEATS repeats ---
    # handoff 4b(i) asks for five random repeats. The leakage estimate is the quantity this
    # experiment exists to produce, so its Monte-Carlo error must be reported rather than
    # assumed small: one repeat gives a point with no spread.
    for rep in range(N_REPEATS):
        rng = np.random.default_rng(SEED + 1000*rep)
        for k, sz in enumerate(shipped_sizes):
            idx = rng.permutation(n); te = np.zeros(n, bool); te[idx[:sz]] = True; tr = ~te
            m, ng, a = fit_eval(X[tr], X[te], Y[tr], Y[te])
            rows.append(dict(encoder=enc, task=task, design="random_spot", fold=k, repeat=rep,
                             n_train=int(tr.sum()), n_test=int(te.sum()), n_genes=ng,
                             alpha=a, pearson=m, n_test_samples=int(len(set(sid[te])))))
        print(f"  {task} random  repeat{rep}: "
              f"mean r={np.mean([r['pearson'] for r in rows if r['design']=='random_spot' and r['task']==task and r['repeat']==rep]):.4f}",
              flush=True)

    # --- C: leave-one-sample-out ---
    for k, s in enumerate(sorted(set(sid))):
        te = sid == s; tr = ~te
        if te.sum() < 20 or tr.sum() < 50:
            continue
        m, ng, a = fit_eval(X[tr], X[te], Y[tr], Y[te])
        rows.append(dict(encoder=enc, task=task, design="leave_one_sample", fold=k, repeat=None,
                         n_train=int(tr.sum()), n_test=int(te.sum()), n_genes=ng,
                         alpha=a, pearson=m, n_test_samples=1))
    print(f"[done] {task}: n={n}, {len(set(sid))} samples", flush=True)
    del X, Y

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/split_comparison_v2__{enc}.csv", index=False)
s = d.groupby(["task","design"]).pearson.mean().unstack()
print()
print(s.round(4).to_string())
if {"random_spot","patient"} <= set(s.columns):
    print(f"\nmean leakage gap (random_spot - patient): {(s.random_spot - s.patient).mean():+.4f}")
    per_rep = (d[d.design=="random_spot"].groupby(["task","repeat"]).pearson.mean()
               .unstack("repeat"))
    pat = d[d.design=="patient"].groupby("task").pearson.mean()
    gap_rep = per_rep.sub(pat, axis=0)
    print(f"leakage gap per repeat (mean over tasks): "
          f"{gap_rep.mean(axis=0).round(4).to_dict()}")
    print(f"Monte-Carlo SD of the gap across {N_REPEATS} repeats: "
          f"{gap_rep.mean(axis=0).std():.4f}")
if {"patient","leave_one_sample"} <= set(s.columns):
    print(f"mean site-shift gap (patient - leave_one_sample): {(s.patient - s.leave_one_sample).mean():+.4f}")
