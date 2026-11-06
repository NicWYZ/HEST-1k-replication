#!/usr/bin/env python3
"""Check that CLAUDE.md's state block still describes where the project stands.

Read only. Run from the repository root at every session start and before every
documentation commit. Python 3.8+, standard library only.

The state block is a fenced block with the info string `state` in CLAUDE.md:

    ```state
    updated: 2026-11-04 (oversight chat, personal account)
    unit: round02
    status: running
    next: Close round 2 once all three tracks have merged.
    branch round2-harmonize: running | docs/round02/tracks/harmonize/round02_harmonize_plan.md
    branch round2-borrow: to-merge | PR #21
    waiting: Q2 | since 2026-10-26 | venue, dates and authorship
    ```

unit status is one of open, running, waiting, closing, closed. branch status is one of
running, waiting, to-merge, abandoned. What follows a `|` is free text; a repository
path there is checked on that branch.

Flags: no state block or an invalid one; live branches the block does not name;
branches the block names that are no longer live; commits on main after CLAUDE.md last
changed; open pull requests from unnamed branches; CLAUDE.md over its line limit; paths
in CLAUDE.md and the index files that do not exist. Notes: items waiting longer than
--stale-days, plan paths not yet on their branch, [proposed] and [verify] tags.
Exit status is 0 unless --strict is given and something was flagged.
"""
import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
from pathlib import Path

UNIT_STATUS = {"open", "running", "waiting", "closing", "closed"}
BRANCH_STATUS = {"running", "waiting", "to-merge", "abandoned"}
PATH_EXT = (".md", ".py", ".sh", ".R", ".csv", ".json", ".yaml", ".yml", ".toml", ".txt", ".tex", ".tsv")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def git(*args):
    r = subprocess.run(["git", "--no-optional-locks", *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def parse_block(text):
    m = re.search(r"^```state[ \t]*\n(.*?)^```", text, re.S | re.M)
    if not m:
        return None
    block = {"branches": {}, "waiting": []}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, val = (s.strip() for s in line.split(":", 1))
        if key.startswith("branch "):
            parts = [p.strip() for p in val.split("|")]
            block["branches"][key[7:].strip()] = parts
        elif key == "waiting":
            block["waiting"].append(val)
        else:
            block[key] = val
    return block


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", default="CLAUDE.md", help="the state file (default CLAUDE.md)")
    ap.add_argument("--main", default=None, help="the main branch ref (default origin/main, else main)")
    ap.add_argument("--index", nargs="*", default=None,
                    help="index files whose paths are checked (default: docs/README.md and planning/README.md if present)")
    ap.add_argument("--max-lines", type=int, default=200, help="line limit for the state file (default 200)")
    ap.add_argument("--stale-days", type=int, default=14, help="note waiting items older than this (default 14)")
    ap.add_argument("--no-remote", action="store_true", help="skip the pull-request lookup")
    ap.add_argument("--strict", action="store_true", help="exit 1 when anything is flagged")
    a = ap.parse_args()

    if not git("rev-parse", "--show-toplevel"):
        sys.exit("Not inside a git repository; run from the repository root.")
    state = Path(a.state)
    if not state.is_file():
        sys.exit(f"{a.state} not found; run from the repository root or pass --state.")
    text = state.read_text(encoding="utf-8")
    main_ref = a.main or next((r for r in ("origin/main", "origin/master", "main")
                               if git("rev-parse", "--verify", "-q", r)), None)
    remote = main_ref.split("/")[0] + "/" if main_ref and "/" in main_ref else ""
    flags, notes = [], []

    # The state block.
    block = parse_block(text)
    if block is None:
        flags.append(f"{a.state} has no ```state block; add one (see this script's --help)")
        block = {"branches": {}, "waiting": []}
    else:
        for key in ("unit", "status", "next"):
            if not block.get(key):
                flags.append(f"state block has no `{key}:` line")
        if block.get("status") and block["status"].split()[0] not in UNIT_STATUS:
            flags.append(f"state block status `{block['status']}` is not one of {sorted(UNIT_STATUS)}")
        for name, parts in block["branches"].items():
            if parts[0] not in BRANCH_STATUS:
                flags.append(f"branch {name}: status `{parts[0]}` is not one of {sorted(BRANCH_STATUS)}")
        today = dt.date.today()
        for w in block["waiting"]:
            d = DATE.search(w)
            if d and (today - dt.date.fromisoformat(d.group())).days > a.stale_days:
                notes.append(f"waiting more than {a.stale_days} days: {w}")

    # Length.
    n = len(text.splitlines())
    if n > a.max_lines:
        flags.append(f"{a.state} has {n} lines (limit {a.max_lines}); move finished work to the log and facts to the record")

    if not main_ref:
        flags.append("no main branch found; fetch first or pass --main")
    else:
        if git("rev-parse", "HEAD") != git("rev-parse", main_ref):
            notes.append(f"HEAD is not {main_ref}; pull before committing documentation")
        # Commits on main after the state file last changed there.
        base = git("log", "-1", "--format=%h", main_ref, "--", a.state)
        newer = git("log", "--oneline", "--first-parent", f"{base}..{main_ref}") if base else ""
        if newer:
            flags.append(f"commits on {main_ref} after {a.state} last changed ({base}); read them and update the state:\n    "
                         + newer.replace("\n", "\n    "))
        # Live branches against the block.
        out = git("branch", "-r", "--no-merged", main_ref, "--format=%(refname:short) %(committerdate:short) %(subject)")
        live = {}
        for l in out.splitlines():
            ref = l.split()[0] if l else ""
            if ref and "/HEAD" not in ref and ref != main_ref:
                live[ref[len(remote):] if ref.startswith(remote) else ref] = l
        unnamed = [l for b, l in live.items() if b not in block["branches"]]
        if unnamed:
            flags.append("live branches the state block does not name (add a `branch <name>:` line with its status):\n    "
                         + "\n    ".join(unnamed))
        for name, parts in block["branches"].items():
            if name not in live and parts[0] != "abandoned":
                flags.append(f"branch {name} is named as {parts[0]} but has no commits off main (merged or deleted); update the state")
            for p in parts[1:]:
                if name in live and "/" in p and p.endswith(PATH_EXT) and " " not in p:
                    if subprocess.run(["git", "cat-file", "-e", f"{remote}{name}:{p}"], capture_output=True).returncode:
                        notes.append(f"{p} is not on {name} yet")

    # Open pull requests.
    if not a.no_remote and shutil.which("gh"):
        r = subprocess.run(["gh", "pr", "list", "--state", "open", "--limit", "50", "--json", "number,title,headRefName",
                            "--template", "{{range .}}{{.headRefName}}\t#{{.number}} {{.title}}\n{{end}}"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            for l in r.stdout.splitlines():
                head, desc = l.split("\t", 1)
                (notes if head in block["branches"] else flags).append(f"open pull request {desc} from {head}"
                                                                        + ("" if head in block["branches"] else ", not in the state block"))
        else:
            notes.append("gh could not list pull requests; check them by hand")

    # Paths named in the state and index files exist.
    index = a.index if a.index is not None else [p for p in ("docs/README.md", "planning/README.md") if Path(p).is_file()]
    for f in [a.state, *index]:
        body = Path(f).read_text(encoding="utf-8", errors="ignore") if Path(f).is_file() else ""
        body = re.sub(r"^```state.*?^```", "", body, flags=re.S | re.M)
        missing = set()
        for tok in re.findall(r"(?<!`)`([^`\s]+)`(?!`)", body):
            tok = tok.rstrip(".,;:)")
            if tok.startswith(("/", "~", "$", "<", "http", "-")) or any(c in tok for c in "<>*{}") or "/" not in tok:
                continue
            if not (tok.endswith(PATH_EXT) or tok.endswith("/")):
                continue
            if any(Path(c).exists() for c in (tok, Path(f).parent / tok)):
                continue
            if subprocess.run(["git", "check-ignore", "-q", tok], capture_output=True).returncode == 0:
                continue  # gitignored, so absent from clones by design
            missing.add(tok)
        if missing:
            flags.append(f"paths in {f} not found: " + ", ".join(sorted(missing)))

    # Tags still open.
    for tag in ("[proposed]", "[verify]"):
        hits = [i for i, l in enumerate(text.splitlines(), 1) if tag in l and f"`{tag}`" not in l]
        if hits:
            notes.append(f"{tag} in {a.state} at lines {hits}")

    for x in notes:
        print("Note: " + x)
    for x in flags:
        print("- " + x)
    print(f"{len(flags)} flagged." if flags else "Nothing flagged.")
    return 1 if (a.strict and flags) else 0


if __name__ == "__main__":
    sys.exit(main())
