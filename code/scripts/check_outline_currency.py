#!/usr/bin/env python
"""Check that a document quotes CURRENT results, not merely resolvable ones.

Stage: closeout repository refresh (deck_figures_and_repo_update.md section 2.6).

verify_numeric_claims.py answers "does this number exist in a cited file". That is
not the same question as "is this the number we would compute today", and in this
repository the gap is real: two of the three file pairs retired during the
closeout were byte-level re-writes carrying identical values, so a stale
quotation can match a stale file and pass. One quotation had already slipped
through that way -- theta1 on the top IDC slide, quoted from round 1's morphology
build while the current build gives a different value, with both builds on disk.

Three checks, none of which the numeric sweep performs:

1. WITHDRAWN QUANTITIES. Round 2 withdrew six specific claims. A withdrawn number
   can survive a numeric sweep indefinitely, because the file that supported it
   is still in the repository. These are matched as literal strings.

2. SUPERSEDED-ONLY RESOLUTION. Re-run the numeric sweep with `superseded/`
   excluded from the resolver. Any claim that was verified before and is
   unresolvable now was resolving only against a retired file.

3. VERSIONED BUILDS. Where a quantity exists under two builds -- the two
   morphology builds, the float32 and float64 head families, the 11- and
   12-encoder width cohorts -- report which build the document's value matches,
   so quoting the superseded one is visible rather than silent.
"""
import os
import re
import subprocess
import sys

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
DOC = sys.argv[1] if len(sys.argv) > 1 else "docs/deck_master_outline.md"

# ---------------------------------------------------------------- check 1
# (pattern, what it was, why it was withdrawn)
WITHDRAWN = [
    (r"0\.0419", "the institution-shift scalar",
     "its two arms share a generating laboratory and differ in scan resolution, "
     "so it is not an institution contrast"),
    (r"0\.1241", "the pooled slide-signature term",
     "it averaged over tasks where the contrast means different things; per task "
     "it ranges from 0.026 to 0.294"),
    (r"confound[- ]free", "the phrase 'confound-free'",
     "no contrast in HEST-bench is confound-free; the IDC one differs in "
     "resolution as well as source"),
    (r"199\s*[x\u00d7]|199-fold", "the 199x COAD ratio",
     "its denominator is indistinguishable from zero, and COAD's patient labels "
     "do not separate patients"),
    (r"7\.6\s*\\?times?\s*10\^?\{?14", "the 7.6e14 Gram condition number",
     "the sweep files give 2.87e15 to 3.18e15; corrected to 3.0e15"),
    (r"14\s*/\s*474", "the 14/474 ZINB count",
     "the exclusion rule behind the 474 denominator is not a column in "
     "count_diagnostics.csv and cannot be re-derived"),
]
# Phrases rather than numbers: the two readings that were withdrawn as readings.
WITHDRAWN_READINGS = [
    (r"COAD[^.\n]{0,120}same[- ]patient|same[- ]patient[^.\n]{0,120}COAD",
     "the COAD same-patient reading",
     "COAD's shipped patient split does not separate patients, so the term is "
     "not a patient effect"),
    (r"either[^.\n]{0,60}or[^.\n]{0,60}(mostly biology|technical)",
     "the either/or probe-1 interpretation rule",
     "the probe's outcome is not a binary between technical and biological"),
]

# ---------------------------------------------------------------- check 3
# label -> (file, current column, superseded column, note)
# label -> (file, current column, superseded column, note, line-context regex)
# The context regex is load-bearing. Matching a 2-decimal token anywhere in the
# document reported "0.42", "0.13", "0.15" and "0.01" as build evidence when they
# were unrelated numbers on unrelated slides -- a check that fires on everything
# identifies nothing. A match now counts only on a line that discusses the
# quantity itself.
VERSIONED = {
    "theta1 per IDC slide": (
        "results/round2/R6_variance/r6_theta_build_comparison.csv",
        "v2_theta1_raw", "v1_theta1_raw",
        "morphology_v2 is the current build; v1 is round 1's",
        r"theta|GATA3|nuclear area"),
}
COHORTS = {
    "Spearman(width, score), raw head": (
        "results/round2/R8_raw_heads/r8_width_correlations.csv",
        12, 11, "n_encoders"),
}


def read(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    import csv
    with open(p) as f:
        return list(csv.DictReader(f))


md = open(os.path.join(ROOT, DOC), errors="replace").read()
problems, notes = [], []

# A withdrawn quantity may legitimately appear in a sentence that RETRACTS it --
# "round 1 reported 14/474, but the exclusion rule cannot be re-derived" is the
# correct way to carry a withdrawn number, and flagging it would push the
# document towards deleting the record instead of keeping it. A match on a line
# carrying one of these markers is reported as a retraction, not a problem.
RETRACTION = re.compile(
    r"withdraw|retract|cannot be re-derived|should not be quoted|no longer|"
    r"previously|not reported as|is not an? |superseded|round 1 reported|"
    r"corrected to|in place of", re.I)

print(f"=== check 1: withdrawn quantities in {DOC}")
hits1 = retracted = 0
doc_lines = md.split("\n")
for pat, what, why in WITHDRAWN + WITHDRAWN_READINGS:
    for m in re.finditer(pat, md, re.I):
        line = md[:m.start()].count("\n") + 1
        text = doc_lines[line - 1]
        ctx = re.sub(r"\s+", " ", md[max(0, m.start() - 90):m.start() + 90])
        if RETRACTION.search(text):
            print(f"  ok L{line}: {what} appears, but the line retracts it")
            retracted += 1
            continue
        problems.append(f"{DOC}:{line} quotes {what} -- {why}")
        print(f"  FOUND L{line}: {what}")
        print(f"     ...{ctx}...")
        hits1 += 1
print(f"  {hits1} quoted as current, {retracted} appearing inside a retraction")

print(f"\n=== check 2: claims that resolve ONLY against a retired file")
V = os.path.join(ROOT, "code/scripts/verify_numeric_claims.py")
base = ["--search-dir", ".", "--exceptions", "docs/.verify-exceptions-deck",
        "--always", "results/summary/deck_numbers.csv"]


def sweep(extra):
    r = subprocess.run([sys.executable, V, DOC, *base, *extra],
                       cwd=ROOT, capture_output=True, text=True)
    m = re.search(r"(\d+) claims, (\d+) verified, (\d+) not found, (\d+) uncited",
                  r.stdout)
    return tuple(map(int, m.groups())) if m else None


with_sup = sweep([])
without_sup = sweep(["--exclude-dir", "superseded"])
print(f"  including superseded/: {with_sup}")
print(f"  excluding superseded/: {without_sup}")
if with_sup and without_sup:
    if without_sup[2] > with_sup[2] or without_sup[3] > with_sup[3]:
        problems.append(
            f"{DOC}: {without_sup[2] - with_sup[2]} claims became unresolved and "
            f"{without_sup[3] - with_sup[3]} became uncited once superseded/ was "
            f"excluded -- those were matching retired files")
        print("  PROBLEM: some claims were resolving only against retired files")
    else:
        print("  no claim depends on a retired file")

print(f"\n=== check 3: versioned builds -- which one does the document quote?")
for label, (rel, cur_col, old_col, note, ctx) in VERSIONED.items():
    rows = read(rel)
    if rows is None:
        notes.append(f"{rel} absent; {label} not checked")
        continue
    lines = md.split("\n")
    relevant = [(i + 1, l) for i, l in enumerate(lines) if re.search(ctx, l, re.I)]
    if not relevant:
        notes.append(f"{label}: no line in {DOC} discusses it; not checked")
        continue
    for row in rows:
        cur, old = row.get(cur_col), row.get(old_col)
        if not cur or not old:
            continue
        sid = row.get("sample_id", "?")
        for dec in (2, 3, 4):
            tc, to = f"{float(cur):.{dec}f}", f"{float(old):.{dec}f}"
            if tc == to:
                continue          # the builds agree at this precision; uninformative
            for ln, l in relevant:
                if to in l and tc not in l:
                    msg = (f"{label} ({sid}): line quotes {to}, the SUPERSEDED "
                           f"value; the current build gives {tc} ({note})")
                    print(f"  L{ln}: {msg}")
                    problems.append(f"{DOC}:{ln} {msg}")
                elif tc in l:
                    print(f"  L{ln}: {label} ({sid}) quotes {tc}, the current value")
for label, (rel, cur_n, old_n, col) in COHORTS.items():
    rows = read(rel)
    if rows is None:
        notes.append(f"{rel} absent; {label} not checked")
        continue
    for row in rows:
        n = row.get(col)
        print(f"  {label}: cohort n={n} -> "
              + ", ".join(f"{k}={v}" for k, v in row.items() if k != col))

print("\n" + "=" * 62)
if problems:
    print(f"{len(problems)} PROBLEM(S):")
    for p in problems:
        print(f"  - {p}")
else:
    print("no stale quotation found by these three checks")
for n in notes:
    print(f"  note: {n}")
sys.exit(1 if problems else 0)
