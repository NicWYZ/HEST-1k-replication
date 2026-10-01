#!/usr/bin/env python
"""Round 4, PPI track, stage Q1: the simulation (source section 6 Q1, plan section 3).

One unit = one (G_L, rho) pair. Within a unit the grid is
  superpopulation target: G_U in {10, 20, 50}, m in {200, 1000, 5000}, r in {0, 0.3, 0.5, 0.8},
                          fresh donors every replicate;
  design-based target:    a fixed population of G = 24 donors drawn once per (m, rho, r), the
                          labelled donors drawn from it without replacement, U the other
                          24 - G_L donors (so the G_U grid does not apply; plan section 8
                          records this), m and r as above.
Estimands: the mean and theta_3 (slope on the covariate), spot-weighted and donor-weighted.
2,000 replicates per cell. Every estimator component of round4_ppi_estimator is applied to the
same replicates.

THE MODEL. Donor g, spot i.
  covariate  m_gi = c_g + d_gi, c ~ N(0, s_c), d ~ N(0, 1 - s_c), so E m = 0 and Var m = 1
             (standardised overall by construction).
  outcome    y_gi = mu + u_g + beta m_gi + e_gi, u ~ N(0, rho), e ~ N(0, 1 - rho).
  predictor  yhat_gi = y_gi - a_g - eps_gi, a ~ N(0, rho / 2) (half of sigma_u^2), eps scaled
             so that corr(y, yhat) = r at the spot level, Var eps = Var y (1/r^2 - 1) - rho/2.
             At r = 0 that construction does not exist (plan section 8 item 1). Addendum 1
             (plan section 11.1 item 1) fixes the r = 0 predictor as yhat = nu + p_g + d_gi,
             p ~ N(0, sigma_u^2 = rho), d ~ N(0, sigma_e^2 = 1 - rho), independent of
             everything else, so it has the outcome's between-donor share; nu = mu = 0.
  Unspecified by the source and fixed here (recorded in the config): mu = 0, beta = 0.3,
  s_c = 0.3 (the covariate's between-donor share).

THE ESTIMANDS as means of a per-spot scalar z, as in round3_b1_ppi.py.
  mean      z = y.
  theta_3   spot-weighted z = (m - mu_m) y / V_m with label-free constants: the known
            population values (0, 1) for the superpopulation target, the fixed population's
            values for the design target. Donor-weighted: the donor's own OLS slope,
            t_g = sum (m - mbar_g) y / sum (m - mbar_g)^2 over all its spots.
  Truths: superpopulation mean mu, theta_3 beta, both populations; design-based, the values
  on the fixed population.

FORMS (addendum 1 section 2, plan section 11.2). Every row carries `form`.
  design target   `textbook`, the difference estimator with the prediction term over the whole
                  fixed population, primary; and `complement`, B1's lambda * mean_U(f) +
                  mean_L(r) with U the unlabelled donors, as a named legacy variant. No
                  Welch-Satterthwaite rows in the design arm (there is no random U term).
  superpopulation `complement` (U is G_U fresh donors independent of L), with the
                  Welch-Satterthwaite rows.

OUTPUT, per unit: q1_sim__GL<G_L>__rho<rho>.csv, one row per
(cell, estimand, population, form, lambda rule, interval, fpc) with coverage at 90%, its MC
standard error, mean and median width, the mean width of the classical estimator with the
same interval and fpc, their ratio, lambda summaries, mean df, the empirical sd of the
estimate, the root mean estimated variance, bias, and non-finite counts. A summary JSON with
timings goes beside it, written first.
"""
import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round4_ppi_estimator as E  # noqa: E402

GRID = dict(G_U=(10, 20, 50), m=(200, 1000, 5000), r=(0.0, 0.3, 0.5, 0.8))
G_DESIGN = 24
MU, BETA, S_C = 0.0, 0.3, 0.3
RULES = ("none", "a_b1", "b_cluster", "c_crossfit")
ESTS = ("mean", "theta3")
POPS = ("spot", "donor")


# ============================================================== data
def gen_block(rng, G, m, R, rho):
    """R replicates of G donors with m spots each. Returns the pieces from which y and yhat
    at any r are formed, as arrays (R, G, m) or (R, G, 1)."""
    c = rng.normal(0.0, np.sqrt(S_C), size=(R, G, 1))
    d = rng.normal(0.0, np.sqrt(1.0 - S_C), size=(R, G, m))
    u = rng.normal(0.0, np.sqrt(rho), size=(R, G, 1))
    e = rng.normal(0.0, np.sqrt(1.0 - rho), size=(R, G, m))
    a0 = rng.normal(size=(R, G, 1))
    eps0 = rng.normal(size=(R, G, m))
    mm = c + d
    y = MU + u + BETA * mm + e
    return mm, y, a0, eps0


def yhat_at(y, a0, eps0, r, rho):
    var_y = BETA ** 2 + 1.0
    sa = np.sqrt(rho / 2.0)
    if r == 0.0:
        # addendum 1: nu + p_g + d_gi, p ~ N(0, rho), d ~ N(0, 1 - rho), independent of y
        return MU + np.sqrt(rho) * a0 + np.sqrt(1.0 - rho) * eps0
    ve = var_y * (1.0 / r ** 2 - 1.0) - rho / 2.0
    assert ve >= 0, (r, rho, ve)
    return y - sa * a0 - np.sqrt(ve) * eps0


def donor_stats(z, zf):
    """Per-donor sufficient statistics, arrays (G, R), from per-spot (R, G, m)."""
    return dict(n=np.full(z.shape[:2], float(z.shape[2])).T,
                Sz=z.sum(2).T, Sf=zf.sum(2).T, Szz=(z * z).sum(2).T,
                Sff=(zf * zf).sum(2).T, Szf=(z * zf).sum(2).T)


def donor_value_stats(t, tf):
    """Donor-level values packed so that donor_values() returns them (n = 1)."""
    return dict(n=np.ones_like(t), Sz=t, Sf=tf, Szz=t * t, Sff=tf * tf, Szf=t * tf)


def build_stats(mm, y, yh, consts):
    """Sufficient statistics for every (estimand, population)."""
    out = {}
    out[("mean", "spot")] = donor_stats(y, yh)
    out[("mean", "donor")] = donor_value_stats(y.mean(2).T, yh.mean(2).T)
    mu_m, v_m = consts
    w = (mm - mu_m) / v_m
    out[("theta3", "spot")] = donor_stats(w * y, w * yh)
    dm = mm - mm.mean(2, keepdims=True)
    sxx = (dm * dm).sum(2)
    out[("theta3", "donor")] = donor_value_stats(((dm * y).sum(2) / sxx).T,
                                                 ((dm * yh).sum(2) / sxx).T)
    return out


def _n_for_iid(D_don, m):
    """Donor-value stats carry n = 1; the donor population's i.i.d. variance needs the spot
    count, so it is restored here (the estimator reads t = Sz / n, so Sz is scaled too)."""
    D = {k: v * m for k, v in D_don.items() if k in ("Sz", "Sf")}
    D["n"] = np.full_like(D_don["n"], float(m))
    D["Szz"] = D_don["Szz"] * m * m
    D["Sff"] = D_don["Sff"] * m * m
    D["Szf"] = D_don["Szf"] * m * m
    return D


# ============================================================== one cell
def run_cell(stats_list, masks, truth, G_pop, design, seed, n_boot, m):
    """stats_list: dict (est, pop) -> D with columns = replicates in this chunk.
    Returns dict key -> dict of per-replicate arrays."""
    Lm, Um = masks
    out = {}
    for (est, pop), D0 in stats_list.items():
        D = _n_for_iid(D0, m) if pop == "donor" else D0
        tr = truth[(est, pop)]
        tr = np.broadcast_to(tr, (Lm.shape[1],))
        for rule in RULES:
            sd = f"{seed}|{est}|{pop}|{rule}"
            lam, res, iv = E.all_intervals(pop, D, Lm, Um, rule, tr, G_pop=G_pop, seed=sd,
                                           n_boot=n_boot, design_exact=design,
                                           with_ws=not design)
            runs = [("complement", lam, res["theta"], iv)]
            if design:
                lam_t, tb, iv_t = E.textbook_intervals(pop, D, Lm, Um, rule, seed=sd,
                                                       n_boot=n_boot)
                runs.append(("textbook", lam_t, tb["theta"], iv_t))
            for form, lm, th, ivs in runs:
                for name, v in ivs.items():
                    base, _, f = name.partition("|")
                    key = (est, pop, form, rule, base, f == "fpc")
                    out[key] = dict(cov=(v["lo"] <= tr) & (tr <= v["hi"]),
                                    width=v["hi"] - v["lo"], lam=lm["lam"], df=v["df"],
                                    theta=th, var=v["var"],
                                    finite=np.isfinite(v["lo"]) & np.isfinite(v["hi"]),
                                    truth=tr)
    return out


def merge_chunks(acc, new):
    for k, v in new.items():
        if k not in acc:
            acc[k] = {kk: [vv] for kk, vv in v.items()}
        else:
            for kk, vv in v.items():
                acc[k][kk].append(vv)


def summarise(acc, cell):
    rows = []
    fin = {k: {kk: np.concatenate(vv) for kk, vv in v.items()} for k, v in acc.items()}
    for (est, pop, form, rule, iv, fpc), v in fin.items():
        R = len(v["cov"])
        ok = v["finite"]
        cov = float(np.mean(v["cov"][ok])) if ok.any() else np.nan
        cl = fin.get((est, pop, form, "none", iv, fpc))
        wcl = float(np.nanmean(cl["width"])) if cl is not None else np.nan
        w = float(np.nanmean(v["width"][ok])) if ok.any() else np.nan
        lam = v["lam"]
        rows.append(dict(**cell, estimand=est, population=pop, form=form,
                         estimator="classical" if rule == "none" else "ppi",
                         lambda_rule=rule, interval=iv, fpc=bool(fpc), n_reps=R,
                         n_nonfinite=int((~ok).sum()), coverage=cov,
                         mc_se=float(np.sqrt(cov * (1 - cov) / max(ok.sum(), 1))),
                         mean_width=w, median_width=float(np.nanmedian(v["width"][ok])) if ok.any() else np.nan,
                         classical_mean_width=wcl, width_ratio=w / wcl if wcl > 0 else np.nan,
                         lambda_mean=float(np.mean(lam)), lambda_median=float(np.median(lam)),
                         lambda_frac_le_005=float(np.mean(lam <= 0.05)),
                         mean_df=float(np.nanmean(np.where(np.isinf(v["df"]), np.nan, v["df"])))
                         if np.isfinite(v["df"]).any() else np.nan,
                         truth=float(np.mean(v["truth"])),
                         bias=float(np.mean(v["theta"] - v["truth"])),
                         emp_sd=float(np.std(v["theta"], ddof=1)),
                         rms_se=float(np.sqrt(np.nanmean(v["var"])))))
    return rows


# ============================================================== the two targets
def superpop_cells(G_L, rho, R, chunk, n_boot, t0, log, max_spots):
    rows = []
    for G_U in GRID["G_U"]:
        for m in GRID["m"]:
            G = G_L + G_U
            accs = {r: {} for r in GRID["r"]}
            rng = E.seed_rng(f"q1|super|GL{G_L}|GU{G_U}|m{m}|rho{rho}")
            done = 0
            ch = 0
            while done < R:
                n = min(chunk, R - done)
                sub = max(1, int(max_spots // (G * m)))
                parts = {r: [] for r in GRID["r"]}
                for s0 in range(0, n, sub):
                    rr = min(sub, n - s0)
                    mm, y, a0, eps0 = gen_block(rng, G, m, rr, rho)
                    for r in GRID["r"]:
                        yh = yhat_at(y, a0, eps0, r, rho)
                        parts[r].append(build_stats(mm, y, yh, (0.0, 1.0)))
                Lm = np.zeros((G, n), bool); Lm[:G_L] = True
                Um = ~Lm
                truth = {(e, p): (MU if e == "mean" else BETA) for e in ESTS for p in POPS}
                for r in GRID["r"]:
                    st = {k: {kk: np.concatenate([pp[k][kk] for pp in parts[r]], axis=1)
                              for kk in E.STAT_KEYS} for k in parts[r][0]}
                    new = run_cell(st, (Lm, Um), truth, G, False,
                                   f"q1|super|GL{G_L}|GU{G_U}|m{m}|rho{rho}|r{r}|ch{ch}",
                                   n_boot, m)
                    merge_chunks(accs[r], new)
                done += n
                ch += 1
            for r in GRID["r"]:
                rows += summarise(accs[r], dict(target="super", G_L=G_L, G_U=G_U, G_pop=G,
                                                m=m, rho=rho, r=r))
            log(f"[super] GL{G_L} GU{G_U} m{m} rho{rho} done {time.time()-t0:.0f}s")
    return rows


def design_cells(G_L, rho, R, chunk, n_boot, t0, log, max_spots):
    rows = []
    G = G_DESIGN
    G_U = G - G_L
    for m in GRID["m"]:
        # the fixed population is shared by every G_L unit: its seed does not name G_L
        rng = E.seed_rng(f"q1|design|pop|m{m}|rho{rho}")
        mm, y, a0, eps0 = gen_block(rng, G, m, 1, rho)
        consts = (float(mm.mean()), float(mm.var()))
        for r in GRID["r"]:
            yh = yhat_at(y, a0, eps0, r, rho)
            st1 = build_stats(mm, y, yh, consts)
            truth = {}
            for (e, p), D in st1.items():
                if p == "spot":
                    truth[(e, p)] = float(D["Sz"].sum() / D["n"].sum())
                else:
                    truth[(e, p)] = float(D["Sz"].mean())
            acc = {}
            rsel = E.seed_rng(f"q1|design|draws|GL{G_L}|m{m}|rho{rho}|r{r}")
            done, ch = 0, 0
            while done < R:
                n = min(chunk, R - done)
                Lm = np.zeros((G, n), bool)
                for j in range(n):
                    Lm[rsel.choice(G, G_L, replace=False), j] = True
                Um = ~Lm
                st = {k: {kk: np.repeat(v[kk], n, axis=1) for kk in E.STAT_KEYS}
                      for k, v in st1.items()}
                new = run_cell(st, (Lm, Um), truth, G, True,
                               f"q1|design|GL{G_L}|m{m}|rho{rho}|r{r}|ch{ch}", n_boot, m)
                merge_chunks(acc, new)
                done += n
                ch += 1
            rows += summarise(acc, dict(target="design", G_L=G_L, G_U=G_U, G_pop=G, m=m,
                                        rho=rho, r=r))
        log(f"[design] GL{G_L} m{m} rho{rho} done {time.time()-t0:.0f}s")
    return rows


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--G-L", type=int, required=True)
    p.add_argument("--rho", type=float, required=True)
    p.add_argument("--reps", type=int, default=2000)
    p.add_argument("--chunk", type=int, default=250)
    p.add_argument("--n-boot", type=int, default=500)
    p.add_argument("--max-spots", type=float, default=4e6,
                   help="spots generated per sub-batch (memory bound)")
    p.add_argument("--targets", default="design,super")
    p.add_argument("--m-grid", default="")
    p.add_argument("--GU-grid", default="")
    p.add_argument("--out-dir", required=True)
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    if a.m_grid:
        GRID["m"] = tuple(int(x) for x in a.m_grid.split(","))
    if a.GU_grid:
        GRID["G_U"] = tuple(int(x) for x in a.GU_grid.split(","))
    os.makedirs(a.out_dir, exist_ok=True)
    cfg = dict(stage="r4ppi_Q1_sim", G_L=a.G_L, rho=a.rho, reps=a.reps, chunk=a.chunk,
               n_boot=a.n_boot, grid={k: list(v) for k, v in GRID.items()},
               G_design=G_DESIGN, mu=MU, beta=BETA, s_c=S_C, sigma_a2="rho/2",
               rules=list(RULES), estimands=list(ESTS), populations=list(POPS),
               r0_predictor="nu + p_g + d_gi, p~N(0,rho), d~N(0,1-rho) (addendum 1)",
               forms={"design": ["textbook", "complement"], "super": ["complement"]},
               alpha=E.ALPHA, min_tune_g=E.MIN_TUNE_G, targets=a.targets,
               seed_source="zlib.crc32")
    blob = json.dumps(cfg, sort_keys=True)
    chash = hashlib.sha256(blob.encode()).hexdigest()[:16]
    tag = f"GL{a.G_L}__rho{a.rho}"
    with open(f"{a.out_dir}/q1_sim_config__{tag}.json", "w") as fh:
        fh.write(blob)
    t0 = time.time()
    log = lambda s: print(s, flush=True)  # noqa: E731
    rows, timing = [], {}
    for tgt in a.targets.split(","):
        t1 = time.time()
        fn = design_cells if tgt == "design" else superpop_cells
        rows += fn(a.G_L, a.rho, a.reps, a.chunk, a.n_boot, t0, log, a.max_spots)
        timing[tgt] = time.time() - t1
    df = pd.DataFrame(rows)
    summ = dict(config_hash=chash, n_rows=len(df), wall_s=time.time() - t0, timing_s=timing,
                n_cells=int(df.groupby(["target", "G_U", "m", "r"]).ngroups),
                coverage_min=float(df.coverage.min()), coverage_max=float(df.coverage.max()),
                any_nonfinite=int(df.n_nonfinite.sum()))
    with open(f"{a.out_dir}/q1_sim_summary__{tag}.json", "w") as fh:
        json.dump(summ, fh, indent=1)
    df.to_csv(f"{a.out_dir}/q1_sim__{tag}.csv", index=False)
    log(json.dumps(summ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
