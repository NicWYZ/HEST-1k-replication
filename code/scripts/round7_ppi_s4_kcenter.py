"""Round 7 inference track, S4: greedy k-center with a uniform random start, computed exactly over the G starts.

Theory: docs/round07/tracks/ppi/round07_ppi_theory.md section 4. One tissue task and arm per call, n_L in
{4, 6, 8, 12}, estimands theta3 and theta2 (theta2 over the valid clusters). Per cell: the exact pi_g and pi_gh, the
share of pairs with pi_gh = 0, the number of distinct samples, and for each interval its exact coverage over the G
starts (conditional, share formed, and coverage_all with a missing interval counted as a miss): textbook_t|fpc|lin
for the classical mean as if simple random, Broska and Howes's interval with bh_t, bh_t_n2 and bh_t_fpc, and HT and
Hajek with apx_size from the exact pi. The exact sd of HT and the classical mean's exact bias and rmse.
Outputs s4_cells__<tag>.csv (median over genes), s4_genes__<tag>.csv.gz, s4_diag__<tag>.csv, s4_pi__<tag>.csv.
"""
import argparse
import json
import os
import time

import numpy as np
import pandas as pd

import round5_ppi_balance as BAL
import round7_ppi_d2 as D2
import round7_ppi_weighting as W
from round7_ppi_s3_cube import bh_variants, summ, add_rows

LIN = "textbook_t|fpc|lin"


def kcenter_samples(Z, nL):
    """Z (G, k) coordinates. Returns S (G starts, G) bool, the sample of each start."""
    G = Z.shape[0]
    Dm = np.sqrt(((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1))
    S = np.zeros((G, G), bool)
    for s in range(G):
        S[s, s] = True
        mind = Dm[s].copy()
        for _ in range(nL - 1):
            m = np.where(S[s], -np.inf, mind)
            g = int(np.argmax(m))                   # first maximum: ties to the lowest index
            S[s, g] = True
            mind = np.minimum(mind, Dm[g])
    assert (S.sum(1) == nL).all()
    return S


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--parquet", required=True); p.add_argument("--perm-parquet", required=True)
    p.add_argument("--ref-parquet", required=True); p.add_argument("--ref-arm", required=True)
    p.add_argument("--vtag", required=True); p.add_argument("--arm", required=True)
    p.add_argument("--nls", default="4,6,8,12")
    p.add_argument("--estimands", default="theta3,theta2")
    p.add_argument("--theta2-kind", default="neo_minus_stroma")
    p.add_argument("--root", default=D2.ROOT)
    p.add_argument("--out-dir", default=".")
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    t0 = time.time()
    tag = f"{a.vtag}__{a.arm}"
    enc = "resnet50" if a.arm in ("permuted", "constant") else a.arm
    rows, generows, diag, pirows, skipped = [], [], [], [], []
    for est in a.estimands.split(","):
        cell = D2.load_cell(a.parquet, a.perm_parquet, a.ref_parquet, a.ref_arm, a.vtag, a.arm, est, a.root,
                            a.theta2_kind)
        emb = D2.embeddings(a.root, a.vtag, enc, cell["donors"])
        if emb is None or not np.isfinite(emb[cell["vid"]]).all():
            skipped.append(dict(estimand=est, reason=f"no finite {enc} embedding for every cluster"))
            continue
        G = cell["G"]; zbar, fbar, theta = cell["zbar"], cell["fbar"], cell["theta"]
        genes = cell["genes"]; ng = len(genes)
        Zc = D2.pcs(emb[cell["vid"]], min(10, G - 1, emb.shape[1]))
        for nL in map(int, a.nls.split(",")):
            if nL > G - 2:
                skipped.append(dict(estimand=est, n_L=nL, reason=f"n_L {nL} > G - 2 (G = {G})"))
                continue
            S = kcenter_samples(Zc, nL)
            pi = S.mean(0)
            Sf = S.astype(float)
            pgh = (Sf.T @ Sf) / G
            np.fill_diagonal(pgh, 0.0)
            off = ~np.eye(G, dtype=bool)
            Lall = np.ascontiguousarray(np.broadcast_to(S[:, :, None], (G, G, ng)))
            base = dict(vtag=a.vtag, arm=a.arm, encoder=enc, estimand=est, G=G, Gall=cell["Gall"], n_L=nL,
                        design="kcenter")
            # classical as if simple random
            th_c = np.full((G, ng), np.nan); v_c = th_c.copy(); df_c = th_c.copy()
            for s in range(G):
                out, _ = BAL.estimate_srs_like(zbar, fbar, np.ascontiguousarray(Lall[s]), "none",
                                               f"r7ppi|S4|{a.vtag}|{a.arm}|{est}|nL{nL}|s{s}")
                th_c[s], v_c[s], df_c[s] = out[LIN]
            ivs = {("classical", LIN, "n1"): (th_c, v_c, df_c, False)}
            pib = np.broadcast_to(pi[:, None], (G, ng)).copy()
            Ps, nfs = W.fix_nonpositive(W.pgh_apx_size(pib))
            w = W.weighted(zbar, fbar, Lall, pib, {"apx_size": Ps}, True)
            for e_ in ("HT", "H"):
                ivs[(e_, "apx_size", "n1")] = (w[e_]["theta"], w[e_]["var"]["apx_size"], np.full((G, ng), nL - 1.0), False)
            ivs.update(bh_variants(zbar, fbar, Lall, G, nL))
            for key, (th, v, df, normal) in ivs.items():
                s_ = summ(th, v, df, theta, normal)
                s_["exact_sd"] = np.sqrt(np.nanmean((th - theta[None]) ** 2, 0))       # rmse over starts
                s_["exact_bias"] = np.nanmean(th, 0) - theta
                add_rows(rows, generows, base, key, s_, genes)
                rows[-1]["exact_rmse_median"] = float(np.nanmedian(s_["exact_sd"]))
                rows[-1]["exact_abs_bias_median"] = float(np.nanmedian(np.abs(s_["exact_bias"])))
            n_distinct = len({tuple(np.flatnonzero(r)) for r in S})
            diag.append(dict(base, n_distinct_samples=n_distinct, pi_min=float(pi.min()), pi_max=float(pi.max()),
                             pi_ratio_min=float(pi.min() / (nL / G)), pi_ratio_max=float(pi.max() / (nL / G)),
                             n_pi_one=int((pi >= 1).sum()), share_pairs_pgh_zero=float((pgh[off] <= 0).mean()),
                             apx_size_nonpositive_fixed=nfs,
                             ht_unbiased_check_max=float(np.nanmax(np.abs(np.nanmean(w["HT"]["theta"], 0) - theta))),
                             wall_s=time.time() - t0))
            for gi, dn in enumerate(cell["donors"][cell["vid"]]):
                pirows.append(dict(base, cluster=str(dn), pi=float(pi[gi])))
            print(f"{est} nL{nL} {time.time() - t0:.0f}s", flush=True)
    os.makedirs(a.out_dir, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"s4_cells__{tag}.csv"), index=False, float_format="%.10g")
    pd.DataFrame(generows).to_csv(os.path.join(a.out_dir, f"s4_genes__{tag}.csv.gz"), index=False, float_format="%.10g")
    pd.DataFrame(diag).to_csv(os.path.join(a.out_dir, f"s4_diag__{tag}.csv"), index=False, float_format="%.10g")
    pd.DataFrame(pirows).to_csv(os.path.join(a.out_dir, f"s4_pi__{tag}.csv"), index=False, float_format="%.10g")
    pd.DataFrame(skipped).to_csv(os.path.join(a.out_dir, f"s4_skipped__{tag}.csv"), index=False)
    json.dump(dict(tag=tag, wall_s=time.time() - t0, n_rows=len(rows), args=vars(a)),
              open(os.path.join(a.out_dir, f"s4_summary__{tag}.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
