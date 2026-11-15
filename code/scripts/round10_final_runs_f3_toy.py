"""Round 10, track final-runs, stage F3, open point 2 of the F2 decision file (plan section 5d.6, item 2).

Regime B's toy shortfall, extended. F1's toy (round10_final_runs_f1_formC_check.py) has one sampled cluster of M0 = 10
units and one cluster of M1 = 6 units labelled in full, with m in {4, 5, 6}. This script keeps F1's population law
(yhat ~ N(1, 0.7), y = 0.8 yhat + Gamma(1.5, 0.4), theta3 weights w ~ N(0, 1) centred within each cluster, the mean with
w = 1) and F1's fully labelled cluster of M1 = 6 units, and varies the sampled clusters' size M0 in
{10, 20, 50, 200, 1000}, the units drawn per sampled cluster m in {4, 5, 6, 10, 20} with m / M0 <= 0.6, and the number
of sampled clusters G_s in {1, 8}. Estimand theta3 (the item's subject) and, as a control whose ratio is 1 by
construction, the mean. Coefficients 'fixed1' and 'classical', as in F1. Every estimate is
round10_final_runs_estimators.regime_b_formC, unchanged.

Design moments. In regime B, theta_hat = mean_g zhat_g and V_hat = sum_g V_g / G^2 (round5_ppi_twolevel.estimate,
`if regime_b:`), and for 'fixed1' and 'classical' zhat_g and V_g depend on cluster g's own labelled units only. So
  - G_s = 1 and C(M0, m) <= 1e6: every subset is enumerated and E(V_hat) / Var(theta_hat) is F1's statistic
    V.mean() / theta.var() over the subsets;
  - G_s = 8 and C(M0, m) <= 1e6: every subset of a sampled cluster is enumerated, and since the clusters are drawn
    independently, E(V_hat) = sum_g mean_s V_g(s) / G^2 and Var(theta_hat) = sum_g var_s zhat_g(s) / G^2 exactly;
  - otherwise 200,000 joint draws (each sampled cluster an independent simple random sample of m units), with the
    ratio's Monte Carlo standard error from 20 batches of 10,000 draws.
To make 200,000 draws affordable, K independent copies of the population are stacked as K * G clusters in one call of
regime_b_formC, and copy k's (zhat_g, V_g) give draw k. The anchor mode checks that this equals one call per draw.

Seeds. Population (M0 = 10, G_s = 1) replays F1's stream (default_rng(20261109), drawn theta3, theta2, mean in F1's
order), so its rows reproduce F1's rows. Other populations: zlib.crc32('r10f3toy|pop|<kind>|M0<M0>|Gs<G_s>'). Draws:
zlib.crc32('r10f3toy|draws|<kind>|M0<M0>|Gs<G_s>|m<m>'), shared by both coefficients.

usage: round10_final_runs_f3_toy.py anchor <out_dir> <f1_ref_csv>
       round10_final_runs_f3_toy.py grid <config.json> <out_dir>
"""
import itertools, json, math, os, sys, time, zlib
from multiprocessing import Pool
import numpy as np, pandas as pd
import round5_ppi_twolevel as TL
import round10_final_runs_estimators as E
import round10_final_runs_f1_formC_check as F1

M1 = 6
F1_SEED = 20261109
ENUM_MAX = 10 ** 6
R_MC = 200000
NBATCH = 20
COEFS = ("fixed1", "classical")
SEEDSTR = "chk"                       # F1's cross-fit seed string; unused by 'fixed1' and 'classical'
M0_GRID = (10, 20, 50, 200, 1000)
M_GRID = (4, 5, 6, 10, 20)
GS_GRID = (1, 8)
KINDS = ("theta3", "mean")
KDIV = (1000, 500, 250, 200, 125, 100, 50, 40, 25, 20, 10, 8, 5, 4, 2, 1)   # divisors of 10,000
COLS = ["kind", "M0", "m", "frac", "Gs", "G", "coef", "method", "n_subsets_per_cluster", "draws", "theta_full", "bias",
        "mcse_bias", "EV", "Var", "V_ratio", "V_ratio_mcse", "V_ratio_cluster_min", "V_ratio_cluster_max", "seconds"]


def crc(tag):
    return zlib.crc32(tag.encode())


def cells():
    """The grid in its fixed order; the first cell is F1's (theta3, G_s 1, M0 10, m 4)."""
    out = []
    for kind in KINDS:
        for Gs in GS_GRID:
            for M0 in M0_GRID:
                for m in M_GRID:
                    if m < M0 and m / M0 <= 0.6:
                        out.append((kind, Gs, M0, m))
    return out


def population_ext(kind, rng, M0, Gs, M1=M1):
    """F1's population law with G_s sampled clusters of M0 units (clusters 0..G_s-1) and one cluster of M1 units labelled
    in full (cluster G_s). For G_s = 1 the draws and arithmetic are F1.population's (checked in the anchor mode)."""
    G = Gs + 1
    M = Gs * M0 + M1
    didx = np.r_[np.repeat(np.arange(Gs), M0), np.full(M1, Gs)].astype(int)
    yhat = rng.normal(1.0, 0.7, (M, 1)); y = 0.8 * yhat + rng.gamma(1.5, 0.4, (M, 1))
    if kind == "theta3":
        w = rng.normal(0, 1, M)
        for g in range(G):
            w[didx == g] -= w[didx == g].mean()
    elif kind == "mean":
        w = np.ones(M)
    else:
        raise ValueError(kind)
    return y, yhat, w, didx


def population(kind, M0, Gs):
    if (M0, Gs) == (10, 1):
        rng = np.random.default_rng(F1_SEED)
        for k in ("theta3", "theta2", "mean"):
            if k == kind:
                return population_ext(kind, rng, M0, Gs)
            F1.population(k, rng)        # advance F1's stream exactly as F1.main does
        raise ValueError(kind)
    return population_ext(kind, np.random.default_rng(crc(f"r10f3toy|pop|{kind}|M0{M0}|Gs{Gs}")), M0, Gs)


class Stack:
    """K copies of one population as K * G clusters, prepared once per K."""

    def __init__(self, pop, kind, M0, Gs):
        self.y, self.yhat, self.w, self.didx = pop
        self.kind, self.M0, self.Gs, self.G = kind, M0, Gs, Gs + 1
        self.n1 = len(self.didx)
        self.T1 = TL.prepare(self.y, self.yhat, self.w, self.didx, self.G, kind)
        self.full = np.flatnonzero(self.didx == Gs)
        self.cache = {}

    def T(self, K):
        if K not in self.cache:
            off = (np.arange(K) * self.G)[:, None]
            d = (self.didx[None, :] + off).ravel()
            self.cache[K] = TL.prepare(np.tile(self.y, (K, 1)), np.tile(self.yhat, (K, 1)), np.tile(self.w, K), d,
                                       K * self.G, self.kind)
        return self.cache[K]

    def run(self, loc, coef):
        """loc (K, G_s, m) local unit indices within each sampled cluster. Returns zhat, V (K, G)."""
        K = loc.shape[0]
        base = (np.arange(K) * self.n1)[:, None, None] + (np.arange(self.Gs) * self.M0)[None, :, None]
        sel = np.concatenate([(loc + base).reshape(K, -1), (np.arange(K) * self.n1)[:, None] + self.full[None, :]], 1)
        o = E.regime_b_formC(self.T(K), sel.ravel(), SEEDSTR, coef)
        return o["zhat"][:, 0].reshape(K, self.G), o["V"][:, 0].reshape(K, self.G)

    def joint(self, zhat, V):
        """theta_hat and V_hat of each copy, as round5_ppi_twolevel.estimate forms them in regime B."""
        return zhat.mean(1), V.sum(1) / self.G ** 2


def pick_K(n1, Gs, M0, cap_units=10 ** 6, cap_keys=4 * 10 ** 6):
    for K in KDIV:
        if K * n1 <= cap_units and K * Gs * M0 <= cap_keys:
            return K
    return 1


def run_cell(kind, Gs, M0, m, R=R_MC, force_mc=False):
    t0 = time.time()
    S = Stack(population(kind, M0, Gs), kind, M0, Gs)
    th_full = float(S.T1["theta_full"][0])
    nsub = math.comb(M0, m)
    rows = []
    base = dict(kind=kind, M0=M0, m=m, frac=m / M0, Gs=Gs, G=Gs + 1, n_subsets_per_cluster=float(nsub),
                theta_full=th_full)
    if nsub <= ENUM_MAX and not force_mc:
        subs = np.array(list(itertools.combinations(range(M0), m)), dtype=int)
        K = pick_K(S.n1, Gs, M0)
        for coef in COEFS:
            Z, V = [], []
            for a in range(0, nsub, K):
                s = subs[a:a + K]
                loc = np.ascontiguousarray(np.broadcast_to(s[:, None, :], (len(s), Gs, m)))
                z, v = S.run(loc, coef)
                Z.append(z); V.append(v)
            Z, V = np.concatenate(Z), np.concatenate(V)
            r = dict(base, coef=coef, method="enumerate", draws=nsub, mcse_bias=np.nan, V_ratio_mcse=np.nan)
            if Gs == 1:
                th, vv = S.joint(Z, V)
                r.update(bias=float(th.mean() - th_full), EV=float(vv.mean()), Var=float(th.var()),
                         V_ratio=float(vv.mean() / th.var()) if th.var() > 0 else np.nan,
                         V_ratio_cluster_min=np.nan, V_ratio_cluster_max=np.nan)
            else:
                ev_g, var_g = V[:, :Gs].mean(0), Z[:, :Gs].var(0)
                EV = float(V.mean(0).sum() / S.G ** 2); Var = float(Z.var(0).sum() / S.G ** 2)
                rg = ev_g / var_g
                r.update(bias=float(Z.mean(0).mean() - th_full), EV=EV, Var=Var, V_ratio=EV / Var if Var > 0 else np.nan,
                         V_ratio_cluster_min=float(rg.min()), V_ratio_cluster_max=float(rg.max()))
            rows.append(r)
    else:
        rng = np.random.default_rng(crc(f"r10f3toy|draws|{kind}|M0{M0}|Gs{Gs}|m{m}"))
        K = pick_K(S.n1, Gs, M0)
        TH = {c: [] for c in COEFS}; VV = {c: [] for c in COEFS}
        for a in range(0, R, K):
            keys = rng.random((K, Gs, M0))
            loc = np.sort(np.argpartition(keys, m - 1, axis=-1)[..., :m], axis=-1)
            for coef in COEFS:
                th, vv = S.joint(*S.run(loc, coef))
                TH[coef].append(th); VV[coef].append(vv)
        for coef in COEFS:
            th, vv = np.concatenate(TH[coef]), np.concatenate(VV[coef])
            bt, bv = th.reshape(NBATCH, -1), vv.reshape(NBATCH, -1)
            br = bv.mean(1) / bt.var(1)
            rows.append(dict(base, coef=coef, method="mc", draws=R, bias=float(th.mean() - th_full),
                             mcse_bias=float(th.std() / np.sqrt(R)), EV=float(vv.mean()), Var=float(th.var()),
                             V_ratio=float(vv.mean() / th.var()), V_ratio_mcse=float(br.std(ddof=1) / np.sqrt(NBATCH)),
                             V_ratio_cluster_min=np.nan, V_ratio_cluster_max=np.nan))
    sec = round(time.time() - t0, 2)
    for r in rows:
        r["seconds"] = sec
    return rows


def _cell(args):
    return run_cell(*args)


def run_grid(cfg, out):
    os.makedirs(out, exist_ok=True)
    sp = os.path.join(out, "toy_summary.json")
    summ = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"), cells=len(cells()))
    json.dump(summ, open(sp, "w"), indent=1)
    t0 = time.time()
    with Pool(int(cfg.get("workers", 4))) as p:
        res = p.map(_cell, cells(), chunksize=1)
    rows = [r for rr in res for r in rr]
    d = pd.DataFrame(rows, columns=COLS)
    # checks: the first row is F1's anchor; the mean's ratio is 1 (exact cells to 1e-12, Monte Carlo cells within 4 MCSE)
    a = d.iloc[0]
    mean_ex = d[(d.kind == "mean") & (d.method == "enumerate")]
    mean_mc = d[(d.kind == "mean") & (d.method == "mc")]
    summ.update(seconds=round(time.time() - t0, 1), rows=len(d),
                first_row=dict(kind=a.kind, M0=int(a.M0), Gs=int(a.Gs), m=int(a.m), coef=a.coef, V_ratio=float(a.V_ratio),
                               V_ratio_repr=repr(float(a.V_ratio))),
                first_row_exact=bool(a.kind == "theta3" and a.M0 == 10 and a.Gs == 1 and a.m == 4 and a.coef == "fixed1"
                                     and float(a.V_ratio) == float(cfg["anchor_V_ratio"])),
                mean_enum_max_abs_dev=float((mean_ex.V_ratio - 1).abs().max()),
                mean_mc_max_abs_z=float(((mean_mc.V_ratio - 1).abs() / mean_mc.V_ratio_mcse).max()),
                finished=time.strftime("%Y-%m-%dT%H:%M:%S"))
    summ["passed"] = bool(summ["first_row_exact"] and summ["mean_enum_max_abs_dev"] < 1e-12 and summ["mean_mc_max_abs_z"] < 4)
    json.dump(summ, open(sp, "w"), indent=1)
    d.to_csv(os.path.join(out, "f3_toy_grid.csv"), index=False)
    print(json.dumps({k: v for k, v in summ.items() if k != "config"}, indent=1))


def run_anchor(out, ref_csv):
    """Anchor and smoke. (a) F1.main unchanged into out/anchor_f1, compared with the committed F1 table. (b) The
    extended population law against F1.population. (c) This script's rows at (G_s 1, M0 10) against F1's rows, the first
    one exactly. (d) The stacked call against one call per draw. (e) Exact moments for G_s = 8 against 200,000 joint
    draws. (f) Timings of the costliest production cells."""
    os.makedirs(out, exist_ok=True)
    sp = os.path.join(out, "toy_anchor.json")
    A = dict(started=time.strftime("%Y-%m-%dT%H:%M:%S"), ref_csv=ref_csv)
    json.dump(A, open(sp, "w"), indent=1)
    # (a)
    t0 = time.time()
    argv = sys.argv; sys.argv = ["round10_final_runs_f1_formC_check.py", os.path.join(out, "anchor_f1")]
    try:
        F1.main()
    finally:
        sys.argv = argv
    new = pd.read_csv(os.path.join(out, "anchor_f1", "f1_formC_check.csv")); ref = pd.read_csv(ref_csv)
    same_shape = new.shape == ref.shape and list(new.columns) == list(ref.columns)
    num = ["m", "subsets", "bias", "V_ratio", "d_vs_round5"]
    eq = same_shape and all(np.array_equal(new[c].to_numpy(float), ref[c].to_numpy(float), equal_nan=True) for c in num) \
        and (new.kind.tolist() == ref.kind.tolist()) and (new.coef.tolist() == ref.coef.tolist())
    A["a_f1_rerun"] = dict(rows=int(len(new)), identical=bool(eq), seconds=round(time.time() - t0, 1))
    # (b)
    r1 = np.random.default_rng(F1_SEED); r2 = np.random.default_rng(F1_SEED); bsame = True
    for k in ("theta3", "theta2", "mean"):
        a = F1.population(k, r1)
        if k == "theta2":
            F1.population(k, r2); continue
        b = population_ext(k, r2, 10, 1)
        bsame &= all(np.array_equal(x, y) for x, y in zip(a[:3], b[:3])) and np.array_equal(a[3], b[3])
    A["b_population_law_identical"] = bool(bsame)
    # (c)
    rows = []
    for kind in KINDS:
        for m in (4, 5, 6):
            rows += run_cell(kind, 1, 10, m)
    c = pd.DataFrame(rows, columns=COLS)
    c.to_csv(os.path.join(out, "toy_anchor_rows.csv"), index=False)
    mm = c.merge(ref, on=["kind", "m", "coef"], suffixes=("", "_f1"))
    first = c[(c.kind == "theta3") & (c.m == 4) & (c.coef == "fixed1")].iloc[0]
    A["c_rows_vs_f1"] = dict(rows=int(len(mm)), max_abs_d_V_ratio=float((mm.V_ratio - mm.V_ratio_f1).abs().max()),
                             max_abs_d_bias=float((mm.bias - mm.bias_f1).abs().max()),
                             n_subsets_equal=bool((mm.draws == mm.subsets).all()),
                             first_row_V_ratio=float(first.V_ratio), first_row_V_ratio_repr=repr(float(first.V_ratio)),
                             first_row_exact=bool(float(first.V_ratio) == 0.7626189557829646))
    json.dump(A, open(sp, "w"), indent=1)
    # (d)
    dmax = 0.0; nchk = 0
    for kind, Gs, M0, m in (("theta3", 8, 50, 5), ("mean", 1, 20, 6), ("theta3", 8, 1000, 20), ("theta3", 1, 200, 4)):
        S = Stack(population(kind, M0, Gs), kind, M0, Gs)
        rng = np.random.default_rng(crc(f"r10f3toy|check_stack|{kind}|M0{M0}|Gs{Gs}|m{m}"))
        loc = np.sort(np.argpartition(rng.random((20, Gs, M0)), m - 1, axis=-1)[..., :m], axis=-1)
        for coef in COEFS:
            th, vv = S.joint(*S.run(loc, coef))
            for k in range(20):
                sel = np.r_[np.concatenate([g * M0 + loc[k, g] for g in range(Gs)]), S.full]
                o = E.regime_b_formC(S.T1, sel, SEEDSTR, coef)
                dmax = max(dmax, abs(o["theta"][0] - th[k]), abs(o["var"][0] - vv[k])); nchk += 1
    A["d_stack_vs_direct"] = dict(draws_checked=nchk, max_abs_diff=float(dmax), passed=bool(dmax < 1e-12))
    json.dump(A, open(sp, "w"), indent=1)
    # (e)
    ex = run_cell("theta3", 8, 20, 4); mc = run_cell("theta3", 8, 20, 4, force_mc=True)
    A["e_exact_vs_mc"] = [dict(coef=a["coef"], exact=a["V_ratio"], mc=b["V_ratio"], mcse=b["V_ratio_mcse"],
                               z=(b["V_ratio"] - a["V_ratio"]) / b["V_ratio_mcse"], seconds_exact=a["seconds"],
                               seconds_mc=b["seconds"]) for a, b in zip(ex, mc)]
    json.dump(A, open(sp, "w"), indent=1)
    # (f)
    tim = []
    for cell in (("theta3", 8, 1000, 20), ("theta3", 8, 50, 4), ("theta3", 1, 20, 10), ("theta3", 1, 1000, 20)):
        rr = run_cell(*cell)
        tim.append(dict(cell="|".join(map(str, cell)), method=rr[0]["method"], seconds=rr[0]["seconds"],
                        V_ratio_fixed1=rr[0]["V_ratio"]))
        json.dump(dict(A, f_timings=tim), open(sp, "w"), indent=1)
    A["f_timings"] = tim
    A["grid_cells"] = len(cells())
    A["passed"] = bool(A["a_f1_rerun"]["identical"] and A["b_population_law_identical"] and A["c_rows_vs_f1"]["first_row_exact"]
                       and A["c_rows_vs_f1"]["max_abs_d_V_ratio"] == 0.0 and A["d_stack_vs_direct"]["passed"]
                       and all(abs(e["z"]) < 4 for e in A["e_exact_vs_mc"]))
    A["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(A, open(sp, "w"), indent=1)
    print(json.dumps(A, indent=1))


def main():
    if sys.argv[1] == "anchor":
        run_anchor(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "grid":
        run_grid(json.load(open(sys.argv[2])), sys.argv[3])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
