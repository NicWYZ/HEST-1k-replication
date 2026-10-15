"""Round 7 inference track, S2: the comparators from the literature (track document S2.2; theory sections 2.1-2.3).

Two modes.
  --mode masking: one task, arm and n_L (estimands theta3, theta2; the ACS mean skipped for the constant arm). Set A
    is the fixed task (design target): D0 with round 4's draw_L seeds over all donors, as round 5. Set B is the
    resampled world of theory section 2.3 (G valid clusters drawn with replacement; superpopulation target = the
    task's theta, design target = the world's mean).
  --mode sim: one G, law and n_L of round 5's E4b simulation (60 populations as columns, R2 grid, lambda* grid);
    design target = the population's mean, superpopulation target = 0. D0 uses E4b's pool candidate 0 per draw.
In each set: D0 with the classical and tuned estimators (textbook_t|fpc|lin, textbook_t|fpc|lin|xf, and round 5's
superpopulation interval s_e^2 / n_L with t_{n_L-1}) and Broska and Howes's interval; Kluger et al.'s uniform
(pi = n_L/G) and score (half |f - F| proportional, half uniform, capped) Bernoulli designs, each with their
predict-then-debias estimator and 2,000-draw cluster bootstrap, and the HT and Hajek means with the Poisson-design
variance. Every interval is scored against both targets where both exist.
Outputs: s2m_cells__<tag>.csv (median over genes) and s2m_genes__<tag>.csv.gz (masking), s2_sim__<tag>.csv (sim).
With --bh-only (S2b item 3), only Broska and Howes's interval and its variants bh_t, bh_t_n2 and bh_t_fpc, written to
s2bm_cells__/s2bm_genes__ (masking) and s2b_sim__ (sim).
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

import round5_ppi_balance as BAL
import round5_ppi_estimator as R5
import round7_ppi_d2 as D2
import round7_ppi_weighting as W
from round5_ppi_e2_regimeB import ACS

ALPHA = R5.ALPHA
LIN, XF = "textbook_t|fpc|lin", "textbook_t|fpc|lin|xf"
B_BOOT = 2000


def pi_score(u, nL):
    """theory 2.2: half proportional to u, half uniform, capped at 1 with the excess redistributed. u (G, ncol)."""
    G = u.shape[0]
    s = u.sum(0)
    base = np.where(s[None, :] > 0, 0.5 * nL * u / np.where(s > 0, s, 1.0)[None, :], 0.5 * nL / G) + 0.5 * nL / G
    p = base.copy()
    for _ in range(100):
        over = p > 1
        if not over.any():
            break
        excess = np.where(over, p - 1, 0).sum(0)
        p = np.where(over, 1.0, p)
        free = p < 1
        tot = np.where(free, p, 0).sum(0)
        p = np.where(free, p + excess[None, :] * p / np.where(tot > 0, tot, 1.0)[None, :], p)
    return np.minimum(p, 1.0)


def bh3(Z, F, L, tiny=1e-24):
    """W.bh with per-draw populations: Z, F, L (D, G, ncol)."""
    Lf = L.astype(float)
    n = Lf.sum(1); G = L.shape[1]; N = G - n; r = n / N
    Fbar = F.mean(1)
    zL = (Lf * Z).sum(1) / n; fL = (Lf * F).sum(1) / n; fU = ((1 - Lf) * F).sum(1) / N
    Zh = (Lf - r[:, None, :] * (1 - Lf)) * (F - Fbar[:, None, :])

    def sig(th):
        eps = Lf * (Z - th[:, None, :])
        return (eps ** 2).sum(1) / G, (eps * Zh).sum(1) / G, (Zh ** 2).sum(1) / G
    s11, s12, s22 = sig(zL + (fU - fL))
    lz = s22 <= tiny * np.maximum(1.0, Fbar ** 2)
    lam = np.where(lz, 0.0, s12 / np.where(lz, 1.0, s22))
    th = zL + lam * (fU - fL)
    s11, s12, s22 = sig(th)
    se = np.sqrt(np.maximum((G / n) * (s11 - 2 * lam * s12 + lam ** 2 * s22), 0) / n)
    return th, se


def kluger_draw(Z, F, pi, xi, rng, B=B_BOOT):
    """One draw: Z, F, pi (G, ncol), xi (G, ncol) bool. Returns dict of (ncol,) arrays: ptd, lo, hi, boot_drop,
    ht, ht_v, hj, hj_v, nL."""
    G, ncol = Z.shape
    x = xi.astype(float)
    Wd = x / pi
    with np.errstate(divide="ignore", invalid="ignore"):
        Wo = np.where(pi < 1, (1 - x) / np.where(pi < 1, 1 - pi, 1.0), 0.0)
    nL = x.sum(0)
    sw, so = Wd.sum(0), Wo.sum(0)
    th_d = (Wd * Z).sum(0) / sw
    ga_d = (Wd * F).sum(0) / sw
    ga_o = np.where(so > 0, (Wo * F).sum(0) / np.where(so > 0, so, 1.0), np.nan)
    C = rng.multinomial(G, np.full(G, 1.0 / G), size=B).astype(float)
    cw, co = C @ Wd, C @ Wo
    with np.errstate(divide="ignore", invalid="ignore"):
        tb = (C @ (Wd * Z)) / cw
        gb = (C @ (Wd * F)) / cw
        ob = (C @ (Wo * F)) / co
    ok = (cw > 0) & (co > 0)
    tbm = np.where(ok, tb, np.nan); gbm = np.where(ok, gb, np.nan); obm = np.where(ok, ob, np.nan)
    cov = np.nanmean((tbm - np.nanmean(tbm, 0)) * (gbm - np.nanmean(gbm, 0)), 0)
    den = np.nanvar(gbm, 0) + np.nanvar(obm, 0)
    # a constant predictor leaves only rounding noise in the bootstrap variances; treat a variance below 1e-20 of
    # the predictions' mean square as zero and set Omega = 0 (S2 implementation check, first run Slurm 4824921)
    tiny = 1e-20 * np.maximum(1.0, (F ** 2).mean(0))
    om = np.where(den > tiny, cov / np.where(den > tiny, den, 1.0), 0.0)
    ptd = om * ga_o + th_d - om * ga_d
    pb = om * obm + tbm - om * gbm
    lo = np.nanquantile(pb, ALPHA / 2, axis=0); hi = np.nanquantile(pb, 1 - ALPHA / 2, axis=0)
    ht = (x * Z / pi).sum(0) / G
    ht_v = (x * (1 - pi) * Z ** 2 / pi ** 2).sum(0) / G ** 2
    hj_v = (x * (1 - pi) * (Z - th_d) ** 2 / pi ** 2).sum(0) / sw ** 2
    bad = nL < 2
    out = dict(ptd=ptd, lo=lo, hi=hi, boot_drop=1 - ok.mean(0), ht=ht, ht_v=ht_v, hj=th_d, hj_v=hj_v, nL=nL, omega=om)
    for kk in out:
        if kk != "nL":
            out[kk] = np.where(bad, np.nan, out[kk])
    return out


def bh3_parts(Z, F, L, tiny=1e-24):
    """bh3 split into the labelled and unlabelled clusters' terms of sigma^2 / n (theory section 2.1, expanded form):
    T_L = sum_L (z - theta - lam (f - F))^2 / n^2 and T_U = lam^2 r^2 sum_U (f - F)^2 / n^2, so bh3's se^2 = T_L + T_U.
    Returns theta, T_L, T_U, n (D, ncol)."""
    Lf = L.astype(float)
    n = Lf.sum(1); G = L.shape[1]; N = G - n; r = n / N
    Fbar = F.mean(1)
    zL = (Lf * Z).sum(1) / n; fL = (Lf * F).sum(1) / n; fU = ((1 - Lf) * F).sum(1) / N
    fc = F - Fbar[:, None, :]
    Zh = (Lf - r[:, None, :] * (1 - Lf)) * fc

    def sig(th):
        eps = Lf * (Z - th[:, None, :])
        return (eps ** 2).sum(1) / G, (eps * Zh).sum(1) / G, (Zh ** 2).sum(1) / G
    s11, s12, s22 = sig(zL + (fU - fL))
    lz = s22 <= tiny * np.maximum(1.0, Fbar ** 2)
    lam = np.where(lz, 0.0, s12 / np.where(lz, 1.0, s22))
    th = zL + lam * (fU - fL)
    TL = (Lf * (Z - th[:, None, :] - lam[:, None, :] * fc) ** 2).sum(1) / n ** 2
    TU = lam ** 2 * r ** 2 * ((1 - Lf) * fc ** 2).sum(1) / n ** 2
    return th, TL, TU, n


def rho_bh(f, R2):
    """theory section 2.1: ratio of what Broska and Howes's variance estimates to the design variance under D0."""
    return (1 - (1 - f) * R2) / ((1 - f) * (1 - R2))


def bh_variants(Zs, Fs, L, truths, G, nL):
    """S2 memo, S2b item 3: the published interval and bh_t (labelled term x n/(n-1), t_{n-1}; beside it t_{n-2})
    and bh_t_fpc (bh_t x (1 - n_L/G)), with the median-free per-gene variance diagnostics."""
    th, TL, TU, n = bh3_parts(Zs, Fs, L)
    z = stats.norm.ppf(1 - ALPHA / 2)
    v_pub = TL + TU
    with np.errstate(divide="ignore", invalid="ignore"):
        v_t = TL * n / (n - 1) + TU
    v_fpc = v_t * (1 - nL / G)
    zc = Zs - Zs.mean(1, keepdims=True); fc = Fs - Fs.mean(1, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        R2d = (zc * fc).sum(1) ** 2 / ((zc ** 2).sum(1) * (fc ** 2).sum(1))
    R2 = np.nanmean(R2d, 0)
    out = {}
    se = np.sqrt(np.maximum(v_pub, 0))
    out[("D0", "BH", "bh")] = score(th - z * se, th + z * se, th, truths)
    for nm, v, df in (("bh_t", v_t, n - 1), ("bh_t_n2", v_t, n - 2), ("bh_t_fpc", v_fpc, n - 1)):
        lo, hi = t_lohi(th, np.where(df >= 1, v, np.nan), df)
        out[("D0", "BH", nm)] = score(lo, hi, th, truths)
    emp = np.nanvar(th, 0, ddof=1)
    for key, v in ((("D0", "BH", "bh"), v_pub), (("D0", "BH", "bh_t"), v_t), (("D0", "BH", "bh_t_n2"), v_t),
                   (("D0", "BH", "bh_t_fpc"), v_fpc)):
        out[key]["est_var"] = np.nanmean(v, 0)
        out[key]["est_over_emp"] = np.nanmean(v, 0) / emp
        out[key]["R2"] = R2
        out[key]["rho_bh"] = rho_bh(nL / G, R2)
    return out


def t_lohi(th, v, df):
    q = stats.t.ppf(1 - ALPHA / 2, np.where(df >= 1, df, np.nan))
    se = np.sqrt(np.maximum(v, 0))
    return th - q * se, th + q * se


def score(lo, hi, th, truths):
    """lo, hi, th (D, ncol); truths dict name -> (D, ncol) or (ncol,). Per-gene dict."""
    formed = np.isfinite(lo) & np.isfinite(hi)
    out = dict(share_formed=formed.mean(0), width=np.nanmean(np.where(formed, hi - lo, np.nan), 0),
               emp_var=np.nanvar(th, 0, ddof=1), n_draws=np.full(th.shape[1], th.shape[0]))
    for nm, t in truths.items():
        t = np.broadcast_to(t, th.shape)
        cov = np.where(formed, (lo <= t) & (t <= hi), np.nan)
        out[f"coverage_{nm}"] = np.nanmean(cov, 0)
        out[f"bias_{nm}"] = np.nanmean(th - t, 0)
    return out


def run_set(Zs, Fs, Lsrs, truths, seeds, nL, Gd, est_label, d0_seed_fn, bh_only=False):
    """Zs, Fs: (D, G, ncol) populations per draw; Lsrs (D, G, ncol) the D0 labelled masks. Returns {key: per-gene}.
    bh_only: only Broska and Howes's interval and its two small-sample variants (bh_variants), on the same draws."""
    D, G, ncol = Zs.shape
    if bh_only:
        keep = Lsrs.sum(1).min(1) >= 2
        tr = {k: (v[keep] if np.ndim(v) == 2 else v) for k, v in truths.items()}
        return bh_variants(Zs[keep], Fs[keep], Lsrs[keep], tr, G, nL)
    res = {}
    acc = {}
    for d in range(D):
        Z, F, Lm = Zs[d], Fs[d], Lsrs[d]
        if Lm.sum(0).min() < 2:
            continue
        nn = Lm.sum(0).astype(float)
        for rule, nm in (("none", "classical"), ("c_crossfit_design", "tuned")):
            out, _ = BAL.estimate_srs_like(Z, F, Lm, rule, d0_seed_fn(d, rule))
            th, v, df = out[LIN]
            acc.setdefault((nm, LIN), []).append((d, th, *t_lohi(th, v, df)))
            if rule != "none":
                thx, vx, dfx = out[XF]
                acc.setdefault((nm, XF), []).append((d, thx, *t_lohi(thx, vx, dfx)))
            vs = v / np.maximum(1 - nn / G, 1e-12)
            acc.setdefault((nm, "round5_superpop"), []).append((d, th, *t_lohi(th, vs, nn - 1)))
    for key, L in acc.items():
        idx = np.array([x[0] for x in L])
        th = np.array([x[1] for x in L]); lo = np.array([x[2] for x in L]); hi = np.array([x[3] for x in L])
        tr = {k: (v[idx] if np.ndim(v) == 2 else v) for k, v in truths.items()}
        res[("D0",) + key] = score(lo, hi, th, tr)
    th, se = bh3(Zs, Fs, Lsrs)
    z = stats.norm.ppf(1 - ALPHA / 2)
    res[("D0", "BH", "bh")] = score(th - z * se, th + z * se, th, truths)
    for dname in ("bern_uniform", "bern_score"):
        cols = {k: np.full((D, ncol), np.nan) for k in ("ptd", "lo", "hi", "ht", "ht_v", "hj", "hj_v", "nL", "boot_drop")}
        for d in range(D):
            Z, F = Zs[d], Fs[d]
            if dname == "bern_uniform":
                pi = np.full((G, ncol), nL / G)
            else:
                pi = pi_score(np.abs(F - F.mean(0, keepdims=True)), nL)
            U = np.random.default_rng(W.seed_of(f"{seeds}|{dname}|xi|d{d}")).random(G)
            xi = U[:, None] < pi
            o = kluger_draw(Z, F, pi, xi, np.random.default_rng(W.seed_of(f"{seeds}|{dname}|boot|d{d}")))
            for kk in cols:
                cols[kk][d] = o[kk]
        res[(dname, "kluger_ptd", "cluster_boot")] = score(cols["lo"], cols["hi"], cols["ptd"], truths)
        res[(dname, "kluger_ptd", "cluster_boot")]["boot_drop_mean"] = np.nanmean(cols["boot_drop"], 0)
        for e_, th_, v_ in (("HT", "ht", "ht_v"), ("H", "hj", "hj_v")):
            lo, hi = t_lohi(cols[th_], cols[v_], cols["nL"] - 1)
            res[(dname, e_, "poisson")] = score(lo, hi, cols[th_], truths)
        sh = np.mean(cols["nL"] < 2, 0)
        for k in res:
            if k[0] == dname:
                res[k]["share_nL_lt2"] = sh
                res[k]["nL_mean"] = np.nanmean(cols["nL"], 0)
    return res


def masking(a):
    t0 = time.time()
    tag = f"{a.vtag}__{a.arm}__nL{a.nl}"
    rows, generows = [], []
    census = a.vtag in ACS
    for est in a.estimands.split(","):
        if census and est == "theta2" and a.arm == "constant":
            continue
        cell = D2.load_cell(a.parquet, a.perm_parquet, a.ref_parquet, a.ref_arm, a.vtag, a.arm, est, a.root, a.theta2_kind)
        if a.max_genes:
            for kk in ("zbar", "fbar", "theta"):
                cell[kk] = cell[kk][..., :a.max_genes]
            cell["genes"] = cell["genes"][:a.max_genes]
        G, Gall, nL, genes = cell["G"], cell["Gall"], a.nl, cell["genes"]
        ng = len(genes)
        if nL > Gall - 2 or nL > G - 2:
            continue
        z, f, theta = cell["zbar"], cell["fbar"], cell["theta"]
        # set A: the fixed task, D0 over all donors with round 4's seeds
        LA = np.zeros((a.draws, G, ng), bool)
        for d in range(a.draws):
            LA[d] = np.isin(cell["vid"], D2.RJ.cand_idx(cell["donors"], a.vtag, nL, d, 0))[:, None]
        keep = LA.sum(1).min(1) >= 2
        LA = LA[keep]
        DA = len(LA)
        ZA = np.broadcast_to(z, (DA, G, ng)); FA = np.broadcast_to(f, (DA, G, ng))
        seedA = f"r7ppi|S2|A|{a.vtag}|{a.arm}|{est}|nL{nL}"
        kidx = np.flatnonzero(keep)
        resA = run_set(ZA, FA, LA, {"design": theta}, seedA, nL, G, est,
                       lambda d, rule: f"q2|{a.vtag}|nL{nL}|m0|d{int(kidx[d])}|{est}|donor|{rule}", bh_only=a.bh_only)
        # set B: resampled worlds
        seedB = f"r7ppi|S2|B|{a.vtag}|{a.arm}|{est}|nL{nL}"
        wid = np.stack([np.random.default_rng(W.seed_of(f"{seedB}|world|d{d}")).integers(0, G, G) for d in range(a.draws)])
        ZB, FB = z[wid], f[wid]
        LB = np.zeros((a.draws, G, ng), bool)
        for d in range(a.draws):
            LB[d, np.random.default_rng(W.seed_of(f"{seedB}|srs|d{d}")).permutation(G)[:nL]] = True
        resB = run_set(ZB, FB, LB, {"design": ZB.mean(1), "super": theta}, seedB, nL, G, est,
                       lambda d, rule: f"{seedB}|x|d{d}|{rule}", bh_only=a.bh_only)
        for setname, res in (("A_fixed", resA), ("B_world", resB)):
            for key, s in res.items():
                base = dict(vtag=a.vtag, arm=a.arm, estimand=est, G=G, Gall=Gall, n_L=nL, set=setname,
                            design=key[0], estimator=key[1], interval=key[2])
                rows.append(dict(base, n_genes=ng, **{f"{k}_median": float(np.nanmedian(v)) for k, v in s.items()}))
                for j, g in enumerate(genes):
                    generows.append(dict(base, gene=g, **{k: float(v[j]) for k, v in s.items()}))
        print(f"{est} {time.time() - t0:.0f}s", flush=True)
    px = "s2bm" if a.bh_only else "s2m"
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"{px}_cells__{tag}.csv"), index=False, float_format="%.10g")
    pd.DataFrame(generows).to_csv(os.path.join(a.out_dir, f"{px}_genes__{tag}.csv.gz"), index=False, float_format="%.10g")
    json.dump(dict(tag=tag, wall_s=time.time() - t0, args=vars(a)), open(os.path.join(a.out_dir, f"{px}_summary__{tag}.json"), "w"), indent=1)


def sim(a):
    from round5_ppi_e1_sim import populations, R2_GRID, LAMSTAR
    from round5_ppi_e4_sim import pool, LAWS
    t0 = time.time()
    law = dict(normal="normal", skewed=LAWS[1]).get(a.law, a.law)
    lt = "n" if law == "normal" else "s"
    G, nL = a.G, a.nl
    tag = f"G{G}_{lt}_nL{nL}"
    masks = pool(G, nL, a.draws, 1)          # candidate 0 of E4b's pool is the D0 sample of every draw
    rows = []
    for R2, ls in itertools.product(map(float, a.r2.split(",")), map(float, a.lamstar.split(","))):
        z, f = populations(G, R2, ls, 0.0, law)
        npop = z.shape[1]
        L = np.ascontiguousarray(np.broadcast_to(masks[:, 0][:, :, None], (a.draws, G, npop)))
        Zs = np.broadcast_to(z, (a.draws, G, npop)); Fs = np.broadcast_to(f, (a.draws, G, npop))
        res = run_set(Zs, Fs, L, {"design": z.mean(0), "super": np.zeros(npop)}, f"r7ppi|S2sim|{tag}|R2{R2}|lam{ls}",
                      nL, G, "sim", lambda d, rule: f"r5e4simx|G{G}|nL{nL}|d{d}|D0", bh_only=a.bh_only)
        for key, s in res.items():
            r = dict(G=G, n_L=nL, R2=R2, lambda_star=ls, law=lt, design=key[0], estimator=key[1], interval=key[2], n_pop=npop)
            for k, v in s.items():
                r[f"{k}_mean"] = float(np.nanmean(v))
                if k.startswith("coverage"):
                    r[f"{k}_p05"] = float(np.nanquantile(v, 0.05)) if np.isfinite(v).any() else np.nan
            rows.append(r)
        print(f"{tag} R2{R2} lam{ls} {time.time() - t0:.0f}s", flush=True)
        px = "s2b_sim" if a.bh_only else "s2_sim"
        pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"{px}__{tag}.csv"), index=False, float_format="%.10g")
    json.dump(dict(tag=tag, wall_s=time.time() - t0, args=vars(a)), open(os.path.join(a.out_dir, f"{px}_summary__{tag}.json"), "w"), indent=1)


def main():
    from round5_ppi_e1_sim import R2_GRID, LAMSTAR
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=("masking", "sim"), required=True)
    p.add_argument("--parquet"); p.add_argument("--perm-parquet"); p.add_argument("--ref-parquet"); p.add_argument("--ref-arm")
    p.add_argument("--vtag"); p.add_argument("--arm"); p.add_argument("--nl", type=int)
    p.add_argument("--estimands", default="theta3,theta2"); p.add_argument("--theta2-kind", default="neo_minus_stroma")
    p.add_argument("--G", type=int); p.add_argument("--law")
    p.add_argument("--r2", default=",".join(map(str, R2_GRID))); p.add_argument("--lamstar", default=",".join(map(str, LAMSTAR)))
    p.add_argument("--draws", type=int, default=2000); p.add_argument("--max-genes", type=int, default=0)
    p.add_argument("--root", default=D2.ROOT); p.add_argument("--out-dir", default=".")
    p.add_argument("--bh-only", action="store_true", help="S2b item 3: only Broska and Howes and its two variants")
    p.add_argument("--arms", default="", help="loop over these arms (masking); parquets from --pred-dir, the permuted and "
                   "constant arms and --perm/--ref from resnet50, as the S2 units ran")
    p.add_argument("--pred-dir", default="")
    p.add_argument("--nls", default="", help="loop over these n_L")
    a = p.parse_args()
    np.seterr(all="ignore")
    os.makedirs(a.out_dir, exist_ok=True)
    import copy
    arms = a.arms.split(",") if a.arms else [None]
    nls = [int(v) for v in a.nls.split(",")] if a.nls else [a.nl]
    for arm in arms:
        for nl in nls:
            b = copy.copy(a); b.nl = nl
            if arm is not None:
                b.arm = arm
            if arm is not None and a.pred_dir:
                pq_ = lambda m: os.path.join(a.pred_dir, f"b1_predictions__{a.vtag}__{m}.parquet")
                b.parquet = pq_("resnet50" if arm in ("permuted", "constant") else arm)
                b.perm_parquet = b.ref_parquet = pq_("resnet50"); b.ref_arm = "resnet50"
            masking(b) if a.mode == "masking" else sim(b)


if __name__ == "__main__":
    main()
