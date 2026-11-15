"""Round 10, track final-runs, F2.4: regime B with form C (plan, section 5.4).

Every valid cluster is labelled and m units are drawn without replacement within each cluster (stratified by group
for theta2, as round 5's E3 draws them). For each draw three forms of round 5's two-level estimator in form C run on
the same units: the coefficient fixed at 1 ('C_fix1'), round 5's cross-fitted coefficient ('C_ppi') and the classical
form ('C_classical'), through round10_final_runs_estimators.regime_b_formC, which calls round5_ppi_twolevel.estimate
(the fixed coefficient through its one inserted line). The draws and seeds are round 5's E3 `regb` part's
(round5_ppi_e3_twolevel.units with 'r5e3u|<vtag>|<tag>|d<d>|<est>', cross-fit halves 'r5e3x|...', tag
'regb|B|Bnan|unit|nL<G>|m<m>'), so the first 200 draws of a cell are round 5's draws, continued to R.

Data. HEST tasks and ACS through round 5's load_arm on the prediction parquets round 5's E3 read; corpus tasks through
corpus_data(), which builds the same dictionary from a corpus prediction file and the option (b) spot features, with
round 10's cluster-value joining rule (spots with at least one nucleus and finite area and group share; m_std the
area standardised over them with ddof 0). round5_ppi_e3_twolevel.build then forms the estimands with round 3's design
constants. Where the config names cluster values, the cluster means of the estimand's linear form (TL.prepare's zbar)
are compared with the cluster values z of regime A for the same task, encoder, scale and estimand.

usage: round10_final_runs_f2_regimeB.py <config.json> <out_dir>
config: populations [{task, vtag, encoder, scale, source 'r5' (parquet, arm) or 'corpus' (path, morph_path, y_prefix,
        f_prefix), theta2_kind, estimands, cluster_values (optional)}], m_grid, R, label; optional anchor
        {vtag, arm, parquet, estimand, m_list, draws, ref_csv, named: {m, estimator}}.
Writes regimeB_summary.json first, then regimeB_cells.csv (round 5's summary columns), regimeB_genes.parquet.
"""
import json, os, sys, time
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
from scipy import stats
import round4_ppi_estimator as R4
import round4_ppi_q2_masking as Q2
import round5_ppi_e3_twolevel as E3
from round5_ppi_e2_regimeB import load_arm
import round10_final_runs_estimators as E

FORMS = (("C_fix1", "fixed1"), ("C_ppi", "crossfit"), ("C_classical", "classical"))
ALPHA = 0.10
GSCHEMA = pa.schema([("task", pa.string()), ("encoder", pa.string()), ("scale", pa.string()), ("estimand", pa.string()),
                     ("gene", pa.string()), ("G", pa.int64()), ("m", pa.int64()), ("form", pa.string()), ("R", pa.int64()),
                     ("theta", pa.float64()), ("bias", pa.float64()), ("mcse_bias", pa.float64()), ("sd", pa.float64()),
                     ("rmse", pa.float64()), ("coverage", pa.float64()), ("coverage_se", pa.float64()),
                     ("frac_no_interval", pa.float64()), ("mean_width", pa.float64()), ("median_width", pa.float64()),
                     ("ev_over_var", pa.float64()), ("frac_v_neg", pa.float64()), ("df_mean", pa.float64())])


def corpus_data(path, morph_path, y_prefix, f_prefix, donor_col="donor_id"):
    df = pd.read_parquet(path)
    mp = pd.read_parquet(morph_path, columns=["sample_id", "barcode", "n_nuclei", "area_mean", "frac_neoplastic"])
    df = df.merge(mp, on=["sample_id", "barcode"], how="left", validate="one_to_one")
    ar, nf = df["area_mean"].to_numpy(float), df["frac_neoplastic"].to_numpy(float)
    jn = np.isfinite(ar) & np.isfinite(nf) & (df["n_nuclei"].fillna(0).to_numpy() > 0)
    mu, sd = float(ar[jn].mean()), float(ar[jn].std(ddof=0))
    genes = [c[len(y_prefix):] for c in df.columns if c.startswith(y_prefix)]
    Y = df[[y_prefix + g for g in genes]].to_numpy(np.float64)[jn]
    P = df[[f_prefix + g for g in genes]].to_numpy(np.float64)[jn]
    did = df[donor_col].astype(str).to_numpy(object)[jn]
    donors = np.array(sorted(set(did.tolist())), dtype=object)
    didx = np.searchsorted(donors, did)
    order = np.argsort(didx, kind="stable")
    bounds = np.searchsorted(didx[order], np.arange(len(donors) + 1))
    return dict(genes=genes, Y=Y, P=P, m=(ar[jn] - mu) / sd, neo=nf[jn], donors=donors, didx=didx,
                by_donor=[order[bounds[g]:bounds[g + 1]] for g in range(len(donors))])


def load(pop):
    Q2.THETA2_KIND = pop.get("theta2_kind", "neo_minus_stroma")
    if pop["source"] == "corpus":
        return corpus_data(pop["path"], pop["morph_path"], pop["y_prefix"], pop["f_prefix"], pop.get("donor_col", "donor_id"))
    return load_arm(pop["parquet"], pop["arm"], pop["vtag"])


def tag_of(G, m):
    """round5_ppi_e3_twolevel.run_part's cell tag for part regb (budget nan, cost unit, n_L = G)."""
    return f"regb|B|Bnan|unit|nL{G}|m{m}"


def run_cell(data, T, vtag, est, m, R, forms=FORMS, label=None):
    """R draws of one (estimand, m) cell; est names round 5's estimand in the seeds, label the output.
    Returns acc in round 4's format and per-form arrays."""
    label = label or est
    Gall = len(data["donors"]); tag = tag_of(Gall, m)
    Lmask = T["valid"].copy(); acc = {}; arr = {nm: dict(th=[], v=[], df=[]) for nm, _ in forms}
    for d in range(R):
        sel = E3.units(data, T, Lmask, m, E3.rng_of(f"r5e3u|{vtag}|{tag}|d{d}|{est}"))
        seed = f"r5e3x|{vtag}|{tag}|d{d}|{est}"
        for nm, coef in forms:
            o = E.regime_b_formC(T, sel, seed, coef)
            df = np.full(o["theta"].shape, o["df"], dtype=float)
            lo, hi = R4.t_interval(o["theta"], o["var"], df)
            lw = o["lam_w"][Lmask & T["valid"]]
            lmed = np.nanmedian(lw, axis=0) if lw.size else np.zeros(T["ng"])
            Q2._acc(acc, (label, "donor", "design", nm, "regB_t"), o["theta"], o["var"], lo, hi, lmed, T["theta_full"])
            arr[nm]["th"].append(o["theta"]); arr[nm]["v"].append(o["var"]); arr[nm]["df"].append(df)
    return acc, {k: {kk: np.array(vv) for kk, vv in v.items()} for k, v in arr.items()}


def gene_rows(arr, truth, keys, genes, G, m):
    out = []
    for nm, a in arr.items():
        th, v, df = a["th"], a["v"], a["df"]; R = th.shape[0]
        q = stats.t.ppf(1 - ALPHA / 2, np.where(df >= 1, df, np.nan))
        ok = np.isfinite(v) & (v >= 0) & np.isfinite(q)
        half = np.where(ok, q * np.sqrt(np.where(ok, v, 0.0)), np.nan)
        cov = ok & (np.abs(th - truth[None, :]) <= half)
        err = th - truth[None, :]; var = np.nanvar(th, axis=0)
        for j, g in enumerate(genes):
            w = 2 * half[ok[:, j], j]; p = float(cov[:, j].mean())
            out.append(dict(**keys, gene=g, G=G, m=m, form=nm, R=R, theta=float(truth[j]), bias=float(np.nanmean(err[:, j])),
                            mcse_bias=float(np.nanstd(err[:, j]) / np.sqrt(R)), sd=float(np.nanstd(err[:, j])),
                            rmse=float(np.sqrt(np.nanmean(err[:, j] ** 2))), coverage=p,
                            coverage_se=float(np.sqrt(p * (1 - p) / R)), frac_no_interval=float(1 - ok[:, j].mean()),
                            mean_width=float(w.mean()) if len(w) else np.nan,
                            median_width=float(np.median(w)) if len(w) else np.nan,
                            ev_over_var=float(np.nanmean(v[:, j]) / var[j]) if var[j] > 0 else np.nan,
                            frac_v_neg=float(np.mean(v[:, j] < 0)), df_mean=float(np.nanmean(df[:, j]))))
    return out


def check_cluster_values(T, data, cvp, keys, est_cv):
    cv = pd.read_parquet(cvp)
    cv = cv[(cv.task == keys["task"]) & (cv.encoder == keys["encoder"]) & (cv.scale == keys["scale"]) & (cv.estimand == est_cv)]
    if not len(cv):
        return dict(n_matched=0)
    Z = cv.pivot(index="donor", columns="gene", values="z")
    donors = [str(d) for d in data["donors"]]; genes = list(data["genes"])
    vd = [donors[g] for g in np.flatnonzero(T["valid"])]
    common = [d for d in vd if d in Z.index]; gl = [g for g in genes if g in Z.columns]
    a = T["zbar"][[donors.index(d) for d in common]][:, [genes.index(g) for g in gl]]
    b = Z.loc[common, gl].to_numpy(float)
    fin = np.isfinite(b)
    rel = np.abs(a - b)[fin] / np.maximum(1e-12, np.abs(b[fin]))
    return dict(n_valid_regimeB=len(vd), n_donors_cv=int(Z.shape[0]), n_common=len(common), n_genes=len(gl),
                only_regimeB=sorted(set(vd) - set(Z.index))[:20], only_cv=sorted(set(Z.index) - set(vd))[:20],
                max_rel=float(rel.max()) if rel.size else np.nan, max_abs=float(np.abs(a - b)[fin].max()) if fin.any() else np.nan)


def run_anchor(cfg, out):
    A = cfg["anchor"]
    data = load(dict(source="r5", parquet=A["parquet"], arm=A["arm"], vtag=A["vtag"], theta2_kind=A.get("theta2_kind", "neo_minus_stroma")))
    Tset = E3.build(data, A["vtag"], A["arm"])
    rows, generows = [], []
    for est in A["estimands"]:
        T = Tset[est]
        for m in A["m_list"]:
            if (T["kind"] == "theta2" and m < 4):
                continue
            acc, _ = run_cell(data, T, A["vtag"], est, m, int(A["draws"]), forms=(("C_ppi", "crossfit"), ("C_classical", "classical")))
            cell = dict(vtag=A["vtag"], arm=A["arm"], G=len(data["donors"]), part="regb", regime="B", budget=np.nan,
                        cost="unit", n_L=len(data["donors"]), m=m)
            E3.summarise(acc, cell, data["genes"], rows, generows)
    s = pd.DataFrame(rows)
    ref = pd.read_csv(A["ref_csv"])
    k = ["vtag", "arm", "m", "estimand", "estimator", "interval", "n_draws"]
    s["m"] = s["m"].astype(str); ref["m"] = ref["m"].astype(str)
    mm = s.merge(ref, on=k, how="left", suffixes=("", "_r5"))
    cols = ("n_genes", "emp_var_median", "est_var_over_emp_var_median", "coverage_median", "coverage_mean", "coverage_min")
    for c in cols:
        mm["d_" + c] = (mm[c] - mm[c + "_r5"]).abs()
    mm.to_csv(os.path.join(out, "regimeB_anchor_r5.csv"), index=False)
    nm = A["named"]
    key = mm[(mm.m == str(nm["m"])) & (mm.estimator == nm["estimator"]) & (mm.estimand == nm["estimand"])].iloc[0]
    return dict(rows=len(mm), rows_matched=int(mm.coverage_median_r5.notna().sum()),
                named=dict(nm, coverage_median=float(key.coverage_median), coverage_median_r5=float(key.coverage_median_r5),
                           ev_ratio=float(key.est_var_over_emp_var_median), ev_ratio_r5=float(key.est_var_over_emp_var_median_r5)),
                **{f"max_d_{c}": float(mm["d_" + c].max()) for c in cols})


def main():
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    summ = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"), populations=[])
    sp = os.path.join(out, "regimeB_summary.json"); json.dump(summ, open(sp, "w"), indent=1)
    if cfg.get("anchor"):
        t0 = time.time(); summ["anchor"] = run_anchor(cfg, out); summ["anchor"]["seconds"] = round(time.time() - t0, 1)
        json.dump(summ, open(sp, "w"), indent=1); print(json.dumps(summ["anchor"]), flush=True)
    rows, generows, grows = [], [], []
    R = int(cfg.get("R", 2000))
    for pop in cfg.get("populations", []):
        t0 = time.time()
        data = load(pop)
        Tset = E3.build(data, pop["vtag"], pop.get("arm", pop["encoder"]))
        info = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], G=len(data["donors"]),
                    n_units=int(len(data["didx"])), n_genes=len(data["genes"]), cells=[])
        summ["populations"].append(info)
        for est in pop["estimands"]:
            if est not in Tset:
                info["cells"].append(dict(estimand=est, skipped="not built")); continue
            T = Tset[est]
            est_out = "mu" if T["kind"] == "mean" else est
            keys = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], estimand=est_out)
            if pop.get("cluster_values"):
                info.setdefault("cv_check", {})[est_out] = check_cluster_values(T, data, pop["cluster_values"], keys, est_out)
            for m in pop.get("m_grid", cfg["m_grid"]):
                if (T["kind"] == "theta3" and m < 3) or (T["kind"] == "theta2" and m < 4):
                    continue
                tc = time.time()
                acc, arr = run_cell(data, T, pop["vtag"], est, m, R, label=est_out)
                cell = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], G=info["G"],
                            G_valid=int(T["valid"].sum()), m=m)
                E3.summarise(acc, cell, data["genes"], rows, generows)
                grows += gene_rows(arr, T["theta_full"], keys, data["genes"], int(T["valid"].sum()), m)
                info["cells"].append(dict(estimand=est_out, m=m, seconds=round(time.time() - tc, 1)))
                print(json.dumps(dict(pop=pop["task"] + "|" + pop["encoder"] + "|" + pop["scale"], est=est_out, m=m,
                                      s=round(time.time() - tc, 1))), flush=True)
                json.dump(summ, open(sp, "w"), indent=1, default=str)
        info["seconds"] = round(time.time() - t0, 1)
    summ["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(summ, open(sp, "w"), indent=1, default=str)
    pd.DataFrame(rows).to_csv(os.path.join(out, "regimeB_cells.csv"), index=False)
    pq.write_table(pa.Table.from_pandas(pd.DataFrame(grows, columns=GSCHEMA.names), schema=GSCHEMA, preserve_index=False),
                   os.path.join(out, "regimeB_genes.parquet"))
    print(json.dumps({k: v for k, v in summ.items() if k not in ("config",)}, indent=1, default=str)[:4000])


if __name__ == "__main__":
    main()
