"""Round 5 PPI, stage E3a: identity tests of the corrected interval (theory section 2.0).

No data. Each test prints one row of e3a_tests.csv (test, n_checked, n_pass, worst, tolerance).
  1. identity: the estimator equals T1 - kappa*delta*Delta draw by draw (even and odd n_L).
  2. mean_L (lamL - cU)^2 equals kappa*delta^2 (even and odd n_L).
  3. rule none and a fixed coefficient: |lin|xf variance equals |lin variance exactly.
  4. both halves clipped to the same bound (d = 0): the two variances are equal exactly.
  5. n_L < 6: lambda is 0 on both halves and the two variances are equal exactly.
  6. n_L = G: theta - thetahat = kappa*delta*Delta and the |lin variance is exactly 0.
"""
import csv
import sys
import zlib

import numpy as np

import round4_ppi_estimator as E
import round5_ppi_estimator as R5
from round5_ppi_e1_sim import stats_arrays


def pops(G, k, slope, seed, kappa=2.0):
    rng = np.random.default_rng(seed)
    p = rng.standard_normal((G, k)); xi = rng.standard_normal((G, k))
    return slope * p + 0.5 * xi, kappa + p


def run(G, nL, z, f, rule, d):
    rng = np.random.default_rng(zlib.crc32(f"t|G{G}|nL{nL}|d{d}".encode()))
    L = np.zeros(G, bool); L[rng.choice(G, nL, replace=False)] = True
    Lm = np.broadcast_to(L[:, None], z.shape).copy()
    if rule == "oracle":
        lam = R5.oracle_lambda("donor", z, f, Lm)
    else:
        lam = E.lambda_rule(rule, "donor", stats_arrays(z, f), Lm, ~Lm, seed=f"t|{d}")
    o1 = R5.design_whole_clusters("donor", z, f, Lm, lam, lin=True)
    o2 = R5.design_whole_clusters("donor", z, f, Lm, lam, lin=True, xf=True)
    return L, Lm, lam, o1, o2


def main():
    out = []
    # 1, 2: identity and the mean of squared deviations, rule c_crossfit_design
    worst1 = worst2 = 0.0; n = 0
    for G, nL in ((24, 12), (24, 13), (15, 9), (51, 20)):
        z, f = pops(G, 40, 0.6, G * 100 + nL)
        for d in range(20):
            L, Lm, lam, o1, o2 = run(G, nL, z, f, "c_crossfit_design", d)
            half = lam["strata"]
            A, B = half == 0, half == 1
            nA, nB = A.sum(0), B.sum(0)
            fA = np.where(A, f, 0).sum(0) / nA; fB = np.where(B, f, 0).sum(0) / nB
            delta = lam["lamB"] - lam["lamA"]
            kap = nA * nB / nL ** 2
            zL = np.where(Lm, z, 0).sum(0) / nL; fL = np.where(Lm, f, 0).sum(0) / nL
            T1 = zL - lam["cU"] * (fL - f.mean(0))
            worst1 = max(worst1, np.abs(o1["theta"] - (T1 - kap * delta * (fA - fB))).max())
            dev2 = np.where(Lm, (lam["lamL"] - lam["cU"]) ** 2, 0).sum(0) / nL
            worst2 = max(worst2, np.abs(dev2 - kap * delta ** 2).max())
            n += z.shape[1]
    out += [("1_identity_T1_minus_kappa_delta_Delta", n, n if worst1 < 1e-12 else 0, worst1, 1e-12),
            ("2_mean_sq_dev_equals_kappa_delta2", n, n if worst2 < 1e-12 else 0, worst2, 1e-12)]
    # 3: rule none and the oracle (fixed coefficient)
    worst = 0.0; n = 0
    for rule in ("none", "oracle"):
        for G, nL in ((24, 12), (15, 12)):
            z, f = pops(G, 40, 0.6, 7 + G + nL)
            for d in range(10):
                *_, o1, o2 = run(G, nL, z, f, rule, d)
                worst = max(worst, np.abs(o2["var"] - o1["var"]).max()); n += z.shape[1]
    out.append(("3_none_and_fixed_identical", n, n if worst == 0.0 else 0, worst, 0.0))
    # 4: both halves clipped at 1 (steep slope, little noise)
    worst = 0.0; n = 0; nd0 = 0
    z, f = pops(24, 40, 3.0, 99)
    for d in range(10):
        L, Lm, lam, o1, o2 = run(24, 12, z, f, "c_crossfit_design", d)
        same = lam["lamA"] == lam["lamB"]
        nd0 += int(same.sum())
        if same.any():
            worst = max(worst, np.abs(o2["var"][same] - o1["var"][same]).max())
        n += int(same.sum())
    out.append(("4_equal_halves_identical", n, n if (worst == 0.0 and nd0 > 0) else 0, worst, 0.0))
    # 5: n_L < 6
    worst = 0.0; n = 0
    z, f = pops(24, 40, 0.6, 5)
    for nL in (4, 5):
        for d in range(10):
            L, Lm, lam, o1, o2 = run(24, nL, z, f, "c_crossfit_design", d)
            worst = max(worst, np.abs(o2["var"] - o1["var"]).max(), np.abs(lam["lamL"]).max()); n += z.shape[1]
    out.append(("5_nL_below_6_identical", n, n if worst == 0.0 else 0, worst, 0.0))
    # 6: n_L = G
    worstt = worstv = 0.0; n = 0
    G = 15
    z, f = pops(G, 40, 0.6, 15)
    for d in range(10):
        L, Lm, lam, o1, o2 = run(G, G, z, f, "c_crossfit_design", d)
        half = lam["strata"]; A, B = half == 0, half == 1
        fA = np.where(A, f, 0).sum(0) / A.sum(0); fB = np.where(B, f, 0).sum(0) / B.sum(0)
        kap = A.sum(0) * B.sum(0) / G ** 2
        err = (z.mean(0) - o1["theta"]) - kap * (lam["lamB"] - lam["lamA"]) * (fA - fB)
        worstt = max(worstt, np.abs(err).max()); worstv = max(worstv, np.abs(o1["var"]).max())
        n += z.shape[1]
    out.append(("6_nL_equals_G_error_is_T2", n, n if worstt < 1e-12 else 0, worstt, 1e-12))
    out.append(("6_nL_equals_G_lin_var_zero", n, n if worstv == 0.0 else 0, worstv, 0.0))
    w = csv.writer(sys.stdout)
    w.writerow(["test", "n_checked", "n_pass", "worst", "tolerance"])
    for r in out:
        w.writerow(r)
    with open("e3a_tests.csv", "w", newline="") as fh:
        ww = csv.writer(fh); ww.writerow(["test", "n_checked", "n_pass", "worst", "tolerance"]); ww.writerows(out)
    return 0 if all(r[1] == r[2] for r in out) else 1


if __name__ == "__main__":
    raise SystemExit(main())
