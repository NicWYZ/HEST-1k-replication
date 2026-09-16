#!/usr/bin/env python
"""Stage 4e: per-spot CellViT morphology features for all benchmark samples.

handoff 4e: "per spot compute nuclear count, mean and median nuclear area, and the fraction of
nuclei in each of the five CellViT classes within the 112um patch. Join to 4a."

Coordinate handling is the validated version from fig3e_gate.py, which reproduced HEST Figure 3.e
at r=0.4578 vs the paper's 0.47 on NCBI785. Two points carried over, both load-bearing:

  * NO micron conversion. CellViT polygons and adata.obsm['spatial'] share the WSI pixel space,
    and the v1.1.0 metadata ships no pixel-size column. The spot territory radius is calibrated
    per sample from that sample's own median nearest-neighbour spot spacing, which varies widely
    even within one task (IDC: 275-471 px across four samples), so a constant would be wrong.
  * Area and centroid are DERIVED from the polygon via geopandas; the parquet stores only
    geometry, class and cell_id.

The five classes are taken from the data rather than hardcoded, and asserted to be a subset of
the expected set so a CellViT version change surfaces as an error instead of silent NaN columns.
"""
import os, glob, sys
import numpy as np, pandas as pd, anndata as ad
import geopandas as gpd
from scipy.spatial import cKDTree
from huggingface_hub import hf_hub_download

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, OUT = f"{ROOT}/bench_data", f"{ROOT}/instrumentation"
SPOT_FRAC = 0.5
EXPECTED = {"neoplastic","inflammatory","connective","epithelial","dead"}
os.makedirs(f"{OUT}/morphology", exist_ok=True)

tasks = sorted([d for d in os.listdir(BD) if os.path.isdir(f"{BD}/{d}") and not d.startswith('.')])
if len(sys.argv) > 1:
    tasks = [t for t in tasks if t in sys.argv[1].split(",")]

summary = []
for task in tasks:
    out_p = f"{OUT}/morphology/{task}_morph.parquet"
    if os.path.isfile(out_p):
        print(f"[skip] {task}: exists", flush=True); continue
    frames = []
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        sid = os.path.basename(p)[:-5]
        try:
            f = hf_hub_download("MahmoodLab/hest", f"cellvit_seg/{sid}_cellvit_seg.parquet",
                                repo_type="dataset", cache_dir=os.environ.get("HF_HOME"))
        except Exception as e:
            print(f"[warn] {task}/{sid}: cellvit unavailable ({type(e).__name__})", flush=True)
            continue
        nuc = gpd.read_parquet(f)
        assert nuc.geometry.notna().all(), f"{sid}: null geometry"
        cls = nuc["class"].astype(str).str.lower()
        unknown = set(cls.unique()) - EXPECTED
        assert not unknown, f"{sid}: unexpected CellViT classes {unknown}"
        cent = nuc.geometry.centroid
        cx, cy, area = cent.x.to_numpy(), cent.y.to_numpy(), nuc.geometry.area.to_numpy()
        assert (area > 0).all(), f"{sid}: non-positive area"

        A = ad.read_h5ad(p, backed="r")
        bc = np.asarray(A.obs_names[:], dtype=object)
        xy = np.asarray(A.obsm["spatial"], dtype=np.float64)
        try: A.file.close()
        except Exception: pass

        tree = cKDTree(xy)
        nn, _ = tree.query(xy, k=2)
        pitch = float(np.median(nn[:, 1])); radius = SPOT_FRAC * pitch
        d, j = tree.query(np.c_[cx, cy], k=1)
        keep = d <= radius
        assert keep.any(), f"{sid}: no nucleus fell inside any spot territory"

        df = pd.DataFrame(dict(spot=j[keep], area=area[keep], cls=cls.to_numpy()[keep]))
        g = df.groupby("spot")
        feat = pd.DataFrame(dict(n_nuclei=g.size(), area_mean=g.area.mean(), area_median=g.area.median()))
        # class fractions: reindexed over the full expected set so every sample has every column
        fr = (df.pivot_table(index="spot", columns="cls", values="area", aggfunc="size")
                .reindex(columns=sorted(EXPECTED)).fillna(0.0))
        fr = fr.div(fr.sum(axis=1).replace(0, np.nan), axis=0)
        fr.columns = [f"frac_{c}" for c in fr.columns]
        feat = feat.join(fr)
        # neoplastic-only area, the quantity Figure 3.e uses
        neo = df[df.cls == "neoplastic"].groupby("spot").area
        feat["neo_area_mean"] = neo.mean(); feat["n_neoplastic"] = neo.size()

        full = pd.DataFrame(index=np.arange(len(xy))).join(feat)
        full.insert(0, "barcode", bc); full.insert(0, "sample_id", sid); full.insert(0, "task", task)
        full["n_nuclei"] = full.n_nuclei.fillna(0).astype(int)
        full["n_neoplastic"] = full.n_neoplastic.fillna(0).astype(int)
        frames.append(full.reset_index(drop=True))
        summary.append(dict(task=task, sample_id=sid, n_spots=len(xy), n_nuclei=len(nuc),
                            spot_pitch_px=pitch, frac_assigned=float(keep.mean()),
                            spots_with_nuclei=int((full.n_nuclei > 0).sum()),
                            classes="|".join(sorted(cls.unique()))))
        print(f"  {task}/{sid}: {len(nuc):,} nuclei, pitch {pitch:.0f}px, "
              f"{100*keep.mean():.0f}% assigned, {int((full.n_nuclei>0).sum())}/{len(xy)} spots covered",
              flush=True)
    if frames:
        out = pd.concat(frames, ignore_index=True)
        out.to_parquet(out_p, index=False)
        print(f"[done] {task}: {len(out):,} spot rows -> {out_p}", flush=True)

if summary:
    s = pd.DataFrame(summary)
    # ONE WRITER PER FILE. Five of these run concurrently, one per task group; appending to a
    # shared CSV would race on the header check and interleave rows. Each job writes its own
    # file keyed by its task list, and the reader concatenates the glob.
    tag = "_".join(tasks)
    s.to_csv(f"{OUT}/morphology_summary__{tag}.csv", index=False)
    print("\n" + s.to_string(index=False))
    print(f"\nsamples: {len(s)} | median pitch {s.spot_pitch_px.median():.0f}px "
          f"(range {s.spot_pitch_px.min():.0f}-{s.spot_pitch_px.max():.0f}) | "
          f"mean assigned {s.frac_assigned.mean():.3f}")
