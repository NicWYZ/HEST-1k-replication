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

Stage: closeout repository refresh and the post-deck numeric-claim gate
(deck_figures_and_repo_update.md section 2.6; post_deck_repo_instructions.md
sections 1 and 2).
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
# Resource caps, set from what actually failed rather than guessed: a 32 GB job was
# OOM-killed reading a cited per-spot parquet.
SKIP_WINDOW = 48          # wider than the longest skippable token (a 36-char UUID)
# One citation's expansion is bounded by TOTAL BYTES, not by file count. Count is the
# wrong unit: `results.json` resolves by basename to 2150 per-split files of a few
# kilobytes each, trivial to read in full, while `preds__<encoder>.parquet` resolves to
# a dozen files of hundreds of megabytes, which is not. Smallest first, so summary
# tables -- where a quoted value almost always lives -- are always reached.
FAMILY_BYTES = 256 * 1024 * 1024
FAMILY_CAP = 4000                # a hard ceiling on file count as well
MAX_READ_BYTES = 200 * 1024 * 1024
MAX_CELLS = 3_000_000

# Scientific notation is matched as ONE token. Without the exponent alternative,
# "3.15e-02" parsed as two claims, 3.15 and 02, and every acceptance-threshold table
# in a stage report became a page of false unresolved entries -- which is most of why
# round2_R0_R1_stage_report.md showed 224.
_SIGN = r"[+\-\u2212\u2013]?"
_EXP = r"(?:[eE]" + _SIGN + r"\d+)?"
NUM_RE = re.compile(
    r"(?<![\w.])(" + _SIGN + r"\d{1,3}(?:,\d{3})+|"
    + _SIGN + r"\d*\.\d+" + _EXP + r"|"
    + _SIGN + r"\d+" + _EXP + r")(%?)")

# Note on the scientific-notation branch above, which is load-bearing now that NUM_RE
# reads exponents. A bare-integer mantissa (1e-6, 5e-04) is, in these documents, always
# an acceptance THRESHOLD the document itself specifies -- it exists in no results file
# and checking it would be a guaranteed false unresolved. A mantissa with significant
# digits (3.15e-02, 1.265e-05) is a MEASURED value that should be in a results file and
# is checked. The distinction is really role, not shape, but the shape is a reliable
# proxy here: thresholds are round powers and measurements are not.

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
      10\.\d{4,9}/[^\s)\]]+        # DOIs: 10.1038/s41467-023-43458-x parses as 10.1038 and 43458
    | (?:GSE|GSM|SRR|SRP|PRJNA|SAMN|E-MTAB)[-\d]+   # database accessions
    | arXiv:\s*\d{4}\.\d{4,5}     # arXiv ids
    | \d+\s*:\s*\d+(?:\s*[\-\u2013\u2212]\s*\d+)?  # journal volume:page, or a
                                   # volume:start-end page range ("PNAS 117:30266",
                                   # "Nature Methods 23:1447-1457") -- a citation, not a
                                   # measurement. Without the optional range tail, the END
                                   # page of a hyphenated range (the 1457 in 23:1447-1457)
                                   # was left unprotected and scanned as its own claim.
    | \d{4}-\d{2}-\d{2}            # dates
    | v?\d+\.\d+\.\d+              # version strings
    | \d+e[+\-]?\d+                # see note below: 1e-6 is a threshold, 3.15e-02 is not
    | [0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}
                                   # UUIDs: an artifact id in a plain markdown image link,
                                   # ![cap](art_5d580e1c-1647-4142-ac6f-...), put the digit
                                   # run 4142 in front of the scanner. The {{artifact:...}}
                                   # marker form was already stripped; this covers the rest,
                                   # and a UUID is an identifier by definition.
    | [A-Za-z]+\d+                 # identifiers such as TENX95, NCBI785, INT23
""", re.X)


def _norm_minus(s: str) -> str:
    return s.replace("\u2212", "-").replace("\u2013", "-")


# Scientific notation written for a human reader rather than for a parser:
# "5.4 x 10^-6", "5.4 * 10^-6", "5.4 \u00d7 10^-6". These appear in prose where an "e"
# form would read badly, and without this the mantissa alone was taken as the claim --
# 5.4 compared against a stored 5.4e-06, which cannot match.
PROSE_SCI = re.compile(
    r"([+\-\u2212\u2013]?\d*\.?\d+)\s*[x\u00d7*]\s*10\s*\^?\s*"
    r"([+\-\u2212\u2013]?\d+)")


def _rewrite_prose_sci(text: str) -> str:
    """Rewrite prose scientific notation into the e-form the scanner understands."""
    return PROSE_SCI.sub(
        lambda m: f"{m.group(1)}e{_norm_minus(m.group(2))}", text)


def parse_claim(raw):
    """(value, decimals, is_percent) for a single written number, or None.

    This is the precision rule on its own, WITHOUT the context rules that decide whether a
    number in prose is a claim at all. numbers_in() applies both, which is right when
    scanning a document and wrong when parsing an entry KEY: a key of "54" or "20" carries
    no surrounding sentence, so the context rules reject it and a legitimate entry reads as
    unparseable. Both callers share this function so "how precise is this number" has one
    answer.
    """
    txt = _norm_minus(str(raw)).strip()
    pct = txt.endswith("%")
    body = txt.rstrip("%").replace(",", "").strip()
    try:
        val = float(body)
    except ValueError:
        return None
    m = re.match(r"^[+\-]?(\d*)(?:\.(\d+))?(?:[eE]([+\-]?\d+))?$", body)
    if not m:
        return None
    dec = len(m.group(2) or "")
    if m.group(3):
        # 3.15e-02 is known to 1e-4, not to the mantissa's 1e-2: the exponent shifts the
        # precision with the value, and ignoring it gives a tolerance far wider than the
        # number's own precision.
        dec -= int(m.group(3))
    return val, dec, pct


def numbers_in(text: str):
    """Yield (value, decimals, is_percent, raw) for each numeric claim in `text`."""
    text = _rewrite_prose_sci(text)
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
        # The window has to be wider than the longest skippable token, or the test
        # silently never fires for long ones: a UUID is 36 characters, so at +-8 the
        # pattern could not match around a digit run in its middle. Widening is safe
        # because the test still requires the CLAIM's position to fall inside the
        # matched token's span, so an unrelated identifier elsewhere on the line cannot
        # swallow a real claim.
        lo = max(0, m.start() - SKIP_WINDOW)
        window = text[lo:m.end() + SKIP_WINDOW]
        if any(t.start() <= (m.start() - lo) < t.end()
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
        parsed = parse_claim(raw)
        if parsed is None:
            continue
        val, dec, _pct_unused = parsed
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


class FileValues:
    """The numbers a file asserts, in a form whose size does not track the file's.

    The previous representation was a Python list of (provenance, value) tuples with
    one entry per CELL, plus one per number inside every text cell. For a per-spot
    table that is tens of millions of tuples at roughly 70 bytes each, which is what
    OOM-killed the sweep at 4, 24, 32 and 64 GB -- the read was never the problem, the
    materialisation was. Three changes make the footprint bounded instead:

      * literals are DEDUPLICATED into one sorted float64 array and matched by binary
        search. Every literal carried the same provenance string anyway, so nothing is
        lost, and claims are compared at 2-4 decimals where a large table has orders of
        magnitude fewer distinct values than rows.
      * aggregates keep their provenance but are bounded by columns x statistics x
        group levels, not by rows.
      * a large file is read in CHUNKS, so the DataFrame never fully materialises
        either.

    `notes` records anything that could not be computed, so a claim that would only
    have matched a skipped statistic comes back unresolved WITH the reason rather than
    silently passing or silently failing.
    """

    __slots__ = ("lit", "tagged", "notes")

    def __init__(self):
        self.lit = None          # np.ndarray, sorted, unique
        self.tagged = []         # [(provenance, value)]
        self.notes = []          # [str]

    def set_literals(self, arr):
        import numpy as np
        a = np.asarray(sorted(set(float(x) for x in arr if math.isfinite(float(x)))),
                       dtype="float64")
        self.lit = a

    def near(self, x, tol):
        """True if any literal is within tol of x. Binary search, not a scan."""
        import numpy as np
        if self.lit is None or not self.lit.size:
            return False
        k = int(np.searchsorted(self.lit, x))
        for idx in (k - 1, k):
            if 0 <= idx < self.lit.size and abs(self.lit[idx] - x) <= tol:
                return True
        return False

    def __bool__(self):
        return bool((self.lit is not None and self.lit.size) or self.tagged)


# Above this many rows a CSV is read in chunks and the statistics that need every
# value in memory at once are not computed. Set from the failure: the document that
# OOM-killed at 64 GB cites tables of a few million rows.
CHUNK_ROWS = 400_000
CHUNK_SIZE = 200_000


def _numeric_cols(df):
    import pandas as pd
    out = {}
    for col in df.columns:
        v = pd.to_numeric(df[col], errors="coerce").dropna()
        if not v.empty:
            out[col] = v
    return out


def _small_file_values(df, fv):
    """Full-precision path for a table small enough to hold: every statistic."""
    import pandas as pd
    lits = []
    cols = _numeric_cols(df)
    big = df.shape[0] * max(1, df.shape[1]) > MAX_CELLS
    for col, v in cols.items():
        lits.append(v.to_numpy())
        for stat in ("mean", "median", "min", "max", "sum", "std"):
            try:
                a = getattr(v, stat)()
            except Exception:
                continue
            if a is not None and math.isfinite(float(a)):
                fv.tagged.append((f"agg:{col}:{stat}", float(a)))
        if big:
            continue
        # Group-wise aggregates over low-cardinality key columns. Documents very
        # often quote "mean over the three encoders for probe X", which is a mean of
        # a few rows and is nowhere in the file as a cell or a whole-column statistic.
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
                g = v.groupby(df[key].loc[v.index])
            except Exception:
                continue
            for stat in ("mean", "median", "min", "max"):
                try:
                    agg = getattr(g, stat)()
                except Exception:
                    continue
                for lvl, a in agg.items():
                    if a is not None and math.isfinite(float(a)):
                        fv.tagged.append(
                            (f"agg:{col}:{stat}[{key}={lvl}]", float(a)))
    # Text cells carry numbers too -- note and detail columns routinely hold a range
    # or a parenthetical figure that the prose then quotes. Unique cells only.
    for col in df.columns:
        if col in cols:          # numeric: already captured as literals
            continue
        try:
            uniq = df[col].astype(str).unique()
        except Exception:
            continue
        for cell in uniq:
            for mm in re.finditer(r"[+\-\u2212]?\d*\.?\d+(?:[eE][+\-]?\d+)?", cell):
                try:
                    fv.tagged.append((f"text:{col}", float(_norm_minus(mm.group()))))
                except ValueError:
                    pass
    for v in getattr(df.index, "to_numpy", lambda: [])():
        if isinstance(v, (int, float)) and math.isfinite(float(v)):
            lits.append([float(v)])
    return lits


def _chunked_file_values(path, sep, fv):
    """Streaming path for a large CSV: exact count/sum/min/max, dedup'd literals.

    mean, min and max are exact from running accumulators. median and std are NOT
    computed, because both need every value at once and holding them is the thing
    this path exists to avoid; each is recorded in `notes` so a claim that could only
    have matched one of them is reported unresolved with that reason, never passed.
    """
    import numpy as np
    import pandas as pd

    acc = {}
    uniq = set()
    text_seen = set()
    nrows = 0
    for chunk in pd.read_csv(path, sep=sep, chunksize=CHUNK_SIZE, low_memory=False):
        nrows += len(chunk)
        for col, v in _numeric_cols(chunk).items():
            a = acc.setdefault(col, {"n": 0, "s": 0.0, "mn": math.inf, "mx": -math.inf})
            arr = v.to_numpy(dtype="float64")
            a["n"] += arr.size
            a["s"] += float(arr.sum())
            a["mn"] = min(a["mn"], float(arr.min()))
            a["mx"] = max(a["mx"], float(arr.max()))
            # Round before dedup: claims are compared at 2-6 decimals, so keeping
            # full float64 identity would defeat the deduplication on a column of
            # continuous values.
            uniq.update(np.unique(np.round(arr, 6)).tolist())
        for col in chunk.columns:
            # A numeric column's values are already literals; scanning them as text
            # duplicates them into tagged entries and, on a wide table, is most of
            # what fills the text budget with nothing new.
            if col in acc:
                continue
            try:
                cells = chunk[col].astype(str).unique()
            except Exception:
                continue
            for cell in cells:
                if cell in text_seen or len(text_seen) > 200_000:
                    continue
                text_seen.add(cell)
                for mm in re.finditer(r"[+\-\u2212]?\d*\.?\d+(?:[eE][+\-]?\d+)?", cell):
                    try:
                        fv.tagged.append((f"text:{col}", float(_norm_minus(mm.group()))))
                    except ValueError:
                        pass
    for col, a in acc.items():
        if a["n"]:
            fv.tagged.append((f"agg:{col}:mean", a["s"] / a["n"]))
            fv.tagged.append((f"agg:{col}:min", a["mn"]))
            fv.tagged.append((f"agg:{col}:max", a["mx"]))
            fv.tagged.append((f"agg:{col}:sum", a["s"]))
    fv.notes.append(
        f"read in chunks ({nrows:,} rows): median, std and group-wise aggregates not "
        f"computed, so a claim matching only one of those is reported unresolved")
    fv.set_literals(uniq)
    return fv


# An on-disk cache of the values extracted from each cited file, keyed by path, size and
# mtime. Extraction is the sweep's only expensive step -- a per-gene parquet is hundreds of
# megabytes -- and a document whose claims mostly do NOT match forces every cited file to
# be read, so the largest report could not finish inside an interactive command window at
# all. With the cache the first pass warms whatever it reaches and a repeat pass completes,
# which turns an unrunnable document into a resumable one. The key includes size and mtime,
# so a regenerated file is re-read rather than served stale.
CACHE_DIR = os.environ.get("VERIFY_CACHE", ".verify-cache")


def _cache_key(path):
    try:
        st = os.stat(path)
    except OSError:
        return None
    import hashlib
    h = hashlib.sha1(f"{os.path.abspath(path)}|{st.st_size}|{int(st.st_mtime)}"
                     f"|v2".encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{h}.pkl")


def file_values(path):
    """Cached wrapper around _file_values_uncached."""
    key = _cache_key(path)
    if key and os.path.exists(key):
        import pickle
        try:
            with open(key, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass                      # a damaged cache entry is recomputed, never trusted
    fv = _file_values_uncached(path)
    if key:
        import pickle
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            tmp = key + ".tmp"
            with open(tmp, "wb") as f:
                pickle.dump(fv, f, protocol=4)
            os.replace(tmp, key)      # atomic, so a concurrent reader never sees a partial
        except Exception:
            pass                      # the cache is an optimisation, never a requirement
    return fv


def _file_values_uncached(path: str):
    """Return a FileValues for every number the file asserts.

    No size cap. The closeout version refused to read anything over 200 MB, which the
    instruction correctly calls the sweep's limitation rather than the document's; with
    chunked reading and deduplicated literals the footprint no longer tracks the file
    size, so the cap is gone.
    """
    import numpy as np
    ext = os.path.splitext(path)[1].lower()
    fv = FileValues()
    lits = []
    if ext in (".csv", ".tsv", ".parquet"):
        import pandas as pd
        sep = "\t" if ext == ".tsv" else ","
        if ext == ".parquet":
            df = pd.read_parquet(path)
            if df.shape[0] > CHUNK_ROWS:
                # A parquet is already columnar, so read it column by column rather
                # than expanding the whole frame into per-cell tuples.
                uniq = set()
                for col in df.columns:
                    v = pd.to_numeric(df[col], errors="coerce").dropna()
                    if v.empty:
                        continue
                    arr = v.to_numpy(dtype="float64")
                    uniq.update(np.unique(np.round(arr, 6)).tolist())
                    fv.tagged.append((f"agg:{col}:mean", float(arr.mean())))
                    fv.tagged.append((f"agg:{col}:min", float(arr.min())))
                    fv.tagged.append((f"agg:{col}:max", float(arr.max())))
                    fv.tagged.append((f"agg:{col}:median", float(np.median(arr))))
                    fv.tagged.append((f"agg:{col}:std", float(arr.std(ddof=1))))
                    del arr, v
                fv.notes.append(f"parquet read column-wise ({df.shape[0]:,} rows): "
                                f"group-wise aggregates not computed")
                fv.set_literals(uniq)
                return fv
            lits = _small_file_values(df, fv)
        else:
            try:
                nrows = sum(1 for _ in open(path, errors="replace")) - 1
            except OSError:
                nrows = 0
            if nrows > CHUNK_ROWS:
                return _chunked_file_values(path, sep, fv)
            df = pd.read_csv(path, sep=sep, low_memory=False)
            lits = _small_file_values(df, fv)
    elif ext == ".json":
        tmp = []
        _flatten_json(json.load(open(path)), tmp)
        fv.tagged.extend(tmp)
    else:
        # Comma-grouped integers must be matched as ONE token, before the plain-digit
        # alternative: without this "892,966" in a cited markdown record split into 892
        # and 966, so a document quoting that figure could never resolve against it.
        txt = open(path, errors="replace").read()
        pat = (r"[+\-\u2212]?\d{1,3}(?:,\d{3})+"
               r"|[+\-\u2212]?\d*\.?\d+(?:[eE][+\-\u2212]?\d+)?")
        for m in re.finditer(pat, txt):
            try:
                lits.append([float(_norm_minus(m.group()).replace(",", ""))])
            except ValueError:
                pass
    flat = []
    for chunkarr in lits:
        flat.extend(float(x) for x in chunkarr)
    fv.set_literals(flat)
    return fv


def matches(claim: float, dec: int, pct: bool, fv):
    """Return the provenance of a file value matching the claim, else None.

    A claim is compared at its own written precision, so a document rounding 0.37610
    to 0.376 matches. Percentages are additionally compared against the proportion,
    always on the PERCENT scale -- comparing claim/100 against a stored proportion
    with a percent-scale tolerance would give "54%" a window of +-0.5 in proportion
    units and match almost anything, which is the false pass this check exists to
    prevent.

    `fv` is a FileValues: literals are binary-searched, tagged values scanned. A list
    of (provenance, value) pairs is still accepted so the derived-class evaluator and
    the tests can pass one directly.
    """
    tol = 0.5 * (10 ** -dec) * 1.000001

    def scan(pairs):
        for prov, v in pairs:
            if v is None:
                continue
            if abs(v - claim) <= tol:
                return prov
            if pct and abs(v * 100.0 - claim) <= tol:
                return prov
        return None

    if isinstance(fv, FileValues):
        if fv.near(claim, tol):
            return "literal"
        if pct and fv.near(claim / 100.0, tol / 100.0):
            return "literal(as proportion)"
        return scan(fv.tagged)
    return scan(fv)


# --------------------------------------------------------------------------- document parsing

CODE_FENCE = re.compile(r"^```")
INLINE_CODE = re.compile(r"`([^`]*)`")
# {{artifact:UUID}} embeds are plumbing; their hex groups parse as numbers.
ARTIFACT_MARKER = re.compile(r"\{\{[^}]*\}\}")
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
# `*` and `?` are part of a path here: this repository cites per-encoder families as
# acceptance__*__f64.csv, and a citation the pattern cannot even capture is a citation
# the resolver never sees, so the claim reads as uncited.
# `<encoder>`-style PLACEHOLDERS are part of a path too. These reports cite a per-encoder
# family as acceptance__<encoder>.csv, which parsed as no path at all, so whole blocks of
# claims read as uncited -- a real check silently replaced by none. A placeholder is
# translated to a glob at resolution time, so the citation resolves across the family the
# way the prose means it.
PATHLIKE = re.compile(r"[\w./\-*?<>]+\.(?:csv|tsv|parquet|json|md|txt|png|yaml|yml|py)")
PLACEHOLDER = re.compile(r"<[^<>/]{1,24}>")


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

    # Citation pools are HIERARCHICAL: a scope sees the citations of its own section and
    # of every ANCESTOR section, but not of its siblings.
    #
    # Flat per-section pooling was the first design, and it was too strict in a way that
    # produced most of the false unresolved entries in this repository: a file named once
    # in a "##" section's preamble was invisible to every "###" subsection beneath it,
    # so a report that says "all numbers in this section come from X" and then discusses
    # X in subsections had every one of those numbers flagged. Ancestor inheritance is
    # the document semantics a reader assumes. Sibling inheritance is still refused --
    # that was the original bug, where a file named at the top of one section was carried
    # across later, unrelated paragraphs and values were checked against the wrong file.
    def level_of(text):
        m = re.match(r"^(#{1,6}) ", text)
        return len(m.group(1)) if m else None

    # First pass: each heading's own section gets a pool of the citations appearing in it
    # (heading line included), keyed by the heading's position.
    sections = []            # [(level, own_pool, [(ln, text), ...])]
    cur_level, cur_pool, cur_items = 0, [], []
    for ln, text in out:
        lv = level_of(text)
        if lv is not None:
            sections.append((cur_level, cur_pool, cur_items))
            cur_level, cur_pool, cur_items = lv, [], []
        for c in own_cites(text):
            if c not in cur_pool:
                cur_pool.append(c)
        cur_items.append((ln, text))
    sections.append((cur_level, cur_pool, cur_items))

    # Second pass: walk the sections in order carrying a stack of ancestor pools.
    resolved, stack = [], []          # stack of (level, pool)
    for level, pool, items in sections:
        while stack and stack[-1][0] >= level:
            stack.pop()
        inherited_pool = [c for _, p in stack for c in p]
        effective = list(dict.fromkeys(inherited_pool + pool))
        for ln, text in items:
            resolved.append((ln, text, effective + list(ALWAYS)))
        stack.append((level, pool))
    return resolved


# A URL is an address, and every digit in it is part of that address: a publisher's
# article id (nature.com/articles/s41592-025-02814-z) and an arXiv id both parse as
# numbers otherwise. Handled by REMOVING urls before extraction rather than by a
# skip-token rule, because a skip rule has to find its token inside a fixed window and a
# url is routinely longer than any window worth scanning.
URL = re.compile(r"(?:https?://|www\.|doi\.org/)[^\s)\]>\"']+")


def strip_code(text: str) -> str:
    """Remove inline code spans, artifact markers and urls -- addresses, not claims."""
    return URL.sub(" ", ARTIFACT_MARKER.sub(" ", INLINE_CODE.sub(" ", text)))


# --------------------------------------------------------------------------- resolution

SKIP_DIRS = {".git", "env", "miniforge3", "node_modules", "__pycache__", ".venv",
             "site-packages", "embeddings", "bench_data"}


def make_resolver(search_dirs, max_files=400000, exclude_dirs=()):
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
    # exclude_dirs is how the currency check is run: a claim that resolves ONLY
    # inside superseded/ has matched a retired file, which the plain sweep cannot
    # distinguish from a live match because two of this repository's retired
    # files are byte-level re-writes with identical values.
    for d in search_dirs:
        for root, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".")
                       and x not in exclude_dirs]
            for f in files:
                # .md and .txt are indexed as well, because these documents legitimately
                # cite one another for values whose primary source is external -- a vendor
                # page cell count recorded in r5_idc_provenance.md has no CSV behind it,
                # and the alternative to resolving it is an exception that checks nothing.
                # A document's values are only reachable if a subsection cites it.
                if os.path.splitext(f)[1].lower() in (".csv", ".tsv", ".parquet",
                                                      ".json", ".md", ".txt"):
                    index.setdefault(f, []).append(os.path.join(root, f))
                    n += 1
                    if n > max_files:
                        break

    import fnmatch

    def blocked(p):
        """True if any directory component of p is excluded.

        Applied to the direct-path branches as well as the index, because a
        document cites paths EXPLICITLY -- filtering only the basename index
        would let a cited superseded/ path resolve and defeat the check.
        """
        return bool(exclude_dirs) and any(
            part in exclude_dirs for part in os.path.normpath(p).split(os.sep))

    def resolve(path):
        # acceptance__<encoder>.csv means "any encoder's file", so it becomes a glob.
        if PLACEHOLDER.search(path):
            path = PLACEHOLDER.sub("*", path)
        for c in (path, os.path.basename(path)):
            if os.path.isfile(c) and not blocked(c):
                return [c]
        for d in search_dirs:
            p = os.path.join(d, path)
            if os.path.isfile(p) and not blocked(p):
                return [p]
        # A citation may be a GLOB -- acceptance__*__f64.csv -- which is how this
        # repository refers to a per-encoder family of files. A "worst over 12 encoders"
        # claim legitimately resolves against any of them, and without this the citation
        # matched nothing and the claim read as uncited: a real check turned into none.
        base = os.path.basename(path)
        if any(ch in base for ch in "*?["):
            hits = [p for name, paths in index.items() if fnmatch.fnmatch(name, base)
                    for p in paths if not blocked(p)]
            return sorted(dict.fromkeys(hits))
        return [p for p in index.get(base, []) if not blocked(p)]
    return resolve


# --------------------------------------------------------------------- derived claims

# A reference to a single cell or to a column statistic in a named file.
#   r5c_leak_summary.csv#mean@task=IDC      -> the one cell where task == IDC
#   r3_per_task_terms.csv#novel slide:sum   -> a whole-column statistic
# Three forms, in the order the regex tries them:
#   file#col@key=val          one cell, ambiguity refused
#   file#col:stat@key=val     a statistic over the rows where key=val  <- added after the
#                             R5 triage reported that several report claims are means over
#                             a filtered subset ("mean over the three encoders for PAAD")
#                             and could be expressed neither as a cell nor as a whole
#                             column, which left them unresolvable except by declaration
#   file#col:stat             a whole-column statistic
# A reference is: file # column [:stat] [@key=val ...]
#
# The filter is a CHAIN of one or more @key=val pairs, all of which must hold. A single
# filter was the first design and it silently selected the wrong rows: the patient label
# is not unique across tasks -- "patient 2" appears in PRAD, SKCM and LUNG -- so
# @patient="patient 2" alone spanned 0.172 to 0.688 um/px and a within-patient fold-ratio
# came out 2.55 instead of 1.02. The derived check caught that, which is the whole point
# of evaluating these rather than declaring them; a declared exception would have left the
# wrong reading in place unexamined.
#
# A quoted column name is the only way to reference one containing a hyphen
# (r3_per_task_terms.csv has a column literally named "TOTAL random - patient", and an
# unquoted hyphen is subtraction). A quoted value is the only way to carry whitespace.
_VAL = r'(?:"[^"]+"|[^\s()+\-*/@]+)'
DERIVED_REF = re.compile(
    r"(?P<file>[\w./\-]+\.(?:csv|tsv|parquet))"
    r'#(?:"(?P<colq>[^"]+)"|(?P<col>[^@:\s()+\-*/]+(?: [^@:\s()+\-*/]+)*))'
    r"(?::(?P<stat>mean|median|min|max|sum|std|count|p\d{1,2}))?"
    r"(?P<filters>(?:@[^=\s]+=" + _VAL + r")*)")

FILTER_RE = re.compile(r"@(?P<key>[^=\s]+)=(?:\"(?P<valq>[^\"]+)\"|(?P<val>[^\s()+\-*/@]+))")


def _filters_of(m):
    """[(key, value), ...] for a reference's filter chain, in written order."""
    return [(f.group("key"), f.group("valq") or f.group("val"))
            for f in FILTER_RE.finditer(m.group("filters") or "")]


STATS = ("mean", "median", "min", "max", "sum", "std", "count")
# :p95 and friends. A percentile is a perfectly ordinary summary and a claim
# quoting one was otherwise undeclarable except as an exception.

# Built lazily inside eval_derived so the module imports without ast.
_ALLOWED_NODES = None


class DerivedError(Exception):
    """A derived entry that cannot be evaluated. Never silently a pass."""


def load_derived(path):
    """Parse a derived-claims file into {claim_text: (formula, reason)}.

    Format: claim<TAB>formula<TAB>reason, '#' comments ignored. The claim is matched
    against the literal text as written in the document, exactly as the plain
    exceptions file does, so "54%" and "0.54" are different entries.

    This exists because the largest category of unresolved claim in this repository is
    a quantity the documents compute -- a difference between two terms, a share of a
    gap, a spread across slides -- which is in no file as a cell and which the sweep
    therefore could only ever have passed by declaration. Declaring it proves nothing.
    Evaluating the formula against the cited cells checks the arithmetic the document
    actually did.
    """
    out = {}
    if not (path and os.path.isfile(path)):
        return out
    for raw in open(path):
        # '#' is a comment only at the start of a line -- see load_exceptions.
        if raw.lstrip().startswith("#"):
            continue
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split("\t") if p.strip()]
        if len(parts) < 2:
            continue
        claim, formula = parts[0], parts[1]
        reason = parts[2] if len(parts) > 2 else ""
        out[claim] = (formula, reason)
    return out


def _resolve_ref(m, resolver):
    """Resolve one reference to a float, raising rather than guessing."""
    import pandas as pd
    fname = m.group("file")
    col = m.group("colq") or m.group("col")
    paths = resolver(fname)
    if not paths:
        raise DerivedError(f"file not found: {fname}")
    if len(paths) > 1:
        raise DerivedError(f"ambiguous file {fname}: {len(paths)} matches")
    p = paths[0]
    df = (pd.read_parquet(p) if p.endswith(".parquet")
          else pd.read_csv(p, sep="\t" if p.endswith(".tsv") else ","))
    # A column may be the index rather than a column, which is how several of these
    # summary tables are written.
    if col not in df.columns:
        if df.index.name == col:
            df = df.reset_index()
        else:
            df = df.reset_index()
            if col not in df.columns:
                raise DerivedError(f"no column {col!r} in {fname}")
    series = pd.to_numeric(df[col], errors="coerce")

    # Apply the filter chain. Every pair must hold, which is what makes a within-patient
    # quantity expressible: @task=PRAD@patient="patient 2".
    filters = _filters_of(m)
    for key, val in filters:
        if key not in df.columns:
            raise DerivedError(f"no key column {key!r} in {fname}")
        keep = df[key].astype(str) == val
        if not keep.any():
            raise DerivedError(f"no rows with {key}={val} in {fname}")
        df, series = df[keep], series[keep]

    shown = "".join(f"@{k}={v}" for k, v in filters)
    stat = m.group("stat")
    if stat:
        sel = series.dropna()
        if sel.empty:
            raise DerivedError(f"{fname}#{col}{shown} has no numeric rows")
        if stat == "count":
            v = float(sel.size)
        elif stat.startswith("p"):
            v = float(sel.quantile(int(stat[1:]) / 100.0))
        else:
            v = getattr(sel, stat)()
        if v is None or not math.isfinite(float(v)):
            raise DerivedError(f"{fname}#{col}:{stat}{shown} is not finite")
        return float(v)

    if not filters:
        raise DerivedError(
            f"{fname}#{col} names a whole column with no statistic and no filter; "
            f"add :mean/:sum/... or @key=value")
    sel = series.dropna()
    if sel.empty:
        raise DerivedError(f"no numeric value at {fname}#{col}{shown}")
    if sel.size > 1:
        # Refusing an ambiguous reference is the point: a formula that silently averaged
        # several rows would verify a number the document never claimed.
        raise DerivedError(
            f"{fname}#{col}{shown} selects {sel.size} rows, not one; "
            f"add a filter or ask for a statistic")
    v = float(sel.iloc[0])
    if not math.isfinite(v):
        raise DerivedError(f"{fname}#{col}{shown} is not finite")
    return v


def eval_derived(formula, resolver):
    """Evaluate a formula over named cells. Returns (value, substituted_formula).

    Only arithmetic over resolved references and numeric literals is permitted: the
    expression is parsed and every node type checked against a whitelist, so a name,
    attribute or call cannot appear. A formula that references something it does not
    name cannot be written.
    """
    import ast as _ast
    global _ALLOWED_NODES
    if _ALLOWED_NODES is None:
        _ALLOWED_NODES = (
            _ast.Expression, _ast.BinOp, _ast.UnaryOp, _ast.Constant,
            _ast.Add, _ast.Sub, _ast.Mult, _ast.Div, _ast.Pow,
            _ast.USub, _ast.UAdd, _ast.Tuple,
        )

    refs = list(DERIVED_REF.finditer(formula))
    if not refs:
        # Arithmetic over literals alone is a legitimate derived claim: "1.265e-05 is 106
        # times float32 epsilon" is checkable and involves no file. Requiring a file
        # reference forced such claims into a declared exception, which checks nothing.
        # The whitelist below still applies, so this cannot become an escape hatch.
        if re.search(r"[A-Za-z_]", re.sub(r"[eE](?=[+\-]?\d)", "", formula)):
            raise DerivedError(
                "formula names no file reference and is not pure arithmetic over literals")
    out, last, shown = [], 0, []
    for m in refs:
        val = _resolve_ref(m, resolver)
        out.append(formula[last:m.start()])
        out.append(f"({val!r})")
        shown.append(f"{m.group(0)} = {val:.6g}")
        last = m.end()
    out.append(formula[last:])
    expr = "".join(out)

    tree = _ast.parse(expr, mode="eval")
    for node in _ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise DerivedError(
                f"disallowed expression element {type(node).__name__}; "
                f"only arithmetic over named references is permitted")
    try:
        value = eval(compile(tree, "<derived>", "eval"), {"__builtins__": {}}, {})
    except ZeroDivisionError:
        raise DerivedError("division by zero")
    if not math.isfinite(float(value)):
        raise DerivedError("formula is not finite")
    return float(value), "; ".join(shown)


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
        for raw in open(path):
            # A '#' is a comment only at the START of a line. Mid-line it is content:
            # a reason routinely cites "issue #133", and the derived-claims syntax uses
            # '#' to separate a file from a column. Treating it as a comment anywhere
            # truncated every derived formula to its filename, which the self-test
            # caught on its first run.
            if raw.lstrip().startswith("#"):
                continue
            line = raw.rstrip("\n").strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                ex[parts[0].strip()] = parts[1].strip()
    return ex


def _entry_key(table, doc, raw):
    """The key in `table` that applies to claim `raw` in document `doc`, or None.

    An entry may be written scoped -- "docs/WAYS_OF_WORKING.md:117" -- or bare -- "117".
    A scoped entry wins, and it is the only way to keep two documents' identical numerals
    apart: a derived entry keyed "117" for a COAD ratio would otherwise VERIFY the journal
    volume in "PNAS 117:30266" in a different document, which is a false pass, and a false
    pass is worse than a false failure because nothing ever reports it.
    """
    base = os.path.basename(doc)
    for k in (f"{doc}:{raw}", f"{base}:{raw}", raw):
        if k in table:
            return k
    return None


def verify(doc, resolver, verbose=False, exceptions=None, derived=None):
    """Verify one document. Returns (rows, stats)."""
    exceptions = exceptions or {}
    derived = derived or {}
    md = open(doc, errors="replace").read()
    rows, cache, fv_cache, seen_missing, capped = [], {}, {}, set(), {}
    n_claims = n_ok = n_claims_derived_bad = 0
    for ln, text, cites in scopes(doc and md):
        body = strip_code(text)
        claims = list(numbers_in(body))
        if not claims:
            continue
        # Cited files are read LAZILY, one at a time, and the scan stops at the first
        # file that matches. Reading every cited file up front was affordable while a
        # citation named one file; once a placeholder or glob citation
        # (preds__<encoder>.parquet) expands to a whole per-encoder family, eager reading
        # pulled in twelve large parquets per scope and the sweep stopped finishing at
        # all. Most claims match in the first file, so this is the difference between
        # minutes and seconds.
        paths_for, used, notes = [], [], []
        for c in cites:
            if c not in cache:
                paths = resolver(c) or None
                # A family citation -- preds__<encoder>.parquet -- can expand to every
                # per-encoder file in every task: over a hundred parquets of hundreds of
                # megabytes each. Reading all of them to check a handful of claims is the
                # wrong trade, and doing it anyway made the largest report unmeasurable.
                # The expansion is capped and the cap is RECORDED, so a claim that fails
                # against a capped citation says so instead of being quietly wrong in
                # either direction. Ordered by size, smallest first: summary tables are
                # small and are where a quoted value almost always lives.
                if paths and len(paths) > 1:
                    paths = sorted(paths, key=lambda p: os.path.getsize(p)
                                   if os.path.exists(p) else 0)
                    keep, total = [], 0
                    for p in paths[:FAMILY_CAP]:
                        try:
                            total += os.path.getsize(p)
                        except OSError:
                            continue
                        if keep and total > FAMILY_BYTES:
                            break
                        keep.append(p)
                    if len(keep) < len(paths):
                        capped[c] = (len(paths), len(keep))
                    paths = keep
                cache[c] = paths
            if cache[c] is not None:
                paths_for.append((c, cache[c]))
                used.append(c)

        def read_cached(p):
            if p not in fv_cache:
                try:
                    fv_cache[p] = file_values(p)
                except Exception as e:
                    fv_cache[p] = None
                    if p not in seen_missing:
                        seen_missing.add(p)
                        rows.append(dict(doc=doc, line=ln, value="", status="unreadable",
                                         cited=p, detail=f"{type(e).__name__}: {e}"[:90],
                                         context=""))
            return fv_cache[p]
        for val, dec, pct, raw in claims:
            n_claims += 1
            if not used and not _entry_key(derived, doc, raw):
                # A derived entry is consulted even where the scope cites nothing: a
                # formula over literals ("106 times float32 epsilon") involves no file,
                # and reporting it as uncited would force it into a declared exception
                # when it is arithmetic anyone can check.
                rows.append(dict(doc=doc, line=ln, value=raw, status="uncited", cited="",
                                 detail="no readable file cited in scope or section",
                                 context=body[:110].replace("\n", " ")))
                continue
            # Each cited file is matched separately, since a FileValues holds its
            # own literal array; the first hit wins, as before.
            prov = None
            for _c, paths in paths_for:
                for p in paths:
                    f = read_cached(p)
                    if f is None:
                        continue
                    notes.extend(f.notes)
                    prov = matches(val, dec, pct, f)
                    if prov:
                        break
                if prov:
                    break
            # A derived claim is EVALUATED, not declared. Three outcomes, all
            # distinct: the arithmetic agrees (verified), the arithmetic disagrees
            # (DERIVED MISMATCH -- a real defect, in the document or in the formula),
            # or the formula cannot be resolved (DERIVED ERROR). None of them is a
            # silent pass, which is the whole difference from an exceptions entry.
            dkey = _entry_key(derived, doc, raw)
            if not prov and dkey:
                formula, why = derived[dkey]
                try:
                    got, shown = eval_derived(formula, resolver)
                except DerivedError as e:
                    rows.append(dict(doc=doc, line=ln, value=raw,
                                     status="DERIVED ERROR", cited=formula,
                                     detail=str(e)[:130],
                                     context=body[:110].replace("\n", " ")))
                    n_claims_derived_bad += 1
                    continue
                tol = 0.5 * (10 ** -dec) * 1.000001
                target = val / 100.0 if pct and abs(got) <= 1.5 else val
                if abs(got - target) <= tol or (
                        pct and abs(got * 100.0 - val) <= tol):
                    prov = f"derived: {formula} -> {got:.6g} [{why}]"
                else:
                    rows.append(dict(doc=doc, line=ln, value=raw,
                                     status="DERIVED MISMATCH", cited=formula,
                                     detail=f"formula gives {got:.6g}, document says "
                                            f"{raw} [{why}]"[:130],
                                     context=body[:110].replace("\n", " ")))
                    n_claims_derived_bad += 1
                    continue
            ekey = _entry_key(exceptions, doc, raw)
            if not prov and ekey:
                prov = f"declared: {exceptions[ekey]}"
            if prov:
                n_ok += 1
                if verbose:
                    rows.append(dict(doc=doc, line=ln, value=raw, status="ok",
                                     cited=",".join(used), detail=prov, context=""))
            else:
                # If a cited file was read in a reduced mode, say so on the row:
                # the claim may be unresolved because a statistic was not computed,
                # which is a different fact from the number being absent.
                caps = [f"{c}: cited family expanded to {n} files, smallest {k} read "
                        f"({FAMILY_BYTES // (1024 * 1024)} MB budget)"
                        for c, (n, k) in capped.items() if c in used]
                rows.append(dict(doc=doc, line=ln, value=raw, status="NOT FOUND",
                                 cited=",".join(used),
                                 detail="; ".join(sorted(set(notes)) + caps)[:200],
                                 context=body[:110].replace("\n", " ")))
    return rows, dict(doc=doc, claims=n_claims, ok=n_ok,
                      derived_bad=n_claims_derived_bad)


ALWAYS = []


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("docs", nargs="+")
    ap.add_argument("--search-dir", action="append", default=["."])
    ap.add_argument("--tsv")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--exceptions", default=".verify-exceptions")
    # Derived claims live in their own file because their entries are formulas, not
    # reasons: an exceptions entry asserts a claim need not be checked, a derived
    # entry says how to check it.
    ap.add_argument("--derived", default=".verify-derived")
    # A file consulted for EVERY claim, regardless of what the enclosing
    # subsection cites. This exists for a single-source-of-truth table such as
    # results/summary/deck_numbers.csv: the document quotes its numbers in prose
    # without citing it line by line, so without this the table is invisible to
    # the sweep and 30 checkable claims read as uncited.
    ap.add_argument("--always", action="append", default=[])
    ap.add_argument("--exclude-dir", action="append", default=[],
                    help="directory NAME to keep out of the index (e.g. superseded)")
    a = ap.parse_args()
    global ALWAYS
    ALWAYS = list(a.always)
    resolver = make_resolver(a.search_dir, exclude_dirs=set(a.exclude_dir))
    ex = load_exceptions(a.exceptions)
    dv = load_derived(a.derived)
    allrows, stats = [], []
    for d in a.docs:
        r, s = verify(d, resolver, a.verbose, ex, dv)
        allrows += r
        stats.append(s)
    # A DERIVED MISMATCH or DERIVED ERROR is a failure, not a neutral outcome: a
    # document containing one previously printed "0 not found" and looked clean, which
    # is the silent pass this whole class exists to prevent.
    bad = [r for r in allrows
           if r["status"] in ("NOT FOUND", "unreadable",
                              "DERIVED MISMATCH", "DERIVED ERROR")]
    for s in stats:
        def cnt(st):
            return sum(1 for r in allrows if r["doc"] == s["doc"] and r["status"] == st)
        n, dm, de = cnt("NOT FOUND"), cnt("DERIVED MISMATCH"), cnt("DERIVED ERROR")
        extra = ""
        if dm or de:
            extra = f", {dm} derived mismatch, {de} derived error"
        print(f"{s['doc']}: {s['claims']} claims, {s['ok']} verified, {n} not found, "
              f"{cnt('uncited')} uncited{extra}")
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
