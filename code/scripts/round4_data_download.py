"""Round-4 stage P, P1: download one selected set from MahmoodLab/hest.

Follows `code/scripts/round3_d1_download.py` (the D1 machinery): the same four
components (patches, st, cellvit_seg, metadata), never wsis/ or anything else,
the same `snapshot_download` with `allow_patterns` built per sample from the D0
HuggingFace file listing, the same HEST-1k layout inside each set directory,
and the same file-by-file size verification against that listing.

Two differences from D1, both required by the round-4 instruction:

1. The per-sample relation checked is the SUBSET relation established by
   `round3_d1_patch_spot_audit.py` (every patch barcode is an expression
   barcode), with the unpatched fraction recorded per sample. D1's original
   test, patch count equals spot count, is stale: it fails on valid samples,
   because HEST's patching drops spots near the section edge. The stale test is
   still computed and reported beside the subset relation, but it is not an
   acceptance criterion.
2. Nothing is written at `ext_root`. D1 writes d1_summary.json, PROVENANCE.txt
   and the verification table at the root of `hest_ext/`, where the round-3
   records live. This script writes its tables into the job working directory
   and only `PROVENANCE.txt` and `_provenance.json` into the new set directory
   it creates.

usage: round4_data_download.py --set <set_name> [--config round4_p1_config.json]
"""
import argparse
import csv
import datetime as dt
import gzip
import hashlib
import json
import os
import platform
import shlex
import subprocess
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--set", dest="set_name", required=True)
ap.add_argument("--config", default="round4_p1_config.json")
ap.add_argument("--out-dir", default=".")
args = ap.parse_args()

CFG = json.load(open(args.config))
PROJ = CFG["project_root"]
EXT = CFG["ext_root"]
PINNED = CFG["pinned_revision"]
COMPONENTS = set(CFG["components"])
SET = args.set_name
SPEC = CFG["sets"][SET]
MEMBERS = sorted(SPEC["members"])
RESUNC = SPEC.get("resolution_uncertain", {})
OUT = os.path.abspath(args.out_dir)
os.makedirs(OUT, exist_ok=True)
SET_DIR = os.path.join(EXT, SET)


def sh(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (p.stdout + p.stderr).rstrip()


def storage_snapshot(label):
    return "\n".join([
        f"## {label} ({dt.datetime.now().astimezone().isoformat()})",
        "### df -h /work",
        sh("df -h /work"),
        "### quota -s",
        sh("quota -s 2>&1 | head -8"),
        f"### du -s --block-size=1 {SET_DIR}",
        sh(f"du -s --block-size=1 {shlex.quote(SET_DIR)} 2>&1"),
        "",
    ])


# ---------------------------------------------------------------- expected files
listing = os.path.join(PROJ, CFG["listing_rel"])
expected = {}
with gzip.open(listing, "rt", newline="") as fh:
    for row in csv.DictReader(fh):
        if row["kind"] != "file":
            continue
        path = row["path"]
        comp, _, base = path.partition("/")
        if comp not in COMPONENTS or not base:
            continue
        stem = base.split(".")[0]
        sid = stem[:-len("_cellvit_seg")] if stem.endswith("_cellvit_seg") else stem
        if sid in set(MEMBERS):
            expected.setdefault(sid, {})[path] = int(float(row["size_bytes"]))

missing_ids = sorted(set(MEMBERS) - set(expected))
if missing_ids:
    sys.exit(f"FATAL: no listed files for {missing_ids}")

n_files_expected = sum(len(v) for v in expected.values())
bytes_expected = sum(sum(v.values()) for v in expected.values())
print(f"set {SET}: {len(MEMBERS)} samples, {n_files_expected} files, {bytes_expected} bytes "
      f"expected from {CFG['listing_rel']}", flush=True)
if "expect" in SPEC:
    e = SPEC["expect"]
    assert len(MEMBERS) == e["n_samples"], (len(MEMBERS), e["n_samples"])
    assert n_files_expected == e["n_files"], (n_files_expected, e["n_files"])
    assert bytes_expected == e["bytes"], (bytes_expected, e["bytes"])
    print("PRECHECK ok: sample count, file count and byte total match the selection table",
          flush=True)

os.makedirs(SET_DIR, exist_ok=True)
before = storage_snapshot("BEFORE")
print(before, flush=True)

# ---------------------------------------------------------------- revision check
from huggingface_hub import HfApi, snapshot_download
import huggingface_hub

api = HfApi()
current_main = api.dataset_info(CFG["repo_id"], revision="main").sha
if current_main == PINNED:
    revision_used = PINNED
    rev_note = (f"pinned revision {PINNED}; repository main is now {current_main} (identical); "
                f"the pinned revision is used")
else:
    revision_used = current_main
    rev_note = (f"pinned revision {PINNED}; repository main has moved to {current_main}; "
                f"per the round-4 instruction the newer revision is used for this set only, "
                f"and both are recorded")
print("REVISION " + rev_note, flush=True)

# ---------------------------------------------------------------- download
patterns = sorted(p for s in MEMBERS for p in expected[s])
t0 = dt.datetime.now()
print(f"[{t0.isoformat()}] downloading {len(patterns)} files -> {SET_DIR}", flush=True)
snapshot_download(
    repo_id=CFG["repo_id"],
    repo_type="dataset",
    revision=revision_used,
    allow_patterns=patterns,
    local_dir=SET_DIR,
    max_workers=8,
)
transfer_seconds = (dt.datetime.now() - t0).total_seconds()
bytes_on_disk = sum(os.path.getsize(os.path.join(SET_DIR, p))
                    for s in MEMBERS for p in expected[s]
                    if os.path.isfile(os.path.join(SET_DIR, p)))
print(f"  transfer done in {transfer_seconds:.0f}s, {bytes_on_disk} bytes on disk "
      f"({bytes_on_disk / max(transfer_seconds, 1e-9) / 1e6:.0f} MB/s)", flush=True)

after = storage_snapshot("AFTER")
print(after, flush=True)

# ---------------------------------------------------------------- verification
import h5py
import numpy as np


def _bc(arr):
    a = np.asarray(arr).reshape(-1)
    return np.array([x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in a])


def patch_info(path):
    with h5py.File(path, "r") as f:
        key = "img" if "img" in f else ("imgs" if "imgs" in f else "images")
        bkey = "barcodes" if "barcodes" in f else ("barcode" if "barcode" in f else None)
        n_img = int(f[key].shape[0])
        shape = "x".join(str(int(x)) for x in f[key].shape[1:])
        bcs = _bc(f[bkey][:]) if bkey else np.array([], dtype=object)
        return n_img, shape, bcs


def st_barcodes(path):
    with h5py.File(path, "r") as f:
        obs = f["obs"]
        idx = obs.attrs.get("_index", "_index")
        if isinstance(idx, bytes):
            idx = idx.decode()
        return _bc(obs[idx][:])


FIELDS = ["set", "sample_id", "n_files_expected", "n_files_present", "n_files_size_mismatch",
          "bytes_expected", "bytes_present", "missing_files", "size_mismatch_detail",
          "n_patches", "n_patch_barcodes_unique", "patch_shape", "n_expr_spots",
          "n_expr_barcodes_unique", "subset_holds", "n_patch_barcodes_not_in_expr",
          "example_patch_barcodes_not_in_expr", "n_expr_spots_without_a_patch",
          "unpatched_fraction", "patch_barcodes_unique", "expr_barcodes_unique",
          "patch_count_equals_spot_count_STALE", "resolution_uncertain", "verified", "error"]

ver = []
for sid in MEMBERS:
    rec = {k: "" for k in FIELDS}
    rec.update({"set": SET, "sample_id": sid, "n_files_expected": len(expected[sid]),
                "n_files_present": 0, "n_files_size_mismatch": 0,
                "bytes_expected": sum(expected[sid].values()), "bytes_present": 0,
                "n_patches": -1, "n_patch_barcodes_unique": -1, "n_expr_spots": -1,
                "n_expr_barcodes_unique": -1, "n_patch_barcodes_not_in_expr": -1,
                "n_expr_spots_without_a_patch": -1,
                "resolution_uncertain": str(bool(RESUNC.get(sid, False)))})
    miss, mism = [], []
    for p, size in sorted(expected[sid].items()):
        fp = os.path.join(SET_DIR, p)
        if not os.path.isfile(fp):
            miss.append(p)
            continue
        rec["n_files_present"] += 1
        got = os.path.getsize(fp)
        rec["bytes_present"] += got
        if got != size:
            mism.append(f"{p}:{got}!={size}")
    rec["missing_files"] = ";".join(miss)
    rec["size_mismatch_detail"] = ";".join(mism)
    rec["n_files_size_mismatch"] = len(mism)
    try:
        n_img, shape, pb = patch_info(os.path.join(SET_DIR, f"patches/{sid}.h5"))
        sb = st_barcodes(os.path.join(SET_DIR, f"st/{sid}.h5ad"))
        pset, sset = set(pb), set(sb)
        extra = sorted(pset - sset)
        without = sset - pset
        rec.update({
            "n_patches": n_img, "patch_shape": shape,
            "n_patch_barcodes_unique": len(pset),
            "n_expr_spots": int(len(sb)), "n_expr_barcodes_unique": len(sset),
            "subset_holds": str(len(extra) == 0),
            "n_patch_barcodes_not_in_expr": len(extra),
            "example_patch_barcodes_not_in_expr": ";".join(extra[:3]),
            "n_expr_spots_without_a_patch": len(without),
            "unpatched_fraction": f"{len(without) / max(len(sset), 1):.6f}",
            "patch_barcodes_unique": str(len(pset) == len(pb)),
            "expr_barcodes_unique": str(len(sset) == len(sb)),
            "patch_count_equals_spot_count_STALE": str(n_img == len(sb)),
        })
    except Exception as exc:
        rec["error"] = f"{type(exc).__name__}: {exc}"
    rec["verified"] = str(not rec["missing_files"] and rec["n_files_size_mismatch"] == 0
                          and rec["subset_holds"] == "True" and not rec["error"])
    ver.append(rec)
    print(f"  {sid} files {rec['n_files_present']}/{rec['n_files_expected']} "
          f"mismatch {rec['n_files_size_mismatch']} patches {rec['n_patches']} "
          f"spots {rec['n_expr_spots']} subset {rec['subset_holds']} "
          f"unpatched {rec['unpatched_fraction']} verified {rec['verified']} {rec['error']}",
          flush=True)

fail_missing = [r["sample_id"] for r in ver if r["missing_files"]]
fail_size = [r["sample_id"] for r in ver if r["n_files_size_mismatch"]]
fail_subset = [r["sample_id"] for r in ver if r["subset_holds"] != "True"]
dropped = [r["sample_id"] for r in ver if r["verified"] != "True"]
unp = sorted(float(r["unpatched_fraction"]) for r in ver if r["unpatched_fraction"] != "")

blob = json.dumps(CFG, sort_keys=True, separators=(",", ":")).encode()
cfg_hash = f"sha256:{hashlib.sha256(blob).hexdigest()[:32]}"
script_md5 = hashlib.md5(open(os.path.abspath(__file__), "rb").read()).hexdigest()

summary = {
    "stage": "round4_P1_download",
    "set": SET,
    "n_samples": len(ver),
    "n_files_expected": n_files_expected,
    "n_files_present": sum(r["n_files_present"] for r in ver),
    "bytes_expected": bytes_expected,
    "bytes_present": sum(r["bytes_present"] for r in ver),
    "gb_present": round(sum(r["bytes_present"] for r in ver) / 1e9, 3),
    "transfer_seconds": round(transfer_seconds, 1),
    "transfer_MBps": round(bytes_on_disk / max(transfer_seconds, 1e-9) / 1e6, 1),
    "samples_with_missing_files": fail_missing,
    "samples_with_size_mismatch": fail_size,
    "samples_subset_relation_fails": fail_subset,
    "samples_dropped_unverified": dropped,
    "n_verified": sum(1 for r in ver if r["verified"] == "True"),
    "n_patches_total": sum(r["n_patches"] for r in ver if r["n_patches"] > 0),
    "n_expr_spots_total": sum(r["n_expr_spots"] for r in ver if r["n_expr_spots"] > 0),
    "unpatched_fraction_min": unp[0] if unp else None,
    "unpatched_fraction_median": unp[len(unp) // 2] if unp else None,
    "unpatched_fraction_max": unp[-1] if unp else None,
    "n_resolution_uncertain": sum(1 for r in ver if r["resolution_uncertain"] == "True"),
    "n_stale_patch_count_equals_spot_count": sum(
        1 for r in ver if r["patch_count_equals_spot_count_STALE"] == "True"),
    "hf_repo": CFG["repo_id"],
    "hf_revision_pinned": PINNED,
    "hf_main_revision_now": current_main,
    "hf_revision_used": revision_used,
    "revision_note": rev_note,
    "huggingface_hub_version": huggingface_hub.__version__,
    "components": sorted(COMPONENTS),
    "script_md5": script_md5,
    "config_hash": cfg_hash,
    "slurm_job_id": os.environ.get("SLURM_JOB_ID", "NA"),
    "slurm_partition": os.environ.get("SLURM_JOB_PARTITION", "NA"),
    "slurm_nodelist": os.environ.get("SLURM_JOB_NODELIST", "NA"),
    "node": platform.node(),
    "pythonhashseed": os.environ.get("PYTHONHASHSEED", "unset"),
    "created": dt.datetime.now().astimezone().isoformat(),
}

# summary first, then the per-sample table
spath = os.path.join(OUT, f"p1_summary__{SET}.json")
json.dump(summary, open(spath, "w"), indent=2)
print("SUMMARY " + json.dumps(summary), flush=True)

vpath = os.path.join(OUT, f"p1_verification__{SET}.csv")
with open(vpath, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(ver)

# ---------------------------------------------------------------- provenance
lines = [
    f"dir              : {SET_DIR}",
    f"stage            : round4 stage P, P1 (download of set {SET})",
    "script           : code/scripts/round4_data_download.py",
    f"script_md5       : {script_md5}  (md5 of the file that ran, computed inside the job)",
    f"created          : {dt.datetime.now().astimezone().isoformat()}",
    "operator         : weiyang (Nicolas Weiyang Zhang)",
    f"slurm_job_id     : {os.environ.get('SLURM_JOB_ID', 'NA')}",
    f"slurm_partition  : {os.environ.get('SLURM_JOB_PARTITION', 'NA')}  (partition actually used)",
    f"slurm_nodelist   : {os.environ.get('SLURM_JOB_NODELIST', 'NA')}",
    f"node             : {platform.node()}",
    f"platform         : {platform.platform()}",
    f"python           : {platform.python_version()}",
    f"executable       : {sys.executable}",
    f"commit           : {CFG.get('repo_commit', 'NA')}  (working copy commit recorded in the "
    f"config; this script runs no git command)",
    f"command_line     : {sys.executable} " + " ".join(shlex.quote(a) for a in sys.argv),
    f"pythonhashseed   : {os.environ.get('PYTHONHASHSEED', 'unset')}",
    f"config_hash      : {cfg_hash}  (over the config below, copied into this directory as "
    f"round4_p1_config__{SET}.json)",
    f"config           : {json.dumps(CFG, sort_keys=True)}",
    f"hf_repo          : {CFG['repo_id']}",
    f"hf_revision_used : {revision_used}",
    f"hf_revision_note : {rev_note}",
    f"huggingface_hub  : {huggingface_hub.__version__}",
    f"components       : {sorted(COMPONENTS)}  (no wsis/, no transcripts/, no xenium_seg/, "
    f"nothing else)",
    f"bytes_downloaded : {summary['bytes_present']} over {summary['n_files_present']} files "
    f"in {summary['transfer_seconds']} s",
    f"verification     : file sizes against {CFG['listing_rel']}; the subset relation "
    f"(every patch barcode is an expression barcode), which replaces D1's stale "
    f"patch-count-equals-spot-count test",
    f"n_verified       : {summary['n_verified']} / {len(ver)}",
    f"dropped          : {dropped if dropped else 'none'}",
    "",
    f"## sample list ({len(MEMBERS)})",
    ";".join(MEMBERS),
    "",
    "## storage before and after",
    before,
    after,
]
open(os.path.join(SET_DIR, "PROVENANCE.txt"), "w").write("\n".join(lines) + "\n")
json.dump(CFG, open(os.path.join(SET_DIR, f"round4_p1_config__{SET}.json"), "w"), indent=2)

stamp = {
    "writer": "claude-science",
    "project_id": CFG["stamp"]["project_id"],
    "frame_id": CFG["stamp"]["frame_id"],
    "track": CFG["stamp"]["track"],
    "plan": CFG["stamp"]["plan"],
    "note": f"round4 stage P, P1 download of set {SET} "
            f"({len(MEMBERS)} samples, four components, HEST revision {revision_used})",
    "host": platform.node(),
    "created_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
}
spj = os.path.join(SET_DIR, "_provenance.json")
if os.path.isfile(spj):
    old = json.load(open(spj))
    if old.get("frame_id") != stamp["frame_id"]:
        sys.exit(f"FATAL: {spj} already belongs to frame {old.get('frame_id')}; not overwriting")
json.dump(stamp, open(spj, "w"), indent=2)

import shutil
for f in (os.path.join(SET_DIR, "PROVENANCE.txt"), spj):
    shutil.copy(f, os.path.join(OUT, f"{os.path.basename(f)}__{SET}"))

ok = not (fail_missing or fail_size or fail_subset)
print(f"ACCEPT set={SET} samples={len(ver)} verified={summary['n_verified']} "
      f"files={summary['n_files_present']}/{n_files_expected} "
      f"size_mismatches={sum(r['n_files_size_mismatch'] for r in ver)} "
      f"subset_fails={len(fail_subset)} bytes={summary['bytes_present']}", flush=True)
print("OK" if ok else "FAILURES PRESENT", flush=True)
