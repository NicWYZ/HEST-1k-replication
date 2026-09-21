#!/usr/bin/env python
"""Extract donor_verdicts.csv -- the audit's irreducible human output -- from donor_audit.csv.

Stage: post-deck repository gaps (post_deck_repo_instructions.md section 3).

Run ONCE, to split the committed donor_audit.csv into the two things it actually
contains: fields copied from HEST's own metadata (which hest_source_map.csv already
holds) and fields a human determined by reading sources outside HEST (which nothing
holds separately, and which round2_r5b_audit.py cannot recompute).

After this, donor_audit.csv is a derived file: round2_r5b_audit.py joins
hest_source_map.csv to donor_verdicts.csv and must reproduce it exactly.

This script is kept in the repository rather than discarded, because it documents where
donor_verdicts.csv came from -- but it is not part of the regeneration path and must
never be run again: it reads donor_audit.csv, so re-running it after an edit to the
audit would launder that edit into the verdicts file and destroy the check.
"""
import os
import sys

import pandas as pd

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
AUD = os.path.join(ROOT, "results/round2/R5b_audit")

# Fields a human determined by reading a source. Everything else in donor_audit.csv is
# either from hest_source_map.csv or derived by the COAD rule.
VERDICT_COLS = ["sample_id", "donor_id", "donor_label_status", "source_url",
                "donor_statement", "notes", "correction"]

d = pd.read_csv(os.path.join(AUD, "donor_audit.csv"))
assert len(d) == 72, f"expected 72 samples, found {len(d)}"
missing = [c for c in VERDICT_COLS if c not in d.columns]
assert not missing, f"donor_audit.csv lacks {missing}"

out = os.path.join(AUD, "donor_verdicts.csv")
if os.path.exists(out) and "--force" not in sys.argv:
    print(f"{out} already exists; refusing to overwrite (pass --force only if you are "
          f"certain donor_audit.csv has not been edited since it was extracted)")
    sys.exit(1)

d[VERDICT_COLS].to_csv(out, index=False)
print(f"wrote {out}: {len(d)} rows, {len(VERDICT_COLS)} columns")
print(d.donor_label_status.value_counts().to_string())
