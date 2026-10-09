"""Round 5 PPI, interval 2, stage E3 on the real tasks: the two-level estimator in forms P and C.

Brief section 6, E3, with section 5 of the E2 decision memo; theory section 2; estimator core
round5_ppi_twolevel.py. One task and arm per call, one or more parts:

  regcomp   the regime comparison rerun. Regime A: n_L in {4, 6, 8, 12}, budgets B in {2400,
            4800, 9600}, m_A = B / n_L. Regime B: every valid donor, m_g = max(1, round(B' M_g / N))
            capped at M_g (round 4's allocation) at B' = B (cost 'unit') and at the cost-matched
            B' = n_L (c + m_A) - c G for c in {10, 100, 1000} when positive.
  masking   n_L in {4, 6, 8, 12, 16}, m in {25, 50, 100, 200, 500, all}.
  regb      regime B at small m: equal m_g = min(m, M_g), m in {2, 3, 4, 5, 6, 8, 10, 15, 20, 25,
            50, 100} (E2's grid); theta2 rows only for m >= 4.
  unitw     the spot-weighted estimands with every unit labelled, n_L in {4, 6, 8, 12, 16}: the
            GREG estimator of theory 2.5 with (A_g, F_g), its classical version (lambda = 0) and,
            for the mean, the ratio estimator.
  components  from the full data, per estimand, form and gene: the between variance A, the mean
            within variance B on each form's scale, R^2_c and R^2_w, m* and m*_PP at cost ratios
            10, 100 and 1000 (theory 2.4).
  accept    E3 acceptance checks 1 and 2 against round 4's own draws and seeds (regime A at B =
            2400 and every unit labelled, regime B at B = 2400).

Six estimators on every draw (round5_ppi_twolevel.ESTIMATORS), donor-weighted, design target,
estimands theta3 and theta2 (the mean on ACS, --theta2-kind mean). Every theta2 row with m < all
uses the draw stratified by group (memo section 5, E3 item 1); theta3 and the mean use simple random
sampling inside the donor. Regime-A intervals are computed with and without the E3a cross-fitting
correction (interval names textbook_t|fpc|lin|xf and textbook_t|fpc|lin); regime B uses regB_t.

Seeds (new tag r5e3): labelled donors 'r5e3|<vtag>|<cell>|d<draw>' with round3 draw_L; units
'r5e3u|<vtag>|<cell>|d<draw>|<est>'; cross-fit 'r5e3x|<vtag>|<cell>|d<draw>|<est>'. A draw does not
depend on the arm or the estimator, so all arms and estimators of a cell are paired.

Arms (as E2): an encoder or the package predictor; 'permuted' (round 4); 'constant' (the task-wide
mean of the base prediction per gene) and 'donor_constant' (the donor's own mean), base resnet50 on
tissue and the package predictor on ACS; constant arms skip the ACS mean.

Outputs per part: e3_<part>__<vtag>__<arm>.csv (round4 summarise columns plus part keys) and
e3_<part>_genes__<vtag>__<arm>.csv.gz; components: e3_components__<vtag>__<arm>.csv; accept:
e3_accept__<vtag>__<arm>.csv and e3_accept_identity__<vtag>__<arm>.csv.
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
import round5_ppi_twolevel as TL
from round5_ppi_e2_regimeB import load_arm, ACS

NSTAT = 100.0
REGA_NL, BUDGETS, COSTS = (4, 6, 8, 12), (2400, 4800, 9600), (10.0, 100.0, 1000.0)
MASK_NL, MASK_M = (4, 6, 8, 12, 16), (25, 50, 100, 200, 500, 0)
REGB_M = (2, 3, 4, 5, 6, 8, 10, 15, 20, 25, 50, 100)
UNITW_NL = (4, 6, 8, 12, 16)


def rng_of(s):
    return np.random.default_rng(zlib.crc32(s.encode()))


# ------------------------------------------------------------------ data
def build(data, vtag, arm, srs_theta2=False):
    """Per estimand: TL.prepare arrays (donor-weighted). Skips the constant arms on the ACS mean."""
    G = len(data["donors"])
    out = {}
    for est in Q2.ESTS:
        if vtag in ACS and est == "theta2" and arm in ("constant", "donor_constant"):
            continue
        if est == "theta2" and Q2.THETA2_KIND == "mean":
            kind, w, grp, ok = "mean", np.ones(len(data["didx"])), None, np.ones(G, bool)
        else:
            c = Q2.B1.design_consts(data["m"], data["neo"], data["didx"], G)
            w = Q2.B1.build_z(est, np.ones((len(data["didx"]), 1)), data["m"], data["neo"], c, data["didx"])[:, 0, 0]
            ok = Q2.B1.unit_valid(est, c)
            w = np.nan_to_num(w)
            kind = est
            grp = None
            if est == "theta2" and not srs_theta2:
                grp = np.where(data["neo"] > Q2.B1.NEO_HI, 0, np.where(data["neo"] < Q2.B1.STR_LO, 1, -1))
        out[est] = TL.prepare(data["Y"], data["P"], w, data["didx"], G, kind, grp, ok)
    return out


def units(data, T, Lmask, m, rng):
    """Labelled unit indices: every unit (m = 0), SRS of min(m, M_g) (theta3, mean) or the stratified
    draw of the memo (theta2). m may be an array (G,) of per-donor sizes."""
    G = T["G"]
    mm = np.broadcast_to(np.asarray(m), (G,))
    sel = []
    for g in np.flatnonzero(Lmask & T["valid"]):
        idx = data["by_donor"][g]
        k = int(mm[g])
        if k == 0 or (T["kind"] != "theta2" and k >= len(idx)):
            sel.append(idx); continue
        if T["kind"] != "theta2":
            sel.append(np.sort(rng.choice(idx, k, replace=False))); continue
        gr = T["group"][idx]
        parts = [idx[gr == 0], idx[gr == 1]]
        sz = [len(p) for p in parts]
        if k >= sz[0] + sz[1]:
            sel += parts; continue
        rare = int(np.argmin(sz))
        want = [k // 2, k // 2]; want[rare] = k - k // 2
        take = [min(want[h], sz[h]) for h in (0, 1)]
        short = k - sum(take)
        oth = 1 - rare
        if take[rare] < want[rare]:
            take[oth] = min(sz[oth], take[oth] + short)
        for h in (0, 1):
            sel.append(np.sort(rng.choice(parts[h], take[h], replace=False)) if take[h] < sz[h] else parts[h])
    return np.concatenate(sel) if sel else np.zeros(0, int)


def r4_lambda_A(T, Lmask, sel, seed):
    """Round 4's design coefficient: lambda_rule c_crossfit_design on the donors' HT means."""
    G, ng = T["G"], T["ng"]
    t, tf = TL.ht_means(T, sel)
    t = np.where(Lmask[:, None], t, T["zbar"]); tf = np.where(Lmask[:, None], tf, T["fbar"])
    D = dict(n=np.full((G, ng), NSTAT), Sz=t * NSTAT, Sf=tf * NSTAT)
    D["Szz"], D["Sff"], D["Szf"] = D["Sz"] ** 2 / NSTAT, D["Sf"] ** 2 / NSTAT, D["Sz"] * D["Sf"] / NSTAT
    Lc = Lmask & T["valid"]
    Lm = np.broadcast_to(Lc[:, None], (G, ng)).copy()
    Um = np.broadcast_to((~Lc & T["valid"])[:, None], (G, ng)).copy()
    return E.lambda_rule("c_crossfit_design", "donor", D, Lm, Um, seed=seed)


def r4_lambda_B(T, sel, seed):
    """Round 4's regime B coefficient: pooled within-donor slope of z on f over the labelled units of
    the other half, clipped (round4_ppi_q3_regimes._half_lambda), halves from TL's cross-fit halves."""
    G, ng = T["G"], T["ng"]
    Lm = np.broadcast_to(T["valid"][:, None], (G, ng)).copy()
    half = E._crossfit_halves(Lm, seed)
    s = np.zeros(len(T["didx"]), bool); s[sel] = True
    lam = np.zeros((G, ng))
    for j in range(ng):
        A, B = np.flatnonzero(half[:, j] == 0), np.flatnonzero(half[:, j] == 1)
        lA, _, _ = Q3._half_lambda(T["z"][:, j:j + 1], T["f"][:, j:j + 1], T["didx"], s, A, None)
        lB, _, _ = Q3._half_lambda(T["z"][:, j:j + 1], T["f"][:, j:j + 1], T["didx"], s, B, None)
        lam[A, j], lam[B, j] = lB[0], lA[0]
    return lam


def run_draw(acc, T, est, Lmask, sel, seed, regime_b, key_base):
    tr = T["theta_full"]
    lam_r4 = r4_lambda_B(T, sel, seed) if regime_b else r4_lambda_A(T, Lmask, sel, seed)
    th = {}
    for name in TL.ESTIMATORS:
        o = TL.estimate(T, Lmask, sel, name, seed, regime_b=regime_b, xf=True, lam_r4=lam_r4)
        th[name] = (o["theta"], o["var"])
        ivs = (("regB_t", o["var"]),) if regime_b else (("textbook_t|fpc|lin", o["var_noxf"]),
                                                       ("textbook_t|fpc|lin|xf", o["var"]))
        df = np.full(o["theta"].shape, o["df"])
        lw = o["lam_w"][Lmask & T["valid"]]
        lmed = np.nanmedian(lw, axis=0) if lw.size else np.zeros(T["ng"])
        for iv, v in ivs:
            lo, hi = E.t_interval(o["theta"], v, df)
            Q2._acc(acc, key_base + (name, iv), o["theta"], v, lo, hi, lmed, tr)
    # E3 acceptance check 3 (meaningful for the constant arms): form C with the predictor equals
    # form C classical; returned for every arm, the merge reads it for constant and donor_constant
    return (float(np.nanmax(np.abs(th["C_ppi"][0] - th["C_classical"][0]))),
            float(np.nanmax(np.abs(th["C_ppi"][1] - th["C_classical"][1]))))


def summarise(acc, cell, genes, rows, generows):
    for r in Q2.summarise(acc, cell, genes):
        for gr in r.pop("_genes", []):
            generows.append(dict({k: r[k] for k in cell}, estimand=r["estimand"], estimator=r["lambda_rule"],
                                 interval=r["interval"], **gr))
        r["estimator"] = r.pop("lambda_rule")
        rows.append(r)


# ------------------------------------------------------------------ parts
def part_cells(part, data, Tset):
    G = len(data["donors"])
    M = np.bincount(data["didx"], minlength=G).astype(float)
    N = M.sum()
    cells = []
    if part == "regcomp":
        for B in BUDGETS:
            for nL in REGA_NL:
                if nL <= G - 2:
                    cells.append(dict(regime="A", budget=B, cost="unit", n_L=nL, m=B // nL))
            cells.append(dict(regime="B", budget=B, cost="unit", n_L=G, m="prop"))
            for c in COSTS:
                for nL in REGA_NL:
                    if nL > G - 2:
                        continue
                    Bp = nL * (c + B / nL) - c * G
                    if Bp > 0:
                        cells.append(dict(regime="B", budget=float(Bp), cost=f"cd_cs_{c:g}_vs_A_nL{nL}_B{B}",
                                          n_L=G, m="prop"))
    elif part == "masking":
        for nL in MASK_NL:
            if nL <= G - 2:
                for m in MASK_M:
                    cells.append(dict(regime="A", budget=np.nan, cost="unit", n_L=nL, m=m))
    elif part == "regb":
        for m in REGB_M:
            cells.append(dict(regime="B", budget=np.nan, cost="unit", n_L=G, m=m))
    for c in cells:
        if c["m"] == "prop":
            c["mg"] = np.minimum(M, np.maximum(1, np.round(c["budget"] * M / N)))
    return cells


def run_part(part, data, Tset, vtag, arm, draws, out):
    rows, generows, ident = [], [], []
    t0 = time.time()
    for ci, c in enumerate(part_cells(part, data, Tset)):
        acc = {}
        i3 = {}
        tag = f"{part}|{c['regime']}|B{c['budget']}|{c['cost']}|nL{c['n_L']}|m{c['m']}"
        for d in range(draws):
            for est, T in Tset.items():
                rb = c["regime"] == "B"
                if rb:
                    Lmask = T["valid"].copy()
                else:
                    Ld = Q2.B1.draw_L(list(data["donors"]), c["n_L"], f"r5e3|{vtag}|{tag}|d{d}")
                    Lmask = np.isin(data["donors"], Ld)
                m = c["mg"] if c["m"] == "prop" else c["m"]
                if est == "theta2" and T["kind"] == "theta2":
                    if np.isscalar(m) and 0 < m < 4:
                        continue
                    if not np.isscalar(m):
                        m = np.maximum(m, 4)
                sel = units(data, T, Lmask, m, rng_of(f"r5e3u|{vtag}|{tag}|d{d}|{est}"))
                dth, dv = run_draw(acc, T, est, Lmask, sel, f"r5e3x|{vtag}|{tag}|d{d}|{est}", rb,
                                   (est, "donor", "design"))
                k3 = (est,)
                i3[k3] = (max(i3.get(k3, (0, 0))[0], dth), max(i3.get(k3, (0, 0))[1], dv))
        cell = dict(vtag=vtag, arm=arm, G=len(data["donors"]), part=part, regime=c["regime"],
                    budget=c["budget"], cost=c["cost"], n_L=c["n_L"],
                    m=("all" if c["m"] == 0 else c["m"]))
        if c["m"] == "prop":
            cell["m_median"] = float(np.median(c["mg"]))
        summarise(acc, cell, data["genes"], rows, generows)
        for (est,), (dth, dv) in i3.items():
            ident.append(dict(cell, estimand=est, max_abs_theta_Cppi_minus_Ccl=dth, max_abs_var_Cppi_minus_Ccl=dv))
        print(f"{part} cell {ci + 1} {tag} {time.time() - t0:.0f}s", flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(out, f"e3_{part}__{vtag}__{arm}.csv"), index=False)
    pd.DataFrame(generows).to_csv(os.path.join(out, f"e3_{part}_genes__{vtag}__{arm}.csv.gz"), index=False)
    pd.DataFrame(ident).to_csv(os.path.join(out, f"e3_{part}_formC_identity__{vtag}__{arm}.csv"), index=False)
    return len(rows)


# ------------------------------------------------------------------ unit-weighted
def greg_draw(Z, A, F, Lmask, seed, ppi, xf=True):
    """Theory 2.5. Z, F (G, ng) cluster totals; A (G,) weight sums. Returns theta, var (ng,)."""
    G, ng = Z.shape
    Lm = np.broadcast_to(Lmask[:, None], (G, ng)).copy()
    half = E._crossfit_halves(Lm, seed)
    Ab = np.broadcast_to(A[:, None], (G, ng))
    coefs = []
    for h in (0, 1):
        s = half == h
        saa = np.where(s, Ab * Ab, 0).sum(0); saf = np.where(s, Ab * F, 0).sum(0); sff = np.where(s, F * F, 0).sum(0)
        saz = np.where(s, Ab * Z, 0).sum(0); sfz = np.where(s, F * Z, 0).sum(0)
        if ppi:
            det = saa * sff - saf ** 2
            sing = ~(det > 1e-12 * np.maximum(saa * sff, 1e-300))
            with np.errstate(invalid="ignore", divide="ignore"):
                lr = np.where(sing, 0.0, (saa * sfz - saf * saz) / np.where(sing, 1.0, det))
            lam = np.clip(lr, 0.0, 1.0)
        else:
            lam = np.zeros(ng)
        with np.errstate(invalid="ignore", divide="ignore"):
            gam = np.where(saa > 0, (saz - lam * saf) / np.where(saa > 0, saa, 1), 0.0)
        coefs.append((gam, lam))
    (gA, lA), (gB, lB) = coefs
    gL = TL._assign(gA, gB, half); lL = TL._assign(lA, lB, half)
    nL = Lmask.sum()
    gbar = np.where(Lm, gL, 0).sum(0) / nL; lbar = np.where(Lm, lL, 0).sum(0) / nL
    AU, FU = A.sum(), F.sum(0)
    return gL, lL, gbar, lbar, AU, FU, Lm, nL


def unitw_part(data, vtag, arm, draws, out):
    G = len(data["donors"])
    M = np.bincount(data["didx"], minlength=G).astype(float)
    Ntot = M.sum()
    rows, generows = [], []
    for est in Q2.ESTS:
        if vtag in ACS and est == "theta2" and arm in ("constant", "donor_constant"):
            continue
        z, zf, ok = Q2.z_arrays(data, est, "spot")
        if est == "theta2" and Q2.THETA2_KIND == "mean":
            w = np.ones(len(data["didx"]))
        else:
            c = Q2.B1.design_consts(data["m"], data["neo"], np.zeros(len(data["didx"]), int), 1)
            w = np.nan_to_num(Q2.B1.build_z(est, np.ones((len(data["didx"]), 1)), data["m"], data["neo"], c,
                                            np.zeros(len(data["didx"]), int))[:, 0, 0])
        Z = np.zeros((G, z.shape[1])); np.add.at(Z, data["didx"], z)
        F = np.zeros((G, z.shape[1])); np.add.at(F, data["didx"], zf)
        A = np.bincount(data["didx"], weights=w, minlength=G)
        tr = Z.sum(0) / Ntot
        for nL in UNITW_NL:
            if nL > G - 2:
                continue
            acc = {}
            for d in range(draws):
                Ld = Q2.B1.draw_L(list(data["donors"]), nL, f"r5e3|{vtag}|unitw|nL{nL}|d{d}")
                Lmask = np.isin(data["donors"], Ld)
                seed = f"r5e3x|{vtag}|unitw|nL{nL}|d{d}|{est}"
                for name, ppi in (("greg_classical", False), ("greg_ppi", True)):
                    gL, lL, gbar, lbar, AU, FU, Lm, n = greg_draw(Z, A, F, Lmask, seed, ppi)
                    R = np.where(Lm, Z - gL * A[:, None] - lL * F, 0.0)
                    theta = (gbar * AU + lbar * FU + (G / n) * R.sum(0)) / Ntot
                    e = np.where(Lm, (G / Ntot) * (R + ((gL - gbar) * AU + (lL - lbar) * FU) / G), 0.0)
                    em = e.sum(0) / n
                    s2 = np.where(Lm, (e - em) ** 2, 0).sum(0) / (n - 1)
                    var0 = (1 - n / G) * s2 / n
                    # xf: (n/G)(G/N)^2 (1/n) mean_L[(b_g - bbar)' S_x (b_g - bbar)], x = (A, F)
                    Ab = np.broadcast_to(A[:, None], Z.shape)
                    am = np.where(Lm, Ab, 0).sum(0) / n; fm = np.where(Lm, F, 0).sum(0) / n
                    saa = np.where(Lm, (Ab - am) ** 2, 0).sum(0) / (n - 1)
                    sff = np.where(Lm, (F - fm) ** 2, 0).sum(0) / (n - 1)
                    saf = np.where(Lm, (Ab - am) * (F - fm), 0).sum(0) / (n - 1)
                    dg, dl = np.where(Lm, gL - gbar, 0), np.where(Lm, lL - lbar, 0)
                    q = (dg ** 2 * saa + 2 * dg * dl * saf + dl ** 2 * sff).sum(0) / n
                    extra = (n / G) * (G / Ntot) ** 2 * q / n
                    for iv, v in (("textbook_t|fpc|lin", var0), ("textbook_t|fpc|lin|xf", var0 + extra)):
                        lo, hi = E.t_interval(theta, v, np.full(theta.shape, n - 1.0))
                        Q2._acc(acc, (est, "spot", "design", name, iv), theta, v, lo, hi, np.median(lL[Lmask], 0), tr)
                if est == "theta2" and Q2.THETA2_KIND == "mean":
                    R_ = np.where(Lm, Z, 0).sum(0) / np.where(Lm, M[:, None], 0).sum(0)
                    e = np.where(Lm, (G / Ntot) * (Z - R_ * M[:, None]), 0.0)
                    em = e.sum(0) / n
                    v = (1 - n / G) * np.where(Lm, (e - em) ** 2, 0).sum(0) / (n - 1) / n
                    lo, hi = E.t_interval(R_, v, np.full(R_.shape, n - 1.0))
                    Q2._acc(acc, (est, "spot", "design", "ratio", "textbook_t|fpc"), R_, v, lo, hi, np.zeros(Z.shape[1]), tr)
            cell = dict(vtag=vtag, arm=arm, G=G, part="unitw", regime="A", budget=np.nan, cost="unit",
                        n_L=nL, m="all")
            summarise(acc, cell, data["genes"], rows, generows)
    pd.DataFrame(rows).to_csv(os.path.join(out, f"e3_unitw__{vtag}__{arm}.csv"), index=False)
    pd.DataFrame(generows).to_csv(os.path.join(out, f"e3_unitw_genes__{vtag}__{arm}.csv.gz"), index=False)
    return len(rows)


# ------------------------------------------------------------------ components
def components_part(data, Tset, vtag, arm, out):
    rows = []
    for est, T in Tset.items():
        ok = T["valid"]; didx = T["didx"]; G = T["G"]
        zb, fb = T["zbar"][ok], T["fbar"][ok]
        A = zb.var(0, ddof=1)
        zc, fc = zb - zb.mean(0), fb - fb.mean(0)
        lc = np.clip(np.where((fc ** 2).sum(0) > 0, (zc * fc).sum(0) / np.maximum((fc ** 2).sum(0), 1e-300), 0), 0, 1)
        R2c = 1 - ((zc - lc * fc) ** 2).sum(0) / np.maximum((zc ** 2).sum(0), 1e-300)
        inok = ok[didx]
        if T["kind"] == "theta2":
            key = didx * 2 + np.maximum(T["group"], 0)
            inok = inok & (T["group"] >= 0)
        else:
            key = didx.copy()
        K = G * T["H"]

        def within(v):
            v = v[inok]; k = key[inok]
            cnt = np.bincount(k, minlength=K).astype(float)
            s = np.zeros((K, v.shape[1])); np.add.at(s, k, v)
            q = np.zeros((K, v.shape[1])); np.add.at(q, k, v * v)
            var = np.where(cnt[:, None] > 1, (q - s ** 2 / np.maximum(cnt, 1)[:, None]) / np.maximum(cnt - 1, 1)[:, None], 0)
            return var, cnt

        def pooled_slope(x, y):
            x = x[inok]; y = y[inok]; k = key[inok]
            cnt = np.bincount(k, minlength=K).astype(float)[:, None]
            sx = np.zeros((K, x.shape[1])); np.add.at(sx, k, x)
            sy = np.zeros((K, x.shape[1])); np.add.at(sy, k, y)
            xc, yc = x - (sx / np.maximum(cnt, 1))[k], y - (sy / np.maximum(cnt, 1))[k]
            return np.clip(np.where((xc * xc).sum(0) > 0, (xc * yc).sum(0) / np.maximum((xc * xc).sum(0), 1e-300), 0), 0, 1)
        y, yh, w, z, f = T["y"], T["yhat"], T["w"][:, None], T["z"], T["f"]
        forms = {}
        # round 4 and form P scale: within variance of z (r4) and of z - gamma a (P), PPI residual
        lam_zf = pooled_slope(f, z)
        v0, _ = within(z); v1, _ = within(z - lam_zf * f)
        okk = np.repeat(ok, T["H"])
        forms["r4"] = (v0[okk].mean(0), v1[okk].mean(0))
        if T["kind"] == "theta3":
            wc = w - T["abar"][didx][:, None]
            ym = np.zeros((G, y.shape[1])); np.add.at(ym, didx, y); ym /= T["M"][:, None]
            hm = np.zeros((G, y.shape[1])); np.add.at(hm, didx, yh); hm /= T["M"][:, None]
            uy, uh = wc * (y - ym[didx]), wc * (yh - hm[didx])
            lamC = np.clip(np.where((uh * uh)[inok].sum(0) > 0, (uh * uy)[inok].sum(0) / np.maximum((uh * uh)[inok].sum(0), 1e-300), 0), 0, 1)
            k2 = (((T["M"] - 1) / T["M"]) ** 2)[:, None]
            c0, _ = within(uy); c1, _ = within(uy - lamC * uh)
            forms["C"] = ((k2 * c0)[ok].mean(0), (k2 * c1)[ok].mean(0))
        elif T["kind"] == "theta2":
            lamC = pooled_slope(yh, y)
            c0, _ = within(y); c1, _ = within(y - lamC * yh)
            c0 = c0.reshape(G, 2, -1).sum(1) * 2; c1 = c1.reshape(G, 2, -1).sum(1) * 2
            forms["C"] = (c0[ok].mean(0), c1[ok].mean(0))
        else:
            lamC = pooled_slope(yh, y)
            c0, _ = within(y); c1, _ = within(y - lamC * yh)
            forms["C"] = (c0[ok].mean(0), c1[ok].mean(0))
        for form, (B0, B1) in forms.items():
            R2w = 1 - B1 / np.where(B0 > 0, B0, np.nan)
            for j, g in enumerate(data["genes"]):
                r = dict(vtag=vtag, arm=arm, estimand=est, form=form, gene=g, G=int(ok.sum()),
                         A=float(A[j]), B_classical=float(B0[j]), B_ppi=float(B1[j]),
                         R2_c=float(R2c[j]), R2_w=float(R2w[j]))
                for cd in COSTS:
                    ms = np.sqrt(B0[j] / A[j] * cd) if A[j] > 0 else np.nan
                    r[f"mstar_cd{cd:g}"] = ms
                    r[f"mstarPP_cd{cd:g}"] = ms * np.sqrt((1 - R2w[j]) / (1 - R2c[j])) if R2c[j] < 1 else np.nan
                rows.append(r)
    pd.DataFrame(rows).to_csv(os.path.join(out, f"e3_components__{vtag}__{arm}.csv"), index=False)
    return len(rows)


# ------------------------------------------------------------------ acceptance 1 and 2
def accept_part(data, Tset, vtag, arm, draws, out):
    """Round 4's own draws and seeds. Regime A: Q2.run_cell's labelled donors and spots (q2 seeds) at
    B = 2400 (m_A = 2400 / n_L) and at m = all; regime B: run_b's spots at B = 2400 (q3B seeds) and
    regime_b's halves. Per draw, r4_ppi is compared with round 4's own computation; the summaries are
    written for comparison with q4_main_table.csv by the merge."""
    G = len(data["donors"])
    M = np.bincount(data["didx"], minlength=G).astype(float)
    rows, generows, ident = [], [], []
    Tsrs = build(data, vtag, arm, srs_theta2=True)
    for (nL, m) in [(n, 2400 // n) for n in REGA_NL if n <= G - 2] + [(n, 0) for n in REGA_NL if n <= G - 2]:
        acc = {}
        for d in range(draws):
            Ld = Q2.B1.draw_L(list(data["donors"]), nL, f"q2|{vtag}|nL{nL}|d{d}")
            Lmask = np.isin(data["donors"], Ld)
            rng = rng_of(f"q2spots|{vtag}|nL{nL}|m{m}|d{d}")
            selb = np.zeros(len(data["didx"]), bool)
            for g in np.flatnonzero(Lmask):
                idx = data["by_donor"][g]
                ii = idx if (m == 0 or m >= len(idx)) else np.sort(rng.choice(idx, m, replace=False))
                selb[ii] = True
            sel = np.flatnonzero(selb)
            for est, T in Tsrs.items():
                sd = f"q2|{vtag}|nL{nL}|m{m}|d{d}|{est}|donor|c_crossfit_design"
                Lc = Lmask & T["valid"]
                mlab = np.bincount(T["didx"][selb], minlength=G).astype(float)
                Dl = Q2.donor_sums(T["z"], T["f"], T["didx"], G, selb)
                Dp = Q2.donor_sums(T["z"], T["f"], T["didx"], G)
                scale = np.where(mlab > 0, M / np.maximum(mlab, 1), 0.0)[:, None]
                Dx = {k: np.where(Lmask[:, None], Dl[k] * scale, Dp[k]) for k in ("Sz", "Sf", "Szz", "Sff", "Szf")}
                Dx["n"] = np.broadcast_to(M[:, None], (G, T["ng"])).copy()
                Lm = np.broadcast_to(Lc[:, None], (G, T["ng"])).copy()
                Um = np.broadcast_to((~Lmask & T["valid"])[:, None], (G, T["ng"])).copy()
                lam = E.lambda_rule("c_crossfit_design", "donor", Dx, Lm, Um, seed=sd)
                s2w = np.zeros((G, T["ng"]))
                for g in np.flatnonzero(Lc):
                    ii = np.flatnonzero(selb & (T["didx"] == g))
                    if len(ii) > 1:
                        s2w[g] = (T["z"][ii] - lam["lamL"][g] * T["f"][ii]).var(0, ddof=1)
                th, var, df = Q2.textbook_two_stage("donor", Dx, Dp, Lm, Lm | Um, lam, M,
                                                    np.broadcast_to(mlab[:, None], (G, T["ng"])), s2w, lin=True)
                o = TL.estimate(T, Lmask, sel, "r4_ppi", sd, xf=False, lam_r4=lam)
                ident.append(dict(check="1_regimeA_r4_vs_round4_code", estimand=est, n_L=nL, m=m, draw=d,
                                  max_abs_theta=float(np.abs(o["theta"] - th).max()),
                                  max_rel_var=float(np.nanmax(np.abs(o["var"] / var - 1)))))
                names = ("r4_ppi",) if m else ("r4_ppi", "P_ppi", "C_ppi")
                for name in names:
                    oo = o if name == "r4_ppi" else TL.estimate(Tset[est], Lmask, sel, name, sd, xf=False)
                    lo, hi = E.t_interval(oo["theta"], oo["var"], np.full(oo["theta"].shape, oo["df"]))
                    Q2._acc(acc, (est, "donor", "design", name, "textbook_t|fpc|lin"), oo["theta"], oo["var"], lo, hi,
                            np.zeros(T["ng"]), T["theta_full"])
        cell = dict(vtag=vtag, arm=arm, G=G, part="accept", regime="A", budget=(2400 if m else np.nan),
                    cost="unit", n_L=nL, m=("all" if m == 0 else m))
        summarise(acc, cell, data["genes"], rows, generows)
    # regime B at B = 2400 with round 4's seeds
    N = M.sum()
    mg = np.minimum(M, np.maximum(1, np.round(2400 * M / N)))
    acc = {}
    for d in range(draws):
        rng = rng_of(f"q3B|{vtag}|B2400|d{d}")
        selb = np.zeros(len(data["didx"]), bool)
        for g in range(G):
            idx = data["by_donor"][g]
            selb[idx if mg[g] >= len(idx) else rng.choice(idx, int(mg[g]), replace=False)] = True
        sel = np.flatnonzero(selb)
        for est, T in Tsrs.items():
            seed = f"{vtag}|B2400|d{d}|{est}|donor|c_crossfit"
            rb = Q3.regime_b(T["z"], T["f"], T["didx"], T["valid"], M, mg, selb, "donor", "c_crossfit", seed)
            th_b, var_b, df_b = rb["design"]
            vd = np.flatnonzero(T["valid"])
            perm = E.seed_rng(f"q3crossfit|{seed}").permutation(vd)
            h = len(perm) // 2
            lA, _, _ = Q3._half_lambda(T["z"], T["f"], T["didx"], selb, perm[:h], None)
            lB, _, _ = Q3._half_lambda(T["z"], T["f"], T["didx"], selb, perm[h:], None)
            lamg = np.zeros((G, T["ng"])); lamg[perm[:h]] = lB; lamg[perm[h:]] = lA
            o = TL.estimate(T, T["valid"].copy(), sel, "r4_ppi", seed, regime_b=True, lam_r4=lamg)
            ident.append(dict(check="1_regimeB_r4_vs_round4_code", estimand=est, n_L=G, m="prop", draw=d,
                              max_abs_theta=float(np.abs(o["theta"] - th_b).max()),
                              max_rel_var=float(np.nanmax(np.abs(o["var"] / var_b - 1)))))
            lo, hi = E.t_interval(o["theta"], o["var"], np.full(o["theta"].shape, o["df"]))
            Q2._acc(acc, (est, "donor", "design", "r4_ppi", "regB_t"), o["theta"], o["var"], lo, hi,
                    np.zeros(T["ng"]), T["theta_full"])
    cell = dict(vtag=vtag, arm=arm, G=G, part="accept", regime="B", budget=2400, cost="unit", n_L=G, m="prop")
    summarise(acc, cell, data["genes"], rows, generows)
    pd.DataFrame(rows).to_csv(os.path.join(out, f"e3_accept__{vtag}__{arm}.csv"), index=False)
    pd.DataFrame(ident).to_csv(os.path.join(out, f"e3_accept_identity__{vtag}__{arm}.csv"), index=False)
    return len(rows)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--parquet", required=True)
    p.add_argument("--vtag", required=True)
    p.add_argument("--arm", required=True)
    p.add_argument("--parts", default="components,regcomp,masking,regb,unitw")
    p.add_argument("--draws", type=int, default=200)
    p.add_argument("--max-genes", type=int, default=0)
    p.add_argument("--theta2-kind", default="neo_minus_stroma", choices=("neo_minus_stroma", "mean"))
    p.add_argument("--out-dir", default=".")
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    Q2.THETA2_KIND = a.theta2_kind
    os.makedirs(a.out_dir, exist_ok=True)
    t0 = time.time()
    data = load_arm(a.parquet, a.arm, a.vtag)
    if a.max_genes:
        data["genes"] = data["genes"][:a.max_genes]
        data["Y"], data["P"] = data["Y"][:, :a.max_genes], data["P"][:, :a.max_genes]
    Tset = build(data, a.vtag, a.arm)
    summ = dict(vtag=a.vtag, arm=a.arm, G=len(data["donors"]), n_genes=len(data["genes"]), draws=a.draws,
                parts={}, theta2_kind=a.theta2_kind)
    for part in a.parts.split(","):
        if part == "components":
            summ["parts"][part] = components_part(data, Tset, a.vtag, a.arm, a.out_dir)
        elif part == "unitw":
            summ["parts"][part] = unitw_part(data, a.vtag, a.arm, a.draws, a.out_dir)
        elif part == "accept":
            summ["parts"][part] = accept_part(data, Tset, a.vtag, a.arm, a.draws, a.out_dir)
        else:
            summ["parts"][part] = run_part(part, data, Tset, a.vtag, a.arm, a.draws, a.out_dir)
        print(f"part {part} done {time.time() - t0:.0f}s", flush=True)
    summ["wall_s"] = time.time() - t0
    json.dump(summ, open(os.path.join(a.out_dir, f"e3_summary__{a.vtag}__{a.arm}__{a.parts.replace(',', '+')}.json"), "w"),
              indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
