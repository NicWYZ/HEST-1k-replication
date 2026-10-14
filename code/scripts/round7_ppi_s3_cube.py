"""Round 7 inference track, S3: the adaptive, balanced design (cube method) and the D2/D0 mixture.

Theory: docs/round07/tracks/ppi/round07_ppi_theory.md section 3. Track document section 2.3, S2 memo section 5.

* target_pi: tau = 0.5 mixture of a score and uniform probabilities, with the memo's cap rule (theory 3.1).
* cube: the fast flight phase of the cube method on p + 1 = 3 units at a time, balance variables (pi_g, fbar_g),
  then landing by dropping the fbar_g row (theory 3.2). Vectorised over draws and columns.
* pi_sim: simulated pi_g, pi_gh, the inexact-balance share, from R draws of the implemented sampler.
* resid_var: the residual-form variance for the Hajek and HT means (theory 3.4).
* Modes:
  test     the synthetic test of theory 3.6 on S1's test populations;
  masking  one task, arm and n_L: cube with score u1 (|fbar_g - Fbar|) and, on tissue, u2 (nearest-neighbour
           distance in the first 10 PCs of the mean embeddings), and the mixture of D2 (own, p_a 0.1 and 0.01) and D0
           with coin 0.5, for theta3 and theta2 (theta2 cube draws over the valid clusters);
  sim      one (G, law, n_L) cell of round 5's simulation, k = 1, cube with u1 and the mixture.
Every summary row carries coverage over formed draws, the share formed, and coverage_all (a draw with no interval
counted as a miss, S2 memo section 2).
"""
import argparse
import itertools
import json
import math
import os
import time

import numpy as np
import pandas as pd
from scipy import stats

import round7_ppi_weighting as W

ALPHA = W.ALPHA
TAU = 0.5
EPS = 1e-9
NDRAW = 2000


# ---------------------------------------------------------------- design

def target_pi(u, nL, tau=TAU):
    """u (G, ncol) >= 0 -> pi (G, ncol), sum nL per column, capped at 1 by the memo's rule."""
    u = np.asarray(u, float)
    G, ncol = u.shape
    s = u.sum(0)
    with np.errstate(divide="ignore", invalid="ignore"):
        sc = np.where(s[None, :] > 0, u / np.where(s > 0, s, 1.0)[None, :], 1.0 / G)
    pi = tau * nL * sc + (1 - tau) * nL / G
    for _ in range(G + 1):
        cap = pi >= 1.0
        over = (pi > 1.0 + 1e-12).any(0)
        if not over.any():
            break
        for j in np.flatnonzero(over):
            c = pi[:, j] >= 1.0
            free = ~c
            pi[c, j] = 1.0
            pi[free, j] *= (nL - c.sum()) / pi[free, j].sum()
    return np.minimum(pi, 1.0)


def _steps(p, v):
    """largest lambda1 (along +v) and lambda2 (along -v) keeping p in [0, 1]; p, v (M, m)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        up = np.where(v > 0, (1 - p) / v, np.where(v < 0, -p / v, np.inf))
        dn = np.where(v > 0, p / v, np.where(v < 0, (p - 1) / v, np.inf))
    return up.min(1), dn.min(1)


def cube(pi, f, B, rng):
    """B cube samples per column. pi, f (G, ncol). Returns xi (B, ncol, G) bool and the relative fbar balance
    residual (B, ncol) |sum_L f/pi - sum f| / sum |f| (0 when f is identically 0)."""
    G, ncol = pi.shape
    M = B * ncol
    cidx = np.tile(np.arange(ncol), B)
    P = pi.T[cidx].copy()                                   # (M, G)
    with np.errstate(divide="ignore", invalid="ignore"):
        a2 = (f / pi).T                                     # (ncol, G)
    A2 = a2[cidx]
    P[P >= 1 - EPS] = 1.0
    P[P <= EPS] = 0.0
    frac = (P > 0) & (P < 1)
    key = rng.random((M, G))
    key[~frac] = np.inf
    ordf = np.argsort(key, axis=1)
    nfrac = frac.sum(1)
    Wk = ordf[:, :3].copy()
    valid = np.arange(3)[None, :] < nfrac[:, None]
    ptr = np.minimum(3, nfrac)
    rows_all = np.arange(M)
    alt = np.array([1.0, -1.0, 0.0])
    # flight
    while True:
        idx = np.flatnonzero(valid.all(1))
        if not len(idx):
            break
        Wi = Wk[idx]
        p = P[idx[:, None], Wi]
        r2 = A2[idx[:, None], Wi]
        r1 = np.ones_like(r2)
        v = np.cross(r1, r2)
        nrm = np.linalg.norm(v, axis=1)
        scale = np.linalg.norm(r2, axis=1) + 1.0
        deg = ~(nrm > 1e-10 * scale)
        v[deg] = alt
        u = rng.random(len(idx))
        l1, l2 = _steps(p, v)
        go_up = u < l2 / (l1 + l2)
        newp = p + np.where(go_up, l1, -l2)[:, None] * v
        newp[newp <= EPS] = 0.0
        newp[newp >= 1 - EPS] = 1.0
        P[idx[:, None], Wi] = newp
        res = (newp == 0) | (newp == 1)
        if not res.any():
            raise RuntimeError("cube flight step resolved no unit")
        for s in range(3):
            rr = idx[res[:, s]]
            can = ptr[rr] < nfrac[rr]
            rc = rr[can]
            Wk[rc, s] = ordf[rc, ptr[rc]]
            ptr[rc] += 1
            valid[rr[~can], s] = False
    # landing: first balance row only (fixed size), v = (1, -1) on two fractional units
    for _ in range(4):
        pv = np.where(valid, P[rows_all[:, None], Wk], 0.0)
        fr = valid & (pv > 0) & (pv < 1)
        nf = fr.sum(1)
        if not nf.any():
            break
        two = np.flatnonzero(nf >= 2)
        if len(two):
            o = np.argsort(~fr[two], axis=1, kind="stable")[:, :2]
            g = Wk[two[:, None], o]
            p = P[two[:, None], g]
            v = np.tile(np.array([1.0, -1.0]), (len(two), 1))
            l1, l2 = _steps(p, v)
            go_up = rng.random(len(two)) < l2 / (l1 + l2)
            newp = p + np.where(go_up, l1, -l2)[:, None] * v
            newp[newp <= EPS] = 0.0
            newp[newp >= 1 - EPS] = 1.0
            P[two[:, None], g] = newp
        one = np.flatnonzero(nf == 1)
        if len(one):                                        # rounding remainder only: Bernoulli(p) keeps the mean
            o = np.argmax(fr[one], axis=1)
            g = Wk[one, o]
            P[one, g] = (rng.random(len(one)) < P[one, g]).astype(float)
    xi = P > 0.5
    size = xi.sum(1)
    exp_size = np.rint(pi.sum(0))[cidx]
    if not (size == exp_size).all():
        raise RuntimeError("cube sample size differs from n_L")
    fx = np.where(np.isfinite(A2), A2, 0.0)
    tot = f.sum(0)[cidx]
    den = np.abs(f).sum(0)[cidx]
    resid = np.abs((xi * fx).sum(1) - tot) / np.where(den > 0, den, 1.0)
    return xi.reshape(B, ncol, G), resid.reshape(B, ncol)


def batch_for(G, ncol, target=6_000_000):
    return int(max(64, min(50_000, target // max(1, G * ncol))))


def pi_sim(pi, f, R, seed_prefix):
    """R cube draws per column, batches seeded '<seed_prefix>|b<i>'. Returns dict cnt (G, ncol), pair (ncol, G, G),
    R, inexact share (ncol,), resid median (ncol,)."""
    G, ncol = pi.shape
    B = batch_for(G, ncol)
    cnt = np.zeros((G, ncol)); pair = np.zeros((ncol, G, G)); inex = np.zeros(ncol); done = 0; i = 0
    rmed = []
    while done < R:
        b = min(B, R - done)
        xi, res = cube(pi, f, b, np.random.default_rng(W.seed_of(f"{seed_prefix}|b{i}")))
        X = xi.astype(np.float32)
        cnt += X.sum(0).T
        pair += np.einsum("bcg,bch->cgh", X, X, optimize=True)
        inex += (res > 1e-9).sum(0)
        rmed.append(np.median(res, 0))
        done += b; i += 1
    for j in range(ncol):
        np.fill_diagonal(pair[j], 0.0)
    return dict(cnt=cnt, pair=pair, R=R, inexact=inex / R, resid_median=np.median(np.array(rmed), 0))


def eval_draws(pi, f, D, seed_prefix):
    """D independent cube draws per column -> Lall (D, G, ncol) bool, resid (D, ncol)."""
    G, ncol = pi.shape
    B = batch_for(G, ncol)
    Ls, rs = [], []
    done, i = 0, 0
    while done < D:
        b = min(B, D - done)
        xi, res = cube(pi, f, b, np.random.default_rng(W.seed_of(f"{seed_prefix}|b{i}")))
        Ls.append(np.transpose(xi, (0, 2, 1))); rs.append(res)
        done += b; i += 1
    return np.concatenate(Ls), np.concatenate(rs)


def R_for(G, n):
    p = n * (n - 1) / (G * (G - 1))
    return int(min(1_000_000, max(100_000, math.ceil(400 / p))))


# ---------------------------------------------------------------- estimators

def resid_var(zbar, fbar, Lall, pi_w, pi_x, theta_h):
    """Theory 3.4. Lall (D, G, ncol); pi_w (G, ncol) the probabilities used as weights; pi_x (G, ncol) the balance
    variable. Returns dict HT, H -> (var (D, ncol), p (D, ncol) rank)."""
    D, G, ncol = Lall.shape
    Lf = Lall.astype(float)
    ip = 1.0 / pi_w
    q = Lf * ((1 - pi_w) / pi_w * ip)[None]                 # v_g / pi_g on L
    x1 = np.broadcast_to(pi_x[None], Lall.shape); x2 = np.broadcast_to(fbar[None], Lall.shape)
    S11 = (q * x1 * x1).sum(1); S12 = (q * x1 * x2).sum(1); S22 = (q * x2 * x2).sum(1)
    det = S11 * S22 - S12 ** 2
    n = Lf.sum(1)
    Nh = (Lf * ip[None]).sum(1)
    out = {}
    rank2 = det > 1e-10 * np.maximum(S11 * S22, 1e-300)
    for nm, y, denom in (("HT", np.broadcast_to(zbar[None], Lall.shape), np.full((D, ncol), float(G))),
                         ("H", zbar[None] - theta_h[:, None, :], Nh)):
        b1 = (q * x1 * y).sum(1); b2 = (q * x2 * y).sum(1)
        with np.errstate(divide="ignore", invalid="ignore"):
            c1 = np.where(rank2, (S22 * b1 - S12 * b2) / det, b1 / S11)
            c2 = np.where(rank2, (S11 * b2 - S12 * b1) / det, 0.0)
        e = y - c1[:, None, :] * x1 - c2[:, None, :] * x2
        p = np.where(rank2, 2.0, 1.0)
        with np.errstate(divide="ignore", invalid="ignore"):
            v = (n / (n - p)) * (q * e ** 2).sum(1) / denom ** 2
        out[nm] = (np.where(n - p > 0, v, np.nan), p)
    return out


def bh_variants(zbar, fbar, Lall, G, nL):
    """Broska and Howes's interval and the S2b variants, as if simple random (theory 2.1). (th, var, df, normal)."""
    import round7_ppi_s2_comparators as S2
    th, TL, TU, n = S2.bh3_parts(zbar[None], fbar[None], Lall)
    with np.errstate(divide="ignore", invalid="ignore"):
        vt = TL * n / (n - 1) + TU
    return {("BH", "bh", "normal"): (th, TL + TU, np.inf, True),
            ("BH", "bh_t", "n1"): (th, vt, n - 1, False),
            ("BH", "bh_t_n2", "n2"): (th, vt, n - 2, False),
            ("BH", "bh_t_fpc", "n1"): (th, vt * (1 - nL / G), n - 1, False)}


def summ(th, v, df, theta, normal=False):
    s = W.summarise(th, v, df, theta, normal=normal)
    s["coverage_all"] = np.where(s["share_formed"] > 0, np.nan_to_num(s["coverage"]) * s["share_formed"], 0.0)
    return s


def all_intervals(zbar, fbar, Lall, pi_hat, pi_x, pgh, fixed, G, nL, bad=None):
    """Every S3 interval for one design. Returns dict key -> summarise input (th, v, df, normal)."""
    Ps, nfs = W.fix_nonpositive(W.pgh_apx_size(pi_hat))
    w = W.weighted(zbar, fbar, Lall, pi_hat, {"sim": pgh, "apx_size": Ps}, fixed)
    rv = resid_var(zbar, fbar, Lall, pi_hat, pi_x, w["H"]["theta"])
    nn = Lall.sum(1).astype(float)
    out = {}
    for e_ in ("HT", "H"):
        th = w[e_]["theta"].copy()
        if bad is not None:
            th[bad] = np.nan
        v, p = rv[e_]
        out[(e_, "res", "res")] = (th, v, nn - p, False)
        for vn in ("sim", "apx_size"):
            out[(e_, vn, "res")] = (th, w[e_]["var"][vn], nn - 2, False)
    for k_, val in bh_variants(zbar, fbar, Lall, G, nL).items():
        th = val[0].copy()
        if bad is not None:
            th[bad] = np.nan
        out[k_] = (th,) + val[1:]
    return out, nfs


def nn_score(emb):
    import round7_ppi_d2 as D2
    k = min(10, emb.shape[1], emb.shape[0] - 1)
    Z = D2.pcs(emb, k)
    d = np.sqrt(((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(d, np.inf)
    return d.min(1)


def pi_diag(pi_hat, pi_t, pgh, R, nL, G):
    se = np.sqrt(pi_t * (1 - pi_t) / R)
    with np.errstate(divide="ignore", invalid="ignore"):
        zmax = np.nanmax(np.where(se > 0, np.abs(pi_hat - pi_t) / se, 0.0))
    off = ~np.eye(G, dtype=bool)
    ratio = pi_hat / (nL / G)
    return dict(pi_hat_vs_target_zmax=float(zmax), pi_hat_ratio_min_min=float(ratio.min()),
                pi_hat_ratio_min_median=float(np.median(ratio.min(0))), pi_target_ratio_min=float((pi_t / (nL / G)).min()),
                pi_target_ratio_max=float((pi_t / (nL / G)).max()), n_capped=int((pi_t >= 1).sum()),
                share_pairs_pgh_zero=float((pgh[:, off] <= 0).mean()), min_pair_count=float((pgh[:, off] * R).min()))


# ---------------------------------------------------------------- test mode

def run_test(out_dir, r_pi=1_000_000, n_eval=20_000):
    from round7_ppi_s1_tests import pop
    rows = []
    for (G, n, k) in ((51, 8, 1), (24, 8, 1), (15, 6, 2)):
        for law in ("normal", "skewed"):
            t0 = time.time()
            rng = np.random.default_rng(W.seed_of(f"r7ppi|S1test|pop|G{G}|n{n}|k{k}|{law}"))
            z, Xp = pop(G, k, law, rng)
            zbar = z[:, None]; fbar = Xp[:, :1]
            u = np.abs(fbar - fbar.mean(0))
            pit = target_pi(u, n)
            tag = f"G{G}_n{n}_{law}"
            st = pi_sim(pit, fbar, r_pi, f"r7ppi|S3test|pi|{tag}")
            pih = st["cnt"] / st["R"]; pgh = st["pair"] / st["R"]
            se = np.sqrt(pih * (1 - pih) / st["R"])
            zpi = np.abs(pih - pit) / np.maximum(np.sqrt(pit * (1 - pit) / st["R"]), 1e-12)
            L, res = eval_draws(pit, fbar, n_eval, f"r7ppi|S3test|eval|{tag}")
            theta = zbar.mean(0)
            iv, nfs = all_intervals(zbar, fbar, L, pih, pit, pgh, True, G, n)
            # HT with the target probabilities (unbiasedness of the sampler, not of pi_hat)
            ht_t = (L[:, :, 0] * (zbar[:, 0] / pit[:, 0])[None]).sum(1) / G
            bz_t = (ht_t.mean() - theta[0]) / (ht_t.std(ddof=1) / math.sqrt(n_eval))
            base = dict(G=G, n_L=n, law=law, R=st["R"], n_eval=n_eval, pi_z_max=float(zpi.max()),
                        pi_z_gt3=int((zpi > 3).sum()), pi_target_min_ratio=float((pit / (n / G)).min()),
                        pi_target_max_ratio=float((pit / (n / G)).max()), n_capped=int((pit >= 1).sum()),
                        share_pairs_pgh_zero=float((pgh[0][~np.eye(G, dtype=bool)] <= 0).mean()),
                        inexact_share_eval=float((res > 1e-9).mean()), inexact_share_pi=float(st["inexact"][0]),
                        resid_median_eval=float(np.median(res)), resid_max_eval=float(res.max()),
                        ht_target_pi_bias_z=float(bz_t))
            ex = (res[:, 0] <= 1e-9)
            for key, (th, v, df, normal) in iv.items():
                s = summ(th, v, df, theta, normal)
                s_ex = summ(th[ex], v[ex], (df[ex] if np.ndim(df) else df), theta, normal) if ex.sum() > 10 else None
                rows.append(dict(base, estimator=key[0], variance=key[1], ref=key[2], coverage=float(s["coverage"][0]),
                                 coverage_all=float(s["coverage_all"][0]), share_formed=float(s["share_formed"][0]),
                                 width=float(s["width"][0]), est_var=float(s["est_var"][0]), emp_var=float(s["emp_var"][0]),
                                 est_over_emp=float(s["est_var"][0] / s["emp_var"][0]), bias_z=float(s["bias_z"][0]),
                                 coverage_exact_draws=float(s_ex["coverage"][0]) if s_ex else np.nan,
                                 est_over_emp_exact_draws=float(s_ex["est_var"][0] / s_ex["emp_var"][0]) if s_ex else np.nan))
            print(f"test {tag} {time.time() - t0:.0f}s", flush=True)
    os.makedirs(out_dir, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "s3_tests.csv"), index=False, float_format="%.10g")


# ---------------------------------------------------------------- masking mode

def add_rows(rows, generows, base, key, s, genes):
    est, var, ref = key
    med = lambda a: float(np.nanmedian(a)) if np.isfinite(a).any() else np.nan
    rows.append(dict(base, estimator=est, variance=var, ref=ref, n_genes=int(np.isfinite(s["coverage"]).sum()),
                     coverage_median=med(s["coverage"]), coverage_all_median=med(s["coverage_all"]),
                     width_median=med(s["width"]), est_over_emp_median=med(s["est_var"] / s["emp_var"]),
                     share_bias_z_gt3=float(np.nanmean(np.abs(s["bias_z"]) > 3)),
                     share_formed_median=med(s["share_formed"]), share_formed_min=float(np.nanmin(s["share_formed"])),
                     share_neg_max=float(np.nanmax(s["share_neg"]))))
    for j, g in enumerate(genes):
        generows.append(dict(base, estimator=est, variance=var, ref=ref, gene=g, **{k: float(v[j]) for k, v in s.items()}))


def run_masking(a):
    import round7_ppi_d2 as D2
    import round7_ppi_s1_masking as M
    from round5_ppi_e2_regimeB import ACS
    t0 = time.time()
    tag = f"{a.vtag}__{a.arm}__nL{a.nl}"
    census = a.vtag in ACS
    diag, rows, generows, skipped = [], [], [], []
    designs = a.designs.split(",")
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
        zbar, fbar, theta = cell["zbar"], cell["fbar"], cell["theta"]
        # cube over the G valid clusters
        scores = {}
        if "cube_u1" in designs:
            scores["u1"] = np.abs(fbar - fbar.mean(0, keepdims=True))
        if "cube_u2" in designs:
            if cell["emb"] is None or a.arm == "constant":
                skipped.append(dict(estimand=est, design="cube_u2", reason="no embedding for this arm or task"))
            elif not np.isfinite(cell["emb"][cell["vid"]]).all():
                skipped.append(dict(estimand=est, design="cube_u2", reason="embedding not finite for every valid cluster"))
            else:
                scores["u2"] = np.broadcast_to(nn_score(cell["emb"][cell["vid"]])[:, None], (G, ng)).copy()
        if scores and nL > G - 2:
            skipped.append(dict(estimand=est, design="cube", reason=f"n_L {nL} > G - 2 (G = {G} valid clusters)"))
            scores = {}
        for sn, u in scores.items():
            ckey = f"{a.vtag}|{a.arm}|{est}|nL{nL}|cube_{sn}"
            pit = target_pi(u, nL)
            R = min(R_for(G, nL), a.r_cap)
            st = pi_sim(pit, fbar, R, f"r7ppi|S3|pi|{ckey}")
            pih = st["cnt"] / R; pgh = st["pair"] / R
            L, res = eval_draws(pit, fbar, a.draws, f"r7ppi|S3|eval|{ckey}")
            iv, nfs = all_intervals(zbar, fbar, L, pih, pit, pgh, True, G, nL)
            base = dict(vtag=a.vtag, arm=a.arm, estimand=est, G=G, Gall=Gall, n_L=nL, design=f"cube_{sn}",
                        balance="pi,own", p_a=np.nan)
            for key, (th, v, df, normal) in iv.items():
                add_rows(rows, generows, base, key, summ(th, v, df, theta, normal), genes)
            diag.append(dict(base, R=R, apx_size_nonpositive_fixed=nfs, **pi_diag(pih, pit, pgh, R, nL, G),
                             inexact_share_eval=float((res > 1e-9).mean()), inexact_share_pi=float(st["inexact"].mean()),
                             resid_median_eval=float(np.median(res)), wall_s=time.time() - t0))
            print(f"{est} cube_{sn} {time.time() - t0:.0f}s R {R}", flush=True)
        # mixture of D2 (own) and D0
        mix_pas = [float(x) for x in a.mix_pa.split(",") if x] if any(d.startswith("mix") for d in designs) else []
        if mix_pas and nL > Gall - 2:
            skipped.append(dict(estimand=est, design="mix", reason=f"n_L {nL} > Gall - 2"))
            mix_pas = []
        if mix_pas:
            fixed = Gall == G
            first = D2.r5_first(cell, nL, n_cand=D2.POOL_CAND)
            L0 = np.zeros((a.draws, G, ng), bool)
            for d in range(a.draws):
                L0[d] = np.isin(cell["vid"], first[d, 0])[:, None]
            X = cell["bal"]["own"]
            thr, _ = D2.fixed_thresholds(cell, X, first)
            for pa_ in mix_pas:
                t = thr[pa_]
                ckey1 = f"{a.vtag}|{a.arm}|{est}|nL{nL}|own|pa{pa_}"          # S1's key: same pi_hat as S1
                R = min(M.R_for(Gall, nL), a.r_cap)
                st = W.pi_stream(X, cell["vid"], Gall, t, nL, R, f"r7ppi|S1|pi|{ckey1}")
                pi2, se2, pgh2 = W.from_counts(st)
                sel = D2.d2_stream(cell, X, t, nL, a.draws, f"r7ppi|S3|mixeval|{ckey1}")["acc"]
                L2 = M.L_from_sel(cell, sel, ng)
                coin = np.random.default_rng(W.seed_of(f"r7ppi|S3|mixcoin|{ckey1}")).random(a.draws) < 0.5
                Lm = np.where(coin[:, None, None], L2, L0)
                p0 = nL / Gall; p00 = nL * (nL - 1) / (Gall * (Gall - 1))
                pim = 0.5 * pi2 + 0.5 * p0
                pghm = 0.5 * pgh2 + 0.5 * p00
                for j in range(pghm.shape[0]):
                    np.fill_diagonal(pghm[j], 0.0)
                bc = lambda A_: A_ if A_.shape[-1] == ng else np.broadcast_to(A_, A_.shape[:-1] + (ng,)).copy()
                bcP = lambda P_: P_ if P_.shape[0] == ng else np.broadcast_to(P_, (ng,) + P_.shape[1:]).copy()
                pim = bc(pim); pghm = bcP(pghm)
                bad = Lm.sum(1) < 2
                iv, nfs = all_intervals(zbar, fbar, Lm, pim, pim, pghm, fixed, G, nL, bad=bad)
                base = dict(vtag=a.vtag, arm=a.arm, estimand=est, G=G, Gall=Gall, n_L=nL, design="mix_D2D0",
                            balance="own", p_a=pa_)
                for key, (th, v, df, normal) in iv.items():
                    add_rows(rows, generows, base, key, summ(th, v, df, theta, normal), genes)
                off = ~np.eye(G, dtype=bool)
                diag.append(dict(base, R=R, n_candidates=st["n_cand"], apx_size_nonpositive_fixed=nfs,
                                 share_D2_draws=float(coin.mean()), pi_hat_ratio_min_min=float((pim / (nL / Gall)).min()),
                                 pi_hat_ratio_min_median=float(np.median((pim / (nL / Gall)).min(0))),
                                 d2_share_pairs_pgh_zero=float((pgh2[:, off] <= 0).mean()),
                                 mix_share_pairs_pgh_zero=float((pghm[:, off] <= 0).mean()),
                                 d2_pi_hat_sum_check=float(np.abs(pi2.sum(0) - (nL if fixed else pi2.sum(0))).max()),
                                 draws_with_lt2_valid=int(bad.any(1).sum()), wall_s=time.time() - t0))
                print(f"{est} mix pa{pa_} {time.time() - t0:.0f}s R {R}", flush=True)
    os.makedirs(a.out_dir, exist_ok=True)
    pd.DataFrame(diag).to_csv(os.path.join(a.out_dir, f"s3m_diag__{tag}.csv"), index=False, float_format="%.10g")
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"s3m_cells__{tag}.csv"), index=False, float_format="%.10g")
    pd.DataFrame(skipped).to_csv(os.path.join(a.out_dir, f"s3m_skipped__{tag}.csv"), index=False)
    pd.DataFrame(generows).to_csv(os.path.join(a.out_dir, f"s3m_genes__{tag}.csv.gz"), index=False, float_format="%.10g")
    json.dump(dict(tag=tag, wall_s=time.time() - t0, n_cells=len(diag), n_rows=len(rows), args=vars(a)),
              open(os.path.join(a.out_dir, f"s3m_summary__{tag}.json"), "w"), indent=1)


# ---------------------------------------------------------------- sim mode

def run_sim(a):
    import round5_ppi_e4b_sim as R4b
    from round5_ppi_e1_sim import populations, R2_GRID, LAMSTAR
    from round5_ppi_e4_sim import pool, LAWS
    from round7_ppi_s1_sim import cell_row
    t0 = time.time()
    law = dict(normal="normal", skewed=LAWS[1]).get(a.law, a.law)
    lawtag = "n" if law == "normal" else "s"
    G, nL = a.G, a.nl
    tag = f"G{G}_{lawtag}_k1_nL{nL}"
    masks = pool(G, nL, a.draws, a.n_cand)
    flat = masks.reshape(-1, G)
    vid = np.arange(G)
    R = min(R_for(G, nL), a.r_cap)
    rows = []
    for R2, ls in itertools.product(map(float, a.r2.split(",")), map(float, a.lamstar.split(","))):
        z, f = populations(G, R2, ls, 0.0, law)
        npop = z.shape[1]
        theta = z.mean(0)
        base0 = dict(G=G, n_L=nL, R2=R2, lambda_star=ls, kappa=0.0, law=lawtag, k=1)
        ckey = f"G{G}|{lawtag}|nL{nL}|R2{R2}|lam{ls}"

        def emit(base, iv):
            for key, (th, v, df, normal) in iv.items():
                s = summ(th, v, df, theta, normal)
                r = cell_row(base, key, s, a.draws)
                r["coverage_all_mean"] = float(np.nanmean(s["coverage_all"]))
                rows.append(r)
        # cube with u1
        pit = target_pi(np.abs(f - f.mean(0)), nL)
        st = pi_sim(pit, f, R, f"r7ppi|S3sim|pi|{ckey}|cube_u1")
        pih = st["cnt"] / R; pgh = st["pair"] / R
        L, res = eval_draws(pit, f, a.draws, f"r7ppi|S3sim|eval|{ckey}|cube_u1")
        iv, nfs = all_intervals(z, f, L, pih, pit, pgh, True, G, nL)
        emit(dict(base0, design="cube_u1", p_a=np.nan, R=R, apx_nonpositive_fixed=nfs,
                  inexact_share_eval=float((res > 1e-9).mean()), **pi_diag(pih, pit, pgh, R, nL, G)), iv)
        # mixture: D2 (k = 1, E4b's draws and S1's pi_hat) with D0 (pool candidate 0)
        L0 = np.ascontiguousarray(np.broadcast_to(masks[:, 0][:, :, None], (a.draws, G, npop)))
        X = f[:, :, None]
        fc = f - f.mean(0)
        d1 = ((flat.astype(float) @ fc) / nL) ** 2 / f.var(0, ddof=1)[None, :]
        for pa_ in (0.1, 0.01):
            thr1 = np.quantile(d1, pa_, axis=0)
            Lsel, _ = R4b.d2_select_redraw(d1, masks, f, fc, thr1, G, nL, a.draws, a.n_cand)
            ck1 = f"G{G}|{lawtag}|k1|nL{nL}|R2{R2}|lam{ls}|pa{pa_}"         # S1's key
            st2 = W.pi_stream(X, vid, G, thr1, nL, R, f"r7ppi|S1sim|pi|{ck1}")
            pi2, _, pgh2 = W.from_counts(st2)
            coin = np.random.default_rng(W.seed_of(f"r7ppi|S3sim|mixcoin|{ck1}")).random(a.draws) < 0.5
            Lm = np.where(coin[:, None, None], Lsel, L0)
            pim = 0.5 * pi2 + 0.5 * nL / G
            pghm = 0.5 * pgh2 + 0.5 * nL * (nL - 1) / (G * (G - 1))
            for j in range(npop):
                np.fill_diagonal(pghm[j], 0.0)
            iv, nfs = all_intervals(z, f, Lm, pim, pim, pghm, True, G, nL)
            off = ~np.eye(G, dtype=bool)
            emit(dict(base0, design="mix_D2D0", p_a=pa_, R=R, apx_nonpositive_fixed=nfs,
                      share_D2_draws=float(coin.mean()), pi_hat_ratio_min_min=float((pim / (nL / G)).min()),
                      d2_share_pairs_pgh_zero=float((pgh2[:, off] <= 0).mean())), iv)
        print(f"{tag} R2{R2} lam{ls} {time.time() - t0:.0f}s", flush=True)
    os.makedirs(a.out_dir, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"s3_sim__{tag}.csv"), index=False, float_format="%.10g")
    json.dump(dict(tag=tag, R=R, draws=a.draws, n_rows=len(rows), wall_s=time.time() - t0),
              open(os.path.join(a.out_dir, f"s3_sim_summary__{tag}.json"), "w"), indent=1)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["test", "masking", "sim"])
    p.add_argument("--out-dir", default=".")
    p.add_argument("--draws", type=int, default=NDRAW)
    p.add_argument("--r-cap", type=int, default=1_000_000)
    p.add_argument("--test-r", type=int, default=1_000_000)
    p.add_argument("--test-eval", type=int, default=20_000)
    # masking
    p.add_argument("--parquet"); p.add_argument("--perm-parquet"); p.add_argument("--ref-parquet")
    p.add_argument("--ref-arm"); p.add_argument("--vtag"); p.add_argument("--arm"); p.add_argument("--nl", type=int)
    p.add_argument("--estimands", default="theta3,theta2")
    p.add_argument("--theta2-kind", default="neo_minus_stroma")
    p.add_argument("--designs", default="cube_u1,cube_u2,mix")
    p.add_argument("--mix-pa", default="0.1,0.01")
    p.add_argument("--max-genes", type=int, default=0)
    p.add_argument("--root", default="/work/users/w/e/weiyang/hest_replication")
    # sim
    p.add_argument("--G", type=int); p.add_argument("--law")
    p.add_argument("--n-cand", type=int, default=1000)
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
