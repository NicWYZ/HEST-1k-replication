#!/usr/bin/env python
"""Round 5, prediction-set track, W4 part B step 5: numerical probe of HCP in the revealed-law model.

docs/round5_conf_theory.md section B.5. The data are K group laws, the target score is one draw
from an unseen (K+1)-th law, and a symmetric method returns a threshold q(D) for the score. By
section B.3 a method is valid for every law on laws iff, for every configuration of K + 1 laws,
  (1/(K+1)) sum_j F_j(q(D_{-j})) >= 1 - alpha.
In this model HCP's threshold is the smallest q with sum_{k in D} F_k(q) >= c, c = (K+1)(1-alpha)
(the test group's mass 1/(K+1) sits at +inf). With continuous laws and K + 1 > 1/alpha it has no
atom to randomise at, so randomised HCP equals HCP.

Checks, each against the closed form derived in B.5:
  a  coverage at disjoint ordered configurations = ceil(c)/(K + 1)
  b  coverage at homogeneous configurations = c/K
  c  for random configurations D0 of K normal laws and x in (q0 - eps, q0), q0 = q_H(D0): the
     leave-one-out thresholds of D0 + delta_x equal x when x is close to q0 (band 'near', q0 - x in
     1e-6..1e-3; checked to the bisection's resolution), and HCP's coverage of D0 + delta_x equals
     (1 + sum_j F_j(x))/(K + 1); a method equal to HCP except q(D0) < x has coverage
     sum_j F_j(x)/(K + 1) < 1 - alpha.
  d  the smallest coverage of HCP over random configurations of K + 1 normal laws (how close to
     1 - alpha the slack goes in that family).
Outputs results/round5/conformal/W4_theory/w4_hcp_pointwise.csv and PROVENANCE.txt.
"""
import argparse
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class Law:
    def __init__(self, kind, a, b=1.0):
        self.kind, self.a, self.b = kind, a, b

    def cdf(self, q):
        if self.kind == "normal":
            return 0.5 * (1.0 + math.erf((q - self.a) / (self.b * math.sqrt(2.0))))
        if self.kind == "uniform":
            return float(np.clip((q - self.a) / (self.b - self.a), 0.0, 1.0))
        return 1.0 if q >= self.a else 0.0          # point mass at a


def hcp_q(laws, c, lo=-1e3, hi=1e3):  # 80 bisection steps: interval width 2e3 / 2**80
    """Smallest q with sum F_k(q) >= c (right-continuous CDFs), by bisection on a monotone step-
    or continuous function; returns +inf when even the total mass falls short."""
    if sum(1.0 for _ in laws) < c - 1e-12:
        return math.inf
    f = lambda q: sum(L.cdf(q) for L in laws)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if f(mid) >= c - 1e-12:
            hi = mid
        else:
            lo = mid
    return hi


def coverage(conf, c, qfun=None):
    K1 = len(conf)
    tot = 0.0
    for j in range(K1):
        D = conf[:j] + conf[j + 1:]
        q = qfun(D) if qfun else hcp_q(D, c)
        tot += conf[j].cdf(q)
    return tot / K1


def main(a):
    rng = np.random.default_rng(20261008)
    rows = []
    for K, alpha in ((10, 0.1), (14, 0.1), (20, 0.1), (10, 0.2), (19, 0.05)):
        c = (K + 1) * (1 - alpha)
        conf = [Law("uniform", 10.0 * i, 10.0 * i + 1) for i in range(K + 1)]
        rows.append(dict(check="a_disjoint", K=K, alpha=alpha, value=coverage(conf, c),
                         closed_form=math.ceil(c - 1e-12) / (K + 1)))
        conf = [Law("normal", 0.0, 1.0) for _ in range(K + 1)]
        rows.append(dict(check="b_homogeneous", K=K, alpha=alpha, value=coverage(conf, c),
                         closed_form=c / K))
        worst_c, worst_gap = 0.0, 0.0
        for t in range(60):
            band = "near" if t % 2 == 0 else "far"
            D0 = [Law("normal", rng.normal(0, 2), math.exp(rng.normal(0, 0.5))) for _ in range(K)]
            q0 = hcp_q(D0, c)
            x = q0 - (10 ** rng.uniform(-6, -3) if band == "near" else 10 ** rng.uniform(-3, -1))
            conf = D0 + [Law("point", x)]
            cov_h = coverage(conf, c)
            sF = sum(L.cdf(x) for L in D0)
            loo = [hcp_q(D0[:j] + D0[j + 1:] + [Law("point", x)], c) for j in range(K)]
            if band == "near":
                worst_c = max(worst_c, abs(cov_h - (1 + sF) / (K + 1)))
                worst_gap = max(worst_gap, max(abs(l - x) for l in loo))
            qB = lambda D, D0=D0, x=x: (x - 1.0) if D is not None and all(d is e for d, e in zip(D, D0)) and len(D) == len(D0) else hcp_q(D, c)
            cov_b = coverage(conf, c, qfun=qB)
            rows.append(dict(check="c_reduced_at_D0", K=K, alpha=alpha, value=cov_b,
                             closed_form=sF / (K + 1), below_level=bool(cov_b < 1 - alpha), t=t, band=band))
        rows.append(dict(check="c_hcp_coverage_formula_max_err", K=K, alpha=alpha, value=worst_c, closed_form=0.0))
        rows.append(dict(check="c_loo_threshold_equals_x_max_err", K=K, alpha=alpha, value=worst_gap, closed_form=0.0))
        mins = []
        for t in range(80):
            spread = 10 ** rng.uniform(-1, 1.5)
            conf = [Law("normal", rng.normal(0, spread), math.exp(rng.normal(0, 0.7))) for _ in range(K + 1)]
            mins.append(coverage(conf, c))
        rows.append(dict(check="d_min_coverage_random_normal_configs", K=K, alpha=alpha,
                         value=float(min(mins)), closed_form=1 - alpha))
    import pandas as pd
    d = pd.DataFrame(rows)
    os.makedirs(a.out, exist_ok=True)
    d.to_csv(os.path.join(a.out, "w4_hcp_pointwise.csv"), index=False)
    import round5_conf_io as IO5
    IO5.write_provenance(a.out, "W4_hcp_pointwise", __file__, dict(seed=20261008),
                         extra=dict(host="local (plan section 5 item 7)"))
    s = d[d.check.isin(["a_disjoint", "b_homogeneous"])]
    print(s.assign(err=(s.value - s.closed_form).abs())[["check", "K", "alpha", "value", "closed_form", "err"]].to_string())
    cc = d[d.check == "c_reduced_at_D0"]
    for bd, g in cc.groupby("band"):
        print("c", bd, ": reduced-method coverage below level in", int(g.below_level.sum()), "of", len(g),
              "; max |value - closed form|", float((g.value - g.closed_form).abs().max()))
    print(d[d.check.str.contains("max_err|min_cov")][["check", "K", "alpha", "value"]].to_string())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    main(p.parse_args())
