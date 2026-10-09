"""Round 5 PPI, interval 2, stage E4 in simulation: balanced designs on E1's generator.

Brief section 6, E4: E1's generator (round5_ppi_e1_sim.populations, imported unchanged) at G in
{15, 24, 51}, n_L in {4, 6, 8, 12}, R2 in E1's grid, lambda* in {0.6, 1.2}, kappa = 0, the normal
and the skewed law (lognormal:0.940959499999249). Each of the 60 populations of a cell is a column
with its own balance variable, its fbar_g (one outcome, case (i) of the brief). Designs
(round5_ppi_balance.py): D0; D1 two per stratum on fbar_g; D2 rejective with p_a in {0.1, 0.01}.
Estimators: classical (rule none) and final (rule c_crossfit_design), intervals textbook_t|fpc|lin
and |lin|xf under D0 and D2, strat_t under D1.

Draws: for each (G, n_L) a pool of n_draws x n_cand candidate samples, candidate k of draw d the
first n_L of argsort(uniform(G)) under 'r5e4sim|G<G>|nL<n>|d<d>' (one generator per draw, n_cand rows);
candidate 0 is the D0 draw. The pool depends on (G, n_L) only, so every cell and design at that
(G, n_L) is paired. D2's threshold is the p_a quantile of the squared standardised distance
(fbar_L - Fbar)^2 / S_f^2 over the pool, per population. D1 draws under 'r5e4simD1|G|nL|d'.
Cross-fit seed 'r5e4simx|G<G>|nL<n>|d<d>|<design>'.

Output: e4_sim__<tag>.csv, one row per cell, design, p_a, rule and interval: coverage (mean over
populations), mean over populations of the empirical variance, of est/emp, of the variance ratio to
D0 classical (per population), and the median finite-population R^2 of the cell.
"""
import argparse
import itertools
import json
import os
import time
import zlib

import numpy as np
import pandas as pd

import round5_ppi_balance as BAL
import round5_ppi_estimator as R5
from round5_ppi_e1_sim import populations, R2_GRID, LAMSTAR

GRID_G, NL = (15, 24, 51), (4, 6, 8, 12)
LAWS = ("normal", "lognormal:0.940959499999249")


def pool(G, nL, n_draws, n_cand):
    masks = np.zeros((n_draws, n_cand, G), bool)
    for d in range(n_draws):
        rng = np.random.default_rng(zlib.crc32(f"r5e4sim|G{G}|nL{nL}|d{d}".encode()))
        idx = np.argsort(rng.random((n_cand, G)), axis=1)[:, :nL]
        np.put_along_axis(masks[d], idx, True, axis=1)
    return masks


def run_cell(G, nL, R2, ls, law, masks, n_draws, n_cand):
    from scipy import stats
    z, f = populations(G, R2, ls, 0.0, law)
    npop = z.shape[1]
    theta = z.mean(0)
    zc, fc = z - z.mean(0), f - f.mean(0)
    r2_fp = (zc * fc).sum(0) ** 2 / ((zc ** 2).sum(0) * (fc ** 2).sum(0))
    flat = masks.reshape(-1, G).astype(float)
    dist = ((flat @ fc) / nL) ** 2 / f.var(0, ddof=1)[None, :]           # (n_draws*n_cand, npop)
    designs = [("D0", 1.0), ("D2", 0.1), ("D2", 0.01), ("D1", np.nan)]
    st = BAL.d1_strata(f, nL) if nL % 2 == 0 else None
    res = {}
    for dname, pa in designs:
        if dname == "D2":
            sel, thr, nmiss = BAL.d2_select(dist, n_draws, n_cand, pa)
        for d in range(n_draws):
            if dname == "D0":
                Lm = np.ascontiguousarray(np.broadcast_to(masks[d, 0][:, None], (G, npop)))
            elif dname == "D2":
                Lm = np.ascontiguousarray(masks[d][sel[d], :].T)
            else:
                if st is None:
                    break
                Lm = BAL.d1_draw(st, np.random.default_rng(zlib.crc32(f"r5e4simD1|G{G}|nL{nL}|d{d}".encode())))
            for rule in ("none", "c_crossfit_design"):
                seed = f"r5e4simx|G{G}|nL{nL}|d{d}|{dname}"
                if dname == "D1":
                    out, _ = BAL.estimate_d1(z, f, Lm, st, rule, seed)
                else:
                    out, _ = BAL.estimate_srs_like(z, f, Lm, rule, seed)
                for iv, (th, v, df) in out.items():
                    res.setdefault((dname, pa, rule, iv), []).append((th, v, np.broadcast_to(df, th.shape)))
    rows = []
    ev0 = None
    for key in sorted(res, key=lambda k: (k[0] != "D0", str(k))):
        dname, pa, rule, iv = key
        L = res[key]
        th = np.array([x[0] for x in L]); v = np.array([x[1] for x in L]); df = np.array([x[2] for x in L])
        q = stats.t.ppf(1 - R5.ALPHA / 2, df)
        se = np.sqrt(np.maximum(v, 0))
        cov = (np.abs(th - theta[None, :]) <= q * se).mean(0)
        ev = th.var(0, ddof=1)
        if dname == "D0" and rule == "none" and iv == "textbook_t|fpc|lin":
            ev0 = ev
        rows.append(dict(G=G, n_L=nL, R2=R2, lambda_star=ls, kappa=0.0, law=law, design=dname, p_a=pa, rule=rule,
                         interval=iv, n_pop=npop, n_draws=len(L), coverage_mean=float(cov.mean()),
                         coverage_p05=float(np.quantile(cov, 0.05)), emp_var_mean=float(ev.mean()),
                         est_over_emp_mean=float((v.mean(0) / ev).mean()),
                         var_ratio_to_D0_classical_mean=np.nan, _ev=ev,
                         r2_fp_median=float(np.median(r2_fp))))
    for r in rows:
        ev = r.pop("_ev")
        r["var_ratio_to_D0_classical_mean"] = float((ev / ev0).mean()) if ev0 is not None else np.nan
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--G", type=int, required=True)
    ap.add_argument("--laws", default=",".join(LAWS))
    ap.add_argument("--nl", default=",".join(map(str, NL)))
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--n-cand", type=int, default=1000)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out-dir", default=".")
    a = ap.parse_args()
    np.seterr(all="ignore")
    t0 = time.time()
    rows = []
    for nL in map(int, a.nl.split(",")):
        masks = pool(a.G, nL, a.draws, a.n_cand)
        for R2, ls, law in itertools.product(R2_GRID, LAMSTAR, a.laws.split(",")):
            rows += run_cell(a.G, nL, R2, ls, law, masks, a.draws, a.n_cand)
            print(f"G{a.G} nL{nL} R2{R2} lam{ls} {law} {time.time() - t0:.0f}s", flush=True)
    os.makedirs(a.out_dir, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"e4_sim__{a.tag}.csv"), index=False)
    json.dump(dict(G=a.G, draws=a.draws, n_cand=a.n_cand, n_rows=len(rows), wall_s=time.time() - t0),
              open(os.path.join(a.out_dir, f"e4_sim_summary__{a.tag}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
