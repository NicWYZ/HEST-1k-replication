"""Round 5 PPI, interval 2, stage E3a: the E1 grid rerun with the cross-fitting correction.

docs/decisions/round5_ppi_E2_decisions.md section 5, E3a; theory section 2.0. The cells, the
populations, the samples, the halves and every seed are those of round5_ppi_e1_sim.py, whose
generator functions (crc, draw_law, populations, stats_arrays) are imported from it unchanged.
run_cell is E1's with two changes only. The intervals are
    textbook_t|fpc        (no linearised term)
    textbook_t|fpc|lin    (E1's final interval; these rows must reproduce e1_sim_grid.csv)
    textbook_t|fpc|lin|xf (the corrected interval, round5_ppi_estimator.crossfit_extra)
and Johnson's interval, dropped at E2, is not computed. The rows of rule none and of the oracle
are the same for |lin and |lin|xf by construction (acceptance check).

Output: e3a_sim_grid__<tag>.csv, e3a_sim_pop__<tag>.csv.gz, e3a_sim_summary__<tag>.json.
"""
import argparse
import itertools
import json
import os
import time

import numpy as np
import pandas as pd

import round4_ppi_estimator as E
import round5_ppi_estimator as R5
from round5_ppi_e1_sim import (N_POP, N_DRAW, NL_ALL, R2_GRID, LAMSTAR, KAPPA,  # noqa: F401
                               crc, draw_law, populations, stats_arrays)


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
    ivs = ("textbook_t|fpc", "textbook_t|fpc|lin", "textbook_t|fpc|lin|xf")
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
                lin = "|lin" in iv
                o = R5.design_whole_clusters("donor", z, f, Lm, lam, lin=lin, xf=iv.endswith("|xf"))
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
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"e3a_sim_grid__{a.tag}.csv"), index=False)
    pd.DataFrame(prows).to_csv(os.path.join(a.out_dir, f"e3a_sim_pop__{a.tag}.csv.gz"), index=False)
    json.dump(dict(G=G, n_cells=len(grid), n_rows=len(rows), wall_s=time.time() - t0, laws=a.laws, nl=nls,
                   draws=a.draws, n_pop=N_POP), open(os.path.join(a.out_dir, f"e3a_sim_summary__{a.tag}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
