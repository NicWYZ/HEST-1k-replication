#!/usr/bin/env python
"""Round 4 stage P7: the derived numbers docs/round4_data_report.md quotes, computed from cited files.

The numeric-claim gate resolves a quoted value against a cell or a whole-column aggregate of a cited
file. Some values in the report are neither, being a statistic over a subset of rows, or accounting
held in pipe-separated sacct output. This script writes them to results/round4/data/P7_report/
with the formula and source beside each value, so every such number has one file it is read from.

Outputs
  report_numbers.csv    name, value, source, formula
  stageP_sacct.csv      results/round4/data/P7_report/stageP_sacct.psv as CSV, MaxRSS in K as a number
  p6_sacct_lead.csv     results/round4/data/P6_genes/p6_sacct_lead.psv, the same way

Usage, from the repository root:
  python code/scripts/round4_data_report_numbers.py
"""
import os

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "results/round4/data/P7_report")
V5 = ["CCRCC", "PRAD", "READ", "LYMPH_IDC", "HCC"]


def psv_to_csv(src, dst):
    d = pd.read_csv(os.path.join(ROOT, src), sep="|", dtype=str, keep_default_na=False)
    d["MaxRSS_K"] = pd.to_numeric(d.MaxRSS.str.rstrip("K"), errors="coerce")
    d.to_csv(os.path.join(OUT, dst), index=False)
    return d


def main():
    rows = []

    def add(name, value, source, formula):
        rows.append(dict(name=name, value=value, source=source, formula=formula))

    src = "results/round2/R2_fold_hvg/fold_hvg__hoptimus0.csv"
    f = pd.read_csv(os.path.join(ROOT, src))
    f = f[f.task.isin(V5)]
    add("r2_shared_top50_five_visium_mean", round(f.n_genes_shared.mean(), 2), src,
        "mean n_genes_shared over rows with task in CCRCC, PRAD, READ, LYMPH_IDC, HCC")
    add("r2_shared_top50_five_visium_sd", round(f.n_genes_shared.std(), 2), src, "sample sd, same rows")
    add("r2_shared_top50_five_visium_n_folds", len(f), src, "row count, same rows")

    src = "results/round4/data/P6_genes/p6_gene_summary.csv"
    s = pd.read_csv(os.path.join(ROOT, src))
    b = s[s.task != "INDIANA_KIDNEY"]
    add("p6_overlap_top50_benchmark_mean", round(b.overlap_top50_shipped.mean(), 2), src,
        "mean overlap_top50_shipped over the benchmark-task rows (task != INDIANA_KIDNEY)")
    add("p6_overlap_top50_benchmark_sd", round(b.overlap_top50_shipped.std(), 2), src, "sample sd, same rows")
    add("p6_overlap_top50_benchmark_n_folds", len(b), src, "row count, same rows")

    src = "results/round4/data/P1_download/p1_verification.csv"
    v = pd.read_csv(os.path.join(ROOT, src))
    for st in ("lung_xenium", "donor_labelled_v"):
        u = v.loc[v.set == st, "unpatched_fraction"]
        for stat in ("min", "median", "max", "mean"):
            add(f"p1_unpatched_{st}_{stat}", round(float(getattr(u, stat)()), 6), src,
                f"{stat} unpatched_fraction over set == {st}")
        add(f"p1_unpatched_{st}_sd", round(float(u.std()), 6), src, f"sample sd, set == {st}")

    for name, d in (("stageP", psv_to_csv("results/round4/data/P7_report/stageP_sacct.psv", "stageP_sacct.csv")),
                    ("p6", psv_to_csv("results/round4/data/P6_genes/p6_sacct_lead.psv", "p6_sacct_lead.csv"))):
        add(f"{name}_sacct_n_batch_steps", int(d.JobID.str.endswith(".batch").sum()),
            f"results/round4/data/P7_report/{name}_sacct{'_lead' if name == 'p6' else ''}.csv",
            "rows whose JobID ends in .batch")

    os.makedirs(OUT, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "report_numbers.csv"), index=False)
    print(pd.DataFrame(rows)[["name", "value"]].to_string(index=False))


if __name__ == "__main__":
    main()
