#!/usr/bin/env python
"""Stage 4f: held-out-gene sanity check, with the regularisation confound separated.

handoff 4f: "for one task, hold out 10 of the 50 genes from the ridge fit and confirm the
remaining 40 give a comparable average, guarding against per-gene leakage in the HVG selection
step."

THE CONFOUND. benchmark.py sets alpha = 100 / (latent_dim * n_genes). Dropping 10 targets
therefore changes the penalty from 100/(256*50) = 0.0078125 to 100/(256*40) = 0.009765625, a 25%
increase -- so a naive 40-gene refit varies the gene set AND the regularisation at once. If the
40-gene average moved, the naive experiment could not say which caused it. This is the same
defect as the Table A13 no-PCA comparison, where removing PCA also changed alpha 4x.

So three fits per fold, on identical folds and identical features:
  all50          all 50 targets, alpha = 100/(256*50)         -- the benchmark
  sub40_formula  40 targets, alpha = 100/(256*40)             -- naive subsetting
  sub40_fixed    40 targets, alpha = 100/(256*50) (unchanged) -- gene set varied ALONE
The comparison that answers the handoff's question is all50 vs sub40_fixed, restricted to the
same 40 genes in both. sub40_formula is reported to show how much of any apparent effect is
regularisation rather than leakage.

WHAT IT CAN AND CANNOT DETECT. Multi-output ridge fits each target independently given a shared
design matrix, so with alpha fixed the 40 retained genes' predictions should be IDENTICAL, not
merely comparable -- any difference beyond solver tolerance means something couples the targets.
That makes this a strong check with a sharp prediction. It does NOT test leakage in the
highly-variable-gene SELECTION itself: the 50 genes were ranked using every spot in the task,
test folds included. That is a property of the shipped benchmark data, not of the fit, and it
cannot be tested by refitting -- it would need the ranking recomputed inside each fold. Reported
as a separate limitation rather than implied to be covered.

Usage: heldout_gene_check.py <task> <encoder>
"""
import os, sys, json, glob
import numpy as np, pandas as pd, h5py, anndata as ad, scanpy as sc
from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, EMB, OUT = f"{ROOT}/bench_data", f"{ROOT}/embeddings", f"{ROOT}/results/tailored/genes"
SEED, LATENT, N_DROP = 1, 256, 10
task, enc = sys.argv[1], sys.argv[2]

genes = json.load(open(f"{BD}/{task}/var_50genes.json"))["genes"]
rng = np.random.default_rng(SEED)
drop_idx = np.sort(rng.choice(len(genes), size=N_DROP, replace=False))
keep_idx = np.array([i for i in range(len(genes)) if i not in set(drop_idx.tolist())])
print(f"task={task} enc={enc}")
print(f"dropped {N_DROP}: {[genes[i] for i in drop_idx]}")
print(f"kept {len(keep_idx)}")

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
print(f"X {X.shape} Y {Y.shape}")

def run(Xtr, Xte, Ytr, Yte, alpha):
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=min(LATENT, Xtr.shape[1]), random_state=SEED))])
    A_ = pipe.fit_transform(Xtr); B_ = pipe.transform(Xte)
    reg = Ridge(solver="lsqr", alpha=alpha, random_state=0,
                fit_intercept=False, max_iter=1000).fit(A_, Ytr)
    return reg.predict(B_)

rows = []
for sp in sorted(glob.glob(f"{BD}/{task}/splits/test_*.csv")):
    k = int(os.path.basename(sp).split("_")[1].split(".")[0])
    test_ids = {os.path.basename(x).replace(".h5ad","") for x in pd.read_csv(sp)["expr_path"]}
    te = np.isin(samp, list(test_ids)); tr = ~te
    a50 = 100/(LATENT*len(genes)); a40 = 100/(LATENT*len(keep_idx))

    P_all = run(X[tr], X[te], Y[tr], Y[te], a50)[:, keep_idx]
    P_for = run(X[tr], X[te], Y[tr][:, keep_idx], Y[te][:, keep_idx], a40)
    P_fix = run(X[tr], X[te], Y[tr][:, keep_idx], Y[te][:, keep_idx], a50)
    Yk = Y[te][:, keep_idx]

    def avg(P):
        rs = [pearsonr(P[:, j], Yk[:, j])[0] for j in range(Yk.shape[1])
              if np.std(Yk[:, j]) > 0 and np.std(P[:, j]) > 0]
        return float(np.mean(rs)) if rs else np.nan

    rows.append(dict(task=task, encoder=enc, fold=k, n_train=int(tr.sum()), n_test=int(te.sum()),
                     alpha_50=a50, alpha_40=a40,
                     r_all50=avg(P_all), r_sub40_formula=avg(P_for), r_sub40_fixed=avg(P_fix),
                     max_abs_pred_diff_fixed=float(np.abs(P_all - P_fix).max()),
                     max_abs_pred_diff_formula=float(np.abs(P_all - P_for).max())))
    print(f"  fold{k}: all50={rows[-1]['r_all50']:.4f} "
          f"sub40_fixed={rows[-1]['r_sub40_fixed']:.4f} "
          f"sub40_formula={rows[-1]['r_sub40_formula']:.4f} | "
          f"max|pred diff| fixed={rows[-1]['max_abs_pred_diff_fixed']:.2e}", flush=True)

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/heldout_gene_check__{task}__{enc}.csv", index=False)
print("\n=== handoff 4f ===")
print(d[["fold","r_all50","r_sub40_fixed","r_sub40_formula",
         "max_abs_pred_diff_fixed","max_abs_pred_diff_formula"]].round(6).to_string(index=False))
print(f"\nalpha: 50 genes {d.alpha_50.iloc[0]:.8f} | 40 genes by formula {d.alpha_40.iloc[0]:.8f} "
      f"({d.alpha_40.iloc[0]/d.alpha_50.iloc[0]:.2f}x)")
print(f"\ngene set varied ALONE (alpha fixed):")
print(f"  mean r all50 = {d.r_all50.mean():.6f}  vs  sub40_fixed = {d.r_sub40_fixed.mean():.6f}  "
      f"diff = {d.r_all50.mean()-d.r_sub40_fixed.mean():+.2e}")
print(f"  max |prediction difference| over all folds: {d.max_abs_pred_diff_fixed.max():.2e}")
print(f"  PREDICTION: identical, since multi-output ridge fits each target independently. "
      f"{'CONFIRMED' if d.max_abs_pred_diff_fixed.max() < 1e-4 else 'VIOLATED - targets are coupled'}")
print(f"\nregularisation effect alone (formula alpha vs fixed):")
print(f"  mean r sub40_formula = {d.r_sub40_formula.mean():.6f}  "
      f"diff vs fixed = {d.r_sub40_formula.mean()-d.r_sub40_fixed.mean():+.2e}")
print(f"\nNOT TESTED: leakage in the highly-variable-gene SELECTION, which ranked genes using all "
      f"spots\nincluding test folds. That is a property of the shipped data and needs the ranking "
      f"recomputed\nper fold, not a refit.")
