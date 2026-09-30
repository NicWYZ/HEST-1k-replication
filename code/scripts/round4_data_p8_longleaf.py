#!/usr/bin/env python
"""Round 4 P8 items 1 and 5, the parts that need the data on Longleaf.

(a) The subset relation after the drop. For each of the 20 lung members, every patch barcode that
    is not listed in dropped_patch_barcodes must be an expression barcode. The relation is asserted,
    not relaxed: the only change is the explicit per-sample drop list.
(b) The edge-patch diagnostic (report only). Patch centres are the patch file's `coords`, which are
    box centres. The tissue centroid is their mean, and the diagnostic reports the fraction of
    patches whose centre lies more than threshold_mm (1.6 mm, the memo's value for a 3 mm core) from
    it, with the HEST rectangle and the core diameter beside it. Beside that, the same fraction
    against each sample's own core diameter from its GEO title (3 mm or 5 mm), at radius + margin_mm.
    Dropped patches are left out of both.
Reads hest_ext/lung_xenium/{patches,st}; writes only into the current directory.
"""
import hashlib, json, os, sys
import h5py
import numpy as np
import pandas as pd

cfg = json.load(open("p8_config.json"))
ROOT, SET = cfg["root"], cfg["set_dir"]

def _bc(a):
    a = np.asarray(a).reshape(-1)
    return np.array([x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in a], dtype=object)

sub, edge = [], []
for sid in cfg["members"]:
    with h5py.File(f"{ROOT}/{SET}/patches/{sid}.h5", "r") as f:
        bkey = "barcodes" if "barcodes" in f else "barcode"
        pb = _bc(f[bkey][:])
        xy = np.asarray(f["coords"][:], dtype=np.float64)
    with h5py.File(f"{ROOT}/{SET}/st/{sid}.h5ad", "r") as f:
        obs = f["obs"]; idx = obs.attrs.get("_index", "_index")
        idx = idx.decode() if isinstance(idx, bytes) else idx
        sb = set(_bc(obs[idx][:]))
    assert len(pb) == len(xy), sid
    drop = set(cfg["dropped_patch_barcodes"].get(sid, []))
    missing_before = sorted(set(pb) - sb)
    keep = np.array([b not in drop for b in pb])
    assert (~keep).sum() == len(drop), f"{sid}: drop list names barcodes not in the patch file"
    missing_after = sorted(set(pb[keep]) - sb)
    sub.append(dict(sample_id=sid, n_patches=len(pb), n_dropped=int((~keep).sum()),
                    dropped=";".join(sorted(drop)), n_missing_before_drop=len(missing_before),
                    missing_before_drop=";".join(missing_before[:5]),
                    n_patches_after_drop=int(keep.sum()), n_missing_after_drop=len(missing_after),
                    subset_holds_after_drop=len(missing_after) == 0))
    px = cfg["pixel_size_um"][sid]
    c = xy[keep]
    cen = c.mean(axis=0)
    d_mm = np.hypot(*(c - cen).T) * px / 1000.0
    w, h = cfg["fullres_px"][sid]
    edge.append(dict(sample_id=sid, n_patches_used=int(keep.sum()), pixel_size_um=px,
                     centroid_x_px=round(float(cen[0]), 1), centroid_y_px=round(float(cen[1]), 1),
                     threshold_mm=cfg["threshold_mm"],
                     n_beyond_threshold=int((d_mm > cfg["threshold_mm"]).sum()),
                     frac_beyond_threshold=round(float((d_mm > cfg["threshold_mm"]).mean()), 6),
                     dist_mm_median=round(float(np.median(d_mm)), 4),
                     dist_mm_q95=round(float(np.quantile(d_mm, 0.95)), 4),
                     dist_mm_max=round(float(d_mm.max()), 4),
                     hest_rect_px_w=w, hest_rect_px_h=h,
                     hest_rect_mm_w=round(w * px / 1000.0, 3), hest_rect_mm_h=round(h * px / 1000.0, 3),
                     core_diameter_mm=cfg["core_diameter_mm"],
                     core_diameter_mm_source=cfg["core_diameter_mm_source"][sid],
                     threshold_source_mm=cfg["core_diameter_mm_source"][sid] / 2.0 + cfg["margin_mm"],
                     n_beyond_source_threshold=int((d_mm > cfg["core_diameter_mm_source"][sid] / 2.0 + cfg["margin_mm"]).sum()),
                     frac_beyond_source_threshold=round(float((d_mm > cfg["core_diameter_mm_source"][sid] / 2.0 + cfg["margin_mm"]).mean()), 6)))
    print(sid, sub[-1]["n_missing_before_drop"], sub[-1]["n_missing_after_drop"],
          edge[-1]["frac_beyond_threshold"], flush=True)

pd.DataFrame(sub).to_csv("p8_subset_after_drop.csv", index=False)
pd.DataFrame(edge).to_csv("lung_edge_patches.csv", index=False)
ok = all(r["subset_holds_after_drop"] for r in sub)
json.dump(dict(n_samples=len(sub), subset_holds_after_drop_all=ok,
               n_samples_failing_before_drop=sum(r["n_missing_before_drop"] > 0 for r in sub),
               script_md5=hashlib.md5(open(__file__, "rb").read()).hexdigest()),
          open("p8_longleaf_summary.json", "w"), indent=1)
print("SUBSET_AFTER_DROP_ALL", ok)
sys.exit(0 if ok else 3)
