"""Sweep code/scripts/ for docstring damage after the automated Stage-line edit.

Stage: closeout repository refresh (deck_figures_and_repo_update.md section 2.5).

Three faults, each of which this project has now actually produced:
  1. a file that no longer parses;
  2. a Stage line spliced into the middle of a summary sentence, because the
     inserting script assumed the summary was one line;
  3. a missing Stage line.

The point of running this as a separate sweep is that the inserting script
reported success on every file it touched -- it compiled each result, and a
mid-sentence splice compiles perfectly well.
"""
import ast
import pathlib
import re
import sys

D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "code/scripts")
unparsed, spliced, missing, ok = [], [], [], 0

for p in sorted(D.glob("*.py")):
    text = p.read_text()
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        unparsed.append((p.name, f"line {e.lineno}: {e.msg}"))
        continue
    doc = ast.get_docstring(tree)
    if not doc:
        missing.append((p.name, "no module docstring"))
        continue
    lines = doc.split("\n")
    i = next((k for k, l in enumerate(lines) if l.lstrip().startswith("Stage:")), None)
    if i is None:
        missing.append((p.name, "no Stage line"))
        continue
    if i > 0:
        prev = next((lines[k] for k in range(i - 1, -1, -1) if lines[k].strip()), "")
        # A summary that does not end in terminal punctuation was cut mid-sentence.
        if prev and not re.search(r'[.?!:"\]\)]\s*$', prev.strip()):
            spliced.append((p.name, prev.strip()[-72:]))
            continue
    ok += 1

n = len(list(D.glob("*.py")))
print(f"{D}: {n} scripts")
print(f"  well formed          : {ok}")
print(f"  do not parse         : {len(unparsed)}")
print(f"  Stage line mid-sentence: {len(spliced)}")
print(f"  no Stage line        : {len(missing)}")
for label, rows in (("DO NOT PARSE", unparsed), ("MID-SENTENCE", spliced),
                    ("NO STAGE LINE", missing)):
    for name, why in rows:
        print(f"    [{label}] {name}: {why}")
sys.exit(1 if (unparsed or spliced or missing) else 0)
