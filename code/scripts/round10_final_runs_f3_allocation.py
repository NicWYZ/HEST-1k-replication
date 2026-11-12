"""Round 10, track final-runs, F3.3 (iii): the allocation formula from the final components (plan, section 5d.3 (iii)).

Modes
  anchor_check <new_csv> <ref_csv> <out_json>
      Compares round 5's e5_allocation.csv, as rerun by round5_ppi_e5_allocation.py unchanged on round 5's committed
      CSVs, with the committed file: every row and numeric column, and the named row CCRCC, uni_v2, n_L 8.
  run <config.json> <out_dir>
      For each population (task, encoder, scale) of the config, loaded as F2's regime B driver loads it
      (round10_final_runs_f2_regimeB.load, then round5_ppi_e3_twolevel.build), per estimand: theta3, theta2 (round 3's
      neoplastic and stromal groups) and mu (round 5's 'mean' kind, the same loaded units):
        A            the between-donor variance of the cluster values zbar over the valid donors (ddof 1), as round 5
        B0, B1       round 5's form C within-donor variances of the unit contributions (per-donor variance, ddof 1,
                     averaged over the valid donors, with round 5's ((M - 1)/M)^2 factor for theta3), of y (B0) and of
                     y - f (B1), that is the coefficient fixed at 1
        1 - R2_w     B1 / B0;   1 - R2_c = Var_g(zbar - fbar) / Var_g(zbar)
        m_star_cd<c> sqrt(B0 c / A), as round5_ppi_e3_twolevel.components_part computes it (the plan's text writes
                     sqrt(B0/(A c)); the code, which the anchor reproduces, has c in the numerator)
        rho_c(n_L)   the ratio of the median over genes of F2 regime A's empirical variances (sd^2) of the fixed
                     coefficient and of the classical estimator (arms fix1 and classical, variance fpc) at n_L whole
                     clusters, from regimeA_cells.parquet
        m_star_PP_cd<c>(n_L) = median_g m_star_cd<c> * sqrt(median_g (1 - R2_w) / rho_c(n_L)), round 5's E5 rule.
      Round 5's own components (clipped coefficients) are computed beside by components_part on the same data. Where
      the config names round 5's e3_components.csv, its rows for the same task, arm, estimand and gene are compared.
      Gene scopes: 'all', and for LUNG_XENIUM also 'r9_42' (zlib.crc32(gene) % 7 == 0).
Writes allocation_summary.json first, then allocation_rows.csv, allocation_genes.parquet and r5_components_check.csv.
"""
import json, os, sys, time, zlib, traceback
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
import round4_ppi_q2_masking as Q2
import round5_ppi_e3_twolevel as E3
import round10_final_runs_f2_regimeB as RB

COSTS = (10.0, 100.0, 1000.0)
R9_TASKS = ("LUNG_XENIUM",)
GSCHEMA = pa.schema([(k, pa.string()) for k in ("task", "encoder", "scale", "estimand", "gene")] +
                    [("G", pa.int64())] + [(k, pa.float64()) for k in
                    ("A", "B0", "B1", "one_minus_R2_w", "one_minus_R2_c", "R2_w_r5clip", "R2_c_r5clip",
                     "mstar_cd10", "mstar_cd100", "mstar_cd1000")])


def scopes(task, genes):
    out = {"all": list(genes)}
    if task in R9_TASKS:
        out["r9_42"] = [g for g in genes if zlib.crc32(g.encode()) % 7 == 0]
    return out


def fixed_components(T):
    """Round 5's components_part, form C, with the within coefficient fixed at 1 (lamC = 1) and R2_c from z - f."""
    ok = T["valid"]; didx = T["didx"]; G = T["G"]
    zb, fb = T["zbar"][ok], T["fbar"][ok]
    A = zb.var(0, ddof=1)
    omc = (zb - fb).var(0, ddof=1) / np.where(A > 0, A, np.nan)
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
        return np.where(cnt[:, None] > 1, (q - s ** 2 / np.maximum(cnt, 1)[:, None]) / np.maximum(cnt - 1, 1)[:, None], 0)

    y, yh, w = T["y"], T["yhat"], T["w"][:, None]
    if T["kind"] == "theta3":
        wc = w - T["abar"][didx][:, None]
        ym = np.zeros((G, y.shape[1])); np.add.at(ym, didx, y); ym /= T["M"][:, None]
        hm = np.zeros((G, y.shape[1])); np.add.at(hm, didx, yh); hm /= T["M"][:, None]
        uy, uh = wc * (y - ym[didx]), wc * (yh - hm[didx])
        k2 = (((T["M"] - 1) / T["M"]) ** 2)[:, None]
        B0, B1 = (k2 * within(uy))[ok].mean(0), (k2 * within(uy - uh))[ok].mean(0)
    elif T["kind"] == "theta2":
        c0, c1 = within(y), within(y - yh)
        c0 = c0.reshape(G, 2, -1).sum(1) * 2; c1 = c1.reshape(G, 2, -1).sum(1) * 2
        B0, B1 = c0[ok].mean(0), c1[ok].mean(0)
    else:
        B0, B1 = within(y)[ok].mean(0), within(y - yh)[ok].mean(0)
    return A, B0, B1, omc


def regimeA_rho(paths):
    parts = []
    for p in paths:
        t = pq.read_table(p, columns=["task", "encoder", "scale", "estimand", "gene", "n", "arm", "variance", "sd"],
                          filters=[("arm", "in", ["fix1", "classical"]), ("variance", "=", "fpc")])
        parts.append(t.to_pandas())
    d = pd.concat(parts, ignore_index=True)
    d["v"] = d["sd"] ** 2
    return d


def anchor_check(new_csv, ref_csv, out_json):
    a, b = pd.read_csv(new_csv), pd.read_csv(ref_csv)
    keys = ["vtag", "arm", "form", "estimand", "n_L"]
    m = a.merge(b, on=keys, how="outer", suffixes=("", "_ref"), indicator=True)
    num = [c for c in b.columns if c not in keys and pd.api.types.is_numeric_dtype(b[c])]
    dmax = {}
    for c in num:
        x, y = m[c].to_numpy(float), m[c + "_ref"].to_numpy(float)
        both = np.isfinite(x) & np.isfinite(y)
        nan_mismatch = int((np.isfinite(x) != np.isfinite(y)).sum())
        dmax[c] = dict(max_abs=float(np.abs(x - y)[both].max()) if both.any() else 0.0, nan_mismatch=nan_mismatch)
    r = m[(m.vtag == "CCRCC") & (m.arm == "uni_v2") & (m.n_L == 8)].iloc[0]
    out = dict(rows_new=len(a), rows_ref=len(b), rows_both=int((m["_merge"] == "both").sum()), max_diff=dmax,
               named=dict(m_star_PP_cd100=float(r.m_star_PP_cd100), m_star_PP_cd100_ref=float(r.m_star_PP_cd100_ref),
                          rho_c=float(r.rho_c), one_minus_R2_w=float(r.one_minus_R2_w),
                          m_star_classical_cd100=float(r.m_star_classical_cd100)))
    out["exact"] = bool(out["rows_both"] == len(b) == len(a) and all(v["max_abs"] == 0 and v["nan_mismatch"] == 0
                                                                    for v in dmax.values()))
    json.dump(out, open(out_json, "w"), indent=1)
    print(json.dumps(out, indent=1))
    return 0 if out["exact"] else 1


def run(cfg_path, out):
    cfg = json.load(open(cfg_path)); os.makedirs(out, exist_ok=True)
    summ = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"), populations=[])
    sp = os.path.join(out, "allocation_summary.json"); json.dump(summ, open(sp, "w"), indent=1)
    rA = regimeA_rho(cfg["regimeA_cells"])
    ref = pd.read_csv(cfg["r5_components_ref"].replace("__OUT__", out)) if cfg.get("r5_components_ref") else None
    rows, grows, chk = [], [], []
    for pop in cfg["populations"]:
        t0 = time.time()
        info = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"])
        summ["populations"].append(info)
        try:
            data = RB.load(pop)
        except Exception as e:
            info["error"] = f"load failed: {type(e).__name__}: {e}"; info["traceback"] = traceback.format_exc()[-1500:]
            json.dump(summ, open(sp, "w"), indent=1, default=str); continue
        info.update(G=len(data["donors"]), n_units=int(len(data["didx"])), n_genes=len(data["genes"]), estimands={})
        genes = list(data["genes"])
        kinds = [("neo_minus_stroma", ("theta3", "theta2"))] if pop.get("theta2_kind", "neo_minus_stroma") != "mean" else []
        kinds.append(("mean", ("theta3", "theta2") if pop.get("theta2_kind") == "mean" else ("theta2",)))
        for kind, ests in kinds:
            Q2.THETA2_KIND = kind
            Tset = E3.build(data, pop["vtag"], pop.get("arm", pop["encoder"]))
            r5dir = os.path.join(out, "r5_components", f"{pop['task']}__{pop['encoder']}__{pop['scale']}__{kind}")
            os.makedirs(r5dir, exist_ok=True)
            E3.components_part(data, Tset, pop["vtag"], pop.get("arm", pop["encoder"]), r5dir)
            r5c = pd.read_csv(os.path.join(r5dir, f"e3_components__{pop['vtag']}__{pop.get('arm', pop['encoder'])}.csv"))
            for est in ests:
                if est not in Tset:
                    continue
                T = Tset[est]
                lab = "mu" if T["kind"] == "mean" else est
                if lab in info["estimands"] or lab not in pop.get("estimands_out", ("theta3", "theta2", "mu")):
                    continue
                A, B0, B1, omc = fixed_components(T)
                G = int(T["valid"].sum())
                omw = B1 / np.where(B0 > 0, B0, np.nan)
                ms = {c: np.where(A > 0, np.sqrt(B0 / np.where(A > 0, A, np.nan) * c), np.nan) for c in COSTS}
                rc = r5c[(r5c.estimand == est) & (r5c.form == "C")].set_index("gene").reindex(genes)
                # round 5's classical components do not depend on the coefficient: B_classical and A must agree
                dA = float(np.nanmax(np.abs(rc["A"].to_numpy(float) - A)))
                dB = float(np.nanmax(np.abs(rc["B_classical"].to_numpy(float) - B0)))
                keys = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], estimand=lab)
                cvi = RB.check_cluster_values(T, data, pop["cluster_values"], keys, lab) if pop.get("cluster_values") else {}
                info["estimands"][lab] = dict(G_valid=G, d_A_vs_components_part=dA, d_B0_vs_components_part=dB, cv_check=cvi)
                if ref is not None and T["kind"] != "mean":
                    rr = ref[(ref.vtag == pop["vtag"]) & (ref.arm == pop.get("arm", pop["encoder"])) & (ref.estimand == est)
                             & (ref.form == "C")].set_index("gene").reindex(genes)
                    if rr["A"].notna().any():
                        for col, mine in (("A", A), ("B_classical", B0), ("R2_c", rc["R2_c"].to_numpy(float)),
                                          ("R2_w", rc["R2_w"].to_numpy(float)), ("B_ppi", rc["B_ppi"].to_numpy(float))):
                            x = rr[col].to_numpy(float); fin = np.isfinite(x) & np.isfinite(mine)
                            chk.append(dict(**keys, column=col, n_genes=int(fin.sum()),
                                            max_abs=float(np.abs(x - mine)[fin].max()) if fin.any() else np.nan,
                                            max_rel=float((np.abs(x - mine) / np.maximum(np.abs(x), 1e-300))[fin].max()) if fin.any() else np.nan))
                for j, g in enumerate(genes):
                    grows.append(dict(**keys, gene=g, G=G, A=float(A[j]), B0=float(B0[j]), B1=float(B1[j]),
                                      one_minus_R2_w=float(omw[j]), one_minus_R2_c=float(omc[j]),
                                      R2_w_r5clip=float(rc["R2_w"].iloc[j]), R2_c_r5clip=float(rc["R2_c"].iloc[j]),
                                      **{f"mstar_cd{c:g}": float(ms[c][j]) for c in COSTS}))
                ra = rA[(rA.task == pop["task"]) & (rA.encoder == pop["encoder"]) & (rA.scale == pop["scale"]) & (rA.estimand == lab)]
                for sc, gl in scopes(pop["task"], genes).items():
                    ix = [genes.index(g) for g in gl]
                    w_, c_ = float(np.nanmedian(omw[ix])), float(np.nanmedian(omc[ix]))
                    msm = {c: float(np.nanmedian(ms[c][ix])) for c in COSTS}
                    r_sc = ra[ra.gene.isin(gl)]
                    nls = sorted(r_sc.n.unique()) or [np.nan]
                    for nL in nls:
                        x = r_sc[r_sc.n == nL]
                        vf = x[x.arm == "fix1"].v.median(); vc = x[x.arm == "classical"].v.median()
                        rho = float(vf / vc) if (len(x) and vc > 0) else np.nan
                        row = dict(**keys, gene_scope=sc, n_L=nL, G=G, n_genes=len(ix),
                                   n_genes_regimeA=int(x[x.arm == "fix1"].gene.nunique()) if len(x) else 0,
                                   one_minus_R2_w=w_, one_minus_R2_c=c_, rho_c=rho,
                                   one_minus_R2_w_r5clip=float(1 - np.nanmedian(rc["R2_w"].to_numpy(float)[ix])),
                                   one_minus_R2_c_r5clip=float(1 - np.nanmedian(rc["R2_c"].to_numpy(float)[ix])))
                        for c in COSTS:
                            row[f"m_star_classical_cd{c:g}"] = msm[c]
                            row[f"m_star_PP_cd{c:g}"] = msm[c] * np.sqrt(w_ / rho) if (rho > 0 and w_ >= 0) else np.nan
                        row["ratio_PP_over_classical"] = float(np.sqrt(w_ / rho)) if (rho > 0 and w_ >= 0) else np.nan
                        rows.append(row)
        info["seconds"] = round(time.time() - t0, 1)
        print(json.dumps(dict(pop=f"{pop['task']}|{pop['encoder']}|{pop['scale']}", s=info["seconds"])), flush=True)
        json.dump(summ, open(sp, "w"), indent=1, default=str)
    Q2.THETA2_KIND = "neo_minus_stroma"
    summ["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    summ["n_rows"] = len(rows); summ["n_gene_rows"] = len(grows)
    summ["r5_check_max_rel"] = float(pd.DataFrame(chk)["max_rel"].max()) if chk else None
    summ["n_errors"] = sum(1 for p in summ["populations"] if "error" in p)
    json.dump(summ, open(sp, "w"), indent=1, default=str)
    pd.DataFrame(rows).to_csv(os.path.join(out, "allocation_rows.csv"), index=False)
    pd.DataFrame(chk).to_csv(os.path.join(out, "r5_components_check.csv"), index=False)
    pq.write_table(pa.Table.from_pandas(pd.DataFrame(grows, columns=GSCHEMA.names), schema=GSCHEMA, preserve_index=False),
                   os.path.join(out, "allocation_genes.parquet"))
    print(json.dumps({k: v for k, v in summ.items() if k not in ("config", "populations")}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "anchor_check":
        raise SystemExit(anchor_check(*sys.argv[2:5]))
    raise SystemExit(run(sys.argv[2], sys.argv[3]))
