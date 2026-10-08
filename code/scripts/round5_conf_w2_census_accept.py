#!/usr/bin/env python
"""Round 5 W2 part 2, acceptance check 3: the Longleaf census run against the paper's values.

Agreement rule of round 4 (read from the columns of results/round4/conformal/C3_real/frag_ACS_o/
acs_ghcp_reproduction.csv, whose writing script is not in the repository; the rule is checked against
every row of that file below): a row agrees when |ours - paper| <= half_unit(0.0005 for coverage, 0.5 for width) +
2 sqrt(paper_se^2 + ours_se^2), as in round4_conf_c1_ghcp_compare.py (0.5 * 10^-d for d printed decimals; the paper prints
coverage to 3 decimals and width as integers), and ours_se = sd(ddof 1)/sqrt(n) over the replicates. A paper
value of inf agrees when ours is inf. ours = mean over the 1000 replicates of coverage, and of
width_income (inf if any replicate is infinite, as round 4's Std-CP rows at o = 0 and 5 show).
Released method names: GHCP = Donor-HCP, Pooling CDF = Pooling, Subsampling Once = Subsampling,
Repeated Subsampling = Repeated; HCP and Std-CP keep their names.
"""
import math, os, sys
import numpy as np, pandas as pd
import round5_conf_io as IO

P = sys.argv[1]; out = sys.argv[2]
REF = pd.read_csv("acs_paper_reference.csv")
R4 = pd.read_csv("acs_ghcp_reproduction_round4.csv")
MAP = {"GHCP": "Donor-HCP", "Pooling CDF": "Pooling", "Subsampling Once": "Subsampling",
       "Repeated Subsampling": "Repeated", "HCP": "HCP", "Std-CP": "Std-CP"}
D = {}
for a in ("10", "20"):
    d = f"{P}/released_a{a}/paper-results/acs/results/true_marginal_permuted_rf_income_notrim_yoep2000_alpha{a}"
    D[float(a) / 100] = pd.read_csv(f"{d}/acs_true_marg_alpha{a}_detailed.csv")


def half_unit_metric(metric):
    """The paper prints coverages to 3 decimals and widths as integers (round 4's tolerance column:
    0.0005 for every coverage row, 0.5 for every width row)."""
    return 0.0005 if metric == "coverage" else 0.5


rows = []
for r in REF.itertuples():
    det = D[float(r.alpha)]
    g = det[(det.method == MAP[r.method]) & (det.o == r.o)]
    col = "coverage" if r.metric == "coverage" else "width_income"
    x = g[col].astype(float).to_numpy()
    n = len(x)
    v = float(np.mean(x)) if n else float("nan")
    se = float(np.std(x, ddof=1) / math.sqrt(n)) if n > 1 and np.isfinite(v) else float("nan")
    pv = float(r.value)
    pse = float(r.se) if np.isfinite(r.se) else 0.0
    if math.isinf(pv):
        diff, tol, ok = (0.0 if math.isinf(v) else float("inf")), float("nan"), bool(math.isinf(v))
    else:
        diff = abs(v - pv)
        tol = half_unit_metric(r.metric) + 2 * math.sqrt(pse ** 2 + (se if np.isfinite(se) else 0.0) ** 2)
        ok = bool(np.isfinite(diff) and diff <= tol + 1e-12)
    rows.append(dict(table=r.table, alpha=r.alpha, method=r.method, o=r.o, metric=r.metric, paper=r.value,
                     paper_se=r.se, ours=v, ours_se=se, n_replicates=n, abs_diff=diff, tolerance=tol, within_tolerance=ok))
O = pd.DataFrame(rows)
m = O.merge(R4[["table", "alpha", "method", "o", "metric", "ours", "ours_se", "tolerance"]],
            on=["table", "alpha", "method", "o", "metric"], suffixes=("", "_round4_local"), how="left")
m["ours_minus_round4_local"] = np.where(np.isinf(m.ours) & np.isinf(m.ours_round4_local), 0.0, m.ours - m.ours_round4_local)
# the rule itself: recompute round 4's own tolerance column from its ours_se and compare
chk = R4.copy()
chk["tol_recomputed"] = [half_unit_metric(mt) + 2 * math.sqrt((s if np.isfinite(s) else 0) ** 2 + (o if np.isfinite(o) else 0) ** 2)
                         if np.isfinite(p) and not math.isinf(p) else float("nan")
                         for p, s, o, mt in zip(chk.paper, chk.paper_se, chk.ours_se, chk.metric)]
rule_ok = bool(np.allclose(chk.tol_recomputed.dropna(), chk.tolerance.dropna(), rtol=1e-9))
m.to_csv(os.path.join(out, "w2_census_acceptance_released.csv"), index=False)
print("rows", len(m), "agree", int(m.within_tolerance.sum()), "rule reproduces round-4 tolerance column:", rule_ok)
print("max |ours - round-4 local| / tolerance:", float(np.nanmax(np.abs(m.ours_minus_round4_local) / m.tolerance)))
print(m[~m.within_tolerance].to_string())
IO.stamp(out, "round5-conformal W2 part2", "acceptance 3 table")
IO.write_provenance(out, "W2p2_accept", os.path.abspath(__file__), {"P": P},
                    extra=dict(agree=int(m.within_tolerance.sum()), n=len(m), rule_reproduces_round4_tolerance=rule_ok))
