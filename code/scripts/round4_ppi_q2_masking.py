#!/usr/bin/env python
"""Round 4, PPI track, Q2: the masking experiment on real data (instruction Q2, plan sections 3
and 13; theory in docs/round4_ppi_theory.md).

INPUT. One per-spot predictions parquet in B1's schema (round3_b1_ppi.write_predictions:
sample_id, barcode, donor_id, joined, m_std, frac_neoplastic, y__<gene>, f__<gene>), written by
round3_b1_ppi.py --predict in the harness's calibration-fraction-zero `donor` mode, so every spot is
predicted by a head fitted on the other donors. The `permuted` arm is built here exactly as B1 builds
it, the resnet50 predictions permuted over all rows of the task under crc32('<vtag>|permute').
Only joined spots enter (B1's rule).

ESTIMANDS, B1's linear forms with label-free design constants from all joined spots
(round3_b1_ppi.design_consts and build_z): theta_3 the slope of log1p(y) on standardised mean
nuclear area, theta_2 the neoplastic-minus-stromal mean difference. Both populations: spot-weighted
(one unit, the task) and donor-weighted (one unit per donor, the donor's own constants).
The donor-weighted population is the primary estimand (memo section 4).

DESIGN (regime A). For each n_L in the grid and each draw, n_L donors are labelled (B1's draw_L with
seed 'q2|<vtag>|nL<n_L>|d<draw>'); within each labelled donor m spots are labelled, drawn uniformly
without replacement (seed 'q2spots|<vtag>|nL<n_L>|m<m>|d<draw>'), or all its spots when m = all or
m is at least the donor's count. Every other donor is unlabelled with all its spots predicted. The
labelled donor's other spots are not used. Within a labelled donor the subsample sums are expanded
to the donor's total, so the labelled donor's z and f totals are Horvitz-Thompson estimates of the
donor totals and the spot-weighted estimand keeps its weights M_g.

ESTIMATORS, memo section 2. Rules none (classical), c_crossfit, d1_pretest, d2_pretest.
  superpopulation  complement form, CR1 with t_{G_L-1} (t_{G_L-2} under cross-fitting), and CR2
                   with Bell-McCaffrey df as the comparison the Q3 report needs.
  design           the textbook difference estimator over the task's G donors with the
                   finite-population correction, extended to two stages when m < all:
                   Var = (1 - n_L/G) s_b^2 / n_L + (1/(G n_L)) sum_L (1 - m/M_g) s_{r,g}^2 / m
                   (donor-weighted; spot-weighted with the (G/N)^2 and M_g^2 factors), t_{n_L-1}.
                   At m = all it is exactly addendum 1's textbook form.
TARGET for coverage: theta_full, the classical estimate with every spot of every donor labelled.

OUTPUT. q2_variance_grid__<vtag>__<arm>.csv, one row per (estimand, population, target, rule,
interval, n_L, m) with the empirical variance over draws (median and mean over genes), the mean
estimated variance, their ratio, coverage of theta_full, the width, the PPI-to-classical empirical
variance ratio, and lambda summaries; q2_cluster_r2__<vtag>__<arm>.csv with the unit-level,
within-cluster and cluster-level R^2 (raw, and corrected by one-way ANOVA for cluster size) of
(z, f-z) per estimand, population and gene, and of (log1p y, f) per gene; and with --fit,
q2_fitted_components__<vtag>__<arm>.csv from the variance surface Var = a/n_L + b/(n_L m) + c.
"""
import argparse
import hashlib
import json
import os
import sys
import time
import types
import importlib
import zlib

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round4_ppi_estimator as E  # noqa: E402

STUBBED = []


class _Stub(types.ModuleType):
    __path__ = []

    def __getattr__(self, k):
        if k.startswith("__"):
            raise AttributeError(k)
        return _Stub(self.__name__ + "." + k)

    def __call__(self, *x, **y):
        return None


def _imp(name):
    """Import round3_b1_ppi for its pure functions (design_consts, build_z, draw_L); modules it
    imports only for its predict mode are stubbed if absent, and the list is recorded."""
    while True:
        try:
            return importlib.import_module(name)
        except ModuleNotFoundError as e:
            miss = e.name.split(".")[0]
            if miss in STUBBED or miss == name:
                raise
            sys.modules[miss] = _Stub(miss)
            STUBBED.append(miss)


B1 = _imp("round3_b1_ppi")

RULES = ("none", "c_crossfit", "d1_pretest", "d2_pretest")
ESTS = ("theta3", "theta2")
POPS = ("donor", "spot")
NL_GRID = (4, 6, 8, 12, 16)
M_GRID = (25, 50, 100, 200, 500, 0)          # 0 = all
N_DRAWS = 200


# ============================================================== data
def load(parquet, arm, vtag):
    d = pd.read_parquet(parquet)
    genes = [c[3:] for c in d.columns if c.startswith("y__")]
    Y = d[[f"y__{g}" for g in genes]].to_numpy(np.float64)
    P = d[[f"f__{g}" for g in genes]].to_numpy(np.float64)
    if arm == "permuted":
        pr = np.random.default_rng(zlib.crc32(f"{vtag}|permute".encode()))
        P = P[pr.permutation(len(d))]
    js = d["joined"].to_numpy(bool)
    d, Y, P = d[js].reset_index(drop=True), Y[js], P[js]
    donors = np.array(sorted(d["donor_id"].unique()), dtype=object)
    didx = np.searchsorted(donors, d["donor_id"].to_numpy(object))
    order = np.argsort(didx, kind="stable")
    bounds = np.searchsorted(didx[order], np.arange(len(donors) + 1))
    by_donor = [order[bounds[g]:bounds[g + 1]] for g in range(len(donors))]
    return dict(genes=genes, Y=Y, P=P, m=d["m_std"].to_numpy(np.float64),
                neo=d["frac_neoplastic"].to_numpy(np.float64), donors=donors, didx=didx,
                by_donor=by_donor)


THETA2_KIND = "neo_minus_stroma"     # 'mean' for ACS (instruction Q2: ACS theta_2 is the mean)


def z_arrays(data, est, pop):
    """Per-spot z and f-z (n, n_gene) with B1's constants; unit validity per donor."""
    G = len(data["donors"])
    if est == "theta2" and THETA2_KIND == "mean":
        return data["Y"].copy(), data["P"].copy(), np.ones(G, bool)
    if pop == "spot":
        uidx, nu = np.zeros(len(data["didx"]), int), 1
    else:
        uidx, nu = data["didx"], G
    c = B1.design_consts(data["m"], data["neo"], uidx, nu)
    z = B1.build_z(est, data["Y"], data["m"], data["neo"], c, uidx)[:, :, 0]
    zf = B1.build_z(est, data["P"], data["m"], data["neo"], c, uidx)[:, :, 0]
    valid = B1.unit_valid(est, c)
    if pop == "spot":
        valid = np.full(G, bool(valid[0]))
    return np.nan_to_num(z), np.nan_to_num(zf), valid


def donor_sums(z, zf, didx, G, sel=None):
    """Per-donor sums (G, n_gene); sel restricts to a spot subset."""
    if sel is not None:
        z, zf, didx = z[sel], zf[sel], didx[sel]
    out = {}
    for k, v in (("Sz", z), ("Sf", zf), ("Szz", z * z), ("Sff", zf * zf), ("Szf", z * zf)):
        a = np.zeros((G, z.shape[1]))
        np.add.at(a, didx, v)
        out[k] = a
    n = np.bincount(didx, minlength=G).astype(float)
    out["n"] = np.broadcast_to(n[:, None], (G, z.shape[1])).copy()
    return out


# ============================================================== R^2 measures
def r2_measures(z, zf, didx, G):
    """Unit-level, within-cluster and cluster-level R^2 of z on zf per gene; the cluster level both
    from raw donor means and corrected by one-way ANOVA (between minus within mean square over n0)."""
    n = np.bincount(didx, minlength=G).astype(float)
    N = n.sum()
    S = donor_sums(z, zf, didx, G)
    mz, mf = S["Sz"] / n[:, None], S["Sf"] / n[:, None]
    gz, gf = z.mean(0), zf.mean(0)
    # unit level
    cz, cf = z - gz, zf - gf
    r_unit = (cz * cf).sum(0) / np.sqrt((cz ** 2).sum(0) * (cf ** 2).sum(0))
    # within
    wz, wf = z - mz[didx], zf - mf[didx]
    Wzz, Wff, Wzf = (wz ** 2).sum(0), (wf ** 2).sum(0), (wz * wf).sum(0)
    r_within = Wzf / np.sqrt(Wzz * Wff)
    # between, raw donor means (equal donor weight)
    bz, bf = mz - mz.mean(0), mf - mf.mean(0)
    r_between_raw = (bz * bf).sum(0) / np.sqrt((bz ** 2).sum(0) * (bf ** 2).sum(0))
    # ANOVA components
    Bzz = (n[:, None] * (mz - gz) ** 2).sum(0)
    Bff = (n[:, None] * (mf - gf) ** 2).sum(0)
    Bzf = (n[:, None] * (mz - gz) * (mf - gf)).sum(0)
    msb = np.stack([Bzz, Bff, Bzf]) / (G - 1)
    msw = np.stack([Wzz, Wff, Wzf]) / (N - G)
    n0 = (N - (n ** 2).sum() / N) / (G - 1)
    su = (msb - msw) / n0
    r2c = np.where((su[0] > 0) & (su[1] > 0), su[2] ** 2 / (su[0] * su[1]), np.nan)
    return dict(R2_unit=r_unit ** 2, R2_within=r_within ** 2, R2_cluster_raw=r_between_raw ** 2,
                R2_cluster_corrected=np.clip(r2c, 0, 1), sigma_u2=su[0], sigma_p2=su[1],
                cov_up=su[2], sigma_e2=msw[0], sigma_d2=msw[1], cov_ed=msw[2], n0=np.full_like(r2c, n0),
                icc_z=su[0] / (su[0] + msw[0]))


# ============================================================== textbook, two-stage
def textbook_two_stage(pop, Dl, Dpop, Lm, Am, lam, M, m_lab, s2w):
    """Design-based difference estimator over all G donors. Dl: labelled donors' expanded sums;
    Dpop: all donors' all-spot f sums; Am the population mask (valid donors); s2w: per labelled donor the within-donor sample variance of
    the rectifier over its labelled spots, (G, ncol); M: donor spot counts (G,); m_lab (G, ncol)."""
    lamL, cU = lam["lamL"], lam["cU"]
    GL = Lm.sum(0).astype(float)
    G = Am.sum(0).astype(float)
    f2 = np.where(Lm, 1.0 - m_lab / M[:, None], 0.0)
    if pop == "spot":
        N = np.where(Am, M[:, None], 0.0).sum(0)
        Ftot = np.where(Am, Dpop["Sf"], 0.0).sum(0)
        R = np.where(Lm, Dl["Sz"] - lamL * Dl["Sf"], 0.0)
        theta = cU * Ftot / N + (G / (N * GL)) * R.sum(0)
        e = np.where(Lm, (G / N)[None, :] * R, 0.0)
        within = np.where(Lm, (G / N)[None, :] ** 2 * M[:, None] ** 2 * f2 * s2w
                          / np.maximum(m_lab, 1), 0.0)
    else:
        t = Dl["Sz"] / np.where(Dl["n"] > 0, Dl["n"], 1.0)
        tf = Dl["Sf"] / np.where(Dl["n"] > 0, Dl["n"], 1.0)
        tfp = Dpop["Sf"] / Dpop["n"]
        R = np.where(Lm, t - lamL * tf, 0.0)
        theta = cU * np.where(Am, tfp, 0.0).sum(0) / G + R.sum(0) / GL
        e = R
        within = np.where(Lm, f2 * s2w / np.maximum(m_lab, 1), 0.0)
    em = np.where(Lm, e, 0.0).sum(0) / GL
    s2 = np.where(Lm, (e - em) ** 2, 0.0).sum(0) / (GL - 1.0)
    var = (1.0 - GL / G) * s2 / GL + within.sum(0) / (G * GL)
    return theta, var, GL - 1.0


# ============================================================== one (n_L, m) cell
def run_cell(data, Z, n_L, m, n_draws, vtag, theta_full, valid, Dpop):
    G = len(data["donors"])
    didx = data["didx"]
    M = np.bincount(didx, minlength=G).astype(float)
    ng = len(data["genes"])
    acc = {}
    for d in range(n_draws):
        Ld = B1.draw_L(list(data["donors"]), n_L, f"q2|{vtag}|nL{n_L}|d{d}")
        Lmask = np.isin(data["donors"], Ld)
        rng = np.random.default_rng(zlib.crc32(f"q2spots|{vtag}|nL{n_L}|m{m}|d{d}".encode()))
        sel = np.zeros(len(didx), bool)
        lab_idx = {}
        for g in np.flatnonzero(Lmask):
            idx = data["by_donor"][g]
            ii = idx if (m == 0 or m >= len(idx)) else np.sort(rng.choice(idx, m, replace=False))
            sel[ii] = True
            lab_idx[g] = ii
        mlab = np.bincount(didx[sel], minlength=G).astype(float)
        for (est, pop), (z, zf) in Z.items():
            ok = valid[(est, pop)]
            Dl = donor_sums(z, zf, didx, G, sel)
            Dp = Dpop[(est, pop)]
            scale = np.where(mlab > 0, M / np.maximum(mlab, 1), 0.0)[:, None]
            Dx = {k: np.where(Lmask[:, None], Dl[k] * scale, Dp[k]) for k in ("Sz", "Sf", "Szz", "Sff", "Szf")}
            Dx["n"] = np.broadcast_to(M[:, None], (G, ng)).copy()
            use = ok
            Lm = np.broadcast_to((Lmask & use)[:, None], (G, ng)).copy()
            Um = np.broadcast_to((~Lmask & use)[:, None], (G, ng)).copy()
            Am = Lm | Um
            Dd = Dx
            tr = theta_full[(est, pop)]
            for rule in RULES:
                sd = f"q2|{vtag}|nL{n_L}|m{m}|d{d}|{est}|{pop}|{rule}"
                lam, res, iv = E.all_intervals(pop, Dd, Lm, Um, rule, tr, seed=sd, do_boot=False,
                                               with_ws=False)
                for name in ("CR1_t", "CR2_bm"):
                    v = iv[name]
                    _acc(acc, (est, pop, "super", rule, name), res["theta"], v["var"], v["lo"], v["hi"],
                         lam["lam"], tr)
                # design target: within-donor rectifier variance over labelled spots
                lamL = lam["lamL"]
                s2w = np.zeros((G, ng))
                for g, ii in lab_idx.items():
                    if len(ii) > 1:
                        s2w[g] = (z[ii] - lamL[g] * zf[ii]).var(0, ddof=1)
                lam_d = lam
                th, var, df = textbook_two_stage(pop, Dx, Dp, Lm, Am, lam_d, M, np.broadcast_to(mlab[:, None], (G, ng)), s2w)
                if lam.get("classical_cols") is not None and lam["classical_cols"].any():
                    lam0 = E.lambda_rule("none", pop, Dd, Lm, Um)
                    s20 = np.zeros((G, ng))
                    for g, ii in lab_idx.items():
                        if len(ii) > 1:
                            s20[g] = z[ii].var(0, ddof=1)
                    th0, var0, _ = textbook_two_stage(pop, Dx, Dp, Lm, Am, lam0, M, np.broadcast_to(mlab[:, None], (G, ng)), s20)
                    cc = lam["classical_cols"]
                    th, var = np.where(cc, th0, th), np.where(cc, var0, var)
                lo, hi = E.t_interval(th, var, df)
                _acc(acc, (est, pop, "design", rule, "textbook_t|fpc"), th, var, lo, hi, lam["lam"], tr)
    return acc


def _acc(acc, key, th, var, lo, hi, lam, tr):
    a = acc.setdefault(key, dict(th=[], var=[], cov=[], w=[], lam=[]))
    a["th"].append(th); a["var"].append(var); a["cov"].append((lo <= tr) & (tr <= hi))
    a["w"].append(hi - lo); a["lam"].append(lam)


def summarise(acc, cell, genes):
    rows = []
    fin = {k: {kk: np.stack(vv) for kk, vv in v.items()} for k, v in acc.items()}
    for (est, pop, tgt, rule, iv), v in fin.items():
        ev = np.nanvar(v["th"], axis=0, ddof=1)
        mv = np.nanmean(v["var"], axis=0)
        cl = fin.get((est, pop, tgt, "none", iv))
        evc = np.nanvar(cl["th"], axis=0, ddof=1) if cl is not None else np.full_like(ev, np.nan)
        wc = np.nanmean(cl["w"], axis=0) if cl is not None else np.full_like(ev, np.nan)
        cov = np.nanmean(v["cov"], axis=0)
        w = np.nanmean(v["w"], axis=0)
        ok = np.isfinite(ev) & (ev > 0)
        rows.append(dict(**cell, estimand=est, population=pop, target=tgt, lambda_rule=rule,
                         interval=iv, n_draws=v["th"].shape[0], n_genes=int(ok.sum()),
                         emp_var_median=float(np.nanmedian(ev[ok])) if ok.any() else np.nan,
                         est_var_over_emp_var_median=float(np.nanmedian(mv[ok] / ev[ok])) if ok.any() else np.nan,
                         coverage_median=float(np.nanmedian(cov[ok])) if ok.any() else np.nan,
                         coverage_mean=float(np.nanmean(cov[ok])) if ok.any() else np.nan,
                         coverage_min=float(np.nanmin(cov[ok])) if ok.any() else np.nan,
                         width_ratio_median=float(np.nanmedian(w[ok] / wc[ok])) if ok.any() else np.nan,
                         emp_var_ratio_median=float(np.nanmedian(ev[ok] / evc[ok])) if ok.any() else np.nan,
                         lambda_median=float(np.nanmedian(v["lam"])),
                         lambda_frac_zero=float(np.mean(v["lam"] == 0.0))))
        # per-gene rows for the fit and the gene axis
        for j, gname in enumerate(genes):
            if not ok[j]:
                continue
            rows[-1].setdefault("_genes", []).append(dict(gene=gname, emp_var=ev[j], est_var=mv[j],
                                                         emp_var_classical=evc[j], coverage=cov[j],
                                                         width=w[j], width_classical=wc[j]))
    return rows


def fit_components(grid_gene, out_path):
    """Per (estimand, population, target, rule, gene): least squares of emp_var on 1/n_L and
    1/(n_L m) (m = all replaced by the donor median count) with an intercept for V_U."""
    rows = []
    for key, g in grid_gene.groupby(["estimand", "population", "target", "lambda_rule", "interval", "gene"]):
        X = np.column_stack([1.0 / g["n_L"], 1.0 / (g["n_L"] * g["m_eff"]), np.ones(len(g))])
        beta, *_ = np.linalg.lstsq(X, g["emp_var"].to_numpy(), rcond=None)
        a, b, c = beta
        r = dict(zip(["estimand", "population", "target", "lambda_rule", "interval", "gene"], key),
                 sigma2_cluster=a, sigma2_unit=b, V_U=c, rho_r=a / (a + b) if a + b > 0 else np.nan)
        for k in (10, 100, 1000):
            r[f"m_star_cd_cs_{k}"] = np.sqrt(k * b / a) if a > 0 and b > 0 else np.nan
        r["m_at_f0.1"] = (1 - r["rho_r"]) / (0.1 * r["rho_r"]) if r["rho_r"] and r["rho_r"] > 0 else np.nan
        rows.append(r)
    pd.DataFrame(rows).to_csv(out_path, index=False)


def fit_main(argv):
    """--fit-from: fit the variance surface on per-gene grid files written by separate n_L jobs."""
    import glob
    p = argparse.ArgumentParser()
    p.add_argument("--fit-from", required=True, help="glob of q2_variance_grid_genes__*.csv.gz files")
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    files = sorted(glob.glob(a.fit_from))
    assert files, a.fit_from
    gg = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    fit_components(gg, a.out)
    print(json.dumps(dict(files=files, n_gene_rows=len(gg), out=a.out)))
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0].startswith("--fit-from"):
        return fit_main(argv)
    p = argparse.ArgumentParser()
    p.add_argument("--parquet", required=True)
    p.add_argument("--vtag", required=True, help="task tag as in B1, e.g. CCRCC or CCRCC_merged")
    p.add_argument("--arm", required=True, help="encoder name, or 'permuted' with the resnet50 parquet")
    p.add_argument("--nl-grid", default=",".join(map(str, NL_GRID)))
    p.add_argument("--m-grid", default=",".join(map(str, M_GRID)), help="0 means all")
    p.add_argument("--draws", type=int, default=N_DRAWS)
    p.add_argument("--max-genes", type=int, default=0, help="0 = all genes")
    p.add_argument("--fit", action="store_true")
    p.add_argument("--theta2-kind", default="neo_minus_stroma", choices=("neo_minus_stroma", "mean"))
    p.add_argument("--out-dir", required=True)
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    global THETA2_KIND
    THETA2_KIND = a.theta2_kind
    os.makedirs(a.out_dir, exist_ok=True)
    t0 = time.time()
    data = load(a.parquet, a.arm, a.vtag)
    if a.max_genes:
        data["genes"] = data["genes"][:a.max_genes]
        data["Y"], data["P"] = data["Y"][:, :a.max_genes], data["P"][:, :a.max_genes]
    G = len(data["donors"])
    nls = [n for n in map(int, a.nl_grid.split(",")) if n <= G - 2]
    ms = list(map(int, a.m_grid.split(",")))
    Z, valid, theta_full, Dpop = {}, {}, {}, {}
    r2rows = []
    for est in ESTS:
        for pop in POPS:
            z, zf, ok = z_arrays(data, est, pop)
            Z[(est, pop)] = (z, zf)
            valid[(est, pop)] = ok
            keep = np.isin(data["didx"], np.flatnonzero(ok))
            S = donor_sums(z, zf, data["didx"], G)
            Dpop[(est, pop)] = S
            if pop == "spot":
                theta_full[(est, pop)] = S["Sz"][ok].sum(0) / S["n"][ok].sum(0)
            else:
                theta_full[(est, pop)] = (S["Sz"] / S["n"])[ok].mean(0)
            rr = r2_measures(z[keep], zf[keep], np.searchsorted(np.flatnonzero(ok), data["didx"][keep]), int(ok.sum()))
            for j, gname in enumerate(data["genes"]):
                r2rows.append(dict(vtag=a.vtag, arm=a.arm, scale="z", estimand=est, population=pop,
                                   gene=gname, G=int(ok.sum()), **{k: float(v[j]) for k, v in rr.items()}))
    yy, ff = data["Y"], data["P"]           # the parquet's y is log1p(count), B1's outcome
    rr = r2_measures(yy, ff, data["didx"], G)
    for j, gname in enumerate(data["genes"]):
        r2rows.append(dict(vtag=a.vtag, arm=a.arm, scale="log1p_y", estimand="", population="", gene=gname,
                           G=G, **{k: float(v[j]) for k, v in rr.items()}))
    tag = f"{a.vtag}__{a.arm}"
    pd.DataFrame(r2rows).to_csv(f"{a.out_dir}/q2_cluster_r2__{tag}.csv", index=False)
    rows, generows = [], []
    medM = float(np.median(np.bincount(data["didx"], minlength=G)))
    for n_L in nls:
        for m in ms:
            acc = run_cell(data, Z, n_L, m, a.draws, a.vtag, theta_full, valid, Dpop)
            cell = dict(vtag=a.vtag, arm=a.arm, G=G, n_L=n_L, m=("all" if m == 0 else m),
                        m_eff=(medM if m == 0 else min(m, medM)))
            for r in summarise(acc, cell, data["genes"]):
                for gr in r.pop("_genes", []):
                    generows.append(dict({k: r[k] for k in ("vtag", "arm", "G", "n_L", "m", "m_eff", "estimand",
                                                           "population", "target", "lambda_rule", "interval")}, **gr))
                rows.append(r)
            print(f"nL{n_L} m{m} {time.time()-t0:.0f}s", flush=True)
    pd.DataFrame(rows).to_csv(f"{a.out_dir}/q2_variance_grid__{tag}.csv", index=False)
    gg = pd.DataFrame(generows)
    gg.to_csv(f"{a.out_dir}/q2_variance_grid_genes__{tag}.csv.gz", index=False)
    if a.fit:
        fit_components(gg, f"{a.out_dir}/q2_fitted_components__{tag}.csv")
    summ = dict(vtag=a.vtag, arm=a.arm, n_rows=len(rows), n_gene_rows=len(gg), wall_s=time.time() - t0,
                n_donors=G, n_genes=len(data["genes"]), stubbed=STUBBED, nl_grid=nls, m_grid=ms,
                draws=a.draws, rules=list(RULES), theta2_kind=THETA2_KIND)
    with open(f"{a.out_dir}/q2_summary__{tag}.json", "w") as fh:
        json.dump(summ, fh, indent=1)
    print(json.dumps(summ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
