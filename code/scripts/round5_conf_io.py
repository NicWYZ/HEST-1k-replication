#!/usr/bin/env python
"""Round 5, prediction-set track: provenance and stamps for every job of the track.

docs/round5_conf_plan.md section 2 (section 4 of the instruction, standing rules). Nothing here
computes a result. It writes two files into an output directory, from the job that produced it.

1. PROVENANCE.txt, appended, with the Slurm job id, the partition the job actually ran on, the
   node and its CPU vendor, the date, the code clone and its HEAD (read from the clone's .git files,
   so no git command runs in a job), the data root, the command line, PYTHONHASHSEED, the Python,
   numpy and pandas versions, a config hash with the config it hashes, the intended job-name prefix
   r5conf_<stage>, and the md5 of every script that ran. "Every script that ran" is the main script
   plus every module loaded from the clone's code/scripts directory at the time of writing, which
   includes the round-4 modules the track imports unmodified and the round-3 harness.
2. _provenance.json, the longleaf-provenance stamp, with the frame id the brief assigned, taken
   from the environment variable R5CONF_FRAME_ID. A stamp that belongs to another frame is never
   overwritten; the call raises instead.
"""
import hashlib
import json
import os
import platform
import socket
import sys
from datetime import datetime, timezone

DATA_ROOT = "/work/users/w/e/weiyang/hest_replication"
PROJECT_ID = "proj_3a4e23273fb6"
PLAN = "round5 conformal track (docs/round5_conf_plan.md)"
HARNESS_MD5 = "0ad7ae8efe554c1f285e5f384a9fb7f5"
_HERE = os.path.dirname(os.path.abspath(__file__))
CLONE = os.environ.get("R5CONF_CODE_CLONE", os.path.dirname(os.path.dirname(_HERE)))


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def clone_head(clone=CLONE):
    """HEAD of the code clone, read from its .git files. No git command is run."""
    try:
        h = open(os.path.join(clone, ".git", "HEAD")).read().strip()
        if not h.startswith("ref:"):
            return h
        ref = h.split(None, 1)[1]
        p = os.path.join(clone, ".git", ref)
        if os.path.exists(p):
            return open(p).read().strip()
        for line in open(os.path.join(clone, ".git", "packed-refs")):
            if line.strip().endswith(ref):
                return line.split()[0]
        return f"unresolved ref {ref}"
    except Exception as e:  # recorded, not hidden
        return f"unreadable ({e.__class__.__name__})"


def cpu_vendor():
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("vendor_id"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


def config_hash(cfg):
    blob = json.dumps(cfg, sort_keys=True, default=str)
    return "sha256/16 " + hashlib.sha256(blob.encode()).hexdigest()[:16], blob


def executed_scripts(main_script):
    """The main script and every loaded module whose file lies in the clone's code/scripts."""
    paths = {os.path.abspath(main_script)}
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if f and os.path.abspath(f).startswith(os.path.abspath(_HERE) + os.sep) and f.endswith(".py"):
            paths.add(os.path.abspath(f))
    harness = os.path.join(_HERE, "round3_a0_harness.py")
    if os.path.exists(harness):
        paths.add(harness)
    return sorted(paths)


def write_provenance(outdir, stage, main_script, cfg, extra=None):
    import numpy as np
    import pandas as pd
    os.makedirs(outdir, exist_ok=True)
    ch, blob = config_hash(cfg)
    lines = [
        f"Round 5 conformal track, stage {stage}",
        f"job_name_prefix : r5conf_{stage}  (the submission route replaces --job-name)",
        f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID', 'none')}",
        f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION', 'none')}",
        f"slurm_account   : {os.environ.get('SLURM_JOB_ACCOUNT', 'none')}",
        f"node            : {socket.gethostname()}",
        f"cpu_vendor      : {cpu_vendor()}",
        f"date            : {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"code_clone      : {CLONE}",
        f"code_clone_head : {clone_head()}",
        f"data_root       : {DATA_ROOT}",
        f"command_line    : {' '.join(sys.argv)}",
        f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED', 'unset')}",
        f"python          : {sys.version.split()[0]}",
        f"numpy           : {np.__version__}",
        f"pandas          : {pd.__version__}",
        f"config_hash     : {ch}",
        f"config          : {blob}",
    ]
    for p in executed_scripts(main_script):
        lines.append(f"script_md5      : {md5(p)}  {p}")
    for k, v in (extra or {}).items():
        lines.append(f"{k:<16}: {v}")
    with open(os.path.join(outdir, "PROVENANCE.txt"), "a") as f:
        f.write("=" * 78 + "\n" + "\n".join(lines) + "\n")


def stamp(outdir, track, note):
    """The longleaf-provenance stamp, written by the producing process."""
    frame = os.environ.get("R5CONF_FRAME_ID", "")
    assert frame, "R5CONF_FRAME_ID must be set by the process that owns this directory"
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, "_provenance.json")
    if os.path.exists(p):
        old = json.load(open(p))
        if old.get("frame_id") != frame:
            raise RuntimeError(f"{p} belongs to frame {old.get('frame_id')}; not overwriting")
    json.dump(dict(writer="claude-science", project_id=PROJECT_ID, frame_id=frame, track=track,
                   plan=PLAN, note=note, host=socket.gethostname(),
                   created_at=datetime.now(timezone.utc).isoformat(timespec="seconds")),
              open(p, "w"), indent=2)
