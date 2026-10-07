"""Round 5 PPI, stage E2: two diagnostics for the report, run on Longleaf from E2_regimeB/diag/.

1. Pairing. The classical (rule none) regime B estimate uses only z and the labelled units, which are
   the same in every arm of a task, so its per-gene width should agree across arms. The merge found
   a largest absolute spread of 1.85e-7. This writes the largest relative spread per task and estimand
   and the arms involved (e2_pairing_check.csv), from the units' e2_regimeB_genes files.
2. Theta2 and rare groups. The theta2 weight is 1/pi on the rarer group's units, so a labelled sample
   of m units that misses the rarer group gives a small within-cluster variance estimate exactly when
   the estimate is far from the cluster value. For each tissue task this writes, per m, the mean over
   valid donors of the probability that m units drawn without replacement include no unit of the
   neoplastic-dominant group or none of the stromal-dominant group (hypergeometric, label-free, from
   the design constants of round3_b1_ppi), the median over donors of min(pi_N, pi_S), and beside them
   the classical theta2 coverage_median of the merged grid (e2_theta2_rare_group.csv), with the
   Spearman correlation over (task, m) cells.
"""
import glob

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import gammaln

import round4_ppi_q2_masking as Q2
import round5_ppi_common as C

TISSUE = {"CCRCC": "results/round3/B1_ppi/b1_predictions__CCRCC__hoptimus0.parquet",
          "CCRCC_merged": "results/round3/B1_ppi/b1_predictions__CCRCC_merged__hoptimus0.parquet",
          "INDIANA_KIDNEY": "results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__hoptimus0.parquet",
          "LUNG_XENIUM": "results/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__hoptimus0.parquet"}
M_GRID = (2, 3, 4, 5, 6, 8, 10, 15, 20, 25, 50, 100)


def lchoose(n, k):
    return gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1)


def p_zero(M, K, m):
    """P(no unit of a group of size K among m drawn without replacement from M)."""
    if m > M - K:
        return 0.0
    return float(np.exp(lchoose(M - K, m) - lchoose(M, m)))


def main():
    rows = []
    for f in sorted(glob.glob("../frag_*/**/e2_regimeB_genes__*.csv.gz", recursive=True)):
        if "smoke" in f:
            continue
        g = pd.read_csv(f)
        g = g[g.lambda_rule == "none"][["vtag", "arm", "m", "estimand", "population", "target", "gene", "width"]]
        rows.append(g)
    g = pd.concat(rows, ignore_index=True)
    k = ["vtag", "m", "estimand", "population", "target", "gene"]
    agg = g.groupby(k).width.agg(["min", "max", "count"]).reset_index()
    agg["abs_spread"] = agg["max"] - agg["min"]
    agg["rel_spread"] = agg["abs_spread"] / agg["max"].abs()
    out = agg.groupby(["vtag", "estimand", "population"]).agg(max_abs_spread=("abs_spread", "max"),
                                                               max_rel_spread=("rel_spread", "max"),
                                                               median_width=("max", "median"),
                                                               n_arms=("count", "max")).reset_index()
    out.to_csv("e2_pairing_check.csv", index=False)
    grid = pd.read_csv("../e2_regimeB_grid.csv")
    cl = grid[(grid.lambda_rule == "none") & (grid.estimand == "theta2") & (grid.population == "donor")
              & (grid.target == "design") & (grid.arm == "hoptimus0")]
    rr = []
    for vt, rel in TISSUE.items():
        data = Q2.load(f"{C.ROOT}/{rel}", "hoptimus0", vt)
        G = len(data["donors"])
        c = Q2.B1.design_consts(data["m"], data["neo"], data["didx"], G)
        ok = Q2.B1.unit_valid("theta2", c)
        n = c["n"]
        KN = np.round(c["p_neo"] * n); KS = np.round(c["p_str"] * n)
        pmin = np.minimum(c["p_neo"], c["p_str"])
        for m in M_GRID:
            pm = []
            for gi in np.flatnonzero(ok):
                M_, a, b = int(n[gi]), int(KN[gi]), int(KS[gi])
                mm = min(m, M_)
                pm.append(p_zero(M_, a, mm) + p_zero(M_, b, mm) - p_zero(M_, a + b, mm))
            cov = cl[(cl.vtag == vt) & (cl.m == m)].coverage_median
            rr.append(dict(vtag=vt, m=m, n_valid_donors=int(ok.sum()), mean_p_miss_a_group=float(np.mean(pm)),
                           median_min_pi=float(np.median(pmin[ok])), min_min_pi=float(np.min(pmin[ok])),
                           n_donors_min_pi_below_005=int((pmin[ok] < 0.05).sum()),
                           classical_theta2_coverage_median=float(cov.iloc[0]) if len(cov) else np.nan))
    df = pd.DataFrame(rr)
    rho, p = stats.spearmanr(df.mean_p_miss_a_group, df.classical_theta2_coverage_median)
    df["spearman_over_cells"] = rho
    df["spearman_p"] = p
    df.to_csv("e2_theta2_rare_group.csv", index=False)
    print(out.to_string()); print(df.to_string())


if __name__ == "__main__":
    main()
