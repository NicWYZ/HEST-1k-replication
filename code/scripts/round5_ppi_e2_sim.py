"""Round 5 PPI, stage E2 part 2: regime B in simulation with an outcome level.

Built on the round-4 regime B simulation (round4_ppi_q3_regimeB_sim.py, imported unmodified), whose
generator is round4_ppi_q1_sim.gen_block / yhat_at and whose estimator is round4_ppi_q3_regimes.regime_b.
G = 24, M = 1000, between-cluster share rho = 0.3, m in {2, 5, 20, 100}, 2,000 replicates.

The level. The round-4 outcome has mean MU = 0 and variance 1 + BETA^2. Here y = y_round4 + mu * sd(y),
mu in {0, 1, 3, 10}, the same random draws at every mu, so the comparisons across mu are paired.
Arms (all built from the round-4 pieces):
  r0.5, r0.8   yhat_at(y, ...) with unit-level correlation r; it inherits the level through y
  uninf        the round-4 r = 0 predictor (independent of y) plus the same level
  const        every unit of a replicate gets that replicate's task-wide mean of the r0.5 predictor
               (skipped for the mean, where it has no within-cluster variance)
Estimands theta3 and the mean, both populations; targets 'super' (truth BETA or the level) and
'design_on_realised' (truth the replicate's realised mean of z over all G x M units); rules none and
c_crossfit.

Seeds are the round-4 strings: gen_block and the selection keys from q3Bsim|G24|rho0.3 and
q3Bsim|sel|G24|rho0.3 in chunks of 100, and regime_b's cross-fit seed
q3Bsim|G24|rho0.3|ch<k>|r<r>|m<m>|<est>|<pop>|<rule> with r the round-4 label (0.5, 0.8, 0.0 for uninf,
'const' for the constant). So at mu = 0 the arms r0.5, r0.8 and uninf, at m = 5, 20 and 100, are the
round-4 replicates themselves, which is E2 acceptance check 3's anchor.

The level share. For every replicate, arm, estimand and population the script also computes from the
full simulated population the pooled within-cluster quantities of docs/round5_ppi_theory.md section 1.2,
with equal cluster weights (equal M and m): S_zf = sum_g Cov_g(z, f), S_ff = sum_g Var_g(f),
S_zz = sum_g Var_g(z); the unclipped share S_zf^2/(S_ff S_zz) and the share removed at the clipped
coefficient clip(S_zf/S_ff, 0, 1), (2 l S_zf - l^2 S_ff)/S_zz.
"""
import argparse
import json
import os
import time

import numpy as np
import pandas as pd

import round4_ppi_q3_regimeB_sim as S3

Q1, E = S3.Q1, S3.E
G_DEF, M_SPOTS, RHO = 24, S3.M_SPOTS, 0.3
MS = (2, 5, 20, 100)
MUS = (0.0, 1.0, 3.0, 10.0)
RULES = ("none", "c_crossfit")
ARMS = (("r0.5", 0.5), ("r0.8", 0.8), ("uninf", 0.0), ("const", "const"))
ESTP = S3.ESTP


def pooled_share(z, zf):
    """z, zf (R, G, M) -> per replicate unclipped share, clipped share and coefficient."""
    zc = z - z.mean(2, keepdims=True)
    fc = zf - zf.mean(2, keepdims=True)
    szf = (zc * fc).mean(2).sum(1)
    sff = (fc * fc).mean(2).sum(1)
    szz = (zc * zc).mean(2).sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        lam = np.where(sff > 0, szf / sff, np.nan)
        un = np.where(sff > 0, szf ** 2 / (sff * szz), 0.0)
        lc = np.clip(np.nan_to_num(lam), 0.0, 1.0)
        cl = (2 * lc * szf - lc ** 2 * sff) / szz
    return un, cl, lam


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--G", type=int, default=G_DEF)
    p.add_argument("--reps", type=int, default=2000)
    p.add_argument("--chunk", type=int, default=100)
    p.add_argument("--mus", default=",".join(map(str, MUS)))
    p.add_argument("--tag", default="")
    p.add_argument("--out-dir", default=".")
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    G = a.G
    mus = tuple(float(x) for x in a.mus.split(","))
    sd_y = float(np.sqrt(1.0 + Q1.BETA ** 2))
    t0 = time.time()
    rng = E.seed_rng(f"q3Bsim|G{G}|rho{RHO}")
    rsel = E.seed_rng(f"q3Bsim|sel|G{G}|rho{RHO}")
    acc, shares = {}, {}
    done, ch = 0, 0
    while done < a.reps:
        n = min(a.chunk, a.reps - done)
        mm, y0, a0, e0 = Q1.gen_block(rng, G, M_SPOTS, n, RHO)
        keys = rsel.random((n, G, M_SPOTS))
        idxs = {m: np.argpartition(keys, m - 1, axis=2)[..., :m] for m in MS}
        del keys
        for mu in mus:
            lev = mu * sd_y
            y = y0 + lev
            yh05 = Q1.yhat_at(y, a0, e0, 0.5, RHO)
            for arm, r in ARMS:
                if arm == "const":
                    yh = np.broadcast_to(yh05.mean((1, 2), keepdims=True), y.shape).copy()
                elif r == 0.0:
                    yh = Q1.yhat_at(y0, a0, e0, 0.0, RHO) + lev
                else:
                    yh = Q1.yhat_at(y, a0, e0, r, RHO)
                rlab = "const" if arm == "const" else r
                for est, pop in ESTP:
                    if arm == "const" and est == "mean":
                        continue
                    z, zf = S3.z_full(est, pop, mm, y, yh)
                    real = z.mean((1, 2))
                    tr = (Q1.MU + lev) if est == "mean" else Q1.BETA
                    un, cl, lam = pooled_share(z, zf)
                    sh = shares.setdefault((mu, arm, est, pop), dict(un=[], cl=[], lam=[]))
                    sh["un"].append(un); sh["cl"].append(cl); sh["lam"].append(lam)
                    for m in MS:
                        for rule in RULES:
                            seed = f"q3Bsim|G{G}|rho{RHO}|ch{ch}|r{rlab}|m{m}|{est}|{pop}|{rule}"
                            o = S3.run_one(z, zf, idxs[m], G, m, pop, rule, seed)
                            for tgt, truth in (("super", tr), ("design_on_realised", real)):
                                th, v, df = o["design" if tgt != "super" else "super"]
                                lo, hi = E.t_interval(th, v, np.full(th.shape, float(df)))
                                d = acc.setdefault((mu, arm, m, est, pop, tgt, rule),
                                                   dict(th=[], var=[], lo=[], hi=[], lam=[], tr=[], real=[], df=df))
                                d["th"].append(th); d["var"].append(v); d["lo"].append(lo); d["hi"].append(hi)
                                d["lam"].append(o["lam"]); d["tr"].append(np.broadcast_to(truth, th.shape).copy())
                                d["real"].append(real)
                    del z, zf
        done += n; ch += 1
        print(f"G{G} {done}/{a.reps} {time.time()-t0:.0f}s", flush=True)
    fin = {k: {kk: (np.concatenate(vv) if isinstance(vv, list) else vv) for kk, vv in d.items()} for k, d in acc.items()}
    shf = {k: {kk: np.concatenate(vv) for kk, vv in d.items()} for k, d in shares.items()}
    rows = []
    for (mu, arm, m, est, pop, tgt, rule), d in fin.items():
        ok = np.isfinite(d["lo"]) & np.isfinite(d["hi"])
        cv = (d["lo"] <= d["tr"]) & (d["tr"] <= d["hi"])
        cov = float(cv[ok].mean()) if ok.any() else np.nan
        w = d["hi"] - d["lo"]
        cl = fin[(mu, arm, m, est, pop, tgt, "none")]
        okc = np.isfinite(cl["lo"]) & np.isfinite(cl["hi"])
        wcl = float(np.mean((cl["hi"] - cl["lo"])[okc])) if okc.any() else np.nan
        wm = float(np.mean(w[ok])) if ok.any() else np.nan
        err = d["th"] - d["real"]
        err_cl = cl["th"] - cl["real"]
        sh = shf[(mu, arm, est, pop)]
        rms = float(np.sqrt(np.nanmean(d["var"])))
        rows.append(dict(G=G, M=M_SPOTS, m=m, rho=RHO, mu=mu, arm=arm, estimand=est, population=pop, target=tgt,
                         lambda_rule=rule, df=float(d["df"]), n_reps=len(ok), n_nonfinite=int((~ok).sum()),
                         coverage=cov, mc_se=float(np.sqrt(cov * (1 - cov) / max(ok.sum(), 1))) if ok.any() else np.nan,
                         mean_width=wm, classical_mean_width=wcl, width_ratio=wm / wcl if wcl > 0 else np.nan,
                         emp_sd=float(np.std(d["th"], ddof=1)), rms_se=rms,
                         design_err_var=float(np.var(err, ddof=1)),
                         design_err_var_ratio_to_classical=float(np.var(err, ddof=1) / np.var(err_cl, ddof=1)),
                         bias=float(np.mean(d["th"] - d["tr"])),
                         lambda_mean=float(np.nanmean(d["lam"])), lambda_median=float(np.nanmedian(d["lam"])),
                         share_unclipped_mean=float(np.nanmean(sh["un"])), share_clipped_mean=float(np.nanmean(sh["cl"])),
                         pooled_coef_unclipped_median=float(np.nanmedian(sh["lam"]))))
    os.makedirs(a.out_dir, exist_ok=True)
    tag = f"G{G}{a.tag}"
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(a.out_dir, f"e2_sim__{tag}.csv"), index=False)
    json.dump(dict(G=G, n_rows=len(df), reps=a.reps, mus=list(mus), ms=list(MS), wall_s=time.time() - t0),
              open(os.path.join(a.out_dir, f"e2_sim_summary__{tag}.json"), "w"), indent=1)
    print("done", time.time() - t0, flush=True)


if __name__ == "__main__":
    main()
