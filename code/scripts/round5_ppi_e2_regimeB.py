"""Round 5 PPI, stage E2 part 1: regime B with equal labelled units per cluster, and its controls.

Calls round4_ppi_q3_regimes.regime_b unmodified with m_g = min(m, M_g), m in {2,3,4,5,6,8,10,15,20,25,50,100},
200 draws per m with crc32 seeds under the new tag r5e2B, rules none and c_crossfit, both estimands
(theta3, theta2), both populations (donor, spot) and both targets (design, super), the summaries made
by round4_ppi_q2_masking.summarise unmodified.

Arms. An encoder (hoptimus0, uni_v2, resnet50) or the package predictor on ACS reads the parquet's
predictions; 'permuted' is the round-4 permuted predictor (round4_ppi_q2_masking.load); 'constant' gives
every unit the task-wide mean of the base prediction for that gene, 'donor_constant' its own cluster's
mean, where the base is resnet50 on the tissue tasks and the package predictor on ACS. A constant control
is skipped where it has no within-cluster variance, which is theta2 on ACS (the mean, w = 1). The draws
(which units are labelled) and the cross-fit halves depend only on (vtag, m, draw, estimand, population,
rule), so every arm of a task sees the same labelled units, and the comparisons across arms are paired.

Also written, from the full data and for every arm, estimand, population, gene and m, the pooled
within-cluster shares of docs/round5_ppi_theory.md section 1.2 with the regime-B design weights
omega_g = (1 - m_g/M_g) M_g / ((M_g - 1) m_g): S_zf, S_ff, S_zz (omega-weighted sums of within-cluster
covariance and variances, divisor M_g), the unclipped share S_zf^2/(S_ff S_zz) and the share at the
clipped coefficient. For 'constant' this is the level share L. And Q2.r2_measures on the z scale.

Modes: default runs the grid for one arm. --acceptance runs E2 acceptance checks 1 and 2 instead:
(1) m_g = M_g returns the full-data value exactly; (2) with the round-4 proportional allocation of a
total budget and the round-4 seed strings, this script's own draw loop reproduces a given round-4
regime B table (the E0 anchor, results/round5/ppi/E0_anchors/regimeB/q3_regime_comparison__CCRCC__hoptimus0.csv).
"""
import argparse
import json
import os
import time
import zlib

import numpy as np
import pandas as pd

import round4_ppi_estimator as E
import round4_ppi_q2_masking as Q2
import round4_ppi_q3_regimes as Q3

M_GRID = (2, 3, 4, 5, 6, 8, 10, 15, 20, 25, 50, 100)
RULES = ("none", "c_crossfit")
ACS = ("ACS_STATES", "ACS_CA_PUMA")


def load_arm(parquet, arm, vtag):
    """parquet: the arm's own predictions for an encoder or the package predictor; the resnet50
    parquet (tissue) or the package parquet (ACS) for permuted, constant and donor_constant."""
    data = Q2.load(parquet, "permuted" if arm == "permuted" else "as_is", vtag)
    if arm == "constant":
        data["P"] = np.broadcast_to(data["P"].mean(0, keepdims=True), data["P"].shape).copy()
    elif arm == "donor_constant":
        G = len(data["donors"])
        s = np.zeros((G, data["P"].shape[1])); np.add.at(s, data["didx"], data["P"])
        s /= np.bincount(data["didx"], minlength=G)[:, None]
        data["P"] = s[data["didx"]]
    return data


def skip(vtag, arm, est):
    return vtag in ACS and est == "theta2" and arm in ("constant", "donor_constant")


def prepare(data, vtag, arm):
    G = len(data["donors"])
    Z, valid, theta_full = {}, {}, {}
    for est in Q2.ESTS:
        if skip(vtag, arm, est):
            continue
        for pop in Q2.POPS:
            z, zf, ok = Q2.z_arrays(data, est, pop)
            Z[(est, pop)], valid[(est, pop)] = (z, zf), ok
            S = Q2.donor_sums(z, zf, data["didx"], G)
            theta_full[(est, pop)] = (S["Sz"][ok].sum(0) / S["n"][ok].sum(0) if pop == "spot"
                                      else (S["Sz"] / S["n"])[ok].mean(0))
    return Z, valid, theta_full


def draws(data, Z, valid, theta_full, mg, n_draws, sel_seed, rb_seed, one_draw=False):
    """The draw loop of round4 run_b with the allocation and both seed formats as arguments."""
    didx = data["didx"]
    G = len(data["donors"])
    M = np.bincount(didx, minlength=G).astype(float)
    acc = {}
    for d in range(n_draws):
        rng = np.random.default_rng(zlib.crc32(sel_seed(d).encode()))
        sel = np.zeros(len(didx), bool)
        for g in range(G):
            idx = data["by_donor"][g]
            sel[idx if mg[g] >= len(idx) else rng.choice(idx, int(mg[g]), replace=False)] = True
        for (est, pop), (z, zf) in Z.items():
            tr = theta_full[(est, pop)]
            for rule in Q2.RULES:
                o = Q3.regime_b(z, zf, didx, valid[(est, pop)], M, mg, sel, pop, rule, rb_seed(d, est, pop, rule))
                for tgt in ("design", "super"):
                    th, v, df = o[tgt]
                    lo, hi = E.t_interval(th, v, np.full(th.shape, df))
                    Q2._acc(acc, (est, pop, tgt, rule, "regB_t"), th, v, lo, hi, o["lam"], tr,
                            None, o["lam_raw"], o["lam_raw_se"])
        if one_draw:
            break
    return acc


def shares(data, Z, valid, mg, M, genes, cell):
    didx = data["didx"]
    G = len(M)
    rows = []
    om = (1.0 - mg / M) * M / np.maximum((M - 1.0) * mg, 1e-300)
    n = M
    for (est, pop), (z, zf) in Z.items():
        ok = valid[(est, pop)]
        S = Q2.donor_sums(z, zf, didx, G)
        mz, mf = S["Sz"] / n[:, None], S["Sf"] / n[:, None]
        czf = S["Szf"] / n[:, None] - mz * mf
        cff = S["Sff"] / n[:, None] - mf * mf
        czz = S["Szz"] / n[:, None] - mz * mz
        w = np.where(ok, om, 0.0)[:, None]
        szf, sff, szz = (w * czf).sum(0), (w * cff).sum(0), (w * czz).sum(0)
        with np.errstate(invalid="ignore", divide="ignore"):
            lam = np.where(sff > 0, szf / sff, np.nan)
            un = np.where((sff > 0) & (szz > 0), szf ** 2 / (sff * szz), np.nan)
            lc = np.clip(np.nan_to_num(lam), 0.0, 1.0)
            cl = (2 * lc * szf - lc ** 2 * sff) / szz
        for j, gname in enumerate(genes):
            rows.append(dict(**cell, estimand=est, population=pop, gene=gname, S_zf=szf[j], S_ff=sff[j], S_zz=szz[j],
                             coef_unclipped=lam[j], share_unclipped=un[j], share_clipped=cl[j]))
    return rows


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--parquet", required=True)
    p.add_argument("--vtag", required=True)
    p.add_argument("--arm", required=True)
    p.add_argument("--m-grid", default=",".join(map(str, M_GRID)))
    p.add_argument("--draws", type=int, default=200)
    p.add_argument("--theta2-kind", default="neo_minus_stroma", choices=("neo_minus_stroma", "mean"))
    p.add_argument("--acceptance", default="", help="'m_all' for check 1 only, or the path of a round-4 regime B table (budget 2400) to reproduce as check 2")
    p.add_argument("--out-dir", default=".")
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    Q2.THETA2_KIND = a.theta2_kind
    Q2.RULES = RULES
    os.makedirs(a.out_dir, exist_ok=True)
    t0 = time.time()
    data = load_arm(a.parquet, a.arm, a.vtag)
    G = len(data["donors"])
    M = np.bincount(data["didx"], minlength=G).astype(float)
    Z, valid, theta_full = prepare(data, a.vtag, a.arm)
    tag = f"{a.vtag}__{a.arm}"
    if a.acceptance:
        rows = []
        # check 1: m_g = M_g
        for (est, pop), (z, zf) in Z.items():
            for rule in RULES:
                o = Q3.regime_b(z, zf, data["didx"], valid[(est, pop)], M, M.copy(), np.ones(len(data["didx"]), bool),
                                pop, rule, "r5e2acc")
                rows.append(dict(check="m_all_equals_theta_full", vtag=a.vtag, arm=a.arm, estimand=est, population=pop,
                                 lambda_rule=rule, value=float(np.nanmax(np.abs(o["design"][0] - theta_full[(est, pop)]))),
                                 design_var_max=float(np.nanmax(np.abs(o["design"][1])))))
        if a.acceptance == "m_all":
            pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"e2_acceptance__{tag}.csv"), index=False)
            print(pd.DataFrame(rows).to_string())
            return 0
        # check 2: proportional allocation of B = 2400 with the round-4 seed strings
        B = 2400
        N = M.sum()
        mg = np.minimum(M, np.maximum(1, np.round(B * M / N)))
        acc = draws(data, Z, valid, theta_full, mg, a.draws, lambda d: f"q3B|{a.vtag}|B{B}|d{d}",
                    lambda d, est, pop, rule: f"{a.vtag}|B{B}|d{d}|{est}|{pop}|{rule}")
        new = []
        for r in Q2.summarise(acc, dict(vtag=a.vtag, arm=a.arm, G=G, regime="B", budget=B, cost="unit", n_L=G,
                                        m=float(np.median(mg))), data["genes"]):
            r.pop("_genes", None); new.append(r)
        new = pd.DataFrame(new)
        ref = pd.read_csv(a.acceptance)
        ref = ref[(ref.regime == "B") & (ref.cost == "unit")]
        keys = ["estimand", "population", "target", "lambda_rule", "interval"]
        mrg = ref.merge(new, on=keys, suffixes=("_ref", "_new"))
        for col in ("emp_var_median", "coverage_median", "est_var_over_emp_var_median", "width_ratio_median",
                    "emp_var_ratio_median", "lambda_median"):
            dif = np.nanmax(np.abs(mrg[f"{col}_ref"].astype(float) - mrg[f"{col}_new"].astype(float)))
            rows.append(dict(check=f"reproduce_round4_B2400|{col}", vtag=a.vtag, arm=a.arm, value=float(dif),
                             n_ref=len(ref), n_matched=len(mrg)))
        pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"e2_acceptance__{tag}.csv"), index=False)
        print(pd.DataFrame(rows).to_string())
        return 0
    rr = []
    for (est, pop), (z, zf) in Z.items():
        ok = valid[(est, pop)]
        keep = np.isin(data["didx"], np.flatnonzero(ok))
        meas = Q2.r2_measures(z[keep], zf[keep], np.searchsorted(np.flatnonzero(ok), data["didx"][keep]), int(ok.sum()))
        for j, gname in enumerate(data["genes"]):
            rr.append(dict(vtag=a.vtag, arm=a.arm, estimand=est, population=pop, gene=gname,
                           **{k: float(v[j]) for k, v in meas.items()}))
    pd.DataFrame(rr).to_csv(os.path.join(a.out_dir, f"e2_r2__{tag}.csv"), index=False)
    rows, generows, shrows = [], [], []
    for m in map(int, a.m_grid.split(",")):
        mg = np.minimum(float(m), M)
        cell = dict(vtag=a.vtag, arm=a.arm, G=G, regime="B_equal_m", m=m, m_median=float(np.median(mg)),
                    n_clusters_full=int((mg >= M).sum()))
        shrows += shares(data, Z, valid, mg, M, data["genes"], cell)
        acc = draws(data, Z, valid, theta_full, mg, a.draws, lambda d: f"r5e2B|{a.vtag}|m{m}|d{d}",
                    lambda d, est, pop, rule: f"r5e2B|{a.vtag}|m{m}|d{d}|{est}|{pop}|{rule}")
        for r in Q2.summarise(acc, cell, data["genes"]):
            for gr in r.pop("_genes", []):
                generows.append(dict({k: r[k] for k in ("vtag", "arm", "G", "m", "estimand", "population", "target",
                                                       "lambda_rule", "interval")}, **gr))
            rows.append(r)
        print(f"{tag} m{m} {time.time()-t0:.0f}s", flush=True)
        # write as we go, summaries first
        pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"e2_regimeB_grid__{tag}.csv"), index=False)
    pd.DataFrame(shrows).to_csv(os.path.join(a.out_dir, f"e2_shares__{tag}.csv.gz"), index=False)
    pd.DataFrame(generows).to_csv(os.path.join(a.out_dir, f"e2_regimeB_genes__{tag}.csv.gz"), index=False)
    json.dump(dict(vtag=a.vtag, arm=a.arm, G=G, n_genes=len(data["genes"]), m_grid=a.m_grid, draws=a.draws,
                   wall_s=time.time() - t0, stubbed=Q2.STUBBED, skipped=[e for e in Q2.ESTS if skip(a.vtag, a.arm, e)]),
              open(os.path.join(a.out_dir, f"e2_summary__{tag}.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    main()
