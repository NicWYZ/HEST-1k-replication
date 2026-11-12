"""Round 10, track final-runs, stage F3, open point 2 (plan section 5d.6, item 2), second job: the within-donor
heterogeneity of the real regime B populations, beside the toy's.

For every population of the named F2 regime B configs, the data are loaded and the estimands built exactly as F2's
regime B script does (round10_final_runs_f2_regimeB.load, round5_ppi_e3_twolevel.build), and for theta3 the script
tabulates per donor g:
  - n_units M_g and whether theta3 is valid in the donor;
  - mean, sd, skewness and excess kurtosis of m_std (data['m']) within the donor;
  - sd, skewness and excess kurtosis of the theta3 weight w within the donor;
  - for the theta3 unit contribution u_i = (w_i - abar_g)(r_i - rbar_g), with r = y - yhat (coefficient 1, 'fix1') and
    r = y (coefficient 0, 'classical'), the within-donor sd, skewness and excess kurtosis per gene, summarised over genes
    by the median, 10th and 90th percentiles.
Moments are population moments of the donor's units (divisor M_g); excess kurtosis is m4 / m2^2 - 3. abar_g and rbar_g
are the donor's means over all its units. The same table is computed for every theta3 population of the toy grid
(round10_final_runs_f3_toy.population), one row per toy cluster, with m_std left empty (the toy has none; w is its
analogue).
Checks: the donor means of theta3's linear form against F2's cluster values (F2's check_cluster_values, criterion
max_rel < 1e-9, as F2's regime B used), and G and n_units against the F2 regime B unit's regimeB_summary.json.

usage: round10_final_runs_f3_heterogeneity.py <config.json> <out_dir>
config: {configs: [F2 regime B config file names], configs_root: directory holding them (relative to the working
        directory; the job extracts them from the commit), regimeB_dir: <BASE>/F2/regimeB, toy: true|false}
Writes heterogeneity_summary.json first, then f3_heterogeneity_donors.csv and f3_heterogeneity_by_population.csv.
"""
import json, os, sys, time
import numpy as np, pandas as pd
import round5_ppi_e3_twolevel as E3
import round10_final_runs_f2_regimeB as RB

STATS = ("sd", "skew", "exkurt")


def seg_moments(x, didx, G):
    """x (n,) or (n, k). Per cluster: count, mean, sd, skewness, excess kurtosis (population moments)."""
    x = np.asarray(x, float)
    one = x.ndim == 1
    X = x[:, None] if one else x
    o = np.argsort(didx, kind="stable"); d = didx[o]; X = X[o]
    starts = np.searchsorted(d, np.arange(G)); n = np.bincount(d, minlength=G).astype(float)
    ok = n > 0
    st = starts[ok]
    def rs(v):
        out = np.full((G, X.shape[1]), np.nan); out[ok] = np.add.reduceat(v, st, axis=0); return out
    mu = rs(X) / n[:, None]
    c = X - mu[d]
    m2, m3, m4 = rs(c ** 2) / n[:, None], rs(c ** 3) / n[:, None], rs(c ** 4) / n[:, None]
    with np.errstate(invalid="ignore", divide="ignore"):
        pos = m2 > 0
        sd = np.sqrt(m2)
        skew = np.where(pos, m3 / np.where(pos, m2, 1.0) ** 1.5, np.nan)
        exk = np.where(pos, m4 / np.where(pos, m2, 1.0) ** 2 - 3.0, np.nan)
    res = dict(n=n, mean=mu, sd=sd, skew=skew, exkurt=exk)
    if one:
        res = {k: (v[:, 0] if v.ndim == 2 else v) for k, v in res.items()}
    return res


def donor_table(T, mstd, keys, donors):
    """One row per donor of a theta3 T (TL.prepare output)."""
    G, didx = T["G"], T["didx"]
    rows = []
    wm = seg_moments(T["w"], didx, G)
    mm = seg_moments(mstd, didx, G) if mstd is not None else None
    wc = (T["w"] - T["abar"][didx])[:, None]
    U = {}
    for lab, r in (("fix1", T["y"] - T["yhat"]), ("classical", T["y"])):
        rb = seg_moments(r, didx, G)["mean"]
        U[lab] = seg_moments(wc * (r - rb[didx]), didx, G)
    for g in range(G):
        row = dict(keys, donor=str(donors[g]), valid=bool(T["valid"][g]), n_units=int(wm["n"][g]), n_genes=int(T["ng"]))
        for s in ("mean",) + STATS:
            row[f"m_std_{s}"] = float(mm[s][g]) if mm is not None else np.nan
        for s in STATS:
            row[f"w_{s}"] = float(wm[s][g])
        for lab, u in U.items():
            for s in STATS:
                v = u[s][g]
                v = v[np.isfinite(v)]
                row[f"u_{lab}_{s}_med"] = float(np.median(v)) if v.size else np.nan
                row[f"u_{lab}_{s}_q10"] = float(np.quantile(v, 0.1)) if v.size else np.nan
                row[f"u_{lab}_{s}_q90"] = float(np.quantile(v, 0.9)) if v.size else np.nan
        rows.append(row)
    return rows


def f2_summary_match(rbdir, unit, pop, info):
    p = os.path.join(rbdir, unit, "regimeB_summary.json")
    if not os.path.exists(p):
        return dict(found=False)
    s = json.load(open(p))
    for q in s.get("populations", []):
        if q["task"] == pop["task"] and q["encoder"] == pop["encoder"] and q["scale"] == pop["scale"]:
            return dict(found=True, G_f2=q["G"], n_units_f2=q["n_units"], n_genes_f2=q["n_genes"],
                        match=bool(q["G"] == info["G"] and q["n_units"] == info["n_units"] and q["n_genes"] == info["n_genes"]))
    return dict(found=False)


def by_population(d):
    v = d[d.valid]
    cols = [c for c in d.columns if c.startswith(("m_std_", "w_", "u_")) and not c.endswith(("_q10", "_q90"))]
    out = []
    for k, g in v.groupby(["source", "task", "encoder", "scale"], sort=False):
        r = dict(zip(["source", "task", "encoder", "scale"], k), donors_valid=len(g), n_units_min=int(g.n_units.min()),
                 n_units_median=float(g.n_units.median()), n_units_max=int(g.n_units.max()))
        for c in cols:
            x = g[c].to_numpy(float); x = x[np.isfinite(x)]
            r[c + "__donor_median"] = float(np.median(x)) if x.size else np.nan
            r[c + "__donor_q10"] = float(np.quantile(x, 0.1)) if x.size else np.nan
            r[c + "__donor_q90"] = float(np.quantile(x, 0.9)) if x.size else np.nan
        out.append(r)
    return pd.DataFrame(out)


def main():
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    sp = os.path.join(out, "heterogeneity_summary.json")
    summ = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"), populations=[])
    json.dump(summ, open(sp, "w"), indent=1)
    rows = []
    for cp in cfg["configs"]:
        c = json.load(open(os.path.join(cfg.get("configs_root", ""), cp)))
        for pop in c.get("populations", []):
            t0 = time.time()
            data = RB.load(pop)
            Tset = E3.build(data, pop["vtag"], pop.get("arm", pop["encoder"]))
            info = dict(unit=c["unit"], task=pop["task"], encoder=pop["encoder"], scale=pop["scale"],
                        G=len(data["donors"]), n_units=int(len(data["didx"])), n_genes=len(data["genes"]))
            if "theta3" not in Tset:
                info["skipped"] = "theta3 not built"; summ["populations"].append(info); continue
            T = Tset["theta3"]
            keys = dict(source="real", task=pop["task"], encoder=pop["encoder"], scale=pop["scale"])
            if pop.get("cluster_values"):
                info["cv_check"] = RB.check_cluster_values(T, data, pop["cluster_values"], keys, "theta3")
            info["f2_summary"] = f2_summary_match(cfg["regimeB_dir"], c["unit"].replace("regimeB__", ""), pop, info)
            rows += donor_table(T, data["m"], keys, data["donors"])
            info["G_valid"] = int(T["valid"].sum()); info["seconds"] = round(time.time() - t0, 1)
            summ["populations"].append(info)
            json.dump(summ, open(sp, "w"), indent=1, default=str)
            print(json.dumps({k: v for k, v in info.items()}, default=str), flush=True)
            del data, Tset, T
    if cfg.get("toy", True):
        import round5_ppi_twolevel as TL
        import round10_final_runs_f3_toy as TOY
        for Gs in TOY.GS_GRID:
            for M0 in TOY.M0_GRID:
                y, yhat, w, didx = TOY.population("theta3", M0, Gs)
                T = TL.prepare(y, yhat, w, didx, Gs + 1, "theta3")
                names = [f"s{g}" for g in range(Gs)] + ["full"]
                rows += donor_table(T, None, dict(source="toy", task="toy", encoder="toy", scale=f"M0{M0}_Gs{Gs}"), names)
    d = pd.DataFrame(rows)
    pops = [p for p in summ["populations"] if "cv_check" in p]
    rel = [p["cv_check"].get("max_rel", np.nan) for p in pops]
    summ.update(rows=len(d), populations_n=len(summ["populations"]),
                cv_max_rel=float(np.nanmax(rel)) if len(rel) else np.nan,
                cv_all_matched=bool(all(p["cv_check"].get("n_common", 0) == p.get("G_valid", -1) for p in pops)),
                f2_summary_all_match=bool(all(p.get("f2_summary", {}).get("match", False) for p in summ["populations"]
                                              if "skipped" not in p)),
                finished=time.strftime("%Y-%m-%dT%H:%M:%S"))
    summ["passed"] = bool(summ["cv_max_rel"] < 1e-9 and summ["f2_summary_all_match"])
    json.dump(summ, open(sp, "w"), indent=1, default=str)
    by_population(d).to_csv(os.path.join(out, "f3_heterogeneity_by_population.csv"), index=False)
    d.to_csv(os.path.join(out, "f3_heterogeneity_donors.csv"), index=False)
    print(json.dumps({k: v for k, v in summ.items() if k not in ("config", "populations")}, indent=1, default=str))


if __name__ == "__main__":
    main()
