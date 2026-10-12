"""Round 6 extension, cheatsheet track: the trial harness (instruction 6.4, 6.5).

Runs in the container. It builds trial directories, starts each session as a
confined headless child (round6_cheatsheet_ext_child.py), runs a writer's
audit loop, validates and scores predictions, and appends one row per session
to the stage's manifest.

A writer's audit loop
  1. after the writer stops, cut cheatsheet.txt to b bytes at the last whole
     character if it is longer, and overwrite it in the writer's directory
  2. run the mechanical checks and keep their report
  3. copy the version into a fresh checker directory and run the checker
  4. if the verdict lists violations and fewer than two revisions were made,
     resume the writer's session with the revision prompt, then go to 1
A cheatsheet still failing after the second revision is used as it stands and
flagged. If a resumed revision ends with a session error or no readable file,
the previous version is put back, the attempt counts as one of the two
revisions, and the last verdict stands for the next step. The predictor gets
the last version.

Readings of the instruction made here, recorded in the plan
  - a verdict passes if and only if its list of violations is empty, and a
    `pass` key that disagrees is recorded
  - the mechanical report is kept beside the verdict and is not shown to the
    checker, whose directory and prompt 6.2 and 6.3 fix
  - a session that stops at its turn cap with a valid output file is used,
    with its stop reason recorded

A session without a valid output file is run once more as a new session with
a new ID. If the second also fails it is recorded as failed.

    python round6_cheatsheet_ext_run.py STAGE baseline
    python round6_cheatsheet_ext_run.py STAGE writer --size 4096
    python round6_cheatsheet_ext_run.py STAGE predictor --size 4096 --writer TRIAL_ID
    python round6_cheatsheet_ext_run.py STAGE combined
    python round6_cheatsheet_ext_run.py STAGE grid --sizes 256 512 ... [--parallel 4]
"""
import argparse
import csv
import datetime
import json
import os
import shutil
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round6_cheatsheet_ext_build as B  # noqa: E402
import round6_cheatsheet_ext_check_cheatsheet as K  # noqa: E402
import round6_cheatsheet_ext_child as C  # noqa: E402
import round6_cheatsheet_ext_prompts as PR  # noqa: E402
import round6_cheatsheet_ext_scan as SC  # noqa: E402
import round6_cheatsheet_ext_score as S  # noqa: E402

RESULTS = "/results"
MAX_REVISIONS = 2
LOCK = threading.Lock()
FIELDS = ["stage", "trial_id", "role", "size", "depends_on", "version", "audit", "attempt", "session_id", "resumed",
          "status", "detail", "bytes_written", "bytes_kept", "mechanical_flags", "violations", "rc",
          "result_subtype", "is_error", "input_tokens", "output_tokens", "cache_read", "cache_write", "cost_usd",
          "num_turns", "wall_s", "claude_code_version", "served_model", "stream", "started_utc"]


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def stage_dir(stage, *parts):
    d = os.path.join(RESULTS, stage, *parts)
    os.makedirs(d, exist_ok=True)
    return d


def record(stage, row):
    path = os.path.join(stage_dir(stage), "manifest.csv")
    with LOCK:
        new = not os.path.exists(path)
        with open(path, "a", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
            if new:
                w.writeheader()
            w.writerow(row)


def session(stage, trial_dir, name, prompt, role, resume=None):
    """Run one child and return its run record merged with its stream summary."""
    started = now()
    r = C.run(trial_dir, prompt, os.path.join(B.PRIVATE, "logs", stage), name, role=role, resume=resume)
    r.update(C.summarise(r["stream"]))
    r["started_utc"] = started
    r["stream"] = os.path.basename(r["stream"])
    r["errored"] = bool(r["rc"] != 0 or (r.get("is_error") and r.get("result_subtype") != "error_max_turns")
                        or r.get("result_subtype") is None)
    return r


def blind_check(stage, tid, root):
    hits = SC.scan_tree(root)
    if hits:
        SC.write(hits, os.path.join(stage_dir(stage, "blinding"), f"{tid}_hits.csv"))
        raise RuntimeError(f"{tid}: {len(hits)} blinding hits in the trial directory, not started")
    with LOCK, open(os.path.join(stage_dir(stage, "blinding"), "clean.csv"), "a") as fh:
        n = sum(len(f) for _, _, f in os.walk(root))
        fh.write(f"{tid},{n} files,0 hits\n")


# ---------------------------------------------------------------- predictors

def run_predicting(stage, role, size=0, writer=None, cheatsheet=None):
    """baseline, predictor or combined. Returns the trial ID that produced valid predictions, or None."""
    for attempt in (1, 2):
        tid, root = B.build(role, size=size, cheatsheet=cheatsheet)
        blind_check(stage, tid, root)
        r = session(stage, root, f"{tid}_{role}", PR.render(role), "other")
        row = dict(r, stage=stage, trial_id=tid, role=role, size=size, depends_on=writer or "", attempt=attempt)
        try:
            truth, slide, genes = B.truth_for(tid)
            pred = S.validate(pd.read_csv(os.path.join(root, "predictions.csv")), list(truth.index), genes)
        except Exception as e:  # missing, unreadable or invalid file
            row.update(status="failed", detail=f"{type(e).__name__}: {e}"[:300])
            record(stage, row)
            continue
        sc = S.score(pred, truth, slide)
        shutil.copyfile(os.path.join(root, "predictions.csv"),
                        os.path.join(stage_dir(stage, "predictions_raw"), f"{tid}.csv"))
        sc["cells"].assign(trial_id=tid).to_csv(os.path.join(stage_dir(stage, "scores"), f"{tid}_cells.csv"), index=False)
        json.dump({"trial_id": tid, "role": role, "size": size, "writer": writer, "rbar": sc["rbar"],
                   "pooled": sc["pooled"], "per_slide": sc["per_slide"],
                   "n_constant_pred_cells": sc["n_constant_pred_cells"],
                   "n_constant_truth_cells": sc["n_constant_truth_cells"]},
                  open(os.path.join(stage_dir(stage, "scores"), f"{tid}.json"), "w"), indent=1)
        row.update(status="ok", detail=f"rbar={sc['rbar']:.4f}")
        record(stage, row)
        return tid
    return None


# ------------------------------------------------------------------- writers

def cut(path, b):
    """Cut the file to b bytes at the last whole character. Returns (written, kept)."""
    data = open(path, "rb").read()
    written = len(data)
    if written > b:
        data = data[:b].decode("utf-8", errors="ignore").encode("utf-8")
        open(path, "wb").write(data)
    return written, len(data)


def parse_verdict(path):
    v = json.load(open(path))
    assert isinstance(v, dict) and isinstance(v.get("violations"), list) and "pass" in v
    for x in v["violations"]:
        assert isinstance(x, dict) and {"lines", "rule", "reason"} <= set(x), x
    return v


def audit(stage, writer_tid, size, version_path, version):
    """Run a fresh checker on one version. Returns (audit ID, verdict) or (None, None)."""
    for attempt in (1, 2):
        aid, root = B.build("checker", cheatsheet=version_path)
        blind_check(stage, aid, root)
        r = session(stage, root, f"{aid}_checker", PR.render("checker"), "checker")
        row = dict(r, stage=stage, trial_id=aid, role="checker", size=size, depends_on=writer_tid,
                   version=version, audit=version, attempt=attempt)
        try:
            v = parse_verdict(os.path.join(root, "verdict.json"))
        except Exception as e:
            row.update(status="failed", detail=f"{type(e).__name__}: {e}"[:300])
            record(stage, row)
            continue
        json.dump(dict(v, audit_id=aid, writer=writer_tid, version=version, size=size),
                  open(os.path.join(stage_dir(stage, "verdicts"), f"{aid}.json"), "w"), indent=1)
        agree = bool(v["pass"]) == (len(v["violations"]) == 0)
        row.update(status="ok", violations=len(v["violations"]),
                   detail="" if agree else "the pass key disagrees with the list of violations")
        record(stage, row)
        return aid, v
    return None, None


def violations_text(v):
    out = []
    for x in v["violations"]:
        lines = x["lines"]
        if isinstance(lines, (list, tuple)):
            lines = ", ".join(str(i) for i in lines)
        out.append(f"lines {lines}, rule {x['rule']}: {' '.join(str(x['reason']).split())}")
    return "\n".join(out)


def run_writer(stage, size):
    """The writer and its audit loop. Returns (writer trial ID, path of the final version, summary) or None."""
    genes = B.package()[0]
    for attempt in (1, 2):
        tid, root = B.build("writer", size=size)
        blind_check(stage, tid, root)
        sheet = os.path.join(root, "cheatsheet.txt")
        r = session(stage, root, f"{tid}_writer_v1", PR.render("writer", b=size), "writer")
        row = dict(r, stage=stage, trial_id=tid, role="writer", size=size, version=1, attempt=attempt)
        try:
            open(sheet, "rb").read().decode("utf-8")
        except Exception as e:
            row.update(status="failed", detail=f"{type(e).__name__}: {e}"[:300])
            record(stage, row)
            continue
        sid, version, revisions, verdict, final, summary = r["session_id"], 1, 0, None, None, []
        while True:
            written, kept = cut(sheet, size)
            _, flags = K.check(open(sheet, "rb").read(), size, genes)
            final = os.path.join(stage_dir(stage, "cheatsheets"), f"{tid}_v{version}.txt")
            shutil.copyfile(sheet, final)
            json.dump({"trial_id": tid, "version": version, "bytes_written": written, "bytes_kept": kept,
                       "flags": flags}, open(os.path.join(stage_dir(stage, "mechanical"), f"{tid}_v{version}.json"), "w"), indent=1)
            row.update(status="ok", bytes_written=written, bytes_kept=kept, mechanical_flags=len(flags))
            record(stage, row)
            aid, verdict = audit(stage, tid, size, final, version)
            summary.append({"version": version, "audit_id": aid, "bytes_written": written, "bytes_kept": kept,
                            "mechanical_flags": len(flags),
                            "violations": None if verdict is None else len(verdict["violations"])})
            if verdict is None or not verdict["violations"] or revisions >= MAX_REVISIONS:
                break
            # a revision, by resuming the writer's own session in its own directory
            while revisions < MAX_REVISIONS:
                revisions += 1
                previous = open(sheet, "rb").read()
                r = session(stage, root, f"{tid}_writer_v{version + 1}",
                            PR.render("revision", b=size, violations=violations_text(verdict)), "writer", resume=sid)
                row = dict(r, stage=stage, trial_id=tid, role="writer_revision", size=size, version=version + 1,
                           attempt=attempt)
                try:
                    assert not r["errored"], f"session error rc={r['rc']} subtype={r.get('result_subtype')}"
                    open(sheet, "rb").read().decode("utf-8")
                except Exception as e:
                    open(sheet, "wb").write(previous)
                    row.update(status="revision_failed", detail=f"previous version kept. {type(e).__name__}: {e}"[:300])
                    record(stage, row)
                    summary.append({"version": version, "revision_failed": revisions})
                    continue
                version += 1
                break
            else:
                break  # both revisions used without a new version
        passed = verdict is not None and not verdict["violations"]
        out = {"writer": tid, "size": size, "final_version": version, "revisions": revisions, "passed": passed,
               "flagged": not passed, "final": os.path.basename(final), "audits": summary}
        json.dump(out, open(os.path.join(stage_dir(stage, "writers"), f"{tid}.json"), "w"), indent=1)
        return tid, final, out
    return None


def run_cell(stage, size):
    w = run_writer(stage, size)
    if w is None:
        return {"size": size, "writer": None, "predictor": None}
    tid, final, out = w
    p = run_predicting(stage, "predictor", size=size, writer=tid, cheatsheet=final)
    return {"size": size, "writer": tid, "predictor": p, "passed": out["passed"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage")
    ap.add_argument("what", choices=["baseline", "writer", "predictor", "combined", "cell", "grid"])
    ap.add_argument("--size", type=int, default=0)
    ap.add_argument("--sizes", type=int, nargs="*", default=[])
    ap.add_argument("--writer", default=None)
    ap.add_argument("--parallel", type=int, default=4)
    a = ap.parse_args()
    if a.what == "baseline":
        out = run_predicting(a.stage, "baseline")
    elif a.what == "combined":
        out = run_predicting(a.stage, "combined")
    elif a.what == "writer":
        w = run_writer(a.stage, a.size)
        out = None if w is None else w[2]
    elif a.what == "predictor":
        w = json.load(open(os.path.join(stage_dir(a.stage, "writers"), f"{a.writer}.json")))
        out = run_predicting(a.stage, "predictor", size=w["size"], writer=a.writer,
                             cheatsheet=os.path.join(stage_dir(a.stage, "cheatsheets"), w["final"]))
    elif a.what == "cell":
        out = run_cell(a.stage, a.size)
    else:
        with ThreadPoolExecutor(a.parallel) as ex:
            out = list(ex.map(lambda b: run_cell(a.stage, b), a.sizes))
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
