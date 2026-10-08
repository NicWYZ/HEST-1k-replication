"""Round 5 PPI, interval 2, stage E3a: the masking with every unit labelled, both intervals.

docs/decisions/round5_ppi_E2_decisions.md section 5, E3a; theory section 2.0. For one task and
arm, n_L in {6, 8, 12, 16} (cells with n_L > G - 2 are skipped, as round 4 skips them), every
spot of a labelled donor labelled, theta3 and theta2, donor-weighted, design target, rules none
and c_crossfit_design, and the intervals
    textbook_t|fpc|lin      round 4's final interval; these rows must reproduce q4a_table61.csv
    textbook_t|fpc|lin|xf   the corrected interval, round5_ppi_estimator.crossfit_extra
    textbook_t|fpc          reported beside them.

The draw loop is round4_ppi_q2_masking.run_cell at m = all, restricted to the donor-weighted
population and the design target, with its seeds unchanged: the labelled donors come from
round3_b1_ppi.draw_L with 'q2|<vtag>|nL<n_L>|d<draw>' and the cross-fit seed is
'q2|<vtag>|nL<n_L>|m0|d<draw>|<est>|donor|<rule>'. Since every seed of a (est, pop, rule) is its
own, dropping the spot-weighted population and the superpopulation target changes no row that
remains. Data loading, z arrays, donor sums, textbook_two_stage and summarise are imported from
round4_ppi_q2_masking unmodified.

Output: e3a_masking__<vtag>__<arm>.csv (one row per estimand, rule, interval and n_L, the columns
of round4 summarise) and e3a_masking_genes__<vtag>__<arm>.csv.gz.
"""
import argparse
import json
import os
import time

import numpy as np
import pandas as pd

import round4_ppi_estimator as E
import round4_ppi_q2_masking as Q2
import round5_ppi_estimator as R5

NL_GRID = (6, 8, 12, 16)
RULES = ("none", "c_crossfit_design")
POP = "donor"


def run_cell_all(data, Z, n_L, n_draws, vtag, theta_full, valid, Dpop):
    G = len(data["donors"])
    didx = data["didx"]
    M = np.bincount(didx, minlength=G).astype(float)
    ng = len(data["genes"])
    acc = {}
    xf_share = {}
    for d in range(n_draws):
        Ld = Q2.B1.draw_L(list(data["donors"]), n_L, f"q2|{vtag}|nL{n_L}|d{d}")
        Lmask = np.isin(data["donors"], Ld)
        sel = np.isin(didx, np.flatnonzero(Lmask))
        mlab = np.bincount(didx[sel], minlength=G).astype(float)
        mlab2 = np.broadcast_to(mlab[:, None], (G, ng))
        for (est, pop), (z, zf) in Z.items():
            ok = valid[(est, pop)]
            Dp = Dpop[(est, pop)]
            Dl = Q2.donor_sums(z, zf, didx, G, sel)
            scale = np.where(mlab > 0, M / np.maximum(mlab, 1), 0.0)[:, None]
            Dx = {k: np.where(Lmask[:, None], Dl[k] * scale, Dp[k]) for k in ("Sz", "Sf", "Szz", "Sff", "Szf")}
            Dx["n"] = np.broadcast_to(M[:, None], (G, ng)).copy()
            Lm = np.broadcast_to((Lmask & ok)[:, None], (G, ng)).copy()
            Um = np.broadcast_to((~Lmask & ok)[:, None], (G, ng)).copy()
            Am = Lm | Um
            tr = theta_full[(est, pop)]
            s2w = np.zeros((G, ng))          # every spot labelled: no within-donor term
            fbar = Dx["Sf"] / Dx["n"]
            for rule in RULES:
                sd = f"q2|{vtag}|nL{n_L}|m0|d{d}|{est}|{pop}|{rule}"
                lam = E.lambda_rule(rule, pop, Dx, Lm, Um, seed=sd)
                th, var, df = Q2.textbook_two_stage(pop, Dx, Dp, Lm, Am, lam, M, mlab2, s2w)
                lo, hi = E.t_interval(th, var, df)
                Q2._acc(acc, (est, pop, "design", rule, "textbook_t|fpc"), th, var, lo, hi, lam["lam"], tr,
                        lam.get("lam_se"), *Q2._raw(lam))
                _, varl, _ = Q2.textbook_two_stage(pop, Dx, Dp, Lm, Am, lam, M, mlab2, s2w, lin=True)
                lo, hi = E.t_interval(th, varl, df)
                Q2._acc(acc, (est, pop, "design", rule, "textbook_t|fpc|lin"), th, varl, lo, hi, lam["lam"], tr,
                        lam.get("lam_se"), *Q2._raw(lam))
                extra = R5.crossfit_extra(pop, fbar, Lm, lam, Am)
                varx = varl + extra
                lo, hi = E.t_interval(th, varx, df)
                Q2._acc(acc, (est, pop, "design", rule, "textbook_t|fpc|lin|xf"), th, varx, lo, hi, lam["lam"], tr,
                        lam.get("lam_se"), *Q2._raw(lam))
                xf_share.setdefault((est, rule), []).append(np.where(varl > 0, extra / varl, np.nan))
    return acc, xf_share


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--parquet", required=True)
    p.add_argument("--vtag", required=True)
    p.add_argument("--arm", required=True, help="encoder or package name, or 'permuted'")
    p.add_argument("--nl-grid", default=",".join(map(str, NL_GRID)))
    p.add_argument("--draws", type=int, default=200)
    p.add_argument("--theta2-kind", default="neo_minus_stroma", choices=("neo_minus_stroma", "mean"))
    p.add_argument("--out-dir", default=".")
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    Q2.THETA2_KIND = a.theta2_kind
    os.makedirs(a.out_dir, exist_ok=True)
    t0 = time.time()
    data = Q2.load(a.parquet, a.arm, a.vtag)
    G = len(data["donors"])
    nls = [n for n in map(int, a.nl_grid.split(",")) if n <= G - 2]
    Z, valid, theta_full, Dpop = {}, {}, {}, {}
    for est in Q2.ESTS:
        z, zf, ok = Q2.z_arrays(data, est, POP)
        Z[(est, POP)], valid[(est, POP)] = (z, zf), ok
        S = Q2.donor_sums(z, zf, data["didx"], G)
        Dpop[(est, POP)] = S
        theta_full[(est, POP)] = (S["Sz"] / S["n"])[ok].mean(0)
    rows, generows = [], []
    medM = float(np.median(np.bincount(data["didx"], minlength=G)))
    for n_L in nls:
        acc, xs = run_cell_all(data, Z, n_L, a.draws, a.vtag, theta_full, valid, Dpop)
        cell = dict(vtag=a.vtag, arm=a.arm, G=G, n_L=n_L, m="all", m_eff=medM)
        for r in Q2.summarise(acc, cell, data["genes"]):
            for gr in r.pop("_genes", []):
                generows.append(dict({k: r[k] for k in ("vtag", "arm", "G", "n_L", "m", "estimand", "population",
                                                       "target", "lambda_rule", "interval")}, **gr))
            sh = xs.get((r["estimand"], r["lambda_rule"]))
            r["valid_donors"] = int(valid[(r["estimand"], POP)].sum())
            r["xf_extra_over_lin_var_median"] = (float(np.nanmedian(np.stack(sh))) if sh is not None
                                                 and r["interval"].endswith("|xf") else np.nan)
            rows.append(r)
        print(f"nL{n_L} {time.time()-t0:.0f}s", flush=True)
    tag = f"{a.vtag}__{a.arm}"
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"e3a_masking__{tag}.csv"), index=False)
    pd.DataFrame(generows).to_csv(os.path.join(a.out_dir, f"e3a_masking_genes__{tag}.csv.gz"), index=False)
    json.dump(dict(vtag=a.vtag, arm=a.arm, G=G, nl=nls, draws=a.draws, n_rows=len(rows),
                   theta2_kind=a.theta2_kind, wall_s=time.time() - t0),
              open(os.path.join(a.out_dir, f"e3a_masking_summary__{tag}.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
