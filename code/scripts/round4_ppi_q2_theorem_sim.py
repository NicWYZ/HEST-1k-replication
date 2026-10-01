#!/usr/bin/env python
"""Round 4, PPI track, Q2 unit 6: simulation check of the gain theorem (Q1 decision memo section 5;
plan section 13.5; docs/round4_ppi_theory.md section 2).

Grid: G_L in {6, 12}, G_U in {20, 100}, m in {200, 5000}, rho = 0.3, r = 0.5,
sigma_a^2 / sigma_u^2 in {0.25, 1, 4} with sigma_u^2 = rho as the memo writes it; 2,000 replicates;
lambda rule c_crossfit against the classical estimator; donor-weighted mean; superpopulation target.

The Q1 generator (round4_ppi_q1_sim.gen_block) supplies covariate, outcome and the standard-normal
pieces a0, eps0. The predictor is yhat = y - sigma_a a0 - sigma_eps eps0, Q1's construction with
sigma_a^2 set from the grid instead of Q1's rho / 2, and sigma_eps^2 = Var(y)(1/r^2 - 1) - sigma_a^2
so that the spot-level correlation is r, as in Q1.

Q1's outcome also carries beta c_g, a donor-level covariate term, so the outcome's cluster variance is
sigma_U^2 = rho + beta^2 s_c, not rho. The file records both: R2_cluster_memo = 1/(1 + sigma_a^2/rho),
the memo's nominal value, and R2_cluster_exact = sigma_U^2/(sigma_U^2 + sigma_a^2).

Columns of q2_sim_theorem.csv, one row per cell: the empirical variance of the PPI estimate over
replicates divided by the classical one (`emp_var_ratio`, with a delta-method MC standard error),
`one_minus_R2_memo`, `one_minus_R2_exact`, the large-m full ratios at the cluster optimum and at the
two-term optimum (`full_ratio_lambda_c`, `full_ratio_lambda_A`, theory section 2 step 3, exact R2),
the finite-m ratio at lambda_A (`finite_m_ratio_lambda_A`), the G_U term's size at lambda_A
(`GU_term_lambda_A` = R2 n_L/(G_U + n_L)), and the lambda summaries.
"""
import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round4_ppi_estimator as E  # noqa: E402
import round4_ppi_q1_sim as Q1  # noqa: E402

GRID = dict(G_L=(6, 12), G_U=(20, 100), m=(200, 5000), ratio=(0.25, 1.0, 4.0))
RHO, R = 0.3, 0.5
BETA, S_C, MU = Q1.BETA, Q1.S_C, Q1.MU


def components(ratio, m, G_L, G_U):
    sU2 = RHO + BETA ** 2 * S_C
    sa2 = ratio * RHO
    var_y = BETA ** 2 + 1.0
    seps2 = var_y * (1.0 / R ** 2 - 1.0) - sa2
    assert seps2 >= 0
    se2 = BETA ** 2 * (1.0 - S_C) + (1.0 - RHO)      # within-donor variance of y
    sp2 = sU2 + sa2                                   # Var p_g, p = u + beta c - a
    Cu = sU2
    Ce, sd2 = se2, se2 + seps2
    R2 = Cu ** 2 / (sU2 * sp2)
    lam_c = Cu / sp2
    lam_A_inf = lam_c * G_U / (G_U + G_L)
    # finite m, both terms, unlabelled donors also with m spots
    num = (Cu + Ce / m) / G_L
    den = (sp2 + sd2 / m) * (1.0 / G_L + 1.0 / G_U)
    lam_A = num / den

    def vpp(lam):
        su_r = sU2 - 2 * lam * Cu + lam ** 2 * sp2
        se_r = se2 - 2 * lam * Ce + lam ** 2 * sd2
        return (su_r + se_r / m) / G_L + lam ** 2 * (sp2 + sd2 / m) / G_U

    vcl = (sU2 + se2 / m) / G_L
    return dict(sigma_U2=sU2, sigma_a2=sa2, sigma_eps2=seps2, R2_cluster_exact=R2,
                R2_cluster_memo=1.0 / (1.0 + ratio), lambda_c=lam_c, lambda_A_inf=lam_A_inf,
                lambda_A_finite=lam_A, one_minus_R2_exact=1.0 - R2,
                one_minus_R2_memo=1.0 - 1.0 / (1.0 + ratio),
                full_ratio_lambda_c=1.0 - R2 + G_L / G_U * R2,
                full_ratio_lambda_A=1.0 - R2 * G_U / (G_U + G_L),
                finite_m_ratio_lambda_A=vpp(lam_A) / vcl,
                GU_term_lambda_A=R2 * G_L / (G_U + G_L))


def run_cell(G_L, G_U, m, ratio, reps, chunk, max_spots, seed):
    G = G_L + G_U
    comp = components(ratio, m, G_L, G_U)
    sa, seps = np.sqrt(comp["sigma_a2"]), np.sqrt(comp["sigma_eps2"])
    rng = E.seed_rng(seed)
    th = {"none": [], "c_crossfit": []}
    lams = []
    done, ch = 0, 0
    while done < reps:
        n = min(chunk, reps - done)
        sub = max(1, int(max_spots // (G * m)))
        t_parts, tf_parts = [], []
        for s0 in range(0, n, sub):
            rr = min(sub, n - s0)
            mm, y, a0, eps0 = Q1.gen_block(rng, G, m, rr, RHO)
            yh = y - sa * a0 - seps * eps0
            t_parts.append(y.mean(2).T)
            tf_parts.append(yh.mean(2).T)
        t, tf = np.concatenate(t_parts, 1), np.concatenate(tf_parts, 1)
        D = Q1._n_for_iid(Q1.donor_value_stats(t, tf), m)
        Lm = np.zeros((G, n), bool); Lm[:G_L] = True
        Um = ~Lm
        for rule in th:
            lam = E.lambda_rule(rule, "donor", D, Lm, Um, seed=f"{seed}|ch{ch}|{rule}")
            res = E.estimate("donor", D, Lm, Um, lam)
            th[rule].append(res["theta"])
            if rule == "c_crossfit":
                lams.append(lam["lam"])
        done += n
        ch += 1
    a, b = np.concatenate(th["c_crossfit"]), np.concatenate(th["none"])
    va, vb = a.var(ddof=1), b.var(ddof=1)
    ratio_emp = va / vb
    # delta-method MC se of a variance ratio of two correlated estimates
    da, db = (a - a.mean()) ** 2 - va, (b - b.mean()) ** 2 - vb
    g = da / va - db / vb
    se = ratio_emp * np.sqrt(np.var(g, ddof=1) / len(a))
    lam = np.concatenate(lams)
    return dict(G_L=G_L, G_U=G_U, m=m, rho=RHO, r=R, sigma_a2_over_sigma_u2=ratio, n_reps=len(a),
                emp_var_ratio=ratio_emp, emp_var_ratio_mc_se=se, emp_var_ppi=va, emp_var_cl=vb,
                bias_ppi=float(a.mean() - MU), bias_cl=float(b.mean() - MU),
                lambda_mean=float(lam.mean()), lambda_median=float(np.median(lam)), **comp)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--reps", type=int, default=2000)
    p.add_argument("--chunk", type=int, default=250)
    p.add_argument("--max-spots", type=float, default=4e6)
    p.add_argument("--G-L-grid", default="")
    p.add_argument("--out-dir", required=True)
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    if a.G_L_grid:
        GRID["G_L"] = tuple(int(x) for x in a.G_L_grid.split(","))
    os.makedirs(a.out_dir, exist_ok=True)
    cfg = dict(stage="r4ppi_Q2_theorem_sim", grid={k: list(v) for k, v in GRID.items()}, rho=RHO,
               r=R, beta=BETA, s_c=S_C, mu=MU, reps=a.reps, rule="c_crossfit", population="donor",
               estimand="mean", target="super", seed_source="zlib.crc32")
    blob = json.dumps(cfg, sort_keys=True)
    tag = "GL" + "_".join(str(g) for g in GRID["G_L"])
    with open(f"{a.out_dir}/q2_sim_theorem_config__{tag}.json", "w") as fh:
        fh.write(blob)
    t0 = time.time()
    rows = []
    for G_L in GRID["G_L"]:
        for G_U in GRID["G_U"]:
            for m in GRID["m"]:
                for ratio in GRID["ratio"]:
                    rows.append(run_cell(G_L, G_U, m, ratio, a.reps, a.chunk, a.max_spots,
                                         f"q2thm|GL{G_L}|GU{G_U}|m{m}|ratio{ratio}"))
                    print(f"GL{G_L} GU{G_U} m{m} ratio{ratio} {time.time()-t0:.0f}s", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(f"{a.out_dir}/q2_sim_theorem__{tag}.csv", index=False)
    summ = dict(config_hash=hashlib.sha256(blob.encode()).hexdigest()[:16], n_rows=len(df),
                wall_s=time.time() - t0)
    with open(f"{a.out_dir}/q2_sim_theorem_summary__{tag}.json", "w") as fh:
        json.dump(summ, fh, indent=1)
    print(json.dumps(summ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
