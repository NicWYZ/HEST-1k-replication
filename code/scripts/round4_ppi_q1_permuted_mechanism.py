#!/usr/bin/env python
"""Round 4, PPI track, Q1: why B1's donor-weighted lambda for the permuted predictor on
theta_2 is far from 0 (addendum 1 section 3 asks the Q1 report to explain it).

Reads the Q0 anchor's per-spot predictions (b1_predictions__CCRCC__resnet50.parquet), rebuilds
B1's permuted arm exactly (resnet50 predictions permuted over all rows of the file under
crc32('CCRCC|permute'), round3_b1_ppi.py line 687) and B1's donor-level values for theta_2 and
theta_3 (donor-weighted population), and checks them against the sufficient statistics
(b1_suffstats__CCRCC__resnet50.npz) before using them.

Then, per estimand, over all valid donors and per gene: the ratio sd(t_d) / sd(tf_d), the OLS
slope of t_d on tf_d, and over 200 crc32 draws of n_L in {6, 8, 12} labelled donors the share of
(gene, draw) cells where the donor-pairs lambda (rule a = rule b for this population) is clipped
at exactly 0 and at exactly 1. Output q1_permuted_lambda_mechanism.csv.
"""
import argparse
import os
import sys
import zlib

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_ppi_estimator as E  # noqa: E402

NEO_HI, STR_LO = 0.7, 0.3


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--pred", required=True)
    p.add_argument("--suff", required=True)
    p.add_argument("--out-dir", required=True)
    a = p.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    t = pq.read_table(a.pred).to_pandas()
    genes = [c[3:] for c in t.columns if c.startswith("y__")]
    F = t[[f"f__{g}" for g in genes]].to_numpy(np.float64)
    pr = np.random.default_rng(zlib.crc32("CCRCC|permute".encode()))
    Fp_all = F[pr.permutation(len(t))]
    keep = t.joined.to_numpy(bool)
    t, Fp = t[keep], Fp_all[keep]
    Y = t[[f"y__{g}" for g in genes]].to_numpy(np.float64)
    don = t.donor_id.to_numpy()
    dl = sorted(set(don))
    di = np.array([dl.index(d) for d in don])
    m, neo = t.m_std.to_numpy(), t.frac_neoplastic.to_numpy()
    out, check = [], []
    z = np.load(a.suff, allow_pickle=True)
    for est in ("theta2", "theta3"):
        T = np.full((len(dl), len(genes)), np.nan)
        Tf = np.full_like(T, np.nan)
        for k in range(len(dl)):
            s = di == k
            if est == "theta2":
                pn, ps = (neo[s] > NEO_HI).mean(), (neo[s] < STR_LO).mean()
                if pn == 0 or ps == 0:
                    continue
                w = (neo[s] > NEO_HI) / pn - (neo[s] < STR_LO) / ps
            else:
                v = m[s].var()
                if v <= 0:
                    continue
                w = (m[s] - m[s].mean()) / v
            T[k] = (w[:, None] * Y[s]).mean(0)
            Tf[k] = (w[:, None] * Fp[s]).mean(0)
        ok = np.isfinite(T[:, 0])
        # check against B1's sufficient statistics (donor population, permuted arm)
        S1 = z[f"full|permuted|{est}|donor|S1"]
        dos = z["donor_of_slide"]
        npg = z["n_per_slide"]
        valid = z[f"valid|{est}|donor|group"]
        g_genes = [str(g) for g in z[f"genes|{est}"]]
        gi = [genes.index(g) for g in g_genes]
        dmax = 0.0
        for k, d in enumerate(dl):
            sel = (dos == d) & valid
            if not sel.any() or not ok[k]:
                continue
            tf_b1 = S1[sel][:, :, 1].sum(0) / npg[sel].sum()
            dmax = max(dmax, float(np.max(np.abs(tf_b1 - Tf[k, gi]))))
        check.append(dict(estimand=est, max_abs_diff_tf_vs_b1_suffstats=dmax))
        Tk, Tfk = T[ok], Tf[ok]
        sdr = Tk.std(0) / Tfk.std(0)
        a_ = Tk - Tk.mean(0)
        b_ = Tfk - Tfk.mean(0)
        slope = (a_ * b_).sum(0) / (b_ * b_).sum(0)
        G = int(ok.sum())
        idx = np.flatnonzero(ok)
        for n_L in (6, 8, 12):
            lam = []
            for dr in range(200):
                rng = np.random.default_rng(zlib.crc32(f"q1mech|{est}|nL{n_L}|d{dr}".encode()))
                L = rng.choice(idx, n_L, replace=False)
                Lm = np.zeros(T.shape, bool)
                Lm[L] = True
                Um = np.zeros(T.shape, bool)
                Um[idx] = True
                Um &= ~Lm
                lam.append(E._cluster_lambda_donor(np.nan_to_num(T), np.nan_to_num(Tf), Lm, Um))
            lam = np.array(lam)
            out.append(dict(estimand=est, population="donor", n_L=n_L, n_valid_donors=G,
                            n_genes=len(genes), n_draws=200,
                            sd_ratio_t_over_tf_median=float(np.median(sdr)),
                            ols_slope_t_on_tf_median=float(np.median(slope)),
                            ols_slope_q25=float(np.quantile(slope, .25)),
                            ols_slope_q75=float(np.quantile(slope, .75)),
                            lambda_median=float(np.median(lam)),
                            frac_lambda_eq_0=float((lam == 0).mean()),
                            frac_lambda_eq_1=float((lam == 1).mean())))
    pd.DataFrame(out).to_csv(f"{a.out_dir}/q1_permuted_lambda_mechanism.csv", index=False)
    pd.DataFrame(check).to_csv(f"{a.out_dir}/q1_permuted_lambda_mechanism_check.csv", index=False)
    print(pd.DataFrame(check).to_string(index=False))
    print(pd.DataFrame(out).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
