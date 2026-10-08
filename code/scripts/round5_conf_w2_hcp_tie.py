#!/usr/bin/env python
"""Round 5, W2 part 1: why this track's hcp_q differs from the released HCP in some replicates.

Reads the pooled wrapper rows, lists every (design, chunk, replicate) where this track's `hcp` width
differs from the released HCP's by more than 1e-9, then redraws those replicates with the wrapper's own
stream (round5_conf_w2_wrapper: same seeds, same emulation of the global stream) and, for each, recomputes
the weighted cumulative distribution of the calibration scores the released HCP uses. For each flagged
(replicate, alpha) it records the number of calibration groups, the group sizes, the cumulative mass at
the released threshold and at the previous score, the distance of both from 1 - alpha, and the two
thresholds. The released rule takes the first score whose float cumulative mass is >= 1 - alpha; this
track's wquantile takes the first whose mass is >= (1 - alpha)(1 - QTOL) with QTOL a relative
tolerance, so the two differ only when a cumulative mass equals 1 - alpha up to float error.
Usage: round5_conf_w2_hcp_tie.py --ghcp-code DIR --rows ROWS.csv.gz --design D --out DIR
"""
import argparse
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round5_conf_w2_wrapper as W  # noqa: E402
import round4_conf_sim as SIM  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ghcp-code", required=True)
    p.add_argument("--rows", required=True)
    p.add_argument("--design", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    os.environ["HCP_PLOTS_MARGINAL"] = os.path.join(a.out, "scratch_paper_results")
    os.environ["HCP_RESULTS_MARGINAL"] = os.path.join(a.out, "scratch_results")
    D = pd.read_csv(a.rows)
    D = D[D.design == a.design]
    h = D[D.method == "hcp"].drop_duplicates(["alpha", "experiment"])[["alpha", "experiment", "chunk", "width"]]
    r = D[D.method == "released_hcp"][["alpha", "experiment", "width"]]
    M = h.merge(r, on=["alpha", "experiment"], suffixes=("_mine", "_released"))
    M["diff"] = M.width_mine - M.width_released
    bad = M[~((M.width_mine == M.width_released) | ((M["diff"].abs() <= 1e-9)))]
    summ = dict(design=a.design, n_alpha_replicate=len(M), n_differ=len(bad),
                n_released_wider=int((bad["diff"] < 0).sum()), n_mine_wider=int((bad["diff"] > 0).sum()),
                max_abs_diff=float(bad["diff"].abs().max()) if len(bad) else 0.0)
    pd.DataFrame([summ]).to_csv(os.path.join(a.out, f"w2_hcp_tie_summary__{a.design}.csv"), index=False)
    print(summ)
    if not len(bad):
        return 0
    R = W.load_released(a.ghcp_code)
    c = W.make_ctx(R, a.design, 20)
    n_chunks = int(np.ceil(1000 / W.CHUNK_SIZE[a.design]))
    sizes = R["LCH"].split_counts(1000, n_chunks)
    offsets = np.cumsum([0] + sizes[:-1]).tolist()
    SC, DH, BH = R["SC"], R["DH"], R["BH"]
    rows = []
    for ch in sorted(bad.chunk.unique()):
        want = set(bad[bad.chunk == ch].experiment.astype(int) - offsets[ch])
        np.random.seed(R["LCH"].BASE_SEED + 1000 * int(ch))
        W.install_generators(c)
        for e in range(sizes[ch]):
            cal, test = W.draw_replicate(c)
            Z_cal, U_cal = cal["Z_calibration"], cal["U_calibration"]
            N = np.array([len(z) for z in Z_cal])
            if (e + 1) in want:
                tr, ca = DH.get_hcp_train_cal_split(sample_sizes=list(N), o_observed=0, alpha_selection=0.5)
                mdl = c.mu_baseline["fit_global"](U_matrix=U_cal, Z_list=Z_cal, group_index_vector=tr)
                sl = []
                for j in ca:
                    X = np.array([z["X"] for z in Z_cal[j]]); y = np.array([z["Y"] for z in Z_cal[j]])
                    mu = np.array([c.mu_baseline["predict_global"](mdl, X[i], U_cal[j, :]) for i in range(len(X))])
                    sl.append(np.abs(y - mu))
                K = len(sl)
                s = np.concatenate(sl)
                w = np.concatenate([np.full(len(x), 1.0 / ((K + 1) * len(x))) for x in sl])
                o_ = np.argsort(s, kind="stable")
                cw = np.cumsum(w[o_]) / (w.sum() + 1.0 / (K + 1))
                for al in (0.1, 0.2):
                    t_rel = BH.compute_hcp_interval_radius(sl, al, quantile_mode="deterministic")
                    t_me = SIM.hcp_q(sl, al)
                    if abs(t_rel - t_me) > 1e-9 or True:
                        i_rel = int(np.searchsorted(cw, 1 - al, side="left"))
                        rows.append(dict(design=a.design, chunk=ch, experiment=e + 1 + offsets[ch], alpha=al,
                                         K=K, sizes=";".join(map(str, sorted(len(x) for x in sl))),
                                         released_threshold=t_rel, this_track_threshold=t_me,
                                         cum_at_released_index=float(cw[i_rel]) if i_rel < len(cw) else float("nan"),
                                         cum_before=float(cw[i_rel - 1]) if 0 < i_rel < len(cw) else float("nan"),
                                         one_minus_alpha=1 - al,
                                         dist_released_index=float(cw[i_rel] - (1 - al)) if i_rel < len(cw) else float("nan"),
                                         dist_before=float(cw[i_rel - 1] - (1 - al)) if 0 < i_rel < len(cw) else float("nan")))
                want.discard(e + 1)
            for o in W.LAUNCHER_O:
                for _a in W.LAUNCHER_ALPHAS:
                    W.emulate_sr_draws(R, N, 20, o)
            if not want:
                break
    pd.DataFrame(rows).to_csv(os.path.join(a.out, f"w2_hcp_tie_cases__{a.design}.csv"), index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
