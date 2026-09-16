#!/usr/bin/env python
"""Does the benchmark's ridge penalty do anything? An alpha sweep at both feature scales.

WHY. Earlier in this replication I reported that the Table A13 no-PCA comparison "conflates
removing PCA with a 4x change in regularisation strength", because benchmark.py sets
alpha = 100/(d * n_genes) and d goes from 256 (PCA) to the raw embedding width. Stage 4f then
found that a 25% alpha change at PCA-256 moves the mean Pearson by 7e-09 -- nothing. If alpha is
negligible at that scale, the ridge is effectively OLS and my A13 claim overstated the problem.

That is a measurable question, so it is measured here rather than argued from magnitudes. For
each feature scale the penalty is swept across eight orders of magnitude, with the benchmark's
own formula value marked. Two possible outcomes, both informative:
  * the curve is flat at the formula value -> the penalty is decorative, A13 is NOT confounded by
    it, and my earlier framing needs correcting
  * the curve is steep there -> the penalty binds and the A13 confound is real as stated
The raw arm matters independently: raw features are standardised but not decorrelated, so the
Gram matrix is far worse conditioned than PCA components and alpha could bind there while being
irrelevant after PCA.

alpha=0 is included as the OLS reference (via lstsq, since Ridge(alpha=0) warns).
Usage: alpha_sweep.py <task> <encoder>
"""
import os, sys, json, glob
import numpy as np, pandas as pd, h5py, anndata as ad, scanpy as sc
from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, EMB, OUT = f"{ROOT}/bench_data", f"{ROOT}/embeddings", f"{ROOT}/results/tailored/regularization"
SEED, LATENT = 1, 256
task, enc = sys.argv[1], sys.argv[2]
ALPHAS = [0.0, 1e-4, 1e-3, 1e-2, 1e-1, 1.0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6]

genes = json.load(open(f"{BD}/{task}/var_50genes.json"))["genes"]
Xs, Ys, samp = [], [], []
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
    Ys.append(np.asarray(Y, dtype=np.float32)); samp += [sid]*len(bc)
X, Y, samp = np.vstack(Xs), np.vstack(Ys), np.array(samp)
D_RAW = X.shape[1]
print(f"task={task} enc={enc} X={X.shape} Y={Y.shape}")
print(f"formula alpha: PCA-256 = {100/(LATENT*len(genes)):.9f} | "
      f"raw d={D_RAW} = {100/(D_RAW*len(genes)):.9f}")

def score(P, Yte):
    rs = [pearsonr(P[:, j], Yte[:, j])[0] for j in range(Yte.shape[1])
          if np.std(Yte[:, j]) > 0 and np.std(P[:, j]) > 0]
    return float(np.mean(rs)) if rs else np.nan

rows = []
for sp in sorted(glob.glob(f"{BD}/{task}/splits/test_*.csv")):
    k = int(os.path.basename(sp).split("_")[1].split(".")[0])
    test_ids = {os.path.basename(x).replace(".h5ad","") for x in pd.read_csv(sp)["expr_path"]}
    te = np.isin(samp, list(test_ids)); tr = ~te

    for scale in ("pca256", "raw"):
        if scale == "pca256":
            pipe = Pipeline([("scaler", StandardScaler()),
                             ("PCA", PCA(n_components=min(LATENT, X.shape[1]), random_state=SEED))])
            A_ = pipe.fit_transform(X[tr]); B_ = pipe.transform(X[te])
            formula = 100/(LATENT*len(genes))
        else:
            sc_ = StandardScaler()
            A_ = sc_.fit_transform(X[tr]); B_ = sc_.transform(X[te])
            formula = 100/(D_RAW*len(genes))
        # condition number of the Gram matrix: the quantity that decides whether alpha can bind
        sv = np.linalg.svd(A_, compute_uv=False)
        cond = float((sv[0]/sv[-1])**2) if sv[-1] > 0 else np.inf
        gram_diag = float((A_**2).sum(0).mean())

        for a in ALPHAS:
            if a == 0.0:
                W, *_ = np.linalg.lstsq(A_, Y[tr], rcond=None)
                P = B_ @ W
            else:
                P = Ridge(solver="lsqr", alpha=a, random_state=0,
                          fit_intercept=False, max_iter=1000).fit(A_, Y[tr]).predict(B_)
            rows.append(dict(task=task, encoder=enc, fold=k, scale=scale, alpha=a,
                             is_formula_value=bool(abs(a-formula) < 1e-12),
                             formula_alpha=formula, d=A_.shape[1],
                             gram_cond=cond, gram_diag_mean=gram_diag,
                             pearson=score(P, Y[te])))
        print(f"  fold{k} {scale:7s} d={A_.shape[1]:5d} cond={cond:.3e} "
              f"formula_alpha={formula:.9f}", flush=True)

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/alpha_sweep__{task}__{enc}.csv", index=False)
piv = d.groupby(["scale","alpha"]).pearson.mean().unstack("scale")
print("\n=== mean Pearson vs alpha ===")
print(piv.round(5).to_string())
for scale in ("pca256","raw"):
    g = d[d.scale == scale]
    fa = g.formula_alpha.iloc[0]
    at_formula = g[g.alpha == 0.0].pearson.mean()   # OLS reference
    best = piv[scale].max(); worst = piv[scale].min()
    near = g[g.is_formula_value].pearson.mean()
    print(f"\n{scale}: formula alpha = {fa:.9f}, d = {int(g.d.iloc[0])}, "
          f"Gram cond = {g.gram_cond.mean():.3e}")
    print(f"  Pearson at alpha=0 (OLS)        : {at_formula:.6f}")
    print(f"  Pearson at the formula alpha    : {near:.6f}" if np.isfinite(near) else
          "  formula alpha not on the sweep grid")
    print(f"  best over the sweep             : {best:.6f} at alpha="
          f"{piv[scale].idxmax():g}")
    print(f"  |OLS - formula|                 : {abs(at_formula-near):.2e}"
          if np.isfinite(near) else "")
    print(f"  range across 8 orders of alpha  : {worst:.6f} to {best:.6f}")
