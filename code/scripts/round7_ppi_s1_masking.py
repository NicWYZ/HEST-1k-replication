"""Round 7 inference track, S1 on the real tasks: D2 with the weighted estimators, one task, arm and n_L per call.

Track document sections 6 and 7 (S1.3); theory sections 1 and 2.1; plan section 1.1. For each estimand (theta3,
theta2; the ACS mean is skipped for the constant arm, as round 5 did) and each balance variable (own, pcF2, pcE2 on
tissue, perm_cluster; own and perm_cluster on census) at p_a 0.1 and 0.01:

* D2's fixed thresholds from round 5's pool (round7_ppi_d2.fixed_thresholds).
* Inclusion probabilities from R accepted samples, R = max(100,000, ceil(400 / pi_gh under simple random selection)),
  capped at 1,000,000, seeds 'r7ppi|S1|pi|...' (theory section 1.3).
* 2,000 evaluation draws: round 5's E4b draws, replayed, where the cell is one of E4b's (n_L <= 12, arm not
  constant); otherwise new draws under 'r7ppi|S1|eval|...'.
* Per draw: the classical mean with textbook_t|fpc|lin and rej_t; HT and Hajek with SYG (HT variance for random size)
  and simulated, apx_size and apx_bal pair probabilities; the cross-fitted difference form (simulated); Broska and
  Howes as if unbalanced. References t_{n-k-1} with the floor nu >= 2 ('res') and t_{n-1} without it ('n1').
* D0 with round 4's draw_L seeds: the classical and tuned estimators, Broska and Howes, and HT and Hajek with exact
  simple-random probabilities (an identity check against the classical mean).

Outputs, in this order: s1m_diag__<tag>.csv (one row per D2 cell), s1m_cells__<tag>.csv (median over genes per cell
and interval), s1m_genes__<tag>.csv.gz (per gene), s1m_pi__<tag>.parquet (pi_hat and se per cluster), summary json.
"""
import argparse
import json
import math
import os
import time

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

import round4_ppi_estimator as E
import round5_ppi_balance as BAL
import round7_ppi_d2 as D2
import round7_ppi_weighting as W
from round5_ppi_e2_regimeB import ACS

LIN, XF = "textbook_t|fpc|lin", "textbook_t|fpc|lin|xf"
NDRAW = 2000
PI_SCHEMA = pa.schema([("vtag", pa.string()), ("arm", pa.string()), ("estimand", pa.string()), ("n_L", pa.int32()),
                       ("balance", pa.string()), ("p_a", pa.float64()), ("column", pa.string()), ("cluster", pa.string()),
                       ("pi_hat", pa.float64()), ("pi_se", pa.float64()), ("pi_hat_half_a", pa.float64()),
                       ("pi_hat_half_b", pa.float64()), ("R", pa.int64())])


def R_for(Gall, n):
    p = n * (n - 1) / (Gall * (Gall - 1))
    return int(min(1_000_000, max(100_000, math.ceil(400 / p))))


def L_from_sel(cell, sel, ng):
    D = sel.shape[0]
    out = np.zeros((D, cell["G"], ng), bool)
    for d in range(D):
        m = D2.Lm_from(cell, sel[d])
        out[d] = m if m.shape[1] == ng else np.broadcast_to(m, (cell["G"], ng))
    return out


def per_draw_round5(cell, Lall, est, nL, pa_, X, rules, design):
    """classical (+tuned) intervals and lambda for the difference form, per draw, with round 5's seeds."""
    D, G, ng = Lall.shape
    res = {}
    lamL = np.zeros((D, G, ng)); cU = np.zeros((D, ng))
    Dst = BAL.stats_arrays(cell["zbar"], cell["fbar"])
    for d in range(D):
        Lm = Lall[d]
        if Lm.sum(0).min() < 2:
            for key in res:
                res[key][0][d] = np.nan
            continue
        for rule in rules:
            out, lam = BAL.estimate_srs_like(cell["zbar"], cell["fbar"], Lm, rule,
                                             f"q2|{cell['vtag']}|nL{nL}|m0|d{d}|{est}|donor|{rule}")
            for iv, (th, v, df) in out.items():
                key = ("classical" if rule == "none" else "tuned", iv)
                if key not in res:
                    res[key] = [np.full((D, ng), np.nan), np.full((D, ng), np.nan), np.full((D, ng), np.nan)]
                res[key][0][d], res[key][1][d], res[key][2][d] = th, v, np.broadcast_to(df, (ng,))
        lr = E.lambda_rule("c_crossfit_design", "donor", Dst, Lm, ~Lm,
                           seed=f"q2|{cell['vtag']}|nL{nL}|m0|d{d}|{est}|donor|c_crossfit_design")
        lamL[d], cU[d] = lr["lamL"], lr["cU"]
        if design == "D2":
            th, v, df = BAL.rej_t(cell["zbar"], X, Lm, pa_)
            key = ("classical", "rej_t")
            if key not in res:
                res[key] = [np.full((D, ng), np.nan), np.full((D, ng), np.nan), np.full((D, ng), np.nan)]
            res[key][0][d], res[key][1][d], res[key][2][d] = th, v, df
    return res, (lamL, cU)


def add_rows(rows, generows, base, key, s, genes):
    est, var, ref = key
    med = lambda a: float(np.nanmedian(a)) if np.isfinite(a).any() else np.nan
    rows.append(dict(base, estimator=est, variance=var, ref=ref, n_genes=int(np.isfinite(s["coverage"]).sum()),
                     coverage_median=med(s["coverage"]), coverage_mean=float(np.nanmean(s["coverage"])) if np.isfinite(s["coverage"]).any() else np.nan,
                     width_median=med(s["width"]), est_over_emp_median=med(s["est_var"] / s["emp_var"]),
                     share_bias_z_gt3=float(np.nanmean(np.abs(s["bias_z"]) > 3)),
                     share_formed_median=med(s["share_formed"]), share_neg_max=float(np.nanmax(s["share_neg"]))))
    for j, g in enumerate(genes):
        generows.append(dict(base, estimator=est, variance=var, ref=ref, gene=g,
                             **{k: float(v[j]) for k, v in s.items()}))


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--parquet", required=True)
    p.add_argument("--perm-parquet", required=True)
    p.add_argument("--ref-parquet", required=True)
    p.add_argument("--ref-arm", required=True)
    p.add_argument("--vtag", required=True)
    p.add_argument("--arm", required=True)
    p.add_argument("--nl", type=int, required=True)
    p.add_argument("--estimands", default="theta3,theta2")
    p.add_argument("--theta2-kind", default="neo_minus_stroma")
    p.add_argument("--balances", default="")
    p.add_argument("--draws", type=int, default=NDRAW)
    p.add_argument("--max-genes", type=int, default=0)
    p.add_argument("--r-cap", type=int, default=1_000_000)
    p.add_argument("--root", default=D2.ROOT)
    p.add_argument("--out-dir", default=".")
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    t0 = time.time()
    tag = f"{a.vtag}__{a.arm}__nL{a.nl}"
    census = a.vtag in ACS
    diag, rows, generows, pirows, skipped = [], [], [], [], []
    for est in a.estimands.split(","):
        if census and est == "theta2" and a.arm == "constant":
            skipped.append(dict(estimand=est, reason="constant arm on the ACS mean, skipped as in round 5"))
            continue
        cell = D2.load_cell(a.parquet, a.perm_parquet, a.ref_parquet, a.ref_arm, a.vtag, a.arm, est, a.root,
                            a.theta2_kind)
        if a.max_genes:
            for kk in ("zbar", "fbar", "theta"):
                cell[kk] = cell[kk][..., :a.max_genes]
            cell["genes"] = cell["genes"][:a.max_genes]
            cell["bal"] = {b: (x[:, :a.max_genes] if x.shape[1] > 1 else x) for b, x in cell["bal"].items()}
        G, Gall, nL = cell["G"], cell["Gall"], a.nl
        genes = cell["genes"]; ng = len(genes)
        if nL > Gall - 2:
            skipped.append(dict(estimand=est, reason=f"n_L {nL} > Gall - 2"))
            continue
        fixed = Gall == G
        bals = a.balances.split(",") if a.balances else (["own", "perm_cluster"] if census else ["own", "pcF2", "pcE2", "perm_cluster"])
        bals = [b for b in bals if b in cell["bal"]]
        for b in set(a.balances.split(",") if a.balances else (["own", "perm_cluster"] if census else ["own", "pcF2", "pcE2", "perm_cluster"])) - set(bals):
            skipped.append(dict(estimand=est, balance=b, reason="balance variable not available for this arm"))
        replay = nL <= 12 and a.arm != "constant"
        first = D2.r5_first(cell, nL, n_cand=D2.BATCH if replay else D2.POOL_CAND)
        print(f"{est} first {time.time() - t0:.0f}s", flush=True)
        theta = cell["theta"]
        # D0
        L0 = np.zeros((a.draws, G, ng), bool)
        for d in range(a.draws):
            L0[d] = np.isin(cell["vid"], first[d, 0])[:, None]
        bad0 = L0.sum(1).min(1) < 2
        L0 = L0[~bad0]
        res0, lam0 = per_draw_round5(cell, L0, est, nL, None, None, ("none", "c_crossfit_design"), "D0")
        pi0 = np.full((G, ng), nL / Gall)
        P0 = np.full((ng, G, G), nL * (nL - 1) / (Gall * (Gall - 1)))
        for j in range(ng):
            np.fill_diagonal(P0[j], 0.0)
        w0 = W.weighted(cell["zbar"], cell["fbar"], L0, pi0, {"exact": P0}, fixed, lam=lam0)
        b0 = W.bh(cell["zbar"], cell["fbar"], L0)
        base = dict(vtag=a.vtag, arm=a.arm, estimand=est, G=G, Gall=Gall, n_L=nL, design="D0", balance="none", k=0,
                    p_a=1.0)
        nn0 = L0.sum(1)
        for (est_, iv), (th, v, df) in res0.items():
            add_rows(rows, generows, base, (est_, iv, "n1"), W.summarise(th, v, df, theta), genes)
        for est_ in ("HT", "H", "HTl"):
            add_rows(rows, generows, base, (est_, "exact", "n1"),
                     W.summarise(w0[est_]["theta"], w0[est_]["var"]["exact"], nn0 - 1, theta), genes)
        add_rows(rows, generows, base, ("BH", "bh", "normal"),
                 W.summarise(b0["theta"], b0["se"] ** 2, np.inf, theta, normal=True), genes)
        idd = float(np.nanmax(np.abs(w0["HT"]["theta"] - res0[("classical", LIN)][0]))) if fixed else np.nan
        diag.append(dict(base, part="D0_identity", ht_minus_classical_max=idd, d0_draws_dropped=int(bad0.sum()),
                         bh_lambda_zero_share=float(b0["lam_zero"].mean())))
        print(f"{est} D0 {time.time() - t0:.0f}s", flush=True)
        # D2
        for b in bals:
            X = cell["bal"][b]
            kx = X.shape[2]
            thr, _ = D2.fixed_thresholds(cell, X, first)
            for pa_ in (0.1, 0.01):
                t = thr[pa_]
                ckey = f"{a.vtag}|{a.arm}|{est}|nL{nL}|{b}|pa{pa_}"
                R = min(R_for(Gall, nL), a.r_cap)
                st = W.pi_stream(X, cell["vid"], Gall, t, nL, R, f"r7ppi|S1|pi|{ckey}")
                pi, se, pgh = W.from_counts(st)
                pia, pib = st["cnt_a"] / st["half"], st["cnt_b"] / (R - st["half"])
                va = BAL.va_nominal(kx, pa_)
                Pb, nfb = W.fix_nonpositive(W.pgh_apx_bal(pi, X, va))
                Ps, nfs = W.fix_nonpositive(W.pgh_apx_size(pi))
                if replay:
                    sel = D2.round5_draws(cell, X, t, first, a.draws)
                    src = "round5_e4b_replay"
                else:
                    sel = D2.d2_stream(cell, X, t, nL, a.draws, f"r7ppi|S1|eval|{ckey}")["acc"]
                    src = "new"
                Lall = L_from_sel(cell, sel, ng)
                res, lam = per_draw_round5(cell, Lall, est, nL, pa_, X, ("none",), "D2")
                bc = lambda A: A if A.shape[-1] == ng else np.broadcast_to(A, A.shape[:-1] + (ng,)).copy()
                pib_ = bc(pi)
                bcP = lambda P: P if P.shape[0] == ng else np.broadcast_to(P, (ng,) + P.shape[1:]).copy()
                pghs = {"sim": bcP(pgh), "apx_size": bcP(Ps), "apx_bal": bcP(Pb)}
                w = W.weighted(cell["zbar"], cell["fbar"], Lall, pib_, pghs, fixed, lam=lam)
                bhr = W.bh(cell["zbar"], cell["fbar"], Lall)
                base = dict(vtag=a.vtag, arm=a.arm, estimand=est, G=G, Gall=Gall, n_L=nL, design="D2", balance=b,
                            k=kx, p_a=pa_)
                nn = Lall.sum(1)
                for (est_, iv), (th, v, df) in res.items():
                    add_rows(rows, generows, base, (est_, iv, "res" if iv == "rej_t" else "n1"),
                             W.summarise(th, v, df, theta), genes)
                for est_ in ("HT", "H", "HTl"):
                    for vnm in (("sim", "apx_size", "apx_bal") if est_ != "HTl" else ("sim",)):
                        for ref, df in (("res", nn - kx - 1), ("n1", nn - 1)):
                            if ref == "n1":
                                s = summarise_nofloor(w[est_]["theta"], w[est_]["var"][vnm], df, theta)
                            else:
                                s = W.summarise(w[est_]["theta"], w[est_]["var"][vnm], df, theta)
                            add_rows(rows, generows, base, (est_, vnm, ref), s, genes)
                add_rows(rows, generows, base, ("BH", "bh", "normal"),
                         W.summarise(bhr["theta"], bhr["se"] ** 2, np.inf, theta, normal=True), genes)
                # diagnostics
                ratio = pi / (nL / Gall)
                off = ~np.eye(G, dtype=bool)
                cnt = pgh[:, off] * R
                good = cnt >= 100
                relb = np.where(good, np.abs(Pb[:, off] / np.where(pgh[:, off] > 0, pgh[:, off], np.nan) - 1), np.nan)
                rels = np.where(good, np.abs(Ps[:, off] / np.where(pgh[:, off] > 0, pgh[:, off], np.nan) - 1), np.nan)
                # HT bias with pi from each half (theory section 1.3)
                bzh = {}
                for hn, ph in (("a", pia), ("b", pib)):
                    php = bc(ph)
                    with np.errstate(divide="ignore", invalid="ignore"):
                        hth = np.where(Lall, cell["zbar"][None] / php[None], 0.0).sum(1) / G
                    sdh = hth.std(0, ddof=1)
                    bzh[hn] = float(np.nanmean(np.abs((hth.mean(0) - theta) / (sdh / np.sqrt(hth.shape[0]))) > 3))
                sc = W.summarise(res[("classical", LIN)][0], res[("classical", LIN)][1], res[("classical", LIN)][2], theta)
                sht = W.summarise(w["HT"]["theta"], w["HT"]["var"]["sim"], nn - kx - 1, theta)
                shh = W.summarise(w["H"]["theta"], w["H"]["var"]["sim"], nn - kx - 1, theta)
                diag.append(dict(base, part="D2", support=pa_ * math.comb(Gall, nL), threshold_median=float(np.median(t)),
                                 R=R, n_candidates=st["n_cand"], eval_draws=src,
                                 pi_ratio_min_median=float(np.median(ratio.min(0))), pi_ratio_min_min=float(ratio.min()),
                                 pi_ratio_max_median=float(np.median(ratio.max(0))), pi_ratio_max_max=float(ratio.max()),
                                 n_columns_with_pi_zero=int((pi.min(0) <= 0).sum()),
                                 share_pairs_pgh_zero=float((pgh[:, off] <= 0).mean()),
                                 min_pair_count=float(cnt.min()), median_pair_count=float(np.median(cnt)),
                                 apx_bal_rel_err_median=float(np.nanmedian(relb)) if np.isfinite(relb).any() else np.nan,
                                 apx_size_rel_err_median=float(np.nanmedian(rels)) if np.isfinite(rels).any() else np.nan,
                                 apx_bal_nonpositive_fixed=nfb, apx_size_nonpositive_fixed=nfs,
                                 share_genes_bias_z_gt3_classical=float(np.nanmean(np.abs(sc["bias_z"]) > 3)),
                                 share_genes_bias_z_gt3_HT=float(np.nanmean(np.abs(sht["bias_z"]) > 3)),
                                 share_genes_bias_z_gt3_H=float(np.nanmean(np.abs(shh["bias_z"]) > 3)),
                                 share_genes_bias_z_gt3_HT_pi_half_a=bzh["a"], share_genes_bias_z_gt3_HT_pi_half_b=bzh["b"],
                                 va_nominal=va, fixed_size=fixed,
                                 draws_with_zero_pair_in_sample=float((w["HT"]["zero"]["sim"] > 0).mean())))
                cols = genes if pi.shape[1] == ng else ["_shared"]
                for j, cname in enumerate(cols):
                    for gi, dn in enumerate(cell["donors"][cell["vid"]]):
                        pirows.append(dict(vtag=a.vtag, arm=a.arm, estimand=est, n_L=nL, balance=b, p_a=pa_,
                                           column=str(cname), cluster=str(dn), pi_hat=float(pi[gi, j]),
                                           pi_se=float(se[gi, j]), pi_hat_half_a=float(pia[gi, j]),
                                           pi_hat_half_b=float(pib[gi, j]), R=R))
                print(f"{est} {b} pa{pa_} {time.time() - t0:.0f}s R {R} cand {st['n_cand']}", flush=True)
    os.makedirs(a.out_dir, exist_ok=True)
    pd.DataFrame(diag).to_csv(os.path.join(a.out_dir, f"s1m_diag__{tag}.csv"), index=False, float_format="%.10g")
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"s1m_cells__{tag}.csv"), index=False, float_format="%.10g")
    pd.DataFrame(skipped).to_csv(os.path.join(a.out_dir, f"s1m_skipped__{tag}.csv"), index=False)
    pd.DataFrame(generows).to_csv(os.path.join(a.out_dir, f"s1m_genes__{tag}.csv.gz"), index=False, float_format="%.10g")
    pq.write_table(pa.Table.from_pandas(pd.DataFrame(pirows, columns=PI_SCHEMA.names), schema=PI_SCHEMA,
                                        preserve_index=False), os.path.join(a.out_dir, f"s1m_pi__{tag}.parquet"))
    json.dump(dict(tag=tag, wall_s=time.time() - t0, n_cells=len(diag), n_rows=len(rows), args=vars(a)),
              open(os.path.join(a.out_dir, f"s1m_summary__{tag}.json"), "w"), indent=1)
    return 0


def summarise_nofloor(th, v, df, theta):
    """W.summarise with t_{df} for every df >= 1 (the 'n1' reference has no floor)."""
    from scipy import stats
    D = th.shape[0]
    df = np.asarray(df, float)
    formed = np.isfinite(v) & np.isfinite(th) & (df >= 1)
    neg = formed & (v < 0)
    vv = np.where(formed, np.maximum(v, 0.0), np.nan)
    q = stats.t.ppf(1 - W.ALPHA / 2, np.where(df >= 1, df, np.nan))
    se = np.sqrt(vv)
    cov = np.where(formed, np.abs(th - theta[None, :]) <= q * se, np.nan)
    thf = np.where(np.isfinite(th), th, np.nan)
    nth = np.isfinite(thf).sum(0)
    mean = np.nanmean(thf, 0); sd = np.nanstd(thf, 0, ddof=1)
    bz = (mean - theta) / (sd / np.sqrt(nth))
    return dict(coverage=np.nanmean(cov, 0), width=np.nanmean(2 * q * se, 0), emp_var=sd ** 2,
                est_var=np.nanmean(vv, 0), bias=mean - theta, bias_z=bz, share_formed=formed.mean(0),
                share_neg=neg.sum(0) / np.maximum(formed.sum(0), 1), n_draws=np.full(th.shape[1], D))


if __name__ == "__main__":
    raise SystemExit(main())
