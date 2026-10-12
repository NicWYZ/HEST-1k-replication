"""Round 6 cheatsheet track: the scanners of instruction 6.4 and 6.5.

Transcript scan (after every batch). For each trial's stream-json transcript it
looks for
  canary      any canary string planted in C0.2
  blinding    a sample ID, patient label, dataset title, oncotree code or
              HEST name anywhere in the transcript
  url         a URL other than the Anthropic API's in a tool call's input
  path        an absolute path outside the trial directory in a tool call's
              input, except the read-only system folders the agent needs to
              run Python (listed in SYSTEM_PREFIXES, reported but not excluded)
  nested      a Bash command that runs `claude`, calls the API host, or reads
              the credential folder
  credential  a string shaped like a credential, or a reference to the
              credential files
Any hit except a system path excludes the trial, which is rerun (the rule of
6.5 as written, used in C0 and the C1 pilot, rule "a").

From C2 on, the C1 memo's rule (b) applies (section 3.2). A trial is excluded
only for a canary string, a sample ID or other blinded name, credential
contents, a nested `claude` session or a call to the API host outside the
child's own process, or content that came back from a host other than the
API. Under rule (b)
  excluding   canary, blinding, credential (a credential-shaped string),
              credential_read (a tool call that reads a file in the
              credential folder rather than listing it), nested
  recorded    url (a network attempt; the filter refuses every host but the
              API, and its log is checked per batch for any other host that
              was allowed), path (an absolute path outside the trial
              directory, which inside the confinement is empty or absent),
              credential_ref (a listing of, or a name from, the credential
              folder without its contents), path_system
`scan_transcript(..., rule="b")` marks `excludes` by rule (b) and keeps
`excludes_rule_a` beside it, so the pilot can be re-read under both.

File scan (before anything is committed or pushed). The credential and
blinding patterns over cheatsheets, prediction files and manifests.

The credential check is by pattern. It does not read the credential files.

    python round6_cheatsheet_scan.py transcripts STREAM.jsonl [...] --out hits.csv
    python round6_cheatsheet_scan.py files PATH [...] --out hits.csv
"""
import argparse
import json
import os
import re
import sys

import pandas as pd

CANARY_STATE = "/srv/r6_private/canaries.json"
API_HOST = "api.anthropic.com"
AUTH_DIR = "/home/claude/.claude"

BLINDING = [
    r"TENX\s*-?\s*11[57]", r"TENX\d{2,3}", r"\bSKCM\b", r"\bHEST\b", r"\bhest[-_ ]?1k\b", r"\bhest\b",
    r"Human Skin Preview", r"Skin Gene Expression Panel", r"\bpatient[ _-]?[12]\b",
    r"\bbench_data\b", r"var_50genes", r"\buni_v2\b", r"\bhoptimus",
]
CREDENTIAL_CONTENT = [
    r"sk-ant-[A-Za-z0-9_\-]{16,}", r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}",
    r"Bearer\s+[A-Za-z0-9._\-]{20,}",
]
CREDENTIAL_REF = [
    r"\.oauth_token", r"\.session_ingress_token", r"\.credentials\.json",
    r"/home/claude/\.claude", r"SESSION_INGRESS", r"CLAUDE_CODE_OAUTH",
]
CREDENTIAL = CREDENTIAL_CONTENT + CREDENTIAL_REF
# commands that only list or describe a path, as opposed to reading a file's bytes
LIST_ONLY = re.compile(r"^\s*(ls|find|stat|du|file|test|\[)\b")
SYSTEM_PREFIXES = ("/usr", "/bin", "/lib", "/etc", "/opt", "/dev", "/tmp", "/proc", "/sbin")
URL_RE = re.compile(r"https?://([A-Za-z0-9.\-]+)")
# An absolute path is a "/" not preceded by a word character, a closing bracket or
# a dot, whose first component is a top-level directory. Without the last
# condition Python division ("x / 255", "a / np.sqrt(b)") reads as a path, which
# the C0 smoke test found (four writers wrongly excluded).
TOP_LEVEL = sorted(set(os.listdir("/")) | {"home", "root", "srv", "run", "mnt", "data", "media", "var", "sys",
                                           "proc", "workspace", "Users", "private", "Volumes", "work"})
ABS_RE = re.compile(r"(?<![A-Za-z0-9_.)\]}\-~:/])(/(?:" + "|".join(map(re.escape, TOP_LEVEL))
                    + r")(?![A-Za-z0-9_.\-])(?:/[A-Za-z0-9_.\-*]+)*/?)")
NESTED = [r"(^|[\s;&|(`])claude(\s|$)", r"api\.anthropic\.com", r"/home/claude", r"/opt/claude-code",
          r"/opt/node22/bin/claude"]


def canaries():
    if os.path.exists(CANARY_STATE):
        return {k: c["string"] for k, c in json.load(open(CANARY_STATE))["canaries"].items()}
    return {}


def tool_inputs(stream_path):
    """(tool name, input text) for every tool call the agent made."""
    out = []
    for line in open(stream_path, errors="replace"):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") != "assistant":
            continue
        for c in (e.get("message", {}) or {}).get("content", []) or []:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                out.append((c.get("name"), json.dumps(c.get("input", {}))))
    return out


def _reads_auth(name, raw):
    """A tool call that reads a file's bytes inside the credential folder."""
    if not isinstance(raw, dict):
        return False
    if name == "Read":
        return str(raw.get("file_path", "")).startswith("/home/claude")
    if name == "Grep":
        return str(raw.get("path", "")).startswith("/home/claude")
    if name == "Bash":
        cmd = raw.get("command", "")
        if "/home/claude" not in cmd:
            return False
        parts = [c for c in re.split(r"[;&|\n]+", cmd) if "/home/claude" in c]
        return any(not LIST_ONLY.match(c) for c in parts)
    return False


def scan_transcript(stream_path, trial_id, rule="b"):
    text = open(stream_path, errors="replace").read()
    hits = []

    def add(kind, detail, exclude_a=True, exclude_b=None):
        exclude_b = exclude_a if exclude_b is None else exclude_b
        hits.append({"trial_id": trial_id, "file": os.path.basename(stream_path), "kind": kind,
                     "detail": detail[:300], "excludes": exclude_b if rule == "b" else exclude_a,
                     "excludes_rule_a": exclude_a, "excludes_rule_b": exclude_b})

    for k, s in canaries().items():
        if s in text:
            add("canary", k)
    for pat in BLINDING:
        for m in set(re.findall(pat, text, flags=re.IGNORECASE)):
            add("blinding", f"{pat} -> {m if isinstance(m, str) else m[0]}")
    for pat in CREDENTIAL_CONTENT:
        if re.search(pat, text):
            add("credential", pat)
    for pat in CREDENTIAL_REF:
        if re.search(pat, text):
            add("credential_ref", pat, exclude_b=False)
    for name, inp in tool_inputs(stream_path):
        raw = json.loads(inp)
        flat = " ".join(str(v) for v in raw.values()) if isinstance(raw, dict) else inp
        for host in set(URL_RE.findall(flat)):
            if host != API_HOST:
                add("url", f"{name}: {host}", exclude_b=False)
        if API_HOST in flat:  # an API call written into a script or command, outside the child's own process
            add("nested", f"{name}: mentions {API_HOST}")
        if _reads_auth(name, raw):
            add("credential_read", f"{name}: {flat[:200]}")
        for p in set(ABS_RE.findall(flat)):
            if p == "/work" or p.startswith("/work/"):
                continue
            if p.startswith(SYSTEM_PREFIXES) or p in ("/", "/proc", "/dev", "/usr", "/tmp"):
                add("path_system", f"{name}: {p}", exclude_a=False)
            else:
                add("path", f"{name}: {p}", exclude_b=False)
        if name == "Bash":
            cmd = raw.get("command", "") if isinstance(raw, dict) else ""
            for pat in NESTED:
                if re.search(pat, cmd):
                    nested = pat not in (r"/home/claude",)  # the credential folder is judged by _reads_auth
                    add("nested" if nested else "credential_ref", f"{pat}: {cmd[:200]}", exclude_b=nested)
    return hits


def scan_file(path):
    hits = []
    try:
        text = open(path, errors="replace").read()
    except IsADirectoryError:
        return hits
    for pat in CREDENTIAL:
        if re.search(pat, text):
            hits.append({"file": path, "kind": "credential", "detail": pat, "excludes": True})
    for k, s in canaries().items():
        if s in text:
            hits.append({"file": path, "kind": "canary", "detail": k, "excludes": True})
    return hits


def blinding_scan_tree(root):
    """I4: no blinding term in any file name, path or text file under root."""
    hits = []
    root = os.path.abspath(root)
    for pat in BLINDING:
        if re.search(pat, os.path.basename(root), flags=re.IGNORECASE):
            hits.append({"file": root, "kind": "blinding_path", "detail": pat})
    for dirpath, dirnames, filenames in os.walk(root):
        for n in dirnames + filenames:
            full = os.path.join(dirpath, n)
            rel = os.path.relpath(full, root)
            for pat in BLINDING:
                if re.search(pat, rel, flags=re.IGNORECASE):
                    hits.append({"file": full, "kind": "blinding_path", "detail": pat})
        for n in filenames:
            full = os.path.join(dirpath, n)
            if n.lower().endswith((".csv", ".txt", ".json", ".md")):
                text = open(full, errors="replace").read()
                for pat in BLINDING:
                    if re.search(pat, text, flags=re.IGNORECASE):
                        hits.append({"file": full, "kind": "blinding_text", "detail": pat})
            elif n.lower().endswith(".png"):
                from PIL import Image
                im = Image.open(full)
                meta = " ".join(f"{k}={v}" for k, v in (im.info or {}).items() if isinstance(v, (str, bytes)))
                for pat in BLINDING:
                    if re.search(pat, meta, flags=re.IGNORECASE):
                        hits.append({"file": full, "kind": "blinding_png_meta", "detail": pat})
    return hits


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["transcripts", "files", "tree"])
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = []
    for p in a.paths:
        if a.mode == "transcripts":
            rows += scan_transcript(p, os.path.basename(p).split("_")[0].split(".")[0])
        elif a.mode == "files":
            rows += scan_file(p)
        else:
            rows += blinding_scan_tree(p)
    df = pd.DataFrame(rows)
    df.to_csv(a.out, index=False)
    print(df.to_string(index=False) if len(df) else "no hits")
    sys.exit(1 if len(df) and df.get("excludes", pd.Series([True] * len(df))).any() else 0)
