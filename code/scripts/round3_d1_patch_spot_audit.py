"""Round-3 D1 follow-up: why the patch count does not equal the spot count.

The D1 verification found patch count < spot count for 94 of 105 samples. This
establishes the relation rather than assuming it: are the patch barcodes a
subset of the expression file's barcodes, so that HEST's patching has dropped
spots, or are they a different set?

It also runs the patch-level half of the anchor comparison on CPU, for the 28
samples that exist in both layouts: HEST-1k patches against the round-1
benchmark's bench_data patches, on count, barcode set, coordinates and raw
image bytes. That is the diagnostic the anchor check needs if the embeddings
disagree, and it does not need a GPU.

Rewrites hest_ext/d1_verification.csv with the subset columns appended.
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
BENCH_DATA = os.path.join(PROJ, "bench_data")
BENCH_TASK = D2["bench_task"]

home = {r["sample_id"]: r["home_set"] for r in csv.DictReader(open("sample_home_map.csv"))}
prev = {r["sample_id"]: r for r in csv.DictReader(open("d1_verification.csv"))}
ALL = sorted(home)


def bc(arr):
    a = np.asarray(arr).reshape(-1)
    return np.array([x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in a])


def patch_bc(path):
    with h5py.File(path, "r") as f:
        k = "barcodes" if "barcodes" in f else "barcode"
        return bc(f[k][:])


def st_bc(path):
    with h5py.File(path, "r") as f:
        obs = f["obs"]
        idx = obs.attrs.get("_index", "_index")
        if isinstance(idx, bytes):
            idx = idx.decode()
        return bc(obs[idx][:])


def attrs_of(path):
    out = {"file": {}, "datasets": {}}
    with h5py.File(path, "r") as f:
        out["file"] = {k: str(v) for k, v in f.attrs.items()}
        for k in f.keys():
            out["datasets"][k] = {"shape": list(f[k].shape), "dtype": str(f[k].dtype),
                                  "attrs": {a: str(v) for a, v in f[k].attrs.items()}}
    return out


rows = []
for sid in ALL:
    d = os.path.join(EXT, home[sid])
    rec = dict(prev[sid])
    try:
        pb = patch_bc(os.path.join(d, f"patches/{sid}.h5"))
        sb = st_bc(os.path.join(d, f"st/{sid}.h5ad"))
        extra = sorted(set(pb) - set(sb))
        rec.update({
            "n_patch_barcodes_unique": str(len(set(pb))),
            "n_st_barcodes_unique": str(len(set(sb))),
            "n_patch_barcodes_not_in_st": str(len(extra)),
            "patch_barcodes_subset_of_st": str(len(extra) == 0),
            "patch_barcodes_unique": str(len(set(pb)) == len(pb)),
            "st_barcodes_unique": str(len(set(sb)) == len(sb)),
            "n_st_spots_without_a_patch": str(len(set(sb) - set(pb))),
            "patch_count_le_spot_count": str(len(pb) <= len(sb)),
            "example_patch_barcodes_not_in_st": ";".join(extra[:3]),
            "audit_error": "",
        })
    except Exception as exc:
        rec.update({k: "" for k in ["n_patch_barcodes_unique", "n_st_barcodes_unique",
                                    "n_patch_barcodes_not_in_st", "patch_barcodes_subset_of_st",
                                    "patch_barcodes_unique", "st_barcodes_unique",
                                    "n_st_spots_without_a_patch", "patch_count_le_spot_count",
                                    "example_patch_barcodes_not_in_st"]})
        rec["audit_error"] = f"{type(exc).__name__}: {exc}"
    rows.append(rec)
    print(f"  {sid} patch {rec.get('n_patch_barcodes_unique')} st {rec.get('n_st_barcodes_unique')} "
          f"subset {rec.get('patch_barcodes_subset_of_st')} "
          f"spots_without_patch {rec.get('n_st_spots_without_a_patch')} {rec['audit_error']}",
          flush=True)

fields = list(rows[0].keys())
with open(os.path.join(EXT, "d1_verification.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

# ------------------------------------------------------- anchor patch comparison
arows = []
for sid in sorted(BENCH_TASK):
    task = BENCH_TASK[sid]
    newp = os.path.join(EXT, home[sid], "patches", f"{sid}.h5")
    bp = os.path.join(BENCH_DATA, task, "patches", f"{sid}.h5")
    rec = {"sample_id": sid, "benchmark_task": task, "hest1k_patches": newp,
           "bench_patches": bp, "n_patches_hest1k": -1, "n_patches_bench": -1,
           "patch_shape_hest1k": "", "patch_shape_bench": "",
           "patch_dtype_hest1k": "", "patch_dtype_bench": "",
           "n_barcodes_shared": -1, "barcode_sets_identical": "",
           "row_order_identical": "", "n_barcodes_compared": -1,
           "max_abs_img_diff": "", "frac_img_bytes_differing": "",
           "max_abs_coord_diff": "", "attrs_hest1k": "", "attrs_bench": "", "error": ""}
    try:
        an, ab = attrs_of(newp), attrs_of(bp)
        kn = "img" if "img" in an["datasets"] else ("imgs" if "imgs" in an["datasets"] else "images")
        kb = "img" if "img" in ab["datasets"] else ("imgs" if "imgs" in ab["datasets"] else "images")
        rec.update({
            "n_patches_hest1k": an["datasets"][kn]["shape"][0],
            "n_patches_bench": ab["datasets"][kb]["shape"][0],
            "patch_shape_hest1k": "x".join(str(x) for x in an["datasets"][kn]["shape"][1:]),
            "patch_shape_bench": "x".join(str(x) for x in ab["datasets"][kb]["shape"][1:]),
            "patch_dtype_hest1k": an["datasets"][kn]["dtype"],
            "patch_dtype_bench": ab["datasets"][kb]["dtype"],
            "attrs_hest1k": json.dumps(an, sort_keys=True),
            "attrs_bench": json.dumps(ab, sort_keys=True),
        })
        with h5py.File(newp, "r") as fn, h5py.File(bp, "r") as fb:
            pn = bc(fn["barcodes"][:] if "barcodes" in fn else fn["barcode"][:])
            pb2 = bc(fb["barcodes"][:] if "barcodes" in fb else fb["barcode"][:])
            shared = np.array(sorted(set(pn) & set(pb2)))
            rec.update({"n_barcodes_shared": int(len(shared)),
                        "barcode_sets_identical": str(set(pn) == set(pb2)),
                        "row_order_identical": str(len(pn) == len(pb2)
                                                   and bool((pn == pb2).all()))})
            if len(shared) and an["datasets"][kn]["shape"][1:] == ab["datasets"][kb]["shape"][1:]:
                take = shared[np.linspace(0, len(shared) - 1, min(32, len(shared))).astype(int)]
                mn = {b: i for i, b in enumerate(pn)}
                mb = {b: i for i, b in enumerate(pb2)}
                dmax = ndiff = ntot = cmax = 0
                for b in take:
                    x = fn[kn][mn[b]].astype(np.int64)
                    y = fb[kb][mb[b]].astype(np.int64)
                    dd = np.abs(x - y)
                    dmax = max(dmax, int(dd.max()))
                    ndiff += int((dd != 0).sum())
                    ntot += dd.size
                    cmax = max(cmax, int(np.abs(fn["coords"][mn[b]].astype(np.int64)
                                                - fb["coords"][mb[b]].astype(np.int64)).max()))
                rec.update({"n_barcodes_compared": int(len(take)), "max_abs_img_diff": str(dmax),
                            "frac_img_bytes_differing": f"{ndiff / max(ntot, 1):.6f}",
                            "max_abs_coord_diff": str(cmax)})
    except Exception as exc:
        rec["error"] = f"{type(exc).__name__}: {exc}"
    arows.append(rec)
    print(f"  ANCHOR-PATCH {sid} n {rec['n_patches_hest1k']} vs {rec['n_patches_bench']} "
          f"bcsets_identical {rec['barcode_sets_identical']} order {rec['row_order_identical']} "
          f"img_maxdiff {rec['max_abs_img_diff']} coord_maxdiff {rec['max_abs_coord_diff']} "
          f"{rec['error']}", flush=True)

apath = os.path.join(EXT, "anchor_patch_compare.csv")
with open(apath, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(arows[0].keys()))
    w.writeheader()
    w.writerows(arows)

ok = [r for r in rows if not r["audit_error"]]
aok = [r for r in arows if not r["error"]]
summary = {
    "n_samples": len(rows),
    "n_patch_count_equals_spot_count": sum(1 for r in ok
                                           if r["patch_count_equals_spot_count"] == "True"),
    "n_patch_count_le_spot_count": sum(1 for r in ok if r["patch_count_le_spot_count"] == "True"),
    "n_patch_barcodes_subset_of_st": sum(1 for r in ok
                                         if r["patch_barcodes_subset_of_st"] == "True"),
    "samples_patch_barcodes_not_subset": [r["sample_id"] for r in ok
                                          if r["patch_barcodes_subset_of_st"] != "True"],
    "total_st_spots_without_a_patch": sum(int(r["n_st_spots_without_a_patch"]) for r in ok),
    "total_st_spots": sum(int(r["n_st_barcodes_unique"]) for r in ok),
    "all_patch_barcodes_unique": all(r["patch_barcodes_unique"] == "True" for r in ok),
    "all_st_barcodes_unique": all(r["st_barcodes_unique"] == "True" for r in ok),
    "n_audit_errors": len(rows) - len(ok),
    "anchor_n": len(arows),
    "anchor_n_barcode_sets_identical": sum(1 for r in aok
                                           if r["barcode_sets_identical"] == "True"),
    "anchor_n_row_order_identical": sum(1 for r in aok if r["row_order_identical"] == "True"),
    "anchor_max_img_diff": max([int(r["max_abs_img_diff"]) for r in aok
                                if r["max_abs_img_diff"] != ""], default=None),
    "anchor_max_coord_diff": max([int(r["max_abs_coord_diff"]) for r in aok
                                  if r["max_abs_coord_diff"] != ""], default=None),
    "anchor_count_mismatch": [(r["sample_id"], r["n_patches_hest1k"], r["n_patches_bench"])
                              for r in aok if r["n_patches_hest1k"] != r["n_patches_bench"]],
    "anchor_errors": [(r["sample_id"], r["error"]) for r in arows if r["error"]],
    "slurm_job_id": os.environ.get("SLURM_JOB_ID", "NA"),
    "slurm_partition": os.environ.get("SLURM_JOB_PARTITION", "NA"),
    "slurm_nodelist": os.environ.get("SLURM_JOB_NODELIST", "NA"),
    "node": platform.node(),
    "python": platform.python_version(),
    "executable": sys.executable,
    "pythonhashseed": os.environ.get("PYTHONHASHSEED", "unset"),
    "created": dt.datetime.now().astimezone().isoformat(),
}
sp = os.path.join(EXT, "d1_patch_spot_audit.json")
json.dump(summary, open(sp, "w"), indent=2)
print("SUMMARY " + json.dumps(summary), flush=True)

import shutil
shutil.copy(os.path.join(EXT, "d1_verification.csv"), "d1_verification.csv")
shutil.copy(apath, "anchor_patch_compare.csv")
shutil.copy(sp, "d1_patch_spot_audit.json")
print("DONE", flush=True)
