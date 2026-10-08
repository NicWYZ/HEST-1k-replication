#!/usr/bin/env python
"""Round 5, W2 part 1, acceptance 1: the rerun of the released launchers against round 4.

Reads the summaries the released plot_paper.py wrote into --ours (paper-results/dgp/summaries) and
looks up each T2 and T3 row of round 4's c1_ghcp_reproduction.csv with round 4's own lookup
(round4_conf_c1_ghcp_compare.lookup), then compares the new value with that file's `ours` column at
1e-9. A row that differs is also scored by round 4's agreement rule against the `paper` column,
|ours - paper| <= r + 2 sqrt(se_paper^2 + se_ours^2) with r half a unit of the last printed digit.
It also compares the whole of each summary file, every alpha, o and method including Std-CP, with
round 4's (--r4-summaries-dir), and, if --launcher-raw and --r4-store are given, every column of the
launcher's per-replicate file against the concatenated round-4 chunk pickles.
Usage: round5_conf_w2_accept1.py --ours DIR --r4-repro CSV --r4-summaries-dir DIR --out DIR
"""
import argparse
import glob
import math
import os
import sys
from collections import namedtuple

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_c1_ghcp_compare as CMP  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ours", required=True)
    p.add_argument("--r4-repro", required=True)
    p.add_argument("--r4-summaries-dir", required=True)
    p.add_argument("--launcher-raw", default="")
    p.add_argument("--r4-store", default="")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    R4 = pd.read_csv(a.r4_repro, dtype={"paper": str, "paper_se": str})
    R4 = R4[R4.table.isin(["T2", "T3"])]
    Row = namedtuple("Row", "table design alpha method metric o")
    cache, out = {}, []
    for r in R4.itertuples(index=False):
        v, se = CMP.lookup(a.ours, Row(r.table, r.design, r.alpha, r.method, r.metric, r.o), cache)
        old = float(r.ours)
        same_inf = math.isinf(v) and math.isinf(old)
        d = 0.0 if same_inf else abs(v - old)
        pv = math.inf if str(r.paper).strip().lower() in ("inf", "+inf") else float(r.paper)
        pse = float(r.paper_se) if str(r.paper_se) not in ("nan", "", "None") else 0.0
        diff_p = abs(v - pv)
        tol = CMP.half_unit(r.paper) + 2 * math.sqrt(pse ** 2 + (se if np.isfinite(se) else 0.0) ** 2)
        out.append(dict(table=r.table, design=r.design, alpha=r.alpha, method=r.method, metric=r.metric, o=r.o,
                        round4_ours=old, rerun=v, abs_diff=d, within_1e9=bool(d <= 1e-9),
                        paper=r.paper, abs_diff_paper=diff_p, agreement_tol=tol,
                        agrees_with_paper=bool(diff_p <= tol + 1e-12)))
    O = pd.DataFrame(out)
    O.to_csv(os.path.join(a.out, "w2_accept1_T2_T3.csv"), index=False)
    print("T2/T3 rows", len(O), "within 1e-9:", int(O.within_1e9.sum()), "agree with paper:", int(O.agrees_with_paper.sum()),
          "max abs diff", float(O.abs_diff.max()))
    files = []
    for des in ("fixedN21", "poissonNmean25"):
        new = os.path.join(a.ours, "paper-results", "dgp", "summaries", f"{des}_summary_by_alpha_o_method.csv")
        old = os.path.join(a.r4_summaries_dir, f"ours_{des}_summary_by_alpha_o_method.csv")
        if os.path.exists(new) and os.path.exists(old):
            r = CMP.compare_csv(new, old)
            r["file"] = des
            files.append(r)
    pd.DataFrame(files).to_csv(os.path.join(a.out, "w2_accept1_summary_files.csv"), index=False)
    print(pd.DataFrame(files).to_string())
    if a.launcher_raw and a.r4_store:
        N = pd.read_csv(a.launcher_raw)
        Ofs = sorted(glob.glob(os.path.join(a.r4_store, "e0_w*.pkl")))
        Old = pd.concat([pd.read_pickle(f) for f in Ofs], ignore_index=True)
        keys = ["experiment", "alpha", "o_observed"]
        M = N.merge(Old, on=keys, suffixes=("_new", "_old"))
        rows = []
        for c in [c for c in Old.columns if c not in keys + ["worker_id", "quantile_mode", "gamma"]]:
            x, y = M[c + "_new"].to_numpy(float), M[c + "_old"].to_numpy(float)
            both_inf = np.isinf(x) & np.isinf(y) & (np.sign(x) == np.sign(y))
            m = ~(both_inf | (np.isnan(x) & np.isnan(y)))
            bad = int((np.isnan(x[m]) | np.isnan(y[m]) | np.isinf(x[m]) | np.isinf(y[m])).sum())
            rows.append(dict(column=c, n=len(M), n_inf_or_nan_mismatch=bad,
                             max_abs_diff=float(np.max(np.abs(x[m & np.isfinite(x) & np.isfinite(y)]
                                                              - y[m & np.isfinite(x) & np.isfinite(y)])))
                             if (m & np.isfinite(x) & np.isfinite(y)).any() else 0.0))
        R = pd.DataFrame(rows)
        R.to_csv(os.path.join(a.out, "w2_accept1_raw_columns.csv"), index=False)
        print("raw rows merged", len(M), "of", len(N), len(Old), "max over columns", float(R.max_abs_diff.max()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
