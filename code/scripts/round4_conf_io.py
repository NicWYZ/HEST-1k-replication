#!/usr/bin/env python
"""Round 4, conformal track: shared I/O, provenance and read-time filters.

Stage: every stage of the conformal track (docs/round4_conf_plan.md). Nothing here computes a
result; it reads data the way the track's instruction requires and writes provenance.

THIS MODULE EDITS NO ROUND-3 FILE. It imports round3_d4_sets.py (and through it the harness)
unmodified, as a module, from ROUND3_SCRIPTS_DIR, which defaults to this file's own directory.

1. Dropped patch barcodes. The lung task file records NCBI865's patch barcode 051x019 under the
   top-level `dropped_patch_barcodes`, because it has no expression row. The embedding file still
   has 2,143 rows. Round 3's round3_d4_sets.load_set asserts that every embedding barcode is an
   expression barcode, so it raises on NCBI865 when called directly. `load_set_dropped` below
   takes the embedding rows through round 3's own patched_barcodes(), removes the dropped
   barcodes from the barcode list, X and the coordinates together, and only then asserts the
   subset relation. The assertion is kept, not relaxed.
2. Xenium control features. Any panel or target list read here has NegControl*,
   UnassignedCodeword* and BLANK* removed first, with the count removed returned so the caller
   records it (`drop_control_features`).
3. Provenance. `write_provenance` writes PROVENANCE.txt (job id, partition actually used, node,
   date, commit of the code clone, command line, config hash with its config, PYTHONHASHSEED,
   md5 of the executed script) and `stamp` writes the longleaf-provenance `_provenance.json` from
   the process that produced the directory, with the frame id passed in by that process.
"""
import hashlib
import importlib.util
import json
import os
import re
import socket
import subprocess
import sys
import zlib
from datetime import datetime, timezone

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
ROUND3_SCRIPTS_DIR = os.environ.get("ROUND3_SCRIPTS_DIR", _HERE)
DATA_ROOT = "/work/users/w/e/weiyang/hest_replication"   # the harness's ROOT; read-only here
HARNESS_MD5 = "0ad7ae8efe554c1f285e5f384a9fb7f5"
PROJECT_ID = "proj_3a4e23273fb6"
CONTROL_RE = re.compile(r"^(NegControl|UnassignedCodeword|BLANK)")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def seed(key):
    """Seeds from zlib.crc32 of a string key, never hash()."""
    return zlib.crc32(key.encode())


def import_round3(name):
    path = os.path.join(ROUND3_SCRIPTS_DIR, f"{name}.py")
    assert os.path.exists(path), f"{path} not found; set ROUND3_SCRIPTS_DIR"
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check_harness():
    p = os.path.join(ROUND3_SCRIPTS_DIR, "round3_a0_harness.py")
    got = md5(p)
    assert got == HARNESS_MD5, f"harness md5 {got} != {HARNESS_MD5}"
    return got


# ------------------------------------------------------------------ read-time filters
def drop_control_features(genes):
    """(kept list in input order, number removed)."""
    kept = [g for g in genes if not CONTROL_RE.match(str(g))]
    return kept, len(genes) - len(kept)


def dropped_barcodes(td, sid):
    return set(td.get("dropped_patch_barcodes", {}).get(sid, []))


def load_set_dropped(td, enc, genes_union, sample_ids=None, D4=None):
    """round3_d4_sets.load_set with the task file's dropped_patch_barcodes applied BEFORE the
    subset assertion. Returns X, Yraw, samp, bc, xy exactly as load_set does, plus a per-sample
    record {sid: (n_embedding_rows, n_dropped, n_kept)}.

    The body mirrors load_set line for line (read at round4-data-v2) except for the drop step,
    so for any sample with no dropped barcode the output is identical to load_set's.
    """
    import anndata as ad
    D4 = D4 or import_round3("round3_d4_sets")
    ids = sorted(sample_ids or [s["sample_id"] for s in td["samples"]])
    genes_union, n_ctrl = drop_control_features(list(genes_union))
    Xs, Ys, samp, bcs, xys, rec = [], [], [], [], [], {}
    for sid in ids:
        bc, X, xy = D4.patched_barcodes(td, sid, enc)
        drop = dropped_barcodes(td, sid)
        keep = np.array([b not in drop for b in bc], bool)
        assert int((~keep).sum()) == len(drop & set(bc)), f"{sid}: drop list mismatch"
        bc = [b for b, k in zip(bc, keep) if k]
        X, xy = X[keep], xy[keep]
        A = ad.read_h5ad(f"{D4.ROOT}/{td['paths']['adata'].format(sample_id=sid)}")
        assert set(bc) <= set(map(str, A.obs_names)), f"{sid}: patch barcode not in expression"
        sub = A[bc, genes_union]
        assert sub.n_obs == len(bc), f"{sid}: expression barcode index is not unique"
        Yr = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
        Xs.append(X)
        Ys.append(np.asarray(Yr, dtype=np.float32))
        samp += [sid] * len(bc)
        bcs += bc
        xys.append(xy)
        rec[sid] = (int(keep.size), int((~keep).sum()), int(keep.sum()))
        del A, sub
    return (np.vstack(Xs), np.vstack(Ys), np.array(samp), np.array(bcs, dtype=object),
            np.vstack(xys), rec, n_ctrl)


# ------------------------------------------------------------------ provenance
def code_head(clone=None):
    clone = clone or os.path.dirname(os.path.dirname(_HERE))
    try:
        return subprocess.run(["git", "-C", clone, "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception as e:  # recorded, not hidden
        return f"unreadable ({e.__class__.__name__})"


def config_hash(cfg):
    blob = json.dumps(cfg, sort_keys=True, default=str)
    return "sha256/16 " + hashlib.sha256(blob.encode()).hexdigest()[:16], blob


def write_provenance(outdir, stage, script, cfg, extra=None, clone=None):
    os.makedirs(outdir, exist_ok=True)
    ch, blob = config_hash(cfg)
    lines = [
        f"Round 4 conformal track, stage {stage}",
        f"job_name_prefix : r4conf_{stage}  (the submission route replaces --job-name)",
        f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID', 'none')}",
        f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION', 'none')}",
        f"node            : {socket.gethostname()}",
        f"date            : {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"code_clone      : {clone or os.path.dirname(os.path.dirname(_HERE))}",
        f"code_clone_head : {code_head(clone)}",
        f"data_root       : {DATA_ROOT}",
        f"script          : {os.path.abspath(script)}",
        f"script_md5      : {md5(script)}",
        f"harness_md5     : {md5(os.path.join(ROUND3_SCRIPTS_DIR, 'round3_a0_harness.py'))}",
        f"command_line    : {' '.join(sys.argv)}",
        f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED', 'unset')}",
        f"python          : {sys.version.split()[0]}",
        f"numpy           : {np.__version__}",
        f"config_hash     : {ch}",
        f"config          : {blob}",
    ]
    for k, v in (extra or {}).items():
        lines.append(f"{k:<16}: {v}")
    with open(os.path.join(outdir, "PROVENANCE.txt"), "a") as f:
        f.write("=" * 78 + "\n" + "\n".join(lines) + "\n")


def stamp(outdir, track, note, plan="round4 conformal track (docs/round4_conf_plan.md)"):
    """The longleaf-provenance stamp, written by the producing process. Never overwrites a
    stamp that belongs to another frame; raises instead."""
    frame = os.environ.get("R4CONF_FRAME_ID", "")
    assert frame, "R4CONF_FRAME_ID must be set by the process that owns this directory"
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, "_provenance.json")
    if os.path.exists(p):
        old = json.load(open(p))
        if old.get("frame_id") != frame:
            raise RuntimeError(f"{p} belongs to frame {old.get('frame_id')}; not overwriting")
    json.dump(dict(writer="claude-science", project_id=PROJECT_ID, frame_id=frame, track=track,
                   plan=plan, note=note, host=socket.gethostname(),
                   created_at=datetime.now(timezone.utc).isoformat(timespec="seconds")),
              open(p, "w"), indent=2)
