"""Round 7 inference track, S4b: the cube design with pi_g, 1 and fbar_g balanced.

Theory: docs/round07/tracks/ppi/round07_ppi_theory.md section 3.9 (and 3.1 to 3.4). S4 memo, section 5.

* cube_p: the fast flight phase on p + 1 units with any number p of balance variables, null vectors by singular value
  decomposition (rank-aware), balance rows scaled per column; landing drops the last balance variable, then the next,
  keeping the size equation to the end. Returns the samples, the relative residual of the fbar equation and
  |N_hat / G - 1|.
* resid_var_p: the residual form of theory 3.4 with x_g = (pi_g, 1, fbar_g), divisor n - rank.
* Intervals: HT and Hajek with the Sen-Yates-Grundy form and simulated pi_gh (primary), apx_size, and the residual
  form; references t_{n - rank} with the floor 2 ('res') and t_{n - 2} ('n2', S3's quantile); Broska and Howes's
  interval and its variants as if simple random.
* Modes: test (S3's test populations), masking (one task, arm and n_L, design cube3_u1), sim (one G, law, n_L cell).
Output files are named s4b_tests.csv, s4bm_*__<tag> and s4b_sim__<tag>. Every summary row carries coverage over formed
draws, coverage_all (no interval counted as a miss) and the share formed.
"""
import argparse
import itertools
import json
import math
import os
import time

import numpy as np
import pandas as pd

import round7_ppi_weighting as W
from round7_ppi_s3_cube import (EPS, NDRAW, R_for, _steps, add_rows, batch_for, bh_variants, pi_diag, summ,
                                target_pi)


def _balance(pi, f, const):
    """a_g = x_g / pi_g, (ncol, G, p), each variable scaled by its mean absolute value per column."""
    rows = [np.ones_like(pi.T)] + ([1.0 / pi.T] if const else []) + [(f / pi).T]
    A = np.stack(rows, -1)
    sc = np.abs(A).mean(1, keepdims=True)
    return A / np.where(sc > 0, sc, 1.0)


def _snap(x):
    x[x <= EPS] = 0.0
    x[x >= 1 - EPS] = 1.0
    return x


def cube_p(pi, f, B, rng, const=True):
    """B cube samples per column with balance variables (pi_g, [1,] fbar_g). Returns xi (B, ncol, G) bool, the
    relative fbar residual (B, ncol) and |N_hat/G - 1| (B, ncol)."""
    G, ncol = pi.shape
    M = B * ncol
    cidx = np.tile(np.arange(ncol), B)
    A = _balance(pi, f, const)
    p = A.shape[-1]
    S = p + 1
    Am = A[cidx]                                            # (M, G, p)
    P = _snap(pi.T[cidx].copy())
    frac = (P > 0) & (P < 1)
    key = rng.random((M, G))
    key[~frac] = np.inf
    ordf = np.argsort(key, axis=1)
    nfrac = frac.sum(1)
    Wk = ordf[:, :S].copy()
    valid = np.arange(S)[None, :] < nfrac[:, None]
    ptr = np.minimum(S, nfrac)

    def step(idx, units, q):
        pv = P[idx[:, None], units]
        Aq = np.transpose(Am[idx[:, None], units][:, :, :q], (0, 2, 1))     # (n, q, q+1)
        v = np.linalg.svd(Aq)[2][:, -1, :]
        v = np.where(np.abs(v) < 1e-12, 0.0, v)
        l1, l2 = _steps(pv, v)
        up = rng.random(len(idx)) < l2 / (l1 + l2)
        newp = _snap(pv + np.where(up, l1, -l2)[:, None] * v)
        P[idx[:, None], units] = newp
        return newp

    while True:                                             # flight
        idx = np.flatnonzero(valid.all(1))
        if not len(idx):
            break
        newp = step(idx, Wk[idx], p)
        res = (newp == 0) | (newp == 1)
        if not res.any():
            raise RuntimeError("cube flight step resolved no unit")
        for s in range(S):
            rr = idx[res[:, s]]
            can = ptr[rr] < nfrac[rr]
            rc = rr[can]
            Wk[rc, s] = ordf[rc, ptr[rc]]
            ptr[rc] += 1
            valid[rr[~can], s] = False
    rows_all = np.arange(M)
    for q in range(p - 1, 0, -1):                           # landing: drop the last variable, then the next
        for _ in range(4 * S):
            pv = np.where(valid, P[rows_all[:, None], Wk], 0.0)
            fr = valid & (pv > 0) & (pv < 1)
            idx = np.flatnonzero(fr.sum(1) >= q + 1)
            if not len(idx):
                break
            o = np.argsort(~fr[idx], axis=1, kind="stable")[:, :q + 1]
            step(idx, Wk[idx[:, None], o], q)
        else:
            raise RuntimeError("cube landing did not finish")
    pv = np.where(valid, P[rows_all[:, None], Wk], 0.0)
    fr = valid & (pv > 0) & (pv < 1)
    one = np.flatnonzero(fr.sum(1) == 1)
    if len(one):                                            # rounding remainder only: Bernoulli(p) keeps the mean
        g = Wk[one, np.argmax(fr[one], axis=1)]
        P[one, g] = (rng.random(len(one)) < P[one, g]).astype(float)
    if (fr.sum(1) > 1).any():
        raise RuntimeError("fractional units left after landing")
    xi = P > 0.5
    if not (xi.sum(1) == np.rint(pi.sum(0))[cidx]).all():
        raise RuntimeError("cube sample size differs from n_L")
    fpi = (f / pi).T[cidx]
    tot = f.sum(0)[cidx]
    den = np.abs(f).sum(0)[cidx]
    rf = np.abs((xi * fpi).sum(1) - tot) / np.where(den > 0, den, 1.0)
    rN = np.abs((xi / pi.T[cidx]).sum(1) / G - 1.0)
    return xi.reshape(B, ncol, G), rf.reshape(B, ncol), rN.reshape(B, ncol)


def pi_sim_p(pi, f, R, seed_prefix, const=True):
    G, ncol = pi.shape
    B = batch_for(G, ncol, 3_000_000)
    cnt = np.zeros((G, ncol)); pair = np.zeros((ncol, G, G)); done = 0; i = 0
    while done < R:
        b = min(B, R - done)
        xi, _, _ = cube_p(pi, f, b, np.random.default_rng(W.seed_of(f"{seed_prefix}|b{i}")), const)
        X = xi.astype(np.float32)
        cnt += X.sum(0).T
        pair += np.einsum("bcg,bch->cgh", X, X, optimize=True)
        done += b; i += 1
    for j in range(ncol):
        np.fill_diagonal(pair[j], 0.0)
    return dict(cnt=cnt, pair=pair, R=R)


def eval_p(pi, f, D, seed_prefix, const=True):
    G, ncol = pi.shape
    B = batch_for(G, ncol, 3_000_000)
    Ls, rf, rN = [], [], []
    done, i = 0, 0
    while done < D:
        b = min(B, D - done)
        xi, a, c = cube_p(pi, f, b, np.random.default_rng(W.seed_of(f"{seed_prefix}|b{i}")), const)
        Ls.append(np.transpose(xi, (0, 2, 1))); rf.append(a); rN.append(c)
        done += b; i += 1
    return np.concatenate(Ls), np.concatenate(rf), np.concatenate(rN)


def resid_var_p(zbar, fbar, Lall, pi_w, pi_x, theta_h, const=True):
    """Theory 3.4 with x_g = (pi_g, [1,] fbar_g). Returns dict HT, H -> (var (D, ncol), rank (D, ncol))."""
    D, G, ncol = Lall.shape
    Lf = Lall.astype(float)
    ip = 1.0 / pi_w
    q = Lf * ((1 - pi_w) / pi_w * ip)[None]
    xs = [np.broadcast_to(pi_x[None], Lall.shape)] + ([np.ones(Lall.shape)] if const else []) + \
         [np.broadcast_to(fbar[None], Lall.shape)]
    X = np.stack(xs, -1)
    Sm = np.einsum("dgc,dgci,dgcj->dcij", q, X, X, optimize=True)
    dsc = np.sqrt(np.maximum(np.einsum("dcii->dci", Sm), 1e-300))
    Sn = Sm / (dsc[..., :, None] * dsc[..., None, :])
    rank = np.linalg.matrix_rank(Sn, tol=1e-9).astype(float)
    Si = np.linalg.pinv(Sn, rcond=1e-9)
    n = Lf.sum(1)
    Nh = (Lf * ip[None]).sum(1)
    out = {}
    for nm, y, den in (("HT", np.broadcast_to(zbar[None], Lall.shape), np.full((D, ncol), float(G))),
                       ("H", zbar[None] - theta_h[:, None, :], Nh)):
        b = np.einsum("dgc,dgci,dgc->dci", q, X, y, optimize=True) / dsc
        c = np.einsum("dcij,dcj->dci", Si, b) / dsc
        e = y - np.einsum("dgci,dci->dgc", X, c, optimize=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            v = (n / (n - rank)) * (q * e ** 2).sum(1) / den ** 2
        out[nm] = (np.where(n - rank > 0, v, np.nan), rank)
    return out


def intervals_p(zbar, fbar, Lall, pi_hat, pi_x, pgh, G, nL, const=True):
    Ps, nfs = W.fix_nonpositive(W.pgh_apx_size(pi_hat))
    w = W.weighted(zbar, fbar, Lall, pi_hat, {"sim": pgh, "apx_size": Ps}, True)
    rv = resid_var_p(zbar, fbar, Lall, pi_hat, pi_x, w["H"]["theta"], const)
    nn = Lall.sum(1).astype(float)
    out = {}
    for e_ in ("HT", "H"):
        th = w[e_]["theta"]
        v, rank = rv[e_]
        for vn, vv in (("sim", w[e_]["var"]["sim"]), ("res", v), ("apx_size", w[e_]["var"]["apx_size"])):
            out[(e_, vn, "res")] = (th, vv, nn - rank, False)
            out[(e_, vn, "n2")] = (th, vv, nn - 2, False)
    out.update(bh_variants(zbar, fbar, Lall, G, nL))
    return out, nfs, rv["H"][1]


def run_test(out_dir, r_pi, n_eval):
    from round7_ppi_s1_tests import pop
    rows = []
    for (G, n, k) in ((51, 8, 1), (24, 8, 1), (15, 6, 2)):
        for law in ("normal", "skewed"):
            t0 = time.time()
            rng = np.random.default_rng(W.seed_of(f"r7ppi|S1test|pop|G{G}|n{n}|k{k}|{law}"))
            z, Xp = pop(G, k, law, rng)
            zbar = z[:, None]; fbar = Xp[:, :1]
            pit = target_pi(np.abs(fbar - fbar.mean(0)), n)
            tag = f"G{G}_n{n}_{law}"
            st = pi_sim_p(pit, fbar, r_pi, f"r7ppi|S4btest|pi|{tag}")
            pih = st["cnt"] / st["R"]; pgh = st["pair"] / st["R"]
            zpi = np.abs(pih - pit) / np.maximum(np.sqrt(pit * (1 - pit) / st["R"]), 1e-12)
            L, rf, rN = eval_p(pit, fbar, n_eval, f"r7ppi|S4btest|eval|{tag}")
            theta = zbar.mean(0)
            iv, nfs, rank = intervals_p(zbar, fbar, L, pih, pit, pgh, G, n)
            ht_t = (L[:, :, 0] * (zbar[:, 0] / pit[:, 0])[None]).sum(1) / G
            bz_t = (ht_t.mean() - theta[0]) / (ht_t.std(ddof=1) / math.sqrt(n_eval))
            base = dict(G=G, n_L=n, law=law, R=st["R"], n_eval=n_eval, pi_z_max=float(zpi.max()),
                        pi_z_gt3=int((zpi > 3).sum()), pi_target_min_ratio=float((pit / (n / G)).min()),
                        n_capped=int((pit >= 1).sum()), share_pairs_pgh_zero=float((pgh[0][~np.eye(G, dtype=bool)] <= 0).mean()),
                        resid_f_median=float(np.median(rf)), resid_f_max=float(rf.max()),
                        resid_N_median=float(np.median(rN)), resid_N_max=float(rN.max()),
                        share_N_exact=float((rN <= 1e-9).mean()), rank_median=float(np.median(rank)),
                        ht_target_pi_bias_z=float(bz_t), wall_s=time.time() - t0)
            for key, (th, v, df, normal) in iv.items():
                s = summ(th, v, df, theta, normal)
                rows.append(dict(base, estimator=key[0], variance=key[1], ref=key[2], coverage=float(s["coverage"][0]),
                                 coverage_all=float(s["coverage_all"][0]), share_formed=float(s["share_formed"][0]),
                                 width=float(s["width"][0]), est_over_emp=float(s["est_var"][0] / s["emp_var"][0]),
                                 emp_var=float(s["emp_var"][0]), bias_z=float(s["bias_z"][0])))
            print(f"test {tag} {time.time() - t0:.0f}s", flush=True)
    os.makedirs(out_dir, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "s4b_tests.csv"), index=False, float_format="%.10g")


def run_masking(a):
    import round7_ppi_d2 as D2
    from round5_ppi_e2_regimeB import ACS
    t0 = time.time()
    tag = f"{a.vtag}__{a.arm}__nL{a.nl}"
    census = a.vtag in ACS
    diag, rows, generows, skipped = [], [], [], []
    for est in a.estimands.split(","):
        if census and est == "theta2" and a.arm == "constant":
            skipped.append(dict(estimand=est, reason="constant arm on the ACS mean, skipped as in round 5"))
            continue
        cell = D2.load_cell(a.parquet, a.perm_parquet, a.ref_parquet, a.ref_arm, a.vtag, a.arm, est, a.root, a.theta2_kind)
        if a.max_genes:
            for kk in ("zbar", "fbar", "theta"):
                cell[kk] = cell[kk][..., :a.max_genes]
            cell["genes"] = cell["genes"][:a.max_genes]
        G, Gall, nL = cell["G"], cell["Gall"], a.nl
        genes = cell["genes"]
        zbar, fbar, theta = cell["zbar"], cell["fbar"], cell["theta"]
        if nL > G - 2:
            skipped.append(dict(estimand=est, design="cube3_u1", reason=f"n_L {nL} > G - 2 (G = {G} valid clusters)"))
            continue
        ckey = f"{a.vtag}|{a.arm}|{est}|nL{nL}|cube3_u1"
        pit = target_pi(np.abs(fbar - fbar.mean(0, keepdims=True)), nL)
        R = min(R_for(G, nL), a.r_cap)
        st = pi_sim_p(pit, fbar, R, f"r7ppi|S4b|pi|{ckey}")
        pih = st["cnt"] / R; pgh = st["pair"] / R
        L, rf, rN = eval_p(pit, fbar, a.draws, f"r7ppi|S4b|eval|{ckey}")
        iv, nfs, rank = intervals_p(zbar, fbar, L, pih, pit, pgh, G, nL)
        base = dict(vtag=a.vtag, arm=a.arm, estimand=est, G=G, Gall=Gall, n_L=nL, design="cube3_u1",
                    balance="pi,1,own", p_a=np.nan)
        for key, (th, v, df, normal) in iv.items():
            add_rows(rows, generows, base, key, summ(th, v, df, theta, normal), genes)
        diag.append(dict(base, R=R, apx_size_nonpositive_fixed=nfs, **pi_diag(pih, pit, pgh, R, nL, G),
                         resid_f_median=float(np.median(rf)), resid_f_max=float(rf.max()),
                         resid_N_median=float(np.median(rN)), resid_N_max=float(rN.max()),
                         share_N_exact=float((rN <= 1e-9).mean()), rank_median=float(np.median(rank)),
                         rank_min=float(rank.min()), wall_s=time.time() - t0))
        print(f"{est} cube3_u1 {time.time() - t0:.0f}s R {R}", flush=True)
    os.makedirs(a.out_dir, exist_ok=True)
    pd.DataFrame(diag).to_csv(os.path.join(a.out_dir, f"s4bm_diag__{tag}.csv"), index=False, float_format="%.10g")
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"s4bm_cells__{tag}.csv"), index=False, float_format="%.10g")
    pd.DataFrame(skipped).to_csv(os.path.join(a.out_dir, f"s4bm_skipped__{tag}.csv"), index=False)
    pd.DataFrame(generows).to_csv(os.path.join(a.out_dir, f"s4bm_genes__{tag}.csv.gz"), index=False, float_format="%.10g")
    json.dump(dict(tag=tag, wall_s=time.time() - t0, n_cells=len(diag), n_rows=len(rows), args=vars(a)),
              open(os.path.join(a.out_dir, f"s4bm_summary__{tag}.json"), "w"), indent=1)


def run_sim(a):
    from round5_ppi_e1_sim import populations
    from round5_ppi_e4_sim import LAWS
    from round7_ppi_s1_sim import cell_row
    t0 = time.time()
    law = dict(normal="normal", skewed=LAWS[1]).get(a.law, a.law)
    lawtag = "n" if law == "normal" else "s"
    G, nL = a.G, a.nl
    tag = f"G{G}_{lawtag}_k1_nL{nL}"
    R = min(R_for(G, nL), a.r_cap)
    rows = []
    for R2, ls in itertools.product(map(float, a.r2.split(",")), map(float, a.lamstar.split(","))):
        z, f = populations(G, R2, ls, 0.0, law)
        theta = z.mean(0)
        ckey = f"G{G}|{lawtag}|nL{nL}|R2{R2}|lam{ls}|cube3_u1"
        pit = target_pi(np.abs(f - f.mean(0)), nL)
        st = pi_sim_p(pit, f, R, f"r7ppi|S4bsim|pi|{ckey}")
        pih = st["cnt"] / R; pgh = st["pair"] / R
        L, rf, rN = eval_p(pit, f, a.draws, f"r7ppi|S4bsim|eval|{ckey}")
        iv, nfs, rank = intervals_p(z, f, L, pih, pit, pgh, G, nL)
        base = dict(G=G, n_L=nL, R2=R2, lambda_star=ls, kappa=0.0, law=lawtag, k=1, design="cube3_u1", p_a=np.nan, R=R,
                    apx_nonpositive_fixed=nfs, resid_f_median=float(np.median(rf)), resid_N_median=float(np.median(rN)),
                    share_N_exact=float((rN <= 1e-9).mean()), **pi_diag(pih, pit, pgh, R, nL, G))
        for key, (th, v, df, normal) in iv.items():
            s = summ(th, v, df, theta, normal)
            r = cell_row(base, key, s, a.draws)
            r["coverage_all_mean"] = float(np.nanmean(s["coverage_all"]))
            rows.append(r)
        print(f"{tag} R2{R2} lam{ls} {time.time() - t0:.0f}s", flush=True)
    os.makedirs(a.out_dir, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"s4b_sim__{tag}.csv"), index=False, float_format="%.10g")
    json.dump(dict(tag=tag, R=R, draws=a.draws, n_rows=len(rows), wall_s=time.time() - t0),
              open(os.path.join(a.out_dir, f"s4b_sim_summary__{tag}.json"), "w"), indent=1)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["test", "masking", "sim"])
    p.add_argument("--out-dir", default=".")
    p.add_argument("--draws", type=int, default=NDRAW)
    p.add_argument("--r-cap", type=int, default=1_000_000)
    p.add_argument("--test-r", type=int, default=1_000_000)
    p.add_argument("--test-eval", type=int, default=20_000)
    p.add_argument("--parquet"); p.add_argument("--perm-parquet"); p.add_argument("--ref-parquet")
    p.add_argument("--ref-arm"); p.add_argument("--vtag"); p.add_argument("--arm"); p.add_argument("--nl", type=int)
    p.add_argument("--estimands", default="theta3,theta2")
    p.add_argument("--theta2-kind", default="neo_minus_stroma")
    p.add_argument("--max-genes", type=int, default=0)
    p.add_argument("--root", default="/work/users/w/e/weiyang/hest_replication")
    p.add_argument("--G", type=int); p.add_argument("--law")
    p.add_argument("--r2", default="0.0,0.2,0.4,0.7,0.9")
    p.add_argument("--lamstar", default="0.6,1.2")
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    if a.mode == "test":
        run_test(a.out_dir, a.test_r, a.test_eval)
    elif a.mode == "masking":
        run_masking(a)
    else:
        run_sim(a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
