#!/usr/bin/env python
"""Round 4 P8: the derived numbers docs/round4_data_P8_report.md quotes, from cited files.

Writes, under results/round4/data/P8_addendum/:
  p8_report_numbers.csv   name, value, source, formula
  p8_sacct.csv            p8_sacct.psv (the lead's sacct query) as CSV, MaxRSS in K as a number

Usage, from the repository root:
  python code/scripts/round4_data_p8_report_numbers.py
"""
import os

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = "results/round4/data/P8_addendum"


def main():
    rows = []

    def add(name, value, source, formula):
        rows.append(dict(name=name, value=value, source=source, formula=formula))

    s = pd.read_csv(os.path.join(ROOT, D, "p8_sacct.psv"), sep="|", dtype=str, keep_default_na=False)
    s["MaxRSS_K"] = pd.to_numeric(s.MaxRSS.str.rstrip("K"), errors="coerce")
    s.to_csv(os.path.join(ROOT, D, "p8_sacct.csv"), index=False)

    src = f"{D}/lung_edge_patches.csv"
    e = pd.read_csv(os.path.join(ROOT, src))
    for col, tag in (("frac_beyond_threshold", "memo"), ("frac_beyond_source_threshold", "source")):
        v = e[col]
        for stat in ("min", "median", "max", "mean"):
            add(f"edge_{tag}_frac_{stat}", round(float(getattr(v, stat)()), 6), src, f"{stat} of {col}, 20 rows")
        add(f"edge_{tag}_frac_sd", round(float(v.std()), 6), src, f"sample sd of {col}")
        add(f"edge_{tag}_n_samples_over_0.10", int((v > 0.10).sum()), src, f"rows with {col} > 0.10")
        add(f"edge_{tag}_n_samples_zero", int((v == 0).sum()), src, f"rows with {col} == 0")
    for mm in (3, 5):
        sub = e[e.core_diameter_mm_source == mm]
        add(f"edge_n_samples_core_{mm}mm", len(sub), src, f"rows with core_diameter_mm_source == {mm}")
        add(f"edge_core_{mm}mm_memo_frac_median", round(float(sub.frac_beyond_threshold.median()), 6), src,
            f"median frac_beyond_threshold over those rows")
        add(f"edge_core_{mm}mm_source_frac_median", round(float(sub.frac_beyond_source_threshold.median()), 6),
            src, "median frac_beyond_source_threshold over those rows")
    add("edge_n_patches_used_total", int(e.n_patches_used.sum()), src, "sum n_patches_used")

    src = f"{D}/p8_subset_after_drop.csv"
    b = pd.read_csv(os.path.join(ROOT, src))
    add("subset_n_samples_holding_after_drop", int(b.subset_holds_after_drop.sum()), src, "rows with subset_holds_after_drop")
    add("subset_n_samples_failing_before_drop", int((b.n_missing_before_drop > 0).sum()), src,
        "rows with n_missing_before_drop > 0")
    add("subset_n_patches_after_drop_total", int(b.n_patches_after_drop.sum()), src, "sum n_patches_after_drop")

    src = "results/round4/data/P5_task/panel_job/lung_genes_by_sample.json"
    import json
    import re
    lung = json.load(open(os.path.join(ROOT, src)))
    td = json.load(open(os.path.join(ROOT, "results/round4/data/P5_task/LUNG_XENIUM.json")))
    panels = {tuple(lung[x["sample_id"]]) for x in td["samples"]}
    assert len(panels) == 1
    feats = next(iter(panels))
    for fam in ("NegControlCodeword", "NegControlProbe", "UnassignedCodeword", "BLANK"):
        add(f"lung_task_n_{fam}", sum(bool(re.match(f"^{fam}", g)) for g in feats), src,
            f"features of the shared member panel whose name starts with {fam}")
    add("lung_task_n_features", len(feats), src, "features of the shared member panel")

    pd.DataFrame(rows).to_csv(os.path.join(ROOT, D, "p8_report_numbers.csv"), index=False)
    print(pd.DataFrame(rows)[["name", "value"]].to_string(index=False))


if __name__ == "__main__":
    main()
