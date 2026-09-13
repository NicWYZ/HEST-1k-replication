#!/usr/bin/env python
"""Stage 1 inventory of MahmoodLab/hest-bench. Verifies structure against the
HEST replication handoff expectations. Writes INVENTORY.md + inventory.json."""
import os, json, glob, sys
import numpy as np, h5py, anndata as ad, pandas as pd

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD   = os.path.join(ROOT, "bench_data")
OUT  = BD

def is_integral(x):
    x = np.asarray(x, dtype=np.float64)
    if x.size == 0: return None
    return bool(np.all(np.isfinite(x)) and np.all(x == np.round(x)))

tasks = sorted([d for d in os.listdir(BD)
                if os.path.isdir(os.path.join(BD,d)) and not d.startswith('.')])
report = {}

for t in tasks:
    td = os.path.join(BD, t)
    info = {"task": t}
    info["subdirs"] = sorted([d for d in os.listdir(td) if os.path.isdir(os.path.join(td,d))])
    info["loose_files"] = sorted([f for f in os.listdir(td) if os.path.isfile(os.path.join(td,f))])

    adatas  = sorted(glob.glob(os.path.join(td, "adata", "*.h5ad")))
    patches = sorted(glob.glob(os.path.join(td, "patches", "*.h5")))
    splits  = sorted(glob.glob(os.path.join(td, "splits", "*.csv")))
    jsons   = sorted(glob.glob(os.path.join(td, "*.json")))
    info["n_adata"], info["n_patches"], info["n_splits"], info["jsons"] = \
        len(adatas), len(patches), len(splits), [os.path.basename(j) for j in jsons]
    info["sample_ids"] = [os.path.basename(p).replace(".h5ad","") for p in adatas]

    # ---- gene list ----
    gl = None
    for j in jsons:
        try:
            d = json.load(open(j))
        except Exception:
            continue
        if isinstance(d, dict) and "genes" in d:
            gl = d["genes"]; info["gene_list_file"] = os.path.basename(j); break
        if isinstance(d, list) and len(d) and isinstance(d[0], str):
            gl = d; info["gene_list_file"] = os.path.basename(j); break
    info["n_genes_in_list"] = len(gl) if gl is not None else None
    info["genes_head"] = gl[:5] if gl else None

    # ---- per-sample adata + patch checks ----
    per = []
    for p in adatas:
        sid = os.path.basename(p).replace(".h5ad","")
        rec = {"sample_id": sid}
        try:
            A = ad.read_h5ad(p, backed="r")
            rec["n_spots"], rec["n_vars"] = int(A.shape[0]), int(A.shape[1])
            X = A.X[:min(500, A.shape[0])]
            X = X.toarray() if hasattr(X, "toarray") else np.asarray(X)
            rec["X_dtype"] = str(X.dtype)
            rec["X_is_integer"] = is_integral(X)
            rec["X_min"], rec["X_max"] = float(np.min(X)), float(np.max(X))
            rec["obs_cols"] = list(A.obs.columns)[:12]
            bc_adata = list(map(str, A.obs_names[:]))
            rec["n_obs_names"] = len(bc_adata)
            try: A.file.close()
            except Exception: pass
        except Exception as e:
            rec["adata_error"] = f"{type(e).__name__}: {e}"; bc_adata = None

        hp = os.path.join(td, "patches", sid + ".h5")
        if os.path.exists(hp):
            try:
                with h5py.File(hp, "r") as f:
                    rec["patch_keys"] = list(f.keys())
                    if "img" in f:  rec["img_shape"] = list(f["img"].shape); rec["img_dtype"] = str(f["img"].dtype)
                    if "coords" in f: rec["coords_shape"] = list(f["coords"].shape)
                    bkey = next((k for k in ("barcode","barcodes") if k in f), None)
                    if bkey:
                        b = f[bkey][:]
                        b = np.asarray(b).reshape(-1)
                        bc_h5 = [x.decode() if isinstance(x,(bytes,np.bytes_)) else str(x) for x in b]
                        rec["n_barcodes_h5"] = len(bc_h5)
                        if bc_adata is not None:
                            rec["barcodes_match_exact"]  = bool(bc_h5 == bc_adata)
                            rec["barcodes_match_asset"]  = bool(set(bc_h5) == set(bc_adata))
                    else:
                        rec["barcode_key"] = None
            except Exception as e:
                rec["patch_error"] = f"{type(e).__name__}: {e}"
        else:
            rec["patch_error"] = "missing patch h5"
        per.append(rec)
    info["samples"] = per
    info["total_spots"] = int(sum(r.get("n_spots",0) for r in per))

    # ---- splits ----
    sp = []
    for s in splits:
        try:
            df = pd.read_csv(s)
            sp.append({"file": os.path.basename(s), "n_rows": int(len(df)),
                       "cols": list(df.columns)})
        except Exception as e:
            sp.append({"file": os.path.basename(s), "error": str(e)})
    info["splits"] = sp
    report[t] = info
    print(f"[done] {t}: {len(adatas)} samples, {info['total_spots']} spots, "
          f"{info['n_genes_in_list']} genes, {len(splits)} split files", flush=True)

json.dump(report, open(os.path.join(OUT,"inventory.json"),"w"), indent=1)

# ---------- markdown ----------
L = ["# hest-bench INVENTORY", "",
     f"Generated: {pd.Timestamp.now().isoformat()}",
     f"Source: HuggingFace `MahmoodLab/hest-bench` snapshot at `{BD}`", "",
     "## Per-task summary", "",
     "| task | n_samples | total_spots | n_genes | n_split_files | patch shape | X integer? |",
     "|---|---|---|---|---|---|---|"]
for t, i in report.items():
    shp = next((r.get("img_shape") for r in i["samples"] if r.get("img_shape")), None)
    shp = "x".join(map(str, shp[1:])) if shp else "?"
    ints = {r.get("X_is_integer") for r in i["samples"]}
    ints = "yes" if ints=={True} else ("no" if False in ints else "mixed/err")
    L.append(f"| {t} | {i['n_adata']} | {i['total_spots']} | {i['n_genes_in_list']} | "
             f"{i['n_splits']} | {shp} | {ints} |")
L += ["", "## Barcode agreement (patch HDF5 vs adata.obs_names)", "",
      "| task | samples exact-order match | samples set match |", "|---|---|---|"]
for t, i in report.items():
    ex = sum(1 for r in i["samples"] if r.get("barcodes_match_exact"))
    st = sum(1 for r in i["samples"] if r.get("barcodes_match_asset"))
    L.append(f"| {t} | {ex}/{i['n_adata']} | {st}/{i['n_adata']} |")
L += ["", "## Split files", ""]
for t, i in report.items():
    L.append(f"**{t}** ({i['n_splits']} files): " +
             ", ".join(f"{s['file']}({s.get('n_rows','?')})" for s in i["splits"]))
    L.append("")
open(os.path.join(OUT,"INVENTORY.md"),"w").write("\n".join(L))
print("INVENTORY_WRITTEN")
