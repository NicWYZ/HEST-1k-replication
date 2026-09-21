#!/usr/bin/env python
"""Generate MANIFEST.md: path, size and SHA256 of every large artifact deliberately
left on Longleaf rather than committed. Run from the project root before each push.

Stage: closeout, regenerating MANIFEST.md so it covers everything round 2 added on
Longleaf -- instrumentation/round2_intercept, round2_intercept_f64, morphology_v2, and
the per-gene parquets under results/round2/R3_splits/ -- with sizes and hashes
(deck_figures_and_repo_update.md section 2.4).
"""
import os, hashlib, datetime, sys

ROOT = "/work/users/w/e/weiyang/hest_replication"
# Untracked-but-important trees. Directories are summarised; files are hashed individually.
TARGETS = [
    ("bench_data",     "hest-bench snapshot (GATED - MahmoodLab/hest-bench)"),
    ("embeddings",     "per-encoder per-sample patch embeddings (HDF5)"),
    ("instrumentation","Stage 4 joined tables"),
]
# Trees walked for individual per-file hashing (results/ dumps, and now instrumentation/
# tables -- 390 parquets, none over 1 GB, so hashing all of them is feasible).
HASH_ROOTS = ["results", "instrumentation"]
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
# Absolute, trailing-slash-qualified prefixes of the summarised target trees, used below to
# avoid double-counting a file both in its tree's summary total and in the per-file hash walk.
TARGET_DIR_PREFIXES = tuple(os.path.join(ROOT, rel) + os.sep for rel, _ in TARGETS)

for rel, desc in TARGETS:
    d = os.path.join(ROOT, rel)
    if not os.path.isdir(d):
        continue
    nf = nb = 0
    sub_stats = {}   # one-level-down child name -> [files, bytes]
    for dp, _, fns in os.walk(d):
        relpath = os.path.relpath(dp, d)
        top = relpath.split(os.sep)[0] if relpath != "." else None
        key = top if top is not None else "(files directly in this directory)"
        for fn in fns:
            fp = os.path.join(dp, fn)
            if os.path.islink(fp): continue
            try: sz = os.path.getsize(fp)
            except OSError: continue
            nf += 1; nb += sz
            e = sub_stats.setdefault(key, [0, 0])
            e[0] += 1; e[1] += sz
    grand_files += nf; grand_bytes += nb
    L += [f"## `{rel}/`", "", f"{desc}", "", f"- files: {nf:,}", f"- total size: {human(nb)}", ""]
    # (a) one-level-down breakdown so a reader can see which subtrees are present.
    L += [f"Subtrees of `{rel}/`:", "",
          "| subtree | files | size |", "|---|---|---|"]
    for name in sorted(sub_stats.keys()):
        snf, snb = sub_stats[name]
        label = name if name.startswith("(") else f"{rel}/{name}/"
        L.append(f"| `{label}` | {snf:,} | {human(snb)} |")
    L.append("")

# (b) Individually hash the per-split inference dumps (results/) AND the instrumentation/
# joined tables (390 parquets, none over 1 GB) -- the scientifically load-bearing binaries.
L += ["## Individually hashed files", "",
      "Every `.pkl`/`.parquet` under `results/` and every `.pkl`/`.parquet` under",
      "`instrumentation/` is hashed below. Files under `instrumentation/` were already",
      "counted in that tree's summary above, so they are **not** added a second time to",
      "the grand total.", "",
      "| path (relative to root) | size | sha256 |", "|---|---|---|"]
rows = 0
for hroot in HASH_ROOTS:
    base = os.path.join(ROOT, hroot)
    if not os.path.isdir(base):
        continue
    for dp, _, fns in os.walk(base):
        for fn in sorted(fns):
            if os.path.splitext(fn)[1] not in HASH_EXT: continue
            fp = os.path.join(dp, fn)
            if os.path.islink(fp): continue
            try: sz = os.path.getsize(fp)
            except OSError: continue
            dig = sha256(fp) if sz <= MAX_HASH_BYTES else "(skipped - too large)"
            L.append(f"| `{os.path.relpath(fp, ROOT)}` | {human(sz)} | `{dig}` |")
            rows += 1
            # (c) skip the grand-total increment for any path already counted in a
            # summarised target tree above (currently: instrumentation/).
            if not fp.startswith(TARGET_DIR_PREFIXES):
                grand_files += 1
                grand_bytes += sz
L += ["", f"**{rows:,} files hashed individually.**",
      "", f"Grand total across all untracked artifacts: {grand_files:,} files, {human(grand_bytes)}.", ""]

out = os.path.join(ROOT, "MANIFEST.md")
open(out, "w").write("\n".join(L))
print(f"wrote {out}: {rows} hashed files, {grand_files} files, {human(grand_bytes)}")
