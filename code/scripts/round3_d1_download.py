"""Round-3 D1: download the three approved expansion sets from MahmoodLab/hest.

Four components only (patches, st, cellvit_seg, metadata); never wsis/ or any
other component. HEST-1k's own layout is kept inside each set directory. Sets
overlap, so each sample has exactly one physical home, assigned by the set
order in the config (kidney, breast Xenium, platform-pair).

Then verifies: every expected file present with the byte size recorded in the
D0 HuggingFace listing, and per sample the patch count against the expression
file's spot count.
"""
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
import zlib

CFG = json.load(open("d1_config.json"))
PROJ = CFG["project_root"]
EXT = CFG["ext_root"]
PINNED = CFG["pinned_revision"]
COMPONENTS = set(CFG["components"])
ALL_IDS = sorted({s for v in CFG["sets"].values() for s in v["members"]})
EXPECTED_IDS = set(ALL_IDS)


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
        "### du -s --block-size=1 hest_ext",
        sh(f"du -s --block-size=1 {shlex.quote(EXT)} 2>&1"),
        "",
    ])


# ---------------------------------------------------------------- expected files
listing = os.path.join(PROJ, CFG["listing_rel"])
expected = {}   # sample -> {relpath: size_bytes}
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
        if sid in EXPECTED_IDS:
            expected.setdefault(sid, {})[path] = int(float(row["size_bytes"]))

missing_ids = sorted(EXPECTED_IDS - set(expected))
if missing_ids:
    sys.exit(f"FATAL: no listed files for {missing_ids}")
for sid, files in sorted(expected.items()):
    comps = {p.split("/", 1)[0] for p in files}
    if comps != COMPONENTS:
        print(f"WARN {sid}: components present in listing = {sorted(comps)}", flush=True)

print(f"expected {sum(len(v) for v in expected.values())} files over {len(expected)} samples, "
      f"{sum(sum(v.values()) for v in expected.values())} bytes", flush=True)

os.makedirs(EXT, exist_ok=True)
before = storage_snapshot("BEFORE")
print(before, flush=True)

# ---------------------------------------------------------------- revision check
from huggingface_hub import HfApi, snapshot_download
import huggingface_hub

api = HfApi()
info = api.dataset_info(CFG["repo_id"], revision="main")
current_main = info.sha
rev_note = (f"pinned revision {PINNED}; repository main is now {current_main}"
            + (" (identical)" if current_main == PINNED
               else " -- HuggingFace has moved on since D0; the pinned revision is used anyway"))
print(rev_note, flush=True)

# ---------------------------------------------------------------- download
home_map = []
download_log = []
for set_name in CFG["set_order"]:
    owned = CFG["sets"][set_name]["owned"]
    local_dir = os.path.join(EXT, set_name)
    patterns = sorted(p for s in owned for p in expected[s])
    t0 = dt.datetime.now()
    print(f"[{t0.isoformat()}] {set_name}: {len(owned)} samples, {len(patterns)} files "
          f"-> {local_dir}", flush=True)
    snapshot_download(
        repo_id=CFG["repo_id"],
        repo_type="dataset",
        revision=PINNED,
        allow_patterns=patterns,
        local_dir=local_dir,
        max_workers=8,
    )
    got = 0
    for s in owned:
        for p in expected[s]:
            fp = os.path.join(local_dir, p)
            if os.path.isfile(fp):
                got += os.path.getsize(fp)
        home_map.append({"sample_id": s, "home_set": set_name,
                         "member_of_sets": ";".join(sorted(
                             k for k, v in CFG["sets"].items() if s in v["members"]))})
    secs = (dt.datetime.now() - t0).total_seconds()
    download_log.append({"set": set_name, "n_samples_owned": len(owned),
                         "n_files": len(patterns), "bytes_on_disk": got,
                         "seconds": round(secs, 1)})
    print(f"  done in {secs:.0f}s, {got} bytes on disk", flush=True)

after = storage_snapshot("AFTER")
print(after, flush=True)

# ---------------------------------------------------------------- verification
import h5py

home = {h["sample_id"]: h["home_set"] for h in home_map}


def spot_count(h5ad_path):
    with h5py.File(h5ad_path, "r") as f:
        obs = f["obs"]
        idx = obs.attrs.get("_index", "_index")
        if isinstance(idx, bytes):
            idx = idx.decode()
        return int(obs[idx].shape[0])


def patch_probe(h5_path):
    with h5py.File(h5_path, "r") as f:
        key = "img" if "img" in f else ("imgs" if "imgs" in f else "images")
        bkey = "barcodes" if "barcodes" in f else ("barcode" if "barcode" in f else None)
        return (int(f[key].shape[0]),
                (int(f[bkey].shape[0]) if bkey else -1),
                tuple(int(x) for x in f[key].shape[1:]),
                sorted(f.keys()))


ver = []
for sid in ALL_IDS:
    set_name = home[sid]
    d = os.path.join(EXT, set_name)
    rec = {"sample_id": sid, "home_set": set_name,
           "n_files_expected": len(expected[sid]), "n_files_present": 0,
           "n_files_size_mismatch": 0, "bytes_expected": sum(expected[sid].values()),
           "bytes_present": 0, "missing_files": "", "size_mismatch_detail": "",
           "n_patches": -1, "n_patch_barcodes": -1, "patch_shape": "",
           "n_spots_st": -1, "patch_count_equals_spot_count": "",
           "patches_h5_keys": "", "error": ""}
    miss, mism = [], []
    for p, size in sorted(expected[sid].items()):
        fp = os.path.join(d, p)
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
        n_img, n_bc, shp, keys = patch_probe(os.path.join(d, f"patches/{sid}.h5"))
        rec.update({"n_patches": n_img, "n_patch_barcodes": n_bc,
                    "patch_shape": "x".join(str(x) for x in shp),
                    "patches_h5_keys": ";".join(keys)})
        rec["n_spots_st"] = spot_count(os.path.join(d, f"st/{sid}.h5ad"))
        rec["patch_count_equals_spot_count"] = str(rec["n_patches"] == rec["n_spots_st"])
    except Exception as exc:
        rec["error"] = f"{type(exc).__name__}: {exc}"
    ver.append(rec)
    print(f"  {sid} {set_name} files {rec['n_files_present']}/{rec['n_files_expected']} "
          f"mismatch {rec['n_files_size_mismatch']} patches {rec['n_patches']} "
          f"spots {rec['n_spots_st']} eq {rec['patch_count_equals_spot_count']} "
          f"{rec['error']}", flush=True)

vpath = os.path.join(EXT, "d1_verification.csv")
with open(vpath, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(ver[0].keys()))
    w.writeheader()
    w.writerows(ver)

hpath = os.path.join(EXT, "sample_home_map.csv")
with open(hpath, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["sample_id", "home_set", "member_of_sets"])
    w.writeheader()
    w.writerows(sorted(home_map, key=lambda r: r["sample_id"]))

fail_missing = [r["sample_id"] for r in ver if r["missing_files"]]
fail_size = [r["sample_id"] for r in ver if r["n_files_size_mismatch"]]
fail_count = [r["sample_id"] for r in ver if r["patch_count_equals_spot_count"] != "True"]
summary = {
    "n_samples": len(ver),
    "n_files_expected": sum(r["n_files_expected"] for r in ver),
    "n_files_present": sum(r["n_files_present"] for r in ver),
    "bytes_expected": sum(r["bytes_expected"] for r in ver),
    "bytes_present": sum(r["bytes_present"] for r in ver),
    "samples_with_missing_files": fail_missing,
    "samples_with_size_mismatch": fail_size,
    "samples_patch_count_ne_spot_count": fail_count,
    "per_set": download_log,
    "revision_note": rev_note,
    "hf_revision_used": PINNED,
    "hf_main_revision_now": current_main,
    "huggingface_hub_version": huggingface_hub.__version__,
}
json.dump(summary, open(os.path.join(EXT, "d1_summary.json"), "w"), indent=2)
print("SUMMARY " + json.dumps({k: v for k, v in summary.items() if k != "per_set"}), flush=True)

# ---------------------------------------------------------------- provenance
blob = json.dumps(CFG, sort_keys=True, separators=(",", ":")).encode()
cfg_hash = f"sha256:{hashlib.sha256(blob).hexdigest()[:32]} crc32:{zlib.crc32(blob):08x}"
commit = sh(f"git -C {shlex.quote(PROJ)} rev-parse HEAD")
lines = [
    f"dir              : {EXT}",
    "stage            : round3 D1 (download of the three approved expansion sets)",
    "script           : code/scripts/round3_d1_download.py (staged as d1.py in the job workdir)",
    f"created          : {dt.datetime.now().astimezone().isoformat()}",
    "operator         : weiyang (Nicolas Weiyang Zhang)",
    f"slurm_job_id     : {os.environ.get('SLURM_JOB_ID', 'NA')}",
    f"slurm_partition  : {os.environ.get('SLURM_JOB_PARTITION', 'NA')}",
    f"slurm_nodelist   : {os.environ.get('SLURM_JOB_NODELIST', 'NA')}",
    f"node             : {platform.node()}",
    f"platform         : {platform.platform()}",
    f"python           : {platform.python_version()}",
    f"executable       : {sys.executable}",
    f"commit           : {commit}",
    f"command_line     : {sys.executable} " + " ".join(shlex.quote(a) for a in sys.argv),
    f"pythonhashseed   : {os.environ.get('PYTHONHASHSEED', 'unset')}",
    f"config           : {json.dumps({k: v for k, v in CFG.items() if k != 'sets'}, sort_keys=True)}",
    f"config_sets      : {json.dumps({k: {'n_members': len(v['members']), 'n_owned': len(v['owned'])} for k, v in CFG['sets'].items()}, sort_keys=True)}",
    f"config_hash      : {cfg_hash}  (over d1_config.json, copied into this directory)",
    f"hf_repo          : {CFG['repo_id']}",
    f"hf_revision_used : {PINNED}",
    f"hf_revision_note : {rev_note}",
    f"huggingface_hub  : {huggingface_hub.__version__}",
    f"components       : {sorted(COMPONENTS)}  (no wsis/, no transcripts/, no xenium_seg/, nothing else)",
    f"bytes_downloaded : {summary['bytes_present']} over {summary['n_files_present']} files",
    "",
    "## sets and physical homes (sets overlap; home is the first set in set_order containing the sample)",
]
for k, v in CFG["sets"].items():
    lines.append(f"{k}: members={len(v['members'])} owned={len(v['owned'])}")
lines.append("")
lines.append("## sample list, by home set")
for set_name in CFG["set_order"]:
    lines.append(f"{set_name} ({len(CFG['sets'][set_name]['owned'])}): "
                 + ";".join(CFG["sets"][set_name]["owned"]))
lines.append("")
lines.append("## per-set download")
for d in download_log:
    lines.append(f"{d['set']}: {d['n_samples_owned']} samples, {d['n_files']} files, "
                 f"{d['bytes_on_disk']} bytes, {d['seconds']} s")
lines.append("")
lines.append("## storage before and after")
lines.append(before)
lines.append(after)
open(os.path.join(EXT, "PROVENANCE.txt"), "w").write("\n".join(lines) + "\n")

import shutil
shutil.copy(os.path.join(EXT, "PROVENANCE.txt"), "PROVENANCE.txt")
shutil.copy(vpath, "d1_verification.csv")
shutil.copy(hpath, "sample_home_map.csv")
shutil.copy(os.path.join(EXT, "d1_summary.json"), "d1_summary.json")
shutil.copy("d1_config.json", os.path.join(EXT, "d1_config.json"))
print("OK" if not (fail_missing or fail_size or fail_count) else "FAILURES PRESENT", flush=True)
