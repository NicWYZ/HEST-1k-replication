#!/usr/bin/env python
"""Round 4, PPI track, Q3: regimes A and B at matched labelling budgets (instruction Q3; plan
sections 3 and 13; theory in docs/round4_ppi_theory.md section 4).

Same input, estimands, populations, rules and design constants as round4_ppi_q2_masking.py,
whose functions are imported.

REGIME A. n_L donors fully labelled up to m_A = B / n_L spots each (Q2's run_cell with m = m_A),
for n_L in {4, 6, 8, 12} and B in {2400, 4800, 9600}.

REGIME B. Every donor of the task has labelled spots; the budget B is spread over donors in
proportion to their spot counts, m_g = max(1, round(B M_g / N)) capped at M_g (the instruction's
"spread over a donor's slides in proportion to spot counts"; a donor's spots are drawn uniformly
without replacement across all its slides, seed 'q3B|<vtag>|B<B>|d<draw>'). Every spot is
predicted. Per donor the difference estimator of its mean is
    ybar_g = lambda fbar_g(all spots) + rbar_g(labelled spots).
lambda: rule none (0); c_crossfit, the pooled within-donor slope of z on f over the labelled spots
of one half of the donors (halves by crc32 seed), clipped to [0, 1] and applied to the other half;
d1_pretest and d2_pretest, the same with a half's lambda set to 0 unless its unclipped value exceeds
k times its OLS standard error (within-donor centred, n - G_h - 1 df).
  design target  donor-weighted Var = G^-2 sum_g (1 - m_g/M_g) s_{r,g}^2 / m_g, spot-weighted with
                 weights M_g / N; t on sum_g (m_g - 1) df. Donors with m_g = 1 contribute no s^2 and
                 are flagged (n_donors_m1).
  superpop       cluster-robust over the G per-donor estimates, CR1 with t_{G-1} (t_{G-2} under
                 cross-fitting, within-half centring); spot-weighted as a ratio with weights M_g.

COST-WEIGHTED. At c_d / c_s = 100, regime A's cost n_L (c_d + c_s m_A) buys regime B a budget
B' = n_L (100 + m_A) - 100 G spots (in spot-cost units), when positive; regime B is rerun at B'.

ACCEPTANCE (instruction Q3). Regime B at m = all equals theta_full exactly (`acc_mall_maxdiff`).
At m_g = 1 every donor's design term is unidentified and the superpopulation variance reduces to the
one-labelled-unit cluster formula (`acc_m1_*`).

OUTPUT q3_regime_comparison__<vtag>__<arm>.csv and q3_acceptance__<vtag>__<arm>.csv.
"""
import argparse
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
import round4_ppi_q2_masking as Q2  # noqa: E402

BUDGETS = (2400, 4800, 9600)
NL_A = (4, 6, 8, 12)
CD_CS = 100.0
RULES = Q2.RULES


def _half_lambda(z, zf, didx, sel, donors_h, k):
    s = sel & np.isin(didx, donors_h)
    if not s.any():
        return np.zeros(z.shape[1]), np.zeros(z.shape[1])
    dd = didx[s]
    G = int(didx.max()) + 1
    n = np.bincount(dd, minlength=G).astype(float)
    mz = np.zeros((G, z.shape[1])); np.add.at(mz, dd, z[s]); mz /= np.maximum(n, 1)[:, None]
    mf = np.zeros((G, z.shape[1])); np.add.at(mf, dd, zf[s]); mf /= np.maximum(n, 1)[:, None]
    wz, wf = z[s] - mz[dd], zf[s] - mf[dd]
    sxx, sxy = (wf ** 2).sum(0), (wf * wz).sum(0)
    raw = np.where(sxx > 0, sxy / np.where(sxx > 0, sxx, 1), np.nan)
    clip = np.clip(np.nan_to_num(raw), 0.0, 1.0)
    if k is None:
        return clip, raw
    Gh = int((n > 0).sum())
    dfree = s.sum() - Gh - 1
    rss = ((wz - raw * wf) ** 2).sum(0)
    se = np.sqrt(np.where((dfree > 0) & (sxx > 0), rss / max(dfree, 1) / np.where(sxx > 0, sxx, 1), np.nan))
    ok = np.isfinite(se) & np.isfinite(raw) & (raw > k * se) & (len(donors_h) >= 3)
    return np.where(ok, clip, 0.0), raw


def regime_b(z, zf, didx, valid, M, mg, sel, pop, rule, seed):
    """One draw of regime B for one (estimand, population). Returns dict target -> (theta, var, df)."""
    G = len(M)
    ng = z.shape[1]
    vd = np.flatnonzero(valid)
    if rule == "none":
        lamg = np.zeros((G, ng)); strata = None
    else:
        rng = E.seed_rng(f"q3crossfit|{seed}")
        perm = rng.permutation(vd)
        h = len(perm) // 2
        A, Bh = perm[:h], perm[h:]
        k = E.PRETEST_K.get(rule)
        lA, _ = _half_lambda(z, zf, didx, sel, A, k)
        lB, _ = _half_lambda(z, zf, didx, sel, Bh, k)
        lamg = np.zeros((G, ng)); lamg[A] = lB; lamg[Bh] = lA
        strata = np.full(G, -1); strata[A] = 0; strata[Bh] = 1
    nall = np.bincount(didx, minlength=G).astype(float)
    fall = np.zeros((G, ng)); np.add.at(fall, didx, zf); fall /= np.maximum(nall, 1)[:, None]
    r = z - lamg[didx] * zf
    dl = didx[sel]
    rs = np.zeros((G, ng)); np.add.at(rs, dl, r[sel])
    rq = np.zeros((G, ng)); np.add.at(rq, dl, r[sel] ** 2)
    mm = mg.astype(float)
    rbar = rs / np.maximum(mm, 1)[:, None]
    s2 = np.where((mm > 1)[:, None], (rq - mm[:, None] * rbar ** 2) / np.maximum(mm - 1, 1)[:, None], 0.0)
    yb = lamg * fall + rbar
    vm = valid.astype(bool)
    f2 = (1.0 - mm / M)[:, None]
    if pop == "donor":
        w = np.where(vm, 1.0, 0.0) / vm.sum()
    else:
        w = np.where(vm, M, 0.0) / M[vm].sum()
    theta = (w[:, None] * yb).sum(0)
    v_design = ((w ** 2)[:, None] * f2 * s2 / np.maximum(mm, 1)[:, None]).sum(0)
    df_design = float(np.maximum(mm[vm] - 1, 0).sum())
    # superpopulation: CR1 over donors on the weighted contributions, within-half centring
    Gv = float(vm.sum())
    contrib = np.where(vm[:, None], w[:, None] * Gv * yb, 0.0)       # mean of these = theta
    if strata is None:
        cen = (contrib[vm].mean(0))[None, :]
        q = np.where(vm[:, None], contrib - cen, 0.0)
        kst = 1
    else:
        q = np.zeros_like(contrib)
        for hh in (0, 1):
            ss = vm & (strata == hh)
            q[ss] = contrib[ss] - contrib[ss].mean(0)
        kst = 2
    v_super = Gv / (Gv - kst) * (q ** 2).sum(0) / Gv ** 2
    return dict(design=(theta, v_design, df_design), super=(theta, v_super, Gv - kst),
                lam=np.nanmedian(lamg[vm], axis=0), n_m1=int((mm[vm] == 1).sum()))


def run_b(data, Z, valid, theta_full, B, n_draws, vtag, budget_label):
    G = len(data["donors"])
    didx = data["didx"]
    M = np.bincount(didx, minlength=G).astype(float)
    N = M.sum()
    mg = np.minimum(M, np.maximum(1, np.round(B * M / N))) if B > 0 else M.copy()
    acc = {}
    for d in range(n_draws):
        rng = np.random.default_rng(zlib.crc32(f"q3B|{vtag}|B{budget_label}|d{d}".encode()))
        sel = np.zeros(len(didx), bool)
        for g in range(G):
            idx = data["by_donor"][g]
            sel[idx if mg[g] >= len(idx) else rng.choice(idx, int(mg[g]), replace=False)] = True
        for (est, pop), (z, zf) in Z.items():
            tr = theta_full[(est, pop)]
            for rule in RULES:
                o = regime_b(z, zf, didx, valid[(est, pop)], M, mg, sel, pop, rule,
                             f"{vtag}|B{budget_label}|d{d}|{est}|{pop}|{rule}")
                for tgt in ("design", "super"):
                    th, v, df = o[tgt]
                    lo, hi = E.t_interval(th, v, np.full(th.shape, df))
                    Q2._acc(acc, (est, pop, tgt, rule, "regB_t"), th, v, lo, hi, o["lam"], tr)
        if B == 0:
            break
    return acc, mg


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--parquet", required=True)
    p.add_argument("--vtag", required=True)
    p.add_argument("--arm", required=True)
    p.add_argument("--budgets", default=",".join(map(str, BUDGETS)))
    p.add_argument("--nl-grid", default=",".join(map(str, NL_A)))
    p.add_argument("--draws", type=int, default=Q2.N_DRAWS)
    p.add_argument("--max-genes", type=int, default=0)
    p.add_argument("--theta2-kind", default="neo_minus_stroma", choices=("neo_minus_stroma", "mean"))
    p.add_argument("--out-dir", required=True)
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    Q2.THETA2_KIND = a.theta2_kind
    os.makedirs(a.out_dir, exist_ok=True)
    t0 = time.time()
    data = Q2.load(a.parquet, a.arm, a.vtag)
    if a.max_genes:
        data["genes"] = data["genes"][:a.max_genes]
        data["Y"], data["P"] = data["Y"][:, :a.max_genes], data["P"][:, :a.max_genes]
    G = len(data["donors"])
    Z, valid, theta_full, Dpop = {}, {}, {}, {}
    for est in Q2.ESTS:
        for pop in Q2.POPS:
            z, zf, ok = Q2.z_arrays(data, est, pop)
            Z[(est, pop)], valid[(est, pop)] = (z, zf), ok
            S = Q2.donor_sums(z, zf, data["didx"], G)
            Dpop[(est, pop)] = S
            theta_full[(est, pop)] = (S["Sz"][ok].sum(0) / S["n"][ok].sum(0) if pop == "spot"
                                      else (S["Sz"] / S["n"])[ok].mean(0))
    rows, accrows = [], []
    nls = [n for n in map(int, a.nl_grid.split(",")) if n <= G - 2]
    for B in map(int, a.budgets.split(",")):
        for n_L in nls:
            mA = int(B // n_L)
            acc = Q2.run_cell(data, Z, n_L, mA, a.draws, a.vtag, theta_full, valid, Dpop)
            for r in Q2.summarise(acc, dict(vtag=a.vtag, arm=a.arm, G=G, regime="A", budget=B,
                                            cost="unit", n_L=n_L, m=mA), data["genes"]):
                r.pop("_genes", None); rows.append(r)
            Bc = int(round(n_L * (CD_CS + mA) - CD_CS * G))
            if Bc > 0:
                acc, mg = run_b(data, Z, valid, theta_full, Bc, a.draws, a.vtag, f"cost{B}_{n_L}")
                for r in Q2.summarise(acc, dict(vtag=a.vtag, arm=a.arm, G=G, regime="B", budget=Bc,
                                                cost=f"cd_cs_{CD_CS:g}_vs_A_nL{n_L}_B{B}", n_L=G,
                                                m=float(np.median(mg))), data["genes"]):
                    r.pop("_genes", None); rows.append(r)
            print(f"A B{B} nL{n_L} {time.time()-t0:.0f}s", flush=True)
        acc, mg = run_b(data, Z, valid, theta_full, B, a.draws, a.vtag, str(B))
        for r in Q2.summarise(acc, dict(vtag=a.vtag, arm=a.arm, G=G, regime="B", budget=B, cost="unit",
                                        n_L=G, m=float(np.median(mg))), data["genes"]):
            r.pop("_genes", None); rows.append(r)
        print(f"B B{B} {time.time()-t0:.0f}s", flush=True)
    # acceptance: m = all, and m = 1
    didx = data["didx"]
    M = np.bincount(didx, minlength=G).astype(float)
    for (est, pop), (z, zf) in Z.items():
        for rule in RULES:
            o = regime_b(z, zf, didx, valid[(est, pop)], M, M.copy(), np.ones(len(didx), bool), pop, rule, "acc")
            accrows.append(dict(vtag=a.vtag, arm=a.arm, estimand=est, population=pop, lambda_rule=rule,
                                check="m_all_equals_theta_full",
                                value=float(np.nanmax(np.abs(o["design"][0] - theta_full[(est, pop)])))))
            rng = np.random.default_rng(zlib.crc32(f"q3acc1|{a.vtag}".encode()))
            sel = np.zeros(len(didx), bool)
            for g in range(G):
                sel[rng.choice(data["by_donor"][g])] = True
            o1 = regime_b(z, zf, didx, valid[(est, pop)], M, np.ones(G), sel, pop, rule, "acc1")
            # one-labelled-unit formula: classical CR1 over donors of w_g G (lam fbar_g + r_g1)
            vm = valid[(est, pop)].astype(bool)
            accrows.append(dict(vtag=a.vtag, arm=a.arm, estimand=est, population=pop, lambda_rule=rule,
                                check="m1_design_var_zero_and_n_m1", value=float(np.nanmax(np.abs(o1["design"][1]))),
                                n_m1=o1["n_m1"], n_valid=int(vm.sum())))
    tag = f"{a.vtag}__{a.arm}"
    pd.DataFrame(rows).to_csv(f"{a.out_dir}/q3_regime_comparison__{tag}.csv", index=False)
    pd.DataFrame(accrows).to_csv(f"{a.out_dir}/q3_acceptance__{tag}.csv", index=False)
    summ = dict(vtag=a.vtag, arm=a.arm, n_rows=len(rows), wall_s=time.time() - t0, budgets=a.budgets,
                nl=nls, draws=a.draws, stubbed=Q2.STUBBED)
    json.dump(summ, open(f"{a.out_dir}/q3_summary__{tag}.json", "w"), indent=1)
    print(json.dumps(summ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
