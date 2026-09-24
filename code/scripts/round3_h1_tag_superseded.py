"""Tag the superseded IDC `audited` rows of every round-3 result table.

Instruction: docs/decisions/round3_A3_decisions.md section 2.1, transcribed in
docs/round3_execution_plan.md section 13.2 item 1 and section 13.4 item 1 -- "Every round-3 table
carrying an IDC `audited` row keeps the row, tagged `superseded_label_set`; no further stage runs
IDC `audited`."

What it does. For every CSV under results/round3/ that has both a `task` and a `label_set` column
and at least one row with task == IDC and label_set == audited, it appends one column,
`superseded_label_set`, holding True on exactly those rows and False on every other row. Files with
no such row are left alone, so the tag marks the superseded label set rather than the absence of it
on tables that never had it.

How the edit is made, and why it is made that way. The new field is appended to the end of each
line as text; no existing byte of any line is touched. That is stronger than rewriting the file
through a CSV writer, which would be free to requote or reformat fields it round-trips. The script
then reparses the file and asserts that every pre-existing cell is equal to what it was, so the
"nothing else changed" claim is checked rather than asserted.

The parquets are on Longleaf and gitignored; they are NOT touched by this script, and the tag is a
property of the committed summary tables only.

Rerunning is safe: a file that already carries the column is verified against the rule and left
byte-identical, and the manifest records it as `already_tagged`.

Outputs results/round3/H1_housekeeping/superseded_tag_manifest.csv with columns
file, rows, rows_tagged, sha256_before, sha256_after, action.

Usage (repository root):  python code/scripts/round3_h1_tag_superseded.py
"""
from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

ROOT = Path("results/round3")
OUTDIR = ROOT / "H1_housekeeping"
MANIFEST = OUTDIR / "superseded_tag_manifest.csv"
COL = "superseded_label_set"
TASK, LABEL_SET = "IDC", "audited"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path):
    with open(path, newline="") as f:
        r = csv.reader(f)
        try:
            header = next(r)
        except StopIteration:
            return None, []
        return header, list(r)


def is_superseded(row, ti: int, li: int) -> bool:
    return row[ti] == TASK and row[li] == LABEL_SET


def split_eol(line: str):
    """Return (payload, end_of_line) so the file's own line terminators survive the edit."""
    for eol in ("\r\n", "\n", "\r"):
        if line.endswith(eol):
            return line[: -len(eol)], eol
    return line, ""


def tag(path: Path) -> dict | None:
    header, rows = read_rows(path)
    if header is None or "label_set" not in header or "task" not in header:
        return None
    ti, li = header.index("task"), header.index("label_set")
    n_tagged = sum(1 for row in rows if is_superseded(row, ti, li))
    if n_tagged == 0:
        return None

    before = sha256(path)
    if COL in header:
        ci = header.index(COL)
        for row in rows:
            want = "True" if is_superseded(row, ti, li) else "False"
            assert row[ci] == want, f"{path}: {COL} is {row[ci]!r}, rule says {want!r}"
        return {"file": str(path), "rows": len(rows), "rows_tagged": n_tagged,
                "sha256_before": before, "sha256_after": before, "action": "already_tagged"}

    lines = path.read_text().splitlines(keepends=True)
    assert len(lines) == len(rows) + 1, (path, len(lines), len(rows))
    out = []
    head, eol = split_eol(lines[0])
    out.append(f"{head},{COL}{eol}")
    for line, row in zip(lines[1:], rows):
        payload, eol = split_eol(line)
        out.append(f"{payload},{'True' if is_superseded(row, ti, li) else 'False'}{eol}")
    path.write_text("".join(out))

    header2, rows2 = read_rows(path)
    assert header2 == header + [COL], (path, header2[-3:])
    assert len(rows2) == len(rows), (path, len(rows2), len(rows))
    for a, b in zip(rows, rows2):
        assert b[:-1] == a, f"{path}: a pre-existing cell changed"
        assert b[-1] == ("True" if is_superseded(a, ti, li) else "False")
    return {"file": str(path), "rows": len(rows), "rows_tagged": n_tagged,
            "sha256_before": before, "sha256_after": sha256(path), "action": "tagged"}


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    records = []
    for path in sorted(ROOT.rglob("*.csv")):
        if path.parent == OUTDIR:
            continue
        rec = tag(path)
        if rec is not None:
            records.append(rec)
    fields = ["file", "rows", "rows_tagged", "sha256_before", "sha256_after", "action"]
    with open(MANIFEST, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(records)
    n_tagged = sum(r["action"] == "tagged" for r in records)
    print(f"wrote {MANIFEST}: {len(records)} files in scope "
          f"({n_tagged} tagged this run, {len(records) - n_tagged} already tagged), "
          f"{sum(r['rows_tagged'] for r in records)} rows marked "
          f"{COL}=True over {sum(r['rows'] for r in records)} rows")
    print("parquets are on Longleaf and gitignored; none were touched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
