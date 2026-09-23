"""Merge the A2 fragments written by the Anatomy and Mechanisms tracks, with collision reporting.

Plan § 12.8: two tracks contribute to `a2_by_stratum.csv` and `a2_prad_donor_sharing.csv`, each
writing a fragment (`__anatomy` / `__spot`, `__paired` / `__arm`). This script concatenates the
fragments, tags every row with its source fragment, and reports any identifying key that appears in
more than one fragment (a collision) or more than once within one fragment (a duplicate). Colliding
rows are kept, not resolved; the report lists them so a human decides.

Usage:
    python code/scripts/round3_a2_merge.py [--dir results/round3/A2_conditional]

Writes, in --dir:
    a2_by_stratum.csv, a2_prad_donor_sharing.csv        merged tables with a `fragment` column
    a2_merge_collisions.csv                             every colliding / duplicated key row
    a2_merge_report.json                                row counts per fragment and per output
"""
import argparse
import json
from pathlib import Path

import pandas as pd

MERGES = {
    "a2_by_stratum.csv": {
        "fragments": ["a2_by_stratum__anatomy.csv", "a2_by_stratum__spot.csv"],
        "base_key": ["task", "label_set", "design", "score", "stratum", "stratum_value", "agg_unit"],
        # The two tracks named the same concepts differently; harmonise before keying.
        # Spot fragment: stratum_kind is the stratum name, scope ('fold' / 'pooled_over_folds')
        # is the aggregation unit.
        "rename": {"a2_by_stratum__spot.csv": {"stratum_kind": "stratum", "scope": "agg_unit"}},
    },
    "a2_prad_donor_sharing.csv": {
        "fragments": ["a2_prad_donor_sharing__paired.csv", "a2_prad_donor_sharing__arm.csv"],
        "base_key": ["level", "task", "label_set", "design", "encoder", "score", "test_slide"],
        # Arm fragment: slide is the held-out test slide, scope ('arm_by_slide' /
        # 'paired_by_slide') plays the role of the paired fragment's level ('pair' / 'summary').
        "rename": {"a2_prad_donor_sharing__arm.csv": {"slide": "test_slide", "scope": "level"}},
    },
}
# Identifier columns that, when a fragment carries them, join the key (e.g. an arm or encoder
# column present in one fragment only). Filled with "" in fragments that lack them.
OPTIONAL_KEY = ["encoder", "arm", "fold", "calibration_unit", "gene", "fold_id", "test_unit", "label"]


def merge_one(d: Path, out_name: str, spec: dict):
    frames, counts, missing = [], {}, []
    for frag in spec["fragments"]:
        p = d / frag
        if not p.exists():
            missing.append(frag)
            continue
        df = pd.read_csv(p, dtype=str, keep_default_na=False)
        ren = spec.get("rename", {}).get(frag, {})
        clash = [new for old, new in ren.items() if old in df.columns and new in df.columns]
        assert not clash, f"{frag}: rename target already present: {clash}"
        df = df.rename(columns=ren)
        df.insert(0, "fragment", frag.split("__", 1)[1].removesuffix(".csv"))
        frames.append(df)
        counts[frag] = len(df)
    if not frames:
        return None, None, {"missing": missing}
    merged = pd.concat(frames, ignore_index=True, sort=False).fillna("")
    key = [c for c in spec["base_key"] if c in merged.columns]
    key += [c for c in OPTIONAL_KEY if c in merged.columns and c not in key]
    dup_any = merged.duplicated(key, keep=False)
    n_frag_per_key = merged.groupby(key, dropna=False)["fragment"].transform("nunique")
    coll = merged[dup_any].copy()
    coll["kind"] = ["cross_fragment" if n > 1 else "within_fragment" for n in n_frag_per_key[dup_any]]
    coll.insert(0, "output", out_name)
    rep = {
        "fragments_present": counts,
        "fragments_missing": missing,
        "renames_applied": spec.get("rename", {}),
        "key": key,
        "rows_out": len(merged),
        "collision_rows_cross_fragment": int((coll["kind"] == "cross_fragment").sum()),
        "collision_rows_within_fragment": int((coll["kind"] == "within_fragment").sum()),
    }
    return merged, coll, rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/round3/A2_conditional")
    a = ap.parse_args()
    d = Path(a.dir)
    report, colls = {}, []
    for out_name, spec in MERGES.items():
        merged, coll, rep = merge_one(d, out_name, spec)
        report[out_name] = rep
        if merged is None:
            continue
        merged.to_csv(d / out_name, index=False)
        if len(coll):
            colls.append(coll)
    (pd.concat(colls, ignore_index=True, sort=False) if colls
     else pd.DataFrame(columns=["output", "kind"])).to_csv(d / "a2_merge_collisions.csv", index=False)
    (d / "a2_merge_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
