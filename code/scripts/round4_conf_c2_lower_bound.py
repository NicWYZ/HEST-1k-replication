#!/usr/bin/env python
"""Round 4, conformal track, stage C2: the numbers behind docs/round4_conf_lower_bound.md.

Two computations, both small enough to run on a laptop; neither touches data.

  beta_star   Proposition 1 of the lower-bound document. For K calibration groups and level
              alpha, beta*(K, alpha) is the largest beta with
                  max_{eps in [0,1]} (1 - eps)^K [eps + beta (1 - eps)] <= alpha.
              Any method valid at 1 - alpha for every hierarchical model then covers at least
              1 - beta* under every model. Written to c2_lb_beta_star.csv.
  switch      The probe of section 5: group laws N(x_j, 1) revealed exactly (N_k -> infinity),
              test group uniform among K + 1 fixed locations (the permutation form of validity,
              section 2). Rule: if the K observed locations span at most d, the pooled quantile of
              their mixture at level 1 - alpha + delta; otherwise HCP. For each (K, d), delta is
              the smallest value (bisection to 2^-14 of 0.1) at which the worst coverage over the
              configuration families below is at least 1 - alpha. One-sided scores. The families
              are m groups shifted by g (m = 1, 2, 3, 5), K + 1 locations evenly spread on [0, g],
              and two halves at 0 and g, for g on a grid of 61 values in [0, 3]. This is evidence
              over those families only, not a validity proof. Written to c2_lb_switch_probe.csv.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def beta_star(K, alpha, n_eps=200001):
    eps = np.linspace(0, 1, n_eps)
    lo, hi = 0.0, alpha
    for _ in range(60):
        b = (lo + hi) / 2
        if np.max((1 - eps) ** K * (eps + b * (1 - eps))) <= alpha:
            lo = b
        else:
            hi = b
    return lo


def q_mix(locs, level, inf_mass=0.0):
    if level / (1 - inf_mass) >= 1:
        return np.inf
    return brentq(lambda q: (1 - inf_mass) * np.mean(stats.norm.cdf(q - locs)) - level, -50, 80)


def cov_rule(x, alpha, d, delta):
    K = len(x) - 1
    tot = 0.0
    for j in range(K + 1):
        obs = np.delete(x, j)
        q = (q_mix(obs, 1 - alpha + delta) if obs.max() - obs.min() <= d
             else q_mix(obs, 1 - alpha, 1 / (K + 1)))
        tot += stats.norm.cdf(q - x[j]) if np.isfinite(q) else 1.0
    return tot / (K + 1)


def configs(K):
    for g in np.linspace(0, 3, 61):
        for m in (1, 2, 3, 5):
            x = np.zeros(K + 1)
            x[:m] = g
            yield f"outliers_m{m}", g, x
        yield "even", g, np.linspace(0, g, K + 1)
        x = np.zeros(K + 1)
        x[:(K + 1) // 2] = g
        yield "halves", g, x


def worst(K, alpha, d, delta):
    w = (2.0, "", np.nan)
    for lab, g, x in configs(K):
        cv = cov_rule(x, alpha, d, delta)
        if cv < w[0]:
            w = (cv, lab, g)
    return w


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--skip-switch", action="store_true")
    a = p.parse_args(argv)
    import round4_conf_io as IO
    os.makedirs(a.out, exist_ok=True)
    rows = []
    for alpha in (0.1, 0.2):
        for K in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 50):
            b = beta_star(K, alpha)
            rows.append(dict(alpha=alpha, K=K, beta_star=b, min_coverage_any_valid=1 - b,
                             forced_overcoverage=alpha - b,
                             hcp_quantile_level=min(1.0, (1 - alpha) * (K + 1) / K),
                             hcp_upper_bound=(1 - alpha) + 2 / (K + 1),
                             hcp_finite=bool(1 / (K + 1) <= alpha + 1e-12)))
    pd.DataFrame(rows).to_csv(f"{a.out}/c2_lb_beta_star.csv", index=False)
    if not a.skip_switch:
        rs = []
        for K in (9, 10, 15, 20):
            for d in (0.25, 0.5, 1.0):
                if worst(K, 0.1, d, 0.0)[0] >= 0.9:
                    dl = 0.0
                else:
                    lo, hi = 0.0, 0.1 - 1e-9
                    for _ in range(14):
                        mid = (lo + hi) / 2
                        if worst(K, 0.1, d, mid)[0] >= 0.9:
                            hi = mid
                        else:
                            lo = mid
                    dl = hi
                w = worst(K, 0.1, d, dl)
                rs.append(dict(K=K, alpha=0.1, d=d, delta_needed=dl, worst_coverage=w[0],
                               worst_family=w[1], worst_g=w[2],
                               pooled_level_used=0.9 + dl,
                               hcp_quantile_level=min(1.0, 0.9 * (K + 1) / K)))
                print(rs[-1], flush=True)
        pd.DataFrame(rs).to_csv(f"{a.out}/c2_lb_switch_probe.csv", index=False)
    IO.write_provenance(a.out, "C2", __file__, dict(stage="C2 lower bound", skip_switch=a.skip_switch),
                        extra={"where": "local laptop, no Slurm job; no data read"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
