#!/usr/bin/env python
"""Derive the derived-formula count in docs_clean_report.md instead of typing it.

Stage: post-deck numeric-claim gate (post_deck_repo_instructions.md section 5).

The report said "117 derived formulas ... all 117 agreeing". The gate run in the very same
cell printed 118: a formula had been added between the sentence being written and the
check being run. Third typed number in this report to disagree with its own evidence, so
this one is read from .verify-derived and cross-checked against check_derived.py's own
output rather than written by hand.
"""
import os
import re
import subprocess
import sys

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
os.chdir(ROOT)
P = "docs/docs_clean_report.md"

# Count the entries in the file itself.
n_file = sum(1 for line in open(".verify-derived")
             if line.strip() and not line.startswith("#"))

# And ask the checker, which parses the same file and evaluates every entry.
out = subprocess.run([sys.executable, "code/scripts/check_derived.py"],
                     capture_output=True, text=True).stdout
m = re.search(r"(\d+) agree, (\d+) mismatch, (\d+) unevaluable", out)
if not m:
    print("could not read the checker's summary line; refusing to edit")
    print(out[-400:])
    sys.exit(1)
agree, mismatch, unevaluable = (int(g) for g in m.groups())
print(f".verify-derived entries: {n_file} | checker: {agree} agree, "
      f"{mismatch} mismatch, {unevaluable} unevaluable")
if agree != n_file or mismatch or unevaluable:
    print("the file count and the checker disagree, or a formula fails; refusing to edit")
    sys.exit(1)

s = open(P).read()
before = s
s = re.sub(r"\*\*\d+ derived formulas\*\*", f"**{n_file} derived formulas**", s)
s = re.sub(r"all \d+ agreeing with the claims", f"all {n_file} agreeing with the claims", s)
s = re.sub(r"(\d+) derived formulas all agreeing", f"{n_file} derived formulas all agreeing", s)
if s == before:
    print("no formula-count sentence matched; nothing changed")
else:
    open(P, "w").write(s)

check = open(P).read()
stale = [m.group(0) for m in re.finditer(r"\b117\b(?=[^\n]{0,40}(derived|agreeing))", check)]
print(f"rewrote to {n_file}; stale '117' near a formula claim: {stale or 'none'}")
