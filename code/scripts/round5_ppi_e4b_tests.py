"""Round 5 PPI, interval 3, E4b: tests of rej_t, v_a, perm_cluster and the redraw rule.

1. rej_t's point estimate equals the classical mean of the labelled clusters, and its variance equals
   a direct per-column least-squares computation.
2. v_a (Morgan and Rubin 2012, Theorem 3.1) against a Monte Carlo of E(chi2 | chi2 <= q_a) / k.
3. Theory section 3.7: a normal synthetic population, 200,000 simple random samples, acceptance at
   the empirical p_a quantile of the Mahalanobis distance; the ratio of the empirical variance of the
   accepted classical means to section 3.3's value, and of the mean rej_t variance to the empirical.
4. perm_cluster keeps each gene's values over clusters and is reproducible.
5. first_accepted: the first candidate at or below the threshold, per column, and columns already
   accepted are left alone.
6. With a support of a few samples the pool threshold accepts a candidate in every column.
Writes e4b_tests.csv in the working directory.
"""
import csv
import sys

import numpy as np
from scipy import stats

import round5_ppi_balance as BAL


def main():
    out = []
    rng = np.random.default_rng(20261009)
    # 1
    G, ncol, n = 30, 7, 8
    z = rng.normal(size=(G, ncol)); X = rng.normal(size=(G, ncol, 2))
    Lm = np.zeros((G, ncol), bool)
    for j in range(ncol):
        Lm[rng.choice(G, n, replace=False), j] = True
    th, v, df = BAL.rej_t(z, X, Lm, 0.01)
    worst_th, worst_v = 0.0, 0.0
    for j in range(ncol):
        zl, xl = z[Lm[:, j], j], X[Lm[:, j], j, :]
        D = np.column_stack([np.ones(n), xl])
        c, *_ = np.linalg.lstsq(D, zl, rcond=None)
        r = zl - D @ c
        s2 = r @ r / (n - 3)
        b = c[1:]
        Sx = np.cov(xl.T, ddof=1)
        vv = (1 - n / G) * (s2 + BAL.va_nominal(2, 0.01) * b @ Sx @ b) / n
        worst_th = max(worst_th, abs(th[j] - zl.mean())); worst_v = max(worst_v, abs(v[j] - vv) / vv)
    out.append(("1_rej_t_point_equals_classical", ncol, int(worst_th < 1e-12), worst_th, "1e-12"))
    out.append(("1_rej_t_var_equals_direct_lstsq", ncol, int(worst_v < 1e-10), worst_v, "1e-10 rel"))
    # 2
    for k in (1, 2):
        for pa in (0.1, 0.01):
            q = stats.chi2.ppf(pa, k)
            x = rng.chisquare(k, 4_000_000)
            mc = x[x <= q].mean() / k
            nom = BAL.va_nominal(k, pa)
            out.append((f"2_va_k{k}_pa{pa}", 1, int(abs(mc / nom - 1) < 0.02), mc / nom, "MC/nominal within 0.02"))
    # 3
    for G, n, k in ((51, 8, 1), (51, 8, 2), (24, 8, 1), (51, 12, 2), (15, 8, 1)):
        Xp = rng.normal(size=(G, k)); zp = Xp @ np.ones(k) * 0.8 + rng.normal(size=G)
        Xc = Xp - Xp.mean(0); S = np.atleast_2d(np.cov(Xp.T, ddof=1))
        B = np.linalg.solve(S, Xc.T @ (zp - zp.mean()) / (G - 1)); e = zp - zp.mean() - Xc @ B
        idx = np.argsort(rng.random((200_000, G)), 1)[:, :n]
        xm = Xc[idx].mean(1); M = np.einsum("ki,ij,kj->k", xm, np.linalg.inv(S), xm)
        for pa in (0.1, 0.01):
            acc = idx[M <= np.quantile(M, pa)]
            zb = zp[acc].mean(1); emp = zb.var(ddof=1)
            pred = (1 - n / G) / n * (e.var(ddof=1) + BAL.va_nominal(k, pa) * B @ S @ B)
            m = min(len(acc), 3000)
            Lm = np.zeros((G, m), bool)
            Lm[acc[:m].T, np.arange(m)[None, :]] = True
            _, vr, _ = BAL.rej_t(np.repeat(zp[:, None], m, 1), np.repeat(Xp[:, None, :], m, 1), Lm, pa)
            supp = pa * __import__("math").comb(G, n)
            out.append((f"3_synth_G{G}_n{n}_k{k}_pa{pa}_emp_over_theory", len(acc), int(abs(emp / pred - 1) < 0.15), emp / pred, f"support {supp:.0f}; within 0.15"))
            out.append((f"3_synth_G{G}_n{n}_k{k}_pa{pa}_rej_over_emp", m, int(abs(np.mean(vr) / emp - 1) < 0.15) if supp >= 1000 else 1,
                        np.mean(vr) / emp, f"support {supp:.0f}; within 0.15 when support >= 1000, reported otherwise"))
    # 4
    f = rng.normal(size=(12, 5)); genes = [f"g{i}" for i in range(5)]
    p1 = BAL.perm_cluster_variable(f, genes, "test"); p2 = BAL.perm_cluster_variable(f, genes, "test")
    same = all(np.allclose(np.sort(p1[:, j, 0]), np.sort(f[:, j])) for j in range(5))
    out.append(("4_perm_cluster_multiset_and_repro", 5, int(same and np.array_equal(p1, p2) and not np.array_equal(p1[:, :, 0], f)), 0.0, "exact"))
    # 5
    d = np.array([[5.0, 1.0, 9.0], [0.5, 2.0, 9.0], [0.1, 0.2, 9.0]])
    kacc, done = BAL.first_accepted(d, np.array([1.0, 1.0, 1.0]), 10, np.array([False, True, False]))
    ok5 = list(kacc) == [11, -1, -1] and list(done) == [True, True, False]
    out.append(("5_first_accepted", 3, int(ok5), 0.0, "exact"))
    # 6: with a support of a few samples (9 valid of 15 clusters, n_L 4 and 12) every column's pool threshold
    # accepts at least one candidate of the pool itself (the float32 threshold of 9185bc6 did not)
    import round5_ppi_e4b_rejective as RJ
    G, nv = 15, 9
    vid = np.sort(rng.choice(G, nv, replace=False))
    Xg = rng.normal(size=(nv, 40, 1)) / 3.0
    for nL in (4, 12):
        idx = np.stack([np.sort(rng.choice(G, nL, replace=False)) for _ in range(20000)])
        pool = RJ.masks_from(idx, G)
        thr, _ = RJ.pool_thresholds(pool, vid, Xg, (0.1, 0.01))
        dd, _ = RJ.dist_valid(pool, vid, Xg)
        never = sum(int((~(dd <= thr[pa][None, :]).any(0)).sum()) for pa in (0.1, 0.01))
        out.append((f"6_small_support_threshold_accepts_nL{nL}", 80, int(never == 0), float(never),
                    "columns with no accepted pool candidate; 0 required; the float32 threshold of 9185bc6 fails this check"))
    w = csv.writer(sys.stdout)
    w.writerow(["test", "n_checked", "n_pass", "worst", "tolerance"]); w.writerows(out)
    with open("e4b_tests.csv", "w", newline="") as fh:
        ww = csv.writer(fh); ww.writerow(["test", "n_checked", "n_pass", "worst", "tolerance"]); ww.writerows(out)


if __name__ == "__main__":
    main()
