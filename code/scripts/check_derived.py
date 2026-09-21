#!/usr/bin/env python
"""Evaluate every entry in .verify-derived and compare it with the claim it stands for.

Stage: post-deck sweep work (post_deck_repo_instructions.md section 2).

A derived entry is only worth having if it is actually evaluated. This checks all of them
in one pass, independently of document scanning, so a formula that disagrees with its
claim is found even before the document is swept -- and a disagreement is the interesting
outcome: it means either the formula is wrong or the number in the document is, and a
declared exception would have hidden both.

Search directories are scoped rather than walking the whole repository, because the
working tree carries 64 GB of untracked artifacts and a full walk exceeds the interactive
command limit.
"""
import importlib.util
import os
import sys

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
os.chdir(ROOT)

spec = importlib.util.spec_from_file_location(
    "v", os.path.join(ROOT, "code/scripts/verify_numeric_claims.py"))
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)

DIRS = ["results/summary", "results/round2", "results/tailored", "results/faithful"]
resolver = V.make_resolver(DIRS)

entries = V.load_derived(".verify-derived")
print(f"{len(entries)} derived entries\n")

ok = mismatch = err = 0
for key, (formula, reason) in sorted(entries.items()):
    # An entry may be scoped to a document: "docs/WAYS_OF_WORKING.md:117". The claim is
    # the part after the last colon; the scope only decides which document the entry
    # applies to and is not part of the number.
    claim = key.rsplit(":", 1)[1] if ".md:" in key else key
    try:
        val, shown = V.eval_derived(formula, resolver)
    except V.DerivedError as e:
        print(f"  ERROR     {claim:<12} {str(e)[:92]}")
        err += 1
        continue
    # Precision comes from the sweep's OWN parser, not a private copy of the rule. The
    # private copy counted the exponent's characters as decimal places -- "3.15e-02" read
    # as six decimals instead of four -- so two formulas that the sweep accepts were
    # reported here as mismatches. One source of truth for how precise a written number
    # is; a checker that disagrees with the checker is worse than no second check.
    parsed = V.parse_claim(claim)
    if parsed is None:
        print(f"  UNPARSED  {claim!r}")
        err += 1
        continue
    target, dec, pct = parsed
    if pct and abs(val) <= 1.5:
        val *= 100
    tol = 0.5 * (10 ** -dec) * 1.000001
    if abs(val - target) <= tol:
        print(f"  ok        {claim:<12} = {val:.6g}")
        ok += 1
    else:
        print(f"  MISMATCH  {claim:<12} formula gives {val:.6g}, document says {target:.6g}")
        print(f"            {formula[:100]}")
        mismatch += 1

print(f"\n{ok} agree, {mismatch} mismatch, {err} unevaluable")
sys.exit(1 if (mismatch or err) else 0)
