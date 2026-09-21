#!/usr/bin/env python
"""Regenerate donor_audit.csv from its two committed inputs.

Stage: round 2 R5b, donor provenance audit (round2_R5_decisions.md decision 1.2,
directive 2.1); written for post_deck_repo_instructions.md section 3.

WHAT THIS SCRIPT IS, AND IS NOT. The R5b audit was a reading task: vendor dataset pages,
GEO subseries strings and an upstream issue thread. A script cannot redo that reading,
and this one does not pretend to. What it does is make donor_audit.csv a DERIVED file
rather than a hand-maintained one, by joining the two inputs that together determine it:

  hest_source_map.csv   extracted from HEST's own HEST_v1_1_0.csv -- the per-sample
                        task, patient label, subseries string, dataset title and
                        source page. Reproducible from HEST.
  donor_verdicts.csv    the audit's human output -- donor_id, donor_label_status, the
                        source citation and statement per sample. NOT reproducible
                        without redoing the reading, which is why it is committed.

The closeout report recorded the absence of this script as a reproducibility gap,
because donor_id is the grouping variable R6 and R7 use, and a grouping variable with no
regeneration path is one nobody can check.

THE COAD RULE. COAD's donor_id is the one field this script derives rather than copies.
HEST v1.1.0 labelled TENX147, TENX148 and TENX149 all as "Patient 1"; the corrected
v1.3.0 mapping is P5, P2, P1, and each slide's own subseries string carries it:

    "Xenium In Situ, Sample P5 CRC"  ->  COAD_Oliveira_P5

A COAD slide whose subseries carries no such identifier is its own donor
(TENX111, subseries "Cancer, pre-designed + add-on panel" -> COAD_donor_TENX111).

The rule is APPLIED and then ASSERTED against the recorded verdict, so if the rule and
the audit ever disagree the script fails rather than silently preferring one.

ACCEPTANCE. The script asserts it reproduces the committed donor_audit.csv byte for
byte. Run with --check to verify without writing.
"""
import os
import re
import sys

import pandas as pd

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
AUD = os.path.join(ROOT, "results/round2/R5b_audit")

SRC = os.path.join(AUD, "hest_source_map.csv")
VERD = os.path.join(AUD, "donor_verdicts.csv")
OUT = os.path.join(AUD, "donor_audit.csv")

# hest_source_map.csv column -> donor_audit.csv column
SRC_RENAME = {
    "patient": "hest_patient",
    "dataset_title": "hest_dataset_title",
    "subseries": "hest_subseries",
    "download_page_link1": "hest_source_page",
}

# The column order of the committed file. Named explicitly rather than inferred, so a
# reordering is a visible change to this script and not a silent diff.
COLUMNS = ["task", "sample_id", "hest_patient", "source_url", "donor_statement",
           "donor_id", "donor_label_status", "notes", "hest_dataset_title",
           "hest_subseries", "hest_source_page", "correction"]

COAD_SAMPLE_RE = re.compile(r"\bSample\s+(P\d+)\b")


def coad_donor_id(sample_id, subseries):
    """The COAD subseries rule. Returns the donor_id this slide's own source implies."""
    m = COAD_SAMPLE_RE.search(str(subseries))
    if m:
        return f"COAD_Oliveira_{m.group(1)}"
    return f"COAD_donor_{sample_id}"


def build():
    src = pd.read_csv(SRC)
    verd = pd.read_csv(VERD)

    assert len(src) == 72, f"hest_source_map.csv has {len(src)} rows, expected 72"
    assert len(verd) == 72, f"donor_verdicts.csv has {len(verd)} rows, expected 72"
    assert set(src.sample_id) == set(verd.sample_id), \
        "the two inputs cover different samples"

    src = src.rename(columns=SRC_RENAME)
    df = src.merge(verd, on="sample_id", how="left", validate="1:1")

    # Apply the COAD rule, then check it against the recorded verdict.
    coad = df.task == "COAD"
    derived = df.loc[coad].apply(
        lambda r: coad_donor_id(r.sample_id, r.hest_subseries), axis=1)
    recorded = df.loc[coad, "donor_id"]
    disagree = derived[derived.values != recorded.values]
    if len(disagree):
        rows = df.loc[disagree.index, ["sample_id", "hest_subseries", "donor_id"]]
        raise AssertionError(
            "the COAD subseries rule disagrees with the recorded verdict for "
            f"{len(disagree)} sample(s):\n{rows.to_string(index=False)}\n"
            f"rule gives: {list(disagree)}\n"
            "Fix the rule or the verdict -- do not let them diverge.")
    df.loc[coad, "donor_id"] = derived.values

    missing = [c for c in COLUMNS if c not in df.columns]
    assert not missing, f"join produced no {missing}"
    df = df[COLUMNS]

    # Row order of the committed file, so byte comparison is meaningful.
    order = pd.read_csv(OUT, usecols=["sample_id"]).sample_id.tolist() \
        if os.path.exists(OUT) else sorted(df.sample_id)
    df = df.set_index("sample_id").loc[order].reset_index()
    return df[COLUMNS]


def main():
    df = build()
    text = df.to_csv(index=False)

    if os.path.exists(OUT):
        committed = open(OUT).read()
        if text == committed:
            print(f"reproduces the committed {os.path.basename(OUT)} byte for byte "
                  f"({len(df)} rows)")
        else:
            # Report WHERE it differs rather than only that it does.
            cur = pd.read_csv(OUT)
            diffs = []
            for col in COLUMNS:
                if col not in cur.columns:
                    diffs.append(f"{col}: absent from the committed file")
                    continue
                a = df[col].astype(str).fillna("")
                b = cur[col].astype(str).fillna("")
                n = int((a.values != b.values).sum())
                if n:
                    diffs.append(f"{col}: {n} row(s) differ")
            msg = ("does NOT reproduce the committed file"
                   + (": " + "; ".join(diffs) if diffs else
                      " (same values, different formatting)"))
            if "--check" in sys.argv:
                print(msg)
                sys.exit(1)
            raise AssertionError(msg)
    if "--check" in sys.argv:
        return
    with open(OUT, "w") as f:
        f.write(text)
    print(f"wrote {OUT}: {len(df)} rows")
    print(df.donor_label_status.value_counts().to_string())
    print(f"donors: {df.donor_id.nunique()} across {len(df)} samples")


if __name__ == "__main__":
    main()
