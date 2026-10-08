#!/usr/bin/env python
"""Round 5, W2 part 1 item 2: why the released Std-CP is finite in some replicates at o = 5.

The released run_one_experiment (code/shared/dgp/experiments.py lines 525 to 539) calls
_compute_std_cp_interval(x_hist = the first o labelled units, ..., quantile_mode = "randomized").
That function (lines 136 to 279) fits a local random forest on a random half of the o units
(n_train = o // 2, a permutation drawn from rng), computes absolute residuals on the other
n_cal = o - o // 2 units and passes them to _split_conformal_radius (lines 38 to 64), whose randomized
branch appends an infinity atom, gives every atom mass 1/(n_cal + 1), and calls
scores.randomized_weighted_quantile (scores.py lines 127 to 260). When beta = 1 - alpha falls inside
the jump of the infinity atom the quantile is randomized between the largest finite score and
infinity, with probability gamma = (n_cal + 1) beta - n_cal of infinity. So the released Std-CP is
finite with probability 1 - gamma at that (alpha, n_cal) and the finite value is the largest of
the n_cal scores. This script evaluates the released function itself on random scores and prints
the theoretical and empirical probability of an infinite radius for each n_cal, and compares them
with the round-4 counts of infinite Std-CP intervals in a launcher summary file.
Usage: round5_conf_w2_stdcp_check.py --ghcp-code DIR --out DIR [--summary ours_fixedN21_summary.csv]
"""
import argparse
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round5_conf_w2_wrapper as W  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ghcp-code", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--summary", default="")
    p.add_argument("--draws", type=int, default=20000)
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    os.environ["HCP_PLOTS_MARGINAL"] = os.path.join(a.out, "scratch_paper_results")
    os.environ["HCP_RESULTS_MARGINAL"] = os.path.join(a.out, "scratch_results")
    R = W.load_released(a.ghcp_code)
    EXP = R["EXP"]
    rows = []
    for alpha in (0.05, 0.1, 0.15, 0.2):
        for o in (0, 2, 5, 8, 9, 10, 12, 15, 17, 20, 25, 30, 35):
            n_cal = o - o // 2
            if n_cal < 1:
                theo = 1.0
            else:
                b = 1 - alpha
                k = math.ceil((n_cal + 1) * b - 1e-12)
                theo = max(0.0, (n_cal + 1) * b - n_cal) if k > n_cal else 0.0
                theo = min(theo, 1.0)
            rng = np.random.default_rng(1000 + o)
            inf = 0
            maxfin = []
            for i in range(a.draws):
                s = np.abs(rng.standard_normal(max(n_cal, 0)))
                r = EXP._split_conformal_radius(s, alpha, quantile_mode="randomized",
                                                random_seed=None, rng=np.random.default_rng(i))
                inf += int(not np.isfinite(r))
                if n_cal > 0 and np.isfinite(r) and len(maxfin) < 200 and (n_cal + 1) * (1 - alpha) > n_cal:
                    maxfin.append(abs(r - s.max()) < 1e-12)
            row = dict(alpha=alpha, o=o, n_train=o // 2, n_cal=n_cal, p_inf_theory=theo,
                       p_inf_released_function=inf / a.draws,
                       finite_value_is_max_score=(all(maxfin) if maxfin else ""))
            rows.append(row)
    df = pd.DataFrame(rows)
    if a.summary and os.path.exists(a.summary):
        s = pd.read_csv(a.summary)
        s = s[s.method.str.contains("Std", case=False)][["alpha", "o", "method", "width_n_infinite", "width_n_total"]]
        df = df.merge(s.rename(columns={"width_n_infinite": "launcher_summary_n_infinite",
                                        "width_n_total": "launcher_summary_n_total"}),
                      on=["alpha", "o"], how="left")
        df["launcher_summary_p_inf"] = df.launcher_summary_n_infinite / df.launcher_summary_n_total
    df.to_csv(os.path.join(a.out, "w2_stdcp_finiteness.csv"), index=False)
    print(df[df.alpha.isin([0.1, 0.2])].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
