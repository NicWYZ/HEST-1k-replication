"""Round 10, track final-runs, F3: regime B on F2's driver, with per-draw widths and new grids (plan, section 5d).

Uses F2's round10_final_runs_f2_regimeB.py and round10_final_runs_estimators.py unchanged (imported, not edited):
F2.load, round5_ppi_e3_twolevel.build, F2.run_cell (round 5's E3 'regb' seeds, so every draw at a given m is the
draw F2 made), F2.gene_rows and round 5's summarise. What this driver adds:

  * per-draw interval widths for chosen forms, written as a wide parquet (one row per estimand, m, form and draw,
    one float32 column per gene), and the bootstrap over draws of the median over genes of the per-gene width ratio
    (median width of a form over median width of C_classical, F2's aggregate definition), plan 5d.4 item 2;
  * a check of every row at an m that F2 ran against F2's gene-level rows of the same task, encoder and scale
    (F2/regimeB/<unit>/regimeB_genes.parquet), and of the recomputed cell summary against F2's committed
    f2_regimeB_summary.csv (the anchor of 5d.4 item 2);
  * a choice of forms per run (question V's coverage cells run C_fix1 only, plan 5d.3 (ii));
  * mode 'schema', which reads the parquet schemas of the refitted normalised-scale HEST files and the cluster
    values v3 (open point 5, plan 5d.6 item 5) without running any cell.

usage: round10_final_runs_f3_regimeB.py run <config.json> <out_dir>
       round10_final_runs_f3_regimeB.py schema <config.json> <out_dir>
config (run): populations [F2's population dict, plus optional m_grid, R, f2_genes (path of F2's gene parquet for the
        same task and encoder)], m_grid, R, forms (subset of C_fix1, C_ppi, C_classical; default all three),
        widths_forms (forms whose per-draw widths are written; default none), wr_boot (bootstrap replicates of the
        width ratio; default 0), f2_summary (path of F2's committed f2_regimeB_summary.csv, optional), label.
Writes regimeB_summary.json first, then regimeB_cells.csv, regimeB_wr.csv (width ratios with bootstrap standard
errors), regimeB_f2check*.csv, regimeB_genes.parquet (F2's schema) and regimeB_widths__<task>__<encoder>__<scale>.parquet.
"""
import json, os, sys, time, zlib
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
from scipy import stats
import round5_ppi_e3_twolevel as E3
import round10_final_runs_f2_regimeB as F2

FORM_COEF = dict(F2.FORMS)
ALPHA = F2.ALPHA
NUMCOLS = ("theta", "bias", "mcse_bias", "sd", "rmse", "coverage", "coverage_se", "frac_no_interval", "mean_width",
           "median_width", "ev_over_var", "frac_v_neg", "df_mean")
WRCOLS = ["task", "encoder", "scale", "estimand", "m", "form", "genes", "R", "median_wr", "boot_B", "boot_se",
          "boot_q05", "boot_q95"]


def seed_of(tag):
    return np.random.default_rng(zlib.crc32(tag.encode()))


def draw_widths(a):
    """Per-draw interval widths (R, ng) of one form, NaN where no interval forms (F2.gene_rows' rule)."""
    th, v, df = a["th"], a["v"], a["df"]
    q = stats.t.ppf(1 - ALPHA / 2, np.where(df >= 1, df, np.nan))
    ok = np.isfinite(v) & (v >= 0) & np.isfinite(q)
    return np.where(ok, 2 * q * np.sqrt(np.where(ok, v, 0.0)), np.nan)


def median_wr(wf, wc):
    """F2's aggregate: per gene the median width over draws with an interval, ratio of the two forms, median over
    genes (pandas' median skips genes whose ratio is undefined)."""
    with np.errstate(all="ignore"):
        r = np.nanmedian(wf, axis=0) / np.nanmedian(wc, axis=0)
    r = r[np.isfinite(r)]
    return float(np.median(r)) if r.size else np.nan


def wr_boot(wf, wc, B, rng):
    R = wf.shape[0]; out = np.empty(B)
    for b in range(B):
        i = rng.integers(0, R, R)
        out[b] = median_wr(wf[i], wc[i])
    return out


def run_population(pop, cfg, sink, log=print, data=None):
    """Runs every (estimand, m) cell of one population; appends to sink's lists. Returns (info, data). data, when
    given, is F2.load(pop) already made by the caller (F2.load also sets round 5's theta2 kind)."""
    R = int(pop.get("R", cfg.get("R", 2000)))
    forms = tuple((f, FORM_COEF[f]) for f in cfg.get("forms", [f for f, _ in F2.FORMS]))
    wforms = list(cfg.get("widths_forms", []))
    B = int(cfg.get("wr_boot", 0))
    t0 = time.time()
    if data is None:
        data = F2.load(pop)
    else:
        F2.Q2.THETA2_KIND = pop.get("theta2_kind", "neo_minus_stroma")
    Tset = E3.build(data, pop["vtag"], pop.get("arm", pop["encoder"]))
    info = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], G=len(data["donors"]),
                n_units=int(len(data["didx"])), n_genes=len(data["genes"]), load_seconds=round(time.time() - t0, 1),
                cells=[])
    for est in pop["estimands"]:
        if est not in Tset:
            info["cells"].append(dict(estimand=est, skipped="not built")); continue
        T = Tset[est]
        est_out = "mu" if T["kind"] == "mean" else est
        keys = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], estimand=est_out)
        if pop.get("cluster_values"):
            info.setdefault("cv_check", {})[est_out] = F2.check_cluster_values(T, data, pop["cluster_values"], keys, est_out)
        for m in pop.get("m_grid", cfg["m_grid"]):
            if (T["kind"] == "theta3" and m < 3) or (T["kind"] == "theta2" and m < 4):
                continue
            tc = time.time()
            acc, arr = F2.run_cell(data, T, pop["vtag"], est, m, R, forms=forms, label=est_out)
            ts = time.time() - tc
            cell = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], G=info["G"],
                        G_valid=int(T["valid"].sum()), m=m)
            E3.summarise(acc, cell, data["genes"], sink["rows"], [])
            sink["grows"] += F2.gene_rows(arr, T["theta_full"], keys, data["genes"], int(T["valid"].sum()), m)
            W = {nm: draw_widths(a) for nm, a in arr.items()}
            for nm in wforms:
                if nm in W:
                    sink["widths"].append((dict(keys, m=m, form=nm), W[nm].astype(np.float32)))
            tb = time.time()
            if "C_classical" in W:
                for nm in [f for f in W if f != "C_classical"]:
                    r = dict(keys, m=m, form=nm, genes=len(data["genes"]), R=R, median_wr=median_wr(W[nm], W["C_classical"]),
                             boot_B=B, boot_se=np.nan, boot_q05=np.nan, boot_q95=np.nan)
                    if B > 0:
                        bt = wr_boot(W[nm], W["C_classical"], B,
                                     seed_of(f"f3|regB|wrboot|{pop['task']}|{pop['encoder']}|{pop['scale']}|{est_out}|m{m}|{nm}"))
                        bt = bt[np.isfinite(bt)]
                        if bt.size > 1:
                            r.update(boot_se=float(bt.std(ddof=1)), boot_q05=float(np.quantile(bt, 0.05)),
                                     boot_q95=float(np.quantile(bt, 0.95)))
                    sink["wr"].append(r)
            info["cells"].append(dict(estimand=est_out, m=m, seconds=round(time.time() - tc, 1), sim_seconds=round(ts, 1),
                                      boot_seconds=round(time.time() - tb, 1)))
            log(json.dumps(dict(pop=pop["task"] + "|" + pop["encoder"] + "|" + pop["scale"], est=est_out, m=m,
                                s=round(time.time() - tc, 1))))
    info["genes"] = list(data["genes"])
    info["seconds"] = round(time.time() - t0, 1)
    return info, data


def f2_check(G, pops, f2_summary):
    """Compares every gene row at an m F2 ran with F2's gene parquet of the same task and encoder (all of F2's
    numeric columns), and the cell summaries recomputed with F2's aggregate rule with F2's committed summary."""
    out = []
    for pop in pops:
        if not pop.get("f2_genes"):
            continue
        f = pd.read_parquet(pop["f2_genes"])
        f = f[(f.task == pop["task"]) & (f.encoder == pop["encoder"]) & (f.scale == pop["scale"])]
        g = G[(G.task == pop["task"]) & (G.encoder == pop["encoder"]) & (G.scale == pop["scale"])]
        k = ["estimand", "m", "form", "gene"]
        mm = g.merge(f, on=k, how="inner", suffixes=("", "_f2"))
        r = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], rows_f3=len(g), rows_f2=len(f),
                 rows_matched=len(mm), m_matched=",".join(str(x) for x in sorted(mm.m.unique())))
        for c in NUMCOLS:
            a, b = mm[c].to_numpy(float), mm[c + "_f2"].to_numpy(float)
            d = np.where(np.isnan(a) & np.isnan(b), 0.0, np.abs(a - b))
            d = np.where(np.isnan(d), np.inf, d)
            r[f"max_abs_{c}"] = float(d.max()) if len(d) else np.nan
        r["max_abs_all"] = max(r[f"max_abs_{c}"] for c in NUMCOLS) if len(mm) else np.nan
        out.append(r)
    S = None
    if f2_summary and len(G):
        K = ["task", "encoder", "scale", "estimand", "m", "form"]
        q = lambda p: (lambda s: s.quantile(p))
        mine = G.groupby(K).agg(genes=("gene", "size"), median_coverage=("coverage", "median"),
                                q10_coverage=("coverage", q(0.1)), q90_coverage=("coverage", q(0.9)),
                                median_width=("median_width", "median"),
                                median_ev_over_var=("ev_over_var", "median")).reset_index()
        ref = pd.read_csv(f2_summary)
        S = mine.merge(ref, on=K, how="inner", suffixes=("", "_f2"))
        for c in ("genes", "median_coverage", "q10_coverage", "q90_coverage", "median_width", "median_ev_over_var"):
            S["d_" + c] = (S[c] - S[c + "_f2"]).abs()
    return pd.DataFrame(out), S


def write_widths(widths, genes, path):
    """Wide per-draw widths: one row per (task, encoder, scale, estimand, m, form, draw), one float32 column per gene."""
    if not widths:
        return 0
    fields = [("task", pa.string()), ("encoder", pa.string()), ("scale", pa.string()), ("estimand", pa.string()),
              ("m", pa.int64()), ("form", pa.string()), ("draw", pa.int32())] + [("w__" + g, pa.float32()) for g in genes]
    schema = pa.schema(fields)
    writer = pq.ParquetWriter(path, schema, compression="zstd")
    n = 0
    for keys, W in widths:
        R = W.shape[0]
        cols = {k: pa.array([keys[k]] * R, type=schema.field(k).type) for k in ("task", "encoder", "scale", "estimand", "m", "form")}
        cols["draw"] = pa.array(np.arange(R, dtype=np.int32))
        for j, g in enumerate(genes):
            cols["w__" + g] = pa.array(W[:, j], type=pa.float32())
        writer.write_table(pa.table([cols[f.name] for f in schema], schema=schema)); n += R
    writer.close()
    return n


def main_run(cfg, out):
    summ = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"), populations=[])
    sp = os.path.join(out, "regimeB_summary.json"); json.dump(summ, open(sp, "w"), indent=1)
    sink = dict(rows=[], grows=[], widths=[], wr=[])
    wfiles = []
    for pop in cfg.get("populations", []):
        info, data = run_population(pop, cfg, sink, log=lambda s: print(s, flush=True))
        genes = info.pop("genes")
        summ["populations"].append(info)
        json.dump(summ, open(sp, "w"), indent=1, default=str)
        if sink["widths"]:
            wfiles.append((f"regimeB_widths__{pop['task']}__{pop['encoder']}__{pop['scale']}.parquet", list(sink["widths"]), genes))
            sink["widths"] = []
    G = pd.DataFrame(sink["grows"], columns=F2.GSCHEMA.names)
    chk, S = f2_check(G, cfg.get("populations", []), cfg.get("f2_summary"))
    if len(chk):
        summ["f2_check"] = dict(rows_matched=int(chk.rows_matched.sum()), max_abs_all=float(chk.max_abs_all.max()))
    if S is not None and len(S):
        summ["f2_check_summary"] = dict(cells_matched=len(S), **{f"max_{c}": float(S[c].max()) for c in S.columns if c.startswith("d_")})
    WR = pd.DataFrame(sink["wr"], columns=WRCOLS)
    if len(WR):
        summ["wr"] = dict(rows=len(WR), median_boot_se=float(WR.boot_se.median()) if WR.boot_se.notna().any() else None)
    summ["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(summ, open(sp, "w"), indent=1, default=str)
    pd.DataFrame(sink["rows"]).to_csv(os.path.join(out, "regimeB_cells.csv"), index=False)
    WR.to_csv(os.path.join(out, "regimeB_wr.csv"), index=False)
    if len(chk):
        chk.to_csv(os.path.join(out, "regimeB_f2check.csv"), index=False)
    if S is not None and len(S):
        S.to_csv(os.path.join(out, "regimeB_f2check_summary.csv"), index=False)
    pq.write_table(pa.Table.from_pandas(G, schema=F2.GSCHEMA, preserve_index=False), os.path.join(out, "regimeB_genes.parquet"))
    tw = time.time()
    summ["widths_files"] = {fn: write_widths(w, g, os.path.join(out, fn)) for fn, w, g in wfiles}
    summ["widths_seconds"] = round(time.time() - tw, 1)
    json.dump(summ, open(sp, "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in summ.items() if k != "config"}, indent=1, default=str)[:6000])


# ------------------------------------------------------------------ schema check (open point 5)
LOADER_COLS = ("donor_id", "joined", "m_std", "frac_neoplastic")


def main_schema(cfg, out):
    """For each named parquet: its schema, the columns round 5's loader reads (round4_ppi_q2_masking.load: y__*, f__*,
    donor_id, joined, m_std, frac_neoplastic), the gene list, the row and joined counts against a reference file
    (the log(1 + y) file of the same task and encoder); for each cluster-values parquet the (task, encoder, scale,
    estimand) combinations it holds."""
    rows, cv_rows = [], []
    res = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"))
    json.dump(res, open(os.path.join(out, "schema_summary.json"), "w"), indent=1)
    for it in cfg.get("parquets", []):
        sch = pq.read_schema(it["path"]); names = list(sch.names)
        ygen = [c[3:] for c in names if c.startswith("y__")]; fgen = [c[3:] for c in names if c.startswith("f__")]
        r = dict(label=it["label"], path=it["path"], n_cols=len(names), n_y=len(ygen), n_f=len(fgen),
                 y_equals_f=ygen == fgen, missing_loader_cols=",".join(c for c in LOADER_COLS if c not in names),
                 types=";".join(f"{c}:{sch.field(c).type}" for c in LOADER_COLS if c in names)
                 + (f";y__:{sch.field('y__' + ygen[0]).type};f__:{sch.field('f__' + fgen[0]).type}" if ygen and fgen else ""))
        r["n_rows"] = pq.read_metadata(it["path"]).num_rows
        j = None
        if "joined" in names:
            j = pq.read_table(it["path"], columns=["joined", "donor_id"]).to_pandas()
            r["n_joined"] = int(j.joined.astype(bool).sum()); r["n_donors"] = int(j.donor_id.nunique())
            r["n_donors_joined"] = int(j.donor_id[j.joined.astype(bool)].nunique())
        if it.get("reference"):
            rs = pq.read_schema(it["reference"]); rg = [c[3:] for c in rs.names if c.startswith("y__")]
            r["genes_equal_reference"] = rg == ygen
            r["reference_only_cols"] = ",".join(sorted(set(rs.names) - set(names)))[:300]
            r["file_only_cols"] = ",".join(sorted(set(names) - set(rs.names)))[:300]
            if "joined" in rs.names and j is not None:
                rj = pq.read_table(it["reference"], columns=["joined", "donor_id"]).to_pandas()
                r["ref_n_rows"] = len(rj); r["ref_n_joined"] = int(rj.joined.astype(bool).sum())
                r["joined_equal_reference"] = bool(len(rj) == len(j)
                                                   and (rj.joined.astype(bool).to_numpy() == j.joined.astype(bool).to_numpy()).all()
                                                   and (rj.donor_id.astype(str).to_numpy() == j.donor_id.astype(str).to_numpy()).all())
        r["ok"] = bool(r["missing_loader_cols"] == "" and r["n_y"] > 0 and r["y_equals_f"])
        rows.append(r)
    for p in cfg.get("cluster_values", []):
        cv = pd.read_parquet(p)
        for (t, e, s, est), d in cv.groupby(["task", "encoder", "scale", "estimand"]):
            cv_rows.append(dict(path=p, task=t, encoder=e, scale=s, estimand=est, donors=int(d.donor.nunique()),
                                genes=int(d.gene.nunique()), cols=",".join(cv.columns)))
    R = pd.DataFrame(rows); C = pd.DataFrame(cv_rows)
    res.update(n_files=len(R), all_ok=bool(R.ok.all()) if len(R) else False,
               genes_equal_reference_all=bool(R["genes_equal_reference"].fillna(False).all()) if "genes_equal_reference" in R else None,
               cv_combinations=len(C), finished=time.strftime("%Y-%m-%dT%H:%M:%S"))
    json.dump(res, open(os.path.join(out, "schema_summary.json"), "w"), indent=1, default=str)
    R.to_csv(os.path.join(out, "schema_parquets.csv"), index=False)
    C.to_csv(os.path.join(out, "schema_cluster_values.csv"), index=False)
    print(json.dumps({k: v for k, v in res.items() if k != "config"}, indent=1, default=str))
    print(R.drop(columns=["path"]).to_string()[:6000])


def main():
    mode, cfgp, out = sys.argv[1:4]
    cfg = json.load(open(cfgp)); os.makedirs(out, exist_ok=True)
    np.seterr(all="ignore")
    if mode == "run":
        main_run(cfg, out)
    elif mode == "schema":
        main_schema(cfg, out)
    else:
        raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    main()
