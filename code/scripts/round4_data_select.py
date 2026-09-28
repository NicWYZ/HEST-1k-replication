#!/usr/bin/env python
"""Round 4 stage P1: select sets L and V from the HEST-1k inventory, before anything is downloaded.

Source rule: docs/decisions/round4_data_pull.md section 6, P1, transcribed in
docs/round4_data_plan.md section 3.

  Set L, lung Xenium: species human, organ Lung, technology Xenium, not a duplicate.
  Set V, donor-labelled Visium and Xenium: species human; technology exactly Visium or Xenium
    (not Visium HD, not Spatial Transcriptomics; the inventory's separate 'Xenium 5k' label is not
    named by the rule, plan section 7 item 4); patient_label_status usable (the inventory's
    'labelled', which excludes null and whitespace-only labels); not a duplicate; not already on
    disk under bench_data/ (the 72 benchmark samples) or hest_ext/ (round 3 D1's 105, from
    results/round3/D1_download/sample_home_map.csv); not in set L.

Writes results/round4/data/P1_selection/selection.csv (one row per selected sample, with the set and
the reason) and selection_summary.json, then applies the stop-and-report check of plan section 5.
The check exits non-zero, and nothing downloads, if either count is outside its predicted range by
more than a factor of two: set L predicted at 24, set V at 150 to 250.

Reads committed CSVs only. No network.

Usage, from the repository root:  python code/scripts/round4_data_select.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INV = "results/round3/D0_inventory/hest_inventory.csv"
HOME = "results/round3/D1_download/sample_home_map.csv"
OUT = "results/round4/data/P1_selection"
PRED = {"L": (24, 24), "V": (150, 250)}


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def main():
    inv = pd.read_csv(os.path.join(ROOT, INV), low_memory=False)
    home = pd.read_csv(os.path.join(ROOT, HOME))
    assert inv.id.is_unique and len(inv) == 1276, len(inv)
    human = inv.species == "Homo sapiens"
    dup = inv.is_duplicate_of_other_id.astype(bool)
    on_bench = inv.in_benchmark.astype(bool)
    on_ext = inv.id.isin(set(home.sample_id))

    L = inv[human & (inv.organ == "Lung") & (inv.st_technology == "Xenium") & ~dup].copy()
    L["set"] = "L"
    L["reason"] = ("human, organ Lung, technology Xenium, not a duplicate"
                   + L.in_benchmark.map({True: "; also a benchmark LUNG sample (plan section 7 item 1)",
                                         False: ""}))
    assert len(L) == 24, f"set L has {len(L)} samples, expected 24"

    usable = inv.patient_label_status == "labelled"
    tech = inv.st_technology.isin(["Visium", "Xenium"])
    V = inv[human & tech & usable & ~dup & ~on_bench & ~on_ext & ~inv.id.isin(set(L.id))].copy()
    V["set"] = "V"
    V["reason"] = ("human, technology " + V.st_technology + ", patient label usable, not a duplicate, "
                   "not on disk under bench_data/ or hest_ext/, not in set L")

    # counted, not selected: what the literal technology rule leaves out
    x5k = inv[human & (inv.st_technology == "Xenium 5k") & usable & ~dup & ~on_bench & ~on_ext]

    cols = ["set", "id", "organ", "st_technology", "dataset_title", "patient_label",
            "patient_label_status", "donor_key_provisional", "in_benchmark", "benchmark_task",
            "pixel_size_um_estimated", "resolution_uncertain", "bytes_four_components",
            "nfiles_patches", "nfiles_st", "nfiles_cellvit_seg", "nfiles_metadata", "reason"]
    sel = pd.concat([L[cols], V[cols]], ignore_index=True).rename(columns={"id": "sample_id"})
    os.makedirs(os.path.join(ROOT, OUT), exist_ok=True)
    sel.to_csv(os.path.join(ROOT, OUT, "selection.csv"), index=False)

    def block(df):
        return {
            "n_samples": int(len(df)),
            "n_donor_keys": int(df.donor_key_provisional.nunique()),
            "n_missing_label": int((df.patient_label_status != "labelled").sum()),
            "n_in_benchmark": int(df.in_benchmark.astype(bool).sum()),
            "organs": {k: int(v) for k, v in df.organ.value_counts().items()},
            "technologies": {k: int(v) for k, v in df.st_technology.value_counts().items()},
            "n_dataset_titles": int(df.dataset_title.nunique()),
            "pixel_sizes_estimated": sorted(float(round(v, 4)) for v in df.pixel_size_um_estimated.dropna().unique()),
            "n_resolution_uncertain": int(df.resolution_uncertain.astype(bool).sum()),
            "bytes_four_components": int(df.bytes_four_components.sum()),
            "gb_four_components": round(df.bytes_four_components.sum() / 1e9, 2),
        }

    summary = {
        "stage": "round4_P1_selection",
        "inventory": INV, "inventory_md5": md5(os.path.join(ROOT, INV)),
        "home_map": HOME, "home_map_md5": md5(os.path.join(ROOT, HOME)),
        "script_md5": md5(os.path.abspath(__file__)),
        "set_L": block(L), "set_V": block(V),
        "excluded_by_literal_technology_rule_xenium_5k_labelled": int(len(x5k)),
        "predicted": {k: list(v) for k, v in PRED.items()},
    }
    ok = True
    for k, df in (("L", L), ("V", V)):
        lo, hi = PRED[k]
        n = len(df)
        inside2x = (lo / 2) <= n <= (hi * 2)
        summary[f"set_{k}_within_factor_two_of_prediction"] = bool(inside2x)
        ok &= inside2x
    json.dump(summary, open(os.path.join(ROOT, OUT, "selection_summary.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k.startswith("set_") or k.startswith("exc")}, indent=1))
    if not ok:
        sys.exit("STOP AND REPORT: a set count is outside its predicted range by more than a factor of two")


if __name__ == "__main__":
    main()
