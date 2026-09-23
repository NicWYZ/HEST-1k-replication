"""Round-3 D2: patch embeddings for one expansion set with one encoder.

Uses the benchmark's own extraction path from round 1, by importing the same
functions rather than reimplementing them:

  trident.patch_encoder_models.encoder_factory   (pinned TRIDENT commit)
  hest.bench.st_dataset.H5PatchDataset
  hest.bench.benchmark.embed_tiles, set_seed

which is exactly what hest.bench.benchmark.predict_single_split calls, with the
round-1 config values (seed 1, batch_size 128, num_workers 4). Output layout
mirrors round 1's embeddings/<task>/<encoder>/<sample>.h5 as
embeddings_ext/<set>/<encoder>/<sample>.h5, one file per sample, so a killed
job resumes and skips what is already written.

Then, for the samples of this set that also exist in the round-1 benchmark
layout, the anchor check: new embeddings against the cached benchmark
embeddings for the same encoder, matched on barcode. Patch-level diagnostics
(patch count, patch shape, h5 attributes, barcode sets, raw image bytes) are
recorded in the same pass so a disagreement can be attributed.

usage: round3_d2_embed.py --set <set_name> --encoder <encoder>
"""
import argparse
import csv
import datetime as dt
import glob
import hashlib
import json
import os
import platform
import shlex
import subprocess
import sys
import zlib

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--set", dest="set_name", required=True)
ap.add_argument("--encoder", required=True)
ap.add_argument("--config", default="d2_config.json")
args = ap.parse_args()

CFG = json.load(open(args.config))
PROJ = CFG["project_root"]
EXT = CFG["ext_root"]
EMB = CFG["emb_ext_root"]
BENCH_EMB = os.path.join(PROJ, "embeddings")
BENCH_DATA = os.path.join(PROJ, "bench_data")
SEED = CFG["seed"]
BATCH = CFG["batch_size"]
WORKERS = CFG["num_workers"]

members = CFG["sets"][args.set_name]["members"]
home = CFG["home"]          # sample_id -> home set directory under hest_ext
bench_task = CFG["bench_task"]   # sample_id -> benchmark task, for samples in the benchmark


def sh(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (p.stdout + p.stderr).strip()


if not os.path.isdir(os.path.join(PROJ, "code", "HEST", "src", "hest")):
    sys.exit("FATAL: HEST source tree not found")
try:
    import hest  # noqa: F401
except ImportError:
    sys.path.insert(0, os.path.join(PROJ, "code", "HEST", "src"))

import h5py
import torch
from torch.utils.data import DataLoader
from torch.utils.data._utils.collate import default_collate

from hest.bench.benchmark import embed_tiles, set_seed
from hest.bench.st_dataset import H5PatchDataset
from trident.patch_encoder_models import encoder_factory

# ------------------------------------------------------------------ environment
trident_commit = ""
for p in glob.glob(os.path.join(os.path.dirname(os.path.dirname(torch.__file__)),
                                "trident-*.dist-info", "direct_url.json")):
    trident_commit = json.load(open(p)).get("vcs_info", {}).get("commit_id", "")
env_facts = {
    "slurm_job_id": os.environ.get("SLURM_JOB_ID", "NA"),
    "slurm_partition": os.environ.get("SLURM_JOB_PARTITION", "NA"),
    "slurm_nodelist": os.environ.get("SLURM_JOB_NODELIST", "NA"),
    "node": platform.node(),
    "pythonhashseed": os.environ.get("PYTHONHASHSEED", "unset"),
    "python": platform.python_version(),
    "executable": sys.executable,
    "torch": torch.__version__,
    "cuda": torch.version.cuda,
    "cudnn": torch.backends.cudnn.version(),
    "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NO GPU",
    "gpu_capability": str(torch.cuda.get_device_capability(0)) if torch.cuda.is_available() else "",
    "trident_version": __import__("trident").__version__ if hasattr(__import__("trident"), "__version__") else "",
    "trident_commit_installed": trident_commit,
    "trident_commit_pinned": CFG["trident_commit_pinned"],
    "commit": sh(f"git -C {shlex.quote(PROJ)} rev-parse HEAD"),
}
if trident_commit and trident_commit != CFG["trident_commit_pinned"]:
    sys.exit(f"FATAL: installed TRIDENT {trident_commit} is not the pinned "
             f"{CFG['trident_commit_pinned']}")
print("ENV " + json.dumps(env_facts, sort_keys=True), flush=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
if device != "cuda":
    sys.exit("FATAL: no CUDA device")


def _patch_path(sid):
    return os.path.join(EXT, CFG["home"][sid], "patches", f"{sid}.h5")


# Guard. These jobs are queued behind D1 with a Slurm dependency, so they can
# start before or without D1's downloads. Establish what is on disk before
# loading an encoder onto the GPU: with nothing to do, exit immediately rather
# than hold a GPU; with some samples present, embed those and report the rest.
_present = [s for s in sorted(members) if os.path.isfile(_patch_path(s))]
print(f"GUARD {args.set_name}: {len(_present)}/{len(members)} samples have patches on disk",
      flush=True)
if not _present:
    sys.exit(f"FATAL: no patches on disk for set {args.set_name} under {EXT}; "
             f"D1 has not delivered this set. Nothing to embed, releasing the GPU.")
if len(_present) < len(members):
    print("WARN missing patches for: "
          + ";".join(s for s in sorted(members) if s not in set(_present)), flush=True)

set_seed(SEED)
encoder = encoder_factory(args.encoder)
precision = encoder.precision
_ = encoder.eval()
encoder.to(device)
env_facts["encoder_precision"] = str(precision)
env_facts["encoder_class"] = type(encoder).__name__
print(f"encoder {args.encoder} class {type(encoder).__name__} precision {precision}", flush=True)

out_dir = os.path.join(EMB, args.set_name, args.encoder)
os.makedirs(out_dir, exist_ok=True)


def _collate_object_barcodes(batch):
    """Default collate, except barcodes arrive as a dtype-object array.

    HEST's save_hdf5 appends each batch to the open dataset behind
    `assert dset.dtype == val.dtype`, and benchmark._to_numpy casts a unicode
    barcode array to S<max_len_in_this_batch>, recomputed per batch. A sample
    whose barcode string lengths differ between batches therefore fails that
    assert partway through extraction.

    Observed, not inferred: job 2128583 (resnet50, institution_breast_xenium)
    died at that assert on the third batch of the sample that follows TENX95 in
    sorted order, after TENX95 completed. The log prints no sample name before
    the crash and no byte lengths, so which sample and which lengths is an
    inference from the iteration order, not a reading. The mechanism above is
    read directly from benchmark._to_numpy and file_utils.save_hdf5.

    Handing the barcodes over as dtype object routes save_hdf5 down the
    variable-length-string branch it already has, which every batch then
    matches. Images, transforms, batch order, encoder and barcode values are
    untouched; only the h5 string dtype of the barcode column changes.
    """
    bcs = np.empty(len(batch), dtype=object)
    for i, b in enumerate(batch):
        bcs[i] = b["barcodes"]
    rest = default_collate([{k: v for k, v in b.items() if k != "barcodes"} for b in batch])
    rest["barcodes"] = bcs
    return rest


def n_rows(h5_path, key="embeddings"):
    with h5py.File(h5_path, "r") as f:
        return int(f[key].shape[0])


def patch_path(sid):
    return os.path.join(EXT, home[sid], "patches", f"{sid}.h5")


# ------------------------------------------------------------------ extraction
log = []
for sid in sorted(members):
    tile_h5 = patch_path(sid)
    if not os.path.isfile(tile_h5):
        log.append({"sample_id": sid, "status": "MISSING_PATCHES", "n_patches": -1,
                    "seconds": 0.0})
        print(f"  {sid}: MISSING PATCHES {tile_h5}", flush=True)
        continue
    with h5py.File(tile_h5, "r") as f:
        key = "img" if "img" in f else ("imgs" if "imgs" in f else "images")
        n_patch = int(f[key].shape[0])
    dst = os.path.join(out_dir, f"{sid}.h5")
    if os.path.isfile(dst):
        try:
            if n_rows(dst) == n_patch:
                log.append({"sample_id": sid, "status": "cached", "n_patches": n_patch,
                            "seconds": 0.0})
                print(f"  {sid}: cached ({n_patch} patches)", flush=True)
                continue
            print(f"  {sid}: cached file has {n_rows(dst)} rows, expected {n_patch}; redoing",
                  flush=True)
        except Exception as exc:
            print(f"  {sid}: cached file unreadable ({exc}); redoing", flush=True)
        os.remove(dst)
    t0 = dt.datetime.now()
    tmp = dst + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    ds = H5PatchDataset(tile_h5, img_transform=encoder.eval_transforms)
    dl = DataLoader(ds, batch_size=BATCH, shuffle=False, num_workers=WORKERS,
                    collate_fn=_collate_object_barcodes)
    embed_tiles(dl, encoder, tmp, device, precision)
    os.replace(tmp, dst)
    secs = (dt.datetime.now() - t0).total_seconds()
    log.append({"sample_id": sid, "status": "written", "n_patches": n_patch,
                "seconds": round(secs, 1)})
    print(f"  {sid}: written {n_patch} patches in {secs:.0f}s "
          f"({n_patch / max(secs, 1e-9):.0f} patch/s)", flush=True)

lp = os.path.join(EMB, f"d2_extraction__{args.set_name}__{args.encoder}.csv")
with open(lp, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["sample_id", "status", "n_patches", "seconds"])
    w.writeheader()
    w.writerows(log)

# ------------------------------------------------------------------ anchor check
def read_h5(path, keys):
    out = {}
    with h5py.File(path, "r") as f:
        for k in keys:
            if k in f:
                out[k] = f[k][:]
    return out


def barcodes_of(arr):
    a = np.asarray(arr).reshape(-1)
    return np.array([x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in a])


def attrs_json(path):
    out = {"file": {}, "datasets": {}}
    with h5py.File(path, "r") as f:
        out["file"] = {k: str(v) for k, v in f.attrs.items()}
        for k in f.keys():
            out["datasets"][k] = {"shape": list(f[k].shape), "dtype": str(f[k].dtype),
                                  "attrs": {a: str(v) for a, v in f[k].attrs.items()}}
    return out


anchors = [s for s in sorted(members) if s in bench_task]
rows = []
for sid in anchors:
    task = bench_task[sid]
    newp = os.path.join(out_dir, f"{sid}.h5")
    benchp = os.path.join(BENCH_EMB, task, args.encoder, f"{sid}.h5")
    newpatch = patch_path(sid)
    benchpatch = os.path.join(BENCH_DATA, task, "patches", f"{sid}.h5")
    rec = {"sample_id": sid, "set_name": args.set_name, "encoder": args.encoder,
           "benchmark_task": task, "new_embeddings": newp, "bench_embeddings": benchp,
           "n_rows_new": -1, "n_rows_bench": -1, "emb_dim_new": -1, "emb_dim_bench": -1,
           "n_barcodes_new": -1, "n_barcodes_bench": -1, "n_barcodes_matched": -1,
           "barcode_sets_identical": "", "row_order_identical": "",
           "max_abs_diff": "", "max_rel_diff_elem": "", "median_rel_diff_elem": "",
           "frac_elems_excluded_small": "", "max_rel_l2_row": "", "median_rel_l2_row": "",
           "agrees_1e-5": "",
           "n_patches_new": -1, "n_patches_bench": -1,
           "patch_shape_new": "", "patch_shape_bench": "",
           "patch_dtype_new": "", "patch_dtype_bench": "",
           "patch_attrs_new": "", "patch_attrs_bench": "",
           "n_patch_barcodes_compared": -1, "max_abs_img_diff": "",
           "frac_img_bytes_differing": "", "max_abs_coord_diff": "", "error": ""}
    try:
        if not os.path.isfile(newp):
            raise FileNotFoundError(f"new embeddings absent: {newp}")
        if not os.path.isfile(benchp):
            raise FileNotFoundError(f"benchmark embeddings absent: {benchp}")
        A = read_h5(newp, ["embeddings", "barcodes", "coords"])
        B = read_h5(benchp, ["embeddings", "barcodes", "coords"])
        ea, eb = np.asarray(A["embeddings"]), np.asarray(B["embeddings"])
        ba, bb = barcodes_of(A["barcodes"]), barcodes_of(B["barcodes"])
        rec.update({"n_rows_new": int(ea.shape[0]), "n_rows_bench": int(eb.shape[0]),
                    "emb_dim_new": int(ea.shape[1]), "emb_dim_bench": int(eb.shape[1]),
                    "n_barcodes_new": int(len(set(ba))), "n_barcodes_bench": int(len(set(bb))),
                    "barcode_sets_identical": str(set(ba) == set(bb)),
                    "row_order_identical": str(len(ba) == len(bb) and bool((ba == bb).all()))})
        common = np.array(sorted(set(ba) & set(bb)))
        rec["n_barcodes_matched"] = int(len(common))
        if len(common) and ea.shape[1] == eb.shape[1]:
            ia = {b: i for i, b in enumerate(ba)}
            ib = {b: i for i, b in enumerate(bb)}
            X = ea[[ia[b] for b in common]].astype(np.float64)
            Y = eb[[ib[b] for b in common]].astype(np.float64)
            d = np.abs(X - Y)
            scale = np.maximum(np.abs(X), np.abs(Y))
            floor = 1e-3 * float(np.median(scale))
            m = scale > floor
            rel = d[m] / scale[m]
            l2 = np.linalg.norm(X - Y, axis=1) / np.maximum(np.linalg.norm(X, axis=1), 1e-30)
            rec.update({
                "max_abs_diff": f"{float(d.max()):.6e}",
                "max_rel_diff_elem": f"{float(rel.max()):.6e}" if rel.size else "",
                "median_rel_diff_elem": f"{float(np.median(rel)):.6e}" if rel.size else "",
                "frac_elems_excluded_small": f"{1.0 - m.mean():.4f}",
                "max_rel_l2_row": f"{float(l2.max()):.6e}",
                "median_rel_l2_row": f"{float(np.median(l2)):.6e}",
                "agrees_1e-5": str(bool(rel.size and rel.max() <= 1e-5)),
            })
        # patch-level diagnostics, run whether or not the embeddings agreed
        if os.path.isfile(newpatch) and os.path.isfile(benchpatch):
            an, ab = attrs_json(newpatch), attrs_json(benchpatch)
            kn = "img" if "img" in an["datasets"] else ("imgs" if "imgs" in an["datasets"] else "images")
            kb = "img" if "img" in ab["datasets"] else ("imgs" if "imgs" in ab["datasets"] else "images")
            rec.update({
                "n_patches_new": an["datasets"][kn]["shape"][0],
                "n_patches_bench": ab["datasets"][kb]["shape"][0],
                "patch_shape_new": "x".join(str(x) for x in an["datasets"][kn]["shape"][1:]),
                "patch_shape_bench": "x".join(str(x) for x in ab["datasets"][kb]["shape"][1:]),
                "patch_dtype_new": an["datasets"][kn]["dtype"],
                "patch_dtype_bench": ab["datasets"][kb]["dtype"],
                "patch_attrs_new": json.dumps(an, sort_keys=True),
                "patch_attrs_bench": json.dumps(ab, sort_keys=True),
            })
            with h5py.File(newpatch, "r") as fn, h5py.File(benchpatch, "r") as fb:
                pn = barcodes_of(fn["barcodes"][:] if "barcodes" in fn else fn["barcode"][:])
                pb = barcodes_of(fb["barcodes"][:] if "barcodes" in fb else fb["barcode"][:])
                shared = np.array(sorted(set(pn) & set(pb)))
                take = shared[np.linspace(0, len(shared) - 1, min(32, len(shared))).astype(int)] \
                    if len(shared) else shared
                rec["n_patch_barcodes_compared"] = int(len(take))
                if len(take) and an["datasets"][kn]["shape"][1:] == ab["datasets"][kb]["shape"][1:]:
                    mn = {b: i for i, b in enumerate(pn)}
                    mb = {b: i for i, b in enumerate(pb)}
                    dmax, ndiff, ntot = 0, 0, 0
                    cmax = 0
                    for b in take:
                        x = fn[kn][mn[b]].astype(np.int64)
                        y = fb[kb][mb[b]].astype(np.int64)
                        dd = np.abs(x - y)
                        dmax = max(dmax, int(dd.max()))
                        ndiff += int((dd != 0).sum())
                        ntot += dd.size
                        cmax = max(cmax, int(np.abs(fn["coords"][mn[b]].astype(np.int64)
                                                    - fb["coords"][mb[b]].astype(np.int64)).max()))
                    rec.update({"max_abs_img_diff": str(dmax),
                                "frac_img_bytes_differing": f"{ndiff / max(ntot, 1):.6f}",
                                "max_abs_coord_diff": str(cmax)})
    except Exception as exc:
        rec["error"] = f"{type(exc).__name__}: {exc}"
    rows.append(rec)
    print(f"  ANCHOR {sid} matched {rec['n_barcodes_matched']} "
          f"max_rel_elem {rec['max_rel_diff_elem']} median_rel_elem {rec['median_rel_diff_elem']} "
          f"max_rel_l2 {rec['max_rel_l2_row']} agrees {rec['agrees_1e-5']} {rec['error']}",
          flush=True)

apath = os.path.join(EMB, f"anchor_check__{args.set_name}__{args.encoder}.csv")
if rows:
    with open(apath, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def fnum(rs, key):
    return [float(r[key]) for r in rs if r[key] not in ("", None)]


ok = [r for r in rows if not r["error"]]
summary = {
    "set": args.set_name, "encoder": args.encoder,
    "n_samples": len(members),
    "n_written": sum(1 for r in log if r["status"] == "written"),
    "n_cached": sum(1 for r in log if r["status"] == "cached"),
    "n_missing_patches": sum(1 for r in log if r["status"] == "MISSING_PATCHES"),
    "patches_embedded": sum(r["n_patches"] for r in log if r["status"] == "written"),
    "seconds_extraction": round(sum(r["seconds"] for r in log), 1),
    "n_anchor_samples": len(rows),
    "n_anchor_errors": len(rows) - len(ok),
    "anchor_barcodes_matched_total": sum(r["n_barcodes_matched"] for r in ok
                                         if r["n_barcodes_matched"] > 0),
    "anchor_max_rel_diff_elem": max(fnum(ok, "max_rel_diff_elem"), default=None),
    "anchor_median_of_median_rel_diff_elem": (
        float(np.median(fnum(ok, "median_rel_diff_elem")))
        if fnum(ok, "median_rel_diff_elem") else None),
    "anchor_max_rel_l2_row": max(fnum(ok, "max_rel_l2_row"), default=None),
    "anchor_median_of_median_rel_l2_row": (
        float(np.median(fnum(ok, "median_rel_l2_row")))
        if fnum(ok, "median_rel_l2_row") else None),
    "anchor_all_agree_1e-5": all(r["agrees_1e-5"] == "True" for r in ok) if ok else None,
    "anchor_samples_disagreeing": [r["sample_id"] for r in ok if r["agrees_1e-5"] != "True"],
    "anchor_barcode_sets_identical_all": all(r["barcode_sets_identical"] == "True" for r in ok)
                                          if ok else None,
    "anchor_row_order_identical_all": all(r["row_order_identical"] == "True" for r in ok)
                                       if ok else None,
    "anchor_max_abs_img_diff": max(fnum(ok, "max_abs_img_diff"), default=None),
    "anchor_max_abs_coord_diff": max(fnum(ok, "max_abs_coord_diff"), default=None),
    "env": env_facts,
    "config": {"seed": SEED, "batch_size": BATCH, "num_workers": WORKERS},
}
spath = os.path.join(EMB, f"d2_summary__{args.set_name}__{args.encoder}.json")
json.dump(summary, open(spath, "w"), indent=2, default=str)
print("SUMMARY " + json.dumps({k: v for k, v in summary.items() if k != "env"}, default=str),
      flush=True)

# ------------------------------------------------------------------ provenance
blob = json.dumps(CFG, sort_keys=True, separators=(",", ":")).encode()
cfg_hash = f"sha256:{hashlib.sha256(blob).hexdigest()[:32]} crc32:{zlib.crc32(blob):08x}"
prov = os.path.join(EMB, f"PROVENANCE__{args.set_name}__{args.encoder}.txt")
lines = [
    f"dir              : {out_dir}",
    f"stage            : round3 D2 (patch embeddings, set={args.set_name}, encoder={args.encoder})",
    "script           : code/scripts/round3_d2_embed.py (staged as d2.py in the job workdir)",
    "extraction_path  : hest.bench.benchmark.embed_tiles + hest.bench.st_dataset.H5PatchDataset"
    " + trident.patch_encoder_models.encoder_factory, the same calls"
    " hest.bench.benchmark.predict_single_split makes, with round-1 config values",
    f"created          : {dt.datetime.now().astimezone().isoformat()}",
    "operator         : weiyang (Nicolas Weiyang Zhang)",
    f"command_line     : {sys.executable} " + " ".join(shlex.quote(a) for a in sys.argv),
    f"config_hash      : {cfg_hash}  (over d2_config.json, copied into {EMB})",
]
for k in sorted(env_facts):
    lines.append(f"{k:17}: {env_facts[k]}")
lines.append(f"seed             : {SEED}")
lines.append(f"batch_size       : {BATCH}")
lines.append(f"num_workers      : {WORKERS}")
lines.append("")
lines.append("## summary")
lines.append(json.dumps({k: v for k, v in summary.items() if k != "env"}, indent=2, default=str))
open(prov, "w").write("\n".join(lines) + "\n")

import shutil
shutil.copy(args.config, os.path.join(EMB, "d2_config.json"))
for f in [lp, apath, spath, prov]:
    if os.path.isfile(f):
        shutil.copy(f, os.path.basename(f))
print("DONE", flush=True)
