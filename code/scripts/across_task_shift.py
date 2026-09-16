#!/usr/bin/env python
"""Stage 4b(iii), arm B: across-task shift on a SHARED gene panel.

Handoff 4b(iii) asks to "also run across-task, training on all Xenium tasks and testing on a
held-out Xenium task". A first attempt found 0 genes shared across the five Xenium tasks' top-50
variance-ranked lists and reported the arm infeasible. That was the wrong gene set to test: the
top-50 SELECTIONS are disjoint (pairwise overlap 1-20), and the underlying assay panels differ
too (each task ships 538-541 var_names but they are DIFFERENT Xenium panels).

Two corrections to a first attempt at this script:
  (a) the intersection must be taken over ALL 15 Xenium samples, not the first sample of each
      task -- panels vary WITHIN a task as well (PAAD: 3 samples, 159 shared of a 919 union;
      LUNG: 259 of 823; no task has identical panels across its samples).
  (b) Xenium negative-control probes must be excluded. The raw intersection is 75 entries of
      which 61 are NegControlProbe_*/NegControlCodeword_* QC features that carry no biological
      signal by construction. Regressing on them yields numbers that look real and mean nothing.
That leaves 14 REAL shared genes: ACTA2 CCR7 CD3E CD79A CD83 CD8A CXCR4 GPR183 GZMK KIT KLRB1
MKI67 PDGFRA TNFRSF17 -- immune-infiltration and proliferation markers.

So the arm runs on those 14 shared real genes. Because that is NOT the benchmark's target set, an
across-task number on 77 genes is not comparable to Table 1. The comparison is therefore made
WITHIN this gene set:
    within_task  the shipped patient folds, scored on the 77 shared genes
    across_task  train on the other four Xenium tasks, test on the held-out one, same 77 genes
The gap (within - across) is the across-task shift with the gene set held constant, so it cannot
be an artefact of the shared panel containing genes that happen to be hard in some task.

TRAINING SIZE MUST ALSO BE MATCHED. The unmatched arm trains the across-task model on every spot
from the other four tasks (31k-64k), while the within-task model trains on one task's complement
(1.5k for SKCM). That is up to a 40x data advantage, in the direction that favours the across-task
arm precisely for the small tasks -- so an unmatched gap confounds shift with training-set size.
A third arm fixes it: for each within-task fold, fit an across-task model on EXACTLY as many spots
as that fold's training set, drawn from the other tasks, and evaluate on the SAME test spots. Then
within_task and across_matched differ only in where the training spots came from. Both arms are
reported, as unmatched (across_task) and matched (across_matched).

Pipeline is the benchmark's, verbatim.
Usage: across_task_shift.py <encoder>
"""
import os, sys, json, glob, re
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

# ---- shared panel: intersection over EVERY Xenium sample, negative controls removed ----
CTRL = re.compile(r"^(NegControl|BLANK|Unassigned|antisense|DeprecatedCodeword)", re.I)
per_sample = {}
for t in XENIUM:
    for p in sorted(glob.glob(f"{BD}/{t}/adata/*.h5ad")):
        A = ad.read_h5ad(p, backed="r")
        per_sample[(t, os.path.basename(p)[:-5])] = set(map(str, A.var_names[:]))
        try: A.file.close()
        except Exception: pass
raw = set.intersection(*per_sample.values())
SHARED = sorted(g for g in raw if not CTRL.match(g))
n_ctrl = len(raw) - len(SHARED)
print(f"Xenium samples scanned: {len(per_sample)}", flush=True)
print(f"raw intersection {len(raw)} = {len(SHARED)} real genes + {n_ctrl} negative controls",
      flush=True)
print(f"shared real genes: {SHARED}", flush=True)
assert len(SHARED) >= MIN_GENES, f"only {len(SHARED)} real shared genes"

def load(task, genes):
    Xs, Ys, slides = [], [], []
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

data = {t: load(t, SHARED) for t in XENIUM}
for t in XENIUM:
    print(f"  loaded {t}: X={data[t][0].shape}", flush=True)

rows = []
for held in XENIUM:
    Xh, Yh, sh = data[held]

    # --- within_task: the shipped patient folds, scored on the SHARED genes ---
    accs, fold_specs = [], []
    for sp in sorted(glob.glob(f"{BD}/{held}/splits/test_*.csv")):
        test_ids = {os.path.basename(x).replace(".h5ad","")
                    for x in pd.read_csv(sp)["expr_path"]}
        te = np.isin(sh, list(test_ids)); tr = ~te
        if te.sum() < 20 or tr.sum() < 50:
            continue
        r_, ng = fit_eval(Xh[tr], Xh[te], Yh[tr], Yh[te])
        accs.append(r_); fold_specs.append((int(tr.sum()), te.copy()))
    r_within = float(np.mean(accs)) if accs else np.nan

    # --- across_task: train on the other four Xenium tasks ---
    others = [t for t in XENIUM if t != held]
    Xtr = np.vstack([data[t][0] for t in others])
    Ytr = np.vstack([data[t][1] for t in others])
    r_across, ng2 = fit_eval(Xtr, Xh, Ytr, Yh)

    # --- across_matched: same test spots and same n_train as each within-task fold ---
    matched = []
    for sp, (tr_n, te_mask) in zip(sorted(glob.glob(f"{BD}/{held}/splits/test_*.csv")), fold_specs):
        rng = np.random.default_rng(SEED)
        if len(Xtr) < tr_n:
            continue
        pick = rng.choice(len(Xtr), size=tr_n, replace=False)
        assert len(pick) == tr_n
        r_m, _ = fit_eval(Xtr[pick], Xh[te_mask], Ytr[pick], Yh[te_mask])
        matched.append(r_m)
    r_matched = float(np.mean(matched)) if matched else np.nan

    rows.append(dict(encoder=enc, held_task=held, n_genes_shared=len(SHARED), n_ctrl_excluded=n_ctrl,
                     n_train_across=len(Xtr), n_test=len(Xh), n_folds_within=len(accs),
                     n_train_within=int(np.mean([f[0] for f in fold_specs])) if fold_specs else None,
                     pearson_within=r_within, pearson_across=r_across,
                     pearson_across_matched=r_matched,
                     across_task_shift=r_within - r_across,
                     across_task_shift_matched=r_within - r_matched,
                     train_tasks="|".join(others)))
    print(f"  hold={held:6s} within={r_within:.4f} across={r_across:.4f} "
          f"across_matched={r_matched:.4f} | shift={r_within-r_across:+.4f} "
          f"matched_shift={r_within-r_matched:+.4f}  "
          f"(n_train within~{int(np.mean([f[0] for f in fold_specs])) if fold_specs else 0} "
          f"vs across {len(Xtr)})", flush=True)

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/across_task_shift__{enc}.csv", index=False)
print()
print(d[["held_task","n_train_within","n_train_across","pearson_within","pearson_across",
         "pearson_across_matched","across_task_shift","across_task_shift_matched"]]
      .round(4).to_string(index=False))
print(f"\nmean across-task shift, UNMATCHED training size: {d.across_task_shift.mean():+.4f}")
print(f"mean across-task shift, MATCHED training size  : {d.across_task_shift_matched.mean():+.4f}")
print(f"  on {len(SHARED)} shared REAL genes ({n_ctrl} negative controls excluded)")
print(f"across-task Pearson positive in {int((d.pearson_across > 0).sum())}/{len(d)} tasks")
