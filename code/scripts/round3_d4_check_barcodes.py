#!/usr/bin/env python
"""D4 integrity check: are the expression files' barcode indexes unique, and would selecting the
patch barcode list return exactly one row per patch barcode?

anndata warned "Observation names are not unique" while reading hest_ext st files in the D4 smoke
run. Every D4 arm, and the harness's own load_task, select expression rows by
`A[patch_barcodes, genes]`, which with a duplicated obs index returns one row per MATCH and would
misalign Y against X. This checks it per sample, from the obs index alone (backed read, no
expression matrix loaded), so the row count that selection WOULD return is the sum over the patch
barcodes of their multiplicity in the obs index.
"""
import glob, os
import anndata as ad, h5py, numpy as np, pandas as pd

ROOT = "/work/users/w/e/weiyang/hest_replication"


def obs_var_index(p):
    A = ad.read_h5ad(p, backed="r")
    obs = pd.Index([str(x) for x in A.obs_names])
    var = pd.Index([str(x) for x in A.var_names])
    try:
        A.file.close()
    except Exception:
        pass
    return obs, var


def patch_bc(p):
    with h5py.File(p, "r") as f:
        k = "barcode" if "barcode" in f else "barcodes"
        b = np.asarray(f[k][:]).reshape(-1)
    return [x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in b]


rows = []
jobs = [("kidney_visium_cell", f"{ROOT}/hest_ext/kidney_visium_cell"),
        ("institution_breast_xenium", f"{ROOT}/hest_ext/institution_breast_xenium")]
for setname, base in jobs:
    for p in sorted(glob.glob(f"{base}/st/*.h5ad")):
        sid = os.path.basename(p)[:-5]
        obs, var = obs_var_index(p)
        pbc = patch_bc(f"{base}/patches/{sid}.h5")
        mult = obs.value_counts()
        would = int(sum(int(mult.get(b, 0)) for b in pbc))
        rows.append(dict(set=setname, sample_id=sid, n_obs=len(obs),
                         n_obs_unique=int(obs.nunique()), obs_unique=bool(obs.is_unique),
                         n_patch=len(pbc), n_patch_unique=len(set(pbc)),
                         n_rows_selection_would_return=would,
                         one_row_per_patch_barcode=bool(would == len(pbc)),
                         var_unique=bool(var.is_unique), n_var=len(var)))
for task in ("CCRCC", "IDC"):
    for p in sorted(glob.glob(f"{ROOT}/bench_data/{task}/adata/*.h5ad")):
        sid = os.path.basename(p)[:-5]
        obs, var = obs_var_index(p)
        pbc = patch_bc(f"{ROOT}/bench_data/{task}/patches/{sid}.h5")
        mult = obs.value_counts()
        would = int(sum(int(mult.get(b, 0)) for b in pbc))
        rows.append(dict(set=f"bench_{task}", sample_id=sid, n_obs=len(obs),
                         n_obs_unique=int(obs.nunique()), obs_unique=bool(obs.is_unique),
                         n_patch=len(pbc), n_patch_unique=len(set(pbc)),
                         n_rows_selection_would_return=would,
                         one_row_per_patch_barcode=bool(would == len(pbc)),
                         var_unique=bool(var.is_unique), n_var=len(var)))
D = pd.DataFrame(rows)
D.to_csv("d4_barcode_integrity.csv", index=False)
bad = D[~D.one_row_per_patch_barcode | ~D.obs_unique | ~D.var_unique
        | (D.n_patch != D.n_patch_unique)]
print(f"{len(D)} samples checked; {len(bad)} with a problem")
print(bad.to_string(index=False) if len(bad) else
      "no duplicated obs_names, no duplicated patch barcodes, no duplicated var_names, and "
      "selecting the patch barcode list returns exactly one row per barcode on every sample")
print(D.groupby("set")[["obs_unique", "var_unique", "one_row_per_patch_barcode"]].all().to_string())
pq = sorted(glob.glob(f"{ROOT}/results/round3/A1_coverage/pergene__*.parquet"))
print("\nA1 pergene parquets on disk:", [os.path.basename(x) for x in pq][:14])
