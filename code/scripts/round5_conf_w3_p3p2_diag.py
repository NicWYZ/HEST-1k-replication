#!/usr/bin/env python
"""Round 5 conformal track, W3: part 3 at K = 20 against part 2 at K = 20, by CPU model.

Read-only diagnostic for the merge check p3_K20_equals_p2_K20. Reads the w3_full__*.csv.gz of
the p2_* and p3_* unit directories under ROOT (skipping --exclude substrings), keeps K = 20,
attaches each file's cpu_model from the PROVENANCE.txt beside it, matches rows on the merge KEY
and writes OUT/w3_p3p2_by_cpu.csv: per (task, cpu_model_p2, cpu_model_p3) the matched rows, the
largest absolute coverage difference, the largest width_mean and width_median difference in the
merge's metric, and the number of rows whose width differs at all.
Usage: round5_conf_w3_p3p2_diag.py --root W3_real --out DIR [--exclude S ...]
"""
import argparse, glob, os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from round5_conf_w3_merge import KEY, prov_field, wdiff  # noqa: E402


def load(root, prefix, excl):
    out = []
    for f in sorted(glob.glob(os.path.join(root, prefix + "*", "**", "w3_full__*.csv.gz"), recursive=True)):
        if any(e in f for e in excl):
            continue
        d = pd.read_csv(f, dtype={"fold": str})
        d = d[d.K == 20]
        d["cpu_model"] = prov_field(f, "cpu_model")
        out.append(d[KEY + ["coverage", "width_mean", "width_median", "cpu_model"]])
    return pd.concat(out, ignore_index=True)


def main(a):
    os.makedirs(a.out, exist_ok=True)
    p3 = load(a.root, "p3_", a.exclude or [])
    p2 = load(a.root, "p2_", a.exclude or [])
    p2 = p2[p2.task.isin(p3.task.unique())]
    m = p3.merge(p2, on=KEY, suffixes=("_p3", "_p2"))
    m["dcov"] = (m.coverage_p3 - m.coverage_p2).abs()
    m["dw"] = wdiff(m.width_mean_p3, m.width_mean_p2)
    m["dwm"] = wdiff(m.width_median_p3, m.width_median_p2)
    g = m.groupby(["task", "cpu_model_p2", "cpu_model_p3"])
    r = g.agg(rows=("dw", "size"), cov_max=("dcov", "max"), width_mean_max=("dw", "max"),
              width_median_max=("dwm", "max"), rows_width_differs=("dw", lambda x: int((x > 0).sum()))).reset_index()
    r["same_cpu"] = r.cpu_model_p2 == r.cpu_model_p3
    r.to_csv(os.path.join(a.out, "w3_p3p2_by_cpu.csv"), index=False)
    print(f"p3 rows {len(p3)} matched {len(m)}")
    print(r.groupby("same_cpu")[["rows", "rows_width_differs", "cov_max", "width_mean_max", "width_median_max"]]
          .agg({"rows": "sum", "rows_width_differs": "sum", "cov_max": "max", "width_mean_max": "max",
                "width_median_max": "max"}).to_string())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--exclude", action="append")
    main(p.parse_args())
