#!/usr/bin/env python
"""Round 4, PPI track, unit Q1b: the Q1 supplement (Q1 decision memo section 3; plan section 13.3).

One unit = one G_L. The Q1 generator and code paths (round4_ppi_q1_sim.py, round4_ppi_estimator.py)
with three additions.

GRID. G_L given; superpopulation G_U = 20; m in {200, 1000}; rho in {0.1, 0.3, 0.5};
r in {0, 0.5, 0.8}; estimands mean and theta_3, spot- and donor-weighted; targets superpopulation
(complement form) and design-based (fixed population of G = 24, textbook form, plus the complement
form as a labelled variant); 2,000 replicates per cell.

ADDITION 1. Lambda rules none (classical), c_crossfit, d1_pretest, d2_pretest. Intervals CR1 with
t_{G_L-1} (t_{G_L-2} under cross-fitting, as in Q1) and CR2 with Bell-McCaffrey df, each without and
with the finite-population correction in the design arm; textbook_t with and without fpc in the
design arm. No Welch-Satterthwaite rows, no donor bootstraps (memo section 2).

ADDITION 2. Two size arms. `equal`: every donor has m spots. `unequal`: donor g has
m_g = round(m * s_g) spots, s_1..s_24 the 24 CCRCC donors' patch-spot counts divided by their mean,
read from results/round3/D4_expansion/task_defs/CCRCC_hest_layout.json and recorded in the config.
Assignment: the 24 shares are ordered by zlib.crc32 of the donor index string ('0'..'23') and donor
g receives share number g mod 24 of that order (recycled when G > 24). Spots beyond m_g are masked.

ADDITION 3. On theta_3 spot-weighted, superpopulation target, classical and rule c only: the wild
cluster bootstrap-t (Cameron, Gelbach and Miller 2008) on the labelled donors' influence
contributions, 500 draws, Rademacher weights (`wild_t_rad`) and Mammen two-point weights
(`wild_t_mammen`), the unlabelled term held fixed; studentised by the CR1 standard error
recomputed on each bootstrap sample (within-half centring under cross-fitting).

OUTPUT per unit: q1b_sim__GL<G_L>.csv with the Q1 columns plus `size_arm`, and summary and config
JSON beside it.
"""
import argparse
import hashlib
import json
import os
import sys
import time
import zlib

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round4_ppi_estimator as E  # noqa: E402
import round4_ppi_q1_sim as Q1  # noqa: E402

GRID = dict(G_U=(20,), m=(200, 1000), rho=(0.1, 0.3, 0.5), r=(0.0, 0.5, 0.8))
G_DESIGN = 24
RULES = ("none", "c_crossfit", "d1_pretest", "d2_pretest")
WILD_RULES = ("none", "c_crossfit")
N_WILD = 500
ESTS, POPS = Q1.ESTS, Q1.POPS
MU, BETA, S_C = Q1.MU, Q1.BETA, Q1.S_C
CCRCC_TASK = "results/round3/D4_expansion/task_defs/CCRCC_hest_layout.json"


# ============================================================== donor sizes
def ccrcc_shares(repo_root):
    t = json.load(open(os.path.join(repo_root, CCRCC_TASK)))
    tot = {}
    for s in t["samples"]:
        if s.get("excluded_from_donor_units"):
            continue
        tot[s["donor_id"]] = tot.get(s["donor_id"], 0) + int(s["n_patch_spots"])
    v = np.array(list(tot.values()), dtype=float)
    assert len(v) == 24, len(v)
    return dict(zip(tot.keys(), (v / v.mean()).tolist())), v / v.mean()


def share_order():
    return np.argsort([zlib.crc32(str(i).encode()) for i in range(24)], kind="stable")


def donor_sizes(G, m, arm, shares):
    if arm == "equal":
        return np.full(G, m, dtype=int)
    order = share_order()
    s = shares[order[np.arange(G) % 24]]
    return np.maximum(1, np.round(m * s).astype(int))


# ============================================================== data with spot masks
def gen_block(rng, sizes, R, rho):
    """As Q1.gen_block with per-donor spot counts: arrays (R, G, mmax) and a spot mask (G, mmax).
    Draw order and shapes depend only on (G, mmax, R), so the equal arm matches Q1's draws."""
    G, mmax = len(sizes), int(sizes.max())
    mm, y, a0, eps0 = Q1.gen_block(rng, G, mmax, R, rho)
    M = np.arange(mmax)[None, :] < sizes[:, None]
    return mm, y, a0, eps0, M


def donor_stats(z, zf, M):
    Mf = M[None, :, :].astype(float)
    zz, ff = z * Mf, zf * Mf
    n = np.broadcast_to(M.sum(1).astype(float)[:, None], (M.shape[0], z.shape[0])).copy()
    return dict(n=n, Sz=zz.sum(2).T, Sf=ff.sum(2).T, Szz=(zz * z).sum(2).T,
                Sff=(ff * zf).sum(2).T, Szf=(zz * zf).sum(2).T)


def build_stats(mm, y, yh, consts, M):
    Mf = M[None, :, :].astype(float)
    nd = M.sum(1).astype(float)[None, :]
    out = {}
    out[("mean", "spot")] = donor_stats(y, yh, M)
    out[("mean", "donor")] = Q1.donor_value_stats(((y * Mf).sum(2) / nd).T,
                                                  ((yh * Mf).sum(2) / nd).T)
    mu_m, v_m = consts
    w = (mm - mu_m) / v_m
    out[("theta3", "spot")] = donor_stats(w * y, w * yh, M)
    mbar = (mm * Mf).sum(2, keepdims=True) / nd[..., None]
    dm = (mm - mbar) * Mf
    sxx = (dm * dm).sum(2)
    out[("theta3", "donor")] = Q1.donor_value_stats(((dm * y).sum(2) / sxx).T,
                                                    ((dm * yh).sum(2) / sxx).T)
    return out


def n_for_iid(D_don, nspots):
    """Donor-value stats carry n = 1; restore spot counts for the i.i.d. pieces (Q1's
    _n_for_iid with per-donor counts)."""
    m = nspots[:, None]
    D = {"Sz": D_don["Sz"] * m, "Sf": D_don["Sf"] * m,
         "n": np.broadcast_to(m, D_don["n"].shape).astype(float).copy(),
         "Szz": D_don["Szz"] * m * m, "Sff": D_don["Sff"] * m * m, "Szf": D_don["Szf"] * m * m}
    return D


# ============================================================== wild cluster bootstrap-t
def wild_weights(kind, shape, rng):
    if kind == "rad":
        return rng.choice(np.array([-1.0, 1.0]), size=shape)
    s5 = np.sqrt(5.0)
    p = (s5 + 1.0) / (2.0 * s5)
    lo, hi = -(s5 - 1.0) / 2.0, (s5 + 1.0) / 2.0
    return np.where(rng.random(shape) < p, lo, hi)


def wild_t(res, theta, n_wild, seed, alpha):
    """Wild cluster bootstrap-t on the labelled term's per-donor influence contributions q_g
    (res['L']['q'], deviations from the (within-half) centre, summing to theta_L - its centre),
    the U term held fixed. theta* - theta = sum_g w_g q_g; the bootstrap residual contributions
    are w_g q_g recentred by the donor's size share within its stratum; se* is CR1 on them plus
    the fixed U variance. Returns dict kind -> (lo, hi)."""
    L = res["L"]
    q, mask, strata = L["q"], L["mask"], L["strata"]
    G, ncol = q.shape
    vU = E.var_term_cr1(res["U"])
    shares = E._shares(L)
    labels = [None] if strata is None else list(np.unique(strata[strata >= 0]))
    k = E._n_strata(L)
    GL = mask.sum(0).astype(float)
    c1 = GL / np.maximum(GL - k, 1e-300)
    se_hat = np.sqrt(np.maximum(c1 * (q ** 2).sum(0) + vU, 0.0))
    out = {}
    for kind in ("rad", "mammen"):
        rng = E.seed_rng(f"wild|{kind}|{seed}")
        tstar = np.empty((ncol, n_wild))
        for b in range(n_wild):
            w = np.where(mask, wild_weights(kind, (G, ncol), rng), 0.0)
            wq = w * q
            d = wq.sum(0)
            qs = np.zeros_like(q)
            for h in labels:
                s = mask if h is None else (mask & (strata == h))
                qs = np.where(s, wq - shares * np.where(s, wq, 0.0).sum(0)[None, :], qs)
            vstar = c1 * (qs ** 2).sum(0) + vU
            tstar[:, b] = d / np.sqrt(np.where(vstar > 0, vstar, np.nan))
        hi_q = np.nanpercentile(tstar, 100 * (1 - alpha / 2), axis=1)
        lo_q = np.nanpercentile(tstar, 100 * alpha / 2, axis=1)
        out[kind] = (theta - hi_q * se_hat, theta - lo_q * se_hat)
    return out


# ============================================================== one cell
def run_cell(stats, masks, truth, G_pop, design, seed, nspots, do_wild):
    Lm, Um = masks
    out = {}
    for (est, pop), D0 in stats.items():
        D = n_for_iid(D0, nspots) if pop == "donor" else D0
        tr = np.broadcast_to(truth[(est, pop)], (Lm.shape[1],))
        for rule in RULES:
            sd = f"{seed}|{est}|{pop}|{rule}"
            lam, res, iv = E.all_intervals(pop, D, Lm, Um, rule, tr, G_pop=G_pop, seed=sd,
                                           do_boot=False, with_ws=False)
            iv = {k: v for k, v in iv.items() if k.split("|")[0] in ("CR1_t", "CR2_bm")}
            if (do_wild and not design and est == "theta3" and pop == "spot"
                    and rule in WILD_RULES):
                wb = wild_t(res, res["theta"], N_WILD, sd, E.ALPHA)
                for kind, (lo, hi) in wb.items():
                    iv[f"wild_t_{kind}"] = dict(lo=lo, hi=hi, df=np.full(lo.shape, np.nan),
                                                var=iv["CR1_t"]["var"])
            runs = [("complement", lam, res["theta"], iv)]
            if design:
                lam_t, tb, iv_t = E.textbook_intervals(pop, D, Lm, Um, rule, seed=sd,
                                                       do_boot=False)
                runs.append(("textbook", lam_t, tb["theta"], iv_t))
            for form, lm, th, ivs in runs:
                for name, v in ivs.items():
                    base, _, f = name.partition("|")
                    out[(est, pop, form, rule, base, f == "fpc")] = dict(
                        cov=(v["lo"] <= tr) & (tr <= v["hi"]), width=v["hi"] - v["lo"],
                        lam=lm["lam"], df=v["df"], theta=th, var=v["var"],
                        finite=np.isfinite(v["lo"]) & np.isfinite(v["hi"]), truth=tr)
    return out


def superpop_cells(G_L, R, chunk, t0, log, max_spots, shares, do_wild):
    rows = []
    for arm in ("equal", "unequal"):
        for G_U in GRID["G_U"]:
            G = G_L + G_U
            for m in GRID["m"]:
                sizes = donor_sizes(G, m, arm, shares)
                for rho in GRID["rho"]:
                    accs = {r: {} for r in GRID["r"]}
                    rng = E.seed_rng(f"q1b|super|{arm}|GL{G_L}|GU{G_U}|m{m}|rho{rho}")
                    done, ch = 0, 0
                    while done < R:
                        n = min(chunk, R - done)
                        sub = max(1, int(max_spots // (G * sizes.max())))
                        parts = {r: [] for r in GRID["r"]}
                        for s0 in range(0, n, sub):
                            rr = min(sub, n - s0)
                            mm, y, a0, eps0, M = gen_block(rng, sizes, rr, rho)
                            for r in GRID["r"]:
                                yh = Q1.yhat_at(y, a0, eps0, r, rho)
                                parts[r].append(build_stats(mm, y, yh, (0.0, 1.0), M))
                        Lm = np.zeros((G, n), bool); Lm[:G_L] = True
                        Um = ~Lm
                        truth = {(e, p): (MU if e == "mean" else BETA) for e in ESTS for p in POPS}
                        for r in GRID["r"]:
                            st = {k: {kk: np.concatenate([pp[k][kk] for pp in parts[r]], axis=1)
                                      for kk in E.STAT_KEYS} for k in parts[r][0]}
                            new = run_cell(st, (Lm, Um), truth, G, False,
                                           f"q1b|super|{arm}|GL{G_L}|GU{G_U}|m{m}|rho{rho}|r{r}|ch{ch}",
                                           sizes.astype(float), do_wild)
                            Q1.merge_chunks(accs[r], new)
                        done += n
                        ch += 1
                    for r in GRID["r"]:
                        rows += [dict(x, size_arm=arm) for x in Q1.summarise(
                            accs[r], dict(target="super", G_L=G_L, G_U=G_U, G_pop=G, m=m,
                                          rho=rho, r=r))]
                    log(f"[super] {arm} GL{G_L} m{m} rho{rho} done {time.time()-t0:.0f}s")
    return rows


def design_cells(G_L, R, chunk, t0, log, shares):
    rows = []
    G = G_DESIGN
    for arm in ("equal", "unequal"):
        for m in GRID["m"]:
            sizes = donor_sizes(G, m, arm, shares)
            for rho in GRID["rho"]:
                rng = E.seed_rng(f"q1b|design|pop|{arm}|m{m}|rho{rho}")
                mm, y, a0, eps0, M = gen_block(rng, sizes, 1, rho)
                Mf = M[None].astype(float)
                mu_m = float((mm * Mf).sum() / M.sum())
                v_m = float((((mm - mu_m) ** 2) * Mf).sum() / M.sum())
                for r in GRID["r"]:
                    yh = Q1.yhat_at(y, a0, eps0, r, rho)
                    st1 = build_stats(mm, y, yh, (mu_m, v_m), M)
                    truth = {}
                    for (e, p), D in st1.items():
                        truth[(e, p)] = (float(D["Sz"].sum() / D["n"].sum()) if p == "spot"
                                         else float(D["Sz"].mean()))
                    acc = {}
                    rsel = E.seed_rng(f"q1b|design|draws|{arm}|GL{G_L}|m{m}|rho{rho}|r{r}")
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
                                       f"q1b|design|{arm}|GL{G_L}|m{m}|rho{rho}|r{r}|ch{ch}",
                                       sizes.astype(float), False)
                        Q1.merge_chunks(acc, new)
                        done += n
                        ch += 1
                    rows += [dict(x, size_arm=arm) for x in Q1.summarise(
                        acc, dict(target="design", G_L=G_L, G_U=G - G_L, G_pop=G, m=m,
                                  rho=rho, r=r))]
                log(f"[design] {arm} GL{G_L} m{m} rho{rho} done {time.time()-t0:.0f}s")
    return rows


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--G-L", type=int, required=True)
    p.add_argument("--reps", type=int, default=2000)
    p.add_argument("--chunk", type=int, default=250)
    p.add_argument("--max-spots", type=float, default=4e6)
    p.add_argument("--targets", default="design,super")
    p.add_argument("--rho-grid", default="")
    p.add_argument("--m-grid", default="")
    p.add_argument("--no-wild", action="store_true")
    p.add_argument("--repo-root", default=os.path.dirname(os.path.dirname(HERE)))
    p.add_argument("--out-dir", required=True)
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    if a.rho_grid:
        GRID["rho"] = tuple(float(x) for x in a.rho_grid.split(","))
    if a.m_grid:
        GRID["m"] = tuple(int(x) for x in a.m_grid.split(","))
    share_map, shares = ccrcc_shares(a.repo_root)
    os.makedirs(a.out_dir, exist_ok=True)
    cfg = dict(stage="r4ppi_Q1b_sim", G_L=a.G_L, reps=a.reps, chunk=a.chunk,
               grid={k: list(v) for k, v in GRID.items()}, G_design=G_DESIGN, mu=MU, beta=BETA,
               s_c=S_C, sigma_a2="rho/2", rules=list(RULES), wild_rules=list(WILD_RULES),
               n_wild=N_WILD, pretest_k=E.PRETEST_K, estimands=list(ESTS),
               populations=list(POPS), size_arms=["equal", "unequal"],
               ccrcc_task_def=CCRCC_TASK, ccrcc_shares=share_map,
               share_assignment="donor g gets share order[g mod 24], order = argsort(crc32(str(i)))",
               share_order=share_order().tolist(), alpha=E.ALPHA, targets=a.targets,
               seed_source="zlib.crc32")
    blob = json.dumps(cfg, sort_keys=True)
    chash = hashlib.sha256(blob.encode()).hexdigest()[:16]
    tag = f"GL{a.G_L}"
    with open(f"{a.out_dir}/q1b_sim_config__{tag}.json", "w") as fh:
        fh.write(blob)
    t0 = time.time()
    log = lambda s: print(s, flush=True)  # noqa: E731
    rows, timing = [], {}
    for tgt in a.targets.split(","):
        t1 = time.time()
        if tgt == "design":
            rows += design_cells(a.G_L, a.reps, a.chunk, t0, log, shares)
        else:
            rows += superpop_cells(a.G_L, a.reps, a.chunk, t0, log, a.max_spots, shares,
                                   not a.no_wild)
        timing[tgt] = time.time() - t1
    df = pd.DataFrame(rows)
    summ = dict(config_hash=chash, n_rows=len(df), wall_s=time.time() - t0, timing_s=timing,
                n_cells=int(df.groupby(["target", "size_arm", "G_U", "m", "rho", "r"]).ngroups),
                coverage_min=float(df.coverage.min()), coverage_max=float(df.coverage.max()),
                any_nonfinite=int(df.n_nonfinite.sum()))
    with open(f"{a.out_dir}/q1b_sim_summary__{tag}.json", "w") as fh:
        json.dump(summ, fh, indent=1)
    df.to_csv(f"{a.out_dir}/q1b_sim__{tag}.csv", index=False)
    log(json.dumps(summ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
