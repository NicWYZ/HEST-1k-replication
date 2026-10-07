"""Round 5 PPI, stage E1: the real-task diagnostic, the law shapes and acceptance check 1.

Modes
  --moments   for every task, predictor, estimand (theta3, theta2; donor-weighted) and gene, from
              the full data: sample skewness and excess kurtosis of the G contributions zbar_g, the
              same for zbar_g - lambda fbar_g at the finite-population least-squares coefficient,
              the finite-population R2 of zbar on fbar, and the level Fbar / sd(fbar). Writes
              e1_contribution_moments.csv. Then sets the log-normal shapes of E1's skewed and heavy
              laws: sigma such that the median |skewness| over simulated populations of 24 equals
              the median over genes on CCRCC (theta3, donor-weighted) and its 90th percentile.
              Writes e1_law_shapes.json.
  --acceptance  E1 acceptance check 1: round5_ppi_estimator.design_whole_clusters against
              round4_ppi_q2_masking.textbook_two_stage(..., lin=True) with every unit labelled, on
              the synthetic array of round4_ppi_q4a_tests.synth() and on one CCRCC masking draw
              (hoptimus0, n_L = 8, draw 0, the round-4 seed strings). Writes e1_acceptance1.csv.
  --spearman  reads per-gene coverage from the round-4 masking script's q2_variance_grid_genes
              files (rules none, n_L 8, m all) and writes e1_real_coverage_vs_skewness.csv with the
              Spearman correlation of a gene's classical coverage and |skewness| of its zbar_g.
Sample skewness and kurtosis are scipy.stats.skew and kurtosis with their defaults (biased,
Fisher), for the real contributions and the simulated populations alike.
"""
import argparse
import glob
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

import round4_ppi_estimator as E
import round4_ppi_q2_masking as Q2
import round5_ppi_common as C
import round5_ppi_estimator as R5

TISSUE = ("CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM")
ACS = ("ACS_STATES", "ACS_CA_PUMA")


def parquet_for(vtag, arm):
    if vtag in ACS:
        return os.path.join(C.ROOT, C.ACS_PARQUETS[(vtag, "package")])
    enc = "resnet50" if arm == "permuted" else arm
    return os.path.join(C.ROOT, C.TISSUE_PARQUETS[(vtag, enc)])


def arms_for(vtag):
    return ("package", "permuted") if vtag in ACS else ("hoptimus0", "uni_v2", "resnet50", "permuted")


def cluster_means(vtag, arm, est):
    Q2.THETA2_KIND = "mean" if vtag in ACS else "neo_minus_stroma"
    data = Q2.load(parquet_for(vtag, arm), arm, vtag)
    G = len(data["donors"])
    z, zf, ok = Q2.z_arrays(data, est, "donor")
    S = Q2.donor_sums(z, zf, data["didx"], G)
    zbar, fbar = S["Sz"] / S["n"], S["Sf"] / S["n"]
    return zbar[ok], fbar[ok], data["genes"], data


def moments():
    rows = []
    for vtag in TISSUE + ACS:
        for arm in arms_for(vtag):
            for est in ("theta3", "theta2"):
                zb, fb, genes, _ = cluster_means(vtag, arm, est)
                zc, fc = zb - zb.mean(0), fb - fb.mean(0)
                sff = (fc ** 2).sum(0)
                lam = np.where(sff > 0, (zc * fc).sum(0) / np.where(sff > 0, sff, 1), 0.0)
                r = zb - lam * fb
                r2 = np.where(sff > 0, (zc * fc).sum(0) ** 2 / ((zc ** 2).sum(0) * np.where(sff > 0, sff, 1)), np.nan)
                sdf = fb.std(0, ddof=1)
                for j, gname in enumerate(genes):
                    rows.append(dict(vtag=vtag, arm=arm, estimand=est, population="donor", gene=gname, G=zb.shape[0],
                                     skew_z=stats.skew(zb[:, j]), exkurt_z=stats.kurtosis(zb[:, j]),
                                     skew_r=stats.skew(r[:, j]), exkurt_r=stats.kurtosis(r[:, j]),
                                     lambda_fp=lam[j], R2_fp=r2[j],
                                     level_over_sd_f=(fb[:, j].mean() / sdf[j]) if sdf[j] > 0 else np.nan))
                print(vtag, arm, est, len(genes), flush=True)
    df = pd.DataFrame(rows)
    df.to_csv("e1_contribution_moments.csv", index=False)
    # law shapes
    cc = df[(df.vtag == "CCRCC") & (df.arm == "hoptimus0") & (df.estimand == "theta3")]
    targ_med = float(np.median(np.abs(cc.skew_z)))
    targ_p90 = float(np.quantile(np.abs(cc.skew_z), 0.9))

    def med_abs_skew(sig, q, nsim=20000, G=24):
        rng = np.random.default_rng(C_crc(f"r5e1shape|{sig:.6f}"))
        x = np.exp(sig * rng.standard_normal((nsim, G)))
        return float(np.quantile(np.abs(stats.skew(x, axis=1)), q))

    def solve(target, q=0.5):
        lo, hi = 1e-4, 3.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if med_abs_skew(mid, q) < target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    s_skew = solve(targ_med)
    s_heavy = solve(targ_p90)
    out = dict(target_source="e1_contribution_moments.csv, CCRCC, theta3, donor-weighted, |skew_z| over 50 genes "
                             "(zbar_g does not depend on the predictor; arm hoptimus0 rows used)",
               ccrcc_median_abs_skew=targ_med, ccrcc_p90_abs_skew=targ_p90,
               rule="sigma such that the median over 20,000 simulated populations of 24 of |sample skewness| of "
                    "exp(sigma Z) equals the target (bisection, 40 steps)",
               sigma_skewed=s_skew, sigma_heavy=s_heavy,
               check_median_abs_skew_at_sigma_skewed=med_abs_skew(s_skew, 0.5),
               check_median_abs_skew_at_sigma_heavy=med_abs_skew(s_heavy, 0.5),
               population_skewness_skewed=float((np.exp(s_skew**2) + 2) * np.sqrt(np.exp(s_skew**2) - 1)),
               population_skewness_heavy=float((np.exp(s_heavy**2) + 2) * np.sqrt(np.exp(s_heavy**2) - 1)))
    json.dump(out, open("e1_law_shapes.json", "w"), indent=1)
    print(json.dumps(out))


def C_crc(s):
    import zlib
    return zlib.crc32(s.encode())


def rel(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.nanmax(np.abs(a - b) / np.maximum(np.abs(b), 1e-300)))


def acceptance():
    import round4_ppi_q4a_tests as T
    rows = []
    # synthetic array, both populations, both rules
    D = T.synth(); G, ncol = D["n"].shape
    Lm, Um = T.masks(G, ncol, 12)
    Am = Lm | Um
    M = D["n"][:, 0]
    for pop in ("donor", "spot"):
        for rule in ("none", "c_crossfit_design"):
            lam = E.lambda_rule(rule, pop, D, Lm, Um, seed="r5e1acc")
            th0, v0, df0 = Q2.textbook_two_stage(pop, D, D, Lm, Am, lam, M, D["n"], np.zeros((G, ncol)), lin=True)
            o = R5.design_whole_clusters(pop, D["Sz"] / D["n"], D["Sf"] / D["n"], Lm, lam, Am, M=M, lin=True)
            rows.append(dict(case="synthetic_q4a_synth", pop=pop, rule=rule, rel_diff_theta=rel(o["theta"], th0),
                             rel_diff_var=rel(o["var"], v0), df_equal=bool(np.all(o["df"] == df0))))
    # one CCRCC masking draw, hoptimus0, n_L = 8, m = all, draw 0, round-4 seed strings
    vtag, arm, n_L, m, d = "CCRCC", "hoptimus0", 8, 0, 0
    Q2.THETA2_KIND = "neo_minus_stroma"
    data = Q2.load(parquet_for(vtag, arm), arm, vtag)
    G = len(data["donors"]); didx = data["didx"]; ng = len(data["genes"])
    M = np.bincount(didx, minlength=G).astype(float)
    Ld = Q2.B1.draw_L(list(data["donors"]), n_L, f"q2|{vtag}|nL{n_L}|d{d}")
    Lmask = np.isin(data["donors"], Ld)
    for est in ("theta3", "theta2"):
        for pop in ("donor", "spot"):
            z, zf, ok = Q2.z_arrays(data, est, pop)
            Dp = Q2.donor_sums(z, zf, didx, G)
            Dx = {k: Dp[k] for k in ("Sz", "Sf", "Szz", "Sff", "Szf")}
            Dx["n"] = np.broadcast_to(M[:, None], (G, ng)).copy()
            Lm = np.broadcast_to((Lmask & ok)[:, None], (G, ng)).copy()
            Um = np.broadcast_to((~Lmask & ok)[:, None], (G, ng)).copy()
            Am = Lm | Um
            for rule in ("none", "c_crossfit_design"):
                sd = f"q2|{vtag}|nL{n_L}|m{m}|d{d}|{est}|{pop}|{rule}"
                lam = E.lambda_rule(rule, pop, Dx, Lm, Um, seed=sd)
                th0, v0, df0 = Q2.textbook_two_stage(pop, Dx, Dp, Lm, Am, lam, M,
                                                     np.broadcast_to(M[:, None], (G, ng)), np.zeros((G, ng)), lin=True)
                o = R5.design_whole_clusters(pop, Dx["Sz"] / Dx["n"], Dp["Sf"] / Dp["n"], Lm, lam, Am, M=M, lin=True)
                rows.append(dict(case=f"CCRCC_hoptimus0_nL8_d0_{est}", pop=pop, rule=rule,
                                 rel_diff_theta=rel(o["theta"], th0), rel_diff_var=rel(o["var"], v0),
                                 df_equal=bool(np.all(o["df"] == df0))))
    df = pd.DataFrame(rows)
    df["passes"] = (df.rel_diff_theta <= 1e-12) & (df.rel_diff_var <= 1e-12) & df.df_equal
    df.to_csv("e1_acceptance1.csv", index=False)
    print(df.to_string())


def spearman(grid_glob):
    mom = pd.read_csv("e1_contribution_moments.csv")
    rows = []
    for f in sorted(glob.glob(grid_glob)):
        g = pd.read_csv(f)
        g = g[(g.population == "donor") & (g.target == "design") & (g.lambda_rule == "none")
              & (g.interval == "textbook_t|fpc") & (g.n_L == 8)]
        for (vtag, arm, est), gg in g.groupby(["vtag", "arm", "estimand"]):
            mm = mom[(mom.vtag == vtag) & (mom.arm == arm) & (mom.estimand == est)][["gene", "skew_z", "exkurt_z"]]
            j = gg.merge(mm, on="gene")
            if len(j) >= 3:
                rho, p = stats.spearmanr(j.coverage, np.abs(j.skew_z))
                rk, pk = stats.spearmanr(j.coverage, j.exkurt_z)
            else:
                rho = p = rk = pk = np.nan
            rows.append(dict(vtag=vtag, arm=arm, estimand=est, n_genes=len(j), spearman_cov_abs_skew=rho, p_value=p,
                             spearman_cov_exkurt=rk, p_value_exkurt=pk,
                             coverage_median=float(j.coverage.median()) if len(j) else np.nan,
                             coverage_min=float(j.coverage.min()) if len(j) else np.nan,
                             abs_skew_median=float(np.abs(j.skew_z).median()) if len(j) else np.nan,
                             source=os.path.basename(f)))
    pd.DataFrame(rows).to_csv("e1_real_coverage_vs_skewness.csv", index=False)
    print(pd.DataFrame(rows).to_string())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--moments", action="store_true")
    ap.add_argument("--acceptance", action="store_true")
    ap.add_argument("--spearman", default="", help="glob of q2_variance_grid_genes__*.csv.gz")
    a = ap.parse_args()
    np.seterr(all="ignore")
    if a.moments:
        moments()
    if a.acceptance:
        acceptance()
    if a.spearman:
        spearman(a.spearman)


if __name__ == "__main__":
    main()
