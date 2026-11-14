"""Round 10, track final-runs, F4 (plan 5e.1): the mu check.

Regime B's mu on the HEST and corpus tasks is mu_J, the donor mean over the spots joined to nuclear morphology, because
F2.load (round 4's Q2.load for the HEST tasks, which keeps rows with `joined`; corpus_data's jn mask for the corpus
tasks) loads only those spots. F2's cluster values carry mu over all of a donor's spots. This module measures the gap
and whether it changes F3's design conclusions (F3 decision file, section 2.1).

Modes
  means <box_config_dir> <out>   parts 1 and 2. For every F3 box config whose population is a HEST or corpus mu
                                 population (theta2_kind 'mean', task not ACS_STATES): (1) the all-spot donor means of
                                 y and f, read from the prediction file with pandas, against the committed cluster
                                 values' mu rows; (2) mu_J through F2.load and round5_ppi_e3_twolevel.build, as the
                                 regcomp and box units formed it, and mu - mu_J per gene, with the between-donor SD of
                                 the all-spot donor means. Anchor: on CCRCC uni_v2 log1p, max |zbar - z| equals F3's
                                 regcomp_mu_check value 0.1332702393296752 exactly.
  regcomp <config.json> <out>    part 3: round10_final_runs_f3_regcomp's run on all spots (F2.load and E3.build replaced
                                 for the mean kind by load_all and build_mean, the same TL.prepare call E3.build makes
                                 for the mean kind). Anchor: every T built has zbar equal to the all-spot cluster values
                                 within 1e-10 relative (mu_allspot_anchor.json).
  box <config.json> <out>        part 3: round10_final_runs_f3_box's run on all spots, same replacement and anchor.
  compare <config.json> <out>    part 3: the all-spot rows against the committed mu_J rows, with the thresholds of plan
                                 5e.1 (coverage 0.01, width ratio B/A 0.02 relative, required m one grid step).
Writes a summary JSON first, then the tables.
"""
import glob, json, os, sys, time
import numpy as np, pandas as pd

CRIT_REL = 1e-10
ANCHOR_ZBAR = 0.1332702393296752


def pop_frame(pop):
    """Prediction file, y and f prefixes and donor column of a population, as F2.load reads it."""
    if pop["source"] == "corpus":
        return pd.read_parquet(pop["path"]), pop["y_prefix"], pop["f_prefix"], pop.get("donor_col", "donor_id"), True
    return pd.read_parquet(pop["parquet"]), "y__", "f__", "donor_id", False


def load_all(pop):
    """F2.load's dictionary built from every spot (no joined filter). m and neo are not used by the mean kind."""
    import round4_ppi_q2_masking as Q2
    Q2.THETA2_KIND = pop.get("theta2_kind", "neo_minus_stroma")
    if Q2.THETA2_KIND != "mean":
        raise SystemExit("load_all serves the mean kind only")
    df, yp, fp, dcol, as_str = pop_frame(pop)
    genes = [c[len(yp):] for c in df.columns if c.startswith(yp)]
    Y = df[[yp + g for g in genes]].to_numpy(np.float64)
    P = df[[fp + g for g in genes]].to_numpy(np.float64)
    did = df[dcol].astype(str).to_numpy(object) if as_str else df[dcol].to_numpy(object)
    donors = np.array(sorted(set(did.tolist())), dtype=object)
    didx = np.searchsorted(donors, did)
    order = np.argsort(didx, kind="stable")
    bounds = np.searchsorted(didx[order], np.arange(len(donors) + 1))
    n = len(didx)
    return dict(genes=genes, Y=Y, P=P, m=np.zeros(n), neo=np.full(n, np.nan), donors=donors, didx=didx,
                by_donor=[order[bounds[g]:bounds[g + 1]] for g in range(len(donors))])


BUILT = []


def build_mean(data, vtag, arm, srs_theta2=False):
    """E3.build's mean branch alone: TL.prepare(Y, P, ones, didx, G, 'mean', None, ones)."""
    import round4_ppi_q2_masking as Q2
    import round5_ppi_twolevel as TL
    if Q2.THETA2_KIND != "mean":
        raise SystemExit("build_mean serves the mean kind only")
    G = len(data["donors"])
    T = TL.prepare(data["Y"], data["P"], np.ones(len(data["didx"])), data["didx"], G, "mean", None, np.ones(G, bool))
    BUILT.append(dict(donors=[str(d) for d in data["donors"]], genes=list(data["genes"]), zbar=np.asarray(T["zbar"], float),
                      n_units=int(len(data["didx"]))))
    return {"theta2": T}


def cv_mu(path, task, encoder, scale):
    cv = pd.read_parquet(path)
    return cv[(cv.task == task) & (cv.encoder == encoder) & (cv.scale == scale) & (cv.estimand == "mu")]


def main_means(cdir, out):
    import round10_final_runs_f2_regimeB as F2
    import round5_ppi_e3_twolevel as E3
    cfgs = sorted(glob.glob(os.path.join(cdir, "f3_box__*.json")))
    summ = dict(started=time.strftime("%Y-%m-%dT%H:%M:%S"), config_dir=cdir, crit_rel=CRIT_REL, populations=[])
    sp = os.path.join(out, "mu_check_summary.json"); json.dump(summ, open(sp, "w"), indent=1)
    prow, grow = [], []
    for p in cfgs:
        cfg = json.load(open(p))
        if not cfg.get("populations"):
            continue
        pop = cfg["populations"][0]
        if pop.get("theta2_kind") != "mean" or pop["task"] == "ACS_STATES":
            continue
        t0 = time.time()
        key = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"])
        df, yp, fp, dcol, as_str = pop_frame(pop)
        genes = [c[len(yp):] for c in df.columns if c.startswith(yp)]
        dd = df[dcol].astype(str)
        Yd = df[[yp + g for g in genes]]
        Fd = df[[fp + g for g in genes]]
        nonfinite = int((~np.isfinite(Yd.to_numpy(float))).sum() + (~np.isfinite(Fd.to_numpy(float))).sum())
        Ay = Yd.groupby(dd).mean(); Af = Fd.groupby(dd).mean()
        Ay.columns = genes; Af.columns = genes
        cv = cv_mu(pop["cluster_values"], **key)
        donors = sorted(cv.donor.astype(str).unique().tolist())
        Z = cv.assign(donor=cv.donor.astype(str)).pivot(index="donor", columns="gene", values="z").loc[donors, genes]
        A = Ay.loc[donors, genes]
        rel_y = float((np.abs(A.to_numpy() - Z.to_numpy()) / np.maximum(1e-12, np.abs(Z.to_numpy()))).max())
        rel_f = None
        if "f" in cv.columns:
            Fz = cv.assign(donor=cv.donor.astype(str)).pivot(index="donor", columns="gene", values="f").loc[donors, genes]
            rel_f = float((np.abs(Af.loc[donors, genes].to_numpy() - Fz.to_numpy()) / np.maximum(1e-12, np.abs(Fz.to_numpy()))).max())
        data = F2.load(pop)
        Tset = E3.build(data, pop["vtag"], pop.get("arm", pop["encoder"]))
        T = Tset["theta2"]
        assert T.get("kind") == "mean"
        jd = [str(d) for d in data["donors"]]
        zb = pd.DataFrame(np.asarray(T["zbar"], float), index=jd, columns=list(data["genes"])).loc[donors, genes]
        mu = A.mean(0).to_numpy(); muJ = zb.mean(0).to_numpy()
        tf = np.asarray(T["theta_full"], float)
        tf = pd.Series(tf, index=list(data["genes"])).loc[genes].to_numpy()
        sdb = A.std(0, ddof=1).to_numpy()
        G = len(donors)
        diff = mu - muJ
        std_diff = diff / sdb
        se_diff = diff / (sdb / np.sqrt(G))
        n_all = int(len(df)); n_join = int(len(data["didx"]))
        r = dict(key, G=G, n_spots_all=n_all, n_spots_joined=n_join, share_kept=n_join / n_all, nonfinite_yf=nonfinite,
                 allspot_vs_cv_max_rel_y=rel_y, allspot_vs_cv_max_rel_f=rel_f, allspot_pass=bool(rel_y <= CRIT_REL and (rel_f is None or rel_f <= CRIT_REL)),
                 thetafull_vs_muJ_max_abs=float(np.abs(tf - muJ).max()),
                 zbar_vs_cv_max_abs=float(np.abs(zb.to_numpy() - Z.to_numpy()).max()),
                 abs_std_diff_median=float(np.median(np.abs(std_diff))), abs_std_diff_max=float(np.abs(std_diff).max()),
                 abs_se_diff_median=float(np.median(np.abs(se_diff))), abs_se_diff_max=float(np.abs(se_diff).max()),
                 seconds=round(time.time() - t0, 1))
        if key == dict(task="CCRCC", encoder="uni_v2", scale="log1p"):
            r["anchor_f3_zbar_vs_cv"] = ANCHOR_ZBAR
            r["anchor_pass"] = bool(r["zbar_vs_cv_max_abs"] == ANCHOR_ZBAR)
            summ["anchor"] = dict(value=r["zbar_vs_cv_max_abs"], reference=ANCHOR_ZBAR, passed=r["anchor_pass"])
        prow.append(r)
        for i, g in enumerate(genes):
            grow.append(dict(key, gene=g, mu=mu[i], mu_J=muJ[i], diff=diff[i], sd_between=sdb[i], std_diff=std_diff[i], se_diff=se_diff[i]))
        summ["populations"].append({k: r[k] for k in ("task", "encoder", "scale", "allspot_pass", "abs_std_diff_max")})
        json.dump(summ, open(sp, "w"), indent=1)
        print(json.dumps(r), flush=True)
    P = pd.DataFrame(prow)
    summ["n_populations"] = len(P)
    summ["all_allspot_pass"] = bool(P.allspot_pass.all())
    summ["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(summ, open(sp, "w"), indent=1)
    P.to_csv(os.path.join(out, "mu_check_populations.csv"), index=False)
    pd.DataFrame(grow).to_csv(os.path.join(out, "mu_check_genes.csv.gz"), index=False)
    print(json.dumps({k: v for k, v in summ.items() if k != "populations"}, indent=1))


def patch():
    import round10_final_runs_f2_regimeB as F2
    import round5_ppi_e3_twolevel as E3
    F2.load = load_all
    E3.build = build_mean


def anchor_check(cfg, out):
    rows = []
    for pop, b in zip(cfg["populations"], BUILT):
        cv = cv_mu(pop["cluster_values"], pop["task"], pop["encoder"], pop["scale"])
        Z = cv.assign(donor=cv.donor.astype(str)).pivot(index="donor", columns="gene", values="z").loc[b["donors"], b["genes"]].to_numpy(float)
        rel = float((np.abs(b["zbar"] - Z) / np.maximum(1e-12, np.abs(Z))).max())
        rows.append(dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], n_units=b["n_units"], max_rel=rel, passed=bool(rel <= CRIT_REL)))
    res = dict(builds=len(BUILT), populations=len(cfg["populations"]), rows=rows,
               passed=bool(len(BUILT) == len(cfg["populations"]) and all(r["passed"] for r in rows)))
    json.dump(res, open(os.path.join(out, "mu_allspot_anchor.json"), "w"), indent=1)
    print(json.dumps(res)[:3000], flush=True)
    return res["passed"]


def main_part3(mode, cfgp, out):
    cfg = json.load(open(cfgp))
    patch()
    np.seterr(all="ignore")
    if mode == "regcomp":
        import round10_final_runs_f3_regcomp as M
    else:
        import round10_final_runs_f3_box as M
    M.main_run(cfg, out)
    if not anchor_check(cfg, out):
        raise SystemExit(5)


def _ratio_table(g):
    """Median over genes of regime B's C_fix1 median width over regime A's, paired on (budget, cost, n_L)."""
    a = g[(g.regime == "A") & (g.form == "C_fix1") & (g.interval == "twostage_t|fpc")]
    b = g[(g.regime == "B") & (g.form == "C_fix1") & (g.interval == "regB_t")]
    k = ["budget", "cost", "n_L", "gene"]
    m = a[k + ["median_width"]].merge(b[k + ["median_width"]], on=k, suffixes=("_A", "_B"))
    m["r"] = m.median_width_B / m.median_width_A
    return m.groupby(["budget", "cost", "n_L"]).r.median().rename("wr_BA").reset_index()


def main_compare(cfgp, out):
    cfg = json.load(open(cfgp))
    res = dict(config=cfg, thresholds=dict(coverage=0.01, width_ratio_rel=0.02, m_steps=1))
    sp = os.path.join(out, "mu_part3_compare.json"); json.dump(res, open(sp, "w"), indent=1)
    def cells(dirs, name):
        return pd.concat([pd.read_csv(os.path.join(d, name)) for d in dirs], ignore_index=True)
    def genes(dirs, name):
        return pd.concat([pd.read_parquet(os.path.join(d, name)) for d in dirs], ignore_index=True)
    K = ["regime", "budget", "cost", "n_L", "m", "interval", "estimator", "estimand"]
    cn, co = cells(cfg["regcomp_new"], "regcomp_cells.csv"), cells(cfg["regcomp_old"], "regcomp_cells.csv")
    co = co[co.estimand == "mu"]; cn = cn[cn.estimand == "mu"]
    mc = cn.merge(co, on=K, suffixes=("_all", "_J"))
    mc["d_cov"] = mc.coverage_median_all - mc.coverage_median_J
    gn, go = genes(cfg["regcomp_new"], "regcomp_genes.parquet"), genes(cfg["regcomp_old"], "regcomp_genes.parquet")
    go = go[go.estimand == "mu"]; gn = gn[gn.estimand == "mu"]
    wr = _ratio_table(gn).merge(_ratio_table(go), on=["budget", "cost", "n_L"], suffixes=("_all", "_J"))
    wr["rel"] = wr.wr_BA_all / wr.wr_BA_J - 1.0
    bn, bo = pd.read_csv(os.path.join(cfg["box_new"], "box_coverage_cells.csv")), pd.read_csv(os.path.join(cfg["box_old"], "box_coverage_cells.csv"))
    bc = bn.merge(bo, on=["m", "interval", "estimator", "estimand"], suffixes=("_all", "_J"))
    bc["d_cov"] = bc.coverage_median_all - bc.coverage_median_J
    gb, go2 = pd.read_csv(os.path.join(cfg["box_new"], "box_genes.csv")), pd.read_csv(os.path.join(cfg["box_old"], "box_genes.csv"))
    mrows = []
    for lam, d in gb.groupby("lambda"):
        e = go2[go2["lambda"] == lam]
        for col in ("m_min_B_bounded", "m_min_B_unbounded"):
            a, b = float(np.nanmedian(d[col])), float(np.nanmedian(e[col]))
            mrows.append(dict(lam=lam, column=col, median_all=a, median_J=b,
                              steps=float(abs(np.searchsorted(cfg["m_grid_box"], a) - np.searchsorted(cfg["m_grid_box"], b)))))
    M = pd.DataFrame(mrows)
    res.update(regcomp_cells=len(mc), regcomp_max_abs_dcov=float(mc.d_cov.abs().max()),
               wr_cells=len(wr), wr_max_abs_rel=float(wr.rel.abs().max()),
               box_cells=len(bc), box_max_abs_dcov=float(bc.d_cov.abs().max()),
               box_m_max_steps=float(M.steps.max()))
    res["pass_coverage"] = bool(max(res["regcomp_max_abs_dcov"], res["box_max_abs_dcov"]) <= 0.01)
    res["pass_width_ratio"] = bool(res["wr_max_abs_rel"] <= 0.02)
    res["pass_m"] = bool(res["box_m_max_steps"] <= 1)
    res["passed"] = bool(res["pass_coverage"] and res["pass_width_ratio"] and res["pass_m"])
    json.dump(res, open(sp, "w"), indent=1, default=str)
    mc.to_csv(os.path.join(out, "mu_part3_regcomp_cells.csv"), index=False)
    wr.to_csv(os.path.join(out, "mu_part3_width_ratio.csv"), index=False)
    bc.to_csv(os.path.join(out, "mu_part3_box_cells.csv"), index=False)
    M.to_csv(os.path.join(out, "mu_part3_box_m.csv"), index=False)
    print(json.dumps({k: v for k, v in res.items() if k != "config"}, indent=1, default=str))


def main():
    mode = sys.argv[1]
    if mode == "means":
        cdir, out = sys.argv[2:4]; os.makedirs(out, exist_ok=True); main_means(cdir, out)
    elif mode in ("regcomp", "box"):
        cfgp, out = sys.argv[2:4]; os.makedirs(out, exist_ok=True); main_part3(mode, cfgp, out)
    elif mode == "compare":
        cfgp, out = sys.argv[2:4]; os.makedirs(out, exist_ok=True); main_compare(cfgp, out)
    else:
        raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    main()
