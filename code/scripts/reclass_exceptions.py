#!/usr/bin/env python
"""Give every exception entry a class, and convert the computable ones into checked formulas.

Stage: post-deck sweep work (post_deck_repo_instructions.md section 2).

43 entries in the two exceptions files carried a substantive reason but no class prefix:
they were written before this instruction mandated derived / cost / historical / external.
The instruction is explicit on both points -- every entry records the class, and a number
that is *derived* must not be declared but written as a formula the sweep EVALUATES.

So this does two things, and the first matters more than the second:

  MOVE  the entries whose quantity is computable from committed files out of
        .verify-exceptions and into .verify-derived as formulas. A declared exception
        asserts "this cannot be checked"; a formula gets checked. The entries that move
        are exactly the keys of TO_DERIVED below -- the script prints the count it
        actually moved rather than this docstring asserting one, because an earlier
        version of this text claimed eleven while the dict listed five. They became
        expressible only after the derived language gained group-filtered statistics,
        quoted key values and multi-key filters, each added in response to a triage pass
        reporting the previous form as a limitation.

  CLASS the rest with the class their reason already describes: historical for round-1
        results and withdrawn values, cost for scheduler accounting, external for
        constants quoted from the paper or the leaderboard.

Idempotent: an entry that already carries a recognised class prefix is left alone.
"""
import os
import sys

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
EXC = os.path.join(ROOT, ".verify-exceptions")
DEC = os.path.join(ROOT, "docs/.verify-exceptions-deck")
DER = os.path.join(ROOT, ".verify-derived")

SM = "results/tailored/integrity/sample_metadata.csv"

# claim -> formula. Every one of these is a quantity computable from committed files that
# was previously declared unverifiable.
TO_DERIVED = {
    "5.02": f"{SM}#pixel_size_um:max / {SM}#pixel_size_um:min",
    "1.71": f"{SM}#pixel_size_um:max@task=IDC / {SM}#pixel_size_um:min@task=IDC",
    "1.02": (f'{SM}#pixel_size_um:max@patient="patient 2" / '
             f'{SM}#pixel_size_um:min@patient="patient 2"'),
    "0.0066": (f'{SM}#pixel_size_um:max@patient="patient 2" - '
               f'{SM}#pixel_size_um:min@patient="patient 2"'),
    "54": ("100 * results/round2/R5c_leak/r5c_leak_summary.csv#mean@task=IDC / "
           "results/round2/R3_splits/r3_per_task_terms.csv#TOTAL random - patient@task=IDC"),
}

# claim -> class, for the entries whose quantity is genuinely not computable here.
TO_CLASS = {
    # round-1 results whose source files were not carried into round 2
    "0.3278": "historical", "0.326": "historical", "0.3046": "historical",
    "0.458": "historical", "0.2938": "historical", "0.026": "historical",
    "0.163": "historical", "2.83": "historical", "1.61": "historical",
    "\u22122.002": "historical", "0.61": "historical", "3.654": "historical",
    "0.014": "historical", "0.099": "historical", "0.002": "historical",
    "0.052": "historical", "\u22120.95": "historical", "474": "historical",
    # scheduler accounting and process facts with no result file behind them
    "8.8": "cost", "5.5": "cost", "70": "cost", "34": "cost", "429": "cost",
    # constants quoted from the paper, the leaderboard or another publication
    "1,229": "external", "153": "external", "112": "external", "224": "external",
    "0.41": "external", "25": "external", "0.42": "external", "0.415": "external",
    "0.47": "external", "2406.16192": "external",
    # a design constant of ours, recorded in a script rather than a results file. None of
    # the four classes fits a design choice; external is the closest, and the reason names
    # the script so a reader can see where it is set. Disclosed in the report.
    "2.5": "external",
}

# Entries that remain declared because the quantity IS derived but the formula language
# still cannot express it. Recorded as such rather than silently classed as something else.
DERIVED_INEXPRESSIBLE = {
    "1.01": "derived",   # a max OVER GROUPS of a within-group ratio
    "2.1": "derived",    # ratio of two spot counts held in no committed table
    "96.1": "derived",   # ratio of two SUMS over a filtered confusion table
    "5.4": "derived",    # mantissa of a p-value, now parsed, kept until re-measured
}

CLASSES = ("derived", "cost", "historical", "external")


def load(path):
    out = []
    for raw in open(path):
        if raw.startswith("#") or not raw.strip():
            out.append((None, raw))
            continue
        parts = raw.rstrip("\n").split("\t")
        out.append((parts, raw))
    return out


def main():
    moved, classed, left = [], [], []
    for path in (EXC, DEC):
        rows, keep = load(path), []
        for parts, raw in rows:
            if parts is None:
                keep.append(raw)
                continue
            claim = parts[0].strip()
            reason = parts[1] if len(parts) > 1 else ""
            if reason.split(":")[0].strip().lower() in CLASSES:
                keep.append(raw)
                continue
            if path == EXC and claim in TO_DERIVED:
                moved.append((claim, TO_DERIVED[claim], reason))
                continue                       # drop from the exceptions file
            cls = TO_CLASS.get(claim) or DERIVED_INEXPRESSIBLE.get(claim)
            if cls:
                keep.append(f"{claim}\t{cls}: {reason}\n")
                classed.append((claim, cls))
            else:
                keep.append(raw)
                left.append((os.path.basename(path), claim, reason[:60]))
        with open(path, "w") as f:
            f.writelines(keep)

    if moved:
        with open(DER, "a") as f:
            for claim, formula, reason in moved:
                f.write(f"{claim}\t{formula}\t"
                        f"{reason} -- moved from .verify-exceptions so it is evaluated "
                        f"rather than declared\n")

    print(f"moved to .verify-derived (now evaluated): {len(moved)}")
    for claim, formula, _ in moved:
        print(f"  {claim:<9} {formula[:88]}")
    print(f"\nclassed in place: {len(classed)}")
    for cls in CLASSES:
        n = [c for c, k in classed if k == cls]
        if n:
            print(f"  {cls:<11} {len(n):>3}  {', '.join(n[:9])}")
    if left:
        print(f"\nSTILL UNCLASSED: {len(left)}")
        for f_, c, r in left:
            print(f"  {f_} {c!r}: {r}")
        sys.exit(1)
    print("\nevery entry now carries a class")


if __name__ == "__main__":
    main()
