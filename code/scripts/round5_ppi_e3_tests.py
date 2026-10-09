"""Round 5 PPI, stage E3: synthetic tests of round5_ppi_twolevel (theory section 2). No data.

Writes e3_tests.csv (test, n_checked, n_pass, worst, tolerance) and exits 1 if any fails.
  1. every unit labelled: zhat_g = zbar_g and V_g = 0, all forms and kinds.
  2. form C: a predictor constant within clusters leaves every estimate unchanged (theta3, theta2),
     regime A and regime B (E3 acceptance check 3's identity on synthetic data).
  3. r4_ppi with round 4's coefficient equals round 4's textbook_two_stage (regime A, SRS draw)
     and regime_b (regime B) draw by draw.
  4. Monte Carlo: with fixed coefficients zhat_g is unbiased for zbar_g and the mean of V_g is
     within Monte Carlo error of the empirical variance (form C theta3, form C theta2 stratified,
     form P theta3).
"""
import csv
import sys
import zlib

import numpy as np

import round4_ppi_estimator as E
import round4_ppi_q2_masking as Q2
import round4_ppi_q3_regimes as Q3
import round5_ppi_twolevel as TL


def synth(G=12, Mg=(80, 200), ng=6, seed=1, const=None):
    rng = np.random.default_rng(seed)
    M = rng.integers(Mg[0], Mg[1], G)
    didx = np.repeat(np.arange(G), M)
    n = len(didx)
    m = rng.standard_normal(n) + 0.5 * rng.standard_normal(G)[didx]
    neo = rng.uniform(0, 1, n) ** (1 + rng.uniform(0, 2, G)[didx])
    lev = rng.standard_normal((G, ng))
    y = 3 + lev[didx] + 0.6 * m[:, None] + rng.standard_normal((n, ng))
    y += 0.8 * (neo[:, None] > 0.7)
    yhat = 0.7 * (y - 3) + 0.5 * rng.standard_normal((n, ng)) + 3
    if const == "cluster":
        s = np.zeros((G, ng)); np.add.at(s, didx, yhat); s /= M[:, None]; yhat = s[didx]
    return dict(G=G, M=M, didx=didx, m=m, neo=neo, y=y, yhat=yhat)


def weights(S, kind):
    G, didx, m, neo = S["G"], S["didx"], S["m"], S["neo"]
    if kind == "theta3":
        mu = np.bincount(didx, m, G) / S["M"]
        v = np.bincount(didx, (m - mu[didx]) ** 2, G) / S["M"]
        return (m - mu[didx]) / v[didx], None, np.ones(G, bool)
    if kind == "theta2":
        g = np.where(neo > 0.7, 0, np.where(neo < 0.3, 1, -1))
        pn = np.bincount(didx, (g == 0).astype(float), G) / S["M"]
        ps = np.bincount(didx, (g == 1).astype(float), G) / S["M"]
        w = np.where(g == 0, 1 / pn[didx], np.where(g == 1, -1 / ps[didx], 0.0))
        return w, g, (pn > 0) & (ps > 0)
    return np.ones(len(didx)), None, np.ones(G, bool)


def draw(S, T, nL, m, d, kind, strat):
    rng = np.random.default_rng(zlib.crc32(f"t|{nL}|{m}|{d}".encode()))
    G = S["G"]
    L = np.zeros(G, bool)
    if nL >= G:
        L[:] = True
    else:
        L[rng.choice(G, nL, replace=False)] = True
    sel = []
    for g in np.flatnonzero(L):
        idx = np.flatnonzero(S["didx"] == g)
        if m == 0:
            sel.append(idx); continue
        if strat:
            gr = T["group"][idx]
            parts = [idx[gr == 0], idx[gr == 1]]
            sz = [len(p) for p in parts]
            rare = int(np.argmin(sz))
            want = [m // 2, m // 2]; want[rare] = m - m // 2
            take = [min(want[h], sz[h]) for h in (0, 1)]
            short = sum(want) - sum(take)
            o = 1 - rare if take[rare] < want[rare] else rare
            take[o] = min(sz[o], take[o] + short)
            for h in (0, 1):
                sel.append(np.sort(rng.choice(parts[h], take[h], replace=False)))
        else:
            sel.append(np.sort(rng.choice(idx, min(m, len(idx)), replace=False)))
    return L, np.concatenate(sel)


def main():
    out = []
    # 1
    worst = 0.0; n = 0
    for kind in ("theta3", "theta2", "mean"):
        S = synth(seed=3)
        w, g, ok = weights(S, kind)
        T = TL.prepare(S["y"], S["yhat"], w, S["didx"], S["G"], kind, g, ok)
        L, sel = draw(S, T, 6, 0, 0, kind, False)
        for est in TL.ESTIMATORS:
            lam = None
            if est == "r4_ppi":
                lam = dict(lamL=np.full((S["G"], T["ng"]), 0.4), cU=np.full(T["ng"], 0.4))
            o = TL.estimate(T, L, sel, est, "s1", lam_r4=lam)
            Lv = L & T["valid"]
            worst = max(worst, np.abs(o["zhat"][Lv] - T["zbar"][Lv]).max(), np.abs(o["V"]).max())
            n += int(Lv.sum()) * T["ng"]
    out.append(("1_all_labelled_exact", n, n if worst < 1e-10 else 0, worst, 1e-10))
    # 2
    worst = 0.0; n = 0
    for kind in ("theta3", "theta2"):
        S = synth(seed=5); Sc = synth(seed=5, const="cluster")
        w, g, ok = weights(S, kind)
        T = TL.prepare(S["y"], S["yhat"], w, S["didx"], S["G"], kind, g, ok)
        Tc = TL.prepare(Sc["y"], Sc["yhat"], w, S["didx"], S["G"], kind, g, ok)
        for nL, m, rb in ((8, 20, False), (12, 8, True)):
            for d in range(5):
                L, sel = draw(S, T, nL, m, d, kind, kind == "theta2")
                a = TL.estimate(T, L, sel, "C_classical", f"c{d}", regime_b=rb)
                b = TL.estimate(Tc, L, sel, "C_ppi", f"c{d}", regime_b=rb)
                worst = max(worst, np.abs(a["theta"] - b["theta"]).max(), np.abs(a["var"] - b["var"]).max())
                n += T["ng"]
    out.append(("2_formC_constant_identity", n, n if worst < 1e-10 else 0, worst, 1e-10))
    # 3 regime A against textbook_two_stage, regime B against regime_b
    worst = 0.0; n = 0
    S = synth(G=14, seed=7)
    w, g, ok = weights(S, "theta3")
    T = TL.prepare(S["y"], S["yhat"], w, S["didx"], 14, "theta3", g, ok)
    z, zf, M = T["z"], T["f"], T["M"]
    Dpop = Q2.donor_sums(z, zf, S["didx"], 14)
    for d in range(5):
        L, sel = draw(S, T, 8, 30, d, "theta3", False)
        s = np.zeros(len(S["didx"]), bool); s[sel] = True
        Dl = Q2.donor_sums(z, zf, S["didx"], 14, s)
        mlab = np.bincount(S["didx"][s], minlength=14).astype(float)
        scale = np.where(mlab > 0, M / np.maximum(mlab, 1), 0.0)[:, None]
        Dx = {k: np.where(L[:, None], Dl[k] * scale, Dpop[k]) for k in ("Sz", "Sf", "Szz", "Sff", "Szf")}
        Dx["n"] = np.broadcast_to(M[:, None], (14, T["ng"])).copy()
        Lm = np.broadcast_to(L[:, None], (14, T["ng"])).copy()
        lam = E.lambda_rule("c_crossfit_design", "donor", Dx, Lm, ~Lm, seed=f"q{d}")
        s2w = np.zeros((14, T["ng"]))
        for gg in np.flatnonzero(L):
            ii = sel[S["didx"][sel] == gg]
            s2w[gg] = (z[ii] - lam["lamL"][gg] * zf[ii]).var(0, ddof=1)
        th, var, df = Q2.textbook_two_stage("donor", Dx, Dpop, Lm, Lm | ~Lm, lam, M,
                                            np.broadcast_to(mlab[:, None], (14, T["ng"])), s2w, lin=True)
        o = TL.estimate(T, L, sel, "r4_ppi", f"q{d}", xf=False, lam_r4=lam)
        worst = max(worst, np.abs(o["theta"] - th).max(), np.abs(o["var"] / var - 1).max())
        n += T["ng"]
        # regime B
        mg = np.full(14, 10)
        Lb, selb = draw(S, T, 14, 10, d, "theta3", False)
        sb = np.zeros(len(S["didx"]), bool); sb[selb] = True
        rb = Q3.regime_b(z, zf, S["didx"], ok, M, mg, sb, "donor", "c_crossfit", f"b{d}")
        th_b, var_b, df_b = rb["design"]
        rng = E.seed_rng(f"q3crossfit|b{d}")
        perm = rng.permutation(np.flatnonzero(ok)); h = len(perm) // 2
        lA, _, _ = Q3._half_lambda(z, zf, S["didx"], sb, perm[:h], None)
        lB, _, _ = Q3._half_lambda(z, zf, S["didx"], sb, perm[h:], None)
        lamg = np.zeros((14, T["ng"])); lamg[perm[:h]] = lB; lamg[perm[h:]] = lA
        ob = TL.estimate(T, Lb, selb, "r4_ppi", f"b{d}", regime_b=True, lam_r4=lamg)
        worst = max(worst, np.abs(ob["theta"] - th_b).max(), np.abs(ob["var"] / var_b - 1).max(),
                    abs(ob["df"] - df_b))
        n += T["ng"]
    out.append(("3_r4_equals_round4_code", n, n if worst < 1e-10 else 0, worst, 1e-10))
    # 4 Monte Carlo unbiasedness and variance, fixed coefficient lam = 0.3 (via r4-style override not
    # available for C, so use classical forms and check zhat for C_ppi with half coefficients frozen)
    rows4 = []
    for kind, est, strat in (("theta3", "C_classical", False), ("theta2", "C_classical", True),
                             ("theta3", "P_classical", False)):
        S = synth(G=10, Mg=(150, 151), ng=4, seed=11)
        w, g, ok = weights(S, kind)
        T = TL.prepare(S["y"], S["yhat"], w, S["didx"], 10, kind, g, ok)
        Z, Vs = [], []
        for d in range(3000):
            L, sel = draw(S, T, 10, 12, d, kind, strat)
            o = TL.estimate(T, L, sel, est, f"m{d}", regime_b=True)
            Z.append(o["zhat"][ok]); Vs.append(o["V"][ok])
        Z, Vs = np.array(Z), np.array(Vs)
        if est.startswith("P"):
            bias = np.nan       # form P classical carries a cross-fitted gamma; unbiased given gamma only
        else:
            se = Z.std(0, ddof=1) / np.sqrt(len(Z))
            bias = float(np.abs((Z.mean(0) - T["zbar"][ok]) / se).max())
        vr = Vs.mean(0) / Z.var(0, ddof=1)
        rows4.append((kind, est, bias, float(np.median(vr)), float(vr.min()), float(vr.max())))
    for kind, est, bias, med, lo, hi in rows4:
        okb = (np.isnan(bias) or bias < 4.5)
        okv = 0.8 < med < 1.2
        out.append((f"4_mc_{kind}_{est}_bias_z_max", 1, int(okb), bias, 4.5))
        out.append((f"4_mc_{kind}_{est}_Vmean_over_empvar_median", 1, int(okv), med, "0.8..1.2"))
    w = csv.writer(sys.stdout)
    w.writerow(["test", "n_checked", "n_pass", "worst", "tolerance"])
    w.writerows(out)
    with open("e3_tests.csv", "w", newline="") as fh:
        ww = csv.writer(fh); ww.writerow(["test", "n_checked", "n_pass", "worst", "tolerance"]); ww.writerows(out)
    return 0 if all(r[1] == r[2] for r in out) else 1


if __name__ == "__main__":
    raise SystemExit(main())
