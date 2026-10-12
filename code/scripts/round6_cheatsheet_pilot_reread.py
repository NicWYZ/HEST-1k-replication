"""Round 6 cheatsheet track: re-read the C1 pilot's attempts under rule (b).

The C1 memo (section 3.2) keeps the pilot's trials as a high-effort reference
and asks for its attempts to be re-read under the exclusion rule of C2. For
each pilot slot, the first attempt that passes rule (b) is that slot's
reference value, reported beside the value counted under rule (a).

The pilot's transcripts are read from a clone of the private repository
(transcripts/C1_pilot/<id>.jsonl.gz), and their md5s are checked against
results/round6/cheatsheet/C1_pilot/transcripts_md5.csv first.

    python round6_cheatsheet_pilot_reread.py --tx /home/user/hest-r6-data/transcripts/C1_pilot \
        --out results/round6/cheatsheet/C2_grid
Writes pilot_reread_attempts.csv (every attempt, both rules) and
pilot_reference.csv (one row per slot).
"""
import argparse
import gzip
import hashlib
import os
import shutil
import sys
import tempfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round6_cheatsheet_scan as S  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PILOT = os.path.join(REPO, "results/round6/cheatsheet/C1_pilot")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tx", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    m = pd.read_csv(os.path.join(PILOT, "manifest.csv"), dtype=str).fillna("")
    md = pd.read_csv(os.path.join(PILOT, "transcripts_md5.csv"), dtype=str).set_index("trial_id")
    tmp = tempfile.mkdtemp()
    rows = []
    for _, r in m.iterrows():
        gz = os.path.join(a.tx, f"{r.trial_id}.jsonl.gz")
        assert md5(gz) == md.loc[r.trial_id, "md5_gz"], f"md5 of {gz}"
        js = os.path.join(tmp, f"{r.trial_id}.jsonl")
        with gzip.open(gz, "rb") as fi, open(js, "wb") as fo:
            shutil.copyfileobj(fi, fo)
        assert md5(js) == md.loc[r.trial_id, "md5_jsonl"], f"md5 of {js}"
        h = S.scan_transcript(js, r.trial_id)
        rows.append({
            "trial_id": r.trial_id, "slot": r.slot, "attempt": int(r.attempt), "model": r.model, "role": r.role,
            "status_c1": r.status, "rbar": r.rbar, "cost_usd": r.cost_usd, "turns": r.turns, "wall_s": r.wall_s,
            "excluded_rule_a": any(x["excludes_rule_a"] for x in h),
            "excluded_rule_b": any(x["excludes_rule_b"] for x in h),
            "kinds_rule_b": ";".join(sorted({x["kind"] for x in h if x["excludes_rule_b"]})),
            "network_attempts": sum(x["kind"] == "url" for x in h),
            "outside_paths": sum(x["kind"] == "path" for x in h),
            "credential_refs": sum(x["kind"] == "credential_ref" for x in h),
        })
    shutil.rmtree(tmp)
    d = pd.DataFrame(rows)
    # rule (a) as re-read must reproduce the pilot's own statuses
    assert (d["excluded_rule_a"] == (d["status_c1"] == "excluded")).all(), "rule (a) re-read differs from C1"
    os.makedirs(a.out, exist_ok=True)
    d.to_csv(os.path.join(a.out, "pilot_reread_attempts.csv"), index=False)
    ref = []
    for slot, g in d.sort_values("attempt").groupby("slot", sort=False):
        a_ok = g[g["status_c1"] == "done"]
        b_ok = g[~g["excluded_rule_b"] & (g["status_c1"] != "failed")]
        fa = a_ok.iloc[0] if len(a_ok) else None
        fb = b_ok.iloc[0] if len(b_ok) else None
        ref.append({"slot": slot, "model": g["model"].iloc[0], "role": g["role"].iloc[0], "attempts": len(g),
                    "trial_rule_a": fa["trial_id"] if fa is not None else "",
                    "rbar_rule_a": fa["rbar"] if fa is not None else "",
                    "trial_rule_b": fb["trial_id"] if fb is not None else "",
                    "rbar_rule_b": fb["rbar"] if fb is not None else "",
                    "cost_usd_rule_b": fb["cost_usd"] if fb is not None else "",
                    "turns_rule_b": fb["turns"] if fb is not None else "",
                    "wall_s_rule_b": fb["wall_s"] if fb is not None else ""})
    pd.DataFrame(ref).to_csv(os.path.join(a.out, "pilot_reference.csv"), index=False)
    print(pd.DataFrame(ref).to_string(index=False))
