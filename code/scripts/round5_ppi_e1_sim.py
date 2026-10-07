"""Round 5 PPI, stage E1: the final design-target interval in simulation (brief section 6, E1).

For each cell (G, n_L, R2, lambda*, kappa, law) draw 60 finite populations of G cluster pairs
    fbar_g = kappa + p_g,   zbar_g = lambda* p_g + sigma_xi xi_g,   sigma_xi^2 = lambda*^2 (1 - R2)/R2,
(at R2 = 0, zbar_g = xi_g), with p and xi independent draws of the law, standardised to mean 0 and
variance 1. For each population draw 1,000 simple random samples of n_L clusters and compute,
for rules none, c_crossfit_design (round-4 lambda_rule, called unmodified on sufficient-statistic
arrays built as synth() in round4_ppi_q4a_tests.py does) and an oracle with lambda fixed at the
population's least-squares slope, the intervals
    textbook_t|fpc        (no linearised term)
    textbook_t|fpc|lin    (the final interval)
    johnson|fpc|lin       (Johnson 1978 on e_g, diagnostic)
against the population's own mean of zbar_g.

The 60 populations of a cell are the columns of one array, so a draw is one call per rule. The
samples of draw d depend only on (G, n_L, d), so every cell with the same G and n_L sees the same
samples, which pairs the comparisons across R2, lambda*, kappa and law. Populations depend on
(G, R2, lambda*, kappa, law, population index) and not on n_L.

Laws: normal; 'lognormal:<sigma>' a standardised log-normal exp(sigma Z), with sigma fixed in the
plan before the run. Seeds: zlib.crc32 of a string naming the stage, the cell and the draw.

Output (summaries first, as WAYS_OF_WORKING asks): e1_sim_grid__<tag>.csv, one row per cell,
rule and interval, and e1_sim_pop__<tag>.csv.gz, one row per cell, rule, interval and population.
"""
import argparse
import itertools
import json
import os
import time
import zlib

import numpy as np
import pandas as pd

import round4_ppi_estimator as E
import round5_ppi_estimator as R5

N_POP = 60
N_DRAW = 1000
NL_ALL = (4, 6, 8, 12, 16, 20)
R2_GRID = (0.0, 0.2, 0.4, 0.7, 0.9)
LAMSTAR = (0.6, 1.2)
KAPPA = (0.0, 2.0, 10.0)
NCOL_STAT = 100.0   # every cluster is given 100 units in the sufficient statistics; with every
                    # unit labelled only the cluster means enter, so the value does not matter


def crc(s):
    return zlib.crc32(s.encode())


def draw_law(law, rng, size):
    if law == "normal":
        return rng.standard_normal(size)
    if law.startswith("lognormal:"):
        s = float(law.split(":")[1])
        x = np.exp(s * rng.standard_normal(size))
        mu = np.exp(s * s / 2.0)
        sd = np.sqrt((np.exp(s * s) - 1.0) * np.exp(s * s))
        return (x - mu) / sd
    raise ValueError(law)


def populations(G, R2, lamstar, kappa, law):
    p = np.empty((G, N_POP)); xi = np.empty((G, N_POP))
    for k in range(N_POP):
        rng = np.random.default_rng(crc(f"r5e1pop|G{G}|R2{R2}|lam{lamstar}|kap{kappa}|{law}|p{k}"))
        p[:, k] = draw_law(law, rng, G)
        xi[:, k] = draw_law(law, rng, G)
    f = kappa + p
    if R2 == 0:
        z = xi
    else:
        z = lamstar * p + np.sqrt(lamstar ** 2 * (1.0 - R2) / R2) * xi
    return z, f


def stats_arrays(z, f):
    n = np.full(z.shape, NCOL_STAT)
    D = dict(n=n, Sz=z * n, Sf=f * n)
    D["Szz"], D["Sff"], D["Szf"] = D["Sz"] ** 2 / n, D["Sf"] ** 2 / n, D["Sz"] * D["Sf"] / n
    return D


def run_cell(G, nL, R2, lamstar, kappa, law, n_draw):
    z, f = populations(G, R2, lamstar, kappa, law)
    D = stats_arrays(z, f)
    theta_pop = z.mean(0)
    # population facts per column
    zc, fc = z - z.mean(0), f - f.mean(0)
    r2_fp = (zc * fc).sum(0) ** 2 / ((zc ** 2).sum(0) * (fc ** 2).sum(0))
    orc_full = R5.oracle_lambda("donor", z, f, np.ones_like(z, bool))
    Sr2 = R5.population_rectifier_var("donor", z, f, orc_full["lam"])
    Sz2 = z.var(0, ddof=1)
    rules = ("none", "c_crossfit_design", "oracle")
    ivs = ("textbook_t|fpc", "textbook_t|fpc|lin", "johnson|fpc|lin")
    acc = {(r, iv): dict(th=[], var=[], cov=[], w=[]) for r in rules for iv in ivs}
    lam_c, lam_raw = [], []
    for d in range(n_draw):
        rng = np.random.default_rng(crc(f"r5e1srs|G{G}|nL{nL}|d{d}"))
        L = np.zeros(G, bool); L[rng.choice(G, nL, replace=False)] = True
        Lm = np.broadcast_to(L[:, None], z.shape).copy()
        Um = ~Lm
        for rule in rules:
            if rule == "oracle":
                lam = R5.oracle_lambda("donor", z, f, Lm)
            else:
                lam = E.lambda_rule(rule, "donor", D, Lm, Um, seed=f"r5e1|G{G}|nL{nL}|d{d}")
                if rule == "c_crossfit_design":
                    lam_c.append(lam["cU"]); lam_raw.append((lam["rawA"] + lam["rawB"]) / 2.0)
            for iv in ivs:
                lin = iv.endswith("|lin")
                o = R5.design_whole_clusters("donor", z, f, Lm, lam, lin=lin)
                if iv.startswith("johnson"):
                    lo, hi = R5.johnson_interval(o["e"], Lm, o["theta"], o["var"], o["df"])
                else:
                    lo, hi = R5.t_interval(o["theta"], o["var"], o["df"])
                a = acc[(rule, iv)]
                a["th"].append(o["theta"]); a["var"].append(o["var"])
                a["cov"].append((lo <= theta_pop) & (theta_pop <= hi)); a["w"].append(hi - lo)
    fin = {k: {kk: np.array(vv) for kk, vv in v.items()} for k, v in acc.items()}
    ev_cl = fin[("none", "textbook_t|fpc")]["th"].var(0, ddof=1)
    lam_c, lam_raw = np.array(lam_c), np.array(lam_raw)
    rows, prow = [], []
    exact_fixed = (1.0 - nL / G) * Sr2 / nL
    exact_cl = (1.0 - nL / G) * Sz2 / nL
    for (rule, iv), v in fin.items():
        th = v["th"]
        ev = th.var(0, ddof=1)
        m4 = ((th - th.mean(0)) ** 4).mean(0)
        ev_se = np.sqrt(np.maximum(m4 - ev ** 2 * (n_draw - 3) / (n_draw - 1), 0) / n_draw)
        cov = v["cov"].mean(0)
        est_over_emp = v["var"].mean(0) / ev
        vr_cl = ev / ev_cl
        orc_ratio = ev / exact_fixed
        orc_ratio_se = ev_se / exact_fixed
        cl_ratio = ev / exact_cl
        cell = dict(G=G, n_L=nL, R2=R2, lambda_star=lamstar, kappa=kappa, law=law, rule=rule, interval=iv)
        rows.append(dict(**cell, n_pop=th.shape[1], n_draw=n_draw,
                         coverage_mean=cov.mean(), coverage_sd_pop=cov.std(ddof=1),
                         coverage_p05=np.quantile(cov, 0.05), coverage_p50=np.median(cov), coverage_p95=np.quantile(cov, 0.95),
                         coverage_mc_se=np.sqrt((cov * (1 - cov) / n_draw).sum()) / len(cov),
                         est_over_emp_mean=est_over_emp.mean(), est_over_emp_median=np.median(est_over_emp),
                         est_over_emp_p05=np.quantile(est_over_emp, 0.05), est_over_emp_p95=np.quantile(est_over_emp, 0.95),
                         var_ratio_to_classical_mean=vr_cl.mean(), var_ratio_to_classical_median=np.median(vr_cl),
                         emp_over_exact_fixed_mean=orc_ratio.mean(),
                         emp_over_exact_fixed_mc_se=np.sqrt((orc_ratio_se ** 2).sum()) / len(orc_ratio),
                         emp_over_exact_classical_mean=cl_ratio.mean(),
                         width_mean=v["w"].mean(),
                         lambda_clipped_median=float(np.nanmedian(lam_c)) if rule == "c_crossfit_design" else
                         (float(np.median(orc_full["lam"])) if rule == "oracle" else 0.0),
                         lambda_unclipped_median=float(np.nanmedian(lam_raw)) if rule == "c_crossfit_design" else np.nan,
                         r2_fp_median=float(np.median(r2_fp)), level_over_sd_f_median=float(np.median(f.mean(0) / f.std(0, ddof=1))),
                         n_nonfinite=int((~np.isfinite(th)).sum() + (~np.isfinite(v["var"])).sum())))
        for k in range(th.shape[1]):
            prow.append(dict(**cell, pop=k, coverage=cov[k], emp_var=ev[k], est_over_emp=est_over_emp[k],
                             var_ratio_to_classical=vr_cl[k], emp_over_exact_fixed=orc_ratio[k], r2_fp=r2_fp[k]))
    return rows, prow


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--G", type=int, required=True)
    ap.add_argument("--laws", required=True, help="comma list: normal, lognormal:<sigma>")
    ap.add_argument("--nl", default=",".join(map(str, NL_ALL)))
    ap.add_argument("--r2", default=",".join(map(str, R2_GRID)))
    ap.add_argument("--lamstar", default=",".join(map(str, LAMSTAR)))
    ap.add_argument("--kappa", default=",".join(map(str, KAPPA)))
    ap.add_argument("--draws", type=int, default=N_DRAW)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out-dir", default=".")
    a = ap.parse_args()
    np.seterr(all="ignore")
    G = a.G
    nls = [n for n in map(int, a.nl.split(",")) if n <= G - 3]
    grid = list(itertools.product(nls, map(float, a.r2.split(",")), map(float, a.lamstar.split(",")),
                                  map(float, a.kappa.split(",")), a.laws.split(",")))
    t0 = time.time()
    rows, prows = [], []
    for i, (nL, R2, ls, kap, law) in enumerate(grid):
        r, p = run_cell(G, nL, R2, ls, kap, law, a.draws)
        rows += r; prows += p
        if i % 10 == 0 or i == len(grid) - 1:
            print(f"cell {i+1}/{len(grid)} G{G} nL{nL} R2{R2} lam{ls} kap{kap} {law} {time.time()-t0:.0f}s", flush=True)
    os.makedirs(a.out_dir, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"e1_sim_grid__{a.tag}.csv"), index=False)
    pd.DataFrame(prows).to_csv(os.path.join(a.out_dir, f"e1_sim_pop__{a.tag}.csv.gz"), index=False)
    json.dump(dict(G=G, n_cells=len(grid), n_rows=len(rows), wall_s=time.time() - t0, laws=a.laws, nl=nls,
                   draws=a.draws, n_pop=N_POP), open(os.path.join(a.out_dir, f"e1_sim_summary__{a.tag}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
