"""Round-3 D1/D2: establish HOW the two patch layouts differ.

The anchor check failed: resnet50 embeddings from HEST-1k patches disagree with
the round-1 cached embeddings by about 7 percent relative, per-barcode, while
the two patch files carry the same nominal geometry (patch_size_src 245,
patch_size_target 224, downsample 1.0943..., pixel_size 0.4569 for INT1). This
measures where the difference actually is, rather than guessing:

  coordinates  delta per axis for matched barcodes; whether an axis swap, a
               constant offset or a scale factor explains it
  images       for matched barcodes, mean and max absolute difference,
               fraction of bytes differing, Pearson correlation; and whether
               the bench patch is better matched by a DIFFERENT HEST-1k patch,
               which would mean a barcode-to-row misalignment rather than a
               resampling difference
  barcodes     the set relation, and which spots each layout dropped
"""
import csv
import datetime as dt
import json
import os
import platform
import sys

import h5py
import numpy as np

CFG = json.load(open("d1_config.json"))
D2 = json.load(open("d2_config.json"))
PROJ = CFG["project_root"]
EXT = CFG["ext_root"]
BENCH = os.path.join(PROJ, "bench_data")
home = D2["home"]
SAMPLES = json.loads(os.environ.get("DIAG_SAMPLES", '["INT13", "INT1", "TENX95", "NCBI783"]'))
NB = int(os.environ.get("DIAG_NBARCODES", "24"))


def bc(a):
    a = np.asarray(a).reshape(-1)
    return np.array([x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in a])


rows = []
for sid in SAMPLES:
    task = D2["bench_task"][sid]
    pn = os.path.join(EXT, home[sid], "patches", f"{sid}.h5")
    pb = os.path.join(BENCH, task, "patches", f"{sid}.h5")
    rec = {"sample_id": sid, "benchmark_task": task}
    with h5py.File(pn, "r") as fn, h5py.File(pb, "r") as fb:
        kn = "img" if "img" in fn else "imgs"
        kb = "img" if "img" in fb else "imgs"
        an = bc(fn["barcodes"][:] if "barcodes" in fn else fn["barcode"][:])
        ab = bc(fb["barcodes"][:] if "barcodes" in fb else fb["barcode"][:])
        cn = np.asarray(fn["coords"][:], dtype=np.int64)
        cb = np.asarray(fb["coords"][:], dtype=np.int64)
        rec.update({
            "n_hest1k": len(an), "n_bench": len(ab),
            "n_shared": int(len(set(an) & set(ab))),
            "n_only_hest1k": int(len(set(an) - set(ab))),
            "n_only_bench": int(len(set(ab) - set(an))),
            "barcode_sets_identical": str(set(an) == set(ab)),
            "row_order_identical": str(len(an) == len(ab) and bool((an == ab).all())),
            "attrs_hest1k_img": json.dumps({k: str(v) for k, v in fn[kn].attrs.items()},
                                           sort_keys=True),
            "attrs_bench_img": json.dumps({k: str(v) for k, v in fb[kb].attrs.items()},
                                          sort_keys=True),
            "shape_hest1k": str(fn[kn].shape), "shape_bench": str(fb[kb].shape),
        })
        shared = np.array(sorted(set(an) & set(ab)))
        mn = {b: i for i, b in enumerate(an)}
        mb = {b: i for i, b in enumerate(ab)}
        # ---- coordinates, matched on barcode
        ix = np.array([mn[b] for b in shared])
        iy = np.array([mb[b] for b in shared])
        A, B = cn[ix], cb[iy]
        d = A - B
        rec.update({
            "coord_hest1k_first5": json.dumps(A[:5].tolist()),
            "coord_bench_first5": json.dumps(B[:5].tolist()),
            "coord_delta_min": json.dumps(d.min(axis=0).tolist()),
            "coord_delta_max": json.dumps(d.max(axis=0).tolist()),
            "coord_delta_unique_count": json.dumps([int(len(np.unique(d[:, 0]))),
                                                    int(len(np.unique(d[:, 1])))]),
            "coord_identical": str(bool((d == 0).all())),
            "coord_matches_after_axis_swap": str(bool((A[:, ::-1] == B).all())),
            "coord_constant_offset": (json.dumps(d[0].tolist())
                                      if bool((d == d[0]).all()) else ""),
            "coord_ratio_median": json.dumps(
                [float(np.median(A[:, 0] / np.where(B[:, 0] == 0, np.nan, B[:, 0]))),
                 float(np.median(A[:, 1] / np.where(B[:, 1] == 0, np.nan, B[:, 1])))]),
        })
        # ---- images, matched on barcode
        take = shared[np.linspace(0, len(shared) - 1, min(NB, len(shared))).astype(int)]
        mad, mx, fr, co = [], [], [], []
        cross_better = 0
        for b in take:
            x = fn[kn][mn[b]].astype(np.float64)
            y = fb[kb][mb[b]].astype(np.float64)
            dd = np.abs(x - y)
            mad.append(float(dd.mean()))
            mx.append(float(dd.max()))
            fr.append(float((dd != 0).mean()))
            co.append(float(np.corrcoef(x.ravel(), y.ravel())[0, 1]))
            # is some OTHER hest1k patch a better match to this bench patch?
            cand = shared[np.linspace(0, len(shared) - 1, min(40, len(shared))).astype(int)]
            best, bestb = None, None
            for cb_ in cand:
                z = fn[kn][mn[cb_]].astype(np.float64)
                e = float(np.abs(z - y).mean())
                if best is None or e < best:
                    best, bestb = e, cb_
            if bestb != b and best < mad[-1] * 0.9:
                cross_better += 1
        rec.update({
            "n_barcodes_compared": len(take),
            "img_mean_abs_diff_median": f"{float(np.median(mad)):.4f}",
            "img_mean_abs_diff_max": f"{float(np.max(mad)):.4f}",
            "img_max_abs_diff_max": f"{float(np.max(mx)):.0f}",
            "img_frac_bytes_differing_median": f"{float(np.median(fr)):.6f}",
            "img_pearson_min": f"{float(np.min(co)):.6f}",
            "img_pearson_median": f"{float(np.median(co)):.6f}",
            "n_barcodes_better_matched_by_another_patch": cross_better,
        })
    rows.append(rec)
    print(json.dumps(rec, sort_keys=True), flush=True)

out = os.path.join(EXT, "anchor_layout_diagnostic.csv")
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

meta = {"samples": SAMPLES, "n_barcodes_per_sample": NB,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID", "NA"),
        "slurm_partition": os.environ.get("SLURM_JOB_PARTITION", "NA"),
        "slurm_nodelist": os.environ.get("SLURM_JOB_NODELIST", "NA"),
        "node": platform.node(), "python": platform.python_version(),
        "executable": sys.executable,
        "pythonhashseed": os.environ.get("PYTHONHASHSEED", "unset"),
        "created": dt.datetime.now().astimezone().isoformat()}
json.dump(meta, open(os.path.join(EXT, "anchor_layout_diagnostic.json"), "w"), indent=2)

import shutil
shutil.copy(out, "anchor_layout_diagnostic.csv")
shutil.copy(os.path.join(EXT, "anchor_layout_diagnostic.json"), "anchor_layout_diagnostic.json")
print("DONE", flush=True)
