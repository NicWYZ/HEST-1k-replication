#!/usr/bin/env python3
"""Check that CLAUDE.md and the chronological docs/ tree are current, complete and tidy.

Read only. Run from the repository root at the start of every planning session, before
each documentation commit, and as part of every round close. Accepted hits go in
.state-check-ignore, one substring per line. Python 3.8+, standard library only. Exit
status is 0 unless --strict is given and something was flagged.
"""
import argparse, re, subprocess, sys
from collections import defaultdict
from pathlib import Path, PurePosixPath as P

EXT = (".md", ".py", ".csv", ".json", ".txt", ".sh", ".pptx", ".pdf", ".R", ".yaml", ".toml")
ROUND = re.compile(r"^round(\d+)$")
INTERVAL = re.compile(r"^i\d{2,}$")
ROUND_ROOT_DIRS = ("00_prep", "oversight", "tracks")
PREFIX = re.compile(r"^round0*(\d+)_")


def git(*args):
    r = subprocess.run(["git", "--no-optional-locks", *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def prose_lines(text):
    """Yield (number, line) outside code fences, skipping tables and headings."""
    fence = False
    for i, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if not fence and line.strip() and not line.lstrip().startswith(("|", "#")):
            yield i, line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="CLAUDE.md")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--log", default="docs/progress-log.md")
    ap.add_argument("--standing", nargs="*",
                    default=["README.md", "progress-log.md", "WAYS_OF_WORKING.md", "goals.md", "open-questions.md", "moved.md"],
                    help="files allowed directly under docs/")
    ap.add_argument("--standing-dirs", nargs="*", default=["reference"], help="folders allowed directly under docs/ besides rounds")
    ap.add_argument("--summary-heading", default="What the round established")
    ap.add_argument("--closing", help="the round being closed, e.g. round05; its summary is then required")
    ap.add_argument("--main", default="origin/main")
    ap.add_argument("--max-lines", type=int, default=200)
    ap.add_argument("--style", nargs="*", default=[], help="extra files to check for banned constructions")
    ap.add_argument("--facts-from", help="an old version of CLAUDE.md; its facts must survive in CLAUDE.md or docs/")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    tracked = git("ls-files", "--cached", "--others", "--exclude-standard").splitlines()
    if not tracked:
        sys.exit("Not inside a git repository with tracked files; run from the repository root.")
    if not Path(a.state).is_file():
        sys.exit(f"{a.state} not found; run from the repository root or pass --state.")
    docs = P(a.docs)
    state = Path(a.state).read_text(encoding="utf-8")
    flags, notes = [], []
    ignore = []
    if Path(".state-check-ignore").is_file():
        ignore = [l.strip() for l in Path(".state-check-ignore").read_text(encoding="utf-8").splitlines()
                  if l.strip() and not l.startswith("#")]
    in_docs = [P(p) for p in tracked if P(p).parts[:len(docs.parts)] == docs.parts]
    md_docs = [p for p in in_docs if p.suffix == ".md"]
    basenames = {P(p).name for p in tracked}
    rel = lambda p: P(*p.parts[len(docs.parts):])
    read = lambda p: Path(p).read_text(encoding="utf-8", errors="ignore") if Path(p).is_file() else ""

    def arrived(path):
        out = git("log", "-1", "--first-parent", "--format=%ct", "HEAD", "--", str(path))
        return int(out) if out else 0

    # 1. Length of CLAUDE.md.
    n = len(state.splitlines())
    if n > a.max_lines:
        flags.append(f"{a.state} has {n} lines (limit {a.max_lines}); move finished steps to the progress log")

    # 2. Staleness. The base is the last commit on the main branch that changed CLAUDE.md,
    # since a session corrects the state before committing it.
    if not git("rev-parse", "--verify", a.main):
        flags.append(f"{a.main} not found; fetch first")
    else:
        if git("rev-parse", "HEAD") != git("rev-parse", a.main):
            notes.append(f"HEAD differs from {a.main}; pull before committing.")
        base = git("log", "-1", "--format=%h", a.main, "--", a.state)
        newer = git("log", "--oneline", "--first-parent", f"{base}..{a.main}") if base else ""
        if newer:
            flags.append(f"commits on {a.main} after {a.state} last changed ({base}); read them and correct the "
                         "current state:\n    " + newer.replace("\n", "\n    "))
    tags = git("for-each-ref", "--sort=-creatordate", "--count=3",
               "--format=%(refname:short) %(creatordate:short)", "refs/tags")
    if tags:
        notes.append("latest tags: " + "; ".join(tags.splitlines()))

    # 3. Layout of docs/.
    rounds, stray = {}, set()
    for p in in_docs:
        r = rel(p).parts
        if r[-1].startswith("."):
            continue
        if len(r) == 1:
            if r[0] not in a.standing:
                flags.append(f"loose file at the top of {docs}/: {r[0]} (file it in a round folder or add it to --standing)")
            continue
        m = ROUND.match(r[0])
        if not m:
            if r[0] not in a.standing_dirs and r[0] not in stray:
                stray.add(r[0])
                flags.append(f"folder {docs}/{r[0]}/ is neither a round folder nor a standing folder")
            continue
        rounds.setdefault(r[0], int(m.group(1)))
        if len(r) == 2 and int(m.group(1)) > 0 and r[1] not in ("README.md", "masterplan.md"):
            flags.append(f"loose file at the top of {docs}/{r[0]}/: {r[1]}")
        if int(m.group(1)) > 0 and len(r) >= 3:
            if not (INTERVAL.match(r[1]) or r[1] in ROUND_ROOT_DIRS) and (r[0], r[1]) not in stray:
                stray.add((r[0], r[1]))
                flags.append(f"{docs}/{r[0]}/{r[1]}/ is not 00_prep/, iNN/, oversight/ or tracks/")
            elif (INTERVAL.match(r[1]) or r[1] == "tracks") and len(r) == 3:
                flags.append(f"file directly in {docs}/{r[0]}/{r[1]}/ without a track folder: {r[2]}")
            pm = PREFIX.match(r[-1])
            if pm and p.suffix == ".md" and r[1] != "00_prep" and int(pm.group(1)) != int(m.group(1)):
                flags.append(f"{p} carries a round prefix that differs from its folder")
    for name, num in sorted(rounds.items(), key=lambda kv: kv[1]):
        if not re.match(r"^round\d{2,}$", name):
            flags.append(f"{docs}/{name}/ should be zero-padded (round{num:02d}) so rounds sort in order")
        if not Path(docs / name / "README.md").is_file():
            flags.append(f"{docs}/{name}/README.md is missing")
        started = any(INTERVAL.match(d.name) for d in Path(docs / name).iterdir() if d.is_dir())
        if started and not Path(docs / name / "masterplan.md").is_file():
            flags.append(f"{docs}/{name}/ has intervals but no masterplan.md")
    current = max(rounds.values()) if rounds else None
    if rounds:
        notes.append(f"rounds found: {', '.join(sorted(rounds, key=rounds.get))}; the highest is taken as current")

    # 4. Reading guides list every document, and closed rounds carry their summary.
    top = read(docs / "README.md")
    if not top:
        flags.append(f"{docs}/README.md, the reading guide, is missing")
    for name in rounds:
        if top and name not in top:
            flags.append(f"{docs}/README.md has no row for {name}")
    for p in md_docs:
        r = rel(p).parts
        if r[-1] == "README.md" and len(r) <= 2 or (len(r) == 2 and r[1] == "masterplan.md"):
            continue
        if ROUND.match(r[0]):
            guide = read(docs / r[0] / "README.md")
            if guide and str(P(*r[1:])) not in guide and p.name not in guide:
                flags.append(f"{p} has no row in {docs}/{r[0]}/README.md")
        elif top and str(P(*r)) not in top and p.name not in top:
            flags.append(f"{p} has no row in {docs}/README.md")
    for name, num in rounds.items():
        if 0 < num and (num != current or name == a.closing) and a.summary_heading not in read(docs / name / "README.md"):
            flags.append(f"{docs}/{name}/README.md has no '{a.summary_heading}' section, and the round is closed or being closed")

    # 5. Basenames are unique, so a file opened alone says where it belongs.
    seen = defaultdict(list)
    for p in md_docs:
        if p.name not in ("README.md", "masterplan.md"):
            seen[p.name].append(str(p))
    for name, paths in seen.items():
        if len(paths) > 1:
            flags.append(f"basename {name} is used more than once: {', '.join(paths)}")

    # 6. The state and the guides are not behind the documents they describe.
    for f in (a.state, a.log):
        t = arrived(f)
        later = [str(p) for p in md_docs if str(p) != f and p.name != "README.md" and arrived(p) > t]
        if later:
            flags.append(f"{f} last changed before these documents arrived: " + ", ".join(later[:10])
                         + (" ..." if len(later) > 10 else ""))
    for name in rounds:
        guide = docs / name / "README.md"
        t = arrived(guide)
        later = [str(p) for p in md_docs if rel(p).parts[0] == name and p != guide and arrived(p) > t]
        if later and Path(guide).is_file():
            flags.append(f"{guide} last changed before these documents arrived: " + ", ".join(later[:10]))

    # 7. Paths named in CLAUDE.md and the reading guides exist.
    for f in [P(a.state)] + [p for p in md_docs if p.name == "README.md"]:
        missing = []
        for tok in re.findall(r"(?<!`)`([^`\s]+)`(?!`)", read(f)):
            tok = tok.rstrip(".,;:)")
            if any(c in tok for c in "<>*~$") or tok.startswith(("/", "http", ".git/")) or not tok.endswith(EXT + ("/",)):
                continue
            cands = [P(tok), f.parent / tok, docs / tok]
            if not any(Path(c).exists() for c in cands) and ("/" in tok.rstrip("/") or P(tok).name not in basenames):
                missing.append(tok)
        if missing:
            flags.append(f"paths in {f} not found: " + ", ".join(sorted(set(missing))))

    # 8. Banned constructions, which are em-dashes and possible colon-then-explanation sentences.
    core = [a.state, a.log, *[str(p) for p in md_docs if p.name in ("README.md", "masterplan.md")], *a.style]
    cur = [str(p) for p in md_docs if current is not None and ROUND.match(rel(p).parts[0] if len(rel(p).parts) > 1 else "")
           and rounds.get(rel(p).parts[0]) == current]
    for f in dict.fromkeys(core + cur):
        for i, line in enumerate(read(f).splitlines(), 1):
            if "\u2014" in line:
                flags.append(f"{f}:{i} em-dash")
    for f in core:
        for i, line in prose_lines(read(f)):
            plain = re.sub(r"`[^`]*`|\*\*[^*]*\*\*|\[[^\]]*\]\([^)]*\)|https?://\S+", "", line)
            if re.search(r"[a-z)]: [A-Za-z]", plain) and not plain.rstrip().endswith(":"):
                flags.append(f"{f}:{i} possible colon-then-explanation: {line.strip()[:90]}")

    # 9. Tags still open in CLAUDE.md.
    for tag in ("[proposed]", "[verify]"):
        hits = [i for i, l in enumerate(state.splitlines(), 1) if tag in l]
        if hits:
            notes.append(f"{tag} in {a.state} at lines {hits}")

    # 10. Facts of an old CLAUDE.md that are now nowhere.
    if a.facts_from:
        old = read(a.facts_from)
        new = state + "".join(read(p) for p in md_docs)
        toks = set(re.findall(r"(?<!`)`([^`\n]+)`(?!`)", old)) | set(re.findall(r"\b\d{4}-\d{2}-\d{2}\b", old))
        months = "January|February|March|April|May|June|July|August|September|October|November|December"
        toks |= set(re.findall(r"\b\d{1,2} (?:%s)\b" % months, old))
        toks |= set(re.findall(r"#\d+\b", old)) | set(re.findall(r"\b\d+\.\d+\b", old))
        lost = sorted(t for t in toks if t not in new)
        if lost:
            flags.append(f"in {a.facts_from} but in neither {a.state} nor {docs}/; account for each: " + ", ".join(lost))

    flags = [f for f in flags if not any(i in f for i in ignore)]
    for x in notes:
        print("Note: " + x)
    for f in flags:
        print("- " + f)
    print(f"{len(flags)} flagged." if flags else "Nothing flagged.")
    return 1 if (a.strict and flags) else 0


if __name__ == "__main__":
    sys.exit(main())
