"""Round 7 federated learning track, shared helpers: paths, md5, provenance and ownership stamps.

stamp_dir, read_stamp and whose follow the longleaf-provenance skill, with the frame and project
ids passed explicitly, because a Slurm job has no session environment. They are transcribed from
code/scripts/round5_ppi_common.py with the track and plan names changed.

Jobs run from a read-only snapshot of a delivered commit, written by the delivery job to
/work/users/w/e/weiyang/hest_code/round7-fedlearn_snapshots/<full commit hash>/code/. The commit a
job ran from is therefore the name of the snapshot directory, which snapshot_commit() reads from
the path of the running script. Nothing here computes a statistic.
"""
import datetime
import hashlib
import json
import os
import platform
import socket
import subprocess
import sys

ROOT = "/work/users/w/e/weiyang/hest_replication"
CLONE = "/work/users/w/e/weiyang/hest_code/round7-fedlearn"
SNAPSHOTS = "/work/users/w/e/weiyang/hest_code/round7-fedlearn_snapshots"
PY = f"{ROOT}/env/miniforge3/envs/hest/bin/python"
PROJECT_ID = "proj_3a4e23273fb6"
TRACK = "round7-fedlearn"
PLAN = "round07_fedlearn_plan"
JOB_PREFIX = "r7fl_"
PROVENANCE_FILENAME = "_provenance.json"


def md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def snapshot_root(script_path):
    """<snapshot>/code/scripts/x.py -> <snapshot>."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(script_path))))


def snapshot_commit(script_path):
    """The full commit hash that names the snapshot the script runs from, or '' if the script
    does not run from a snapshot directory."""
    root = snapshot_root(script_path)
    name = os.path.basename(root)
    if os.path.dirname(root) == SNAPSHOTS and len(name) == 40 and all(c in "0123456789abcdef" for c in name):
        return name
    return ""


def repo_relative(script_path):
    """code/scripts/x.py, the path of the script inside the repository."""
    return os.path.relpath(os.path.abspath(script_path), snapshot_root(script_path))


def stamp_dir(path, frame_id, note="", project_id=PROJECT_ID):
    os.makedirs(path, exist_ok=True)
    target = os.path.join(path, PROVENANCE_FILENAME)
    payload = {
        "writer": "claude-science", "project_id": project_id, "frame_id": frame_id, "track": TRACK,
        "plan": PLAN, "note": note, "host": socket.gethostname(),
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    if os.path.exists(target):
        try:
            existing = json.load(open(target))
        except Exception:
            existing = {}
        owner = existing.get("frame_id", "")
        if owner and owner != frame_id:
            raise RuntimeError(f"refusing to overwrite a stamp owned by frame {owner[:8]} in {path}")
    with open(target, "w") as fh:
        json.dump(payload, fh, indent=2)
    return target


def read_stamp(path):
    d = path if os.path.isdir(path) else os.path.dirname(path)
    t = os.path.join(d, PROVENANCE_FILENAME)
    if not os.path.exists(t):
        return None
    try:
        return json.load(open(t))
    except Exception:
        return None


def whose(path, frame_id, project_id=PROJECT_ID, plan=PLAN):
    s = read_stamp(path)
    if s is None:
        return {"verdict": "unstamped", "stamp": None}
    if s.get("frame_id") and s["frame_id"] == frame_id:
        v = "mine"
    elif project_id and s.get("project_id") and s["project_id"] != project_id:
        v = "other_project"
    elif plan is not None and s.get("plan") == plan:
        v = "sibling"
    elif project_id and s.get("project_id") == project_id:
        v = "sibling"
    else:
        v = "foreign_session"
    return {"verdict": v, "stamp": s}


def write_provenance(outdir, stage, frame_id, command, config, scripts, extra=None):
    """Append one record to outdir/PROVENANCE.txt with the job id, partition actually used, node,
    date, the snapshot commit, the command line, the config with its md5, PYTHONHASHSEED and the
    md5 of every script that ran (path inside the repository)."""
    try:
        head = subprocess.run(["git", "--no-optional-locks", "-C", CLONE, "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
    except Exception as e:  # pragma: no cover
        head = f"unreadable ({e})"
    cfg = json.dumps(config, sort_keys=True)
    commits = sorted({snapshot_commit(s) for s in scripts})
    lines = [
        f"stage: {stage}", f"intended_job_prefix: {JOB_PREFIX}", f"frame_id: {frame_id}",
        f"slurm_job_id: {os.environ.get('SLURM_JOB_ID', '')}",
        f"partition: {os.environ.get('SLURM_JOB_PARTITION', '')}",
        f"account: {os.environ.get('SLURM_JOB_ACCOUNT', '')}",
        f"node: {socket.gethostname()}",
        f"cpu: {platform.processor() or platform.machine()}",
        f"date_utc: {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}",
        f"snapshot_commit: {' '.join(commits)}",
        f"code_clone: {CLONE}", f"code_clone_HEAD: {head}",
        f"PYTHONHASHSEED: {os.environ.get('PYTHONHASHSEED', '')}",
        f"python: {sys.version.split()[0]} at {sys.executable}",
        f"command: {command}",
        f"config: {cfg}", f"config_md5: {hashlib.md5(cfg.encode()).hexdigest()}",
        "script_md5:",
    ] + [f"  {md5(s)}  {repo_relative(s)}" for s in scripts]
    try:
        import numpy, pandas, scipy
        lines.append(f"versions: numpy {numpy.__version__} pandas {pandas.__version__} scipy {scipy.__version__}")
    except Exception:
        pass
    for k, v in (extra or {}).items():
        lines.append(f"{k}: {v}")
    with open(os.path.join(outdir, "PROVENANCE.txt"), "a") as fh:
        fh.write("\n".join(lines) + "\n\n")
