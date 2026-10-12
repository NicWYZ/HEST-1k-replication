"""Round 6 cheatsheet track: run a stage's trials, keep the manifest, score.

A stage plan (CSV) lists logical slots: slot, arm, size, model, replicate,
role, writer_slot. Each attempt at a slot is a trial with a fresh opaque ID.
A slot whose trial ends without a valid output is run once more under a new
ID; a second failure marks the slot failed. A trial the scanner excludes, or
one interrupted by a reclaimed container, is rerun and does not count as a
failure (instruction 6.4, 6.5, section 5).

    python round6_cheatsheet_run.py PLAN_CSV --stage C1_pilot [--parallel 2]

Committed outputs, under results/round6/cheatsheet/<stage>/
  manifest.csv          one row per trial (attempt), the fields of 6.4
  cheatsheets/<id>.txt  every writer's kept cheatsheet
  predictions.parquet   every valid prediction, mapped back to spots
  scores.csv            rbar per scored trial; per_gene_scores.csv
  scan_hits.csv         every scanner hit; transcripts_md5.csv
  PROVENANCE.txt
Private (never committed), under /srv/r6_private/
  logs/<stage>/<id>.stream.jsonl and .stderr.txt, raw/<id>/ (raw outputs),
  maps/<id>.csv, transcripts/<stage>/<id>.jsonl.gz
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
import platform
import secrets
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round6_cheatsheet_build as B  # noqa: E402
import round6_cheatsheet_child as C  # noqa: E402
import round6_cheatsheet_prompts as PR  # noqa: E402
import round6_cheatsheet_scan as S  # noqa: E402
from round6_cheatsheet_score import InvalidPredictions, score, validate  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PRIVATE = B.PRIVATE
TRIALS = B.TRIALS
MANIFEST_COLS = [
    "trial_id", "slot", "attempt", "stage", "arm", "size", "model", "replicate", "role", "writer_slot",
    "writer_trial_id", "session_id", "status", "fail_reason", "bytes_written", "bytes_kept",
    "input_tokens", "output_tokens", "cache_read", "cache_write", "cost_usd", "turns", "wall_s",
    "claude_code_version", "served_model", "result_subtype", "started_utc", "finished_utc", "rbar",
    "n_constant_pred", "scan_excluding_hits", "scan_system_paths",
]
LOCK = threading.Lock()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def truncate_utf8(data, b):
    """First b bytes, cut at the last whole character."""
    if len(data) <= b:
        return data
    cut = data[:b]
    for k in range(4):
        try:
            cut[:len(cut) - k].decode("utf-8")
            return cut[:len(cut) - k]
        except UnicodeDecodeError:
            continue
    return cut  # not valid UTF-8 for another reason; kept as bytes and recorded


class Stage:
    def __init__(self, plan_csv, stage, parallel, out=None):
        self.plan = pd.read_csv(plan_csv, dtype=str).fillna("")
        self.stage = stage
        self.out = out or os.path.join(REPO, "results/round6/cheatsheet", stage)
        os.makedirs(os.path.join(self.out, "cheatsheets"), exist_ok=True)
        self.logs = os.path.join(PRIVATE, "logs", stage)
        self.tx = os.path.join(PRIVATE, "transcripts", stage)
        os.makedirs(self.tx, exist_ok=True)
        self.parallel = parallel
        self.mpath = os.path.join(self.out, "manifest.csv")
        self.manifest = pd.read_csv(self.mpath, dtype=str).fillna("") if os.path.exists(self.mpath) \
            else pd.DataFrame(columns=MANIFEST_COLS)
        self.P = B.Package()

    # ---------- manifest ----------
    def save(self):
        self.manifest.to_csv(self.mpath, index=False)

    def slot_state(self, slot):
        rows = self.manifest[self.manifest["slot"] == slot]
        if (rows["status"] == "done").any():
            return "done", rows[rows["status"] == "done"].iloc[-1]
        if (rows["status"] == "failed").sum() >= 2 or len(rows) >= 4:
            return "failed", None
        return "pending", None

    def failures(self, slot):
        rows = self.manifest[self.manifest["slot"] == slot]
        return int((rows["status"] == "failed").sum())

    # ---------- one trial ----------
    def new_id(self):
        while True:
            tid = secrets.token_hex(4)
            if not os.path.exists(os.path.join(TRIALS, tid)) and tid not in set(self.manifest["trial_id"]):
                return tid

    def run_slot(self, r):
        with LOCK:
            tid = self.new_id()
            attempt = int((self.manifest["slot"] == r["slot"]).sum()) + 1
        row = {c: "" for c in MANIFEST_COLS}
        row.update({k: r[k] for k in ("slot", "arm", "size", "model", "replicate", "role", "writer_slot")})
        row.update({"trial_id": tid, "attempt": attempt, "stage": self.stage, "started_utc": now()})
        cheatsheet = None
        if r["role"] == "predictor":
            st, wrow = self.slot_state(r["writer_slot"])
            assert st == "done", f"writer {r['writer_slot']} not done"
            row["writer_trial_id"] = wrow["trial_id"]
            cheatsheet = os.path.join(self.out, "cheatsheets", f"{wrow['trial_id']}.txt")
        d, maps = B.build(self.P, {"trial_id": tid, "role": r["role"], "arm": r["arm"]}, cheatsheet=cheatsheet)
        prompt = PR.prompt_for(r["role"], r["size"] if r["role"] == "writer" else None)
        res = C.run(d, r["model"], prompt, self.logs, tid, max_turns=80)
        s = C.summarise(res["stream"])
        row.update({"session_id": res["session_id"], "wall_s": res["wall_s"], "served_model": s["served_model"],
                    "claude_code_version": s["claude_code_version"], "turns": s["num_turns"],
                    "cost_usd": s["cost_usd"], "input_tokens": s["input_tokens"],
                    "output_tokens": s["output_tokens"], "cache_read": s["cache_read"],
                    "cache_write": s["cache_write"], "result_subtype": s["result_subtype"]})
        raw = os.path.join(PRIVATE, "raw", tid)
        os.makedirs(raw, exist_ok=True)
        status, reason, extra = self.collect(r, tid, d, maps, raw)
        row.update(extra)
        # transcript: scan, compress, md5
        hits = S.scan_transcript(res["stream"], tid)
        excl = [h for h in hits if h["excludes"]]
        row["scan_excluding_hits"] = len(excl)
        row["scan_system_paths"] = sum(1 for h in hits if not h["excludes"])
        if excl and status == "done":
            status, reason = "excluded", "scanner: " + "; ".join(sorted({h["kind"] for h in excl}))
        gz = os.path.join(self.tx, f"{tid}.jsonl.gz")
        with open(res["stream"], "rb") as fi, gzip.open(gz, "wb") as fo:
            shutil.copyfileobj(fi, fo)
        row.update({"status": status, "fail_reason": reason, "finished_utc": now()})
        with LOCK:
            self.manifest = pd.concat([self.manifest, pd.DataFrame([row])], ignore_index=True)
            self.save()
            if hits:
                hp = os.path.join(self.out, "scan_hits.csv")
                pd.DataFrame(hits).to_csv(hp, mode="a", header=not os.path.exists(hp), index=False)
            mp = os.path.join(self.out, "transcripts_md5.csv")
            pd.DataFrame([{"trial_id": tid, "file": os.path.basename(gz), "md5_gz": md5(gz),
                           "md5_jsonl": md5(res["stream"]), "bytes_gz": os.path.getsize(gz)}]).to_csv(
                mp, mode="a", header=not os.path.exists(mp), index=False)
        return row

    def collect(self, r, tid, d, maps, raw):
        if r["role"] == "writer":
            p = os.path.join(d, "cheatsheet.txt")
            if not os.path.isfile(p):
                return "failed", "no cheatsheet.txt", {}
            data = open(p, "rb").read()
            shutil.copy(p, os.path.join(raw, "cheatsheet_raw.txt"))
            kept = truncate_utf8(data, int(r["size"]))
            hits = S.scan_file(p)
            if hits:
                return "excluded", "credential or canary in cheatsheet", {"bytes_written": len(data)}
            with open(os.path.join(self.out, "cheatsheets", f"{tid}.txt"), "wb") as fh:
                fh.write(kept)
            if len(kept) == 0:
                return "failed", "empty cheatsheet", {"bytes_written": len(data), "bytes_kept": 0}
            return "done", ("truncated" if len(kept) < len(data) else ""), \
                {"bytes_written": len(data), "bytes_kept": len(kept)}
        p = os.path.join(d, "predictions.csv")
        if not os.path.isfile(p):
            return "failed", "no predictions.csv", {}
        shutil.copy(p, os.path.join(raw, "predictions.csv"))
        target = maps[maps["kind"] == "target"]
        try:
            df = pd.read_csv(p)
            pred = validate(df, list(target["local_id"]), self.P.genes)
        except (InvalidPredictions, pd.errors.ParserError, UnicodeDecodeError, ValueError) as e:
            return "failed", f"invalid predictions: {str(e)[:200]}", {}
        slide, star, truth = self.P.scored(r["arm"])
        to_spot = dict(zip(target["local_id"], target["spot"]))
        pred.index = [to_spot[i] for i in pred.index]
        rbar, pg = score(pred, truth.loc[pred.index, self.P.genes])
        with LOCK:
            pg.assign(trial_id=tid).to_csv(os.path.join(self.out, "per_gene_scores.csv"), mode="a",
                                           header=not os.path.exists(os.path.join(self.out, "per_gene_scores.csv")),
                                           index=False)
            long = pred.reset_index().rename(columns={"index": "spot"}).melt(
                id_vars="spot", var_name="gene", value_name="prediction")
            long.insert(0, "slide", slide)
            long.insert(0, "trial_id", tid)
            long.to_parquet(os.path.join(PRIVATE, "raw", tid, "predictions_long.parquet"), index=False)
        return "done", "", {"rbar": rbar, "n_constant_pred": int(pg["constant_pred"].sum())}

    # ---------- the loop ----------
    def ready(self, running):
        out = []
        for _, r in self.plan.iterrows():
            if r["slot"] in running:
                continue
            st, _ = self.slot_state(r["slot"])
            if st != "pending":
                continue
            if r.get("after", ""):  # keeps the order the instruction gives within a model
                ast, _ = self.slot_state(r["after"])
                if ast == "pending":
                    continue
            if r["role"] == "predictor":
                wst, _ = self.slot_state(r["writer_slot"])
                if wst == "failed":
                    continue
                if wst != "done":
                    continue
            out.append(r)
        return out

    def run(self):
        running = {}
        with ThreadPoolExecutor(self.parallel) as ex:
            while True:
                for r in self.ready(running):
                    if len(running) >= self.parallel:
                        break
                    running[r["slot"]] = ex.submit(self.run_slot, r)
                    time.sleep(2)
                if not running:
                    break
                done, _ = wait(list(running.values()), return_when=FIRST_COMPLETED)
                for slot in [k for k, f in running.items() if f in done]:
                    f = running.pop(slot)
                    try:
                        row = f.result()
                        print(now(), slot, row["trial_id"], row["status"], row["fail_reason"], row.get("rbar", ""),
                              row["cost_usd"], row["wall_s"], flush=True)
                    except Exception as e:  # harness error: recorded, slot left pending once
                        print(now(), slot, "HARNESS ERROR", repr(e), flush=True)
                        raise
        self.finish()

    def finish(self):
        m = self.manifest
        done = m[(m["status"] == "done") & (m["role"] != "writer")]
        parts = [pd.read_parquet(os.path.join(PRIVATE, "raw", t, "predictions_long.parquet")) for t in done["trial_id"]]
        if parts:
            df = pd.concat(parts, ignore_index=True)
            schema = pa.schema([("trial_id", pa.string()), ("slide", pa.string()), ("spot", pa.string()),
                                ("gene", pa.string()), ("prediction", pa.float64())])
            pq.write_table(pa.Table.from_pandas(df[["trial_id", "slide", "spot", "gene", "prediction"]],
                                                schema=schema, preserve_index=False),
                           os.path.join(self.out, "predictions.parquet"))
        sc = m[m["rbar"].astype(str) != ""][["trial_id", "slot", "arm", "size", "model", "replicate", "role",
                                             "writer_trial_id", "rbar", "n_constant_pred"]]
        sc.to_csv(os.path.join(self.out, "scores.csv"), index=False)


def provenance(out, cmd):
    pkg = os.path.join(PRIVATE, "package", "MANIFEST.tsv")
    scripts = sorted(f for f in os.listdir(os.path.dirname(os.path.abspath(__file__))) if f.startswith("round6_cheatsheet_"))
    head = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    ver = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    lines = [f"container_id: {os.environ.get('CLAUDE_CODE_CONTAINER_ID', '')}", f"date_utc: {now()}",
             f"code_commit: {head}", f"command: {cmd}", f"PYTHONHASHSEED: {os.environ.get('PYTHONHASHSEED', '')}",
             f"python: {platform.python_version()}", f"claude_code: {ver}",
             f"package_manifest_md5: {md5(pkg) if os.path.exists(pkg) else 'absent'}", "script_md5:"]
    lines += [f"  {md5(os.path.join(os.path.dirname(os.path.abspath(__file__)), s))}  {s}" for s in scripts]
    with open(os.path.join(out, "PROVENANCE.txt"), "a") as fh:
        fh.write("\n".join(lines) + "\n\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--stage", required=True)
    ap.add_argument("--parallel", type=int, default=2)
    ap.add_argument("--out", default=None, help="only for smoke tests outside results/")
    a = ap.parse_args()
    st = Stage(a.plan, a.stage, a.parallel, a.out)
    provenance(st.out, " ".join(sys.argv))
    st.run()
