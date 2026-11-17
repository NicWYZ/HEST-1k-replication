"""Helpers for stamping and identifying output ownership on a shared cluster."""
import json
import os
import socket
import datetime

PROVENANCE_FILENAME = "_provenance.json"
WRITER_TAG = "claude-science"


def current_context():
    """Best-effort current project/frame ids from the environment."""
    return {
        "project_id": os.environ.get("CLAUDE_PROJECT_ID") or os.environ.get("PROJECT_ID") or "",
        "frame_id": os.environ.get("CLAUDE_FRAME_ID") or os.environ.get("FRAME_ID") or "",
    }


def provenance_payload(track="", plan="", note="", project_id=None, frame_id=None):
    """Build the stamp dict. Explicit ids win over environment lookup."""
    ctx = current_context()
    return {
        "writer": WRITER_TAG,
        "project_id": project_id if project_id is not None else ctx["project_id"],
        "frame_id": frame_id if frame_id is not None else ctx["frame_id"],
        "track": track,
        "plan": plan,
        "note": note,
        "host": socket.gethostname(),
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }


def stamp_dir(path, track="", plan="", note="", project_id=None, frame_id=None, force=False):
    """Write _provenance.json into `path`. Refuses to clobber another frame's stamp."""
    os.makedirs(path, exist_ok=True)
    target = os.path.join(path, PROVENANCE_FILENAME)
    payload = provenance_payload(track, plan, note, project_id, frame_id)
    if os.path.exists(target) and not force:
        try:
            with open(target) as fh:
                existing = json.load(fh)
        except Exception:
            existing = {}
        owner = existing.get("frame_id", "")
        if owner == payload["frame_id"]:
            # same owner re-stamping: keep previously recorded fields we were not given
            for key in ("track", "plan", "note"):
                if not payload.get(key) and existing.get(key):
                    payload[key] = existing[key]
        if owner and owner != payload["frame_id"]:
            raise RuntimeError(
                "refusing to overwrite a stamp owned by frame %s (track=%r). "
                "You are about to write into another agent's output tree. "
                "Ask the parent before proceeding, or pass force=True if you own it."
                % (owner[:8], existing.get("track", ""))
            )
    with open(target, "w") as fh:
        json.dump(payload, fh, indent=2)
    return target


def read_stamp(path):
    """Return the stamp dict for a directory (or the file's directory), or None."""
    d = path if os.path.isdir(path) else os.path.dirname(path)
    target = os.path.join(d, PROVENANCE_FILENAME)
    if not os.path.exists(target):
        return None
    try:
        with open(target) as fh:
            return json.load(fh)
    except Exception:
        return None


def whose(path, project_id=None, frame_id=None, plan=None):
    """Classify ownership of an output directory.

    verdict in {mine, sibling, foreign_session, other_project, unstamped}
    """
    ctx = current_context()
    me_p = project_id if project_id is not None else ctx["project_id"]
    me_f = frame_id if frame_id is not None else ctx["frame_id"]
    stamp = read_stamp(path)
    if stamp is None:
        return {
            "verdict": "unstamped",
            "stamp": None,
            "action": "ASK THE PARENT before reusing or rebuilding. Unstamped is not "
                      "evidence of foreign ownership.",
        }
    if stamp.get("frame_id") and stamp["frame_id"] == me_f:
        verdict, action = "mine", "reuse freely"
    elif me_p and stamp.get("project_id") and stamp["project_id"] != me_p:
        verdict, action = "other_project", "do not touch"
    elif plan is not None and stamp.get("plan") and stamp["plan"] == plan:
        verdict, action = "sibling", "reuse; do NOT rebuild. Ask the parent what it covers."
    elif me_p and stamp.get("project_id") == me_p:
        verdict, action = "sibling", ("same project, different frame - most likely a sibling "
                                      "track under the same plan. Ask the parent; do NOT rebuild.")
    else:
        verdict, action = "foreign_session", "ask the parent/user before touching"
    return {"verdict": verdict, "stamp": stamp, "action": action}


def provenance_shell_snippet(track="", plan="", note="", outdir="$OUTDIR",
                             project_id=None, frame_id=None):
    """Shell block to paste into an sbatch script so the compute node writes the stamp."""
    p = provenance_payload(track, plan, note, project_id, frame_id)
    body = json.dumps(
        {k: v for k, v in p.items() if k not in ("host", "created_at")}, indent=2
    )[1:-1].rstrip()
    body = "\n".join(line if line.startswith("  ") else "  " + line.lstrip()
                     for line in body.splitlines() if line.strip())
    return (
        'mkdir -p "%s"\n'
        'cat > "%s/%s" <<PROVEOF\n'
        '{\n%s,\n'
        '  "host": "$(hostname)",\n'
        '  "created_at": "$(date -u +%%Y-%%m-%%dT%%H:%%M:%%S+00:00)"\n'
        '}\n'
        'PROVEOF' % (outdir, outdir, PROVENANCE_FILENAME, body)
    )


def scan_tree(root, max_depth=3):
    """List stamped directories under `root` with their owning track/frame."""
    out = []
    root = os.path.abspath(root)
    base_depth = root.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, filenames in os.walk(root):
        if dirpath.count(os.sep) - base_depth >= max_depth:
            dirnames[:] = []
        if PROVENANCE_FILENAME in filenames:
            s = read_stamp(dirpath) or {}
            out.append({
                "path": dirpath,
                "track": s.get("track", ""),
                "frame_id": (s.get("frame_id") or "")[:8],
                "created_at": s.get("created_at", ""),
                "note": s.get("note", ""),
            })
    return out
