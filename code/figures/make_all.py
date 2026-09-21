#!/usr/bin/env python
"""Render every deck figure, in order.

Stage: deck rendering (deck_figures_and_repo_update.md section 1.1).

Usage:
    python code/figures/make_all.py                 # all seven
    python code/figures/make_all.py fig03 fig05     # by prefix

Each figure is a standalone script reading only committed CSVs, so they are run
as separate processes rather than imported: a figure that fails takes its own
exit code and the others still render, and no figure can leave state behind that
another one picks up. HEST_ROOT is passed through unchanged so the whole set can
be rendered against a checkout somewhere other than the default path.

Every script prints its own render check (smallest font, text overlaps). This
runner fails if ANY figure reports a text overlap, because a figure with
colliding labels is not a deliverable, and a warning nobody reads is how it
ships anyway.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIGURES = [
    "fig01_fidelity.py",
    "fig02_replicate_leak.py",
    "fig03_split_staircase.py",
    "fig04_raw_head_width.py",
    "fig05_r2_ladder.py",
    "fig06_session_signature.py",
    "fig07_theta_and_variance.py",
]

OVERLAP_RE = re.compile(r"text overlaps (\d+)")


def main(argv):
    want = argv[1:]
    todo = [f for f in FIGURES if not want or any(f.startswith(w) for w in want)]
    if not todo:
        print(f"no figure matches {want}; known: {[f[:5] for f in FIGURES]}")
        return 2

    env = dict(os.environ)
    env.setdefault("MPLBACKEND", "Agg")
    failed, overlapping = [], []

    for f in todo:
        print(f"\n=== {f}")
        r = subprocess.run([sys.executable, str(HERE / f)], env=env,
                           capture_output=True, text=True)
        head = [ln for ln in r.stdout.splitlines()
                if "wrote" in ln or "OVERLAPS" in ln or "absorbed" in ln]
        print("\n".join(head) if head else r.stdout[-400:])
        if r.returncode != 0:
            failed.append(f)
            print(f"    FAILED rc={r.returncode}")
            print("   " + "\n   ".join(r.stderr.strip().splitlines()[-6:]))
            continue
        m = OVERLAP_RE.search(r.stdout)
        if m and int(m.group(1)) > 0:
            overlapping.append((f, int(m.group(1))))

    print(f"\n{'=' * 60}")
    print(f"rendered {len(todo) - len(failed)} of {len(todo)} figures")
    if failed:
        print(f"FAILED: {failed}")
    if overlapping:
        print(f"TEXT OVERLAPS: {overlapping}")
    if not failed and not overlapping:
        print("all clean: zero text overlaps")
    return 1 if (failed or overlapping) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
