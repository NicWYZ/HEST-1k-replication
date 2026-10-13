"""Mechanical check of cheatsheet.txt (round 6 extension, instruction 6.4).

    python3 check_cheatsheet.py

Reads cheatsheet.txt and genes.txt in the current directory and reports the
size and five kinds of possible problem, with line numbers. A flag from this
script is a warning, not a verdict. An independent reviewer decides whether
the file follows RULES.md.

The harness copies this file into a writer's directory as check_cheatsheet.py
with the size written into the line `B = ...` below, and runs the same
function, check(), on every version of every cheatsheet.
"""
import re
import sys

B = None  # the allowed size in bytes, written in by the harness

CODE_START = re.compile(r"^(import |from \S.* import\b|def |class [A-Za-z_]\w*\s*[(:]|return |print\(|lambda\b)")
CODE_BLOCK = re.compile(r"^(for |while |if ).*:$")
CODE_LIB = re.compile(r"(?<![A-Za-z0-9_])(np|pd|cv2|skimage|sklearn)\.[A-Za-z_]")
SPOT_ID = re.compile(r"(?<![A-Za-z0-9_])s\d{4}(?![A-Za-z0-9_])")
PATIENT = re.compile(r"(?<![A-Za-z0-9_])P[1-7](?![A-Za-z0-9_])")
NUMBER = re.compile(r"(?<![A-Za-z0-9_.])\d+(?:\.\d+)?(?![A-Za-z_])")
RUN, TABLE_ROWS, TABLE_NUMBERS = 40, 64, 5


def gene_list(token, genes):
    parts = [p.strip("()[]{}:;.'\"`*") for p in re.split(r"[,/\-]", token)]
    parts = [p for p in parts if p]
    return bool(parts) and all(p in genes for p in parts)


def check(data, b, genes):
    """data is the file's bytes. Returns (size in bytes, list of flags)."""
    genes = set(genes)
    flags = []

    def flag(k, line, reason):
        flags.append({"check": k, "line": line, "reason": reason})

    size = len(data)
    if size > b:
        flag(1, 0, f"the file is {size} bytes, over the limit of {b}; everything after byte {b} will be cut off")
    lines = data.decode("utf-8", errors="replace").split("\n")
    run_start, run_len = None, 0
    for n, raw in enumerate(lines + [""], start=1):
        line = raw.rstrip("\r")
        s = line.lstrip(" ")
        if n <= len(lines):
            if s.startswith("```"):
                flag(2, n, "a code fence")
            elif CODE_START.match(s) or CODE_BLOCK.match(s.rstrip()):
                flag(2, n, "the line looks like code")
            if CODE_LIB.search(line):
                flag(2, n, "the line names a code library (np., pd., cv2., skimage. or sklearn.)")
            for m in SPOT_ID.finditer(line):
                flag(3, n, f"'{m.group(0)}' has the form of a training spot ID")
            for m in PATIENT.finditer(line):
                flag(3, n, f"'{m.group(0)}' is a patient label")
            for tok in line.split():
                if len(tok) >= RUN and not gene_list(tok, genes):
                    flag(4, n, f"an unbroken run of {len(tok)} characters without a space")
        numeric = n <= len(lines) and len(NUMBER.findall(line)) >= TABLE_NUMBERS
        if numeric:
            if run_start is None:
                run_start, run_len = n, 0
            run_len += 1
        else:
            if run_start is not None and run_len > TABLE_ROWS:
                flag(5, run_start, f"a table of {run_len} rows (lines {run_start} to {n - 1}), more than {TABLE_ROWS}")
            run_start, run_len = None, 0
    return size, flags


def report(size, b, flags):
    out = ["This check is mechanical. A flag is a warning, not a verdict. An independent reviewer "
           "decides whether the file follows RULES.md.",
           f"Size: {size} bytes of {b} allowed ({'within' if size <= b else 'OVER'} the limit)."]
    if not flags:
        out.append("No possible problems found.")
    for f in flags:
        where = f"line {f['line']}" if f["line"] else "whole file"
        out.append(f"check {f['check']}, {where}: {f['reason']}")
    return "\n".join(out)


if __name__ == "__main__":
    try:
        data = open("cheatsheet.txt", "rb").read()
    except OSError:
        print("cheatsheet.txt is not in this directory yet.")
        sys.exit(1)
    genes = [g.strip() for g in open("genes.txt") if g.strip()]
    size, flags = check(data, B, genes)
    print(report(size, B, flags))
