#!/usr/bin/env python
"""Verify that every numeric claim in a markdown document appears in the file it cites.

Why this exists. The most recurrent defect in round 2 was a number typed from memory into
a sentence whose *citation* was accurate -- the file named was the right file, the value
beside it was not in that file. Review caught it twice (the COAD decomposition terms in the
authors' draft; two gene-set predictability values in an escalation message). Both times the
prose read as though it had been checked, because the citation had been. This script checks
the other half.

What it does. For each claim scope in the document -- a paragraph, a list item, or a single
table row -- it collects the file paths cited in that scope, or inherited from the nearest
preceding scope in the same section, extracts the numeric claims in the scope, loads each
cited file, and reports any claimed value it cannot find.

A claimed value counts as found when it matches, at the document's own precision:
  * a literal value in the file (`literal`), or
  * a simple aggregate of one numeric column -- mean, median, min, max, sum, std
    (`agg:<column>:<stat>`).
The aggregate rule matters because documents legitimately quote "mean 0.376" for a value
that is nowhere in the file as a cell.

Matching is precision-aware in the direction that actually occurs: a document writes fewer
decimals than the source carries, so 0.376 matches a stored 0.37610. The reverse -- more
decimals in the document than the file has -- does not match, which is correct.

WHAT THIS DOES NOT CHECK, and it is the more dangerous half:
  * that the cited file is the RIGHT file for the claim. A value can exist in the cited
    file and still be the wrong quantity. The second review finding of round 2 turned on
    exactly this, and no script settles it -- it is a judgement about meaning.
  * prose claims with no number ("the largest of any task").
  * numbers in fenced code blocks and inline code spans, which are skipped as quoted
    material rather than claims.

Usage
  python verify_numeric_claims.py DOC.md [DOC2.md ...] [--search-dir DIR]... [--tsv OUT]
  # or in a kernel, passing a resolver that can reach an artifact store:
  #   from verify_numeric_claims import verify
  #   verify("report.md", resolver=my_resolver)

Exit status is 1 if any claim is unresolved, so it can gate a handover.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys

# --------------------------------------------------------------------------- number parsing

# Signed decimals and comma-grouped integers, with an optional trailing percent sign.
# Unicode minus and en-dash are both used as minus signs in these documents.
NUM_RE = re.compile(r"(?<![\w.])([+\-\u2212\u2013]?\d{1,3}(?:,\d{3})+|[+\-\u2212\u2013]?\d*\.\d+|"
                    r"[+\-\u2212\u2013]?\d+)(%?)")

# Contexts where a number is not a data claim.
SKIP_BEFORE = re.compile(
    r"(§|Section|section|Table|table|Figure|figure|Fig\.|issue|Issue|#|item|Item|step|Step|"
    r"round|Round|v|V|[Dd]irectives?|[Mm]emos?|[Dd]ecisions?|[Pp]robes?|[Ll]imitations?|"
    r"[Ss]tages?|and|,|HTTP|HTTP Error|code|"
    r"[Pp]roperty|[Pp]hase|R)\s*$")
# Stage and directive identifiers written bare in a table cell or at the start of a line:
# "| 2.7 IDC confusion |", "2.3 asks for ...". They look like data and are not.
SKIP_BARE_REF = re.compile(r"^\s*\|?\s*\d\.\d+\s")
# A bare four-digit number in 1900-2100 is read as a calendar year rather than a
# measurement, UNLESS a unit or countable noun follows it. Enumerating venues and
# month names was tried first and kept missing cases ("Nat Methods 2026", "Jan
# 2026"); the range test with a unit guard is both shorter and harder to evade.
# Counts of that magnitude are comma-grouped in these documents ("1,229 samples",
# "2,195 spots"), so they are matched by a different branch of NUM_RE and are
# unaffected.
YEAR_RE = re.compile(r"^(19|20)\d{2}$")
YEAR_UNIT_AFTER = re.compile(
    r"^\s*(spots?|genes?|cells?|samples?|slides?|rows?|folds?|patients?|donors?|"
    r"dimensions?|\u00b5m|um|px|pixels?|GB|MB|encoders?|pairs?|%)\b")

SKIP_TOKEN = re.compile(r"""
      \d{4}-\d{2}-\d{2}            # dates
    | v?\d+\.\d+\.\d+              # version strings
    | \d+e[+\-]?\d+                # scientific thresholds such as 1e-3
    | [A-Za-z]+\d+                 # identifiers such as TENX95, NCBI785, INT23
""", re.X)


def _norm_minus(s: str) -> str:
    return s.replace("\u2212", "-").replace("\u2013", "-")


def numbers_in(text: str):
    """Yield (value, decimals, is_percent, raw) for each numeric claim in `text`."""
    bare_ref = SKIP_BARE_REF.match(text)
    for m in NUM_RE.finditer(text):
        raw, pct = m.group(1), m.group(2) == "%"
        if bare_ref and m.start() < bare_ref.end():
            continue
        before = text[max(0, m.start() - 12):m.start()]
        after = text[m.end():m.end() + 6]
        if SKIP_BEFORE.search(before):
            continue
        # identifier or date or version that the number is embedded in
        window = text[max(0, m.start() - 8):m.end() + 8]
        if any(t.start() <= (m.start() - max(0, m.start() - 8)) < t.end()
               for t in SKIP_TOKEN.finditer(window)):
            continue
        if re.match(r"^\s*(?:st|nd|rd|th)\b", after):      # ordinals: 7th of 12
            continue
        # A calendar year, recognised by what precedes it: a month name, a venue,
        # "as of", or a day number. Bare four-digit numbers elsewhere are left
        # alone, so a genuine count of 1229 samples is still checked.
        # `after` is only six characters, too short for " samples"; the year test
        # needs its own wider lookahead.
        if YEAR_RE.match(raw) and not YEAR_UNIT_AFTER.match(text[m.end():m.end() + 16]):
            continue
        # The upper end of an identifier range ("TENX153-156") is part of the identifier,
        # not a measurement. Only treat a post-dash number as a claim when what precedes
        # the dash is itself numeric.
        pre = text[max(0, m.start() - 24):m.start()]
        if re.search(r"[A-Za-z]+\d+\s*[\-\u2013\u2212]\s*$", pre):
            continue
        # Hyphenated names carrying a number: PCA-256, H-optimus-1, float-64. The number
        # names the thing rather than measuring it.
        if re.search(r"[A-Za-z]-$", pre):
            continue
        # A parenthesised section reference after a label: "**Rank supplement (2.6).**"
        if re.match(r"^\(\d\.\d\)", text[m.start() - 1:m.end() + 1]) or \
           (pre.endswith("(") and re.match(r"^\d\.\d\)", raw + after)):
            continue
        # Magnitude suffixes: "130M-row", "8.8 GB" is a claim but "130M" is prose scale.
        if re.match(r"^M\b", after):
            continue
        body = _norm_minus(raw).replace(",", "")
        try:
            val = float(body)
        except ValueError:
            continue
        dec = len(body.split(".")[1]) if "." in body else 0
        # Four-digit years in a citation ("Janesick et al. 2023").
        if dec == 0 and 1900 <= val <= 2100 and re.search(r"(al\.|et al|\(|,)\s*$", pre):
            continue
        # Bare small integers are overwhelmingly counts of things named in the sentence,
        # enumeration, or prose ("two donors"); they generate noise without catching errors.
        if dec == 0 and not pct and abs(val) < 100 and "," not in raw:
            continue
        yield val, dec, pct, raw


# --------------------------------------------------------------------------- file values

def _flatten_json(o, out):
    if isinstance(o, dict):
        for v in o.values():
            _flatten_json(v, out)
    elif isinstance(o, (list, tuple)):
        for v in o:
            _flatten_json(v, out)
    elif isinstance(o, bool):
        pass
    elif isinstance(o, (int, float)) and math.isfinite(o):
        out.append(("literal", float(o)))


def file_values(path: str):
    """Return [(provenance, value)] for every number the file asserts.

    Provenance is 'literal' for a stored value, or 'agg:<column>:<stat>' for a simple
    column aggregate, so a report can say how a claim was satisfied.
    """
    ext = os.path.splitext(path)[1].lower()
    vals = []
    if ext in (".csv", ".tsv", ".parquet"):
        import pandas as pd
        df = (pd.read_parquet(path) if ext == ".parquet"
              else pd.read_csv(path, sep="\t" if ext == ".tsv" else ","))
        for col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce").dropna()
            if s.empty:
                continue
            vals += [("literal", float(v)) for v in s.to_numpy()]
            for stat in ("mean", "median", "min", "max", "sum", "std"):
                try:
                    a = getattr(s, stat)()
                except Exception:
                    continue
                if a is not None and math.isfinite(float(a)):
                    vals.append((f"agg:{col}:{stat}", float(a)))
            # Group-wise aggregates over low-cardinality key columns. Documents very often
            # quote "mean over the three encoders for probe X", which is a mean of a few
            # rows and is nowhere in the file as a cell or as a whole-column statistic.
            # Restricted to keys with few levels so this stays bounded.
            for key in df.columns:
                if key == col:
                    continue
                try:
                    lv = df[key].nunique(dropna=True)
                except Exception:
                    continue
                if not (1 < lv <= 12) or pd.api.types.is_numeric_dtype(df[key]):
                    continue
                try:
                    g = s.groupby(df[key].loc[s.index])
                except Exception:
                    continue
                for stat in ("mean", "median", "min", "max"):
                    try:
                        agg = getattr(g, stat)()
                    except Exception:
                        continue
                    for lvl, a in agg.items():
                        if a is not None and math.isfinite(float(a)):
                            vals.append((f"agg:{col}:{stat}[{key}={lvl}]", float(a)))
        # Text cells carry numbers too -- note and detail columns routinely hold a range
        # or a parenthetical figure that the prose then quotes.
        for col in df.columns:
            for cell in df[col].astype(str).unique():
                for mm in re.finditer(r"[+\-\u2212]?\d*\.?\d+(?:[eE][+\-]?\d+)?", cell):
                    try:
                        vals.append((f"text:{col}", float(_norm_minus(mm.group()))))
                    except ValueError:
                        pass
        # index labels are sometimes the quantity (e.g. a task-indexed summary)
        for v in getattr(df.index, "to_numpy", lambda: [])():
            if isinstance(v, (int, float)) and math.isfinite(float(v)):
                vals.append(("literal", float(v)))
    elif ext == ".parquet0":
        pass
    elif ext == ".json":
        _flatten_json(json.load(open(path)), vals)
    else:
        txt = open(path, errors="replace").read()
        for m in re.finditer(r"[+\-\u2212]?\d*\.?\d+(?:[eE][+\-]?\d+)?", txt):
            try:
                vals.append(("literal", float(_norm_minus(m.group()))))
            except ValueError:
                pass
    return vals


def matches(claim: float, dec: int, pct: bool, vals):
    """Return the provenance of the first file value matching the claim, else None.

    A claim is compared at its own written precision, so a document rounding 0.37610 to
    0.376 matches. Percentages are additionally compared against the proportion.
    """
    tol = 0.5 * (10 ** -dec) * 1.000001
    for prov, v in vals:
        if abs(v - claim) <= tol:
            return prov
        # A percentage may be stored as a proportion. Compare on the PERCENT scale, at the
        # claim's own precision -- comparing claim/100 against v with a percent-scale
        # tolerance would give "54%" a window of +-0.5 in proportion units, which matches
        # almost any stored value. That false pass is exactly what this check exists to
        # avoid, so the comparison is always done in the units the claim is written in.
        if pct and abs(v * 100.0 - claim) <= tol:
            return prov
    return None


# --------------------------------------------------------------------------- document parsing

CODE_FENCE = re.compile(r"^```")
INLINE_CODE = re.compile(r"`([^`]*)`")
# {{artifact:UUID}} embeds are plumbing; their hex groups parse as numbers.
ARTIFACT_MARKER = re.compile(r"\{\{[^}]*\}\}")
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
PATHLIKE = re.compile(r"[\w./\-]+\.(?:csv|tsv|parquet|json|md|txt|png|yaml|yml|py)")


def scopes(md: str):
    """Split a document into claim scopes: table rows, list items, and paragraphs.

    Each scope is (line_no, text, cited_paths). A scope with no citation of its own
    inherits the most recent citation seen earlier in the same '##' section, which is how
    these reports are written -- files named once at the top of a section.
    """
    out, buf, start, inherited, in_fence = [], [], 1, [], False

    def flush(end_line):
        nonlocal buf, start
        if buf:
            text = "\n".join(buf).strip()
            if text:
                out.append([start, text])
            buf = []
        start = end_line + 1

    lines = md.split("\n")
    for n, line in enumerate(lines, 1):
        if CODE_FENCE.match(line.strip()):
            in_fence = not in_fence
            flush(n)
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if not stripped:
            flush(n)
        elif stripped.startswith("|") or re.match(r"^([-*+]|\d+\.)\s", stripped):
            flush(n - 1)                     # each row / item is its own scope
            out.append([n, stripped])
            start = n + 1
        elif stripped.startswith("#"):
            flush(n)
            out.append([n, stripped])
            start = n + 1
        else:
            if not buf:
                start = n
            buf.append(line)
    flush(len(lines))

    # Citations are pooled over the enclosing subsection rather than inherited forward from
    # the last one seen. Forward inheritance was tried first and is wrong for these
    # documents: a file named at the top of a section was carried across every later
    # paragraph, so values whose real source is named further down were checked against an
    # unrelated file and flagged. Pooling by subsection asks the question that matters --
    # is this number in ANY file this subsection cites -- and removed most false positives
    # without weakening the check, since a value absent from all of them still flags.
    def own_cites(text):
        cites = []
        for m in MD_LINK.finditer(text):
            if PATHLIKE.search(m.group(1)):
                cites.append(m.group(1))
        for m in INLINE_CODE.finditer(text):
            cites += PATHLIKE.findall(m.group(1))
        cites += PATHLIKE.findall(text)
        return [c for c in dict.fromkeys(cites)
                if not c.endswith((".png", ".py", ".yaml", ".yml"))]

    groups, cur = [], []
    for ln, text in out:
        if re.match(r"^#{2,3} ", text):
            if cur:
                groups.append(cur)
            cur = []
        cur.append((ln, text))
    if cur:
        groups.append(cur)

    resolved = []
    for g in groups:
        pool = []
        for _, text in g:
            for c in own_cites(text):
                if c not in pool:
                    pool.append(c)
        for ln, text in g:
            resolved.append((ln, text, list(pool) + list(ALWAYS)))
    return resolved


def strip_code(text: str) -> str:
    """Remove inline code spans and artifact markers -- quoted material, not claims."""
    return ARTIFACT_MARKER.sub(" ", INLINE_CODE.sub(" ", text))


# --------------------------------------------------------------------------- resolution

SKIP_DIRS = {".git", "env", "miniforge3", "node_modules", "__pycache__", ".venv",
             "site-packages", "embeddings", "bench_data"}


def make_resolver(search_dirs, max_files=400000):
    """Resolve a cited path against the tree, by exact path first then by basename.

    Documents in this repository cite files by bare name (`r3_per_task_terms.csv`) while
    the files live several directories down (`results/round2/R7_pergene/...`). A
    non-recursive lookup reports those as uncited, which silently converts a real check
    into no check at all -- the failure mode this script exists to prevent. So the tree is
    indexed once by basename. Where a basename is ambiguous, every match is returned and
    the claim is checked against all of them, with the ambiguity reported.
    """
    index = {}
    n = 0
    for d in search_dirs:
        for root, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".")]
            for f in files:
                if os.path.splitext(f)[1].lower() in (".csv", ".tsv", ".parquet", ".json"):
                    index.setdefault(f, []).append(os.path.join(root, f))
                    n += 1
                    if n > max_files:
                        break

    def resolve(path):
        for c in (path, os.path.basename(path)):
            if os.path.isfile(c):
                return [c]
        for d in search_dirs:
            p = os.path.join(d, path)
            if os.path.isfile(p):
                return [p]
        return index.get(os.path.basename(path), [])
    return resolve


def load_exceptions(path):
    """Values that are legitimately not in any cited file, each with a written reason.

    Format: one 'value<TAB>reason' per line, '#' comments ignored. This exists so that a
    derived quantity (a ratio of two files' values, a simulation ground truth, a p-value,
    a figure from an external source) passes by DECLARATION rather than by the checker
    being loosened. Every number in a handover document is then either present in a cited
    file or has a recorded reason why not -- which is the property worth having.
    """
    ex = {}
    if path and os.path.isfile(path):
        for line in open(path):
            line = line.split("#")[0].strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                ex[parts[0].strip()] = parts[1].strip()
    return ex


def verify(doc, resolver, verbose=False, exceptions=None):
    """Verify one document. Returns (rows, stats)."""
    exceptions = exceptions or {}
    md = open(doc, errors="replace").read()
    rows, cache, seen_missing = [], {}, set()
    n_claims = n_ok = 0
    for ln, text, cites in scopes(doc and md):
        body = strip_code(text)
        claims = list(numbers_in(body))
        if not claims:
            continue
        vals, used = [], []
        for c in cites:
            if c not in cache:
                paths = resolver(c)
                try:
                    vv = []
                    for p in paths:
                        vv += file_values(p)
                    cache[c] = vv if paths else None
                except Exception as e:
                    cache[c] = None
                    if c not in seen_missing:
                        seen_missing.add(c)
                        rows.append(dict(doc=doc, line=ln, value="", status="unreadable",
                                         cited=c, detail=f"{type(e).__name__}: {e}"[:90],
                                         context=""))
            if cache[c] is not None:
                vals += cache[c]
                used.append(c)
        for val, dec, pct, raw in claims:
            n_claims += 1
            if not used:
                rows.append(dict(doc=doc, line=ln, value=raw, status="uncited", cited="",
                                 detail="no readable file cited in scope or section",
                                 context=body[:110].replace("\n", " ")))
                continue
            prov = matches(val, dec, pct, vals)
            if not prov and raw in exceptions:
                prov = f"declared: {exceptions[raw]}"
            if prov:
                n_ok += 1
                if verbose:
                    rows.append(dict(doc=doc, line=ln, value=raw, status="ok",
                                     cited=",".join(used), detail=prov, context=""))
            else:
                rows.append(dict(doc=doc, line=ln, value=raw, status="NOT FOUND",
                                 cited=",".join(used), detail="",
                                 context=body[:110].replace("\n", " ")))
    return rows, dict(doc=doc, claims=n_claims, ok=n_ok)


ALWAYS = []


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("docs", nargs="+")
    ap.add_argument("--search-dir", action="append", default=["."])
    ap.add_argument("--tsv")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--exceptions", default=".verify-exceptions")
    # A file consulted for EVERY claim, regardless of what the enclosing
    # subsection cites. This exists for a single-source-of-truth table such as
    # results/summary/deck_numbers.csv: the document quotes its numbers in prose
    # without citing it line by line, so without this the table is invisible to
    # the sweep and 30 checkable claims read as uncited.
    ap.add_argument("--always", action="append", default=[])
    a = ap.parse_args()
    global ALWAYS
    ALWAYS = list(a.always)
    resolver = make_resolver(a.search_dir)
    ex = load_exceptions(a.exceptions)
    allrows, stats = [], []
    for d in a.docs:
        r, s = verify(d, resolver, a.verbose, ex)
        allrows += r
        stats.append(s)
    bad = [r for r in allrows if r["status"] in ("NOT FOUND", "unreadable")]
    for s in stats:
        n = sum(1 for r in allrows if r["doc"] == s["doc"] and r["status"] == "NOT FOUND")
        print(f"{s['doc']}: {s['claims']} claims, {s['ok']} verified, {n} not found, "
              f"{sum(1 for r in allrows if r['doc']==s['doc'] and r['status']=='uncited')} uncited")
    for r in bad:
        print(f"  [{r['status']}] {r['doc']}:{r['line']}  {r['value']}  "
              f"cited={r['cited']}  {r['detail']}\n      {r['context']}")
    if a.tsv:
        import csv
        with open(a.tsv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["doc", "line", "value", "status", "cited",
                                              "detail", "context"], delimiter="\t")
            w.writeheader()
            w.writerows(allrows)
        print(f"\nwrote {a.tsv} ({len(allrows)} rows)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
