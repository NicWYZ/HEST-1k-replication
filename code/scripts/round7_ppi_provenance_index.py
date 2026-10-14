"""Round 7 inference track: provenance index (round 5 E2 memo, section 4, item 6).

Reads every PROVENANCE.txt under results/round7/ppi/ in the clone, and the records of units whose own PROVENANCE.txt
stays on Longleaf from results/round7/ppi/provenance_raw/. Writes results/round7/ppi/provenance_index.csv with one row
per job and script. Check 1: the recorded snapshot commit is an ancestor of --head (the gate tag is that commit or a
descendant of it). Check 2: the recorded md5 equals the md5 of the script at the recorded commit.
Run from the repository root.
"""
import argparse
import glob
import hashlib
import os
import subprocess

import pandas as pd


def git(*a):
    return subprocess.run(["git", *a], capture_output=True)


def parse(path):
    d, scripts, mode = {}, [], None
    for line in open(path).read().splitlines():
        if line.startswith("scripts_executed"):
            mode = "s"
            continue
        if line.startswith("inputs"):
            mode = None
            continue
        if mode == "s" and line.startswith("  "):
            md5, p = line.split()
            scripts.append((p, md5))
            continue
        if ": " in line and not line.startswith(" "):
            k, v = line.split(": ", 1)
            d[k] = v
    return d, scripts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--head", default="HEAD")
    a = ap.parse_args()
    head = git("rev-parse", a.head).stdout.decode().strip()
    files = sorted(glob.glob("results/round7/ppi/**/PROVENANCE.txt", recursive=True))
    files += sorted(glob.glob("results/round7/ppi/provenance_raw/*.txt"))
    rows, anc, blob = [], {}, {}
    for f in files:
        d, scripts = parse(f)
        c = d.get("snapshot_commit", "")
        if c not in anc:
            anc[c] = git("merge-base", "--is-ancestor", c, head).returncode == 0 if c else False
        for p, md5 in scripts:
            if (c, p) not in blob:
                r = git("show", f"{c}:{p}")
                blob[(c, p)] = hashlib.md5(r.stdout).hexdigest() if r.returncode == 0 else ""
            rows.append(dict(job_id=d.get("slurm_job_id", ""), platform=d.get("platform", ""), stage=d.get("stage", ""),
                             unit=d.get("unit", ""), status=d.get("status", ""), frame_id=d.get("frame_id", ""),
                             script_path=p, md5=md5, recorded_commit=c, provenance_file=f, head_tested=head,
                             check1_ancestor=anc[c], check2_md5=blob[(c, p)] == md5))
    df = pd.DataFrame(rows)
    df.to_csv("results/round7/ppi/provenance_index.csv", index=False)
    print(len(files), len(df), df["job_id"].nunique(), int((~df["check1_ancestor"]).sum()), int((~df["check2_md5"]).sum()))


if __name__ == "__main__":
    main()
