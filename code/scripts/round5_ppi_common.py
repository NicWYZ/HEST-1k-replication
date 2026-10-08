"""Round 5 PPI track, shared helpers: paths, md5, provenance and ownership stamps.

stamp_dir, read_stamp, whose and scan_tree are transcribed from the longleaf-provenance skill
(kernel.py) with the frame and project ids passed explicitly, because a Slurm job has no
session environment. Nothing here computes a statistic.
"""
import datetime
import hashlib
import json
import os
import platform
import socket
import sys

ROOT = "/work/users/w/e/weiyang/hest_replication"
CLONE = "/work/users/w/e/weiyang/hest_code/round5-ppi"
PY = f"{ROOT}/env/miniforge3/envs/hest/bin/python"
PROJECT_ID = "proj_3a4e23273fb6"
PROVENANCE_FILENAME = "_provenance.json"

TISSUE_PARQUETS = {
    ("CCRCC", enc): f"results/round3/B1_ppi/b1_predictions__CCRCC__{enc}.parquet" for enc in ("hoptimus0", "uni_v2", "resnet50")
}
TISSUE_PARQUETS.update({("CCRCC_merged", enc): f"results/round3/B1_ppi/b1_predictions__CCRCC_merged__{enc}.parquet" for enc in ("hoptimus0", "uni_v2", "resnet50")})
TISSUE_PARQUETS.update({("INDIANA_KIDNEY", enc): f"results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__{enc}.parquet" for enc in ("hoptimus0", "uni_v2", "resnet50")})
TISSUE_PARQUETS.update({("LUNG_XENIUM", enc): f"results/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__{enc}.parquet" for enc in ("hoptimus0", "uni_v2", "resnet50")})
ACS_PARQUETS = {
    ("ACS_STATES", "package"): "results/round4/ppi/Q2_theory/predictions/ACS_STATES.parquet",
    ("ACS_CA_PUMA", "package"): "results/round4/ppi/Q2_theory/predictions/ACS_CA_PUMA.parquet",
}


def md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def stamp_dir(path, frame_id, track="round5-ppi", plan="round5_ppi_plan", note="", project_id=PROJECT_ID):
    os.makedirs(path, exist_ok=True)
    target = os.path.join(path, PROVENANCE_FILENAME)
    payload = {
        "writer": "claude-science", "project_id": project_id, "frame_id": frame_id, "track": track,
        "plan": plan, "note": note, "host": socket.gethostname(),
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


def whose(path, frame_id, project_id=PROJECT_ID, plan=None):
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


def scan_tree(root, max_depth=3):
    out = []
    root = os.path.abspath(root)
    base = root.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, filenames in os.walk(root):
        if dirpath.count(os.sep) - base >= max_depth:
            dirnames[:] = []
        if PROVENANCE_FILENAME in filenames:
            s = read_stamp(dirpath) or {}
            out.append({"path": os.path.relpath(dirpath, root), "track": s.get("track", ""),
                        "frame_id": s.get("frame_id", ""), "project_id": s.get("project_id", ""),
                        "plan": s.get("plan", ""), "created_at": s.get("created_at", "")})
    return out


def write_provenance(outdir, stage, frame_id, command, config, scripts, extra=None):
    """PROVENANCE.txt with job id, partition, node, date, clone HEAD, command, config hash,
    PYTHONHASHSEED and the md5 of every script that ran."""
    import subprocess
    try:
        head = subprocess.run(["git", "--no-optional-locks", "-C", CLONE, "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
    except Exception as e:  # pragma: no cover
        head = f"unreadable ({e})"
    cfg = json.dumps(config, sort_keys=True)
    lines = [
        f"stage: {stage}", "intended_job_prefix: r5ppi_", f"frame_id: {frame_id}",
        f"slurm_job_id: {os.environ.get('SLURM_JOB_ID', '')}",
        f"partition: {os.environ.get('SLURM_JOB_PARTITION', '')}",
        f"account: {os.environ.get('SLURM_JOB_ACCOUNT', '')}",
        f"node: {socket.gethostname()}",
        f"cpu: {platform.processor() or platform.machine()}",
        f"date_utc: {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}",
        f"code_clone: {CLONE}", f"code_clone_HEAD: {head}",
        f"PYTHONHASHSEED: {os.environ.get('PYTHONHASHSEED', '')}",
        f"python: {sys.version.split()[0]} at {sys.executable}",
        f"command: {command}",
        f"config: {cfg}", f"config_md5: {hashlib.md5(cfg.encode()).hexdigest()}",
        "script_md5:",
    ] + [f"  {md5(s)}  {s}" for s in scripts]
    try:
        import numpy, pandas, scipy
        lines.append(f"versions: numpy {numpy.__version__} pandas {pandas.__version__} scipy {scipy.__version__}")
    except Exception:
        pass
    for k, v in (extra or {}).items():
        lines.append(f"{k}: {v}")
    with open(os.path.join(outdir, "PROVENANCE.txt"), "a") as fh:
        fh.write("\n".join(lines) + "\n\n")
