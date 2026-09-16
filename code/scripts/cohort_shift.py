#!/usr/bin/env python
"""Stage 4b(iii) (CORRECTED): site shift as LEAVE-COHORT-SOURCE-OUT, per the handoff.

Handoff 4b: "(iii) leave-cohort-source-out where a task contains more than one source (IDC has
TENX and NCBI; also run across-task, training on all Xenium tasks and testing on a held-out
Xenium task). Report Pearson under each. The (i) minus (ii) gap is leakage; the (ii) minus (iii)
gap is site shift."

My earlier attempts used leave-one-SAMPLE-out and then a size-matched within/cross-slide
contrast. Both measure slide novelty, not INSTITUTION novelty. A new cohort source means a
different institution, scanner and staining protocol -- the shift that actually breaks
calibration -- so this is the arm the handoff asked for and the meaningful one.

Two arms:
  A. within-task leave-cohort-out. Only IDC qualifies: TENX95/TENX99 vs NCBI783/NCBI785, same
     breast tissue, same 541-gene Xenium panel. Train on one source, test on the other, both
     directions. Directly comparable to the shipped IDC number since the gene panel is identical.
  B. across-task leave-one-Xenium-task-out. Train on four Xenium tasks, test on the fifth.
     Requires a SHARED target gene set: each task ships its own top-50 list, so the intersection
     across the five Xenium tasks is used. If that intersection is too small the arm is reported
     INFEASIBLE rather than forced -- a 3-gene Pearson is not comparable to a 50-gene one.

Pipeline is the benchmark's, verbatim.
Usage: cohort_shift.py <encoder>
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
SEED, LATENT, MIN_GENES = 1, 256, 10
XENIUM = ["COAD","IDC","LUNG","PAAD","SKCM"]
enc = sys.argv[1]

def load(task, genes):
    Xs, Ys, slides = [], [], []
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        sl = os.path.basename(p)[:-5]
        f5 = f"{EMB}/{task}/{enc}/{sl}.h5"
        if not os.path.isfile(f5):
            return None, None, None
        with h5py.File(f5, "r") as f:
            k = "barcodes" if "barcodes" in f else "barcode"
            b = np.asarray(f[k][:]).reshape(-1)
            bc = [x.decode() if isinstance(x,(bytes,np.bytes_)) else str(x) for x in b]
            Xs.append(np.asarray(f["embeddings"][:], dtype=np.float32))
        A = ad.read_h5ad(p); sc.pp.log1p(A)
        miss = [g for g in genes if g not in set(map(str, A.var_names))]
        if miss:
            return None, None, None
        sub = A[bc, genes]
        Y = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
        Ys.append(np.asarray(Y, dtype=np.float32)); slides += [sl]*len(bc)
    return np.vstack(Xs), np.vstack(Ys), np.array(slides)

def fit_eval(Xtr, Xte, Ytr, Yte):
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=min(LATENT, Xtr.shape[1]), random_state=SEED))])
    A = pipe.fit_transform(Xtr); B = pipe.transform(Xte)
    reg = Ridge(solver="lsqr", alpha=100/(A.shape[1]*Ytr.shape[1]),
                random_state=0, fit_intercept=False, max_iter=1000).fit(A, Ytr)
    P = reg.predict(B)
    r = [pearsonr(P[:, j], Yte[:, j])[0] for j in range(Yte.shape[1])
         if np.std(Yte[:, j]) > 0 and np.std(P[:, j]) > 0]
    return float(np.mean(r)), len(r)

rows = []

# ---------------- arm A: within-task leave-cohort-out (IDC) ----------------
genes_idc = json.load(open(f"{BD}/IDC/var_50genes.json"))["genes"]
X, Y, slides = load("IDC", genes_idc)
if X is not None:
    cohort = np.array(["".join(c for c in s if c.isalpha()) for s in slides])
    for held in sorted(set(cohort)):
        te = cohort == held; tr = ~te
        if te.sum() < 50 or tr.sum() < 50:
            continue
        r, ng = fit_eval(X[tr], X[te], Y[tr], Y[te])
        rows.append(dict(encoder=enc, arm="within_task_leave_cohort_out", task="IDC",
                         held_out=held, n_train=int(tr.sum()), n_test=int(te.sum()),
                         n_genes=ng, pearson=r,
                         train_sources="|".join(sorted(set(cohort[tr]))),
                         note="same tissue, same 541-gene Xenium panel; differs only by institution"))
        print(f"  IDC hold-cohort={held:5s} train={tr.sum():6d} test={te.sum():6d} "
              f"r={r:.4f}", flush=True)
    del X, Y

# ---------------- arm B: across-task leave-one-Xenium-task-out ----------------
lists = {t: json.load(open(f"{BD}/{t}/var_50genes.json"))["genes"] for t in XENIUM}
shared = sorted(set.intersection(*[set(v) for v in lists.values()]))
print(f"\nshared genes across the 5 Xenium task panels: {len(shared)} "
      f"{shared[:12]}{' ...' if len(shared) > 12 else ''}", flush=True)
if len(shared) < MIN_GENES:
    rows.append(dict(encoder=enc, arm="across_task_xenium", task="ALL_XENIUM",
                     held_out=None, n_train=None, n_test=None, n_genes=len(shared),
                     pearson=np.nan,
                     note=f"INFEASIBLE: only {len(shared)} genes shared across the five Xenium "
                          f"panels (need >= {MIN_GENES}); a score on so few genes is not "
                          f"comparable to the 50-gene benchmark numbers"))
    print(f"  across-task arm INFEASIBLE: {len(shared)} shared genes < {MIN_GENES}", flush=True)
else:
    data = {}
    for t in XENIUM:
        Xt, Yt, st = load(t, shared)
        if Xt is not None:
            data[t] = (Xt, Yt, st)
    for held in sorted(data):
        Xte, Yte, _ = data[held]
        tr_tasks = [t for t in data if t != held]
        Xtr = np.vstack([data[t][0] for t in tr_tasks])
        Ytr = np.vstack([data[t][1] for t in tr_tasks])
        r, ng = fit_eval(Xtr, Xte, Ytr, Yte)
        rows.append(dict(encoder=enc, arm="across_task_xenium", task=held, held_out=held,
                         n_train=len(Xtr), n_test=len(Xte), n_genes=ng, pearson=r,
                         train_sources="|".join(tr_tasks),
                         note=f"trained on {len(tr_tasks)} other Xenium tasks, {len(shared)} shared genes"))
        print(f"  across-task hold={held:10s} train={len(Xtr):6d} test={len(Xte):6d} "
              f"r={r:.4f} on {ng} genes", flush=True)

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/cohort_shift__{enc}.csv", index=False)
print()
print(d[["arm","task","held_out","n_genes","pearson"]].to_string(index=False))
