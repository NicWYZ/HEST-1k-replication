#!/usr/bin/env python
"""Round 4 P8 item 2: the v2 task-definition extension schema.

Source: docs/decisions/round4_data_P7_decisions.md section 3 item 2, transcribed in
docs/round4_data_plan.md section 9. v2 is the v1 extension schema
(results/round3/D4_expansion/task_defs/task_def_ext.schema.json, which is not modified) with
exactly four additions:
  1. 'expansion_r4' appended to samples[].donor_label_status_row_origin's enum;
  2. an optional per-sample 'slide_id' (string or null);
  3. an optional folds.a4b_k10 key: the K = 10 design's fold-by-draw rows, one object each;
  4. an optional top-level 'dropped_patch_barcodes': sample id -> non-empty list of patch barcodes
     dropped before use (the subset relation is asserted after the drop).
All four are optional, so every definition that validates against v1 still validates against v2;
the script checks that on the committed D4 definitions.

Usage, from the repository root:
  python code/scripts/round4_data_p8_schema_v2.py
"""
import copy
import glob
import importlib.util
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
V1 = "results/round3/D4_expansion/task_defs/task_def_ext.schema.json"
V2 = "results/round3/D4_expansion/task_defs/task_def_ext.schema.v2.json"
D4TD = "code/scripts/round3_d4_task_defs.py"

A4B_ROW = {
    "type": "object",
    "required": ["fold", "cal_draw", "n_pool_donors", "calibration_donors", "training_donors",
                 "calibration_samples", "training_samples"],
    "additionalProperties": False,
    "properties": {
        "fold": {"type": "string"},
        "cal_draw": {"type": "integer", "minimum": 0},
        "n_pool_donors": {"type": "integer", "minimum": 1},
        "calibration_donors": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "training_donors": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "calibration_samples": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "training_samples": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    },
}


def build(v1):
    v2 = copy.deepcopy(v1)
    v2["title"] = v1["title"].replace("version 1", "version 1, extension schema v2") + \
        " (round 4 P8: expansion_r4 row origin, slide_id, folds.a4b_k10, dropped_patch_barcodes)"
    item = v2["properties"]["samples"]["items"]["properties"]
    enum = item["donor_label_status_row_origin"]["enum"]
    assert enum == ["benchmark_r2", "expansion_d3"], enum
    item["donor_label_status_row_origin"]["enum"] = enum + ["expansion_r4"]
    assert "slide_id" not in item
    item["slide_id"] = {"type": ["string", "null"]}
    folds = v2["properties"]["folds"]["properties"]
    assert "a4b_k10" not in folds
    folds["a4b_k10"] = {"type": "array", "items": {"$ref": "#/definitions/a4bRow"}}
    v2["definitions"]["a4bRow"] = A4B_ROW
    assert "dropped_patch_barcodes" not in v2["properties"]
    v2["properties"]["dropped_patch_barcodes"] = {
        "type": "object",
        "additionalProperties": {"type": "array", "items": {"type": "string"}, "minItems": 1}}
    return v2


def main():
    v1 = json.load(open(os.path.join(ROOT, V1)))
    v2 = build(v1)
    with open(os.path.join(ROOT, V2), "w") as f:
        json.dump(v2, f, indent=2)
        f.write("\n")
    spec = importlib.util.spec_from_file_location("d4td", os.path.join(ROOT, D4TD))
    d4 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d4)
    # every committed D4 definition that passes v1 must pass v2
    for p in sorted(glob.glob(os.path.join(ROOT, "results/round3/D4_expansion/task_defs/*.json"))):
        if "schema" in os.path.basename(p):
            continue
        td = json.load(open(p))
        e1, e2 = d4.validate(td, v1), d4.validate(td, v2)
        print(f"{os.path.basename(p)}: v1 errors {len(e1)}, v2 errors {len(e2)}")
        if not e1:
            assert not e2, f"{os.path.basename(p)}: v2 rejects a definition v1 accepts"


if __name__ == "__main__":
    main()
