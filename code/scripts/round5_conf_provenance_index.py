#!/usr/bin/env python
"""Round 5 conformal track: provenance index over every PROVENANCE.txt.

For each (PROVENANCE.txt block, script_md5 line) it records the job, the
unit (results directory), the script, the recorded md5 and the recorded
commit, and runs two checks (memo section 4):

  check 1  the recorded commit is an ancestor of the gate commit
  check 2  the recorded md5 equals the md5 of the script at that commit

The recorded commit is `snapshot_commit` when it is a hash, else the
`code_clone_head` of the clone the job ran from.  A staged copy (a script path
outside a clone) is mapped to code/scripts/<file name>.  When check 2 fails the
script reports the first commit (on the gate's first-parent history) whose
blob has the recorded md5, so staged-script runs stay traceable.

Usage: round5_conf_provenance_index.py --gate <rev> --out <csv>
Run from the repository root.
"""
import argparse, csv, hashlib, re, subprocess, sys
from pathlib import Path

ROOT = Path("results/round5/conformal")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SNAP = re.compile(r"_snapshots/([0-9a-f]{40})")


def git(*a, check=True):
    r = subprocess.run(["git", *a], capture_output=True)
    if check and r.returncode:
        raise RuntimeError(r.stderr.decode())
    return r


def blob_md5(commit, path):
    r = git("show", f"{commit}:{path}", check=False)
    return hashlib.md5(r.stdout).hexdigest() if r.returncode == 0 else None


def parse_blocks(text):
    blocks, cur = [], None
    for line in text.splitlines():
        if line.startswith("====="):
            continue
        if line.startswith("Round 5 conformal track"):
            cur = {"stage": line.split("stage", 1)[-1].strip(), "md5": []}
            blocks.append(cur)
            continue
        if cur is None or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if k == "script_md5":
            m, _, p = v.partition("  ")
            cur["md5"].append((m.strip(), p.strip()))
        else:
            cur.setdefault(k, v)
    return blocks


def repo_path(abs_path):
    """Map a recorded absolute script path to its path in the repository."""
    i = abs_path.find("/code/")
    if i >= 0:
        return abs_path[i + 1:]
    # staged copy (job workdir or results directory): same file name under code/scripts
    name = Path(abs_path).name
    if not name.startswith("round5_conf_") and name.startswith("w"):
        name = "round5_conf_" + name   # staged under a short name, committed with the prefix
    return "code/scripts/" + name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    gate = git("rev-parse", a.gate).stdout.decode().strip()
    history = git("rev-list", "--reverse", "--first-parent", gate).stdout.decode().split()
    rows, cache = [], {}
    for prov in sorted(ROOT.rglob("PROVENANCE.txt")):
        for b in parse_blocks(prov.read_text(errors="replace")):
            snap = b.get("snapshot_commit", "")
            head = b.get("code_clone_head", "")
            if HEX40.match(snap):
                commit, src = snap, "snapshot_commit"
            elif HEX40.match(head.split()[0] if head else ""):
                commit, src = head.split()[0], "code_clone_head"
            elif SNAP.search(b.get("code_clone", "")):
                commit, src = SNAP.search(b["code_clone"]).group(1), "code_clone snapshot directory"
            else:
                commit, src = "", f"none (snapshot_commit={snap!r}; code_clone_head={head!r})"
            anc = (git("merge-base", "--is-ancestor", commit, gate, check=False).returncode == 0) if commit else False
            for md5, p in b["md5"]:
                rp = repo_path(p)
                at = blob_md5(commit, rp) if (commit and rp) else None
                ok2 = at == md5
                first = ""
                if not ok2 and rp:
                    key = (rp, md5)
                    if key not in cache:
                        cache[key] = next((c for c in history if blob_md5(c, rp) == md5), "")
                    first = cache[key]
                staged = "/code/" not in p
                if ok2:
                    note = "md5 matches the script at the recorded commit"
                elif first and staged:
                    note = f"staged copy; md5 first appears at {first[:7]} on the gate history"
                elif first:
                    note = (f"run from an uncommitted working tree at {commit[:7]}; "
                            f"md5 first appears at {first[:7]} (the commit that delivered it)")
                else:
                    note = "UNTRACED: md5 not found on the gate history"
                rows.append({
                    "unit": str(prov.parent.relative_to(ROOT)),
                    "stage": b.get("stage", ""),
                    "slurm_job_id": b.get("slurm_job_id", ""),
                    "node": b.get("node", ""),
                    "cpu_model": b.get("cpu_model", ""),
                    "script": rp or p,
                    "recorded_path": p,
                    "recorded_md5": md5,
                    "recorded_commit": commit,
                    "commit_source": src,
                    "check1_ancestor_of_gate": anc,
                    "md5_at_recorded_commit": at or "",
                    "check2_md5_matches": ok2,
                    "first_gate_commit_with_md5": first,
                    "first_commit_is_ancestor": bool(first),
                    "staged_copy": staged,
                    "resolution": note,
                })
    keys = list(rows[0]) if rows else []
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader(); w.writerows(rows)
    n = len(rows)
    c1 = sum(r["check1_ancestor_of_gate"] for r in rows)
    c2 = sum(r["check2_md5_matches"] for r in rows)
    tr = sum(r["check2_md5_matches"] or r["first_commit_is_ancestor"] for r in rows)
    print(f"gate {gate} rows {n} check1 {c1} check2 {c2} traceable {tr}")


if __name__ == "__main__":
    sys.exit(main())
