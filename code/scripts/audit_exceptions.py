#!/usr/bin/env python
"""Audit the exceptions and derived files for entries that record no class or no reason.

Stage: post-deck sweep work (post_deck_repo_instructions.md section 2).

The instruction is explicit that every entry must record the claim text, the class and
the reason, and that an entry with no reason is not acceptable. Reaching zero unresolved
by adding an entry that says nothing is exactly the outcome the classes exist to prevent,
so the files get checked rather than trusted -- including the ones I wrote.

Reports, per file: entries with a missing or empty reason, entries whose reason names no
recognised class, entries whose reason is a bare back-reference ("as above") that does
not stand on its own, and duplicate claim texts.
"""
import collections
import os
import sys

# `diagnostic` is a fifth class, authorised during this stage for values measured in a
# debugging experiment and deliberately not checkpointed. The four in the instruction
# had no honest home for those: they are not costs, not historical results, not
# external, and not derivable from anything committed. Filing them as "cost" would have
# been false, so the class was added and disclosed rather than the entries misfiled.
CLASSES = ("derived", "cost", "historical", "external", "diagnostic")
FILES = sys.argv[1:] or [".verify-exceptions", "docs/.verify-exceptions-deck",
                         ".verify-derived"]

bad = 0
for path in FILES:
    if not os.path.exists(path):
        print(f"{path}: absent")
        continue
    rows, noreason, noclass, backref = [], [], [], []
    for n, raw in enumerate(open(path), 1):
        if raw.startswith("#") or not raw.strip():
            continue
        parts = raw.rstrip("\n").split("\t")
        claim = parts[0].strip()
        rest = [p.strip() for p in parts[1:]]
        rows.append(claim)
        # A derived entry is claim<TAB>formula<TAB>reason; an exception is
        # claim<TAB>reason, where the reason is conventionally "<class>: <why>".
        if path.endswith(".verify-derived"):
            if len(rest) < 2 or not rest[1]:
                noreason.append((n, claim, rest))
            continue
        reason = rest[0] if rest else ""
        if len(rest) > 1 and rest[1]:
            reason = f"{rest[0]}: {rest[1]}" if ":" not in rest[0] else reason
        if not reason:
            noreason.append((n, claim, rest))
            continue
        cls = reason.split(":")[0].strip().lower()
        if cls not in CLASSES:
            noclass.append((n, claim, reason))
        body = reason.split(":", 1)[1].strip() if ":" in reason else reason
        if len(body) < 12 or body.lower().rstrip(".") in ("as above", "see above", "ditto"):
            backref.append((n, claim, reason))

    dupes = [c for c, k in collections.Counter(rows).items() if k > 1]
    print(f"\n=== {path}: {len(rows)} entries")
    for label, items in (("NO REASON", noreason), ("NO RECOGNISED CLASS", noclass),
                         ("REASON TOO THIN", backref)):
        if items:
            bad += len(items)
            print(f"  {label}: {len(items)}")
            for n, claim, extra in items[:12]:
                print(f"    L{n:<4} claim={claim[:34]!r:38} -> {str(extra)[:78]}")
    if dupes:
        print(f"  DUPLICATE claim texts: {len(dupes)} -> {dupes[:6]}")
    if not (noreason or noclass or backref or dupes):
        print("  clean: every entry has a class and a reason that stands on its own")

print(f"\ntotal problem entries: {bad}")
sys.exit(1 if bad else 0)
