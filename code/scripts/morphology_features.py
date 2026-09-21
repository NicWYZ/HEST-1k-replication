#!/usr/bin/env python
"""Stage 4e (v2): per-spot CellViT morphology features over the ACTUAL patch the encoder saw.

Stage: tailored analysis, per-spot nuclear morphology (v1); superseded by morphology_features_v2.py.

handoff 4e asks for nuclei "within the 112um patch". v1 of this script assigned each nucleus to
its nearest spot within half the spot-grid pitch. That was wrong in two ways, both found by
reading the patch HDF5 attributes rather than inferring geometry:

1. WRONG REGION. The patch extent in WSI pixels is 224 * factor, where `factor` is stored as an
   attribute on the patches/<sample>.h5 'img' dataset. It is NOT half the spot pitch. Across the
   benchmark the patch is consistently ~1.12x the spot spacing, so a pitch/2 radius under-covered
   the patch and also used a disc where the patch is a square. The morphology features must
   describe the same pixels the encoder embedded, otherwise the join to predictions relates two
   different image regions.
   The `patch_size` attribute is NOT reliable: it records the source extent for 68 of 72 samples
   and the OUTPUT size (224) for the other 4, so reading it directly would put a 224px box where
   409px was correct. 224 * factor is consistent for all 72.
   Verified against the metadata across all 72 samples (patch_scale_sources.csv):
     112 / pixel_size_um_estimated  -- agrees with 224*factor to 0.000 px on 72/72, i.e. `factor`
                                       IS this quantity; either source is correct
     112 / pixel_size_um_embedded   -- present for 45/72 only and disagrees by up to 415 px on 4
                                       of those, so the embedded scan metadata is sometimes wrong
                                       and HEST used the estimated value
     inter_spot_dist                -- populated for the 57 Visium samples, empty for all 15
                                       Xenium ones, so unusable as a general scale source
   The patch attribute is preferred simply because it is the value the extraction actually used,
   so it cannot drift from the pixels the encoder saw. Patch extents span 244-818 px across the
   benchmark (PAAD/TENX116 is scanned at 0.137 um/px), which is why no constant works.

2. NUCLEI CAN BELONG TO SEVERAL SPOTS. Because patches are ~1.12x the spot spacing, adjacent
   patches OVERLAP. A nucleus in an overlap region was genuinely inside both patches and was seen
   by the encoder for both spots, so it must count toward both. v1's nearest-spot assignment gave
   each nucleus to exactly one spot, undercounting in overlap regions.

So: for each spot, every nucleus whose centroid lies in the square [cx +- 112*factor,
cy +- 112*factor]. Implemented as a KD-tree ball query at the circumscribing radius followed by
an exact box filter, chunked so the dense samples (COAD averages ~214 nuclei per spot) stay in
memory.
"""
import os, glob, sys
import numpy as np, pandas as pd, anndata as ad, h5py
import geopandas as gpd
from scipy.spatial import cKDTree
from huggingface_hub import hf_hub_download

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, OUT = f"{ROOT}/bench_data", f"{ROOT}/results/tailored/morphology"
DATA = f"{ROOT}/instrumentation"   # gitignored: per-task morphology parquet
EXPECTED = {"neoplastic","inflammatory","connective","epithelial","dead"}
CHUNK = 20000
os.makedirs(f"{DATA}/morphology", exist_ok=True)

tasks = sorted([d for d in os.listdir(BD) if os.path.isdir(f"{BD}/{d}") and not d.startswith('.')])
if len(sys.argv) > 1:
    tasks = [t for t in tasks if t in sys.argv[1].split(",")]

summary = []
for task in tasks:
    out_p = f"{DATA}/morphology/{task}_morph.parquet"
    if os.path.isfile(out_p):
        print(f"[skip] {task}: exists", flush=True); continue
    frames = []
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        sid = os.path.basename(p)[:-5]
        # patch geometry, straight from the file the benchmark actually read
        with h5py.File(f"{BD}/{task}/patches/{sid}.h5", "r") as f:
            at = dict(f["img"].attrs)
            factor = float(at["factor"])
            pbar = np.asarray(f["barcode"][:]).reshape(-1)
            patch_bc = set(x.decode() if isinstance(x,(bytes,np.bytes_)) else str(x) for x in pbar)
        half = 112.0 * factor          # patch half-width in WSI pixels
        assert half > 0

        try:
            fp = hf_hub_download("MahmoodLab/hest", f"cellvit_seg/{sid}_cellvit_seg.parquet",
                                 repo_type="dataset", cache_dir=os.environ.get("HF_HOME"))
        except Exception as e:
            print(f"[warn] {task}/{sid}: cellvit unavailable ({type(e).__name__})", flush=True); continue
        nuc = gpd.read_parquet(fp)
        assert nuc.geometry.notna().all(), f"{sid}: null geometry"
        cls = nuc["class"].astype(str).str.lower().to_numpy()
        unknown = set(np.unique(cls)) - EXPECTED
        assert not unknown, f"{sid}: unexpected classes {unknown}"
        cent = nuc.geometry.centroid
        cx, cy = cent.x.to_numpy(), cent.y.to_numpy()
        area = nuc.geometry.area.to_numpy()
        assert (area > 0).all(), f"{sid}: non-positive area"

        A = ad.read_h5ad(p, backed="r")
        bc = np.asarray(A.obs_names[:], dtype=object)
        xy = np.asarray(A.obsm["spatial"], dtype=np.float64)
        try: A.file.close()
        except Exception: pass

        tree = cKDTree(np.c_[cx, cy])
        recs = []
        for s0 in range(0, len(xy), CHUNK):
            block = xy[s0:s0+CHUNK]
            balls = tree.query_ball_point(block, r=half*np.sqrt(2.0), workers=-1)
            for li, idxs in enumerate(balls):
                if not idxs: continue
                ii = np.asarray(idxs)
                inbox = (np.abs(cx[ii]-block[li,0]) <= half) & (np.abs(cy[ii]-block[li,1]) <= half)
                ii = ii[inbox]
                if ii.size == 0: continue
                a_, c_ = area[ii], cls[ii]
                rec = dict(spot=s0+li, n_nuclei=int(ii.size),
                           area_mean=float(a_.mean()), area_median=float(np.median(a_)))
                for k_ in sorted(EXPECTED):
                    rec[f"frac_{k_}"] = float((c_ == k_).mean())
                neo = a_[c_ == "neoplastic"]
                rec["n_neoplastic"] = int(neo.size)
                rec["neo_area_mean"] = float(neo.mean()) if neo.size else np.nan
                recs.append(rec)
        feat = pd.DataFrame(recs).set_index("spot") if recs else pd.DataFrame()
        full = pd.DataFrame(index=np.arange(len(xy))).join(feat)
        full.insert(0, "barcode", bc); full.insert(0, "sample_id", sid); full.insert(0, "task", task)
        full["in_patch_set"] = [b in patch_bc for b in bc]   # the 4a join key subset
        for col in ("n_nuclei","n_neoplastic"):
            full[col] = full[col].fillna(0).astype(int)
        frames.append(full.reset_index(drop=True))

        n_assigned = int(full.n_nuclei.sum())
        summary.append(dict(task=task, sample_id=sid, n_spots=len(xy), n_patch_spots=len(patch_bc),
                            n_nuclei=len(nuc), factor=factor, patch_px=2*half,
                            nucleus_spot_pairs=n_assigned,
                            spots_with_nuclei=int((full.n_nuclei > 0).sum()),
                            mean_nuclei_per_spot=float(full.n_nuclei.mean()),
                            classes="|".join(sorted(np.unique(cls)))))
        print(f"  {task}/{sid}: {len(nuc):,} nuclei, patch {2*half:.0f}px (factor {factor:.4f}), "
              f"{n_assigned:,} nucleus-spot pairs, "
              f"{int((full.n_nuclei>0).sum())}/{len(xy)} spots covered", flush=True)
    if frames:
        out = pd.concat(frames, ignore_index=True)
        out.to_parquet(out_p, index=False)
        print(f"[done] {task}: {len(out):,} spot rows -> {out_p}", flush=True)

if summary:
    s = pd.DataFrame(summary)
    s.to_csv(f"{OUT}/morphology_summary__{'_'.join(tasks)}.csv", index=False)
    print("\n" + s.to_string(index=False))
