#!/usr/bin/env python
"""Round 2, R2 step 2: within-fold gene selection versus the shipped lists.

The shipped 50 target genes per task were variance-ranked over EVERY spot, test folds
included. A leakage-free evaluation recomputes the ranking inside each fold from training
samples only. This measures the difference.

Run only after `round2_r2_gene_check.py` reproduces the shipped lists exactly (directive
D2): if the reimplementation cannot reproduce them, a difference between the shipped and
fold-selected lists is uninterpretable, because it could be the reimplementation.

Both arms use IDENTICAL features and the identical head, so the only thing that varies
between them is which 50 genes are the targets. Per fold:

  shipped arm   the 50 genes in var_50genes.json (selected using test-fold spots)
  fold arm      50 genes selected from this fold's TRAINING samples only

Usage: round2_r2_fold_hvg.py <encoder>
"""
import glob
import json
import os
import sys
import time

import anndata as ad
import h5py
import numpy as np
import pandas as pd
import scanpy as sc
from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from round2_r2_gene_check import get_k_genes            # the verified reimplementation

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, EMB = f"{ROOT}/bench_data", f"{ROOT}/embeddings"
OUT = f"{ROOT}/results/round2/R2_fold_hvg"
SEED, LATENT, MIN_SPOTS, K = 1, 256, 50, 50

enc = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


def load_raw(task):
    """Raw (un-logged) AnnData per sample, with the barcode order the embeddings use."""
    out = []
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        sid = os.path.basename(p)[:-5]
        hp = f"{EMB}/{task}/{enc}/{sid}.h5"
        if not os.path.exists(hp):
            continue
        with h5py.File(hp, "r") as f:
            key = "barcodes" if "barcodes" in f else "barcode"
            b = np.asarray(f[key][:]).reshape(-1)
            bc = [x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in b]
            Xe = np.asarray(f["embeddings"][:], dtype=np.float32)
        A = ad.read_h5ad(p)
        out.append(dict(sid=sid, adata=A, bc=bc, X=Xe, panel=set(map(str, A.var_names))))
    return out


def targets(parts, genes):
    """log1p expression for `genes`, in embedding barcode order, stacked over samples."""
    Ys = []
    for q in parts:
        A = q["adata"].copy()
        sc.pp.log1p(A)
        sub = A[q["bc"], genes]
        Y = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
        Ys.append(np.asarray(Y, dtype=np.float32))
    return np.vstack(Ys)


def fit_intercept_head(Xtr, Xte, Ytr):
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("PCA", PCA(n_components=min(LATENT, Xtr.shape[1]), random_state=SEED))])
    A = pipe.fit_transform(Xtr)
    B = pipe.transform(Xte)
    reg = Ridge(solver="cholesky", alpha=100 / (A.shape[1] * Ytr.shape[1]),
                random_state=0, fit_intercept=True).fit(A.astype(np.float64),
                                                        Ytr.astype(np.float64))
    return reg.predict(B.astype(np.float64))


def score(P, Yte, samp_te, genes):
    """Pooled-over-fold Pearson per gene (the faithful metric, matches R1), and within-slide
    Pearson per gene. Returns (mean pooled, mean within, {gene: within})."""
    pooled = [pearsonr(P[:, j], Yte[:, j])[0] for j in range(Yte.shape[1])
              if np.std(Yte[:, j]) > 0 and np.std(P[:, j]) > 0]
    per_gene = {g: [] for g in genes}
    for s in np.unique(samp_te):
        m = samp_te == s
        if m.sum() < MIN_SPOTS:
            continue
        for j, g in enumerate(genes):
            if np.std(Yte[m, j]) > 0 and np.std(P[m, j]) > 0:
                per_gene[g].append(float(pearsonr(P[m, j], Yte[m, j])[0]))
    gw = {g: float(np.mean(v)) for g, v in per_gene.items() if v}
    return (float(np.mean(pooled)) if pooled else np.nan,
            float(np.mean(list(gw.values()))) if gw else np.nan, gw)


rows, panel_rows = [], []
tasks = sorted(d for d in os.listdir(BD)
               if os.path.isdir(f"{BD}/{d}") and not d.startswith("."))
for task in tasks:
    if not glob.glob(f"{EMB}/{task}/{enc}/*.h5"):
        print(f"[skip] {task}: no embeddings for {enc}", flush=True)
        continue
    shipped = json.load(open(f"{BD}/{task}/var_50genes.json"))["genes"]
    parts = load_raw(task)
    if not parts:
        continue
    X = np.vstack([q["X"] for q in parts])
    samp = np.concatenate([[q["sid"]] * len(q["bc"]) for q in parts])
    Y_ship = targets(parts, shipped)

    # panel heterogeneity within the task
    PANEL_ALL = set.intersection(*[q["panel"] for q in parts])
    psz = {q["sid"]: len(q["panel"]) for q in parts}
    print(f"[{task}] panels: sizes {sorted(set(psz.values()))}, "
          f"intersection {len(PANEL_ALL)}, union {len(set().union(*[q['panel'] for q in parts]))}, "
          f"identical across samples: {len(set(map(frozenset, (q['panel'] for q in parts)))) == 1}",
          flush=True)
    panel_rows.append(dict(task=task, n_samples=len(parts),
                           panel_min=min(psz.values()), panel_max=max(psz.values()),
                           panel_intersection=len(PANEL_ALL),
                           panel_union=len(set().union(*[q["panel"] for q in parts])),
                           panels_identical=len(set(map(frozenset,
                                                        (q["panel"] for q in parts)))) == 1,
                           shipped_all_on_panel=all(g in PANEL_ALL for g in shipped)))

    for sp in sorted(glob.glob(f"{BD}/{task}/splits/test_*.csv")):
        k = int(os.path.basename(sp).split("_")[1].split(".")[0])
        test_ids = {os.path.basename(x).replace(".h5ad", "") for x in pd.read_csv(sp)["expr_path"]}
        te = np.isin(samp, list(test_ids))
        tr = ~te
        t0 = time.time()

        # --- fold-selected genes: training samples only ---
        train_ads = [q["adata"] for q in parts if q["sid"] not in test_ids]
        assert train_ads, f"{task} fold {k}: no training samples"
        fold_raw, n_common = get_k_genes(train_ads, k=K)

        # A gene selected from the TRAINING samples need not be measured on the test slide:
        # HEST-bench samples within a task can carry different gene panels, and the shipped
        # 50-gene list is the intersection over ALL samples, test included. So a genuinely
        # leakage-free selection can name genes the test slide cannot report, and those are
        # dropped here rather than silently failing. Recording the count is the point: it is
        # the sense in which leakage-free gene selection is not merely unperformed on this
        # benchmark but not well defined without the test slide's panel.
        dropped = [g for g in fold_raw if g not in PANEL_ALL]
        fold_genes = [g for g in fold_raw if g in PANEL_ALL]
        assert fold_genes, f"{task} fold {k}: every fold-selected gene is off-panel somewhere"
        Y_fold = targets(parts, fold_genes)

        P_ship = fit_intercept_head(X[tr], X[te], Y_ship[tr])
        P_fold = fit_intercept_head(X[tr], X[te], Y_fold[tr])
        po_s, wi_s, gw_s = score(P_ship, Y_ship[te], samp[te], shipped)
        po_f, wi_f, gw_f = score(P_fold, Y_fold[te], samp[te], fold_genes)

        only_shipped = [g for g in shipped if g not in set(fold_genes)]
        mean_only_shipped = (float(np.mean([gw_s[g] for g in only_shipped if g in gw_s]))
                             if any(g in gw_s for g in only_shipped) else np.nan)
        only_fold = [g for g in fold_genes if g not in set(shipped)]
        mean_only_fold = (float(np.mean([gw_f[g] for g in only_fold if g in gw_f]))
                          if any(g in gw_f for g in only_fold) else np.nan)

        rows.append(dict(
            encoder=enc, task=task, fold=k, n_train=int(tr.sum()), n_test=int(te.sum()),
            n_train_samples=len(train_ads), n_common_genes=n_common,
            n_genes_shared=len(set(shipped) & set(fold_genes)),
            n_fold_genes_used=len(fold_genes),
            n_fold_genes_off_panel=len(dropped),
            genes_off_panel=";".join(dropped),
            pearson_pooled_shipped=po_s, pearson_pooled_fold=po_f,
            pearson_within_shipped=wi_s, pearson_within_fold=wi_f,
            delta_pooled=po_s - po_f, delta_within=wi_s - wi_f,
            mean_within_only_in_shipped=mean_only_shipped,
            mean_within_only_in_fold=mean_only_fold,
            genes_only_in_shipped=";".join(only_shipped),
            genes_only_in_fold=";".join(only_fold)))
        print(f"  {task} fold{k}: shared {len(set(shipped)&set(fold_genes))}/50, "
              f"pooled {po_s:.4f} vs {po_f:.4f} (d={po_s-po_f:+.4f}), "
              f"within {wi_s:.4f} vs {wi_f:.4f} (d={wi_s-wi_f:+.4f})  "
              f"[{time.time()-t0:.0f}s]", flush=True)
    del X, Y_ship, parts

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/fold_hvg__{enc}.csv", index=False)
pn = pd.DataFrame(panel_rows)
pn.to_csv(f"{OUT}/panel_heterogeneity__{enc}.csv", index=False)
print("\n=== gene-panel heterogeneity within each task ===")
print(pn.to_string(index=False))
print(f"\ntasks whose samples do NOT share one panel: "
      f"{pn[~pn.panels_identical].task.tolist()}")
print(f"shipped 50 genes all on the common panel, every task: {bool(pn.shipped_all_on_panel.all())}")
print(f"\nfold-selected genes dropped as off-panel: total {int(d.n_fold_genes_off_panel.sum())} "
      f"over {len(d)} folds; folds with any {int((d.n_fold_genes_off_panel>0).sum())}; "
      f"worst fold {int(d.n_fold_genes_off_panel.max())}/50")
print(d.groupby("task").n_fold_genes_off_panel.agg(["mean","max"]).round(2).to_string())

print(f"\n=== R2: shipped minus fold-selected, encoder {enc} ===")
agg = d.groupby("task").agg(
    n_folds=("fold", "size"),
    shared_genes_mean=("n_genes_shared", "mean"),
    delta_within_mean=("delta_within", "mean"), delta_within_sd=("delta_within", "std"),
    delta_pooled_mean=("delta_pooled", "mean"), delta_pooled_sd=("delta_pooled", "std"),
    n_positive=("delta_within", lambda s: int((s > 0).sum())))
print(agg.round(4).to_string())
print(f"\noverall delta_within: mean {d.delta_within.mean():+.4f} "
      f"sd {d.delta_within.std():.4f} over {len(d)} folds; "
      f"positive in {int((d.delta_within > 0).sum())}/{len(d)}")
print(f"overall delta_pooled: mean {d.delta_pooled.mean():+.4f} sd {d.delta_pooled.std():.4f}")
print(f"mean shared genes: {d.n_genes_shared.mean():.1f}/50")
worst = float(agg.delta_within_mean.max())
print(f"\nlargest per-task mean delta_within: {worst:+.4f}  [escalation threshold 0.02]  "
      f"{'ESCALATE to Nicolas' if worst > 0.02 else 'below threshold'}")

with open(f"{OUT}/PROVENANCE__fold_hvg_{enc}.txt", "w") as f:
    f.write(f"Round 2, R2 step 2 - within-fold gene selection, encoder {enc}\n"
            f"slurm_job_id      : {os.environ.get('SLURM_JOB_ID','NA')}\n"
            f"slurm_partition   : {os.environ.get('SLURM_JOB_PARTITION','NA')}\n"
            f"node              : {os.environ.get('SLURMD_NODENAME','NA')}\n"
            f"date              : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
            f"repo_commit       : {os.popen(f'git -C {ROOT} rev-parse HEAD').read().strip()}\n"
            f"script            : code/scripts/round2_r2_fold_hvg.py\n"
            f"command_line      : {' '.join(sys.argv)}\n"
            f"config_hash       : foldhvg-k50-intercept-f64-cholesky-latent256\n"
            f"config            : head=Ridge(fit_intercept=True, solver=cholesky, float64), "
            f"alpha=100/(256*50); features=StandardScaler->PCA(256,random_state=1) train only; "
            f"gene selection=get_k_genes(criteria=var,k=50,min_cells_pct=0.10) on TRAINING "
            f"samples only; metrics=pooled and within-slide Pearson\n"
            f"gate              : requires round2_r2_gene_check.py exact reproduction (D2)\n"
            f"decisions         : round2_R1_decisions.md directive D2\n")
print(f"\nwrote {OUT}/fold_hvg__{enc}.csv ({len(d)} rows)")
