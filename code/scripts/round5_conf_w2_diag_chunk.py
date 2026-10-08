#!/usr/bin/env python
"""Round 5, W2 part 1 diagnostic: the released run_chunk for the first replicates, called directly.

Calls code.marginal.run_true_marginal_latent_intercept_rf_experiments.run_chunk(0, n, 0, config)
unmodified (the function the released launcher submits to its process pool), writes its DataFrame, and
compares it with the same replicates from the wrapper and from a stored round-4 chunk pickle.
Usage: round5_conf_w2_diag_chunk.py --ghcp-code DIR --design fixedN21 --n 2 --out DIR [--pkl FILE]
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round5_conf_w2_wrapper as W  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ghcp-code", required=True)
    p.add_argument("--design", required=True)
    p.add_argument("--n", type=int, default=2)
    p.add_argument("--pkl", default="")
    p.add_argument("--chunk", type=int, default=0)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    os.environ["HCP_PLOTS_MARGINAL"] = os.path.join(a.out, "scratch_paper_results")
    os.environ["HCP_RESULTS_MARGINAL"] = os.path.join(a.out, "scratch_results")
    R = W.load_released(a.ghcp_code)
    c = W.make_ctx(R, a.design, 20)
    cfg = dict(R["LCH"].build_configs(total_replicates=1000, alpha=0.05, gamma=R["LCH"].DEFAULT_GAMMA,
                                      quantile_mode="deterministic", quantile_base_seed=R["LCH"].BASE_SEED)[a.design])
    cfg["alphas"] = list(W.LAUNCHER_ALPHAS)
    cfg["alpha"] = W.LAUNCHER_ALPHAS[0]
    off = a.chunk * W.CHUNK_SIZE[a.design]
    df = R["RFL"].run_chunk(a.chunk, a.n, off, cfg)
    df.to_csv(os.path.join(a.out, "released_run_chunk_first_reps__chunk%d.csv" % a.chunk), index=False)
    if a.pkl:
        old = pd.read_pickle(a.pkl)
        old = old[old.experiment <= off + a.n]
        M = df.merge(old, on=["experiment", "alpha", "o_observed"], suffixes=("_fresh", "_r4"))
        rows = []
        for col in [x for x in old.columns if x.startswith(("coverage", "width"))]:
            x, y = M[col + "_fresh"].to_numpy(float), M[col + "_r4"].to_numpy(float)
            f = np.isfinite(x) & np.isfinite(y)
            rows.append(dict(column=col, n=len(M), max_abs_diff=float(np.max(np.abs(x[f] - y[f]))) if f.any() else 0.0))
        pd.DataFrame(rows).to_csv(os.path.join(a.out, "fresh_vs_round4_pickle__chunk%d.csv" % a.chunk), index=False)
        print(pd.DataFrame(rows).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
