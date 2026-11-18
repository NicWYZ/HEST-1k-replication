"""fcheck: assemble the recomputed part of fcheck_table.csv: every number of the report's tables (and the counted
claims named in the brief) against the recomputed values in the fcheck output directories. Reported values typed
from docs/round11/closeout/round11_closeout_report.md at d0821b62."""
import json, os
import numpy as np, pandas as pd
F = "/work/users/w/e/weiyang/hest_replication/results/round11/closeout/fcheck"
inputs = []
def rc(p): inputs.append(p); return pd.read_csv(p)
D = rc(f"{F}/donor/fcheck_donor_cells.csv"); D12 = rc(f"{F}/donor/fcheck_d12.csv")
C = rc(f"{F}/center_v2/fcheck_center_pearson.csv"); H = rc(f"{F}/center_v2/fcheck_center_hcp.csv")
K = rc(f"{F}/conformal_v2/fcheck_conformal_cells.csv"); T3 = rc(f"{F}/conformal_v2/fcheck_round3_uni_v2_shortfalls.csv")
JOB = {k: open(f"{F}/{k}/PROVENANCE.txt").read().split("\n")[0].split(": ")[1] for k in ("donor", "center_v2", "conformal_v2")}; JOB["center"] = JOB["center_v2"]; JOB["conformal"] = JOB["conformal_v2"]
rows = []
def add(loc, qty, rep, val, job, src, prec=None):
    rep_s = str(rep); dec = len(rep_s.split(".")[1]) if "." in rep_s else 0
    if prec is not None: dec = prec
    if val is None or (isinstance(val, float) and np.isnan(val)):
        rows.append(dict(location=loc, quantity=qty, reported=rep_s, recomputed="", abs_diff="", verdict="NOT FOUND", job=JOB.get(job, job), file=src)); return
    diff = abs(float(rep) - float(val))
    ok = diff <= 0.5 * 10 ** (-dec) + 1e-9
    rows.append(dict(location=loc, quantity=qty, reported=rep_s, recomputed=repr(float(val)), abs_diff=f"{diff:.3g}",
                     verdict="agrees at quoted precision" if ok else "DISAGREES", job=JOB.get(job, job), file=src))
def d(task, arm, col, scale="log1p", est="theta3", n=8):
    q = D[(D.task == task) & (D.arm == arm) & (D.scale == scale) & (D.estimand == est) & (D.n == n)]
    assert len(q) == 1, (task, arm, scale, est, n, len(q)); return float(q[col].iloc[0])
DSRC = "a6/donor/<task>__<arm>/regimeA/regimeA_cells.parquet; cv/cluster_values__*.parquet"
TL = {"CCRCC": "CCRCC", "INDIANA_KIDNEY": "INDIANA_KIDNEY", "kidney__Visium": "kidney Visium", "bowel__Visium": "bowel Visium", "LUNG_XENIUM": "LUNG_XENIUM"}
T62 = [("CCRCC", "R10", 0.8949, None, 0.4290, 0.8966, 0.0022), ("CCRCC", "P", 0.9750, (0.0704, -0.0108, 0.1349), 0.2809, 0.8871, 0.0022),
       ("CCRCC", "E", 0.9984, (0.0588, 0.0009, 0.1307), 0.3381, 0.8957, 0.0022),
       ("INDIANA_KIDNEY", "R10", 0.9570, None, 0.1390, 0.8974, 0.0021), ("INDIANA_KIDNEY", "P", 0.9227, (-0.0136, -0.0559, 0.0167), 0.1639, 0.8955, 0.0022),
       ("INDIANA_KIDNEY", "E", 0.9107, (-0.0195, -0.0598, 0.0168), 0.2075, 0.8955, 0.0022),
       ("kidney__Visium", "R10", 0.9367, None, 0.1986, 0.8948, 0.0022), ("kidney__Visium", "P", 0.9631, (0.0210, -0.0025, 0.0507), 0.1224, 0.8925, 0.0022),
       ("kidney__Visium", "E", 0.9930, (0.0495, 0.0262, 0.0708), 0.1238, 0.8915, 0.0022),
       ("bowel__Visium", "R10", 0.6691, None, 0.6258, 0.8878, 0.0022), ("bowel__Visium", "P", 0.6372, (-0.0484, -0.1030, 0.0056), 0.6326, 0.8902, 0.0022),
       ("bowel__Visium", "E", 0.6044, (-0.0680, -0.0930, -0.0056), 0.6451, 0.8892, 0.0022),
       ("LUNG_XENIUM", "R10", 0.5853, None, 0.7139, 0.8878, 0.0022), ("LUNG_XENIUM", "P", 0.5627, (-0.0136, -0.0518, 0.0184), 0.7219, 0.8891, 0.0022),
       ("LUNG_XENIUM", "E", 0.5425, (-0.0360, -0.0860, 0.0210), 0.7402, 0.8908, 0.0022)]
for t, a, wr, ch, r2, cov, se in T62:
    L = f"6.2 table, {TL[t]} {a}"
    add(L, "width ratio fix1/classical (theta3 log1p nL=8)", wr, d(t, a, "wr_median"), "donor", DSRC, 4)
    if ch:
        for nm, v, col in zip(("median", "q25", "q75"), ch, ("wr_diff_median", "wr_diff_q25", "wr_diff_q75")):
            add(L, f"per-gene change vs R10, {nm}", v, d(t, a, col), "donor", DSRC, 4)
    add(L, "median R2c", r2, d(t, a, "R2c_median"), "donor", DSRC, 4)
    add(L, "fix1 coverage median", cov, d(t, a, "cov_fix1_median"), "donor", DSRC, 4)
    add(L, "fix1 coverage MCSE (median over genes)", se, d(t, a, "mcse_fix1_median"), "donor", DSRC, 4)
for t, a, wr, r2 in [("CCRCC", "P", 0.9750, 0.2809), ("INDIANA_KIDNEY", "P", 0.9227, 0.1639), ("kidney__Visium", "P", 0.9631, 0.1224), ("bowel__Visium", "P", 0.6372, 0.6326), ("LUNG_XENIUM", "P", 0.5627, 0.7219),
                     ("CCRCC", "E", 0.9984, 0.3381), ("INDIANA_KIDNEY", "E", 0.9107, 0.2075), ("kidney__Visium", "E", 0.9930, 0.1238), ("bowel__Visium", "E", 0.6044, 0.6451), ("LUNG_XENIUM", "E", 0.5425, 0.7402)]:
    add(f"headline H3 Part A, {TL[t]} {a}", "width ratio", wr, d(t, a, "wr_median"), "donor", DSRC, 4)
    add(f"headline H3 Part A, {TL[t]} {a}", "median R2c", r2, d(t, a, "R2c_median"), "donor", DSRC, 4)
for t, wr in [("CCRCC", 0.8949), ("INDIANA_KIDNEY", 0.9570), ("kidney__Visium", 0.9367), ("bowel__Visium", 0.6691), ("LUNG_XENIUM", 0.5853)]:
    add(f"headline H3 Part A, {TL[t]} R10", "width ratio", wr, d(t, "R10", "wr_median"), "donor", DSRC, 4)
add("headline item 3", "CCRCC width ratio rise under P", 0.080, d("CCRCC", "P", "wr_median") - d("CCRCC", "R10", "wr_median"), "donor", DSRC, 3)
add("headline item 3", "CCRCC width ratio rise under E", 0.104, d("CCRCC", "E", "wr_median") - d("CCRCC", "R10", "wr_median"), "donor", DSRC, 3)
def d12(t, a):
    q = D12[(D12.task == t) & (D12.arm == a) & (D12.scale == "log1p") & ~D12.file.str.contains("lognorm")]; assert len(q) == 1, (t, a, len(q)); return float(q.R2_loo_const_median.iloc[0])
for t, vals in [("CCRCC", (0.0237, 0.0118, 0.0467)), ("INDIANA_KIDNEY", (0.0423, 0.0565, 0.0834)), ("LUNG_XENIUM", (0.1071, 0.1264, 0.1395)),
                ("bowel__Visium", (0.2218, 0.2617, 0.3545)), ("kidney__Visium", (0.3815, 0.3446, 0.3213))]:
    for a, v in zip(("R10", "P", "E"), vals):
        add(f"6.2 LODO list, {TL[t]} {a}", "LODO median R2 vs LOO constant (log1p)", v, d12(t, a), "donor", "a6/donor/<task>__<arm>/d12*/d12_lodo_r2__*.csv", 4)
for t, a, v in [("CCRCC", "P", 0.0118), ("kidney__Visium", "P", 0.3446), ("CCRCC", "E", 0.0467), ("kidney__Visium", "E", 0.3213)]:
    add(f"headline H3 Part A, {TL[t]} {a}", "LODO R2", v, d12(t, a), "donor", "d12_lodo_r2__*.csv", 4)
th = D[D.estimand == "theta3"]; mu = D[D.estimand == "mu"]
add("6.2 reading / headline H3", "theta3 cells where rho(wr,R2c) < rho(wr,pearson)", 84, int((th.rho_wr_R2c < th.rho_wr_pearson).sum()), "donor", "fcheck_donor_cells.csv", 0)
add("6.2 reading / headline H3", "theta3 cells (count)", 84, len(th), "donor", "fcheck_donor_cells.csv", 0)
add("6.2 reading", "theta3 rho(wr,R2c) minimum", -0.97, th.rho_wr_R2c.min(), "donor", "fcheck_donor_cells.csv", 2)
add("6.2 reading", "theta3 rho(wr,R2c) maximum", -0.30, th.rho_wr_R2c.max(), "donor", "fcheck_donor_cells.csv", 2)
add("6.2 reading", "mu cells where rho(wr,R2c) < rho(wr,pearson)", 82, int((mu.rho_wr_R2c < mu.rho_wr_pearson).sum()), "donor", "fcheck_donor_cells.csv", 0)
add("6.2 reading", "mu cells (count)", 84, len(mu), "donor", "fcheck_donor_cells.csv", 0)
ex = mu[~(mu.rho_wr_R2c < mu.rho_wr_pearson)]
rows.append(dict(location="6.2 reading", quantity="mu exceptions", reported="CCRCC log1p nL=8 under R10 and P; within 0.03",
                 recomputed="; ".join(f"{r.task} {r.scale} n={r.n} {r.arm}: {r.rho_wr_R2c:.4f} vs {r.rho_wr_pearson:.4f}" for r in ex.itertuples()),
                 abs_diff="", verdict="see recomputed", job=JOB["donor"], file="fcheck_donor_cells.csv"))
c15 = th[(th.scale == "log1p") & (th.n == 8)]
add("5.3 A6.2(d)", "cells held of 15", 15, int((c15.rho_wr_R2c < c15.rho_wr_pearson).sum()), "donor", "fcheck_donor_cells.csv", 0)
add("6.2 reading", "INDIANA_KIDNEY P median spot Pearson", 0.2235, d("INDIANA_KIDNEY", "P", "pearson_spot_median"), "donor", "join_log1p parquet (y__, f__)", 4)
add("6.2 reading", "INDIANA_KIDNEY R10 median spot Pearson", 0.2299, d("INDIANA_KIDNEY", "R10", "pearson_spot_median"), "donor", "join_log1p parquet (y__, f__)", 4)
nine = sum(d(t, a, "pearson_spot_median") > d(t, "R10", "pearson_spot_median") for t in TL for a in ("P", "E"))
add("6.2 reading", "cells (of 10) where spot Pearson rises vs R10", 9, nine, "donor", "fcheck_donor_cells.csv", 0)
add("6.2 normalised scale", "kidney Visium theta3 lognorm nL=8 wr P", 0.9516, d("kidney__Visium", "P", "wr_median", "lognorm"), "donor", DSRC, 4)
add("6.2 normalised scale", "kidney Visium theta3 lognorm nL=8 wr E", 1.0225, d("kidney__Visium", "E", "wr_median", "lognorm"), "donor", DSRC, 4)
add("6.2 normalised scale", "kidney Visium theta3 lognorm nL=8 wr R10", 0.9566, d("kidney__Visium", "R10", "wr_median", "lognorm"), "donor", DSRC, 4)
for nm, col in (("median of per-gene ratios", "sdf_ratio_median_of_ratios"), ("ratio of medians", "sdf_ratio_of_medians")):
    for t, a, v in [("bowel__Visium", "P", 1.016), ("LUNG_XENIUM", "P", 1.072), ("kidney__Visium", "E", 1.120), ("bowel__Visium", "E", 1.023)]:
        add(f"5.3 A6.1 / 6.2 spread of f_g, mu log1p [{nm}]", f"{TL[t]} {a}", v, d(t, a, col, est="mu"), "donor", "cv/cluster_values__*.parquet", 3)
mup = D[(D.estimand == "mu") & (D.scale == "log1p") & (D.n == 8) & (D.arm == "P")]
dd = mup.R2c_median - mup.R2c_median_R10
add("6.2 / plan A6.1", "P mu log1p R2c change vs R10, min", -0.037, dd.min(), "donor", "cv/cluster_values__*.parquet", 3)
add("6.2 / plan A6.1", "P mu log1p R2c change vs R10, max", 0.029, dd.max(), "donor", "cv/cluster_values__*.parquet", 3)
add("5.3 A6.1", "bowel P mu R2c change", -0.010, d("bowel__Visium", "P", "R2c_median", est="mu") - d("bowel__Visium", "R10", "R2c_median", est="mu"), "donor", "cluster_values", 3)
add("5.3 A6.1", "LUNG_XENIUM P mu R2c change", 0.007, d("LUNG_XENIUM", "P", "R2c_median", est="mu") - d("LUNG_XENIUM", "R10", "R2c_median", est="mu"), "donor", "cluster_values", 3)
ccmu = D[(D.task == "CCRCC") & (D.estimand == "mu") & (D.scale == "log1p") & (D.n.isin([8, 16]))]
add("5.3 A6.2(f) / 7 item 4", "CCRCC mu log1p fix1 coverage min (nL 8,16, 3 arms)", 0.848, ccmu.cov_fix1_median.min(), "donor", DSRC, 3)
add("5.3 A6.2(f) / 7 item 4", "CCRCC mu log1p fix1 coverage max (nL 8,16, 3 arms)", 0.870, ccmu.cov_fix1_median.max(), "donor", DSRC, 3)
# Center
def cp(dirname, col):
    q = C[C.dir == dirname]; assert len(q) == 1, dirname; return float(q[col].iloc[0])
CSRC = "predict/<task>__<arm>__center/pred__*.parquet"
for t, a, v, fm, q25, q75 in [("kidney__Visium", "R10", 0.1231, 0.1325, 0.0326, 0.2922), ("kidney__Visium", "P", 0.1068, 0.1554, 0.1454, 0.3311),
                              ("kidney__Visium", "E", 0.1360, 0.1784, 0.0096, 0.3574), ("brain__Visium", "R10", 0.0215, 0.1213, 0.0130, 0.1914),
                              ("brain__Visium", "P", 0.0643, 0.1264, 0.0379, 0.2347), ("brain__Visium", "E", 0.1177, 0.1153, 0.0420, 0.1630)]:
    dn = f"{t}__{a}__center"; L = f"6.3 table, {t.split('__')[0]} Visium {a}"
    add(L, "median Pearson held out by center", v, cp(dn, "median_pearson_log1p"), "center", CSRC, 4)
    add(L, "per-fold median, median over folds", fm, cp(dn, "fold_median"), "center", CSRC, 4)
    add(L, "per-fold median, q25", q25, cp(dn, "fold_q25"), "center", CSRC, 4)
    add(L, "per-fold median, q75", q75, cp(dn, "fold_q75"), "center", CSRC, 4)
    add(f"headline H2 Part A, {t.split('__')[0]} Visium {a}", "by center", v, cp(dn, "median_pearson_log1p"), "center", CSRC, 4)
add("headline H2 / 5.1 P11.3", "kidney P by donor", 0.4816, cp("kidney__Visium__P__donor", "median_pearson_log1p"), "center", "predict/kidney__Visium__P__donor/pred__*.parquet", 4)
add("6.3 text", "kidney R10 by donor (0.47, lower end)", 0.47, cp("kidney__Visium__R10__donor", "median_pearson_log1p"), "center", "predict/kidney__Visium__R10__donor/pred__*.parquet", 2)
add("6.3 text", "kidney E by donor (0.50, upper end)", 0.50, cp("kidney__Visium__E__donor_v2", "median_pearson_log1p"), "center", "predict/kidney__Visium__E__donor_v2/pred__*.parquet", 2)
HSRC = "a6/inst/center_v1/inst_by_gene.parquet"
def h(a, kind, col):
    enc = {"R10": "uni_v2", "P": "P", "E": "E_posthoc"}[a]; q = H[(H.encoder == enc) & (H.arm == kind)]
    assert len(q) == 1, (a, kind, len(q)); return float(q[col].iloc[0])
for a, med, s6, hc in [("R10", 0.9057, 0.6552, 1.0), ("P", 0.9281, 0.5819, 1.0), ("E", 0.9326, 0.6296, 1.0)]:
    try:
        add(f"6.3 table, kidney Visium {a}", "HCP pooled (donor-level), median center, alpha 0.2", med, h(a, "hcp_donor", "median_center"), "center", HSRC, 4)
        add(f"6.3 table, kidney Visium {a}", "HCP pooled (donor-level), S0006", s6, h(a, "hcp_donor", "S0006"), "center", HSRC, 4)
        add(f"6.3 table, kidney Visium {a}", "HCP over centers, median center", hc, h(a, "hcp_center", "median_center"), "center", HSRC, 1)
        add(f"headline H2 Part A, kidney {a}", "S0006", s6, h(a, "hcp_donor", "S0006"), "center", HSRC, 4)
        add(f"headline H2 Part A, kidney {a}", "median center", med, h(a, "hcp_donor", "median_center"), "center", HSRC, 4)
    except AssertionError as e:
        rows.append(dict(location=f"6.3 table, kidney Visium {a}", quantity="HCP", reported="", recomputed=str(e), abs_diff="", verdict="NOT FOUND", job=JOB["center"], file=HSRC))
# Conformal
K = K[K.score == "abs"].copy()
K["D"] = np.where(K.dir.str.endswith("__center"), "center", K.design)
def k(t, a, D_, col="coverage_mean", sc="log1p"):
    q = K[(K.task == t) & (K.arm == a) & (K.D == D_) & (K.scale == sc)]; assert len(q) == 1, (t, a, D_, sc, len(q)); return float(q[col].iloc[0])
KSRC = "a6/conformal/<task>__<arm>__<design>/a1_by_fold__*.csv"
T64 = [("CCRCC", 24, (0.8824, 0.0009), None, (0.8640, 0.1442), None, 0.8649, 0.8613),
       ("INDIANA_KIDNEY", 25, (0.9070, 0.0130), (0.8790, 0.0463), (0.8776, 0.0442), None, 0.8747, 0.8771),
       ("LUNG_XENIUM", 15, (0.9006, 0.0056), (0.8970, 0.0404), (0.8872, 0.0376), None, 0.8874, 0.8850),
       ("bowel__Visium", 18, (0.8984, 0.0055), (0.8941, 0.1352), (0.8921, 0.1261), (0.8344, 0.1351), 0.8881, 0.8870),
       ("kidney__Visium", 51, (0.9073, 0.0114), (0.8999, 0.0673), (0.8940, 0.0787), (0.8777, 0.1096), 0.8923, 0.8941)]
for t, nd, ra, so, do, ce, dp, de in T64:
    L = f"6.4 table, {TL[t]}"
    add(L, "donors (donor design n_folds)", nd, k(t, "R10", "donor", "n_folds"), "conformal", KSRC, 0)
    for nm, D_, v in (("random", "random", ra), ("slide_out", "slide_out", so), ("donor", "donor", do), ("center", "center", ce)):
        if v:
            add(L, f"R10 {nm} coverage mean", v[0], k(t, "R10", D_), "conformal", KSRC, 4)
            add(L, f"R10 {nm} coverage sd over folds", v[1], k(t, "R10", D_, "coverage_sd_ddof1"), "conformal", KSRC, 4)
    add(L, "donor under P", dp, k(t, "P", "donor"), "conformal", KSRC, 4)
    add(L, "donor under E", de, k(t, "E", "donor"), "conformal", KSRC, 4)
    add(f"headline H1(b) Part A, {TL[t]}", "donor under P", dp, k(t, "P", "donor"), "conformal", KSRC, 4)
add("6.4 note", "kidney Visium random folds reported", 35, k("kidney__Visium", "R10", "random", "n_folds"), "conformal", KSRC, 0)
for t, v in [("CCRCC", 0.8803), ("INDIANA_KIDNEY", 0.9069), ("LUNG_XENIUM", 0.9000), ("bowel__Visium", 0.8977), ("kidney__Visium", 0.9084)]:
    add(f"headline H1(b) Part A, {TL[t]}", "random under P", v, k(t, "P", "random"), "conformal", KSRC, 4)
add("headline / 5.1 P11.4", "kidney center under P", 0.8714, k("kidney__Visium", "P", "center"), "conformal", KSRC, 4)
add("headline item 4", "kidney P random - center", 0.0370, k("kidney__Visium", "P", "random") - k("kidney__Visium", "P", "center"), "conformal", KSRC, 4)
add("headline item 4", "kidney R10 random - center", 0.0296, k("kidney__Visium", "R10", "random") - k("kidney__Visium", "R10", "center"), "conformal", KSRC, 4)
cells = K.pivot_table(index=["task", "arm", "scale"], columns="D", values="coverage_mean").reset_index()
add("5.3 A6.4(a)", "cells with random within 0.01 of 0.90", 27, int(((cells["random"] - 0.9).abs() <= 0.01).sum()), "conformal", KSRC, 0)
add("5.3 A6.4", "(task, scale, arm) cells", 30, len(cells), "conformal", KSRC, 0)
for a, v in (("R10", 0.8824), ("P", 0.8803), ("E", 0.8868)):
    add("5.3 A6.4(a)", f"CCRCC log1p random under {a}", v, k("CCRCC", a, "random"), "conformal", KSRC, 4)
cells["short"] = cells["random"] - cells["donor"]
add("5.3 A6.4(b)", "cells with donor >= 0.02 below random", 5, int((cells.short >= 0.02).sum()), "conformal", KSRC, 0)
oth = cells[cells.arm != "R10"].merge(cells[cells.arm == "R10"][["task", "scale", "donor"]], on=["task", "scale"], suffixes=("", "_R10"))
add("5.3 A6.4(c) / 6.4", "max |donor(P,E) - donor(R10)| over 20 cells", 0.0051, (oth.donor - oth.donor_R10).abs().max(), "conformal", KSRC, 4)
add("5.3 A6.4(c)", "cells compared", 20, len(oth), "conformal", KSRC, 0)
sdd = K[K.D == "donor"]
add("6.4 reading", "donor coverage sd over folds, min (30 cells)", 0.030, sdd.coverage_sd_ddof1.min(), "conformal", KSRC, 3)
add("6.4 reading", "donor coverage sd over folds, max (30 cells)", 0.147, sdd.coverage_sd_ddof1.max(), "conformal", KSRC, 3)
cc = cells.dropna(subset=["center"]).copy(); cc["gap"] = cc.donor - cc.center
add("5.3 A6.4(d) / 6.4", "cells with center below donor", 12, int((cc.gap > 0).sum()), "conformal", KSRC, 0)
add("5.3 A6.4(d)", "center cells (count)", 12, len(cc), "conformal", KSRC, 0)
def gap(t, a, sc): return float(cc[(cc.task == t) & (cc.arm == a) & (cc.scale == sc)].gap.iloc[0])
add("6.4 reading / 5.3 B2(d)", "R10 bowel log1p donor - center", 0.0578, gap("bowel__Visium", "R10", "log1p"), "conformal", KSRC, 4)
add("6.4 reading", "R10 kidney lognorm donor - center", 0.0479, gap("kidney__Visium", "R10", "lognorm"), "conformal", KSRC, 4)
add("6.4 reading / 5.3 B2(d)", "R10 kidney log1p donor - center", 0.0164, gap("kidney__Visium", "R10", "log1p"), "conformal", KSRC, 4)
add("6.4 reading", "R10 bowel lognorm donor - center", 0.0064, gap("bowel__Visium", "R10", "lognorm"), "conformal", KSRC, 4)
r10l = cells[(cells.arm == "R10") & (cells.scale == "log1p")]
add("6.4 / headline H1(b)", "R10 log1p donor shortfall min", 0.006, r10l.short.min(), "conformal", KSRC, 3)
add("6.4 / headline H1(b)", "R10 log1p donor shortfall max", 0.029, r10l.short.max(), "conformal", KSRC, 3)
def t3(task, col, ls="shipped"):
    q = T3[(T3.task == task) & (T3.label_set == ls)]; assert len(q) == 1; return float(q[col].iloc[0])
R3 = "results/round3/A1_coverage/a1_by_task__uni_v2__main.csv (score abs)"
for tk, v in (("HCC", 0.7625), ("SKCM", 0.6801), ("LUNG", 0.6177)):
    add("6.4 reading / headline item 4 (round 3)", f"{tk} donor coverage", v, t3(tk, "donor"), "conformal", R3, 4)
add("6.4 reading (round 3)", "shortfall min over HCC/SKCM/LUNG", 0.14, min(t3(x, "shortfall") for x in ("HCC", "SKCM", "LUNG")), "conformal", R3, 2)
add("6.4 reading (round 3)", "shortfall max over HCC/SKCM/LUNG", 0.28, max(t3(x, "shortfall") for x in ("HCC", "SKCM", "LUNG")), "conformal", R3, 2)
add("6.4 reading (round 3)", "CCRCC shortfall", 0.0176, t3("CCRCC", "shortfall"), "conformal", R3, 4)
add("6.4 reading (round 3)", "PRAD shortfall", 0.0207, t3("PRAD", "shortfall"), "conformal", R3, 4)
add("6.4 reading (round 3)", "PAAD shortfall", -0.0023, t3("PAAD", "shortfall"), "conformal", R3, 4)
add("plan A6.4 reading (round 3)", "LYMPH_IDC shortfall", 0.0845, t3("LYMPH_IDC", "shortfall"), "conformal", R3, 4)
add("plan A6.4 reading (round 3)", "READ shortfall", 0.0655, t3("READ", "shortfall"), "conformal", R3, 4)
add("headline item 4 / 6.4 (round 3)", "CCRCC donor", 0.8654, t3("CCRCC", "donor"), "conformal", R3, 4)
add("headline item 4 / 6.4 (round 3)", "CCRCC random", 0.8830, t3("CCRCC", "random"), "conformal", R3, 4)
big = T3[T3.shortfall > 0.05]
rows.append(dict(location="6.4 reading (round 3)", quantity="every shortfall > 0.05 on a task with at most four donors", reported="true",
                 recomputed=f"max donors among shortfall>0.05: {int(big.donors.max())}; " + "; ".join(f"{r.task}/{r.label_set} {r.donors}d {r.shortfall:.4f}" for r in big.itertuples()),
                 abs_diff="", verdict="agrees" if big.donors.max() <= 4 else "DISAGREES", job=JOB["conformal"], file=R3))
o = pd.DataFrame(rows); o.to_csv("fcheck_table_recomputed.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 200); pd.set_option("display.max_rows", 500)
print(o.verdict.value_counts().to_dict()); print(o[o.verdict != "agrees at quoted precision"].to_string())
open("inputs.txt", "w").write("\n".join(sorted(set(inputs))) + "\n")
