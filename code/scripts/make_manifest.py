#!/usr/bin/env python
"""Generate MANIFEST.md: path, size and SHA256 of every large artifact deliberately
left on Longleaf rather than committed. Run from the project root before each push."""
import os, hashlib, datetime, sys

ROOT = "/work/users/w/e/weiyang/hest_replication"
# Untracked-but-important trees. Directories are summarised; files are hashed individually.
TARGETS = [
    ("bench_data",     "hest-bench snapshot (GATED - MahmoodLab/hest-bench)"),
    ("embeddings",     "per-encoder per-sample patch embeddings (HDF5)"),
    ("instrumentation","Stage 4 joined tables"),
]
HASH_EXT = {".pkl", ".parquet"}
MAX_HASH_BYTES = 2_000_000_000   # skip hashing anything absurd

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()

def human(n):
    for u in ("B","KB","MB","GB","TB"):
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"

L = ["# MANIFEST — large artifacts held on Longleaf", "",
     f"Generated: {datetime.datetime.now().isoformat(timespec='seconds')}",
     f"Host path root: `{ROOT}`", "",
     "These files are deliberately **not** committed: GitHub's 100 MB per-file limit, and",
     "`MahmoodLab/hest-bench` is a gated dataset (`inference_dump.pkl` contains `targets_all`,",
     "the measured expression). Hashes let a collaborator verify a copy obtained through",
     "proper channels.", ""]

grand_files = grand_bytes = 0
for rel, desc in TARGETS:
    d = os.path.join(ROOT, rel)
    if not os.path.isdir(d):
        continue
    nf = nb = 0
    for dp, _, fns in os.walk(d):
        for fn in fns:
            fp = os.path.join(dp, fn)
            if os.path.islink(fp): continue
            try: nb += os.path.getsize(fp)
            except OSError: continue
            nf += 1
    grand_files += nf; grand_bytes += nb
    L += [f"## `{rel}/`", "", f"{desc}", "", f"- files: {nf:,}", f"- total size: {human(nb)}", ""]

# Individually hash the per-split dumps (the scientifically load-bearing binaries)
L += ["## Per-split inference dumps", "",
      "| path (relative to root) | size | sha256 |", "|---|---|---|"]
rows = 0
for dp, _, fns in os.walk(os.path.join(ROOT, "results")):
    for fn in sorted(fns):
        if os.path.splitext(fn)[1] not in HASH_EXT: continue
        fp = os.path.join(dp, fn)
        try: sz = os.path.getsize(fp)
        except OSError: continue
        dig = sha256(fp) if sz <= MAX_HASH_BYTES else "(skipped - too large)"
        L.append(f"| `{os.path.relpath(fp, ROOT)}` | {human(sz)} | `{dig}` |")
        rows += 1; grand_files += 1; grand_bytes += sz
L += ["", f"**{rows:,} dump files hashed.**",
      "", f"Grand total across all untracked artifacts: {grand_files:,} files, {human(grand_bytes)}.", ""]

out = os.path.join(ROOT, "MANIFEST.md")
open(out, "w").write("\n".join(L))
print(f"wrote {out}: {rows} hashed dumps, {grand_files} files, {human(grand_bytes)}")
