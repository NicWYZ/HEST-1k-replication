#!/usr/bin/env python
"""Prove that inference_dump.pkl rows can be mapped back to (sample_id, barcode).

Stage: faithful replication stage 4, row-identity check between the joined tables and their sources.

inference_dump.pkl stores only preds_all / targets_all. benchmark.py builds the test
matrix by reading barcodes from each test sample's embedding HDF5 and indexing
adata[barcodes], so row order == concatenation of embedding-file barcode order over the
test samples listed in splits/test_<k>.csv.

This script reconstructs targets_all from the AnnData independently and compares. If the
reconstruction is exact, the row mapping is proven and Stage 4a can rely on it.
"""
import os, glob, json, pickle
import numpy as np, pandas as pd, h5py, anndata as ad, scanpy as sc

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD   = f"{ROOT}/bench_data"
EMB  = f"{ROOT}/embeddings"   # layout: embeddings/<task>/<encoder>/<sample>.h5

def barcodes_of(path):
    with h5py.File(path, "r") as f:
        k = "barcodes" if "barcodes" in f else "barcode"
        b = np.asarray(f[k][:]).reshape(-1)
    return [x.decode() if isinstance(x,(bytes,np.bytes_)) else str(x) for x in b]

def rebuild(task, encoder, split):
    test = pd.read_csv(f"{BD}/{task}/splits/test_{split}.csv")
    genes = json.load(open(f"{BD}/{task}/var_50genes.json"))["genes"]
    ids, bcs, mats = [], [], []
    for _, row in test.iterrows():
        sid = os.path.basename(row["expr_path"]).replace(".h5ad","")
        bc  = barcodes_of(f"{EMB}/{task}/{encoder}/{sid}.h5")
        A   = ad.read_h5ad(f"{BD}/{task}/adata/{sid}.h5ad")
        sc.pp.log1p(A)                       # benchmark: normalize=True -> log1p only
        sub = A[bc, genes]
        X = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
        mats.append(np.asarray(X, dtype=np.float64))
        ids += [sid]*len(bc); bcs += bc
    return np.vstack(mats), ids, bcs, genes

rows = []
CASES = [("IDC","resnet50"), ("PRAD","resnet50"), ("CCRCC","phikon"), ("SKCM","uni_v1")]
for task, enc in CASES:
    dumps = sorted(glob.glob(f"{ROOT}/results/faithful/faithful_pca_ridge__{enc}*/{task}/{enc}/split*/inference_dump.pkl"))
    for dp in dumps:
        k = int(dp.split("split")[-1].split("/")[0])
        d = pickle.load(open(dp,"rb"))
        T = d["targets_all"]
        R, ids, bcs, genes = rebuild(task, enc, k)
        ok_shape = R.shape == T.shape
        maxdiff = float(np.max(np.abs(R - T))) if ok_shape else np.nan
        rows.append(dict(task=task, encoder=enc, split=k, dump_rows=T.shape[0],
                         rebuilt_rows=R.shape[0], shape_match=ok_shape,
                         max_abs_diff=maxdiff, exact=bool(ok_shape and maxdiff < 1e-9),
                         n_samples=len(set(ids))))
        print(f"{task:10s} {enc:9s} split{k}  dump={T.shape}  rebuilt={R.shape}  "
              f"max|diff|={maxdiff:.3e}  exact={rows[-1]['exact']}", flush=True)

df = pd.DataFrame(rows)
df.to_csv(f"{ROOT}/results/tailored/integrity/row_identity_check.csv", index=False)
print()
print("cases checked      :", len(df))
print("all shapes match   :", bool(df.shape_match.all()))
print("all exact (<1e-9)  :", bool(df.exact.all()))
print("worst max|diff|    :", float(df.max_abs_diff.max()))
