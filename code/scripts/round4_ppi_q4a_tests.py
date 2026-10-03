#!/usr/bin/env python
"""Round 4 PPI, interval 3: unit tests for the design-target lambda rule 'c_crossfit_design'
(Q3 decision memo section 2, plan section 14.2).

T1  each half's lambda equals the clipped least-squares slope (with intercept) of the textbook
    form's donor contributions over that half, computed independently with numpy.polyfit;
T2  the halves are identical to rule (c)'s for the same seed;
T3  lambda = 0 in every column when n_L < 6, so the estimate equals the classical one;
T4  the rule minimises the half's between-donor sample variance of r_g = y_g - lambda x_g over a
    grid of lambda in [0, 1] (to grid resolution), with no unlabelled term;
T5  rule (c)'s lambda is unchanged by the interval-3 edits (compared with a copy of the
    interval-2 formula);
T6  the spot population uses donor totals (Sz_d, Sf_d).
Writes a pass/fail line per test and exits 1 on any failure.
"""
import sys

import numpy as np

import round4_ppi_estimator as E


def synth(G=24, ncol=7, seed=1):
    rng = np.random.default_rng(seed)
    n = rng.integers(50, 400, size=G).astype(float)
    p = rng.normal(size=(G, ncol))
    u = 0.6 * p + rng.normal(scale=0.8, size=(G, ncol))
    t, tf = u + 1.0, p + 0.3
    D = dict(n=np.broadcast_to(n[:, None], (G, ncol)).copy())
    D["Sz"], D["Sf"] = t * D["n"], tf * D["n"]
    D["Szz"], D["Sff"], D["Szf"] = D["Sz"] ** 2 / D["n"], D["Sf"] ** 2 / D["n"], D["Sz"] * D["Sf"] / D["n"]
    return D


def masks(G, ncol, nL, seed=3):
    rng = np.random.default_rng(seed)
    L = np.zeros(G, bool); L[rng.choice(G, nL, replace=False)] = True
    return np.broadcast_to(L[:, None], (G, ncol)).copy(), np.broadcast_to(~L[:, None], (G, ncol)).copy()


def main():
    ok_all = True

    def rep(name, ok, detail=""):
        nonlocal ok_all
        ok_all &= bool(ok)
        print(f"{name}: {'PASS' if ok else 'FAIL'} {detail}")

    D = synth(); G, ncol = D["n"].shape
    Lm, Um = masks(G, ncol, 12)
    for pop in ("donor", "spot"):
        lam = E.lambda_rule("c_crossfit_design", pop, D, Lm, Um, seed="t")
        y, x = (D["Sz"] / D["n"], D["Sf"] / D["n"]) if pop == "donor" else (D["Sz"], D["Sf"])
        half = lam["strata"]
        errs = []
        for h, key in ((0, "lamA"), (1, "lamB")):
            for j in range(ncol):
                idx = half[:, j] == h
                b = np.polyfit(x[idx, j], y[idx, j], 1)[0]
                errs.append(abs(np.clip(b, 0, 1) - lam[key][j]))
        rep(f"T1[{pop}]", max(errs) < 1e-10, f"max |diff| {max(errs):.2e}")
        lc = E.lambda_rule("c_crossfit", pop, D, Lm, Um, seed="t")
        rep(f"T2[{pop}]", np.array_equal(lc["strata"], lam["strata"]))
        grid = np.linspace(0, 1, 2001)
        errs = []
        for h, key in ((0, "lamA"), (1, "lamB")):
            for j in range(ncol):
                idx = half[:, j] == h
                v = [np.var(y[idx, j] - g * x[idx, j], ddof=1) for g in grid]
                errs.append(abs(grid[int(np.argmin(v))] - lam[key][j]))
        rep(f"T4[{pop}]", max(errs) <= 1e-3 + 1e-12, f"max |grid argmin - lambda| {max(errs):.1e}")
    for nL in (4, 5):
        Lm5, Um5 = masks(G, ncol, nL)
        for pop in ("donor", "spot"):
            lam = E.lambda_rule("c_crossfit_design", pop, D, Lm5, Um5, seed="t")
            tb = E.estimate_textbook(pop, D, Lm5, Lm5 | Um5, lam)
            tb0 = E.estimate_textbook(pop, D, Lm5, Lm5 | Um5, E.lambda_rule("none", pop, D, Lm5, Um5))
            rep(f"T3[{pop},nL{nL}]", np.all(lam["lamL"] == 0) and np.allclose(tb["theta"], tb0["theta"], atol=1e-12))
    # T5: interval-2 rule (c) formula, reimplemented
    for pop in ("donor", "spot"):
        lam = E.lambda_rule("c_crossfit", pop, D, Lm, Um, seed="t")
        half = lam["strata"]
        LA, LB = half == 0, half == 1
        if pop == "donor":
            t, tf = E.donor_values(D)
            a_, b_ = E._cluster_lambda_donor(t, tf, LA, Um), E._cluster_lambda_donor(t, tf, LB, Um)
        else:
            a_, b_ = E._cluster_lambda_spot(D, LA, Um), E._cluster_lambda_spot(D, LB, Um)
        rep(f"T5[{pop}]", np.allclose(a_, lam["lamA"]) and np.allclose(b_, lam["lamB"]))
    lam_s = E.lambda_rule("c_crossfit_design", "spot", D, Lm, Um, seed="t")
    lam_d = E.lambda_rule("c_crossfit_design", "donor", D, Lm, Um, seed="t")
    rep("T6", not np.allclose(lam_s["lamA"], lam_d["lamA"]), "(spot totals differ from donor means)")
    print("ALL PASS" if ok_all else "SOME FAILED")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
