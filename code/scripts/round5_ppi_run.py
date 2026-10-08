#!/usr/bin/env python
"""Run one round-5 PPI script from a read-only snapshot of a delivered or committed commit.

Stage: interval 2, plan sections 7.3 and 7.4. Every job of interval 2, on Longleaf or local,
runs its script through this runner, from a snapshot and never from a working tree or a clone,
in its own output directory, and leaves a PROVENANCE.txt with the snapshot's commit and the md5
of every module it executed, and a one-row `_run_row.csv`.

Longleaf (the snapshot was written by the delivery job, plan section 7.3 item 3):
    python <snap>/code/scripts/round5_ppi_run.py --snapshot-dir <snap> --out-dir <dir> \
        --unit <name> --stage <E3a|E3|E4> -- <script.py> [script args ...]
Local (the snapshot is made here with git archive, plan section 7.4):
    python round5_ppi_run.py --repo <clone> --commit <hash> --out-dir <dir> \
        --unit <name> --stage <E3a|E3|E4> -- <script.py> [script args ...]

The local snapshot root defaults to /tmp/r5ppi_snapshots and can be set with R5_SNAPROOT.
The script is executed in this process with runpy, so the md5 of every module that was
loaded from the snapshot can be recorded after it finishes.
"""
import argparse
import csv
import datetime as dt
import hashlib
import os
import platform
import runpy
import subprocess
import sys
import time


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def snapshot(repo, commit):
    full = subprocess.run(["git", "-C", repo, "rev-parse", commit + "^{commit}"],
                          capture_output=True, text=True, check=True).stdout.strip()
    root = os.environ.get("R5_SNAPROOT", "/tmp/r5ppi_snapshots")
    snap = os.path.join(root, full)
    if not os.path.isdir(os.path.join(snap, "code", "scripts")):
        tmp = snap + ".tmp%d" % os.getpid()
        os.makedirs(tmp, exist_ok=True)
        arc = subprocess.run(["git", "-C", repo, "archive", full, "code"],
                             capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", tmp], input=arc, check=True)
        try:
            os.rename(tmp, snap)
        except OSError:
            subprocess.run(["rm", "-rf", tmp])
        subprocess.run(["chmod", "-R", "a-w", snap], check=True)
    return full, snap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="")
    ap.add_argument("--commit", default="")
    ap.add_argument("--snapshot-dir", default="")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--unit", required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--workers", default="")
    ap.add_argument("--inputs", default="", help="comma list of input files to md5")
    ap.add_argument("rest", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    rest = a.rest[1:] if a.rest and a.rest[0] == "--" else a.rest
    assert rest, "no script given"
    if a.snapshot_dir:
        snap = os.path.realpath(a.snapshot_dir)
        full = os.path.basename(snap)
        assert len(full) == 40, "snapshot directory must be named by the full commit hash"
    else:
        assert a.repo and a.commit, "--repo and --commit, or --snapshot-dir"
        full, snap = snapshot(a.repo, a.commit)
    scripts = os.path.join(snap, "code", "scripts")
    script = os.path.join(scripts, os.path.basename(rest[0]))
    assert os.path.isfile(script), script
    os.makedirs(a.out_dir, exist_ok=True)
    os.chdir(a.out_dir)
    sys.path.insert(0, scripts)
    os.environ["PYTHONPATH"] = scripts + os.pathsep + os.environ.get("PYTHONPATH", "")
    import numpy, pandas, scipy  # noqa: E401  (versions are recorded)
    t0 = time.time()
    start = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    sys.argv = [script] + rest[1:]
    status = "COMPLETED"
    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as e:
        if e.code not in (None, 0):
            status = "FAILED exit %s" % e.code
    except Exception as e:  # recorded, then re-raised
        status = "FAILED %s" % type(e).__name__
        raise
    finally:
        el = time.time() - t0
        end = dt.datetime.now().astimezone().isoformat(timespec="seconds")
        mods = sorted({os.path.realpath(m.__file__) for m in list(sys.modules.values())
                       if getattr(m, "__file__", None)
                       and os.path.realpath(m.__file__).startswith(os.path.realpath(scripts))})
        ins = [p for p in a.inputs.split(",") if p]
        with open("PROVENANCE.txt", "w") as f:
            if os.environ.get("SLURM_JOB_ID"):
                f.write("platform: Longleaf, plan section 7.3\n")
                for k in ("SLURM_JOB_ID", "SLURM_JOB_PARTITION", "SLURM_JOB_ACCOUNT", "SLURM_CPUS_ON_NODE"):
                    f.write("%s: %s\n" % (k.lower(), os.environ.get(k, "")))
                f.write("node: %s\n" % platform.node())
            else:
                f.write("platform: local (Nicolas's Mac), plan section 7.4\n")
            f.write("PYTHONHASHSEED: %s\n" % os.environ.get("PYTHONHASHSEED", ""))
            f.write("host: %s\n" % platform.platform())
            f.write("python: %s at %s\n" % (sys.version.split()[0], os.path.realpath(sys.executable)))
            f.write("versions: numpy %s pandas %s scipy %s\n"
                    % (numpy.__version__, pandas.__version__, scipy.__version__))
            f.write("snapshot_commit: %s\nsnapshot: %s\n" % (full, snap))
            f.write("unit: %s\nstage: %s\nworkers: %s\n" % (a.unit, a.stage, a.workers))
            f.write("command: %s\n" % " ".join([os.path.basename(script)] + rest[1:]))
            f.write("start: %s\nend: %s\nelapsed_s: %.1f\nstatus: %s\n" % (start, end, el, status))
            f.write("scripts_executed (md5, path relative to snapshot):\n")
            for m in mods:
                f.write("  %s  %s\n" % (md5(m), os.path.relpath(m, snap)))
            f.write("inputs (md5, path):\n")
            for p in ins:
                f.write("  %s  %s\n" % (md5(p), p))
        with open("_run_row.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["platform", "slurm_job_id", "stage", "unit", "start", "end", "elapsed_s", "status", "commit",
                        "workers", "out_dir", "command"])
            w.writerow(["longleaf" if os.environ.get("SLURM_JOB_ID") else "local",
                        os.environ.get("SLURM_JOB_ID", ""), a.stage, a.unit, start, end, "%.1f" % el, status, full, a.workers,
                        os.path.realpath(a.out_dir) if os.path.isabs(a.out_dir) else os.getcwd(),
                        " ".join([os.path.basename(script)] + rest[1:])])


if __name__ == "__main__":
    main()
