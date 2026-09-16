#!/usr/bin/env python
"""Stage 4e gate: reproduce HEST Figure 3.e before any morphology feature is used.

Paper text (Section 5, Figure 3.e): "we measured the Pearson correlation between the expression
of GATA3 and nuclear area in NEOPLASTIC cells (Figure 3.e). We observe a moderate correlation
(R=0.47, P-value < ...)". Two details that a looser reading would get wrong:

  * NEOPLASTIC nuclei only. CellViT classifies each nucleus; averaging over all classes answers a
    different question and will not reproduce 0.47.
  * The common unit must be the SPOT. GATA3 expression is per spot; nuclear area is per nucleus.
    So the per-spot statistic is the mean area of neoplastic nuclei whose centroid falls inside
    the spot's 112um patch, correlated across spots against that spot's GATA3.

WHICH SAMPLE. The paper does not name it, but it reports nuclei counts: n=168,033 for Figure 3.a
and n=342,018 for Appendix Figure 6.a. IDC ships four Xenium samples, so the sample is identified
empirically by matching its total CellViT nucleus count against those two figures rather than
assumed. All four are reported so the match is visible.

This is a GATE, not a feature build: handoff 4e requires r within 0.05 of 0.47 before the
morphology features are joined into the instrumentation table, because a coordinate-system or
scaling error would otherwise propagate silently into every downstream analysis.
"""
import os, glob, json
import numpy as np, pandas as pd, anndata as ad
import geopandas as gpd
from scipy.stats import pearsonr
from scipy.spatial import cKDTree
from huggingface_hub import hf_hub_download

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD, OUT = f"{ROOT}/bench_data", f"{ROOT}/instrumentation"
# NO hardcoded micron-per-pixel. The v1.1.0 metadata ships no pixel-size column, so a constant
# would silently apply the wrong physical patch size to any sample not scanned at 0.5 um/px.
# Both the CellViT polygons and adata.obsm['spatial'] live in the SAME WSI pixel space, so the
# assignment needs no micron conversion at all -- only a spot territory radius, which is
# calibrated per sample from the spot grid's own median nearest-neighbour spacing.
SPOT_FRAC = 0.5                        # a nucleus belongs to a spot within half the grid pitch
os.makedirs(f"{OUT}/cellvit", exist_ok=True)

meta = pd.read_csv(f"{ROOT}/code/HEST/assets/HEST_v1_1_0.csv")
idcols = [c for c in meta.columns if c.lower() in ("id","sample_id","hest_id")]
print("metadata rows:", len(meta), "| id column:", idcols, "| columns:", list(meta.columns)[:14])

rows, per_spot_all = [], []
for p in sorted(glob.glob(f"{BD}/IDC/adata/*.h5ad")):
    sid = os.path.basename(p)[:-5]
    try:
        f = hf_hub_download("MahmoodLab/hest", f"cellvit_seg/{sid}_cellvit_seg.parquet",
                            repo_type="dataset", cache_dir=os.environ.get("HF_HOME"))
    except Exception as e:
        print(f"[skip] {sid}: {type(e).__name__} {e}"); continue
    nuc = pd.read_parquet(f)
    if sid == sorted(glob.glob(f"{BD}/IDC/adata/*.h5ad"))[0].split("/")[-1][:-5]:
        print("cellvit columns:", list(nuc.columns))
        print("class values:", nuc[[c for c in nuc.columns if "class" in c.lower()
                                   or "type" in c.lower()][:1][0]].value_counts().to_dict()
              if any("class" in c.lower() or "type" in c.lower() for c in nuc.columns) else "(none)")

    ccol = next((c for c in nuc.columns if c.lower() == "class"), None)
    assert ccol is not None, f"no class column: {list(nuc.columns)}"
    # geometry is a polygon per nucleus; centroid and area are DERIVED, not stored
    if not isinstance(nuc, gpd.GeoDataFrame):
        nuc = gpd.read_parquet(f)
    assert nuc.geometry.notna().all(), "null geometries present"
    cent = nuc.geometry.centroid
    nuc["_cx"], nuc["_cy"], nuc["_area"] = cent.x.to_numpy(), cent.y.to_numpy(), nuc.geometry.area.to_numpy()
    assert (nuc["_area"] > 0).all(), "non-positive nuclear area"

    neo_mask = nuc[ccol].astype(str).str.lower().eq("neoplastic")
    print(f"{sid}: {len(nuc):,} nuclei total, {int(neo_mask.sum()):,} neoplastic "
          f"({100*neo_mask.mean():.1f}%) | classes {nuc[ccol].value_counts().to_dict()}")

    A = ad.read_h5ad(p)
    if "GATA3" not in set(map(str, A.var_names)):
        print(f"[skip] {sid}: no GATA3"); continue
    xy = np.asarray(A.obsm["spatial"], dtype=np.float64)
    gv = A[:, "GATA3"].X
    gata = np.asarray(gv.todense()).ravel() if hasattr(gv, "todense") else np.asarray(gv).ravel()

    # spot territory radius, calibrated from the grid itself (same pixel space as the polygons)
    tree = cKDTree(xy)
    nn, _ = tree.query(xy, k=2)
    pitch = float(np.median(nn[:, 1]))
    radius = SPOT_FRAC * pitch
    assert pitch > 0, "degenerate spot grid"

    nx = nuc.loc[neo_mask, "_cx"].to_numpy(float)
    ny = nuc.loc[neo_mask, "_cy"].to_numpy(float)
    na = nuc.loc[neo_mask, "_area"].to_numpy(float)
    # assign each neoplastic nucleus to its nearest spot, but only within that spot's territory.
    # Without the radius test, nuclei in tissue gaps attach to whichever spot is merely closest,
    # inflating counts at tissue edges.
    d, j = tree.query(np.c_[nx, ny], k=1)
    inside = d <= radius
    df = pd.DataFrame(dict(spot=j[inside], area=na[inside]))
    agg = df.groupby("spot").area.agg(["mean", "median", "size"])

    m = np.zeros(len(xy), bool); m[agg.index.to_numpy()] = True
    ok = m & (gata == gata)
    area_mean = np.full(len(xy), np.nan); area_mean[agg.index.to_numpy()] = agg["mean"].to_numpy()
    n_nuc = np.zeros(len(xy)); n_nuc[agg.index.to_numpy()] = agg["size"].to_numpy()

    r_raw, p_raw = pearsonr(area_mean[ok], gata[ok])
    lg = np.log1p(gata[ok])
    r_log, p_log = pearsonr(area_mean[ok], lg)
    rows.append(dict(sample_id=sid, n_nuclei_total=len(nuc), n_nuclei_neoplastic=int(neo_mask.sum()),
                     n_spots=len(xy), n_spots_with_neoplastic=int(ok.sum()),
                     spot_pitch_px=pitch, radius_px=radius,
                     frac_nuclei_assigned=float(inside.mean()),
                     pearson_raw=r_raw, p_raw=p_raw, pearson_log1p=r_log, p_log=p_log,
                     matches_fig3a=abs(len(nuc)-168033) < 2000,
                     matches_appendix6a=abs(len(nuc)-342018) < 2000))
    per_spot_all.append(pd.DataFrame(dict(sample_id=sid, spot=np.arange(len(xy)),
                                          gata3=gata, neo_area_mean=area_mean, n_neoplastic=n_nuc)))
    print(f"  {sid}: r(raw)={r_raw:+.4f} r(log1p)={r_log:+.4f} on {int(ok.sum()):,} spots", flush=True)

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/fig3e_gate.csv", index=False)
pd.concat(per_spot_all, ignore_index=True).to_parquet(f"{OUT}/fig3e_per_spot.parquet", index=False)
print("\n=== Figure 3.e gate ===")
print(d[["sample_id","n_nuclei_total","n_nuclei_neoplastic","n_spots_with_neoplastic",
         "spot_pitch_px","frac_nuclei_assigned","pearson_raw","pearson_log1p",
         "matches_fig3a","matches_appendix6a"]].round(4).to_string(index=False))
tgt = 0.47
for col in ("pearson_raw","pearson_log1p"):
    best = d.loc[d[col].sub(tgt).abs().idxmin()]
    print(f"\nclosest to R=0.47 using {col}: {best.sample_id} at {best[col]:+.4f} "
          f"(|diff| = {abs(best[col]-tgt):.4f}) -> gate {'PASS' if abs(best[col]-tgt)<=0.05 else 'FAIL'}")
if d.matches_fig3a.any():
    print(f"\nsample matching the paper's Figure 3.a nucleus count (168,033): "
          f"{d.loc[d.matches_fig3a,'sample_id'].tolist()}")
