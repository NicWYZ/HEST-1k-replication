"""Round 7 inference track: S1's synthetic test (track document S1.2) and Broska and Howes's two checks (section 2.3).

--part s1 writes s1_tests.csv and s1_tests_cells.csv; --part bh writes bh_tests.csv. Theory sections 1 and 2.1.

s1. Round 5's test 3 population (z = 0.8 * 1'x + e, normal, theory section 3.7 of round 5) and, beside it, a skewed
    population (x lognormal, centred), at (G, n, k) in {(51, 8, 1), (51, 8, 2), (24, 8, 1), (15, 6, 2)} and p_a in
    {0.1, 0.01}. Threshold: the empirical p_a quantile of the distance over 200,000 simple random samples. Inclusion
    probabilities: 1,000,000 accepted samples (pi_stream), and exactly by enumeration where C(G, n) <= 3,000,000.
    Evaluation: 20,000 accepted samples from an independent stream.
    A. HT is unbiased within Monte Carlo error: |mean - theta| <= 3 sd / sqrt(D), with exact pi where available and
       simulated pi otherwise (both reported).
    B. The mean of the SYG variance estimate (simulated pi_gh) is within 0.10 of the empirical variance of HT,
       relative, where the support p_a C(G, n) is at least 1,000; reported otherwise. Hajek and the two
       approximations are reported beside it.
    C. Simulated against exact pi_g: largest |pi_hat - pi| / se.
    D. Under simple random selection with exact pi, HT, Hajek and their SYG variances equal the classical mean and
       (1 - n/G) s^2 / n to 1e-12.
bh. 1. Clusters of size one, i.i.d.: the variance of bh() (equations 6, 7, 9, 12) equals bh_direct() (example 1) to
       1e-10 relative, over 200 data sets, with an encoder-like predictor and with a constant one (lambda 0).
    2. Their assumptions with G large: clusters drawn i.i.d., whole clusters labelled by independent Bernoulli(0.2),
       superpopulation target; coverage of the 90% interval over 4,000 replicates within 3 Monte Carlo se of 0.90.
"""
import argparse
import math

import numpy as np
import pandas as pd

import round7_ppi_weighting as W


def pop(G, k, law, rng):
    if law == "normal":
        Xp = rng.normal(size=(G, k))
    else:
        Xp = rng.lognormal(0.0, 0.94, size=(G, k)); Xp = Xp - Xp.mean(0)
    z = Xp @ np.ones(k) * 0.8 + rng.normal(size=G)
    return z, Xp


def part_s1():
    rows, cells = [], []
    for (G, n, k) in ((51, 8, 1), (51, 8, 2), (24, 8, 1), (15, 6, 2)):
        for law in ("normal", "skewed"):
            rng = np.random.default_rng(W.seed_of(f"r7ppi|S1test|pop|G{G}|n{n}|k{k}|{law}"))
            z, Xp = pop(G, k, law, rng)
            X = Xp[:, None, :]
            vid = np.arange(G)
            dist = W.Dist(X, vid, G)
            poolrng = np.random.default_rng(W.seed_of(f"r7ppi|S1test|pool|G{G}|n{n}|k{k}|{law}"))
            Mpool = dist(W.srs_idx(poolrng, G, n, 200_000))[:, 0]
            for pa in (0.1, 0.01):
                thr = np.array([np.quantile(Mpool, pa)])
                supp = pa * math.comb(G, n)
                tag = f"G{G}_n{n}_k{k}_{law}_pa{pa}"
                st = W.pi_stream(X, vid, G, thr, n, 1_000_000, f"r7ppi|S1test|pi|{tag}")
                pi_s, se_s, pgh_s = W.from_counts(st)
                exact = math.comb(G, n) <= 3_000_000
                if exact:
                    pi_e, pgh_e, nacc = W.pi_exact(X, vid, G, thr, n)
                    worst = float(np.max(np.abs(pi_s - pi_e) / np.maximum(se_s, 1e-12)))
                    offe = ~np.eye(G, dtype=bool)
                    zsh = float((pgh_e[0][offe] <= 0).mean())
                    rows.append(dict(test="C_pi_sim_vs_exact", cell=tag, value=worst, tolerance="<= 4.5",
                                     passed=worst <= 4.5, note=f"exact accepted set {int(nacc[0])}; share of pairs with exact pi_gh = 0: {zsh:.4f}"))
                    cells.append(dict(cell=tag, pi="exact", estimator="-", part="share_pairs_exact_pgh_zero", value=zsh))
                # evaluation draws
                erng_pref = f"r7ppi|S1test|eval|{tag}"
                acc = []
                i = 0
                while sum(len(a) for a in acc) < 20000:
                    r = np.random.default_rng(W.seed_of(f"{erng_pref}|b{i}"))
                    C = W.srs_idx(r, G, n, 50000)
                    acc.append(C[dist(C)[:, 0] <= thr[0] * (1 + W.TOL)]); i += 1
                C = np.concatenate(acc)[:20000]
                D = len(C)
                L = np.zeros((D, G, 1), bool)
                L[np.arange(D)[:, None], C, 0] = True
                theta = z.mean()
                zz = z[:, None]
                va = W.BAL.va_nominal(k, pa)
                pis = {"sim": (pi_s, pgh_s)}
                if exact:
                    pis["exact"] = (pi_e, pgh_e)
                for pnm, (pi, pgh) in pis.items():
                    pghs = {"sim_pgh": pgh, "apx_size": W.fix_nonpositive(W.pgh_apx_size(pi))[0],
                            "apx_bal": W.fix_nonpositive(W.pgh_apx_bal(pi, X, va))[0]}
                    if pnm == "exact":
                        pghs = {"exact_pgh": pgh_e, "apx_size": pghs["apx_size"], "apx_bal": pghs["apx_bal"]}
                    out = W.weighted(zz, zz * 0, L, pi, pghs, fixed_size=True)
                    cl = np.where(L[:, :, 0], z[None, :], np.nan)
                    cmean = np.nanmean(cl, 1)
                    for est in ("HT", "H"):
                        th = out[est]["theta"][:, 0]
                        sd = th.std(ddof=1)
                        bz = (th.mean() - theta) / (sd / math.sqrt(D))
                        cells.append(dict(cell=tag, pi=pnm, estimator=est, part="bias", value=bz, emp_var=sd ** 2))
                        if est == "HT":
                            rows.append(dict(test="A_HT_unbiased", cell=tag + f"_{pnm}", value=float(bz),
                                             tolerance="|z| <= 3", passed=abs(bz) <= 3,
                                             note=f"classical z {(cmean.mean() - theta) / (cmean.std(ddof=1) / math.sqrt(D)):.2f}"))
                        for vnm, v in out[est]["var"].items():
                            ratio = float(np.mean(v[:, 0]) / sd ** 2)
                            cells.append(dict(cell=tag, pi=pnm, estimator=est, part=f"var_{vnm}", value=ratio,
                                              emp_var=sd ** 2, support=supp))
                            if est == "HT" and vnm == "sim_pgh":
                                rows.append(dict(test="B_SYG_mean_over_emp", cell=tag, value=ratio,
                                                 tolerance="within 0.10 when support >= 1000",
                                                 passed=(abs(ratio - 1) <= 0.10) if supp >= 1000 else True,
                                                 note=f"support {supp:.0f}" + ("" if supp >= 1000 else ", reported only")))
                    cells.append(dict(cell=tag, pi=pnm, estimator="classical", part="bias",
                                      value=float((cmean.mean() - theta) / (cmean.std(ddof=1) / math.sqrt(D))),
                                      emp_var=float(cmean.var(ddof=1))))
                    if pnm == "sim":
                        off = ~np.eye(G, dtype=bool)
                        cnt = pgh_s[0][off] * st["R"]
                        cells.append(dict(cell=tag, pi=pnm, estimator="-", part="min_pair_count", value=float(cnt.min())))
                        cells.append(dict(cell=tag, pi=pnm, estimator="-", part="pi_ratio_min",
                                          value=float(pi_s.min() / (n / G))))
                        cells.append(dict(cell=tag, pi=pnm, estimator="-", part="pi_ratio_max",
                                          value=float(pi_s.max() / (n / G))))
                        if exact:
                            for vnm in ("apx_size", "apx_bal"):
                                P = pghs[vnm][0][off]
                                cells.append(dict(cell=tag, pi=pnm, estimator="-", part=f"pgh_{vnm}_rel_err_median",
                                                  value=float(np.median(np.abs(P / pgh_e[0][off] - 1)))))
                print(tag, flush=True)
    # D. simple random identity
    rng = np.random.default_rng(W.seed_of("r7ppi|S1test|srs_identity"))
    worst = 0.0
    for (G, n) in ((24, 8), (51, 4), (15, 12)):
        z = rng.normal(size=(G, 5))
        D = 300
        L = np.zeros((D, G, 5), bool)
        for d in range(D):
            for j in range(5):
                L[d, rng.choice(G, n, replace=False), j] = True
        pi = np.full((G, 5), n / G)
        P = np.full((5, G, G), n * (n - 1) / (G * (G - 1)))
        for j in range(5):
            np.fill_diagonal(P[j], 0)
        out = W.weighted(z, z * 0, L, pi, {"exact": P}, fixed_size=True)
        zl = np.where(L, z[None], np.nan)
        cm = np.nanmean(zl, 1)
        cv = (1 - n / G) * np.nanvar(zl, 1, ddof=1) / n
        for est in ("HT", "H"):
            worst = max(worst, np.max(np.abs(out[est]["theta"] - cm)), np.max(np.abs(out[est]["var"]["exact"] - cv) / cv))
    rows.append(dict(test="D_srs_identity", cell="G24n8,G51n4,G15n12", value=float(worst), tolerance="<= 1e-12",
                     passed=worst <= 1e-12, note="max abs theta diff and max relative var diff"))
    pd.DataFrame(rows).to_csv("s1_tests.csv", index=False, float_format="%.10g")
    pd.DataFrame(cells).to_csv("s1_tests_cells.csv", index=False, float_format="%.10g")
    print(pd.DataFrame(rows).to_string())


def part_bh():
    rows = []
    rng = np.random.default_rng(W.seed_of("r7ppi|S2test|bh1"))
    worst, worst_c = 0.0, 0.0
    for rep in range(200):
        G = int(rng.integers(50, 2000))
        xi = rng.random(G) < rng.uniform(0.05, 0.6)
        if xi.sum() < 3 or (~xi).sum() < 3:
            continue
        f = rng.normal(size=G); z = 0.7 * f + rng.normal(size=G) * rng.uniform(0.2, 2)
        for kind, ff in (("encoder", f), ("constant", np.full(G, 1.3))):
            o = W.bh(z[:, None], ff[:, None], xi[None, :, None])
            lam = float(o["lam"][0, 0]); n = xi.sum()
            th_d, s2_d = W.bh_direct(z, ff, xi, lam)
            s2_bh = float(o["se"][0, 0]) ** 2 * n
            rel = abs(s2_bh - s2_d) / s2_d
            worst = max(worst, rel, abs(float(o["theta"][0, 0]) - th_d))
            if kind == "constant":
                worst_c = max(worst_c, abs(lam))
    rows.append(dict(test="bh_check1_example1_identity", value=worst, tolerance="<= 1e-10", passed=worst <= 1e-10,
                     note="200 i.i.d. data sets, sizes 50-2000; max relative variance difference and max |theta diff|"))
    rows.append(dict(test="bh_constant_predictor_lambda_zero", value=worst_c, tolerance="== 0", passed=worst_c == 0,
                     note="Sigma_22 = 0 sets lambda to 0"))
    # 2. coverage under their assumptions, G large, superpopulation target
    rng = np.random.default_rng(W.seed_of("r7ppi|S2test|bh2"))
    G, reps = 2000, 4000
    cov = []
    for rep in range(reps):
        u = rng.normal(size=G); fg = u + 0.5 * rng.normal(size=G)
        zg = 1.0 + u + 0.8 * rng.normal(size=G)        # superpopulation mean 1.0
        xi = rng.random(G) < 0.2
        o = W.bh(zg[:, None], fg[:, None], xi[None, :, None])
        cov.append(abs(float(o["theta"][0, 0]) - 1.0) <= 1.6448536269514722 * float(o["se"][0, 0]))
    c = float(np.mean(cov)); se = math.sqrt(0.9 * 0.1 / reps)
    rows.append(dict(test="bh_check2_coverage_large_G", value=c, tolerance=f"within 3 se ({3 * se:.4f}) of 0.90",
                     passed=abs(c - 0.9) <= 3 * se, note=f"G {G}, Bernoulli(0.2) whole clusters, {reps} replicates"))
    pd.DataFrame(rows).to_csv("bh_tests.csv", index=False, float_format="%.12g")
    print(pd.DataFrame(rows).to_string())


def part_s2():
    """S2 implementation checks: bh3 equals W.bh on fixed populations; pi_score sums to n_L and is capped at 1;
    the Kluger draw with uniform pi and a constant predictor gives Omega = 0 and the Hajek mean."""
    import round7_ppi_s2_comparators as S2
    rows = []
    rng = np.random.default_rng(W.seed_of("r7ppi|S2test|impl"))
    worst = 0.0
    for G, n in ((24, 8), (51, 4), (15, 12)):
        z = rng.normal(size=(G, 7)); f = z * 0.5 + rng.normal(size=(G, 7))
        L = np.zeros((40, G, 7), bool)
        for d in range(40):
            L[d, rng.choice(G, n, replace=False)] = True
        o = W.bh(z, f, L)
        th, se = S2.bh3(np.broadcast_to(z, L.shape), np.broadcast_to(f, L.shape), L)
        worst = max(worst, float(np.max(np.abs(th - o["theta"]))), float(np.max(np.abs(se - o["se"]))))
    rows.append(dict(test="s2_bh3_equals_bh", value=worst, tolerance="<= 1e-12", passed=worst <= 1e-12, note="3 designs, 40 draws, 7 columns"))
    worst_s, worst_c = 0.0, 0.0
    for G, n in ((24, 8), (265, 4), (15, 12), (51, 16)):
        u = np.abs(rng.lognormal(0, 1.5, size=(G, 9)))
        p = S2.pi_score(u, n)
        worst_s = max(worst_s, float(np.max(np.abs(p.sum(0) - n))))
        worst_c = max(worst_c, float(p.max() - 1.0))
    rows.append(dict(test="s2_pi_score_sums_to_nL", value=worst_s, tolerance="<= 1e-9", passed=worst_s <= 1e-9, note="lognormal scores"))
    rows.append(dict(test="s2_pi_score_capped", value=worst_c, tolerance="<= 0", passed=worst_c <= 0, note=""))
    G, n = 24, 8
    z = rng.normal(size=(G, 3)); f = np.full((G, 3), 0.7)
    pi = np.full((G, 3), n / G); xi = np.zeros((G, 3), bool); xi[rng.choice(G, n, replace=False)] = True
    o = S2.kluger_draw(z, f, pi, xi, np.random.default_rng(1), B=500)
    dev = float(np.max(np.abs(o["omega"]))) + float(np.max(np.abs(o["ptd"] - z[xi[:, 0], :].mean(0))))
    rows.append(dict(test="s2_kluger_constant_predictor", value=dev, tolerance="<= 1e-12", passed=dev <= 1e-12,
                     note="Omega = 0 and the estimate is the labelled mean"))
    pd.DataFrame(rows).to_csv("s2_impl_tests.csv", index=False, float_format="%.12g")
    print(pd.DataFrame(rows).to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=("s1", "bh", "s2"), required=True)
    a = ap.parse_args()
    {"s1": part_s1, "bh": part_bh, "s2": part_s2}[a.part]()
