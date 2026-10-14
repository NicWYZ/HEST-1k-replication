#!/usr/bin/env python
"""Run one script of round 7's inference track from a read-only snapshot of a delivered commit.

docs/round07/tracks/ppi/round07_ppi_plan.md section 1.1 item 4 and section 4; track document section 4.
Adapted from round5_ppi_run.py. Every Longleaf job of the track runs its script through this runner:

    python <snap>/code/scripts/round7_ppi_run.py --snapshot-dir <snap> --out-dir <dir> \
        --stage <S0|S1|...> --unit <name> --frame-id <owner frame id> -- <script.py> [script args ...]

The script runs in this process with runpy from the snapshot's code/scripts, in its own output directory, so
the md5 of every module loaded from the snapshot can be recorded after it finishes. The runner writes
PROVENANCE.txt (Slurm job id, partition actually used, account, node, date, snapshot commit, command line,
the config and its sha256, PYTHONHASHSEED, the intended job prefix r7ppi_, stage, unit, owning frame id,
library versions, md5 of every executed script and of every --inputs file) and a one-row _run_row.csv.
It does not write _provenance.json: the job script writes that stamp on the node from the
longleaf-provenance payload before the runner starts, and the runner refuses to run without it.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import platform
import runpy
import sys
import time

PREFIX = "r7ppi_"


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--unit", required=True)
    ap.add_argument("--frame-id", required=True)
    ap.add_argument("--inputs", default="", help="comma list of input files to md5")
    ap.add_argument("rest", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    rest = a.rest[1:] if a.rest and a.rest[0] == "--" else a.rest
    assert rest, "no script given"
    snap = os.path.realpath(a.snapshot_dir)
    full = os.path.basename(snap)
    assert len(full) == 40, "snapshot directory must be named by the full commit hash"
    scripts = os.path.join(snap, "code", "scripts")
    script = os.path.join(scripts, os.path.basename(rest[0]))
    assert os.path.isfile(script), script
    os.makedirs(a.out_dir, exist_ok=True)
    os.chdir(a.out_dir)
    stamp = json.load(open("_provenance.json"))
    assert stamp.get("frame_id") == a.frame_id, "stamp frame id %r differs from --frame-id" % stamp.get("frame_id")
    sys.path.insert(0, scripts)
    os.environ["PYTHONPATH"] = scripts + os.pathsep + os.environ.get("PYTHONPATH", "")
    import numpy, pandas, scipy  # noqa: E401  (versions are recorded)
    try:
        import pyarrow
        pav = pyarrow.__version__
    except ImportError:
        pav = "absent"
    cmdline = " ".join([os.path.basename(script)] + rest[1:])
    config = dict(stage=a.stage, unit=a.unit, snapshot_commit=full, command=cmdline,
                  inputs=[p for p in a.inputs.split(",") if p])
    config_json = json.dumps(config, sort_keys=True, separators=(",", ":"))
    config_hash = hashlib.sha256(config_json.encode()).hexdigest()
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
        here = os.path.realpath(__file__)
        mods = {os.path.realpath(m.__file__) for m in list(sys.modules.values())
                if getattr(m, "__file__", None) and os.path.realpath(m.__file__).startswith(os.path.realpath(scripts))}
        if here.startswith(os.path.realpath(scripts)):
            mods.add(here)
        mods.add(os.path.realpath(script))
        ins = config["inputs"]
        with open("PROVENANCE.txt", "w") as f:
            f.write("platform: %s\n" % ("Longleaf" if os.environ.get("SLURM_JOB_ID") else "local"))
            for k in ("SLURM_JOB_ID", "SLURM_JOB_PARTITION", "SLURM_JOB_ACCOUNT", "SLURM_CPUS_ON_NODE", "SLURM_MEM_PER_NODE"):
                f.write("%s: %s\n" % (k.lower(), os.environ.get(k, "")))
            f.write("node: %s\n" % platform.node())
            f.write("job_prefix_intended: %s%s\n" % (PREFIX, a.stage))
            f.write("stage: %s\nunit: %s\nframe_id: %s\n" % (a.stage, a.unit, a.frame_id))
            f.write("PYTHONHASHSEED: %s\n" % os.environ.get("PYTHONHASHSEED", ""))
            f.write("host: %s\n" % platform.platform())
            f.write("python: %s at %s\n" % (sys.version.split()[0], os.path.realpath(sys.executable)))
            f.write("versions: numpy %s pandas %s scipy %s pyarrow %s\n"
                    % (numpy.__version__, pandas.__version__, scipy.__version__, pav))
            f.write("snapshot_commit: %s\nsnapshot: %s\n" % (full, snap))
            f.write("command: %s\n" % cmdline)
            f.write("config: %s\nconfig_sha256: %s\n" % (config_json, config_hash))
            f.write("start: %s\nend: %s\nelapsed_s: %.1f\nstatus: %s\n" % (start, end, el, status))
            f.write("scripts_executed (md5, path relative to snapshot):\n")
            for m in sorted(mods):
                f.write("  %s  %s\n" % (md5(m), os.path.relpath(m, os.path.realpath(snap))))
            f.write("inputs (md5, path):\n")
            for p in ins:
                f.write("  %s  %s\n" % (md5(p), p))
        with open("_run_row.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["slurm_job_id", "partition", "node", "stage", "unit", "frame_id", "start", "end", "elapsed_s",
                        "status", "commit", "config_sha256", "out_dir", "command"])
            w.writerow([os.environ.get("SLURM_JOB_ID", ""), os.environ.get("SLURM_JOB_PARTITION", ""), platform.node(),
                        a.stage, a.unit, a.frame_id, start, end, "%.1f" % el, status, full, config_hash, os.getcwd(),
                        cmdline])


if __name__ == "__main__":
    main()
