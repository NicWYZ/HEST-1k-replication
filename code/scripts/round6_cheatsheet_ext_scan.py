"""Round 6 extension, cheatsheet track: the scanners of instruction 6.6.

Round 6's scanner (round6_cheatsheet_scan.py) with this track's names. Its
functions are used unchanged, under its rule (b), which is the rule 6.6 states.

Transcript scan, after every batch. A session is excluded and rerun only for a
canary string, a sample ID or other blinded name, the token's contents, a
nested `claude` session or direct API call. Network attempts, absolute paths
outside the trial directory and mentions of the token's variable name are
recorded and do not exclude.

Blinded names differ by use. The tree scan (I4, before a trial runs) is strict
and also refuses the task's code and patient numbers. The transcript scan
leaves those two out, because an agent told the tissue is clear cell renal
cell carcinoma may write the abbreviation or "patient 3" by itself.

File scan, before anything is committed or pushed. Token and canary patterns
over cheatsheets, verdicts, prediction files, manifests and reports, plus the
token's literal value.

    python round6_cheatsheet_ext_scan.py transcripts STREAM.jsonl [...] --out hits.csv
    python round6_cheatsheet_ext_scan.py files PATH [...] --out hits.csv
    python round6_cheatsheet_ext_scan.py tree TRIAL_DIR [...] --out hits.csv
"""
import argparse
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round6_cheatsheet_scan as R  # noqa: E402

TOKEN_FILES = ("/private/oauth_token", os.path.expanduser("~/hest-1k/r6ext_private/oauth_token"))
CANARY_STATES = ("/private/canaries.json", os.path.expanduser("~/hest-1k/r6ext_private/canaries.json"))

BLINDING_TRANSCRIPT = [
    r"(?-i:(?<![A-Za-z0-9])INT\d{1,2}(?![0-9]))", r"\bhest\b", r"\bhest[-_ ]?1k\b", r"Meylan", r"Tertiary lymphoid structures generate",
    r"\bGSE\d{5,}\b", r"\bbench_data\b", r"var_50genes", r"\buni_v2\b", r"\bvirchow", r"ffpe_c_\d+",
    r"frozen_[abc]_\d+", r"(?-i:(?<![A-Za-z0-9])[ACGT]{16}-1(?![0-9]))", r"round6ext", r"r6ext",
]
BLINDING_TREE = BLINDING_TRANSCRIPT + [r"(?-i:(?<![A-Za-z0-9])S?CCRCC(?![A-Za-z0-9]))", r"\bpatient[ _-]?\d{1,2}\b", r"(?-i:(?<![A-Za-z0-9])INT(?![A-Za-z0-9]))"]

R.CANARY_STATE = next((p for p in CANARY_STATES if os.path.exists(p)), CANARY_STATES[0])
R.CREDENTIAL_REF = [r"oauth_token", r"CLAUDE_CODE_OAUTH"]
R.CREDENTIAL = R.CREDENTIAL_CONTENT + R.CREDENTIAL_REF
R.NESTED = [r"(^|[\s;&|(`])claude(\s|$)", r"api\.anthropic\.com", r"/usr/local/bin/claude",
            r"/usr/local/lib/node_modules"]


def token():
    for p in TOKEN_FILES:
        if os.path.exists(p):
            return open(p).read().strip()
    return None


def scan_transcript(stream_path, trial_id):
    R.BLINDING = BLINDING_TRANSCRIPT
    hits = R.scan_transcript(stream_path, trial_id, rule="b")
    t = token()
    if t and t in open(stream_path, errors="replace").read():
        hits.append({"trial_id": trial_id, "file": os.path.basename(stream_path), "kind": "token",
                     "detail": "the token's literal value", "excludes": True,
                     "excludes_rule_a": True, "excludes_rule_b": True})
    return hits


def scan_file(path):
    if os.path.isdir(path):
        return [h for d, _, fs in os.walk(path) for f in fs for h in scan_file(os.path.join(d, f))]
    R.CREDENTIAL = R.CREDENTIAL_CONTENT  # a file that names the variable without its value is not a leak
    hits = R.scan_file(path)
    t = token()
    if t and t.encode() in open(path, "rb").read():
        hits.append({"file": path, "kind": "token", "detail": "the token's literal value", "excludes": True})
    return hits


def scan_tree(root):
    R.BLINDING = BLINDING_TREE
    return R.blinding_scan_tree(root)


def write(rows, out):
    cols = sorted({k for r in rows for k in r}) or ["file", "kind", "detail"]
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


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
            rows += scan_tree(p)
    write(rows, a.out)
    kinds = {}
    for r in rows:
        key = (r["kind"], bool(r.get("excludes", True)))
        kinds[key] = kinds.get(key, 0) + 1
    print({f"{k}{'' if e else ' (recorded)'}": n for (k, e), n in sorted(kinds.items())} or "no hits")
    sys.exit(1 if any(r.get("excludes", True) for r in rows) else 0)
