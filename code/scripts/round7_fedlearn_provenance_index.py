#!/usr/bin/env python
"""Round 7 federated learning track: provenance index and the two gate checks.

Section 5 of docs/round07/i01/fedlearn/round07_fedlearn_track.md, after item 6 of section 4 of
docs/round05/i02/ppi/round5_ppi_E2_decisions.md. Run in the Mac clone before a gate push. It reads
every PROVENANCE.txt under results/round7/fedlearn/ and writes
results/round7/fedlearn/provenance_index.csv with one row per job and script:

  check1_ancestor  the recorded snapshot commit is an ancestor of the gate ref
  check2_md5       the recorded script md5 equals the md5 of that script at the recorded commit

Usage: python code/scripts/round7_fedlearn_provenance_index.py <gate ref, for example HEAD>
It reads git objects only and computes no statistic.
"""
import csv
import glob
import hashlib
import os
import subprocess
import sys

OUT = "results/round7/fedlearn/provenance_index.csv"


def git(*args):
    return subprocess.run(["git", "--no-optional-locks", *args], capture_output=True)


def parse(path):
    recs, cur, in_md5 = [], {}, False
    for line in open(path).read().splitlines() + [""]:
        if not line.strip():
            if cur:
                recs.append(cur)
            cur, in_md5 = {}, False
            continue
        if line.startswith("script_md5:"):
            in_md5 = True
            cur["scripts"] = []
            continue
        if in_md5 and line.startswith("  "):
            md5, script = line.split()
            cur["scripts"].append((script, md5))
            continue
        in_md5 = False
        if ": " in line:
            k, v = line.split(": ", 1)
            cur[k.strip()] = v.strip()
    return recs


def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    ref_hash = git("rev-parse", ref).stdout.decode().strip()
    rows = []
    for p in sorted(glob.glob("results/round7/fedlearn/**/PROVENANCE.txt", recursive=True)):
        for r in parse(p):
            commit = r.get("snapshot_commit", "")
            anc = git("merge-base", "--is-ancestor", commit, ref).returncode == 0 if commit else False
            for script, md5 in r.get("scripts", []):
                blob = git("show", f"{commit}:{script}")
                at_commit = hashlib.md5(blob.stdout).hexdigest() if blob.returncode == 0 else ""
                rows.append(dict(job_id=r.get("slurm_job_id", ""), platform="Longleaf", stage=r.get("stage", ""),
                                 partition=r.get("partition", ""), node=r.get("node", ""), script_path=script, md5=md5,
                                 recorded_commit=commit, provenance_file=p, gate_ref=ref, gate_ref_hash=ref_hash,
                                 check1_ancestor=anc, md5_at_commit=at_commit, check2_md5=(md5 == at_commit)))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cols = ["job_id", "platform", "stage", "partition", "node", "script_path", "md5", "recorded_commit",
            "provenance_file", "gate_ref", "gate_ref_hash", "check1_ancestor", "md5_at_commit", "check2_md5"]
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"rows={len(rows)} check1_fail={sum(not r['check1_ancestor'] for r in rows)} "
          f"check2_fail={sum(not r['check2_md5'] for r in rows)}")


if __name__ == "__main__":
    main()
