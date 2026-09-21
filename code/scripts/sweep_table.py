#!/usr/bin/env python
"""Measure every document and emit the before-and-after table the report needs.

Stage: post-deck sweep work (post_deck_repo_instructions.md sections 2 and 5).

    python code/scripts/sweep_table.py before   # detached worktree at round2-final-deck
    python code/scripts/sweep_table.py after    # the working tree, with real exceptions
    python code/scripts/sweep_table.py compare  # join the two into one table

Two things this script exists to get right.

BEFORE is measured in a git worktree at the tag, not in the working tree. Once the
triage starts editing documents, a working-tree measurement is neither before nor after.
It is also much faster: a worktree holds only tracked files (about 90 MB) while the
working tree carries 64 GB of untracked artifacts, and the resolver walks its search
directories.

ALL documents go through ONE invocation per mode. The resolver indexes each search
directory once per process, so sixteen separate invocations walk the tree sixteen times
-- which is most of why the closeout's per-document runs took hours. The bounded-memory
rewrite is what makes a single invocation possible at all.

The before mode passes an EMPTY derived file, because the derived class is part of the
fix being measured; counting it in "before" would hide the work.
"""
import csv
import os
import subprocess
import sys

MODE = sys.argv[1] if len(sys.argv) > 1 else "compare"
assert MODE in ("before", "after", "compare"), MODE

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
TREE = os.environ.get("BEFORE_TREE",
                      "/work/users/w/e/weiyang/.claude-science-scratch/before-tree")
OUT = "/tmp/sweep_{}.csv"
SWEEP = "code/scripts/verify_numeric_claims.py"
ALWAYS = "results/summary/deck_numbers.csv"


def measure(mode):
    cwd = TREE if mode == "before" else ROOT
    docs = ["README.md"] + sorted(
        os.path.join("docs", f) for f in os.listdir(os.path.join(cwd, "docs"))
        if f.endswith(".md"))
    rows = []
    # The deck outline keeps its own exceptions file; everything else uses the
    # repository-root one. Measuring the outline against the wrong file reported 9
    # unresolved where it has none.
    for group, ex in ((
            [d for d in docs if not d.endswith("deck_master_outline.md")],
            ".verify-exceptions"),
            ([d for d in docs if d.endswith("deck_master_outline.md")],
             "docs/.verify-exceptions-deck")):
        if not group:
            continue
        derived = "/dev/null" if mode == "before" else ".verify-derived"
        p = subprocess.run(
            [sys.executable, SWEEP, *group, "--search-dir", ".",
             "--exceptions", ex, "--derived", derived, "--always", ALWAYS],
            cwd=cwd, capture_output=True, text=True)
        for line in p.stdout.splitlines():
            if "claims," not in line:
                continue
            doc, _, rest = line.partition(":")
            nums = [int(t) for t in rest.replace(",", " ").split() if t.isdigit()]
            row = dict(doc=doc.strip(), claims=nums[0], verified=nums[1],
                       unresolved=nums[2], uncited=nums[3],
                       derived_mismatch=nums[4] if len(nums) > 4 else 0,
                       derived_error=nums[5] if len(nums) > 5 else 0)
            rows.append(row)
        seen = {r["doc"] for r in rows}
        for d in group:
            if d not in seen:
                rows.append(dict(doc=d, claims=None, verified=None, unresolved=None,
                                 uncited=None, derived_mismatch=None,
                                 derived_error=None))
    return rows


def write(rows, mode):
    path = OUT.format(mode)
    cols = ["doc", "claims", "verified", "unresolved", "uncited",
            "derived_mismatch", "derived_error"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    ok = [r for r in rows if r["claims"] is not None]
    tot = {c: sum(r[c] for r in ok) for c in cols[1:]}
    print(f"{mode}: {len(ok)} assessed, {tot['claims']} claims, "
          f"{tot['verified']} verified, {tot['unresolved']} unresolved, "
          f"{tot['uncited']} uncited, {tot['derived_mismatch']} derived mismatch, "
          f"{tot['derived_error']} derived error")
    assert tot["claims"] - tot["verified"] == tot["unresolved"], "count identity fails"
    print(f"  identity holds: {tot['claims']} - {tot['verified']} = {tot['unresolved']}")
    print(f"  wrote {path}")
    return tot


def compare():
    b = {r["doc"]: r for r in csv.DictReader(open(OUT.format("before")))}
    a = {r["doc"]: r for r in csv.DictReader(open(OUT.format("after")))}
    docs = sorted(set(b) | set(a),
                  key=lambda d: -int(b.get(d, {}).get("unresolved") or 0))

    def g(d, src, k):
        v = src.get(d, {}).get(k)
        return int(v) if v not in (None, "", "None") else None

    print(f"{'document':<42} {'before':>7} {'after':>7} {'claims':>7} {'note':>22}")
    tb = ta = 0
    for d in docs:
        ub, ua = g(d, b, "unresolved"), g(d, a, "unresolved")
        cl = g(d, a, "claims") or g(d, b, "claims")
        note = ""
        if ub is None:
            note = "not assessed before"
        if ua is None:
            note = "NOT ASSESSED AFTER"
        dm = g(d, a, "derived_mismatch") or 0
        de = g(d, a, "derived_error") or 0
        if dm or de:
            note = f"{dm} mismatch, {de} error"
        tb += ub or 0
        ta += ua or 0
        print(f"{d:<42} {str(ub if ub is not None else '-'):>7} "
              f"{str(ua if ua is not None else '-'):>7} {str(cl or '-'):>7} {note:>22}")
    print(f"{'TOTAL':<42} {tb:>7} {ta:>7}")
    print(f"\nunresolved: {tb} -> {ta}  (closed {tb - ta})")
    with open("/tmp/sweep_compare.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["doc", "unresolved_before", "unresolved_after", "claims_after"])
        for d in docs:
            w.writerow([d, g(d, b, "unresolved"), g(d, a, "unresolved"),
                        g(d, a, "claims")])
        w.writerow(["TOTAL", tb, ta, ""])
    print("wrote /tmp/sweep_compare.csv")


if MODE == "compare":
    compare()
else:
    write(measure(MODE), MODE)
