#!/usr/bin/env python
"""Round 4, stage P, sub-stage P4: build results/round4/data/P4_audit/donor_audit_r4.csv.

Deterministic and offline. Three inputs, no network, no inference:

  1. results/round3/D3_audit/donor_audit_r3.csv   148 rows, carried through unchanged
  2. results/round4/data/P4_audit/p4_verdicts.csv  24 hand verdicts for set L, from source records
  3. results/round3/D0_inventory/hest_inventory.csv  HEST's own fields, for the hest_* columns
  4. results/round4/data/P1_selection/selection.csv  set membership for sets L and V

Output rows: 148 carried + 24 set-L audited (row_origin expansion_r4)
           + 39 set-V unaudited (row_origin expansion_r4_setv) = 211.

The round-3 columns keep their round-3 order and values. New columns are appended
after them. Run twice and compare sha256; the file must be byte-identical.

Usage: python round4_data_build_audit_r4.py --repo <repo root> --out <output csv>
"""
import argparse
import hashlib
import os
import sys

import pandas as pd

R3_COLS = [
    "row_origin", "task", "sample_id", "hest_patient", "source_url", "donor_statement",
    "donor_id", "donor_label_status", "notes", "hest_dataset_title", "hest_subseries",
    "hest_source_page", "correction", "set_name", "in_benchmark", "lab", "lab_label_status",
    "hest_lab_provisional", "disease", "region", "preservation", "scanner",
    "pixel_size_um_estimated", "pixel_size_um_embedded", "magnification_hest",
    "pixel_size_source", "resolution_uncertain_hest", "resolution_uncertain_rederived",
    "citation",
]

NEW_COLS = [
    "instrument", "instrument_generation", "objective_source", "source_region_name",
    "source_gsm", "source_slide_id", "source_run_date", "pixel_size_um_source",
    "multi_donor_capture_area", "multi_donor_detail", "donor_unit_id",
    "donor_unit_eligible", "contradictions",
]

ALL_COLS = R3_COLS + NEW_COLS


def _read(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False, low_memory=False)


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build(repo, verdicts_path):
    r3 = _read(os.path.join(repo, "results/round3/D3_audit/donor_audit_r3.csv"))
    inv = _read(os.path.join(repo, "results/round3/D0_inventory/hest_inventory.csv"))
    sel = _read(os.path.join(repo, "results/round4/data/P1_selection/selection.csv"))
    ver = _read(verdicts_path)

    assert list(r3.columns) == R3_COLS, "round-3 column order changed"
    assert len(r3) == 148, f"expected 148 round-3 rows, found {len(r3)}"
    assert len(ver) == 24, f"expected 24 verdict rows, found {len(ver)}"

    inv_by_id = inv.set_index("id")
    set_l = sel.loc[sel["set"] == "L", "sample_id"].tolist()
    set_v = sel.loc[sel["set"] == "V", "sample_id"].tolist()
    assert len(set_l) == 24 and len(set_v) == 39, (len(set_l), len(set_v))
    assert sorted(ver["sample_id"]) == sorted(set_l), "verdicts do not cover set L exactly"

    out = [r3.reindex(columns=ALL_COLS, fill_value="")]

    # ---- the 24 set-L rows, audited against source records --------------------
    lung = []
    for sid in sorted(set_l):
        v = ver.loc[ver["sample_id"] == sid].iloc[0]
        h = inv_by_id.loc[sid]
        if sid.startswith("TENX"):
            # TENX118 has a readable CDN run record; TENX141 has no readable source at all,
            # so its source_url is the page HEST cites, which the origin refuses.
            src = ("https://cf.10xgenomics.com/samples/xenium/2.0.0/Xenium_V1_humanLung_Cancer_FFPE/"
                   "Xenium_V1_humanLung_Cancer_FFPE_experiment.xenium"
                   if v["source_region_name"] else h["download_page_link1"])
        else:
            src = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=" + v["source_gsm"]
        lung.append({
            "row_origin": "expansion_r4",
            "task": v["task"],
            "sample_id": sid,
            "hest_patient": h["patient_label"],
            "source_url": src,
            "donor_statement": v["donor_statement"],
            "donor_id": v["donor_id"],
            "donor_label_status": v["donor_label_status"],
            "notes": v["notes"],
            "hest_dataset_title": h["dataset_title"],
            "hest_subseries": h["subseries"],
            "hest_source_page": h["download_page_link1"],
            "correction": "",
            "set_name": "L",
            "in_benchmark": h["in_benchmark"],
            "lab": v["lab"],
            "lab_label_status": v["lab_label_status"],
            "hest_lab_provisional": h["lab_provisional"],
            "disease": v["disease"],
            "region": v["region"],
            "preservation": v["preservation"],
            "scanner": v["scanner"],
            "pixel_size_um_estimated": h["pixel_size_um_estimated"],
            "pixel_size_um_embedded": h["pixel_size_um_embedded"],
            "magnification_hest": h["magnification"],
            "pixel_size_source": v["pixel_size_source"],
            "resolution_uncertain_hest": h["resolution_uncertain"],
            "resolution_uncertain_rederived": "",
            "citation": v["citation"],
            "instrument": v["instrument"],
            "instrument_generation": v["instrument_generation"],
            "objective_source": v["objective_source"],
            "source_region_name": v["source_region_name"],
            "source_gsm": v["source_gsm"],
            "source_slide_id": v["source_slide_id"],
            "source_run_date": v["source_run_date"],
            "pixel_size_um_source": v["pixel_size_um_source"],
            "multi_donor_capture_area": v["multi_donor_capture_area"],
            "multi_donor_detail": v["multi_donor_detail"],
            "donor_unit_id": v["donor_unit_id"],
            "donor_unit_eligible": v["donor_unit_eligible"],
            "contradictions": v["contradictions"],
        })
    out.append(pd.DataFrame(lung, columns=ALL_COLS))

    # ---- the 39 set-V rows, no reading done in this stage ---------------------
    setv = []
    for sid in sorted(set_v):
        h = inv_by_id.loc[sid]
        setv.append({
            "row_origin": "expansion_r4_setv",
            "task": "",
            "sample_id": sid,
            "hest_patient": h["patient_label"],
            "source_url": "",
            "donor_statement": "",
            "donor_id": "",
            "donor_label_status": "unaudited",
            "notes": "set V was downloaded but not read against source records in stage P. "
                     "No track may group by donor on this row without auditing it first.",
            "hest_dataset_title": h["dataset_title"],
            "hest_subseries": h["subseries"],
            "hest_source_page": h["download_page_link1"],
            "correction": "",
            "set_name": "V",
            "in_benchmark": h["in_benchmark"],
            "lab": "",
            "lab_label_status": "unaudited",
            "hest_lab_provisional": h["lab_provisional"],
            "disease": "",
            "region": "",
            "preservation": "",
            "scanner": "",
            "pixel_size_um_estimated": h["pixel_size_um_estimated"],
            "pixel_size_um_embedded": h["pixel_size_um_embedded"],
            "magnification_hest": h["magnification"],
            "pixel_size_source": "",
            "resolution_uncertain_hest": h["resolution_uncertain"],
            "resolution_uncertain_rederived": "",
            "citation": "",
            "instrument": "", "instrument_generation": "", "objective_source": "",
            "source_region_name": "", "source_gsm": "", "source_slide_id": "",
            "source_run_date": "", "pixel_size_um_source": "",
            "multi_donor_capture_area": "", "multi_donor_detail": "",
            "donor_unit_id": "", "donor_unit_eligible": "", "contradictions": "",
        })
    out.append(pd.DataFrame(setv, columns=ALL_COLS))

    df = pd.concat(out, ignore_index=True)[ALL_COLS]
    assert len(df) == 211, len(df)
    assert (df["row_origin"].value_counts().to_dict() ==
            {"expansion_d3": 76, "benchmark_r2": 72, "expansion_r4_setv": 39,
             "expansion_r4": 24}), df["row_origin"].value_counts().to_dict()
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--verdicts", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    df = build(a.repo, a.verdicts)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    # summary first, then the bulk table
    summary_path = os.path.join(os.path.dirname(os.path.abspath(a.out)), "p4_audit_summary.csv")
    summ = (df.groupby(["row_origin", "donor_label_status"], dropna=False)
              .size().reset_index(name="n_rows").sort_values(["row_origin", "donor_label_status"]))
    summ.to_csv(summary_path, index=False, lineterminator="\n")
    df.to_csv(a.out, index=False, lineterminator="\n")

    print(f"rows={len(df)} cols={len(df.columns)}")
    print(f"script_md5={md5(os.path.abspath(__file__))}")
    print(f"out_sha256={sha256(a.out)}")
    print(f"summary={summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
