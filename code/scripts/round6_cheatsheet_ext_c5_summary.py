"""Round 6 extension, cheatsheet track, C5: the pilot's tables.

Runs in the container on a stage's outputs under /results/<STAGE> and its
transcripts under /private/logs/<STAGE>. Writes, in /results/<STAGE>/

  predictions.parquet     every valid prediction file of the stage, one row
                          per trial and scored spot (trial_id, pid, slide,
                          barcode, 50 genes), explicit schema
  sessions.csv            per session: role, size, status, tokens, cost,
                          turns, wall time, peak context, images returned
  scores.csv              per predicting session: rbar, pooled, per slide
  transcripts_md5.csv     md5 and bytes of each transcript
  PROVENANCE.txt

Peak context is the largest input side of any single model call in the
session, input tokens plus cache reads plus cache writes, from the stream's
per-message usage. Images returned are counted from tool results. How many
patches each image held is not in the stream, so it is read from the commands
that made the images and kept in a hand-made file beside this one's outputs.
"""
import csv
import datetime
import glob
import hashlib
import json
import os
import subprocess
import sys

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round6_cheatsheet_ext_build as B  # noqa: E402
import round6_cheatsheet_ext_score as S  # noqa: E402


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def stream_stats(path):
    peak, images, tools = 0, 0, {}
    for line in open(path, errors="replace"):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = e.get("message") or {}
        if e.get("type") == "assistant":
            u = msg.get("usage") or {}
            peak = max(peak, (u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)
                       + (u.get("cache_creation_input_tokens") or 0))
            for c in msg.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    tools[c["name"]] = tools.get(c["name"], 0) + 1
        elif e.get("type") == "user" and isinstance(msg.get("content"), list):
            for c in msg["content"]:
                if isinstance(c, dict) and c.get("type") == "tool_result" and isinstance(c.get("content"), list):
                    images += sum(1 for x in c["content"] if isinstance(x, dict) and x.get("type") == "image")
    return peak, images, tools


def main():
    stage = sys.argv[1]
    out = os.path.join("/results", stage)
    logs = os.path.join("/private/logs", stage)
    man = pd.read_csv(os.path.join(out, "manifest.csv"))
    rows, md5s = [], []
    for _, r in man.iterrows():
        p = os.path.join(logs, r["stream"])
        peak, images, tools = stream_stats(p)
        rows.append({**{k: r[k] for k in ("trial_id", "role", "size", "version", "attempt", "status", "result_subtype",
                                          "input_tokens", "output_tokens", "cache_read", "cache_write", "cost_usd",
                                          "num_turns", "wall_s", "bytes_written", "bytes_kept", "mechanical_flags",
                                          "violations", "served_model", "claude_code_version")},
                     "peak_context_tokens": peak, "images_returned": images, "tool_calls": json.dumps(tools, sort_keys=True)})
        md5s.append({"trial_id": r["trial_id"], "role": r["role"], "file": r["stream"], "md5": md5(p), "bytes": os.path.getsize(p)})
    pd.DataFrame(rows).to_csv(os.path.join(out, "sessions.csv"), index=False)
    pd.DataFrame(md5s).to_csv(os.path.join(out, "transcripts_md5.csv"), index=False)

    genes = B.package()[0]
    parts, scores = [], []
    for f in sorted(glob.glob(os.path.join(out, "predictions_raw", "*.csv"))):
        tid = os.path.basename(f)[:-4]
        truth, slide, _ = B.truth_for(tid)
        pred = S.validate(pd.read_csv(f), list(truth.index), genes)
        m = json.load(open(os.path.join(B.MAPS, f"{tid}.json")))["target"]["spots"]
        d = pred.reset_index(drop=True)
        d.insert(0, "barcode", [m[p][1] for p in pred.index])
        d.insert(0, "slide", [m[p][0] for p in pred.index])
        d.insert(0, "pid", list(pred.index))
        d.insert(0, "trial_id", tid)
        parts.append(d)
        s = json.load(open(os.path.join(out, "scores", f"{tid}.json")))
        again = S.score(pred, truth, slide)
        assert abs(again["rbar"] - s["rbar"]) < 1e-12, tid
        scores.append({"trial_id": tid, "role": s["role"], "size": s["size"], "writer": s["writer"], "rbar": s["rbar"],
                       "pooled": s["pooled"], **{f"rbar_{k}": v for k, v in sorted(s["per_slide"].items())},
                       "n_constant_pred_cells": s["n_constant_pred_cells"]})
    allp = pd.concat(parts, ignore_index=True)
    schema = pa.schema([pa.field(c, pa.string()) for c in ("trial_id", "pid", "slide", "barcode")]
                       + [pa.field(g, pa.float64()) for g in genes])
    pq.write_table(pa.Table.from_pandas(allp, schema=schema, preserve_index=False), os.path.join(out, "predictions.parquet"))
    pd.DataFrame(scores).to_csv(os.path.join(out, "scores.csv"), index=False)

    v = lambda c: subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()  # noqa: E731
    scripts = sorted(glob.glob(os.path.join(HERE, "round6_cheatsheet_ext_*.py"))) + [os.path.join(HERE, "round6_cheatsheet_score.py"),
                                                                                   os.path.join(HERE, "round6_cheatsheet_scan.py")]
    with open(os.path.join(out, "PROVENANCE.txt"), "w") as fh:
        fh.write(f"""stage: {stage}
machine: Nicolas's Mac (arm64, macOS 26.6.2), in the container r6ext (image r6ext:1)
date_utc: {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}
code_commit: {os.environ.get('CODE_COMMIT', 'see the md5s below')}
commands: /opt/harness/bin/python -B /repo/code/scripts/round6_cheatsheet_ext_run.py {stage} baseline
          /opt/harness/bin/python -B /repo/code/scripts/round6_cheatsheet_ext_run.py {stage} cell --size 4096
          /opt/harness/bin/python -B /repo/code/scripts/round6_cheatsheet_ext_c5_summary.py {stage}
PYTHONHASHSEED: {os.environ.get('PYTHONHASHSEED', 'not set')}
claude_code_version: {v('claude --version')}
served_model: {', '.join(sorted(set(man['served_model'].astype(str))))}
effort: medium
data_package_manifest_md5: {md5('/private/package/MANIFEST.tsv')}
trial_python: {v('python3 --version')}, numpy 2.5.3, pandas 3.0.5, scipy 1.18.1, Pillow 12.3.0, scikit-image 0.26.0, scikit-learn 1.9.1
script_md5:
""" + "".join(f"  {md5(s)}  {os.path.basename(s)}\n" for s in scripts))
    print(pd.DataFrame(rows).drop(columns=["tool_calls", "served_model", "claude_code_version"]).to_string(index=False))
    print(pd.DataFrame(scores).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
