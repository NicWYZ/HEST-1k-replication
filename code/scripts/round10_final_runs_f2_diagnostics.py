"""Round 10, track final-runs, F2.5 to F2.8: shortfall, what predictions buy, scale difference, superpopulation interval
(plan, sections 5.5 to 5.7).

Per population (task, encoder, scale, estimand) and gene, from the cluster values: skewness of z_g and of the fix1
residual e_g = z_g - f_g (scipy.stats.skew, round 9's default), the residual max-share kappa of e (round 9's `kap`),
of z and of the least-squares residual of z on f (round 9's `kappa_resid`), G* = 1 / sum_g s_g^2 with s_g the share of
cluster g in sum_g (e_g - ebar)^2 (decisions section 4, item 3), and the cluster-level R^2 = corr(z, f)^2 (round 9's
R2c_mean). round 9's `frontiers(G, n)` gives (k*, kappa_star_v1, kappa_sup) at each n_L of regime A's grid. The
functions `kap`, `frontiers` and `pi_k` are taken from round9_fewcluster_hest_kappa.py by executing its definitions
unchanged (the script's module-level code after them, which reads its input, is not run).
Spot-level Pearson per gene and the ratio of the donor-clustered to the i.i.d. standard error of the spot mean (D9) are
computed from the spot files the config lists. pc1_share per (task, encoder, scale) through round 9's factor_rows
(round9_c0_diagnostics.py, imported unchanged) on the mu cluster values.
Each gene row is joined to regime A's gene rows of fix1, classical, xf2_r5 (V_w) and fix1_nofpc.

usage: round10_final_runs_f2_diagnostics.py <config.json> <out_dir>
Writes f2_diag_summary.json first, then f2_gene_diag.parquet, f2_anchor_r9_kappa.csv, f2_anchor_r9_c0.csv,
f2_pc1_share.csv, f2_anchor_r9_pc1.csv, f2_d9.csv, f2_shortfall.csv, f2_fr6.csv, f2_buy.csv, f2_scale_diff.csv,
f2_superpop.csv.
"""
import glob, json, os, sys, time
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
from scipy import stats
import round9_c0_diagnostics as C0

KEYS = ["task", "encoder", "scale", "estimand", "gene"]


def round9_kappa_functions(path):
    src = open(path).read()
    cut = src.index("\nd = pd.read_csv(src)")
    ns = {}
    argv = sys.argv; sys.argv = [path, "unused", "unused"]
    try:
        exec(compile(src[:cut], path, "exec"), ns)
    finally:
        sys.argv = argv
    return ns


def gene_stats(z, f, kap):
    e = z - f
    X = np.c_[np.ones(len(z)), f]; H = X @ np.linalg.pinv(X); r = z - H @ z
    d = (e - e.mean()) ** 2; ss = d.sum()
    res = np.polyval(np.polyfit(f, z, 1), f)
    return dict(G=len(z), skew_z=float(stats.skew(z)), skew_e=float(stats.skew(e)), kappa_z=kap(z), kappa_e=kap(e),
                kappa_ols=kap(r), Gstar_e=float(1.0 / ((d / ss) ** 2).sum()) if ss > 0 else np.nan,
                R2c=float(np.corrcoef(z, f)[0, 1] ** 2) if np.std(f) > 0 and np.std(z) > 0 else np.nan,
                skew_resid_ols=float(stats.skew(z - res)))


def spot_stats(sf):
    df = pd.read_parquet(sf["path"])
    donor = df[sf.get("donor_col", "donor_id")].astype(str).to_numpy()
    if "joined_only" in sf and sf["joined_only"]:
        df = df[df["joined"].to_numpy(bool)]; donor = df[sf.get("donor_col", "donor_id")].astype(str).to_numpy()
    codes, uniq = pd.factorize(donor); G = len(uniq)
    rows = []
    for sc in sf["scales"]:
        genes = [c[len(sc["y_prefix"]):] for c in df.columns if c.startswith(sc["y_prefix"])]
        Y = df[[sc["y_prefix"] + g for g in genes]].to_numpy(np.float64)
        F = df[[sc["f_prefix"] + g for g in genes]].to_numpy(np.float64) if sc.get("f_prefix") else None
        N = len(Y); dev = Y - Y.mean(0)
        S = np.zeros((G, Y.shape[1])); np.add.at(S, codes, dev)
        se_cl = np.sqrt(G / (G - 1) * (S ** 2).sum(0)) / N
        se_iid = Y.std(0, ddof=1) / np.sqrt(N)
        for j, g in enumerate(genes):
            p = np.nan
            if F is not None and np.std(F[:, j]) > 0 and np.std(Y[:, j]) > 0:
                p = float(np.corrcoef(Y[:, j], F[:, j])[0, 1])
            rows.append(dict(task=sf["task"], encoder=sf["encoder"], scale=sc["name"], gene=g, n_spots=N, G_spot=G,
                             pearson_spot=p, d9_ratio=float(se_cl[j] / se_iid[j]) if se_iid[j] > 0 else np.nan))
    return rows


def main():
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    summ = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"))
    sp = os.path.join(out, "f2_diag_summary.json"); json.dump(summ, open(sp, "w"), indent=1)
    ks = cfg["round9_kappa_script"]
    ks = ks if os.path.isabs(ks) else os.path.join(os.path.dirname(os.path.abspath(__file__)), ks)
    K9 = round9_kappa_functions(ks); kap = K9["kap"]

    def frontiers(G, n):
        """round 9's frontiers(G, n); (nan, nan, nan) where no k <= G/2 reaches pi_k <= alpha (round 9's code then fails)."""
        try:
            return K9["frontiers"](G, n)
        except TypeError:
            return (np.nan, np.nan, np.nan)
    cv = pd.concat([pd.read_parquet(p) for p in cfg["cluster_values"]], ignore_index=True)
    rows = []
    for key, g in cv.groupby(KEYS, sort=True):
        g = g.sort_values("donor"); z = g.z.to_numpy(float); f = g.f.to_numpy(float)
        if not (np.isfinite(z).all() and np.isfinite(f).all()) or len(z) < 3:
            continue
        rows.append(dict(zip(KEYS, key), **gene_stats(z, f, kap)))
    GD = pd.DataFrame(rows)
    # anchors against round 9 (mu, log1p; HEST uni_v2 and ACS pkg for kappa; every encoder in c0 for R2c and skew)
    i24 = pd.read_csv(cfg["r9_i24"])
    a = GD[(GD.estimand == "mu") & (GD.scale.isin(["log1p", "log_income"]))].merge(i24, on=["task", "encoder", "gene"], suffixes=("", "_r9"))
    a["n_mid"] = a["n_mid"].astype(int)
    fr = a.apply(lambda r: frontiers(int(r.G), int(r.n_mid)), axis=1, result_type="expand")
    a["v1_ours"], a["sup_ours"] = fr[1], fr[2]
    ak = dict(rows=len(a), rows_r9=len(i24), max_d_kappa_raw=float((a.kappa_z - a.kappa_raw).abs().max()),
              max_d_kappa_resid=float((a.kappa_ols - a.kappa_resid).abs().max()),
              max_d_v1=float((a.v1_ours - a.kappa_star_v1).abs().max()),
              max_d_sup=float((a.sup_ours.replace(np.inf, 1e9) - a.kappa_sup.replace(np.inf, 1e9)).abs().max()))
    a.to_csv(os.path.join(out, "f2_anchor_r9_kappa.csv"), index=False)
    c0 = pd.read_csv(cfg["r9_c0_gene"])
    b = GD[(GD.estimand == "mu") & (GD.scale.isin(["log1p", "log_income"]))].merge(c0, on=["task", "encoder", "gene"], suffixes=("", "_r9"))
    ac = dict(rows=len(b), rows_r9=len(c0), max_d_R2c=float((b.R2c - b.R2c_mean).abs().max()),
              max_d_skew_y=float((b.skew_z - b.skew_meany).abs().max()),
              max_d_skew_resid=float((b.skew_resid_ols - b.skew_resid_mean).abs().max()))
    b.to_csv(os.path.join(out, "f2_anchor_r9_c0.csv"), index=False)
    summ["anchors"] = dict(kappa=ak, c0=ac); json.dump(summ, open(sp, "w"), indent=1); print(json.dumps(summ["anchors"]), flush=True)
    # pc1_share per scale through round 9's factor_rows
    m = cv[cv.estimand == "mu"].rename(columns={"z": "mean_y", "f": "mean_f"}).assign(frac_nonzero_y=np.nan)
    pcs = []
    for sc, g in m.groupby("scale"):
        fr_ = C0.factor_rows(g[["task", "encoder", "donor", "gene", "mean_y", "mean_f", "frac_nonzero_y"]])
        if len(fr_):
            pcs.append(fr_.assign(scale=sc))
    PC = pd.concat(pcs, ignore_index=True); PC.to_csv(os.path.join(out, "f2_pc1_share.csv"), index=False)
    r9 = pd.read_csv(cfg["r9_c0_factor"]); ns = pd.read_csv(cfg["r9_norm_summary"])
    p1 = PC[PC.scale == "log1p"].merge(r9[["task", "encoder", "pc1_share"]], on=["task", "encoder"], suffixes=("", "_r9"))
    p2 = PC[(PC.scale == "norm_r9pair") & (PC.encoder == "uni_v2")].merge(ns[["task", "pc1_share_norm"]], on="task")
    ap = dict(rows_log1p=len(p1), max_d_log1p=float((p1.pc1_share - p1.pc1_share_r9).abs().max()) if len(p1) else np.nan,
              rows_norm=len(p2), max_d_norm_3dp=float((p2.pc1_share.round(3) - p2.pc1_share_norm).abs().max()) if len(p2) else np.nan)
    pd.concat([p1.assign(ref="c0_shared_donor_factor"), p2.assign(ref="norm_summary")]).to_csv(os.path.join(out, "f2_anchor_r9_pc1.csv"), index=False)
    summ["anchors"]["pc1"] = ap; json.dump(summ, open(sp, "w"), indent=1, default=str); print(json.dumps(ap), flush=True)
    # spot-level Pearson and D9
    SR = []
    for sf in cfg.get("spot_files", []):
        t0 = time.time(); SR += spot_stats(sf); print(f"spot {sf['task']} {sf['encoder']} {time.time() - t0:.0f}s", flush=True)
    SP = pd.DataFrame(SR); SP.to_csv(os.path.join(out, "f2_d9.csv"), index=False)
    GD = GD.merge(SP[["task", "encoder", "scale", "gene", "pearson_spot", "d9_ratio"]], on=["task", "encoder", "scale", "gene"], how="left")
    # regime A gene rows
    want = {("fix1", "fpc"): "fix1", ("classical", "fpc"): "cl", ("xf2_r5", "V_w"): "xf2", ("fix1_nofpc", "nofpc"): "fix1nf"}
    ra = []
    for p in sorted(glob.glob(os.path.join(cfg["regimeA_root"], "*", "regimeA_cells.parquet"))):
        x = pd.read_parquet(p, columns=KEYS + ["G", "n", "arm", "variance", "coverage", "median_width", "rmse"])
        x = x[[(a_, v_) in want for a_, v_ in zip(x.arm, x.variance)]]
        x["lab"] = [want[(a_, v_)] for a_, v_ in zip(x.arm, x.variance)]
        ra.append(x.drop(columns=["arm", "variance"]))
    RA = pd.concat(ra, ignore_index=True)
    W = RA.pivot_table(index=KEYS + ["n"], columns="lab", values=["coverage", "median_width", "rmse"]).reset_index()
    W.columns = ["_".join([c for c in col if c]) if isinstance(col, tuple) else col for col in W.columns]
    J = W.merge(GD, on=KEYS, how="left")
    fr = {(G, n): frontiers(int(G), int(n)) for G, n in set(zip(J.G, J.n))}
    J["k_star"] = [fr[(G, n)][0] for G, n in zip(J.G, J.n)]
    J["kappa_v1"] = [fr[(G, n)][1] for G, n in zip(J.G, J.n)]
    J["kappa_sup"] = [fr[(G, n)][2] for G, n in zip(J.G, J.n)]
    J["beyond_v1"] = J.kappa_e > J.kappa_v1; J["beyond_sup"] = J.kappa_e > J.kappa_sup
    J["wr_fix1"] = J.median_width_fix1 / J.median_width_cl; J["wr_xf2"] = J.median_width_xf2 / J.median_width_cl
    pq.write_table(pa.Table.from_pandas(J, preserve_index=False), os.path.join(out, "f2_gene_diag.parquet"))
    C = ["task", "encoder", "scale", "estimand", "n"]
    q = lambda s: s.median()
    sh = J.groupby(C).agg(G=("G", "first"), genes=("gene", "size"), k_star=("k_star", "first"), kappa_v1=("kappa_v1", "first"),
                          kappa_sup=("kappa_sup", "first"), median_kappa_e=("kappa_e", "median"),
                          median_kappa_ols=("kappa_ols", "median"), share_beyond_v1=("beyond_v1", "mean"),
                          share_beyond_sup=("beyond_sup", "mean"), median_Gstar_e=("Gstar_e", "median"),
                          median_skew_e=("skew_e", "median"), median_skew_z=("skew_z", "median"),
                          median_cov_fix1=("coverage_fix1", "median"), median_cov_cl=("coverage_cl", "median")).reset_index()
    by = J.groupby(C + ["beyond_sup"]).agg(median_cov_fix1=("coverage_fix1", "median"), genes=("gene", "size")).reset_index()
    byw = by.pivot_table(index=C, columns="beyond_sup", values=["median_cov_fix1", "genes"])
    byw.columns = [f"{a_}__beyond_sup_{b_}" for a_, b_ in byw.columns]
    sh = sh.merge(byw.reset_index(), on=C, how="left")
    rho = lambda a_, b_: float(stats.spearmanr(a_, b_, nan_policy="omit")[0]) if np.isfinite(a_).sum() > 3 else np.nan
    cc = J.groupby(C).apply(lambda g: pd.Series(dict(
        rho_cov_fix1_kappa_e=rho(g.coverage_fix1, g.kappa_e), rho_cov_fix1_skew_e=rho(g.coverage_fix1, g.skew_e),
        rho_cov_fix1_Gstar=rho(g.coverage_fix1, g.Gstar_e), rho_cov_cl_skew_z=rho(g.coverage_cl, g.skew_z)))).reset_index()
    sh = sh.merge(cc, on=C); sh.to_csv(os.path.join(out, "f2_shortfall.csv"), index=False)
    fr6 = sh[(sh.task == "kidney__Visium") & (sh.n == 16)]; fr6.to_csv(os.path.join(out, "f2_fr6.csv"), index=False)
    buy = J.groupby(C).apply(lambda g: pd.Series(dict(
        genes=len(g), median_wr_fix1=g.wr_fix1.median(), median_wr_xf2=g.wr_xf2.median(), median_R2c=g.R2c.median(),
        median_pearson_spot=g.pearson_spot.median(), rho_wr_fix1_R2c=rho(g.wr_fix1, g.R2c),
        rho_wr_fix1_pearson=rho(g.wr_fix1, g.pearson_spot), rho_wr_xf2_R2c=rho(g.wr_xf2, g.R2c),
        rho_wr_xf2_pearson=rho(g.wr_xf2, g.pearson_spot), median_d9=g.d9_ratio.median(),
        share_fix1_narrower=float((g.wr_fix1 < 1).mean())))).reset_index()
    buy.to_csv(os.path.join(out, "f2_buy.csv"), index=False)
    # scale difference: every pair of scales a task carries, against log1p
    Cs = ["task", "encoder", "estimand", "n"]
    rows = []
    for (t, e, est, n), g in sh.groupby(Cs):
        if "log1p" not in set(g.scale):
            continue
        base = J[(J.task == t) & (J.encoder == e) & (J.estimand == est) & (J.n == n)]
        b0 = base[base.scale == "log1p"]
        for sc in sorted(set(base.scale) - {"log1p"}):
            b1 = base[base.scale == sc]
            for lab in ("fix1", "xf2", "cl"):
                rows.append(dict(task=t, encoder=e, estimand=est, n=n, other_scale=sc, arm=lab,
                                 cov_log1p=float(b0[f"coverage_{lab}"].median()), cov_other=float(b1[f"coverage_{lab}"].median()),
                                 width_log1p=float(b0[f"median_width_{lab}"].median()), width_other=float(b1[f"median_width_{lab}"].median()),
                                 d_cov_other_minus_log1p=float(b1[f"coverage_{lab}"].median() - b0[f"coverage_{lab}"].median())))
    SD = pd.DataFrame(rows)
    pcw = PC.pivot_table(index=["task", "encoder"], columns="scale", values="pc1_share")
    pcw.columns = [f"pc1_share__{c}" for c in pcw.columns]
    SD = SD.merge(pcw.reset_index(), on=["task", "encoder"], how="left"); SD.to_csv(os.path.join(out, "f2_scale_diff.csv"), index=False)
    spp = J.groupby(C).agg(genes=("gene", "size"), median_cov_fix1=("coverage_fix1", "median"),
                           median_cov_fix1_nofpc=("coverage_fix1nf", "median"),
                           median_width_ratio_nofpc=("median_width_fix1nf", "median")).reset_index()
    spp["median_width_ratio_nofpc"] = J.assign(r=J.median_width_fix1nf / J.median_width_fix1).groupby(C).r.median().to_numpy()
    spp.to_csv(os.path.join(out, "f2_superpop.csv"), index=False)
    summ.update(gene_rows=len(J), shortfall_rows=len(sh), finished=time.strftime("%Y-%m-%dT%H:%M:%S"))
    json.dump(summ, open(sp, "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in summ.items() if k != "config"}, indent=1, default=str))


if __name__ == "__main__":
    main()
