"""Round 7 inference track: design D2 as track document section 2.3 defines it, and the S0 anchor (arm 2).

Plan docs/round07/tracks/ppi/round07_ppi_plan.md, sections 1.1 and 3. D2 is rejective selection with round 5's
fixed thresholds and further candidates drawn until one is accepted, never the fallback of d2_select.

* The fixed thresholds. For each task, arm, estimand, n_L and balance variable, the per-column p_a quantiles of the
  Mahalanobis distance over round 5's calibration pool, the first 500 candidates of each of 2,000 draws under round
  5's candidate seeds (round5_ppi_e4b_rejective.cand_idx), computed by round 5's pool_thresholds. They are
  deterministic and reproduce the thresholds of the E4b run; _threshold/ on Longleaf holds only their medians.
* The sampler. Candidates are simple random samples of n_L of all donors, drawn in batches from a numpy generator
  seeded with zlib.crc32 of a seed string; a candidate is accepted for a column when it has at least two valid
  labelled clusters and its distance is at or below that column's threshold. Each column takes its accepted
  candidates in stream order. Accepted candidates of an i.i.d. stream are i.i.d. draws from D2, so the same stream
  also gives the inclusion frequencies of S1.
* round5_draws() replays E4b's own selection (candidate 0 from round 4's draw_L, candidates k >= 1 from
  'r5e4c|...', scanning past 2,000 until accepted), so the anchor can be computed with round 5's samples through
  this module's estimator path and compared with E4b's stored value.

S0 driver (main): one cell, theta3, own balance. Writes s0_arm2__<vtag>__<arm>.csv with, for round 5's draws and for
new draws, the width ratio of rej_t to the D0 classical interval (median over genes of the ratio of mean widths over
2,000 draws, as round5_ppi_e4b_merge.py computes wr_D0cl) and its bootstrap standard error over draws, and
s0_thresholds__<vtag>__<arm>.csv with the per-gene fixed thresholds and their median.
"""
import argparse
import json
import math
import os
import time
import zlib

import numpy as np
import pandas as pd
from scipy import stats

import round4_ppi_q2_masking as Q2
import round5_ppi_balance as BAL
import round5_ppi_estimator as R5
import round5_ppi_e4b_rejective as RJ
from round5_ppi_e2_regimeB import load_arm, ACS
from round5_ppi_e4_selection import pcs, donor_arrays, embeddings

ROOT = "/work/users/w/e/weiyang/hest_replication"
POOL_DRAWS, POOL_CAND, BATCH = 2000, 500, RJ.BATCH
LIN = "textbook_t|fpc|lin"


def seed_of(s):
    return zlib.crc32(s.encode())


def load_cell(parquet, perm_parquet, ref_parquet, ref_arm, vtag, arm, est, root=ROOT, theta2_kind=None):
    """Everything a D2 cell needs, built exactly as round5_ppi_e4b_rejective.main builds it."""
    if theta2_kind is not None:
        Q2.THETA2_KIND = theta2_kind
    data = load_arm(parquet, arm, vtag)
    pdata = load_arm(perm_parquet, "permuted", vtag)
    rdata = load_arm(ref_parquet, ref_arm, vtag)
    for dd in (pdata, rdata):
        assert list(dd["genes"]) == list(data["genes"]), "gene order differs between arms"
        assert list(map(str, dd["donors"])) == list(map(str, data["donors"])), "donor order differs between arms"
    donors = np.asarray(data["donors"])
    genes = list(data["genes"])
    zbar_all, fbar_all, ok = donor_arrays(data, est)
    _, fperm_all, _ = donor_arrays(pdata, est)
    _, fref_all, _ = donor_arrays(rdata, est)
    vid = np.flatnonzero(ok)
    zbar, fbar, fperm, fref = zbar_all[vid], fbar_all[vid], fperm_all[vid], fref_all[vid]
    bal = {"own": fbar[:, :, None], "perm": fperm[:, :, None],
           "perm_cluster": BAL.perm_cluster_variable(fref, genes, f"r5e4b_pc|{vtag}|{est}")}
    bal["pcF2"] = pcs(fbar, 2)[:, None, :]
    emb = None if vtag in ACS else embeddings(root, vtag, "resnet50" if arm == "permuted" else arm, donors)
    if emb is not None and np.isfinite(emb[vid]).all():
        bal["pcE2"] = pcs(emb[vid], 2)[:, None, :]
    return dict(vtag=vtag, arm=arm, est=est, donors=donors, Gall=len(donors), vid=vid, G=len(vid), genes=genes,
                zbar=zbar, fbar=fbar, theta=zbar.mean(0), bal=bal, emb=emb)


def r5_first(cell, nL, draws=POOL_DRAWS, n_cand=BATCH):
    """Round 5's candidates 0..n_cand-1 of every draw, (draws, n_cand, nL) int16 indices over all donors."""
    first = np.empty((draws, n_cand, nL), np.int16)
    for d in range(draws):
        for k in range(n_cand):
            first[d, k] = RJ.cand_idx(cell["donors"], cell["vtag"], nL, d, k)
    return first


def fixed_thresholds(cell, X, first, pas=(0.1, 0.01)):
    """Per-column p_a quantiles over round 5's pool (first POOL_CAND candidates of every draw)."""
    nL = first.shape[2]
    pool = RJ.masks_from(first[:POOL_DRAWS, :POOL_CAND].reshape(-1, nL), cell["Gall"])
    thr, vae = RJ.pool_thresholds(pool, cell["vid"], X, pas)
    return thr, vae


def round5_draws(cell, X, thr, first, draws=POOL_DRAWS):
    """E4b's accepted candidate per draw and column, replayed: (draws, ncol, nL) int16."""
    nL, ncol = first.shape[2], X.shape[1]
    out = np.empty((draws, ncol, nL), np.int16)
    for d in range(draws):
        m0 = RJ.masks_from(first[d], cell["Gall"])
        dd = RJ.dist_valid(m0, cell["vid"], X)[0]
        done = np.zeros(ncol, bool)
        kacc, done = BAL.first_accepted(dd, thr, 0, done)
        sel = kacc.copy()
        cand = {}
        k0 = BATCH
        while not done.all():
            ext = np.stack([RJ.cand_idx(cell["donors"], cell["vtag"], nL, d, k) for k in range(k0, k0 + BATCH)])
            dd = RJ.dist_valid(RJ.masks_from(ext, cell["Gall"]), cell["vid"], X)[0]
            kacc, newdone = BAL.first_accepted(dd, thr, k0, done)
            for j in np.flatnonzero(newdone & ~done):
                cand[j] = ext[kacc[j] - k0]
            sel = np.where(kacc >= 0, kacc, sel)
            done = newdone
            k0 += BATCH
            if k0 > 2_000_000:
                raise RuntimeError(f"no accepted candidate after 2,000,000 candidates, draw {d}")
        for j in range(ncol):
            out[d, j] = first[d, sel[j]] if sel[j] < BATCH else cand[j]
    return out


def srs_batch(rng, Gall, nL, B):
    """B simple random samples of nL of Gall donors, (B, nL) sorted int16."""
    return np.sort(np.argsort(rng.random((B, Gall)), axis=1)[:, :nL], axis=1).astype(np.int16)


def d2_stream(cell, X, thr, nL, n_acc, seed_prefix, batch=20000, max_cand=200_000_000):
    """New D2 draws. Returns dict with acc (n_acc, ncol, nL) int16, the first n_acc accepted candidates of every
    column in stream order, and n_cand, the candidates drawn. Batches are seeded '<seed_prefix>|b<i>'."""
    ncol = X.shape[1]
    acc = np.full((n_acc, ncol, nL), -1, np.int16)
    got = np.zeros(ncol, int)
    n_cand, i = 0, 0
    while (got < n_acc).any():
        rng = np.random.default_rng(seed_of(f"{seed_prefix}|b{i}"))
        C = srs_batch(rng, cell["Gall"], nL, batch)
        dd = RJ.dist_valid(RJ.masks_from(C, cell["Gall"]), cell["vid"], X)[0]
        ok = dd <= thr[None, :]
        for j in np.flatnonzero(got < n_acc):
            rows = np.flatnonzero(ok[:, j])[: n_acc - got[j]]
            acc[got[j]:got[j] + len(rows), j] = C[rows]
            got[j] += len(rows)
        n_cand += batch
        i += 1
        if n_cand > max_cand:
            raise RuntimeError(f"fewer than {n_acc} accepted after {n_cand} candidates")
    return dict(acc=acc, n_cand=n_cand)


def Lm_from(cell, cands):
    """cands (ncol, nL) indices over all donors -> (G, ncol) bool over the valid clusters."""
    ncol = cands.shape[0]
    m = np.zeros((ncol, cell["Gall"]), bool)
    np.put_along_axis(m, cands.astype(np.int64), True, axis=1)
    return m[:, cell["vid"]].T


def widths_rej(cell, X, sel, p_a):
    """Per-draw rej_t widths (draws, ncol) and point estimates."""
    D, ncol = sel.shape[0], sel.shape[1]
    W, T = np.full((D, ncol), np.nan), np.full((D, ncol), np.nan)
    for d in range(D):
        Lm = Lm_from(cell, sel[d])
        th, v, df = BAL.rej_t(cell["zbar"], X, Lm, p_a)
        q = stats.t.ppf(1 - R5.ALPHA / 2, df)
        W[d], T[d] = 2 * q * np.sqrt(np.maximum(v, 0)), th
    return W, T


def widths_d0(cell, nL, est, draws=POOL_DRAWS):
    """D0 classical interval widths per draw, round 4's draw_L seeds as E4b's D0 used them."""
    ncol = cell["zbar"].shape[1]
    W, T = np.full((draws, ncol), np.nan), np.full((draws, ncol), np.nan)
    for d in range(draws):
        Ld = RJ.cand_idx(cell["donors"], cell["vtag"], nL, d, 0)
        Lm = np.broadcast_to(np.isin(cell["vid"], Ld)[:, None], cell["zbar"].shape).copy()
        out, _ = BAL.estimate_srs_like(cell["zbar"], cell["fbar"], Lm, "none",
                                       f"q2|{cell['vtag']}|nL{nL}|m0|d{d}|{est}|donor|none")
        th, v, df = out[LIN]
        q = stats.t.ppf(1 - R5.ALPHA / 2, df)
        W[d], T[d] = 2 * q * np.sqrt(np.maximum(v, 0)), th
    return W, T


def wr_median(Wd, W0, cd=None, c0=None):
    """Median over genes of mean width ratio; with multinomial weights (B, draws) returns (B,)."""
    if cd is None:
        return float(np.nanmedian(np.nanmean(Wd, 0) / np.nanmean(W0, 0)))
    md = (cd @ np.nan_to_num(Wd)) / cd.sum(1, keepdims=True)
    m0 = (c0 @ np.nan_to_num(W0)) / c0.sum(1, keepdims=True)
    return np.nanmedian(md / m0, axis=1)


def boot_se(Wd, W0, seed, n_boot=500):
    rng = np.random.default_rng(seed_of(seed))
    Dd, D0 = Wd.shape[0], W0.shape[0]
    cd = rng.multinomial(Dd, np.full(Dd, 1.0 / Dd), size=n_boot).astype(float)
    c0 = rng.multinomial(D0, np.full(D0, 1.0 / D0), size=n_boot).astype(float)
    return float(np.std(wr_median(Wd, W0, cd, c0), ddof=1))


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--parquet", required=True)
    p.add_argument("--perm-parquet", required=True)
    p.add_argument("--ref-parquet", required=True)
    p.add_argument("--ref-arm", required=True)
    p.add_argument("--vtag", required=True)
    p.add_argument("--arm", required=True)
    p.add_argument("--estimand", default="theta3")
    p.add_argument("--theta2-kind", default="neo_minus_stroma")
    p.add_argument("--nl", type=int, default=8)
    p.add_argument("--balance", default="own")
    p.add_argument("--p-a", type=float, default=0.01)
    p.add_argument("--draws", type=int, default=2000)
    p.add_argument("--root", default=ROOT)
    p.add_argument("--out-dir", default=".")
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    t0 = time.time()
    cell = load_cell(a.parquet, a.perm_parquet, a.ref_parquet, a.ref_arm, a.vtag, a.arm, a.estimand, a.root,
                     a.theta2_kind)
    X = cell["bal"][a.balance]
    first = r5_first(cell, a.nl)
    thr, vae = fixed_thresholds(cell, X, first, (0.1, 0.01))
    t = thr[a.p_a]
    pd.DataFrame(dict(vtag=a.vtag, arm=a.arm, estimand=a.estimand, n_L=a.nl, balance=a.balance, p_a=a.p_a,
                      gene=cell["genes"], threshold=t)).to_csv(
        os.path.join(a.out_dir, f"s0_thresholds__{a.vtag}__{a.arm}.csv"), index=False, float_format="%.17g")
    print(f"thresholds {time.time() - t0:.0f}s", flush=True)
    W0, _ = widths_d0(cell, a.nl, a.estimand, a.draws)
    sel5 = round5_draws(cell, X, t, first, a.draws)
    print(f"round 5 draws {time.time() - t0:.0f}s", flush=True)
    del first
    W5, _ = widths_rej(cell, X, sel5, a.p_a)
    pref = f"r7ppi|S0|{a.vtag}|{a.arm}|{a.estimand}|nL{a.nl}|{a.balance}|pa{a.p_a}|eval"
    st = d2_stream(cell, X, t, a.nl, a.draws, pref)
    print(f"new draws {time.time() - t0:.0f}s, {st['n_cand']} candidates", flush=True)
    W7, _ = widths_rej(cell, X, st["acc"], a.p_a)
    rows = []
    for draws_kind, Wd in (("round5_draws", W5), ("new_draws", W7)):
        rows.append(dict(vtag=a.vtag, arm=a.arm, estimand=a.estimand, n_L=a.nl, balance=a.balance, p_a=a.p_a,
                         draws_kind=draws_kind, n_draws=Wd.shape[0], n_genes=int(np.isfinite(np.nanmean(Wd, 0)).sum()),
                         wr_D0cl=wr_median(Wd, W0),
                         boot_se=boot_se(Wd, W0, f"r7ppi|S0|boot|{a.vtag}|{a.arm}|{draws_kind}"),
                         n_candidates=st["n_cand"] if draws_kind == "new_draws" else np.nan,
                         threshold_median=float(np.median(t))))
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"s0_arm2__{a.vtag}__{a.arm}.csv"), index=False,
                              float_format="%.17g")
    json.dump(dict(wall_s=time.time() - t0, seed_prefix=pref, args=vars(a)),
              open(os.path.join(a.out_dir, f"s0_arm2_summary__{a.vtag}__{a.arm}.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
