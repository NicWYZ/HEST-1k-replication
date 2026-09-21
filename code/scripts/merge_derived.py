#!/usr/bin/env python
"""Recover .verify-derived after a concurrent overwrite, merging three sources.

Stage: post-deck sweep work (post_deck_repo_instructions.md section 2).

What happened. Four triage tracks and this session were all told to edit .verify-derived
and .verify-exceptions. The exceptions file survived because every writer appended to it.
The derived file did not: one track wrote it as a new file, which discarded the 15 entries
an earlier track had put there and the 5 this session had moved in from the exceptions
file. Nothing was corrupted -- the file is valid and self-consistent -- which is exactly
why it went unnoticed until a document that had verified came back with an unresolved
claim.

That is my error, not the track's. Handing several concurrent writers the same file with
no protocol invites precisely this, and the fix for next time is either one writer per
file or a per-track fragment merged at the end.

Three sources, merged by claim text:
  BACKUP   /tmp/der.bak, taken before this session's edits: the 15 entries from the
           replicate-leak triage.
  MINE     the 5 entries moved out of .verify-exceptions, restated here with the
           CORRECTED formulas -- two of the originals were wrong and the derived check
           caught them (a single patient filter spans three tasks; an inter-session gap
           is not the within-patient range).
  CURRENT  whatever .verify-derived holds now: the 23 entries from the split-decomposition
           triage.

A claim present in more than one source with a DIFFERENT formula is reported rather than
silently resolved, because keying by claim text is document-agnostic: "117" is a computed
value in one document and a journal volume in another, and a collision may mean two
unrelated claims share a numeral.
"""
import os
import sys

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
CUR = os.path.join(ROOT, ".verify-derived")
BAK = "/tmp/der.bak"

SM = "results/tailored/integrity/sample_metadata.csv"
MINE = [
    ("5.02", f"{SM}#pixel_size_um:max / {SM}#pixel_size_um:min",
     "derived: fold-ratio of max/min pixel_size_um across the 72 samples; moved from "
     ".verify-exceptions so it is evaluated rather than declared"),
    ("1.71", f"{SM}#pixel_size_um:max@task=IDC / {SM}#pixel_size_um:min@task=IDC",
     "derived: within-task pixel-size fold-ratio for IDC; moved from .verify-exceptions"),
    ("1.02", f'{SM}#pixel_size_um:max@task=PRAD@patient="patient 2" / '
             f'{SM}#pixel_size_um:min@task=PRAD@patient="patient 2"',
     "derived: within-patient pixel-size fold-ratio for PRAD patient 2. The task filter "
     "is load-bearing: the patient label is not unique across tasks, and without it this "
     "came out 2.55 -- caught by the derived check, which a declared exception would not "
     "have done"),
    ("0.0066", f"{SM}#pixel_size_um@sample_id=MEND150 - {SM}#pixel_size_um@sample_id=MEND139",
     "derived: gap BETWEEN PRAD patient 2's two scan sessions -- the upper cluster's "
     "lowest slide minus the lower cluster's highest. NOT the within-patient range, which "
     "is 0.0080; sample_metadata.csv has no session column, so the two bounding slides are "
     "named. The first version of this formula said max-minus-min and the derived check "
     "caught it"),
    ("54", ' 100 * results/round2/R5c_leak/r5c_leak_summary.csv#mean@task=IDC / '
           'results/round2/R3_splits/r3_per_task_terms.csv#"TOTAL random - patient"@task=IDC',
     "derived: IDC leak as a percentage of its random-minus-patient gap; the column name "
     "is quoted because it contains a hyphen"),
]


def read(path):
    out = {}
    order = []
    if not os.path.exists(path):
        return out, order, []
    head = []
    for raw in open(path):
        if raw.startswith("#") or not raw.strip():
            head.append(raw)
            continue
        parts = raw.rstrip("\n").split("\t")
        if len(parts) < 2:
            continue
        claim = parts[0].strip()
        out[claim] = (parts[1].strip(), parts[2].strip() if len(parts) > 2 else "")
        order.append(claim)
    return out, order, head


cur, cur_order, head = read(CUR)
bak, bak_order, _ = read(BAK)

merged, collisions = {}, []
for label, src in (("backup", bak), ("current", cur)):
    for claim, (formula, reason) in src.items():
        if claim in merged and merged[claim][0] != formula:
            collisions.append((claim, merged[claim][0], formula))
        merged.setdefault(claim, (formula, reason))
for claim, formula, reason in MINE:
    if claim in merged and merged[claim][0] != formula:
        collisions.append((claim, merged[claim][0], formula))
    merged[claim] = (formula, reason)          # my corrected versions win

if not head:
    head = ["# Derived-claim formulas. Format: claim<TAB>formula<TAB>reason.\n",
            "# '#' is a comment ONLY at the start of a line (the formula syntax uses "
            "'#' for file#column).\n", "\n"]

with open(CUR, "w") as f:
    f.writelines(head)
    for claim in sorted(merged):
        formula, reason = merged[claim]
        f.write(f"{claim}\t{formula}\t{reason}\n")

print(f"backup {len(bak)} + current {len(cur)} + mine {len(MINE)} -> {len(merged)} merged")
print(f"recovered from the backup: "
      f"{sorted(set(bak) - set(cur) - {c for c, _, _ in MINE})}")
if collisions:
    print(f"\nCOLLISIONS ({len(collisions)}) -- same claim text, different formula:")
    for claim, a, b in collisions:
        print(f"  {claim!r}\n    kept:  {a[:88]}\n    other: {b[:88]}")
    print("  Keying by claim text is document-agnostic; check these are the same quantity.")
sys.exit(0)
