#!/usr/bin/env python
"""Replace the stale upper bound on the live unresolved count with the measured figure.

Stage: post-deck numeric-claim gate (post_deck_repo_instructions.md section 5).

closeout_gate_report.md hedged the live count as "at most 441" because the triage was
still running when that sentence was written. That was the honest statement at the time.
It is now measured at zero, so the bound is superseded -- and the replacement says so
rather than quietly swapping the number, because the bound was not wrong.
"""
import os
import sys

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
P = os.path.join(ROOT, "docs/closeout_gate_report.md")
s = open(P).read()

OLD = ("The live current total, as of this\nsession's last combined sweep run, is at most "
       "`688 minus 228 minus 19, i.e. 441` and may\nbe lower still wherever a sibling track "
       "has also since triaged its document.")
NEW = ("The live current total is **zero**: every document in the repository has since been "
       "triaged to zero unresolved and zero uncited, verified in a final combined sweep of "
       "1,992 claims across nineteen documents. This sentence previously gave an upper bound "
       "of `441`, which was the honest statement while the triage was still running; the "
       "measured figure replaces it. The per-document table is in `docs_clean_report.md`.")

if OLD not in s:
    print("PASSAGE NOT FOUND -- nothing changed. Current text around 'live current total':")
    i = s.find("live current total")
    print(repr(s[max(0, i - 120):i + 320]))
    sys.exit(1)

s = s.replace(OLD, NEW, 1)
s = s.rstrip("\n") + (
    "\n- 22 September 2026: replaced the `at most 441` upper bound on the live unresolved\n"
    "  count with the measured figure, zero, now that every document has been triaged and\n"
    "  re-swept. The bound was correct when written and is superseded, not wrong.\n")
open(P, "w").write(s)

check = open(P).read()
assert NEW.split(".")[0] in check, "write did not land"
assert "at most" not in check.split("## Changelog")[0], "the old bound survives above the changelog"
print("replaced; 'at most' occurrences now:", check.count("at most"))
