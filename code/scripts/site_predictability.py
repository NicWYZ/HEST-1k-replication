#!/usr/bin/env python
"""Stage 4d: how much site (slide) identity do the encoder features carry?

For each (task, encoder): PCA(256) on all spots, then multinomial logistic regression
predicting sample_id from the reduced features, scored on held-out spots drawn at random
WITHIN each sample (stratified), so every site is represented in training. The question is
separability of sites in feature space, not generalisation to a new site.

Reported as balanced accuracy against the chance level 1/n_samples. High separability means
the embedding encodes which slide a patch came from -- batch structure that any downstream
uncertainty estimate has to contend with, since spots are then not exchangeable across sites.

Usage: site_predictability.py <encoder> [<encoder> ...]
Writes instrumentation/site_predictability__<first-encoder>.csv
"""
import os, sys, json, glob
import numpy as np, pandas as pd, h5py
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import balanced_accuracy_score, accuracy_score

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, EMB, OUT = f"{ROOT}/bench_data", f"{ROOT}/embeddings", f"{ROOT}/instrumentation"
SEED, LATENT = 1, 256
encoders = sys.argv[1:]

def load(task, enc):
    Xs, sids = [], []
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        sid = os.path.basename(p)[:-5]
        f5 = f"{EMB}/{task}/{enc}/{sid}.h5"
        if not os.path.isfile(f5):
            return None, None
        with h5py.File(f5, "r") as f:
            E = np.asarray(f["embeddings"][:], dtype=np.float32)
        Xs.append(E); sids += [sid]*len(E)
    return np.vstack(Xs), np.array(sids)

rows = []
tasks = sorted([d for d in os.listdir(BD) if os.path.isdir(f"{BD}/{d}") and not d.startswith('.')])
for enc in encoders:
    for task in tasks:
        X, sid = load(task, enc)
        if X is None:
            print(f"[skip] {task}/{enc}: missing embeddings", flush=True); continue
        n_samp = len(set(sid))
        if n_samp < 2:
            continue
        Xtr, Xte, ytr, yte = train_test_split(X, sid, test_size=0.3, random_state=SEED, stratify=sid)
        pipe = Pipeline([("scaler", StandardScaler()),
                         ("PCA", PCA(n_components=min(LATENT, Xtr.shape[1]), random_state=SEED))])
        Ztr = pipe.fit_transform(Xtr); Zte = pipe.transform(Xte)
        # multi_class= was removed in scikit-learn 1.7; multinomial is the default for
        # multiclass problems with the lbfgs solver, so the behaviour is unchanged.
        clf = LogisticRegression(max_iter=2000, n_jobs=-1)
        clf.fit(Ztr, ytr)
        pred = clf.predict(Zte)
        bacc = balanced_accuracy_score(yte, pred)
        acc = accuracy_score(yte, pred)
        chance = 1.0 / n_samp
        rows.append(dict(encoder=enc, task=task, n_spots=len(X), n_samples=n_samp,
                         embed_dim=int(X.shape[1]), balanced_acc=bacc, accuracy=acc,
                         chance=chance, lift=bacc/chance,
                         excess=bacc-chance))
        print(f"  {enc:11s} {task:10s} n={len(X):6d} sites={n_samp:2d}  "
              f"bal.acc={bacc:.3f}  chance={chance:.3f}  lift={bacc/chance:.1f}x", flush=True)
        del X, Xtr, Xte, Ztr, Zte

d = pd.DataFrame(rows)
tag = encoders[0]
d.to_csv(f"{OUT}/site_predictability__{tag}.csv", index=False)
print()
print(d.groupby("encoder")[["balanced_acc","chance","lift"]].mean().round(3).to_string())
print(f"\nmean balanced accuracy {d.balanced_acc.mean():.3f} vs mean chance {d.chance.mean():.3f}")
print(f"min balanced accuracy  {d.balanced_acc.min():.3f} (task {d.loc[d.balanced_acc.idxmin(),'task']})")
