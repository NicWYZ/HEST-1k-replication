"""Round-3 anchor follow-up: test the coordinate relation on every shared barcode.

On the first five rows of four anchor samples, the bench_data coordinate equals
the HEST-1k coordinate with its two axes exchanged plus floor(patch_size_src/2)
in both axes, exactly. That is the claim the anchor conclusion rests on (the two
layouts address the same patch window), so it is tested here over every shared
barcode of all 28 anchor samples rather than on twenty rows.
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


def bc(a):
    a = np.asarray(a).reshape(-1)
    return np.array([x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in a])


rows = []
for sid in sorted(D2["bench_task"]):
    task = D2["bench_task"][sid]
    pn = os.path.join(EXT, D2["home"][sid], "patches", f"{sid}.h5")
    pb = os.path.join(BENCH, task, "patches", f"{sid}.h5")
    rec = {"sample_id": sid, "benchmark_task": task}
    with h5py.File(pn, "r") as fn, h5py.File(pb, "r") as fb:
        kn = "img" if "img" in fn else "imgs"
        kb = "img" if "img" in fb else "imgs"
        psrc_n = int(float(fn[kn].attrs["patch_size_src"]))
        psrc_b = int(float(fb[kb].attrs["patch_size"]))
        an = bc(fn["barcodes"][:] if "barcodes" in fn else fn["barcode"][:])
        ab = bc(fb["barcodes"][:] if "barcodes" in fb else fb["barcode"][:])
        cn = np.asarray(fn["coords"][:], dtype=np.int64)
        cb = np.asarray(fb["coords"][:], dtype=np.int64)
    shared = np.array(sorted(set(an) & set(ab)))
    mn = {b: i for i, b in enumerate(an)}
    mb = {b: i for i, b in enumerate(ab)}
    A = cn[[mn[b] for b in shared]]
    B = cb[[mb[b] for b in shared]]
    half = psrc_n // 2
    pred = A[:, ::-1] + half
    d = B - pred
    rec.update({
        "patch_size_src_hest1k": psrc_n, "patch_size_bench": psrc_b,
        "patch_size_agrees": str(psrc_n == psrc_b), "half_patch": half,
        "n_shared_barcodes": int(len(shared)),
        "relation_holds_exactly": str(bool((d == 0).all())),
        "n_rows_violating": int((d != 0).any(axis=1).sum()),
        "residual_min": json.dumps(d.min(axis=0).tolist()) if len(d) else "",
        "residual_max": json.dumps(d.max(axis=0).tolist()) if len(d) else "",
        "residual_unique": json.dumps(
            [int(len(np.unique(d[:, 0]))), int(len(np.unique(d[:, 1])))]) if len(d) else "",
        "no_swap_residual_max": json.dumps((B - (A + half)).max(axis=0).tolist()) if len(d) else "",
        "no_offset_residual_max": json.dumps((B - A[:, ::-1]).max(axis=0).tolist()) if len(d) else "",
    })
    rows.append(rec)
    print(f"  {sid} shared {rec['n_shared_barcodes']} psrc {psrc_n}/{psrc_b} "
          f"holds {rec['relation_holds_exactly']} violating {rec['n_rows_violating']} "
          f"resid {rec['residual_min']}..{rec['residual_max']}", flush=True)

out = os.path.join(EXT, "anchor_coord_relation.csv")
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

summary = {
    "relation_tested": "bench_coords == hest1k_coords[:, ::-1] + floor(patch_size_src/2)",
    "n_samples": len(rows),
    "n_holds_exactly": sum(1 for r in rows if r["relation_holds_exactly"] == "True"),
    "samples_violating": [(r["sample_id"], r["n_rows_violating"], r["residual_min"],
                           r["residual_max"]) for r in rows
                          if r["relation_holds_exactly"] != "True"],
    "total_shared_barcodes_tested": sum(r["n_shared_barcodes"] for r in rows),
    "n_patch_size_agrees": sum(1 for r in rows if r["patch_size_agrees"] == "True"),
    "slurm_job_id": os.environ.get("SLURM_JOB_ID", "NA"),
    "slurm_partition": os.environ.get("SLURM_JOB_PARTITION", "NA"),
    "slurm_nodelist": os.environ.get("SLURM_JOB_NODELIST", "NA"),
    "node": platform.node(), "python": platform.python_version(),
    "executable": sys.executable,
    "pythonhashseed": os.environ.get("PYTHONHASHSEED", "unset"),
    "created": dt.datetime.now().astimezone().isoformat(),
}
json.dump(summary, open(os.path.join(EXT, "anchor_coord_relation.json"), "w"), indent=2)
print("SUMMARY " + json.dumps(summary), flush=True)

import shutil
shutil.copy(out, "anchor_coord_relation.csv")
shutil.copy(os.path.join(EXT, "anchor_coord_relation.json"), "anchor_coord_relation.json")
print("DONE", flush=True)
