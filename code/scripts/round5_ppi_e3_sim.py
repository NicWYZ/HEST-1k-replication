"""Round 5 PPI, interval 2, stage E3, simulation unit: the two-level estimator in simulation.

Generator (round 4's, reused as E2's simulation reuses it). round4_ppi_q1_sim.gen_block / yhat_at,
G clusters of M = 1000 units, between-cluster share rho = 0.3, outcome y = y_round4 + mu * sd(y),
sd(y) = sqrt(1 + BETA^2), mu in {0, 3, 10}. Arms: r0.5, r0.8 (unit-level correlation r, level through
y), uninf (round-4 r = 0 predictor plus the same level), const (every unit of the replicate gets the
replicate's task-wide mean of the r0.5 predictor; skipped for the mean).
Estimands (donor-weighted, kind in round5_ppi_twolevel): 'theta3' with w = (x - xbar_g) / S_g where S_g
is the cluster's within variance of x (divisor M), so sum_i w_gi = 0 per cluster, and 'mean' with w = 1.

Draw. Population of replicate k at G: rng 'r5e3sim|pop|G<G>|rep<k>' (it does not depend on n_L, m, mu,
arm or estimand; y0, a0, eps0 are the same at every mu and arm, so those are paired). Selection of a
cell: rng 'r5e3sim|sel|G<G>|nL<n_L>|m<m>|mu<mu>|arm<arm>|rep<k>': SRS of n_L of the G clusters
(everything when n_L = G), then SRS of m of the M units in each labelled cluster (everything when m =
all). The selection and the cross-fit seed 'r5e3sim|xf|<same fields>' do not depend on the estimator or
the estimand, so the six estimators (and theta3 and mean) share each draw. crc32 of the string seeds
numpy default_rng. n_L = G is regime B (regime_b=True), n_L < G regime A.

Estimators: round5_ppi_twolevel.ESTIMATORS, called unmodified, on the same draw.
r4_ppi coefficient (lam_r4):
  regime A: round4_ppi_estimator.lambda_rule('c_crossfit_design','donor', D, Lm, Um, seed) with D from
    the clusters' Horvitz-Thompson means t, tf (twolevel.ht_means), n = 100, Sz = 100 t, Sf = 100 tf,
    Szz = Sz^2/n, Sff = Sf^2/n, Szf = Sz Sf/n (round5_ppi_e1_sim.stats_arrays), the cross-fit seed above.
  regime B (n_L = G): round4_ppi_q3_regimes._half_lambda, the pooled within-cluster slope of z on f over
    the labelled units of the OTHER half, clipped to [0, 1], with the two halves of
    round4_ppi_estimator._crossfit_halves(Lm, seed) (the halves of round 5's estimator, not regime_b's own
    permutation, which is acceptable per the brief).
Regime A is computed with the xf correction and without it. xf=False is estimate(..., xf=False). The xf
interval adds round5_ppi_estimator.crossfit_extra to that variance; this is exactly what
estimate(xf=True) does, but it lets this script recover cU. For P_ppi and C_ppi cU and the coefficients are
recovered by calling lambda_rule again on the same D and seed that estimate() built (deterministic);
for r4_ppi they are lam_r4; classical estimators have cU = 0 and extra = 0.

Targets.
  design: truth = T['theta_full'], the replicate's realised mean over the G clusters of zbar_g. Interval
    theta +- t_df se with estimate()'s variance (two-stage, theory 2.1) and df (n_L - 1 in regime A;
    regime B the within-cluster degrees of freedom of estimate()).
  super: truth the generator parameter (BETA = 0.3 for theta3; MU + mu sd(y) for the mean). Cluster-robust
    variance on the cluster contributions. n_L < G: e_g = zhat_g - lam_c,g f_g + (lam_c,g - cU) Fbar over the
    labelled clusters, CR1 variance n_L/(n_L-1) sum_g (e_g - ebar)^2 / n_L^2 = s_e^2 / n_L, t_{n_L-1},
    centred at the estimator's theta. n_L = G: CR1 over zhat_g, G/(G-1) sum (zhat_g - mean)^2 / G^2, t_{G-1}.
Intervals are 90% (round4_ppi_estimator.ALPHA = 0.10, t quantile at 1 - ALPHA/2).
Coverage counts |theta - truth| <= q se + 1e-9 max(1, |truth|); the tolerance only matters for m = all
with n_L = G, where the interval has zero width and theta equals the truth up to rounding.

Output, per (G, n_L, m, mu, arm, estimand, estimator, xf, target): n_reps, n_nonfinite, coverage, mc_se,
mean_width, emp_var (variance of the error theta - truth over replicates), mean_var (mean estimated
variance), var_ratio = mean_var/emp_var, bias, mean within and between coefficients, mean_width ratios
to the same form's classical estimator (width_ratio_own) and to r4_classical (width_ratio_r4cl), and
population quantities of the cell (means over replicates): between share of z (var of zbar_g over var of
zbar_g + mean within variance of z), within R^2 (pooled within-cluster, unclipped, as form C) and the
cluster-level R^2 (squared correlation of zbar_g, fbar_g). Streaming sums are kept, not per-replicate
arrays. Run through round5_ppi_run.py; arguments --G, --est, --mus, --reps, --nLs, --ms, --arms.
"""
import argparse
import json
import os
import time
import zlib

import numpy as np
import pandas as pd
from scipy import stats

import round4_ppi_estimator as E
import round4_ppi_q1_sim as Q1
import round4_ppi_q3_regimes as Q3
import round5_ppi_estimator as R5
import round5_ppi_twolevel as TL

M_U, RHO = 1000, 0.3
NLS_DEF, MS_DEF, MUS_DEF = (6, 8, 12, "G"), (3, 5, 20, 100, "all"), (0.0, 3.0, 10.0)
ARMS = (("r0.5", 0.5), ("r0.8", 0.8), ("uninf", 0.0), ("const", "const"))
NSTAT = 100.0
_Q = {}


def crc(s):
    return zlib.crc32(s.encode())


def tq(df):
    if df not in _Q:
        _Q[df] = stats.t.ppf(1 - E.ALPHA / 2, df) if df > 0 else np.nan
    return _Q[df]


def population(G, rep, mu, arm, r, est, base, yh05):
    mm, y0, a0, e0 = base
    lev = mu * np.sqrt(1.0 + Q1.BETA ** 2)
    y = y0 + lev
    if arm == "const":
        yh = np.broadcast_to(yh05.mean(), y.shape).copy()
    elif r == 0.0:
        yh = Q1.yhat_at(y0, a0, e0, 0.0, RHO) + lev
    else:
        yh = Q1.yhat_at(y, a0, e0, r, RHO)
    if est == "theta3":
        dm = mm - mm.mean(1, keepdims=True)
        w = dm / (dm * dm).mean(1, keepdims=True)
    else:
        w = np.ones_like(y)
    return y, yh, w, lev


def pop_quantities(T, G):
    z, f = T["z"][:, 0].reshape(G, -1), T["f"][:, 0].reshape(G, -1)
    zb, fb = z.mean(1), f.mean(1)
    wz = ((z - zb[:, None]) ** 2).mean(1).mean()
    bshare = zb.var(ddof=0) / (zb.var(ddof=0) + wz) if (zb.var() + wz) > 0 else np.nan
    zc, fc = z - zb[:, None], f - fb[:, None]
    szf, sff, szz = (zc * fc).mean(1).sum(), (fc * fc).mean(1).sum(), (zc * zc).mean(1).sum()
    r2w = szf ** 2 / (sff * szz) if sff > 0 and szz > 0 else 0.0
    sc = np.std(zb) * np.std(fb)
    r2c = (np.mean((zb - zb.mean()) * (fb - fb.mean())) / sc) ** 2 if sc > 0 else 0.0
    return bshare, r2w, r2c


def lam_regime_b(T, Lc, sel, seed):
    G = T["G"]
    Lm = Lc[:, None].copy()
    half = E._crossfit_halves(Lm, seed)[:, 0]
    s = np.zeros(len(T["didx"]), bool); s[sel] = True
    A, B = np.flatnonzero(half == 0), np.flatnonzero(half == 1)
    lA = Q3._half_lambda(T["z"], T["f"], T["didx"], s, A, None)[0]
    lB = Q3._half_lambda(T["z"], T["f"], T["didx"], s, B, None)[0]
    lam = np.zeros((G, 1)); lam[A] = lB; lam[B] = lA
    return lam


def one_draw(T, G, nL, Lc, sel, seed, estimators=TL.ESTIMATORS):
    """Returns {(estimator, xf): {'design': (theta, var, df), 'super': (theta, var, df), lam_w, lam_c}}."""
    regB = nL == G
    valid = T["valid"]
    fb = T["fbar"]
    Fbar = fb[valid].mean(0)
    Lm = np.broadcast_to((Lc & valid)[:, None], (G, 1)).copy()
    Um = np.broadcast_to((~Lc & valid)[:, None], (G, 1)).copy()
    Vm = np.broadcast_to(valid[:, None], (G, 1))
    if regB:
        lam_r4 = lam_regime_b(T, Lc & valid, sel, seed)
    else:
        t, tf = TL.ht_means(T, sel)
        D = dict(n=np.full((G, 1), NSTAT), Sz=t * NSTAT, Sf=tf * NSTAT)
        D["Szz"], D["Sff"], D["Szf"] = D["Sz"] ** 2 / NSTAT, D["Sf"] ** 2 / NSTAT, D["Sz"] * D["Sf"] / NSTAT
        lam_r4 = E.lambda_rule("c_crossfit_design", "donor", D, Lm, Um, seed=seed)
    res = {}
    for est in estimators:
        o = TL.estimate(T, Lc, sel, est, seed, regime_b=regB, xf=False, lam_r4=lam_r4 if est == "r4_ppi" else None)
        zhat, lamc = o["zhat"], o["lam_c"]
        nLv = int((Lc & valid).sum())
        if regB:
            th = o["theta"]
            q = zhat[Lc & valid, 0]
            vs = G / (G - 1.0) * ((q - q.mean()) ** 2).sum() / G ** 2
            sup = (th, np.array([vs]), float(G - 1))
            res[(est, False)] = dict(design=(th, o["var"], o["df"]), super=sup, lam_w=o["lam_w"][Lc & valid].mean(), lam_c=0.0)
            continue
        form, kc = est.split("_")
        if est == "r4_ppi":
            lam = lam_r4
        elif kc == "ppi":
            D2 = dict(n=np.full((G, 1), NSTAT), Sz=zhat * NSTAT, Sf=fb * NSTAT)
            D2["Szz"], D2["Sff"], D2["Szf"] = D2["Sz"] ** 2 / NSTAT, D2["Sf"] ** 2 / NSTAT, D2["Sz"] * D2["Sf"] / NSTAT
            lam = E.lambda_rule("c_crossfit_design", "donor", D2, Lm, Um, seed=seed)
        else:
            lam = dict(lamL=np.zeros((G, 1)), cU=np.zeros(1))
        cU = lam["cU"]
        R = np.where(Lm, zhat - lamc * fb, 0.0)
        e = np.where(Lm, R + (lamc - cU[None, :]) * Fbar[None, :], 0.0)
        em = e.sum(0) / nLv
        s2e = (np.where(Lm, (e - em) ** 2, 0.0)).sum(0) / (nLv - 1.0)
        sup = (o["theta"], s2e / nLv, float(nLv - 1))
        extra = R5.crossfit_extra("donor", fb, Lm, lam, Vm)
        lw = o["lam_w"][Lc & valid].mean()
        lc = lamc[Lc & valid].mean()
        res[(est, False)] = dict(design=(o["theta"], o["var"], o["df"]), super=sup, lam_w=lw, lam_c=lc)
        res[(est, True)] = dict(design=(o["theta"], o["var"] + extra, o["df"]), super=sup, lam_w=lw, lam_c=lc)
    return res


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--G", type=int, required=True)
    p.add_argument("--est", default="theta3,mean")
    p.add_argument("--mus", default=",".join(map(str, MUS_DEF)))
    p.add_argument("--nLs", default="6,8,12,G")
    p.add_argument("--ms", default="3,5,20,100,all")
    p.add_argument("--arms", default="r0.5,r0.8,uninf,const")
    p.add_argument("--reps", type=int, default=2000)
    p.add_argument("--tag", default="")
    p.add_argument("--out-dir", default=".")
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    G = a.G
    ests = a.est.split(",")
    mus = [float(x) for x in a.mus.split(",")]
    nLs = [G if x == "G" else int(x) for x in a.nLs.split(",")]
    ms = [M_U if x == "all" else int(x) for x in a.ms.split(",")]
    arms = [x for x in ARMS if x[0] in a.arms.split(",")]
    didx = np.repeat(np.arange(G), M_U)
    acc, pq = {}, {}
    t0 = time.time()
    for rep in range(a.reps):
        rng = np.random.default_rng(crc(f"r5e3sim|pop|G{G}|rep{rep}"))
        base = [x[0] for x in Q1.gen_block(rng, G, M_U, 1, RHO)]
        mm, y0, a0, e0 = base
        for mu in mus:
            lev = mu * np.sqrt(1.0 + Q1.BETA ** 2)
            yh05 = Q1.yhat_at(y0 + lev, a0, e0, 0.5, RHO)
            for arm, r in arms:
                for est in ests:
                    if arm == "const" and est == "mean":
                        continue
                    y, yh, w, lev = population(G, rep, mu, arm, r, est, base, yh05)
                    T = TL.prepare(y.reshape(-1, 1), yh.reshape(-1, 1), w.reshape(-1), didx, G, est)
                    truth = {"design": float(T["theta_full"][0]),
                             "super": (Q1.BETA if est == "theta3" else Q1.MU + lev)}
                    k = (mu, arm, est)
                    q = pop_quantities(T, G)
                    pq.setdefault(k, np.zeros(4))[:] += np.r_[1.0, q]
                    for nL in nLs:
                        for m in ms:
                            tagc = f"G{G}|nL{nL}|m{m}|mu{mu}|arm{arm}|rep{rep}"
                            sr = np.random.default_rng(crc(f"r5e3sim|sel|{tagc}"))
                            Lc = np.zeros(G, bool)
                            Lc[sr.choice(G, nL, replace=False) if nL < G else np.arange(G)] = True
                            cl = np.flatnonzero(Lc)
                            if m == M_U:
                                pos = np.broadcast_to(np.arange(M_U), (len(cl), M_U))
                            else:
                                pos = np.argpartition(sr.random((len(cl), M_U)), m - 1, axis=1)[:, :m]
                            sel = (cl[:, None] * M_U + pos).ravel()
                            res = one_draw(T, G, nL, Lc, sel, f"r5e3sim|xf|{tagc}")
                            for (estr, xf), o in res.items():
                                for tgt in ("design", "super"):
                                    th, v, df = o[tgt]
                                    th, v = float(th[0]), float(v[0])
                                    qq = tq(df)
                                    se = np.sqrt(max(v, 0.0))
                                    ok = np.isfinite(th) and np.isfinite(v) and np.isfinite(qq)
                                    err = th - truth[tgt]
                                    cov = float(ok and abs(err) <= qq * se + 1e-9 * max(1.0, abs(truth[tgt])))
                                    d = acc.setdefault((nL, m, mu, arm, est, estr, xf, tgt), np.zeros(12))
                                    d[0] += 1
                                    if ok:
                                        d += np.r_[0, 0, 1, cov, 2 * qq * se, err, err * err, v, o["lam_w"], o["lam_c"], 0, 0]
                                    else:
                                        d[1] += 1
        if (rep + 1) % 20 == 0:
            print(f"G{G} {a.est} mu{a.mus} rep {rep+1}/{a.reps} {time.time()-t0:.0f}s", flush=True)
    rows = []
    for (nL, m, mu, arm, est, estr, xf, tgt), d in acc.items():
        n, bad, nok, cv, wsum, es, es2, vs, lw, lc = d[:10]
        mw = wsum / nok
        ev = (es2 - es * es / nok) / (nok - 1) if nok > 1 else np.nan
        pqv = pq[(mu, arm, est)]
        rows.append(dict(G=G, nL=nL, m=("all" if m == M_U else m), M=M_U, mu=mu, arm=arm, estimand=est, estimator=estr, xf=xf,
                         target=tgt, regime=("B" if nL == G else "A"), n_reps=int(n), n_nonfinite=int(bad),
                         coverage=cv / nok, mc_se=float(np.sqrt(cv / nok * (1 - cv / nok) / nok)), mean_width=mw,
                         emp_var=ev, mean_var=vs / nok, var_ratio=(vs / nok) / ev if ev and ev > 0 else np.nan,
                         bias=es / nok, lam_w_mean=lw / nok, lam_c_mean=lc / nok,
                         between_share=pqv[1] / pqv[0], R2_within=pqv[2] / pqv[0], R2_cluster=pqv[3] / pqv[0]))
    df = pd.DataFrame(rows)
    # width ratios: to the same form's classical estimator (same xf, same target) and to r4_classical
    key = ["G", "nL", "m", "mu", "arm", "estimand", "target"]
    own = df.assign(form=df.estimator.str.split("_").str[0], kind=df.estimator.str.split("_").str[1])
    cl = own[own.kind == "classical"][key + ["form", "xf", "mean_width"]].rename(columns={"mean_width": "w_own"})
    df = own.merge(cl, on=key + ["form", "xf"], how="left")
    r4 = own[own.estimator == "r4_classical"][key + ["xf", "mean_width"]].rename(columns={"mean_width": "w_r4cl"})
    df = df.merge(r4, on=key + ["xf"], how="left")
    df["width_ratio_own"] = df.mean_width / df.w_own
    df["width_ratio_r4cl"] = df.mean_width / df.w_r4cl
    df = df.drop(columns=["form", "kind", "w_own", "w_r4cl"])
    os.makedirs(a.out_dir, exist_ok=True)
    tag = f"G{G}_{a.est.replace(',', '+')}{a.tag}"
    df.to_csv(os.path.join(a.out_dir, f"e3_sim__{tag}.csv"), index=False)
    json.dump(dict(G=G, n_rows=len(df), reps=a.reps, mus=mus, nLs=nLs, ms=ms, est=ests, wall_s=time.time() - t0),
              open(os.path.join(a.out_dir, f"e3_sim_summary__{tag}.json"), "w"), indent=1)
    print("done", time.time() - t0, flush=True)


if __name__ == "__main__":
    main()
