"""L3 exact-enumeration check for question E (round 10, track ledger, 8 November 2026).

Extends checks/mickey_williams_check.py. Every sample of size n from N and every
assignment of the sample to folds is enumerated. Each fold estimator t_k is Mickey's
(1959) t_alpha with the coefficient fitted on the complement of fold k (the other
folds' labelled units) and the difference estimator on fold k for the rest of the
population. The average over folds is T = mean_k t_k.

  C6. Unequal halves (odd n, folds of sizes floor(n/2) and ceil(n/2)): T unbiased, and
      V = mean_k s2_k - mean_k (t_k - T)^2 unbiased for Var(T).
  C7. K = 3 folds: the same two statements.
  C8. What two nonnegative alternatives estimate, as a ratio of expectation to Var(T):
      Vcons = mean_k s2_k (conservative by Cauchy-Schwarz), and round 9's within-half
      plug-in (1 - n/N) s2_w / n with s2_w the residual variance pooled within folds
      (code/scripts/round9_fewcluster_williams.py, v_within).
  C9. Fraction of samples with V < 0, and fraction where V < 0.25 Vcons.

The identity behind C6 and C7: if every t_k has the same mean and E s2_k = Var(t_k),
then E[mean_k s2_k - mean_k (t_k - T)^2] = Var(T), with no condition on the joint law
of the t_k. Run: python3 -I l3_split_variance_check.py
"""
import itertools
import numpy as np


def slope(x, y, rule, n_total):
    if rule == "r5" and n_total < 6:
        return 0.0
    vx = np.var(x, ddof=1)
    b = 0.0 if vx == 0 else np.cov(x, y, ddof=1)[0, 1] / vx
    return float(np.clip(b, 0, 1)) if rule == "r5" else b


def fold_piece(Y, X, fit_idx, est_idx, N, mux, rule, n_total):
    """Mickey's t_alpha with Z_alpha = fit_idx kept as observed, and its classical variance."""
    a, m = len(fit_idx), len(est_idx)
    b = slope(X[fit_idx], Y[fit_idx], rule, n_total)
    e = Y[est_idx] - b * X[est_idx]
    # mean over U \ fit of y estimated by b * mean_{U \ fit} x + mean_est e
    mux_rest = (N * mux - X[fit_idx].sum()) / (N - a)
    rest = b * mux_rest + e.mean()
    t = (Y[fit_idx].sum() + (N - a) * rest) / N
    s2 = ((N - a) / N) ** 2 * (1 - m / (N - a)) * np.var(e, ddof=1) / m
    return t, s2, e


def run(Y, X, n, K, rule):
    N = len(Y); mux = X.mean(); muy = Y.mean()
    sizes = [n // K + (1 if i < n % K else 0) for i in range(K)]
    T, V, VC, VW = [], [], [], []
    for s in itertools.combinations(range(N), n):
        s = np.array(s)
        # every assignment of the n sampled units to folds of the given sizes
        for perm in set(itertools.permutations(sum([[k] * sizes[k] for k in range(K)], []))):
            lab = np.array(perm)
            ts, s2s, es = [], [], []
            for k in range(K):
                t, s2, e = fold_piece(Y, X, s[lab != k], s[lab == k], N, mux, rule, n)
                ts.append(t); s2s.append(s2); es.append(e)
            ts = np.array(ts); s2s = np.array(s2s)
            Tm = ts.mean()
            T.append(Tm)
            V.append(s2s.mean() - ((ts - Tm) ** 2).mean())
            VC.append(s2s.mean())
            sw2 = sum(((e - e.mean()) ** 2).sum() for e in es) / (n - K)
            VW.append((1 - n / N) * sw2 / n)
    T, V, VC, VW = map(np.array, (T, V, VC, VW))
    var = T.var()
    return dict(bias=T.mean() - muy, V_ratio=V.mean() / var, Vcons_ratio=VC.mean() / var,
                Vwithin_ratio=VW.mean() / var, frac_V_negative=(V < 0).mean(),
                frac_V_below_quarter_Vcons=(V < 0.25 * VC).mean())


if __name__ == "__main__":
    rng = np.random.default_rng(20261107)
    pops = {}
    X1 = rng.gamma(2.0, 1.0, 10); pops["nonlinear_N10"] = (np.exp(0.6 * X1) + rng.normal(0, 0.5, 10), X1)
    X2 = rng.normal(5, 1, 12); pops["skewed_N12"] = (0.7 * X2 + rng.lognormal(0, 1, 12), X2)
    X3 = rng.normal(0, 1, 12); Y3 = 0.8 * X3 + rng.normal(0, 0.6, 12); Y3[0] += 4.0
    pops["one_outlier_N12"] = (Y3, X3)
    for name, (Y, X) in pops.items():
        for rule in ("ols", "r5"):
            for n, K in ((6, 2), (7, 2), (8, 2), (9, 2), (9, 3)):
                r = run(Y, X, n, K, rule)
                print(name, rule, f"n={n} K={K}", {k: float(np.round(v, 6)) for k, v in r.items()})
