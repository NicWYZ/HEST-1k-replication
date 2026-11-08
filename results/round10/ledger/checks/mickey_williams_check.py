"""Exact-enumeration check of the oversight chat's reading of Mickey (1959) for question E.

Claims checked, on toy populations, by enumerating every sample of size n from N and
every ordered split of the sample into a first half A (size n/2) and second half B:

  C1. Williams' (1961) k = 2 estimator equals the average over the two orders of the
      halves of Mickey's t_alpha with alpha = n/2 (Mickey eq. 2.2).
  C2. Mickey's t_alpha is design-unbiased (his Theorem), and so is Williams' form.
  C3. s2_A = ((N - a)/N)^2 (1 - (n - a)/(N - a)) s2_{e,B}/(n - a), with e = y - b_A x on B,
      is unbiased for Var(t_alpha) (Mickey eq. 2.6 plus the classical SRSWOR variance).
  C4. V = (s2_A + s2_B)/2 - (t_A - t_B)^2/4 is unbiased for Var(Williams k = 2)
      (Mickey eqs. 4.4 to 4.6 with the two orders of the halves as the orderings).
  C5. Mickey's chain estimator (4.1) with k = 2 pieces and its variance (4.2) are unbiased.

Coefficient rules: unclipped least-squares slope, and round 5's rule (slope clipped to
[0, 1], zero below six clusters). Run: python3 -I mickey_williams_check.py
"""
import itertools
import numpy as np

def slope(x, y, rule, n_total):
    if rule == "r5" and n_total < 6:
        return 0.0
    vx = np.var(x, ddof=1)
    b = 0.0 if vx == 0 else np.cov(x, y, ddof=1)[0, 1] / vx
    return float(np.clip(b, 0, 1)) if rule == "r5" else b

def t_alpha(yA, xA, yB, xB, N, mux, rule, n_total):
    """Mickey (2.2): coefficient from the first alpha draws (A), applied to the rest."""
    a = len(yA); n = a + len(yB)
    y = np.concatenate([yA, yB]); x = np.concatenate([xA, xB])
    b = slope(xA, yA, rule, n_total)
    ybar, xbar = y.mean(), x.mean()
    return ybar - b * (xbar - mux) - a * (N - n) / ((n - a) * N) * (yA.mean() - ybar - b * (xA.mean() - xbar)), b

def s2_single(yA, xA, yB, xB, N, rule, n_total):
    a = len(yA); m = len(yB)
    b = slope(xA, yA, rule, n_total)
    e = yB - b * xB
    return ((N - a) / N) ** 2 * (1 - m / (N - a)) * np.var(e, ddof=1) / m

def williams(yA, xA, yB, xB, N, mux, rule, n_total):
    n = len(yA) + len(yB)
    y = np.concatenate([yA, yB]); x = np.concatenate([xA, xB])
    bA = slope(xA, yA, rule, n_total); bB = slope(xB, yB, rule, n_total)
    bbar = (bA + bB) / 2
    return y.mean() + bbar * (mux - x.mean()) + (1 - n / N) * (bA - bB) * (xA.mean() - xB.mean()) / 4

def run(Y, X, n, rule):
    N = len(Y); mux = X.mean(); muy = Y.mean(); a = n // 2
    TW, VW, TA, SA, maxdiff = [], [], [], [], 0.0
    for s in itertools.combinations(range(N), n):
        s = np.array(s)
        for A in itertools.combinations(range(n), a):
            Am = np.zeros(n, bool); Am[list(A)] = True
            iA, iB = s[Am], s[~Am]
            tA, _ = t_alpha(Y[iA], X[iA], Y[iB], X[iB], N, mux, rule, n)
            tB, _ = t_alpha(Y[iB], X[iB], Y[iA], X[iA], N, mux, rule, n)
            w = williams(Y[iA], X[iA], Y[iB], X[iB], N, mux, rule, n)
            maxdiff = max(maxdiff, abs(w - (tA + tB) / 2))
            sA = s2_single(Y[iA], X[iA], Y[iB], X[iB], N, rule, n)
            sB = s2_single(Y[iB], X[iB], Y[iA], X[iA], N, rule, n)
            TW.append(w); VW.append((sA + sB) / 2 - (tA - tB) ** 2 / 4)
            TA.append(tA); SA.append(sA)
    TW, VW, TA, SA = map(np.array, (TW, VW, TA, SA))
    return dict(C1_maxdiff=maxdiff, C2_bias_W=TW.mean() - muy, C2_bias_tA=TA.mean() - muy,
                C3_ratio=SA.mean() / TA.var(), C4_ratio=VW.mean() / TW.var(),
                C4_frac_negative=(VW < 0).mean(), sd_W=TW.std())

def chain(Y, X, n, rule):
    """C5: t(a1, a2) and t(a2, n) over every ordered sample; (4.2) with k = 2."""
    N = len(Y); mux = X.mean(); muy = Y.mean(); a1, a2 = 3, n - 2
    est, var = [], []
    for s in itertools.permutations(range(N), n):
        s = np.array(s)
        p1, _ = t_alpha(Y[s[:a1]], X[s[:a1]], Y[s[a1:a2]], X[s[a1:a2]], N, mux, rule, n)
        p2, _ = t_alpha(Y[s[:a2]], X[s[:a2]], Y[s[a2:]], X[s[a2:]], N, mux, rule, n)
        tb = (p1 + p2) / 2
        est.append(tb); var.append(((p1 - tb) ** 2 + (p2 - tb) ** 2) / 2)
    est, var = np.array(est), np.array(var)
    return dict(C5_bias=est.mean() - muy, C5_ratio=var.mean() / est.var(), C5_min=var.min())

if __name__ == "__main__":
    rng = np.random.default_rng(20261107)
    pops = {}
    X1 = rng.gamma(2.0, 1.0, 10); pops["nonlinear_N10"] = (np.exp(0.6 * X1) + rng.normal(0, 0.5, 10), X1)
    X2 = rng.normal(5, 1, 12); pops["skewed_N12"] = (0.7 * X2 + rng.lognormal(0, 1, 12), X2)
    for name, (Y, X) in pops.items():
        for rule in ("ols", "r5"):
            for n in (4, 6, 8):
                r = run(Y, X, n, rule)
                print(name, rule, f"n={n}", {k: float(np.round(v, 12)) for k, v in r.items()})
    Y, X = pops["nonlinear_N10"]; Y, X = Y[:8], X[:8]
    for rule in ("ols", "r5"):
        print("nonlinear_N8 chain n=7", rule, {k: float(np.round(v, 12)) for k, v in chain(Y, X, 7, rule).items()})
