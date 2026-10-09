"""Round 5 PPI, interval 3, stage E4b in simulation: E4's simulation with rej_t and redraw.

Memo docs/decisions/round5_ppi_E4_decisions.md section 5, E4b; plan section 8.4. E4's simulation
(round5_ppi_e4_sim.py: E1's generator, G in {15, 24, 51}, n_L in {4, 6, 8, 12}, E1's R2 grid,
lambda* in {0.6, 1.2}, kappa = 0, normal and skewed laws, 60 populations per cell as columns, own
balance on fbar_g, the same candidate pool and seeds) with two changes:

  * rej_t (round5_ppi_balance.rej_t, k = 1) is added under D2.
  * A draw and population with no accepted candidate among the pool's n_cand candidates draws
    further candidates, batches of n_cand under 'r5e4sim|G<G>|nL<n>|d<d>|ext<j>', until one is
    accepted. No draw falls back to its last candidate. The number of candidates used is recorded.

Output e4b_sim__<tag>.csv: E4's columns plus width_mean (mean over populations of the mean interval
width), candidates_mean, candidates_max, n_beyond_pool and support (p_a * C(G, n_L)).
"""
import argparse
import itertools
import json
import math
import os
import time
import zlib

import numpy as np
import pandas as pd

import round5_ppi_balance as BAL
import round5_ppi_estimator as R5
from round5_ppi_e1_sim import populations, R2_GRID, LAMSTAR
from round5_ppi_e4_sim import pool, GRID_G, NL, LAWS


def ext_batch(G, nL, d, j, n_cand):
    rng = np.random.default_rng(zlib.crc32(f"r5e4sim|G{G}|nL{nL}|d{d}|ext{j}".encode()))
    idx = np.argsort(rng.random((n_cand, G)), axis=1)[:, :nL]
    m = np.zeros((n_cand, G), bool)
    np.put_along_axis(m, idx, True, axis=1)
    return m


def d2_select_redraw(dist, masks, f, fc, thr_pa, G, nL, n_draws, n_cand):
    """Returns Lsel (n_draws, G, npop) accepted samples and the candidates used (n_draws, npop)."""
    npop = dist.shape[1]
    D = dist.reshape(n_draws, n_cand, npop)
    thr = thr_pa
    ok = D <= thr[None, None, :]
    has = ok.any(1)
    first = ok.argmax(1)
    Lsel = np.zeros((n_draws, G, npop), bool)
    used = np.where(has, first + 1, 0)
    for d in range(n_draws):
        Lsel[d][:, has[d]] = masks[d][first[d, has[d]], :].T
        miss = np.flatnonzero(~has[d])
        j = 0
        while len(miss):
            me = ext_batch(G, nL, d, j, n_cand)
            dd = ((me.astype(float) @ fc[:, miss]) / nL) ** 2 / f[:, miss].var(0, ddof=1)[None, :]
            okm = dd <= thr[miss][None, :]
            got = okm.any(0)
            k = okm.argmax(0)
            for i_, p in enumerate(miss):
                if got[i_]:
                    Lsel[d][:, p] = me[k[i_]]
                    used[d, p] = n_cand * (j + 1) + k[i_] + 1
            miss = miss[~got]
            j += 1
            if j > 2000:
                raise RuntimeError("no accepted candidate after 2,000 extension batches")
    return Lsel, used


def run_cell(G, nL, R2, ls, law, masks, n_draws, n_cand):
    from scipy import stats
    z, f = populations(G, R2, ls, 0.0, law)
    npop = z.shape[1]
    theta = z.mean(0)
    zc, fc = z - z.mean(0), f - f.mean(0)
    r2_fp = (zc * fc).sum(0) ** 2 / ((zc ** 2).sum(0) * (fc ** 2).sum(0))
    flat = masks.reshape(-1, G).astype(float)
    dist = ((flat @ fc) / nL) ** 2 / f.var(0, ddof=1)[None, :]
    designs = [("D0", 1.0), ("D2", 0.1), ("D2", 0.01), ("D1", np.nan)]
    st = BAL.d1_strata(f, nL) if nL % 2 == 0 else None
    res, cinfo = {}, {}
    for dname, pa in designs:
        if dname == "D2":
            thr = np.quantile(dist, pa, axis=0)
            Lsel, used = d2_select_redraw(dist, masks, f, fc, thr, G, nL, n_draws, n_cand)
            cinfo[pa] = used
        for d in range(n_draws):
            if dname == "D0":
                Lm = np.ascontiguousarray(np.broadcast_to(masks[d, 0][:, None], (G, npop)))
            elif dname == "D2":
                Lm = np.ascontiguousarray(Lsel[d])
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
            if dname == "D2":
                th, v, df = BAL.rej_t(z, f[:, :, None], Lm, pa)
                res.setdefault((dname, pa, "none", "rej_t"), []).append((th, v, np.broadcast_to(df, th.shape)))
    rows, ev0 = [], None
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
        used = cinfo.get(pa) if dname == "D2" else None
        rows.append(dict(G=G, n_L=nL, R2=R2, lambda_star=ls, kappa=0.0, law=law, design=dname, p_a=pa, rule=rule,
                         interval=iv, n_pop=npop, n_draws=len(L), coverage_mean=float(cov.mean()),
                         coverage_p05=float(np.quantile(cov, 0.05)), emp_var_mean=float(ev.mean()),
                         est_over_emp_mean=float((v.mean(0) / ev).mean()),
                         width_mean=float((2 * q * se).mean(0).mean()),
                         var_ratio_to_D0_classical_mean=np.nan, _ev=ev, r2_fp_median=float(np.median(r2_fp)),
                         support=(pa * math.comb(G, nL)) if dname == "D2" else np.nan,
                         candidates_mean=float(used.mean()) if used is not None else np.nan,
                         candidates_max=int(used.max()) if used is not None else -1,
                         n_beyond_pool=int((used > n_cand).sum()) if used is not None else 0))
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
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"e4b_sim__{a.tag}.csv"), index=False)
    json.dump(dict(G=a.G, draws=a.draws, n_cand=a.n_cand, n_rows=len(rows), wall_s=time.time() - t0),
              open(os.path.join(a.out_dir, f"e4b_sim_summary__{a.tag}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
