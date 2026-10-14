"""Round 7 inference track, S1 in simulation: round 5's E4b simulation with the weighted estimators.

Track document section 6 and S1.3; theory section 1. One G, law, k and n_L per call, over E1's R2 grid and
lambda* in {0.6, 1.2}, kappa = 0, 60 populations per cell as columns (round5_ppi_e1_sim.populations).

* k = 1 balances on the own f_g, exactly as E4b's simulation: the pool (round5_ppi_e4_sim.pool, 'r5e4sim' seeds,
  1,000 draws x 1,000 candidates), the p_a quantile over the pool as the threshold, and E4b's own accepted draws,
  replayed with round5_ppi_e4b_sim.d2_select_redraw.
* k = 2 adds a second balance variable drawn N(0, 1) per cluster and population, independent of everything else
  ('r7ppi|S1sim|x2|...'), with the same pool, the Mahalanobis threshold over it and the same scanning and extension
  seeds as E4b.
* G = 51, n_L = 16 is the added cell family, with the same procedure (the pool seeds exist for any n_L).
* Inclusion probabilities from R = max(100,000, ceil(400 / pi_gh^SRS)) accepted samples per population,
  'r7ppi|S1sim|pi|...'.
* Estimators as round7_ppi_s1_masking.py: classical with textbook_t|fpc|lin and rej_t, HT, Hajek (sim, apx_size,
  apx_bal) and the difference form (sim), each with references 'res' (t_{n-k-1}, floor 2) and 'n1' (t_{n-1});
  Broska and Howes as if unbalanced; D0 with the classical and tuned estimators and Broska and Howes.

With --by-population, also s1_sim_pop__<tag>.csv (S2b item 2). Output s1_sim__<tag>.csv, one row per cell and interval: coverage mean and 5% quantile over populations, mean width,
mean ratio of estimated to empirical variance, the mean over populations of |bias| / sd and its noise-corrected root
mean square, the share of populations with |standardised bias| > 3, and the cell's design diagnostics.
"""
import argparse
import itertools
import json
import math
import os
import time

import numpy as np
import pandas as pd

import round4_ppi_estimator as E
import round5_ppi_balance as BAL
import round5_ppi_e4b_sim as R4b
import round7_ppi_weighting as W
from round5_ppi_e1_sim import populations, R2_GRID, LAMSTAR
from round5_ppi_e4_sim import pool, LAWS

LIN, XF = "textbook_t|fpc|lin", "textbook_t|fpc|lin|xf"


def replay_k(dist_fn, masks, thr, G, nL, n_draws, n_cand, npop):
    """E4b's scanning for any distance: first pool candidate at or below the threshold per draw and population,
    else extension batches under E4b's 'r5e4sim|...|ext<j>' seeds. Returns Lsel (n_draws, G, npop)."""
    Lsel = np.zeros((n_draws, G, npop), bool)
    for d in range(n_draws):
        dd = dist_fn(masks[d])                          # (n_cand, npop)
        ok = dd <= thr[None, :]
        has = ok.any(0); first = ok.argmax(0)
        Lsel[d][:, has] = masks[d][first[has], :].T
        miss = np.flatnonzero(~has); j = 0
        while len(miss):
            me = R4b.ext_batch(G, nL, d, j, n_cand)
            okm = dist_fn(me)[:, miss] <= thr[miss][None, :]
            got = okm.any(0); kk = okm.argmax(0)
            for i_, p in enumerate(miss):
                if got[i_]:
                    Lsel[d][:, p] = me[kk[i_]]
            miss = miss[~got]; j += 1
            if j > 2000:
                raise RuntimeError("no accepted candidate after 2,000 extension batches")
    return Lsel


def summ(th, v, df, theta, normal=False, nofloor=False):
    from round7_ppi_s1_masking import summarise_nofloor
    return summarise_nofloor(th, v, df, theta) if nofloor else W.summarise(th, v, df, theta, normal=normal)


def cell_row(base, key, s, D):
    est, var, ref = key
    b_over_sd = np.abs(s["bias"]) / np.sqrt(s["emp_var"])
    rms = np.sqrt(np.maximum(np.nanmean((s["bias"] ** 2) / s["emp_var"]) - 1.0 / D, 0.0))
    return dict(base, estimator=est, variance=var, ref=ref, n_pop=len(s["coverage"]),
                coverage_mean=float(np.nanmean(s["coverage"])), coverage_p05=float(np.nanquantile(s["coverage"], 0.05)),
                width_mean=float(np.nanmean(s["width"])), est_over_emp_mean=float(np.nanmean(s["est_var"] / s["emp_var"])),
                emp_var_mean=float(np.nanmean(s["emp_var"])), abs_bias_over_sd_mean=float(np.nanmean(b_over_sd)),
                bias_over_sd_rms_corrected=float(rms), share_pop_bias_z_gt3=float(np.nanmean(np.abs(s["bias_z"]) > 3)),
                share_formed_mean=float(np.nanmean(s["share_formed"])), share_neg_max=float(np.nanmax(s["share_neg"])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--G", type=int, required=True)
    ap.add_argument("--law", required=True)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--nl", type=int, required=True)
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--n-cand", type=int, default=1000)
    ap.add_argument("--r2", default=",".join(map(str, R2_GRID)))
    ap.add_argument("--lamstar", default=",".join(map(str, LAMSTAR)))
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--by-population", action="store_true",
                    help="also write s1_sim_pop__<tag>.csv, one row per D2 cell, estimator and population (S2 memo, S2b item 2)")
    a = ap.parse_args()
    np.seterr(all="ignore")
    t0 = time.time()
    law = dict(normal="normal", skewed=LAWS[1]).get(a.law, a.law)
    lawtag = "n" if law == "normal" else "s"
    G, nL, k = a.G, a.nl, a.k
    tag = f"G{G}_{lawtag}_k{k}_nL{nL}"
    masks = pool(G, nL, a.draws, a.n_cand)
    flat = masks.reshape(-1, G)
    vid = np.arange(G)
    R = int(min(1_000_000, max(100_000, math.ceil(400 / (nL * (nL - 1) / (G * (G - 1)))))))
    rows = []
    poprows = []
    for R2, ls in itertools.product(map(float, a.r2.split(",")), map(float, a.lamstar.split(","))):
        z, f = populations(G, R2, ls, 0.0, law)
        npop = z.shape[1]
        theta = z.mean(0)
        if k == 1:
            X = f[:, :, None]
        else:
            x2 = np.empty((G, npop))
            for p_ in range(npop):
                x2[:, p_] = np.random.default_rng(W.seed_of(f"r7ppi|S1sim|x2|G{G}|R2{R2}|lam{ls}|{lawtag}|p{p_}")).normal(size=G)
            X = np.stack([f, x2], 2)
        dist = W.Dist(X, vid, G)
        mdist = lambda m: BAL.mahalanobis_pool(m, X)
        Dst = BAL.stats_arrays(z, f)
        base0 = dict(G=G, n_L=nL, R2=R2, lambda_star=ls, kappa=0.0, law=lawtag, k=k)

        def per_draw(Lsel, design, pa_):
            D = Lsel.shape[0]
            res = {}
            lamL = np.zeros((D, G, npop)); cU = np.zeros((D, npop))
            for d in range(D):
                Lm = np.ascontiguousarray(Lsel[d])
                for rule in (("none", "c_crossfit_design") if design == "D0" else ("none",)):
                    out, _ = BAL.estimate_srs_like(z, f, Lm, rule, f"r5e4simx|G{G}|nL{nL}|d{d}|{design}")
                    for iv, (th, v, df) in out.items():
                        key = ("classical" if rule == "none" else "tuned", iv)
                        res.setdefault(key, [np.full((D, npop), np.nan) for _ in range(3)])
                        res[key][0][d], res[key][1][d], res[key][2][d] = th, v, np.broadcast_to(df, (npop,))
                lr = E.lambda_rule("c_crossfit_design", "donor", Dst, Lm, ~Lm, seed=f"r5e4simx|G{G}|nL{nL}|d{d}|{design}")
                lamL[d], cU[d] = lr["lamL"], lr["cU"]
                if design == "D2":
                    th, v, df = BAL.rej_t(z, X, Lm, pa_)
                    res.setdefault(("classical", "rej_t"), [np.full((D, npop), np.nan) for _ in range(3)])
                    res[("classical", "rej_t")][0][d], res[("classical", "rej_t")][1][d], res[("classical", "rej_t")][2][d] = th, v, df
            return res, (lamL, cU)

        # D0
        L0 = np.ascontiguousarray(np.broadcast_to(masks[:, 0][:, :, None], (a.draws, G, npop)))
        res0, lam0 = per_draw(L0, "D0", None)
        P0 = np.full((npop, G, G), nL * (nL - 1) / (G * (G - 1)))
        for j in range(npop):
            np.fill_diagonal(P0[j], 0)
        w0 = W.weighted(z, f, L0, np.full((G, npop), nL / G), {"exact": P0}, True, lam=lam0)
        b0 = W.bh(z, f, L0)
        base = dict(base0, design="D0", p_a=1.0)
        for (e_, iv), (th, v, df) in res0.items():
            rows.append(cell_row(base, (e_, iv, "n1"), summ(th, v, df, theta), a.draws))
        for e_ in ("HT", "H", "HTl"):
            rows.append(cell_row(base, (e_, "exact", "n1"), summ(w0[e_]["theta"], w0[e_]["var"]["exact"], nL - 1, theta), a.draws))
        rows.append(cell_row(base, ("BH", "bh", "normal"), summ(b0["theta"], b0["se"] ** 2, np.inf, theta, normal=True), a.draws))
        # D2
        dpool = mdist(flat) if k > 1 else None
        for pa_ in (0.1, 0.01):
            if k == 1:
                fc = f - f.mean(0)
                d1 = ((flat.astype(float) @ fc) / nL) ** 2 / f.var(0, ddof=1)[None, :]
                thr1 = np.quantile(d1, pa_, axis=0)
                Lsel, _ = R4b.d2_select_redraw(d1, masks, f, fc, thr1, G, nL, a.draws, a.n_cand)
                thr_used = thr1
            else:
                thr = np.quantile(np.where(np.isfinite(dpool), dpool, np.nan), pa_, axis=0)
                Lsel = replay_k(mdist, masks, thr, G, nL, a.draws, a.n_cand, npop)
                thr_used = thr
            ckey = f"G{G}|{lawtag}|k{k}|nL{nL}|R2{R2}|lam{ls}|pa{pa_}"
            st = W.pi_stream(X, vid, G, thr_used, nL, R, f"r7ppi|S1sim|pi|{ckey}")
            pi, se, pgh = W.from_counts(st)
            va = BAL.va_nominal(k, pa_)
            Pb, nfb = W.fix_nonpositive(W.pgh_apx_bal(pi, X, va))
            Ps, nfs = W.fix_nonpositive(W.pgh_apx_size(pi))
            res, lam = per_draw(Lsel, "D2", pa_)
            w = W.weighted(z, f, Lsel, pi, {"sim": pgh, "apx_size": Ps, "apx_bal": Pb}, True, lam=lam)
            bhr = W.bh(z, f, Lsel)
            off = ~np.eye(G, dtype=bool)
            cnt = pgh[:, off] * R
            good = cnt >= 100
            relb = np.where(good, np.abs(Pb[:, off] / np.where(pgh[:, off] > 0, pgh[:, off], np.nan) - 1), np.nan)
            ratio = pi / (nL / G)
            base = dict(base0, design="D2", p_a=pa_, support=pa_ * math.comb(G, nL), R=R, n_candidates=st["n_cand"],
                        pi_ratio_min_median=float(np.median(ratio.min(0))), pi_ratio_max_median=float(np.median(ratio.max(0))),
                        min_pair_count=float(cnt.min()), share_pairs_pgh_zero=float((pgh[:, off] <= 0).mean()),
                        apx_bal_rel_err_median=float(np.nanmedian(relb)) if np.isfinite(relb).any() else np.nan,
                        apx_nonpositive_fixed=nfb + nfs)
            for (e_, iv), (th, v, df) in res.items():
                rows.append(cell_row(base, (e_, iv, "res" if iv == "rej_t" else "n1"), summ(th, v, df, theta), a.draws))
            for e_ in ("HT", "H", "HTl"):
                for vnm in (("sim", "apx_size", "apx_bal") if e_ != "HTl" else ("sim",)):
                    rows.append(cell_row(base, (e_, vnm, "res"), summ(w[e_]["theta"], w[e_]["var"][vnm], nL - k - 1, theta), a.draws))
                    rows.append(cell_row(base, (e_, vnm, "n1"), summ(w[e_]["theta"], w[e_]["var"][vnm], nL - 1, theta, nofloor=True), a.draws))
            rows.append(cell_row(base, ("BH", "bh", "normal"), summ(bhr["theta"], bhr["se"] ** 2, np.inf, theta, normal=True), a.draws))
            if a.by_population:
                pz = (pgh[:, off] <= 0).mean(1)
                for nm, (th_, v_, df_) in (("classical", res[("classical", LIN)]),
                                           ("HT", (w["HT"]["theta"], w["HT"]["var"]["sim"], nL - k - 1)),
                                           ("H", (w["H"]["theta"], w["H"]["var"]["sim"], nL - k - 1))):
                    sp = summ(th_, v_, df_, theta)
                    for p_ in range(npop):
                        poprows.append(dict(base0, p_a=pa_, estimator=nm, population=p_, pi_ratio_min=float(ratio[:, p_].min()),
                                            n_clusters_pi_zero=int((pi[:, p_] <= 0).sum()), share_pairs_pgh_zero=float(pz[p_]),
                                            bias=float(sp["bias"][p_]), sd=float(np.sqrt(sp["emp_var"][p_])),
                                            bias_z=float(sp["bias_z"][p_]), coverage=float(sp["coverage"][p_]),
                                            share_formed=float(sp["share_formed"][p_])))
            print(f"{tag} R2{R2} lam{ls} pa{pa_} {time.time() - t0:.0f}s", flush=True)
        os.makedirs(a.out_dir, exist_ok=True)
        pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"s1_sim__{tag}.csv"), index=False, float_format="%.10g")
        if a.by_population:
            pd.DataFrame(poprows).to_csv(os.path.join(a.out_dir, f"s1_sim_pop__{tag}.csv"), index=False, float_format="%.10g")
    json.dump(dict(tag=tag, R=R, draws=a.draws, n_cand=a.n_cand, n_rows=len(rows), wall_s=time.time() - t0),
              open(os.path.join(a.out_dir, f"s1_sim_summary__{tag}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
