"""Round 5 PPI, stage E4 diagnostic: inclusion frequencies under rejective sampling (acceptance 2).

E4 acceptance check 2 expects balancing on the permuted predictor to leave the classical estimator's
variance unchanged. On several tasks it fell below 1. A permuted predictor carries no information
about the outcome, but its donor means fbar_g have a variance that depends on the donor (its spot
count and, for theta3, its weights), so rejecting samples whose mean of fbar_g is far from the
population mean can change which donors are likely to be labelled. This script measures that.

For one task, the perm balance, D2 with p_a in {0.1, 0.01}, n_L in {6, 8, 12}, both estimands, with
exactly the candidate pool and selection of round5_ppi_e4_selection.py, it writes per donor and
gene-median the inclusion frequency over the accepted draws against n_L/G, the donor's spot count,
and per gene the standardised bias of the classical estimator, (mean - theta)/(sd/sqrt(draws)).
Output: e4_inclusion__<vtag>.csv (per donor), e4_inclusion_bias__<vtag>.csv (per gene, summarised).
"""
import argparse
import os
import zlib

import numpy as np
import pandas as pd
from scipy import stats

import round4_ppi_q2_masking as Q2
import round5_ppi_balance as BAL
from round5_ppi_e2_regimeB import load_arm
from round5_ppi_e4_selection import donor_arrays


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--perm-parquet", required=True)
    p.add_argument("--vtag", required=True)
    p.add_argument("--draws", type=int, default=200)
    p.add_argument("--n-cand", type=int, default=2000)
    p.add_argument("--nl-grid", default="6,8,12")
    p.add_argument("--theta2-kind", default="neo_minus_stroma", choices=("neo_minus_stroma", "mean"))
    p.add_argument("--out-dir", default=".")
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    Q2.THETA2_KIND = a.theta2_kind
    pdata = load_arm(a.perm_parquet, "permuted", a.vtag)
    donors = pdata["donors"]
    Gall = len(donors)
    M = np.bincount(pdata["didx"], minlength=Gall).astype(float)
    rows, brows = [], []
    for est in Q2.ESTS:
        zbar_all, fperm_all, ok = donor_arrays(pdata, est)
        vid = np.flatnonzero(ok)
        G = len(vid)
        zbar, fperm = zbar_all[vid], fperm_all[vid]
        ng = zbar.shape[1]
        theta = zbar.mean(0)
        for nL in map(int, a.nl_grid.split(",")):
            if nL > Gall - 2:
                continue
            masks = np.zeros((a.draws * a.n_cand, Gall), bool)
            for d in range(a.draws):
                Ld = Q2.B1.draw_L(list(donors), nL, f"q2|{a.vtag}|nL{nL}|d{d}")
                masks[d * a.n_cand, np.isin(donors, Ld)] = True
                for k in range(1, a.n_cand):
                    perm = np.random.default_rng(zlib.crc32(f"r5e4c|{a.vtag}|nL{nL}|d{d}|k{k}".encode())).permutation(Gall)
                    masks[d * a.n_cand + k, perm[:nL]] = True
            mv = masks[:, vid]
            nlab = mv.sum(1)
            mv = mv & (nlab >= 2)[:, None]
            dd = BAL.mahalanobis_pool(mv, fperm[:, :, None])
            dd[nlab < 2] = np.inf
            for pa in (1.0, 0.1, 0.01):
                sel, thr, nmiss = BAL.d2_select(dd, a.draws, a.n_cand, pa)
                inc = np.zeros((G, ng)); th = []
                for d in range(a.draws):
                    Lm = mv[d * a.n_cand + sel[d]].T
                    inc += Lm
                    n = Lm.sum(0)
                    th.append(np.where(Lm, zbar, 0).sum(0) / np.maximum(n, 1))
                inc /= a.draws
                th = np.array(th)
                zb = (th.mean(0) - theta) / (th.std(0, ddof=1) / np.sqrt(a.draws))
                fm = np.median(inc, axis=1)
                rho = stats.spearmanr(fm, M[vid]).correlation if G > 2 else np.nan
                rho_sd = stats.spearmanr(fm, fperm.std(1)).correlation if G > 2 else np.nan
                for i, g in enumerate(vid):
                    rows.append(dict(vtag=a.vtag, estimand=est, n_L=nL, p_a=pa, donor=str(donors[g]),
                                     spot_count=M[g], inclusion_median_over_genes=fm[i], expected=nL / G,
                                     spearman_inclusion_vs_spots=rho, spearman_inclusion_vs_sd_fperm=rho_sd))
                brows.append(dict(vtag=a.vtag, estimand=est, n_L=nL, p_a=pa, G=G, n_genes=ng,
                                  bias_z_median=float(np.median(zb)), bias_z_abs_median=float(np.median(np.abs(zb))),
                                  frac_genes_abs_bias_z_gt_3=float((np.abs(zb) > 3).mean()),
                                  inclusion_sd_over_donors=float(fm.std()), spearman_inclusion_vs_spots=rho))
                print(est, nL, pa, round(rho, 3) if rho == rho else rho, flush=True)
    os.makedirs(a.out_dir, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"e4_inclusion__{a.vtag}.csv"), index=False)
    pd.DataFrame(brows).to_csv(os.path.join(a.out_dir, f"e4_inclusion_bias__{a.vtag}.csv"), index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
