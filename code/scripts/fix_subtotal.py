#!/usr/bin/env python
"""Correct the 16-document subtotal in docs_clean_report.md, and compute it rather than type it.

Stage: post-deck numeric-claim gate (post_deck_repo_instructions.md section 5).

The 19-document total in that report was computed from the per-document counts; the
16-document subtotal beside it was typed, and typed wrong -- 1,806 where the same counts
give 1,809. Exactly the fault this whole exercise exists to catch, in the report about the
exercise. Both totals are now derived here from the table's own rows, and the identity
subtotal + the three late rows = total is asserted, so the two cannot drift apart again.
"""
import os
import re
import sys

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
P = os.path.join(ROOT, "docs/docs_clean_report.md")
s = open(P).read()

# Parse the after-column from the table's own rows rather than trusting any total.
ROW = re.compile(r"^\| `([^`]+)`( †)? \| ([\d,]+|—) \| (?:\*\*)?(\d+)(?:\*\*)?|—"
                 r" \| (\d+) \| (\d+) \|$", re.M)
rows, late = {}, {}
for line in s.split("\n"):
    m = re.match(r"^\| `([^`]+)`( †)? \| .* \| (\d+) \| (\d+) \|$", line)
    if not m:
        continue
    doc, dagger, after_claims, after_unres = m.group(1), bool(m.group(2)), int(m.group(3)), int(m.group(4))
    (late if dagger else rows)[doc] = (after_claims, after_unres)

sub = sum(c for c, _ in rows.values())
lat = sum(c for c, _ in late.values())
unres = sum(u for u, in [(u,) for _, u in list(rows.values()) + list(late.values())])
print(f"parsed {len(rows)} core rows + {len(late)} late rows")
print(f"  subtotal {sub:,}  late {lat:,}  total {sub + lat:,}  unresolved {unres}")
if len(rows) != 16 or len(late) != 3:
    print("ROW PARSE UNEXPECTED -- refusing to edit")
    sys.exit(1)

s2 = s.replace(f"| **total, 16 documents** | **1,786** | **688** | **1,806** | **0** |",
               f"| **total, 16 documents** | **1,786** | **688** | **{sub:,}** | **0** |")
s2 = re.sub(r"\| \*\*total, 19 documents\*\* \| \| \| \*\*[\d,]+\*\* \| \*\*0\*\* \|",
            f"| **total, 19 documents** | | | **{sub + lat:,}** | **0** |", s2)
if s2 == s:
    print("nothing replaced -- the totals may already be correct")
else:
    open(P, "w").write(s2)
    print(f"rewrote both totals from the rows: {sub:,} and {sub + lat:,}")

check = open(P).read()
assert f"**{sub:,}** | **0** |" in check and f"**{sub + lat:,}** | **0** |" in check
assert "1,806" not in check, "the wrong subtotal survives"
print("read-back: both totals present and the wrong subtotal is gone")
