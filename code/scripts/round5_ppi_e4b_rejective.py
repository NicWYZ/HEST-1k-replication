"""Round 5 PPI, interval 3, stage E4b on the real tasks: an interval that uses the balance.

docs/decisions/round5_ppi_E4_decisions.md section 5, E4b; plan section 8.4; theory section 3. One
task and arm per call. E4's real-task masking (round5_ppi_e4_selection.py) with:

  * 2,000 accepted draws per cell (--draws), the first 200 on E4's seeds. Candidate 0 of draw d is
    round 4's draw (round3_b1_ppi.draw_L, 'q2|<vtag>|nL<n>|d<d>'), candidate k >= 1 the first n_L of
    a permutation under 'r5e4c|<vtag>|nL<n>|d<d>|k<k>', exactly as E4, continued past k = 1,999.
  * D2's threshold: the p_a quantile of the Mahalanobis distance over a calibration pool of the
    first --pool-cand candidates of every draw (2,000 x 500 = 1,000,000 samples by default, against
    E4's 200 x 2,000), per column. Each draw scans its candidates in order and, per column, accepts
    the first at or below the threshold; a column with no accepted candidate in the first 2,000
    continues with further candidates until one is accepted. No draw falls back to its last
    candidate. The number of candidates used is recorded.
  * Balance variables own, pcF2, pcE2 (tissue tasks), perm (the unit-level permuted predictor's
    fbar_g) and perm_cluster (the reference arm's own fbar_g permuted across the valid clusters with
    crc32 seed 'r5e4b_pc|<vtag>|<estimand>|<gene>'; reference arm resnet50 on tissue, package on ACS).
  * Designs D0, D1 (two per stratum on own, pcF1, pcE1, perm, perm_cluster), D2 at p_a 0.1 and 0.01.
  * Intervals: textbook_t|fpc|lin for the classical mean (rule none) and the tuned estimator,
    textbook_t|fpc|lin|xf for the tuned estimator (rule c_crossfit_design), rej_t under D2 (classical
    mean, balance variables of the design), strat_t under D1.
  * Beside every D2 cell: support p_a * C(G, n_L), candidates used per accepted draw, the empirical
    v_a (mean distance over accepted pool candidates over the mean over the pool), the inclusion
    frequency's sd over clusters and its Spearman correlation with |x_g - Xbar| (k = 1) or the
    Mahalanobis norm of x_g - Xbar (k = 2), and the share of genes with |standardised bias| > 3.
  * Acceptance 3: bootstrap over draws (500 replicates, each design's draws resampled with
    replacement jointly for all genes, independently between designs, crc32 seed
    'r5e4b_boot|<vtag>|<arm>|<est>|nL<n>|<design>|<balance>|<p_a>') of the ratio of median-over-genes
    empirical variances of the classical mean under the design and under D0.

Every summary row is written twice, over all draws (n_sub = draws) and over the first 200 draws
(n_sub = 200), the latter for acceptance 1 against E4. Per-draw classical estimates are kept in
_draws/ (npz, float32) for re-analysis and are not part of the committed record.
"""
import argparse
import json
import math
import os
import time
import zlib

import numpy as np
import pandas as pd

import round4_ppi_q2_masking as Q2
import round5_ppi_balance as BAL
import round5_ppi_estimator as R5
from round5_ppi_e2_regimeB import load_arm, ACS
from round5_ppi_e4_selection import pcs, donor_arrays, embeddings

NL = (4, 6, 8, 12)
BATCH = 2000
RULES = ("none", "c_crossfit_design")
N_BOOT = 500
SUB = 200


def cand_idx(donors, vtag, nL, d, k):
    if k == 0:
        Ld = Q2.B1.draw_L(list(donors), nL, f"q2|{vtag}|nL{nL}|d{d}")
        return np.flatnonzero(np.isin(donors, Ld))
    perm = np.random.default_rng(zlib.crc32(f"r5e4c|{vtag}|nL{nL}|d{d}|k{k}".encode())).permutation(len(donors))
    return np.sort(perm[:nL])


def masks_from(idx, Gall):
    """idx (K, n_L) int indices over all donors -> (K, Gall) bool masks."""
    idx = np.asarray(idx)
    m = np.zeros((idx.shape[0], Gall), bool)
    np.put_along_axis(m, idx.astype(np.int64), True, axis=1)
    return m


def dist_valid(masks_all, vid, X):
    mv = masks_all[:, vid]
    nlab = mv.sum(1)
    mv = mv & (nlab >= 2)[:, None]
    with np.errstate(invalid="ignore", divide="ignore"):
        dd = BAL.mahalanobis_pool(mv, X)
    dd[nlab < 2] = np.inf
    return np.where(np.isfinite(dd), dd, np.inf), mv


def pool_thresholds(pool_masks, vid, X, pas, chunk_cols=20, chunk_rows=200000):
    """Per column p_a quantiles of the distance over the pool, and the empirical v_a."""
    ncol = X.shape[1]
    thr = {pa: np.full(ncol, np.inf) for pa in pas}
    vae = {pa: np.full(ncol, np.nan) for pa in pas}
    for c0 in range(0, ncol, chunk_cols):
        cs = slice(c0, min(ncol, c0 + chunk_cols))
        parts = []
        for r0 in range(0, len(pool_masks), chunk_rows):
            dd, _ = dist_valid(pool_masks[r0:r0 + chunk_rows], vid, X[:, cs, :])
            # float64: a float32 threshold can round below the smallest distance when the support is a
            # handful of samples (lung theta2), and then no candidate is ever accepted
            parts.append(dd)
        D = np.concatenate(parts, 0)
        fin = np.isfinite(D)
        Dn = np.where(fin, D, np.nan)
        mall = np.nanmean(Dn, 0)
        for pa in pas:
            t = np.nanquantile(Dn, pa, axis=0)
            thr[pa][cs] = t
            acc = np.where(fin & (D <= t[None, :]), D, np.nan)
            vae[pa][cs] = np.nanmean(acc, 0) / mall
        del D, Dn
    return thr, vae


def summarise(acc, theta, cell, genes, rows, generows, n_sub=None, gene_rows=True):
    from scipy import stats
    for (rule, iv), L in acc.items():
        L = L if n_sub is None else [x for x in L if x[3] < n_sub]
        th = np.array([x[0] for x in L]); v = np.array([x[1] for x in L])
        df = np.array([np.broadcast_to(x[2], th.shape[1:]) for x in L])
        q = stats.t.ppf(1 - R5.ALPHA / 2, df)
        se = np.sqrt(np.maximum(v, 0))
        cov = (np.abs(th - theta[None, :]) <= q * se).mean(0)
        ev = th.var(0, ddof=1)
        mv = np.nanmean(v, 0)
        w = np.nanmean(2 * q * se, 0)
        okg = np.isfinite(ev) & (ev > 0) & np.isfinite(mv)
        med = lambda a: float(np.median(a[okg])) if okg.any() else np.nan
        rows.append(dict(cell, rule=rule, interval=iv, n_sub=len(L), n_genes=int(okg.sum()),
                         emp_var_median=med(ev), est_var_over_emp_var_median=med(mv / np.where(ev > 0, ev, np.nan)),
                         coverage_median=med(cov), coverage_mean=float(np.mean(cov[okg])) if okg.any() else np.nan,
                         width_median=med(w)))
        if gene_rows:
            for j, g in enumerate(genes):
                if okg[j]:
                    generows.append(dict(cell, rule=rule, interval=iv, n_sub=len(L), gene=g, emp_var=ev[j],
                                         est_var=mv[j], coverage=cov[j], width=w[j]))


def boot_ratio(th_d, th_0, seed, n_boot=N_BOOT):
    """Ratio of median-over-genes empirical variances, design over D0, with a bootstrap se."""
    def medvar(th, c=None):
        if c is None:
            return np.nanmedian(th.var(0, ddof=1))
        D = th.shape[0]
        s1 = c @ th; s2 = c @ (th ** 2)
        return np.nanmedian((s2 - s1 ** 2 / D) / (D - 1), axis=1)
    r = medvar(th_d) / medvar(th_0)
    rng = np.random.default_rng(zlib.crc32(seed.encode()))
    Dd, D0 = th_d.shape[0], th_0.shape[0]
    cd = rng.multinomial(Dd, np.full(Dd, 1.0 / Dd), size=n_boot).astype(float)
    c0 = rng.multinomial(D0, np.full(D0, 1.0 / D0), size=n_boot).astype(float)
    rb = medvar(th_d.astype(float), cd) / medvar(th_0.astype(float), c0)
    return float(r), float(np.std(rb, ddof=1))


def main(argv=None):
    from scipy import stats
    p = argparse.ArgumentParser()
    p.add_argument("--parquet", required=True)
    p.add_argument("--perm-parquet", required=True, help="the base parquet of the permuted control")
    p.add_argument("--ref-parquet", required=True, help="the reference arm (resnet50 on tissue, package on ACS) for perm_cluster")
    p.add_argument("--ref-arm", required=True)
    p.add_argument("--vtag", required=True)
    p.add_argument("--arm", required=True)
    p.add_argument("--root", default="/work/users/w/e/weiyang/hest_replication")
    p.add_argument("--draws", type=int, default=2000)
    p.add_argument("--pool-cand", type=int, default=500)
    p.add_argument("--nl-grid", default=",".join(map(str, NL)))
    p.add_argument("--estimands", default=",".join(Q2.ESTS))
    p.add_argument("--theta2-kind", default="neo_minus_stroma", choices=("neo_minus_stroma", "mean"))
    p.add_argument("--max-genes", type=int, default=0)
    p.add_argument("--out-dir", default=".")
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    Q2.THETA2_KIND = a.theta2_kind
    t0 = time.time()
    data = load_arm(a.parquet, a.arm, a.vtag)
    pdata = load_arm(a.perm_parquet, "permuted", a.vtag)
    rdata = load_arm(a.ref_parquet, a.ref_arm, a.vtag)
    if a.max_genes:
        for dd in (data, pdata, rdata):
            dd["genes"] = dd["genes"][:a.max_genes]
            dd["Y"], dd["P"] = dd["Y"][:, :a.max_genes], dd["P"][:, :a.max_genes]
    for dd in (pdata, rdata):
        assert list(dd["genes"]) == list(data["genes"]), "gene order differs between arms"
        assert list(map(str, dd["donors"])) == list(map(str, data["donors"])), "donor order differs between arms"
    donors = np.asarray(data["donors"])
    Gall = len(donors)
    genes = list(data["genes"])
    enc = "resnet50" if a.arm == "permuted" else a.arm
    emb = None if a.vtag in ACS else embeddings(a.root, a.vtag, enc, donors)
    os.makedirs(a.out_dir, exist_ok=True)
    os.makedirs(os.path.join(a.out_dir, "_draws"), exist_ok=True)
    rows, generows, diag, boots, skipped = [], [], [], [], []
    tag = f"{a.vtag}__{a.arm}"
    for est in a.estimands.split(","):
        zbar_all, fbar_all, ok = donor_arrays(data, est)
        _, fperm_all, _ = donor_arrays(pdata, est)
        _, fref_all, _ = donor_arrays(rdata, est)
        vid = np.flatnonzero(ok)
        G = len(vid)
        zbar, fbar, fperm, fref = zbar_all[vid], fbar_all[vid], fperm_all[vid], fref_all[vid]
        ng = zbar.shape[1]
        theta = zbar.mean(0)
        bal = {"own": fbar[:, :, None], "perm": fperm[:, :, None],
               "perm_cluster": BAL.perm_cluster_variable(fref, genes, f"r5e4b_pc|{a.vtag}|{est}")}
        bal["pcF2"] = pcs(fbar, 2)[:, None, :]
        if emb is not None and np.isfinite(emb[vid]).all():
            bal["pcE2"] = pcs(emb[vid], 2)[:, None, :]
        d1fam = {"own": bal["own"][:, :, 0], "pcF": pcs(fbar, 1)[:, None, 0], "perm": bal["perm"][:, :, 0],
                 "perm_cluster": bal["perm_cluster"][:, :, 0]}
        if "pcE2" in bal:
            d1fam["pcE"] = pcs(emb[vid], 1)[:, None, 0]
        for nL in map(int, a.nl_grid.split(",")):
            if nL > Gall - 2:
                continue
            tn = time.time()
            # candidates 0..BATCH-1 of every draw, as index arrays over all donors
            first = np.empty((a.draws, BATCH, nL), np.int16)
            for d in range(a.draws):
                for k in range(BATCH):
                    first[d, k] = cand_idx(donors, a.vtag, nL, d, k)
            pool = masks_from(first[:, :a.pool_cand].reshape(-1, nL), Gall)
            thr, vae = {}, {}
            for b in bal:
                thr[b], vae[b] = pool_thresholds(pool, vid, bal[b], (0.1, 0.01))
            del pool
            # D2 scanning: per draw, per balance, per p_a, the accepted candidate per column
            sel = {(b, pa): np.full((a.draws, bal[b].shape[1]), -1) for b in bal for pa in (0.1, 0.01)}
            extra = {}
            for d in range(a.draws):
                m0 = masks_from(first[d], Gall)
                done = {key: np.zeros(bal[key[0]].shape[1], bool) for key in sel}
                dists = {b: dist_valid(m0, vid, bal[b])[0] for b in bal}
                for key in sel:
                    kacc, done[key] = BAL.first_accepted(dists[key[0]], thr[key[0]][key[1]], 0, done[key])
                    sel[key][d] = kacc
                k0 = BATCH
                while not all(v.all() for v in done.values()):
                    ext = np.stack([cand_idx(donors, a.vtag, nL, d, k) for k in range(k0, k0 + BATCH)])
                    me = masks_from(ext, Gall)
                    for key in sel:
                        if done[key].all():
                            continue
                        dd = dist_valid(me, vid, bal[key[0]])[0]
                        kacc, newdone = BAL.first_accepted(dd, thr[key[0]][key[1]], k0, done[key])
                        sel[key][d] = np.where(kacc >= 0, kacc, sel[key][d])
                        done[key] = newdone
                    for key in sel:
                        for kk in np.unique(sel[key][d]):
                            if k0 <= kk < k0 + BATCH:
                                extra[(d, int(kk))] = ext[kk - k0].copy()
                    k0 += BATCH
                    if k0 > 2_000_000:
                        raise RuntimeError(f"no accepted candidate after 2,000,000 candidates, draw {d}")

            def cand(d, k):
                return first[d, k] if k < BATCH else extra[(d, k)]

            def Lmat(d, ks):
                """ks (ncol,) accepted candidate per column -> Lm (G, ng) over the valid clusters."""
                ks = np.broadcast_to(ks, (ng,)) if np.ndim(ks) == 0 or len(ks) == 1 else ks
                Lm = np.zeros((G, ng), bool)
                for kk in np.unique(ks):
                    m = np.isin(vid, cand(d, int(kk)))
                    Lm[np.ix_(m, ks == kk)] = True
                return Lm

            supp_G = math.comb(G, nL) if nL <= G else 0
            th_classical = {}
            # D0 and D2
            designs = [("D0", "none", 1.0)] + [("D2", b, pa) for b in bal for pa in (0.1, 0.01)]
            for dname, b, pa in designs:
                acc = {}
                incl = np.zeros((G, ng))
                kept = 0
                for d in range(a.draws):
                    if dname == "D0":
                        Lm = Lmat(d, np.zeros(1, int))
                    else:
                        s = sel[(b, pa)][d]
                        Lm = Lmat(d, s if len(s) == ng else np.full(ng, s[0]))
                    if Lm.sum(0).min() < 2:
                        continue
                    kept += 1
                    incl += Lm
                    for rule in RULES:
                        out, lam = BAL.estimate_srs_like(zbar, fbar, Lm, rule, f"q2|{a.vtag}|nL{nL}|m0|d{d}|{est}|donor|{rule}")
                        for iv, (th, v, df) in out.items():
                            acc.setdefault((rule, iv), []).append((th, v, df, d))
                    if dname == "D2":
                        X = bal[b]
                        th, v, df = BAL.rej_t(zbar, X, Lm, pa)
                        acc.setdefault(("none", "rej_t"), []).append((th, v, df, d))
                cell = dict(vtag=a.vtag, arm=a.arm, estimand=est, G=G, n_L=nL, design=dname, balance=b, p_a=pa,
                            n_draws=kept)
                if ("none", "rej_t") in acc and all(np.isnan(x[1]).all() for x in acc[("none", "rej_t")]):
                    skipped.append(dict(cell, interval="rej_t", reason=f"n_L - k - 1 = {np.nanmax(acc[('none', 'rej_t')][0][2]):.0f} < 2"))
                    del acc[("none", "rej_t")]
                summarise(acc, theta, cell, genes, rows, generows)
                summarise(acc, theta, cell, genes, rows, generows, n_sub=SUB, gene_rows=False)
                thc = np.array([x[0] for x in acc[("none", "textbook_t|fpc|lin")]], dtype=np.float32)
                th_classical[(dname, b, pa)] = thc
                if dname == "D2":
                    # rej_t point estimate equals the classical mean (acceptance 2)
                    if ("none", "rej_t") in acc:
                        thr_ = np.array([x[0] for x in acc[("none", "rej_t")]], dtype=np.float32)
                        a2 = float(np.nanmax(np.abs(thr_ - thc)))
                    else:
                        a2 = np.nan
                    fr = incl / max(kept, 1)
                    X = np.broadcast_to(bal[b], (G, ng, bal[b].shape[2]))
                    Xc = X - X.mean(0, keepdims=True)
                    if X.shape[2] == 1:
                        dev = np.abs(Xc[:, :, 0])
                    else:
                        S = np.einsum("gci,gcj->cij", Xc, Xc) / (G - 1)
                        dev = np.sqrt(np.einsum("gci,cij,gcj->gc", Xc, np.linalg.pinv(S), Xc))
                    rho = np.array([stats.spearmanr(fr[:, j], dev[:, j])[0] if np.std(fr[:, j]) > 0 else np.nan
                                    for j in range(ng)])
                    sd_th = thc.std(0, ddof=1)
                    bz = (thc.mean(0) - theta) / (sd_th / np.sqrt(len(thc)))
                    nc = sel[(b, pa)] + 1
                    diag.append(dict(vtag=a.vtag, arm=a.arm, estimand=est, G=G, n_L=nL, balance=b, p_a=pa,
                                     k=int(bal[b].shape[2]), support=pa * supp_G,
                                     threshold_median=float(np.median(thr[b][pa])),
                                     va_nominal=BAL.va_nominal(int(bal[b].shape[2]), pa),
                                     va_empirical_median=float(np.nanmedian(vae[b][pa])),
                                     candidates_mean=float(nc.mean()), candidates_max=int(nc.max()),
                                     n_beyond_first_batch=int((sel[(b, pa)] >= BATCH).sum()),
                                     inclusion_sd_median=float(np.median(fr.std(0, ddof=1))),
                                     spearman_inclusion_vs_dev_median=float(np.nanmedian(rho)),
                                     frac_genes_abs_bias_z_gt_3=float(np.nanmean(np.abs(bz) > 3)),
                                     acc2_rej_minus_classical_max=a2))
            # D1
            for fam, x in d1fam.items():
                if nL < 4 or nL % 2 or nL > G:
                    if nL > G:
                        skipped.append(dict(vtag=a.vtag, arm=a.arm, estimand=est, G=G, n_L=nL, design="D1",
                                            balance=fam, interval="strat_t", reason="n_L exceeds the valid clusters"))
                    continue
                xx = x if x.shape[1] == ng else np.broadcast_to(x, (G, ng))
                st = BAL.d1_strata(np.ascontiguousarray(x if x.shape[1] == 1 else x), nL)
                st_full = np.ascontiguousarray(np.broadcast_to(st, (G, ng))) if st.shape[1] == 1 else st
                acc = {}
                for d in range(a.draws):
                    rng = np.random.default_rng(zlib.crc32(f"r5e4D1|{a.vtag}|nL{nL}|d{d}|{est}|{fam if fam not in ('pcF', 'pcE') else fam + '1'}".encode()))
                    Ld = BAL.d1_draw(st, rng)
                    Lm = np.ascontiguousarray(np.broadcast_to(Ld, (G, ng))) if Ld.shape[1] == 1 else Ld
                    for rule in RULES:
                        out, lam = BAL.estimate_d1(zbar, fbar, Lm, st_full, rule,
                                                   f"r5e4x|{a.vtag}|nL{nL}|d{d}|{est}|{fam if fam not in ('pcF', 'pcE') else fam + '1'}")
                        for iv, (th, v, df) in out.items():
                            acc.setdefault((rule, iv), []).append((th, v, np.broadcast_to(df, (ng,)), d))
                cell = dict(vtag=a.vtag, arm=a.arm, estimand=est, G=G, n_L=nL, design="D1", balance=fam, p_a=np.nan,
                            n_draws=a.draws)
                summarise(acc, theta, cell, genes, rows, generows)
                summarise(acc, theta, cell, genes, rows, generows, n_sub=SUB, gene_rows=False)
                th_classical[("D1", fam, np.nan)] = np.array([x[0] for x in acc[("none", "strat_t")]], dtype=np.float32)
            # acceptance 3 bootstrap, every D2 and D1 cell against D0
            th0 = th_classical[("D0", "none", 1.0)]
            for (dname, b, pa), thd in th_classical.items():
                if dname == "D0":
                    continue
                r, se = boot_ratio(thd, th0, f"r5e4b_boot|{a.vtag}|{a.arm}|{est}|nL{nL}|{dname}|{b}|{pa}")
                boots.append(dict(vtag=a.vtag, arm=a.arm, estimand=est, G=G, n_L=nL, design=dname, balance=b, p_a=pa,
                                  support=(pa * supp_G) if dname == "D2" else np.nan, ratio=r, boot_se=se,
                                  z_from_1=(r - 1) / se if se > 0 else np.nan, n_boot=N_BOOT))
            np.savez_compressed(os.path.join(a.out_dir, "_draws", f"e4b_theta_classical__{tag}__{est}__nL{nL}.npz"),
                                **{f"{k[0]}|{k[1]}|{k[2]}": v for k, v in th_classical.items()}, theta=theta.astype(np.float32))
            print(f"{est} nL{nL} {time.time() - tn:.0f}s (total {time.time() - t0:.0f}s)", flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"e4b_rejective__{tag}.csv"), index=False)
    pd.DataFrame(generows).to_csv(os.path.join(a.out_dir, f"e4b_rejective_genes__{tag}.csv.gz"), index=False)
    pd.DataFrame(diag).to_csv(os.path.join(a.out_dir, f"e4b_d2_diagnostics__{tag}.csv"), index=False)
    pd.DataFrame(boots).to_csv(os.path.join(a.out_dir, f"e4b_bootstrap__{tag}.csv"), index=False)
    pd.DataFrame(skipped).to_csv(os.path.join(a.out_dir, f"e4b_skipped__{tag}.csv"), index=False)
    json.dump(dict(vtag=a.vtag, arm=a.arm, draws=a.draws, pool_cand=a.pool_cand, batch=BATCH, n_rows=len(rows),
                   estimands=a.estimands, nl_grid=a.nl_grid, embeddings=emb is not None, wall_s=time.time() - t0),
              open(os.path.join(a.out_dir, f"e4b_rejective_summary__{tag}.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
