#!/usr/bin/env python
"""Stage 4a: join predictions to spot identity, covariates and raw counts.

Row identity in inference_dump.pkl is reconstructed from splits/test_<k>.csv plus the
barcode order in each embedding HDF5. That mapping is PROVEN in
instrumentation/row_identity_check.csv: reconstructing targets_all independently agrees to
4.4e-7 (below float32 eps x max value = 9.6e-7) while any row permutation registers ~8.0.

Writes, per task, under instrumentation/<task>/:
  spots.parquet  one row per (sample_id, barcode): fold, coords, spot covariates,
                 raw integer counts and log1p targets for the task's 50 genes (long in gene)
  preds.parquet  one row per (encoder, sample_id, barcode, gene): prediction + target
Genes differ per task, so long-in-gene is used rather than 50 wide columns.
"""
import os, glob, json, pickle, sys
import numpy as np, pandas as pd, h5py, anndata as ad, scanpy as sc

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, EMB, RES = f"{ROOT}/bench_data", f"{ROOT}/embeddings", f"{ROOT}/results/faithful"
OUT = f"{ROOT}/instrumentation"
HEAD = "faithful_pca_ridge"

def read_emb(path):
    with h5py.File(path, "r") as f:
        k = "barcodes" if "barcodes" in f else "barcode"
        b = np.asarray(f[k][:]).reshape(-1)
        bc = [x.decode() if isinstance(x,(bytes,np.bytes_)) else str(x) for x in b]
        co = f["coords"][:] if "coords" in f else np.full((len(bc),2), -1)
    return bc, co

def encoders_for(task):
    out = []
    for d in sorted(glob.glob(f"{RES}/{HEAD}__*")):
        enc = os.path.basename(d).split("__")[1].split("::")[0]
        if glob.glob(f"{d}/{task}/{enc}/split*/inference_dump.pkl"):
            out.append((enc, d))
    return out

tasks = sorted([d for d in os.listdir(BD) if os.path.isdir(f"{BD}/{d}") and not d.startswith('.')])
# smallest task first: a failure surfaces in seconds rather than after the 24-sample task,
# and a partial run still leaves usable output for most tasks
tasks.sort(key=lambda t: len(glob.glob(f"{BD}/{t}/adata/*.h5ad")))
summary = []

for task in tasks:
    genes = json.load(open(f"{BD}/{task}/var_50genes.json"))["genes"]
    splits = sorted(glob.glob(f"{BD}/{task}/splits/test_*.csv"))
    encs = encoders_for(task)
    if not encs:
        print(f"[skip] {task}: no dumps", flush=True); continue

    # ---- spot-level table, walking folds in the same order the benchmark did ----
    spot_rows, order = [], {}     # order[(fold)] = list of (sid, bc) in dump-row order
    for sp in splits:
        k = int(os.path.basename(sp).split("_")[1].split(".")[0])
        test = pd.read_csv(sp)
        seq = []
        for _, row in test.iterrows():
            sid = os.path.basename(row["expr_path"]).replace(".h5ad","")
            bc, co = read_emb(f"{EMB}/{task}/{encs[0][0]}/{sid}.h5")
            A = ad.read_h5ad(f"{BD}/{task}/adata/{sid}.h5ad")
            raw = A[bc, genes]
            Xr = raw.X.toarray() if hasattr(raw.X,"toarray") else np.asarray(raw.X)
            Xr = np.asarray(Xr, dtype=np.float64)
            tot = np.asarray(A[bc].X.sum(axis=1)).ravel()
            ndet = np.asarray((A[bc].X > 0).sum(axis=1)).ravel()
            sc.pp.log1p(A)
            lg = A[bc, genes]
            Xl = lg.X.toarray() if hasattr(lg.X,"toarray") else np.asarray(lg.X)
            Xl = np.asarray(Xl, dtype=np.float64)
            obs = A.obs.loc[bc]
            in_t = obs["in_tissue"].values if "in_tissue" in obs.columns else np.full(len(bc), np.nan)
            nb = len(bc)
            spot_rows.append(pd.DataFrame({
                "task": task, "fold": k, "sample_id": sid,
                "barcode": np.repeat(bc, len(genes)),
                "gene": np.tile(genes, nb),
                "count": Xr.ravel(), "target": Xl.ravel(),
                "x": np.repeat(co[:,0], len(genes)), "y": np.repeat(co[:,1], len(genes)),
                "spot_total_counts": np.repeat(tot, len(genes)),
                "spot_n_genes_detected": np.repeat(ndet, len(genes)),
                "in_tissue": np.repeat(in_t, len(genes)),
            }))
            seq += [(sid, b) for b in bc]
        order[k] = seq
    spots = pd.concat(spot_rows, ignore_index=True)
    for col in ("task","sample_id","barcode","gene"):
        spots[col] = spots[col].astype("category")
    for col in ("count","target","spot_total_counts"):
        spots[col] = spots[col].astype(np.float32)

    # ---- predictions, one block per (encoder, fold) ----
    pred_rows = []
    for enc, edir in encs:
        for dp in sorted(glob.glob(f"{edir}/{task}/{enc}/split*/inference_dump.pkl")):
            k = int(dp.split("split")[-1].split("/")[0])
            d = pickle.load(open(dp,"rb"))
            P, T = d["preds_all"], d["targets_all"]
            seq = order[k]
            assert P.shape[0] == len(seq), f"{task}/{enc}/split{k}: {P.shape[0]} rows vs {len(seq)} barcodes"
            assert P.shape[1] == len(genes), f"{task}/{enc}/split{k}: {P.shape[1]} cols vs {len(genes)} genes"
            sid_arr = np.repeat([s for s,_ in seq], len(genes))
            bc_arr  = np.repeat([b for _,b in seq], len(genes))
            pred_rows.append(pd.DataFrame({
                "task": task, "encoder": enc, "fold": k,
                "sample_id": sid_arr, "barcode": bc_arr,
                "gene": np.tile(genes, len(seq)),
                "pred": P.ravel().astype(np.float32),
                "target": T.ravel().astype(np.float32),
            }))
    preds = pd.concat(pred_rows, ignore_index=True)
    for col in ("task","encoder","sample_id","barcode","gene"):
        preds[col] = preds[col].astype("category")

    # ---- integrity: dumped targets must equal the independently built targets ----
    # Checked per (encoder, fold) block against the spot table's own target column, keyed on
    # (sample_id, barcode, gene). Done blockwise rather than as one merge over all encoders:
    # the full join would materialise ~40M rows twice for the largest task.
    key = spots.set_index(["sample_id","barcode","gene"])["target"]
    worst = 0.0
    for (enc_, k_), blk in preds.groupby(["encoder","fold"], observed=True, sort=False):
        ref = key.reindex(pd.MultiIndex.from_arrays(
            [blk.sample_id.astype(str), blk.barcode.astype(str), blk.gene.astype(str)]))
        assert ref.notna().all(), f"{task}/{enc_}/split{k_}: unmatched prediction rows"
        worst = max(worst, float(np.max(np.abs(blk.target.to_numpy(np.float64) - ref.to_numpy()))))
    del key

    os.makedirs(f"{OUT}/{task}", exist_ok=True)
    for df_, nm in ((spots,"spots"), (preds,"preds")):
        df_.to_parquet(f"{OUT}/{task}/{nm}.parquet", index=False, compression="snappy")
    # unique (sample_id, barcode) pairs -- NOT barcode.nunique(), which counts barcode
    # strings and undercounts badly: Xenium tasks reuse pseudo-Visium grid barcodes
    # (000x002 etc.) in every sample, and Visium barcodes recur across samples.
    n_spot_pairs = (spots.sample_id.astype(str) + "|" + spots.barcode.astype(str)).nunique()
    summary.append(dict(task=task, n_spots=n_spot_pairs, n_genes=len(genes),
                        n_folds=len(splits), n_encoders=len(encs),
                        spot_rows=len(spots), pred_rows=len(preds),
                        target_max_abs_diff=worst))
    print(f"[done] {task}: {n_spot_pairs} spots x {len(genes)} genes x "
          f"{len(encs)} encoders -> {len(preds):,} pred rows, target max|diff|={worst:.2e}", flush=True)
    del spots, preds, spot_rows, pred_rows

s = pd.DataFrame(summary)
s.to_csv(f"{OUT}/stage4a_summary.csv", index=False)
print()
print(s.to_string(index=False))
print("\ntotal prediction rows:", f"{int(s.pred_rows.sum()):,}")
print("worst target discrepancy across all tasks:", f"{s.target_max_abs_diff.max():.2e}")
