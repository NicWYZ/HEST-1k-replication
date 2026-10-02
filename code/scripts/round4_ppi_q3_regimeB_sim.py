#!/usr/bin/env python
"""Round 4 PPI track, Q3: regime B arm of the Q1 simulation (plan section 3).

Superpopulation target, fresh G donors per replicate, M = 1000 spots per donor, m labelled spots per
donor drawn uniformly without replacement (a fresh draw per replicate and donor). Generator:
round4_ppi_q1_sim.gen_block / yhat_at (unedited). Estimator: round4_ppi_q3_regimes.regime_b (unedited).
Truth: mu = 0 (mean), beta = 0.3 (theta_3), as in Q1.

Reduction used for speed, exact: regime_b reads the donor mean of zf over ALL spots and the labelled
spots' z, zf. For each donor the driver passes the m labelled spots plus ONE unlabelled pseudo-spot whose zf
is (m+1) fbar_g - sum(labelled zf), so the donor mean over the passed spots equals fbar_g exactly; M and m_g
are passed explicitly. `check()` compares this against the full-spot call and the run aborts if the largest
difference exceeds 1e-8.

Targets per cell: `super` (primary: CR1 over donors, t_{G-1}; t_{G-2} under cross-fitting, truth mu/beta)
and `design_on_realised` (labelled variant: regime_b's design interval, truth the replicate's realised
population mean of z over all its G x M spots).
"""
import argparse, json, os, sys, time
import numpy as np
import pandas as pd

import round4_ppi_estimator as E
import round4_ppi_q1_sim as Q1
import round4_ppi_q3_regimes as Q3

M_SPOTS = 1000
MS = (1, 5, 20, 100)
RHOS = (0.1, 0.3, 0.5)
RS = (0.0, 0.5, 0.8)
RULES = ("none", "c_crossfit", "d1_pretest", "d2_pretest")
ESTP = (("mean", "spot"), ("mean", "donor"), ("theta3", "spot"), ("theta3", "donor"))


def z_full(est, pop, mm, y, yh):
    """per-spot z and zf, arrays (R, G, M); same definitions as Q1.build_stats."""
    if est == "mean":
        return y, yh
    if pop == "spot":
        return mm * y, mm * yh
    dm = mm - mm.mean(2, keepdims=True)
    sxx_n = (dm * dm).mean(2, keepdims=True)
    return dm * y / sxx_n, dm * yh / sxx_n


def reduced(z, zf, idx):
    """z, zf (R,G,M); idx (R,G,m) labelled positions -> reduced arrays (G*(m+1), R), didx, sel."""
    R, G, M = z.shape
    m = idx.shape[2]
    zl = np.take_along_axis(z, idx, 2)
    fl = np.take_along_axis(zf, idx, 2)
    fbar = zf.mean(2)
    pseudo = (m + 1) * fbar - fl.sum(2)
    Zr = np.concatenate([zl, np.zeros((R, G, 1))], 2)
    Fr = np.concatenate([fl, pseudo[:, :, None]], 2)
    f = lambda a: a.transpose(1, 2, 0).reshape(G * (m + 1), R)
    didx = np.repeat(np.arange(G), m + 1)
    sel = np.tile(np.r_[np.ones(m, bool), False], G)
    return f(Zr), f(Fr), didx, sel


def run_one(z, zf, idx, G, m, pop, rule, seed):
    Zr, Fr, didx, sel = reduced(z, zf, idx)
    return Q3.regime_b(Zr, Fr, didx, np.ones(G, bool), np.full(G, float(M_SPOTS)),
                       np.full(G, float(m)), sel, pop, rule, seed)


def check(G, rho, r, rng, tol=1e-8):
    R = 6
    out = []
    mm, y, a0, e0 = Q1.gen_block(rng, G, M_SPOTS, R, rho)
    yh = Q1.yhat_at(y, a0, e0, r, rho)
    for m in (1, 5, 20):
        keys = rng.random((R, G, M_SPOTS))
        idx = np.argpartition(keys, m - 1, axis=2)[..., :m]
        for est, pop in ESTP:
            z, zf = z_full(est, pop, mm, y, yh)
            for rule in RULES:
                seed = f"chk|{G}|{m}|{est}|{pop}|{rule}"
                o1 = run_one(z, zf, idx, G, m, pop, rule, seed)
                # full-spot path
                Z = z.transpose(1, 2, 0).reshape(G * M_SPOTS, R)
                F = zf.transpose(1, 2, 0).reshape(G * M_SPOTS, R)
                sel = np.zeros((R, G, M_SPOTS), bool)
                np.put_along_axis(sel, idx, True, 2)
                # one shared sel is required by regime_b, so compare column by column
                dif = 0.0
                for j in range(R):
                    s = sel[j].reshape(-1)
                    o2 = Q3.regime_b(Z[:, [j]], F[:, [j]], np.repeat(np.arange(G), M_SPOTS), np.ones(G, bool),
                                     np.full(G, float(M_SPOTS)), np.full(G, float(m)), s, pop, rule, seed)
                    r1 = run_one(z[[j]], zf[[j]], idx[[j]], G, m, pop, rule, seed)
                    for t in ("design", "super"):
                        for k in range(2):
                            a, b = np.asarray(r1[t][k]).ravel()[0], np.asarray(o2[t][k]).ravel()[0]
                            if np.isfinite(a) or np.isfinite(b):
                                dif = max(dif, abs(a - b))
                    if np.isfinite(r1["lam"][0]) or np.isfinite(o2["lam"][0]):
                        dif = max(dif, abs(r1["lam"][0] - o2["lam"][0]))
                out.append(dict(G=G, m=m, est=est, pop=pop, rule=rule, maxdiff=dif))
    mx = max(o["maxdiff"] for o in out)
    assert mx < tol, ("reduced path differs from full path", mx)
    return mx, len(out)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--G", type=int, required=True)
    p.add_argument("--reps", type=int, default=2000)
    p.add_argument("--chunk", type=int, default=100)
    p.add_argument("--rhos", default=",".join(map(str, RHOS)))
    p.add_argument("--tag", default="")
    p.add_argument("--out-dir", required=True)
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    os.makedirs(a.out_dir, exist_ok=True)
    G = a.G
    rhos = tuple(float(x) for x in a.rhos.split(","))
    tag = f"G{G}{a.tag}"
    t0 = time.time()
    mx, nchk = check(12 if G == 12 else G, 0.3, 0.5, E.seed_rng(f"q3Bsim|check|G{G}"))
    print(f"check ok: {nchk} combos, max diff reduced vs full {mx:.3e}", flush=True)
    json.dump(dict(G=G, n_combos=nchk, max_abs_diff=mx), open(f"{a.out_dir}/regimeB_check__{tag}.json", "w"))
    cfg = dict(stage="r4ppi_Q3_regimeB_sim", G=G, M=M_SPOTS, m=list(MS), rho=list(rhos), r=list(RS), reps=a.reps,
               chunk=a.chunk, rules=list(RULES), mu=Q1.MU, beta=Q1.BETA, s_c=Q1.S_C, alpha=E.ALPHA)
    json.dump(cfg, open(f"{a.out_dir}/regimeB_config__{tag}.json", "w"), indent=1)
    acc = {}
    for rho in rhos:
        rng = E.seed_rng(f"q3Bsim|G{G}|rho{rho}")
        rsel = E.seed_rng(f"q3Bsim|sel|G{G}|rho{rho}")
        done, ch = 0, 0
        while done < a.reps:
            n = min(a.chunk, a.reps - done)
            mm, y, a0, e0 = Q1.gen_block(rng, G, M_SPOTS, n, rho)
            keys = rsel.random((n, G, M_SPOTS))
            idxs = {m: np.argpartition(keys, m - 1, axis=2)[..., :m] for m in MS}
            del keys
            for r in RS:
                yh = Q1.yhat_at(y, a0, e0, r, rho)
                for est, pop in ESTP:
                    z, zf = z_full(est, pop, mm, y, yh)
                    real = z.mean((1, 2))
                    tr = Q1.MU if est == "mean" else Q1.BETA
                    for m in MS:
                        for rule in RULES:
                            seed = f"q3Bsim|G{G}|rho{rho}|ch{ch}|r{r}|m{m}|{est}|{pop}|{rule}"
                            o = run_one(z, zf, idxs[m], G, m, pop, rule, seed)
                            for tgt, truth in (("super", tr), ("design_on_realised", real)):
                                th, v, df = o["design" if tgt != "super" else "super"]
                                lo, hi = E.t_interval(th, v, np.full(th.shape, float(df)))
                                k = (rho, r, m, est, pop, tgt, rule)
                                d = acc.setdefault(k, dict(th=[], var=[], lo=[], hi=[], lam=[], tr=[], df=df))
                                d["th"].append(th); d["var"].append(v); d["lo"].append(lo); d["hi"].append(hi)
                                d["lam"].append(o["lam"]); d["tr"].append(np.broadcast_to(truth, th.shape).copy())
                del z, zf
            done += n; ch += 1
            print(f"G{G} rho{rho} {done}/{a.reps} {time.time()-t0:.0f}s", flush=True)
    rows = []
    fin = {k: {kk: (np.concatenate(vv) if isinstance(vv, list) else vv) for kk, vv in d.items()} for k, d in acc.items()}
    for (rho, r, m, est, pop, tgt, rule), d in fin.items():
        ok = np.isfinite(d["lo"]) & np.isfinite(d["hi"])
        cv = (d["lo"] <= d["tr"]) & (d["tr"] <= d["hi"])
        cov = float(cv[ok].mean()) if ok.any() else np.nan
        w = d["hi"] - d["lo"]
        cl = fin[(rho, r, m, est, pop, tgt, "none")]
        wcl = float(np.nanmean((cl["hi"] - cl["lo"])[np.isfinite(cl["lo"]) & np.isfinite(cl["hi"])])) if ok.any() else np.nan
        wm = float(np.mean(w[ok])) if ok.any() else np.nan
        lam = d["lam"]
        rms = float(np.sqrt(np.nanmean(d["var"])))
        rows.append(dict(G=G, M=M_SPOTS, m=m, rho=rho, r=r, estimand=est, population=pop, target=tgt,
                         lambda_rule=rule, estimator="classical" if rule == "none" else "ppi",
                         df=float(d["df"]), n_reps=len(ok), n_nonfinite=int((~ok).sum()), coverage=cov,
                         mc_se=float(np.sqrt(cov * (1 - cov) / max(ok.sum(), 1))) if ok.any() else np.nan,
                         mean_width=wm, classical_mean_width=wcl, width_ratio=wm / wcl if wcl > 0 else np.nan,
                         emp_sd=float(np.std(d["th"], ddof=1)), rms_se=rms,
                         sd_over_rms_se=float(np.std(d["th"], ddof=1)) / rms if rms > 0 else np.nan,
                         bias=float(np.mean(d["th"] - d["tr"])),
                         lambda_mean=float(np.nanmean(lam)), lambda_median=float(np.nanmedian(lam)),
                         lambda_frac_le_005=float(np.mean(lam <= 0.05))))
    df = pd.DataFrame(rows)
    df.to_csv(f"{a.out_dir}/regimeB_sim__{tag}.csv", index=False)
    s = df[df.target == "super"]
    json.dump(dict(G=G, n_rows=len(df), wall_s=time.time() - t0, check_maxdiff=mx,
                   coverage_min_super=float(s.coverage.min()), coverage_max_super=float(s.coverage.max())),
              open(f"{a.out_dir}/regimeB_summary__{tag}.json", "w"), indent=1)
    print("done", time.time() - t0, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
